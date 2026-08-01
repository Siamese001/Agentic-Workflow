"""Exact factual, human-review, and adjudication binding helpers."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from apps_rg.evals.resume_graph.constants import _SHA256_RE
from apps_rg.evals.resume_graph.models import EvaluationDataError

BINDING_FIELDS = (
    "employer",
    "role",
    "date",
    "metric",
    "credential",
    "scope",
    "certainty",
)
_BINDING_STATUSES = frozenset({"EXACT", "MISMATCH", "NOT_APPLICABLE", "UNKNOWN"})


def binding_disposition(value: Any) -> tuple[str, str | None]:
    """Return the fail-closed disposition and reason for one factual binding."""

    if not isinstance(value, Mapping):
        return "UNKNOWN", "BINDING_MISSING"
    status = value.get("status")
    if status not in _BINDING_STATUSES:
        return "UNKNOWN", "BINDING_STATUS_INVALID"
    if status == "UNKNOWN":
        return "UNKNOWN", "BINDING_UNKNOWN"
    if status == "MISMATCH":
        return "FAIL", "BINDING_MISMATCH"
    if status == "NOT_APPLICABLE":
        return "NOT_APPLICABLE", None

    expected = value.get("expected")
    observed = value.get("observed")
    if expected is None or observed is None:
        return "UNKNOWN", "BINDING_VALUE_MISSING"
    if expected != observed:
        return "FAIL", "BINDING_VALUE_MISMATCH"
    if value.get("inflation") is True:
        return "FAIL", "BINDING_INFLATION"
    return "PASS", None


def exact_binding_accuracy(records: list[Mapping[str, Any]], field: str) -> float:
    """Measure exactness over all applicable bindings for ``field``."""

    if field not in BINDING_FIELDS:
        raise EvaluationDataError(f"unknown binding field: {field}")
    applicable = []
    for record in records:
        bindings = record.get("bindings")
        value = bindings.get(field) if isinstance(bindings, Mapping) else None
        disposition, _ = binding_disposition(value)
        if disposition != "NOT_APPLICABLE":
            applicable.append(disposition)
    if not applicable:
        raise EvaluationDataError(f"no applicable {field} bindings")
    return sum(disposition == "PASS" for disposition in applicable) / len(applicable)


def _receipt_ref(value: Any) -> str:
    if isinstance(value, Mapping):
        receipt_id = str(value.get("adjudication_id") or value.get("receipt_id") or "")
        digest = str(value.get("record_digest") or value.get("digest") or "")
        return f"{receipt_id}::{digest}" if receipt_id and digest else ""
    return str(value or "")


def _valid_review_ref(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    review_id = value.get("review_id")
    reviewer_hash = value.get("reviewer_id_hash")
    reviewer_identity_ref = value.get("reviewer_identity_ref")
    digest = value.get("review_digest")
    return (
        isinstance(review_id, str)
        and bool(review_id)
        and isinstance(reviewer_hash, str)
        and bool(_SHA256_RE.fullmatch(reviewer_hash))
        and isinstance(reviewer_identity_ref, str)
        and reviewer_identity_ref.startswith("human-reviewer://")
        and reviewer_hash == hashlib.sha256(reviewer_identity_ref.encode("utf-8")).hexdigest()
        and isinstance(digest, str)
        and bool(_SHA256_RE.fullmatch(digest))
    )


def _valid_review_ref_pair(values: Any) -> bool:
    if not isinstance(values, list) or len(values) != 2:
        return False
    if any(not _valid_review_ref(value) for value in values):
        return False
    for field in (
        "review_id",
        "reviewer_id_hash",
        "reviewer_identity_ref",
        "review_digest",
    ):
        if len({str(value[field]) for value in values}) != 2:
            return False
    return True


def _valid_adjudication_ref(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    receipt_id = value.get("adjudication_id")
    digest = value.get("record_digest")
    return (
        isinstance(receipt_id, str)
        and bool(receipt_id)
        and isinstance(digest, str)
        and bool(_SHA256_RE.fullmatch(digest))
    )
