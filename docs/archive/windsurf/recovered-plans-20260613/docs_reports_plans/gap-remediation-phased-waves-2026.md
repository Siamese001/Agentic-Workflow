# P0–P4 Gap Remediation: Phased Wave Plan

**Generated:** 2026-03-14
**Redis snapshot:** `adg:meta` timestamp=03132026_1424, ingested_at=03142026
**ADG totals:** 8,234 nodes · 224,969 edges · sqlite `adg_indexed_03142026_0655.sqlite`
**Sources:** Live Redis hot-cache queries + RCA analysis + ChatGPT reconciliation

---

## Baseline Numbers (live from Redis `adg:snapshot.graph_plane_counts`)

| Relation | Count | Significance |
|---|---|---|
| `calls` | 18,499 | Primary execution surface |
| `invokes_eval` | 501 | Evaluation dispatch surface |
| `invokes_dynamic` | 536 | Opaque dynamic calls |
| `invokes_getattr_dynamic` | 2,978 | **Largest determinism risk** |
| `invokes_importlib` | 166 | Runtime module loading |
| **Total execution surface** | **22,514** | Denominator for all ratios |
| `writes_to` | 4,875 | **Ungoverned writes** |
| `writes_through` | 80 | Governed UWG writes |
| **Ungoverned write ratio** | **98.4%** | Critical |
| `applies_guardrail` | 68 | 0.30% of execution surface |
| `records_execution_trace` | 64 | 0.28% of execution surface |
| `execution_terminates_at_uwg` | 44 | UWG termination edges |
| `agent_executes_agent` | 2 | Visible orchestration topology |
| `reads_policy_state` | 1,317 | **Policy reads only — NOT enforcement** (reads ≠ gates) |
| `emits_replay_key` | 2 | Replay proof artifacts |
| `emits_determinism_digest` | 3 | Determinism proof artifacts |
| `uses_wall_clock` | 884 | Non-determinism source |
| `uses_random` | 59 | Non-determinism source |
| `dead_imports` | 4,409 | Structural debt |
| `antipattern` | 1,528 | Catalogued violations |
| `registers_antipattern` | 11 | Detection hooks wired |
| `unresolved_count` | 412 | Phantom imports |
| `reads_runtime_state` | 459 | State reads (fragmented) |
| `observes_runtime_state` | 3 | Structured observation edges |
| `snapshots_state` | 1 | State checkpoint edges |
| `signs_execution_trace` | 21 | Trace signing infra exists |
| `stamps_work_contract` | 18 | Work contract stamping |
| `decorated_by` | 16,771 | Decoration without enforcement |
| `orchestrates_healing` | 75 | Healing orchestration edges |
| `dispatches_healing_run` | 71 | Healing dispatch edges |
| `heals` | 2 | **Actual heal outcomes** |
| `escalates_to_human` | 15 | HITL wiring |
| `proposal_commits_routing` | 42 | Routing decisions recorded |
| `validated_by_safety_plane` | 18 | Safety plane validation |
| `validated_by_llm_gateway` | 30 | LLM gateway validation |

---

## RCA Digest: Why Every Prior Attempt Failed

| Root Cause | ADG Evidence | Failure Mode |
|---|---|---|
| Write path never unified | `writes_to:4875` vs `writes_through:80` | UWG was opt-in; existing code never migrated |
| Dynamic dispatch exploded | `invokes_getattr_dynamic:2978` vs `agent_executes_agent:2` | `getattr` calls are invisible to the ADG; topology cannot be governed |
| Governance added as decoration | `decorated_by:16771` but `applies_guardrail:68` | Annotations record membership; they do not gate execution |
| Non-determinism never blocked | `uses_wall_clock:884` vs `emits_determinism_digest:3` | Determinism was instrumented in 3 places then abandoned |
| ADG was advisory, not enforcement | `dead_imports:4409` + `antipattern:1528` merged continuously | CI scans but does not block |
| Healing infra consumed energy budget | `orchestrates_healing:75` but `heals:2` | Scaffolding is satisfying to build; closed loops are not |
| P4 work was entirely skipped | Zero P4 changes in all prior waves | P4 is perpetually deprioritized in favour of P0/P1 |

**Core principle violated in all prior attempts:** Opt-in governance never becomes structural enforcement. Every wave below enforces the inverse: **the ungoverned path must require more effort than the governed path.**

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | [Tokens |]
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**


---



```
Wave 0  ── ADG becomes a hard CI blocker            (no new debt admitted)          [prerequisite]
Wave 1  ── Write path sovereignty                   (UWG universalisation)          [structural]
Wave 2  ── Dynamic dispatch → typed registry        (orchestration topology)        [structural]
Wave 3  ── Pre-execution guardrail enforcement      (chokepoint wiring)             [structural]
Wave 4  ── Deterministic time/random injection      (replay proof)                  [coverage]
Wave 5  ── Execution trace wiring                   (breadth expansion)             [coverage]
Wave 6  ── Unified runtime state authority          (state ledger)                  [coverage]
Wave 7  ── Structural debt burndown                 (P4: dead imports + antipatterns)[cleanup]
```

Waves 0–3 are **structural prerequisite** waves — no coverage wave begins until its structural predecessor's ADG gate passes.
Waves 4–6 are **coverage expansion** waves that piggyback on the chokepoints created in 1–3.
Wave 7 is **cleanup** — explicitly the wave that was 100% skipped in all prior implementations.

---

## Wave 0: ADG Hard CI Gate

**Addresses:** ADG advisory-only gap (root cause #5 above)
**ADG baseline:** `dead_imports:4409`, `antipattern:1528`, `writes_to` growing unchecked
**Why first:** Every subsequent wave is undermined if new violations can be merged alongside fixes.

### Deliverables

1. **`adg-invariant-scan.yml` → hard-fail thresholds**
   Add `--fail-on dead_imports_delta > 0` and `--fail-on antipattern_delta > 0`.
   Current counts become immutable ceilings. Any PR raising either count fails CI.

2. **`writes_to` delta gate**
   Any PR adding a `writes_to` edge without a matching `writes_through` increase fails.
   Stops the 98.4% ungoverned write ratio from worsening during Wave 1.

3. **`invokes_getattr_dynamic` freeze at 2,978**
   Any PR adding getattr-based dispatch must add a typed `agent_executes_agent` edge or fail.

4. **`dead_imports` freeze baseline = 4,409**
   Record in `ops_scripts/ci/_analyse_ssot_violations.py`.

5. **`antipattern` freeze baseline = 1,528**
   Any PR registering a new antipattern without a companion removal fails.

### Acceptance Gate
```
CI: dead_imports_delta <= 0 per PR
CI: antipattern_delta <= 0 per PR
CI: writes_to_delta <= 0 unless writes_through_delta > 0
CI: invokes_getattr_dynamic_delta <= 0 unless agent_executes_agent_delta > 0
```

### Derisking
Run in **warn-only** mode for one sprint before switching to hard-fail. Measure false-positive rate.

---

## Wave 1: Write Path Sovereignty (UWG Universalisation)

**Addresses:** L4 P0 Unified Runtime State Authority, L2 P0 Execution Core
**ADG baseline:** `writes_to:4875` vs `writes_through:80` = **98.4% ungoverned**
**Closes:** L4 P0, L2 P0 (partial), L4 P1 State Lifecycle Governance

### Why Wave 1

Every other gap depends on writes being governed. Trace signing, policy enforcement, and state snapshots are meaningless if the underlying writes bypass the audit trail. UWG is the foundation — nothing in Waves 5 or 6 is reliable without it.

### Deliverables

1. **UWG import enforcement rule**
   Any module with a `writes_to` edge not in the UWG allowlist fails CI.
   Allowlist starts empty — modules must explicitly register with justification.
   Extend `ops_scripts/ci/_analyse_ssot_violations.py`.

2. **Batch migration: L_APP layer (1,324 modules)**
   `apps_lic`, `apps_rg`, `apps_exec`, `apps_rfp`, `apps_research` — highest write surface, lowest blast radius.
   Extend existing `ops_scripts/general/_patch_execute_ssot_routing.py` for this migration.

3. **Batch migration: L3 orchestrators (215 modules)**
   Direct orchestrator writes are highest-risk bypass. All state commits from L3 must route through UWG.

4. **Batch migration: L0 routing (372 modules)**
   Routing decisions that write policy state must be governed.

5. **`execution_terminates_at_uwg` expansion**
   Current: 44. Target: ≥200. All execution paths producing durable state must terminate at UWG.

6. **`snapshots_state` expansion**
   Current: 1. Wire one snapshot per L3 orchestration run into existing `UniversalWriteGateway.py`. Target: ≥10.

### Acceptance Gate
```
writes_through / (writes_through + writes_to) >= 0.80
execution_terminates_at_uwg >= 200
snapshots_state >= 10
```

### Derisking
- Migrate in sublayer order: L_APP → L3 → L0 (smallest blast radius first)
- Each sublayer migration ships with regression test proving identical observable output
- Feature flag: `UWG_ENFORCEMENT_MODE = warn | enforce` — one sprint in `warn` per sublayer before promoting

---

## Wave 2: Dynamic Dispatch → Typed Agent Registry

**Addresses:** L3 P0 Agent Handoff Topology, L3 P1 Agent Capability Registry
**ADG baseline:** `invokes_getattr_dynamic:2978` + `invokes_dynamic:536` vs `agent_executes_agent:2`
**Closes:** L3 P0 orchestration topology, L3 P1 capability registry, L0 P1 routing policy governance (partial)

### Why Wave 2

Guardrails (Wave 3) and traces (Wave 5) both require a visible call graph. You cannot place a guardrail before a call you cannot see. `invokes_getattr_dynamic:2978` means 2,978 edges exist that governance cannot reason about.

### Deliverables

1. **`AgentDispatchRegistry` — single SSOT**
   New module in `agentic_core/L3_orchestration/`.
   `registry.dispatch(agent_name, method, *args)` produces typed `agent_executes_agent` edges.
   Starts as a shim: internally calls `getattr(instance, method)(*args)` — no semantic change, new graph visibility.

2. **Replace top-20 `invokes_getattr_dynamic` hotspots first**
   Fan-out analysis from Redis: `execute_ssot.py` (fan-out 1,010) and `static_scanner.py` (fan-out 798) are top sources.
   Converting these two alone reduces `invokes_getattr_dynamic` by ~600.

3. **`invokes_importlib:166` audit**
   Each `importlib`-based dispatch is a dynamic agent load. Replace with registry pre-registration where target is known at startup.

4. **Capability token integration**
   `issues_capability_token:5` exists but is not wired to dispatch. All registry dispatches must require a valid capability token. Target: `issues_capability_token >= 20`.

5. **`agent_executes_agent` target: ≥50**
   Current: 2. Converting the top orchestrators should surface ≥50 typed handoff edges, making L3 topology visible in the ADG for the first time.

### Acceptance Gate
```
agent_executes_agent >= 50
invokes_getattr_dynamic <= 2,000  (reduction of ~33%)
invokes_importlib <= 80           (reduction of ~50%)
issues_capability_token >= 20
```

### Derisking
- Registry shim preserves `getattr` semantics internally — zero behaviour change during transition
- Hard cutover (remove getattr fallback) only after acceptance gate passes and full test suite green
- ADG re-ingest after every PR to verify edge counts move in correct direction

---

## Wave 3: Pre-Execution Guardrail Enforcement

**Addresses:** L2 P0 Guardrail Enforcement Before Actions, L5 P1 Tool Safety (corrected to OPEN)
**ADG baseline:** `applies_guardrail:68` vs 22,514 execution surface = **0.30%**
**Closes:** L2 P0, L5 P1 Tool Safety, L5 P0 Policy Enforcement (enforcement half)

### Why Wave 3 requires Waves 1 + 2 first

- Guardrails placed in front of `invokes_getattr_dynamic` are structurally impossible — the call is invisible
- UWG (Wave 1) creates the write chokepoint; guardrail must fire before that chokepoint
- Registry dispatch (Wave 2) creates the call chokepoint; guardrail hooks into the registry

### Deliverables

1. **`authorize_and_execute()` mandatory guardrail pre-check**
   `execution_terminates_at_uwg:44` shows the chokepoint exists. Extend `agentic_core/L2_execution/` to require a synchronous, fail-closed guardrail check before every invocation.
   No guardrail resolution = hard fail (not pass-through).

2. **Guardrail hook in `AgentDispatchRegistry.dispatch()`**
   All Wave 2 registry calls wrap with a guardrail pre-check. Single injection point covers all typed agent handoffs.

3. **L5 cross-path safety guard for all execution paths**
   `validated_by_safety_plane:18` — extend to all four execution paths (A/B/C/D).
   Currently only some paths hit safety plane validation.

4. **`reenters_safety` expansion**
   Current: 3. Any guardrail failure must produce a `reenters_safety` edge. Target: ≥30.

5. **CI guardrail coverage gate**
   `applies_guardrail / calls >= 0.10` minimum. Fails if coverage drops below threshold on any PR.

### Acceptance Gate
```
applies_guardrail >= 500
applies_guardrail / calls >= 0.10
reenters_safety >= 30
validated_by_safety_plane >= 50
```

### Derisking
- Guardrail check starts in `warn` mode: logs violation, does not block
- Switch to `enforce` mode sublayer by sublayer: L3 → L_APP → L0
- Each sublayer switch requires 48-hour soak in `warn` with zero new violations before promoting

---

## Wave 4: Deterministic Time and Random Injection

**Addresses:** L0 P0 Deterministic Request Routing, L2 P1 Deterministic Execution Proof
**ADG baseline:** `uses_wall_clock:884` + `uses_random:59` vs `emits_determinism_digest:3` + `emits_replay_key:2`
**Closes:** L0 P0 replay proof, L2 P1 deterministic execution proof, L0 P2 routing telemetry

### Deliverables

1. **`ClockProvider` / `RandomProvider` dependency injection**
   Extend existing `agentic_core/L2_execution/determinism.py`.
   - `ClockProvider.now()` replaces all `datetime.now()` / `time.time()` calls
   - `RandomProvider.randint()` replaces all `random.*` calls
   Both injectable: tests inject `FrozenClock`; production injects `WallClock` that records value into trace context.
   `patches_time:20` exists in tests already — extend this pattern to production.

2. **Top-50 `uses_wall_clock` hotspots first**
   Priority: modules that also have `routes_path` or `proposal_commits_routing` edges.
   These are routing decision modules where non-determinism directly poisons replay.

3. **`emits_replay_key` expansion**
   Current: 2. Every L0 routing decision must emit a replay key.
   Wire into existing `TraceID + PolicyHash` assignment in L0 routing. Target: ≥50.

4. **`emits_determinism_digest` expansion**
   Current: 3. Every L3 orchestration run completion emits a determinism digest covering: inputs, routing decision, tool calls, outputs. Target: ≥20.

5. **Replay harness**
   Takes any `emits_replay_key` artifact, re-executes the trace, compares outputs.
   Target: harness covering ≥10 execution paths with verified deterministic output.

6. **`seeds_rng` discipline**
   `seeds_rng:14` but `uses_random:59`. All random usage must be seeded from trace context, not from `os.urandom` or uncontrolled entropy.

7. **`invokes_getattr_dynamic` determinism gate (separate from W2 topology gate)**
   W2 addresses `invokes_getattr_dynamic` as a *topology* problem. Wave 4 addresses it as a *determinism* problem: any remaining getattr-dispatched call that also touches `uses_wall_clock` or `uses_random` is a non-deterministic, invisible call — the worst combination. ADG query: modules with both `invokes_getattr_dynamic` fan-out AND `uses_wall_clock` edges must be prioritised in the ClockProvider injection sweep. Per ChatGPT reconciliation: **Dynamic dispatch determinism risk is a standalone major gap**, not a sub-item of orchestration topology.

### Acceptance Gate
```
emits_replay_key >= 50
emits_determinism_digest >= 20
uses_wall_clock <= 584  (reduction of 300 from 884)
replay harness covers >= 10 execution paths with verified deterministic output
# ChatGPT standalone gate: dynamic dispatch determinism
modules with (invokes_getattr_dynamic AND uses_wall_clock) = 0  [full closure target]
```

### Derisking
- `ClockProvider` starts as thin wrapper: `WallClock.now()` returns `datetime.now()` but appends to trace context
- No behavioural change initially; determinism guarantee added by switching to `FrozenClock` in targeted execution contexts
- No replay harness until `emits_replay_key >= 10` — prevents building test infrastructure against a non-existent signal

---

## Wave 5: Execution Trace Wiring

**Addresses:** L1 P0 Reasoning Traceability, L6 P0 Cross-Layer Execution Trace Coverage
**ADG baseline:** `records_execution_trace:64` on 22,514 execution surface = **0.28%**
**Closes:** L1 P0, L6 P0, L2 P1 proof edges, L6 P1 evaluation signal integration

### Why Wave 5 benefits directly from Waves 1–3

The trace signing/stamping infrastructure already exists (`signs_execution_trace:21`, `stamps_work_contract:18`). **However, infrastructure presence ≠ operational maturity.** These 21 signing edges and 18 stamping edges are design artifacts — they are not being invoked across the execution surface (`records_execution_trace:64` on 22,514 surface = 0.28%). Per the ChatGPT reconciliation, the trace pipeline should be classified as **OPEN / early-partial**, not mature-partial. The gap is call-site wiring breadth, not design. Waves 2 and 3 create exactly two chokepoints (`AgentDispatchRegistry.dispatch()` and `authorize_and_execute()`) where a single trace record injection covers the majority of the execution surface.

### Deliverables

1. **`TraceContext.record()` in `authorize_and_execute()` and registry dispatch**
   Two injection points. All capability calls and all registry-routed agent calls emit a trace record.
   Existing `signs_execution_trace:21` and `stamps_work_contract:18` infrastructure is reused.

2. **`hard_fails_untranscripted` enforcement**
   Current: 6. Any execution that completes without a trace record produces a `hard_fails_untranscripted` edge.
   Makes missing traces structurally visible in ADG rather than silently absent. Target: ≥50.

3. **`transcripts_response` expansion**
   Current: 10. All `SovereignLLMGateway` responses must be transcripted.
   Target: ≥100 (covers all LLM call sites).

4. **L6 evaluation signal tie-in**
   `invokes_eval:501` — evaluation is invoked but results are not fed back into traces.
   Wire `EvalSnap` output into trace records so evaluation outcomes are searchable by trace ID.

5. **Trace coverage CI gate**
   `records_execution_trace / (calls + invokes_eval) >= 0.05` minimum. Fails on regression.

### Acceptance Gate
```
records_execution_trace >= 1,000
hard_fails_untranscripted >= 50
transcripts_response >= 100
signs_execution_trace >= 100
```

### Derisking
- Additive only; does not change execution semantics
- Waves 2 and 3 create the chokepoints — Wave 5 simply populates them

---

## Wave 6: Unified Runtime State Authority

**Addresses:** L4 P0 Unified Runtime State Authority, L4 P1 Memory System Fragmentation
**ADG baseline:** `reads_runtime_state:459`, `observes_runtime_state:3`, `snapshots_state:1`
**Closes:** L4 P0, L4 P1 memory fragmentation, L4 P2 state versioning, L3 P1 run-scoped coordination state, L1 P1 unified reasoning context

### Deliverables

1. **`RunStateAuthority` — single ledger facade**
   New module in L4 state layer.
   - All `reads_runtime_state` go through `RunStateAuthority.read()`
   - All `writes_through` (from Wave 1) commit via `RunStateAuthority.commit()`
   - Maintains a versioned log of state changes per run ID
   Starts as a facade: delegates to existing state stores with no behavioural change.

2. **`observes_runtime_state` expansion**
   Current: 3. Every L3 orchestrator and L1 cognitive module observes state through `RunStateAuthority`. Target: ≥50.

3. **`snapshots_state` expansion**
   Current: 1. One snapshot per completed L3 orchestration run. Target: ≥20 per normal test suite execution.

4. **State versioning**
   `RunStateAuthority` maintains version vectors. Reads include version at time of read. Enables conflict detection for concurrent orchestration runs.

5. **L1 memory binding**
   L1 modules (106 total) currently read from multiple sources. After Wave 6, all L1 memory reads are bound to the current run's `RunStateAuthority` scope. Closes L1 P1 "memory not bound to run context."

6. **Semantic cache unification**
   `L4H` Redis cache and `semantic_cache_manager.py` remain as performance layers. All writes go through `RunStateAuthority`. Eliminates fragmented write paths.

### Acceptance Gate
```
observes_runtime_state >= 50
snapshots_state >= 20
reads_runtime_state via RunStateAuthority >= 80% of total
state versioning: all writes produce version increment (verifiable via trace)
```

### Derisking
- `RunStateAuthority` starts as pass-through facade — zero semantic change
- Migrate one L3 orchestrator at a time; run existing state integrity tests after each
- Full migration only after zero state-corruption failures across 3 consecutive sprint test runs

---

## Wave 7: Structural Debt Burndown (P4)

**Addresses:** P4 across all layers
**ADG baseline:** `dead_imports:4409`, `antipattern:1528`, `registers_antipattern:11`, `unresolved_count:412`
**This is the wave that was 100% skipped in all prior implementations.**

### Why P4 was always skipped — and why it cannot be skipped again

P4 work produces no new features and no new graph edges. It only removes. It is perpetually deprioritised because P0/P1 work is always more urgent. However:

- 4,409 dead imports inflate apparent connectivity and pollute ADG impact analysis
- 1,528 antipatterns create false confidence in coverage metrics
- 412 unresolved imports make ADG blast-radius analysis imprecise
- Wave 0 freezes the ceiling; Wave 7 burns it down

Without Wave 7, the ADG degrades in precision over time even as Waves 1–6 improve enforcement.

### Deliverables

1. **Dead import elimination: 4,409 → target 0**
   Run `ruff --select F401` across all layers.
   Batch by layer: L_TEST → L_OPS → L_APP → core (lowest risk first).
   Wave 0 CI gate prevents re-introduction.

2. **Antipattern remediation: 1,528 → target ≤200**
   Classify by type using `registers_antipattern` hook:
   - **Auto-fixable** (ruff rules): fix programmatically in batch
   - **Manual/mechanical** (string path concat, etc.): fix layer by layer
   - **Architectural** (dynamic dispatch, exception catch-alls): resolved by Waves 1–3; mark closed after those gates pass

3. **Unresolved import resolution: 412 → 0**
   Each must either be resolved (add correct module) or removed (dead import).
   ADG precision increases directly — `unresolved_count` affects confidence scores on all nodes in the subgraph.

4. **`registers_antipattern` expansion: 11 → ≥50**
   All known antipattern categories should have registered detection hooks so new instances are caught by the Wave 0 CI gate.

### Phase 7a / 7b Split (to avoid one massive PR)
- **7a:** `dead_imports` L_TEST + L_OPS layers + `unresolved_count` full sweep
- **7b:** `dead_imports` L_APP + core layers + `antipattern` full remediation

### Acceptance Gate
```
Phase 7a: dead_imports <= 2,000  |  unresolved_count <= 50
Phase 7b: dead_imports <= 500    |  antipattern <= 500  |  registers_antipattern >= 50
Final:    dead_imports = 0       |  antipattern <= 200
```

### Derisking
- All changes are removal/cleanup; no new logic
- Exception: antipatterns that are load-bearing at runtime must be identified before removal
- Mandatory full test run after each batch PR
- Wave 0 CI gate means any regression re-introducing dead imports fails immediately

---

## Cross-Wave Dependency Graph

```
Wave 0 ──────────────────────────────────────────────> ALL (hard prerequisite, must pass before any other wave starts)

Wave 1 (UWG sovereignty) ────────────────────────────> Wave 5 (traces need governed write path)
                                                     > Wave 6 (state authority needs write sovereignty)

Wave 2 (typed dispatch registry) ────────────────────> Wave 3 (guardrails need visible call graph)
                                                     > Wave 5 (traces piggyback on registry chokepoint)

Wave 3 (guardrail enforcement) ──────────────────────> Wave 5 (traces piggyback on guardrail chokepoint)

Wave 4 (determinism injection) ──────────────────────> Wave 5 (traces include clock values for replay)

Wave 1 + Wave 2 + Wave 3 ────────────────────────────> Wave 6 (state authority needs: sovereign writes + typed calls + guardrails)

Waves 1–6 complete ──────────────────────────────────> Wave 7 (debt cleanup safe once structure is sound)
```

---

## ADG Acceptance Gates Summary

| Wave | Key Gate Metric | Current (Redis) | Target |
|---|---|---|---|
| **W0** | ADG CI blocks on delta | Advisory only | Hard-fail |
| **W1** | `writes_through / total_writes` | 1.6% (80/4955) | ≥80% |
| **W1** | `execution_terminates_at_uwg` | 44 | ≥200 |
| **W1** | `snapshots_state` | 1 | ≥10 |
| **W2** | `agent_executes_agent` | 2 | ≥50 |
| **W2** | `invokes_getattr_dynamic` | 2,978 | ≤2,000 |
| **W2** | `invokes_importlib` | 166 | ≤80 |
| **W2** | `issues_capability_token` | 5 | ≥20 |
| **W3** | `applies_guardrail` | 68 | ≥500 |
| **W3** | `applies_guardrail / calls` | 0.30% | ≥10% |
| **W3** | `reenters_safety` | 3 | ≥30 |
| **W3** | `validated_by_safety_plane` | 18 | ≥50 |
| **W4** | `emits_replay_key` | 2 | ≥50 |
| **W4** | `emits_determinism_digest` | 3 | ≥20 |
| **W4** | `uses_wall_clock` | 884 | ≤584 |
| **W5** | `records_execution_trace` | 64 | ≥1,000 |
| **W5** | `hard_fails_untranscripted` | 6 | ≥50 |
| **W5** | `transcripts_response` | 10 | ≥100 |
| **W6** | `observes_runtime_state` | 3 | ≥50 |
| **W6** | `snapshots_state` | 1 | ≥20 |
| **W7a** | `dead_imports` | 4,409 | ≤2,000 |
| **W7a** | `unresolved_count` | 412 | ≤50 |
| **W7b** | `dead_imports` | — | ≤500 |
| **W7b** | `antipattern` | 1,528 | ≤500 |
| **W7b** | `registers_antipattern` | 11 | ≥50 |

---

## Derisking Principles (Applied Universally)

1. **Opt-out enforcement, not opt-in.** The governed path must be the path of least resistance. Ungoverned paths require explicit allowlist registration with justification.

2. **Shim-first, cutover-second.** Every Wave 1–3 change uses a shim preserving existing call semantics while emitting correct graph edges. Hard cutover happens only after ADG acceptance gate passes.

3. **`warn` before `enforce`.** All enforcement modes start as `warn` (log violation, do not block). Switch to `enforce` after one sprint of zero new violations in `warn` mode per sublayer.

4. **Sublayer order: outermost first.** Migrate `L_APP` before `L3` before `L2` before `L0`. Blast radius is smallest at the app layer, largest at the routing layer.

5. **ADG re-ingest after every PR.** Run `python tools/adg/adg_redis_ingest.py --force` after every PR in Waves 1–3. The ADG must show the expected edge delta before merge.

6. **No wave begins until predecessor gate passes.** This is the specific rule violated in all prior attempts. Partial completion of a structural wave followed by starting a coverage wave produces exactly the failure pattern documented in the RCA.

7. **P4 (Wave 7) is not optional.** It is explicitly tracked in ADG CI from Wave 0 onward. Any sprint that claims P4 work was "deprioritised" must document the explicit rollover decision in the PR log.

---

## Gap × Wave Coverage Matrix

| Gap (from analysis) | Priority | Primary Wave | Secondary Wave |
|---|---|---|---|
| L0 Deterministic Routing | P0 | W4 (determinism) | W0 (CI gate) |
| L1 Reasoning Traceability | P0 | W5 (traces) | W2 (typed calls) |
| L2 Guardrail Before Actions | P0 | W3 (guardrails) | W2 (typed calls) |
| L3 Agent Handoff Topology | P0 | W2 (registry) | W3 (guardrails) |
| Dynamic dispatch determinism risk | **Major (standalone — NOT subsumed by topology gap)** | W4 (determinism gate: `invokes_getattr_dynamic AND uses_wall_clock` modules) | W2 (registry reduces surface) |
| L4 Unified Runtime State | P0 | W1 (UWG) | W6 (state authority) |
| L5 Policy Enforcement Coverage | P0 | W3 (guardrails) | W0 (CI gate) |
| L5 Policy Reads (partial only) | — | *`reads_policy_state:1317` = visibility progress, NOT gap closure. Gap closes only when `applies_guardrail/calls >= 0.10` in W3.* | — |
| L6 Cross-Layer Trace Coverage | P0 | W5 (traces) | W4 (determinism) |
| L0 Routing Policy Governance | P1 | W2 (registry) | W3 (guardrails) |
| L1 Unified Reasoning Context | P1 | W6 (state) | W5 (traces) |
| L2 Deterministic Execution Proof | P1 | W4 (determinism) | W5 (traces) |
| L3 Run-Scoped Coordination State | P1 | W6 (state) | W2 (registry) |
| L4 Memory System Fragmentation | P1 | W6 (state) | W1 (UWG) |
| L5 Tool Safety Governance (OPEN) | P1 | W3 (guardrails) | W2 (registry) |
| L6 Evaluation Signal Integration | P1 | W5 (traces) | — |
| L0 Routing Telemetry | P2 | W4 (determinism) | W5 (traces) |
| L2 Typed Tool Interfaces | P2 | W2 (registry) | W3 (guardrails) |
| L3 Agent Capability Registry | P2 | W2 (registry) | — |
| L4 State Versioning | P2 | W6 (state) | W1 (UWG) |
| L5 Safety Audit Trails | P2 | W5 (traces) | W3 (guardrails) |
| All P3 gaps | P3 | W5 / W6 | W7 |
| All P4 gaps | P4 | **W7** | W0 (gate) |

---

## Plan Hardening Addendum

**Purpose:** Convert the remediation plan from a structural roadmap into an enforceable deterministic execution program with zero silent bypasses. This section does not replace any wave — it introduces global invariants, CI enforcement modules, per-wave hardening rules, and a post-wave validation loop that must be satisfied before any wave is declared complete.

---

### Global Invariants (Apply to All Waves)

All six invariants must hold across the system before any wave is considered complete. A wave that passes its ADG acceptance gate but violates any invariant below is **not closed**.

| ID | Invariant | Enforcement Point |
|---|---|---|
| **I1** | **No Silent Bypass.** Any governance control introduced must be the only executable path. Shadow paths, fallback wrappers, and optional bypasses are prohibited. | Wave-exit ADG scan: any `writes_to` / `invokes_getattr_dynamic` / `applies_guardrail` delta that is not offset by the governed equivalent fails. |
| **I2** | **Enforcement Before Instrumentation.** Trace/metric/log edges do not count toward gap closure unless the enforcement gate already exists. `records_execution_trace` growth is only counted toward W5 closure after W3 guardrail gate passes. | ADG gate ordering: W5 gate cannot be evaluated until W3 gate is certified. |
| **I3** | **Deterministic State Mutation.** All persistent mutations must be verifiably routed through UWG. `writes_through >= writes_to` at Wave 1 exit; ratio `>= 0.80`. | CI Module 3 (see below). |
| **I4** | **ADG as Ground Truth.** All acceptance gates are validated using ADG edge counts. CI must run ADG ingest on every PR. Command: `python tools/adg/adg_redis_ingest.py --force` | CI pre-merge hook. |
| **I5** | **No Telemetry→Execution Feedback Loops.** Observability systems cannot mutate routing, safety, or execution state directly. All mutations must pass through the meta-learning or governance plane. | ADG scan: any edge `observes_runtime_state → writes_to` that bypasses `RunStateAuthority` or UWG is a violation. |
| **I6** | **C0 Informational Boundary.** All telemetry, metrics, traces, and Redis observations remain informational unless explicitly authorized through a governance path. RAG context cannot mutate routing decisions, safety thresholds, execution tiers, or policies. | ADG: no `reads_runtime_state` or `reads_policy_state` edge from a C0 module may have a downstream `writes_to` edge within the same execution scope. |

---

### CI Enforcement Layer

Six CI modules must be implemented as hard-fail checks in `ops_scripts/ci/`. Each runs on every PR. Failure blocks merge — no exceptions, no manual overrides.

#### CI Module 1 — Determinism Gate
```
Fail if: uses_wall_clock_delta > 0
         uses_random_delta > 0
Unless:  ClockProvider or RandomProvider injection is present in the same PR
         (verified by presence of `emits_determinism_digest_delta > 0` or `seeds_rng_delta > 0`)
```

#### CI Module 2 — Dispatch Visibility Gate
```
Fail if: invokes_getattr_dynamic_delta > 0
Unless:  agent_executes_agent_delta > 0  (typed registry edge added in same PR)
```

#### CI Module 3 — Mutation Sovereignty Gate
```
Fail if: writes_to_delta > 0
Unless:  writes_through_delta > 0  (UWG-governed write added in same PR)
```

#### CI Module 4 — Guardrail Coverage Gate
```
Fail if: applies_guardrail / calls < 0.10
```
*(Active from Wave 3 exit onward — Wave 0 records baseline, Wave 3 sets the floor.)*

#### CI Module 5 — Trace Coverage Gate
```
Fail if: records_execution_trace / (calls + invokes_eval) < 0.05
```
*(Active from Wave 5 exit onward.)*

#### CI Module 6 — Determinism Artifact Gate
```
Fail if: emits_replay_key_delta == 0
         for any PR that adds a module touching routing decisions
         (identified by: module has routes_path or proposal_commits_routing edge)
```

**Implementation target:** All six modules implemented in `ops_scripts/ci/_adg_ci_gates.py` as Wave 0 deliverable #6. Modules 4 and 5 start in `warn` mode and switch to `enforce` at their respective wave exit gates.

---

### Per-Wave Hardening Rules

These rules are additive to each wave's existing acceptance gates. A wave fails if any hardening rule below is not satisfied.

#### Wave 1 Hardening — UWG Mutation Verification

Every UWG write must produce a structured mutation record:

```json
{
  "mutation_hash": "<sha256 of payload>",
  "actor_id":      "<module or agent id>",
  "run_id":        "<trace id>",
  "replay_key":    "<deterministic replay key>",
  "timestamp":     "<ClockProvider.now() — never datetime.now() directly>"
}
```

CI must verify: `hash(mutation_payload) == mutation_hash` for every record in the ledger.

Replay engine must reconstruct full state from mutation ledger alone (no side-channel reads).

**Failure mode prevented:** Silent state mutation bypassing UWG; state divergence between primary and replay.

#### Wave 2 Hardening — Dispatch Registry Hard Cutoff

Once `invokes_getattr_dynamic <= 300` (≤10% of baseline 2,978), the implicit `getattr` fallback inside `AgentDispatchRegistry` **must be removed**. After removal:

- Any unregistered dispatch attempt raises a hard `UnregisteredDispatchError`
- `agent_executes_agent` edge is the only valid dispatch proof
- `issues_capability_token` and `validated_by_safety_plane` edges must be produced by every registry call

**Hard cutoff rule enforced by CI Module 2.** Post-cutover, `invokes_getattr_dynamic_delta > 0` on any PR is an unconditional build failure.

#### Wave 3 Hardening — Fail-Closed Guardrail

Guardrail results of `UNKNOWN`, `ERROR`, or `TIMEOUT` must all produce execution termination — never pass-through. Specifically:

- `UNKNOWN` → treat as `REJECT`
- `ERROR` → escalate to `reenters_safety` path
- `TIMEOUT` → treat as `REJECT` + emit `hard_fails_untranscripted`

Every guardrail decision must emit a structured decision record:

```json
{
  "guardrail_decision_hash": "<sha256>",
  "policy_hash":             "<active policy hash>",
  "decision_timestamp":      "<ClockProvider.now()>",
  "verdict":                 "APPROVE | REJECT | ESCALATE"
}
```

Both `guardrail_decision_hash` and `policy_hash` must appear in the execution trace.

#### Wave 4 Hardening — Deterministic Provider Contract

`ClockProvider` must implement:
- `WallClock` — production; records value into trace context before returning
- `FrozenClock` — replay; returns pre-recorded value from trace context

`RandomProvider` must implement:
- `SeededRandom` — seeded from `run_id + trace_id`; deterministic given same seed
- `DeterministicRandom` — testing; returns pre-specified sequence

**Replay verification gate (mandatory):**
```
hash(output_original) == hash(output_replay)
```
This comparison must pass for every trace in the replay harness. Failure blocks CI.

#### Wave 5 Hardening — Three Trace Properties (T1/T2/T3)

A trace is only valid (counted toward `records_execution_trace`) if all three properties hold:

| Property | Requirement |
|---|---|
| **T1 Complete** | Trace covers every execution surface call in the run (no gaps between first and last call in trace context) |
| **T2 Signed** | Trace includes `trace_id` + `execution_signature` (produced by `signs_execution_trace`) |
| **T3 Replayable** | Trace includes: `inputs`, `routing_decision`, `tool_calls`, `outputs` — sufficient to reproduce the run |

CI validation must successfully replay a minimum of **10 distinct traces** per wave exit. Replay failures block wave closure.

#### Wave 6 Hardening — `RunStateAuthority` Ledger Properties

`RunStateAuthority` state mutations must satisfy:

1. **Append-only** — no mutation overwrites a prior version; history is immutable
2. **Versioned** — every write increments the version vector; every read returns `(value, state_version)`
3. **Conflict-detecting** — if two writes target the same key with the same version vector, the second write is rejected with a `StateConflictError`

Cross-run mutation detection: any write referencing a `run_id` other than the current run's `run_id` must be explicitly authorized via a cross-run merge token.

#### Wave 7 Hardening — CI Re-introduction Prevention

Dead import and antipattern cleanup must be permanently protected:

```
CI: dead_imports_delta > 0  → unconditional build failure (no exceptions)
CI: antipattern_delta > 0   → unconditional build failure
    unless: registers_antipattern edge added in same PR with documented justification
```

All new antipatterns — including those introduced during development of Waves 1–6 — must be registered via `registers_antipattern` before merge. Zero-tolerance from Wave 0 onward.

---

### Determinism Risk Classification (Standalone ADG Invariant)

Per ChatGPT reconciliation: the intersection of dynamic dispatch and non-deterministic time is the highest-risk surface in the system. Tracked as an independent ADG invariant separate from both the topology gap and the determinism gap.

```
Risk surface: modules where BOTH hold:
  - invokes_getattr_dynamic fan-out > 0
  - uses_wall_clock fan-out > 0

Current count (baseline, live from Redis 03142026):
  Nodes with invokes_getattr_dynamic:  941
  Nodes with uses_wall_clock:          269
  INTERSECTION (both risks):            84  ← standalone invariant target

Target: 0 modules

ADG query (Python — re-run after every wave):
  import redis, json
  r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
  cursor = 0
  ga, wc = set(), set()
  while True:
      cursor, keys = r.scan(cursor, match='adg:edge:*:invokes_getattr_dynamic', count=1000)
      for k in keys: ga.add(k.split(':')[2])
      if cursor == 0: break
  cursor = 0
  while True:
      cursor, keys = r.scan(cursor, match='adg:edge:*:uses_wall_clock', count=1000)
      for k in keys: wc.add(k.split(':')[2])
      if cursor == 0: break
  print('Intersection:', len(ga & wc))
```

**Layer distribution of 84 intersection modules (baseline):**

| Layer | Count | Notes |
|---|---|---|
| L_APP | 17 | Highest count — lowest blast radius; migrate first |
| L_SHARED | 16 | Mixins (`ssot_*_mixin.py`) — single fix propagates widely |
| L_TEST | 13 | Test files — `uses_wall_clock` in tests is lower risk but still signals missing `FrozenClock` adoption |
| L5 | 10 | Safety layer — highest priority: `error_recovery_guardrail.py` + sovereignty agents |
| L3 | 7 | Orchestration — `NervousSystemAgent`, `mission_runner`, `sovereign_rag_orchestrator` |
| L_RUNTIME | 4 | `trace_emitter.py` + runtime configs |
| L_OPS | 4 | CI scripts — lower risk but `ci_timeout_decorator.py` is notable |
| L2 | 4 | `SovereignLLMGateway.py`, `RedisSovereignAgent.py` — high-value targets |
| L4 | 3 | State layer — `CachedStateLedger.py` is direct state mutation risk |
| L0 | 3 | **Highest severity:** `execute_ssot.py`, `_ssot_routing.py`, `seam_audit.py` — routing decisions with non-deterministic time |
| L1 | 1 | `execution_status.py` |
| L_TOOLS | 1 | `prove_meta_learning_bus.py` |

**Priority order for closure:**
1. **L0 first** (3 modules): routing decisions + dynamic dispatch + wall clock = worst combination
2. **L5 next** (10 modules): guardrail + enforcement layer must itself be deterministic
3. **L2 next** (4 modules): `SovereignLLMGateway` is on every execution path
4. **L_SHARED mixins** (16 modules): single `ClockProvider` injection in base mixin closes ~16 descendant modules
5. **L3 orchestrators** (7 modules): after registry (W2) reduces dynamic dispatch surface
6. **L_APP / L_RUNTIME / L_OPS**: lower priority, lower blast radius

This invariant is tracked from Wave 0 onward and closes only when the intersection set is empty. Progress toward zero is mandatory in both Wave 2 (topology reduction) and Wave 4 (determinism injection). Whichever wave runs last on a given module owns its closure.

---

### Post-Wave Validation Loop

After every wave, all five steps must be completed and recorded in the wave's evidence artifact before the wave is declared closed. Partial completion of this loop does not count.

```
Step 1: Re-ingest ADG
        python tools/adg/adg_redis_ingest.py --force

Step 2: Compute graph plane counts
        python -c "
        import redis, json
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        snap = json.loads(r.get('adg:snapshot'))
        gpc = snap['graph_plane_counts']
        for k in sorted(gpc): print(k, gpc[k])
        "

Step 3: Verify wave acceptance gates
        All numeric gates from wave's Acceptance Gate block must pass.
        Record: gate_name, baseline, current, delta, pass/fail.

Step 4: Run replay harness
        Minimum 10 traces replayed.
        hash(output_original) == hash(output_replay) for all 10.
        Record: trace_id, replay_status, output_hash_match.

Step 5: Confirm no invariant violation
        Re-run all six Global Invariants (I1–I6) as ADG queries.
        Any violation resets the wave to IN_PROGRESS regardless of gate status.
```

Evidence artifact path: `docs/reports/plans/wave-{N}-exit-evidence-{timestamp}.md`

---

### Final Structural Guarantee (Seven Conditions for P0 Closure)

The architecture cannot claim closure of P0 gaps until all seven conditions hold **simultaneously**. Partial satisfaction (e.g., five of seven) does not constitute closure.

| # | Condition | Primary Wave | Verification |
|---|---|---|---|
| 1 | All writes flow through UWG | W1 | `writes_through / total_writes >= 0.80` + mutation record audit |
| 2 | All calls flow through typed dispatch | W2 | `agent_executes_agent >= 50` + `invokes_getattr_dynamic <= 300` |
| 3 | All executions pass guardrail validation | W3 | `applies_guardrail / calls >= 0.10` + fail-closed verification |
| 4 | All runs produce signed execution traces | W5 | `records_execution_trace >= 1,000` + T1/T2/T3 properties verified |
| 5 | All traces can be deterministically replayed | W4 | `emits_replay_key >= 50` + replay harness passing 10 traces |
| 6 | All state mutations are versioned and auditable | W6 | `observes_runtime_state >= 50` + `RunStateAuthority` ledger verified |
| 7 | All architectural debt is prevented from re-entering | W0 + W7 | CI modules 1–6 all in `enforce` mode + `dead_imports = 0` + `antipattern <= 200` |

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

