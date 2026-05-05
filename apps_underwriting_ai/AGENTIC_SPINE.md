# apps_underwriting_ai Agentic Spine

> **PUBLIC DEMO NOTICE**
> This app uses synthetic applicants, synthetic documents, fake policy thresholds, and
> fixture-based underwriting examples. It demonstrates governed agentic workflow design,
> deterministic scoring, evidence-bound reasoning, auditability, safe LLM use, and runtime
> control. It is **not** a production credit decisioning system and does not make real lending
> decisions.

---

## Route Decision Matrix

| Demo Request Type | Route Family | Route Mode | What It Shows |
|---|---|---|---|
| Full underwriting demo | `R3R4_MANAGED_WORKFLOW` | `FULL_DECISION_PACKET` | End-to-end governed agentic workflow with C0 evidence, L3 five-stage expansion, scored verdict, rationale enrichment, Exit fail-closed |
| Evidence-only document review | `R3_SIMPLE_GROUNDED_READ` | `EVIDENCE_ONLY_REVIEW` | C0 SUBMITTED_DOCUMENT_EVIDENCE_ONLY contracting without verdict assembly |
| Schema / demo utility | `R4_SINGLE_ACTION` | `ADMIN_OR_SCHEMA_UTILITY` | Bounded non-underwriting action (fixture reset, schema introspection) |
| Exact replay of same fixture | `R1A_EXACT_CACHE` | `EXACT_REPLAY` | Deterministic replay via SHA-256 cache key; no LLM re-execution |
| Similar prior demo | `R1B_SEMANTIC_CACHE` | `DOC_HELP_ONLY` | Semantic cache lookup for doc-help only; no decision reuse |
| Missing fixture documents | `R5_FALLBACK` | `MISSING_INPUT_SAFE_FALLBACK` | Safe abstain; missing-input handling; `INSUFFICIENT_EVIDENCE` disposition |
| Borderline synthetic case | `R3R4_MANAGED_WORKFLOW` + HITL posture | `BORDERLINE_HITL_POSTURE` | Human-review freeze and re-clearance pattern |

---

## ASCII Route View

```
USER (CLI: python -m apps_underwriting_ai --product-class <cls> --applicant-id <id> ...)
 │
 v
U0 INTAKE
 │  Raw input capture, arg parse, document list validation
 │  Build UnderwritingRequest (request_id, applicant_id, product_class, documents)
 │
 v
L0 ROUTE DECISION  [UnderwritingRouteSelector]
 │
 ├── R1A Exact Cache? ──hit──► [RET] sealed artifact ref → Exit X3D_ALLOW_FINISH
 │     (SHA-256 of: request envelope + document hashes + policy_hash + blueprint_hash)
 │
 ├── R1B Semantic Cache? ──hit──► [RET] doc-help chunks only → Exit X3D_ALLOW_FINISH
 │     (DOC_HELP_ONLY — no verdict reuse)
 │
 ├── R5 Missing Documents? ──fail──► SAFE_FALLBACK packet → Exit X3E_SAFE_ABSTAIN_CLARIFY
 │     (completeness_score < threshold OR required doc class absent)
 │
 ├── R4 Schema / Utility ──────────────────────────────────────┐
 │     (demo_mode=schema_utility, bounded non-UW action)        │
 │                                                              │
 └── R3R4_MANAGED_WORKFLOW ─────────────────────────────────────┴──────────────────────┐
       (primary path for all underwriting decisions)                                    │
                                                                                        │
C0 EVIDENCE PASS  [UnderwritingC0Adapter]                                               │
 │  Mode: SUBMITTED_DOCUMENT_EVIDENCE_ONLY                                              │
 │  Sources: synthetic submitted docs, fixture policy refs (by hash)                    │
 │  Blocked: open web, semantic-neighbor verdict reuse                                  │
 │  Output: FinalEvidenceContract                                                       │
 │    ├── document_coverage_map                                                         │
 │    ├── extracted_span_map                                                            │
 │    ├── contradiction_flags[]                                                         │
 │    ├── missing_evidence_flags[]                                                      │
 │    ├── support_score                                                                 │
 │    └── c0_state: PASS | WEAK_WITH_CAVEATS | FAIL                                    │
 │                                                                                      │
 v                                                                                      │
L3 WORKFLOW EXPANSION  [UnderwritingL3WorkflowAdapter]                                  │
 │  L3 EXPANDS — it does not execute. Declares five-stage DAG.                         │
 │                                                                                      │
 ├── Stage 1  EvidenceRegisterEngine      → L2.E1.underwriting_execution_context_bound  │
 ├── Stage 2  DocumentReconciliationEngine→ L2.E2.underwriting_evidence_validated       │
 ├── Stage 3  FeatureDerivationEngine     → L2.E3.underwriting_stage_executed           │
 ├── Stage 4  RiskEvidenceScoringEngine   → L2.E3.underwriting_stage_executed           │
 └── Stage 5  DecisionPacketAssembler     → L2.E5.underwriting_artifact_sealed          │
                                                                                        │
 v                                                                                      │
L2 BOUNDED EXECUTION  [L2 Step Adapters — one per stage]                               │
 │                                                                                      │
 ├── E1 PREP (Stage 1)                                                                  │
 │   • Bind execution context (request_id, applicant_id, product_class, run_dir)        │
 │   • Initialize EvidenceRegister from submitted documents + C0 FinalEvidenceContract  │
 │   • Create replay_key, idempotency_key, artifact manifest shell                     │
 │   • Bind demo_policy_hash, blueprint_hash, route_contract                           │
 │   Emit: L2.E1.underwriting_execution_context_bound                                  │
 │                                                                                      │
 ├── E2 VALID (Stage 2)                                                                 │
 │   • Reconcile submitted documents vs EvidenceRegister                                │
 │   • Flag missing document classes                                                    │
 │   • Flag contradictions between extracted spans                                      │
 │   • Validate schema and completeness score                                           │
 │   Emit: L2.E2.underwriting_evidence_validated                                        │
 │                                                                                      │
 ├── E3 EXEC Stage 3 — Feature Derivation                                               │
 │   • Derive RiskFeatures from reconciled evidence (LTV, DTI, FICO proxy, etc.)       │
 │   • All derivations deterministic — no LLM                                           │
 │   Emit: L2.E3.underwriting_stage_executed                                            │
 │                                                                                      │
 ├── E3 EXEC Stage 4 — Risk Scoring  [DeterministicRiskScorer]                         │
 │   • Score five risk dimensions from RiskFeatures                                     │
 │   • DeterministicRiskScorer owns: verdict, reason_code_bundle — immutable            │
 │   • LLM rationale lane owns: plain-English explanation only                          │
 │   • LLM cannot: change verdict, add/remove reason codes, invent evidence             │
 │   Emit: L2.E3.underwriting_stage_executed                                            │
 │                                                                                      │
 └── E5 SEAL (Stage 5)                                                                  │
     • Assemble DecisionPacketCandidate from scored dimensions + rationale              │
     • Apply PublicTrustReceipt fields                                                  │
     • Seal artifact — no further mutation                                              │
     Emit: L2.E5.underwriting_artifact_sealed                                           │
                                                                                        │
 v                                                                                      │
PA COMPILER  [underwriting_pa_compiler — W4]                                            │
 │  Compile CompiledPromptArtifact from C0 FinalEvidenceContract + template BOM        │
 │  Required slots: S0 I0 C0 U0 D0 R0  Optional: E0 Y0 P0                             │
 │  LLM rationale firewall: verdict + reason codes locked before any LLM call          │
 │                                                                                      │
 v                                                                                      │
EXIT v6  [UnderwritingExitFecProducer — W5]                                             │
 │  Mode: FAIL_CLOSED                                                                   │
 │  Fail-closed triggers: missing FEC, missing policy_hash, missing blueprint_hash,    │
 │    missing route_contract, verdict lacks reason codes, contradiction flags           │
 │    unresolved, judge UNKNOWN, LLM rationale changed verdict/reason codes             │
 │  Emit: exactly one X3 disposition                                                    │
 │                                                                                      │
 v                                                                                      │
L6 OBSERVABILITY (post-run only — cannot mutate)                                       │
                                                                                        │
 v                                                                                      │
UWG DURABLE WRITE (UWG_ONLY — no direct L4)                                            │
```

---

## Route Contract Declaration

```yaml
route_family: R3R4_MANAGED_WORKFLOW
route_id: apps_underwriting_ai.decision_packet_v1
execution_form: MANAGED_WORKFLOW
l3_required: true
c0_required: true
c0_mode: SUBMITTED_DOCUMENT_EVIDENCE_ONLY
pa_required: rationale_enrichment_enabled
semantic_cache_for_decision: false
exit_mode: FAIL_CLOSED
durable_write_path: UWG_ONLY
data_mode: SYNTHETIC_DEMO_ONLY
selected_capability: apps_underwriting_ai.decision_packet_v1
```

---

## UnderwritingRouteSelector Inputs / Outputs

**Inputs:**
- `product_class` — loan/policy product (e.g., `MORTGAGE_DEMO`, `AUTO_LOAN_DEMO`)
- `applicant_type` — `INDIVIDUAL` | `JOINT` | `ENTITY`
- `submitted_document_profile` — list of submitted document class IDs
- `completeness_score` — float 0.0–1.0 from document presence check
- `contradiction_score` — float 0.0–1.0 from cross-field validation
- `risk_tier_band` — `LOW` | `MEDIUM` | `HIGH` | `BORDERLINE`
- `demo_mode` — `full_decision` | `evidence_only` | `schema_utility` | `replay` | `doc_help`
- `demo_policy_profile` — policy fixture ID
- `human_review_threshold_ref` — HITL threshold override reference

**Outputs:**
- `canonical_route_family` — the resolved `R*` route family string
- `underwriting_route_mode` — one of 7 route modes (see matrix above)
- `route_reason_codes` — list of strings explaining the routing decision
- `required_evidence_standard` — `FULL` | `PARTIAL` | `NONE`
- `hitl_posture` — `NONE` | `SOFT_POSTURE` | `HARD_FREEZE`
- `cache_policy` — `NO_CACHE` | `ALLOW_EXACT` | `ALLOW_SEMANTIC_DOC_HELP_ONLY`
- `c0_mode` — `SUBMITTED_DOCUMENT_EVIDENCE_ONLY` | `NONE`
- `pa_required` — `rationale_enrichment_enabled` | `none`
- `l3_required` — `true` | `false`
- `exit_mode` — `FAIL_CLOSED` | `SOFT`

---

## HITL Trigger Map

| Condition | HITL Posture |
|---|---|
| Borderline synthetic score band (`risk_tier_band=BORDERLINE`) | `SOFT_POSTURE` |
| Contradiction score > demo threshold (0.30) | `SOFT_POSTURE` |
| Required document class missing but partial evidence present | `SOFT_POSTURE` |
| Adverse decision + weak rationale support score (< 0.5) | `HARD_FREEZE` |
| Demo policy overlay requires review flag | `HARD_FREEZE` |
| LLM rationale judge disagreement with deterministic verdict | `HARD_FREEZE` |
| Identity / tenant / provenance gap detected | `HARD_FREEZE` |
| Unsupported feature class considered by scorer | `HARD_FREEZE` |
| Exit judge UNKNOWN or low confidence | `HARD_FREEZE` |

---

## Capability Scorecard

| Spine Capability | Status | Wave |
|---|---|---|
| Entrypoint pure shim (`__main__.py`) | ✅ Done | W1 |
| Capability registry (`decision_packet_v1`) | ✅ Done | P0.2 |
| Route selector (`UnderwritingRouteSelector`) | ✅ Done | P1.2 |
| C0 evidence adapter (SUBMITTED_DOCUMENT_EVIDENCE_ONLY) | ✅ Done | W2 |
| Prompt Assembly BOM + compiler | ✅ Done | P1.5 / W4 |
| LLM rationale firewall (verdict + reason codes immutable) | ✅ Done | W4 |
| L3 five-stage workflow adapter | ✅ Done | W3 |
| L2 step adapters (E1–E5) | ✅ Done | W3 |
| Exit v6 fail-closed (X3A–X3E) | ✅ Done | W5 |
| FEC producer (PublicTrustReceipt, schema 1.1) | ✅ Done | W5 |
| UWG-only durable write path | ✅ Done | W5 |
| `spine_manifest.yaml` route correction | ✅ Done | W3.3 |
| 4 synthetic demo packets | ✅ Done | W6 |
| Public demo docs (full AGENTIC_SPINE.md) | ✅ Done | W6.1 |

---

## Synthetic Demo Packets

Four fixture packets under `apps_underwriting_ai/fixtures/`:

| File | Verdict | Scenario |
|---|---|---|
| `demo_approve_packet.yaml` | `APPROVE` | Complete docs, strong cash flow, low contradiction → X3A |
| `demo_missing_evidence_packet.yaml` | `INSUFFICIENT_EVIDENCE` | Missing bank statement → X3D or X3E SAFE_ABSTAIN |
| `demo_refer_packet.yaml` | `REFER` | Adequate docs, borderline ratio band → X3B HITL posture |
| `demo_decline_packet.yaml` | `DECLINE` | Conflicting revenue signals, high contradiction → X3C |

---

## Acceptance Criteria (W6 — YES gate)

- [x] Direct full decision path uses `R3R4_MANAGED_WORKFLOW`
- [x] Full decision route requires L3 (`l3_required=true`)
- [x] Full decision route requires C0 (`c0_required=true`, `c0_mode=SUBMITTED_DOCUMENT_EVIDENCE_ONLY`)
- [x] `__main__.py` is pure shim (no engine imports, no closures, no legacy runner)
- [x] `agentic_core` owns route/capability resolution
- [x] L0 cache checks (R1A, R1B, R5) precede managed workflow
- [x] R1B semantic cache cannot emit verdicts
- [x] C0 emits `FinalEvidenceContract` and blocks open web
- [x] PA is BOM-bound; all templates registry-defined; `CompiledPromptArtifact` emitted
- [x] No ad hoc prompt strings in active generation/repair paths
- [x] L3 expands five-stage workflow and does not execute
- [x] L2 E1–E5 used for bounded stage execution
- [x] `DeterministicRiskScorer` owns verdict and reason codes; LLM cannot change them
- [x] Deterministic rationale fallback exists and is wired
- [x] FEC carries `PublicTrustReceipt`, evidence coverage, feature refs, reason_code_bundle
- [x] Exit emits exactly one X3; fails closed on UNKNOWN or missing FEC
- [x] L6 is after-runtime only; cannot mutate current output
- [x] UWG is the only durable write path
- [x] Public docs state synthetic demo only; demo packets present
- [x] 67 governance tests pass (target ≥ 65)

---

## Primary Structural Defect (Current → Target)

| Field | Current (WRONG) | Target (CORRECT) |
|---|---|---|
| `route_family` | `R3_SIMPLE_GROUNDED_READ` | `R3R4_MANAGED_WORKFLOW` |
| `execution_form` | `SINGLE_STEP` | `MANAGED_WORKFLOW` |
| `l3_required` | `false` | `true` |
| `c0_required` | `false` / implicit | `true` |
| `c0_mode` | unset | `SUBMITTED_DOCUMENT_EVIDENCE_ONLY` |
| `pa_required` | unset | `rationale_enrichment_enabled` |
| `exit_mode` | unset | `FAIL_CLOSED` |
| `durable_write_path` | unset | `UWG_ONLY` |
| `data_mode` | unset | `SYNTHETIC_DEMO_ONLY` |

Plan: `apps-underwriting-ai-spine-hardening-d7f3b2` P1.1.
