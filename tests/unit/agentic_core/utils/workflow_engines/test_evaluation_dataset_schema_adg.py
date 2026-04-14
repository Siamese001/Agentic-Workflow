"""Tests for agentic_core/utils/schemas/evaluation_dataset_schema.py hardening changes."""

import json

import pytest


@pytest.mark.unit
class TestEvaluationDatasetSchemaAdg:
    """Tests for _normalize_json_path, atomic save_to_file, and load_from_file validation."""

    def test_normalize_json_path_non_json_raises(self, tmp_path):
        """_normalize_json_path raises ValueError when suffix is not .json."""
        from agentic_core.utils.schemas.evaluation_dataset_schema import _normalize_json_path

        with pytest.raises(ValueError, match=r"\.json"):
            _normalize_json_path(tmp_path / "data.txt", must_exist=False)

    def test_normalize_json_path_json_suffix_accepted(self, tmp_path):
        """_normalize_json_path returns a resolved Path for a valid .json path."""
        from agentic_core.utils.schemas.evaluation_dataset_schema import _normalize_json_path

        result = _normalize_json_path(tmp_path / "data.json", must_exist=False)
        assert result.suffix == ".json"

    def test_save_load_roundtrip_preserves_data(self, tmp_path):
        """save_to_file + load_from_file round-trip preserves all example fields."""
        from agentic_core.utils.schemas.evaluation_dataset_schema import (
            EvaluationDataset,
            EvaluationExample,
        )

        example = EvaluationExample(
            query="What is AI?",
            ground_truth_documents=["doc1"],
            expected_answer="Artificial Intelligence",
        )
        dataset = EvaluationDataset(
            examples=[example],
            name="test_ds",
            version="1.0",
            description="unit test",
        )
        target = tmp_path / "ds.json"
        dataset.save_to_file(target)
        loaded = EvaluationDataset.load_from_file(target)
        assert loaded.name == "test_ds"
        assert len(loaded.examples) == 1
        assert loaded.examples[0].query == "What is AI?"

    def test_load_from_file_non_dict_json_raises(self, tmp_path):
        """load_from_file raises ValueError when top-level JSON is not a dict."""
        from agentic_core.utils.schemas.evaluation_dataset_schema import EvaluationDataset

        bad_file = tmp_path / "bad.json"
        bad_file.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
        with pytest.raises(ValueError, match="top-level JSON object"):
            EvaluationDataset.load_from_file(bad_file)
