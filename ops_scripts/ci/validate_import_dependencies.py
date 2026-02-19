#!/usr/bin/env python3
"""
Import Dependency Validation Hook

Validates that all import statements in Python files resolve to existing modules.
Catches missing dependencies, undefined references, and basic import syntax errors.
"""

import argparse
import ast
import importlib.util
import os
import re
import sys
from pathlib import Path


class ImportDependencyValidator:
    """Validates import dependencies in Python files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.repo_package_roots = self._discover_repo_package_roots()
        self.errors = []
        self.warnings = []

    def _discover_repo_package_roots(self) -> set[str]:
        """Discover top-level package roots in the repository."""
        roots: set[str] = set()
        for child in self.project_root.iterdir():
            if child.is_dir() and (child / "__init__.py").exists():
                roots.add(child.name)
        return roots

    def validate_file(self, file_path: Path) -> list[str]:
        """Validate a single Python file for import issues."""
        errors = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to extract imports
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                return [f"Syntax error in {file_path}: {e}"]

            # Extract all import statements
            imports = self._extract_imports(tree)

            # Validate each import
            for import_info in imports:
                error = self._validate_import(import_info, file_path)
                if error:
                    errors.append(error)

        except Exception as e:
            errors.append(f"Error processing {file_path}: {e}")

        return errors

    def _extract_imports(self, tree: ast.AST) -> list[dict]:
        """Extract import statements from AST."""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {"type": "import", "module": alias.name, "alias": alias.asname, "line": node.lineno}
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import_from",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                            "level": node.level,
                        }
                    )

        return imports

    def _validate_import(self, import_info: dict, file_path: Path) -> str | None:
        """Validate a single import statement."""
        try:
            if import_info["type"] == "import":
                return self._validate_import_statement(import_info, file_path)
            elif import_info["type"] == "import_from":
                return self._validate_import_from(import_info, file_path)
        except Exception as e:
            return (
                f"Line {import_info['line']}: Error validating import '{import_info.get('module', '')}': {e}"
            )

        return None

    def _validate_import_statement(self, import_info: dict, file_path: Path) -> str | None:
        """Validate 'import x' statements."""
        module_name = import_info["module"]
        line = import_info["line"]

        # Skip relative imports (shouldn't occur with import statement)
        if module_name.startswith("."):
            return None

        if not self._module_exists(module_name):
            return f"Line {line}: Module '{module_name}' not found"

        return None

    def _validate_import_from(self, import_info: dict, file_path: Path) -> str | None:
        """Validate 'from x import y' statements."""
        module = import_info["module"]
        name = import_info["name"]
        level = import_info["level"]
        line = import_info["line"]

        # Handle relative imports
        if level > 0:
            return self._validate_relative_import(import_info, file_path)

        # Handle absolute imports
        if module:
            full_module = module
        else:
            # from . import x (module is None)
            return f"Line {line}: Relative import without module base"

        if not self._module_exists(full_module):
            return f"Line {line}: Module '{full_module}' not found"

        # Try to get the specific name
        if name == "*":
            # Star import - accept it
            return None

        # Static check: verify imported name likely exists for local modules.
        # For third-party/stdlib modules we only verify the module resolves.
        name_exists, name_error = self._imported_name_exists(full_module, name)
        if not name_exists:
            return f"Line {line}: {name_error}"

        return None

    def _validate_relative_import(self, import_info: dict, file_path: Path) -> str | None:
        """Validate relative imports."""
        # For pre-commit, we'll be more lenient with relative imports
        # since they depend on the file's location in the package structure
        level = import_info["level"]
        module = import_info["module"] or ""
        line = import_info["line"]

        # Basic sanity check: relative imports should use dots
        if level == 0 and not module:
            return f"Line {line}: Invalid relative import syntax"

        # For now, accept relative imports but warn about complex ones
        if level > 3:
            return f"Line {line}: Deep relative import (level {level}) - consider restructuring"

        return None

    def _module_exists(self, module_name: str) -> bool:
        """Return True if module appears resolvable via repo files or importlib spec lookup."""
        if not module_name:
            return False

        # Resolve repository-local modules without executing imports.
        local_path = self._resolve_local_module_path(module_name)
        if local_path is not None:
            return True

        # Resolve stdlib/third-party without executing module body.
        try:
            return importlib.util.find_spec(module_name) is not None
        except (ImportError, AttributeError, ValueError, ModuleNotFoundError):
            return False

    def _resolve_local_module_path(self, module_name: str) -> Path | None:
        """Resolve a repository-local module path if present."""
        root = module_name.split(".", 1)[0]
        if root not in self.repo_package_roots:
            return None

        parts = module_name.split(".")
        candidate_file = self.project_root.joinpath(*parts).with_suffix(".py")
        if candidate_file.exists():
            return candidate_file

        candidate_pkg = self.project_root.joinpath(*parts) / "__init__.py"
        if candidate_pkg.exists():
            return candidate_pkg

        return None

    def _imported_name_exists(self, module_name: str, imported_name: str) -> tuple[bool, str]:
        """Best-effort static check for `from module import name`."""
        if imported_name == "*":
            return True, ""

        module_path = self._resolve_local_module_path(module_name)
        if module_path is None:
            # External module: module-level check is sufficient for this hook.
            return True, ""

        try:
            source = module_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(module_path))
        except (OSError, SyntaxError) as e:
            return False, f"cannot parse module '{module_name}' ({e})"

        exported_names: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                exported_names.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        exported_names.add(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                exported_names.add(node.target.id)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    exported_names.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != "*":
                        exported_names.add(alias.asname or alias.name)

        if imported_name in exported_names:
            return True, ""
        return False, f"'{imported_name}' not found in module '{module_name}'"

    def validate_repository(self, target_files: list[Path] | None = None) -> bool:
        """Validate Python files in the repository or a supplied target subset."""
        python_files = target_files if target_files else list(self.project_root.rglob("*.py"))

        # Exclude common non-source directories
        exclude_dirs = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".pytest_cache",
            ".mypy_cache",
            "node_modules",
            "build",
            "dist",
            ".tox",
            "_quarantine",
            "archives",
        }

        python_files = [
            f for f in python_files if not any(exclude_dir in f.parts for exclude_dir in exclude_dirs)
        ]

        all_errors = []

        for py_file in python_files:
            file_errors = self.validate_file(py_file)
            if file_errors:
                all_errors.extend([f"{py_file}: {error}" for error in file_errors])

        if all_errors:
            print("ERROR: Import Dependency Validation Failed")
            print("=" * 50)
            for error in all_errors:
                print(f"  {error}")
            print("=" * 50)
            print(f"Found {len(all_errors)} import errors")
            return False
        else:
            print(f"OK: Import Dependency Validation Passed ({len(python_files)} files)")
            return True


BASELINE_FILE = Path(__file__).resolve().parents[2] / "ops_scripts" / "hooks" / "import_dep_baseline.txt"

_LINE_NUM_RE = re.compile(r": Line \d+:")
_PROJECT_ROOT_STR = str(Path(__file__).resolve().parents[2])


def _normalize_baseline_key(entry: str, project_root: str = _PROJECT_ROOT_STR) -> str:
    """Normalize a baseline entry to be path-style- and line-number-insensitive.

    Converts the file path portion to a repo-relative forward-slash path and
    strips 'Line N:' so that absolute vs relative path differences and
    import-line shifts do not cause pre-existing violations to appear new.
    """
    colon_idx = entry.find(": ")
    if colon_idx <= 0:
        return entry
    path_part = entry[:colon_idx]
    rest = entry[colon_idx:]
    path_norm = path_part.replace("\\", "/")
    root_norm = project_root.replace("\\", "/")
    if path_norm.startswith(root_norm):
        path_norm = path_norm[len(root_norm) :].lstrip("/")
    rest = _LINE_NUM_RE.sub(":", rest, count=1)
    return path_norm + rest


def load_import_baseline() -> set[str]:
    """Load baseline of known import errors (normalized, location-insensitive)."""
    if not BASELINE_FILE.exists():
        return set()
    try:
        content = BASELINE_FILE.read_text(encoding="utf-8")
        return {_normalize_baseline_key(line.strip()) for line in content.splitlines() if line.strip()}
    except (OSError, UnicodeDecodeError):
        return set()


def main():
    """Main entry point for the hook."""
    parser = argparse.ArgumentParser(description="Validate import dependencies")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write current errors to baseline (requires ALLOW_IMPORT_BASELINE_WRITE=1)",
    )
    parser.add_argument("filenames", nargs="*", help="Optional staged Python files from pre-commit")

    args = parser.parse_args()
    validator = ImportDependencyValidator(args.project_root)

    if args.write_baseline:
        if os.environ.get("ALLOW_IMPORT_BASELINE_WRITE") != "1":
            print("[ERROR] --write-baseline requires ALLOW_IMPORT_BASELINE_WRITE=1")
            sys.exit(1)
        all_errors = []
        python_files = list(args.project_root.rglob("*.py"))
        exclude_dirs = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".pytest_cache",
            ".mypy_cache",
            "node_modules",
            "build",
            "dist",
            ".tox",
            "_quarantine",
            "archives",
        }
        python_files = [f for f in python_files if not any(d in f.parts for d in exclude_dirs)]
        for py_file in python_files:
            file_errors = validator.validate_file(py_file)
            for err in file_errors:
                all_errors.append(f"{py_file}: {err}")
        all_errors.sort()
        BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_FILE.write_text("\n".join(all_errors) + "\n", encoding="utf-8")
        print(f"Wrote {len(all_errors)} errors to {BASELINE_FILE.name}")
        sys.exit(0)

    target_files = [Path(f) for f in args.filenames if f.endswith(".py")]

    # Collect errors
    all_errors = []
    if target_files:
        scan_files = target_files
    else:
        scan_files = list(args.project_root.rglob("*.py"))
        exclude_dirs = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".pytest_cache",
            ".mypy_cache",
            "node_modules",
            "build",
            "dist",
            ".tox",
            "_quarantine",
            "archives",
        }
        scan_files = [f for f in scan_files if not any(d in f.parts for d in exclude_dirs)]

    for py_file in scan_files:
        file_errors = validator.validate_file(py_file)
        for err in file_errors:
            all_errors.append(f"{py_file}: {err}")

    baseline = load_import_baseline()
    new_errors = [e for e in all_errors if _normalize_baseline_key(e) not in baseline]

    if new_errors:
        print("ERROR: New Import Dependency Errors Found")
        print("=" * 50)
        for error in new_errors:
            print(f"  {error}")
        print("=" * 50)
        print(
            f"Found {len(new_errors)} new import errors ({len(all_errors)} total, {len(baseline)} baselined)"
        )
        sys.exit(1)
    else:
        if all_errors:
            print(f"OK: {len(all_errors)} baselined errors, 0 new errors")
        else:
            print(f"OK: Import Dependency Validation Passed ({len(scan_files)} files)")
        sys.exit(0)


if __name__ == "__main__":
    main()
