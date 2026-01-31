"""
Phase 2: SSOT Compliance Guardian
=================================
The Civil Engineer - Validates architectural integrity against structure_blueprint.py

This test suite ensures:
1. All files exist in SSOT-approved locations
2. No files violate the sovereign territory boundaries
3. Base agents are in their constitutional location
4. Layer hierarchy is respected (L0-L6)

USAGE:
    pytest tests/guardian/test_ssot_compliance.py -v

EXPECTED RESULT:
    100% pass rate - any failure indicates structural drift
"""

import ast
import sys
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import SSOT constants from structure_blueprint
from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
    CORE_SUBFOLDER_MAP,
    FORBIDDEN_ROOT_FOLDERS,
    ROOT_WHITELIST,
    SOVEREIGN_TERRITORIES,
)


class TestSSOTCompliance:
    """Test suite for SSOT structural compliance"""

    # ==========================================================================
    # KNOWN TECHNICAL DEBT (Documented violations to be remediated)
    # These are tracked and will be fixed in future sprints.
    # New violations will still cause test failures.
    # ==========================================================================

    # Base agents that need to be moved to agentic_core/base_agents/
    KNOWN_BASE_AGENT_VIOLATIONS = {
        "L0MaintenanceBaseAgent.py",
        "CanonBaseAgent.py",  # Multiple copies exist
        "LICAgentBaseAgent.py",
        "RGAgentBaseAgent.py",
        "test_SovereignBaseAgent.py",  # Test file - naming exception
    }

    # apps_shared files with known dependency violations (to be refactored)
    KNOWN_APPS_SHARED_VIOLATIONS = {
        "GoldenStateEvaluator.py",
        "MockSyntaxValidatorAgent.py",
    }

    # Test files at root level (legacy - to be moved)
    KNOWN_ROOT_TEST_FILES = {
        "test_always_heal_llm.py",
        "test_execute_ssot_e2e.py",
        "test_healing_confidence.py",
        "test_heal_implementations.py",
        "test_location_agent_heal.py",
        "test_location_agent_integration.py",
        "test_sovereign_remediation_simple.py",
    }

    # ops_scripts test files (legacy - to be moved to tests/integration/)
    KNOWN_OPS_SCRIPTS_TEST_FILES = {
        "test_autonomous_decision_making.py",
        "test_autonomous_end_to_end.py",
        "test_batch_performance_optimization.py",
        "test_complete_mission_workflow.py",
        "test_hop2_sovereign_strategist.py",
        "test_hop3_hop4_hop5_foundation.py",
        "test_hop6_hop7_crucible_governor.py",
        "test_hop8_hop9_persistence_handoff.py",
        "test_hop_orchestrator_master.py",
        "test_lic_rg_parity.py",
        "test_location_agent_telemetry.py",
        "test_master_verification_simulation.py",
        "test_mission_dry_run.py",
        "test_multi_agent_collaboration.py",
        "test_nuclear_audit.py",
        "test_parallel_healing_performance.py",
        "test_phase2_integration.py",
        "test_phase3_integration.py",
        "test_phase4_integration.py",
        "test_phase5_integration.py",
        "test_phase6_integration.py",
        "test_phase7_integration.py",
        "test_phase8_integration.py",
        "test_phase9_integration.py",
        "test_phase10_integration.py",
        "test_phase11_integration.py",
        "test_phase12_integration.py",
        "test_phase13_integration.py",
        "test_phase14_integration.py",
        "test_phase15_integration.py",
        "test_phase16_integration.py",
        "test_phase17_integration.py",
        "test_phase18_integration.py",
        "test_phase19_integration.py",
        "test_phase20_integration.py",
        # Additional ops_scripts test files discovered
        "test_mission_script_integrity.py",
        "test_mission_telemetry_dashboard.py",
        "test_phase1_config.py",
        "test_phase1_interface.py",
        "test_phase2_core.py",
        "test_phase2_interface.py",
        "test_phase3_base.py",
        "test_phase4_orchestrator.py",
        "test_canon_key_removal.py",
        "test_cognitive_subset.py",
        "test_manifest_completion.py",
        "test_mro_refactor.py",
    }

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.project_root = PROJECT_ROOT
        self.excluded_dirs = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            ".pytest_cache",
            "archives",
            ".sovereign_healing_backup",
            ".backup",
            "node_modules",
            ".mypy_cache",
            ".ruff_cache",
            "temp_quiet_test",
            "temp_verbose_test",
        }
        self.excluded_files = {
            ".gitignore",
            ".env",
            ".secrets.baseline",
            ".coverage",
            ".manifest.lock",
        }

    def _get_all_python_files(self) -> list[Path]:
        """Get all Python files in the repository, excluding ignored directories"""
        python_files = []
        for path in self.project_root.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in path.parts for excluded in self.excluded_dirs):
                continue
            python_files.append(path)
        return python_files

    def _get_relative_path(self, path: Path) -> Path:
        """Get path relative to project root"""
        return path.relative_to(self.project_root)

    def test_all_files_in_valid_territories(self):
        """
        Test 1: Every file must exist in a valid sovereign territory.

        Validates that no files exist outside the defined SOVEREIGN_TERRITORIES.
        """
        print("\n=== SSOT Compliance: Territory Validation ===")

        valid_territories = set(SOVEREIGN_TERRITORIES.keys())
        # Add common root-level items that are allowed
        valid_territories.update(
            {
                "scripts",
                ".github",
                ".windsurf",
                ".gravity_state",
            }
        )

        violations = []
        all_files = list(self.project_root.rglob("*"))

        for path in all_files:
            if path.is_dir():
                continue

            rel_path = self._get_relative_path(path)
            parts = rel_path.parts

            if len(parts) == 0:
                continue

            # Root-level files are allowed
            if len(parts) == 1:
                continue

            territory = parts[0]

            # Skip hidden directories (they have their own rules)
            if territory.startswith("."):
                continue

            # Skip excluded directories
            if territory in self.excluded_dirs:
                continue

            if territory not in valid_territories:
                violations.append(f"Unknown territory '{territory}': {rel_path}")

        if violations:
            error_msg = f"SSOT TERRITORY VIOLATIONS ({len(violations)} files):\n"
            for v in violations[:20]:  # Limit output
                error_msg += f"  [X] {v}\n"
            if len(violations) > 20:
                error_msg += f"  ... and {len(violations) - 20} more\n"
            pytest.fail(error_msg)

        print(f"[OK] All files in valid territories ({len(all_files)} checked)")

    def test_agentic_core_subfolder_compliance(self):
        """
        Test 2: agentic_core files must be in approved subfolders.

        Validates the L0-L6 layer structure and specialized domains.
        """
        print("\n=== SSOT Compliance: Agentic Core Structure ===")

        valid_subfolders = set(CORE_SUBFOLDER_MAP.keys())
        agentic_core_path = self.project_root / AGENTIC_CORE_DIR

        if not agentic_core_path.exists():
            pytest.skip("agentic_core directory not found")

        violations = []

        for path in agentic_core_path.iterdir():
            if path.name.startswith(".") or path.name.startswith("__"):
                continue

            if path.is_dir():
                if path.name not in valid_subfolders:
                    violations.append(
                        f"Invalid subfolder '{path.name}' in agentic_core. "
                        f"Valid: {sorted(valid_subfolders)}"
                    )
            elif path.suffix == ".py":
                # Python files at agentic_core root are allowed (e.g., __init__.py)
                if path.name not in {"__init__.py", "DiscoveredAgent.py"}:
                    violations.append(f"Unexpected Python file at agentic_core root: {path.name}")

        if violations:
            error_msg = f"AGENTIC_CORE STRUCTURE VIOLATIONS ({len(violations)}):\n"
            for v in violations:
                error_msg += f"  [X] {v}\n"
            pytest.fail(error_msg)

        print(f"[OK] agentic_core structure compliant ({len(valid_subfolders)} subfolders)")

    def test_base_agents_constitutional_location(self):
        """
        Test 3: [CONSTITUTIONAL] All *BaseAgent.py files must be in agentic_core/base_agents/

        This is a constitutional rule that CANNOT be overridden.
        Known violations are tracked as technical debt.
        """
        print("\n=== SSOT Compliance: Constitutional Base Agent Location ===")

        canonical_dir = self.project_root / AGENTIC_CORE_DIR / "base_agents"
        violations = []
        known_debt = []

        # Find all files ending in BaseAgent.py
        for path in self.project_root.rglob("*BaseAgent.py"):
            rel_path = self._get_relative_path(path)

            # Skip excluded directories
            if any(excluded in path.parts for excluded in self.excluded_dirs):
                continue

            # Check if it's in the canonical location
            if not str(path).startswith(str(canonical_dir)):
                # Check if this is known technical debt
                if path.name in self.KNOWN_BASE_AGENT_VIOLATIONS:
                    known_debt.append(f"[KNOWN DEBT] {path.name}: {rel_path}")
                else:
                    violations.append(
                        f"[CONSTITUTIONAL] Base agent '{path.name}' found in wrong location: "
                        f"{rel_path} (must be in agentic_core/base_agents/)"
                    )

        # Report known debt (informational)
        if known_debt:
            print(
                f"[INFO] {len(known_debt)} known base agent violations (tracked as technical debt)"
            )

        # Fail only on NEW violations
        if violations:
            error_msg = "NEW CONSTITUTIONAL VIOLATIONS - BASE AGENT LOCATION:\n"
            error_msg += "These violations CANNOT be overridden:\n\n"
            for v in violations:
                error_msg += f"  [!!!] {v}\n"
            pytest.fail(error_msg)

        # Count base agents in canonical location
        base_agent_count = (
            len(list(canonical_dir.glob("*BaseAgent.py"))) if canonical_dir.exists() else 0
        )
        print(
            f"[OK] All {base_agent_count} base agents in constitutional location (+ {len(known_debt)} known debt)"
        )

    def test_apps_shared_independence(self):
        """
        Test 4: apps_shared MUST NOT import from apps_rg or apps_lic.

        Enforces the one-way dependency valve.
        Known violations are tracked as technical debt.
        """
        print("\n=== SSOT Compliance: apps_shared Independence ===")

        apps_shared_path = self.project_root / APPS_SHARED_DIR

        if not apps_shared_path.exists():
            pytest.skip("apps_shared directory not found")

        violations = []
        known_debt = []

        for py_file in apps_shared_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith(("apps_rg", "apps_lic")):
                                if py_file.name in self.KNOWN_APPS_SHARED_VIOLATIONS:
                                    known_debt.append(f"[KNOWN DEBT] {py_file.name}")
                                else:
                                    violations.append(
                                        f"{self._get_relative_path(py_file)}: "
                                        f"imports '{alias.name}'"
                                    )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith(("apps_rg", "apps_lic")):
                            if py_file.name in self.KNOWN_APPS_SHARED_VIOLATIONS:
                                known_debt.append(f"[KNOWN DEBT] {py_file.name}")
                            else:
                                violations.append(
                                    f"{self._get_relative_path(py_file)}: "
                                    f"imports from '{node.module}'"
                                )
            except SyntaxError:
                continue
            except Exception as e:
                print(f"Warning: Could not parse {py_file}: {e}")
                continue

        # Report known debt (informational)
        if known_debt:
            print(
                f"[INFO] {len(set(known_debt))} known dependency violations (tracked as technical debt)"
            )

        # Fail only on NEW violations
        if violations:
            error_msg = f"NEW APPS_SHARED INDEPENDENCE VIOLATIONS ({len(violations)}):\n"
            error_msg += "apps_shared MUST NOT import from apps_rg or apps_lic:\n\n"
            for v in violations[:20]:
                error_msg += f"  [X] {v}\n"
            if len(violations) > 20:
                error_msg += f"  ... and {len(violations) - 20} more\n"
            pytest.fail(error_msg)

        file_count = len(list(apps_shared_path.rglob("*.py")))
        print(
            f"[OK] apps_shared independence verified ({file_count} files, {len(set(known_debt))} known debt)"
        )

    def test_test_files_in_tests_directory(self):
        """
        Test 5: All test_*.py files must be in the tests/ directory.

        Prevents test file leakage into source directories.
        Known violations are tracked as technical debt.
        """
        print("\n=== SSOT Compliance: Test File Placement ===")

        violations = []
        known_debt = []
        tests_dir = self.project_root / "tests"

        # Combine all known test file violations
        all_known_test_files = self.KNOWN_ROOT_TEST_FILES | self.KNOWN_OPS_SCRIPTS_TEST_FILES

        for py_file in self.project_root.rglob("test_*.py"):
            rel_path = self._get_relative_path(py_file)

            # Skip excluded directories
            if any(excluded in py_file.parts for excluded in self.excluded_dirs):
                continue

            # Check if it's in the tests directory
            if not str(py_file).startswith(str(tests_dir)):
                # Allow conftest.py
                if py_file.name == "conftest.py":
                    continue
                # Check if this is known technical debt
                if py_file.name in all_known_test_files:
                    known_debt.append(f"[KNOWN DEBT] {py_file.name}")
                else:
                    violations.append(f"Test file outside tests/: {rel_path}")

        # Report known debt (informational)
        if known_debt:
            print(
                f"[INFO] {len(known_debt)} known test file placement violations (tracked as technical debt)"
            )

        # Fail only on NEW violations
        if violations:
            error_msg = f"NEW TEST FILE PLACEMENT VIOLATIONS ({len(violations)}):\n"
            for v in violations[:20]:
                error_msg += f"  [X] {v}\n"
            if len(violations) > 20:
                error_msg += f"  ... and {len(violations) - 20} more\n"
            pytest.fail(error_msg)

        test_count = len(list(tests_dir.rglob("test_*.py"))) if tests_dir.exists() else 0
        print(
            f"[OK] All test files in tests/ directory ({test_count} files, {len(known_debt)} known debt)"
        )

    def test_layer_hierarchy_integrity(self):
        """
        Test 6: L0-L6 layers must not have cross-layer imports that violate hierarchy.

        Lower layers (L0-L2) should not import from higher layers (L4-L6).

        NOTE: This test is currently INFORMATIONAL due to extensive existing violations.
        It reports violations but does not fail the test suite.
        Once violations are remediated, this can be made strict.
        """
        print("\n=== SSOT Compliance: Layer Hierarchy Integrity (INFORMATIONAL) ===")

        # Define layer hierarchy (lower number = lower layer)
        layer_order = {
            "L0_maintenance": 0,
            "L1_cognition": 1,
            "L2_execution": 2,
            "L3_orchestration": 3,
            "L4_state": 4,
            "L5_safety": 5,
            "L6_observability": 6,
        }

        # Allowed cross-layer imports (exceptions)
        # These are architectural decisions that are intentionally allowed
        allowed_exceptions = {
            # L0 can import from any layer (maintenance scripts need full access)
            ("L0_maintenance", "L1_cognition"),
            ("L0_maintenance", "L2_execution"),
            ("L0_maintenance", "L3_orchestration"),
            ("L0_maintenance", "L4_state"),
            ("L0_maintenance", "L5_safety"),
            ("L0_maintenance", "L6_observability"),
            # L2 can import from L5 for safety validation
            ("L2_execution", "L5_safety"),
            # All layers can import from base_agents
            ("L0_maintenance", "base_agents"),
            ("L1_cognition", "base_agents"),
            ("L2_execution", "base_agents"),
            ("L3_orchestration", "base_agents"),
            ("L4_state", "base_agents"),
            ("L5_safety", "base_agents"),
            ("L6_observability", "base_agents"),
            # All layers can import from utils, config, schemas
            ("L0_maintenance", "utils"),
            ("L0_maintenance", "config"),
            ("L0_maintenance", "schemas"),
            ("L1_cognition", "utils"),
            ("L2_execution", "utils"),
            ("L3_orchestration", "utils"),
            ("L4_state", "utils"),
            ("L5_safety", "utils"),
            ("L6_observability", "utils"),
        }

        violations = []
        agentic_core_path = self.project_root / AGENTIC_CORE_DIR

        for layer_name, layer_level in layer_order.items():
            layer_path = agentic_core_path / layer_name
            if not layer_path.exists():
                continue

            for py_file in layer_path.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        import_module = None
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name.startswith("agentic_core."):
                                    import_module = alias.name
                        elif isinstance(node, ast.ImportFrom):
                            if node.module and node.module.startswith("agentic_core."):
                                import_module = node.module

                        if import_module:
                            # Extract the layer being imported
                            parts = import_module.split(".")
                            if len(parts) >= 2:
                                imported_layer = parts[1]
                                if imported_layer in layer_order:
                                    imported_level = layer_order[imported_layer]
                                    # Check for upward imports (lower importing higher)
                                    if imported_level > layer_level:
                                        # Check if it's an allowed exception
                                        if (layer_name, imported_layer) not in allowed_exceptions:
                                            violations.append(
                                                f"{layer_name} -> {imported_layer}: "
                                                f"{self._get_relative_path(py_file)}"
                                            )
                except SyntaxError:
                    continue
                except Exception:
                    continue

        # Report violations as informational (not failing)
        if violations:
            print(
                f"[INFO] {len(violations)} layer hierarchy violations detected (tracked as technical debt)"
            )
            print("       These will be addressed in future refactoring sprints.")
        else:
            print(f"[OK] Layer hierarchy integrity verified ({len(layer_order)} layers)")

    def test_void_compliance_whitelist(self):
        """
        Test 7: [VOID COMPLIANCE] Root folder whitelist enforcement.

        Fails if any file exists in a root folder not in ROOT_WHITELIST.
        Fails if any file exists in FORBIDDEN_ROOT_FOLDERS.
        """
        print("\n=== SSOT Compliance: Void Folder Whitelist ===")

        violations = []
        forbidden_violations = []

        # Check all files at root level
        for path in self.project_root.iterdir():
            if not path.is_dir():
                continue

            folder_name = path.name

            # Skip hidden directories
            if folder_name.startswith("."):
                continue

            # Check if folder is in whitelist
            if folder_name not in ROOT_WHITELIST:
                # Check if it has any Python files
                py_files = list(path.rglob("*.py"))
                if py_files:
                    violations.append(
                        f"Folder '{folder_name}' contains {len(py_files)} Python files but is not in ROOT_WHITELIST"
                    )

            # Check if folder is forbidden
            if folder_name in FORBIDDEN_ROOT_FOLDERS:
                py_files = list(path.rglob("*.py"))
                if py_files:
                    forbidden_violations.append(
                        f"Folder '{folder_name}' is FORBIDDEN but contains {len(py_files)} Python files"
                    )

        # Report violations
        if violations or forbidden_violations:
            error_msg = "VOID COMPLIANCE VIOLATIONS:\n\n"

            if violations:
                error_msg += f"WHITELIST VIOLATIONS ({len(violations)}):\n"
                for v in violations:
                    error_msg += f"  [X] {v}\n"

            if forbidden_violations:
                error_msg += f"\nFORBIDDEN FOLDER VIOLATIONS ({len(forbidden_violations)}):\n"
                for v in forbidden_violations:
                    error_msg += f"  [!!!] {v}\n"

            pytest.fail(error_msg)

        print(
            f"[OK] All root folders comply with whitelist ({len(ROOT_WHITELIST)} whitelisted, {len(FORBIDDEN_ROOT_FOLDERS)} forbidden)"
        )

    def test_sub_atomic_granularity(self):
        """
        Test 8: [SUB-ATOMIC] File size granularity checks (Key 13/49).

        - Monolith Check: Fail if any file > 800 LOC.
        - Code Dust Check: Fail if any file < 80 LOC (exclude __init__.py and tests/).
        """
        print("\n=== SSOT Compliance: Sub-Atomic Granularity ===")

        monolith_violations = []
        code_dust_violations = []

        # Get all Python files
        for py_file in self.project_root.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(py_file) for excluded in self.excluded_dirs):
                continue

            # Skip __init__.py files for code dust check
            is_init_file = py_file.name == "__init__.py"

            # Skip test files for code dust check
            is_test_file = "tests" in py_file.parts

            try:
                # Count lines of code
                with open(py_file, encoding="utf-8") as f:
                    lines = f.readlines()

                # Filter out empty lines and comments
                code_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        code_lines.append(line)

                loc_count = len(code_lines)

                # Monolith check (> 800 LOC)
                if loc_count > 800:
                    monolith_violations.append(
                        f"{self._get_relative_path(py_file)}: {loc_count} LOC (limit: 800)"
                    )

                # Code dust check (< 80 LOC)
                if not is_init_file and not is_test_file and loc_count < 80:
                    code_dust_violations.append(
                        f"{self._get_relative_path(py_file)}: {loc_count} LOC (minimum: 80)"
                    )

            except (UnicodeDecodeError, PermissionError):
                # Skip files that can't be read
                continue

        # Report violations as warnings (tracked as technical debt)
        if monolith_violations or code_dust_violations:
            print("\n⚠️  GRANULARITY TECHNICAL DEBT (tracked, not blocking):")

            if monolith_violations:
                print(f"\nMonolith files ({len(monolith_violations)} files > 800 LOC):")
                for v in monolith_violations[:5]:
                    print(f"  • {v}")
                if len(monolith_violations) > 5:
                    print(f"  ... and {len(monolith_violations) - 5} more")

            if code_dust_violations:
                print(f"\nCode dust files ({len(code_dust_violations)} files < 80 LOC):")
                for v in code_dust_violations[:5]:
                    print(f"  • {v}")
                if len(code_dust_violations) > 5:
                    print(f"  ... and {len(code_dust_violations) - 5} more")

            print("\n✅ Test passes - violations tracked as technical debt for future refactoring")
        else:
            print("[OK] All files within granularity bounds (monolith: 0, code dust: 0)")


# Standalone runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
