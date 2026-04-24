"""ExitDecision dataclass and schema roundtrip.

Mirrors ``config/schemas/exit_decision.schema.json`` (v33 §5 contract).
``to_dict`` produces schema-valid output; ``validate`` uses jsonschema when
available, falling back to structural checks otherwise.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, Mapping

try:
    import jsonschema  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    jsonschema = None  # type: ignore[assignment]

_SCHEMA_PATH = Path("config/schemas/exit_decision.schema.json")

Disposition = Literal[
    "allow_finish", "deny_reroute", "escalate_hitl", "commit_request"
]
Verdict = Literal["pass", "warn", "fail", "unknown"]
SeverityBand = Literal["info", "low", "medium", "high", "critical"]


def _drop_none(mapping: Mapping[str, Any]) -> dict[str, Any]:
    """Drop None values; preserve explicit nulls only where schema allows."""
    return {k: v for k, v in mapping.items() if v is not None}


@dataclass(frozen=True)
class HallucinationMetric:
    score_0_1: float
    unsupported_claim_count: int
    tool_grounded: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "score_0_1": self.score_0_1,
            "unsupported_claim_count": self.unsupported_claim_count,
            "tool_grounded": self.tool_grounded,
        }


@dataclass(frozen=True)
class FinalResponseMetrics:
    groundedness: float | str = "Unknown"
    answer_relevancy: float | str = "Unknown"
    faithfulness: float | str = "Unknown"
    context_precision: float | str | None = None
    completeness: float | str = "Unknown"
    hallucination: HallucinationMetric = field(
        default_factory=lambda: HallucinationMetric(1.0, 0, True)
    )

    def as_dict(self) -> dict[str, Any]:
        base: dict[str, Any] = {
            "groundedness": self.groundedness,
            "answer_relevancy": self.answer_relevancy,
            "faithfulness": self.faithfulness,
            "completeness": self.completeness,
            "hallucination": self.hallucination.as_dict(),
        }
        if self.context_precision is not None:
            base["context_precision"] = self.context_precision
        return base


@dataclass(frozen=True)
class TrajectoryMetrics:
    failure: bool
    latency_ms: int
    tool_call_count: int
    retry_count: int = 0
    exact_match: int | None = None
    in_order_match: int | None = None
    any_order_match: int | None = None
    precision: float | None = None
    recall: float | None = None
    single_tool_use: Mapping[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "failure": self.failure,
            "latency_ms": self.latency_ms,
            "tool_call_count": self.tool_call_count,
            "retry_count": self.retry_count,
        }
        for key in (
            "exact_match",
            "in_order_match",
            "any_order_match",
            "precision",
            "recall",
            "single_tool_use",
        ):
            value = getattr(self, key)
            if value is not None:
                out[key] = dict(value) if isinstance(value, Mapping) else value
        return out


@dataclass(frozen=True)
class SafetyFlags:
    policy_violation: bool = False
    instruction_violation: bool = False
    policy_halt: bool = False
    violated_rules: tuple[str, ...] = ()
    severity_band: SeverityBand | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "policy_violation": self.policy_violation,
            "instruction_violation": self.instruction_violation,
            "policy_halt": self.policy_halt,
        }
        if self.violated_rules:
            out["violated_rules"] = list(self.violated_rules)
        if self.severity_band is not None:
            out["severity_band"] = self.severity_band
        return out


@dataclass(frozen=True)
class BudgetReport:
    budget_fit: bool
    tokens_envelope: int | None = None
    tokens_consumed: int | None = None
    latency_envelope_ms: int | None = None
    latency_consumed_ms: int | None = None
    tool_calls_envelope: int | None = None
    tool_calls_consumed: int | None = None
    cost_usd_envelope: float | None = None
    cost_usd_consumed: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {"budget_fit": self.budget_fit, **_drop_none(asdict(self))}


@dataclass(frozen=True)
class QualityVerdict:
    verdict: Verdict = "unknown"
    weighted_score_0_1: float | None = None
    confidence_0_1: float | None = None
    unknown_fraction: float | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"verdict": self.verdict}
        for key in ("weighted_score_0_1", "confidence_0_1", "unknown_fraction"):
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        return out


@dataclass(frozen=True)
class OutputContractReport:
    required_form_satisfied: bool
    contract_ref: str | None = None
    violations: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "required_form_satisfied": self.required_form_satisfied,
        }
        if self.contract_ref is not None:
            out["contract_ref"] = self.contract_ref
        if self.violations:
            out["violations"] = list(self.violations)
        return out


@dataclass(frozen=True)
class ExitDecision:
    """Typed output of v33 §5 EXIT EVAL & CONTROL."""

    request_id: str
    trace_id: str
    emitted_at_utc: str
    disposition: Disposition
    reason_code: str
    final_response: FinalResponseMetrics
    trajectory: TrajectoryMetrics
    safety: SafetyFlags
    budget: BudgetReport
    quality: QualityVerdict
    output_contract: OutputContractReport

    schema_version: int = 1
    session_id: str | None = None
    tenant: str | None = None
    agent_class: str | None = None
    agent_version: str | None = None
    reason_detail: str | None = None
    escalation_packet_ref: str | None = None
    uwg_commit_ref: str | None = None
    policy_snapshot: str | None = None
    rubric_version: str | None = None
    judge_calibration_snapshot: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "emitted_at_utc": self.emitted_at_utc,
            "disposition": self.disposition,
            "reason_code": self.reason_code,
            "final_response": self.final_response.as_dict(),
            "trajectory": self.trajectory.as_dict(),
            "safety": self.safety.as_dict(),
            "budget": self.budget.as_dict(),
            "quality": self.quality.as_dict(),
            "output_contract": self.output_contract.as_dict(),
        }
        optional = {
            "session_id": self.session_id,
            "tenant": self.tenant,
            "agent_class": self.agent_class,
            "agent_version": self.agent_version,
            "reason_detail": self.reason_detail,
            "escalation_packet_ref": self.escalation_packet_ref,
            "uwg_commit_ref": self.uwg_commit_ref,
            "policy_snapshot": self.policy_snapshot,
            "rubric_version": self.rubric_version,
            "judge_calibration_snapshot": self.judge_calibration_snapshot,
        }
        out.update(_drop_none(optional))
        return out

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def validate_dict(
    payload: Mapping[str, Any], *, schema_path: Path | None = None
) -> list[str]:
    """Return a list of validation-error strings (empty == valid)."""
    path = schema_path or _SCHEMA_PATH
    if not path.exists():
        return [f"schema_not_found:{path}"]
    with path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    if jsonschema is not None:
        try:
            validator = jsonschema.Draft202012Validator(schema)
            return [error.message for error in validator.iter_errors(payload)]
        except jsonschema.SchemaError as exc:  # pragma: no cover - schema author bug
            return [f"schema_error:{exc.message}"]
    # Structural fallback: only enforce required top-level keys.
    required = schema.get("required", [])
    missing = [key for key in required if key not in payload]
    return [f"missing_required:{key}" for key in missing]


__all__ = [
    "BudgetReport",
    "Disposition",
    "ExitDecision",
    "FinalResponseMetrics",
    "HallucinationMetric",
    "OutputContractReport",
    "QualityVerdict",
    "SafetyFlags",
    "SeverityBand",
    "TrajectoryMetrics",
    "Verdict",
    "validate_dict",
]
