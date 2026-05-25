#!/usr/bin/env python3
"""W7: graph-skills-quality plan must not diff agentic_core/ (until W10-AG Author-Gate)."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"


def _run_git(args: list[str], *, cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return proc.returncode, (proc.stdout or "").strip()


def collect_agentic_core_diff_paths(
    repo_root: Path,
    *,
    base_ref: str | None = None,
) -> list[str]:
    """Return repo-relative paths under agentic_core/ changed in working tree or vs base."""
    seen: set[str] = set()
    commands: list[list[str]] = [
        ["git", "diff", "--name-only", "agentic_core/"],
        ["git", "diff", "--cached", "--name-only", "agentic_core/"],
    ]
    if base_ref:
        commands.append(["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", "agentic_core/"])
    for argv in commands:
        code, out = _run_git(argv, cwd=repo_root)
        if code != 0:
            continue
        for line in out.splitlines():
            path = line.strip().replace("\\", "/")
            if path.startswith("agentic_core/"):
                seen.add(path)
    return sorted(seen)


def check_boundary(
    *,
    repo_root: Path | None = None,
    base_ref: str | None = None,
    allow_agentic_core: bool = False,
) -> dict[str, object]:
    root = repo_root or REPO_ROOT
    if allow_agentic_core or os.environ.get("GRAPH_SKILLS_ALLOW_AGENTIC_CORE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return {
            "schema": "graph_skills_agentic_core_boundary_v1",
            "plan_id": PLAN_ID,
            "status": "PASS",
            "skipped": True,
            "reason": "GRAPH_SKILLS_ALLOW_AGENTIC_CORE set",
            "changed_paths": [],
        }
    effective_base = base_ref or os.environ.get("GRAPH_SKILLS_BASE_REF", "").strip() or None
    changed = collect_agentic_core_diff_paths(root, base_ref=effective_base)
    status = "PASS" if not changed else "FAIL"
    return {
        "schema": "graph_skills_agentic_core_boundary_v1",
        "plan_id": PLAN_ID,
        "status": status,
        "base_ref": effective_base,
        "changed_paths": changed,
        "changed_count": len(changed),
        "policy": "graph-skills-quality-enhancement touches_agentic_core=false until W10-AG",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", default="", help="Optional git base (e.g. origin/main)")
    parser.add_argument("--allow-agentic-core", action="store_true")
    parser.add_argument("--json-out", default="", help="Write result JSON path")
    args = parser.parse_args()
    result = check_boundary(
        base_ref=args.base_ref or None,
        allow_agentic_core=args.allow_agentic_core,
    )
    if args.json_out:
        import json

        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    status = str(result.get("status"))
    if status == "PASS":
        print("GRAPH_SKILLS_AGENTIC_CORE_BOUNDARY: PASS (no agentic_core/ diffs)")
        return 0
    print("GRAPH_SKILLS_AGENTIC_CORE_BOUNDARY: FAIL")
    for path in result.get("changed_paths") or []:
        print(f"  - {path}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
