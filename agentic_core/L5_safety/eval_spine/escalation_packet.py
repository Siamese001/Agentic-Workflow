"""EscalationPacket dataclass + factory (ADR-036 escalate_hitl path).

Mirrors ``config/schemas/escalation_packet.schema.json``. Produced by §5
whenever disposition==escalate_hitl.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal, Mapping

try:
    import jsonschema  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    jsonschema = None  # type: ignore[assignment]

from agentic_core.L5_safety.eval_spine.exit_decision import ExitDecision, SeverityBand
from agentic_core.L5_safety.exit_control.hitl_classes import (
    CLASS_NAMES,
    HitlClass,
)

_SCHEMA_PATH = Path("config/schemas/escalation_packet.schema.json")

EvidenceKind = Literal[
    "trace_span",
    "artifact",
    "rubric_report",
    "policy_diff",
    "tool_output",
    "trajectory",
    "exit_decision",
    "other",
]

FallbackDirective = Literal["abstain", "clarify", "safe_default", "deny", "hold"]


@dataclass(frozen=True)
class EvidenceRef:
    kind: EvidenceKind
    ref: str
    summary: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"kind": self.kind, "ref": self.ref}
        if self.summary is not None:
            out["summary"] = self.summary
        return out


@dataclass(frozen=True)
class OptionLedgerEntry:
    label: str
    description: str
    recommendation: Literal["recommended", "alternative", "fallback"]
    confidence_0_1: float
    reversibility: Literal["read", "action", "write"] | None = None
    side_effects: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "label": self.label,
            "description": self.description,
            "recommendation": self.recommendation,
            "confidence_0_1": self.confidence_0_1,
        }
        if self.reversibility is not None:
            out["reversibility"] = self.reversibility
        if self.side_effects:
            out["side_effects"] = list(self.side_effects)
        return out


@dataclass(frozen=True)
class BlastRadius:
    scope: Literal["self", "session", "tenant", "fleet"]
    affected_count: int | None = None
    write_surfaces: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"scope": self.scope}
        if self.affected_count is not None:
            out["affected_count"] = self.affected_count
        if self.write_surfaces:
            out["write_surfaces"] = list(self.write_surfaces)
        return out


@dataclass(frozen=True)
class ResumptionContract:
    reentry_layer: Literal["L0", "L1", "L2", "L3", "L5_exit"]
    must_revalidate: bool
    binds_budget: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "reentry_layer": self.reentry_layer,
            "must_revalidate": self.must_revalidate,
            "binds_budget": self.binds_budget,
        }


@dataclass(frozen=True)
class EscalationPacket:
    """Bounded packet emitted at §5 for disposition==escalate_hitl."""

    packet_id: str
    request_id: str
    trace_ref: str
    exit_decision_ref: str
    emitted_at_utc: str
    deadline_utc: str
    hitl_class: str
    severity_band: SeverityBand
    reason_code: str
    reason_detail: str
    evidence_refs: tuple[EvidenceRef, ...]
    options_ledger: tuple[OptionLedgerEntry, ...]
    approver_pool: str
    fallback_directive: FallbackDirective
    policy_snapshot: str

    schema_version: int = 1
    session_id: str | None = None
    tenant: str | None = None
    confidence_0_1: float | None = None
    novelty_0_1: float | None = None
    blast_radius: BlastRadius | None = None
    approver_scope: str | None = None
    resumption_contract: ResumptionContract | None = None

    def __post_init__(self) -> None:
        if self.hitl_class not in CLASS_NAMES:
            raise ValueError(f"hitl_class {self.hitl_class!r} not in canonical HitlClass enum")
        if not self.evidence_refs:
            raise ValueError("evidence_refs must contain at least one entry")
        if not self.options_ledger:
            raise ValueError("options_ledger must contain at least one entry")

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "schema_version": self.schema_version,
            "packet_id": self.packet_id,
            "request_id": self.request_id,
            "trace_ref": self.trace_ref,
            "exit_decision_ref": self.exit_decision_ref,
            "emitted_at_utc": self.emitted_at_utc,
            "deadline_utc": self.deadline_utc,
            "hitl_class": self.hitl_class,
            "severity_band": self.severity_band,
            "reason_code": self.reason_code,
            "reason_detail": self.reason_detail,
            "evidence_refs": [ref.as_dict() for ref in self.evidence_refs],
            "options_ledger": [entry.as_dict() for entry in self.options_ledger],
            "approver_pool": self.approver_pool,
            "fallback_directive": self.fallback_directive,
            "policy_snapshot": self.policy_snapshot,
        }
        if self.session_id is not None:
            out["session_id"] = self.session_id
        if self.tenant is not None:
            out["tenant"] = self.tenant
        if self.confidence_0_1 is not None:
            out["confidence_0_1"] = self.confidence_0_1
        if self.novelty_0_1 is not None:
            out["novelty_0_1"] = self.novelty_0_1
        if self.blast_radius is not None:
            out["blast_radius"] = self.blast_radius.as_dict()
        if self.approver_scope is not None:
            out["approver_scope"] = self.approver_scope
        if self.resumption_contract is not None:
            out["resumption_contract"] = self.resumption_contract.as_dict()
        return out

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def from_exit_decision(
    decision: ExitDecision,
    *,
    hitl_class: str | HitlClass,
    reason_detail: str,
    evidence_refs: tuple[EvidenceRef, ...],
    options_ledger: tuple[OptionLedgerEntry, ...],
    approver_pool: str,
    fallback_directive: FallbackDirective,
    deadline_seconds: int,
    policy_snapshot: str | None = None,
    packet_id: str | None = None,
    confidence_0_1: float | None = None,
    novelty_0_1: float | None = None,
    blast_radius: BlastRadius | None = None,
    resumption_contract: ResumptionContract | None = None,
) -> EscalationPacket:
    """Mint an EscalationPacket from an ExitDecision.

    The caller is responsible for obtaining the policy snapshot if the
    decision did not carry one; a ValueError is raised when neither source
    has a snapshot (ADR-023 §3.6 requires the audit bind).
    """
    class_name = hitl_class.value if isinstance(hitl_class, HitlClass) else hitl_class
    snapshot = policy_snapshot or decision.policy_snapshot
    if not snapshot:
        raise ValueError("policy_snapshot missing — required for escalation audit binding (ADR-023)")
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(seconds=max(0, deadline_seconds))
    return EscalationPacket(
        packet_id=packet_id or f"esc-{uuid.uuid4().hex}",
        request_id=decision.request_id,
        trace_ref=decision.trace_id,
        exit_decision_ref=decision.request_id,
        emitted_at_utc=now.isoformat().replace("+00:00", "Z"),
        deadline_utc=deadline.isoformat().replace("+00:00", "Z"),
        hitl_class=class_name,
        severity_band=decision.safety.severity_band or "medium",
        reason_code=decision.reason_code,
        reason_detail=reason_detail,
        evidence_refs=evidence_refs,
        options_ledger=options_ledger,
        approver_pool=approver_pool,
        fallback_directive=fallback_directive,
        policy_snapshot=snapshot,
        session_id=decision.session_id,
        tenant=decision.tenant,
        confidence_0_1=confidence_0_1,
        novelty_0_1=novelty_0_1,
        blast_radius=blast_radius,
        resumption_contract=resumption_contract,
    )


def validate_dict(payload: Mapping[str, Any], *, schema_path: Path | None = None) -> list[str]:
    path = schema_path or _SCHEMA_PATH
    if not path.exists():
        return [f"schema_not_found:{path}"]
    with path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    if jsonschema is not None:
        try:
            validator = jsonschema.Draft202012Validator(schema)
            return [error.message for error in validator.iter_errors(payload)]
        except jsonschema.SchemaError as exc:  # pragma: no cover
            return [f"schema_error:{exc.message}"]
    required = schema.get("required", [])
    return [f"missing_required:{key}" for key in required if key not in payload]


__all__ = [
    "BlastRadius",
    "EscalationPacket",
    "EvidenceKind",
    "EvidenceRef",
    "FallbackDirective",
    "OptionLedgerEntry",
    "ResumptionContract",
    "from_exit_decision",
    "validate_dict",
]
