# V15 Gap Remediation — Hardened Phased Implementation Plan

Phased plan to close 89 V15 target-state gaps (0% compliant → full compliance), prioritized P0–P4 by blast radius, dependency order, and safety criticality.  All hardening feedback from reconciliation review incorporated.

**Source**: `docs/reports/plans/v15_gap_analysis.json`
**Version**: 3.0 (A++ hardened)

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


## Cross-Cutting Invariant: No Parallel Schemas

**INV-1**: When V15 enforcement is enabled, every typed artifact at a runtime boundary MUST use the V15 canonical type.  Legacy/non-V15 schemas MUST NOT coexist at the same boundary.  This applies to:
- Guardian artifacts (X3: `GuardianArtifact` vs `SignedGuardianArtifact`)
- Route decisions (3.1: `contextual_router_config.RouteDecision` vs `v15_types.RouteDecisionArtifact`)
- Any future dual-schema discovered during implementation

**Enforcement**: At least one guardian test per schema boundary proves that the runtime imports and uses only the V15 type when V15 mode is on.

**INV-2**: Legacy (unsigned/non-V15) artifact types MUST be marked `@deprecated` and their constructors MUST raise `V15EnforcementError` when `V15_ENFORCEMENT=True`.  This prevents mid-pipeline consumption of unsigned artifacts — not just boundary escape.

**INV-3**: `V15_ENFORCEMENT` defaults to `False` during P0–P2 (safe rollout).  After P3 exit, CI MUST fail if `V15_ENFORCEMENT` defaults to `False` on the `main` branch.  This prevents permanent dark-launch drift.

**INV-4**: P4 MUST NOT introduce new V15 contract types or typed artifacts.  P4 composes existing primitives into end-to-end flows only.  Any new type required by P4 work MUST be back-ported to P2 and re-gated before use.

---

## Deterministic Gating Mechanism

Each phase gate is measured by regenerating the A–E coverage table from `v15_gap_analysis.json` schema.  A script (`ops_scripts/ci/v15_coverage_scoreboard.py`) enumerates every sub-capability's 5-layer booleans and produces a machine-readable report.

| Phase | Gate Metric | Threshold | Measurement |
|-------|-------------|-----------|-------------|
| P0 | FAIL count | == 0 | `by_status.FAIL == 0` |
| P1 | D_RUNTIME_WIRED | ≥ 80% | `by_layer.D_RUNTIME_WIRED.pct_complete >= 80.0` |
| P2 | MISSING count | == 0 | `by_status.MISSING == 0` |
| P3 | E_CI_ENFORCED | ≥ 95% of enforceable | `by_layer.E_CI_ENFORCED.pct_complete >= 95.0` (excl. process-only §14) |
| P4 | COMPLIANT count | == 89 (or 87 excl. §14) | `by_status.COMPLIANT >= 87` |

Phases are gated: P(N) exit criteria MUST pass before P(N+1) work begins.

---

## Priority Legend

| Priority | Meaning | Gate |
|----------|---------|------|
| **P0** | Resolve contradictions (FAIL) + schema conflicts + missing primitives | 0 FAIL statuses |
| **P1** | Runtime wiring — connect ALL existing contracts to execution paths | D ≥ 80% |
| **P2** | Build MISSING capabilities — new types, contracts, AST scanners | 0 MISSING statuses |
| **P3** | CI enforcement — gate all invariants in GitHub Actions | E ≥ 95% |
| **P4** | Human-in-the-loop flows + advanced cognitive safety | Full compliance |

---

## P0 — Resolve Contradictions, Schema Conflicts & Missing Primitives

**Goal**: Eliminate all FAIL statuses (4), resolve dual-schema conflicts, create missing typed artifacts.

### P0.1 — Single canonical Guardian artifact schema (X3, 7.2.1, 7.4)

**Problem**: Two competing schemas — `guardian_contract.py::GuardianResult/GuardianArtifact` vs `v15_p5_types.py::SignedGuardianArtifact`.  Runtime uses the non-V15 one.

**Resolution**: Single canonical model at runtime boundary.
1. Add `signature: str | None`, `trace_id: str | None`, `commit_hash: str | None` fields to `GuardianResult` (structurally unify)
2. Add `sign(enclave: SignatureEnclave) -> SignedGuardianArtifact` method on `GuardianResult` that produces the V15 signed artifact
3. Modify guardian runner: when `V15_ENFORCEMENT=True`, runner MUST call `sign()` before exit — **fail-closed** (unsigned artifact = FAIL)
4. Add guardian test: `test_guardian_runner_cannot_exit_unsigned_in_v15_mode`
5. `SignedGuardianArtifact` becomes a strict superset — legacy `GuardianArtifact` is an alias for the unsigned subset
6. **INV-2 enforcement**: Mark legacy `GuardianArtifact` constructor with `@deprecated`; add constructor guard that raises `V15EnforcementError` when `V15_ENFORCEMENT=True` — prevents mid-pipeline instantiation of unsigned artifacts, not just boundary escape

**Acceptance**: Guardian runner in V15 mode always produces signed artifact.  No unsigned artifacts pass through runtime boundary.  Legacy artifact type is unconstructable when V15 is on.

### P0.2 — Eliminate adapter pattern contradiction (8.1)

**Problem**: V15 prohibits adapters but `AdapterBase.py` + 4 adapter files exist.

**Current blast radius** (from grep):
- `AdapterBase.py` — base class (10 refs, all self-referential)
- `DomainPlannerAdapter.py` — only active consumer (imports AdapterBase)
- `SurgicalHealingAdapter.py`, `VerificationGateAdapter.py`, `HumanReviewAdapter.py` — zero importers
- `LocalDiskAdapter` — storage adapter in L4 (different pattern, 1 importer in `runtime_bootstrapper_util.py`)

**Resolution**:
1. Move `SurgicalHealingAdapter.py`, `VerificationGateAdapter.py`, `HumanReviewAdapter.py` to `archives/deprecated/` (zero importers, safe)
2. Refactor `DomainPlannerAdapter.py` to eliminate `AdapterBase` dependency — inline the needed logic or convert to a mixin
3. Move `AdapterBase.py` to `archives/deprecated/` with backwards-compat shim
4. `LocalDiskAdapter` is a storage provider pattern, not V15 "adapter pattern" — add explicit V15 exception annotation `# v15-exception: storage-provider-not-behavioral-adapter`
5. CI AST scanner (`ops_scripts/ci/check_adapter_prohibition.py`): fail on `class *Adapter*(AdapterBase)` or `import *AdapterBase*` outside `archives/`

**Acceptance**: No active runtime path imports `AdapterBase`.  CI scanner prevents re-introduction.  `LocalDiskAdapter` has explicit annotated exception.

### P0.3 — Route decision schema convergence (3.1, 3.2, 3.3)

**Problem**: `contextual_router_config.py::RouteDecision` is a parallel truth source vs `v15_types.py::RouteDecisionArtifact`.

**Current blast radius**: Only 1 file (`test_contextual_router_config.py`) imports `RouteDecision`. No production importers.

**Resolution**:
1. Replace `contextual_router_config.RouteDecision` enum with import of `v15_types.RoutePath`
2. Replace `contextual_router_config.RoutingResult` with V15 `RouteDecisionArtifact` (map fields)
3. Update `ContextualRouter` to emit `RouteDecisionArtifact` with `RoutingRationale` enum
4. Update test file to use V15 types
5. Add guardian test: `test_no_parallel_route_schemas` — AST scan for `class RouteDecision` outside v15_types

**Acceptance**: Single `RoutePath` + `RouteDecisionArtifact` used everywhere.

### P0.4 — Create missing typed artifacts (X4)

- **Gaps**: 1.7, 2.5, 12.2
- Add `HealingPlan` frozen dataclass to `v15_types.py` (fields: trace_id, plan_id, manifests, semantic_clock_tick, policy_liaison_node)
- Add `StaleWriteIncident` frozen dataclass to `v15_types.py` (fields: trace_id, target_path, expected_hash, actual_hash, semantic_clock_tick)
- Add `SideEffectRegistry` class to `v15_p6_types.py` (tracks touched resources per heal wave: paths_read, paths_written, apis_called)
- **Tests**: Construction + freeze + serialization for each

### P0.5 — Discovery JSON schema with hard contract (X5, 8.4)

1. Define `V15DiscoverySchema` as a frozen dataclass in `v15_p6_types.py` with ALL required fields: `identity`, `layer`, `status`, `file_path`, `class_name`, `mro_chain`, `mixins`, `detected_methods`, `integrity_hash`, `mro_signature`
2. `mro_signature` = SHA-256 of `"|".join(mro_chain)`
3. Extend `forensic_discovery_prep.py` output to emit all fields
4. Add guardian test: `test_discovery_schema_v15_complete` — fails if any required field is absent from discovery output
5. Pin discovery schema version in `v15_p6_types.py` constant

**Acceptance**: Discovery output validated against pinned schema.  Missing field = HARD FAIL.

### P0.6 — Coverage scoreboard script

- Create `ops_scripts/ci/v15_coverage_scoreboard.py`
- Reads `v15_gap_analysis.json`, computes A–E layer percentages and status counts
- Outputs machine-readable JSON report + human-readable summary
- Returns exit code 1 if gate thresholds not met (parameterized per phase)
- Used as gate check in all subsequent phases

**P0 exit criteria**: `v15_coverage_scoreboard.py --phase P0` returns exit code 0 (FAIL count == 0).

---

## P1 — Runtime Wiring (Layer D)

**Goal**: Connect ALL existing V15 contracts (4,044 LOC) to execution paths.  This phase addresses every sub-capability where A/B/C exist but D is false — the single largest gap.

### P1.1 — Wire V15ExecutionGateway into SovereignBaseAgent.heal()
- **Gaps**: 1.1, 1.2, 1.3, 1.6, 2.1, 2.5, 5.1
- Add `V15ExecutionGateway` as execution wrapper in `SovereignBaseAgent`
- Feature flag: `V15_ENFORCEMENT` env var (default False for safe rollout)
- When enabled, `heal()` calls go through gateway enforcing: SurgicalManifest input, forbidden input rejection, dedupe, pipe order
- **Scope**: Base class change → all 137+ agents inherit
- **Tests**: Integration test with mock heal_fn through gateway

### P1.2 — Wire PolicyConfigGuard + PolicyConfigPin into healing wave lifecycle
- **Gaps**: 4.1, 4.2, 4.3
- Wave start: `PolicyConfigGuard.load()` + `pin_policy_config()`
- Wave end: `verify_policy_config_unchanged()`
- Mutation detected → `PolicyMutationIncident` raised
- **Integration point**: `execute_ssot.py` or orchestrator wave entry

### P1.3 — Wire SemanticClock into state commit paths
- **Gaps**: 13.1, 13.1.1
- Instantiate `SemanticClock` per orchestration session
- Pass clock to `V15ExecutionGateway` (already supported)
- All state commits through `clock.tick(layer, state_commit_valid=True)`
- **Integration point**: `HealingTransactionBoundary` context manager

### P1.4 — Wire HealingTransactionBoundary + BoundarySnapshot into heal()
- **Gaps**: 10.1, 10.2, 10.3, 10.4
- Wrap heal execution in `HealingTransactionBoundary`
- Pre-mutation: `create_boundary_snapshot()`
- Post-failure: `verify_rollback_integrity()`
- RESULT emission: `validate_result_emission(layer)`

### P1.5 — Wire GuardrailGuard + artifact presence into guardian pipeline
- **Gaps**: 7.3, 7.5, 7.7
- Before guardian execution: `GuardrailGuard.enforce_all()`
- After guardian execution: `enforce_artifact_presence()`
- Before L2 heal admission: `aggregate_gate_check()`

### P1.6 — Wire LawSlotHandler + CapabilityDepletion into agent tool access
- **Gaps**: 3.6, 15.4
- Replace direct tool access with `LawSlotHandler.use_tool()`
- Depletion tracking per agent per wave
- **Integration point**: Base agent tool dispatch

### P1.7 — Wire boundary schema validation at layer crossings
- **Gaps**: 2.4, 12.1
- Add `validate_boundary_schema()` at each inter-layer message pass
- **Integration point**: Orchestrator dispatch / message bus

### P1.8 — Wire Trace ID format + TelemetryEmitter
- **Gaps**: 15.5, 15.6
- All V15 artifact constructors validate trace_id format via `validate_trace_id()`
- `generate_trace_id()` at orchestration session start
- After INCIDENT or RESULT emission: `TelemetryEmitter.emit()`

### P1.9 — Wire ReplayGuardStore + signature verification into guardian execution
- **Gaps**: 7.2, 7.4.1, 7.4.2
- Guardian runner: sign result via `sign_artifact()`, verify via `verify_signature()`
- Track artifact hashes via `ReplayGuardStore`

### P1.10 — Wire cognitive safety contracts (6.1, 6.2, 6.3, 6.4, 6.6–6.10)

**Moved from P2 — these are wiring of existing PARTIAL capabilities, not new primitives.**

- Wire `enforce_episodic_query_before_planning()` into planning agents (6.1)
- Wire `TrajectoryReuseConstraint` into trajectory reuse logic (6.2)
- Wire `TokenControlArtifact` emission before LLM calls (6.3)
- Wire `static_policy_alignment_check()` into cognitive response paths (6.4)
- Wire `knowledge_supervisor_check()` into L4 retrieval (6.6)
- Wire `PlanProvenance` generation into planning code (6.7)
- Wire `MemoryHypostate` generation into state commit paths (6.8)
- Wire `enforce_advisory_only()` into knowledge graph outputs (6.9)
- Wire `EpisodicSemanticLink` into episodic memory recording (6.10)

### P1.11 — Wire RAG Artifact Chain (6.5)

**Moved from P2.**

- Wire `RetrievalQuery → RetrievedChunks → RerankScores → CitationBundle` into RAG/retrieval code
- Validate chain end-to-end via `validate_citation_chain()`

### P1.12 — Wire budget guards (11.1, 11.2)

**Moved from P2.**

- Wire `TokenCapArtifact` emission before LLM calls
- Wire `RouteRecoveryBox` into token overflow handling

### P1.13 — Wire EvidencePack + PolicyExceptionArtifact + Context Retrieval
- **Gaps**: 3.4, 3.7, 3.8
- Wire `build_evidence_pack()` into escalation flow entry points
- Wire `emit_policy_exception()` into policy challenge paths
- Wire `ContextRetrievalRequest` into L0→L4 query path (read-only enforced)

### P1.14 — Wire Tiered Vigilance + SelfHealingTrigger + ErrorSignature
- **Gaps**: 5.2, 5.4, 15.1
- Wire `TieredVigilanceMonitor` into L6 observability agents
- Wire `SelfHealingTrigger` emission from L6, route to L2
- Wire `build_error_signature()` into agent error handlers

### P1.15 — Wire Hash Mismatch escalation + AGGREGATE emission
- **Gaps**: 2.6, 2.8
- Wire `HashMismatchTracker` into healing wave
- Wire `AggregateArtifact` emission on conditional outcomes

**P1 exit criteria**: `v15_coverage_scoreboard.py --phase P1` returns exit code 0 (D_RUNTIME_WIRED.pct_complete >= 80.0).

**Critical D-set** (must be 100% wired regardless of overall percentage):

| ID | Contract | Rationale |
|----|----------|-----------|
| 1.1 | V15ExecutionGateway in base heal() | Entry point for all enforcement |
| 7.4 | Guardian signing (sign_artifact) | P5 tokenized authority |
| 10.1 | HealingTransactionBoundary | Atomicity guarantee |
| 4.2 | PolicyConfigPin at wave start | P3 immutability |
| 13.1 | SemanticClock in state commits | P2 determinism |
| 15.5 | Trace ID generation | Traceability foundation |

If any critical D-set item is D=false, the P1 gate fails even if overall D ≥ 80%.

---

## P2 — Build MISSING Capabilities (Layers A+B+C only)

**Goal**: Create types, contracts, and tests for sub-capabilities where NO implementation exists.  This phase contains ONLY new-primitive work — all wiring of existing primitives was moved to P1.

### P2.1 — MRO enforcement (8.3, 8.4, 8.5)
- AST scanner: verify safety mixins LEFT of base classes in MRO
- MRO verification against discovery JSON `mro_signature` (from P0.5)
- MRO violation = HARD FAIL
- **SSOT constraint**: MRO scanner MUST consume ONLY the pinned `V15DiscoverySchema` discovery JSON as its class-structure source — no live `inspect.getmro()` reflection fallback.  This guarantees SSOT discipline and prevents scanner results from diverging from the auditable discovery artifact.
- **Output**: `ops_scripts/ci/check_mro_ordering.py`
- **Tests**: Parametrized tests for correct/incorrect MRO ordering

**Acceptance**: MRO scanner reads pinned discovery JSON only.  Live reflection = HARD FAIL in scanner.

### P2.2 — Separation of responsibilities scanners (9.1, 9.2, 9.3)
- AST scanner: shared mixins contain no domain-specific logic
- AST scanner: `heal()` methods contain no adapter/factory/orchestrator delegation
- **Output**: `ops_scripts/ci/check_separation_of_responsibilities.py`

### P2.3 — Validator safety emulation (2.2)
- Define `SafetyEmulationResult` typed artifact
- Implement sandbox pre-flight: apply manifest to in-memory AST copy, diff, validate
- Contract + tests

### P2.4 — Validator L5 permission check (2.3)
- Define `PermissionCheckResult` typed artifact
- Validator queries L5 Guardian rules before passing manifest to healer
- Fail-closed: no permission = no heal

### P2.5 — Root Scope Pinning for signal collapse (5.3, 5.5)
- Define `RootScopePin` typed artifact
- Correlated signals collapse to single root cause before INCIDENT emission
- Deterministic correlation hash required before INCIDENT emission

### P2.6 — Layer write-capability enforcement (12.3)
- Define `LayerCapability` enum (READ_ONLY, READ_WRITE)
- AST scanner: L0/L4/L6 agents must not call file-write, git-commit, or state-mutation APIs
- **Output**: `ops_scripts/ci/check_layer_write_capability.py`

### P2.7 — Human resolution flow primitives (2.7, 2.7.1)
- Contract for `HumanResolution` ternary flow (APPROVE/REJECT/MODIFY)
- Builder for `SignedModify` artifact generation
- These are primitives (A+B+C); wiring into a full UI/CLI is P4

### P2.8 — PolicyUpdateProposal builder contract (3.5)
- Builder for bidirectional feedback on human override
- Primitive only; full flow is P4

**P2 exit criteria**: `v15_coverage_scoreboard.py --phase P2` returns exit code 0 (MISSING count == 0).

---

## P3 — CI Enforcement (Layer E)

**Goal**: Gate every V15 invariant in CI.  Currently E_CI_ENFORCED = 0%.

### P3.1 — V15 compliance CI workflow
- New `.github/workflows/v15-compliance.yml`
- Runs all `tests/guardian/test_v15_p*_compliance.py` tests
- Runs `v15_coverage_scoreboard.py --phase P3` as gate
- Gates on pass/fail

### P3.2 — Wall-clock AST scanner in CI (13.2)
- Wire `ast_scan_wall_clock()` into CI
- Scan all V15 contract files + agent files for forbidden wall-clock callables

### P3.3 — Meta-Guardian coverage gate (7.6)
- Wire `meta_guardian_check()` into CI
- Require ≥ 95% invariant coverage
- Measure via `run_meta_invariants()` report

### P3.4 — Forbidden input scanner in CI (1.2)
- AST scan all `heal()` methods for forbidden input patterns
- Fail on raw path, regex, or diff as execution input

### P3.5 — Guardian determinism scanner (7.1)
- AST scan guardian files for LLM imports
- Fail if any guardian file imports LLM libraries

### P3.6 — No-parallel-schemas guardian test (INV-1)
- AST scan for duplicate typed artifact definitions at runtime boundaries
- `test_no_parallel_guardian_schemas`, `test_no_parallel_route_schemas`
- Fail if non-V15 schema is used at any boundary when V15 enabled

### P3.7 — Adapter prohibition scanner (P0.2 backstop)
- Run `check_adapter_prohibition.py` in CI
- Fail on `AdapterBase` import outside `archives/`

### P3.8 — MRO + Separation + Layer-write scanners in CI
- Wire scanners from P2.1, P2.2, P2.6 into CI workflow

### P3.9 — V15_ENFORCEMENT kill-switch enforcement (INV-3)
- Add CI check: on `main` branch, `V15_ENFORCEMENT` env var default MUST be `True`
- Scanner verifies that base agent configuration sets `V15_ENFORCEMENT=True` by default
- Fail if default is `False` after P3 merge

**P3 exit criteria**: `v15_coverage_scoreboard.py --phase P3` returns exit code 0 (E_CI_ENFORCED.pct_complete >= 95.0, excluding process-only §14).  `V15_ENFORCEMENT` defaults to `True` on `main`.

---

## P4 — Human-in-the-Loop & Advanced Features

**Goal**: Implement end-to-end human escalation flow and advanced cognitive/L6 features.

**INV-4 enforcement**: P4 MUST NOT introduce new V15 contract types or typed artifacts.  All work in this phase composes existing primitives (from P0–P2) into end-to-end flows.  If a new type is discovered as needed, it MUST be back-ported to P2, gated, and merged before P4 work resumes.

### P4.1 — Human escalation flow (X6)
- **Gaps**: 2.6, 2.7, 2.7.1, 3.4, 3.5, 3.7
- CLI/API for human review of escalated manifests
- `EvidencePack` generation on escalation
- Ternary resolution (APPROVE/REJECT/MODIFY) with `SignedModify`
- `PolicyUpdateProposal` on human override
- `PolicyExceptionArtifact` for policy challenges

### P4.2 — Tiered Vigilance runtime integration (15.1)
- Full `TieredVigilanceMonitor` → `EvacuationProtocol` execution chain in L6

### P4.3 — Cognitive Diff Bundles for incident response (15.2)
- Wire `build_cognitive_diff_bundle()` into incident response flow

### P4.4 — Forensic Trace Buffer (15.3)
- Wire `ForensicTraceBuffer` into signal processing paths
- Velocity threshold enforcement at runtime

### P4.5 — Context Retrieval Request full flow (3.8)
- Complete L0→L4 query path with read-only constraint enforcement

**P4 exit criteria**: `v15_coverage_scoreboard.py --phase P4` returns exit code 0 (COMPLIANT count >= 87).

---

## Summary

| Phase | Work Items | Status Transition | Gate |
|-------|-----------|-------------------|------|
| **P0** | 6 | 4 FAIL → 0 FAIL; schema conflicts resolved; missing types created | `FAIL == 0` |
| **P1** | 15 | D: 2.2% → ≥80%; all existing contracts wired to runtime | `D >= 80%` |
| **P2** | 8 | 33 MISSING → 0 MISSING; new primitives with A+B+C coverage | `MISSING == 0` |
| **P3** | 9 | E: 0% → ≥95%; all invariants gated in CI; V15 default=True | `E >= 95%` + INV-3 |
| **P4** | 5 | PARTIAL → COMPLIANT; human-in-the-loop functional | `COMPLIANT >= 87` |

**Estimated scope**: ~5,000 LOC new code + ~2,500 LOC modifications across ~60 files.

---

## Reconciliation Changelog

### v1 → v2

1. **P0.1 rewritten**: Optional fields → single canonical model + fail-closed signing in V15 mode
2. **P0.2 rewritten**: CI scanner only → eliminate runtime adapter dependencies + CI scanner as backstop
3. **P0.3 added**: Route decision schema convergence (was buried in P2.11)
4. **P2.8–P2.11 moved to P1**: Wiring of existing PARTIAL capabilities belongs in P1, not P2
5. **Deterministic gating added**: `v15_coverage_scoreboard.py` with numeric thresholds per phase
6. **INV-1 added**: Cross-cutting "no parallel schemas" invariant with guardian tests
7. **P0.5 hardened**: Discovery schema pinned as typed dataclass with guardian test (not just "extend output")

### v2 → v3 (A++ hardening)

8. **INV-2 added**: Legacy artifact constructors raise `V15EnforcementError` when V15 enabled — eliminates mid-pipeline unsigned artifact consumption (P0.1 step 6)
9. **INV-3 added**: `V15_ENFORCEMENT` kill-switch policy — must default to `True` on `main` after P3 exit (P3.9)
10. **P2.1 hardened**: MRO scanner must consume ONLY pinned discovery JSON — no live reflection fallback
11. **Critical D-set added**: 6 high-leverage contracts must be 100% D=true regardless of overall P1 percentage
12. **INV-4 added**: P4 cannot introduce new contract types — compose only, back-port if needed

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

