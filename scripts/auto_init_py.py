# scripts/auto_init_py.py
import sys, pathlib

for p in sys.argv[1:]:
    path = pathlib.Path(p)
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    init_file = parent / "__init__.py"
    if not init_file.exists():
        init_file.touch(exist_ok=True)
