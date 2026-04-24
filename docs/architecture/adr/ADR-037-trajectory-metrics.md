# ADR-037 — Trajectory Metric Suite

- **Status:** Proposed
- **Date:** 2026-04-23
- **Deciders:** Eval Lab, Safety Officer (L5), Architecture
- **Impact Layers:** L5, L6, apps_eval, L2 (trace emission), v33 §5, §6B
- **Relates to:** ADR-036 (runtime trace-grader), ADR-030 (runtime ADG ingest), ADR-028 (eval SL publisher)

## 1. Context

v33 §6B mentions "Grade trajectories: tool order, retries, budget, execution shape"
in prose. There is no canonical metric set. Google Vertex defines six trajectory
metrics that have become the de-facto industry standard; absent them, our §5
trajectory section is unscorable on comparable benchmarks and we cannot populate
`ExitDecision.trajectory.*`.

## 2. Decision

Adopt the **Vertex trajectory metric suite verbatim** plus the default-always-on
pair Vertex emits for every run.

### 2.1 Default always-on (every run, no reference required)

| Metric | Type | Source |
|---|---|---|
| `latency_ms` | integer | `L6_observability` span aggregate end − ingress stamp |
| `failure` | boolean | terminal class ∈ {FAILURE, ERROR, TIMEOUT} |
| `tool_call_count` | integer | length of tool-call ledger on sealed artifact |
| `retry_count` | integer | number of heal attempts observed in trace |

### 2.2 Reference-based (computed only when a reference trajectory is attached to the request or dataset scenario)

| Metric | Semantics | Range |
|---|---|---|
| `trajectory_exact_match` | predicted == reference: same tool calls, same order | {0, 1} |
| `trajectory_in_order_match` | predicted contains reference in order; extras allowed | {0, 1} |
| `trajectory_any_order_match` | predicted contains reference as a set; order-free; extras allowed | {0, 1} |
| `trajectory_precision` | \|predicted ∩ reference\| / \|predicted\| | [0.0, 1.0] |
| `trajectory_recall` | \|predicted ∩ reference\| / \|reference\| | [0.0, 1.0] |
| `single_tool_use` | for a named tool: is it present in predicted? | {present: bool, tool_name: str} |

These semantics match Vertex *exactly* — see
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-agents.

### 2.3 Predicted-trajectory extraction contract

A predicted trajectory is a list of **normalized tool-call records**:

```
[
  {"tool": "<canonical_tool_name>", "args_hash": "<sha256 of normalized args>"},
  ...
]
```

- `canonical_tool_name` — from the MCP / sovereign-gateway registry, no aliases.
- `args_hash` — sha256 of a JCS-canonicalized JSON of the args, excluding
  volatile fields (timestamps, request_ids, trace_ids). Canonicalization rules
  live with the emitter, not here.
- Two calls are "equivalent" for set/order comparison iff `tool` matches AND
  `args_hash` matches.

### 2.4 Reference trajectory format

Stored under `data/eval/golden/trajectory/<scenario_name>.json`:

```
{
  "scenario": "<human-readable>",
  "schema_version": 1,
  "reference": [ {"tool": "...", "args_hash": "..."}, ... ],
  "comparison_policy": {
    "args_match": "hash" | "regex" | "semantic",
    "semantic_matcher_ref": null
  }
}
```

`semantic` matching is out of scope for this ADR (tracked as follow-up).

## 3. Projection into `ExitDecision.trajectory`

The emitter populates:

- Always: `failure`, `latency_ms`, `tool_call_count`, `retry_count`.
- When reference present: `exact_match`, `in_order_match`, `any_order_match`,
  `precision`, `recall`, `single_tool_use`.
- When reference absent: the six reference-based fields are `null` (schema
  allows null).

## 4. Consequences

- **Positive:** parity with Vertex; `scorecard_engine.py` gets typed trajectory
  inputs; regression suites can track `exact_match` pass rate.
- **Negative:** requires scenarios to ship reference trajectories where
  trajectory correctness matters. Bootstrap cost in `data/eval/golden/`.
- **Risk:** over-reliance on exact_match will under-reward legitimate variation.
  Mitigated by treating `any_order_match` + `recall ≥ 0.9` as the promotion gate,
  with `exact_match` reserved for strict regression suites.

## 5. Alternatives Considered

- **Invent bespoke metrics.** Rejected — loses comparability with public
  benchmarks and Vertex docs.
- **Anthropic-style "transcript scoring" only.** Rejected — covered by
  ADR-036 trace-grader `trajectory_shape` dim; not a replacement for quantitative
  set/order metrics.

## 6. Open Items (tracked to follow-up plans)

- Code execution plan: emitter wiring from L2 trace into
  `ExitDecision.trajectory` (blocked on this ADR).
- Canonical tool-call normalization spec (args_hash rules) — separate doc.
- `data/eval/golden/trajectory/` initial scenario seed (~10 scenarios).
- CI gate: reference trajectories must pass schema validation.
