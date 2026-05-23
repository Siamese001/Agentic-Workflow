"""Canonical section-lane X2 gate artifact writer (includes C0 metrics gates)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.bindings.section_lane_c0_metrics import augment_section_x2_gates
from apps_rg.runtime.rigor.convergence_audit import apply_rigor_convergence_to_x2_payload

_CANON_GATE_IDS = frozenset(
    {
        "x2_fec_subset_of_canonical_evidence_pool",
        "x2_prompt_c0_ids_subset_of_fec",
        "x2_claim_ledger_source_fact_ids_subset_of_fec",
        "X2_BLOCK_ID_NAMESPACE_SPLIT",
        "x2_active_pool_digest_matches_fec_digest",
    }
)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_runtime_payload(artifact_dir: Path) -> dict[str, Any] | None:
    rp_path = artifact_dir / "runtime_payload.json"
    if not rp_path.is_file():
        return None
    try:
        raw = json.loads(rp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return raw if isinstance(raw, dict) else None


def _load_claim_ledger(artifact_dir: Path) -> list[dict[str, Any]]:
    cl_path = artifact_dir / "claim_ledger.json"
    if not cl_path.is_file():
        return []
    try:
        cl_raw = json.loads(cl_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if isinstance(cl_raw, list):
        return [r for r in cl_raw if isinstance(r, dict)]
    return []


def _append_canonical_gates(
    augmented: list[dict[str, Any]],
    *,
    artifact_dir: Path,
    section_id: str,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    from apps_rg.runtime.evidence.canonical_evidence_x2 import (
        append_canonical_evidence_invariant_x2_gates,
    )
    from apps_rg.runtime.validators.executive_summary_x2 import X2GateResult

    out = [g for g in augmented if str(g.get("gate_id") or "") not in _CANON_GATE_IDS]
    allowed = {str(x) for x in (payload.get("allowed_fact_ids") or []) if str(x).strip()}
    fresh: list[X2GateResult] = []
    append_canonical_evidence_invariant_x2_gates(
        fresh,
        runtime_payload=payload,
        allowed_fact_ids=allowed,
        claim_ledger=_load_claim_ledger(artifact_dir),
        artifacts_dir=artifact_dir,
    )
    for g in fresh:
        out.append(
            {
                "gate_id": g.gate_id,
                "gate_type": g.gate_type,
                "pass": g.pass_,
                "observed_value": g.observed_value,
                "threshold": g.threshold,
                "failure_reason": g.failure_reason,
                "evidence_ref": g.evidence_ref,
            }
        )
    return out


def write_section_x2_gate_outputs(
    artifact_dir: Path,
    section_id: str,
    gates: list[dict[str, Any]],
    *,
    runtime_payload: dict[str, Any] | None = None,
) -> None:
    """Write ``x2_gate_outputs.json`` with optional C0 metrics gates for grounded lanes."""
    payload = runtime_payload if isinstance(runtime_payload, dict) else _load_runtime_payload(artifact_dir)
    augmented = augment_section_x2_gates(
        gates,
        artifact_dir,
        section_id,
        runtime_payload=payload,
    )
    if isinstance(payload, dict):
        augmented = _append_canonical_gates(
            augmented, artifact_dir=artifact_dir, section_id=section_id, payload=payload
        )
    failed = [g["gate_id"] for g in augmented if not g.get("pass")]
    payload_out = {
        "gates": augmented,
        "failed_gates": failed,
        "x2_passed": sum(1 for g in augmented if g.get("pass")),
        "x2_failed": len(failed),
        "total_x2_gates": len(augmented),
    }
    payload_out = apply_rigor_convergence_to_x2_payload(
        payload_out,
        lane=section_id,
        gates=augmented,
        c0_sidecar=True,
    )
    write_json(artifact_dir / "x2_gate_outputs.json", payload_out)
    from apps_rg.runtime.evidence.canonical_evidence_digest_chain import (
        emit_canonical_evidence_digest_chain,
    )

    emit_canonical_evidence_digest_chain(artifact_dir, section_id=section_id)
    payload2 = _load_runtime_payload(artifact_dir)
    if isinstance(payload2, dict):
        augmented2 = _append_canonical_gates(
            list(payload_out["gates"]),
            artifact_dir=artifact_dir,
            section_id=section_id,
            payload=payload2,
        )
        failed2 = [g["gate_id"] for g in augmented2 if not g.get("pass")]
        payload_out = apply_rigor_convergence_to_x2_payload(
            {
                "gates": augmented2,
                "failed_gates": failed2,
                "x2_passed": sum(1 for g in augmented2 if g.get("pass")),
                "x2_failed": len(failed2),
                "total_x2_gates": len(augmented2),
            },
            lane=section_id,
            gates=augmented2,
            c0_sidecar=True,
        )
        write_json(artifact_dir / "x2_gate_outputs.json", payload_out)


def write_x2_gate_outputs(path: Path, gates: list[dict[str, Any]]) -> None:
    """Legacy path-only writer (no C0 augmentation — prefer write_section_x2_gate_outputs)."""
    failed = [g["gate_id"] for g in gates if not g.get("pass")]
    write_json(
        path,
        {
            "gates": gates,
            "failed_gates": failed,
            "x2_passed": sum(1 for g in gates if g.get("pass")),
            "x2_failed": len(failed),
            "total_x2_gates": len(gates),
        },
    )


__all__ = ["write_section_x2_gate_outputs", "write_x2_gate_outputs"]
