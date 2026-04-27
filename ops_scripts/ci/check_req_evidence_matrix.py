"""CI gate — requirements-to-runtime evidence matrix.

Wave 1 mode: ADVISORY by default (compiles the matrix, surfaces gap counts,
exits 0). Pass ``--strict`` (or set ``REQ_EVIDENCE_GATE_MODE=strict``) to
flip the exit semantics — non-zero on any release-blocking status.

Once enough requirements have explicit ``REQ_BINDING`` annotations, the
gate should be flipped to strict in CI YAML.

The hard rule per RCA Install 7: release-eligibility = BOTH
  1. apps_proof harness `--mode full` exits 0
  2. this gate exits 0 in --strict mode
Either alone is insufficient.
"""

from __future__ import annotations

import argparse
import os
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CI gate for requirements-evidence matrix",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when any requirement is in release-blocking status",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "runtime" / "req_evidence" / "latest",
    )
    args = parser.parse_args(argv)

    strict = args.strict or os.environ.get("REQ_EVIDENCE_GATE_MODE", "").lower() == "strict"

    cmd = [
        sys.executable, "-m", "tools.proof.req_compiler",
        "--out-dir", str(args.out_dir),
    ]
    if strict:
        cmd.append("--strict")

    print(f"$ {' '.join(cmd)}")
    proc = subprocess.run(  # noqa: S603 -- argv form, shell=False
        cmd, shell=False, timeout=300, cwd=REPO_ROOT, check=False,
    )

    if proc.returncode == 0:
        mode = "STRICT" if strict else "ADVISORY"
        print(f"PASS ({mode}) — req_evidence matrix at {args.out_dir}/requirements_matrix.md")
        return 0

    print(
        f"FAIL — req_evidence matrix has release-blocking rows "
        f"(see {args.out_dir}/requirements_matrix.md)",
        file=sys.stderr,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
