from __future__ import annotations

import sys
import types
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TESTS_ROOT = _REPO_ROOT / "tests"
_TESTS_FLAT_ROOT = _REPO_ROOT / "tests_flat"

for _candidate in (_REPO_ROOT, _TESTS_FLAT_ROOT):
    _candidate_str = str(_candidate)
    if _candidate_str not in sys.path:
        sys.path.insert(0, _candidate_str)

_tests_pkg = sys.modules.setdefault("tests", types.ModuleType("tests"))
_tests_pkg.__path__ = list({*(getattr(_tests_pkg, "__path__", []) or []), str(_TESTS_ROOT), str(_TESTS_FLAT_ROOT)})

__all__ = []
