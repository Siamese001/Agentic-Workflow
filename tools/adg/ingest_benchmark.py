"""
ADG Redis Ingest Performance Analysis
RCA: Command Volume Explosion and Throughput Optimization
"""
import json
import sqlite3
import time

import redis

# Test configurations
BATCH_SIZE = 5000
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True,
    'socket_keepalive': True,
    'socket_connect_timeout': 5,
    'socket_timeout': 30,
    'health_check_interval': 30,
    'max_connections': 20,
}

def profile_ingest_stages():
    """
    Profile each stage of the ingest pipeline:
    1. SQLite fetch/serialization
    2. Python dict construction
    3. Redis pipeline buffer fill
    4. Network round-trip (execute)
    5. Redis server-side processing
    """
    r = redis.Redis(**REDIS_CONFIG)

    # Connect to ADG SQLite
    conn = sqlite3.connect(r'C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04022026_0905.sqlite')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get sample data
    cur.execute("SELECT * FROM nodes LIMIT 1000")
    rows = cur.fetchall()

    print(f"Profiling {len(rows)} nodes...")

    # Stage 1: SQLite fetch + dict conversion
    t0 = time.time()
    dicts = []
    for row in rows:
        d = dict(row)
        safe = {k: str(v) for k, v in d.items() if v is not None and str(v) != ""}
        dicts.append((d.get('id'), safe))
    t1 = time.time()
    print(f"  Stage 1 (SQLite→dict): {t1-t0:.3f}s")

    # Stage 2: Pipeline construction with hmset (original fast path)
    pipe = r.pipeline(transaction=False)
    t0 = time.time()
    for node_id, safe in dicts:
        pipe.hmset(f"adg:node:{node_id}", safe)
    t1 = time.time()
    print(f"  Stage 2 (pipeline fill hmset): {t1-t0:.3f}s")

    # Stage 3: Execute
    t0 = time.time()
    pipe.execute()
    t1 = time.time()
    print(f"  Stage 3 (execute 1000 hmset): {t1-t0:.3f}s")

    # Cleanup
    pipe = r.pipeline(transaction=False)
    for node_id, _ in dicts:
        pipe.delete(f"adg:node:{node_id}")
    pipe.execute()

    conn.close()

    return {
        'serialization': t1-t0,
        'total_per_1k': (t1-t0) * 3  # rough extrapolation
    }

def compare_write_layouts():
    """
    Compare different write layouts:
    1. hmset (deprecated, fast) - one command, multi-field hash
    2. hset per-field (slow) - N commands per entity
    3. packed JSON (one set) - one command, packed blob
    4. hset mapping= (modern, needs Redis 4.0+)
    """
    r = redis.Redis(**REDIS_CONFIG)

    sample_data = {
        'id': '12345',
        'adg_name': 'test::module',
        'entity_type': 'module',
        'layer': 'L2',
        'identity_kind': 'precise',
        'confidence': '0.95',
        'resolved_path': 'agentic_core/test.py',
        'precision_type': 'full',
    }

    results = {}

    # Test 1: hmset (deprecated but fast)
    key1 = "test:layout:hmset"
    t0 = time.time()
    pipe = r.pipeline(transaction=False)
    for i in range(1000):
        pipe.hmset(f"{key1}:{i}", sample_data)
    pipe.execute()
    t1 = time.time()
    results['hmset'] = {'time': t1-t0, 'commands': 1000}

    # Cleanup
    pipe = r.pipeline(transaction=False)
    for i in range(1000):
        pipe.delete(f"{key1}:{i}")
    pipe.execute()

    # Test 2: hset per-field (what caused the slowdown)
    key2 = "test:layout:hset-per-field"
    t0 = time.time()
    pipe = r.pipeline(transaction=False)
    for i in range(1000):
        for k, v in sample_data.items():
            pipe.hset(f"{key2}:{i}", k, v)
    pipe.execute()
    t1 = time.time()
    results['hset-per-field'] = {'time': t1-t0, 'commands': 1000 * len(sample_data)}

    # Cleanup
    pipe = r.pipeline(transaction=False)
    for i in range(1000):
        pipe.delete(f"{key2}:{i}")
    pipe.execute()

    # Test 3: packed JSON
    key3 = "test:layout:json"
    json_blob = json.dumps(sample_data, sort_keys=True)
    t0 = time.time()
    pipe = r.pipeline(transaction=False)
    for i in range(1000):
        pipe.set(f"{key3}:{i}", json_blob)
    pipe.execute()
    t1 = time.time()
    results['json-packed'] = {'time': t1-t0, 'commands': 1000}

    # Cleanup
    pipe = r.pipeline(transaction=False)
    for i in range(1000):
        pipe.delete(f"{key3}:{i}")
    pipe.execute()

    # Print results
    print("\n=== Write Layout Comparison (1000 entities) ===")
    baseline = results['hmset']['time']
    for name, data in results.items():
        ratio = data['time'] / baseline
        print(f"{name:20s}: {data['time']:.3f}s ({ratio:.1f}x) - {data['commands']} commands")

    return results

def estimate_full_ingest_time(layout_results, node_count=188713, edge_count=738603):
    """
    Estimate full ingest time based on benchmark results
    """
    print("\n=== Full Ingest Estimates ===")

    for name, data in layout_results.items():
        time_per_1k = data['time']
        total_entities = node_count + edge_count
        estimated_time = (total_entities / 1000) * time_per_1k
        print(f"{name:20s}: ~{estimated_time:.1f}s for {total_entities:,} entities")

if __name__ == "__main__":
    print("=" * 60)
    print("ADG Redis Ingest Performance Analysis")
    print("=" * 60)

    # Profile stages
    print("\n--- Stage Profiling ---")
    profile_ingest_stages()

    # Compare layouts
    results = compare_write_layouts()

    # Estimate full ingest
    estimate_full_ingest_time(results)

    print("\n" + "=" * 60)
