"""Evidence breakout helpers for executive ADG reports."""

from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SPINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")
SPINE_ORDINALS = {layer: idx for idx, layer in enumerate(SPINE_LAYERS)}


def _fmt_int(value: Any) -> str:
    try:
        return f"{int(value or 0):,}"
    except (TypeError, ValueError):
        return "0"


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    try:
        return [str(row[1]) for row in conn.execute(f'PRAGMA table_info("{table}")')]
    except sqlite3.Error:
        return []


def _gap_layers(src_layer: str, dst_layer: str) -> list[str]:
    a = SPINE_ORDINALS.get(src_layer)
    b = SPINE_ORDINALS.get(dst_layer)
    if a is None or b is None:
        return []
    if abs(a - b) <= 1:
        return []
    lo, hi = sorted((a, b))
    return [SPINE_LAYERS[idx] for idx in range(lo + 1, hi)]


def _build_group_summary(groups: list[dict[str, Any]], *, empty_fallback: str) -> str:
    if not groups:
        return empty_fallback
    if len(groups) == 1:
        group = groups[0]
        return group.get("summary") or empty_fallback
    lead = groups[0].get("summary") or empty_fallback
    extra = f"{len(groups)} breakout groups"
    return f"{lead}; {extra}"


def _top_pairs(rows: list[dict[str, Any]], *, src_key: str, dst_key: str, limit: int = 3) -> list[dict[str, Any]]:
    counter: Counter[tuple[str, str]] = Counter()
    for row in rows:
        src = str(row.get(src_key) or "").strip()
        dst = str(row.get(dst_key) or "").strip()
        if src and dst:
            counter[(src, dst)] += 1
    top: list[dict[str, Any]] = []
    for (src, dst), count in counter.most_common(limit):
        top.append({"src": src, "dst": dst, "count": count})
    return top


def _top_files(rows: list[dict[str, Any]], *, path_key: str, line_key: str | None = None, limit: int = 3) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    lines: dict[str, int] = {}
    for row in rows:
        path = str(row.get(path_key) or "").strip()
        if not path:
            continue
        counter[path] += 1
        if line_key and path not in lines:
            lines[path] = _int(row.get(line_key), 0)
    top: list[dict[str, Any]] = []
    for path, count in counter.most_common(limit):
        entry = {"path": path, "count": count}
        if path in lines and lines[path]:
            entry["line_no"] = lines[path]
        top.append(entry)
    return top


def _format_pair_samples(pairs: list[dict[str, Any]], *, joiner: str = " to ") -> str:
    if not pairs:
        return ""
    samples = [f"{pair['count']} links from {pair['src']}{joiner}{pair['dst']}" for pair in pairs[:3]]
    if len(samples) == 1:
        return samples[0]
    if len(samples) == 2:
        return f"{samples[0]} and {samples[1]}"
    return f"{samples[0]}, {samples[1]}, and {samples[2]}"


def _format_count_and_delta(gate: dict[str, Any]) -> tuple[int, str, int, str]:
    count = _int(gate.get("violation_count"))
    baseline = gate.get("baseline_count")
    if baseline in (None, ""):
        return count, "", 0, ""
    base = _int(baseline)
    delta = count - base
    return count, _fmt_int(base), delta, f"+{delta} above baseline {base}"


def build_layer_skip_breakout(sqlite_path: Path, gate_id: str, limit: int = 10) -> dict[str, Any]:
    if not sqlite_path.is_file():
        return {
            "status": "missing",
            "finding_name": "direct dependency links",
            "summary": "breakout unavailable",
            "groups": [],
            "samples": [],
            "note": f"{gate_id} breakout unavailable because the SQLite snapshot is missing.",
        }

    rows: list[dict[str, Any]] = []
    with sqlite3.connect(sqlite_path) as conn:
        conn.row_factory = sqlite3.Row
        try:
            rows = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT
                        src.resolved_path AS src_path,
                        src.layer AS src_layer,
                        dst.resolved_path AS dst_path,
                        dst.layer AS dst_layer
                    FROM edges e
                    JOIN nodes src ON src.id = e.src_id
                    JOIN nodes dst ON dst.id = e.dst_id
                    WHERE e.relation_type = 'imports'
                      AND src.layer IN ('L0','L1','L2','L3','L4','L5','L6')
                      AND dst.layer IN ('L0','L1','L2','L3','L4','L5','L6')
                      AND src.resolved_path IS NOT NULL
                      AND dst.resolved_path IS NOT NULL
                    """
                )
            ]
        except sqlite3.Error:
            rows = []

    filtered: list[dict[str, Any]] = []
    for row in rows:
        src_layer = str(row.get("src_layer") or "").strip()
        dst_layer = str(row.get("dst_layer") or "").strip()
        gap_layers = _gap_layers(src_layer, dst_layer)
        if not gap_layers:
            continue
        filtered.append(
            {
                "src_path": str(row.get("src_path") or "").strip(),
                "src_layer": src_layer,
                "dst_path": str(row.get("dst_path") or "").strip(),
                "dst_layer": dst_layer,
                "skip_layers": gap_layers,
                "skip_distance": len(gap_layers),
            }
        )

    if not filtered:
        return {
            "status": "missing",
            "finding_name": "direct dependency links",
            "summary": "breakout unavailable",
            "groups": [],
            "samples": [],
            "note": f"{gate_id} breakout unavailable because no layer-skip rows were found.",
        }

    group_rows: dict[tuple[str, str, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for row in filtered:
        key = (row["src_layer"], row["dst_layer"], tuple(row["skip_layers"]))
        group_rows[key].append(row)

    groups: list[dict[str, Any]] = []
    for (src_layer, dst_layer, skip_layers), bucket in sorted(
        group_rows.items(),
        key=lambda item: (-len(item[1]), item[0][0], item[0][1]),
    ):
        pair_counts = _top_pairs(bucket, src_key="src_path", dst_key="dst_path", limit=limit)
        groups.append(
            {
                "src_layer": src_layer,
                "dst_layer": dst_layer,
                "skip_layers": list(skip_layers),
                "count": len(bucket),
                "summary": f"All +{len(bucket)} are direct dependency links from {src_layer} -> {dst_layer}, skipping {'/'.join(skip_layers) if skip_layers else 'no intermediate layers'}",
                "top_pairs": pair_counts,
                "samples": bucket[:limit],
            }
        )

    top_group = groups[0]
    samples = top_group.get("top_pairs") or []
    if not samples:
        samples = [{"src": row["src_path"], "dst": row["dst_path"], "count": 1} for row in filtered[:limit]]

    return {
        "status": "present",
        "finding_name": "direct dependency links",
        "summary": top_group["summary"],
        "groups": groups,
        "samples": samples,
        "sample_findings": filtered[:limit],
        "top_sources": samples,
    }


def build_l5_bypass_breakout(sqlite_path: Path, gate_id: str, limit: int = 10) -> dict[str, Any]:
    if not sqlite_path.is_file():
        return {
            "status": "missing",
            "finding_name": "provider/tool calls bypassing the L5 gateway",
            "summary": "breakout unavailable",
            "groups": [],
            "samples": [],
            "note": f"{gate_id} breakout unavailable because the SQLite snapshot is missing.",
        }

    rows: list[dict[str, Any]] = []
    with sqlite3.connect(sqlite_path) as conn:
        conn.row_factory = sqlite3.Row
        if not _table_columns(conn, "mv_gateway_bypass_paths"):
            return {
                "status": "missing",
                "finding_name": "provider/tool calls bypassing the L5 gateway",
                "summary": "breakout unavailable",
                "groups": [],
                "samples": [],
                "note": f"{gate_id} breakout unavailable because mv_gateway_bypass_paths is missing.",
            }
        try:
            rows = [dict(row) for row in conn.execute("SELECT src_file, src_layer, provider_symbol, line_no, bypass_type FROM mv_gateway_bypass_paths")]
        except sqlite3.Error:
            rows = []

    if not rows:
        return {
            "status": "missing",
            "finding_name": "provider/tool calls bypassing the L5 gateway",
            "summary": "breakout unavailable",
            "groups": [],
            "samples": [],
            "note": f"{gate_id} breakout unavailable because mv_gateway_bypass_paths produced no rows.",
        }

    group_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        group_rows[(str(row.get("src_layer") or "").strip(), str(row.get("bypass_type") or "").strip())].append(row)

    groups: list[dict[str, Any]] = []
    for (src_layer, bypass_type), bucket in sorted(group_rows.items(), key=lambda item: (-len(item[1]), item[0][0], item[0][1])):
        pairs = _top_files(bucket, path_key="src_file", line_key="line_no", limit=limit)
        groups.append(
            {
                "src_layer": src_layer,
                "bypass_type": bypass_type,
                "count": len(bucket),
                "summary": f"{len(bucket)} provider/tool calls from {src_layer} bypass the L5 gateway",
                "top_sources": pairs,
                "samples": bucket[:limit],
            }
        )

    top_group = groups[0]
    return {
        "status": "present",
        "finding_name": "provider/tool calls bypassing the L5 gateway",
        "summary": top_group["summary"],
        "groups": groups,
        "samples": top_group.get("top_sources") or [],
        "sample_findings": rows[:limit],
        "top_sources": top_group.get("top_sources") or [],
    }


def build_untyped_seam_breakout(sqlite_path: Path, gate_id: str, limit: int = 10) -> dict[str, Any]:
    if not sqlite_path.is_file():
        return {
            "status": "missing",
            "finding_name": "cross-layer imports with empty type surfaces",
            "summary": "breakout unavailable",
            "groups": [],
            "samples": [],
            "note": f"{gate_id} breakout unavailable because the SQLite snapshot is missing.",
        }

    rows: list[dict[str, Any]] = []
    with sqlite3.connect(sqlite_path) as conn:
        conn.row_factory = sqlite3.Row
        try:
            rows = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT
                        src.resolved_path AS src_path,
                        src.layer AS src_layer,
                        dst.resolved_path AS dst_path,
                        dst.layer AS dst_layer
                    FROM edges e
                    JOIN nodes src ON src.id = e.src_id
                    JOIN nodes dst ON dst.id = e.dst_id
                    WHERE e.relation_type = 'imports'
                      AND src.layer IN ('L0','L1','L2','L3','L4','L5','L6')
                      AND dst.layer IN ('L0','L1','L2','L3','L4','L5','L6')
                      AND src.layer <> dst.layer
                      AND (dst.type_surface IS NULL OR dst.type_surface = '')
                      AND src.resolved_path IS NOT NULL
                      AND dst.resolved_path IS NOT NULL
                    """
                )
            ]
        except sqlite3.Error:
            rows = []

    if not rows:
        return {
            "status": "missing",
            "finding_name": "cross-layer imports with empty type surfaces",
            "summary": "breakout unavailable",
            "groups": [],
            "samples": [],
            "note": f"{gate_id} breakout unavailable because no cross-layer untyped-seam rows were found.",
        }

    group_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        group_rows[(str(row.get("src_layer") or "").strip(), str(row.get("dst_layer") or "").strip())].append(row)

    groups: list[dict[str, Any]] = []
    for (src_layer, dst_layer), bucket in sorted(group_rows.items(), key=lambda item: (-len(item[1]), item[0][0], item[0][1])):
        pairs = _top_pairs(bucket, src_key="src_path", dst_key="dst_path", limit=limit)
        groups.append(
            {
                "src_layer": src_layer,
                "dst_layer": dst_layer,
                "count": len(bucket),
                "summary": f"{len(bucket)} cross-layer imports land on empty type surfaces from {src_layer} to {dst_layer}",
                "top_pairs": pairs,
                "samples": bucket[:limit],
            }
        )

    top_group = groups[0]
    return {
        "status": "present",
        "finding_name": "cross-layer imports with empty type surfaces",
        "summary": top_group["summary"],
        "groups": groups,
        "samples": top_group.get("top_pairs") or [],
        "sample_findings": rows[:limit],
        "top_sources": top_group.get("top_pairs") or [],
    }


def build_gate_breakout(gate: dict[str, Any], sqlite_path: Path, limit: int = 10) -> dict[str, Any]:
    gate_id = str(gate.get("gate_id") or "").strip()
    if gate_id.startswith("B2_"):
        return build_layer_skip_breakout(sqlite_path, gate_id, limit=limit)
    if gate_id.startswith("C2_"):
        return build_l5_bypass_breakout(sqlite_path, gate_id, limit=limit)
    if gate_id.startswith("F1_"):
        return build_untyped_seam_breakout(sqlite_path, gate_id, limit=limit)
    return {
        "status": "missing",
        "finding_name": gate_id or "gate findings",
        "summary": "breakout unavailable",
        "groups": [],
        "samples": [],
        "note": f"{gate_id or 'gate'} breakout unavailable because no dedicated breaker is defined.",
    }


def format_evidence_line(gate: dict[str, Any], run_id: str, breakout: dict[str, Any] | None) -> str:
    gate_id = str(gate.get("gate_id") or "").strip()
    finding_name = str((breakout or {}).get("finding_name") or "findings").strip()
    count, base_text, delta, delta_text = _format_count_and_delta(gate)
    summary = str((breakout or {}).get("summary") or "").strip().rstrip(".")
    top_sources = list((breakout or {}).get("top_sources") or [])

    if base_text:
        lead = f"ADG `{run_id}`: `{gate_id}` found {_fmt_int(count)} {finding_name}, {delta_text}."
    else:
        lead = f"ADG `{run_id}`: `{gate_id}` found {_fmt_int(count)} {finding_name}."

    if summary and summary != "breakout unavailable":
        lead += f" {summary}."
    elif count == 0:
        lead += " No rows were promoted."
    else:
        lead += " Breakout unavailable."

    sample_text = ""
    if top_sources:
        if "src" in top_sources[0]:
            sample_text = _format_pair_samples(top_sources, joiner=" to ")
        elif "path" in top_sources[0]:
            parts: list[str] = []
            for item in top_sources[:3]:
                path = item["path"]
                count_text = _fmt_int(item.get("count"))
                if item.get("line_no"):
                    parts.append(f"{count_text} rows from {path}:{item['line_no']}")
                else:
                    parts.append(f"{count_text} rows from {path}")
            if len(parts) == 1:
                sample_text = parts[0]
            elif len(parts) == 2:
                sample_text = f"{parts[0]} and {parts[1]}"
            else:
                sample_text = f"{parts[0]}, {parts[1]}, and {parts[2]}"

    if sample_text:
        lead += f" Examples: {sample_text}."
    return lead
