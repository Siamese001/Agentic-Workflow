"""Build bounded Notion Plans summaries from on-disk plan SSOT files.

Plans DB rows are dashboard rows, so their ``Summary`` property must carry
enough wave/phase status and completion notes to be useful without opening the
markdown file. This module is pure logic: no Notion API calls and no file I/O.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

MAX_SUMMARY_CHARS = 2000
MAX_AI_SUMMARY_CHARS = 180

_STATE_RE = re.compile(r"^(PLAN_STATUS|CURRENT_WAVE|LAST_COMPLETED_WAVE|LAST_UPDATED):\s*(.+?)\s*$")
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
_CLOSEOUT_RE = re.compile(
    r"^\s*(?:CLOSEOUT_)?(?P<kind>WAVE_COMPLETE|PHASE_COMPLETE|PLAN_COMPLETE):\s*(?P<body>.+?)\s*$"
)
_KV_RE = re.compile(
    r"\b(?P<key>plan|wave|phase|note)="
    r"(?:\"(?P<qval>[^\"]*)\"|'(?P<sqval>[^']*)'|(?P<bval>\S+))"
)

_STATUS_GLYPHS = {
    "\u2705": "",
    "\u26a0\ufe0f": "",
    "\u26a0": "",
    "\U0001f532": "",
}


@dataclass(frozen=True)
class WaveRow:
    wave: str
    focus: str
    status: str
    success_criteria: str


@dataclass(frozen=True)
class PhaseRow:
    phase: str
    title: str
    status: str


@dataclass(frozen=True)
class CloseoutNote:
    kind: str
    label: str
    note: str


def _clean(text: str, *, max_chars: int | None = None) -> str:
    out = text.replace("`", "").replace("**", "")
    out = out.replace("\u2014", "-").replace("\u2013", "-")
    for glyph, repl in _STATUS_GLYPHS.items():
        out = out.replace(glyph, repl)
    out = re.sub(r"\s+", " ", out).strip(" -|\t\r\n")
    if max_chars is not None and len(out) > max_chars:
        out = out[: max_chars - 3].rstrip() + "..."
    return out


def _extract_state(content: str) -> dict[str, str]:
    state: dict[str, str] = {}
    for line in content.splitlines():
        m = _STATE_RE.match(line.strip())
        if m:
            state[m.group(1)] = _clean(m.group(2), max_chars=80)
    return state


def _extract_h1(content: str) -> str:
    for line in content.splitlines():
        m = _HEADING_RE.match(line.strip())
        if m:
            return _clean(m.group(1), max_chars=140)
    return "Plan"


def _split_table_row(line: str) -> list[str]:
    raw = line.strip()
    if not raw.startswith("|") or not raw.endswith("|"):
        return []
    return [_clean(part) for part in raw.strip("|").split("|")]


def _find_table_rows(content: str, heading: str) -> list[dict[str, str]]:
    lines = content.splitlines()
    start = None
    heading_re = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.IGNORECASE)
    for idx, line in enumerate(lines):
        if heading_re.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return []

    table_lines: list[str] = []
    for line in lines[start:]:
        if not line.strip():
            if table_lines:
                break
            continue
        if not line.lstrip().startswith("|"):
            if table_lines:
                break
            continue
        table_lines.append(line)

    if len(table_lines) < 2:
        return []
    headers = _split_table_row(table_lines[0])
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cells = _split_table_row(line)
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def extract_wave_rows(content: str) -> list[WaveRow]:
    rows: list[WaveRow] = []
    for row in _find_table_rows(content, "Wave Progress"):
        wave = row.get("Wave", "")
        if not wave:
            continue
        rows.append(
            WaveRow(
                wave=wave,
                focus=row.get("Focus", ""),
                status=row.get("Status", ""),
                success_criteria=row.get("Success Criteria", ""),
            )
        )
    return rows


def extract_phase_rows(content: str) -> list[PhaseRow]:
    rows: list[PhaseRow] = []
    for row in _find_table_rows(content, "Phase Progress"):
        phase = row.get("Phase", "")
        if not phase:
            continue
        rows.append(
            PhaseRow(
                phase=phase,
                title=row.get("Title", ""),
                status=row.get("Status", ""),
            )
        )
    return rows


def _parse_kv(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in _KV_RE.finditer(body):
        val = m.group("qval")
        if val is None:
            val = m.group("sqval")
        if val is None:
            val = m.group("bval") or ""
        out[m.group("key")] = _clean(val)
    return out


def extract_closeout_notes(content: str) -> list[CloseoutNote]:
    notes: list[CloseoutNote] = []
    for line in content.splitlines():
        m = _CLOSEOUT_RE.match(line)
        if not m:
            continue
        fields = _parse_kv(m.group("body"))
        note = fields.get("note", "")
        if not note:
            continue
        kind = m.group("kind")
        if kind == "WAVE_COMPLETE":
            label = f"W{fields.get('wave', '?')}"
        elif kind == "PHASE_COMPLETE":
            label = fields.get("phase", "Phase ?")
        else:
            label = "PLAN"
        notes.append(CloseoutNote(kind=kind, label=label, note=note))
    return notes


def build_plan_notion_ai_summary(content: str, *, max_chars: int = MAX_AI_SUMMARY_CHARS) -> str:
    state = _extract_state(content)
    waves = extract_wave_rows(content)
    done = [w.wave for w in waves if "DONE" in w.status.upper()]
    status = state.get("PLAN_STATUS") or "UNKNOWN"
    if done:
        text = f"{status}: {', '.join(done)} complete for {_extract_h1(content)}."
    else:
        current = state.get("CURRENT_WAVE") or "no current wave"
        text = f"{status}: {current} for {_extract_h1(content)}."
    return _clean(text, max_chars=max_chars)


def build_plan_notion_summary(content: str, *, max_chars: int = MAX_SUMMARY_CHARS) -> str:
    state = _extract_state(content)
    waves = extract_wave_rows(content)
    phases = extract_phase_rows(content)
    notes = extract_closeout_notes(content)

    status_bits = [
        f"PLAN_STATUS={state.get('PLAN_STATUS', 'UNKNOWN')}",
        f"CURRENT_WAVE={state.get('CURRENT_WAVE', 'UNKNOWN')}",
    ]
    if state.get("LAST_COMPLETED_WAVE"):
        status_bits.append(f"LAST_COMPLETED_WAVE={state['LAST_COMPLETED_WAVE']}")
    if state.get("LAST_UPDATED"):
        status_bits.append(f"LAST_UPDATED={state['LAST_UPDATED']}")
    parts = ["Overall: " + "; ".join(status_bits) + "."]

    if waves:
        wave_bits = []
        for row in waves:
            focus = row.focus.split(" -- ", 1)[0].split(" - ", 1)[0]
            if not focus:
                focus = row.success_criteria
            wave_bits.append(
                f"{row.wave} {row.status or 'UNKNOWN'}: {_clean(focus, max_chars=120)}"
            )
        parts.append("Waves: " + "; ".join(wave_bits) + ".")

    if phases:
        phase_bits = [
            f"{row.phase} {row.status or 'UNKNOWN'}"
            for row in phases[:12]
        ]
        extra = len(phases) - len(phase_bits)
        if extra > 0:
            phase_bits.append(f"+{extra} more")
        parts.append("Phases: " + "; ".join(phase_bits) + ".")

    if notes:
        note_bits = [
            f"{note.label}: {_clean(note.note, max_chars=140)}"
            for note in notes[:10]
        ]
        extra = len(notes) - len(note_bits)
        if extra > 0:
            note_bits.append(f"+{extra} more notes")
        parts.append("Closeout notes: " + "; ".join(note_bits) + ".")

    summary = " ".join(part for part in parts if part.strip())
    return _clean(summary, max_chars=max_chars)


__all__ = [
    "MAX_SUMMARY_CHARS",
    "MAX_AI_SUMMARY_CHARS",
    "WaveRow",
    "PhaseRow",
    "CloseoutNote",
    "extract_wave_rows",
    "extract_phase_rows",
    "extract_closeout_notes",
    "build_plan_notion_ai_summary",
    "build_plan_notion_summary",
]
