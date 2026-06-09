"""Consolidated wave summary at top — shared validator (plan governance).

Plans MUST expose a single consolidated wave summary table near the top
(under ``## Status Tables`` → ``### Wave Progress``) before per-wave detail
sections (``## Wave N —``).

Used by:
- ``check_plan_format_compliance.py`` (per-path strict/advisory)
- ``check_plan_wave_summary_top.py`` (repo scan)
- ``.cursor/hooks/after_file_edit.py`` (post-edit warn/block)
- ``.claude/governance/scripts/post_agent_plan_wave_summary_audit.py``
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class WaveSummarySeverity(Enum):
    FAIL = "FAIL"
    WARN = "WARN"


@dataclass(frozen=True)
class WaveSummaryViolation:
    severity: WaveSummarySeverity
    rule_id: str
    line_num: int
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity.value,
            "rule_id": self.rule_id,
            "line_num": self.line_num,
            "message": self.message,
        }


_FRONTMATTER_RE = re.compile(r"^---\n(.+?)\n---\n", re.DOTALL)
_DOD_EXEMPT_RE = re.compile(r"^\s*dod_exempt\s*:\s*true\s*$", re.IGNORECASE | re.MULTILINE)

_STATUS_TABLES_RE = re.compile(r"^##\s+Status Tables\s*$", re.IGNORECASE | re.MULTILINE)
_CONSOLIDATED_RE = re.compile(r"^##\s+Consolidated Wave Summary\s*$", re.IGNORECASE | re.MULTILINE)
_WAVE_PROGRESS_RE = re.compile(r"^###\s+Wave Progress\s*$", re.IGNORECASE | re.MULTILINE)
_PHASE_PROGRESS_RE = re.compile(r"^###\s+Phase Progress\s*$", re.IGNORECASE | re.MULTILINE)
_WAVE_DETAIL_RE = re.compile(r"^##\s+Wave\s+\d+\b", re.IGNORECASE | re.MULTILINE)
_WAVE_HEADING_NUM_RE = re.compile(r"^##\s+Wave\s+(\d+)\b", re.IGNORECASE | re.MULTILINE)
_TABLE_ROW_RE = re.compile(r"^\|.+\|$")
_TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|$")

# plan_format: v2 marker — the grandfather switch. Strict phase-at-top, wave-ordering,
# and canonical-column enforcement applies ONLY to v2 plans; legacy plans (no marker) keep
# the historical advisory behaviour (user directive 2026-06-09: enforce going forward only).
_PLAN_FORMAT_V2_FM_RE = re.compile(r"^\s*plan_format\s*:\s*v2\b", re.IGNORECASE | re.MULTILINE)
_PLAN_FORMAT_V2_BODY_RE = re.compile(r"^\s*PLAN_FORMAT:\s*v2\b", re.MULTILINE)

# Backward-dependency language inside a `## Wave N` section that points at another wave.
_WAVE_DEP_RE = re.compile(
    r"\b(?:depends?\s+on|dependent\s+on|after|requires?|blocked\s+by|must\s+follow|prerequisite[:\s]+)\s*"
    r"(?:wave\s*)?W(\d+)\b",
    re.IGNORECASE,
)
# Explicit "W<a> before/precedes W<b>" ordering statements anywhere in the plan.
_WAVE_BEFORE_RE = re.compile(
    r"\bW(\d+)\s+(?:before|must\s+precede|precedes?|runs?\s+before)\s+(?:wave\s*)?W(\d+)\b",
    re.IGNORECASE,
)


def is_plan_wave_summary_exempt(content: str, filepath: str = "") -> bool:
    """True for dod_exempt frontmatter or archive paths."""
    norm = filepath.replace("\\", "/")
    if "/plans/_archive/" in norm or norm.startswith(".claude/plans/_archive/"):
        return True
    fm = _FRONTMATTER_RE.match(content)
    if fm and _DOD_EXEMPT_RE.search(fm.group(1)):
        return True
    return False


def is_plan_format_v2(content: str) -> bool:
    """True when the plan opts into the v2 standard (``plan_format: v2``).

    The template injects this marker, so every plan created going forward is v2 and is held to the
    strict standard (Wave + Phase summary tables at top, canonical columns, ascending wave order with
    no backward dependency). Plans without the marker are legacy and stay grandfathered to advisory
    behaviour — no retroactive churn. Accepted in frontmatter (``plan_format: v2``) or as a body
    Plan State Marker (``PLAN_FORMAT: v2``).
    """
    fm = _FRONTMATTER_RE.match(content)
    if fm and _PLAN_FORMAT_V2_FM_RE.search(fm.group(1)):
        return True
    return bool(_PLAN_FORMAT_V2_BODY_RE.search(content))


def _line_number(content: str, index: int) -> int:
    if index < 0:
        return 0
    return content[:index].count("\n") + 1


def _find_first_match(pattern: re.Pattern[str], content: str) -> int | None:
    m = pattern.search(content)
    if not m:
        return None
    return _line_number(content, m.start())


def _parse_table_header(line: str) -> list[str]:
    cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
    return [c for c in cells if c]


def _table_has_required_columns(header_cells: list[str]) -> tuple[bool, bool]:
    """Return (has_min_columns, has_full_canonical_columns)."""
    joined = " ".join(header_cells)
    has_min = "wave" in joined and "status" in joined and "focus" in joined
    has_full = (
        has_min
        and any("phase" in c for c in header_cells)
        and any("success" in c for c in header_cells)
        and any("token" in c for c in header_cells)
        and any("assumption" in c for c in header_cells)
    )
    return has_min, has_full


def _find_consolidated_wave_table(
    lines: list[str],
    *,
    search_start: int,
    search_end: int,
) -> tuple[int | None, list[str], bool]:
    """Return (header_line_1based, header_cells, has_full_canonical_columns)."""
    i = search_start
    while i < search_end:
        line = lines[i]
        if _TABLE_ROW_RE.match(line) and i + 1 < search_end and _TABLE_SEP_RE.match(lines[i + 1]):
            header_cells = _parse_table_header(line)
            first = header_cells[0] if header_cells else ""
            if header_cells and (first == "wave" or first.startswith("wave")):
                has_min, has_full = _table_has_required_columns(header_cells)
                if has_min:
                    # require at least one W# data row before next heading or end
                    j = i + 2
                    has_wave_row = False
                    while j < search_end:
                        row = lines[j]
                        if row.startswith("#"):
                            break
                        if _TABLE_ROW_RE.match(row) and re.search(r"\bW\d+\b", row, re.IGNORECASE):
                            has_wave_row = True
                            break
                        j += 1
                    if has_wave_row:
                        return i + 1, header_cells, has_full
        i += 1
    return None, [], False


def validate_consolidated_wave_summary_at_top(
    content: str,
    filepath: str = "",
    *,
    strict: bool = False,
) -> list[WaveSummaryViolation]:
    """Validate plan obeys consolidated wave summary at top.

    ``strict`` (set for v2 plans) escalates the canonical-column check (WS-TOP-7) from WARN to FAIL.
    """
    if is_plan_wave_summary_exempt(content, filepath):
        return []

    violations: list[WaveSummaryViolation] = []
    lines = content.split("\n")

    status_tables_line = _find_first_match(_STATUS_TABLES_RE, content)
    consolidated_line = _find_first_match(_CONSOLIDATED_RE, content)
    wave_progress_line = _find_first_match(_WAVE_PROGRESS_RE, content)
    first_wave_detail = _find_first_match(_WAVE_DETAIL_RE, content)

    section_line = status_tables_line or consolidated_line
    if section_line is None:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-TOP-1",
                first_wave_detail or 0,
                "Missing `## Status Tables` (or `## Consolidated Wave Summary`) before wave detail sections.",
            )
        )
        return violations

    if first_wave_detail is not None and section_line > first_wave_detail:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-TOP-2",
                section_line,
                "`## Status Tables` must appear before the first `## Wave N` detail section.",
            )
        )

    if status_tables_line is not None and wave_progress_line is None:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-TOP-3",
                status_tables_line,
                "Under `## Status Tables`, add `### Wave Progress` with the consolidated wave summary table.",
            )
        )

    if wave_progress_line is not None and first_wave_detail is not None and wave_progress_line > first_wave_detail:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-TOP-4",
                wave_progress_line,
                "`### Wave Progress` must appear before the first `## Wave N` detail section.",
            )
        )

    search_start = (wave_progress_line or section_line) - 1
    search_end = (first_wave_detail - 1) if first_wave_detail else len(lines)
    if search_start < 0:
        search_start = 0
    if search_end <= search_start:
        search_end = len(lines)

    header_line, _header_cells, has_full = _find_consolidated_wave_table(
        lines,
        search_start=search_start,
        search_end=search_end,
    )
    if header_line is None:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-TOP-5",
                section_line,
                "Missing consolidated wave summary markdown table (columns must include Wave, Focus, Status; "
                "at least one `W#` row) under `### Wave Progress` before wave detail sections.",
            )
        )
        return violations

    if first_wave_detail is not None and header_line > first_wave_detail:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-TOP-6",
                header_line,
                "Consolidated wave summary table must appear before the first `## Wave N` detail section.",
            )
        )

    if not has_full:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL if strict else WaveSummarySeverity.WARN,
                "WS-TOP-7",
                header_line,
                "Wave summary table must use canonical columns: "
                "| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |",
            )
        )

    return violations


def _phase_table_present(lines: list[str], search_start: int, search_end: int) -> bool:
    """True when a phase summary table (header has Phase + Status, ≥1 data row) exists in range."""
    i = search_start
    while i < search_end:
        line = lines[i]
        if _TABLE_ROW_RE.match(line) and i + 1 < search_end and _TABLE_SEP_RE.match(lines[i + 1]):
            header = _parse_table_header(line)
            joined = " ".join(header)
            if "phase" in joined and "status" in joined:
                j = i + 2
                while j < search_end:
                    row = lines[j]
                    if row.startswith("#"):
                        break
                    if _TABLE_ROW_RE.match(row) and not _TABLE_SEP_RE.match(row):
                        return True
                    j += 1
        i += 1
    return False


def validate_phase_summary_at_top(content: str, filepath: str = "") -> list[WaveSummaryViolation]:
    """Require a consolidated ``### Phase Progress`` table at the top (v2 plans).

    Companion to the wave summary: phases must also be summarised in a table under ``## Status Tables``
    before the first ``## Wave N`` detail section, not buried mid-document.
    """
    if is_plan_wave_summary_exempt(content, filepath):
        return []

    violations: list[WaveSummaryViolation] = []
    lines = content.split("\n")

    status_tables_line = _find_first_match(_STATUS_TABLES_RE, content) or _find_first_match(
        _CONSOLIDATED_RE, content
    )
    phase_progress_line = _find_first_match(_PHASE_PROGRESS_RE, content)
    first_wave_detail = _find_first_match(_WAVE_DETAIL_RE, content)

    if status_tables_line is None:
        # The wave validator already emits WS-TOP-1 for the missing section; don't double-report.
        return violations

    if phase_progress_line is None:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-PHASE-1",
                status_tables_line,
                "Under `## Status Tables`, add `### Phase Progress` with the consolidated phase summary "
                "table (Phase ID, Title, Status) before the first `## Wave N` detail section.",
            )
        )
        return violations

    if first_wave_detail is not None and phase_progress_line > first_wave_detail:
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-PHASE-2",
                phase_progress_line,
                "`### Phase Progress` must appear before the first `## Wave N` detail section.",
            )
        )

    search_start = phase_progress_line - 1
    search_end = (first_wave_detail - 1) if first_wave_detail else len(lines)
    if search_start < 0:
        search_start = 0
    if search_end <= search_start:
        search_end = len(lines)

    if not _phase_table_present(lines, search_start, search_end):
        violations.append(
            WaveSummaryViolation(
                WaveSummarySeverity.FAIL,
                "WS-PHASE-3",
                phase_progress_line,
                "Missing phase summary markdown table (columns must include Phase and Status; at least "
                "one row) under `### Phase Progress`.",
            )
        )

    return violations


def validate_wave_execution_order(content: str, filepath: str = "") -> list[WaveSummaryViolation]:
    """Require waves to be numbered in execution order with no backward dependency (v2 plans).

    - WS-ORDER-1: ``## Wave N`` detail headings must be strictly ascending in document order.
    - WS-ORDER-2: a wave section may not declare a dependency (depends on / after / requires /
      blocked by / prerequisite) on a HIGHER-numbered wave — prerequisites must run first.
    - WS-ORDER-3: an explicit "W<a> before W<b>" statement must have a < b.
    """
    if is_plan_wave_summary_exempt(content, filepath):
        return []

    violations: list[WaveSummaryViolation] = []
    headings = [(m.start(), int(m.group(1))) for m in _WAVE_HEADING_NUM_RE.finditer(content)]

    prev_num: int | None = None
    for start, num in headings:
        if prev_num is not None and num <= prev_num:
            violations.append(
                WaveSummaryViolation(
                    WaveSummarySeverity.FAIL,
                    "WS-ORDER-1",
                    _line_number(content, start),
                    f"Wave detail sections must be in ascending execution order; `## Wave {num}` "
                    f"follows `## Wave {prev_num}`. Number waves in the order they are intended to run.",
                )
            )
        prev_num = num

    section_bounds = [s for s, _ in headings] + [len(content)]
    for idx, (start, num) in enumerate(headings):
        section = content[start : section_bounds[idx + 1]]
        for dm in _WAVE_DEP_RE.finditer(section):
            ref = int(dm.group(1))
            if ref > num:
                violations.append(
                    WaveSummaryViolation(
                        WaveSummarySeverity.FAIL,
                        "WS-ORDER-2",
                        _line_number(content, start + dm.start()),
                        f"`## Wave {num}` declares a dependency on higher-numbered W{ref}; a wave may "
                        f"only depend on earlier (lower-numbered) waves. Reorder so prerequisites run first.",
                    )
                )

    for bm in _WAVE_BEFORE_RE.finditer(content):
        a, b = int(bm.group(1)), int(bm.group(2))
        if a > b:
            violations.append(
                WaveSummaryViolation(
                    WaveSummarySeverity.FAIL,
                    "WS-ORDER-3",
                    _line_number(content, bm.start()),
                    f"Ordering statement says W{a} runs before W{b}, but W{a} is numbered later. "
                    f"The earlier-running wave must get the lower number.",
                )
            )

    return violations


def validate_plan_format(content: str, filepath: str = "") -> list[WaveSummaryViolation]:
    """Aggregate plan-format validator — wave summary + (v2) phase summary + (v2) wave ordering.

    Legacy plans (no ``plan_format: v2`` marker) get ONLY the historical wave-summary checks at their
    historical severities (grandfathered). v2 plans additionally get strict canonical columns, the
    phase-summary-at-top requirement, and wave-execution-order enforcement. This is how "enforce going
    forward only" is implemented: every plan created from the template is v2 and fully enforced; no
    pre-existing plan is retroactively blocked.
    """
    if is_plan_wave_summary_exempt(content, filepath):
        return []
    v2 = is_plan_format_v2(content)
    out = list(validate_consolidated_wave_summary_at_top(content, filepath, strict=v2))
    if v2:
        out += validate_phase_summary_at_top(content, filepath)
        out += validate_wave_execution_order(content, filepath)
    return out
