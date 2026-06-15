"""apps_lic 5x4 eval lane matrix (the apps_rg "11/11" analog) — W4.

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (W4.1 + W4.2).

Evaluates every (message_type x recipient_class) lane deterministically through
the live C0.3 path — governed ingestion -> recipient-class derivation ->
message-requirement gate -> sender-proof packet (W2 apps_rg-grounded provenance +
W3 recipient-fit weighting) — and renders a 20-cell pass/fail matrix.

Each cell is evaluated INDEPENDENTLY: a BLOCKED lane never suppresses another
(W4.2, no all-or-nothing — mirrors campaign_batch_policy abort_on_first_failure
= false). This harness is offline/deterministic (no LLM, no Redis): it uses
proof-packet readiness + message-gate pass + grounded provenance as the quality
proxy. Live X1D judge verdicts are an optional augmentation, not required here.

Usage:
    python tools/apps_lic/eval_lane_matrix.py            # write artifacts + print
    python tools/apps_lic/eval_lane_matrix.py --json     # print JSON only
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_lic.engines.governed_opportunity_ingestion import (
    WRITE_AUTHORITY_GOVERNED_INGESTION,
    InMemoryOpportunityFactStore,
    OpportunityIngestionInput,
    run_governed_opportunity_ingestion,
)
from apps_lic.engines.message_type_requirement_gate import (
    MESSAGE_FOLLOW_UP,
    MESSAGE_GENERAL_INTRO,
    MESSAGE_REFERRAL_ASK,
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
    STATUS_REQUIREMENTS_PASS,
    evaluate_message_requirements_from_store,
)
from apps_lic.engines.recipient_classification import derive_recipient_class_from_store
from apps_lic.engines.sender_proof_graph import (
    STATUS_PROOF_GRAPH_READY,
    build_sender_proof_graph_packet_from_store,
)
from apps_lic.integrations.apps_rg_proof_bridge import (
    load_apps_rg_proof_index,
    recipient_fit_weight,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "apps_lic"

# 5 message types x 4 recipient classes = 20 lanes.
MESSAGE_TYPES: tuple[str, ...] = (
    MESSAGE_GENERAL_INTRO,
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
    MESSAGE_REFERRAL_ASK,
    MESSAGE_FOLLOW_UP,
)
# Title chosen to derive the intended recipient class (recipient_classification).
RECIPIENT_TITLES: dict[str, str] = {
    "RECRUITER": "Senior Technical Recruiter",
    "SENIOR_TA": "Head of Talent Acquisition",
    "EXECUTIVE": "Executive Vice President",
    "C_LEVEL": "Chief Digital Officer",
}

DISPOSITION_READY = "READY"
DISPOSITION_BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class LaneResult:
    message_type: str
    intended_recipient_class: str
    derived_recipient_class: str
    disposition: str
    message_gate_pass: bool
    proof_ready: bool
    proof_count: int
    grounded_provenance_count: int
    recipient_fit_weight: float
    blocking_reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_type": self.message_type,
            "intended_recipient_class": self.intended_recipient_class,
            "derived_recipient_class": self.derived_recipient_class,
            "disposition": self.disposition,
            "message_gate_pass": self.message_gate_pass,
            "proof_ready": self.proof_ready,
            "proof_count": self.proof_count,
            "grounded_provenance_count": self.grounded_provenance_count,
            "recipient_fit_weight": self.recipient_fit_weight,
            "blocking_reasons": list(self.blocking_reasons),
        }


@dataclass
class MatrixReport:
    ssot_available: bool
    graph_version: str
    cells: list[LaneResult] = field(default_factory=list)

    @property
    def ready_count(self) -> int:
        return sum(1 for c in self.cells if c.disposition == DISPOSITION_READY)

    @property
    def blocked_count(self) -> int:
        return sum(1 for c in self.cells if c.disposition == DISPOSITION_BLOCKED)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_lic.eval_lane_matrix.v1",
            "ssot_available": self.ssot_available,
            "graph_version": self.graph_version,
            "total_cells": len(self.cells),
            "ready_count": self.ready_count,
            "blocked_count": self.blocked_count,
            "cells": [c.to_dict() for c in self.cells],
        }


def _build_store(title: str) -> InMemoryOpportunityFactStore:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id=f"req-matrix-{title}",
        trace_root="trace-matrix",
        idempotency_key=f"idem-matrix-{title}",
        contact={
            "name": "Jane Target",
            "title": title,
            "headline": title,
            "company": "AIG",
            "linkedin_url": "https://www.linkedin.com/in/jane-target",
        },
        company={"company": "AIG", "context": "Regulated insurer expanding agentic AI governance."},
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production agentic AI platforms for regulated workflows.",
        },
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
        role_ownership=None,
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    return store


def _evaluate_cell(*, message_type: str, intended_class: str, title: str) -> LaneResult:
    store = _build_store(title)
    derivation = derive_recipient_class_from_store(store)
    gate = evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=derivation,
        message_type_hint=message_type,
        intent_text="Regulated agentic AI platform leadership and resume review.",
    )
    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Concise outreach about AIG agentic AI platform work.",
        company_context="AIG regulated insurance AI platform work.",
        desired_next_step="resume review",
    )
    message_pass = gate.status == STATUS_REQUIREMENTS_PASS
    proof_ready = packet.status == STATUS_PROOF_GRAPH_READY and packet.ready
    grounded = sum(
        1 for prov in packet.apps_rg_provenance.values() if prov.get("ssot_grounded")
    )
    best_fit = 0.0
    for point in packet.selected_proof_points:
        fit = recipient_fit_weight(
            apps_rg_skill_ids=getattr(point, "apps_rg_skill_ids", ()),
            recipient_class=derivation.derived_recipient_class,
        )
        best_fit = max(best_fit, float(fit["weight"]))
    disposition = DISPOSITION_READY if (message_pass and proof_ready) else DISPOSITION_BLOCKED
    reasons: tuple[str, ...] = ()
    if disposition == DISPOSITION_BLOCKED:
        reasons = tuple(
            dict.fromkeys(
                (
                    *(() if message_pass else tuple(gate.missing_fields)),
                    *(() if proof_ready else tuple(packet.reason_codes)),
                )
            )
        )
    return LaneResult(
        message_type=message_type,
        intended_recipient_class=intended_class,
        derived_recipient_class=derivation.derived_recipient_class,
        disposition=disposition,
        message_gate_pass=message_pass,
        proof_ready=proof_ready,
        proof_count=len(packet.selected_proof_points),
        grounded_provenance_count=grounded,
        recipient_fit_weight=round(best_fit, 4),
        blocking_reasons=reasons,
    )


def evaluate_lane_matrix(*, progress: bool = False) -> MatrixReport:
    """Evaluate all 20 lanes independently (no all-or-nothing)."""
    index = load_apps_rg_proof_index()
    report = MatrixReport(ssot_available=index.available, graph_version=index.graph_version)
    total = len(MESSAGE_TYPES) * len(RECIPIENT_TITLES)
    done = 0
    for message_type in MESSAGE_TYPES:
        for recipient_class, title in RECIPIENT_TITLES.items():
            # Each cell is isolated: a failure in one never aborts the sweep.
            try:
                cell = _evaluate_cell(
                    message_type=message_type,
                    intended_class=recipient_class,
                    title=title,
                )
            except Exception as exc:  # guardian: allow-broad-exception -- matrix isolates per-cell failures so one bad lane never fails the whole sweep
                cell = LaneResult(
                    message_type=message_type,
                    intended_recipient_class=recipient_class,
                    derived_recipient_class="",
                    disposition=DISPOSITION_BLOCKED,
                    message_gate_pass=False,
                    proof_ready=False,
                    proof_count=0,
                    grounded_provenance_count=0,
                    recipient_fit_weight=0.0,
                    blocking_reasons=(f"cell_error:{type(exc).__name__}",),
                )
            report.cells.append(cell)
            done += 1
            if progress:
                print(f"[eval_lane_matrix] {done}/{total} {message_type}/{recipient_class} -> {cell.disposition}")
    return report


def render_markdown(report: MatrixReport) -> str:
    classes = list(RECIPIENT_TITLES.keys())
    by_key = {(c.message_type, c.intended_recipient_class): c for c in report.cells}
    lines: list[str] = []
    lines.append("# apps_lic Eval Lane Matrix (5x4)")
    lines.append("")
    lines.append(
        f"- SSOT available: **{report.ssot_available}** (apps_rg graph `{report.graph_version}`)"
    )
    lines.append(
        f"- Lanes READY: **{report.ready_count}/{len(report.cells)}** · BLOCKED: **{report.blocked_count}** "
        "(each lane evaluated independently — no all-or-nothing)"
    )
    lines.append("")
    header = "| message_type \\ recipient | " + " | ".join(classes) + " |"
    sep = "|" + "---|" * (len(classes) + 1)
    lines.append(header)
    lines.append(sep)
    for message_type in MESSAGE_TYPES:
        row = [message_type]
        for cls in classes:
            cell = by_key.get((message_type, cls))
            if cell is None:
                row.append("—")
            elif cell.disposition == DISPOSITION_READY:
                row.append(f"✅ {cell.proof_count}p/{cell.grounded_provenance_count}g")
            else:
                row.append("⛔")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("## Blocked lanes (per-cell reasons)")
    for cell in report.cells:
        if cell.disposition == DISPOSITION_BLOCKED:
            lines.append(
                f"- {cell.message_type} / {cell.intended_recipient_class} "
                f"(derived={cell.derived_recipient_class or 'n/a'}): "
                f"{', '.join(cell.blocking_reasons) or 'unspecified'}"
            )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="apps_lic 5x4 eval lane matrix")
    parser.add_argument("--json", action="store_true", help="print JSON only")
    args = parser.parse_args(argv)

    report = evaluate_lane_matrix(progress=not args.json)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return 0

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = ARTIFACT_DIR / "eval_lane_matrix.md"
    json_path = ARTIFACT_DIR / "eval_lane_matrix.json"
    md_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    print(render_markdown(report))
    print(f"\nWrote {md_path}")
    print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
