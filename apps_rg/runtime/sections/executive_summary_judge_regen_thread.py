"""Judge regen thread compaction — preserve rubric/candidate/facts; drop unbounded assistant JSON stacks."""

from __future__ import annotations

import json
import re
from typing import Any

_JSON_OBJECT_RE = re.compile(r"^\s*\{", re.MULTILINE)
_ASSISTANT_ROLE = "assistant"


def _looks_like_full_model_json(content: str) -> bool:
    text = str(content or "").strip()
    if not text or not _JSON_OBJECT_RE.match(text):
        return False
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return False
    return isinstance(obj, dict) and (
        "resume_display_text" in obj or "claim_ledger" in obj or "selected_fact_plan" in obj
    )


def compact_judge_regen_messages(
    messages: list[dict[str, str]],
    *,
    preserve_tail_turns: int = 2,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Drop stacked full assistant JSON turns; keep frozen prefix + latest tail."""
    receipt: dict[str, Any] = {
        "schema": "executive_summary_judge_regen_thread_compact_v1",
        "input_turns": len(messages),
        "removed_assistant_json_turns": 0,
        "preserved_system": False,
        "preserved_initial_user": False,
    }
    if len(messages) <= 3:
        receipt["compacted"] = False
        return list(messages), receipt

    prefix: list[dict[str, str]] = []
    middle: list[dict[str, str]] = []
    tail: list[dict[str, str]] = []

    idx = 0
    while idx < len(messages) and messages[idx].get("role") in ("system", "user"):
        prefix.append(dict(messages[idx]))
        idx += 1
    receipt["preserved_system"] = any(m.get("role") == "system" for m in prefix)
    receipt["preserved_initial_user"] = any(m.get("role") == "user" for m in prefix)

    remainder = [dict(m) for m in messages[idx:]]
    if len(remainder) <= preserve_tail_turns:
        receipt["compacted"] = False
        return list(messages), receipt

    tail = remainder[-preserve_tail_turns:]
    middle = remainder[:-preserve_tail_turns]

    kept_middle: list[dict[str, str]] = []
    removed = 0
    for msg in middle:
        if msg.get("role") == _ASSISTANT_ROLE and _looks_like_full_model_json(str(msg.get("content") or "")):
            removed += 1
            continue
        kept_middle.append(msg)

    out = [*prefix, *kept_middle, *tail]
    receipt["removed_assistant_json_turns"] = removed
    receipt["output_turns"] = len(out)
    receipt["compacted"] = removed > 0
    return out, receipt


def assert_judge_regen_thread_invariants(
    before: list[dict[str, str]],
    after: list[dict[str, str]],
    *,
    required_substrings: tuple[str, ...] = (),
) -> list[str]:
    """Return violations when compaction dropped required judge-thread material."""
    violations: list[str] = []
    joined_before = "\n".join(str(m.get("content") or "") for m in before)
    joined_after = "\n".join(str(m.get("content") or "") for m in after)
    for needle in required_substrings:
        if needle and needle in joined_before and needle not in joined_after:
            violations.append(f"missing_required_substring:{needle[:48]}")
    if any(m.get("role") == "system" for m in before) and not any(m.get("role") == "system" for m in after):
        violations.append("missing_system_message")
    return violations


__all__ = [
    "assert_judge_regen_thread_invariants",
    "compact_judge_regen_messages",
]
