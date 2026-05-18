"""L6 shadow handoff for executive_summary (post-X3; post_runtime attachment)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.shadow.l6_handoff_packet import build_l6_shadow_handoff_dict, repo_rel

SECTION_ID = "executive_summary"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _failed_x2_ids(x2blob: dict[str, Any]) -> list[str]:
    gates = x2blob.get("gates")
    if isinstance(gates, list):
        return [str(g.get("gate_id")) for g in gates if isinstance(g, dict) and g.get("pass") is False]
    fg = x2blob.get("failed_gates")
    if isinstance(fg, list):
        return [str(x) for x in fg]
    return []


def build_l6_shadow_package(
    *,
    artifact_dir: Path,
    repo_root: Path,
    prompt_id: str,
    temperature: float | None,
    max_tokens: int | None,
) -> dict[str, Any]:
    ad = artifact_dir.resolve()
    rr = repo_root.resolve()
    base = build_l6_shadow_handoff_dict(
        artifact_dir=ad,
        repo_root=rr,
        section_id=SECTION_ID,
        prompt_id=prompt_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    x3 = _load_json(ad / "x3_disposition.json")
    x2 = _load_json(ad / "x2_gate_outputs.json")
    failed = _failed_x2_ids(x2)
    exhaust = ad / "runtime_exhaust_bundle.json"
    canon = ad / "canonical_claim_ledger_v2.json"
    tcov = ad / "text_claim_coverage.json"
    rtxt = ad / "resume_display_text.txt"
    post_runtime_fields: dict[str, Any] = {
        "post_runtime_phase": True,
        "consumed_after_x3": True,
        "future_run_signal_only": True,
        "source_runtime_exhaust_bundle_ref": repo_rel(rr, exhaust) if exhaust.is_file() else None,
        "source_x3_disposition_ref": base.get("x3_disposition_ref"),
        "source_x2_gate_outputs_ref": base.get("x2_gate_outputs_ref"),
        "source_canonical_claim_ledger_ref": repo_rel(rr, canon) if canon.is_file() else None,
        "source_text_claim_coverage_ref": repo_rel(rr, tcov) if tcov.is_file() else None,
        "source_resume_display_text_ref": repo_rel(rr, rtxt) if rtxt.is_file() else None,
        "observed_x3_code": x3.get("x3_code"),
        "observed_x2_failed_gates": failed,
        "no_current_run_rescue_assertion": True,
        "no_current_run_mutation_assertion": True,
        "l6_is_runtime_gate": False,
        "l6_can_change_x3": False,
        "x3_changed_by_l6": False,
        "proof_eligible_changed_by_l6": False,
    }
    base.update(post_runtime_fields)
    return base


__all__ = ["build_l6_shadow_package", "SECTION_ID"]
