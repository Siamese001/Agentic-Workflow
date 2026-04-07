"""Test RunSummaryRenderer functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunSummaryRenderer:
    """Test RunSummaryRenderer functionality."""

    def test_render_json(self):
        """Test rendering summary as JSON."""
        from apps_eval.outputs.run_summary_renderer import RunSummaryRenderer

        mock_summary = MagicMock()
        mock_summary.trace_id = "trace-123"
        mock_summary.app = "test_app"
        mock_summary.version = "1.0.0"
        mock_summary.status = "completed"
        mock_summary.suites_run = 5
        mock_summary.scenarios_run = 10
        mock_summary.scenarios_passed = 8
        mock_summary.overall_score = 0.85
        mock_summary.regressions_detected = 0
        mock_summary.gate_violations = []
        mock_summary.artifacts = []
        mock_summary.error = None
        mock_summary.provenance = {"source": "test"}

        mock_summary.to_dict.return_value = {
            "trace_id": "trace-123",
            "app": "test_app",
            "version": "1.0.0",
            "status": "completed",
        }

        renderer = RunSummaryRenderer()
        json_output = renderer.render_json(mock_summary)

        assert "trace-123" in json_output
        assert "test_app" in json_output

    def test_render_markdown(self):
        """Test rendering summary as Markdown."""
        from apps_eval.outputs.run_summary_renderer import RunSummaryRenderer

        mock_summary = MagicMock()
        mock_summary.trace_id = "trace-123"
        mock_summary.app = "test_app"
        mock_summary.version = "1.0.0"
        mock_summary.status = "completed"
        mock_summary.suites_run = 5
        mock_summary.scenarios_run = 10
        mock_summary.scenarios_passed = 8
        mock_summary.overall_score = 0.85
        mock_summary.regressions_detected = 0
        mock_summary.gate_violations = []
        mock_summary.artifacts = []
        mock_summary.error = None
        mock_summary.provenance = {"source": "test"}

        renderer = RunSummaryRenderer()
        markdown = renderer.render_markdown(mock_summary)

        assert "# Evaluation Run Summary" in markdown
        assert "trace-123" in markdown
        assert "test_app" in markdown
        assert "85.00%" in markdown

    def test_render_markdown_with_violations(self):
        """Test rendering Markdown with gate violations."""
        from apps_eval.outputs.run_summary_renderer import RunSummaryRenderer

        mock_summary = MagicMock()
        mock_summary.trace_id = "trace-123"
        mock_summary.app = "test_app"
        mock_summary.version = "1.0.0"
        mock_summary.status = "completed"
        mock_summary.suites_run = 5
        mock_summary.scenarios_run = 10
        mock_summary.scenarios_passed = 8
        mock_summary.overall_score = 0.85
        mock_summary.regressions_detected = 0
        mock_summary.gate_violations = ["violation_1", "violation_2"]
        mock_summary.artifacts = []
        mock_summary.error = None
        mock_summary.provenance = {"source": "test"}

        renderer = RunSummaryRenderer()
        markdown = renderer.render_markdown(mock_summary)

        assert "## Gate Violations" in markdown
        assert "violation_1" in markdown
        assert "violation_2" in markdown

    def test_render_markdown_with_error(self):
        """Test rendering Markdown with error."""
        from apps_eval.outputs.run_summary_renderer import RunSummaryRenderer

        mock_summary = MagicMock()
        mock_summary.trace_id = "trace-123"
        mock_summary.app = "test_app"
        mock_summary.version = "1.0.0"
        mock_summary.status = "failed"
        mock_summary.suites_run = 0
        mock_summary.scenarios_run = 0
        mock_summary.scenarios_passed = 0
        mock_summary.overall_score = 0.0
        mock_summary.regressions_detected = 0
        mock_summary.gate_violations = []
        mock_summary.artifacts = []
        mock_summary.error = "Test error occurred"
        mock_summary.provenance = {"source": "test"}

        renderer = RunSummaryRenderer()
        markdown = renderer.render_markdown(mock_summary)

        assert "## Error" in markdown
        assert "Test error occurred" in markdown

    def test_render_markdown_with_artifacts(self):
        """Test rendering Markdown with artifacts."""
        from apps_eval.outputs.run_summary_renderer import RunSummaryRenderer

        mock_summary = MagicMock()
        mock_summary.trace_id = "trace-123"
        mock_summary.app = "test_app"
        mock_summary.version = "1.0.0"
        mock_summary.status = "completed"
        mock_summary.suites_run = 5
        mock_summary.scenarios_run = 10
        mock_summary.scenarios_passed = 8
        mock_summary.overall_score = 0.85
        mock_summary.regressions_detected = 0
        mock_summary.gate_violations = []
        mock_summary.artifacts = ["artifact_1.json", "artifact_2.json"]
        mock_summary.error = None
        mock_summary.provenance = {"source": "test"}

        renderer = RunSummaryRenderer()
        markdown = renderer.render_markdown(mock_summary)

        assert "## Artifacts" in markdown
        assert "artifact_1.json" in markdown
        assert "artifact_2.json" in markdown

    def test_render_compact(self):
        """Test rendering as compact dict."""
        from apps_eval.outputs.run_summary_renderer import RunSummaryRenderer

        mock_summary = MagicMock()
        mock_summary.trace_id = "trace-123"
        mock_summary.status = "completed"
        mock_summary.overall_score = 0.85
        mock_summary.gate_violations = []
        mock_summary.error = None

        renderer = RunSummaryRenderer()
        compact = renderer.render_compact(mock_summary)

        assert compact["trace_id"] == "trace-123"
        assert compact["status"] == "completed"
        assert compact["score"] == 0.85
        assert compact["passed"] is True
        assert compact["violations"] == 0

    def test_render_compact_with_violations(self):
        """Test rendering compact dict with violations."""
        from apps_eval.outputs.run_summary_renderer import RunSummaryRenderer

        mock_summary = MagicMock()
        mock_summary.trace_id = "trace-123"
        mock_summary.status = "completed"
        mock_summary.overall_score = 0.85
        mock_summary.gate_violations = ["violation_1"]
        mock_summary.error = None

        renderer = RunSummaryRenderer()
        compact = renderer.render_compact(mock_summary)

        assert compact["passed"] is False
        assert compact["violations"] == 1

    def test_render_compact_with_error(self):
        """Test rendering compact dict with error."""
        from apps_eval.outputs.run_summary_renderer import RunSummaryRenderer

        mock_summary = MagicMock()
        mock_summary.trace_id = "trace-123"
        mock_summary.status = "failed"
        mock_summary.overall_score = 0.0
        mock_summary.gate_violations = []
        mock_summary.error = "Test error"

        renderer = RunSummaryRenderer()
        compact = renderer.render_compact(mock_summary)

        assert compact["passed"] is False
