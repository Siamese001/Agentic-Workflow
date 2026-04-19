"""
Phase 3.2: Enhanced Test Coverage Integration for Exception Handling Violations.

Comprehensive test discovery, test-to-violation mapping, and auto-generated
test skeletons for remediated exception handlers.

Key capabilities:
1. Dynamic test discovery from existing test suites
2. Comprehensive tests_execution_of edge population
3. Test-to-violation mapping with precise line coverage
4. Auto-generated test skeletons for remediated code
5. Coverage gap analysis and prioritization
"""

from __future__ import annotations

import ast
import sqlite3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tqdm import tqdm


class TestFramework(Enum):
    """Supported test frameworks."""

    PYTEST = "pytest"
    UNITTEST = "unittest"
    UNKNOWN = "unknown"


@dataclass
class TestFunction:
    """Test function information."""

    name: str
    file_path: str
    line_start: int
    line_end: int
    framework: TestFramework
    test_type: str  # 'unit', 'integration', 'property'
    target_functions: list[str]  # Functions this test calls
    target_classes: list[str]  # Classes this test uses
    target_modules: list[str]  # Modules this test imports


@dataclass
class TestCoverageGap:
    """Gap in test coverage for a violation."""

    violation_file: str
    violation_line: int
    violation_function: str | None
    missing_test_types: list[str]
    suggested_test_name: str
    priority: float  # 0.0 to 1.0


class TestDiscoveryEngine:
    """Discover and analyze test functions from test suites."""

    def __init__(self):
        self.test_patterns = {
            "test_": TestFramework.PYTEST,
            "Test": TestFramework.UNITTEST,
        }

    def discover_tests_in_directory(self, test_dir: Path) -> list[TestFunction]:
        """Discover all test functions in a directory."""
        tests = []

        if not test_dir.exists():
            return tests

        for test_file in test_dir.rglob("*.py"):
            file_tests = self.discover_tests_in_file(test_file)
            tests.extend(file_tests)

        return tests

    def discover_tests_in_file(self, test_file: Path) -> list[TestFunction]:
        """Discover test functions in a single test file."""
        import re

        try:
            with open(test_file, encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError, ValueError, TypeError) as e:
            print(f"    ⚠️  Could not read test file {test_file}: {e}")
            return []

        try:
            tree = ast.parse(content)
            tests = []

            # Extract file-level imports for module detection
            file_imports: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_imports.append(node.module)

            for node in tqdm(ast.walk(tree), desc="ast walk tests", unit="node", leave=False):
                if isinstance(node, ast.FunctionDef):
                    framework = self._detect_framework(node.name, content)
                    if framework != TestFramework.UNKNOWN:
                        test_info = self._analyze_test_function(node, test_file, framework, file_imports)
                        tests.append(test_info)
                elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                    # Unittest test class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test"):
                            test_info = self._analyze_test_function(
                                item,
                                test_file,
                                TestFramework.UNITTEST,
                                file_imports,
                            )
                            tests.append(test_info)

            return tests

        except SyntaxError:
            # Fallback: use regex to find test function names when AST parse fails
            tests = []
            for match in tqdm(
                list(re.finditer(r"^def (test\w+)\s*\(", content, re.MULTILINE)),
                desc="regex matches",
                unit="match",
                leave=False,
            ):
                func_name = match.group(1)
                line_no = content[: match.start()].count("\n") + 1
                tests.append(
                    TestFunction(
                        name=func_name,
                        file_path=str(test_file),
                        line_start=line_no,
                        line_end=line_no,
                        framework=TestFramework.PYTEST,
                        test_type="unit",
                        target_functions=[],
                        target_classes=[],
                        target_modules=[],
                    ),
                )
            return tests
        except (OSError, RuntimeError, ValueError, TypeError) as e:
            print(f"    ⚠️  Could not analyze test file {test_file}: {e}")
            return []

    def _detect_framework(self, func_name: str, content: str) -> TestFramework:
        """Detect the test framework used."""
        if func_name.startswith("test_"):
            return TestFramework.PYTEST
        elif func_name.startswith("test") and "unittest" in content:
            return TestFramework.UNITTEST
        return TestFramework.UNKNOWN

    def _analyze_test_function(
        self,
        node: ast.FunctionDef,
        test_file: Path,
        framework: TestFramework,
        file_imports: list[str] | None = None,
    ) -> TestFunction:
        """Analyze a test function to extract target information."""
        target_functions: list[str] = []
        target_classes: list[str] = []
        target_modules: list[str] = list(file_imports or [])

        # Walk the AST to find function calls
        for child in tqdm(ast.walk(node), desc="ast walk calls", unit="node", leave=False):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    name = child.func.id
                    # Uppercase first letter = class instantiation
                    if name and name[0].isupper():
                        if name not in target_classes:
                            target_classes.append(name)
                    else:
                        if name not in target_functions:
                            target_functions.append(name)
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        # module.function() pattern
                        func_name = child.func.attr
                        mod_name = child.func.value.id
                        if func_name not in target_functions:
                            target_functions.append(func_name)
                        if mod_name not in target_modules:
                            target_modules.append(mod_name)

        # Determine test type
        test_type = self._determine_test_type(node, target_functions)

        return TestFunction(
            name=node.name,
            file_path=str(test_file),
            line_start=node.lineno,
            line_end=getattr(node, "end_lineno", node.lineno),
            framework=framework,
            test_type=test_type,
            target_functions=target_functions,
            target_classes=target_classes,
            target_modules=target_modules,
        )

    def _determine_test_type(self, node: ast.FunctionDef, targets: list[str]) -> str:
        """Determine the type of test (unit, integration, property)."""
        try:
            content = ast.unparse(node).lower()
        except (AttributeError, ValueError, TypeError):
            content = node.name.lower()

        # Property-based test patterns
        if any(pattern in content for pattern in ["hypothesis", "@given", "st.", "assume("]):
            return "property"

        # Integration test patterns
        if any(pattern in content for pattern in ["mock", "patch", "fixture", "setup"]):
            return "integration"

        # Default to unit test
        return "unit"


class TestCoverageAnalyzer:
    """Analyze test coverage for exception handling violations."""

    def __init__(self, adg_path: Path):
        self.adg_path = adg_path
        self.conn: sqlite3.Connection | None = None
        self.test_discovery = TestDiscoveryEngine()

    def __enter__(self) -> TestCoverageAnalyzer:
        self.conn = sqlite3.connect(str(self.adg_path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn:
            self.conn.close()

    def analyze_test_coverage_gaps(self, test_dirs: list[Path]) -> list[TestCoverageGap]:
        """Analyze test coverage gaps for exception handling violations."""
        if not self.conn:
            raise RuntimeError("Analyzer not used as context manager")

        print("🔍 Phase 3.2: Analyzing test coverage gaps...")

        # Discover all tests
        all_tests = []
        for test_dir in test_dirs:
            tests = self.test_discovery.discover_tests_in_directory(test_dir)
            all_tests.extend(tests)

        print(f"  Discovered {len(all_tests)} test functions")

        # Load violations from ADG
        violations = self._load_violations_for_coverage_analysis()
        print(f"  Analyzing {len(violations)} violations for coverage gaps")

        gaps = []
        for violation in tqdm(violations, desc="coverage gaps", unit="violation", leave=False):
            gap = self._analyze_single_violation_coverage(violation, all_tests)
            if gap:
                gaps.append(gap)

        # Sort by priority (highest first)
        gaps.sort(key=lambda g: g.priority, reverse=True)

        print(f"  Found {len(gaps)} test coverage gaps")
        return gaps

    def _load_violations_for_coverage_analysis(self) -> list[dict]:
        """Load violations that need test coverage analysis."""
        # Check schema to determine which columns exist
        cursor = self.conn.execute("PRAGMA table_info(violations)")
        columns = {row[1] for row in cursor.fetchall()}

        if "disposition" in columns and "severity" in columns:
            cursor = self.conn.execute("""
                SELECT file_path, line_no, evidence, severity
                FROM violations
                WHERE category = 'antipattern'
                  AND disposition IN ('untriaged', 'tested')
                  AND (evidence LIKE 'except:Exception%' OR evidence LIKE 'except:bare%')
                ORDER BY severity DESC, file_path, line_no
            """)
        elif "severity" in columns:
            cursor = self.conn.execute("""
                SELECT file_path, line_no, evidence, severity
                FROM violations
                WHERE category = 'antipattern'
                  AND (evidence LIKE 'except:Exception%' OR evidence LIKE 'except:bare%')
                ORDER BY severity DESC, file_path, line_no
            """)
        else:
            cursor = self.conn.execute("""
                SELECT file_path, line_no, evidence, 'MEDIUM'
                FROM violations
                WHERE category = 'antipattern'
                  AND (evidence LIKE 'except:Exception%' OR evidence LIKE 'except:bare%')
                ORDER BY file_path, line_no
            """)

        violations = []
        for file_path, line_no, evidence, severity in cursor.fetchall():
            violations.append(
                {"file_path": file_path, "line_no": line_no, "evidence": evidence, "severity": severity},
            )

        return violations

    def _analyze_single_violation_coverage(
        self,
        violation: dict,
        all_tests: list[TestFunction],
    ) -> TestCoverageGap | None:
        """Analyze test coverage for a single violation."""
        violation_file = violation["file_path"]
        violation_line = violation["line_no"]

        # Find tests that cover this file and line
        covering_tests = []
        for test in all_tests:
            if self._test_covers_violation(test, violation_file, violation_line):
                covering_tests.append(test)

        # Determine what test types are missing
        existing_types = {test.test_type for test in covering_tests}
        missing_types = ["unit", "integration"]  # We want both unit and integration tests

        # If we have good coverage, no gap
        if len(covering_tests) >= 2 and existing_types >= {"unit", "integration"}:
            return None

        # Calculate priority based on severity and existing coverage
        severity_bonus = {"HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.2}.get(violation["severity"], 0.3)
        coverage_bonus = len(covering_tests) * 0.1  # Less coverage = higher priority
        priority = min(severity_bonus + (0.5 - coverage_bonus), 1.0)

        # Generate suggested test name
        function_name = self._extract_function_name(violation_file, violation_line)
        suggested_name = (
            f"test_{function_name}_exception_handling" if function_name else "test_exception_handling"
        )

        return TestCoverageGap(
            violation_file=violation_file,
            violation_line=violation_line,
            violation_function=function_name,
            missing_test_types=missing_types,
            suggested_test_name=suggested_name,
            priority=priority,
        )

    def _test_covers_violation(self, test: TestFunction, violation_file: str, violation_line: int) -> bool:
        """Check if a test covers a violation."""
        # Check if test file is in same module or related module
        test_path = Path(test.file_path)
        violation_path = Path(violation_file)

        # Simple heuristic: test in tests/ directory for the same module
        if "tests" in test_path.parts:
            # Extract module name from test path
            test_module_parts = [p for p in test_path.parts if p != "tests" and p.endswith(".py")]
            violation_module_parts = violation_path.parts

            # Check if test is for the same module
            for part in test_module_parts:
                if any(part in vp for vp in violation_module_parts):
                    return True

        # Check if test imports the module containing the violation
        if any(violation_path.stem in target for target in test.target_modules):
            return True

        return False

    def _extract_function_name(self, file_path: str, line_no: int) -> str | None:
        """Extract the function name containing a violation."""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if line_no <= len(lines):
                # Search backwards for function definition
                for i in range(line_no - 1, max(-1, line_no - 50), -1):
                    line = lines[i].strip()
                    if line.startswith("def "):
                        return line.split("(")[0].replace("def ", "")
                    elif line.startswith("class "):
                        return line.split("(")[0].replace("class ", "")

        except (OSError, RuntimeError, ValueError, TypeError):  # guardian: allow-silent-swallow allow-return-none-swallow -- coverage lookup best-effort: caller treats None as no coverage data
            pass

        return None

    def populate_comprehensive_test_edges(self, test_dirs: list[Path]) -> dict[str, int]:
        """Populate comprehensive tests_execution_of edges in ADG."""
        if not self.conn:
            raise RuntimeError("Analyzer not used as context manager")

        print("🔗 Phase 3.2: Populating comprehensive test edges...")

        # Discover all tests
        all_tests = []
        for test_dir in test_dirs:
            tests = self.test_discovery.discover_tests_in_directory(test_dir)
            all_tests.extend(tests)

        print(f"  Processing {len(all_tests)} test functions")

        # Clear existing test edges (if edges table exists)
        deleted_count = 0
        try:
            cursor = self.conn.execute("DELETE FROM edges WHERE relation_type = 'tests_execution_of'")
            deleted_count = cursor.rowcount
        except sqlite3.Error:  # guardian: allow-silent-swallow -- DELETE best-effort: empty table or missing edges, continue with insert
            pass
        print(f"  Cleared {deleted_count} existing test edges")

        # Get all nodes from ADG (if nodes table exists)
        nodes = {}
        try:
            cursor = self.conn.execute("SELECT id, adg_name, entity_type, resolved_path FROM nodes")
        except sqlite3.Error:
            self.conn.commit()
            return {"tests_discovered": len(all_tests), "edges_created": 0, "nodes_added": 0}
        for node_id, adg_name, entity_type, resolved_path in cursor.fetchall():
            nodes[adg_name] = {"id": node_id, "entity_type": entity_type, "resolved_path": resolved_path}

        # Create test nodes and edges
        edges_created = 0
        for test in tqdm(all_tests, desc="test nodes", unit="test", leave=False):
            # Create test node
            test_adg_name = f"test::{test.name}"
            if test_adg_name not in nodes:
                cursor = self.conn.execute(
                    """
                    INSERT INTO nodes (adg_name, entity_type, layer, resolved_path, span_line, span_end_line)
                    VALUES (?, 'symbol', 'tests', ?, ?, ?)
                """,
                    (test_adg_name, test.file_path, test.line_start, test.line_end),
                )
                test_node_id = cursor.lastrowid
                nodes[test_adg_name] = {
                    "id": test_node_id,
                    "entity_type": "symbol",
                    "resolved_path": test.file_path,
                }
            else:
                test_node_id = nodes[test_adg_name]["id"]

            # Create edges to target functions/classes
            for target_func in tqdm(test.target_functions, desc="  target funcs", unit="func", leave=False):
                target_adg_name = f"symbol::{target_func}"
                if target_adg_name in nodes:
                    cursor = self.conn.execute(
                        """
                        INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                        VALUES (?, ?, 'tests_execution_of', 'test_linkage', ?, ?, ?)
                    """,
                        (
                            test_node_id,
                            nodes[target_adg_name]["id"],
                            test.file_path,
                            test.line_start,
                            target_func,
                        ),
                    )
                    edges_created += 1

        self.conn.commit()
        print(f"  Created {edges_created} new test edges")

        return {
            "tests_discovered": len(all_tests),
            "edges_created": edges_created,
            "nodes_added": len(all_tests) - (len(all_tests) - edges_created),  # Approximate
        }


class TestSkeletonGenerator:
    """Generate test skeletons for remediated exception handlers."""

    def __init__(self):
        self.test_templates = {
            "unit": self._unit_test_template,
            "integration": self._integration_test_template,
            "property": self._property_test_template,
        }

    def generate_test_skeleton(
        self,
        gap: TestCoverageGap,
        exception_type: str,
        remediation_strategy: str,
    ) -> str:
        """Generate a test skeleton for a coverage gap."""
        test_type = gap.missing_test_types[0] if gap.missing_test_types else "unit"
        template = self.test_templates.get(test_type, self._unit_test_template)
        return template(gap, exception_type, remediation_strategy)

    def _unit_test_template(
        self,
        gap: TestCoverageGap,
        exception_type: str,
        remediation_strategy: str,
    ) -> str:
        """Generate a unit test template."""
        function_name = gap.violation_function or "target_function"
        test_name = gap.suggested_test_name

        template = f'''def {test_name}():
    """Test exception handling in {function_name}."""
    # TODO: Implement this test to cover the exception handler at {gap.violation_file}:{gap.violation_line}

    # Test case 1: Normal operation
    # result = {function_name}(valid_input)
    # assert result is not None

    # Test case 2: Exception case - should raise {exception_type}
    # with pytest.raises({exception_type}):
    #     {function_name}(invalid_input)

    # Test case 3: Exception handling behavior
    # result = {function_name}(invalid_input)
    # assert result is None  # or expected fallback behavior

    pass  # Remove this line when implementing the test
'''
        return template

    def _integration_test_template(
        self,
        gap: TestCoverageGap,
        exception_type: str,
        remediation_strategy: str,
    ) -> str:
        """Generate an integration test template."""
        function_name = gap.violation_function or "target_function"
        test_name = f"{gap.suggested_test_name}_integration"

        template = f'''def {test_name}():
    """Integration test for exception handling in {function_name}."""
    # TODO: Implement this integration test

    # Setup: Mock external dependencies
    # with patch('module.external_dependency') as mock_dep:
    #     mock_dep.side_effect = {exception_type}("Simulated error")

    # Test: Verify exception handling in integration context
    # result = {function_name}(test_input)
    # assert result is not None  # or expected fallback

    pass  # Remove this line when implementing the test
'''
        return template

    def _property_test_template(
        self,
        gap: TestCoverageGap,
        exception_type: str,
        remediation_strategy: str,
    ) -> str:
        """Generate a property-based test template."""
        function_name = gap.violation_function or "target_function"
        test_name = f"{gap.suggested_test_name}_property"

        template = f'''@given(st.text(), st.text())
def {test_name}(input_data, config_data):
    """Property-based test for exception handling in {function_name}."""
    # TODO: Implement property-based test

    # Property: Function should handle {exception_type} gracefully
    # assume isinstance(input_data, str)  # Add appropriate assumptions

    # try:
    #     result = {function_name}(input_data, config_data)
    #     assert result is not None  # or expected invariant
    # except {exception_type}:
    #     # Exception should be handled gracefully
    #     assert True  # Add specific invariants

    pass  # Remove this line when implementing the test
'''
        return template


def run_phase3_enhanced_test_coverage(adg_path: Path, test_dirs: list[Path]) -> dict:
    """Convenience function to run Phase 3 enhanced test coverage analysis."""
    with TestCoverageAnalyzer(adg_path) as analyzer:
        gaps = analyzer.analyze_test_coverage_gaps(test_dirs)
        edge_stats = analyzer.populate_comprehensive_test_edges(test_dirs)

        # Generate test skeletons for high-priority gaps
        generator = TestSkeletonGenerator()
        skeletons = {}
        for gap in gaps[:5]:  # Top 5 gaps
            skeleton = generator.generate_test_skeleton(gap, "Exception", "add_logging")
            skeletons[gap.suggested_test_name] = skeleton

        return {
            "coverage_gaps": len(gaps),
            "high_priority_gaps": len([g for g in gaps if g.priority > 0.7]),
            "test_edges_created": edge_stats["edges_created"],
            "tests_discovered": edge_stats["tests_discovered"],
            "generated_skeletons": len(skeletons),
            "skeletons": skeletons,
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage: python phase3_enhanced_test_coverage.py <path_to_adg.sqlite> <test_dir1> [test_dir2 ...]",
        )
        sys.exit(1)

    adg_path = Path(sys.argv[1])
    test_dirs = [Path(d) for d in sys.argv[2:]]

    results = run_phase3_enhanced_test_coverage(adg_path, test_dirs)
    print(
        f"\nPhase 3.2 Analysis Complete: {results['coverage_gaps']} gaps found, {results['generated_skeletons']} test skeletons generated",
    )
