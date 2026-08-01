from __future__ import annotations

import inspect
import json
from pathlib import Path

import apps_rg.evals.resume_graph_evaluation as facade
from apps_rg.evals.resume_graph import dataset, gates, models, normalization, reporting, validation
from apps_rg.evals.resume_graph.metrics import binding, calibration, proof, retrieval

EVALS_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASE = EVALS_ROOT / "fixtures" / "resume_graph" / "golden_report_case.v1.json"


def _golden_case() -> dict:
    return json.loads(GOLDEN_CASE.read_text(encoding="utf-8"))


def test_compatibility_facade_preserves_exports_and_signatures() -> None:
    golden = _golden_case()

    assert facade.__all__ == golden["expected_exports"]
    assert {
        name: str(inspect.signature(getattr(facade, name))) for name in golden["expected_signatures"]
    } == golden["expected_signatures"]


def test_golden_report_is_semantically_identical_after_modularization() -> None:
    golden = _golden_case()

    report = facade.evaluate_rows(
        golden["rows"],
        golden["profile"],
        allow_internal_rows=True,
        source_ref=golden["source_ref"],
    )

    assert report == golden["expected_report"]
    assert (
        report["deterministic_digest"] == "1ecf1ee561da3e1df5cbcd02227e1066379741f1aef031bef421830eed9557b7"
    )


def test_extracted_symbols_have_single_module_owners() -> None:
    expected_owners = {
        dataset._mapping: "apps_rg.evals.resume_graph.dataset",
        gates._gate_results: "apps_rg.evals.resume_graph.gates",
        normalization._normalize_rows: "apps_rg.evals.resume_graph.normalization",
        reporting._base_report: "apps_rg.evals.resume_graph.reporting",
        validation._validate_dataset: "apps_rg.evals.resume_graph.validation",
        binding._valid_review_ref_pair: "apps_rg.evals.resume_graph.metrics.binding",
        calibration.fit_isotonic_pav: "apps_rg.evals.resume_graph.metrics.calibration",
        proof._unique_proof_rows: "apps_rg.evals.resume_graph.metrics.proof",
        retrieval.recall_at_k: "apps_rg.evals.resume_graph.metrics.retrieval",
        models.IsotonicModel: "apps_rg.evals.resume_graph.models",
    }

    assert {symbol.__module__ for symbol in expected_owners} == set(expected_owners.values())
    for symbol, module_name in expected_owners.items():
        assert symbol.__module__ == module_name


def test_facade_reexports_the_extracted_public_implementations() -> None:
    assert facade.recall_at_k is retrieval.recall_at_k
    assert facade.ndcg_at_k is retrieval.ndcg_at_k
    assert facade.reciprocal_rank is retrieval.reciprocal_rank
    assert facade.fit_isotonic_pav is calibration.fit_isotonic_pav
    assert facade.build_sanitized_ci_receipt is reporting.build_sanitized_ci_receipt
    assert facade.IsotonicModel is models.IsotonicModel
