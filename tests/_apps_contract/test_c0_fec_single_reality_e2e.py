"""E2E: C0 proof pool → FEC materialization → PA/X2 share one fact set and digest.

Guards the failure mode where pool_ids (A) and FEC allowed ids (B) diverge before
prompt assembly and X2 validation — different digests, different realities.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.embedding_settings import bootstrap_apps_rg_embedding_env
from apps_rg.runtime.evidence.canonical_evidence_x2 import append_canonical_evidence_invariant_x2_gates
from apps_rg.runtime.evidence.canonical_section_evidence_set import (
    build_canonical_section_evidence_set,
    canonical_evidence_set_digest,
    collect_prompt_c0_fact_ids,
    validate_downstream_subset,
)
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane
from apps_rg.runtime.spine.c0_fec_compose import (
    FEC_BRIDGE_ARTIFACT,
    wire_spine_c0_fec_for_section,
)
from apps_rg.runtime.sections.competencies_lane_defaults import (
    BRIEFING_DEFAULT,
    JD_TEXT_DEFAULT,
    REPO_ROOT,
    TARGET_COMPANY_DEFAULT,
    TARGET_TITLE_DEFAULT,
)
from apps_rg.runtime.sections.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
from apps_rg.runtime.validators.executive_summary_x2 import X2GateResult

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "artifacts/apps_rg/c0/prior_resume_variant_fact_extraction_manifest.json"
LEDGER = default_ledger_path(REPO)

_X2_REALITY_GATE_IDS = (
    "x2_fec_subset_of_canonical_evidence_pool",
    "x2_prompt_c0_ids_subset_of_fec",
    "x2_claim_ledger_source_fact_ids_subset_of_fec",
    "X2_BLOCK_ID_NAMESPACE_SPLIT",
    "x2_active_pool_digest_matches_fec_digest",
)


def _bootstrap_c0_e2e_env() -> None:
    """Match CLI: Chroma persist dir + embedding defaults for real C0 evidence room."""
    os.environ["APPS_RG_C0_EVIDENCE_ROOM"] = "1"
    bootstrap_apps_rg_embedding_env(REPO)


def _lane_args() -> argparse.Namespace:
    return argparse.Namespace(
        target_company=TARGET_COMPANY_DEFAULT,
        target_title=TARGET_TITLE_DEFAULT,
        target_role=TARGET_TITLE_DEFAULT,
        jd_text=JD_TEXT_DEFAULT,
        briefing=BRIEFING_DEFAULT,
        selected_role_fact_set="",
        broad_skills_ledger_path="",
        base_resume_ref="",
        provider="qwen_vllm",
    )


def _assert_single_reality_chain(
    *,
    section_id: str,
    pool: Any,
    runtime_payload: dict[str, Any],
    bridge_doc: dict[str, Any],
    fec_on_disk: dict[str, Any],
    claim_ledger: list[dict[str, Any]] | None = None,
) -> None:
    """Pool, FEC bridge, runtime_payload, and on-disk FEC must describe one reality."""
    canonical = build_canonical_section_evidence_set(pool)
    pool_ordered = list(canonical.pool_ids_ordered)
    pool_digest = canonical.pool_digest

    fec_allowed = [str(x).strip() for x in (runtime_payload.get("allowed_fact_ids") or []) if str(x).strip()]
    fec_digest = str(runtime_payload.get("fec_allowed_fact_ids_digest") or "")
    runtime_pool_digest = str(runtime_payload.get("canonical_evidence_set_digest") or "")

    assert pool_ordered, f"{section_id}: canonical pool must be non-empty"
    assert runtime_pool_digest == pool_digest, (
        f"{section_id}: runtime canonical_evidence_set_digest must match pool"
    )
    assert fec_allowed, f"{section_id}: FEC allowlist must be materialized on runtime_payload"

    mat = runtime_payload.get("fec_materialization_receipt") or {}
    narrowed = bool(mat.get("fec_narrowed_from_pool"))
    pool_set = set(pool_ordered)
    fec_set = set(fec_allowed)
    assert fec_set <= pool_set, f"{section_id}: FEC allowlist must never widen beyond pool"
    assert canonical_evidence_set_digest(fec_allowed) == fec_digest, (
        f"{section_id}: fec_allowed_fact_ids_digest must match materialized allowlist"
    )
    if narrowed:
        assert mat.get("explicit_narrowing") is True, f"{section_id}: narrowing requires receipt flag"
        dropped = set(mat.get("narrowing_dropped_pool_ids") or [])
        assert dropped or fec_set < pool_set or fec_digest != pool_digest, (
            f"{section_id}: narrowed receipt must record dropped ids or digest change"
        )
    else:
        assert fec_digest == pool_digest, (
            f"{section_id}: fec digest must equal pool digest when not explicitly narrowed"
        )
        assert fec_set == pool_set, (
            f"{section_id}: FEC allowlist must equal pool when not narrowed"
        )

    assert str(bridge_doc.get("canonical_evidence_set_digest") or "") == pool_digest
    assert str(bridge_doc.get("proof_pool_digest") or "") == pool_digest
    assert str(bridge_doc.get("fec_allowed_fact_ids_digest") or "") == fec_digest
    assert list(bridge_doc.get("allowed_fact_ids") or []) == fec_allowed

    disk_allowed = [str(x).strip() for x in (fec_on_disk.get("allowed_fact_ids") or []) if str(x).strip()]
    assert disk_allowed == fec_allowed, f"{section_id}: on-disk FEC allowlist must match runtime_payload"
    assert str(fec_on_disk.get("canonical_evidence_set_digest") or "") == pool_digest

    canon_doc = runtime_payload.get("canonical_section_evidence_set") or {}
    assert list(canon_doc.get("pool_ids_ordered") or []) == pool_ordered
    assert str(canon_doc.get("canonical_evidence_set_digest") or "") == pool_digest

    meta = runtime_payload.get("proof_pool_metadata") or {}
    assert str(meta.get("canonical_evidence_set_digest") or "") == pool_digest
    assert str(meta.get("fec_allowed_fact_ids_digest") or "") == fec_digest
    assert str(meta.get("proof_pool_digest") or "") == pool_digest

    gates: list[X2GateResult] = []
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload=runtime_payload,
        allowed_fact_ids=set(fec_allowed),
        claim_ledger=claim_ledger or [],
    )
    by_id = {g.gate_id: g for g in gates}
    for gate_id in _X2_REALITY_GATE_IDS:
        assert gate_id in by_id, f"{section_id}: missing X2 gate {gate_id}"
        assert by_id[gate_id].pass_, (
            f"{section_id}: {gate_id} failed: {by_id[gate_id].failure_reason}"
        )


@pytest.mark.skipif(not LEDGER.is_file(), reason="master candidate fact ledger missing")
@pytest.mark.skipif(not MANIFEST.is_file(), reason="prior resume variant manifest missing")
@pytest.mark.parametrize("section_id", GENERATED_LANES)
def test_generated_lane_c0_fec_single_reality_e2e(
    tmp_path: Path,
    section_id: str,
) -> None:
    """Real proof pool + C0 room + FEC bridge: pool digest, FEC digest, and X2 gates align."""
    _bootstrap_c0_e2e_env()
    artifact_dir = tmp_path / f"{section_id}_single_reality"
    pool, _base, _path, _hash, front_spine = load_section_proof_for_lane(
        section_id=section_id,
        args=_lane_args(),
        repo_root=REPO,
        collect_employment_bullets_fn=collect_employment_bullets,
        artifact_dir=artifact_dir,
    )
    assert pool.allowed_fact_ids_ordered, f"{section_id}: proof pool must resolve allowed facts"

    runtime_payload: dict[str, Any] = {
        "run_id": f"single_reality_{section_id}",
        "section_id": section_id,
        "target_title": TARGET_TITLE_DEFAULT,
        "target_company": TARGET_COMPANY_DEFAULT,
        "jd_text": JD_TEXT_DEFAULT,
        "briefing": BRIEFING_DEFAULT,
        "selected_fact_plan": dict(pool.selected_fact_plan or {}),
        "proof_pool_metadata": dict(pool.proof_pool_metadata or {}),
    }
    bridge = wire_spine_c0_fec_for_section(
        artifact_dir=artifact_dir,
        section_id=section_id,
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
    )
    fec_on_disk = json.loads((artifact_dir / FEC_BRIDGE_ARTIFACT).read_text(encoding="utf-8"))
    _assert_single_reality_chain(
        section_id=section_id,
        pool=pool,
        runtime_payload=runtime_payload,
        bridge_doc=bridge.bridge_doc,
        fec_on_disk=fec_on_disk,
    )


@pytest.mark.skipif(not LEDGER.is_file(), reason="master candidate fact ledger missing")
@pytest.mark.skipif(not MANIFEST.is_file(), reason="prior resume variant manifest missing")
def test_executive_summary_prompt_c0_ids_subset_of_fec_after_wire(tmp_path: Path) -> None:
    """PA compile must not introduce fact ids outside the materialized FEC allowlist."""
    _bootstrap_c0_e2e_env()
    section_id = "executive_summary"
    artifact_dir = tmp_path / "exec_summary_single_reality_pa"
    pool, _base, _path, _hash, front_spine = load_section_proof_for_lane(
        section_id=section_id,
        args=_lane_args(),
        repo_root=REPO,
        collect_employment_bullets_fn=collect_employment_bullets,
        artifact_dir=artifact_dir,
    )
    runtime_payload: dict[str, Any] = {
        "run_id": "single_reality_exec_pa",
        "section_id": section_id,
        "target_title": TARGET_TITLE_DEFAULT,
        "target_company": TARGET_COMPANY_DEFAULT,
        "jd_text": JD_TEXT_DEFAULT,
        "briefing": BRIEFING_DEFAULT,
        "selected_fact_plan": dict(pool.selected_fact_plan or {}),
        "proof_pool_metadata": dict(pool.proof_pool_metadata or {}),
    }
    bridge = wire_spine_c0_fec_for_section(
        artifact_dir=artifact_dir,
        section_id=section_id,
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
    )
    fec_on_disk = json.loads((artifact_dir / FEC_BRIDGE_ARTIFACT).read_text(encoding="utf-8"))
    _assert_single_reality_chain(
        section_id=section_id,
        pool=pool,
        runtime_payload=runtime_payload,
        bridge_doc=bridge.bridge_doc,
        fec_on_disk=fec_on_disk,
    )

    compiled = compile_executive_summary_prompt(runtime_payload, run_id=runtime_payload["run_id"])
    content = compiled.artifact.messages[-1]["content"]
    fec_ids = {str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])}
    alias = dict(
        (runtime_payload.get("canonical_section_evidence_set") or {}).get("id_alias_map") or {}
    )
    plan_ids = [
        str(row.get("fact_id") or "").strip()
        for row in (runtime_payload.get("selected_fact_plan") or {}).get("facts") or []
        if isinstance(row, dict) and str(row.get("fact_id") or "").strip()
    ]
    assert plan_ids, "executive_summary selected_fact_plan must list proof facts"
    for fid in plan_ids:
        assert fid in content, f"selected plan fact missing from compiled prompt: {fid}"
    plan_ok, plan_bad = validate_downstream_subset(
        plan_ids,
        fec_ids,
        label="selected_fact_plan",
        alias_map=alias,
    )
    assert plan_ok, f"selected_fact_plan facts must be subset of FEC: {plan_bad}"

    runtime_payload["section_fec_bridge"] = bridge.bridge_doc
    prompt_c0 = collect_prompt_c0_fact_ids(runtime_payload)
    prompt_ok, prompt_bad = validate_downstream_subset(
        prompt_c0,
        fec_ids,
        label="prompt_c0",
        alias_map=alias,
    )
    assert prompt_ok, f"prompt C0 ids must be subset of FEC: {prompt_bad}"


def test_divergent_pool_fec_reality_fails_x2_gates() -> None:
    """Regression: disjoint pool vs FEC namespaces must fail canonical X2 gates."""
    pool_digest = canonical_evidence_set_digest(["bul_unify_001"])
    fec_digest = canonical_evidence_set_digest(["fact_revenue_ops_001"])
    runtime_payload = {
        "allowed_fact_ids": ["fact_revenue_ops_001"],
        "canonical_evidence_set_digest": pool_digest,
        "fec_allowed_fact_ids_digest": fec_digest,
        "canonical_section_evidence_set": {
            "pool_ids_ordered": ["bul_unify_001"],
            "canonical_evidence_set_digest": pool_digest,
            "id_alias_map": {},
        },
        "section_fec_bridge": {
            "allowed_fact_ids": ["fact_revenue_ops_001"],
            "evidence_items": [{"source_fact_id": "fact_revenue_ops_001"}],
        },
    }
    gates: list[X2GateResult] = []
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload=runtime_payload,
        allowed_fact_ids={"fact_revenue_ops_001"},
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["bul_unify_001"]}],
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["X2_BLOCK_ID_NAMESPACE_SPLIT"].pass_ is False
    assert by_id["x2_active_pool_digest_matches_fec_digest"].pass_ is False
    assert by_id["x2_claim_ledger_source_fact_ids_subset_of_fec"].pass_ is False
