"""
SSOT Compliance Guardian (HARDENED)
====================================
Zero-Trust Guardian Layer for SSOT structural compliance.

MANIFESTO COMPLIANCE:
1. Static Stasis: AST-only analysis, NO code execution
2. Binary Output: PASS or BLOCK (pytest.fail), NO warnings
3. Machine-Readable: JSON violations via GuardianReportBuilder
4. Constitutional Lock: structure_blueprint.py enforcement exact
5. No Ghost Files: Any file outside SSOT is BLOCKED
6. No AI Checking AI: Deterministic Python only

This test suite ensures:
1. All files exist in SSOT-approved locations (BLOCK otherwise)
2. No files violate sovereign territory boundaries (BLOCK otherwise)
3. Base agents are in constitutional location (BLOCK otherwise)
4. Layer hierarchy is respected (BLOCK otherwise)

USAGE:
    pytest tests/guardian/test_ssot_compliance.py -v

EXPECTED RESULT:
    100% pass rate - any failure BLOCKS the pipeline
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
from agentic_core.L5_safety.validators.structure_blueprint_config import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
    CORE_SUBFOLDER_MAP,
    FORBIDDEN_ROOT_FOLDERS,
    ROOT_WHITELIST,
    SOVEREIGN_TERRITORIES,
)
from tests.guardian.guardian_report import (
    FixAction,
    GuardianReportBuilder,
    ViolationCode,
)

# =============================================================================
# CONSTANTS - NO EXCEPTIONS ALLOWED
# =============================================================================
MAX_LOC = 800  # Subatomic atomicity limit


class TestSSOTCompliance:
    """HARDENED Test suite for SSOT structural compliance.

    NO DEBT TRACKING. All violations are BLOCKING.
    Violations are reported to GuardianReportBuilder for JSON output.
    """

    @pytest.fixture(scope="class")
    def report_builder(self):
        """Get the singleton report builder for JSON output."""
        return GuardianReportBuilder.get_instance("guardian")

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

    def test_all_files_in_valid_territories(self, report_builder):
        """
        BLOCKING: Every file must exist in a valid sovereign territory.

        Validates that no files exist outside the defined SOVEREIGN_TERRITORIES.
        """

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
                violations.append({"territory": territory, "path": str(rel_path)})
                report_builder.add_violation(
                    code=ViolationCode.SSOT_TERRITORY,
                    file=str(rel_path),
                    line=1,
                    message=f"File in unknown territory '{territory}'",
                    fix_action=FixAction.MOVE_FILE,
                )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} files in unknown territories:\n"
                + "\n".join(f"  - {v['path']}" for v in violations[:20])
            )

    def test_agentic_core_subfolder_compliance(self, report_builder):
        """
        BLOCKING: agentic_core files must be in approved subfolders.

        Validates the L0-L6 layer structure and specialized domains.
        """
        valid_subfolders = set(CORE_SUBFOLDER_MAP.keys())
        agentic_core_path = self.project_root / AGENTIC_CORE_DIR

        if not agentic_core_path.exists():
            pytest.fail("BLOCKING: agentic_core directory not found")

        violations = []

        for path in agentic_core_path.iterdir():
            if path.name.startswith(".") or path.name.startswith("__"):
                continue

            if path.is_dir():
                if path.name not in valid_subfolders:
                    violations.append(
                        f"Invalid subfolder '{path.name}' in agentic_core. Valid: {sorted(valid_subfolders)}"
                    )
            elif path.suffix == ".py":
                # Python files at agentic_core root are allowed (e.g., __init__.py)
                if path.name not in {"__init__.py"}:
                    violations.append({"file": path.name, "type": "root_file"})
                    report_builder.add_violation(
                        code=ViolationCode.SSOT_GHOST_FILE,
                        file=str(path),
                        line=1,
                        message=f"Unexpected Python file at agentic_core root: {path.name}",
                        fix_action=FixAction.MOVE_FILE,
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} agentic_core structure violations:\n"
                + "\n".join(f"  - {v}" for v in violations[:10])
            )

    def test_base_agents_constitutional_location(self, report_builder):
        """
        BLOCKING [CONSTITUTIONAL]: All *BaseAgent.py files must be in agentic_core/base_agents/

        This is a constitutional rule that CANNOT be overridden. NO EXCEPTIONS.
        """
        canonical_dir = self.project_root / AGENTIC_CORE_DIR / "base_agents"
        violations = []

        # Find all files ending in BaseAgent.py
        for path in self.project_root.rglob("*BaseAgent.py"):
            rel_path = self._get_relative_path(path)

            # Skip excluded directories
            if any(excluded in path.parts for excluded in self.excluded_dirs):
                continue

            # Check if it's in the canonical location
            if not str(path).startswith(str(canonical_dir)):
                violations.append({"file": path.name, "path": str(rel_path)})
                report_builder.add_violation(
                    code=ViolationCode.CONSTITUTIONAL_BASE_AGENT,
                    file=str(rel_path),
                    line=1,
                    message=f"Base agent '{path.name}' found in wrong location (must be in agentic_core/base_agents/)",
                    fix_action=FixAction.MOVE_FILE,
                )

        if violations:
            pytest.fail(
                f"BLOCKING [CONSTITUTIONAL]: {len(violations)} base agents in wrong location:\n"
                + "\n".join(f"  - {v['path']}" for v in violations[:10])
            )

    def test_apps_shared_independence(self, report_builder):
        """
        BLOCKING: apps_shared MUST NOT import from apps_rg or apps_lic.

        Enforces the one-way dependency valve. NO EXCEPTIONS.
        """
        apps_shared_path = self.project_root / APPS_SHARED_DIR

        if not apps_shared_path.exists():
            pytest.fail("BLOCKING: apps_shared directory not found")

        violations = []

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
                                violations.append(
                                    {
                                        "file": str(self._get_relative_path(py_file)),
                                        "import": alias.name,
                                        "line": node.lineno,
                                    }
                                )
                                report_builder.add_violation(
                                    code=ViolationCode.SSOT_INDEPENDENCE,
                                    file=str(py_file),
                                    line=node.lineno,
                                    message=f"apps_shared imports '{alias.name}'",
                                    fix_action=FixAction.REMOVE_IMPORT,
                                )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith(("apps_rg", "apps_lic")):
                            violations.append(
                                {
                                    "file": str(self._get_relative_path(py_file)),
                                    "import": node.module,
                                    "line": node.lineno,
                                }
                            )
                            report_builder.add_violation(
                                code=ViolationCode.SSOT_INDEPENDENCE,
                                file=str(py_file),
                                line=node.lineno,
                                message=f"apps_shared imports from '{node.module}'",
                                fix_action=FixAction.REMOVE_IMPORT,
                            )
            except SyntaxError:
                continue
            except Exception:
                continue

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} apps_shared independence violations:\n"
                + "\n".join(f"  - {v['file']}:{v['line']} imports {v['import']}" for v in violations[:20])
            )

    def test_test_files_in_tests_directory(self, report_builder):
        """
        BLOCKING: All test_*.py files must be in the tests/ directory.

        Prevents test file leakage into source directories. NO EXCEPTIONS.
        """
        violations = []
        tests_dir = self.project_root / "tests"

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
                violations.append({"file": py_file.name, "path": str(rel_path)})
                report_builder.add_violation(
                    code=ViolationCode.SSOT_TEST_PLACEMENT,
                    file=str(rel_path),
                    line=1,
                    message=f"Test file '{py_file.name}' outside tests/ directory",
                    fix_action=FixAction.MOVE_FILE,
                )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} test files outside tests/ directory:\n"
                + "\n".join(f"  - {v['path']}" for v in violations[:20])
            )

    def test_layer_hierarchy_integrity(self, report_builder):
        """
        BLOCKING: L0-L6 layers must not have cross-layer imports that violate hierarchy.

        Lower layers (L0-L2) should not import from higher layers (L4-L6).
        NO EXCEPTIONS beyond the allowed_exceptions set.
        """

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
                                                {
                                                    "from_layer": layer_name,
                                                    "to_layer": imported_layer,
                                                    "file": str(self._get_relative_path(py_file)),
                                                    "line": node.lineno if hasattr(node, "lineno") else 1,
                                                }
                                            )
                                            report_builder.add_violation(
                                                code=ViolationCode.SSOT_LAYER_HIERARCHY,
                                                file=str(py_file),
                                                line=node.lineno if hasattr(node, "lineno") else 1,
                                                message=f"Layer {layer_name} imports from higher layer {imported_layer}",
                                                fix_action=FixAction.REMOVE_IMPORT,
                                            )
                except SyntaxError:
                    continue
                except Exception:
                    continue

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} layer hierarchy violations:\n"
                + "\n".join(f"  - {v['from_layer']} -> {v['to_layer']}: {v['file']}" for v in violations[:20])
            )

    def test_void_compliance_whitelist(self, report_builder):
        """
        BLOCKING [VOID COMPLIANCE]: Root folder whitelist enforcement.

        Fails if any file exists in a root folder not in ROOT_WHITELIST.
        Fails if any file exists in FORBIDDEN_ROOT_FOLDERS.
        """
        violations = []

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
                py_files = list(path.rglob("*.py"))
                if py_files:
                    violations.append({"folder": folder_name, "count": len(py_files), "type": "whitelist"})
                    report_builder.add_violation(
                        code=ViolationCode.SSOT_VOID_COMPLIANCE,
                        file=folder_name,
                        line=1,
                        message=f"Folder '{folder_name}' contains {len(py_files)} Python files but is not in ROOT_WHITELIST",
                        fix_action=FixAction.DELETE,
                    )

            # Check if folder is forbidden
            if folder_name in FORBIDDEN_ROOT_FOLDERS:
                py_files = list(path.rglob("*.py"))
                if py_files:
                    violations.append({"folder": folder_name, "count": len(py_files), "type": "forbidden"})
                    report_builder.add_violation(
                        code=ViolationCode.SSOT_VOID_COMPLIANCE,
                        file=folder_name,
                        line=1,
                        message=f"FORBIDDEN folder '{folder_name}' contains {len(py_files)} Python files",
                        fix_action=FixAction.DELETE,
                    )

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} void compliance violations:\n"
                + "\n".join(f"  - {v['folder']}: {v['count']} files ({v['type']})" for v in violations)
            )

    def test_sub_atomic_granularity(self, report_builder):
        """
        BLOCKING [SUB-ATOMIC]: File size granularity checks.

        - Monolith Check: BLOCK if any file > 800 LOC.

        Note: Code dust check (< 80 LOC) is NOT enforced as blocking.
        """
        violations = []

        # Get all Python files
        for py_file in self.project_root.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(py_file) for excluded in self.excluded_dirs):
                continue

            try:
                # Count lines of code
                with open(py_file, encoding="utf-8") as f:
                    lines = f.readlines()

                # Filter out empty lines and comments
                code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
                loc_count = len(code_lines)

                # Monolith check (> 800 LOC) - BLOCKING
                if loc_count > MAX_LOC:
                    rel_path = self._get_relative_path(py_file)
                    violations.append(
                        {
                            "file": str(rel_path),
                            "loc": loc_count,
                            "limit": MAX_LOC,
                        }
                    )
                    report_builder.add_violation(
                        code=ViolationCode.SUBATOMIC_MONOLITH,
                        file=str(rel_path),
                        line=1,
                        message=f"File has {loc_count} LOC (max: {MAX_LOC})",
                        fix_action=FixAction.SPLIT_FILE,
                        context={"loc": loc_count, "limit": MAX_LOC},
                    )

            except (UnicodeDecodeError, PermissionError):
                continue

        if violations:
            pytest.fail(
                f"BLOCKING: {len(violations)} monolith files exceed {MAX_LOC} LOC:\n"
                + "\n".join(f"  - {v['file']}: {v['loc']} LOC" for v in violations[:10])
            )


# Standalone runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
