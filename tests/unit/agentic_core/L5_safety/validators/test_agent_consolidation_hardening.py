import ast
import importlib
import inspect
from pathlib import Path

import pytest

# -------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.parent

# The 11 Unified Agents that must reside ONLY in 'unified'
UNIFIED_AGENTS = [
    "CodeDetectorAgent",
    "CodeEnforcerAgent",
    "CodeHealerAgent",
    "CodeValidatorAgent",
    "ResourceManagerAgent",
    "SafetyDetectorAgent",
    "SafetyExecutorAgent",
    "SecurityManagerAgent",
    "StructureEnforcerAgent",
    "StructureHealerAgent",
    "StructureValidatorAgent",
]

# Canonical Paths (The "Source of Truth")
CANONICAL_UNIFIED_PATH = "agentic_core.L5_safety.unified"
CANONICAL_ROUTER_PATH = "agentic_core.L2_execution.unified"
CANONICAL_HYGIENE_PATH = "agentic_core.L5_safety.validators"

# Deprecated Paths (Forbidden)
DEPRECATED_PATHS = {
    "agentic_core.L5_safety.enforcement": UNIFIED_AGENTS,
    "agentic_core.L2_execution.reasoning": ["ModelRouterAgent"],
    "apps_shared.base_agents": ["HygieneGuardianAgent"],
}


class TestConsolidationRuntimeIntegrity:
    """
    Verifies that the agents actually exist and are importable
    from their new canonical locations.
    """

    @pytest.mark.parametrize("agent_name", UNIFIED_AGENTS)
    def test_UnifiedAgents_importable_from_canonical(self, agent_name):
        """Verify each unified agent loads from agentic_core.L5_safety.unified"""
        module = importlib.import_module(CANONICAL_UNIFIED_PATH)
        agent_class = getattr(module, agent_name, None)
        assert agent_class is not None, f"{agent_name} not found in {CANONICAL_UNIFIED_PATH}"
        assert inspect.isclass(agent_class), f"{agent_name} is not a class"

    def test_model_router_importable_from_canonical(self):
        """Verify ModelRouterAgent loads from execution unified"""
        module = importlib.import_module(CANONICAL_ROUTER_PATH)
        agent_class = getattr(module, "ModelRouterAgent", None)
        assert agent_class is not None

    def test_hygiene_guardian_importable_from_canonical(self):
        """Verify HygieneGuardianAgent loads from validators"""
        # Direct import to avoid circular import issues with __init__.py
        from agentic_core.L5_safety.reasoning.HygieneGuardianAgent import HygieneGuardianAgent

        assert HygieneGuardianAgent is not None
        assert inspect.isclass(HygieneGuardianAgent)


class TestConsolidationStaticAnalysis:
    """
    AST-based static analysis to ensure no files in the codebase
    are importing from deprecated locations.
    """

    def _get_python_files(self) -> list[Path]:
        """Recursively get all .py files in relevant directories."""
        # Exclude this test file and archives
        exclude_dirs = ["archives", ".git", "__pycache__", "venv", "env"]
        files = []

        for root_dir in [PROJECT_ROOT / "agentic_core", PROJECT_ROOT / "apps_shared"]:
            if not root_dir.exists():
                continue
            for path in root_dir.rglob("*.py"):
                if any(excluded in str(path) for excluded in exclude_dirs):
                    continue
                files.append(path)
        return files

    def _check_imports_in_file(self, file_path: Path) -> list[str]:
        """
        Parses a file and checks for forbidden imports.
        Returns a list of violation messages.
        """
        violations = []
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return []  # Skip unparseable files

        for node in ast.walk(tree):
            # Check: from X import Y
            if isinstance(node, ast.ImportFrom):
                module = node.module
                if not module:
                    continue

                # Check against all deprecated paths
                for bad_path, bad_agents in DEPRECATED_PATHS.items():
                    if module == bad_path or module.startswith(bad_path + "."):
                        # Check if specific forbidden agents are imported
                        for name in node.names:
                            imported_name = name.name
                            if imported_name in bad_agents or "*" in bad_agents:
                                violations.append(
                                    f"Line {node.lineno}: Imports '{imported_name}' from deprecated '{module}'"
                                )

            # Check: import X (less common for deep nesting, but good to check)
            elif isinstance(node, ast.Import):
                for name in node.names:
                    for bad_path, bad_agents in DEPRECATED_PATHS.items():
                        if name.name == bad_path:
                            violations.append(
                                f"Line {node.lineno}: Direct import of deprecated module '{name.name}'"
                            )

        return violations

    def test_identify_deprecated_imports(self):
        """
        Scans the codebase for imports from deprecated locations.

        During Phase 1 (Pre-Consolidation): This test acts as a finder.
        During Phase 4 (Verification): This test acts as a regression guardrail.
        """
        all_files = self._get_python_files()
        all_violations = {}

        for file_path in all_files:
            violations = self._check_imports_in_file(file_path)
            if violations:
                rel_path = file_path.relative_to(PROJECT_ROOT)
                all_violations[str(rel_path)] = violations

        if all_violations:
            # Format the output for the developer
            report = ["\n[!] DEPRECATED IMPORT VIOLATIONS FOUND:"]
            for fpath, errors in all_violations.items():
                report.append(f"\nFile: {fpath}")
                for err in errors:
                    report.append(f"  - {err}")

            report.append("\nACTION REQUIRED: Update imports in these files to use canonical paths.")

            # Fail the test if violations exist
            pytest.fail("\n".join(report))


class TestDirectoryIntegrity:
    """
    Ensures directory structure follows architectural standards.
    """

    def test_guardrails_contains_no_UnifiedAgents(self):
        """Ensure agentic_core/L5_safety/enforcement/ contains zero Unified* files."""
        guardrails_dir = PROJECT_ROOT / "agentic_core" / "L5_safety" / "guardrails"
        if not guardrails_dir.exists():
            pytest.skip("guardrails directory does not exist")

        unified_files = list(guardrails_dir.glob("Unified*.py"))
        assert len(unified_files) == 0, (
            f"Found {len(unified_files)} Unified* files in guardrails/ that should be in unified/: "
            f"{[f.name for f in unified_files]}"
        )

    def test_toolregistry_contains_no_unified_model_router(self):
        """Ensure tool_registry does not contain ModelRouterAgent."""
        toolregistry_dir = PROJECT_ROOT / "agentic_core" / "L2_execution" / "tool_registry"
        if not toolregistry_dir.exists():
            pytest.skip("tool_registry directory does not exist")

        router_file = toolregistry_dir / "ModelRouterAgent.py"
        assert not router_file.exists(), (
            "ModelRouterAgent.py should not exist in tool_registry/ - "
            "canonical location is L2_execution/unified/"
        )

    def test_apps_shared_contains_no_hygiene_guardian(self):
        """Ensure apps_shared/base_agents does not contain HygieneGuardianAgent."""
        apps_shared_dir = PROJECT_ROOT / "apps_shared" / "base_agents"
        if not apps_shared_dir.exists():
            pytest.skip("apps_shared/base_agents directory does not exist")

        hygiene_file = apps_shared_dir / "HygieneGuardianAgent.py"
        assert not hygiene_file.exists(), (
            "HygieneGuardianAgent.py should not exist in apps_shared/base_agents/ - "
            "canonical location is L5_safety/validators/"
        )


class TestNamingConventionCompliance:
    """
    Verifies naming conventions are followed in key directories.
    """

    def test_validators_naming_convention(self):
        """Verify files in validators/ follow naming conventions."""
        validators_dir = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators"
        if not validators_dir.exists():
            pytest.skip("validators directory does not exist")

        # Get all Python files (excluding __init__.py and non-agent files)
        py_files = [f for f in validators_dir.glob("*.py") if f.name != "__init__.py"]

        # Known non-agent files that are allowed
        allowed_non_agent_files = {
            "decorators.py",
            "filesystem.py",
            "healing_strategies.py",
            "healing_healing_strategies.py",
            "location_constants.py",
            "ssot_relocator.py",
            "structure_blueprint.py",
            "intervention_server.py",
        }

        violations = []
        for f in py_files:
            if f.name in allowed_non_agent_files:
                continue
            # Agent files should end with Agent.py
            if not f.name.endswith("Agent.py"):
                violations.append(f.name)

        assert len(violations) == 0, f"Files in validators/ should end with 'Agent.py': {violations}"


class TestPotentialOverlapsVerification:
    """
    Verifies that potential overlaps identified in the analysis are intentional separations.
    """

    def test_location_agents_are_distinct(self):
        """Verify Location* agents have different implementations (not duplicates)."""
        import hashlib

        validators_dir = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators"

        location_files = {
            "LocationAgent.py": validators_dir / "LocationAgent.py",
            "LocationValidatorAgent.py": validators_dir / "LocationValidatorAgent.py",
            "LocationHealerAgent.py": validators_dir / "LocationHealerAgent.py",
        }

        hashes = {}
        for name, path in location_files.items():
            if path.exists():
                hashes[name] = hashlib.md5(path.read_bytes()).hexdigest()

        # All hashes should be unique (different implementations)
        unique_hashes = set(hashes.values())
        assert len(unique_hashes) == len(hashes), (
            f"Location agents should have different implementations. Found duplicates: {hashes}"
        )

    def test_import_agents_are_distinct(self):
        """Verify Import* agents have different implementations."""
        import hashlib

        gravity_dir = PROJECT_ROOT / "agentic_core" / "L5_safety" / "gravity"

        import_files = {
            "ImportAgent.py": gravity_dir / "ImportAgent.py",
            "ImportLockAgent.py": gravity_dir / "ImportLockAgent.py",
        }

        hashes = {}
        for name, path in import_files.items():
            if path.exists():
                hashes[name] = hashlib.md5(path.read_bytes()).hexdigest()

        unique_hashes = set(hashes.values())
        assert len(unique_hashes) == len(hashes), (
            f"Import agents should have different implementations. Found duplicates: {hashes}"
        )

    def test_strategic_agents_are_distinct(self):
        """Verify Strategic* agents have different implementations."""
        import hashlib

        strategic_files = {
            "StrategicRecommendationAgent.py": PROJECT_ROOT
            / "agentic_core"
            / "L1_cognition"
            / "thought_engine"
            / "StrategicRecommendationAgent.py",
            "StrategicPlannerAgent.py": PROJECT_ROOT
            / "agentic_core"
            / "L2_execution"
            / "tool_registry"
            / "StrategicPlannerAgent.py",
        }

        hashes = {}
        for name, path in strategic_files.items():
            if path.exists():
                hashes[name] = hashlib.md5(path.read_bytes()).hexdigest()

        unique_hashes = set(hashes.values())
        assert len(unique_hashes) == len(hashes), (
            f"Strategic agents should have different implementations. Found duplicates: {hashes}"
        )
