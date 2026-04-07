"""Redis hot-cache ADG query for unified routing consolidation plan."""

import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

ROUTING_FRAGS = [
    "healing_tier_router",
    "healing_tier_config",
    "heal_policy_types",
    "_ssot_routing",
    "_ssot_types",
    "_ssot_reporting",
    "tiered_batch_util",
    "qwen_meta_learning",
    "SovereignBaseAgent",
    "decorators_util",
    "healing_tier_dispatcher",
]

ROUTING_SYMS = [
    "route_healing_tier",
    "route_by_confidence",
    "compute_heal_confidence",
    "decide_heal_escalation",
    "classify_score",
    "classify_confidence",
    "decide_reasoning_tier",
    "compute_routing_decision",
    "should_proceed_with_healing",
    "calculate_healing_confidence",
]

THRESHOLD_SYMS = [
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "SCORE_THRESHOLD_DET",
    "SCORE_THRESHOLD_QWEN",
    "SOVEREIGN_HIGH_CONFIDENCE",
    "SOVEREIGN_MEDIUM_CONFIDENCE",
]

out = []


def p(s=""):
    out.append(s)
    print(s)


# ── Helper: get node dict ───────────────────────────────────────────────────
def get_node(nid):
    return r.hgetall(f"adg:node:{nid}")


def skip(path):
    return any(x in (path or "") for x in ("archive", "backup", ".backup"))


# ── Q1: Module nodes for routing files ─────────────────────────────────────
p("=== Q1: ROUTING MODULE NODES ===")
file_module_ids = {}  # frag -> list[nid]
for frag in ROUTING_FRAGS:
    matched_keys = list(r.scan_iter(f"adg:nodes:by_file:*{frag}*"))
    for mk in matched_keys:
        file_path = mk.replace("adg:nodes:by_file:", "")
        if skip(file_path) or "test" in file_path:
            continue
        node_ids = r.smembers(mk)
        for nid in node_ids:
            nd = get_node(nid)
            if nd.get("entity_type") == "module":
                p(f"  id={nid:<6} layer={nd.get('layer', '?'):<14} {file_path}")
                file_module_ids.setdefault(frag, []).append(nid)

# ── Q2: Routing/threshold symbols ──────────────────────────────────────────
p("\n=== Q2: ROUTING + THRESHOLD SYMBOLS (defined in) ===")
sym_node_map = {}  # sym -> list[nid]
for sym in ROUTING_SYMS + THRESHOLD_SYMS:
    matched_keys = list(r.scan_iter("adg:nodes:by_file:*"))
    # search by adg_name prefix scan
    found = []
    for mk in r.scan_iter("adg:nodes:by_file:*"):
        file_path = mk.replace("adg:nodes:by_file:", "")
        if skip(file_path):
            continue
        for nid in r.smembers(mk):
            nd = get_node(nid)
            name = nd.get("adg_name", "")
            if sym in name and nd.get("entity_type") == "symbol":
                found.append((nid, file_path, name))
    if found:
        p(f"  {sym}:")
        for nid, fp, name in found[:4]:
            p(f"    id={nid} [{fp}]")
        sym_node_map[sym] = [f[0] for f in found]

# ── Q3: Production callers of routing functions (fan-in) ───────────────────
p("\n=== Q3: PRODUCTION CALLERS (fan-in via imports+calls) ===")
for sym in ROUTING_SYMS:
    if sym not in sym_node_map:
        continue
    callers = set()
    for nid in sym_node_map[sym]:
        for rel in ("imports", "calls"):
            fan_in_key = f"adg:edge:in:{nid}:{rel}"
            src_ids = r.smembers(fan_in_key)
            for src_id in src_ids:
                src = get_node(src_id)
                path = src.get("resolved_path", "")
                if path and not skip(path) and "test" not in path:
                    callers.add(path)
    if callers:
        p(f"  {sym} ({len(callers)} prod callers):")
        for c in sorted(callers):
            p(f"    {c}")

# ── Q4: Who imports heal_policy_types (production) ─────────────────────────
p("\n=== Q4: PRODUCTION IMPORTERS OF heal_policy_types ===")
for nid in file_module_ids.get("heal_policy_types", []):
    fan_in_key = f"adg:edge:in:{nid}:imports"
    src_ids = r.smembers(fan_in_key)
    for sid in src_ids:
        src = get_node(sid)
        path = src.get("resolved_path", "")
        if path and not skip(path) and "test" not in path:
            p(f"  {path}")

# ── Q5: Who imports _ssot_routing / _ssot_types (production) ───────────────
p("\n=== Q5: PRODUCTION IMPORTERS OF _ssot_routing + _ssot_types ===")
for frag in ("_ssot_routing", "_ssot_types"):
    p(f"  [{frag}]:")
    for nid in file_module_ids.get(frag, []):
        fan_in_key = f"adg:edge:in:{nid}:imports"
        for sid in r.smembers(fan_in_key):
            src = get_node(sid)
            path = src.get("resolved_path", "")
            if path and not skip(path) and "test" not in path:
                p(f"    {path}")

# ── Q6: reads_env edges in routing files ───────────────────────────────────
p("\n=== Q6: reads_env IN ROUTING FILES ===")
for frag in ROUTING_FRAGS:
    for nid in file_module_ids.get(frag, []):
        fan_out_key = f"adg:edge:{nid}:reads_env"
        targets = r.smembers(fan_out_key)
        if targets:
            nd = get_node(nid)
            p(f"  {nd.get('resolved_path', '?')}: {len(targets)} reads_env edges")

# ── Q7: HEALING_CONFIDENCE_X/Y importers (production) ──────────────────────
p("\n=== Q7: HEALING_CONFIDENCE_X/Y PRODUCTION IMPORTERS ===")
for sym in ("HEALING_CONFIDENCE_X", "HEALING_CONFIDENCE_Y"):
    importers = set()
    for nid in sym_node_map.get(sym, []):
        for sid in r.smembers(f"adg:edge:in:{nid}:imports"):
            src = get_node(sid)
            path = src.get("resolved_path", "")
            if path and not skip(path) and "test" not in path:
                importers.add(path)
    p(f"  {sym} ({len(importers)} importers): {sorted(importers)}")

# ── Q8: antipattern edges in routing files ─────────────────────────────────
p("\n=== Q8: antipattern EDGES IN ROUTING FILES ===")
for frag in ROUTING_FRAGS:
    for nid in file_module_ids.get(frag, []):
        ap_key = f"adg:edge:{nid}:antipattern"
        targets = r.smembers(ap_key)
        if targets:
            nd = get_node(nid)
            p(f"  {nd.get('resolved_path', '?')}: {len(targets)} antipattern edges")

# ── Q9: dead_import edges in routing files ─────────────────────────────────
p("\n=== Q9: dead_import EDGES IN ROUTING FILES ===")
for frag in ROUTING_FRAGS:
    for nid in file_module_ids.get(frag, []):
        di_key = f"adg:edge:{nid}:dead_import"
        targets = r.smembers(di_key)
        if targets:
            nd = get_node(nid)
            p(f"  {nd.get('resolved_path', '?')}: {len(targets)} dead imports")
            for tid in targets:
                tnd = get_node(tid)
                p(f"    -> {tnd.get('adg_name', '?')}")

# ── Q10: RoutingTier vs HealingTier importers ──────────────────────────────
p("\n=== Q10: RoutingTier vs HealingTier IMPORTERS (prod) ===")
for tier_sym in ("RoutingTier", "HealingTier"):
    importers = set()
    for mk in r.scan_iter("adg:nodes:by_file:*"):
        file_path = mk.replace("adg:nodes:by_file:", "")
        if skip(file_path):
            continue
        for nid in r.smembers(mk):
            nd = get_node(nid)
            if tier_sym in nd.get("adg_name", "") and nd.get("entity_type") == "symbol":
                for sid in r.smembers(f"adg:edge:in:{nid}:imports"):
                    src = get_node(sid)
                    path = src.get("resolved_path", "")
                    if path and not skip(path) and "test" not in path:
                        importers.add(path)
    p(f"  {tier_sym} ({len(importers)} prod importers): {sorted(importers)}")

# ── Q11: Layer violations involving routing files ──────────────────────────
p("\n=== Q11: layer_violation EDGES IN ROUTING FILES ===")
for frag in ROUTING_FRAGS:
    for nid in file_module_ids.get(frag, []):
        lv_key = f"adg:edge:{nid}:layer_violation"
        targets = r.smembers(lv_key)
        if targets:
            nd = get_node(nid)
            p(f"  {nd.get('resolved_path', '?')}: {len(targets)} layer violations")

# ── Q12: New nodes since 0840 snapshot ─────────────────────────────────────
p("\n=== Q12: ADG META (current snapshot) ===")
meta = r.hgetall("adg:meta")
p(f"  timestamp:   {meta.get('timestamp')}")
p(f"  nodes:       {meta.get('node_count')}")
p(f"  edges:       {meta.get('edge_count')}")
p(f"  sqlite:      {meta.get('sqlite_path')}")
p(f"  ingested_at: {meta.get('ingested_at')}")

# ── Write output ────────────────────────────────────────────────────────────
with open("tools/evidence/_adg_redis_routing_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("\nDONE. Written to tools/evidence/_adg_redis_routing_out.txt")
