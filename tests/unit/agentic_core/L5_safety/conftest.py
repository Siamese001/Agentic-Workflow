from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import pytest

FIRST_PARTY_MODULE_PREFIXES = (
    "agentic_core",
    "system_learning",
    "fix_high_severity_silent_swallowers",
)


def _candidate_roots() -> list[Path]:
    cwd = Path.cwd().resolve()
    file_root = Path(__file__).resolve().parent
    candidates: list[Path] = [cwd, *cwd.parents, file_root, *file_root.parents]
    seen: set[Path] = set()
    ordered: list[Path] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            ordered.append(candidate)
    return ordered


def _bootstrap_repo_path() -> bool:
    for candidate in _candidate_roots():
        agentic_core_dir = candidate / "agentic_core"
        if agentic_core_dir.is_dir():
            candidate_str = str(candidate)
            if candidate_str not in sys.path:
                sys.path.insert(0, candidate_str)
            return True
    return False


HAS_MONOREPO = _bootstrap_repo_path()


@lru_cache(maxsize=None)
def _source_text(path_str: str) -> str:
    try:
        return Path(path_str).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _requires_monorepo(item: pytest.Item) -> bool:
    text = _source_text(str(item.path))
    return any(prefix in text for prefix in FIRST_PARTY_MODULE_PREFIXES)


def pytest_collection_modifyitems(config, items) -> None:  # pragma: no cover
    if HAS_MONOREPO:
        return
    skip_marker = pytest.mark.skip(
        reason="Requires first-party monorepo content that is not included in this standalone snapshot.",
    )
    for item in items:
        if _requires_monorepo(item):
            item.add_marker(skip_marker)


def pytest_configure(config) -> None:  # pragma: no cover
    config.addinivalue_line("markers", "unit: unit-level test")
    config.addinivalue_line("markers", "unit_min_deps: unit test with minimal dependency surface")
    config.addinivalue_line("markers", "spec: specification-style test")
