"""
Phase 4 Optimization Tests - JSON Parser
Tests for native Python JSON parsing utilities.
"""

import pytest
from apps_shared.utils.json_parser_validator import JsonParser, ParseResult


class TestParseResult:
    """Test ParseResult dataclass."""

    def test_parse_result_creation(self):
        """Test creating ParseResult."""
        result = ParseResult(success=True, data={"key": "value"}, errors=[], metadata={})

        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.errors == []


class TestJsonParser:
    """Test JsonParser functionality."""

    def test_parse_json_valid(self):
        """Test parsing valid JSON."""
        json_string = '{"name": "test", "value": 42}'
        result = JsonParser.parse_json(json_string)

        assert result.success is True
        assert result.data["name"] == "test"
        assert result.data["value"] == 42

    def test_parse_json_invalid(self):
        """Test parsing invalid JSON."""
        json_string = '{"name": "test", invalid}'
        result = JsonParser.parse_json(json_string)

        assert result.success is False
        assert len(result.errors) > 0

    def test_parse_json_array(self):
        """Test parsing JSON array."""
        json_string = "[1, 2, 3, 4, 5]"
        result = JsonParser.parse_json(json_string)

        assert result.success is True
        assert result.data == [1, 2, 3, 4, 5]

    def test_safe_get_simple(self):
        """Test safe get with simple path."""
        data = {"user": {"name": "John", "age": 30}}
        result = JsonParser.safe_get(data, "user.name")

        assert result == "John"

    def test_safe_get_nested(self):
        """Test safe get with nested path."""
        data = {"user": {"profile": {"email": "test@example.com"}}}
        result = JsonParser.safe_get(data, "user.profile.email")

        assert result == "test@example.com"

    def test_safe_get_missing_key(self):
        """Test safe get with missing key."""
        data = {"user": {"name": "John"}}
        result = JsonParser.safe_get(data, "user.email", default="N/A")

        assert result == "N/A"

    def test_safe_set_simple(self):
        """Test safe set with simple path."""
        data = {}
        JsonParser.safe_set(data, "user.name", "John")

        assert data["user"]["name"] == "John"

    def test_safe_set_nested(self):
        """Test safe set with nested path."""
        data = {}
        JsonParser.safe_set(data, "user.profile.email", "test@example.com")

        assert data["user"]["profile"]["email"] == "test@example.com"

    def test_merge_dicts_shallow(self):
        """Test shallow dictionary merge."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = JsonParser.merge_dicts(dict1, dict2, deep=False)

        assert result["a"] == 1
        assert result["b"] == 3
        assert result["c"] == 4

    def test_merge_dicts_deep(self):
        """Test deep dictionary merge."""
        dict1 = {"user": {"name": "John", "age": 30}}
        dict2 = {"user": {"age": 31, "email": "john@example.com"}}
        result = JsonParser.merge_dicts(dict1, dict2, deep=True)

        assert result["user"]["name"] == "John"
        assert result["user"]["age"] == 31
        assert result["user"]["email"] == "john@example.com"

    def test_flatten_dict_simple(self):
        """Test flattening simple nested dictionary."""
        data = {"user": {"name": "John", "age": 30}}
        result = JsonParser.flatten_dict(data)

        assert result["user.name"] == "John"
        assert result["user.age"] == 30

    def test_flatten_dict_with_list(self):
        """Test flattening dictionary with list."""
        data = {"items": [1, 2, 3]}
        result = JsonParser.flatten_dict(data)

        assert result["items.0"] == 1
        assert result["items.1"] == 2
        assert result["items.2"] == 3

    def test_unflatten_dict_simple(self):
        """Test unflattening dictionary."""
        data = {"user.name": "John", "user.age": 30}
        result = JsonParser.unflatten_dict(data)

        assert result["user"]["name"] == "John"
        assert result["user"]["age"] == 30

    def test_filter_keys_include(self):
        """Test filtering keys to include."""
        data = {"a": 1, "b": 2, "c": 3}
        result = JsonParser.filter_keys(data, ["a", "c"], include=True)

        assert "a" in result
        assert "b" not in result
        assert "c" in result

    def test_filter_keys_exclude(self):
        """Test filtering keys to exclude."""
        data = {"a": 1, "b": 2, "c": 3}
        result = JsonParser.filter_keys(data, ["b"], include=False)

        assert "a" in result
        assert "b" not in result
        assert "c" in result

    def test_validate_schema_valid(self):
        """Test schema validation with valid data."""
        data = {"name": "John", "age": 30, "active": True}
        schema = {"name": str, "age": int, "active": bool}
        result = JsonParser.validate_schema(data, schema)

        assert result.success is True

    def test_validate_schema_missing_key(self):
        """Test schema validation with missing key."""
        data = {"name": "John"}
        schema = {"name": str, "age": int}
        result = JsonParser.validate_schema(data, schema)

        assert result.success is False
        assert any("Missing" in error for error in result.errors)

    def test_validate_schema_wrong_type(self):
        """Test schema validation with wrong type."""
        data = {"name": "John", "age": "thirty"}
        schema = {"name": str, "age": int}
        result = JsonParser.validate_schema(data, schema)

        assert result.success is False
        assert any("wrong type" in error for error in result.errors)

    def test_extract_values_simple(self):
        """Test extracting values from simple structure."""
        data = {"user": {"id": 1}, "admin": {"id": 2}}
        result = JsonParser.extract_values(data, "id")

        assert result == [1, 2]

    def test_extract_values_nested(self):
        """Test extracting values from nested structure."""
        data = {"users": [{"name": "John", "id": 1}, {"name": "Jane", "id": 2}]}
        result = JsonParser.extract_values(data, "name")

        assert result == ["John", "Jane"]

    def test_transform_keys_simple(self):
        """Test transforming keys."""
        data = {"first_name": "John", "last_name": "Doe"}
        result = JsonParser.transform_keys(data, str.upper)

        assert "FIRST_NAME" in result
        assert "LAST_NAME" in result

    def test_transform_keys_nested(self):
        """Test transforming nested keys."""
        data = {"user_data": {"first_name": "John"}}
        result = JsonParser.transform_keys(data, str.upper)

        assert "USER_DATA" in result
        assert "FIRST_NAME" in result["USER_DATA"]

    def test_to_camel_case(self):
        """Test converting to camelCase."""
        result = JsonParser.to_camel_case("user_name")

        assert result == "userName"

    def test_to_camel_case_multiple_words(self):
        """Test converting multiple words to camelCase."""
        result = JsonParser.to_camel_case("user_first_name")

        assert result == "userFirstName"

    def test_to_snake_case(self):
        """Test converting to snake_case."""
        result = JsonParser.to_snake_case("userName")

        assert result == "user_name"

    def test_to_snake_case_multiple_words(self):
        """Test converting multiple words to snake_case."""
        result = JsonParser.to_snake_case("userFirstName")

        assert result == "user_first_name"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
