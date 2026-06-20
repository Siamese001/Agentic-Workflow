"""Build ranked ADG post-run action queue from gate results and optional P7 artifacts.

SSOT output: ``artifacts/adg/adg_action_queue_<ts>.json``

Plan: ``.codex/plans/adg-action-dispatch-c9e4a2.md`` (W1)
Schema: ``.codex/schemas/adg_action_queue.schema.json``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.reports.gate_signal_catalog import (
    display_verdict,
    display_verdict_sub,
    format_gate_signal,
    needs_fix,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
SCHEMA_PATH = REPO_ROOT / ".codex" / "schemas" / "adg_action_queue.schema.json"

DEFAULT_MAX_ACTIONS = 10
BAND_ORD = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "L_APP": 4}

SUB_TO_SORT_BUCKET = {
    "block": 0,
    "regr": 1,
    "seed": 2,
}


@dataclass(frozen=True)
class ProvenanceInput:
    artifact_key: str
    path: str
    snapshot_ts: str | None
    digest_sha256: str | None
    status: str
    required: bool
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_key": self.artifact_key,
            "path": self.path,
            "snapshot_ts": self.snapshot_ts,
            "digest_sha256": self.digest_sha256,
            "status": self.status,
            "required": self.required,
        }


def _repo_rel(path: Path, repo_root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize_ts(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.replace("Z", "+00:00")


def _ts_match(active: str | None, candidate: str | None) -> bool:
    a = _normalize_ts(active)
    c = _normalize_ts(candidate)
    if not a or not c:
        return False
    if a == c:
        return True
    return a[:19] == c[:19]


def _parse_ts_from_json(data: dict[str, Any]) -> str | None:
    for key in ("timestamp", "snapshot_ts", "generated_at", "active_snapshot_ts"):
        val = data.get(key)
        if val:
            return _normalize_ts(str(val))
    return None


def _parse_ts_from_filename(path: Path, prefix: str) -> str | None:
    stem = path.stem
    if not stem.startswith(prefix):
        return None
    suffix = stem[len(prefix) :]
    if len(suffix) >= 15 and suffix[8] == "_":
        # 20260525_120401 -> ISO-ish
        date_part, time_part = suffix.split("_", 1)
        if len(date_part) == 8 and len(time_part) >= 6:
            return (
                f"{date_part[0:4]}-{date_part[4:6]}-{date_part[6:8]}"
                f"T{time_part[0:2]}:{time_part[2:4]}:{time_part[4:6]}+00:00"
            )
    return None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_latest(glob_pattern: str, artifacts_dir: Path = ARTIFACTS_ADG) -> Path | None:
    candidates = sorted(artifacts_dir.glob(glob_pattern), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def _inspect_artifact(
    artifact_key: str,
    path: Path | None,
    *,
    required: bool,
    active_snapshot_ts: str | None,
    reject_unless_match: bool = False,
) -> ProvenanceInput:
    if path is None or not path.is_file():
        return ProvenanceInput(
            artifact_key=artifact_key,
            path=_repo_rel(path or (ARTIFACTS_ADG / f"{artifact_key}.missing")),
            snapshot_ts=None,
            digest_sha256=None,
            status="missing",
            required=required,
        )

    digest = _file_digest(path)
    try:
        data = _load_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        if required:
            raise ValueError(f"{artifact_key} malformed: {exc}") from exc
        return ProvenanceInput(
            artifact_key=artifact_key,
            path=_repo_rel(path),
            snapshot_ts=None,
            digest_sha256=digest,
            status="missing",
            required=required,
        )

    snap = _parse_ts_from_json(data) or _parse_ts_from_filename(path, f"adg_{artifact_key}_")
    if artifact_key == "gate_results":
        snap = _parse_ts_from_json(data) or snap
    if artifact_key == "p0_wave_plan":
        snap = snap or _parse_ts_from_filename(path, "p0_remediation_wave_plan_")

    status = "present"
    if reject_unless_match and active_snapshot_ts and snap and not _ts_match(active_snapshot_ts, snap):
        status = "stale" if snap else "rejected"
    elif reject_unless_match and active_snapshot_ts and not snap:
        status = "rejected"

    return ProvenanceInput(
        artifact_key=artifact_key,
        path=_repo_rel(path),
        snapshot_ts=snap,
        digest_sha256=digest,
        status=status,
        required=required,
        raw=data if status == "present" else None,
    )


def _validate_required_gate_results(data: dict[str, Any]) -> None:
    if not isinstance(data.get("gates"), list):
        raise ValueError("gate_results missing gates[]")
    if not data.get("timestamp"):
        raise ValueError("gate_results missing timestamp")


def _validate_required_burndown(data: dict[str, Any]) -> None:
    if "schema_version" not in data and "summary" not in data and "bands" not in data:
        raise ValueError("burndown missing schema_version/summary/bands")


def _regression_delta(gate: dict[str, Any]) -> int:
    count = int(gate.get("violation_count") or 0)
    baseline = gate.get("baseline_count")
    if baseline is None:
        return count
    try:
        return max(0, count - int(baseline))
    except (TypeError, ValueError):
        return count


def _fix_sort_key(gate: dict[str, Any]) -> tuple[int, int, int, int, str]:
    sub = display_verdict_sub(gate)
    bucket = SUB_TO_SORT_BUCKET.get(sub, 9)
    band = str(gate.get("band", "P3"))
    band_ord = BAND_ORD.get(band, 99)
    if sub == "regr":
        metric = _regression_delta(gate)
    else:
        metric = int(gate.get("violation_count") or 0)
    return (bucket, band_ord, metric, int(gate.get("violation_count") or 0), str(gate.get("gate_id", "")))


def _ordering_reason_for_fix(gate: dict[str, Any]) -> str:
    sub = display_verdict_sub(gate)
    band = str(gate.get("band", "P3")).lower()
    if sub == "block":
        return f"fix_block_{band}_violations_asc"
    if sub == "regr":
        return f"fix_regr_{band}_delta_asc"
    if sub == "seed":
        return f"fix_seed_{band}_violations_asc"
    return f"fix_{sub}_{band}"


def _build_fix_actions(gates: list[dict[str, Any]], source_digest: str) -> list[dict[str, Any]]:
    fix_gates = [g for g in gates if needs_fix(g)]
    fix_gates.sort(key=_fix_sort_key)
    rows: list[dict[str, Any]] = []
    for gate in fix_gates:
        sub = display_verdict_sub(gate)
        rows.append(
            {
                "verdict_cluster": "FIX",
                "gate_id": gate.get("gate_id"),
                "source_id": None,
                "action_kind": "fix_gate",
                "file_path": None,
                "symbol": None,
                "scoped_tests": [],
                "plan_hint": "immediate_session",
                "signal": format_gate_signal(gate),
                "sort_bucket": SUB_TO_SORT_BUCKET.get(sub, 9),
                "sort_band": str(gate.get("band", "P3")),
                "violation_count": int(gate.get("violation_count") or 0),
                "source_artifact": "gate_results",
                "source_digest": source_digest,
                "ordering_reason": _ordering_reason_for_fix(gate),
            }
        )
    return rows


def _build_p0_wave_actions(plan: dict[str, Any], source_digest: str, max_files: int = 3) -> list[dict[str, Any]]:
    if not plan.get("plan_required"):
        return []
    top_files = plan.get("top_files") or []
    rows: list[dict[str, Any]] = []
    for item in top_files[:max_files]:
        source_file = str(item.get("source_file") or "")
        if not source_file:
            continue
        rows.append(
            {
                "verdict_cluster": "P0_WAVE",
                "gate_id": None,
                "source_id": source_file,
                "action_kind": "p0_wave_file",
                "file_path": source_file,
                "symbol": None,
                "scoped_tests": [],
                "plan_hint": "p0_wave_session",
                "signal": f"P0 wave file; issues={item.get('issue_count', 0)}",
                "sort_bucket": 3,
                "sort_band": "P0",
                "violation_count": int(item.get("issue_count") or 0),
                "source_artifact": "p0_wave_plan",
                "source_digest": source_digest,
                "ordering_reason": "p0_wave_top_files_priority",
            }
        )
    return rows


def _build_refactor_actions(accelerator: dict[str, Any], source_digest: str, max_candidates: int = 3) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for cand in accelerator.get("candidates") or []:
        file_path = _candidate_path(cand)
        if not file_path or file_path in seen_paths:
            continue
        seen_paths.add(file_path)
        tests = cand.get("impacted_tests") or []
        if not isinstance(tests, list):
            tests = []
        dimensions = cand.get("dimensions") if isinstance(cand.get("dimensions"), dict) else {}
        rows.append(
            {
                "verdict_cluster": "REFACTOR",
                "gate_id": None,
                "source_id": file_path,
                "action_kind": "refactor_candidate",
                "file_path": file_path,
                "symbol": cand.get("symbol") or cand.get("adg_name"),
                "scoped_tests": [str(t) for t in tests[:5]],
                "plan_hint": "refactor_when_fix_clear",
                "signal": f"Refactor candidate; score={cand.get('score', cand.get('priority_score', 'n/a'))}",
                "sort_bucket": 4,
                "sort_band": str(cand.get("layer") or cand.get("band") or "L_APP"),
                "violation_count": _int_value(cand.get("violation_count"), dimensions.get("violations"), default=0),
                "source_artifact": "refactor_accelerator",
                "source_digest": source_digest,
                "ordering_reason": "refactor_accelerator_candidates_desc",
            }
        )
        if len(rows) >= max_candidates:
            break
    return rows


def _int_value(*values: Any, default: int = 0) -> int:
    for value in values:
        if value is None or value == "":
            continue
        try:
            return int(float(value))
        except (TypeError, ValueError):
            continue
    return default


def _float_value(*values: Any, default: float = 0.0) -> float:
    for value in values:
        if value is None or value == "":
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return default


def _candidate_path(cand: dict[str, Any]) -> str:
    for key in ("file_path", "path", "resolved_path", "file", "source_file", "module_path"):
        value = cand.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().replace("\\", "/")
    return ""


def _resolve_snapshot_from_gate_data(gate_data: dict[str, Any], repo_root: Path) -> Path | None:
    raw = gate_data.get("snapshot_path")
    if not raw and isinstance(gate_data.get("snapshot"), dict):
        raw = gate_data["snapshot"].get("path") or gate_data["snapshot"].get("sqlite_path")
    if not raw:
        return None
    path = Path(str(raw))
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve() if path.exists() else None


def _build_test_hotspot_actions(
    sqlite_snapshot_path: Path | None,
    source_digest: str,
    *,
    max_candidates: int = 3,
) -> list[dict[str, Any]]:
    """Promote mv_hotspot_coverage_risk into next-best testing actions when available."""
    if sqlite_snapshot_path is None or not sqlite_snapshot_path.is_file():
        return []

    rows: list[dict[str, Any]] = []
    try:
        con = sqlite3.connect(f"file:{sqlite_snapshot_path}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        try:
            has_mv = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name='mv_hotspot_coverage_risk'"
            ).fetchone()
            if not has_mv:
                return []
            result_rows = con.execute(
                """
                SELECT file, layer, priority_band, risk_band, coverage_band,
                       criticality_score, combined_risk_score, fan_in, fan_out,
                       violation_count, coverage_pct
                FROM mv_hotspot_coverage_risk
                WHERE priority_band IN ('P1_URGENT', 'P2_GAP')
                ORDER BY
                  CASE priority_band WHEN 'P1_URGENT' THEN 0 ELSE 1 END,
                  criticality_score DESC,
                  combined_risk_score DESC,
                  fan_in DESC,
                  file ASC
                LIMIT ?
                """,
                (max_candidates,),
            ).fetchall()
        finally:
            con.close()
    except (sqlite3.Error, OSError):
        return []

    for row in result_rows:
        file_path = str(row["file"] or "").replace("\\", "/")
        if not file_path:
            continue
        leaf = Path(file_path).stem
        coverage_pct = _float_value(row["coverage_pct"], default=-1.0)
        coverage_text = "absent" if coverage_pct < 0 else f"{coverage_pct:.1f}%"
        priority = str(row["priority_band"] or "P?_GAP")
        rows.append(
            {
                "verdict_cluster": "GRAPHDB",
                "gate_id": None,
                "source_id": file_path,
                "action_kind": "test_hotspot_gap",
                "file_path": file_path,
                "symbol": None,
                "scoped_tests": [f"tests/**/test_{leaf}.py"],
                "plan_hint": "test_hotspot_when_fix_clear",
                "signal": (
                    f"Test hotspot gap from mv_hotspot_coverage_risk; priority={priority}; "
                    f"risk={row['risk_band']}; coverage={row['coverage_band']} ({coverage_text}); "
                    f"criticality={_float_value(row['criticality_score']):.2f}; "
                    f"fan_in={_int_value(row['fan_in'])}"
                ),
                "sort_bucket": 3,
                "sort_band": priority,
                "violation_count": _int_value(row["violation_count"], default=0),
                "source_artifact": "sqlite:mv_hotspot_coverage_risk",
                "source_digest": source_digest,
                "ordering_reason": "mv_hotspot_coverage_risk_priority",
            }
        )
    return rows


def _build_structural_hotspot_actions(
    structural: dict[str, Any],
    source_digest: str,
    *,
    max_candidates: int = 3,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    blast_radius = structural.get("blast_radius") if isinstance(structural.get("blast_radius"), dict) else {}
    centrality = structural.get("centrality") if isinstance(structural.get("centrality"), dict) else {}
    for cand in blast_radius.get("hotspots") or []:
        if isinstance(cand, dict):
            item = dict(cand)
            item["_mv_source"] = "blast_radius.hotspots"
            candidates.append(item)
    for cand in centrality.get("nodes") or []:
        if isinstance(cand, dict):
            item = dict(cand)
            item["_mv_source"] = "centrality.nodes"
            candidates.append(item)

    def _rank(cand: dict[str, Any]) -> tuple[float, int, str]:
        return (
            _float_value(cand.get("centrality_score"), default=0.0),
            _int_value(cand.get("direct_fan_in"), cand.get("fan_in"), default=0),
            _candidate_path(cand),
        )

    rows: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for cand in sorted(candidates, key=_rank, reverse=True):
        file_path = _candidate_path(cand)
        if not file_path or file_path in seen_paths:
            continue
        seen_paths.add(file_path)
        fan_in = _int_value(cand.get("direct_fan_in"), cand.get("fan_in"), default=0)
        rows.append(
            {
                "verdict_cluster": "GRAPHDB",
                "gate_id": None,
                "source_id": file_path,
                "action_kind": "graphdb_hotspot",
                "file_path": file_path,
                "symbol": cand.get("adg_name") or cand.get("symbol"),
                "scoped_tests": [],
                "plan_hint": "graphdb_when_fix_clear",
                "signal": (
                    f"GraphDB/MV hotspot from {cand.get('_mv_source')}; "
                    f"fan_in={fan_in}; centrality={_float_value(cand.get('centrality_score')):.4f}"
                ),
                "sort_bucket": 5,
                "sort_band": str(cand.get("layer") or "L_APP"),
                "violation_count": 0,
                "source_artifact": "structural_outputs",
                "source_digest": source_digest,
                "ordering_reason": "structural_outputs_hotspot_desc",
            }
        )
        if len(rows) >= max_candidates:
            break
    return rows


def _list_at(data: dict[str, Any], dotted_path: str) -> list[Any]:
    current: Any = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return []
        current = current.get(part)
    return current if isinstance(current, list) else []


def _build_graphdb_structural_actions(
    graphdb: dict[str, Any],
    source_digest: str,
    *,
    max_candidates: int = 2,
) -> list[dict[str, Any]]:
    checks = [
        (
            "structural.uwg_durable_write_conformance",
            "UWG durable write conformance rows",
        ),
        ("structural.gravity_import_violations", "gravity import violations"),
        ("structural.illegal_layer_reach", "illegal layer reach rows"),
        (
            "structural.capability_tool_provider_chokepoint_conformance.providers.violations",
            "provider chokepoint conformance rows",
        ),
        ("structural.l2_lifecycle_conformance.non_conformant_modules", "L2 lifecycle non-conformant modules"),
    ]
    scored: list[tuple[int, str, str]] = []
    for key, label in checks:
        count = len(_list_at(graphdb, key))
        if count > 0:
            scored.append((count, key, label))
    scored.sort(reverse=True)

    rows: list[dict[str, Any]] = []
    for count, key, label in scored[:max_candidates]:
        rows.append(
            {
                "verdict_cluster": "GRAPHDB",
                "gate_id": None,
                "source_id": key,
                "action_kind": "graphdb_structural_signal",
                "file_path": None,
                "symbol": None,
                "scoped_tests": [],
                "plan_hint": "graphdb_when_fix_clear",
                "signal": (
                    f"GraphDB structural signal; rows={count}; {label}. "
                    "Inspect adg_graphdb_queries for concrete rows."
                ),
                "sort_bucket": 5,
                "sort_band": "GRAPHDB",
                "violation_count": count,
                "source_artifact": "graphdb_queries",
                "source_digest": source_digest,
                "ordering_reason": "graphdb_structural_signal_count_desc",
            }
        )
    return rows


def _apply_cap(
    rows: list[dict[str, Any]],
    max_actions: int,
) -> list[dict[str, Any]]:
    if len(rows) <= max_actions:
        return rows
    first_fix = next((r for r in rows if r.get("verdict_cluster") == "FIX"), None)
    trimmed = rows[:max_actions]
    if first_fix is not None and first_fix not in trimmed:
        trimmed = [first_fix] + [r for r in rows if r is not first_fix][: max_actions - 1]
    return trimmed


def _assign_ranks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        item = dict(row)
        item["rank"] = idx
        out.append(item)
    return out


def _count_verdicts(gates: list[dict[str, Any]]) -> tuple[int, int, int]:
    fix_n = track_n = clear_n = 0
    for gate in gates:
        cluster = display_verdict(gate)
        if cluster == "FIX":
            fix_n += 1
        elif cluster == "TRACK":
            track_n += 1
        else:
            clear_n += 1
    return fix_n, track_n, clear_n


def build_action_queue(
    *,
    gate_results_path: Path,
    burndown_path: Path,
    p0_wave_plan_path: Path | None = None,
    refactor_accelerator_path: Path | None = None,
    failure_clusters_path: Path | None = None,
    structural_outputs_path: Path | None = None,
    graphdb_queries_path: Path | None = None,
    sqlite_snapshot_path: Path | None = None,
    max_actions: int = DEFAULT_MAX_ACTIONS,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Build queue document; raises ValueError on required input failure."""
    gate_data = _load_json(gate_results_path)
    burndown_data = _load_json(burndown_path)
    _validate_required_gate_results(gate_data)
    _validate_required_burndown(burndown_data)

    active_ts = _normalize_ts(str(gate_data.get("timestamp", "")))
    if not active_ts:
        raise ValueError("gate_results missing timestamp")

    gate_prov = _inspect_artifact(
        "gate_results",
        gate_results_path,
        required=True,
        active_snapshot_ts=active_ts,
    )
    burndown_prov = _inspect_artifact(
        "burndown",
        burndown_path,
        required=True,
        active_snapshot_ts=active_ts,
    )
    p0_prov = _inspect_artifact(
        "p0_wave_plan",
        p0_wave_plan_path,
        required=False,
        active_snapshot_ts=active_ts,
    )
    accel_prov = _inspect_artifact(
        "refactor_accelerator",
        refactor_accelerator_path,
        required=False,
        active_snapshot_ts=active_ts,
    )
    cluster_prov = _inspect_artifact(
        "failure_clusters",
        failure_clusters_path,
        required=False,
        active_snapshot_ts=active_ts,
        reject_unless_match=True,
    )
    structural_prov = _inspect_artifact(
        "structural_outputs",
        structural_outputs_path,
        required=False,
        active_snapshot_ts=active_ts,
    )
    graphdb_prov = _inspect_artifact(
        "graphdb_queries",
        graphdb_queries_path,
        required=False,
        active_snapshot_ts=active_ts,
    )

    degradation: list[str] = []
    if p0_prov.status == "missing":
        degradation.append("p0_wave_plan missing")
    elif p0_prov.status == "stale":
        degradation.append("p0_wave_plan stale vs active snapshot")
    if accel_prov.status == "missing":
        degradation.append("refactor_accelerator missing")
    elif accel_prov.status == "stale":
        degradation.append("refactor_accelerator stale vs active snapshot")
    if cluster_prov.status == "stale":
        degradation.append("failure_clusters stale — excluded from merge")
    elif cluster_prov.status == "rejected":
        degradation.append("failure_clusters rejected — excluded from merge")
    if structural_prov.status == "missing":
        degradation.append("structural_outputs missing")
    elif structural_prov.status == "stale":
        degradation.append("structural_outputs stale vs active snapshot")
    if graphdb_prov.status == "missing":
        degradation.append("graphdb_queries missing")
    elif graphdb_prov.status == "stale":
        degradation.append("graphdb_queries stale vs active snapshot")

    gates = gate_data.get("gates") or []
    fix_n, track_n, clear_n = _count_verdicts(gates)

    assert gate_prov.digest_sha256
    fix_rows = _build_fix_actions(gates, gate_prov.digest_sha256)

    combined = list(fix_rows)
    if p0_prov.status == "present" and p0_prov.raw:
        combined.extend(_build_p0_wave_actions(p0_prov.raw, p0_prov.digest_sha256 or ""))

    snapshot_path = sqlite_snapshot_path or _resolve_snapshot_from_gate_data(gate_data, repo_root)
    combined.extend(_build_test_hotspot_actions(snapshot_path, gate_prov.digest_sha256))

    fix_count = len(fix_rows)
    if accel_prov.status == "present" and accel_prov.raw and (fix_count < max_actions or not fix_rows):
        combined.extend(_build_refactor_actions(accel_prov.raw, accel_prov.digest_sha256 or ""))
    if structural_prov.status == "present" and structural_prov.raw and (fix_count < max_actions or not fix_rows):
        combined.extend(_build_structural_hotspot_actions(structural_prov.raw, structural_prov.digest_sha256 or ""))
    if graphdb_prov.status == "present" and graphdb_prov.raw and (fix_count < max_actions or not fix_rows):
        combined.extend(_build_graphdb_structural_actions(graphdb_prov.raw, graphdb_prov.digest_sha256 or ""))

    combined = _apply_cap(combined, max_actions)
    actions = _assign_ranks(combined)

    degraded = bool(degradation)
    emit_status = "degraded" if degraded else "ok"

    return {
        "schema_version": "1.0",
        "snapshot_ts": active_ts,
        "emit_status": emit_status,
        "provenance": {
            "active_snapshot_ts": active_ts,
            "degraded": degraded,
            "degradation_reasons": degradation,
            "inputs": [
                gate_prov.to_dict(),
                burndown_prov.to_dict(),
                p0_prov.to_dict(),
                accel_prov.to_dict(),
                cluster_prov.to_dict(),
                structural_prov.to_dict(),
                graphdb_prov.to_dict(),
            ],
        },
        "summary": {
            "fix_count": fix_n,
            "track_count": track_n,
            "clear_count": clear_n,
            "actions_emitted": len(actions),
            "max_actions": max_actions,
            "recommended_rank": 1,
            "degraded": degraded,
        },
        "actions": actions,
    }


def validate_action_queue(doc: dict[str, Any], schema_path: Path = SCHEMA_PATH) -> list[str]:
    """Return validation errors; empty list means valid."""
    errors: list[str] = []

    try:
        import jsonschema

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        for err in sorted(validator.iter_errors(doc), key=lambda e: e.path):
            errors.append(str(err.message))
    except ImportError:
        pass

    required_top = {
        "schema_version",
        "snapshot_ts",
        "emit_status",
        "provenance",
        "summary",
        "actions",
    }
    for key in required_top:
        if key not in doc:
            errors.append(f"missing top-level field: {key}")

    actions = doc.get("actions") or []
    max_actions = int(doc.get("summary", {}).get("max_actions", DEFAULT_MAX_ACTIONS))
    if len(actions) > max_actions:
        errors.append(f"actions length {len(actions)} exceeds max_actions {max_actions}")

    ranks = [a.get("rank") for a in actions]
    if ranks != list(range(1, len(ranks) + 1)):
        errors.append("actions ranks must be monotonic 1..N")

    for action in actions:
        if action.get("verdict_cluster") == "TRACK":
            errors.append("TRACK must not appear in actions")
        if not action.get("gate_id") and not action.get("source_id"):
            errors.append("action missing gate_id and source_id")

    fix_ranks = [a["rank"] for a in actions if a.get("verdict_cluster") == "FIX"]
    non_fix_ranks = [a["rank"] for a in actions if a.get("verdict_cluster") != "FIX"]
    if fix_ranks and non_fix_ranks and min(non_fix_ranks) < max(fix_ranks):
        errors.append("non-FIX action outranks FIX")

    return errors


def notion_fix_idempotency_key(
    gate_id: str,
    snapshot_ts: str,
    source_digest: str,
) -> str:
    """Idempotency key for W3 Notion rows: gate_id + snapshot_ts, else gate_id + source_digest."""
    if snapshot_ts:
        return f"{gate_id}+{snapshot_ts}"
    return f"{gate_id}+{source_digest}"


def extract_notion_fix_rows(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Rows eligible for W3 Notion FIX backlog sync (FIX gates only)."""
    snap = str(doc.get("snapshot_ts") or "")
    out: list[dict[str, Any]] = []
    for action in doc.get("actions") or []:
        if action.get("verdict_cluster") != "FIX":
            continue
        gate_id = action.get("gate_id")
        if not gate_id:
            continue
        digest = str(action.get("source_digest") or "")
        out.append(
            {
                "gate_id": gate_id,
                "snapshot_ts": snap,
                "idempotency_key": notion_fix_idempotency_key(gate_id, snap, digest),
                "source_digest": digest,
                "signal": action.get("signal", ""),
                "rank": action.get("rank"),
                "sort_band": action.get("sort_band", "P3"),
                "ordering_reason": action.get("ordering_reason", ""),
                "violation_count": action.get("violation_count", 0),
            }
        )
    return out


def render_markdown_table(doc: dict[str, Any], top: int = 10) -> str:
    lines = [
        "# ADG Action Queue (triage)",
        "",
        f"- **snapshot_ts:** {doc.get('snapshot_ts')}",
        f"- **emit_status:** {doc.get('emit_status')}",
        f"- **degraded:** {doc.get('provenance', {}).get('degraded')}",
        "",
        "| Rank | Lane | Kind | Target | ordering_reason | signal |",
        "|-----:|------|------|--------|-----------------|--------|",
    ]
    for action in (doc.get("actions") or [])[:top]:
        target = action.get("gate_id") or action.get("source_id") or "?"
        lines.append(
            f"| {action.get('rank')} | {action.get('verdict_cluster')} | "
            f"{action.get('action_kind')} | `{target}` | "
            f"{action.get('ordering_reason')} | {action.get('signal', '')[:80]} |"
        )
    if doc.get("provenance", {}).get("degradation_reasons"):
        lines.extend(["", "**Degraded inputs:**"])
        for reason in doc["provenance"]["degradation_reasons"]:
            lines.append(f"- {reason}")
    return "\n".join(lines) + "\n"


def emit_adg_action_queue(
    *,
    gate_results: Path | None = None,
    burndown: Path | None = None,
    p0_wave_plan: Path | None = None,
    refactor_accelerator: Path | None = None,
    failure_clusters: Path | None = None,
    structural_outputs: Path | None = None,
    graphdb_queries: Path | None = None,
    sqlite_snapshot: Path | None = None,
    output_path: Path | None = None,
    ts: str | None = None,
    max_actions: int = DEFAULT_MAX_ACTIONS,
    fail_closed: bool = True,
    repo_root: Path = REPO_ROOT,
) -> tuple[int, Path | None]:
    """Emit queue JSON. Returns (exit_code, path_or_none)."""
    artifacts = repo_root / "artifacts" / "adg"
    gate_path = gate_results or _resolve_latest("adg_gate_results_*.json", artifacts)
    burndown_path = burndown or (artifacts / "adg_burndown_table.json")

    if gate_path is None or not gate_path.is_file():
        msg = "required gate_results not found"
        print(f"[adg_action_queue] NEXT_ACTION_ERROR={msg}", file=sys.stderr)
        return (1 if fail_closed else 0, None)
    if not burndown_path.is_file():
        msg = "required burndown table not found"
        print(f"[adg_action_queue] NEXT_ACTION_ERROR={msg}", file=sys.stderr)
        return (1 if fail_closed else 0, None)

    if p0_wave_plan is None and ts:
        candidate = artifacts / "issues" / f"p0_remediation_wave_plan_{ts}.json"
        if candidate.is_file():
            p0_wave_plan = candidate
    if p0_wave_plan is None:
        p0_wave_plan = _resolve_latest("issues/p0_remediation_wave_plan_*.json", artifacts)

    if refactor_accelerator is None:
        if ts:
            candidate = artifacts / f"adg_refactor_accelerator_{ts}.json"
            if candidate.is_file():
                refactor_accelerator = candidate
    if refactor_accelerator is None:
        refactor_accelerator = _resolve_latest("adg_refactor_accelerator_*.json", artifacts)

    if failure_clusters is None:
        fc = artifacts / "adg_failure_clusters.json"
        failure_clusters = fc if fc.is_file() else None

    if structural_outputs is None:
        if ts:
            candidate = artifacts / f"adg_structural_outputs_{ts}.json"
            if candidate.is_file():
                structural_outputs = candidate
    if structural_outputs is None:
        structural_outputs = _resolve_latest("adg_structural_outputs_*.json", artifacts)

    if graphdb_queries is None:
        if ts:
            candidate = artifacts / f"adg_graphdb_queries_{ts}.json"
            if candidate.is_file():
                graphdb_queries = candidate
    if graphdb_queries is None:
        graphdb_queries = _resolve_latest("adg_graphdb_queries_*.json", artifacts)

    try:
        doc = build_action_queue(
            gate_results_path=gate_path,
            burndown_path=burndown_path,
            p0_wave_plan_path=p0_wave_plan,
            refactor_accelerator_path=refactor_accelerator,
            failure_clusters_path=failure_clusters,
            structural_outputs_path=structural_outputs,
            graphdb_queries_path=graphdb_queries,
            sqlite_snapshot_path=sqlite_snapshot,
            max_actions=max_actions,
            repo_root=repo_root,
        )
    except ValueError as exc:
        print(f"[adg_action_queue] NEXT_ACTION_ERROR={exc}", file=sys.stderr)
        return (1 if fail_closed else 0, None)

    val_errors = validate_action_queue(doc)
    if val_errors:
        print(f"[adg_action_queue] NEXT_ACTION_ERROR=validation: {val_errors[0]}", file=sys.stderr)
        return (1 if fail_closed else 0, None)

    if output_path is None:
        if ts:
            out_name = f"adg_action_queue_{ts}.json"
        else:
            stem = gate_path.stem.replace("adg_gate_results_", "")
            out_name = f"adg_action_queue_{stem}.json"
        output_path = artifacts / out_name

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rel = _repo_rel(output_path, repo_root)
    print(f"[adg_action_queue] NEXT_ACTION={rel}", file=sys.stderr)
    if doc.get("emit_status") == "degraded":
        print("[adg_action_queue] NEXT_ACTION_DEGRADED=1", file=sys.stderr)
    return (0, output_path)


def emit_adg_action_queue_from_adg_run(
    *,
    adg_artifacts_dir: Path,
    ts: str,
    fail_closed: bool = False,
) -> tuple[int, Path | None]:
    """Non-blocking hook for generate_full_adg (fail_closed=False preserves ADG exit)."""
    try:
        return emit_adg_action_queue(
            gate_results=None,
            burndown=adg_artifacts_dir / "adg_burndown_table.json",
            ts=ts,
            fail_closed=fail_closed,
            repo_root=adg_artifacts_dir.parent.parent,
        )
    except Exception as exc:
        print(f"[adg_action_queue] NEXT_ACTION_ERROR={exc}", file=sys.stderr)
        return (0 if not fail_closed else 1, None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit ADG post-run action queue JSON.")
    parser.add_argument("--gate-results", type=Path, default=None)
    parser.add_argument("--burndown", type=Path, default=None)
    parser.add_argument("--p0-wave-plan", type=Path, default=None)
    parser.add_argument("--refactor-accelerator", type=Path, default=None)
    parser.add_argument("--failure-clusters", type=Path, default=None)
    parser.add_argument("--structural-outputs", type=Path, default=None)
    parser.add_argument("--graphdb-queries", type=Path, default=None)
    parser.add_argument("--sqlite-snapshot", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--ts", type=str, default=None)
    parser.add_argument("--max-actions", type=int, default=DEFAULT_MAX_ACTIONS)
    parser.add_argument("--latest", action="store_true", help="Use latest gate_results under artifacts/adg")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="json writes file; markdown prints triage table to stdout",
    )
    args = parser.parse_args(argv)

    if args.format == "markdown" and args.latest:
        gate = _resolve_latest("adg_gate_results_*.json", ARTIFACTS_ADG)
        burndown = ARTIFACTS_ADG / "adg_burndown_table.json"
        if not gate or not burndown.is_file():
            print("missing gate_results or burndown", file=sys.stderr)
            return 1
        doc = build_action_queue(
            gate_results_path=gate,
            burndown_path=burndown,
            p0_wave_plan_path=_resolve_latest("issues/p0_remediation_wave_plan_*.json", ARTIFACTS_ADG),
            refactor_accelerator_path=_resolve_latest("adg_refactor_accelerator_*.json", ARTIFACTS_ADG),
            failure_clusters_path=(
                ARTIFACTS_ADG / "adg_failure_clusters.json"
                if (ARTIFACTS_ADG / "adg_failure_clusters.json").is_file()
                else None
            ),
            structural_outputs_path=_resolve_latest("adg_structural_outputs_*.json", ARTIFACTS_ADG),
            graphdb_queries_path=_resolve_latest("adg_graphdb_queries_*.json", ARTIFACTS_ADG),
            sqlite_snapshot_path=args.sqlite_snapshot,
            max_actions=args.max_actions,
        )
        print(render_markdown_table(doc, top=args.top))
        return 0

    rc, path = emit_adg_action_queue(
        gate_results=args.gate_results,
        burndown=args.burndown,
        p0_wave_plan=args.p0_wave_plan,
        refactor_accelerator=args.refactor_accelerator,
        failure_clusters=args.failure_clusters,
        structural_outputs=args.structural_outputs,
        graphdb_queries=args.graphdb_queries,
        sqlite_snapshot=args.sqlite_snapshot,
        output_path=args.out,
        ts=args.ts,
        max_actions=args.max_actions,
        fail_closed=True,
    )
    if rc == 0 and path and args.format == "markdown":
        doc = _load_json(path)
        print(render_markdown_table(doc, top=args.top))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
