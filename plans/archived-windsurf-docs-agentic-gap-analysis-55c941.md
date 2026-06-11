---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\agentic-gap-analysis-55c941.md'
original_relative_path: 'agentic-gap-analysis-55c941.md'
source_sha256: 5acac717c25a72f23ba156970564d2b7e354ac6f01fe2cd057bd13ed58abeb8c
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agentic Process Mapping — Top 10 Gap Analysis & Implementation Plan

This plan prioritizes the 10 highest-impact gaps between the repo's current state and the full architecture spec in `docs/technical/agentic_process_mapping.md`.

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


## Gap Prioritization Summary

| # | Gap | Severity | Effort |
|---|-----|----------|--------|
| 1 | `SandboxEnvelope` missing `ToolBudget` caps | Critical | S |
| 2 | `HumanDecisionArtifact` (Path D contract) absent | Critical | M |
| 3 | `AgentExecutionProfileRegistry` not enforced at L0 | Critical | M |
| 4 | `apps_*` agents missing `{intent_delta, tool_requests[], state_diff_proposal}` output schema | High | L |
| 5 | `ExecutionTrace` audit envelope not wired to L4/L6 | High | M |
| 6 | `ToolBudget` enforcement (compute_ms / memory_mb / stdout_bytes) missing from L2 | High | M |
| 7 | Meta-learning Stage 8.6 `PatternAnalysisEngine` not integrated via `PatternAnalysisEngineAdapter` in pipeline | Medium | S |
| 8 | `EmbeddingServiceFactory` AST-scanner guard not wired into CI | Medium | S |
| 9 | Path D `DPOPair` feedback loop not connected to `RLHFOptimizer` in pipeline | Medium | M |
| 10 | Layer sovereignty write-violation enforcement (L0/L4/L6 must NOT write) has no AST-based CI gate | Medium | M |

---

## Gap Details & Implementation Steps

---

### Gap 1 — `SandboxEnvelope` missing `ToolBudget` caps
**Location:** `agentic_core/L2_execution/types/sandbox_envelope_types.py`

**Spec requirement (contract [2]):**
```
SandboxEnvelope = [InstructionPacket, ToolBudget(compute_ms, memory_mb, stdout_bytes)]
```
`SandboxEnvelope` currently carries only `envelope_id`, `tool_name`, `tool_args`, `instruction_packet_id`, `invocation_metadata`. No budget cap fields exist anywhere in the codebase.

**Implementation steps:**
1. Add `ToolBudget` dataclass to `agentic_core/L2_execution/types/sandbox_envelope_types.py` with fields `compute_ms: int`, `memory_mb: int`, `stdout_bytes: int` (all `> 0`).
2. Add `tool_budget: ToolBudget` field to `SandboxEnvelope`; include in `_signable_dict()` so budget is cryptographically bound to the envelope.
3. In `agentic_core/L2_execution/enforcement/boundary_verifier.py`, add enforcement that verifies budget is present before permitting any side-effect.
4. Update existing unit tests in `tests/agentic_core/L2_execution/types/test_sandbox_envelope.py` to supply a budget; add new assertion that `verify()` rejects a zero-budget envelope.
5. Propagate budget construction into `agentic_core/L3_orchestration/ptc/tool_invoker.py` (the PTC invocation path) and stub default caps via config.

---

### Gap 2 — `HumanDecisionArtifact` (Path D contract) absent
**Location:** `agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py` + new type file

**Spec requirement (contract [5]):**
```
HumanDecisionArtifact = [trace_id, policy_hash, reviewer_id,
  action:[APPROVE|MODIFY_DIFF|REJECT], structured_patch_schema,
  reviewer_sig]
MODIFY_DIFF MUST reference original plan_hash, use allowlist tools, re-clear L5 before execution.
```
`human_review_queue.py` exists but there is no typed `HumanDecisionArtifact` contract with `reviewer_sig` binding, `MODIFY_DIFF` must-reference enforcement, or L5 re-clear trigger.

**Implementation steps:**
1. Create `agentic_core/L5_safety/types/human_decision_artifact_types.py` with frozen `HumanDecisionArtifact` dataclass matching the spec (all 6 fields; `reviewer_sig` HMAC-SHA256 over canonical JSON).
2. Add `MODIFY_DIFF` invariant: if `action == "MODIFY_DIFF"` and `original_plan_hash` is absent → raise `HumanDecisionContractViolation`.
3. Wire `human_review_queue.py` to emit `HumanDecisionArtifact` on queue completion and return it to the L5 `safety_layer.py` for mandatory re-clear before Path D routes back to L2.
4. Add `test_human_decision_artifact_contract.py` under `tests/agentic_core/L5_safety/types/` covering: APPROVE, REJECT, MODIFY_DIFF with/without plan_hash, missing reviewer_sig.
5. Register `HumanDecisionArtifact` in `agentic_core/seams/contracts/safety_agents.py` as an exported seam contract.

---

### Gap 3 — `AgentExecutionProfileRegistry` not enforced at L0
**Location:** `agentic_core/agents/agent_registry.py` + `agentic_core/L0_routing/enforcement/`

**Spec requirement:**
```
L0: Every agent must be registered in AgentExecutionProfileRegistry.
    Profiles: LOW (deterministic only), HIGH (LLM via Gateway only).
    Unregistered agent invocation -> HARD FAIL.
    Registry hash included in determinism digest.
```
`AgentExecutionProfile` type and `agent_registry.py` exist, but there is no enforcement hook in L0 routing that hard-fails on unregistered agent invocation.

**Implementation steps:**
1. In `agentic_core/L0_routing/enforcement/execution_gateway.py`, add a `check_agent_profile_registered(agent_name: str)` call that looks up `AgentExecutionProfileRegistry`; raise `UnregisteredAgentError` on miss.
2. Add `registry_hash` to the `InstructionPacket` determinism digest computation in `agentic_core/L2_execution/types/instruction_packet_types.py`.
3. Create `tests/agentic_core/L0_routing/enforcement/test_agent_profile_enforcement.py` verifying: registered LOW agent passes, registered HIGH agent passes, unregistered agent raises `UnregisteredAgentError`, registry hash changes when registry mutates.
4. Add AST-based CI check (extend `ops_scripts/ci/`) that scans `apps_*` for any agent invocation missing a registry entry.

---

### Gap 4 — `apps_*` agents missing `{intent_delta, tool_requests[], state_diff_proposal}` schema
**Location:** `apps_lic/reasoning/`, `apps_rg/reasoning/`, `apps_shared/reasoning/`

**Spec requirement:**
```
apps_* agents => SCHEMA MUST EMIT:
  {intent_delta, tool_requests[], state_diff_proposal}
```
None of the `apps_lic` (38 agents), `apps_rg` (24 agents), or `apps_shared` (9 orchestrators) emit this standardized output schema. They return ad-hoc dicts/strings.

**Implementation steps:**
1. Define `AgentOutputContract` dataclass in `apps_shared/types/agent_output_contract.py` with fields `intent_delta: str`, `tool_requests: list[ToolRequest]`, `state_diff_proposal: dict`.
2. Add `IAgentOutputContract` Protocol to `agentic_core/interfaces/__init__.py`.
3. Add a base mixin `AgentOutputContractMixin` in `agentic_core/mixins/` that validates the return value of `execute()` against the contract.
4. Apply mixin to `apps_lic` HOP1-9 agents (38 files) and `apps_rg` core reasoning agents (24 files) — automated via a small migration script (not a runner script; a one-shot ops script).
5. Add invariant test `tests/architecture/test_apps_agent_output_contract.py` that AST-scans all `apps_*/reasoning/` files and asserts every agent class is a subclass of the mixin or implements the protocol.
6. Guard: `ops_scripts/ci/check_apps_output_contract.py` — AST-based, fails CI if any agent lacks the schema.

---

### Gap 5 — `ExecutionTrace` audit envelope not wired to L4/L6
**Location:** `agentic_core/L2_execution/audit/`, `agentic_core/L6_observability/`

**Spec requirement (contract [4]):**
```
ExecutionTrace = [trace_id, plan_hash, actor, target, diff, policy_hash,
  timestamp, prev_hash (chaining), replay_key(trace_id+plan_hash+transcript_hash)]
```
`ExecutionTrace` appears only in `apps_shared/types/execution_orchestrator_types.py` as a partial struct (no `prev_hash` chaining, no `replay_key`). There is no write path to L4 nor broadcast to L6.

**Implementation steps:**
1. Create canonical `ExecutionTrace` type in `agentic_core/L2_execution/types/execution_trace_types.py` with all 8 fields from spec including `prev_hash` and `replay_key`.
2. Implement `ExecutionTraceWriter` in `agentic_core/L2_execution/audit/execution_trace_writer.py` that: computes `replay_key = sha256(trace_id + plan_hash + transcript_hash)`, chains `prev_hash` from last committed trace, writes to L4 via `L4StateWriter`.
3. Call `ExecutionTraceWriter.commit()` at the `[FINAL DECISION / OUTCOME LOGGING]` stage in the L2 `validation_orchestrator.py`.
4. Add `ExecutionTraceReader` to `agentic_core/L6_observability/engines/` to read traces for anomaly detection.
5. Add `tests/agentic_core/L2_execution/audit/test_execution_trace_writer.py` verifying chaining invariant, `replay_key` determinism, and L4 write.

---

### Gap 6 — `ToolBudget` enforcement missing from L2 execution path
**Location:** `agentic_core/L3_orchestration/ptc/tool_invoker.py`, `agentic_core/L2_execution/engines/execute_command_executor.py`

**Spec requirement:**
```
L2 P2 PTC EXECUTION:
  [STDOUT RULE] Verified constraint: structured, max bytes
  [CEIL] TERMINATE STUCK COMPUTE CYCLES
  ToolBudget caps: compute_ms, memory_mb, stdout_bytes
```
The PTC `tool_invoker.py` invokes tools without checking any budget cap. `execute_command_executor.py` has no timeout or memory limit enforcement.

**Implementation steps:**
1. Add `budget_enforcer.py` to `agentic_core/L2_execution/enforcement/` that reads `ToolBudget` from `SandboxEnvelope` and: (a) enforces `stdout_bytes` cap via byte-counting wrapper, (b) enforces `compute_ms` timeout via threading timer, (c) raises `BudgetExceededError` on violation.
2. Integrate `budget_enforcer.py` into `tool_invoker.py` wrapping each `invoke()` call.
3. Enforce in `execute_command_executor.py`: wrap subprocess with timeout = `compute_ms / 1000` seconds; truncate stdout to `stdout_bytes`.
4. Add `tests/agentic_core/L2_execution/enforcement/test_budget_enforcer.py` with: stdout overflow, compute timeout, passing case.

---

### Gap 7 — `PatternAnalysisEngine` adapter not integrated in meta-learning pipeline
**Location:** `system_learning/pipelines/meta_learning_pipeline.py`, `system_learning/engines/pattern_analysis_engine_adapter.py`

**Spec requirement (Stage 8.6):**
```
[PATTERN] PatternAnalysisEngine.analyze(healing_snapshot, detection_signal,
  drift_snapshot) -> PatternFindingReport
```
`pattern_analysis_engine_adapter.py` (7 KB) exists but search confirms it is not called in `meta_learning_pipeline.py` at Stage 8.6. The pipeline jumps from Stage 8.5 (`HealingConfigOptimizer`) directly to Stage 8.7 (`EmbeddingService`).

**Implementation steps:**
1. Read `meta_learning_pipeline.py` Stage 8.5/8.7 boundary to identify exact insertion point.
2. Instantiate `PatternAnalysisEngineAdapter` in the pipeline's `__init__` alongside existing adapters.
3. In the pipeline's `run()` method, add Stage 8.6 call: `pattern_report = self._pattern_adapter.analyze(healing_snapshot, detection_signal, drift_snapshot)`.
4. Pass `pattern_report` to Stage 8.7's `_retrieve_semantic_context(rca_report, pattern_report)` — verifying the signature already accepts both args.
5. Add unit test `tests/system_learning/test_meta_learning_stage_8_6.py` confirming the adapter is called and its output flows into Stage 8.7.

---

### Gap 8 — `EmbeddingServiceFactory` AST-scanner guard not wired into CI
**Location:** `.github/workflows/`, `agentic_core/L0_routing/enforcement/` (AST scanner)

**Spec requirement:**
```
Sovereign LLM Gateway AST SCANNER:
  Blocks embedding instantiation outside EmbeddingServiceFactory.
CI ENFORCEMENT: Fails build on any AST or signature violation.
```
`embedding_service_factory.py` exists with singleton enforcement logic but no CI workflow enforces the "no direct embedding instantiation" invariant. Checking `.github/workflows/` shows no embedding-guard workflow.

**Implementation steps:**
1. Create `ops_scripts/ci/check_embedding_factory_boundary.py` — AST-based scan of all `.py` files; hard-fail if any file outside `system_learning/engines/embedding_service_factory.py` directly instantiates `OpenAIEmbedder`, `LocalFAISSStore`, or any class matching `*Embedder` pattern, except inside test stubs.
2. Create `.github/workflows/embedding-factory-guard.yml` triggering on push/PR to `main`; runs the checker.
3. Add `tests/architecture/test_embedding_factory_boundary.py` as an in-process version of the same AST scan.

---

### Gap 9 — Path D `DPOPair` → `RLHFOptimizer` feedback not connected in pipeline
**Location:** `system_learning/engines/rlhf_optimizer.py`, `system_learning/pipelines/meta_learning_pipeline.py`

**Spec requirement (Stage 6 DPO PATH):**
```
dpo_batch_bytes + RLHFOptimizer.propose_from_dpo() -> threshold ChangePackage
```
`L6_observability/engines/dpo_pair_generator.py` and `system_learning/engines/rlhf_optimizer.py` both exist. But the pipeline's Stage 6 proposer list does not call `RLHFOptimizer.propose_from_dpo()` with DPO batch bytes sourced from `DPOPairGenerator`. They are decoupled dead code paths.

**Implementation steps:**
1. In `meta_learning_pipeline.py` Stage 6, after existing proposers (`L0ThresholdTuner`, `RAGProposer`), add: `dpo_batch = self._dpo_pair_generator.get_pending_batch()` → `rlhf_pkg = self._rlhf_optimizer.propose_from_dpo(dpo_batch)` → append to `change_packages`.
2. Inject `DPOPairGenerator` and `RLHFOptimizer` instances into the pipeline constructor (existing constructor must be extended; both classes already exist).
3. Verify `RLHFOptimizer` adjustments are clamped to `[0.1, 2.0]` per Guarantee #23 — add assertion in `propose_from_dpo()` if not already present.
4. Add `tests/system_learning/test_meta_learning_dpo_stage6.py` with: batch present → ChangePackage produced, empty batch → no ChangePackage, clamp bounds enforced.

---

### Gap 10 — Layer sovereignty write-violation enforcement has no AST CI gate
**Location:** `.github/workflows/`, `ops_scripts/ci/`

**Spec requirement (Layer Sovereignty Matrix):**
```
L0/L4/L6 MUST NOT perform persistent writes.
L5 is sole structural enforcement authority.
Upward mutation across layers is forbidden.
```
There are mixins and runtime guards but no CI AST-based gate that statically verifies L0, L4, and L6 modules do not contain direct file/DB/vector write calls outside the permitted paths.

**Implementation steps:**
1. Create `ops_scripts/ci/check_layer_write_sovereignty.py` — AST-based scan defining:
   - `WRITE_FORBIDDEN_LAYERS = ["agentic_core/L0_routing", "agentic_core/L4_state", "agentic_core/L6_observability", "L6_observability"]`
   - Forbidden call patterns: `open(..., 'w')`, `os.write`, `faiss.write_index`, any `*Store.persist()` or `*Writer.write*()` call not delegated through `L2_execution` or `L5_safety`.
   - Allowlist: `L4StateWriter` calls that originate from L2 execution path.
2. Create `.github/workflows/layer-write-sovereignty.yml` — runs checker on push/PR.
3. Add `tests/architecture/test_layer_write_sovereignty.py` as in-process equivalent.
4. Fix any violations discovered (likely 0–3 files based on current structure).

---

## Execution Order

Recommended sequencing by dependency and risk:

1. **Gap 1** → **Gap 6** (ToolBudget type first, then enforcement)
2. **Gap 3** (registry enforcement — foundational, unlocks profiling)
3. **Gap 2** (Path D contract — needed before Gap 9 is meaningful)
4. **Gap 5** (ExecutionTrace — audit envelope, no deps)
5. **Gap 7** (pipeline Stage 8.6 — small, isolated)
6. **Gap 8** (CI guard — isolated, zero source changes)
7. **Gap 9** (DPO↔RLHF wiring — depends on Gap 2 for Path D sourcing)
8. **Gap 10** (sovereignty CI gate — runs after prior structural work)
9. **Gap 4** (apps_* schema — large surface, tackle last)

Each gap = one phase. Evidence file per phase in `docs/reports/plans/`.

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

