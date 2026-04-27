"""Parse Prompt Assembly doctrine .md files for STATUS VALUES and MUST EMIT
sections.

Purpose
-------
The runtime evidence harness ``tools/prompt_assembly/runtime_evidence.py``
hard-codes the doctrine tables. That makes the harness self-consistent
but introduces a SSOT drift risk: editing the .md doesn't invalidate the
harness. This parser closes that loophole — it reads each
``PA.X_..._detailed.md`` file, extracts the canonical
``STATUS VALUES`` and ``MUST EMIT`` sections, and exposes them as
dictionaries the harness can compare against.

Doctrine format reminder (each child file uses the same template)::

    STATUS VALUES
    ----------------------------------------------------------------------
    - PA_FOO
    - PA_BAR
    - PA_BAZ

    MUST EMIT
    ----------------------------------------------------------------------
    - SomeReceipt
    - some_field_name
    - another_field

The parser is intentionally line-based and tolerant: extra prose between
sections is ignored, sections may appear in either order, and trailing
text on a heading line is stripped.
"""

from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Stage -> doctrine file mapping. Synchronized with runtime_evidence.py.
# ---------------------------------------------------------------------------

DOCTRINE_FILES: dict[str, str] = {
    "PA.0": "docs/reference/03B_PA_Prompt_Assembly/PA.0_Boundary_Check.md",
    "PA.1": "docs/reference/03B_PA_Prompt_Assembly/PA.1_Load_Resolve_Prompt_BOM.md",
    "PA.2": "docs/reference/03B_PA_Prompt_Assembly/PA.2_Slot_Composition.md",
    "PA.3": "docs/reference/03B_PA_Prompt_Assembly/PA.3_Airlock_Security_Pass.md",
    "PA.4": "docs/reference/03B_PA_Prompt_Assembly/PA.4_Validate_Slot_Contract.md",
    "PA.5": "docs/reference/03B_PA_Prompt_Assembly/PA.5_Token_Budget_Determinism.md",
    "PA.6": "docs/reference/03B_PA_Prompt_Assembly/PA.6_Provider_Aware_Rendering.md",
    "PA.7": "docs/reference/03B_PA_Prompt_Assembly/PA.7_Final_Emit_Compiled_Prompt_Artifact.md",
}

# Doctrine files outside the canonical PA.0..PA.7 partition. PARENT is
# the authoritative parent doctrine; PA.8 is the additive Authority
# Red-Team / Slot Formal Verification child. Both expose distinct
# section vocabularies and are parsed by dedicated check functions in
# the runtime-evidence harness.
EXTRA_DOCTRINE_FILES: dict[str, str] = {
    "PARENT": "docs/reference/03B_PA_Prompt_Assembly/Prompt_Assembly.md",
    "PA.8": "docs/reference/03B_PA_Prompt_Assembly/PA.8_Authority_RedTeam_Slot_Verification.md",
}

# Section headings recognised by the parser. We anchor on the heading
# string at the start of a line (after stripping leading whitespace).
# A heading line is ``HEADING NAME`` optionally followed by a single
# trailing colon. Trailing whitespace is tolerated.
_SECTION_RE = re.compile(
    r"^(STATUS VALUES|STATUS VOCABULARY|MUST EMIT|MUST NOT|FORBIDDEN OUTPUTS FROM THIS CHILD|FORBIDDEN OUTPUTS FROM THIS FILE|ACCEPTANCE TESTS|ACCEPTANCE EXPECTATIONS|SOURCE OWNERSHIP BOUNDARY|UNIQUE OWNERSHIP SURFACE|THIS FILE OWNS|THIS FILE DOES NOT OWN|TEST REQUIREMENTS|RULES|CONTRACTS TO IMPLEMENT):?\s*$",
    re.IGNORECASE,
)

# A bullet line whose payload is a comma-separated identifier list,
# e.g. ``- ALLOW, DENY, CLARIFY``. Used by :func:`_extract_csv_section`
# to capture every token from forbidden-output blocks where the
# doctrine packs many tokens onto one bullet line.
_CSV_BULLET_RE = re.compile(r"^\s*-\s+([A-Za-z][A-Za-z0-9_,\s]*[A-Za-z0-9_])\s*$")

# A bullet line we consider extractable: "- value" optionally followed by prose
# after a comma or dash. Captures the leading token.
# Accepts hyphen, asterisk, or bullet (\u2022) markers to tolerate the
# variety of markdown styles found across the doctrine corpus. Tab or
# space indentation is fine.
_BULLET_RE = re.compile(r"^[\s]*[-*\u2022]\s+([A-Za-z][A-Za-z0-9_]*)")


def _extract_section(lines: list[str], section_name: str) -> list[str]:
    """Extract the bullet items under a given section heading.

    Stops at the next recognised heading or at end-of-file.
    """
    items: list[str] = []
    in_section = False
    target = section_name.upper()
    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        match = _SECTION_RE.match(stripped)
        if match:
            heading = match.group(1).upper()
            in_section = heading == target
            continue
        if not in_section:
            continue
        # Skip the underline ---- separators that follow a heading.
        if stripped.startswith("-" * 10):
            continue
        # Empty line ends the bullet list.
        if not stripped:
            if items:
                break
            continue
        bm = _BULLET_RE.match(line)
        if bm:
            items.append(bm.group(1))
        else:
            # First non-bullet, non-empty line ends the section.
            if items:
                break
    return items


def _extract_csv_section(lines: list[str], section_name: str) -> list[str]:
    """Extract every comma-separated token under a section heading.

    Doctrine forbidden-output blocks pack many tokens onto a single
    bullet line, e.g. ``- ALLOW, DENY, CLARIFY``. The standard bullet
    extractor only captures the first identifier; this helper splits
    each bullet on commas and returns every token.
    """
    items: list[str] = []
    in_section = False
    target = section_name.upper()
    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        match = _SECTION_RE.match(stripped)
        if match:
            heading = match.group(1).upper()
            in_section = heading == target
            continue
        if not in_section:
            continue
        if stripped.startswith("-" * 10):
            continue
        if not stripped:
            if items:
                break
            continue
        bm = _CSV_BULLET_RE.match(line)
        if bm:
            payload = bm.group(1)
            for tok in payload.split(","):
                tok = tok.strip()
                if tok:
                    items.append(tok)
        else:
            if items:
                break
    return items


def parse_stage(stage: str, repo_root: Path) -> dict[str, list[str]]:
    """Parse a single stage's doctrine file.

    Returns a dict with keys ``status_values``, ``must_emit``,
    ``must_not``, ``forbidden_outputs``, ``acceptance_tests``,
    ``rules``, ``test_requirements``, ``contracts_to_implement``.

    The lookup falls back to :data:`EXTRA_DOCTRINE_FILES` so PARENT and
    PA.8 can be parsed by the same surface.
    """
    rel = DOCTRINE_FILES.get(stage) or EXTRA_DOCTRINE_FILES.get(stage)
    empty = {
        "status_values": [],
        "must_emit": [],
        "must_not": [],
        "forbidden_outputs": [],
        "acceptance_tests": [],
        "rules": [],
        "test_requirements": [],
        "contracts_to_implement": [],
    }
    if rel is None:
        return empty
    path = repo_root / rel
    if not path.exists():
        return empty
    # ``utf-8-sig`` strips a leading UTF-8 BOM if present so the parser
    # is resilient to Windows-style file encoding artefacts.
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    forbidden = _extract_csv_section(lines, "FORBIDDEN OUTPUTS FROM THIS CHILD") or _extract_csv_section(
        lines, "FORBIDDEN OUTPUTS FROM THIS FILE"
    )
    return {
        "status_values": (
            _extract_section(lines, "STATUS VALUES") or _extract_section(lines, "STATUS VOCABULARY")
        ),
        "must_emit": _extract_section(lines, "MUST EMIT"),
        "must_not": _extract_section(lines, "MUST NOT"),
        "forbidden_outputs": forbidden,
        "acceptance_tests": (
            _extract_section(lines, "ACCEPTANCE TESTS") or _extract_section(lines, "ACCEPTANCE EXPECTATIONS")
        ),
        "rules": _extract_section(lines, "RULES"),
        "test_requirements": _extract_section(lines, "TEST REQUIREMENTS"),
        "contracts_to_implement": _extract_section(lines, "CONTRACTS TO IMPLEMENT"),
    }


def parse_all(repo_root: Path) -> dict[str, dict[str, list[str]]]:
    """Parse every stage's doctrine file (PA.0..PA.7 only)."""
    return {stage: parse_stage(stage, repo_root) for stage in DOCTRINE_FILES}


def parse_extra(repo_root: Path) -> dict[str, dict[str, list[str]]]:
    """Parse PARENT and PA.8 (non-stage) doctrine files."""
    return {key: parse_stage(key, repo_root) for key in EXTRA_DOCTRINE_FILES}


def diff(parsed: dict[str, list[str]], harness: list[str]) -> dict[str, list[str]]:
    """Compute set differences between parsed doctrine and harness baseline.

    Returns ``{"only_in_doctrine": [...], "only_in_harness": [...]}``. The
    harness is allowed to include synthetic infrastructure keys
    (``stage``, ``doctrine_status``) that the doctrine itself does not
    enumerate, so callers may post-filter the diff.
    """
    parsed_set = set(parsed)
    harness_set = set(harness)
    return {
        "only_in_doctrine": sorted(parsed_set - harness_set),
        "only_in_harness": sorted(harness_set - parsed_set),
    }


__all__ = [
    "DOCTRINE_FILES",
    "EXTRA_DOCTRINE_FILES",
    "parse_all",
    "parse_extra",
    "parse_stage",
    "diff",
]
