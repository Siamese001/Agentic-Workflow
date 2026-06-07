"""Contract-test fixtures (deterministic slices from production proof runs)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_LEGACY_FIXTURES_PATH = Path(__file__).resolve().parent.parent / "fixtures.py"
_SPEC = importlib.util.spec_from_file_location(
    "tests._apps_contract._legacy_fixtures_module",
    _LEGACY_FIXTURES_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load contract fixtures from {_LEGACY_FIXTURES_PATH}")
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

APP_CONTRACT_REGISTRY = _MODULE.APP_CONTRACT_REGISTRY
AppContract = _MODULE.AppContract
build_config = _MODULE.build_config
build_request = _MODULE.build_request
build_result = _MODULE.build_result
import_class = _MODULE.import_class

__all__ = [
    "APP_CONTRACT_REGISTRY",
    "AppContract",
    "build_config",
    "build_request",
    "build_result",
    "import_class",
]
