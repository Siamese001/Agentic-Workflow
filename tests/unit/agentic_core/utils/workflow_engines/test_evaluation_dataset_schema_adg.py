"""Test EvaluationDatasetSchemaAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEvaluationDatasetSchemaAdg:
    """Test EvaluationDatasetSchemaAdg functionality."""

    def test_evaluation_dataset_schema_adg_imports(self):
        """Test evaluation_dataset_schema_adg module imports."""
        from agentic_core import evaluation_dataset_schema_adg

        assert evaluation_dataset_schema_adg is not None

    def test_evaluation_dataset_schema_adg_class(self):
        """Test EvaluationDatasetSchemaAdg class exists."""
        from agentic_core import EvaluationDatasetSchemaAdg

        assert EvaluationDatasetSchemaAdg is not None

    def test_evaluation_dataset_schema_adg_callable(self):
        """Test evaluation_dataset_schema_adg functions are callable."""
        from agentic_core import validate_evaluation_dataset_schema_adg

        assert callable(validate_evaluation_dataset_schema_adg)
