import importlib as _importlib
import importlib.util as _ilu
import sys as _sys
from pathlib import Path as _Path

# Under --import-mode=importlib, pytest registers this file as the 'agentic_core'
# package in sys.modules.  We must immediately replace that entry with the real
# production package so all sub-imports resolve correctly.
_project_root = str(_Path(__file__).parent.parent.parent)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)

_real_pkg_path = _Path(_project_root) / "agentic_core"
_current = _sys.modules.get("agentic_core")
_current_paths = list(getattr(_current, "__path__", []))
_is_tests_pkg = any("tests" in str(p) for p in _current_paths)
if _is_tests_pkg:
    # Remove the tests/agentic_core namespace and all sub-entries
    _to_del = [k for k in list(_sys.modules) if k == "agentic_core" or k.startswith("agentic_core.")]
    for _k in _to_del:
        del _sys.modules[_k]
    # Re-import from the project root
    _importlib.import_module("agentic_core")
