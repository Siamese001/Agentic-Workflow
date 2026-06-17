"""conftest for apps_research tests - keeps source imports ahead of test shadows."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

# Ensure the repo root is on sys.path before any apps_research imports.
_REPO_ROOT = str(Path(__file__).resolve().parents[3])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Purge any apps_research shadow modules that may have been imported from tests/.
_TESTS_ROOT = str(Path(__file__).resolve().parents[2])
_to_purge = [
    key
    for key, module in sys.modules.items()
    if (key == "apps_research" or key.startswith("apps_research."))
    and _TESTS_ROOT in (getattr(module, "__file__", "") or "")
]
for _key in _to_purge:
    del sys.modules[_key]

warnings.filterwarnings(
    "ignore",
    message=".*PydanticDeprecatedSince20.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=".*Pydantic V1 style.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=".*Support for class-based.*",
    category=DeprecationWarning,
)


@pytest.fixture(autouse=True)
def _apps_research_unit_test_harness(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests are not `python -m apps_research` product runs."""
    monkeypatch.setenv("APPS_RESEARCH_TEST_HARNESS", "1")
