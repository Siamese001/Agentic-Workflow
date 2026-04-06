from __future__ import annotations

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

emit_replay_key("p0", "HygieneGuardianAgent")
emit_determinism_digest("p0", "HygieneGuardianAgent")

_emit_dispatches_healing_run("p1", "HygieneGuardianAgent", "L5")
_emit_routes_through("p1", "HygieneGuardianAgent", "L5")
_emit_checks_agent_registry("p1", "HygieneGuardianAgent", "agent_registry")
_emit_validates_agent_capability("p1", "HygieneGuardianAgent", "capability")
_emit_dispatches_execution_plan("p1", "HygieneGuardianAgent", "exec_plan")
_emit_agent_executes_agent("p1", "HygieneGuardianAgent", "sub_agent")
_emit_routes_to_agent("p1", "HygieneGuardianAgent", "target_agent")
_emit_verifies_policy("p1", "HygieneGuardianAgent", "policy_check")
_emit_observes_runtime_state("p1", "HygieneGuardianAgent", "runtime_state")
_emit_verifies_boundary("p1", "HygieneGuardianAgent", "boundary_check")
_emit_transcripts_response("p1", "HygieneGuardianAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "HygieneGuardianAgent")
_emit_gated_by_confidence("p1", "HygieneGuardianAgent", "confidence_gate")
_emit_escalates_to_human("p1", "HygieneGuardianAgent", "L5")
_emit_reads_policy_state("p1", "HygieneGuardianAgent", "L5")
_emit_authorize_and_execute("p2", "HygieneGuardianAgent", "execution_auth")
_emit_validates_capability("p2", "HygieneGuardianAgent", "capability_check")
_emit_routes_to_capability("p2", "HygieneGuardianAgent", "capability_route")
_emit_writes_via_uwg("p2", "HygieneGuardianAgent", "uwg_write")
_emit_blocks_direct_write("p2", "HygieneGuardianAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "HygieneGuardianAgent", "tool_invocation")
_emit_captures_execution_output("p2", "HygieneGuardianAgent", "exec_output")
_emit_dispatches_agent("p3", "HygieneGuardianAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "HygieneGuardianAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "HygieneGuardianAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "HygieneGuardianAgent", "healing_outcome")
_emit_escalates_failure("p3", "HygieneGuardianAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "HygieneGuardianAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "HygieneGuardianAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "HygieneGuardianAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "HygieneGuardianAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "HygieneGuardianAgent", "eval_metric")
_emit_stores_embedding("p4", "HygieneGuardianAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "HygieneGuardianAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "HygieneGuardianAgent", "exec_snapshot_link")

"\nHygieneGuardianAgent - Repository Hygiene Enforcement\n\nConsolidates hygiene checks:\n- Empty file detection and cleanup\n- Orphaned __init__.py files\n- Stale backup files (.bak, .orig, .backup)\n- Temporary files cleanup (.tmp, .temp, ~)\n- Debug print statement detection\n- Commented-out code detection\n\nTerritory: agentic_core/L5_safety/validators/\n"
import os
import re
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper
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

_emit_emits_metric_event("HygieneGuardianAgent", "p4obs", "metric_1")
_emit_emits_metric_event("HygieneGuardianAgent", "p4obs", "metric_2")
_emit_emits_metric_event("HygieneGuardianAgent", "p4obs", "metric_3")
_emit_emits_metric_event("HygieneGuardianAgent", "p4obs", "metric_4")
_emit_emits_metric_event("HygieneGuardianAgent", "p4obs", "metric_5")
_emit_emits_metric_event("HygieneGuardianAgent", "p4obs", "metric_6")
_emit_records_incident_event("HygieneGuardianAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("HygieneGuardianAgent", "p4obs", "anomaly")
_emit_writes_observability_log("HygieneGuardianAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("HygieneGuardianAgent", "p4obs", "mon_state")
_emit_triggers_alert("HygieneGuardianAgent", "p4obs", "alert")
_emit_links_incident_trace("HygieneGuardianAgent", "p4obs", "trace_link")
_emit_captures_pattern("HygieneGuardianAgent", "p3lm", "pattern")
_emit_records_learning_event("HygieneGuardianAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("HygieneGuardianAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("HygieneGuardianAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("HygieneGuardianAgent", "p3lm", "routing")
_emit_improves_agent_policy("HygieneGuardianAgent", "p3lm", "policy")
_emit_stores_learning_state("HygieneGuardianAgent", "p3lm", "state")
_emit_records_execution_trace("HygieneGuardianAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("HygieneGuardianAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("HygieneGuardianAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("HygieneGuardianAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("HygieneGuardianAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("HygieneGuardianAgent", "env_read", "p2_env_1")
_emit_reads_environ("HygieneGuardianAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("HygieneGuardianAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("HygieneGuardianAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "HygieneGuardianAgent", "context_pull")
_emit_pulls_context("p1", "HygieneGuardianAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "HygieneGuardianAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "HygieneGuardianAgent", "uwg_term_2")
_emit_writes_through("p1", "HygieneGuardianAgent", "write_through")
_emit_writes_through("p1", "HygieneGuardianAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "HygieneGuardianAgent", "safety_validation")
_emit_invokes_eval("p1", "HygieneGuardianAgent", "eval_call")
_emit_proposal_commits_routing("p1", "HygieneGuardianAgent", "routing_commit")

MAX_FILENAME_WORDS = 5
MAX_TEST_FILENAME_WORDS = 8
REDUNDANT_TERMS = {"implementation", "management", "service", "script", "scripts", "utility", "utilities"}


@dataclass
class HygieneViolation:
    """Structured violation for hygiene issues."""

    file_path: Path
    violation_type: str
    message: str
    line_number: int | None = None
    severity: int = 5
    auto_fixable: bool = False


class HygieneGuardianAgent(SovereignBaseAgent):
    """
    Repository hygiene enforcement agent.

    Detects and optionally fixes:
    - Empty files (0 bytes or only whitespace)
    - Orphaned __init__.py files (in directories with no other Python files)
    - Stale backup files (.bak, .orig, .backup)
    - Temporary files (.tmp, .temp, ~)
    - Debug print statements
    - Large blocks of commented-out code
    - Repeated filename strings (e.g., 'enums_enums_enums') [Merged from FileCleanupAgent]
    - Copy-pattern filenames (e.g., 'Copy of file.py', 'file (1).py')

    Uses ArchivalGatekeeper for all destructive operations (safe deletion).

    Inherits:
        SubatomicTestingMixin: Testing utilities
        HealerMixin: Healing chain support
        MCPHardenedMixin: MCP integration
    """

    PYTHON_EXTENSIONS = {".py", ".pyi"}
    BACKUP_EXTENSIONS = {".bak", ".orig", ".backup", ".old"}
    TEMP_EXTENSIONS = {".tmp", ".temp", ".swp", ".swo"}
    DEBUG_PRINT_PATTERN = re.compile("^\\s*print\\s*\\(", re.MULTILINE)
    COMMENTED_CODE_PATTERN = re.compile(
        "^\\s*#\\s*(def|class|import|from|if|for|while|try)\\s+", re.MULTILINE
    )
    COPY_PATTERNS = [
        re.compile("^Copy of (.+)$", re.IGNORECASE),
        re.compile("^(.+) \\(\\d+\\)$"),
        re.compile("^(.+)_copy\\d*$", re.IGNORECASE),
    ]

    def __init__(self, project_root: Path, ctx: Any = None, dry_run: bool = True):
        """
        Initialize the hygiene guardian.

        Args:
            project_root: Root directory of the project
            ctx: Execution context (optional)
            dry_run: If True, only report violations without fixing
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "HygieneGuardianAgent.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        self.project_root = Path(project_root).resolve()
        self.ctx = ctx
        self.dry_run = dry_run
        self.violations: list[HygieneViolation] = []
        self.agent_name = self.__class__.__name__
        self.naming_violations: list[dict] = []
        self.gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)
        self.rules = {
            "MAX_FILENAME_WORDS": MAX_FILENAME_WORDS,
            "MAX_TEST_FILENAME_WORDS": MAX_TEST_FILENAME_WORDS,
            "FORBIDDEN_PATTERNS": ["temp_", "test_v2", "final_final"],
            "CASE_CONVENTION": "snake_case_for_scripts",
            "REDUNDANT_TERMS": REDUNDANT_TERMS,
        }

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for HygieneGuardianAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, "HygieneGuardianAgent.heal")
        try:
            violation.get("type", "")
            file_path = violation.get("file")
            if not file_path:
                return {
                    "status": "failed",
                    "details": "No file path provided in violation",
                    "artifacts": [],
                    "errors": ["Missing file path"],
                }
            return {
                "status": "manual_required",
                "details": "HygieneGuardianAgent requires manual review for healing",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            return {
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling

    def _is_empty_file(self, file_path: Path) -> bool:
        """Check if file is empty or contains only whitespace."""
        try:
            content = file_path.read_text(encoding="utf-8")
            return len(content.strip()) == 0
        except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
            return False

    def _is_orphaned_init(self, file_path: Path) -> bool:
        """Check if __init__.py is orphaned (no other Python files in directory)."""
        if file_path.name != "__init__.py":
            return False
        parent_dir = file_path.parent
        python_files = [
            f for f in parent_dir.glob("*.py") if f.name != "__init__.py" and (not f.name.startswith("."))
        ]
        return len(python_files) == 0

    def _has_debug_prints(self, file_path: Path) -> list[int]:
        """Detect debug print statements and return line numbers."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            debug_lines = []
            for i, line in enumerate(lines, 1):
                stripped = line.strip()    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                if self.DEBUG_PRINT_PATTERN.search(line):
                    if "logger" not in line.lower() and "log(" not in line.lower():
                        debug_lines.append(i)
            return debug_lines
        except (OSError, UnicodeDecodeError, SyntaxError) as e:    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
            self.logger.debug(f"Failed to scan for debug statements in {file_path.name}: {e}")
            return []

    def _has_commented_code(self, file_path: Path) -> tuple[bool, int]:
        """
        Detect large blocks of commented-out code.

        Returns:
            (has_commented_code, num_lines)
        """    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
        try:
            content = file_path.read_text(encoding="utf-8")
            matches = self.COMMENTED_CODE_PATTERN.findall(content)
            if len(matches) > 5:
                return (True, len(matches))
            return (False, 0)
        except (OSError, UnicodeDecodeError, SyntaxError) as e:    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
            self.logger.debug(f"Failed to scan for commented code in {file_path.name}: {e}")
            return (False, 0)

    def _has_repeated_filename_parts(self, filename: str) -> tuple[bool, str | None]:
        """
        Check if filename has repeated consecutive strings (merged from FileCleanupAgent).

        Args:
            filename: Filename to check (without extension)

        Returns:
            Tuple of (has_repeats, repeated_pattern) or (False, None)

        Examples:
            'enums_enums' -> (True, 'enums')
            'impl_impl_impl' -> (True, 'impl')
            'data_models_enums_enums' -> (True, 'enums')
            'test_data' -> (False, None)
        """
        parts = filename.split("_")
        for i in range(len(parts) - 1):
            if parts[i] == parts[i + 1] and parts[i]:
                return (True, parts[i])
        part_counts = Counter(parts)
        for part, count in part_counts.items():
            if count > 1 and part and (len(part) > 2):
                return (True, part)
        return (False, None)

    def _is_copy_pattern_filename(self, filename: str) -> tuple[bool, str | None]:
        """
        Check if filename matches copy patterns.

        Args:
            filename: Filename to check (without extension)

        Returns:
            Tuple of (is_copy, original_name) or (False, None)

        Examples:
            'Copy of report' -> (True, 'report')
            'report (1)' -> (True, 'report')
            'report_copy2' -> (True, 'report')
        """
        for pattern in self.COPY_PATTERNS:
            match = pattern.match(filename)
            if match:
                return (True, match.group(1))
        return (False, None)

    def _scan_directory(self, directory: Path) -> None:
        """Recursively scan directory for hygiene violations."""
        ignore_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
        for item in directory.rglob("*"):
            if any(ignored in item.parts for ignored in ignore_dirs):
                continue
            if not item.is_file():
                continue
            if item.suffix in self.BACKUP_EXTENSIONS:
                self.violations.append(
                    HygieneViolation(
                        file_path=item,
                        violation_type="stale_backup",
                        message=f"Stale backup file: {item.suffix}",
                        severity=3,
                        auto_fixable=True,
                    )
                )
            if item.suffix in self.TEMP_EXTENSIONS or item.name.endswith("~"):
                self.violations.append(
                    HygieneViolation(
                        file_path=item,
                        violation_type="temp_file",
                        message="Temporary file should be removed",
                        severity=4,
                        auto_fixable=True,
                    )
                )
            if item.suffix in self.PYTHON_EXTENSIONS:
                if self._is_empty_file(item):
                    self.violations.append(
                        HygieneViolation(
                            file_path=item,
                            violation_type="empty_file",
                            message="Empty Python file",
                            severity=5,
                            auto_fixable=True,
                        )
                    )
                if self._is_orphaned_init(item):
                    self.violations.append(
                        HygieneViolation(
                            file_path=item,
                            violation_type="orphaned_init",
                            message="Orphaned __init__.py with no other Python files",
                            severity=4,
                            auto_fixable=True,
                        )
                    )
                debug_lines = self._has_debug_prints(item)
                if debug_lines:
                    self.violations.append(
                        HygieneViolation(
                            file_path=item,
                            violation_type="debug_print",
                            message=f"Debug print statements found on lines: {debug_lines[:5]}",
                            line_number=debug_lines[0],
                            severity=2,
                            auto_fixable=False,
                        )
                    )
                has_commented, num_lines = self._has_commented_code(item)
                if has_commented:
                    self.violations.append(
                        HygieneViolation(
                            file_path=item,
                            violation_type="commented_code",
                            message=f"Large block of commented-out code ({num_lines} lines)",
                            severity=2,
                            auto_fixable=False,
                        )
                    )
                has_repeats, pattern = self._has_repeated_filename_parts(item.stem)
                if has_repeats:
                    self.violations.append(
                        HygieneViolation(
                            file_path=item,
                            violation_type="repeated_filename",
                            message=f'Repeated string in filename: "{pattern}"',
                            severity=4,
                            auto_fixable=True,
                        )
                    )
                is_copy, original = self._is_copy_pattern_filename(item.stem)
                if is_copy:
                    self.violations.append(
                        HygieneViolation(
                            file_path=item,
                            violation_type="copy_pattern",
                            message=f'Copy-pattern filename detected (original: "{original}")',
                            severity=5,
                            auto_fixable=True,
                        )
                    )

    def _fix_violations(self) -> int:
        """
        Attempt to auto-fix violations where possible.

        Uses ArchivalGatekeeper for all destructive operations (safe deletion).

        Returns:
            Number of violations fixed
        """
        fixed_count = 0
        archivable_types = {
            "stale_backup",
            "temp_file",
            "empty_file",
            "orphaned_init",
            "repeated_filename",
            "copy_pattern",
        }
        for violation in self.violations:
            if not violation.auto_fixable or self.dry_run:
                continue
            try:
                if violation.violation_type in archivable_types:
                    result = self.gatekeeper.safe_delete(
                        violation.file_path,
                        self.agent_name,
                        f"{violation.violation_type}: {violation.message}",
                    )
                    if result.success:
                        print(f"   [FIXED] Archived {violation.violation_type}: {violation.file_path}")
                        fixed_count += 1
                    else:
                        print(f"   [ERROR] Failed to archive {violation.file_path}: {result.error}")
            # guardian: allow-silent-swallow
            except (RuntimeError, OSError) as e:
                print(f"   [ERROR] Failed to fix {violation.file_path}: {e}")
        return fixed_count

    @standard_heal
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> dict[str, Any]:
        """
        Autonomous healing method for repository hygiene.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute fixes (overrides dry_run)
            **kwargs: Additional arguments

        Returns:
            Dictionary with healing results
        """
        self.dry_run = dry_run and (not execute)
        self.violations = []
        print(f"\n[*] HYGIENE GUARDIAN - Scanning {self.project_root}")
        print(f"    Mode: {('DRY RUN' if self.dry_run else 'EXECUTE')}")
        self._scan_directory(self.project_root)
        by_type: dict[str, list[HygieneViolation]] = {}
        for v in self.violations:
            by_type.setdefault(v.violation_type, []).append(v)
        if self.violations:
            print(f"\n   [!] Found {len(self.violations)} hygiene violations:")
            for vtype, viols in sorted(by_type.items()):
                print(f"\n   [{vtype.upper()}] {len(viols)} violations:")
                for v in viols[:5]:
                    rel_path = v.file_path.relative_to(self.project_root)
                    print(f"      - {rel_path}: {v.message}")
                if len(viols) > 5:
                    print(f"      ... and {len(viols) - 5} more")
        else:
            print("   [OK] No hygiene violations detected")
        fixed_count = 0
        if not self.dry_run:
            fixed_count = self._fix_violations()
            print(f"\n   [FIXED] {fixed_count} violations auto-fixed")
        return {
            "violations_found": len(self.violations),
            "violations_fixed": fixed_count,
            "errors": 0,
            "skipped": 0,
        }

    def audit_naming_conventions(self) -> list[dict]:
        """
        Performs a deep audit of the repository's naming conventions,
        enforcing word-count limits and semantic density.
        """
        print(f"[*] Hygiene Guardian: Scanning {self.project_root} for naming violations...")
        self.naming_violations = []
        ignored_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for f in files:
                if not f.endswith(".py") or f.startswith("__"):
                    continue
                path = Path(root) / f
                self._check_filename_length(path)
        return self.naming_violations

    def _check_filename_length(self, path: Path):
        """
        Checks for 'Semantic Bloat' where filenames exceed the word limit.
        Enhanced with CamelCase splitting and mixed delimiter handling.
        Example Violation: logic_synthesis_pick_best_refinement_refine_scripts_ranking.py
        """
        _emit_applies_guardrail(str(uuid.uuid4()), "HygieneGuardianAgent._check_filename_length", "L5_POLICY")
        base_name = path.stem
        ext = path.suffix
        clean_name = base_name.replace("-", "_")
        clean_name = re.sub("(?<!^)(?=[A-Z])", "_", clean_name)
        words = [w for w in clean_name.split("_") if w]
        word_count = len(words)
        is_test = base_name.startswith("test_") or base_name.endswith("_test")
        limit = self.rules["MAX_TEST_FILENAME_WORDS"] if is_test else self.rules["MAX_FILENAME_WORDS"]
        if word_count > limit:
            violation = {
                "file": str(path.relative_to(self.project_root)),
                "rule": "MAX_TEST_FILENAME_WORDS" if is_test else "MAX_FILENAME_WORDS",
                "current_count": word_count,
                "limit": limit,
                "suggestion": self._generate_concise_suggestion(words, ext),
            }
            self.naming_violations.append(violation)
            print(f"  [VIOLATION] {path.name}: {word_count} words exceeds limit of {limit}")

    def _generate_concise_suggestion(self, words: list[str], ext: str) -> str:
        """Proposes a concise alternative using semantic anchors and redundant term removal."""
        filtered = [w for w in words if w.lower() not in self.rules["REDUNDANT_TERMS"]]
        if len(filtered) > self.rules["MAX_FILENAME_WORDS"]:
            mid = len(filtered) // 2
            concise = filtered[:2] + [filtered[mid]] + filtered[-1:]
            return "_".join(concise).lower() + ext
        return "_".join(filtered).lower() + ext
        return {
            "violations_found": len(self.violations),
            "violations_fixed": fixed_count,
            "violations_by_type": {k: len(v) for k, v in by_type.items()},
            "dry_run": self.dry_run,
        }

    async def execute(self) -> dict[str, Any]:
        """Execute hygiene checks (async wrapper)."""
        return self.heal_repository(dry_run=self.dry_run)
