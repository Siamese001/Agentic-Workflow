"""Publish a reconciled canonical C0.3 graph from an explicit source path."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps_rg.fact_inventory.c03_graph_authority_reconciliation import (
    reconcile_graph_authority,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    collect_canonical_graph_issues,
)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    source = args.input.resolve()
    output = args.output.resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    reconciled = reconcile_graph_authority(payload)
    issues = collect_canonical_graph_issues(reconciled)
    if issues:
        raise SystemExit("reconciled graph failed validation: " + "; ".join(issues))

    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.with_name(f".{output.name}.staging-{os.getpid()}")
    staging.write_text(
        json.dumps(reconciled, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(staging, output)
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": str(output),
                "skill_count": len(reconciled["skill_rows"]),
                "node_count": len(reconciled["graph_nodes"]),
                "edge_count": len(reconciled["graph_edges"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
