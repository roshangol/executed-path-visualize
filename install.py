import os
import sys
import platform
import shutil

ver = (sys.version)[:3]


os_type = platform.system()

if os_type == 'Linux':
    os.system('python3 -m venv venv && . venv/bin/activate && pip3 install -r requirement.txt')
    os.remove(f'./venv/lib/python{ver}/site-packages/astor/source_repr.py')
    shutil.copyfile('./third_part/source_repr.py', f'./venv/lib/python{ver}/site-packages/astor/source_repr.py')
elif os_type == 'Windows':
    os.system(r'python -m venv venv && .\venv\Scripts\activate && pip3 install -r requirement.txt')
    os.remove(f'./venv/Lib/site-packages/astor/source_repr.py')
    shutil.copyfile('./third_part/source_repr.py', f'./venv/Lib/site-packages/astor/source_repr.py')
