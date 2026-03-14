import json

import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
meta = r.hgetall("adg:meta")
snapshot = r.get("adg:snapshot")
s = json.loads(snapshot)

by_layer = s.get("by_layer", {})
layer_counts = {}
for k, v in by_layer.items():
    layer_counts[k] = v if isinstance(v, int) else len(v)

prod_layers = [
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L_APP",
    "L_OPS",
    "L_SHARED",
    "L_TOOLS",
    "L_RUNTIME",
    "L_SL",
    "L_PG",
]
prod_total = sum(layer_counts.get(layer, 0) for layer in prod_layers)
test_total = layer_counts.get("L_TEST", 0)
total_nodes = prod_total + test_total

counts = s.get("counts", {})
edge_counts = counts.get("by_edge_type", {})

result = {
    "meta": meta,
    "layer_counts": layer_counts,
    "edge_type_counts": edge_counts,
    "total_nodes": total_nodes,
    "prod_nodes": prod_total,
    "test_nodes": test_total,
}

print(json.dumps(result, indent=2))
