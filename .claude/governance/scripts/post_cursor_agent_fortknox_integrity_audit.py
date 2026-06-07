#!/usr/bin/env python3
"""Fort Knox integrity audit — Constitutional §32.

Fires on every Cursor Agent response via `post_cursor_agent_response`. Fail-open
(never blocks). Appends structured violation rows to
`artifacts/cursor/fortknox_integrity_violations.jsonl` when Cursor Agent
has made a forbidden claim or edit in the current response.

Detection (conservative — prefers false negatives over false positives
to avoid drowning the log):
1. Prose claim that a requirement is SIGNED_OFF / FINAL_SIGNED_CERTIFICATION
   / "certified" / "trust level upgraded" / "acceptance complete"
   without a matching subprocess invocation of
   `compile_requirement_signoff.py` in the same response.
2. Prose edit hint indicating Cursor Agent touched
   `final_requirement_signoff_report.json` manually (tool-call name
   `edit`/`write_to_file` with the report path).
3. Use of the forbidden vocabulary `"all_pass"` / `"linked_req_ids"`
   outside a context that also names the atomic-assertions JSONL
   (the two surface together when Cursor Agent is correctly discussing
   the forbidden pattern — otherwise it is a regression).

Input: Cursor Agent response body on stdin (Windsurf convention), or a file
path via `--response-path`. Silent no-op on empty stdin.

Advisory rule: `.claude/rules/fortknox-certification-discipline.md`.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path


_SIGNOFF_CLAIM_RE = re.compile(
    r"\b(SIGNED_OFF|FINAL_SIGNED_CERTIFICATION|trust[-_ ]level[- ]upgraded"
    r"|acceptance\s+complete|all\s+requirements\s+pass|runtime\s+certified)\b",
    re.IGNORECASE,
)
_COMPILER_INVOCATION_RE = re.compile(
    r"compile_requirement_signoff\.py", re.IGNORECASE
)
_MANUAL_REPORT_EDIT_RE = re.compile(
    r"(final_requirement_signoff_report\.(?:json|sha256|merkle\.json|signature\.json))",
    re.IGNORECASE,
)
_EDIT_TOOL_CALL_RE = re.compile(
    r'<function_calls>.*?<invoke name="(?:edit|write_to_file|multi_edit)">',
    re.IGNORECASE | re.DOTALL,
)
_FORBIDDEN_VOCAB_RE = re.compile(r"\"(all_pass|linked_req_ids)\"")
_ATOMIC_CONTEXT_RE = re.compile(
    r"evidence_assertions\.jsonl|atomic[- ]assertion|fortknox-certification-discipline",
    re.IGNORECASE,
)


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / ".git").exists():
            return p
    return Path.cwd()


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log_violations(rows: list[dict], repo: Path) -> None:
    if not rows:
        return
    out_dir = repo / "artifacts" / "windsurf"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "fortknox_integrity_violations.jsonl"
    try:
        with out.open("a", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError as exc:  # fail-open
        print(f"[post_cursor_agent_fortknox_integrity_audit] WARN: log write failed: {exc}", file=sys.stderr)


def _read_response(args: argparse.Namespace) -> str:
    if args.response_path:
        try:
            return Path(args.response_path).read_text(encoding="utf-8")
        except OSError:
            return ""
    if not sys.stdin.isatty():
        try:
            return sys.stdin.read()
        except (OSError, UnicodeDecodeError):
            return ""
    return ""


def analyze(body: str) -> list[dict]:
    """Return violation dicts. Pure function for testability."""
    violations: list[dict] = []
    if not body:
        return violations

    ts = _now_iso()

    # (1) signoff claim without compiler invocation.
    if _SIGNOFF_CLAIM_RE.search(body) and not _COMPILER_INVOCATION_RE.search(body):
        matches = _SIGNOFF_CLAIM_RE.findall(body)
        violations.append({
            "timestamp_utc": ts,
            "kind": "signoff_claim_without_compiler",
            "detail": f"prose asserts signoff ({matches[:3]}) but no compile_requirement_signoff.py invocation found",
            "severity": "high",
        })

    # (2) manual report edit.
    if _EDIT_TOOL_CALL_RE.search(body) and _MANUAL_REPORT_EDIT_RE.search(body):
        match = _MANUAL_REPORT_EDIT_RE.search(body)
        violations.append({
            "timestamp_utc": ts,
            "kind": "manual_report_edit",
            "detail": f"edit/write_to_file invocation paired with report artifact path: {match.group(1)}",
            "severity": "critical",
        })

    # (3) forbidden vocabulary outside atomic-assertion context.
    if _FORBIDDEN_VOCAB_RE.search(body) and not _ATOMIC_CONTEXT_RE.search(body):
        matches = _FORBIDDEN_VOCAB_RE.findall(body)
        violations.append({
            "timestamp_utc": ts,
            "kind": "forbidden_vocab_without_context",
            "detail": f"uses {sorted(set(matches))} outside of atomic-assertion context",
            "severity": "medium",
        })

    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-path", default=None)
    args = parser.parse_args()

    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        return 0

    try:
        body = _read_response(args)
        violations = analyze(body)
        if violations:
            _log_violations(violations, _repo_root())
    except (OSError, ValueError) as exc:  # fail-open
        print(f"[post_cursor_agent_fortknox_integrity_audit] WARN: {exc!r} — fail-open", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
