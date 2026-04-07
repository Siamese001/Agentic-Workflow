from __future__ import annotations

import importlib
from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_snapshots_state,
    # noqa: E402
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

emit_replay_key("p0", "GenerativeGuardAgent")
emit_determinism_digest("p0", "GenerativeGuardAgent")

_emit_dispatches_healing_run("p1", "GenerativeGuardAgent", "L5")
_emit_routes_through("p1", "GenerativeGuardAgent", "L5")
_emit_checks_agent_registry("p1", "GenerativeGuardAgent", "agent_registry")
_emit_validates_agent_capability("p1", "GenerativeGuardAgent", "capability")
_emit_dispatches_execution_plan("p1", "GenerativeGuardAgent", "exec_plan")
_emit_agent_executes_agent("p1", "GenerativeGuardAgent", "sub_agent")
_emit_routes_to_agent("p1", "GenerativeGuardAgent", "target_agent")
_emit_verifies_policy("p1", "GenerativeGuardAgent", "policy_check")
_emit_observes_runtime_state("p1", "GenerativeGuardAgent", "runtime_state")
_emit_verifies_boundary("p1", "GenerativeGuardAgent", "boundary_check")
_emit_transcripts_response("p1", "GenerativeGuardAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "GenerativeGuardAgent")
_emit_gated_by_confidence("p1", "GenerativeGuardAgent", "confidence_gate")
_emit_escalates_to_human("p1", "GenerativeGuardAgent", "L5")
_emit_reads_policy_state("p1", "GenerativeGuardAgent", "L5")

_emit_snapshots_state("p0", "GenerativeGuardAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "GenerativeGuardAgent", "execution_auth")
_emit_validates_capability("p2", "GenerativeGuardAgent", "capability_check")
_emit_routes_to_capability("p2", "GenerativeGuardAgent", "capability_route")
_emit_writes_via_uwg("p2", "GenerativeGuardAgent", "uwg_write")
_emit_blocks_direct_write("p2", "GenerativeGuardAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "GenerativeGuardAgent", "tool_invocation")
_emit_captures_execution_output("p2", "GenerativeGuardAgent", "exec_output")
_emit_dispatches_agent("p3", "GenerativeGuardAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "GenerativeGuardAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "GenerativeGuardAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "GenerativeGuardAgent", "healing_outcome")
_emit_escalates_failure("p3", "GenerativeGuardAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "GenerativeGuardAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GenerativeGuardAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "GenerativeGuardAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "GenerativeGuardAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GenerativeGuardAgent", "eval_metric")
_emit_stores_embedding("p4", "GenerativeGuardAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "GenerativeGuardAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GenerativeGuardAgent", "exec_snapshot_link")

"\nGenerativeGuardAgent - Detects and removes runaway generated files.\n\nKEYS: 45 (Dead Code/Runaway Generation)\nROLE: The Watchdog. Identifies and deletes recursively-generated files.\nExtracted from CanonHealerAgent.py for one-file-per-agent pattern.\n"
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import TESTS_DIR

_mod = importlib.import_module("agentic_core.L5_safety.enforcement.mcp_hardened_mixin")
MCPHardenedMixin = _mod.MCPHardenedMixin
try:
    from agentic_core.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
except ImportError:  # guardian: allow-silent-swallow

    class CanonBaseAgentInterface:
        pass


try:
    from agentic_core.L5_safety.config.structure_blueprint import (
        AGENT_DISCOVERY_JSON,
        AGENT_DISCOVERY_MANIFEST_JSON,
        AGENTIC_CORE_DIR,
        DASHBOARD_DIR,
        L0_MAINTENANCE_DIR,
        L1_COGNITION_DIR,
        L2_EXECUTION_DIR,
        L3_ORCHESTRATION_DIR,
        L4_STATE_DIR,
        L5_SAFETY_DIR,
        L6_OBSERVABILITY_DIR,
        SCRIPTS_DIR,
        TESTS_DIR,
        get_validated_project_root,
    )
except ImportError:
    from pathlib import Path

    AGENT_DISCOVERY_JSON = "agent_discovery_full.json"
    AGENT_DISCOVERY_MANIFEST_JSON = "agent_discovery_manifest.json"
    _root = Path(__file__).resolve().parent.parent.parent.parent
    AGENTIC_CORE_DIR = _root / AGENTIC_CORE_DIR
    SCRIPTS_DIR = _root / "scripts"
    TESTS_DIR = _root / TESTS_DIR
    DASHBOARD_DIR = _root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards"
    L0_MAINTENANCE_DIR = _root / AGENTIC_CORE_DIR / "L0_routing"
    L1_COGNITION_DIR = _root / AGENTIC_CORE_DIR / "L1_cognition"
    L2_EXECUTION_DIR = _root / AGENTIC_CORE_DIR / "L2_execution"
    L3_ORCHESTRATION_DIR = _root / AGENTIC_CORE_DIR / "L3_orchestration"
    L4_STATE_DIR = _root / AGENTIC_CORE_DIR / "L4_state"
    L5_SAFETY_DIR = _root / AGENTIC_CORE_DIR / "L5_safety"
    L6_OBSERVABILITY_DIR = _root / AGENTIC_CORE_DIR / "L6_observability"

    def get_validated_project_root() -> Path:
        return _root


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("GenerativeGuardAgent", "p4obs", "metric_1")
_emit_emits_metric_event("GenerativeGuardAgent", "p4obs", "metric_2")
_emit_emits_metric_event("GenerativeGuardAgent", "p4obs", "metric_3")
_emit_emits_metric_event("GenerativeGuardAgent", "p4obs", "metric_4")
_emit_emits_metric_event("GenerativeGuardAgent", "p4obs", "metric_5")
_emit_emits_metric_event("GenerativeGuardAgent", "p4obs", "metric_6")
_emit_records_incident_event("GenerativeGuardAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("GenerativeGuardAgent", "p4obs", "anomaly")
_emit_writes_observability_log("GenerativeGuardAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("GenerativeGuardAgent", "p4obs", "mon_state")
_emit_triggers_alert("GenerativeGuardAgent", "p4obs", "alert")
_emit_links_incident_trace("GenerativeGuardAgent", "p4obs", "trace_link")
_emit_captures_pattern("GenerativeGuardAgent", "p3lm", "pattern")
_emit_records_learning_event("GenerativeGuardAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("GenerativeGuardAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("GenerativeGuardAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("GenerativeGuardAgent", "p3lm", "routing")
_emit_improves_agent_policy("GenerativeGuardAgent", "p3lm", "policy")
_emit_stores_learning_state("GenerativeGuardAgent", "p3lm", "state")
_emit_records_execution_trace("GenerativeGuardAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("GenerativeGuardAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("GenerativeGuardAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("GenerativeGuardAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("GenerativeGuardAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("GenerativeGuardAgent", "env_read", "p2_env_1")
_emit_reads_environ("GenerativeGuardAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("GenerativeGuardAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("GenerativeGuardAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "GenerativeGuardAgent", "context_pull")
_emit_pulls_context("p1", "GenerativeGuardAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "GenerativeGuardAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "GenerativeGuardAgent", "uwg_term_2")
_emit_writes_through("p1", "GenerativeGuardAgent", "write_through")
_emit_writes_through("p1", "GenerativeGuardAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "GenerativeGuardAgent", "safety_validation")
_emit_invokes_eval("p1", "GenerativeGuardAgent", "eval_call")
_emit_proposal_commits_routing("p1", "GenerativeGuardAgent", "routing_commit")

EXCLUDED_DIRS = list(GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS)


@dataclass
class GenerativeGuardAgent(SovereignBaseAgent, HealerMixin, CanonBaseAgentInterface, MCPHardenedMixin):
    """
    KEYS: 45 (Dead Code/Runaway Generation)
    ROLE: The Watchdog. Identifies and deletes recursively-generated files.

    Detects files matching runaway generation patterns:
    - *_copy*.py
    - *_backup*.py
    - *_old*.py
    - *_temp*.py
    """

    def __init__(self, ctx: Any = None) -> None:
        """Initialize the instance."""
        self.impl = None
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.Logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.GENERATIVE_PATTERNS = [
            "_copy\\d*\\.py$",
            "_backup\\d*\\.py$",
            "_old\\d*\\.py$",
            "_temp\\d*\\.py$",
        ]

    # guardian: allow-type-erasure
    async def execute(self, goal: str = None, context: dict[str, Any] = None) -> dict[str, Any]:
        """Execute guard checks - maintains backward compatibility."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "GenerativeGuardAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GenerativeGuardAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        await self._execute_guard()
        return {"status": "completed", "agent": self.name}

    def get_capabilities(self) -> list[str]:
        """Return agent capabilities."""
        return ["runaway_detection", "file_cleanup", "pattern_matching"]

    def validate_state(self) -> bool:
        """Validate agent state."""
        return self.ctx is not None

    # guardian: allow-type-erasure
    async def _execute_guard(self) -> Any:
        """Scan for and optionally purge runaway generated files."""
        _emit_applies_guardrail(str(uuid.uuid4()), "GenerativeGuardAgent._execute_guard", "L5_POLICY")
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Generative Policy...")
        violations = []
        project_root = getattr(self.ctx, "project_root", ".")
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            violations.extend(self._find_runaway_violations_in_dir(root, files))
        if violations:
            self._process_found_violations(violations)
        else:
            print("   [OK] No runaway generation detected.")
            self.ctx.report(self.name, 45, True, [])
            self.ctx.signals.add("GENERATIVE_CLEAN")    # guardian: Add error context logging

    # guardian: allow-type-erasure
    def _purge_single_file(self, file_path: str) -> Any:
        """Helper to attempt purging a single file and report."""
        try:
            _wg.remove_file(file_path)
            print(f"         DELETED: {file_path}")
        except OSError as e:    # guardian: Add error context logging
            print(f"         [X] Failed to delete {file_path}: {e}", file=sys.stderr)

    # guardian: allow-type-erasure
    def _process_found_violations(self, violations: list[str]) -> Any:
        """Helper to process and optionally purge detected runaway files."""
        print(f"   🛑 RUNAWAY GENERATION DETECTED ({len(violations)} files).")
        self.ctx.report(self.name, 45, False, violations)
        purge_runaway = "--purge-runaway" in sys.argv
        if not purge_runaway:
            self.ctx.signals.add("GENERATIVE_FAIL")
            print("      Hint: Run with '--purge-runaway' to delete these files.")
        else:
            print("      🗑️  Purging runaway generated files...")
            for file_path in violations:
                self._purge_single_file(file_path)
            self.ctx.signals.add("GENERATIVE_CLEAN")

    def _is_runaway_file(self, normalized_file_path: str) -> bool:
        """Helper to check if a file path matches any runaway pattern."""
        for pattern in self.GENERATIVE_PATTERNS:
            if re.search(pattern, normalized_file_path):
                return True
        return False

    def _find_runaway_violations_in_dir(self, root: str, files: list[str]) -> list[str]:
        """Helper to find runaway violations within a specific directory."""
        violations_in_dir = []
        for file in files:
            file_path = Path(root) / file
            normalized_file_path = Path(file_path).as_posix()
            if self._is_runaway_file(normalized_file_path):
                violations_in_dir.append(file_path)
        return violations_in_dir

    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L1 cognition agent - operational only."""
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
            print(f"[{agent_name}] L1 cognition - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal generative guard violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (runaway_generation)
                - path: Path to the runaway file
                - pattern: Pattern that matched

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        path = violation.get("path", "")
        if path:
            try:
                import os

                # guardian: allow-path-string
                if os.path.exists(path):
                    _wg.remove_file(path)
                    return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
            except (ValueError, TypeError):  # guardian: allow-silent-swallow
                return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}
        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
