"""
Phase 7: Final Ranked Report — ADG GraphDB Technical Debt / SSOT / Hardcoding / Architectural Audit.

Consolidates findings from Phases 3-6 into a single ranked report with:
- Deduplicated findings across phases
- Composite severity scoring (layer multiplier × fan-in × surface intersection)
- Exact ADG queries used for each finding
- Actionable remediation wave ordering

Read-only. No code modifications.
"""
import json
import sqlite3
from pathlib import Path
from collections import defaultdict

DB = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite")
OUT = Path(r"C:\Git\Agentic-Workflow\artifacts\audit_phase7_final_report.json")

# Layer criticality multipliers (from adg-canonical-invariants.md §6)
LAYER_MULTIPLIER = {
    "L0": 2.0, "L5": 2.0,
    "L3": 1.75, "L4": 1.75,
    "L1": 1.0, "L2": 1.0,
    "L6": 0.75,
    "L_SHARED": 1.0, "L_RUNTIME": 1.0, "L_TOOLS": 1.0,
    "L_APP": 1.0, "L_OPS": 1.0, "L_SL": 1.0,
    "L_INFRA": 1.0, "L_PG": 1.0, "L_TEST": 0.5,
    "L_UNKNOWN": 0.5,
}

# Surface boost (from adg-canonical-invariants.md §3)
SURFACE_BOOST = {
    "Security": 1.5, "Write": 1.4, "Execution": 1.3,
    "State": 1.2, "Observability": 1.1, "None": 1.0,
}

# Load all phase artifacts
PHASES = {}
for phase_id, path in [
    ("P3", r"artifacts/audit_phase3_fanin.json"),
    ("P4", r"artifacts/audit_phase4_fanout.json"),
    ("P5", r"artifacts/audit_phase5_ssot.json"),
    ("P6", r"artifacts/audit_phase6_legacy.json"),
]:
    try:
        PHASES[phase_id] = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        PHASES[phase_id] = {"queries": {}, "summary": {}}


def compute_impact(fan_in: int, fan_out: int, layer: str,
                   surface: str = "None", violation_count: int = 1) -> float:
    """Compute composite impact score using ADG canonical formula.
    Uses fan_in as primary (consumers = blast radius) and fan_out as secondary."""
    lm = LAYER_MULTIPLIER.get(layer, 1.0)
    sb = SURFACE_BOOST.get(surface, 1.0)
    # Primary: fan_in drives blast radius; fan_out adds dispatch surface
    connectivity = fan_in + fan_out * 0.5
    return violation_count * lm * (1 + max(0, __import__("math").log10(1 + connectivity))) * sb


def extract_all_findings() -> list[dict]:
    """Extract and normalize all findings from Phases 3-6."""
    findings = []

    for phase_id, data in PHASES.items():
        for qname, rows in data.get("queries", {}).items():
            for r in rows:
                f = {
                    "phase": phase_id,
                    "query": qname,
                    "severity_raw": r.get("_severity", "P3"),
                    "layer": r.get("layer", ""),
                    "resolved_path": r.get("resolved_path", r.get("caller_file", r.get("importer_file", r.get("files", "")))),
                    "adg_name": r.get("adg_name", r.get("short_name", "")),
                    "fan_in": r.get("fan_in") or r.get("total_fan_in") or r.get("module_fan_in") or r.get("target_fan_in") or 0,
                    "fan_out": r.get("fan_out") or r.get("total_fan_out") or r.get("module_fan_out") or r.get("egress_edge_count") or r.get("write_target_count") or 0,
                    "betweenness": r.get("betweenness_approx", 0) or 0,
                    "category": r.get("_audit_category", qname),
                }
                # Convert to int
                try:
                    f["fan_in"] = int(f["fan_in"])
                except (ValueError, TypeError):
                    f["fan_in"] = 0
                try:
                    f["fan_out"] = int(f["fan_out"])
                except (ValueError, TypeError):
                    f["fan_out"] = 0
                try:
                    f["betweenness"] = float(f["betweenness"])
                except (ValueError, TypeError):
                    f["betweenness"] = 0.0

                findings.append(f)

    return findings


def deduplicate_by_path(findings: list[dict]) -> list[dict]:
    """Merge findings for the same resolved_path across phases.
    Keep the highest severity, sum phase evidence."""
    by_path: dict[str, dict] = {}

    for f in findings:
        rp = f.get("resolved_path", "")
        if not rp or rp in ("", "None", "unknown"):
            continue

        key = rp
        if key not in by_path:
            by_path[key] = {
                "resolved_path": rp,
                "layer": f["layer"],
                "adg_name": f["adg_name"],
                "fan_in": f["fan_in"],
                "fan_out": f["fan_out"],
                "betweenness": f["betweenness"],
                "phases": [],
                "queries": [],
                "severity_raw": "P3",
                "surfaces": set(),
                "findings_detail": [],
            }

        entry = by_path[key]
        # Keep max values
        entry["fan_in"] = max(entry["fan_in"], f["fan_in"])
        entry["fan_out"] = max(entry["fan_out"], f["fan_out"])
        entry["betweenness"] = max(entry["betweenness"], f["betweenness"])

        # Track which phases/queries found this
        if f["phase"] not in entry["phases"]:
            entry["phases"].append(f["phase"])
        if f["query"] not in entry["queries"]:
            entry["queries"].append(f["query"])

        # Keep highest severity
        sev_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        if sev_order.get(f["severity_raw"], 3) < sev_order.get(entry["severity_raw"], 3):
            entry["severity_raw"] = f["severity_raw"]

        # Classify surfaces
        q = f["query"]
        if "write" in q or "writes_to" in str(f.get("findings_detail", "")):
            entry["surfaces"].add("Write")
        if "observ" in q or "trace" in q:
            entry["surfaces"].add("Observability")
        if "forbidden" in q or "boundary" in q or "authority" in q:
            entry["surfaces"].add("Security")
        if "state" in q or "config" in q or "registry" in q:
            entry["surfaces"].add("State")
        if "egress" in q or "provider" in q or "dispatch" in q:
            entry["surfaces"].add("Execution")

        entry["findings_detail"].append({
            "phase": f["phase"],
            "query": f["query"],
            "severity": f["severity_raw"],
        })

    # Convert sets to strings
    for entry in by_path.values():
        if not entry["surfaces"]:
            entry["surfaces"] = "None"
        else:
            entry["surfaces"] = "+".join(sorted(entry["surfaces"]))

    return list(by_path.values())


def rank_findings(merged: list[dict]) -> list[dict]:
    """Compute composite impact score and rank."""
    for entry in merged:
        surface = entry["surfaces"] if isinstance(entry["surfaces"], str) else "None"
        # Use the primary surface for boost
        primary_surface = surface.split("+")[0] if "+" in surface else surface
        entry["impact_score"] = compute_impact(
            fan_in=entry["fan_in"],
            fan_out=entry["fan_out"],
            layer=entry["layer"],
            surface=primary_surface,
            violation_count=len(entry["findings_detail"]),
        )
        # Cross-phase multiplier: found in more phases = higher confidence
        entry["cross_phase_count"] = len(entry["phases"])
        entry["impact_score"] *= (1 + 0.2 * (entry["cross_phase_count"] - 1))

        # Final severity based on impact score
        if entry["impact_score"] >= 30:
            entry["severity_final"] = "P0"
        elif entry["impact_score"] >= 15:
            entry["severity_final"] = "P1"
        elif entry["impact_score"] >= 5:
            entry["severity_final"] = "P2"
        else:
            entry["severity_final"] = "P3"

    merged.sort(key=lambda x: -x["impact_score"])
    return merged


def generate_wave_plan(ranked: list[dict]) -> list[dict]:
    """Generate remediation wave plan from ranked findings.
    P0 → Wave 1 (immediate), P1 → Wave 2, P2 → Wave 3, P3 → Wave 4."""
    waves = [
        {"wave": "W1", "label": "Critical Structural Bottlenecks", "severity_filter": "P0", "items": []},
        {"wave": "W2", "label": "Authority & Observability Gaps", "severity_filter": "P1", "items": []},
        {"wave": "W3", "label": "SSOT Consolidation & Dead Code", "severity_filter": "P2", "items": []},
        {"wave": "W4", "label": "Hygiene & Naming Cleanup", "severity_filter": "P3", "items": []},
    ]

    for entry in ranked:
        for w in waves:
            if entry["severity_final"] == w["severity_filter"]:
                w["items"].append({
                    "resolved_path": entry["resolved_path"],
                    "layer": entry["layer"],
                    "impact_score": round(entry["impact_score"], 2),
                    "fan_in": entry["fan_in"],
                    "fan_out": entry["fan_out"],
                    "surfaces": entry["surfaces"],
                    "phases": entry["phases"],
                })
                break

    # Summary per wave
    for w in waves:
        w["item_count"] = len(w["items"])
        w["total_impact"] = round(sum(i["impact_score"] for i in w["items"]), 2)

    return waves


def main() -> None:
    print("Extracting findings from Phases 3-6 ...", flush=True)
    all_findings = extract_all_findings()
    print(f"  Total raw findings: {len(all_findings)}")

    print("Deduplicating by resolved_path ...", flush=True)
    merged = deduplicate_by_path(all_findings)
    print(f"  Unique paths: {len(merged)}")

    print("Ranking by composite impact ...", flush=True)
    ranked = rank_findings(merged)

    print("Generating wave plan ...", flush=True)
    waves = generate_wave_plan(ranked)

    # Severity distribution
    sev_dist = defaultdict(int)
    for entry in ranked:
        sev_dist[entry["severity_final"]] += 1

    # Layer distribution
    layer_dist = defaultdict(int)
    for entry in ranked:
        layer_dist[entry["layer"]] += 1

    # Surface distribution
    surface_dist = defaultdict(int)
    for entry in ranked:
        for s in entry["surfaces"].split("+"):
            surface_dist[s] += 1

    # Top 50 ranked findings
    top50 = ranked[:50]

    # Queries used (from each phase)
    queries_used = {}
    for phase_id, data in PHASES.items():
        queries_used[phase_id] = {
            "query_names": list(data.get("queries", {}).keys()),
            "summary": data.get("summary", {}),
        }

    report = {
        "phase": "7_final_ranked_report",
        "adg_snapshot": "04252026_0521",
        "methodology": {
            "impact_formula": "impact = violation_count × layer_multiplier × (1 + log10(1 + max(fan_in, fan_out))) × surface_boost × cross_phase_multiplier",
            "layer_multipliers": LAYER_MULTIPLIER,
            "surface_boosts": SURFACE_BOOST,
            "cross_phase_multiplier": "1 + 0.2 × (phase_count - 1)",
            "severity_bands": {"P0": "impact ≥ 30", "P1": "impact ≥ 15", "P2": "impact ≥ 5", "P3": "impact < 5"},
        },
        "overall_stats": {
            "total_raw_findings": len(all_findings),
            "unique_paths": len(merged),
            "severity_distribution": dict(sev_dist),
            "layer_distribution": dict(layer_dist),
            "surface_distribution": dict(surface_dist),
        },
        "top_50_ranked": [
            {
                "rank": i + 1,
                "resolved_path": e["resolved_path"],
                "layer": e["layer"],
                "adg_name": e["adg_name"],
                "fan_in": e["fan_in"],
                "fan_out": e["fan_out"],
                "betweenness": round(e["betweenness"], 4),
                "impact_score": round(e["impact_score"], 2),
                "severity_final": e["severity_final"],
                "severity_raw": e["severity_raw"],
                "surfaces": e["surfaces"],
                "phases": e["phases"],
                "queries": e["queries"],
                "findings_count": len(e["findings_detail"]),
            }
            for i, e in enumerate(top50)
        ],
        "wave_plan": waves,
        "queries_used": queries_used,
    }

    OUT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"\nSeverity distribution: {dict(sev_dist)}")
    print(f"Wave plan: W1={waves[0]['item_count']} items, W2={waves[1]['item_count']}, W3={waves[2]['item_count']}, W4={waves[3]['item_count']}")


if __name__ == "__main__":
    main()
