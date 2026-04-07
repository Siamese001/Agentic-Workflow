"""
Test suite for Boilerplate Ratio Dashboard

Verifies that the ratio report correctly analyzes files
and generates accurate metrics.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add tools/adg to path for importing
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "tools" / "adg"))


# Lazy imports to avoid collection-time conflicts
def _get_analyzer_classes():
    from boilerplate_ratio_report import (
        BoilerplateRatioAnalyzer,
        LayerStats,
        RatioReport,
    )
    return BoilerplateRatioAnalyzer, LayerStats, RatioReport


def test_infer_layer_from_path():
    """Test layer inference from file paths."""
    BoilerplateRatioAnalyzer, LayerStats, RatioReport = _get_analyzer_classes()
    analyzer = BoilerplateRatioAnalyzer(Path("."))

    # Test various layer paths
    assert analyzer.infer_layer_from_path(Path("agentic_core/L0_routing/test.py")) == "L0"
    assert analyzer.infer_layer_from_path(Path("agentic_core/L5_safety/test.py")) == "L5"
    assert analyzer.infer_layer_from_path(Path("apps/test_app/test.py")) == "APPS"
    assert analyzer.infer_layer_from_path(Path("ops_scripts/ci/test.py")) == "OPS"
    assert analyzer.infer_layer_from_path(Path("tests/unit/test.py")) == "TESTS"
    assert analyzer.infer_layer_from_path(Path("tools/adg/test.py")) == "TOOLS"
    assert analyzer.infer_layer_from_path(Path("unknown/path/test.py")) == "UNKNOWN"


def test_calculate_boilerplate_ratio_hollow():
    """Test ratio calculation for hollow file."""
    BoilerplateRatioAnalyzer, LayerStats, RatioReport = _get_analyzer_classes()
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
        analyzer = BoilerplateRatioAnalyzer(Path("."))
        ratio, metadata = analyzer.calculate_boilerplate_ratio(temp_path)

        assert ratio == 1.0  # All boilerplate
        assert metadata["behavioral_nodes"] == 0
        assert metadata["boilerplate_nodes"] > 0
        assert metadata["classification"] in ["hollow", "boilerplate_heavy"]
    finally:
        temp_path.unlink()


def test_calculate_boilerplate_ratio_healthy():
    """Test ratio calculation for healthy file."""
    BoilerplateRatioAnalyzer, LayerStats, RatioReport = _get_analyzer_classes()
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
        analyzer = BoilerplateRatioAnalyzer(Path("."))
        ratio, metadata = analyzer.calculate_boilerplate_ratio(temp_path)

        assert ratio < 0.7  # Should be healthy
        assert metadata["behavioral_nodes"] > 0
        assert metadata["classification"] == "healthy"
    finally:
        temp_path.unlink()


def test_calculate_boilerplate_ratio_syntax_error():
    """Test ratio calculation for file with syntax error."""
    BoilerplateRatioAnalyzer, LayerStats, RatioReport = _get_analyzer_classes()
    # Create temporary file with syntax error
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def broken(\n")  # Missing closing parenthesis
        temp_path = Path(f.name)

    try:
        analyzer = BoilerplateRatioAnalyzer(Path("."))
        ratio, metadata = analyzer.calculate_boilerplate_ratio(temp_path)

        assert ratio == 1.0  # Syntax errors treated as all boilerplate
        assert "error" in metadata
    finally:
        temp_path.unlink()


def test_calculate_boilerplate_ratio_empty():
    """Test ratio calculation for empty file."""
    BoilerplateRatioAnalyzer, LayerStats, RatioReport = _get_analyzer_classes()
    # Create temporary empty file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")
        temp_path = Path(f.name)

    try:
        analyzer = BoilerplateRatioAnalyzer(Path("."))
        ratio, metadata = analyzer.calculate_boilerplate_ratio(temp_path)

        assert ratio == 1.0  # Empty file is all boilerplate
        assert metadata["behavioral_nodes"] == 0
        assert metadata["boilerplate_nodes"] == 0
    finally:
        temp_path.unlink()


@patch('boilerplate_ratio_report.BoilerplateRatioAnalyzer.calculate_boilerplate_ratio')
@patch('boilerplate_ratio_report.BoilerplateRatioAnalyzer.scan_python_files')
def test_generate_ratio_report(mock_scan, mock_calculate):
    """Test complete report generation."""
    BoilerplateRatioAnalyzer, LayerStats, RatioReport = _get_analyzer_classes()
    # Mock file list - use paths that will be classified to expected layers
    mock_scan.return_value = [
        Path("agentic_core/L0_routing/file1.py"),  # Will be L0
        Path("agentic_core/L0_routing/file2.py"),  # Will be L0
        Path("agentic_core/L5_safety/file1.py"),    # Will be L5
    ]

    # Mock ratio calculations
    mock_calculate.side_effect = [
        (1.0, {"classification": "hollow", "behavioral_nodes": 0, "boilerplate_nodes": 5, "lines": 10}),
        (0.5, {"classification": "healthy", "behavioral_nodes": 2, "boilerplate_nodes": 2, "lines": 20}),
        (0.8, {"classification": "boilerplate_heavy", "behavioral_nodes": 1, "boilerplate_nodes": 4, "lines": 15}),
    ]

    analyzer = BoilerplateRatioAnalyzer(Path("."))
    report = analyzer.generate_ratio_report()

    # Check totals
    assert report.total_files == 3
    # hollow = ratio == 1.0 OR classification == "hollow" -> 1 (file1)
    # boilerplate_heavy = ratio > 0.7 OR classification == "boilerplate_heavy" -> 2 (file3=0.8, and file1 has ratio 1.0 but is already counted as hollow)
    # healthy = ratio <= 0.7 AND classification == "healthy" -> 1 (file2=0.5, healthy)
    assert report.summary["total_hollow"] == 1
    assert report.summary["total_healthy"] == 1

    # Check layer stats
    assert "L0" in report.layer_stats
    assert "L5" in report.layer_stats

    l0_stats = report.layer_stats["L0"]
    assert l0_stats.files == 2
    assert l0_stats.hollow == 1
    assert l0_stats.healthy == 1
    assert l0_stats.avg_ratio == 0.75  # (1.0 + 0.5) / 2

    l5_stats = report.layer_stats["L5"]
    assert l5_stats.files == 1
    assert l5_stats.boilerplate_heavy == 1
    assert l5_stats.avg_ratio == 0.8


def test_scan_python_files():
    """Test Python file scanning."""
    BoilerplateRatioAnalyzer, LayerStats, RatioReport = _get_analyzer_classes()
    analyzer = BoilerplateRatioAnalyzer(Path("."))

    with patch('pathlib.Path.rglob') as mock_rglob:
        mock_rglob.return_value = [
            Path("test1.py"),
            Path("test2.py"),
            Path(".git/test.py"),  # Should be excluded
            Path("__pycache__/test.py"),  # Should be excluded
            # Note: rglob('*.py') would never return .pyc files
        ]

        files = analyzer.scan_python_files()

        # Should only include actual Python files not in excluded dirs
        # test1.py and test2.py pass all filters
        assert len(files) == 2
        assert Path("test1.py") in files
        assert Path("test2.py") in files


def test_print_summary(capsys):
    """Test summary printing."""
    BoilerplateRatioAnalyzer, LayerStats, RatioReport = _get_analyzer_classes()
    report = RatioReport(
        timestamp="2023-01-01T00:00:00",
        total_files=2,
        layer_stats={
            "L0": LayerStats(
                files=2,
                hollow=1,
                boilerplate_heavy=1,
                healthy=0,
                avg_ratio=0.75,
                min_ratio=0.5,
                max_ratio=1.0,
                median_ratio=0.75,
                total_lines=30,
                behavioral_nodes=2,
                boilerplate_nodes=8,
            ),
        },
        file_details=[
            {
                "file": "L0_file1.py",
                "layer": "L0",
                "ratio": 1.0,
                "classification": "hollow",
                "behavioral_nodes": 0,
                "boilerplate_nodes": 5,
                "lines": 10,
            },
            {
                "file": "L0_file2.py",
                "layer": "L0",
                "ratio": 0.5,
                "classification": "healthy",
                "behavioral_nodes": 2,
                "boilerplate_nodes": 2,
                "lines": 20,
            },
        ],
        summary={
            "total_files": 2,
            "total_hollow": 1,
            "total_boilerplate_heavy": 1,
            "total_healthy": 0,
            "overall_hollow_percentage": 50.0,
            "overall_boilerplate_heavy_percentage": 50.0,
        },
    )

    analyzer = BoilerplateRatioAnalyzer(Path("."))
    analyzer.print_summary(report)

    captured = capsys.readouterr()
    assert "Boilerplate Ratio Report" in captured.out
    assert "L0:" in captured.out
    assert "Hollow: 1 (50.0%)" in captured.out
    assert "Heavy: 1 (50.0%)" in captured.out


if __name__ == "__main__":
    pytest.main([__file__])
