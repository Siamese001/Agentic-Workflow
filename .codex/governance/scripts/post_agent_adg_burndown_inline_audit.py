#!/usr/bin/env python3
"""post_agent_adg_burndown_inline_audit.py — ADG burndown inline-render gate.

Reads the agent response from stdin (post-agent payload). If the response
contains a ``generate_full_adg`` / ``run_full_adg_audit`` / ``adg_gates/run.py``
invocation AND a completion claim (PASS / completed / "exit 0"), it asserts the
SAME response also rendered the ADG CI burndown **inline** — i.e. the severity-band
summary AND the CI-gates table.

Rationale: ``.codex/rules/adg-post-run-burndown.md`` § Completion Gate makes the
inline summary + gates table a non-bypassable completion requirement. The report
is already emitted to stdout by ``emit_mandatory_adg_burndown_report()``; this gate
catches the case where the operator ran the generator but did not surface the table
in chat (a proof-contract violation per ``002-pass-blocked-proof-contract``).

**Advisory only** — always exits 0 (fail-open). Logs a VIOLATION row to
``artifacts/governance/adg_burndown_inline_violations.jsonl`` and prints a
``VIOLATION:`` / ``ALLOW:`` / ``NOT_APPLICABLE:`` line to stderr. It never claims to
block an already-emitted response.

Bypass: ``ADG_BURNDOWN_INLINE_BYPASS=1`` (also suppresses the stdout markdown).

Companion rule: ``.codex/rules/adg-post-run-burndown.md`` § Completion Gate.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _post_agent_payload import extract_response_text

fail_policy = "open"

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "governance" / "adg_burndown_inline_violations.jsonl"
MAX_RESPONSE_BYTES = 1024 * 1024

# A generate / audit run appears in the response (tool invocation or prose mention).
_RUN_PATTERNS = (
    re.compile(r"generate_full_adg\.py", re.IGNORECASE),
    re.compile(r"run_full_adg_audit\.py", re.IGNORECASE),
    re.compile(r"adg_gates[\\/]run\.py", re.IGNORECASE),
    re.compile(r"\bpython\b[^\n]*\bgenerate_full_adg\b", re.IGNORECASE),
)

# A completion / pass claim about that run.
_COMPLETION_PATTERNS = (
    re.compile(r"\bSTATUS:\s*PASS\b", re.IGNORECASE),
    re.compile(r"\bADG\b[^\n]{0,40}\b(generated|complete|completed|done|green)\b", re.IGNORECASE),
    re.compile(r"\bexit[ _]?(?:code)?\s*[:=]?\s*0\b", re.IGNORECASE),
    re.compile(r"\bgeneration\s+(complete|completed|succeeded)\b", re.IGNORECASE),
)

# Inline burndown was rendered: need BOTH a band-summary signal AND a gates-table signal.
_BAND_SUMMARY_PATTERNS = (
    re.compile(r"Burndown by Severity Band", re.IGNORECASE),
    re.compile(r"\bP0\b[^\n]*\blayer_violations\b", re.IGNORECASE),
    re.compile(r"\bFIX\b[^\n]*\bTRACK\b[^\n]*\bCLEAR\b"),
)
_GATES_TABLE_PATTERNS = (
    re.compile(r"Recommended Next Step", re.IGNORECASE),
    re.compile(r"All CI Gates", re.IGNORECASE),
    re.compile(r"\|\s*Gate ID\s*\|", re.IGNORECASE),
)


def _read_response() -> str:
    try:
        raw = sys.stdin.read(MAX_RESPONSE_BYTES + 1)
    except OSError:
        return ""
    if not raw:
        return ""
    return extract_response_text(raw)


def _any(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    return any(p.search(text) for p in patterns)


def evaluate(text: str) -> tuple[str, str]:
    """Return (verdict, reason). verdict in {NOT_APPLICABLE, ALLOW, VIOLATION}."""
    if os.environ.get("ADG_BURNDOWN_INLINE_BYPASS") == "1":
        return "ALLOW", "ADG_BURNDOWN_INLINE_BYPASS=1"
    if not _any(text, _RUN_PATTERNS):
        return "NOT_APPLICABLE", "no ADG generate/audit run in response"
    if not _any(text, _COMPLETION_PATTERNS):
        return "NOT_APPLICABLE", "ADG run present but no completion/PASS claim"
    has_band = _any(text, _BAND_SUMMARY_PATTERNS)
    has_table = _any(text, _GATES_TABLE_PATTERNS)
    if has_band and has_table:
        return "ALLOW", "inline burndown summary + gates table present"
    missing = []
    if not has_band:
        missing.append("severity-band summary")
    if not has_table:
        missing.append("CI-gates table")
    return "VIOLATION", "ADG run marked complete without inline " + " + ".join(missing)


def _log_violation(reason: str) -> None:
    try:
        VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "rule": "adg-post-run-burndown#completion-gate",
            "reason": reason,
        }
        with VIOLATIONS_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        # guardian: allow-broad-exception -- audit fail-open contract (logging best-effort)
        pass


def main() -> int:
    text = _read_response()
    try:
        verdict, reason = evaluate(text)
    except Exception as exc:  # guardian: allow-broad-exception -- audit fail-open contract
        sys.stderr.write(f"adg_burndown_inline_audit error (allowing): {exc}\n")
        return 0
    if verdict == "VIOLATION":
        _log_violation(reason)
    sys.stderr.write(f"{verdict}: {reason}\n")
    return 0  # advisory — always fail-open


if __name__ == "__main__":
    raise SystemExit(main())
