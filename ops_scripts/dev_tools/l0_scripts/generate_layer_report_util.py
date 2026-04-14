"""Generate a layer report from agent_discovery_full.json with safe root discovery."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_MANIFEST = "agent_discovery_full.json"
LAYER_ORDER = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "Base", "Apps", "Utils", "Tests", "Unknown"]


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        manifest = candidate / DEFAULT_MANIFEST
        if manifest.exists():
            return candidate
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def _load_agents(project_root: Path, manifest_name: str) -> list[dict]:
    manifest_path = project_root / manifest_name
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    with manifest_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of agents in {manifest_path}")
    return data


def _normalize_layer(agent: dict) -> str:
    layer = str(agent.get("layer") or "Unknown").strip()
    if not layer:
        return "Unknown"
    if layer.lower() in {"test", "tests"}:
        return "Tests"
    return layer


def _summarize_layer(agents: list[dict]) -> dict[str, int]:
    return {
        "count": len(agents),
        "healing": sum(1 for agent in agents if agent.get("has_healing")),
        "mcp": sum(1 for agent in agents if agent.get("mcp_hardened")),
        "subatomic": sum(1 for agent in agents if agent.get("has_subatomic")),
        "tools": sum(1 for agent in agents if agent.get("has_tools")),
        "loc": sum(int(agent.get("loc", 0) or 0) for agent in agents),
    }


def build_report(agents: list[dict]) -> tuple[list[dict], dict[str, int]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for agent in agents:
        grouped[_normalize_layer(agent)].append(agent)

    ordered_layers = [layer for layer in LAYER_ORDER if layer in grouped]
    ordered_layers.extend(sorted(layer for layer in grouped if layer not in ordered_layers))

    rows: list[dict] = []
    totals = {"count": 0, "healing": 0, "mcp": 0, "subatomic": 0, "tools": 0, "loc": 0}
    for layer in ordered_layers:
        summary = _summarize_layer(grouped[layer])
        totals = {key: totals[key] + summary[key] for key in totals}
        rows.append({"layer": layer, **summary})
    return rows, totals


def _print_report(rows: list[dict], totals: dict[str, int]) -> None:
    print("=" * 88)
    print("AGENT LAYER REPORT")
    print("=" * 88)
    print(f"{'Layer':<12} {'Count':>7} {'Healing':>8} {'MCP':>6} {'Sub':>6} {'Tools':>7} {'LOC':>8}")
    print("-" * 88)
    for row in rows:
        print(
            f"{row['layer']:<12} {row['count']:>7} {row['healing']:>8} {row['mcp']:>6} "
            f"{row['subatomic']:>6} {row['tools']:>7} {row['loc']:>8}"
        )
    print("-" * 88)
    print(
        f"{'TOTAL':<12} {totals['count']:>7} {totals['healing']:>8} {totals['mcp']:>6} "
        f"{totals['subatomic']:>6} {totals['tools']:>7} {totals['loc']:>8}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a layer summary from the agent discovery manifest")
    parser.add_argument(
        "--manifest", default=DEFAULT_MANIFEST, help="Manifest filename relative to the project root"
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of a table")
    args = parser.parse_args(argv)

    try:
        project_root = _find_project_root()
        agents = _load_agents(project_root, args.manifest)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"[layer-report] {exc}", file=sys.stderr)
        return 1

    rows, totals = build_report(agents)
    if args.json:
        print(json.dumps({"project_root": str(project_root), "layers": rows, "totals": totals}, indent=2))
    else:
        _print_report(rows, totals)
    return 0


if __name__ == "__main__":
    sys.exit(main())
