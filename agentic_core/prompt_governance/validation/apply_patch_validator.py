"""Validation for canonical ``apply_patch`` envelopes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


_BEGIN = "*** Begin Patch"
_END = "*** End Patch"
_FILE_HEADER_RE = re.compile(r"^\*\*\* (Add File|Update File|Delete File):\s*(.+?)\s*$")


@dataclass
class ApplyPatchReport:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    files: list[tuple[str, str]] = field(default_factory=list)


def validate_apply_patch(
    patch_text: str,
    *,
    allowed_path_prefixes: Iterable[str] | None = None,
) -> ApplyPatchReport:
    """Return a lightweight structural report for an ``apply_patch`` payload."""
    reasons: list[str] = []
    files: list[tuple[str, str]] = []

    if not isinstance(patch_text, str) or not patch_text.strip():
        return ApplyPatchReport(ok=False, reasons=["patch input must be a non-empty string"])

    begin_idx = patch_text.find(_BEGIN)
    end_idx = patch_text.find(_END)
    if begin_idx < 0:
        reasons.append("missing Begin Patch fence")
    if end_idx < 0:
        reasons.append("missing End Patch fence")
    if begin_idx >= 0 and end_idx >= 0 and end_idx < begin_idx:
        reasons.append("End Patch appears before Begin Patch")
    if reasons:
        return ApplyPatchReport(ok=False, reasons=reasons)

    body = patch_text[begin_idx : end_idx + len(_END)]
    for line in body.splitlines():
        match = _FILE_HEADER_RE.match(line.strip())
        if match:
            action, raw_path = match.groups()
            files.append((action, _normalize_patch_path(raw_path)))

    if not files:
        reasons.append("patch envelope contains no file action")

    prefixes = tuple(_normalize_prefix(p) for p in (allowed_path_prefixes or ()) if str(p).strip())
    if prefixes:
        for _action, path in files:
            if not any(path.startswith(prefix) for prefix in prefixes):
                reasons.append(f"path outside allowed prefixes: {path}")

    return ApplyPatchReport(ok=not reasons, reasons=reasons, files=files)


def _normalize_patch_path(path: str) -> str:
    return str(path or "").strip().replace("\\", "/").lstrip("./")


def _normalize_prefix(prefix: str) -> str:
    cleaned = _normalize_patch_path(prefix)
    return cleaned if cleaned.endswith("/") else f"{cleaned}/"


__all__ = ["ApplyPatchReport", "validate_apply_patch"]
