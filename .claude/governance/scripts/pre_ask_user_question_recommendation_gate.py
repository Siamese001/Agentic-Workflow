#!/usr/bin/env python3
"""pre_ask_user_question_recommendation_gate.py — native AskUserQuestion contract gate.

Companion thin hook: ``.claude/hooks/before_ask_user_question.py`` (registered under
``PreToolUse`` matcher ``AskUserQuestion``).

Why this exists
---------------
Constitutional §6 / CLAUDE.md Author-Gate require: when ≥2 plausible approaches have
different blast radius and no unambiguous directive, call the native ``AskUserQuestion``
tool **and mark the recommended option**. The retired W1 Author-Gate pipeline
(``author-gate-packet-builder`` → ``author-gate-ui-renderer``; ADR-093 /
``claude-native-supersession-9d3f7a``) used to *manufacture* two load-bearing fields
deterministically — a STAR recommendation and a confidence band. The native tool dropped
those affordances, so the §6 invariant lost its enforcing mechanism (RCA 2026-06-08: two
AskUserQuestion calls shipped with neither a ``(Recommended)`` marker nor a confidence
signal).

This gate re-adds the missing deterministic control on the *native tool input*. It is the
post-supersession successor to the retired routing gate
(``_legacy_windsurf/pre_ask_user_question_gate.py``) — distinct name on purpose so the two
are never confused. It inspects the proposed ``AskUserQuestion`` options and flags when:

* no option label ends with ``(Recommended)`` — the §6 marker is absent (Finding 1);
* the recommended option's description carries no confidence signal — the retired
  renderer's confidence band is missing (Finding 2);
* the recommended option is not placed first (native-tool authoring convention).

Decision contract (``evaluate``)
--------------------------------
Returns ``(0, reason)`` to allow or ``(2, reason)`` to block.

* Not an ``AskUserQuestion`` call ............ allow
* ``ASK_REC_GUARD_BYPASS=1`` ................. allow (logged)
* Every question has a marked + confident recommendation ... allow
* A question is missing the marker / confidence ............ **ADVISORY warn (exit 0)** by
  default; **BLOCK (exit 2)** only when ``ASK_REC_GUARD_STRICT=1``.

Advisory-by-default because not every AskUserQuestion is an Author-Gate-class decision (a
symmetric preference question legitimately has no recommendation); strict mode is opt-in for
sessions that want a hard contract. Fail policy: OPEN — any unexpected error → allow
(exit 0). A governance gate must never be the reason a turn hangs or dies.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_VIOLATIONS_LOG = _REPO_ROOT / "artifacts" / "cursor" / "ask_user_question_violations.jsonl"

_BYPASS_ENV = "ASK_REC_GUARD_BYPASS"
_STRICT_ENV = "ASK_REC_GUARD_STRICT"

# A "(Recommended)" suffix on an option label (case-insensitive, trailing-space tolerant).
_RECOMMENDED_RE = re.compile(r"\(\s*recommended\s*\)\s*$", re.IGNORECASE)
# A confidence signal in the recommended option's description: the word "confidence" or an
# explicit band token. Loose on purpose — this is an advisory presence check, not a parser.
_CONFIDENCE_RE = re.compile(r"confiden|\b(?:high|medium|low)\b", re.IGNORECASE)


def _bypass() -> bool:
    return os.environ.get(_BYPASS_ENV) == "1"


def _strict() -> bool:
    return os.environ.get(_STRICT_ENV) == "1"


def question_findings(idx: int, question: dict) -> list[str]:
    """Return human-readable findings for one question (empty list == compliant)."""
    if not isinstance(question, dict):
        return []
    options = question.get("options")
    if not isinstance(options, list) or not options:
        # No options to evaluate (free-text only) — nothing to enforce.
        return []
    opt_dicts = [o for o in options if isinstance(o, dict)]
    labels = [str(o.get("label", "")) for o in opt_dicts]
    rec_positions = [i for i, label in enumerate(labels) if _RECOMMENDED_RE.search(label)]
    header = str(question.get("header") or question.get("question") or f"q{idx}")[:48]
    findings: list[str] = []
    if not rec_positions:
        findings.append(f"[{header}] no option marked '(Recommended)' (§6 marker absent)")
        return findings
    rec_descs = [str(opt_dicts[i].get("description", "")) for i in rec_positions]
    if not any(_CONFIDENCE_RE.search(d) for d in rec_descs):
        findings.append(
            f"[{header}] recommended option carries no confidence signal "
            "(high/medium/low or 'confidence')"
        )
    if 0 not in rec_positions:
        findings.append(f"[{header}] recommended option is not placed first")
    return findings


def evaluate(payload: dict) -> tuple[int, str]:
    """Pure decision function. Returns (exit_code, reason). Logs on non-compliance."""
    if not isinstance(payload, dict):
        return 0, "non-dict payload — allow (fail-open)"
    if payload.get("tool_name") != "AskUserQuestion":
        return 0, "not AskUserQuestion — allow"
    if _bypass():
        return 0, f"{_BYPASS_ENV}=1 — allow (logged)"

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0, "no tool_input — allow"
    questions = tool_input.get("questions")
    if not isinstance(questions, list) or not questions:
        return 0, "no questions — allow"

    all_findings: list[str] = []
    for idx, question in enumerate(questions):
        all_findings.extend(question_findings(idx, question))

    if not all_findings:
        return 0, "ok: every question has a marked, confidence-bearing recommendation"

    reason = "; ".join(all_findings)
    _log_violation(payload, reason)
    if _strict():
        return 2, f"AskUserQuestion recommendation/confidence contract: {reason}"
    return 0, f"ADVISORY (AskUserQuestion recommendation/confidence): {reason}"


def _log_violation(payload: dict, reason: str) -> None:
    """Append one JSONL violation row. Fail-open — logging must never wedge the gate."""
    try:
        _VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "tool_name": payload.get("tool_name"),
            "session_id": payload.get("session_id"),
            "strict": _strict(),
            "reason": reason,
        }
        with _VIOLATIONS_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        # guardian: allow-broad-exception -- gate fail-open contract (logging is best-effort)
        pass


def main() -> int:
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    try:
        code, reason = evaluate(payload if isinstance(payload, dict) else {})
    except Exception as exc:  # guardian: allow-broad-exception -- gate fail-open contract
        sys.stderr.write(f"pre_ask_user_question_recommendation_gate error (allowing): {exc}\n")
        return 0
    if (code != 0) or reason.startswith("ADVISORY"):
        sys.stderr.write(reason + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
