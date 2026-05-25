"""Print per-cycle judge score deltas from executive_summary proof artifact dirs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def analyze_run(run_dir: Path) -> None:
    cycles_path = run_dir / "judge_remediation_cycles.json"
    cycles_doc = _load(cycles_path)
    print(f"\n=== {run_dir.name} ===")
    if not cycles_doc:
        print("  (no judge_remediation_cycles.json)")
        return
    for cycle in cycles_doc.get("cycles") or []:
        if not isinstance(cycle, dict):
            continue
        n = cycle.get("cycle")
        print(f"  cycle {n}: accepted={cycle.get('accepted')} output_changed={cycle.get('output_changed')}")
        for row in cycle.get("score_deltas") or []:
            if not isinstance(row, dict):
                continue
            pk = row.get("provider_key")
            before = row.get("normalized_score_before")
            after = row.get("normalized_score_after")
            delta = row.get("normalized_score_delta")
            improved = row.get("improved")
            print(f"    {pk}: {before} -> {after} (delta={delta}, improved={improved})")
        if not cycle.get("score_deltas"):
            print("    (no score_deltas — pre-fix artifact or regen did not rescore)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact_dirs",
        nargs="*",
        type=Path,
        help="Proof run dirs (default: latest under runtime_proofs/executive_summary/real)",
    )
    args = parser.parse_args()
    dirs = list(args.artifact_dirs)
    if not dirs:
        root = Path("artifacts/apps_rg/runtime_proofs/executive_summary/real")
        if root.is_dir():
            dirs = sorted(root.glob("exec_summary_*"), key=lambda p: p.stat().st_mtime)[-5:]
    for d in dirs:
        analyze_run(d)


if __name__ == "__main__":
    main()
