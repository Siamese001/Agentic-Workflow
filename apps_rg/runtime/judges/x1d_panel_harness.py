"""apps_rg-owned multi-provider judge panel harness.

This module mirrors the small app-facing panel contract surface used by the
executive-summary X1D proof path without importing concrete agentic_core judge
internals.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


_REQUIRED_TASK = "GRADE_ONLY"
RECONCILE_POLICY_VERSION = "gate_closure_v1"


@dataclass(frozen=True)
class CanonicalJudgeContract:
    """Immutable grading contract consumed by all panel providers."""

    section_id: str
    user_prompt: str
    deterministic_gate_summary: Mapping[str, Any]
    judge_task: str = _REQUIRED_TASK
    output_schema_ref: str = ""
    proof_boundary: Mapping[str, Any] | None = None
    canonical_hash: str | None = None

    def contract_hash(self) -> str:
        if self.canonical_hash:
            return self.canonical_hash
        return compute_contract_hash(self)

    def input_hash(self) -> str:
        return compute_contract_hash(self)[:16]


def compute_contract_hash(contract: CanonicalJudgeContract) -> str:
    payload = {
        "judge_task": contract.judge_task,
        "section_id": contract.section_id,
        "user_prompt": contract.user_prompt,
        "deterministic_gate_summary": dict(contract.deterministic_gate_summary),
        "output_schema_ref": contract.output_schema_ref,
        "proof_boundary": dict(contract.proof_boundary or {}),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_contract(contract: CanonicalJudgeContract) -> list[str]:
    errors: list[str] = []
    if str(contract.judge_task).upper() != _REQUIRED_TASK:
        errors.append(f"judge_task must be {_REQUIRED_TASK!r}, got {contract.judge_task!r}")
    if not str(contract.section_id).strip():
        errors.append("section_id is required")
    if not str(contract.user_prompt).strip():
        errors.append("user_prompt is required")
    if not contract.deterministic_gate_summary:
        errors.append("deterministic_gate_summary is required")
    boundary = contract.proof_boundary or {}
    for flag in (
        "jd_is_targeting_context_only",
        "briefing_is_targeting_context_only",
        "judges_must_not_rewrite",
    ):
        if flag in boundary and boundary[flag] is not True:
            errors.append(f"proof_boundary.{flag} must be true when present")
    return errors


@dataclass(frozen=True)
class DeclaredTransportPolicy:
    """Declared transport knobs audited against TransportReceipt."""

    max_output_tokens: int
    json_output_lock: str
    temperature: float | None = None
    system_includes_score_schema: bool = True


@dataclass(frozen=True)
class TransportReceipt:
    """Observed provider transport fields for parity audit."""

    provider_key: str
    contract_hash: str
    max_output_tokens: int
    temperature: float | None
    json_output_lock: str
    finish_or_stop_reason: str | None
    parse_status: str
    attempt: int = 1


@dataclass(frozen=True)
class PanelJudgeOutcome:
    """Normalized outcome from one provider after parse and score law."""

    provider_key: str
    contract_hash: str
    input_hash: str
    evaluator_mode: str
    provider_status: str
    score: float | None
    score_scale: str
    threshold: float
    pass_: bool
    decisive_failure: bool
    findings: tuple[str, ...] = field(default_factory=tuple)
    cited_sentence_indexes: tuple[int, ...] = field(default_factory=tuple)
    remediation_suggestions: tuple[str, ...] = field(default_factory=tuple)
    transport_receipt: TransportReceipt | None = None
    raw_body: dict[str, Any] | None = None


@dataclass(frozen=True)
class TransportParityViolation:
    code: str
    detail: str
    provider_key: str = ""


@dataclass(frozen=True)
class GateClosureRule:
    gate_id: str
    forbidden_finding_codes: frozenset[str]
    required_gate_status: str = "pass"


@dataclass(frozen=True)
class GateClosureMap:
    rules: tuple[GateClosureRule, ...]
    version: str = RECONCILE_POLICY_VERSION


@dataclass(frozen=True)
class PanelRunResult:
    contract_hash: str
    outcomes: tuple[PanelJudgeOutcome, ...]
    transport_violations: tuple[TransportParityViolation, ...]


class AdapterInvokeError(Exception):
    """Transport or parse failure, not content-quality FAIL."""


class JudgeProviderAdapter(Protocol):
    provider_key: str

    def declared_policy(self, *, attempt: int = 1) -> DeclaredTransportPolicy:
        """Return declared transport policy for parity preflight."""

    def invoke(
        self,
        contract: CanonicalJudgeContract,
        *,
        attempt: int = 1,
    ) -> tuple[PanelJudgeOutcome, TransportReceipt]:
        """Grade contract and return normalized outcome plus transport receipt."""


class PanelAdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, JudgeProviderAdapter] = {}

    def register(self, adapter: JudgeProviderAdapter) -> None:
        key = str(adapter.provider_key)
        if not key:
            raise ValueError("adapter.provider_key is required")
        self._adapters[key] = adapter

    def get(self, provider_key: str) -> JudgeProviderAdapter:
        try:
            return self._adapters[provider_key]
        except KeyError as exc:
            raise KeyError(f"no panel adapter registered for {provider_key!r}") from exc

    def keys(self) -> frozenset[str]:
        return frozenset(self._adapters.keys())


class JudgePanelRunner:
    """Fan-out grading: identical contract hash and user prompt for every provider."""

    def __init__(self, registry: PanelAdapterRegistry) -> None:
        self._registry = registry

    def run(
        self,
        contract: CanonicalJudgeContract,
        provider_keys: list[str],
        *,
        max_attempts: int = 2,
    ) -> PanelRunResult:
        errors = validate_contract(contract)
        if errors:
            raise ValueError("; ".join(errors))

        contract_hash = contract.contract_hash()
        outcomes: list[PanelJudgeOutcome] = []
        violations: list[TransportParityViolation] = []

        for key in provider_keys:
            adapter = self._registry.get(key)
            outcome: PanelJudgeOutcome | None = None
            receipt = None
            last_exc: Exception | None = None

            for attempt in range(1, max(max_attempts, 1) + 1):  # guardian: allow-retry-without-backoff -- bounded panel adapter retries
                declared = adapter.declared_policy(attempt=attempt)
                try:
                    outcome, receipt = adapter.invoke(contract, attempt=attempt)
                    break
                except AdapterInvokeError as exc:  # guardian: allow-retry-without-backoff -- bounded panel adapter retries
                    last_exc = exc
                    continue

            if outcome is None or receipt is None:
                msg = str(last_exc) if last_exc else "adapter returned no outcome"
                outcomes.append(
                    PanelJudgeOutcome(
                        provider_key=key,
                        contract_hash=contract_hash,
                        input_hash=contract.input_hash(),
                        evaluator_mode="BLOCKED",
                        provider_status="JUDGE_PROVIDER_BLOCKED",
                        score=None,
                        score_scale="0_to_5",
                        threshold=4.0,
                        pass_=False,
                        decisive_failure=False,
                        findings=(msg,),
                    )
                )
                continue

            if outcome.contract_hash != contract_hash:
                violations.append(
                    TransportParityViolation(
                        code="contract_hash_mismatch",
                        detail=f"outcome hash {outcome.contract_hash!r} != {contract_hash!r}",
                        provider_key=key,
                    )
                )

            violations.extend(audit_transport_parity(key, declared, receipt))
            outcomes.append(outcome)

        return PanelRunResult(
            contract_hash=contract_hash,
            outcomes=tuple(outcomes),
            transport_violations=tuple(violations),
        )


def audit_provider_transport_profile(
    provider_key: str,
    declared: DeclaredTransportPolicy,
    observed: TransportReceipt,
) -> list[TransportParityViolation]:
    return audit_transport_parity(provider_key, declared, observed)


def audit_transport_parity(
    provider_key: str,
    declared: DeclaredTransportPolicy,
    observed: TransportReceipt,
) -> list[TransportParityViolation]:
    violations: list[TransportParityViolation] = []
    if observed.provider_key != provider_key:
        violations.append(
            TransportParityViolation(
                code="provider_key_mismatch",
                detail=f"observed={observed.provider_key!r}",
                provider_key=provider_key,
            )
        )
    if observed.max_output_tokens < declared.max_output_tokens:
        violations.append(
            TransportParityViolation(
                code="max_output_tokens_below_declared",
                detail=f"observed={observed.max_output_tokens} declared={declared.max_output_tokens}",
                provider_key=provider_key,
            )
        )
    if declared.json_output_lock and observed.json_output_lock != declared.json_output_lock:
        violations.append(
            TransportParityViolation(
                code="json_output_lock_mismatch",
                detail=f"observed={observed.json_output_lock!r} declared={declared.json_output_lock!r}",
                provider_key=provider_key,
            )
        )
    if declared.system_includes_score_schema and observed.parse_status == "missing_schema_anchor":
        violations.append(
            TransportParityViolation(
                code="system_missing_score_schema",
                detail="parse_status indicates missing schema anchor",
                provider_key=provider_key,
            )
        )
    if observed.finish_or_stop_reason in frozenset({"max_tokens", "length", "model_length"}):
        violations.append(
            TransportParityViolation(
                code="truncation_stop_reason",
                detail=f"finish/stop reason={observed.finish_or_stop_reason!r}",
                provider_key=provider_key,
            )
        )
    return violations


__all__ = [
    "AdapterInvokeError",
    "CanonicalJudgeContract",
    "DeclaredTransportPolicy",
    "GateClosureMap",
    "GateClosureRule",
    "JudgePanelRunner",
    "JudgeProviderAdapter",
    "PanelAdapterRegistry",
    "PanelJudgeOutcome",
    "PanelRunResult",
    "TransportParityViolation",
    "TransportReceipt",
    "audit_provider_transport_profile",
    "audit_transport_parity",
    "compute_contract_hash",
    "validate_contract",
]
