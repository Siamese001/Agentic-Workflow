"""Orchestrator for `notion-backlog-residual-cleanup-c3d8f2` plan.

Executes all 5 waves and registers progress in Notion.

Wave A: Apply 4 valid Pass 1 scores
Wave B: Investigate 4 questionable scores (auto-decide)
Wave C: Rewrite 3 PARTIAL Blocking Items
Wave D: Extract embedded [Pn] bands from 68 unscorable
Wave E: git push origin main

Plus:
- POST plan to Plans DB
- POST + PATCH 5 wave summary rows to Wave/Phase Convergence DB
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOKEN = os.environ.get("NOTION_TOKEN")
VERSION = "2025-09-03"

PLANS_DB = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
WPC_DB = "aa8d2507-101e-4384-81d9-60ea3fe33876"
RECEIPTS = ROOT / "artifacts" / "notion" / "_writeback_receipts.jsonl"
PLAN_SLUG = "notion-backlog-residual-cleanup-c3d8f2"
PLAN_FILE = ".windsurf/plans/notion-backlog-residual-cleanup-c3d8f2.md"

ROWS = json.loads((ROOT / "artifacts/notion/open_rows_with_ids.json").read_text(encoding="utf-8"))
RESCORE = json.loads((ROOT / "artifacts/notion/_pending_rescore.json").read_text(encoding="utf-8"))
ADG_DB = ROOT / "artifacts/adg/adg_indexed_04242026_0513.sqlite"


def http(method, url, body=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _rt(s, max_len=2000):
    return {"rich_text": [{"type": "text", "text": {"content": s[:max_len]}}]}


def _title(s, max_len=200):
    return {"title": [{"type": "text", "text": {"content": s[:max_len]}}]}


def receipt(op, page_id, ok, **extra):
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "op": op,
        "page_id": page_id,
        "ok": ok,
        **extra,
    }
    with RECEIPTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# ---- Plans DB registration ------------------------------------------------


def register_plan() -> str:
    """POST a Plans DB row for this plan. Returns page_id."""
    body = {
        "parent": {"type": "database_id", "database_id": PLANS_DB},
        "properties": {
            "Plan Name": _title(f"notion-backlog-residual-cleanup-c3d8f2"),
            "Plan File Path": _rt(PLAN_FILE),
            "Status": {"select": {"name": "Not Started"}},
            "Exists On Disk": {"checkbox": True},
        },
    }
    try:
        r = http("POST", "https://api.notion.com/v1/pages", body)
        receipt("POST-plan-register", r["id"], True, slug=PLAN_SLUG)
        print(f"[plan] registered: {r['id']}")
        return r["id"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        print(f"[plan] registration failed (will continue): {detail[:200]}", file=sys.stderr)
        receipt("POST-plan-register", None, False, detail=detail[:300])
        return ""


# ---- Wave A ---------------------------------------------------------------

WAVE_A_TARGETS = {
    # phase -> (proposed_band, impact, layer, fan_in, surface)
    ("W2-P1", "2.1"): ("P1", 384.5, "L0", 3, "State"),
    ("F4", "F4.2"): ("P2", 156.1, "L_TOOLS", 1, "State"),
    ("W3", "P3.1"): ("P3", 130.0, "L_UNKNOWN", 0, "Execution"),
    ("W4", "W4"): ("P3", 120.0, "L_APP", 0, "State"),
}


def find_row(wave: str, phase: str) -> dict | None:
    for r in ROWS:
        if r["wave"] == wave and r["phase"] == phase:
            return r
    return None


def wave_a():
    print("\n=== Wave A: Apply 4 valid Pass 1 scores ===")
    done = 0
    for (wave, phase), (band, impact, layer, fan_in, surface) in WAVE_A_TARGETS.items():
        row = find_row(wave, phase)
        if not row:
            print(f"  [SKIP] {wave}/{phase}: row not found")
            continue
        note = (
            f"RESCORED 2026-04-24 (Wave A of {PLAN_SLUG}): band={band} impact={impact} "
            f"layer={layer} fan_in={fan_in} surface={surface}. "
            f"Source: artifacts/notion/_pending_rescore.json. "
            f"Original: {row.get('blocking', '')[:300]}"
        )
        body = {
            "properties": {
                "P-Band": {"select": {"name": band}},
                "Impact Score": {"number": impact},
                "Blocking Items": _rt(note),
            }
        }
        try:
            http("PATCH", f"https://api.notion.com/v1/pages/{row['id']}", body)
            receipt("PATCH-pass1-valid", row["id"], True, wave=wave, phase=phase, band=band)
            done += 1
            print(f"  [{done}/4] {wave}/{phase} -> {band} (impact {impact})")
        except urllib.error.HTTPError as e:
            detail = e.read().decode()
            receipt("PATCH-pass1-valid", row["id"], False, detail=detail[:300])
            print(f"  [FAIL] {wave}/{phase}: {detail[:200]}", file=sys.stderr)
    return done


# ---- Wave B ---------------------------------------------------------------

WAVE_B_DECISIONS = {
    # phase -> (action, note)
    # action: 'descope', 'unscored', 'apply' (with computed values)
    "GAP-4": (
        "unscored",
        "INVESTIGATED 2026-04-24 (Wave B): naive scorer matched _constants.py too broadly "
        "(fan_in=257 across many _constants.py files in the repo). The real target is "
        "L5_safety/config/structure_blueprint/_constants.py per plan slug 'streamline-constants'. "
        "Decision: leave UNSCORED until plan author specifies the exact target file in Files In Scope.",
    ),
    "5.1": (
        "unscored",
        "INVESTIGATED 2026-04-24 (Wave B): row is an action ('Post-W4 resnapshot'), not file-work. "
        "Naive scorer matched a debug script. Decision: leave UNSCORED — actions don't take P-bands. "
        "Action item: run python tools/generate_full_adg.py once W4 lands, then descope.",
    ),
    "3.2": (
        "unscored",
        "INVESTIGATED 2026-04-24 (Wave B): naive scorer matched literal 'init.py' token. Real targets "
        "are __init__.py files in the structure_blueprint_config retirement scope (ref: parent plan "
        "structure-blueprint-config-retirement-*.md). Decision: leave UNSCORED until parent plan "
        "lists exact __init__.py files in Files In Scope.",
    ),
    "1.2": (
        "apply",
        "INVESTIGATED 2026-04-24 (Wave B): scorer computed impact=0 because tests mirror exists for "
        "EmbeddingSovereignAgent. However, work is to ADD ValueError handlers (a guardrail addition), "
        "not test coverage. Coverage-gap-based scoring underweights guardrail additions. "
        "Decision: assign P3 manually (L2 layer, fan_in=5 callers, Execution surface). Impact: ~50.",
    ),
}

WAVE_B_PHASE_TO_WAVE = {
    "GAP-4": "GAP",
    "5.1": "W5",
    "3.2": "Wave 3",
    "1.2": "W1-P0",
}


def wave_b():
    print("\n=== Wave B: Investigate 4 questionable scores ===")
    decisions = {}
    done = 0
    for phase, (action, note) in WAVE_B_DECISIONS.items():
        wave = WAVE_B_PHASE_TO_WAVE[phase]
        row = find_row(wave, phase)
        if not row:
            print(f"  [SKIP] {wave}/{phase}: not found")
            continue
        if action == "unscored":
            body = {"properties": {"Blocking Items": _rt(note)}}
            try:
                http("PATCH", f"https://api.notion.com/v1/pages/{row['id']}", body)
                receipt("PATCH-pass1-investigate", row["id"], True, wave=wave, phase=phase, action="unscored")
                decisions[f"{wave}/{phase}"] = "unscored"
                done += 1
                print(f"  [{done}/4] {wave}/{phase} -> UNSCORED (note added)")
            except urllib.error.HTTPError as e:
                detail = e.read().decode()
                receipt("PATCH-pass1-investigate", row["id"], False, detail=detail[:300])
                print(f"  [FAIL] {wave}/{phase}: {detail[:200]}", file=sys.stderr)
        elif action == "apply":
            body = {
                "properties": {
                    "P-Band": {"select": {"name": "P3"}},
                    "Impact Score": {"number": 50.0},
                    "Blocking Items": _rt(note),
                }
            }
            try:
                http("PATCH", f"https://api.notion.com/v1/pages/{row['id']}", body)
                receipt(
                    "PATCH-pass1-investigate",
                    row["id"],
                    True,
                    wave=wave,
                    phase=phase,
                    action="apply",
                    band="P3",
                )
                decisions[f"{wave}/{phase}"] = "apply P3"
                done += 1
                print(f"  [{done}/4] {wave}/{phase} -> P3 (manual override, impact 50)")
            except urllib.error.HTTPError as e:
                detail = e.read().decode()
                receipt("PATCH-pass1-investigate", row["id"], False, detail=detail[:300])
                print(f"  [FAIL] {wave}/{phase}: {detail[:200]}", file=sys.stderr)
    (ROOT / "artifacts/notion/_wave_b_decisions.json").write_text(
        json.dumps(decisions, indent=2), encoding="utf-8"
    )
    return done


# ---- Wave C ---------------------------------------------------------------

WAVE_C_REWRITES = {
    ("W2", "2.8"): (
        "PARTIAL (audited 2026-04-24): rule files exist (`author-gate-svp-calibration.md`, "
        "`hitl-svp-calibration.md`, `judge-calibration-cadence.md`); GAP: not referenced in "
        "constitutional.md. Promote to Done by adding §-reference in constitutional, or descope "
        "if HITL SVP calibration intentionally lives only in conditional rules."
    ),
    ("W2", "2.2"): (
        "PARTIAL (audited 2026-04-24): keyword 'cleanup' too generic for filesystem verification. "
        "Plan author should restate scope in concrete terms (which policy file, what cleanup) before "
        "this row can be promoted to Done or descoped."
    ),
    ("W2", "2.5"): (
        "PARTIAL (audited 2026-04-24): gate `ops_scripts/ci/check_mcp_sync_integrity.py` exists "
        "(covers 'check' keyword) but row title doesn't name a specific version-check mechanism. "
        "Likely covered by sync_integrity gate; verify intent and either close as Done or restate "
        "the version-check requirement (e.g., MCP SDK version pinning, server-version compat)."
    ),
}


def wave_c():
    print("\n=== Wave C: Rewrite 3 PARTIAL Blocking Items ===")
    done = 0
    for (wave, phase), note in WAVE_C_REWRITES.items():
        row = find_row(wave, phase)
        if not row:
            print(f"  [SKIP] {wave}/{phase}: not found")
            continue
        body = {"properties": {"Blocking Items": _rt(note)}}
        try:
            http("PATCH", f"https://api.notion.com/v1/pages/{row['id']}", body)
            receipt("PATCH-partial-rewrite", row["id"], True, wave=wave, phase=phase)
            done += 1
            print(f"  [{done}/3] {wave}/{phase} rewritten")
        except urllib.error.HTTPError as e:
            detail = e.read().decode()
            receipt("PATCH-partial-rewrite", row["id"], False, detail=detail[:300])
            print(f"  [FAIL] {wave}/{phase}: {detail[:200]}", file=sys.stderr)
    return done


# ---- Wave D ---------------------------------------------------------------

BAND_RE = re.compile(r"\[(P[1-5])\]")


def wave_d():
    print("\n=== Wave D: Band-extraction for 68 unscorable rows ===")
    unscorable = [r for r in RESCORE if r.get("proposed_band") == "UNSCORABLE"]
    print(f"  Examining {len(unscorable)} unscorable rows...")
    targets = []
    for r in unscorable:
        match = BAND_RE.search(r["title"])
        if match:
            targets.append((r["id"], r["wave"], r["phase"], r["title"], match.group(1)))
    print(f"  Found embedded [Pn] band in {len(targets)} rows")
    done = 0
    for page_id, wave, phase, title, band in targets:
        note = (
            f"BAND-EXTRACTED 2026-04-24 (Wave D of {PLAN_SLUG}): band={band} extracted from title "
            f"prefix. Impact score not computed (preserves human-assigned priority intent). "
            f"Original title: {title[:200]}"
        )
        body = {
            "properties": {
                "P-Band": {"select": {"name": band}},
                "Blocking Items": _rt(note),
            }
        }
        try:
            http("PATCH", f"https://api.notion.com/v1/pages/{page_id}", body)
            receipt("PATCH-band-extracted", page_id, True, wave=wave, phase=phase, band=band)
            done += 1
            if done % 10 == 0:
                print(f"  [{done}/{len(targets)}] ...")
        except urllib.error.HTTPError as e:
            detail = e.read().decode()
            receipt("PATCH-band-extracted", page_id, False, detail=detail[:300])
            print(f"  [FAIL] {page_id}: {detail[:200]}", file=sys.stderr)
    print(f"  Done: {done}/{len(targets)} band extractions applied")
    return done


# ---- Wave E ---------------------------------------------------------------


def wave_e():
    print("\n=== Wave E: git push origin main ===")
    try:
        r = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        if r.returncode == 0:
            receipt("git-push", "origin/main", True, stdout=r.stdout[:300], stderr=r.stderr[:300])
            return 1
        else:
            receipt("git-push", "origin/main", False, returncode=r.returncode, stderr=r.stderr[:500])
            return 0
    except (subprocess.TimeoutExpired, OSError) as e:
        receipt("git-push", "origin/main", False, error=str(e))
        print(f"  [FAIL] git push: {e}", file=sys.stderr)
        return 0


# ---- Summary rows in Wave/Phase Convergence -----------------------------


def post_wave_summary(wave_letter: str, label: str, scope: str, est_tokens: int, status: str, results: str):
    body = {
        "parent": {"type": "database_id", "database_id": WPC_DB},
        "properties": {
            "Phase Title": _title(f"[META] Wave {wave_letter} — {label}"),
            "Phase ID": _rt(f"Wave-{wave_letter}"),
            "Wave ID": _rt("RESIDUAL-CLEANUP"),
            "Sub-Wave": _rt(f"RESIDUAL-{wave_letter}-CORE"),
            "Plan File": _rt(PLAN_FILE),
            "Parent Plan Summary": _rt(
                f"notion-backlog-residual-cleanup-c3d8f2: 5-wave residual cleanup of Wave/Phase "
                f"Convergence DB. Wave A=apply valid scores, B=investigate questionable, "
                f"C=rewrite PARTIAL, D=band-extraction, E=git push."
            ),
            "Success Criteria": _rt(scope),
            "Files In Scope": _rt("artifacts/notion/*.json, tools/debug/_residual_cleanup_orchestrator.py"),
            "Dependencies": _rt("Pass 1/Pass 2 dry-run output (artifacts/notion/_pending_*.json)"),
            "Blocking Items": _rt(f"COMPLETED 2026-04-24: {results}"),
            "Status": {"select": {"name": status}},
            "Est Tokens": {"number": est_tokens},
        },
    }
    try:
        r = http("POST", "https://api.notion.com/v1/pages", body)
        receipt("POST-residual-summary", r["id"], True, wave=wave_letter, label=label)
        print(f"  [summary] Wave {wave_letter} row posted: {r['id']}")
        return r["id"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        receipt("POST-residual-summary", None, False, detail=detail[:300])
        print(f"  [FAIL] summary {wave_letter}: {detail[:200]}", file=sys.stderr)
        return ""


# ---- Main -----------------------------------------------------------------


def main():
    if not TOKEN:
        print("NOTION_TOKEN missing", file=sys.stderr)
        return 1

    print(f"Orchestrator: {PLAN_SLUG}")
    print(f"Receipts: {RECEIPTS}")

    # Register plan
    register_plan()

    # Execute all waves
    a_done = wave_a()
    b_done = wave_b()
    c_done = wave_c()
    d_done = wave_d()
    e_done = wave_e()

    # Post summary rows for each wave
    print("\n=== Posting wave summary rows ===")
    post_wave_summary(
        "A",
        "Apply 4 valid Pass 1 scores",
        "4 PATCHes with computed P-Band + Impact Score",
        2000,
        "Done",
        f"{a_done}/4 PATCHes applied. See _writeback_receipts.jsonl op=PATCH-pass1-valid.",
    )
    post_wave_summary(
        "B",
        "Investigate 4 questionable scores",
        "Per-row decisions documented; 3 unscored, 1 manual P3 override",
        6000,
        "Done",
        f"{b_done}/4 decisions applied. See _wave_b_decisions.json + receipts op=PATCH-pass1-investigate.",
    )
    post_wave_summary(
        "C",
        "Rewrite 3 PARTIAL Blocking Items",
        "3 rewrites with explicit gap text",
        3000,
        "Done",
        f"{c_done}/3 PATCHes applied. See receipts op=PATCH-partial-rewrite.",
    )
    post_wave_summary(
        "D",
        "Band-extraction for 68 unscorable",
        "Regex extract [Pn] from titles, PATCH P-Band, no impact recomputation",
        8000,
        "Done",
        f"{d_done} band extractions applied. See receipts op=PATCH-band-extracted.",
    )
    post_wave_summary(
        "E",
        "Push to origin/main",
        "git push origin main",
        1000,
        "Done" if e_done else "Blocked",
        f"{'Pushed successfully' if e_done else 'Push failed; check stderr in receipts'}.",
    )

    print(f"\n=== ORCHESTRATOR COMPLETE ===")
    print(f"Wave A: {a_done}/4")
    print(f"Wave B: {b_done}/4")
    print(f"Wave C: {c_done}/3")
    print(f"Wave D: {d_done} band extractions")
    print(f"Wave E: {'PUSHED' if e_done else 'FAILED'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
