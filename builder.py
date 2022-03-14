from __future__ import annotations
import ast
import astor
from typing import Dict, List, Tuple, Set, Optional, Type
from model import *
from model import BasicBlock
from visual import build_node_template
import pickle

counter = 1
block_counter = 1
func_name = []


class CFG:
    def __init__(self, name: str):
        self.name: str = name
        self.start: Optional[BasicBlock] = None
        self.func_calls: Dict[str, CFG] = {}
        self.blocks: Dict[int, BasicBlock] = {}
        self.edges: Dict[Tuple[int, int], Type[ast.AST]] = {}
        # self.graph: Optional[gv.dot.Digraph] = None

    def _traverse(self, block: BasicBlock, visited: Set[int] = set(), calls: bool = True,
                  is_verbose: bool = True) -> None:
        if block.bid not in visited:
            visited.add(block.bid)
            nodelabel = block.stmts_to_code(is_verbose)
            # print(nodelabel)
            if "End" in nodelabel:
                self.graph.node(str(block.bid), label=nodelabel,
                                _attributes={'color': '#ffaaaa', 'style': 'filled', 'shape': 'oval'})

                with open('./out_vis/End.pickle', 'wb') as handle:
                    pickle.dump(block.bid, handle, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                self.graph.node(str(block.bid), label=build_node_template(block_counter - 1, nodelabel))
            for next_bid in block.next:
                b = nodelabel.rstrip("\n")
                e = astor.to_source(self.edges[(block.bid, next_bid)]).rstrip("\n")if self.edges[(block.bid, next_bid)] else 'None'
                # print('nodelable :', end=" ")
                # print(b)
                # print('edge :', end=" ")
                # print(e)
                # print(b.find(e))
                if b.find(e) != -1 and ("break" or "continue") not in e:
                    self.graph.edge(str(block.bid), str(next_bid), label="True")
                elif 'None' in e:
                    self.graph.edge(str(block.bid), str(next_bid), label="")
                elif "break" in e:
                    self.graph.edge(str(block.bid), str(next_bid), label="break")
                elif "continue" in e:
                    self.graph.edge(str(block.bid), str(next_bid), label="continue")
                else:
                    self.graph.edge(str(block.bid), str(next_bid), label="False")
                # self.graph.edge(str(block.bid), str(next_bid),
                #                 label=astor.to_source(self.edges[(block.bid, next_bid)])
                #                 if self.edges[(block.bid, next_bid)] else '')
                self._traverse(self.blocks[next_bid], visited, calls=calls, is_verbose=is_verbose)
            self.graph.render('./out_vis/cfg.dot')

    # def _traverse(self, block: BasicBlock, visited: Set[int] = set(), calls: bool = True,
    #               is_verbose: bool = True) -> None:
    #     if block.bid not in visited:
    #         visited.add(block.bid)
    #         nodelabel = block.stmts_to_code(is_verbose)
    #         print(nodelabel)
    #         if "End" in nodelabel:
    #             self.graph.node(str(block.bid), label=nodelabel,
    #                             _attributes={'color': '#ffaaaa', 'style': 'filled', 'shape': 'oval'})
    #         else:
    #             self.graph.node(str(block.bid), label=build_node_template(block_counter - 1, nodelabel))
    #         for next_bid in block.next:
    #             # b = nodelabel.rstrip("\n")
    #             # e = astor.to_source(self.edges[(block.bid, next_bid)]).rstrip("\n")if self.edges[(block.bid, next_bid)] else 'None'
    #             # # print('nodelable :', end=" ")
    #             # print(b)
    #             # # print('edge :', end=" ")
    #             # print(e)
    #             # print(b.find(e))
    #             # if b.find(e) != -1:
    #             #     self.graph.edge(str(block.bid), str(next_bid), label="True")
    #             # else:
    #             self.graph.edge(str(block.bid), str(next_bid),
    #                             label=astor.to_source(self.edges[(block.bid, next_bid)])
    #                             if self.edges[(block.bid, next_bid)] else '')
    #             self._traverse(self.blocks[next_bid], visited, calls=calls, is_verbose=is_verbose)

    def _show(self, fmt: str = 'png', calls: bool = True, is_verbose: bool = True) -> gv.dot.Digraph:
        # print(self.blocks)
        # print(self.edges)
        self.graph = gv.Digraph(name='cluster_' + self.name, format=fmt, graph_attr={'label': self.name})
        self.graph.attr('node', shape='none')
        self.graph.node('Start', _attributes={'color': '#aaffaa', 'style': 'filled', 'shape': 'oval'})
        self.graph.edge('Start', '1')
        self._traverse(self.start, calls=calls, is_verbose=is_verbose)
        return self.graph

    def show(self, filepath: str = './output', fmt: str = 'png', calls: bool = True, show: bool = True,
             is_verbose: bool = True) -> None:
        self._show(fmt, calls, is_verbose=is_verbose)
        self.graph.render(filepath, view=False, cleanup=True)


class CFGVisitor(ast.NodeVisitor):
    invertComparators: Dict[Type[ast.AST], Type[ast.AST]] = \
        {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.GtE,
         ast.LtE: ast.Gt,
         ast.Gt: ast.LtE, ast.GtE: ast.Lt, ast.Is: ast.IsNot,
         ast.IsNot: ast.Is, ast.In: ast.NotIn, ast.NotIn: ast.In}

    def __init__(self):
        super().__init__()
        self.loop_stack: List[BasicBlock] = []
        self.curr_loop_guard_stack: List[BasicBlock] = []
        self.ifExp = False

    def build(self, name: str, tree: Type[ast.AST]) -> CFG:
        self.cfg = CFG(name)
        self.curr_block = self.new_block()
        self.cfg.start = self.curr_block

        self.visit(tree)
        self.remove_empty_blocks(self.cfg.start)
        return self.cfg

    def new_block(self) -> BasicBlock:
        bid: int = BlockId().gen()
        self.cfg.blocks[bid] = BasicBlock(bid)
        return self.cfg.blocks[bid]

    def add_stmt(self, block: BasicBlock, stmt: Type[ast.AST]) -> None:
        block.stmts.append(stmt)

    def add_edge(self, frm_id: int, to_id: int, condition=None) -> BasicBlock:
        self.cfg.blocks[frm_id].next.append(to_id)
        self.cfg.blocks[to_id].prev.append(frm_id)
        self.cfg.edges[(frm_id, to_id)] = condition
        return self.cfg.blocks[to_id]

    def add_loop_block(self) -> BasicBlock:
        if self.curr_block.is_empty() and not self.curr_block.has_next():
            return self.curr_block
        else:
            loop_block = self.new_block()
            self.add_edge(self.curr_block.bid, loop_block.bid)
            return loop_block

    def add_subgraph(self, tree: Type[ast.AST]) -> None:
        self.cfg.func_calls[tree.name] = CFGVisitor().build(tree.name, ast.Module(body=tree.body))

    def add_condition(self, cond1: Optional[Type[ast.AST]], cond2: Optional[Type[ast.AST]]) -> Optional[Type[ast.AST]]:
        if cond1 and cond2:
            return ast.BoolOp(ast.And(), values=[cond1, cond2])
        else:
            return cond1 if cond1 else cond2

    def remove_empty_blocks(self, block: BasicBlock, visited: Set[int] = set()) -> None:
        if block.bid not in visited:
            visited.add(block.bid)
            if block.is_empty():
                for prev_bid in block.prev:
                    prev_block = self.cfg.blocks[prev_bid]
                    for next_bid in block.next:
                        next_block = self.cfg.blocks[next_bid]
                        self.add_edge(prev_bid, next_bid, self.add_condition(self.cfg.edges.get((prev_bid, block.bid)),
                                                                             self.cfg.edges.get((block.bid, next_bid))))
                        self.cfg.edges.pop((block.bid, next_bid), None)
                        next_block.remove_from_prev(block.bid)
                    self.cfg.edges.pop((prev_bid, block.bid), None)
                    prev_block.remove_from_next(block.bid)
                block.prev.clear()
                for next_bid in block.next:
                    self.remove_empty_blocks(self.cfg.blocks[next_bid], visited)
                block.next.clear()

            else:
                for next_bid in block.next:
                    self.remove_empty_blocks(self.cfg.blocks[next_bid], visited)

    def invert(self, node: Type[ast.AST]) -> Type[ast.AST]:
        if type(node) == ast.Compare:
            if len(node.ops) == 1:
                return ast.Compare(left=node.left, ops=[self.invertComparators[type(node.ops[0])]()],
                                   comparators=node.comparators)
            else:
                tmpNode = ast.BoolOp(op=ast.And(), values=[
                    ast.Compare(left=node.left, ops=[node.ops[0]], comparators=[node.comparators[0]])])
                for i in range(0, len(node.ops) - 1):
                    tmpNode.values.append(ast.Compare(left=node.comparators[i], ops=[node.ops[i + 1]],
                                                      comparators=[node.comparators[i + 1]]))
                return self.invert(tmpNode)
        elif isinstance(node, ast.BinOp) and type(node.op) in self.invertComparators:
            return ast.BinOp(node.left, self.invertComparators[type(node.op)](), node.right)
        elif type(node) == ast.NameConstant and type(node.value) == bool:
            return ast.NameConstant(value=not node.value)
        elif type(node) == ast.BoolOp:
            return ast.BoolOp(values=[self.invert(x) for x in node.values],
                              op={ast.And: ast.Or(), ast.Or: ast.And()}.get(type(node.op)))
        elif type(node) == ast.UnaryOp:
            return self.UnaryopInvert(node)
        else:
            return ast.UnaryOp(op=ast.Not(), operand=node)

    def UnaryopInvert(self, node: Type[ast.AST]) -> Type[ast.AST]:
        if type(node.op) == ast.UAdd:
            return ast.UnaryOp(op=ast.USub(), operand=node.operand)
        elif type(node.op) == ast.USub:
            return ast.UnaryOp(op=ast.UAdd(), operand=node.operand)
        elif type(node.op) == ast.Invert:
            return ast.UnaryOp(op=ast.Not(), operand=node)
        else:
            return node.operand

    def combine_conditions(self, node_list: List[Type[ast.AST]]) -> Type[ast.AST]:
        return node_list[0] if len(node_list) == 1 else ast.BoolOp(op=ast.And(), values=node_list)

    def generic_visit(self, node):
        if type(node) in [ast.Import, ast.ImportFrom]:
            self.add_stmt(self.curr_block, node)
            return
        if type(node) in [ast.AnnAssign, ast.AugAssign]:
            self.add_stmt(self.curr_block, node)
        super().generic_visit(node)

    def get_function_name(self, node: Type[ast.AST]) -> str:
        if type(node) == ast.Name:
            return node.id
        elif type(node) == ast.Attribute:
            return self.get_function_name(node.value) + '.' + node.attr
        elif type(node) == ast.Str:
            return node.s
        elif type(node) == ast.Subscript:
            return node.value.id
        elif type(node) == ast.Lambda:
            return 'lambda function'

    def populate_body(self, body_list: List[Type[ast.AST]], to_bid: int) -> None:
        for child in body_list:
            self.visit(child)
        if not self.curr_block.next:
            self.add_edge(self.curr_block.bid, to_bid)

    def visit_FunctionDef(self, node):
        builder.func_name.append(node.name)
        # print(node.name)
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.add_stmt(self.curr_block, node)
        # If the assertion fails, the current flow ends, so the fail block is a
        # final block of the CFG.
        # self.cfg.finalblocks.append(self.add_edge(self.curr_block.bid, self.new_block().bid, self.invert(node.test)))
        # If the assertion is True, continue the flow of the program.
        # success block
        self.curr_block = self.add_edge(self.curr_block.bid, self.new_block().bid, node.test)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if type(node.value) in [ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.Lambda] and len(
                node.targets) == 1 and type(node.targets[0]) == ast.Name:
            if type(node.value) == ast.ListComp:
                self.add_stmt(self.curr_block, ast.Assign(targets=[ast.Name(id=node.targets[0].id, ctx=ast.Store())],
                                                          value=ast.List(elts=[], ctx=ast.Load())))
                self.listCompReg = (node.targets[0].id, node.value)
            elif type(node.value) == ast.SetComp:
                self.add_stmt(self.curr_block, ast.Assign(targets=[ast.Name(id=node.targets[0].id, ctx=ast.Store())],
                                                          value=ast.Call(func=ast.Name(id='set', ctx=ast.Load()),
                                                                         args=[], keywords=[])))
                self.setCompReg = (node.targets[0].id, node.value)
            elif type(node.value) == ast.DictComp:
                self.add_stmt(self.curr_block, ast.Assign(targets=[ast.Name(id=node.targets[0].id, ctx=ast.Store())],
                                                          value=ast.Dict(keys=[], values=[])))
                self.dictCompReg = (node.targets[0].id, node.value)
            elif type(node.value) == ast.GeneratorExp:
                self.add_stmt(self.curr_block, ast.Assign(targets=[ast.Name(id=node.targets[0].id, ctx=ast.Store())],
                                                          value=ast.Call(func=ast.Name(
                                                              id='__' + node.targets[0].id + 'Generator__',
                                                              ctx=ast.Load()), args=[], keywords=[])))
                self.genExpReg = (node.targets[0].id, node.value)
            else:
                self.lambdaReg = (node.targets[0].id, node.value)
        else:
            self.add_stmt(self.curr_block, node)
        self.generic_visit(node)

    def visit_Await(self, node):
        afterawait_block = self.new_block()
        self.add_edge(self.curr_block.bid, afterawait_block.bid)
        self.generic_visit(node)
        self.curr_block = afterawait_block

    def visit_Break(self, node):
        assert len(self.loop_stack), "Found break not inside loop"
        self.add_edge(self.curr_block.bid, self.loop_stack[-1].bid, ast.Break())

    def visit_Call(self, node):
        if type(node.func) == ast.Lambda:
            self.lambdaReg = ('Anonymous Function', node.func)
            self.generic_visit(node)
        else:
            self.curr_block.calls.append(self.get_function_name(node.func))

    def visit_Continue(self, node):
        assert len(self.loop_stack), "Found continue not inside loop"
        self.add_edge(self.curr_block.bid, self.curr_loop_guard_stack[-1].bid, ast.Continue())

    def visit_DictComp_Rec(self, generators: List[Type[ast.AST]]) -> List[Type[ast.AST]]:
        if not generators:
            if self.dictCompReg[0]:
                return [ast.Assign(targets=[ast.Subscript(value=ast.Name(id=self.dictCompReg[0], ctx=ast.Load()),
                                                          slice=ast.Index(value=self.dictCompReg[1].key),
                                                          ctx=ast.Store())], value=self.dictCompReg[1].value)]
        else:
            return [ast.For(target=generators[-1].target, iter=generators[-1].iter, body=[
                ast.If(test=self.combine_conditions(generators[-1].ifs), body=self.visit_DictComp_Rec(generators[:-1]),
                       orelse=[])] if generators[-1].ifs else self.visit_DictComp_Rec(generators[:-1]), orelse=[])]

    def visit_DictComp(self, node):
        try:
            self.generic_visit(ast.Module(self.visit_DictComp_Rec(self.dictCompReg[1].generators)))
        except:
            pass
        finally:
            self.dictCompReg = None

    def visit_Expr(self, node):
        if type(node.value) == ast.ListComp and type(node.value.elt) == ast.Call:
            self.listCompReg = (None, node.value)
        elif type(node.value) == ast.Lambda:
            self.lambdaReg = ('Anonymous Function', node.value)
        else:
            self.add_stmt(self.curr_block, node)
        self.generic_visit(node)

    def visit_For(self, node):
        loop_guard = self.add_loop_block()
        self.curr_block = loop_guard
        self.add_stmt(self.curr_block, node)
        # New block for the body of the for-loop.
        for_block = self.add_edge(self.curr_block.bid, self.new_block().bid)
        if not node.orelse:
            # Block of code after the for loop.
            afterfor_block = self.add_edge(self.curr_block.bid, self.new_block().bid)
            self.loop_stack.append(afterfor_block)
            self.curr_block = for_block

            self.populate_body(node.body, loop_guard.bid)
        else:
            # Block of code after the for loop.
            afterfor_block = self.new_block()
            orelse_block = self.add_edge(self.curr_block.bid, self.new_block().bid, ast.Name(id='else', ctx=ast.Load()))
            self.loop_stack.append(afterfor_block)
            self.curr_block = for_block

            self.populate_body(node.body, loop_guard.bid)

            self.curr_block = orelse_block
            for child in node.orelse:
                self.visit(child)
            self.add_edge(orelse_block.bid, afterfor_block.bid)

        # Continue building the CFG in the after-for block.
        self.curr_block = afterfor_block

    def visit_GeneratorExp_Rec(self, generators: List[Type[ast.AST]]) -> List[Type[ast.AST]]:
        if not generators:
            self.generic_visit(self.genExpReg[1].elt)
            if self.genExpReg[0]:
                return [ast.Expr(value=ast.Yield(value=self.genExpReg[1].elt))]
        else:
            return [ast.For(target=generators[-1].target, iter=generators[-1].iter, body=[
                ast.If(test=self.combine_conditions(generators[-1].ifs),
                       body=self.visit_GeneratorExp_Rec(generators[:-1]), orelse=[])] if generators[
                -1].ifs else self.visit_GeneratorExp_Rec(generators[:-1]), orelse=[])]

    def visit_GeneratorExp(self, node):
        try:
            self.generic_visit(ast.FunctionDef(name='__' + self.genExpReg[0] + 'Generator__',
                                               args=ast.arguments(args=[], vararg=None, kwonlyargs=[], kw_defaults=[],
                                                                  kwarg=None, defaults=[]),
                                               body=self.visit_GeneratorExp_Rec(self.genExpReg[1].generators),
                                               decorator_list=[], returns=None))
        except:
            pass
        finally:
            self.genExpReg = None

    def visit_If(self, node):
        # Add the If statement at the end of the current block.
        self.add_stmt(self.curr_block, node)

        # Create a block for the code after the if-else.
        afterif_block = self.new_block()
        # Create a new block for the body of the if.
        if_block = self.add_edge(self.curr_block.bid, self.new_block().bid, node.test)

        # New block for the body of the else if there is an else clause.
        if node.orelse:
            self.curr_block = self.add_edge(self.curr_block.bid, self.new_block().bid, self.invert(node.test))

            # Visit the children in the body of the else to populate the block.
            self.populate_body(node.orelse, afterif_block.bid)
        else:
            self.add_edge(self.curr_block.bid, afterif_block.bid, self.invert(node.test))

        # Visit children to populate the if block.
        self.curr_block = if_block

        self.populate_body(node.body, afterif_block.bid)

        # Continue building the CFG in the after-if block.
        self.curr_block = afterif_block

    def visit_IfExp_Rec(self, node: Type[ast.AST]) -> List[Type[ast.AST]]:
        return [ast.If(test=node.test, body=[ast.Return(value=node.body)],
                       orelse=self.visit_IfExp_Rec(node.orelse) if type(node.orelse) == ast.IfExp else [
                           ast.Return(value=node.orelse)])]

    def visit_IfExp(self, node):
        if self.ifExp:
            self.generic_visit(ast.Module(self.visit_IfExp_Rec(node)))

    def visit_Lambda(self, node):
        self.add_subgraph(ast.FunctionDef(name=self.lambdaReg[0], args=node.args, body=[ast.Return(value=node.body)],
                                          decorator_list=[], returns=None))
        self.lambdaReg = None

    def visit_ListComp_Rec(self, generators: List[Type[ast.AST]]) -> List[Type[ast.AST]]:
        if not generators:
            self.generic_visit(self.listCompReg[1].elt)
            if self.listCompReg[0]:
                return [ast.Expr(value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id=self.listCompReg[0], ctx=ast.Load()), attr='append',
                                       ctx=ast.Load()), args=[self.listCompReg[1].elt], keywords=[]))]
            else:
                return [ast.Expr(value=self.listCompReg[1].elt)]
        else:
            return [ast.For(target=generators[-1].target, iter=generators[-1].iter, body=[
                ast.If(test=self.combine_conditions(generators[-1].ifs), body=self.visit_ListComp_Rec(generators[:-1]),
                       orelse=[])] if generators[-1].ifs else self.visit_ListComp_Rec(generators[:-1]), orelse=[])]

    def visit_ListComp(self, node):
        try:
            self.generic_visit(ast.Module(self.visit_ListComp_Rec(self.listCompReg[1].generators)))
        except:
            pass
        finally:
            self.listCompReg = None

    def visit_Pass(self, node):
        self.add_stmt(self.curr_block, node)

    def visit_Raise(self, node):
        self.add_stmt(self.curr_block, node)
        self.curr_block = self.new_block()

    def visit_Return(self, node):
        if type(node.value) == ast.IfExp:
            self.ifExp = True
            self.generic_visit(node)
            self.ifExp = False
        else:
            self.add_stmt(self.curr_block, node)
        # self.cfg.finalblocks.append(self.curr_block)
        # Continue in a new block but without any jump to it -> all code after
        # the return statement will not be included in the CFG.
        self.curr_block = self.new_block()

    def visit_SetComp_Rec(self, generators: List[Type[ast.AST]]) -> List[Type[ast.AST]]:
        if not generators:
            self.generic_visit(self.setCompReg[1].elt)
            if self.setCompReg[0]:
                return [ast.Expr(value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id=self.setCompReg[0], ctx=ast.Load()), attr='add',
                                       ctx=ast.Load()), args=[self.setCompReg[1].elt], keywords=[]))]
            else:  # not supported yet
                return [ast.Expr(value=self.setCompReg[1].elt)]
        else:
            return [ast.For(target=generators[-1].target, iter=generators[-1].iter, body=[
                ast.If(test=self.combine_conditions(generators[-1].ifs), body=self.visit_SetComp_Rec(generators[:-1]),
                       orelse=[])] if generators[-1].ifs else self.visit_SetComp_Rec(generators[:-1]), orelse=[])]

    def visit_SetComp(self, node):
        try:
            self.generic_visit(ast.Module(self.visit_SetComp_Rec(self.setCompReg[1].generators)))
        except:
            pass
        finally:
            self.setCompReg = None

    def visit_Try(self, node):
        loop_guard = self.add_loop_block()
        self.curr_block = loop_guard
        self.add_stmt(loop_guard, ast.Try(body=[], handlers=[], orelse=[], finalbody=[]))

        after_try_block = self.new_block()
        self.add_stmt(after_try_block, ast.Name(id='handle errors', ctx=ast.Load()))
        self.populate_body(node.body, after_try_block.bid)

        self.curr_block = after_try_block

        if node.handlers:
            for handler in node.handlers:
                before_handler_block = self.new_block()
                self.curr_block = before_handler_block
                self.add_edge(after_try_block.bid, before_handler_block.bid,
                              handler.type if handler.type else ast.Name(id='Error', ctx=ast.Load()))

                after_handler_block = self.new_block()
                self.add_stmt(after_handler_block, ast.Name(id='end except', ctx=ast.Load()))
                self.populate_body(handler.body, after_handler_block.bid)
                self.add_edge(after_handler_block.bid, after_try_block.bid)

        if node.orelse:
            before_else_block = self.new_block()
            self.curr_block = before_else_block
            self.add_edge(after_try_block.bid, before_else_block.bid, ast.Name(id='No Error', ctx=ast.Load()))

            after_else_block = self.new_block()
            self.add_stmt(after_else_block, ast.Name(id='end no error', ctx=ast.Load()))
            self.populate_body(node.orelse, after_else_block.bid)
            self.add_edge(after_else_block.bid, after_try_block.bid)

        finally_block = self.new_block()
        self.curr_block = finally_block

        if node.finalbody:
            self.add_edge(after_try_block.bid, finally_block.bid, ast.Name(id='Finally', ctx=ast.Load()))
            after_finally_block = self.new_block()
            self.populate_body(node.finalbody, after_finally_block.bid)
            self.curr_block = after_finally_block
        else:
            self.add_edge(after_try_block.bid, finally_block.bid)

    def visit_While(self, node):
        loop_guard = self.add_loop_block()
        self.curr_block = loop_guard
        self.curr_loop_guard_stack.append(loop_guard)
        self.add_stmt(loop_guard, node)
        # New block for the case where the test in the while is False.
        afterwhile_block = self.new_block()
        self.loop_stack.append(afterwhile_block)
        inverted_test = self.invert(node.test)

        if not node.orelse:
            # Skip shortcut loop edge if while True:
            if not (isinstance(inverted_test, ast.NameConstant) and inverted_test.value == False):
                self.add_edge(self.curr_block.bid, afterwhile_block.bid, inverted_test)

            # New block for the case where the test in the while is True.
            # Populate the while block.
            self.curr_block = self.add_edge(self.curr_block.bid, self.new_block().bid, node.test)

            self.populate_body(node.body, loop_guard.bid)
        else:
            orelse_block = self.new_block()
            if not (isinstance(inverted_test, ast.NameConstant) and inverted_test.value == False):
                self.add_edge(self.curr_block.bid, orelse_block.bid, inverted_test)
            self.curr_block = self.add_edge(self.curr_block.bid, self.new_block().bid, node.test)

            self.populate_body(node.body, loop_guard.bid)
            self.curr_block = orelse_block
            for child in node.orelse:
                self.visit(child)
            self.add_edge(orelse_block.bid, afterwhile_block.bid)

        # Continue building the CFG in the after-while block.
        self.curr_block = afterwhile_block
        self.loop_stack.pop()
        self.curr_loop_guard_stack.pop()

    def visit_Yield(self, node):
        self.curr_block = self.add_edge(self.curr_block.bid, self.new_block().bid)
