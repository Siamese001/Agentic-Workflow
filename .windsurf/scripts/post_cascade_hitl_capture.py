#!/usr/bin/env python3
"""
post_cascade_hitl_capture.py — Windsurf post_cascade_response HITL capture hook.

Reads the cascade response payload from stdin.
Detects surfaced HITL decision packets via the mandatory PACKET HEADER format
defined in hitl-enforcement.md and writes a structured record to the local
SQLite decision ledger.

Detection heuristic:
    PACKET HEADER present in response text:
        Recommended: <option>
        Why it wins: <...>
        Candidates evaluated: N | ...

Behavior (ADVISORY — always exits 0):
    - False negatives are acceptable; false positives are not.
    - DB and schema are created on first successful capture.
    - FTS5 content table is kept in sync on every insert.
    - No user data is sent anywhere — purely local.

Fail policy: OPEN — any error exits 0 silently.
Zero hardcoded paths — REPO_ROOT resolved from __file__.
"""

import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

FAIL_POLICY = "open"

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_DIR = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions"
DB_PATH = DB_DIR / "refactor_decision_ledger.sqlite"
_LOG_PATH = DB_DIR / "hitl_capture.log"


def _debug_log(msg: str) -> None:
    """Append a timestamped line to the capture log (diagnostic only)."""
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"{ts}  {msg}\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

_PACKET_HEADER_RE = re.compile(
    r"Recommended:\s*(.+?)\n"
    r".*?Why it wins:\s*(.+?)\n"
    r".*?Candidates evaluated:\s*(\d+)",
    re.DOTALL | re.MULTILINE,
)

# Structured capture marker emitted by Cascade post-HITL:
# DECISION_CAPTURED: type=<type>, repo_area=<path>, selected=<label>, outcome=<status>
_CAPTURE_MARKER_RE = re.compile(
    r"DECISION_CAPTURED:\s*type=(?P<dtype>[\w_]+),\s*"
    r"repo_area=(?P<area>[^,]+),\s*"
    r"selected=(?P<selected>[^,]+),\s*"
    r"outcome=(?P<outcome>\w+)",
    re.MULTILINE,
)

_DECISION_TYPE_KEYWORDS: list[tuple[str, str]] = [
    ("architecture", "architecture_choice"),
    ("architectural", "architecture_choice"),
    ("refactor", "refactor_scope"),
    ("anti-pattern", "anti_pattern"),
    ("antipattern", "anti_pattern"),
    ("dependency", "dependency_addition"),
    ("test strategy", "test_strategy"),
    ("test failure", "test_strategy"),
    ("delet", "deletion_strategy"),
    ("archiv", "deletion_strategy"),
    ("error handling", "error_handling"),
    ("exception handling", "error_handling"),
]

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_DDL = """\
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS decisions (
    decision_id           TEXT PRIMARY KEY,
    created_at            TEXT NOT NULL,
    branch                TEXT,
    commit_sha            TEXT,
    task_id               TEXT,
    decision_type         TEXT NOT NULL DEFAULT 'unknown',
    request_summary       TEXT,
    normalized_intent     TEXT,
    user_goal             TEXT,
    constraints_json      TEXT,
    risk_profile_json     TEXT,
    blast_radius_estimate TEXT,
    options_json          TEXT,
    recommended_option_id TEXT,
    selected_option_id    TEXT,
    selection_rationale   TEXT,
    status                TEXT NOT NULL DEFAULT 'surfaced'
);

CREATE TABLE IF NOT EXISTS decision_scope (
    scope_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT NOT NULL REFERENCES decisions(decision_id),
    file_path   TEXT,
    symbol_name TEXT,
    symbol_kind TEXT,
    layer       TEXT,
    repo_area   TEXT,
    tags        TEXT
);

CREATE TABLE IF NOT EXISTS decision_outcomes (
    outcome_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id           TEXT NOT NULL REFERENCES decisions(decision_id),
    execution_completed   INTEGER DEFAULT 0,
    tests_passed          INTEGER DEFAULT 0,
    regression_found      INTEGER DEFAULT 0,
    rollback_required     INTEGER DEFAULT 0,
    followup_decision_id  TEXT,
    promote_to_pattern    INTEGER DEFAULT 0,
    outcome_notes         TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
    decision_id       UNINDEXED,
    normalized_intent,
    request_summary,
    user_goal,
    selection_rationale,
    content=decisions,
    content_rowid=rowid
);
"""


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def _init_db() -> Optional[sqlite3.Connection]:
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.executescript(_DDL)
        conn.commit()
        return conn
    except (sqlite3.Error, OSError):
        return None


def _get_git_info() -> tuple[str, str]:
    """Return (branch, commit_sha). Empty strings on failure."""
    branch, sha = "", ""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(REPO_ROOT),
            shell=False,
            check=False,
        )
        if r.returncode == 0:
            branch = r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(REPO_ROOT),
            shell=False,
            check=False,
        )
        if r.returncode == 0:
            sha = r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return branch, sha


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        # post_cascade_response puts response text at tool_info.response (Windsurf docs)
        tool_info = payload.get("tool_info")
        if isinstance(tool_info, dict):
            for key in ("response", "text", "content", "message", "cascade_response"):
                val = tool_info.get(key)
                if isinstance(val, str) and val.strip():
                    return val
        # Fallback: top-level keys (plain payloads, tests, other hook formats)
        for key in ("response", "text", "content", "message", "cascade_response"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val
        try:
            return json.dumps(payload)
        except (TypeError, ValueError):
            return ""
    return ""


def _infer_decision_type(text: str) -> str:
    lower = text.lower()
    for keyword, dtype in _DECISION_TYPE_KEYWORDS:
        if keyword in lower:
            return dtype
    return "unknown"


def _extract_options(text: str) -> list[str]:
    """Heuristically extract option labels from HITL packet text."""
    options: list[str] = []
    for match in re.finditer(r"Option\s+\d+\.?\s+(.+)", text, re.MULTILINE):
        opt = match.group(1).strip()[:120]
        if opt and opt not in options:
            options.append(opt)
        if len(options) >= 6:
            break
    return options


def _make_decision_id(text: str, _ts: str) -> str:  # _ts kept for call-site compat; not in hash
    return "dec_" + hashlib.sha1(text[:200].encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Core capture
# ---------------------------------------------------------------------------


def _capture_from_marker(m: re.Match[str], text: str, conn: sqlite3.Connection) -> bool:
    """Capture a decision from a DECISION_CAPTURED structured marker."""
    dtype = m.group("dtype")
    area = m.group("area").strip()
    selected = m.group("selected").strip()[:200]
    outcome = m.group("outcome").strip()

    ts = datetime.now(timezone.utc).isoformat()
    decision_id = _make_decision_id(f"marker:{area}:{selected}", ts)

    existing = conn.execute("SELECT 1 FROM decisions WHERE decision_id = ?", (decision_id,)).fetchone()
    if existing:
        return False

    branch, sha = _get_git_info()
    status = "executed" if outcome == "executed" else "surfaced"
    context_window = text[max(0, m.start() - 300) : m.end() + 200].strip()

    conn.execute(
        """
        INSERT OR IGNORE INTO decisions
            (decision_id, created_at, branch, commit_sha, decision_type,
             request_summary, normalized_intent, recommended_option_id,
             selected_option_id, options_json, status)
        VALUES
            (:decision_id, :created_at, :branch, :commit_sha, :decision_type,
             :request_summary, :normalized_intent, :recommended_option_id,
             :selected_option_id, :options_json, :status)
        """,
        {
            "decision_id": decision_id,
            "created_at": ts,
            "branch": branch,
            "commit_sha": sha,
            "decision_type": dtype,
            "request_summary": context_window[:500],
            "normalized_intent": area[:200],
            "recommended_option_id": selected,
            "selected_option_id": selected,
            "options_json": json.dumps([selected]),
            "status": status,
        },
    )
    conn.execute(
        """INSERT INTO decisions_fts
               (decision_id, normalized_intent, request_summary, user_goal, selection_rationale)
           VALUES (?, ?, ?, '', '')""",
        (decision_id, area[:200], context_window[:500]),
    )
    conn.commit()
    return True


def detect_and_capture(text: str, conn: sqlite3.Connection) -> bool:
    """
    Detect a HITL packet in text and write a decision record.
    Returns True if a new record was inserted, False otherwise.
    Tries structured marker first, falls back to HITL packet header heuristic.
    """
    # Path 1: structured DECISION_CAPTURED marker (reliable, emitted by Cascade post-HITL)
    marker = _CAPTURE_MARKER_RE.search(text)
    if marker:
        return _capture_from_marker(marker, text, conn)

    # Path 2: heuristic HITL packet header in prose (fallback)
    m = _PACKET_HEADER_RE.search(text)
    if not m:
        return False

    recommended = m.group(1).strip()[:200]
    ts = datetime.now(timezone.utc).isoformat()
    decision_id = _make_decision_id(text, ts)

    # Dedup: same HITL packet may fire hook twice in one session
    existing = conn.execute("SELECT 1 FROM decisions WHERE decision_id = ?", (decision_id,)).fetchone()
    if existing:
        return False

    decision_type = _infer_decision_type(text)
    start = max(0, m.start() - 200)
    context_window = text[start : m.start() + 500].strip()
    request_summary = context_window[:500]
    normalized_intent = context_window[:200]
    options = _extract_options(text)
    branch, sha = _get_git_info()

    conn.execute(
        """
        INSERT OR IGNORE INTO decisions
            (decision_id, created_at, branch, commit_sha, decision_type,
             request_summary, normalized_intent, recommended_option_id,
             options_json, status)
        VALUES
            (:decision_id, :created_at, :branch, :commit_sha, :decision_type,
             :request_summary, :normalized_intent, :recommended_option_id,
             :options_json, :status)
        """,
        {
            "decision_id": decision_id,
            "created_at": ts,
            "branch": branch,
            "commit_sha": sha,
            "decision_type": decision_type,
            "request_summary": request_summary,
            "normalized_intent": normalized_intent,
            "recommended_option_id": recommended,
            "options_json": json.dumps(options),
            "status": "surfaced",
        },
    )

    conn.execute(
        """
        INSERT INTO decisions_fts
            (decision_id, normalized_intent, request_summary, user_goal, selection_rationale)
        VALUES (?, ?, ?, '', '')
        """,
        (decision_id, normalized_intent, request_summary),
    )

    conn.commit()
    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            _debug_log("stdin_empty")
            return 0

        try:
            payload: object = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw

        text = _extract_response_text(payload)
        if not text.strip():
            _debug_log("no_text_extracted")
            return 0

        marker_found = bool(_CAPTURE_MARKER_RE.search(text))
        _debug_log(f"text_len={len(text)} marker={marker_found}")

        conn = _init_db()
        if conn is None:
            _debug_log("db_init_failed")
            return 0

        try:
            captured = detect_and_capture(text, conn)
            _debug_log(f"captured={captured}")
        except sqlite3.Error:
            pass
        finally:
            conn.close()

    except (OSError, ValueError):
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
