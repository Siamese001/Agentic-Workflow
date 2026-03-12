"""ADG SQLite ingestion query — joins src_id/dst_id through nodes table for names."""
import sqlite3

DB = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03122026.sqlite"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

# ── helpers ──────────────────────────────────────────────────────────────────
def layer_from_path(path: str) -> str:
    p = path.replace("ADG::Module::", "")
    if p.startswith("agentic_core/L0"): return "L0"
    if p.startswith("agentic_core/L1"): return "L1"
    if p.startswith("agentic_core/L2"): return "L2"
    if p.startswith("agentic_core/L3"): return "L3"
    if p.startswith("agentic_core/L4"): return "L4"
    if p.startswith("agentic_core/L5"): return "L5"
    if p.startswith("agentic_core/L6"): return "L6"
    if p.startswith("apps_"): return "L_APP"
    if p.startswith("system_learning"): return "L_SL"
    if p.startswith("agentic_core/prompt_governance") or p.startswith("agentic_core/knowledge"): return "L_PG"
    if p.startswith("tests/"): return "L_TEST"
    if p.startswith("tools/") or p.startswith("agentic_core/adg"): return "L_TOOLS"
    if p.startswith("ops_scripts"): return "L_OPS"
    if p.startswith("apps_shared"): return "L_SHARED"
    return "OTHER"

sep = "\n" + "="*70

# ── 1. Edge type totals ───────────────────────────────────────────────────────
print(sep + "\n=== EDGE TYPE TOTALS ===")
cur.execute("SELECT relation_type, COUNT(*) c FROM edges GROUP BY relation_type ORDER BY c DESC")
for r in cur: print(f"  {r['relation_type']}: {r['c']}")

# ── 2. Violates edges (with resolved names) ────────────────────────────────────
print(sep + "\n=== VIOLATES EDGES — resolved (sample 30) ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst, e.source_file, e.line_no
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'violates'
    LIMIT 30
""")
for r in cur:
    print(f"  {r['src'][:65]}\n    --> {r['dst'][:65]}\n    @ {r['source_file']}:{r['line_no']}")

# ── 3. writes_to vs writes_through gap ────────────────────────────────────────
print(sep + "\n=== WRITES_TO vs WRITES_THROUGH gap ===")
cur.execute("""
    SELECT COUNT(DISTINCT src_id) FROM edges WHERE relation_type='writes_to'
""")
total_writers = cur.fetchone()[0]
cur.execute("""
    SELECT COUNT(DISTINCT src_id) FROM edges WHERE relation_type='writes_through'
""")
uwg_writers = cur.fetchone()[0]
print(f"  Modules with writes_to:      {total_writers}")
print(f"  Modules with writes_through: {uwg_writers}")
print(f"  Bypass gap:                  {total_writers - uwg_writers}")

# ── 4. writes_to targets — resolved names ─────────────────────────────────────
print(sep + "\n=== WRITES_TO TARGETS — resolved top 30 ===")
cur.execute("""
    SELECT nd.adg_name dst, COUNT(*) c
    FROM edges e JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'writes_to'
    GROUP BY e.dst_id ORDER BY c DESC LIMIT 30
""")
for r in cur:
    print(f"  {r['dst'][:80]}: {r['c']}")

# ── 5. writes_to bypass by layer (source modules not using UWG) ────────────────
print(sep + "\n=== WRITES_TO BYPASS BY LAYER (modules with writes_to but NO writes_through) ===")
cur.execute("""
    SELECT ns.adg_name
    FROM edges e JOIN nodes ns ON ns.id = e.src_id
    WHERE e.relation_type = 'writes_to'
      AND e.src_id NOT IN (SELECT src_id FROM edges WHERE relation_type='writes_through')
    GROUP BY e.src_id
""")
bypass_by_layer = {}
for r in cur:
    lyr = layer_from_path(r['adg_name'])
    bypass_by_layer[lyr] = bypass_by_layer.get(lyr, 0) + 1
for k,v in sorted(bypass_by_layer.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")

# ── 6. generates_prompt by layer ────────────────────────────────────────────────
print(sep + "\n=== GENERATES_PROMPT BY SOURCE LAYER ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'generates_prompt'
""")
gp_by_layer = {}
gp_samples = []
for r in cur:
    lyr = layer_from_path(r['src'])
    gp_by_layer[lyr] = gp_by_layer.get(lyr, 0) + 1
    if len(gp_samples) < 10:
        gp_samples.append((r['src'], r['dst']))
for k,v in sorted(gp_by_layer.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")
print("  Samples:")
for src, dst in gp_samples:
    print(f"    {src[:60]} --> {dst[:60]}")

# ── 7. consumes_prompt — who consumes? ────────────────────────────────────────
print(sep + "\n=== CONSUMES_PROMPT edges (all 11) ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'consumes_prompt'
""")
for r in cur:
    print(f"  {r['src'][:70]} --> {r['dst'][:70]}")

# ── 8. invokes_provider by layer ─────────────────────────────────────────────
print(sep + "\n=== INVOKES_PROVIDER BY SOURCE LAYER ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'invokes_provider'
""")
ip_by_layer = {}
ip_without_l5 = []
for r in cur:
    lyr = layer_from_path(r['src'])
    ip_by_layer[lyr] = ip_by_layer.get(lyr, 0) + 1
for k,v in sorted(ip_by_layer.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")

# ── 9. invokes_provider sources with NO L5 import ────────────────────────────
print(sep + "\n=== INVOKES_PROVIDER SOURCES WITH NO L5 SAFETY IMPORT ===")
cur.execute("""
    SELECT DISTINCT e.src_id, ns.adg_name
    FROM edges e JOIN nodes ns ON ns.id = e.src_id
    WHERE e.relation_type = 'invokes_provider'
""")
provider_callers = {r['src_id']: r['adg_name'] for r in cur}

cur.execute("""
    SELECT DISTINCT e.src_id
    FROM edges e JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'imports'
      AND (nd.adg_name LIKE '%L5_safety%' OR nd.adg_name LIKE '%L5%safety%')
""")
has_l5 = {r['src_id'] for r in cur}

missing_l5 = {sid: name for sid, name in provider_callers.items() if sid not in has_l5
              and 'tests/' not in name and 'tools/' not in name and 'ops_scripts' not in name}
print(f"  Total invokes_provider callers: {len(provider_callers)}")
print(f"  With L5 safety import:          {len(has_l5 & set(provider_callers))}")
print(f"  WITHOUT L5 safety import:       {len(missing_l5)}")
for name in sorted(missing_l5.values())[:25]:
    print(f"    {name[:80]}")

# ── 10. dead_imports by layer ──────────────────────────────────────────────────
print(sep + "\n=== DEAD_IMPORTS BY SOURCE LAYER ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'dead_imports'
""")
di_by_layer = {}
for r in cur:
    lyr = layer_from_path(r['src'])
    di_by_layer[lyr] = di_by_layer.get(lyr, 0) + 1
for k,v in sorted(di_by_layer.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")

# ── 11. antipattern edges — resolved ──────────────────────────────────────────
print(sep + "\n=== ANTIPATTERN EDGES — resolved top targets ===")
cur.execute("""
    SELECT nd.adg_name dst, COUNT(*) c
    FROM edges e JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'antipattern'
    GROUP BY e.dst_id ORDER BY c DESC LIMIT 10
""")
for r in cur:
    print(f"  {r['dst'][:80]}: {r['c']}")

print(sep + "\n=== ANTIPATTERN SOURCE SAMPLE (20) ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst, e.source_file, e.line_no
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'antipattern'
    LIMIT 20
""")
for r in cur:
    print(f"  {r['src'][:60]} --> {r['dst'][:50]} @ {r['source_file']}:{r['line_no']}")

# ── 12. triggered_telemetry — resolved ────────────────────────────────────────
print(sep + "\n=== TRIGGERED_TELEMETRY edges (all) ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst, e.source_file, e.line_no
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'triggered_telemetry'
""")
for r in cur:
    print(f"  {r['src'][:70]} --> {r['dst'][:70]}")
    print(f"    @ {r['source_file']}:{r['line_no']}")

# ── 13. system_learning outbound edges ────────────────────────────────────────
print(sep + "\n=== SYSTEM_LEARNING (L_SL) OUTBOUND EDGES ===")
cur.execute("""
    SELECT e.relation_type, COUNT(*) c
    FROM edges e JOIN nodes ns ON ns.id = e.src_id
    WHERE ns.adg_name LIKE '%system_learning%'
    GROUP BY e.relation_type ORDER BY c DESC
""")
for r in cur:
    print(f"  {r['relation_type']}: {r['c']}")

# ── 14. Who imports from system_learning? ─────────────────────────────────────
print(sep + "\n=== IMPORTS FROM system_learning BY LAYER ===")
cur.execute("""
    SELECT ns.adg_name src
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'imports' AND nd.adg_name LIKE '%system_learning%'
""")
sl_importers = {}
for r in cur:
    lyr = layer_from_path(r['src'])
    sl_importers[lyr] = sl_importers.get(lyr, 0) + 1
for k,v in sorted(sl_importers.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")

# ── 15. routes_through — resolved ─────────────────────────────────────────────
print(sep + "\n=== ROUTES_THROUGH edges (resolved, sample 20) ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'routes_through'
    LIMIT 20
""")
for r in cur:
    print(f"  {r['src'][:65]}")
    print(f"    --> {r['dst'][:65]}")

# ── 16. L3 orchestration outbound edges ───────────────────────────────────────
print(sep + "\n=== L3_orchestration OUTBOUND EDGE TYPES ===")
cur.execute("""
    SELECT e.relation_type, COUNT(*) c
    FROM edges e JOIN nodes ns ON ns.id = e.src_id
    WHERE ns.adg_name LIKE '%L3_orchestration%'
    GROUP BY e.relation_type ORDER BY c DESC
""")
for r in cur:
    print(f"  {r['relation_type']}: {r['c']}")

# ── 17. L4 state — inbound edges ───────────────────────────────────────────────
print(sep + "\n=== L4 INBOUND EDGE TYPES ===")
cur.execute("""
    SELECT e.relation_type, COUNT(*) c
    FROM edges e JOIN nodes nd ON nd.id = e.dst_id
    WHERE nd.adg_name LIKE '%L4%'
    GROUP BY e.relation_type ORDER BY c DESC
""")
for r in cur:
    print(f"  {r['relation_type']}: {r['c']}")

# ── 18. L_APP test coverage gap ───────────────────────────────────────────────
print(sep + "\n=== L_APP TEST COVERAGE GAP ===")
cur.execute("""
    SELECT COUNT(DISTINCT dst_id) FROM edges WHERE relation_type='covers'
""")
covered_ids = cur.fetchone()[0]
cur.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE adg_name LIKE '%apps_%' AND entity_type='module'
""")
total_app = cur.fetchone()[0]
cur.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE adg_name LIKE '%apps_%' AND entity_type='module'
      AND id NOT IN (SELECT dst_id FROM edges WHERE relation_type='covers')
""")
uncovered_app = cur.fetchone()[0]
print(f"  Total nodes with covers edges (any): {covered_ids}")
print(f"  L_APP module nodes total:            {total_app}")
print(f"  L_APP modules with NO covers edge:   {uncovered_app}")

# ── 19. influences edges — what influences what? ──────────────────────────────
print(sep + "\n=== INFLUENCES EDGES BY SOURCE LAYER ===")
cur.execute("""
    SELECT ns.adg_name src
    FROM edges e JOIN nodes ns ON ns.id = e.src_id
    WHERE e.relation_type = 'influences'
""")
inf_by_layer = {}
for r in cur:
    lyr = layer_from_path(r['src'])
    inf_by_layer[lyr] = inf_by_layer.get(lyr, 0) + 1
for k,v in sorted(inf_by_layer.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")

# ── 20. reads_from — config read coverage by layer ────────────────────────────
print(sep + "\n=== READS_FROM (config reads) BY SOURCE LAYER ===")
cur.execute("""
    SELECT ns.adg_name src
    FROM edges e JOIN nodes ns ON ns.id = e.src_id
    WHERE e.relation_type = 'reads_from'
""")
rf_by_layer = {}
for r in cur:
    lyr = layer_from_path(r['src'])
    rf_by_layer[lyr] = rf_by_layer.get(lyr, 0) + 1
for k,v in sorted(rf_by_layer.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")

# ── 21. L5 safety modules — what do they export/cover? ────────────────────────
print(sep + "\n=== L5_safety OUTBOUND EDGE TYPES ===")
cur.execute("""
    SELECT e.relation_type, COUNT(*) c
    FROM edges e JOIN nodes ns ON ns.id = e.src_id
    WHERE ns.adg_name LIKE '%L5_safety%'
    GROUP BY e.relation_type ORDER BY c DESC
""")
for r in cur:
    print(f"  {r['relation_type']}: {r['c']}")

# ── 22. Missing prompt governance: LLM callers with no generates_prompt ────────
print(sep + "\n=== LLM CALLERS (invokes_provider) WITH NO generates_prompt EDGE ===")
cur.execute("SELECT DISTINCT src_id FROM edges WHERE relation_type='invokes_provider'")
llm_callers = {r[0] for r in cur}
cur.execute("SELECT DISTINCT src_id FROM edges WHERE relation_type='generates_prompt'")
has_prompt = {r[0] for r in cur}
ungoverned = llm_callers - has_prompt
print(f"  LLM callers total:                    {len(llm_callers)}")
print(f"  With generates_prompt (governed):     {len(has_prompt & llm_callers)}")
print(f"  WITHOUT generates_prompt (ungoverned):{len(ungoverned)}")
cur.execute(f"""
    SELECT adg_name FROM nodes
    WHERE id IN ({','.join(str(i) for i in sorted(ungoverned)[:50])})
""")
for r in cur:
    print(f"    {r[0][:80]}")

# ── 23. L_SL learning — what writes to L4 (commits learning)? ─────────────────
print(sep + "\n=== L_SL MODULES WRITING TO L4 (learning commits) ===")
cur.execute("""
    SELECT ns.adg_name src, nd.adg_name dst
    FROM edges e
    JOIN nodes ns ON ns.id = e.src_id
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type IN ('writes_to','writes_through')
      AND ns.adg_name LIKE '%system_learning%'
""")
sl_writes = list(cur)
print(f"  Count: {len(sl_writes)}")
for r in sl_writes[:20]:
    print(f"  {r['src'][:70]} --> {r['dst'][:70]}")

# ── 24. orphan modules (no inbound imports, no outbound imports) ───────────────
print(sep + "\n=== ORPHAN MODULES (no imports in or out) BY LAYER ===")
cur.execute("""
    SELECT adg_name FROM nodes
    WHERE entity_type='module'
      AND id NOT IN (SELECT src_id FROM edges WHERE relation_type='imports')
      AND id NOT IN (SELECT dst_id FROM edges WHERE relation_type='imports')
      AND adg_name NOT LIKE '%tests/%'
      AND adg_name NOT LIKE '%ops_scripts%'
      AND adg_name NOT LIKE '%tools/%'
      AND adg_name NOT LIKE '%__pycache__%'
""")
orphan_by_layer = {}
for r in cur:
    lyr = layer_from_path(r[0])
    orphan_by_layer[lyr] = orphan_by_layer.get(lyr, 0) + 1
for k,v in sorted(orphan_by_layer.items(), key=lambda x:-x[1]):
    print(f"  {k}: {v}")

db.close()
print("\nDONE")
