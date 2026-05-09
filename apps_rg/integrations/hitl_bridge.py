"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/integrations\hitl_bridge.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations\hitl_bridge is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/integrations\hitl_bridge.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """W6.P3 — apps_rg HITL bridge to agentic_core L5 HITLApprovalGate.
# 
# Plan: apps-rg-runtime-cert-hardening-a3f8c2.md
# Phase: W6.P3 (supersedes W1.P1 advisory mark_stage fix)
# 
# Bridges apps_rg's `run_report.status='HUMAN_REVIEW'` signal into the
# canonical `HITLApprovalGate` (G06) at agentic_core/L5_safety/runtime_gates/
# so the gate returns a structured GateDecision instead of advisory JSON.
# 
# For W6 skeleton (AG-RG-012 deferred until user decision), the bridge:
# 1. Detects HUMAN_REVIEW status in run_report.json
# 2. Constructs a GateContext with hitl.review_requested=True
# 3. Invokes HITLApprovalGate.evaluate(ctx)
# 4. Returns the structured GateDecision (disposition + alias + reason_codes)
# 
# The actual blocking behavior (CLI stdin-pause vs fail-closed vs async-callback)
# is deferred to AG-RG-012 resolution. This module provides the wiring only.
# """
# from __future__ import annotations
# 
# import json
# import logging
# from pathlib import Path
# from typing import Any
# 
# from agentic_core.L5_safety.runtime_gates.g06_hitl_approval import HITLApprovalGate
# from agentic_core.L5_safety.runtime_gates.types import GateContext, GateDecision
# 
# _log = logging.getLogger(__name__)
# 
# 
# def read_run_report(run_dir: Path) -> dict[str, Any] | None:
#     """Read run_report.json from a run directory (fail-soft)."""
#     report_path = run_dir / "run_report.json"
#     if not report_path.exists():
#         return None
#     try:
#         return json.loads(report_path.read_text(encoding="utf-8"))
#     except Exception:  # noqa: BLE001
#         # guardian: allow-broad-except -- HITL bridge must be fail-soft;
#         # any parse error leaves the gate as no-op so cert bundle is unaffected
#         _log.warning("[hitl_bridge] Failed to parse run_report.json at %s", report_path)
#         return None
# 
# 
# def build_hitl_context(
#     run_report: dict[str, Any],
#     *,
#     replay_key: str | None = None,
# ) -> GateContext:
#     """Construct a GateContext from a run_report for HITLApprovalGate.evaluate.
# 
#     W6.P3 wiring: translates apps_rg's run_report into the canonical
#     GateContext.hitl dict shape expected by G06.
# 
#     Args:
#         run_report: Parsed run_report.json contents.
#         replay_key: W4 adapter replay_key for reclearance audit binding.
# 
#     Returns:
#         GateContext with hitl.review_requested=True iff status=HUMAN_REVIEW.
#     """
#     ctx = GateContext()
# 
#     status = run_report.get("status")
#     provenance = run_report.get("provenance_report", {})
# 
#     if status == "HUMAN_REVIEW":
#         ctx.hitl = {
#             "review_requested": True,
#             "verdict": "pending",  # HITL not yet answered
#             "latency_ms": 0.0,
#             "reason": provenance.get("reason", "human_review_requested"),
#             "replay_key": replay_key or "",
#             "source": "apps_rg.run_report",
#         }
#     else:
#         ctx.hitl = {"review_requested": False}
# 
#     return ctx
# 
# 
# def evaluate_hitl(
#     run_dir: Path,
#     *,
#     replay_key: str | None = None,
# ) -> GateDecision | None:
#     """Run HITLApprovalGate.evaluate against a sealed apps_rg run.
# 
#     Args:
#         run_dir: Path to artifacts/apps_rg/runs/<timestamp>/.
#         replay_key: W4 adapter replay_key for reclearance audit binding.
# 
#     Returns:
#         GateDecision if run_report.json was readable, None otherwise.
#         Caller inspects decision.disposition + decision.alias to act.
#     """
#     run_report = read_run_report(run_dir)
#     if run_report is None:
#         _log.info("[hitl_bridge] No run_report.json - skipping HITL evaluation")
#         return None
# 
#     ctx = build_hitl_context(run_report, replay_key=replay_key)
#     gate = HITLApprovalGate()
#     decision = gate.evaluate(ctx)
# 
#     _log.info(
#         "[hitl_bridge] HITLApprovalGate decision: disposition=%s alias=%s reasons=%s",
#         decision.disposition.value if hasattr(decision.disposition, "value") else decision.disposition,
#         decision.alias,
#         decision.reason_codes,
#     )
#     return decision
# 
# 
# __all__ = [
#     "read_run_report",
#     "build_hitl_context",
#     "evaluate_hitl",
# ]
# 