"""CI smoke gate — W3.P2: verify R1B warm-up script is importable and dry-run succeeds.

Gate ID: RG-W3 (advisory)
Tier: T7 (assurance)

Checks:
1. warm_r1b_cache module imports without error.
2. run_warmup() dry_run=True completes for top-5 pairs with zero failures.
3. warm_r1b_cache CLI --dry-run --top 3 exits 0 in < 30 s.

This gate is advisory by default. Set R1B_WARMUP_SMOKE_FAIL_CLOSED=1 to make
it fail-closed (exit 1 on any finding).

Exit codes: 0 = all clear, 1 = findings (when fail-closed).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FAIL_CLOSED = os.environ.get("R1B_WARMUP_SMOKE_FAIL_CLOSED", "0") == "1"

_findings: list[str] = []


def _check(label: str, ok: bool, detail: str = "") -> None:
    tag = "OK " if ok else "ERR"
    msg = f"[{tag}] {label}" + (f": {detail}" if detail else "")
    print(msg)
    if not ok:
        _findings.append(label)


# ---------------------------------------------------------------------------
# Check 1 — module import
# ---------------------------------------------------------------------------

try:
    import importlib
    mod = importlib.import_module("tools.apps_rg.warm_r1b_cache")
    _check("warm_r1b_cache importable", True)
except Exception as exc:
    _check("warm_r1b_cache importable", False, str(exc))
    mod = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Check 2 — run_warmup dry_run=True
# ---------------------------------------------------------------------------

if mod is not None:
    try:
        t0 = time.monotonic()
        summary = mod.run_warmup(
            pairs=mod.TOP_PAIRS,
            policy_hash="smoke_policy_v1",
            blueprint_hash="smoke_blueprint_v1",
            tenant_id="smoke",
            dry_run=True,
            top=5,
        )
        elapsed = time.monotonic() - t0
        ok = summary["failed"] == 0 and summary["succeeded"] >= 1
        _check(
            "run_warmup dry_run top-5 succeeds",
            ok,
            f"succeeded={summary['succeeded']} failed={summary['failed']} elapsed={elapsed:.2f}s",
        )
    except Exception as exc:
        _check("run_warmup dry_run top-5 succeeds", False, str(exc))
else:
    _check("run_warmup dry_run top-5 succeeds", False, "module not importable (skipped)")


# ---------------------------------------------------------------------------
# Check 3 — CLI subprocess --dry-run --top 3
# ---------------------------------------------------------------------------

try:
    t0 = time.monotonic()
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "apps_rg" / "warm_r1b_cache.py"),
         "--dry-run", "--top", "3"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO_ROOT),
    )
    elapsed = time.monotonic() - t0
    ok = result.returncode == 0
    _check(
        "CLI --dry-run --top 3 exits 0",
        ok,
        f"rc={result.returncode} elapsed={elapsed:.1f}s"
        + (f" stderr={result.stderr[:120]!r}" if not ok else ""),
    )
except subprocess.TimeoutExpired:
    _check("CLI --dry-run --top 3 exits 0", False, "timeout after 30 s")
except Exception as exc:
    _check("CLI --dry-run --top 3 exits 0", False, str(exc))


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print(f"\nR1B warm-up smoke: {len(_findings)} finding(s)")
if _findings:
    for f in _findings:
        print(f"  FINDING: {f}")

if _findings and FAIL_CLOSED:
    sys.exit(1)
sys.exit(0)
