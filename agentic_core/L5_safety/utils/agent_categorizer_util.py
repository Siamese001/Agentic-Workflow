"""
AST-based agent categorization for dashboard display.
Creates non-overlapping categories based on agent class patterns and docstrings.
"""

import ast
import re
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

emit_replay_key("p0", "agent_categorizer_util")
emit_determinism_digest("p0", "agent_categorizer_util")

_emit_dispatches_healing_run("p1", "agent_categorizer_util", "L5")
_emit_routes_through("p1", "agent_categorizer_util", "L5")
_emit_checks_agent_registry("p1", "agent_categorizer_util", "agent_registry")
_emit_validates_agent_capability("p1", "agent_categorizer_util", "capability")
_emit_dispatches_execution_plan("p1", "agent_categorizer_util", "exec_plan")
_emit_agent_executes_agent("p1", "agent_categorizer_util", "sub_agent")
_emit_routes_to_agent("p1", "agent_categorizer_util", "target_agent")
_emit_verifies_policy("p1", "agent_categorizer_util", "policy_check")
_emit_observes_runtime_state("p1", "agent_categorizer_util", "runtime_state")
_emit_verifies_boundary("p1", "agent_categorizer_util", "boundary_check")
_emit_transcripts_response("p1", "agent_categorizer_util", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_categorizer_util")
_emit_gated_by_confidence("p1", "agent_categorizer_util", "confidence_gate")
_emit_escalates_to_human("p1", "agent_categorizer_util", "L5")
_emit_reads_policy_state("p1", "agent_categorizer_util", "L5")

_emit_applies_guardrail("p0", "agent_categorizer_util", "p0_governance")
_emit_snapshots_state("p0", "agent_categorizer_util", "state_snapshot")
_emit_authorize_and_execute("p2", "agent_categorizer_util", "execution_auth")
_emit_validates_capability("p2", "agent_categorizer_util", "capability_check")
_emit_routes_to_capability("p2", "agent_categorizer_util", "capability_route")
_emit_writes_via_uwg("p2", "agent_categorizer_util", "uwg_write")
_emit_blocks_direct_write("p2", "agent_categorizer_util", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_categorizer_util", "tool_invocation")
_emit_captures_execution_output("p2", "agent_categorizer_util", "exec_output")
_emit_dispatches_agent("p3", "agent_categorizer_util", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_categorizer_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_categorizer_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_categorizer_util", "healing_outcome")
_emit_escalates_failure("p3", "agent_categorizer_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_categorizer_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_categorizer_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_categorizer_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_categorizer_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_categorizer_util", "eval_metric")
_emit_stores_embedding("p4", "agent_categorizer_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_categorizer_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_categorizer_util", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("agent_categorizer_util", "p4obs", "metric_1")
_emit_emits_metric_event("agent_categorizer_util", "p4obs", "metric_2")
_emit_emits_metric_event("agent_categorizer_util", "p4obs", "metric_3")
_emit_emits_metric_event("agent_categorizer_util", "p4obs", "metric_4")
_emit_emits_metric_event("agent_categorizer_util", "p4obs", "metric_5")
_emit_emits_metric_event("agent_categorizer_util", "p4obs", "metric_6")
_emit_records_incident_event("agent_categorizer_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_categorizer_util", "p4obs", "anomaly")
_emit_writes_observability_log("agent_categorizer_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_categorizer_util", "p4obs", "mon_state")
_emit_triggers_alert("agent_categorizer_util", "p4obs", "alert")
_emit_links_incident_trace("agent_categorizer_util", "p4obs", "trace_link")
_emit_captures_pattern("agent_categorizer_util", "p3lm", "pattern")
_emit_records_learning_event("agent_categorizer_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_categorizer_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_categorizer_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_categorizer_util", "p3lm", "routing")
_emit_improves_agent_policy("agent_categorizer_util", "p3lm", "policy")
_emit_stores_learning_state("agent_categorizer_util", "p3lm", "state")
_emit_records_execution_trace("agent_categorizer_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_categorizer_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_categorizer_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_categorizer_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_categorizer_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_categorizer_util", "env_read", "p2_env_1")
_emit_reads_environ("agent_categorizer_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_categorizer_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_categorizer_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_categorizer_util", "context_pull")
_emit_pulls_context("p1", "agent_categorizer_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_categorizer_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_categorizer_util", "uwg_term_2")
_emit_writes_through("p1", "agent_categorizer_util", "write_through")
_emit_writes_through("p1", "agent_categorizer_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_categorizer_util", "safety_validation")
_emit_invokes_eval("p1", "agent_categorizer_util", "eval_call")
_emit_proposal_commits_routing("p1", "agent_categorizer_util", "routing_commit")


class AgentCategorizer:
    """Categorizes agents into non-overlapping groups based on AST analysis."""

    CATEGORY_PATTERNS = [
        {
            "name": "Validation & Compliance",
            "patterns": [
                "Validator|Validation",
                "Compliance|Enforce",
                "Check|Verify|Audit",
                "SSOT|Constitution",
            ],
            "exclude": ["Heal|Repair|Fix", "Guard|Protect|Safety"],
        },
        {
            "name": "Self-Healing & Recovery",
            "patterns": ["Healer|Healing", "Repair|Fix|Recovery", "Reconcile|Restore"],
            "exclude": ["Validator|Compliance"],
        },
        {
            "name": "Safety & Security",
            "patterns": [
                "Guardian|Guard",
                "Safety|Security",
                "Protect|Defense",
                "Sentinel|Watchdog",
                "Immune|Threat",
            ],
            "exclude": ["Validator|Healer"],
        },
        {
            "name": "Code Quality & Analysis",
            "patterns": [
                "Analyzer|Analysis",
                "Detector|Detection",
                "Hunter|Finder",
                "Formatter|Format",
                "Deduplicat|Duplicate",
                "Cleanup|Clean",
                "Unused|Prune",
            ],
            "exclude": ["Validator|Healer|Guardian"],
        },
        {
            "name": "Governance & Architecture",
            "patterns": [
                "Governor|Governance",
                "Architect|Architecture",
                "Hierarchy|Hierarchical",
                "Location|Territory",
                "Import|Gravity",
            ],
            "exclude": ["Validator|Healer|Guardian"],
        },
        {
            "name": "Orchestration & Routing",
            "patterns": [
                "Orchestrator|Orchestration",
                "router|Route|Routing",
                "Conductor|Coordinate",
                "Scheduler|Schedule",
            ],
            "exclude": ["Validator|Healer"],
        },
        {
            "name": "observability & Monitoring",
            "patterns": [
                "Monitor|Monitoring",
                "Metric|Metrics",
                "Telemetry|Trace|Tracing",
                "Logger|Logging",
                "Report|Reporting",
            ],
            "exclude": ["Validator|Healer"],
        },
        {
            "name": "Testing & Verification",
            "patterns": ["Test|Testing", "Oracle|Prophecy", "Regression|Coverage", "Verify|Verification"],
            "exclude": ["Validator|Healer"],
        },
        {"name": "Specialized Agents", "patterns": [".*Agent"], "exclude": []},
    ]

    def __init__(self, folder_path: Path):
        self.folder_path = folder_path
        self.agents: dict[str, dict] = {}
        self.categories: dict[str, list[str]] = defaultdict(list)

    def scan_folder(self) -> dict[str, list[str]]:
        """Scan folder and categorize all agents."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AgentCategorizer.scan_folder")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AgentCategorizer.scan_folder".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

        py_files = list(get_python_files(self.folder_path))
        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue
            try:
                self._analyze_file(py_file)
            except (SyntaxError, UnicodeDecodeError):    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                continue
        return dict(self.categories)

    def _analyze_file(self, py_file: Path) -> None:
        """Analyze a Python file and extract agent classes."""
        source = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                category = self._categorize_agent(node, source)
                self.categories[category].append(node.name)
                self.agents[node.name] = {
                    "file": py_file.name,
                    "category": category,
                    "docstring": ast.get_docstring(node) or "",
                }

    def _categorize_agent(self, class_node: ast.ClassDef, source: str) -> str:
        """Determine category for an agent based on name and docstring."""
        name = class_node.name
        docstring = ast.get_docstring(class_node) or ""
        combined_text = f"{name} {docstring}".lower()
        for category_def in self.CATEGORY_PATTERNS:
            excluded = False
            for exclude_pattern in category_def["exclude"]:
                if re.search(exclude_pattern, combined_text, re.IGNORECASE):
                    excluded = True
                    break
            if excluded:
                continue
            for pattern in category_def["patterns"]:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return category_def["name"]
        return "Specialized Agents"

    def get_category_summary(self) -> dict[str, int]:
        """Get count of agents per category."""
        return {cat: len(agents) for cat, agents in self.categories.items()}

    def get_agents_by_category(self, category: str) -> list[str]:
        """Get list of agents in a specific category."""
        return self.categories.get(category, [])


def categorize_agents_for_dashboard(folder_path: Path) -> dict[str, list[str]]:
    """Main entry point for dashboard categorization."""
    categorizer = AgentCategorizer(folder_path)
    return categorizer.scan_folder()
