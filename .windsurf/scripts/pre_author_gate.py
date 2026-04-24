#!/usr/bin/env python3
"""
pre_author_gate.py — Author-Gate trigger gate (developer-loop / harness-side).

Invoked via .windsurf/hooks.json on pre_write_code. Evaluates observable
features of the pending action against .windsurf/schemas/author_gate_triggers.yaml.
When a trigger fires AND no active author-gate decision matches the current
context fingerprint, emits AUTHOR_GATE_REQUIRED and blocks the write.

Not the same as runtime HITL — that lives in agentic_core/L5_safety/ per ADR-023.

Deny-and-continue semantics (Anthropic Auto Mode):
    - Exit 2 with structured AUTHOR_GATE_REQUIRED marker (back-compat alias HITL_REQUIRED also emitted)
    - Increments consecutive + total denial counters in author_gate_session_state.json
    - After N consecutive (default 3) or M cumulative (default 20) denials,
      escalates to a hard halt and writes a severity=critical violation row

Fresh invocation modes:
    python .windsurf/scripts/pre_author_gate.py                 # hook mode
    python .windsurf/scripts/pre_author_gate.py --self-test     # validate triggers.yaml
    python .windsurf/scripts/pre_author_gate.py --dry-run       # evaluate without exiting 2
    python .windsurf/scripts/pre_author_gate.py --reset-session # clear denial counters

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
TRIGGERS_PATH = REPO_ROOT / ".windsurf" / "schemas" / "author_gate_triggers.yaml"
LEDGER_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
STATE_DIR = REPO_ROOT / "artifacts" / "windsurf"
SESSION_STATE_PATH = STATE_DIR / "author_gate_session_state.json"
VIOLATIONS_PATH = STATE_DIR / "author_gate_violations.jsonl"
# W2.2 — precedent sidecar: cleared at gate-pass, written at gate-fire.
# Cascade reads this file at packet-construction time and includes the matches
# in the AUTHOR-GATE DECISION header. Format: dict from lookup_refactor_decisions.
PRECEDENT_SIDECAR_PATH = STATE_DIR / "author_gate_precedent.json"
LOOKUP_SKILL_PATH = REPO_ROOT / ".windsurf" / "skills" / "refactor-decision-memory" / "lookup_refactor_decisions.py"

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
    """Persist precedent lookup result for Cascade to read when building the packet."""
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


def check_tier(cfg: dict[str, Any], snap: ChangeSnapshot) -> str:
    """Return 'tier_1', 'tier_2', or 'tier_3'. Tier 1/2 → skip gate."""
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


def _layers_in_changed_files(files: list[str]) -> set[str]:
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


def evaluate_trigger(trg: dict[str, Any], snap: ChangeSnapshot) -> bool:
    feats = trg.get("features", {})

    if "files_changed_min" in feats and snap.files_changed < feats["files_changed_min"]:
        return False

    if "deletions_min" in feats and len(snap.deleted_files) < feats["deletions_min"]:
        return False

    if feats.get("layer_crossing") is True:
        layers = _layers_in_changed_files(snap.changed_files + snap.deleted_files)
        if len(layers) < 2:
            return False
    elif feats.get("layer_crossing") is False and "files_changed_min" in feats:
        layers = _layers_in_changed_files(snap.changed_files + snap.deleted_files)
        if len(layers) >= 2:
            return False  # this rule is for single-layer large changes

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
        if evaluate_trigger(trg, snap):
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
    # The sidecar file is read by Cascade at packet-construction time. This is
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
            f"(Cascade: include this precedent block in the AUTHOR-GATE DECISION header)",
            file=sys.stderr,
        )

    enforcement = str(cfg.get("enforcement", "shadow")).lower()
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
