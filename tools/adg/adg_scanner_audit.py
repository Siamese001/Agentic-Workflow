"""ADG Scanner Integrity Audit — read-only, no modifications."""
import ast
import hashlib
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATTERN = "artifacts/adg/adg_indexed_03242026_1352.sqlite"
DB_PATH = ROOT / DB_PATTERN

def get_conn():
    if not DB_PATH.exists():
        # find latest
        arts = ROOT / "artifacts" / "adg"
        dbs = sorted(arts.glob("adg_indexed_*.sqlite"))
        if not dbs:
            print("ERROR: No ADG SQLite found"); sys.exit(1)
        return sqlite3.connect(str(dbs[-1]))
    return sqlite3.connect(str(DB_PATH))

# ─── §1: SYNTHETIC EDGE DETECTION ───────────────────────────────────────────

def audit_synthetic_edges(conn):
    """Identify edges from _P1608HardeningVisitor (all have line_no=1, synthetic symbols)."""
    cur = conn.cursor()

    # P1608 edge types (emitted in __init__, no AST visit)
    p1608_types = [
        'mutation_signature', 'parent_snapshot_hash', 'policy_verification',
        'dispatches_execution_plan',  # NOTE: also emitted by P1 visitor legitimately
        'defines_test_case', 'defines_test_suite', 'defines_invariant',
        'emits_test_result', 'records_validation_outcome',
        'links_to_execution_trace', 'gates_promotion', 'detects_regression',
    ]

    # P1608 synthetic edges: line_no=1 AND symbol matches hardcoded pattern
    p1608_synthetic_symbols = {
        'mutation_signature', 'parent_snapshot_hash', 'policy_verification',
        'dispatches_execution_plan', 'defines_test_case', 'defines_test_suite',
        'defines_invariant', 'emits_test_result', 'records_validation_outcome',
        'links_to_execution_trace', 'gates_promotion', 'detects_regression',
    }

    print("=" * 70)
    print("§1: SYNTHETIC EDGE DETECTION")
    print("=" * 70)

    total_edges = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    print(f"\nTotal edges in ADG: {total_edges:,}")

    # Count by P1608 relation type
    p1608_counts = {}
    p1608_total = 0
    for rt in p1608_types:
        # Count edges with line_no=1 AND symbol matching (P1608 signature)
        cnt_synthetic = cur.execute(
            "SELECT COUNT(*) FROM edges WHERE relation_type=? AND line_no=1 AND symbol=?",
            (rt, rt)
        ).fetchone()[0]
        cnt_all = cur.execute(
            "SELECT COUNT(*) FROM edges WHERE relation_type=?", (rt,)
        ).fetchone()[0]
        p1608_counts[rt] = (cnt_synthetic, cnt_all)
        p1608_total += cnt_synthetic

    print(f"\n{'Relation Type':<35} {'Synthetic':>10} {'Total':>10} {'Synth%':>8}")
    print("-" * 65)
    for rt, (synth, total) in sorted(p1608_counts.items()):
        pct = (synth / total * 100) if total > 0 else 0
        print(f"{rt:<35} {synth:>10,} {total:>10,} {pct:>7.1f}%")

    synth_ratio = p1608_total / total_edges if total_edges > 0 else 0
    print(f"\n{'TOTAL P1608 SYNTHETIC':<35} {p1608_total:>10,} {total_edges:>10,} {synth_ratio*100:>7.2f}%")
    print(f"\n  synthetic_edge_ratio = {synth_ratio:.6f} ({p1608_total:,} / {total_edges:,})")

    # Check if any synthetic edges contribute to gap closure numerators
    # Gap closure numerators: the P1/P2/P3/P4 edge types
    gap_numerator_types = {
        'routes_to_agent', 'orchestrates_workflow', 'dispatches_execution_plan',
        'validates_agent_capability', 'checks_agent_registry',
        'authorize_and_execute', 'validates_capability', 'routes_to_capability',
        'writes_via_uwg', 'blocks_direct_write', 'records_tool_invocation',
        'captures_execution_output',
        'dispatches_agent', 'coordinates_agents', 'records_workflow_lineage',
        'records_healing_outcome', 'escalates_failure', 'invokes_evaluation',
        'records_telemetry_event', 'captures_evaluation_metric',
        'stores_embedding', 'updates_meta_learning_state', 'links_execution_to_snapshot',
        'captures_pattern', 'records_learning_event', 'writes_learning_snapshot',
        'feeds_meta_learning', 'updates_routing_strategy', 'improves_agent_policy',
        'stores_learning_state',
    }

    overlap = set(p1608_types) & gap_numerator_types
    if overlap:
        print(f"\n  WARNING: OVERLAP: P1608 synthetic types in gap numerators: {overlap}")
        for rt in overlap:
            synth, total = p1608_counts[rt]
            print(f"    {rt}: {synth} synthetic out of {total} total")
    else:
        print("\n  OK: No P1608 synthetic types overlap with gap numerators")

    return {
        'synthetic_edge_ratio': synth_ratio,
        'p1608_total': p1608_total,
        'total_edges': total_edges,
        'p1608_counts': {k: v for k, v in p1608_counts.items()},
        'overlap_with_gap_numerators': list(overlap),
    }


# ─── §2: DETERMINISM DIGEST VALIDATION ──────────────────────────────────────

def audit_determinism_digest(conn):
    """Check if digest includes semantic enrichment fields."""
    print("\n" + "=" * 70)
    print("§2: DETERMINISM DIGEST VALIDATION")
    print("=" * 70)

    cur = conn.cursor()

    # Get column names
    cur.execute("PRAGMA table_info(edges)")
    columns = [row[1] for row in cur.fetchall()]
    print(f"\n  Edge table columns: {columns}")

    # Check which fields exist
    semantic_fields = ['semantic_type', 'confidence', 'source_span_line',
                       'source_span_column', 'target_span_line', 'target_span_column',
                       'dynamic_resolution']
    present = [f for f in semantic_fields if f in columns]
    missing = [f for f in semantic_fields if f not in columns]

    print(f"  Semantic fields PRESENT in schema: {present}")
    print(f"  Semantic fields MISSING from schema: {missing}")

    # Sample edges with semantic fields populated
    if present:
        cnt_total = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        for field in present:
            cnt_populated = cur.execute(
                f"SELECT COUNT(*) FROM edges WHERE {field} IS NOT NULL AND CAST({field} AS TEXT) != '' AND CAST({field} AS TEXT) != '0'"
            ).fetchone()[0]
            print(f"  {field}: {cnt_populated:,} / {cnt_total:,} populated ({cnt_populated/cnt_total*100:.1f}%)")

    # Now check what the digest actually covers
    # Read the scanner digest computation
    print("\n  Checking scanner digest computation...")
    scanner_path = ROOT / "agentic_core" / "adg" / "extraction" / "static_scanner.py"
    with open(scanner_path, encoding='utf-8') as f:
        scanner_src = f.read()

    # Find digest/hash computation
    digest_sensitive = 'semantic_type' in scanner_src and 'hashlib' in scanner_src
    print(f"  Scanner references 'semantic_type' in digest context: {digest_sensitive}")

    # Compute two digests: structural-only vs full
    # Sample 1000 edges
    sample = cur.execute(
        "SELECT src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol FROM edges LIMIT 1000"
    ).fetchall()

    structural_hash = hashlib.sha256()
    for row in sample:
        structural_hash.update(str(row).encode())
    structural_digest = structural_hash.hexdigest()[:16]

    # Full hash including semantic fields if available
    if present:
        cols = "src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol, " + ", ".join(present)
        full_sample = cur.execute(f"SELECT {cols} FROM edges LIMIT 1000").fetchall()
        full_hash = hashlib.sha256()
        for row in full_sample:
            full_hash.update(str(row).encode())
        full_digest = full_hash.hexdigest()[:16]

        sensitivity = "WEAK" if structural_digest == full_digest else "SENSITIVE"
        print(f"\n  Structural digest (sample): {structural_digest}")
        print(f"  Full digest (sample):       {full_digest}")
        print(f"  semantic_digest_sensitivity: {sensitivity}")
    else:
        sensitivity = "N/A (no semantic fields in schema)"
        full_digest = structural_digest
        print(f"\n  semantic_digest_sensitivity: {sensitivity}")

    return {
        'semantic_fields_present': present,
        'semantic_fields_missing': missing,
        'semantic_digest_sensitivity': sensitivity,
        'structural_digest': structural_digest,
        'full_digest': full_digest,
    }


# ─── §3: SYMBOL IDENTITY CONSISTENCY ────────────────────────────────────────

def audit_symbol_consistency(conn):
    """Check symbol construction consistency across visitors."""
    print("\n" + "=" * 70)
    print("§3: SYMBOL IDENTITY CONSISTENCY")
    print("=" * 70)

    cur = conn.cursor()

    # Check: for same source_file, how many distinct src_id values exist?
    cur.execute("""
        SELECT source_file, COUNT(DISTINCT src_id) as distinct_src_ids
        FROM edges
        GROUP BY source_file
        HAVING distinct_src_ids > 1
    """)
    multi_from = cur.fetchall()

    total_files = cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges").fetchone()[0]
    files_with_multi_from = len(multi_from)

    print(f"\n  Total source files with edges: {total_files:,}")
    print(f"  Files with >1 distinct src_id: {files_with_multi_from:,}")

    # This is expected for files with classes/functions (symbol-level nodes)
    # The real check: for MODULE-level from_nodes, is the naming consistent?

    # Check src_id patterns via join with nodes
    cur.execute("""
        SELECT DISTINCT n.adg_name
        FROM edges e JOIN nodes n ON e.src_id = n.id
        LIMIT 20
    """)
    sample_from = [r[0] for r in cur.fetchall()]
    print("\n  Sample src node adg_name patterns:")
    for fn in sample_from[:10]:
        print(f"    {fn}")

    # Check for fragmentation: same logical entity with different IDs
    cur.execute("""
        SELECT n.adg_name, COUNT(DISTINCT e.relation_type) as edge_types
        FROM edges e JOIN nodes n ON e.src_id = n.id
        WHERE n.adg_name LIKE 'ADG::Module::%'
        GROUP BY n.adg_name
        ORDER BY edge_types DESC
        LIMIT 10
    """)
    top_modules = cur.fetchall()
    print("\n  Top modules by edge type diversity:")
    for mod, cnt in top_modules:
        print(f"    {mod}: {cnt} distinct edge types")

    # Symbol alignment: check if ExecutionSemantic vs other visitors
    # produce same symbol for same code
    cur.execute("""
        SELECT source_file, line_no, symbol, COUNT(DISTINCT relation_type) as rt_count
        FROM edges
        WHERE line_no > 0
        GROUP BY source_file, line_no, symbol
        HAVING rt_count > 1
        LIMIT 20
    """)
    shared_locations = cur.fetchall()

    # Check for same file+line but DIFFERENT symbols
    cur.execute("""
        SELECT source_file, line_no, GROUP_CONCAT(DISTINCT symbol) as symbols, COUNT(DISTINCT symbol) as sym_count
        FROM edges
        WHERE line_no > 1
        GROUP BY source_file, line_no
        HAVING sym_count > 1
        LIMIT 20
    """)
    fragmented = cur.fetchall()

    total_locations = cur.execute(
        "SELECT COUNT(DISTINCT source_file || ':' || line_no) FROM edges WHERE line_no > 1"
    ).fetchone()[0]
    fragmented_count = len(fragmented)

    alignment_rate = 1.0 - (fragmented_count / total_locations) if total_locations > 0 else 1.0

    print(f"\n  Total unique (file, line) locations: {total_locations:,}")
    print(f"  Locations with symbol fragmentation: {fragmented_count}")
    print(f"  symbol_alignment_rate: {alignment_rate:.6f}")

    if fragmented:
        print("\n  Sample fragmented locations:")
        for sf, ln, syms, cnt in fragmented[:5]:
            print(f"    {sf}:{ln} -> {cnt} symbols: {syms[:100]}")

    return {
        'symbol_alignment_rate': alignment_rate,
        'total_locations': total_locations,
        'fragmented_locations': fragmented_count,
        'fragmented_samples': [(sf, ln, syms) for sf, ln, syms, _ in fragmented[:10]],
    }


# ─── §4: DUPLICATE EDGE GENERATION ──────────────────────────────────────────

def audit_duplicate_edges(conn):
    """Detect double-counting across visitors."""
    print("\n" + "=" * 70)
    print("§4: DUPLICATE EDGE GENERATION")
    print("=" * 70)

    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

    # Exact duplicates: same (src_id, dst_id, relation_type, edge_kind)
    cur.execute("""
        SELECT src_id, dst_id, relation_type, edge_kind, COUNT(*) as cnt
        FROM edges
        GROUP BY src_id, dst_id, relation_type, edge_kind
        HAVING cnt > 1
        ORDER BY cnt DESC
        LIMIT 20
    """)
    dupes = cur.fetchall()

    total_dupe_groups = cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT src_id, dst_id, relation_type, edge_kind, COUNT(*) as cnt
            FROM edges
            GROUP BY src_id, dst_id, relation_type, edge_kind
            HAVING cnt > 1
        )
    """).fetchone()[0]

    total_excess = cur.execute("""
        SELECT SUM(cnt - 1) FROM (
            SELECT src_id, dst_id, relation_type, edge_kind, COUNT(*) as cnt
            FROM edges
            GROUP BY src_id, dst_id, relation_type, edge_kind
            HAVING cnt > 1
        )
    """).fetchone()[0] or 0

    dupe_ratio = total_excess / total if total > 0 else 0

    print(f"\n  Total edges: {total:,}")
    print(f"  Duplicate groups (exact match on from,to,rel,kind): {total_dupe_groups:,}")
    print(f"  Excess duplicate edges: {total_excess:,}")
    print(f"  duplicate_edge_ratio: {dupe_ratio:.6f}")

    if dupes:
        print("\n  Top duplicates:")
        for sid, did, rt, ek, cnt in dupes[:10]:
            print(f"    [{cnt}x] {rt}/{ek}: src={sid} -> dst={did}")

    # Also check _P1608 vs other visitors overlap
    cur.execute("""
        SELECT src_id, dst_id, relation_type, edge_kind, symbol, line_no, COUNT(*) as cnt
        FROM edges
        WHERE relation_type = 'dispatches_execution_plan'
        GROUP BY src_id, dst_id, relation_type, edge_kind
        HAVING cnt > 1
        ORDER BY cnt DESC
        LIMIT 10
    """)
    dep_dupes = cur.fetchall()
    if dep_dupes:
        print("\n  dispatches_execution_plan duplicates (P1608 vs P1Orch):")
        for row in dep_dupes[:5]:
            print(f"    [{row[6]}x] src={row[0]} -> dst={row[1]} (sym={row[4]}, ln={row[5]})")

    return {
        'duplicate_edge_ratio': dupe_ratio,
        'total_dupe_groups': total_dupe_groups,
        'total_excess': total_excess,
    }


# ─── §5: DENOMINATOR INTEGRITY TEST ─────────────────────────────────────────

def audit_denominator_integrity(conn):
    """Compare scanner denominators vs independent AST traversal."""
    print("\n" + "=" * 70)
    print("§5: DENOMINATOR INTEGRITY TEST")
    print("=" * 70)

    cur = conn.cursor()

    # Denominators per memory: writes_to, reads_from, records_execution_trace, calls, applies_guardrail
    denom_types = ['writes_to', 'reads_from', 'records_execution_trace', 'calls', 'applies_guardrail']

    print(f"\n  {'Relation Type':<30} {'Scanner Count':>15}")
    print("  " + "-" * 47)
    for dt in denom_types:
        cnt = cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (dt,)).fetchone()[0]
        print(f"  {dt:<30} {cnt:>15,}")

    # Independent check: count Python files in the repo that the scanner should cover
    total_modules = cur.execute("SELECT COUNT(DISTINCT source_file) FROM edges").fetchone()[0]
    total_py_files = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Skip excluded dirs
        rel = os.path.relpath(dirpath, ROOT)
        if any(x in rel for x in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
            continue
        for f in filenames:
            if f.endswith('.py'):
                total_py_files += 1

    print(f"\n  Total .py files in repo: {total_py_files:,}")
    print(f"  Total distinct source_file in edges: {total_modules:,}")
    module_coverage = total_modules / total_py_files if total_py_files > 0 else 0
    print(f"  Module coverage: {module_coverage:.2%}")

    # Check records_execution_trace — should these be only from EXECUTION_TRACE_CLASSES?
    cur.execute("""
        SELECT symbol, COUNT(*) as cnt FROM edges
        WHERE relation_type='records_execution_trace'
        GROUP BY symbol ORDER BY cnt DESC LIMIT 10
    """)
    ret_symbols = cur.fetchall()
    print("\n  records_execution_trace top symbols:")
    for sym, cnt in ret_symbols:
        print(f"    {sym}: {cnt}")

    # Check applies_guardrail
    cur.execute("""
        SELECT symbol, COUNT(*) as cnt FROM edges
        WHERE relation_type='applies_guardrail'
        GROUP BY symbol ORDER BY cnt DESC LIMIT 10
    """)
    ag_symbols = cur.fetchall()
    print("\n  applies_guardrail top symbols:")
    for sym, cnt in ag_symbols:
        print(f"    {sym}: {cnt}")

    return {
        'module_coverage': module_coverage,
        'total_py_files': total_py_files,
        'total_modules_in_edges': total_modules,
    }


# ─── §8: SCANNER SELF-INSTRUMENTATION CHECK ─────────────────────────────────

def audit_self_instrumentation(conn):
    """Check if scanner's own _emit_* calls produce edges that inflate metrics."""
    print("\n" + "=" * 70)
    print("§8: SCANNER SELF-INSTRUMENTATION CHECK")
    print("=" * 70)

    cur = conn.cursor()

    # Scanner file
    scanner_files = [
        'agentic_core/adg/extraction/static_scanner.py',
    ]

    for sf in scanner_files:
        total_from_scanner = cur.execute(
            "SELECT COUNT(*) FROM edges WHERE source_file=?", (sf,)
        ).fetchone()[0]

        print(f"\n  Edges from {sf}: {total_from_scanner:,}")

        # Breakdown by relation type
        cur.execute("""
            SELECT relation_type, COUNT(*) as cnt
            FROM edges WHERE source_file=?
            GROUP BY relation_type ORDER BY cnt DESC
        """, (sf,))
        for rt, cnt in cur.fetchall():
            print(f"    {rt}: {cnt}")

    # Check: scanner file producing edges where symbol is _emit_* (self-instrumentation)
    cur.execute("""
        SELECT relation_type, COUNT(*) as cnt
        FROM edges
        WHERE source_file='agentic_core/adg/extraction/static_scanner.py'
          AND (symbol LIKE '%%_emit_%%' OR symbol LIKE '%%emit_%%')
        GROUP BY relation_type ORDER BY cnt DESC
    """)
    self_emit_edges = cur.fetchall()

    total_self = sum(cnt for _, cnt in self_emit_edges) if self_emit_edges else 0
    total_all = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    self_ratio = total_self / total_all if total_all > 0 else 0

    print(f"\n  Self-generated edges (scanner _emit_* symbols): {total_self}")
    print(f"  self_generated_edge_ratio: {self_ratio:.6f}")

    if self_emit_edges:
        print("\n  Self-emit edge types:")
        for rt, cnt in self_emit_edges:
            print(f"    {rt}: {cnt}")

    # Check lifecycle_trace_contract too — it bootstraps itself
    ltc_file = 'agentic_core/runtime/lifecycle_trace_contract.py'
    ltc_edges = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE source_file=?", (ltc_file,)
    ).fetchone()[0]
    print(f"\n  Edges from {ltc_file}: {ltc_edges:,}")

    # Module-level _emit_* calls in scanner (self-bootstrap)
    cur.execute("""
        SELECT relation_type, symbol, line_no, COUNT(*)
        FROM edges
        WHERE source_file='agentic_core/adg/extraction/static_scanner.py'
          AND line_no < 400
        GROUP BY relation_type, symbol
        ORDER BY line_no
        LIMIT 40
    """)
    bootstrap_edges = cur.fetchall()
    if bootstrap_edges:
        print("\n  Scanner module-level edges (lines 1-400, likely bootstrap):")
        for rt, sym, ln, cnt in bootstrap_edges:
            print(f"    L{ln}: {rt} / {sym} [{cnt}]")

    return {
        'self_generated_edge_ratio': self_ratio,
        'total_self_emit_edges': total_self,
        'scanner_total_edges': cur.execute(
            "SELECT COUNT(*) FROM edges WHERE source_file='agentic_core/adg/extraction/static_scanner.py'"
        ).fetchone()[0],
    }


# ─── §6: EXECUTION vs AST GAP ───────────────────────────────────────────────

def audit_execution_vs_ast(conn):
    """Compare edge types distribution and check for false positives."""
    print("\n" + "=" * 70)
    print("§6: EXECUTION vs AST GAP (structural analysis)")
    print("=" * 70)

    cur = conn.cursor()

    # We can't build a full runtime shadow graph without running the system,
    # but we CAN check for structural indicators of false positives:
    # 1. Edges with line_no=0 or line_no=1 (no real AST location)
    line0 = cur.execute("SELECT COUNT(*) FROM edges WHERE line_no = 0").fetchone()[0]
    line1 = cur.execute("SELECT COUNT(*) FROM edges WHERE line_no = 1").fetchone()[0]
    total = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    real_lines = total - line0 - line1

    print(f"\n  Edges with line_no=0 (no location): {line0:,} ({line0/total*100:.1f}%)")
    print(f"  Edges with line_no=1 (possible synthetic): {line1:,} ({line1/total*100:.1f}%)")
    print(f"  Edges with real line locations (>1): {real_lines:,} ({real_lines/total*100:.1f}%)")

    # Breakdown of line_no=1 by relation_type
    cur.execute("""
        SELECT relation_type, COUNT(*) as cnt
        FROM edges WHERE line_no = 1
        GROUP BY relation_type ORDER BY cnt DESC
        LIMIT 20
    """)
    line1_types = cur.fetchall()
    print("\n  Top relation types at line_no=1:")
    for rt, cnt in line1_types:
        print(f"    {rt}: {cnt:,}")

    # line_no=0 types
    cur.execute("""
        SELECT relation_type, COUNT(*) as cnt
        FROM edges WHERE line_no = 0
        GROUP BY relation_type ORDER BY cnt DESC
        LIMIT 20
    """)
    line0_types = cur.fetchall()
    print("\n  Top relation types at line_no=0:")
    for rt, cnt in line0_types:
        print(f"    {rt}: {cnt:,}")

    return {
        'edges_line0': line0,
        'edges_line1': line1,
        'edges_real_lines': real_lines,
        'ast_location_rate': real_lines / total if total > 0 else 0,
    }


# ─── §7: HEURISTIC vs TRUE SEMANTIC ─────────────────────────────────────────

def audit_semantic_classification(conn):
    """Sample edges and check semantic classification accuracy."""
    print("\n" + "=" * 70)
    print("§7: HEURISTIC vs TRUE SEMANTIC CLASSIFICATION")
    print("=" * 70)

    cur = conn.cursor()

    # Focus on flows_to, controls_flow, emits_side_effect
    semantic_types = ['flows_to', 'controls_flow', 'emits_side_effect']

    for st in semantic_types:
        cnt = cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (st,)).fetchone()[0]
        print(f"\n  {st}: {cnt:,} edges")

        # Sample with line locations
        cur.execute("""
            SELECT source_file, line_no, symbol, src_id, dst_id
            FROM edges WHERE relation_type=? AND line_no > 1
            LIMIT 5
        """, (st,))
        samples = cur.fetchall()
        for sf, ln, sym, sid, did in samples:
            print(f"    {sf}:{ln} sym={sym} src={sid} dst={did}")

        # Check: what % have real line numbers?
        real = cur.execute(
            "SELECT COUNT(*) FROM edges WHERE relation_type=? AND line_no > 1", (st,)
        ).fetchone()[0]
        total = max(cnt, 1)
        print(f"    Real line locations: {real}/{cnt} ({real/total*100:.1f}%)")

    # For flows_to: verify against AST that the assignment actually exists
    # Sample 10 flows_to edges and check the source file
    cur.execute("""
        SELECT source_file, line_no, symbol, src_id, dst_id
        FROM edges WHERE relation_type='flows_to' AND line_no > 1
        ORDER BY RANDOM() LIMIT 10
    """)
    flow_samples = cur.fetchall()

    verified = 0
    checked = 0
    print("\n  AST verification of flows_to samples:")
    for sf, ln, sym, sid, did in flow_samples:
        fpath = ROOT / sf
        if fpath.exists():
            try:
                with open(fpath, encoding='utf-8', errors='replace') as f:
                    src = f.read()
                tree = ast.parse(src, filename=str(fpath))
                # Check if line_no has an assignment
                has_assign = False
                for node in ast.walk(tree):
                    if hasattr(node, 'lineno') and node.lineno == ln:
                        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.For, ast.With)):
                            has_assign = True
                            break
                checked += 1
                if has_assign:
                    verified += 1
                    print(f"    OK {sf}:{ln} -- assignment confirmed")
                else:
                    print(f"    ?? {sf}:{ln} -- no assignment at line (may be nested)")
            except (ValueError, TypeError, RuntimeError) as e:
                print(f"    FAIL {sf}:{ln} -- parse error: {e}")
        else:
            print(f"    SKIP {sf} -- file not found")

    accuracy = verified / checked if checked > 0 else 0
    print(f"\n  flows_to AST verification: {verified}/{checked} ({accuracy:.0%})")

    return {
        'semantic_accuracy_estimate': accuracy,
        'checked': checked,
        'verified': verified,
    }


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    conn = get_conn()

    results = {}
    results['s1'] = audit_synthetic_edges(conn)
    results['s2'] = audit_determinism_digest(conn)
    results['s3'] = audit_symbol_consistency(conn)
    results['s4'] = audit_duplicate_edges(conn)
    results['s5'] = audit_denominator_integrity(conn)
    results['s6'] = audit_execution_vs_ast(conn)
    results['s7'] = audit_semantic_classification(conn)
    results['s8'] = audit_self_instrumentation(conn)

    # ─── §9: FINAL OUTPUT ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("§9: FINAL METRICS TABLE")
    print("=" * 70)

    metrics = {
        'synthetic_edge_ratio': results['s1']['synthetic_edge_ratio'],
        'semantic_digest_sensitivity': results['s2']['semantic_digest_sensitivity'],
        'symbol_alignment_rate': results['s3']['symbol_alignment_rate'],
        'duplicate_edge_ratio': results['s4']['duplicate_edge_ratio'],
        'ast_location_rate': results['s6']['ast_location_rate'],
        'semantic_accuracy_estimate': results['s7']['semantic_accuracy_estimate'],
        'self_generated_edge_ratio': results['s8']['self_generated_edge_ratio'],
    }

    print(f"\n  {'Metric':<35} {'Value':>15}")
    print("  " + "-" * 52)
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k:<35} {v:>15.6f}")
        else:
            print(f"  {k:<35} {str(v):>15}")

    conn.close()
    return results


if __name__ == "__main__":
    main()
