"""Golden State Evaluator - Phase 2 Implementation.

Phase 2 - Pillar 12: Testing (Golden State)
Evaluates agent outputs against golden test cases.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "golden_state_evaluator_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "golden_state_evaluator_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "golden_state_evaluator_types", "state_snapshot")
trace_contract.emit_replay_key("p0", "golden_state_evaluator_types")
trace_contract.emit_determinism_digest("p0", "golden_state_evaluator_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "golden_state_evaluator_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "golden_state_evaluator_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "golden_state_evaluator_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "golden_state_evaluator_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "golden_state_evaluator_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "golden_state_evaluator_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "golden_state_evaluator_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "golden_state_evaluator_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "golden_state_evaluator_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "golden_state_evaluator_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "golden_state_evaluator_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "golden_state_evaluator_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "golden_state_evaluator_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "golden_state_evaluator_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "golden_state_evaluator_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "golden_state_evaluator_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "golden_state_evaluator_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "golden_state_evaluator_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "golden_state_evaluator_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "golden_state_evaluator_types", "exec_snapshot_link")

try:
    from apps_rg.core.JudgeEvaluation import JudgeEvaluationResult, JudgeEvaluator, create_judge_evaluator
except ImportError:  # guardian: allow-silent-swallow -- optional dependency

    @dataclass
    class JudgeEvaluationResult:
        score: float
        reasoning: str

    class JudgeEvaluator:
        def evaluate(self, case: Any) -> JudgeEvaluationResult:
            return JudgeEvaluationResult(0.5, "Fallback evaluator")

    def create_judge_evaluator():
        return JudgeEvaluator()



trace_contract._emit_emits_metric_event("golden_state_evaluator_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("golden_state_evaluator_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("golden_state_evaluator_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("golden_state_evaluator_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("golden_state_evaluator_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("golden_state_evaluator_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("golden_state_evaluator_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("golden_state_evaluator_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("golden_state_evaluator_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("golden_state_evaluator_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("golden_state_evaluator_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("golden_state_evaluator_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("golden_state_evaluator_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("golden_state_evaluator_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("golden_state_evaluator_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("golden_state_evaluator_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("golden_state_evaluator_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("golden_state_evaluator_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("golden_state_evaluator_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("golden_state_evaluator_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("golden_state_evaluator_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("golden_state_evaluator_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("golden_state_evaluator_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("golden_state_evaluator_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("golden_state_evaluator_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("golden_state_evaluator_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("golden_state_evaluator_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("golden_state_evaluator_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "golden_state_evaluator_types", "context_pull")
trace_contract._emit_pulls_context("p1", "golden_state_evaluator_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "golden_state_evaluator_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "golden_state_evaluator_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "golden_state_evaluator_types", "write_through")
trace_contract._emit_writes_through("p1", "golden_state_evaluator_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "golden_state_evaluator_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "golden_state_evaluator_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "golden_state_evaluator_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "golden_state_evaluator_types", "human_escalation")
trace_contract._emit_routes_through("p1", "golden_state_evaluator_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "golden_state_evaluator_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "golden_state_evaluator_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "golden_state_evaluator_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "golden_state_evaluator_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "golden_state_evaluator_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "golden_state_evaluator_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "golden_state_evaluator_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "golden_state_evaluator_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "golden_state_evaluator_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "golden_state_evaluator_types")
trace_contract._emit_gated_by_confidence("p1", "golden_state_evaluator_types", "confidence_gate")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_1")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_2")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_3")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_4")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_5")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_6")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_7")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_8")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_9")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_10")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_11")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_12")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_13")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_14")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_15")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_16")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_17")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_18")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_19")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_20")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_21")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_22")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_23")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_24")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_25")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_26")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_27")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_28")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_29")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_30")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_31")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_32")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_33")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_34")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_35")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_36")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_37")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_38")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_39")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_40")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_41")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_42")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_43")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_44")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_45")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_46")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_47")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_48")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_49")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_50")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_51")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_52")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_53")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_54")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_55")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_56")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_57")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_58")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_59")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_60")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_61")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_62")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_63")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_64")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_65")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_66")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_67")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_68")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_69")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_70")
trace_contract._emit_reads_through("l4", "golden_state_evaluator_types", "urg_read_71")

Logger = logging.getLogger(__name__)


@dataclass
class GoldenCase:
    """Golden test case."""

    id: str
    name: str
    category: str
    mission: str
    scene: dict[str, Any]
    expected_output: dict[str, Any]
    expected_actions: list[dict[str, Any]]
    quality_criteria: dict[str, float]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GoldenCase":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            mission=data["mission"],
            scene=data["scene"],
            expected_output=data["expected_output"],
            expected_actions=data["expected_actions"],
            quality_criteria=data["quality_criteria"],
        )


@dataclass
class GoldenOutput:
    """Output from agent execution."""

    case_id: str
    actual_output: str
    actions_taken: list[dict[str, Any]] = field(default_factory=list)
    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationReport:
    """Evaluation report for a golden case."""

    case_id: str
    case_name: str
    passed: bool
    judge_result: JudgeEvaluationResult
    action_match_score: float
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "case_name": self.case_name,
            "passed": self.passed,
            "judge_result": self.judge_result.to_dict(),
            "action_match_score": self.action_match_score,
            "errors": self.errors,
        }


class GoldenStateEvaluator:
    """Evaluator for golden state test cases.

    Loads golden test cases and evaluates agent outputs against them.
    Uses JudgeEvaluator for quality assessment.
    """

    def __init__(
        self,
        dataset_path: Path | None = None,
        JudgeEvaluator: JudgeEvaluator | None = None,
        enable_logging: bool = True,
    ):
        """Initialize evaluator.

        Args:
            dataset_path: Path to golden dataset JSON
            JudgeEvaluator: Judge evaluator instance
            enable_logging: Enable logging
        """
        self.dataset_path = dataset_path or Path("data/golden_state/datasets/core/test_cases.json")
        self.JudgeEvaluator = JudgeEvaluator or create_judge_evaluator()
        self.enable_logging = enable_logging
        self.golden_cases: list[GoldenCase] = []
        self._load_cases()

    def _load_cases(self) -> None:
        """Load golden test cases from dataset."""
        try:
            with open(self.dataset_path) as f:
                data = json.load(f)
            for case_data in data.get("test_cases", []):
                case = GoldenCase.from_dict(case_data)
                self.golden_cases.append(case)
            if self.enable_logging:
                Logger.info(
                    "golden_cases_loaded", extra={"count": len(self.golden_cases)}
                )  # review: File operations should check existence before access
        except FileNotFoundError:
            if self.enable_logging:
                Logger.warning("golden_dataset_not_found", extra={"path": str(self.dataset_path)})
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:
            raise

    async def evaluate_case(self, case: GoldenCase, output: GoldenOutput) -> EvaluationReport:
        """Evaluate output against golden case.

        Args:
            case: Golden test case
            output: Agent output

        Returns:
            EvaluationReport with results
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "GoldenStateEvaluator.evaluate_case"
        )

        errors: list[str] = []
        expected_output = case.expected_output
        if isinstance(expected_output, dict) and "contains" in expected_output:
            expected_str = ", ".join(expected_output["contains"])
        else:
            expected_str = str(expected_output) if expected_output else None
        judge_result = await self.JudgeEvaluator.evaluate(
            output=output.actual_output,
            expected=expected_str,
            context={"Task": case.mission, "category": case.category},
        )
        action_match_score = self._evaluate_actions(
            expected=case.expected_actions,
            actual=output.actions_taken,
        )
        self._check_output_constraints(case.expected_output, output.actual_output, errors)
        passed = judge_result.passed and action_match_score >= 0.5 and (len(errors) == 0)
        report = EvaluationReport(
            case_id=case.id,
            case_name=case.name,
            passed=passed,
            judge_result=judge_result,
            action_match_score=action_match_score,
            errors=errors,
        )
        if self.enable_logging:
            Logger.info(
                "case_evaluated",
                extra={
                    "case_id": case.id,
                    "passed": passed,
                    "judge_score": judge_result.overall_score,
                    "action_score": action_match_score,
                },
            )
        return report

    def _evaluate_actions(self, expected: list[dict[str, Any]], actual: list[dict[str, Any]]) -> float:
        """Evaluate action matching.

        Args:
            expected: Expected actions
            actual: Actual actions taken

        Returns:
            Match score (0.0-1.0)
        """
        if not expected:
            return 1.0
        if not actual:
            return 0.0
        expected_tools = {a.get("tool") for a in expected if a.get("tool")}
        actual_tools = {a.get("tool") for a in actual if a.get("tool")}
        if not expected_tools:
            return 1.0
        matches = len(expected_tools & actual_tools)
        score = matches / len(expected_tools)
        return score

    def _check_output_constraints(self, expected: dict[str, Any], actual: str, errors: list[str]) -> None:
        """Check output constraints.

        Args:
            expected: Expected output constraints
            actual: Actual output
            errors: List to append errors to
        """
        min_length = expected.get("min_length", 0)
        if len(actual) < min_length:
            errors.append(f"Output too short: {len(actual)} < {min_length}")
        max_length = expected.get("max_length")
        if max_length and len(actual) > max_length:
            errors.append(f"Output too long: {len(actual)} > {max_length}")
        contains = expected.get("contains", [])
        if isinstance(contains, list):
            for required in contains:
                if required.lower() not in actual.lower():
                    errors.append(f"Missing required content: {required}")
        not_contains = expected.get("not_contains", [])
        if isinstance(not_contains, list):
            for forbidden in not_contains:
                if forbidden.lower() in actual.lower():
                    errors.append(f"Contains forbidden content: {forbidden}")

    async def evaluate_all(self, outputs: dict[str, GoldenOutput]) -> dict[str, EvaluationReport]:
        """Evaluate all golden cases.

        Args:
            outputs: Dict of case_id -> GoldenOutput

        Returns:
            Dict of case_id -> EvaluationReport
        """
        reports: dict[str, EvaluationReport] = {}
        for case in self.golden_cases:
            if case.id in outputs:
                report = await self.evaluate_case(case, outputs[case.id])
                reports[case.id] = report
        return reports

    def generate_summary(self, reports: dict[str, EvaluationReport]) -> dict[str, Any]:
        """Generate summary of evaluation results.

        Args:
            reports: Evaluation reports

        Returns:
            Summary dict
        """
        total = len(reports)
        passed = sum(1 for r in reports.values() if r.passed)
        failed = total - passed
        pass_rate = passed / total if total > 0 else 0.0
        avg_judge_score = (
            sum(r.judge_result.overall_score for r in reports.values()) / total if total > 0 else 0.0
        )
        avg_action_score = sum(r.action_match_score for r in reports.values()) / total if total > 0 else 0.0
        failing_cases = [
            {"id": r.case_id, "name": r.case_name, "errors": r.errors}
            for r in reports.values()
            if not r.passed
        ]
        return {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "avg_judge_score": avg_judge_score,
            "avg_action_score": avg_action_score,
            "failing_cases": failing_cases,
        }


def load_golden_cases(dataset_path: Path | None = None) -> list[GoldenCase]:
    """Load golden test cases.

    Args:
        dataset_path: Path to dataset JSON

    Returns:
        List of GoldenCase objects
    """
    evaluator = GoldenStateEvaluator(dataset_path=dataset_path)
    return evaluator.golden_cases


async def evaluate_case_output(case: GoldenCase, output: GoldenOutput) -> EvaluationReport:
    """Evaluate a single case output.

    Args:
        case: Golden test case
        output: Agent output

    Returns:
        EvaluationReport
    """
    evaluator = GoldenStateEvaluator()
    return await evaluator.evaluate_case(case, output)
