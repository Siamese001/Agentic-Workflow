---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-underwriting-ai-spine-hardening-d7f3b2.md'
original_relative_path: '_archive\\2026-05\\apps-underwriting-ai-spine-hardening-d7f3b2.md'
source_sha256: 9b5e9dcf352460be26c4f2d4ae680758e4b158b2a75108d53bb921165731084c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-underwriting-ai-spine-hardening-d7f3b2
plan_type: refactor
status: Completed
completed: 2026-05-05
---

# apps_underwriting_ai — Zero-Loss Spine Hardening & Public Demo Alignment

Refactor `apps_underwriting_ai` from a standalone imperative underwriting runner into a canonical agentic_core-spine-aligned, public-facing synthetic underwriting demo using `R3R4_MANAGED_WORKFLOW`, governed Prompt Assembly, C0 submitted-document evidence, L3 five-stage workflow, Exit fail-closed, and UWG-only durable writes.

---

## Context (SCQA)

- **Situation** — `apps_underwriting_ai` is a deterministic 5-stage synthetic underwriting simulator. It has a working `DeterministicRiskScorer`, `EvidenceRegister`, `ReconciliationResult`, `RiskFeatures`, and `DecisionPacketAssembler`. The FEC producer is wired (plan `apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9`). The eval harness is active (plan `apps-eval-harness-deferred-e4a1b7`). The app is a portfolio-grade public demo of governed agentic workflow design.
- **Complication** — The current `spine_manifest.yaml` and candidate AGENTIC_SPINE documentation label the production path as `R3_SIMPLE_GROUNDED_READ` with `execution_form=SINGLE_STEP`, `l3_required=false`, and `grounding_required=false`. This is a material routing contradiction: a 5-stage dependent workflow with staged evidence, deterministic scoring, checkpoint needs, and HITL posture triggers cannot be `SIMPLE_GROUNDED_READ`. `__main__.py` directly instantiates underwriting engines, calls the pipeline imperatively, and constructs `l2_callable`-equivalent closures — all off-spine. No governed Prompt Assembly BOM exists. No `UnderwritingRouteSelector` exists. No `R3R4_MANAGED_WORKFLOW` route contract is declared.
- **Question** — How do we refactor `apps_underwriting_ai` so that its full decision path uses `R3R4_MANAGED_WORKFLOW`, its entrypoint is a pure shim, its Prompt Assembly is BOM-bound, its C0 runs in `SUBMITTED_DOCUMENT_EVIDENCE_ONLY` mode, its L3 expands a five-stage workflow, its Exit is fail-closed, and its public documentation is portfolio-ready synthetic-demo-framed?
- **Answer** — Execute six waves: (P0) entrypoint purity + capability registry, (P1) routing matrix + `UnderwritingRouteSelector`, (P1.5) Prompt Assembly BOM + real template bodies, (W1–W6) C0 → L3 → L2 → Exit/FEC/UWG → public docs + fixtures + acceptance sweep.

---

## Public Demo Notice

> **PUBLIC DEMO NOTICE**
> This app uses synthetic applicants, synthetic documents, fake policy thresholds, and fixture-based underwriting examples. It is designed to demonstrate governed agentic workflow design, deterministic scoring, evidence-bound reasoning, auditability, safe LLM use, and runtime control. It is **not** a production credit decisioning system and does not make real lending decisions.

---

## Primary Structural Defect

| Field | Current (WRONG) | Target (CORRECT) |
|---|---|---|
| `route_family` | `R3_SIMPLE_GROUNDED_READ` | `R3R4_MANAGED_WORKFLOW` |
| `execution_form` | `SINGLE_STEP` | `MANAGED_WORKFLOW` |
| `l3_required` | `false` | `true` |
| `c0_required` | `false` / implicit | `true` |
| `c0_mode` | unset | `SUBMITTED_DOCUMENT_EVIDENCE_ONLY` |
| `pa_required` | unset | `rationale_enrichment_enabled` |
| `grounding_required` | `false` | implicit via C0 |
| `exit_mode` | unset | `FAIL_CLOSED` |
| `durable_write_path` | unset | `UWG_ONLY` |
| `data_mode` | unset | `SYNTHETIC_DEMO_ONLY` |

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_underwriting_ai/__main__.py` | Entrypoint purity baseline | 🔲 |
| `apps_underwriting_ai/spine_manifest.yaml` | Route contradiction evidence | 🔲 |
| `apps_underwriting_ai/engines/*.py` | Engine import boundary check | 🔲 |
| `apps_underwriting_ai/cert/fec_producer.py` | FEC producer baseline | 🔲 |
| `apps_underwriting_ai/types/underwriting_types.py` | Contract types baseline | 🔲 |
| `agentic_core/L0_routing/` | Canonical route/capability resolution | 🔲 |
| `agentic_core/L3_orchestration/` | L3 workflow executor baseline | 🔲 |
| `apps_shared/cert/exit_eval_hook.py` | Exit hook adoption pattern | 🔲 |
| Prior plan `apps-qna-c0-fec-producer-wiring-d4f1e8` | FEC producer pattern | 🔲 |
| Prior plan `apps-eval-harness-deferred-e4a1b7` | Eval harness wiring | 🔲 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| P0 | P0.1–P0.5 | Entrypoint purity + capability/recipe registry | ~18k | Existing engine code untouched; new integration scaffolds only | ✅ DONE | 20 governance tests pass; `__main__.py` imports no engines/C0/PA/L2/providers; capability registry exports present |
| P1 | P1.1–P1.3 | Routing matrix + `UnderwritingRouteSelector` | ~10k | No new canonical route families; selector is metadata only | ✅ DONE | Route decision matrix documented; selector outputs correct `route_family` for 7 demo request types; 10 routing tests pass |
| P1.5 | P1.5.1–P1.5.4 | Prompt Assembly BOM + real template bodies | ~20k | `CompiledPromptArtifact` contract exists in `agentic_core`; templates are YAML | ✅ DONE | `prompt_bom.yaml`, `prompt_registry.yaml`, 5 template YAMLs, `underwriting_pa_compiler.py` created; 17 PA tests pass; zero placeholder text |
| W1 | W1.1–W1.3 | `__main__.py` pure shim + core-owned route/recipe resolution | ~12k | `agentic_core` runner API exists or stub is created | ✅ DONE | `__main__.py` is CLI arg parser + runner call only; capability resolution through `agentic_core`; R5 fail-closed on unavailable capability |
| W2 | W2.1–W2.3 | C0 submitted-document evidence contract implementation | ~14k | C0 adapter pattern exists in `agentic_core.L0_routing.c0_retrieval` | ✅ DONE | `underwriting_c0_adapter.py` complete; `FinalEvidenceContract` emitted; PASS/WEAK/FAIL modes implemented; open-web blocked; 5 C0 tests pass |
| W3 | W3.1–W3.5 | L3 managed workflow + L2 E1–E5 stage execution | ~22k | `HopPipelineExecutor` and `L2` E-stage lifecycle exist | ✅ DONE | `underwriting_l3_workflow_adapter.py` expands 5 stages; L2 E1–E5 receipts emitted; `underwriting_l2_step_adapters.py` complete; 8 L3/L2 tests pass |
| W4 | W4.1–W4.2 | PA + rationale firewall + L2 compiled prompt path | ~10k | `underwriting_pa_compiler.py` from P1.5 complete | ✅ DONE | PA compiler consumes C0 FEC → `CompiledPromptArtifact`; LLM cannot change verdict/reason codes; deterministic fallback wired; 6 LLM firewall tests pass |
| W5 | W5.1–W5.4 | FEC + Exit v6 + L6/UWG proof | ~12k | Exit v6 and UWG interfaces exist | ✅ DONE | FEC producer carries `PublicTrustReceipt`, route_family, evidence coverage, reason_code_bundle; Exit emits exactly one X3; L6 post-run only; UWG-only write path; 10 Exit/state tests pass |
| W6 | W6.1–W6.4 | Public demo docs, fixtures, acceptance sweep, legacy quarantine | ~14k | Synthetic fixture data acceptable; no real applicant data | ✅ DONE | 4 synthetic demo packets; `PublicTrustReceipt` schema; capability scorecard; ASCII route views; DEMO NOTICE in docs; legacy runner quarantined; 65-test acceptance sweep passes |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|--------------|-------------|-------------|--------|
| P0.1 | Governance test scaffolds | `tests/governance/test_apps_underwriting_ai_entrypoint_purity.py` +4 new test files | No existing governance tests for entrypoint purity | ~5k | ✅ |
| P0.2 | Capability registry | `apps_underwriting_ai/integrations/underwriting_capability_registry.py` | Must mirror `agentic_core` capability resolution protocol | ~4k | ✅ |
| P0.3 | Integration scaffold stubs | `underwriting_l2_step_adapters.py`, `underwriting_c0_adapter.py`, `underwriting_l3_workflow_adapter.py`, `underwriting_exit_fec_producer.py` | Stub only — full impl in W2/W3/W4/W5 | ~4k | ✅ |
| P0.4 | 20 governance tests | All 20 P0 required tests | Tests must be hard (import inspection + AST boundary) | ~5k | ✅ |
| P1.1 | Route decision matrix doc | `apps_underwriting_ai/AGENTIC_SPINE.md` (route matrix section) | Must not invent new canonical route families | ~3k | ✅ |
| P1.2 | `UnderwritingRouteSelector` | `apps_underwriting_ai/integrations/` or L0 route declarations | Selector is metadata only — L0 retains authority | ~4k | ✅ |
| P1.3 | Routing tests | 10 routing tests in `tests/governance/` | Route selector must not become a new runtime layer | ~3k | ✅ |
| P1.5.1 | `prompt_bom.yaml` | `apps_underwriting_ai/prompt_assembly/prompt_bom.yaml` | Must match exact slot schema from spec | ~3k | ✅ |
| P1.5.2 | `prompt_registry.yaml` + `underwriting_pa_compiler.py` | `apps_underwriting_ai/prompt_assembly/` | Compiler must emit `CompiledPromptArtifact` with all hash fields | ~6k | ✅ |
| P1.5.3 | 5 template YAML bodies | `apps_underwriting_ai/prompt_assembly/templates/*.yaml` | All templates must have real implementation-grade content — zero placeholders | ~7k | ✅ |
| P1.5.4 | PA tests (17) | `tests/governance/` PA test cases 21–37 | Hash binding + no-retrieve + no-call-provider invariants | ~4k | ✅ |
| W1.1 | `__main__.py` rewrite | `apps_underwriting_ai/__main__.py` | Must delete all engine imports, closures, legacy runner references | ~4k | ✅ |
| W1.2 | Core runner integration | `apps_underwriting_ai/integrations/underwriting_capability_registry.py` (finalize) | Fail-closed on missing capability → R5 terminal packet | ~4k | ✅ |
| W1.3 | Entrypoint purity tests | Tests 1–11 (entrypoint group) | AST/import inspection boundary | ~4k | ✅ |
| W2.1 | C0 adapter | `apps_underwriting_ai/integrations/underwriting_c0_adapter.py` | `SUBMITTED_DOCUMENT_EVIDENCE_ONLY` mode; block open-web; PASS/WEAK/FAIL | ~6k | ✅ |
| W2.2 | `FinalEvidenceContract` emission | C0 adapter output contract | Must carry evidence_ids, coverage_map, contradiction_flags, support_score | ~4k | ✅ |
| W2.3 | C0 tests (5) | Tests 11–15 (C0 group) | Verify open-web blocked; FEC emitted; evidence IDs preserved | ~4k | ✅ |
| W3.1 | L3 workflow adapter | `apps_underwriting_ai/integrations/underwriting_l3_workflow_adapter.py` | Expand → do not execute; 5 stage contracts declared | ~6k | ✅ |
| W3.2 | L2 step adapters (5 stages) | `apps_underwriting_ai/integrations/underwriting_l2_step_adapters.py` | E1–E5 receipts; no new retrieval; no L4 write | ~8k | ✅ |
| W3.3 | `spine_manifest.yaml` update | `apps_underwriting_ai/spine_manifest.yaml` | Change route to `R3R4_MANAGED_WORKFLOW`; update entry_points | ~2k | ✅ |
| W3.4 | L3/L2 tests (8) | Tests 44–49 (L3/L2 group) | L3 expands not executes; feature derivation requires evidence_refs | ~6k | ✅ |
| W4.1 | LLM firewall wiring | `apps_underwriting_ai/engines/decision_packet_assembler.py` + PA compiler integration | PA compiler must precede any provider call; fallback deterministic | ~5k | ✅ |
| W4.2 | LLM firewall tests (6) | Tests 38–43 (LLM firewall group) | Verdict immutability + reason_code immutability + fallback | ~5k | ✅ |
| W5.1 | FEC producer extension | `apps_underwriting_ai/cert/fec_producer.py` | Add `PublicTrustReceipt`, `route_family`, `reason_code_bundle`, evidence coverage | ~4k | ✅ |
| W5.2 | Exit v6 integration | `apps_underwriting_ai/integrations/underwriting_exit_fec_producer.py` | Fail-closed on missing FEC/policy_hash/blueprint_hash | ~4k | ✅ |
| W5.3 | L6/UWG proof | Docs + test assertions | L6 post-run only; UWG-only write; no direct L4 | ~2k | ✅ |
| W5.4 | Exit/state tests (10) | Tests 50–59 (Exit + state group) | UNKNOWN never passes; exactly one X3; L6 cannot mutate | ~4k | ✅ |
| W6.1 | `AGENTIC_SPINE.md` full doc | `apps_underwriting_ai/AGENTIC_SPINE.md` | Route matrix, ASCII views, scorecard, demo notice, HITL trigger map | ~6k | ✅ |
| W6.2 | Synthetic demo packets (4) | `apps_underwriting_ai/fixtures/` or `docs/` | Approve/Missing/Refer/Decline; clearly synthetic | ~4k | ✅ |
| W6.3 | `PublicTrustReceipt` schema | `apps_underwriting_ai/types/underwriting_types.py` + docs | All required fields per spec | ~2k | ✅ |
| W6.4 | Acceptance sweep + legacy quarantine | All 65 tests; legacy runner removal/quarantine | Full acceptance report; YES/NO verdict | ~6k | ✅ |

---

## Target Production Demo Route

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

## Route Decision Matrix

| Demo Request Type | Route Family | What It Shows |
|---|---|---|
| Full underwriting demo | `R3R4_MANAGED_WORKFLOW` | End-to-end governed agentic workflow |
| Evidence-only document review | `R3_SIMPLE_GROUNDED_READ` | C0 evidence contracting without verdict |
| Schema/demo utility | `R4_SINGLE_ACTION` | Bounded non-underwriting action |
| Exact replay of same fixture | `R1A_EXACT_CACHE` | Deterministic replay and strict cache discipline |
| Similar prior demo | `R1B_SEMANTIC_CACHE` | Semantic doc-help only, no decision reuse |
| Missing fixture docs | `R5_FALLBACK` | Safe abstain / missing-input handling |
| Borderline synthetic case | `R3R4_MANAGED_WORKFLOW` + `HITL_POSTURE` | Human-review freeze and re-clearance pattern |

---

## UnderwritingRouteSelector Inputs/Outputs

**Inputs:** `product_class`, `applicant_type`, `submitted_document_profile`, `completeness_score`, `contradiction_score`, `risk_tier_band`, `demo_mode`, `demo_policy_profile`, `human_review_threshold_ref`

**Outputs:** `canonical_route_family`, `underwriting_route_mode`, `route_reason_codes[]`, `required_evidence_standard`, `hitl_posture`, `cache_policy`, `c0_mode`, `pa_required`, `l3_required`, `exit_mode`

**Route modes:** `FULL_DECISION_PACKET` | `EVIDENCE_ONLY_REVIEW` | `MISSING_INPUT_SAFE_FALLBACK` | `EXACT_REPLAY` | `DOC_HELP_ONLY` | `BORDERLINE_HITL_POSTURE` | `ADMIN_OR_SCHEMA_UTILITY`

---

## Prompt Assembly BOM Summary

**Required slots:** S0 (system_and_governance), I0 (underwriting_rationale_rules), C0 (verified_evidence_context), U0 (user_underwriting_request), D0 (origin_and_injection_fences), R0 (output_schema_and_constraints)

**Optional slots:** E0 (approved_examples), Y0 (approved_style_preferences), P0 (demo_policy_profile)

**Templates to create:**
1. `decision_rationale_enrichment_v1.yaml` — E3 exec; SyntheticUnderwritingRationale output
2. `evidence_to_rationale_context_v1.yaml` — E2 validate; RationalePromptContext output
3. `unsupported_reason_omission_v1.yaml` — E4 heal; UnsupportedReasonRepair output
4. `rationale_caveat_and_confidence_repair_v1.yaml` — E4 heal; RationaleCaveatConfidenceRepair output
5. `rationale_length_and_structure_repair_v1.yaml` — E4 heal; RationaleStructureRepair output

All templates must contain real implementation-grade prompt content. Zero placeholders. Zero TODOs.

---

## Five-Stage Workflow (L3 Expansion)

| Stage | Engine | L2 Receipt | Output |
|---|---|---|---|
| Stage 1 | `EvidenceRegisterEngine` | `L2.E1.underwriting_execution_context_bound` | `EvidenceRegister` |
| Stage 2 | `DocumentReconciliationEngine` | `L2.E2.underwriting_evidence_validated` | `ReconciliationResult` |
| Stage 3 | `FeatureDerivationEngine` | `L2.E3.underwriting_stage_executed` | `RiskFeatures` |
| Stage 4 | `RiskEvidenceScoringEngine` | `L2.E3.underwriting_stage_executed` | `RiskDimensionScores` |
| Stage 5 | `DecisionPacketAssembler` | `L2.E5.underwriting_artifact_sealed` | `DecisionPacketCandidate` |

---

## LLM Rationale Firewall

- `DeterministicRiskScorer` **owns**: feature vector, risk score, threshold application, verdict, `reason_code_bundle` — immutable
- LLM rationale lane **owns only**: plain-English explanation, formatting, summarization of already-approved reason codes
- LLM **must not**: change verdict, add/remove reason codes, invent evidence, cite unsupported spans
- Failure path: deterministic rationale fallback → `deterministic_rationale_fallback_used = true` → continue to Exit

---

## C0 Contract

- Mode: `SUBMITTED_DOCUMENT_EVIDENCE_ONLY`
- Allowed sources: synthetic submitted docs, extracted field spans, fixture docs, approved demo policy table refs by hash
- Blocked sources: open web, broad internet enrichment, semantic-neighbor packets for verdict reuse
- Outputs: `FinalEvidenceContract`, `document_coverage_map`, `extracted_span_map`, `contradiction_flags`, `missing_evidence_flags`, `support_score`, `evidence_sufficiency`
- C0 states: `PASS` | `WEAK_WITH_CAVEATS` | `FAIL/DEGRADE`

---

## Exit Fail-Closed Triggers

Exit must fail closed or escalate when: FinalEvidenceContract missing, `demo_policy_hash` missing, `blueprint_hash` missing, `route_contract` missing, `replay_key` missing, `terminal_class` missing, unsupported feature in decision, verdict lacks reason codes, rationale unsupported by evidence refs, judge result UNKNOWN, contradiction flags unresolved, output schema invalid, LLM rationale changed verdict or reason codes, semantic cache attempted to emit a verdict, direct L4 write attempted.

---

## PublicTrustReceipt Fields

`route_family`, `underwriting_route_mode`, `evidence_contract_status`, `documents_received_count`, `documents_missing_count`, `contradiction_flags_count`, `demo_scorer_version`, `demo_policy_hash`, `replay_key_prefix`, `exit_disposition`, `hitl_posture`, `generated_rationale_used`, `deterministic_rationale_fallback_used`, `demo_packet_id`, `demo_mode`

---

## HITL Trigger Map

HITL posture triggered when: borderline synthetic score band, contradiction score above demo threshold, required document missing but partial evidence exists, adverse decision with weak rationale support, demo policy overlay requires review, model rationale judge disagreement, identity/tenant/provenance gap, unsupported feature considered by scorer, Exit judge UNKNOWN or low confidence.

---

## Synthetic Demo Packets (W6)

1. **Clean Approve** — complete docs, strong synthetic cash flow, low contradiction → `APPROVE`
2. **Missing Evidence** — missing bank statement → `SAFE_FALLBACK` or `INSUFFICIENT_EVIDENCE`
3. **Borderline Refer** — adequate docs, borderline ratio band → `HITL_POSTURE` or `REFER`
4. **Contradiction Decline** — conflicting revenue signals, high contradiction → `DECLINE` or `REFER`

---

## Capability Scorecard (W6)

| Capability Demonstrated | Where It Shows Up |
|---|---|
| Deterministic decisioning | `DeterministicRiskScorer` |
| Evidence-bound reasoning | C0 `FinalEvidenceContract` |
| Safe LLM use | Rationale-only PA/L2 lane |
| Agentic orchestration | L3 five-stage workflow |
| Governed runtime | Runtime Gates + Exit X3 |
| Auditability | `trace_root` / `replay_key` / receipts |
| Learning boundary | L6 post-run only |
| State sovereignty | UWG-only durable writes |
| Replay discipline | Exact cache hash gates |
| Human review posture | HITL trigger map |

---

## Required New Files

```
tests/governance/test_apps_underwriting_ai_entrypoint_purity.py
tests/governance/test_apps_underwriting_ai_recipe_resolution.py
tests/governance/test_apps_underwriting_ai_no_legacy_runner.py
tests/governance/test_apps_underwriting_ai_provider_boundary.py
tests/governance/test_apps_underwriting_ai_l4_write_boundary.py
apps_underwriting_ai/integrations/underwriting_capability_registry.py
apps_underwriting_ai/integrations/underwriting_l2_step_adapters.py
apps_underwriting_ai/integrations/underwriting_c0_adapter.py
apps_underwriting_ai/integrations/underwriting_l3_workflow_adapter.py
apps_underwriting_ai/integrations/underwriting_exit_fec_producer.py
apps_underwriting_ai/prompt_assembly/prompt_bom.yaml
apps_underwriting_ai/config/prompt_registry.yaml
apps_underwriting_ai/prompt_assembly/underwriting_pa_compiler.py
apps_underwriting_ai/prompt_assembly/templates/decision_rationale_enrichment_v1.yaml
apps_underwriting_ai/prompt_assembly/templates/evidence_to_rationale_context_v1.yaml
apps_underwriting_ai/prompt_assembly/templates/unsupported_reason_omission_v1.yaml
apps_underwriting_ai/prompt_assembly/templates/rationale_caveat_and_confidence_repair_v1.yaml
apps_underwriting_ai/prompt_assembly/templates/rationale_length_and_structure_repair_v1.yaml
apps_underwriting_ai/AGENTIC_SPINE.md
apps_underwriting_ai/fixtures/demo_approve_packet.yaml
apps_underwriting_ai/fixtures/demo_missing_evidence_packet.yaml
apps_underwriting_ai/fixtures/demo_refer_packet.yaml
apps_underwriting_ai/fixtures/demo_decline_packet.yaml
```

## Required Modified Files

```
apps_underwriting_ai/__main__.py          (pure shim rewrite)
apps_underwriting_ai/spine_manifest.yaml  (route contradiction fix)
apps_underwriting_ai/cert/fec_producer.py (+ PublicTrustReceipt + route_family + reason_code_bundle)
apps_underwriting_ai/types/underwriting_types.py (+ PublicTrustReceipt dataclass)
apps_underwriting_ai/engines/decision_packet_assembler.py (+ PA compiler integration + firewall)
```

---

## Acceptance Criteria (YES gate)

- [ ] Direct full decision path uses `R3R4_MANAGED_WORKFLOW`
- [ ] Full decision route requires L3 (`l3_required=true`)
- [ ] Full decision route requires C0 (`c0_required=true`, `c0_mode=SUBMITTED_DOCUMENT_EVIDENCE_ONLY`)
- [ ] `__main__.py` is pure shim (no engine imports, no closures, no legacy runner)
- [ ] `agentic_core` owns route/capability resolution
- [ ] L0 cache checks (R1A, R1B, R5) precede managed workflow
- [ ] R1B semantic cache cannot emit verdicts
- [ ] R1A exact cache requires strict snapshot/policy/scorer/schema hash matching
- [ ] C0 emits `FinalEvidenceContract` and blocks open web
- [ ] PA is BOM-bound; all templates are registry-defined with real content; `CompiledPromptArtifact` emitted
- [ ] No ad hoc prompt strings in active generation/repair paths
- [ ] L3 expands five-stage workflow and does not execute
- [ ] L2 E1–E5 used correctly for bounded stage execution
- [ ] `DeterministicRiskScorer` owns verdict and reason codes; LLM cannot change them
- [ ] Deterministic rationale fallback exists and is wired
- [ ] FEC carries `PublicTrustReceipt`, evidence coverage, feature refs, reason_code_bundle, rationale support status
- [ ] Exit emits exactly one X3; fails closed on UNKNOWN or missing FEC
- [ ] L6 is after-runtime only; cannot mutate current output
- [ ] UWG is the only durable write path
- [ ] Public docs state synthetic demo only; demo packets, route matrix, scorecard, ASCII views, PublicTrustReceipt present
- [ ] All 65 governance tests pass

---

## Non-Goals

- No renaming of canonical layers
- No new top-level route families
- No duplication of C0, PA, Exit, L6, L4, or UWG responsibilities inside `apps_underwriting_ai`
- No real applicant data, real lending thresholds, or production credit decisioning
- No broad unrelated refactors of other apps
- No changes to `agentic_core` core routing logic (only app-side adapters/declarations)

---

## Gap Register

| ID | Gap | Severity | Resolution Wave |
|---|---|---|---|
| G1 | `spine_manifest.yaml` declares `R3_SIMPLE_GROUNDED_READ` — routing contradiction | BLOCKER | W3.3 |
| G2 | `__main__.py` imports and instantiates underwriting engines directly | BLOCKER | W1.1 |
| G3 | No `UnderwritingRouteSelector` exists | HIGH | P1.2 |
| G4 | No Prompt Assembly BOM or template registry | HIGH | P1.5 |
| G5 | No `underwriting_c0_adapter.py` in `SUBMITTED_DOCUMENT_EVIDENCE_ONLY` mode | HIGH | W2.1 |
| G6 | No `underwriting_l3_workflow_adapter.py` expanding five stages | HIGH | W3.1 |
| G7 | FEC producer missing `PublicTrustReceipt`, `route_family`, `reason_code_bundle` | MEDIUM | W5.1 |
| G8 | No governance/entrypoint-purity test suite | MEDIUM | P0.4 |
| G9 | No public `AGENTIC_SPINE.md` with demo notice, route matrix, scorecard, ASCII views | MEDIUM | W6.1 |
| G10 | No synthetic demo fixture packets | LOW | W6.2 |
