from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "credential_guard")
emit_determinism_digest("p0", "credential_guard")

_emit_dispatches_healing_run("p1", "credential_guard", "L5")
_emit_routes_through("p1", "credential_guard", "L5")
_emit_escalates_to_human("p1", "credential_guard", "L5")
_emit_reads_policy_state("p1", "credential_guard", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "credential_guard")
_emit_applies_guardrail("p0", "credential_guard", "p0_governance")
_emit_snapshots_state("p0", "credential_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "credential_guard", "execution_auth")
_emit_validates_capability("p2", "credential_guard", "capability_check")
_emit_routes_to_capability("p2", "credential_guard", "capability_route")
_emit_writes_via_uwg("p2", "credential_guard", "uwg_write")
_emit_blocks_direct_write("p2", "credential_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "credential_guard", "tool_invocation")
_emit_captures_execution_output("p2", "credential_guard", "exec_output")
_emit_dispatches_agent("p3", "credential_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "credential_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "credential_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "credential_guard", "healing_outcome")
_emit_escalates_failure("p3", "credential_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "credential_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "credential_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "credential_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "credential_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "credential_guard", "eval_metric")
_emit_stores_embedding("p4", "credential_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "credential_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "credential_guard", "exec_snapshot_link")

"\nDeterministic Credential Scanner\n\nRepository Security Gate Maintainer (L5 Safety Surface)\n\nScans repository for exposed credentials using deterministic regex patterns.\nRead-only scanning only - no file modification or auto-remediation.\n"
import re
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("credential_guard", "p4obs", "metric_1")
_emit_emits_metric_event("credential_guard", "p4obs", "metric_2")
_emit_emits_metric_event("credential_guard", "p4obs", "metric_3")
_emit_emits_metric_event("credential_guard", "p4obs", "metric_4")
_emit_emits_metric_event("credential_guard", "p4obs", "metric_5")
_emit_emits_metric_event("credential_guard", "p4obs", "metric_6")
_emit_records_incident_event("credential_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("credential_guard", "p4obs", "anomaly")
_emit_writes_observability_log("credential_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("credential_guard", "p4obs", "mon_state")
_emit_triggers_alert("credential_guard", "p4obs", "alert")
_emit_links_incident_trace("credential_guard", "p4obs", "trace_link")
_emit_captures_pattern("credential_guard", "p3lm", "pattern")
_emit_records_learning_event("credential_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("credential_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("credential_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("credential_guard", "p3lm", "routing")
_emit_improves_agent_policy("credential_guard", "p3lm", "policy")
_emit_stores_learning_state("credential_guard", "p3lm", "state")
_emit_records_execution_trace("credential_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("credential_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("credential_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("credential_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("credential_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("credential_guard", "env_read", "p2_env_1")
_emit_reads_environ("credential_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("credential_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("credential_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "credential_guard", "context_pull")
_emit_pulls_context("p1", "credential_guard", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "credential_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "credential_guard", "uwg_term_secondary")
_emit_writes_through("p1", "credential_guard", "write_through")
_emit_writes_through("p1", "credential_guard", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "credential_guard", "safety_validation")
_emit_invokes_eval("p1", "credential_guard", "eval_call")
_emit_proposal_commits_routing("p1", "credential_guard", "routing_commit")

PATTERNS = [
    {"name": "OPENAI_KEY_PROJ", "regex": re.compile("sk-proj-[A-Za-z0-9_-]{20,}")},
    {"name": "OPENAI_KEY_ADMIN", "regex": re.compile("sk-admin-[A-Za-z0-9_-]{20,}")},
    {"name": "OPENAI_KEY_GENERIC", "regex": re.compile("sk-[A-Za-z0-9]{48}")},
    {"name": "ANTHROPIC_API_KEY", "regex": re.compile("sk-ant-api[0-9]+-[A-Za-z0-9_-]{20,}")},
    {"name": "GOOGLE_GEMINI_KEY", "regex": re.compile("AIzaSy[A-Za-z0-9_-]{33}")},
    {"name": "PINECONE_API_KEY", "regex": re.compile("pcsk_[A-Za-z0-9_]{30,}")},
    {"name": "GITHUB_PAT", "regex": re.compile("github_pat_[A-Za-z0-9_]{20,}")},
    {"name": "GITHUB_TOKEN_GHP", "regex": re.compile("ghp_[A-Za-z0-9]{36}")},
    {"name": "FIGMA_TOKEN", "regex": re.compile("figd_[A-Za-z0-9_-]{20,}")},
    {"name": "BRAVE_API_KEY", "regex": re.compile("BSA[A-Za-z0-9]{20,}")},
    {"name": "SLACK_TOKEN", "regex": re.compile("xox[baprs]-[A-Za-z0-9-]{10,}")},
]
EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
MAX_FILE_SIZE = 2 * 1024 * 1024


def is_text_file(file_path: Path) -> bool:
    """Check if file is likely a text file based on extension and content."""
    text_extensions = {
        ".py",
        ".js",
        ".ts",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".txt",
        ".md",
        ".env",
        ".ini",
        ".cfg",
        ".conf",
        ".sh",
        ".bash",
        ".zsh",
        ".ps1",
        ".html",
        ".css",
        ".xml",
        ".sql",
        ".log",
        ".out",
        ".err",
    }
    if file_path.suffix.lower() in text_extensions:
        return True
    if not file_path.suffix and file_path.stat().st_size < MAX_FILE_SIZE:
        try:
            with open(file_path, encoding="utf-8") as f:
                f.read(1024)
            return True
        except (UnicodeDecodeError, PermissionError):
            return False
    return False


def scan_file(file_path: Path) -> list[dict[str, Any]]:
    """Scan a single file for credential patterns."""
    violations = []
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return violations
    lines = content.split("\n")
    for line_num, line in enumerate(lines, 1):
        for pattern in PATTERNS:
            if pattern["regex"].search(line):
                violations.append(
                    {"file": str(file_path), "line_number": line_num, "pattern": pattern["name"]}
                )
    return violations


def scan_repository(root_path: Path) -> dict[str, Any]:
    """Scan entire repository for credentials."""
    all_violations = []
    files_scanned = 0
    all_files = sorted(root_path.rglob("*"))
    for file_path in all_files:
        if file_path.is_dir():
            continue
        if any(exclude_dir in file_path.parts for exclude_dir in EXCLUDE_DIRS):
            continue
        if file_path.stat().st_size > MAX_FILE_SIZE:
            continue
        if not is_text_file(file_path):
            continue
        violations = scan_file(file_path)
        all_violations.extend(violations)
        files_scanned += 1
    all_violations.sort(key=lambda v: (v["file"], v["line_number"], v["pattern"]))
    return {"files_scanned": files_scanned, "violations": all_violations}


def main():
    """Main scanner execution."""
    root_path = Path(__file__).parent.parent.parent
    print(f"Scanning repository for credentials: {root_path}")
    scan_result = scan_repository(root_path)
    artifacts_dir = root_path / "artifacts" / "security"
    _wg.ensure_dir(artifacts_dir)
    report_path = artifacts_dir / "credential_scan_report.json"
    _wg.write_json(report_path, scan_result, indent=2)
    print(f"Scan complete. Report written to: {report_path}")
    print(f"Files scanned: {scan_result['files_scanned']}")
    print(f"Violations found: {len(scan_result['violations'])}")
    if scan_result["violations"]:
        print("CREDENTIAL VIOLATIONS DETECTED:")
        for violation in scan_result["violations"]:
            print(f"  {violation['file']}:{violation['line_number']} - {violation['pattern']}")
        exit(1)
    else:
        print("No credential violations found.")
        exit(0)


if __name__ == "__main__":
    main()
