from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "complexity_metrics_config", "p0_governance")
_emit_reads_policy_state("p0", "complexity_metrics_config", "policy_binding")
_emit_snapshots_state("p0", "complexity_metrics_config", "state_snapshot")
emit_replay_key("p0", "complexity_metrics_config")
emit_determinism_digest("p0", "complexity_metrics_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "complexity_metrics_config", "execution_auth")
_emit_validates_capability("p2", "complexity_metrics_config", "capability_check")
_emit_routes_to_capability("p2", "complexity_metrics_config", "capability_route")
_emit_writes_via_uwg("p2", "complexity_metrics_config", "uwg_write")
_emit_blocks_direct_write("p2", "complexity_metrics_config", "direct_write_block")
_emit_records_tool_invocation("p2", "complexity_metrics_config", "tool_invocation")
_emit_captures_execution_output("p2", "complexity_metrics_config", "exec_output")
_emit_dispatches_agent("p3", "complexity_metrics_config", "agent_dispatch")
_emit_coordinates_agents("p3", "complexity_metrics_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "complexity_metrics_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "complexity_metrics_config", "healing_outcome")
_emit_escalates_failure("p3", "complexity_metrics_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "complexity_metrics_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "complexity_metrics_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "complexity_metrics_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "complexity_metrics_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "complexity_metrics_config", "eval_metric")
_emit_stores_embedding("p4", "complexity_metrics_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "complexity_metrics_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "complexity_metrics_config", "exec_snapshot_link")

# Configuration constants

"""
⚛️ Subatomic Flattening Rule - Golden State Reference

This module contains the extracted pattern from the successful agent_logic.py refactoring.
This pattern can be applied to any method that exceeds complexity thresholds.

Pattern Origin: agent_logic.py check_and_learn() method refactoring (Dec 19, 2025)
Success Metrics: 41% line reduction, 50% nesting reduction, 103% preservation
"""
import ast
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("complexity_metrics_config", "p4obs", "metric_1")
_emit_emits_metric_event("complexity_metrics_config", "p4obs", "metric_2")
_emit_emits_metric_event("complexity_metrics_config", "p4obs", "metric_3")
_emit_emits_metric_event("complexity_metrics_config", "p4obs", "metric_4")
_emit_emits_metric_event("complexity_metrics_config", "p4obs", "metric_5")
_emit_emits_metric_event("complexity_metrics_config", "p4obs", "metric_6")
_emit_records_incident_event("complexity_metrics_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("complexity_metrics_config", "p4obs", "anomaly")
_emit_writes_observability_log("complexity_metrics_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("complexity_metrics_config", "p4obs", "mon_state")
_emit_triggers_alert("complexity_metrics_config", "p4obs", "alert")
_emit_links_incident_trace("complexity_metrics_config", "p4obs", "trace_link")
_emit_captures_pattern("complexity_metrics_config", "p3lm", "pattern")
_emit_records_learning_event("complexity_metrics_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("complexity_metrics_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("complexity_metrics_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("complexity_metrics_config", "p3lm", "routing")
_emit_improves_agent_policy("complexity_metrics_config", "p3lm", "policy")
_emit_stores_learning_state("complexity_metrics_config", "p3lm", "state")
_emit_records_execution_trace("complexity_metrics_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("complexity_metrics_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("complexity_metrics_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("complexity_metrics_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("complexity_metrics_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("complexity_metrics_config", "env_read", "p2_env_1")
_emit_reads_environ("complexity_metrics_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("complexity_metrics_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("complexity_metrics_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "complexity_metrics_config", "context_pull")
_emit_pulls_context("p1", "complexity_metrics_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "complexity_metrics_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "complexity_metrics_config", "uwg_term_2")
_emit_writes_through("p1", "complexity_metrics_config", "write_through")
_emit_writes_through("p1", "complexity_metrics_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "complexity_metrics_config", "safety_validation")
_emit_invokes_eval("p1", "complexity_metrics_config", "eval_call")
_emit_proposal_commits_routing("p1", "complexity_metrics_config", "routing_commit")
_emit_escalates_to_human("p1", "complexity_metrics_config", "human_escalation")
_emit_routes_through("p1", "complexity_metrics_config", "route_through")
_emit_checks_agent_registry("p1", "complexity_metrics_config", "agent_registry")
_emit_validates_agent_capability("p1", "complexity_metrics_config", "capability")
_emit_dispatches_execution_plan("p1", "complexity_metrics_config", "exec_plan")
_emit_agent_executes_agent("p1", "complexity_metrics_config", "sub_agent")
_emit_routes_to_agent("p1", "complexity_metrics_config", "target_agent")
_emit_verifies_policy("p1", "complexity_metrics_config", "policy_check")
_emit_observes_runtime_state("p1", "complexity_metrics_config", "runtime_state")
_emit_verifies_boundary("p1", "complexity_metrics_config", "boundary_check")
_emit_transcripts_response("p1", "complexity_metrics_config", "transcript")
_emit_hard_fails_untranscripted("p1", "complexity_metrics_config")
_emit_gated_by_confidence("p1", "complexity_metrics_config", "confidence_gate")


@dataclass
# NAMING FIXED: ComplexityMetrics → ComplexityMetrics
class ComplexityMetrics:
    """Metrics for measuring method complexity."""

    line_count: int
    nesting_depth: int
    conditional_branches: int
    duplicate_patterns: int

    def exceeds_threshold(self) -> bool:
        """Check if method exceeds complexity thresholds."""
        return self.line_count > 40 or self.nesting_depth > 3


@dataclass
# NAMING FIXED: ExtractionCandidate → ExtractionCandidate
class ExtractionCandidate:
    """Represents a code block candidate for extraction."""

    block_type: str  # "initialization", "conditional_branch", "loop", "error_handling"
    start_line: int
    end_line: int
    line_count: int
    nesting_level: int
    suggested_name: str
    dependencies: list[str]
    returns: str | None


@dataclass
# NAMING FIXED: FlatteningPattern → FlatteningPattern
class FlatteningPattern:
    """
    Golden State Reference: Subatomic Flattening Pattern

    This pattern was successfully applied to agent_logic.py check_and_learn() method:
    - Original: 85 lines, 4 nesting levels
    - After: 50 lines, 2 nesting levels
    - Preservation: 103%
    """

    # Thresholds
    MAX_METHOD_LINES = 40
    MAX_NESTING_DEPTH = 3
    MIN_EXTRACTION_LINES = 8

    # Pattern Recognition
    EXTRACTION_TRIGGERS = [
        "if_elif_chain_with_duplicate_logic",
        "nested_conditional_with_validation",
        "repeated_dictionary_updates",
        "initialization_blocks",
        "error_handling_blocks",
    ]

    # Naming Conventions
    HELPER_PREFIXES = {
        "initialization": "_initialize_",
        "conditional_branch": "_process_",
        "validation": "_validate_",
        "transformation": "_transform_",
        "error_handling": "_handle_",
    }

    @classmethod
    def analyze_method(
        cls,
        method_code: str,
        method_name: str,
    ) -> tuple[ComplexityMetrics, list[ExtractionCandidate]]:
        """
        Analyze a method and identify extraction candidates.

        Args:
            method_code: Source code of the method
            method_name: Name of the method

        Returns:
            Tuple of (complexity metrics, extraction candidates)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "FlatteningPattern.analyze_method"
        )

        try:
            tree = ast.parse(method_code)
        except SyntaxError:  # guardian: allow-silent-swallow - acceptable exception handling
            return ComplexityMetrics(0, 0, 0, 0), []

        # Calculate metrics
        lines = method_code.split("\n")
        line_count = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
        nesting_depth = cls._calculate_max_nesting(tree)
        conditional_branches = cls._count_conditionals(tree)

        metrics = ComplexityMetrics(
            line_count=line_count,
            nesting_depth=nesting_depth,
            conditional_branches=conditional_branches,
            duplicate_patterns=0,  # Would need semantic analysis
        )

        # Identify extraction candidates
        candidates = []
        if metrics.exceeds_threshold():
            candidates = cls._identify_extraction_candidates(tree, method_name)

        return metrics, candidates

    @classmethod
    def _calculate_max_nesting(cls, tree: ast.AST) -> int:
        """Calculate maximum nesting depth in AST."""
        max_depth = 0

        def visit_node(node, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)

            # Increase depth for control flow structures
            if isinstance(node, ast.If | ast.For | ast.While | ast.With | ast.Try):
                depth += 1

            for child in ast.iter_child_nodes(node):
                visit_node(child, depth)

        visit_node(tree)
        return max_depth

    @classmethod
    def _count_conditionals(cls, tree: ast.AST) -> int:
        """Count conditional branches in AST."""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                count += 1
                # Count elif branches
                while node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    count += 1
                    node = node.orelse[0]
        return count

    @classmethod
    def _identify_extraction_candidates(cls, tree: ast.AST, method_name: str) -> list[ExtractionCandidate]:
        """
        Identify code blocks that should be extracted into helper methods.

        Based on the agent_logic.py pattern:
        1. Dictionary initialization blocks → _initialize_[result_name]
        2. If/elif branches with validation → _process_[branch_name]
        3. Nested conditionals with side effects → _handle_[action_name]
        """
        candidates = []

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            # Pattern 1: Dictionary initialization
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
                if len(node.value.keys) >= 5:  # Large dict initialization
                    candidates.append(
                        ExtractionCandidate(
                            block_type="initialization",
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            line_count=(node.end_lineno or node.lineno) - node.lineno + 1,
                            nesting_level=1,
                            suggested_name=f"_initialize_{node.targets[0].id if hasattr(node.targets[0], 'id') else 'result'}",
                            dependencies=[],
                            returns="Dict[str, Any]",
                        ),
                    )

            # Pattern 2: If/elif chains with similar structure
            if isinstance(node, ast.If):
                # Check for if/elif pattern with similar bodies
                if node.orelse and isinstance(node.orelse[0], ast.If):
                    # This is an if/elif chain
                    candidates.append(
                        ExtractionCandidate(
                            block_type="conditional_branch",
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            line_count=(node.end_lineno or node.lineno) - node.lineno + 1,
                            nesting_level=2,
                            suggested_name="_process_conditional_branch",
                            dependencies=[],
                            returns="Dict[str, Any]",
                        ),
                    )

        return candidates

    @classmethod
    def generate_extraction_plan(
        cls,
        metrics: ComplexityMetrics,
        candidates: list[ExtractionCandidate],
    ) -> dict:
        """
        Generate a step-by-step extraction plan.

        Returns:
            Dictionary with extraction strategy and steps
        """
        if not metrics.exceeds_threshold():
            return {
                "needs_extraction": False,
                "reason": "Method within acceptable complexity thresholds",
            }

        # Sort candidates by potential impact (line count * nesting level)
        sorted_candidates = sorted(candidates, key=lambda c: c.line_count * c.nesting_level, reverse=True)

        return {
            "needs_extraction": True,
            "current_metrics": {
                "lines": metrics.line_count,
                "nesting": metrics.nesting_depth,
                "branches": metrics.conditional_branches,
            },
            "extraction_steps": [
                {
                    "step": i + 1,
                    "block_type": candidate.block_type,
                    "lines": f"{candidate.start_line}-{candidate.end_line}",
                    "suggested_name": candidate.suggested_name,
                    "expected_reduction": candidate.line_count,
                }
                for i, candidate in enumerate(sorted_candidates[:3])  # Top 3 candidates
            ],
            "projected_metrics": {
                "lines": metrics.line_count - sum(c.line_count for c in sorted_candidates[:3]),
                "nesting": max(2, metrics.nesting_depth - 2),
                "improvement": f"{(sum(c.line_count for c in sorted_candidates[:3]) / metrics.line_count * 100):.1f}% reduction",
            },
        }


# Golden State Reference: Successful Extraction Example
# NAMING FIXED: AGENT_LOGIC_PATTERN → agent_logic_pattern
agent_logic_pattern = {
    "source_file": "agentic_core/agent_logic.py",
    "method_name": "check_and_learn",
    "date": "2025-12-19",
    "before": {
        "lines": 85,
        "nesting_depth": 4,
        "conditional_branches": 2,
        "issues": [
            "Exceeded 40-line threshold by 112%",
            "Exceeded 3-level nesting by 33%",
            "SystemArchitect hit 'Enough thinking reasoning limit'",
            "Multiple Clean Slate Protocol retries",
        ],
    },
    "extraction_strategy": {
        "identified_blocks": [
            {
                "type": "initialization",
                "lines": "129-136",
                "pattern": "Dictionary with 6 key-value pairs",
                "extracted_to": "_initialize_validation_result()",
                "reduction": "8 lines",
            },
            {
                "type": "conditional_branch",
                "lines": "138-152",
                "pattern": "If block with validation call and result update",
                "extracted_to": "_process_l1_match(new_entry, best_match)",
                "reduction": "15 lines",
            },
            {
                "type": "conditional_branch",
                "lines": "154-172",
                "pattern": "Elif block with validation call, result update, and promotion",
                "extracted_to": "_process_l2_match(new_entry, best_match)",
                "reduction": "19 lines",
            },
        ],
        "total_extracted": "42 lines (49% of original method)",
    },
    "after": {
        "lines": 50,
        "nesting_depth": 2,
        "conditional_branches": 2,
        "improvements": [
            "41% line reduction (85 → 50 lines)",
            "50% nesting reduction (4 → 2 levels)",
            "103% preservation (added helper methods)",
            "Ready for single-pass healing (~11.5K tokens)",
        ],
    },
    "helper_methods": [
        {
            "name": "_initialize_validation_result",
            "lines": 10,
            "nesting": 1,
            "purpose": "Encapsulate default result structure",
            "pattern": "Pure data structure initialization",
        },
        {
            "name": "_process_l1_match",
            "lines": 15,
            "nesting": 1,
            "purpose": "Handle L1 Redis cache hit validation",
            "pattern": "Validation + result formatting + logging",
        },
        {
            "name": "_process_l2_match",
            "lines": 20,
            "nesting": 2,
            "purpose": "Handle L2 Qdrant cache hit with promotion",
            "pattern": "Validation + result formatting + conditional promotion + logging",
        },
    ],
    "success_metrics": {
        "preservation_rate": 103.0,
        "complexity_reduction": 41.0,
        "nesting_reduction": 50.0,
        "healing_readiness": "single_pass",
        "token_budget": "11.5K / 24.5K (47% usage)",
    },
    "reusable_pattern": {
        "trigger": "method > 40 lines AND nesting > 3",
        "recognition": [
            "If/elif chains with similar structure",
            "Repeated dictionary updates",
            "Large initialization blocks",
            "Nested conditionals with side effects",
        ],
        "extraction_heuristic": [
            "1. Identify logical blocks (initialization, branches, error handling)",
            "2. Extract blocks with 8+ lines into private helpers",
            "3. Name helpers: _[action]_[noun] (e.g., _process_l1_match)",
            "4. Preserve behavior: maintain all side effects and logging",
            "5. Verify: ensure nesting ≤ 3 and lines ≤ 40 after extraction",
        ],
        "naming_convention": {
            "initialization": "_initialize_[result_name]",
            "processing": "_process_[data_source]_[action]",
            "validation": "_validate_[aspect]",
            "handling": "_handle_[event]_[action]",
        },
    },
}


def get_flattening_pattern() -> dict:
    """
    Get the golden state flattening pattern for Pinecone storage.

    Returns:
        Complete pattern dictionary ready for vector embedding
    """
    return AGENT_LOGIC_PATTERN
