"""
AST-based agent categorization for dashboard display.
Creates non-overlapping categories based on agent class patterns and docstrings.
"""

import ast
import re
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "agent_categorizer_util")
emit_determinism_digest("p0", "agent_categorizer_util")

_emit_dispatches_healing_run("p1", "agent_categorizer_util", "L5")
_emit_routes_through("p1", "agent_categorizer_util", "L5")
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

        from agentic_core.utils.ssot_discovery_validator import get_python_files

        py_files = list(get_python_files(self.folder_path))
        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue
            try:
                self._analyze_file(py_file)
            except (SyntaxError, UnicodeDecodeError):
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
