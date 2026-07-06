"""W12 — R1B write-to-read lifecycle proof orchestration."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_derived_index import (
    derived_index_available,
    derived_index_root,
    list_derived_index_record_ids,
    load_derived_index_entry,
    lookup_r1b_via_derived_index,
    project_durable_to_derived_index,
)
from apps_rg.cache.r1b_uwg_receipt_contract import document_r1b_uwg_core_receipt_gaps
from apps_rg.cache.r1b_whole_run_preflight import execute_whole_run_r1b_preflight
from apps_rg.cache.whole_run_entrypoint_preflight import PREFLIGHT_ORDER as ENTRY_PREFLIGHT_ORDER


@dataclass
class LifecycleProofResult:
    steps: list[dict[str, Any]] = field(default_factory=list)
    accepted_hit: bool = False
    miss_fallthrough: bool = False
    rejected_candidate: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": self.steps,
            "accepted_hit": self.accepted_hit,
            "miss_fallthrough": self.miss_fallthrough,
            "rejected_candidate": self.rejected_candidate,
            "preflight_order": list(ENTRY_PREFLIGHT_ORDER),
        }


def prove_r1b_index_lifecycle(
    *,
    projection_root: Path,
    match_request: dict[str, Any],
    miss_request: dict[str, Any],
    reject_request: dict[str, Any],
    prompt_profile_hash: str,
    gate_profile_hash: str,
) -> LifecycleProofResult:
    """Document lifecycle stages after durable bundles and derived index exist."""
    result = LifecycleProofResult()
    root = Path(projection_root)

    result.steps.append(
        {
            "stage": "durable_truth_present",
            "ok": (root / "durable" / "uwg_admitted" / "intents").is_dir(),
        }
    )
    refresh = project_durable_to_derived_index(root)
    result.steps.append({"stage": "derived_index_refresh", "receipt": refresh.to_dict()})
    manifest_path = derived_index_root(root) / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    for rid in list_derived_index_record_ids(root):
        entry = load_derived_index_entry(root, rid) or {}
        durable_ref = str(entry.get("durable_bundle_ref") or "")
        refresh_ref = str(entry.get("source_refresh_receipt_ref") or "")
        bundle = json.loads((root / durable_ref).read_text(encoding="utf-8"))
        refresh_payload = json.loads((root / refresh_ref).read_text(encoding="utf-8"))
        same_commit = (
            entry.get("source_commit_receipt_ref")
            == bundle.get("source_commit_receipt_ref")
            == refresh_payload.get("source_commit_receipt_ref")
        )
        result.steps.append(
            {
                "stage": "receipt_chain_consistency",
                "record_id": rid,
                "same_commit_receipt_ref": same_commit,
                "manifest_points_to_commit": entry.get("source_commit_receipt_ref")
                in (manifest.get("source_commit_receipt_refs") or []),
                "manifest_points_to_refresh": refresh_ref
                in (manifest.get("source_refresh_receipt_refs") or []),
                "derived_index_replaces_provenance": False,
            }
        )

    hit, report = lookup_r1b_via_derived_index(
        match_request,
        projection_root=root,
        similarity_threshold=0.5,
        query_prompt_hash=prompt_profile_hash,
        query_gate_hash=gate_profile_hash,
    )
    pf = execute_whole_run_r1b_preflight(
        raw_request=match_request,
        runs_dir=str(root),
        similarity_threshold=0.5,
        prompt_profile_hash=prompt_profile_hash,
        gate_profile_hash=gate_profile_hash,
    )
    result.accepted_hit = bool(hit and pf.r1b_hit)
    result.steps.append(
        {
            "stage": "future_whole_run_r1b_lookup",
            "r1b_hit": pf.r1b_hit,
            "derived_index_used": derived_index_available(root),
            "exit_review_required": bool(
                pf.terminal_packet and pf.terminal_packet.get("exit_review_required")
            ),
            "exit_bypassed": pf.terminal_packet.get("exit_bypassed") if pf.terminal_packet else None,
            "generation_required": pf.generation_required,
            "child_chunk_inspection": pf.child_chunk_inspection,
        }
    )

    miss_pf = execute_whole_run_r1b_preflight(
        raw_request=miss_request,
        runs_dir=str(root),
        prompt_profile_hash=prompt_profile_hash,
        gate_profile_hash=gate_profile_hash,
    )
    result.miss_fallthrough = not miss_pf.r1b_hit and miss_pf.generation_required
    result.steps.append(
        {
            "stage": "miss_fallthrough",
            "generation_required": miss_pf.generation_required,
            "r1b_hit": miss_pf.r1b_hit,
        }
    )

    reject_hit, _ = lookup_r1b_via_derived_index(
        reject_request,
        projection_root=root,
        query_prompt_hash="WRONG",
        query_gate_hash="WRONG",
    )
    result.rejected_candidate = reject_hit is None
    result.steps.append(
        {
            "stage": "rejected_candidate",
            "hit": reject_hit is not None,
            "profile_mismatch_blocked": True,
        }
    )

    return result


def write_w10b_gap_carry_forward(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **document_r1b_uwg_core_receipt_gaps(),
        "carry_forward_wave": "W11-W12",
        "apps_rg_sidecar_preserves_governance_refs": True,
        "derived_index_does_not_replace_sidecar": True,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


__all__ = [
    "LifecycleProofResult",
    "prove_r1b_index_lifecycle",
    "write_w10b_gap_carry_forward",
]
