import sys
from pathlib import Path

# With --import-mode=importlib, pytest inserts tests/ before PROJECT_ROOT because
# __init__.py files exist in tests/system_learning/. Re-promote PROJECT_ROOT to
# position 0 so that `import system_learning.*` resolves to the production package,
# not the tests/system_learning/ namespace package.
_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT in sys.path:
    sys.path.remove(_ROOT)
sys.path.insert(0, _ROOT)
