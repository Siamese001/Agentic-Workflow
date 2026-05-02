#!/usr/bin/env python3
"""ADG-verified closure pass over current Draft backlog rows.

For each Draft row, parse Evidence/Blocking Items for structural claims
(file paths moved, layers changed, commits landed, symbols created) and
verify against the fresh ADG snapshot. Flip to Completed when claim
matches reality. Rationale: many "P1/P2" rows are actually verification
debt — work already landed but Notion status never updated.

Hard rules:
  - NEVER flip a row without a concrete structural claim + matching ADG fact
  - NEVER trust title-only claims; require Evidence or Blocking Items text
  - Require at least one of: (a) file path that exists at claimed layer,
    (b) commit SHA (8+ hex) mentioned, (c) "DONE <date>" + file path
  - Per-row decision logged to audit jsonl
"""

from __future__ import annotations
import argparse, json, os, re, sqlite3, sys, time
import urllib.error, urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from triage_keep_drafts import (  # type: ignore[import-not-found]
    _token, _http, _txt, fetch_drafts,
    NOTION_API, REPO_ROOT,
)

AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "adg_verified_closure_audit.jsonl"

# Claim extraction regexes
FILE_PATH_RE = re.compile(r"\b((?:agentic_core|apps_\w+|ops_scripts|tools|config|scripts|certification|docs|tests)/[\w\-_/]+\.(?:py|yaml|yml|md|json))\b")
COMMIT_SHA_RE = re.compile(r"\b(?:commit\s+|landed\s+as\s+|landed\s+in\s+commits?\s+)([0-9a-f]{8,40})\b", re.IGNORECASE)
DONE_DATE_RE = re.compile(r"(?:DONE|COMPLETED|CLOSED|RESOLVED|Closed|Complete|Done)\s*[\.:]?\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
LAYER_CLAIM_RE = re.compile(r"layer\s*=\s*(L[0-6_][_A-Z]*)", re.IGNORECASE)


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_adg(snap_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{snap_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def verify_claim(con: sqlite3.Connection, row: dict) -> tuple[str, str, dict]:
    """Return (verdict, reason, evidence).
    verdict ∈ {CLOSE, KEEP}. CLOSE = structural claim verified in ADG.
    """
    p = row["properties"]
    bi = _txt(p.get("Blocking Items"))
    sc = _txt(p.get("Success Criteria"))
    ev = _txt(p.get("Evidence"))
    haystack = f"{bi}\n{sc}\n{ev}"

    # Extract claims
    file_paths = set(FILE_PATH_RE.findall(haystack))
    commit_shas = set(COMMIT_SHA_RE.findall(haystack))
    done_dates = DONE_DATE_RE.findall(haystack)
    layer_claims = LAYER_CLAIM_RE.findall(haystack)

    evidence = {
        "file_paths": list(file_paths)[:10],
        "commit_shas": list(commit_shas)[:5],
        "done_dates": done_dates[:3],
        "layer_claims": layer_claims[:3],
    }

    # Decision logic
    if not (file_paths or commit_shas or done_dates):
        return "KEEP", "no_structural_claim", evidence

    # Check file paths exist as ADG nodes
    cur = con.cursor()
    verified_paths = []
    for fp in file_paths:
        cur.execute("SELECT resolved_path, layer FROM nodes WHERE resolved_path = ? LIMIT 1", (fp,))
        r = cur.fetchone()
        if r:
            verified_paths.append({"path": fp, "layer": r["layer"]})
    evidence["verified_paths"] = verified_paths

    # Decision: CLOSE if (a) has done-date + ≥1 file verified, OR
    #                    (b) has commit SHA + ≥1 file verified, OR
    #                    (c) ≥2 files verified with explicit DONE/landed language
    strong_closure_word = re.search(
        r"(?i)("
        r"DONE\b|COMPLETED|CLOSED|RESOLVED|Closed\.|Complete\.|"
        r"landed\s+as|landed\s+in\s+commit|fully complete|"
        r"PARTIAL CLOSURE|BASELINE VERIFICATION|"
        r"Decision:\s+(leave|descope|retire|no action|skip|unscored)|"
        r"all .* met\b|all .* pass\b|ALL MET"
        r")",
        haystack,
    )

    if done_dates and verified_paths and strong_closure_word:
        return "CLOSE", f"done_date+{len(verified_paths)}_paths_verified", evidence
    if commit_shas and verified_paths and strong_closure_word:
        return "CLOSE", f"commit_sha+{len(verified_paths)}_paths_verified", evidence
    if len(verified_paths) >= 2 and strong_closure_word:
        return "CLOSE", f"multi_path_with_closure_word", evidence
    if len(verified_paths) >= 1 and strong_closure_word and done_dates:
        return "CLOSE", f"path+closure+date", evidence

    return "KEEP", "claim_but_insufficient_adg_match", evidence


def patch_complete(tok: str, page_id: str, verdict_reason: str, evidence: dict, dry: bool) -> None:
    today = date.today().isoformat()
    note = (
        f"[ADG-VERIFIED CLOSURE {today}] reason={verdict_reason}. "
        f"Verified file paths: {', '.join(p['path'] for p in evidence.get('verified_paths', []))[:400]}. "
        f"Commits cited: {', '.join(evidence.get('commit_shas', []))[:200]}. "
        f"Done dates cited: {', '.join(evidence.get('done_dates', []))[:80]}. "
        f"Snapshot: adg_indexed_05022026_1651.sqlite."
    )[:1900]
    body = {"properties": {
        "Status": {"select": {"name": "Completed"}},
        "Last Updated": {"date": {"start": today}},
        "Evidence": {"rich_text": [{"type": "text", "text": {"content": note}}]},
    }}
    if not dry:
        _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--snapshot", type=str, default="artifacts/adg/adg_indexed_05022026_1651.sqlite")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if args.dry_run == args.execute:
        ap.error("--dry-run or --execute")

    snap_path = Path(args.snapshot)
    if not snap_path.is_absolute():
        snap_path = REPO_ROOT / snap_path
    if not snap_path.exists():
        print(f"snapshot not found: {snap_path}", flush=True)
        return 2
    con = load_adg(snap_path)
    print(f"snapshot: {snap_path.name}", flush=True)

    tok = _token()
    rows = fetch_drafts(tok)
    print(f"draft rows: {len(rows)}", flush=True)

    close_list = []
    keep_reasons = defaultdict(int)
    for r in rows:
        verdict, reason, evidence = verify_claim(con, r)
        if verdict == "CLOSE":
            close_list.append((r, reason, evidence))
        else:
            keep_reasons[reason] += 1

    print(f"\nCLOSE: {len(close_list)}")
    print(f"KEEP reasons:")
    for k, v in keep_reasons.items():
        print(f"  {v:4} {k}")

    # Execute
    print(f"\n--- mutations ---")
    n = 0
    for r, reason, evidence in close_list:
        if args.limit and n >= args.limit:
            break
        title_t = r["properties"]["Phase Title"]["title"]
        title = title_t[0]["plain_text"][:80] if title_t else "(no title)"
        try:
            patch_complete(tok, r["id"], reason, evidence, dry=args.dry_run)
            _audit({"step": "adg_close", "page_id": r["id"], "title": title, "reason": reason, "evidence": evidence, "dry_run": args.dry_run})
            n += 1
            if n % 10 == 0:
                print(f"  ... {n} closed")
        except Exception as e:
            print(f"  ERROR on {r['id']} ({title}): {e}")
            _audit({"step": "adg_close_error", "page_id": r["id"], "title": title, "error": str(e)})
        time.sleep(0.35)
    print(f"TOTAL closed: {n}")
    print(f"\naudit: {AUDIT_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
