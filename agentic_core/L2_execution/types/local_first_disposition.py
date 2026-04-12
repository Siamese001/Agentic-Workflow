"""LocalFirstDisposition — current-run routing decision packet for local-first orchestrators.

Phase 1: one packet per run(), emitted as a structured log line and attached to the
run result as an optional field. No learning mutation. No HITL/UWG changes.

Invariant: every allow/escalate/skip/fail outcome is explicit and auditable.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Optional


class AdapterDecision:
    """Canonical disposition values for the local-first Qwen lane."""

    ALLOW_LOCAL_QWEN = "ALLOW_LOCAL_QWEN"
    """Predicate selected LOCAL_VLLM, adapter allowed, Qwen called successfully."""

    ESCALATE_EXTERNAL = "ESCALATE_EXTERNAL"
    """Predicate selected LOCAL_VLLM but adapter forced Gemini (token/queue/breaker)."""

    SKIP_QWEN_NON_LOCAL_ROUTE = "SKIP_QWEN_NON_LOCAL_ROUTE"
    """Predicate selected a non-local provider (OPUS), or gateway was not initialised."""

    FAIL_LOCAL_INIT = "FAIL_LOCAL_INIT"
    """Predicate selected LOCAL_VLLM but gateway initialisation failed — run raises."""

    FAIL_LOCAL_EXECUTION = "FAIL_LOCAL_EXECUTION"
    """Adapter allowed, Qwen was called but raised — run re-raises."""


@dataclass
class LocalFirstDisposition:
    """Single current-run disposition packet for local-first orchestrators.

    Emitted once per run() call via::

        _logger.info("LOCAL_FIRST_DISPOSITION %s", json.dumps(packet.as_dict()))

    Also attached to the run result as ``result["local_first_disposition"]`` (dict
    results) or ``result.local_first_disposition`` (Pydantic results) for non-exception
    paths.  Exception paths (FAIL_LOCAL_INIT, FAIL_LOCAL_EXECUTION) log only.
    """

    orchestrator: str
    run_id: str
    route_provider: str
    adapter_decision: str
    provider_lane: str
    reason_code: str
    adapter_telemetry: dict = field(default_factory=dict)
    qwen_called: bool = False
    qwen_result_present: bool = False
    predicate_hash: str = ""
    init_error: Optional[str] = None
    execution_error: Optional[str] = None

    LOG_PREFIX = "LOCAL_FIRST_DISPOSITION"

    def as_dict(self) -> dict:
        """Return a JSON-serialisable dict (excludes class-level LOG_PREFIX)."""
        return asdict(self)

    def as_log_line(self) -> str:
        """Return the canonical structured log line for this packet."""
        return f"{self.LOG_PREFIX} {json.dumps(self.as_dict())}"

    # ------------------------------------------------------------------
    # Factories — one per canonical outcome.  Orchestrators call these
    # instead of the full positional constructor so the field mapping is
    # defined in one place.  All parameters are keyword-only to prevent
    # ordering mistakes at call sites.
    # ------------------------------------------------------------------

    @classmethod
    def for_fail_init(
        cls,
        *,
        orchestrator: str,
        run_id: str,
        predicate_hash: str,
        init_error: str,
    ) -> "LocalFirstDisposition":
        """LOCAL_VLLM selected but gateway init failed — run raises."""
        return cls(
            orchestrator=orchestrator,
            run_id=run_id,
            route_provider="LOCAL_VLLM",
            adapter_decision=AdapterDecision.FAIL_LOCAL_INIT,
            provider_lane="none",
            reason_code="qwen_init_failed",
            predicate_hash=predicate_hash,
            init_error=init_error,
        )

    @classmethod
    def for_escalate(
        cls,
        *,
        orchestrator: str,
        run_id: str,
        predicate_hash: str,
        telem: dict,
    ) -> "LocalFirstDisposition":
        """Adapter forced Gemini (token / queue / breaker)."""
        return cls(
            orchestrator=orchestrator,
            run_id=run_id,
            route_provider="LOCAL_VLLM",
            adapter_decision=AdapterDecision.ESCALATE_EXTERNAL,
            provider_lane=telem.get("provider_selected", "gemini"),
            reason_code="adapter_route_to_gemini",
            adapter_telemetry=telem,
            predicate_hash=predicate_hash,
        )

    @classmethod
    def for_fail_exec(
        cls,
        *,
        orchestrator: str,
        run_id: str,
        predicate_hash: str,
        telem: dict,
        exc: BaseException,
    ) -> "LocalFirstDisposition":
        """Adapter allowed, Qwen was called but raised — run re-raises."""
        return cls(
            orchestrator=orchestrator,
            run_id=run_id,
            route_provider="LOCAL_VLLM",
            adapter_decision=AdapterDecision.FAIL_LOCAL_EXECUTION,
            provider_lane=telem.get("provider_selected", "local_fast"),
            reason_code="qwen_execution_error",
            adapter_telemetry=telem,
            qwen_called=True,
            predicate_hash=predicate_hash,
            execution_error=str(exc),
        )

    @classmethod
    def for_allow(
        cls,
        *,
        orchestrator: str,
        run_id: str,
        predicate_hash: str,
        telem: dict,
        qwen_result_present: bool,
    ) -> "LocalFirstDisposition":
        """Adapter allowed, Qwen called successfully."""
        return cls(
            orchestrator=orchestrator,
            run_id=run_id,
            route_provider="LOCAL_VLLM",
            adapter_decision=AdapterDecision.ALLOW_LOCAL_QWEN,
            provider_lane=telem.get("provider_selected", "local_fast"),
            reason_code="adapter_allow",
            adapter_telemetry=telem,
            qwen_called=True,
            qwen_result_present=qwen_result_present,
            predicate_hash=predicate_hash,
        )

    @classmethod
    def for_skip(
        cls,
        *,
        orchestrator: str,
        run_id: str,
        provider_value: str,
        predicate_hash: str,
        reason_code: str,
    ) -> "LocalFirstDisposition":
        """Non-local predicate selected, or gateway not initialised — Qwen not called."""
        return cls(
            orchestrator=orchestrator,
            run_id=run_id,
            route_provider=provider_value,
            adapter_decision=AdapterDecision.SKIP_QWEN_NON_LOCAL_ROUTE,
            provider_lane="none",
            reason_code=reason_code,
            predicate_hash=predicate_hash,
        )
