---
plan_id: acceptance-gates-master-tracking-b5c3e1
plan_type: tracker    # tracker for AG status dashboard
dod_exempt: false
---

# Acceptance Gates (AG) Master Tracking Plan

Single plan tracking all Acceptance Gates (AG-1 through AG-6 completed, AG-7+ planned). Each wave represents a discrete acceptance proof for the apps_rg pipeline and related components.

---

## Context (SCQA)

- **Situation** — AG items (AG-1 through AG-6) have been implemented across multiple sessions but were not centrally tracked. Each AG represents a specific acceptance proof: contract definitions, embedding gap analysis, exit wiring, evidence contracts, evaluator wiring, and golden path runtime proof.

- **Complication** — Without a single tracking plan, AG status is scattered across artifacts and memories. Dependencies (like AG-7) reference AG-6 status but there's no single source of truth for which AG items are completed vs pending.

- **Question** — How do we create a single, queryable record of all Acceptance Gates with their status, artifacts, and dependencies?

- **Answer** — One master tracking plan with waves AG-1 through AG-6 marked complete, and future waves (AG-7+) defined for upcoming acceptance work.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `artifacts/apps_rg/ag*_acceptance_evidence.json` | AG completion artifacts | ✅ |
| `artifacts/apps_embedding_gap_analysis/` | AG-5 embedding analysis | ✅ |
| `tests/_apps_contract/test_ag*.py` | AG test files | ✅ |
| `ops_scripts/ci/check_apps_rg_*.py` | AG CI gates | ✅ |

---

## Wave Structure

| Wave | AG Item | Status | Focus | Key Artifacts |
|------|---------|--------|-------|---------------|
| Wave 1 | AG-1 | ✅ COMPLETE | Contract Definitions for apps_rg | `l1_plan_contract.py`, `final_evidence_contract.py`, `compiled_prompt_artifact.py` |
| Wave 2 | AG-2 | ✅ COMPLETE | Prompt Assembly with Evidence Slots | `apps_rg_pa_binding.py`, slot_lineage_map |
| Wave 3 | AG-3 | ✅ COMPLETE | C0 Evidence Integration | `apps_rg_c0_binding.py`, `FinalEvidenceContract` population |
| Wave 4 | AG-4 | ✅ COMPLETE | Final Evidence Contract Fields | 23/25 AG-4 fields populated, NOT_APPLICABLE with reasons |
| Wave 5 | AG-5 | ✅ COMPLETE | Exit X1 Evaluator Wiring | `x1_checkout_adapter.py`, `x1d_deterministic_evaluator.py`, `x1_gates.py` |
| Wave 6 | AG-6 | ✅ COMPLETE | Golden Path Runtime Proof | `test_ag6_apps_rg_golden_path.py`, 15 tests, CI gate |
| Wave 7 | AG-7 | 🟡 PLANNED | Template Extraction | Pending AG-6 acceptance |
| Wave 8 | AG-8+ | ⚪ FUTURE | (Reserved for future gates) | — |

---

## Phase-Level Summary

| Phase ID | Title | Scope | Status |
|----------|-------|-------|--------|
| P1 | AG-1 Contract Definitions | `L1PlanContract`, `FinalEvidenceContract`, `CompiledPromptArtifact` | ✅ Done |
| P2 | AG-2 Prompt Assembly Slots | `slot_lineage_map`, `component_hash_map`, evidence data-only | ✅ Done |
| P3 | AG-3 C0 Integration | `c0_retrieve_apps_rg()`, evidence population | ✅ Done |
| P4 | AG-4 Field Compliance | 23/25 AG-4 fields, NOT_APPLICABLE reasons | ✅ Done |
| P5 | AG-5 Exit X1 Wiring | X1CheckoutResult, X1D evaluator, X2 aggregate, X3 disposition | ✅ Done |
| P6 | AG-6 Golden Path Proof | E2E test, CI gate, 15 tests, no Chroma/embedding/bypass | ✅ Done |
| P7 | AG-7 Template Extraction | (Planned) Resume template extraction from generated outputs | 🟡 Not Started |
| P8 | AG-8+ | (Reserved) | Future acceptance gates | ⚪ Not Started |

---

## AG-6 Completion Evidence

**Test Results:**
```
15 passed, 3 warnings in 0.87s

TestAG6Preconditions::test_runtime_imports_available PASSED
TestAG6GoldenPathContractChain::test_w0_ingress_payload_is_valid PASSED
TestAG6GoldenPathContractChain::test_w1_u0_produces_validated_request PASSED
TestAG6GoldenPathContractChain::test_w2_l1_produces_plan_contract PASSED
TestAG6GoldenPathContractChain::test_w3_l0_produces_route_contract PASSED
TestAG6GoldenPathContractChain::test_w4_c0_produces_final_evidence_contract PASSED
TestAG6GoldenPathContractChain::test_w5_pa_consumes_evidence_as_data_only PASSED
TestAG6GoldenPathContractChain::test_w6_l2_preserves_evidence_refs PASSED
TestAG6GoldenPathContractChain::test_w7_exit_produces_x3_with_x1_checkout PASSED
TestAG6GoldenPathContractChain::test_w8_no_chromadb_imports_in_golden_path PASSED
TestAG6GoldenPathContractChain::test_w9_no_embedding_calls_in_golden_path PASSED
TestAG6X1ExitIntegration::test_x1_checkout_can_be_built_from_sealed_artifact PASSED
TestAG6X1ExitIntegration::test_x1d_groundedness_evaluates_fec_status PASSED
TestAG6NoBypass::test_c0_never_reads_envelope_payload PASSED
TestAG6NoBypass::test_pa_never_reads_legacy_payload PASSED
```

**CI Gate:**
```
✅ ALL 10 CHECKS PASSED
```

---

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| DoD-1 | All AG-1 through AG-6 artifacts documented | ✅ |
| DoD-2 | AG-6 tests pass (15/15) | ✅ |
| DoD-3 | CI gate passes (10/10) | ✅ |
| DoD-4 | Plan registered in Notion | 🟡 This plan |
| DoD-5 | AG-7+ future waves defined | ✅ |

---

## Files Referenced

| File | Purpose |
|------|---------|
| `tests/_apps_contract/test_ag6_apps_rg_golden_path.py` | AG-6 E2E tests |
| `ops_scripts/ci/check_apps_rg_golden_path_runtime.py` | AG-6 CI gate |
| `artifacts/apps_rg/ag6_acceptance_evidence.json` | AG-6 acceptance |
| `artifacts/apps_rg/ag6_contract_chain_receipt.json` | Contract chain |
| `artifacts/apps_rg/ag6_evidence_population_matrix.json` | Evidence fields |
| `artifacts/apps_rg/ag6_no_bypass_map.json` | Bypass prevention |
| `artifacts/apps_rg/ag6_apps_rg_golden_path_report.md` | Full report |
| `artifacts/apps_embedding_gap_analysis/ag5_acceptance_evidence.json` | AG-5 |

---

## Dependencies

- **Blocks:** AG-7 (Template Extraction) — waiting on AG-6 acceptance
- **Blocked by:** None — this is a tracking plan

---

PLAN_CREATED: slug=acceptance-gates-master-tracking-b5c3e1
