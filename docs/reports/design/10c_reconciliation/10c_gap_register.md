# 10C Semantic Reconciliation Gap Register

**Generated:** 2025-01-23  
**Source:** Post-10B semantic reconciliation across full markdown architecture corpus  
**Baseline:** 10a baseline_requirements.md (28 requirements)  
**Comparison:** 10b requirements_traceability_matrix.md  
**Corpus Ingested:** 22 files in docs/reference/

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total 10C requirements extracted | 173 |
| 10a explicit coverage | 31 |
| 10a partial coverage | 84 |
| 10a no coverage | 58 |
| Net new requirements | 132 |
| Critical severity gaps | 18 |
| High severity gaps | 62 |

---

## Serial Gap Register

### GAP-10C-001: Embedding/Retrieval Substrate Deeply Under-Specified

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-001 |
| **severity** | CRITICAL |
| **impacted_req_ids** | 10C-REQ-016 through 10C-REQ-028, 10C-REQ-163, 10C-REQ-165, 10C-REQ-166 |
| **source_files** | 00B_token_vector_mechanics.md, Contextual Refinement in Transformer Models.md |
| **what corpus requires** | Complete token-to-vector mechanics pipeline: tokenizer load, tokenization, checkpoint resolution, weight load, forward pass, pooling/projection, normalization, output contract; PLUS encoder-only vs decoder-only architectural distinction with bidirectional vs causal attention and pooling ferry vs vocabulary exit divergence |
| **what 10a covers** | REQ-027 mentions "five storage surfaces" for vector store but NONE of the embedding generation internals |
| **what 10b covers** | Not traced - no repo evidence for embedding internals |
| **why gap exists** | 10a baseline started at REQ-001 focusing on runtime layers (L0-L6) and completely omitted the offline embedding/retrieval substrate internals |
| **missing tests/benchmarks** | Tests for tokenizer compatibility, forward pass correctness, pooling quality, L2 normalization, encoder/decoder separation |
| **HITL required** | YES - architectural decision on embedding model binding (BAAI/bge-m3 vs alternatives) |
| **remediation objective** | Extract or implement embedding generation pipeline with explicit encoder-only (bidirectional) vs generation LLM (causal) separation |

---

### GAP-10C-002: Sparse Index and Hybrid Merge Absent from Baseline

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-002 |
| **severity** | HIGH |
| **impacted_req_ids** | 10C-REQ-036 through 10C-REQ-048 |
| **source_files** | 00D_sparse_index_hybrid_merge.md |
| **what corpus requires** | Complete sparse index build pipeline: normalize, extract IDs/fields/terms/phrases/symbols, tokenize, weight with title/field boost, inverted index build, sparse store, canonical store; PLUS query-time sparse path, dense path, hybrid merge with sparse priority, governance filters, hydrate |
| **what 10a covers** | NONE - no sparse index requirements in 28 baseline |
| **what 10b covers** | No repo evidence for sparse indexing |
| **why gap exists** | 10a assumed dense-only vector retrieval; corpus mandates hybrid sparse+dense |
| **missing tests/benchmarks** | Sparse index build tests, hybrid merge accuracy, sparse priority enforcement |
| **HITL required** | NO - technical implementation decision |
| **remediation objective** | Implement sparse index builder and hybrid merge query path |

---

### GAP-10C-003: C0 Governance Plane (G1-G7) Completely Missing

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-003 |
| **severity** | CRITICAL |
| **impacted_req_ids** | 10C-REQ-110 through 10C-REQ-116 |
| **source_files** | C0_Governance_Safety_Enforcement.md |
| **what corpus requires** | Complete governance plane: G1 triage mode selection, G2 authority context binding, G3 layer isolation check, G4 registry validation, G5 classify shape, G6 policy chokepoint, G7 sovereign egress with fail-closed |
| **what 10a covers** | REQ-023 mentions "ACL prefilter" but NONE of the C0 governance stages |
| **what 10b covers** | Partial ACL enforcement in routing layer |
| **why gap exists** | 10a conflated governance with routing; corpus separates C0 as cross-cutting policy plane |
| **missing tests/benchmarks** | Governance stage tests, fail-closed enforcement, prompt injection detection |
| **HITL required** | YES - policy chokepoint thresholds and risk tiering |
| **remediation objective** | Implement C0 governance plane with G1-G7 stages and fail-closed sovereign egress |

---

### GAP-10C-004: C1 Deterministic Replay Plane Completely Missing

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-004 |
| **severity** | CRITICAL |
| **impacted_req_ids** | 10C-REQ-117 through 10C-REQ-121 |
| **source_files** | C1_Deterministic_Replay_Execution_Integrity.md |
| **what corpus requires** | Replay envelope build with replay_key policy_hash capability_token run_id; Freeze signal propagation L0->L3->L5->L2; Determinism surface enforcement (Run Clock Only Seeded Only Stable IDs Only Photocopy Calls One Snapshot Only Proposal Only); Replay guard wrapping all invocations; Determinism digest seal |
| **what 10a covers** | NONE - no replay requirements in 28 baseline |
| **what 10b covers** | No deterministic replay implementation |
| **why gap exists** | 10a focused on live runtime only; corpus mandates replay for audit/regression |
| **missing tests/benchmarks** | Replay envelope tests, freeze propagation, determinism verification, wall clock interception, seeded random, stable ID tests |
| **HITL required** | YES - replay strictness tradeoffs (performance vs auditability) |
| **remediation objective** | Implement C1 replay plane with envelope propagation guards and digest sealing |

---

### GAP-10C-005: C2 Observability/Telemetry Plane Completely Missing

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-005 |
| **severity** | HIGH |
| **impacted_req_ids** | 10C-REQ-128 through 10C-REQ-134 |
| **source_files** | C2_Observability_Telemetry_Control_Signals.md |
| **what corpus requires** | L6 read surfaces (sealed trace, exit dispositions, L4 telemetry, baseline metrics); S1 time audit; S2 isolation check; S3 drift detection; S4 packet seal; BUS D/E live control signals; BUS T async telemetry |
| **what 10a covers** | REQ-021 mentions "shadow evaluation" but not C2 observability stage requirements |
| **what 10b covers** | Basic telemetry collection exists |
| **why gap exists** | 10a conflated L6 shadow eval with C2 observability; corpus separates them |
| **missing tests/benchmarks** | Time audit tests, isolation verification, drift detection accuracy, bus signal emission |
| **HITL required** | NO - technical implementation |
| **remediation objective** | Implement C2 observability plane with S1-S4 stages and bus D/E/T signaling |

---

### GAP-10C-006: C3 Healing/Remediation/Escalation Plane Under-Specified

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-006 |
| **severity** | CRITICAL |
| **impacted_req_ids** | 10C-REQ-135 through 10C-REQ-140 |
| **source_files** | C3_Healing_Remediation_Escalation.md |
| **what corpus requires** | Failure signal from context only no hallucination; Local heal deterministic rule fix; Heal confidence scoring with tier routing (High->Local Agent Medium->Qwen_vLLM Low->Gemini_2.5_Pro); Sovereign gateway; Secure reading room bounded packet only; Zero-loss failure containment with freeze UWG lock audit handoff L4 note L6 tune |
| **what 10a covers** | REQ-010 mentions "heal loop" but NONE of the tiered routing or zero-loss containment details |
| **what 10b covers** | Basic heal loop exists |
| **why gap exists** | 10a simplified healing to single loop; corpus mandates tiered model routing and zero-loss containment |
| **missing tests/benchmarks** | Tier routing tests, zero-loss freeze verification, UWG diff locking |
| **HITL required** | YES - model tier thresholds and confidence scoring |
| **remediation objective** | Implement C3 healing plane with tiered model routing and zero-loss containment |

---

### GAP-10C-007: C4 Universal Write Governance (UWG) Deeply Missing

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-007 |
| **severity** | CRITICAL |
| **impacted_req_ids** | 10C-REQ-122 through 10C-REQ-127 |
| **source_files** | C4_State_Sovereignty_Universal_Write_Governance.md |
| **what corpus requires** | UWG singleton clerk; Verify signature compliance_hash policy_hash capability tokens; Catalog rules RBAC blast radius before-after diff; Claim write lock prevent ghost writes; Commit + hash-chain append; Refresh read surfaces alias swap cache clear |
| **what 10a covers** | NONE - no UWG requirements in 28 baseline |
| **what 10b covers** | No durable commit via UWG |
| **why gap exists** | 10a missed the entire write governance layer; corpus emphasizes UWG as sole ink path |
| **missing tests/benchmarks** | UWG serialization tests, hash-chain verification, alias swap atomics, cache clearing |
| **HITL required** | YES - write authorization thresholds and RBAC rules |
| **remediation objective** | Implement C4 UWG plane with serialized write queue and hash-chain durability |

---

### GAP-10C-008: C6 Evaluation/Learning/Promotion System Under-Specified

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-008 |
| **severity** | HIGH |
| **impacted_req_ids** | 10C-REQ-146 through 10C-REQ-154 |
| **source_files** | C6_Evaluation_Learning_Promotion_System.md |
| **what corpus requires** | Phase 1 current run exit review; L6 analysis core (outcome B trajectory C regression D calibration F); E signal aggregator; Archive freeze 1-3; Case file compilation 4; Investigation 5; Rule drafting 6; Commandant gauntlet 7 (shadow replay regression safety SME sign-off promotion readiness sovereign approve/veto); Knowledge extraction 8 |
| **what 10a covers** | REQ-019 REQ-021 cover metrics and learning but NOT the 8-phase learning pipeline |
| **what 10b covers** | Basic evaluation exists |
| **why gap exists** | 10a simplified to metrics collection; corpus mandates full 8-phase learning promotion system |
| **missing tests/benchmarks** | Shadow replay tests, gauntlet safety validation, SME sign-off workflow |
| **HITL required** | YES - promotion readiness criteria and sovereign approve/veto |
| **remediation objective** | Implement C6 8-phase learning system with commandant gauntlet gating |

---

### GAP-10C-009: C7 Capability/Tool/Model Access Control Plane Missing

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-009 |
| **severity** | CRITICAL |
| **impacted_req_ids** | 10C-REQ-155 through 10C-REQ-161 |
| **source_files** | C7_Capability_Tool_Model_Access_Control_Plane.md |
| **what corpus requires** | G1 classify access type; G2 registry allowed set validation; G3 choose lane; G4 build access ticket capability_token sandbox_envelope; G5 intercept call validate args route target injection checks risk tiering; G6 sovereign egress no silent fallback exactly one approved path; G7 invocation record usage provider tool cost audit log |
| **what 10a covers** | REQ-020 mentions capability tokens but NONE of the C7 plane stages |
| **what 10b covers** | No C7 capability plane implementation |
| **why gap exists** | 10a mentioned tokens but missed the full capability control plane; corpus mandates G1-G7 |
| **missing tests/benchmarks** | Access classification tests, lane routing, ticket generation, call interception, egress mapping |
| **HITL required** | YES - allowed model sets and risk tiering thresholds |
| **remediation objective** | Implement C7 capability plane with G1-G7 stages and no-silent-fallback egress |

---

### GAP-10C-010: Row-Level Stage Requirements Not Captured in 10a

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-010 |
| **severity** | HIGH |
| **impacted_req_ids** | 10C-REQ-049 through 10C-REQ-088 (E1-E6 I1-I4 M1-M4 P1-P4 V1-V5 R1A-R5 PA.1-PA.4) |
| **source_files** | 01_request_intake.md, 02_L1_Reasoning_Plan_Generation.md, 03_Route_Decision_Switching.md |
| **what corpus requires** | 40+ row-level stage requirements extracted from ASCII diagrams and prose blocks at granular level |
| **what 10a covers** | REQ-001 through REQ-008 cover stages generally but NOT at row level (e.g., REQ-001 has E1-E6 as one requirement) |
| **what 10b covers** | Implementation covers stages but not explicit row-level artifacts |
| **why gap exists** | 10a collapsed ASCII diagram stages into high-level requirements; corpus mandates row-per-stage-unit |
| **missing tests/benchmarks** | Stage-level unit tests for each row requirement |
| **HITL required** | NO - documentation alignment only |
| **remediation objective** | Expand 10a baseline to include row-level stage requirements OR document as 10c delta |

---

### GAP-10C-011: C5 Retrieval/Prompt Assembly Duplication and Mismatch

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-011 |
| **severity** | MEDIUM |
| **impacted_req_ids** | 10C-REQ-141 through 10C-REQ-145 |
| **source_files** | C5_Retrieval_Prompt_Assembly.md |
| **what corpus requires** | C5-specific C0.1-C0.4 retrieval pipeline; offline catalog build; chunk tag index vectors lineage graph |
| **what 10a covers** | REQ-007 REQ-008 cover C0 and prompt assembly generally |
| **what 10b covers** | Partial C0 implementation |
| **why gap exists** | 10a covered C0 in 03_Route_Decision_Switching; C5 file has duplicate/similar content; divergence risk |
| **missing tests/benchmarks** | Cross-file consistency tests |
| **HITL required** | YES - which C0 spec is authoritative |
| **remediation objective** | Reconcile C0 between 03_Route_Decision_Switching and C5_Retrieval_Prompt_Assembly; select SSOT |

---

### GAP-10C-012: Model-Role Separation Not Normatively Captured

| Field | Value |
|-------|-------|
| **gap_id** | GAP-10C-012 |
| **severity** | CRITICAL |
| **impacted_req_ids** | 10C-REQ-007, 10C-REQ-137, 10C-REQ-163 through 10C-REQ-166 |
| **source_files** | 00_ingestion_pipeline_index_build.md, Contextual Refinement in Transformer Models.md, C3_Healing_Remediation_Escalation.md |
| **what corpus requires** | Embedding model (encoder-only bidirectional) vs Generation LLM (decoder-only causal) MUST be architecturally separated; Chunk-by-chunk vs current prompt prefix scope constraints; Pooling ferry chunk vector vs Vocabulary exit next-token divergence |
| **what 10a covers** | NONE - no model-role separation in 28 baseline |
| **what 10b covers** | No explicit model binding separation |
| **why gap exists** | 10a assumed single model type; corpus mandates strict architectural separation |
| **missing tests/benchmarks** | Model role binding tests, architecture violation detection |
| **HITL required** | YES - model binding matrix and tier routing thresholds |
| **remediation objective** | Create explicit model-role binding matrix and enforce encoder/decoder separation |

---

## Gap Severity Summary

| Severity | Count | Gap IDs |
|----------|-------|---------|
| CRITICAL | 7 | GAP-10C-001 GAP-10C-003 GAP-10C-004 GAP-10C-006 GAP-10C-007 GAP-10C-009 GAP-10C-012 |
| HIGH | 4 | GAP-10C-002 GAP-10C-005 GAP-10C-008 GAP-10C-010 |
| MEDIUM | 1 | GAP-10C-011 |

---

## Delta Remediation Plan

### Phase 1: Critical Infrastructure (Weeks 1-4)

| Gap ID | Remediation Action | Owner | Priority |
|--------|-------------------|-------|----------|
| GAP-10C-007 | Implement C4 UWG with hash-chain durability | Architecture | P0 |
| GAP-10C-004 | Implement C1 replay plane with determinism guards | Architecture | P0 |
| GAP-10C-003 | Implement C0 governance plane G1-G7 | Security | P0 |
| GAP-10C-009 | Implement C7 capability plane G1-G7 | Security | P0 |

### Phase 2: Retrieval & Embedding (Weeks 3-6)

| Gap ID | Remediation Action | Owner | Priority |
|--------|-------------------|-------|----------|
| GAP-10C-001 | Implement embedding pipeline with model-role separation | ML/Infra | P1 |
| GAP-10C-002 | Implement sparse index and hybrid merge | Search | P1 |
| GAP-10C-012 | Create model binding matrix | Architecture | P1 |

### Phase 3: Healing & Learning (Weeks 5-8)

| Gap ID | Remediation Action | Owner | Priority |
|--------|-------------------|-------|----------|
| GAP-10C-006 | Implement C3 healing with tier routing | Reliability | P2 |
| GAP-10C-008 | Implement C6 learning pipeline | ML/Eval | P2 |
| GAP-10C-005 | Implement C2 observability plane | Observability | P2 |

### Phase 4: Documentation Alignment (Weeks 7-10)

| Gap ID | Remediation Action | Owner | Priority |
|--------|-------------------|-------|----------|
| GAP-10C-010 | Expand 10a baseline with row-level requirements | Docs | P3 |
| GAP-10C-011 | Reconcile C5 and 03_Route C0 specs | Architecture | P3 |

---

## Alias/Terminology SSOT

| Corpus Term | 10a Term | Canonical Term | Definition |
|-------------|----------|----------------|------------|
| query_vec | query embedding | query_vec (blue) | Query-side semantic seeker vector |
| raw_text_vector | document embedding | raw_text_vector (orange) | Document-side literal semantic map |
| contextual_text_vector | contextual embedding | contextual_text_vector (orange) | Document-side semantic overlay map |
| UWG | durable commit | Universal Write Gate | Sole write path for all mutations |
| L5 | policy plane | L5 Live Runtime Exit Control | Cross-cutting authority over exits |
| C0 | retrieval layer | C0 Context Engine | Grounded retrieval only no routing |
| L2 | execution | L2 Live Task Dispatch | Tool/model invocation no direct write |
| L1 | reasoning | L1 Reasoning Plan Generation | Internal planning no execution |
| L0 | routing | L0 Route Decision Switching | Path selection no retrieval |
| L6 | shadow eval | L6 Shadow Evaluation | Async post-run analysis |

---

## Data Contract Matrix (Sample)

| Contract | Source | Consumer | Fields | Invariant |
|----------|--------|----------|--------|-----------|
| Ingress Output | E6 | L1 | validated_request request_id trace_root caller_scope | No routing authority at ingress |
| L1 Plan | P4 | L0 | proposed_route query_spec task_spec route_risk grounding_required | No execution no retrieval |
| L0 PromptEnvelope | PA.4 | L2 | verified_context task_spec citation_anchors HMAC replay | C0 before U0 ordering enforced |
| L2 Sealed Artifact | E5 | L5 | payload traces replay_receipts terminal_class | No durable commit |
| UWG Commit | C4 Refresh | L4 | ledger_write hash_chain_audit alias_swap | Sole ink path enforced |

---

## HITL Decision Log Template

| Decision ID | Date | Decision | Stakeholders | Rationale | Status |
|-------------|------|----------|--------------|-----------|--------|
| HITL-10C-001 | TBD | Embedding model binding (bge-m3 vs alternatives) | ML/Infra/Security | Accuracy vs latency tradeoff | PENDING |
| HITL-10C-002 | TBD | Replay strictness (determinism vs performance) | Architecture/Reliability | Auditability cost | PENDING |
| HITL-10C-003 | TBD | Healing confidence thresholds (High/Med/Low routing) | Reliability/ML | Model tier routing boundaries | PENDING |
| HITL-10C-004 | TBD | C5 C0 authority (03_Route vs C5_Retrieval) | Architecture/Docs | SSOT selection | PENDING |

---

*End of 10C Gap Register*
