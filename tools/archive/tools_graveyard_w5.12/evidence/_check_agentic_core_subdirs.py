import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

subdirs = [
    "agentic_core/knowledge",
    "agentic_core/mixins",
    "agentic_core/patterns",
    "agentic_core/prompt_governance",
    "agentic_core/runtime",
    "agentic_core/seams",
    "agentic_core/utils",
    "agentic_core/base_agents",
    "agentic_core/cache",
    "agentic_core/config",
    "agentic_core/embeddings",
    "agentic_core/enforcement",
    "agentic_core/evaluation",
    "agentic_core/interfaces",
]

print(f"{'Subdir':<40} {'L_UNKNOWN':>10} {'Correct Layer':>15} {'Total':>7}")
print("-" * 76)

for subdir in subdirs:
    # Scan for all by_file keys matching this subdir
    cursor = 0
    layer_counts = {}
    total = 0
    while True:
        cursor, keys = r.scan(cursor, match=f'adg:nodes:by_file:{subdir}*', count=500)
        for k in keys:
            node_ids = r.smembers(k)
            for nid in node_ids:
                node = r.hgetall(f'adg:node:{nid}')
                layer = node.get('layer', 'MISSING')
                layer_counts[layer] = layer_counts.get(layer, 0) + 1
                total += 1
        if cursor == 0:
            break

    unknown = layer_counts.get('L_UNKNOWN', 0)
    correct = {k: v for k, v in layer_counts.items() if k != 'L_UNKNOWN'}
    correct_str = ', '.join(f'{k}:{v}' for k, v in sorted(correct.items(), key=lambda x: -x[1]))
    status = "✓" if unknown == 0 else "✗ HAS L_UNKNOWN"
    print(f"{subdir:<40} {unknown:>10} {correct_str:>30} {total:>7}  {status}")
