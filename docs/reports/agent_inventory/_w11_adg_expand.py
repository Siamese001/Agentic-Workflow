#!/usr/bin/env python3
"""ADG import fan-in expansion for W11-M2."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.adg.mcp import tool_handlers as adg
MATRIX = REPO / "docs/reports/agent_inventory/w11_candidate_fanin_matrix.json"

_ALLOWED_SHIM_STATIC_REFS = frozenset(
    {
        "apps_rg/runtime/bindings/l2_binding_adapter.py",
        "ops_scripts/ci/check_agentic_core_addition.py",
        "tests/_apps_contract/test_apps_rg_exit_uwg_l4_no_bypass_boundary.py",
        "tests/_apps_contract/test_apps_rg_l2_binding_shim_boundary.py",
        "tests/governance/test_apps_rg_l1_core_boundary.py",
        "docs/reports/agent_inventory/_w11_fanin_scan.py",
        "docs/reports/agent_inventory/_w11_adg_expand.py",
    }
)

NOT_PATTERN = {
    "legacy_full_resume_env",
    "offline_contract_stub_env",
    "stub_only_provider_env",
    "mock_judges_cli",
}


def _module_node_id(file_path: str) -> tuple[str | None, str]:
    resp = adg.adg_nodes_by_file(file_path, 50)
    if resp.get("status") != "ok":
        return None, f"nodes_by_file:{resp.get('status')}"
    nodes = resp.get("data", {}).get("nodes", [])
    for n in nodes:
        if n.get("entity_type") == "module":
            return str(n["id"]), "ok"
    return None, "no_module_node"


def _import_fanin(node_id: str) -> tuple[int, str]:
    resp = adg.adg_edge_fanin(node_id, "imports", 500)
    if resp.get("status") != "ok":
        return -1, f"fanin:{resp.get('status')}"
    edges = resp.get("data", {}).get("edges", [])
    return len(edges), "ok"


def _files_for_candidate(cid: str, path: str) -> list[str]:
    if cid in NOT_PATTERN:
        return []
    if cid == "dry_run_dir":
        root = REPO / "apps_rg/runtime/dry_run"
        return sorted(p.relative_to(REPO).as_posix() for p in root.rglob("*.py"))
    if "*" in path:
        if cid == "code_quality_examples":
            root = REPO / "agentic_core/L2_execution/reasoning/examples"
            return sorted(p.relative_to(REPO).as_posix() for p in root.glob("code_quality_*.py"))
        if cid == "rg_reasoning_agents":
            root = REPO / "apps_rg/reasoning"
            return sorted(p.relative_to(REPO).as_posix() for p in root.glob("Rg*.py"))
        if cid == "deprecated_dispatch_clis":
            root = REPO / "apps_rg/runtime/dispatch"
            return sorted(p.relative_to(REPO).as_posix() for p in root.glob("*_dispatch.py"))
        if cid == "shim_apps_rg_l2_binding":
            root = REPO / "archives"
            return sorted(
                p.relative_to(REPO).as_posix()
                for p in root.glob("l2_rationalization_*/agentic_core/L2_execution/apps_rg_l2_binding.py")
            )
        return []
    if " + " in path:
        return [p.strip() for p in path.split(" + ")]
    if path.endswith(".py"):
        return [path]
    return []


def expand() -> dict:
    health = adg.adg_health()
    snap = health.get("data", {}).get("adg_snapshot_id", "unknown")
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    stats = {
        "adg_run_count": 0,
        "adg_not_supported_count": 0,
        "adg_not_available_count": 0,
        "fanin_zero_count": 0,
        "fanin_nonzero_count": 0,
    }
    for cand in data["candidates"]:
        cid = cand["id"]
        if cid in NOT_PATTERN:
            cand["adg_status"] = "NOT_SUPPORTED_PATTERN"
            cand["adg_fanin_count"] = None
            cand["adg_note"] = "env/CLI hatch — ADG pattern fan-in not supported"
            stats["adg_not_supported_count"] += 1
            continue
        files = _files_for_candidate(cid, cand["path"])
        if not files:
            cand["adg_status"] = "NOT_SUPPORTED_PATTERN"
            cand["adg_fanin_count"] = None
            cand["adg_note"] = f"unresolved path pattern: {cand['path']}"
            stats["adg_not_supported_count"] += 1
            continue
        details: list[dict] = []
        total = 0
        ok_all = True
        for fp in files:
            nid, st = _module_node_id(fp)
            if nid is None:
                details.append({"file": fp, "node_id": None, "fanin": None, "status": st})
                ok_all = False
                continue
            cnt, fst = _import_fanin(nid)
            if fst != "ok":
                details.append({"file": fp, "node_id": nid, "fanin": cnt, "status": fst})
                ok_all = False
                continue
            total += max(cnt, 0)
            details.append({"file": fp, "node_id": nid, "fanin": cnt, "status": "ok"})
        cand["adg_details"] = details
        cand["adg_fanin_count"] = total
        if ok_all:
            cand["adg_status"] = "ok"
            stats["adg_run_count"] += 1
            if total == 0:
                stats["fanin_zero_count"] += 1
            else:
                stats["fanin_nonzero_count"] += 1
            cand["adg_note"] = (
                f"ADG imports fan-in aggregate={total} across {len(files)} file(s)"
            )
        else:
            cand["adg_status"] = "PARTIAL"
            stats["adg_not_available_count"] += 1
            cand["adg_note"] = "one or more files failed ADG node/fan-in lookup"
        if cid == "shim_apps_rg_l2_binding":
            cand["proposed_final_classification"] = "ARCHIVED"
            cand["migration_required"] = False
            cand["delete_readiness"] = "NO"
            cand["archive_readiness"] = "DONE"
            cand["blocker"] = "archived under archives/l2_rationalization_20260519/"
        if cid == "validation_orchestrator" and total == 0:
            cand["proposed_final_classification"] = "QUARANTINE_30D"
            cand["blocker"] = (
                "ADG import fan-in 0; CI baselines + 30d quarantine before ARCHIVE"
            )
    data["adg_snapshot_id"] = snap
    data["adg_expansion"] = stats
    data["w11_shim_archive_prep"] = "2026-05-19"
    data["summary"]["archive_ready_count"] = sum(
        1 for c in data["candidates"] if c.get("archive_readiness") in ("YES", "DONE")
    )
    data["summary"]["archived_count"] = sum(
        1 for c in data["candidates"] if c.get("archive_readiness") == "DONE"
    )
    data["summary"]["migration_required_count"] = sum(
        1 for c in data["candidates"] if c.get("migration_required")
    )
    MATRIX.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return stats


if __name__ == "__main__":
    import pprint

    pprint.pp(expand())
