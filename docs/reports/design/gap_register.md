# Gap Register
**Phase**: Design Only — No code changes permitted  
**Date**: 2026-04-09  

Severity: `P0-CRITICAL` | `P1-HIGH` | `P2-MEDIUM` | `P3-LOW`

---

## GAP-001 — Ingress Envelope: No Unified Intake Contract
| Field | Value |
|---|---|
| **gap_id** | GAP-001 |
| **req_ids** | REQ-001, REQ-002 |
| **severity** | P0-CRITICAL |
| **category** | Intake / ingress validation |
| **description** | No single dedicated ingress envelope module enforces the E1–E6 checklist (transport validation → auth → quota → schema → normalization → stamp) as one atomic pre-pipeline gate. The closest implementation is `api_gateway_integration.py` (generic multi-gateway stub supporting Kong/Envoy/AWS) which handles rate limiting and tracing headers, but lacks: (a) tenant binding to caller_scope_baseline, (b) enforcement of request_id + session_id + trace_root as mandatory output fields, (c) rejection slip artifact with reason_code. Rate limiting lives in `knowledge/concurrency/rate_limiter.py` which is semantically incorrect layer placement. |
| **evidence** | `gateway/api_gateway_integration.py` — multi-gateway generic; `knowledge/concurrency/rate_limiter.py` — wrong layer; no `L5_safety` or ingress-layer module found for E1–E6 contract |
| **risk_if_unaddressed** | Requests without auth, with stale tenants, or with malformed schemas enter the reasoning pipeline. Trace_root not stamped = no end-to-end trace. Rate limiting enforcement is layer-misplaced, bypassable by direct L1 invocation. |
| **recommended_resolution** | Create `L5_safety/enforcement/ingress_envelope_check.py` implementing E1–E6 as an enforced pre-pipeline gate. Stamp request_id, session_id, trace_root. Emit rejection slip with reason_code on any failure. Move rate limiter invocation to this gate. |
| **blast_radius** | L5 (new module), gateway (routing change), L1 (must accept stamped request only) |
| **confidence_that_gap_is_real** | 0.85 |
| **HITL_before_fix** | No |

---

## GAP-002 — L1 Plan Contract: No Formal Typed Output Schema
| Field | Value |
|---|---|
| **gap_id** | GAP-002 |
| **req_ids** | REQ-003 |
| **severity** | P1-HIGH |
| **category** | L1 reasoning / plan contract |
| **description** | `L1_cognition` has `reasoning_chokepoint.py`, `cognitive_engine.py`, and various types, but a single mandatory typed `L1PlanContract` dataclass with all seven required fields (proposed_route, query_spec, task_spec, route_risk, confidence, grounding_required, assumption_gaps) is not confirmed as the enforced output shape. Without this, the L0 router cannot deterministically consume L1 output. |
| **evidence** | `L1_cognition/enforcement/reasoning_chokepoint.py` exists; `L1_cognition/types/` has rag_types, search_types, guardrail_types — no `plan_contract_types.py` identified |
| **risk_if_unaddressed** | L0 router receives untyped or variably-shaped L1 output; route selection becomes implicit; grounding_required flag missing means C0 retrieval may not fire |
| **recommended_resolution** | Create `L1_cognition/types/plan_contract_types.py` with `L1PlanContract` dataclass; enforce as output type in `reasoning_chokepoint.py`; add validation in L0 input receiver. |
| **blast_radius** | L1 types, L1 chokepoint, L0 routing input parser |
| **confidence_that_gap_is_real** | 0.82 |
| **HITL_before_fix** | No |

---

## GAP-003 — Prompt Assembly: No HMAC Signing + Token Overflow→ABSTAIN Path
| Field | Value |
|---|---|
| **gap_id** | GAP-003 |
| **req_ids** | REQ-008 |
| **severity** | P1-HIGH |
| **category** | C0 retrieval / evidence shaping / prompt assembly |
| **description** | `prompt_assembler.py` emits trace events and loads policy references, but HMAC signing of the PromptEnvelope is not confirmed. The C0-slot-before-U0 ordering rule and token overflow→ABSTAIN path are also unconfirmed. `compiled_artifact_types.py` has envelope shape. `token_enforcement_types.py` and `token_budget_loader.py` exist but wiring to overflow→ABSTAIN disposition is unconfirmed. |
| **evidence** | `prompt_governance/contracts/compiled_artifact_types.py` — envelope types; `L2_execution/types/token_enforcement_types.py` — token types; no HMAC signing confirmed in prompt_assembler.py first 50 lines |
| **risk_if_unaddressed** | Prompt envelope integrity unverifiable on replay; C0 evidence slotted after U0 policy allows user-context to pollute policy framing; token overflow silently truncates without triggering ABSTAIN, producing hallucinated completions |
| **recommended_resolution** | Add HMAC signing step (PA.4) to `prompt_assembler.py` using a stable key from capability_token; enforce C0-before-U0 slot ordering validator; wire token budget overflow to emit ExitDisposition.ABSTAIN. |
| **blast_radius** | prompt_governance/core, L2 exit path, token budget config |
| **confidence_that_gap_is_real** | 0.80 |
| **HITL_before_fix** | No |

---

## GAP-004 — Exit Control Gate: No Standalone X1A–X1D Evaluation Module
| Field | Value |
|---|---|
| **gap_id** | GAP-004 |
| **req_ids** | REQ-012 |
| **severity** | P0-CRITICAL |
| **category** | Exit control / runtime evaluation |
| **description** | The architecture mandates a four-dimensional exit evaluation (X1A: rules/rubrics, X1B: prompt/format fit, X1C: policy/secrets/mutation/replay, X1D: groundedness/citation/abstain) producing one of four explicit exit dispositions. `policy_enforcement_point.py` and `policy_action_contract.py` exist but cover policy enforcement broadly; no single module implementing the complete X1A–X1D evaluation matrix with ExitDisposition enum is confirmed. `outcome_logger.py` logs outcomes but does not gate them. No-silent-fallback rule is unconfirmed at this boundary. |
| **evidence** | `L5_safety/enforcement/policy_enforcement_point.py`; `L5_safety/enforcement/policy_action_contract.py`; `L6_observability/enforcement/outcome_logger.py` — but no `exit_control_gate.py` found |
| **risk_if_unaddressed** | Unsafe, grounding-failed, or policy-violating L2 artifacts may reach the response path without a formal gating decision. COMMIT_TO_UWG path may fire without groundedness check. Silent fallback from ESCALATE to ALLOW is possible. |
| **recommended_resolution** | Create `L5_safety/enforcement/exit_control_gate.py` implementing X1A–X1D evaluation and ExitDisposition enum {ALLOW_RESPONSE, DENY_RETURN, ESCALATE_TO_HITL, COMMIT_TO_UWG}. Wire to `outcome_logger`. Enforce no-silent-fallback: unknown/error disposition always → DENY_RETURN. |
| **blast_radius** | L5_safety/enforcement, response path, UWG trigger path, HITL trigger path |
| **confidence_that_gap_is_real** | 0.80 |
| **HITL_before_fix** | YES — HITL-003: implementation path ambiguous |

---

## GAP-005 — HITL Re-Clearance Sequence: Ambiguous Exit-Control vs Healing HITL Paths
| Field | Value |
|---|---|
| **gap_id** | GAP-005 |
| **req_ids** | REQ-013 |
| **severity** | P0-CRITICAL |
| **category** | HITL / escalation / re-clearance |
| **description** | `hitl_gate.py` enforces destructive-operation approval in the healing pipeline (H1/N/S/A prompts, TTY-required, abort on no-TTY). `re_clear_loop_enforcer.py` and `final_airlock_trimmer_enforcer.py` exist. However, the exit-control HITL path (H1: freeze authority_state=FROZEN + write_auth=NONE; H2: materialize bounded packet; H3: human reviews only bounded packet; H4: treat human input as untrusted DATA; H5: L5 re-clearance before ALLOW/COMMIT) is not confirmed as a distinct code path separate from the healing HITL. If the same `hitl_gate.py` serves both, the exit-control freeze semantics (no write_auth) may not be enforced. |
| **evidence** | `L5_safety/enforcement/hitl_gate.py` — healing-focus doc; `L5_safety/enforcement/re_clear_loop_enforcer.py`; `L5_safety/enforcement/final_airlock_trimmer_enforcer.py` — exist; no separate exit-control HITL module confirmed |
| **risk_if_unaddressed** | Human review of exit-control HITL may bypass L5 re-clearance; human-modified output may enter response/commit path without policy re-validation; authority_state may not be frozen during review, allowing concurrent mutations |
| **recommended_resolution** | HITL decision required before implementation: confirm whether exit-control HITL should be a distinct module from healing HITL, or whether existing modules cover both paths. See HITL-004. |
| **blast_radius** | L5_safety/enforcement, HITL trigger, re-clearance loop, exit gate, UWG commit path |
| **confidence_that_gap_is_real** | 0.78 |
| **HITL_before_fix** | YES — HITL-004 |

---

## GAP-006 — Heal Loop: Same-Snapshot Policy Binding Not Enforced
| Field | Value |
|---|---|
| **gap_id** | GAP-006 |
| **req_ids** | REQ-010 |
| **severity** | P1-HIGH |
| **category** | L2 execution / validation / healing |
| **description** | The architecture mandates that the heal loop reads the SAME blueprint_hash/policy_hash snapshot as the original execution. `IHealerProtocol.py` and `IHealingStrategyProtocol.py` define healer interfaces; `circuit_breaker_gate.py` provides oscillation protection. However, enforcement that the heal context binds the same policy_hash and blueprint_hash as the originating execution context is not confirmed. Additionally, parent_packet_id binding in heal requests is not confirmed, making repair ancestry tracing incomplete. |
| **evidence** | `interfaces/IHealerProtocol.py`; `interfaces/IHealingStrategyProtocol.py`; `L5_safety/enforcement/HealingStrategy.py`; `L5_safety/enforcement/circuit_breaker_gate.py` — oscillation guard |
| **risk_if_unaddressed** | Heal loop may silently upgrade to a newer policy version mid-run, making the repair non-deterministic and non-replayable; repair ancestry chain broken if parent_packet_id is missing |
| **recommended_resolution** | Add `policy_hash` and `blueprint_hash` as mandatory fields in heal request types; add assertion in `HealingStrategy` initialization that heal_context.policy_hash == originating_context.policy_hash; add `parent_packet_id` to `HealRequest` type. |
| **blast_radius** | L5_safety/enforcement, L2_execution/types, IHealerProtocol |
| **confidence_that_gap_is_real** | 0.80 |
| **HITL_before_fix** | No |

---

## GAP-007 — C0 Evidence Contract: No Formal C0EvidenceContract Type
| Field | Value |
|---|---|
| **gap_id** | GAP-007 |
| **req_ids** | REQ-007 |
| **severity** | P1-HIGH |
| **category** | C0 retrieval / evidence shaping / prompt assembly |
| **description** | Hybrid retrieval (dense+sparse), reranker models (c0_reranker, advanced_c0_reranker), and sovereign RAG orchestrator exist. Evidence shaping components are present. However, the C0.4 evidence contract — a typed output specifying verified_chunks, cited_spans, source_ids, coverage_score, abstain_hint, and contradiction_flags — is not confirmed as a mandatory output shape from the retrieval pipeline. Without it, the prompt assembly layer cannot make well-formed token budget and ABSTAIN decisions. |
| **evidence** | `L3_orchestration/reasoning/engines/hybrid_search_engine.py`; `knowledge/retrieval/hybrid_recall_stage.py`; `L1_cognition/reasoning/ml_decision_support/models/c0_reranker.py` — evidence shaping exists; no `C0EvidenceContract` type file found |
| **risk_if_unaddressed** | Prompt assembler receives untyped retrieval results; coverage_score missing means overflow→ABSTAIN cannot trigger correctly; abstain_hint missing means low-coverage answers pass through |
| **recommended_resolution** | Create `L3_orchestration/types/c0_evidence_contract_types.py` with `C0EvidenceContract` dataclass; enforce as mandatory output of retrieval pipeline; wire `abstain_hint` to prompt assembler's ABSTAIN trigger. |
| **blast_radius** | L3_orchestration/types, retrieval pipeline output, prompt assembler input |
| **confidence_that_gap_is_real** | 0.82 |
| **HITL_before_fix** | No |

---

## GAP-008 — C2 Observability: No Unified Verify Spine + L6EvidenceBundle Type
| Field | Value |
|---|---|
| **gap_id** | GAP-008 |
| **req_ids** | REQ-018 |
| **severity** | P1-HIGH |
| **category** | Observability / telemetry / anomaly signals |
| **description** | L6 observability components (shadow_replay_integration, determinism_digest_emitter, drift_detector, agent_monitor, outcome_logger) exist but are scattered. No single `verify_spine.py` orchestrator executing all four checks (time audit, isolation check, drift detection, packet seal) in sequence is confirmed. The formalized `L6EvidenceBundle` type with five mandatory fields (replay_key, determinism_status, anomaly_flags, audit_traces, normalized_metrics) is not confirmed. BUS_D/BUS_E live control signal emission path to exit gate is not confirmed. |
| **evidence** | `L6_observability/utils/evaluation/shadow_replay_integration.py`; `L6_observability/utils/engines/drift_detector.py`; `L6_observability/enforcement/agent_monitor.py`; `L6_observability/enforcement/outcome_logger.py` — individual components exist; no verify_spine.py or L6EvidenceBundle type file found |
| **risk_if_unaddressed** | Observability signals are generated but not reliably delivered to the exit gate as live control signals; anomaly detection may not trigger DENY/ESCALATE; L6 learning loop may receive untyped telemetry |
| **recommended_resolution** | Create `L6_observability/enforcement/verify_spine.py` orchestrating four-check sequence; create `L6_observability/types/l6_evidence_bundle_types.py`; wire BUS_D/BUS_E to exit_control_gate.py (GAP-004 resolution). |
| **blast_radius** | L6_observability/enforcement, L6_observability/types, exit gate wire-up |
| **confidence_that_gap_is_real** | 0.78 |
| **HITL_before_fix** | No |

---

## GAP-009 — Commandant's Gauntlet: Promotion Pipeline Not Confirmed
| Field | Value |
|---|---|
| **gap_id** | GAP-009 |
| **req_ids** | REQ-020 |
| **severity** | P1-HIGH |
| **category** | Shadow evaluation / learning / promotion |
| **description** | `promotion_token.py` and `promotion_authority.py` exist. Shadow replay integration exists. `pipeline_d_learning.py` exists. However, the Commandant's Gauntlet — specifically (a) shadow replay of proposed changes, (b) regression test run on promoted rules, (c) SME sign-off gate, (d) sovereign approve/veto before ledger commit — is not confirmed as an enforced code path. The Master Ledger Commit via UWG (the "sole ink path") is referenced but the eight-step pipeline as an enforced sequence is unconfirmed. |
| **evidence** | `L2_execution/types/promotion_token.py`; `L4_state/enforcement/promotion_authority.py`; `L6_observability/utils/evaluation/shadow_replay_integration.py` — components exist; no `commandant_gauntlet.py` found |
| **risk_if_unaddressed** | Learning promotions may bypass shadow replay validation or SME review, pushing untested rule changes to production rubrics; sovereign veto path absent means unsafe promotions reach UWG |
| **recommended_resolution** | HITL decision required (HITL-005): confirm whether Commandant's Gauntlet should be a synchronous gate or async approval queue; then create `L6_observability/enforcement/commandant_gauntlet.py`. |
| **blast_radius** | L6_observability/enforcement, L4_state/enforcement, UWG commit path, learning pipeline |
| **confidence_that_gap_is_real** | 0.80 |
| **HITL_before_fix** | YES — HITL-005 |

---

## GAP-010 — Pre-Routing ACL Gate: Layer Placement and Sequence Unconfirmed
| Field | Value |
|---|---|
| **gap_id** | GAP-010 |
| **req_ids** | REQ-005, REQ-023 |
| **severity** | P1-HIGH |
| **category** | L0 routing / route switching + Security |
| **description** | `PreRetrievalGate` exists in `knowledge/gates/` with ACL and scope filtering. However, its placement in `knowledge/` rather than `L0_routing/enforcement/` raises a design concern: whether the gate fires BEFORE cache lookup (at route time) or only at vector search time. The architecture mandates pre-FILTER-before-cache, meaning the ACL check must precede even the semantic cache lookup in R1B. Cross-tenant chunk isolation at pre-search time is unconfirmed. |
| **evidence** | `knowledge/gates/preretrieval_gate.py` — ACL/scope gate exists; `knowledge/gates/scope_metadata_resolver.py`; no evidence of call from `L0_routing/enforcement/` before cache check |
| **risk_if_unaddressed** | Stale or cross-tenant items may appear in semantic cache hits (R1B) if ACL check fires after cache; this is a P0 security concern during cache-hit paths |
| **recommended_resolution** | Confirm that `PreRetrievalGate` is invoked from `L0_routing/enforcement/` before R1A/R1B cache access, not only before vector search. If not, add a gate invocation at the routing layer. |
| **blast_radius** | L0_routing/enforcement, knowledge/gates, semantic cache (R1B path) |
| **confidence_that_gap_is_real** | 0.82 |
| **HITL_before_fix** | No |

---

## GAP-011 — Freeze Signal Propagation: L0→L3→L5→L2 Replay Freeze Chain Unconfirmed
| Field | Value |
|---|---|
| **gap_id** | GAP-011 |
| **req_ids** | REQ-017 |
| **severity** | P1-HIGH |
| **category** | Replay / determinism / integrity |
| **description** | Replay guard components exist at L0 and in mixins. Determinism digest emitter exists at L6. `adg/runtime/determinism_control.py` and `adg/runtime/sandbox_airlock.py` exist. However, the Freeze signal propagation chain (L0 builds replay_envelope → emits Freeze → L3 relays → L5 enforces → L2 executes under guard) as a confirmed sequential protocol is unconfirmed. Whether all four non-deterministic surfaces (wall clock, raw random, uuid4, live network) are intercepted in ALL execution paths (not just the primary tool path) is unconfirmed. |
| **evidence** | `L0_routing/enforcement/deterministic_replay_guard.py`; `L2_execution/utils/replay_guard.py`; `mixins/replay_guard_mixin.py` — guards exist; `adg/runtime/determinism_control.py`; `L6_observability/utils/engines/determinism_digest_emitter.py`; but freeze propagation chain through L3, L5 is unconfirmed |
| **risk_if_unaddressed** | Execution paths that bypass the replay mixin (e.g., code paths not using the mixin, direct model calls) produce non-replayable output; determinism_digest may not reflect actual execution non-determinism |
| **recommended_resolution** | Document and confirm the Freeze signal propagation chain as a `DETERMINISM_SURFACE_MAP`; audit all tool/model call sites for replay_guard_mixin application; add static enforcement gate in CI that rejects non-guarded tool calls. |
| **blast_radius** | L0, L3, L5, L2 (all execution paths), CI gate |
| **confidence_that_gap_is_real** | 0.80 |
| **HITL_before_fix** | No |

---

## GAP-012 — Ingestion Lifecycle: Tombstone + Lineage Preservation Pipeline Unconfirmed
| Field | Value |
|---|---|
| **gap_id** | GAP-012 |
| **req_ids** | REQ-026 |
| **severity** | P2-MEDIUM |
| **category** | Intake / ingestion pipeline |
| **description** | `knowledge/lifecycle/` directory exists (4 items per listing) but module internals were not read. The dedupe → version compare → tombstone → lineage → reindex trigger sequence is unconfirmed as an enforced pipeline. Graph lineage preservation post-tombstone is particularly high risk if absent. |
| **evidence** | `knowledge/lifecycle/` — exists with 4 items; contents not confirmed |
| **risk_if_unaddressed** | Duplicate chunks degrade retrieval; stale chunks without tombstoning pollute evidence; graph lineage broken = parent-child hydration fails |
| **recommended_resolution** | Read and confirm `knowledge/lifecycle/` modules; if tombstone+lineage enforcement is missing, add `lifecycle_sync_enforcer.py`. |
| **blast_radius** | knowledge/lifecycle, knowledge/chunking, L4 retrieval surfaces |
| **confidence_that_gap_is_real** | 0.75 |
| **HITL_before_fix** | No |

---

## GAP-013 — Proof of Ledger: No Formal Five-Field Sealed Artifact
| Field | Value |
|---|---|
| **gap_id** | GAP-013 |
| **req_ids** | REQ-024 |
| **severity** | P1-HIGH |
| **category** | Testing / auditability / traceability / evidence |
| **description** | Genealogy registry, mission historian, audit trail mixin, and ledger retention config exist. However, the formal five-field Proof of Ledger artifact (catalog_digest, staff_roster_hash, desk_tools_hash, night_shift_protocol_hash, knowledge_state_digest with four sub-hashes) as a single sealed verifiable output per commit is not confirmed. Without it, external audit of state integrity is impossible. |
| **evidence** | `L4_state/enforcement/genealogy_registry.py`; `L4_state/enforcement/mission_historian.py`; `mixins/audit_trail_mixin.py`; `L4_state/config/ledger_retention_config.py` — individual components; no `proof_of_ledger.py` found |
| **risk_if_unaddressed** | State mutations not provably reconstructable from audit record; compliance audit fails; replay of historical state not possible |
| **recommended_resolution** | Create `L4_state/enforcement/proof_of_ledger.py` producing the formal five-field artifact; wire to UWG post-commit; include in every commit receipt. |
| **blast_radius** | L4_state/enforcement, UWG commit path, audit trail |
| **confidence_that_gap_is_real** | 0.82 |
| **HITL_before_fix** | No |

---

## GAP-014 — Metadata Binding: Six Required Chunk Fields Not Confirmed as Mandatory
| Field | Value |
|---|---|
| **gap_id** | GAP-014 |
| **req_ids** | REQ-022 |
| **severity** | P1-HIGH |
| **category** | Security / ACL / tenancy / freshness / scope |
| **description** | `ContentMetadata` type exists in `knowledge/ingestion/modality_types.py`. However, whether all six required fields (ACL, tenant_id, confidentiality_tier, freshness_band, effective_date, expiry_date, embedding_schema_version) are present as mandatory non-nullable fields is unconfirmed. If any are optional, ingestion may produce chunks without proper security labels, allowing retrieval contamination. |
| **evidence** | `knowledge/ingestion/modality_types.py` — `ContentMetadata` type exists; field completeness not confirmed |
| **risk_if_unaddressed** | Chunks without tenant_id or confidentiality_tier may cross tenant boundaries at retrieval; chunks without expiry_date cannot be freshness-filtered |
| **recommended_resolution** | Audit `ContentMetadata` fields; add all six as non-nullable required fields; add ingestion validation gate that rejects any chunk missing these fields. |
| **blast_radius** | knowledge/ingestion/modality_types, ingestion pipeline, pre-retrieval gate |
| **confidence_that_gap_is_real** | 0.80 |
| **HITL_before_fix** | No |

---

## GAP-015 — Index Eval Feedback Loop: Metrics Not Wired to Reindex Trigger
| Field | Value |
|---|---|
| **gap_id** | GAP-015 |
| **req_ids** | REQ-019 |
| **severity** | P2-MEDIUM |
| **category** | Observability / telemetry / anomaly signals |
| **description** | Retrieval quality metrics (NDCG, MRR, Recall@K, precision@K) exist as evaluation utilities in `utils/workflow_engines/`. However, an automated feedback loop that closes these metrics back to the ingestion pipeline as reindex_trigger signals is not confirmed. Metrics appear to be used in evaluation runners, not piped back to ingestion. |
| **evidence** | `utils/workflow_engines/ndcg.py`; `utils/workflow_engines/mrr.py`; `utils/workflow_engines/recall_at_k.py`; `evaluation/retrieval/`; but no `knowledge/lifecycle/index_eval_feedback.py` found |
| **risk_if_unaddressed** | Retrieval quality degrades silently without triggering chunking tuning or reindex; drift in embedding quality undetected |
| **recommended_resolution** | Create `knowledge/lifecycle/index_eval_feedback.py` consuming retrieval metrics and emitting reindex_trigger, chunking_tuning_signal, dense_sparse_balance_update. |
| **blast_radius** | knowledge/lifecycle, knowledge/chunking, knowledge/embeddings |
| **confidence_that_gap_is_real** | 0.78 |
| **HITL_before_fix** | No |

---

## GAP-016 — Runtime Handoff Readiness: No Five-Surface Pre-Flight Check
| Field | Value |
|---|---|
| **gap_id** | GAP-016 |
| **req_ids** | REQ-027 |
| **severity** | P2-MEDIUM |
| **category** | Intake / ingestion pipeline |
| **description** | Individual storage surfaces exist (BM25 sparse store, parent-child hydrator, static_index directory, retrieval utils). However, a runtime handoff readiness check — a gate that verifies all five surfaces (raw_text_vector, contextual_text_vector, sparse keyword, canonical raw, parent-child lineage) are warm before any inference request is accepted — is not confirmed. |
| **evidence** | `L4_state/utils/memory/bm25_store.py`; `knowledge/retrieval/parent_child_hydrator.py`; `knowledge/static_index/`; retrieval config; no `runtime_handoff_readiness_check.py` found |
| **risk_if_unaddressed** | Runtime inference begins with incomplete retrieval surfaces; dense recall falls back to empty results silently |
| **recommended_resolution** | Create `knowledge/lifecycle/runtime_handoff_readiness_check.py` performing a five-surface health check; block inference until all surfaces pass; integrate into startup sequence. |
| **blast_radius** | knowledge/lifecycle, startup sequence, L0 routing |
| **confidence_that_gap_is_real** | 0.75 |
| **HITL_before_fix** | No |

---

## Gap Summary by Severity

| Severity | Count | Gap IDs |
|---|---|---|
| **P0-CRITICAL** | 3 | GAP-001, GAP-004, GAP-005 |
| **P1-HIGH** | 9 | GAP-002, GAP-003, GAP-006, GAP-007, GAP-008, GAP-009, GAP-010, GAP-011, GAP-013, GAP-014 |
| **P2-MEDIUM** | 3 | GAP-012, GAP-015, GAP-016 |
| **P3-LOW** | 0 | — |

*Total: 15 gaps identified across 28 requirements. 2 of 28 requirements (REQ-009, REQ-011) have no material gap — implemented with coverage.*
