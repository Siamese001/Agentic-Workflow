"""Scanner Structure Tests — Detect Code Quality Issues.

Tests to detect structural patterns in static_scanner.py that indicate
maintenance issues (repetitive code, excessive line counts, etc.).
"""
import ast
from pathlib import Path

import pytest


@pytest.mark.unit
class TestScannerCodeStructure:
    """Tests for static_scanner.py code structure quality."""

    def test_no_excessive_repetitive_calls(self):
        """Detect excessive repetitive function calls that should be loops.

        This test catches issues like the 640+ _emit_reads_through() calls
        that were added as individual lines instead of a loop.
        """
        scanner_path = Path("agentic_core/adg/extraction/static_scanner.py")
        if not scanner_path.exists():
            pytest.skip("Scanner file not found at expected path")

        content = scanner_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Count consecutive identical call patterns
        call_counts = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Name):
                    func_name = call.func.id
                    if func_name.startswith("_emit_"):
                        call_counts[func_name] = call_counts.get(func_name, 0) + 1

        # Any single emitter called more than 50 times indicates a pattern
        # that should have been a loop
        excessive_emitters = [
            (name, count) for name, count in call_counts.items()
            if count > 50
        ]

        if excessive_emitters:
            names = [f"{name}({count})" for name, count in excessive_emitters]
            pytest.fail(
                f"Found excessive repetitive emitter calls that should be loops: {', '.join(names)}. "
                f"Consider consolidating into a loop or configuration-driven approach."
            )

    def test_file_size_reasonable(self):
        """Ensure static_scanner.py isn't excessively large."""
        scanner_path = Path("agentic_core/adg/extraction/static_scanner.py")
        if not scanner_path.exists():
            pytest.skip("Scanner file not found")

        lines = scanner_path.read_text(encoding="utf-8").splitlines()
        line_count = len(lines)

        # 3000+ lines is excessive for a single module
        # Current issue: 3700+ lines with 640+ repetitive calls
        max_reasonable_lines = 3000

        if line_count > max_reasonable_lines:
            pytest.fail(
                f"static_scanner.py has {line_count} lines, exceeding {max_reasonable_lines}. "
                f"Consider refactoring: split visitors into separate modules, "
                f"consolidate repetitive bootstrap calls into loops."
            )

    def test_visitor_classes_documented(self):
        """Ensure all visitor classes have docstrings."""
        scanner_path = Path("agentic_core/adg/extraction/static_scanner.py")
        if not scanner_path.exists():
            pytest.skip("Scanner file not found")

        content = scanner_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        visitor_classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.endswith("Visitor") and not node.name.startswith("_"):
                    visitor_classes.append(node)

        # All visitors should have docstrings
        visitors_without_docs = [
            c.name for c in visitor_classes
            if not (ast.get_docstring(c))
        ]

        # This is informational - we log but don't fail
        # since some internal visitors may be intentionally private
        if visitors_without_docs:
            print(f"Note: {len(visitors_without_docs)} visitors without docstrings: {visitors_without_docs}")

        # Only public visitors must have docstrings
        public_visitors = [c for c in visitor_classes if not c.name.startswith("_")]
        undocumented_public = [c.name for c in public_visitors if not ast.get_docstring(c)]

        if undocumented_public:
            pytest.fail(f"Public visitor classes missing docstrings: {undocumented_public}")


@pytest.mark.unit
class TestEdgeDetectionQuality:
    """Tests that verify edge detection actually works (not just initialization)."""

    def test_import_visitor_creates_imports_edge(self):
        """Verify _ImportVisitor actually creates an 'imports' edge."""
        from agentic_core.adg.extraction.static_scanner import _ImportVisitor, Edge

        code = "import os"
        tree = ast.parse(code)
        visitor = _ImportVisitor("test_module", "test_file.py")
        visitor.visit(tree)

        # Should have at least one edge with 'imports' relation
        import_edges = [
            e for e in visitor.edges
            if e.relation_type == "imports"
        ]

        assert len(import_edges) >= 1, (
            f"Expected at least 1 'imports' edge, got {len(import_edges)}. "
            f"Visitor edges: {[e.relation_type for e in visitor.edges]}"
        )

    def test_import_visitor_edge_attributes(self):
        """Verify import edges have correct attributes."""
        from agentic_core.adg.extraction.static_scanner import _ImportVisitor, Edge

        code = "import os"
        tree = ast.parse(code)
        visitor = _ImportVisitor("test_module", "test_file.py")
        visitor.visit(tree)

        # Find imports edges
        import_edges = [e for e in visitor.edges if e.relation_type == "imports"]

        if not import_edges:
            pytest.skip("No import edges detected")

        edge = import_edges[0]
        assert edge.from_name == "test_module"
        assert edge.to_name == "os" or "os" in edge.to_name
        assert edge.source_file == "test_file.py"
        assert edge.line_no == 1
        assert edge.symbol == "os"

    def test_dynamic_invocation_detects_eval(self):
        """Verify _DynamicInvocationVisitor detects eval() calls."""
        from agentic_core.adg.extraction.static_scanner import _DynamicInvocationVisitor

        code = "eval('x + 1')"
        tree = ast.parse(code)
        visitor = _DynamicInvocationVisitor("test_module", "test_file.py")
        visitor.visit(tree)

        # Should detect the eval call
        eval_edges = [
            e for e in visitor.edges
            if e.symbol == "eval" or "eval" in e.relation_type
        ]

        assert len(eval_edges) >= 1, (
            f"Expected eval detection, got edges: {[e.symbol for e in visitor.edges]}"
        )

    def test_call_visitor_detects_function_calls(self):
        """Verify _CallVisitor creates call edges."""
        from agentic_core.adg.extraction.static_scanner import _CallVisitor

        code = """
def helper():
    pass

def main():
    helper()
"""
        tree = ast.parse(code)
        visitor = _CallVisitor("test_module", "test_file.py")
        visitor.visit(tree)

        # Should detect the function call
        call_edges = [e for e in visitor.edges if e.relation_type == "calls"]

        assert len(call_edges) >= 1, (
            f"Expected at least 1 call edge, got {len(call_edges)}. "
            f"All edges: {[e.relation_type for e in visitor.edges]}"
        )
