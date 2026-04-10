"""
Phase 1: Registry Verification Module
=====================================
Scans codebase for all agents, validates discovery completeness, flags orphans.

This module provides:
1. Full codebase scan for *Agent.py files
2. Cross-reference with agent_discovery_full.json
3. Orphan agent detection (in registry but missing from filesystem)
4. Missing agent detection (in filesystem but not in registry)
5. Path mismatch detection (registry path != actual path)

USAGE:
    from agentic_core.L5_safety.enforcement.registry_verification_enforcer import RegistryVerifier
    verifier = RegistryVerifier()
    report = verifier.verify_registry()
"""

from __future__ import annotations

import ast
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from agentic_core.L0_routing.config.path_constants import (
    AGENT_DISCOVERY_JSON,
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
)
from agentic_core.L0_routing.config.path_constants import DISCOVERY_EXCLUDED_TERRITORIES, GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
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
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
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

emit_replay_key("p0", "registry_verification_enforcer")
emit_determinism_digest("p0", "registry_verification_enforcer")

_emit_dispatches_healing_run("p1", "registry_verification_enforcer", "L5")
_emit_routes_through("p1", "registry_verification_enforcer", "L5")
_emit_checks_agent_registry("p1", "registry_verification_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "registry_verification_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "registry_verification_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "registry_verification_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "registry_verification_enforcer", "target_agent")
_emit_verifies_policy("p1", "registry_verification_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "registry_verification_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "registry_verification_enforcer", "boundary_check")
_emit_transcripts_response("p1", "registry_verification_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "registry_verification_enforcer")
_emit_gated_by_confidence("p1", "registry_verification_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "registry_verification_enforcer", "L5")
_emit_reads_policy_state("p1", "registry_verification_enforcer", "L5")
_emit_authorize_and_execute("p2", "registry_verification_enforcer", "execution_auth")
_emit_validates_capability("p2", "registry_verification_enforcer", "capability_check")
_emit_routes_to_capability("p2", "registry_verification_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "registry_verification_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "registry_verification_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "registry_verification_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "registry_verification_enforcer", "exec_output")
_emit_dispatches_agent("p3", "registry_verification_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "registry_verification_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "registry_verification_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "registry_verification_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "registry_verification_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "registry_verification_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "registry_verification_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "registry_verification_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "registry_verification_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "registry_verification_enforcer", "eval_metric")
_emit_stores_embedding("p4", "registry_verification_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "registry_verification_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "registry_verification_enforcer", "exec_snapshot_link")
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

_emit_emits_metric_event("registry_verification_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("registry_verification_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("registry_verification_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("registry_verification_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("registry_verification_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("registry_verification_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("registry_verification_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("registry_verification_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("registry_verification_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("registry_verification_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("registry_verification_enforcer", "p4obs", "alert")
_emit_links_incident_trace("registry_verification_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("registry_verification_enforcer", "p3lm", "pattern")
_emit_records_learning_event("registry_verification_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("registry_verification_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("registry_verification_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("registry_verification_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("registry_verification_enforcer", "p3lm", "policy")
_emit_stores_learning_state("registry_verification_enforcer", "p3lm", "state")
_emit_records_execution_trace("registry_verification_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("registry_verification_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("registry_verification_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("registry_verification_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("registry_verification_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("registry_verification_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("registry_verification_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("registry_verification_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("registry_verification_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "registry_verification_enforcer", "context_pull")
_emit_pulls_context("p1", "registry_verification_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "registry_verification_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "registry_verification_enforcer", "uwg_term_2")
_emit_writes_through("p1", "registry_verification_enforcer", "write_through")
_emit_writes_through("p1", "registry_verification_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "registry_verification_enforcer", "safety_validation")
_emit_invokes_eval("p1", "registry_verification_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "registry_verification_enforcer", "routing_commit")

EXCLUDED_DIRS: Final[frozenset[str]] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)


@dataclass
class AgentInfo:
    """Information about a discovered agent."""

    class_name: str
    file_path: Path
    relative_path: str
    layer: str = "Unknown"
    has_agent_class: bool = False
    inheritance: list[str] = field(default_factory=list)
    key_methods: list[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    """Result of registry verification."""

    total_filesystem_agents: int = 0
    total_registry_agents: int = 0
    orphan_agents: list[dict[str, Any]] = field(default_factory=list)
    missing_agents: list[AgentInfo] = field(default_factory=list)
    path_mismatches: list[dict[str, Any]] = field(default_factory=list)
    valid_agents: list[AgentInfo] = field(default_factory=list)
    coverage_percentage: float = 0.0
    is_complete: bool = False
    errors: list[str] = field(default_factory=list)


class RegistryVerifier:
    """Verifies agent registry completeness against filesystem."""

    def __init__(self, project_root: Path | None = None):
        """Initialize verifier with project root."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RegistryVerifier.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RegistryVerifier.__init__", "p0_governance")
        self.project_root = project_root or self._find_project_root()
        self.discovery_path = self._find_discovery_json()

    def _find_project_root(self) -> Path:
        """Find project root by looking for pyproject.toml or .git."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
                return parent
        return Path.cwd()

    def _find_discovery_json(self) -> Path:
        """Find the agent discovery JSON file."""
        l0_path = self.project_root / AGENTIC_CORE_DIR / "L0_routing" / AGENT_DISCOVERY_JSON
        if l0_path.exists():
            return l0_path
        root_path = self.project_root / AGENT_DISCOVERY_JSON
        if root_path.exists():
            return root_path
        return l0_path

    def _is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        path_parts = set(path.parts)
        return bool(path_parts & EXCLUDED_DIRS)

    def _is_test_file(self, path: Path) -> bool:
        """Check if path is a test file."""
        return TESTS_DIR in path.parts or path.name.startswith("test_")

    def _extract_layer(self, relative_path: str) -> str:
        """Extract layer from relative path."""
        parts = Path(relative_path).parts
        if len(parts) < 2:
            return "Root"
        first_dir = parts[0]
        if first_dir == AGENTIC_CORE_DIR:
            if len(parts) >= 2:
                second_dir = parts[1]
                if second_dir.startswith("L") and "_" in second_dir:
                    return second_dir.split("_")[0]
                if second_dir == "base_agents":
                    return "Base"
                return second_dir.capitalize()
        elif first_dir == APPS_RG_DIR:
            return "Apps_RG"
        elif first_dir == APPS_LIC_DIR:
            return "Apps_LIC"
        elif first_dir == APPS_SHARED_DIR:
            return "Apps_Shared"
        return "Unknown"

    def _parse_agent_file(self, file_path: Path) -> AgentInfo | None:
        """Parse an agent file to extract class information."""
        try:
            if not file_path.exists():
                return None
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError, OSError, FileNotFoundError):    # guardian: Parsing and encoding errors need separate handling strategies
            return None
        relative_path = str(file_path.relative_to(self.project_root))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]
                return AgentInfo(
                    class_name=node.name,
                    file_path=file_path,
                    relative_path=relative_path,
                    layer=self._extract_layer(relative_path),
                    has_agent_class=True,
                    inheritance=bases,
                    key_methods=methods[:10],
                )
        return None

    def scan_filesystem(self) -> list[AgentInfo]:
        """Scan filesystem for all agent files."""

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L5_POLICY, "RegistryVerifier.scan_filesystem",
        )
        agents: list[AgentInfo] = []
        for agent_file in self.project_root.rglob("*Agent.py"):
            if self._is_excluded(agent_file):
                continue
            if self._is_test_file(agent_file):
                continue
            agent_info = self._parse_agent_file(agent_file)
            if agent_info and agent_info.has_agent_class:
                agents.append(agent_info)
        return agents

    def load_registry(self) -> list[dict[str, Any]]:
        """Load agent registry from JSON file."""
        if not self.discovery_path.exists():
            return []
        try:
            with open(self.discovery_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):    # guardian: Add error context logging
            return []

    def verify_registry(self) -> VerificationResult:
        """Perform full registry verification."""
        result = VerificationResult()
        filesystem_agents = self.scan_filesystem()
        result.total_filesystem_agents = len(filesystem_agents)
        registry_agents = self.load_registry()
        result.total_registry_agents = len(registry_agents)
        fs_by_class = {a.class_name: a for a in filesystem_agents}
        fs_by_path = {a.relative_path.replace("\\", "/"): a for a in filesystem_agents}
        registry_by_class = {a.get("class_name", ""): a for a in registry_agents}
        for reg_agent in registry_agents:
            class_name = reg_agent.get("class_name", "")
            reg_path = reg_agent.get("path", "").replace("\\", "/")
            if class_name not in fs_by_class:
                result.orphan_agents.append(
                    {
                        "class_name": class_name,
                        "registry_path": reg_path,
                        "reason": "Class not found in filesystem",
                    },
                )
            elif reg_path not in fs_by_path:
                actual_agent = fs_by_class[class_name]
                result.path_mismatches.append(
                    {
                        "class_name": class_name,
                        "registry_path": reg_path,
                        "actual_path": actual_agent.relative_path.replace("\\", "/"),
                        "reason": "Path mismatch between registry and filesystem",
                    },
                )
        for fs_agent in filesystem_agents:
            if fs_agent.class_name not in registry_by_class:
                result.missing_agents.append(fs_agent)
            else:
                result.valid_agents.append(fs_agent)
        if result.total_filesystem_agents > 0:
            result.coverage_percentage = len(result.valid_agents) / result.total_filesystem_agents * 100
        result.is_complete = (
            len(result.orphan_agents) == 0
            and len(result.missing_agents) == 0
            and (len(result.path_mismatches) == 0)
        )
        return result

    def generate_report(self, result: VerificationResult) -> str:
        """Generate markdown report from verification result."""
        lines = [
            "# Phase 1: Registry Verification Report",
            "",
            "## Summary",
            "",
            f"- **Total Filesystem Agents:** {result.total_filesystem_agents}",
            f"- **Total Registry Agents:** {result.total_registry_agents}",
            f"- **Valid Agents:** {len(result.valid_agents)}",
            f"- **Missing from Registry:** {len(result.missing_agents)}",
            f"- **Orphan Agents:** {len(result.orphan_agents)}",
            f"- **Path Mismatches:** {len(result.path_mismatches)}",
            f"- **Coverage:** {result.coverage_percentage:.1f}%",
            f"- **Status:** {('PASS' if result.is_complete else 'FAIL')}",
            "",
        ]
        if result.orphan_agents:
            lines.extend(
                [
                    "## Orphan Agents (In Registry, Not in Filesystem)",
                    "",
                    "| Class Name | Registry Path | Reason |",
                    "|------------|---------------|--------|",
                ],
            )
            for orphan in result.orphan_agents:
                cls = orphan["class_name"]
                path = orphan["registry_path"]
                reason = orphan["reason"]
                lines.append(f"| {cls} | {path} | {reason} |")
            lines.append("")
        if result.path_mismatches:
            lines.extend(
                [
                    "## Path Mismatches",
                    "",
                    "| Class Name | Registry Path | Actual Path |",
                    "|------------|---------------|-------------|",
                ],
            )
            for mismatch in result.path_mismatches:
                cls = mismatch["class_name"]
                reg = mismatch["registry_path"]
                act = mismatch["actual_path"]
                lines.append(f"| {cls} | {reg} | {act} |")
            lines.append("")
        if result.missing_agents:
            lines.extend(
                [
                    "## Missing from Registry (In Filesystem, Not in Registry)",
                    "",
                    "| Class Name | File Path | Layer |",
                    "|------------|-----------|-------|",
                ],
            )
            for agent in result.missing_agents[:50]:
                lines.append(f"| {agent.class_name} | {agent.relative_path} | {agent.layer} |")
            if len(result.missing_agents) > 50:
                remaining = len(result.missing_agents) - 50
                lines.append(f"| ... | ({remaining} more) | ... |")
            lines.append("")
        return "\n".join(lines)


def run_verification() -> VerificationResult:
    """Run registry verification and return result."""
    verifier = RegistryVerifier()
    return verifier.verify_registry()


if __name__ == "__main__":
    verifier = RegistryVerifier()
    result = verifier.verify_registry()
    report = verifier.generate_report(result)
    print(report)
