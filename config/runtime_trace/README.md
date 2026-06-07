# Runtime Trace Contracts

Registry for **runtime trace contracts** consumed by the runtime-trace proof
gate (`ops_scripts/ci/check_runtime_trace_contract.py`).

## Distinction from `config/contracts/`

| Registry | Validates | Consumer |
|---|---|---|
| `config/contracts/` (ADR-039) | Agent **output** shape (text/JSON the agent produces) | Output-Contract Validator at v33 §5 EXIT EVAL |
| `config/runtime_trace/contracts/` (this dir) | OTEL **span DAG** emitted at runtime | Runtime-trace proof gate |

These registries are intentionally separate. Output validation answers *"is the
agent's answer well-formed?"*. Runtime trace validation answers *"did the
system actually walk the expected path?"*.

## Layout

```
config/runtime_trace/
  README.md                    # this file
  contracts/
    canary_<route>_<vN>.yaml   # one contract per canary route
```

## Contract Schema (canary_v1)

Each contract is a YAML file with this shape:

```yaml
contract_id: canary.<route>.v1     # unique identifier
version: 1                          # schema version (currently 1)
description: |                      # human-readable purpose
  One-paragraph description of what this canary proves.

required_spans:                     # spans that MUST appear in the trace
  - name: <span.name>               # OTEL span name (dot-separated)
    layer: <L0..L6>                 # architectural layer
    parent: <span.name> | null      # parent span (null = root)
    attributes:                     # required attribute keys
      - trace_id
      - route_id
    optional_attributes: []         # attributes that may appear

required_edges:                     # parent/child or semantic edges that MUST exist
  - from: <span.name>
    to: <span.name>
    kind: parent_child | writes_to | flows_to | emits_side_effect

forbidden:                          # invariants the trace MUST NOT violate
  - direct_l4_write_outside_uwg     # no L4 write spans whose parent is not uwg.commit
  - cross_layer_skip                # no span at layer L_n whose parent is L_(n-2) or lower
  - swallowed_exception             # no span with status=error followed by status=ok with no recover.* span

invariant_attributes:               # attributes that MUST be consistent across all spans
  - trace_id                        # same value in every span
```

## Resolution

A canary runner declares `runtime_trace_contract_ref: "canary.<route>.v1"`,
which resolves to `config/runtime_trace/contracts/canary_<route>_v1.yaml`.

Missing refs cause the runtime-trace proof gate to fail with violation
`runtime_trace_contract_unresolved:<contract_id>`.

## Status

Scaffold + initial `canary_lic_v1.yaml`. Additional canary contracts are
added per route as they enter the proof gate.

## See Also

- ADR-039 (output contracts) — sibling registry, distinct concern
- `agentic_core/L6_observability/runtime_trace/contract.py` — Python loader/validator
- `ops_scripts/ci/check_runtime_trace_contract.py` — CI gate consumer
- `scripts/proof/run_runtime_trace_proof.py` — canary runner
- Plan: `docs/archive/windsurf/legacy-tree/plans/assurance-p1-gates-ab4758.md` (W1.1)
