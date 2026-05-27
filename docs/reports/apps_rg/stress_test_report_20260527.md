# Stress Test Report: apps_rg End-to-End — 2026-05-27

## Executive Summary

7 stress test runs across 4 sections and 4 distinct targets. Found **5 bugs**; **2 fixed in this session** with
unit test coverage. 2 additional bugs are LLM output quality issues (not code defects) requiring prompt attention.

---

## Test Matrix

| Target | Section | Exit | Product Status | X2 Fails |
|--------|---------|------|----------------|----------|
| Brown & Brown SVP IT | headline | 0 | X3_ALLOW ✅ | 0 |
| Brown & Brown SVP IT | unify_bullets | 0 | X3_ALLOW ✅ | 0 |
| Brown & Brown SVP IT | competencies | 1 | X3_BLOCK ❌ → FIXED | 0 (false positive) |
| Truist Head Agentic AI | executive_summary | 1 | X3_BLOCK ❌ | 2 |
| AIG VP Global Head Agentic AI | executive_summary | 1 | X3_BLOCK ❌ | 5 |
| Anthropic (no brief) | executive_summary | 2 | BLOCKED (expected) ✅ | — |

---

## Bug Inventory

### BUG-001 — FIXED ✅ `finalize_competencies_v3_output` false-positive X3_BLOCK on competencies

**Severity:** HIGH — every competencies run that modifies output through `finalize_competencies_v3_output`
results in a false-positive `product_quality_status: FAIL` and X3_BLOCK, despite all X2 gates passing.

**Root cause:** `ledger_blocks_product_pass` in `section_repair_ledger.py` treated ANY deterministic rewrite
(except `graph_only_generation_quality_repair`) as an unauthorized fix that hides X2 failures.
`finalize_competencies_v3_output` (capability projection, always runs on competencies) and
`repair_protected_unify_bullet_metrics` (metric restoration on unify_bullets) are authorized standard
pipeline steps, not error masks.

**Fix:** Extended `_AUTHORIZED_DET_OPS` frozenset to include both operations.

**Files changed:**
- `apps_rg/runtime/section_repair_ledger.py`
- `tests/unit/apps_rg/test_section_repair_ledger_authorized_ops.py` (7 new tests, all pass)

---

### BUG-002 — FIXED ✅ Synthesis regen sentence-count feedback never fires

**Severity:** HIGH — when `_build_synthesis_repair_user` is called with a sentence count failure
("Output has 5 sentences; executive synthesis requires exactly 6 sentences"), the targeted feedback
note never fired because the trigger condition checked `"sentence_"` (with underscore) while the
reject reason contains `"sentences"` (without underscore). Additionally, the `utilization_note`
contained ambiguous guidance: "Prefer 6 sentences when the fact pool has 7+ facts; use 5 when the
pool is tighter" — which contradicts the hard X2 gate requiring exactly 6.

**Fix:**
1. Added dedicated `sentence_count_note` that fires on `"found 5"`, `"found 4"`, or `"sentences; found"` in the reject reason blob.
2. Changed `utilization_note` condition from `"sentence_" in blob` to `"sentences" in blob`.
3. Removed ambiguous "use 5 when the pool is tighter" from `utilization_note`.

**Files changed:**
- `apps_rg/runtime/sections/executive_summary_lane.py`
- `tests/unit/apps_rg/test_executive_summary_synthesis_regen.py` (4 new tests added, all pass)

---

### BUG-003 — OPEN — Truist exec_summary: model generates 5 sentences persistently

**Severity:** MEDIUM — specific target profiles (Truist "Head of Agentic AI Engineering") cause
the LLM to consistently produce 5-sentence outputs even after 3 synthesis regen cycles.

**Observed output:**
> "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, and
> commercialization into one IT strategy and innovation agenda for decentralized regulated
> enterprises. Building on that platform foundation, platform commercialization generated $22M in
> IP-led revenue and expanded gross margins by 20% while scaling the ML engineering organization
> from 8 to 28 specialists. Through that operating model, Basel III and CCAR data lineage,
> cataloging, and automated validation frameworks cut regulatory reporting errors by 40%.
> FSA-chartered quantitative foundation, built through early-career capital modeling and portfolio
> stress analytics. Governed platform delivery, engineering scale, and regulatory-grade controls
> extend that arc toward enterprise architecture modernization and data-driven innovation programs."

5 sentences. Also contains thin S6 recap pattern ("extend that arc toward").

**Contributing factors:**
- BUG-002 (now fixed) meant the model didn't get explicit "SENTENCE COUNT HARD FAIL" feedback
- The Truist brief may produce a narrower C0 fact set that the model compresses into 5 sentences
- S6 is a thin recap, not a genuine synthesis sentence

**Recommended next step:** Run another stress test on Truist after BUG-002 fix goes live.

---

### BUG-004 — OPEN — AIG exec_summary: claim_ledger attribution failures

**Severity:** MEDIUM — AIG run failed `x2_exec_summary_allowed_fact_utilization` because
`fact_exec_002` was used in prose ("scaling the ML engineering organization from 8 to 28
specialists") but not cited in the claim_ledger. Also: `x2_claim_ledger_row_count_matches_sentence_count`
failed (6 sentences but different number of claim_ledger rows).

**Contributing factors:**
- AIG is an "Agentic AI" focused role — different from SVP IT Strategy. The composition plan
  may route differently, resulting in S3 cramming two facts without separate ledger rows.
- The model produced a "Designed and operationalized" S2 opener (mechanical stack) but the gate passed.

**Recommended next step:** Inspect `fact_exec_002` claim_ledger attribution in the AIG proof
artifact; verify if the composition plan's fact weaving guidance applies `fact_exec_002` to S3 or S4.

---

### BUG-005 — OPEN — AIG exec_summary: X1D judges not running

**Severity:** LOW — `x2_x1d_required_judges_present: FAIL` and `x2_x1d_schema_valid: FAIL` on
AIG section-only run. No judges ran (`X1D_LLM_JUDGE_OUTPUTS` table was empty).

**Observed context:** Brown & Brown exec_summary (previous passing sessions) also shows empty X1D
table in section-only mode. The difference is that AIG's proof profile may declare judges as
required for X3 ALLOW, while Brown & Brown's doesn't.

**Recommended next step:** Check `APPS_RG_E2E_X1D_JUDGES` env var requirements for the AIG target
profile vs the SVP profile. May require `--x1d-judges` flag for this role profile.

---

## Files Changed This Session

- [`section_repair_ledger.py`](apps_rg/runtime/section_repair_ledger.py) — BUG-001 fix
- [`executive_summary_lane.py`](apps_rg/runtime/sections/executive_summary_lane.py) — BUG-002 fix
- [`test_section_repair_ledger_authorized_ops.py`](tests/unit/apps_rg/test_section_repair_ledger_authorized_ops.py) — new (7 tests)
- [`test_executive_summary_synthesis_regen.py`](tests/unit/apps_rg/test_executive_summary_synthesis_regen.py) — 4 new tests appended

## Artifacts (stress test outputs)

- [`stress_test_truist_exec_summary.txt`](artifacts/stress_test_truist_exec_summary.txt)
- [`stress_test_bb_competencies.txt`](artifacts/stress_test_bb_competencies.txt)
- [`stress_test_bb_headline.txt`](artifacts/stress_test_bb_headline.txt)
- [`stress_test_anthropic_no_brief.txt`](artifacts/stress_test_anthropic_no_brief.txt)
- [`stress_test_aig_exec_summary.txt`](artifacts/stress_test_aig_exec_summary.txt)
- [`stress_test_bb_unify_bullets.txt`](artifacts/stress_test_bb_unify_bullets.txt)
