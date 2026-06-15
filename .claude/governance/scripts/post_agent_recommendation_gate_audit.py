"""post_agent_recommendation_gate_audit.py — trigger-side audit for the AskUserQuestion contract.

The PreToolUse gate (`pre_ask_user_question_recommendation_gate.py`) enforces the SHAPE of an
AskUserQuestion (recommended option + confidence) and blocks. This audit covers the TRIGGER:
a response that surfaces a decision/options menu in PROSE — or a "do you want X or Y?" closer —
without ever calling AskUserQuestion. That is exactly the `no-prose-options-menus` anti-pattern
(CLAUDE.md Author-Gate): a decision the user should have been asked, rendered as prose instead.

Heuristic and ADVISORY by design: "a decision was needed" cannot be inferred from text with
enough precision to block safely, so this NEVER blocks — it logs to
``artifacts/governance/recommendation_gate_violations.jsonl`` for review. Patterns are
conservative (clear option menus / lettered "(a) … or (b)" / explicit decision questions) and
an AskUserQuestion-was-used anti-signal suppresses the flag.

Bypass: RECOMMENDATION_GATE_BYPASS=1
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Sibling import of the SSOT payload extractor (check_post_agent_payload.py forbids a
# hand-rolled parser). Ensure this script's own dir is importable as a subprocess and in tests.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _post_agent_payload import extract_response_text  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
VIOLATIONS_FILE = REPO_ROOT / "artifacts" / "governance" / "recommendation_gate_violations.jsonl"

# Anti-signal: an AskUserQuestion was actually posed (its native markers appear in the turn) →
# compliant, suppress. The confidence/recommended markers are the strong signal; the tool name
# is a softer one. Over-suppression is acceptable for an advisory detector (favor low FP).
_ASK_USED_RE = re.compile(
    r"(?i)\[confidence=0\.\d|\[RECOMMENDED|\bask_user_question\b|AskUserQuestion"
)

# Conservative prose decision / options-menu patterns.
_PROSE_DECISION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?im)^\s*\*\*\s*option\s+[a-d0-9]\b"), "bold_option_menu"),
    (re.compile(r"(?im)^\s*#{1,6}\s*option\s+[a-d]\b"), "option_header_menu"),
    (re.compile(r"(?is)\(\s*a\s*\).{0,200}?\bor\b.{0,80}?\(\s*b\s*\)"), "lettered_or_menu"),
    (
        re.compile(
            r"(?i)\b(?:do you want|would you (?:like|prefer)|should i|want me to)\b"
            r"[^?\n]{0,200}\bor\b[^?\n]{0,200}\?"
        ),
        "prose_decision_question",
    ),
)

_REMEDY = (
    "A decision was surfaced in prose without AskUserQuestion. Fire AskUserQuestion with "
    "the recommended option first and labeled '(Recommended)'; descriptions must begin with "
    "[RECOMMENDED ⭐ confidence=0.NN] for the recommendation and [confidence=0.NN] for every "
    "other option, with Pros: and Cons: text. Or decide-and-proceed — never a prose options menu. "
    "SSOT: no-prose-options-menus memory; CLAUDE.md Author-Gate."
)


def _bypass() -> bool:
    return os.environ.get("RECOMMENDATION_GATE_BYPASS", "").strip().lower() in ("1", "true", "yes")


def _append(record: dict) -> None:
    try:
        VIOLATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with VIOLATIONS_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def detect(text: str) -> list[dict]:
    """Return advisory violation records (empty if compliant or no decision-in-prose)."""
    if _ASK_USED_RE.search(text):
        return []  # an AskUserQuestion was posed (markers present) — compliant
    hits = [name for rx, name in _PROSE_DECISION_PATTERNS if rx.search(text)]
    if not hits:
        return []
    return [
        {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "kind": "recommendation_not_gated",
            "patterns": hits,
            "remedy": _REMEDY,
            "rule_ref": "CLAUDE.md Author-Gate / no-prose-options-menus",
        }
    ]


def main() -> int:
    try:
        if _bypass():
            return 0
        text = extract_response_text(sys.stdin.read())
        if not text.strip():
            return 0
        for record in detect(text):
            _append(record)
            print(
                f"[recommendation-gate] {record['kind']}: patterns={record['patterns']} — "
                "use AskUserQuestion with confidence levels, not a prose menu.",
                file=sys.stderr,
            )
        return 0
    except Exception:  # guardian: allow-broad-exception -- hook fail-soft contract
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
