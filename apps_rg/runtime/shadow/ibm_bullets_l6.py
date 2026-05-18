"""L6 shadow handoff for ibm_bullets (bullet rewrite envelope + future-run-only attestations).

Post-runtime shadow overlay onto ``build_l6_shadow_handoff_dict``. Emitted only after
``x3_disposition.json`` exists. Observer-only: must not mutate X1D/X2/X3 or the current section output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.shadow.l6_handoff_packet import build_l6_shadow_handoff_dict, repo_rel

SECTION_ID = "ibm_bullets"
CLAIM_TEXT_GATE_ID = "x2_claim_ledger_claim_text_non_empty"
FOUNDATION_MODEL_ID = "IBM_BULLETS_FOUNDATION_PROOF_MODEL_V1"


def _x2_gate_pass(gates: list[dict[str, Any]], gate_id: str) -> bool:
    row = next((g for g in gates if g.get("gate_id") == gate_id), {})
    return bool(row.get("pass"))


def _rewrite_counts_shadow(bullets: list[dict[str, Any]] | None) -> dict[str, int]:
    counts = {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    for bullet in bullets or []:
        if not isinstance(bullet, dict):
            continue
        key = str(bullet.get("rewrite_intensity", "")).upper()
        if key in counts:
            counts[key] += 1
    return counts


def _ref_if(repo_root: Path, artifact_dir: Path, filename: str) -> str | None:
    path = artifact_dir / filename
    return repo_rel(repo_root, path.resolve()) if path.is_file() else None


def extend_ibm_bullets_l6_learning_fields(
    base: dict[str, Any],
    *,
    artifact_dir: Path,
    repo_root: Path,
    provider: str,
    x2_gates: list[dict[str, Any]],
    x3_code: str,
    authorization_scope: str,
    mocked_judges: list[str],
    proof_bundle: dict[str, Any],
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str] | frozenset[str],
    bullets: list[dict[str, Any]] | None = None,
    rewrite_distribution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge IBM bullets learning-metadata / observer attestations (offline only).

    Intended only after Exit/X3 artifacts for this run are written.
    """
    ad = artifact_dir.resolve()
    rr = repo_root.resolve()
    failed = [str(g.get("gate_id", "")) for g in x2_gates if not g.get("pass")]
    ct_row = next((g for g in x2_gates if g.get("gate_id") == CLAIM_TEXT_GATE_ID), {})

    roots: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            roots.add(str(fid).split("_metric_")[0])

    unify_overlap: list[str] = []
    if not _x2_gate_pass(x2_gates, "x2_no_unify_fact_leakage"):
        unify_overlap.append("unify_fact_or_scope_signal_failed")
    if not _x2_gate_pass(x2_gates, "x2_no_unify_runtime_terms"):
        unify_overlap.append("unify_runtime_terms_in_display_text_failed")
    if not _x2_gate_pass(x2_gates, "x2_no_agentic_inflation"):
        unify_overlap.append("agentic_token_in_display_text_failed")

    foundation_calibration: dict[str, Any] = {
        "foundation_proof_model_id": FOUNDATION_MODEL_ID,
        "treatment_profile": "REWRITE_FROM_FACT_POOL_CONSTRAINED",
        "rewrite_intensity_distribution_observed": _rewrite_counts_shadow(bullets),
        "rewrite_distribution_declared": dict(rewrite_distribution or {}),
        "taxonomy_label_prefix_gate_pass": _x2_gate_pass(
            x2_gates, "x2_no_taxonomy_label_prefix_in_display_text"
        ),
        "unify_bullet_overlap_risk_notes": unify_overlap,
        "unify_bullet_overlap_risk_level": "none" if not unify_overlap else "elevated",
        "x2_gate_summary": {str(g.get("gate_id")): bool(g.get("pass")) for g in x2_gates},
        "x3_status": x3_code,
    }

    overlay: dict[str, Any] = {
        "provider": provider,
        "source_run_dir": repo_rel(rr, ad),
        "section_run_id": base.get("run_id"),
        "x3_code": x3_code,
        "x3_disposition_ref": _ref_if(rr, ad, "x3_disposition.json"),
        "x2_gate_outputs_ref": _ref_if(rr, ad, "x2_gate_outputs.json"),
        "x2_failed_gates": failed,
        "blocked_failed_unknown_gate_summary": {
            "failed_gate_ids": failed,
            "x2_failed_count": len(failed),
        },
        "claim_text_gate_id": CLAIM_TEXT_GATE_ID,
        "claim_text_gate_result": bool(ct_row.get("pass")),
        "claim_ledger_summary": {
            "row_count": len(claim_ledger),
            "distinct_source_fact_id_roots_sorted": sorted(roots),
            "claim_ledger_ref": _ref_if(rr, ad, "claim_ledger.json"),
        },
        "allowed_fact_ids_summary": {
            "allowed_fact_ids_sorted": sorted(str(x) for x in allowed_fact_ids),
            "count": len(allowed_fact_ids),
            "runtime_payload_ref": _ref_if(rr, ad, "runtime_payload.json"),
        },
        "compiled_prompt_artifact_ref": _ref_if(rr, ad, "compiled_prompt_artifact.json"),
        "compiled_prompt_txt_ref": _ref_if(rr, ad, "compiled_prompt.txt"),
        "provider_request_ref": _ref_if(rr, ad, "provider_request.json"),
        "provider_response_ref": _ref_if(rr, ad, "provider_response.json"),
        "mocked_judges_note": "mocked_judges listed only when present in X3 artifact for this run.",
        "mocked_judges": list(mocked_judges),
        "proof_eligible": proof_bundle["proof_eligible"],
        "proof_scope": proof_bundle.get("proof_scope"),
        "proof_status": proof_bundle.get("proof_status"),
        "provider_proof_eligible": proof_bundle["provider_proof_eligible"],
        "judge_proof_eligible": proof_bundle["judge_proof_eligible"],
        "test_only_mock_judges": proof_bundle.get("test_only_mock_judges"),
        "offline_contract_stub_used": proof_bundle.get("offline_contract_stub_used"),
        "offline_contract_stub_reason": (
            "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB" if proof_bundle.get("offline_contract_stub_used") else None
        ),
        "artifact_namespace_class": proof_bundle.get("artifact_namespace_class"),
        "runtime_generation_status_class": proof_bundle.get("runtime_generation_status_class"),
        "authorization_scope": authorization_scope,
        "no_runtime_approval_authority_assertion": True,
        "no_current_run_mutation_assertion": True,
        "offline_only": True,
        "human_label_required": True,
        "foundation_proof_calibration": foundation_calibration,
        "observer_law_assertion": (
            "L6 shadow observer did not mutate prompts, rubrics, gates, judges, policy, registry, "
            "claim ledger, bullet text, or X1D/X2/X3 disposition for this run."
        ),
        "future_run_only_assertion": True,
        "current_run_mutation_assertion": False,
        "current_run_rescue_assertion": False,
        "durable_write_assertion": False,
        "direct_l4_write_assertion": False,
        "future_run_only": True,
        "learning_promotion_status": "NOT_REQUESTED",
    }

    merged = dict(base)
    merged.update(overlay)
    return merged


def build_l6_shadow_package(
    *,
    artifact_dir: Path,
    repo_root: Path,
    prompt_id: str,
    temperature: float | None,
    max_tokens: int | None,
) -> dict[str, Any]:
    return build_l6_shadow_handoff_dict(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        section_id=SECTION_ID,
        prompt_id=prompt_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )


__all__ = [
    "CLAIM_TEXT_GATE_ID",
    "FOUNDATION_MODEL_ID",
    "SECTION_ID",
    "build_l6_shadow_package",
    "extend_ibm_bullets_l6_learning_fields",
]
