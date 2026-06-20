#!/usr/bin/env python3
"""post_ask_user_question_capture.py — PostToolUse capture for the native AskUserQuestion tool.

Plan: askq-confidence-meta-learning-loop-c4e7a1 (W1.2). Companion thin hook:
``.codex/hooks/after_ask_user_question.py`` (registered under ``PostToolUse`` matcher
``AskUserQuestion``).

Why this exists
---------------
The ``ask_user_question_decisions`` ledger + ``AskUserQuestionConsulter`` already exist, but the
native tool never wrote to them: the only live hook was the PreToolUse *shape* gate, and
``hooks.json`` had no ``PostToolUse`` matcher for ``AskUserQuestion`` — so the user's actual
selection (the core learning signal) was never captured. This hook closes the WRITE+SELECTION
seam: a single PostToolUse event carries both ``tool_input`` (options + confidence) and
``tool_response`` (the user's choice), so one atomic capture needs no PreToolUse correlation.

Selection-shape robustness
---------------------------
Claude Code's ``tool_input`` shape for AskUserQuestion is reliable (questions[] → options[] with
label/description; the recommended option's label ends ``(Recommended)`` and its description
carries ``[confidence=0.NN]`` — guaranteed by the PreToolUse gate). The ``tool_response``
selected-option representation is NOT authoritatively documented, so selection extraction is
deliberately defensive: it collects every plausible "selected label / index" shape and matches
back to an option **by label** (resilient to index/label/header-map variants). On the very first
real call, the raw payload is also dumped to a debug JSONL so the exact shape can be confirmed and
the parser tightened if needed.

Contract: never blocks (PostToolUse), fail-soft on every error — a capture failure must never
wedge a turn. Bypass: ``ASKQ_CAPTURE_BYPASS=1``.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_DEBUG_LOG = _REPO_ROOT / "artifacts" / "governance" / "auq_capture_debug.jsonl"

# `[confidence=0.NN]`, also inside `[RECOMMENDED ⭐ confidence=0.NN]`.
_CONFIDENCE_RE = re.compile(r"confidence\s*=\s*([01](?:\.\d+)?)", re.IGNORECASE)
_RECOMMENDED_RE = re.compile(r"\(\s*recommended\s*\)\s*$", re.IGNORECASE)
# Word-band fallback (the gate tolerates legacy high/medium/low).
_BAND_RE = re.compile(r"\b(high|medium|low)\b", re.IGNORECASE)
_BAND_SCORE = {"high": 0.9, "medium": 0.7, "low": 0.5}


def _bypass() -> bool:
    return os.environ.get("ASKQ_CAPTURE_BYPASS", "").strip().lower() in ("1", "true", "yes")


def _norm_label(label: str) -> str:
    """Normalize an option label for matching: strip the (Recommended) suffix, lower, collapse ws."""
    s = _RECOMMENDED_RE.sub("", str(label or "")).strip().lower()
    return re.sub(r"\s+", " ", s)


def parse_confidence(description: str) -> tuple[float | None, str]:
    """Return (confidence_score, confidence_source) parsed from an option description.

    ``explicit`` when a numeric ``confidence=0.NN`` is present; ``band`` for a high/medium/low
    word-band; ``heuristic_default`` when neither is found.
    """
    text = str(description or "")
    m = _CONFIDENCE_RE.search(text)
    if m:
        try:
            return float(m.group(1)), "explicit"
        except ValueError:
            pass
    b = _BAND_RE.search(text)
    if b:
        return _BAND_SCORE[b.group(1).lower()], "band"
    return None, "heuristic_default"


def recommended_index(options: list[dict]) -> int | None:
    """Index of the option whose label ends with ``(Recommended)`` (first wins), else None."""
    for i, opt in enumerate(options):
        if isinstance(opt, dict) and _RECOMMENDED_RE.search(str(opt.get("label", ""))):
            return i
    return None


def _context_from_question(question: dict, fallback_idx: int) -> str:
    """Derive a stable telemetry context slug from a question's header (or question text)."""
    raw = str(question.get("header") or question.get("question") or f"q{fallback_idx}")
    slug = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower()).strip("-")
    return (slug or f"q{fallback_idx}")[:64]


def _collect_selected_strings(node: Any, out: list[str]) -> None:
    """Recursively collect plausible 'selected label/answer' strings from any tool_response shape.

    Defensive by design: AskUserQuestion's response shape is not authoritatively documented, so we
    harvest string values under the common selection keys, plus bare strings in lists, and let
    label-matching disambiguate.
    """
    _SELECT_KEYS = (
        "selected_label", "selected", "label", "answer", "answers",
        "value", "choice", "choices", "option", "selected_option", "response",
    )
    if isinstance(node, str):
        if node.strip():
            out.append(node)
    elif isinstance(node, list):
        for item in node:
            _collect_selected_strings(item, out)
    elif isinstance(node, dict):
        # Prefer explicit selection keys; if none present, recurse into all values
        # (covers header->label maps).
        hit = False
        for key in _SELECT_KEYS:
            if key in node:
                hit = True
                _collect_selected_strings(node[key], out)
        if not hit:
            for v in node.values():
                _collect_selected_strings(v, out)


def _collect_indices_by_question(tool_response: Any) -> dict[int, int]:
    """Best-effort map question_index -> selected numeric index, if the payload exposes ints."""
    result: dict[int, int] = {}
    answers = None
    if isinstance(tool_response, dict):
        for key in ("answers", "responses", "results"):
            if isinstance(tool_response.get(key), list):
                answers = tool_response[key]
                break
    if isinstance(answers, list):
        for i, ans in enumerate(answers):
            if not isinstance(ans, dict):
                continue
            qidx = ans.get("question_index")
            qidx = qidx if isinstance(qidx, int) else i
            for ik in ("selected_index", "selected_option_index", "index", "option_index"):
                if isinstance(ans.get(ik), int):
                    result[qidx] = ans[ik]
                    break
    return result


def _answers_list(tool_response: Any) -> list | None:
    """Return the positional per-question answer list if the payload exposes one, else None."""
    if isinstance(tool_response, dict):
        for key in ("answers", "responses", "results"):
            v = tool_response.get(key)
            if isinstance(v, list):
                return v
    if isinstance(tool_response, list):
        return tool_response
    return None


def selected_strings_for_question(
    tool_response: Any,
    question_idx: int,
    question: dict,
    total_questions: int,
) -> list[str]:
    """Selected label/answer strings scoped to ONE question (avoids cross-question collisions).

    Multi-question AskUserQuestion calls may reuse option labels (two yes/no prompts). A global
    pool would let q0 match q1's choice, corrupting the acceptance/override signal. So scope by:
    (1) positional answers list → entry at this question's index; (2) header/question-keyed map →
    this question's key; (3) only when there is a single question, fall back to the whole response.
    """
    out: list[str] = []
    answers = _answers_list(tool_response)
    if answers is not None:
        if 0 <= question_idx < len(answers):
            _collect_selected_strings(answers[question_idx], out)
        return out
    if isinstance(tool_response, dict):
        for key in (question.get("header"), question.get("question")):
            if isinstance(key, str) and key in tool_response:
                _collect_selected_strings(tool_response[key], out)
        if out:
            return out
        if total_questions == 1:  # no sibling questions → no collision risk
            _collect_selected_strings(tool_response, out)
        return out
    return out


def selected_index_for_question(
    question_idx: int,
    options: list[dict],
    selected_strings: list[str],
    indices_by_question: dict[int, int],
) -> int | None:
    """Resolve the chosen option index for one question.

    Priority: (1) label match against harvested selected strings (most robust); (2) an explicit
    numeric index keyed by question position; else None (unknown — e.g. free-text 'Other').
    """
    norm_selected = {_norm_label(s) for s in selected_strings}
    for i, opt in enumerate(options):
        if isinstance(opt, dict) and _norm_label(opt.get("label", "")) in norm_selected:
            return i
    idx = indices_by_question.get(question_idx)
    if isinstance(idx, int) and 0 <= idx < len(options):
        return idx
    return None


def build_decision_rows(tool_input: dict, tool_response: Any) -> list[dict]:
    """Build one capture row per question (packet + selected_index) ready for write_decision."""
    questions = tool_input.get("questions") if isinstance(tool_input, dict) else None
    if not isinstance(questions, list) or not questions:
        return []

    total_questions = len(questions)
    indices_by_question = _collect_indices_by_question(tool_response)

    rows: list[dict] = []
    now = datetime.now(timezone.utc).isoformat()
    for q_idx, question in enumerate(questions):
        if not isinstance(question, dict):
            continue
        options = [o for o in (question.get("options") or []) if isinstance(o, dict)]
        if not options:
            continue
        rec_idx = recommended_index(options)
        conf_score, conf_source = (None, "heuristic_default")
        if rec_idx is not None:
            conf_score, conf_source = parse_confidence(options[rec_idx].get("description", ""))
        sel_strings = selected_strings_for_question(tool_response, q_idx, question, total_questions)
        sel_idx = selected_index_for_question(q_idx, options, sel_strings, indices_by_question)
        question_text = str(question.get("question") or question.get("header") or "")
        packet: dict[str, Any] = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "timestamp": now,
            "decision_type": "enriched_choice",
            "context": _context_from_question(question, q_idx),
            "question": question_text,
            "option_count": len(options),
            "recommended_index": rec_idx,
            "confidence_source": conf_source,
            "invariants": ["confidence_prefix", "pros_cons_segment", "star_marker", "recommended_label"],
            "options": [
                {"label": str(o.get("label", "")), "description": str(o.get("description", ""))}
                for o in options
            ],
            "recommended_label": (
                str(options[rec_idx].get("label", "")) if rec_idx is not None else None
            ),
            "selected_label": (
                str(options[sel_idx].get("label", "")) if sel_idx is not None else None
            ),
            "selected_index": sel_idx,
            "matched_recommendation": (
                bool(sel_idx == rec_idx) if sel_idx is not None and rec_idx is not None else None
            ),
        }
        if conf_score is not None:
            packet["confidence_score"] = conf_score
        rows.append({"packet": packet, "selected_index": sel_idx})
    return rows


def _dump_debug(payload: dict, decision_ids: list[str]) -> None:
    """Append the raw payload + outcome to a debug JSONL (self-probe — confirms the live shape)."""
    try:
        _DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "decision_ids": decision_ids,
            "tool_response": payload.get("tool_response"),
        }
        with _DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    except OSError:
        # guardian: allow-broad-exception -- debug dump is best-effort; never wedge the hook
        pass


def capture(payload: dict) -> list[str]:
    """Capture one AskUserQuestion decision per question. Returns written decision_ids."""
    if not isinstance(payload, dict) or payload.get("tool_name") != "AskUserQuestion":
        return []
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return []
    rows = build_decision_rows(tool_input, payload.get("tool_response"))
    if not rows:
        return []

    from tools.ledgers.ask_user_question_ledger import write_decision

    decision_ids: list[str] = []
    for row in rows:
        try:
            decision_ids.append(write_decision(row["packet"], selected_index=row["selected_index"]))
        except Exception as exc:  # guardian: allow-broad-exception -- ledger write fail-soft
            sys.stderr.write(f"post_ask_user_question_capture: ledger write failed ({exc})\n")
    _dump_debug(payload, decision_ids)
    return decision_ids


def main() -> int:
    try:
        if _bypass():
            return 0
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        ids = capture(payload if isinstance(payload, dict) else {})
        if ids:
            sys.stderr.write(
                f"[askq-capture] recorded {len(ids)} ask_user_question decision(s): "
                f"{', '.join(ids)}\n"
            )
        return 0
    except Exception as exc:  # guardian: allow-broad-exception -- PostToolUse fail-soft contract
        sys.stderr.write(f"post_ask_user_question_capture error (ignored): {exc}\n")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
