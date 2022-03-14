"""
Control flow graph for Python programs.
"""
from __future__ import annotations
import ast
import astor
from typing import Dict, List, Tuple, Set, Optional, Type
from collections import defaultdict
import pickle
import graphviz as gv

import builder
from builder import *



class SingletonMeta(type):
    _instance: Optional[BlockId] = None

    def __call__(self) -> BlockId:
        if self._instance is None:
            self._instance = super().__call__()
        return self._instance


class BlockId(metaclass=SingletonMeta):
    counter: int = 0

    def gen(self) -> int:
        self.counter += 1
        return self.counter


class BasicBlock:
    block_line = defaultdict(list)

    def __init__(self, bid: int):
        self.bid: int = bid
        self.stmts: List[Type[ast.AST]] = []
        self.calls: List[str] = []
        self.prev: List[int] = []
        self.next: List[int] = []


    def is_empty(self) -> bool:
        return len(self.stmts) == 0

    def has_next(self) -> bool:
        return len(self.next) != 0

    def has_previous(self) -> bool:
        return len(self.prev) != 0

    def remove_from_prev(self, prev_bid: int) -> None:
        if prev_bid in self.prev:
            self.prev.remove(prev_bid)

    def remove_from_next(self, next_bid: int) -> None:
        if next_bid in self.next:
            self.next.remove(next_bid)

    def stmts_to_code(self, is_verbose: bool) -> str:
        global block_line
        src = ""
        # print(builder.func_name)
        builder.block_counter += 1
        if is_verbose:
            for stmt in self.stmts:
                builder.counter += 1
                if type(stmt) in [ast.If, ast.For, ast.While]:
                    src += str(builder.counter) + ": " + (astor.to_source(stmt)).split('\n')[0] + "\n"
                    # print("if 1")
                    print(src)
                elif type(stmt) == ast.FunctionDef or \
                        type(stmt) == ast.AsyncFunctionDef:
                    src += str(builder.counter) + ": " + (astor.to_source(stmt)).split('\n')[0] + "...\n"
                    # print("if 2")
                    print(src)
                else:
                    # print("if 3")
                    token = astor.to_source(stmt).split("\n")
                    # print(token)
                    if token[0] == 'End':
                        # print("eeeee")
                        builder.block_counter -= 1
                        builder.counter -= 1
                        src = astor.to_source(stmt)
                        print(src)
                    else:
                        for n in builder.func_name:
                            if n in token[0].split("(")[0]:
                                builder.counter -= 1
                                # print(token[0].split("(")[0])
                        # print("elseee")
                        # print(type(stmt))
                        src += str(builder.counter) + ": " + astor.to_source(stmt)
                        print(src)
                BasicBlock.block_line[self.bid].append(stmt.lineno)

        else:
            for stmt in self.stmts:
                builder.counter += 1
                if type(stmt) in [ast.If, ast.For, ast.While]:
                    src += str(builder.counter) + " "
                elif type(stmt) == ast.FunctionDef or type(stmt) == ast.AsyncFunctionDef:
                    src += str(builder.counter) + " "
                else:
                    token = astor.to_source(stmt).split(" ")
                    if token[0] == 'End':
                        builder.block_counter -= 1
                        builder.counter -= 1
                        src = astor.to_source(stmt)
                    else:
                        src += str(builder.counter) + " "
                BasicBlock.block_line[self.bid].append(stmt.lineno)
        with open('./out_vis/block_lines.pickle', 'wb') as handle:
            pickle.dump(self.block_line, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return src

    def calls_to_code(self) -> str:
        return '\n'.join(self.calls)
