#!/usr/bin/env python3
"""Post-agent audit: plan edits must keep consolidated wave summary at top.

Scans Cursor Agent response text for ``.claude/plans/*.md`` paths, validates each
file on disk via ``plan_wave_summary_top`` shared module.

Bypass: ``PLAN_WAVE_SUMMARY_TOP_AUDIT_BYPASS=1``.
Strict (stderr + exit 2): ``PLAN_WAVE_SUMMARY_TOP_AUDIT_STRICT=1``.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_LOG_PATH = _ROOT / "artifacts" / "cursor" / "plan_wave_summary_top_violations.jsonl"
_BYPASS_ENV = "PLAN_WAVE_SUMMARY_TOP_AUDIT_BYPASS"
_STRICT_ENV = "PLAN_WAVE_SUMMARY_TOP_AUDIT_STRICT"

_PLAN_PATH_RE = re.compile(
    r"(?:[\\/]|^)\.cursor[\\/]plans[\\/]([A-Za-z0-9_\-]+-[0-9a-f]{6})\.md",
    re.IGNORECASE,
)


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("tool_info", "response", "text", "content"):
            val = payload.get(key)
            if isinstance(val, dict):
                for inner in ("response", "text", "content"):
                    inner_val = val.get(inner)
                    if isinstance(inner_val, str) and inner_val.strip():
                        return inner_val
            if isinstance(val, str) and val.strip():
                return val
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def _find_edited_plans(response_text: str) -> list[Path]:
    stems = {m.group(1).lower() for m in _PLAN_PATH_RE.finditer(response_text)}
    if not stems:
        return []
    plans_dir = _ROOT / ".claude" / "plans"
    found: list[Path] = []
    for stem in sorted(stems):
        candidate = plans_dir / f"{stem}.md"
        if candidate.is_file():
            found.append(candidate)
    return found


def _log_violation(plan_rel: str, rule_id: str, line: int, message: str) -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "plan": plan_rel,
        "rule_id": rule_id,
        "line": line,
        "message": message,
    }
    with _LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def main() -> int:
    if os.environ.get(_BYPASS_ENV, "").strip() in ("1", "true", "yes"):
        return 0

    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    response_text = _extract_response_text(payload)
    plan_paths = _find_edited_plans(response_text)
    if not plan_paths:
        return 0

    from ops_scripts.ci.plan_wave_summary_top import (
        WaveSummarySeverity,
        validate_consolidated_wave_summary_at_top,
    )

    strict = os.environ.get(_STRICT_ENV, "").strip() in ("1", "true", "yes")
    any_fail = False

    for plan_path in plan_paths:
        rel = str(plan_path.relative_to(_ROOT)).replace("\\", "/")
        try:
            content = plan_path.read_text(encoding="utf-8")
        except OSError as exc:
            msg = f"cannot read plan: {exc}"
            _log_violation(rel, "READ-ERROR", 0, msg)
            print(f"[PLAN-WAVE-TOP-AUDIT] {rel}: {msg}", file=sys.stderr)
            any_fail = True
            continue

        violations = validate_consolidated_wave_summary_at_top(content, rel)
        for v in violations:
            if v.severity != WaveSummarySeverity.FAIL:
                continue
            any_fail = True
            _log_violation(rel, v.rule_id, v.line_num, v.message)
            print(
                f"[PLAN-WAVE-TOP-AUDIT] {rel}:{v.line_num} [{v.rule_id}] {v.message}",
                file=sys.stderr,
            )

    if any_fail and strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
