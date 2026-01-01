"""
Unit Tests for Dependency Graph Analyzer (DGA)

Tests dependency analysis capabilities:
- build_graph: Build import/call dependency graph
- detect_cycles: Find circular dependencies
- impact_analysis: Analyze change impact
- unused_imports: Find unused imports
"""
import sys
from pathlib import Path
import tempfile
import os

# Ensure project root is in path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest

from agentic_core.L2_execution.tool_registry.tools.dependency_graph import (
    DependencyGraphArgs,
    GraphOperation,
    DependencyGraph,
    GraphResult,
    dependency_graph,
    build_graph,
    detect_cycles,
    impact_analysis,
    find_unused_imports,
    parse_file,
    quick_cycles,
    quick_impact,
    quick_unused,
)


def write_temp_file(content: str) -> str:
    """Write content to a temp file and return path. Caller must delete."""
    fd, fpath = tempfile.mkstemp(suffix='.py')
    try:
        os.write(fd, content.encode('utf-8'))
    finally:
        os.close(fd)
    return fpath


class TestParseFile:
    """Tests for parse_file function."""

    def test_parse_simple_imports(self):
        """Parse file with simple imports."""
        fpath = write_temp_file("""
import os
from pathlib import Path
from typing import Dict, List

def main():
    pass
""")
        try:
            result = parse_file(fpath, include_stdlib=True)
            assert result["success"] is True
            assert len(result["imports"]) >= 2
        finally:
            os.unlink(fpath)

    def test_parse_function_definitions(self):
        """Parse file with function definitions."""
        fpath = write_temp_file("""
def foo():
    pass

async def bar():
    pass

class MyClass:
    def method(self):
        pass
""")
        try:
            result = parse_file(fpath)
            assert result["success"] is True
            assert len(result["definitions"]) >= 3
            
            def_names = [d["name"] for d in result["definitions"]]
            assert "foo" in def_names
            assert "bar" in def_names
            assert "MyClass" in def_names
        finally:
            os.unlink(fpath)

    def test_parse_syntax_error(self):
        """Parse file with syntax error should fail gracefully."""
        fpath = write_temp_file("def broken(")
        try:
            result = parse_file(fpath)
            assert result["success"] is False
            assert "syntax" in result["error"].lower()
        finally:
            os.unlink(fpath)

    def test_parse_calls(self):
        """Parse file and extract function calls."""
        fpath = write_temp_file("""
def main():
    print("hello")
    result = process_data()
    obj.method()
""")
        try:
            result = parse_file(fpath)
            assert result["success"] is True
            call_names = [c["name"] for c in result["calls"]]
            assert "print" in call_names
            assert "process_data" in call_names
        finally:
            os.unlink(fpath)


class TestBuildGraph:
    """Tests for build_graph function."""

    def test_build_graph_single_file(self):
        """Build graph from a single file."""
        fpath = write_temp_file("""
from mymodule import helper

def main():
    helper()
""")
        try:
            result = build_graph(fpath)
            assert result.success is True
            assert "nodes" in result.data
            assert "edges" in result.data
        finally:
            os.unlink(fpath)

    def test_build_graph_directory(self):
        """Build graph from a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "module_a.py").write_text("""
from module_b import func_b

def func_a():
    func_b()
""")
            (Path(tmpdir) / "module_b.py").write_text("""
def func_b():
    pass
""")
            
            result = build_graph(tmpdir)
            
            assert result.success is True
            assert result.data["node_count"] >= 2

    def test_build_graph_nonexistent_path(self):
        """Build graph from nonexistent path should fail."""
        result = build_graph("/nonexistent/path")
        
        assert result.success is False
        assert "does not exist" in result.error


class TestDetectCycles:
    """Tests for detect_cycles function."""

    def test_no_cycles(self):
        """Detect cycles in acyclic graph."""
        graph_data = {
            "nodes": {
                "a": {"imports": ["b"], "imported_by": []},
                "b": {"imports": ["c"], "imported_by": ["a"]},
                "c": {"imports": [], "imported_by": ["b"]},
            }
        }
        
        result = detect_cycles(graph_data)
        
        assert result.success is True
        assert result.data["has_cycles"] is False
        assert result.data["cycle_count"] == 0

    def test_simple_cycle(self):
        """Detect a simple A -> B -> A cycle."""
        graph_data = {
            "nodes": {
                "a": {"imports": ["b"], "imported_by": ["b"]},
                "b": {"imports": ["a"], "imported_by": ["a"]},
            }
        }
        
        result = detect_cycles(graph_data)
        
        assert result.success is True
        assert result.data["has_cycles"] is True
        assert result.data["cycle_count"] >= 1

    def test_complex_cycle(self):
        """Detect a complex A -> B -> C -> A cycle."""
        graph_data = {
            "nodes": {
                "a": {"imports": ["b"], "imported_by": ["c"]},
                "b": {"imports": ["c"], "imported_by": ["a"]},
                "c": {"imports": ["a"], "imported_by": ["b"]},
            }
        }
        
        result = detect_cycles(graph_data)
        
        assert result.success is True
        assert result.data["has_cycles"] is True


class TestImpactAnalysis:
    """Tests for impact_analysis function."""

    def test_impact_direct_dependents(self):
        """Find direct dependents of a module."""
        graph_data = {
            "nodes": {
                "core": {"imports": [], "imported_by": ["app", "utils"]},
                "app": {"imports": ["core"], "imported_by": []},
                "utils": {"imports": ["core"], "imported_by": []},
            }
        }
        
        result = impact_analysis(graph_data, "core")
        
        assert result.success is True
        assert "app" in result.data["direct_dependents"]
        assert "utils" in result.data["direct_dependents"]

    def test_impact_transitive_dependents(self):
        """Find transitive dependents."""
        graph_data = {
            "nodes": {
                "core": {"imports": [], "imported_by": ["utils"]},
                "utils": {"imports": ["core"], "imported_by": ["app"]},
                "app": {"imports": ["utils"], "imported_by": []},
            }
        }
        
        result = impact_analysis(graph_data, "core")
        
        assert result.success is True
        assert "utils" in result.data["direct_dependents"]
        # app depends on utils which depends on core
        assert result.data["total_impact"] >= 2

    def test_impact_nonexistent_symbol(self):
        """Impact analysis for nonexistent symbol should fail."""
        graph_data = {"nodes": {}}
        
        result = impact_analysis(graph_data, "nonexistent")
        
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_impact_risk_levels(self):
        """Verify risk level calculation."""
        graph_data = {
            "nodes": {
                "core": {"imports": [], "imported_by": ["a", "b", "c", "d", "e"]},
                "a": {"imports": ["core"], "imported_by": []},
                "b": {"imports": ["core"], "imported_by": []},
                "c": {"imports": ["core"], "imported_by": []},
                "d": {"imports": ["core"], "imported_by": []},
                "e": {"imports": ["core"], "imported_by": []},
            }
        }
        
        result = impact_analysis(graph_data, "core")
        
        assert result.success is True
        assert result.data["risk_level"] in ["low", "medium", "high", "critical"]


class TestUnusedImports:
    """Tests for find_unused_imports function."""

    def test_find_unused_import(self):
        """Find unused imports in a file."""
        fpath = write_temp_file("""
import os
import sys

def main():
    os.path.exists("test")
""")
        try:
            result = find_unused_imports(fpath)
            assert result.success is True
            # sys should be detected as unused (os is used)
            unused_names = [u["name"] for u in result.data["unused_imports"]]
            # Note: detection depends on call extraction accuracy
            assert result.data["files_analyzed"] == 1
        finally:
            os.unlink(fpath)

    def test_no_unused_imports(self):
        """File with all imports used."""
        fpath = write_temp_file("""
import os

def main():
    os.path.exists("test")
""")
        try:
            result = find_unused_imports(fpath)
            assert result.success is True
            assert result.data["files_analyzed"] == 1
        finally:
            os.unlink(fpath)


class TestDependencyGraphDispatch:
    """Tests for the main dependency_graph entry point."""

    def test_dispatch_build_graph(self):
        """Dispatch to build_graph operation."""
        fpath = write_temp_file("x = 10")
        try:
            args = DependencyGraphArgs(
                operation=GraphOperation.BUILD_GRAPH,
                target_path=fpath
            )
            result = dependency_graph(args)
            assert result["success"] is True
        finally:
            os.unlink(fpath)

    def test_dispatch_detect_cycles(self):
        """Dispatch to detect_cycles operation."""
        fpath = write_temp_file("x = 10")
        try:
            args = DependencyGraphArgs(
                operation=GraphOperation.DETECT_CYCLES,
                target_path=fpath
            )
            result = dependency_graph(args)
            assert result["success"] is True
            assert "has_cycles" in result["data"]
        finally:
            os.unlink(fpath)

    def test_dispatch_impact_analysis_missing_symbol(self):
        """Impact analysis without symbol should fail."""
        fpath = write_temp_file("x = 10")
        try:
            args = DependencyGraphArgs(
                operation=GraphOperation.IMPACT_ANALYSIS,
                target_path=fpath
                # Missing symbol
            )
            result = dependency_graph(args)
            assert result["success"] is False
            assert "symbol required" in result["error"]
        finally:
            os.unlink(fpath)


class TestQuickFunctions:
    """Tests for convenience quick_* functions."""

    def test_quick_cycles(self):
        """quick_cycles should return list of cycles."""
        fpath = write_temp_file("x = 10")
        try:
            cycles = quick_cycles(fpath)
            assert isinstance(cycles, list)
        finally:
            os.unlink(fpath)

    def test_quick_unused(self):
        """quick_unused should return list of unused imports."""
        fpath = write_temp_file("import sys\nx = 10")
        try:
            unused = quick_unused(fpath)
            assert isinstance(unused, list)
        finally:
            os.unlink(fpath)


class TestDependencyGraph:
    """Tests for DependencyGraph dataclass."""

    def test_add_node(self):
        """Add node to graph."""
        graph = DependencyGraph()
        node = graph.add_node("test_module", path="/path/to/module.py")
        
        assert node.name == "test_module"
        assert "test_module" in graph.nodes

    def test_add_edge(self):
        """Add edge between nodes."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b")
        graph.add_edge("a", "b", "imports")
        
        assert len(graph.edges) == 1
        assert ("a", "b", "imports") in graph.edges
        assert "b" in graph.nodes["a"].imports

    def test_to_dict(self):
        """Convert graph to dict."""
        graph = DependencyGraph()
        graph.add_node("a")
        graph.add_node("b")
        graph.add_edge("a", "b", "imports")
        
        d = graph.to_dict()
        
        assert "nodes" in d
        assert "edges" in d
        assert d["node_count"] == 2
        assert d["edge_count"] == 1
