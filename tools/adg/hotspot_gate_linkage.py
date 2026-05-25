"""Deterministic gate linkage for ADG app hotspot reports (plan adg-action-dispatch-c9e4a2 W2).

Linkage sources (no markdown grep, no invented gate ids):
  - gate_results: action-queue file_path -> gate_id; P-view consumer_file -> gate_id
  - MV: mv_debt_concentration_hotspots.file match
  - accelerator: candidates[].file_path exact match
  - unknown: explicit missing confidence when no join
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"

# P-view name -> gate_id (SSOT: ops_scripts/ci/adg_gates/unified_registry.py notes)
P_VIEW_TO_GATE_ID: dict[str, str] = {
    "v_p0_apps_direct_infra": "10_infra_wiring",
    "v_p0_write_bypass_uwg": "C1_uwg_bypass_pview",
    "v_p0_provider_bypass": "C2_l5_bypass_pview",
    "v_p0_l1_direct_infra": "10_infra_wiring",
    "v_p0_l6_mutation": "3_write_sovereignty",
    "v_p0_l0_raw_execution": "5_text_to_action",
}


@dataclass
class HotspotLinkage:
    module_path: str
    linked_gate_ids: list[str] = field(default_factory=list)
    violation_refs: list[str] = field(default_factory=list)
    impacted_tests_sample: list[str] = field(default_factory=list)
    linkage_source: str = "unknown"
    linkage_confidence: str = "missing"

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_path": self.module_path,
            "linked_gate_ids": list(self.linked_gate_ids),
            "violation_refs": list(self.violation_refs),
            "impacted_tests_sample": list(self.impacted_tests_sample),
            "linkage_source": self.linkage_source,
            "linkage_confidence": self.linkage_confidence,
        }


@dataclass
class LinkageContext:
    queue_file_to_gate: dict[str, str] = field(default_factory=dict)
    accelerator_by_file: dict[str, dict[str, Any]] = field(default_factory=dict)
    mv_debt_files: set[str] = field(default_factory=set)
    pview_file_to_gates: dict[str, set[str]] = field(default_factory=dict)
    violation_refs_by_file: dict[str, list[str]] = field(default_factory=dict)


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip().lstrip("./")


def _resolve_latest(glob_pattern: str, root: Path = ARTIFACTS_ADG) -> Path | None:
    hits = sorted(root.glob(glob_pattern), key=lambda p: p.stat().st_mtime)
    return hits[-1] if hits else None


def load_linkage_context(
    *,
    repo_root: Path = REPO_ROOT,
    gate_results_path: Path | None = None,
    action_queue_path: Path | None = None,
    refactor_accelerator_path: Path | None = None,
    sqlite_connection: Any | None = None,
) -> LinkageContext:
    """Build indexes from gate_results queue, accelerator, sqlite MVs/P-views/violations."""
    artifacts = repo_root / "artifacts" / "adg"
    ctx = LinkageContext()

    queue_path = action_queue_path or _resolve_latest("adg_action_queue_*.json", artifacts)
    if queue_path and queue_path.is_file():
        doc = json.loads(queue_path.read_text(encoding="utf-8"))
        for action in doc.get("actions") or []:
            fp = action.get("file_path") or action.get("source_id")
            gate_id = action.get("gate_id")
            if fp and gate_id:
                ctx.queue_file_to_gate[_normalize_path(str(fp))] = str(gate_id)

    accel_path = refactor_accelerator_path or _resolve_latest("adg_refactor_accelerator_*.json", artifacts)
    if accel_path and accel_path.is_file():
        doc = json.loads(accel_path.read_text(encoding="utf-8"))
        for cand in doc.get("candidates") or []:
            fp = _normalize_path(str(cand.get("file_path") or cand.get("path") or ""))
            if fp:
                ctx.accelerator_by_file[fp] = cand

    if sqlite_connection is not None:
        _load_sqlite_linkage(ctx, sqlite_connection)

    return ctx


def _load_sqlite_linkage(ctx: LinkageContext, con: Any) -> None:
    """Populate MV, P-view, and violations indexes from ADG sqlite."""
    try:
        if con.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') "
            "AND name='mv_debt_concentration_hotspots'"
        ).fetchone():
            for row in con.execute("SELECT file FROM mv_debt_concentration_hotspots").fetchall():
                if row[0]:
                    ctx.mv_debt_files.add(_normalize_path(str(row[0])))
    except Exception:
        pass

    for view_name, gate_id in P_VIEW_TO_GATE_ID.items():
        try:
            exists = con.execute(
                "SELECT name FROM sqlite_master WHERE type='view' AND name=?",
                (view_name,),
            ).fetchone()
            if not exists:
                continue
            cols = {r[1] for r in con.execute(f"PRAGMA table_info({view_name})").fetchall()}
            file_col = "consumer_file" if "consumer_file" in cols else "source_file" if "source_file" in cols else None
            if not file_col:
                continue
            for row in con.execute(f"SELECT DISTINCT {file_col} FROM {view_name}").fetchall():
                fp = _normalize_path(str(row[0] or ""))
                if fp:
                    ctx.pview_file_to_gates.setdefault(fp, set()).add(gate_id)
        except Exception:
            continue

    try:
        if con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='violations'"
        ).fetchone():
            rows = con.execute(
                """
                SELECT id, file_path, violation_class, severity
                FROM violations
                WHERE file_path IS NOT NULL AND file_path != ''
                LIMIT 500000
                """
            ).fetchall()
            for vid, fpath, vclass, sev in rows:
                fp = _normalize_path(str(fpath))
                ref = f"violations:{vid}:{vclass}:{sev}"
                ctx.violation_refs_by_file.setdefault(fp, []).append(ref)
    except Exception:
        pass


def resolve_module_linkage(module_path: str, ctx: LinkageContext) -> HotspotLinkage:
    """Resolve deterministic linkage for one module path."""
    path = _normalize_path(module_path)
    linkage = HotspotLinkage(module_path=path)

    linkage.violation_refs = (ctx.violation_refs_by_file.get(path) or [])[:10]

    if path in ctx.accelerator_by_file:
        cand = ctx.accelerator_by_file[path]
        tests = cand.get("impacted_tests") or []
        if isinstance(tests, list):
            linkage.impacted_tests_sample = [str(t) for t in tests[:5]]
        linkage.linkage_source = "accelerator"
        linkage.linkage_confidence = "exact"
        gates: set[str] = set()
        if path in ctx.queue_file_to_gate:
            gates.add(ctx.queue_file_to_gate[path])
        linkage.linked_gate_ids = sorted(gates)
        return linkage

    gates: set[str] = set()
    if path in ctx.queue_file_to_gate:
        gates.add(ctx.queue_file_to_gate[path])
        linkage.linkage_source = "gate_results"
        linkage.linkage_confidence = "exact"

    if path in ctx.pview_file_to_gates:
        gates.update(ctx.pview_file_to_gates[path])
        linkage.linkage_source = "gate_results"
        linkage.linkage_confidence = "exact"

    if path in ctx.mv_debt_files:
        if linkage.linkage_source == "unknown":
            linkage.linkage_source = "MV"
            linkage.linkage_confidence = "inferred"
        elif linkage.linkage_confidence == "inferred":
            linkage.linkage_confidence = "inferred"

    linkage.linked_gate_ids = sorted(gates)

    if linkage.linkage_source == "unknown":
        linkage.linkage_confidence = "missing"

    return linkage


def top_module_paths_from_scan(scan: dict[str, Any], *, limit: int = 5) -> list[str]:
    """Pick top-N module paths from fan-in / MV rows (deterministic order)."""
    seen: list[str] = []
    for row in scan.get("top_fanin") or []:
        if row and row[0] != "__error__" and len(row) > 1:
            path = _normalize_path(str(row[1]))
            if path and path not in seen:
                seen.append(path)
        if len(seen) >= limit:
            return seen[:limit]
    if _table_has_paths(scan, "mv_hotspot_centrality"):
        for row in scan.get("mv_hotspot_centrality") or []:
            if row and row[0] != "__error__":
                for cell in row:
                    if isinstance(cell, str) and "/" in cell and cell.endswith(".py"):
                        path = _normalize_path(cell)
                        if path not in seen:
                            seen.append(path)
                    if len(seen) >= limit:
                        return seen[:limit]
    return seen[:limit]


def _table_has_paths(scan: dict[str, Any], key: str) -> bool:
    val = scan.get(key)
    return bool(val) and val is not None and val != [(("__error__", "missing"))]
