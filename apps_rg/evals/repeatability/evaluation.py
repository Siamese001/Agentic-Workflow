"""Compare decisions in sealed stored runs without invoking Apps RG runtime."""

from __future__ import annotations

import itertools
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from apps_rg.evals.resume_graph.reporting import canonical_digest

_ROOT = Path(__file__).resolve().parent
_REGISTRY = _ROOT / "scenarios.v1.yaml"
RUN_SCHEMA = "apps_rg.repeatability_run.v1"
RUN_SET_SCHEMA = "apps_rg.repeatability_run_set.v1"
RECEIPT_SCHEMA = "apps_rg.repeatability_receipt.v1"
_RUN_FIELDS = {
    "schema_version",
    "execution_id",
    "execution_receipt_digest",
    "independent_execution_attested",
    "retrieved_candidate_ids",
    "selected_evidence_ids",
    "selected_graph_path_ids",
    "material_claim_ids",
    "bindings",
    "section_decisions",
    "grounding_dispositions",
    "final_disposition",
    "output_quality_scores",
    "output_text_by_section",
    "record_digest",
}
_HEX = re.compile(r"^[0-9a-f]{64}$")


def _registry() -> tuple[dict[str, str], str]:
    value = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
    scenarios = {row["scenario_id"]: row["expected_disposition"] for row in value["scenarios"]}
    return scenarios, canonical_digest(value)


def seal_run(run: Mapping[str, Any]) -> dict[str, Any]:
    sealed = dict(run)
    sealed["record_digest"] = canonical_digest(
        {key: value for key, value in sealed.items() if key != "record_digest"}
    )
    return sealed


def seal_run_set(run_set: Mapping[str, Any]) -> dict[str, Any]:
    sealed = dict(run_set)
    sealed["scenarios"] = [
        {**scenario, "runs": [seal_run(run) for run in scenario.get("runs", [])]}
        for scenario in run_set.get("scenarios", [])
    ]
    sealed["bundle_digest"] = canonical_digest(
        {key: value for key, value in sealed.items() if key != "bundle_digest"}
    )
    return sealed


def scenario_registry_digest() -> str:
    return _registry()[1]


def _jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    a, b = set(left), set(right)
    return len(a & b) / len(a | b) if a or b else 1.0


def _pairwise_mean(runs: Sequence[Mapping[str, Any]], scorer: Any) -> float:
    values = [scorer(left, right) for left, right in itertools.combinations(runs, 2)]
    return sum(values) / len(values) if values else 1.0


def _mapping_stability(runs: Sequence[Mapping[str, Any]], field: str) -> float:
    return _pairwise_mean(runs, lambda left, right: float(left[field] == right[field]))


def _score_stability(runs: Sequence[Mapping[str, Any]]) -> float:
    def score(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
        keys = set(left["output_quality_scores"]) | set(right["output_quality_scores"])
        if not keys:
            return 1.0
        delta = sum(
            abs(float(left["output_quality_scores"].get(key, 0)) - float(right["output_quality_scores"].get(key, 0)))
            for key in keys
        ) / len(keys)
        return max(0.0, 1.0 - min(delta / 4.0, 1.0))

    return _pairwise_mean(runs, score)


def _validate_run(run: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if set(run) != _RUN_FIELDS or run.get("schema_version") != RUN_SCHEMA:
        reasons.append("RUN_SCHEMA_INVALID")
    if not isinstance(run.get("execution_id"), str) or not run.get("execution_id"):
        reasons.append("EXECUTION_ID_INVALID")
    if not _HEX.fullmatch(str(run.get("execution_receipt_digest", ""))):
        reasons.append("EXECUTION_RECEIPT_DIGEST_INVALID")
    if run.get("independent_execution_attested") is not True:
        reasons.append("INDEPENDENT_EXECUTION_NOT_ATTESTED")
    for field in (
        "retrieved_candidate_ids",
        "selected_evidence_ids",
        "selected_graph_path_ids",
        "material_claim_ids",
    ):
        value = run.get(field)
        if (
            not isinstance(value, list)
            or any(not isinstance(item, str) or not item for item in value)
            or len(set(value)) != len(value)
        ):
            reasons.append(f"{field.upper()}_INVALID")
    for field in (
        "bindings",
        "section_decisions",
        "grounding_dispositions",
        "output_quality_scores",
        "output_text_by_section",
    ):
        if not isinstance(run.get(field), Mapping):
            reasons.append(f"{field.upper()}_INVALID")
    grounding = run.get("grounding_dispositions")
    if isinstance(grounding, Mapping) and any(
        not isinstance(key, str)
        or not key
        or value not in {"SUPPORTED", "PARTIAL", "UNSUPPORTED", "UNKNOWN"}
        for key, value in grounding.items()
    ):
        reasons.append("GROUNDING_DISPOSITIONS_INVALID")
    scores = run.get("output_quality_scores")
    if isinstance(scores, Mapping) and any(
        not isinstance(key, str)
        or not key
        or not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
        for key, value in scores.items()
    ):
        reasons.append("OUTPUT_QUALITY_SCORES_INVALID")
    text = run.get("output_text_by_section")
    if isinstance(text, Mapping) and any(
        not isinstance(key, str) or not key or not isinstance(value, str)
        for key, value in text.items()
    ):
        reasons.append("OUTPUT_TEXT_BY_SECTION_INVALID")
    if run.get("final_disposition") not in {"GENERATE", "ESCALATE", "ABSTAIN"}:
        reasons.append("FINAL_DISPOSITION_INVALID")
    digest = run.get("record_digest")
    if not _HEX.fullmatch(str(digest or "")) or digest != canonical_digest(
        {key: value for key, value in run.items() if key != "record_digest"}
    ):
        reasons.append("RUN_DIGEST_INVALID")
    return sorted(set(reasons))


def evaluate_run_set(run_set: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate G5 from stored artifacts only; this function has no runtime hook."""

    registry, registry_digest = _registry()
    unknown_reasons: list[str] = []
    if run_set.get("schema_version") != RUN_SET_SCHEMA:
        unknown_reasons.append("RUN_SET_SCHEMA_INVALID")
    if run_set.get("scenario_registry_digest") != registry_digest:
        unknown_reasons.append("SCENARIO_REGISTRY_DIGEST_INVALID")
    digest = run_set.get("bundle_digest")
    if not _HEX.fullmatch(str(digest or "")) or digest != canonical_digest(
        {key: value for key, value in run_set.items() if key != "bundle_digest"}
    ):
        unknown_reasons.append("RUN_SET_DIGEST_INVALID")
    scenarios = run_set.get("scenarios")
    if not isinstance(scenarios, list):
        scenarios = []
        unknown_reasons.append("SCENARIO_SET_INVALID")
    by_id = {
        scenario.get("scenario_id"): scenario
        for scenario in scenarios
        if isinstance(scenario, Mapping) and isinstance(scenario.get("scenario_id"), str)
    }
    if set(by_id) != set(registry) or len(by_id) != len(scenarios):
        unknown_reasons.append("REQUIRED_SCENARIO_SET_INCOMPLETE")

    scenario_results: list[dict[str, Any]] = []
    for scenario_id in sorted(registry):
        scenario = by_id.get(scenario_id, {})
        runs = scenario.get("runs", []) if isinstance(scenario, Mapping) else []
        reasons: list[str] = []
        if not isinstance(runs, list):
            runs = []
            reasons.append("RUN_LIST_INVALID")
        for run in runs:
            if not isinstance(run, Mapping):
                reasons.append("RUN_SCHEMA_INVALID")
            else:
                reasons.extend(_validate_run(run))
        execution_ids = [
            run.get("execution_id")
            for run in runs
            if isinstance(run, Mapping) and isinstance(run.get("execution_id"), str)
        ]
        receipt_ids = [
            run.get("execution_receipt_digest")
            for run in runs
            if isinstance(run, Mapping) and isinstance(run.get("execution_receipt_digest"), str)
        ]
        if (
            len(runs) < 3
            or len(execution_ids) != len(runs)
            or len(receipt_ids) != len(runs)
            or len(set(execution_ids)) < 3
            or len(set(receipt_ids)) < 3
        ):
            reasons.append("THREE_INDEPENDENT_EXECUTIONS_REQUIRED")

        metrics: dict[str, Any] = {}
        critical_divergence_count = 0
        expected_mismatch_count = 0
        prose_variation_pair_count = 0
        if runs and not reasons:
            metrics = {
                "retrieved_candidate_stability": _pairwise_mean(
                    runs, lambda left, right: _jaccard(left["retrieved_candidate_ids"], right["retrieved_candidate_ids"])
                ),
                "evidence_selection_stability": _pairwise_mean(
                    runs,
                    lambda left, right: (
                        _jaccard(left["selected_evidence_ids"], right["selected_evidence_ids"])
                        + _jaccard(left["selected_graph_path_ids"], right["selected_graph_path_ids"])
                    ) / 2.0,
                ),
                "material_claim_identity_stability": _pairwise_mean(
                    runs, lambda left, right: _jaccard(left["material_claim_ids"], right["material_claim_ids"])
                ),
                "binding_stability": _mapping_stability(runs, "bindings"),
                "grounding_disposition_stability": _mapping_stability(runs, "grounding_dispositions"),
                "semantic_output_stability": _mapping_stability(runs, "section_decisions"),
                "output_quality_score_stability": _score_stability(runs),
            }
            for left, right in itertools.combinations(runs, 2):
                if left["grounding_dispositions"] != right["grounding_dispositions"]:
                    critical_divergence_count += 1
                if left["final_disposition"] != right["final_disposition"]:
                    critical_divergence_count += 1
                if left["output_text_by_section"] != right["output_text_by_section"]:
                    prose_variation_pair_count += 1
            expected_mismatch_count = sum(
                run["final_disposition"] != registry[scenario_id] for run in runs
            )
        metrics.update(
            {
                "critical_divergence_count": critical_divergence_count,
                "expected_disposition_mismatch_count": expected_mismatch_count,
                "prose_variation_pair_count": prose_variation_pair_count,
            }
        )
        status = "UNKNOWN" if reasons else "FAIL" if critical_divergence_count or expected_mismatch_count else "PASS"
        scenario_results.append(
            {
                "scenario_id": scenario_id,
                "expected_disposition": registry[scenario_id],
                "independent_execution_count": len(set(receipt_ids)),
                "status": status,
                "metrics": metrics,
                "unknown_reasons": sorted(set(reasons)),
            }
        )

    unknown_reasons.extend(
        reason for result in scenario_results for reason in result["unknown_reasons"]
    )
    critical_count = sum(result["metrics"]["critical_divergence_count"] for result in scenario_results)
    mismatch_count = sum(
        result["metrics"]["expected_disposition_mismatch_count"] for result in scenario_results
    )
    status = "UNKNOWN" if unknown_reasons else "FAIL" if critical_count or mismatch_count else "PASS"
    measured_results = [result for result in scenario_results if result["status"] != "UNKNOWN"]
    stability_names = (
        "retrieved_candidate_stability",
        "evidence_selection_stability",
        "material_claim_identity_stability",
        "binding_stability",
        "grounding_disposition_stability",
        "semantic_output_stability",
        "output_quality_score_stability",
    )
    aggregate_stability = {
        name: (
            sum(result["metrics"][name] for result in measured_results) / len(measured_results)
            if measured_results
            else None
        )
        for name in stability_names
    }
    body: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA,
        "gate_id": "G5",
        "score_groups": ["runtime_repeatability"],
        "evaluation_id": run_set.get("evaluation_id"),
        "source_run_set_digest": run_set.get("bundle_digest"),
        "scenario_registry_digest": registry_digest,
        "status": status,
        "metrics": {
            **aggregate_stability,
            "required_scenario_count": len(registry),
            "measured_scenario_count": sum(result["status"] != "UNKNOWN" for result in scenario_results),
            "critical_divergence_count": critical_count,
            "expected_disposition_mismatch_count": mismatch_count,
            "evidence_instability_scenario_count": sum(
                result["metrics"].get("evidence_selection_stability") != 1.0
                for result in scenario_results
                if result["status"] != "UNKNOWN"
            ),
            "prose_variation_pair_count": sum(
                result["metrics"]["prose_variation_pair_count"] for result in scenario_results
            ),
        },
        "scenario_results": scenario_results,
        "failure_codes": (
            ["CRITICAL_RUN_DIVERGENCE"] if critical_count else []
        ) + (["EXPECTED_DISPOSITION_MISMATCH"] if mismatch_count else []),
        "unknown_reasons": sorted(set(unknown_reasons)),
        "authority": {
            "measurement_scope": "STORED_SEALED_RUNS_ONLY",
            "runtime_invoked": False,
            "promotion_scope": "FUTURE_RUNS_ONLY",
            "release_authorizing": False,
        },
    }
    body["record_digest"] = canonical_digest(body)
    return body
