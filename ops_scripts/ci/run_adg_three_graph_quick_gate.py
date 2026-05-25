#!/usr/bin/env python3
"""Contract-gate entry: plane-2 quick manifest on latest ADG snapshot."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    snap = latest_sqlite()
    if snap is None:
        print("[3B0] ERROR: no ADG snapshot found")
        return 2
    from ops_scripts.ci.run_adg_three_graph_tests import main as run_main  # noqa: PLC0415

    return run_main(["--suite", "quick", "--strict", "--snapshot", str(snap)])


if __name__ == "__main__":
    raise SystemExit(main())
