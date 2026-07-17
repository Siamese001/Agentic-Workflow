#!/usr/bin/env python3
"""post_agent_adg_burndown_inline_audit.py — sealed ADG output-bundle gate.

Reads the agent response from stdin (post-agent payload). If the response
contains a ``generate_full_adg`` / ``run_full_adg_audit``
invocation AND a completion claim (PASS / completed / "exit 0"), it asserts the
SAME response also rendered exactly one sealed ADG executive brief **inline** —
including the impact inventory, decision-gate/FIX view, and final process
disposition. A standalone burndown replay is rejected as duplicate terminal
output.

Rationale: ``.codex/rules/adg-post-run-burndown.md`` § Completion Gate makes the
single sealed summary a non-bypassable completion requirement. The report is
emitted only after the output bundle and wrapper gates finish; this gate catches
the case where the operator ran the generator but did not surface that final brief
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
    re.compile(r"\bpython\b[^\n]*\bgenerate_full_adg\b", re.IGNORECASE),
)

# A completion / pass claim about that run.
_COMPLETION_PATTERNS = (
    re.compile(r"\bSTATUS:\s*PASS\b", re.IGNORECASE),
    re.compile(r"\bADG\b[^\n]{0,40}\b(generated|complete|completed|done|green)\b", re.IGNORECASE),
    re.compile(r"\bexit[ _]?(?:code)?\s*[:=]?\s*0\b", re.IGNORECASE),
    re.compile(r"\bgeneration\s+(complete|completed|succeeded)\b", re.IGNORECASE),
)

# One sealed executive brief: need its unique header, impact inventory, and decision gate.
_BUNDLE_HEADER = re.compile(r"^## ADG Executive Brief\s*$", re.IGNORECASE | re.MULTILINE)
_BAND_SUMMARY_PATTERNS = (
    re.compile(r"Impact Inventory", re.IGNORECASE),
    re.compile(r"\|\s*Band\s*\|\s*Impact severity\s*\|", re.IGNORECASE),
)
_GATES_TABLE_PATTERNS = (
    re.compile(r"Decision gate:", re.IGNORECASE),
    re.compile(r"\|\s*Gate\s*\|\s*Status\s*\|\s*Evidence\s*\|", re.IGNORECASE),
    re.compile(r"Fix now:", re.IGNORECASE),
)
_FINAL_DISPOSITION_HEADER = re.compile(r"^## Final disposition\s*$", re.IGNORECASE | re.MULTILINE)
_PROCESS_EXIT_CODE = re.compile(
    r"^\s*-\s*\*\*Process exit code:\*\*\s*`?-?\d+`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_STANDALONE_BURNDOWN_HEADER = re.compile(r"^# ADG CI Burndown Report\s*$", re.IGNORECASE | re.MULTILINE)


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
    header_count = len(_BUNDLE_HEADER.findall(text))
    final_disposition_count = len(_FINAL_DISPOSITION_HEADER.findall(text))
    process_exit_code_count = len(_PROCESS_EXIT_CODE.findall(text))
    burndown_replay_count = len(_STANDALONE_BURNDOWN_HEADER.findall(text))
    has_band = _any(text, _BAND_SUMMARY_PATTERNS)
    has_table = _any(text, _GATES_TABLE_PATTERNS)
    if (
        header_count == 1
        and has_band
        and has_table
        and final_disposition_count == 1
        and process_exit_code_count == 1
        and burndown_replay_count == 0
    ):
        return "ALLOW", "one sealed ADG executive brief with final disposition present"
    missing = []
    if header_count != 1:
        missing.append(f"exactly one executive brief (found {header_count})")
    if not has_band:
        missing.append("severity-band summary")
    if not has_table:
        missing.append("CI-gates table")
    if final_disposition_count != 1:
        missing.append(f"exactly one final disposition (found {final_disposition_count})")
    if process_exit_code_count != 1:
        missing.append(f"exactly one process exit code (found {process_exit_code_count})")
    if burndown_replay_count:
        missing.append(f"no standalone burndown replay (found {burndown_replay_count})")
    return "VIOLATION", "ADG run marked complete without sealed inline " + " + ".join(missing)


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
