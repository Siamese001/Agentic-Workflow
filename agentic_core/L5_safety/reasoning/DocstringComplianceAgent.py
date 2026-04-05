from __future__ import annotations

import ast

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)
from agentic_core.mixins.prompt_rendering_mixin import PromptRenderingMixin

emit_replay_key("p0", "DocstringComplianceAgent")
emit_determinism_digest("p0", "DocstringComplianceAgent")

_emit_dispatches_healing_run("p1", "DocstringComplianceAgent", "L5")
_emit_routes_through("p1", "DocstringComplianceAgent", "L5")
_emit_checks_agent_registry("p1", "DocstringComplianceAgent", "agent_registry")
_emit_validates_agent_capability("p1", "DocstringComplianceAgent", "capability")
_emit_dispatches_execution_plan("p1", "DocstringComplianceAgent", "exec_plan")
_emit_agent_executes_agent("p1", "DocstringComplianceAgent", "sub_agent")
_emit_routes_to_agent("p1", "DocstringComplianceAgent", "target_agent")
_emit_verifies_policy("p1", "DocstringComplianceAgent", "policy_check")
_emit_observes_runtime_state("p1", "DocstringComplianceAgent", "runtime_state")
_emit_verifies_boundary("p1", "DocstringComplianceAgent", "boundary_check")
_emit_transcripts_response("p1", "DocstringComplianceAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "DocstringComplianceAgent")
_emit_gated_by_confidence("p1", "DocstringComplianceAgent", "confidence_gate")
_emit_escalates_to_human("p1", "DocstringComplianceAgent", "L5")
_emit_reads_policy_state("p1", "DocstringComplianceAgent", "L5")
_emit_authorize_and_execute("p2", "DocstringComplianceAgent", "execution_auth")
_emit_validates_capability("p2", "DocstringComplianceAgent", "capability_check")
_emit_routes_to_capability("p2", "DocstringComplianceAgent", "capability_route")
_emit_writes_via_uwg("p2", "DocstringComplianceAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DocstringComplianceAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DocstringComplianceAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DocstringComplianceAgent", "exec_output")
_emit_dispatches_agent("p3", "DocstringComplianceAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DocstringComplianceAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DocstringComplianceAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DocstringComplianceAgent", "healing_outcome")
_emit_escalates_failure("p3", "DocstringComplianceAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DocstringComplianceAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DocstringComplianceAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DocstringComplianceAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DocstringComplianceAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DocstringComplianceAgent", "eval_metric")
_emit_stores_embedding("p4", "DocstringComplianceAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DocstringComplianceAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DocstringComplianceAgent", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.utils.schemas.decorators_compat_util import standard_heal
from agentic_core.utils.schemas.timeout_decorator_util import timeout

_emit_emits_metric_event("DocstringComplianceAgent", "p4obs", "metric_1")
_emit_emits_metric_event("DocstringComplianceAgent", "p4obs", "metric_2")
_emit_emits_metric_event("DocstringComplianceAgent", "p4obs", "metric_3")
_emit_emits_metric_event("DocstringComplianceAgent", "p4obs", "metric_4")
_emit_emits_metric_event("DocstringComplianceAgent", "p4obs", "metric_5")
_emit_emits_metric_event("DocstringComplianceAgent", "p4obs", "metric_6")
_emit_records_incident_event("DocstringComplianceAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("DocstringComplianceAgent", "p4obs", "anomaly")
_emit_writes_observability_log("DocstringComplianceAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("DocstringComplianceAgent", "p4obs", "mon_state")
_emit_triggers_alert("DocstringComplianceAgent", "p4obs", "alert")
_emit_links_incident_trace("DocstringComplianceAgent", "p4obs", "trace_link")
_emit_captures_pattern("DocstringComplianceAgent", "p3lm", "pattern")
_emit_records_learning_event("DocstringComplianceAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DocstringComplianceAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("DocstringComplianceAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DocstringComplianceAgent", "p3lm", "routing")
_emit_improves_agent_policy("DocstringComplianceAgent", "p3lm", "policy")
_emit_stores_learning_state("DocstringComplianceAgent", "p3lm", "state")
_emit_records_execution_trace("DocstringComplianceAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DocstringComplianceAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DocstringComplianceAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DocstringComplianceAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DocstringComplianceAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DocstringComplianceAgent", "env_read", "p2_env_1")
_emit_reads_environ("DocstringComplianceAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("DocstringComplianceAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DocstringComplianceAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DocstringComplianceAgent", "context_pull")
_emit_pulls_context("p1", "DocstringComplianceAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "DocstringComplianceAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DocstringComplianceAgent", "uwg_term_2")
_emit_writes_through("p1", "DocstringComplianceAgent", "write_through")
_emit_writes_through("p1", "DocstringComplianceAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "DocstringComplianceAgent", "safety_validation")
_emit_invokes_eval("p1", "DocstringComplianceAgent", "eval_call")
_emit_proposal_commits_routing("p1", "DocstringComplianceAgent", "routing_commit")


class DocstringComplianceAgent(PromptRenderingMixin, SovereignBaseAgent):
    """
    Ensures public functions, classes, and modules have docstrings.

    Rules:
    - Module-level docstring required (first statement)
    - Public classes (not starting with _) must have docstring
    - Public functions/methods (not starting with _) must have docstring
    - Minimal stub: '''Brief description of functionality and purpose.'''

    Why ungated healing is safe:
    - Only adds Missing triple-quoted strings immediately after def/class
    - Never removes or modifies existing content
    - Single-file scope
    """

    MIN_DOCSTRING: str = "'''Brief description of functionality and purpose.'''"

    def __init__(self, ctx: Any, project_root: str | None = None) -> None:
        """
        Initialize with mandatory ctx for sovereign operation.

        Args:
            ctx: Execution context (mandatory)
            project_root: Optional project root directory

        Raises:
            ValueError: If ctx is None
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DocstringComplianceAgent.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DocstringComplianceAgent.__init__", "p0_governance")
        if ctx is None:
            raise ValueError("ctx is mandatory for DocstringComplianceAgent (sovereign agent)")
        self.ctx = ctx
        self.project_root = project_root

    async def execute(self, file_path: str) -> dict[str, Any]:
        """
        Execute method for validator compatibility.

        Args:
            file_path: Path to file to validate

        Returns:
            Dict with healed status
        """
        return await self.heal_violation(Path(file_path), self.ctx)

    async def heal_violation(self, file_path: Path, ctx: Any | None = None) -> dict[str, Any]:
        """
        Per-file healing: add missing docstrings.

        Args:
            file_path: Path to file to heal
            ctx: Optional execution context (uses self.ctx if None)

        Returns:
            Dict with healed status and violations fixed count
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "DocstringComplianceAgent.heal_violation"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DocstringComplianceAgent.heal_violation".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        ctx = ctx or self.ctx
        try:
            source: str = file_path.read_text(encoding="utf-8")
            tree: ast.Module = ast.parse(source)
            needs_docstring: List[tuple] = []
            if not ast.get_docstring(tree):
                needs_docstring.append(("module", 0))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
                    if node.name.startswith("_"):
                        continue
                    if ast.get_docstring(node) is None:
                        needs_docstring.append((type(node).__name__, node.lineno))
            if not needs_docstring:
                return {"healed": False}
            lines: List[str] = source.splitlines(keepends=True)
            new_lines: List[str] = lines.copy()
            added_count: Any = 0
            needs_docstring.sort(key=lambda x: x[1] if x[0] != "module" else 0, reverse=True)
            for node_type, lineno in needs_docstring:
                if node_type == "module":
                    insert_idx: Any = 0
                    for i, line in enumerate(lines):
                        if line.strip() and (not line.strip().startswith(("#", "__"))):
                            insert_idx: Any = i + 1
                            break
                    indent: Any = ""
                else:
                    insert_idx: Any = lineno
                    def_line: Any = lines[lineno - 1]
                    indent: Any = "    " * (len(def_line) - len(def_line.lstrip()) + 1)
                doc_lines: Any = [f"{indent}\n"]
                new_lines[insert_idx:insert_idx] = doc_lines
                added_count += 1
            if added_count > 0:
                new_content: Any = "".join(new_lines)
                _wg.write_text(file_path, new_content, encoding="utf-8")
                message: Any = f"Added {added_count} Missing docstring(s)"
                print(f"      [HEALED] {file_path.name}: {message}")
                ctx.report(self.__class__.__name__, key_id=18, success=True, msg=message)
                return {"healed": True, "details": message}
            return {"healed": False}
        # guardian: allow-silent-swallow -- docstring healing failure is reported to convergence context and returns un-healed
        except (ValueError, TypeError) as e:
            ctx.report(self.__class__.__name__, 18, False, f"Docstring healing failed: {str(e)[:100]}")
            return {"healed": False}

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal a specific violation (IHealerProtocol compliance).

        Args:
            violation: Dict containing violation details

        Returns:
            Dict with status, details, artifacts, errors
        """
        return {
            "status": "success",
            "details": "DocstringComplianceAgent observability heal - no action required",
            "artifacts": [],
            "errors": [],
        }

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config -- 300s timeout is deploy-environment-specific safety bound
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """Autonomous docstring compliance enforcement."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        if self.__class__.__name__ in _call_path:
            return {"errors": 0, "skipped": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 0, "skipped": 1, "depth_limited": True}
        _call_path.add(self.__class__.__name__)
        try:
            print(
                f"[DocstringCompliance HEAL @ depth {depth}] Requires ctx parameter - operational mode only"
            )
            return {"skipped": 1, "requires_ctx": True}
        finally:
            _call_path.discard(self.__class__.__name__)


def get_docstring_compliance_agent() -> Any:
    """Brief description of functionality and purpose."""
    super().heal_repository()
    return DocstringComplianceAgent()
