"""
Test Validator classification precision.

Validates:
- Validators require AST evidence (class endswith Validator)
- No filename-only matching
- validate()/verify() function exports considered
"""

import ast

import pytest


def is_validator_by_ast(content: str) -> bool:
    """
    Check if content defines a Validator class using AST.

    Returns True only if:
    - Class name ends with 'Validator', OR
    - Module exports validate()/verify() function AND is in validators/
    """
    try:
        tree = ast.parse(content)

        # Check for Validator class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.endswith("Validator"):
                    return True

        # Check for validate/verify functions at module level
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name in ("validate", "verify"):
                    return True

        return False
    except SyntaxError:
        return False


def is_validator_by_filename_only(filename: str) -> bool:
    """
    WRONG: Check if file is validator by filename only.

    This is the pattern we want to AVOID.
    """
    keywords = ["validate", "verify", "check", "validator"]
    return any(kw in filename.lower() for kw in keywords)


class TestValidatorByAST:
    """Tests for AST-based Validator detection."""

    def test_validator_class_detected(self):
        """Class ending with Validator should be detected."""
        content = """
class MyValidator:
    def validate(self, data):
        return True
"""
        assert is_validator_by_ast(content)

    def test_validate_function_detected(self):
        """Module-level validate() function should be detected."""
        content = '''
def validate(data):
    """Validate the data."""
    return True
'''
        assert is_validator_by_ast(content)

    def test_verify_function_detected(self):
        """Module-level verify() function should be detected."""
        content = '''
def verify(data):
    """Verify the data."""
    return True
'''
        assert is_validator_by_ast(content)

    def test_non_validator_not_detected(self):
        """Regular class should not be detected as Validator."""
        content = """
class RegularClass:
    def process(self, data):
        return data
"""
        assert not is_validator_by_ast(content)

    def test_agent_not_detected_as_validator(self):
        """Agent class should not be detected as Validator."""
        content = """
class MyAgent:
    def execute(self):
        pass
"""
        assert not is_validator_by_ast(content)


class TestFilenameOnlyMatching:
    """Tests showing why filename-only matching is wrong."""

    def test_filename_matching_false_positive_validate(self):
        """Filename with 'validate' might not be a Validator."""
        # File named 'validate_helper.py' but contains no Validator
        content = '''
def helper_function():
    """Just a helper, not a validator."""
    pass
'''
        filename = "validate_helper.py"

        # Filename-only says yes (WRONG)
        assert is_validator_by_filename_only(filename)

        # AST says no (CORRECT)
        assert not is_validator_by_ast(content)

    def test_filename_matching_false_positive_check(self):
        """Filename with 'check' might not be a Validator."""
        content = '''
def check_syntax(code):
    """Check syntax but not a validator."""
    return True
'''
        filename = "check_syntax_util.py"

        # Filename-only says yes (WRONG)
        assert is_validator_by_filename_only(filename)

        # AST says no (CORRECT) - check_syntax is not validate/verify
        assert not is_validator_by_ast(content)

    def test_filename_matching_false_negative(self):
        """Validator class in file without 'validator' in name."""
        content = """
class InputValidator:
    def validate(self, data):
        return True
"""
        filename = "input_processor.py"  # No validator keywords

        # Filename-only says no (WRONG for this case)
        assert not is_validator_by_filename_only(filename)

        # AST says yes (CORRECT)
        assert is_validator_by_ast(content)


class TestValidatorClassNaming:
    """Tests for Validator class naming conventions."""

    @pytest.mark.parametrize(
        "class_name,expected",
        [
            ("MyValidator", True),
            ("InputValidator", True),
            ("SchemaValidator", True),
            ("DataValidator", True),
            ("MyAgent", False),
            ("ValidatorHelper", False),  # Helper, not Validator
            ("PreValidator", True),  # DOES end with Validator
            ("Validator", True),  # Just "Validator" is valid
        ],
    )
    def test_validator_class_name_patterns(self, class_name: str, expected: bool):
        """Test various Validator class name patterns."""
        content = f"""
class {class_name}:
    pass
"""
        result = is_validator_by_ast(content)
        assert result == expected, f"{class_name} should be {expected}"


class TestValidatorInContext:
    """Tests for Validator detection in context."""

    def test_validator_in_validators_folder(self, tmp_path):
        """Validator in validators/ folder should be detected."""
        validators_dir = tmp_path / "validators"
        validators_dir.mkdir()

        validator_file = validators_dir / "my_validator.py"
        validator_file.write_text("""
class MyValidator:
    def validate(self, data):
        return True
""")

        content = validator_file.read_text()
        assert is_validator_by_ast(content)

    def test_non_validator_in_validators_folder(self, tmp_path):
        """Non-Validator in validators/ folder should NOT be detected."""
        validators_dir = tmp_path / "validators"
        validators_dir.mkdir()

        helper_file = validators_dir / "helper.py"
        helper_file.write_text("""
def helper_function():
    pass
""")

        content = helper_file.read_text()
        assert not is_validator_by_ast(content)
