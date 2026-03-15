"""Guard test: importing critical agents must not raise MRO TypeError.

This test validates that the redundant SubatomicTestingMixin removal
from agent class hierarchies does not regress. SovereignBaseAgent already
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

includes SubatomicTestingMixin in its MRO, so subclasses must NOT
re-declare it as a direct base.

The allowlist is loaded from critical_modules.txt (tracked, reviewable).
Redundant-base assertion covers ALL allowlisted agents, not only L6.
"""

import importlib
import py_compile
from pathlib import Path

import pytest

CRITICAL_LIST_PATH = Path(__file__).with_name("critical_modules.txt")


def _load_critical_modules() -> list[str]:
    lines = CRITICAL_LIST_PATH.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        # Support explicit exclusions for documentation; exclusions are not loaded.
        if s.startswith("EXCLUDE "):
            continue
        out.append(s)
    assert out, (
        "critical_modules.txt yielded 0 active modules; guard cannot be considered valid. "
        "Check EXCLUDE lines in the file."
    )
    return out


CRITICAL_MODULES = _load_critical_modules()


@pytest.mark.parametrize("module_path", CRITICAL_MODULES)
def test_import_no_mro_crash(module_path: str) -> None:
    """Import must succeed without MRO TypeError."""
    importlib.import_module(module_path)


@pytest.mark.parametrize("module_path", CRITICAL_MODULES)
def test_agent_no_redundant_subatomic_base(module_path: str) -> None:
    """ALL allowlisted agents must NOT have SubatomicTestingMixin as a direct base."""
    mod = importlib.import_module(module_path)
    # Prefer the class whose name matches the module filename
    expected_name = module_path.rsplit(".", 1)[-1]
    cls = getattr(mod, expected_name, None)
    if cls is None:
        # Fallback: find a class ending with "Agent" defined in this module (not imported)
        cls = next(
            (
                v
                for k, v in mod.__dict__.items()
                if k.endswith("Agent")
                and isinstance(v, type)
                and getattr(v, "__module__", None) == mod.__name__
            ),
            None,
        )
    assert cls is not None, f"No agent class found in {module_path}"
    mro_names = {c.__name__ for c in cls.__mro__}
    # Positive: SubatomicTestingMixin must be reachable via base agent MRO
    assert "SubatomicTestingMixin" in mro_names, (
        f"{cls.__name__} is missing SubatomicTestingMixin from its MRO "
        f"(expected via SovereignBaseAgent inheritance chain)"
    )
    # Negative: it must NOT be a direct base (redundant base anti-pattern)
    assert all(b.__name__ != "SubatomicTestingMixin" for b in cls.__bases__), (
        f"{cls.__name__} redundantly inherits SubatomicTestingMixin as a direct base"
    )


def _resolve_source_path(module_path: str) -> Path:
    """Resolve a dotted module path to its on-disk .py file."""
    parts = module_path.split(".")
    # Walk from project root (two levels up from this test file)
    base = Path(__file__).resolve().parent.parent.parent
    candidate = base / Path(*parts)
    py_file = candidate.with_suffix(".py")
    if py_file.is_file():
        return py_file
    pkg_init = candidate / "__init__.py"
    if pkg_init.is_file():
        return pkg_init
    pytest.fail(f"Cannot resolve source for {module_path}: tried {py_file} and {pkg_init}")


@pytest.mark.parametrize("module_path", CRITICAL_MODULES)
def test_preflight_compile(module_path: str) -> None:
    """Source file for each allowlisted module must compile without SyntaxError."""
    src = _resolve_source_path(module_path)
    try:
        py_compile.compile(str(src), doraise=True)
    except py_compile.PyCompileError as exc:
        pytest.fail(
            f"Preflight compile failed for {module_path}\n"
            f"  source: {src}\n"
            f"  error:  {exc.__class__.__name__}: {exc}",
        )
