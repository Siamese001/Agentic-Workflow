"""Phase 4 — ADG / GraphRAG substrate rule and runtime guard.

Clean rule (from spec):
  * SQLite is canonical ADG truth.
  * GraphDB is the traversal projection.
  * GraphRAG / C0.3 uses the GraphDB traversal adapter.
  * C0.3 must NOT directly traverse SQLite.
  * LLM synthesis receives a C0 evidence packet, never raw SQLite rows.

This module supplies:
  * ``assert_no_direct_sqlite_traversal(modules)`` — a static-style guard
    that raises ``SubstrateViolation`` if any C0.3 runtime module imports
    ``sqlite3``,
  * ``sqlite_substrate_guard()`` — a context manager that monkey-patches
    ``sqlite3.connect`` to raise ``SubstrateViolation`` if invoked from any
    frame whose filename is inside the C0.3 runtime path.
"""

from __future__ import annotations

import contextlib
import inspect
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable, Iterator


C0_3_RUNTIME_DIRNAME = "c0_3_enhanced"

# substrate.py legitimately imports sqlite3 to install the runtime guard;
# exclude it from the substrate-rule scan.
_SUBSTRATE_SELF_FILENAME = "substrate.py"

# Exact runtime directory — populated at module import. Used to filter
# stack frames so test files whose path contains "c0_3_enhanced" but which
# live under tests/ are NOT treated as runtime frames.
_C0_3_RUNTIME_DIR = Path(__file__).resolve().parent


class SubstrateViolation(RuntimeError):
    """Raised when a C0.3 runtime path attempts direct SQLite traversal."""


def _module_imports_sqlite(mod: ModuleType) -> bool:
    src = getattr(mod, "__file__", None)
    if not src:
        return False
    if Path(src).name == _SUBSTRATE_SELF_FILENAME:
        return False  # substrate.py installs the guard; legitimate import
    try:
        with open(src, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    if "import sqlite3" in text or "from sqlite3" in text:
        return True
    return False


def assert_no_direct_sqlite_traversal(
    modules: Iterable[ModuleType] | None = None,
) -> None:
    """Static guard.

    Walks the C0.3 enhanced subpackage (or the supplied modules) and raises
    ``SubstrateViolation`` if any of them import sqlite3.

    Allowed modules in the future MAY whitelist projection-builder-only
    paths — keep this list empty until that need surfaces.
    """
    if modules is None:
        package_root = Path(__file__).parent
        modules = [
            mod
            for name, mod in list(sys.modules.items())
            if mod is not None
            and getattr(mod, "__file__", None)
            and Path(str(mod.__file__)).parent == package_root
        ]
    bad: list[str] = []
    for mod in modules:
        if _module_imports_sqlite(mod):
            bad.append(getattr(mod, "__name__", repr(mod)))
    if bad:
        raise SubstrateViolation("C0.3 runtime modules must not import sqlite3 directly: " + ", ".join(bad))


@contextlib.contextmanager
def sqlite_substrate_guard() -> Iterator[None]:
    """Runtime guard.

    Wraps ``sqlite3.connect`` and ``sqlite3.Connection.__init__`` so any call
    originating from inside ``c0_3_enhanced`` raises ``SubstrateViolation``.
    Calls from elsewhere (e.g. CI tools, projection builders) are allowed.
    """
    import sqlite3

    real_connect = sqlite3.connect

    runtime_dir_norm = os.path.normcase(str(_C0_3_RUNTIME_DIR))

    def _frame_in_runtime() -> str | None:
        for frame_info in inspect.stack():
            fname = frame_info.filename or ""
            if not fname:
                continue
            try:
                resolved = Path(fname).resolve()
            except OSError:
                continue
            parent_norm = os.path.normcase(str(resolved.parent))
            # Frame is "runtime" only if its file lives EXACTLY inside the
            # c0_3_enhanced package directory (case-insensitive on Windows).
            if parent_norm != runtime_dir_norm:
                continue
            # substrate.py installs the guard; allow it to bootstrap.
            if resolved.name == _SUBSTRATE_SELF_FILENAME:
                continue
            return fname
        return None

    def _guarded_connect(*args, **kwargs):  # type: ignore[no-untyped-def]
        offending = _frame_in_runtime()
        if offending is not None:
            raise SubstrateViolation(f"Direct SQLite traversal forbidden in C0.3 runtime path: {offending}")
        return real_connect(*args, **kwargs)

    sqlite3.connect = _guarded_connect  # type: ignore[assignment]
    try:
        yield
    finally:
        sqlite3.connect = real_connect  # type: ignore[assignment]


__all__ = [
    "SubstrateViolation",
    "assert_no_direct_sqlite_traversal",
    "sqlite_substrate_guard",
]
