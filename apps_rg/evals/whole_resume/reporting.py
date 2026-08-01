"""Deterministic whole-resume receipt sealing and output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from apps_rg.evals.resume_graph.reporting import canonical_digest


def receipt_digest(receipt: Mapping[str, Any]) -> str:
    """Hash a receipt without its self-referential digest field."""

    return canonical_digest({key: value for key, value in receipt.items() if key != "record_digest"})


def seal_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Return a receipt copy with a deterministic record digest."""

    sealed = dict(receipt)
    sealed["record_digest"] = receipt_digest(sealed)
    return sealed


def receipt_digest_is_valid(receipt: Mapping[str, Any]) -> bool:
    digest = receipt.get("record_digest")
    return isinstance(digest, str) and digest == receipt_digest(receipt)


def write_receipt(receipt: Mapping[str, Any], path: Path, *, pretty: bool = True) -> None:
    payload = json.dumps(
        receipt,
        allow_nan=False,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload + "\n", encoding="utf-8")


__all__ = [
    "receipt_digest",
    "receipt_digest_is_valid",
    "seal_receipt",
    "write_receipt",
]
