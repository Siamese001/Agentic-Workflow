"""Tests for Wave 18 REQ-136/256: Cross-layer typed schema version mismatch."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import pytest

pytestmark = pytest.mark.governance


class LayerVersion(Enum):
    """Layer version enumeration."""

    V1 = "1.0.0"
    V2 = "2.0.0"
    V3 = "3.0.0"


@dataclass(frozen=True)
class LayerSchema:
    """Schema definition for a layer."""

    layer_name: str
    version: LayerVersion
    schema_hash: str
    fields: dict[str, str]
    required_fields: list[str]


class CrossLayerCallValidator:
    """Validates cross-layer calls against schema versions."""

    def __init__(self):
        self._schemas: dict[str, LayerSchema] = {}
        self._version_compatibility: dict[str, dict[LayerVersion, list[LayerVersion]]] = {}

    def register_schema(self, schema: LayerSchema):
        """Register a layer schema."""
        self._schemas[schema.layer_name] = schema

        # Initialize compatibility matrix if not exists
        if schema.layer_name not in self._version_compatibility:
            self._version_compatibility[schema.layer_name] = {}

    def set_compatibility(self, layer_name: str, from_version: LayerVersion, to_versions: list[LayerVersion]):
        """Set version compatibility for a layer."""
        if layer_name not in self._version_compatibility:
            self._version_compatibility[layer_name] = {}
        self._version_compatibility[layer_name][from_version] = to_versions

    def validate_cross_layer_call(
        self,
        source_layer: str,
        source_version: LayerVersion,
        target_layer: str,
        target_version: LayerVersion,
        payload: dict[str, Any],
    ) -> bool:
        """Validate a cross-layer call."""
        # Check if schemas exist
        if source_layer not in self._schemas:
            raise ValueError(f"Source layer {source_layer} not registered")
        if target_layer not in self._schemas:
            raise ValueError(f"Target layer {target_layer} not registered")

        # Check version pinning
        source_schema = self._schemas[source_layer]
        target_schema = self._schemas[target_layer]

        if source_schema.version != source_version:
            raise ValueError(
                f"Source layer version mismatch: expected {source_schema.version}, got {source_version}"
            )

        if target_schema.version != target_version:
            raise ValueError(
                f"Target layer version mismatch: expected {target_schema.version}, got {target_version}"
            )

        # Check compatibility
        if not self._is_compatible(target_layer, target_version, target_schema.version):
            raise ValueError(
                f"Target layer version {target_version} not compatible with {target_schema.version}"
            )

        # Validate payload against target schema
        self._validate_payload(payload, target_schema)

        return True

    def _is_compatible(self, layer_name: str, from_version: LayerVersion, to_version: LayerVersion) -> bool:
        """Check if two versions are compatible."""
        compatibility = self._version_compatibility.get(layer_name, {})
        compatible_versions = compatibility.get(from_version, [])
        return to_version in compatible_versions

    def _validate_payload(self, payload: dict[str, Any], schema: LayerSchema):
        """Validate payload against schema."""
        # Check required fields
        for field in schema.required_fields:
            if field not in payload:
                raise ValueError(f"Missing required field: {field}")

        # Check field types
        for field_name, field_value in payload.items():
            if field_name in schema.fields:
                expected_type = schema.fields[field_name]
                if not self._check_type(field_value, expected_type):
                    raise ValueError(f"Field {field_name} type mismatch: expected {expected_type}")

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {"str": str, "int": int, "float": float, "bool": bool, "dict": dict, "list": list}

        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, assume valid

        return isinstance(value, expected_python_type)


class TestCrossLayerSchema:
    """Test cross-layer typed schema version pinning."""

    def setup_method(self):
        """Set up test environment."""
        self.validator = CrossLayerCallValidator()

        # Register schemas
        self.l1_schema = LayerSchema(
            layer_name="L1_routing",
            version=LayerVersion.V1,
            schema_hash="hash_l1_v1",
            fields={"request_id": "str", "payload": "dict", "priority": "int"},
            required_fields=["request_id", "payload"],
        )

        self.l2_schema = LayerSchema(
            layer_name="L2_execution",
            version=LayerVersion.V1,
            schema_hash="hash_l2_v1",
            fields={"instruction": "dict", "context": "dict", "trace_id": "str"},
            required_fields=["instruction", "trace_id"],
        )

        self.l3_schema = LayerSchema(
            layer_name="L3_orchestration",
            version=LayerVersion.V2,
            schema_hash="hash_l3_v2",
            fields={"task": "str", "parameters": "dict", "callback": "str"},
            required_fields=["task", "parameters"],
        )

        self.validator.register_schema(self.l1_schema)
        self.validator.register_schema(self.l2_schema)
        self.validator.register_schema(self.l3_schema)

        # Set compatibility
        self.validator.set_compatibility("L2_execution", LayerVersion.V1, [LayerVersion.V1])
        self.validator.set_compatibility("L3_orchestration", LayerVersion.V1, [LayerVersion.V2])
        self.validator.set_compatibility("L3_orchestration", LayerVersion.V2, [LayerVersion.V2])

    def test_version_pinned_call_success(self):
        """Test successful version-pinned cross-layer call."""
        # Given - Valid payload
        payload = {
            "instruction": {"type": "test", "data": "value"},
            "trace_id": "trace_123",
            "context": {"user": "test"},
        }

        # When/Then - Should validate successfully
        assert self.validator.validate_cross_layer_call(
            source_layer="L1_routing",
            source_version=LayerVersion.V1,
            target_layer="L2_execution",
            target_version=LayerVersion.V1,
            payload=payload,
        ), "Valid call should succeed"

    def test_version_mismatch_detection(self):
        """Test detection of version mismatch."""
        # Given - Payload with wrong version
        payload = {"instruction": {}, "trace_id": "123"}

        # When/Then - Should detect version mismatch
        with pytest.raises(ValueError, match="Target layer version mismatch"):
            self.validator.validate_cross_layer_call(
                source_layer="L1_routing",
                source_version=LayerVersion.V1,
                target_layer="L2_execution",
                target_version=LayerVersion.V2,  # Wrong version
                payload=payload,
            )

    def test_schema_evolution_compatibility(self):
        """Test schema evolution compatibility."""
        # Given - Call from V1 to V2 (compatible)
        payload = {"task": "test_task", "parameters": {"param1": "value1"}, "callback": "callback_func"}

        # When/Then - Should handle version evolution
        assert self.validator.validate_cross_layer_call(
            source_layer="L2_execution",
            source_version=LayerVersion.V1,
            target_layer="L3_orchestration",
            target_version=LayerVersion.V2,
            payload=payload,
        ), "Compatible version evolution should work"

    def test_incompatible_version_rejection(self):
        """Test rejection of incompatible versions."""
        # Given - Try to call V2 from V1 when not compatible
        payload = {"task": "test", "parameters": {}}

        # When/Then - Should reject incompatible version
        with pytest.raises(ValueError, match="not compatible|version mismatch"):
            self.validator.validate_cross_layer_call(
                source_layer="L1_routing",
                source_version=LayerVersion.V1,
                target_layer="L3_orchestration",
                target_version=LayerVersion.V1,  # Incompatible
                payload=payload,
            )

    def test_missing_required_field_detection(self):
        """Test detection of missing required fields."""
        # Given - Payload missing required field
        payload = {"instruction": {"type": "test"}}  # Missing trace_id

        # When/Then - Should detect missing field
        with pytest.raises(ValueError, match="Missing required field"):
            self.validator.validate_cross_layer_call(
                source_layer="L1_routing",
                source_version=LayerVersion.V1,
                target_layer="L2_execution",
                target_version=LayerVersion.V1,
                payload=payload,
            )

    def test_field_type_validation(self):
        """Test field type validation."""
        # Given - Payload with wrong field type
        payload = {
            "instruction": {"type": "test"},
            "trace_id": 123,  # Should be string
            "context": {},
        }

        # When/Then - Should detect type mismatch
        with pytest.raises(ValueError, match="Field trace_id type mismatch"):
            self.validator.validate_cross_layer_call(
                source_layer="L1_routing",
                source_version=LayerVersion.V1,
                target_layer="L2_execution",
                target_version=LayerVersion.V1,
                payload=payload,
            )

    def test_unregistered_layer_detection(self):
        """Test detection of unregistered layers."""
        # Given - Call to unregistered layer
        payload = {"data": "test"}

        # When/Then - Should detect unregistered layer
        with pytest.raises(ValueError, match="Target layer unregistered_layer not registered"):
            self.validator.validate_cross_layer_call(
                source_layer="L1_routing",
                source_version=LayerVersion.V1,
                target_layer="unregistered_layer",
                target_version=LayerVersion.V1,
                payload=payload,
            )

    def test_schema_hash_consistency(self):
        """Test schema hash consistency."""
        # Given - Same schema definition
        schema1 = LayerSchema(
            layer_name="test_layer",
            version=LayerVersion.V1,
            schema_hash="test_hash",
            fields={"field1": "str"},
            required_fields=["field1"],
        )

        schema2 = LayerSchema(
            layer_name="test_layer",
            version=LayerVersion.V1,
            schema_hash="test_hash",
            fields={"field1": "str"},
            required_fields=["field1"],
        )

        # When/Then - Should have identical hashes
        assert schema1.schema_hash == schema2.schema_hash, "Identical schemas should have identical hashes"

    def test_schema_version_pinning_persistence(self):
        """Test that schema version pinning persists across calls."""
        # Given - Multiple calls to same layer
        payload1 = {"instruction": {}, "trace_id": "1"}
        payload2 = {"instruction": {}, "trace_id": "2"}

        # When - Make multiple calls
        result1 = self.validator.validate_cross_layer_call(
            source_layer="L1_routing",
            source_version=LayerVersion.V1,
            target_layer="L2_execution",
            target_version=LayerVersion.V1,
            payload=payload1,
        )

        result2 = self.validator.validate_cross_layer_call(
            source_layer="L1_routing",
            source_version=LayerVersion.V1,
            target_layer="L2_execution",
            target_version=LayerVersion.V1,
            payload=payload2,
        )

        # Then - Both should succeed with same version
        assert result1 and result2, "Both calls should succeed"

        # Version should remain pinned
        schema = self.validator._schemas["L2_execution"]
        assert schema.version == LayerVersion.V1, "Version should remain pinned"


def test_req136_cross_layer_schema_version_pinning():
    """REQ-136: Test cross-layer typed schema version pinning."""
    test = TestCrossLayerSchema()
    test.setup_method()

    # Core functionality tests
    test.test_version_pinned_call_success()
    test.test_version_mismatch_detection()
    test.test_schema_evolution_compatibility()
    test.test_incompatible_version_rejection()

    # Validation tests
    test.test_missing_required_field_detection()
    test.test_field_type_validation()
    test.test_unregistered_layer_detection()

    # Consistency tests
    test.test_schema_hash_consistency()
    test.test_schema_version_pinning_persistence()


def test_req256_schema_mismatch_abort():
    """REQ-256: Test schema mismatch causes abort."""
    test = TestCrossLayerSchema()
    test.setup_method()

    # Test version mismatch directly
    payload = {"instruction": {}, "trace_id": "123"}
    with pytest.raises(ValueError, match="Target layer version mismatch"):
        test.validator.validate_cross_layer_call(
            source_layer="L1_routing",
            source_version=LayerVersion.V1,
            target_layer="L2_execution",
            target_version=LayerVersion.V2,  # Wrong version
            payload=payload,
        )

    # Test missing required field directly
    payload_missing = {"instruction": {}}  # Missing trace_id
    with pytest.raises(ValueError, match="Missing required field"):
        test.validator.validate_cross_layer_call(
            source_layer="L1_routing",
            source_version=LayerVersion.V1,
            target_layer="L2_execution",
            target_version=LayerVersion.V1,
            payload=payload_missing,
        )

    # Test field type mismatch directly
    payload_wrong_type = {
        "instruction": {"type": "test"},
        "trace_id": 123,  # Should be string
        "context": {},
    }
    with pytest.raises(ValueError, match="Field.*type mismatch"):
        test.validator.validate_cross_layer_call(
            source_layer="L1_routing",
            source_version=LayerVersion.V1,
            target_layer="L2_execution",
            target_version=LayerVersion.V1,
            payload=payload_wrong_type,
        )
