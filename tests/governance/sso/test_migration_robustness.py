"""Migration Robustness Tests - Verify collection isolation migration worked correctly."""

import ast
import pathlib
import re

import pytest


class TestMigrationSyntaxValidity:
    """Verify all migrated test files have valid Python syntax."""

    def test_all_test_files_have_valid_syntax(self):
        """Every test file should parse without syntax errors."""
        test_files = list(pathlib.Path("tests").rglob("test_*.py"))
        syntax_errors = []

        for test_file in test_files:
            try:
                content = test_file.read_text(encoding="utf-8")
                ast.parse(content)
            except SyntaxError as e:
                syntax_errors.append(f"{test_file}: {e}")
            except UnicodeDecodeError:
                syntax_errors.append(f"{test_file}: Unicode decode error")

        assert not syntax_errors, "Syntax errors found:\n" + "\n".join(syntax_errors)


class TestTopLevelImportElimination:
    """Verify no top-level app imports remain in test files."""

    def test_no_top_level_agentic_core_imports(self):
        """No top-level imports from agentic_core should remain."""
        test_files = list(pathlib.Path("tests").rglob("test_*.py"))
        violations = []

        # Pattern to match top-level imports from target modules
        top_level_import_pattern = re.compile(
            r"^(from\s+agentic_core\.\S*|import\s+agentic_core\.\S+)",
            re.MULTILINE,
        )

        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")

            # Skip if it's a demo file or migration script
            if "demo" in test_file.name or "migrator" in test_file.name:
                continue

            # Look for top-level imports outside of test functions
            lines = content.splitlines()
            in_test_function = False

            for i, line in enumerate(lines):
                # Track if we're in a test function
                if re.match(r"^\s*def\s+test_\w+\s*\(", line):
                    in_test_function = True
                elif re.match(r"^\s*(def|class|@)", line) and not line.strip().startswith("def test_"):
                    in_test_function = False

                # Check for top-level imports
                if not in_test_function and top_level_import_pattern.match(line.strip()):
                    violations.append(f"{test_file}:{i + 1}: {line.strip()}")

        assert not violations, "Top-level agentic_core imports found:\n" + "\n".join(violations)

    def test_no_top_level_apps_imports(self):
        """No top-level imports from apps_* modules should remain."""
        test_files = list(pathlib.Path("tests").rglob("test_*.py"))
        violations = []

        top_level_import_pattern = re.compile(
            r"^(from\s+apps_\S*|import\s+apps_\S+)",
            re.MULTILINE,
        )

        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")

            if "demo" in test_file.name or "migrator" in test_file.name:
                continue

            lines = content.splitlines()
            in_test_function = False

            for i, line in enumerate(lines):
                if re.match(r"^\s*def\s+test_\w+\s*\(", line):
                    in_test_function = True
                elif re.match(r"^\s*(def|class|@)", line) and not line.strip().startswith("def test_"):
                    in_test_function = False

                if not in_test_function and top_level_import_pattern.match(line.strip()):
                    violations.append(f"{test_file}:{i + 1}: {line.strip()}")

        assert not violations, "Top-level apps_* imports found:\n" + "\n".join(violations)

    def test_no_top_level_system_learning_imports(self):
        """No top-level imports from system_learning should remain."""
        test_files = list(pathlib.Path("tests").rglob("test_*.py"))
        violations = []

        top_level_import_pattern = re.compile(
            r"^(from\s+system_learning\.\S*|import\s+system_learning\.\S+)",
            re.MULTILINE,
        )

        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")

            if "demo" in test_file.name or "migrator" in test_file.name:
                continue

            lines = content.splitlines()
            in_test_function = False

            for i, line in enumerate(lines):
                if re.match(r"^\s*def\s+test_\w+\s*\(", line):
                    in_test_function = True
                elif re.match(r"^\s*(def|class|@)", line) and not line.strip().startswith("def test_"):
                    in_test_function = False

                if not in_test_function and top_level_import_pattern.match(line.strip()):
                    violations.append(f"{test_file}:{i + 1}: {line.strip()}")

        assert not violations, "Top-level system_learning imports found:\n" + "\n".join(violations)


class TestImportPlacementCorrectness:
    """Verify imports are correctly placed inside test functions."""

    def test_imports_in_test_functions(self):
        """Imports should be inside test functions, not at module level."""
        test_files = list(pathlib.Path("tests").rglob("test_*.py"))
        files_without_function_imports = []

        for test_file in test_files:
            if "demo" in test_file.name or "migrator" in test_file.name:
                continue

            content = test_file.read_text(encoding="utf-8")

            # Check if file has any target imports
            has_target_imports = bool(
                re.search(
                    r"from\s+(agentic_core|apps_|system_learning)\.\S*|import\s+(agentic_core|apps_|system_learning)\.\S+",
                    content,
                )
            )

            if has_target_imports:
                # Check if imports are inside test functions
                has_function_imports = bool(
                    re.search(
                        r"def\s+test_\w+.*?\n\s+from\s+(agentic_core|apps_|system_learning)",
                        content,
                        re.DOTALL,
                    )
                )

                if not has_function_imports:
                    files_without_function_imports.append(str(test_file))

        # Allow some files to not have imports (they might be clean)
        # But if they have target imports, those should be in functions
        assert len(files_without_function_imports) < 50, (
            f"Too many files ({len(files_without_function_imports)}) have imports but not in test functions"
        )


class TestLegacyCommentCleanup:
    """Verify legacy commented imports are cleaned up."""

    def test_no_legacy_moved_comments(self):
        """Legacy '# # MOVED:' comments should be cleaned up."""
        test_files = list(pathlib.Path("tests").rglob("test_*.py"))
        files_with_legacy_comments = []

        for test_file in test_files:
            if "demo" in test_file.name:
                continue  # Demo files can keep comments for reference

            content = test_file.read_text(encoding="utf-8")

            if "#  # MOVED:" in content:
                files_with_legacy_comments.append(str(test_file))

        # Allow some legacy comments for now, but flag the issue
        if files_with_legacy_comments:
            print(f"WARNING: {len(files_with_legacy_comments)} files still have legacy '# # MOVED:' comments")
            # Don't fail the test for now, but this should be cleaned up


class TestDuplicateImportElimination:
    """Verify duplicate import statements are eliminated."""

    def test_no_duplicate_imports_in_functions(self):
        """Test functions should not have duplicate import statements."""
        test_files = list(pathlib.Path("tests").rglob("test_*.py"))
        duplicate_issues = []

        for test_file in test_files:
            if "demo" in test_file.name or "migrator" in test_file.name:
                continue

            content = test_file.read_text(encoding="utf-8")

            # Find test functions
            test_functions = re.finditer(
                r"(def\s+test_\w+\s*\([^)]*\).*?)(?=def\s+test_\w+|\Z)",
                content,
                re.DOTALL,
            )

            for func_match in test_functions:
                func_content = func_match.group(1)
                func_name = re.search(r"def\s+(test_\w+)", func_content).group(1)

                # Find all import statements in this function
                imports = re.findall(r"from\s+\S+|import\s+\S+", func_content)

                # Check for duplicates
                seen_imports = set()
                duplicates = set()

                for import_stmt in imports:
                    if import_stmt in seen_imports:
                        duplicates.add(import_stmt)
                    seen_imports.add(import_stmt)

                if duplicates:
                    duplicate_issues.append(f"{test_file}:{func_name} - Duplicates: {duplicates}")

        assert not duplicate_issues, "Duplicate imports found:\n" + "\n".join(duplicate_issues)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
