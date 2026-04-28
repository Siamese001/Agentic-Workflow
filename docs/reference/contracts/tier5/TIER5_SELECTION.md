# Tier 5 Selection

Selected count: **25**

Excluded: 17 Tier 0, 15 Tier 1, 22 Tier 2, 25 Tier 3, 25 Tier 4 (total 104 protected).

Status vocabulary: READY | BLOCKED | LINKED_LITERAL | LINKED_CONCEPTUAL | PARTIAL_LINK | NO_LINK.

## Selected REQ_IDs by priority rank

| Rank | REQ_ID | Owner | Risk Category | Why Tier 5 |
|---:|---|---|---|---|
| 1 | `REQ-L5-CAPABILITY-TOKEN-SCHEMA-001` | L5/L5_safety_governance | schema_integrity | Capability-token schema is the structural floor under L5 authority binding. Tier 0..4 cover binding-presence and registr |
| 2 | `REQ-L5-CROSS-CHILD-CERT-CONSISTENCY-001` | L5/L5_safety_governance | gate_integrity | Cross-child consistency is the parent/child invariant L4 cert-bind alone cannot detect. |
| 3 | `REQ-L5-CALIBRATION-ASSURANCE-001` | L5/L5_safety_governance | calibration_integrity | Calibration assurance is the L5 invariant that protects judge-derived decisions from drift. |
| 4 | `REQ-L4-BLUEPRINT-VERSION-MIGRATION-001` | L4/L4_state_uwg | migration_integrity | Migration determinism is the next-tier integrity invariant beyond Tier 4 blueprint-state read-only enforcement. |
| 5 | `REQ-L4-MEMORY-PROMOTION-STATE-001` | L4/L4_state_uwg | write_sovereignty | Memory promotion is a write-sovereignty surface not yet tier-protected. |
| 6 | `REQ-L4-READ-SURFACE-REFRESH-001` | L4/L4_state_uwg | cache_integrity | Read-surface refresh determinism guards retrieval consistency. |
| 7 | `REQ-U0-TRANSPORT-ENVELOPE-001` | U0/U0_intake | schema_integrity | Transport-envelope validation closes the schema gap upstream of identity/tenant/session sealing. |
| 8 | `REQ-U0-DATA-LABELING-001` | U0/U0_intake | origin_trust | Data labeling is the upstream provenance bedrock for any policy decision in L1..L5. |
| 9 | `REQ-U0-REJECTION-PATH-001` | U0/U0_intake | intake_integrity | Rejection-path determinism prevents silent admit-after-reject failures. |
| 10 | `REQ-L1-CONTEXTUAL-REFINEMENT-001` | L1/L1_cognition_plan | planning_integrity | Contextual-refinement drift is the planning-integrity invariant beyond Tier 4 intent-frame presence. |
| 11 | `REQ-L1-DRAFT-PLAN-ROUTE-HINTS-001` | L1/L1_cognition_plan | planning_integrity | Route-hint determinism protects L0 routing from prompt-engineered drift. |
| 12 | `REQ-L3-CONCURRENCY-FALLBACK-001` | L3/L3_orchestration | orchestration_integrity | Concurrency-fallback determinism is the orchestration safety floor. |
| 13 | `REQ-L3-STEP-READINESS-LEDGER-001` | L3/L3_orchestration | audit_traceability | Readiness-ledger immutability is the audit bedrock for L3 step handoff. |
| 14 | `REQ-C0-SHAPE-RERANK-STRATIFY-001` | C0/C0_context_engine | retrieval_boundary | Shape-rerank-stratify determinism guards retrieval ranking from drift. |
| 15 | `REQ-PA-SLOT-COMPOSITION-001` | PA/PA_prompt_assembly | prompt_boundary | Slot-composition determinism is the prompt-integrity invariant beyond Tier 4 BOM resolution. |
| 16 | `REQ-L2-E2-VALID-WORK-ORDER-001` | L2/L2_execution | schema_integrity | Work-order validation is the next L2 invariant beyond Tier 4 frozen-room sealing. |
| 17 | `REQ-L2-E3-EXEC-LANES-SANDBOX-001` | L2/L2_execution | sandbox_integrity | Lane-sandbox enforcement is the runtime isolation invariant. |
| 18 | `REQ-L2-E4-HEAL-SAME-AUTHORITY-001` | L2/L2_execution | authority_bypass | Heal-same-authority is the cross-cutting invariant between L2 healing and L5 authority binding. |
| 19 | `REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001` | L2/L2_execution | state_integrity | Resolution-context invariance closes the L2 state-integrity gap. |
| 20 | `REQ-EXIT-INPUT-NORMALIZATION-001` | Exit/Exit_runtime_control | schema_integrity | Exit-input normalization is the schema floor at the exit boundary. |
| 21 | `REQ-EXIT-GRADER-COMPOSITION-001` | Exit/Exit_runtime_control | evaluation_integrity | Grader-composition determinism is the exit-judgment integrity invariant. |
| 22 | `REQ-EXIT-RETURN-RESPONSE-001` | Exit/Exit_runtime_control | output_disposition | Return-response disposition tagging is the output-integrity invariant. |
| 23 | `REQ-L6-OUTCOME-TRAJECTORY-001` | L6/L6_observability | observability_integrity | Outcome-trajectory immutability is the L6 audit bedrock beyond Tier 4 exhaust ingest. |
| 24 | `REQ-L6-PROPOSAL-ADMISSION-001` | L6/L6_observability | learning_firewall | Proposal-admission policy enforcement guards the learning firewall. |
| 25 | `REQ-L6-MEMORY-PROMOTION-IFACE-001` | L6/L6_observability | learning_firewall | Memory-promotion interface enforcement closes the L6->L4 promotion-write surface. |
