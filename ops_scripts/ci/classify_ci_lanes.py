#!/usr/bin/env python3
"""Classify changed files into CI lanes from ``.github/ci-lanes.yaml``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - CI installs PyYAML via python-setup.
    raise SystemExit(f"PyYAML required: {exc}") from exc

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / ".github" / "ci-lanes.yaml"


def _load_config(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a YAML mapping")
    workflows = data.get("workflows", {})
    if not isinstance(workflows, dict):
        raise SystemExit(f"{path} must contain a 'workflows:' mapping")
    return data


def _load_changed_files(path: Path) -> list[str]:
    if not path.exists():
        return []
    files: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = line.strip().replace("\\", "/")
        if entry:
            files.append(entry)
    return files


def _matches(path: str, pattern: str) -> bool:
    cleaned = pattern.strip()
    if not cleaned:
        return False
    if any(ch in cleaned for ch in "*?["):
        from fnmatch import fnmatch

        return fnmatch(path, cleaned)
    return cleaned in path


def classify(workflow: str, changed_files: list[str], config: dict) -> dict[str, object]:
    workflows = config.get("workflows", {})
    workflow_cfg = workflows.get(workflow, {})
    if not isinstance(workflow_cfg, dict):
        raise SystemExit(f"workflow '{workflow}' is not defined in {DEFAULT_CONFIG}")
    lanes = workflow_cfg.get("lanes", {})
    if not isinstance(lanes, dict):
        raise SystemExit(f"workflow '{workflow}' must contain a 'lanes:' mapping")

    lane_hits: dict[str, bool] = {}
    selected: list[str] = []
    for lane_name, lane_cfg in lanes.items():
        patterns = []
        if isinstance(lane_cfg, dict):
            raw = lane_cfg.get("match", [])
            if isinstance(raw, list):
                patterns = [str(item) for item in raw]
        hit = any(
            _matches(file_path, pattern)
            for file_path in changed_files
            for pattern in patterns
        )
        lane_hits[str(lane_name)] = hit
        if hit:
            selected.append(str(lane_name))

    return {
        "workflow": workflow,
        "changed_files": changed_files,
        "selected_lanes": selected,
        "lane_hits": lane_hits,
        "any": bool(selected),
    }


def _write_github_output(path: Path, payload: dict[str, object], base_ref: str) -> None:
    selected = payload["selected_lanes"]
    lane_hits = payload["lane_hits"]
    changed = payload["changed_files"]
    with path.open("a", encoding="utf-8") as out:
        for lane, hit in lane_hits.items():
            out.write(f"{lane}={str(bool(hit)).lower()}\n")
        out.write(f"any={str(bool(payload['any'])).lower()}\n")
        out.write(f"base-ref={base_ref}\n")
        out.write(f"selected-lanes={','.join(selected)}\n")
        out.write("changed-files<<EOF\n")
        out.write("\n".join(changed))
        out.write("\nEOF\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", required=True, help="Workflow name in .github/ci-lanes.yaml")
    parser.add_argument("--changed-files-file", type=Path, required=True)
    parser.add_argument("--base-ref", default="main")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--github-output", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config = _load_config(args.config)
    changed_files = _load_changed_files(args.changed_files_file)
    payload = classify(args.workflow, changed_files, config)
    if args.github_output is not None:
        _write_github_output(args.github_output, payload, args.base_ref)
    if args.json:
        print(json.dumps({**payload, "base_ref": args.base_ref}, indent=2, sort_keys=True))
    else:
        print(
            f"{args.workflow}: {len(payload['selected_lanes'])} lane(s) matched "
            f"from {len(changed_files)} changed file(s)"
        )
        if payload["selected_lanes"]:
            print("selected:", ", ".join(payload["selected_lanes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
