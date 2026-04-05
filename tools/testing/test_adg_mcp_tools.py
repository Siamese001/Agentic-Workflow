#!/usr/bin/env python3
"""Test all 17 ADG Redis MCP tools"""
import sys

sys.path.insert(0, r'C:\Git\Agentic-Workflow')

from tools.adg.adg_mcp_server import (
    adg_assert_fresh,
    adg_meta,
    adg_nodes_by_layer,
    adg_snapshot,
    adg_status,
    adg_violations,
    redis_get,
    redis_hgetall,
    redis_lrange,
    redis_scan,
    redis_smembers,
    redis_ttl,
    redis_type,
)

print("=" * 60)
print("ADG REDIS MCP - 17 TOOL VERIFICATION")
print("=" * 60)

# Tier 1 - ADG-specific tools
print("\n--- Tier 1: ADG-Specific Tools ---")

# Test 1: adg_status
print("\n[1/17] adg_status()")
try:
    result = adg_status()
    if result.get('status') == 'ok':
        data = result.get('data', {})
        print(f"  ✅ OK - Nodes: {data.get('node_count')}, Edges: {data.get('edge_count')}, Fresh: {data.get('is_fresh')}")
    else:
        print(f"  ❌ Error: {result.get('message')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 2: adg_meta
print("\n[2/17] adg_meta()")
try:
    result = adg_meta()
    if 'error' not in result:
        print(f"  ✅ OK - Timestamp: {result.get('timestamp', 'N/A')[:20]}...")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 3: adg_snapshot
print("\n[3/17] adg_snapshot()")
try:
    result = adg_snapshot()
    if 'error' not in result:
        data = result.get('data', {})
        layers = data.get('layer_counts', {})
        print(f"  ✅ OK - Layers: {len(layers)} layers in snapshot")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 4: adg_assert_fresh
print("\n[4/17] adg_assert_fresh()")
try:
    result = adg_assert_fresh()
    if 'error' not in result:
        print(f"  ✅ OK - Fresh: {result.get('is_fresh')}, Verdict: {result.get('verdict', 'N/A')[:40]}...")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 5: redis_scan
print("\n[5/17] redis_scan()")
try:
    result = redis_scan(pattern="adg:*", max_keys=10)
    if 'error' not in result:
        print(f"  ✅ OK - Found {result.get('matched_keys')} keys")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 6: redis_type on adg:status
print("\n[6/17] redis_type('adg:status')")
try:
    result = redis_type("adg:status")
    if 'error' not in result:
        print(f"  ✅ OK - Type: {result.get('type')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 7: redis_get on adg:status
print("\n[7/17] redis_get('adg:status')")
try:
    result = redis_get("adg:status")
    if 'error' not in result:
        print(f"  ✅ OK - Exists: {result.get('exists')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 8: redis_hgetall on adg:meta
print("\n[8/17] redis_hgetall('adg:meta')")
try:
    result = redis_hgetall("adg:meta")
    if 'error' not in result:
        print(f"  ✅ OK - Fields: {result.get('field_count')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 9: adg_nodes_by_layer
print("\n[9/17] adg_nodes_by_layer('L0')")
try:
    result = adg_nodes_by_layer("L0", limit=5)
    if 'error' not in result:
        print(f"  ✅ OK - Total L0 nodes: {result.get('total_count')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 10: adg_violations
print("\n[10/17] adg_violations()")
try:
    result = adg_violations()
    if 'error' not in result:
        print(f"  ✅ OK - Violations: {result.get('count')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 11: redis_smembers on layer set
print("\n[11/17] redis_smembers('adg:nodes:by_layer:L1')")
try:
    result = redis_smembers("adg:nodes:by_layer:L1", limit=5)
    if 'error' not in result:
        print(f"  ✅ OK - Total L1 nodes: {result.get('total_count')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 12: redis_lrange on violations
print("\n[12/17] redis_lrange('adg:violations')")
try:
    result = redis_lrange("adg:violations", start=0, stop=5)
    if 'error' not in result:
        print(f"  ✅ OK - Total violations: {result.get('total_length')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 13: redis_ttl on adg:status
print("\n[13/17] redis_ttl('adg:status')")
try:
    result = redis_ttl("adg:status")
    if 'error' not in result:
        print(f"  ✅ OK - TTL: {result.get('ttl_seconds')} (persistent={result.get('persistent')})")
    else:
        print(f"  ❌ Error: {result.get('error')}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

print("\n" + "=" * 60)
print("SUMMARY: Tests 1-13 executed")
print("Note: Tests 14-17 require specific node/edge IDs from above results")
print("=" * 60)
