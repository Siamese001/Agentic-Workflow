---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\v15-gap-closure-implementation-plan-69a143.md'
original_relative_path: 'v15-gap-closure-implementation-plan-69a143.md'
source_sha256: ca1f49015899bf817b8e33bb6346cff6771e202483d8e2e51478df4cafb168ec
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# V15 Gap Analysis Closure — Phased Implementation Plan

A prioritized plan to close the gap between the current V15 codebase and the Prompt v5.0 Enhanced Gap Analysis requirements, organized into 4 priority tiers by risk and impact.

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


## Current State Assessment (Revised)

The codebase has **significantly more** V15 infrastructure than initially apparent:

| Layer | Description | Status | Evidence |
|-------|------------|--------|----------|
| **A: Types Defined** | Frozen dataclasses for all §1–§15 artifacts | **~95% complete** | `v15_types.py`, `v15_p2_types.py`, `v15_p3_types.py`, `v15_p4_types.py`, `v15_p5_types.py`, `v15_p6_types.py` |
| **B: Contracts Enforced** | Enforcement functions consuming types | **~80% complete** | `v15_contracts.py`, `v15_p2_contracts.py`, `v15_p3_contracts.py`, `v15_p4_contracts.py`, `v15_p5_contracts.py`, `v15_p6_contracts.py` |
| **C: Tests Covering** | Guardian compliance tests | **332/332 PASS** | `tests/guardian/test_v15_p{1..6}_compliance.py` |
| **D: Runtime Wired** | Agents actually consuming typed artifacts | **~5–10%** | Only `SovereignBaseAgent.py`, `v15_execution_gateway.py`, `contextual_router_config.py` import V15 types |
| **E: CI Enforced** | CI gates verifying runtime conformance | **~15%** | P0/P1/P2 gates exist; no P3–P6 gates |

### Typed Artifacts Already Defined

Every artifact from the gap analysis exists as a frozen dataclass:

| § | Artifact | Type File | Contract File |
|---|----------|-----------|--------------|
| §1.3 | `SurgicalManifest` (10 fields) | `v15_p2_types.py` | `v15_p2_contracts.py` |
| §2.5 | `HEALER_PIPE_ORDER` (10-step) | `v15_types.py` | `v15_contracts.py::PipeOrderEnforcer` |
| §2.7.1 | `SignedModify` | `v15_p5_types.py` | — |
| §2.8 | `AggregateArtifact` | `v15_types.py` | `v15_contracts.py::aggregate_gate_check` |
| §3.1 | `RouteDecisionArtifact` | `v15_types.py` | — |
| §3.4 | `EvidencePack` | `v15_p3_types.py` | — |
| §3.5 | `PolicyUpdateProposal` | `v15_p3_types.py` | — |
| §3.6 | `LawSlotHandler` | — | `v15_contracts.py` |
| §3.7 | `PolicyExceptionArtifact` | `v15_p3_types.py` | — |
| §3.8 | `ContextRetrievalRequest` | `v15_p6_types.py` | — |
| §4.1 | `PolicyConfigGuard` | `v15_types.py` | `v15_contracts.py` |
| §5.2 | `ErrorSignature` | `v15_p4_types.py` | — |
| §5.4 | `SelfHealingTrigger` | `v15_types.py` | — |
| §6.1 | `EpisodicMemoryQueryResult` | `v15_p2_types.py` | `v15_p2_contracts.py` |
| §6.3 | `TokenControlArtifact` | `v15_types.py` | — |
| §6.5 | `RetrievalQuery → RetrievedChunk → RerankScore → CitationBundle` | `v15_p4_types.py` | — |
| §6.6 | `KnowledgeSupervisorResult` | `v15_p2_types.py` | `v15_p2_contracts.py` |
| §6.7 | `PlanProvenance` | `v15_p4_types.py` | — |
| §6.8 | `MemoryHypostate` | `v15_p2_types.py` | — |
| §7.2 | `ReplayGuardRecord` | `v15_p5_types.py` | — |
| §7.2.1 | `SignedGuardianArtifact` | `v15_p5_types.py` | — |
| §7.4.1 | `SignatureEnclave` (ABC) + `DeterministicTestEnclave` | `v15_p5_types.py` | — |
| §7.4.2 | `TrustRoot`, `KeyRecord` | `v15_p5_types.py` | — |
| §10.2 | `BoundarySnapshotArtifact` | `v15_p2_types.py` | `v15_p2_contracts.py` |
| §10.4 | `ResultArtifact` | `v15_types.py` | `v15_contracts.py::validate_result_emission` |
| §11.1 | `TokenCapArtifact`, `PermsArtifact` | `v15_types.py` | — |
| §12.2 | `SideEffectRegistry` | `v15_p6_types.py` | — |
| §13.1 | `SemanticClock` | `v15_p2_types.py` | `v15_p2_contracts.py` |
| §15.1 | `VigilanceTier`, `EvacuationProtocol` | `v15_types.py` | `v15_contracts.py::TieredVigilanceMonitor` |
| §15.2 | `CognitiveDiffBundle` | `v15_p4_types.py` | — |
| §15.3 | `ForensicTraceBuffer` | `v15_p2_types.py` | `v15_p2_contracts.py` |
| §15.5 | `TRACE_ID_PATTERN` + `validate_trace_id` | `v15_p4_types.py` | — |

### The Real Gap

The primary gap is **Layer D: Runtime Wiring** — the 149 active agents don't consume these typed artifacts at runtime. The types and contracts exist, the tests pass, but the agents use older ad-hoc patterns. The secondary gap is **Layer E: CI Enforcement** — only P0/P1/P2 CI gates exist.

---

## Phased Implementation

### TIER 1 — Critical Path (Runtime Wiring Foundation)
**Priority**: P0 — blocks all downstream work
**Risk**: Low (no behavior change, additive only)
**Estimated effort**: 2–3 sessions

#### Phase 7.1: SovereignBaseAgent V15 Artifact Protocol

Wire the base agent class to emit/consume typed artifacts, so all 149 agents inherit the protocol.

**Target file**: `agentic_core/base_agents/SovereignBaseAgent.py`

**Changes**:
1. Add `SemanticClock` instance to base agent `__init__`
2. Add `_emit_boundary_snapshot()` to `heal()` pre-path
3. Add `_emit_result()` to `heal()` post-path (L2 only)
4. Add `_emit_aggregate()` to validation pre-path
5. Add `trace_id` generation (§15.5 format `^CC3AL1-[0-9A-F]{8}$`) at entry
6. Add `SideEffectRegistry` accumulator

**Diff sketch** (SovereignBaseAgent.__init__):
```python
# BEFORE
def __init__(self, project_root=None, ...):
    self.project_root = project_root
    ...

# AFTER
def __init__(self, project_root=None, ...):
    self.project_root = project_root
    self._semantic_clock = SemanticClock()
    self._trace_id: str | None = None
    self._side_effects: list[str] = []
    ...
```

**Diff sketch** (heal method wrapper):
```python
# BEFORE
def heal(self, ...):
    ...do healing...

# AFTER
def heal(self, ...):
    from agentic_core.L0_maintenance.types.v15_p4_types import validate_trace_id
    self._trace_id = self._generate_trace_id()
    snapshot = self._create_boundary_snapshot()
    try:
        result = self._do_heal(...)  # existing logic
        self._emit_result(result)
        self._semantic_clock.tick(self._layer, state_commit_valid=True)
    except Exception:
        self._verify_rollback(snapshot)
        raise
```

**Guardian tests**: Add to `test_v15_p1_compliance.py` — verify base agent has SemanticClock, trace_id generation, snapshot methods.

---

#### Phase 7.2: V15 Execution Gateway Runtime Integration

The `v15_execution_gateway.py` already imports V15 types. Wire it to actually enforce the `PipeOrderEnforcer` and `PolicyConfigGuard` at runtime.

**Target file**: `agentic_core/L0_maintenance/enforcement/v15_execution_gateway.py`

**Changes**:
1. Instantiate `PipeOrderEnforcer` in the gateway
2. Call `PolicyConfigGuard` at wave start
3. Enforce `RESULT_EMISSION_ALLOWED_LAYERS` check before any result emission
4. Emit `AggregateArtifact` on conditional flows

**Guardian tests**: Verify gateway enforces pipe order, rejects out-of-order steps, rejects RESULT from non-L2 layers.

---

#### Phase 7.3: CI Gates P3–P6

Extend the CI gate infrastructure to cover all 6 priority levels.

**New files**:
- `ops_scripts/ci/run_v15_p3_gate.py` — P3 (No Silent State Mutation)
- `ops_scripts/ci/run_v15_p4_gate.py` — P4 (Immutable Traceability)
- `ops_scripts/ci/run_v15_p5_gate.py` — P5 (Tokenized Authority)
- `ops_scripts/ci/run_v15_p6_gate.py` — P6 (Typed Boundaries)

Each gate:
1. AST-scans agents for the relevant contract consumption
2. Checks that the typed artifacts are emitted on correct flows
3. Produces evidence JSON
4. Fails on threshold violation

**Template** (modeled on existing `run_v15_p2_gate.py`):
```python
def main():
    evidence = collect_p3_evidence()  # AST scan for state mutation patterns
    result = evaluate_p3_gate(evidence)
    print(f"[P3-GATE] {'PASSED' if result else 'FAILED'}")
    return 0 if result else 1
```

---

### TIER 2 — Agent Wiring (Per-Agent Compliance)
**Priority**: P1 — the bulk of the work
**Risk**: Medium (touches agent internals)
**Estimated effort**: 3–5 sessions

#### Phase 8.1: Validator → Healer Pipe Wiring (§2)

Wire the top-priority agents (those in the P2 inventory — 28 runtime entrypoints) to use `SurgicalManifest` as exclusive execution input.

**Approach**: For each agent that has a `heal()` method:
1. Wrap validation output in `SurgicalManifest`
2. Pass through `PipeOrderEnforcer` (10-step sequence)
3. Check for `SignedModify` overrides at step 4
4. Emit `StaleWriteIncident` on hash mismatch
5. Increment circuit breaker on failure

**Priority agents** (from P2 inventory, 6 categories):
- Category A: `orchestrator_engine.py`, `NervousSystemAgent.py`, `security_level_config.py`
- Category B: `agent_engine.py`, `SubatomicHopAgent.py`, `SovereignActionPlaneAgent.py`
- Category C: `mission_runner.py` (3 modes)
- Category D: `tool_reliability_mixin.py` (with_retry)
- Category E: `execute_ssot.py`

**Diff sketch** (per agent validator):
```python
# BEFORE
violations = self._scan_violations(target)
for v in violations:
    self._heal_violation(v)

# AFTER
from agentic_core.L0_maintenance.types.v15_p2_types import SurgicalManifest
violations = self._scan_violations(target)
for v in violations:
    manifest = self._to_surgical_manifest(v)  # new method
    self._pipe_enforcer.validate_and_heal(manifest)  # via PipeOrderEnforcer
```

#### Phase 8.2: TokenCap & Budget Guard Wiring (§11)

Wire `TokenCapArtifact` and `PermsArtifact` emission before every LLM call.

**Target files**: All files that call LLM APIs:
- `agentic_core/L1_cognition/` — cognitive agents
- `agentic_core/L2_execution/reasoning/` — tool agents with LLM heal

**Diff sketch**:
```python
# BEFORE
response = llm_client.complete(prompt)

# AFTER
from agentic_core.L0_maintenance.types.v15_types import TokenCapArtifact, TokenGateResult
cap = TokenCapArtifact(
    trace_id=self._trace_id,
    policy_hash=self._policy_hash,
    budget_limit=self._budget,
    tokens_requested=len(prompt.split()),
    gate_result=TokenGateResult.ALLOW if len(prompt.split()) <= self._budget else TokenGateResult.DENY,
)
if cap.gate_result == TokenGateResult.DENY:
    raise BudgetExceeded(cap)
response = llm_client.complete(prompt)
```

#### Phase 8.3: Signal Dedup & Incident Emission (§5)

Wire `ErrorSignature` computation and `IncidentArtifact` emission in L6 observability agents.

**Target files**: `agentic_core/L6_observability/reasoning/`

**Changes**:
1. Compute `ErrorSignature` using semantic clock (not wall clock)
2. Deduplicate via SHA-256 before emitting
3. Emit `IncidentArtifact` with `correlation_hash`
4. Emit `SelfHealingTrigger` to L2 when appropriate

---

### TIER 3 — Advanced Protocols
**Priority**: P2 — required for full compliance but less blast radius
**Risk**: Medium-High (new runtime behaviors)
**Estimated effort**: 3–4 sessions

#### Phase 9.1: RAG Artifact Chain (§6.5)

Wire the full `RetrievalQuery → RetrievedChunks → RerankScores → CitationBundle` chain in L1/L4 agents.

**Target files**: Knowledge/cognition agents in `agentic_core/L1_cognition/` and `agentic_core/L4_state/`

#### Phase 9.2: Guardian Signing (§7)

Wire `SignatureEnclave` and `SignedGuardianArtifact` emission in guardian test infrastructure.

**Target files**:
- `tests/guardian/conftest.py` — add enclave fixture
- Guardian test output → emit `SignedGuardianArtifact` with `DeterministicTestEnclave`
- `ReplayGuardRecord` tracking in `v15_execution_gateway.py`

#### Phase 9.3: Human Escalation Protocol (§2.6, §2.7, §3.4, §3.5)

Wire `HashMismatchTracker` → `EvidencePack` → human review → `SignedModify` or `PolicyUpdateProposal` chain.

**Target**: Create `agentic_core/L0_maintenance/enforcement/v15_human_escalation.py`

#### Phase 9.4: Tiered Monitoring (§15.1–§15.3)

Wire `TieredVigilanceMonitor`, `CognitiveDiffBundle`, and `ForensicTraceBuffer` in L6 agents.

**Target files**: `agentic_core/L6_observability/reasoning/`

---

### TIER 4 — Full Compliance Hardening
**Priority**: P3 — polish and edge cases
**Risk**: Low (mostly additive checks)
**Estimated effort**: 2–3 sessions

#### Phase 10.1: Wall-Clock Elimination (§13.2)

AST-scan all agents for wall-clock usage in hash/signature/dedup paths. Replace with SemanticClock ticks.

**Tool**: `v15_p2_contracts.py::ast_scan_wall_clock()` already exists — run repo-wide, fix violations.

#### Phase 10.2: MRO Safety Mixin Verification (§8.3)

AST-verify that safety mixins appear LEFT of base classes in all 149 agents.

**Tool**: Discovery JSON `mro_chain` field already captures this — write a CI gate that checks ordering.

#### Phase 10.3: Read-Only Layer Enforcement (§12.3)

AST-verify that L0, L4, L6 agents cannot perform state mutation (no `write_text`, `mkdir`, `open(w)`, etc.).

**Tool**: Extend `v15_d_inventory_collect_full.py` side-effect detector to produce a per-layer mutation report.

#### Phase 10.4: Meta-Guardian 95% Coverage (§7.6)

Wire `meta_guardian_check()` (already exists in `v15_contracts.py`) into CI as a gating check.

---

## Dependency Graph

```
TIER 1 (Foundation)
  7.1 SovereignBaseAgent protocol ──┐
  7.2 Execution Gateway wiring ─────┤
  7.3 CI Gates P3–P6 ──────────────┘
         │
TIER 2 (Agent Wiring)
  8.1 Validator→Healer pipe ────────┐
  8.2 TokenCap/Budget guards ───────┤
  8.3 Signal dedup & incidents ─────┘
         │
TIER 3 (Advanced Protocols)
  9.1 RAG chain ────────────────────┐
  9.2 Guardian signing ─────────────┤
  9.3 Human escalation ────────────┤
  9.4 Tiered monitoring ────────────┘
         │
TIER 4 (Hardening)
  10.1 Wall-clock elimination ──────┐
  10.2 MRO safety verification ────┤
  10.3 Read-only layer enforcement ─┤
  10.4 Meta-Guardian 95% gate ──────┘
```

## Acceptance Criteria (per Tier)

| Tier | Gate | Threshold |
|------|------|-----------|
| TIER 1 | P0–P2 gates PASS + P3–P6 gates exist | All 6 gates green |
| TIER 2 | 28 P2 entrypoints emit typed artifacts | UNWIRED_ARTIFACTS = 0 |
| TIER 3 | Full artifact chain verified end-to-end | Integration test PASS |
| TIER 4 | `meta_guardian_check` ≥ 95% | CI gate enforced |

## Risk Mitigation

- **No behavior changes**: Each phase adds artifact emission/validation alongside existing logic, never replacing it
- **Feature flags**: All new enforcement gated by `V15_ENFORCEMENT` env var (existing pattern)
- **Incremental gates**: Each tier adds gates that pass before the next tier starts
- **Rollback safe**: Every phase is independently revertible (single commit per phase)

## Estimated Total Effort

| Tier | Sessions | Files Modified | New Tests |
|------|----------|---------------|-----------|
| TIER 1 | 2–3 | ~8 | ~40 |
| TIER 2 | 3–5 | ~30 | ~60 |
| TIER 3 | 3–4 | ~15 | ~40 |
| TIER 4 | 2–3 | ~10 | ~30 |
| **Total** | **10–15** | **~63** | **~170** |

---

## Key Insight

The gap analysis compliance is **much closer than initially assessed**. The typed artifact infrastructure (Layer A) and contract enforcement (Layer B) are nearly complete with 332 passing guardian tests. The primary work is **Layer D (runtime wiring)** — making the 149 active agents actually consume and emit the artifacts that already exist as typed definitions. This is a wiring exercise, not a design exercise.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

