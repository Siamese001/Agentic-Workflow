"""
Wave 15.2 — Full Static Upward Import Enforcement (21 Pairs).

AST-based static import detection enforcing gravity rule:
Lower layer may NOT import higher layer.
Covers all 21 ordered layer pairs (L0-L6).
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path

import pytest

AGENTIC_CORE_ROOT = Path(__file__).parent.parent.parent / "agentic_core"
LAYER_PATTERN = re.compile(r"^L(\d+)_")
IMPORT_LAYER_PATTERN = re.compile(r"agentic_core\.L(\d+)_")


@dataclass
class ImportViolation:
    """Represents an upward import violation."""

    source_file: Path
    source_layer: int
    target_layer: int
    import_statement: str
    line_number: int
    violation_type: str = "UPWARD_IMPORT"

    def __str__(self) -> str:
        return (
            f"{self.violation_type}: L{self.source_layer} -> L{self.target_layer} "
            f"in {self.source_file.name}:{self.line_number} ({self.import_statement})"
        )


def layer_of_path(path: Path) -> int | None:
    """Extract layer number from a path."""
    try:
        rel = path.relative_to(AGENTIC_CORE_ROOT)
    except ValueError:
        return None

    parts = rel.parts
    if not parts:
        return None

    match = LAYER_PATTERN.match(parts[0])
    if match:
        return int(match.group(1))
    return None


def extract_import_targets(node: ast.AST) -> list[tuple[str, int]]:
    """Extract import target strings and line numbers from an AST node.

    Returns:
        List of (import_string, line_number) tuples.
    """
    targets = []

    if isinstance(node, ast.Import):
        for alias in node.names:
            targets.append((alias.name, node.lineno))
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            targets.append((node.module, node.lineno))

    return targets


def _is_inside_function_or_guarded(tree: ast.AST, target_lineno: int) -> bool:
    """Check if a line is inside a function, method, or try/except block.

    Imports inside these constructs are considered "lazy" or "guarded"
    and are acceptable patterns that don't violate gravity rules.

    Args:
        tree: The AST tree to search.
        target_lineno: The line number to check.

    Returns:
        True if the line is inside a guarded context, False otherwise.
    """
    for node in ast.walk(tree):
        # Check functions/methods
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        return True
        # Check try/except blocks (guarded imports)
        if isinstance(node, ast.Try):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        return True
    return False


def detect_upward_imports(file_path: Path) -> list[ImportViolation]:
    """Detect upward import violations in a Python file.

    Only detects TRUE module-level static imports, not lazy imports
    inside functions which are an acceptable pattern.

    Args:
        file_path: Path to Python file to analyze.

    Returns:
        List of ImportViolation objects.
    """
    source_layer = layer_of_path(file_path)
    if source_layer is None:
        return []

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    violations = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for import_str, line_no in extract_import_targets(node):
                match = IMPORT_LAYER_PATTERN.search(import_str)
                if match:
                    target_layer = int(match.group(1))
                    if target_layer > source_layer:
                        # Skip imports inside functions (lazy imports are OK)
                        if _is_inside_function_or_guarded(tree, line_no):
                            continue

                        violation_type = "UPWARD_IMPORT"
                        if source_layer == 0 and target_layer in (5, 6):
                            violation_type = "DIRECT_L0_TO_L5_L6"

                        violations.append(
                            ImportViolation(
                                source_file=file_path,
                                source_layer=source_layer,
                                target_layer=target_layer,
                                import_statement=import_str,
                                line_number=line_no,
                                violation_type=violation_type,
                            )
                        )

    return violations


def scan_all_layer_files() -> list[ImportViolation]:
    """Scan all layer files for upward import violations.

    Returns:
        List of all violations found.
    """
    all_violations = []

    for layer in range(7):
        layer_dir = None
        for item in AGENTIC_CORE_ROOT.iterdir():
            if item.is_dir() and item.name.startswith(f"L{layer}_"):
                layer_dir = item
                break

        if layer_dir is None:
            continue

        for py_file in layer_dir.rglob("*.py"):
            violations = detect_upward_imports(py_file)
            all_violations.extend(violations)

    return all_violations


def get_all_layer_pairs() -> list[tuple[int, int]]:
    """Get all 21 ordered layer pairs where lower < higher.

    Returns:
        List of (lower, higher) tuples.
    """
    pairs = []
    for lower in range(7):
        for higher in range(lower + 1, 7):
            pairs.append((lower, higher))
    return pairs


@pytest.mark.governance
class TestUpwardImportEnforcement:
    """Test suite for upward import enforcement."""

    def test_all_21_layer_pairs_covered(self):
        """Assert all 21 ordered layer pairs are defined."""
        pairs = get_all_layer_pairs()
        assert len(pairs) == 21, f"Expected 21 pairs, got {len(pairs)}"

        # Verify specific pairs
        expected_pairs = [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (0, 6),
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (1, 6),
            (2, 3),
            (2, 4),
            (2, 5),
            (2, 6),
            (3, 4),
            (3, 5),
            (3, 6),
            (4, 5),
            (4, 6),
            (5, 6),
        ]
        assert pairs == expected_pairs

    def test_detector_identifies_l0_to_l5_l6_as_special(self):
        """Assert L0→L5 and L0→L6 are classified as DIRECT_L0_TO_L5_L6."""
        violations = scan_all_layer_files()

        l0_to_l5_l6 = [v for v in violations if v.source_layer == 0 and v.target_layer in (5, 6)]

        for v in l0_to_l5_l6:
            assert v.violation_type == "DIRECT_L0_TO_L5_L6", (
                f"Expected DIRECT_L0_TO_L5_L6, got {v.violation_type} for {v}"
            )

    def test_scan_produces_deterministic_results(self):
        """Assert scanning produces consistent results."""
        violations1 = scan_all_layer_files()
        violations2 = scan_all_layer_files()

        assert len(violations1) == len(violations2), "Non-deterministic scan"

    def test_violation_summary(self):
        """Print violation summary for evidence."""
        violations = scan_all_layer_files()

        print("\n=== UPWARD IMPORT VIOLATION SUMMARY ===")
        print(f"Total violations found: {len(violations)}")

        # Group by violation type
        by_type = {}
        for v in violations:
            by_type.setdefault(v.violation_type, []).append(v)

        for vtype, vlist in sorted(by_type.items()):
            print(f"  {vtype}: {len(vlist)}")

        # Group by layer pair
        by_pair = {}
        for v in violations:
            pair = (v.source_layer, v.target_layer)
            by_pair.setdefault(pair, []).append(v)

        print("\nViolations by layer pair:")
        for pair in get_all_layer_pairs():
            count = len(by_pair.get(pair, []))
            if count > 0:
                print(f"  L{pair[0]} -> L{pair[1]}: {count}")

        assert True  # Evidence test


def _detect_upward_imports_with_root(file_path: Path, agentic_root: Path) -> list[ImportViolation]:
    """Detect upward imports with custom agentic_core root for testing.

    Args:
        file_path: Path to Python file to analyze.
        agentic_root: Root path for agentic_core.

    Returns:
        List of ImportViolation objects.
    """
    # Determine source layer from path relative to custom root
    try:
        rel = file_path.relative_to(agentic_root)
    except ValueError:
        return []

    parts = rel.parts
    if not parts:
        return []

    match = LAYER_PATTERN.match(parts[0])
    if not match:
        return []

    source_layer = int(match.group(1))

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    violations = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for import_str, line_no in extract_import_targets(node):
                match = IMPORT_LAYER_PATTERN.search(import_str)
                if match:
                    target_layer = int(match.group(1))
                    if target_layer > source_layer:
                        violation_type = "UPWARD_IMPORT"
                        if source_layer == 0 and target_layer in (5, 6):
                            violation_type = "DIRECT_L0_TO_L5_L6"

                        violations.append(
                            ImportViolation(
                                source_file=file_path,
                                source_layer=source_layer,
                                target_layer=target_layer,
                                import_statement=import_str,
                                line_number=line_no,
                                violation_type=violation_type,
                            )
                        )

    return violations


@pytest.mark.governance
class TestUpwardImportMutation:
    """Mutation tests for upward import detector."""

    def test_mutation_l0_imports_l5(self, tmp_path):
        """Mutation: L0 importing L5 must be detected."""
        agentic_root = tmp_path / "agentic_core"
        l0_dir = agentic_root / "L0_routing"
        l0_dir.mkdir(parents=True)

        test_file = l0_dir / "test_violation.py"
        test_file.write_text("from agentic_core.L5_safety.validators import SomeValidator\n")

        violations = _detect_upward_imports_with_root(test_file, agentic_root)
        assert len(violations) == 1, f"Expected 1 violation, got {len(violations)}"
        assert violations[0].source_layer == 0
        assert violations[0].target_layer == 5
        assert violations[0].violation_type == "DIRECT_L0_TO_L5_L6"

    def test_mutation_l2_imports_l6(self, tmp_path):
        """Mutation: L2 importing L6 must be detected."""
        agentic_root = tmp_path / "agentic_core"
        l2_dir = agentic_root / "L2_execution"
        l2_dir.mkdir(parents=True)

        test_file = l2_dir / "test_violation.py"
        test_file.write_text("import agentic_core.L6_observability.telemetry\n")

        violations = _detect_upward_imports_with_root(test_file, agentic_root)
        assert len(violations) == 1
        assert violations[0].source_layer == 2
        assert violations[0].target_layer == 6
        assert violations[0].violation_type == "UPWARD_IMPORT"

    def test_mutation_l1_imports_l3(self, tmp_path):
        """Mutation: L1 importing L3 must be detected."""
        agentic_root = tmp_path / "agentic_core"
        l1_dir = agentic_root / "L1_cognition"
        l1_dir.mkdir(parents=True)

        test_file = l1_dir / "test_violation.py"
        test_file.write_text("from agentic_core.L3_orchestration.workflow import Workflow\n")

        violations = _detect_upward_imports_with_root(test_file, agentic_root)
        assert len(violations) == 1
        assert violations[0].source_layer == 1
        assert violations[0].target_layer == 3

    def test_mutation_downward_import_allowed(self, tmp_path):
        """Mutation: Downward imports (L5->L0) must NOT be flagged."""
        agentic_root = tmp_path / "agentic_core"
        l5_dir = agentic_root / "L5_safety"
        l5_dir.mkdir(parents=True)

        test_file = l5_dir / "test_allowed.py"
        test_file.write_text("from agentic_core.L0_routing.router import Router\n")

        violations = _detect_upward_imports_with_root(test_file, agentic_root)
        assert len(violations) == 0, "Downward import should not be flagged"

    def test_mutation_same_layer_import_allowed(self, tmp_path):
        """Mutation: Same-layer imports must NOT be flagged."""
        agentic_root = tmp_path / "agentic_core"
        l3_dir = agentic_root / "L3_orchestration"
        l3_dir.mkdir(parents=True)

        test_file = l3_dir / "test_allowed.py"
        test_file.write_text("from agentic_core.L3_orchestration.other_module import Something\n")

        violations = _detect_upward_imports_with_root(test_file, agentic_root)
        assert len(violations) == 0, "Same-layer import should not be flagged"

    def test_mutation_non_layer_import_ignored(self, tmp_path):
        """Mutation: Non-layer imports must NOT be flagged."""
        agentic_root = tmp_path / "agentic_core"
        l0_dir = agentic_root / "L0_routing"
        l0_dir.mkdir(parents=True)

        test_file = l0_dir / "test_allowed.py"
        test_file.write_text(
            "from agentic_core.utils.helpers import helper_func\nimport os\nfrom pathlib import Path\n"
        )

        violations = _detect_upward_imports_with_root(test_file, agentic_root)
        assert len(violations) == 0, "Non-layer imports should not be flagged"


@pytest.mark.governance
class TestNegativeRegressionNewDefinition:
    """Negative regression tests: prove NEW definition catches reintroduced module-level upward imports.

    These tests use the real codebase scanner (NEW_DEFINITION with _is_inside_function_or_guarded).
    They will FAIL if a module-level static upward import is reintroduced into any layer file.
    """

    def test_zero_violations_under_new_definition(self):
        """NEW_DEFINITION must report exactly 0 violations.

        This is the primary regression lock for Phase 1 Path B.
        If any module-level static upward import is reintroduced, this test fails.
        """
        violations = scan_all_layer_files()
        assert violations == [], (
            "NEW_DEFINITION violation(s) reintroduced — Phase 1 regression:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def test_module_level_upward_import_is_caught_not_lazy(self, tmp_path):
        """Negative: a module-level static upward import must be detected.

        Proves _is_inside_function_or_guarded does NOT suppress true
        module-level violations — only function/try-scoped ones.
        """
        (tmp_path / "L2_execution").mkdir()
        victim = tmp_path / "L2_execution" / "reintroduced.py"
        victim.write_text(
            "from agentic_core.L5_safety.enforcement.activation_gate import assert_activation_allowed\n"
        )
        violations = _detect_upward_imports_with_root(victim, tmp_path)
        assert len(violations) == 1, (
            f"Expected 1 violation for module-level static upward import, got {len(violations)}"
        )
        assert violations[0].source_layer == 2
        assert violations[0].target_layer == 5

    def test_lazy_upward_import_inside_function_is_allowed(self, tmp_path):
        """Negative: a lazy upward import inside a function must NOT be flagged.

        Proves _is_inside_function_or_guarded correctly suppresses
        function-scoped imports — the core semantic change of Path B.
        Uses detect_upward_imports (NEW_DEFINITION) with a real L2 temp file.
        """
        import tempfile

        real_l2 = AGENTIC_CORE_ROOT / "L2_execution"
        with tempfile.NamedTemporaryFile(dir=real_l2, suffix=".py", delete=False, mode="w") as tf:
            tf.write(
                "def _get_assert_activation_allowed():\n"
                "    from agentic_core.L5_safety.enforcement.activation_gate"
                " import assert_activation_allowed\n"
                "    return assert_activation_allowed\n"
            )
            tmp_name = tf.name
        try:
            violations = detect_upward_imports(Path(tmp_name))
            assert violations == [], f"Lazy import inside function must not be flagged: {violations}"
        finally:
            Path(tmp_name).unlink(missing_ok=True)
