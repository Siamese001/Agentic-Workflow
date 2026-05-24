"""Multi-provider judge panel runner — one contract, N transports."""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.judges.panel.adapter_protocol import AdapterInvokeError
from agentic_core.runtime.judges.panel.canonical_contract import (
    CanonicalJudgeContract,
    validate_contract,
)
from agentic_core.runtime.judges.panel.panel_registry import PanelAdapterRegistry
from agentic_core.runtime.judges.panel.panel_types import PanelJudgeOutcome, TransportParityViolation
from agentic_core.runtime.judges.panel.transport_parity import audit_transport_parity


@dataclass(frozen=True)
class PanelRunResult:
    contract_hash: str
    outcomes: tuple[PanelJudgeOutcome, ...]
    transport_violations: tuple[TransportParityViolation, ...]


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
            declared = adapter.declared_policy(attempt=1)
            outcome: PanelJudgeOutcome | None = None
            receipt = None
            last_exc: Exception | None = None

            for attempt in range(1, max(max_attempts, 1) + 1):
                declared = adapter.declared_policy(attempt=attempt)
                try:
                    outcome, receipt = adapter.invoke(contract, attempt=attempt)
                    break
                except AdapterInvokeError as exc:
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


__all__ = ["JudgePanelRunner", "PanelRunResult"]
