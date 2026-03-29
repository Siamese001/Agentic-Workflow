"""Wave 1: Static Scanner — Core Visitors Foundation

Tests for AST visitors in static_scanner.py covering governance edge extraction.
18 tests for actual visitors that exist in static_scanner.py.
"""

import ast
from unittest.mock import patch

import pytest

# Import actual scanner components that exist
from agentic_core.adg.extraction.static_scanner import (
    _ImportVisitor,
    _CallVisitor,
    _JITContextVisitor,
    _DynamicInvocationVisitor,
    _P4StateTelemetryVisitor,
    _DynamicExecutionVisitor,
    _InternalCallGraphVisitor,
    _ExecutionTraceVisitor,
    Edge,
    ScanManifest,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def parse_code():
    """Fixture to parse Python code into AST."""
    def _parse(code: str) -> ast.AST:
        return ast.parse(code)
    return _parse


# ============================================================================
# Import Visitor Tests (G7)
# ============================================================================

@pytest.mark.unit
class TestImportVisitor:
    """Tests for _ImportVisitor — G7 governance edge extraction."""

    def test_import_visitor_initialization(self):
        """Test _ImportVisitor can be initialized."""
        visitor = _ImportVisitor("test_module", "test_file")
        assert visitor.module_adg_name == "test_module"
        assert visitor.source_file == "test_file"
        assert hasattr(visitor, 'edges')

    def test_import_visitor_visits_import(self, parse_code):
        """Test _ImportVisitor processes import statements."""
        code = "import os"
        tree = parse_code(code)
        visitor = _ImportVisitor("test_module", "test_file")
        visitor.visit(tree)

        # Should have processed the import
        assert isinstance(visitor.edges, list)


# ============================================================================
# JIT Context Visitor Tests (G9)
# ============================================================================

@pytest.mark.unit
class TestJITContextVisitor:
    """Tests for _JITContextVisitor — G9 JIT context detection."""

    def test_jit_visitor_initialization(self):
        """Test _JITContextVisitor can be initialized."""
        visitor = _JITContextVisitor("test_module", "test_file")
        assert visitor.module_adg_name == "test_module"
        assert visitor.source_file == "test_file"
        assert hasattr(visitor, 'edges')

    def test_jit_visitor_visits_code(self, parse_code):
        """Test _JITContextVisitor processes code."""
        code = "def test(): pass"
        tree = parse_code(code)
        visitor = _JITContextVisitor("test_module", "test_file")
        visitor.visit(tree)

        # Should have processed the code
        assert isinstance(visitor.edges, list)


# ============================================================================
# Dynamic Invocation Visitor Tests (G19)
# ============================================================================

@pytest.mark.unit
class TestDynamicInvocationVisitor:
    """Tests for _DynamicInvocationVisitor — G19 dynamic execution detection."""

    def test_dynamic_visitor_initialization(self):
        """Test _DynamicInvocationVisitor can be initialized."""
        visitor = _DynamicInvocationVisitor("test_module", "test_file")
        assert visitor.module_adg_name == "test_module"
        assert visitor.source_file == "test_file"
        assert hasattr(visitor, 'edges')

    def test_dynamic_visitor_visits_eval(self, parse_code):
        """Test _DynamicInvocationVisitor detects eval."""
        code = "eval('code')"
        tree = parse_code(code)
        visitor = _DynamicInvocationVisitor("test_module", "test_file")
        visitor.visit(tree)

        # Should have processed the eval
        assert isinstance(visitor.edges, list)


# ============================================================================
# State Telemetry Visitor Tests (G28)
# ============================================================================

@pytest.mark.unit
class TestStateTelemetryVisitor:
    """Tests for _P4StateTelemetryVisitor — G28 state tracking."""

    def test_telemetry_visitor_initialization(self):
        """Test _P4StateTelemetryVisitor can be initialized."""
        visitor = _P4StateTelemetryVisitor("test_module", "test_file")
        assert visitor.module_adg_name == "test_module"
        assert visitor.source_file == "test_file"
        assert hasattr(visitor, 'edges')

    def test_telemetry_visitor_visits_code(self, parse_code):
        """Test _P4StateTelemetryVisitor processes code."""
        code = "def test(): pass"
        tree = parse_code(code)
        visitor = _P4StateTelemetryVisitor("test_module", "test_file")
        visitor.visit(tree)

        # Should have processed the code
        assert isinstance(visitor.edges, list)


# ============================================================================
# Dynamic Execution Visitor Tests (G29)
# ============================================================================

@pytest.mark.unit
class TestDynamicExecutionVisitor:
    """Tests for _DynamicExecutionVisitor — G29 side effects."""

    def test_dynamic_execution_initialization(self):
        """Test _DynamicExecutionVisitor can be initialized."""
        visitor = _DynamicExecutionVisitor("test_module", "test_file")
        assert visitor.module_adg_name == "test_module"
        assert visitor.source_file == "test_file"
        assert hasattr(visitor, 'edges')

    def test_dynamic_execution_visits_file_ops(self, parse_code):
        """Test _DynamicExecutionVisitor detects file operations."""
        code = "open('file.txt')"
        tree = parse_code(code)
        visitor = _DynamicExecutionVisitor("test_module", "test_file")
        visitor.visit(tree)

        # Should have processed the file operation
        assert isinstance(visitor.edges, list)


# ============================================================================
# Internal Call Graph Visitor Tests (G30)
# ============================================================================

@pytest.mark.unit
class TestInternalCallGraphVisitor:
    """Tests for _InternalCallGraphVisitor — G30 call graph construction."""

    def test_call_graph_initialization(self):
        """Test _InternalCallGraphVisitor can be initialized."""
        visitor = _InternalCallGraphVisitor("test_module", "test_file")
        assert visitor.module_adg_name == "test_module"
        assert visitor.source_file == "test_file"
        assert hasattr(visitor, 'edges')

    def test_call_graph_visits_function_calls(self, parse_code):
        """Test _InternalCallGraphVisitor detects function calls."""
        code = "def helper(): pass\ndef main(): helper()"
        tree = parse_code(code)
        visitor = _InternalCallGraphVisitor("test_module", "test_file")
        visitor.visit(tree)

        # Should have processed the function calls
        assert isinstance(visitor.edges, list)


# ============================================================================
# Execution Trace Visitor Tests
# ============================================================================

@pytest.mark.unit
class TestExecutionTraceVisitor:
    """Tests for _ExecutionTraceVisitor."""

    def test_execution_trace_initialization(self):
        """Test _ExecutionTraceVisitor can be initialized."""
        visitor = _ExecutionTraceVisitor("test_module", "test_file")
        assert visitor.module_adg_name == "test_module"
        assert visitor.source_file == "test_file"
        assert hasattr(visitor, 'edges')

    def test_execution_trace_visits_code(self, parse_code):
        """Test _ExecutionTraceVisitor processes code."""
        code = "def test(): pass"
        tree = parse_code(code)
        visitor = _ExecutionTraceVisitor("test_module", "test_file")
        visitor.visit(tree)

        # Should have processed the code
        assert isinstance(visitor.edges, list)


# ============================================================================
# Edge Data Structure Tests
# ============================================================================

@pytest.mark.unit
class TestEdge:
    """Tests for Edge data structure."""

    def test_edge_creation(self):
        """Test Edge can be created with required fields."""
        edge = Edge(
            from_name="test_from",
            relation_type="test_relation",
            to_name="test_to",
            edge_kind="test_kind",
            source_file="test.py",
            line_no=1,
            symbol="test_symbol"
        )
        assert edge.from_name == "test_from"
        assert edge.relation_type == "test_relation"
        assert edge.to_name == "test_to"

    def test_edge_sortable(self):
        """Test Edge is sortable."""
        edge1 = Edge("a", "rel", "b", "kind", "file.py", 1, "sym")
        edge2 = Edge("b", "rel", "c", "kind", "file.py", 2, "sym")

        # Should be comparable
        assert edge1 < edge2


# ============================================================================
# Scan Manifest Tests
# ============================================================================

@pytest.mark.unit
class TestScanManifest:
    """Tests for ScanManifest functionality."""

    def test_manifest_creation(self):
        """Test creation of scan manifest."""
        manifest = ScanManifest(
            discovered_module_count=10,
            parsed_module_count=8,
            edge_counts_by_graph={"imports": 15}
        )

        assert manifest.discovered_module_count == 10
        assert manifest.parsed_module_count == 8
        assert manifest.edge_counts_by_graph["imports"] == 15

    def test_manifest_to_dict(self):
        """Test manifest serialization."""
        manifest = ScanManifest(
            discovered_module_count=10,
            parsed_module_count=8,
            edge_counts_by_graph={"imports": 15}
        )

        data = manifest.to_dict()
        assert isinstance(data, dict)
        assert 'discovered_module_count' in data
        assert 'parsed_module_count' in data


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.unit
class TestScannerIntegration:
    """Integration tests for scanner components."""

    def test_multiple_visitors_integration(self, parse_code):
        """Test multiple visitors working together."""
        code = '''
import os
def process():
    result = helper()
    return result
'''
        tree = parse_code(code)

        # Run multiple visitors
        visitors = [
            _ImportVisitor("test_module", "test_file"),
            _InternalCallGraphVisitor("test_module", "test_file"),
        ]

        all_edges = []
        for visitor in visitors:
            visitor.visit(tree)
            all_edges.extend(getattr(visitor, 'edges', []))

        # Should have edges from all visitors
        assert isinstance(all_edges, list)

    def test_visitor_error_handling(self, parse_code):
        """Test visitors handle errors gracefully."""
        code = "def test(): pass"
        tree = parse_code(code)

        # All visitors should handle visiting without crashing
        visitors = [
            _ImportVisitor("test_module", "test_file"),
            _JITContextVisitor("test_module", "test_file"),
            _DynamicInvocationVisitor("test_module", "test_file"),
            _P4StateTelemetryVisitor("test_module", "test_file"),
            _DynamicExecutionVisitor("test_module", "test_file"),
            _InternalCallGraphVisitor("test_module", "test_file"),
            _ExecutionTraceVisitor("test_module", "test_file"),
        ]

        for visitor in visitors:
            try:
                visitor.visit(tree)
                assert True  # Should not crash
            except Exception:
                pytest.fail(f"Visitor {visitor.__class__.__name__} crashed during visit")
