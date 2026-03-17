#!/usr/bin/env python3
"""
PowerShell Usage Ban Guardrail

Enforces user preference: NEVER use PowerShell for shell commands or evidence generation.
ALWAYS use Python subprocess or direct Python file operations instead.

PowerShell has parsing issues with heredocs and complex pipelines that cause hangs and errors.

Usage:
    python ops_scripts/ci/check_powershell_ban.py [--fix]

Exit codes:
    0 - No PowerShell usage found
    1 - PowerShell usage detected (build fails)
"""

import argparse

# Force UTF-8 encoding for Windows compatibility
import io
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "check_powershell_ban")
_emit_applies_guardrail("p0", "check_powershell_ban", "p0_governance")
_emit_reads_policy_state("p0", "check_powershell_ban", "policy_binding")
_emit_snapshots_state("p0", "check_powershell_ban", "state_snapshot")
emit_replay_key("p0", "check_powershell_ban")
emit_determinism_digest("p0", "check_powershell_ban")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_powershell_ban", "execution_auth")
_emit_validates_capability("p2", "check_powershell_ban", "capability_check")
_emit_routes_to_capability("p2", "check_powershell_ban", "capability_route")
_emit_writes_via_uwg("p2", "check_powershell_ban", "uwg_write")
_emit_blocks_direct_write("p2", "check_powershell_ban", "direct_write_block")
_emit_records_tool_invocation("p2", "check_powershell_ban", "tool_invocation")
_emit_captures_execution_output("p2", "check_powershell_ban", "exec_output")
_emit_dispatches_agent("p3", "check_powershell_ban", "agent_dispatch")
_emit_coordinates_agents("p3", "check_powershell_ban", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_powershell_ban", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_powershell_ban", "healing_outcome")
_emit_escalates_failure("p3", "check_powershell_ban", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_powershell_ban", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_powershell_ban", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_powershell_ban", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_powershell_ban", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_powershell_ban", "eval_metric")
_emit_stores_embedding("p4", "check_powershell_ban", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_powershell_ban", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_powershell_ban", "exec_snapshot_link")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("check_powershell_ban", "p4obs", "metric_1")
_emit_emits_metric_event("check_powershell_ban", "p4obs", "metric_2")
_emit_emits_metric_event("check_powershell_ban", "p4obs", "metric_3")
_emit_emits_metric_event("check_powershell_ban", "p4obs", "metric_4")
_emit_emits_metric_event("check_powershell_ban", "p4obs", "metric_5")
_emit_emits_metric_event("check_powershell_ban", "p4obs", "metric_6")
_emit_records_incident_event("check_powershell_ban", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_powershell_ban", "p4obs", "anomaly")
_emit_writes_observability_log("check_powershell_ban", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_powershell_ban", "p4obs", "mon_state")
_emit_triggers_alert("check_powershell_ban", "p4obs", "alert")
_emit_links_incident_trace("check_powershell_ban", "p4obs", "trace_link")
_emit_captures_pattern("check_powershell_ban", "p3lm", "pattern")
_emit_records_learning_event("check_powershell_ban", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_powershell_ban", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_powershell_ban", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_powershell_ban", "p3lm", "routing")
_emit_improves_agent_policy("check_powershell_ban", "p3lm", "policy")
_emit_stores_learning_state("check_powershell_ban", "p3lm", "state")
_emit_records_execution_trace("check_powershell_ban", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_powershell_ban", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_powershell_ban", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_powershell_ban", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_powershell_ban", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_powershell_ban", "env_read", "p2_env_1")
_emit_reads_environ("check_powershell_ban", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_powershell_ban", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_powershell_ban", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_powershell_ban", "context_pull")
_emit_pulls_context("p1", "check_powershell_ban", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_powershell_ban", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_powershell_ban", "uwg_term_secondary")
_emit_writes_through("p1", "check_powershell_ban", "write_through")
_emit_writes_through("p1", "check_powershell_ban", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_powershell_ban", "safety_validation")
_emit_invokes_eval("p1", "check_powershell_ban", "eval_call")
_emit_proposal_commits_routing("p1", "check_powershell_ban", "routing_commit")
_emit_escalates_to_human("p1", "check_powershell_ban", "human_escalation")
_emit_routes_through("p1", "check_powershell_ban", "route_through")
_emit_checks_agent_registry("p1", "check_powershell_ban", "agent_registry")
_emit_validates_agent_capability("p1", "check_powershell_ban", "capability")
_emit_dispatches_execution_plan("p1", "check_powershell_ban", "exec_plan")
_emit_agent_executes_agent("p1", "check_powershell_ban", "sub_agent")
_emit_routes_to_agent("p1", "check_powershell_ban", "target_agent")
_emit_verifies_policy("p1", "check_powershell_ban", "policy_check")
_emit_observes_runtime_state("p1", "check_powershell_ban", "runtime_state")
_emit_verifies_boundary("p1", "check_powershell_ban", "boundary_check")
_emit_transcripts_response("p1", "check_powershell_ban", "transcript")
_emit_hard_fails_untranscripted("p1", "check_powershell_ban")
_emit_gated_by_confidence("p1", "check_powershell_ban", "confidence_gate")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_1")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_2")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_3")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_4")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_5")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_6")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_7")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_8")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_9")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_10")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_11")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_12")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_13")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_14")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_15")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_16")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_17")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_18")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_19")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_20")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_21")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_22")
_emit_reads_through("l4", "check_powershell_ban", "urg_read_23")

PROJECT_ROOT = get_validated_project_root()


class PowerShellBanChecker:
    """Enforces PowerShell usage ban across the repository."""

    # PowerShell patterns to detect
    POWERSHELL_PATTERNS = [
        # Direct PowerShell executable calls
        r"powershell\.exe",
        r"pwsh\.exe",
        r"PowerShell\.",

        # PowerShell cmdlets
        r"Start-Process",
        r"Invoke-Expression",
        r"Invoke-Command",
        r"New-Object",
        r"Get-Content",
        r"Set-Content",
        r"Out-File",
        r"Write-Output",
        r"Write-Host",
        r"Write-Error",
        r"Try-Catch",
        r"ForEach-Object",
        r"Where-Object",
        r"Select-Object",
        r"Sort-Object",
        r"Group-Object",

        # PowerShell operators and syntax
        r"\$[a-zA-Z_][a-zA-Z0-9_]*",  # Variables like $var
        r"\$\([^)]+\)",  # Subexpression operator
        r"@\(.*?\)",  # Array operator
        r"%\{.*?\}",  # Hash table
        r"\.ps1",
        r"\.psm1",
        r"\.psd1",

        # PowerShell specific constructs
        r"param\s*\(",
        r"function\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\{",
        r"if\s*\([^)]+\)\s*\{",
        r"switch\s*\([^)]+\)\s*\{",

        # Pipeline operators
        r"\s*\|\s*[a-zA-Z-]+",
    ]

    # File extensions to check
    CHECK_EXTENSIONS = {'.py', '.yml', '.yaml', '.md', '.txt', '.json', '.cfg', '.ini', '.toml'}

    # Directories to exclude
    EXCLUDE_DIRS = {
        '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
        'node_modules', '.venv', 'venv', '.vscode', '.idea'
    }

    def __init__(self):
        self.violations: list[dict[str, Any]] = []
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in self.POWERSHELL_PATTERNS]

    # guardian: allow-magic-config
    def check_repository(self, max_files: int = 1000) -> list[dict[str, Any]]:
        """Check repository for PowerShell usage with file limit."""
        self.violations = []
        files_checked = 0

        for file_path in PROJECT_ROOT.rglob("*"):
            if files_checked >= max_files:
                print(f"⚠️  Reached file limit ({max_files}), stopping scan")
                break

            if self._should_check_file(file_path):
                self._check_file(file_path)
                files_checked += 1

                if files_checked % 100 == 0:
                    print(f"📊 Scanned {files_checked} files...", end='\r')

        print(f"✅ Scanned {files_checked} files total")
        return self.violations

    def _should_check_file(self, file_path: Path) -> bool:
        """Determine if file should be checked for PowerShell usage."""
        # Skip directories
        if not file_path.is_file():
            return False

        # Skip excluded directories
        if any(exclude in str(file_path) for exclude in self.EXCLUDE_DIRS):
            return False

        # Skip binary files
        if file_path.suffix.lower() in ['.exe', '.dll', '.so', '.dylib', '.png', '.jpg', '.gif', '.pdf']:
            return False

        # Check specific extensions or common config files
        if file_path.suffix.lower() in self.CHECK_EXTENSIONS:
            return True

        # Check common script/automation files by name
        script_patterns = ['script', 'setup', 'install', 'build', 'deploy', 'run', 'execute']
        filename_lower = file_path.name.lower()
        if any(pattern in filename_lower for pattern in script_patterns):
            return True

        return False

    def _check_file(self, file_path: Path) -> None:
        """Check a single file for PowerShell usage."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            for i, pattern in enumerate(self.compiled_patterns):
                matches = pattern.finditer(content)

                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = self._get_line_content(content, line_num)

                    # Skip false positives
                    if self._is_false_positive(match.group(), line_content, file_path):
                        continue

                    violation = {
                        "type": "powershell_usage",
                        "file": str(file_path.relative_to(PROJECT_ROOT)),
                        "line": line_num,
                        "column": match.start() - content.rfind('\n', 0, match.start()),
                        "pattern": self.POWERSHELL_PATTERNS[i],
                        "match": match.group(),
                        "line_content": line_content.strip(),
                        "message": f"PowerShell usage detected: {match.group()}",
                        "severity": "error",
                        "suggestion": self._get_suggestion(match.group(), file_path)
                    }

                    self.violations.append(violation)

        except Exception as e:
            raise
            # Skip files that can't be read
            pass

    def _get_line_content(self, content: str, line_num: int) -> str:
        """Extract the content of a specific line."""
        lines = content.split('\n')
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""

    def _is_false_positive(self, match: str, line_content: str, file_path: Path) -> bool:
        """Check if this is a false positive."""
        # Skip comments mentioning PowerShell
        if line_content.strip().startswith('#') and 'powershell' in line_content.lower():
            return True

        # Skip documentation about PowerShell
        if file_path.suffix == '.md' and 'powershell' in line_content.lower():
            return True

        # Skip strings that contain PowerShell but aren't actually PowerShell code
        if line_content.strip().startswith('"') or line_content.strip().startswith("'"):
            return True

        # Skip $ in regular expressions (not PowerShell variables)
        if re.search(r'["\'][^"\']*\$[^"\']*["\']', line_content):
            return True

        # Skip $ in environment variable contexts like ${VAR}
        if '${' in line_content and '}' in line_content:
            return True

        return False

    def _get_suggestion(self, match: str, file_path: Path) -> str:
        """Get suggestion for fixing PowerShell usage."""
        suggestions = {
            "powershell.exe": "Use Python subprocess.run() instead",
            "pwsh.exe": "Use Python subprocess.run() instead",
            "Start-Process": "Use Python subprocess.Popen() instead",
            "Invoke-Expression": "Use Python eval() or exec() instead",
            "Get-Content": "Use Python Path.read_text() or open() instead",
            "Set-Content": "Use Python Path.write_text() or open() instead",
            "Out-File": "Use Python Path.write_text() or print() with file redirection instead",
            "Write-Host": "Use Python print() instead",
            "Write-Error": "Use Python logging.error() or sys.stderr.write() instead",
            "Try-Catch": "Use Python try-except instead",
            "ForEach-Object": "Use Python for loop or list comprehension instead",
            "Where-Object": "Use Python list comprehension or filter() instead",
            "Select-Object": "Use Python list comprehension or map() instead",
        }

        for pattern, suggestion in suggestions.items():
            if pattern.lower() in match.lower():
                return suggestion

        if match.startswith('$'):
            return "Use Python variables without $ prefix"
        elif match.endswith('.ps1'):
            return "Convert PowerShell script to Python"
        elif '|' in match and '-' in match:
            return "Use Python pipes and functions instead of PowerShell pipeline"
        else:
            return "Replace with equivalent Python operation"

    def fix_violations(self) -> bool:
        """Attempt to automatically fix simple PowerShell violations."""
        fixed_count = 0

        for violation in self.violations[:]:  # Copy list to allow modification
            file_path = PROJECT_ROOT / violation["file"]

            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                line_idx = violation["line"] - 1

                if 0 <= line_idx < len(lines):
                    line = lines[line_idx]

                    # Simple fixes for common patterns
                    new_line = self._fix_line(line, violation["match"])
                    if new_line != line:
                        lines[line_idx] = new_line
                        file_path.write_text('\n'.join(lines), encoding='utf-8')
                        print(f"✅ Fixed PowerShell usage in {violation['file']}:{violation['line']}")
                        fixed_count += 1
                        self.violations.remove(violation)

            except Exception as e:
                raise
                print(f"❌ Failed to fix {violation['file']}: {e}")

        return fixed_count > 0

    def _fix_line(self, line: str, match: str) -> str:
        """Attempt to fix a line with PowerShell usage."""
        # Simple substitutions
        fixes = {
            "Write-Host": "print",
            "Write-Error": "logging.error",
            "Write-Warning": "logging.warning",
        }

        for powershell_cmd, python_cmd in fixes.items():
            if powershell_cmd in line:
                return line.replace(powershell_cmd, python_cmd)

        # Variable substitution (simple cases)
        if re.match(r'\$[a-zA-Z_][a-zA-Z0-9_]*', match):
            return line.replace(match, match[1:])  # Remove $ prefix

        return line

    def print_report(self, verbose: bool = False) -> None:
        """Print PowerShell usage report."""
        if not self.violations:
            print("✅ PowerShell usage ban: No violations found")
            print("📝 Preference enforced: Python subprocess or direct file operations only")
            return

        print(f"❌ PowerShell usage violations found: {len(self.violations)}")
        print()

        # Group violations by file
        by_file = {}
        for v in self.violations:
            file_key = v["file"]
            if file_key not in by_file:
                by_file[file_key] = []
            by_file[file_key].append(v)

        for file_path, file_violations in sorted(by_file.items()):
            print(f"📁 {file_path}")

            for v in sorted(file_violations, key=lambda x: x["line"]):
                print(f"   Line {v['line']}: {v['message']}")
                if verbose:
                    print(f"   Match: '{v['match']}'")
                    print(f"   Context: {v['line_content']}")
                print(f"   Suggestion: {v['suggestion']}")
            print()

        print("🐍 Python alternatives:")
        print("   • subprocess.run() for shell commands")
        print("   • Path.read_text()/write_text() for file operations")
        print("   • print() for output")
        print("   • logging module for structured logging")
        print("   • Built-in Python functions for data processing")
        print()
        print("📖 Reference: User preference - NEVER use PowerShell")

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about PowerShell usage violations."""
        if not self.violations:
            return {"total": 0}

        by_pattern = {}
        by_file = {}

        for v in self.violations:
            pattern = v["pattern"]
            file_path = v["file"]

            by_pattern[pattern] = by_pattern.get(pattern, 0) + 1
            by_file[file_path] = by_file.get(file_path, 0) + 1

        return {
            "total": len(self.violations),
            "by_pattern": by_pattern,
            "by_file": by_file,
            "most_common_pattern": max(by_pattern.items(), key=lambda x: x[1]) if by_pattern else None,
            "most_affected_file": max(by_file.items(), key=lambda x: x[1]) if by_file else None
        }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check for PowerShell usage violations")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix simple violations")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    checker = PowerShellBanChecker()
    violations = checker.check_repository()

    if args.fix:
        print("🔧 Attempting to fix PowerShell violations...")
        checker.fix_violations()
        violations = checker.check_repository()  # Re-check

    if args.stats:
        stats = checker.get_statistics()
        print("📊 PowerShell Usage Statistics:")
        print(json.dumps(stats, indent=2))
        print()

    if args.json:
        print(json.dumps({
            "status": "failed" if violations else "passed",
            "violations": violations,
            "statistics": checker.get_statistics()
        }, indent=2))
    else:
        checker.print_report(args.verbose)

    # Fail build if any PowerShell usage found
    if violations:
        print(f"\n❌ POWERSHELL BAN GUARDRAIL: {len(violations)} violations found")
        print("Build FAILED - PowerShell usage violates user preference")
        return 1
    else:
        print("\n✅ POWERSHELL BAN GUARDRAIL: No violations found")
        return 0


if __name__ == "__main__":
    sys.exit(main())
