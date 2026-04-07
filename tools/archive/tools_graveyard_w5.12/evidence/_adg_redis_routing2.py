"""Redis hot-cache targeted follow-up queries for routing consolidation."""

import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def get_node(nid):
    return r.hgetall("adg:node:" + str(nid))


def skip(path):
    return any(x in (path or "") for x in ("archive", "backup", ".backup", "test"))


# Antipattern details
print("=== ANTIPATTERN EDGE DETAILS ===")
checks = [
    ("614", "healing_tier_router"),
    ("80", "_ssot_routing"),
    ("79", "_ssot_reporting"),
    ("2000", "SovereignBaseAgent"),
]
for nid_str, label in checks:
    targets = r.smembers("adg:edge:" + nid_str + ":antipattern")
    if targets:
        print(f"  [{label}] id={nid_str}: {len(targets)} antipattern targets")
        for tid in targets:
            nd = get_node(tid)
            print(f"    -> id={tid} name={nd.get('adg_name', '?')[:80]}")

# reads_env details
print("\n=== reads_env DETAILS ===")
for nid_str, label in [
    ("81", "_ssot_types"),
    ("80", "_ssot_routing"),
    ("2000", "SovereignBaseAgent"),
    ("2503", "decorators_util"),
]:
    targets = r.smembers("adg:edge:" + nid_str + ":reads_env")
    print(f"  [{label}] {len(targets)} reads_env edges:")
    for tid in targets:
        nd = get_node(tid)
        print(f"    -> id={tid} name={nd.get('adg_name', '?')[:80]}")

# compute_routing_decision location and callers
print("\n=== compute_routing_decision CALLERS ===")
for mk in r.scan_iter("adg:nodes:by_file:*execute_ssot*"):
    fp = mk.replace("adg:nodes:by_file:", "")
    if skip(fp) or "_patch" in fp:
        continue
    for nid in r.smembers(mk):
        nd = get_node(nid)
        if "compute_routing_decision" in nd.get("adg_name", ""):
            print(f"  defined: id={nid} layer={nd.get('layer')} path={fp}")
            callers = r.smembers("adg:edge:in:" + nid + ":calls")
            callers = callers | r.smembers("adg:edge:in:" + nid + ":imports")
            for sid in callers:
                src = get_node(sid)
                spath = src.get("resolved_path", "")
                if spath and not skip(spath):
                    print(f"    caller: {spath}")

# Also check _ssot_routing for compute_routing_decision
print("\n=== compute_routing_decision in _ssot_routing ===")
for mk in r.scan_iter("adg:nodes:by_file:*_ssot_routing*"):
    fp = mk.replace("adg:nodes:by_file:", "")
    if skip(fp):
        continue
    for nid in r.smembers(mk):
        nd = get_node(nid)
        if "compute_routing_decision" in nd.get("adg_name", ""):
            print(f"  found: id={nid} name={nd.get('adg_name')}")

# _ssot_routing imports HEALING_CONFIDENCE_X/Y
print("\n=== _ssot_routing IMPORTS of HEALING_CONFIDENCE constants ===")
for sym_id, sym_name in [("13926", "HEALING_CONFIDENCE_X"), ("13927", "HEALING_CONFIDENCE_Y")]:
    fan_in = r.smembers("adg:edge:in:" + sym_id + ":imports")
    if fan_in:
        print(f"  {sym_name} importers:")
        for sid in fan_in:
            src = get_node(sid)
            path = src.get("resolved_path", "")
            if path and not skip(path):
                print(f"    {path}")

# execute_ssot imports
print("\n=== execute_ssot.py routing imports ===")
for mk in r.scan_iter("adg:nodes:by_file:*execute_ssot*"):
    fp = mk.replace("adg:nodes:by_file:", "")
    if skip(fp) or "_patch" in fp:
        continue
    for nid in r.smembers(mk):
        nd = get_node(nid)
        if nd.get("entity_type") != "module":
            continue
        fan_out = r.smembers("adg:edge:" + nid + ":imports")
        for tid in fan_out:
            tnd = get_node(tid)
            name = tnd.get("adg_name", "")
            if any(
                x in name
                for x in (
                    "HEALING_CONF",
                    "SCORE_THRESHOLD",
                    "route_healing",
                    "compute_routing",
                    "heal_policy",
                )
            ):
                print(f"  imports: {name[:70]} from {tnd.get('resolved_path', '?')}")

# _ssot_routing.py fan-out imports
print("\n=== _ssot_routing.py ALL imports (routing-related) ===")
nd80 = get_node("80")
fan_out = r.smembers("adg:edge:80:imports")
print(f"  _ssot_routing.py imports {len(fan_out)} symbols total")
for tid in fan_out:
    tnd = get_node(tid)
    name = tnd.get("adg_name", "")
    if any(
        x in name
        for x in ("HEALING", "SCORE", "route_", "RoutingTier", "HealingTier", "ConfidenceScore", "ssot_types")
    ):
        print(f"  -> {name[:70]} from {tnd.get('resolved_path', '?')}")

print("\nDONE.")
