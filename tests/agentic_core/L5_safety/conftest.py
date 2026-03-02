"""
conftest.py for tests/agentic_core/L5_safety/

Under --import-mode=importlib pytest registers tests/agentic_core as the
'agentic_core' package in sys.modules, shadowing the production package at
the project root.  The pytest_configure hook fires before any test module is
imported, purging all agentic_core.* entries from sys.modules and re-inserting
the project root so subsequent imports resolve to the real production package.
"""

import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).parent.parent.parent.parent)


def pytest_configure(config):
    """Purge shadowed agentic_core from sys.modules before any test imports."""
    if _PROJECT_ROOT not in sys.path:
        sys.path.insert(0, _PROJECT_ROOT)

    # Remove all agentic_core.* entries that point into tests/ so the next
    # import resolves from the project root production package.
    _tests_agentic_core = str(Path(_PROJECT_ROOT) / "tests" / "agentic_core")
    to_delete = []
    for key, mod in sys.modules.items():
        if not key.startswith("agentic_core"):
            continue
        pkg_path = getattr(mod, "__path__", None)
        pkg_file = getattr(mod, "__file__", None) or ""
        if pkg_path and any(_tests_agentic_core in str(p) for p in pkg_path):
            to_delete.append(key)
        elif _tests_agentic_core in pkg_file:
            to_delete.append(key)
    for key in to_delete:
        del sys.modules[key]
