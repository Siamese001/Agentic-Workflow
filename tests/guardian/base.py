#!/usr/bin/env python3
"""
Guardian Test Base Classes and Utilities
Provides shared functionality to reduce duplication across Guardian tests.
"""

import ast
import sys
import tempfile
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    # guardian: allow-global-mutation
    sys.path.insert(0, str(PROJECT_ROOT))

LAYER_HIERARCHY = {
    "L0_routing": 0,
    "L1_cognition": 1,
    "L2_execution": 2,
    "L3_orchestration": 3,
    "L4_state": 4,
    "L5_safety": 5,
    "L6_observability": 6,
}


class GuardianTestBase:
    """Base class for all Guardian tests."""

    @staticmethod
    def get_project_root() -> Path:
        """Get project root path."""
        return PROJECT_ROOT

    @staticmethod
    def scan_agents(pattern: str = "**/*Agent.py") -> list[Path]:
        """Scan for agent files matching pattern."""
        return list(PROJECT_ROOT.glob(pattern))

    @staticmethod
    def check_layer_hierarchy(file_path: Path) -> dict[str, Any]:
        """Check layer hierarchy compliance."""
        parts = file_path.parts
        current_layer = None
        current_level = -1

        for part in parts:
            if part in LAYER_HIERARCHY:
                current_layer = part
                current_level = LAYER_HIERARCHY[part]
                break

        return {
            "layer": current_layer,
            "level": current_level,
            "hierarchy": LAYER_HIERARCHY,
        }

    @staticmethod
    def parse_ast(file_path: Path) -> ast.Module | None:
        """Parse file to AST with error handling."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return ast.parse(content)
        except (OSError, UnicodeDecodeError, SyntaxError):    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
            return None

    @staticmethod
    def find_agent_classes(tree: ast.Module) -> list[ast.ClassDef]:
        """Find all agent classes in AST."""
        return [
            node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
        ]

    @staticmethod
    def get_class_methods(class_node: ast.ClassDef) -> list[str]:
        """Get all method names from a class."""
        return [
            node.name for node in class_node.body if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        ]

    @staticmethod
    def get_imports(tree: ast.Module) -> list[str]:
        """Get all import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports


class AgentTestMixin:
    """Mixin for agent-specific test utilities."""

    def create_temp_file(self, code: str, suffix: str = ".py") -> Path:
        """Create temporary file with given code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(code)
            f.flush()
            return Path(f.name)

    def cleanup_temp_file(self, temp_path: Path) -> None:
        """Clean up temporary file with retry for Windows."""
        import time

        for _ in range(3):
            try:
                temp_path.unlink(missing_ok=True)
                break
            except PermissionError:    # guardian: Permission errors should validate access before operation    # guardian: Permission errors should validate access before operation    # guardian: Permission errors should validate access before operation    # guardian: Permission errors should validate access before operation    # guardian: Permission errors should validate access before operation
                time.sleep(DEFAULT_SLEEP)

    def assert_agent_compliance(self, agent_file: Path, required_methods: list[str]) -> None:
        """Assert agent has required methods."""
        tree = GuardianTestBase.parse_ast(agent_file)
        assert tree is not None, f"Could not parse {agent_file}"

        agent_classes = GuardianTestBase.find_agent_classes(tree)
        assert agent_classes, f"No agent classes found in {agent_file}"

        agent_class = agent_classes[0]
        methods = GuardianTestBase.get_class_methods(agent_class)

        for method in required_methods:
            assert method in methods, f"Missing required method: {method}"

    def assert_no_gravity_violations(self, agent_file: Path) -> None:
        """Assert agent has no gravity violations."""
        tree = GuardianTestBase.parse_ast(agent_file)
        assert tree is not None, f"Could not parse {agent_file}"

        layer_info = GuardianTestBase.check_layer_hierarchy(agent_file)
        current_level = layer_info["level"]

        if current_level == -1:
            return

        imports = GuardianTestBase.get_imports(tree)

        for imp in imports:
            parts = imp.split(".")
            if len(parts) >= 2 and parts[0] == AGENTIC_CORE_DIR:
                imported_layer = parts[1]
                if imported_layer in LAYER_HIERARCHY:
                    imported_level = LAYER_HIERARCHY[imported_layer]
                    assert current_level >= imported_level, (
                        f"Gravity violation: {layer_info['layer']} importing from {imported_layer}"
                    )


class ValidationResult:
    """Standard validation result container."""

    def __init__(self):
        self.compliant = True
        self.violations = []
        self.warnings = []
        self.error = None

    def add_violation(self, message: str) -> None:
        """Add a violation."""
        self.violations.append(message)
        self.compliant = False

    def add_warning(self, message: str) -> None:
        """Add a warning (doesn't affect compliance)."""
        self.warnings.append(message)

    def set_error(self, message: str) -> None:
        """Set an error."""
        self.error = message
        self.compliant = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "compliant": self.compliant,
            "violations": self.violations,
            "warnings": self.warnings,
            "error": self.error,
        }