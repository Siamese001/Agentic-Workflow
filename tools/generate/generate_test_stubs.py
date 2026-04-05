"""Generate test stubs from source files."""

import ast
import pathlib


class TestStubGenerator:
    """Generate minimal test stubs for source files."""

    def __init__(self):
        self.templates = {
            "function": '''    def test_{name}(self):
        """Test {name} function."""
        from {module} import {name}
        # TODO: Implement actual test
        result = {name}()
        self.assertIsNotNone(result)
''',
            "class": '''    def test_{class_name}_init(self):
        """Test {class_name} initialization."""
        from {module} import {class_name}
        # TODO: Implement actual test
        instance = {class_name}()
        self.assertIsNotNone(instance)
''',
            "method": '''    def test_{class_name}_{method_name}(self):
        """Test {class_name}.{method_name} method."""
        from {module} import {class_name}
        # TODO: Implement actual test
        instance = {class_name}()
        result = instance.{method_name}()
        self.assertIsNotNone(result)
''',
        }

    def analyze_source_file(self, source_path: pathlib.Path) -> dict:
        """Analyze a source file and extract testable items."""
        try:
            with open(source_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            analysis = {"functions": [], "classes": [], "module_name": self._get_module_name(source_path)}

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions
                    if not node.name.startswith("_"):
                        analysis["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(
                        {
                            "name": node.name,
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
                            ],
                        }
                    )

            return analysis

        except Exception as e:
            print(f"Error analyzing {source_path}: {e}")
            return {"functions": [], "classes": [], "module_name": ""}

    def _get_module_name(self, source_path: pathlib.Path) -> str:
        """Convert file path to module name."""
        # Convert path to module import string
        parts = source_path.parts
        if "agentic_core" in parts:
            idx = parts.index("agentic_core")
            return ".".join(parts[idx:-1])  # Exclude filename
        return str(source_path.parent).replace("/", ".")

    def generate_test_stub(self, source_path: pathlib.Path, test_path: pathlib.Path) -> str:
        """Generate a test stub for a source file."""
        analysis = self.analyze_source_file(source_path)

        if not analysis["functions"] and not analysis["classes"]:
            return None

        # Read existing test file to preserve structure
        test_content = self._read_test_file(test_path)

        # Generate test methods
        test_methods = []

        # Add function tests (limit to 2 most important)
        for func_name in analysis["functions"][:2]:
            test_methods.append(
                self.templates["function"].format(name=func_name, module=analysis["module_name"])
            )

        # Add class tests (limit to 2 most important)
        for class_info in analysis["classes"][:2]:
            # Test class initialization
            test_methods.append(
                self.templates["class"].format(class_name=class_info["name"], module=analysis["module_name"])
            )

            # Test one key method if available
            if class_info["methods"]:
                method_name = class_info["methods"][0]
                test_methods.append(
                    self.templates["method"].format(
                        class_name=class_info["name"], method_name=method_name, module=analysis["module_name"]
                    )
                )

        # Replace placeholder test class with generated tests
        # Handle both unittest and pytest styles
        placeholder_start = test_content.find("class PlaceholderTest(unittest.TestCase):")
        pytest_start = test_content.find("class Test")

        if placeholder_start == -1 and pytest_start == -1:
            return None

        # For pytest, find the first test class
        if placeholder_start == -1:
            placeholder_start = pytest_start
            # Find end of class
            placeholder_end = test_content.find("\n\n", placeholder_start)
            if placeholder_end == -1:
                placeholder_end = len(test_content)
        else:
            placeholder_end = test_content.find("\n\nif __name__ == '__main__':")
            if placeholder_end == -1:
                placeholder_end = len(test_content)

        # Build new test class
        # Use unittest or pytest based on what's in the file
        if "import unittest" in test_content:
            new_test_class = f'''class GeneratedTest(unittest.TestCase):
    """Generated test class for {analysis["module_name"]}."""

{"".join(test_methods)}'''
        else:
            # Use pytest style
            pytest_methods = []
            for method in test_methods:
                # Convert unittest methods to pytest
                method = method.replace("self.", "")
                method = method.replace("self.assert", "assert")
                pytest_methods.append(method)

            new_test_class = f'''class GeneratedTest:
    """Generated test class for {analysis["module_name"]}."""

{"".join(pytest_methods)}'''

        # Replace placeholder
        new_content = test_content[:placeholder_start] + new_test_class + test_content[placeholder_end:]

        return new_content

    def _read_test_file(self, test_path: pathlib.Path) -> str:
        """Read existing test file content."""
        if test_path.exists():
            with open(test_path, encoding="utf-8") as f:
                return f.read()

        # Return basic test file structure if doesn't exist
        return '''"""Placeholder test file - syntax fixed."""

import unittest

class PlaceholderTest(unittest.TestCase):
    """Placeholder test class."""

    def test_placeholder_1(self):
        """Placeholder test method 1."""
        self.assertTrue(True)

    def test_placeholder_2(self):
        """Placeholder test method 2."""
        self.assertEqual(1 + 1, 2)

    def test_placeholder_3(self):
        """Placeholder test method 3."""
        self.assertIsNotNone(None)


if __name__ == '__main__':
    unittest.main()
'''


def generate_stub(source_file: str, test_file: str) -> bool:
    """Generate a test stub for a source file.

    Args:
        source_file: Path to the source file
        test_file: Path to the test file to update

    Returns:
        True if successful, False otherwise
    """
    generator = TestStubGenerator()
    source_path = pathlib.Path(source_file)
    test_path = pathlib.Path(test_file)

    new_content = generator.generate_test_stub(source_path, test_path)

    if new_content:
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True

    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python generate_test_stubs.py <source_file> <test_file>")
        sys.exit(1)

    success = generate_stub(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
