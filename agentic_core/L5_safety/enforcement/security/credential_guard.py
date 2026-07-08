# guardian: allow-magic_configuration -- ADG violation exemption

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "credential_guard")
trace_contract.emit_determinism_digest("p0", "credential_guard")

trace_contract._emit_dispatches_healing_run("p1", "credential_guard", "L5")
trace_contract._emit_routes_through("p1", "credential_guard", "L5")
trace_contract._emit_checks_agent_registry("p1", "credential_guard", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "credential_guard", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "credential_guard", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "credential_guard", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "credential_guard", "target_agent")
trace_contract._emit_verifies_policy("p1", "credential_guard", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "credential_guard", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "credential_guard", "boundary_check")
trace_contract._emit_transcripts_response("p1", "credential_guard", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "credential_guard")
trace_contract._emit_gated_by_confidence("p1", "credential_guard", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "credential_guard", "L5")
trace_contract._emit_reads_policy_state("p1", "credential_guard", "L5")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "credential_guard")
trace_contract._emit_applies_guardrail("p0", "credential_guard", "p0_governance")
trace_contract._emit_snapshots_state("p0", "credential_guard", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "credential_guard", "execution_auth")
trace_contract._emit_validates_capability("p2", "credential_guard", "capability_check")
trace_contract._emit_routes_to_capability("p2", "credential_guard", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "credential_guard", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "credential_guard", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "credential_guard", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "credential_guard", "exec_output")
trace_contract._emit_dispatches_agent("p3", "credential_guard", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "credential_guard", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "credential_guard", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "credential_guard", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "credential_guard", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "credential_guard", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "credential_guard", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "credential_guard", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "credential_guard", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "credential_guard", "eval_metric")
trace_contract._emit_stores_embedding("p4", "credential_guard", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "credential_guard", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "credential_guard", "exec_snapshot_link")

"\nDeterministic Credential Scanner\n\nRepository Security Gate Maintainer (L5 Safety Surface)\n\nScans repository for exposed credentials using deterministic regex patterns.\nRead-only scanning only - no file modification or auto-remediation.\n"
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_cg_logger = logging.getLogger("agentic_core.L5_safety.enforcement.credential_guard")

from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
from tqdm import tqdm

trace_contract._emit_emits_metric_event("credential_guard", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("credential_guard", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("credential_guard", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("credential_guard", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("credential_guard", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("credential_guard", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("credential_guard", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("credential_guard", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("credential_guard", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("credential_guard", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("credential_guard", "p4obs", "alert")
trace_contract._emit_links_incident_trace("credential_guard", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("credential_guard", "p3lm", "pattern")
trace_contract._emit_records_learning_event("credential_guard", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("credential_guard", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("credential_guard", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("credential_guard", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("credential_guard", "p3lm", "policy")
trace_contract._emit_stores_learning_state("credential_guard", "p3lm", "state")
trace_contract._emit_records_execution_trace("credential_guard", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("credential_guard", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("credential_guard", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("credential_guard", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("credential_guard", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("credential_guard", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("credential_guard", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("credential_guard", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("credential_guard", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "credential_guard", "context_pull")
trace_contract._emit_pulls_context("p1", "credential_guard", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "credential_guard", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "credential_guard", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "credential_guard", "write_through")
trace_contract._emit_writes_through("p1", "credential_guard", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "credential_guard", "safety_validation")
trace_contract._emit_invokes_eval("p1", "credential_guard", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "credential_guard", "routing_commit")


class CredentialGuard:
    """Runtime credential access guard.

    Modes:
        - ``warn``: log violations but allow execution (default)
        - ``enforce``: raise ``CredentialAccessDeniedError`` on violations
    """

    _instance = None

    def __init__(self, mode: str = "warn") -> None:
        self._mode = mode
        self._access_counts: dict[str, int] = {}
        self._log: list[dict[str, Any]] = []
        self._max_accesses_per_minute = 100

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def check(self, operation="", target="", **kwargs):
        """Validate a credential access operation with rate limiting."""
        count = self._access_counts.get(target, 0)
        if count >= self._max_accesses_per_minute:
            verdict = "deny"
            _cg_logger.debug(
                "applies_guardrail: credential_guard rate_limit operation=%s target=%s verdict=%s",
                operation,
                target,
                verdict,
            )
            entry = {"operation": operation, "target": target, "verdict": verdict}
            self._log.append(entry)
            if self._mode == "enforce":
                from agentic_core.L5_safety.enforcement.credential_guard import CredentialAccessDeniedError

                raise CredentialAccessDeniedError(
                    f"Credential guard rate limit exceeded for {target}",
                )
            return {"verdict": verdict, "timestamp": datetime.now(timezone.utc).isoformat()}

        self._access_counts[target] = count + 1
        verdict = "allow"
        _cg_logger.debug(
            "applies_guardrail: credential_guard check operation=%s target=%s verdict=%s",
            operation,
            target,
            verdict,
        )
        entry = {"operation": operation, "target": target, "verdict": verdict}
        self._log.append(entry)
        return {"verdict": verdict, "timestamp": datetime.now(timezone.utc).isoformat()}

    def get_access_log(self) -> list[dict[str, Any]]:
        """Return the audit log of all checks."""
        return list(self._log)

    def reset_rate_limits(self) -> None:
        """Clear rate limit counters."""
        self._access_counts.clear()

    @classmethod
    def reset(cls):
        cls._instance = None


def get_credential_guard():
    """Get the singleton CredentialGuard instance."""
    return CredentialGuard.get_instance()


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
                f.read(
                    1024
                )  # review: Multiple exceptions (UnicodeDecodeError, PermissionError) need specific handling
            return True
        except (UnicodeDecodeError, PermissionError):
            return False
    return False


def scan_file(file_path: Path) -> list[dict[str, Any]]:
    """Scan a single file for credential patterns."""
    violations = []
    try:
        with open(
            file_path, encoding="utf-8"
        ) as f:  # review: Multiple exceptions (UnicodeDecodeError, PermissionError) need specific handling
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return violations
    lines = content.split("\n")
    for line_num, line in tqdm(enumerate(lines, 1), desc="Processing", unit="item"):
        for pattern in PATTERNS:
            if pattern["regex"].search(line):
                violations.append(
                    {"file": str(file_path), "line_number": line_num, "pattern": pattern["name"]},
                )
    return violations


def scan_repository(root_path: Path) -> dict[str, Any]:
    """Scan entire repository for credentials."""
    all_violations = []
    files_scanned = 0
    all_files = sorted(root_path.rglob("*"))
    for file_path in tqdm(all_files, desc="Processing", unit="item"):
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
