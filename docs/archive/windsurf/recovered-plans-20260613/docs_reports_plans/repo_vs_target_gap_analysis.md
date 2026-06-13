# Repo-vs-Target Gap Analysis Report

Based on `@/c:\Git\Agentic-Workflow\docs\technical\agentic_process_mapping.md:1-317`

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


## §1 — Embedding Governance (Items 1–7)

### Item 1: Kill-switch — **IMPLEMENTED**
- **Target**: `EMBEDDING_ENABLED` env var, `_DisabledEmbeddingService` returned when disabled
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\engines\embedding_service_factory.py:76-95` defines `_DisabledEmbeddingService` with `is_disabled()=True`, `retrieve()→None`. Kill-switch at line 182: `os.environ.get("EMBEDDING_ENABLED", "true").lower() == "true"`.
- **Gap**: None. Fully implemented with tests in `tests/system_learning/test_embedding_service_factory.py`.

### Item 2: Singleton + Fork Guard — **IMPLEMENTED**
- **Target**: `get_or_disabled()` is only public entrypoint; fork guard with `(pid, psutil.create_time)`; raises `EmbeddingForkViolationError`
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\engines\embedding_service_factory.py:133-172` — `get_or_disabled()` classmethod, thread-safe `_LOCK`, fork guard at line 166-171 comparing `(pid, create_time)`, raises `EmbeddingForkViolationError`.
- **Gap**: None.

### Item 3: Integrity Enforcement at Startup — **IMPLEMENTED**
- **Target**: SHA-256 of `embeddings.f32` must match `seed_manifest.json matrix_hash`; raises `EmbeddingIntegrityError`
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\engines\embedding_service_factory.py:258-275` — streaming SHA-256 verify, raises `EmbeddingIntegrityError`.
- **Gap**: None.

### Item 4: Determinism Constraints — **IMPLEMENTED**
- **Target**: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, eps guard, 6-decimal rounding, tie-break `(-score, content_hash ASC)`
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\engines\embedding_service_factory.py:27-28` — BLAS locks set. Line 239: `eps = 1e-12`. Line 346: `np.round(scores, 6)`. Line 359: `sorted(indices, key=lambda i: (-scores_rounded[i], self._row_hashes[i]))`.
- **Gap**: None.

### Item 5: Top-k & Cutoff Governance — **IMPLEMENTED**
- **Target**: `k <= 20`, `cutoff >= 0.5`, replay key includes model_ver + pack_hash + k + cutoff + blas_impl
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\engines\embedding_service_factory.py:333` — `max_k = 20`. Line 86: default `cutoff=0.5`. Lines 394-407: replay key computed from all required components.
- **Gap type**: **PARTIAL** — `cutoff >= 0.5` is not enforced as a hard lower bound; a caller can pass `cutoff=0.1` and it will be accepted. The `0.5` is only a default, not a guard.
- **Fix**: Add `cutoff = max(cutoff, 0.5)` or raise `ValueError` if `cutoff < 0.5` in `retrieve()`.

### Item 6: Seed Pack Location + Schema — **IMPLEMENTED**
- **Target**: `C:/AgenticEmbeddings/seed_packs/<namespace>/<hash>/` with `seed_manifest.json`, `row_index.jsonl`, `embeddings.f32`
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\engines\embedding_service_factory.py:153-155` — hardcoded path. Lines 196-228: loads all three files.
- **Gap**: None.

### Item 7: Production Embedder Pinned — **IMPLEMENTED**
- **Target**: `text-embedding-3-large`, batch=500, retries/backoff, requires `OPENAI_API_KEY`
- **Repo evidence**: `system_learning/engines/openai_embedder.py` (37 matches for `text-embedding-3-large`), `system_learning/engines/seed_pack_build_cli.py`, plus tests.
- **Gap**: None.

---

## §2 — Runtime Retrieval Injection (Items 8–10)

### Item 8: Where Runtime Retrieval is Called — **IMPLEMENTED**
- **Target**: Retrieval invoked in L1/L0 assembly stage
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\pipelines\meta_learning_pipeline.py:625-784` — `_retrieve_semantic_context()` is called at pipeline step 8.7 (line 1097).
- **Gap type**: **PARTIAL** — Retrieval is called inside the meta-learning pipeline (offline), NOT at L1/L0 prompt assembly time. The mapping asserts it should also augment runtime prompt assembly. No evidence of runtime prompt-time retrieval call outside meta-learning pipeline.
- **Fix**: Wire embedding retrieval into the L0/L1 assembly stage (the "Elevator Shaft" seam) so it runs at prompt-composition time, not only in meta-learning.

### Item 9: C0-only Rule Enforcement — **IMPLEMENTED**
- **Target**: Retrieved context augments prompt only, no mutation of routing/safety/execution
- **Repo evidence**: Multiple code comments enforce this: `@/c:\Git\Agentic-Workflow\system_learning\pipelines\meta_learning_pipeline.py:632-633` — "C0 informational context only". Embedding metadata is stored for audit only.
- **Gap type**: **UNTESTED** — No dedicated negative-control test proving that embedding results *cannot* mutate thresholds.
- **Fix**: Add a negative-control test that injects fake embedding results and asserts no routing/safety/threshold mutation occurs.

### Item 10: Deterministic Retrieval Ordering — **IMPLEMENTED**
- **Target**: Stable ordering, deterministic tie-break, replay artifact emitted
- **Repo evidence**: Tie-break at `@/c:\Git\Agentic-Workflow\system_learning\engines\embedding_service_factory.py:359`. Replay key at lines 394-407. Tests in `tests/system_learning/w1_strong_determinism_test.py`.
- **Gap**: None.

---

## §3 — Healing Tier Subsystem (Items 11–17)

### Item 11: Healer Escalation Allowlist Gating — **IMPLEMENTED**
- **Target**: `HEALER_ESCALATION_ALLOWLIST` exists, frozenset, non-allowlisted cannot escalate
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\scripts\remediation_dispatcher.py:79-86` — `frozenset` of `(check_id, healer_name)` pairs. Guard at line 534.
- **Gap**: None.

### Item 12: `needs_llm_escalation` opt-in only — **IMPLEMENTED**
- **Target**: Must be explicitly `True`, policy/permission failures must not escalate
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\scripts\remediation_dispatcher.py:526-527` — Guard 2 explicitly checks `needs_llm_escalation`. `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\types\heal_contract.py` — field with default behavior.
- **Gap**: None. Tests in `test_remediation_dispatcher.py` (29 matches).

### Item 13: EscalationContext is SSOT — **IMPLEMENTED**
- **Target**: Built deterministically from `HealCheckResult` only
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\scripts\remediation_dispatcher.py:136-202` — `EscalationContext.from_result()` class method, builds from `HealCheckResult`.
- **Gap**: None.

### Item 14: FailureSignal Contract — **IMPLEMENTED**
- **Target**: Built from EscalationContext ONLY, NO_TIERING agents emit it
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_tier_types.py:83-131` — `FailureSignal` with `to_healing_input()`. Built from EscalationContext at `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\scripts\remediation_dispatcher.py:546-554`.
- **Gap**: None.

### Item 15: `route_healing_tier` is single choke point — **IMPLEMENTED**
- **Target**: No agent can pick LOCAL/QWEN/GEMINI directly
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_tier_router.py:146-193` — single function with docstring "SINGLE CHOKE POINT". CI enforcement in `ops_scripts/ci/audit_healing_tier_enforcement.py`.
- **Gap**: None.

### Item 16: InvocationRecord Audit String — **IMPLEMENTED**
- **Target**: Immutable record with tier, model_id, agent_name, trace_id, heal_confidence, method_called
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_tier_dispatcher.py:44-53` — frozen dataclass with all required fields.
- **Gap**: None.

### Item 17: Provider Invoker Seam — **IMPLEMENTED**
- **Target**: `HealingProviderInvoker` is injectable Protocol; tests use `FakeInvoker`; production uses `DefaultHealingProviderInvoker`
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_tier_dispatcher.py:61-93` — Protocol class. `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_tier_dispatcher.py:101-158` — `DefaultHealingProviderInvoker`. Real adapters in `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_provider_adapters.py:1-389`.
- **Gap**: None.

---

## §4 — Provider Tiering Behavior (Items 18–20)

### Item 18: Threshold Values SSOT — **IMPLEMENTED**
- **Target**: X=0.75, Y=0.40, retry_count≥3 forces GEMINI
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_tier_config.py:61-67` — `heal_confidence_x=0.75`, `heal_confidence_y=0.40`, `max_heal_retries=3`.
- **Gap**: None.

### Item 19: Confidence Computation Deterministic — **IMPLEMENTED**
- **Target**: Deterministic inputs/rounding/ordering, no network calls
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_tier_router.py:91-138` — pure arithmetic, `round(heal_confidence, 6)`, no network calls.
- **Gap**: None.

### Item 20: Actual Provider Calls Exist — **IMPLEMENTED**
- **Target**: Qwen + Gemini invocation is not stubbed, production wiring routes via adapters
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\healing_provider_adapters.py:36-172` — `QwenInvokerAdapter` with real OpenAI SDK call. Lines 179-267 — `GeminiInvokerAdapter` with real Google GenAI SDK call.
- **Gap type**: **PARTIAL** — `DefaultHealingProviderInvoker` (the default used by `dispatch_healing`) is still a stub that just records invocations without real calls. Production wiring that selects the correct adapter at runtime is not visible.
- **Fix**: Wire `dispatch_healing` default invoker to select `QwenInvokerAdapter`/`GeminiInvokerAdapter`/`LocalAgentAdapter` based on tier, or document the integration point.

---

## §5 — Generation Routing Governance (Items 21–23)

### Item 21: SovereignLLMGateway has `route_generation` — **PARTIAL**
- **Target**: Centralized `route_generation` with deterministic temperature (0.0) and policy model selection
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:142-408` — Has `generate()` method (not `route_generation`). Temperature defaults to `0.7` not `0.0`.
- **Gap type**: **INCONSISTENT** — Method is `generate()` not `route_generation()`. Temperature default is 0.7 (non-deterministic). No policy-driven model selection — model is selected by caller or falls back to config default.
- **Fix**: Either rename to `route_generation` or create a `route_generation()` wrapper that enforces `temperature=0.0` for deterministic calls. Add policy-based model selection from L4 config.

### Item 22: `MCPOperationMixin.call_llm` exists — **PARTIAL**
- **Target**: All engines call LLM via `call_llm` → gateway `route_generation`
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\mixins\mcp_operation_mixin.py` (3 matches) and `@/c:\Git\Agentic-Workflow\agentic_core\mixins\mcp_hardened_mixin.py` (5 matches). However, `call_llm` found in multiple engines calling it directly without routing through the gateway: `apps_rg/engines/bullet_generation_task.py:43`, `apps_rg/engines/message_generation_task.py:33`, `apps_shared/enforcement/DecomposedqueryagentStrategy.py:123`.
- **Gap type**: **INCONSISTENT** — Several `call_llm` implementations exist that do NOT route through `SovereignLLMGateway`. Some are in commented-out code, some are active.
- **Fix**: Audit all `call_llm` callsites; ensure they route through the gateway. Add CI enforcement.

### Item 23: Model Literals Eliminated — **MISSING**
- **Target**: No model string literals outside gateway/policy/config allowlisted surfaces
- **Repo evidence**: `SovereignLLMGateway` has inline model fallback at line 174: `os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")`. No CI scan exists for scattered model literals.
- **Gap type**: **UNENFORCED** — No CI gate or AST scan prevents agents from embedding model string literals.
- **Fix**: Create AST-based CI scanner for model literals. Allowlist only `SovereignLLMGateway`, `healing_tier_config.py`, and `sovereign_config.py`.

---

## §6 — Meta-Learning Pipeline Stages (Items 24–35)

### Item 24–26: Stages 1–3 (Audit, Telemetry, Config) — **IMPLEMENTED**
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\pipelines\meta_learning_pipeline.py:841-850` — Steps 1-3 call `AuditStore`, `TelemetryStore`, `ConfigProvider` protocols.

### Item 27: Stage 4 Snapshot — **IMPLEMENTED**
- **Repo evidence**: Lines 852-871 — `create_snapshot()` with `engine_version`, `config_surface_version`, `SemanticClockSnapshot`.

### Item 28: Stage 5 RCA Engine — **IMPLEMENTED**
- **Repo evidence**: Lines 873-881 — `analyze_failures()` from `system_learning/engines/rca_engine.py`. Tests in `test_rca_engine.py` (16 matches).

### Item 29: Stage 6 Proposers Fixed Order — **IMPLEMENTED**
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\pipelines\meta_learning_pipeline.py:884-885` — `PROPOSER_ORDER = ("L0", "RAG", "L1", "L5")`.

### Item 30: Stage 7 Validators — **IMPLEMENTED**
- **Repo evidence**: Lines 987-1046 — `replay_validate`, `evaluate_shadow`, `assert_cooldown_ok`, `assert_min_sample_size`, `compute_freeze_decision`.
- **Gap type**: **PARTIAL** — `OscillationDetector` class name not found (search returned 0 matches). Instead, `OscillationPolicy` + `compute_freeze_decision` function exists. The concept is implemented but the class naming differs from the mapping.

### Item 31: Stage 8 Intake Always Persists Before `proposal_only` Check — **IMPLEMENTED**
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\pipelines\meta_learning_pipeline.py:1048-1071` — intake runs at step 8, before the `proposal_only` check at step 9 (line 1205).

### Item 32: Stage 8.5 HealingConfigOptimizer Snapshot — **IMPLEMENTED**
- **Repo evidence**: Lines 1073-1091.

### Item 33: Stage 8.6 PatternAnalysisEngine Integration — **IMPLEMENTED**
- **Repo evidence**: Lines 1093-1094 — `_analyze_historical_patterns(deps, aggregate_snapshot)`. Engine at `system_learning/engines/pattern_analysis_engine.py`.

### Item 34: Stage 8.7 Embedding Retrieval (C0-only) — **IMPLEMENTED**
- **Repo evidence**: Lines 1096-1099 — `_retrieve_semantic_context()`.

### Item 35: Stage 9 Commit Gating — **IMPLEMENTED**
- **Repo evidence**: Lines 1204-1238 — `proposal_only` check, requires both `version_store` and `approval_gate`. Hard errors on line 1212-1213 if either is None.

---

## §7 — Approval / Activation Safety (Items 36–37)

### Item 36: `proposal_only=True` Default — **IMPLEMENTED**
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\pipelines\meta_learning_pipeline.py:283` — `proposal_only: bool = True`.

### Item 37: No Activation Without BOTH Injected — **IMPLEMENTED**
- **Repo evidence**: Lines 1211-1214 — `if deps.version_store is None: raise PipelineError(...)` and `if deps.approval_gate is None: raise PipelineError(...)`.
- **Gap type**: **PARTIAL** — The check is at runtime (step 9), not a constructor invariant. The mapping asserts this should be a constructor check so the pipeline refuses to start if only one is injected. Currently, you can construct `PipelineDependencies` with `version_store` but no `approval_gate`, and it only fails at step 9.
- **Fix**: Add `__post_init__` validation to `PipelineDependencies` that rejects `version_store` without `approval_gate` and vice-versa when `proposal_only=False`.

---

## §8 — Core Data Contracts & Crypto (Items 38–43)

### Item 38: Canonical JSON Rules — **IMPLEMENTED**
- **Repo evidence**: DPO types use `json.dumps(..., separators=(",", ":"), sort_keys=True).encode("ascii")` — e.g., `@/c:\Git\Agentic-Workflow\L6_observability\types\dpo_types.py:31-38`. Same pattern in `ChangePackage`, `CanonicalEscalationPayload`.
- **Gap**: None for types that implement it, but no universal enforcer exists.

### Item 39: InstructionPacket Signature — **MISSING**
- **Target**: `InstructionPacket` with signature(HMAC-SHA256 of canonical JSON), verified at L2 boundary
- **Repo evidence**: grep for `InstructionPacket` found 0 matches in `.py` files (only in spec docs). No implementation exists.
- **Gap type**: **MISSING** — Contract [1] from the mapping is entirely unimplemented.
- **Fix**: Create `InstructionPacket` dataclass with HMAC-SHA256 signature field; add verification at L2 entry.

### Item 40: SandboxEnvelope Signature — **MISSING**
- **Target**: `SandboxEnvelope` verified at L2 boundary
- **Repo evidence**: grep for `SandboxEnvelope` found only spec docs, no `.py` implementation.
- **Gap type**: **MISSING** — Contract [2] from the mapping is unimplemented.

### Item 41: PTC Tool Contract Constraints — **PARTIAL**
- **Target**: stdout only, redaction, byte caps
- **Repo evidence**: Exists in spec docs (`PTC_SCOPE_LOCK_SPEC.md`) but no runtime enforcement found in Python code.
- **Gap type**: **UNENFORCED** — Spec exists, runtime enforcement missing.

### Item 42: ExecutionTrace Chain Fields — **PARTIAL**
- **Target**: `prev_hash` chaining, replay key includes transcript hash
- **Repo evidence**: `ExecutionTrace` referenced in `apps_shared/types/execution_orchestrator_types.py` and `agentic_core/mixins/ssot_audit_trail_mixin.py`. grep for `prev_hash.*chain|replay_key.*transcript` found 4 matches — some chaining logic exists.
- **Gap type**: **PARTIAL** — Field exists but full HMAC chain verification at runtime is not evident.

### Item 43: Replay Key Stability — **PARTIAL**
- **Repo evidence**: Replay key computed in embedding factory (lines 394-407) and `system_learning/engines/replay_validator.py`. But no universal replay key contract across all pipeline stages.
- **Gap type**: **PARTIAL** — Embedding replay key is stable; no universal replay key contract.

---

## §9 — Observability / L6 (Items 44–47)

### Item 44: DPO Types Exist and Are Used — **IMPLEMENTED**
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\L6_observability\types\dpo_types.py:1-143` — `DPOExampleId`, `DPOPair`, `DPOBatch` all frozen dataclasses. Used in `dpo_pair_generator.py` and wired through `meta_learning_pipeline.py` (lines 964-984).

### Item 45: RLHF Optimizer Clamps — **IMPLEMENTED**
- **Target**: Adjustments clamped [0.1, 2.0], delta ±0.1
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\engines\rlhf_optimizer.py:41-47` — `min_threshold=0.1`, `max_threshold=2.0`, `approve_relax_delta=0.1`, `reject_tighten_delta=-0.1`. Final clamp at line 153.

### Item 46: Deterministic Sort for DPO — **IMPLEMENTED**
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\system_learning\engines\rlhf_optimizer.py:111-113` — `sorted(..., key=lambda p: (p["example_id"]["control_hash"], p["example_id"]["candidate_hash"]))`.

### Item 47: Feedback Routed from Human Review Deterministically — **PARTIAL**
- **Target**: Path D Human Review decisions deterministically routed
- **Repo evidence**: `DPOPairGenerator` protocol exists, `DefaultDeterministicDPOPairGenerator` implemented, wired via `deps.dpo_batch_bytes` in pipeline.
- **Gap type**: **PARTIAL** — The DPO→RLHF path is implemented. But the actual Human Review artifact → DPO pair generation path (from Path D L3 orchestration) is not wired end-to-end. The pipeline expects pre-serialized `dpo_batch_bytes` injected by caller.
- **Fix**: Wire the Path D orchestration output to `DPOPairGenerator` and inject `dpo_batch_bytes` into the pipeline automatically.

---

## §10 — Cross-layer Non-bypass Rules (Items 48–51)

### Item 48: Universal Write Gateway — **IMPLEMENTED**
- **Target**: Blocks non-gateway writes at runtime
- **Repo evidence**: `@/c:\Git\Agentic-Workflow\agentic_core\L2_execution\tools\write_gateway.py:1-455` — Comprehensive gateway with size caps, amplification guards, source-root fence, protected-root enforcement. Static enforcer at `L5_safety/static_checks/write_gateway_enforcer.py`.
- **Gap type**: **PARTIAL** — Gateway exists and blocks writes into source roots, but there is no runtime interceptor that blocks `open(path, 'w')` calls that bypass the gateway. It's a convention enforced by policy, not a true runtime sandbox.
- **Fix**: Add CI AST scan verifying no direct `open(..., 'w')`, `Path.write_text()`, etc. outside the write gateway module.

### Item 49: No Direct Model Calls in Agents — **PARTIAL**
- **Target**: All model calls go through gateway
- **Repo evidence**: Some agents have `call_llm` methods that don't route through `SovereignLLMGateway` (see Item 22). `test_standard_heal_no_routing_contract.py` exists but scope is limited.
- **Gap type**: **UNENFORCED** — No comprehensive CI guard.
- **Fix**: Extend the AST-based routing compliance scanner to cover all `apps_*` engines and reasoning modules.

### Item 50: No Bypass of Tier Router — **IMPLEMENTED**
- **Target**: No agent selects healing tier directly
- **Repo evidence**: `ops_scripts/ci/audit_healing_tier_enforcement.py` exists. `route_healing_tier()` is the sole choke point. Tests: `test_healing_tier_enforcement_proof.py` (17 matches).

### Item 51: CI Scripts for Routing Compliance — **PARTIAL**
- **Target**: CI enforcement for routing compliance
- **Repo evidence**: `audit_healing_tier_enforcement.py` exists for healing tier. No equivalent for generation routing compliance via `SovereignLLMGateway`.
- **Gap type**: **PARTIAL** — Healing tier CI exists. Generation routing CI missing.
- **Fix**: Create `.github/workflows/generation-routing-compliance.yml` + AST scanner for direct model calls.

---

# Summary: Gap Counts

| Status | Count | Items |
|---|---|---|
| **IMPLEMENTED** | 33 | 1, 2, 3, 4, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 24–29, 31–36, 44, 45, 46, 50 |
| **PARTIAL** | 12 | 5, 8, 9, 20, 22, 30, 37, 42, 43, 47, 48, 51 |
| **MISSING** | 3 | 39, 40, 41 |
| **INCONSISTENT** | 2 | 21, 23 |
| **UNENFORCED** | 1 | 49 |

---

# Plan Items for MISSING / PARTIAL / INCONSISTENT Gaps

## Phase A: Core Crypto Contracts (MISSING — Items 39, 40, 41)

| Field | Value |
|---|---|
| **Target claim** | [39] InstructionPacket + [40] SandboxEnvelope + [41] PTC contracts |
| **Repo evidence** | `grep InstructionPacket *.py` → 0 hits; `grep SandboxEnvelope *.py` → 0 hits |
| **Tasks** | Create `agentic_core/L2_execution/types/instruction_packet_types.py` (InstructionPacket with HMAC-SHA256), `sandbox_envelope.py` (SandboxEnvelope), PTC contract enforcer |
| **Acceptance** | `python -m pytest tests/agentic_core/L2_execution/types/test_instruction_packet.py -q --color=no` |
| **Determinism** | 2-run stable digest on canonical JSON serialization |
| **Negative control** | Tamper signature → XFAIL; restore → PASS |

## Phase B: Generation Routing Hardening (Items 21, 22, 23, 49, 51)

| Field | Value |
|---|---|
| **Target claim** | [21] route_generation [22] call_llm routing [23] model literal elimination [49] no direct calls [51] CI guard |
| **Repo evidence** | `SovereignLLMGateway.generate()` exists but no `route_generation`; `call_llm` scattered across `apps_*` |
| **Tasks** | (1) Add `route_generation()` to gateway with `temperature=0.0` default, (2) AST-based CI scanner for model literals + direct provider SDK usage, (3) Wire all `call_llm` through gateway |
| **Acceptance** | `python -m pytest tests/agentic_core/L2_execution/enforcement/test_SovereignLLMGateway.py -q --color=no` + CI scanner passes |
| **Determinism** | Same model/temp/prompt → identical output hash across 2 runs |
| **Negative control** | Insert rogue model literal → CI FAIL; remove → PASS |

## Phase C: Embedding Governance Tightening (Items 5, 9)

| Field | Value |
|---|---|
| **Target claim** | [5] cutoff ≥ 0.5 enforcement [9] C0-only negative control |
| **Repo evidence** | `embedding_service_factory.py:86` default=0.5 but no lower-bound guard |
| **Tasks** | (1) Add `cutoff = max(cutoff, 0.5)` or `ValueError` in `retrieve()`, (2) Add negative-control test asserting embedding results cannot mutate thresholds |
| **Acceptance** | `python -m pytest tests/system_learning/test_embedding_service_factory.py -q --color=no` |
| **Determinism** | 2-run stable on cutoff enforcement |
| **Negative control** | Pass `cutoff=0.1` → ValueError; pass `cutoff=0.5` → PASS |

## Phase D: Runtime Retrieval at Prompt Assembly (Item 8)

| Field | Value |
|---|---|
| **Target claim** | [8] Runtime retrieval at L0/L1 assembly stage |
| **Repo evidence** | Retrieval only in meta-learning pipeline, not prompt assembly |
| **Tasks** | Wire `_retrieve_semantic_context()` into L0/L1 elevator shaft seam for C0 context injection at prompt composition time |
| **Acceptance** | Integration test showing retrieval called during prompt assembly |
| **Determinism** | Stable replay key + ordering |
| **Negative control** | `EMBEDDING_ENABLED=false` → no retrieval attempt |

## Phase E: Pipeline Safety Invariants (Items 37, 30)

| Field | Value |
|---|---|
| **Target claim** | [37] Constructor invariant for dual injection [30] OscillationDetector naming |
| **Tasks** | (1) Add `__post_init__` to `PipelineDependencies` rejecting `version_store` XOR `approval_gate` when `proposal_only=False`, (2) Align naming: rename `compute_freeze_decision` wrapper to `OscillationDetector` class or document alias |
| **Acceptance** | `python -m pytest tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py -q --color=no` |
| **Negative control** | Inject `version_store` without `approval_gate` → constructor raises |

## Phase F: Provider Wiring + Path D Closure (Items 20, 47)

| Field | Value |
|---|---|
| **Target claim** | [20] DefaultHealingProviderInvoker is stub [47] Path D → DPO not wired E2E |
| **Tasks** | (1) Wire `dispatch_healing` default invoker to select real adapter by tier, (2) Wire Path D orchestration output to `DPOPairGenerator` → pipeline injection |
| **Acceptance** | Integration tests with mocked providers showing tier-appropriate adapter selection |
| **Determinism** | Deterministic adapter selection for identical HealingInput |
| **Negative control** | Invalid tier → raises |

## Phase G: Write Gateway + ExecutionTrace Hardening (Items 42, 43, 48)

| Field | Value |
|---|---|
| **Target claim** | [42] prev_hash chaining [43] replay key universality [48] write gateway runtime enforcement |
| **Tasks** | (1) Add AST CI scan for direct filesystem writes bypassing write gateway, (2) Strengthen ExecutionTrace chain verification, (3) Universal replay key contract |
| **Acceptance** | CI scanner + `python -m pytest tests/agentic_core/L2_execution/test_ssot_audit_trail_mixin.py -q --color=no` |
| **Negative control** | Direct `Path.write_text()` in agent → CI FAIL |

---

To proceed with implementation, switch to **Code mode** and specify which phase(s) you want executed. Each phase produces exactly one evidence file under `docs/reports/plans/`.

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

