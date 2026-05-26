"""Shared fixtures for apps_rg contract tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests._apps_contract.lane_cli_common import contract_harness_fast

_REPO = Path(__file__).resolve().parents[2]

# Subprocess ``python -m apps_rg`` lanes — each run is minutes when vLLM is up.
_LIVE_CLI_PATH_FRAGMENTS = (
    "section_pipeline",
    "runtime_slice",
    "live_proof",
    "integrated_spine",
    "graph_story_authority_e2e",
    "c0_evidence_room",
    "c0_fec_single_reality",
    "augmented_skills_graph_all_sections",
    "section_input_usage_ledgers",
    "resume_lanes_live",
    "qwen_vllm_reliability",
    "l6_shadow_learning",
    "section_lane_c0_metrics",
)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "contract_harness_live: full python -m apps_rg subprocess with live qwen_vllm",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    fast = contract_harness_fast()
    for item in items:
        path = Path(str(item.fspath)).as_posix().replace("\\", "/")
        if "/tests/_apps_contract/" not in path:
            continue
        if any(frag in path for frag in _LIVE_CLI_PATH_FRAGMENTS):
            item.add_marker(pytest.mark.contract_harness_live)
            item.add_marker(pytest.mark.slow)
            if fast:
                item.add_marker(
                    pytest.mark.skip(
                        reason="APPS_RG_CONTRACT_HARNESS_FAST=1 (use run_contract_harness_live.py for CLI proof)",
                    )
                )


@pytest.fixture(autouse=True)
def _contract_harness_runtime_env(monkeypatch: pytest.MonkeyPatch, tmp_path_factory) -> None:
    """Align contract tests with live qwen_vllm + optional C0 Chroma (root conftest sets stub_only)."""
    monkeypatch.setenv("APPS_RG_L2_PROVIDER_MODE", "live_allowed")
    monkeypatch.setenv("PYTEST_APPS_RG_LIVE_L2", "1")
    monkeypatch.delenv("APPS_RG_L2_FORCE_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)

    # Fast harness: do not point at Chroma unless embeddings are enabled (fail-closed C0.2).
    if not contract_harness_fast():
        chroma_default = _REPO / "data" / "cache" / "chromadb"
        if chroma_default.is_dir():
            monkeypatch.setenv("CHROMA_PERSIST_DIR", str(chroma_default.resolve()))
        else:
            chroma_tmp = tmp_path_factory.mktemp("contract_chroma")
            chroma_tmp.mkdir(parents=True, exist_ok=True)
            monkeypatch.setenv("CHROMA_PERSIST_DIR", str(chroma_tmp))
    else:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.setenv("APPS_RG_C0_EVIDENCE_ROOM", "0")

    cache_root = _REPO / "data" / "cache" / "r1b"
    cache_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("APPS_RG_R1B_CACHE_ROOT", str(cache_root.resolve()))


@pytest.fixture(autouse=True)
def _contract_tests_proof_pool_fixture_dev_bypass() -> None:
    """Direct ``resolve_section_proof_pool`` contract tests: non-product-certified bypass."""
    from apps_rg.runtime.spine.front_contracts import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()
