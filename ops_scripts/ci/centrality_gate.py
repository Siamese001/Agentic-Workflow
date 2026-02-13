#!/usr/bin/env python3
"""Centrality Gate — CI Gate (Baseline + New-Node Explainer).

Recomputes in-degree centrality for all Python modules and fails if:
  1. Any module exceeds its ceiling (ALLOWLIST or GENERAL_CEILING=15).
  2. Executor modules exceed their per-module ceilings.
  3. Any NEW module appears above threshold that is not in the committed
     baseline (new gravity node → FAIL unless allowlisted).

When a new gravity node is detected, the gate prints:
  - which module is new-above-threshold
  - who imports it (top 10 importers)
This makes failures actionable without repo narration.

Baseline: artifacts/consolidation/centrality_baseline.json

Exit 0 = pass, exit 1 = violations found.

Merge-ready gate.
"""

from __future__ import annotations

import ast
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

SCAN_ROOTS = [
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
]

GENERAL_CEILING = 15

ALLOWLIST: dict[str, int] = {
    "agentic_core.base_agents.SovereignBaseAgent": 200,
    "agentic_core.L5_safety.config.structure_blueprint_config": 200,
    "agentic_core.base_agents.decorators": 120,
    "agentic_core.base_agents.timeout_decorator": 80,
    "agentic_core.mixins.subatomic_testing_mixin": 60,
    "agentic_core.mixins.atomic_execution_mixin": 40,
    "agentic_core.L5_safety.enforcement.archival_gatekeeper": 20,
    "agentic_core.L5_safety.reasoning.HierarchyAgent": 20,
    "apps_rg.utils.RGAgentBase": 20,
    "agentic_core.mixins.mcp_hardened_mixin": 20,
    "agentic_core.L0_routing.scripts.full_agent_discovery": 20,
    "agentic_core.L3_orchestration.reasoning.UnifiedAgent": 20,
    "agentic_core.L5_safety.reasoning.FileClassificationAgent": 20,
    "agentic_core.L5_safety.reasoning.CodeHealerAgent": 20,
    "agentic_core.L5_safety.types.healing_orchestration_types": 20,
    "agentic_core.L5_safety.config.structure_blueprint.enforcement.types": 20,
    "agentic_core.L5_safety.reasoning.CodeValidatorAgent": 20,
    "apps_shared.utils.ConfigurationService": 20,
    "apps_lic.utils.LICAgentBase": 20,
}

EXECUTOR_CEILINGS: dict[str, int] = {
    "apps_lic.engines.HOPPipelineExecutor": 12,
    "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor": 10,
    "apps_lic.engines.LICValidationExecutor": 10,
    "agentic_core.L5_safety.reasoning.InspectorExecutor": 10,
    "apps_rg.engines.RGValidationExecutor": 10,
    "apps_rg.engines.RGStrategyExecutor": 10,
}


def _path_to_module(path: str) -> str:
    return path.replace(os.sep, ".").replace("/", ".").removesuffix(".py")


def compute_centrality(project_root: Path) -> tuple[dict[str, int], dict[str, set[str]]]:
    """Return (module -> importer count, module -> set of importers)."""
    reverse_graph: dict[str, set[str]] = defaultdict(set)
    all_modules: set[str] = set()

    for scan_root in SCAN_ROOTS:
        root_path = project_root / scan_root
        if not root_path.is_dir():
            continue
        for dirpath, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d != "__pycache__" and d != ".git"]
            for f in files:
                if not f.endswith(".py"):
                    continue
                # guardian: allow-path-string
                fpath = os.path.join(dirpath, f)
                rel = os.path.relpath(fpath, project_root)
                mod = _path_to_module(rel)
                all_modules.add(mod)
                try:
                    source = open(fpath, encoding="utf-8", errors="replace").read()
                    tree = ast.parse(source, filename=fpath)
                except (SyntaxError, OSError):
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        target = node.module
                        if target.split(".")[0] in SCAN_ROOTS:
                            reverse_graph[target].add(mod)

    counts = {mod: len(reverse_graph.get(mod, set())) for mod in all_modules}
    return counts, dict(reverse_graph)


BASELINE_PATH = "artifacts/consolidation/centrality_baseline.json"


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    centrality, reverse_graph = compute_centrality(project_root)
    violations: list[str] = []

    # Load baseline for new-node detection
    baseline_file = project_root / BASELINE_PATH
    if not baseline_file.is_file():
        print(f"FAIL: baseline not found: {BASELINE_PATH}", file=sys.stderr)
        return 1
    baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
    known_above = set(baseline.get("known_above_threshold", {}).keys())

    # Check general ceiling
    for mod, count in sorted(centrality.items(), key=lambda x: -x[1]):
        ceiling = ALLOWLIST.get(mod, GENERAL_CEILING)
        if count > ceiling:
            violations.append(
                f"{mod}: {count} importers exceeds ceiling {ceiling}",
            )

    # Check executor ceilings
    for executor, ceiling in EXECUTOR_CEILINGS.items():
        count = centrality.get(executor, 0)
        if count > ceiling:
            violations.append(
                f"EXECUTOR {executor}: {count} importers exceeds ceiling {ceiling}",
            )

    # New-node detection: any module above threshold NOT in baseline
    new_gravity_nodes: list[tuple[str, int]] = []
    for mod, count in centrality.items():
        if count > GENERAL_CEILING and mod not in known_above and mod not in ALLOWLIST:
            new_gravity_nodes.append((mod, count))
    if new_gravity_nodes:
        print(f"\n{'=' * 70}")
        print("NEW GRAVITY NODE(S) DETECTED — actionable detail:")
        print(f"{'=' * 70}")
        for mod, count in sorted(new_gravity_nodes, key=lambda x: -x[1]):
            violations.append(
                f"NEW GRAVITY NODE: {mod} = {count} importers (not in baseline, not allowlisted)",
            )
            importers = sorted(reverse_graph.get(mod, set()))
            top_importers = importers[:10]
            print(f"\n  Module: {mod}")
            print(f"  Importers: {count} (threshold: {GENERAL_CEILING})")
            print(f"  Top {len(top_importers)} importers:")
            for imp in top_importers:
                print(f"    - {imp}")
            if len(importers) > 10:
                print(f"    ... and {len(importers) - 10} more")
            print("  Fix: add to ALLOWLIST with ceiling, or add to")
            print("        centrality_baseline.json with CENTRALITY_BASELINE_BUMP:<reason>")
        print(f"{'=' * 70}")

    # Print top 10
    top = sorted(centrality.items(), key=lambda x: -x[1])[:10]
    print("Centrality Gate (baseline + new-node detection):")
    print(f"  baseline_known={len(known_above)}")
    for mod, count in top:
        ceiling = ALLOWLIST.get(mod, GENERAL_CEILING)
        status = "OK" if count <= ceiling else "OVER"
        print(f"  {status}: {mod} = {count} (ceiling {ceiling})")

    # Print executor centrality
    print("\nExecutor centrality:")
    for executor, ceiling in sorted(EXECUTOR_CEILINGS.items()):
        count = centrality.get(executor, 0)
        status = "OK" if count <= ceiling else "OVER"
        print(f"  {status}: {executor} = {count} (ceiling {ceiling})")

    if violations:
        print(f"\nFAIL: {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("\nPASS: all modules within ceilings, no new gravity nodes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
