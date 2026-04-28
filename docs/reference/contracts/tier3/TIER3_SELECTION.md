# Tier 3 Selection — 25 REQ_IDs

**Caveat:** Selection only. This document does not claim proof, coverage, or readiness. The Tier 3 enforcement gate is expected to be BLOCKED on first generation until on-disk references and validators are wired in subsequent prompts.

**Excluded:** Tier 0 (17), Tier 1 (15), Tier 2 (22). Total Tier 0-2 protected: 54. Remaining Step 1 rows: 96.

## Selected rows (priority rank 1-25)

| Rank | REQ_ID | Layer | Strength | Risk Category | Why Tier 3 |
|---:|---|---|---|---|---|
| 1 | `REQ-L6-OBS-ANTI-BYPASS-001` | L6 | MUST_NOT | `observability_integrity` | L6 firewall anti-bypass not yet covered by Tier 0-2; structurally identical to L4/UWG/Gate anti-bypass rows already protected. |
| 2 | `REQ-C0-NO-WRITE-001` | C0 | MUST_NOT | `write_sovereignty` | C0 retrieval boundary forbids durable writes; complements L1/L2 NO-RETRIEVAL/NO-EXECUTE pair already in Tier 2. |
| 3 | `REQ-L0-NO-EXECUTE-001` | L0 | MUST_NOT | `execution_safety` | L0 execution boundary; complements L0-NO-RETRIEVAL-001 already in Tier 2 to fully bound L0 authority. |
| 4 | `REQ-L0-GROUNDED-ACTION-HANDOFF-001` | L0 | MUST | `orchestration_integrity` | L0 to L3/L2 grounded/action handoff is the canonical post-route contract; no Tier 0-2 row covers this. |
| 5 | `REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001` | UWG | MUST | `audit_traceability` | UWG audit/replay consistency invariant; complements UWG-OBS-ANTI-BYPASS already in Tier 1. |
| 6 | `REQ-GATE-G01-G05-INGRESS-001` | RuntimeGates | MUST | `gate_integrity` | Ingress gate band (identity/intent/safety) not yet covered by Tier 0-2; structurally critical for U0 boundary. |
| 7 | `REQ-GATE-G06-G10-HITL-ROUTE-001` | RuntimeGates | MUST | `gate_integrity` | HITL/route/retrieval/evidence gate band; complements L5-HITL-RECLEARANCE in Tier 2. |
| 8 | `REQ-GATE-G11-G15-TOOL-MODEL-001` | RuntimeGates | MUST | `gate_integrity` | Tool/model/args/egress/sandbox gate band; complements L2-PTC-SANDBOX in Tier 2. |
| 9 | `REQ-GATE-G16-G20-MEMORY-WORKFLOW-001` | RuntimeGates | MUST | `gate_integrity` | Memory/privacy/workflow gate band; no Tier 0-2 row covers this surface. |
| 10 | `REQ-GATE-G21-G24-OUTPUT-REPLAY-001` | RuntimeGates | MUST | `gate_integrity` | Output/security/replay gate band; complements EXIT-NO-OVERLAP and L4-REPLAY-SNAPSHOT-AUDIT. |
| 11 | `REQ-GATE-G25-G29-EXIT-WRITE-001` | RuntimeGates | MUST | `gate_integrity` | Anomaly/exit/write/audit gate band; spans EXIT and UWG admission boundaries. |
| 12 | `REQ-GATE-NO-OVERLAP-WITH-EXIT-001` | RuntimeGates | MUST_NOT | `gate_integrity` | Runtime gates vs Exit decision authority no-overlap invariant; mirrors EXIT-NO-OVERLAP-RUNTIME-GATES (Tier 2) from the gate side. |
| 13 | `REQ-GATE-NO-OVERLAP-WITH-L5-001` | RuntimeGates | MUST_NOT | `gate_integrity` | Runtime gates vs L5 governance no-overlap invariant; closes the runtime/governance authority partition. |
| 14 | `REQ-L5-REPLAY-AUDIT-CERT-001` | L5 | MUST | `audit_traceability` | L5 governance certification emitted as replayable audit; complements L5-STATIC-GOV-DRIFT in Tier 1. |
| 15 | `REQ-U0-OBS-REPLAY-001` | U0 | MUST | `observability_integrity` | Intake observability/replay evidence; complements U0-VALIDATED-REQUEST-HANDOFF and U0-ANTI-BYPASS in Tier 2. |
| 16 | `REQ-L1-OBS-OTEL-001` | L1 | MUST | `observability_integrity` | L1 OTEL spans for intent framing/refinement/plan emission; mandatory for L1PlanContract traceability. |
| 17 | `REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001` | L1 | MUST | `planning_integrity` | L1 plan validation/self-repair before L1PlanContract handoff; gates the contract already covered by Tier 2. |
| 18 | `REQ-L1-AMBIGUITY-EVIDENCE-001` | L1 | MUST | `planning_integrity` | Ambiguity register carried into L1PlanContract; downstream gates depend on this evidence. |
| 19 | `REQ-U0-CHANNEL-VALIDATION-001` | U0 | MUST | `intake_integrity` | Channel-level intake validation; complements U0-VALIDATED-REQUEST-HANDOFF and U0-ANTI-BYPASS in Tier 2. |
| 20 | `REQ-EXIT-X1A-X1F-CHECKS-001` | Exit | MUST | `output_disposition` | Exit X1A-X1F current-run checkout checks before X3 disposition; complements EXIT-X3-ONE-DISPOSITION in Tier 0. |
| 21 | `REQ-PA-VALIDATE-SLOT-CONTRACT-001` | PA | MUST | `prompt_boundary` | PA slot-contract validation before token-budget step; complements PA-AIRLOCK-SECURITY (Tier 2) and PA-ASSEMBLY-NO-RETRIEVAL/EXECUTE (Tier 0). |
| 22 | `REQ-L5-EGRESS-PROVIDER-GOV-001` | L5 | MUST | `policy_integrity` | Egress provider governance certification; complements L5-RISK-TIER-BANDS in Tier 2 from the provider side. |
| 23 | `REQ-E2E-FIXTURES-REPLAY-HARNESS-001` | E2E | ONLY | `replay_integrity` | E2E fixtures/replay harness sole-entry invariant; complements EXIT-X1G-X1I-REPLAY in Tier 1. |
| 24 | `REQ-C0-PREFLIGHT-GROUNDING-001` | C0 | MUST | `retrieval_boundary` | C0 grounding eligibility preflight; gates whether C0 retrieval-fetch (Tier 2) is reachable at all. |
| 25 | `REQ-C0-GRAPH-RAG-001` | C0 | MUST | `retrieval_boundary` | C0 graph-RAG bounded-traversal invariant; complements C0-EVIDENCE-FETCH in Tier 2. |

## Selection priority basis

1. RELEASE_BLOCKING rows from remaining Step 1 set.
2. MUST / MUST_NOT / NEVER / ONLY / REQUIRED strength rows.
3. Runtime evidence obligations (OTEL, replay, audit).
4. Cross-layer handoff obligations.
5. Auditability / traceability obligations.
6. Schema and artifact integrity obligations.
7. Coverage of enforcement blind spots (gate bands G01-G29, anti-bypass siblings of Tier 0-2 rows, partition invariants).

## Risk category distribution

| Risk Category | Count |
|---|---:|
| `gate_integrity` | 8 |
| `observability_integrity` | 3 |
| `audit_traceability` | 2 |
| `planning_integrity` | 2 |
| `retrieval_boundary` | 2 |
| `execution_safety` | 1 |
| `intake_integrity` | 1 |
| `orchestration_integrity` | 1 |
| `output_disposition` | 1 |
| `policy_integrity` | 1 |
| `prompt_boundary` | 1 |
| `replay_integrity` | 1 |
| `write_sovereignty` | 1 |
