import sys
import pickle
from pathlib import Path
from builder import *
from instrument import code_instrumentation
from animate import animation_gen
import os
import platform

if platform.system() == 'Windows':
    os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

def prompt():
    is_read_file = input("Read from file/stream (f/s)? ").startswith(("f", "F"))
    is_verbose = input("Verbose graph draw (y/n)? ").startswith(("y", "Y"))
    file_path = None
    if is_read_file:
        default_path = "code.py"
        file_path = input("Enter file path: ")
        file_path = file_path if file_path else default_path
    return is_read_file, is_verbose, file_path


def read_file(file_path):
    with open(file_path, 'r') as src_file:
        src = src_file.read() + "\n" + "End"
    tree = ast.parse(src, mode='exec')
    print(ast.dump(tree))
    cfg = CFGVisitor().build(file_path, tree)
    return cfg


def read_stdIn():
    input("Type Python src\n")
    src = ""
    buffer = []
    while True:
        line = sys.stdin.readline().rstrip("\n")
        # print(line)
        if line == '':
            break
        else:
            buffer.append(line)
    for item in buffer:
        src = src + "\n" + item
    src += "\nEnd"
    print(src)
    tree = ast.parse(src, mode='exec')
    cfg = CFGVisitor().build('example.py', tree)
    return cfg


def run_and_save_path(test_data, func_name):
    exe_file = f'{func_name}_instrumented'
    sys.path.append('./out_vis')
    exec(f"from code_instrumented import {func_name}_instrumented")
    argss = ""
    exe_file += "(" + test_data + ")"
    executed_path, result = eval(exe_file)
    return executed_path


def main():
    func_name = input('Enter function name:')
    func_name = "triangleType"
    code_instrumentation('.', 'code', func_name, './out_vis')
    # test_data = '4,5,8'
    test_data = input('Enter test data:')

    is_read_file, is_verbose, file_path = prompt()
    if is_read_file and is_verbose:
        cfg = read_file(file_path)
        png_name = Path(file_path).with_suffix('').name
        cfg.show(filepath=f"output/{png_name}")
    elif is_read_file:
        cfg = read_file(file_path)
        png_name = Path(file_path).with_suffix('').name
        cfg.show(filepath=f"output/{png_name}", is_verbose=False)
    elif (not is_read_file) and is_verbose:
        cfg = read_stdIn()
        png_name = Path('example.py').with_suffix('').name
        cfg.show(filepath=f"output/{png_name}")
    else:
        cfg = read_stdIn()
        png_name = Path('example.py').with_suffix('').name
        cfg.show(filepath=f"output/{png_name}", is_verbose=False)
    executed_path = run_and_save_path(test_data, func_name)
    animation_gen(executed_path)


if __name__ == '__main__':
    main()
