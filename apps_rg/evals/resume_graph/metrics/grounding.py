"""Fail-closed material-claim grounding and exact-binding evaluation."""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from apps_rg.evals.resume_graph.constants import _SHA256_RE
from apps_rg.evals.resume_graph.metrics.binding import BINDING_FIELDS, binding_disposition
from apps_rg.evals.resume_graph.reporting import canonical_digest

_REQUIRED_RECORD_FIELDS = frozenset(
    {
        "schema_version",
        "claim_id",
        "claim_text",
        "materiality",
        "source_id",
        "exact_evidence_locator",
        "locator_failure_reason",
        "source_excerpt_digest",
        "graph_path",
        "path_binding",
        "bindings",
        "entailment_grade",
        "support_disposition",
        "components",
        "record_digest",
    }
)
_ALLOWED_RECORD_FIELDS = _REQUIRED_RECORD_FIELDS
_ENTAILMENT_GRADES = frozenset({"FULL", "PARTIAL", "NONE", "CONTRADICTED", "UNKNOWN"})
_SUPPORT_DISPOSITIONS = frozenset({"SUPPORTED", "PARTIAL", "UNSUPPORTED", "UNKNOWN"})


def claim_evidence_digest(record: Mapping[str, Any]) -> str:
    """Digest a claim-evidence record without its self-referential digest."""

    return canonical_digest({key: value for key, value in record.items() if key != "record_digest"})


def seal_claim_evidence_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy sealed with a deterministic record digest."""

    sealed = dict(record)
    sealed["record_digest"] = claim_evidence_digest(sealed)
    return sealed


def _unknown_reason(record: Mapping[str, Any], *, require_grounding_judgment: bool = True) -> str | None:
    if set(record) != _ALLOWED_RECORD_FIELDS or not _REQUIRED_RECORD_FIELDS.issubset(record):
        return "CLAIM_EVIDENCE_SCHEMA_INVALID"
    if record.get("schema_version") != "apps_rg.claim_evidence_record.v1":
        return "CLAIM_EVIDENCE_SCHEMA_INVALID"
    if not all(isinstance(record.get(field), str) and record[field] for field in ("claim_id", "claim_text")):
        return "CLAIM_IDENTITY_MISSING"
    if record.get("materiality") not in {"MATERIAL", "NON_MATERIAL"}:
        return "CLAIM_MATERIALITY_INVALID"
    digest = record.get("record_digest")
    if (
        not isinstance(digest, str)
        or not _SHA256_RE.fullmatch(digest)
        or digest != claim_evidence_digest(record)
    ):
        return "CLAIM_EVIDENCE_DIGEST_INVALID"
    if record.get("entailment_grade") not in _ENTAILMENT_GRADES:
        return "ENTAILMENT_GRADE_INVALID"
    if record.get("support_disposition") not in _SUPPORT_DISPOSITIONS:
        return "DECLARED_SUPPORT_DISPOSITION_INVALID"

    locator = record.get("exact_evidence_locator")
    locator_failure = record.get("locator_failure_reason")
    if not locator:
        if isinstance(locator_failure, str) and locator_failure:
            return "EXACT_EVIDENCE_LOCATOR_UNAVAILABLE"
        return "EXACT_EVIDENCE_LOCATOR_MISSING"
    if (
        not isinstance(locator, Mapping)
        or set(locator) != {"artifact_ref", "start", "end"}
        or not isinstance(locator.get("artifact_ref"), str)
        or not locator["artifact_ref"]
        or not isinstance(locator.get("start"), int)
        or isinstance(locator.get("start"), bool)
        or not isinstance(locator.get("end"), int)
        or isinstance(locator.get("end"), bool)
        or locator["start"] < 0
        or locator["end"] < locator["start"]
    ):
        return "EXACT_EVIDENCE_LOCATOR_INVALID"
    if not isinstance(record.get("source_id"), str) or not record["source_id"]:
        return "SOURCE_ID_MISSING"
    excerpt_digest = record.get("source_excerpt_digest")
    if not isinstance(excerpt_digest, str) or not _SHA256_RE.fullmatch(excerpt_digest):
        return "SOURCE_EXCERPT_DIGEST_MISSING"
    graph_path = record.get("graph_path")
    if (
        not isinstance(graph_path, list)
        or not graph_path
        or any(not isinstance(node, str) or not node for node in graph_path)
    ):
        return "GRAPH_PATH_MISSING"
    if record.get("path_binding") not in {"EXACT", "MISMATCH", "UNKNOWN"}:
        return "PATH_BINDING_INVALID"
    if record.get("path_binding") == "UNKNOWN":
        return "PATH_BINDING_UNKNOWN"
    if not isinstance(record.get("bindings"), Mapping) or set(record["bindings"]) != set(BINDING_FIELDS):
        return "BINDING_SET_INCOMPLETE"
    if require_grounding_judgment and record.get("entailment_grade") == "UNKNOWN":
        return "ENTAILMENT_UNKNOWN"
    components = record.get("components")
    if not isinstance(components, list):
        return "CLAIM_COMPONENTS_INVALID"
    if any(
        not isinstance(component, Mapping)
        or not isinstance(component.get("component_id"), str)
        or not component.get("component_id")
        or component.get("entailment_grade") not in _ENTAILMENT_GRADES
        for component in components
    ):
        return "CLAIM_COMPONENTS_INVALID"
    if require_grounding_judgment and any(
        component.get("entailment_grade") == "UNKNOWN" for component in components
    ):
        return "CLAIM_COMPONENT_ENTAILMENT_UNKNOWN"
    for binding in record["bindings"].values():
        if (
            not isinstance(binding, Mapping)
            or set(binding) != {"status", "expected", "observed", "inflation"}
            or not isinstance(binding.get("inflation"), bool)
        ):
            return "BINDING_SCHEMA_INVALID"
        disposition, reason = binding_disposition(binding)
        if disposition == "UNKNOWN":
            return reason
    return None


def evaluate_claim_evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate one record without trusting its declared support disposition."""

    unknown_reason = _unknown_reason(record)
    if unknown_reason is not None:
        return {
            "claim_id": str(record.get("claim_id", "")),
            "status": "UNKNOWN",
            "recomputed_support_disposition": "UNKNOWN",
            "source_id": record.get("source_id"),
            "exact_evidence_locator": record.get("exact_evidence_locator"),
            "locator_failure_reason": record.get("locator_failure_reason") or unknown_reason,
            "source_excerpt_digest": record.get("source_excerpt_digest"),
            "graph_path": record.get("graph_path"),
            "failure_codes": [],
            "unknown_reasons": [unknown_reason],
            "binding_results": {},
        }

    failure_codes: list[str] = []
    binding_results: dict[str, str] = {}
    if record["path_binding"] != "EXACT":
        failure_codes.append("GRAPH_PATH_MISMATCH")
    for field, binding in record["bindings"].items():
        disposition, reason = binding_disposition(binding)
        binding_results[field] = disposition
        if disposition == "FAIL":
            failure_codes.append(f"{field.upper()}_{reason}")
        if isinstance(binding, Mapping) and binding.get("inflation") is True:
            failure_codes.append(f"{field.upper()}_BINDING_INFLATION")

    entailment = record["entailment_grade"]
    component_grades = [component["entailment_grade"] for component in record["components"]]
    if entailment == "PARTIAL" or "PARTIAL" in component_grades:
        failure_codes.append("PARTIAL_SUPPORT")
    elif entailment != "FULL" or any(grade != "FULL" for grade in component_grades):
        failure_codes.append("UNSUPPORTED_CLAIM")

    if failure_codes:
        recomputed = "PARTIAL" if "PARTIAL_SUPPORT" in failure_codes else "UNSUPPORTED"
        status = "FAIL"
    else:
        recomputed = "SUPPORTED"
        status = "PASS"
    if record["support_disposition"] != recomputed:
        failure_codes.append("DECLARED_SUPPORT_DISPOSITION_MISMATCH")
        status = "FAIL"

    return {
        "claim_id": record["claim_id"],
        "status": status,
        "recomputed_support_disposition": recomputed,
        "source_id": record["source_id"],
        "exact_evidence_locator": record["exact_evidence_locator"],
        "locator_failure_reason": record["locator_failure_reason"],
        "source_excerpt_digest": record["source_excerpt_digest"],
        "graph_path": record["graph_path"],
        "failure_codes": sorted(set(failure_codes)),
        "unknown_reasons": [],
        "binding_results": binding_results,
    }


def _accuracy(results: Sequence[Mapping[str, Any]], field: str) -> float | None:
    applicable = [
        result["binding_results"].get(field)
        for result in results
        if field in result["binding_results"] and result["binding_results"].get(field) != "NOT_APPLICABLE"
    ]
    return None if not applicable else sum(value == "PASS" for value in applicable) / len(applicable)


def evaluate_grounding_gate(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Evaluate the complete frozen material-claim denominator."""

    if not records:
        return {
            "gate_id": "G3",
            "score_groups": ["factual_grounding"],
            "status": "UNKNOWN",
            "metrics": {},
            "failure_codes": [],
            "unknown_reasons": ["MATERIAL_CLAIM_INVENTORY_EMPTY"],
            "claim_results": [],
            "authority": "ADVISORY_FUTURE_RUN_ONLY",
        }
    results = [evaluate_claim_evidence(record) for record in records]
    material_pairs = [
        (record, result)
        for record, result in zip(records, results)
        if record.get("materiality") != "NON_MATERIAL"
    ]
    material_records = [record for record, _ in material_pairs]
    material_results = [result for _, result in material_pairs]
    unknown_reasons = sorted({reason for result in material_results for reason in result["unknown_reasons"]})
    failure_codes = sorted({code for result in material_results for code in result["failure_codes"]})
    if not material_results:
        unknown_reasons.append("MATERIAL_CLAIM_INVENTORY_EMPTY")

    support_count = sum(result["status"] == "PASS" for result in material_results)
    partial_count = sum(result["recomputed_support_disposition"] == "PARTIAL" for result in material_results)
    unsupported_count = sum(result["status"] != "PASS" for result in material_results)
    composite = [result for record, result in material_pairs if record.get("components")]
    failure_histogram = Counter(code for result in material_results for code in result["failure_codes"])
    metrics = {
        "material_claim_support_rate": support_count / len(material_results) if material_results else None,
        "unsupported_material_claim_count": unsupported_count,
        "partial_support_count": partial_count,
        "numeric_binding_accuracy": _accuracy(material_results, "metric"),
        "date_binding_accuracy": _accuracy(material_results, "date"),
        "employer_binding_accuracy": _accuracy(material_results, "employer"),
        "role_binding_accuracy": _accuracy(material_results, "role"),
        "credential_binding_accuracy": _accuracy(material_results, "credential"),
        "exact_path_accuracy": (
            sum(record.get("path_binding") == "EXACT" for record in material_records) / len(material_records)
            if material_records
            else None
        ),
        "scope_binding_accuracy": _accuracy(material_results, "scope"),
        "scope_inflation_rate": sum(
            "SCOPE_BINDING_INFLATION" in result["failure_codes"] for result in material_results
        )
        / len(material_results)
        if material_results
        else None,
        "certainty_inflation_rate": sum(
            "CERTAINTY_BINDING_INFLATION" in result["failure_codes"] for result in material_results
        )
        / len(material_results)
        if material_results
        else None,
        "composite_claim_full_support_rate": (
            sum(result["status"] == "PASS" for result in composite) / len(composite) if composite else None
        ),
    }
    if unknown_reasons:
        status = "UNKNOWN"
        failure_codes = []
    elif failure_codes or unsupported_count:
        status = "FAIL"
    else:
        status = "PASS"
    return {
        "gate_id": "G3",
        "score_groups": ["factual_grounding"],
        "status": status,
        "metrics": metrics,
        "failure_codes": failure_codes,
        "unknown_reasons": sorted(set(unknown_reasons)),
        "claim_results": results,
        "diagnostics": {"failure_code_counts": dict(sorted(failure_histogram.items()))},
        "authority": "ADVISORY_FUTURE_RUN_ONLY",
    }


def evaluate_binding_gate(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Evaluate G2 independently from the claim-entailment G3 disposition."""

    if not records:
        return {
            "gate_id": "G2",
            "score_groups": ["binding_accuracy"],
            "status": "UNKNOWN",
            "metrics": {},
            "failure_codes": [],
            "unknown_reasons": ["CLAIM_BINDING_INVENTORY_EMPTY"],
            "claim_results": [],
            "authority": "ADVISORY_FUTURE_RUN_ONLY",
        }
    results = []
    for record in records:
        unknown_reason = _unknown_reason(record, require_grounding_judgment=False)
        binding_results: dict[str, str] = {}
        failure_codes: list[str] = []
        if unknown_reason is None:
            if record["path_binding"] != "EXACT":
                failure_codes.append("GRAPH_PATH_MISMATCH")
            for field, binding in record["bindings"].items():
                disposition, reason = binding_disposition(binding)
                binding_results[field] = disposition
                if disposition == "FAIL":
                    failure_codes.append(f"{field.upper()}_{reason}")
                if binding.get("inflation") is True:
                    failure_codes.append(f"{field.upper()}_BINDING_INFLATION")
        results.append(
            {
                "claim_id": str(record.get("claim_id", "")),
                "status": ("UNKNOWN" if unknown_reason else "FAIL" if failure_codes else "PASS"),
                "source_id": record.get("source_id"),
                "exact_evidence_locator": record.get("exact_evidence_locator"),
                "locator_failure_reason": record.get("locator_failure_reason") or unknown_reason,
                "source_excerpt_digest": record.get("source_excerpt_digest"),
                "graph_path": record.get("graph_path"),
                "failure_codes": sorted(set(failure_codes)),
                "unknown_reasons": [unknown_reason] if unknown_reason else [],
                "binding_results": binding_results,
            }
        )
    material_pairs = [
        (record, result)
        for record, result in zip(records, results)
        if record.get("materiality") != "NON_MATERIAL"
    ]
    material_records = [record for record, _ in material_pairs]
    material_results = [result for _, result in material_pairs]
    unknown_reasons = sorted({reason for result in material_results for reason in result["unknown_reasons"]})
    if not material_results:
        unknown_reasons.append("CLAIM_BINDING_INVENTORY_EMPTY")
    binding_failure_codes = sorted(
        {
            code
            for result in material_results
            for code in result["failure_codes"]
            if code == "GRAPH_PATH_MISMATCH"
            or any(code.startswith(f"{field.upper()}_") for field in BINDING_FIELDS)
        }
    )
    metrics = {
        f"{'numeric' if field == 'metric' else field}_binding_accuracy": _accuracy(material_results, field)
        for field in BINDING_FIELDS
    }
    metrics["exact_path_accuracy"] = (
        sum(record.get("path_binding") == "EXACT" for record in material_records) / len(material_records)
        if material_records
        else None
    )
    if unknown_reasons:
        status = "UNKNOWN"
        binding_failure_codes = []
    elif binding_failure_codes:
        status = "FAIL"
    else:
        status = "PASS"
    return {
        "gate_id": "G2",
        "score_groups": ["binding_accuracy"],
        "status": status,
        "metrics": metrics,
        "failure_codes": binding_failure_codes,
        "unknown_reasons": unknown_reasons,
        "claim_results": results,
        "authority": "ADVISORY_FUTURE_RUN_ONLY",
    }
