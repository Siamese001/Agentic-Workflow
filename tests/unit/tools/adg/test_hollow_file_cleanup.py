"""
Test suite for Hollow File Cleanup Scanner

Verifies that the cleanup scanner correctly analyzes hollow files
and generates appropriate cleanup manifests.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# Lazy imports to avoid collection-time conflicts
def _get_analyzer_classes():
    from tools.adg.hollow_file_cleanup import (
        CleanupManifest,
        FileAnalysis,
        HollowFileCleanupAnalyzer,
    )
    return HollowFileCleanupAnalyzer, CleanupManifest, FileAnalysis


def test_analyze_file_hollow():
    """Test analysis of a hollow file."""
    HollowFileCleanupAnalyzer, CleanupManifest, FileAnalysis = _get_analyzer_classes()
    # Create temporary hollow file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import os
import sys

_emit_records_execution_trace("test", "test", "test")
_emit_applies_guardrail("test", "test", "test")
""")
        temp_path = Path(f.name)

    try:
        analyzer = HollowFileCleanupAnalyzer(Path("."))
        result = analyzer.analyze_file(temp_path)

        assert result.is_hollow is True
        assert result.classification in ["hollow", "boilerplate_heavy"]
        assert result.behavioral_nodes == 0
        assert result.boilerplate_nodes > 0
    finally:
        temp_path.unlink()


def test_analyze_file_healthy():
    """Test analysis of a healthy file."""
    HollowFileCleanupAnalyzer, CleanupManifest, FileAnalysis = _get_analyzer_classes()
    # Create temporary healthy file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import os

def behavioral_function():
    x = 1 + 1
    return x

class TestClass:
    def method(self):
        return "test"
""")
        temp_path = Path(f.name)

    try:
        analyzer = HollowFileCleanupAnalyzer(Path("."))
        result = analyzer.analyze_file(temp_path)

        assert result.is_hollow is False
        assert result.classification == "healthy"
        assert result.behavioral_nodes > 0
    finally:
        temp_path.unlink()


def test_classify_cleanup_safety():
    """Test classification of cleanup safety."""
    HollowFileCleanupAnalyzer, CleanupManifest, FileAnalysis = _get_analyzer_classes()
    analyses = [
        FileAnalysis(
            file_path="safe1.py",
            is_hollow=True,
            classification="hollow",
            behavioral_nodes=0,
            boilerplate_nodes=10,
            incoming_edges=[],
            outgoing_edges=[],
            incoming_count=0,
            outgoing_count=0
        ),
        FileAnalysis(
            file_path="safe2.py",
            is_hollow=True,
            classification="hollow",
            behavioral_nodes=0,
            boilerplate_nodes=5,
            incoming_edges=[],
            outgoing_edges=["os", "sys"],
            incoming_count=0,
            outgoing_count=2
        ),
        FileAnalysis(
            file_path="unsafe.py",
            is_hollow=True,
            classification="hollow",
            behavioral_nodes=0,
            boilerplate_nodes=8,
            incoming_edges=["other_module"],
            outgoing_edges=["os"],
            incoming_count=1,
            outgoing_count=1
        )
    ]

    analyzer = HollowFileCleanupAnalyzer(Path("."))
    manifest = analyzer.classify_cleanup_safety(analyses)

    assert len(manifest.tier1_safe_delete) == 1
    assert "safe1.py" in manifest.tier1_safe_delete

    assert len(manifest.tier2_boilerplate_only) == 1
    assert "safe2.py" in manifest.tier2_boilerplate_only

    assert len(manifest.tier3_behavioral_imports) == 1
    assert "unsafe.py" in manifest.tier3_behavioral_imports


def test_try_adg_enhancement_no_adg():
    """Test ADG enhancement when ADG is not available."""
    HollowFileCleanupAnalyzer, CleanupManifest, FileAnalysis = _get_analyzer_classes()
    analyses = [
        FileAnalysis(
            file_path="test.py",
            is_hollow=True,
            classification="hollow",
            behavioral_nodes=0,
            boilerplate_nodes=5,
            incoming_edges=[],
            outgoing_edges=[],
            incoming_count=0,
            outgoing_count=0
        )
    ]

    analyzer = HollowFileCleanupAnalyzer(Path("."))
    manifest = analyzer.classify_cleanup_safety(analyses)

    # Should handle missing ADG gracefully
    enhanced = analyzer.try_adg_enhancement(manifest)

    assert enhanced is manifest
    assert len(enhanced.tier1_safe_delete) == 1


@patch('tools.adg.hollow_file_cleanup.HollowFileCleanupAnalyzer.analyze_file')
def test_scan_repository(mock_analyze):
    """Test repository scanning."""
    HollowFileCleanupAnalyzer, CleanupManifest, FileAnalysis = _get_analyzer_classes()
    # Mock analyze_file to return hollow files
    mock_analyze.side_effect = [
        FileAnalysis(
            file_path="hollow1.py",
            is_hollow=True,
            classification="hollow",
            behavioral_nodes=0,
            boilerplate_nodes=5,
            incoming_edges=[],
            outgoing_edges=[],
            incoming_count=0,
            outgoing_count=0
        ),
        FileAnalysis(
            file_path="hollow2.py",
            is_hollow=True,
            classification="boilerplate_heavy",
            behavioral_nodes=0,
            boilerplate_nodes=10,
            incoming_edges=[],
            outgoing_edges=[],
            incoming_count=0,
            outgoing_count=0
        )
    ]

    with patch('pathlib.Path.rglob') as mock_rglob:
        mock_rglob.return_value = [Path("hollow1.py"), Path("hollow2.py"), Path("healthy.py")]

        analyzer = HollowFileCleanupAnalyzer(Path("."))

        # Mock file existence check
        with patch('pathlib.Path.exists', return_value=True):
            results = analyzer.scan_repository()

    assert len(results) == 2  # Only hollow files returned
    assert all(r.is_hollow for r in results)


def test_analyze_file_syntax_error():
    """Test analysis of file with syntax error."""
    HollowFileCleanupAnalyzer, CleanupManifest, FileAnalysis = _get_analyzer_classes()
    # Create temporary file with syntax error
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def broken(\n")  # Missing closing parenthesis
        temp_path = Path(f.name)

    try:
        analyzer = HollowFileCleanupAnalyzer(Path("."))
        result = analyzer.analyze_file(temp_path)

        assert result.is_hollow is False  # Syntax errors not treated as hollow
        assert result.classification == "healthy"
        assert result.behavioral_nodes == 0
        assert result.boilerplate_nodes == 0
    finally:
        temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
