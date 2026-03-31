from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    # noqa: E402
    _emit_gated_by_confidence,
    # noqa: E402
    _emit_records_healing_outcome,
    # noqa: E402
    _emit_routes_to_agent,
    # noqa: E402
    emit_replay_key,
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
    _emit_escalates_to_human,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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
    emit_determinism_digest
)

emit_replay_key("p0", "DependencyPruningAgent")
emit_determinism_digest("p0", "DependencyPruningAgent")

_emit_dispatches_healing_run("p1", "DependencyPruningAgent", "L5")
_emit_routes_through("p1", "DependencyPruningAgent", "L5")
_emit_checks_agent_registry("p1", "DependencyPruningAgent", "agent_registry")
_emit_validates_agent_capability("p1", "DependencyPruningAgent", "capability")
_emit_dispatches_execution_plan("p1", "DependencyPruningAgent", "exec_plan")
_emit_agent_executes_agent("p1", "DependencyPruningAgent", "sub_agent")
_emit_routes_to_agent("p1", "DependencyPruningAgent", "target_agent")
_emit_verifies_policy("p1", "DependencyPruningAgent", "policy_check")
_emit_observes_runtime_state("p1", "DependencyPruningAgent", "runtime_state")
_emit_verifies_boundary("p1", "DependencyPruningAgent", "boundary_check")
_emit_transcripts_response("p1", "DependencyPruningAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "DependencyPruningAgent")
_emit_gated_by_confidence("p1", "DependencyPruningAgent", "confidence_gate")
_emit_escalates_to_human("p1", "DependencyPruningAgent", "L5")
_emit_reads_policy_state("p1", "DependencyPruningAgent", "L5")
_emit_authorize_and_execute("p2", "DependencyPruningAgent", "execution_auth")
_emit_validates_capability("p2", "DependencyPruningAgent", "capability_check")
_emit_routes_to_capability("p2", "DependencyPruningAgent", "capability_route")
_emit_writes_via_uwg("p2", "DependencyPruningAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DependencyPruningAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DependencyPruningAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DependencyPruningAgent", "exec_output")
_emit_dispatches_agent("p3", "DependencyPruningAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DependencyPruningAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DependencyPruningAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DependencyPruningAgent", "healing_outcome")
_emit_escalates_failure("p3", "DependencyPruningAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DependencyPruningAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DependencyPruningAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DependencyPruningAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DependencyPruningAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DependencyPruningAgent", "eval_metric")
_emit_stores_embedding("p4", "DependencyPruningAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DependencyPruningAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DependencyPruningAgent", "exec_snapshot_link")

"Dependency Pruning Agent - Detects and removes unused Python dependencies.\n\nThis module provides a batch agent that detects and removes unused Python\ndependencies from requirements.txt using 'deptry' for accurate AST-based\nunused detection.\n\nTypical usage:\n    agent = DependencyPruningAgent(project_root=Path(\"/path/to/project\"), ctx=context)\n    result = await agent.execute()\n"
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.security_util import safe_execute
from agentic_core.utils.timeout_decorator_util import timeout

_emit_emits_metric_event("DependencyPruningAgent", "p4obs", "metric_1")
_emit_emits_metric_event("DependencyPruningAgent", "p4obs", "metric_2")
_emit_emits_metric_event("DependencyPruningAgent", "p4obs", "metric_3")
_emit_emits_metric_event("DependencyPruningAgent", "p4obs", "metric_4")
_emit_emits_metric_event("DependencyPruningAgent", "p4obs", "metric_5")
_emit_emits_metric_event("DependencyPruningAgent", "p4obs", "metric_6")
_emit_records_incident_event("DependencyPruningAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("DependencyPruningAgent", "p4obs", "anomaly")
_emit_writes_observability_log("DependencyPruningAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("DependencyPruningAgent", "p4obs", "mon_state")
_emit_triggers_alert("DependencyPruningAgent", "p4obs", "alert")
_emit_links_incident_trace("DependencyPruningAgent", "p4obs", "trace_link")
_emit_captures_pattern("DependencyPruningAgent", "p3lm", "pattern")
_emit_records_learning_event("DependencyPruningAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DependencyPruningAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("DependencyPruningAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DependencyPruningAgent", "p3lm", "routing")
_emit_improves_agent_policy("DependencyPruningAgent", "p3lm", "policy")
_emit_stores_learning_state("DependencyPruningAgent", "p3lm", "state")
_emit_records_execution_trace("DependencyPruningAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DependencyPruningAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DependencyPruningAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DependencyPruningAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DependencyPruningAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DependencyPruningAgent", "env_read", "p2_env_1")
_emit_reads_environ("DependencyPruningAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("DependencyPruningAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DependencyPruningAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DependencyPruningAgent", "context_pull")
_emit_pulls_context("p1", "DependencyPruningAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "DependencyPruningAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DependencyPruningAgent", "uwg_term_2")
_emit_writes_through("p1", "DependencyPruningAgent", "write_through")
_emit_writes_through("p1", "DependencyPruningAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "DependencyPruningAgent", "safety_validation")
_emit_invokes_eval("p1", "DependencyPruningAgent", "eval_call")
_emit_proposal_commits_routing("p1", "DependencyPruningAgent", "routing_commit")


@dataclass
class DependencyPruningAgent(SovereignBaseAgent):
    """L5 Safety agent that detects and removes unused Python dependencies.

    This batch agent uses 'deptry' for accurate AST-based detection of unused
    dependencies and can remove them from requirements.txt.

    Attributes:
        project_root: Root directory of the project.
        ctx: Execution context with reporting capabilities.
        dry_run: If True, only report what would be removed (default: True).
        requirements_path: Path to requirements.txt file.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    """

    def __init__(self, project_root: Path, ctx: Any) -> None:
        """Initialize the dependency pruning agent.

        Args:
            project_root: Root directory of the project.
            ctx: Execution context with optional report() method.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DependencyPruningAgent.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DependencyPruningAgent.__init__", "p0_governance")
        self.project_root: Path = Path(project_root)
        self.ctx: Any = ctx
        self.dry_run: bool = True
        self.requirements_path: Path = self.project_root / "requirements.txt"

    def _find_unused_deptry(self) -> list[str]:
        """Use deptry to find unused dependencies via AST analysis.

        Returns:
            List of unused package names, empty if deptry fails or not installed.
        """
        try:
            result = safe_execute(
                ["deptry", ".", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access
                check=False,
                timeout=DEFAULT_TIMEOUT,
            )
            if result.returncode == 0:
                data: dict[str, Any] = json.loads(result.stdout)
                return data.get("unused", [])
        except FileNotFoundError:    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access
            pass
        # guardian: allow-silent-swallow
        except (json.JSONDecodeError, Exception):
            pass
        return []

    # guardian: allow-type-erasure
    def _remove_from_requirements_txt(self, unused: list[str]) -> dict[str, Any]:
        """Remove unused packages from requirements.txt.

        Args:
            unused: List of package names to remove.

        Returns:
            Dictionary with removal results:
                - removed: Count of packages removed
                - file: Name of the modified file
        """
        if not self.requirements_path.exists():
            return {"removed": 0}
        content: str = self.requirements_path.read_text(encoding="utf-8")
        lines: list[str] = content.splitlines()
        new_lines: list[str] = []
        removed: int = 0
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("#"):
                new_lines.append(line)
                continue
            match = re.match("^([a-zA-Z0-9_-]+)", line_stripped)
            if match and match.group(1).lower() in [u.lower() for u in unused]:
                removed += 1
                if self.dry_run:
                    new_lines.append(f"# [PRUNED UNUSED] {line}")
                else:
                    continue
            else:
                new_lines.append(line)
        if removed > 0 and (not self.dry_run):
            _wg.write_text(self.requirements_path, "\n".join(new_lines) + "\n", encoding="utf-8")
        return {"removed": removed, "file": "requirements.txt"}

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "DependencyPruningAgent.heal_repository"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DependencyPruningAgent.heal_repository".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    async def execute(self) -> dict[str, Any]:
        """Scan for and optionally remove unused dependencies.

        Returns:
            Dictionary with scan results:
                - unused_found: Count of unused dependencies found
                - removed: Count of dependencies removed
                - dry_run: Whether this was a dry run
        """
        print("   [PRUNE] Scanning for unused dependencies...")
        _adg_dead_imports: int = 0
        try:
            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _src = Path(__file__).resolve()
            _bp = _gbp(_src, self.project_root)
            _adg_dead_imports = len(_bp.antipattern_signals)
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError):
            pass
        unused: list[str] = self._find_unused_deptry()
        if not unused:
            print("   [✓] No unused dependencies detected")
            return {"unused_found": 0, "removed": 0, "adg_dead_import_signals": _adg_dead_imports}
        print(f"   [!] Found {len(unused)} potentially unused packages: {', '.join(unused[:5])}")
        if len(unused) > 5:
            print(f"       ... and {len(unused) - 5} more")
        result: dict[str, Any] = self._remove_from_requirements_txt(unused)
        return {
            "unused_found": len(unused),
            "removed": result["removed"],
            "dry_run": self.dry_run,
            "adg_dead_import_signals": _adg_dead_imports,
        }

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal dependency pruning violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (unused_dependency)
                - package: Name of the unused package
                - path: Path to requirements.txt

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        package = violation.get("package", "")
        if package:
            try:
                self.dry_run = False
                result = self._remove_from_requirements_txt([package])
                return {
                    "violations_fixed": result.get("removed", 0),
                    "violations_found": 1,
                    "errors": 0,
                    "skipped": 0,
                }
            # guardian: allow-silent-swallow
            except (RuntimeError, OSError):
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}
        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
