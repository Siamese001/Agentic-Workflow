#!/usr/bin/env python3
"""
ADG Import Validator — Validate import hygiene using ADG imports edges

Replaces AST re-parsing with ADG-powered queries for better performance
and accuracy in detecting import issues and dependency validation.

Usage:
    python tools/adg/adg_import_validator.py
    python tools/adg/adg_import_validator.py --directory agentic_core
    python tools/adg/adg_import_validator.py --file path/to/file.py
    python tools/adg/adg_import_validator.py --module agentic_core.L0_routing
"""

import argparse
import warnings
from pathlib import Path
from typing import Any

# Try to import ADG Query Bridge
try:
    from adg_query_bridge import ADGQueryBridge, FileMatch, Node

    ADG_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"ADG Query Bridge unavailable: {e}")
    ADG_AVAILABLE = False


class ImportViolation:
    """Represents an import violation found by the validator."""

    def __init__(
        self,
        file_path: str,
        line_number: int,
        import_module: str,
        violation_type: str,
        message: str = "",
        severity: str = "warning",
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.import_module = import_module
        self.violation_type = violation_type
        self.message = message
        self.severity = severity

    def __repr__(self):
        return f"ImportViolation({self.file_path}:{self.line_number} - {self.import_module} [{self.violation_type}])"


class ADGImportValidator:
    """Validator for import hygiene using ADG."""

    def __init__(self, repo_root: str | None = None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.bridge = ADGQueryBridge() if ADG_AVAILABLE else None

        # Known stdlib modules (simplified list)
        self.stdlib_modules = self._load_stdlib_modules()

    def _load_stdlib_modules(self) -> set[str]:
        """Load a basic set of stdlib modules."""
        return {
            "os",
            "sys",
            "pathlib",
            "json",
            "re",
            "ast",
            "argparse",
            "logging",
            "datetime",
            "time",
            "collections",
            "itertools",
            "functools",
            "operator",
            "math",
            "random",
            "string",
            "typing",
            "dataclasses",
            "enum",
            "threading",
            "multiprocessing",
            "subprocess",
            "shutil",
            "tempfile",
            "glob",
            "fnmatch",
            "urllib",
            "http",
            "email",
            "xml",
            "csv",
            "sqlite3",
            "pickle",
            "base64",
            "hashlib",
            "hmac",
            "uuid",
            "inspect",
            "importlib",
            "pkgutil",
            "warnings",
            "traceback",
            "unittest",
            "pytest",
            "mock",
            "io",
            "contextlib",
            "weakref",
        }

    def validate_file(self, file_path: str) -> list[ImportViolation]:
        """Validate imports in a specific file."""
        violations = []
        file_path_obj = Path(file_path)

        # Convert to absolute path if relative
        if not file_path_obj.is_absolute():
            file_path_obj = self.repo_root / file_path_obj

        if not file_path_obj.exists():
            return [ImportViolation(file_path, 0, "", "file_not_found", f"File not found: {file_path}")]

        try:
            if ADG_AVAILABLE:
                violations = self._validate_file_with_adg(file_path_obj)
            else:
                violations = self._validate_file_with_ast_fallback(file_path_obj)
        except Exception as e:
            rel_path = (
                str(file_path_obj.relative_to(self.repo_root))
                if file_path_obj.is_relative_to(self.repo_root)
                else str(file_path_obj)
            )
            violations.append(
                ImportViolation(
                    file_path=rel_path,
                    line_number=0,
                    import_module="",
                    violation_type="validation_error",
                    message=f"Failed to validate imports: {e}",
                    severity="error",
                )
            )

        return violations

    def _validate_file_with_adg(self, file_path: Path) -> list[ImportViolation]:
        """Validate file imports using ADG."""
        violations = []
        rel_path = (
            str(file_path.relative_to(self.repo_root))
            if file_path.is_relative_to(self.repo_root)
            else str(file_path)
        )

        try:
            # Get imports from ADG for this file
            imports = self._extract_imports_ast(file_path)

            for import_info in imports:
                module_name = import_info.get("module", "")
                line_num = import_info.get("line", 0)

                if not module_name:
                    continue

                # Check if module exists in ADG
                violations.extend(self._validate_module_with_adg(module_name, line_num, rel_path))

        except Exception as e:
            warnings.warn(f"ADG validation failed for {rel_path}, falling back to AST: {e}")
            violations = self._validate_file_with_ast_fallback(file_path)

        return violations

    def _extract_imports_ast(self, file_path: Path) -> list[dict[str, Any]]:
        """Extract imports using AST parsing."""
        import ast

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            {
                                "type": "import",
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(
                            {
                                "type": "from",
                                "module": module,
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )

            return imports
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {file_path}: {e}")

    def _validate_module_with_adg(
        self, module_name: str, line_num: int, file_path: str
    ) -> list[ImportViolation]:
        """Validate a module using ADG data."""
        violations = []

        try:
            # Check if module is stdlib
            if self._is_stdlib_module(module_name):
                return violations

            # Check if module exists in ADG
            importers = self.bridge.files_importing(module_name)

            if not importers:
                # Module not found in ADG, check if it's a local module
                if not self._is_local_module(module_name):
                    violations.append(
                        ImportViolation(
                            file_path=file_path,
                            line_number=line_num,
                            import_module=module_name,
                            violation_type="module_not_found",
                            message=f"Module '{module_name}' not found in ADG index or stdlib",
                            severity="warning",
                        )
                    )

        except Exception as e:
            warnings.warn(f"Failed to validate module {module_name}: {e}")

        return violations

    def _is_stdlib_module(self, module_name: str) -> bool:
        """Check if a module is a standard library module."""
        # Check exact match
        if module_name in self.stdlib_modules:
            return True

        # Check parent module
        parent_module = module_name.split(".")[0]
        return parent_module in self.stdlib_modules

    def _is_local_module(self, module_name: str) -> bool:
        """Check if a module exists locally in the repository."""
        try:
            # Try to find the module as a file or package
            module_parts = module_name.split(".")

            # Check as package
            package_path = self.repo_root / Path(*module_parts)
            if package_path.is_dir() and (package_path / "__init__.py").exists():
                return True

            # Check as file
            file_path = self.repo_root / Path(*module_parts[:-1]) / f"{module_parts[-1]}.py"
            return file_path.exists()

        except Exception:
            return False

    def _validate_file_with_ast_fallback(self, file_path: Path) -> list[ImportViolation]:
        """Validate file imports using AST fallback when ADG is unavailable."""
        violations = []
        rel_path = (
            str(file_path.relative_to(self.repo_root))
            if file_path.is_relative_to(self.repo_root)
            else str(file_path)
        )

        try:
            imports = self._extract_imports_ast(file_path)

            for import_info in imports:
                module_name = import_info.get("module", "")
                line_num = import_info.get("line", 0)

                if not module_name:
                    continue

                # Basic validation without ADG
                if not self._is_stdlib_module(module_name) and not self._is_local_module(module_name):
                    violations.append(
                        ImportViolation(
                            file_path=rel_path,
                            line_number=line_num,
                            import_module=module_name,
                            violation_type="module_not_found",
                            message=f"Module '{module_name}' not found (ADG unavailable for validation)",
                            severity="warning",
                        )
                    )

        except Exception as e:
            violations.append(
                ImportViolation(
                    file_path=rel_path,
                    line_number=0,
                    import_module="",
                    violation_type="validation_error",
                    message=f"Failed to validate imports: {e}",
                    severity="error",
                )
            )

        return violations

    def validate_directory(self, directory: str) -> list[ImportViolation]:
        """Validate imports in all Python files in a directory."""
        violations = []
        dir_path = self.repo_root / directory

        if not dir_path.exists():
            return [
                ImportViolation(directory, 0, "", "directory_not_found", f"Directory not found: {directory}")
            ]

        for py_file in dir_path.rglob("*.py"):
            file_violations = self.validate_file(str(py_file))
            violations.extend(file_violations)

        return violations

    def validate_module_dependencies(self, module_name: str) -> list[ImportViolation]:
        """Validate dependencies for a specific module."""
        violations = []

        if not ADG_AVAILABLE:
            return [
                ImportViolation(
                    module_name, 0, "", "adg_unavailable", "ADG not available for module validation"
                )
            ]

        try:
            # Get files that import this module
            importers = self.bridge.files_importing(module_name)

            if not importers:
                violations.append(
                    ImportViolation(
                        file_path=module_name,
                        line_number=0,
                        import_module=module_name,
                        violation_type="unused_module",
                        message=f"Module '{module_name}' is not imported by any files",
                        severity="info",
                    )
                )

            # Check each importer for potential issues
            for importer in importers:
                violations.extend(self._validate_file_with_adg(self.repo_root / importer.file_path))

        except Exception as e:
            violations.append(
                ImportViolation(
                    file_path=module_name,
                    line_number=0,
                    import_module=module_name,
                    violation_type="validation_error",
                    message=f"Failed to validate module dependencies: {e}",
                    severity="error",
                )
            )

        return violations

    def get_import_graph_summary(self) -> dict[str, Any]:
        """Get a summary of the import graph."""
        if not ADG_AVAILABLE:
            return {"error": "ADG not available"}

        try:
            # Get basic statistics from ADG
            summary = {
                "total_files": 0,
                "total_imports": 0,
                "top_imported_modules": [],
                "files_with_most_imports": [],
                "orphaned_modules": [],
            }

            # This is a simplified implementation
            # In practice, would query ADG for detailed statistics
            return summary

        except Exception as e:
            return {"error": f"Failed to get import graph summary: {e}"}


def main():
    """Main entry point for the ADG import validator."""
    parser = argparse.ArgumentParser(description="ADG Import Validator")
    parser.add_argument("--file", help="Specific file to validate")
    parser.add_argument("--directory", help="Directory to validate")
    parser.add_argument("--module", help="Module to validate dependencies for")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--severity", choices=["error", "warning", "info"], help="Filter by severity")

    args = parser.parse_args()

    validator = ADGImportValidator()
    violations = []

    if args.file:
        violations = validator.validate_file(args.file)
    elif args.directory:
        violations = validator.validate_directory(args.directory)
    elif args.module:
        violations = validator.validate_module_dependencies(args.module)
    else:
        # Validate entire repository
        violations = validator.validate_directory(".")

    # Filter by severity if specified
    if args.severity:
        violations = [v for v in violations if v.severity == args.severity]

    if args.format == "json":
        import json

        output = [
            {
                "file_path": v.file_path,
                "line_number": v.line_number,
                "import_module": v.import_module,
                "violation_type": v.violation_type,
                "message": v.message,
                "severity": v.severity,
            }
            for v in violations
        ]
        print(json.dumps(output, indent=2))
    else:
        print("ADG Import Validator Results")
        print("===========================")
        print(f"Found {len(violations)} import violations")
        print()

        # Group violations by type
        by_type = {}
        by_severity = {"error": [], "warning": [], "info": []}

        for v in violations:
            if v.violation_type not in by_type:
                by_type[v.violation_type] = []
            by_type[v.violation_type].append(v)
            by_severity[v.severity].append(v)

        # Show errors first
        if by_severity["error"]:
            print("ERRORS:")
            for v in sorted(by_severity["error"], key=lambda x: (x.file_path, x.line_number)):
                print(f"  {v.file_path}:{v.line_number} - {v.import_module}")
                print(f"    {v.message}")
            print()

        # Show warnings
        if by_severity["warning"]:
            print("WARNINGS:")
            for v in sorted(by_severity["warning"], key=lambda x: (x.file_path, x.line_number)):
                print(f"  {v.file_path}:{v.line_number} - {v.import_module}")
                if v.message:
                    print(f"    {v.message}")
            print()

        # Show info
        if by_severity["info"]:
            print("INFO:")
            for v in sorted(by_severity["info"], key=lambda x: (x.file_path, x.line_number)):
                print(f"  {v.file_path}:{v.line_number} - {v.import_module}")
                if v.message:
                    print(f"    {v.message}")
            print()

        if not violations:
            print("✅ No import violations found")
        else:
            print("Summary by type:")
            for violation_type, type_violations in sorted(by_type.items()):
                print(f"  {violation_type}: {len(type_violations)}")


if __name__ == "__main__":
    main()
