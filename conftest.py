"""
Root conftest.py

Under --import-mode=importlib, pytest can register tests/agentic_core as the
'agentic_core' package in sys.modules, shadowing the production package.
This hook fires at the very start of the session (before any __init__.py is
imported) and ensures the project root is at the front of sys.path so that
'from agentic_core.X import Y' always resolves to the real production package.
"""

import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).parent)


def pytest_configure(config):
    if _PROJECT_ROOT not in sys.path:
        sys.path.insert(0, _PROJECT_ROOT)
