"""Optional export profile: 00C.7 mesh verdict → parent REQ-ID summary JSON.

Internal mesh remains authoritative (see ADR-00C-7-gate-verdict-ssot-b8e4f2).
This module is for external auditors and 00X traceability only.
"""

from __future__ import annotations

from typing import Any, Mapping

# Parent 00C §5 (REQ-ID summary) disposition vocabulary.
PARENT_EXPORT_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "ALLOW",
        "DENY",
        "REROUTE_HINT",
        "ESCALATE_HINT",
        "BLOCK_COMMIT",
        "NA",
    }
)

_MESH_TO_PARENT_DISPOSITION: dict[str, str] = {
    "ALLOW": "ALLOW",
    "DENY": "DENY",
    "BLOCK_COMMIT": "BLOCK_COMMIT",
    "REROUTE": "REROUTE_HINT",
    "ESCALATE_HITL": "ESCALATE_HINT",
    "CLARIFY": "ESCALATE_HINT",
    "ABSTAIN": "DENY",
    "SHRINK_SCOPE": "DENY",
    "RETRY": "REROUTE_HINT",
    "HEAL": "REROUTE_HINT",
    "QUARANTINE": "DENY",
    "REDACT": "DENY",
    "SAFE_FALLBACK": "DENY",
    "MARK_DEGRADED": "ALLOW",
    "COMMIT_REQUEST": "ALLOW",
}

_MESH_TO_PARENT_RESULT: dict[str, str] = {
    "PASS": "PASS",
    "FAIL": "FAIL",
    "UNKNOWN": "UNKNOWN",
    "NOT_APPLICABLE": "NOT_APPLICABLE",
    "WARN": "PASS",
}


def export_disposition(mesh_disposition: str) -> str:
    key = (mesh_disposition or "").strip().upper()
    if key in PARENT_EXPORT_DISPOSITIONS:
        return key
    mapped = _MESH_TO_PARENT_DISPOSITION.get(key)
    if mapped is None:
        raise ValueError(f"Cannot map mesh disposition {mesh_disposition!r} to parent export")
    return mapped


def export_result(mesh_result: str) -> str:
    key = (mesh_result or "").strip().upper()
    if key in {"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"}:
        return key
    return _MESH_TO_PARENT_RESULT.get(key, "UNKNOWN")


def gate_verdict_to_parent_export(verdict: Mapping[str, Any]) -> dict[str, Any]:
    """Project a canonical 00C.7 verdict dict to parent §5 export profile."""

    disp = export_disposition(str(verdict.get("disposition", "")))
    result = export_result(str(verdict.get("result", "")))
    severity = str(verdict.get("severity", "INFO")).lower()
    if severity not in {"info", "low", "medium", "high", "critical"}:
        severity = "info"
    out: dict[str, Any] = {
        "gate_id": verdict.get("gate_id"),
        "result": result,
        "disposition": disp,
        "severity": severity,
        "reason_codes": list(verdict.get("reason_codes") or []),
        "score": verdict.get("score"),
        "threshold": verdict.get("threshold"),
        "evidence_refs": list(verdict.get("evidence_refs") or []),
        "replay_refs": list(verdict.get("replay_refs") or []),
        "confidence": verdict.get("confidence", 1.0),
        "abstain_flag": bool(verdict.get("abstain_flag", False)),
        "remediation_hint": verdict.get("remediation_hint"),
        "req_id": verdict.get("req_id") or f"REQ-GATE-{verdict.get('gate_id')}-001",
        "trace_id": verdict.get("trace_id", ""),
        "span_id": verdict.get("span_id", ""),
        "policy_hash": verdict.get("policy_hash", ""),
        "blueprint_hash": verdict.get("blueprint_hash", ""),
        "replay_key": verdict.get("replay_key", ""),
        "export_profile": "00C_parent_reqid_v1",
        "schema_version_source": verdict.get("schema_version", "00C-1.0.0"),
    }
    return out


def export_verdict_bundle(verdicts: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [gate_verdict_to_parent_export(v) for v in verdicts]
