"""conftest for apps_rg tests - handles Pydantic V2 deprecation warnings and package shadowing."""

import sys
import warnings
from pathlib import Path

import pytest

# Ensure repo root is on sys.path BEFORE any test module import
_REPO_ROOT = str(Path(__file__).resolve().parents[3])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Purge any apps_rg shadow registered from tests/unit/apps_rg/__init__.py
# so imports like `from apps_rg.config.X import Y` resolve to the real package
_TESTS_ROOT = str(Path(__file__).resolve().parents[2])
_to_purge = [
    k
    for k, m in sys.modules.items()
    if (k == "apps_rg" or k.startswith("apps_rg.")) and _TESTS_ROOT in (getattr(m, "__file__", "") or "")
]
for _k in _to_purge:
    del sys.modules[_k]

# Filter Pydantic V2 deprecation warnings to prevent collection errors
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
def _apps_rg_unit_test_harness(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests are not ``python -m apps_rg`` product runs — relax fail-closed shortcuts."""
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")


@pytest.fixture(autouse=True)
def _w6_r1b_order_isolation(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """W6 receipt tests fail under full-suite env leaks; isolate cache/Chroma per test."""
    nodeid = request.node.nodeid.replace("\\", "/")
    if "section_evidence_w6" not in nodeid:
        yield
        return
    from apps_rg.cache.r1b_bge_embedding import reset_bge_model_for_testing
    from apps_rg.runtime import qwen_transport_diag as qtd

    reset_bge_model_for_testing()
    qtd.reset_transport_context_for_tests()
    cache_root = tmp_path / "r1b_cache"
    chroma_dir = tmp_path / "chroma"
    monkeypatch.setenv("APPS_RG_R1B_CACHE_ROOT", str(cache_root))
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(chroma_dir))
    monkeypatch.delenv("APPS_RG_R1B_SKIP_CHROMA_PROJECTION", raising=False)
    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    yield
    reset_bge_model_for_testing()
    qtd.reset_transport_context_for_tests()
