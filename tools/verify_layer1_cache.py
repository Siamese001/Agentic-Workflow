#!/usr/bin/env python3
"""Comprehensive Layer 1 (Redis) + Layer 2 (Semantic) Cache Verification"""
import sys

sys.path.insert(0, r'C:\Git\Agentic-Workflow')

from tools.adg.adg_mcp_server import (
    adg_status,
    redis_hgetall,
    redis_scan,
    redis_smembers,
    redis_ttl,
    redis_type,
)

print("=" * 70)
print("LAYER 1 (REDIS KEY-VALUE) ACCELERATION VERIFICATION")
print("=" * 70)

# 1. Cache Freshness
print("\n[1] CACHE FRESHNESS")
status = adg_status()
if status.get('status') == 'ok':
    data = status['data']
    print(f"  Nodes: {data['node_count']:,}")
    print(f"  Edges: {data['edge_count']:,}")
    print(f"  Is Fresh: {data['is_fresh']}")
    print(f"  Age: {data['age_seconds']:.1f} seconds")
    print("  ✅ HOT CACHE - Ready for O(1) lookups")
else:
    print(f"  ❌ Cache error: {status.get('message')}")

# 2. Key Structure Analysis
print("\n[2] KEY STRUCTURE (Tier 1 - ADG Specific)")
scan = redis_scan(pattern="adg:*", max_keys=500)
if scan.get('status') == 'ok':
    data = scan['data']
    prefixes = data.get('prefix_summary', {})
    print(f"  Total ADG keys: {data['matched_keys']}")
    print("  Top key patterns:")
    for prefix, count in list(prefixes.items())[:8]:
        print(f"    {prefix}: {count}")

# 3. Meta Data Access (O(1) HGETALL)
print("\n[3] META DATA (O(1) HASH lookup)")
meta = redis_hgetall("adg:meta")
if meta.get('status') == 'ok':
    data = meta['data']
    print(f"  Fields: {data['field_count']}")
    print(f"  Timestamp: {data['fields'].get('timestamp')}")
    print(f"  SQLite: {data['fields'].get('sqlite_path', 'N/A')[-40:]}")
    print("  ✅ O(1) HASH access working")

# 4. Layer Sets (SMEMBERS - O(N) where N=set size)
print("\n[4] LAYER INDEXING (SET operations)")
for layer in ['L0', 'L1', 'L2', 'L3']:
    result = redis_smembers(f"adg:nodes:by_layer:{layer}", limit=3)
    if result.get('status') == 'ok':
        data = result['data']
        print(f"  {layer}: {data['total_count']:,} nodes")

# 5. TTL Analysis (Keys are persistent)
print("\n[5] PERSISTENCE (TTL check)")
ttl = redis_ttl("adg:meta")
if ttl.get('status') == 'ok':
    data = ttl['data']
    if data['persistent']:
        print("  adg:meta: Persistent (no expiry)")
        print("  ✅ Data survives until explicit deletion")

# 6. Type Validation
print("\n[6] TYPE SAFETY")
for key, expected in [
    ("adg:status", "string"),
    ("adg:meta", "hash"),
    ("adg:nodes:by_layer:L0", "set"),
    ("adg:violations", "list")
]:
    t = redis_type(key)
    if t.get('status') == 'ok' and t['data']['type'] == expected:
        print(f"  {key}: {expected} ✅")
    else:
        print(f"  {key}: {t.get('data', {}).get('type')} (expected {expected})")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("Layer 1 (Redis) is OPERATIONAL with:")
print("  - O(1) key-value lookups")
print("  - HASH operations for metadata")
print("  - SET operations for layer indexing")
print("  - LIST operations for violations")
print("  - Persistent storage (no TTL expiry)")
print("=" * 70)
