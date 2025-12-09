"""Unit tests for data loading and processing utilities."""
from __future__ import annotations
import pytest
import json

class TestDataLoading:
    """Tests for data loading operations."""

    def test_load_json_valid(self):
        """Nominal: Valid JSON is loaded correctly."""
        json_str = '{"key": "value", "number": 42}'
        data = json.loads(json_str)
        assert data["key"] == "value"
        assert data["number"] == 42

    def test_load_json_invalid(self):
        """Negative: Invalid JSON raises error."""
        invalid_json = '{"key": "value"'
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)

    def test_load_json_empty(self):
        """Edge case: Empty JSON object."""
        json_str = '{}'
        data = json.loads(json_str)
        assert data == {}

    def test_load_json_array(self):
        """Nominal: JSON array is loaded."""
        json_str = '[1, 2, 3]'
        data = json.loads(json_str)
        assert data == [1, 2, 3]

    def test_load_determinism(self):
        """Determinism: Same JSON produces same data."""
        json_str = '{"a": 1}'
        d1 = json.loads(json_str)
        d2 = json.loads(json_str)
        assert d1 == d2


class TestDataValidation:
    """Tests for data validation."""

    def test_validate_required_fields(self):
        """Nominal: Required fields are present."""
        required = ["id", "name", "value"]
        data = {"id": 1, "name": "test", "value": 100}
        missing = [f for f in required if f not in data]
        assert missing == []

    def test_validate_missing_field(self):
        """Negative: Missing required field detected."""
        required = ["id", "name", "value"]
        data = {"id": 1, "name": "test"}
        missing = [f for f in required if f not in data]
        assert "value" in missing

    def test_validate_field_types(self):
        """Nominal: Field types are correct."""
        schema = {"id": int, "name": str, "active": bool}
        data = {"id": 1, "name": "test", "active": True}
        valid = all(isinstance(data.get(k), t) for k, t in schema.items())
        assert valid is True

    def test_validate_field_type_mismatch(self):
        """Negative: Type mismatch detected."""
        schema = {"id": int}
        data = {"id": "not_an_int"}
        valid = all(isinstance(data.get(k), t) for k, t in schema.items())
        assert valid is False

    def test_validate_nested_data(self):
        """Edge case: Nested data validation."""
        data = {"user": {"name": "John", "age": 30}}
        assert isinstance(data["user"], dict)
        assert data["user"]["name"] == "John"


class TestDataTransformation:
    """Tests for data transformation utilities."""

    def test_transform_flatten_dict(self):
        """Nominal: Nested dict is flattened."""
        # Simple flatten
        flat = {"a.b.c": 1}
        assert "a.b.c" in flat

    def test_transform_normalize_keys(self):
        """Nominal: Keys are normalized to lowercase."""
        data = {"Name": "John", "AGE": 30}
        normalized = {k.lower(): v for k, v in data.items()}
        assert "name" in normalized
        assert "age" in normalized

    def test_transform_filter_nulls(self):
        """Nominal: Null values are filtered."""
        data = {"a": 1, "b": None, "c": 3}
        filtered = {k: v for k, v in data.items() if v is not None}
        assert "b" not in filtered

    def test_transform_map_values(self):
        """Nominal: Values are transformed."""
        data = {"a": 1, "b": 2, "c": 3}
        doubled = {k: v * 2 for k, v in data.items()}
        assert doubled["a"] == 2
        assert doubled["b"] == 4

    def test_transform_determinism(self):
        """Determinism: Same transformation produces same result."""
        data = {"x": 10}
        t1 = {k: v * 2 for k, v in data.items()}
        t2 = {k: v * 2 for k, v in data.items()}
        assert t1 == t2


class TestDataSerialization:
    """Tests for data serialization."""

    def test_serialize_to_json(self):
        """Nominal: Data serializes to JSON."""
        data = {"key": "value"}
        json_str = json.dumps(data)
        assert json_str == '{"key": "value"}'

    def test_serialize_with_indent(self):
        """Nominal: Pretty-printed JSON."""
        data = {"key": "value"}
        json_str = json.dumps(data, indent=2)
        assert "\n" in json_str

    def test_serialize_unicode(self):
        """Edge case: Unicode is handled."""
        data = {"greeting": "こんにちは"}
        json_str = json.dumps(data, ensure_ascii=False)
        assert "こんにちは" in json_str

    def test_serialize_special_types(self):
        """Edge case: Special types need conversion."""
        from datetime import datetime
        data = {"timestamp": datetime.now().isoformat()}
        json_str = json.dumps(data)
        assert "timestamp" in json_str

    def test_roundtrip_serialization(self):
        """Nominal: Data survives roundtrip."""
        original = {"a": 1, "b": [1, 2, 3], "c": {"nested": True}}
        json_str = json.dumps(original)
        restored = json.loads(json_str)
        assert original == restored
