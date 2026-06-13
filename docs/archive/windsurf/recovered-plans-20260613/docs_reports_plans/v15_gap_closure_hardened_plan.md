# V15 Gap Closure — Hardened Implementation Plan

Hardened, execution-ready version of the V15 Gap Closure Implementation Plan, produced by the Deterministic Guardian subsystem reviewer.

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


## PHASE 1 — STRUCTURAL CRITIQUE

### 1.1 Critical Findings

| ID | Finding | Severity | Location | Impact |
|----|---------|----------|----------|--------|
| S1 | `SovereignBaseAgent._v15_enhanced_heal()` already routes through `V15ExecutionGateway` when `V15_ENFORCEMENT=1`. Original plan ignores this existing wiring and risks duplication. | HIGH | `SovereignBaseAgent.py:252-329` | Plan Phase 7.1 must be scoped as a *fix* of existing wiring, not greenfield. |
| S2 | `V15ExecutionGateway` is instantiated per-heal-call (`gateway = V15ExecutionGateway()`). SemanticClock resets to 0 every call. Dedupe set is empty every call. Both invariants (§13.1 tick persistence, §5.1 dedupe across signals) are silently violated. | CRITICAL | `SovereignBaseAgent.py:280` | Gateway must be promoted to agent-level or wave-level singleton. |
| S3 | `trace_id` generated via `uuid.uuid4()` (format: `a1b2c3d4-...`). §15.5 requires `^CC3AL1-[0-9A-F]{8}$`. Live format violation. | CRITICAL | `SovereignBaseAgent.py:257` | Must be fixed as a prerequisite before any downstream artifact emission. |
| S4 | `state_hash_fn()` returns placeholder strings `("fs_hash", "git_hash", "mem_hash")`. `BoundarySnapshotArtifact` is produced with garbage hashes. Rollback verification always trivially passes. | CRITICAL | `SovereignBaseAgent.py:297-300` | Renders §10.2/§10.3 compliance non-functional. Must be replaced with real hash computation. |
| S5 | `heal_fn` inner closure references `manifest.payload` and `manifest.trace_id` — neither field exists on `SurgicalManifest`. Runtime crash when `V15_ENFORCEMENT=1`. | CRITICAL | `SovereignBaseAgent.py:286,294` | Live bug. Must be fixed before any enforcement testing. |
| S6 | Phase 7.1 (base class edit) has blast radius of 149 agents. Original plan rates this "Low risk (additive only)" — incorrect. | HIGH | Plan Tier 1 | Must use mixin injection or shadow mode, not direct `__init__` edit. |
| S7 | `V15_ENFORCEMENT` is a single global flag. No per-artifact or per-capability granularity. Cannot progressively enable enforcement. | HIGH | `v15_runtime_guard.py:is_v15_enforced()` | Must add granular enforcement flags or a shadow/log-only mode. |
| S8 | Phase 7.3 (CI gates — safe, additive) is bundled with Phase 7.1-7.2 (base class + gateway edits — high blast radius) in same tier. | MEDIUM | Plan Tier 1 | Must separate purely additive work from mutation-risk work. |

### 1.2 Hidden Assumptions

| ID | Assumption | Validity | Mitigation |
|----|-----------|----------|------------|
| A1 | "Types are ~95% complete" implies wiring is straightforward | PARTIALLY VALID | Types exist; but contracts are never called from production code outside `SovereignBaseAgent._v15_enhanced_heal()`. Wiring requires integration, not just imports. |
| A2 | `332 guardian tests pass` implies contracts are exercised | INVALID | Tests exercise types and contracts in isolation. No test verifies runtime emission from an actual agent heal path. |
| A3 | `V15ExecutionGateway` is a working integration point | PARTIALLY VALID | Gateway executes the correct contract sequence, but is instantiated fresh each call (no state persistence) and receives placeholder hashes. |
| A4 | 28 P2 entrypoints can all be converted uniformly | INVALID | Entrypoints span 5 distinct categories (orchestrators, engines, mission runner modes, mixin methods, bootstrap scripts). Each requires category-specific manifest construction. |

---

## PHASE 2 — RUNTIME ENFORCEMENT GAPS

### 2.1 Type-Presence vs Runtime-Emission Matrix

| § | Artifact | Type Defined | Contract Exists | Called at Runtime | Runtime Probe Needed |
|---|----------|:---:|:---:|:---:|:---:|
| §1.3 | `SurgicalManifest` | YES | YES (`v15_p2_contracts`) | YES (base agent only, with bugs S3/S5) | Fix bugs, then verify via integration test |
| §2.5 | `PipeOrderEnforcer` | YES | YES (`v15_contracts`) | NO | Add to gateway execution path |
| §2.6 | `HashMismatchTracker` | YES | YES (`v15_p5_contracts`) | NO | Wire into gateway rollback path |
| §2.8 | `AggregateArtifact` | YES | YES (`v15_contracts::aggregate_gate_check`) | NO | Emit from validator pre-heal path |
| §3.4 | `EvidencePack` | YES | YES (`v15_p3_contracts`) | NO | Wire into human escalation trigger |
| §3.6 | `LawSlotHandler` | YES | YES (`v15_contracts`) | NO | Deferred: requires tool isolation redesign |
| §4.1 | `PolicyConfigGuard` | YES | YES (`v15_contracts`) | NO | Wire into gateway wave-start |
| §5.1 | SHA-256 dedupe | YES | YES (`v15_p2_contracts`) | YES (gateway, but stateless — resets each call) | Promote dedupe set to agent/wave scope |
| §5.2 | `ErrorSignature` | YES | YES (`v15_p4_contracts`) | NO | Wire into L6 observability agents |
| §6.3 | `TokenControlArtifact` | YES | NO contract | NO | Add contract + wire pre-LLM |
| §6.5 | RAG chain (4 types) | YES | YES (`v15_p4_contracts`) | NO | Deferred: requires L1/L4 integration |
| §7.2 | `ReplayGuardStore` | YES | YES (`v15_p5_contracts`) | NO | Wire into gateway or base agent |
| §7.2.1 | `SignedGuardianArtifact` | YES | YES (`v15_p5_contracts`) | NO | Wire into guardian test output |
| §7.4.1 | `SignatureEnclave` | YES | YES (`v15_p5_contracts`) | NO | Deferred: requires key management |
| §10.2 | `BoundarySnapshotArtifact` | YES | YES (`v15_p2_contracts`) | YES (gateway, but placeholder hashes) | Replace placeholder with real hashes |
| §10.4 | `validate_result_emission` | YES | YES (`v15_contracts`) | NO | Wire into RESULT emission path |
| §12.1 | `BoundarySchemaDescriptor` | YES | YES (`v15_p6_contracts`) | NO | Deferred: requires cross-layer schema registry |
| §12.2 | `SideEffectRegistry` | YES | NO contract | NO | Add contract + wire into heal path |
| §13.1 | `SemanticClock` | YES | YES (`v15_p2_contracts`) | YES (gateway, but resets each call) | Promote to agent/wave scope |
| §15.1 | `TieredVigilanceMonitor` | YES | YES (`v15_contracts`) | NO | Deferred: requires L6 integration |
| §15.3 | `ForensicTraceBuffer` | YES | YES (`v15_p2_contracts`) | NO | Deferred: requires L6 integration |
| §15.5 | `validate_trace_id` | YES | YES (`v15_p4_contracts`) | NO (base agent uses uuid4 — S3) | Fix trace_id generation first |

### 2.2 Misclassification Risks

| Risk | Description | Trigger Condition | Consequence |
|------|------------|-------------------|-------------|
| R1 | `RESULT` emitted from non-L2 layer | Agent in L0/L5/L6 calls a method that creates `ResultArtifact` | §10.4 violation. `validate_result_emission()` exists but is never called at runtime. |
| R2 | `AGGREGATE` emitted on terminal flow | Gateway success path creates aggregate instead of result | §2.8 violation. No runtime guard distinguishes conditional vs terminal flows. |
| R3 | Late trace_id assignment | Artifact emitted before trace_id is generated | §15.5 violation. trace_id must be first operation in any execution path. |
| R4 | SemanticClock tick without valid StateCommit | Clock ticked on partial success | §13.1.1 violation. Gateway handles this correctly, but only when gateway is used. Non-gateway paths have no clock at all. |

---

## PHASE 3 — RISK ISOLATION & ROLLBACK HARDENING

### 3.1 Enforcement Sequencing (Three Modes)

| Mode | Behavior | Flag Value | Purpose |
|------|----------|-----------|---------|
| **LOG_ONLY** | Construct artifacts, log to structured audit trail, never block | `V15_ENFORCEMENT=log` | Catch wiring bugs without breaking production |
| **SOFT_FAIL** | Construct artifacts, validate, log violations, emit warnings, do not block | `V15_ENFORCEMENT=soft` | Measure violation rate before hard cutover |
| **HARD_FAIL** | Construct artifacts, validate, block on violation (current `=1` behavior) | `V15_ENFORCEMENT=1` | Production enforcement |

### 3.2 Redesigned Phase Structure

| Original Phase | Risk | Redesigned Phase | Isolation Strategy |
|---------------|------|-----------------|-------------------|
| 7.1 SovereignBaseAgent protocol | HIGH (149-agent blast) | **7.0 Bug fixes** (S3, S4, S5) + **7.1a Mixin** (`V15ArtifactEmitterMixin`) | Fix bugs in isolation first. New mixin avoids base class `__init__` edit. Base agent inherits mixin via MRO addition (single LOC). |
| 7.2 Gateway runtime integration | MEDIUM | **7.1b Gateway singleton** | Promote gateway to agent-level `__init__`, not per-call. Single edit to `_v15_enhanced_heal`. |
| 7.3 CI Gates P3-P6 | LOW (purely additive) | **7.2 CI Gates** (moved earlier) | No production code touched. Safe to run first. |
| 8.1 Validator→Healer pipe | MEDIUM | **8.1a-e** (5 sub-phases by category) | Each agent category wired independently. Per-category rollback boundary. |
| 8.2 TokenCap wiring | MEDIUM | **8.2** (unchanged) | Gated by `V15_ENFORCEMENT=log` initially |
| 8.3 Signal dedup | LOW-MEDIUM | **8.3** (unchanged) | L6 agents only. No cross-layer blast. |
| 9.1-9.4 Advanced protocols | HIGH | **Deferred** with justification | Require multi-layer integration. Must wait for Tier 1+2 to stabilize. |
| 10.1-10.4 Hardening | LOW | **10.1-10.4** (unchanged) | AST scans and CI gates only. No production mutation. |

### 3.3 Rollback Boundaries

| Phase | Rollback Unit | Rollback Mechanism | Blast Radius |
|-------|-------------|-------------------|-------------|
| 7.0 | 3 bug fixes in `SovereignBaseAgent.py` | `git revert` single commit | 1 file, affects V15-enabled path only |
| 7.1a | New `V15ArtifactEmitterMixin` file + 1 LOC in base agent MRO | Delete mixin file + revert MRO line | 1 new file + 1 LOC edit |
| 7.1b | Gateway promotion to agent-level | Revert `_v15_enhanced_heal` to per-call instantiation | 1 method |
| 7.2 | 4 new CI gate scripts | Delete scripts | 0 production code touched |
| 8.1a-e | Per-category agent edits | Revert category-specific commits | 3-8 files per category |

---

## PHASE 4 — ACCEPTANCE CRITERIA HARDENING

### 4.1 Binary Exit Conditions Per Phase

| Phase | Exit Condition | CI Command | Pass Definition |
|-------|---------------|-----------|-----------------|
| **7.0** | Bug fixes verified | `python -m pytest tests/guardian/test_v15_p7_bugfixes.py -x` | 0 failures. Tests assert: (a) trace_id matches `^CC3AL1-[0-9A-F]{8}$`, (b) `state_hash_fn` returns non-placeholder hashes, (c) `heal_fn` does not reference `manifest.payload` or `manifest.trace_id`. |
| **7.1a** | Mixin importable, base agent MRO includes it, `V15_ENFORCEMENT=log` produces structured log entries | `V15_ENFORCEMENT=log python -m pytest tests/guardian/test_v15_p7_mixin.py -x` | 0 failures. Tests assert: (a) `V15ArtifactEmitterMixin` in `SovereignBaseAgent.__mro__`, (b) heal path emits structured JSON log with `trace_id`, `semantic_clock_tick`, `artifact_type` fields. |
| **7.1b** | Gateway singleton verified | `python -m pytest tests/guardian/test_v15_p7_gateway_singleton.py -x` | 0 failures. Tests assert: (a) `self._v15_gateway` is same object across 2 heal calls, (b) `SemanticClock.step_id > 0` after second heal, (c) dedupe set contains entries from first heal. |
| **7.2** | P3-P6 gates produce evidence JSON | `python ops_scripts/ci/run_v15_p3_gate.py && python ops_scripts/ci/run_v15_p4_gate.py && python ops_scripts/ci/run_v15_p5_gate.py && python ops_scripts/ci/run_v15_p6_gate.py` | All 4 exit code 0. Evidence JSON written to `docs/reports/plans/`. |
| **8.1a** | Category A agents (orchestrators) emit `SurgicalManifest` via gateway | `V15_ENFORCEMENT=log python -m pytest tests/guardian/test_v15_p8_cat_a.py -x` | 0 failures. Tests assert: (a) `orchestrator_engine.execute()` constructs `SurgicalManifest`, (b) manifest passes `verify_hash()`, (c) gateway result logged with valid `semantic_clock_tick`. |
| **8.1b-e** | Categories B-E follow same pattern | Per-category test suites | Same structure as 8.1a adapted to each category |
| **8.2** | TokenCap emitted before LLM calls | `V15_ENFORCEMENT=log python -m pytest tests/guardian/test_v15_p8_tokencap.py -x` | 0 failures. Tests assert: (a) `TokenCapArtifact` logged before LLM call, (b) `gate_result` is `ALLOW` or `DENY`, (c) `DENY` prevents LLM invocation. |
| **8.3** | Error signatures use semantic clock | `V15_ENFORCEMENT=log python -m pytest tests/guardian/test_v15_p8_dedup.py -x` | 0 failures. Tests assert: (a) `ErrorSignature.time_bucket` is semantic tick not wall clock, (b) duplicate signals collapsed. |

### 4.2 Missing Acceptance Gates (Added)

| Gate | Purpose | Phase Dependency |
|------|---------|-----------------|
| **Runtime Emission Probe** | Verify artifacts are actually constructed (not just importable) during a real agent heal path | Required for 7.1a exit |
| **Flow-Correctness Gate** | Verify AGGREGATE on conditional flows, RESULT on terminal flows | Required for 8.1a exit |
| **Cross-Layer Mutation Gate** | Verify L0/L4/L6 agents do not call `validate_result_emission` with success | Required for 8.1e exit |
| **Replay Determinism Gate** | Same input + same policy → same artifact sequence (hash comparison) | Required for Tier 3 entry |

---

## PHASE 5 — HARDENED PLAN

### Tier 0 — Prerequisite Bug Fixes (MUST precede all other work)

| Phase | Scope | Risk | Changes | Exit Condition |
|-------|-------|------|---------|---------------|
| **7.0a** | Fix trace_id format: replace `uuid.uuid4()` with `generate_trace_id()` from `v15_p4_contracts` in `SovereignBaseAgent._v15_enhanced_heal()` | LOW (1 line in V15-only path) | `SovereignBaseAgent.py:257` — replace `str(uuid.uuid4())` with `generate_trace_id(secrets.token_hex(4).upper())` | `validate_trace_id(trace_id)` does not raise |
| **7.0b** | Fix dead field references: `manifest.payload` → violation dict passthrough; `manifest.trace_id` → `trace_id` local variable | LOW (2 lines in V15-only path) | `SovereignBaseAgent.py:286,294` — remove references to nonexistent fields | `V15_ENFORCEMENT=1 python -c "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent"` does not crash |
| **7.0c** | Fix placeholder state hashes: replace literal strings with real SHA-256 of project root contents | MEDIUM (touches state computation) | `SovereignBaseAgent.py:297-300` — compute `hashlib.sha256` of git HEAD, project root mtime, and agent class name | Pre/post hashes differ after a real mutation |

**Risk note**: All 7.0 changes are inside `_v15_enhanced_heal()` which only executes when `V15_ENFORCEMENT` is non-zero. Zero risk to default (`V15_ENFORCEMENT=0`) code paths.

### Tier 1A — Additive Infrastructure (Zero production mutation)

| Phase | Scope | Risk | Changes | Exit Condition |
|-------|-------|------|---------|---------------|
| **7.2** | CI Gates P3-P6 | ZERO (new files only) | 4 new scripts in `ops_scripts/ci/`: `run_v15_p3_gate.py`, `run_v15_p4_gate.py`, `run_v15_p5_gate.py`, `run_v15_p6_gate.py`. Modeled on existing `run_v15_p2_gate.py`. | All 6 gates (P0-P6) exit code 0 |

**Risk note**: No production code modified. Gates can fail without blocking anything until explicitly added to CI pipeline.

### Tier 1B — Gateway & Clock Hardening (V15-path only)

| Phase | Scope | Risk | Changes | Exit Condition |
|-------|-------|------|---------|---------------|
| **7.1a** | Add `V15_ENFORCEMENT=log` mode to `is_v15_enforced()` | LOW (additive branch) | `v15_runtime_guard.py` — add `is_v15_log_mode()` check. Return `False` from `is_v15_enforced()` when `=log`, but expose mode for callers. | `is_v15_log_mode()` returns `True` when `V15_ENFORCEMENT=log` |
| **7.1b** | Promote gateway to agent-level singleton | LOW (V15-only path) | `SovereignBaseAgent.__post_init__` — add `self._v15_gateway = V15ExecutionGateway()`. `_v15_enhanced_heal()` — use `self._v15_gateway` instead of local instantiation. | SemanticClock.step_id increments across heal calls; dedupe set persists |
| **7.1c** | Wire `PipeOrderEnforcer` into gateway execution | LOW (gateway internals only) | `v15_execution_gateway.py` — instantiate `PipeOrderEnforcer` in `execute()`, call `advance()` at each step | `PipeOrderViolation` raised on out-of-order step in test |
| **7.1d** | Wire `PolicyConfigGuard` into gateway | LOW (gateway internals only) | `v15_execution_gateway.py` — accept `policy_config` param, create guard at wave start | `PolicyMutationIncident` raised on config change in test |
| **7.1e** | Wire `HashMismatchTracker` into gateway rollback path | LOW (gateway internals only) | `v15_execution_gateway.py` — track mismatches, raise `EscalationRequiredError` at threshold | Escalation triggered after 2 mismatches in test |

**Risk note**: All changes in V15-enforcement-only code path. Default path (`V15_ENFORCEMENT=0`) unchanged.

### Tier 2 — Agent Wiring (Per-Category, LOG_ONLY first)

| Phase | Category | Agents | Risk | Exit Condition |
|-------|----------|--------|------|---------------|
| **8.1a** | A: Orchestrators | `orchestrator_engine.py`, `NervousSystemAgent.py`, `security_level_config.py` | MEDIUM (3 files) | `V15_ENFORCEMENT=log` — structured log shows `SurgicalManifest` + `AggregateArtifact` emitted per heal |
| **8.1b** | B: Engines | `agent_engine.py`, `SubatomicHopAgent.py`, `SovereignActionPlaneAgent.py` | MEDIUM (3 files) | Same log verification pattern |
| **8.1c** | C: Mission Runner | `mission_runner.py` (3 modes: daemon, surgical, standard) | MEDIUM (1 file, 3 paths) | Same log verification pattern per mode |
| **8.1d** | D: Mixin retry | `tool_reliability_mixin.py` (with_retry, with_retry_sync) | LOW (1 file, mixin-scoped) | Same log verification pattern |
| **8.1e** | E: Bootstrap | `execute_ssot.py` via `execute_ssot_entrypoint.py` | LOW (entrypoint only) | Same log verification pattern |
| **8.2** | TokenCap pre-LLM | All agents with LLM calls (via `prepare_messages_for_llm`) | MEDIUM (base agent method) | `TokenCapArtifact` logged before every `llm_client.complete()` call |
| **8.3** | Signal dedup | L6 observability agents | LOW (isolated layer) | `ErrorSignature` uses `semantic_clock_tick` not wall clock |

**Risk note**: All Tier 2 work starts in `LOG_ONLY` mode. Promotion to `SOFT_FAIL` requires Phase 7.1b exit conditions met. Promotion to `HARD_FAIL` requires 0 violations logged for 3 consecutive CI runs.

### Tier 3 — Advanced Protocols (DEFERRED with justification)

| Phase | Capability | Deferral Justification |
|-------|-----------|----------------------|
| **9.1** | RAG Artifact Chain (§6.5) | Requires L1/L4 agent integration. No L1/L4 agents currently consume V15 types. Must wait for Tier 2 to establish the wiring pattern. |
| **9.2** | Guardian Signing (§7.4) | Requires key management infrastructure (`TrustRoot` population, key rotation). `DeterministicTestEnclave` works for tests but is not production-ready. |
| **9.3** | Human Escalation (§2.6/§3.4) | Requires `HashMismatchTracker` to be wired (Tier 1B prerequisite) and a human review UI/API. No such interface exists. |
| **9.4** | Tiered Monitoring (§15.1-§15.3) | Requires L6 observability agents to emit `IncidentArtifact`. No L6 agent currently does. Must wait for Tier 2 Phase 8.3. |

**Entry criteria for Tier 3**: All Tier 1B and Tier 2 exit conditions met. At least one full CI pipeline run in `SOFT_FAIL` mode with 0 violations.

### Tier 4 — CI Hardening (Additive AST scans)

| Phase | Scope | Risk | Exit Condition |
|-------|-------|------|---------------|
| **10.1** | Wall-clock AST scan | ZERO (read-only scan) | `ast_scan_wall_clock()` run repo-wide. 0 violations in hash/signature/dedup paths. |
| **10.2** | MRO safety mixin LEFT verification | ZERO (read-only scan) | Discovery JSON `mro_chain` verified: safety mixins left of base classes for all 149 agents. |
| **10.3** | Read-only layer enforcement (L0/L4/L6) | ZERO (read-only scan) | AST scan confirms L0/L4/L6 agents have no `open(mode='w')`, `Path.write_text`, `subprocess.run`, `os.makedirs` in non-guarded paths. |
| **10.4** | Meta-Guardian 95% gate | ZERO (CI gate) | `meta_guardian_check(total, covered) >= 0.95` passes. |

---

### Summary: Original Plan vs Hardened Plan

| Dimension | Original | Hardened |
|-----------|----------|---------|
| Prerequisite bug fixes | Not identified | 3 critical bugs (S3, S4, S5) in Tier 0 |
| Enforcement modes | Binary (on/off) | Three modes (LOG_ONLY → SOFT_FAIL → HARD_FAIL) |
| Base class edit strategy | Direct `__init__` edit (149-agent blast) | Gateway singleton in V15-only path (0 blast to default path) |
| Phase granularity | 4 tiers, 12 phases | 5 tiers, 20 phases with per-category isolation |
| Acceptance criteria | Tier-level, qualitative | Per-phase, binary, CI-verifiable |
| Rollback boundaries | Per-tier | Per-phase, single-commit revertible |
| Deferred work | Implicit | Explicit with entry criteria and justification |
| Runtime emission verification | Not addressed | Required via LOG_ONLY mode + structured log assertions |
| Agent category isolation | All 28 entrypoints in one phase | 5 sub-phases by category (A-E), independent rollback |

---

## REVIEW PASS 2 — HARDENED DELTA

Second-pass deterministic review of the hardened plan itself, identifying internal contradictions, residual risks, enforcement gaps, rollback hazards, and acceptance criteria weaknesses. Output is a correction delta only.

---

### R2-1 Internal Consistency Audit

| ID | Contradiction | Severity | Affected Phases | Resolution |
|----|--------------|----------|----------------|------------|
| IC1 | Phase 7.1a says `is_v15_enforced()` returns `False` when `V15_ENFORCEMENT=log`. But `SovereignBaseAgent.heal()` at line 237 gates on `if is_v15_enforced()` to enter `_v15_enhanced_heal()`. If `False`, the V15 path is never reached. **LOG_ONLY mode is dead code under the current plan.** | CRITICAL | 7.1a, all Tier 2 | `is_v15_enforced()` must return `True` for `log`, `soft`, AND `1`. Add separate `is_v15_hard_fail()` for blocking decisions. `heal()` enters V15 path for all three modes. Internal contract functions check `is_v15_hard_fail()` before raising. |
| IC2 | `is_v15_enforced()` is defined in `guardian_contract.py:35`, NOT in `v15_runtime_guard.py`. Base agent imports from `guardian_contract.py`. Plan Phase 7.1a targets `v15_runtime_guard.py` for the LOG_ONLY change — wrong file. | HIGH | 7.1a | Phase 7.1a must modify `guardian_contract.py`, not `v15_runtime_guard.py`. `v15_runtime_guard.py` re-imports from `guardian_contract.py` and inherits the change. |
| IC3 | Phase 7.1b adds `self._v15_gateway = V15ExecutionGateway()` in `__post_init__`. This runs for ALL 149 agents regardless of `V15_ENFORCEMENT`. Unconditional gateway instantiation wastes memory and creates 149 independent SemanticClocks. | MEDIUM | 7.1b | Guard instantiation: `self._v15_gateway = V15ExecutionGateway() if is_v15_enforced() else None`. `_v15_enhanced_heal` checks `self._v15_gateway is not None`. |
| IC4 | Phase 7.0b exit condition is `python -c "from ... import SovereignBaseAgent"` — this tests import, not execution. The `manifest.payload` bug only crashes during `heal()`, not during import. Exit condition does not verify the fix. | HIGH | 7.0b | Replace with: `V15_ENFORCEMENT=1 python -m pytest tests/guardian/test_v15_p7_bugfixes.py::test_heal_fn_no_dead_fields -x` — must exercise actual heal path. |
| IC5 | Phase 7.0c state hash uses "git HEAD + project root mtime + agent class name". `state_hash_fn` is called pre-heal and post-heal. Git HEAD does not change within a single heal call unless heal commits to git. For non-git mutations, pre/post hashes are identical, making rollback verification trivially pass (same bug as S4, just different placeholder). | MEDIUM | 7.0c | State hash must include mutable filesystem state: SHA-256 of tracked file contents in target scope, not repo-global git HEAD. Use `hashlib.sha256` of file bytes in the manifest's `node_id` target path. |
| IC6 | Tier 2 promotion rule says "Promotion to SOFT_FAIL requires Phase 7.1b exit conditions met." 7.1b is a structural gate (singleton). Promotion should require behavioral validation: 0 LOG_ONLY violations across N runs. | LOW | Tier 2 risk note | Amend: "Promotion to SOFT_FAIL requires 7.1b exit AND 0 LOG_ONLY violations across 3 consecutive CI runs." |

### R2-2 Residual Risk Identification

| ID | Risk | Severity | Location | Mitigation |
|----|------|----------|----------|------------|
| RR1 | Gateway singleton is per-agent, not per-wave. If multiple agents participate in the same healing wave, each has an independent SemanticClock and dedupe set. Cross-agent dedup and clock ordering are not enforced. | MEDIUM | 7.1b | Acceptable for Tier 1-2 (single-agent heal paths). Must be addressed in Tier 3 with wave-scoped gateway factory. Document as known limitation. |
| RR2 | `prepare_messages_for_llm()` is defined in base agent but never called by any production code (0 callers found in codebase). Plan Phase 8.2 says to wire TokenCap "via `prepare_messages_for_llm`" — this is a dead integration point. | HIGH | 8.2 | Phase 8.2 must identify actual LLM call sites (in `LLMProviderMixin` or agent-specific `_call_llm` methods) and wire TokenCap there. `prepare_messages_for_llm` is not the interception point. |
| RR3 | §7.2 `ReplayGuardStore` is listed in Phase 2.1 matrix as "Wire into gateway or base agent" but is not assigned to any Tier 1B or Tier 2 phase. Not in deferred list either. Falls through unassigned. | MEDIUM | Plan gap | Add as Phase 7.1f in Tier 1B: wire `ReplayGuardStore` into gateway. Low risk (gateway internals only). |
| RR4 | §6.3 `TokenControlArtifact` and §12.2 `SideEffectRegistry` both marked "NO contract" in Phase 2.1 matrix. No phase creates the missing contracts. Both fall through unassigned. | MEDIUM | Plan gap | Add contract creation to Tier 1A (additive, zero-risk). Wiring deferred to Tier 2. |
| RR5 | L5 layer (77 agents, largest layer) has no wiring phases in Tiers 0-2. Only L0, L2, L6 layers are addressed. L5 agents inherit from SovereignBaseAgent and have heal paths, but no category in 8.1a-e covers L5 specifically. | LOW | 8.1a-e scope | Acceptable: L5 agents inherit base class V15 wiring automatically. Explicit L5 wiring is Tier 3+ scope. Document as known gap. |

### R2-3 Enforcement Completeness Check

| § | Invariant | Runtime Enforcement Status in Plan | Gap |
|---|-----------|-----------------------------------|-----|
| §1.3 | SurgicalManifest as exclusive input | Covered by Tier 0 bug fixes + gateway | None after IC1 fix |
| §2.5 | Pipe order 1..10 | Covered by Phase 7.1c | None |
| §2.6 | Hash mismatch escalation | Covered by Phase 7.1e | None |
| §4.1 | Policy config immutability | Covered by Phase 7.1d | None |
| §5.1 | SHA-256 dedupe persistence | Covered by Phase 7.1b singleton fix | Partial: per-agent, not per-wave (RR1) |
| §6.3 | TokenCap before LLM | Plan says Phase 8.2 via `prepare_messages_for_llm` | **BROKEN** (RR2): dead integration point, must rewire |
| §7.2 | Replay guard | **MISSING** from all tiers (RR3) | Add Phase 7.1f |
| §10.2 | Boundary snapshot real hashes | Covered by Phase 7.0c | Partial: hash scope too broad (IC5) |
| §10.4 | RESULT from L2 only | Plan Phase 4.2 "Flow-Correctness Gate" | Gate defined but no phase implements it. Add to 8.1a. |
| §12.2 | SideEffectRegistry | **NO CONTRACT** exists (RR4) | Add contract to Tier 1A |
| §13.1 | SemanticClock persistence | Covered by Phase 7.1b singleton fix | None after IC3 fix |
| §15.5 | Trace ID format | Covered by Phase 7.0a | None |

### R2-4 Rollout & Rollback Stress Test

| Phase | Rollback Claim | Hidden State Concern | Verdict |
|-------|---------------|---------------------|---------|
| 7.0a-c | `git revert` single commit | No persistent state created. Changes are in-memory code path. | SAFE |
| 7.1a | Revert `guardian_contract.py` (per IC2 fix) | No persistent state. `is_v15_enforced()` reverts to binary. | SAFE |
| 7.1b | Revert `__post_init__` line + `_v15_enhanced_heal` edit | **HAZARD**: If agents were instantiated with `_v15_gateway` attribute and are long-lived (daemon mode), rollback removes the attribute but live instances retain it. New instances won't have it. | SAFE for fresh starts. **UNSAFE for hot-reload in daemon mode.** Add rollback check: verify no live agent instances hold stale gateway refs. |
| 7.1c-e | Revert gateway internals | Gateway state (PipeOrderEnforcer, PolicyConfigGuard, HashMismatchTracker) exists only in per-call scope or per-gateway scope. Revert removes the code. | SAFE |
| 8.1a-e | Revert per-category agent edits | Agent-specific manifest construction code removed. No persistent artifact storage. | SAFE |
| 8.2 | Revert TokenCap wiring | No persistent state. TokenCap artifacts are in-memory, not persisted. | SAFE |

### R2-5 Acceptance Criteria Tightening

| Phase | Current Exit Condition | Weakness | Tightened Condition |
|-------|----------------------|----------|-------------------|
| 7.0b | Import-time check (`python -c "from ... import ..."`) | Does not exercise heal path where bug manifests (IC4) | `V15_ENFORCEMENT=1 python -m pytest tests/guardian/test_v15_p7_bugfixes.py::test_heal_no_dead_fields -x` — must call `agent.heal({...})` and verify no `AttributeError` |
| 7.0c | "Pre/post hashes differ after a real mutation" | Does not specify what mutation or how to verify (IC5) | "Pre-snapshot `filesystem_hash` differs from post-snapshot after a file write to the manifest's target path. Test writes a temp file, verifies hash change, deletes file, verifies hash returns to pre-value." |
| 7.1a | `is_v15_log_mode()` returns True when `=log` | Function alone is insufficient; must verify heal path is entered (IC1) | "With `V15_ENFORCEMENT=log`, `SovereignBaseAgent.heal()` enters `_v15_enhanced_heal()` AND produces structured log. With `V15_ENFORCEMENT=0`, heal() does NOT enter `_v15_enhanced_heal()`." |
| 7.1b | SemanticClock increments, dedupe persists | Does not verify gateway is the SAME object (identity check) | Add: `assert agent._v15_gateway is agent._v15_gateway` after 2 heal calls (trivially true). More critically: `id(agent._v15_gateway)` is constant across calls AND `agent._v15_gateway._clock.step_id == 2` after 2 successful heals. |
| 8.2 | TokenCap logged before LLM call | References `prepare_messages_for_llm` which has 0 callers (RR2) | Must identify actual LLM interception point and test against THAT call site. Exit condition: "TokenCapArtifact with valid `gate_result` appears in structured log BEFORE the LLM HTTP request in the same trace_id." |
| 10.4 | `meta_guardian_check >= 0.95` | Does not define what counts as "total_invariants" or "covered_invariants" | Add: "total_invariants = count of § sections in gap analysis (22). covered_invariants = count where runtime enforcement exists (not just AST scan). 0.95 × 22 = 20.9 → at least 21 must have runtime enforcement." |

### R2-6 Hardened Delta Summary

| Delta ID | Type | Target | Change |
|----------|------|--------|--------|
| D1 | **CRITICAL FIX** | Phase 7.1a | Modify `guardian_contract.py` (not `v15_runtime_guard.py`). `is_v15_enforced()` must return `True` for `log`, `soft`, `1`. Add `is_v15_hard_fail() -> bool` that returns `True` only for `1`. All contract raise-on-violation checks call `is_v15_hard_fail()`. |
| D2 | **FIX** | Phase 7.1b | Guard gateway instantiation in `__post_init__`: `self._v15_gateway = V15ExecutionGateway() if is_v15_enforced() else None`. |
| D3 | **FIX** | Phase 7.0b | Replace import-time exit condition with heal-path integration test. |
| D4 | **FIX** | Phase 7.0c | Narrow state hash scope to manifest target path file contents, not repo-global git HEAD. |
| D5 | **ADD** | Tier 1A | Add contract stubs for `TokenControlArtifact` (§6.3) and `SideEffectRegistry` (§12.2) — additive, zero risk. |
| D6 | **ADD** | Tier 1B as 7.1f | Wire `ReplayGuardStore` into gateway execution path. |
| D7 | **FIX** | Phase 8.2 | Replace `prepare_messages_for_llm` interception (0 callers) with actual LLM call site interception in `LLMProviderMixin` or agent-specific `_call_llm`. |
| D8 | **CLARIFY** | Tier 2 risk note | Promotion to SOFT_FAIL requires 7.1b exit AND 0 LOG_ONLY violations across 3 consecutive CI runs. |
| D9 | **DOCUMENT** | Known limitations | Per-agent gateway (not per-wave) is a known limitation for Tiers 1-2. Cross-agent clock ordering and dedupe deferred to Tier 3. |
| D10 | **DOCUMENT** | Known limitations | L5 layer (77 agents) has no explicit wiring phases. Inherits base class V15 path. Explicit L5 wiring is Tier 3+ scope. |
| D11 | **HAZARD** | Phase 7.1b rollback | Daemon-mode agents with long-lived instances retain stale `_v15_gateway` after rollback. Rollback procedure must include process restart or attribute cleanup. |
| D12 | **FIX** | Phase 10.4 | Define `total_invariants` = 22 (§ sections in gap analysis). `covered_invariants` = count with runtime enforcement (not AST-only). Threshold: ≥21. |

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

