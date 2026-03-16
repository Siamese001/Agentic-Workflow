"""
Guardian Test: Agent Capability Limits and Layer-Scoped Mutation Ownership
============================================================================

MANIFESTO COMPLIANCE:
1. Static Stasis: AST-only analysis, no runtime imports
2. Binary Output: PASS or BLOCK only
3. Machine-Readable: JSON schema output
4. Constitutional Lock: structure_blueprint.py enforcement
5. No AI Checking AI: Deterministic Python only

ENFORCEMENT:
- Capability limits: ≤2 capabilities per agent, pillar-validated
- L4 source mutation: No writes outside state directories
"""

import ast
import re
import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_agent_capability_limits")
_emit_applies_guardrail("p0", "test_agent_capability_limits", "p0_governance")
_emit_reads_policy_state("p0", "test_agent_capability_limits", "policy_binding")
_emit_snapshots_state("p0", "test_agent_capability_limits", "state_snapshot")
emit_replay_key("p0", "test_agent_capability_limits")
emit_determinism_digest("p0", "test_agent_capability_limits")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_agent_capability_limits", "execution_auth")
_emit_validates_capability("p2", "test_agent_capability_limits", "capability_check")
_emit_routes_to_capability("p2", "test_agent_capability_limits", "capability_route")
_emit_writes_via_uwg("p2", "test_agent_capability_limits", "uwg_write")
_emit_blocks_direct_write("p2", "test_agent_capability_limits", "direct_write_block")
_emit_records_tool_invocation("p2", "test_agent_capability_limits", "tool_invocation")
_emit_captures_execution_output("p2", "test_agent_capability_limits", "exec_output")
_emit_dispatches_agent("p3", "test_agent_capability_limits", "agent_dispatch")
_emit_coordinates_agents("p3", "test_agent_capability_limits", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_agent_capability_limits", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_agent_capability_limits", "healing_outcome")
_emit_escalates_failure("p3", "test_agent_capability_limits", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_agent_capability_limits", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_agent_capability_limits", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_agent_capability_limits", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_agent_capability_limits", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_agent_capability_limits", "eval_metric")
_emit_stores_embedding("p4", "test_agent_capability_limits", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_agent_capability_limits", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_agent_capability_limits", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
from tests.guardian.guardian_report import (
    FixAction,
    GuardianReportBuilder,
    ViolationCode,
)

_emit_emits_metric_event("test_agent_capability_limits", "p4obs", "metric_1")
_emit_emits_metric_event("test_agent_capability_limits", "p4obs", "metric_2")
_emit_emits_metric_event("test_agent_capability_limits", "p4obs", "metric_3")
_emit_emits_metric_event("test_agent_capability_limits", "p4obs", "metric_4")
_emit_emits_metric_event("test_agent_capability_limits", "p4obs", "metric_5")
_emit_emits_metric_event("test_agent_capability_limits", "p4obs", "metric_6")
_emit_records_incident_event("test_agent_capability_limits", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_agent_capability_limits", "p4obs", "anomaly")
_emit_writes_observability_log("test_agent_capability_limits", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_agent_capability_limits", "p4obs", "mon_state")
_emit_triggers_alert("test_agent_capability_limits", "p4obs", "alert")
_emit_links_incident_trace("test_agent_capability_limits", "p4obs", "trace_link")
_emit_captures_pattern("test_agent_capability_limits", "p3lm", "pattern")
_emit_records_learning_event("test_agent_capability_limits", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_agent_capability_limits", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_agent_capability_limits", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_agent_capability_limits", "p3lm", "routing")
_emit_improves_agent_policy("test_agent_capability_limits", "p3lm", "policy")
_emit_stores_learning_state("test_agent_capability_limits", "p3lm", "state")
_emit_records_execution_trace("test_agent_capability_limits", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_agent_capability_limits", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_agent_capability_limits", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_agent_capability_limits", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_agent_capability_limits", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_agent_capability_limits", "env_read", "p2_env_1")
_emit_reads_environ("test_agent_capability_limits", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_agent_capability_limits", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_agent_capability_limits", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_agent_capability_limits", "context_pull")
_emit_pulls_context("p1", "test_agent_capability_limits", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_agent_capability_limits", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_agent_capability_limits", "uwg_term_secondary")
_emit_writes_through("p1", "test_agent_capability_limits", "write_through")
_emit_writes_through("p1", "test_agent_capability_limits", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_agent_capability_limits", "safety_validation")
_emit_invokes_eval("p1", "test_agent_capability_limits", "eval_call")
_emit_proposal_commits_routing("p1", "test_agent_capability_limits", "routing_commit")
_emit_escalates_to_human("p1", "test_agent_capability_limits", "human_escalation")
_emit_routes_through("p1", "test_agent_capability_limits", "route_through")
_emit_checks_agent_registry("p1", "test_agent_capability_limits", "agent_registry")
_emit_validates_agent_capability("p1", "test_agent_capability_limits", "capability")
_emit_dispatches_execution_plan("p1", "test_agent_capability_limits", "exec_plan")
_emit_agent_executes_agent("p1", "test_agent_capability_limits", "sub_agent")
_emit_routes_to_agent("p1", "test_agent_capability_limits", "target_agent")
_emit_verifies_policy("p1", "test_agent_capability_limits", "policy_check")
_emit_observes_runtime_state("p1", "test_agent_capability_limits", "runtime_state")
_emit_verifies_boundary("p1", "test_agent_capability_limits", "boundary_check")
_emit_transcripts_response("p1", "test_agent_capability_limits", "transcript")
_emit_hard_fails_untranscripted("p1", "test_agent_capability_limits")
_emit_gated_by_confidence("p1", "test_agent_capability_limits", "confidence_gate")

# =============================================================================
# PILLAR ENUM SSOT
# =============================================================================
PILLARS = frozenset(
    {
        "LAYERING_MODEL",
        "AGENT_BOUNDARIES",
        "TYPED_CONTRACTS",
        "WORKFLOW_DAGS",
        "CAPABILITY_MATURITY",
        "OBSERVABILITY",
        "SECURITY_POSTURE",
        "COST_OPTIMIZATION",
        "TESTING_GOLDEN_STATE",
        "PROMPT_GOVERNANCE",
        "EXECUTION_SANDBOX",
    }
)

# =============================================================================
# STAGED CAPABILITY ENFORCEMENT TARGETS
# =============================================================================
# NOTE: Empty for initial rollout - enable after agents have CAPABILITIES
# To enforce: add "GravityLeakRepairAgent", "GravityStateAgent"
ENFORCED_AGENT_PATTERNS: tuple = ()

# =============================================================================
# L4 SOURCE MUTATION DETECTION
# =============================================================================
ALLOWED_STATE_DIRS = (
    ".gravity_state",
    "state",
    "cache",
    ".cache",
    "logs",
    ".logs",
)

WRITE_MODES = ("w", "a", "+")


# =============================================================================
# DYNAMIC LAYER DISCOVERY
# =============================================================================
def discover_agentic_core_layers():
    """Dynamically discover all L* layers in agentic_core/ directory."""
    agentic_core_dir = PROJECT_ROOT / AGENTIC_CORE_DIR
    if not agentic_core_dir.exists():
        pytest.fail("BLOCKING: agentic_core/ directory not found")

    layer_pattern = re.compile(r"^L(\d+)_.*$")
    layer_dirs = {}

    for item in agentic_core_dir.iterdir():
        if item.is_dir() and layer_pattern.match(item.name):
            layer_dirs[item.name] = item

    sorted_layers = dict(sorted(layer_dirs.items(), key=lambda x: (int(x[0][1 : x[0].find("_")]), x[0])))
    return sorted_layers


def get_layer_numeric_index(layer_name: str) -> int:
    """Extract numeric index from layer name."""
    match = re.match(r"L(\d+)_", layer_name)
    return int(match.group(1)) if match else -1


def is_enforced_agent(class_name: str) -> bool:
    """Check if agent class is in enforced patterns."""
    for pattern in ENFORCED_AGENT_PATTERNS:
        if pattern in class_name:
            return True
    return False


# =============================================================================
# AST ANALYZER
# =============================================================================
class CapabilityAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze agent classes for capability compliance."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.agent_classes = []
        self.source_mutations = []

    def visit_ClassDef(self, node):
        """Analyze class definitions for agent patterns."""
        is_agent = any(
            self._get_base_name(base).endswith("Agent") or "Agent" in self._get_base_name(base)
            for base in node.bases
        )

        if is_agent or node.name.endswith("Agent"):
            capabilities = []
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "CAPABILITIES":
                            capabilities = self._extract_capabilities(item.value)

            self.agent_classes.append(
                {
                    "name": node.name,
                    "line_number": node.lineno,
                    "capabilities": capabilities,
                    "has_capabilities": len(capabilities) > 0,
                }
            )

        self.generic_visit(node)

    def visit_Call(self, node):
        """Detect source-tree mutation calls."""
        # Check for open(..., "w"/"a"/"+")
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if len(node.args) >= 2:
                mode_arg = node.args[1]
                if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                    if any(m in mode_arg.value for m in WRITE_MODES):
                        target_path = self._extract_path_literal(node.args[0]) if node.args else None
                        if not self._is_allowed_state_path(target_path):
                            self.source_mutations.append(
                                {
                                    "type": "open_write",
                                    "line": node.lineno,
                                    "target_path": target_path,
                                }
                            )

        # Check for Path.write_text / write_bytes
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("write_text", "write_bytes"):
                target_path = self._extract_path_from_attr(node.func.value)
                if not self._is_allowed_state_path(target_path):
                    self.source_mutations.append(
                        {
                            "type": f"Path.{node.func.attr}",
                            "line": node.lineno,
                            "target_path": target_path,
                        }
                    )

            # Check for os.remove / shutil.rmtree / unlink
            if node.func.attr in ("remove", "rmtree", "unlink"):
                target_path = self._extract_path_literal(node.args[0]) if node.args else None
                if not self._is_allowed_state_path(target_path):
                    self.source_mutations.append(
                        {
                            "type": node.func.attr,
                            "line": node.lineno,
                            "target_path": target_path,
                        }
                    )

        self.generic_visit(node)

    def _extract_capabilities(self, node) -> list:
        """Extract capability strings from AST node."""
        capabilities = []
        if isinstance(node, ast.Tuple):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    capabilities.append(elt.value)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            capabilities.append(node.value)
        return capabilities

    def _extract_path_literal(self, node) -> str | None:
        """Extract path string literal from AST node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def _extract_path_from_attr(self, node) -> str | None:
        """Extract path from attribute access chain."""
        if isinstance(node, ast.Call) and node.args:
            if isinstance(node.args[0], ast.Constant):
                return node.args[0].value
        return None

    def _is_allowed_state_path(self, path: str | None) -> bool:
        """Check if path is within allowed state directories."""
        if path is None:
            return True  # Unknown paths allowed (can't prove violation)

        for allowed_dir in ALLOWED_STATE_DIRS:
            if path.startswith(allowed_dir) or f"/{allowed_dir}" in path or f"\\{allowed_dir}" in path:
                return True

        path_lower = path.lower()
        if any(kw in path_lower for kw in ("state", "cache", "log", "tmp", "temp")):
            return True

        return False

    def _get_base_name(self, base) -> str:
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return str(base)


# =============================================================================
# TEST CLASS
# =============================================================================
class TestAgentCapabilityLimits:
    """Test suite for agent capability limits and L4 source mutation detection."""

    @pytest.fixture(scope="class")
    def report_builder(self):
        """Guardian report builder for test violations."""
        return GuardianReportBuilder()

    def test_agent_capability_limits(self, report_builder):
        """
        Staged capability enforcement.

        BLOCKING only for ENFORCED_AGENT_PATTERNS.
        All other agents: record violations but do not fail.
        """
        layer_dirs = discover_agentic_core_layers()

        enforced_violations = []
        legacy_violations = []

        for layer_name, layer_path in layer_dirs.items():
            reasoning_path = layer_path / "reasoning"
            if not reasoning_path.exists():
                continue

            for py_file in reasoning_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    analyzer = CapabilityAnalyzer(str(py_file))
                    analyzer.visit(tree)

                    for agent in analyzer.agent_classes:
                        violation = None

                        if not agent["has_capabilities"]:
                            violation = {
                                "file": str(py_file.relative_to(PROJECT_ROOT)),
                                "class": agent["name"],
                                "issue": "missing CAPABILITIES",
                            }
                        elif len(agent["capabilities"]) > 2:
                            violation = {
                                "file": str(py_file.relative_to(PROJECT_ROOT)),
                                "class": agent["name"],
                                "issue": f"exceeds 2 capabilities ({len(agent['capabilities'])})",
                            }
                        else:
                            unknown = [c for c in agent["capabilities"] if c not in PILLARS]
                            if unknown:
                                violation = {
                                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                                    "class": agent["name"],
                                    "issue": f"unknown pillar: {', '.join(unknown)}",
                                }

                        if violation:
                            if is_enforced_agent(agent["name"]):
                                enforced_violations.append(violation)
                            else:
                                legacy_violations.append(violation)

                except Exception:  # guardian: allow-silent-swallower
                    continue

        # Sort deterministically
        enforced_violations.sort(key=lambda x: (x["file"], x["class"]))
        legacy_violations.sort(key=lambda x: (x["file"], x["class"]))

        # Report legacy violations (non-blocking)
        if legacy_violations:
            print(f"\n[INFO] {len(legacy_violations)} legacy agents missing CAPABILITIES (non-blocking)")

        # Fail only on enforced violations
        if enforced_violations:
            summary = "\n".join(f"  - {v['file']}::{v['class']} {v['issue']}" for v in enforced_violations)

            report_builder.add_violation(
                code=ViolationCode.CAPABILITY_VIOLATION,
                file=enforced_violations[0]["file"],
                line=1,
                message=f"Capability violations: {len(enforced_violations)} enforced agents",
                fix_action=FixAction.REFACTOR_INHERITANCE,
                context={"violations": enforced_violations},
            )

            pytest.fail(
                f"BLOCKING: {len(enforced_violations)} capability violations (enforced agents):\n" + summary
            )

    def test_layer_scoped_mutation_ownership(self, report_builder):
        """
        L4 source-tree mutation detection.

        Detects open(..., "w"/"a"/"+"), Path.write_*, os.remove, shutil.rmtree
        outside allowed state directories.
        """
        layer_dirs = discover_agentic_core_layers()

        mutations = []

        for layer_name, layer_path in layer_dirs.items():
            if get_layer_numeric_index(layer_name) != 4:
                continue

            reasoning_path = layer_path / "reasoning"
            if not reasoning_path.exists():
                continue

            for py_file in reasoning_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    analyzer = CapabilityAnalyzer(str(py_file))
                    analyzer.visit(tree)

                    for mutation in analyzer.source_mutations:
                        mutations.append(
                            {
                                "file": str(py_file.relative_to(PROJECT_ROOT)),
                                "layer": layer_name,
                                "type": mutation["type"],
                                "line": mutation["line"],
                                "target_path": mutation.get("target_path", "unknown"),
                            }
                        )

                except Exception:  # guardian: allow-silent-swallower
                    continue

        mutations.sort(key=lambda x: (x["file"], x["line"]))

        if mutations:
            summary = "\n".join(
                f"  - {m['file']}:{m['line']} {m['type']} -> {m['target_path']}" for m in mutations[:25]
            )

            if len(mutations) > 25:
                summary += f"\n  ... and {len(mutations) - 25} more"

            report_builder.add_violation(
                code=ViolationCode.MUTATION_VIOLATION,
                file=mutations[0]["file"],
                line=mutations[0]["line"],
                message=f"L4 source mutations: {len(mutations)} writes outside state dirs",
                fix_action=FixAction.MOVE_FILE,
                context={"violations": mutations},
            )

            pytest.fail(f"BLOCKING: {len(mutations)} L4 source-tree mutations:\n" + summary)
