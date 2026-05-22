"""E2E: graph-only story lanes — no SRFS/base-resume bullet authority (offline stub)."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.sections.graph_story_authority import (
    change_log_has_base_resume_hydration,
    verbatim_base_resume_bullet_ids,
)
from apps_rg.runtime.sections.ibm_canonical_hydration import (
    hydrate_parsed_ibm_bullets_from_canonical_resume,
)
from apps_rg.runtime.sections.unify_canonical_hydration import (
    hydrate_parsed_unify_bullets_from_canonical_resume,
)

from tests._apps_contract.contract_harness_paths import harness_run

REPO = Path(__file__).resolve().parents[2]
LEDGER = default_ledger_path(REPO)
STORY_BULLET_LANES = ("unify_bullets", "ibm_bullets")


@pytest.fixture
def stub_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")


@pytest.mark.skipif(not LEDGER.is_file(), reason="master candidate fact ledger missing")
@pytest.mark.parametrize("section_id", STORY_BULLET_LANES)
def test_story_bullet_lane_graph_proof_pool_and_no_base_hydration(
    section_id: str,
    stub_env: None,
    tmp_path: Path,
) -> None:
    run_dir = harness_run(f"_graph_story_{uuid.uuid4().hex[:12]}", section_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    args = argparse.Namespace(
        provider="qwen_vllm",
        temperature=0.45,
        x1d_judges="gemini_pro",
        mock_judges=True,
        allow_test_mock_judges=True,
        target_title="VP Engineering",
        target_company="Acme Corp",
        jd_text="Lead platform engineering and AI delivery.",
        briefing="Emphasize scale, governance, and regulated delivery.",
        base_resume_ref="",
    )
    if section_id == "unify_bullets":
        from apps_rg.runtime.sections.unify_bullets_lane import run_unify_bullets_execution

        ctx = run_unify_bullets_execution(args, artifact_dir_override=run_dir)
    else:
        from apps_rg.runtime.sections.ibm_bullets_lane import run_ibm_bullets_execution

        ctx = run_ibm_bullets_execution(args, artifact_dir_override=run_dir)

    payload = json.loads((run_dir / "runtime_payload.json").read_text(encoding="utf-8"))
    meta = payload.get("proof_pool_metadata") or {}
    assert meta.get("proof_pool_type") == "augmented_skills_graph"
    assert meta.get("skills_authority_status") == "PASS"
    assert meta.get("base_resume_claim_authority") is False

    x2_path = run_dir / "x2_gate_outputs.json"
    assert x2_path.is_file()
    x2 = json.loads(x2_path.read_text(encoding="utf-8"))
    gate_ids = {g.get("gate_id") for g in x2.get("gates") or []}
    graph_gate = (
        "x2_unify_augmented_skills_graph_proof_pool_only"
        if section_id == "unify_bullets"
        else "x2_ibm_augmented_skills_graph_proof_pool_only"
    )
    no_base_gate = (
        "x2_unify_graph_only_no_base_resume_bullets"
        if section_id == "unify_bullets"
        else "x2_ibm_graph_only_no_base_resume_bullets"
    )
    assert graph_gate in gate_ids
    assert no_base_gate in gate_ids
    for g in x2.get("gates") or []:
        if g.get("gate_id") in (graph_gate, no_base_gate):
            assert g.get("pass") is True, g

    parsed_path = run_dir / "parsed_output.json"
    if parsed_path.is_file():
        parsed = json.loads(parsed_path.read_text(encoding="utf-8"))
        assert not change_log_has_base_resume_hydration(parsed)
        base_path = REPO / "apps_rg/resume/base/amit_ayer_base_resume_v1.json"
        if base_path.is_file():
            base = json.loads(base_path.read_text(encoding="utf-8"))
            assert not verbatim_base_resume_bullet_ids(
                parsed, base_resume=base, section_id=section_id
            )

    assert ctx.get("x3") is not None


def test_hydrate_functions_raise() -> None:
    with pytest.raises(ValueError, match="forbidden"):
        hydrate_parsed_unify_bullets_from_canonical_resume(
            {},
            runtime_payload={},
            canon_facts=[],
            canon_allowed=set(),
            default_intensity_by_bullet={},
        )
    with pytest.raises(ValueError, match="forbidden"):
        hydrate_parsed_ibm_bullets_from_canonical_resume(
            {},
            runtime_payload={},
            canon_facts=[],
            canon_allowed=set(),
            default_intensity_by_bullet={},
        )


def test_canonical_dispatch_has_no_selected_role_fact_set_parameters() -> None:
    import inspect

    from apps_rg.runtime.orchestration import canonical_dispatch as cd

    for name, fn in inspect.getmembers(cd, inspect.isfunction):
        if not name.startswith("_run_") or not name.endswith("_from_cli"):
            continue
        sig = inspect.signature(fn)
        assert "selected_role_fact_set" not in sig.parameters, name
