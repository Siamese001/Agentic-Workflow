"""Consolidated wave summary at top — shared validator (plan governance).

Plans MUST expose a single consolidated wave summary table near the top
(under ``## Status Tables`` → ``### Wave Progress``) before per-wave detail
sections (``## Wave N —``).

Used by:
- ``check_plan_format_compliance.py`` (per-path strict/advisory)
- ``check_plan_wave_summary_top.py`` (repo scan)
- ``.cursor/hooks/after_file_edit.py`` (post-edit warn/block)
- ``.claude/governance/scripts/post_cursor_agent_plan_wave_summary_audit.py``
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
_WAVE_DETAIL_RE = re.compile(r"^##\s+Wave\s+\d+\b", re.IGNORECASE | re.MULTILINE)
_TABLE_ROW_RE = re.compile(r"^\|.+\|$")
_TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|$")


def is_plan_wave_summary_exempt(content: str, filepath: str = "") -> bool:
    """True for dod_exempt frontmatter or archive paths."""
    norm = filepath.replace("\\", "/")
    if "/plans/_archive/" in norm or norm.startswith(".claude/plans/_archive/"):
        return True
    fm = _FRONTMATTER_RE.match(content)
    if fm and _DOD_EXEMPT_RE.search(fm.group(1)):
        return True
    return False


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
) -> list[WaveSummaryViolation]:
    """Validate plan obeys consolidated wave summary at top."""
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
                WaveSummarySeverity.WARN,
                "WS-TOP-7",
                header_line,
                "Wave summary table should use canonical columns: "
                "| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |",
            )
        )

    return violations
