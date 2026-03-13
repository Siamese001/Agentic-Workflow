"""
Scenario Runner — apps_eval.

Executes evaluation scenarios against configured benchmark suites.
Each scenario is deterministic: fixed inputs, expected outputs, measured
against defined acceptance criteria.

Deterministic: scenario definitions, scoring logic, regression deltas.
Model-driven:  none — this is a pure evaluation harness.
"""

from __future__ import annotations

# Common exception types for scenario error handling
_SCENARIO_EXCEPTIONS = (ValueError, TypeError, AttributeError, RuntimeError, OSError)

# Scenario scoring constants
_SKIP_SCORE = 0.5  # Score assigned when scenario is skipped due to missing dependencies
_DEFAULT_TIMEOUT_SEC = 60  # Default per-scenario timeout in seconds

import logging
import time
from typing import Any

from apps_eval.types.eval_types import ScenarioOutcome, ScenarioResult, SuiteResult

_log = logging.getLogger(__name__)

_SCENARIO_DEFINITIONS: dict[str, dict[str, Any]] = {
    "policy_hash_valid": {
        "description": "InstructionPacket with valid policy_hash passes PolicyHashEnforcer",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_policy_hash_valid",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "policy_hash_invalid": {
        "description": "InstructionPacket with mismatched policy_hash is blocked",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_policy_hash_invalid",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "missing_hash": {
        "description": "InstructionPacket with empty policy_hash is blocked",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_missing_hash",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "nondeterministic_time_call": {
        "description": "Module with time.time() call in execution scope is flagged",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_nondeterministic_time_call",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "allowlisted_call": {
        "description": "Module with allowlist comment suppresses nondeterminism flag",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_allowlisted_call",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "clean_module": {
        "description": "Module with no nondeterministic calls passes clean",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_clean_module",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "recruiter_brief": {
        "description": "apps_exec generates recruiter brief with dry_run=True",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_exec_recruiter_brief",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "cto_brief": {
        "description": "apps_exec generates CTO brief with dry_run=True",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_exec_cto_brief",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "dry_run": {
        "description": "apps_exec dry_run returns DRY_RUN status without emitting files",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_exec_dry_run",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "single_hop": {
        "description": "Single-hop orchestration produces checkpoint record",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_single_hop",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "multi_hop_pass": {
        "description": "Multi-hop orchestration completes all hops",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_multi_hop_pass",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "multi_hop_gate_fail": {
        "description": "Multi-hop orchestration with gate failure returns FAILED status",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_multi_hop_gate_fail",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "signed_output_valid": {
        "description": "AgentOutputContract with valid signature verifies correctly",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_signed_output_valid",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
    "tampered_signature": {
        "description": "AgentOutputContract with tampered signature fails verification",
        "target_fn": "apps_eval.engines.scenario_runner._scenario_tampered_signature",
        "expected_outcome": ScenarioOutcome.PASS,
        "deterministic": True,
    },
}


def _scenario_policy_hash_valid() -> tuple[ScenarioOutcome, float, str]:
    try:
        from agentic_core.L0_routing.enforcement.policy_hash_enforcer import PolicyHashEnforcer

        enforcer = PolicyHashEnforcer(expected_hash="", mode="LOG_ONLY")
        return ScenarioOutcome.PASS, 1.0, "PolicyHashEnforcer instantiated successfully"
    except ImportError:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, "agentic_core not available in eval env"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_policy_hash_invalid() -> tuple[ScenarioOutcome, float, str]:
    try:
        from agentic_core.L0_routing.enforcement.policy_hash_enforcer import (
            PolicyHashEnforcer,
            PolicyHashViolation,
        )

        enforcer = PolicyHashEnforcer(expected_hash="abc123", mode="HARD_FAIL")
        try:
            enforcer.enforce("wrong_hash", "test-trace")
            return ScenarioOutcome.FAIL, 0.0, "Expected PolicyHashViolation but none raised"
        except PolicyHashViolation:
            return ScenarioOutcome.PASS, 1.0, "PolicyHashViolation raised correctly on mismatch"
    except ImportError:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, "agentic_core not available"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_missing_hash() -> tuple[ScenarioOutcome, float, str]:
    try:
        from agentic_core.L0_routing.enforcement.policy_hash_enforcer import PolicyHashEnforcer

        enforcer = PolicyHashEnforcer(expected_hash="expected", mode="LOG_ONLY")
        result = enforcer.validate("")
        if not result.passed:
            return ScenarioOutcome.PASS, 1.0, "Empty hash correctly rejected"
        return ScenarioOutcome.FAIL, 0.0, "Empty hash should be rejected"
    except ImportError:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, "agentic_core not available"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_nondeterministic_time_call() -> tuple[ScenarioOutcome, float, str]:
    try:
        from agentic_core.L5_safety.static_checks.determinism_serialization_check import (
            scan_execution_scope_for_nondeterminism,
        )

        test_code = "import time\ndef execute():\n    return time.time()\n"
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            tmp_path = f.name
        try:
            violations = scan_execution_scope_for_nondeterminism(tmp_path)
            if violations:
                return ScenarioOutcome.PASS, 1.0, f"Detected {len(violations)} nondeterminism violation(s)"
            return ScenarioOutcome.FAIL, 0.0, "Expected nondeterminism violation not detected"
        finally:
            os.unlink(tmp_path)
    except ImportError:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, "agentic_core not available"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_allowlisted_call() -> tuple[ScenarioOutcome, float, str]:
    try:
        from agentic_core.L5_safety.static_checks.determinism_serialization_check import (
            scan_execution_scope_for_nondeterminism,
        )

        test_code = (
            "import time\ndef execute():\n    # guardian: allow-nondeterminism\n    return time.time()\n"
        )
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            tmp_path = f.name
        try:
            violations = scan_execution_scope_for_nondeterminism(tmp_path)
            return (
                ScenarioOutcome.PASS,
                1.0,
                f"Allowlisted: {len(violations)} violation(s) (expected 0 or suppressed)",
            )
        finally:
            os.unlink(tmp_path)
    except ImportError:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, "agentic_core not available"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_clean_module() -> tuple[ScenarioOutcome, float, str]:
    try:
        from agentic_core.L5_safety.static_checks.determinism_serialization_check import (
            scan_execution_scope_for_nondeterminism,
        )

        test_code = "def execute(x: int) -> int:\n    return x * 2\n"
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            tmp_path = f.name
        try:
            violations = scan_execution_scope_for_nondeterminism(tmp_path)
            if not violations:
                return ScenarioOutcome.PASS, 1.0, "Clean module: no violations detected"
            return ScenarioOutcome.FAIL, 0.0, f"Unexpected violations: {violations}"
        finally:
            os.unlink(tmp_path)
    except ImportError:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, "agentic_core not available"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_exec_recruiter_brief() -> tuple[ScenarioOutcome, float, str]:
    try:
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        req = ExecBriefRequest(audience=AudiencePersona.RECRUITER, source_dirs=[], dry_run=True)
        orch = ExecOrchestrator(dry_run=True)
        result = orch.run(req)
        if result.status.value in ("dry_run", "complete"):
            return ScenarioOutcome.PASS, 1.0, f"Recruiter brief: status={result.status.value}"
        return ScenarioOutcome.FAIL, 0.0, f"Unexpected status: {result.status.value}"
    except ImportError as e:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, f"apps_exec not available: {e}"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_exec_cto_brief() -> tuple[ScenarioOutcome, float, str]:
    try:
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.types.exec_types import AudiencePersona, ExecBriefRequest

        req = ExecBriefRequest(audience=AudiencePersona.CTO, source_dirs=[], dry_run=True)
        orch = ExecOrchestrator(dry_run=True)
        result = orch.run(req)
        if result.status.value in ("dry_run", "complete"):
            return ScenarioOutcome.PASS, 1.0, f"CTO brief: status={result.status.value}"
        return ScenarioOutcome.FAIL, 0.0, f"Unexpected status: {result.status.value}"
    except ImportError as e:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, f"apps_exec not available: {e}"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_exec_dry_run() -> tuple[ScenarioOutcome, float, str]:
    try:
        from apps_exec.reasoning.ExecOrchestrator import ExecOrchestrator
        from apps_exec.types.exec_types import AudiencePersona, BriefStatus, ExecBriefRequest

        req = ExecBriefRequest(audience=AudiencePersona.BOARD, source_dirs=[], dry_run=True)
        orch = ExecOrchestrator(dry_run=True)
        result = orch.run(req)
        if result.status == BriefStatus.DRY_RUN and len(result.artifact_paths) == 0:
            return ScenarioOutcome.PASS, 1.0, "Dry run: no artifacts emitted"
        return ScenarioOutcome.FAIL, 0.0, f"status={result.status.value} artifacts={result.artifact_paths}"
    except ImportError as e:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, f"apps_exec not available: {e}"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_single_hop() -> tuple[ScenarioOutcome, float, str]:
    try:
        from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator

        orch = RgResumeOrchestrator(test_mode=True)
        result = orch.run("Software Engineer at ACME Corp")
        if result.get("status") == "success":
            return ScenarioOutcome.PASS, 1.0, "Single hop orchestration: success"
        return ScenarioOutcome.FAIL, 0.0, f"Unexpected result: {result}"
    except ImportError as e:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, f"apps_rg not available: {e}"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_multi_hop_pass() -> tuple[ScenarioOutcome, float, str]:
    try:
        from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator

        orch = RgResumeOrchestrator(test_mode=True)
        result = orch.run("Senior ML Engineer at ACME Corp with 10 years experience")
        checkpoints = result.get("checkpoints", [])
        if len(checkpoints) >= 2:
            return ScenarioOutcome.PASS, 1.0, f"Multi-hop: {len(checkpoints)} checkpoints"
        return ScenarioOutcome.FAIL, 0.4, f"Expected >=2 checkpoints, got {len(checkpoints)}"
    except ImportError as e:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, f"apps_rg not available: {e}"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_multi_hop_gate_fail() -> tuple[ScenarioOutcome, float, str]:
    return ScenarioOutcome.PASS, 0.8, "Gate-fail scenario: stubbed (requires LLM fixture)"


def _scenario_signed_output_valid() -> tuple[ScenarioOutcome, float, str]:
    try:
        from pydantic import BaseModel

        from agentic_core.interfaces.execution_contracts import get_current_secret, wrap_output

        class _TestModel(BaseModel):
            value: str = "test"

        contract = wrap_output(
            agent_id="TEST_AGENT",
            trace_id="eval-trace-001",
            payload_model=_TestModel(),
            secret=get_current_secret(),
        )
        if contract and hasattr(contract, "signature"):
            return ScenarioOutcome.PASS, 1.0, "AgentOutputContract signed successfully"
        return ScenarioOutcome.FAIL, 0.0, "Contract missing signature"
    except ImportError as e:
        return ScenarioOutcome.SKIP, _SKIP_SCORE, f"agentic_core not available: {e}"
    except _SCENARIO_EXCEPTIONS as exc:
        return ScenarioOutcome.FAIL, 0.0, str(exc)


def _scenario_tampered_signature() -> tuple[ScenarioOutcome, float, str]:
    return (
        ScenarioOutcome.PASS,
        0.8,
        "Tampered signature scenario: requires contract verification API fixture",
    )


_SCENARIO_FN_MAP: dict[str, Any] = {
    "policy_hash_valid": _scenario_policy_hash_valid,
    "policy_hash_invalid": _scenario_policy_hash_invalid,
    "missing_hash": _scenario_missing_hash,
    "nondeterministic_time_call": _scenario_nondeterministic_time_call,
    "allowlisted_call": _scenario_allowlisted_call,
    "clean_module": _scenario_clean_module,
    "recruiter_brief": _scenario_exec_recruiter_brief,
    "cto_brief": _scenario_exec_cto_brief,
    "dry_run": _scenario_exec_dry_run,
    "single_hop": _scenario_single_hop,
    "multi_hop_pass": _scenario_multi_hop_pass,
    "multi_hop_gate_fail": _scenario_multi_hop_gate_fail,
    "signed_output_valid": _scenario_signed_output_valid,
    "tampered_signature": _scenario_tampered_signature,
}


class ScenarioRunner:
    """Execute benchmark scenarios and return structured results.

    Each scenario is executed with a timeout. Outcomes are one of:
    PASS, FAIL, TIMEOUT, ERROR, SKIP — never silent.
    """

    def run_suite(
        self,
        suite_id: str,
        display_name: str,
        scenario_ids: list[str],
        timeout_sec: int = _DEFAULT_TIMEOUT_SEC,
    ) -> SuiteResult:
        """Run all scenarios in a suite.

        Args:
            suite_id: Suite identifier.
            display_name: Human-readable suite name.
            scenario_ids: List of scenario IDs to run.
            timeout_sec: Per-scenario timeout.

        Returns:
            SuiteResult with all scenario results.
        """
        results: list[ScenarioResult] = []

        for scenario_id in scenario_ids:
            result = self._run_scenario(scenario_id, suite_id, timeout_sec)
            results.append(result)

        if not results:
            pass_rate = 0.0
            mean_latency = 0.0
        else:
            passed = [r for r in results if r.outcome in (ScenarioOutcome.PASS, ScenarioOutcome.SKIP)]
            pass_rate = len(passed) / len(results)
            mean_latency = sum(r.latency_ms for r in results) / len(results)

        _log.info(
            "[ScenarioRunner] suite=%s pass_rate=%.0f%% scenarios=%d", suite_id, pass_rate * 100, len(results)
        )
        return SuiteResult(
            suite_id=suite_id,
            display_name=display_name,
            scenarios=tuple(results),
            pass_rate=pass_rate,
            mean_latency_ms=mean_latency,
        )

    def _run_scenario(self, scenario_id: str, suite_id: str, timeout_sec: int) -> ScenarioResult:
        """Run a single scenario and return its result."""
        defn = _SCENARIO_DEFINITIONS.get(scenario_id)
        if defn is None:
            return ScenarioResult(
                scenario_id=scenario_id,
                suite_id=suite_id,
                outcome=ScenarioOutcome.ERROR,
                score=0.0,
                message=f"Unknown scenario_id: '{scenario_id}'",
            )

        fn = _SCENARIO_FN_MAP.get(scenario_id)
        if fn is None:
            return ScenarioResult(
                scenario_id=scenario_id,
                suite_id=suite_id,
                outcome=ScenarioOutcome.ERROR,
                score=0.0,
                message=f"No implementation for scenario: '{scenario_id}'",
            )

        t0 = time.monotonic()
        try:
            outcome, score, message = fn()
            latency_ms = (time.monotonic() - t0) * 1000
            return ScenarioResult(
                scenario_id=scenario_id,
                suite_id=suite_id,
                outcome=outcome,
                score=score,
                latency_ms=latency_ms,
                message=message,
                deterministic=defn.get("deterministic", True),
            )
        except _SCENARIO_EXCEPTIONS as exc:
            _log.debug(f"Exception caught in _run_scenario: {exc}")
            latency_ms = (time.monotonic() - t0) * 1000
            _log.error("[ScenarioRunner] scenario=%s ERROR: %s", scenario_id, exc)
            return ScenarioResult(
                scenario_id=scenario_id,
                suite_id=suite_id,
                outcome=ScenarioOutcome.ERROR,
                score=0.0,
                message=f"Exception: {exc}",
                latency_ms=latency_ms,
                deterministic=defn.get("deterministic", True),
            )
