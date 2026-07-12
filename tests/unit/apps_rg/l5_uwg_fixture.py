"""Shared verified L5 metadata fixtures for apps_rg UWG tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.l5.packet_builder import compute_l5_packet_verification_digest


def verified_l5_exit_metadata(
    *,
    request_id: str,
    run_id: str,
    trace_id: str,
    packet_digest: str = "d" * 64,
    runtime_binding_digest: str = "b" * 64,
) -> dict[str, Any]:
    packet_ref = f"l5_packet:{packet_digest}"
    return {
        "request_id": request_id,
        "run_id": run_id,
        "trace_id": trace_id,
        "l5_certification_packet_ref": packet_ref,
        "l5_certification_packet_digest": packet_digest,
        "l5_certification_status": "L5_CERTIFIED",
        "l5_runtime_binding_digest": runtime_binding_digest,
        "l5_certification_verified": True,
        "l5_certification_verification_digest": compute_l5_packet_verification_digest(
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            packet_ref=packet_ref,
            packet_digest=packet_digest,
            status="L5_CERTIFIED",
            runtime_binding_digest_value=runtime_binding_digest,
        ),
    }


def write_verified_l5_sealed_artifact(
    artifact_dir: Path,
    *,
    request_id: str,
    run_id: str,
    trace_id: str,
) -> dict[str, Any]:
    metadata = verified_l5_exit_metadata(
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "sealed_l2_artifact.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


__all__ = ["verified_l5_exit_metadata", "write_verified_l5_sealed_artifact"]
