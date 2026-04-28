#!/usr/bin/env python3
"""Replay proof CI gate — wrapper around run_replay_proof.py.

W3.2 of plan ``assurance-p1-gates-ab4758``. Fails closed when two canary
replays produce different digests.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROOF_SCRIPT = REPO_ROOT / "scripts" / "proof" / "run_replay_proof.py"

DEFAULT_TIMEOUT_S = 30


def main() -> int:
    if not PROOF_SCRIPT.is_file():
        print(f"❌ proof script missing: {PROOF_SCRIPT}", file=sys.stderr)
        return 2

    cmd = [sys.executable, str(PROOF_SCRIPT), "--json"]
    try:
        proc = subprocess.run(  # noqa: S603 — fixed argv, shell=False
            cmd,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=DEFAULT_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"⚠️  replay proof timed out after {DEFAULT_TIMEOUT_S}s", file=sys.stderr)
        return 2

    print("🔍 Replay proof gate")
    out = proc.stdout.strip()
    try:
        result = json.loads(out) if out else {}
    except json.JSONDecodeError:
        print(f"❌ proof output not JSON: {out[:240]!r}")
        return 2

    if result.get("error"):
        print(f"⚠️  INFRA-ERROR — {result['error']}")
        return 2
    if result.get("ok"):
        digest = result["runs"][0]["digest"]
        print(f"  ✅ replay deterministic — digest={digest[:16]}…")
        return 0

    print(f"  ❌ replay digests differ")
    if len(result.get("runs", [])) >= 2:
        a = result["runs"][0]
        b = result["runs"][1]
        print(f"      run_a digest: {a['digest']}")
        print(f"      run_b digest: {b['digest']}")
        # Print invariant diffs.
        inv_a, inv_b = a["invariant"], b["invariant"]
        for key in sorted(set(inv_a) | set(inv_b)):
            if inv_a.get(key) != inv_b.get(key):
                print(f"      diff [{key}]: {inv_a.get(key)!r} != {inv_b.get(key)!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
