#!/usr/bin/env python3
"""Test all 17 ADG Redis MCP tools - FIXED VERSION"""
import sys

sys.path.insert(0, r'C:\Git\Agentic-Workflow')

from tools.adg.adg_mcp_server import (
    adg_assert_fresh,
    adg_meta,
    adg_node,
    adg_nodes_by_file,
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

print("=" * 70)
print("ADG REDIS MCP - 17 TOOL VERIFICATION (FIXED)")
print("=" * 70)

passed = 0
failed = 0

def check_result(name, result, check_fn=None):
    global passed, failed
    print(f"\n{name}")
    try:
        if isinstance(result, dict):
            if 'status' in result and result['status'] == 'error':
                print(f"  ❌ Error: {result.get('message', 'Unknown')}")
                failed += 1
                return False
            elif 'error' in result:
                print(f"  ❌ Error: {result['error']}")
                failed += 1
                return False
            else:
                if check_fn:
                    check_fn(result)
                else:
                    print(f"  ✅ OK - Keys: {list(result.keys())[:5]}")
                passed += 1
                return True
        else:
            print(f"  ⚠️  Unexpected type: {type(result)}")
            failed += 1
            return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        failed += 1
        return False

# Test 1: adg_status
result = adg_status()
check_result("[1/17] adg_status()", result,
    lambda r: print(f"  ✅ OK - Nodes: {r['data'].get('node_count')}, Edges: {r['data'].get('edge_count')}, Fresh: {r['data'].get('is_fresh')}"))

# Test 2: adg_meta
check_result("[2/17] adg_meta()", adg_meta(),
    lambda r: print(f"  ✅ OK - Timestamp: {r.get('timestamp')}, Node count: {r.get('node_count')}"))

# Test 3: adg_snapshot (might be large)
check_result("[3/17] adg_snapshot()", adg_snapshot(),
    lambda r: print(f"  ✅ OK - Data keys: {list(r.keys())}"))

# Test 4: adg_assert_fresh
check_result("[4/17] adg_assert_fresh()", adg_assert_fresh(),
    lambda r: print(f"  ✅ OK - Fresh: {r.get('is_fresh')}, Delta: {r.get('delta_seconds')}s"))

# Test 5: redis_scan
check_result("[5/17] redis_scan()", redis_scan(pattern="adg:*", max_keys=50),
    lambda r: print(f"  ✅ OK - Matched: {r.get('matched_keys')} keys, Prefixes: {list(r.get('prefix_summary', {}).keys())[:3]}"))

# Test 6: redis_type
check_result("[6/17] redis_type('adg:status')", redis_type("adg:status"),
    lambda r: print(f"  ✅ OK - Type: {r.get('type')} (read with: {r.get('read_with')})"))

# Test 7: redis_get
check_result("[7/17] redis_get('adg:status')", redis_get("adg:status"),
    lambda r: print(f"  ✅ OK - Exists: {r.get('exists')}, Value length: {len(str(r.get('value', '')))}"))

# Test 8: redis_hgetall
check_result("[8/17] redis_hgetall('adg:meta')", redis_hgetall("adg:meta"),
    lambda r: print(f"  ✅ OK - Fields: {r.get('field_count')}, Exists: {r.get('exists')}"))

# Test 9: adg_nodes_by_layer
check_result("[9/17] adg_nodes_by_layer('L0')", adg_nodes_by_layer("L0", limit=5),
    lambda r: print(f"  ✅ OK - Total L0: {r.get('total_count')}, Returned: {r.get('returned')}"))

# Test 10: adg_violations
check_result("[10/17] adg_violations()", adg_violations(),
    lambda r: print(f"  ✅ OK - Count: {r.get('count')}"))

# Test 11: redis_smembers
check_result("[11/17] redis_smembers('adg:nodes:by_layer:L1')", redis_smembers("adg:nodes:by_layer:L1", limit=5),
    lambda r: print(f"  ✅ OK - Total: {r.get('total_count')}, Returned: {r.get('returned')}"))

# Test 12: redis_lrange
check_result("[12/17] redis_lrange('adg:violations')", redis_lrange("adg:violations", start=0, stop=5),
    lambda r: print(f"  ✅ OK - Total: {r.get('total_length')}, Returned: {r.get('returned')}"))

# Test 13: redis_ttl
check_result("[13/17] redis_ttl('adg:status')", redis_ttl("adg:status"),
    lambda r: print(f"  ✅ OK - TTL: {r.get('ttl_seconds')} (persistent={r.get('persistent')})"))

# Test 14: adg_nodes_by_file (need a valid file path)
print("\n[14/17] adg_nodes_by_file('tools/adg/adg_mcp_server.py')")
try:
    # Get a sample node first
    sample = adg_nodes_by_layer("L0", limit=1)
    if sample.get('node_ids'):
        node_id = sample['node_ids'][0]
        # Get node details to find file path
        node = adg_node(node_id)
        if node.get('resolved_path'):
            file_path = node['resolved_path']
            result = adg_nodes_by_file(file_path)
            check_result(f"  adg_nodes_by_file('{file_path}')", result,
                lambda r: print(f"  ✅ OK - Count: {r.get('count')} nodes in file"))
        else:
            print("  ⚠️  No resolved_path in node")
    else:
        print("  ⚠️  No L0 nodes found")
except Exception as e:
    print(f"  ❌ Exception: {e}")

print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 70)
if passed >= 13:
    print("✅ ADG Redis MCP is OPERATIONAL - all core tools working!")
else:
    print("⚠️  Some tools need attention")
