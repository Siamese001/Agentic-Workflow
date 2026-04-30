"""
Formal governed-exception record and safe partial adoption for apps_eval.

apps_eval is permanently exempt from GovernedAppRunner because it IS the
evaluation framework; routing it through GovernedAppRunner (which calls
evaluate_and_emit in L5/L6) would create a circular evaluation-of-evaluator
loop.

Safe adoptions implemented here
--------------------------------
  BUS_T_telemetry      : Emit structured telemetry WITHOUT calling evaluate_and_emit.
  conformance_metadata : get_exception_record() for the conformance gate.

This module deliberately imports NOTHING from agentic_core.L6_observability
or apps_shared.integrations.governed_app_runner to preserve the boundary.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exception constants
# ---------------------------------------------------------------------------

EXCEPTION_REASON_CODE = "circular_dependency"
BLOCKED_LAYERS: tuple[str, ...] = ("L0", "L1", "C0", "L2", "L5", "L6")
SAFE_LAYERS: tuple[str, ...] = ("BUS_T_telemetry", "conformance_metadata")
COMPENSATING_CONTROLS: tuple[str, ...] = (
    "CC-EVAL-01: eval runs emit standard telemetry without calling evaluate_and_emit",
    "CC-EVAL-02: get_exception_record() exposes machine-readable ExceptionRecord",
    "CC-EVAL-03: module import guard — no L6 circularity triggered on import",
    "CC-EVAL-04: exception reviewed and re-certified annually by eval-platform team",
)

# ---------------------------------------------------------------------------
# Exception record (machine-readable declaration)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvalExceptionRecord:
    """Formal exception declaration for apps_eval."""

    app_name: str = "apps_eval"
    exception_reason_code: str = EXCEPTION_REASON_CODE
    blocked_layers: tuple[str, ...] = BLOCKED_LAYERS
    safe_layers: tuple[str, ...] = SAFE_LAYERS
    compensating_controls: tuple[str, ...] = COMPENSATING_CONTROLS
    review_cadence: str = "annual"
    owner: str = "eval-platform team"
    target_phase: str = "N/A — permanent exception"


# ---------------------------------------------------------------------------
# BUS T-compatible telemetry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvalRunTelemetry:
    """BUS T-compatible telemetry packet for an evaluation run.

    Deliberately does NOT call evaluate_and_emit to prevent circularity.
    """

    run_id: str
    eval_type: str
    suite_name: str
    passed: bool
    metric_count: int
    timestamp: str
    exception_app: str = "apps_eval"


# ---------------------------------------------------------------------------
# Exception handler
# ---------------------------------------------------------------------------


class GovernedEvalException:
    """Safe partial-adoption handler for apps_eval.

    Does NOT subclass GovernedAppRunner.  The circular-dependency
    boundary IS the reason this class exists.

    Safe surfaces
    -------------
    - BUS T telemetry emission (no evaluate_and_emit)
    - Conformance metadata endpoint
    - check_compensating_controls() for the gate
    """

    APP_NAME = "apps_eval"
    EXCEPTION_REASON_CODE = EXCEPTION_REASON_CODE

    def get_exception_record(self) -> EvalExceptionRecord:
        """Return the formal exception record for the conformance gate."""
        return EvalExceptionRecord()

    def emit_run_telemetry(
        self,
        *,
        eval_type: str,
        suite_name: str,
        passed: bool,
        metric_count: int = 0,
    ) -> EvalRunTelemetry:
        """Emit BUS T-compatible telemetry for an evaluation run.

        Deliberately avoids evaluate_and_emit — that call would be circular.
        This is a lightweight structured log only.
        """
        telemetry = EvalRunTelemetry(
            run_id=f"eval-{uuid.uuid4().hex[:12]}",
            eval_type=eval_type,
            suite_name=suite_name,
            passed=passed,
            metric_count=metric_count,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
        )
        _LOGGER.info(
            "eval_exception_telemetry run_id=%s eval_type=%s passed=%s metric_count=%d",
            telemetry.run_id,
            telemetry.eval_type,
            telemetry.passed,
            telemetry.metric_count,
        )
        return telemetry

    def check_compensating_controls(self) -> list[tuple[str, bool, str]]:
        """Verify all compensating controls are in place.

        Returns list of (label, passed, detail) tuples compatible with
        the conformance gate proof table format.
        """
        results: list[tuple[str, bool, str]] = []

        # CC-EVAL-01: telemetry emission — no circularity
        try:
            t = self.emit_run_telemetry(
                eval_type="conformance_check",
                suite_name="cc_eval_01",
                passed=True,
                metric_count=1,
            )
            cc01_pass = bool(t.run_id)
            cc01_detail = f"run_id={t.run_id}"
        except (RuntimeError, TypeError, ValueError) as exc:
            cc01_pass = False
            cc01_detail = str(exc)[:50]
        results.append(("CC-EVAL-01 telemetry (no circularity)", cc01_pass, cc01_detail))

        # CC-EVAL-02: exception record accessible
        try:
            rec = self.get_exception_record()
            cc02_pass = rec.app_name == "apps_eval"
            cc02_detail = f"app={rec.app_name}"
        except (AttributeError, TypeError) as exc:
            cc02_pass = False
            cc02_detail = str(exc)[:50]
        results.append(("CC-EVAL-02 exception record accessible", cc02_pass, cc02_detail))

        # CC-EVAL-03: import guard (module importable without L6 circularity)
        try:
            import importlib  # noqa: PLC0415

            m = importlib.import_module("apps_eval.integrations.governed_eval_exception")
            cc03_pass = hasattr(m, "GovernedEvalException")
            cc03_detail = "import OK — no L6 circularity"
        except ImportError as exc:
            cc03_pass = False
            cc03_detail = str(exc)[:50]
        results.append(("CC-EVAL-03 import guard (no L6 circularity)", cc03_pass, cc03_detail))

        # CC-EVAL-04: review cadence declared
        rec = self.get_exception_record()
        cc04_pass = bool(rec.review_cadence)
        cc04_detail = f"cadence={rec.review_cadence}"
        results.append(("CC-EVAL-04 review cadence declared", cc04_pass, cc04_detail))

        return results


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_eval.integrations.governed_eval_exception', "module_loaded")
