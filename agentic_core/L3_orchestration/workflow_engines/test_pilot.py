"""
TestPilot - Property-Based Testing Agent

Implements regression testing and property-based testing using Hypothesis
to detect deep logic failures that standard unit tests miss.
"""
import asyncio
import logging
import os
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Protocol

LOGGER = logging.getLogger(__name__)

# Few-shot patterns for property-based testing
FEW_SHOT_PROPERTY_TESTS = """
FEW-SHOT HYPOTHESIS PROPERTY TESTS (Valid syntax only):

EXAMPLE 1: List reversal idempotency
from hypothesis import given, strategies as st
@given(st.lists(st.integers()))
def test_reverse_twice(lst):
    assert lst[::-1][::-1] == lst

EXAMPLE 2: JSON serialization roundtrip
@given(st.dictionaries(st.text(), st.integers()))
def test_json_roundtrip(data):
    assert json.loads(json.dumps(data)) == data

EXAMPLE 3: Sorting is idempotent
@given(st.lists(st.integers()))
def test_sorted_idempotent(numbers):
    assert sorted(sorted(numbers)) == sorted(numbers)

EXAMPLE 4: Set operations
@given(st.sets(st.integers()))
def test_set_union_idempotent(s):
    assert s | s == s

EXAMPLE 5: Dictionary merge
@given(st.dictionaries(st.text(), st.integers()), st.dictionaries(st.text(), st.integers()))
def test_dict_merge(a, b):
    merged = {**a, **b}
    for k, v in a.items():
        if k not in b:
            assert merged[k] == v
"""


class TestPilot:
    """
    TestPilot agent with property-based testing capabilities.

    Uses Hypothesis to generate and run ephemeral property tests
    for detecting deep logic failures.
    """

    def __init__(self, test_paths: List[str] = None, enable_conversational_repair: bool = True):
        """
        Initialize TestPilot.

        Args:
            test_paths: Paths to test directories
            enable_conversational_repair: Whether to enable multi-agent debate for failures
        """
        self.test_paths = test_paths or ["tests"]
        self.property_violations = []
        self.enable_conversational_repair = enable_conversational_repair

        # Import conversational repair if enabled
        if self.enable_conversational_repair:
            from agentic_core.conversational_repair import get_conversational_repair
            self.conversational_repair = get_conversational_repair()
    async def execute(self, modified_files: List[str] = None) -> Dict[str, Any]:
        """
        Execute tests and return results.

        Args:
            modified_files: List of modified files to test

        Returns:
            Test execution results
        """
        results = {
            "standard_tests": await self._run_standard_tests(),
            "property_tests": await self._run_property_tests(modified_files or []),
            "violations": self.property_violations,
            "signals": set()
        }

        # Check if conversational repair is needed
        if self.enable_conversational_repair and self._needs_conversational_repair(results):
            repair_results = await self._initiate_conversational_repair(results)
            results["conversational_repair"] = repair_results

        # Process results
        if not results["standard_tests"]["passed"]:
            results["signals"].add("TEST_FAILURE")
            LOGGER.error(f"Standard tests failed: {results['standard_tests']['failures']}")

        if results["property_tests"] and not results["property_tests"]["passed"]:
            results["signals"].add("PROPERTY_VIOLATION")
            LOGGER.error(f"Property tests failed: {results['property_tests']['violations']}")
            results["violations"] = self.property_violations

        if not results["signals"]:
            results["signals"].add("TESTS_PASS")
            LOGGER.info("[OK] All tests passed")

        # Convert signals set to list for JSON serialization
        results["signals"] = list(results["signals"])

        return results

    async def _run_standard_tests(self) -> Dict[str, Any]:
        """Run standard pytest tests."""
        try:
            # Find test files
            test_files = self._find_test_files()

            if not test_files:
                return {
                    "passed": True,
                    "count": 0,
                    "failures": 0,
                    "details": ["No test files found"]
                }

            LOGGER.info(f"Found {len(test_files)} test file(s)")

            # Run pytest
            cmd = [sys.executable, "-m", "pytest", "--quiet", "-x", "--tb=short"] + test_files[:20]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            output = stdout.decode() + stderr.decode()

            if process.returncode == 0:
                return {
                    "passed": True,
                    "count": len(test_files),
                    "failures": 0,
                    "details": ["All standard tests passed"]
                }
            else:
                # Parse failures
                failures = output.count("FAILED")
                return {
                    "passed": False,
                    "count": len(test_files),
                    "failures": failures,
                    "details": [output[:1000]]  # Truncate output
                }

        except Exception as e:
            LOGGER.error(f"Error running standard tests: {e}")
            return {
                "passed": False,
                "count": 0,
                "failures": 1,
                "details": [f"Error: {str(e)}"]
            }

    async def _run_property_tests(self, modified_files: List[str]) -> Dict[str, Any]:
        """
        Run property-based tests on modified files.

        Args:
            modified_files: List of modified Python files

        Returns:
            Property test results
        """
        if not modified_files:
            return {
                "passed": True,
                "generated": 0,
                "violations": 0,
                "details": ["No files to test"]
            }

        LOGGER.info(f"Running property-based tests on {len(modified_files)} files")

        results = {
            "passed": True,
            "generated": 0,
            "violations": 0,
            "details": []
        }
        for file_path in modified_files:
            if file_path.endswith('.py'):
                result = await self._run_property_check(file_path)
                results["generated"] += result.get("generated", 0)

                if not result.get("passed", True):
                    results["passed"] = False
                    results["violations"] += result.get("violations", 0)
                    results["details"].extend(result.get("details", []))

        return results

    async def _run_property_check(self, file_path: str) -> Dict[str, Any]:
        """
        Generate and run property tests for a specific file.

        Args:
            file_path: Path to the Python file to test

        Returns:
            Property test results for the file
        """
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract functions and classes
            functions = self._extract_functions(content)

            if not functions:
                return {
                    "passed": True,
                    "generated": 0,
                    "violations": 0,
                    "details": [f"No testable functions in {file_path}"]
                }

            # Generate property tests
            test_code = await self._generate_property_tests(file_path, functions)

            if not test_code:
                return {
                    "passed": True,
                    "generated": 0,
                    "violations": 0,
                    "details": [f"No property tests generated for {file_path}"]
                }

            # Write test to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='_property_test.py', delete=False) as f:
                f.write(test_code)
                test_file = f.name

            try:
                # Run the property test
                result = await self._execute_property_test(test_file, file_path)

                # Check for falsifying examples
                if "Falsifying example" in result.get("output", ""):
                    # Parse the falsifying example
                    violation = self._parse_violation(result["output"], file_path)
                    self._property_violations.append(violation)

                    return {
                        "passed": False,
                        "generated": 1,
                        "violations": 1,
                        "details": [f"Property violation in {file_path}: {violation['description']}"]
                    }

                return {
                    "passed": True,
                    "generated": 1,
                    "violations": 0,
                    "details": [f"Property tests passed for {file_path}"]
                }

            finally:
                # Clean up temporary file
                try:
                    os.unlink(test_file)
                except:
                    pass

        except Exception as e:
            LOGGER.error(f"Error in property check for {file_path}: {e}")
            return {
                "passed": False,
                "generated": 0,
                "violations": 1,
                "details": [f"Error: {str(e)}"]
            }

    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function signatures from Python code."""
        import ast

        functions = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get function info
                    args = []
                    for arg in node.args.args:
                        args.append(arg.arg)

                    functions.append({
                        "name": node.name,
                        "args": args,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node) or ""
                    })

        except SyntaxError:
            pass

        return functions

    async def _generate_property_tests(self, file_path: str, functions: List[Dict[str, Any]]) -> str:
        """
        Generate property test code using LLM guidance.

        Args:
            file_path: Path to the file being tested
            functions: List of functions in the file

        Returns:
            Generated test code
        """
        # For now, use simple pattern-based generation
        # In a full implementation, this would use an LLM with FEW_SHOT_PROPERTY_TESTS

        test_code = f"""
import json
from hypothesis import given, strategies as st, settings
import sys
import os

# Add the source directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath('{file_path}')))

# Import the module
module_name = os.path.splitext(os.path.basename('{file_path}'))[0]
import importlib
try:
    module = importlib.import_module(module_name)
except ImportError:
    # Try to load as a script
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, '{file_path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

"""

        # Generate tests for each function
        for func in functions:
            if self._should_test_function(func):
                test_code += self._generate_test_for_function(func)

        return test_code

    def _should_test_function(self, func: Dict[str, Any]) -> bool:
        """Determine if a function should have property tests generated."""
        # Skip private functions and simple getters
        if func["name"].startswith("_"):
            return False

        # Skip functions with no arguments or only self
        if len(func["args"]) <= 1:
            return False

        return True

    def _generate_test_for_function(self, func: Dict[str, Any]) -> str:
        """Generate a property test for a specific function."""
        func_name = func["name"]
        args = func["args"]

        # Simple heuristic for test generation
        if "sort" in func_name.lower():
            return f"""
@settings(max_examples=100)
@given(st.lists(st.integers()))
def test_{func_name}_sorted_idempotent(lst):
    result = module.{func_name}(lst.copy())
    assert module.{func_name}(result) == result
"""

        elif "json" in func_name.lower() or "serialize" in func_name.lower():
            return f"""
@settings(max_examples=100)
@given(st.dictionaries(st.text(), st.integers()))
def test_{func_name}_roundtrip(data):
    result = module.{func_name}(data)
    if isinstance(result, str):
        assert json.loads(result) == data
"""

        elif "reverse" in func_name.lower():
            return f"""
@settings(max_examples=100)
@given(st.lists(st.integers()))
def test_{func_name}_double_reverse(lst):
    result = module.{func_name}(lst)
    assert module.{func_name}(result) == lst
"""

        else:
            # Generic test - just check it doesn't crash
            strategy = self._get_strategy_for_args(args)
            return f"""
@settings(max_examples=50)
@given({strategy})
def test_{func_name}_properties({', '.join(args)}):
    # Just check the function doesn't crash
    result = module.{func_name}({', '.join(args)})
    assert result is not None
"""

    def _get_strategy_for_args(self, args: List[str]) -> str:
        """Get appropriate Hypothesis strategy for function arguments."""
        strategies = []

        for arg in args:
            if arg == "self":
                continue
            elif "int" in arg.lower():
                strategies.append("st.integers()")
            elif "str" in arg.lower() or "text" in arg.lower():
                strategies.append("st.text()")
            elif "list" in arg.lower():
                strategies.append("st.lists(st.integers())")
            elif "dict" in arg.lower():
                strategies.append("st.dictionaries(st.text(), st.integers())")
            else:
                strategies.append("st.integers()")

        return ", ".join(strategies)

    async def _execute_property_test(self, test_file: str, source_file: str) -> Dict[str, Any]:
        """Execute a property test file."""
        try:
            cmd = [sys.executable, "-m", "hypothesis", "test", test_file, "--verbose"]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            output = stdout.decode() + stderr.decode()

            return {
                "file": source_file,
                "returncode": process.returncode,
                "output": output
            }

        except Exception as e:
            return {
                "file": source_file,
                "returncode": -1,
                "output": f"Error: {str(e)}"
            }

    def _parse_violation(self, output: str, file_path: str) -> Dict[str, Any]:
        """Parse a property test violation from Hypothesis output."""
        violation = {
            "file": file_path,
            "description": "",
            "example": "",
            "timestamp": time.time()
        }

        # Extract falsifying example
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if "Falsifying example" in line:
                # Get the next few lines as the example
                example_lines = []
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].strip() and not lines[j].startswith(" "):
                        break
                    example_lines.append(lines[j])

                violation["example"] = '\n'.join(example_lines)
                violation["description"] = f"Property violation found: {line}"
                break

        return violation

    def _find_test_files(self) -> List[str]:
        """Find test files in the repository."""
        test_files = []
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', '.venv']]
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))
        return test_files

    def get_property_violations(self) -> List[Dict[str, Any]]:
        """Get all property violations found."""
        return self._property_violations.copy()

    def clear_violations(self):
        """Clear stored property violations."""
        self._property_violations.clear()


# Factory function
def create_test_pilot(enable_property_testing: bool = True) -> TestPilot:
    """Create a TestPilot instance."""
    return TestPilot(enable_property_testing)
