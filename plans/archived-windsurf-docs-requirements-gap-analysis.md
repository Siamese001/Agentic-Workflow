---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\requirements-gap-analysis.md'
original_relative_path: 'requirements-gap-analysis.md'
source_sha256: 67a2a2f4c049b64b093e5e0ad779c6c17e499b801aef69ae59ff3eb41dd283db
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-28'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# FULL REQUIREMENTS GAP ANALYSIS
## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Agentic Repository vs. Master Requirements v3.2
### Audit Date: 2026-02-27

---

## PHASE 1 — REQUIREMENTS INGESTION VALIDATION

### Parse Results

| Field | Result |
|-------|--------|
| **Parsed total rows** | 486 (REQ-001..REQ-417 = 417; Extensions = 69) |
| **Integrity block claimed** | TOTAL_ROWS=486, CORPUS_ROWS=417, EXT_ROWS=69 |
| **Row count match** | ✓ PASS |
| **Duplicate IDs** | None detected — PASS |
| **Numeric gap check REQ-001..REQ-417** | No gaps — PASS |
| **Extension prefix coverage** | REQ-PT (12), REQ-EM (4), REQ-RAGX (6), REQ-CTX (2), REQ-APP (2), REQ-TLM (1), REQ-PHJ (2), REQ-MEMX (5), REQ-WLD (4), REQ-DPO (3), REQ-COG (2), REQ-HEALX (2) — All recognized |
| **Field completeness** | All rows have: Req ID, Domain, Requirement, Enforcement, Severity, ENFORCEMENT_LAYERS, ENFORCEMENT_CLASS — PASS |

**Structural validation: PASS. Analysis proceeds.**

---

## PHASE 2 — ENFORCEMENT SURFACE MAP

### Surfaces Found

| Surface | Key Files | Status |
|---------|-----------|--------|
| **Gateway** | `L2_execution/enforcement/SovereignLLMGateway.py`, `interfaces/gateway.py`, `L2_execution/enforcement/network_egress_guard.py`, `L2_execution/enforcement/provider_binding_determinism.py`, `L2_execution/enforcement/provider_substitution_prohibition.py` | Present |
| **Embedding Factory** | `embeddings/embedding_factory.py`, `embeddings/embedding_input_guard.py`, `architecture/embedding_allowlist.py`, `L4_state/enforcement/embedding_sovereignty_guard.py` | Present |
| **UWG** | `L2_execution/UniversalWriteGateway.py`, `L2_execution/tools/write_gateway.py` | Present |
| **Determinism** | `L2_execution/determinism.py`, `L2_execution/determinism/` (6 files), `L2_execution/deterministic_providers.py` | Partial |
| **Replay** | `replay/replay_envelope.py`, `L2_execution/determinism/replay_guard.py`, `L3_orchestration/replay/`, `L4_state/enforcement/replay_bundle_store.py`, `system_learning/engines/replay_validator.py` | Partial |
| **Prompt Governance** | `prompt_governance/core/prompt_assembler.py`, `prompt_governance/core/governance_hub.py`, `prompt_governance/core/invariant_registry.py` | Partial |
| **Signature/HMAC** | `security/signature_verifier.py`, `L2_execution/enforcement/key_derivation.py`, `L2_execution/enforcement/key_source.py`, `L0_routing/types/crypto_trust_types.py` | Partial |
| **Healing** | `L2_execution/healers/healing_tier_router.py`, `L2_execution/healers/healing_tier_dispatcher.py`, `L2_execution/healers/healing_provider_adapters.py` | Partial |
| **RAG/Citation** | `L4_state/types/citation_bundle_types.py`, `L4_state/enforcement/citation_enforcement.py`, `L0_routing/types/traceability_types.py` | Partial |
| **Semantic Clock** | `L0_routing/types/determinism_types.py`, `L0_routing/enforcement/trace_id_generator.py`, `L2_execution/types/capability_token_types.py` | Partial |
| **Version/Promotion** | `L4_state/enforcement/promotion_authority.py`, `L4_state/enforcement/activation_flags.py`, `L4_state/enforcement/phase_lock_store.py` | Partial |
| **Guardian** | `L5_safety/enforcement/` (extensive), `L0_routing/enforcement/governance_contracts.py` | Partial |
| **Emergency Freeze** | `L0_routing/types/routing_artifact_types.py`, `L0_routing/types/routing_contracts_types.py` | SPARSE |
| **Memory/State** | `L4_state/memory/` (15 items), `L4_state/enforcement/` (26 items) | Partial |
| **DPO/RLHF** | `L6_observability/engines/dpo_pair_generator.py`, `system_learning/engines/rlhf_optimizer.py` | Partial |
| **Cognitive Safety** | No `PolicyViolationArtifact`, no `PolicyAlignmentCheck` found | MISSING |
| **Healing Seam Protocol** | `HealingProviderInvoker` / `InvocationRecord` found in dispatcher only, not injectable Protocol | PARTIAL |
| **Emergency Freeze Runtime** | Type exists in routing artifacts; no runtime freeze gate enforcer found | SPARSE |
| **CI Workflows** | 17 workflows covering: sovereignty, SSO, prompt governance, determinism, guardian, structure, scope, embedding | Partial |
| **WaveAuditSummary** | Not found as a concrete emitting implementation | MISSING |
| **HashChainAuditLog** | `L2_execution/audit/hash_chain_audit_log.py` | Present |
| **VersionStore** | `L4_state/memory/prompt_version_store.py`, `system_learning/engines/l4_version_store.py` | Partial |

---

## PHASE 3 + 4 — SECTION A: REQUIREMENT GAP LEDGER

Classification key:
- **PASS** — functional implementation + required enforcement layers present
- **PARTIAL** — implemented but ≥1 required enforcement layer absent
- **FAIL** — not implemented
- **DRIFT** — implemented but diverges from specification
- **STRUCTURAL_ONLY** — AST-level present; runtime guard absent where required

> Note: Due to the size of the corpus (486 requirements), identical or near-duplicate requirements (many exist across REQ-135..264 duplicating 135..164, REQ-265..332 duplicating seam/SER blocks, etc.) are classified individually per their unique ID. Where no distinguishing evidence exists, the classification of the logical peer applies.

### Layer Sovereignty (REQ-001..REQ-010)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-001 | CRITICAL | PARTIAL | Runtime import hook not demonstrated live | `L0_routing/enforcement/`, `L5_safety/enforcement/mutation_prohibition_enforcer.py` | AST scan present; no runtime hook verified as active import interceptor |
| REQ-002 | CRITICAL | PARTIAL | Runtime import hook not demonstrated live | Same as above | Same gap as REQ-001 |
| REQ-003 | CRITICAL | PARTIAL | Runtime import hook not demonstrated live | `L2_execution/UniversalWriteGateway.py` | UWG exists; runtime durable-write intercept coverage for apps_* gap |
| REQ-004 | CRITICAL | PARTIAL | Runtime boundary assertion at L1 not independently verified | `base_agents/L1CognitionBase.py` | Layer declared; no standalone L1 boundary runtime assertion enforcer found |
| REQ-005 | CRITICAL | PARTIAL | Runtime boundary assertion at L0 not independently verified | `base_agents/L0RoutingBase.py` | Same as REQ-004 |
| REQ-006 | CRITICAL | PARTIAL | Runtime boundary assertion at L5 not independently verified | `base_agents/L5SafetyBase.py` | Same pattern |
| REQ-007 | HIGH | STRUCTURAL_ONLY | Runtime guard absent | `base_agents/L2ExecutionBase.py`, `L5_safety/static_checks/` | AST/static only; no runtime guard |
| REQ-008 | HIGH | STRUCTURAL_ONLY | Runtime guard absent | `base_agents/L4StateBase.py` | Same |
| REQ-009 | CRITICAL | STRUCTURAL_ONLY | Runtime guard absent | `base_agents/L6ObservabilityBase.py` | CRITICAL + STRUCTURAL_ONLY is a severe gap |
| REQ-010 | CRITICAL | PARTIAL | Runtime CI ratchet enforcement verified; cross-layer runtime prevention unverified | `L5_safety/enforcement/`, `layer-sovereignty-enforcement.yml` | CI workflow present; runtime interceptor completeness unconfirmed |

### Gateway (REQ-011..REQ-015)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-011 | CRITICAL | PARTIAL | No complete AST scan blocking non-gateway LLM calls across all apps_* | `L2_execution/enforcement/SovereignLLMGateway.py`, `interfaces/gateway.py` | Gateway exists; AST enforcement of "all callers must route through it" unverified as zero-gap |
| REQ-012 | CRITICAL | PARTIAL | AST scan present in `system_invariant_scanner.py`; runtime scan scope unclear | `L5_safety/static_checks/system_invariant_scanner.py` | Static check exists; runtime complement missing |
| REQ-013 | CRITICAL | PARTIAL | Runtime assertion coverage incomplete | `embeddings/embedding_factory.py`, `architecture/embedding_allowlist.py` | Factory exists; runtime assertion that every embedder is factory-produced is not a verified live gate |
| REQ-014 | CRITICAL | PARTIAL | Registry check + CI ratchet; no `AgentExecutionProfile` class found in scans | `agents/agent_registry.py` | `AgentExecutionProfile` type existence not confirmed; registry check implementation unclear |
| REQ-015 | HIGH | PARTIAL | Digest implementation exists but completeness of registry hash + artifact hash + execution hash binding unverified | `L2_execution/determinism.py`, `L2_execution/determinism/digest_calculator.py` | Partial digest confirmed; triple-component binding not verified |

### META-INVARIANT (REQ-016..REQ-020)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-016 | CRITICAL | PARTIAL | "No silent fallback" contractually declared but no single meta-invariant runtime enforcer | Multiple enforcement files | Individual failure-close present per subsystem; no unified meta-gate |
| REQ-017 | HIGH | PARTIAL | Schema validation present; NaN/float rejection and byte-stability not verified as explicit guards | `utils/canonical_json_util.py` | `sort_keys=True` likely present; NaN rejection unverified |
| REQ-018 | CRITICAL | PARTIAL | HMAC-SHA256 signing present on packets; "all authenticity-critical artifacts" scope unverified | `L2_execution/enforcement/key_derivation.py`, `L0_routing/types/crypto_trust_types.py` | Packet-level signing present; artifact-level universality unverified |
| REQ-019 | CRITICAL | PARTIAL | "Before any state mutation" sequencing not verified as a universal gate | `security/signature_verifier.py` | Signature verify exists; sequencing guarantee (verify THEN mutate) not structurally enforced across all paths |
| REQ-020 | CRITICAL | PARTIAL | Append-only memory confirmed partially; memory conflict INCIDENT emission not verified | `L4_state/enforcement/violation_event_store.py`, `L4_state/memory/` | Memory conflict detection and prior-version preservation not confirmed |

### Packet / Replay / Envelope / Budget / Tools (REQ-021..REQ-031)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-021 | HIGH | PARTIAL | Schema validated; `allowed_tools[]` field presence unverified | `L2_execution/types/instruction_packet_types.py` | Most fields present; `allowed_tools` field not confirmed |
| REQ-022 | CRITICAL | PASS | — | `L2_execution/types/instruction_packet_types.py`, `L2_execution/enforcement/boundary_verifier.py` | Signature + verification present |
| REQ-023 | CRITICAL | PARTIAL | `ReplayGuardStore` concrete class not found; replay check in `replay_guard.py` only | `L2_execution/determinism/replay_guard.py` | Single-use enforcement partially present; full store unverified |
| REQ-024 | CRITICAL | PASS | — | `L2_execution/types/sandbox_envelope_types.py`, `L2_execution/enforcement/boundary_verifier.py` | Envelope + signature verification found |
| REQ-025 | CRITICAL | PARTIAL | Budget schema and runtime present; CI enforcement coverage unverified | `L2_execution/enforcement/budget_enforcer.py` | Enforcer exists; `compute_ms/memory_mb/stdout_bytes` field completeness unverified |
| REQ-026 | HIGH | PARTIAL | Schema defined; `exit_code` field presence in ToolResult unverified | `L2_execution/types/` | Tool types present; field completeness not confirmed |
| REQ-027 | HIGH | STRUCTURAL_ONLY | Runtime STDOUT-only enforcement not verified | `L2_execution/tools/` | Tool tools exist; runtime STDOUT restriction not verified as live |
| REQ-028 | CRITICAL | PARTIAL | Redaction present in gateway; byte cap enforcement unverified | `L2_execution/enforcement/SovereignLLMGateway.py` | Partial; stdout byte caps unclear |
| REQ-029 | CRITICAL | PASS | — | `L2_execution/UniversalWriteGateway.py`, `L2_execution/tools/write_gateway.py` | UWG present and used |
| REQ-030 | CRITICAL | PARTIAL | `ToolNotAllowedError` defined in UWG; CI ratchet on non-UWG writes not confirmed | `L2_execution/UniversalWriteGateway.py` | Error type present; coverage ratchet unconfirmed |
| REQ-031 | HIGH | PARTIAL | UWG exists; "15 named write primitives" count not verified | `L2_execution/UniversalWriteGateway.py` | Primitive count not confirmed |

### Artifacts (REQ-032..REQ-034)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-032 | CRITICAL | PARTIAL | TypedDict/Pydantic typing enforced selectively; AST scan coverage across all artifacts unverified | `L2_execution/types/`, `L0_routing/types/` | Rich type ecosystem present; universal enforcement unverified |
| REQ-033 | CRITICAL | PARTIAL | ExecutionTrace present; `prev_hash` field presence unverified | `L2_execution/types/execution_trace_types.py` | Most fields confirmed; hash-chain field unconfirmed |
| REQ-034 | CRITICAL | PARTIAL | `replay_key` present in L6; deterministic binding of all three components unverified | `L6_observability/engines/replay_key_computer.py` | Partial binding |

### Determinism Canon (REQ-035..REQ-037, REQ-111..REQ-116)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-035 | CRITICAL | PARTIAL | Determinism artifact emission logic exists; "exactly once per wave and per replay" enforcement not verified | `L2_execution/determinism.py` | Emission present; uniqueness gate missing |
| REQ-036 | CRITICAL | PARTIAL | Replay engine present; dual-run identical-digest test not confirmed in CI | `system_learning/engines/deterministic_replay_engine.py` | Engine present; no confirmed dual-run CI test |
| REQ-037 | CRITICAL | FAIL | Negative control test with `XFAIL(strict=True)` covering all 5 tamper vectors not found | No file found | **CRITICAL FAIL** — No evidence of negative control test covering: prompt slot order mutation, slot ownership violation, embedding misuse, CitationBundle bypass, hidden context injection |
| REQ-111 | CRITICAL | PARTIAL | `uuid4` AST scan present; `determinism_guard.py` catches uses; completeness unverified | `L2_execution/determinism/determinism_guard.py` | Guard present; CI ratchet completeness unverified |
| REQ-112 | CRITICAL | PARTIAL | `sort_keys=True` likely enforced in canonical_json; all lists sorted before hashing unverified | `utils/canonical_json_util.py` | Partial |
| REQ-113 | CRITICAL | PARTIAL | UTF-8 encoding enforced in canonical serializer; explicit enforcement of canonical byte representation in hash inputs unverified | `utils/canonical_serializer_util.py` | Partial |
| REQ-114 | CRITICAL | PARTIAL | `wall.clock`/`datetime.now` appear in 260+ files — **significant drift** | Widespread | `uuid4` and wall-clock in determinism paths: 737 matches across 260 files is a CRITICAL drift signal |
| REQ-115 | CRITICAL | PARTIAL | Semantic Clock tick logic present in types; "StateCommit-only" advancement not verified as exclusive | `L0_routing/types/determinism_types.py` | Partial |
| REQ-116 | CRITICAL | PARTIAL | No unified "determinism violation fails CI" gate confirmed | `spine-determinism-guard.yml` | CI workflow exists; gate completeness unverified |

### Healing (REQ-038..REQ-044)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-038 | CRITICAL | PASS | — | `L2_execution/healers/healing_tier_router.py` | `route_healing_tier` function present |
| REQ-039 | CRITICAL | PARTIAL | `needs_llm_escalation` present in types; explicit opt-in enforcement in CI unverified | `L2_execution/healers/healing_tier_types.py` | Partial |
| REQ-040 | HIGH | PARTIAL | Monotonic enforcer present; GEMINI tier at retry>=3 not confirmed | `L2_execution/healers/monotonic_reentrancy_enforcer.py` | Partial |
| REQ-041 | MEDIUM | PARTIAL | `HealCheckResult` type present; `CONTRACT_VERSION=2` field unverified | `L2_execution/healers/healing_tier_types.py` | Partial |
| REQ-042 | HIGH | PARTIAL | `changes_made` field likely present; deterministic sorting not verified | Healing types | Partial |
| REQ-043 | CRITICAL | PARTIAL | Escalation context derivation chain present; CI ratchet unverified | `L2_execution/healers/escalation_context.py` | Partial |
| REQ-044 | HIGH | PARTIAL | `NO_TIERING` agent behavior not confirmed as FailureSignal emitter | `L2_execution/healers/tiering_allowlist.py` | Partial |

### Embeddings (REQ-045..REQ-048)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-045 | CRITICAL | PARTIAL | Embedding-as-authority guard present in `embedding_input_guard.py` and `embedding_sovereignty_guard.py`; fail-closed runtime gate not confirmed for all routing/safety paths | `embeddings/embedding_input_guard.py`, `L4_state/enforcement/embedding_sovereignty_guard.py` | Guards exist; coverage not complete |
| REQ-046 | CRITICAL | PARTIAL | SHA-256 startup verification logic not confirmed in factory | `embeddings/embedding_factory.py` | Factory present; startup hash check unverified |
| REQ-047 | CRITICAL | PARTIAL | `SeedEmbeddingPackManifest` schema fields unverified | `system_learning/engines/seed_embedding_pack_builder.py` | Partial |
| REQ-048 | CRITICAL | PARTIAL | `EmbeddingResult` fields partially confirmed; `input_hash`, `semantic_clock_tick` binding into digest unverified; deterministic embedding under replay unverified | `embeddings/embedding_factory.py` | Significant gap — replay determinism of embeddings is unverified |

### Meta-Learning Stages (REQ-049..REQ-079)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-049 | CRITICAL | PARTIAL | `ChangePackage` with `proposal_only=True` default present in interfaces; kill-switch fail-closed not confirmed | `interfaces/meta_learning.py` | Partial |
| REQ-050 | CRITICAL | PARTIAL | `VersionStore.activate()` / `VersionPointer` present; explicit dual injection requirement unverified | `system_learning/engines/l4_version_store.py` | Partial |
| REQ-051 | CRITICAL | PARTIAL | HMAC signing of ChangePackage referenced; `package_hash` as HMAC-SHA256 unverified | `interfaces/meta_learning.py` | Partial |
| REQ-052 | HIGH | PARTIAL | Layer-scope validator not confirmed as standalone component | `interfaces/meta_learning.py` | Partial |
| REQ-053 | HIGH | PARTIAL | ChangePackage schema fields partially present; `delta_payload` and `layer_target` not confirmed | `interfaces/meta_learning.py` | Partial |
| REQ-054 | CRITICAL | PARTIAL | Kind allowlist present in interfaces; per-kind schema validation not confirmed | `interfaces/meta_learning.py` | Partial |
| REQ-055 | CRITICAL | STRUCTURAL_ONLY | HMAC key management outside repo — static scan only; no runtime enclave verification | `L2_execution/enforcement/key_source.py` | STRUCTURAL_ONLY for CRITICAL requirement |
| REQ-056 | CRITICAL | PARTIAL | `proposal_only` gate present; Stage 9 blocking when `proposal_only=True` unverified | `interfaces/meta_learning.py` | Partial |
| REQ-057 | CRITICAL | PARTIAL | Dual injection requirement referenced; hard-fail on single injection not confirmed | `interfaces/meta_learning.py` | Partial |
| REQ-058 | CRITICAL | PARTIAL | Stage order (AUDIT→TELEMETRY→...→COMMIT) referenced; no stage controller pipeline file confirmed | `L0_routing/meta_control/meta_learning_bus.py` | Stage bus present; ordered pipeline controller unverified |
| REQ-059 | HIGH | PARTIAL | Unknown stage rejection logic unverified | `L0_routing/meta_control/` | Partial |
| REQ-060 | CRITICAL | PARTIAL | Stage determinism (no wall-clock/random) unverified; wall-clock widely present | `L0_routing/meta_control/meta_apply.py` | DRIFT risk — wall-clock found in 260+ files |
| REQ-061 | HIGH | PARTIAL | Typed artifacts (CandidateConfig, Snapshot, RCAReport) not all confirmed | `system_learning/engines/rca_engine.py` | RCA present; CandidateConfig/Snapshot unconfirmed |
| REQ-062 | CRITICAL | PARTIAL | Stage 6 ChangePackage sole emitter not confirmed as invariant | `interfaces/meta_learning.py` | Partial |
| REQ-063 | CRITICAL | PARTIAL | Proposer fixed order L0→RAG→L1→L5 not confirmed | `L0_routing/meta_control/meta_apply.py` | Partial |
| REQ-064 | HIGH | PARTIAL | Single consolidated ChangePackage per trace_id not confirmed | `interfaces/meta_learning.py` | Partial |
| REQ-065 | CRITICAL | PARTIAL | `ReplayValidator`, `ShadowEvaluator`, `DampeningValidators`, `OscillationDetector` composition unverified in Stage 7 | `system_learning/engines/replay_validator.py` | Replay validator exists; composition of all 4 unverified |
| REQ-066 | CRITICAL | PARTIAL | `ReplayValidator` reject logic present; CI ratchet unverified | `system_learning/engines/replay_validator.py` | Partial |
| REQ-067 | CRITICAL | PARTIAL | `ShadowEvaluator` with typed `shadow_score` not confirmed; "MUST NOT commit" guard unverified | `system_learning/engines/shadow_drift_analyzer.py` | Related file found; exact spec match unverified |
| REQ-068 | CRITICAL | PARTIAL | `CooldownValidator` and `MinSampleValidator` not confirmed as named components | `system_learning/engines/` | Not found by name |
| REQ-069 | CRITICAL | PARTIAL | `OscillationDetector` not confirmed | `system_learning/engines/` | Not found by name |
| REQ-070 | HIGH | PARTIAL | Typed `ValidationReport` from Stage 7 not confirmed | `system_learning/engines/` | Partial |
| REQ-071 | CRITICAL | PARTIAL | Stage 8 INTAKE persistence to L4 confirmed partially; HMAC-signing and UWG routing unverified | `system_learning/engines/l4_state_writer.py` | L4 writer exists; signing + UWG routing unverified |
| REQ-072 | CRITICAL | PARTIAL | Stage 9 as sole VersionStore writer not confirmed as invariant | `system_learning/engines/l4_version_store.py` | Partial |
| REQ-073 | CRITICAL | PARTIAL | `ApprovalGate.decide()` before VersionStore.commit() sequencing not confirmed | `L4_state/enforcement/promotion_authority.py` | Partial |
| REQ-074 | HIGH | PARTIAL | Typed `VersionPointer` present; two sub-stages of Stage 9 not confirmed | `system_learning/engines/l4_version_store.py` | Partial |
| REQ-075 | CRITICAL | PARTIAL | L0 promotion governance present; "MUST NOT bypass L5/HIL/L2" boundary completeness unverified | `L0_routing/scripts/run_guardian_change_package_activation.py` | Partial |
| REQ-076 | CRITICAL | PARTIAL | Kind-scope validator + AbortArtifact on violation not confirmed | `interfaces/meta_learning.py` | Partial |
| REQ-077 | CRITICAL | PARTIAL | Embedding artifacts in ChangePackage as C0 audit metadata only — enforcement not confirmed | `architecture/embedding_allowlist.py` | Allowlist present; runtime enforcement in ChangePackage context unverified |
| REQ-078 | CRITICAL | PARTIAL | L5 certification gate for routing/safety/tool proposals not confirmed as enforced in Stage 6 | `L5_safety/enforcement/` | Partial |
| REQ-079 | CRITICAL | PARTIAL | Immutable CommitAudit emission from Stage 9 not confirmed | `system_learning/engines/l4_version_store.py` | Partial |

### Guardian (REQ-080..REQ-084)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-080 | CRITICAL | PARTIAL | Guardrail Guard + Artifact Guard both referenced; Artifact Guard signature verification completeness unverified | `L5_safety/enforcement/` | Multiple guards present |
| REQ-081 | CRITICAL | PARTIAL | Both traversal enforced — no bypass skip; no positive test confirming both always traversed | `L5_safety/enforcement/` | Partial |
| REQ-082 | CRITICAL | PARTIAL | HARD STOP implemented; "block rejected plans and halt execution" full coverage unverified | `L5_safety/enforcement/` | Partial |
| REQ-083 | CRITICAL | PARTIAL | VALIDATE→ENFORCE→REMEDIATE→CERTIFY order not confirmed as ordered pipeline | `L5_safety/enforcement/` | Partial |
| REQ-084 | CRITICAL | PARTIAL | Artifact Guard replay consistency + signature chain verification present; completeness unverified | `L5_safety/enforcement/` | Partial |

### HIL (REQ-085..REQ-087)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-085 | CRITICAL | PARTIAL | `HumanDecisionArtifact` with `reviewer_id` + `reviewer_sig` found; full schema enforcement unverified | `L5_safety/types/human_decision_artifact_types.py`, `L3_orchestration/types/human_decision_artifact_types.py` | Partial |
| REQ-086 | CRITICAL | PARTIAL | MODIFY_DIFF fields `original_plan_hash` + `structured_patch_schema` + L5 re-clear not confirmed as schema | `L5_safety/types/` | Partial |
| REQ-087 | CRITICAL | PARTIAL | Signature invalidation on MODIFY_DIFF present in `signature_invalidator.py`; full test unverified | `L2_execution/healers/signature_invalidator.py` | Partial |

### Incident / Vigilance (REQ-088..REQ-091)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-088 | HIGH | PARTIAL | `CognitiveDiffBundle` type defined; snapshot+trace+diff binding unverified | `L3_orchestration/types/cognitive_diff_types.py` | Partial |
| REQ-089 | CRITICAL | PARTIAL | `ForensicTraceBuffer` append-only + post-seal mutation error not confirmed | `L0_routing/types/traceability_types.py` | ForensicTraceBuffer referenced; append-only seal enforcement unverified |
| REQ-090 | HIGH | PARTIAL | Tier I/II logging present; no positive test for scope increase behavior | `L6_observability/engines/TieredVigilanceEmitter.py` | Partial |
| REQ-091 | CRITICAL | PARTIAL | Tier III freeze: WriteGateway disable + token halt + promotion freeze + routing freeze + meta-learning freeze — all-or-nothing not confirmed | `L0_routing/types/routing_artifact_types.py`, `L2_execution/UniversalWriteGateway.py` | Freeze type present; all-five-component orchestration unverified |

### Prompt Governance (REQ-092..REQ-096)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-092 | CRITICAL | PARTIAL | AST scan present (`sovereign_precommit_no_raw_prompts_util.py`); runtime chokepoint not confirmed as active gate | `prompt_governance/core/`, `L0_routing/scripts/sovereign_precommit_no_raw_prompts_util.py` | Partial |
| REQ-093 | CRITICAL | PARTIAL | `prompt_governance` module present with assembler/hub; REQ-PT-001..012 enforcement not confirmed as integrated; fail-closed bypass abort unverified | `prompt_governance/core/prompt_assembler.py`, `prompt_governance/core/governance_hub.py` | Significant gap — PT enforcement integration unverified |
| REQ-094 | CRITICAL | PARTIAL | `TokenControl` with `prompt_hash` and `RouteDecision` with `prompt_hash` not confirmed as schema fields | `L2_execution/types/token_enforcement_types.py` | Partial |
| REQ-095 | CRITICAL | PARTIAL | Deterministic prompt composition likely present in assembler; no-UUID/no-wall-clock enforcement unverified; stable slot ordering unverified | `prompt_governance/core/prompt_assembler.py` | Partial — wall-clock drift risk high |
| REQ-096 | HIGH | PARTIAL | Domain fragment lineage logging unverified | `prompt_governance/core/governance_hub.py` | Partial |

### Auth / Kill-Switch (REQ-097..REQ-104)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-097 | CRITICAL | PARTIAL | Capability tokens with scope present; `scope metadata` + `target resources` restriction unverified | `L2_execution/types/capability_token_types.py`, `L2_execution/enforcement/capability_chokepoint.py` | Partial |
| REQ-098 | CRITICAL | PARTIAL | Token expiration with semantic_clock binding present; CI ratchet unverified | `L2_execution/types/capability_token_types.py` | Partial |
| REQ-099 | CRITICAL | PARTIAL | L2 capability chokepoint present; "single chokepoint" exclusivity unverified | `L2_execution/enforcement/capability_chokepoint.py` | Partial |
| REQ-100 | CRITICAL | PARTIAL | ALLOW/DENY artifact emission not confirmed as typed artifact for every invocation | `L2_execution/enforcement/capability_chokepoint.py` | Partial |
| REQ-101 | HIGH | PARTIAL | Conversational input boundary present; no specific test confirming authority non-confer | `L2_execution/enforcement/boundary_verifier.py` | Partial |
| REQ-102 | CRITICAL | PARTIAL | `EMBEDDING_ENABLED` kill-switch present in factory; SovereigntyViolation halt confirmed partially | `embeddings/embedding_factory.py` | Partial |
| REQ-103 | CRITICAL | PARTIAL | `ApprovalGate` present; UWG fail-closed confirmed; complete interception gate unverified | `L4_state/enforcement/promotion_authority.py` | Partial |
| REQ-104 | CRITICAL | PARTIAL | `needs_llm_escalation=False` blocking present; `TIERING_ALLOWLIST` enforcement present | `L2_execution/healers/tiering_allowlist.py` | Partial — CI ratchet unverified |

### Replay (REQ-105..REQ-110)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-105 | CRITICAL | PARTIAL | Replay input schema: `CitationBundle hash`, `RAG config_hash`, `embedding metadata` binding not confirmed | `replay/replay_envelope.py` | Partial — several required fields missing from envelope |
| REQ-106 | CRITICAL | PARTIAL | Read-only sandbox with network IO + SDK blocking not confirmed for replay harness | `replay/replay_envelope.py` | Partial |
| REQ-107 | CRITICAL | PARTIAL | Full side-effect reconstruction in replay not confirmed | `system_learning/engines/deterministic_replay_engine.py` | Partial |
| REQ-108 | CRITICAL | PARTIAL | Deterministic stubs + regression detection + mutation token forbid not all confirmed | `L2_execution/determinism/replay_guard.py` | Partial |
| REQ-109 | CRITICAL | PARTIAL | Replay gate before promotion to ACTIVE not confirmed as hard gate | `L4_state/enforcement/promotion_authority.py` | Partial |
| REQ-110 | HIGH | PARTIAL | `ReplayRunArtifact` emission + hash-bound artifacts not confirmed | `system_learning/engines/` | Partial |

### Sovereignty (REQ-117..REQ-134)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-117 | CRITICAL | PARTIAL | Layer import direction checked in CI; runtime guard absent | `layer-sovereignty-enforcement.yml` | STRUCTURAL_ONLY partially |
| REQ-118 | CRITICAL | PARTIAL | Reflection bypass AST scan present; runtime guard not confirmed | `L5_safety/enforcement/mutation_prohibition_enforcer.py` | Partial |
| REQ-119 | CRITICAL | PARTIAL | `eval`/`exec` AST scan present; completeness unverified | `L5_safety/static_checks/` | Partial |
| REQ-120 | CRITICAL | PARTIAL | Subprocess AST scan + allowlist present; L2 allowlist completeness unverified | `L5_safety/enforcement/safe_subprocess_handler_enforcer.py` | Partial |
| REQ-121 | CRITICAL | PARTIAL | `ToolTranscript` hash-binding to ExecutionTrace not confirmed | `L2_execution/types/execution_trace_types.py` | Partial |
| REQ-122 | CRITICAL | PARTIAL | L2 boundary reject unsigned/expired/unscoped tokens present; completeness of all 3 checks unverified | `L2_execution/enforcement/boundary_verifier.py` | Partial |
| REQ-123 | CRITICAL | PARTIAL | Gateway model-unknown reject + audit + kill-switch block present; completeness unverified | `L2_execution/enforcement/SovereignLLMGateway.py` | Partial |
| REQ-124 | CRITICAL | PARTIAL | `EMBEDDING_ENABLED` check + no-fallback enforcement present; completeness unverified | `embeddings/embedding_factory.py` | Partial |
| REQ-125 | CRITICAL | PARTIAL | Vector index writes through UWG; external weight pull L5 cert requirement unverified | `L2_execution/UniversalWriteGateway.py` | Partial |
| REQ-126 | CRITICAL | PARTIAL | No direct env mutation AST scan; config mutation without ChangePackage prevention unverified | `L5_safety/enforcement/mutation_prohibition_enforcer.py` | Partial |
| REQ-127 | CRITICAL | PARTIAL | VersionStore injection logging present; `PolicyUpdateProposal` emission on all `policy_hash` changes unverified | `system_learning/engines/l4_version_store.py` | Partial |
| REQ-128 | CRITICAL | PARTIAL | `PolicyUpdateProposal` with prev hash + HMAC sign not confirmed as schema | `L0_routing/enforcement/governance_contracts.py` | Partial |
| REQ-129 | CRITICAL | PARTIAL | No mutable global state AST scan present; all exceptions subclassing `SovereigntyError` not confirmed | `L5_safety/enforcement/mutation_prohibition_enforcer.py` | Partial |
| REQ-130 | HIGH | PARTIAL | `AbortArtifact` with `reason_code`, `trace_id`, `timestamp_utc` not confirmed as universal emission | `L2_execution/UniversalWriteGateway.py` | Partial |
| REQ-131 | CRITICAL | PARTIAL | CI fails on CRITICAL violations — CI workflows present; unified per-Req-ID failure list output unverified | 17 CI workflow files | Partial — no single gate that outputs by Req ID |
| REQ-132 | CRITICAL | PARTIAL | Discovery mismatch abort present; signature failure abort and replay mismatch abort — all 3 confirmed? Unverified | `ssot_verify.yml`, `guardian-tests.yml` | Partial |
| REQ-133 | CRITICAL | PARTIAL | No TODO/bypass flags — static scan referenced; confirmed as CI-enforced scan unverified | `L5_safety/static_checks/` | Partial |
| REQ-134 | CRITICAL | PARTIAL | "Zero CRITICAL violations" calculation mechanism unverified as live CI gate | `L5_safety/enforcement/compliance_audit_manager_enforcer.py` | Partial |

### Governance (REQ-135..REQ-139, REQ-255..REQ-264)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-135 | CRITICAL | PARTIAL | Typed exception hierarchy present; sovereignty violations halt not confirmed universally | `L5_safety/enforcement/` | Partial |
| REQ-136 | CRITICAL | PARTIAL | Versioned schema for cross-layer calls + mismatch abort not confirmed | `L5_safety/enforcement/` | Partial |
| REQ-137 | HIGH | PARTIAL | Structured audit logging present; trace_id inclusion not universally confirmed | Multiple | Partial |
| REQ-138 | CRITICAL | PARTIAL | Replay mutation prevention + deterministic clock enforcement unverified together | `L2_execution/determinism/replay_guard.py` | Partial |
| REQ-139 | HIGH | PARTIAL | Integer timestamps policy + embedding+commit hash in digest not confirmed together | `L2_execution/determinism.py` | Partial |
| REQ-255..264 | CRITICAL/HIGH | PARTIAL | These are semantic duplicates of REQ-135..139 with expansions — same classification applies | Same files | Partial |

### Seam (REQ-140..REQ-143, REQ-265..REQ-274)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-140 | CRITICAL | PARTIAL | L0 `importlib` allowlisted seams present; coverage of all upward imports unverified | `L0_routing/seams/`, `L0_routing/seam/safety_enforcement_seam.py` | Partial |
| REQ-141 | HIGH | PARTIAL | Three named seams present; "upward only" exclusivity unverified | `seams/contracts/safety_agents.py` | Partial |
| REQ-142 | CRITICAL | PARTIAL | Seam audit artifact + TraceID binding + no state mutation + deterministic not all confirmed | `L0_routing/seams/` | Partial |
| REQ-143 | CRITICAL | PARTIAL | Seam failure abort + versioned allowlist + CI failure on expansion unverified together | `L0_routing/seams/` | Partial |
| REQ-265..274 | CRITICAL/HIGH | PARTIAL | Expansions of REQ-140..143; additional fields (source_module, target_module, invocation_hash; mutable refs forbidden; per-wave count tracking) not confirmed | Same files | Partial — expansion requirements largely unimplemented |

### CI / CI Ratchet (REQ-144..REQ-153, REQ-275..REQ-294)

| Req ID | Severity | Status | Missing Layers | File Paths | Notes |
|--------|----------|--------|---------------|------------|-------|
| REQ-144 | CRITICAL | PARTIAL | AST governance tests exist; "zero-violation ceiling + upward coverage" enforcement unverified | `.github/workflows/` (17 workflows) | Partial |
| REQ-145 | CRITICAL | PARTIAL | Discovery mismatch abort + abort-on-critical present partially | `ssot_verify.yml` | Partial |
| REQ-146 | CRITICAL | PARTIAL | CommitProofInvariant + AST block outside factory — both unverified as CI jobs | `.github/workflows/` | Partial |
| REQ-147..REQ-153 | CRITICAL | PARTIAL | Individual CI ratchets: mutation/determinism/wall-clock/schema/TraceID/token/clock/HMAC — all CI workflows present but individual ratchet completeness unverified | `.github/workflows/` | Partial |
| REQ-275..294 | CRITICAL/HIGH | PARTIAL | Expansion of REQ-144..153; additions (determinism of CI pipeline itself; per-Req-ID failure output; structured pass/fail artifacts; auto-add forbidden patterns) not confirmed | `.github/workflows/` | Partial — several expanded requirements are FAIL |

### Boundary / Discovery / Trace / Evidence / Override / Surgical / SSOT / SER / Promotion / Emergency Freeze / Artifact Legality / Sovereignty Matrix / Phase Lock / TraceID / Canonical Hashing / HMAC Custody / Signature Enclave / Semantic Clock (REQ-154..REQ-417)

Rather than repeat each row (these form the majority of the 417 corpus), they are classified by domain cluster with supporting evidence:

| Domain | Req IDs | Status | Notes |
|--------|---------|--------|-------|
| **Boundary** | REQ-154, REQ-295 | PARTIAL | Boundary halt on missing header/token/sig present; health=unhealthy default unverified |
| **Discovery** | REQ-155..156, REQ-296..301 | PARTIAL | Discovery JSON schema present; `integrity_hash`, `git_hash`, `blueprint_hash` per agent confirmed partially; ZOMBIE detection CI present |
| **Trace** | REQ-157..158, REQ-302..305 | PARTIAL | ExecutionTrace schema confirmed; HashChainAuditLog present; tamper-detect test unverified |
| **Evidence** | REQ-159, REQ-306..309 | PARTIAL | EvidencePack type references present; hash-bound + replay-verifiable not confirmed |
| **Override** | REQ-160, REQ-310 | PARTIAL | `PolicyUpdateProposal` referenced; delta rationale field unverified |
| **Surgical** | REQ-161..162, REQ-311..314 | PARTIAL | `SurgicalHealingAdapter.py` present in L5; `SurgicalManifest` with `node_id vs blueprint` validation and `manifest_hash SHA-256` unverified; line-number forbid unverified |
| **SSOT** | REQ-163(N/A), REQ-231..233, REQ-315..322 | PARTIAL | SSOT guardrail comprehensive; SignedModify, append-only change_history, SSOT version in all artifacts — partial |
| **Capability Tokens** | REQ-163..165 | PARTIAL | Token schema confirmed; lifecycle state machine (ISSUED→ACTIVE→CONSUMED→EXPIRED→REVOKED) as enforced enum not confirmed |
| **Side-Effect Registry** | REQ-166..168, REQ-323..332 | PARTIAL | L2 effect class declarations present in tool_policy_enforcer; taxonomy-locked registry + guardian comparison + registry immutability during wave not all confirmed |
| **Promotion State** | REQ-169..172, REQ-333..342 | PARTIAL | `promotion_authority.py`, `phase_lock_store.py` present; Candidate→Shadow→Active state machine with explicit gate checks unverified |
| **Emergency Freeze** | REQ-173..174, REQ-343..351 | PARTIAL | Freeze type in routing artifacts; runtime freeze gate enforcer not found; all-or-nothing freeze not confirmed |
| **Artifact Legality** | REQ-175..177, REQ-352..360 | PARTIAL | Artifact type ecosystem present; flow direction enforcement (L2→L4→L6) not confirmed as runtime gate |
| **Sovereignty Matrix** | REQ-178..179, REQ-361..370 | PARTIAL | AST-based matrix scan present; runtime enforcement of matrix at execution time unverified |
| **Phase Lock** | REQ-180..181, REQ-371..375 | PARTIAL | `phase_lock_store.py` present; Wave 7/W6/Guardian+Replay phase gates not confirmed as hard gates |
| **TraceID Canon** | REQ-182, REQ-376..379 | PARTIAL | TraceID regex pattern present in `trace_id_generator.py`; collision abort + uniqueness per wave not confirmed |
| **Canonical Hashing** | REQ-183..185, REQ-380..389 | PARTIAL | Canonicalization present; SHA-256 universal, no truncated hashes, hash metadata schema fields — partial |
| **HMAC Custody** | REQ-186..187, REQ-390..397 | PARTIAL | HMAC key management present; key NOT in repo (static scan); rotation, scope-limit, expired-key rejection — partially confirmed |
| **Signature Enclave** | REQ-188..190, REQ-398..407 | PARTIAL | `security/signature_verifier.py` present; isolated enclave process, key store append-only, batch signing determinism — partially confirmed |
| **Semantic Clock** | REQ-191..193, REQ-408..412 | PARTIAL | Semantic clock types extensive; vector clock monotonicity, conflict abort, divergence INCIDENT, reset forbidden — partially confirmed |
| **Knowledge Supervisor** | REQ-194..197 | PARTIAL | `knowledge_integrity_guard.py`, `local_embedding_population_service.py` present; low-confidence supervision trigger, L5 approval for retraining, threshold SSOT-bound — partially confirmed |
| **RAG Custody** | REQ-198..201 | PARTIAL | CitationBundle type + citation_enforcement.py present; ExternalKnowledgeAccessViolation runtime abort, namespace in RetrievalQuery, deterministic stable sort — partially confirmed |
| **Guardian Meta** | REQ-202..205 | PARTIAL | Guardian tests CI workflow present; ≥95% invariant coverage, deterministic suite not confirmed |
| **L0 Seam** | REQ-206 | PARTIAL | importlib seam present; CI failure on unauthorized expansion unverified |
| **Incident Telemetry** | REQ-207..209 | PARTIAL | `TieredVigilanceEmitter.py` + `telemetry_recorder.py` present; atomic flush, buffer abort on Tier II/III missing buffer — unverified |
| **Cognitive Diff** | REQ-210..212 | PARTIAL | `cognitive_diff_types.py` present; deterministic comparison, signed, immutable, stored in L4 — partially confirmed |
| **Boundary Snapshot** | REQ-213..215 | PARTIAL | Snapshot references present; `filesystem_hash + git_state_hash + agent_memory_hash + semantic_clock` schema unverified |
| **Budget Routing** | REQ-216..218 | PARTIAL | Budget enforcer present; `RouteRecovery` on overflow, BudgetGuard before LLM call, SSOT-bound limits — partially confirmed |
| **Law Slot Handler** | REQ-219..222 | PARTIAL | No `LawSlotHandler` class found explicitly; these appear as functional gaps |
| **MRO Integrity** | REQ-223..226 | PARTIAL | `verify_mro_util.py` (35 matches) present; mro_signature as authoritative, L5 gate for changes, signature hash-bound — partially confirmed |
| **Structure Blueprint** | REQ-227..230 | PARTIAL | `structure_blueprint/_verify.py` + `ssot_guardrail.py` + `ssot_structure_validation.py` present; SHA-256 pre-audit match, binding failure abort — partially confirmed |
| **SSOT Enforcement** | REQ-231..233 | PARTIAL | Comprehensive SSOT tools; SignedModify binding + INCIDENT on mismatch — partially confirmed |
| **Structural Lock** | REQ-234..238 | PARTIAL | Blueprint enforcement present; dynamic class injection forbid AST scan present; runtime guard unverified |
| **Quorum Governance** | REQ-239..240 | PARTIAL | N-of-M signature threshold; no concrete quorum aggregation component found |
| **Rollback Integrity** | REQ-241..242 | PARTIAL | Rollback references in VersionStore; atomic pointer restore + RollbackArtifact unverified |
| **Audit Completeness** | REQ-243..244 | FAIL | `WaveAuditSummary` not found as an implemented emitting component |
| **Human Override** | REQ-245..246 | PARTIAL | TTL + reviewer_sig schema present; auto-revoke on expiry not confirmed |
| **Policy Exception** | REQ-247..248 | PARTIAL | Policy exception handling referenced; no-wildcard scope, single-tick TTL not confirmed |
| **Artifact Registry** | REQ-249..250 | PARTIAL | ArtifactID usage present; unique namespace enforcement + corruption-abort not confirmed |
| **Drift Escalation** | REQ-251..252 | PARTIAL | `shadow_drift_analyzer.py` present; `DriftEscalationArtifact` type not confirmed |
| **Cross-Wave Integrity** | REQ-253..254 | PARTIAL | `prev_wave_hash` linkage type not confirmed as implemented |
| **Provider Binding Determinism** | REQ-413 | PARTIAL | `provider_binding_determinism.py` present; digest including `gateway_version + semantic_clock_vector` unverified |
| **Network Egress Guard** | REQ-414 | PARTIAL | `network_egress_guard.py` present; localhost endpoint coverage unverified |
| **Provider Substitution Prohibition** | REQ-415 | PARTIAL | `provider_substitution_prohibition.py` present; CI negative control test unverified |
| **Critical Dual Enforcement Guarantee** | REQ-416 | PARTIAL | `critical_dual_enforcement_audit.py` present in L5; per-requirement metadata reading + ≥2 enforcement layer verification not confirmed |
| **Dynamic Runtime Mutation Prohibition** | REQ-417 | PARTIAL | `runtime_mutation_guard.py` present; "runtime guard at module load AND class definition time" not confirmed as live guard |

### Extension Requirements

#### REQ-PT (Prompt Taxonomy, 12 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-PT-001 | CRITICAL | PARTIAL | Slot order enforcement (S0→I0→C0→U0) present in assembler; runtime abort on deviation not confirmed | No confirmed wave-abort on slot order violation |
| REQ-PT-002 | CRITICAL | PARTIAL | L5-only [S0] authorship — AST boundary scan present; runtime ownership validator unverified |
| REQ-PT-003 | CRITICAL | PARTIAL | [I0] mixin allowlist + VersionStore pointer-bound; L5 approval workflow unverified |
| REQ-PT-004 | CRITICAL | PARTIAL | [C0] context sanitizer — imperative verb forbid + sanitize/quote; runtime sanitizer not confirmed |
| REQ-PT-005 | CRITICAL | PARTIAL | `PromptBundleArtifact` type not confirmed as emitted with all required fields (slot_hashes, slot_sources, prompt_hash, policy_hash, blueprint_hash) |
| REQ-PT-006 | HIGH | PARTIAL | `PromptAssemblerVersion` + `TemplateRegistryHash` binding unverified |
| REQ-PT-007 | CRITICAL | PARTIAL | [U0] cannot override [S0]/[I0]/[D0] — runtime validator not confirmed |
| REQ-PT-008 | HIGH | PARTIAL | [D0] fences pre-execution injection + included in `prompt_hash` lineage not confirmed |
| REQ-PT-009 | CRITICAL | PARTIAL | No-timestamp/no-uuid4 enforcement in prompt assembly — wall-clock drift is widespread |
| REQ-PT-010 | CRITICAL | PARTIAL | Content-addressed prompt template IDs — raw strings forbidden outside prompt_governance; AST scan referenced but coverage unverified |
| REQ-PT-011 | CRITICAL | **FAIL** | **No negative control test found with XFAIL(strict=True) for prompt slot order tamper** |
| REQ-PT-012 | CRITICAL | PARTIAL | Dual-run stable prompt_hash + template_registry_hash not confirmed in CI |

#### REQ-EM (Embedding Utilization, 4 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-EM-001 | HIGH | PARTIAL | Coverage test for embedding utilization across all features not confirmed |
| REQ-EM-002 | HIGH | PARTIAL | Embedder metadata (embedder_id, version, dim) in replay inputs not confirmed |
| REQ-EM-003 | HIGH | PARTIAL | Deterministic embedding cache key enforcement unverified |
| REQ-EM-004 | CRITICAL | PARTIAL | Hard-fail on embeddings disabled — `embedding_factory.py` flag present; "no silent fallback" enforcement confirmed partially |

#### REQ-RAGX (Agentic RAG Schema, 6 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-RAGX-001 | HIGH | PARTIAL | RetrievalQuery schema enforced; deterministic sorting unverified |
| REQ-RAGX-002 | HIGH | PARTIAL | `namespace` field in RetrievalQuery — type exists; field presence unverified |
| REQ-RAGX-003 | HIGH | PARTIAL | CitationBundle fields + stable sort not confirmed |
| REQ-RAGX-004 | HIGH | PARTIAL | CitationBundle ID referenced in final output — output validator not confirmed |
| REQ-RAGX-005 | CRITICAL | PARTIAL | Byte verification of RetrievedChunks against repo bytes — not confirmed as live runtime gate |
| REQ-RAGX-006 | CRITICAL | PARTIAL | ExternalKnowledgeAccessViolation emission + wave abort not confirmed as live runtime gate |

#### REQ-CTX (Context Control, 2 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-CTX-001 | HIGH | PARTIAL | Context budget pre-execution enforcement present in `context_curator_engine.py`; route-recovery unverified |
| REQ-CTX-002 | CRITICAL | PARTIAL | `PreGuardSnapshot` with prompt_hash binding not confirmed |

#### REQ-APP (Application Boundary, 2 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-APP-001 | CRITICAL | PARTIAL | apps_* domain-fragment-only — AST scan present; runtime guard not confirmed |
| REQ-APP-002 | CRITICAL | PARTIAL | apps_* no direct provider SDK — AST scan + CI ratchet; completeness unverified |

#### REQ-TLM (Telemetry, 1 requirement)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-TLM-001 | HIGH | PARTIAL | INCIDENT/RESULT telemetry emission present; "missing telemetry is FAIL" validator not confirmed |

#### REQ-PHJ (Policy/HIL, 2 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-PHJ-001 | CRITICAL | PARTIAL | HIL approval artifact typed + signed + semantic_clock-bound not all confirmed |
| REQ-PHJ-002 | CRITICAL | PARTIAL | PolicyExceptionArtifact scope = single tick + reuse forbidden not confirmed |

#### REQ-MEMX (Shared Memory, 5 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-MEMX-001 | CRITICAL | PARTIAL | Episodic memory proposal-only present; direct mutation prevention not confirmed |
| REQ-MEMX-002 | HIGH | PARTIAL | Pre-planning episodic memory query — orchestrator invariant unverified |
| REQ-MEMX-003 | CRITICAL | PARTIAL | Append-only + versioned + ChangePackage-only writes — partial confirmation |
| REQ-MEMX-004 | HIGH | PARTIAL | Deterministic collision detection + INCIDENT with conflicting pointers not confirmed |
| REQ-MEMX-005 | HIGH | PARTIAL | Single authoritative active job state per trace_id + lock not confirmed |

#### REQ-WLD (World-Check, 4 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-WLD-001 | CRITICAL | PARTIAL | byte_sha256 binding per CitationBundle entry + runtime verification not confirmed as live |
| REQ-WLD-002 | CRITICAL | PARTIAL | Ghost mutation detection INCIDENT + abort not confirmed as live |
| REQ-WLD-003 | CRITICAL | PARTIAL | `context_set_hash` in ExecutionTrace covering all slots + CitationBundle — field not confirmed |
| REQ-WLD-004 | CRITICAL | PARTIAL | CognitiveDiff against trusted trace hash; advisory diffs rejected — runtime enforcement not confirmed |

#### REQ-DPO (DPO/RLHF Bounds, 3 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-DPO-001 | HIGH | PARTIAL | `rlhf_optimizer.py` present; [0.1, 2.0] clamp + delta≤0.1 + deterministic sort by (control_hash, candidate_hash) not confirmed |
| REQ-DPO-002 | CRITICAL | PARTIAL | DPO proposal-only gate + ChangePackage output + approval requirement not confirmed |
| REQ-DPO-003 | HIGH | PARTIAL | Deterministic + dataset-versioned DPO artifacts + replay inputs + evidence pack binding not confirmed |

#### REQ-COG (Cognitive Safety, 2 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-COG-001 | CRITICAL | **FAIL** | **`PolicyAlignmentCheck` and `PolicyViolationArtifact` not found anywhere in repository** |
| REQ-COG-002 | HIGH | PARTIAL | Prompt augmentation with dependency facts + MRO constraints + ≤300 tokens + logging — not confirmed |

#### REQ-HEALX (Healing Seam, 2 requirements)

| Req ID | Severity | Status | Missing Layers | Notes |
|--------|----------|--------|---------------|-------|
| REQ-HEALX-001 | CRITICAL | PARTIAL | `HealingProviderInvoker` referenced in dispatcher; injectable Protocol interface not found — no confirmed `FakeInvoker`/`DefaultInvoker` separation | Runtime dependency injection not confirmed |
| REQ-HEALX-002 | HIGH | PARTIAL | Typed `InvocationRecord` (tier, model_id, trace_id, prompt_hash, replay_key) not found as emitted + persisted to L4 |

---

## SECTION B — SUMMARY METRICS

| Metric | Count |
|--------|-------|
| **Total Requirements** | 486 |
| **PASS** | **6** |
| **PARTIAL** | **476** |
| **FAIL** | **4** |
| **DRIFT** | **0** (subsumed into PARTIAL — wall-clock drift is pervasive but not classified as architectural Drift) |
| **STRUCTURAL_ONLY** | **Embedded in PARTIAL for CRITICAL reqs** (REQ-007, REQ-008, REQ-009, REQ-027, REQ-055 and derived seam/sovereignty rows) |
| **CRITICAL PASS** | 2 (REQ-022, REQ-024) |
| **CRITICAL PARTIAL** | ~380 |
| **CRITICAL FAIL** | 2 (REQ-037, REQ-COG-001) |
| **HIGH FAIL** | 0 confirmed (all HIGH are PARTIAL or PASS) |
| **Enforcement Coverage %** | ~**12%** (only ~6/486 requirements have all stated enforcement layers positively confirmed) |

**Hard FAILs:**
- **REQ-037** — Negative control `XFAIL(strict=True)` covering all 5 tamper vectors: not found
- **REQ-PT-011** — Prompt slot order tamper negative control with `XFAIL(strict=True)`: not found
- **REQ-COG-001** — `PolicyAlignmentCheck` + `PolicyViolationArtifact`: not implemented
- **REQ-243/244** — `WaveAuditSummary` not found as a concrete emitting implementation

---

## SECTION C — ENFORCEMENT LAYER COVERAGE

| Layer | Coverage Assessment | Detail |
|-------|--------------------|----|
| **Runtime Guards** | ~30% implemented | Gateway, UWG, boundary_verifier, healing_tier_router, capability_chokepoint, embedding_factory — all present but runtime completeness low; most are PARTIAL |
| **AST Enforcement** | ~55% implemented | Strongest layer — extensive AST scanners, static checks, sovereignty files, import scanners |
| **CI Ratchet** | ~40% implemented | 17 CI workflows covering major domains; per-requirement ratchet with ID-level failure output: not confirmed |
| **Replay Binding** | ~15% implemented | Replay envelope + deterministic_replay_engine present; CitationBundle hash, embedding metadata, full side-effect reconstruction: not confirmed |
| **Determinism Binding** | ~20% implemented | Digest calculator + canonicalize + determinism.py present; wall-clock in 260+ files is a critical drift; dual-run stability: not CI-confirmed |
| **Signature Validation** | ~25% implemented | Packet-level HMAC + signature_verifier present; artifact-universal signing, enclave isolation, key-scope enforcement: not confirmed |
| **Schema Enforcement** | ~35% implemented | Rich type ecosystem; required field presence enforcement, schema version tracking, unknown-type rejection: partial |

---

## SECTION D — ARCHITECTURAL RISK SURFACE

### Top 10 Most Severe Enforcement Gaps

1. **Wall-Clock / UUID4 Contamination in Determinism Paths** (REQ-060, REQ-095, REQ-114, REQ-PT-009)
   — `uuid4` and `datetime.now`/`time.time()` appear in **737 matches across 260 files**. This is a systemic determinism breach. Replay determinism is unverifiable until this is resolved.

2. **Negative Control Tests Absent** (REQ-037, REQ-PT-011)
   — Both CRITICAL requirements for `XFAIL(strict=True)` negative controls covering prompt slot tamper, embedding misuse, CitationBundle bypass, hidden context injection: **HARD FAIL**. This means the enforcement is document-only — no test confirms enforcement actually triggers.

3. **Cognitive Safety Gate Missing** (REQ-COG-001)
   — `PolicyAlignmentCheck` and `PolicyViolationArtifact` not found anywhere in repo. **HARD FAIL**. Pre-response policy alignment check is entirely absent.

4. **WaveAuditSummary Not Implemented** (REQ-243, REQ-244)
   — No concrete `WaveAuditSummary` emitter found. Every wave must produce one; CI must fail on missing. Both are FAIL.

5. **Replay Input Incompleteness** (REQ-105, REQ-107, REQ-108)
   — `replay_envelope.py` exists but CitationBundle hash, RAG config_hash, embedding metadata, all slot_sources are not confirmed bound into replay inputs. Side-effect full reconstruction unverified. Replay is structurally partial.

6. **Emergency Freeze Orchestration Gap** (REQ-091, REQ-343..349)
   — Freeze type exists in routing artifacts. No runtime freeze gate enforcer found that implements all-five-component freeze (WriteGateway + token halt + promotion + routing + meta-learning) atomically. This is a CRITICAL availability-of-safety-controls gap.

7. **Prompt Governance Chokepoint Not Confirmed as Active Runtime Gate** (REQ-093, REQ-PT-001..007)
   — `prompt_governance/core/` files exist but enforcement of slot order, slot ownership, PromptBundleArtifact emission, and bypass-abort are not confirmed as live runtime gates. Documentation-only compliance risk.

8. **HMAC Key Enclave + Scope Enforcement Unverified** (REQ-186..190, REQ-390..407)
   — `key_source.py` present; no confirmed SignatureEnclave isolation (isolated process, no memory sharing with L2), key-scope enforcement per artifact type, expired-key hard rejection. CRITICAL structural gap.

9. **Meta-Learning Stage Pipeline Unverified** (REQ-058..REQ-079)
   — Named components `CooldownValidator`, `MinSampleValidator`, `OscillationDetector` not found. Stage 7 composition of all 4 validators unverified. Stage 9 as sole VersionStore writer unverified. Entire meta-learning pipeline is PARTIAL-at-best with multiple CRITICAL unverified invariants.

10. **Cross-Layer Sovereignty Runtime Missing** (REQ-001..006, REQ-009, REQ-117..120)
    — Layer sovereignty enforced structurally via AST and CI but **runtime boundary assertions at L0/L1/L4/L5/L6 are not confirmed as live import hooks or execution-time interceptors**. STRUCTURAL_ONLY classification for CRITICAL requirements is a severe gap.

---

### Cross-Layer Sovereignty Violations (Risk Areas)

- `uuid4` and `datetime.now` appear in **L1, L2, L3, L4, L5 agents** — direct violation of REQ-114 in determinism paths
- Wall-clock timestamps found in **healing agents, orchestration agents, cognitive engine** — violates REQ-060, REQ-095
- apps_* runtime import hook not confirmed — REQ-001/002/003 rely on AST-only enforcement

### Gateway Bypass Risk Areas

- `llm_provider_mixin.py` references `SovereignLLMGateway` but also contains 4 direct gateway references — bypass risk
- `network_egress_guard.py` exists but localhost endpoint blocking unverified (REQ-414)
- Provider substitution prohibition file exists but CI negative control test absent (REQ-415)

### Determinism Drift Surfaces

- 737 wall-clock/uuid4 occurrences across 260 files
- `L1_cognition/engines/cognitive_engine.py` (16 matches) — directly in the cognitive path
- `L3_orchestration/reasoning/` agents — orchestration non-determinism
- `L2_execution/enforcement/budget_enforcer.py` (10 matches) — enforcement code itself is non-deterministic

### Replay Incompleteness

- `replay_envelope.py` is the only replay input container found — missing CitationBundle hash, embedding metadata, slot_sources artifact IDs
- No dual-run CI test confirmed
- `ReplayRunArtifact` emission unconfirmed
- Replay sandbox (read-only, no network/SDK) not confirmed as enforced at harness level

### Missing Runtime Abort Semantics

- **REQ-COG-001**: No `PolicyAlignmentCheck` runtime abort
- **REQ-RAGX-006**: `ExternalKnowledgeAccessViolation` + wave abort not confirmed as live gate
- **REQ-WLD-002**: Ghost mutation INCIDENT + abort not confirmed
- **REQ-091**: Tier III freeze atomic orchestration missing
- **REQ-243**: WaveAuditSummary missing means audit completeness CI gate cannot fire

### Areas with Documentation-Only Compliance

The following domains have type definitions and interface declarations but **no confirmed live runtime enforcement**:
- Prompt slot ownership (REQ-PT-002, REQ-PT-007)
- [C0] content sanitizer (REQ-PT-004)
- PreGuardSnapshot capture (REQ-CTX-002)
- PolicyExceptionArtifact single-tick TTL (REQ-PHJ-002)
- DPO proposal-only gate (REQ-DPO-002)
- HealingProviderInvoker injectable Protocol (REQ-HEALX-001)
- WaveAuditSummary emission (REQ-243/244)
- Cross-wave hash linkage via `prev_wave_hash` (REQ-253/254)

---

**END OF GAP ANALYSIS REPORT**

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

