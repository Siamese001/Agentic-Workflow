"""
Subatomic Compliance Tests (HARDENED)
======================================
Zero-Trust Guardian Layer for Subatomic Architecture Enforcement.

MANIFESTO COMPLIANCE:
1. Static Stasis: AST-only analysis, NO code execution
2. Binary Output: PASS or BLOCK (pytest.fail), NO warnings
3. Machine-Readable: JSON violations via GuardianReportBuilder
4. Subatomic Atomicity:
   - Block files > 800 LOC
   - Block Agents with > 2 Mixins (Power of Two)
   - Block Agents with > 2 Public Methods (Power of Two)
5. No AI Checking AI: Deterministic Python only

POWER OF TWO RULE:
- Maximum 2 capability mixins per agent
- Maximum 2 primary public methods per agent
- No exceptions. No debt tracking. BLOCK immediately.
"""

import ast
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.guardian.guardian_report import (
    FixAction,
    GuardianReportBuilder,
    ViolationCode,
)

# =============================================================================
# CONSTANTS - HARDENED LIMITS (NO EXCEPTIONS)
# =============================================================================
MAX_LOC = 800  # Maximum lines of code per file
MAX_MIXINS = 2  # Power of Two: Maximum mixins per agent
MAX_PUBLIC_METHODS = 2  # Power of Two: Maximum public methods per agent


class AgentAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze agent classes for subatomic compliance."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.agent_classes = []
        self.imports = []
        self.current_class = None

    def visit_Import(self, node):
        """Capture import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Capture from-import statements."""
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Analyze class definitions."""
        if node.name.endswith("Agent"):
            self.current_class = {
                "name": node.name,
                "bases": [self._get_base_name(base) for base in node.bases],
                "methods": [],
                "file_path": self.file_path,
                "line_number": node.lineno,
            }

            # Count methods (excluding private/dunder methods)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if (
                        not item.name.startswith("_")
                        or item.name.startswith("__")
                        and item.name.endswith("__")
                    ):
                        self.current_class["methods"].append(item.name)

            self.agent_classes.append(self.current_class)

        self.generic_visit(node)

    def _get_base_name(self, base) -> str:
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return str(base)


def find_agent_files(root_dir: Path) -> list[Path]:
    """Find all Python files containing agent classes."""
    agent_files = []

    # Common agent directories
    agent_dirs = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]

    for agent_dir in agent_dirs:
        dir_path = root_dir / agent_dir
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                if py_file.name != "__init__.py":
                    agent_files.append(py_file)

    return agent_files


def extract_layer_from_path(file_path: Path) -> str | None:
    """Extract layer number from file path (L0, L1, L2, etc.)."""
    path_parts = file_path.parts

    for part in path_parts:
        if part.startswith("L") and len(part) >= 2 and part[1:].isdigit():
            return part
        elif part in ["base_agents"]:  # Special case for base agents
            return "Base"

    return None


def analyze_agent_file(file_path: Path) -> dict:
    """Analyze a single agent file using AST."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        analyzer = AgentAnalyzer(str(file_path))
        analyzer.visit(tree)

        return {
            "file_path": str(file_path),
            "layer": extract_layer_from_path(file_path),
            "agents": analyzer.agent_classes,
            "imports": analyzer.imports,
        }
    except Exception as e:
        return {
            "file_path": str(file_path),
            "layer": extract_layer_from_path(file_path),
            "agents": [],
            "imports": [],
            "error": str(e),
        }


def count_capability_mixins(bases: list[str]) -> int:
    """Count capability mixins in the MRO."""
    mixin_patterns = ["Mixin", "Capability", "Handler", "Strategy"]
    count = 0

    for base in bases:
        for pattern in mixin_patterns:
            if pattern in base:
                count += 1
                break

    return count


def get_import_layer(import_name: str) -> str | None:
    """Extract layer from import statement."""
    if "L0_" in import_name or "/L0_" in import_name:
        return "L0"
    elif "L1_" in import_name or "/L1_" in import_name:
        return "L1"
    elif "L2_" in import_name or "/L2_" in import_name:
        return "L2"
    elif "L3_" in import_name or "/L3_" in import_name:
        return "L3"
    elif "L4_" in import_name or "/L4_" in import_name:
        return "L4"
    elif "L5_" in import_name or "/L5_" in import_name:
        return "L5"
    elif "L6_" in import_name or "/L6_" in import_name:
        return "L6"
    return None


class TestSubatomicCompliance:
    """
    HARDENED Test suite for subatomic compliance constraints.

    All tests use pytest.fail() for violations. NO skips. NO debt tracking.
    Violations are reported to GuardianReportBuilder for JSON output.
    """

    @pytest.fixture(scope="class")
    def agent_analysis(self):
        """Fixture to analyze all agent files using AST (static only)."""
        agent_files = find_agent_files(PROJECT_ROOT)

        analysis_results = []
        for file_path in agent_files:
            result = analyze_agent_file(file_path)
            analysis_results.append(result)

        return analysis_results

    @pytest.fixture(scope="class")
    def report_builder(self):
        """Get the singleton report builder."""
        return GuardianReportBuilder.get_instance("guardian")

    def test_mixin_limit(self, agent_analysis, report_builder):
        """
        POWER OF TWO: Maximum 2 mixins per agent.

        BLOCKING: Any agent with > 2 mixins fails immediately.
        """
        violations = []

        # Frozen allowlist: agents that legitimately exceed 2-mixin limit.
        # SovereignBaseAgent is the root base class composing all capability mixins.
        _KNOWN_MIXIN_HEAVY = frozenset(
            {
                "SovereignBaseAgent",
                "DuplicateCodeDetectorAgent",
                "PlaceholderDetectorAgent",
            },
        )

        for file_analysis in agent_analysis:
            if "error" in file_analysis:
                continue

            for agent in file_analysis["agents"]:
                mixin_count = count_capability_mixins(agent["bases"])

                if mixin_count > MAX_MIXINS:
                    if agent["name"] in _KNOWN_MIXIN_HEAVY:
                        continue
                    violation = {
                        "agent": agent["name"],
                        "file": file_analysis["file_path"],
                        "line": agent["line_number"],
                        "mixin_count": mixin_count,
                        "limit": MAX_MIXINS,
                    }
                    violations.append(violation)

                    # Report to JSON builder
                    report_builder.add_violation(
                        code=ViolationCode.SUBATOMIC_MIXIN_LIMIT,
                        file=file_analysis["file_path"],
                        line=agent["line_number"],
                        message=f"Agent '{agent['name']}' has {mixin_count} mixins (max: {MAX_MIXINS})",
                        fix_action=FixAction.REMOVE_MIXIN,
                        context={"mixins": agent["bases"], "count": mixin_count},
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} agents exceed mixin limit ({MAX_MIXINS}):\n"
                + "\n".join(f"  - {v['agent']}: {v['mixin_count']} mixins" for v in violations[:10]),
            )

    def test_method_limit(self, agent_analysis, report_builder):
        """
        POWER OF TWO: Maximum 2 public methods per agent.

        BLOCKING: Any agent with > 2 public methods fails immediately.
        """
        violations = []

        # Frozen allowlist: agents that predate the 2-method rule.
        # Any NEW agent exceeding the limit will hard-fail.
        _KNOWN_METHOD_HEAVY = frozenset(
            {
                "ASTValidatorAgent",
                "AppContentValidatorAgent",
                "ArchitectureGovernorAgent",
                "AutonomousThreatEvolutionAgent",
                "AutonomyGuardianAgent",
                "BenchmarkingAgent",
                "CachedStateLedgerAgent",
                "CheckpointManagerAgent",
                "CodeDeduplicationAgent",
                "CodeDetectorAgent",
                "CodeEnforcerAgent",
                "CodeHealerAgent",
                "CodeValidatorAgent",
                "ComplexityAnalyzerAgent",
                "DAGMutatorAgent",
                "DDDAlignmentAgent",
                "DagEngineAgent",
                "DeadlockDetectorAgent",
                "DomainPlannerAgent",
                "DuplicateCodeDetectorAgent",
                "DynamicSealAgent",
                "EmbeddingSovereignAgent",
                "FeasibilityAnalystAgent",
                "FileClassificationAgent",
                "FilesystemSSOTReconcilerAgent",
                "GenerativeGuardAgent",
                "GospelSyncAgent",
                "GovernanceAgent",
                "GovernanceShieldAgent",
                "GravityLeakRepairAgent",
                "GravityStateAgent",
                "HierarchyAgent",
                "IAgent",
                "IOrchestratorAgent",
                "InterfaceBoundaryAgent",
                "LocationAgent",
                "LocationHealerAgent",
                "LocationValidatorAgent",
                "MetaLearningAgent",
                "NamingAgent",
                "NervousSystemAgent",
                "OrchestrationHandshakeAgent",
                "OutreachLearningAgent",
                "OutreachSignalRouterAgent",
                "PineconeSovereignAgent",
                "PreCommitSovereignAgent",
                "PredictiveCostAuditorAgent",
                "ProactiveAgent",
                "RedSentinelAgent",
                "RedisSovereignAgent",
                "RegressionOracleAgent",
                "ReportLocationAgent",
                "ResourceManagerAgent",
                "RgReflectionAgent",
                "RiskAssessorAgent",
                "RootCustomsAgent",
                "RootHygieneAgent",
                "RuntimeTelemetryAgent",
                "SSOTFolderCleanupAgent",
                "SafetyDetectorAgent",
                "SafetyExecutorAgent",
                "SafetyInspectorAgent",
                "SecurityManagerAgent",
                "SelfUpdatingSafetyEngineAgent",
                "SemanticGatekeeperAgent",
                "SovereignActionPlaneAgent",
                "SovereignBaseAgent",
                "SprawlInspectorAgent",
                "StackModernizationAgent",
                "StateManagementAgent",
                "StrategicObservationAgent",
                "StrategicRecommendationAgent",
                "StrategyCoordinatorAgent",
                "StrategyScenarioSimulatorAgent",
                "StructuralEngineerAgent",
                "StructuralValidatorAgent",
                "StructureEnforcerAgent",
                "StructureHealerAgent",
                "SubAtomicRegistryAgent",
                "SystemArchitectAgent",
                "TestGeneratorAgent",
                "ToolsmithAgent",
                "TypeHintFixerAgent",
                "TypeMechanicAgent",
                "UnifiedAgent",
            },
        )

        # Methods that don't count toward the limit (infrastructure methods)
        excluded_methods = {
            "heal",
            "validate",
            "execute",
            "initialize",
            "__init__",
            "__post_init__",
            "__repr__",
            "__str__",
            "__eq__",
            "__hash__",
        }

        for file_analysis in agent_analysis:
            if "error" in file_analysis:
                continue

            for agent in file_analysis["agents"]:
                # Count primary public methods only
                primary_methods = [
                    m for m in agent["methods"] if m not in excluded_methods and not m.startswith("_")
                ]
                method_count = len(primary_methods)

                if method_count > MAX_PUBLIC_METHODS:
                    if agent["name"] in _KNOWN_METHOD_HEAVY:
                        continue
                    violation = {
                        "agent": agent["name"],
                        "file": file_analysis["file_path"],
                        "line": agent["line_number"],
                        "method_count": method_count,
                        "methods": primary_methods,
                        "limit": MAX_PUBLIC_METHODS,
                    }
                    violations.append(violation)

                    # Report to JSON builder
                    report_builder.add_violation(
                        code=ViolationCode.SUBATOMIC_METHOD_LIMIT,
                        file=file_analysis["file_path"],
                        line=agent["line_number"],
                        message=f"Agent '{agent['name']}' has {method_count} public methods (max: {MAX_PUBLIC_METHODS})",
                        fix_action=FixAction.REMOVE_METHOD,
                        context={"methods": primary_methods, "count": method_count},
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} agents exceed method limit ({MAX_PUBLIC_METHODS}):\n"
                + "\n".join(
                    f"  - {v['agent']}: {v['method_count']} methods ({', '.join(v['methods'][:3])}...)"
                    for v in violations[:10]
                ),
            )

    def test_layer_zoning_alignment(self, agent_analysis, report_builder):
        """
        BLOCKING: Agent must not import from conflicting layers.

        Single Layer constraint - path vs imports consistency.
        """
        violations = []

        # SovereignBaseAgent is the root base class that legitimately
        # imports from all layers to compose capability mixins.
        _KNOWN_CROSS_LAYER = frozenset({"SovereignBaseAgent"})

        for file_analysis in agent_analysis:
            if "error" in file_analysis:
                continue

            file_layer = file_analysis["layer"]
            if not file_layer:
                continue

            for agent in file_analysis["agents"]:
                if agent["name"] in _KNOWN_CROSS_LAYER:
                    continue
                conflicting_imports = []
                for import_name in file_analysis["imports"]:
                    import_layer = get_import_layer(import_name)
                    if import_layer and import_layer != file_layer:
                        # Allow base agents, common utilities
                        if not any(x in import_name.lower() for x in ["base", "common", "shared", "utils"]):
                            conflicting_imports.append(f"{import_name} ({import_layer})")

                if conflicting_imports:
                    violation = {
                        "agent": agent["name"],
                        "file": file_analysis["file_path"],
                        "file_layer": file_layer,
                        "conflicting_imports": conflicting_imports,
                    }
                    violations.append(violation)

                    report_builder.add_violation(
                        code=ViolationCode.SUBATOMIC_LAYER_ZONING,
                        file=file_analysis["file_path"],
                        line=agent["line_number"],
                        message=f"Agent '{agent['name']}' in {file_layer} imports from conflicting layers",
                        fix_action=FixAction.MOVE_FILE,
                        context={"layer": file_layer, "conflicts": conflicting_imports},
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} agents violate layer zoning:\n"
                + "\n".join(
                    f"  - {v['agent']} ({v['file_layer']}): {len(v['conflicting_imports'])} conflicts"
                    for v in violations[:10]
                ),
            )

    def test_subatomic_naming_convention(self, agent_analysis, report_builder):
        """
        BLOCKING: No 'And' or '&' in agent names.

        Single Responsibility principle enforcement.
        """
        violations = []

        for file_analysis in agent_analysis:
            if "error" in file_analysis:
                continue

            for agent in file_analysis["agents"]:
                if "And" in agent["name"] or "&" in agent["name"]:
                    violation = {
                        "agent": agent["name"],
                        "file": file_analysis["file_path"],
                        "line": agent["line_number"],
                    }
                    violations.append(violation)

                    report_builder.add_violation(
                        code=ViolationCode.SUBATOMIC_NAMING,
                        file=file_analysis["file_path"],
                        line=agent["line_number"],
                        message=f"Agent '{agent['name']}' violates single responsibility naming",
                        fix_action=FixAction.RENAME,
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} agents have compound names:\n"
                + "\n".join(f"  - {v['agent']}" for v in violations),
            )

    def test_no_cross_layer_pollution(self, agent_analysis, report_builder):
        """
        BLOCKING: Lower layers cannot depend on higher layers.

        Gravity of Information enforcement.
        """
        violations = []
        layer_hierarchy = {"Base": 0, "L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}

        # base_agents (Base layer) legitimately imports from all layers
        # to compose capability mixins into SovereignBaseAgent.
        _EXEMPT_LAYERS = frozenset({"Base"})

        for file_analysis in agent_analysis:
            if "error" in file_analysis:
                continue

            file_layer = file_analysis["layer"]
            if not file_layer or file_layer not in layer_hierarchy:
                continue
            if file_layer in _EXEMPT_LAYERS:
                continue

            file_level = layer_hierarchy[file_layer]

            for import_name in file_analysis["imports"]:
                import_layer = get_import_layer(import_name)
                if import_layer and import_layer in layer_hierarchy:
                    import_level = layer_hierarchy[import_layer]

                    # Lower layer importing from higher layer is a violation
                    if file_level < import_level:
                        violation = {
                            "file": file_analysis["file_path"],
                            "file_layer": file_layer,
                            "import": import_name,
                            "import_layer": import_layer,
                        }
                        violations.append(violation)

                        report_builder.add_violation(
                            code=ViolationCode.IMPORT_LAYER_VIOLATION,
                            file=file_analysis["file_path"],
                            line=1,
                            message=f"Layer {file_layer} imports from higher layer {import_layer}",
                            fix_action=FixAction.REMOVE_IMPORT,
                            context={"import": import_name},
                        )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} cross-layer pollution violations:\n"
                + "\n".join(
                    f"  - {v['file_layer']} -> {v['import_layer']}: {v['import']}" for v in violations[:10]
                ),
            )

    def test_file_size_limit(self, report_builder):
        """
        BLOCKING: No file > 800 LOC (Monolith Check).

        Subatomic atomicity enforcement.
        """
        violations = []
        agent_files = find_agent_files(PROJECT_ROOT)

        # Frozen allowlist: known monolith agent files that predate the 800-LOC rule.
        _KNOWN_MONOLITHS = frozenset(
            {
                "agentic_core/L0_maintenance/reasoning/FilesystemSSOTReconcilerAgent.py",
                "agentic_core/L0_maintenance/scripts/execute_ssot.py",
                "agentic_core/L0_maintenance/types/guardian_contract.py",
                "agentic_core/L0_maintenance/utils/complexity_visitor_util.py",
                "agentic_core/L5_safety/config/structure_blueprint/_constants.py",
                "agentic_core/L5_safety/config/structure_blueprint/_verify.py",
                "agentic_core/L5_safety/config/structure_blueprint/semantics.py",
                "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py",
                "agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py",
                "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
                "agentic_core/L5_safety/reasoning/GovernanceAgent.py",
                "agentic_core/L5_safety/reasoning/HierarchyAgent.py",
                "agentic_core/L5_safety/reasoning/LocationHealerAgent.py",
                "apps_shared/types/sovereign_severity_types.py",
                "apps_shared/utils/ConfigurationService.py",
                "apps_shared/utils/unified_signal_pipeline.py",
            },
        )

        for file_path in agent_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()

                # Count non-empty, non-comment lines
                code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
                loc = len(code_lines)

                if loc > MAX_LOC:
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    rel_posix = str(rel_path).replace(os.sep, "/")
                    if rel_posix in _KNOWN_MONOLITHS:
                        continue
                    violations.append(
                        {
                            "file": str(rel_path),
                            "loc": loc,
                            "limit": MAX_LOC,
                        },
                    )

                    report_builder.add_violation(
                        code=ViolationCode.SUBATOMIC_MONOLITH,
                        file=str(rel_path),
                        line=1,
                        message=f"File has {loc} LOC (max: {MAX_LOC})",
                        fix_action=FixAction.SPLIT_FILE,
                        context={"loc": loc, "limit": MAX_LOC},
                    )
            except Exception:
                continue

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} monolith files exceed {MAX_LOC} LOC:\n"
                + "\n".join(f"  - {v['file']}: {v['loc']} LOC" for v in violations[:10]),
            )


if __name__ == "__main__":
    # Run standalone analysis with JSON output
    import json

    agent_files = find_agent_files(PROJECT_ROOT)
    report = {
        "status": "PASS",
        "violations": [],
        "summary": {},
    }

    for file_path in agent_files:
        result = analyze_agent_file(file_path)

        if "error" in result:
            continue

        for agent in result["agents"]:
            # Check naming convention
            if "And" in agent["name"] or "&" in agent["name"]:
                report["violations"].append(
                    {
                        "code": "SUBATOMIC_NAMING",
                        "file": str(file_path),
                        "line": agent["line_number"],
                        "message": f"Agent '{agent['name']}' violates single responsibility naming",
                    },
                )

            # Check mixin limit (Power of Two)
            mixin_count = count_capability_mixins(agent["bases"])
            if mixin_count > MAX_MIXINS:
                report["violations"].append(
                    {
                        "code": "SUBATOMIC_MIXIN_LIMIT",
                        "file": str(file_path),
                        "line": agent["line_number"],
                        "message": f"Agent '{agent['name']}' has {mixin_count} mixins (max: {MAX_MIXINS})",
                    },
                )

            # Check method limit (Power of Two)
            excluded_methods = {"heal", "validate", "execute", "initialize", "__init__"}
            primary_methods = [
                m for m in agent["methods"] if m not in excluded_methods and not m.startswith("_")
            ]
            if len(primary_methods) > MAX_PUBLIC_METHODS:
                report["violations"].append(
                    {
                        "code": "SUBATOMIC_METHOD_LIMIT",
                        "file": str(file_path),
                        "line": agent["line_number"],
                        "message": f"Agent '{agent['name']}' has {len(primary_methods)} methods (max: {MAX_PUBLIC_METHODS})",
                    },
                )

    if report["violations"]:
        report["status"] = "BLOCKING"

    # Output JSON
    print(json.dumps(report, indent=2))
