"""Replay consistency helpers for L4 audit, commit, and refresh evidence."""

from __future__ import annotations

from typing import Any


def validate_replay_consistency(
    *,
    commit_receipt: Any,
    audit_append_receipt: Any,
    refresh_receipts: list[Any] | tuple[Any, ...] = (),
    derived_index_manifest: dict[str, Any] | None = None,
) -> tuple[bool, tuple[str, ...]]:
    """Return fail-closed consistency status and reason codes."""
    reasons: list[str] = []
    commit_id = str(getattr(commit_receipt, "commit_receipt_id", "") or "")
    if not commit_id:
        reasons.append("missing_commit_receipt_ref")
    if not str(getattr(commit_receipt, "audit_append_receipt_ref", "") or ""):
        reasons.append("missing_audit_append_receipt_ref")
    if not str(getattr(audit_append_receipt, "chain_hash", "") or ""):
        reasons.append("missing_audit_chain_hash")
    if str(getattr(commit_receipt, "chain_hash", "") or "") != str(
        getattr(audit_append_receipt, "chain_hash", "") or ""
    ):
        reasons.append("commit_audit_chain_hash_mismatch")
    for receipt in refresh_receipts:
        if str(getattr(receipt, "source_commit_receipt_ref", "") or "") != commit_id:
            reasons.append("refresh_commit_receipt_ref_mismatch")
    if derived_index_manifest is not None:
        refs = tuple(derived_index_manifest.get("source_commit_receipt_refs") or ())
        if commit_id and commit_id not in refs:
            reasons.append("derived_index_commit_receipt_ref_mismatch")
    return (not reasons, tuple(reasons))


__all__ = ["validate_replay_consistency"]
