"""CI gate: refuse merge when Fort Knox evidence is stale.

Reads `certification/evidence_assertions.jsonl` and fails closed when
any assertion's `generated_at_utc` is older than its declared
`freshness_hours` window.

This implements the W2.2 freshness contract from plan
`.cursor/plans/fortknox-100pct-static-runtime-gap-9a3d4f.md` §GAP-4:
"per-PR regen matrix" — every PR must have fresh evidence for every
claim_type cluster. The enforcement is not "re-emit everything every
PR" (wasteful) but "reject stale evidence at gate time" (cheap + strict).

Also prints a per-claim_type summary so operators can see which cluster
needs re-emission next.

Exit codes:
    0 — all assertions fresh
    2 — one or more assertions stale (FAIL_CLOSED)
    3 — HARNESS_ERROR (assertions file missing / unparseable)
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSERTIONS = REPO_ROOT / "certification" / "evidence_assertions.jsonl"
REQS = REPO_ROOT / "certification" / "requirements_source.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hours-ceiling",
        type=int,
        default=None,
        help=("Override: apply an upper-bound ceiling across all rows. A row's "
              "effective window becomes min(row.freshness_hours, ceiling). "
              "Default: honor each row's declared freshness."),
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print per-claim_type summary even when everything passes.",
    )
    args = parser.parse_args()

    if os.environ.get("FORTKNOX_FRESHNESS_BYPASS") == "1":
        print("[check_signoff_freshness] BYPASS (FORTKNOX_FRESHNESS_BYPASS=1)")
        return 0

    if not ASSERTIONS.exists() or not REQS.exists():
        print(
            f"HARNESS_ERROR: required inputs missing "
            f"(assertions={ASSERTIONS.exists()}, reqs={REQS.exists()})",
            file=sys.stderr,
        )
        return 3

    try:
        reqs_doc = json.loads(REQS.read_text(encoding="utf-8"))
        reqs_by_id = {r["req_id"]: r for r in reqs_doc["requirements"]}
    except (json.JSONDecodeError, KeyError, OSError) as exc:
        print(f"HARNESS_ERROR: requirements_source unreadable: {exc}", file=sys.stderr)
        return 3

    now = datetime.now(timezone.utc)
    stale: list[tuple[str, str, float, int]] = []
    fresh_by_claim: dict[str, int] = collections.Counter()
    stale_by_claim: dict[str, int] = collections.Counter()
    total = 0

    with ASSERTIONS.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            rid = a.get("req_id", "?")
            ctrl = a.get("control", "?")
            gen = a.get("generated_at_utc", "")
            hours = int(a.get("freshness_hours", 168))
            if args.hours_ceiling is not None:
                hours = min(hours, args.hours_ceiling)
            try:
                gen_dt = datetime.fromisoformat(gen.replace("Z", "+00:00"))
            except ValueError:
                stale.append((rid, ctrl, -1.0, hours))
                continue
            age_h = (now - gen_dt).total_seconds() / 3600.0
            claim_type = reqs_by_id.get(rid, {}).get("claim_type", "UNKNOWN")
            if age_h > hours:
                stale.append((rid, ctrl, age_h, hours))
                stale_by_claim[claim_type] += 1
            else:
                fresh_by_claim[claim_type] += 1

    # Per-claim_type summary
    if stale or args.summary_only:
        print("[check_signoff_freshness] per-claim_type summary:")
        all_claims = set(fresh_by_claim) | set(stale_by_claim)
        for c in sorted(all_claims):
            f_n = fresh_by_claim.get(c, 0)
            s_n = stale_by_claim.get(c, 0)
            tag = "OK" if s_n == 0 else "STALE"
            print(f"  [{tag:<5}] {c:<32s} fresh={f_n:<4d} stale={s_n}")

    if stale:
        print(
            f"[check_signoff_freshness] FAIL_CLOSED: {len(stale)} of {total} "
            f"assertions stale. First 10:",
            file=sys.stderr,
        )
        for rid, ctrl, age_h, hours in stale[:10]:
            if age_h < 0:
                print(f"  {rid} / {ctrl}: unparseable generated_at_utc", file=sys.stderr)
            else:
                print(
                    f"  {rid} / {ctrl}: age={age_h:.1f}h > freshness_hours={hours}",
                    file=sys.stderr,
                )
        print(
            "To re-emit evidence, run the producer scripts in "
            "tools/cert/ and tools/certification/ then re-compile signoff. "
            "To bypass (dev loop), set FORTKNOX_FRESHNESS_BYPASS=1.",
            file=sys.stderr,
        )
        return 2

    print(f"[check_signoff_freshness] PASS: {total} assertions fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
