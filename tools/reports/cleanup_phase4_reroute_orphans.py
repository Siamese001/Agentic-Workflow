"""Phase 4 — re-route the 7 truly-orphan rows to closest-fit LIVE plans.

Each PATCH:
  1. Sets Plan File = ".windsurf/plans/<successor>.md"
  2. Appends a [REROUTE 2026-04-30] marker to Blocking Items with the original slug
  3. Preserves Status (Blocked stays Blocked, In Progress stays In Progress)

Reversible via the JSONL audit log (preserves old Plan File and Blocking Items).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "reports"))
from audit_notion_backlog_coverage import _query_all_rows, _extract  # noqa: E402

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
AUDIT_LOG = REPO / "artifacts" / "windsurf" / "notion_phase4_reroute.jsonl"

MARKER_DATE = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
MARKER_PREFIX = "[REROUTE"

# Mapping: (plan_norm_orphan_slug, phase_id) -> successor_live_plan_slug
REROUTE_MAP: dict[tuple[str, str], str] = {
    ("adg-l5-bypass-cleanup", "W1.1"): "adg-architectural-p0-violations-cleanup-bced9c",
    ("adg-trace-replay-eval-ratchet", "W1.1"): "adg-gap-remediation-wave-plan-ae5b42",
    ("adg-seam-test-coherence-cleanup", "W1.1"): "gap-closure-test-impl-b77a11",
    ("post-cursor-agent-watchdog-hardening", "W11.1"): "windsurf-maintenance-2026-q2-0f3564",
    ("windsurf-hook-outage-2026-04-23", "HOOK.WINDSURF_TICKET"): "windsurf-maintenance-2026-q2-0f3564",
    ("pytest-server-functional-tests", "W1.1"): "gap-closure-test-impl-b77a11",
    ("d7-anchor-tuning", "W7.4"): "audit-uncovered-gates-and-remediation-627368",
}


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if tok:
        return tok
    env = REPO / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("NOTION_TOKEN not set")


def _patch(token: str, page_id: str, props: dict[str, Any]) -> dict[str, Any]:
    body = {"properties": props}
    req = urllib.request.Request(
        f"{NOTION_API}/pages/{page_id}",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if attempt == 2:
                raise SystemExit(f"PATCH failed for {page_id}: HTTP {exc.code}: {exc.read().decode(errors='replace')}") from exc
            time.sleep(1.5 * (attempt + 1))
        except urllib.error.URLError as exc:
            if attempt == 2:
                raise SystemExit(f"PATCH network error for {page_id}: {exc.reason}") from exc
            time.sleep(1.5 * (attempt + 1))
    return {}


def _existing_blocking(row: dict[str, Any]) -> str:
    rt = row.get("properties", {}).get("Blocking Items", {}).get("rich_text", [])
    return "".join(b.get("plain_text", "") for b in rt)


def _existing_plan_file(row: dict[str, Any]) -> str:
    rt = row.get("properties", {}).get("Plan File", {}).get("rich_text", [])
    return "".join(b.get("plain_text", "") for b in rt)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.dry_run and not args.execute:
        parser.error("specify --dry-run or --execute")

    print("Querying Notion (paginated)...")
    raw_rows = _query_all_rows()
    print(f"  {len(raw_rows)} rows retrieved")

    targets: list[tuple[dict[str, Any], dict[str, str], str]] = []
    for raw in raw_rows:
        ext = _extract(raw)
        key = (ext["plan_file"], ext["phase_id"])
        if key not in REROUTE_MAP:
            continue
        existing = _existing_blocking(raw)
        if MARKER_PREFIX in existing:
            continue  # already re-routed
        successor = REROUTE_MAP[key]
        targets.append((raw, ext, successor))

    print(f"  Targets: {len(targets)} / 7 expected")
    print()
    print("=== TARGETS ===")
    for _, t, succ in targets:
        print(f"  [{t['status']:>11}] {t['plan_file']:<45} | {t['phase_id']:<22} -> {succ}")

    if args.dry_run:
        print()
        print("DRY RUN — re-run with --execute")
        return 0

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    token = _token()
    succ_n = 0
    fail = 0
    print()
    print("Executing PATCHes...")
    with AUDIT_LOG.open("a", encoding="utf-8") as log:
        for raw, t, successor in targets:
            old_plan = _existing_plan_file(raw)
            old_blocking = _existing_blocking(raw)
            new_plan = f".windsurf/plans/{successor}.md"
            marker = (
                f"{MARKER_PREFIX} {MARKER_DATE}] Re-routed from orphan slug "
                f"`{t['plan_file']}` (no plan on disk) to live plan `{successor}`. "
                "Original phase_id and title preserved; successor plan owner should "
                "decide whether to fold into an existing wave or treat as new wave."
            )
            new_blocking = f"{marker}\n\n--- previous Blocking Items ---\n{old_blocking}".rstrip()
            try:
                _patch(token, raw["id"], {
                    "Plan File": {"rich_text": [{"type": "text", "text": {"content": new_plan}}]},
                    "Blocking Items": {"rich_text": [{"type": "text", "text": {"content": new_blocking[:1900]}}]},
                })
                succ_n += 1
                log.write(json.dumps({
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                    "action": "orphan_rerouted",
                    "page_id": raw["id"],
                    "phase_id": t["phase_id"],
                    "old_plan_file": old_plan,
                    "new_plan_file": new_plan,
                    "title": t["title"],
                    "status_preserved": t["status"],
                }) + "\n")
                print(f"  rerouted: {t['plan_file']}/{t['phase_id']} -> {successor}")
            except SystemExit as exc:
                fail += 1
                print(f"  ERROR {raw['id']}: {exc}")
            time.sleep(0.35)

    print()
    print(f"Done. Succeeded: {succ_n}, Failed: {fail}")
    print(f"Audit log: {AUDIT_LOG}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
