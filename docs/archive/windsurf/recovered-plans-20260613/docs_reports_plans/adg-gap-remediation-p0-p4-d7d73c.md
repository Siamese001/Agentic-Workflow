# ADG Gap Remediation Plan — P0 through P4

ADG-evidence-backed remediation plan covering all 35 confirmed gaps (P0–P4, L0–L6), each with architecture design and concrete implementation tasks.

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


## Phasing Strategy

| Phase | Priority | Gaps | Rationale |
|---|---|---|---|
| **Phase 1** | P0 | 7 gaps | Safety-critical: ungoverned execution, absent traces, no replay |
| **Phase 2** | P1 | 7 gaps | Correctness: policy governance, context binding, coordination state |
| **Phase 3** | P2 | 7 gaps | Completeness: typed interfaces, audit trails, capability registry |
| **Phase 4** | P3 | 7 gaps | Observability: dashboarding, lifecycle governance, HITL |
| **Phase 5** | P4 | 7 gaps | Optimization: adaptive routing, learning loops, memory compression |

---

## P0 — Safety-Critical Gaps (7)

### P0-L0: Deterministic Request Routing

**ADG Evidence:** 0/366 L0 modules have `emits_replay_key`, `emits_determinism_digest`, `proposal_commits_routing`, or `guards_replay`. All 3 `emits_determinism_digest` edges are test-only.

**Design:** Introduce a `RoutingArtifact` dataclass emitted at each L0 decision point, carrying a determinism digest and replay key. Route decisions must pass through a `DeterministicRoutingGateway` that stamps and stores the artifact before forwarding.

**Implementation Tasks:**
- Create `agentic_core/L0_routing/artifacts/routing_artifact.py` — `RoutingArtifact(digest, replay_key, route_decision, timestamp)`
- Wire `emits_determinism_digest` + `emits_replay_key` into L0 routing entry points (e.g. `agentic_core/L0_routing/` dispatch modules)
- Add `guards_replay` linkage in `agentic_core/L0_routing/` to `agentic_core/runtime/execution_trace.py`
- CI check: any L0 module with `calls`/`routes_path` must have an upstream `emits_replay_key` or `proposal_commits_routing` edge

---

### P0-L1: Reasoning Traceability

**ADG Evidence:** 0/103 L1 modules emit `records_execution_trace` or `signs_execution_trace`. Only 1 `guards_replay` from L1 (`react_strategy.py`) — a type reference, not a call site.

**Design:** Every L1 reasoning step must emit a structured `ReasoningTrace` record via `agentic_core/runtime/execution_trace.py`. The existing `ExecutionTrace` symbol is present but unlinked from L1 call sites.

**Implementation Tasks:**
- Instrument L1 reasoning engines (e.g. modules in `agentic_core/L1_cognition/engines/`) to call `execution_trace.record()` at each step boundary
- Add `records_execution_trace` → `ExecutionTrace` edges from L1 modules (ADG will pick these up on next regeneration)
- Wire `signs_execution_trace` for authenticated reasoning outputs
- Add ADG invariant: L1 modules with `calls`/`reads_from` must link to at least one `records_execution_trace` target

---

### P0-L2: Guardrail Enforcement Before Actions

**ADG Evidence:** 358 exec edges (`calls`+`writes_to`) vs 1 `applies_guardrail` edge from L2. 99.7% of L2 execution surface ungated. L5→L2 `applies_guardrail` = 0. `execution_terminates_at_uwg` = 44 globally but only 1 from L2.

**Design:** All L2 `writes_to` and `calls` to external/state targets must route through `UniversalWriteGateway.py` which already exists but is underused. Define a mandatory `pre_execute_guardrail_check(context)` protocol enforced at the L2 boundary. L5 safety modules must register guardrail policies consumed by L2 at runtime.

**Implementation Tasks:**
- Audit `agentic_core/L2_execution/` entry points — every public `execute()` / `write()` / `call()` must invoke `UniversalWriteGateway` pre-check
- Add `applies_guardrail` edges from L2 execution modules to their guardrail check call sites
- Wire `validated_by_safety_plane` linkage: L2 exec → L5 policy check before state mutation
- Create `agentic_core/L2_execution/enforcement/guardrail_gate.py` as the canonical pre-execution interceptor
- CI ADG invariant: L2 modules with `writes_to` without `applies_guardrail` upstream = violation

---

### P0-L3: Agent Handoff Topology

**ADG Evidence:** 2 `agent_executes_agent` edges total, both resolve to `L_UNKNOWN` (dynamic `self.run_agent`, `main_orchestrator.run_agent`). 204 L3 modules. 0 `routes_through` from L3.

**Design:** Replace dynamic `self.run_agent()` dispatch with a typed `AgentHandoff` protocol carrying source agent, target agent identity, task context, and handoff timestamp. This makes handoffs statically traceable by the ADG.

**Implementation Tasks:**
- Define `agentic_core/L3_orchestration/contracts/agent_handoff.py` — `AgentHandoff(src, dst, context, timestamp)` typed dataclass
- Refactor `orchestrator_engine.py` and `recursive_orchestration_types.py` to emit `AgentHandoff` instead of bare `self.run_agent()`
- Add explicit `agent_executes_agent` edges resolvable to concrete agent modules (not `L_UNKNOWN`)
- Wire `routes_through` from orchestrator → target agent modules

---

### P0-L4: Unified Runtime State Authority

**ADG Evidence:** 0/142 L4 modules emit `snapshots_state`, `stamps_work_contract`, `freezes_context`, or `unfreezes_context`. `snapshots_state` = 1 globally (from `L_UNKNOWN`). L4 reads 1,827 sources and writes 50 targets with no unification.

**Design:** Introduce a `RunScopedStateAuthority` singleton per execution run, acting as the single ledger for all state reads/writes within L4. All L4 modules must route state access through it rather than directly.

**Implementation Tasks:**
- Create `agentic_core/L4_state/authority/run_scoped_state_authority.py` — provides `read(key)`, `write(key, val)`, `snapshot()`, `freeze()`, `unfreeze()`
- Migrate L4 state modules to use authority instead of direct store access
- Emit `stamps_work_contract` at run start, `snapshots_state` at checkpoints, `freezes_context`/`unfreezes_context` around critical sections
- ADG invariant: `writes_to` from L4 without passing through state authority = violation

---

### P0-L5: Policy Enforcement Coverage

**ADG Evidence:** 68 total `applies_guardrail` edges — 49 (72%) from `L_TEST`. L5 emits only 1. L5→L2 `applies_guardrail` = 0. 1,184 `reads_policy_state` but only 86 `references_policy_hash`. L5 invokes `eval` 136× without guardrails.

**Design:** L5 policy modules must become active enforcers, not passive readers. Define a `PolicyEnforcementPoint` contract that wraps every L5-originated action. The 136 `invokes_eval` from L5 must each have a `validated_by_safety_plane` pre-check.

**Implementation Tasks:**
- Create `agentic_core/L5_safety/enforcement/policy_enforcement_point.py` — decorator/context-manager wrapping L5 actions with policy hash verification
- Wrap all L5 `invokes_eval` / `invokes_dynamic` call sites with `enters_sandbox` + `applies_guardrail`
- Wire L5→L2 guardrail path: L5 policy registry must be consulted before L2 `writes_to` operations
- Add `references_policy_hash` to every L5 module that reads policy state (44 modules — add hash pinning)
- CI: `invokes_eval` from any prod layer without `applies_guardrail` upstream = blocker

---

### P0-L6: Cross-Layer Execution Trace Coverage

**ADG Evidence:** 5 of 7 core prod layers (L0, L1, L4, L5, L6) emit zero `records_execution_trace`. 7 prod-source trace edges all resolve to type definitions, not call sites. `triggered_telemetry` = 3 globally.

**Design:** `agentic_core/runtime/execution_trace.py` exists but is unlinked. Define a `TraceEmitter` mixin/decorator that every boundary-crossing module inherits, auto-emitting a trace record on entry/exit. L6 becomes the aggregator, not just a passive reader.

**Implementation Tasks:**
- Add `TraceEmitter` mixin to `agentic_core/runtime/execution_trace.py`
- Apply to L0 routing dispatch, L1 reasoning engines, L4 state authority, L5 policy enforcement points
- Wire L6 modules to consume and aggregate trace records — emit `triggered_telemetry` on aggregation
- Add `signs_execution_trace` to authenticated trace producers
- Target: `records_execution_trace` present in all 7 core prod layers (currently 2/7)

---

## P1 — Correctness Gaps (7)

### P1-L0: Routing Policy Governance

**ADG Evidence:** 4/366 modules reference policy hash. 0 `proposal_commits_routing`, `routes_through`, `routes_path`. L0 reads policy state (76) without committing to governance constraints.

**Design:** Routing decisions must be committed as `RoutingProposal` records that reference the governing policy hash before execution.

**Implementation Tasks:**
- Add `proposal_commits_routing` emission from L0 decision modules → policy hash node
- Require `reads_governed_config` (not just `reads_policy_state`) before routing dispatch — 3 current vs 366 needed
- Add `verifies_boundary` check at L0 exit points
- Expand `references_policy_hash` from 4 to cover all 366 L0 modules via shared routing policy base class

---

### P1-L1: Unified Reasoning Context

**ADG Evidence:** 0 `pulls_context`, `retrieves_via`, `stamps_work_contract`, `freezes_context`. 4 modules touch context retrieval (5 `embeds_into`). 1,494 `reads_from` without context binding.

**Design:** Introduce `ReasoningContextEnvelope` that travels with each L1 run, binding retrieval results, memory reads, and prompt state into a single immutable object per request.

**Implementation Tasks:**
- Create `agentic_core/L1_cognition/context/reasoning_context_envelope.py`
- Wire L1 reasoning modules to `pulls_context` and `stamps_work_contract` on envelope creation
- Add `freezes_context` before inference, `unfreezes_context` after — prevents mid-run state drift
- Link `gated_by_confidence` to envelope: low-confidence retrievals must be flagged before use

---

### P1-L2: Deterministic Execution Proof

**ADG Evidence:** 1 `records_execution_trace` from L2 = type definition only. 0 `signs_execution_trace`, `emits_determinism_digest`, `emits_replay_key`, `guards_replay`. 75 exec modules, 0 replay-instrumented.

**Design:** Every L2 execution event must produce a signed execution proof (digest + replay key) stored in the execution trace ledger before the action is considered complete.

**Implementation Tasks:**
- Add `emits_determinism_digest` + `emits_replay_key` to L2 execution entry points
- Wire `signs_execution_trace` from L2 modules to `agentic_core/runtime/execution_trace.py`
- Add `guards_replay` linkage: replay guard must be checked before re-executing any L2 action
- ADG invariant: `writes_to` from L2 without `emits_replay_key` upstream = violation

---

### P1-L3: Run-Scoped Coordination State

**ADG Evidence:** 0/204 modules emit `stamps_work_contract`, `freezes_context`, `snapshots_state`, or `observes_runtime_state`. 13 `reads_runtime_state` but 0 write-back coordination signals.

**Design:** L3 orchestration must maintain a `WorkCoordinationBundle` per multi-agent run — a shared case file that all participating agents read from and write to.

**Implementation Tasks:**
- Create `agentic_core/L3_orchestration/coordination/work_coordination_bundle.py`
- Emit `stamps_work_contract` at orchestration start; `snapshots_state` at each agent completion
- Wire `observes_runtime_state` from L3 orchestrator to runtime state store
- All `agent_executes_agent` dispatches must reference the active coordination bundle

---

### P1-L4: Memory System Fragmentation

**ADG Evidence:** 297 memory-named nodes, 19 distinct write targets from L4, 0 `pulls_context`/`retrieves_via`/`gated_by_confidence`. 84 modules reading memory, 20 writing to 19 separate targets.

**Design:** Introduce a `UnifiedMemoryFacade` in L4 that presents a single retrieval and storage interface backed by the existing disparate stores. All 297 memory-named nodes route through it.

**Implementation Tasks:**
- Create `agentic_core/L4_state/memory/unified_memory_facade.py` — wraps semantic memory, replay bundles, retrieval stores
- Wire `retrieves_via` and `pulls_context` through facade (currently 0 from L4)
- Add `gated_by_confidence` before facade returns low-confidence results
- `stores_embedding` and `embeds_into` from L4 must go through facade (currently only 1 each)

---

### P1-L5: Tool Safety Governance

**ADG Evidence:** L5 `invokes_eval` 136×, `invokes_dynamic` 29×. 247 global tool-invoking modules, only 5 with `applies_guardrail` (2%). `validated_by_safety_plane` = 0 from L5.

**Design:** All tool invocations (eval, dynamic dispatch, external HTTP) must pass through a `ToolSafetyGate` that validates authorization before invocation. L5 is both the largest tool-invoker and the safety layer — this is the highest-priority P1 item.

**Implementation Tasks:**
- Create `agentic_core/L5_safety/gates/tool_safety_gate.py` — wraps `invokes_eval`, `invokes_dynamic`, `external_http_call` with `applies_guardrail` + `validated_by_safety_plane`
- Wrap all 136 `invokes_eval` from L5 with `enters_sandbox`
- Add `execution_terminates_at_uwg` path for L5 tool calls that mutate state
- CI: any `invokes_eval`/`invokes_dynamic`/`external_http_call` without `applies_guardrail` = blocker

---

### P1-L6: Evaluation Signal Integration

**ADG Evidence:** 0/47 L6 modules linked to `records_execution_trace`, `triggered_telemetry`, or `validated_by_llm_gateway`. All 40 `scores_groundedness` edges are test-only.

**Design:** L6 evaluation modules must consume live runtime traces and emit graded evaluation signals. Wire `scores_groundedness` and `validated_by_llm_gateway` from L6 to production execution paths.

**Implementation Tasks:**
- Wire L6 grader modules to consume `agentic_core/runtime/execution_trace.py` (currently 0 L6→trace links)
- Add `scores_groundedness` emission from L6 to production reasoning outputs
- Wire `validated_by_llm_gateway` from L6 to L2/L3 execution outputs
- `gated_by_confidence` from L6 should gate L1 reasoning outputs before they proceed

---

## P2 — Completeness Gaps (7)

### P2-L0: Routing Telemetry
**ADG Evidence:** 1/366 L0 modules emit telemetry. 0 `records_execution_trace`, `emits_drift_alert`.

**Design:** Routing dispatch must emit a `RoutingTelemetryEvent` on each decision.
**Tasks:** Add `triggered_telemetry` emission from L0 dispatch modules; wire `routes_through` / `routes_path` to telemetry sink; add `emits_drift_alert` when routing deviates from baseline.

---

### P2-L1: Reasoning Evaluation
**ADG Evidence:** 0 evaluation edges of any kind from 103 L1 modules. `scores_groundedness` + `validated_by_llm_gateway` test-only.

**Design:** L1 reasoning outputs must be scored via an evaluation gate before returning results.
**Tasks:** Wire `gated_by_confidence` from L1 reasoning engines; add `validated_by_llm_gateway` on L1 outputs; link L1 → L6 grader modules via `scores_groundedness`.

---

### P2-L2: Typed Tool Interfaces
**ADG Evidence:** 128 `implements` (typed inheritance exists); only 2 `certifies_envelope`, 0 `validated_by_registry`. 89 modules execute generically.

**Design:** Tool call sites must use typed `ToolContract` envelopes certifying input/output schemas.
**Tasks:** Extend `certifies_envelope` from 2 to cover all L2 tool-invoking modules; add `validated_by_registry` checks before execution; use `stamps_work_contract` per tool invocation.

---

### P2-L3: Agent Capability Registry
**ADG Evidence:** 19 registry/capability-named L3 nodes; 0 `issues_capability_token`, `grants_resource`, `validated_by_registry` from L3. Global `issues_capability_token` = 5, all from `L_TEST`/`L_TOOLS`.

**Design:** Build a live capability registry in L3 that maps agents to capabilities, with tokens issued at routing time.
**Tasks:** Activate `issues_capability_token` emission from L3 agent registry; wire `grants_resource` from registry to agent dispatch; add `validated_by_registry` check before `agent_executes_agent`.

---

### P2-L4: State Versioning
**ADG Evidence:** 27 version/lineage/snapshot-named L4 nodes; 0/142 modules emit any versioning signal (`snapshots_state`, `stamps_work_contract`, `compares_proof`, `packages_diff`).

**Design:** State writes must produce versioned artifacts with lineage metadata.
**Tasks:** Wire `snapshots_state` on L4 state authority writes; add `compares_proof` before state merges; implement `packages_diff` for state delta logging; use `stamps_work_contract` to anchor version identity.

---

### P2-L5: Safety Audit Trails
**ADG Evidence:** 0/608 L5 modules emit any audit signal. `signs_execution_trace` = 21, `hard_fails_untranscripted` = 6 — all test-only.

**Design:** Every L5 safety decision must produce a signed audit record. Hard failures must be transcripted.
**Tasks:** Add `signs_execution_trace` to L5 policy enforcement point; emit `hard_fails_untranscripted` on L5 hard-fail paths; wire `certifies_envelope` to safety decisions; add `registers_antipattern` for detected violations.

---

### P2-L6: Performance Metrics
**ADG Evidence:** 3/47 L6 modules have wall-clock awareness. 0 structured metric emission (`triggered_telemetry`, `emits_drift_alert`, `scores_groundedness`) from L6.

**Design:** L6 must emit structured performance metrics on every workflow pass.
**Tasks:** Wire wall-clock measurements (already present) into `triggered_telemetry` emission; add `emits_drift_alert` for latency/throughput anomalies; expose `scores_groundedness` as a live performance signal.

---

## P3 — Observability Gaps (7)

### P3-L0: Routing Capacity Governance
**ADG Evidence:** 30 capacity-named nodes; 0/366 emit `gated_by_confidence`, `forces_stall`, `vigilance_reroute`. 51 `reads_runtime_state` (capacity data accessible but unused).

**Design:** Add capacity enforcement layer reading runtime load state and applying `forces_stall` / `vigilance_reroute` when thresholds exceeded.
**Tasks:** Wire `gated_by_confidence` to L0 routing decisions under load; implement `forces_stall` when capacity limits hit; add `vigilance_reroute` for load-based alternative routing paths.

---

### P3-L1: Multi-Step Reasoning Planning
**ADG Evidence:** 45 plan/chain/step/react-named L1 nodes (structural vocabulary present); 0 planning artifacts emitted (`generates_prompt`, `stamps_work_contract`, `gated_by_confidence`).

**Design:** L1 planning nodes must emit a `ReasoningPlan` artifact before execution begins.
**Tasks:** Wire `generates_prompt` from L1 plan nodes to prompt templates; emit `stamps_work_contract` for each reasoning plan; add `gated_by_confidence` before plan execution proceeds.

---

### P3-L2: Execution Observability
**ADG Evidence:** 1/75 exec modules observable (1.3%). 46 `uses_wall_clock` but uncoupled from emission.

**Design:** Couple wall-clock measurements to structured `ExecutionTelemetryEvent` emission at every L2 boundary.
**Tasks:** Wrap L2 exec entry points with `triggered_telemetry` emission; link `uses_wall_clock` → `records_execution_trace`; target 75/75 exec modules instrumented.

---

### P3-L3: Workflow Visualization
**ADG Evidence:** 149 workflow/dag/plan-named L3 nodes; 0 `stamps_work_contract`, `snapshots_state`, `packages_diff`. 935 workflow nodes resolve to `L_UNKNOWN` (dynamic dispatch).

**Design:** L3 must emit a `WorkflowGraphSnapshot` at each orchestration state transition, making topology statically observable.
**Tasks:** Add `snapshots_state` at each workflow stage transition; emit `packages_diff` for workflow delta; reduce `L_UNKNOWN` resolution by replacing dynamic dispatch with typed `AgentHandoff`; add `observes_runtime_state` from L3 orchestrator.

---

### P3-L4: State Lifecycle Governance
**ADG Evidence:** 0 lifecycle-named nodes AND 0 lifecycle signal edges — the most complete gap absence across all 35 gaps assessed. 1,827 `reads_from`, 50 `writes_to` with no eviction/expiry concept.

**Design:** Add `StateLifecyclePolicy` attached to every state object defining TTL, eviction rules, and archival triggers.
**Tasks:** Create `agentic_core/L4_state/lifecycle/state_lifecycle_policy.py`; emit `freezes_context` on stale state; add eviction/archival triggers (`forces_stall` on lifecycle boundary); wire `reads_policy_state` to lifecycle policy check before every state read.

---

### P3-L5: Escalation to Human Oversight
**ADG Evidence:** 76 HITL/human-oversight-named L5 nodes; 0/608 L5 modules emit `escalates_to_human`, `requires_human_review`, `forces_stall`, `hard_fails_untranscripted`. All HITL signals are test-only.

**Design:** Activate HITL trigger conditions in L5 policy enforcement point — uncertain decisions above a confidence threshold must route to human review.
**Tasks:** Wire `escalates_to_human` from L5 policy enforcement point; add `requires_human_review` for policy edge cases; implement `forces_stall` when HITL is pending; connect to existing HITL-named modules (76 of them currently unlinked).

---

### P3-L6: Observability Dashboarding
**ADG Evidence:** 34 dashboard/monitor-named L6 nodes; L6 profile is entirely passive (`reads_from`=589, 0 outbound aggregation signals). `emits_drift_alert` global = 7, all test-only.

**Design:** L6 must become an active aggregator — consuming trace/metric data and emitting rolled-up signals upward.
**Tasks:** Wire `emits_drift_alert` from L6 anomaly detection; add `triggered_telemetry` on aggregation completion; connect 34 dashboard-named nodes to live `records_execution_trace` consumers; add `reads_runtime_state` from L6 (currently 0).

---

## P4 — Optimization Gaps (7)

### P4-L0: Adaptive Routing Optimization
**ADG Evidence:** 51 `reads_runtime_state` (historical data accessible); 0 `commits_optimization`, `builds_dpo_batch`, `gated_by_confidence` from L0.

**Tasks:** Add feedback loop: L0 routing outcomes → `produces_preference_pair` → `builds_dpo_batch`; wire `commits_optimization` when routing performance improves; add `gated_by_confidence` on routing decisions using historical success rates.

---

### P4-L1: Knowledge Attribution Optimization
**ADG Evidence:** 19 provenance-named L1 nodes; `compares_proof` (4) + `scores_groundedness` (40) entirely test-only. 1,494 `reads_from` with no attribution.

**Tasks:** Add `compares_proof` at L1 reasoning outputs vs. ground truth; wire `scores_groundedness` from L6 graders back to L1 output nodes; add `retrieves_via` typed attribution edges for all L1 knowledge reads.

---

### P4-L2: Execution Efficiency Optimization
**ADG Evidence:** 46 `uses_wall_clock` (timing exists); 0 `commits_optimization`, `gated_by_confidence`, `builds_dpo_batch`. 53 optim-named nodes unused.

**Tasks:** Feed wall-clock measurements into `commits_optimization` signals; add `builds_dpo_batch` for slow execution paths (training signal); wire `gated_by_confidence` to gate inefficient execution patterns.

---

### P4-L3: Workflow Learning Optimization
**ADG Evidence:** `L_SL`/`L_PG` → L3 = 0 edges. L3 → `L_SL`/`L_PG` = 1 edge. System learning (`L_SL` 264 modules, `L_PG` 84 modules) structurally disconnected from orchestration.

**Tasks:** Add `imports`/`calls` from L3 orchestration to `L_SL` meta-learning modules; wire `produces_preference_pair` from L3 workflow outcomes; add `commits_optimization` when workflow patterns improve; establish bidirectional L3↔L_SL/L_PG edges (currently near-zero).

---

### P4-L4: Memory Compression Strategy
**ADG Evidence:** 2 compress-named nodes; 0 `chunks_into`, `commits_optimization`, `builds_dpo_batch` from L4. Pure accumulation: `reads_from`=1,827, `writes_to`=50, no compaction.

**Tasks:** Implement compaction strategy in `UnifiedMemoryFacade`; emit `chunks_into` on summarization; wire `commits_optimization` after successful compaction; add `builds_dpo_batch` from long-term memory patterns for training signal.

---

### P4-L5: Policy Adaptation Loop
**ADG Evidence:** 44 `reads_policy_state` (consuming); 0 `observes_policy_state`, `registers_antipattern`, `emits_drift_alert`, `commits_optimization` from L5. 61 adapt-named nodes unused.

**Tasks:** Wire `observes_policy_state` from L5 safety monitoring to incident log; add `registers_antipattern` on detected violation patterns; emit `emits_drift_alert` for policy drift; feed incidents into `commits_optimization` for policy update proposals.

---

### P4-L6: Observability-Driven Optimization
**ADG Evidence:** L6→`L_SL`/`L_PG`/`L_RUNTIME` = 1 edge. `builds_dpo_batch` global = 43 — 38 test-only, 0 from L6. `commits_optimization` global = 2, test-only.

**Tasks:** Wire L6 telemetry aggregation → `builds_dpo_batch` for learning signal; add `commits_optimization` from L6 anomaly detection; increase L6→`L_SL` edges from 1 to cover all L6 performance-measurement modules.

---

## ADG Invariant Checklist (CI Enforcement)

Add these ADG-scan checks to the CI pipeline as gap remediation progresses:

| Check | Blocker? | Target Phase |
|---|---|---|
| L2 `writes_to` without upstream `applies_guardrail` | **Yes** | Phase 1 |
| L5 `invokes_eval`/`invokes_dynamic` without `applies_guardrail` | **Yes** | Phase 1 |
| L0 routing dispatch without `emits_replay_key` | Yes | Phase 1 |
| L1 reasoning module without `records_execution_trace` | Yes | Phase 1 |
| `agent_executes_agent` resolving to `L_UNKNOWN` | Warning | Phase 2 |
| L4 `writes_to` without `stamps_work_contract` ancestry | Warning | Phase 2 |
| L5 `reads_policy_state` without `references_policy_hash` | Warning | Phase 2 |
| L6 module with 0 outbound non-import edges | Info | Phase 3 |

---

## Key Metrics to Track (ADG Re-scan After Each Phase)

| Metric | Baseline | P0 Target | P1 Target | Full Target |
|---|---|---|---|---|
| `applies_guardrail` prod (non-test) | 19 | 200+ | 350+ | 500+ |
| `records_execution_trace` prod layers | 2/7 | 7/7 | 7/7 | 7/7 |
| `agent_executes_agent` resolves to known node | 0/2 | 2/2 | — | — |
| `emits_replay_key` from L0 | 0 | 50+ | — | — |
| L5 `invokes_eval` with `enters_sandbox` | 0/136 | 136/136 | — | — |
| `scores_groundedness` from prod (non-test) | 0/40 | — | 20+ | 40+ |
| `builds_dpo_batch` from prod (non-test) | 5/43 | — | — | 25+ |

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

