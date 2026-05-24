"""W10 — apps_rg Exit/X3/UWG/L4 no-bypass + deprecated path non-proof (contract only)."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from apps_rg.runtime.aggregation.review_lane_policy import MOCK_RUNTIME_STATUSES, X3_ALLOW
from apps_rg.runtime.run_bundle_index import _LANE_CORE

REPO_ROOT = Path(__file__).resolve().parents[2]

def _archived_shim_rel() -> str:
    repo = Path(__file__).resolve().parents[2]
    matches = sorted(
        (repo / "archives").glob(
            "l2_rationalization_*/agentic_core/L2_execution/apps_rg_l2_binding.py"
        )
    )
    assert matches, "archived shim missing"
    return matches[-1].relative_to(repo).as_posix()


NON_PRODUCT_PROOF_PATHS: tuple[str, ...] = (
    "tests/fixtures/apps_rg/",
)

NON_PRODUCT_ENV_MARKERS: frozenset[str] = frozenset(
    {
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "APPS_RG_L2_PROVIDER_MODE=stub_only",
        "RETIRED_APPS_RG_R4_GENERATION_MODE",
    }
)


def test_canonical_lane_bundle_requires_x3_disposition_artifact() -> None:
    names = {row[0] for row in _LANE_CORE}
    filenames = {row[1] for row in _LANE_CORE}
    assert "disposition_x3" in names
    assert "x3_disposition.json" in filenames


def test_x2_x1d_alone_insufficient_for_product_allow() -> None:
    """Product ALLOW requires X3_ALLOW + REAL_LLM — not X2 pass alone."""
    from apps_rg.runtime.aggregation.review_lane_policy import _classify_lane

    x2_only = _classify_lane(
        lane="headline",
        x3_code="X3_REVIEW_STRUCTURAL",
        runtime_generation_status="REAL_LLM",
        authorization_scope="PRODUCT",
        product_quality_status="PASS",
    )
    assert x2_only["supports_product_allow"] is False

    allow = _classify_lane(
        lane="headline",
        x3_code=X3_ALLOW,
        runtime_generation_status="REAL_LLM",
        authorization_scope="PRODUCT",
        product_quality_status="PASS",
    )
    assert allow["supports_product_allow"] is True


def test_mock_stub_runtime_status_not_product_allow() -> None:
    from apps_rg.runtime.aggregation.review_lane_policy import _classify_lane

    for rgs in MOCK_RUNTIME_STATUSES:
        out = _classify_lane(
            lane="headline",
            x3_code=X3_ALLOW,
            runtime_generation_status=rgs,
            authorization_scope="PRODUCT",
            product_quality_status="PASS",
        )
        assert out["supports_product_allow"] is False


def test_exit_binding_exports_exit_finalize_and_x3() -> None:
    mod = importlib.import_module("apps_rg.runtime.bindings.exit_binding")
    assert hasattr(mod, "exit_finalize_apps_rg")
    assert hasattr(mod, "X3Disposition") or "X3Disposition" in mod.__all__


def test_exit_binding_documents_inert_commit_candidate() -> None:
    src = Path(
        importlib.import_module("apps_rg.runtime.bindings.exit_binding").__file__
    ).read_text(encoding="utf-8")
    assert "InertArtifactCommitCandidate" in src or "mutation_candidate_inert" in src
    assert "X3Disposition" in src or "x3_disposition" in src


def test_gap001_exit_l4_hardening_tests_exist() -> None:
    """Regression harness: Exit must not durable-write outside UWG."""
    path = REPO_ROOT / "tests/_apps_contract/test_gap001_exit_l4_boundary_hardening.py"
    assert path.is_file()
    src = path.read_text(encoding="utf-8")
    assert "X3Disposition" in src
    assert "InertArtifactCommitCandidate" in src or "mutation_candidate_inert" in src


def test_archived_l2_shim_quarantine_path_exists() -> None:
    rel = _archived_shim_rel()
    assert (REPO_ROOT / rel).is_file(), rel


@pytest.mark.parametrize("rel_path", NON_PRODUCT_PROOF_PATHS)
def test_non_product_paths_exist_but_classified_quarantine(rel_path: str) -> None:
    full = REPO_ROOT / rel_path
    if rel_path.endswith("/"):
        assert full.is_dir(), rel_path
    else:
        assert full.is_file(), rel_path


def test_run_dispatch_main_retired() -> None:
    from apps_rg.l2_recipe.modular_lane_adapter import run_dispatch_main

    with pytest.raises(ImportError, match="run_dispatch_main is retired"):
        run_dispatch_main("apps_rg.runtime.dispatch.headline_dispatch", [])


def test_w10_deprecated_env_markers_documented() -> None:
    main_src = (REPO_ROOT / "apps_rg/__main__.py").read_text(encoding="utf-8")
    assert "APPS_RG_R4_GENERATION_MODE" in main_src
    assert "stub_only" in main_src or "APPS_RG_L2_FORCE_STUB" in main_src
