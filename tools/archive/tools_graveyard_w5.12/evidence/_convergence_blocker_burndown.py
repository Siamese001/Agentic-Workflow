"""Convergence Blocker Burn-Down — Refined gap detector + hard target list.

Excludes __init__.py, config-only, data, and test files from risk classification.
Produces the definitive list of modules that are genuine convergence blockers.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = ROOT / "artifacts" / "adg"


def find_latest_sqlite():
    candidates = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.name, reverse=True)
    if not candidates:
        print("ERROR: No ADG SQLite found")
        sys.exit(1)
    return candidates[0]


# --- Exclusion predicates ---

def is_init_file(path: str) -> bool:
    return path.endswith("__init__.py")


def is_config_only(path: str) -> bool:
    pl = path.lower()
    return any(x in pl for x in [
        "/config/", "\\config\\", "_config.py", "_constants.py",
        "constants.py", "_settings.py", "settings.py",
        "/data/", "\\data\\",
    ])


def is_test_file(path: str) -> bool:
    return path.startswith("tests/") or path.startswith("tests\\") or "/tests/" in path


def is_data_or_artifact(path: str) -> bool:
    pl = path.lower()
    return any(x in pl for x in [
        "artifacts/", "data/golden", "/golden/",
        ".json", ".yaml", ".yml", ".csv", ".txt",
    ])


def should_exclude(path: str) -> bool:
    return is_init_file(path) or is_config_only(path) or is_test_file(path) or is_data_or_artifact(path)


def classify_genuine_risk(filepath: str):
    """Refined risk classifier — only assigns risk types to modules with genuine responsibility."""
    fl = filepath.lower()

    # Skip non-Python
    if not fl.endswith(".py"):
        return None

    types = []

    # Routing: only actual router/gateway/dispatch modules
    if any(x in fl for x in ["router.py", "gateway.py", "dispatch", "routing_engine", "agentic_router"]):
        types.append("routing")

    # Execution: only actual engine/executor modules
    if any(x in fl for x in ["executor.py", "engine.py", "_engine.py", "execution_"]):
        types.append("execution")

    # State mutation: only modules with "write" or "mutate" in name
    if any(x in fl for x in ["write_gateway", "uwg", "mutator", "state_writer"]):
        types.append("state_mutation")

    # Trace production: modules explicitly dealing with traces/replay/determinism
    if any(x in fl for x in ["trace", "replay", "determinism", "observability", "telemetry"]):
        types.append("trace_producer")

    # Orchestration: explicit orchestrator modules
    if any(x in fl for x in ["orchestrator", "orchestrat", "healing_", "planner"]):
        types.extend(["routing", "execution"])

    # Deduplicate
    return list(set(types)) if types else None


# Required relations by risk type
REQUIRED_RELS = {
    "routing": ["calls"],
    "execution": ["calls"],
    "state_mutation": ["writes_to", "writes_through"],
    "state_consumer": ["reads_from", "reads_through"],
    "trace_producer": ["records_execution_trace", "emits_determinism_digest"],
}

# Severity by risk type
SEVERITY_MAP = {
    "trace_producer": "Critical",
    "routing": "High",
    "execution": "High",
    "state_mutation": "Moderate",
    "state_consumer": "Low",
}


def main():
    db_path = find_latest_sqlite()
    print(f"ADG SQLite: {db_path.name}")

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    # Build edges by source file
    c.execute("SELECT source_file, relation_type FROM edges WHERE source_file IS NOT NULL AND source_file != ''")
    edges_by_src = defaultdict(set)
    for sf, rt in c.fetchall():
        edges_by_src[sf].add(rt)

    # Get all unique source files
    all_source_files = set(edges_by_src.keys())
    print(f"Total source files in ADG: {len(all_source_files)}")

    # Phase 1: Apply exclusions
    excluded = {sf for sf in all_source_files if should_exclude(sf)}
    candidates = all_source_files - excluded
    print(f"Excluded (init/config/test/data): {len(excluded)}")
    print(f"Remaining candidates: {len(candidates)}")

    # Phase 2: Classify with refined risk model
    gaps = []
    for sf in sorted(candidates):
        risk_types = classify_genuine_risk(sf)
        if not risk_types:
            continue

        present_rels = edges_by_src.get(sf, set())
        for rt in risk_types:
            required = REQUIRED_RELS.get(rt, [])
            for req_rel in required:
                if req_rel not in present_rels:
                    severity = SEVERITY_MAP.get(rt, "Low")
                    gaps.append({
                        "module": sf,
                        "risk_type": rt,
                        "missing": req_rel,
                        "severity": severity,
                    })

    # Phase 3: Analyze results
    print(f"\n{'='*60}")
    print("REFINED GAP ANALYSIS")
    print(f"{'='*60}")
    print(f"Total refined gaps: {len(gaps)}")

    by_severity = Counter(g["severity"] for g in gaps)
    print(f"By severity: {dict(by_severity)}")

    by_missing = Counter(g["missing"] for g in gaps)
    print("By missing relation:")
    for k, v in by_missing.most_common():
        print(f"  {k}: {v}")

    by_risk = Counter(g["risk_type"] for g in gaps)
    print("By risk type:")
    for k, v in by_risk.most_common():
        print(f"  {k}: {v}")

    # Phase 4: Build hard target list for trace/determinism blockers
    print(f"\n{'='*60}")
    print("HARD TARGET LIST — TRACE/DETERMINISM BLOCKERS")
    print(f"{'='*60}")

    trace_gaps = [g for g in gaps if g["risk_type"] == "trace_producer"]
    trace_modules = sorted(set(g["module"] for g in trace_gaps))

    print(f"Trace/determinism blocker modules: {len(trace_modules)}")
    print(f"\n{'MODULE':<70} {'MISSING'}")
    print("-" * 110)

    target_list = []
    for mod in trace_modules:
        missing = sorted(set(g["missing"] for g in trace_gaps if g["module"] == mod))
        print(f"{mod:<70} {', '.join(missing)}")
        target_list.append({"module": mod, "missing": missing})

    # Phase 5: Build full gap table for other risk types
    print(f"\n{'='*60}")
    print("ROUTING/EXECUTION GAPS (non-trace)")
    print(f"{'='*60}")

    non_trace = [g for g in gaps if g["risk_type"] != "trace_producer"]
    non_trace_modules = sorted(set(g["module"] for g in non_trace))
    print(f"Non-trace gap modules: {len(non_trace_modules)}")

    print(f"\n{'MODULE':<70} {'RISK TYPE':<15} {'MISSING'}")
    print("-" * 120)
    for mod in non_trace_modules[:30]:
        mod_gaps = [g for g in non_trace if g["module"] == mod]
        for g in mod_gaps:
            print(f"{mod:<70} {g['risk_type']:<15} {g['missing']}")
    if len(non_trace_modules) > 30:
        print(f"  ... and {len(non_trace_modules) - 30} more modules")

    conn.close()

    # Phase 6: Verify against existing ADG edge counts
    print(f"\n{'='*60}")
    print("ADG EDGE COUNTS FOR BLOCKER RELATIONS")
    print(f"{'='*60}")

    conn2 = sqlite3.connect(str(db_path))
    c2 = conn2.cursor()
    for rel in ["records_execution_trace", "emits_determinism_digest", "calls",
                 "writes_to", "writes_through", "reads_from", "reads_through",
                 "agent_executes_agent"]:
        c2.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (rel,))
        count = c2.fetchone()[0]
        c2.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type = ? AND source_file IS NOT NULL", (rel,))
        modules = c2.fetchone()[0]
        print(f"  {rel:<35} {count:>8} edges in {modules:>6} modules")
    conn2.close()

    # Phase 7: Save output
    output = {
        "refined_gap_count": len(gaps),
        "severity_counts": dict(by_severity),
        "missing_counts": dict(by_missing),
        "risk_type_counts": dict(by_risk),
        "trace_blocker_count": len(trace_modules),
        "trace_blockers": target_list,
        "non_trace_gap_count": len(non_trace_modules),
        "excluded_count": len(excluded),
        "candidate_count": len(candidates),
    }

    out_path = ROOT / "artifacts" / "adg" / "_convergence_blocker_targets.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nTarget list saved: {out_path.name}")

    # Summary verdict
    print(f"\n{'='*60}")
    print("BURN-DOWN SUMMARY")
    print(f"{'='*60}")
    print("Original raw gaps:           10,916")
    print(f"After exclusion refinement:  {len(gaps)}")
    print(f"Reduction:                   {(1 - len(gaps)/10916)*100:.1f}%")
    print("")
    print(f"TRACE/DETERMINISM BLOCKERS:  {len(trace_modules)} modules (Critical)")
    print(f"ROUTING/EXECUTION GAPS:      {len(non_trace_modules)} modules (High/Moderate)")
    print(f"TOTAL GENUINE BLOCKERS:      {len(trace_modules) + len(non_trace_modules)} modules")


if __name__ == "__main__":
    main()
