# apps_rg Retrieval Metrics Ownership — Implementation Receipt

**Plan:** `apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan`
**Receipt timestamp:** 2026-05-14
**Author:** Cascade (closure proof run)

---

## Wave PASS/FAIL Status

| Wave | Title | Status | Test Count |
|---|---|---|---|
| W0 | Baseline evidence audit | ✅ PASS | read-only survey |
| W1 | apps_rg retrieval profile | ✅ PASS | 41 tests |
| W2 | C0 metrics extraction + enum alignment | ✅ PASS | 60 tests |
| W3 | Durable c0_metrics.json artifact writer | ✅ PASS | 52 tests |
| W4 | apps_rg scoring/Exit consumption | ✅ PASS | 72 tests |
| W5 | Briefing path proof | ✅ PASS | 66 tests |
| W6 | Governance + anti-contamination tests | ✅ PASS | 82 tests (62 governance + 20 shadow-spine) |

**Total W1–W6 suite: 287 passed, 0 failed (run 2026-05-14)**

---

## Closure Proof Commands and Results

```
# W1–W6 acceptance suite
pytest tests/_apps_contract/test_rg_w1_retrieval_requirements_profile.py \
       tests/_apps_contract/test_rg_w2_c0_metrics_extractor.py \
       tests/_apps_contract/test_rg_w3_c0_metrics_artifact.py \
       tests/_apps_contract/test_rg_w4_exit_binding.py \
       tests/_apps_contract/test_rg_w5_briefing_path_proof.py \
       tests/_apps_contract/test_rg_retrieval_metrics_governance.py \
       -v --timeout=60
Result: 287 passed, 3 warnings in 1.27s  ✅

# Shadow-spine regression
pytest tests/unit/ops_scripts/ci/test_check_no_shadow_spine.py -v --timeout=60
Result: 20 passed  ✅

# Shadow-spine gate (direct)
python ops_scripts/ci/check_no_shadow_spine.py
Result: exit 0  ✅
```

---

## Evidence Artifacts Created / Modified

### New files
| File | Purpose |
|---|---|
| `apps_rg/config/domain_contract/retrieval_requirements_profile.resume_generation.v1.yaml` | W1 — apps_rg-owned retrieval requirements profile |
| `apps_rg/runtime/profiles/retrieval_requirements.py` | W1 — profile loader with `load_retrieval_requirements_profile` (lru_cache) |
| `apps_rg/runtime/bindings/c0_metrics_writer.py` | W3 — per-run `c0_metrics.json` artifact builder + writer |
| `apps_rg/runtime/bindings/c0_minimum_safety.py` | W3 — `_PASSING_SUPPORT_STATUSES` gate (no PARTIAL) |
| `apps_rg/runtime/bindings/briefing_mode_classifier.py` | W5 — four-mode classifier with `BriefingModeDecision` |
| `apps_rg/runtime/schemas/c0_metrics.schema.json` | W3 — JSON schema for c0_metrics artifact |
| `tests/_fixtures/c0_metrics_example.json` | W3 — committed fixture for schema validation |
| `tests/_apps_contract/test_rg_w1_retrieval_requirements_profile.py` | W1 tests (41) |
| `tests/_apps_contract/test_rg_w2_c0_metrics_extractor.py` | W2 tests |
| `tests/_apps_contract/test_rg_w3_c0_metrics_artifact.py` | W3 tests |
| `tests/_apps_contract/test_rg_w4_exit_binding.py` | W4 tests |
| `tests/_apps_contract/test_rg_w5_briefing_path_proof.py` | W5 tests (66) |
| `tests/_apps_contract/test_rg_retrieval_metrics_governance.py` | W6 tests (62) |
| `tests/unit/ops_scripts/ci/test_check_no_shadow_spine.py` | W6 shadow-spine regression (20) |
| `ops_scripts/ci/check_no_shadow_spine.py` | W6 gate — exits 0 (no shadow spine violations) |

### Modified files
| File | Change |
|---|---|
| `apps_rg/runtime/bindings/c0_binding.py` | Added `APPS_RG_C0_CERT_REF`, `_NORMATIVE_SOURCE_CLASSES`, `_NORMATIVE_SOURCE_CLASSES_HARDCODED`, `C0EvidenceGapError` |
| `apps_rg/runtime/bindings/exit_binding.py` | W4 — reads `support_status`; blocks on `_BLOCKING_SUPPORT_STATUSES` (UNKNOWN/EMPTY/BLOCKED/CONFLICTED) |
| `agentic_core/runtime/c0/evidence_metrics_extractor.py` | W2 — generic extractor (zero apps_rg imports) |
| `agentic_core/runtime/contracts/final_evidence_contract.py` | W2 — PARTIAL removed from PASSING_VALUES; canonical 6-value enum enforced |

---

## c0_metrics.json Schema

**Schema path:** `apps_rg/runtime/schemas/c0_metrics.schema.json`
**Schema version constant:** `"c0_metrics.v1"`
**Committed fixture:** `tests/_fixtures/c0_metrics_example.json`

### Metrics now serialized per run

| Field | Source | Notes |
|---|---|---|
| `schema_version` | constant `"c0_metrics.v1"` | |
| `run_id` | caller | |
| `route_id` | caller | |
| `retrieval_mode` | briefing classifier | one of 4 canonical modes or UNKNOWN |
| `briefing_source_type` | briefing classifier | |
| `company_brief_provenance` | briefing classifier | dict or null |
| `source_class_coverage` | profile × FEC | per normative class boolean |
| `support_status` | FEC (coerced) | PARTIAL→UNKNOWN; canonical 6-value |
| `support_target_met` | FEC | bool |
| `evidence_counts` | FEC | {total, excluded, blocked} |
| `retrieval_sources` | FEC | list of source strings |
| `excluded_evidence_refs` | FEC | |
| `blocked_source_refs` | FEC | |
| `freshness_receipts` | FEC | |
| `citation_map` | FEC | list of [source, anchor] pairs |
| `support_score_profile` | extractor | per-class scores |
| `final_evidence_digest` | SHA-256 | empty→`e3b0c44...` sentinel |
| `coercion_warnings` | writer | PARTIAL coercions logged |

---

## Ownership Split Proof

| Concern | Owner | Enforcement |
|---|---|---|
| `required_source_classes` | apps_rg profile YAML | W1 loader test: `get_normative_source_classes()` derives from YAML |
| Generic C0 metric computation | `agentic_core/runtime/c0/` | W6 AST scan: zero `apps_rg.*` imports in extractor |
| `c0_metrics.json` serialization | `apps_rg/runtime/bindings/c0_metrics_writer.py` | W3 writer test; W6 confirms writer NOT in agentic_core |
| Briefing mode classification | `apps_rg/runtime/bindings/briefing_mode_classifier.py` | W5 tests; 4 canonical modes |
| Exit `support_status` gating | `apps_rg/runtime/bindings/exit_binding.py` | W4 blocking-status tests |
| Shadow-spine absence | `ops_scripts/ci/check_no_shadow_spine.py` | W6 gate exits 0 |

---

## Known Residual Gaps (non-blocking, explicitly deferred)

| Gap | Decision | Plan section |
|---|---|---|
| Deep native apps_rg company research retrieval | **Deferred** — out of scope per Hard Rule 6 | §14 Non-Goals |
| `pool_first_hit_rate` (legacy narrative metric) | **Deferred** — legacy path only | §14 Non-Goals |
| Real LLM overfit scoring (beyond threshold config) | **Deferred** — threshold profile sufficient | §13 Verification vs Deferral |
| Per-evidence-item ACL verification receipts | **Deferred** — infrastructure gap | §13 Verification vs Deferral |
| G09 freshness warn evaluation at Exit runtime | **Deferred** — gate declared, not connected | W0 gap register |
| G13 citation_map hard-fail connection at Exit | **Deferred** — gate declared, not connected | W0 gap register |
| 17 shadow-spine warnings in apps_qna | **Deferred** — apps_qna-only, non-blocking | W6 §gate output |

All gaps are non-blocking. None prevent the DoD criteria from being met.

---

## Final DoD Verification

| DoD Row | Criterion | Result |
|---|---|---|
| DoD-1 | apps_rg retrieval profile declares required_source_classes, support_target, briefing taxonomy | ✅ PASS — 41 W1 tests |
| DoD-2 | c0_metrics.json written per run with stable schema | ✅ PASS — schema + fixture + writer tests |
| DoD-3 | PARTIAL eliminated; canonical 6-value enum enforced | ✅ PASS — coercion + enum gate tests |
| DoD-4 | apps_rg Exit reads support_status/citation_map/freshness_receipts; G09/G13 gated | ✅ PASS — W4 exit binding tests |
| DoD-5 | No apps_rg literals in agentic_core C0 or contracts | ✅ PASS — W6 AST import scan |
| DoD-6 | Four briefing modes produce distinct retrieval_mode in artifact | ✅ PASS — W5 parametrized mode tests |
| DoD-7 | Final receipt file produced | ✅ PASS — this file |
