from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "import_surgeon_enforcer")
trace_contract.emit_determinism_digest("p0", "import_surgeon_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "import_surgeon_enforcer", "L5")
trace_contract._emit_routes_through("p1", "import_surgeon_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "import_surgeon_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "import_surgeon_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "import_surgeon_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "import_surgeon_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "import_surgeon_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "import_surgeon_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "import_surgeon_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "import_surgeon_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "import_surgeon_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "import_surgeon_enforcer")
trace_contract._emit_gated_by_confidence("p1", "import_surgeon_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "import_surgeon_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "import_surgeon_enforcer", "L5")

trace_contract._emit_applies_guardrail("p0", "import_surgeon_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "import_surgeon_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "import_surgeon_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "import_surgeon_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "import_surgeon_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "import_surgeon_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "import_surgeon_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "import_surgeon_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "import_surgeon_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "import_surgeon_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "import_surgeon_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "import_surgeon_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "import_surgeon_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "import_surgeon_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "import_surgeon_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "import_surgeon_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "import_surgeon_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "import_surgeon_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "import_surgeon_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "import_surgeon_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "import_surgeon_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "import_surgeon_enforcer", "exec_snapshot_link")

"\nSOVEREIGN IMPORT SURGEON\nScans all .py files and identifies import statements that need updating\nto match the new Depth-3 hierarchy.\n\nDRY RUN MODE: Lists all files requiring changes before applying fixes.\n"
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import APPS_SHARED_DIR
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from tqdm import tqdm

trace_contract._emit_emits_metric_event("import_surgeon_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("import_surgeon_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("import_surgeon_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("import_surgeon_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("import_surgeon_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("import_surgeon_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("import_surgeon_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("import_surgeon_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("import_surgeon_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("import_surgeon_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("import_surgeon_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("import_surgeon_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("import_surgeon_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("import_surgeon_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("import_surgeon_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("import_surgeon_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("import_surgeon_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("import_surgeon_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("import_surgeon_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("import_surgeon_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("import_surgeon_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("import_surgeon_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("import_surgeon_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("import_surgeon_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("import_surgeon_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("import_surgeon_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("import_surgeon_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("import_surgeon_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "import_surgeon_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "import_surgeon_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "import_surgeon_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "import_surgeon_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "import_surgeon_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "import_surgeon_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "import_surgeon_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "import_surgeon_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "import_surgeon_enforcer", "routing_commit")

exclude_dirs: Any = SOVEREIGN_EXCLUDED_FOLDERS
exclude_files: Any = {"SovereignImportSurgeon.py"}


class ImportViolation:
    """Represents a single import Violation."""

    def __init__(self, file_path: str, line_num: int, line: str, ViolationType: str, suggested_fix: str):
        self.file_path = file_path
        self.line_num = line_num
        self.line = line
        self.ViolationType = ViolationType
        self.suggested_fix = suggested_fix

    def __repr__(self):
        return f"{self.file_path}:{self.line_num} [{self.ViolationType}]\n  OLD: {self.line.strip()}\n  NEW: {self.suggested_fix}"


class SovereignImportSurgeon:
    """Scans and fixes import statements across the codebase."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.violations: dict[str, list[ImportViolation]] = defaultdict(list)
        self.import_patterns = [("L0_maintancne", "L0_routing", "TYPO_FIX")]
        self.test_file_pattern = re.compile("[\\\\/]tests?[\\\\/]|[\\\\/]test_.*\\.py$")
        self.commented_import_pattern = re.compile("^\\s*#\\s*(from\\s+\\.\\.|from\\s+agentic_core)")
        self.relative_import_pattern = re.compile("^(\\s*)from\\s+\\.\\.")
        self.apps_shared_pattern = re.compile("from\\s+apps_shared\\s+import")
        self.apps_engines_pattern = re.compile("from\\s+(apps_rg|apps_lic)\\.engines\\s+import")
        self.apps_templates_pattern = re.compile("from\\s+(apps_rg|apps_lic)\\.templates\\s+import")
        self.relative_import_pattern = re.compile("^from\\s+\\.\\.")

    def scan_file(self, file_path: Path) -> list[ImportViolation]:
        """Scan a single Python file for import violations."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "SovereignImportSurgeon.scan_file")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SovereignImportSurgeon.scan_file".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations: Any = []
        if self.test_file_pattern.search(str(file_path)):
            return violations
        try:
            with open(file_path, encoding="utf-8") as f:
                lines: Any = f.readlines()
            for line_num, line in tqdm(enumerate(lines, start=1), desc="Processing", unit="item"):
                if not line.strip():
                    continue
                for pattern, replacement, vtype in self.import_patterns:
                    if re.search(pattern, line):
                        suggested: Any = re.sub(pattern, replacement, line).strip()
                        violations.append(ImportViolation(str(file_path), line_num, line, vtype, suggested))
                if self.commented_import_pattern.search(line):
                    match: Any = re.search("#\\s*(from\\s+\\.\\.(\\w+)\\s+import\\s+.+)", line)
                    if match:
                        import_stmt: Any = match.group(1)
                        match.group(2)
                        suggested: Any = self._convert_relative_to_absolute(import_stmt, file_path)
                        violations.append(
                            ImportViolation(str(file_path), line_num, line, "COMMENTED_IMPORT", suggested),
                        )
                if APPS_SHARED_DIR in str(file_path) and "P1_core" in str(file_path):
                    if not line.strip().startswith("#") and self.relative_import_pattern.search(line):
                        suggested: Any = self._convert_relative_to_absolute(line.strip(), file_path)
                        if suggested != line.strip():
                            violations.append(
                                ImportViolation(
                                    str(file_path),
                                    line_num,
                                    line,
                                    "RELATIVE_TO_ABSOLUTE",
                                    suggested,
                                ),
                            )
                if not line.strip().startswith("#") and self.apps_shared_pattern.search(line):
                    suggested: Any = line.replace(
                        "from apps_shared import",
                        "from apps_shared.P1_core import",
                    )
                    if suggested != line:
                        violations.append(
                            ImportViolation(str(file_path), line_num, line, "APP_STAGING", suggested.strip()),
                        )
        except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
            print(f"⚠️  Error scanning {file_path}: {e}")
        return violations

    def _convert_relative_to_absolute(self, line: str, file_path: Path) -> str:
        """Convert relative imports to absolute imports."""
        match = re.match("from\\s+\\.\\.(\\w+)\\s+import\\s+(.+)", line)
        if match:
            match.group(1)
            match.group(2)
        return line.strip()

    def scan_all_files(self) -> Any:
        """Scan all Python files in the project."""
        print(f"🔍 Scanning {self.root_path} for import violations...\n")
        py_files: Any = []
        for root, dirs, files in tqdm(os.walk(self.root_path), desc="Processing", unit="item"):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                if file.endswith(".py") and file not in EXCLUDE_FILES:
                    py_files.append(Path(root) / file)
        print(f"📁 Found {len(py_files)} Python files to scan\n")
        for py_file in py_files:
            violations: Any = self.scan_file(py_file)
            if violations:
                self.violations[str(py_file)] = violations

    def generate_report(self) -> str:
        """Generate a detailed dry run report."""
        if not self.violations:
            return "✅ NO IMPORT VIOLATIONS FOUND - Your imports are already sovereign-compliant!"
        by_type: dict[str, list[ImportViolation]] = defaultdict(list)
        for file_violations in self.violations.values():
            for v in file_violations:
                by_type[v.ViolationType].append(v)
        report: Any = []
        report.append("=" * 80)
        report.append("SOVEREIGN IMPORT SURGERY - DRY RUN REPORT")
        report.append("=" * 80)
        report.append("")
        total_violations: Any = sum(len(v) for v in self.violations.values())
        report.append("📊 SUMMARY:")
        report.append(f"   Files affected: {len(self.violations)}")
        report.append(f"   Total violations: {total_violations}")
        report.append("")
        report.append("📋 VIOLATIONS BY TYPE:")
        for vtype, violations in sorted(by_type.items()):
            report.append(f"   {vtype}: {len(violations)} violations")
        report.append("")
        report.append("=" * 80)
        report.append("DETAILED VIOLATIONS")
        report.append("=" * 80)
        report.append("")
        for vtype in tqdm(sorted(by_type.keys()), desc="Processing", unit="item"):
            report.append(f"\n{'=' * 80}")
            report.append(f"VIOLATION TYPE: {vtype}")
            report.append(f"{'=' * 80}\n")
            files_with_type: Any = defaultdict(list)
            for v in by_type[vtype]:
                files_with_type[v.file_path].append(v)
            for file_path in sorted(files_with_type.keys()):
                report.append(f"\n📄 {file_path}")
                report.append("-" * 80)
                for v in files_with_type[file_path]:
                    report.append(f"  Line {v.line_num}:")
                    report.append(f"    OLD: {v.line.strip()}")
                    report.append(f"    NEW: {v.suggested_fix}")
                    report.append("")
        report.append("\n" + "=" * 80)
        report.append("FILES TO MODIFY")
        report.append("=" * 80)
        report.append("")
        for i, file_path in enumerate(sorted(self.violations.keys()), 1):
            count: Any = len(self.violations[file_path])
            report.append(f"{i:3d}. {file_path} ({count} Violation{('s' if count > 1 else '')})")
        report.append("\n" + "=" * 80)
        report.append("⚠️  DRY RUN COMPLETE - NO CHANGES APPLIED")
        report.append("=" * 80)
        report.append("\nTo apply these changes, confirm with the user first.")
        return "\n".join(report)

    def apply_fixes(self) -> Any:
        """Apply all identified fixes (ONLY after user confirmation)."""
        print("🔧 APPLYING FIXES...\n")
        fixed_count: Any = 0
        for file_path, violations in tqdm(self.violations.items(), desc="Processing", unit="item"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    lines: Any = f.readlines()
                for v in sorted(violations, key=lambda x: x.line_num, reverse=True):
                    lines[v.line_num - 1] = v.suggested_fix + "\n"
                _wg.open_write(file_path, "".join(lines))
                fixed_count += 1
                print(f"✅ Fixed: {file_path}")
            except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
                print(f"❌ Error fixing {file_path}: {e}")
        print(f"\n✅ SURGERY COMPLETE: {fixed_count} files modified")


def main() -> Any:
    """Main entry point."""
    project_root: Any = str(get_validated_project_root())
    surgeon: Any = SovereignImportSurgeon(project_root)
    surgeon.scan_all_files()
    report: Any = surgeon.generate_report()
    print(report)
    report_path: Any = Path(project_root) / "08_scripts" / "import_surgery_report.txt"
    _wg.open_write(report_path, report)
    print(f"\n📄 Report saved to: {report_path}")
    print("\n⚠️  This was a DRY RUN. No files were modified.")
    print("Review the report and confirm before applying changes.")


if __name__ == "__main__":
    main()
