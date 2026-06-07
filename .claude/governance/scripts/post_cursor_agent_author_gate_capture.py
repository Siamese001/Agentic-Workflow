#!/usr/bin/env python3
"""
post_cursor_agent_author_gate_capture.py — Cursor afterAgentResponse Author-Gate capture hook.

Reads the cursor agent response payload from stdin.
Detects surfaced Author-Gate decision packets via the mandatory PACKET HEADER format
defined in author-gate-enforcement.md and writes a structured record to the local
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
Zero hardcoded paths — repo_root resolved from __file__.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from author_gate_ledger_integrity import ensure_row_hash as _ensure_row_hash
except ImportError:  # pragma: no cover — integrity lib optional, capture must still work
    _ensure_row_hash = None  # type: ignore[assignment]

try:
    from author_gate_marker_validator import validate_marker as _validate_marker
    from author_gate_marker_validator import log_violation as _log_marker_violation
except ImportError:  # pragma: no cover — validator optional; capture must still work
    _validate_marker = None  # type: ignore[assignment]
    _log_marker_violation = None  # type: ignore[assignment]

fail_policy = "open"

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tools.refactor_decisions.author_gate_w1_bind import (  # noqa: E402
    merge_precedent_verdict,
    outcome_bind_tier,
)
from tools.refactor_decisions.ledger_w1_schema import ensure_w1_feedback_loop_columns  # noqa: E402
from tools.refactor_decisions.ledger_w2_schema import ensure_w2_decision_signal_columns  # noqa: E402
from tools.refactor_decisions.precedent_capture_metadata import (  # noqa: E402
    compute_precedent_capture_metadata,
)
from tools.refactor_decisions.author_gate_w2_signals import (  # noqa: E402
    replace_decision_signals_for_capture,
)
DB_DIR = repo_root / ".claude" / "state" / "refactor_decisions"
DB_PATH = DB_DIR / "refactor_decision_ledger.sqlite"
_log_path = DB_DIR / "author_gate_capture.log"
# Lowercase aliases preserved for back-compat with any external importer.
db_dir = DB_DIR
db_path = DB_PATH
# Back-compat: legacy name pre-2026-04-21 rename. One-shot migration on first write.
_legacy_log_path = DB_DIR / "hitl_capture.log"
try:
    if _legacy_log_path.exists() and not _log_path.exists():
        _legacy_log_path.rename(_log_path)
except OSError:
    # guardian: allow-silent-swallow -- one-shot log migration: non-fatal, fail-open
    pass


def _debug_log(msg: str) -> None:
    """Append a timestamped line to the capture log (diagnostic only)."""
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with _log_path.open("a", encoding="utf-8") as f:
            f.write(f"{ts}  {msg}\n")
    except OSError:  # guardian: allow-silent-swallow -- debug log write: non-fatal, fail-open
        pass


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

_packet_header_re = re.compile(
    r"Recommended:\s*(.+?)\n"
    r".*?Why it wins:\s*(.+?)\n"
    r".*?Candidates evaluated:\s*(\d+)",
    re.DOTALL | re.MULTILINE,
)

# Structured capture marker emitted by Cursor Agent post-Author-Gate:
# v1: DECISION_CAPTURED: type=<type>, repo_area=<path>, selected=<label>, outcome=<status>
# v2: ...[, confidence=0.NN, gap=0.NN, override=true|false, latency_ms=N, principle=<short>]
# v2 optional fields are parsed via a second pass against the tail of the marker line.
_capture_marker_re = re.compile(
    r"DECISION_CAPTURED:\s*type=(?P<dtype>[\w_]+),\s*"
    r"repo_area=(?P<area>[^,]+),\s*"
    r"selected=(?P<selected>[^,]+),\s*"
    r"outcome=(?P<outcome>\w+)"
    r"(?P<tail>[^\n]*)",
    re.MULTILINE,
)

# Individual field patterns for the optional v2 tail. Each is independent and
# fail-soft — missing fields leave the corresponding column NULL.
_v2_confidence_re = re.compile(r"confidence\s*=\s*(?P<v>[01](?:\.\d+)?)")
_v2_gap_re = re.compile(r"gap\s*=\s*(?P<v>[01](?:\.\d+)?)")
_v2_override_re = re.compile(r"override\s*=\s*(?P<v>true|false)", re.IGNORECASE)
_v2_latency_re = re.compile(r"latency_ms\s*=\s*(?P<v>\d+)")
_v2_principle_re = re.compile(r"principle\s*=\s*(?P<v>[^,\n]{1,80})")
_v2_precedent_re = re.compile(r"precedent\s*=\s*(?P<v>strong|suggestive|none)", re.IGNORECASE)
# W3.1 — exit_criteria=<JSON-or-text>; supports two forms:
#   exit_criteria={"tests_must_pass": ["..."], "p_count_max": 0}
#   exit_criteria=tests_pass; p_count_max:0; rollback_window_h:24
# Stored verbatim in exit_criteria_json (string column). Parser is permissive;
# downstream binders normalise. Stops at the next ", <key>=" boundary.
_v2_exit_criteria_re = re.compile(
    r"exit_criteria\s*=\s*(?P<v>(?:\{[^}]*\}|[^,\n][^,\n]*?))(?=,\s*\w+\s*=|\s*$)",
    re.MULTILINE,
)

# plan author-gate-hardening-a3b8f2 W1.3 — reason-code + calibration tail fields
_v2_reason_code_re = re.compile(
    r"reason_code\s*=\s*(?P<v>override_recommendation|insufficient_precedent|"
    r"blast_radius_too_high|principle_shift|test_strategy_change|"
    r"dependency_risk|deletion_risk|other)"
)
_v2_confidence_calibrated_re = re.compile(r"confidence_calibrated\s*=\s*(?P<v>[01](?:\.\d+)?)")
_v2_calibrator_version_re = re.compile(r"calibrator_version\s*=\s*(?P<v>[\w.\-]+)")
_v2_hotspot_rank_re = re.compile(r"adg_hotspot_rank\s*=\s*(?P<v>\d+)")
_v2_blast_hops_re = re.compile(r"blast_radius_hops\s*=\s*(?P<v>\d+)")
_v2_tier_re = re.compile(r"decision_class_tier\s*=\s*(?P<v>T[0-3])")
_v2_surfaces_re = re.compile(r"surfaces\s*=\s*(?P<v>[A-Za-z,]+)")


def _parse_v2_tail(tail: str) -> dict[str, object]:
    """Extract optional v2 calibration fields from the marker tail.

    Returns a dict with only the fields that were present and parseable.
    """
    out: dict[str, object] = {}
    m = _v2_confidence_re.search(tail)
    if m:
        try:
            out["confidence_top"] = float(m.group("v"))
        except ValueError:
            pass
    m = _v2_gap_re.search(tail)
    if m:
        try:
            out["confidence_dominance_gap"] = float(m.group("v"))
        except ValueError:
            pass
    m = _v2_override_re.search(tail)
    if m:
        out["override_vs_recommendation"] = 1 if m.group("v").lower() == "true" else 0
    m = _v2_latency_re.search(tail)
    if m:
        try:
            out["selection_latency_ms"] = int(m.group("v"))
        except ValueError:
            pass
    m = _v2_principle_re.search(tail)
    if m:
        out["principle_at_stake"] = m.group("v").strip()[:80]
    m = _v2_precedent_re.search(tail)
    if m:
        out["precedent_verdict"] = m.group("v").strip().lower()
    # W3.1 — exit_criteria_json (string; downstream binders normalise to JSON)
    m = _v2_exit_criteria_re.search(tail)
    if m:
        raw = m.group("v").strip()
        if raw:
            out["exit_criteria_json"] = raw[:500]
    # plan author-gate-hardening-a3b8f2 W1.3 — new tail fields
    m = _v2_reason_code_re.search(tail)
    if m:
        out["reason_code"] = m.group("v")
    m = _v2_confidence_calibrated_re.search(tail)
    if m:
        try:
            out["confidence_calibrated"] = float(m.group("v"))
        except ValueError:
            pass
    m = _v2_calibrator_version_re.search(tail)
    if m:
        out["calibrator_version"] = m.group("v")[:40]
    m = _v2_hotspot_rank_re.search(tail)
    if m:
        try:
            out["adg_hotspot_rank"] = int(m.group("v"))
        except ValueError:
            pass
    m = _v2_blast_hops_re.search(tail)
    if m:
        try:
            out["blast_radius_hops"] = int(m.group("v"))
        except ValueError:
            pass
    m = _v2_tier_re.search(tail)
    if m:
        out["decision_class_tier"] = m.group("v")
    m = _v2_surfaces_re.search(tail)
    if m:
        surfaces = [s.strip() for s in m.group("v").split(",") if s.strip()]
        if surfaces:
            out["surface_intersections_json"] = json.dumps(surfaces)
    return out


def _infer_layer(repo_area: str) -> str:
    """Infer architectural layer from a repo-area path prefix. Returns '' if unknown."""
    p = repo_area.replace("\\", "/").strip()
    if p.startswith("./"):
        p = p[2:]
    if p.startswith("agentic_core/L"):
        seg = p.split("/", 2)[1]
        if len(seg) >= 2 and seg[0] == "L" and seg[1].isdigit():
            return seg[:2]
    if p.startswith("apps_"):
        return "apps"
    if p.startswith("system_learning/"):
        return "system_learning"
    if p.startswith("infrastructure/"):
        return "infra"
    if p.startswith("tools/"):
        return "tools"
    if p.startswith(".cursor/") or p.startswith("docs/archive/windsurf/legacy-tree/") or p.startswith("ops_scripts/"):
        return "harness"
    return ""


# Sidecar precedent: Cursor harness writes ``artifacts/cursor/`` (see pre_author_gate.py).
# Legacy Windsurf path retained as secondary read for older working copies.
_PRECEDENT_SIDECAR_PATHS = (
    repo_root / "artifacts" / "cursor" / "author_gate_precedent.json",
    repo_root / "artifacts" / "windsurf" / "author_gate_precedent.json",
)
_PRECEDENT_FRESH_WINDOW_S = 3600


def _read_precedent_sidecar() -> dict | None:
    """Return the newest-fresh sidecar payload from Cursor then legacy paths.

    Fail-soft: any read/parse error skips that path; none fresh → None.
    """
    for path in _PRECEDENT_SIDECAR_PATHS:
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError):
            continue
        ts_raw = data.get("generated_at") if isinstance(data, dict) else None
        if not isinstance(ts_raw, str):
            continue
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        if age > _PRECEDENT_FRESH_WINDOW_S:
            continue
        return data if isinstance(data, dict) else None
    return None


def _derive_precedent_from_sidecar(sidecar: dict) -> tuple[str | None, int | None]:
    """Derive (verdict, match_count) from sidecar matches list.

    Verdict precedence: any 'strong' → 'strong'; else any 'suggestive' → 'suggestive';
    else 'none'. Match count is len(matches).
    """
    matches = sidecar.get("matches") if isinstance(sidecar, dict) else None
    if not isinstance(matches, list):
        return None, None
    strengths = {str(m.get("strength", "")).lower() for m in matches if isinstance(m, dict)}
    if "strong" in strengths:
        verdict = "strong"
    elif "suggestive" in strengths:
        verdict = "suggestive"
    else:
        verdict = "none"
    return verdict, len(matches)


# W3.2 — pytest signal: conftest prefers ``artifacts/cursor`` (see tests/conftest.py).
_TEST_SIGNAL_PATHS = (
    repo_root / "artifacts" / "cursor" / "last_test_signal.json",
    repo_root / "artifacts" / "windsurf" / "last_test_signal.json",
)
_FRESH_TEST_WINDOW_S = 1800  # 30 minutes


def _read_fresh_test_signal() -> dict[str, object] | None:
    """Return pytest signal if one was written in the last 30 min, else None."""
    for path in _TEST_SIGNAL_PATHS:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        ts_str = data.get("ts") if isinstance(data, dict) else None
        if not isinstance(ts_str, str):
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except ValueError:
            continue
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        if age > _FRESH_TEST_WINDOW_S:
            continue
        return data if isinstance(data, dict) else None
    return None


def _direct_bind_outcome(
    conn: sqlite3.Connection,
    decision_id: str,
    commit_sha: str,
    status: str,
    *,
    precedent_verdict: str | None = None,
    override_vs_recommendation: int | None = None,
    reason_code: str | None = None,
    degraded_scope: bool = False,
) -> None:
    """W3.3 — Bind an outcome row IMMEDIATELY at capture time.

    Runs only when the marker carried status='executed' AND a commit SHA is
    available from git HEAD. Eliminates the post-commit race that strands
    decisions when git history is rewritten before the binder runs. Idempotent:
    skipped when an outcome already exists for decision_id.
    """
    if status != "executed" or not commit_sha:
        return
    try:
        exists = conn.execute(
            "SELECT 1 FROM decision_outcomes WHERE decision_id = ?", (decision_id,)
        ).fetchone()
    except sqlite3.Error:
        return
    if exists:
        return

    # Fetch commit subject for outcome_label classification
    subject = ""
    try:
        r = subprocess.run(
            ["git", "show", "-s", "--format=%s", commit_sha],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=5,
            check=False,
        )
        if r.returncode == 0:
            subject = r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass

    lower = subject.lower()
    regression_found = 0
    rollback_required = 0
    label = "undecided"
    if any(tok in lower for tok in ("revert ", "rollback", "hotfix revert")):
        rollback_required = 1
        label = "rollback"
    elif any(tok in lower for tok in ("fix regression", "regression fix", "bug:", "bugfix:")):
        regression_found = 1
        label = "rework"
    elif any(tok in lower for tok in ("fix ", "bugfix")):
        label = "rework"

    # W3.2 — pull pytest signal if fresh; overrides default tests_passed=0
    tests_passed = 0
    test_signal = _read_fresh_test_signal()
    notes_suffix = ""
    if test_signal:
        exit_code = test_signal.get("exit_code")
        if exit_code == 0:
            tests_passed = 1
            if label == "undecided":
                label = "success"
            notes_suffix = f" | test_signal=pass (exit={exit_code})"
        else:
            notes_suffix = f" | test_signal=fail (exit={exit_code})"

    ov = override_vs_recommendation
    if ov is not None and not isinstance(ov, int):
        try:
            ov = int(ov)
        except (TypeError, ValueError):
            ov = None

    bind_tier = outcome_bind_tier(
        precedent_verdict=precedent_verdict,
        override_vs_recommendation=ov,
        reason_code=str(reason_code) if reason_code else None,
        degraded_scope=degraded_scope,
        tests_passed=tests_passed,
        regression_found=regression_found,
        rollback_required=rollback_required,
    )

    try:
        conn.execute(
            """INSERT INTO decision_outcomes
                   (decision_id, execution_completed, tests_passed, regression_found,
                    rollback_required, promote_to_pattern, commit_shas_json,
                    files_written_json, tests_run_json, latency_to_outcome_s,
                    pattern_promotion_eligible, outcome_label, bound_at, outcome_notes,
                    outcome_bind_tier)
               VALUES (?, 1, ?, ?, ?, 0, ?, '[]', '[]', 0, 0, ?, ?, ?, ?)""",
            (
                decision_id,
                tests_passed,
                regression_found,
                rollback_required,
                json.dumps([commit_sha]),
                label,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                f"direct-bound at capture: {subject[:150]}{notes_suffix}",
                bind_tier,
            ),
        )
        conn.commit()
    except sqlite3.Error:
        # guardian: allow-silent-swallow -- direct-bind: non-fatal; post-commit binder will retry
        pass


def _insert_scope_row(conn: sqlite3.Connection, decision_id: str, repo_area: str) -> None:
    """Write a decision_scope row so the outcome binder can match commits to this decision.

    Invariant (W1.3, 2026-04-24): if ``repo_area`` is non-empty we ALWAYS populate
    ``file_path`` — prior logic only set it when the area contained a slash, which
    left ~68% of scope rows with NULL file_path and broke the binder's
    file-intersection fallback path. ``repo_area`` is the SSOT for "where does
    this decision live", so using it as the path is the safest default.
    """
    if not repo_area:
        return
    layer = _infer_layer(repo_area)
    file_path = repo_area[:200]  # ALWAYS set — empty file_path was the 68% gap
    try:
        conn.execute(
            """INSERT INTO decision_scope (decision_id, file_path, layer, repo_area)
               VALUES (?, ?, ?, ?)""",
            (decision_id, file_path, layer or None, repo_area[:200]),
        )
    except sqlite3.Error:
        # guardian: allow-silent-swallow -- scope insert: non-fatal, capture already succeeded
        pass


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

_ddl = """\
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
    status                TEXT NOT NULL DEFAULT 'surfaced',
    -- v2 calibration fields (optional; populated from DECISION_CAPTURED: marker tail)
    confidence_top             REAL,
    confidence_dominance_gap   REAL,
    override_vs_recommendation INTEGER,
    selection_latency_ms       INTEGER,
    principle_at_stake         TEXT,
    -- meta-learning W1 (plan c8f4a2): precedent injection telemetry
    precedent_verdict          TEXT,
    precedent_match_count      INTEGER,
    -- W3.1 (plan 1f4c8a): per-decision testable success conditions
    exit_criteria_json         TEXT,
    -- W1 (plan author-gate-hardening-a3b8f2): calibration + spine-integration columns
    reason_code                TEXT,
    confidence_calibrated      REAL,
    calibrator_version         TEXT,
    adg_hotspot_rank           INTEGER,
    blast_radius_hops          INTEGER,
    surface_intersections_json TEXT,
    decision_class_tier        TEXT
);

CREATE TABLE IF NOT EXISTS decision_signals (
    signal_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id   TEXT NOT NULL REFERENCES decisions(decision_id),
    option_id     TEXT NOT NULL,
    signal_name   TEXT NOT NULL,
    signal_value  REAL NOT NULL,
    signal_weight REAL NOT NULL,
    signal_source TEXT
);
CREATE INDEX IF NOT EXISTS idx_decision_signals_decision
    ON decision_signals(decision_id);

CREATE TABLE IF NOT EXISTS decision_calibration_snapshots (
    snapshot_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at           TEXT NOT NULL,
    calibrator_version   TEXT NOT NULL,
    decision_type        TEXT NOT NULL,
    n_outcomes           INTEGER NOT NULL,
    brier_score          REAL,
    ece_score            REAL,
    reliability_json     TEXT,
    isotonic_points_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_calib_snap_type_ver
    ON decision_calibration_snapshots(decision_type, calibrator_version);

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
        conn.row_factory = sqlite3.Row  # required for column-name access in ensure_row_hash
        conn.executescript(_ddl)
        # W5.1 — add exit_criteria_json column (additive, nullable, idempotent).
        # SQLite has no 'ADD COLUMN IF NOT EXISTS' so we probe PRAGMA first.
        try:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)").fetchall()}
            if "exit_criteria_json" not in cols:
                conn.execute("ALTER TABLE decisions ADD COLUMN exit_criteria_json TEXT")
            # meta-learning W1: precedent telemetry columns (additive)
            if "precedent_verdict" not in cols:
                conn.execute("ALTER TABLE decisions ADD COLUMN precedent_verdict TEXT")
            if "precedent_match_count" not in cols:
                conn.execute("ALTER TABLE decisions ADD COLUMN precedent_match_count INTEGER")
            # plan author-gate-hardening-a3b8f2 W1: calibration + spine columns (additive)
            for _col, _typ in (
                ("reason_code", "TEXT"),
                ("confidence_calibrated", "REAL"),
                ("calibrator_version", "TEXT"),
                ("adg_hotspot_rank", "INTEGER"),
                ("blast_radius_hops", "INTEGER"),
                ("surface_intersections_json", "TEXT"),
                ("decision_class_tier", "TEXT"),
            ):
                if _col not in cols:
                    conn.execute(f"ALTER TABLE decisions ADD COLUMN {_col} {_typ}")
        except sqlite3.Error:
            # guardian: allow-silent-swallow -- additive migration: non-fatal
            pass
        try:
            ensure_w1_feedback_loop_columns(conn)
        except sqlite3.Error:
            # guardian: allow-silent-swallow -- W1 additive columns: non-fatal
            pass
        try:
            ensure_w2_decision_signal_columns(conn)
        except sqlite3.Error:
            # guardian: allow-silent-swallow -- W2 additive columns: non-fatal
            pass
        conn.commit()
        return conn
    except (
        sqlite3.Error,
        OSError,
    ):  # guardian: allow-return-none-swallow -- DB init: non-fatal, caller handles None
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
            cwd=str(repo_root),
            shell=False,
            check=False,
        )
        if r.returncode == 0:
            branch = r.stdout.strip()
    except (
        OSError,
        subprocess.TimeoutExpired,
    ):  # guardian: allow-silent-swallow -- git branch probe: non-fatal, empty string used
        pass
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root),
            shell=False,
            check=False,
        )
        if r.returncode == 0:
            sha = r.stdout.strip()
    except (
        OSError,
        subprocess.TimeoutExpired,
    ):  # guardian: allow-silent-swallow -- git sha probe: non-fatal, empty string used
        pass
    return branch, sha


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def _extract_response_text(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        # post_cursor_agent_response puts response text at tool_info.response (Windsurf docs)
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
    """Heuristically extract option labels from Author-Gate packet text."""
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
    """Capture a decision from a DECISION_CAPTURED structured marker.

    Parses v1 required fields (type, repo_area, selected, outcome) and any v2
    calibration fields present in the tail (confidence, gap, override, latency_ms,
    principle). v2 fields populate otherwise-NULL columns for meta-learning.
    """
    dtype = m.group("dtype")
    area = m.group("area").strip()
    selected = m.group("selected").strip()[:200]
    outcome = m.group("outcome").strip()
    tail = m.groupdict().get("tail") or ""
    v2 = _parse_v2_tail(tail)
    marker_precedent_raw = v2.get("precedent_verdict")
    marker_precedent: str | None = None
    if isinstance(marker_precedent_raw, str):
        s = marker_precedent_raw.strip().lower()
        if s in ("strong", "suggestive", "none"):
            marker_precedent = s

    sidecar = _read_precedent_sidecar()
    sidecar_verdict, sidecar_count = (
        _derive_precedent_from_sidecar(sidecar) if sidecar is not None else (None, None)
    )

    layer_guess = _infer_layer(area)
    meta = compute_precedent_capture_metadata(
        dtype,
        area[:200],
        area.strip()[:200],
        layer=layer_guess,
        degraded_scope=False,
        sidecar=sidecar,
    )
    lookup_verdict = meta.get("precedent_verdict_from_lookup")
    merged = merge_precedent_verdict(marker_precedent, lookup_verdict, sidecar_verdict)
    v2["precedent_verdict"] = merged
    pmc = meta.get("precedent_match_count")
    if pmc is None and sidecar_count is not None:
        pmc = sidecar_count
    v2["precedent_match_count"] = pmc

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
             selected_option_id, options_json, status,
             confidence_top, confidence_dominance_gap, override_vs_recommendation,
             selection_latency_ms, principle_at_stake,
             precedent_verdict, precedent_match_count, exit_criteria_json,
             reason_code, confidence_calibrated, calibrator_version,
             adg_hotspot_rank, blast_radius_hops, surface_intersections_json,
             decision_class_tier,
             precedent_top_match_ids_json, precedent_lookup_query_digest,
             precedent_lookup_policy_version, precedent_capture_utc)
        VALUES
            (:decision_id, :created_at, :branch, :commit_sha, :decision_type,
             :request_summary, :normalized_intent, :recommended_option_id,
             :selected_option_id, :options_json, :status,
             :confidence_top, :confidence_dominance_gap, :override_vs_recommendation,
             :selection_latency_ms, :principle_at_stake,
             :precedent_verdict, :precedent_match_count, :exit_criteria_json,
             :reason_code, :confidence_calibrated, :calibrator_version,
             :adg_hotspot_rank, :blast_radius_hops, :surface_intersections_json,
             :decision_class_tier,
             :precedent_top_match_ids_json, :precedent_lookup_query_digest,
             :precedent_lookup_policy_version, :precedent_capture_utc)
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
            "confidence_top": v2.get("confidence_top"),
            "confidence_dominance_gap": v2.get("confidence_dominance_gap"),
            "override_vs_recommendation": v2.get("override_vs_recommendation"),
            "selection_latency_ms": v2.get("selection_latency_ms"),
            "principle_at_stake": v2.get("principle_at_stake"),
            "precedent_verdict": v2.get("precedent_verdict"),
            "precedent_match_count": v2.get("precedent_match_count"),
            "exit_criteria_json": v2.get("exit_criteria_json"),
            "reason_code": v2.get("reason_code"),
            "confidence_calibrated": v2.get("confidence_calibrated"),
            "calibrator_version": v2.get("calibrator_version"),
            "adg_hotspot_rank": v2.get("adg_hotspot_rank"),
            "blast_radius_hops": v2.get("blast_radius_hops"),
            "surface_intersections_json": v2.get("surface_intersections_json"),
            "decision_class_tier": v2.get("decision_class_tier"),
            "precedent_top_match_ids_json": meta.get("precedent_top_match_ids_json"),
            "precedent_lookup_query_digest": meta.get("precedent_lookup_query_digest"),
            "precedent_lookup_policy_version": meta.get("precedent_lookup_policy_version"),
            "precedent_capture_utc": meta.get("precedent_capture_utc"),
        },
    )
    conn.execute(
        """INSERT INTO decisions_fts
               (decision_id, normalized_intent, request_summary, user_goal, selection_rationale)
           VALUES (?, ?, ?, '', '')""",
        (decision_id, area[:200], context_window[:500]),
    )
    _insert_scope_row(conn, decision_id, area)
    opt_labels = [selected]
    meta_dict = dict(meta) if isinstance(meta, dict) else {}
    replace_decision_signals_for_capture(
        conn,
        decision_id,
        opt_labels,
        recommended_label=selected,
        merged_verdict=merged,
        meta=meta_dict,
        v2=dict(v2),
    )
    conn.commit()
    # W3.3 — direct-bind outcome row NOW, before any rebase can orphan the SHA.
    rc_raw = v2.get("reason_code")
    rc_s = str(rc_raw) if rc_raw is not None else None
    _direct_bind_outcome(
        conn,
        decision_id,
        sha,
        status,
        precedent_verdict=merged,
        override_vs_recommendation=v2.get("override_vs_recommendation")
        if isinstance(v2.get("override_vs_recommendation"), int)
        else None,
        reason_code=rc_s,
        degraded_scope=False,
    )
    if _ensure_row_hash is not None:
        try:
            _ensure_row_hash(conn, decision_id)
        except (
            sqlite3.Error,
            TypeError,
        ):  # guardian: allow-specific-multi -- integrity seal: fail-open (capture succeeded); TypeError covers in-memory conns without row_factory
            pass
    return True


def detect_and_capture(text: str, conn: sqlite3.Connection) -> bool:
    """
    Detect an Author-Gate packet in text and write a decision record.
    Returns True if a new record was inserted, False otherwise.
    Tries structured marker first, falls back to packet header heuristic.
    """
    # Path 1: structured DECISION_CAPTURED marker (reliable, emitted by Cursor Agent post-Author-Gate)
    marker = _capture_marker_re.search(text)
    if marker:
        return _capture_from_marker(marker, text, conn)

    # Path 2: heuristic Author-Gate packet header in prose (fallback)
    m = _packet_header_re.search(text)
    if not m:
        return False

    recommended = m.group(1).strip()[:200]
    ts = datetime.now(timezone.utc).isoformat()
    decision_id = _make_decision_id(text, ts)

    # Dedup: same Author-Gate packet may fire hook twice in one session
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

    sidecar_h = _read_precedent_sidecar()
    sidecar_verdict_h, sidecar_count_h = (
        _derive_precedent_from_sidecar(sidecar_h) if sidecar_h is not None else (None, None)
    )
    layer_h = _infer_layer(normalized_intent)
    meta_h = compute_precedent_capture_metadata(
        decision_type,
        normalized_intent[:200],
        normalized_intent.strip()[:200],
        layer=layer_h,
        degraded_scope=False,
        sidecar=sidecar_h,
    )
    merged_h = merge_precedent_verdict(None, meta_h.get("precedent_verdict_from_lookup"), sidecar_verdict_h)
    pmc_h = meta_h.get("precedent_match_count")
    if pmc_h is None and sidecar_count_h is not None:
        pmc_h = sidecar_count_h

    conn.execute(
        """
        INSERT OR IGNORE INTO decisions
            (decision_id, created_at, branch, commit_sha, decision_type,
             request_summary, normalized_intent, recommended_option_id,
             options_json, status,
             precedent_verdict, precedent_match_count,
             precedent_top_match_ids_json, precedent_lookup_query_digest,
             precedent_lookup_policy_version, precedent_capture_utc)
        VALUES
            (:decision_id, :created_at, :branch, :commit_sha, :decision_type,
             :request_summary, :normalized_intent, :recommended_option_id,
             :options_json, :status,
             :precedent_verdict, :precedent_match_count,
             :precedent_top_match_ids_json, :precedent_lookup_query_digest,
             :precedent_lookup_policy_version, :precedent_capture_utc)
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
            "precedent_verdict": merged_h,
            "precedent_match_count": pmc_h,
            "precedent_top_match_ids_json": meta_h.get("precedent_top_match_ids_json"),
            "precedent_lookup_query_digest": meta_h.get("precedent_lookup_query_digest"),
            "precedent_lookup_policy_version": meta_h.get("precedent_lookup_policy_version"),
            "precedent_capture_utc": meta_h.get("precedent_capture_utc"),
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
    # normalized_intent is the best repo-area proxy available in the v1 packet-header path
    _insert_scope_row(conn, decision_id, normalized_intent)
    opt_labels = options if options else ([recommended] if recommended else [])
    if not opt_labels:
        opt_labels = ["(author_gate_capture)"]
    meta_h_dict = dict(meta_h) if isinstance(meta_h, dict) else {}
    replace_decision_signals_for_capture(
        conn,
        decision_id,
        opt_labels,
        recommended_label=recommended,
        merged_verdict=merged_h,
        meta=meta_h_dict,
        v2={},
    )
    conn.commit()
    if _ensure_row_hash is not None:
        try:
            _ensure_row_hash(conn, decision_id)
        except (
            sqlite3.Error,
            TypeError,
        ):  # guardian: allow-specific-multi -- integrity seal: fail-open (capture succeeded); TypeError covers in-memory conns without row_factory
            pass
    return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
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

        marker_found = bool(_capture_marker_re.search(text))
        _debug_log(f"text_len={len(text)} marker={marker_found}")

        # W1.1 — validate marker grammar completeness. Advisory: log violations
        # but do NOT suppress capture (incomplete data is still valuable).
        if marker_found and _validate_marker is not None and _log_marker_violation is not None:
            try:
                report = _validate_marker(text)
                if not report["valid"]:
                    _log_marker_violation(report, context="capture_hook")
                    _debug_log(f"marker_validator: valid={report['valid']} found={report['markers_found']}")
            except (ValueError, OSError):  # guardian: allow-specific-multi -- validator: non-fatal, fail-open
                pass

        conn = _init_db()
        if conn is None:
            _debug_log("db_init_failed")
            return 0

        try:
            captured = detect_and_capture(text, conn)
            _debug_log(f"captured={captured}")
        except sqlite3.Error:  # guardian: allow-silent-swallow -- Author-Gate capture: non-fatal, fail-open
            pass
        finally:
            conn.close()

    except (
        OSError,
        ValueError,
    ):  # guardian: allow-silent-swallow -- Author-Gate capture main: non-fatal, fail-open
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
