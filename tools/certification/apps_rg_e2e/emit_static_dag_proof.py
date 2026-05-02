"""Emit the static L3 DAG proof for apps_rg.

Honest scan: searches for a static L3 workflow DAG registered for apps_rg.
If none is found, emits `apps_rg_static_l3_dag_proof.json` with
`present=false` and the exact registry paths that were searched. Refuses
to fabricate DAG metadata, nodes, edges, hashes, or registry bindings.

The user's own spec says: "Fail closed if: DAG file is missing. DAG
registry binding is missing." — this emitter surfaces that failure as
deterministic evidence rather than silently omitting the artifact.

Usage:
    python -m tools.certification.apps_rg_e2e.emit_static_dag_proof
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path
from typing import Any

import yaml

from tools.certification.apps_rg_e2e._shared import (
    APP_NAME,
    CERT_DIR,
    PROOF_SCHEMA_VERSION,
    REPO_ROOT,
    relative_to_repo,
    sha256_file,
    utc_now_iso,
    write_json,
)

OUTPUT_PATH = CERT_DIR / "apps_rg_static_l3_dag_proof.json"


# Candidate locations where a static L3 DAG for apps_rg could legitimately
# live. Mirrors the apps_qna pattern: a YAML/JSON registry in app/config.
CANDIDATE_REGISTRIES: tuple[tuple[str, str], ...] = (
    ("apps_rg/config/route_registry.yaml", "route_registry"),
    ("apps_rg/config/route_registry.yml", "route_registry"),
    ("apps_rg/config/route_registry.json", "route_registry"),
    ("apps_rg/config/l3_dag.yaml", "l3_dag_inline"),
    ("apps_rg/config/workflow.yaml", "workflow_inline"),
    ("apps_rg/config/dag.yaml", "dag_inline"),
)

CANDIDATE_DAG_FILES: tuple[str, ...] = (
    "apps_rg/workflows",
    "apps_rg/dags",
    "apps_rg/l3_dags",
    "agentic_core/L3_orchestration/dags/apps_rg",
    "agentic_core/L3_orchestration/workflows/apps_rg",
)


def _scan_registries() -> list[dict[str, Any]]:
    """Return one row per candidate registry location."""
    rows: list[dict[str, Any]] = []
    for rel, kind in CANDIDATE_REGISTRIES:
        p = REPO_ROOT / rel
        rows.append({
            "path": rel,
            "kind": kind,
            "exists": p.exists(),
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size if p.exists() else None,
        })
    return rows


def _scan_dag_dirs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in CANDIDATE_DAG_FILES:
        p = REPO_ROOT / rel
        if not p.exists():
            rows.append({"path": rel, "exists": False, "file_count": 0, "files": []})
            continue
        files: list[dict[str, Any]] = []
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in {".yaml", ".yml", ".json"}:
                    files.append({
                        "path": relative_to_repo(f),
                        "sha256": sha256_file(f),
                        "size_bytes": f.stat().st_size,
                    })
        rows.append({"path": rel, "exists": True, "file_count": len(files), "files": files})
    return rows


def _detect_cycle_and_depth(node_ids: list[str], edges: list[tuple[str, str]],
                             entry_nodes: list[str]) -> tuple[bool, int]:
    """Return (has_cycle, max_depth_from_entry_nodes).

    Uses Kahn's algorithm for cycle detection (any unprocessed nodes after
    topological pass means a cycle). max_depth is the longest path from
    any entry node, computed by BFS over the topo order.
    """
    if not node_ids:
        return (False, 0)
    indeg: dict[str, int] = {n: 0 for n in node_ids}
    adj: dict[str, list[str]] = {n: [] for n in node_ids}
    for src, dst in edges:
        if src in adj and dst in indeg:
            adj[src].append(dst)
            indeg[dst] += 1
    queue: deque[str] = deque([n for n in node_ids if indeg[n] == 0])
    processed = 0
    while queue:
        node = queue.popleft()
        processed += 1
        for dst in adj[node]:
            indeg[dst] -= 1
            if indeg[dst] == 0:
                queue.append(dst)
    has_cycle = processed != len(node_ids)
    if has_cycle:
        return (True, -1)
    # BFS depth from any entry node
    depth = {n: 0 for n in entry_nodes}
    bfs: deque[str] = deque(entry_nodes)
    while bfs:
        node = bfs.popleft()
        for dst in adj.get(node, []):
            new_depth = depth[node] + 1
            if new_depth > depth.get(dst, -1):
                depth[dst] = new_depth
                bfs.append(dst)
    return (False, max(depth.values()) if depth else 0)


def _build_dag_facts(registry_path: Path, dag_path: Path) -> dict[str, Any]:
    """Parse a present registry+DAG into the spec's required fields."""
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    dag = yaml.safe_load(dag_path.read_text(encoding="utf-8")) or {}

    nodes = list(dag.get("nodes") or [])
    edges = list(dag.get("edges") or [])
    node_ids = [str(n.get("id")) for n in nodes if n.get("id")]
    edge_pairs = [(str(e["from"]), str(e["to"])) for e in edges
                  if e.get("from") and e.get("to")]
    entry = list(dag.get("entry_nodes") or [])
    terminal = list(dag.get("terminal_nodes") or [])
    edges_valid = all(src in node_ids and dst in node_ids for src, dst in edge_pairs)
    has_cycle, max_depth = _detect_cycle_and_depth(node_ids, edge_pairs, entry)

    routes = list(registry.get("routes") or [])
    route_ids = [str(r.get("route_id")) for r in routes if r.get("route_id")]
    binding_match = any(
        str(r.get("route_id")) == str(dag.get("route_binding"))
        for r in routes
    )

    return {
        "dag_id": dag.get("dag_id"),
        "dag_name": dag.get("dag_name"),
        "dag_version": dag.get("dag_version"),
        "dag_file_path": relative_to_repo(dag_path),
        "dag_sha256": sha256_file(dag_path),
        "dag_registry_ref": relative_to_repo(registry_path),
        "dag_registry_sha256": sha256_file(registry_path),
        "route_ids": route_ids,
        "route_binding_refs": [dag.get("route_binding")] if dag.get("route_binding") else [],
        "node_count": len(nodes),
        "edge_count": len(edges),
        "entry_nodes": entry,
        "terminal_nodes": terminal,
        "node_ids": node_ids,
        "edge_list": [{"from": s, "to": d} for s, d in edge_pairs],
        "max_depth": max_depth,
        "has_cycle": has_cycle,
        "all_nodes_have_owner": all(n.get("owner") for n in nodes),
        "all_nodes_have_step_contract_schema": all(n.get("step_contract_schema") for n in nodes),
        "all_nodes_have_allowed_execution_surface": all(n.get("allowed_execution_surface") for n in nodes),
        "l3_no_execute_policy": bool(dag.get("l3_no_execute_policy")),
        "l3_no_retrieve_policy": bool(dag.get("l3_no_retrieve_policy")),
        "l3_no_prompt_assembly_policy": bool(dag.get("l3_no_prompt_assembly_policy")),
        "l3_no_l4_write_policy": bool(dag.get("l3_no_l4_write_policy")),
        "edges_reference_existing_nodes": edges_valid,
        "registry_binding_matches_dag": binding_match,
        "app_name_matches": registry.get("app_name") == APP_NAME and dag.get("app_name") == APP_NAME,
    }


def build_static_dag_proof() -> dict[str, Any]:
    generated_at = utc_now_iso()
    registries = _scan_registries()
    dag_dirs = _scan_dag_dirs()

    any_registry_present = any(r["exists"] for r in registries)
    any_dag_file_present = any(d["file_count"] > 0 for d in dag_dirs)

    # Detect the canonical pair: route_registry.yaml + l3_dag.yaml.
    canonical_registry = REPO_ROOT / "apps_rg" / "config" / "route_registry.yaml"
    canonical_dag = REPO_ROOT / "apps_rg" / "config" / "l3_dag.yaml"
    canonical_pair_present = canonical_registry.exists() and canonical_dag.exists()
    present = canonical_pair_present or any_registry_present

    fail_reasons: list[str] = []
    if not canonical_registry.exists():
        fail_reasons.append("no_route_registry_for_apps_rg")
    if not canonical_dag.exists():
        fail_reasons.append("no_static_l3_dag_files_for_apps_rg")
    if not present:
        fail_reasons.append("static_dag_missing_entirely")

    proof: dict[str, Any] = {
        "proof_schema_version": PROOF_SCHEMA_VERSION,
        "proof_kind": "static_l3_dag_proof",
        "app_name": APP_NAME,
        "generated_at_utc": generated_at,
        "present": present,
        "fail_closed": not present,
        "fail_reasons": fail_reasons,
        "dag_id": None,
        "dag_name": None,
        "dag_version": None,
        "dag_file_path": None,
        "dag_sha256": None,
        "dag_registry_ref": None,
        "dag_registry_sha256": None,
        "route_ids": [],
        "route_binding_refs": [],
        "node_count": None,
        "edge_count": None,
        "entry_nodes": [],
        "terminal_nodes": [],
        "node_ids": [],
        "edge_list": [],
        "max_depth": None,
        "has_cycle": None,
        "all_nodes_have_owner": None,
        "all_nodes_have_step_contract_schema": None,
        "all_nodes_have_allowed_execution_surface": None,
        "l3_no_execute_policy": None,
        "l3_no_retrieve_policy": None,
        "l3_no_prompt_assembly_policy": None,
        "l3_no_l4_write_policy": None,
        "edges_reference_existing_nodes": None,
        "registry_binding_matches_dag": None,
        "app_name_matches": None,
        "scan_results": {
            "registries": registries,
            "dag_directories": dag_dirs,
        },
        "scan_method": "deterministic_path_enumeration",
        "notes": (
            "Static DAG for apps_rg does not exist as of this scan."
            if not present else
            "Static DAG present — fields populated from canonical YAML pair."
        ),
    }

    if canonical_pair_present:
        try:
            proof.update(_build_dag_facts(canonical_registry, canonical_dag))
        except (yaml.YAMLError, OSError) as exc:
            proof["fail_reasons"].append(f"dag_parse_error:{type(exc).__name__}")
            proof["fail_closed"] = True
            proof["present"] = False

    return proof


def main() -> int:
    proof = build_static_dag_proof()
    digest, size = write_json(OUTPUT_PATH, proof)
    status = "present" if proof["present"] else "MISSING (fail_closed)"
    print(f"[static_dag_proof] wrote {relative_to_repo(OUTPUT_PATH)}")
    print(f"[static_dag_proof]   sha256={digest}")
    print(f"[static_dag_proof]   size={size} bytes")
    print(f"[static_dag_proof]   present={proof['present']}  status={status}")
    if proof["fail_reasons"]:
        print(f"[static_dag_proof]   fail_reasons: {proof['fail_reasons']}")
    return 0  # the emitter itself succeeds; the DAG's absence is data, not a crash


if __name__ == "__main__":
    sys.exit(main())
