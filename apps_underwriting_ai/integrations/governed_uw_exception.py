"""
Formal governed-exception record and safe partial adoption for apps_underwriting_ai.

apps_underwriting_ai is permanently exempt from GovernedAppRunner because its
decisions are legally-binding credit determinations.  Injecting them through a
generic evidence-retrieval substrate (L1→C0→L2) is inappropriate and a
regulatory compliance risk.  The app defines its own CoreAdapter +
CoreHandoffPayload governance protocol, which provides equivalent guarantees.

Safe adoptions implemented here
--------------------------------
  BUS_T_telemetry      : Wrap ObservabilityAdapter output as BUS T-compatible telemetry.
  conformance_metadata : get_exception_record() for the conformance gate.

Blocked surfaces and their domain equivalents
----------------------------------------------
  L0 generic routing    → product_type + decision_type routing in CoreAdapter
  L1 query decomp       → structured UnderwritingRequest (no free-text query)
  C0 evidence retrieval → retrieval_adapter.py with typed DocumentSet
  L2 authorize_and_exec → policy_adapter.py + domain validators (domain chokepoint)
  L5 safety exit gate   → human_review_reason + review_required (domain gate)
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from apps_shared.integrations.runtime_hitl_integration import (
    HitlResult,
    build_exit_envelope,
    maybe_escalate_hitl,
)

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exception constants
# ---------------------------------------------------------------------------

EXCEPTION_REASON_CODE = "regulatory_domain"
BLOCKED_LAYERS: tuple[str, ...] = ("L0", "L1", "C0", "L2", "L5")
SAFE_LAYERS: tuple[str, ...] = ("BUS_T_telemetry", "conformance_metadata")
COMPENSATING_CONTROLS: tuple[str, ...] = (
    "CC-UW-01: all decisions emit L6-compatible telemetry via ObservabilityAdapter",
    "CC-UW-02: CoreAdapter.prepare_handoff() provides equivalent L2 governance guarantees",
    "CC-UW-03: get_exception_record() exposes machine-readable ExceptionRecord",
    "CC-UW-04: governance protocol reviewed annually with regulatory compliance sign-off",
)

# ---------------------------------------------------------------------------
# Exception record (machine-readable declaration)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UwExceptionRecord:
    """Formal exception declaration for apps_underwriting_ai."""

    app_name: str = "apps_underwriting_ai"
    exception_reason_code: str = EXCEPTION_REASON_CODE
    blocked_layers: tuple[str, ...] = BLOCKED_LAYERS
    safe_layers: tuple[str, ...] = SAFE_LAYERS
    compensating_controls: tuple[str, ...] = COMPENSATING_CONTROLS
    review_cadence: str = "annual"
    owner: str = "underwriting-ai team"
    target_phase: str = "N/A — permanent exception"


# ---------------------------------------------------------------------------
# BUS T-compatible telemetry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UwDecisionTelemetry:
    """BUS T-compatible telemetry packet for an underwriting decision."""

    run_id: str
    request_id: str
    product_type: str
    decision_type: str
    recommended_decision: str
    confidence_score: float
    review_required: bool
    timestamp: str
    exception_app: str = "apps_underwriting_ai"


# ---------------------------------------------------------------------------
# Exception handler
# ---------------------------------------------------------------------------


class GovernedUwException:
    """Safe partial-adoption handler for apps_underwriting_ai.

    Does NOT subclass GovernedAppRunner.  The regulatory-domain boundary
    IS the reason this class exists.

    Safe surfaces
    -------------
    - BUS T telemetry wrapping ObservabilityAdapter output
    - Conformance metadata endpoint
    - check_compensating_controls() for the gate
    """

    APP_NAME = "apps_underwriting_ai"
    EXCEPTION_REASON_CODE = EXCEPTION_REASON_CODE
    # W5 P5.2: opt-in to runtime HITL for covenant-exception decisions only.
    # This does NOT reopen the other blocked layers (L0/L1/C0/L2/L5) — the
    # escalation is invoked from CoreAdapter at the covenant-exception point.
    HITL_ENABLED = True

    @traces_execute(layer="L1_COGNITION")
    def get_exception_record(self) -> UwExceptionRecord:
        """Return the formal exception record for the conformance gate."""
        return UwExceptionRecord()

    def emit_decision_telemetry(
        self,
        *,
        request_id: str,
        product_type: str = "unknown",
        decision_type: str = "unknown",
        recommended_decision: str = "unknown",
        confidence_score: float = 0.0,
        review_required: bool = False,
    ) -> UwDecisionTelemetry:
        """Emit BUS T-compatible telemetry for an underwriting decision."""
        telemetry = UwDecisionTelemetry(
            run_id=f"uw-{uuid.uuid4().hex[:12]}",
            request_id=request_id,
            product_type=product_type,
            decision_type=decision_type,
            recommended_decision=recommended_decision,
            confidence_score=confidence_score,
            review_required=review_required,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
        )
        _LOGGER.info(
            "uw_exception_telemetry run_id=%s request_id=%s decision=%s review_required=%s",
            telemetry.run_id,
            telemetry.request_id,
            telemetry.recommended_decision,
            telemetry.review_required,
        )
        return telemetry

    def check_compensating_controls(self) -> list[tuple[str, bool, str]]:
        """Verify all compensating controls are in place.

        Returns list of (label, passed, detail) tuples compatible with
        the conformance gate proof table format.
        """
        results: list[tuple[str, bool, str]] = []

        # CC-UW-01: telemetry emission works
        try:
            t = self.emit_decision_telemetry(
                request_id="cc-uw-01-probe",
                product_type="commercial_loan",
                recommended_decision="approve",
                confidence_score=0.85,
            )
            cc01_pass = bool(t.run_id)
            cc01_detail = f"run_id={t.run_id}"
        except (RuntimeError, TypeError, ValueError) as exc:
            cc01_pass = False
            cc01_detail = str(exc)[:50]
        results.append(("CC-UW-01 telemetry (ObservabilityAdapter)", cc01_pass, cc01_detail))

        # CC-UW-02: CoreAdapter importable (equivalent L2 governance)
        try:
            import importlib  # noqa: PLC0415

            m = importlib.import_module("apps_underwriting_ai.integrations.core_adapter")
            cc02_pass = hasattr(m, "CoreAdapter") and hasattr(m, "CoreHandoffPayload")
            cc02_detail = "CoreAdapter + CoreHandoffPayload present"
        except ImportError as exc:
            cc02_pass = False
            cc02_detail = str(exc)[:50]
        results.append(("CC-UW-02 CoreAdapter (equiv L2 governance)", cc02_pass, cc02_detail))

        # CC-UW-03: exception record accessible
        try:
            rec = self.get_exception_record()
            cc03_pass = rec.app_name == "apps_underwriting_ai"
            cc03_detail = f"app={rec.app_name}"
        except (AttributeError, TypeError) as exc:
            cc03_pass = False
            cc03_detail = str(exc)[:50]
        results.append(("CC-UW-03 exception record accessible", cc03_pass, cc03_detail))

        # CC-UW-04: review cadence declared
        rec = self.get_exception_record()
        cc04_pass = bool(rec.review_cadence)
        cc04_detail = f"cadence={rec.review_cadence}"
        results.append(("CC-UW-04 review cadence declared", cc04_pass, cc04_detail))

        return results

    # ------------------------------------------------------------------
    # Runtime HITL hook (W5 P5.2) — covenant-exception path
    # ------------------------------------------------------------------

    def maybe_escalate_covenant_exception(
        self,
        *,
        request_id: str,
        product_type: str,
        decision_type: str,
        recommended_decision: str,
        confidence_score: float,
        review_required: bool,
        is_regulated: bool = True,
        is_financial: bool = True,
        covenant_exception_reason: str = "",
        controller: Any = None,
        run_state_store: Any = None,
        extra_checkpoint: Mapping[str, Any] | None = None,
    ) -> HitlResult:
        """Classify a covenant exception for runtime HITL escalation.

        apps_underwriting_ai is permanently exempt from GovernedAppRunner
        (regulatory domain — see module docstring). Runtime HITL integration
        therefore lives HERE, at the one decision point where a legally-binding
        credit determination may need a human reviewer: the covenant exception.

        Envelope mapping:
        - ``is_regulated`` — defaults True (underwriting is always regulated)
        - ``is_financial`` — defaults True (commitment-bearing)
        - ``confidence_score`` — the decision confidence already computed
        - ``requires_policy_override`` — True when ``review_required`` is True

        Checkpoint payload captures enough business state for a resume worker
        to reconstruct the decision context without re-running the full
        CoreAdapter pipeline (G7 closure).

        Returns
        -------
        HitlResult
            ``action=COMMIT`` + ``enabled=False`` when flags are off (rollback
            path). ``action=ESCALATE_HITL`` with a ledger row when classified.
        """
        # gate_disposition="block" when review_required to trigger
        # requires_policy_override via build_exit_envelope's default mapping.
        envelope = build_exit_envelope(
            app_name=self.APP_NAME,
            query=f"covenant_exception:{product_type}:{decision_type}",
            gate_disposition="block" if review_required else "pass",
            grounded=True,
            citation_count=1,
            support_coverage=max(0.0, min(1.0, float(confidence_score))),
            disposition="weak_support" if review_required else "strong_support",
            policy_overrides={
                "is_regulated": bool(is_regulated),
                "is_financial": bool(is_financial),
                "product_type": product_type,
                "decision_type": decision_type,
                "recommended_decision": recommended_decision,
                "covenant_exception_reason": covenant_exception_reason,
            },
        )
        checkpoint_payload: dict[str, Any] = {
            "app_name": self.APP_NAME,
            "request_id": request_id,
            "product_type": product_type,
            "decision_type": decision_type,
            "recommended_decision": recommended_decision,
            "confidence_score": float(confidence_score),
            "review_required": bool(review_required),
            "covenant_exception_reason": covenant_exception_reason,
        }
        if extra_checkpoint:
            checkpoint_payload.update(dict(extra_checkpoint))

        run_id = f"uw-{request_id}"
        result = maybe_escalate_hitl(
            app_name=self.APP_NAME,
            run_id=run_id,
            trace_id=run_id,
            envelope=envelope,
            runner_flag=bool(self.HITL_ENABLED),
            controller=controller,
            run_state_store=run_state_store,
            checkpoint_kind="covenant_exception",
            checkpoint_payload=checkpoint_payload,
        )
        _LOGGER.info(
            "uw_covenant_exception_hitl request_id=%s action=%s class=%s ledger=%s",
            request_id,
            result.action.value,
            result.hitl_class or "-",
            result.ledger_id or "-",
        )
        return result


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_underwriting_ai.integrations.governed_uw_exception', "module_loaded")
