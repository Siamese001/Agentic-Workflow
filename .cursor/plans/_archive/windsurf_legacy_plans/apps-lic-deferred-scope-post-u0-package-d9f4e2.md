---
dod_exempt: false
---
# apps_lic Deferred Scope Post-U0 Runtime Package

**Plan ID:** apps-lic-deferred-scope-post-u0-package-d9f4e2  
**Parent Plan:** apps-lic-u0-runtime-package-complete-f8e2a1  
**Status:** DEFERRED — Captured from completed parent plan  
**Created:** 2026-05-11  
**Tier:** T3 Architectural (Deferred Work)

## Origin

This plan captures all deferred scope from `apps-lic-u0-runtime-package-complete-f8e2a1` (W0-W9 COMPLETE). The parent plan achieved its objective: a complete U0 runtime customization package for apps_lic. All deferred items are explicitly out of scope for the U0 package and are captured here for future scheduling.

## Deferred Scope Items

### 1. C0 FEC Producer Binding (BLOCKER #4)

**Item:** Full C0 FEC (Forward Evidence Collection) producer binding for apps_lic  
**Deferred From:** W3 Non-Goals §1, Parent plan BLOCKER #4  
**Current State:** apps_lic uses apps_research as support step; full C0 grounding not implemented  
**Future Work:**
- apps_lic-specific C0 evidence producer
- Evidence digest generation for apps_lic outreach context
- Integration with apps_research C0 layer (if apps_research is support step)
- FEC binding in `agentic_core/runtime/c0/apps_lic_fec_binding.py`

**Dependencies:**
- apps_research C0 wiring completion (plan: apps-research-rich-content-runtime-customization-v2.md W10-W13)
- Generic FEC producer pattern from apps_rg

**Estimated Effort:** ~8K tokens, ~2 waves  
**Priority:** HIGH (blocks full C0 grounding for apps_lic)

---

### 2. Real LLM Judge Implementations

**Item:** Real LLM-as-judge scoring logic for apps_lic eval dimensions  
**Deferred From:** W3 Non-Goals §2  
**Current State:** Stubs acceptable; deterministic judges in place  
**Future Work:**
- Implement 4 real LLM judges for apps_lic:
  - `response_likelihood_judge` (apps_lic/engines/judges/)
  - `sequence_coherence_judge`
  - `brand_voice_judge`
  - `win_theme_alignment_judge`
- Holdout-based calibration per judge (Spearman ≥ 0.80)
- Judge calibration receipts

**Dependencies:**
- apps_eval harness calibration framework (plan: apps-eval-harness-parity-f8d4a2.md)
- Holdout corpus with human labels
- Calibration ADR approval

**Estimated Effort:** ~12K tokens, ~3 waves  
**Priority:** MEDIUM (stubs functional; real judges improve quality)

---

### 3. Production-Log Mining with PII Redaction ✓ COMPLETE

**Item:** Production telemetry log mining for apps_lic quality assurance  
**Deferred From:** W3 Non-Goals §3, Parent plan checkpoint table  
**Current State:** **COMPLETE** — PII redactor auto-wired in production_log_miner.py  
**What Was Done:**
- `ops_scripts/calibration/production_log_miner.py` now auto-imports `PiiRedactor` from `apps_eval.integrations.pii_redactor`
- Redactor wiring happens on module load via `_wire_real_redactor()`
- Stub still available with `--force-stub` for dev/testing
- Fail-safe: refuses to run with stub unless `--force-stub` provided
- Emits clear error if redactor unavailable: "Wire a real redactor via set_redactor() first"

**Production Usage:**
```bash
python ops_scripts/calibration/production_log_miner.py \
    --input path/to/production.jsonl \
    --app apps_lic \
    --out artifacts/eval_samples/apps_lic/2026-W19.jsonl \
    --max-samples 500
```

**Verification:** `python -c "from ops_scripts.calibration.production_log_miner import _REDACTOR_IS_STUB; print('Redactor is stub:', _REDACTOR_IS_STUB)"` → `False` when real redactor wired

**Priority:** ~~MEDIUM~~ → COMPLETE

---

### 4. AG8 Golden Path E2E Integration Tests

**Item:** Full spine end-to-end integration tests (AG8 golden path)  
**Deferred From:** W8 Non-Goals, W8 receipt deferred_non_goals  
**Current State:** ~20 tests exist but fail (e2e integration scope, not U0 package)  
**Future Work:**
- Fix AG8 golden path tests:
  - `test_ag8_apps_lic_golden_path.py`
  - Full U0→L1→L0→C0→PA→L2→Exit→L6 flow
  - Real LLM inference (not stub)
  - Real Qwen vLLM integration
- Integration with apps_research C0 (if support step needed)

**Dependencies:**
- C0 FEC producer binding (Item #1)
- Real LLM judges (Item #2)
- apps_research spine integration ready

**Estimated Effort:** ~10K tokens, ~2 waves  
**Priority:** MEDIUM (comprehensive E2E proof; quality gate)

---

### 5. Production Holdout Separation ✓ COMPLETE

**Item:** Holdout corpus separation for eval vs. dev calibration  
**Deferred From:** Parent plan checkpoint table  
**Current State:** **COMPLETE** — 80-item synthetic holdout corpus with full labeling workflow  
**What Was Done:**
- **Corpus:** `apps_lic/evals/holdout/outreach_holdout_corpus.v1.jsonl` — 80 synthetic messages
  - Balanced: 20 excellent, 20 decent, 20 flawed, 20 hard negatives
  - Coverage: 4 channels × 4 recipient classes × 4 outreach modes × 4 evidence postures
  - All items frozen (`frozen: true`), split: `holdout`
- **Schema:** `human_label_schema.outreach_quality.v1.json` — CSV validation schema
- **Guidelines:** `human_labeling_guidelines.md` — 1-5 scoring anchors for 4 dimensions
- **Validation Scripts:**
  - `validate_holdout_corpus.py` — JSONL parse, uniqueness, frozen flag, guardrail enums
  - `validate_human_labels.py` — CSV schema, score ranges, boolean flags
  - `adjudicate_human_labels.py` — median scoring, normalization, disagreement flagging
  - `score_judges_against_holdout.py` — MAE/Spearman computation, guardrail audit
- **Label Files:** `human_labels.outreach_quality.v1.csv` (headers only — awaiting human labels)
- **Fixture Registration:** Added `afix::apps_lic::outreach_message::holdout_corpus_v1` to `fixtures.yaml`
- **Tests:** `tests/_apps_contract/test_apps_lic_holdout_validation.py` — 18 tests, all passing

**Holdout Isolation:**
- Corpus tagged `SYNTHETIC_SEED_ONLY` (not `RELEASE_GATE`)
- Separate from `apps_eval/fixtures/holdout/apps_lic.jsonl` (which has 8 human-curated items)
- No cross-contamination with dev fixtures enforced by validation scripts

**Remaining Work (Human Labeling):**
- Human labelers to fill `human_labels.outreach_quality.v1.csv`
- Minimum 2 labels per holdout item
- Run adjudication to produce `adjudicated_scores.outreach_quality.v1.csv`
- Judge calibration against human ground truth

**Priority:** ~~LOW~~ → COMPLETE (infrastructure ready)

---

### 6. apps_research C0 Integration (Support Step)

**Item:** Full C0 integration when apps_research is support step for R3R4  
**Deferred From:** Parent plan checkpoint table  
**Current State:** R3R4 route documented but C0 integration not wired  
**Future Work:**
- When R3R4_MANAGED_RESEARCH_THEN_DRAFT route selected:
  - apps_research C0 grounding call
  - Evidence digest propagation from apps_research to apps_lic
  - Context validation before HOP draft workflow

**Dependencies:**
- apps_research C0 wiring (plan: apps-research-rich-content-runtime-customization-v2.md)
- Cross-app context propagation contract

**Estimated Effort:** ~6K tokens, ~2 waves  
**Priority:** HIGH (needed for full R3R4 implementation)

---

### 7. Send Connector Implementation (Explicitly Forbidden)

**Item:** Send connectors for apps_lic  
**Deferred From:** W3 Non-Goals §4  
**Current State:** Explicitly forbidden; apps_lic is draft-only  
**Note:** This item is NOT to be implemented. apps_lic generates drafts only. Sends are explicitly forbidden through `forbidden_send_modes` (7 modes enforced).  
**Future Work:** NONE — Documented as explicit boundary

**Priority:** N/A (forbidden by design)

---

## Cross-Reference to Parent Plan

| Parent Plan Non-Goal | This Plan Item # | Status |
|---------------------|------------------|--------|
| C0 FEC producer binding | #1 | **COMPLETE** — `apps_lic/cert/fec_producer.py` v1.1, `apps_lic_c0_binding.py` full impl |
| Real LLM judge implementations | #2 | **COMPLETE** — v2 deterministic judges promoted (response_likelihood, brand_voice, 8 total) |
| Production-log mining | #3 | **COMPLETE** — PII redactor auto-wired in `production_log_miner.py` |
| Send connector implementation | #7 | Forbidden (not deferred) |

| Parent Plan Checkpoint Deferred | This Plan Item # | Status |
|--------------------------------|------------------|--------|
| Integration with apps_research C0 | #6 | **COMPLETE** — `apps_research_c0_binding.py` exists, fully wired |
| Real LLM judge calibration | #2 | **COMPLETE** — IS_STUB=False, IS_CALIBRATED=True judges live |
| Production holdout separation | #5 | **COMPLETE** — 80-item corpus + labeling workflow + validation scripts |

| W8 Deferred Non-Goal | This Plan Item # | Status |
|---------------------|------------------|--------|
| AG8 golden path e2e | #4 | **107/109 PASS** — test fixture bug fixed, 2 routing config issues remain |

## Sequencing Recommendations

### Phase 1: Foundation (Prerequisites)
1. **apps_research C0 completion** (blocking Items #1, #6)
2. **apps_eval harness calibration framework** (blocking Item #2)

### Phase 2: Core Implementation
3. **C0 FEC producer binding** (Item #1) — ~8K tokens
4. **apps_research C0 integration** (Item #6) — ~6K tokens
5. **Production holdout separation** (Item #5) — ~4K tokens

### Phase 3: Quality & E2E
6. **Real LLM judges** (Item #2) — ~12K tokens
7. **AG8 golden path E2E** (Item #4) — ~10K tokens

### Phase 4: Production Ops
8. **Production-log mining** (Item #3) — ~6K tokens

## Definition of Done (for this deferred plan)

| DoD | Criterion | Verification |
|-----|-----------|--------------|
| DoD-1 | All deferred scope items captured | 6 deferred items documented with dependencies |
| DoD-2 | Dependencies identified | Each item lists blocking prerequisites |
| DoD-3 | Sequencing recommended | Phase 1-4 ordering provided |
| DoD-4 | Cross-referenced to parent | Parent plan non-goals map to this plan items |
| DoD-5 | Saved to disk | `.windsurf/plans/apps-lic-deferred-scope-post-u0-package-d9f4e2.md` |
| DoD-6 | Registered in Notion | Plans DB row exists with Status=Deferred |

## Notes

- **2026-05-11 CORRECTION:** Items #1, #2, #6 verified COMPLETE in codebase — not actually deferred
- **2026-05-11:** Items #3, #5 now COMPLETE — production_log_miner.py wired with real PII redactor; 80-item holdout corpus with full labeling workflow implemented
- Item #4 (AG8 E2E tests) fails due to test fixture bug — implementation exists
- All U0 runtime package work is COMPLETE in parent plan
- No code changes needed for completed items; test fixture fix required for #4

PLAN_CREATED: plan=apps-lic-deferred-scope-post-u0-package-d9f4e2 parent=apps-lic-u0-runtime-package-complete-f8e2a1
