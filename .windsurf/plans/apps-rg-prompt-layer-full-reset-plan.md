# apps_rg Resume Prompt Layer — Full Reset Plan

> **Plan ID**: `apps-rg-prompt-layer-full-reset-plan`  
> **Created**: 2026-05-14  
> **Status**: Not Started  
> **Risk Classification**: T3 — Architectural (prompt layer governance)  
> **Parent Plan**: `apps-rg-pa-w10-5-section-signal-hardening-d9b3e7`  

---

## 1. Executive Summary

This plan governs a **full reset** of the apps_rg resume generation prompt layer. Current prompts are **UNTRUSTED** until proven compliant with the canonical requirements below. This is a gap-analysis and replacement-plan task — **no implementation changes** outside the plan artifact until waves are approved.

### Current State Finding

| Dimension | Finding |
|-----------|---------|
| **Prompt Layer Trust Status** | **UNTRUSTED** — Current prompts violate canonical requirements in multiple dimensions |
| **L2 Architecture** | **MONOLITHIC** — `strategic_tailor_v1` attempts full-resume generation; no section-specific lanes exist |
| **v1/v2 Variant Status** | **MIXED** — Only v1 templates exist; required v2 templates for section-specific workflow do not exist |
| **Section-Specific Lanes** | **ABSENT** — No bounded lanes for strategic planning, headline, bullets, narratives, competencies |
| **Deterministic Copy Enforcement** | **UNVERIFIED** — No runtime wiring proof that locked sections bypass LLM generation |
| **Claim Ledger Output** | **PARTIAL** — Some templates have citation preservation; no structured claim ledger with fact_id mapping |

---

## 2. Canonical Requirements (Source of Truth)

### 2.1 Non-Monolithic L2 Architecture

Resume customization **MUST** split into bounded section-specific lanes:

| # | Lane ID | Purpose | Output Contract |
|---|---------|---------|-------------------|
| 1 | `strategic_tailor_v2` | Planning only — **NO final resume prose** | target_signal_map, jd_requirement_map, briefing_signal_map, allowed_fact_ids_by_section, forbidden_claims, vocabulary_map, gap_list, section_budget |
| 2 | `headline_tailor_v1` | Global resume headline only | X \| Y \| Z (3 pipe-separated segments, 8-11 words total) |
| 3 | `executive_summary.generate_scratch_v1` | Generate from verified facts only | executive_summary, selected_fact_plan, claim_ledger, jd_alignment, gap_notes, self_check |
| 4 | `unify_bullet_tailor_v1` | Unify experience bullets — exactly 6 bullets | 6 bullets with HEAVY/MODERATE/LIGHT_PROTECTED distribution (2/3/1 default) |
| 5 | `unify_position_narrative_v1` | Unify role narrative — exactly 1 sentence | One elevator-style sentence, complements bullets without repetition |
| 6 | `ibm_bullet_tailor_v1` | IBM bullets — exactly 5 bullets | 5 bullets with MODERATE/LIGHT_PROTECTED only (no HEAVY) |
| 7 | `ibm_position_narrative_v1` | IBM narrative — exactly 1 sentence | One sentence, no Unify-specific runtime terms unless IBM facts support |
| 8 | `competency_selector_v2` | Exactly 8 competency categories | Category Label: term, term format; no sentences; excluded_jd_skills list |
| 9 | `final unify_v2` | Consistency pass only — **NO new content authority** | Resolved duplicates, drift fixes, no locked section modification |
| 10 | `unsupported_claim_omission_v2` | Final validator — block unsupported claims | omission_report, claim_ledger validated |
| 11 | `resume_fact_check_v2` | Final validator — fact-check all claims | verification_report, unsupported_claims, suggested_corrections |
| 12 | `docx_manifest_v2` | DOCX render manifest | Section mapping, locked section preservation proof, render directives |

### 2.2 Locked Deterministic Copy Sections

These sections **MUST bypass LLM generation entirely** — byte-for-byte preservation:

| Section | Fields Locked |
|---------|---------------|
| InsurTech role | company, location, title, dates, narrative, bullets |
| EY role | company, location, title, dates, narrative, bullets |
| Early Career role | company, location, title, dates, bullets |
| Education | institution, degree, dates, GPA (if present) |
| Certifications & Credentials | certification name, issuer, date, credential ID |

**Locked deterministic copy fields across ALL roles:**
- `company_name` — never rewritten
- `location` — never rewritten
- `historical_title` — never rewritten
- `dates` — never rewritten

### 2.3 Global Prompt Law

Every prompt **MUST** enforce:

| Rule | Violation Consequence |
|------|----------------------|
| JD and company briefing are **targeting context only** | If JD becomes proof → FAIL |
| JD and company briefing are **never proof of candidate experience** | If briefing supports claims → FAIL |
| Every material claim **must trace to candidate_fact_map, verified_skill_inventory, or base resume facts** | If untraced claim present → FAIL |
| Unsupported JD requirements are **reported as gaps, not fabricated** | If gap filled with fabrication → FAIL |
| No unsupported tools, frameworks, platforms, model names, compliance terms, industries, certifications, clients, metrics, revenue, team size, dates, titles, or outcomes | If any unsupported present → FAIL |
| **No em dash** — use comma or restructure | If em dash present → FAIL |
| Do not copy **more than 4 consecutive words** from the JD | If >4 consecutive JD words → FAIL |
| Preserve base resume rigor, density, seniority, technical richness, commercial credibility, and human-written tone | If tone flattened to generic leadership → FAIL |
| Do not flatten technical proof into generic leadership language | If technical specifics lost → FAIL |
| Do not keyword stuff | If JD keyword stuffing detected → FAIL |

### 2.4 Required Output Schema Fields

Every generated section **MUST** emit:

| Field | Required In |
|-------|---------------|
| `claim_ledger` — list of claims with source_fact_ids | All generation prompts (summary, bullets, narratives, competencies) |
| `gap_notes` — list of unsupported JD requirements | All generation prompts |
| `change_log` — record of modifications made | All generation prompts |
| `self_check` — prompt self-verification results | All generation prompts |
| `selected_fact_plan` — evidence-first selection before drafting | executive_summary only |
| `jd_alignment` — explicit mapping to JD requirements | executive_summary only |

---

## 3. Current Prompt Inventory (W0)

### 3.1 Template Files Present

| Template File | Registry ID | Status | Canonical Status |
|--------------|---------------|--------|------------------|
| `strategic_tailor_v1.yaml` | strategic_tailor_v1 | **ACTIVE** — Primary E3 template | **FAIL** — Monolithic full-resume generation |
| `tailor_existing_v1.yaml` | tailor_existing_v1 | Present, likely unused | **UNKNOWN** — No runtime wiring proof |
| `generate_scratch_v1.yaml` | generate_scratch_v1 | Present | **UNKNOWN** — No runtime wiring proof |
| `enhance_current_v1.yaml` | enhance_current_v1 | Present | **UNKNOWN** — No runtime wiring proof |
| `resume_fact_check_v1.yaml` | resume_fact_check_v1 | **ACTIVE** — E4 heal | **PARTIAL** — No claim_ledger structured output |
| `unsupported_claim_omission_v1.yaml` | unsupported_claim_omission_v1 | **ACTIVE** — E4 heal | **PARTIAL** — No claim_ledger structured output |
| `bullet_diversity_repair_v1.yaml` | bullet_diversity_repair_v1 | Present | **PARTIAL** — No section-scoped fact_id binding |
| `unify_v1.yaml` | unify_v1 | Present | **FAIL** — Monolithic consistency pass |
| `docx_manifest_v1.yaml` | docx_manifest_v1 | **ACTIVE** — E5 exit | **PARTIAL** — No locked section preservation proof |

### 3.2 Runtime Wiring Status

| Binding | Location | Status | Evidence |
|---------|----------|--------|----------|
| PA Binding | `agentic_core/prompt_governance/apps_rg_pa_binding.py` — LEGACY_SHIM | **MIGRATION REQUIRED** | Re-exports from non-existent `apps_rg/runtime/bindings/pa_binding.py` |
| L2 Binding | `agentic_core/L2_execution/apps_rg_l2_binding.py` — LEGACY_SHIM | **MIGRATION REQUIRED** | Re-exports from non-existent `apps_rg/runtime/bindings/l2_binding.py` |
| C0 Binding | `apps_rg/runtime/bindings/c0_binding.py` | **PRESENT** — Active | W5 implementation with GateVerdict construction |
| Exit Binding | `apps_rg/runtime/bindings/exit_binding.py` | **PRESENT** — Active | W4 implementation |

### 3.3 Section Contracts Present

| Contract File | Coverage | Status |
|--------------|----------|--------|
| `section_contracts/executive_summary_contract.yaml` | Executive summary only | **PARTIAL** — No v2 planning-only separation |
| `section_contracts/unify_contract.yaml` | Unify experience section | **PARTIAL** — No separate bullet/narrative lanes |
| `section_contracts/competencies_contract.yaml` | Competencies section | **PARTIAL** — No 8-category enforcement |

### 3.4 Tests Present

| Test File | Coverage | Status |
|-----------|----------|--------|
| `test_w8_pa_templates_e4_e5.py` | Template resolution, parsing, slot presence | **PARTIAL** — Tests structure only, not content compliance |
| `test_w6_pa_compiler.py` | PA compiler functionality | **PARTIAL** — Tests compilation, not prompt correctness |
| `test_w7_pa_compiler_negative_controls.py` | Override attempt detection | **PARTIAL** — Tests slot ordering, not prompt content |
| `test_apps_rg_pa_tiered_prompt.py` | Tiered prompt authority | **PARTIAL** — Tests tiering, not section-specific lanes |
| `test_w10_5_pa_signal_hardening.py` | Signal hardening (W10.5 plan) | **PARTIAL** — Tests PA boundaries, not prompt reset |

---

## 4. Gap Matrix

| # | Prompt/Workflow Requirement | Current Repo Behavior | Status | Evidence Path | Replacement Needed | Required New Canonical Prompt | Required Routing Change | Required Test | Risk if Not Fixed |
|---|----------------------------|----------------------|--------|---------------|-------------------|------------------------------|------------------------|---------------|-------------------|
| 1 | `strategic_tailor_v2` — planning only, no final prose | `strategic_tailor_v1` generates full resume prose | **FAIL** | `templates/strategic_tailor_v1.yaml` I0 section | YES | `strategic_tailor_v2.yaml` | New registry entry, retire v1 | `test_strategic_tailor_v2_no_prose.py` | **CRITICAL** — Violates non-monolithic architecture |
| 2 | `strategic_tailor_v2` — emits target_signal_map, jd_requirement_map, briefing_signal_map | `strategic_tailor_v1` emits full resume JSON | **FAIL** | `templates/strategic_tailor_v1.yaml` R0 schema | YES | `strategic_tailor_v2.yaml` with planning schema | Registry update | `test_strategic_tailor_v2_outputs.py` | **CRITICAL** — No planning-only lane |
| 3 | `headline_tailor_v1` — X \| Y \| Z format, 8-11 words | No headline-specific template exists | **FAIL** | No `headline_tailor_v1.yaml` | YES | `headline_tailor_v1.yaml` | New registry entry, L2 lane | `test_headline_format_compliance.py` | **HIGH** — Missing required lane |
| 4 | `headline_tailor_v1` — no metrics, no company names, no target company | No headline template to verify | **FAIL** | Absent | YES | `headline_tailor_v1.yaml` with constraints | L2 lane wiring | `test_headline_constraints.py` | **HIGH** |
| 5 | `executive_summary.generate_scratch_v1` — evidence-first, selected_fact_plan | `strategic_tailor_v1` summary section generates without explicit fact selection | **PARTIAL** | `templates/strategic_tailor_v1.yaml` I0 executive_summary section mentions evidence but no selected_fact_plan output | YES | `executive_summary.generate_scratch_v1.yaml` | Replace v1 summary section, new lane | `test_executive_summary_evidence_first.py` | **CRITICAL** — No evidence-first workflow |
| 6 | `executive_summary.generate_scratch_v1` — no target_words, no max_words, fit-based length | `strategic_tailor_v1` has "max 4 lines / max 60 words" | **FAIL** | `templates/generate_scratch_v1.yaml` I0: "LENGTH: max 4 lines / max 60 words" | YES | `executive_summary.generate_scratch_v1.yaml` without word count | Remove word count enforcement | `test_executive_summary_no_word_count.py` | **HIGH** — Violates fit-based length law |
| 7 | `executive_summary.generate_scratch_v1` — claim_ledger, selected_fact_plan, jd_alignment, gap_notes, self_check | No structured claim_ledger output in any template | **FAIL** | All templates lack structured claim_ledger in R0 | YES | `executive_summary.generate_scratch_v1.yaml` with full schema | Registry update, JSON schema update | `test_executive_summary_output_schema.py` | **CRITICAL** — No evidence traceability |
| 8 | `unify_bullet_tailor_v1` — exactly 6 bullets | `strategic_tailor_v1` experience section has no bullet count enforcement | **FAIL** | `templates/strategic_tailor_v1.yaml` I0 experience: no bullet count constraint | YES | `unify_bullet_tailor_v1.yaml` | New section-specific lane | `test_unify_bullet_count.py` | **CRITICAL** — Bullet count not enforced |
| 9 | `unify_bullet_tailor_v1` — HEAVY/MODERATE/LIGHT_PROTECTED distribution 2/3/1 | No rewrite distribution guidance in templates | **FAIL** | No distribution rules found | YES | `unify_bullet_tailor_v1.yaml` with distribution rules | L2 lane, strategic_tailor_plan integration | `test_unify_bullet_distribution.py` | **HIGH** |
| 10 | `unify_bullet_tailor_v1` — max 3 HEAVY, min 1 LIGHT_PROTECTED | No distribution constraints | **FAIL** | Absent | YES | `unify_bullet_tailor_v1.yaml` with constraints | Registry update | `test_unify_distribution_bounds.py` | **HIGH** |
| 11 | `unify_bullet_tailor_v1` — must not write Unify narrative | `strategic_tailor_v1` writes full experience section including narrative | **FAIL** | `templates/strategic_tailor_v1.yaml` I0 experience: includes narrative guidance | YES | `unify_bullet_tailor_v1.yaml` (bullets only) | Separate lane, no narrative | `test_unify_no_narrative.py` | **HIGH** |
| 12 | `unify_position_narrative_v1` — runs after bullet fact check | No separate narrative lane; no fact-check ordering | **FAIL** | `resume_fact_check_v1.yaml` exists but no lane ordering | YES | `unify_position_narrative_v1.yaml` | L2 lane ordering: bullets → fact_check → narrative | `test_unify_narrative_ordering.py` | **HIGH** |
| 13 | `unify_position_narrative_v1` — exactly one elevator-style sentence | No narrative-specific template | **FAIL** | Absent | YES | `unify_position_narrative_v1.yaml` | New lane | `test_unify_narrative_one_sentence.py` | **HIGH** |
| 14 | `unify_position_narrative_v1` — must not repeat bullet metrics | No anti-repetition constraint specific to narrative | **PARTIAL** | `templates/unify_v1.yaml` has consistency guidance but not specific | YES | `unify_position_narrative_v1.yaml` with anti-repetition | L2 lane | `test_unify_narrative_no_repeat.py` | **MEDIUM** |
| 15 | `ibm_bullet_tailor_v1` — exactly 5 bullets | No IBM-specific bullet template | **FAIL** | No IBM-specific templates exist | YES | `ibm_bullet_tailor_v1.yaml` | New lane | `test_ibm_bullet_count.py` | **HIGH** — Missing required lane |
| 16 | `ibm_bullet_tailor_v1` — no HEAVY rewrites, 3 MODERATE/2 LIGHT_PROTECTED | No IBM-specific rewrite rules | **FAIL** | Absent | YES | `ibm_bullet_tailor_v1.yaml` with conservative rules | Registry, L2 lane | `test_ibm_conservative_rewrite.py` | **HIGH** |
| 17 | `ibm_bullet_tailor_v1` — no Unify runtime terms (GraphRAG, multi-agent, etc.) | No IBM-specific term filtering | **FAIL** | Absent | YES | `ibm_bullet_tailor_v1.yaml` with term blacklist | L2 lane | `test_ibm_no_unify_terms.py` | **HIGH** — Cross-role contamination risk |
| 18 | `ibm_position_narrative_v1` — runs after IBM bullet fact check | No IBM narrative lane | **FAIL** | Absent | YES | `ibm_position_narrative_v1.yaml` | L2 lane ordering | `test_ibm_narrative_ordering.py` | **HIGH** |
| 19 | `competency_selector_v2` — exactly 8 competency categories | `strategic_tailor_v1` competencies has no count enforcement | **FAIL** | `templates/strategic_tailor_v1.yaml` I0 competencies: no count | YES | `competency_selector_v2.yaml` | New lane | `test_competency_count.py` | **HIGH** |
| 20 | `competency_selector_v2` — Category: terms format, no sentences | No format enforcement | **FAIL** | Current templates don't specify format | YES | `competency_selector_v2.yaml` with format rules | Registry, L2 lane | `test_competency_format.py` | **HIGH** |
| 21 | `competency_selector_v2` — excluded_jd_skills list | No JD skill exclusion output | **FAIL** | Absent | YES | `competency_selector_v2.yaml` with excluded list | Registry | `test_competency_jd_exclusion.py` | **HIGH** |
| 22 | `competency_selector_v2` — no bullet restatement, source_fact_ids | No anti-repetition or source tracking | **FAIL** | Current templates lack this | YES | `competency_selector_v2.yaml` | Registry | `test_competency_no_repetition.py` | **HIGH** |
| 23 | `final unify_v2` — consistency pass only, no new content | `unify_v1.yaml` claims consistency but has preservation issues | **PARTIAL** | `templates/unify_v1.yaml` has preservation check but no locked section enforcement | YES | `final unify_v2.yaml` | Replace v1, L2 lane | `test_final_unify_no_new_content.py` | **HIGH** |
| 24 | `final unify_v2` — must not modify locked deterministic copy sections | No locked section enforcement in unify | **FAIL** | `templates/unify_v1.yaml` has preservation_check but no locked section list | YES | `final unify_v2.yaml` with locked list | L2 lane | `test_final_unify_locked_sections.py` | **CRITICAL** — Locked section bypass not enforced |
| 25 | `resume_fact_check_v2` — claim ledger validation | `resume_fact_check_v1.yaml` has verification_report but no structured claim_ledger | **PARTIAL** | `templates/resume_fact_check_v1.yaml` R0: verification_report, unsupported_claims, suggested_corrections — no claim_ledger | YES | `resume_fact_check_v2.yaml` | Replace v1 | `test_fact_check_claim_ledger.py` | **HIGH** |
| 26 | `unsupported_claim_omission_v2` — omission report, claim ledger | `unsupported_claim_omission_v1.yaml` has omission but no claim_ledger | **PARTIAL** | `templates/unsupported_claim_omission_v1.yaml` R0: corrected_resume, omitted_claims, gap_notes — no claim_ledger | YES | `unsupported_claim_omission_v2.yaml` | Replace v1 | `test_omission_claim_ledger.py` | **HIGH** |
| 27 | `docx_manifest_v2` — locked section preservation proof | `docx_manifest_v1.yaml` has content_preservation but no locked section proof | **PARTIAL** | `templates/docx_manifest_v1.yaml` R0: content_preservation counts — no locked field verification | YES | `docx_manifest_v2.yaml` with locked proof | Replace v1 | `test_docx_locked_preservation.py` | **HIGH** |
| 28 | Locked deterministic copy — InsurTech byte-for-byte | No explicit locked section template | **FAIL** | No section-specific copy template | YES | `locked_copy_insurtech.yaml` or runtime wiring | L2 lane ordering | `test_insurtech_byte_for_byte.py` | **CRITICAL** — Resume integrity violation |
| 29 | Locked deterministic copy — EY byte-for-byte | No explicit locked section template | **FAIL** | Absent | YES | `locked_copy_ey.yaml` or runtime wiring | L2 lane | `test_ey_byte_for_byte.py` | **CRITICAL** |
| 30 | Locked deterministic copy — Early Career byte-for-byte | No explicit locked section template | **FAIL** | Absent | YES | `locked_copy_early_career.yaml` or runtime wiring | L2 lane | `test_early_career_byte_for_byte.py` | **CRITICAL** |
| 31 | Locked deterministic copy — Education byte-for-byte | No explicit locked section template | **FAIL** | Absent | YES | `locked_copy_education.yaml` or runtime wiring | L2 lane | `test_education_byte_for_byte.py` | **CRITICAL** |
| 32 | Locked deterministic copy — Certifications byte-for-byte | No explicit locked section template | **FAIL** | Absent | YES | `locked_copy_certifications.yaml` or runtime wiring | L2 lane | `test_certifications_byte_for_byte.py` | **CRITICAL** |
| 33 | Company/location/title/dates preserved for all roles | No role header field preservation proof | **FAIL** | Templates don't specify locked field handling | YES | Section templates with locked field contracts | L2 lane | `test_role_headers_preserved.py` | **CRITICAL** |
| 34 | No em dash | `forbidden_ai_phrases.yaml` mentions em dash but no runtime enforcement | **PARTIAL** | `forbidden_ai_phrases.yaml`: "DO NOT PRODUCE: Em dash character" | NO | Update templates with explicit rejection | Add em_dash scanner to L2 or template S0 | `test_no_em_dash.py` | **MEDIUM** |
| 35 | No more than 4 consecutive JD words | No JD word counting in templates | **FAIL** | Absent | YES | Update all generation templates with 4-word constraint | L2 lane or template I0 | `test_jd_word_limit.py` | **HIGH** — JD mimicry risk |
| 36 | JD cannot become proof | `strategic_tailor_v1.yaml` S0 has oath but no runtime verification | **PARTIAL** | `templates/strategic_tailor_v1.yaml` S0: "JD/TARGET CONTEXT IS NOT PROOF" | NO | Strengthen with explicit claim tracing | Add claim tracing to L2 | `test_jd_not_proof.py` | **HIGH** |
| 37 | Briefing cannot support candidate claim | Same as above — oath present, no verification | **PARTIAL** | S0 oath exists | NO | Add briefing claim tracing | L2 verification | `test_briefing_not_proof.py` | **HIGH** |
| 38 | Unsupported JD-only skill excluded from competencies | No explicit exclusion output | **FAIL** | `strategic_tailor_v1.yaml` I0 competencies: "GAP_MARKING_REQUIRED" but no excluded list output | YES | `competency_selector_v2.yaml` | Registry update | `test_jd_skill_exclusion.py` | **HIGH** |
| 39 | Duplicate keyword variants collapsed | No variant collapsing logic | **FAIL** | Absent | YES | `competency_selector_v2.yaml` with variant map | L2 lane | `test_keyword_variant_collapse.py` | **MEDIUM** |
| 40 | Every competency term maps to source_fact_ids | No source tracking in competencies | **FAIL** | Absent | YES | `competency_selector_v2.yaml` with source tracking | Registry, L2 lane | `test_competency_source_mapping.py` | **HIGH** |
| 41 | agentic_core diff is empty | Not applicable to this plan | **PASS** | This plan touches only apps_rg | N/A | N/A | N/A | N/A | N/A |

### Gap Matrix Summary Counts

| Status | Count | Percentage |
|--------|-------|------------|
| **PASS** | 1 | 2.4% |
| **PARTIAL** | 8 | 19.5% |
| **FAIL** | 32 | 78.1% |
| **UNKNOWN** | 0 | 0% |

**Total Gaps**: 41 evaluated items  
**Total Replacements Required**: 24 new/updated templates  
**Total Tests Required**: 40 new test files

---

## 5. Prompt Retirement/Replacement Table

| Current Template | Action | Replacement | Migration Path |
|-----------------|--------|-------------|----------------|
| `strategic_tailor_v1.yaml` | **RETIRE** | `strategic_tailor_v2.yaml` (planning-only) | W1: Create v2; W3: Update routing; W8: Retire v1 after v2 proven |
| `tailor_existing_v1.yaml` | **RETIRE** | None — use `strategic_tailor_v2` planning | W1: Mark deprecated |
| `generate_scratch_v1.yaml` | **RETIRE** | `strategic_tailor_v2` + section lanes | W1: Mark deprecated |
| `enhance_current_v1.yaml` | **RETIRE** | None — use `strategic_tailor_v2` planning | W1: Mark deprecated |
| `resume_fact_check_v1.yaml` | **REPLACE** | `resume_fact_check_v2.yaml` | W7: Create v2; W8: Retire v1 after tests pass |
| `unsupported_claim_omission_v1.yaml` | **REPLACE** | `unsupported_claim_omission_v2.yaml` | W7: Create v2; W8: Retire v1 after tests pass |
| `bullet_diversity_repair_v1.yaml` | **QUARANTINE** | `bullet_diversity_repair_v2.yaml` (section-scoped) | W6: Create section-specific repair; W8: Retire v1 |
| `unify_v1.yaml` | **RETIRE** | `final unify_v2.yaml` (consistency-only) | W3: Create v2; W8: Retire v1 |
| `docx_manifest_v1.yaml` | **REPLACE** | `docx_manifest_v2.yaml` | W7: Create v2; W8: Retire v1 |

### New Templates Required (Not Present)

| New Template | Purpose | Wave |
|-------------|---------|------|
| `headline_tailor_v1.yaml` | X \| Y \| Z headline | W2 |
| `executive_summary.generate_scratch_v1.yaml` | Evidence-first summary | W2 |
| `unify_bullet_tailor_v1.yaml` | Unify 6 bullets | W2 |
| `unify_position_narrative_v1.yaml` | Unify 1-sentence narrative | W2 |
| `ibm_bullet_tailor_v1.yaml` | IBM 5 bullets | W2 |
| `ibm_position_narrative_v1.yaml` | IBM 1-sentence narrative | W2 |
| `competency_selector_v2.yaml` | 8-category competencies | W2 |

---

## 6. Wave Structure

| Wave | Focus | Deliverables | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-------|--------------|---------------|---------------|--------|------------------|
| W0 | Current Prompt Inventory (COMPLETE) | Gap matrix, inventory list, finding report | ~8k | Files readable | ✅ DONE | All 9 templates inventoried, 41 gaps identified |
| W1 | Prompt Retirement Strategy | Retirement table, deprecation markers, migration timeline | ~5k | Templates editable | **Not Started** | All v1 templates marked retire/replace/quarantine |
| W2 | Canonical Prompt Contracts (v2) | `strategic_tailor_v2.yaml`, `headline_tailor_v1.yaml`, `executive_summary.generate_scratch_v1.yaml`, `unify_bullet_tailor_v1.yaml`, `unify_position_narrative_v1.yaml`, `ibm_bullet_tailor_v1.yaml`, `ibm_position_narrative_v1.yaml`, `competency_selector_v2.yaml` | ~25k | Clean slate prompt authoring | **Not Started** | 8 new templates with canonical contracts |
| W3 | Non-Monolithic L2 Routing | L2 lane definitions, ordering enforcement, registry updates | ~8k | Runtime bindings exist | **Not Started** | 12-step lane order enforced |
| W4 | Deterministic Copy Enforcement | Locked section definitions, byte-for-byte preservation, render-time validation | ~6k | DOCX render path known | **Not Started** | 5 locked sections enforced |
| W5 | Claim Ledger and Fact Boundaries | Claim ledger schema, gap_notes output, JD-as-target enforcement | ~8k | Schema definitions available | **Not Started** | All generation prompts emit claim_ledger |
| W6 | Competency Selector Reset | 8-category taxonomy, keyword collapsing, JD exclusion | ~6k | v2 competency template created | **Not Started** | All competency requirements enforced |
| W7 | Final Validators and DOCX Manifest | `resume_fact_check_v2.yaml`, `unsupported_claim_omission_v2.yaml`, `docx_manifest_v2.yaml` | ~8k | v1 templates as reference | **Not Started** | 3 v2 validator templates |
| W8 | CI and Regression Proof | 40 test files, coverage gates, regression suite | ~15k | pytest infrastructure | **Not Started** | All 40 tests pass, ≥80% coverage |

---

## 7. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|---------------|-------------|--------|
| W0 | Current State Inventory | 9 templates, 3 contracts, 5 test files | Large file reads, scattered definitions | ~8k | ✅ DONE |
| W1.P1 | Retirement Markers | 4 template files | Adding deprecation without breaking existing | ~2k | Not Started |
| W1.P2 | Migration Timeline | Plan document | Sequencing dependencies | ~1k | Not Started |
| W1.P3 | Registry Updates | `prompt_registry.yaml` | Flagging templates for retirement | ~2k | Not Started |
| W2.P1 | Strategic Tailor v2 | `strategic_tailor_v2.yaml` | Planning-only constraint | ~6k | Not Started |
| W2.P2 | Headline Template | `headline_tailor_v1.yaml` | X \| Y \| Z format enforcement | ~2k | Not Started |
| W2.P3 | Executive Summary | `executive_summary.generate_scratch_v1.yaml` | Evidence-first workflow | ~4k | Not Started |
| W2.P4 | Unify Bullets | `unify_bullet_tailor_v1.yaml` | 6 bullet count, distribution rules | ~4k | Not Started |
| W2.P5 | Unify Narrative | `unify_position_narrative_v1.yaml` | 1-sentence constraint | ~2k | Not Started |
| W2.P6 | IBM Bullets | `ibm_bullet_tailor_v1.yaml` | 5 bullet count, conservative rules | ~3k | Not Started |
| W2.P7 | IBM Narrative | `ibm_position_narrative_v1.yaml` | Term filtering | ~2k | Not Started |
| W2.P8 | Competencies v2 | `competency_selector_v2.yaml` | 8-category constraint | ~4k | Not Started |
| W3.P1 | L2 Lane Definitions | `l2_binding.py` (new) | Lane ordering enforcement | ~3k | Not Started |
| W3.P2 | Registry Routing | `prompt_registry.yaml` updates | Section-to-lane mapping | ~2k | Not Started |
| W3.P3 | Lane Orchestration | L2 execution order | 12-step ordering | ~3k | Not Started |
| W4.P1 | Locked Section Definitions | Locked copy contracts | Section identification | ~2k | Not Started |
| W4.P2 | Byte-for-Byte Tests | 5 test files | Preservation verification | ~3k | Not Started |
| W4.P3 | Render Validation | DOCX manifest validation | Mutation detection | ~1k | Not Started |
| W5.P1 | Claim Ledger Schema | Schema definitions | Output structure | ~2k | Not Started |
| W5.P2 | Gap Notes Output | Template updates | Unsupported requirement handling | ~3k | Not Started |
| W5.P3 | JD-as-Target Enforcement | Template S0/I0 updates | Proof boundary | ~3k | Not Started |
| W6.P1 | 8-Category Taxonomy | Competency categories | Category definition | ~2k | Not Started |
| W6.P2 | Keyword Collapsing | Variant mapping | Duplicate detection | ~2k | Not Started |
| W6.P3 | JD Skill Exclusion | Exclusion list output | Filtering logic | ~2k | Not Started |
| W7.P1 | Fact Check v2 | `resume_fact_check_v2.yaml` | Claim ledger integration | ~3k | Not Started |
| W7.P2 | Claim Omission v2 | `unsupported_claim_omission_v2.yaml` | Ledger integration | ~3k | Not Started |
| W7.P3 | DOCX Manifest v2 | `docx_manifest_v2.yaml` | Locked section proof | ~2k | Not Started |
| W8.P1 | Strategic Tailor Tests | 4 test files | Planning-only validation | ~4k | Not Started |
| W8.P2 | Headline Tests | 2 test files | Format compliance | ~2k | Not Started |
| W8.P3 | Executive Summary Tests | 4 test files | Evidence-first workflow | ~4k | Not Started |
| W8.P4 | Bullet/Narrative Tests | 8 test files | Count, distribution, ordering | ~6k | Not Started |
| W8.P5 | IBM Tests | 4 test files | Conservative rewrite, term filtering | ~4k | Not Started |
| W8.P6 | Competency Tests | 6 test files | 8-category, exclusion, source mapping | ~4k | Not Started |
| W8.P7 | Validator Tests | 6 test files | Claim ledger, omission, DOCX | ~4k | Not Started |
| W8.P8 | Integration Tests | 6 test files | End-to-end lanes | ~4k | Not Started |

---

## 8. Definition of Done

| DoD | Description | Verification |
|-----|-------------|--------------|
| DoD-1 | All 12 canonical prompt templates exist and resolve from registry | `test_all_templates_resolve.py` passes |
| DoD-2 | `strategic_tailor_v2` emits planning outputs only (no resume prose) | `test_strategic_tailor_v2_no_prose.py` passes |
| DoD-3 | Headline format is X \| Y \| Z with 8-11 words | `test_headline_format_compliance.py` passes |
| DoD-4 | Executive summary has no word count enforcement, uses fit-based length | `test_executive_summary_no_word_count.py` passes |
| DoD-5 | Unify bullets output exactly 6 bullets with correct distribution | `test_unify_bullet_count.py`, `test_unify_bullet_distribution.py` pass |
| DoD-6 | IBM bullets output exactly 5 bullets with no HEAVY rewrites | `test_ibm_bullet_count.py`, `test_ibm_conservative_rewrite.py` pass |
| DoD-7 | Competencies output exactly 8 categories with excluded_jd_skills | `test_competency_count.py`, `test_competency_jd_exclusion.py` pass |
| DoD-8 | All generation prompts emit claim_ledger, gap_notes, self_check | `test_claim_ledger_present.py` passes for all lanes |
| DoD-9 | Locked sections (InsurTech, EY, Early Career, Education, Certs) are byte-for-byte preserved | `test_*_byte_for_byte.py` pass |
| DoD-10 | No em dash in any prompt output | `test_no_em_dash.py` passes |
| DoD-11 | No more than 4 consecutive JD words in any output | `test_jd_word_limit.py` passes |
| DoD-12 | L2 lane ordering enforces: planning → headline → summary → bullets → fact_check → narrative → ... → final validators | `test_l2_lane_ordering.py` passes |
| DoD-13 | `agentic_core` diff is empty (no core changes) | `git diff agentic_core/` returns empty |
| DoD-14 | All 40 new tests pass, ≥80% line coverage | `pytest tests/_apps_contract/ -v` passes |

### Verification vs Deferral Table

| Verification | Deferred |
|--------------|----------|
| W0 inventory complete | W1-W8 implementation (requires wave-by-wave approval) |
| Gap matrix with 41 items | Individual template authoring (deferred to waves) |
| Retirement table defined | Runtime wiring migration (W3 scope) |
| Test list defined | Test implementation (W8 scope) |
| No agentic_core changes in plan | Implementation changes outside plan (blocked until waves approved) |

---

## 9. Top 5 Highest-Risk Prompt Gaps

| Rank | Gap | Risk | Mitigation |
|------|-----|------|------------|
| 1 | **Monolithic `strategic_tailor_v1`** — Generates full resume in one prompt, violating non-monolithic architecture | Resume integrity failures, untraceable claims, locked section mutation | W2: Create `strategic_tailor_v2` planning-only; W3: Implement section lanes |
| 2 | **No section-specific lanes** — Missing headline, bullet, narrative, competency separation | Cross-section contamination, repetition, metric inconsistencies | W2: Create 7 section-specific templates; W3: Wire L2 lanes |
| 3 | **No locked section enforcement** — InsurTech, EY, Early Career, Education, Certs not protected from LLM modification | Resume fraud, experience falsification | W4: Implement deterministic copy with byte-for-byte preservation |
| 4 | **No claim ledger output** — No structured evidence traceability | Unverifiable claims, no fact-checking possible | W5: Add claim_ledger to all generation prompts; W7: Implement v2 validators |
| 5 | **JD can become proof** — Oath present but no runtime verification of claim sources | JD mimicry, unsupported claims presented as experience | W5: Add claim tracing; W7: Strengthen fact check validators |

---

## 10. Files Inspected

### Templates (9 files)
1. `apps_rg/prompt_assembly/templates/strategic_tailor_v1.yaml`
2. `apps_rg/prompt_assembly/templates/tailor_existing_v1.yaml`
3. `apps_rg/prompt_assembly/templates/generate_scratch_v1.yaml`
4. `apps_rg/prompt_assembly/templates/enhance_current_v1.yaml`
5. `apps_rg/prompt_assembly/templates/resume_fact_check_v1.yaml`
6. `apps_rg/prompt_assembly/templates/unsupported_claim_omission_v1.yaml`
7. `apps_rg/prompt_assembly/templates/bullet_diversity_repair_v1.yaml`
8. `apps_rg/prompt_assembly/templates/unify_v1.yaml`
9. `apps_rg/prompt_assembly/templates/docx_manifest_v1.yaml`

### Contracts and Configuration (6 files)
10. `apps_rg/prompt_assembly/prompt_registry.yaml`
11. `apps_rg/prompt_assembly/contracts.py`
12. `apps_rg/prompt_assembly/compiler.py`
13. `apps_rg/prompt_assembly/section_contracts/executive_summary_contract.yaml`
14. `apps_rg/prompt_assembly/section_contracts/unify_contract.yaml`
15. `apps_rg/prompt_assembly/section_contracts/competencies_contract.yaml`

### Runtime Bindings (4 files)
16. `apps_rg/runtime/bindings/c0_binding.py`
17. `apps_rg/runtime/bindings/exit_binding.py`
18. `agentic_core/prompt_governance/apps_rg_pa_binding.py` (LEGACY_SHIM)
19. `agentic_core/L2_execution/apps_rg_l2_binding.py` (LEGACY_SHIM)

### Tests (5 files)
20. `tests/_apps_contract/test_w8_pa_templates_e4_e5.py`
21. `tests/_apps_contract/test_w6_pa_compiler.py`
22. `tests/_apps_contract/test_w7_pa_compiler_negative_controls.py`
23. `tests/_apps_contract/test_apps_rg_pa_tiered_prompt.py`
24. `tests/_apps_contract/test_w10_5_pa_signal_hardening.py`

### Rubrics and Configuration (2 files)
25. `apps_rg/prompt_assembly/rubrics/section_quality_rubrics.yaml`
26. `apps_rg/prompt_assembly/examples/unify_examples.yaml`

---

## 11. Confirmations

| Confirmation | Status |
|--------------|--------|
| **No agentic_core changes** in this plan | ✅ CONFIRMED — Plan touches only apps_rg |
| **No implementation changes** outside plan artifact | ✅ CONFIRMED — Only plan file created |
| **Full reset approach** — existing prompts untrusted | ✅ CONFIRMED — Gap matrix marks most as FAIL/PARTIAL |
| **Gap matrix with 41 items** | ✅ CONFIRMED — See section 4 |
| **Retirement/replacement table** | ✅ CONFIRMED — See section 5 |
| **Wave list with 8 waves** | ✅ CONFIRMED — See section 6 |
| **Files inspected list** | ✅ CONFIRMED — 26 files listed |
| **Top 5 highest-risk gaps identified** | ✅ CONFIRMED — See section 9 |

---

## 12. Next Steps

1. **Review this plan** — Approve wave structure and gap analysis
2. **W1 execution** — Upon approval, begin Prompt Retirement and Replacement Strategy
3. **Wave-by-wave authorization** — Each wave requires explicit go-ahead before implementation
4. **Test-first development** — Each template requires tests before implementation
5. **No agentic_core changes** — All work remains in apps_rg

---

*Plan created per user request: "Do a full reset of the apps_rg resume prompt layer"*  
*Hard stance applied: Current prompts are UNTRUSTED until proven compliant*  
*No code changes made outside this plan artifact*

