"""Canonical section-lane X2 gate artifact writer (includes C0 metrics gates)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.bindings.section_lane_c0_metrics import augment_section_x2_gates
from apps_rg.runtime.rigor.convergence_audit import apply_rigor_convergence_to_x2_payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_section_x2_gate_outputs(
    artifact_dir: Path,
    section_id: str,
    gates: list[dict[str, Any]],
    *,
    runtime_payload: dict[str, Any] | None = None,
) -> None:
    """Write ``x2_gate_outputs.json`` with optional C0 metrics gates for grounded lanes."""
    payload = runtime_payload
    if payload is None:
        rp_path = artifact_dir / "runtime_payload.json"
        if rp_path.is_file():
            try:
                raw = json.loads(rp_path.read_text(encoding="utf-8"))
                payload = raw if isinstance(raw, dict) else None
            except (json.JSONDecodeError, OSError):  # guardian: allow-pass -- optional payload read
                payload = None
    augmented = augment_section_x2_gates(
        gates,
        artifact_dir,
        section_id,
        runtime_payload=payload,
    )
    failed = [g["gate_id"] for g in augmented if not g.get("pass")]
    payload = {
        "gates": augmented,
        "failed_gates": failed,
        "x2_passed": sum(1 for g in augmented if g.get("pass")),
        "x2_failed": len(failed),
        "total_x2_gates": len(augmented),
    }
    payload = apply_rigor_convergence_to_x2_payload(
        payload,
        lane=section_id,
        gates=augmented,
        c0_sidecar=True,
    )
    write_json(artifact_dir / "x2_gate_outputs.json", payload)


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
