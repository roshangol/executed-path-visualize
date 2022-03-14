import sys
sys.path.append(r'/home/roshan/work/0/path_anim/instrument')
sys.path.append(r'/home/roshan/work/0/path_anim')
from runner import evaluate_condition
from Coverage import cover_decorator

@cover_decorator
def triangleType_instrumented(a, b, c):
    isATriangle = False
    if evaluate_condition(1, 'Lt', a, b + c) and evaluate_condition(2, 'Lt', b, a + c) and evaluate_condition(3, 'Lt', c, a + b):
        isATriangle = True is True
    if isATriangle:
        if evaluate_condition(4, 'Eq', a, b) and evaluate_condition(5, 'Eq', b, c):
            print('the triangle was a EQUILATERAL')
        elif evaluate_condition(6, 'NotEq', a, b) and evaluate_condition(7, 'NotEq', a, c) and evaluate_condition(8, 'NotEq', b, c):
            print('the triangle was a SCALENE')
    else:
        print('invalid')
