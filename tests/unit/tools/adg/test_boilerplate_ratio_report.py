"""
Test suite for Boilerplate Ratio Dashboard

Verifies that the ratio report correctly analyzes files
and generates accurate metrics.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.adg.boilerplate_ratio_report import (
    BoilerplateRatioAnalyzer,
    LayerStats,
    RatioReport,
)


def test_infer_layer_from_path():
    """Test layer inference from file paths."""
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


@patch('tools.adg.boilerplate_ratio_report.BoilerplateRatioAnalyzer.calculate_boilerplate_ratio')
@patch('tools.adg.boilerplate_ratio_report.BoilerplateRatioAnalyzer.scan_python_files')
def test_generate_ratio_report(mock_scan, mock_calculate):
    """Test complete report generation."""
    # Mock file list
    mock_scan.return_value = [
        Path("L0_file1.py"),
        Path("L0_file2.py"),
        Path("L5_file1.py")
    ]
    
    # Mock ratio calculations
    mock_calculate.side_effect = [
        (1.0, {"classification": "hollow", "behavioral_nodes": 0, "boilerplate_nodes": 5, "lines": 10}),
        (0.5, {"classification": "healthy", "behavioral_nodes": 2, "boilerplate_nodes": 2, "lines": 20}),
        (0.8, {"classification": "boilerplate_heavy", "behavioral_nodes": 1, "boilerplate_nodes": 4, "lines": 15})
    ]
    
    analyzer = BoilerplateRatioAnalyzer(Path("."))
    report = analyzer.generate_ratio_report()
    
    # Check totals
    assert report.total_files == 3
    assert report.summary["total_hollow"] == 1
    assert report.summary["total_boilerplate_heavy"] == 1
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
    analyzer = BoilerplateRatioAnalyzer(Path("."))
    
    with patch('pathlib.Path.rglob') as mock_rglob:
        mock_rglob.return_value = [
            Path("test1.py"),
            Path("test2.py"),
            Path(".git/test.py"),  # Should be excluded
            Path("__pycache__/test.py"),  # Should be excluded
            Path("test.pyc"),  # Not a Python file
        ]
        
        files = analyzer.scan_python_files()
        
        # Should only include actual Python files not in excluded dirs
        assert len(files) == 2
        assert Path("test1.py") in files
        assert Path("test2.py") in files


def test_print_summary(capsys):
    """Test summary printing."""
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
                boilerplate_nodes=8
            )
        },
        file_details=[
            {
                "file": "L0_file1.py",
                "layer": "L0",
                "ratio": 1.0,
                "classification": "hollow",
                "behavioral_nodes": 0,
                "boilerplate_nodes": 5,
                "lines": 10
            },
            {
                "file": "L0_file2.py",
                "layer": "L0",
                "ratio": 0.5,
                "classification": "healthy",
                "behavioral_nodes": 2,
                "boilerplate_nodes": 2,
                "lines": 20
            }
        ],
        summary={
            "total_files": 2,
            "total_hollow": 1,
            "total_boilerplate_heavy": 1,
            "total_healthy": 0,
            "overall_hollow_percentage": 50.0,
            "overall_boilerplate_heavy_percentage": 50.0
        }
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
