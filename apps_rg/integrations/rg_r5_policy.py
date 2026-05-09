"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/integrations\rg_r5_policy.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations\rg_r5_policy is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/integrations\rg_r5_policy.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """P13 (W4) — Decision-only R5 policy adapter for apps_rg.
# 
# This module surfaces apps_rg's R5 fallback and terminal conditions as PURE
# DATA — trigger classification, missing-prerequisite description, reentry
# targets, and fallback targets — without executing any code or spawning any
# subprocess.
# 
# The canonical contract:
# - R5 is a DECISION emitted by L0 (DECISION-ONLY layer per spine doctrine).
# - L0 detects a missing prerequisite and calls this policy to classify the
#   trigger and choose the R5 reason code + reentry recommendation.
# - L0 then calls ``_emit_r5_terminal_via_exit`` (apps_rg/__main__.py) which
#   routes the decision through Exit V6 to produce an X3 disposition.
# - The process ONLY exits AFTER the Exit receipt exists.
# 
# This policy MUST NOT:
# - Execute fallback work (no subprocess, no API call, no LLM call).
# - Write to L4 state directly.
# - Override the Exit V6 X3 disposition.
# 
# Usage
# -----
# From ``_emit_r5_terminal_via_exit`` or the R4 entrypoint::
# 
#     from apps_rg.integrations.rg_r5_policy import classify_r5_trigger, R5Decision
# 
#     decision = classify_r5_trigger("BRIEF_MISSING", brief_path="/path/to/brief.json")
#     # decision.reason_code, decision.reentry_recommendation, decision.user_message
# 
# Plan: apps-rg-canonical-wireup-c8a4f2 W4 P13.
# """
# from __future__ import annotations
# 
# from dataclasses import dataclass
# from typing import Any
# 
# # ---------------------------------------------------------------------------
# # R5 trigger codes (canonical vocabulary for apps_rg).
# # These map 1-to-1 to entries in l0_policy.yaml r5_terminal_paths.
# # ---------------------------------------------------------------------------
# BRIEF_MISSING = "BRIEF_MISSING"
# JD_MISSING = "JD_MISSING"
# JD_INVALID = "JD_INVALID"
# PREREQUISITE_TIMEOUT = "PREREQUISITE_TIMEOUT"
# L2_FAULT = "L2_FAULT"
# UNKNOWN = "UNKNOWN"
# 
# _KNOWN_TRIGGERS = frozenset([
#     BRIEF_MISSING,
#     JD_MISSING,
#     JD_INVALID,
#     PREREQUISITE_TIMEOUT,
#     L2_FAULT,
# ])
# 
# 
# @dataclass(frozen=True)
# class R5Decision:
#     """Decision-only output of the R5 policy classifier.
# 
#     Attributes
#     ----------
#     reason_code:
#         Canonical R5 reason code (e.g. ``"BRIEF_MISSING"``).
#     severity:
#         ``"FALLBACK"`` — missing prerequisite, user can retry after fixing.
#         ``"FATAL"`` — unrecoverable (e.g. JD_INVALID, L2_FAULT).
#     reentry_recommendation:
#         Human-readable suggestion for the next step.  Never an automated
#         action — the user decides whether to follow it.
#     fallback_target:
#         The app or module that CAN produce the missing prerequisite, if any.
#         ``None`` if no fallback is applicable.
#     user_message:
#         Short message suitable for ``sys.stderr`` output.
#     context:
#         Free-form dict of additional context (paths, hashes, etc.) for
#         audit and telemetry.  Never contains secrets.
#     """
# 
#     reason_code: str
#     severity: str          # "FALLBACK" | "FATAL"
#     reentry_recommendation: str
#     fallback_target: str | None
#     user_message: str
#     context: dict[str, Any]
# 
# 
# # ---------------------------------------------------------------------------
# # Policy table: trigger → (severity, reentry_recommendation, fallback_target, message)
# # ---------------------------------------------------------------------------
# _POLICY: dict[str, tuple[str, str, str | None, str]] = {
#     BRIEF_MISSING: (
#         "FALLBACK",
#         (
#             "Run `python -m apps_research --target-company <COMPANY>` to generate "
#             "the company brief, then re-run apps_rg with "
#             "`--manual-brief <PATH_TO_BRIEF>`."
#         ),
#         "apps_research",
#         "Company brief not found — R5_FALLBACK terminal.",
#     ),
#     JD_MISSING: (
#         "FATAL",
#         (
#             "Provide a valid JD JSON file via `--jd <PATH>`.  "
#             "The file must exist and be readable JSON."
#         ),
#         None,
#         "Job description file not found — R5_FATAL terminal.",
#     ),
#     JD_INVALID: (
#         "FATAL",
#         (
#             "Fix the JD JSON file to pass U0 E4 schema validation "
#             "(apps_rg/config/jd_schema.json)."
#         ),
#         None,
#         "Job description failed U0 schema validation — R5_FATAL terminal.",
#     ),
#     PREREQUISITE_TIMEOUT: (
#         "FALLBACK",
#         "Re-run apps_rg; if timeout persists, check disk and network access.",
#         None,
#         "Prerequisite check timed out — R5_FALLBACK terminal.",
#     ),
#     L2_FAULT: (
#         "FATAL",
#         (
#             "Inspect the run log at artifacts/apps_rg/runs/<latest>/run_report.json "
#             "for the fault detail, then re-run."
#         ),
#         None,
#         "L2 execution fault — R5_FATAL terminal.",
#     ),
# }
# 
# 
# def classify_r5_trigger(
#     trigger: str,
#     **context: Any,
# ) -> R5Decision:
#     """Classify a trigger string into an R5Decision (decision-only, no side effects).
# 
#     Parameters
#     ----------
#     trigger:
#         One of the known trigger codes (BRIEF_MISSING, JD_MISSING, etc.).
#         Unknown triggers are classified as UNKNOWN / FATAL.
#     **context:
#         Arbitrary key=value pairs forwarded into ``R5Decision.context``.
#         Useful for adding paths, hashes, or other diagnostic data.
# 
#     Returns
#     -------
#     R5Decision
#         Immutable decision record.  The caller is responsible for routing
#         this to Exit V6 via ``_emit_r5_terminal_via_exit``.
#     """
#     if trigger in _POLICY:
#         severity, reentry, fallback, message = _POLICY[trigger]
#     else:
#         severity = "FATAL"
#         reentry = f"Unknown R5 trigger '{trigger}' — inspect logs for root cause."
#         fallback = None
#         message = f"Unknown R5 trigger '{trigger}' — R5_FATAL terminal."
# 
#     return R5Decision(
#         reason_code=trigger,
#         severity=severity,
#         reentry_recommendation=reentry,
#         fallback_target=fallback,
#         user_message=message,
#         context=dict(context),
#     )
# 
# 
# def is_fatal(decision: R5Decision) -> bool:
#     """Return True iff the decision severity is FATAL."""
#     return decision.severity == "FATAL"
# 
# 
# def is_fallback(decision: R5Decision) -> bool:
#     """Return True iff the decision severity is FALLBACK (retry possible)."""
#     return decision.severity == "FALLBACK"
# 
# 
# __all__ = [
#     "BRIEF_MISSING",
#     "JD_MISSING",
#     "JD_INVALID",
#     "PREREQUISITE_TIMEOUT",
#     "L2_FAULT",
#     "UNKNOWN",
#     "R5Decision",
#     "classify_r5_trigger",
#     "is_fatal",
#     "is_fallback",
# ]
# 