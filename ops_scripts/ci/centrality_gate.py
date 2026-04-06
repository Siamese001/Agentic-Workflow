"""Centrality Gate — CI Gate (Baseline + New-Node Explainer).

_emit_reads_through("l4", "centrality_gate", "urg_read_1")
_emit_reads_through("l4", "centrality_gate", "urg_read_2")
_emit_reads_through("l4", "centrality_gate", "urg_read_3")
_emit_reads_through("l4", "centrality_gate", "urg_read_4")
_emit_reads_through("l4", "centrality_gate", "urg_read_5")
_emit_reads_through("l4", "centrality_gate", "urg_read_6")
_emit_reads_through("l4", "centrality_gate", "urg_read_7")
_emit_reads_through("l4", "centrality_gate", "urg_read_8")
_emit_reads_through("l4", "centrality_gate", "urg_read_9")
_emit_reads_through("l4", "centrality_gate", "urg_read_10")
_emit_reads_through("l4", "centrality_gate", "urg_read_11")
_emit_reads_through("l4", "centrality_gate", "urg_read_12")
_emit_reads_through("l4", "centrality_gate", "urg_read_13")
_emit_reads_through("l4", "centrality_gate", "urg_read_14")
_emit_reads_through("l4", "centrality_gate", "urg_read_15")
_emit_reads_through("l4", "centrality_gate", "urg_read_16")
_emit_reads_through("l4", "centrality_gate", "urg_read_17")
_emit_reads_through("l4", "centrality_gate", "urg_read_18")
_emit_reads_through("l4", "centrality_gate", "urg_read_19")
_emit_reads_through("l4", "centrality_gate", "urg_read_20")
_emit_reads_through("l4", "centrality_gate", "urg_read_21")
_emit_reads_through("l4", "centrality_gate", "urg_read_22")
_emit_reads_through("l4", "centrality_gate", "urg_read_23")
_emit_reads_through("l4", "centrality_gate", "urg_read_24")
_emit_reads_through("l4", "centrality_gate", "urg_read_25")
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

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through

SCAN_ROOTS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
GENERAL_CEILING = 15
ALLOWLIST: dict[str, int] = {'agentic_core.base_agents.SovereignBaseAgent': 200, 'agentic_core.L5_safety.config.structure_blueprint_config': 200, 'agentic_core.utils.decorators': 120, 'agentic_core.utils.timeout_decorator_util': 80, 'agentic_core.mixins.subatomic_testing_mixin': 60, 'agentic_core.mixins.atomic_execution_mixin': 40, 'agentic_core.L5_safety.enforcement.archival_gatekeeper_gate': 20, 'agentic_core.L5_safety.reasoning.hierarchy_healer': 20, 'apps_rg.utils.RGAgentBase': 20, 'agentic_core.mixins.mcp_hardened_mixin': 20, 'agentic_core.L0_routing.scripts.full_agent_discovery': 20, 'agentic_core.L3_orchestration.reasoning.UnifiedAgent': 20, 'agentic_core.L5_safety.reasoning.FileClassificationAgent': 20, 'agentic_core.L5_safety.reasoning.CodeHealerAgent': 20, 'agentic_core.L5_safety.types.healing_orchestration_types': 20, 'agentic_core.L5_safety.config.structure_blueprint.enforcement.types': 20, 'agentic_core.L5_safety.reasoning.CodeValidatorAgent': 20, 'apps_shared.utils.ConfigurationService': 20, 'apps_lic.utils.LICAgentBase': 20}
EXECUTOR_CEILINGS: dict[str, int] = {'apps_lic.engines.HOPPipelineExecutor': 12, 'agentic_core.L6_observability.reasoning.observability_probe_executor': 10, 'apps_lic.engines.LICValidationExecutor': 10, 'agentic_core.L5_safety.reasoning.InspectorExecutor': 10, 'apps_rg.engines.RGValidationExecutor': 10, 'apps_rg.engines.RGStrategyExecutor': 10}

def _path_to_module(path: str) -> str:
    return path.replace(os.sep, '.').replace('/', '.').removesuffix('.py')

def compute_centrality(project_root: Path) -> tuple[dict[str, int], dict[str, set[str]]]:
    """Return (module -> importer count, module -> set of importers)."""
    reverse_graph: dict[str, set[str]] = defaultdict(set)
    all_modules: set[str] = set()
    for scan_root in SCAN_ROOTS:
        root_path = project_root / scan_root
        if not root_path.is_dir():
            continue
        for dirpath, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for f in files:
                if not f.endswith('.py'):
                    continue
                fpath = Path(dirpath) / f
                rel = os.path.relpath(fpath, project_root)
                mod = _path_to_module(rel)
                all_modules.add(mod)
                try:
                    source = open(fpath, encoding='utf-8', errors='replace').read()
                    tree = ast.parse(source, filename=fpath)
                except (SyntaxError, OSError):    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        target = node.module
                        if target.split('.')[0] in SCAN_ROOTS:
                            reverse_graph[target].add(mod)
    counts = {mod: len(reverse_graph.get(mod, set())) for mod in all_modules}
    return (counts, dict(reverse_graph))
BASELINE_PATH = 'artifacts/consolidation/centrality_baseline.json'

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    centrality, reverse_graph = compute_centrality(project_root)
    violations: list[str] = []
    baseline_file = project_root / BASELINE_PATH
    if not baseline_file.is_file():
        print(f'FAIL: baseline not found: {BASELINE_PATH}', file=sys.stderr)
        return 1
    baseline = json.loads(baseline_file.read_text(encoding='utf-8'))
    known_above = set(baseline.get('known_above_threshold', {}).keys())
    for mod, count in sorted(centrality.items(), key=lambda x: -x[1]):
        ceiling = ALLOWLIST.get(mod, GENERAL_CEILING)
        if count > ceiling:
            violations.append(f'{mod}: {count} importers exceeds ceiling {ceiling}')
    for executor, ceiling in EXECUTOR_CEILINGS.items():
        count = centrality.get(executor, 0)
        if count > ceiling:
            violations.append(f'EXECUTOR {executor}: {count} importers exceeds ceiling {ceiling}')
    new_gravity_nodes: list[tuple[str, int]] = []
    for mod, count in centrality.items():
        if count > GENERAL_CEILING and mod not in known_above and (mod not in ALLOWLIST):
            new_gravity_nodes.append((mod, count))
    if new_gravity_nodes:
        print(f"\n{'=' * 70}")
        print('NEW GRAVITY NODE(S) DETECTED — actionable detail:')
        print(f"{'=' * 70}")
        for mod, count in sorted(new_gravity_nodes, key=lambda x: -x[1]):
            violations.append(f'NEW GRAVITY NODE: {mod} = {count} importers (not in baseline, not allowlisted)')
            importers = sorted(reverse_graph.get(mod, set()))
            top_importers = importers[:10]
            print(f'\n  Module: {mod}')
            print(f'  Importers: {count} (threshold: {GENERAL_CEILING})')
            print(f'  Top {len(top_importers)} importers:')
            for imp in top_importers:
                print(f'    - {imp}')
            if len(importers) > 10:
                print(f'    ... and {len(importers) - 10} more')
            print('  Fix: add to ALLOWLIST with ceiling, or add to')
            print('        centrality_baseline.json with CENTRALITY_BASELINE_BUMP:<reason>')
        print(f"{'=' * 70}")
    top = sorted(centrality.items(), key=lambda x: -x[1])[:10]
    print('Centrality Gate (baseline + new-node detection):')
    print(f'  baseline_known={len(known_above)}')
    for mod, count in top:
        ceiling = ALLOWLIST.get(mod, GENERAL_CEILING)
        status = 'OK' if count <= ceiling else 'OVER'
        print(f'  {status}: {mod} = {count} (ceiling {ceiling})')
    print('\nExecutor centrality:')
    for executor, ceiling in sorted(EXECUTOR_CEILINGS.items()):
        count = centrality.get(executor, 0)
        status = 'OK' if count <= ceiling else 'OVER'
        print(f'  {status}: {executor} = {count} (ceiling {ceiling})')
    if violations:
        print(f'\nFAIL: {len(violations)} violation(s):')
        for v in violations:
            print(f'  - {v}')
        return 1
    print('\nPASS: all modules within ceilings, no new gravity nodes')
    return 0
if __name__ == '__main__':
    sys.exit(main())
