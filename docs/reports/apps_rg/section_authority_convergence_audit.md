# Section Authority Convergence Audit

Generated: `2026-05-22T09:40:32.923519+00:00`
Proof inventory: `artifacts/apps_rg/runtime_proofs/full_resume_0e41a1c13cfe/lanes`

## Executive summary

This audit compares section prompt contracts, product-shape SSOT, X2 validators, 
`lane_registry` critical gates, and canonical runtime proof artifacts. 
Goal: prevent **executive_summary-style authority drift** (prompt shape ≠ X2 shape ≠ rigor anchors).

## Cross-section patterns

- lane_registry critical gates are not all enumerated in production x2_gate_outputs.json
- C0 critical gates are rigor-critical but absent from lane x2_gate_outputs sidecar
- executive_summary proof bundle contains RETIRED_EXEC_SUMMARY_X2_GATE_IDS — refresh runtime proof

## High-severity gaps

- headline: rigor_critical_gate_absent_in_runtime_x2: ['x2_headline_claim_ledger_no_silent_row_drop', 'x2_headline_claim_ledger_segment_decomposition', 'x2_headline_text_claim_coverage_integrity']
- executive_summary: rigor_critical_gate_absent_in_runtime_x2: ['x2_exec_summary_evidence_utilization', 'x2_exec_summary_jd_alignment_proof_flags', 'x2_exec_summary_no_credential_dump', 'x2_exec_summary_no_mechanism_inventory', 'x2_exec_summary_paragraph_max_words', 'x2_exec_summary_prompt_template_authority', 'x2_exec_summary_sentence_count_4_5']
- executive_summary: display_contains_credential_dump_risk: certifications named in resume_display_text while x2_exec_summary_no_credential_dump missing or not failed
- competencies: rigor_critical_gate_absent_in_runtime_x2: ['x2_competencies_approved_category_labels', 'x2_competencies_keyword_repetition_limit', 'x2_competencies_no_all_generic_skill_phrase', 'x2_competencies_no_fragment_or_one_word_terms', 'x2_competencies_term_support_ids_present']
- competencies: rigor_critical_gate_failed: ['x2_competencies_no_low_rigor_two_word_items', 'x2_competencies_no_metrics_as_skills_without_capability_context']
- unify_bullets: rigor_critical_gate_absent_in_runtime_x2: ['x2_unify_at_most_one_mechanism_dense_bullet', 'x2_unify_metric_anchor_bullet_ownership']
- ibm_bullets: rigor_critical_gate_absent_in_runtime_x2: ['x2_ibm_metric_anchor_bullet_ownership', 'x2_text_claim_coverage_integrity']
- ibm_narrative: rigor_critical_gate_absent_in_runtime_x2: ['x2_ibm_narrative_claim_ledger_clause_decomposition', 'x2_ibm_narrative_no_meta_disclaimer_in_display', 'x2_ibm_narrative_requires_finalized_bullets']
- ibm_narrative: display_meta_disclaimer_present_but_gate_absent: 'without claiming' in narrative while x2_ibm_narrative_no_meta_disclaimer_in_display not emitted in x2_gate_outputs.json

## Per-section status

| Section | Status |
|---------|--------|
| headline | PARTIAL |
| executive_summary | FAIL |
| competencies | FAIL |
| unify_bullets | PARTIAL |
| unify_narrative | PARTIAL |
| ibm_bullets | PARTIAL |
| ibm_narrative | FAIL |

## headline

**Status:** PARTIAL

### Product shape
- SSOT: `4 segments; prefix 'SVP Engineering'; 3 pipe separators; 10-13 words total; one line only`
- Contract mode: `COMPOSE_NEW`

### Source authority
- jd_as_proof_allowed: `False`
- companion: `U_TIER_CONTEXT_ONLY`

### Rigor vs runtime X2
- Critical gates (rigor): 18
- Runtime gate rows: 43
- Aggregation: `PASS`

### Critical mismatches
- rigor_critical_gate_absent_in_runtime_x2: ['x2_headline_claim_ledger_no_silent_row_drop', 'x2_headline_claim_ledger_segment_decomposition', 'x2_headline_text_claim_coverage_integrity']
- rigor_c0_gate_not_in_x2_bundle (expected c0_metrics.json sidecar): ['x2_c0_metrics_artifact_present', 'x2_c0_support_status_gate']

### Recommended fix order
- Reconcile lane_registry vs runtime gate enumeration for headline

## executive_summary

**Status:** FAIL

### Product shape
- SSOT: `4-5 sentences; max 220 words; max 58 words/sentence; fit_to_evidence; claim_ledger required; no inline source tags in display text`
- Contract mode: `REWRITE_FROM_FACT_POOL`

### Source authority
- jd_as_proof_allowed: `False`
- companion: `U_TIER_CONTEXT_ONLY`

### Rigor vs runtime X2
- Critical gates (rigor): 16
- Runtime gate rows: 75
- Aggregation: `PASS`

### Critical mismatches
- prompt_drift:missing_required_all_patterns: not all matched (AND): ['briefing_used_as_proof', 'companion_context_used_as_proof'] (apps_rg\prompt_assembly\templates\executive_summary.generate_scratch_v1.yaml)
- rigor_critical_gate_absent_in_runtime_x2: ['x2_exec_summary_evidence_utilization', 'x2_exec_summary_jd_alignment_proof_flags', 'x2_exec_summary_no_credential_dump', 'x2_exec_summary_no_mechanism_inventory', 'x2_exec_summary_paragraph_max_words', 'x2_exec_summary_prompt_template_authority', 'x2_exec_summary_sentence_count_4_5']
- rigor_c0_gate_not_in_x2_bundle (expected c0_metrics.json sidecar): ['x2_c0_metrics_artifact_present', 'x2_c0_support_status_gate']
- display_contains_credential_dump_risk: certifications named in resume_display_text while x2_exec_summary_no_credential_dump missing or not failed

### Recommended fix order
- Align SRFS vs default X2 gate IDs with lane_registry critical set
- Emit x2_exec_summary_no_credential_dump in all runtime bundles
- Enforce paragraph_max_words + jd_alignment_proof_flags in SRFS runs
- Reconcile lane_registry vs runtime gate enumeration for executive_summary

## competencies

**Status:** FAIL

### Product shape
- SSOT: `6-8 categories; 3-6 terms/category; compact noun phrases; ENGINEERING & PLATFORM COMPETENCIES authority`
- Contract mode: `COMPOSE_NEW`

### Source authority
- jd_as_proof_allowed: `False`
- companion: `U_TIER_CONTEXT_ONLY`

### Rigor vs runtime X2
- Critical gates (rigor): 22
- Runtime gate rows: 48
- Aggregation: `FAIL`

### Critical mismatches
- rigor_critical_gate_absent_in_runtime_x2: ['x2_competencies_approved_category_labels', 'x2_competencies_keyword_repetition_limit', 'x2_competencies_no_all_generic_skill_phrase', 'x2_competencies_no_fragment_or_one_word_terms', 'x2_competencies_term_support_ids_present']
- rigor_c0_gate_not_in_x2_bundle (expected c0_metrics.json sidecar): ['x2_c0_metrics_artifact_present', 'x2_c0_support_status_gate']
- rigor_critical_gate_failed: ['x2_competencies_no_low_rigor_two_word_items', 'x2_competencies_no_metrics_as_skills_without_capability_context']

### Recommended fix order
- Repair low-rigor two-word terms and metric-without-context terms before X3
- Reconcile lane_registry vs runtime gate enumeration for competencies

## unify_bullets

**Status:** PARTIAL

### Product shape
- SSOT: `6 bullets; HEAVY=2 MODERATE=3 LIGHT_PROTECTED=1; bul_unify_* fact ids only`
- Contract mode: `REWRITE_FROM_FACT_POOL`

### Source authority
- jd_as_proof_allowed: `False`
- companion: `NONE`

### Rigor vs runtime X2
- Critical gates (rigor): 13
- Runtime gate rows: 35
- Aggregation: `PASS`

### Critical mismatches
- rigor_critical_gate_absent_in_runtime_x2: ['x2_unify_at_most_one_mechanism_dense_bullet', 'x2_unify_metric_anchor_bullet_ownership']
- rigor_c0_gate_not_in_x2_bundle (expected c0_metrics.json sidecar): ['x2_c0_metrics_artifact_present', 'x2_c0_support_status_gate']

### Recommended fix order
- Reconcile lane_registry vs runtime gate enumeration for unify_bullets

## unify_narrative

**Status:** PARTIAL

### Product shape
- SSOT: `exactly 1 sentence; <= 58 words; <= 360 chars; preferred 34-48 words; requires finalized unify bullets`
- Contract mode: `SUMMARIZE_ROLE_SCOPE`

### Source authority
- jd_as_proof_allowed: `False`
- companion: `U_TIER_CONTEXT_ONLY`

### Rigor vs runtime X2
- Critical gates (rigor): 11
- Runtime gate rows: 36
- Aggregation: `PASS`

### Critical mismatches
- rigor_c0_gate_not_in_x2_bundle (expected c0_metrics.json sidecar): ['x2_c0_metrics_artifact_present', 'x2_c0_support_status_gate']

### Recommended fix order
- Reconcile lane_registry vs runtime gate enumeration for unify_narrative

## ibm_bullets

**Status:** PARTIAL

### Product shape
- SSOT: `5 bullets; HEAVY=0 (forbidden); MODERATE=3 LIGHT_PROTECTED=2; bul_ibm_* only`
- Contract mode: `REWRITE_FROM_FACT_POOL_CONSTRAINED`

### Source authority
- jd_as_proof_allowed: `False`
- companion: `NONE`

### Rigor vs runtime X2
- Critical gates (rigor): 12
- Runtime gate rows: 32
- Aggregation: `PASS`

### Critical mismatches
- rigor_critical_gate_absent_in_runtime_x2: ['x2_ibm_metric_anchor_bullet_ownership', 'x2_text_claim_coverage_integrity']
- rigor_c0_gate_not_in_x2_bundle (expected c0_metrics.json sidecar): ['x2_c0_metrics_artifact_present', 'x2_c0_support_status_gate']

### Recommended fix order
- Reconcile lane_registry vs runtime gate enumeration for ibm_bullets

## ibm_narrative

**Status:** FAIL

### Product shape
- SSOT: `exactly 1 sentence; <= 58 words; <= 360 chars; requires finalized ibm bullets; no meta disclaimer in display`
- Contract mode: `REWRITE_FROM_FACT_POOL`

### Source authority
- jd_as_proof_allowed: `False`
- companion: `U_TIER_CONTEXT_ONLY`

### Rigor vs runtime X2
- Critical gates (rigor): 12
- Runtime gate rows: 36
- Aggregation: `PASS`

### Critical mismatches
- rigor_critical_gate_absent_in_runtime_x2: ['x2_ibm_narrative_claim_ledger_clause_decomposition', 'x2_ibm_narrative_no_meta_disclaimer_in_display', 'x2_ibm_narrative_requires_finalized_bullets']
- rigor_c0_gate_not_in_x2_bundle (expected c0_metrics.json sidecar): ['x2_c0_metrics_artifact_present', 'x2_c0_support_status_gate']
- display_meta_disclaimer_present_but_gate_absent: 'without claiming' in narrative while x2_ibm_narrative_no_meta_disclaimer_in_display not emitted in x2_gate_outputs.json

### Recommended fix order
- Emit and fail-closed x2_ibm_narrative_no_meta_disclaimer_in_display in production X2
- Reconcile lane_registry vs runtime gate enumeration for ibm_narrative

## Explicit non-claims

- No release eligibility
- No one-spine convergence
- No agentic_core edits
- No live regeneration in this audit run
- Mock/stub paths not used as product proof unless labeled
