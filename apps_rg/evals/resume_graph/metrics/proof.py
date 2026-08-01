"""Proof identity and deduplication helpers."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def _proof_split(row: Mapping[str, Any]) -> Any:
    return row.get("proof_split", row.get("split"))


def _retrieval_split(row: Mapping[str, Any]) -> Any:
    return row.get("retrieval_split", row.get("split"))


def _proof_identity(row: Mapping[str, Any]) -> str:
    value = row.get("proof_identity_digest")
    return str(value) if value else f"internal-sample::{row.get('sample_id', '')}"


def _proof_split_group(row: Mapping[str, Any]) -> str:
    value = row.get("proof_split_group_digest")
    return str(value) if value else _proof_identity(row)


def _proof_context_identity(row: Mapping[str, Any]) -> str:
    """Group alternative renderings without collapsing distinct target contexts."""

    target_jd = str(row.get("target_jd_digest") or "")
    target_brief = str(row.get("target_brief_digest") or "")
    case_id = str(row.get("case_id") or "")
    if not (target_jd or target_brief or case_id):
        case_id = str(row.get("sample_id") or "")
    return "::".join((_proof_identity(row), target_jd, target_brief, case_id))


def _unique_proof_rows(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    unique: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        identity = _proof_identity(row)
        existing = unique.get(identity)
        if existing is None or (
            row.get("representation_mode") == "CANONICAL_VISIBLE"
            and existing.get("representation_mode") != "CANONICAL_VISIBLE"
        ):
            unique[identity] = row
    return [unique[identity] for identity in sorted(unique)]


def _unique_proof_context_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    unique: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        identity = _proof_context_identity(row)
        existing = unique.get(identity)
        if existing is None or (
            row.get("representation_mode") == "CANONICAL_VISIBLE"
            and existing.get("representation_mode") != "CANONICAL_VISIBLE"
        ):
            unique[identity] = row
    return [unique[identity] for identity in sorted(unique)]
