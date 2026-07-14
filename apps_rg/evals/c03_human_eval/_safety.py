"""Reviewer-payload blinding checks shared by the builder and validator."""

from __future__ import annotations

import re
from typing import Any, Mapping

FORBIDDEN_REVIEWER_KEYS = {
    "adjudication_ref",
    "authority_pass",
    "claim_entailment_score",
    "decision",
    "judge_score",
    "labels",
    "metric_binding_score",
    "other_review",
    "path_confidence_raw",
    "proof_confidence_calibrated",
    "proof_split",
    "rank",
    "raw_score",
    "reviewer_refs",
    "retrieval_split",
    "reviews",
    "selected",
    "selection_margin",
    "split",
    "split_salt",
    "source_independence_score",
    "system_score",
    "system_verdict",
    "target_alignment_score",
}

FORBIDDEN_REVIEWER_KEY_TOKENS = {
    "confidence",
    "decision",
    "label",
    "labels",
    "prediction",
    "probability",
    "rank",
    "ranking",
    "review",
    "reviews",
    "score",
    "split",
    "selected",
    "selection",
    "verdict",
}


def _forbidden_key(raw_key: str) -> bool:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", raw_key).casefold()
    tokens = {
        token for token in re.split(r"[^a-z0-9]+", normalized) if token
    }
    compact = "".join(tokens)
    return bool(
        normalized in FORBIDDEN_REVIEWER_KEYS
        or tokens & FORBIDDEN_REVIEWER_KEY_TOKENS
        or "system" in tokens
        or normalized.endswith("_raw")
        or any(marker in compact for marker in ("confidence", "probability", "verdict"))
        or compact.endswith("score")
    )


def unsafe_reviewer_keys(value: Any, prefix: str = "") -> list[str]:
    """Return recursively located score/verdict/selection/other-label keys."""

    unsafe: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            path = f"{prefix}.{key}" if prefix else key
            if _forbidden_key(key):
                unsafe.append(path)
            unsafe.extend(unsafe_reviewer_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            unsafe.extend(unsafe_reviewer_keys(child, f"{prefix}[{index}]"))
    return unsafe


__all__ = [
    "FORBIDDEN_REVIEWER_KEYS",
    "FORBIDDEN_REVIEWER_KEY_TOKENS",
    "unsafe_reviewer_keys",
]
