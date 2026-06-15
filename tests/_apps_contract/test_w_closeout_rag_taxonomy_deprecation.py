"""Closeout verification — W1 RAG dims, W2 taxonomy, W4 deprecation shim.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-closeout-b7c9d2.md``.

Covers:
- W1.P1/P2: 5 grounded apps carry the 3 RAG dims with OpenAI baselines.
- W2.P1/P2: ScoreDimension.taxonomy_class added + validated; gate emits
  TAXONOMY_COVERAGE INFO for unannotated dims.
- W4.P1: legacy_yaml_deprecation.emit_deprecation issues DeprecationWarning +
  is idempotent per path per process.
"""

from __future__ import annotations

import subprocess
import sys
import warnings
from pathlib import Path

import pytest
import yaml

from agentic_core.L4_state.contracts.app_domain import (
    AppDomainContractError,
    ScoreDimension,
    TAXONOMY_CLASS_VOCAB,
)
from apps_shared.config.legacy_yaml_deprecation import (
    emit_deprecation,
    reset_warning_registry,
)
from ops_scripts.ci.check_grounded_rag_active import _GROUNDED_APPS

REPO_ROOT = Path(__file__).resolve().parents[2]


RAG_DIMS = ("context_recall", "context_precision", "answer_relevancy")

OPENAI_BASELINES = {
    "context_recall": 0.85,
    "context_precision": 0.70,
    "answer_relevancy": 0.80,
}

GROUNDED_APPS = sorted(_GROUNDED_APPS)


class TestRagDimsPresent:
    @pytest.mark.parametrize("app", GROUNDED_APPS)
    def test_all_three_rag_dims_added(self, app: str) -> None:
        rubric_path = REPO_ROOT / app / "config" / "domain_contract" / "eval_rubrics.yaml"
        docs = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
        assert isinstance(docs, list) and docs
        dims = {d["dimension_id"] for d in docs[0].get("score_dimensions", [])}
        for rag_dim in RAG_DIMS:
            assert rag_dim in dims, f"{app}: missing RAG dim {rag_dim}"

    @pytest.mark.parametrize("app", GROUNDED_APPS)
    def test_openai_baseline_thresholds(self, app: str) -> None:
        rubric_path = REPO_ROOT / app / "config" / "domain_contract" / "eval_rubrics.yaml"
        docs = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
        rag_by_id = {
            d["dimension_id"]: d
            for d in docs[0].get("score_dimensions", [])
            if d.get("dimension_id") in RAG_DIMS
        }
        for dim_id, expected in OPENAI_BASELINES.items():
            d = rag_by_id[dim_id]
            assert abs(d["min_required_score"] - expected) < 1e-9, (
                f"{app}.{dim_id}: baseline {d['min_required_score']} != {expected}"
            )
            assert d["grader_type"] == "llm_as_judge"
            assert d["fail_closed_if_unknown"] is False, (
                f"{app}.{dim_id} must be fail-open until producers wire"
            )

    @pytest.mark.parametrize("app", GROUNDED_APPS)
    def test_threshold_profile_declares_intentional_failopen(self, app: str) -> None:
        tp_path = REPO_ROOT / app / "config" / "domain_contract" / "threshold_profiles.yaml"
        docs = yaml.safe_load(tp_path.read_text(encoding="utf-8"))
        failopen = set(docs[0].get("intentional_failopen_dims", []) or [])
        for dim_id in RAG_DIMS:
            assert dim_id in failopen, (
                f"{app}: threshold profile must annotate {dim_id} as intentional_failopen"
            )


class TestTaxonomyClassSchema:
    def test_vocab_has_three_classes(self) -> None:
        assert TAXONOMY_CLASS_VOCAB == frozenset(
            {"capability", "regression", "tracked_metric"}
        )

    @pytest.mark.parametrize("cls", ["capability", "regression", "tracked_metric"])
    def test_valid_class_accepted(self, cls: str) -> None:
        dim = ScoreDimension(
            dimension_id="d", description="t", weight=0.1,
            grader_type="deterministic", taxonomy_class=cls,
        )
        assert dim.taxonomy_class == cls

    def test_invalid_class_rejected(self) -> None:
        with pytest.raises(AppDomainContractError, match="taxonomy_class"):
            ScoreDimension(
                dimension_id="d", description="t", weight=0.1,
                grader_type="deterministic", taxonomy_class="invalid",
            )

    def test_empty_accepted(self) -> None:
        dim = ScoreDimension(
            dimension_id="d", description="t", weight=0.1, grader_type="deterministic",
        )
        assert dim.taxonomy_class == ""


class TestGateTaxonomyCoverage:
    def test_gate_emits_info_for_unannotated_dims(self) -> None:
        """Gate surfaces TAXONOMY_COVERAGE INFO for every unannotated dim.
        All current rubric dims are unannotated, so the count should be
        high (≥ 30 across 8 apps)."""
        gate = REPO_ROOT / "ops_scripts" / "ci" / "check_app_domain_harness_parity.py"
        report_path = REPO_ROOT / "artifacts" / "ci" / "harness_parity_w5p3.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(gate), "--json", "--report", str(report_path)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        import json
        report = json.loads(report_path.read_text(encoding="utf-8"))
        infos = [f for f in report["findings"] if f["check_id"] == "TAXONOMY_COVERAGE"]
        assert len(infos) >= 30, (
            f"Expected many TAXONOMY_COVERAGE INFOs until rubrics are annotated; "
            f"got {len(infos)}"
        )


class TestLegacyDeprecation:
    def test_emits_deprecation_warning(self, tmp_path: Path) -> None:
        reset_warning_registry()
        fake = tmp_path / "legacy_policies.yaml"
        fake.write_text("x: 1", encoding="utf-8")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            emit_deprecation(
                path=fake,
                since="2026-05-03",
                removal_target="2026-09-01",
                canonical_path="apps_x/config/domain_contract/threshold_profiles.yaml",
            )
        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert dep, "emit_deprecation must raise DeprecationWarning"
        assert "DEPRECATED" in str(dep[0].message)

    def test_idempotent_per_path(self, tmp_path: Path) -> None:
        reset_warning_registry()
        fake = tmp_path / "legacy2.yaml"
        fake.write_text("x: 1", encoding="utf-8")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            emit_deprecation(path=fake, since="2026", removal_target="2027", canonical_path="x")
            emit_deprecation(path=fake, since="2026", removal_target="2027", canonical_path="x")
        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert len(dep) == 1, "same path must only warn once per process"
