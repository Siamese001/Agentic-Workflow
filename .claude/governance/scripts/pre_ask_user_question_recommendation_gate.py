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
post-supersession successor to the retired legacy AskUserQuestion routing gate. It inspects
the proposed ``AskUserQuestion`` options and flags when:

* no option label ends with ``(Recommended)`` — the §6 marker is absent (Finding 1);
* the recommended option's description carries no confidence signal — the retired
  renderer's confidence band is missing (Finding 2);
* the recommended option is not placed first (native-tool authoring convention).

Canonical option shape (SSOT)
-----------------------------
Authoring-convention SSOT: the ``ask-user-question-recommendation`` skill. Recommended option
first; its ``label`` ends ``(Recommended)``; **every** option ``description`` begins with a
numeric ``[confidence=0.NN]`` prefix, and the recommended one with
``[RECOMMENDED ⭐ confidence=0.NN]`` (one star). The confidence check below stays tolerant of a
bare ``high``/``medium``/``low`` word as a *legacy fallback* so an older-style call never
hard-blocks — but the numeric ``[confidence=0.NN]`` prefix is the only canonical form.

Decision contract (``evaluate``)
--------------------------------
Returns ``(0, reason)`` to allow or ``(2, reason)`` to block.

* Not an ``AskUserQuestion`` call ............ allow
* ``ASK_REC_GUARD_BYPASS=1`` ................. allow (logged)
* Every question has a marked + confident recommendation ... allow
* A marked ``(Recommended)`` option with **no confidence signal** ... **BLOCK (exit 2) by
  default** — the exact §6 / user-directive violation (a recommendation must carry a
  confidence level). Override only with ``ASK_REC_GUARD_BYPASS=1``.
* **No** option marked ``(Recommended)`` at all, or recommended-not-first ... **ADVISORY
  (exit 0)** by default; **BLOCK** only when ``ASK_REC_GUARD_STRICT=1``.

Default-to-enforcement (user directive 2026-06-13): the core case — *a recommendation was
made but carries no confidence* — blocks by default. The soft case stays advisory because a
missing recommendation may be a legitimate symmetric preference question, not a miss. Fail
policy: OPEN — any unexpected error → allow (exit 0). A governance gate must never be the
reason a turn hangs or dies.
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
# Advisory-only precedent calibration (W2.2 of askq-confidence-meta-learning-loop). Default on;
# set to 0 to silence. NEVER affects the allow/block decision.
_CALIB_ADVISORY_ENV = "ASK_REC_CALIBRATION_ADVISORY"

# A "(Recommended)" suffix on an option label (case-insensitive, trailing-space tolerant).
_RECOMMENDED_RE = re.compile(r"\(\s*recommended\s*\)\s*$", re.IGNORECASE)
# A confidence signal in the recommended option's description: the word "confidence" or an
# explicit band token. Loose on purpose — this is an advisory presence check, not a parser.
_CONFIDENCE_RE = re.compile(r"confiden|\b(?:high|medium|low)\b", re.IGNORECASE)


def _bypass() -> bool:
    return os.environ.get(_BYPASS_ENV) == "1"


def _strict() -> bool:
    return os.environ.get(_STRICT_ENV) == "1"


_NUM_CONFIDENCE_RE = re.compile(r"confidence\s*=\s*([01](?:\.\d+)?)", re.IGNORECASE)


def _context_slug(question: dict, idx: int) -> str:
    """Mirror post_ask_user_question_capture._context_from_question so precedent lookups align."""
    raw = str(question.get("header") or question.get("question") or f"q{idx}")
    slug = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower()).strip("-")
    return (slug or f"q{idx}")[:64]


def calibration_notes(payload: dict) -> list[str]:
    """Best-effort ADVISORY notes when a stated confidence diverges from empirical acceptance.

    Pure-read, fail-open: never raises, never affects the allow/block decision (W2.2 of
    askq-confidence-meta-learning-loop). One note per question whose recommended-option
    confidence diverges from captured precedent for its context.
    """
    if os.environ.get(_CALIB_ADVISORY_ENV, "1").strip().lower() in ("0", "false", "no"):
        return []
    try:
        from tools.ledgers.ask_user_question_calibration import lookup_calibrated_confidence
    except Exception:  # guardian: allow-broad-exception -- consult is optional; absence is fine
        return []
    tool_input = payload.get("tool_input")
    questions = tool_input.get("questions") if isinstance(tool_input, dict) else None
    if not isinstance(questions, list):
        return []
    notes: list[str] = []
    for idx, question in enumerate(questions):
        if not isinstance(question, dict):
            continue
        options = [o for o in (question.get("options") or []) if isinstance(o, dict)]
        rec = next((o for o in options if _RECOMMENDED_RE.search(str(o.get("label", "")))), None)
        if rec is None:
            continue
        m = _NUM_CONFIDENCE_RE.search(str(rec.get("description", "")))
        if not m:
            continue
        try:
            result = lookup_calibrated_confidence(_context_slug(question, idx), float(m.group(1)))
        except Exception:  # guardian: allow-broad-exception -- best-effort consult
            continue
        if result.signal != "none" and result.diverged:
            notes.append(
                f"[{result.context}] stated {result.stated_confidence:.2f} vs empirical "
                f"acceptance {result.empirical_acceptance:.0%} (n={result.n}, {result.signal}) "
                f"-> consider ~{result.calibrated_confidence:.2f}"
            )
    return notes


def question_findings(idx: int, question: dict) -> list[tuple[str, str]]:
    """Return ``(severity, message)`` findings for one question (empty == compliant).

    severity is ``"block"`` (a marked recommendation with NO confidence — the core
    violation, blocks by default) or ``"advisory"`` (no recommendation marked at all, or
    recommended-not-first — soft, advisory unless ``ASK_REC_GUARD_STRICT=1``).
    """
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
    if not rec_positions:
        # Possibly a legitimate symmetric preference question — advisory, not a hard block.
        return [(
            "advisory",
            f"[{header}] no option marked '(Recommended)' (§6 marker absent, or a symmetric question)",
        )]
    findings: list[tuple[str, str]] = []
    rec_descs = [str(opt_dicts[i].get("description", "")) for i in rec_positions]
    if not any(_CONFIDENCE_RE.search(d) for d in rec_descs):
        findings.append((
            "block",
            f"[{header}] recommended option carries no confidence signal "
            "(e.g. 'confidence=0.NN' or high/medium/low)",
        ))
    if 0 not in rec_positions:
        findings.append(("advisory", f"[{header}] recommended option is not placed first"))
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

    block_findings: list[str] = []
    advisory_findings: list[str] = []
    for idx, question in enumerate(questions):
        for severity, message in question_findings(idx, question):
            (block_findings if severity == "block" else advisory_findings).append(message)

    if not block_findings and not advisory_findings:
        return 0, "ok: every question has a marked, confidence-bearing recommendation"

    _log_violation(payload, "; ".join(block_findings + advisory_findings))

    # Default to enforcement: a marked (Recommended) option with no confidence signal is the
    # exact contract violation — block by default (override only via ASK_REC_GUARD_BYPASS=1).
    if block_findings:
        return 2, f"AskUserQuestion recommendation/confidence contract: {'; '.join(block_findings)}"
    # Soft findings (no recommendation marked — possibly a symmetric question; or not-first):
    # advisory by default, blocking only under strict mode.
    if _strict():
        return 2, f"AskUserQuestion recommendation/confidence contract (strict): {'; '.join(advisory_findings)}"
    return 0, f"ADVISORY (AskUserQuestion recommendation/confidence): {'; '.join(advisory_findings)}"


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
    try:
        for note in calibration_notes(payload if isinstance(payload, dict) else {}):
            sys.stderr.write("ADVISORY (askq-calibration): " + note + "\n")
    except Exception:  # guardian: allow-broad-exception -- advisory must never affect the decision
        pass
    if (code != 0) or reason.startswith("ADVISORY"):
        sys.stderr.write(reason + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
