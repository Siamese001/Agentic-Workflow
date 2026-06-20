"""
Validate Phase 1-16 uncovered findings via independent ADG queries.
Each category gets a cross-check that catches false positives:
  - Trace-edge detection gaps (Phase 9)
  - Dynamic-import false fan_in=0 (Phase 15)
  - Constant naming false positives (Phase 14)
  - Same-layer-type-name aliasing (Phase 2)
"""

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import json
import sqlite3
from pathlib import Path
from collections import Counter

DB = Path(r"artifacts/adg/adg_indexed_04252026_0521.sqlite")
ART = Path(r"artifacts")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()


def hr(label: str) -> None:
    print()
    print("=" * 90)
    print(label)
    print("=" * 90)


# -------------------------------------------------------------------
# Validation 1 — SSOT duplicate symbol names: are they really cross-LAYER?
# -------------------------------------------------------------------
hr("VAL-1  SSOT duplicate symbol names — distinct layer count for top 10")
p1 = json.loads((ART / "audit_phase1_ssot_dup_symbols.json").read_text(encoding="utf-8"))
print(f"  total Phase 1 findings: {len(p1['findings'])}")
true_cross_layer = 0
single_layer = 0
for f in p1["findings"][:25]:
    layers = f.get("distinct_layers", [])
    if isinstance(layers, str):
        layers = [x.strip() for x in layers.split(",") if x.strip()]
    n = len(set(layers))
    sn = f.get("short_name", "?")
    files = f.get("files_count") or f.get("file_count") or "?"
    flag = "✓ cross-layer" if n >= 2 else "✗ single-layer"
    if n >= 2:
        true_cross_layer += 1
    else:
        single_layer += 1
    print(f"  {flag}  {sn:<30s} layers={layers}  files={files}")
print(f"  Verdict: {true_cross_layer}/{true_cross_layer+single_layer} truly cross-layer in top 25")


# -------------------------------------------------------------------
# Validation 9 — Observability blind spots: re-check WIDER trace patterns
# -------------------------------------------------------------------
hr("VAL-9  Observability blind spots — wider trace-edge re-check")
p9 = json.loads((ART / "audit_phase9_observability_blind_spots.json").read_text(encoding="utf-8"))
print(f"  total Phase 9 findings: {len(p9['findings'])}")

# For each finding, count ALL outgoing edges to anything looking like obs (broader patterns)
true_blind = []
false_pos = []
for f in p9["findings"]:
    nid = f["id"]
    # broader: any edge to L6, any edge to a module containing tracing/logging/metric/audit/observ
    cur.execute("""
        SELECT COUNT(DISTINCT e.dst_id)
        FROM edges e
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.src_id = ?
          AND (
            dst.layer = 'L6'
            OR dst.adg_name LIKE '%trace%'
            OR dst.adg_name LIKE '%logger%' OR dst.adg_name LIKE '%logging%'
            OR dst.adg_name LIKE '%metric%' OR dst.adg_name LIKE '%audit%'
            OR dst.adg_name LIKE '%observ%' OR dst.adg_name LIKE '%otel%'
            OR dst.adg_name LIKE '%span%' OR dst.adg_name LIKE '%emit%'
            OR dst.adg_name LIKE '%MetricsEmission%'
          )
    """, (nid,))
    obs_edges = cur.fetchone()[0]
    rec = (obs_edges, f["resolved_path"], f["fan_in"])
    if obs_edges == 0:
        true_blind.append(rec)
    else:
        false_pos.append(rec)

print(f"  TRUE BLIND (0 obs edges by broader pattern): {len(true_blind)}")
for obs, path, fi in true_blind:
    print(f"     fi={fi:<6d} obs={obs} {path}")
print(f"  FALSE POSITIVES (had >=1 obs edge): {len(false_pos)}")
for obs, path, fi in false_pos[:5]:
    print(f"     fi={fi:<6d} obs={obs} {path}")


# -------------------------------------------------------------------
# Validation 10 — Hardcoded external literals: spot-check exclusion-allowlist
# -------------------------------------------------------------------
hr("VAL-10  Hardcoded external literals — verify NOT already in exclusion config")
p10 = json.loads((ART / "audit_phase10_hardcoded_external.json").read_text(encoding="utf-8"))
print(f"  total Phase 10 findings: {len(p10['findings'])}")
# Group by pattern
by_pat = Counter(f["matched_pattern"] for f in p10["findings"])
for pat, cnt in by_pat.most_common():
    print(f"  {pat:<32s} {cnt}")
print()
print("  Sample raw findings (first 10):")
for f in p10["findings"][:10]:
    print(f"     {f['matched_pattern']:<28s} {f['file_path']}:{f['line_no']} ev={f['evidence']}")


# -------------------------------------------------------------------
# Validation 12 — Mixed-callee-layer dispatchers: filter out legitimate utility access
# -------------------------------------------------------------------
hr("VAL-12  Mixed-callee-layer dispatchers — strip away dispatchers whose callees are mostly L_SHARED/L_RUNTIME/L_TOOLS")
p12 = json.loads((ART / "audit_phase12_mixed_callee_layers.json").read_text(encoding="utf-8"))
print(f"  total Phase 12 findings: {len(p12['findings'])}")
# A dispatcher is "real" if it crosses MAINLINE layers (L0..L5), not just util layers
mainline = {"L0", "L1", "L2", "L3", "L4", "L5"}
true_dispatchers = []
for f in p12["findings"]:
    callees = set(f["callee_layers"].split(","))
    main_callees = callees & mainline
    # Exclude self-layer
    main_callees.discard(f["layer"])
    if len(main_callees) >= 3:  # crosses 3+ MAINLINE layers
        true_dispatchers.append((len(main_callees), main_callees, f["resolved_path"], f["layer"]))
print(f"  TRUE cross-mainline dispatchers (>=3 mainline callees, excluding self): {len(true_dispatchers)}")
for n, m, path, lay in sorted(true_dispatchers, reverse=True)[:20]:
    print(f"     L={lay:5s} crosses {n} mainline layers {sorted(m)}  {path}")


# -------------------------------------------------------------------
# Validation 14 — env vars: verify the symbols actually reference os.environ/getenv
# (current Phase 14 used name pattern; tighten to require flows_to/calls to os.environ/getenv nodes)
# -------------------------------------------------------------------
hr("VAL-14  Env var refs outside config — tightened: require edge to os.environ/getenv")
cur.execute("""
    SELECT DISTINCT n.resolved_path, n.layer
    FROM edges e
    JOIN nodes n ON n.id = e.src_id
    JOIN nodes dst ON dst.id = e.dst_id
    WHERE n.entity_type = 'module'
      AND n.layer IN ('L0','L1','L2','L3','L4','L5')
      AND n.resolved_path NOT LIKE '%/config/%'
      AND n.resolved_path NOT LIKE '%_config.py'
      AND n.resolved_path NOT LIKE 'tests/%'
      AND (dst.adg_name LIKE '%os.environ%' OR dst.adg_name LIKE '%os.getenv%' OR dst.adg_name = 'getenv')
    ORDER BY n.layer, n.resolved_path
    LIMIT 50
""")
tight_env = cur.fetchall()
print(f"  tightened (require explicit os.environ/getenv edge): {len(tight_env)}")
for r in tight_env[:25]:
    print(f"     L={r[1]:5s}  {r[0]}")


# -------------------------------------------------------------------
# Validation 15 — Orphan config with blast radius: rule out runtime importlib loaders
# (a config is NOT truly orphan if a known dynamic-loader module flows_to it)
# -------------------------------------------------------------------
hr("VAL-15  Orphan config — rule out dynamic loaders (flows_to / resolves_callsite / invokes_dynamic)")
p15 = json.loads((ART / "audit_phase15_orphan_config.json").read_text(encoding="utf-8"))
print(f"  total Phase 15 findings: {len(p15['findings'])}")
true_orphan = []
loader_referenced = []
for f in p15["findings"]:
    nid = f["id"]
    cur.execute("""
        SELECT COUNT(*)
        FROM edges e
        WHERE e.dst_id = ?
          AND e.relation_type IN ('flows_to','resolves_callsite','invokes_dynamic','reads_from')
    """, (nid,))
    dyn_in = cur.fetchone()[0]
    if dyn_in > 0:
        loader_referenced.append((dyn_in, f["resolved_path"], f["fan_out"]))
    else:
        true_orphan.append((f["fan_out"], f["resolved_path"]))
print(f"  TRUE orphan (no dynamic-load inbound edges): {len(true_orphan)}")
for fo, path in sorted(true_orphan, reverse=True)[:15]:
    print(f"     fo={fo:>3d}  {path}")
print(f"  REFERENCED via dynamic loader (false positive for 'orphan'): {len(loader_referenced)}")
for di, path, fo in sorted(loader_referenced, reverse=True)[:5]:
    print(f"     dyn_in={di}  fo={fo}  {path}")


# -------------------------------------------------------------------
# Validation 13 — Cycles: re-check at the SYMBOL layer (not just module imports)
# (Phase 13 found 0; broaden to symbol-level call cycles)
# -------------------------------------------------------------------
hr("VAL-13  Cycles — broaden to symbol-level CALL cycles (not just module imports)")
cur.execute("""
    SELECT n_a.resolved_path, n_b.resolved_path
    FROM edges e1
    JOIN edges e2 ON e2.src_id = e1.dst_id AND e2.dst_id = e1.src_id
    JOIN nodes n_a ON n_a.id = e1.src_id
    JOIN nodes n_b ON n_b.id = e1.dst_id
    WHERE e1.relation_type = 'calls' AND e2.relation_type = 'calls'
      AND n_a.id < n_b.id
      AND n_a.entity_type = 'symbol' AND n_b.entity_type = 'symbol'
      AND n_a.resolved_path != n_b.resolved_path
      AND n_a.resolved_path NOT LIKE 'tests/%'
      AND n_b.resolved_path NOT LIKE 'tests/%'
    LIMIT 25
""")
sym_cycles = cur.fetchall()
print(f"  symbol-level call cycles: {len(sym_cycles)}")
for r in sym_cycles[:15]:
    print(f"     {r[0]}  <->  {r[1]}")


# -------------------------------------------------------------------
# Final validation summary
# -------------------------------------------------------------------
hr("VALIDATION VERDICT — uncovered findings, post-cross-check")
print(f"  Phase 1  (SSOT dup symbols)            true cross-layer: {true_cross_layer}/{true_cross_layer+single_layer} of top 25 sampled")
print(f"  Phase 9  (Obs blind spots)             true blind:        {len(true_blind)}/{len(p9['findings'])}  ({len(false_pos)} had hidden trace edges)")
print(f"  Phase 12 (Mixed dispatchers)           crosses 3+ mainline layers (real): {len(true_dispatchers)}/{len(p12['findings'])}")
print(f"  Phase 13 (Cycles)                      module-level: 0  symbol-level: {len(sym_cycles)}")
print(f"  Phase 14 (Env vars outside config)     tightened (explicit edge): {len(tight_env)}/76")
print(f"  Phase 15 (Orphan configs)              true orphan: {len(true_orphan)}/{len(p15['findings'])}  ({len(loader_referenced)} dynamic-loader-referenced)")

con.close()
