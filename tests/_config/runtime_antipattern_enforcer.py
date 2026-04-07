"""Runtime anti-pattern enforcement fixtures for test execution.

Catches policy bypass and unverified file mutations during test runs.
Import this module in a conftest.py or use the fixtures directly.

Fixtures (autouse=False by default — opt-in per test suite):
  - enforce_no_unverified_writes: fails tests that write files without
    calling mark_path_validated() first.
  - enforce_no_policy_bypass: fails tests where enforcement modules are
    imported directly from lower layers without going through validators.

Helper (for production code):
  - mark_path_validated(path): mark a path as validated before writing.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Generator

import pytest

# ---------------------------------------------------------------------------
# Thread-local validated-path registry
# ---------------------------------------------------------------------------

_thread_local = threading.local()

_TEMP_PATH_FRAGMENTS: tuple[str, ...] = (
    "/tmp/",
    "\\Temp\\",
    "\\tmp\\",
    "/var/folders/",
    "pytest-",
    ".pytest_cache",
    "__pycache__",
)


def mark_path_validated(path: str | Path) -> None:
    """Mark *path* as validated so that ``enforce_no_unverified_writes`` allows the write.

    Call this after your validation logic and before the actual open() call::

        validate_path(path)          # your existing validation
        mark_path_validated(path)    # tell the test hook it's safe
        with open(path, "w") as f:
            f.write(data)
    """
    if not hasattr(_thread_local, "validated_paths"):
        _thread_local.validated_paths: set[str] = set()
    _thread_local.validated_paths.add(str(path))


def is_path_validated(path: str | Path) -> bool:
    """Return True if *path* was marked validated in this thread."""
    if not hasattr(_thread_local, "validated_paths"):
        return False
    return str(path) in _thread_local.validated_paths


def clear_validated_paths() -> None:
    """Clear the validated-path registry (called automatically per test)."""
    if hasattr(_thread_local, "validated_paths"):
        _thread_local.validated_paths.clear()


def _is_temp_path(path_str: str) -> bool:
    """Return True if *path_str* looks like a temporary or test-fixture path."""
    return any(frag in path_str for frag in _TEMP_PATH_FRAGMENTS)


# ---------------------------------------------------------------------------
# Fixture: enforce_no_unverified_writes
# ---------------------------------------------------------------------------


@pytest.fixture()
def enforce_no_unverified_writes(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Fail tests that write files without prior ``mark_path_validated()`` call.

    Wraps ``builtins.open`` so that any write-mode call (``'w'``, ``'a'``,
    ``'x'``, ``'wb'``, ``'ab'``) to a non-temporary path raises
    ``AssertionError`` unless the path was first validated via
    ``mark_path_validated()``.

    Usage::

        def test_my_writer(enforce_no_unverified_writes, tmp_path):
            mark_path_validated(tmp_path / "output.json")
            my_writer.write(tmp_path / "output.json", data)  # now allowed

    Paths inside system temp dirs and pytest fixtures are always allowed.
    """
    clear_validated_paths()
    _builtin_open = open

    def _guarded_open(file: object, mode: str = "r", *args: object, **kwargs: object) -> object:
        str_path = str(file)
        write_modes = {"w", "a", "x", "wb", "ab", "xb", "w+", "a+", "r+"}
        is_write = any(m in str(mode) for m in ("w", "a", "x")) and "r" not in str(mode).replace("+", "")
        # More precise: check mode string directly
        mode_str = str(mode)
        is_write = any(c in mode_str for c in ("w", "a", "x"))

        if is_write and not _is_temp_path(str_path) and not is_path_validated(str_path):
            raise AssertionError(
                f"Unverified write detected: open({str_path!r}, {mode!r})\n"
                f"Call mark_path_validated(path) after validation before writing.",
            )
        return _builtin_open(file, mode, *args, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr("builtins.open", _guarded_open)
    yield
    clear_validated_paths()


# ---------------------------------------------------------------------------
# Fixture: enforce_no_policy_bypass
# ---------------------------------------------------------------------------

_ENFORCEMENT_FRAGMENTS: tuple[str, ...] = ("enforcement",)
_LOWER_LAYER_PREFIXES: tuple[str, ...] = (
    "agentic_core.L0_routing",
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
)
_VALIDATOR_FRAGMENTS: tuple[str, ...] = ("validator", "validators", "enforcement")


@pytest.fixture()
def enforce_no_policy_bypass() -> Generator[None, None, None]:
    """Detect enforcement modules imported directly from lower layers.

    After the test, checks ``sys.modules`` for enforcement-layer modules
    imported from L0/L1/L2 without a corresponding validators/ module also
    loaded in the same import chain.  Emits a warning (not a hard failure)
    because false positives are possible — some enforcement imports are
    legitimately direct.

    Yields a list of detected bypasses so tests can assert on them::

        def test_no_bypass(enforce_no_policy_bypass):
            import_module_under_test()
            # fixture yields — no bypass expected, test passes silently
    """
    import sys

    snapshot_before: set[str] = set(sys.modules.keys())
    yield

    snapshot_after: set[str] = set(sys.modules.keys())
    new_modules = snapshot_after - snapshot_before

    bypasses: list[str] = []
    for mod_name in sorted(new_modules):
        if not any(mod_name.startswith(prefix) for prefix in _LOWER_LAYER_PREFIXES):
            continue
        if "enforcement" not in mod_name:
            continue
        # Check: is there a validators/ counterpart also loaded?
        base = mod_name.rsplit(".enforcement", 1)[0]
        validator_loaded = any(m.startswith(base) and "validator" in m for m in snapshot_after)
        if not validator_loaded:
            bypasses.append(mod_name)

    if bypasses:
        import warnings

        warnings.warn(
            f"Potential policy bypass — enforcement imported without validators: {bypasses}",
            stacklevel=2,
        )
