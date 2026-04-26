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
    "PA.0": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.0_Boundary_Check_detailed.md",
    "PA.1": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.1_Load_Resolve_Prompt_BOM_detailed.md",
    "PA.2": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.2_Slot_Composition_detailed.md",
    "PA.3": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.3_Airlock_Security_Pass_detailed.md",
    "PA.4": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.4_Validate_Slot_Contract_detailed.md",
    "PA.5": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.5_Token_Budget_Determinism_detailed.md",
    "PA.6": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.6_Provider_Aware_Rendering_detailed.md",
    "PA.7": "docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.7_Final_Emit_Compiled_Prompt_Artifact_detailed.md",
}

# Section headings recognised by the parser. We anchor on the heading
# string at the start of a line (after stripping leading whitespace).
_SECTION_RE = re.compile(
    r"^(STATUS VALUES|MUST EMIT|MUST NOT|FORBIDDEN OUTPUTS FROM THIS CHILD|ACCEPTANCE TESTS|SOURCE OWNERSHIP BOUNDARY|UNIQUE OWNERSHIP SURFACE|THIS FILE OWNS|THIS FILE DOES NOT OWN)\s*$",
    re.IGNORECASE,
)

# A bullet line we consider extractable: "- value" optionally followed by prose
# after a comma or dash. Captures the leading token.
_BULLET_RE = re.compile(r"^\s*-\s+([A-Za-z][A-Za-z0-9_]*)")


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


def parse_stage(stage: str, repo_root: Path) -> dict[str, list[str]]:
    """Parse a single stage's doctrine file.

    Returns a dict with keys ``status_values``, ``must_emit``, ``must_not``.
    """
    rel = DOCTRINE_FILES[stage]
    path = repo_root / rel
    if not path.exists():
        return {"status_values": [], "must_emit": [], "must_not": []}
    lines = path.read_text(encoding="utf-8").splitlines()
    return {
        "status_values": _extract_section(lines, "STATUS VALUES"),
        "must_emit": _extract_section(lines, "MUST EMIT"),
        "must_not": _extract_section(lines, "MUST NOT"),
    }


def parse_all(repo_root: Path) -> dict[str, dict[str, list[str]]]:
    """Parse every stage's doctrine file."""
    return {stage: parse_stage(stage, repo_root) for stage in DOCTRINE_FILES}


def diff(
    parsed: dict[str, list[str]], harness: list[str]
) -> dict[str, list[str]]:
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
    "parse_all",
    "parse_stage",
    "diff",
]
