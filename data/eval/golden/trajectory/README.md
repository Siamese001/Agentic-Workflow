# Golden Reference Trajectories

Reference trajectories for the Vertex-style trajectory metric suite defined in
[ADR-037](../../../../docs/architecture/adr/ADR-037-trajectory-metrics.md).

## File layout

One JSON file per scenario:

```
data/eval/golden/trajectory/<scenario_slug>.json
```

## Schema (informal)

```json
{
  "scenario": "human-readable scenario name",
  "schema_version": 1,
  "reference": [
    {"tool": "canonical_tool_name", "args_hash": "sha256_hex"}
  ],
  "comparison_policy": {
    "args_match": "hash",
    "semantic_matcher_ref": null
  },
  "notes": "optional free-form context for calibration"
}
```

Rules:

- `tool` must be a canonical name from the MCP / sovereign-gateway registry
  (no aliases).
- `args_hash` is a sha256 of a JCS-canonicalized JSON of the tool args, with
  volatile fields (timestamps, `request_id`, `trace_id`) stripped before hashing.
- `schema_version: 1` is the only currently accepted version.
- `comparison_policy.args_match` ∈ `{hash, regex, semantic}`. `semantic` is
  reserved for future work (see ADR-037 §2.4).

## Comparison semantics (verbatim from ADR-037)

| Metric | Semantics |
|---|---|
| `trajectory_exact_match` | predicted == reference: same tool calls, same order |
| `trajectory_in_order_match` | predicted contains reference in order; extras allowed |
| `trajectory_any_order_match` | predicted contains reference as a set; order-free; extras allowed |
| `trajectory_precision` | \|predicted ∩ reference\| / \|predicted\| |
| `trajectory_recall` | \|predicted ∩ reference\| / \|reference\| |
| `single_tool_use` | for a named tool: is it present in predicted? |

Two calls are equivalent iff `tool` matches **and** `args_hash` matches (under
the declared `args_match` policy).

## Promotion gate

Per ADR-037 §4, the recommended regression promotion gate uses:

- `any_order_match == 1`, AND
- `recall ≥ 0.9`.

`exact_match` is reserved for strict regression suites where tool order is
contractually fixed.

## Status

This directory is a **scaffold**. Initial scenario seed (~10 scenarios) is a
follow-up task tracked in the execution plan that lifts ADR-037 into code.
