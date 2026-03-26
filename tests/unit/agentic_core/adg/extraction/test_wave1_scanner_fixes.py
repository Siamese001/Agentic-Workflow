"""Wave 1 regression tests for ADG static correctness gap remediation.

Tests cover:
  W1a: Violation confidence floor raised from 0.3 to 0.5
  W1b: Key-based edge deduplication after post-scan passes
  W1c: _ModuleDefinitionVisitor emits module→func/class decomposes_into
"""

from __future__ import annotations

import ast
import textwrap

import pytest

pytestmark = pytest.mark.unit

try:
#  # MOVED: from agentic_core.adg.extraction.static_scanner import (
        Edge,
        ScanResult,
        _ModuleDefinitionVisitor,
        _propagate_violations,
    )

except Exception:

    Edge = None  # type: ignore[assignment,misc]
    ScanResult = None  # type: ignore[assignment,misc]
    _ModuleDefinitionVisitor = None  # type: ignore[assignment,misc]
    _propagate_violations = None  # type: ignore[assignment,misc]


def _make_edge(**overrides) -> Edge:
    """Helper to create an Edge with sensible defaults."""
    defaults = {
        "from_name": "ADG::Module::foo.py",
        "relation_type": "imports",
        "to_name": "ADG::Symbol::bar",
        "edge_kind": "internal",
        "source_file": "foo.py",
        "line_no": 1,
        "symbol": "bar",
    }
    defaults.update(overrides)
    return Edge(**defaults)


# ---------------------------------------------------------------------------
# W1a: Violation confidence floor
# ---------------------------------------------------------------------------
class TestW1aViolationConfidenceFloor:
    """Verify violation_propagates_through edges have confidence >= 0.5."""

    def test_propagated_edges_confidence_minimum(self):
                from agentic_core.adg.extraction.static_scanner import (
            """Test propagated_edges_confidence_minimum runtime behavior."""
            # Arrange
            # TODO: Set up test data for propagated_edges_confidence_minimum
            test_data = {}  # Replace with actual test data

    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute propagated_edges_confidence_minimum
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
                symbol="layer_violation",
            ),
            _make_edge(
                from_name=importer1,
                relation_type="imports",
                to_name="ADG::Symbol::bad_module",
                edge_kind="internal",
                source_file="uses_bad.py",
                symbol="bad_module",
            ),
            _make_edge(
                from_name=importer2,
                relation_type="imports",
                to_name="ADG::Symbol::uses_bad",
                edge_kind="internal",
                source_file="uses_uses_bad.py",
                symbol="uses_bad",
            ),
        ]

        result = ScanResult(edges=edges)
        propagated = _propagate_violations(result)

        for edge in propagated:
            assert edge.relation_type == "violation_propagates_through"
            assert edge.confidence >= 0.5, (
                f"Violation propagation edge has confidence {edge.confidence} < 0.5 "
                f"(from={edge.from_name}, to={edge.to_name})"
            )

    def test_no_synthetic_below_threshold(self):
    """Test no_synthetic_below_threshold runtime behavior."""
    # Arrange
    # TODO: Set up test data for no_synthetic_below_threshold
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute no_synthetic_below_threshold
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        for edge in propagated:
            assert edge.confidence >= 0.5


# ---------------------------------------------------------------------------
# W1b: Edge deduplication
# ---------------------------------------------------------------------------
class TestW1bEdgeDeduplication:
    """Verify key-based edge dedup removes exact duplicates."""

    def test_exact_duplicates_removed(self):
    """Test exact_duplicates_removed runtime behavior."""
    # Arrange
    # TODO: Set up test data for exact_duplicates_removed
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute exact_duplicates_removed
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
            edge_kind="execution",  # different edge_kind but same key
        )
        e3 = _make_edge(
            from_name="ADG::Module::a.py",
            relation_type="calls",
            to_name="ADG::Symbol::func",
            line_no=20,  # different line — NOT a duplicate
            edge_kind="call",
        )

        edges = [e1, e2, e3]
        # Apply the same dedup logic as scan()
        seen_keys: set[tuple[str, str, str, int]] = set()
        deduped: list[Edge] = []
        for edge in edges:
            key = (edge.from_name, edge.relation_type, edge.to_name, edge.line_no)
            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(edge)

        assert len(deduped) == 2, f"Expected 2 unique edges, got {len(deduped)}"
        # First occurrence wins
        assert deduped[0] is e1
        assert deduped[1] is e3

    def test_no_duplicates_unchanged(self):
    """Test no_duplicates_unchanged runtime behavior."""
    # Arrange
    # TODO: Set up test data for no_duplicates_unchanged
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute no_duplicates_unchanged
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        assert len(deduped) == 5


# ---------------------------------------------------------------------------
# W1c: _ModuleDefinitionVisitor
# ---------------------------------------------------------------------------
class TestW1cModuleDefinitionVisitor:
    """Verify _ModuleDefinitionVisitor emits decomposes_into for all defs."""

    def _parse_and_visit(self, source: str, module_adg: str = "ADG::Module::test_mod.py",
                         source_file: str = "test_mod.py"):
        tree = ast.parse(textwrap.dedent(source))
        visitor = _ModuleDefinitionVisitor(module_adg, source_file)
        visitor.visit(tree)
        return visitor.edges

    def test_top_level_function(self):
    """Test top_level_function runtime behavior."""
    # Arrange
    # TODO: Set up test data for top_level_function
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute top_level_function
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

    def test_top_level_class(self):
    """Test top_level_class runtime behavior."""
    # Arrange
    # TODO: Set up test data for top_level_class
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute top_level_class
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
    def test_class_method(self):
    """Test class_method runtime behavior."""
    # Arrange
    # TODO: Set up test data for class_method
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute class_method
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

    def test_async_function(self):
    """Test async_function runtime behavior."""
    # Arrange
    # TODO: Set up test data for async_function
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute async_function
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    """Test nested_functions_not_emitted runtime behavior."""
    # Arrange
    # TODO: Set up test data for nested_functions_not_emitted
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute nested_functions_not_emitted
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    """Test nested_class runtime behavior."""
    # Arrange
    # TODO: Set up test data for nested_class
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute nested_class
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    """Test empty_module runtime behavior."""
    # Arrange
    # TODO: Set up test data for empty_module
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute empty_module
    result = None  # Replace with actual function call

"""Test line_numbers_correct runtime behavior."""
# Arrange
# TODO: Set up test data for line_numbers_correct
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute line_numbers_correct
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
"""Test multiple_defs runtime behavior."""
# Arrange
# TODO: Set up test data for multiple_defs
test_data = {}  # Replace with actual test data

# Act
# TODO: Execute multiple_defs
result = None  # Replace with actual function call

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, object), "Result should be an object"
# TODO: Add specific runtime behavior assertions
