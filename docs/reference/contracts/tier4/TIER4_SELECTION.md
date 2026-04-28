# Tier 4 Selection

Selected count: **25**

Excluded: 17 Tier 0, 15 Tier 1, 22 Tier 2, 25 Tier 3 (total 79 protected).

Status vocabulary: READY | BLOCKED | LINKED_LITERAL | LINKED_CONCEPTUAL | PARTIAL_LINK | NO_LINK.

## Selected REQ_IDs by priority rank

| Rank | REQ_ID | Owner | Risk Category | Why Tier 4 |
|---:|---|---|---|---|
| 1 | `REQ-L5-AUTHORITY-REGISTRY-BIND-001` | L5/L5_safety_governance | authority_bypass | Authority binding is the substrate every other governance gate sits on. Without a Tier 4 bind on the registry-binding st |
| 2 | `REQ-L5-RUNTIME-CERT-BIND-001` | L5/L5_safety_governance | gate_integrity | Runtime cert binding closes the loop between L5 governance and Exit. Tier 0..3 do not assert the cert is bound to the ru |
| 3 | `REQ-L5-GUARDRAIL-FAMILIES-001` | L5/L5_safety_governance | policy_integrity | Guardrail family coverage is policy-bedrock. Tier 0..3 assert L5 anti-bypass and cert presence but not family completene |
| 4 | `REQ-L5-GOV-CONTEXT-INVARIANT-001` | L5/L5_safety_governance | state_integrity | Governance-context drift is a silent-mutation class not yet tier-protected. |
| 5 | `REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001` | L4/L4_state_uwg | write_sovereignty | Tier 0 covers UWG sovereignty but not the per-write context-invariant. Authority drift across a write boundary is the re |
| 6 | `REQ-L4-POLICY-BLUEPRINT-STATE-001` | L4/L4_state_uwg | state_integrity | Policy blueprint mutation is a silent-policy-drift surface not covered by Tier 0..3. |
| 7 | `REQ-GATE-LAYER-INVOCATION-MAP-001` | RG/runtime_gates | gate_integrity | Coverage of the gate map itself is the Tier 4 audit closure for runtime gates. |
| 8 | `REQ-U0-IDENTITY-TENANT-SESSION-001` | U0/U0_intake | identity_quota_integrity | Identity/tenant/session is the upstream basis for every authority and quota check. Tier 3 covers channel validation only |
| 9 | `REQ-U0-QUOTA-BASELINE-001` | U0/U0_intake | identity_quota_integrity | Quota mutation is a downstream-cheating surface not yet tier-protected. |
| 10 | `REQ-U0-SCHEMA-NORMALIZATION-001` | U0/U0_intake | schema_integrity | Schema-drift at intake corrupts every downstream evidence claim. |
| 11 | `REQ-L1-INTENT-FRAME-001` | L1/L1_cognition_plan | planning_integrity | Tier 3 covers ambiguity evidence but not the intent frame itself. |
| 12 | `REQ-L1-PLANNING-PRIORS-001` | L1/L1_cognition_plan | planning_integrity | Prior-drift is a silent-policy class above the existing L1 plan-validation row. |
| 13 | `REQ-L0-ROUTE-INPUT-PREFLIGHT-001` | L0/L0_routing | intake_integrity | Preflight is the first runtime guard at L0; Tier 0..3 assert no-execute and grounded handoff but not preflight. |
| 14 | `REQ-L0-CACHE-FALLBACK-HITL-001` | L0/L0_routing | cache_integrity | Fallback paths are a known authority-bypass surface; Tier 4 closes the audit for cache/fallback/HITL. |
| 15 | `REQ-L0-ROUTECONTRACT-TELEMETRY-001` | L0/L0_routing | replay_integrity | Replay-integrity for L0 RouteContract is the audit bedrock for end-to-end route reproduction. |
| 16 | `REQ-L3-MANAGED-WORKFLOW-001` | L3/L3_orchestration | orchestration_integrity | L3 managed-workflow gating is not yet tier-protected. |
| 17 | `REQ-C0-RETRIEVAL-PLAN-001` | C0/C0_context_engine | retrieval_boundary | Retrieval-plan determinism is the upstream of Tier 3's graph-RAG bounds row. |
| 18 | `REQ-PA-LOAD-RESOLVE-BOM-001` | PA/PA_prompt_assembly | prompt_boundary | BOM determinism is the prompt-assembly bedrock; Tier 3 covers slot contract violation only. |
| 19 | `REQ-PA-TOKEN-BUDGET-DETERMINISM-001` | PA/PA_prompt_assembly | prompt_boundary | Token-budget drift is a silent prompt-mutation surface. |
| 20 | `REQ-L2-E1-FROZEN-ROOM-001` | L2/L2_execution | sandbox_integrity | Frozen-room seal is the tool-execution sandbox bedrock. |
| 21 | `REQ-L2-E5-SEAL-DISPATCH-001` | L2/L2_execution | artifact_integrity | Seal+dispatch atomicity prevents partial-write corruption. |
| 22 | `REQ-L2-SEQUENCER-CONTRACT-001` | L2/L2_execution | orchestration_integrity | Sequencer determinism is the L2 audit bedrock. |
| 23 | `REQ-EXIT-HITL-FREEZE-001` | Exit/Exit_runtime_control | output_disposition | HITL freeze is the human-in-loop kill switch; bypass is a release-blocking class. |
| 24 | `REQ-L6-RUNTIME-EXHAUST-INGEST-001` | L6/L6_observability | audit_traceability | Lossy exhaust-ingest defeats the runtime-to-regression flow. |
| 25 | `REQ-E2E-EVIDENCE-GROUNDEDNESS-001` | E2E/E2E_proof | proof_false_confidence | Groundedness proof is the end-to-end audit bedrock; Tier 3 covers replay-harness boundary only. |
