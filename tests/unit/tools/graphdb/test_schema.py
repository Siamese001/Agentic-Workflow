"""Tests for graphdb schema mapping — node/edge type validation."""

from __future__ import annotations

import pytest

from tools.graphdb.schema import (
    EDGE_TYPE_MAPPING,
    NODE_TYPE_MAPPING,
    NODE_PROPERTIES,
    EDGE_PROPERTIES,
    get_edge_properties,
    get_node_properties,
    validate_edge_type,
    validate_node_type,
)


class TestNodeTypeMapping:
    def test_all_a3_spec_node_types_present(self):
        """All node types required by the A3 spec must be in the mapping."""
        required_types = {
            "file",
            "module",
            "symbol",
            "layer",
            "package",
            "third_party_package",
            "gateway",
            "provider",
            "tool",
            "sink",
            "ingress",
            "prompt_template",
            "prompt_slot",
            "policy",
            "datastore",
            "agent",
            "evaluator",
            "trace_surface",
            "scan_run",
        }
        missing = required_types - set(NODE_TYPE_MAPPING.keys())
        assert not missing, f"Missing node types from A3 spec: {missing}"

    def test_mapping_values_are_pascal_case(self):
        for adg_type, graph_type in NODE_TYPE_MAPPING.items():
            assert graph_type[0].isupper(), f"Graph type '{graph_type}' (for '{adg_type}') must be PascalCase"

    def test_new_spec_types_map_correctly(self):
        assert NODE_TYPE_MAPPING["file"] == "File"
        assert NODE_TYPE_MAPPING["package"] == "Package"
        assert NODE_TYPE_MAPPING["third_party_package"] == "ThirdPartyPackage"
        assert NODE_TYPE_MAPPING["sink"] == "Sink"
        assert NODE_TYPE_MAPPING["ingress"] == "Ingress"
        assert NODE_TYPE_MAPPING["trace_surface"] == "TraceSurface"
        assert NODE_TYPE_MAPPING["evaluator"] == "Evaluator"

    def test_no_duplicate_values(self):
        values = list(NODE_TYPE_MAPPING.values())
        assert len(values) == len(set(values)), "Duplicate graph_type values in NODE_TYPE_MAPPING"


class TestEdgeTypeMapping:
    def test_all_core_edge_types_present(self):
        """All core edge types from the A3 spec must be in the mapping."""
        required_edges = {
            "imports",
            "calls",
            "implements",
            "inherits",
            "reads_from",
            "writes_to",
            "writes_through",
            "routes_through",
            "controls_flow",
            "flows_to",
            "pulls_context",
            "retrieves_via",
            "generates_prompt",
            "consumes_prompt",
            "invokes_provider",
            "applies_guardrail",
            "validates",
            "escalates_to",
            "belongs_to_layer",
            "emits_trace",
            "evaluates",
        }
        missing = required_edges - set(EDGE_TYPE_MAPPING.keys())
        assert not missing, f"Missing edge types from A3 spec: {missing}"

    def test_mapping_values_are_upper_snake(self):
        for _adg_type, graph_type in EDGE_TYPE_MAPPING.items():
            assert graph_type == graph_type.upper(), f"Edge type '{graph_type}' must be UPPER_SNAKE_CASE"

    def test_no_duplicate_values(self):
        values = list(EDGE_TYPE_MAPPING.values())
        assert len(values) == len(set(values)), "Duplicate graph_type values in EDGE_TYPE_MAPPING"


class TestValidateFunctions:
    def test_validate_node_type_known(self):
        result = validate_node_type("module")
        assert result == "Module"

    def test_validate_node_type_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown node type"):
            validate_node_type("nonexistent_type_xyz")

    def test_validate_edge_type_known(self):
        result = validate_edge_type("imports")
        assert result == "IMPORTS"

    def test_validate_edge_type_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown edge type"):
            validate_edge_type("nonexistent_edge_xyz")

    def test_validate_all_mapped_node_types(self):
        for adg_type, expected in NODE_TYPE_MAPPING.items():
            assert validate_node_type(adg_type) == expected

    def test_validate_all_mapped_edge_types(self):
        for adg_type, expected in EDGE_TYPE_MAPPING.items():
            assert validate_edge_type(adg_type) == expected


class TestPropertySchemas:
    def test_get_node_properties_module(self):
        props = get_node_properties("module")
        assert "file_path" in props
        assert "layer" in props

    def test_get_node_properties_new_types(self):
        assert "file_path" in get_node_properties("file")
        assert "sink_type" in get_node_properties("sink")
        assert "ingress_type" in get_node_properties("ingress")
        assert "eval_type" in get_node_properties("evaluator")
        assert "trace_type" in get_node_properties("trace_surface")
        assert "version" in get_node_properties("package")
        assert "import_name" in get_node_properties("third_party_package")

    def test_get_node_properties_unknown_raises_for_unmapped_type(self):
        with pytest.raises(ValueError, match="Unknown node type"):
            get_node_properties("totally_unmapped_type_xyz")

    def test_get_node_properties_mapped_but_no_schema_returns_empty(self):
        no_schema_types = [k for k, v in NODE_TYPE_MAPPING.items() if v not in NODE_PROPERTIES]
        if no_schema_types:
            result = get_node_properties(no_schema_types[0])
            assert result == [], f"Type '{no_schema_types[0]}' has no NODE_PROPERTIES entry; expected []"

    def test_get_edge_properties_imports(self):
        props = get_edge_properties("imports")
        assert "line_number" in props

    def test_get_edge_properties_returns_list(self):
        for edge_type in EDGE_TYPE_MAPPING:
            props = get_edge_properties(edge_type)
            assert isinstance(props, list)

    def test_node_properties_all_values_are_lists(self):
        for node_type, props in NODE_PROPERTIES.items():
            assert isinstance(props, list), f"Properties for {node_type} must be a list"

    def test_edge_properties_all_values_are_lists(self):
        for edge_type, props in EDGE_PROPERTIES.items():
            assert isinstance(props, list), f"Properties for {edge_type} must be a list"
