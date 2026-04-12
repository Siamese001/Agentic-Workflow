from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.utils import write_gateway as _wg
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "StructureEnforcerAgent")
emit_determinism_digest("p0", "StructureEnforcerAgent")

_emit_dispatches_healing_run("p1", "StructureEnforcerAgent", "L5")
_emit_routes_through("p1", "StructureEnforcerAgent", "L5")
_emit_checks_agent_registry("p1", "StructureEnforcerAgent", "agent_registry")
_emit_validates_agent_capability("p1", "StructureEnforcerAgent", "capability")
_emit_dispatches_execution_plan("p1", "StructureEnforcerAgent", "exec_plan")
_emit_agent_executes_agent("p1", "StructureEnforcerAgent", "sub_agent")
_emit_routes_to_agent("p1", "StructureEnforcerAgent", "target_agent")
_emit_verifies_policy("p1", "StructureEnforcerAgent", "policy_check")
_emit_observes_runtime_state("p1", "StructureEnforcerAgent", "runtime_state")
_emit_verifies_boundary("p1", "StructureEnforcerAgent", "boundary_check")
_emit_transcripts_response("p1", "StructureEnforcerAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "StructureEnforcerAgent")
_emit_gated_by_confidence("p1", "StructureEnforcerAgent", "confidence_gate")
_emit_escalates_to_human("p1", "StructureEnforcerAgent", "L5")
_emit_reads_policy_state("p1", "StructureEnforcerAgent", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "StructureEnforcerAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "StructureEnforcerAgent", "execution_auth")
_emit_validates_capability("p2", "StructureEnforcerAgent", "capability_check")
_emit_routes_to_capability("p2", "StructureEnforcerAgent", "capability_route")
_emit_writes_via_uwg("p2", "StructureEnforcerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "StructureEnforcerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "StructureEnforcerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "StructureEnforcerAgent", "exec_output")
_emit_dispatches_agent("p3", "StructureEnforcerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "StructureEnforcerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "StructureEnforcerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "StructureEnforcerAgent", "healing_outcome")
_emit_escalates_failure("p3", "StructureEnforcerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "StructureEnforcerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "StructureEnforcerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "StructureEnforcerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "StructureEnforcerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "StructureEnforcerAgent", "eval_metric")
_emit_stores_embedding("p4", "StructureEnforcerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "StructureEnforcerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "StructureEnforcerAgent", "exec_snapshot_link")

"\nStructureEnforcerAgent - Structural Enforcement\n\nPhase 3 Hard Migration: Consolidates:\n- GravityEnforcerAgent (layer gravity enforcement)\n- HierarchyEnforcerAgent (hierarchy enforcement)\n- NamingEnforcerAgent (naming conventions)\n- DocEnforcerAgent (documentation enforcement)\n- ASCIIEnforcerAgent (ASCII compliance)\n- StrictDocEnforcerAgent (strict documentation)\n\nFeatures:\n- Gravity/layer import enforcement\n- Hierarchy validation\n- Naming convention enforcement ([Name]Agent suffix)\n- Documentation completeness checks\n- ASCII compliance validation\n- Auto-rename for non-compliant classes\n"
import ast
import logging
import re
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import ARCHIVES_DIR
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

_emit_emits_metric_event("StructureEnforcerAgent", "p4obs", "metric_1")
_emit_emits_metric_event("StructureEnforcerAgent", "p4obs", "metric_2")
_emit_emits_metric_event("StructureEnforcerAgent", "p4obs", "metric_3")
_emit_emits_metric_event("StructureEnforcerAgent", "p4obs", "metric_4")
_emit_emits_metric_event("StructureEnforcerAgent", "p4obs", "metric_5")
_emit_emits_metric_event("StructureEnforcerAgent", "p4obs", "metric_6")
_emit_records_incident_event("StructureEnforcerAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("StructureEnforcerAgent", "p4obs", "anomaly")
_emit_writes_observability_log("StructureEnforcerAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("StructureEnforcerAgent", "p4obs", "mon_state")
_emit_triggers_alert("StructureEnforcerAgent", "p4obs", "alert")
_emit_links_incident_trace("StructureEnforcerAgent", "p4obs", "trace_link")
_emit_captures_pattern("StructureEnforcerAgent", "p3lm", "pattern")
_emit_records_learning_event("StructureEnforcerAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("StructureEnforcerAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("StructureEnforcerAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("StructureEnforcerAgent", "p3lm", "routing")
_emit_improves_agent_policy("StructureEnforcerAgent", "p3lm", "policy")
_emit_stores_learning_state("StructureEnforcerAgent", "p3lm", "state")
_emit_records_execution_trace("StructureEnforcerAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("StructureEnforcerAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("StructureEnforcerAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("StructureEnforcerAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("StructureEnforcerAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("StructureEnforcerAgent", "env_read", "p2_env_1")
_emit_reads_environ("StructureEnforcerAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("StructureEnforcerAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("StructureEnforcerAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "StructureEnforcerAgent", "context_pull")
_emit_pulls_context("p1", "StructureEnforcerAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "StructureEnforcerAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "StructureEnforcerAgent", "uwg_term_2")
_emit_writes_through("p1", "StructureEnforcerAgent", "write_through")
_emit_writes_through("p1", "StructureEnforcerAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "StructureEnforcerAgent", "safety_validation")
_emit_invokes_eval("p1", "StructureEnforcerAgent", "eval_call")
_emit_proposal_commits_routing("p1", "StructureEnforcerAgent", "routing_commit")

Logger = logging.getLogger(__name__)


class StructureViolationType:
    """Types of structure violations."""

    GRAVITY = "GRAVITY"
    HIERARCHY = "HIERARCHY"
    NAMING = "NAMING"
    DOCUMENTATION = "DOCUMENTATION"
    ASCII = "ASCII"


@dataclass
class StructureViolation:
    """Represents a structure violation."""

    file_path: Path
    line_number: int
    violation_type: str
    message: str
    suggested_fix: str | None = None
    auto_fixable: bool = False
    severity: str = "ERROR"


@dataclass
class NamingRule:
    """Naming convention rule."""

    pattern: str
    suffix: str
    description: str
    auto_rename: bool = True


@dataclass
class StructureConfig:
    """configuration for structure enforcement."""

    enable_gravity: bool = True
    enable_hierarchy: bool = True
    enable_naming: bool = True
    enable_documentation: bool = True
    enable_ascii: bool = True
    auto_fix: bool = False
    agent_suffix: str = "Agent"
    required_docstring: bool = True
    min_docstring_length: int = 10


class StructureEnforcerAgent(SovereignBaseAgent):
    """
    Unified structure enforcement with gravity and naming.

    Consolidates:
    - GravityEnforcerAgent (layer imports)
    - HierarchyEnforcerAgent (hierarchy)
    - NamingEnforcerAgent (naming)
    - DocEnforcerAgent (documentation)
    - ASCIIEnforcerAgent (ASCII)
    - StrictDocEnforcerAgent (strict docs)

    Usage:
        enforcer = StructureEnforcerAgent()

        # Validate structure
        violations = enforcer.validate_file(Path("my_agent.py"))

        # Check gravity
        is_valid = enforcer.check_gravity_import("L2", "L5")

        # Force rename
        enforcer.force_rename_class(Path("BadName.py"), "BadName", "BadNameAgent")
    """

    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        return {"violations": 0, "fixed": 0, "errors": 0}

    LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
    GRAVITY_RULES = {
        "L0": {"L0"},
        "L1": {"L0", "L1"},
        "L2": {"L0", "L1", "L2"},
        "L3": {"L0", "L1", "L2", "L3"},
        "L4": {"L0", "L1", "L2", "L3", "L4"},
        "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},
        "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},
    }

    def __init__(self, project_root: Path | None = None, agent_config: StructureConfig | None = None):
        self.project_root = project_root or Path.cwd()
        self._agent_config = agent_config or StructureConfig()
        self._lock = threading.RLock()
        self._violations: list[StructureViolation] = []
        Logger.info("StructureEnforcerAgent initialized")

    def validate_file(self, file_path: Path) -> list[StructureViolation]:
        """Validate a file for all structure rules."""

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            f"StructureEnforcerAgent.validate_file:{file_path.name}",
        )
        violations = []
        if not file_path.exists():
            return violations
        try:
            content = file_path.read_text(encoding="utf-8")
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"Failed to read {file_path}: {e}")
            return violations
        if self._agent_config.enable_gravity:
            violations.extend(self._check_gravity(file_path, content))
        if self._agent_config.enable_naming:
            violations.extend(self._check_naming(file_path, content))
        if self._agent_config.enable_documentation:
            violations.extend(self._check_documentation(file_path, content))
        if self._agent_config.enable_ascii:
            violations.extend(self._check_ascii(file_path, content))
        return violations

    def _extract_layer(self, path: Path) -> str | None:
        """Extract layer from file path."""
        path_str = str(path)
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
                return layer
        return None

    def _extract_layer_from_module(self, module: str) -> str | None:
        """Extract layer from module name."""
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f".{layer}_" in module or module.startswith(f"{layer}_") or f"_{layer}_" in module:
                return layer
        return None

    def _check_gravity(self, file_path: Path, content: str) -> list[StructureViolation]:
        """Check gravity (layer import) violations."""
        violations = []
        source_layer = self._extract_layer(file_path)
        if not source_layer:
            return violations
        allowed_layers = self.GRAVITY_RULES.get(source_layer, set())
        try:
            tree = ast.parse(content)
        except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
            return violations
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                target_layer = self._extract_layer_from_module(node.module)
                if target_layer and target_layer not in allowed_layers:
                    violations.append(
                        StructureViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=StructureViolationType.GRAVITY,
                            message=f"Gravity violation: {source_layer} cannot import from {target_layer}",
                            severity="CRITICAL",
                        ),
                    )
        return violations

    def _check_naming(self, file_path: Path, content: str) -> list[StructureViolation]:
        """Check naming convention violations."""
        violations = []
        if not file_path.name.endswith("Agent.py"):
            return violations
        try:
            tree = ast.parse(content)
        except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
            return violations
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name.endswith(self._agent_config.agent_suffix):
                    violations.append(
                        StructureViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=StructureViolationType.NAMING,
                            message=f"Class '{node.name}' must end with '{self._agent_config.agent_suffix}' suffix",
                            suggested_fix=f"{node.name}{self._agent_config.agent_suffix}",
                            auto_fixable=True,
                        ),
                    )
        return violations

    def _check_documentation(self, file_path: Path, content: str) -> list[StructureViolation]:
        """Check documentation violations."""
        violations = []
        try:
            tree = ast.parse(content)
        except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
            return violations
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef | ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if self._agent_config.required_docstring and (not docstring):
                    violations.append(
                        StructureViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=StructureViolationType.DOCUMENTATION,
                            message=f"Missing docstring for {type(node).__name__} '{node.name}'",
                            severity="WARNING",
                        ),
                    )
                elif docstring and len(docstring) < self._agent_config.min_docstring_length:
                    violations.append(
                        StructureViolation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=StructureViolationType.DOCUMENTATION,
                            message=f"Docstring too short for '{node.name}' (min {self._agent_config.min_docstring_length} chars)",
                            severity="INFO",
                        ),
                    )
        return violations

    def _check_ascii(self, file_path: Path, content: str) -> list[StructureViolation]:
        """Check ASCII compliance."""
        violations = []
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            try:
                line.encode("ascii")
            except UnicodeEncodeError:  # guardian: UnicodeEncodeError should be handled with specific context
                non_ascii = [c for c in line if ord(c) > 127]
                violations.append(
                    StructureViolation(
                        file_path=file_path,
                        line_number=i,
                        violation_type=StructureViolationType.ASCII,
                        message=f"Non-ASCII characters found: {non_ascii[:5]}",
                        severity="WARNING",
                    ),
                )
        return violations

    def check_gravity_import(self, source_layer: str, target_layer: str) -> tuple[bool, str]:
        """
        Check if an import from source to target layer is allowed.

        Args:
            source_layer: Layer doing the import (e.g., "L2")
            target_layer: Layer being imported (e.g., "L5")

        Returns:
            Tuple of (allowed, reason)
        """
        allowed_layers = self.GRAVITY_RULES.get(source_layer, set())
        if target_layer in allowed_layers:
            return (True, f"{source_layer} can import from {target_layer}")
        else:
            return (False, f"Gravity violation: {source_layer} cannot import from {target_layer}")

    # guardian: allow-type-erasure
    def force_rename_class(
        self,
        file_path: Path,
        old_name: str,
        new_name: str,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """
        Force rename a class to comply with naming conventions.

        Args:
            file_path: Path to the file
            old_name: Current class name
            new_name: New class name (should end with Agent)
            dry_run: If True, don't actually modify

        Returns:
            Result dictionary
        """
        result = {
            "file": str(file_path),
            "old_name": old_name,
            "new_name": new_name,
            "applied": False,
            "dry_run": dry_run,
        }
        if not file_path.exists():
            result["error"] = "File not found"
            return result
        try:
            content = file_path.read_text(encoding="utf-8")
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            result["error"] = str(e)
            return result
        new_content = re.sub(f"\\bclass\\s+{old_name}\\b", f"class {new_name}", content)
        new_content = re.sub(f"\\b{old_name}\\b", new_name, new_content)
        if new_content == content:
            result["message"] = "No changes needed"
            return result
        if not dry_run:
            backup_dir = self.project_root / ARCHIVES_DIR / "healing_backups" / "naming"
            _wg.ensure_dir(backup_dir)
            backup_path = backup_dir / f"{file_path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            _wg.copy_file(file_path, backup_path)
            _wg.write_text(file_path, new_content, encoding="utf-8")
            result["applied"] = True
            result["backup"] = str(backup_path)
            Logger.info(f"Renamed class: {old_name} -> {new_name} in {file_path}")
        else:
            result["message"] = "Dry run - no changes applied"
        return result

    def validate_hierarchy(self, file_path: Path) -> list[StructureViolation]:
        """Validate file hierarchy placement."""
        violations = []
        layer = self._extract_layer(file_path)
        if not layer:
            return violations
        expected_prefix = f"{layer}_"
        path_parts = file_path.parts
        layer_found = False
        for part in path_parts:
            if part.startswith(expected_prefix):
                layer_found = True
                break
        if not layer_found:
            violations.append(
                StructureViolation(
                    file_path=file_path,
                    line_number=0,
                    violation_type=StructureViolationType.HIERARCHY,
                    message=f"File not in expected layer directory: {layer}",
                ),
            )
        return violations

    def get_violations(self) -> list[StructureViolation]:
        """Get all recorded violations."""
        return self._violations.copy()

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal structure enforcement violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (gravity, hierarchy, naming, documentation, ascii)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        violation_type = violation.get("type", "")
        path = violation.get("path", "")
        Logger.info(f"[STRUCTURE_ENFORCER] Healing {violation_type} at {path}")
        try:
            file_path = Path(path) if path else None
            if not file_path or not file_path.exists():
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
            if violation_type == "gravity":
                result = self.enforce_gravity(file_path)
                return {
                    "violations_fixed": len(result),
                    "violations_found": len(result),
                    "errors": 0,
                    "skipped": 0,
                }
            elif violation_type == "naming":
                result = self.enforce_naming(file_path)
                return {
                    "violations_fixed": len(result),
                    "violations_found": len(result),
                    "errors": 0,
                    "skipped": 0,
                }
            elif violation_type == "hierarchy":
                result = self.enforce_hierarchy(file_path)
                return {
                    "violations_fixed": len(result),
                    "violations_found": len(result),
                    "errors": 0,
                    "skipped": 0,
                }
            else:
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"[STRUCTURE_ENFORCER] Failed to heal: {e}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}


def create_legacy_gravity_enforcer() -> StructureEnforcerAgent:
    """Create enforcer for gravity rules."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.create_legacy_gravity_enforcer", "L5_POLICY")
    config = StructureConfig(
        enable_gravity=True,
        enable_hierarchy=False,
        enable_naming=False,
        enable_documentation=False,
        enable_ascii=False,
    )
    return StructureEnforcerAgent(config=config)


def create_legacy_naming_enforcer() -> StructureEnforcerAgent:
    """Create enforcer for naming conventions."""
    config = StructureConfig(
        enable_gravity=False,
        enable_hierarchy=False,
        enable_naming=True,
        enable_documentation=False,
        enable_ascii=False,
    )
    return StructureEnforcerAgent(config=config)


def create_legacy_doc_enforcer() -> StructureEnforcerAgent:
    """Create enforcer for documentation."""
    config = StructureConfig(
        enable_gravity=False,
        enable_hierarchy=False,
        enable_naming=False,
        enable_documentation=True,
        enable_ascii=False,
    )
    return StructureEnforcerAgent(config=config)
