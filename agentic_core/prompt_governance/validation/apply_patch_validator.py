"""Apply-patch output validator — EQ-12 (ADR-PROMPT-ASSEMBLY-002 §14).

Validates the structural shape of an OpenAI-style ``apply_patch`` output
before it is executed. The validator is intentionally strict on
structure and permissive on content: we reject malformed envelopes and
out-of-scope paths, but we do not second-guess the hunk payload itself
(that is the job of the downstream patcher).

Accepted envelope
-----------------
::

    *** Begin Patch
    *** Update File: path/to/file.py
    @@ <optional anchor>
    <hunk lines>
    *** End Patch

``Update File`` may be replaced by ``Add File`` or ``Delete File``.
Multiple file sections per patch are allowed. Anything outside the
``Begin Patch`` / ``End Patch`` fences is ignored (treats prose
preamble gracefully).

Usage
-----
::

    from agentic_core.prompt_governance.validation.apply_patch_validator import (
        validate_apply_patch,
    )

    report = validate_apply_patch(
        raw_output,
        allowed_path_prefixes=("agentic_core/", "tests/"),
    )
    if not report.ok:
        raise ValueError(report.reasons)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


_BEGIN = "*** Begin Patch"
_END = "*** End Patch"

# File header forms accepted by apply_patch.
_FILE_ACTION_PATTERN = re.compile(
    r"^\*\*\* (Update File|Add File|Delete File): (.+)$"
)


@dataclass
class ApplyPatchReport:
    """Result of validating an apply_patch output."""

    ok: bool
    files: list[tuple[str, str]] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def validate_apply_patch(
    raw_output: str,
    *,
    allowed_path_prefixes: tuple[str, ...] = (),
) -> ApplyPatchReport:
    """Return a report on the structural validity of ``raw_output``.

    Args:
        raw_output: The full assistant response text that should contain
            an apply_patch envelope. Content outside the envelope is
            ignored.
        allowed_path_prefixes: Optional tuple of path prefixes. When
            non-empty, every file path in the patch MUST start with one
            of the prefixes; paths outside scope are reported as
            ``reasons``.

    Returns:
        An :class:`ApplyPatchReport` where ``ok`` is ``True`` iff the
        envelope parsed cleanly AND every file action respects the
        allowed prefixes.
    """
    reasons: list[str] = []
    files: list[tuple[str, str]] = []

    if not raw_output or not isinstance(raw_output, str):
        return ApplyPatchReport(ok=False, reasons=["empty or non-string input"])

    if _BEGIN not in raw_output:
        return ApplyPatchReport(
            ok=False, reasons=["missing '*** Begin Patch' sentinel"]
        )
    if _END not in raw_output:
        return ApplyPatchReport(
            ok=False, reasons=["missing '*** End Patch' sentinel"]
        )

    begin_idx = raw_output.index(_BEGIN)
    end_idx = raw_output.index(_END)
    if end_idx <= begin_idx:
        return ApplyPatchReport(
            ok=False, reasons=["'End Patch' appears before 'Begin Patch'"]
        )

    body = raw_output[begin_idx + len(_BEGIN) : end_idx]
    has_any_file = False
    for line in body.splitlines():
        match = _FILE_ACTION_PATTERN.match(line.strip())
        if not match:
            continue
        action, path = match.group(1), match.group(2).strip()
        has_any_file = True
        if not path:
            reasons.append(f"{action}: empty path")
            continue
        if allowed_path_prefixes and not any(
            path.startswith(prefix) for prefix in allowed_path_prefixes
        ):
            reasons.append(
                f"{action}: path {path!r} outside allowed prefixes {allowed_path_prefixes}"
            )
        files.append((action, path))

    if not has_any_file:
        reasons.append(
            "no file action (Update File / Add File / Delete File) found inside envelope"
        )

    return ApplyPatchReport(ok=not reasons, files=files, reasons=reasons)


__all__ = ["ApplyPatchReport", "validate_apply_patch"]
