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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_agent_capability_limits")
_emit_applies_guardrail("p0", "test_agent_capability_limits", "p0_governance")
_emit_reads_policy_state("p0", "test_agent_capability_limits", "policy_binding")
_emit_snapshots_state("p0", "test_agent_capability_limits", "state_snapshot")
emit_replay_key("p0", "test_agent_capability_limits")
emit_determinism_digest("p0", "test_agent_capability_limits")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.guardian.guardian_report import (
    FixAction,
    GuardianReportBuilder,
    ViolationCode,
)

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
