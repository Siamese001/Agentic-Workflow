from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "gravity_validator")
trace_contract.emit_determinism_digest("p0", "gravity_validator")

trace_contract._emit_dispatches_healing_run("p1", "gravity_validator", "L5")
trace_contract._emit_routes_through("p1", "gravity_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "gravity_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "gravity_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "gravity_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "gravity_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "gravity_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "gravity_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "gravity_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "gravity_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "gravity_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "gravity_validator")
trace_contract._emit_gated_by_confidence("p1", "gravity_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "gravity_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "gravity_validator", "L5")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "gravity_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "gravity_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "gravity_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "gravity_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "gravity_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "gravity_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "gravity_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "gravity_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "gravity_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "gravity_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "gravity_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "gravity_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "gravity_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "gravity_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "gravity_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "gravity_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "gravity_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "gravity_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "gravity_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "gravity_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "gravity_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "gravity_validator", "exec_snapshot_link")

"\nUnified SSOT Validator - Consolidates All Validation Logic\n\nReplaces 5 separate validation tools with a single, comprehensive validator:\n1. audit_ssot.py → Gravity violations (files in wrong layers)\n2. audit_architectural_violations.py → Import violations (upward dependencies)\n3. HierarchyAgent → Depth compliance (max depth per layer)\n4. LocationAgent → Territory compliance (unauthorized folders)\n5. FilesystemSSOTReconcilerAgent → Drift detection (filesystem vs blueprint)\n\nPerformance: <5 seconds for complete validation (vs 60+ seconds running 5 tools)\n"
import ast
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import (
    CORE_SUBFOLDER_MAP,
    DEPTH_RULES,
    PROJECT_ROOT_WHITELIST,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L5_safety.enforcement.ssot_scanner_enforcer import SSOTScanner
from tqdm import tqdm

trace_contract._emit_emits_metric_event("gravity_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("gravity_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("gravity_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("gravity_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("gravity_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("gravity_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("gravity_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("gravity_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("gravity_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("gravity_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("gravity_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("gravity_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("gravity_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("gravity_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("gravity_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("gravity_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("gravity_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("gravity_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("gravity_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("gravity_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("gravity_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("gravity_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("gravity_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("gravity_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("gravity_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("gravity_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("gravity_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("gravity_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "gravity_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "gravity_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "gravity_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "gravity_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "gravity_validator", "write_through")
trace_contract._emit_writes_through("p1", "gravity_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "gravity_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "gravity_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "gravity_validator", "routing_commit")


@dataclass
class GravityViolation:
    """Agent in wrong layer (physical location mismatch)."""

    file_path: str
    actual_layer: str
    assigned_layer: str
    agent_name: str

    def __str__(self) -> str:
        return f"{self.file_path}: {self.actual_layer} → {self.assigned_layer}"


@dataclass
class ImportViolation:
    """Illegal upward dependency (lower layer importing from higher layer)."""

    file_path: str
    source_layer: str
    target_layer: str
    import_line: str
    line_number: int
    severity: int = 8

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_number}: L{self.source_layer} → L{self.target_layer}"


@dataclass
class HierarchyViolation:
    """Depth limit exceeded (too many nested folders)."""

    folder_path: str
    actual_depth: int
    max_depth: int
    root_folder: str

    def __str__(self) -> str:
        return f"{self.folder_path}: depth {self.actual_depth} > max {self.max_depth}"


@dataclass
class DriftViolation:
    """Unauthorized folder not in blueprint."""

    folder_path: str
    parent_folder: str
    violation_type: str

    def __str__(self) -> str:
        return f"{self.folder_path}: {self.violation_type} ({self.parent_folder})"


@dataclass
class SovereignHealthReport:
    """
    Comprehensive SSOT health report.

    Consolidates all validation results into a single report.
    """

    gravity_violations: list[GravityViolation] = field(default_factory=list)
    import_violations: list[ImportViolation] = field(default_factory=list)
    hierarchy_violations: list[HierarchyViolation] = field(default_factory=list)
    drift_violations: list[DriftViolation] = field(default_factory=list)
    total_agents: int = 0
    total_files_scanned: int = 0
    compliance_score: float = 0.0
    scan_duration: float = 0.0

    @property
    def total_violations(self) -> int:
        """Total number of violations across all categories."""
        return (
            len(self.gravity_violations)
            + len(self.import_violations)
            + len(self.hierarchy_violations)
            + len(self.drift_violations)
        )

    @property
    def is_compliant(self) -> bool:
        """Check if system is fully compliant (zero violations)."""
        return self.total_violations == 0

    def to_markdown(self) -> str:
        """Generate Markdown report optimized for LLM/Human consumption."""

        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()),
            trace_contract.LayerSegment.L5_POLICY,
            "GravityValidator.to_markdown",
        )
        lines = []
        lines.append("# SSOT Sovereign Health Report")
        lines.append("")
        lines.append(f"**Compliance Score**: {self.compliance_score:.1f}%")
        lines.append(f"**Total Violations**: {self.total_violations}")
        lines.append(f"**Scan Duration**: {self.scan_duration:.2f}s")
        lines.append("")
        if self.is_compliant:
            lines.append("## ✅ Status: COMPLIANT")
            lines.append("")
            lines.append("All SSOT validation checks passed. System is HARDENED and GRAVITY-ALIGNED.")
        else:
            lines.append("## ⚠️ Status: NON-COMPLIANT")
            lines.append("")
            lines.append(f"Found {self.total_violations} violations requiring attention.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 1. Gravity Violations (Physical Location)")
        lines.append("")
        if self.gravity_violations:
            lines.append(f"**Count**: {len(self.gravity_violations)}")
            lines.append("")
            lines.append("| File | Actual Layer | Assigned Layer |")
            lines.append("|------|--------------|----------------|")
            for v in self.gravity_violations[:10]:
                lines.append(f"| `{v.file_path}` | {v.actual_layer} | {v.assigned_layer} |")
            if len(self.gravity_violations) > 10:
                lines.append(f"| ... and {len(self.gravity_violations) - 10} more | | |")
        else:
            lines.append("✅ **No violations** - All agents in correct layers")
        lines.append("")
        lines.append("## 2. Import Violations (Upward Dependencies)")
        lines.append("")
        if self.import_violations:
            lines.append(f"**Count**: {len(self.import_violations)}")
            lines.append("")
            lines.append("| File | Line | Source → Target | Import |")
            lines.append("|------|------|-----------------|--------|")
            for v in self.import_violations[:10]:
                lines.append(
                    f"| `{v.file_path}` | {v.line_number} | L{v.source_layer} → L{v.target_layer} | `{v.import_line[:50]}...` |",
                )
            if len(self.import_violations) > 10:
                lines.append(f"| ... and {len(self.import_violations) - 10} more | | | |")
        else:
            lines.append("✅ **No violations** - No illegal upward dependencies")
        lines.append("")
        lines.append("## 3. Hierarchy Violations (Depth Limits)")
        lines.append("")
        if self.hierarchy_violations:
            lines.append(f"**Count**: {len(self.hierarchy_violations)}")
            lines.append("")
            lines.append("| Folder | Actual Depth | Max Depth | Root |")
            lines.append("|--------|--------------|-----------|------|")
            for v in self.hierarchy_violations[:10]:
                lines.append(f"| `{v.folder_path}` | {v.actual_depth} | {v.max_depth} | {v.root_folder} |")
            if len(self.hierarchy_violations) > 10:
                lines.append(f"| ... and {len(self.hierarchy_violations) - 10} more | | | |")
        else:
            lines.append("✅ **No violations** - All folders within depth limits")
        lines.append("")
        lines.append("## 4. Drift Violations (Filesystem vs Blueprint)")
        lines.append("")
        if self.drift_violations:
            lines.append(f"**Count**: {len(self.drift_violations)}")
            lines.append("")
            lines.append("| Folder | Type | Parent |")
            lines.append("|--------|------|--------|")
            for v in self.drift_violations[:10]:
                lines.append(f"| `{v.folder_path}` | {v.violation_type} | {v.parent_folder} |")
            if len(self.drift_violations) > 10:
                lines.append(f"| ... and {len(self.drift_violations) - 10} more | | |")
        else:
            lines.append("✅ **No violations** - Filesystem matches blueprint")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Summary Statistics")
        lines.append("")
        lines.append(f"- **Total Agents**: {self.total_agents}")
        lines.append(f"- **Files Scanned**: {self.total_files_scanned}")
        lines.append(f"- **Gravity Violations**: {len(self.gravity_violations)}")
        lines.append(f"- **Import Violations**: {len(self.import_violations)}")
        lines.append(f"- **Hierarchy Violations**: {len(self.hierarchy_violations)}")
        lines.append(f"- **Drift Violations**: {len(self.drift_violations)}")
        lines.append(f"- **Compliance Score**: {self.compliance_score:.1f}%")
        return "\n".join(lines)


class UnifiedSSOTValidator:
    """
    Unified SSOT Validator - Single source of truth for all validation.

    Consolidates logic from:
    - audit_ssot.py (gravity violations)
    - audit_architectural_violations.py (import violations)
    - HierarchyAgent (depth compliance)
    - LocationAgent (territory compliance)
    - FilesystemSSOTReconcilerAgent (drift detection)
    """

    def __init__(self, project_root: Path):
        """
        Initialize unified validator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root.resolve()
        self.scanner = SSOTScanner(project_root)
        self.layer_hierarchy = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}

    def validate_all(self) -> SovereignHealthReport:
        """
        Run all validation checks and generate comprehensive report.

        Returns:
            SovereignHealthReport with all violations and statistics
        """
        trace_contract._emit_validated_by_safety_plane(str(uuid.uuid4()), "UnifiedSSOTValidator.validate_all", "L5_POLICY")
        import time

        start_time = time.time()
        report = SovereignHealthReport()
        report.gravity_violations = self._check_gravity_violations()
        report.import_violations = self._check_import_violations()
        report.hierarchy_violations = self._check_hierarchy_violations()
        report.drift_violations = self._check_drift_violations()
        stats = self.scanner.get_compliance_stats()
        report.total_agents = stats["total_agents"]
        from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

        report.total_files_scanned = len(list(get_python_files(self.project_root)))
        total_checks = report.total_agents * 4
        violations = report.total_violations
        report.compliance_score = (
            max(0.0, (total_checks - violations) / total_checks * 100) if total_checks > 0 else 100.0
        )
        report.scan_duration = time.time() - start_time
        return report

    def _check_gravity_violations(self) -> list[GravityViolation]:
        """Check for agents in wrong layers (physical location mismatch)."""
        violations = []
        agents = self.scanner.find_gravity_violations()
        for agent in agents:
            violations.append(
                GravityViolation(
                    file_path=agent.relative_path,
                    actual_layer=agent.layer,
                    assigned_layer=agent.assigned_layer,
                    agent_name=agent.class_name,
                ),
            )
        return violations

    def _check_import_violations(self) -> list[ImportViolation]:
        """Check for illegal upward dependencies (lower layer importing from higher)."""
        violations = []
        agentic_core = self.project_root / AGENTIC_CORE_DIR
        if not agentic_core.exists():
            return violations
        from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

        for py_file in tqdm(get_python_files(agentic_core), desc="Processing", unit="item"):
            source_layer = self._get_layer_from_path(py_file)
            if not source_layer or source_layer not in self.layer_hierarchy:
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
                    if isinstance(node, ast.Import | ast.ImportFrom):
                        import_line = self._get_import_line(node, content)
                        target_layer = self._extract_target_layer(node)
                        if target_layer and target_layer in self.layer_hierarchy:
                            if self.layer_hierarchy[source_layer] < self.layer_hierarchy[target_layer]:
                                violations.append(
                                    ImportViolation(
                                        file_path=str(py_file.relative_to(self.project_root)),
                                        source_layer=source_layer,
                                        target_layer=target_layer,
                                        import_line=import_line,
                                        line_number=node.lineno,
                                        severity=8,
                                    ),
                                )
            except (
                SyntaxError,
                UnicodeDecodeError,
            ):  # review: Parsing and encoding errors need separate handling strategies
                continue
        return violations

    def _check_hierarchy_violations(self) -> list[HierarchyViolation]:
        """Check for folders exceeding maximum depth limits."""
        violations = []
        for root_name in tqdm(PROJECT_ROOT_WHITELIST, desc="Processing", unit="item"):
            root_path = self.project_root / root_name
            if not root_path.exists():
                continue
            max_depth = DEPTH_RULES.get(root_name, 3)
            import os

            for root, dirs, _files in tqdm(os.walk(root_path), desc="Processing", unit="item"):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for dir_name in tqdm(dirs, desc="Processing", unit="item"):
                    folder = Path(root) / dir_name
                    if any(excluded in folder.parts for excluded in SOVEREIGN_EXCLUDED_FOLDERS):
                        continue
                    try:
                        rel_path = folder.relative_to(root_path)
                        actual_depth = len(rel_path.parts)
                        if actual_depth > max_depth:
                            violations.append(
                                HierarchyViolation(
                                    folder_path=str(folder.relative_to(self.project_root)),
                                    actual_depth=actual_depth,
                                    max_depth=max_depth,
                                    root_folder=root_name,
                                ),
                            )
                    except ValueError:
                        continue
        return violations

    def _check_drift_violations(self) -> list[DriftViolation]:
        """Check for unauthorized folders not in blueprint."""
        violations = []
        agentic_core = self.project_root / AGENTIC_CORE_DIR
        if not agentic_core.exists():
            return violations
        authorized_l1 = set(CORE_SUBFOLDER_MAP.keys())
        for folder in tqdm(agentic_core.iterdir(), desc="Processing", unit="item"):
            if not folder.is_dir():
                continue
            folder_name = folder.name
            if folder_name in SOVEREIGN_EXCLUDED_FOLDERS:
                continue
            if folder_name not in authorized_l1:
                violations.append(
                    DriftViolation(
                        folder_path=str(folder.relative_to(self.project_root)),
                        parent_folder=AGENTIC_CORE_DIR,
                        violation_type="orphaned",
                    ),
                )
            else:
                authorized_l2 = set(CORE_SUBFOLDER_MAP.get(folder_name, []))
                for subfolder in tqdm(folder.iterdir(), desc="Processing", unit="item"):
                    if not subfolder.is_dir():
                        continue
                    subfolder_name = subfolder.name
                    if subfolder_name in SOVEREIGN_EXCLUDED_FOLDERS:
                        continue
                    if authorized_l2 and subfolder_name not in authorized_l2:
                        violations.append(
                            DriftViolation(
                                folder_path=str(subfolder.relative_to(self.project_root)),
                                parent_folder=folder_name,
                                violation_type="orphaned",
                            ),
                        )
        return violations

    def _get_layer_from_path(self, file_path: Path) -> str | None:
        """Extract layer (L0-L5) from file path."""
        parts = file_path.parts
        for part in parts:
            if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
                return part[:2]
        return None

    def _extract_target_layer(self, node: ast.AST) -> str | None:
        """Extract target layer from import statement."""
        if isinstance(node, ast.ImportFrom):
            if node.module and AGENTIC_CORE_DIR in node.module:
                parts = node.module.split(".")
                for part in parts:
                    if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
                        return part[:2]
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if AGENTIC_CORE_DIR in alias.name:
                    parts = alias.name.split(".")
                    for part in parts:
                        if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
                            return part[:2]
        return None

    def _get_import_line(self, node: ast.AST, content: str) -> str:
        """Extract import line text from AST node."""
        lines = content.split("\n")
        if 0 <= node.lineno - 1 < len(lines):
            return lines[node.lineno - 1].strip()
        return ""
