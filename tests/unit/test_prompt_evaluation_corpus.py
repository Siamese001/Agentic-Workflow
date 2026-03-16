"""Data-driven tests for the prompt governance evaluation corpus.

Covers all four YAML files in data/prompt_governance/evaluations/ via
EvaluationLoader, plus full branch coverage of EvaluationLoader itself.

BRANCH_INVENTORY
================
File: agentic_core/prompt_governance/core/evaluation_loader.py
- EvaluationLoader.__init__
  | not isinstance(eval_dir, Path)          -> TypeError           | test_init_non_path_raises_type_error
  | not eval_dir.exists()                   -> ValueError          | test_init_nonexistent_dir_raises_value_error
  | not eval_dir.is_dir()                   -> ValueError          | test_init_file_path_raises_value_error
  | happy path                              -> ok                  | all corpus tests (implicit)
- EvaluationLoader.load_eval_set
  | empty/non-str name                      -> ValueError          | test_empty_name_raises_value_error
  | file missing                            -> EvalLoadError       | test_missing_file_raises_eval_load_error
  | path is not a file                      -> EvalLoadError       | (structural; covered by missing_file path)
  | yaml.YAMLError                          -> EvalLoadError       | test_malformed_yaml_raises_eval_load_error
  | OSError                                 -> EvalLoadError       | test_os_error_raises_eval_load_error
  | root not a dict                         -> EvalSchemaError     | test_non_dict_root_raises_eval_schema_error
  | cache hit (name already loaded)         -> same object         | test_cache_hit_returns_same_object
  | happy path (name not in cache)          -> loaded dict         | all corpus tests
- EvaluationLoader.clear_cache
  | clears _cache                           -> empty               | test_clear_cache_forces_reread
- EvaluationLoader.cache_info
  | returns counts                          -> dict                | test_cache_info_reflects_loaded_items
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.prompt_governance.core.evaluation_loader import (
    EvalLoadError,
    EvalSchemaError,
    EvaluationLoader,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_prompt_evaluation_corpus")
_emit_applies_guardrail("p0", "test_prompt_evaluation_corpus", "p0_governance")
_emit_reads_policy_state("p0", "test_prompt_evaluation_corpus", "policy_binding")
_emit_snapshots_state("p0", "test_prompt_evaluation_corpus", "state_snapshot")
emit_replay_key("p0", "test_prompt_evaluation_corpus")
emit_determinism_digest("p0", "test_prompt_evaluation_corpus")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Fixture: canonical evaluations directory
# ---------------------------------------------------------------------------

EVAL_DIR = Path(__file__).parent.parent.parent / "data" / "prompt_governance" / "evaluations"


@pytest.fixture(scope="module")
def loader() -> EvaluationLoader:
    assert EVAL_DIR.is_dir(), f"Evaluations directory not found: {EVAL_DIR}"
    return EvaluationLoader(EVAL_DIR)


# ===========================================================================
# TestEvalSetsCorpus
# ===========================================================================


class TestEvalSetsCorpus:
    def test_loads_without_error(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("eval_sets")
        assert isinstance(data, dict)

    def test_resume_engine_tests_present(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("eval_sets")
        suites = data["evaluation_sets"]["test_suites"]
        assert "resume_engine_tests" in suites, "resume_engine_tests missing from eval_sets"

    def test_outreach_engine_tests_present(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("eval_sets")
        suites = data["evaluation_sets"]["test_suites"]
        assert "outreach_engine_tests" in suites, "outreach_engine_tests missing from eval_sets"

    def test_performance_benchmarks_present(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("eval_sets")
        assert "performance_benchmarks" in data["evaluation_sets"], (
            "performance_benchmarks missing from eval_sets"
        )

    def _collect_named_cases(self, node: object) -> list[dict]:
        """Recursively collect every dict that has a 'name' key."""
        results: list[dict] = []
        if isinstance(node, dict):
            if "name" in node:
                results.append(node)
            for v in node.values():
                results.extend(self._collect_named_cases(v))
        elif isinstance(node, list):
            for item in node:
                results.extend(self._collect_named_cases(item))
        return results

    def test_all_named_cases_have_description(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("eval_sets")
        cases = self._collect_named_cases(data)
        missing = [c["name"] for c in cases if not c.get("description")]
        assert not missing, f"Named cases missing description: {missing}"


# ===========================================================================
# TestRubricCorpus
# ===========================================================================


class TestRubricCorpus:
    def test_loads_without_error(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("rubric")
        assert isinstance(data, dict)

    def test_all_criteria_have_weight(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("rubric")
        criteria = data["prompt_evaluation_rubric"]["evaluation_criteria"]
        missing: list[str] = []
        for category, sub in criteria.items():
            if isinstance(sub, dict):
                for criterion, details in sub.items():
                    if isinstance(details, dict) and "weight" not in details:
                        missing.append(f"{category}.{criterion}")
        assert not missing, f"Criteria missing weight: {missing}"

    def test_weights_sum_to_one_per_category(self, loader: EvaluationLoader) -> None:
        """Validate that the specialized_rubrics scoring_weights sum to 1.0 per engine."""
        data = loader.load_eval_set("rubric")
        specialized = data["prompt_evaluation_rubric"]["specialized_rubrics"]
        for engine_name, engine_cfg in specialized.items():
            if not isinstance(engine_cfg, dict):
                continue
            scoring_weights = engine_cfg.get("scoring_weights", {})
            if not scoring_weights:
                continue
            total = sum(float(v) for v in scoring_weights.values())
            assert abs(total - 1.0) <= 0.01, (
                f"Engine '{engine_name}' scoring_weights sum to {total:.4f}, expected 1.0 ±0.01"
            )

    def test_passing_threshold_defined(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("rubric")
        threshold = data["prompt_evaluation_rubric"]["scoring_methodology"]["overall_score_calculation"][
            "passing_threshold"
        ]
        assert isinstance(threshold, (int, float)), "passing_threshold must be numeric"

    def test_grade_classifications_complete(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("rubric")
        grades = data["prompt_evaluation_rubric"]["scoring_methodology"]["grade_classifications"]
        required = {"A_plus", "A", "B_plus", "B", "C_plus", "C", "D", "F"}
        present = set(grades.keys())
        missing = required - present
        assert not missing, f"Missing grade classifications: {missing}"


# ===========================================================================
# TestRegressionTestsCorpus
# ===========================================================================


class TestRegressionTestsCorpus:
    def test_loads_without_error(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("regression_tests")
        assert isinstance(data, dict)

    def test_resume_engine_regression_present(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("regression_tests")
        suites = data["regression_tests"]["core_test_suites"]
        assert "resume_engine_regression" in suites, "resume_engine_regression missing"

    def test_outreach_engine_regression_present(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("regression_tests")
        suites = data["regression_tests"]["core_test_suites"]
        assert "outreach_engine_regression" in suites, "outreach_engine_regression missing"

    def _collect_regression_cases(self, node: object) -> list[dict]:
        results: list[dict] = []
        if isinstance(node, dict):
            if "name" in node and "success_criteria" in node:
                results.append(node)
            for v in node.values():
                results.extend(self._collect_regression_cases(v))
        elif isinstance(node, list):
            for item in node:
                results.extend(self._collect_regression_cases(item))
        return results

    def test_all_cases_have_success_criteria(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("regression_tests")
        cases = self._collect_regression_cases(data)
        assert cases, "No regression cases with success_criteria found"
        missing = [c["name"] for c in cases if not c.get("success_criteria")]
        assert not missing, f"Cases missing success_criteria: {missing}"

    def test_no_case_missing_description(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("regression_tests")
        cases = self._collect_regression_cases(data)
        missing = [c["name"] for c in cases if not c.get("description")]
        assert not missing, f"Regression cases missing description: {missing}"


# ===========================================================================
# TestStyleChecksCorpus
# ===========================================================================


class TestStyleChecksCorpus:
    def _collect_named_checks(self, node: object) -> list[dict]:
        results: list[dict] = []
        if isinstance(node, dict):
            if "name" in node and "checks" in node:
                results.append(node)
            for v in node.values():
                results.extend(self._collect_named_checks(v))
        elif isinstance(node, list):
            for item in node:
                results.extend(self._collect_named_checks(item))
        return results

    def test_loads_without_error(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("style_checks")
        assert isinstance(data, dict)

    def test_resume_and_outreach_engine_styles_present(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("style_checks")
        engine_checks = data["style_checks"]["engine_specific_checks"]
        assert "resume_engine_style" in engine_checks, "resume_engine_style missing"
        assert "outreach_engine_style" in engine_checks, "outreach_engine_style missing"

    def test_all_checks_have_validation_method(self, loader: EvaluationLoader) -> None:
        """Engine-specific style checks (under engine_specific_checks) must have validation_method."""
        data = loader.load_eval_set("style_checks")
        engine_checks = data["style_checks"]["engine_specific_checks"]
        items = self._collect_named_checks(engine_checks)
        missing = [c["name"] for c in items if not c.get("validation_method")]
        assert not missing, f"Engine-specific style checks missing validation_method: {missing}"

    def test_no_duplicate_check_names(self, loader: EvaluationLoader) -> None:
        data = loader.load_eval_set("style_checks")
        items = self._collect_named_checks(data)
        names = [c["name"] for c in items]
        duplicates = {n for n in names if names.count(n) > 1}
        assert not duplicates, f"Duplicate style check names: {duplicates}"


# ===========================================================================
# TestEvaluationLoaderErrorPaths  (branch coverage)
# ===========================================================================


class TestEvaluationLoaderErrorPaths:
    # --- __init__ guards ---

    def test_init_non_path_raises_type_error(self) -> None:
        with pytest.raises(TypeError, match="must be a Path"):
            EvaluationLoader("/some/string/path")  # type: ignore[arg-type]

    def test_init_nonexistent_dir_raises_value_error(self, tmp_path: Path) -> None:
        missing = tmp_path / "does_not_exist"
        with pytest.raises(ValueError, match="does not exist"):
            EvaluationLoader(missing)

    def test_init_file_path_raises_value_error(self, tmp_path: Path) -> None:
        f = tmp_path / "not_a_dir.yaml"
        f.write_text("data: 1")
        with pytest.raises(ValueError, match="must be a directory"):
            EvaluationLoader(f)

    # --- load_eval_set guards ---

    def test_empty_name_raises_value_error(self, tmp_path: Path) -> None:
        ldr = EvaluationLoader(tmp_path)
        with pytest.raises(ValueError):
            ldr.load_eval_set("")

    def test_none_name_raises_value_error(self, tmp_path: Path) -> None:
        ldr = EvaluationLoader(tmp_path)
        with pytest.raises((ValueError, AttributeError)):
            ldr.load_eval_set(None)  # type: ignore[arg-type]

    def test_missing_file_raises_eval_load_error(self, tmp_path: Path) -> None:
        ldr = EvaluationLoader(tmp_path)
        with pytest.raises(EvalLoadError, match="not found"):
            ldr.load_eval_set("nonexistent")

    def test_malformed_yaml_raises_eval_load_error(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("key: [\nunclosed bracket", encoding="utf-8")
        ldr = EvaluationLoader(tmp_path)
        with pytest.raises(EvalLoadError, match="Invalid YAML"):
            ldr.load_eval_set("bad")

    def test_os_error_raises_eval_load_error(self, tmp_path: Path) -> None:
        target = tmp_path / "unreadable.yaml"
        target.write_text("data: 1", encoding="utf-8")
        ldr = EvaluationLoader(tmp_path)
        with patch("builtins.open", side_effect=OSError("permission denied")):
            with pytest.raises(EvalLoadError, match="Cannot read"):
                ldr.load_eval_set("unreadable")

    def test_non_dict_root_raises_eval_schema_error(self, tmp_path: Path) -> None:
        list_yaml = tmp_path / "list_root.yaml"
        list_yaml.write_text("- item1\n- item2\n", encoding="utf-8")
        ldr = EvaluationLoader(tmp_path)
        with pytest.raises(EvalSchemaError, match="root must be a dict"):
            ldr.load_eval_set("list_root")

    def test_non_dict_root_scalar_raises_eval_schema_error(self, tmp_path: Path) -> None:
        scalar_yaml = tmp_path / "scalar.yaml"
        scalar_yaml.write_text("just a string\n", encoding="utf-8")
        ldr = EvaluationLoader(tmp_path)
        with pytest.raises(EvalSchemaError):
            ldr.load_eval_set("scalar")

    # --- cache behaviour ---

    def test_cache_hit_returns_same_object(self, tmp_path: Path) -> None:
        good = tmp_path / "good.yaml"
        good.write_text("key: value\n", encoding="utf-8")
        ldr = EvaluationLoader(tmp_path)
        first = ldr.load_eval_set("good")
        second = ldr.load_eval_set("good")
        assert first is second, "Cache hit must return the identical object"

    def test_clear_cache_forces_reread(self, tmp_path: Path) -> None:
        f = tmp_path / "mutable.yaml"
        f.write_text("version: 1\n", encoding="utf-8")
        ldr = EvaluationLoader(tmp_path)
        first = ldr.load_eval_set("mutable")
        assert first["version"] == 1

        ldr.clear_cache()
        f.write_text("version: 2\n", encoding="utf-8")
        second = ldr.load_eval_set("mutable")
        assert second["version"] == 2, "clear_cache must allow fresh read"
        assert first is not second

    def test_cache_info_reflects_loaded_items(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.yaml"
        f2 = tmp_path / "b.yaml"
        f1.write_text("x: 1\n", encoding="utf-8")
        f2.write_text("y: 2\n", encoding="utf-8")
        ldr = EvaluationLoader(tmp_path)
        assert ldr.cache_info()["cached_items"] == 0
        ldr.load_eval_set("a")
        assert ldr.cache_info()["cached_items"] == 1
        ldr.load_eval_set("b")
        info = ldr.cache_info()
        assert info["cached_items"] == 2
        assert set(info["cache_keys"]) == {"a", "b"}

    def test_cache_info_after_clear(self, tmp_path: Path) -> None:
        f = tmp_path / "c.yaml"
        f.write_text("z: 3\n", encoding="utf-8")
        ldr = EvaluationLoader(tmp_path)
        ldr.load_eval_set("c")
        ldr.clear_cache()
        assert ldr.cache_info()["cached_items"] == 0
        assert ldr.cache_info()["cache_keys"] == []
