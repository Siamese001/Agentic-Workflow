"""
Analyze agent_discovery_full.json for suspected non-agents.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from tqdm import tqdm


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _load_agents(discovery_json: Path) -> list[dict]:
    if not discovery_json.exists():
        raise FileNotFoundError(f"Discovery file not found: {discovery_json}")
    with discovery_json.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of agent entries in {discovery_json}")
    return data


def analyze_suspects(discovery_json: Path) -> dict[str, list[dict]]:
    agents = _load_agents(discovery_json)

    print(f"Total entries in {discovery_json.name}: {len(agents)}")
    print("=" * 80)

    suspects: dict[str, list[dict]] = {
        "scripts": [],
        "mixins": [],
        "utils": [],
        "no_agent_suffix": [],
        "clients": [],
        "data_classes": [],
    }

    for agent in tqdm(agents, desc="Processing", unit="item"):
        path = str(agent.get("path", "")).replace("\\", "/").lower()
        name = str(agent.get("class_name", ""))
        has_healing = bool(agent.get("has_healing", False))

        if "/scripts/" in path:
            suspects["scripts"].append(agent)
        if "Mixin" in name:
            suspects["mixins"].append(agent)
        if "/utils/" in path:
            suspects["utils"].append(agent)
        if not name.endswith("Agent"):
            suspects["no_agent_suffix"].append(agent)
        if name.endswith("Client"):
            suspects["clients"].append(agent)
        if not has_healing and not name.endswith("Agent"):
            suspects["data_classes"].append(agent)

    for category, items in suspects.items():
        if not items:
            continue
        print(f"\n{category.upper()} ({len(items)} entries):")
        print("-" * 60)
        for item in items[:15]:
            print(f"  {item.get('class_name', '<unknown>')}")
            print(f"    Path: {item.get('path', '<missing>')}")
            print(f"    Layer: {item.get('layer', 'unknown')}")
            print(f"    Has Healing: {item.get('has_healing', False)}")
            print(f"    Inheritance: {list(item.get('inheritance', []))[:3]}")
        if len(items) > 15:
            print(f"  ... and {len(items) - 15} more")

    print("\n" + "=" * 80)
    print("SUMMARY OF POTENTIAL MISCLASSIFICATIONS:")
    print("=" * 80)
    all_suspect_names = {
        str(item.get("class_name", ""))
        for items in suspects.values()
        for item in items
        if item.get("class_name")
    }
    print(f"Total unique suspects: {len(all_suspect_names)}")
    print(f"  - In scripts/: {len(suspects['scripts'])}")
    print(f"  - Mixins: {len(suspects['mixins'])}")
    print(f"  - In utils/: {len(suspects['utils'])}")
    print(f"  - No 'Agent' suffix: {len(suspects['no_agent_suffix'])}")
    print(f"  - Clients: {len(suspects['clients'])}")

    print("\n" + "-" * 80)
    print("ALL UNIQUE SUSPECTS (for exclusion filter):")
    print("-" * 80)
    for name in sorted(all_suspect_names):
        matching = next(
            (agent for agent in agents if agent.get("class_name") == name),
            None,
        )
        path = matching.get("path", "<missing>") if matching else "<missing>"
        print(f"  {name}: {path}")

    return suspects


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze agent discovery output for likely non-agent entries.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument(
        "--discovery-json",
        help="Path to agent_discovery_full.json. Defaults to the file under the detected repo root.",
    )
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    discovery_json = (
        Path(args.discovery_json).expanduser().resolve()
        if args.discovery_json
        else repo_root / "agent_discovery_full.json"
    )

    try:
        analyze_suspects(discovery_json)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
