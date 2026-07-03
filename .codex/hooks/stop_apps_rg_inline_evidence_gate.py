"""Stop gate for apps_rg final-message inline evidence.

This hook closes the gap between producer-side apps_rg artifacts and chat delivery:
if a final assistant response appears to close an apps_rg run, it must paste the
mandatory runtime evidence inline. Links to artifacts alone are not enough.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from lib.codex_hook_common import allow, block, read_payload, resolve_response_text, write_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_NAME = "stop_apps_rg_inline_evidence_gate"

MANDATORY_JSON = "APPS_RG_MANDATORY_RUN_OUTPUT.json"
MANDATORY_FILE_NAMES = {
    MANDATORY_JSON,
    "APPS_RG_MANDATORY_RUN_OUTPUT.md",
    "BCG_EXECUTIVE_OUTPUT.md",
    "FINAL_RESUME_OUTPUT.txt",
    "FINAL_RESUME_OUTPUT.json",
    "RUN_SUMMARY_RENDERED.md",
}

REQUIRED_HEADINGS = (
    "## apps_rg Runtime Evidence",
    "## Locked BCG Output",
    "## Locked Section Lane Summary Table",
    "## Resume DOCX Full Version Inline",
)
MAX_TRANSCRIPT_CONTEXT_CHARS = 4_000_000

_RUN_ROOT_RE = re.compile(r"Run root:\s*`?@?(?P<path>[^`\n]+)`?", re.IGNORECASE)
_MANDATORY_PATH_RE = re.compile(
    r"(?P<path>(?:[A-Za-z]:)?[^`'\"\s|<>\]]*"
    r"(?:APPS_RG_MANDATORY_RUN_OUTPUT\.json|APPS_RG_MANDATORY_RUN_OUTPUT\.md|"
    r"BCG_EXECUTIVE_OUTPUT\.md|FINAL_RESUME_OUTPUT\.txt|FINAL_RESUME_OUTPUT\.json|"
    r"RUN_SUMMARY_RENDERED\.md))",
    re.IGNORECASE,
)
_ARTIFACT_PATH_RE = re.compile(
    r"(?P<path>(?:[A-Za-z]:)?[^`'\"\s|<>\]]*artifacts[\\/][A-Za-z0-9_.:\\/\-]+)",
    re.IGNORECASE,
)


def _bypass() -> bool:
    return os.environ.get("APPS_RG_INLINE_EVIDENCE_GATE_BYPASS", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _normal(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "").replace("`", "").strip()).lower()


def _contains(haystack: str, needle: Any) -> bool:
    normalized_needle = _normal(needle)
    if not normalized_needle:
        return True
    return normalized_needle in _normal(haystack)


def _appears_to_close_apps_rg_run(text: str) -> bool:
    lowered = text.lower()
    if "## apps_rg runtime evidence" in lowered:
        return True
    hard_tokens = (
        "apps_rg_mandatory_run_output",
        "bcg_executive_output.md",
        "final_resume_output",
        "run_summary_rendered.md",
    )
    if any(token in lowered for token in hard_tokens):
        return True
    return "apps_rg" in lowered and re.search(r"artifacts[\\/].*rg_", text, re.IGNORECASE) is not None


def _is_user_event(event: dict[str, Any]) -> bool:
    message = event.get("message")
    role = str(message.get("role") or "") if isinstance(message, dict) else ""
    return event.get("type") == "user" or role == "user"


def _recent_transcript_context(payload: dict[str, Any]) -> str:
    """Return bounded non-user transcript text from the current turn.

    Stop payloads can carry only ``transcript_path`` while the final response itself is
    terse. Resetting at the last user event keeps this gate tied to the current turn
    instead of letting an older apps_rg run poison unrelated later responses.
    """
    raw = str(payload.get("transcript_path") or payload.get("transcriptPath") or "").strip()
    if not raw:
        return ""
    path = Path(raw)
    if not path.is_file():
        return ""
    parts: list[str] = []
    total = 0
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    event = json.loads(stripped)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                if _is_user_event(event):
                    parts = []
                    total = 0
                    continue
                rendered = json.dumps(event, ensure_ascii=False, sort_keys=True)
                parts.append(rendered)
                total += len(rendered)
                while parts and total > MAX_TRANSCRIPT_CONTEXT_CHARS:
                    total -= len(parts.pop(0))
    except OSError:
        return ""
    return "\n".join(parts)


def _should_validate(payload: dict[str, Any], response_text: str) -> bool:
    if _appears_to_close_apps_rg_run(response_text):
        return True
    return _appears_to_close_apps_rg_run(_recent_transcript_context(payload))


def _clean_path(raw: str) -> Path | None:
    value = raw.strip().strip("`'\"<>[](),.;")
    if value.startswith("@"):
        value = value[1:]
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _candidate_run_dir(path: Path) -> Path | None:
    candidates: list[Path] = []
    if path.name in MANDATORY_FILE_NAMES or path.suffix:
        candidates.append(path.parent)
    candidates.append(path)
    candidates.extend(path.parents)
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / MANDATORY_JSON).is_file():
            return candidate
    return None


def _resolve_run_dir(text: str) -> Path | None:
    raw_candidates: list[str] = []
    raw_candidates.extend(match.group("path") for match in _RUN_ROOT_RE.finditer(text))
    raw_candidates.extend(match.group("path") for match in _MANDATORY_PATH_RE.finditer(text))
    raw_candidates.extend(match.group("path") for match in _ARTIFACT_PATH_RE.finditer(text))

    for raw in raw_candidates:
        path = _clean_path(raw)
        if path is None:
            continue
        run_dir = _candidate_run_dir(path)
        if run_dir is not None:
            return run_dir
    return None


def _load_inline_required_output(run_dir: Path) -> tuple[dict[str, Any] | None, str | None]:
    json_path = run_dir / MANDATORY_JSON
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except OSError as err:
        return None, f"missing_or_unreadable:{json_path}:{err}"
    except json.JSONDecodeError as err:
        return None, f"invalid_json:{json_path}:{err}"
    if not isinstance(payload, dict):
        return None, f"invalid_json_root:{json_path}"
    inline = payload.get("inline_required_output")
    if not isinstance(inline, dict):
        return None, f"missing_inline_required_output:{json_path}"
    return inline, None


def _section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    if next_heading is None:
        return text[start:]
    end = text.find(next_heading, start)
    return text[start:] if end < 0 else text[start:end]


def _table_data_rows(markdown_section: str) -> list[str]:
    rows: list[str] = []
    for line in markdown_section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        compact = stripped.replace(" ", "")
        if compact.startswith("|---") or compact.startswith("|#|Section|"):
            continue
        if stripped.startswith("| # | Section |"):
            continue
        rows.append(stripped)
    return rows


def _row_value(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    return "" if value is None else str(value)


def _validate_bcg(text: str, inline: dict[str, Any], failures: list[str]) -> None:
    section = _section(text, "## Locked BCG Output", "## Locked Section Lane Summary Table")
    bcg = inline.get("bcg") if isinstance(inline.get("bcg"), dict) else {}
    if not section.strip():
        failures.append("bcg.body_missing")
        return
    for key in ("title", "executive_answer"):
        if not _contains(section, bcg.get(key)):
            failures.append(f"bcg.{key}")
    recs = bcg.get("p0_p1_px_recommendations") if isinstance(bcg.get("p0_p1_px_recommendations"), dict) else {}
    for idx, row in enumerate(recs.get("rows") if isinstance(recs.get("rows"), list) else []):
        if not isinstance(row, dict):
            continue
        for key in ("priority", "recommendation", "evidence", "gate_outcome"):
            if not _contains(section, row.get(key)):
                failures.append(f"bcg.p0_p1_px_recommendations.rows[{idx}].{key}")
    board = bcg.get("board_level_readout") if isinstance(bcg.get("board_level_readout"), dict) else {}
    for idx, row in enumerate(board.get("rows") if isinstance(board.get("rows"), list) else []):
        if not isinstance(row, dict):
            continue
        for key in ("question", "answer"):
            if not _contains(section, row.get(key)):
                failures.append(f"bcg.board_level_readout.rows[{idx}].{key}")
    for idx, row in enumerate(bcg.get("issue_tree") if isinstance(bcg.get("issue_tree"), list) else []):
        if not isinstance(row, dict):
            continue
        for key in ("section", "classification", "root_cause"):
            if not _contains(section, row.get(key)):
                failures.append(f"bcg.issue_tree[{idx}].{key}")


def _validate_lane_table(text: str, inline: dict[str, Any], failures: list[str]) -> None:
    section = _section(text, "## Locked Section Lane Summary Table", "## Resume DOCX Full Version Inline")
    lane_table = (
        inline.get("section_lane_summary_table")
        if isinstance(inline.get("section_lane_summary_table"), dict)
        else {}
    )
    rows = lane_table.get("rows") if isinstance(lane_table.get("rows"), list) else []
    if not section.strip():
        failures.append("section_lane_summary_table.body_missing")
        return
    data_rows = _table_data_rows(section)
    if len(data_rows) != len(rows):
        failures.append(f"section_lane_summary_table.row_count expected={len(rows)} observed={len(data_rows)}")
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        for key in ("section", "generation_status", "x3", "display_output"):
            if not _contains(section, _row_value(row, key)):
                failures.append(f"section_lane_summary_table.rows[{idx}].{key}")


def _validate_resume(text: str, inline: dict[str, Any], failures: list[str]) -> None:
    section = _section(text, "## Resume DOCX Full Version Inline")
    resume = (
        inline.get("resume_docx_full_version_inline")
        if isinstance(inline.get("resume_docx_full_version_inline"), dict)
        else {}
    )
    if not section.strip():
        failures.append("resume_docx_full_version_inline.body_missing")
        return
    if not _contains(section, resume.get("source")):
        failures.append("resume_docx_full_version_inline.source")
    if not _contains(section, resume.get("text")):
        failures.append("resume_docx_full_version_inline.text")


def validate_response(text: str) -> list[str]:
    failures: list[str] = []
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            failures.append(f"missing heading: {heading}")

    run_dir = _resolve_run_dir(text)
    if run_dir is None:
        failures.append(f"unable_to_locate_run_dir_with_{MANDATORY_JSON}")
        return failures

    inline, load_error = _load_inline_required_output(run_dir)
    if inline is None:
        failures.append(load_error or "missing_inline_required_output")
        return failures

    _validate_bcg(text, inline, failures)
    _validate_lane_table(text, inline, failures)
    _validate_resume(text, inline, failures)
    return failures


def _reason(failures: list[str]) -> str:
    visible = failures[:18]
    suffix = "" if len(failures) <= len(visible) else f"; +{len(failures) - len(visible)} more"
    return (
        "apps_rg final response must paste mandatory apps_rg runtime evidence inline; "
        "artifact links or summaries are insufficient. Missing/invalid: "
        + "; ".join(visible)
        + suffix
        + ". Required sections: "
        + ", ".join(REQUIRED_HEADINGS)
        + "."
    )


def main() -> int:
    if _bypass():
        return allow("apps_rg inline evidence gate bypass")

    payload = read_payload()
    text = resolve_response_text(payload)
    if not text.strip():
        write_receipt(HOOK_NAME, payload, "allow", "empty stop payload accepted")
        return allow("empty stop payload accepted")
    if not _should_validate(payload, text):
        write_receipt(HOOK_NAME, payload, "allow", "not an apps_rg run closeout")
        return allow("not an apps_rg run closeout")

    failures = validate_response(text)
    if not failures:
        write_receipt(HOOK_NAME, payload, "allow", "apps_rg inline evidence accepted")
        return allow("apps_rg inline evidence accepted")

    reason = _reason(failures)
    write_receipt(HOOK_NAME, payload, "block", reason)
    return block(reason)


if __name__ == "__main__":
    raise SystemExit(main())
