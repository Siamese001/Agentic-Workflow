# V15 Gap Remediation — Phased Implementation Plan

Phased plan to close 89 V15 target-state gaps (0% compliant → full compliance), prioritized P0–P4 by blast radius, dependency order, and safety criticality.

**Source**: `docs/reports/plans/v15_gap_analysis.json`
**Output**: `docs/reports/plans/v15_phased_implementation_plan.md` (canonical copy on approval)

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


## Priority Legend

| Priority | Meaning | Gate |
|----------|---------|------|
| **P0** | Fix contradictions (FAIL status) + unblock all downstream work | Must pass before P1 starts |
| **P1** | Runtime wiring — connect existing contracts to execution paths | Must pass before P2 starts |
| **P2** | Fill MISSING capabilities — new types, contracts, scanners | Must pass before P3 starts |
| **P3** | CI enforcement + meta-guardian coverage | Must pass before P4 starts |
| **P4** | Human-in-the-loop flows + advanced cognitive safety | No gate (incremental) |

---

## P0 — Resolve Contradictions & Schema Conflicts (4 FAIL items + 3 missing types)

**Goal**: Eliminate all FAIL statuses and create missing typed artifacts that block downstream wiring.

### P0.1 — Resolve GuardianArtifact dual-schema conflict (X3)
- **Gaps**: 7.2.1, 7.4
- Extend `guardian_contract.py::GuardianResult` with optional `signature`, `trace_id`, `commit_hash` fields (backwards-compatible)
- Add `to_signed()` method that produces a `SignedGuardianArtifact` from a `GuardianResult` + `SignatureEnclave`
- Update `write_guardian_result()` to optionally sign via enclave
- **Tests**: Verify round-trip `GuardianResult → sign → verify`

### P0.2 — Adapter prohibition enforcement (8.1)
- **Gap**: 8.1
- Add CI AST scanner: `ops_scripts/ci/check_adapter_prohibition.py`
- Scan for `class *Adapter*` or `import *AdapterBase*` outside `archives/`
- Add to `.github/workflows/guardian-tests.yml`
- Deprecation notice on `AdapterBase.py` (move to `archives/deprecated/` or add `__deprecated__` marker)

### P0.3 — Create missing typed artifacts (X4)
- **Gaps**: 1.7, 2.5, 12.2
- Add `HealingPlan` frozen dataclass to `v15_types.py`
- Add `StaleWriteIncident` frozen dataclass to `v15_types.py`
- Add `SideEffectRegistry` class to `v15_p6_types.py` (tracks touched resources per heal wave)
- **Tests**: Construction + freeze + serialization for each

### P0.4 — Discovery JSON schema for V15 audit (X5)
- **Gap**: 8.4
- Extend `forensic_discovery_prep.py` output to include `mro_chain`, `mixins`, `integrity_hash` fields
- Add `mro_signature` computation (SHA-256 of stringified MRO)
- **Tests**: Verify discovery output schema against V15 required fields

**P0 exit criteria**: 0 FAIL statuses, all 3 missing types exist, discovery schema V15-complete.

---

## P1 — Runtime Wiring (Layer D) — Connect Contracts to Execution Paths

**Goal**: Move the 52 PARTIAL items from "types+contracts exist" to "actually used at runtime". This is the single largest gap (D_RUNTIME_WIRED = 2.2%).

### P1.1 — Wire V15ExecutionGateway into SovereignBaseAgent.heal()
- **Gaps**: 1.1, 1.2, 1.3, 1.6, 2.1, 2.5, 5.1
- Add `V15ExecutionGateway` as optional execution wrapper in `SovereignBaseAgent`
- `heal()` calls go through gateway when `v15_enforcement=True` (feature flag)
- Gateway enforces: SurgicalManifest input, forbidden input rejection, dedupe, pipe order
- **Scope**: Base class change → all 137+ agents inherit
- **Tests**: Integration test with mock heal_fn through gateway

### P1.2 — Wire PolicyConfigGuard into healing wave lifecycle
- **Gaps**: 4.1, 4.2, 4.3
- At wave start: `PolicyConfigGuard.load()` + `pin_policy_config()`
- At wave end: `verify_policy_config_unchanged()`
- Mutation detected → `PolicyMutationIncident` raised
- **Integration point**: `execute_ssot.py` or orchestrator wave entry

### P1.3 — Wire SemanticClock into state commit paths
- **Gaps**: 13.1, 13.1.1
- Instantiate `SemanticClock` per orchestration session
- Pass clock to `V15ExecutionGateway` (already supported)
- All state commits must go through `clock.tick(layer, state_commit_valid=True)`
- **Integration point**: `HealingTransactionBoundary` context manager

### P1.4 — Wire HealingTransactionBoundary + BoundarySnapshot into heal()
- **Gaps**: 10.1, 10.2, 10.3, 10.4
- Wrap heal execution in `HealingTransactionBoundary`
- Pre-mutation: `create_boundary_snapshot()`
- Post-failure: `verify_rollback_integrity()`
- RESULT emission: `validate_result_emission(layer)`

### P1.5 — Wire GuardrailGuard into guardian pipeline
- **Gaps**: 7.3, 7.5, 7.7
- Before guardian execution: `GuardrailGuard.enforce_all()`
- After guardian execution: `enforce_artifact_presence()`
- Before L2 heal admission: `aggregate_gate_check()`

### P1.6 — Wire LawSlotHandler into agent tool access
- **Gaps**: 3.6, 15.4
- Replace direct tool access with `LawSlotHandler.use_tool()`
- Depletion tracking per agent per wave
- **Integration point**: Base agent tool dispatch

### P1.7 — Wire boundary schema validation at layer crossings
- **Gaps**: 2.4, 12.1
- Add `validate_boundary_schema()` call at each inter-layer message pass
- **Integration point**: Orchestrator dispatch / message bus

### P1.8 — Wire Trace ID format into all V15 artifact constructors
- **Gap**: 15.5
- All V15 contract builders that accept `trace_id` must validate format via `validate_trace_id()`
- Add `generate_trace_id()` call at orchestration session start

### P1.9 — Wire TelemetryEmitter into INCIDENT/RESULT emission
- **Gap**: 15.6
- After any INCIDENT or RESULT artifact emission, call `TelemetryEmitter.emit()`

### P1.10 — Wire ReplayGuardStore + signature verification into guardian execution
- **Gaps**: 7.2, 7.4.1, 7.4.2
- Guardian runner: sign result via `sign_artifact()`, verify via `verify_signature()`
- Track artifact hashes via `ReplayGuardStore`

**P1 exit criteria**: D_RUNTIME_WIRED ≥ 80% of PARTIAL items. Feature-flagged for safe rollout.

---

## P2 — Fill MISSING Capabilities (33 items, Layer A+B+C)

**Goal**: Create types, contracts, and tests for all MISSING sub-capabilities.

### P2.1 — MRO enforcement (8.3, 8.4, 8.5)
- AST scanner: verify safety mixins LEFT of base classes in MRO
- `mro_signature` field in discovery JSON (from P0.4)
- MRO violation = HARD FAIL in CI
- **Tests**: Parametrized tests for correct/incorrect MRO ordering

### P2.2 — Separation of responsibilities scanners (9.1, 9.2, 9.3)
- AST scanner: shared mixins contain no domain-specific logic (no `heal()` body, no domain imports)
- AST scanner: `heal()` methods contain no adapter/factory/orchestrator delegation
- **Output**: `ops_scripts/ci/check_separation_of_responsibilities.py`

### P2.3 — Validator safety emulation (2.2)
- Define `SafetyEmulationResult` typed artifact
- Implement sandbox pre-flight: apply manifest to in-memory AST copy, diff, validate
- **Integration point**: Validator → Healer pipe

### P2.4 — Validator L5 permission check (2.3)
- Define `PermissionCheckResult` typed artifact
- Validator queries L5 Guardian rules before passing manifest to healer
- Fail-closed: no permission = no heal

### P2.5 — Root Scope Pinning for signal collapse (5.3, 5.5)
- Define `RootScopePin` typed artifact
- Correlated signals collapse to single root cause before INCIDENT emission
- Deterministic correlation hash required

### P2.6 — L6 SelfHealingTrigger emission (5.4)
- Wire `SelfHealingTrigger` emission from L6 observability agents
- Route trigger to L2 execution layer

### P2.7 — Layer write-capability enforcement (12.3)
- Define `LayerCapability` enum (READ_ONLY, READ_WRITE)
- AST scanner: L0/L4/L6 agents must not call file-write, git-commit, or state-mutation APIs
- **Output**: `ops_scripts/ci/check_layer_write_capability.py`

### P2.8 — Cognitive safety wiring (6.1–6.4, 6.6–6.10)
- Wire `enforce_episodic_query_before_planning()` into planning agents
- Wire `static_policy_alignment_check()` into cognitive response paths
- Wire `knowledge_supervisor_check()` into L4 retrieval
- Wire `enforce_advisory_only()` into knowledge graph outputs
- Wire `PlanProvenance` generation into planning code
- Wire `MemoryHypostate` generation into state commit paths
- Wire `EpisodicSemanticLink` into episodic memory recording
- Wire `TrajectoryReuseConstraint` into trajectory reuse logic

### P2.9 — RAG Artifact Chain wiring (6.5)
- Wire `RetrievalQuery → RetrievedChunks → RerankScores → CitationBundle` into RAG/retrieval code
- Validate chain end-to-end via `validate_citation_chain()`

### P2.10 — Budget guards (11.1, 11.2)
- Wire `TokenCapArtifact` emission before LLM calls
- Wire `RouteRecoveryBox` into token overflow handling

### P2.11 — Routing contract wiring (3.1, 3.2, 3.3)
- Replace `contextual_router_config.py` RouteDecision with V15 `RouteDecisionArtifact`
- Enforce `RoutingRationale` enum and `RoutePath` enum in router

**P2 exit criteria**: 0 MISSING statuses. All 89 sub-capabilities have types + contracts + tests.

---

## P3 — CI Enforcement (Layer E)

**Goal**: Gate every V15 invariant in CI. Currently E_CI_ENFORCED = 0%.

### P3.1 — V15 compliance CI workflow
- New `.github/workflows/v15-compliance.yml`
- Runs all `tests/guardian/test_v15_p*_compliance.py` tests
- Gates on pass/fail

### P3.2 — Wall-clock AST scanner in CI (13.2)
- Wire `ast_scan_wall_clock()` into CI
- Scan all V15 contract files + agent files for forbidden wall-clock callables

### P3.3 — Meta-Guardian coverage gate (7.6)
- Wire `meta_guardian_check()` into CI
- Require ≥ 95% invariant coverage
- Measure coverage via `run_meta_invariants()` report

### P3.4 — Forbidden input scanner in CI (1.2)
- AST scan all `heal()` methods for forbidden input patterns
- Fail on raw path, regex, or diff as execution input

### P3.5 — Guardian determinism scanner (7.1)
- AST scan guardian files for LLM imports (`openai`, `anthropic`, `litellm`, etc.)
- Fail if any guardian file imports LLM libraries

### P3.6 — Adapter prohibition scanner in CI (from P0.2)
- Already created in P0.2, ensure it's gated

**P3 exit criteria**: E_CI_ENFORCED > 0 for all enforceable sub-capabilities. V15 compliance workflow green.

---

## P4 — Human-in-the-Loop & Advanced Cognitive Safety

**Goal**: Implement the human escalation flow and advanced cognitive features. These are the most complex and least urgent items.

### P4.1 — Human escalation flow (X6)
- **Gaps**: 2.6, 2.7, 2.7.1, 3.4, 3.5, 3.7
- CLI/API for human review of escalated manifests
- `EvidencePack` generation on escalation
- Ternary resolution (APPROVE/REJECT/MODIFY)
- `SignedModify` artifact on MODIFY
- `PolicyUpdateProposal` on human override
- `PolicyExceptionArtifact` for policy challenges

### P4.2 — Tiered Vigilance runtime (15.1)
- Wire `TieredVigilanceMonitor` into L6 observability agents
- Tier III → `EvacuationProtocol` execution

### P4.3 — Cognitive Diff Bundles for incident response (15.2)
- Wire `build_cognitive_diff_bundle()` into incident response flow

### P4.4 — Forensic Trace Buffer (15.3)
- Wire `ForensicTraceBuffer` into signal processing paths
- Velocity threshold enforcement

### P4.5 — Context Retrieval Request flow (3.8)
- Wire `ContextRetrievalRequest` into L0→L4 query path
- Enforce read-only constraint

**P4 exit criteria**: All 89 sub-capabilities COMPLIANT. Human review flow functional.

---

## Summary Table

| Phase | Items | Status → Target | Key Metric |
|-------|-------|-----------------|------------|
| **P0** | 4 FAIL + 3 missing types + discovery schema | FAIL → PARTIAL | 0 FAIL statuses |
| **P1** | ~35 PARTIAL items (Layer D) | D: 2.2% → 80%+ | Runtime wiring |
| **P2** | 33 MISSING items (Layers A+B+C) | MISSING → PARTIAL | 0 MISSING statuses |
| **P3** | All enforceable items (Layer E) | E: 0% → 100% | CI green |
| **P4** | ~12 advanced items | PARTIAL → COMPLIANT | Full compliance |

**Estimated total**: ~4,000 LOC new code + ~2,000 LOC modifications across ~50 files.

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

