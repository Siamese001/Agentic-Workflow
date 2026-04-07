"""
Test Shared Infrastructure Validators.

SVP Infrastructure Testing - Core utilities and validators.
"""
import unittest

from apps_shared.validators.cache_validator import (
    generate_llm_cache_key,
    generate_llm_cache_key_with_fingerprint,
    should_invalidate_cache,
)
from apps_shared.validators.validation_validator import ExecutionResult, Validation, run_process


class TestCacheValidator(unittest.TestCase):
    """Test cases for cache validation utilities."""

    def test_generate_llm_cache_key_deterministic(self):
        """Test cache key generation is deterministic."""
        model = "gpt-4o"
        messages = [{"role": "user", "content": "Hello"}]
        key1 = generate_llm_cache_key(model, messages)
        key2 = generate_llm_cache_key(model, messages)
        self.assertEqual(key1, key2)
        self.assertEqual(len(key1), 64)  # SHA-256 hex length

    def test_generate_llm_cache_key_different_inputs(self):
        """Test different inputs produce different keys."""
        key1 = generate_llm_cache_key("gpt-4o", [{"role": "user", "content": "Hello"}])
        key2 = generate_llm_cache_key("gpt-4", [{"role": "user", "content": "Hello"}])
        self.assertNotEqual(key1, key2)

    def test_generate_llm_cache_key_with_fingerprint(self):
        """Test cache key with fingerprint."""
        key = generate_llm_cache_key_with_fingerprint(
            "gpt-4o", [{"role": "user", "content": "Hello"}], "fp-123",
        )
        self.assertEqual(len(key), 64)

    def test_should_invalidate_cache_default(self):
        """Test cache invalidation logic."""
        result = should_invalidate_cache("some-key")
        self.assertFalse(result)  # Default is don't invalidate


class TestValidationValidator(unittest.TestCase):
    """Test cases for validation executor."""

    def test_execution_result_creation(self):
        """Test ExecutionResult dataclass."""
        result = ExecutionResult(success=True, data="test")
        self.assertTrue(result.success)
        self.assertEqual(result.data, "test")

    def test_validation_process_dict_success(self):
        """Test validation of dictionary."""
        validator = Validation()
        data = {"name": "Test", "value": 123}
        result = validator.process(data)
        self.assertTrue(result.success)

    def test_validation_process_dict_with_required_fields(self):
        """Test validation with required fields reports errors correctly."""
        validator = Validation(config={"required_fields": ["name", "value"]})
        data = {"name": "Test"}  # Missing "value"
        result = validator.process(data)
        self.assertTrue(result.success)  # Process succeeded
        self.assertIsInstance(result.data, dict)
        self.assertFalse(result.data["is_valid"])  # But validation failed
        self.assertIn("Missing required field: value", result.data["errors"])

    def test_validation_process_list(self):
        """Test validation of list."""
        validator = Validation()
        data = [1, 2, 3]
        result = validator.process(data)
        self.assertTrue(result.success)

    def test_validation_process_string(self):
        """Test validation of string."""
        validator = Validation()
        data = "test string"
        result = validator.process(data)
        self.assertTrue(result.success)

    def test_validation_process_number(self):
        """Test validation of number."""
        validator = Validation()
        data = 42
        result = validator.process(data)
        self.assertTrue(result.success)

    def test_validation_process_boolean(self):
        """Test validation of boolean."""
        validator = Validation()
        data = True
        result = validator.process(data)
        self.assertTrue(result.success)

    def test_validation_process_empty_string(self):
        """Test validation of empty string - edge case."""
        validator = Validation()
        data = ""
        result = validator.process(data)
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, dict)
        self.assertTrue(result.data["is_valid"])  # Empty string is valid by default

    def test_validation_process_empty_list(self):
        """Test validation of empty list - edge case."""
        validator = Validation()
        data = []
        result = validator.process(data)
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, dict)
        self.assertTrue(result.data["is_valid"])  # Empty list is valid by default

    def test_validation_process_empty_dict(self):
        """Test validation of empty dict - edge case."""
        validator = Validation()
        data = {}
        result = validator.process(data)
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, dict)
        self.assertTrue(result.data["is_valid"])  # Empty dict is valid by default

    def test_validation_process_none_handled(self):
        """Test that None input is handled gracefully."""
        validator = Validation()
        result = validator.process(None)
        # None is treated as valid by default (permissive validation)
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, dict)
        self.assertTrue(result.data["is_valid"])
        self.assertIsNone(result.data["validated_data"])

    def test_validation_process_string_max_length_boundary(self):
        """Test string max_length boundary enforcement."""
        validator = Validation(config={"max_string_length": 10})
        # Exactly at boundary
        data_exact = "exactlyten"
        result = validator.process(data_exact)
        self.assertTrue(result.success)
        self.assertTrue(result.data["is_valid"])

        # One over boundary
        data_over = "exactlyten!"
        result = validator.process(data_over)
        self.assertTrue(result.success)  # Process succeeds
        self.assertFalse(result.data["is_valid"])  # But validation fails
        self.assertIn("String exceeds maximum length of 10", result.data["errors"])

    def test_run_process_entry_point(self):
        """Test module-level entry point."""
        result = run_process({"test": "data"})
        self.assertIsInstance(result, ExecutionResult)


if __name__ == "__main__":
    unittest.main()
