# SC/AP Check Definitions Reference

> ADR: [ADR-0043](../architecture/adr/adr-0043-structural-agentic-checks.md)  
> Implementation: `tools/generate/validation/gates.py`  
> Config: `artifacts/adg/sc_ap_config.json`

---

## Violation Classes

| Class | Code | Description |
|-------|------|-------------|
| `hygiene` | Existing P0-P3 | AST-level antipattern detection (broad exceptions, silent swallows, etc.) |
| `structural_conformance` | SC-1..SC-8 | Architectural contract enforcement via graph queries |
| `agentic_antipattern` | AP-1..AP-17 | Agentic system anti-pattern detection via graph queries |

---

## Structural Conformance Checks (SC)

### SC-1: Gravity Import / Illegal Layer Reach
- **Severity**: P0
- **Query**: Finds `imports`/`reads_from`/`controls_flow`/`flows_to` edges that cross gravity-forbidden layer boundaries
- **Forbidden pairs**: L0→{L1,L2,L3,L6}, L1→{L2,L3,L6}, L2→{L0,L1,L6}, L6→{L2}
- **Evidence**: Source file, line number, source layer → destination layer

### SC-2: L2 Execution Lifecycle Conformance
- **Severity**: P0
- **Query**: L2 nodes that lack the required lifecycle edge set: `enters_sandbox`, `stamps_work_contract`, `validates_uwg_intent`, `orchestrates_healing`, `packages_execution_trace`
- **Evidence**: L2 module name, missing lifecycle edges

### SC-3: UWG-Only Durable Write Conformance
- **Severity**: P0
- **Query**: Non-L2 nodes with `writes_to`/`writes_through` edges that lack `validates_uwg_intent` or `commits_mutation_durable` guard edges
- **Evidence**: Writing node, layer, target

### SC-4: Capability/Tool/Provider Choke-Point
- **Severity**: P0
- **Query**: Nodes with `invokes_provider` edges that lack `enters_sandbox`, `issues_capability_token`, or `checks_capability_set`
- **Evidence**: Provider-invoking node, missing gates

### SC-5: Agentic Spine Completeness
- **Severity**: P1
- **Query**: Checks that the graph contains at least one edge of each spine type: `pulls_context`, `generates_prompt`, `consumes_prompt`, `packages_execution_trace`
- **Evidence**: Missing spine edge types

### SC-6: L0/L1/L6 Role Purity
- **Severity**: P1
- **Query**: L0/L1/L6 nodes with edges that violate role boundaries (e.g., L0 with `invokes_provider`, L1 with `writes_to`, L6 with `orchestrates_healing`)
- **Evidence**: Node, layer, forbidden edge type

### SC-7: Grounding Contract / C0-PA Separation
- **Severity**: P1
- **Query**: Nodes with `invokes_provider` that lack `applies_guardrail` companion edges
- **Evidence**: Provider-invoking node without guardrail

### SC-8: Trace/Replay/Eval Surface Coverage
- **Severity**: P1
- **Query**: Nodes with `invokes_provider` or `writes_to` that lack `packages_execution_trace`, `triggered_telemetry`, or `scores_groundedness`
- **Evidence**: Action nodes without trace coverage

---

## Agentic Anti-Pattern Checks (AP)

### AP-1: Unsafe Text-to-Action Path
- **Severity**: P0
- **Query**: Nodes with both `consumes_prompt` (input) and `writes_to`/`invokes_provider` (action) edges but no `validates_uwg_intent` or `applies_guardrail` intermediate edge
- **Evidence**: Node bridging text input to action without validation

### AP-2: L2 Phase Bypass
- **Severity**: P0
- **Query**: L2 nodes with `invokes_provider` or `writes_to` edges that skip the `enters_sandbox` → `stamps_work_contract` phase sequence
- **Evidence**: L2 node performing action without sandbox entry

### AP-3: Provider/Tool Bypass
- **Severity**: P0
- **Query**: Non-L4 nodes with `invokes_provider` edges (providers should be accessed through L4 tool layer)
- **Evidence**: Node invoking provider from wrong layer

### AP-4: Direct Durable Write Breach
- **Severity**: P0
- **Query**: Nodes performing `commits_mutation_durable` without `validates_uwg_intent`
- **Evidence**: Unguarded durable mutation

### AP-5: Tool Overlap / Ambiguous Surfaces
- **Severity**: P1
- **Query**: Multiple nodes invoking the same provider target, indicating tool surface ambiguity
- **Evidence**: Overlapping tool invocations

### AP-6: Premature Multi-Agent Sprawl
- **Severity**: P1
- **Query**: Agent nodes (entity_type containing 'agent') exceeding threshold count without proportional tool surface
- **Evidence**: Agent count vs tool count ratio

### AP-7: Duplicate Specialization
- **Severity**: P1
- **Query**: Nodes in same layer with identical outgoing edge profiles (same set of relation_types to same targets)
- **Evidence**: Duplicate node pair

### AP-8: Missing Trace/Eval on Action Paths
- **Severity**: P1
- **Query**: Nodes performing `writes_to` or `invokes_provider` without any trace/eval edge (`packages_execution_trace`, `triggered_telemetry`, `scores_groundedness`)
- **Evidence**: Untraced action node

### AP-9: Infrastructure Spread / Service Locator Drift
- **Severity**: P1
- **Query**: Configuration/infrastructure nodes (entity_type containing 'config'/'registry'/'factory') with high fan-out (>10 outgoing edges)
- **Evidence**: Spreading infrastructure node

### AP-10: Live/Future Mutation Confusion
- **Severity**: P1
- **Query**: Nodes with both `reads_from` and `writes_to` edges to the same target, indicating potential read-write confusion
- **Evidence**: Node with read-write overlap

### AP-11: Poorly Scoped Work Contracts
- **Severity**: P2
- **Query**: L2 nodes that invoke providers or write but lack `stamps_work_contract` edges
- **Evidence**: L2 action node without work contract

### AP-12: Prompt Scatter
- **Severity**: P2
- **Query**: Nodes with >3 outgoing `generates_prompt` edges (prompt responsibility scattered)
- **Evidence**: Node generating too many prompts

### AP-13: Retry/Heal Without Exit Criteria
- **Severity**: P2
- **Query**: Nodes with `orchestrates_healing` edges but no `packages_execution_trace` (no trace seal = no exit criteria)
- **Evidence**: Healing node without trace seal

### AP-14: Retrieval Without Evidence Contract
- **Severity**: P2
- **Query**: Nodes with `pulls_context` edges but no `applies_guardrail` companion edge
- **Evidence**: Retrieval without guardrail

### AP-15: Agent Count Outrunning Tool Surfaces
- **Severity**: P3
- **Query**: Ratio of agent-type nodes to tool-type nodes exceeds 3:1
- **Evidence**: Agent:tool ratio imbalance

### AP-16: Dormant Infrastructure
- **Severity**: P3
- **Query**: Infrastructure nodes (entity_type containing 'config'/'registry'/'factory'/'util') with <3 incoming import edges
- **Evidence**: Under-utilized infrastructure node

### AP-17: Agentic Semantic Precision Gaps
- **Severity**: P3
- **Query**: Edges with generic `edge_kind` values (`call`, `import`, `use`, `reference`, `depends_on`) that should have domain-specific kinds
- **Evidence**: Generic edge kind on agentic-domain edge

---

## Configuration

Each check has a config entry in `artifacts/adg/sc_ap_config.json`:

```json
{
  "SC-1": {
    "enabled": false,
    "audit_mode": true,
    "promoted_date": null,
    "label": "Gravity import / illegal layer reach"
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | bool | Whether the check runs during ADG generation |
| `audit_mode` | bool | If true, log violations but don't block. If false, block on violation |
| `promoted_date` | string/null | ISO date when check was promoted from audit to enforce |
| `label` | string | Human-readable description |

### Promotion Workflow

1. Set `enabled: true` — check runs in audit mode
2. Observe violations in defect table (SC~/AP~ rows)
3. When violations reach 0 or all exempted:
   - Set `audit_mode: false`
   - Set `promoted_date: "YYYY-MM-DD"`
   - Check now blocks ADG generation on violation
