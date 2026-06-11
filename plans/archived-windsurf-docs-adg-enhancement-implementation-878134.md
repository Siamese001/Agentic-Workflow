---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg-enhancement-implementation-878134.md'
original_relative_path: 'adg-enhancement-implementation-878134.md'
source_sha256: edb4088b77c22de336439a08c801721dd9bae094144e784bc91dcd9f98abfc20
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-12'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Enhancement Implementation Plan

Implement 7 of 10 proposed ADG enhancements across 6 phases, adding a Hybrid ADG (static + runtime unified graph) as the foundational layer plus ~1,400 LOC of new static analysis capability.

**ADG basis:** schema_version 4.0.0 — 76,809 nodes, 209,559 edges (refreshed Mar 12 2026)

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope

**Evaluation basis:** `docs/reports/plans/adg-enhancement-evaluation-878134.md`
**Hybrid ADG feedback:** incorporated below as Phase 0 (prerequisite)

**7 enhancements to implement, 3 excluded:**
- ❌ #6 Cryptographic chain — pure runtime, L6 concern
- ❌ #7 Meta-learning loops — no gap, already modeled
- ❌ #9 Agent behavioral correctness — pure runtime state machine

**Total estimated effort:** ~1,400 LOC (static analyzers + tests) + ~400 LOC (Hybrid ADG foundation)

---

## ADG Refresh Delta

| Metric | Previous scan | New ADG (v4.0.0) | Delta | Plan impact |
|--------|--------------|-----------------|-------|-------------|
| Total nodes | ~49,000 | **76,809** | +57% | Scope of all analyzers expanded |
| Total edges | ~161,000 | **209,559** | +30% | More coverage needed |
| `dead_imports` | 3,421 | **6,274** | +83% | Dead import on L5 safety = unenforced check |
| `dead_imports` L5 | 397 | **1,015** | +156% | Strengthens case for #2 and #11 |
| `dead_imports` L_APP | 224 | **1,067** | +376% | L_APP coverage newly critical |
| `writes_to` bypass gap | ~1,161 | **1,172** | stable | #1 + #12 scope confirmed |
| L_SL `writes_through` | 0 | **0** | unchanged | #12 still needed |
| `invokes_provider` callers | 228 | **229** | stable | 218 still ungoverned in production |
| `generates_prompt` governed | 1 | **11** | +10 | Still 218 ungoverned production callers |
| L5 consultation gap | ~85 est. | **443 modules** | larger | #2 scope increased significantly |
| `antipattern` total | 1,462 | **1,439** | −23 | #13 scope stable |
| `violates` | 224 | **224** | unchanged | #15 unchanged |
| `routes_through` sources | 6 | **15** | +9 | Improved but 733 seams unverified |
| Seam-named modules | 8 | **733** | +725 | #14 scope dramatically expanded |
| L_APP test coverage | partial | **0% (1,204 uncovered)** | worse | New gap: L_APP has zero `covers` edges |

### New gap surfaced by refresh: L_APP test coverage

**Evidence:** L_APP has 1,204 module nodes. `covers` edges to L_APP modules: **0**. This is a complete blind spot — the test suite has no registered coverage of any L_APP module in the ADG. This is a candidate for a future Phase 4 enhancement (test coverage enforcement plane) but is noted here as out-of-scope for the current plan.

---

## Phase 0 — Hybrid ADG Foundation (Prerequisite)

The feedback on the Hybrid ADG proposal is **strongly agree on direction, with three mandatory prerequisites** before runtime edges can be written. These must land before any Phase 2 analyzer that crosses the static/runtime boundary.

### What the Hybrid ADG Enables

Current ADG is purely static. The 4 query patterns that require a hybrid graph:

| Query | Current | Hybrid |
|---|---|---|
| Dead governance validators | ❌ Not possible | ✅ validator node + zero `VALIDATED_BY` runtime edges |
| Unsafe execution path | ❌ Not possible | ✅ `EXECUTED` edge without `VALIDATED_BY` edge |
| Architecture drift | ❌ Not possible | ✅ runtime path without static reachability |
| Learning loop verification | ❌ Not possible | ✅ `PRODUCED_BY → VALIDATED_BY → COMMITTED_TO_L4` chain |

These queries directly unblock the **highest-value enhancements**: #2 (L5 consultation), #4 (capability chokepoint), and #8 (data contracts) can all be strengthened from "static necessary condition" to "runtime execution proof" once the hybrid graph exists.

### Feedback Verdict: What to Accept, Reject, Defer

| Feedback Point | Accept/Reject | Action |
|---|---|---|
| Single unified graph over two separate graphs | ✅ Accept | Single `edges` table with `edge_kind` column |
| Shared node identity | ✅ Accept | Nodes are same entities — see node identity protocol below |
| 4 query patterns | ✅ Accept | These are the target queries |
| Runtime edge metadata (`trace_id`, `timestamp`, `policy_hash`, `result`, `latency`) | ✅ Accept | Add to `RelationRecord` as optional fields |
| `trace`/`policy_hash` as first-class nodes | ⚠️ Defer | Keep as edge metadata for now; promote only if "all entities in trace X" becomes a hot query |
| 8+ new node types | ⚠️ Partial | Accept: `agent`, `tool`, `validator`. Defer: `trace`, `policy_hash`, `instruction_packet`, `sandbox_envelope`, `change_package` |
| Node identity protocol | ❌ Missing — must implement | See below |
| Edge lifecycle policy | ❌ Missing — must implement | See below |
| Table schema commitment | ⚠️ Undecided — must decide | Decision: single table with `edge_kind` |

### Missing Piece 1: Node Identity Protocol

**Problem:** Static AST scan produces `ADG::Module::agentic_core/L2_execution/UniversalWriteGateway.py`. If file moves, runtime edges referencing old node ID become orphaned silently.

**Solution: Content-addressable node identity with path alias index**

```python
# In schema.py — add canonical node ID function
def canonical_node_id(module_path: str, *, commit_sha: str = "") -> str:
    """Stable node ID = canonical ADG name (path-based, not content-hash).

    Path-based identity is intentional: we want 'same file = same node'.
    Moves are tracked via the alias_index, not by changing the primary ID.
    """
    return canonical_name("module", module_path)

# In artifact/builder.py — add alias index to ADGArtifact
alias_index: dict[str, str]  # old_adg_name → current_adg_name
```

**Alias index maintenance:**
- On static rescan: detect moved files via git rename detection
- Write `old_adg_name → new_adg_name` entries to `alias_index`
- Runtime edge writer resolves aliases before writing
- Stale runtime edges (pointing to non-existent nodes with no alias) → flagged in `blind_spots`

**File:** `agentic_core/adg/artifact/builder.py` — add `alias_index: dict[str, str]` to `ADGArtifact`
**File:** `agentic_core/adg/identity/node_identity.py` *(new)* — `resolve_node_id(raw_id, artifact) -> str`

### Missing Piece 2: Edge Lifecycle Policy

**Problem:** Runtime edges accumulate forever → "dead governance" queries become misleading (validator ran 6 months ago = not dead, but appears dead in current run).

**Decision: Run-scoped runtime edges**

```python
# Runtime edges carry a run_id. Queries default to "current run" scope.
# Edge record additions:
run_id: str          # UUID for the execution run that produced this edge
session_id: str      # optional: groups multiple runs into a session
expires_after: int   # optional: Unix timestamp; 0 = keep forever
```

**Lifecycle rules:**
- **Static edges**: permanent, rebuilt on each scan (deterministic)
- **Runtime edges**: scoped to `run_id`; default query scope = latest run
- **Retention**: keep last N runs (default N=10); configurable
- **"Dead governance" query**: validator node with zero `VALIDATED_BY` edges **in current run** — not across all runs

**File:** `agentic_core/adg/runtime/edge_writer.py` *(new)* — `write_runtime_edge(edge, run_id)`
**File:** `agentic_core/adg/artifact/builder.py` — extend `RelationRecord` with `run_id`, `edge_source`

### Missing Piece 3: Static/Runtime Consistency Protocol

**Problem:** Static rescan may invalidate nodes that have live runtime edges pointing to them.

**Decision: Rescan triggers consistency check**

```python
# In artifact/builder.py — post-rescan consistency check
def check_runtime_edge_consistency(
    new_artifact: ADGArtifact,
    runtime_edges: list[RelationRecord],
) -> ConsistencyReport:
    """After static rescan, find runtime edges pointing to nodes not in new artifact."""
```

**Consistency rules:**
- After every static rescan: run consistency check
- Orphaned runtime edges (node deleted, no alias) → written to `blind_spots.orphaned_runtime_edges`
- Orphaned runtime edges with alias → auto-resolved via `alias_index`
- CI gate: orphaned runtime edges without alias > 0 → **warning** (not hard fail, runtime edges are advisory)

**File:** `agentic_core/adg/analysis/consistency.py` *(new)* — `check_runtime_edge_consistency()`

> **Architectural note:** This is an **analyzer** (interprets graph facts), not part of graph construction. It reads `ADGArtifact` + runtime edges and returns a `ConsistencyReport`. It never writes to the graph.

### Schema Commitment: Single Table, `edge_kind` Column

Accepting the feedback recommendation. Current `RelationRecord` already has `edge_kind`. Extend it:

```python
@dataclass
class RelationRecord:
    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str = ""
    # NEW — Hybrid ADG fields (all optional, None = static edge)
    edge_source: Literal["static", "runtime"] = "static"
    run_id: str = ""
    trace_id: str = ""           # edge metadata, NOT a node
    policy_hash: str = ""        # edge metadata, NOT a node
    result: str = ""             # "allow" | "deny" | "pass" | "fail"
    latency_ms: float = 0.0
    timestamp: str = ""          # ISO 8601
```

**No new tables.** Static and runtime edges coexist in `ADGArtifact.relations`. Queries filter by `edge_source`.

### New Runtime Edge Types (to add to `RelationType` in `schema.py`)

Accept only the 3 non-premature node types per feedback:

```python
# Runtime relation types (edge_source="runtime")
"executed_by",          # module EXECUTED_BY agent at runtime
"validated_by",         # module VALIDATED_BY validator at runtime
"committed_to",         # mutation COMMITTED_TO L4 state at runtime
```

Defer: `PRODUCED_BY`, `sandbox_envelope`, `change_package` — premature without use cases.

### Phase 0 File Change Summary

**ADG Core** — creates or stores graph facts:

| File | Action | LOC |
|---|---|-----|
| `agentic_core/adg/schema.py` | Add `edge_source`, 3 runtime `RelationType` values, `canonical_node_id()` | ~30 |
| `agentic_core/adg/artifact/builder.py` | Extend `RelationRecord` with hybrid fields, add `alias_index` to `ADGArtifact` | ~50 |
| `agentic_core/adg/identity/node_identity.py` | New: `resolve_node_id()`, alias resolution (query helper) | ~80 |
| `agentic_core/adg/runtime/edge_writer.py` | New: `write_runtime_edge()`, run_id management | ~100 |

**Analyzers** — interpret graph facts, never write to graph:

| File | Action | LOC |
|---|---|-----|
| `agentic_core/adg/analysis/consistency.py` | New: `check_runtime_edge_consistency()` → `ConsistencyReport` | ~80 |
| `tests/adg/test_hybrid_adg_foundation.py` | New: node identity, edge lifecycle, consistency tests | ~80 |

**Phase 0 Total: ~420 LOC**

### Phase 0 Acceptance Criteria

- `RelationRecord` has `edge_source`, `run_id`, `trace_id`, `policy_hash`, `result`, `latency_ms`, `timestamp`
- `ADGArtifact` has `alias_index: dict[str, str]`
- `resolve_node_id()` returns current node ID given old or current ID
- `write_runtime_edge()` enforces `run_id` on all runtime edges
- `check_runtime_edge_consistency()` (in `analysis/consistency.py`) detects orphaned runtime edges post-rescan — reads only, never mutates artifact
- Static edges still work identically (no regression — `edge_source` defaults to `"static"`)
- All 80 tests in `test_hybrid_adg_foundation.py` green

---

## Phase 1 — Critical (P0)

### Enhancement #1: UWG Mutation Termination Proof

**Gap:** `WRITE_SIDE_EFFECT_SYMBOLS` in `schema.py` covers filesystem/subprocess only. Database and vector store writes bypass detection entirely.

**Evidence (new ADG):** `writes_to` distinct sources: **1,182**. `writes_through` distinct sources: **10**. Bypass gap: **1,172 modules** writing outside UWG.

> **Architectural role:** `schema.py` change = ADG core (adds symbol facts). `uwg_write_authority.py` change = analyzer (interprets which writes violate UWG policy). Both correctly placed.

**Files:**
- `agentic_core/adg/schema.py` — extend `WRITE_SIDE_EFFECT_SYMBOLS`
- `agentic_core/adg/applications/uwg_write_authority.py` — extend endpoint classification

**Changes:**

**Step 1 — `schema.py` (~30 LOC)**

Add to `WRITE_SIDE_EFFECT_SYMBOLS` (currently line 428–447):
```python
# Database writes
"cursor.execute",
"cursor.executemany",
"session.add",
"session.add_all",
"session.commit",
"session.merge",
"session.delete",
"collection.insert_one",
"collection.insert_many",
"collection.update_one",
"collection.update_many",
"collection.delete_one",
"collection.delete_many",
"collection.replace_one",
"redis.set",
"redis.hset",
"redis.lpush",
"redis.rpush",
"redis.sadd",
"redis.zadd",
# Vector store writes
"chromadb.add",
"chromadb.upsert",
"chromadb.delete",
"pinecone.upsert",
"pinecone.delete",
"qdrant.upsert",
"qdrant.delete",
"weaviate.batch.add_objects",
"weaviate.collections.insert",
```

**Step 2 — `uwg_write_authority.py` (~50 LOC)**

Extend `_SIDE_EFFECT_ENDPOINTS` dict (currently only `filesystem_write`, `subprocess_exec`, `network_call`, `database_write`):
- Add `database_write` key with all DB symbols above
- Add `vector_write` key with all vector store symbols above
- Extend violation severity: `database_write` → `critical`, `vector_write` → `critical`
- Update `UWGViolation` to include `endpoint_category` field for richer reporting

**Step 3 — Tests (~50 LOC)**

File: `tests/adg/test_uwg_db_vector_writes.py`
- Test: module with `cursor.execute` and no UWG path → violation detected
- Test: module with `chromadb.add` and no UWG path → violation detected
- Test: module with `session.commit` + `writes_through` UWG → compliant
- Test: L2 execution module with DB write → allowlisted (no violation)

---

### Enhancement #10: Architecture Invariant Documentation Audit

**Gap:** Architecture claims ADG verifies "execution paths" but ADG proves architectural compliance (static), not execution correctness (runtime).

**Files to audit and update:**
- `docs/architecture/hardening_addendum.md`
- `docs/architecture/AI_CHECKING_AI_REMEDIATION_COMPLETE.md`
- `docs/architecture/PascalSovereignty_vs_PreCommit.md`
- `docs/metrics/HEAL_CAPABILITY_DEFINITION.md`
- `agentic_core/adg/applications/architecture_verifier.py` — module docstring

**Changes:**

Create `docs/architecture/ADG_STATIC_VS_RUNTIME_BOUNDARY.md` with:
- What ADG proves statically (layer compliance, mutation routing, policy coupling)
- What ADG cannot prove (runtime execution, crypto results, behavioral order)
- Decision tree: "ADG or runtime monitoring?"
- Correct overclaiming language in existing docs

---

## Phase 2 — High Impact (P1)

### Enhancement #2: L5 Safety Consultation Coverage

**Gap:** No static proof that modules performing sensitive operations (writes, tool calls, provider invocations) import L5 enforcement infrastructure.

**Evidence (new ADG):** Modules with sensitive ops (`writes_to` ∪ `invokes_provider` ∪ `invokes_tool`): **1,329**. Modules importing L5_safety: **886**. Gap: **443 modules** performing sensitive operations with no L5 import.

> **Architectural role:** Analyzer — interprets `ScanResult` edges (`writes_to`, `invokes_tool`, `invokes_provider`, `imports`). Returns `L5ConsultationReport`. Never writes to the graph.

**File:** `agentic_core/adg/analysis/l5_consultation.py` *(new file)*

**Design:**
```
Sensitive operations detected via existing edge types:
  writes_to        → module must import L5 enforcement
  invokes_tool     → module must import L5 enforcement
  invokes_provider → module must import L5 enforcement

L5 enforcement modules (symbols that count as L5 consultation):
  agentic_core/L5_safety/...
  write_gateway_enforcer
  mutation_prohibition
  constitutional_validator
  SovereignContextStrategy

Violation = sensitive operation edge exists AND
            no import/call edge to any L5 module in source module
```

**Dataclasses:** `L5ConsultationViolation`, `L5ConsultationReport`

**Main function:** `detect_l5_consultation_gaps(result: ScanResult) -> L5ConsultationReport`

**Tests (~40 LOC):**
File: `tests/adg/test_l5_consultation.py`
- Test: module with `writes_to` edge but no L5 import → violation
- Test: module with `invokes_tool` edge and L5 import → compliant
- Test: L5 module itself → not flagged (excluded from check)
- Test: test/ and tools/ modules → excluded

**Wired into:** `architecture_verifier.py` as plane `E32_L5_CONSULTATION`

---

### Enhancement #3: Policy Hash Verification (call-graph enhancement)

**Gap:** Existing `policy_hash_validator.py` detects import-level coupling but not call-graph coupling — a module can import `policy_hash` but never actually call the validation function.

> **Architectural role:** Analyzer — reads `calls` and `imports` edges from `ScanResult`. Returns report with violations. Never writes to the graph.

**File:** `agentic_core/adg/analysis/policy_hash_validator.py` *(enhance existing)*

**Changes (~50 LOC):**

Add second violation type: `POLICY_HASH_NOT_CALLED`
- Current: detects `InstructionPacket` used without `policy_hash` *imported*
- New: additionally detect `InstructionPacket` used without `verify_policy_hash` *called* (call edge, not just import edge)

Add `_POLICY_HASH_CALL_SYMBOLS` frozenset:
```python
_POLICY_HASH_CALL_SYMBOLS: frozenset[str] = frozenset({
    "verify_policy_hash",
    "_verify_plan_hash",
    "_verify_replay_hash",
    "validate_policy_stamp",
    "assert_policy_current",
})
```

New pass in `validate_policy_hash_coupling()`:
- Pass 3: For modules with instruction packet symbols AND policy hash import, check if they also have a `calls` edge to any `_POLICY_HASH_CALL_SYMBOLS`
- Emit `POLICY_HASH_IMPORTED_NOT_CALLED` violation if import exists but call doesn't

**Tests (~30 LOC):**
File: `tests/adg/test_policy_hash_call_graph.py`
- Test: module imports and calls `verify_policy_hash` → compliant
- Test: module imports `policy_hash` but has no call edge → `POLICY_HASH_IMPORTED_NOT_CALLED`
- Test: module has neither import nor call → `POLICY_HASH_MISSING` (existing)

---

### Enhancement #4: Capability Token Chokepoint Enforcement

**Gap:** No static proof that tool invocations route through `CapabilityChokepoint.authorize_and_execute`.

> **Architectural role:** Analyzer — interprets `invokes_tool`, `imports`, `calls` edges from `ScanResult`. Returns `CapabilityEnforcementReport`. Never writes to the graph.

**File:** `agentic_core/adg/analysis/capability_enforcement.py` *(new file)*

**Design:**
```
Tool invocation symbols (from runtime_graph.py _TOOL_INVOKE_SYMBOLS):
  tool.run, tool.invoke, execute_tool, run_tool,
  mcp_tool_call, invoke_capability, dispatch_tool

Chokepoint symbols:
  authorize_and_execute       (CapabilityChokepoint method)
  CapabilityChokepoint        (class import)
  capability_chokepoint       (module import)

Violation = module has invokes_tool edge AND
            no import/call edge to chokepoint symbols

Allowlist:
  agentic_core/L2_execution/enforcement/capability_chokepoint.py  (IS the chokepoint)
  tests/
  tools/
```

**Dataclasses:** `CapabilityBypassViolation`, `CapabilityEnforcementReport`

**Main function:** `detect_capability_bypass(result: ScanResult) -> CapabilityEnforcementReport`

**Tests (~50 LOC):**
File: `tests/adg/test_capability_enforcement.py`
- Test: module with `invokes_tool` edge + no chokepoint import → violation
- Test: module with `invokes_tool` edge + `authorize_and_execute` call → compliant
- Test: capability_chokepoint.py itself → allowlisted
- Test: test module → allowlisted

**Wired into:** `architecture_verifier.py` as plane `E33_CAPABILITY_CHOKEPOINT`

---

## Phase 3 — Valuable (P2)

### Enhancement #5: DAG Validation Infrastructure (Partial)

**Scope:** Prove that orchestrator modules have DAG validation infrastructure wired in (not runtime DAG correctness).

> **Architectural role:** Analyzer — reads `calls`, `imports`, layer metadata from `ScanResult`. Returns `OrchestrationValidationReport`. Never writes to the graph.

**File:** `agentic_core/adg/analysis/orchestration_validation.py` *(new file)*

**Design:**
```
Orchestrator detection: modules in L3 or matching patterns:
  *orchestrat*, *planner*, *scheduler*, *dag*, *workflow*

DAG validation symbols (static infrastructure):
  nx.is_directed_acyclic_graph
  networkx.DiGraph
  topological_sort
  detect_cycles
  validate_dag
  dag_validator
  check_acyclic

Violation = module is an orchestrator AND
            builds task graphs (calls graph construction symbols) AND
            has no DAG validation symbols in call graph
```

**Dataclasses:** `OrchestrationValidationViolation`, `OrchestrationValidationReport`

**Main function:** `validate_orchestration_infrastructure(result: ScanResult) -> OrchestrationValidationReport`

**Tests (~40 LOC):**
File: `tests/adg/test_orchestration_validation.py`
- Test: orchestrator with `DiGraph()` call + no DAG validation → violation
- Test: orchestrator with `DiGraph()` + `is_directed_acyclic_graph()` → compliant
- Test: non-orchestrator module → not flagged

**Wired into:** `architecture_verifier.py` as plane `E34_ORCHESTRATION_DAG`

---

### Enhancement #8: Data Contract Integrity Enforcement

**Gap:** No static proof that modules mutating data import and call contract validators (Pydantic, TypedDict).

> **Architectural role:** `schema.py` additions = ADG core (symbol fact definitions). `contract_integrity.py` = analyzer (interprets whether those symbols are correctly used). Returns `ContractIntegrityReport`. Never writes to the graph.

**Files:**
- `agentic_core/adg/schema.py` — add `CONTRACT_DEFINITION_SYMBOLS`, `CONTRACT_VALIDATION_SYMBOLS`
- `agentic_core/adg/analysis/contract_integrity.py` *(new file)*

**Step 1 — `schema.py` additions (~30 LOC):**
```python
CONTRACT_DEFINITION_SYMBOLS: frozenset[str] = frozenset({
    "BaseModel",           # Pydantic
    "TypedDict",           # typing
    "dataclass",           # dataclasses
    "attrs.define",        # attrs
    "pydantic.dataclasses.dataclass",
})

CONTRACT_VALIDATION_SYMBOLS: frozenset[str] = frozenset({
    "model_validate",      # Pydantic v2
    "parse_obj",           # Pydantic v1
    "model_validate_json",
    "TypeAdapter",
    "validate_call",
    "field_validator",
    "model_validator",
    "__post_init__",       # dataclass validation
})
```

**Step 2 — `contract_integrity.py` (~120 LOC):**

```
Violation = module performs writes_to AND
            module handles data structures (imports contract definitions) AND
            module has NO call edge to any CONTRACT_VALIDATION_SYMBOLS

Scope: L0, L1, L2, L3, L_APP modules only
Allowlist: tests/, tools/, schema definition files themselves
```

**Dataclasses:** `ContractIntegrityViolation`, `ContractIntegrityReport`

**Main function:** `detect_contract_integrity_gaps(result: ScanResult) -> ContractIntegrityReport`

**Tests (~50 LOC):**
File: `tests/adg/test_contract_integrity.py`
- Test: module imports `BaseModel` + writes data + no `.model_validate()` call → violation
- Test: module imports `BaseModel` + writes data + calls `.model_validate()` → compliant
- Test: test modules → excluded
- Test: schema definition module → excluded

**Wired into:** `architecture_verifier.py` as plane `E35_CONTRACT_INTEGRITY`

---

## Cross-Cutting: Wire New Planes into Architecture Verifier

**File:** `agentic_core/adg/applications/architecture_verifier.py`

Add plane imports and invocations in `verify_architecture()`. All planes are **external consumers of the graph** — they receive `ScanResult` or `ADGArtifact` as input and return report objects. None write to the graph.

| Plane ID | Analyzer file | Function | Status |
|----------|--------------|----------|--------|
| `E21_PROMPT_AUTHORITY` | `prompt_authority.py` | `detect_prompt_authority_violations` | exists, wire only |
| `E22_PROMPT_DRIFT` | `prompt_drift.py` | `detect_prompt_drift` | exists, wire only |
| `E32_L5_CONSULTATION` | `l5_consultation.py` | `detect_l5_consultation_gaps` | new |
| `E33_CAPABILITY_CHOKEPOINT` | `capability_enforcement.py` | `detect_capability_bypass` | new |
| `E34_ORCHESTRATION_DAG` | `orchestration_validation.py` | `validate_orchestration_infrastructure` | new |
| `E35_CONTRACT_INTEGRITY` | `contract_integrity.py` | `detect_contract_integrity_gaps` | new |
| `E36_ANTIPATTERN_SEVERITY` | `antipattern_severity.py` | `classify_antipattern_severity` | new |
| `E37_SEAM_COVERAGE` | `seam_coverage.py` | `detect_seam_coverage_gaps` | new |
| `E38_VIOLATION_PATTERN` | `layer_authority.py` *(extend)* | `classify_violation_patterns` | extend existing |
| `E39_PROMPT_COVERAGE` | `prompt_governance_coverage.py` | `detect_ungoverned_llm_calls` | new |

> **Architectural note:** `architecture_verifier.py` is an **orchestrator of analyzers**, not part of graph construction. It delegates entirely to analyzer functions and aggregates `PlaneResult` objects. It never reads or writes graph storage directly.

Each plane follows the existing pattern:
```python
PlaneResult(
    plane="E32_L5_CONSULTATION",
    passed=report.violation_count == 0,
    violation_count=report.violation_count,
    summary=report.summary,
)
```

---

## Phase 2.5 — Prompt Governance & Learning Enforcement (P1)

*Evidence: 227/228 LLM callers have no `generates_prompt` edge. `triggered_telemetry` has only 3 edges. `prompt_authority.py` and `prompt_drift.py` already exist but are NOT wired into `architecture_verifier.py`.*

### Enhancement #11: Prompt Governance Coverage

> **Architectural role:** `prompt_authority.py` and `prompt_drift.py` are pure analyzers — they read `generates_prompt`, `consumes_prompt`, `invokes_provider` edges and return report objects. `prompt_governance_coverage.py` (new) is also a pure analyzer. None write to the graph. `architecture_verifier.py` wiring = orchestration only.

**Gap:** `prompt_authority.py` (E21) and `prompt_drift.py` (E22) exist as complete analyzers but are not wired into `architecture_verifier.py`. ADG scan shows **218 of 229** `invokes_provider` callers have zero `generates_prompt` edge — the governed prompt pipeline is almost entirely unenforced at the ADG level.

**Evidence (new ADG):** Ungoverned by layer — L_TEST: 58, L_APP: 46, L0: 32, L5: 21, L2: 18, L_TOOLS: 16, L3: 7, L4: 3, L_SL: 3, L1: 1, L6: 1. Production layers (L0–L6 + L_APP + L_SL) = **132 ungoverned production callers**.

**Files:**
- `agentic_core/adg/applications/architecture_verifier.py` — wire `E21` and `E22` (existing)
- `agentic_core/adg/analysis/prompt_governance_coverage.py` *(new)* — detect `invokes_provider` callers with no `generates_prompt` edge

**`prompt_governance_coverage.py` design (~80 LOC):**
```
Violation = module has invokes_provider edge AND
            no generates_prompt edge from that module AND
            module is not in allowlist (seams, tests, tools, ops_scripts)

Severity: CRITICAL for L0-L3 callers, WARNING for L_APP callers
```

**Dataclasses:** `UngovermedLLMCallViolation`, `PromptGovernanceCoverageReport`

**Main function:** `detect_ungoverned_llm_calls(result: ScanResult) -> PromptGovernanceCoverageReport`

**Wired into:** `architecture_verifier.py` as plane `E39_PROMPT_COVERAGE`

**Tests (~40 LOC):** `tests/adg/test_prompt_governance_coverage.py`
- Test: module with `invokes_provider` + no `generates_prompt` → violation
- Test: module with `invokes_provider` + `generates_prompt` → compliant
- Test: seam module → allowlisted
- Test: L0 vs L_APP severity difference

### Enhancement #12: System Learning UWG Bypass

**Gap:** Enhancement #1 adds DB/vector write symbols to `WRITE_SIDE_EFFECT_SYMBOLS`. But L_SL (`system_learning/`) has **38 distinct modules** making raw filesystem writes (`f.write`, `open`, `mkdir`, `write_text`) — **166 write edges** total — bypassing UWG entirely. This is a distinct violation category: the learning loop commits to L4 state via `l4_state_writer.py` without routing through `UniversalWriteGateway`. Enhancement #1 will not catch these (they are filesystem, not DB/vector) and `writes_through` for L_SL = **0**.

**Evidence (new ADG):** L_SL `writes_to` distinct sources: **38**. L_SL `writes_through`: **0**.

> **Architectural role:** Analyzer — reads `writes_to`, `writes_through` edges and layer metadata from `ScanResult`. The new `LEARNING_LOOP_BYPASSES_UWG` violation type is a new interpretation of existing graph facts, not a new graph fact. Returns updated `MutationAuthorityReport`. Never writes to the graph.

**File:** `agentic_core/adg/analysis/mutation_authority.py` *(extend existing)*

**Changes (~40 LOC):**

Add new violation type `LEARNING_LOOP_BYPASSES_UWG`:
```python
# In mutation_authority.py — new violation subtype
LEARNING_LOOP_BYPASSES_UWG = "LEARNING_LOOP_BYPASSES_UWG"
```
New detection pass in `verify_mutation_paths()`:
- Detect all `L_SL` modules with `writes_to` edges and no `writes_through` edge
- Classify as `LEARNING_LOOP_BYPASSES_UWG` with `CRITICAL` severity
- Exclude: `embedding_corpus_extraction.py` (reads only), test scaffolding

**Tests (~30 LOC):** `tests/adg/test_learning_loop_uwg.py`
- Test: `system_learning/` module with `writes_to` + no `writes_through` → `LEARNING_LOOP_BYPASSES_UWG`
- Test: `system_learning/` module with `writes_through` → compliant
- Test: non-L_SL module → uses existing bypass logic (not this new type)

---

## Phase 3.5 — Anti-Pattern Triage & Seam Coverage (P2)

*Evidence (new ADG, schema v4.0.0): 1,439 antipattern edges with no severity ranking. `routes_through` has 49 edges covering 15 distinct sources, but 733 seam-named modules exist and 228 provider callers have no `routes_through` edge. 224 `violates` edges with no pattern classification.*

### Enhancement #13: Anti-Pattern Severity Classification

**Gap:** ADG detects **1,439** anti-patterns uniformly: `retry_without_backoff` (801), `silent_exception_swallow` (560), `global_state_mutation` (70), `blocking_call_in_async` (8). No severity distinction exists. `global_state_mutation` in `execution_gateway.py` (an enforcement module) is categorically more dangerous than `retry_without_backoff` in a utility script.

**Evidence (new ADG):** Total antipattern edges: **1,439** (down from 1,462 — 23 resolved). Breakdown stable; enforcement-layer CRITICAL cases unchanged.

> **Architectural role:** Analyzer — reads `antipattern` edges and layer metadata from `ScanResult`. Severity classification is interpretation of existing facts, not new graph construction. Returns `AntipatternSeverityReport`. Never writes to the graph.

**File:** `agentic_core/adg/analysis/antipattern_severity.py` *(new)*

**Design (~100 LOC):**
```
Severity matrix:
  CRITICAL = antipattern in enforcement/gateway/L2/L5 modules
  HIGH     = global_state_mutation or blocking_call_in_async anywhere
  MEDIUM   = silent_exception_swallow in L0-L4
  LOW      = retry_without_backoff in L_APP/L_OPS/scripts

Critical module patterns:
  *enforcement*, *gateway*, *chokepoint*, *guard*, *prohibition*
  + any module in L2_execution/enforcement/, L5_safety/enforcement/
```

**Dataclasses:** `SeverityClassifiedAntipattern`, `AntipatternSeverityReport`

**Main function:** `classify_antipattern_severity(result: ScanResult) -> AntipatternSeverityReport`

**Wired into:** `architecture_verifier.py` as plane `E36_ANTIPATTERN_SEVERITY`

**Tests (~40 LOC):** `tests/adg/test_antipattern_severity.py`
- Test: `global_state_mutation` in enforcement module → CRITICAL
- Test: `retry_without_backoff` in L_APP util → LOW
- Test: `blocking_call_in_async` anywhere → HIGH
- Test: `silent_exception_swallow` in L0 → MEDIUM

### Enhancement #14: Seam Coverage Enforcement

**Gap:** `routes_through` plane has **49 edges** across **15 distinct sources** routing through `SovereignLLMGateway`. However the ADG now resolves **733 modules** matching seam name patterns — a dramatic increase from 8 previously identified. Of 229 `invokes_provider` callers, only 15 have `routes_through` edges. The ADG cannot currently prove that all LLM calls route through architectural seams.

**Evidence (new ADG):** `routes_through` edges: **49**, distinct sources: **15**, seam-named modules: **733**, ungoverned provider callers: **228**. Gap between seam inventory and `routes_through` coverage is significant.

> **Architectural role:** Analyzer — reads `invokes_provider`, `routes_through`, `imports` edges and module name patterns from `ScanResult`. Returns `SeamCoverageReport`. Never writes to the graph.

**File:** `agentic_core/adg/analysis/seam_coverage.py` *(new)*

**Design (~110 LOC):**
```
Seam detection:
  - Modules named *_seam.py in L0_routing/seams/
  - Modules with routes_through edge to SovereignLLMGateway

Coverage check:
  For each invokes_provider caller:
    COMPLIANT   = caller IS a seam module
    COMPLIANT   = caller has routes_through edge to a seam
    VIOLATION   = neither (ungated provider call)

Violation types:
  PROVIDER_CALL_BYPASSES_SEAM  — production module calling provider directly
  SEAM_MISSING_ROUTES_THROUGH  — seam module lacks routes_through edge
```

**Dataclasses:** `SeamCoverageViolation`, `SeamCoverageReport`

**Main function:** `detect_seam_coverage_gaps(result: ScanResult) -> SeamCoverageReport`

**Wired into:** `architecture_verifier.py` as plane `E37_SEAM_COVERAGE`

**Tests (~40 LOC):** `tests/adg/test_seam_coverage.py`
- Test: seam module with `invokes_provider` + `routes_through` → compliant
- Test: seam module with `invokes_provider` but no `routes_through` → `SEAM_MISSING_ROUTES_THROUGH`
- Test: non-seam module calling provider directly → `PROVIDER_CALL_BYPASSES_SEAM`
- Test: non-seam module with `routes_through` seam → compliant

### Enhancement #15: Layer Violation Pattern Classifier

**Gap:** **224** `violates` edges exist but are all recorded identically. The ADG cannot answer: "what *kind* of violation is this?" The new ADG confirms L0 is the dominant violating layer: L0→L5 (routing calling safety = safety_skip), L0→L2 (routing calling execution directly = gateway bypass), L0→L4 (routing calling state = state direct), L0→L_SL (upward gravity). All 224 are indistinguishable in current graph.

**Evidence (new ADG):** Violates total: **224** (unchanged). All sourced predominantly from L0. Pattern breakdown requires the new classifier to distinguish actionable from intentional violations.

> **Architectural role:** Analyzer — reads `violates` edges and layer metadata from `ScanResult`. `ViolationPattern` is an interpretation taxonomy, not a new edge type in the graph. Returns `ViolationPatternReport`. Never writes to the graph.

**File:** `agentic_core/adg/analysis/layer_authority.py` *(extend existing)*

**Changes (~80 LOC):**

Add `ViolationPattern` enum and `classify_violation_patterns()` function:
```python
class ViolationPattern(str, Enum):
    UPWARD_GRAVITY    = "upward_gravity"     # lower layer importing higher (L0→L_SL)
    GATEWAY_BYPASS    = "gateway_bypass"     # orchestration calling tools directly
    STATE_DIRECT      = "state_direct"       # non-L4 writing to L4 state directly
    SAFETY_SKIP       = "safety_skip"        # L0-L3 calling L5 directly (bypassing L4 gate)
    CROSS_APP         = "cross_app"          # L_APP modules importing each other
```

**Main function:** `classify_violation_patterns(result: ScanResult) -> ViolationPatternReport`

**Wired into:** `architecture_verifier.py` as plane `E38_VIOLATION_PATTERN`

**Tests (~40 LOC):** `tests/adg/test_violation_patterns.py`
- Test: L0 importing L_SL → `UPWARD_GRAVITY`
- Test: L3 with `invokes_provider` and no L2 routing → `GATEWAY_BYPASS`
- Test: L_SL writing to L4 directly → `STATE_DIRECT`
- Test: L0 importing L5 directly → `SAFETY_SKIP`

---

## Test Strategy

Each new analyzer follows the existing testing pattern in `tests/adg/`:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_uwg_db_vector_writes.py` | 4 | DB/vector write detection |
| `test_l5_consultation.py` | 4 | L5 bypass detection |
| `test_policy_hash_call_graph.py` | 3 | Call-graph policy coupling |
| `test_capability_enforcement.py` | 4 | Chokepoint bypass detection |
| `test_orchestration_validation.py` | 3 | DAG infrastructure existence |
| `test_contract_integrity.py` | 4 | Contract validation wiring |
| `test_prompt_governance_coverage.py` | 4 | Ungoverned LLM call detection |
| `test_learning_loop_uwg.py` | 3 | L_SL UWG bypass detection |
| `test_antipattern_severity.py` | 4 | Anti-pattern severity triage |
| `test_seam_coverage.py` | 4 | Seam routing enforcement |
| `test_violation_patterns.py` | 4 | Violation pattern classification |
| `test_hybrid_adg_foundation.py` | 80 | Node identity, edge lifecycle, consistency |

All tests: deterministic, no mocks of core logic, use synthetic `ScanResult` fixtures.

---

## File Change Summary

> **Principle applied throughout:** Files that *create or store graph facts* belong in ADG core (`schema`, `artifact`, `runtime`, `identity`). Files that *interpret graph facts* are analyzers (`analysis/`, `applications/`). No analyzer writes to the graph.

### ADG Core — creates/stores graph facts

| File | Action | LOC | Phase |
|------|--------|-----|-------|
| `agentic_core/adg/schema.py` | Extend `WRITE_SIDE_EFFECT_SYMBOLS`, add `CONTRACT_*` symbols, 3 runtime `RelationType` values, `canonical_node_id()` | ~90 | P0+P1+P3 |
| `agentic_core/adg/artifact/builder.py` | Extend `RelationRecord` with hybrid fields (`edge_source`, `run_id`, etc.), add `alias_index` to `ADGArtifact` | ~50 | P0 |
| `agentic_core/adg/identity/node_identity.py` | New: `resolve_node_id()` — query helper, returns data only | ~80 | P0 |
| `agentic_core/adg/runtime/edge_writer.py` | New: `write_runtime_edge()`, run_id management | ~100 | P0 |

### Analyzers — interpret graph facts, read-only from graph

| File | Action | LOC | Phase |
|------|--------|-----|-------|
| `agentic_core/adg/analysis/consistency.py` | New: `check_runtime_edge_consistency()` → `ConsistencyReport` | ~80 | P0 |
| `agentic_core/adg/applications/uwg_write_authority.py` | Extend endpoint classification — reads `writes_to`/`writes_through` edges | ~50 | P1 |
| `agentic_core/adg/analysis/l5_consultation.py` | New: `detect_l5_consultation_gaps()` → `L5ConsultationReport` | ~120 | P2 |
| `agentic_core/adg/analysis/policy_hash_validator.py` | Extend: add call-graph check — reads `calls`/`imports` edges | ~50 | P2 |
| `agentic_core/adg/analysis/capability_enforcement.py` | New: `detect_capability_bypass()` → `CapabilityEnforcementReport` | ~130 | P2 |
| `agentic_core/adg/analysis/prompt_authority.py` | Wire only — already complete analyzer, zero code changes | — | P2.5 |
| `agentic_core/adg/analysis/prompt_drift.py` | Wire only — already complete analyzer, zero code changes | — | P2.5 |
| `agentic_core/adg/analysis/prompt_governance_coverage.py` | New: `detect_ungoverned_llm_calls()` → `PromptGovernanceCoverageReport` | ~80 | P2.5 |
| `agentic_core/adg/analysis/mutation_authority.py` | Extend: add `LEARNING_LOOP_BYPASSES_UWG` violation type — reads `writes_to`/layer edges | ~40 | P2.5 |
| `agentic_core/adg/analysis/orchestration_validation.py` | New: `validate_orchestration_infrastructure()` → `OrchestrationValidationReport` | ~110 | P3 |
| `agentic_core/adg/analysis/contract_integrity.py` | New: `detect_contract_integrity_gaps()` → `ContractIntegrityReport` | ~120 | P3 |
| `agentic_core/adg/analysis/antipattern_severity.py` | New: `classify_antipattern_severity()` → `AntipatternSeverityReport` | ~100 | P3.5 |
| `agentic_core/adg/analysis/seam_coverage.py` | New: `detect_seam_coverage_gaps()` → `SeamCoverageReport` | ~110 | P3.5 |
| `agentic_core/adg/analysis/layer_authority.py` | Extend: `classify_violation_patterns()` → `ViolationPatternReport` | ~80 | P3.5 |
| `agentic_core/adg/applications/architecture_verifier.py` | Wire 10 planes — orchestrates analyzers, never reads/writes graph storage | ~80 | P2–P3.5 |

### Docs & Tests

| File | Action | LOC | Phase |
|------|--------|-----|-------|
| `docs/architecture/ADG_STATIC_VS_RUNTIME_BOUNDARY.md` | New: documents creates-vs-interprets boundary for contributors | — | P1 |
| `tests/adg/test_hybrid_adg_foundation.py` | New tests | ~80 | P0 |
| `tests/adg/test_uwg_db_vector_writes.py` | New tests | ~50 | P1 |
| `tests/adg/test_l5_consultation.py` | New tests | ~40 | P2 |
| `tests/adg/test_policy_hash_call_graph.py` | New tests | ~30 | P2 |
| `tests/adg/test_capability_enforcement.py` | New tests | ~50 | P2 |
| `tests/adg/test_prompt_governance_coverage.py` | New tests | ~40 | P2.5 |
| `tests/adg/test_learning_loop_uwg.py` | New tests | ~30 | P2.5 |
| `tests/adg/test_orchestration_validation.py` | New tests | ~40 | P3 |
| `tests/adg/test_contract_integrity.py` | New tests | ~50 | P3 |
| `tests/adg/test_antipattern_severity.py` | New tests | ~40 | P3.5 |
| `tests/adg/test_seam_coverage.py` | New tests | ~40 | P3.5 |
| `tests/adg/test_violation_patterns.py` | New tests | ~40 | P3.5 |

**Total:** ~1,810 LOC (production + tests) across 31 files

---

## Acceptance Criteria

### Phase 0 Complete When:
- `RelationRecord` has `edge_source`, `run_id`, `trace_id`, `policy_hash`, `result`, `latency_ms`, `timestamp`
- `ADGArtifact` has `alias_index: dict[str, str]`
- `resolve_node_id()` returns current node ID given old or current ID
- `write_runtime_edge()` enforces `run_id` on all runtime edges
- `check_runtime_edge_consistency()` detects orphaned runtime edges post-rescan
- All 80 tests in `test_hybrid_adg_foundation.py` green

### Phase 1 Complete When:
- `verify_mutation_paths()` detects `cursor.execute` and `chromadb.add` bypasses
- `tests/adg/test_uwg_db_vector_writes.py` — all 4 tests green
- `docs/architecture/ADG_STATIC_VS_RUNTIME_BOUNDARY.md` exists

### Phase 2 Complete When:
- `detect_l5_consultation_gaps()` detects sensitive operations without L5 import
- `validate_policy_hash_coupling()` detects imported-but-not-called policy hash
- `detect_capability_bypass()` detects tool calls without chokepoint wiring
- All 3 test files green (11 total tests)
- All 3 planes appear in `ArchitectureVerificationReport`

### Phase 2.5 Complete When:
- `detect_ungoverned_llm_calls()` detects the 227 ungoverned `invokes_provider` callers
- `detect_prompt_authority_violations()` (existing) wired and returning results
- `detect_prompt_drift()` (existing) wired and returning results
- `verify_mutation_paths()` detects `LEARNING_LOOP_BYPASSES_UWG` in `system_learning/`
- All 2 new test files green

### Phase 3 Complete When:
- `validate_orchestration_infrastructure()` detects orchestrators without DAG validation
- `detect_contract_integrity_gaps()` detects data mutations without contract validation
- All 2 test files green (7 total tests)
- All planes appear in `ArchitectureVerificationReport`

### Phase 3.5 Complete When:
- `classify_antipattern_severity()` ranks all 1,439 antipatterns by layer+type severity
- `detect_seam_coverage_gaps()` detects modules from 733-seam inventory missing `routes_through` (only 15 currently covered)
- `classify_violation_patterns()` classifies all 224 `violates` edges by pattern type
- All 3 test files green
- `python -m pytest tests/adg/` — zero failures

---

## Excluded (Deferred to Runtime Monitoring Framework)

| # | Enhancement | Reason | Future Home |
|---|------------|--------|-------------|
| 6 | Cryptographic chain validation | Runtime result, not code structure | L6 observability framework |
| 7 | Meta-learning feedback loops | No gap — already in ADG import/call edges | N/A |
| 9 | Agent behavioral correctness | Runtime state machine | Agent runtime framework |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

