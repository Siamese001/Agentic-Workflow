#!/usr/bin/env python3
"""
post_commit_phase_closer.py — auto-flip Notion Wave/Phase Convergence rows to
Status=Done when a git commit ships a phase/wave completion.

Triggers: runs as a git post-commit hook. Also supports a backfill mode that
walks `git log` from a SHA (or last N commits) and re-runs detection.

Detection (commit subject + body — all matches extracted):
    1. Explicit marker:   PHASE_CLOSED: plan=<slug> ... phase=<id>
    2. Subject prefix:    ^<PHASE_ID>(-closure)?:.*\\b(complete|closure|land|ship|full|done)\\b
       (PHASE_ID shapes: W1.2, LJH1.1, RH6B.2, PRF1.A2, adg-ci-W7.1)
    3. Multi-phase prefix: RH6B.1/2: ... → [RH6B.1, RH6B.2]

For each detected Phase ID:
    - Query Wave/Phase Convergence (data_source_id fc7f6bf4-...) via Notion REST
      with filter `Phase ID contains <id>`
    - If row exists AND Status != Done: PATCH Status → Done + record evidence
      (commit SHA) into Blocking Items
    - Idempotent: skip if already Done
    - Dedupe: if multiple rows match, patch the open one with highest Impact Score

Requirements:
    - NOTION_TOKEN env var
    - stdlib only (urllib.request, no external deps)
    - Python 3.11+

Fail policy: OPEN — any error → log + exit 0. Must never block a commit.
Bypass: PHASE_CLOSER_BYPASS=1 → log + exit 0.

Audit log: artifacts/governance/phase_close_audit.jsonl (one JSON line per patch/skip)

CLI:
    python post_commit_phase_closer.py                    # current HEAD
    python post_commit_phase_closer.py --backfill=20      # last 20 commits
    python post_commit_phase_closer.py --backfill-from=abcdef  # since SHA
    python post_commit_phase_closer.py --dry-run          # detect only, no patch
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_LOG = REPO_ROOT / "artifacts" / "governance" / "phase_close_audit.jsonl"

import sys as _sys

_sys.path.insert(0, str(Path(__file__).resolve().parent))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    WAVE_PHASE_DATA_SOURCE_ID,
)

# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# Phase ID with sub-number, e.g. LJH1.1, W7.1, RH6B.2, PRF1.A2, adg-ci-W7.1
PHASE_ID_WITH_SUB_RE = r"[A-Za-z][A-Za-z\-]*\d+[A-Z]?(?:\.[A-Z]?\d+)+"
# Wave ID (no sub), e.g. LJH, W4, RH6B, PRF1
WAVE_ID_RE = r"[A-Za-z][A-Za-z\-]*(?:\d+[A-Z]?)?"

EXPLICIT_MARKER_RE = re.compile(
    r"PHASE_CLOSED:\s*(?:[^\n]*?\bphase=)(" + PHASE_ID_WITH_SUB_RE + r")",
    re.IGNORECASE,
)

# Subject-line prefix — supports multi-phase like RH6B.1/2 and bare waves like LJH
# Alt form: `wave C.3:` / `phase H5:` — prefix words `wave`/`phase` + ID
SUBJECT_PREFIX_RE = re.compile(
    r"^(?:(?:wave|phase)\s+)?"
    r"(?P<prefix>(?:"
    + PHASE_ID_WITH_SUB_RE
    + r")(?:/\d+(?:\.\d+)?)*|"
    + WAVE_ID_RE
    + r")(?:-closure)?:\s+(?P<subject_rest>.*)$",
    re.IGNORECASE | re.MULTILINE,
)

# Expanded completion verb list. Includes phase-closure idioms used in this repo:
# archive (dead code), wire/wired/wiring (adoption), fold/folded (consolidation),
# seed/seeded (fixture/dataset), adopt/adopted/adoption (rollout),
# merge/merged (SSOT merge), migrate/migrated/migration, promote/promoted/promotion,
# consolidate/consolidated, harden/hardened/hardening (security), flip/flipped (mode change).
# Deliberately EXCLUDED — too generic, cause false positives: add, update, implement, fix.
COMPLETION_RE = re.compile(
    r"\b(?:"
    r"complete(?:d|s)?|closure|closed|land(?:ed|s)?|ship(?:ped|s)?|full|done|"
    r"finalis[ez]ed?|finish(?:ed|es)?|"
    r"archiv(?:e|ed|es|ing)|"
    r"wir(?:e|ed|es|ing)|"
    r"fold(?:ed|ing)?|"
    r"seed(?:ed|ing)?|"
    r"adopt(?:ed|ing|ion)?|"
    r"merg(?:e|ed|es|ing)|"
    r"migrat(?:e|ed|es|ing|ion)|"
    r"promot(?:e|ed|es|ing|ion)|"
    r"consolidat(?:e|ed|es|ing|ion)|"
    r"harden(?:ed|ing)?|"
    r"flip(?:ped|s|ping)?|"
    r"remediat(?:e|ed|ion)"
    r")\b",
    re.IGNORECASE,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(record: dict[str, Any]) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    record.setdefault("ts", _utc_now_iso())
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Phase-ID extraction
# ---------------------------------------------------------------------------


def extract_completion_targets(commit_msg: str) -> dict[str, list[str]]:
    """Extract completion targets. Returns {"phases": [...], "waves": [...]}.

    Rules (all require a completion verb somewhere in the full message):
      1. Explicit PHASE_CLOSED marker → phases
      2. Subject prefix matching PHASE_ID with sub (e.g. W7.1, LJH1.1) → phases
         Multi-phase like RH6B.1/2 → expanded
      3. Subject prefix matching bare wave (e.g. LJH, W4) → waves
         (caller expands via Notion query to close all open phases in wave)
    """
    phases: set[str] = set()
    waves: set[str] = set()

    # Rule 1: explicit markers don't need completion verb
    for m in EXPLICIT_MARKER_RE.finditer(commit_msg):
        phases.add(m.group(1))

    has_completion = bool(COMPLETION_RE.search(commit_msg))
    if not has_completion:
        return {"phases": sorted(phases), "waves": sorted(waves)}

    # Rules 2 + 3: subject-line prefix
    first_line = commit_msg.split("\n", 1)[0]
    subj_match = SUBJECT_PREFIX_RE.match(first_line)
    if subj_match:
        prefix = subj_match.group("prefix")
        # Multi-phase: "RH6B.1/2" → ["RH6B.1", "RH6B.2"]
        if "/" in prefix:
            base_match = re.match(r"^(.+?\.)(\d+)((?:/\d+)+)$", prefix)
            if base_match:
                base = base_match.group(1)
                phases.add(f"{base}{base_match.group(2)}")
                for n in base_match.group(3).lstrip("/").split("/"):
                    phases.add(f"{base}{n}")
            else:
                phases.add(prefix)
        elif re.match(PHASE_ID_WITH_SUB_RE + r"$", prefix):
            phases.add(prefix)
        else:
            # Bare wave ID (no dot) — gated to prevent over-fanout via starts_with:
            # 1. Must be ≥4 chars (e.g. LJH1, RH6B, PRF1) OR ≥3 uppercase letters (LJH, PRF)
            #    → rejects W1, W2, E1, P2 which fan out to unrelated W10+, E10+ etc.
            # 2. Pure-alpha IDs with no digits need ≥3 uppercase letters (e.g. LJH, PRF)
            #    → rejects short hyphenated forms
            has_digit = bool(re.search(r"\d", prefix))
            is_long_alpha = bool(re.match(r"^[A-Z]{3,}$", prefix))
            is_long_with_digit = has_digit and len(prefix) >= 4
            if is_long_alpha or is_long_with_digit:
                waves.add(prefix)

    return {"phases": sorted(phases), "waves": sorted(waves)}


# Back-compat alias (simpler call site when caller just wants phases)
def extract_phase_ids(commit_msg: str) -> list[str]:
    return extract_completion_targets(commit_msg)["phases"]


# ---------------------------------------------------------------------------
# Git access
# ---------------------------------------------------------------------------


def _run_git(args: list[str]) -> str:
    """Run git with safe defaults. Returns stdout (stripped) or empty on error."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        _log({"event": "git_error", "args": args, "error": str(exc)})
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_commit_messages(ref_range: str | None = None, count: int | None = None) -> list[tuple[str, str]]:
    """Return [(sha, full_message), ...]."""
    sep = "<<<PHCLOSER_SEP>>>"
    git_args = ["log", f"--format=%H%n%B{sep}"]
    if count is not None:
        git_args.append(f"-{count}")
    if ref_range:
        git_args.append(ref_range)
    out = _run_git(git_args)
    if not out:
        return []
    results: list[tuple[str, str]] = []
    for chunk in out.split(sep):
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split("\n", 1)
        sha = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        if len(sha) >= 7 and re.match(r"^[0-9a-f]+$", sha):
            results.append((sha, body))
    return results


# ---------------------------------------------------------------------------
# Notion API (stdlib urllib, no deps)
# ---------------------------------------------------------------------------


def _notion_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }


def _notion_request(method: str, path: str, token: str, body: dict | None = None) -> dict | None:
    url = f"{NOTION_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=_notion_headers(token))
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            parsed: Any = json.loads(resp.read().decode("utf-8"))
            return parsed if isinstance(parsed, dict) else None
    except urllib.error.HTTPError as exc:
        _log(
            {
                "event": "notion_http_error",
                "method": method,
                "path": path,
                "status": exc.code,
                "body": exc.read().decode("utf-8", errors="replace")[:500],
            }
        )
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        _log({"event": "notion_net_error", "method": method, "path": path, "error": str(exc)})
        return None


def query_phase_rows(phase_id: str, token: str) -> list[dict]:
    """Return all Wave/Phase rows whose Phase ID exactly matches."""
    body = {
        "filter": {"property": "Phase ID", "rich_text": {"equals": phase_id}},
        "page_size": 10,
    }
    resp = _notion_request("POST", f"/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query", token, body)
    if resp is None:
        return []
    results = resp.get("results", [])
    return [r for r in results if isinstance(r, dict)]


def query_wave_rows(wave_id: str, token: str) -> list[dict]:
    """Return Wave/Phase rows whose Wave ID starts with the wave prefix.

    A commit like 'LJH: complete...' should fan out to Wave IDs LJH1, LJH2, ...
    """
    body = {
        "filter": {"property": "Wave ID", "rich_text": {"starts_with": wave_id}},
        "page_size": 100,
    }
    resp = _notion_request("POST", f"/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query", token, body)
    if resp is None:
        return []
    results = resp.get("results", [])
    return [r for r in results if isinstance(r, dict)]


def _get_status(row: dict) -> str | None:
    sel = row.get("properties", {}).get("Status", {}).get("select") or {}
    return sel.get("name")


def _get_impact(row: dict) -> float:
    return float(row.get("properties", {}).get("Impact Score", {}).get("number") or 0.0)


def patch_row_done(page_id: str, commit_sha: str, token: str, existing_blocking: str = "") -> bool:
    evidence_line = (
        f"\n[AUTO-CLOSE {datetime.now(timezone.utc).strftime('%Y-%m-%d')}] commit={commit_sha[:12]}"
    )
    new_blocking = (existing_blocking + evidence_line).strip()[:2000]
    body = {
        "properties": {
            "Status": {"select": {"name": "Done"}},
            "Blocking Items": {"rich_text": [{"type": "text", "text": {"content": new_blocking}}]},
        }
    }
    resp = _notion_request("PATCH", f"/pages/{page_id}", token, body)
    return resp is not None


# ---------------------------------------------------------------------------
# Core: process a single commit
# ---------------------------------------------------------------------------


def _close_rows_for_target(
    target_label: str,
    rows: list[dict],
    sha: str,
    token: str,
    dry_run: bool,
    result: dict[str, Any],
    close_all_open: bool,
) -> None:
    """Close matching rows. If close_all_open, close every open row (wave mode).
    Otherwise close only the highest-impact open row (phase mode)."""
    if not rows:
        result["not_found"].append(target_label)
        return
    open_rows = [r for r in rows if _get_status(r) != "Done"]
    if not open_rows:
        result["skipped_already_done"].append(target_label)
        return
    targets = open_rows if close_all_open else [max(open_rows, key=_get_impact)]
    for target in targets:
        page_id = target["id"]
        phase_id_rt = target.get("properties", {}).get("Phase ID", {}).get("rich_text") or []
        actual_phase = "".join(t.get("plain_text", "") for t in phase_id_rt) or target_label
        if dry_run:
            result["patched"].append(
                {"phase_id": actual_phase, "page_id": page_id, "via": target_label, "dry_run": True}
            )
            continue
        existing_blocking = ""
        rt = target.get("properties", {}).get("Blocking Items", {}).get("rich_text") or []
        if rt:
            existing_blocking = "".join(t.get("plain_text", "") for t in rt)
        ok = patch_row_done(page_id, sha, token, existing_blocking)
        if ok:
            result["patched"].append({"phase_id": actual_phase, "page_id": page_id, "via": target_label})
        else:
            result["errors"].append({"phase_id": actual_phase, "page_id": page_id, "via": target_label})


def process_commit(sha: str, msg: str, token: str, dry_run: bool = False) -> dict[str, Any]:
    targets = extract_completion_targets(msg)
    result: dict[str, Any] = {
        "event": "commit_processed",
        "sha": sha[:12],
        "phase_ids": targets["phases"],
        "wave_ids": targets["waves"],
        "patched": [],
        "skipped_already_done": [],
        "not_found": [],
        "errors": [],
    }
    if not targets["phases"] and not targets["waves"]:
        result["event"] = "commit_no_targets"
        return result

    # Phase-level closures — single row per phase (highest-impact open)
    for pid in targets["phases"]:
        rows = query_phase_rows(pid, token) if not dry_run else []
        if dry_run:
            result["patched"].append({"phase_id": pid, "dry_run": True, "via": "phase"})
            continue
        _close_rows_for_target(pid, rows, sha, token, dry_run, result, close_all_open=False)

    # Wave-level closures — close ALL open phases in the wave
    for wid in targets["waves"]:
        rows = query_wave_rows(wid, token) if not dry_run else []
        if dry_run:
            result["patched"].append({"wave_id": wid, "dry_run": True, "via": "wave"})
            continue
        _close_rows_for_target(wid, rows, sha, token, dry_run, result, close_all_open=True)

    return result


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--backfill", type=int, default=None, help="Process last N commits")
    parser.add_argument(
        "--backfill-from", type=str, default=None, help="Process commits since SHA (exclusive)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Detect only, no Notion writes")
    args = parser.parse_args()

    if os.environ.get("PHASE_CLOSER_BYPASS") == "1":
        _log({"event": "bypass", "reason": "PHASE_CLOSER_BYPASS=1"})
        return 0

    token = os.environ.get("NOTION_TOKEN", "").strip()
    if not token and not args.dry_run:
        _log({"event": "no_token", "msg": "NOTION_TOKEN not set — skipping (use --dry-run to test)"})
        print("post_commit_phase_closer: NOTION_TOKEN not set, skipping", file=sys.stderr)
        return 0

    # Determine commit range
    if args.backfill_from:
        commits = get_commit_messages(ref_range=f"{args.backfill_from}..HEAD")
    elif args.backfill:
        commits = get_commit_messages(count=args.backfill)
    else:
        commits = get_commit_messages(count=1)

    if not commits:
        _log({"event": "no_commits"})
        return 0

    print(f"post_commit_phase_closer: {len(commits)} commit(s) to scan", file=sys.stderr)
    summary = {"total": len(commits), "patched": 0, "already_done": 0, "no_match": 0}

    for sha, msg in commits:
        result = process_commit(sha, msg, token, dry_run=args.dry_run)
        _log(result)
        summary["patched"] += len(result.get("patched", []))
        summary["already_done"] += len(result.get("skipped_already_done", []))
        summary["no_match"] += len(result.get("not_found", []))
        if result.get("patched") or result.get("skipped_already_done") or result.get("not_found"):
            print(
                f"  {sha[:12]}: patched={len(result['patched'])} "
                f"already_done={len(result['skipped_already_done'])} "
                f"not_found={len(result['not_found'])}",
                file=sys.stderr,
            )

    _log({"event": "run_summary", **summary, "dry_run": args.dry_run})
    print(
        f"post_commit_phase_closer: patched={summary['patched']} "
        f"already_done={summary['already_done']} no_match={summary['no_match']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
