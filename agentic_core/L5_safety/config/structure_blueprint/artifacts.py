"""
Artifacts Module - COLD PATH (File Patterns and Prefixes)

This module contains app-specific patterns, forbidden patterns, and
file artifact routing rules. Regex patterns are stored as strings
and compiled lazily.

Loaded lazily on first access.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from re import Pattern
from typing import Any, Final

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "artifacts")
emit_determinism_digest("p0", "artifacts")

_emit_dispatches_healing_run("p1", "artifacts", "L5")
_emit_routes_through("p1", "artifacts", "L5")
_emit_checks_agent_registry("p1", "artifacts", "agent_registry")
_emit_validates_agent_capability("p1", "artifacts", "capability")
_emit_dispatches_execution_plan("p1", "artifacts", "exec_plan")
_emit_agent_executes_agent("p1", "artifacts", "sub_agent")
_emit_routes_to_agent("p1", "artifacts", "target_agent")
_emit_verifies_policy("p1", "artifacts", "policy_check")
_emit_observes_runtime_state("p1", "artifacts", "runtime_state")
_emit_verifies_boundary("p1", "artifacts", "boundary_check")
_emit_transcripts_response("p1", "artifacts", "transcript")
_emit_hard_fails_untranscripted("p1", "artifacts")
_emit_gated_by_confidence("p1", "artifacts", "confidence_gate")
_emit_escalates_to_human("p1", "artifacts", "L5")
_emit_reads_policy_state("p1", "artifacts", "L5")
_emit_authorize_and_execute("p2", "artifacts", "execution_auth")
_emit_validates_capability("p2", "artifacts", "capability_check")
_emit_routes_to_capability("p2", "artifacts", "capability_route")
_emit_writes_via_uwg("p2", "artifacts", "uwg_write")
_emit_blocks_direct_write("p2", "artifacts", "direct_write_block")
_emit_records_tool_invocation("p2", "artifacts", "tool_invocation")
_emit_captures_execution_output("p2", "artifacts", "exec_output")
_emit_dispatches_agent("p3", "artifacts", "agent_dispatch")
_emit_coordinates_agents("p3", "artifacts", "agent_coordination")
_emit_records_workflow_lineage("p3", "artifacts", "workflow_lineage")
_emit_records_healing_outcome("p3", "artifacts", "healing_outcome")
_emit_escalates_failure("p3", "artifacts", "failure_escalation")
_emit_orchestrates_workflow("p3", "artifacts", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "artifacts", "healing_dispatch")
_emit_invokes_evaluation("p3", "artifacts", "evaluation_signal")
_emit_records_telemetry_event("p4", "artifacts", "telemetry_event")
_emit_captures_evaluation_metric("p4", "artifacts", "eval_metric")
_emit_stores_embedding("p4", "artifacts", "embedding_store")
_emit_updates_meta_learning_state("p4", "artifacts", "meta_learning")
_emit_links_execution_to_snapshot("p4", "artifacts", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("artifacts", "p4obs", "metric_1")
_emit_emits_metric_event("artifacts", "p4obs", "metric_2")
_emit_emits_metric_event("artifacts", "p4obs", "metric_3")
_emit_emits_metric_event("artifacts", "p4obs", "metric_4")
_emit_emits_metric_event("artifacts", "p4obs", "metric_5")
_emit_emits_metric_event("artifacts", "p4obs", "metric_6")
_emit_records_incident_event("artifacts", "p4obs", "incident")
_emit_captures_runtime_anomaly("artifacts", "p4obs", "anomaly")
_emit_writes_observability_log("artifacts", "p4obs", "obs_log")
_emit_updates_monitoring_state("artifacts", "p4obs", "mon_state")
_emit_triggers_alert("artifacts", "p4obs", "alert")
_emit_links_incident_trace("artifacts", "p4obs", "trace_link")
_emit_captures_pattern("artifacts", "p3lm", "pattern")
_emit_records_learning_event("artifacts", "p3lm", "learning_event")
_emit_writes_learning_snapshot("artifacts", "p3lm", "snapshot")
_emit_feeds_meta_learning("artifacts", "p3lm", "meta_feed")
_emit_updates_routing_strategy("artifacts", "p3lm", "routing")
_emit_improves_agent_policy("artifacts", "p3lm", "policy")
_emit_stores_learning_state("artifacts", "p3lm", "state")
_emit_records_execution_trace("artifacts", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("artifacts", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("artifacts", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("artifacts", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("artifacts", "L4_STATE", "p2_trace_5")
_emit_reads_environ("artifacts", "env_read", "p2_env_1")
_emit_reads_environ("artifacts", "env_read", "p2_env_2")
_emit_reads_runtime_state("artifacts", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("artifacts", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "artifacts", "context_pull")
_emit_pulls_context("p1", "artifacts", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "artifacts", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "artifacts", "uwg_term_2")
_emit_writes_through("p1", "artifacts", "write_through")
_emit_writes_through("p1", "artifacts", "write_through_2")
_emit_validated_by_safety_plane("p1", "artifacts", "safety_validation")
_emit_invokes_eval("p1", "artifacts", "eval_call")
_emit_proposal_commits_routing("p1", "artifacts", "routing_commit")

APP_SPECIFIC_PREFIXES: Final[Mapping[str, str]] = {
    "rg_": "apps_rg",
    "lic_": "apps_lic",
    "resume_": "apps_rg",
    "outreach_": "apps_rg",
    "dispatch_resume": "apps_rg",
    "dispatch_outreach": "apps_rg",
    "contact_research": "apps_rg",
    "company_research": "apps_rg",
}
STUTTERING_PREFIX_MAP: Final[Mapping[str, str]] = {"r_g_": "rg_", "l_i_c_": "lic_"}
APP_SPECIFIC_TARGET_SUBFOLDER: str = "reasoning"
APP_SPECIFIC_PATTERN_STRINGS: Final[Sequence[str]] = [
    "^rg_.*\\.py$",
    "^lic_.*\\.py$",
    "^resume_.*\\.py$",
    "^outreach_.*\\.py$",
    "^dispatch_(resume|outreach).*\\.py$",
]
FORBIDDEN_LAYER_PREFIXES: Final[tuple[str, ...]] = (
    "l0_",
    "l1_",
    "l2_",
    "l3_",
    "l4_",
    "l5_",
    "l6_",
    "L0_",
    "L1_",
    "L2_",
    "L3_",
    "L4_",
    "L5_",
    "L6_",
    "p0_",
    "p1_",
    "p2_",
    "p3_",
    "P0_",
    "P1_",
    "P2_",
    "P3_",
)
FORBIDDEN_BACKUP_PATTERN_STRINGS: Final[Sequence[str]] = [
    ".*\\.bak\\.\\d+$",
    ".*\\.backup\\.\\d+$",
    ".*\\.old\\.\\d+$",
    ".*\\.tmp\\.\\d+$",
]
FORBIDDEN_FILENAME_PATTERNS: Final[Sequence[Mapping[str, str]]] = [
    {
        "pattern": "(?<![a-z])[a-z]_[a-z]_[a-z]_[a-z]",
        "reason": "Stuttering Acronym Violation (naive CamelCase split). Fix: collapse single-char segments (e.g., s_s_o_t → ssot).",
    },
    {
        "pattern": "(?<!^)_{2,}(?!init__|pycache__)",
        "reason": "Multiple Underscore Violation (unsanitized concatenation). Fix: collapse to single underscore (e.g., setup___init___ → setup_init).",
    },
    {
        "pattern": "^_[a-z]",
        "reason": "Leading Underscore Violation (non-__init__ file). Fix: remove leading underscore or rename to descriptive name.",
    },
]
FORBIDDEN_EPHEMERAL_PATTERNS: Final[Sequence[str]] = [
    "(?i)phase\\s*\\d",
    "(?i)wave\\s*[\\d_]",
    "(?i)sprint\\d",
]
EPHEMERAL_PATTERN_EXEMPTIONS: Final[Sequence[str]] = [
    "(?i)two_?phase",
    "(?i)execution_phase",
    "(?i)mutation_phase",
    "(?i)research_hop_phase",
]


def get_correct_app_folder(filename: str) -> str | None:
    """Return the correct root app folder for a file based on prefix."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_correct_app_folder", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_correct_app_folder", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "get_correct_app_folder")
    for prefix, folder in APP_SPECIFIC_PREFIXES.items():
        if filename.startswith(prefix):
            return folder
    return None


def get_correct_app_path(filename: str) -> str | None:
    """Return the full recommended path for app-specific files."""
    root = get_correct_app_folder(filename)
    if root:
        return f"{root}/{APP_SPECIFIC_TARGET_SUBFOLDER}"
    return None


LAYER_PREFIX_FILENAME_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {"l2_phase_spec.py", "l4_registries.py", "l1_meta_adapter.py"}
)


def has_forbidden_layer_prefix(filename: str) -> str | None:
    """Check if filename starts with a forbidden layer/priority prefix."""
    if filename in LAYER_PREFIX_FILENAME_ALLOWLIST:
        return None
    if filename.startswith(FORBIDDEN_LAYER_PREFIXES):
        for prefix in FORBIDDEN_LAYER_PREFIXES:
            if filename.startswith(prefix):
                return prefix
    return None


@lru_cache(maxsize=1)
def get_app_specific_patterns_compiled() -> list[Pattern]:
    """Compile and cache app-specific patterns."""
    return [re.compile(p) for p in APP_SPECIFIC_PATTERN_STRINGS]


@lru_cache(maxsize=1)
def get_forbidden_backup_patterns_compiled() -> list[Pattern]:
    """Compile and cache forbidden backup patterns."""
    return [re.compile(p) for p in FORBIDDEN_BACKUP_PATTERN_STRINGS]


@lru_cache(maxsize=1)
def get_forbidden_ephemeral_patterns_compiled() -> list[Pattern]:
    """Compile and cache forbidden ephemeral patterns."""
    return [re.compile(p) for p in FORBIDDEN_EPHEMERAL_PATTERNS]


@lru_cache(maxsize=1)
def get_ephemeral_exemption_patterns_compiled() -> list[Pattern]:
    """Compile and cache ephemeral exemption patterns."""
    return [re.compile(p) for p in EPHEMERAL_PATTERN_EXEMPTIONS]


def is_app_specific_file(filename: str) -> bool:
    """Check if a file should be in an app folder, not agentic_core."""
    patterns = get_app_specific_patterns_compiled()
    return any(pattern.match(filename) for pattern in patterns)


def is_broken_backup_file(filename: str) -> bool:
    """Check if filename matches broken backup pattern."""
    patterns = get_forbidden_backup_patterns_compiled()
    return any(pattern.match(filename) for pattern in patterns)


@property
def APP_SPECIFIC_PATTERNS() -> list[Pattern]:
    """Backward compatibility accessor for compiled patterns."""
    return get_app_specific_patterns_compiled()


@property
def FORBIDDEN_BACKUP_PATTERNS() -> list[Pattern]:
    """Backward compatibility accessor for compiled patterns."""
    return get_forbidden_backup_patterns_compiled()


ARTIFACT_ROUTING_MAP: Final[Mapping[str, Mapping[str, Any]]] = {
    "docs/reports/assessments": {
        "description": "Gap analyses, architectural assessments, and strategic reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {"keywords": ["assessment", "analysis", "gap", "architecture", "strategic"]},
        "naming_patterns": [re.compile(".*assessment.*"), re.compile(".*analysis.*"), re.compile(".*gap.*")],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/audit": {
        "description": "Structural audits, drift analysis, and compliance reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "headers": ["# Audit Report", "## Violations", "## Drift"],
            "json_keys": ["critical_violations", "compliance_score", "drift_metrics"],
            "keywords": ["audit", "drift", "variance", "compliance", "SSOT"],
        },
        "naming_patterns": [
            re.compile(".*audit.*"),
            re.compile(".*drift.*"),
            re.compile(".*variance.*"),
            re.compile(".*compliance.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/coverage": {
        "description": "Test coverage reports and code quality metrics.",
        "file_extensions": [".md", ".json", ".html", ".xml", ".txt"],
        "content_signals": {"keywords": ["coverage", "test", "quality", "percentage", "htmlcov"]},
        "naming_patterns": [re.compile(".*coverage.*"), re.compile(".*test.*"), re.compile(".*quality.*")],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/security": {
        "description": "Security assessments, vulnerability scans, and safety reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {"keywords": ["security", "vulnerability", "safety", "hardened", "guardrails"]},
        "naming_patterns": [
            re.compile(".*security.*"),
            re.compile(".*vulnerability.*"),
            re.compile(".*hardened.*"),
            re.compile(".*hardening.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/telemetry": {
        "description": "System telemetry, performance metrics, and observability data.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {"keywords": ["telemetry", "metrics", "performance", "observability"]},
        "naming_patterns": [
            re.compile(".*telemetry.*"),
            re.compile(".*metrics.*"),
            re.compile(".*performance.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/missions": {
        "description": "High-level mission execution traces and runtime logs (Deported from Root).",
        "file_extensions": [".jsonl", ".trace", ".log", ".json"],
        "content_signals": {
            "json_keys": ["mission_id", "trace_id", "execution_log"],
            "keywords": ["mission", "trace", "execution"],
        },
        "naming_patterns": [re.compile(".*mission.*"), re.compile(".*trace.*"), re.compile(".*execution.*")],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "agentic_core/L0_routing/utils": {
        "description": "Runtime debug logs, error dumps, and stack traces.",
        "file_extensions": [".log", ".err", ".out", ".txt"],
        "content_signals": {
            "keywords": ["DEBUG", "ERROR", "Traceback (most recent call)", "Exception", "Stack trace"]
        },
        "naming_patterns": [re.compile(".*debug.*"), re.compile(".*error.*"), re.compile(".*crash.*")],
        "forbidden_extensions": [".py", ".pyc", ".pyo"],
        "forbidden_keywords": ["def main", "if __name__", "import sys", "class "],
    },
    "agentic_core/L0_routing/scripts": {
        "description": "Python utility scripts, maintenance tools, and standalone executables.",
        "file_extensions": [".py"],
        "content_signals": {
            "keywords": [
                "def main(",
                "if __name__",
                "#!/usr/bin/env python",
                "import sys",
                "argparse",
                "click",
                "typer",
            ],
            "imports": ["os", "sys", "shutil", "pathlib", "logging"],
        },
        "naming_patterns": [
            re.compile(".*script.*"),
            re.compile(".*fixer.*"),
            re.compile(".*tool.*"),
            re.compile(".*util.*"),
            re.compile(".*cleaner.*"),
            re.compile(".*migrat.*"),
        ],
        "forbidden_keywords": [
            "class Test",
            "def test_",
            "import unittest",
            "import pytest",
            "class BaseAgent",
            "class Sovereign",
        ],
    },
    "logs": {
        "description": "High-level Mission Execution Traces (Approved for Root).",
        "file_extensions": [".jsonl", ".trace"],
        "content_signals": {"json_keys": ["mission_id", "step_count", "agent_action", "thought_process"]},
        "naming_patterns": [re.compile("^trace_.*"), re.compile("^mission_.*")],
        "forbidden_keywords": ["Traceback", "Exception", "dataset_version"],
    },
    "data/processed": {
        "description": "Structured data outputs and intermediate processing states.",
        "file_extensions": [".json", ".csv", ".parquet"],
        "content_signals": {
            "json_keys": ["dataset_version", "record_count", "processed_at", "schema_version"]
        },
        "naming_patterns": [
            re.compile(".*dataset.*"),
            re.compile(".*processed.*"),
            re.compile("agent_discovery.*\\.json$"),
            re.compile(".*manifest.*\\.json$"),
        ],
        "forbidden_keywords": ["def ", "class ", "api_key", "secret"],
    },
}


def validate_artifact_routing(
    filename: str, content: str | None = None
) -> tuple[bool, str | None, str | None]:
    """
    Validate file against ARTIFACT_ROUTING_MAP negative logic.

    Implements HARD REJECT for files that match forbidden_extensions or forbidden_keywords
    ONLY when they would otherwise match the positive signals for that destination.
    This prevents gravity leakage where code files get misclassified as reports/logs/data.

    Args:
        filename: Name of the file to validate
        content: Optional file content for keyword checking

    Returns:
        Tuple of (is_valid, matched_destination, rejection_reason)
        - is_valid: False if file matches forbidden signals (HARD REJECT)
        - matched_destination: Destination path if positive match found
        - rejection_reason: Reason for rejection if is_valid is False

    Example:
        >>> validate_artifact_routing("test_report.py", "def main():")
        (False, None, "Forbidden extension .py for destination docs/reports")

        >>> validate_artifact_routing("audit_results.md", "# Assessment Report")
        (True, "docs/reports", None)
    """
    file_ext = Path(filename).suffix.lower()
    for dest, rules in ARTIFACT_ROUTING_MAP.items():
        allowed_exts = rules.get("file_extensions", [])
        matches_positive = False
        if allowed_exts and file_ext in allowed_exts:
            matches_positive = True
        naming_patterns = rules.get("naming_patterns", [])
        if naming_patterns:
            for pattern in naming_patterns:
                if pattern.match(filename):
                    matches_positive = True
                    break
        if content and matches_positive:
            content_signals = rules.get("content_signals", {})
            headers = content_signals.get("headers", [])
            if headers and any(header in content for header in headers):
                matches_positive = True
            keywords = content_signals.get("keywords", [])
            if keywords and any(keyword in content for keyword in keywords):
                matches_positive = True
        if matches_positive:
            forbidden_exts = rules.get("forbidden_extensions", [])
            if forbidden_exts and file_ext in forbidden_exts:
                return (False, None, f"Forbidden extension {file_ext} for destination {dest}")
            if content:
                forbidden_keywords = rules.get("forbidden_keywords", [])
                if forbidden_keywords:
                    for keyword in forbidden_keywords:
                        if keyword in content:
                            return (False, None, f"Forbidden keyword '{keyword}' for destination {dest}")
            return (True, dest, None)
    return (True, None, None)


def check_forbidden_signals(filename: str, content: str | None = None) -> str | None:
    """
    Quick check for forbidden signals across all routing rules.

    Returns rejection reason if file matches any forbidden_extensions or forbidden_keywords,
    None otherwise.

    This is a fast-path check for agents that only need to know if a file is forbidden,
    without needing the full routing destination.

    Args:
        filename: Name of the file to check
        content: Optional file content for keyword checking

    Returns:
        Rejection reason string if forbidden, None if allowed
    """
    is_valid, _, rejection_reason = validate_artifact_routing(filename, content)
    return rejection_reason if not is_valid else None


PROJECT_ROOT_SUBFOLDERS: Final[Mapping[str, Sequence[str]]] = {
    "logs": [],
    "ops_scripts": ["ci", "maintenance", "security", "setup"],
    "data": ["raw", "processed", "datasets", "configurations", "governance", "cache", "archives", "logs"],
    "docs": ["technical", "project", "analysis", "guides", "archive"],
    "tests": [],
    "archives": [],
}
PROJECT_ROOT_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "logs": {
        "purpose": "Mission execution logs and trace files",
        "content_types": ["mission_logs", "trace_files", "execution_logs"],
        "execution_allowed": False,
        "notes": "Contains trace.jsonl files for various mission executions",
        "file_patterns": ["*.log", "*.jsonl", "*.trace"],
        "keywords": ["transcript", "log", "trace", "execution"],
    },
    "scripts": {
        "purpose": "Project-level utility scripts (standalone, no core dependencies)",
        "content_types": ["setup_scripts", "deployment_tools", "ci_scripts", "migration_tools"],
        "execution_allowed": True,
        "notes": "Standalone utilities only - NO agentic_core imports allowed",
        "file_patterns": ["*.py", "*.sh", "*.bat", "*.cmd"],
        "keywords": ["setup", "install", "ci", "build", "deploy", "migration", "run"],
    },
    "data": {
        "purpose": "Data files and datasets used by the project",
        "content_types": ["raw_data", "processed_data", "datasets", "configurations", "governance_data"],
        "execution_allowed": False,
        "notes": "Organized by data lifecycle: raw → processed → datasets → configurations",
        "file_patterns": ["*.csv", "*.json", "*.yaml", "*.yml", "*.xml", "*.parquet", "*.db", "*.sqlite"],
        "keywords": ["data", "dataset", "config", "settings", "parameters"],
    },
    "docs": {
        "purpose": "Project documentation and reports organized by purpose",
        "content_types": ["technical_docs", "project_docs", "analysis_reports", "user_guides"],
        "execution_allowed": False,
        "notes": "Categorized documentation: technical, project, analysis, and guides",
        "file_patterns": ["*.md", "*.rst", "*.txt", "*.pdf", "*.docx", "*.html"],
        "keywords": ["doc", "guide", "manual", "readme", "tutorial", "specification"],
    },
    "reports": {
        "purpose": "Generated reports, analysis outputs, and implementation plans",
        "content_types": ["coverage_reports", "telemetry_data", "audit_reports", "implementation_plans"],
        "execution_allowed": False,
        "notes": "SSOT location for all implementation plans and generated reports",
        "file_patterns": ["*.html", "*.json", "*.md", "*.xml", "*.csv"],
        "keywords": ["report", "coverage", "telemetry", "audit", "plan", "implementation"],
    },
    "tests": {
        "purpose": "Test files and test data",
        "content_types": ["test_files", "test_data", "fixtures"],
        "execution_allowed": True,
        "notes": "Test files separate from execution scripts",
        "file_patterns": ["test_*.py", "*_test.py", "conftest.py", "*.fixture"],
        "keywords": ["test", "spec", "fixture", "mock"],
        "naming_convention": "snake_case_test",
    },
    "enforcement": {
        "purpose": "L5 safety enforcement agents and components (guardrails, gravity, gates)",
        "content_types": ["safety_agent", "membrane", "sanitizer", "hygiene_agent", "guardrail", "gate"],
        "execution_allowed": True,
        "notes": "Sovereign operational safety components - snake_case_agent naming mandatory",
        "file_patterns": ["*_agent.py"],
        "keywords": ["guardrail", "membrane", "sanitizer", "hygiene", "redact", "scrub", "pii", "threat"],
        "naming_convention": "snake_case_agent",
    },
    "archives": {
        "purpose": "Archived files and historical data",
        "content_types": ["archived_code", "historical_data", "backups"],
        "execution_allowed": False,
        "notes": "Legacy files and historical archives",
        "file_patterns": ["*.bak", "*.old", "*.backup", "*.archive", "*.zip", "*.tar.gz"],
        "keywords": ["archive", "backup", "old", "legacy", "retired"],
    },
}
DATA_SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "raw": {
        "purpose": "Raw input data and external sources",
        "content_types": ["external_references", "input_files", "source_data"],
        "execution_allowed": False,
        "notes": "Contains external/ reference materials and raw inputs",
    },
    "processed": {
        "purpose": "Processed and transformed data artifacts",
        "content_types": ["audit_results", "evaluations", "manifests", "outputs"],
        "execution_allowed": False,
        "notes": "Data that has been processed or transformed",
    },
    "datasets": {
        "purpose": "Structured datasets for testing and reference",
        "content_types": ["golden_datasets", "test_data", "reference_data"],
        "execution_allowed": False,
        "notes": "Curated datasets for testing and validation",
    },
    "configurations": {
        "purpose": "Configuration files and settings",
        "content_types": ["sdk_configs", "mcp_configs", "prompt_configs", "task_definitions"],
        "execution_allowed": False,
        "notes": "Configuration files for various components",
    },
    "governance": {
        "purpose": "Governance and security-related data",
        "content_types": ["prompt_governance", "injection_data", "safety_data", "registry_data"],
        "execution_allowed": False,
        "notes": "Security, governance, and compliance data",
    },
    "cache": {
        "purpose": "Temporary cache files",
        "content_types": ["temp_files", "cache_data"],
        "execution_allowed": False,
        "notes": "Temporary storage that can be cleared",
    },
    "archives": {
        "purpose": "Archived historical data",
        "content_types": ["historical_data", "backups", "legacy_files"],
        "execution_allowed": False,
        "notes": "Long-term storage of historical data",
    },
    "logs": {
        "purpose": "Data processing logs and traces",
        "content_types": ["processing_logs", "error_logs", "trace_files"],
        "execution_allowed": False,
        "notes": "Logs from data processing operations",
    },
}
DOCS_SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "technical": {
        "purpose": "Technical documentation and specifications",
        "content_types": ["architecture_docs", "integration_guides", "api_docs", "configuration_guides"],
        "execution_allowed": False,
        "notes": "Technical documentation for developers and architects",
    },
    "project": {
        "purpose": "Project management and governance documentation",
        "content_types": ["phase_docs", "planning_docs", "governance_docs", "milestone_tracking"],
        "execution_allowed": False,
        "notes": "Project management and planning documentation",
    },
    "analysis": {
        "purpose": "Analysis reports and research documentation",
        "content_types": ["analysis_reports", "metrics_docs", "investigation_reports", "rca_docs"],
        "execution_allowed": False,
        "notes": "Analysis, research, and investigation reports",
    },
    "guides": {
        "purpose": "User and developer guides",
        "content_types": ["user_guides", "developer_guides", "deployment_guides", "tutorials"],
        "execution_allowed": False,
        "notes": "Instructional documentation for users and developers",
    },
    "archive": {
        "purpose": "Archived and outdated documentation",
        "content_types": ["legacy_docs", "outdated_specs", "historical_docs"],
        "execution_allowed": False,
        "notes": "Documentation kept for historical reference",
    },
}
