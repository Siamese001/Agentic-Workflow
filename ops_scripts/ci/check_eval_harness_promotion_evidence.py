#!/usr/bin/env python3
"""CI wrapper for eval harness promotion evidence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo = Path(__file__).resolve().parents[2]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    return repo


_REPO_ROOT = _bootstrap_repo_root()

from tools.eval.eval_harness_promotion_gate import main as promotion_gate_main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    forwarded = ["--manifest", args.manifest]
    if args.out:
        forwarded.extend(["--out", args.out])
    return promotion_gate_main(forwarded)


if __name__ == "__main__":
    raise SystemExit(main())
