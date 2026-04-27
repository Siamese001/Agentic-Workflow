"""CI gate — runs the apps_* runtime proof harness in W4 (full) mode.

Failure modes (each yields exit != 0):
  - No ADG snapshot under artifacts/adg/
  - bypass validator FAIL (P0 unresolved without active waiver)
  - any scenario PROOF FAIL
  - any W3 validator FAIL (trace/replay/inventory)
  - any negative control NOT CAUGHT
  - write sovereignty FAIL

Usage:
    python ops_scripts/ci/check_apps_runtime_proof.py
    python ops_scripts/ci/check_apps_runtime_proof.py --mode validate   # W3 only
    python ops_scripts/ci/check_apps_runtime_proof.py --mode bypass     # W1 only

The export root is ``artifacts/runtime/apps_proof/ci/<UTC-stamp>/`` so each
CI run leaves an inspectable artifact bundle. A symlink/copy is also written
to ``artifacts/runtime/apps_proof/latest`` for quick inspection.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _latest_adg_snapshot() -> Path | None:
    snaps = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    return snaps[-1] if snaps else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CI gate for apps_* runtime proof harness",
    )
    parser.add_argument(
        "--mode",
        choices=("bypass", "all", "validate", "full"),
        default="full",
        help="Which proof tier to gate on (default: full = W4)",
    )
    parser.add_argument(
        "--adg",
        type=Path,
        default=None,
        help="Optional explicit ADG snapshot path (default: latest in artifacts/adg/)",
    )
    args = parser.parse_args(argv)

    snapshot = args.adg or _latest_adg_snapshot()
    if snapshot is None or not snapshot.exists():
        print(
            "ERROR: no ADG snapshot found under artifacts/adg/. "
            "Run `python tools/generate_full_adg.py` first.",
            file=sys.stderr,
        )
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    export_root = REPO_ROOT / "artifacts" / "runtime" / "apps_proof" / "ci" / stamp
    export_root.mkdir(parents=True, exist_ok=True)

    flag = {
        "bypass": "--bypass-only",
        "all": "--all",
        "validate": "--validate",
        "full": "--full",
    }[args.mode]

    cmd = [
        sys.executable,
        "-m",
        "apps_shared.proof.proof_runner",
        flag,
        "--adg",
        str(snapshot),
        "--export",
        str(export_root),
    ]
    print(f"$ {' '.join(cmd)}")
    proc = subprocess.run(  # noqa: S603 -- argv form, shell=False
        cmd,
        shell=False,
        timeout=600,
        cwd=REPO_ROOT,
        check=False,
    )

    # Mirror to "latest" for convenience
    latest = REPO_ROOT / "artifacts" / "runtime" / "apps_proof" / "latest"
    if latest.exists():
        shutil.rmtree(latest, ignore_errors=True)
    try:
        shutil.copytree(export_root, latest)
    except (OSError, shutil.Error) as exc:
        print(f"WARN: could not mirror to {latest}: {exc}", file=sys.stderr)

    if proc.returncode == 0:
        print(f"PASS — apps_* runtime proof harness ({args.mode}) — see {export_root}")
        return 0
    print(
        f"FAIL — apps_* runtime proof harness ({args.mode}) returned "
        f"exit={proc.returncode}. See {export_root}/proof_report.md",
        file=sys.stderr,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
