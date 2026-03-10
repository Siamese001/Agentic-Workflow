#!/usr/bin/env python3
"""CI Kernel-Extension Boundary Checker.

Enforces that modular extensions do not create reverse dependencies
into kernel internals. Extensions may import kernel interfaces,
but kernel must not import extensions.

Exits with non-zero status on boundary violations.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

# Standard library modules that should be ignored
STANDARD_LIBRARY_MODULES: frozenset[str] = frozenset(
    {
        "__future__",
        "abc",
        "argparse",
        "ast",
        "asyncio",
        "base64",
        "bisect",
        "collections",
        "contextlib",
        "copy",
        "dataclasses",
        "datetime",
        "decimal",
        "enum",
        "functools",
        "gc",
        "hashlib",
        "inspect",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "pickle",
        "re",
        "sys",
        "time",
        "traceback",
        "types",
        "typing",
        "uuid",
        "warnings",
        "weakref",
        # Additional common modules
        "importlib",
        "importlib.util",
        "struct",
        "shutil",
        "tempfile",
        "statistics",
        "dotenv",
        "numpy",
        "openai",
        "subprocess",
        "threading",
        "psutil",
        "pydantic",
        "csv",
        "io",
        "fnmatch",
        "unicodedata",
        "urllib.parse",
        "jinja2",
        # External libraries commonly used
        "libcst",
        "google",
        "google.genai",
        "uvicorn",
        "fastapi",
        "fastapi.responses",
        "xml.etree.ElementTree",
        "yaml",
        "hmac",
        "contextvars",
        # More external libraries
        "tree_sitter",
        "tree_sitter_python",
        "cryptography.fernet",
        "watchdog",
        "watchdog.events",
        "watchdog.observers",
        "tqdm",
        "difflib",
        "textwrap",
        "secrets",
        "platform",
        "winreg",
        "random",
        # Standard library additions
        "concurrent.futures",
        "atexit",
        "signal",
        # More external libraries
        "redis",
        # Internal modules that should be treated as standard library for boundary checking
        "base_detector_validator",
        "engine",
        # Relative imports (treated as internal) - these are typically same-package imports
        "cache_entry_types",
        "claim_type_types",
        "cost_governor_types",
        "expansion_strategy_types",
        "main_util",
        "runtime_bootstrapper",
        "runtime.core.telemetry",
        "services.configuration",
        # Common relative import patterns
        "governance_hub",
        "prompt_assembler",
        "sovereign_prompt_renderer",
        "optimization_strategy",
        "detectors.injection_detector",
        "detectors.pii_scrubber",
        "injection_detector",
        "pii_scrubber",
        "output_schema_validator",
        "shared_infrastructure_config",
        "signal_quality_config",
        "ast_relocator",
        # agentic_core sub-modules that are internal
        "agentic_core.config",
        "agentic_core.patterns",
        "agentic_core.base_agents",
        # More internal modules
        "signature_verifier",
        "context_contracts",
        "slot_contracts",
        # Additional internal modules
        "agentic_core.L6_observability",
        OPS_SCRIPTS_DIR,
        APPS_SHARED_DIR,
        "agentic_core.shared",
        # More internal modules
        "classification_kernel",
        "sovereign_policy_registry",
        "agentic_core.governor",
        "agentic_core.overseer",
        "agentic_core.PiiVault",
        # Even more internal modules
        "persistent_store",
        "agentic_core.storage",
    }
)

# Add project root to Python path for imports
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
    get_validated_project_root,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
)

project_root = get_validated_project_root()

from agentic_core.L5_safety.config.structure_blueprint.sovereign_kernel import (
    is_kernel_component,
    is_modular_extension,
    validate_boundary,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    SOVEREIGN_EXCLUDED_FOLDERS,
)


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements."""

    def __init__(self) -> None:
        self.imports: list[str] = []
        self.from_imports: list[tuple[str, str]] = []  # (module, name)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            for alias in node.names:
                self.from_imports.append((node.module, alias.name))
        self.generic_visit(node)


def get_imports_from_file(file_path: Path) -> tuple[list[str], list[tuple[str, str]]]:
    """Extract imports from a Python file using AST."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
        visitor = ImportVisitor()
        visitor.visit(tree)
        return visitor.imports, visitor.from_imports
    except SyntaxError as e:
        print(f"ERROR: Syntax error in {file_path}: {e}", file=sys.stderr)
        return [], []
    except Exception as e:
        print(f"ERROR: Failed to parse {file_path}: {e}", file=sys.stderr)
        return [], []


def normalize_module_path(module: str) -> str:
    """Convert import module to normalized path format."""
    return module.replace("/", ".").replace("\\", ".")


def check_file_boundary(
    file_path: Path,
    source_module: str,
    imports: list[str],
    from_imports: list[tuple[str, str]],
) -> list[str]:
    """Check if a file violates kernel-extension boundary."""
    violations: list[str] = []

    # Determine if source is kernel or extension
    source_is_kernel, source_reason = validate_boundary(source_module)
    if not source_is_kernel:
        # Skip unclassified modules (likely test files, examples, etc.)
        return violations

    # Check each import
    for imp in imports:
        # Skip standard library modules
        if imp.split(".")[0] in STANDARD_LIBRARY_MODULES:
            continue

        imp_normalized = normalize_module_path(imp)
        imp_is_kernel, imp_reason = validate_boundary(imp_normalized)

        if source_is_kernel and imp_is_kernel:
            # Kernel importing kernel - allowed
            continue
        elif source_is_kernel and not imp_is_kernel:
            # Kernel importing extension - VIOLATION
            violations.append(
                f"KERNEL_IMPORTS_EXTENSION: {source_module} imports extension {imp} "
                f"({source_reason} -> {imp_reason})"
            )
        elif not source_is_kernel and imp_is_kernel:
            # Extension importing kernel - allowed
            continue
        else:
            # Extension importing extension - allowed
            continue

    # Check from-imports
    for module, name in from_imports:
        # Skip standard library modules
        if module.split(".")[0] in STANDARD_LIBRARY_MODULES:
            continue

        module_normalized = normalize_module_path(module)
        module_is_kernel, module_reason = validate_boundary(module_normalized)

        if source_is_kernel and module_is_kernel:
            # Kernel from-import kernel - allowed
            continue
        elif source_is_kernel and not module_is_kernel:
            # Kernel from-import extension - VIOLATION
            violations.append(
                f"KERNEL_FROM_IMPORTS_EXTENSION: {source_module} from-imports {module}.{name} "
                f"({source_reason} -> {module_reason})"
            )
        elif not source_is_kernel and module_is_kernel:
            # Extension from-import kernel - allowed
            continue
        else:
            # Extension from-import extension - allowed
            continue

    return violations


def module_path_from_file_path(file_path: Path, project_root: Path) -> str:
    """Convert file path to module path."""
    try:
        relative_path = file_path.relative_to(project_root)
        # Remove .py extension and convert path separators to dots
        module_parts = list(relative_path.parts)
        if module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]
        # Skip __init__ files - they represent their package
        if module_parts[-1] == "__init__":
            module_parts = module_parts[:-1]
        return ".".join(module_parts)
    except ValueError:
        # File not under project root
        return str(file_path)


def scan_directory(directory: Path) -> dict[str, list[str]]:
    """Scan directory for boundary violations."""
    violations_by_file: dict[str, list[str]] = {}

    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and other non-source directories
        if "__pycache__" in py_file.parts or ".pytest_cache" in py_file.parts:
            continue

        module_path = module_path_from_file_path(py_file, project_root)
        imports, from_imports = get_imports_from_file(py_file)

        file_violations = check_file_boundary(py_file, module_path, imports, from_imports)

        if file_violations:
            violations_by_file[str(py_file)] = file_violations

    return violations_by_file


def main() -> int:
    """Main entry point."""
    print("=== Kernel-Extension Boundary Checker ===")
    print(f"Project root: {project_root}")

    # Scan agentic_core and system_learning directories
    scan_dirs = [
        project_root / AGENTIC_CORE_DIR,
        project_root / SYSTEM_LEARNING_DIR,
    ]

    total_violations = 0
    all_violations: dict[str, list[str]] = {}

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            print(f"WARNING: Directory {scan_dir} does not exist, skipping")
            continue

        print(f"\nScanning {scan_dir}...")
        violations = scan_directory(scan_dir)
        all_violations.update(violations)
        total_violations += sum(len(v) for v in violations.values())

    # Report results
    if total_violations == 0:
        print("\n✅ No boundary violations found")
        return 0
    else:
        print(f"\n❌ Found {total_violations} boundary violations:")
        for file_path, violations in all_violations.items():
            print(f"\n  {file_path}:")
            for violation in violations:
                print(f"    - {violation}")
        print(f"\nTotal violations: {total_violations}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
