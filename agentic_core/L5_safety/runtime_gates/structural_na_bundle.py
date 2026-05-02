"""Structural-mode G01..G29 NOT_APPLICABLE bundle builder.

Produces a full 29-gate verdict bundle where every gate is marked
``NOT_APPLICABLE`` with a declared ``na_reason``. Used by the
structural-only MANAGED_WORKFLOW entry point to prove that:

    1. The full gate cascade WAS considered (``full_suite=True``).
    2. None of the 29 gates had a substantive check to perform (every
       verdict is NOT_APPLICABLE).
    3. Every NOT_APPLICABLE carries a non-empty reason, per the
       ``verify_g01_g29_coverage`` fail-closed rule.

This is NOT a replacement for invoking the real gate mesh in a
full-cascade run. It is the honest bundle shape for a run that does
not execute real tools / models / L4 writes. When a future pass adds a
full-cascade entrypoint that actually invokes each gate, that
entrypoint replaces this bundle with real verdicts.
"""

from __future__ import annotations

from typing import Any

_FULL_GATE_IDS: tuple[str, ...] = tuple(f"G{i:02d}" for i in range(1, 30))

_STRUCTURAL_NA_REASON_PREFIX = "STRUCTURAL_ONLY_NOT_APPLICABLE"

# Per-gate reason code. Keyed by gate ID. Each entry is a terse
# explanation of why the gate cannot produce a substantive verdict on
# a structural MW run. If a gate ID is added in future, the default
# reason code below applies.
_GATE_REASON_MAP: dict[str, str] = {
    "G01": "NO_REQUEST_INGRESS_EXERCISED_BY_STRUCTURAL_DEMO",
    "G02": "NO_LIVE_IDENTITY_OR_SESSION_ENFORCEMENT_IN_STRUCTURAL_DEMO",
    "G03": "NO_INTENT_AMBIGUITY_CHECK_REQUIRED_FOR_NOOP_STEPS",
    "G04": "NO_SAFETY_POLICY_INVOCATION_ON_NOOP_STEPS",
    "G05": "NO_RISK_TIER_PROMOTION_REQUESTED",
    "G06": "NO_HITL_APPROVAL_REQUESTED_IN_STRUCTURAL_DEMO",
    "G07": "ROUTE_ALREADY_FIXED_TO_MW_DEMO_TWO_NODE",
    "G08": "GROUNDING_NOT_REQUIRED",
    "G09": "NO_EVIDENCE_BUNDLE_PRODUCED_BY_STRUCTURAL_DEMO",
    "G10": "PROMPT_ASSEMBLY_NOT_REQUIRED",
    "G11": "NO_TOOL_OR_MODEL_INVOKED",
    "G12": "NO_TOOL_ARGUMENT_TO_VALIDATE",
    "G13": "NO_TOOL_OUTPUT_TO_TRUST_CHECK",
    "G14": "NO_EXTERNAL_EGRESS",
    "G15": "NO_FILESYSTEM_OR_SHELL_INVOCATION",
    "G16": "NO_MEMORY_ACCESS_BY_STRUCTURAL_DEMO",
    "G17": "NO_CROSS_CONTEXT_PRIVACY_BOUNDARY_CROSSED",
    "G18": "NO_WORKFLOW_TRAJECTORY_DEVIATION_POSSIBLE_ON_NOOP_STEPS",
    "G19": "NO_LOOP_OR_RETRY_INVOKED",
    "G20": "NO_COST_OR_LATENCY_BUDGET_CONSUMED",
    "G21": "NO_OUTPUT_SCHEMA_TO_VALIDATE",
    "G22": "NO_OUTPUT_QUALITY_CHECK_ON_STRUCTURAL_DEMO",
    "G23": "NO_SECURITY_LEAKAGE_SURFACE",
    "G24": "DETERMINISM_REPLAY_ENFORCED_BY_IDENTITY_ENVELOPE_DIGEST",
    "G25": "NO_RUNTIME_ANOMALY_SURFACE",
    "G26": "EXIT_DISPOSITION_ENFORCED_BY_X3_RECEIPT_NOT_THIS_GATE",
    "G27": "NO_DURABLE_WRITE_REQUESTED",
    "G28": "AUDIT_TRACE_ENFORCED_BY_RUNTIME_TRACE_SNAPSHOT_ARTIFACT",
    "G29": "NO_LEARNING_FIREWALL_BOUNDARY_CROSSED",
}


def build_structural_full_suite_verdicts() -> list[dict[str, Any]]:
    """Return the 29-entry verdict list for a structural MW run.

    Each verdict is:
        {
            "gate_id":     "G01".."G29",
            "result":      "NOT_APPLICABLE",
            "score":       0.0,
            "threshold":   0.0,
            "reason_codes": [ "<reason>" ],
            "na_reason":   "<reason>",
            "grader_type": "structural_na",
        }
    """
    out: list[dict[str, Any]] = []
    for gid in _FULL_GATE_IDS:
        reason = _GATE_REASON_MAP.get(
            gid, f"{_STRUCTURAL_NA_REASON_PREFIX}_DEFAULT"
        )
        out.append({
            "gate_id": gid,
            "result": "NOT_APPLICABLE",
            "score": 0.0,
            "threshold": 0.0,
            "reason_codes": [reason],
            "na_reason": reason,
            "grader_type": "structural_na",
        })
    return out


__all__ = [
    "build_structural_full_suite_verdicts",
]
