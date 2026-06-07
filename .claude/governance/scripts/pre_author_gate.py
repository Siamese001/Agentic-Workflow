#!/usr/bin/env python3
"""
pre_author_gate.py — Author-Gate trigger gate (developer-loop / harness-side).

Invoked via .cursor/hooks.json on pre_write_code. Evaluates observable
features of the pending action against .claude/schemas/author_gate_triggers.yaml.
When a trigger fires AND no active author-gate decision matches the current
context fingerprint, emits AUTHOR_GATE_REQUIRED and blocks the write.

Not the same as runtime HITL — that lives in agentic_core/L5_safety/ per ADR-023.

Deny-and-continue semantics (Anthropic Auto Mode):
    - Exit 2 with structured AUTHOR_GATE_REQUIRED marker (back-compat alias HITL_REQUIRED also emitted)
    - Increments consecutive + total denial counters in author_gate_session_state.json
    - After N consecutive (default 3) or M cumulative (default 20) denials,
      escalates to a hard halt and writes a severity=critical violation row

Fresh invocation modes:
    python .claude/governance/scripts/pre_author_gate.py                 # hook mode
    python .claude/governance/scripts/pre_author_gate.py --self-test     # validate triggers.yaml
    python .claude/governance/scripts/pre_author_gate.py --dry-run       # evaluate without exiting 2
    python .claude/governance/scripts/pre_author_gate.py --reset-session # clear denial counters

Exit codes:
    0 = pass (Tier 1/2 or no trigger match or bypass condition fired)
    2 = AUTHOR_GATE_REQUIRED — caller must emit a packet and re-run
    3 = HARD_ESCALATION — denial ceiling reached; halt session
    4 = self-test failed
    5 = fatal config error

CONSTITUTIONAL
    - No shell=True, no PowerShell; pure Python + sqlite3
    - UTF-8 stdio
    - Specific exceptions: sqlite3.Error, OSError, ValueError, yaml.YAMLError
    - Bounded operations (500-file scan ceiling)
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("[pre_author_gate] PyYAML required — pip install pyyaml", file=sys.stderr)
    sys.exit(5)

REPO_ROOT = Path(__file__).resolve().parents[2]
TRIGGERS_PATH = REPO_ROOT / ".claude" / "schemas" / "author_gate_triggers.yaml"
ADG_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "adg"

# W1: ADG query timeout and retry configuration
_ADG_QUERY_TIMEOUT = 5.0  # seconds
_ADG_MAX_RETRIES = 3
_ADG_RETRY_DELAY_BASE = 0.1  # seconds, exponential backoff

# Import ADG backend if available (fail-soft if tools/ not in path)
try:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.adg.core.graph_projection_backend import GraphProjectionBackend
    _ADG_BACKEND_AVAILABLE = True
except ImportError:
    _ADG_BACKEND_AVAILABLE = False
LEDGER_PATH = REPO_ROOT / ".claude" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
STATE_DIR = REPO_ROOT / "artifacts" / "cursor"
SESSION_STATE_PATH = STATE_DIR / "author_gate_session_state.json"
VIOLATIONS_PATH = STATE_DIR / "author_gate_violations.jsonl"
# W2.2 — precedent sidecar: cleared at gate-pass, written at gate-fire.
# Cursor Agent reads this file at packet-construction time and includes the matches
# in the AUTHOR-GATE DECISION header. Format: dict from lookup_refactor_decisions.
PRECEDENT_SIDECAR_PATH = STATE_DIR / "author_gate_precedent.json"
LOOKUP_SKILL_PATH = REPO_ROOT / ".claude" / "skills" / "refactor-decision-memory" / "lookup_refactor_decisions.py"

# Back-compat: legacy paths from pre-rename era (2026-04-21 harness-enforcement-rename).
# One-shot migration runs on first touch; removed 2026-07-21 when deprecation window closes.
_LEGACY_SESSION_STATE_PATH = STATE_DIR / "hitl_session_state.json"
_LEGACY_VIOLATIONS_PATH = STATE_DIR / "hitl_violations.jsonl"


def _migrate_legacy_state(legacy: Path, current: Path) -> None:
    """One-shot rename legacy path -> current. Fail-open on any OSError."""
    try:
        if legacy.exists() and not current.exists():
            current.parent.mkdir(parents=True, exist_ok=True)
            legacy.rename(current)
    except OSError:
        # guardian: allow-silent-swallow -- one-shot migration: non-fatal, fail-open
        pass

GIT_TIMEOUT_S = 10
MAX_SCAN_FILES = 500


# ===================================================================== #
# Data model                                                            #
# ===================================================================== #


@dataclass
class ChangeSnapshot:
    """Observable features of the pending change."""

    changed_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    added_lines_by_file: dict[str, list[str]] = field(default_factory=dict)

    @property
    def files_changed(self) -> int:
        return len(self.changed_files) + len(self.deleted_files)

    def fingerprint(self) -> str:
        """Stable hash for matching active decisions to this changeset."""
        canon = "|".join(sorted(set(self.changed_files) | set(self.deleted_files)))
        return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


# ===================================================================== #
# Helpers                                                               #
# ===================================================================== #


def _run_git(argv: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *argv],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=GIT_TIMEOUT_S,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def collect_snapshot() -> ChangeSnapshot:
    """Capture pending changes from git status + diff."""
    snap = ChangeSnapshot()

    # Staged + unstaged changes vs HEAD
    porcelain = _run_git(["status", "--porcelain"])
    for line in porcelain.splitlines():
        if len(line) < 4:
            continue
        code = line[:2]
        path = line[3:].strip().split(" -> ")[-1].strip('"')
        if not path:
            continue
        if "D" in code:
            snap.deleted_files.append(path)
        else:
            snap.changed_files.append(path)
        if len(snap.changed_files) + len(snap.deleted_files) >= MAX_SCAN_FILES:
            break

    # Added lines per file (for content-regex triggers)
    # Use combined diff (staged + unstaged)
    diff = _run_git(["diff", "HEAD", "--unified=0", "--no-color"])
    current_file: str | None = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[len("+++ b/") :]
            snap.added_lines_by_file.setdefault(current_file, [])
        elif line.startswith("+") and not line.startswith("+++") and current_file:
            snap.added_lines_by_file[current_file].append(line)
    return snap


def load_triggers() -> dict[str, Any]:
    if not TRIGGERS_PATH.exists():
        raise FileNotFoundError(f"Triggers config missing: {TRIGGERS_PATH}")
    with TRIGGERS_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_session_state() -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _migrate_legacy_state(_LEGACY_SESSION_STATE_PATH, SESSION_STATE_PATH)
    if not SESSION_STATE_PATH.exists():
        return {
            "session_started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "consecutive_denials": 0,
            "total_denials": 0,
            "active_fingerprints": [],
            "last_trigger": None,
        }
    try:
        with SESSION_STATE_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {
            "session_started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "consecutive_denials": 0,
            "total_denials": 0,
            "active_fingerprints": [],
            "last_trigger": None,
        }


def save_session_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with SESSION_STATE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def has_active_decision(fingerprint: str) -> bool:
    """Check if a surfaced decision already covers this fingerprint."""
    if not LEDGER_PATH.exists():
        return False
    try:
        conn = sqlite3.connect(str(LEDGER_PATH), timeout=5)
    except sqlite3.Error:
        return False
    try:
        cur = conn.execute(
            """
            SELECT 1 FROM decisions
             WHERE status = 'surfaced'
               AND context_fingerprint_json LIKE ?
             LIMIT 1
            """,
            (f'%"fp":"{fingerprint}"%',),
        )
        return cur.fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def append_violation(payload: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _migrate_legacy_state(_LEGACY_VIOLATIONS_PATH, VIOLATIONS_PATH)
    with VIOLATIONS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload) + "\n")


# ===================================================================== #
# W2 — Precedent injection (consult refactor-decision-memory skill)     #
# ===================================================================== #


def _infer_repo_area(snap: ChangeSnapshot) -> str:
    """Pick the most specific shared prefix of changed files as repo_area.

    Returns "" if no files changed or paths don't share a meaningful prefix.
    """
    paths = [p.replace("\\", "/") for p in snap.changed_files + snap.deleted_files]
    if not paths:
        return ""
    if len(paths) == 1:
        # Single-file change — use the file's directory as the area
        return "/".join(paths[0].split("/")[:-1]) or paths[0]
    # Common prefix
    parts_lists = [p.split("/") for p in paths]
    common: list[str] = []
    for segs in zip(*parts_lists):
        if len(set(segs)) == 1:
            common.append(segs[0])
        else:
            break
    return "/".join(common) if common else ""


def _invoke_lookup(decision_type: str, normalized_intent: str, repo_area: str) -> dict[str, Any]:
    """Call the refactor-decision-memory skill. Returns {} on any failure.

    Runs as a short-lived subprocess (no import coupling). Fail-open: any
    non-zero exit, timeout, or parse error returns empty dict.
    """
    if not LOOKUP_SKILL_PATH.exists():
        return {}
    query = json.dumps({
        "decision_type": decision_type,
        "normalized_intent": normalized_intent[:200],
        "repo_area": repo_area[:100],
        "limit": 5,
    })
    try:
        r = subprocess.run(
            [sys.executable, str(LOOKUP_SKILL_PATH)],
            input=query,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}
    if r.returncode != 0:
        return {}
    try:
        parsed: dict[str, Any] = json.loads(r.stdout)
        return parsed
    except (json.JSONDecodeError, ValueError):
        return {}


def _write_precedent_sidecar(matches: list[dict[str, Any]],
                             snap: ChangeSnapshot,
                             triggers: list[dict[str, Any]]) -> None:
    """Persist precedent lookup result for Cursor Agent to read when building the packet."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fingerprint": snap.fingerprint(),
        "files_in_scope": sorted(set(snap.changed_files + snap.deleted_files))[:20],
        "triggers": [t["id"] for t in triggers],
        "matches": matches,
        "match_count": len(matches),
    }
    try:
        with PRECEDENT_SIDECAR_PATH.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
    except OSError:  # guardian: allow-silent-swallow -- sidecar write: non-fatal, fail-open
        pass


def _clear_precedent_sidecar() -> None:
    try:
        if PRECEDENT_SIDECAR_PATH.exists():
            PRECEDENT_SIDECAR_PATH.unlink()
    except OSError:  # guardian: allow-silent-swallow -- sidecar clear: non-fatal
        pass


def consult_precedent(matched_triggers: list[dict[str, Any]],
                      snap: ChangeSnapshot) -> list[dict[str, Any]]:
    """Query the ledger for relevant past decisions. Writes sidecar; returns matches.

    Strategy: try up to 3 queries in widening order so short historical intents
    (e.g. bare repo_area) still match when current intent is verbose. The lookup
    skill's FTS5 query is an AND-of-tokens, so a long intent rarely matches a
    short historical row. Stop at the first non-empty result.

    Query order:
        1. <trigger.description> + repo_area   (semantic + location)
        2. repo_area alone                      (location only — widest, lossy)
        3. trigger.description alone            (semantic only)
    """
    if not matched_triggers:
        return []
    primary = matched_triggers[0]
    decision_type = str(primary.get("decision_type", "unknown"))
    description = str(primary.get("description", "") or primary.get("id", ""))
    repo_area = _infer_repo_area(snap)

    queries: list[str] = []
    if description and repo_area:
        queries.append(f"{description} {repo_area}")
    if repo_area:
        queries.append(repo_area)
    if description:
        queries.append(description)

    matches: list[dict[str, Any]] = []
    for intent in queries:
        result = _invoke_lookup(decision_type, intent[:200], repo_area)
        raw_matches = result.get("matches", []) if isinstance(result, dict) else []
        if raw_matches:
            matches = raw_matches
            break

    if matches:
        _write_precedent_sidecar(matches, snap, matched_triggers)
    else:
        _clear_precedent_sidecar()
    return matches


# ===================================================================== #
# Trigger evaluation                                                    #
# ===================================================================== #


def _globs_any(path: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in globs)


def _regex_any(lines: list[str], patterns: list[str]) -> bool:
    compiled = [re.compile(p) for p in patterns]
    for line in lines:
        for rx in compiled:
            if rx.search(line):
                return True
    return False


def _regex_none(lines: list[str], patterns: list[str]) -> bool:
    """True iff NONE of patterns match any line."""
    compiled = [re.compile(p) for p in patterns]
    for line in lines:
        for rx in compiled:
            if rx.search(line):
                return False
    return True


# Sensitive governance paths that force Tier-3 classification regardless of file count
# These paths CANNOT bypass Author-Gate via Tier-2 single-file edit exemption
SENSITIVE_PATH_PATTERNS = [
    ".claude/rules/",
    ".claude/schemas/",
    ".claude/governance/scripts/pre_author_gate.py",
    "apps_rg/config/",
    "agentic_core/L5_safety/",
    "agentic_core/L4_state/",
    "docs/reference/00A_L5_Governance_Safety/",
    "docs/reference/00B_L4_State_Archive_and_UWG/",
    "docs/reference/00C_Runtime_Gates_Current_Run_Mesh/",
    "docs/architecture/adr/",  # ADR / governance surfaces
    "config/certification/",   # Certification config
    "ops_scripts/ci/",         # CI gates (authoritative enforcement)
]


def _is_sensitive_path(file_path: str) -> bool:
    """Check if file_path matches any sensitive governance pattern.

    W2: Handles Windows backslashes, mixed separators, and absolute paths.
    """
    normalized = file_path.replace("\\", "/")
    for pattern in SENSITIVE_PATH_PATTERNS:
        # Check for exact match, prefix match, or pattern match
        if normalized.startswith(pattern) or fnmatch.fnmatch(normalized, pattern):
            return True
        # W2: Handle absolute Windows paths (e.g., C:/path/.claude/rules/...)
        # Check if pattern appears anywhere in the path (for drive-letter paths)
        if "/" + pattern in normalized or normalized.endswith("/" + pattern.rstrip("/")):
            return True
        # Also check pattern without trailing slash
        pattern_no_slash = pattern.rstrip("/")
        if pattern_no_slash in normalized:
            # Ensure it's a path segment match, not a substring
            # e.g., ".claude/rules" should match "/path/.claude/rules/file"
            # but not "/path/x.claude/rules" (partial match)
            idx = normalized.find(pattern_no_slash)
            if idx > 0:
                # Check that the character before the match is a path separator
                if normalized[idx - 1] == "/":
                    return True
    return False


# ===================================================================== #
# ADG Query Helpers (W3/W4)                                             #
# =====================================================================


# Module-level cache for ADG backend (initialized once per process)
_adg_backend_instance: Any = None


def _get_adg_backend() -> Any:
    """Return cached GraphProjectionBackend instance or None if unavailable."""
    global _adg_backend_instance
    if _adg_backend_instance is not None:
        return _adg_backend_instance
    if not _ADG_BACKEND_AVAILABLE:
        return None
    try:
        _adg_backend_instance = GraphProjectionBackend()
        return _adg_backend_instance
    except Exception:
        return None


def _adg_query_with_retry(
    query_func,
    *args,
    max_retries: int = _ADG_MAX_RETRIES,
    retry_delay_base: float = _ADG_RETRY_DELAY_BASE
):
    """Execute ADG query with retry and exponential backoff.

    Logs retry events to violations for audit trail.
    Returns (success, result, retry_count).
    """
    last_exc = None
    for attempt in range(max_retries):
        try:
            result = query_func(*args)
            if attempt > 0:
                # Log successful retry
                append_violation(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "severity": "adg_retry_success",
                        "attempt": attempt + 1,
                        "query": query_func.__name__,
                        "message": f"ADG query succeeded after {attempt} retries",
                    }
                )
            return True, result, attempt
        except Exception as exc:
            last_exc = exc
            is_sqlite_busy = "database is locked" in str(exc).lower() or "busy" in str(exc).lower()
            is_timeout = "timeout" in str(exc).lower()

            if attempt < max_retries - 1:
                delay = retry_delay_base * (2 ** attempt)
                # Log retry attempt
                append_violation(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "severity": "adg_retry_attempt",
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "delay": delay,
                        "query": query_func.__name__,
                        "error": str(exc)[:100],
                        "error_type": "sqlite_busy" if is_sqlite_busy else ("timeout" if is_timeout else "other"),
                    }
                )
                # Exponential backoff
                import time
                time.sleep(delay)

    # All retries exhausted
    return False, last_exc, max_retries


def _get_adg_fan_in(file_path: str) -> tuple[int | None, str, str]:
    """Query ADG for fan-in (blast radius) of a file.

    W1: Implements explicit timeout and retry with exponential backoff.
    Returns:
        (fan_in_value, artifact_source, status)
        - fan_in_value: int if available, None if not
        - artifact_source: path to ADG artifact used, or "unavailable"
        - status: "ok", "stale", "unavailable", "node_not_found"
    """
    backend = _get_adg_backend()
    if backend is None:
        return None, "unavailable", "unavailable"

    if not backend.is_available():
        return None, "unavailable", "unavailable"

    if backend.is_stale():
        # Still query but mark as stale
        status = "stale"
    else:
        status = "ok"

    # Convert file path to adg_name format (module path)
    # ADG nodes use formats like: agentic_core/L3_orchestration/pipeline.py
    # or ADG::Module::agentic_core::L3_orchestration::pipeline
    normalized = file_path.replace("\\", "/")

    # Helper to set timeout on connection
    def _set_timeout(conn):
        if conn:
            conn.execute(f"PRAGMA busy_timeout = {_ADG_QUERY_TIMEOUT * 1000}")

    # Try direct lookup first with retry
    def _try_blast_radius():
        result = backend.get_blast_radius(normalized, hops=1)
        if result and result.get("blast_radius_direct", 0) > 0:
            source = getattr(backend, '_proj_path', None)
            source_str = str(source) if source else "unknown"
            return result["blast_radius_direct"], source_str, status
        return None

    success, result, retries = _adg_query_with_retry(_try_blast_radius)
    if success and result is not None:
        return result

    # Try as module-style path with proj_centrality direct query with retry
    def _try_centrality_query():
        conn = getattr(backend, '_conn', None)
        if conn:
            _set_timeout(conn)
            # Query by resolved_path via proj_nodes join
            cursor = conn.execute(
                """SELECT c.blast_radius_direct, c.fan_in
                   FROM proj_centrality c
                   JOIN proj_nodes n ON c.adg_name = n.adg_name
                   WHERE n.resolved_path = ? OR n.resolved_path LIKE ?
                   LIMIT 1""",
                (normalized, f"%{normalized}%")
            )
            row = cursor.fetchone()
            if row:
                source = getattr(backend, '_proj_path', None)
                source_str = str(source) if source else "unknown"
                fan_in = row["blast_radius_direct"] or row["fan_in"] or 0
                return fan_in, source_str, status
        return None

    success, result, retries = _adg_query_with_retry(_try_centrality_query)
    if success and result is not None:
        return result

    # Log final failure if retries exhausted
    if retries >= _ADG_MAX_RETRIES:
        _log_degraded_fallback(f"adg_retries_exhausted_{retries}", file_path)

    return None, getattr(backend, '_proj_path', "unavailable"), "node_not_found"


def _get_layers_from_adg(files: list[str]) -> tuple[set[str], str, str]:
    """Query ADG for layer metadata of changed files.

    W1: Implements explicit timeout and retry with exponential backoff.
    Returns:
        (layers_set, source, status)
        - layers_set: set of layer strings (e.g., {'L3', 'L5'})
        - source: "adg" or "unavailable"
        - status: "ok", "stale", "unavailable", "no_data"
    """
    backend = _get_adg_backend()
    if backend is None or not backend.is_available():
        return set(), "unavailable", "unavailable"

    status = "stale" if backend.is_stale() else "ok"
    layers: set[str] = set()

    def _set_timeout(conn):
        if conn:
            conn.execute(f"PRAGMA busy_timeout = {_ADG_QUERY_TIMEOUT * 1000}")

    def _try_layer_queries():
        conn = getattr(backend, '_conn', None)
        if not conn:
            return None  # Signal unavailable

        _set_timeout(conn)
        result_layers: set[str] = set()

        for file_path in files:
            normalized = file_path.replace("\\", "/")
            cursor = conn.execute(
                "SELECT layer FROM proj_nodes WHERE resolved_path = ? OR resolved_path LIKE ?",
                (normalized, f"%{normalized}%")
            )
            row = cursor.fetchone()
            if row and row["layer"]:
                result_layers.add(row["layer"])

        return result_layers if result_layers else None  # None signals no_data

    success, result, retries = _adg_query_with_retry(_try_layer_queries)

    if success:
        if result is not None:
            return result, "adg", status
        else:
            return set(), "adg", "no_data"

    # Log final failure if retries exhausted
    if retries >= _ADG_MAX_RETRIES:
        _log_degraded_fallback(f"adg_layer_retries_exhausted_{retries}", str(files[:3]))

    return set(), "unavailable", "unavailable"


def _log_blast_radius_receipt(
    file_path: str,
    fan_in: int,
    threshold: int,
    adg_artifact: str,
    trigger_id: str
) -> None:
    """Emit structured receipt for blast-radius trigger."""
    print(
        f"BLAST_RADIUS_TRIGGER: file={file_path} "
        f"fan_in={fan_in} threshold={threshold} "
        f"adg_artifact={adg_artifact} trigger_id={trigger_id}",
        file=sys.stderr,
    )


def _log_layer_crossing_receipt(
    layers: set[str],
    files: list[str],
    detection_source: str,
    trigger_id: str
) -> None:
    """Emit structured receipt for layer-crossing trigger."""
    print(
        f"LAYER_CROSSING_TRIGGER: layers_span={','.join(sorted(layers))} "
        f"files_count={len(files)} detection_source={detection_source} "
        f"trigger_id={trigger_id}",
        file=sys.stderr,
    )


def _log_degraded_fallback(reason: str, file_path: str = "") -> None:
    """Emit structured receipt for ADG degraded fallback."""
    prefix = f"DEGRADED_FALLBACK: reason={reason}"
    if file_path:
        prefix += f" file={file_path}"
    print(prefix, file=sys.stderr)


def check_tier(cfg: dict[str, Any], snap: ChangeSnapshot) -> str:
    """Return 'tier_1', 'tier_2', or 'tier_3'. Tier 1/2 → skip gate."""
    # W2: Sensitive path override — governance files must ALWAYS undergo trigger evaluation
    all_files = snap.changed_files + snap.deleted_files
    if any(_is_sensitive_path(f) for f in all_files):
        return "tier_3"

    tiers = cfg.get("tiers", {})

    # Tier 1 — safe allowlist: we only see write events here so Tier 1 rarely fires
    # (those are tool-level reads; this gate sees pre_write_code). Still, zero-change
    # edge cases → treat as Tier 1.
    if snap.files_changed == 0:
        return "tier_1"

    # Tier 2 — single in-project edit, not touching sensitive dirs
    t2 = tiers.get("tier_2_in_project_edits", {}).get("patterns", [])
    excludes: list[str] = []
    single_only = False
    for p in t2:
        if "files_changed_max" in p:
            single_only = p["files_changed_max"] == 1
        if "path_not_under" in p:
            excludes.extend(p["path_not_under"])
    if single_only and snap.files_changed == 1:
        target = (snap.changed_files + snap.deleted_files)[0]
        if not any(target.replace("\\", "/").startswith(exc) for exc in excludes):
            return "tier_2"

    return "tier_3"


def _layers_from_path_heuristic(files: list[str]) -> set[str]:
    """Infer layer from path prefix — cheap heuristic without ADG call."""
    layers: set[str] = set()
    for f in files:
        p = f.replace("\\", "/")
        if p.startswith("agentic_core/L"):
            seg = p.split("/", 2)[1]
            if seg.startswith("L") and len(seg) >= 2 and seg[1].isdigit():
                layers.add(seg[:2])
        elif p.startswith("apps_"):
            layers.add("apps")
        elif p.startswith("system_learning/"):
            layers.add("system_learning")
        elif p.startswith("infrastructure/"):
            layers.add("infra")
    return layers


def _get_layers_with_fallback(files: list[str]) -> tuple[set[str], str, str]:
    """Get layers for files using ADG first, path heuristic fallback.

    Returns:
        (layers_set, source, status)
        - layers_set: set of layer strings
        - source: "adg" or "path_fallback"
        - status: "ok", "stale", "unavailable" (for ADG), "path_only" (for fallback)
    """
    # Try ADG first
    adg_layers, source, status = _get_layers_from_adg(files)
    if adg_layers and source == "adg":
        return adg_layers, "adg", status

    # Path fallback
    path_layers = _layers_from_path_heuristic(files)
    return path_layers, "path_fallback", "path_only"


def evaluate_trigger(trg: dict[str, Any], snap: ChangeSnapshot, cfg: dict[str, Any] | None = None) -> bool:
    feats = trg.get("features", {})
    cfg = cfg or {}  # Ensure cfg is a dict

    if "files_changed_min" in feats and snap.files_changed < feats["files_changed_min"]:
        return False

    if "deletions_min" in feats and len(snap.deleted_files) < feats["deletions_min"]:
        return False

    if feats.get("layer_crossing") is True:
        layers, source, status = _get_layers_with_fallback(snap.changed_files + snap.deleted_files)
        if len(layers) < 2:
            return False
        # W4: Log layer crossing receipt for ADG-backed detection
        if status in ("ok", "stale"):
            _log_layer_crossing_receipt(layers, snap.changed_files + snap.deleted_files, source, trg.get("id", "unknown"))
    elif feats.get("layer_crossing") is False and "files_changed_min" in feats:
        layers, source, status = _get_layers_with_fallback(snap.changed_files + snap.deleted_files)
        if len(layers) >= 2:
            return False  # this rule is for single-layer large changes

    # W3: blast_radius_fan_in_min — ADG-backed fan-in check
    if "blast_radius_fan_in_min" in feats:
        threshold = feats["blast_radius_fan_in_min"]
        all_files = snap.changed_files + snap.deleted_files
        allow_degraded = cfg.get("defaults", {}).get("allow_degraded_mode", False)

        max_fan_in = 0
        max_file = ""
        adg_source = "unavailable"
        adg_status = "unavailable"

        for file_path in all_files:
            fan_in, source, status = _get_adg_fan_in(file_path)
            if fan_in is not None and fan_in > max_fan_in:
                max_fan_in = fan_in
                max_file = file_path
                adg_source = source
                adg_status = status

        if max_fan_in >= threshold:
            # Trigger fired — log receipt
            _log_blast_radius_receipt(max_file, max_fan_in, threshold, adg_source, trg.get("id", "HITL-1.3"))
            return True

        # Not triggered — check if we should fail closed
        if max_fan_in == 0 and adg_status in ("unavailable", "node_not_found"):
            if not allow_degraded:
                # Fail closed: missing ADG data means we can't verify it's safe
                _log_degraded_fallback(f"adg_{adg_status}", max_file)
                return True  # Trigger to be safe
            else:
                _log_degraded_fallback(f"adg_{adg_status}_allowed", max_file)
                # Fall through to other checks

    if "path_globs_any" in feats:
        all_paths = snap.changed_files + snap.deleted_files
        excludes = feats.get("exclude_globs_any", [])
        matched = False
        for path in all_paths:
            if _globs_any(path, feats["path_globs_any"]) and not _globs_any(path, excludes):
                matched = True
                break
        if not matched:
            return False

    if "content_regex_any" in feats:
        # Aggregate added lines across matching files
        relevant_files = (
            [f for f in snap.added_lines_by_file if _globs_any(f, feats.get("path_globs_any", ["**/*"]))]
            if "path_globs_any" in feats
            else list(snap.added_lines_by_file)
        )
        all_lines: list[str] = []
        for f in relevant_files:
            all_lines.extend(snap.added_lines_by_file.get(f, []))
        if not _regex_any(all_lines, feats["content_regex_any"]):
            return False
        if "content_must_not_match" in feats:
            if not _regex_none(all_lines, feats["content_must_not_match"]):
                # negation satisfied already or not applicable — we want lines that match
                # the positive pattern AND do NOT match the negative one. If every line
                # that matched the positive ALSO matches the negative, skip.
                # Conservative: if ANY positive match is paired with a no-negative line, trigger.
                positive = [re.compile(p) for p in feats["content_regex_any"]]
                negative = [re.compile(p) for p in feats["content_must_not_match"]]
                any_pure = False
                for line in all_lines:
                    if any(rx.search(line) for rx in positive) and not any(
                        rx.search(line) for rx in negative
                    ):
                        any_pure = True
                        break
                if not any_pure:
                    return False

    return True


def check_bypass(cfg: dict[str, Any], snap: ChangeSnapshot) -> str | None:
    """Return bypass reason if any bypass condition fires, else None."""
    bypasses = cfg.get("bypass", [])
    # Only implement the deterministic ones for MVP
    last_msg = _run_git(["log", "-1", "--pretty=%s"]).strip()
    for b in bypasses:
        cond = b.get("condition")
        if cond == "commit_message_contains" and b.get("value", "") in last_msg:
            return f"commit-message:{b['value']}"
        if cond == "commit_message_matches":
            try:
                if re.search(b.get("value", ""), last_msg):
                    return f"commit-message-regex:{b['value']}"
            except re.error:
                pass
    return None


# ===================================================================== #
# Main                                                                  #
# ===================================================================== #


def emit_author_gate_required(
    matched: list[dict[str, Any]], snap: ChangeSnapshot, session: dict[str, Any], defaults: dict[str, Any]
) -> int:
    fingerprint = snap.fingerprint()
    session["consecutive_denials"] = int(session.get("consecutive_denials", 0)) + 1
    session["total_denials"] = int(session.get("total_denials", 0)) + 1
    session["last_trigger"] = matched[0]["id"] if matched else None

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "severity": "block",
        "fingerprint": fingerprint,
        "triggers": [m["id"] for m in matched],
        "files": sorted(set(snap.changed_files + snap.deleted_files))[:50],
        "consecutive": session["consecutive_denials"],
        "total": session["total_denials"],
    }
    append_violation(payload)

    max_consec = int(defaults.get("max_consecutive_denials", 3))
    max_total = int(defaults.get("max_total_denials_per_session", 20))

    if session["consecutive_denials"] >= max_consec or session["total_denials"] >= max_total:
        print(
            f"HARD_ESCALATION: reason=denial_ceiling "
            f"consecutive={session['consecutive_denials']}/{max_consec} "
            f"total={session['total_denials']}/{max_total}",
            file=sys.stderr,
        )
        save_session_state(session)
        return 3

    save_session_state(session)
    print(
        f"AUTHOR_GATE_REQUIRED: triggers={','.join(m['id'] for m in matched)} "
        f"fingerprint={fingerprint} files={len(snap.changed_files) + len(snap.deleted_files)}",
        file=sys.stderr,
    )
    # Back-compat alias for any consumer still grepping the legacy marker
    print(
        f"HITL_REQUIRED: triggers={','.join(m['id'] for m in matched)} "
        f"fingerprint={fingerprint} (legacy alias; use AUTHOR_GATE_REQUIRED)",
        file=sys.stderr,
    )
    print(
        "  Rationale: pending change matches author-gate trigger(s). "
        "Emit an Author-Gate packet via ask_user_question before proceeding.",
        file=sys.stderr,
    )
    for m in matched:
        print(f"  - {m['id']} [{m.get('severity', 'block')}] {m.get('description', '')}", file=sys.stderr)
    return 2


def reset_consecutive_on_pass(session: dict[str, Any]) -> None:
    session["consecutive_denials"] = 0
    save_session_state(session)


def self_test() -> int:
    try:
        cfg = load_triggers()
    except (FileNotFoundError, OSError) as exc:
        print(f"[self-test] FAIL: {exc}", file=sys.stderr)
        return 4
    except yaml.YAMLError as exc:
        print(f"[self-test] FAIL YAML parse: {exc}", file=sys.stderr)
        return 4

    triggers = cfg.get("triggers", [])
    if not triggers:
        print("[self-test] FAIL: no triggers defined", file=sys.stderr)
        return 4
    ids = [t.get("id") for t in triggers]
    if len(set(ids)) != len(ids):
        print(f"[self-test] FAIL: duplicate trigger IDs: {ids}", file=sys.stderr)
        return 4
    missing = [t for t in triggers if not t.get("decision_type") or not t.get("features")]
    if missing:
        print(
            f"[self-test] FAIL: triggers missing decision_type/features: {[m['id'] for m in missing]}",
            file=sys.stderr,
        )
        return 4
    # Smoke-test regex compilation
    for t in triggers:
        for rx_list_key in ("content_regex_any", "content_must_not_match"):
            for rx in t.get("features", {}).get(rx_list_key, []):
                try:
                    re.compile(rx)
                except re.error as exc:
                    print(f"[self-test] FAIL: bad regex in {t['id']}: {rx}: {exc}", file=sys.stderr)
                    return 4
    print(f"[self-test] OK — {len(triggers)} triggers, {len(cfg.get('bypass', []))} bypass conditions")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Author-Gate trigger gate (developer-loop, harness-side).")
    parser.add_argument("--self-test", action="store_true", help="Validate triggers.yaml structure")
    parser.add_argument("--dry-run", action="store_true", help="Evaluate without exiting 2")
    parser.add_argument("--reset-session", action="store_true", help="Clear denial counters")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if args.reset_session:
        if SESSION_STATE_PATH.exists():
            SESSION_STATE_PATH.unlink()
        print("[pre_author_gate] Session state cleared.")
        return 0

    # Fail-open on config errors to avoid breaking the hook chain
    try:
        cfg = load_triggers()
    except (FileNotFoundError, OSError, yaml.YAMLError) as exc:
        print(f"[pre_author_gate] Config error (fail-open): {exc}", file=sys.stderr)
        return 0

    snap = collect_snapshot()
    session = load_session_state()
    defaults = cfg.get("defaults", {})

    tier = check_tier(cfg, snap)
    if tier in ("tier_1", "tier_2"):
        if args.verbose:
            print(f"[pre_author_gate] {tier} — pass ({snap.files_changed} files).", file=sys.stderr)
        reset_consecutive_on_pass(session)
        return 0

    bypass_reason = check_bypass(cfg, snap)
    if bypass_reason:
        # W5: Sensitive governance paths cannot be bypassed unless explicitly allowed
        all_files = snap.changed_files + snap.deleted_files
        if any(_is_sensitive_path(f) for f in all_files):
            # Check if sensitive bypass is explicitly allowed in config
            allow_sensitive_bypass = cfg.get("defaults", {}).get("allow_sensitive_bypass", False)
            if not allow_sensitive_bypass:
                if args.verbose:
                    print(
                        f"[pre_author_gate] bypass '{bypass_reason}' blocked: sensitive governance file",
                        file=sys.stderr,
                    )
                # Continue to trigger evaluation (don't return 0)
            else:
                if args.verbose:
                    print(
                        f"[pre_author_gate] bypass fired (sensitive-allowed): {bypass_reason}",
                        file=sys.stderr,
                    )
                reset_consecutive_on_pass(session)
                return 0
        else:
            if args.verbose:
                print(f"[pre_author_gate] bypass fired: {bypass_reason}", file=sys.stderr)
            reset_consecutive_on_pass(session)
            return 0

    fingerprint = snap.fingerprint()
    if has_active_decision(fingerprint):
        if args.verbose:
            print(
                f"[pre_author_gate] active decision matches fingerprint={fingerprint} — pass.",
                file=sys.stderr,
            )
        reset_consecutive_on_pass(session)
        return 0

    matched: list[dict[str, Any]] = []
    for trg in cfg.get("triggers", []):
        if evaluate_trigger(trg, snap, cfg):
            matched.append(trg)

    if not matched:
        if args.verbose:
            print("[pre_author_gate] no trigger match — pass.", file=sys.stderr)
        _clear_precedent_sidecar()  # W2: stale precedent must not leak forward
        reset_consecutive_on_pass(session)
        return 0

    if args.dry_run:
        print(
            f"[pre_author_gate] DRY-RUN would block — {len(matched)} trigger(s) matched: "
            f"{[m['id'] for m in matched]}",
            file=sys.stderr,
        )
        return 0

    # W2 — consult the refactor-decision-memory ledger BEFORE surfacing.
    # The sidecar file is read by Cursor Agent at packet-construction time. This is
    # the closure of the meta-learning feedback loop: stored precedent -> new
    # packet. Emit a PRECEDENT_AVAILABLE banner on stderr so it is visible in
    # the hook output the model sees on the next turn.
    precedent_matches = consult_precedent(matched, snap)
    if precedent_matches:
        top = precedent_matches[0]
        print(
            f"PRECEDENT_AVAILABLE: matches={len(precedent_matches)} "
            f"strongest={top.get('strength','?')} "
            f"decision_id={top.get('decision_id','?')} "
            f"sidecar={PRECEDENT_SIDECAR_PATH} "
            f"(Cursor Agent: include this precedent block in the AUTHOR-GATE DECISION header)",
            file=sys.stderr,
        )

    enforcement = str(cfg.get("enforcement", "block")).lower()
    if enforcement == "shadow":
        # Record the would-block event without exiting 2; hook chain proceeds.
        fingerprint = snap.fingerprint()
        append_violation(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "severity": "shadow_warn",
                "enforcement": "shadow",
                "fingerprint": fingerprint,
                "triggers": [m["id"] for m in matched],
                "files": sorted(set(snap.changed_files + snap.deleted_files))[:50],
                "precedent_matches": len(precedent_matches),
            }
        )
        print(
            f"[pre_author_gate] SHADOW — would AUTHOR_GATE_REQUIRED "
            f"triggers={','.join(m['id'] for m in matched)} "
            f"fingerprint={fingerprint} precedent={len(precedent_matches)} "
            f"(enforcement=shadow; not blocking)",
            file=sys.stderr,
        )
        # Also reset consecutive_denials in shadow mode — we aren't actually denying
        reset_consecutive_on_pass(session)
        return 0

    return emit_author_gate_required(matched, snap, session, defaults)


if __name__ == "__main__":
    sys.exit(main())
