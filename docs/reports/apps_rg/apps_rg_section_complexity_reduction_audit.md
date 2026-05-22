# apps_rg Section Complexity Reduction Audit

Generated: `2026-05-22T09:41:20.449529+00:00`
Proof inventory: `artifacts/apps_rg/runtime_proofs/full_resume_0e41a1c13cfe/lanes`

## Goal

Reduce per-section machinery so apps_rg stays a **thin app** over the governed spine: 
one canonical runtime path, one section spec per lane, shared prompt compile + X2 framework, 
no bespoke repair stacks or duplicate quality authority.

## Cross-section patterns

- 7 lanes × (contract + product_shape + lane_registry + lane_py + x2_py + x1d_py) ≈ mini-spine each
- lane_registry marks gates critical that production x2_gate_outputs.json does not emit
- C0 critical gates validated via c0_metrics.json sidecar, not x2_gate_outputs — rigor over-counts
- 50–78 proof files per lane; only 4–5 gate release artifacts
- executive_summary highest split: 10+ section modules, graph_only repair, SRFS vocabulary drift
- competencies + ibm_narrative use runtime/execution two-file seam

## Per-section status

| Section | Status | Modules | LOC | Repair modules |
|---------|--------|---------|-----|----------------|
| headline | PARTIAL | 6 | 3239 | 0 |
| executive_summary | PARTIAL | 18 | 10427 | 3 |
| competencies | FAIL | 14 | 5828 | 1 |
| unify_bullets | PARTIAL | 5 | 2203 | 0 |
| unify_narrative | PARTIAL | 5 | 1969 | 0 |
| ibm_bullets | PARTIAL | 5 | 1964 | 0 |
| ibm_narrative | PARTIAL | 9 | 2663 | 1 |

## headline

**Status:** PARTIAL

### Runtime modules (section-tagged)
- `apps_rg/runtime/sections/headline_fact_id_resolution.py` (290 lines)
- `apps_rg/runtime/sections/headline_lane.py` (1796 lines)
- `apps_rg/runtime/sections/headline_pa.py` (275 lines)
- `apps_rg/runtime/validators/headline_x2.py` (790 lines)
- `apps_rg/runtime/judges/headline_x1d.py` (83 lines)
- `apps_rg/runtime/dispatch/headline_pa.py` (5 lines)

### Repair stack

- normalize_claim_ledger_string_fact_ids
- lane_normalize_claim_ledger
- headline_proof_shape_retry_llm (same-authority Qwen)
- headline_format_repair LLM
- fact_id_typo_repair against allowlist

### Duplicate dispatch / quality authority

- infer_product_quality (X2 mirror) + headline_format_repair LLM loops
- headline_proof_shape_retry_llm — second quality authority before X2
- headline_fact_id_resolution.py — parallel to shared fact_id_typo_repair

### Duplicated invariants

- lane_registry lists 8 critical gates not in product_shape SSOT (universal/style/C0)

### Rigor gates absent in production `x2_gate_outputs.json`
- `x2_c0_metrics_artifact_present`
- `x2_c0_support_status_gate`
- `x2_headline_claim_ledger_no_silent_row_drop`
- `x2_headline_claim_ledger_segment_decomposition`
- `x2_headline_text_claim_coverage_integrity`

### Collapse / delete candidates

- COLLAPSE split lane_runtime + lane_execution into single generic section runner
- COLLAPSE headline_format_repair LLM loops → X2 fail + one regen max
- ALIGN lane_registry with runtime X2 enumeration OR drop rigor-only ghosts

## executive_summary

**Status:** PARTIAL

### Runtime modules (section-tagged)
- `apps_rg/runtime/sections/executive_summary_briefing.py` (136 lines)
- `apps_rg/runtime/sections/executive_summary_composition.py` (517 lines)
- `apps_rg/runtime/sections/executive_summary_evidence_capsule.py` (409 lines)
- `apps_rg/runtime/sections/executive_summary_judge_remediation.py` (491 lines)
- `apps_rg/runtime/sections/executive_summary_lane.py` (2242 lines)
- `apps_rg/runtime/sections/executive_summary_pa.py` (486 lines)
- `apps_rg/runtime/sections/executive_summary_proof_bundle.py` (253 lines)
- `apps_rg/runtime/sections/executive_summary_repair_policy.py` (52 lines)
- `apps_rg/runtime/sections/executive_summary_srfs_binding.py` (199 lines)
- `apps_rg/runtime/sections/executive_summary_synthesis_monotonic.py` (134 lines)
- `apps_rg/runtime/sections/executive_summary_targeting_cap.py` (410 lines)
- `apps_rg/runtime/sections/executive_summary_token_budget.py` (724 lines)
- … +6 more

### Repair stack

- RELEASE: SRFS emergency finalizer DISABLED
- RELEASE: SRFS judge-safe / density micro-expansion DISABLED
- synthesis_regeneration_enabled (one Qwen regen)
- graph_only_generation_quality_repair (deterministic reformat)
- claim_ledger allowlist repair
- coerce_resume_display_sentence_count_band
- offline SRFS mock uses 5-sentence arc (stub only)

### Duplicate dispatch / quality authority

- infer_product_quality (delegates to X2 but lane still 1858 LOC)
- apply_executive_summary_targeting_cap + token_budget_policy — pre-X2 shaping
- graph_only_generation_quality_repair — deterministic rewrite parallel to X2 style gates
- coerce_resume_display_sentence_count_band — display coercion
- retry_qwen_for_synthesis — second LLM authority when synthesis_regeneration_enabled
- executive_summary_composition.py + evidence_capsule + proof_bundle — split orchestration

### Duplicated invariants

- Second contract file apps_rg/prompt_assembly/section_contracts/executive_summary_contract.yaml overlaps section_prompt_contracts/executive_summary.contract.yaml
- lane_registry lists 5 critical gates not in product_shape SSOT (universal/style/C0)
- RETIRED_EXEC_SUMMARY_X2_GATE_IDS documented in section_product_shape_ssot — must not reappear in run_x2_gates
- EXEC_SUMMARY_STYLE_CRITICAL_GATES in lane_registry duplicates product_shape style_gate_ids

### Rigor gates absent in production `x2_gate_outputs.json`
- `x2_c0_metrics_artifact_present`
- `x2_c0_support_status_gate`
- `x2_exec_summary_evidence_utilization`
- `x2_exec_summary_jd_alignment_proof_flags`
- `x2_exec_summary_no_credential_dump`
- `x2_exec_summary_no_mechanism_inventory`
- `x2_exec_summary_paragraph_max_words`
- `x2_exec_summary_prompt_template_authority`
- `x2_exec_summary_sentence_count_4_5`

### Collapse / delete candidates

- DELETE declarative duplicate: apps_rg/prompt_assembly/section_contracts/executive_summary_contract.yaml → fold into section_spec only
- COLLAPSE split lane_runtime + lane_execution into single generic section runner
- DELETE bespoke repair modules; keep shared fact_id_typo_repair + optional one regen flag in section_spec
- DONE(W2): exec_summary_srfs_density_repair + emergency_finalizer removed
- COLLAPSE executive_summary_composition/evidence_capsule/proof_bundle into spec-driven hooks
- MERGE graph_only_quality into X2 fail-closed only (no parallel rewrite)
- ALIGN lane_registry with runtime X2 enumeration OR drop rigor-only ghosts

## competencies

**Status:** FAIL

### Runtime modules (section-tagged)
- `apps_rg/runtime/sections/competencies_capability_projection.py` (917 lines)
- `apps_rg/runtime/sections/competencies_certification_contract.py` (300 lines)
- `apps_rg/runtime/sections/competencies_lane.py` (80 lines)
- `apps_rg/runtime/sections/competencies_lane_defaults.py` (28 lines)
- `apps_rg/runtime/sections/competencies_lane_execution.py` (797 lines)
- `apps_rg/runtime/sections/competencies_lane_runtime.py` (1448 lines)
- `apps_rg/runtime/sections/competencies_pa.py` (295 lines)
- `apps_rg/runtime/sections/competencies_rigor.py` (338 lines)
- `apps_rg/runtime/sections/competencies_term_phrase.py` (12 lines)
- `apps_rg/runtime/sections/competencies_v3_contract.py` (215 lines)
- `apps_rg/runtime/validators/competencies_proof_markers.py` (33 lines)
- `apps_rg/runtime/validators/competencies_x2.py` (1149 lines)
- … +2 more

### Repair stack

- repair_structured_competencies_source_facts
- bullet_restatement_repair LLM
- fact_id_typo_repair
- deterministic keyword-stuffing repair templates

### Duplicate dispatch / quality authority

- competencies_lane_runtime.py (1542) + competencies_lane_execution.py (795) — two-path seam
- competencies_rigor.py constants duplicate competencies_x2 + lane_registry
- competencies_capability_projection finalize — post-LLM repair stack
- bullet_restatement_repair LLM — narrative quality outside X2

### Duplicated invariants

- Second contract file apps_rg/prompt_assembly/section_contracts/competencies_contract.yaml overlaps section_prompt_contracts/competencies.contract.yaml
- lane_registry lists 7 critical gates not in product_shape SSOT (universal/style/C0)
- competencies_rigor.py MIN/MAX category counts triplicate competencies_x2 + product_shape SSOT

### Rigor gates absent in production `x2_gate_outputs.json`
- `x2_c0_metrics_artifact_present`
- `x2_c0_support_status_gate`
- `x2_competencies_approved_category_labels`
- `x2_competencies_keyword_repetition_limit`
- `x2_competencies_no_all_generic_skill_phrase`
- `x2_competencies_no_fragment_or_one_word_terms`
- `x2_competencies_term_support_ids_present`

### Collapse / delete candidates

- DELETE declarative duplicate: apps_rg/prompt_assembly/section_contracts/competencies_contract.yaml → fold into section_spec only
- COLLAPSE split lane_runtime + lane_execution into single generic section runner
- DELETE bespoke repair modules; keep shared fact_id_typo_repair + optional one regen flag in section_spec
- DELETE competencies_rigor.py — derive checks from section_spec + competencies_x2
- COLLAPSE competencies_capability_projection into validator-only path
- ALIGN lane_registry with runtime X2 enumeration OR drop rigor-only ghosts

## unify_bullets

**Status:** PARTIAL

### Runtime modules (section-tagged)
- `apps_rg/runtime/sections/unify_bullets_lane.py` (1196 lines)
- `apps_rg/runtime/sections/unify_bullets_pa.py` (147 lines)
- `apps_rg/runtime/validators/unify_bullets_x2.py` (766 lines)
- `apps_rg/runtime/judges/unify_bullets_x1d.py` (89 lines)
- `apps_rg/runtime/dispatch/unify_bullets_pa.py` (5 lines)

### Repair stack

- repair_protected_unify_bullet_metrics
- distribution / proof-shape Qwen repair
- fact_id_typo_repair

### Duplicate dispatch / quality authority

- repair_protected_unify_bullet_metrics + distribution Qwen repair
- foundation vs distribution checks split across lane + x2

### Duplicated invariants

- Second contract file apps_rg/prompt_assembly/section_contracts/unify_contract.yaml overlaps section_prompt_contracts/unify_bullets.contract.yaml
- lane_registry lists 7 critical gates not in product_shape SSOT (universal/style/C0)
- DEFAULT_DISTRIBUTION constants in unify_bullets_x2 / ibm_bullets_x2 + product_shape + templates

### Rigor gates absent in production `x2_gate_outputs.json`
- `x2_c0_metrics_artifact_present`
- `x2_c0_support_status_gate`
- `x2_unify_at_most_one_mechanism_dense_bullet`
- `x2_unify_metric_anchor_bullet_ownership`

### Collapse / delete candidates

- DELETE declarative duplicate: apps_rg/prompt_assembly/section_contracts/unify_contract.yaml → fold into section_spec only
- COLLAPSE split lane_runtime + lane_execution into single generic section runner
- ALIGN lane_registry with runtime X2 enumeration OR drop rigor-only ghosts

## unify_narrative

**Status:** PARTIAL

### Runtime modules (section-tagged)
- `apps_rg/runtime/sections/unify_narrative_lane.py` (1136 lines)
- `apps_rg/runtime/sections/unify_narrative_pa.py` (179 lines)
- `apps_rg/runtime/validators/unify_narrative_x2.py` (565 lines)
- `apps_rg/runtime/judges/unify_narrative_x1d.py` (84 lines)
- `apps_rg/runtime/dispatch/unify_narrative_pa.py` (5 lines)

### Repair stack

- companion metric bundle Qwen repair
- fact_id_typo_repair

### Duplicate dispatch / quality authority

- companion metric bundle Qwen repair
- companion_unify_bullets_context artifacts — dependency + duplicate narrative checks

### Duplicated invariants

- Second contract file apps_rg/prompt_assembly/section_contracts/unify_contract.yaml overlaps section_prompt_contracts/unify_narrative.contract.yaml
- lane_registry lists 7 critical gates not in product_shape SSOT (universal/style/C0)

### Rigor gates absent in production `x2_gate_outputs.json`
- `x2_c0_metrics_artifact_present`
- `x2_c0_support_status_gate`

### Collapse / delete candidates

- DELETE declarative duplicate: apps_rg/prompt_assembly/section_contracts/unify_contract.yaml → fold into section_spec only
- COLLAPSE split lane_runtime + lane_execution into single generic section runner
- ALIGN lane_registry with runtime X2 enumeration OR drop rigor-only ghosts

## ibm_bullets

**Status:** PARTIAL

### Runtime modules (section-tagged)
- `apps_rg/runtime/sections/ibm_bullets_lane.py` (1022 lines)
- `apps_rg/runtime/sections/ibm_bullets_pa.py` (122 lines)
- `apps_rg/runtime/validators/ibm_bullets_x2.py` (727 lines)
- `apps_rg/runtime/judges/ibm_bullets_x1d.py` (88 lines)
- `apps_rg/runtime/dispatch/ibm_bullets_pa.py` (5 lines)

### Repair stack

- foundation proof model constrained rewrite
- distribution / proof-shape Qwen repair
- fact_id_typo_repair

### Duplicate dispatch / quality authority

- foundation proof model constrained rewrite
- distribution / proof-shape Qwen repair (mirrors unify_bullets)

### Duplicated invariants

- lane_registry lists 7 critical gates not in product_shape SSOT (universal/style/C0)
- DEFAULT_DISTRIBUTION constants in unify_bullets_x2 / ibm_bullets_x2 + product_shape + templates

### Rigor gates absent in production `x2_gate_outputs.json`
- `x2_c0_metrics_artifact_present`
- `x2_c0_support_status_gate`
- `x2_ibm_metric_anchor_bullet_ownership`
- `x2_text_claim_coverage_integrity`

### Collapse / delete candidates

- COLLAPSE split lane_runtime + lane_execution into single generic section runner
- ALIGN lane_registry with runtime X2 enumeration OR drop rigor-only ghosts

## ibm_narrative

**Status:** PARTIAL

### Runtime modules (section-tagged)
- `apps_rg/runtime/sections/ibm_narrative_lane.py` (55 lines)
- `apps_rg/runtime/sections/ibm_narrative_lane_defaults.py` (28 lines)
- `apps_rg/runtime/sections/ibm_narrative_lane_execution.py` (776 lines)
- `apps_rg/runtime/sections/ibm_narrative_lane_runtime.py` (566 lines)
- `apps_rg/runtime/sections/ibm_narrative_metric_trim.py` (94 lines)
- `apps_rg/runtime/sections/ibm_narrative_pa.py` (264 lines)
- `apps_rg/runtime/validators/ibm_narrative_x2.py` (794 lines)
- `apps_rg/runtime/judges/ibm_narrative_x1d.py` (81 lines)
- `apps_rg/runtime/dispatch/ibm_narrative_pa.py` (5 lines)

### Repair stack

- companion metric bundle Qwen repair
- fact_id_typo_repair

### Duplicate dispatch / quality authority

- ibm_narrative_lane_runtime + ibm_narrative_lane_execution split (like competencies)
- apply_companion_metric_budget_trim — pre-display trim parallel to X2 word budget
- companion metric bundle Qwen repair

### Duplicated invariants

- lane_registry lists 7 critical gates not in product_shape SSOT (universal/style/C0)

### Rigor gates absent in production `x2_gate_outputs.json`
- `x2_c0_metrics_artifact_present`
- `x2_c0_support_status_gate`
- `x2_ibm_narrative_claim_ledger_clause_decomposition`
- `x2_ibm_narrative_no_meta_disclaimer_in_display`
- `x2_ibm_narrative_requires_finalized_bullets`

### Collapse / delete candidates

- COLLAPSE split lane_runtime + lane_execution into single generic section runner
- DELETE bespoke repair modules; keep shared fact_id_typo_repair + optional one regen flag in section_spec
- ALIGN lane_registry with runtime X2 enumeration OR drop rigor-only ghosts

## Proposed section spec (minimal shape)

- Single YAML/JSON per lane — extends section_product_shape_ssot; not a new contract layer.
- **section_id**: stable lane key
- **product_shape**: display_field, bounds, distribution, sentence/word bands
- **source_authority**: jd_as_proof_allowed, companion_context_authority, upstream_lane_deps
- **section_ownership**: forbidden_cross_section_vocabulary (credential_dump, metric_anchor, etc.)
- **style_forbids**: first_person, em_dash, meta_disclaimer patterns
- **evidence_gates**: bounds + proof + style gate_id list (X2 module ref)
- **allowed_repair**: fact_id_typo_only | one_provider_regen | deterministic_reformat_from_facts | none
- **required_runtime_artifacts**: subset of REQUIRED_RELATIVE + display txt + claim_ledger

## Derivation plan

- **prompt rules / PRODUCT_SHAPE compile block** ← section_spec.product_shape + style_forbids + compile_hints (validate: section_prompt_drift_audit.py (existing))
- **X2 critical gates** ← section_spec.evidence_gates (validate: runtime x2_gate_outputs.json must emit every gate_id; C0 gates via c0_metrics.json)
- **lane_registry rigor** ← codegen or test: lane_registry.LANE_CRITICAL_GATES[section] == spec.evidence_gates | UNIVERSAL (validate: test_section_gate_coverage.py — fail on rigor/runtime drift)
- **runtime receipt expectations** ← section_spec.required_runtime_artifacts (validate: generated_lane_rollup REQUIRED_RELATIVE + full_run_section_status display txt)

## Migration order

- 1. Freeze section_spec schema beside section_product_shape_ssot (rename/extend, no new layer)
- 2. Reconcile rigor_critical vs runtime X2 enumeration for all lanes (exec_summary credential_dump first)
- 3. Collapse duplicate section_contracts YAML into spec
- 4. Delete release-disabled repair (SRFS finalizer, density micro-expansion)
- 5. Merge competencies + ibm_narrative split runtime/execution modules
- 6. Replace per-lane infer_product_quality copies with shared helper (already mostly X2-delegating)
- 7. Trim proof artifact emission to required_runtime_artifacts + operator index
- 8. Derive lane_registry from spec via test/codegen — rigor becomes validator not parallel truth

## Explicit non-claims

- No one-spine convergence achieved by this audit
- No agentic_core changes
- No X2/X3 weakening
- No canonical CLI removal
- No code migration executed in this pass
- No release eligibility certification
