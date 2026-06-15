"""Generate the old L5 agent retirement manifest.

This is a read-only scanner over the L5 safety agent cohort plus the latest
existing ADG SQLite snapshot available to this Codex session. It does not
regenerate ADG.
"""

from __future__ import annotations

import json
import re
import sqlite3
import argparse
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PLAN_ID = "old-l5-agent-retirement-a94f6c"
CURRENT_DATE = "2026-06-15"
DEFAULT_ADG_SNAPSHOT = Path("artifacts/adg/adg_indexed_06152026_1043.sqlite")
OUTPUT_PATH = Path(
    "docs/reports/agent_deprecation/old_l5_agent_retirement_manifest_20260615.json"
)
ROOTS = [
    Path("agentic_core/L5_safety/reasoning"),
    Path("agentic_core/L5_safety/validators"),
]
SCAN_BASES = [
    Path("agentic_core"),
    Path("apps_rg"),
    Path("apps_lic"),
    Path("ops_scripts"),
    Path("scripts"),
    Path("tools"),
    Path("tests"),
]
SCANNED_EXTENSIONS = {".py", ".json", ".yaml", ".yml", ".toml", ".txt", ".md"}
IGNORED_PREFIXES = (
    "artifacts/",
    "archives/",
    "docs/archive/",
    "htmlcov/",
    "tools/debug/",
    "tools/archive/",
)
LARGE_FACADE_NAMES = {
    "FileClassificationAgent",
    "ArchitectureGovernorAgent",
    "GovernanceAgent",
    "CodeHealerAgent",
    "PascalSovereigntyAgent",
    "GravityLeakRepairAgent",
    "AutonomyGuardianAgent",
}


def _rel(path: Path) -> str:
    return path.as_posix()


def _nonblank_loc(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def _first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def _deletion_bucket(item: dict[str, Any]) -> str:
    if (
        item["authorized"]
        and item["archive_eligible"]
        and item["archive_eligible"] > CURRENT_DATE
    ):
        return "COOLING_WINDOW_AUTHORIZED"
    if item["path"].startswith("agentic_core/L5_safety/validators/"):
        return "VALIDATOR_DUPLICATE_OR_SHIM"
    if item["loc"] <= 125:
        return "TINY_NOOP_OR_DELEGATING_SHIM"
    if item["name"] in LARGE_FACADE_NAMES:
        return "LARGE_FACADE_RETIREMENT"
    return "UNCLASSIFIED_OLD_L5_AGENT"


def _load_adg_metrics(adg_snapshot: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    adg_nodes_by_path: dict[str, Any] = {}
    adg_coverage_by_path: dict[str, Any] = {}
    adg_hotspot_by_path: dict[str, Any] = {}

    if not adg_snapshot.exists():
        return adg_nodes_by_path, adg_coverage_by_path, adg_hotspot_by_path

    con = sqlite3.connect(str(adg_snapshot))
    con.row_factory = sqlite3.Row
    try:
        raw_nodes_by_path: dict[str, list[dict[str, Any]]] = {}
        for row in con.execute(
            "select id, resolved_path, adg_name, entity_type, layer from nodes"
        ):
            path = row["resolved_path"].replace("\\", "/")
            raw_nodes_by_path.setdefault(path, []).append(dict(row))

        edge_fan_in_by_node: dict[int, int] = {}
        edge_fan_out_by_node: dict[int, int] = {}
        for row in con.execute("select dst_id, count(*) as count from edges group by dst_id"):
            edge_fan_in_by_node[row["dst_id"]] = row["count"]
        for row in con.execute("select src_id, count(*) as count from edges group by src_id"):
            edge_fan_out_by_node[row["src_id"]] = row["count"]

        for path, nodes in raw_nodes_by_path.items():
            ids = [node["id"] for node in nodes]
            if not ids:
                continue
            adg_nodes_by_path[path] = {
                "node_count": len(nodes),
                "fan_in": sum(edge_fan_in_by_node.get(node_id, 0) for node_id in ids),
                "fan_out": sum(edge_fan_out_by_node.get(node_id, 0) for node_id in ids),
                "layers": sorted({node["layer"] for node in nodes}),
            }

        for row in con.execute(
            "select resolved_path, lines_hit, lines_total, coverage_pct, mode "
            "from coverage_by_path"
        ):
            adg_coverage_by_path[row["resolved_path"].replace("\\", "/")] = dict(row)

        for row in con.execute(
            "select file, fan_in, fan_out, violation_count, cross_layer_edges, "
            "criticality_score, combined_risk_score, priority_band, coverage_band "
            "from mv_hotspot_coverage_risk"
        ):
            adg_hotspot_by_path[row["file"].replace("\\", "/")] = dict(row)
    finally:
        con.close()

    return adg_nodes_by_path, adg_coverage_by_path, adg_hotspot_by_path


def _candidate_files() -> list[Path]:
    return sorted(path for root in ROOTS for path in root.glob("*Agent.py"))


def _build_candidates(adg_snapshot: Path) -> list[dict[str, Any]]:
    adg_nodes_by_path, adg_coverage_by_path, adg_hotspot_by_path = _load_adg_metrics(
        adg_snapshot
    )

    candidates: list[dict[str, Any]] = []
    for path in _candidate_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        rel_path = _rel(path)
        module = path.with_suffix("").as_posix().replace("/", ".")
        item: dict[str, Any] = {
            "path": rel_path,
            "module": module,
            "name": path.stem,
            "loc": _nonblank_loc(text),
            "authorized": "AGENT-DELETION-AUTHORIZED" in text,
            "authorization_date": _first_match(
                r"Authorization date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text
            ),
            "archive_eligible": _first_match(
                r"Archive-eligible date:\s*(?:on or after\s*)?([0-9]{4}-[0-9]{2}-[0-9]{2})",
                text,
            ),
            "category": _first_match(r"Category:\s*([^\n]+)", text),
            "canonical_replacement": _first_match(
                r"Canonical replacement:\s*([^\n]+)", text
            ),
            "adg": adg_nodes_by_path.get(
                rel_path, {"node_count": 0, "fan_in": 0, "fan_out": 0, "layers": []}
            ),
            "coverage": adg_coverage_by_path.get(rel_path),
            "hotspot": adg_hotspot_by_path.get(rel_path),
        }
        item["bucket"] = _deletion_bucket(item)
        candidates.append(item)

    _attach_reference_scan(candidates)
    return candidates


def _attach_reference_scan(candidates: list[dict[str, Any]]) -> None:
    for item in candidates:
        refs: list[str] = []
        module_parent, class_name = item["module"].rsplit(".", 1)
        parent_pkg = module_parent.rsplit(".", 1)[0]
        probes = [
            item["module"],
            item["path"],
            f"from {module_parent} import {class_name}",
            f"from {parent_pkg} import {class_name}",
            f"import {item['module']}",
        ]

        for base in SCAN_BASES:
            if not base.exists():
                continue
            for file_path in base.rglob("*"):
                if (
                    not file_path.is_file()
                    or file_path.suffix not in SCANNED_EXTENSIONS
                ):
                    continue
                scanned_path = _rel(file_path)
                if scanned_path == item["path"] or any(
                    scanned_path.startswith(prefix) for prefix in IGNORED_PREFIXES
                ):
                    continue
                try:
                    text = file_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if any(probe in text for probe in probes):
                    refs.append(scanned_path)

        item["raw_live_reference_count"] = len(refs)
        item["raw_live_reference_sample"] = refs[:12]


def _summary(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    bucket_counts: dict[str, int] = {}
    for item in candidates:
        bucket_counts[item["bucket"]] = bucket_counts.get(item["bucket"], 0) + 1

    return {
        "candidate_count": len(candidates),
        "total_nonblank_loc": sum(item["loc"] for item in candidates),
        "authorized_count": sum(1 for item in candidates if item["authorized"]),
        "cooling_window_authorized_count": sum(
            1 for item in candidates if item["bucket"] == "COOLING_WINDOW_AUTHORIZED"
        ),
        "eligible_for_physical_archive_as_of_2026_06_15": sum(
            1
            for item in candidates
            if item["archive_eligible"] and item["archive_eligible"] <= CURRENT_DATE
        ),
        "adg_snapshot_candidates_with_zero_import_fan_in": sum(
            1 for item in candidates if item["adg"].get("fan_in", 0) == 0
        ),
        "bucket_counts": bucket_counts,
    }


def build_manifest(adg_snapshot: Path = DEFAULT_ADG_SNAPSHOT) -> dict[str, Any]:
    candidates = _build_candidates(adg_snapshot)
    return {
        "manifest_version": "1.0",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "plan_id": PLAN_ID,
        "source": {
            "repo": str(Path.cwd()),
            "current_date": CURRENT_DATE,
            "adg_snapshot": str(adg_snapshot),
            "adg_backend": "sqlite_direct_fallback",
            "adg_fallback_reason": (
                "adg_sqlite MCP unavailable in Codex session; existing SQLite "
                "snapshot read only"
            ),
            "scope": [f"{root.as_posix()}/*Agent.py" for root in ROOTS],
        },
        "summary": _summary(candidates),
        "waves": {
            "W0": "Manifest and authorization control plane; no agent deletion.",
            "W1": (
                "Migrate runtime/test references off already-authorized shims with "
                "canonical replacements; no physical archive before 2026-07-23."
            ),
            "W2": "Classify and authorize remaining old L5 cohort.",
            "W3": "Retire large facades after replacement surfaces are proven.",
            "W4": "Physical archive/delete after eligibility and zero-live-consumer proof.",
            "W5": "Verification and ADG closeout.",
        },
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--adg-snapshot",
        type=Path,
        default=DEFAULT_ADG_SNAPSHOT,
        help="Existing ADG SQLite snapshot to read; this script does not regenerate ADG.",
    )
    args = parser.parse_args()

    manifest = build_manifest(args.adg_snapshot)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(OUTPUT_PATH)
    print(json.dumps(manifest["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
