# Live Qwen remaining blockers — Wave 2 closeout

**STATUS: PARTIAL**

Wave 2 targeted the four blocker sections from [live_qwen_remaining_blockers_inventory.md](live_qwen_remaining_blockers_inventory.md). All four sections completed **REAL_LLM** `qwen_vllm` runs with **augmented_skills_graph** skills authority **PASS** and no `agentic_core` edits. Deterministic X2 targets for competencies and IBM lanes are met; judge/X3/proof_eligible gaps remain documented below.

## BEFORE_AFTER_MATRIX

| Section | Before (Wave 1) | After (Wave 2) |
|---------|-----------------|----------------|
| **competencies** | 60s timeout, empty `competencies[]`, X2 FAIL | Non-empty 8 categories, X2 **PASS**, X3 **ALLOW** (`competencies_20260519_012651`) |
| **ibm_bullets** | Missing IBM metrics, `bul_ibm_*` pool mismatch, X2 FAIL | Canonical hydration, core metrics present, X2 **PASS** (`ibm_bullets_20260519_012750`) |
| **ibm_narrative** | `bul_ibm_001` off allow-list, X2 FAIL | Fact-pool remap, X2 **PASS** (`ibm_narrative_20260519_012430`) |
| **executive_summary** | 4 sentences → X2 FAIL `sentence_count_2_3`; judge soft-fail | 3 sentences, X2 **PASS**; judge soft-fail **open** (`exec_summary_20260519_012517`) |

## SECTION_OUTPUTS

### competencies

Run: [competencies_20260519_012651](artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260519_012651)

Eight non-empty categories (excerpt): Agentic AI Systems, Platform Modernization, Quantitative Foundations, Engineering Leadership, HPC Workflows, Regulated Enterprise Environment, AI Platform Leadership, Certifications — see [competencies_section_output.json](artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260519_012651/competencies_section_output.json).

### ibm_bullets

Run: [ibm_bullets_20260519_012750](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260519_012750)

Five bullets with canonical metrics ($15M, 99.9%, 30%, 25%, 50%) — [ibm_bullets_output.txt](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260519_012750/ibm_bullets_output.txt).

### ibm_narrative

Run: [ibm_narrative_20260519_012430](artifacts/apps_rg/runtime_proofs/ibm_narrative/real/ibm_narrative_20260519_012430)

> At IBM, led enterprise-scale cloud, data, lineage and observability initiatives for regulated financial services, establishing the reliability and governance discipline that supported later production AI platform leadership.

### executive_summary

Run: [exec_summary_20260519_012517](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_012517)

Three-sentence display text (X2 band) — [resume_display_text.txt](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_012517/resume_display_text.txt).

## SKILLS_GRAPH_RECEIPTS

| Section | `skills_authority_source_type` | `skills_authority_status` | `legacy_broad_skills_ledger_skills_authority` |
|---------|-------------------------------|---------------------------|-----------------------------------------------|
| competencies | `augmented_skills_graph` | PASS | false |
| ibm_bullets | `augmented_skills_graph` | PASS | false |
| ibm_narrative | `augmented_skills_graph` | PASS | false |
| executive_summary | `augmented_skills_graph` | PASS | false |

Claim evidence remains separate (`candidate_fact_ledger` / `base_resume_fallback` per section usage ledgers).

## X2_RESULTS

| Section | X2 | Failed gates |
|---------|-----|--------------|
| competencies | **PASS** | — |
| ibm_bullets | **PASS** | — |
| ibm_narrative | **PASS** | — |
| executive_summary | **PASS** | — |

## X3_RESULTS

| Section | X3 | Notes |
|---------|-----|-------|
| competencies | **X3_ALLOW** | Judges advisory for allow path |
| ibm_bullets | **X3_REVIEW_JUDGE_PROVIDER_BLOCKED** | X2 PASS; judge transport blocked |
| ibm_narrative | **X3_BLOCK** | Decisive `gemini_pro`; X2 PASS |
| executive_summary | **X3_REVIEW_JUDGE_SOFT_FAIL** | X2 PASS; `gemini_pro`, `anthropic_claude` soft |

## TIMEOUT_RESULTS

| Section | Timeout | Outcome |
|---------|---------|---------|
| competencies | 120s chat timeout (was 60s) | No transport timeout; non-empty output |
| ibm_bullets | default | REAL_LLM complete |
| ibm_narrative | default | REAL_LLM complete |
| executive_summary | default | REAL_LLM complete |

## JUDGE_RESULTS

- **competencies:** X3_ALLOW; `anthropic_claude` soft; `gemini_pro` blocked provider (non-decisive for allow).
- **ibm_bullets:** X2 PASS; judge provider blocked at X3 (not a gate weakening).
- **ibm_narrative:** X2 PASS; decisive `gemini_pro` failure → X3_BLOCK.
- **executive_summary:** X2 PASS; soft-fail judges — **open judge gap** (5-sentence rubric vs 2–3 sentence non-SRFS X2 band).

## AGENTIC_CORE_DIFF_STATUS

`git diff -- agentic_core` → **clean** (no core edits).

## EXPLICIT_NON_CLAIMS

- CLI exit 0 with `--allow-non-allow-exit-zero` is inspection plumbing only, not certification.
- Mock provider and offline contract stub were not used on these runs.
- `broad_skills_ledger` was not used as skills authority.
- X2/X3/judge/density gates were not weakened.

## OPEN_GAPS

1. **executive_summary:** Judge soft-fail without safe 5-sentence path under non-SRFS X2 (documented; no prompt/gate weakening applied).
2. **ibm_narrative:** X3_BLOCK from decisive `gemini_pro` despite X2 PASS.
3. **ibm_bullets:** X3 judge provider blocked; product X2 PASS.

Machine-readable companion: [live_qwen_remaining_blockers_closeout.json](live_qwen_remaining_blockers_closeout.json).

## Wave 2 patches (apps_rg only)

- Competencies: lower `max_tokens`, 120s timeout, projection cap, truncation salvage, fact-id typo repair on structured terms.
- IBM: canonical resume hydration when ledger slice lacks `bul_ibm_*` or core metrics missing.
- IBM narrative: fact-pool claim ledger remap.
- Executive summary: post-SRFS sentence-band coercion to 2–3 sentences for non-SRFS X2.
