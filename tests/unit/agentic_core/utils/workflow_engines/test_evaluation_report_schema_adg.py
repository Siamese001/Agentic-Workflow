"""Test EvaluationReportSchemaAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEvaluationReportSchemaAdg:
    """Test EvaluationReportSchemaAdg functionality."""

    def test_evaluation_report_schema_adg_imports(self):
        """Test evaluation_report_schema_adg module imports."""
        from agentic_core import evaluation_report_schema_adg

        assert evaluation_report_schema_adg is not None

    def test_evaluation_report_schema_adg_class(self):
        """Test EvaluationReportSchemaAdg class exists."""
        from agentic_core import EvaluationReportSchemaAdg

        assert EvaluationReportSchemaAdg is not None

    def test_evaluation_report_schema_adg_callable(self):
        """Test evaluation_report_schema_adg functions are callable."""
        from agentic_core import validate_evaluation_report_schema_adg

        assert callable(validate_evaluation_report_schema_adg)
