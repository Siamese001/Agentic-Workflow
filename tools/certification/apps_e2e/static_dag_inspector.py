"""Generic static L3 DAG proof emitter.

Generalizes tools/certification/apps_rg_e2e/emit_static_dag_proof.py:
parameterized by `app_package` and `app_name`. Searches a fixed set of
candidate registry/DAG paths under the app's config directory and under
`agentic_core/L3_orchestration/{dags,workflows}/<app_name>/`. Emits a
fail-closed proof bundle whether the DAG exists or not.
"""
from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any, Iterable

import yaml

from tools.certification.apps_e2e import PROOF_SCHEMA_VERSION
from tools.certification.apps_e2e.hash_utils import (
    REPO_ROOT, relative_to_repo, sha256_file, utc_now_iso,
)


def _candidate_registries(app_package: str) -> tuple[tuple[str, str], ...]:
    base = f"{app_package}/config"
    return (
        (f"{base}/route_registry.yaml", "route_registry"),
        (f"{base}/route_registry.yml", "route_registry"),
        (f"{base}/route_registry.json", "route_registry"),
        (f"{base}/l3_dag.yaml", "l3_dag_inline"),
        (f"{base}/workflow.yaml", "workflow_inline"),
        (f"{base}/dag.yaml", "dag_inline"),
        (f"{base}/hop_pipeline.yaml", "hop_pipeline_inline"),
    )


def _candidate_dag_dirs(app_package: str, app_name: str) -> tuple[str, ...]:
    return (
        f"{app_package}/workflows",
        f"{app_package}/dags",
        f"{app_package}/l3_dags",
        f"agentic_core/L3_orchestration/dags/{app_name}",
        f"agentic_core/L3_orchestration/workflows/{app_name}",
    )


def _scan_registries(app_package: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel, kind in _candidate_registries(app_package):
        p = REPO_ROOT / rel
        rows.append({
            "path": rel,
            "kind": kind,
            "exists": p.exists(),
            "sha256": sha256_file(p) if p.exists() else None,
            "size_bytes": p.stat().st_size if p.exists() else None,
        })
    return rows


def _scan_dag_dirs(app_package: str, app_name: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in _candidate_dag_dirs(app_package, app_name):
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


def _detect_cycle_and_depth(
    node_ids: list[str],
    edges: list[tuple[str, str]],
    entry_nodes: list[str],
) -> tuple[bool, int]:
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
    if processed != len(node_ids):
        return (True, -1)
    depth = {n: 0 for n in entry_nodes}
    bfs: deque[str] = deque(entry_nodes)
    while bfs:
        node = bfs.popleft()
        for dst in adj.get(node, []):
            new_d = depth[node] + 1
            if new_d > depth.get(dst, -1):
                depth[dst] = new_d
                bfs.append(dst)
    return (False, max(depth.values()) if depth else 0)


def _build_dag_facts(
    registry_path: Path, dag_path: Path, app_name: str,
) -> dict[str, Any]:
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    dag = yaml.safe_load(dag_path.read_text(encoding="utf-8")) or {}
    nodes = list(dag.get("nodes") or [])
    edges = list(dag.get("edges") or [])
    node_ids = [str(n.get("id")) for n in nodes if n.get("id")]
    edge_pairs = [
        (str(e["from"]), str(e["to"])) for e in edges
        if e.get("from") and e.get("to")
    ]
    entry = list(dag.get("entry_nodes") or [])
    terminal = list(dag.get("terminal_nodes") or [])
    edges_valid = all(s in node_ids and d in node_ids for s, d in edge_pairs)
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
        "app_name_matches": (
            registry.get("app_name") == app_name and dag.get("app_name") == app_name
        ),
    }


def build_static_dag_proof(*, app_name: str, app_package: str) -> dict[str, Any]:
    registries = _scan_registries(app_package)
    dag_dirs = _scan_dag_dirs(app_package, app_name)
    any_registry_present = any(r["exists"] for r in registries)
    canonical_registry = REPO_ROOT / app_package / "config" / "route_registry.yaml"
    canonical_dag = REPO_ROOT / app_package / "config" / "l3_dag.yaml"
    canonical_pair_present = canonical_registry.exists() and canonical_dag.exists()
    present = canonical_pair_present
    fail_reasons: list[str] = []
    if not canonical_registry.exists():
        fail_reasons.append(f"no_route_registry_for_{app_name}")
    if not canonical_dag.exists():
        fail_reasons.append(f"no_static_l3_dag_files_for_{app_name}")
    if not present:
        fail_reasons.append("static_dag_missing_entirely")

    proof: dict[str, Any] = {
        "proof_schema_version": PROOF_SCHEMA_VERSION,
        "proof_kind": "static_l3_dag_proof",
        "app_name": app_name,
        "generated_at_utc": utc_now_iso(),
        "present": present,
        "fail_closed": not present,
        "fail_reasons": fail_reasons,
        "dag_id": None, "dag_name": None, "dag_version": None,
        "dag_file_path": None, "dag_sha256": None,
        "dag_registry_ref": None, "dag_registry_sha256": None,
        "route_ids": [], "route_binding_refs": [],
        "node_count": None, "edge_count": None,
        "entry_nodes": [], "terminal_nodes": [],
        "node_ids": [], "edge_list": [],
        "max_depth": None, "has_cycle": None,
        "all_nodes_have_owner": None,
        "all_nodes_have_step_contract_schema": None,
        "all_nodes_have_allowed_execution_surface": None,
        "l3_no_execute_policy": None, "l3_no_retrieve_policy": None,
        "l3_no_prompt_assembly_policy": None, "l3_no_l4_write_policy": None,
        "edges_reference_existing_nodes": None,
        "registry_binding_matches_dag": None,
        "app_name_matches": None,
        "scan_results": {
            "registries": registries,
            "dag_directories": dag_dirs,
        },
        "scan_method": "deterministic_path_enumeration",
        "notes": (
            f"Static DAG for {app_name} does not exist as of this scan."
            if not present else
            f"Static DAG present for {app_name} — fields populated from canonical YAML pair."
        ),
    }

    if canonical_pair_present:
        try:
            proof.update(_build_dag_facts(canonical_registry, canonical_dag, app_name))
        except (yaml.YAMLError, OSError) as exc:
            proof["fail_reasons"].append(f"dag_parse_error:{type(exc).__name__}")
            proof["fail_closed"] = True
            proof["present"] = False

    return proof


__all__ = ["build_static_dag_proof"]
