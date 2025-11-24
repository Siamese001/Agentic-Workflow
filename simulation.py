# FILE: 10_10/simulation.py
"""
Phase-3 Simulation Harness (v10_10) — Batch D (Testing & Simulation)
====================================================================

This module provides a meta-level simulation system for the v10_10 stack.

It focuses on:

  • Exercising the Phase-3 knobs across multiple scenarios:
        - HYDE enabled vs disabled
        - RRF strategies
        - QA council size
        - Correction-loop depth
        - Telemetry routing modes

  • Using the real entrypoints:
        - main_v10_10.run_workflow (single-job)
        - run_batch_v10_10.run_batch (optional batch helper)

  • Producing deterministic, machine-verifiable artefacts:
        - Per-scenario summaries
        - Outcome statistics (success/failure, corrections, council behaviour)
        - Telemetry/event counts
        - Optional golden evaluation reports (via golden_eval)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from itertools import product
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from cli.main_v10_10 import (
    run_workflow,
    RRFStrategy,
    TelemetryRoutingMode,
)
from cli.run_batch_v10_10 import run_batch, BatchJobResult, BatchTelemetrySummary
from golden_eval import (
    GOLDEN_SCENARIOS,
    GoldenScenario,
    ScenarioKnobs,
    EvalReport,
    evaluate_patch,
)
from observability import (
    emit_scenario_start_event,
    emit_scenario_end_event,
    emit_scenario_simulation_event,
)


# ============================================================================
# 1. Small utilities
# ============================================================================


def _as_mapping(obj: Any) -> Mapping[str, Any]:
    """
    Best-effort conversion of arbitrary objects into a mapping view.
    """
    if obj is None:
        return {}
    if isinstance(obj, Mapping):
        return obj
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()  # type: ignore[call-arg]
        except TypeError:
            pass
    if hasattr(obj, "dict"):
        try:
            return obj.dict()  # type: ignore[call-arg]
        except TypeError:
            pass
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return {}


def _extract_state_patch(result: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Try to recover the final state patch from a WorkflowOutput-like object.

    We intentionally support multiple shapes to keep this resilient to
    small refactors in the runtime layer.
    """
    # Direct key
    patch = result.get("state_patch")
    if isinstance(patch, Mapping):
        return patch

    # Alternate naming
    for key in ("final_state_patch", "l4_state_patch", "workflow_state"):
        candidate = result.get(key)
        if isinstance(candidate, Mapping):
            # workflow_state might itself contain a nested state_patch
            nested = candidate.get("state_patch") if isinstance(candidate, Mapping) else None
            if isinstance(nested, Mapping):
                return nested
            return candidate

    return {}


def _extract_l2_results(result: Mapping[str, Any]) -> Mapping[str, Any]:
    l2 = result.get("l2_results")
    if isinstance(l2, Mapping):
        return l2
    return {}


def _build_snapshot(result: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Build a trimmed, stable snapshot from a workflow result for CI output.
    """
    patch = _extract_state_patch(result)
    l2 = _extract_l2_results(result)

    return {
        "state_patch": {
            "strategy_text": patch.get("strategy_text"),
            "rag_evidence": patch.get("rag_evidence"),
            "drafted_sections": patch.get("drafted_sections"),
            "qa_findings": patch.get("qa_findings"),
            "safety_findings": patch.get("safety_findings"),
            "correction_signals": patch.get("correction_signals"),
            "safety_passed": patch.get("safety_passed"),
        },
        "l2_results": {
            "strategy": l2.get("strategy"),
            "rag": l2.get("rag"),
            "drafting": l2.get("drafting"),
            "qa": l2.get("qa"),
            "safety": l2.get("safety"),
        },
    }


def _summarise_telemetry(result: Mapping[str, Any], patch: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Approximate telemetry summary: presence + simple counts.
    """
    # Prefer explicit telemetry_events if present.
    events = None
    for container in (result, patch):
        cand = container.get("telemetry_events")
        if isinstance(cand, list):
            events = cand
            break

    num_events = len(events) if isinstance(events, list) else 0

    # Some pipelines expose aggregate counts instead.
    observability = patch.get("observability") or result.get("observability") or {}
    counts = {}
    if isinstance(observability, Mapping):
        counts_obj = observability.get("telemetry_counts")
        if isinstance(counts_obj, Mapping):
            counts = dict(counts_obj)

    has_telemetry = bool(num_events or counts)

    return {
        "has_telemetry": has_telemetry,
        "num_events": num_events,
        "counts": counts,
    }


def _summarise_outcome(
    result: Mapping[str, Any],
    patch: Mapping[str, Any],
    eval_report: Optional[EvalReport],
    council_size: Optional[int],
    correction_max_iterations: Optional[int],
) -> Dict[str, Any]:
    """
    Collate outcome-level statistics used by tests and CI dashboards.
    """
    safety_passed = bool(result.get("safety_passed", patch.get("safety_passed", True)))
    corrected = bool(result.get("corrected", False))

    qa_findings = patch.get("qa_findings") or []
    if not isinstance(qa_findings, list):
        qa_findings = []
    num_qa_failed = sum(
        1 for f in qa_findings if not bool(_as_mapping(f).get("passed", False))
    )

    safety_findings = patch.get("safety_findings") or []
    if not isinstance(safety_findings, list):
        safety_findings = []
    num_blocking_safety = sum(
        1 for f in safety_findings if bool(_as_mapping(f).get("blocking", False))
    )

    correction_state = patch.get("correction_loop_state") or patch.get("correction_state") or {}
    if isinstance(correction_state, Mapping):
        corr_iteration = int(correction_state.get("iteration", 0) or 0)
        corr_reason = correction_state.get("terminated_reason")
    else:
        corr_iteration = 0
        corr_reason = None

    eval_passed = eval_report.passed if eval_report is not None else None
    eval_score = eval_report.total_score if eval_report is not None else None

    return {
        "safety_passed": safety_passed,
        "corrected": corrected,
        "num_qa_failed": num_qa_failed,
        "num_blocking_safety_findings": num_blocking_safety,
        "correction_iterations": corr_iteration,
        "correction_terminated_reason": corr_reason,
        "council_size": council_size,
        "correction_max_iterations": correction_max_iterations,
        "golden_eval_passed": eval_passed,
        "golden_eval_score": eval_score,
    }


# ============================================================================
# 2. Core simulation primitives
# ============================================================================


@dataclass
class SimulationKnobs:
    """
    Concrete knob settings used for a simulation run.

    This mirrors Phase3Knobs but stays local to the simulation layer.
    """

    hyde_enabled: bool
    rrf_strategy: RRFStrategy
    rrf_weights: Optional[Mapping[str, float]]
    council_size: int
    correction_loop_max_iterations: int
    telemetry_routing_mode: TelemetryRoutingMode

    @classmethod
    def from_scenario_knobs(cls, knobs: ScenarioKnobs) -> "SimulationKnobs":
        return cls(
            hyde_enabled=bool(knobs.hyde_enabled),
            rrf_strategy=RRFStrategy(knobs.rrf_strategy),
            rrf_weights=knobs.rrf_weights,
            council_size=int(knobs.council_size),
            correction_loop_max_iterations=int(knobs.correction_loop_max_iterations),
            telemetry_routing_mode=TelemetryRoutingMode(knobs.telemetry_routing_mode),
        )

    def to_kwargs(self) -> Dict[str, Any]:
        return {
            "hyde_enabled": self.hyde_enabled,
            "rrf_strategy": self.rrf_strategy,
            "rrf_weights": self.rrf_weights,
            "council_size": self.council_size,
            "correction_loop_max_iterations": self.correction_loop_max_iterations,
            "telemetry_routing_mode": self.telemetry_routing_mode,
        }


@dataclass
class SimulationResult:
    """
    Structured result for a single simulation run.
    """

    scenario_id: str
    description: str
    workflow_id: Optional[str]
    knobs: SimulationKnobs
    outcome: Dict[str, Any]
    telemetry: Dict[str, Any]
    eval_report: Optional[EvalReport]
    state_patch: Mapping[str, Any]
    snapshot: Mapping[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "description": self.description,
            "workflow_id": self.workflow_id,
            "knobs": {
                "hyde_enabled": self.knobs.hyde_enabled,
                "rrf_strategy": self.knobs.rrf_strategy.value,
                "rrf_weights": dict(self.knobs.rrf_weights) if self.knobs.rrf_weights else None,
                "council_size": self.knobs.council_size,
                "correction_loop_max_iterations": self.knobs.correction_loop_max_iterations,
                "telemetry_routing_mode": self.knobs.telemetry_routing_mode.value,
            },
            "outcome": self.outcome,
            "telemetry": self.telemetry,
            "eval_report": self.eval_report.model_dump() if self.eval_report else None,
            "state_patch": dict(self.state_patch),
            "snapshot": dict(self.snapshot),
        }


async def _run_with_golden_scenario(
    golden: GoldenScenario,
    overrides: Optional[Dict[str, Any]] = None,
) -> SimulationResult:
    """
    Run a single GoldenScenario through the real entrypoint and evaluate it.
    """
    overrides = overrides or {}

    user_request: Any = overrides.get("user_request") or {
        "objective": f"Golden scenario {golden.scenario_id}",
        "scenario_id": golden.scenario_id,
        "description": golden.description,
    }

    # Allow callers to override profile wiring without touching runtime code.
    execution_profile_name = overrides.get("execution_profile_name", "default")
    routing_policy_name = overrides.get("routing_policy_name", "default")
    sandbox_profile_name = overrides.get("sandbox_profile_name", "default")
    meta_profile_name = overrides.get("meta_profile_name", "default")
    extra_workflow_metadata = overrides.get("extra_workflow_metadata")

    sim_knobs = SimulationKnobs.from_scenario_knobs(golden.knobs)

    # Phase-4: emit scenario_start before running.
    emit_scenario_start_event(
        workflow_id=None,
        scenario_id=golden.scenario_id,
        description=golden.description,
    )

    try:
        raw_output = run_workflow(
            user_request,
            execution_profile_name=execution_profile_name,
            routing_policy_name=routing_policy_name,
            sandbox_profile_name=sandbox_profile_name,
            meta_profile_name=meta_profile_name,
            **sim_knobs.to_kwargs(),
            extra_workflow_metadata=extra_workflow_metadata,
        )
        result_map = _as_mapping(raw_output)
        patch = _extract_state_patch(result_map)
        snapshot = _build_snapshot(result_map)

        eval_report = evaluate_patch(patch, golden.expectation)

        telemetry = _summarise_telemetry(result_map, patch)
        outcome = _summarise_outcome(
            result_map,
            patch,
            eval_report=eval_report,
            council_size=sim_knobs.council_size,
            correction_max_iterations=sim_knobs.correction_loop_max_iterations,
        )

        workflow_id = result_map.get("workflow_id")
    except Exception as exc:  # pragma: no cover - defensive path
        # On failure we still return a structured SimulationResult so the
        # batch as a whole can be analysed.
        patch = {}
        snapshot = {}
        telemetry = {"has_telemetry": False, "num_events": 0, "counts": {}}
        outcome = {
            "safety_passed": False,
            "corrected": False,
            "num_qa_failed": 0,
            "num_blocking_safety_findings": 0,
            "correction_iterations": 0,
            "correction_terminated_reason": f"error:{exc}",
            "council_size": sim_knobs.council_size,
            "correction_max_iterations": sim_knobs.correction_loop_max_iterations,
            "golden_eval_passed": False,
            "golden_eval_score": 0.0,
        }
        eval_report = None
        workflow_id = None

    sim_result = SimulationResult(
        scenario_id=golden.scenario_id,
        description=golden.description,
        workflow_id=workflow_id,
        knobs=sim_knobs,
        outcome=outcome,
        telemetry=telemetry,
        eval_report=eval_report,
        state_patch=patch,
        snapshot=snapshot,
    )

    # Phase-4: emit scenario_end + scenario_simulation (best-effort only).
    try:
        emit_scenario_end_event(
            workflow_id=sim_result.workflow_id,
            scenario_id=sim_result.scenario_id,
            passed=sim_result.eval_report.passed if sim_result.eval_report else None,
            score=sim_result.eval_report.total_score if sim_result.eval_report else None,
        )

        emit_scenario_simulation_event(
            workflow_id=sim_result.workflow_id,
            scenario_id=sim_result.scenario_id,
            outcome=sim_result.outcome,
            telemetry=sim_result.telemetry,
            error_taxonomy=None,
        )
    except Exception:
        # Observability must never break simulation.
        pass

    return sim_result


async def _run_knob_matrix_async(
    user_request: Any,
    *,
    hyde_values: Sequence[bool] = (False, True),
    council_sizes: Sequence[int] = (1, 3),
    correction_depths: Sequence[int] = (0, 1, 2),
    telemetry_modes: Sequence[str] = ("log_only", "enforced"),
    execution_profile_name: str = "default",
    routing_policy_name: str = "default",
    sandbox_profile_name: str = "default",
    meta_profile_name: str = "default",
) -> Dict[str, SimulationResult]:
    """
    Run a matrix of simulations across the HYDE / council / correction /
    telemetry dimensions.

    This uses the same run_workflow entrypoint as the golden scenarios but
    does not attach a GoldenExpectation. It is intended for stress-testing
    and diagnostics (e.g., ensuring no combination explodes).
    """
    results: Dict[str, SimulationResult] = {}

    for hyde_enabled, council_size, depth, telemetry_mode in product(
        hyde_values, council_sizes, correction_depths, telemetry_modes
    ):
        scenario_id = (
            f"matrix_hyde_{'on' if hyde_enabled else 'off'}"
            f"__council_{council_size}"
            f"__corr_{depth}"
            f"__telemetry_{telemetry_mode}"
        )

        sim_knobs = SimulationKnobs(
            hyde_enabled=bool(hyde_enabled),
            rrf_strategy=RRFStrategy.SIMPLE,
            rrf_weights=None,
            council_size=int(council_size),
            correction_loop_max_iterations=int(depth),
            telemetry_routing_mode=TelemetryRoutingMode(telemetry_mode),
        )

        # Phase-4: emit scenario_start for matrix scenario.
        emit_scenario_start_event(
            workflow_id=None,
            scenario_id=scenario_id,
            description="HYDE/council/correction/telemetry matrix scenario",
        )

        try:
            raw_output = run_workflow(
                user_request,
                execution_profile_name=execution_profile_name,
                routing_policy_name=routing_policy_name,
                sandbox_profile_name=sandbox_profile_name,
                meta_profile_name=meta_profile_name,
                **sim_knobs.to_kwargs(),
            )
            result_map = _as_mapping(raw_output)
            patch = _extract_state_patch(result_map)
            snapshot = _build_snapshot(result_map)
            telemetry = _summarise_telemetry(result_map, patch)
            outcome = _summarise_outcome(
                result_map,
                patch,
                eval_report=None,
                council_size=sim_knobs.council_size,
                correction_max_iterations=sim_knobs.correction_loop_max_iterations,
            )
            workflow_id = result_map.get("workflow_id")
        except Exception as exc:  # pragma: no cover - defensive path
            patch = {}
            snapshot = {}
            telemetry = {"has_telemetry": False, "num_events": 0, "counts": {}}
            outcome = {
                "safety_passed": False,
                "corrected": False,
                "num_qa_failed": 0,
                "num_blocking_safety_findings": 0,
                "correction_iterations": 0,
                "correction_terminated_reason": f"error:{exc}",
                "council_size": sim_knobs.council_size,
                "correction_max_iterations": sim_knobs.correction_loop_max_iterations,
                "golden_eval_passed": None,
                "golden_eval_score": None,
            }
            workflow_id = None

        sim_result = SimulationResult(
            scenario_id=scenario_id,
            description=(
                "Matrix scenario for HYDE / council / correction / telemetry "
                "combination."
            ),
            workflow_id=workflow_id,
            knobs=sim_knobs,
            outcome=outcome,
            telemetry=telemetry,
            eval_report=None,
            state_patch=patch,
            snapshot=snapshot,
        )

        # Phase-4: emit scenario_end + scenario_simulation for matrix scenario.
        try:
            emit_scenario_end_event(
                workflow_id=sim_result.workflow_id,
                scenario_id=sim_result.scenario_id,
                passed=None,
                score=None,
            )

            emit_scenario_simulation_event(
                workflow_id=sim_result.workflow_id,
                scenario_id=sim_result.scenario_id,
                outcome=sim_result.outcome,
                telemetry=sim_result.telemetry,
                error_taxonomy=None,
            )
        except Exception:
            # Observability must never break simulation.
            pass

        results[scenario_id] = sim_result

    return results


def run_knob_matrix_sync(
    user_request: Any,
    *,
    hyde_values: Sequence[bool] = (False, True),
    council_sizes: Sequence[int] = (1, 3),
    correction_depths: Sequence[int] = (0, 1, 2),
    telemetry_modes: Sequence[str] = ("log_only", "enforced"),
    execution_profile_name: str = "default",
    routing_policy_name: str = "default",
    sandbox_profile_name: str = "default",
    meta_profile_name: str = "default",
) -> Dict[str, Dict[str, Any]]:
    """
    Synchronous convenience wrapper for the knob-matrix simulation.
    """
    results = asyncio.run(
        _run_knob_matrix_async(
            user_request,
            hyde_values=hyde_values,
            council_sizes=council_sizes,
            correction_depths=correction_depths,
            telemetry_modes=telemetry_modes,
            execution_profile_name=execution_profile_name,
            routing_policy_name=routing_policy_name,
            sandbox_profile_name=sandbox_profile_name,
            meta_profile_name=meta_profile_name,
        )
    )
    return {sid: res.to_dict() for sid, res in results.items()}


# ============================================================================
# 3. Engine abstraction (maintains compatibility with previous tests)
# ============================================================================

# Engine exposes only the *golden* scenarios by default. The knob-matrix
# helper above can be used separately for stress tests.


SCENARIO_REGISTRY: Dict[str, GoldenScenario] = dict(GOLDEN_SCENARIOS)


class Engine:
    """
    Simulation execution engine for v10_10.

    Provides:
        • run(name, overrides=None)
        • run_all()
        • list()
        • synchronous wrappers
    """

    @staticmethod
    async def run(
        name: str,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if name not in SCENARIO_REGISTRY:
            raise ValueError(f"Unknown simulation scenario: {name!r}")

        golden = SCENARIO_REGISTRY[name]
        result = await _run_with_golden_scenario(golden, overrides=overrides)
        return result.to_dict()

    @staticmethod
    async def run_all(
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        overrides = overrides or {}
        results: Dict[str, Dict[str, Any]] = {}
        for name, golden in SCENARIO_REGISTRY.items():
            sim_result = await _run_with_golden_scenario(golden, overrides=overrides)
            results[name] = sim_result.to_dict()
        return results

    @staticmethod
    def run_sync(
        name: str,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return asyncio.run(Engine.run(name, overrides=overrides))

    @staticmethod
    def run_all_sync(
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        return asyncio.run(Engine.run_all(overrides=overrides))

    @staticmethod
    def list() -> Dict[str, str]:
        """
        Return a mapping of scenario_id → human-readable description.
        """
        return {name: golden.description for name, golden in SCENARIO_REGISTRY.items()}


# ============================================================================
# 4. Batch helper (optional, uses run_batch_v10_10)
# ============================================================================


def run_batch_simulation(
    jobs: Sequence[Mapping[str, Any]],
    *,
    execution_profile_name: str = "default",
    routing_policy_name: str = "default",
    sandbox_profile_name: str = "default",
    meta_profile_name: str = "default",
    knobs: Optional[SimulationKnobs] = None,
) -> Tuple[Sequence[BatchJobResult], BatchTelemetrySummary]:
    """
    Convenience wrapper around run_batch_v10_10.run_batch for tests.

    It accepts a list of jobs (already structured for the main entrypoint)
    and optional SimulationKnobs. It returns whatever the underlying
    run_batch implementation returns, without modification.
    """
    knob_kwargs: Dict[str, Any] = {}
    if knobs is not None:
        knob_kwargs = knobs.to_kwargs()

    return run_batch(
        jobs,
        execution_profile_name=execution_profile_name,
        routing_policy_name=routing_policy_name,
        sandbox_profile_name=sandbox_profile_name,
        meta_profile_name=meta_profile_name,
        **knob_kwargs,
    )


# ============================================================================
# 5. CLI entrypoint
# ============================================================================


def _cli() -> None:
    import argparse
    import json as _json

    parser = argparse.ArgumentParser(
        description="v10_10 Phase-3 simulation harness (golden scenarios + knob matrix)."
    )
    parser.add_argument(
        "--matrix",
        action="store_true",
        help="Run the HYDE/council/correction/telemetry knob matrix instead of the golden scenarios.",
    )
    parser.add_argument(
        "--prompt",
        required=False,
        help="Optional free-form prompt/user_request text for simulations.",
    )

    args = parser.parse_args()

    user_request: Any
    if args.prompt:
        user_request = args.prompt
    else:
        user_request = {
            "objective": "Run v10_10 Phase-3 simulation.",
            "messages": [
                {
                    "role": "user",
                    "content": "Please run the v10_10 workflow for simulation.",
                }
            ],
        }

    if args.matrix:
        results = run_knob_matrix_sync(user_request)
        print(_json.dumps(results, indent=2, sort_keys=True))
        return

    # Default: run all golden scenarios.
    print("=== v10_10 Simulation Harness (Golden Scenarios) ===")
    print("Available Scenarios:")
    for name, desc in Engine.list().items():
        print(f"  - {name}: {desc or '(no description)'}")

    print("\n=== Running All Golden Scenarios ===")
    results = Engine.run_all_sync()
    print(_json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":  # pragma: no cover - CLI path
    _cli()




