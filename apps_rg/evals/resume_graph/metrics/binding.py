"""Exact human-review and adjudication binding helpers."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from apps_rg.evals.resume_graph.constants import _SHA256_RE


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
