#!/usr/bin/env python3
"""
post_cursor_agent_author_gate_miss_detector.py — Retroactive Author-Gate miss audit.

Hooks post_cursor_agent_response. Scans the response for signals that a genuine
Author-Gate decision point was reached but NO capture marker was emitted —
i.e. Cursor Agent made an ambiguous decision without surfacing it to the user.

Signals (any one is a candidate; count must exceed threshold to flag):
    - multiple `edit`/`write_to_file` calls to different files (>=2 distinct paths)
    - explicit decision-class keywords in prose ("refactor", "delete", "archive",
      "bare except", "subprocess", "cross-layer", "blast radius")
    - structural-reasoning SR_PLAN markers without SR_APPROVAL / DECISION_CAPTURED
    - plan files created/modified under .cursor/plans/
    - prose options menus (bold **Option A/B/C**, "Recommended Next Phase" + sibling)
      without any DECISION_CAPTURED / AUTHOR_GATE_PACKET anti-signal

Anti-signals (presence of any = NOT a miss):
    - DECISION_CAPTURED: marker line
    - AUTHOR_GATE_PACKET: block (HITL_PACKET: legacy alias also accepted)
    - ask_user_question tool call
    - Trivial-tier markers ("T0", "T1", "trivial", "single-file")
    - Explicit user directive phrases ("user said", "as requested")

Output: artifacts/cursor/author_gate_misses.jsonl  (append-only)
  Each row: {
    timestamp, cascade_id, miss_score, signals: [...], anti_signals: [...],
    files_edited: [...], keywords_hit: [...], response_excerpt: first 500 chars
  }

Fail policy: OPEN. This is AUDIT ONLY — never blocks. Windsurf hook reads exit 0.

CONSTITUTIONAL
    - Specific exceptions (json.JSONDecodeError, OSError)
    - UTF-8 I/O
    - Bounded: response length capped at 1MB before analysis
    - No subprocess, no shell
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MISS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "author_gate_misses.jsonl"
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB — fail-safe cap

# Positive signals — each adds weight toward "miss"
_DECISION_KEYWORDS = (
    "refactor",
    "refactoring",
    "delete",
    "deletion",
    "archive",
    "archived",
    "bare except",
    "except exception",
    "subprocess",
    "shell=true",
    "cross-layer",
    "blast radius",
    "rename file",
    "move file",
    "new dependency",
    "add dependency",
    "breaking change",
    "migration",
)

_FILE_EDIT_PATTERNS = (
    r"^\s*(?:edit|write_to_file|multi_edit)\s*\(",
    r"<invoke name=\"(?:edit|write_to_file|multi_edit)\">",
    r"file_path[=:]\s*[\"'](?P<p1>[^\"']+\.py)[\"']",
    r"TargetFile[=:]\s*[\"'](?P<p2>[^\"']+\.py)[\"']",
)

# Anti-signals — presence of a fully-formed marker zeros the miss score.
# An ``ask_user_question`` invocation alone is NOT proof of compliance — the
# packet must also carry the AG-10 header and gold-star convention from
# author-gate-enforcement.md, otherwise it is a shape violation.
_CAPTURE_MARKERS = (
    re.compile(r"^DECISION_CAPTURED:\s*type=", re.MULTILINE),
    re.compile(r"^AUTHOR_GATE_PACKET:\s*\{", re.MULTILINE),
    re.compile(r"^HITL_PACKET:\s*\{", re.MULTILINE),
)
_ASK_INVOKE_RE = re.compile(r"<invoke\s+name=\"ask_user_question\">")
_AG10_HEADER_RE = re.compile(
    r"AUTHOR-GATE\s+DECISION\s+[—\-:]\s*\w+", re.IGNORECASE
)
_AG10_GOLD_STAR_RE = re.compile(r"⭐\s*Recommended\s*[:—\-]")
_TRIVIAL_TIER_HINTS = re.compile(
    r"\b(?:T0\b|T1\b|trivial\b|single-file\b|single file\b|typo\b|formatting\b)",
    re.IGNORECASE,
)
_USER_DIRECTIVE = re.compile(
    r"\b(?:user (?:said|asked|directed|requested)|as (?:requested|instructed|directed))\b",
    re.IGNORECASE,
)

# Prose-options-menu signal — detects bold/labelled option menus that bypass
# the Author-Gate pipeline.  Fires when ≥2 of these patterns appear in the
# response AND no completion marker (DECISION_CAPTURED / *_PACKET) is present.
# Weight: +3 (single-signal is enough to exceed threshold=2).
_PROSE_OPTIONS_PATTERNS = (
    re.compile(r"\*\*Option\s+[A-D\d]\b", re.IGNORECASE),
    re.compile(r"^#+\s*Option\s+[A-D\d]\s*[\u2014\-:]", re.MULTILINE | re.IGNORECASE),
    re.compile(r"\bOption\s+[A-D]\s*[\u2014\-\u2013]\s+\w", re.IGNORECASE),
    re.compile(r"\bOption\s+[A-D]\s*\(", re.IGNORECASE),
    re.compile(r"^\*\*[A-D]\.\s+\w", re.MULTILINE | re.IGNORECASE),
    re.compile(r"Recommended\s+Next\s+(?:Phase|Step|Wave|Action)\b", re.IGNORECASE),
)

# Threshold: miss_score >= this counts as a suspected miss.
# Lowered from 3 to 2 (2026-04-28) so a non-AG-10 decision question alone
# (which scores 2 from keywords) is sufficient to log a violation.
MISS_SCORE_THRESHOLD = 2


# --------------------------------------------------------------------- #


def _extract_edited_files(text: str) -> list[str]:
    """Pull distinct file paths that appear to have been edited in this response."""
    paths: set[str] = set()
    # file_path="..." and TargetFile="..." patterns
    for m in re.finditer(
        r'(?:file_path|TargetFile)\s*[=:]\s*["\']([^"\']+\.(?:py|md|js|yaml|yml|json|ts|tsx))["\']',
        text,
    ):
        paths.add(m.group(1))
    return sorted(paths)


def _has_capture_marker(text: str) -> list[str]:
    hits: list[str] = []
    for pat in _CAPTURE_MARKERS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


def _has_author_gate_completion_marker(text: str) -> bool:
    """Return True when any durable Author-Gate completion anti-signal is present.

    Covers:
      - DECISION_CAPTURED: marker (decision was logged to ledger)
      - AUTHOR_GATE_PACKET: block (canonical emitter was invoked)
      - HITL_PACKET: legacy alias
      - ask_user_question WITH AG-10 compliant shape (header + gold-star)
    """
    if _has_capture_marker(text):
        return True
    if _ASK_INVOKE_RE.search(text):
        if _AG10_HEADER_RE.search(text) and _AG10_GOLD_STAR_RE.search(text):
            return True
    return False


def _has_prose_options_menu(text: str) -> bool:
    """Return True when ≥2 prose-option-menu occurrences are found in the response.

    A prose options menu is a set of bold/labelled Markdown options presented
    outside the ask_user_question pipeline — e.g. ``**Option A — Continue G2**``.

    Counts the total number of distinct label matches across ALL patterns (using
    findall on each pattern and summing), so that two occurrences of the same
    pattern (e.g. "Option A (...)" and "Option B (...)") both contribute to the
    required minimum of 2.  Avoids false-positives on single incidental references.
    """
    total_hits = 0
    for pat in _PROSE_OPTIONS_PATTERNS:
        total_hits += len(pat.findall(text))
        if total_hits >= 2:
            return True
    return False


def _decision_keywords_hit(text: str) -> list[str]:
    lower = text.lower()
    return [kw for kw in _DECISION_KEYWORDS if kw in lower]


def _compute_miss_score(text: str) -> tuple[int, dict[str, Any]]:
    """Return (score, report). Higher score = more likely a miss."""
    score = 0
    positive_signals: list[str] = []

    # Signal 1: multi-file edits
    files = _extract_edited_files(text)
    if len(files) >= 2:
        score += 2
        positive_signals.append(f"multi_file_edit:{len(files)}")

    # Signal 2: decision keywords
    kws = _decision_keywords_hit(text)
    if len(kws) >= 2:
        score += 2
        positive_signals.append(f"keywords:{len(kws)}")
    elif len(kws) == 1:
        score += 1
        positive_signals.append(f"keyword:{kws[0]}")

    # Signal 3: plan file creation
    plan_hits = re.findall(r".cursor[/\\]plans[/\\][^\s\"']+\.md", text)
    if plan_hits:
        score += 1
        positive_signals.append("plan_file_touched")

    # Signal 4: structural reasoning without approval marker
    if "SR_PLAN" in text or "SR_EXECUTE" in text:
        if "SR_APPROVAL: APPROVED" not in text:
            score += 1
            positive_signals.append("sr_plan_without_approval")

    # Signal 5: prose options menu without any Author-Gate completion marker.
    # Weight +3 — a single hit exceeds MISS_SCORE_THRESHOLD (2) alone.
    # Check anti-signal first so we never double-penalise a correct pipeline.
    if _has_prose_options_menu(text) and not _has_author_gate_completion_marker(text):
        score += 3
        positive_signals.append("prose_options_menu")

    # Anti-signals — capture markers (DECISION_CAPTURED / AUTHOR_GATE_PACKET /
    # HITL_PACKET) prove a refactor-class decision was logged, so clear score.
    # Plan author-gate-ssot-consolidation-b7c3e1 W3.P3.3: the packet IS the
    # canonical SSOT — its presence alone clears the miss. The prior code
    # already cleared on packet presence, but explicitly reaffirm here so
    # the contract is unambiguous.
    capture_hits = _has_capture_marker(text)
    if capture_hits:
        return 0, {
            "positive_signals": positive_signals,
            "anti_signal": "capture_marker_present",
            "capture_marker_patterns": capture_hits,
        }

    # ask_user_question without ANY packet → handled by the dedicated
    # post_cursor_agent_ask_user_question_packet_audit hook (plan W4.P4.1) which
    # owns severity ladder for the vacuum case. Here we still flag shape
    # issues for triage, but as a conditional anti-signal not a hard "miss".
    has_ask = bool(_ASK_INVOKE_RE.search(text))
    if has_ask:
        has_header = bool(_AG10_HEADER_RE.search(text))
        has_star = bool(_AG10_GOLD_STAR_RE.search(text))
        if has_header and has_star:
            return 0, {
                "positive_signals": positive_signals,
                "anti_signal": "ag10_compliant_ask_user_question",
            }
        score += 2
        positive_signals.append(
            "ask_user_question_without_ag10_shape:"
            f"header={has_header},star={has_star}"
        )

    if _TRIVIAL_TIER_HINTS.search(text):
        # reduce by 2 but don't zero out — trivial-tier could still miss
        score = max(0, score - 2)
        positive_signals.append("trivial_hint_detected")

    if _USER_DIRECTIVE.search(text):
        score = max(0, score - 1)
        positive_signals.append("user_directive_detected")

    return score, {
        "positive_signals": positive_signals,
        "keywords_hit": kws,
        "files_edited": files,
    }


def _append_miss_record(record: dict) -> None:
    try:
        MISS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with MISS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:  # guardian: allow-silent-swallow -- miss audit log: non-fatal, fail-open
        pass


def main() -> int:
    try:
        raw = sys.stdin.read(MAX_RESPONSE_BYTES + 1)
    except OSError:
        return 0
    if not raw.strip():
        return 0
    if len(raw) > MAX_RESPONSE_BYTES:
        raw = raw[:MAX_RESPONSE_BYTES]

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # Sometimes hooks pass raw text; treat as-is
        payload = {"response_text": raw}

    if not isinstance(payload, dict):
        return 0

    # Extract response text from various payload shapes
    text = (
        payload.get("response_text")
        or payload.get("text")
        or payload.get("content")
        or (payload.get("tool_info") or {}).get("response_text")
        or ""
    )
    if not text or not isinstance(text, str):
        return 0

    score, report = _compute_miss_score(text)
    if score < MISS_SCORE_THRESHOLD:
        return 0

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cascade_id": payload.get("cascade_id") or payload.get("session_id"),
        "miss_score": score,
        "threshold": MISS_SCORE_THRESHOLD,
        "signals": report.get("positive_signals", []),
        "keywords_hit": report.get("keywords_hit", []),
        "files_edited": report.get("files_edited", []),
        "response_excerpt": text[:500],
    }
    _append_miss_record(record)

    # Advisory stderr only — never blocks
    print(
        f"[author_gate_miss_detector] ADVISORY miss_score={score} "
        f"signals={report.get('positive_signals', [])}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
