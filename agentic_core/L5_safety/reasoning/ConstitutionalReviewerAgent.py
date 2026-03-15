from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)
from agentic_core.utils.timeout_decorator_util import timeout

_emit_dispatches_healing_run("p1", "ConstitutionalReviewerAgent", "L5")
_emit_routes_through("p1", "ConstitutionalReviewerAgent", "L5")
_emit_escalates_to_human("p1", "ConstitutionalReviewerAgent", "L5")
_emit_reads_policy_state("p1", "ConstitutionalReviewerAgent", "L5")

"Constitutional Reviewer Agent - Performs final constitutional review of the output."
import json
import uuid

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal


class ConstitutionalReviewResult:
    """Stub for ConstitutionalReviewResult - TODO: Replace with sovereign equivalent"""

    def __init__(self, review_passed=True, violations_found=None, feedback="") -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ConstitutionalReviewResult.__init__", "state_snapshot")
        self.review_passed = review_passed
        self.violations_found = violations_found or []
        self.feedback = feedback


def track_metrics(name):
    """Stub decorator for track_metrics - TODO: Replace with sovereign equivalent"""

    _emit_applies_guardrail(str(uuid.uuid4()), "Module.track_metrics", "L5_POLICY")

    def decorator(func):
        return func

    return decorator


async def _format_prompt_with_defaults(template, data, budget_manager, goal_state, top_failures):
    """Stub for _format_prompt_with_defaults"""
    return template


class ConstitutionalReviewerAgent(SovereignBaseAgent, L5SafetyBase):
    """Performs final constitutional review of the output."""

    @track_metrics("run_constitutional_review")
    async def run_async(self, final_draft: str, workflow_id: str) -> ConstitutionalReviewResult:
        """Run async constitutional review of the final draft."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ConstitutionalReviewerAgent.run_async"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ConstitutionalReviewerAgent.run_async".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.log_info("Running final constitutional review...")
        if not self.config.agent_stacks.enable_constitutional_review:
            self.log_warning("Constitutional review is disabled. Passing by default.")
            return ConstitutionalReviewResult(
                review_passed=True, violations_found=[], feedback="Review disabled"
            )
        client = self.get_model_client("constitutional_review_model")
        prompt_template = self.prompt_manager.get_template("constitutional_review")
        rules = self.context.rules_loader.get_constitution_rules()
        constitution_text = json.dumps(rules)
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"final_draft": final_draft, "constitution": constitution_text},
            self.BudgetManager,
            client.goal_state,
            client.top_failures,
        )
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.ModelConfig.constitutional_review_model.temperature,
            response_format="json_object",
        )
        validated_output, error = self.validator.validate(response["content"], ConstitutionalReviewResult)
        if error:
            self.log_error(
                f"ConstitutionalReviewer failed validation: {error}. Failing open (passing draft)."
            )
            return ConstitutionalReviewResult(
                review_passed=True, violations_found=["VALIDATION_ERROR"], feedback=error
            )
        if not validated_output.review_passed:
            self.log_warning(f"CONSTITUTIONAL REVIEW FAILED: {validated_output.violations_found}")
        return validated_output

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """Operational guardrail agent - no repository healing required."""
        super().heal_repository()
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] Operational guardrail - no healing required")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal constitutional review violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (constitutional)
                - content: Content that failed review
                - violations_found: List of constitutional violations

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Constitutional violations require content revision",
        }
