"""W8 — Canonical apps_rg product path hygiene (static/contract; no live Qwen/judges)."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

import pytest

from apps_rg.l2_recipe import r4_generation_route as rr
from apps_rg.runtime.runtime_proof_layout import CONTRACT_HARNESS_PREFIXES

REPO_ROOT = Path(__file__).resolve().parents[2]

CANONICAL_CHAIN: tuple[tuple[str, str], ...] = (
    ("apps_rg.__main__", "main"),
    ("agentic_core.runtime.entry.apps_rg_dispatch", "dispatch_apps_rg_run"),
    (
        "apps_rg.runtime.orchestration.canonical_dispatch",
        "run_canonical_apps_rg_from_cli_primitives",
    ),
    ("apps_rg.l2_recipe.modular_resume_generation", "run_modular_resume_generation"),
    ("apps_rg.runtime.providers.qwen_vllm_provider", "build_qwen_request"),
    ("apps_rg.runtime.judges.section_judge_profile", "resolve_section_proof_judge_model"),
    ("apps_rg.runtime.runtime_proof_layout", "prepare_runtime_proof_run_dir"),
)

NON_PRODUCT_PROOF_MARKERS: frozenset[str] = frozenset(
    {
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "APPS_RG_L2_PROVIDER_MODE=stub_only",
        "APPS_RG_L2_FORCE_STUB",
        "RETIRED_APPS_RG_R4_GENERATION_MODE",
        "--mock-judges",
        "tests/fixtures/apps_rg/",
        "APPS_RG_ALLOW_DEMO_HARNESS",
        "contract_harness/",
    }
)


def test_canonical_modules_and_symbols_exist() -> None:
    for mod_name, attr in CANONICAL_CHAIN:
        mod = importlib.import_module(mod_name)
        assert hasattr(mod, attr), f"{mod_name}.{attr}"


def test_main_integrated_path_calls_dispatch_apps_rg_run() -> None:
    main = importlib.import_module("apps_rg.__main__")
    src = inspect.getsource(main.main)
    assert "run_whole_run_with_route_governance" in src
    assert "run_whole_run_spine_harness" not in src


def test_dispatch_apps_rg_run_delegates_to_canonical_dispatch() -> None:
    mod = importlib.import_module("agentic_core.runtime.entry.apps_rg_dispatch")
    src = inspect.getsource(mod.dispatch_apps_rg_run)
    assert "run_canonical_apps_rg_from_cli_primitives" in src


def test_r4_ssot_modular_is_canonical_proven_route() -> None:
    assert rr.CANONICAL_PROVEN_GENERATION_ROUTE == "modular_section_lanes"
    assert rr.R4_RECIPE_USES_FULL_RESUME_ENVELOPE_CPA is False


def test_section_lanes_package_exists() -> None:
    sections = REPO_ROOT / "apps_rg" / "runtime" / "sections"
    lane_files = list(sections.glob("*_lane.py"))
    assert len(lane_files) >= 7


def test_runtime_proof_layout_distinguishes_contract_harness() -> None:
    assert CONTRACT_HARNESS_PREFIXES
    assert any(p.startswith("_contract") or "contract" in p for p in CONTRACT_HARNESS_PREFIXES)


def test_non_product_markers_registry_for_report() -> None:
    """Markers listed for w6_w9 report — must not be treated as product proof."""
    joined = " ".join(NON_PRODUCT_PROOF_MARKERS)
    assert "fixtures/apps_rg" in joined
    assert "DEMO_HARNESS" in joined
    assert "contract_harness" in joined
    assert "stub" in joined.lower()
