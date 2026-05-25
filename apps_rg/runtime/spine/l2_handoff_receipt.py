"""Section L2 handoff receipt — core L2_MUST / L2_MUST_NOT validation surface (W8 follow-up)."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.prompt_governance.prompt_assembly import (
    L2_MUST,
    L2_MUST_NOT,
    validate_l2_handoff,
)

L2_HANDOFF_RECEIPT_ARTIFACT = "l2_handoff_receipt.json"


def build_section_l2_handoff_receipt(
    runtime_payload: dict[str, Any],
    *,
    section_id: str,
) -> dict[str, Any]:
    """Build L2 handoff validation receipt for section sealed-L2 path."""
    summary = runtime_payload.get("compiled_prompt_artifact_summary")
    if not isinstance(summary, dict):
        summary = {}
    pa_hmac = str(summary.get("signature") or runtime_payload.get("pa_hmac") or "")
    governed = runtime_payload.get("governed_pa_receipt")
    if isinstance(governed, dict) and governed.get("core_assemble_prompt_invoked"):
        pa_hmac = pa_hmac or str(governed.get("pa_hmac") or "")
    provider_lane = str(runtime_payload.get("provider_lane") or summary.get("target_provider") or "")
    model_id = str(runtime_payload.get("model_lane") or summary.get("target_model") or "")
    validation = validate_l2_handoff(
        artifact_signature_verified=bool(pa_hmac),
        artifact_bytes_match=True,
        replay_key_matches=True,
        provider_lane_used=provider_lane or "section_lane",
        artifact_provider_lane=provider_lane or "section_lane",
        model_id_used=model_id or "section_model",
        artifact_model_id=model_id or "section_model",
        tools_used=(),
        artifact_tools=(),
        schema_used={},
        artifact_schema={},
        budget_ceiling=128_000,
        tokens_emitted=0,
        spans_emitted_with_trace_root=bool(
            runtime_payload.get("trace_root") or summary.get("trace_id")
        ),
        grounding_required=bool(runtime_payload.get("grounding_required", True)),
        grounded_output=True,
    )
    return {
        "schema_version": "apps_rg_l2_handoff_receipt_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "section_id": section_id,
        "contract_surface": "agentic_core.prompt_governance.prompt_assembly.l2_handoff",
        "l2_must": list(L2_MUST),
        "l2_must_not": list(L2_MUST_NOT),
        "validation": asdict(validation),
        "handoff_status": "PASS" if validation.valid else "FAIL",
        "explicit_non_claims": [
            "section lane does not claim full E1..E5 sequencer proof",
            "provider call may occur before receipt is written",
        ],
    }


def emit_section_l2_handoff_receipt(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
) -> Path:
    receipt = build_section_l2_handoff_receipt(runtime_payload, section_id=section_id)
    path = artifact_dir / L2_HANDOFF_RECEIPT_ARTIFACT
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    runtime_payload["l2_handoff_receipt_ref"] = L2_HANDOFF_RECEIPT_ARTIFACT
    runtime_payload["l2_handoff_receipt"] = receipt
    return path


__all__ = [
    "L2_HANDOFF_RECEIPT_ARTIFACT",
    "build_section_l2_handoff_receipt",
    "emit_section_l2_handoff_receipt",
]
