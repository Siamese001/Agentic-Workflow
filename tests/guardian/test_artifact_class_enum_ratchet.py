"""Ratchet test: GuardianResult must use ArtifactClass enum, not .value strings."""

import ast
import pathlib

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    L0_ROUTING_DIR,
    TESTS_DIR,
)


def _find_guardian_result_with_value_usage(root_dir: pathlib.Path) -> list[tuple[pathlib.Path, int, str]]:
    """
    Scan Python files for GuardianResult construction with .value usage on artifact_class.

    Args:
        root_dir: Directory to scan (recursively) or specific file to scan

    Returns:
        List of (file_path, line_number, description) tuples
    """
    violations = []

    # AST-context whitelist: .value allowed only in these function/method names
    allowed_contexts = {
        "to_dict",  # GuardianResult serialization method
        "_emit_contract_json_schema",  # Schema helper
        "_snapshot_schema_keys",  # Schema helper
        "_parse_artifact_class",  # Deserialization helper
        "validate_against_json_schema",  # Schema validation
    }

    # Determine if we're scanning a directory or a single file
    if root_dir.is_file():
        files_to_scan = [root_dir]
    else:
        files_to_scan = root_dir.rglob("*.py")

    for py_file in files_to_scan:
        try:
            with open(py_file, encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue

        # Add parent references for context walking
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if this is a GuardianResult constructor
                if (isinstance(node.func, ast.Name) and node.func.id == "GuardianResult") or (
                    isinstance(node.func, ast.Attribute) and node.func.attr == "GuardianResult"
                ):
                    # Look for artifact_class keyword argument
                    for kw in node.keywords:
                        if kw.arg == "artifact_class":
                            # Check if the value is .value access
                            if (
                                isinstance(kw.value, ast.Attribute)
                                and kw.value.attr == "value"
                                and isinstance(kw.value.value, ast.Attribute)
                                and isinstance(kw.value.value.value, ast.Name)
                                and kw.value.value.value.id == "ArtifactClass"
                            ):
                                # Check if we're in an allowed AST context
                                in_allowed_context = _check_ast_context_allowed(node, allowed_contexts)

                                if not in_allowed_context:
                                    violations.append(
                                        (
                                            py_file,
                                            node.lineno,
                                            f"GuardianResult with artifact_class=ArtifactClass.{kw.value.value.attr}.value",
                                        ),
                                    )

    return violations


def _check_ast_context_allowed(node: ast.AST, allowed_contexts: set[str]) -> bool:
    """
    Walk up the AST to check if the node is within an allowed context.

    Args:
        node: The AST node to check context for
        allowed_contexts: Set of function/method names where .value is allowed

    Returns:
        True if node is within an allowed context, False otherwise
    """
    parent = getattr(node, "parent", None)
    while parent:
        if isinstance(parent, ast.FunctionDef):
            # Check if function name is in allowed contexts
            if parent.name in allowed_contexts:
                return True

            # Special case: methods within GuardianResult class
            if (
                parent.name == "to_dict"
                and isinstance(getattr(parent, "parent", None), ast.ClassDef)
                and parent.parent.name == "GuardianResult"
            ):
                return True

        parent = getattr(parent, "parent", None)

    return False


def test_no_artifact_class_value_usage_in_construction():
    """Ratchet: GuardianResult construction must use enum, not .value strings."""
    repo_root = pathlib.Path(__file__).parent.parent.parent

    # Scan specific directories
    scan_dirs = [
        repo_root / L0_ROUTING_DIR / "scripts",
        repo_root / TESTS_DIR / "guardian",
    ]

    all_violations = []
    for scan_dir in scan_dirs:
        if scan_dir.exists():
            violations = _find_guardian_result_with_value_usage(scan_dir)
            all_violations.extend(violations)

    if all_violations:
        violation_msgs = [
            f"  {file_path.relative_to(repo_root)}:{line} - {desc}"
            for file_path, line, desc in all_violations
        ]
        raise AssertionError(
            "Found GuardianResult construction using .value:\n"
            + "\n".join(violation_msgs)
            + "\n\nUse ArtifactClass enum directly, e.g., artifact_class=ArtifactClass.AGGREGATE",
        )
        assert True  # no-exception contract


def test_synthetic_value_usage_detected():
    """Verify the ratchet would catch a synthetic .value usage."""
    import tempfile
    import textwrap

    synthetic_code = textwrap.dedent("""
        from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult, ArtifactClass

        # This should be flagged
        result = GuardianResult(
            guardian_id="test",
            artifact_class=ArtifactClass.AGGREGATE.value  # Violation: using .value
        )
    """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(synthetic_code)
        f.flush()
        temp_file_path = pathlib.Path(f.name)

        # Only scan the specific synthetic file, not the whole directory
        violations = _find_guardian_result_with_value_usage(temp_file_path)

        # Should find at least one violation
        assert len(violations) >= 1
        # All violations should be about the .value usage
        for _, _, desc in violations:
            assert "artifact_class=ArtifactClass.AGGREGATE.value" in desc


def test_synthetic_value_usage_allowed_in_to_dict():
    """Verify .value is allowed inside GuardianResult.to_dict() method."""
    import tempfile
    import textwrap

    synthetic_code = textwrap.dedent("""
        from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult, ArtifactClass

        class GuardianResult:
            def to_dict(self):
                # This should be allowed - inside to_dict() method
                return {
                    "artifact_class": ArtifactClass.AGGREGATE.value,
                    "guardian_id": self.guardian_id
                }
    """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(synthetic_code)
        f.flush()

        violations = _find_guardian_result_with_value_usage(pathlib.Path(f.name))

        # Should find no violations - .value inside to_dict() is allowed
        assert len(violations) == 0


def test_synthetic_value_usage_rejected_in_construction():
    """Verify .value is rejected in run_all_guardians() construction context."""
    import tempfile
    import textwrap

    synthetic_code = textwrap.dedent("""
        from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult, ArtifactClass

        def run_all_guardians():
            # This should be flagged - not in allowed context
            results = []
            for guardian_id in ["hygiene", "manifest"]:
                result = GuardianResult(
                    guardian_id=guardian_id,
                    artifact_class=ArtifactClass.INDIVIDUAL.value  # Violation
                )
                results.append(result)
            return results
    """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(synthetic_code)
        f.flush()

        violations = _find_guardian_result_with_value_usage(pathlib.Path(f.name))

        # Should find violations - .value in construction context is not allowed
        assert len(violations) >= 1
        for _, _, desc in violations:
            assert "artifact_class=ArtifactClass.INDIVIDUAL.value" in desc
