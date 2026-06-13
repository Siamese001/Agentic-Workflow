# Full Gap Closure: Waves 0-7 (Live ADG 03142026_0949)

All P0-P4 gaps closed to structural completion across 8 waves, each gated by live Redis+SQLite ADG edge counts.

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


## Live Baseline (8,253 nodes, 225,893 edges)

| Metric | Current | Target |
|---|---|---|
| uses_wall_clock | 878 | 0 |
| invokes_getattr_dynamic | 2,986 | 0 |
| invokes_dynamic | 539 | 0 |
| invokes_importlib | 167 | <=20 |
| applies_guardrail | 68 | >=1,800 (>=10% of calls) |
| agent_executes_agent | 2 | >=50 |
| records_execution_trace | 64 | >=1,000 |
| snapshots_state | 1 | >=20 |
| observes_runtime_state | 3 | >=50 |
| emits_replay_key | 8 | >=50 |
| emits_determinism_digest | 6 | >=20 |
| dead_imports | 4,419 | 0 |
| antipattern | 1,533 | <=200 |
| unresolved_count | 414 | 0 |
| writes_through/writes_to | 1.97% | >=80% |
| execution_terminates_at_uwg | 53 | >=200 |
| dual-risk nodes (getattr AND wall_clock) | ~84 | 0 |

**Already done (Chunks 1-6):** 81 new import edges wired; uses_wall_clock -9; invokes_getattr_dynamic -7.

---

## Wave 0: ADG Hard CI Gates
**Blocks all other waves. Must pass first.**

1. `ops_scripts/ci/_adg_ci_gates.py` with 6 CI modules:
   - M1: uses_wall_clock_delta > 0 = FAIL (unless emits_determinism_digest_delta > 0)
   - M2: invokes_getattr_dynamic_delta > 0 = FAIL (unless agent_executes_agent_delta > 0)
   - M3: writes_to_delta > 0 = FAIL (unless writes_through_delta > 0)
   - M4: applies_guardrail/calls < 0.10 = FAIL (active from W4 exit)
   - M5: records_execution_trace/calls < 0.05 = FAIL (active from W5 exit)
   - M6: routing PR without emits_replay_key_delta > 0 = FAIL (active from W3 exit)
2. Freeze baselines in `ops_scripts/ci/_analyse_ssot_violations.py`: dead_imports=4419, antipattern=1533, invokes_getattr_dynamic=2986
3. Wire M1-M3 into `adg-invariant-scan.yml` in warn mode; promote to enforce after 1-sprint soak

**Gate:** CI modules M1-M3 active in warn mode; baselines frozen

---

## Wave 1: UWG Write-Path Sovereignty
**P0 L4, P1 L4 — Baseline: writes_through:98 / writes_to:4,882 = 1.97% governed**

1. UWG CI allowlist: writes_to not in allowlist = CI fail (M3 enforce)
2. Batch migrate L_APP (1,324 modules) via `_patch_execute_ssot_routing.py`
3. Batch migrate L3 orchestrators (204 modules)
4. Batch migrate L0 routing (366 modules)
5. execution_terminates_at_uwg: 53 -> >=200
6. snapshots_state: 1 -> >=10

**Gate:** writes_through/(writes_through+writes_to) >= 0.80 | execution_terminates_at_uwg >= 200 | snapshots_state >= 10 | M3 enforce

---

## Wave 2: Bulk invokes_getattr_dynamic Elimination
**P0 L3, P2 L2 — Baseline: 2,986 edges vs agent_executes_agent:2**

1. `tools/adg/bulk_getattr_migrator.py` - AST rewriter targeting all getattr dispatch sites in SQLite, layer order: L_APP -> L3 -> L_SHARED -> L2 -> L0
2. Dual-risk intersection first (84 nodes with both invokes_getattr_dynamic AND uses_wall_clock): L0(3) -> L5(10) -> L2(4) -> L_SHARED(16)
3. invokes_importlib:167 -> <=20 (registry pre-registration)
4. invokes_dynamic:539 -> 0 (same migration pattern)
5. issues_capability_token: 5 -> >=20
6. Hard cutover: remove AgentDispatchRegistry getattr fallback once invokes_getattr_dynamic <= 300

**Gate:** invokes_getattr_dynamic <= 300 (then 0) | agent_executes_agent >= 50 | dual-risk intersection = 0 | M2 enforce

---

## Wave 3: Bulk uses_wall_clock Elimination
**P0 L0, P1 L2 — Baseline: 878 sites + uses_random:59**

1. `tools/adg/bulk_clock_migrator.py` - AST rewriter: datetime.now()/time.time() -> ClockProvider.now(); random.* -> RandomProvider.* Layer order: L0 -> L5 -> L2 -> L3 -> L_APP -> L_SHARED
2. FrozenClock injection in all test files with uses_wall_clock edges
3. emits_replay_key: 8 -> >=50 (every L0 routing decision)
4. emits_determinism_digest: 6 -> >=20 (every L3 run completion)
5. seeds_rng discipline: all uses_random seeded from run_id+trace_id
6. Replay harness: >=10 execution paths with hash(original)==hash(replay)

**Gate:** uses_wall_clock = 0 | uses_random = 0 | emits_replay_key >= 50 | emits_determinism_digest >= 20 | M1+M6 enforce | replay harness passes

---

## Wave 4: Guardrail Enforcement Breadth
**P0 L2, P1 L5 — Baseline: applies_guardrail:68 / calls:18,651 = 0.36%**
**Requires W1 (write chokepoint) + W2 (call chokepoint) first**

1. Guardrail in AgentDispatchRegistry.dispatch() - promote to enforce mode
2. Guardrail in UWG.write_through() - extend to all write variants
3. authorize_and_execute() mandatory pre-check: UNKNOWN/ERROR/TIMEOUT -> reject (fail-closed)
4. validated_by_safety_plane: 18 -> >=50 (all execution paths A/B/C/D)
5. reenters_safety: 3 -> >=30
6. Structured guardrail decision record per call (guardrail_decision_hash + policy_hash + verdict)
7. M4 promoted to enforce: applies_guardrail/calls >= 0.10

**Gate:** applies_guardrail >= 1,800 | applies_guardrail/calls >= 0.10 | reenters_safety >= 30 | validated_by_safety_plane >= 50 | M4 enforce

---

## Wave 5: Execution Trace Wiring
**P0 L1, P0 L6 — Baseline: records_execution_trace:64 / 22,514 surface = 0.28%**
**Requires W2 (registry chokepoint) + W4 (guardrail chokepoint)**

1. TraceContext.record() in AgentDispatchRegistry.dispatch() - covers all W2-migrated calls
2. TraceContext.record() in authorize_and_execute() - covers W4 guardrail path
3. T1/T2/T3 trace validity: T1=complete, T2=signed (trace_id+execution_signature), T3=replayable (inputs+routing+tool_calls+outputs)
4. hard_fails_untranscripted: 6 -> >=50
5. transcripts_response: 10 -> >=100 (all SovereignLLMGateway responses)
6. EvalSnap output wired into trace records (invokes_eval:501 results searchable by trace ID)
7. M5 enforce: records_execution_trace/calls >= 0.05

**Gate:** records_execution_trace >= 1,000 | hard_fails_untranscripted >= 50 | transcripts_response >= 100 | signs_execution_trace >= 100 | M5 enforce | 10 traces pass T1/T2/T3

---

## Wave 6: Unified State Authority (RSA Full Adoption)
**P0 L4, P1 L3, P1 L1 — Baseline: observes_runtime_state:3, snapshots_state:1**
**Requires W1+W2+W3+W4**

1. RSA bulk adoption: expand from current 10 importers to all L3 orchestrators + L1 cognitive modules
2. observes_runtime_state: 3 -> >=50
3. snapshots_state: 1 -> >=20 (one per L3 run)
4. reads_runtime_state via RSA >= 80% of total 462
5. Append-only versioned ledger: every write increments version vector; StateConflictError on concurrent writes
6. L1 memory binding: all 103 L1 modules bound to current run RSA scope
7. Semantic cache unification: semantic_cache_manager.py writes route through RSA

**Gate:** observes_runtime_state >= 50 | snapshots_state >= 20 | reads_runtime_state via RSA >= 80% | ledger append-only+versioned verified

---

## Wave 7: Structural Debt Burndown (P4)
**The wave skipped in every prior implementation.**
**Baseline: dead_imports:4,419 | antipattern:1,533 | unresolved_count:414**
**Requires W1-W6 complete**

### Phase 7a (L_TEST + L_OPS - lowest blast radius)
1. Dead import elimination via ruff --select F401 on L_TEST(3,324) + L_OPS(420)
2. unresolved_count: 414 -> 0
3. registers_antipattern: 11 -> >=50

### Phase 7b (L_APP + core)
1. Dead import elimination in L_APP(1,324) + L2-L6 core
2. Antipattern remediation: 1,533 -> <=200 (auto-fix ruff; mechanical layer-by-layer; architectural already closed by W2-W4)
3. All 6 CI modules in enforce mode

**Gate 7a:** dead_imports <= 2,000 | unresolved_count = 0
**Gate 7b:** dead_imports = 0 | antipattern <= 200 | registers_antipattern >= 50 | all 6 CI modules enforce

---

## Cross-Wave Dependencies

```
W0 ────────────> ALL (CI freeze gates before anything else)
W1 (UWG) ──────> W4 (guardrails need write chokepoint)
               > W6 (RSA needs write sovereignty)
W2 (getattr) ──> W4 (guardrails need visible call graph)
               > W5 (traces piggyback on registry chokepoint)
W3 (clock) ────> W5 (traces include clock values for replay)
W4 (guardrail) -> W5 (traces piggyback on guardrail chokepoint)
W1+W2+W3+W4 ───> W6 (RSA needs all structural chokepoints)
W1-W6 ─────────> W7 (debt cleanup safe once structure sound)

W4, W5, W6 can run in PARALLEL once W1+W2+W3 gates all pass.
```

---

## ADG Gate Summary Table

| Wave | Key Metric | Now | Target |
|---|---|---|---|
| W0 | CI M1-M3 active | none | warn live |
| W1 | writes_through/total | 1.97% | >=80% |
| W1 | execution_terminates_at_uwg | 53 | >=200 |
| W2 | invokes_getattr_dynamic | 2,986 | 0 |
| W2 | agent_executes_agent | 2 | >=50 |
| W2 | dual-risk intersection | ~84 | 0 |
| W3 | uses_wall_clock | 878 | 0 |
| W3 | emits_replay_key | 8 | >=50 |
| W4 | applies_guardrail | 68 | >=1,800 |
| W4 | applies_guardrail/calls | 0.36% | >=10% |
| W5 | records_execution_trace | 64 | >=1,000 |
| W5 | transcripts_response | 10 | >=100 |
| W6 | observes_runtime_state | 3 | >=50 |
| W6 | snapshots_state | 1 | >=20 |
| W7a | dead_imports | 4,419 | <=2,000 |
| W7a | unresolved_count | 414 | 0 |
| W7b | dead_imports | - | 0 |
| W7b | antipattern | 1,533 | <=200 |

---

## Seven Conditions for P0 Full Closure (all must hold simultaneously)

| # | Condition | Wave | Gate |
|---|---|---|---|
| 1 | All writes through UWG | W1 | writes_through/total >= 0.80 |
| 2 | All calls through typed dispatch | W2 | invokes_getattr_dynamic = 0 |
| 3 | All executions pass guardrail | W4 | applies_guardrail/calls >= 0.10 |
| 4 | All runs produce signed traces | W5 | records_execution_trace >= 1,000 + T1/T2/T3 |
| 5 | All traces deterministically replayable | W3 | emits_replay_key >= 50 + harness passing |
| 6 | All state versioned and auditable | W6 | observes_runtime_state >= 50 |
| 7 | Debt prevented from re-entering | W0+W7 | CI M1-M6 enforce + dead_imports=0 |

---

## Execution Approach

- Each wave runs in chunks of <=300 lines per PR
- W2 and W3 use Python AST bulk migration tooling (`bulk_getattr_migrator.py`, `bulk_clock_migrator.py`)
- Every PR ends with: `python tools/generate_full_adg.py` + `python tools/adg/adg_redis_ingest.py --force`
- ADG edge delta must confirm expected direction before merge
- Post-wave validation: Steps 1-5 (re-ingest, graph plane counts, gate verify, replay harness, invariant check)
- Evidence artifact per wave: `docs/reports/plans/wave-N-exit-evidence-{timestamp}.md`

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

