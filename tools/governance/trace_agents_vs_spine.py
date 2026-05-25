#!/usr/bin/env python3
"""Trace each agentic_core *Agent class against the canonical product spine import closure.

Spine seeds (ADR-088 + extended execution path):
  integrated_single_action_spine_run, intake pipeline, route_gates, u0_to_l1_plan,
  l2_recipe_resolver, l2_package_driven_executor, managed_workflow_runner, exit_eval v6 pipeline.

Outputs JSON + markdown table: spine_reachable, direct_importers (non-test), apps_rg_importers.
"""
from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SPINE_SEEDS = [
    "agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py",
    "agentic_core/L0_routing/intake/pipeline.py",
    "agentic_core/L0_routing/reasoning/route_gates.py",
    "agentic_core/L1_cognition/bridges/u0_to_l1_plan.py",
    "agentic_core/runtime/l2_recipe_resolver.py",
    "agentic_core/L2_execution/l2_package_driven_executor.py",
    "agentic_core/L3_orchestration/managed_workflow_runner.py",
    "agentic_core/L3_orchestration/exit_eval/v6/pipeline.py",
]

EXCLUDE_IMPORTER_PREFIXES = (
    "tests/",
    "tools/debug/",
    "archives/",
    ".cursor/",
    "docs/",
)

OPS_ONLY_PREFIXES = ("ops_scripts/", "tools/governance/", "tools/_oneoff/")


def _path_to_module(rel: str) -> str:
    return rel.replace("\\", "/").removesuffix(".py").replace("/", ".")


def _parse_imports(py: Path) -> tuple[set[str], set[str]]:
    """Return (imported_modules, imported_names_from_agentic_core)."""
    try:
        tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set(), set()
    mods: set[str] = set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
            if node.module.startswith("agentic_core"):
                for alias in node.names:
                    names.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("agentic_core"):
                    mods.add(alias.name)
                    names.add(alias.name.split(".")[-1])
    return mods, names


def _build_agentic_core_index() -> dict[str, Path]:
    """module dotted path -> file path for all agentic_core py files."""
    index: dict[str, Path] = {}
    root = REPO / "agentic_core"
    for py in root.rglob("*.py"):
        rel = py.relative_to(REPO).as_posix()
        index[_path_to_module(rel)] = py
    return index


def _bfs_closure(seeds: list[str], index: dict[str, Path], max_files: int = 800) -> set[str]:
    """Transitive import closure as module dotted paths."""
    queue = [_path_to_module(s) for s in seeds if (REPO / s).is_file()]
    seen: set[str] = set()
    while queue and len(seen) < max_files:
        mod = queue.pop(0)
        if mod in seen or not mod.startswith("agentic_core"):
            continue
        seen.add(mod)
        py = index.get(mod)
        if not py or not py.is_file():
            continue
        imported_mods, _ = _parse_imports(py)
        for im in imported_mods:
            if im.startswith("agentic_core") and im not in seen:
                queue.append(im)
    return seen


def _collect_agents() -> list[dict[str, str]]:
    assess = json.loads(
        (REPO / "docs/reports/agentic_core_agent_inventory_runtime_assessment.json").read_text(
            encoding="utf-8"
        )
    )
    return [
        {"class_name": r["agent"], "file_path": r["module_path"].replace("\\", "/")}
        for r in assess["rows"]
    ]


def _fanin(class_name: str, file_path: str) -> list[str]:
    """Files that reference class name or import module (rg would be heavy; scan agentic_core+apps)."""
    mod_path = file_path.replace(".py", "")
    hits: list[str] = []
    scan_roots = [REPO / "agentic_core", REPO / "apps_rg", REPO / "ops_scripts"]
    for root in scan_roots:
        if not root.is_dir():
            continue
        for py in root.rglob("*.py"):
            rel = py.relative_to(REPO).as_posix()
            if rel == file_path:
                continue
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if class_name in text or file_path in text or mod_path.replace("/", ".") in text:
                if f"from {mod_path.replace('/', '.')}" in text or f"import {class_name}" in text:
                    hits.append(rel)
                elif class_name in text and ("import" in text or "Agent" in class_name):
                    hits.append(rel)
    return sorted(set(hits))[:40]


@dataclass
class AgentSpineTrace:
    class_name: str
    file_path: str
    module: str
    spine_module_in_closure: bool
    spine_reachable: str  # YES_MODULE | NO
    importer_count_all: int
    importer_count_prod: int
    importer_count_ops_only: int
    importer_count_test: int
    apps_rg_importers: int
    sample_prod_importers: list[str]
    verdict: str


def main() -> int:
    index = _build_agentic_core_index()
    closure = _bfs_closure(SPINE_SEEDS, index)
    agents = _collect_agents()

    traces: list[AgentSpineTrace] = []
    for a in agents:
        cn = a["class_name"]
        fp = a["file_path"]
        mod = _path_to_module(fp)
        in_closure = mod in closure
        importers = _fanin(cn, fp)
        prod = [p for p in importers if not p.startswith(EXCLUDE_IMPORTER_PREFIXES)]
        test = [p for p in importers if p.startswith("tests/")]
        ops = [p for p in prod if p.startswith(OPS_ONLY_PREFIXES)]
        core_prod = [p for p in prod if not p.startswith(OPS_ONLY_PREFIXES)]
        apps_rg = [p for p in core_prod if p.startswith("apps_rg/")]

        if in_closure:
            reachable = "YES_MODULE"
            verdict = "SPINE_CLOSURE"
        elif apps_rg:
            verdict = "APPS_RG_ONLY"
        elif core_prod:
            verdict = "CORE_OFF_SPINE"
        elif ops:
            verdict = "OPS_ONLY"
        elif test and not prod:
            verdict = "TEST_ONLY"
        elif not importers:
            verdict = "ORPHAN_NO_REF"
        else:
            verdict = "OTHER"

        traces.append(
            AgentSpineTrace(
                class_name=cn,
                file_path=fp,
                module=mod,
                spine_module_in_closure=in_closure,
                spine_reachable=reachable if in_closure else "NO",
                importer_count_all=len(importers),
                importer_count_prod=len(prod),
                importer_count_ops_only=len(ops),
                importer_count_test=len(test),
                apps_rg_importers=len(apps_rg),
                sample_prod_importers=(core_prod + ops)[:5],
                verdict=verdict,
            )
        )

    by_verdict = defaultdict(list)
    for t in traces:
        by_verdict[t.verdict].append(t.class_name)

    out_dir = REPO / "docs/reports/cursor"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "generated_at": ts,
        "spine_seeds": SPINE_SEEDS,
        "closure_module_count": len(closure),
        "agent_count": len(traces),
        "by_verdict": {k: len(v) for k, v in sorted(by_verdict.items())},
        "spine_closure_agents": by_verdict.get("SPINE_CLOSURE", []),
        "traces": [asdict(t) for t in traces],
    }
    json_path = out_dir / "agent_spine_trace_per_agent.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Per-agent spine trace (skeptical pass)",
        "",
        f"**Generated:** {ts}",
        "",
        "Transitive import closure from canonical spine seeds (not grep string hits).",
        "",
        f"| Metric | Value |",
        f"|--------|------:|",
        f"| Modules in spine closure | {len(closure)} |",
        f"| Agents scanned | {len(traces)} |",
        f"| Agent **modules** inside spine closure | {len(by_verdict.get('SPINE_CLOSURE', []))} |",
        "",
        "## Verdict rollup",
        "",
        "| Verdict | Count | Meaning |",
        "|---------|------:|---------|",
        "| SPINE_CLOSURE | "
        f"{len(by_verdict.get('SPINE_CLOSURE', []))} | Agent module imported (transitively) from spine seeds |",
        "| APPS_RG_ONLY | "
        f"{len(by_verdict.get('APPS_RG_ONLY', []))} | Referenced from apps_rg, not in spine closure |",
        "| CORE_OFF_SPINE | "
        f"{len(by_verdict.get('CORE_OFF_SPINE', []))} | agentic_core importers, not spine/apps_rg |",
        "| OPS_ONLY | " f"{len(by_verdict.get('OPS_ONLY', []))} | Only ops_scripts/tools importers |",
        "| TEST_ONLY | " f"{len(by_verdict.get('TEST_ONLY', []))} | Only tests reference |",
        "| ORPHAN_NO_REF | "
        f"{len(by_verdict.get('ORPHAN_NO_REF', []))} | No importer found in scan (agentic_core+apps+ops) |",
        "",
        "## SPINE_CLOSURE agents (only these are in spine import graph)",
        "",
    ]
    if by_verdict.get("SPINE_CLOSURE"):
        md_lines.append(", ".join(f"`{x}`" for x in by_verdict["SPINE_CLOSURE"]))
    else:
        md_lines.append("_None_")
    md_lines.extend(
        [
            "",
            "## Full table",
            "",
            "| Agent | Verdict | Spine closure | apps_rg | prod importers | sample |",
            "|-------|---------|:-------------:|:-------:|:--------------:|--------|",
        ]
    )
    for t in sorted(traces, key=lambda x: (x.verdict, x.class_name)):
        samp = "; ".join(t.sample_prod_importers[:2]) or "—"
        md_lines.append(
            f"| {t.class_name} | {t.verdict} | "
            f"{'yes' if t.spine_module_in_closure else 'no'} | {t.apps_rg_importers} | "
            f"{t.importer_count_prod} | {samp} |"
        )

    md_path = out_dir / "agent_spine_trace_per_agent.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(json.dumps({"md": md_path.as_posix(), "json": json_path.as_posix(), "by_verdict": payload["by_verdict"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
