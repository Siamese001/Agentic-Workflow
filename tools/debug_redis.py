#!/usr/bin/env python3
"""Debug Redis key structure"""
import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

print('=== Redis Key Analysis ===')

# Get a sample of keys
keys = r.scan(match='*', count=100)[1]
print(f'\nSample keys (first 20):')
for k in keys[:20]:
    print(f'  {k}')

# Check adg:meta specifically
print(f'\nadg:meta exists: {r.exists("adg:meta")}')
print(f'adg:meta type: {r.type("adg:meta")}')
if r.exists('adg:meta'):
    print(f'adg:meta fields: {r.hlen("adg:meta")}')
    print(f'adg:meta content: {r.hgetall("adg:meta")}')

# Check adg:status
print(f'\nadg:status exists: {r.exists("adg:status")}')
print(f'adg:status type: {r.type("adg:status")}')
if r.exists('adg:status'):
    raw = r.get('adg:status')
    print(f'adg:status content: {raw[:200]}...' if raw and len(raw) > 200 else f'adg:status content: {raw}')

# Check for pattern variations
adg_keys = r.scan(match='adg:*', count=1000)[1]
print(f'\nTotal adg:* keys found: {len(adg_keys)}')

# Group by prefix
prefixes = {}
for k in adg_keys:
    parts = k.split(':')
    prefix = ':'.join(parts[:2]) if len(parts) >= 2 else parts[0]
    prefixes[prefix] = prefixes.get(prefix, 0) + 1

print('\nKey prefixes:')
for p, c in sorted(prefixes.items(), key=lambda x: -x[1])[:15]:
    print(f'  {p}: {c}')
