#!/usr/bin/env python3
"""pre_ask_user_question_recommendation_gate.py — Codex request_user_input contract gate.

Companion thin hook: ``.codex/hooks/before_ask_user_question.py``.

Why this exists
---------------
Constitutional §6 / AGENTS.md Author-Gate require: when ≥2 plausible approaches have
different blast radius and no unambiguous directive, call Codex ``request_user_input`` and
mark the recommended option. This gate adds deterministic control on the proposed Codex
tool input. It inspects each question and flags when:

* the Codex schema fields are absent or malformed (``id``, ``header``, ``question``, and
  2-3 options);
* no option label ends with ``(Recommended)`` — the §6 marker is absent (Finding 1);
* the recommended option's description does not begin with the canonical confidence prefix;
* any option description lacks a numeric confidence prefix or Pros/Cons text;
* the recommended option is not placed first;
* the recommended option lacks the required ``Flips if`` calibration condition.

Canonical option shape (SSOT)
-----------------------------
Authoring-convention SSOT: the ``ask-user-question-recommendation`` skill. Every Codex
question includes a stable ``id`` and a short ``header``. The recommended option goes first,
its ``label`` ends ``(Recommended)``, **every** option ``description`` begins with a numeric
``[confidence=0.NN]`` prefix, and the recommended one begins with
``[RECOMMENDED ⭐ confidence=0.NN]`` (one star). Every option also carries ``Pros:`` and
``Cons:`` text; the recommended option names the fact that would flip the recommendation.

Decision contract (``evaluate``)
--------------------------------
Returns ``(0, reason)`` to allow or ``(2, reason)`` to block.

* Not a Codex request_user_input call ........ allow
* ``ASK_REC_GUARD_BYPASS=1`` ................. allow (logged)
* Every question has a marked + canonical recommendation ... allow
* A Codex question with malformed schema fields ... **BLOCK (exit 2) by default**
* A marked ``(Recommended)`` option with a non-canonical shape ... **BLOCK (exit 2) by
  default** — the exact §6 / user-directive violation (a recommendation must carry
  confidence, pros/cons, and flip criteria). Override only with ``ASK_REC_GUARD_BYPASS=1``.
* **No** option marked ``(Recommended)`` at all, or recommended-not-first ... **ADVISORY
  (exit 0)** by default; **BLOCK** only when ``ASK_REC_GUARD_STRICT=1``.

Default-to-enforcement (user directive 2026-06-13, reinforced 2026-06-15): the core case —
*a recommendation was made but does not carry the full output criteria* — blocks by default.
The soft case stays advisory because a missing recommendation may be a legitimate symmetric
preference question, not a miss. Fail policy: OPEN — any unexpected error → allow (exit 0).
A governance gate must never be the reason a turn hangs or dies.
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

_QUESTION_TOOL_NAMES = frozenset({"request_user_input", "functions.request_user_input"})

# A "(Recommended)" suffix on an option label (case-insensitive, trailing-space tolerant).
_RECOMMENDED_RE = re.compile(r"\(\s*recommended\s*\)\s*$", re.IGNORECASE)
# Canonical visible option description prefixes.
_CONFIDENCE_VALUE = r"(0\.\d{2}|1\.00)"
_NUMERIC_PREFIX_RE = re.compile(rf"^\[confidence=({_CONFIDENCE_VALUE})\]\s*", re.IGNORECASE)
_RECOMMENDED_PREFIX_RE = re.compile(
    rf"^\[RECOMMENDED\s+⭐\s+confidence=({_CONFIDENCE_VALUE})\]\s*",
    re.IGNORECASE,
)
_PROS_RE = re.compile(r"\bPros:\s*\S", re.IGNORECASE)
_CONS_RE = re.compile(r"\bCons:\s*\S", re.IGNORECASE)
_FLIPS_RE = re.compile(r"\bFlips?\s+if\b", re.IGNORECASE)


def _bypass() -> bool:
    return os.environ.get(_BYPASS_ENV) == "1"


def _strict() -> bool:
    return os.environ.get(_STRICT_ENV) == "1"


def _is_question_tool(tool_name: object) -> bool:
    if not isinstance(tool_name, str):
        return False
    return tool_name in _QUESTION_TOOL_NAMES or tool_name.endswith(".request_user_input")


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

    severity is ``"block"`` (a marked recommendation with non-canonical output criteria —
    the core violation, blocks by default) or ``"advisory"`` (no recommendation marked at
    all — soft, advisory unless ``ASK_REC_GUARD_STRICT=1``).
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
    if len(rec_positions) > 1:
        findings.append((
            "block",
            f"[{header}] more than one option is marked '(Recommended)'",
        ))
    rec_idx = rec_positions[0]
    rec_desc = str(opt_dicts[rec_idx].get("description", ""))
    if rec_idx != 0:
        findings.append(("block", f"[{header}] recommended option is not placed first"))
    if not _RECOMMENDED_PREFIX_RE.search(rec_desc):
        findings.append((
            "block",
            f"[{header}] recommended description must begin "
            "'[RECOMMENDED ⭐ confidence=0.NN]' with a numeric 0.00-1.00 confidence value",
        ))
    if rec_desc.count("⭐") != 1:
        findings.append(("block", f"[{header}] recommended description must contain exactly one ⭐"))
    if not _FLIPS_RE.search(rec_desc):
        findings.append(("block", f"[{header}] recommended description must state 'Flips if ...'"))

    for pos, opt in enumerate(opt_dicts):
        desc = str(opt.get("description", ""))
        label = str(opt.get("label", "") or f"option {pos + 1}")
        has_prefix = (
            bool(_RECOMMENDED_PREFIX_RE.search(desc))
            if pos == rec_idx
            else bool(_NUMERIC_PREFIX_RE.search(desc))
        )
        if not has_prefix:
            findings.append((
                "block",
                f"[{header}] {label} description must begin with numeric 0.00-1.00 confidence prefix",
            ))
        if not (_PROS_RE.search(desc) and _CONS_RE.search(desc)):
            findings.append((
                "block",
                f"[{header}] {label} description must include Pros: and Cons:",
            ))
    return findings


def codex_schema_findings(idx: int, question: dict) -> list[str]:
    """Return blocking findings for malformed Codex request_user_input questions."""
    if not isinstance(question, dict):
        return [f"[q{idx}] question must be an object"]

    header = str(question.get("header") or question.get("question") or f"q{idx}")[:48]
    findings: list[str] = []
    for field in ("id", "header", "question"):
        value = question.get(field)
        if not isinstance(value, str) or not value.strip():
            findings.append(f"[{header}] Codex request_user_input question must include non-empty {field!r}")

    if "multiSelect" in question:
        findings.append(f"[{header}] Codex request_user_input question must not include legacy-only 'multiSelect'")

    options = question.get("options")
    if not isinstance(options, list):
        findings.append(f"[{header}] Codex request_user_input question must include an options list")
        return findings
    if not 2 <= len(options) <= 3:
        findings.append(f"[{header}] Codex request_user_input question must include 2-3 options")
    for pos, opt in enumerate(options):
        if not isinstance(opt, dict):
            findings.append(f"[{header}] option {pos + 1} must be an object")
            continue
        for field in ("label", "description"):
            value = opt.get(field)
            if not isinstance(value, str) or not value.strip():
                findings.append(f"[{header}] option {pos + 1} must include non-empty {field!r}")
    return findings


def evaluate(payload: dict) -> tuple[int, str]:
    """Pure decision function. Returns (exit_code, reason). Logs on non-compliance."""
    if not isinstance(payload, dict):
        return 0, "non-dict payload — allow (fail-open)"
    if not _is_question_tool(payload.get("tool_name")):
        return 0, "not a native question tool — allow"
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
        block_findings.extend(codex_schema_findings(idx, question))
        for severity, message in question_findings(idx, question):
            (block_findings if severity == "block" else advisory_findings).append(message)

    if not block_findings and not advisory_findings:
        return 0, "ok: every question has canonical native question-tool output criteria"

    _log_violation(payload, "; ".join(block_findings + advisory_findings))

    # Default to enforcement: a marked (Recommended) option with non-canonical output criteria
    # is the exact contract violation — block by default.
    if block_findings:
        return 2, f"Codex request_user_input recommendation/confidence contract: {'; '.join(block_findings)}"
    # Soft findings (no recommendation marked — possibly a symmetric question; or not-first):
    # advisory by default, blocking only under strict mode.
    if _strict():
        return 2, f"Codex request_user_input recommendation/confidence contract (strict): {'; '.join(advisory_findings)}"
    return 0, f"ADVISORY (Codex request_user_input recommendation/confidence): {'; '.join(advisory_findings)}"


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
