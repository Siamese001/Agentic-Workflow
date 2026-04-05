"""Test ScorecardRenderer functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestScorecardRenderer:
    """Test ScorecardRenderer functionality."""

    def test_render_csv_empty(self):
        """Test rendering CSV with empty rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        renderer = ScorecardRenderer()
        csv_output = renderer.render_csv([])

        assert "dimension_id,display_name,score,weight,weighted_score,verdict" in csv_output

    def test_render_csv_with_rows(self):
        """Test rendering CSV with data rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        mock_row = MagicMock()
        mock_row.dimension_id = "dim_1"
        mock_row.display_name = "Test Dimension"
        mock_row.score = 0.85
        mock_row.weight = 1.0
        mock_row.weighted_score = 0.85
        mock_row.verdict = "PASS"

        renderer = ScorecardRenderer()
        csv_output = renderer.render_csv([mock_row])

        assert "dimension_id" in csv_output
        assert "Test Dimension" in csv_output
        assert "PASS" in csv_output

    def test_render_csv_multiple_rows(self):
        """Test rendering CSV with multiple rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        mock_row1 = MagicMock()
        mock_row1.dimension_id = "dim_1"
        mock_row1.display_name = "Dimension 1"
        mock_row1.score = 0.85
        mock_row1.weight = 1.0
        mock_row1.weighted_score = 0.85
        mock_row1.verdict = "PASS"

        mock_row2 = MagicMock()
        mock_row2.dimension_id = "dim_2"
        mock_row2.display_name = "Dimension 2"
        mock_row2.score = 0.75
        mock_row2.weight = 0.5
        mock_row2.weighted_score = 0.375
        mock_row2.verdict = "WARN"

        renderer = ScorecardRenderer()
        csv_output = renderer.render_csv([mock_row1, mock_row2])

        assert "Dimension 1" in csv_output
        assert "Dimension 2" in csv_output

    def test_render_markdown_empty(self):
        """Test rendering Markdown with empty rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        renderer = ScorecardRenderer()
        markdown = renderer.render_markdown([])

        assert "No scorecard data available" in markdown

    def test_render_markdown_with_rows(self):
        """Test rendering Markdown with data rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        mock_row = MagicMock()
        mock_row.display_name = "Test Dimension"
        mock_row.score = 0.85
        mock_row.weight = 1.0
        mock_row.weighted_score = 0.85
        mock_row.verdict = "PASS"

        renderer = ScorecardRenderer()
        markdown = renderer.render_markdown([mock_row])

        assert "# Evaluation Scorecard" in markdown
        assert "Test Dimension" in markdown
        assert "85.00%" in markdown
        assert "PASS" in markdown

    def test_render_markdown_multiple_rows(self):
        """Test rendering Markdown with multiple rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        mock_row1 = MagicMock()
        mock_row1.display_name = "Dimension 1"
        mock_row1.score = 0.85
        mock_row1.weight = 1.0
        mock_row1.weighted_score = 0.85
        mock_row1.verdict = "PASS"

        mock_row2 = MagicMock()
        mock_row2.display_name = "Dimension 2"
        mock_row2.score = 0.75
        mock_row2.weight = 0.5
        mock_row2.weighted_score = 0.375
        mock_row2.verdict = "WARN"

        renderer = ScorecardRenderer()
        markdown = renderer.render_markdown([mock_row1, mock_row2])

        assert "Dimension 1" in markdown
        assert "Dimension 2" in markdown

    def test_render_summary_empty(self):
        """Test rendering summary with empty rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        renderer = ScorecardRenderer()
        summary = renderer.render_summary([])

        assert summary["total_dimensions"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0

    def test_render_summary_with_rows(self):
        """Test rendering summary with data rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        mock_row1 = MagicMock()
        mock_row1.score = 0.85
        mock_row1.verdict = "PASS"

        mock_row2 = MagicMock()
        mock_row2.score = 0.75
        mock_row2.verdict = "WARN"

        mock_row3 = MagicMock()
        mock_row3.score = 0.5
        mock_row3.verdict = "FAIL"

        renderer = ScorecardRenderer()
        summary = renderer.render_summary([mock_row1, mock_row2, mock_row3])

        assert summary["total_dimensions"] == 3
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["warnings"] == 1
        assert summary["average_score"] == pytest.approx(0.7)

    def test_render_summary_all_pass(self):
        """Test rendering summary with all passing rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        mock_row = MagicMock()
        mock_row.score = 0.9
        mock_row.verdict = "PASS"

        renderer = ScorecardRenderer()
        summary = renderer.render_summary([mock_row])

        assert summary["passed"] == 1
        assert summary["failed"] == 0
        assert summary["warnings"] == 0

    def test_render_summary_all_fail(self):
        """Test rendering summary with all failing rows."""
        from apps_eval.outputs.scorecard_renderer import ScorecardRenderer

        mock_row = MagicMock()
        mock_row.score = 0.5
        mock_row.verdict = "FAIL"

        renderer = ScorecardRenderer()
        summary = renderer.render_summary([mock_row])

        assert summary["passed"] == 0
        assert summary["failed"] == 1
        assert summary["warnings"] == 0
