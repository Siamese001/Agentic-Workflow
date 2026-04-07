"""Convergence Gap Analysis — read-only analytical pass against ADG SQLite.

Produces evidence for all 7 sections of the convergence report.
Does NOT modify any repository files.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = ROOT / "artifacts" / "adg"

# Find the latest SQLite
def find_latest_sqlite():
    candidates = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        print("ERROR: No ADG SQLite found in artifacts/adg/")
        sys.exit(1)
    return candidates[0]


def get_edge_counts(db_path):
    """Get edge counts by relation_type from SQLite."""
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY relation_type")
    counts = dict(c.fetchall())
    c.execute("SELECT COUNT(*) FROM edges")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM nodes")
    node_total = c.fetchone()[0]
    conn.close()
    return counts, total, node_total


def get_all_edges(db_path):
    """Get all edges with full detail."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM edges")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_all_nodes(db_path):
    """Get all nodes with full detail."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM nodes")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def section1_delta_zero(db_path):
    """Section 1: Delta-Zero Graph Stability — 3 rebuilds."""
    print("\n" + "=" * 60)
    print("SECTION 1 — DELTA-ZERO GRAPH STABILITY")
    print("=" * 60)

    TRACKED_FAMILIES = [
        "agent_executes_agent", "applies_guardrail", "calls",
        "dispatches_healing_run", "emits_determinism_digest",
        "pulls_context", "reads_from", "reads_through",
        "records_execution_trace", "writes_to", "writes_through",
    ]

    runs = []
    run_digests = []

    for i in range(3):
        print(f"\n--- ADG Rebuild R{i+1} ---")
        t0 = time.time()
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "generate_full_adg.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=600,
        )
        elapsed = time.time() - t0
        print(f"  Completed in {elapsed:.1f}s (exit={result.returncode})")

        if result.returncode != 0:
            print(f"  STDERR (last 500 chars): {result.stderr[-500:]}")

        # Find the freshly generated sqlite
        latest = find_latest_sqlite()
        print(f"  SQLite: {latest.name}")

        counts, total, node_total = get_edge_counts(latest)
        print(f"  Total edges: {total}, nodes: {node_total}")

        # Compute a digest of the full edge set for determinism check
        conn = sqlite3.connect(str(latest))
        c = conn.cursor()
        c.execute("SELECT src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol FROM edges ORDER BY src_id, dst_id, relation_type, source_file, line_no")
        all_rows = c.fetchall()
        conn.close()
        digest = hashlib.sha256(str(all_rows).encode()).hexdigest()[:16]
        run_digests.append(digest)
        print(f"  Edge digest: {digest}")

        run_data = {"total": total, "nodes": node_total, "digest": digest}
        for fam in TRACKED_FAMILIES:
            run_data[fam] = counts.get(fam, 0)
        runs.append(run_data)

    # Print comparison table
    print("\n--- Edge Family Comparison ---")
    print(f"{'EDGE TYPE':<35} {'R1':>8} {'R2':>8} {'R3':>8} {'R2-R1':>8} {'R3-R2':>8}")
    print("-" * 75)

    unstable = []
    for fam in TRACKED_FAMILIES:
        r1 = runs[0].get(fam, 0)
        r2 = runs[1].get(fam, 0)
        r3 = runs[2].get(fam, 0)
        d12 = r2 - r1
        d23 = r3 - r2
        marker = "" if d23 == 0 else " *** UNSTABLE ***"
        print(f"{fam:<35} {r1:>8} {r2:>8} {r3:>8} {d12:>8} {d23:>8}{marker}")
        if d23 != 0:
            unstable.append({"family": fam, "delta_r2_r3": d23, "r2": r2, "r3": r3})

    print(f"\n{'TOTAL EDGES':<35} {runs[0]['total']:>8} {runs[1]['total']:>8} {runs[2]['total']:>8}")
    print(f"{'TOTAL NODES':<35} {runs[0]['nodes']:>8} {runs[1]['nodes']:>8} {runs[2]['nodes']:>8}")
    print(f"{'DIGEST':<35} {runs[0]['digest']:>8} {runs[1]['digest']:>8} {runs[2]['digest']:>8}")

    stable = len(unstable) == 0
    print(f"\nDELTA-ZERO VERDICT: {'STABLE' if stable else 'UNSTABLE'}")
    if unstable:
        print("Unstable families:")
        for u in unstable:
            print(f"  - {u['family']}: delta={u['delta_r2_r3']}")

    return {"runs": runs, "unstable": unstable, "stable": stable, "digests": run_digests}


def section2_high_risk_gaps(db_path):
    """Section 2: High-Risk Gap Detection."""
    print("\n" + "=" * 60)
    print("SECTION 2 — HIGH-RISK GAP DETECTION")
    print("=" * 60)

    edges = get_all_edges(db_path)
    nodes = get_all_nodes(db_path)

    # Build node lookup
    node_by_id = {n["id"]: n for n in nodes}
    node_by_name = {n.get("adg_name", ""): n for n in nodes}

    # Build edges by source file
    edges_by_src = defaultdict(set)
    for e in edges:
        sf = e.get("source_file", "")
        if sf:
            edges_by_src[sf].add(e["relation_type"])

    # High-risk patterns
    RISK_PATTERNS = [
        "router", "gateway", "orchestrat", "planner", "agent",
        "validator", "governor", "memory", "storage", "trace",
        "replay", "healing", "executor",
    ]

    # Required relations by risk type
    REQUIRED_RELS = {
        "routing": ["calls", "agent_executes_agent"],
        "execution": ["calls"],
        "state_mutation": ["writes_to", "writes_through"],
        "state_consumer": ["reads_from", "reads_through"],
        "trace_producer": ["records_execution_trace", "emits_determinism_digest"],
    }

    # Classify modules by risk type
    def classify_risk(filepath):
        fl = filepath.lower()
        types = []
        if any(p in fl for p in ["router", "gateway", "routing"]):
            types.append("routing")
        if any(p in fl for p in ["executor", "execution", "engine"]):
            types.append("execution")
        if any(p in fl for p in ["writer", "mutator", "uwg", "write_gateway"]):
            types.append("state_mutation")
        if any(p in fl for p in ["reader", "consumer", "retriev", "context"]):
            types.append("state_consumer")
        if any(p in fl for p in ["trace", "replay", "determinism", "observ"]):
            types.append("trace_producer")
        if any(p in fl for p in ["orchestrat", "planner", "healing", "agent"]):
            types.extend(["routing", "execution"])
        return types if types else None

    # Find high-risk modules
    all_source_files = set()
    for e in edges:
        sf = e.get("source_file", "")
        if sf:
            all_source_files.add(sf)

    high_risk_files = set()
    for sf in all_source_files:
        fl = sf.lower()
        if any(p in fl for p in RISK_PATTERNS):
            high_risk_files.add(sf)

    print(f"Total source files in ADG: {len(all_source_files)}")
    print(f"High-risk candidate files: {len(high_risk_files)}")

    # Analyze gaps
    gaps = []
    for sf in sorted(high_risk_files):
        risk_types = classify_risk(sf)
        if not risk_types:
            continue

        present_rels = edges_by_src.get(sf, set())
        for rt in risk_types:
            required = REQUIRED_RELS.get(rt, [])
            for req_rel in required:
                if req_rel not in present_rels:
                    # Determine severity
                    if rt in ("routing", "trace_producer"):
                        severity = "Critical"
                    elif rt in ("state_mutation", "execution"):
                        severity = "High"
                    else:
                        severity = "Moderate"
                    gaps.append({
                        "module": sf,
                        "risk_type": rt,
                        "missing": req_rel,
                        "severity": severity,
                    })

    # Print gap table
    print(f"\nHigh-risk gaps found: {len(gaps)}")
    print(f"\n{'MODULE':<55} {'RISK TYPE':<18} {'MISSING':<30} {'SEVERITY':<10}")
    print("-" * 115)

    severity_counts = Counter()
    # Show top 40 critical/high gaps
    sorted_gaps = sorted(gaps, key=lambda g: {"Critical": 0, "High": 1, "Moderate": 2, "Low": 3}[g["severity"]])
    for g in sorted_gaps[:40]:
        mod_short = g["module"][-52:] if len(g["module"]) > 52 else g["module"]
        print(f"{mod_short:<55} {g['risk_type']:<18} {g['missing']:<30} {g['severity']:<10}")
        severity_counts[g["severity"]] += 1

    if len(sorted_gaps) > 40:
        print(f"  ... and {len(sorted_gaps) - 40} more gaps")

    for sev in ["Critical", "High", "Moderate", "Low"]:
        total_sev = sum(1 for g in gaps if g["severity"] == sev)
        if total_sev:
            print(f"  {sev}: {total_sev}")

    return {"total_gaps": len(gaps), "gaps": sorted_gaps, "severity_counts": dict(Counter(g["severity"] for g in gaps))}


def section3_canonical_path(db_path):
    """Section 3: Canonical Path Closure."""
    print("\n" + "=" * 60)
    print("SECTION 3 — CANONICAL PATH CLOSURE")
    print("=" * 60)

    edges = get_all_edges(db_path)

    # Build relation sets
    rel_sources = defaultdict(set)  # relation -> set of source files
    rel_targets = defaultdict(set)  # relation -> set of target files/nodes
    rel_pairs = defaultdict(set)    # relation -> set of (src, dst) pairs

    for e in edges:
        rt = e["relation_type"]
        sf = e.get("source_file", "")
        # Get target info from dst_id
        rel_sources[rt].add(sf)
        rel_pairs[rt].add((e.get("src_id"), e.get("dst_id")))

    # Canonical path segments
    segments = [
        ("router → context_retrieval", "pulls_context",
         lambda: len(rel_sources.get("pulls_context", set())) > 0),
        ("context_retrieval → reasoning (calls)", "calls",
         lambda: len(rel_sources.get("calls", set())) > 0),
        ("reasoning → reads_from", "reads_from",
         lambda: len(rel_sources.get("reads_from", set())) > 0),
        ("reasoning → writes_to", "writes_to",
         lambda: len(rel_sources.get("writes_to", set())) > 0),
        ("execution → records_execution_trace", "records_execution_trace",
         lambda: len(rel_sources.get("records_execution_trace", set())) > 0),
        ("execution → emits_determinism_digest", "emits_determinism_digest",
         lambda: len(rel_sources.get("emits_determinism_digest", set())) > 0),
        ("router → agent_executes_agent", "agent_executes_agent",
         lambda: len(rel_sources.get("agent_executes_agent", set())) > 0),
        ("execution → writes_through", "writes_through",
         lambda: len(rel_sources.get("writes_through", set())) > 0),
        ("execution → reads_through", "reads_through",
         lambda: len(rel_sources.get("reads_through", set())) > 0),
        ("safety → applies_guardrail", "applies_guardrail",
         lambda: len(rel_sources.get("applies_guardrail", set())) > 0),
    ]

    print(f"\n{'PATH SEGMENT':<50} {'RELATION':<30} {'STATUS':<10} {'EDGE COUNT':>10}")
    print("-" * 105)

    missing_segments = []
    for seg_name, rel, check_fn in segments:
        count = len(rel_pairs.get(rel, set()))
        present = check_fn()
        status = "PRESENT" if present and count > 0 else "MISSING"
        print(f"{seg_name:<50} {rel:<30} {status:<10} {count:>10}")
        if status == "MISSING":
            missing_segments.append({"segment": seg_name, "relation": rel})

    # Check transitive connectivity: do sources of calls overlap with sources of reads_from?
    calls_srcs = rel_sources.get("calls", set())
    reads_srcs = rel_sources.get("reads_from", set())
    writes_srcs = rel_sources.get("writes_to", set())
    trace_srcs = rel_sources.get("records_execution_trace", set())

    overlap_calls_reads = len(calls_srcs & reads_srcs)
    overlap_calls_writes = len(calls_srcs & writes_srcs)
    overlap_calls_trace = len(calls_srcs & trace_srcs)

    print("\nTransitive connectivity (source file overlap):")
    print(f"  calls ∩ reads_from:              {overlap_calls_reads} modules")
    print(f"  calls ∩ writes_to:               {overlap_calls_writes} modules")
    print(f"  calls ∩ records_execution_trace:  {overlap_calls_trace} modules")

    closed = len(missing_segments) == 0
    print(f"\nCANONICAL PATH VERDICT: {'CLOSED' if closed else 'OPEN — ' + str(len(missing_segments)) + ' missing segments'}")

    return {"missing": missing_segments, "closed": closed}


def section4_replay_determinism(db_path):
    """Section 4: Replay Determinism Stability."""
    print("\n" + "=" * 60)
    print("SECTION 4 — REPLAY DETERMINISM STABILITY")
    print("=" * 60)

    # Since we already ran 3 rebuilds in section 1, we can use the digests
    # For additional determinism check: hash the edge set of the current DB
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    # Get deterministic edge ordering
    c.execute("""
        SELECT src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol
        FROM edges
        ORDER BY src_id, dst_id, relation_type, source_file, line_no, symbol
    """)
    all_rows = c.fetchall()

    # Hash in chunks to avoid memory issues
    h = hashlib.sha256()
    for row in all_rows:
        h.update(str(row).encode())
    current_digest = h.hexdigest()[:32]

    # Check emits_determinism_digest and emits_replay_key presence
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'emits_determinism_digest'")
    digest_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'emits_replay_key'")
    replay_count = c.fetchone()[0]

    # Check signs_execution_trace
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'signs_execution_trace'")
    signs_count = c.fetchone()[0]

    conn.close()

    print(f"Current edge digest:          {current_digest}")
    print(f"emits_determinism_digest:     {digest_count} edges")
    print(f"emits_replay_key:             {replay_count} edges")
    print(f"signs_execution_trace:        {signs_count} edges")

    # The determinism check is: the 3 rebuilds from section 1 should have
    # produced identical digests. We'll note this for the report.
    print("\nNote: Full determinism verification requires comparison of 3 rebuild digests")
    print("(performed in Section 1). Cross-reference R2/R3 digest match there.")

    has_determinism_infra = digest_count > 0 and replay_count > 0 and signs_count > 0
    print(f"\nDeterminism infrastructure present: {'YES' if has_determinism_infra else 'NO'}")

    return {
        "current_digest": current_digest,
        "emits_determinism_digest": digest_count,
        "emits_replay_key": replay_count,
        "signs_execution_trace": signs_count,
        "infra_present": has_determinism_infra,
    }


def section5_query_answerability(db_path):
    """Section 5: Query Answerability Test."""
    print("\n" + "=" * 60)
    print("SECTION 5 — QUERY ANSWERABILITY TEST")
    print("=" * 60)

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    results = []

    # Q1: What modules write to each state store?
    print("\nQ1: What modules write to each state store?")
    c.execute("""
        SELECT DISTINCT e.source_file, n.adg_name
        FROM edges e
        JOIN nodes n ON e.dst_id = n.id
        WHERE e.relation_type IN ('writes_to', 'writes_through')
        AND e.source_file IS NOT NULL AND e.source_file != ''
        ORDER BY e.source_file
    """)
    writes = c.fetchall()
    writers = defaultdict(set)
    for src, tgt in writes:
        writers[tgt].add(src)
    q1_count = len(writers)
    q1_modules = sum(len(v) for v in writers.values())
    print(f"  State stores with writers: {q1_count}")
    print(f"  Total writer→store pairs: {q1_modules}")
    q1_success = q1_count > 0
    q1_gaps = "None" if q1_success else "No writes_to/writes_through edges found"
    results.append(("Q1: modules writing to state stores", q1_success, q1_gaps))

    # Q2: What modules read from each state store?
    print("\nQ2: What modules read from each state store?")
    c.execute("""
        SELECT DISTINCT e.source_file, n.adg_name
        FROM edges e
        JOIN nodes n ON e.dst_id = n.id
        WHERE e.relation_type IN ('reads_from', 'reads_through')
        AND e.source_file IS NOT NULL AND e.source_file != ''
        ORDER BY e.source_file
    """)
    reads = c.fetchall()
    readers = defaultdict(set)
    for src, tgt in reads:
        readers[tgt].add(src)
    q2_count = len(readers)
    q2_modules = sum(len(v) for v in readers.values())
    print(f"  State stores with readers: {q2_count}")
    print(f"  Total reader→store pairs: {q2_modules}")
    q2_success = q2_count > 0
    q2_gaps = "None" if q2_success else "No reads_from/reads_through edges found"
    results.append(("Q2: modules reading from state stores", q2_success, q2_gaps))

    # Q3: Which agents orchestrate other agents?
    print("\nQ3: Which agents orchestrate other agents?")
    c.execute("""
        SELECT DISTINCT e.source_file, e.symbol
        FROM edges e
        WHERE e.relation_type IN ('agent_executes_agent', 'orchestrates_workflow', 'dispatches_agent', 'coordinates_agents')
        AND e.source_file IS NOT NULL AND e.source_file != ''
        ORDER BY e.source_file
    """)
    orchestrators = c.fetchall()
    orch_files = set(r[0] for r in orchestrators)
    print(f"  Orchestrating modules: {len(orch_files)}")
    print(f"  Total orchestration edges: {len(orchestrators)}")
    q3_success = len(orch_files) > 0
    q3_gaps = "None" if q3_success else "No agent_executes_agent/orchestrates_workflow edges"
    results.append(("Q3: agents orchestrating agents", q3_success, q3_gaps))

    # Q4: What modules produce execution traces?
    print("\nQ4: What modules produce execution traces?")
    c.execute("""
        SELECT DISTINCT source_file
        FROM edges
        WHERE relation_type IN ('records_execution_trace', 'signs_execution_trace', 'emits_determinism_digest')
        AND source_file IS NOT NULL AND source_file != ''
    """)
    trace_producers = [r[0] for r in c.fetchall()]
    print(f"  Trace-producing modules: {len(trace_producers)}")
    q4_success = len(trace_producers) > 0
    q4_gaps = "None" if q4_success else "No records_execution_trace edges"
    results.append(("Q4: modules producing execution traces", q4_success, q4_gaps))

    # Q5: What tools are invoked by each agent?
    print("\nQ5: What tools are invoked by each agent?")
    c.execute("""
        SELECT DISTINCT e.source_file, e.symbol, n.adg_name
        FROM edges e
        JOIN nodes n ON e.dst_id = n.id
        WHERE e.relation_type = 'calls'
        AND e.source_file IS NOT NULL AND e.source_file != ''
        AND (e.source_file LIKE '%agent%' OR e.source_file LIKE '%Agent%'
             OR e.source_file LIKE '%reasoning%' OR e.source_file LIKE '%orchestrat%')
        ORDER BY e.source_file
        LIMIT 500
    """)
    agent_calls = c.fetchall()
    agent_callers = set(r[0] for r in agent_calls)
    print(f"  Agent modules making calls: {len(agent_callers)}")
    print(f"  Agent→tool call edges (sample): {len(agent_calls)}")
    q5_success = len(agent_callers) > 0
    q5_gaps = "None" if q5_success else "No calls edges from agent modules"
    results.append(("Q5: tools invoked by agents", q5_success, q5_gaps))

    conn.close()

    # Summary table
    print(f"\n{'QUERY':<50} {'SUCCESS':>8} {'GAPS':<40}")
    print("-" * 100)
    for query, success, gaps in results:
        print(f"{query:<50} {'YES' if success else 'NO':>8} {gaps:<40}")

    all_success = all(r[1] for r in results)
    print(f"\nQUERY ANSWERABILITY VERDICT: {'ALL ANSWERABLE' if all_success else 'GAPS EXIST'}")

    return {"results": results, "all_answerable": all_success}


def section6_false_positives(db_path):
    """Section 6: False Positive Edge Detection."""
    print("\n" + "=" * 60)
    print("SECTION 6 — FALSE POSITIVE EDGE DETECTION")
    print("=" * 60)

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    issues = []

    # 1. Self-referential loops
    print("\nChecking self-referential loops...")
    c.execute("""
        SELECT relation_type, source_file, src_id, dst_id, COUNT(*) as cnt
        FROM edges
        WHERE src_id = dst_id
        GROUP BY relation_type, source_file
        ORDER BY cnt DESC
        LIMIT 50
    """)
    self_loops = c.fetchall()
    print(f"  Self-referential edges: {len(self_loops)} groups")
    for rel, sf, src, dst, cnt in self_loops[:10]:
        issues.append({
            "edge_type": rel,
            "source": sf or src,
            "target": dst,
            "issue": f"Self-loop ({cnt} instances)",
        })

    # 2. Edges referencing missing source files (nonexistent on disk)
    print("\nChecking edges with missing source files...")
    c.execute("""
        SELECT DISTINCT source_file
        FROM edges
        WHERE source_file IS NOT NULL AND source_file != ''
    """)
    all_source_files = [r[0] for r in c.fetchall()]
    missing_files = []
    for sf in all_source_files:
        full = ROOT / sf
        if not full.exists():
            missing_files.append(sf)

    print(f"  Source files in ADG: {len(all_source_files)}")
    print(f"  Missing from disk: {len(missing_files)}")
    for mf in missing_files[:10]:
        c.execute("SELECT relation_type, COUNT(*) FROM edges WHERE source_file = ? GROUP BY relation_type", (mf,))
        rels = c.fetchall()
        for rel, cnt in rels:
            issues.append({
                "edge_type": rel,
                "source": mf,
                "target": "(missing file)",
                "issue": f"Source file not on disk ({cnt} edges)",
            })

    # 3. Duplicate edges (exact same src, dst, relation, source_file, line)
    print("\nChecking duplicate edges...")
    c.execute("""
        SELECT src_id, dst_id, relation_type, source_file, line_no, COUNT(*) as cnt
        FROM edges
        GROUP BY src_id, dst_id, relation_type, source_file, line_no
        HAVING cnt > 1
        ORDER BY cnt DESC
        LIMIT 30
    """)
    duplicates = c.fetchall()
    total_dupes = sum(r[5] - 1 for r in duplicates)  # excess count
    print(f"  Duplicate edge groups: {len(duplicates)}")
    print(f"  Excess duplicate edges: {total_dupes}")
    for src, dst, rel, sf, line, cnt in duplicates[:5]:
        issues.append({
            "edge_type": rel,
            "source": sf or str(src),
            "target": str(dst),
            "issue": f"Exact duplicate ({cnt}x at line {line})",
        })

    # 4. Edges with NULL or empty critical fields
    print("\nChecking edges with missing critical fields...")
    c.execute("SELECT COUNT(*) FROM edges WHERE src_id IS NULL OR dst_id IS NULL")
    null_endpoints = c.fetchone()[0]
    print(f"  Edges with NULL src/dst: {null_endpoints}")
    if null_endpoints > 0:
        issues.append({
            "edge_type": "(various)",
            "source": "NULL",
            "target": "NULL",
            "issue": f"{null_endpoints} edges with NULL endpoints",
        })

    # 5. Nodes referenced by edges but not in nodes table
    print("\nChecking orphan edge references...")
    c.execute("""
        SELECT COUNT(DISTINCT e.src_id)
        FROM edges e
        LEFT JOIN nodes n ON e.src_id = n.id
        WHERE n.id IS NULL
    """)
    orphan_src = c.fetchone()[0]
    c.execute("""
        SELECT COUNT(DISTINCT e.dst_id)
        FROM edges e
        LEFT JOIN nodes n ON e.dst_id = n.id
        WHERE n.id IS NULL
    """)
    orphan_dst = c.fetchone()[0]
    print(f"  Orphan src references: {orphan_src}")
    print(f"  Orphan dst references: {orphan_dst}")
    if orphan_src > 0 or orphan_dst > 0:
        issues.append({
            "edge_type": "(various)",
            "source": f"{orphan_src} orphan srcs",
            "target": f"{orphan_dst} orphan dsts",
            "issue": "Edge references nonexistent node",
        })

    # 6. Check for _emit_* instrumentation edges that leaked through
    print("\nChecking for instrumentation edge leakage...")
    c.execute("""
        SELECT relation_type, COUNT(*)
        FROM edges
        WHERE symbol LIKE '_emit_%' OR symbol LIKE 'emit_%'
        GROUP BY relation_type
        ORDER BY COUNT(*) DESC
    """)
    instrumentation_leaks = c.fetchall()
    total_leaks = sum(r[1] for r in instrumentation_leaks)
    print(f"  Instrumentation symbol edges: {total_leaks}")
    if total_leaks > 0:
        for rel, cnt in instrumentation_leaks[:5]:
            issues.append({
                "edge_type": rel,
                "source": "(instrumentation)",
                "target": "_emit_* symbols",
                "issue": f"{cnt} edges from _emit_* calls (should be suppressed)",
            })

    conn.close()

    # Print issues table
    print(f"\n{'EDGE TYPE':<30} {'SOURCE':<35} {'TARGET':<25} {'ISSUE':<35}")
    print("-" * 130)
    for iss in issues[:30]:
        et = iss["edge_type"][:28]
        src = iss["source"][-33:] if len(iss["source"]) > 33 else iss["source"]
        tgt = iss["target"][:23]
        print(f"{et:<30} {src:<35} {tgt:<25} {iss['issue']:<35}")

    print(f"\nTotal issues found: {len(issues)}")
    has_material = any("instrumentation" in i["issue"].lower() or "missing file" in i["issue"].lower() or "NULL" in i["issue"] for i in issues)
    print(f"Material false positives: {'YES' if has_material else 'MINIMAL'}")

    return {"issues": issues, "has_material_false_positives": has_material}


def main():
    db_path = find_latest_sqlite()
    print(f"ADG SQLite: {db_path.name}")
    print(f"Repository: {ROOT}")

    # Run section 1 (3 rebuilds) first
    s1 = section1_delta_zero(db_path)

    # Re-find latest sqlite after rebuilds
    db_path = find_latest_sqlite()
    print(f"\nUsing post-rebuild SQLite: {db_path.name}")

    s2 = section2_high_risk_gaps(db_path)
    s3 = section3_canonical_path(db_path)
    s4 = section4_replay_determinism(db_path)
    s5 = section5_query_answerability(db_path)
    s6 = section6_false_positives(db_path)

    # Section 7: Final Scorecard
    print("\n" + "=" * 60)
    print("SECTION 7 — FINAL CONVERGENCE SCORECARD")
    print("=" * 60)

    criteria = [
        ("Delta-zero graph stability", s1["stable"]),
        ("High-risk gap closure", s2["total_gaps"] == 0),
        ("Canonical path closure", s3["closed"]),
        ("Replay determinism stability", s4["infra_present"] and (len(s1["digests"]) >= 2 and s1["digests"][-1] == s1["digests"][-2])),
        ("Query answerability success", s5["all_answerable"]),
        ("False-positive edge absence", not s6["has_material_false_positives"]),
    ]

    print(f"\n{'CRITERION':<40} {'STATUS':<15} {'NOTES'}")
    print("-" * 90)
    all_pass = True
    scorecard_rows = []
    for name, passed in criteria:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        notes = ""
        if name == "Delta-zero graph stability":
            notes = f"{'0' if s1['stable'] else len(s1['unstable'])} unstable families"
        elif name == "High-risk gap closure":
            notes = f"{s2['total_gaps']} gaps ({s2['severity_counts']})"
        elif name == "Canonical path closure":
            notes = f"{len(s3['missing'])} missing segments"
        elif name == "Replay determinism stability":
            notes = f"digest={s4['current_digest'][:12]}... det_edges={s4['emits_determinism_digest']}"
        elif name == "Query answerability success":
            failed_qs = sum(1 for r in s5["results"] if not r[1])
            notes = f"{failed_qs}/5 queries failed"
        elif name == "False-positive edge absence":
            notes = f"{len(s6['issues'])} issues found"
        print(f"{name:<40} {status:<15} {notes}")
        scorecard_rows.append((name, status, notes))

    verdict = "CONVERGED" if all_pass else "NOT CONVERGED"
    print(f"\n{'=' * 40}")
    print(f"FINAL RESULT: {verdict}")
    print(f"{'=' * 40}")

    # Save raw data for report generation
    output = {
        "s1": s1, "s2": s2, "s3": s3, "s4": s4, "s5": s5, "s6": s6,
        "scorecard": scorecard_rows, "verdict": verdict,
        "db_path": str(db_path.name),
    }

    out_json = ROOT / "artifacts" / "adg" / "_convergence_analysis_raw.json"
    # Sanitize for JSON
    def sanitize(obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Path):
            return str(obj)
        raise TypeError(f"Not serializable: {type(obj)}")

    with open(out_json, "w") as f:
        json.dump(output, f, indent=2, default=sanitize)
    print(f"\nRaw data saved: {out_json.name}")


if __name__ == "__main__":
    main()
