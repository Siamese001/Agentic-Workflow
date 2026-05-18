"""L6 shadow handoff for unify_bullets (includes bullet rewrite envelope).

Post-runtime shadow learning overlay: merges future-run-only attestations onto the generic
``build_l6_shadow_handoff_dict`` packet. Must not mutate X2/X3 or rescue the current run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.shadow.l6_handoff_packet import build_l6_shadow_handoff_dict, repo_rel
from apps_rg.runtime.validators.unify_bullets_x2 import TEXT_COVERAGE_INTEGRITY_GATE_ID

SECTION_ID = "unify_bullets"
CLAIM_TEXT_GATE_ID = "x2_claim_ledger_claim_text_non_empty"


def _ref_if(repo_root: Path, artifact_dir: Path, filename: str) -> str | None:
    path = artifact_dir / filename
    return repo_rel(repo_root, path.resolve()) if path.is_file() else None


def extend_unify_bullets_l6_learning_fields(
    base: dict[str, Any],
    *,
    artifact_dir: Path,
    repo_root: Path,
    provider: str,
    x2_gates: list[dict[str, Any]],
    x3_code: str,
    proof_bundle: dict[str, Any],
) -> dict[str, Any]:
    """Append canonical learning-metadata fields required for unify_bullets parity (offline only).

    Intended only after ``x3_disposition.json`` is written for this run.
    """
    ad = artifact_dir.resolve()
    rr = repo_root.resolve()
    failed = [str(g.get("gate_id", "")) for g in x2_gates if not g.get("pass")]
    ct_row = next((g for g in x2_gates if g.get("gate_id") == CLAIM_TEXT_GATE_ID), {})
    integrity_row = next((g for g in x2_gates if g.get("gate_id") == TEXT_COVERAGE_INTEGRITY_GATE_ID), {})

    overlay: dict[str, Any] = {
        "provider": provider,
        "source_run_dir": repo_rel(rr, ad),
        "x3_code": x3_code,
        "x3_disposition_ref": _ref_if(rr, ad, "x3_disposition.json"),
        "x2_gate_outputs_ref": _ref_if(rr, ad, "x2_gate_outputs.json"),
        "x2_failed_gates": failed,
        "claim_text_gate_id": CLAIM_TEXT_GATE_ID,
        "claim_text_gate_result": bool(ct_row.get("pass")),
        "text_claim_coverage_integrity_gate_id": TEXT_COVERAGE_INTEGRITY_GATE_ID,
        "text_claim_coverage_integrity_gate_pass": bool(integrity_row.get("pass")),
        "canonical_claim_ledger_ref": _ref_if(rr, ad, "canonical_claim_ledger_v2.json"),
        "text_claim_coverage_ref": _ref_if(rr, ad, "text_claim_coverage.json"),
        "parsed_output_ref": _ref_if(rr, ad, "parsed_output.json"),
        "compiled_prompt_artifact_ref": _ref_if(rr, ad, "compiled_prompt_artifact.json"),
        "provider_request_ref": _ref_if(rr, ad, "provider_request.json"),
        "provider_response_ref": _ref_if(rr, ad, "provider_response.json"),
        "proof_eligible": proof_bundle["proof_eligible"],
        "judge_proof_eligible": proof_bundle["judge_proof_eligible"],
        "offline_only": True,
        "human_label_required": True,
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
    "SECTION_ID",
    "build_l6_shadow_package",
    "extend_unify_bullets_l6_learning_fields",
]
