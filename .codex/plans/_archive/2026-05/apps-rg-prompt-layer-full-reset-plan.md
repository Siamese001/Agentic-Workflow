# apps_rg Resume Prompt Layer — Full Reset Plan

> **Plan ID**: `apps-rg-prompt-layer-full-reset-plan`  
> **Created**: 2026-05-14  
> **Updated**: 2026-05-14 (Hardened)  
> **Status**: Not Started  
> **Risk Classification**: T3 — Architectural (prompt layer governance)  
> **Parent Plan**: `apps-rg-pa-w10-5-section-signal-hardening-d9b3e7`  
> **Hardening Level**: v4 — FINAL EXECUTABLE (JSON-SSOT, STOP 0-15, Temperature, Metrics)  

---

## 1. Executive Summary

This plan governs a **full reset** of the apps_rg resume generation prompt layer. Current prompts are **UNTRUSTED** until proven compliant with the canonical requirements below. This is a gap-analysis and replacement-plan task — **no implementation changes** outside the plan artifact until waves are approved.

### Hardening Rules (Non-Negotiable)

| Rule | Enforcement |
|------|-------------|
| **W1 Plan-Only** | W1 defines retirement strategy only — NO editing of existing YAML templates |
| **No agentic_core Changes** | Zero edits to `agentic_core/` including legacy shims; app-local bindings created under `apps_rg/runtime/bindings/` only |
| **Monolith Decommission Gate** | CI fails if any runtime path invokes monolithic full-resume prompt for generation |
| **Deterministic Copy Bypass** | Locked sections bypass L2 model generation entirely — no `locked_copy_*.yaml` prompts |
| **Receipt Per Wave** | Each wave produces receipt artifact with diff confirmation, test results, monolith status |
| **Test-First Grouping** | 40 test cases grouped into 8 domain files, not 40 separate files |
| **Tightened DoD** | 22 DoD items enforce section-specific lanes, claim ledgers, locked section preservation |
| **Base Resume SSOT** | Canonical frozen base resume **JSON** is runtime SSOT; DOCX only for creation/validation; refresh is versioned workflow |
| **Canonical JSON Paths** | `apps_rg/resume/base/amit_ayer_base_resume_v1.json` + `active_base_resume_pointer.json` |
| **STOP 0-15 Gates** | 16 mandatory stop points with receipts; no next wave until prior STOP is PASS |
| **Lane Temperature** | Per-lane temperature profiles; calibrated via sweep; highest passing temp selected |
| **Section Metrics** | Global metric suite, section-granular tracking, threshold profiles per lane |
| **Section Source Hashes** | Every section carries base_section_hash, input_payload_hash, output_payload_hash, claim_ledger_hash |
| **Explicit L2 Count** | Exactly 18 L2 executions + 2 deterministic non-model nodes |
| **L3 Orchestration** | 22-step managed workflow with explicit order, dependencies, stop conditions |
| **No Patch Rule** | Create canonical prompts from scratch; old prompts are reference-only |
| **Runtime Payload Tests** | Tests prove section isolation and payload boundaries |

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

### 2.4 Base Resume SSOT Rule (JSON — Critical Anti-Drift Control)

The **canonical frozen base resume JSON** is the **runtime SSOT**, not DOCX.

**Canonical JSON Design:**

| Component | Path | Purpose |
|-----------|------|---------|
| **Base Resume JSON** | `apps_rg/resume/base/amit_ayer_base_resume_v1.json` | Immutable canonical resume structure |
| **Active Pointer** | `apps_rg/resume/base/active_base_resume_pointer.json` | Runtime reference to current version |

**Runtime Load Requirements:**
Every JD customization MUST load:
- `base_resume_json_ref` — pointer to canonical JSON
- `base_resume_json_hash` — SHA256 of canonical JSON
- `base_resume_schema_version` — schema validation
- `base_section_hashes` — per-section source hashes
- `locked_copy_hashes` — locked section integrity hashes

**DOCX Usage Rules:**
- DOCX may be used **ONLY** to create or validate the canonical JSON
- Normal JD customization **MUST NOT** repeatedly parse DOCX
- Normal JD customization **MUST NOT** mutate canonical JSON
- If DOCX and canonical JSON conflict during runtime → **FAIL** (unless explicit base resume refresh workflow run)

**Authority Hierarchy:**

| Source | Authority Status | Conflict Resolution |
|--------|------------------|---------------------|
| **Canonical base resume JSON** | ✅ **SSOT — AUTHORITATIVE** | Wins all conflicts |
| Older `master_resume.json` | ❌ NON-AUTHORITATIVE | Blocked unless explicitly conflict-cleared |
| Prior resume files | ❌ NON-AUTHORITATIVE | Cannot feed candidate_fact_map |
| Cached bullet pools | ❌ NON-AUTHORITATIVE | Ignored unless mapped and validated |
| Historical candidate facts | ❌ NON-AUTHORITATIVE | Require explicit conflict resolution |
| **DOCX** (during normal customization) | ❌ **NON-AUTHORITATIVE** | Load JSON only; DOCX for refresh workflow only |

**Base Resume Refresh Workflow (Versioned):**
1. Ingest approved new base resume DOCX
2. Generate candidate `base_resume_json`
3. Diff against prior canonical JSON
4. Require human approval
5. Write new version (e.g., `amit_ayer_base_resume_v2.json`)
6. Update `active_base_resume_pointer`
7. Emit `base_resume_refresh_receipt`

**SSOT Tests Required:**
- Runtime loads canonical JSON by ref and hash
- Runtime does not parse DOCX during normal JD customization
- `candidate_fact_map` traces to canonical JSON fact IDs
- `verified_skill_inventory` traces to canonical JSON fact IDs
- Section prompts receive only section-scoped JSON slices
- Locked sections copied from canonical JSON byte-for-byte
- DOCX manifest fails if locked text differs from canonical JSON
- Conflicting older `master_resume.json` cannot override canonical JSON
- Canonical JSON cannot be mutated during JD tailoring
- Base resume refresh requires explicit versioned workflow

### 2.5 Section Source Hash Requirements

Every section packet **MUST** carry cryptographic source hashes:

| Hash Field | Purpose | Validation Point |
|------------|---------|------------------|
| `base_section_hash` | Hash of source section from base resume | L3 input freeze |
| `input_payload_hash` | Hash of prompt + context + allowed_fact_ids | Pre-L2 execution |
| `output_payload_hash` | Hash of raw model output | Post-L2 execution |
| `claim_ledger_hash` | Hash of structured claim_ledger | Post-validation |
| `locked_copy_hash` | Hash of deterministic locked section copy | DOCX manifest |

**DOCX manifest MUST validate** `locked_copy_hash` against base resume source hash. Mismatch = hard fail before render.

### 2.6 Deterministic Copy Architecture (No Model Prompts for Locked Sections)

Locked sections **MUST NOT** enter any model prompt payload as writable text. They bypass L2 model generation entirely:

| Locked Section | Source of Truth | Validation Point |
|----------------|-----------------|------------------|
| InsurTech full section | Base resume structured data | L4 deterministic copy contract |
| EY full section | Base resume structured data | L4 deterministic copy contract |
| Early Career full section | Base resume structured data | L4 deterministic copy contract |
| Education | Base resume structured data | L4 deterministic copy contract |
| Certifications & Credentials | Base resume structured data | L4 deterministic copy contract |

**Locked fields across all roles (read-only in all prompts):**
- `company` — sourced from base resume, never writable
- `location` — sourced from base resume, never writable
- `historical_title` — sourced from base resume, never writable
- `dates` — sourced from base resume, never writable

**NO `locked_copy_*.yaml` model prompts will be created.** Locked sections flow through runtime deterministic copy contracts and are validated at DOCX manifest generation.

**Locked Copy Assembler** (deterministic non-model node):
- InsurTech full section (company, location, title, dates, narrative, bullets)
- EY full section
- Early Career full section
- Education
- Certifications & Credentials
- All role headers (company, location, historical_title, dates)

### 2.7 Explicit L2 Execution Count (18 + 2)

**Generation/Selector Lanes (8):**
1. `strategic_tailor_v2` — planning only
2. `headline_tailor_v1` — X | Y | Z headline
3. `executive_summary.generate_scratch_v1` — evidence-first summary
4. `unify_bullet_tailor_v1` — 6 bullets
5. `unify_position_narrative_v1` — 1 sentence
6. `ibm_bullet_tailor_v1` — 5 bullets
7. `ibm_position_narrative_v1` — 1 sentence
8. `competency_selector_v2` — 8 categories

**Validator Lanes (7):**
9. Executive summary fact check
10. Executive summary unsupported/omission check
11. Unify bullet fact check
12. Unify narrative fact check
13. IBM bullet fact check
14. IBM narrative fact check
15. Competency fact check

**Final Control Lanes (3):**
16. `final_unify_v2` — consistency only, no new content authority
17. `unsupported_claim_omission_v2` — final
18. `resume_fact_check_v2` — final

**Deterministic Non-Model Nodes (2):**
19. Locked copy assembler
20. DOCX manifest validator

**Optional L2 Repair Lanes (0-2):**
- `bullet_diversity_repair_v2` for Unify (only if needed, before fact check)
- `bullet_diversity_repair_v2` for IBM (only if needed, before fact check)

**Total Required L2 Executions: 18**
**Total Deterministic Non-Model Nodes: 2**

### 2.8 L3 Managed Workflow Orchestration Order (22 Steps)

L3 **MUST** enforce this exact execution order with dependencies and stop conditions:

| Step | L2/Node | Purpose | Stop Condition |
|------|---------|---------|----------------|
| 0 | **L3 Parse & Freeze** | Parse inputs, freeze base_resume_ssot_ref, compute base_section_hashes | Any parse error |
| 1 | `strategic_tailor_v2` | Planning only, emits allowed_fact_ids_by_section | Planning failure |
| 2 | `headline_tailor_v1` | X \| Y \| Z headline, 8-11 words | Format violation |
| 3 | `executive_summary.generate_scratch_v1` | Evidence-first summary generation | Evidence trace failure |
| 4 | `resume_fact_check_v2` | Fact check summary claims | Unsupported claim found |
| 5 | `unsupported_claim_omission_v2` | Omission check on summary | Unresolvable claim |
| 6 | `unify_bullet_tailor_v1` | Generate 6 Unify bullets | Wrong bullet count |
| 7 | `bullet_diversity_repair_v2` (optional) | Repair only if repetition detected | N/A — optional |
| 8 | `resume_fact_check_v2` | Fact check Unify bullets | Unsupported bullet claim |
| 9 | `unify_position_narrative_v1` | Generate 1-sentence Unify narrative | Multiple sentences |
| 10 | `resume_fact_check_v2` | Fact check Unify narrative | New claim introduced |
| 11 | `ibm_bullet_tailor_v1` | Generate 5 IBM bullets | Wrong bullet count |
| 12 | `bullet_diversity_repair_v2` (optional) | Repair only if repetition detected | N/A — optional |
| 13 | `resume_fact_check_v2` | Fact check IBM bullets | Unsupported bullet claim |
| 14 | `ibm_position_narrative_v1` | Generate 1-sentence IBM narrative | Unify term contamination |
| 15 | `resume_fact_check_v2` | Fact check IBM narrative | New claim introduced |
| 16 | **Locked Copy Assembler** | Deterministic assembly of locked sections | Hash mismatch |
| 17 | `competency_selector_v2` | Generate 8 competency categories | Wrong category count |
| 18 | `resume_fact_check_v2` | Fact check competencies | Bullet restatement |
| 19 | `final_unify_v2` | Consistency pass, no new content | Net-new claim detected |
| 20 | `unsupported_claim_omission_v2` | Final omission check | Unresolvable claim |
| 21 | `resume_fact_check_v2` | Final fact check | Any unsupported claim |
| 22 | **DOCX Manifest Validator** | Validate all hashes, locked copy, render | Any hash mismatch |

**Dependency Rules:**
- Narrative lanes (steps 9, 14) **MUST NOT** start until bullet fact checks (steps 8, 13) pass
- Final validators (steps 19-21) **MUST NOT** start until all generation lanes complete
- DOCX manifest (step 22) **MUST** validate `locked_copy_hash` against base resume

### 2.9 Hardened Unify Rules (6 Bullets)

| Rule | Constraint | Violation |
|------|------------|-----------|
| Bullet count | Exactly 6 | Not 6 = hard fail |
| Rewrite distribution | 2 HEAVY / 3 MODERATE / 1 LIGHT_PROTECTED | Wrong distribution = soft fail |
| Max HEAVY | 3 (hard limit) | >3 HEAVY = hard fail |
| Min LIGHT_PROTECTED | 1 (hard minimum) | <1 LIGHT = hard fail |
| Default LIGHT_PROTECTED | **Platform Commercialization and Engineering Leadership** bullet | Protected unless strategic_tailor_plan proves otherwise |
| Protected metrics | $22M revenue expansion, 20% margin improvement, 6mo→3wk deployment, 8→28 team scale | Any metric change = hard fail |
| Bullet scope | Bullets only — NO narrative text | Narrative in bullet prompt = hard fail |
| Citation | Every bullet MUST cite source_fact_ids | Missing citation = hard fail |

**Unify LIGHT_PROTECTED Default Rationale:**
The Platform Commercialization bullet carries the highest-value proof ($22M, margin expansion, team scaling). It should only be rewritten if strategic_tailor_plan explicitly identifies a safer bullet to protect.

### 2.10 Hardened IBM Rules (5 Bullets)

| Rule | Constraint | Violation |
|------|------------|-----------|
| Bullet count | Exactly 5 | Not 5 = hard fail |
| HEAVY rewrites | **FORBIDDEN** — 0 HEAVY | Any HEAVY = hard fail |
| Rewrite distribution | 3 MODERATE / 2 LIGHT_PROTECTED | Wrong distribution = soft fail |
| Content domain | Enterprise-scale cloud, data, AI platform, regulated financial services, lineage, observability, portfolio, partnership | Off-domain terms = hard fail |
| Forbidden terms (unless in IBM source facts) | agentic AI, GraphRAG, multi-agent orchestration, deterministic routing, sandboxed execution, replayable traces, governed AI runtime, prompt assembly, C0, L2, Exit, UWG | Forbidden term use = hard fail |
| Narrative isolation | IBM narrative runs AFTER IBM bullet fact check, must not import Unify runtime claims | Unify term contamination = hard fail |
| Citation | Every bullet MUST cite source_fact_ids | Missing citation = hard fail |

### 2.11 Hardened Narrative Prompt Rules (Both Unify and IBM)

| Rule | Constraint | Violation |
|------|------------|-----------|
| Execution order | Run AFTER bullet generation AND bullet fact check | Wrong order = workflow fail |
| Length | Exactly 1 sentence | Multiple sentences = hard fail |
| Style | Elevator-style, catchy but not salesy | Too salesy = soft fail |
| Relationship to bullets | Complement bullets, do NOT summarize them | Summary repetition = hard fail |
| Metric repetition | Do NOT repeat bullet metrics | Metric copied = hard fail |
| Label repetition | Do NOT repeat bullet labels unless specifically justified | Label copied = hard fail |
| Structure | Do NOT copy bullet sentence structure | Parallel structure = soft fail |
| Claims | Do NOT introduce new claims not supported by role allowed facts or fact-checked bullets | New unsupported claim = hard fail |
| Numbers | NO numbers unless already present in base narrative or explicitly allowed | New number = hard fail |

### 2.12 Hardened Competency Selector Rules

| Rule | Constraint | Violation |
|------|------------|-----------|
| Category count | Exactly 8 | Not 8 = hard fail |
| Format | `Category Label: term, term, term` | Full sentences = hard fail |
| Sentence prohibition | NO full sentences, NO bullets, NO keyword stuffing | Violation = hard fail |
| Purpose | Augment bullets, NOT restate them | Pure restatement = hard fail |
| Source tracking | Every term MUST map to source_fact_ids | Missing source = hard fail |
| Overlap check | Compute overlap against finalized bullets | |
| — Rejection threshold | Reject term if it repeats a bullet outcome | Outcome overlap = hard fail |
| — Compression threshold | Reject or compress if >5 consecutive words from a bullet | Word overlap = hard fail |
| JD handling | JD-only skills → `excluded_jd_skills` list | JD skill in output = hard fail |
| Variant collapse | Duplicate variants → one strongest supported term | Duplicate present = soft fail |

**Good vs Bad Competency Example:**
- **BAD:** `AI CI/CD: six-month to three-week deployment reduction` (repeats bullet outcome)
- **GOOD:** `AI CI/CD: release gating, deployment lifecycle standardization` (underlying capability)

### 2.13 Neutered final_unify_v2 (Consistency Pass Only)

**final_unify_v2** has **NO net-new content authority**. It is a consistency editor only.

**ALLOWED Operations:**
- Remove duplicate claim
- Normalize same metric wording (e.g., "$22M" → "$22 million" consistently)
- Resolve terminology drift (e.g., "AI platform" vs "AI platforms")
- Fix section ordering
- Flag issue for human review

**FORBIDDEN Operations:**
- Add new claim (any claim not in input)
- Add new metric (any number not in input)
- Add new skill (any skill not in input)
- Modify locked sections (InsurTech, EY, Early Career, Education, Certs)
- Rewrite Unify or IBM substance (preserves fact-checked content)
- Change copied headers (company, location, title, dates)
- Alter source_fact_ids (preserves evidence trace)
- Alter claim ledger support status (preserves verification state)

**Detection:** If final_unify_v2 output hash shows net-new content vs input, workflow MUST fail before DOCX render.

### 2.14 Required Output Schema Fields

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

## 3. Section Proof Gates and Mandatory Stop Points (STOP 0-15)

Each stop point **MUST** produce a receipt under `artifacts/apps_rg/prompt_reset/`. **No next wave may begin until the prior stop point is PASS.** PARTIAL means stop.

### Receipt Requirements (All Stops)

| Field | Required |
|-------|----------|
| `stop_id` | STOP number |
| `section_or_function_proven` | What was validated |
| `files_changed` | List of files |
| `prompt_ids_involved` | Prompts tested |
| `runtime_lane_involved` | L2 lane |
| `input_fixture_used` | Test fixture path |
| `output_artifact_path` | Output location |
| `tests_run` | Test commands |
| `command_output_summary` | Key results |
| `pass_fail_status` | PASS / FAIL / PARTIAL |
| `known_gaps` | Deferred items |
| `agentic_core_diff_empty` | Boolean confirmation |

### STOP 0: Plan Hardening Proof

| Check | Status Required |
|-------|-----------------|
| Updated plan path | `.cursor/plans/apps-rg-prompt-layer-full-reset-plan.md` exists |
| Diff limited to plan artifact | No implementation files changed |
| agentic_core diff empty | Zero changes to core/shims |
| JSON SSOT specified | Canonical base resume JSON, not DOCX |
| 18 L2 executions specified | Generation + validator + final + deterministic |
| 22-step L3 order specified | Dependencies and stop conditions defined |
| Section hashes specified | 5 hash fields per section |
| Monolith kill switch specified | CI gate blocks monolithic paths |
| Deterministic copy specified | Locked sections bypass LLM |
| Runtime payload tests specified | 10 payload isolation tests |
| STOP 0-15 defined | All stop points present |
| Temperature calibration specified | Per-lane profiles |
| Section metrics specified | Global suite, granular tracking |

### STOP 1: Canonical Base Resume JSON Proof

| Check | Verification |
|-------|--------------|
| Canonical JSON exists | `apps_rg/resume/base/amit_ayer_base_resume_v1.json` |
| Active pointer exists | `apps_rg/resume/base/active_base_resume_pointer.json` |
| `base_resume_json_hash` | SHA256 of canonical JSON |
| `base_section_hashes` | Per-section source hashes |
| `locked_copy_hashes` | Locked section integrity |
| `candidate_fact_map` traces to JSON | All facts map to canonical JSON fact IDs |
| `verified_skill_inventory` traces to JSON | All skills map to canonical JSON |
| No DOCX parsing in normal flow | Runtime loads JSON only |
| No JSON mutation during tailoring | Canonical JSON is read-only during JD customization |

### STOP 2: Strategic Planning Lane Proof

| Check | Verification |
|-------|--------------|
| `strategic_tailor_v2` is planning-only | Output contains NO final resume prose |
| Emits `target_signal_map` | Planning artifact present |
| Emits `jd_requirement_map` | Planning artifact present |
| Emits `briefing_signal_map` | Planning artifact present |
| Emits `allowed_fact_ids_by_section` | Section-scoped fact authorization |
| Emits `forbidden_claims` | Negative constraints |
| Emits `vocabulary_map` | Terminology guidance |
| Emits `gap_list` | Unsupported requirements |
| Emits `section_budget` | Content guidance |
| **Negative test** | Final resume prose in output → FAIL |

### STOP 3: Headline Lane Proof

| Check | Verification |
|-------|--------------|
| Format X \| Y \| Z | Exactly 3 pipe-separated segments |
| Word count 8-11 | Total words excluding pipes |
| Segment count 3 | Each segment 2-5 words |
| No metrics | No numbers in headline |
| No company name | No target or current company |
| No contact mutation | Phone/email unchanged |
| No unsupported JD term | All terms from candidate facts |
| **Negative tests** | Wrong word count, segment count, unsupported JD keyword → FAIL |

### STOP 4: Executive Summary Lane Proof

| Check | Verification |
|-------|--------------|
| Evidence-first | Claims trace to facts |
| `selected_fact_plan` emitted | Before drafting |
| `claim_ledger` emitted | Structured evidence trace |
| `jd_alignment` emitted | Mapping to JD requirements |
| `gap_notes` emitted | Unsupported requirements |
| `self_check` emitted | Prompt verification |
| No `target_words` or `max_words` | Fit-based length only |
| Every claim maps to allowed fact IDs | 100% source coverage |
| Unsupported JD → gap_notes | No fabrication |
| **Negative tests** | Briefing-as-proof, unsupported metric, JD phrase copy, em dash → FAIL |

### STOP 4A: Canonical Prompt Export and ChatGPT Review Gate (MANDATORY)

**Purpose:** Before implementation wiring, Windsurf exports exact canonical prompt templates for external review by ChatGPT. This is a **hard stop** because prompt precision, temperature posture, section boundaries, and hallucination controls are the highest-risk part of the reset.

**Sequencing:** STOP 4A occurs **after W2A, W2B, W2C, and W2D are complete** — all canonical prompts must exist before export for review. The critical prompts `unify_position_narrative_v1` (W2B) and `competency_selector_v2` (W2D) must be drafted before STOP 4A can proceed.

**This stop is mandatory before:** runtime routing, registry activation, or L2 orchestration wiring.

#### Critical Prompts Requiring Explicit ChatGPT Review

| Priority | Prompt ID | Why Critical |
|----------|-----------|--------------|
| **CRITICAL** | `executive_summary.generate_scratch_v1` | Evidence-first flow, no word count, JD-as-target-only |
| **CRITICAL** | `unify_position_narrative_v1` | One-sentence elevator pitch, anti-repetition, no new claims |
| **CRITICAL** | `competency_selector_v2` | 8-category taxonomy, ATS optimization, no bullet restatement |
| Context | `unify_bullet_tailor_v1` | Bullet distribution, rewrite intensity |
| Context | `ibm_bullet_tailor_v1` | Conservative enterprise tone, no HEAVY |
| Context | `ibm_position_narrative_v1` | IBM narrative isolation |
| Context | `headline_tailor_v1` | X \| Y \| Z format, 8-11 words |
| Context | `strategic_tailor_v2` | Planning-only, no resume prose |
| Context | `final_unify_v2` | Consistency-only, no new content authority |
| Context | `resume_fact_check_v2` | Validator precision |
| Context | `unsupported_claim_omission_v2` | Omission detection |
| Context | `docx_manifest_v2` | Locked section preservation proof |

#### Hard Stop Rules

- **Do not wire prompts into runtime** before this stop passes
- **Do not update prompt registry** before this stop passes (draft/inactive entries only if needed)
- **Do not run implementation** beyond prompt authoring before this stop passes
- **Do not claim STOP 4A PASS** until ChatGPT review feedback is incorporated or explicitly waived by Amit
- **If ChatGPT identifies** precision, temperature, payload scope, schema, hallucination, overfitting, ATS, or deterministic-copy issues → mark STOP 4A **PARTIAL** and stop

#### Review Packet Export Location

```
artifacts/apps_rg/prompt_reset/prompt_review_packet/
```

#### Required Files in Review Packet

**1. prompts_export.md**
- Full text of every canonical prompt template
- No truncation
- Include: template_id, section_id, lane_id, mode, inputs, hard_rules, output_contract, failure_behavior, final_instruction

**2. prompt_review_matrix.md**

| Column | Description |
|--------|-------------|
| prompt_id | Template identifier |
| file_path | Location in repo |
| lane_id | L2 lane assignment |
| section_id | Resume section |
| purpose | Generation or validator |
| generation_or_validator | Type classification |
| temperature_profile | Temperature range |
| writable_inputs | Fields LLM can modify |
| read_only_inputs | Context only |
| forbidden_inputs | Must never appear |
| required_output_schema | Expected JSON structure |
| claim_ledger_required | Boolean |
| gap_notes_required | Boolean |
| deterministic_copy_risk | Risk assessment |
| hallucination_risk | Risk assessment |
| ATS_or_overfitting_risk | Risk assessment |
| current_review_status | READY_FOR_CHATGPT_REVIEW \| BLOCKED |

**3. temperature_profile_review.md**

For each model-backed lane:
- Proposed temperature range
- Default temperature
- Why that temperature is safe
- Expected variation benefit
- Hard fail gates
- Section-specific calibration gates
- Whether validator temperature is 0.0
- Whether deterministic lanes have no model call

**4. payload_scope_review.md**

For each prompt:
- Exact writable input fields
- Exact read-only context fields
- allowed_fact_ids scope
- candidate_fact_map subset
- Whether finalized bullets are read-only anti-repetition context
- Proof that locked sections are not writable
- Proof that full resume is not passed as writable context

**5. output_schema_review.md**

For each prompt:
- Expected JSON schema
- Required fields
- self_check fields
- claim_ledger fields
- gap_notes fields
- Negative-control expectations

**6. sample_fixture_inputs.md**

Use one controlled fixture for review:
- Canonical base resume JSON slice references only
- Synthetic target title
- Synthetic JD signals
- Synthetic company briefing signals
- Section-scoped allowed_fact_ids
- No real implementation required

**7. stop_4a_receipt.json**

```json
{
  "stop_id": "STOP_4A",
  "prompt_files_exported": ["..."],
  "prompt_hashes": {"prompt_id": "sha256:..."},
  "review_packet_path": "artifacts/apps_rg/prompt_reset/prompt_review_packet/",
  "agentic_core_diff_empty": true,
  "runtime_wiring_changed": false,
  "registry_activation_changed": false,
  "implementation_files_changed": false,
  "critical_prompts_flagged": [
    "executive_summary.generate_scratch_v1",
    "unify_position_narrative_v1",
    "competency_selector_v2"
  ],
  "status": "READY_FOR_CHATGPT_REVIEW"
}
```

#### Prompt-Specific Review Requirements

**A. executive_summary.generate_scratch_v1**

ChatGPT must validate:
- Evidence-first flow
- No word count enforcement
- Base resume rigor and visual footprint preserved
- Every sentence must add distinct signal
- JD and briefing targeting only, never proof
- selected_fact_plan exists
- claim_ledger exists
- gap_notes exists
- No unsupported metrics
- No generic executive filler
- Temperature range is safe
- Output schema is precise enough to block hallucination

**B. unify_position_narrative_v1**

ChatGPT must validate:
- Runs after Unify bullet fact check
- Exactly one sentence
- Elevator-style, catchy but not salesy
- Complements bullets instead of summarizing them
- Does not repeat bullet metrics
- Does not repeat bullet labels unless justified
- Does not copy bullet sentence structure
- Does not introduce new claims
- Temperature range is safe
- Uses finalized bullets only as read-only anti-repetition context

**C. competency_selector_v2**

ChatGPT must validate:
- Exactly 8 categories
- Category Label: term, term, term format
- Not full sentences
- Not bullets
- Not keyword stuffing
- Maximizes ATS signal without JD stuffing
- Augments bullets instead of restating outcomes
- Every term maps to source_fact_ids
- Unsupported JD-only skills go to excluded_jd_skills
- Duplicate variants collapse
- Overlap check rejects bullet outcome restatement
- Temperature range is conservative enough

#### STOP 4A Acceptance Criteria

- [ ] Review packet exists at `artifacts/apps_rg/prompt_reset/prompt_review_packet/`
- [ ] All canonical prompts exported in full (no truncation)
- [ ] Critical prompts clearly marked (executive_summary, unify_narrative, competency_selector)
- [ ] Temperature profile included for each model-backed lane
- [ ] Payload scope included for each prompt
- [ ] Output schema included for each prompt
- [ ] Runtime wiring is not changed
- [ ] Registry activation is not changed
- [ ] agentic_core diff is empty
- [ ] stop_4a_receipt.json status is READY_FOR_CHATGPT_REVIEW

---

### STOP 4B: ChatGPT Prompt Review Incorporation (MANDATORY)

**Purpose:** After ChatGPT reviews the prompt export packet, Windsurf incorporates only approved prompt corrections before proceeding.

#### Rules

- **Do not proceed to runtime wiring** until STOP 4B passes
- **Apply only prompt/template corrections approved by Amit**
- **Do not broaden scope** based on Windsurf interpretation
- **Do not weaken** deterministic copy, fact tracing, temperature, claim ledger, no-JD-proof, or no-monolith rules
- Any rejected or unresolved ChatGPT feedback must be listed in `unresolved_review_findings`

#### STOP 4B Receipt Location

```
artifacts/apps_rg/prompt_reset/stop_4b_chatgpt_review_incorporation_receipt.json
```

#### Receipt Schema

```json
{
  "stop_id": "STOP_4B",
  "chatgpt_review_source": "path or pasted reference",
  "prompt_ids_changed": ["..."],
  "exact_changes_made": {
    "prompt_id": "description of change"
  },
  "prompt_hashes_before": {"prompt_id": "sha256:..."},
  "prompt_hashes_after": {"prompt_id": "sha256:..."},
  "unresolved_review_findings": ["..."],
  "tests_run": ["..."],
  "status": "PASS | PARTIAL | FAIL",
  "agentic_core_diff_empty": true,
  "runtime_wiring_changed": false,
  "approved_by": "Amit"
}
```

#### STOP 4B Acceptance Criteria

- [ ] ChatGPT review feedback incorporated or explicitly waived by Amit
- [ ] Only approved corrections applied (no scope expansion)
- [ ] Prompt hashes updated for any changes
- [ ] Unresolved findings documented (if any)
- [ ] Tests run to verify changes
- [ ] Status is PASS (not PARTIAL or FAIL)
- [ ] agentic_core diff is empty
- [ ] Runtime wiring not changed yet (pending W3)

---

### STOP 5: Unify Bullet Lane Proof

| Check | Verification |
|-------|--------------|
| Receives only Unify section facts | Payload isolation verified |
| Exactly 6 bullets | Count validation |
| Rewrite distribution 2/3/1 | 2 HEAVY, 3 MODERATE, 1 LIGHT_PROTECTED |
| Max HEAVY = 3 | Hard limit |
| Min LIGHT_PROTECTED = 1 | Hard minimum |
| Default LIGHT_PROTECTED | Platform Commercialization unless proven otherwise |
| Supported metrics preserved | $22M, 20%, 6mo→3wk, 8→28 team |
| No narrative emitted | Bullets only |
| `claim_ledger` and `gap_notes` emitted | Required outputs |
| **Negative tests** | 5 bullets, 7 bullets, >3 HEAVY, no LIGHT, IBM fact in Unify payload, changed metric → FAIL |

### STOP 6: Unify Narrative Lane Proof

| Check | Verification |
|-------|--------------|
| Runs after Unify bullet fact check | Dependency enforced |
| Exactly one sentence | Length validation |
| Uses finalized Unify bullets as read-only | Anti-repetition context only |
| No bullet metric repetition | Metrics not copied |
| No bullet sentence structure copy | Original phrasing |
| No company/location/title/dates mutation | Headers preserved |
| `claim_ledger` and `self_check` emitted | Required outputs |
| **Negative tests** | Repeats metric, two sentences, bullet list, header mutation → FAIL |

### STOP 7: IBM Bullet Lane Proof

| Check | Verification |
|-------|--------------|
| Receives only IBM facts | Payload isolation verified |
| Exactly 5 bullets | Count validation |
| **0 HEAVY rewrites** | Conservative only |
| Distribution 3/2 | 3 MODERATE, 2 LIGHT_PROTECTED |
| IBM metrics preserved | No metric changes |
| No Unify runtime terms | Isolation enforced |
| No narrative emitted | Bullets only |
| `claim_ledger` and `gap_notes` emitted | Required outputs |
| **Negative tests** | 4 bullets, 6 bullets, any HEAVY, Unify fact in IBM payload, forbidden term → FAIL |

### STOP 8: IBM Narrative Lane Proof

| Check | Verification |
|-------|--------------|
| Runs after IBM bullet fact check | Dependency enforced |
| Exactly one sentence | Length validation |
| No heavy rewrite posture | Conservative tone |
| Uses finalized IBM bullets as read-only | Anti-repetition context |
| No bullet metric repetition | Metrics not copied |
| No Unify runtime claim import | Isolation enforced |
| No company/location/title/dates mutation | Headers preserved |

### STOP 9: Locked Deterministic Copy Proof

| Check | Verification |
|-------|--------------|
| Locked sections bypass L2 model generation | No LLM call for locked content |
| Copied from canonical JSON | Source is JSON, not DOCX |
| Never enter model payload as writable | Payload isolation |
| Copied text matches canonical JSON hashes | Hash validation |
| DOCX manifest fails on drift | Integrity check |
| **Locked sections:** | |
| — InsurTech full section | Company, location, title, dates, narrative, bullets |
| — EY full section | Complete section preserved |
| — Early Career full section | Complete section preserved |
| — Education | Institution, degree, dates |
| — Certifications | Credentials preserved |
| — All role headers | Company, location, historical_title, dates |

### STOP 10: Competency Selector Proof

| Check | Verification |
|-------|--------------|
| Exactly 8 categories | Count validation |
| Format: Category Label: term, term, term | Structure validation |
| No full sentence paragraphs | Format validation |
| No bullets | Format validation |
| Every term maps to `source_fact_ids` | Source tracking |
| JD-only skills → `excluded_jd_skills` | Exclusion list |
| Duplicate variants collapsed | Deduplication |
| Terms augment bullets, not restate | Purpose validation |
| Overlap check against finalized bullets | Anti-repetition |
| **Negative tests** | 7/9 categories, unsupported JD skill, bullet outcome restatement, >5 words from bullet, term without source → FAIL |

### STOP 11: Final Unify Proof

| Check | Verification |
|-------|--------------|
| `final_unify_v2` is consistency-only | No generation authority |
| **Allowed operations:** | |
| — Remove duplicate claim | Deduplication |
| — Normalize same metric wording | Consistency |
| — Resolve terminology drift | Standardization |
| — Fix section ordering | Structure |
| — Flag issue for review | Human escalation |
| **Forbidden operations (FAIL if detected):** | |
| — Add new claim | Net-new content |
| — Add new metric | Net-new numbers |
| — Add new skill | Net-new capabilities |
| — Modify locked section | Integrity violation |
| — Rewrite Unify/IBM substance | Fact-checked content preservation |
| — Change copied headers | Role metadata preservation |
| — Alter `source_fact_ids` | Evidence trace preservation |
| — Alter claim ledger support status | Verification state preservation |

### STOP 12: Final Validator and DOCX Manifest Proof

| Check | Verification |
|-------|--------------|
| `unsupported_claim_omission_v2` final runs | Final omission check |
| `resume_fact_check_v2` final runs | Final fact check |
| `docx_manifest_v2` runs | Render validation |
| Final claim ledger exists | Evidence trace complete |
| Omission report exists | Gap documentation |
| Deterministic copy validation exists | Locked section integrity |
| No em dash validation exists | Format compliance |
| JD phrase copying validation exists | Originality compliance |
| Section presence validation exists | Completeness |
| Locked copy hash validation exists | Hash integrity |

### STOP 13: End-to-End Non-Monolithic Runtime Proof

| Check | Verification |
|-------|--------------|
| 18 L2 executions represented | All lanes accounted for |
| Deterministic locked copy assembler | Non-model node confirmed |
| `docx_manifest_v2` deterministic | Non-model validation confirmed |
| No runtime route invokes `strategic_tailor_v1` | Monolith blocked |
| No full-resume generation prompt invoked | Section lanes only |
| Section prompts receive section-scoped `allowed_fact_ids` | Scope enforcement |
| Final output preserves locked sections | Integrity verified |
| `agentic_core` diff is empty | Core unchanged |
| **Negative tests** | Monolithic route fails CI, section prompt receiving full resume fails, missing lane fails |

### STOP 14: Temperature Calibration Proof

| Check | Verification |
|-------|--------------|
| Every model-backed lane has profile | Temperature defined per lane |
| Deterministic lanes have no model call | No temperature for copy lanes |
| Validators use temperature 0.0 | Deterministic validation |
| Sweep was run on fixtures | Low/mid/high tested |
| Selected temperature is highest passing | Not arbitrary midpoint |
| Failed high-temperature candidates rejected | Calibration enforced |
| Receipts include temperature and gates | Runtime tracking |

**Hard Gates for Temperature Calibration:**
- `unsupported_material_claim_count` = 0
- `copied_field_mutation_count` = 0
- `unsupported_metric_count` = 0
- `unsupported_JD_only_skill_count` = 0
- `source_fact_id_coverage_rate` = 100%
- `role_header_mutation_count` = 0
- `em_dash_count` = 0
- `JD_phrase_copy_over_4_words` = 0
- `section_schema_violations` = 0
- `required_section_count_violations` = 0

### STOP 15: Section Metric Receipt Proof

| Check | Verification |
|-------|--------------|
| Shared global metric suite exists | Definitions unified |
| Section threshold profiles exist | Per-lane thresholds |
| Each LLM-generated lane emits metrics | Coverage complete |
| Locked copy lanes emit deterministic metrics | Non-model tracking |
| Final aggregate receipt exists | Summary available |
| Failures are section-attributable | Accountability |
| Unify, IBM, summary, narratives, headline, competencies, final unify, locked copy all have separate metric rows | Granularity |

**Section Metric Receipt Schema:** `artifacts/apps_rg/prompt_reset/section_metric_receipt.json`

| Field | Description |
|-------|-------------|
| `run_id` | Execution identifier |
| `base_resume_json_ref` | Pointer to canonical JSON |
| `base_resume_json_hash` | Canonical JSON integrity |
| `lane_metrics[]` | Per-lane metric rows |
| — `lane_id`, `section_id`, `prompt_id` | Identification |
| — `model`, `provider`, `temperature`, `seed` | Runtime parameters |
| — `rewrite_intensity` | When applicable |
| — `input_payload_hash`, `output_payload_hash` | Payload integrity |
| — `allowed_fact_ids_hash`, `claim_ledger_hash` | Context integrity |
| — `metrics` | Metric values |
| — `threshold_profile` | Lane-specific thresholds |
| — `pass`, `decisive_failures` | Result |
| `aggregate_summary` | Cross-section summary |
| — `total_generated_sections`, `sections_passed/failed` | Counts |
| — `total_unsupported_claims`, `total_locked_copy_mutations` | Quality |
| — `total_schema_violations`, `total_jd_copy_violations` | Compliance |
| — `final_pass` | Overall result |

### Wave-to-STOP Mapping

| Wave | Ends At | STOP Points Covered | Prerequisites |
|------|---------|---------------------|---------------|
| W0 | Current | Inventory complete | — |
| W1 | STOP 0 | Plan hardening proof | — |
| W2A | STOP 1-4 | JSON SSOT + strategic/headline/summary | W1 complete |
| W2B | STOP 5-6 | Unify bullets and narrative | W2A complete |
| W2C | STOP 7-8 | IBM bullets and narrative | W2B complete |
| W2D | STOP 10 | Competencies | W2C complete |
| **W2.P4A** | **STOP 4A** | **Prompt export for ChatGPT review** | **W2A+B+C+D ALL prompts drafted** |
| **W2.P4B** | **STOP 4B** | **ChatGPT review incorporation** | STOP 4A READY |
| W3 | STOP 13 (partial) | Non-monolithic L2 routing and L3 order | **STOP 4B PASS — BLOCKED until prompt review complete** |
| W4 | STOP 9 | Deterministic copy enforcement | W3 partial |
| W5 | STOP 15 | Claim ledger, fact boundaries, metric framework | W4 complete |
| W6 | STOP 14 | Temperature calibration | W5 complete |
| W7 | STOP 11-12 | Final validators, final_unify, DOCX manifest | W6 complete |
| W8 | STOP 13 (final) | CI and E2E regression proof | W7 complete |

**Critical Path Constraint:**  
**W3 CANNOT START until STOP 4B (ChatGPT Prompt Review Incorporation) is PASS.**  
This ensures prompts are externally reviewed and approved before any runtime wiring begins.

**STOP Sequence:**  
STOP 0 → STOP 1 → STOP 2 → STOP 3 → STOP 4 → (W2B: STOP 5-6) → (W2C: STOP 7-8) → (W2D: STOP 10) → **STOP 4A → STOP 4B** → W3...

**STOP Count:** 17 total (0-15 plus 4A, 4B)

---

## 4. Lane Temperature Profiles and Calibration

### Temperature Principles

- **No global temperature** — each L2 lane has its own profile
- **Deterministic copy lanes** — no model, no temperature
- **Validator lanes** — default to 0.0
- **Final unify** — 0.0 to 0.1, no new content authority
- **Higher temperature allowed only** where language quality benefits from variation
- **Temperature must be proven by tests**, not guessed
- **Selected temperature stored** in `lane_temperature_profile`
- **Runtime receipts include:** temperature, model, provider, seed, prompt hash, input hash, output hash, gate result

### Default Lane Temperature Profile

| Lane | Temperature Range | Rationale |
|------|-------------------|-----------|
| `strategic_tailor_v2` | 0.1 – 0.2 | Planning requires consistency |
| `headline_tailor_v1` | 0.25 – 0.45 | Some creativity for positioning |
| `executive_summary.generate_scratch_v1` | 0.35 – 0.55 | Natural language variation |
| `unify_bullet_tailor_v1` HEAVY | 0.35 – 0.50 | Rewrite variation |
| `unify_bullet_tailor_v1` MODERATE | 0.25 – 0.40 | Moderate variation |
| `unify_bullet_tailor_v1` LIGHT_PROTECTED | 0.05 – 0.15 | Minimal change |
| `unify_position_narrative_v1` | 0.35 – 0.55 | Natural phrasing |
| `ibm_bullet_tailor_v1` MODERATE | 0.20 – 0.35 | Conservative enterprise tone |
| `ibm_bullet_tailor_v1` LIGHT_PROTECTED | 0.05 – 0.15 | Minimal change |
| `ibm_position_narrative_v1` | 0.25 – 0.40 | Professional narrative |
| `competency_selector_v2` | 0.10 – 0.25 | Structured output |
| `final_unify_v2` | 0.0 – 0.1 | Consistency only |
| `resume_fact_check_v2` | 0.0 | Deterministic validation |
| `unsupported_claim_omission_v2` | 0.0 | Deterministic validation |
| `docx_manifest_v2` | — | Deterministic, no model |
| Locked copy assembler | — | Deterministic, no model |

### Temperature Calibration Method

For each model-backed lane:
1. Run sweep across allowed band using fixed fixtures: **low**, **midpoint**, **high**
2. Select the **highest temperature that passes all hard gates**
3. Store selected temperature in `lane_temperature_profile`
4. Reject failing high-temperature candidates

### Temperature Calibration Tests

- Each model-backed lane has explicit temperature profile
- Deterministic copy lanes have no temperature and no model call
- Validator lanes run at temperature 0.0
- Sweep selects highest passing temperature, not arbitrary midpoint
- High-temperature failing output is rejected
- Unsupported claim at high temperature fails calibration
- Role header mutation at high temperature fails calibration
- JD keyword stuffing at high temperature fails calibration
- Competency bullet-restatement at high temperature fails calibration
- Runtime receipt records model, provider, temperature, prompt hash, input hash, output hash, gate result

---

## 5. Section-Level Evaluation Metrics and Reporting

### Metric Philosophy

**One global apps_rg resume quality metric suite**, recorded at section and lane granularity.

**Rationale:**
- Different metric definitions per section create unnecessary complexity
- Cross-section comparison is harder with different definitions
- Core safety metrics are the same everywhere
- Section-specific behavior handled through threshold profiles, not different definitions

### Shared Global Metrics

| # | Metric | Definition |
|---|--------|------------|
| 1 | `unsupported_material_claim_count` | Claims without source_fact_id support |
| 2 | `unsupported_metric_count` | Numbers without source evidence |
| 3 | `source_fact_id_coverage_rate` | % of material claims with source |
| 4 | `copied_field_mutation_count` | Changes to company/location/title/dates |
| 5 | `locked_copy_mutation_count` | Changes to locked section content |
| 6 | `jd_phrase_copy_violation_count` | >4 consecutive JD words |
| 7 | `em_dash_count` | Em dash characters |
| 8 | `schema_violation_count` | Output schema non-compliance |
| 9 | `gap_capture_rate` | % of unsupported JD requirements captured |
| 10 | `claim_ledger_completeness_rate` | % of claims with ledger entries |
| 11 | `briefing_as_proof_violation_count` | Claims using briefing as evidence |
| 12 | `section_count_or_shape_violation_count` | Wrong bullet count, category count, etc. |
| 13 | `prompt_payload_scope_violation_count` | Wrong facts in prompt payload |
| 14 | `temperature_gate_pass` | Temperature within calibrated range |
| 15 | `final_fact_check_pass` | All fact checks pass |

### Metric Tracking Dimensions

Every metric tracked by:
- `run_id`, `lane_id`, `section_id`, `prompt_id`
- `model`, `provider`, `temperature`, `seed`
- `rewrite_intensity` (when applicable)
- `input_payload_hash`, `output_payload_hash`
- `claim_ledger_hash`, `base_section_hash`, `allowed_fact_ids_hash`
- `gate_result`

### Section-Specific Thresholds

Metric definitions are **global**. Thresholds and applicability vary by lane.

| Lane | Specific Thresholds |
|------|---------------------|
| **headline** | X \| Y \| Z format, 8-11 words, exactly 3 segments |
| **executive_summary** | `selected_fact_plan` required, 100% source coverage, 0 unsupported claims |
| **Unify bullets** | Exactly 6 bullets, valid rewrite distribution, metrics preserved |
| **Unify narrative** | Exactly 1 sentence, no metric repetition, no structure copy |
| **IBM bullets** | Exactly 5 bullets, 0 HEAVY, no forbidden terms |
| **IBM narrative** | Exactly 1 sentence, no Unify term import |
| **competencies** | Exactly 8 categories, all terms map to source_fact_ids, no bullet restatement |
| **locked copy** | `locked_copy_mutation_count` = 0, hash matches canonical JSON |
| **final_unify_v2** | `new_claim_count` = 0, `locked_copy_mutation_count` = 0 |

### Section Metric Receipt

**Artifact:** `artifacts/apps_rg/prompt_reset/section_metric_receipt.json`

```json
{
  "run_id": "...",
  "base_resume_json_ref": "...",
  "base_resume_json_hash": "...",
  "lane_metrics": [
    {
      "lane_id": "unify_bullet_tailor_v1",
      "section_id": "unify",
      "prompt_id": "...",
      "model": "Qwen/Qwen2.5-32B-Instruct-AWQ",
      "provider": "vllm",
      "temperature": 0.4,
      "seed": 42,
      "rewrite_intensity": "MODERATE",
      "input_payload_hash": "sha256:...",
      "output_payload_hash": "sha256:...",
      "allowed_fact_ids_hash": "sha256:...",
      "claim_ledger_hash": "sha256:...",
      "metrics": {
        "unsupported_material_claim_count": 0,
        "source_fact_id_coverage_rate": 1.0,
        ...
      },
      "threshold_profile": "unify_bullet_standard",
      "pass": true,
      "decisive_failures": []
    }
  ],
  "aggregate_summary": {
    "total_generated_sections": 8,
    "sections_passed": 8,
    "sections_failed": 0,
    "total_unsupported_claims": 0,
    "total_locked_copy_mutations": 0,
    "total_schema_violations": 0,
    "total_jd_copy_violations": 0,
    "final_pass": true
  }
}
```

### Metric Tests Required

- Every LLM-generated lane emits a section metric receipt
- Locked copy lanes emit deterministic copy metrics, no model metrics
- Metric definitions are shared globally
- Threshold profiles can vary by section
- Unify metrics tracked separately from IBM metrics
- Narrative metrics tracked separately from bullet metrics
- Temperature calibration records metrics per lane
- Final aggregate metric receipt fails if any section has unsupported material claims
- Final aggregate metric receipt fails if any locked copied field changes
- Final aggregate metric receipt fails if any LLM-generated section is missing claim ledger metrics

---

## 6. Current Prompt Inventory (W0)

### 6.1 Template Files Present

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

### 6.2 Runtime Wiring Status

| Binding | Location | Status | Evidence |
|---------|----------|--------|----------|
| PA Binding | `agentic_core/prompt_governance/apps_rg_pa_binding.py` — LEGACY_SHIM | **MIGRATION REQUIRED** | Re-exports from non-existent `apps_rg/runtime/bindings/pa_binding.py` |
| L2 Binding | `agentic_core/L2_execution/apps_rg_l2_binding.py` — LEGACY_SHIM | **MIGRATION REQUIRED** | Re-exports from non-existent `apps_rg/runtime/bindings/l2_binding.py` |
| C0 Binding | `apps_rg/runtime/bindings/c0_binding.py` | **PRESENT** — Active | W5 implementation with GateVerdict construction |
| Exit Binding | `apps_rg/runtime/bindings/exit_binding.py` | **PRESENT** — Active | W4 implementation |

### 6.3 Section Contracts Present

| Contract File | Coverage | Status |
|--------------|----------|--------|
| `section_contracts/executive_summary_contract.yaml` | Executive summary only | **PARTIAL** — No v2 planning-only separation |
| `section_contracts/unify_contract.yaml` | Unify experience section | **PARTIAL** — No separate bullet/narrative lanes |
| `section_contracts/competencies_contract.yaml` | Competencies section | **PARTIAL** — No 8-category enforcement |

### 6.4 Tests Present

| Test File | Coverage | Status |
|-----------|----------|--------|
| `test_w8_pa_templates_e4_e5.py` | Template resolution, parsing, slot presence | **PARTIAL** — Tests structure only, not content compliance |
| `test_w6_pa_compiler.py` | PA compiler functionality | **PARTIAL** — Tests compilation, not prompt correctness |
| `test_w7_pa_compiler_negative_controls.py` | Override attempt detection | **PARTIAL** — Tests slot ordering, not prompt content |
| `test_apps_rg_pa_tiered_prompt.py` | Tiered prompt authority | **PARTIAL** — Tests tiering, not section-specific lanes |
| `test_w10_5_pa_signal_hardening.py` | Signal hardening (W10.5 plan) | **PARTIAL** — Tests PA boundaries, not prompt reset |

---

## 7. Gap Matrix

| # | Prompt/Workflow Requirement | Current Repo Behavior | Status | Evidence Path | Replacement Needed | Required New Canonical Prompt | Required Routing Change | Required Test | Risk if Not Fixed |
|---|----------------------------|----------------------|--------|---------------|-------------------|------------------------------|------------------------|---------------|-------------------|
| 1 | `strategic_tailor_v2` — planning only, no final prose | `strategic_tailor_v1` generates full resume prose | **FAIL** | `templates/strategic_tailor_v1.yaml` I0 section | YES | `strategic_tailor_v2.yaml` | New registry entry, retire v1 | `test_strategic_tailor_v2_no_prose.py` | **CRITICAL** — Violates non-monolithic architecture |
| 2 | `strategic_tailor_v2` — emits target_signal_map, jd_requirement_map, briefing_signal_map | `strategic_tailor_v1` emits full resume JSON | **FAIL** | `templates/strategic_tailor_v1.yaml` R0 schema | YES | `strategic_tailor_v2.yaml` with planning schema | Registry update | `test_strategic_tailor_v2_outputs.py` | **CRITICAL** — No planning-only lane |
| 3 | `headline_tailor_v1` — X \| Y \| Z format, 8-11 words | No headline-specific template exists | **FAIL** | No `headline_tailor_v1.yaml` | YES | `headline_tailor_v1.yaml` | New registry entry, L2 lane | `test_headline_summary_prompts.py::test_headline_format_compliance` | **HIGH** — Missing required lane |
| 4 | `headline_tailor_v1` — no metrics, no company names, no target company | No headline template to verify | **FAIL** | Absent | YES | `headline_tailor_v1.yaml` with constraints | L2 lane wiring | `test_headline_summary_prompts.py::test_headline_constraints` | **HIGH** |
| 5 | `executive_summary.generate_scratch_v1` — evidence-first, selected_fact_plan | `strategic_tailor_v1` summary section generates without explicit fact selection | **PARTIAL** | `templates/strategic_tailor_v1.yaml` I0 executive_summary section mentions evidence but no selected_fact_plan output | YES | `executive_summary.generate_scratch_v1.yaml` | Replace v1 summary section, new lane | `test_headline_summary_prompts.py::test_executive_summary_evidence_first` | **CRITICAL** — No evidence-first workflow |
| 6 | `executive_summary.generate_scratch_v1` — no target_words, no max_words, fit-based length | `strategic_tailor_v1` has "max 4 lines / max 60 words" | **FAIL** | `templates/generate_scratch_v1.yaml` I0: "LENGTH: max 4 lines / max 60 words" | YES | `executive_summary.generate_scratch_v1.yaml` without word count | Remove word count enforcement | `test_headline_summary_prompts.py::test_executive_summary_no_word_count` | **HIGH** — Violates fit-based length law |
| 7 | `executive_summary.generate_scratch_v1` — claim_ledger, selected_fact_plan, jd_alignment, gap_notes, self_check | No structured claim_ledger output in any template | **FAIL** | All templates lack structured claim_ledger in R0 | YES | `executive_summary.generate_scratch_v1.yaml` with full schema | Registry update, JSON schema update | `test_executive_summary_output_schema.py` | **CRITICAL** — No evidence traceability |
| 8 | `unify_bullet_tailor_v1` — exactly 6 bullets | `strategic_tailor_v1` experience section has no bullet count enforcement | **FAIL** | `templates/strategic_tailor_v1.yaml` I0 experience: no bullet count constraint | YES | `unify_bullet_tailor_v1.yaml` | New section-specific lane | `test_unify_ibm_prompts.py::test_unify_bullet_count` | **CRITICAL** — Bullet count not enforced |
| 9 | `unify_bullet_tailor_v1` — HEAVY/MODERATE/LIGHT_PROTECTED distribution 2/3/1 | No rewrite distribution guidance in templates | **FAIL** | No distribution rules found | YES | `unify_bullet_tailor_v1.yaml` with distribution rules | L2 lane, strategic_tailor_plan integration | `test_unify_bullet_distribution.py` | **HIGH** |
| 10 | `unify_bullet_tailor_v1` — max 3 HEAVY, min 1 LIGHT_PROTECTED | No distribution constraints | **FAIL** | Absent | YES | `unify_bullet_tailor_v1.yaml` with constraints | Registry update | `test_unify_distribution_bounds.py` | **HIGH** |
| 11 | `unify_bullet_tailor_v1` — must not write Unify narrative | `strategic_tailor_v1` writes full experience section including narrative | **FAIL** | `templates/strategic_tailor_v1.yaml` I0 experience: includes narrative guidance | YES | `unify_bullet_tailor_v1.yaml` (bullets only) | Separate lane, no narrative | `test_unify_ibm_prompts.py::test_unify_no_narrative` | **HIGH** |
| 12 | `unify_position_narrative_v1` — runs after bullet fact check | No separate narrative lane; no fact-check ordering | **FAIL** | `resume_fact_check_v1.yaml` exists but no lane ordering | YES | `unify_position_narrative_v1.yaml` | L2 lane ordering: bullets → fact_check → narrative | `test_unify_ibm_prompts.py::test_unify_narrative_ordering` | **HIGH** |
| 13 | `unify_position_narrative_v1` — exactly one elevator-style sentence | No narrative-specific template | **FAIL** | Absent | YES | `unify_position_narrative_v1.yaml` | New lane | `test_unify_ibm_prompts.py::test_unify_narrative_one_sentence` | **HIGH** |
| 14 | `unify_position_narrative_v1` — must not repeat bullet metrics | No anti-repetition constraint specific to narrative | **PARTIAL** | `templates/unify_v1.yaml` has consistency guidance but not specific | YES | `unify_position_narrative_v1.yaml` with anti-repetition | L2 lane | `test_unify_ibm_prompts.py::test_unify_narrative_no_repeat` | **MEDIUM** |
| 15 | `ibm_bullet_tailor_v1` — exactly 5 bullets | No IBM-specific bullet template | **FAIL** | No IBM-specific templates exist | YES | `ibm_bullet_tailor_v1.yaml` | New lane | `test_unify_ibm_prompts.py::test_ibm_bullet_count` | **HIGH** — Missing required lane |
| 16 | `ibm_bullet_tailor_v1` — no HEAVY rewrites, 3 MODERATE/2 LIGHT_PROTECTED | No IBM-specific rewrite rules | **FAIL** | Absent | YES | `ibm_bullet_tailor_v1.yaml` with conservative rules | Registry, L2 lane | `test_unify_ibm_prompts.py::test_ibm_conservative_rewrite` | **HIGH** |
| 17 | `ibm_bullet_tailor_v1` — no Unify runtime terms (GraphRAG, multi-agent, etc.) | No IBM-specific term filtering | **FAIL** | Absent | YES | `ibm_bullet_tailor_v1.yaml` with term blacklist | L2 lane | `test_unify_ibm_prompts.py::test_ibm_no_unify_terms` | **HIGH** — Cross-role contamination risk |
| 18 | `ibm_position_narrative_v1` — runs after IBM bullet fact check | No IBM narrative lane | **FAIL** | Absent | YES | `ibm_position_narrative_v1.yaml` | L2 lane ordering | `test_unify_ibm_prompts.py::test_ibm_narrative_ordering` | **HIGH** |
| 19 | `competency_selector_v2` — exactly 8 competency categories | `strategic_tailor_v1` competencies has no count enforcement | **FAIL** | `templates/strategic_tailor_v1.yaml` I0 competencies: no count | YES | `competency_selector_v2.yaml` | New lane | `test_competency_selector.py::test_competency_count` | **HIGH** |
| 20 | `competency_selector_v2` — Category: terms format, no sentences | No format enforcement | **FAIL** | Current templates don't specify format | YES | `competency_selector_v2.yaml` with format rules | Registry, L2 lane | `test_competency_selector.py::test_competency_format` | **HIGH** |
| 21 | `competency_selector_v2` — excluded_jd_skills list | No JD skill exclusion output | **FAIL** | Absent | YES | `competency_selector_v2.yaml` with excluded list | Registry | `test_competency_selector.py::test_jd_skill_exclusion` | **HIGH** |
| 22 | `competency_selector_v2` — no bullet restatement, source_fact_ids | No anti-repetition or source tracking | **FAIL** | Current templates lack this | YES | `competency_selector_v2.yaml` | Registry | `test_competency_selector.py::test_no_repetition` | **HIGH** |
| 23 | `final unify_v2` — consistency pass only, no new content | `unify_v1.yaml` claims consistency but has preservation issues | **PARTIAL** | `templates/unify_v1.yaml` has preservation check but no locked section enforcement | YES | `final unify_v2.yaml` | Replace v1, L2 lane | `test_final_validators_docx_manifest.py::test_final_unify_no_new_content` | **HIGH** |
| 24 | `final unify_v2` — must not modify locked deterministic copy sections | No locked section enforcement in unify | **FAIL** | `templates/unify_v1.yaml` has preservation_check but no locked section list | YES | `final unify_v2.yaml` with locked list | L2 lane | `test_final_validators_docx_manifest.py::test_final_unify_locked_sections` | **CRITICAL** — Locked section bypass not enforced |
| 25 | `resume_fact_check_v2` — claim ledger validation | `resume_fact_check_v1.yaml` has verification_report but no structured claim_ledger | **PARTIAL** | `templates/resume_fact_check_v1.yaml` R0: verification_report, unsupported_claims, suggested_corrections — no claim_ledger | YES | `resume_fact_check_v2.yaml` | Replace v1 | `test_final_validators_docx_manifest.py::test_fact_check_claim_ledger` | **HIGH** |
| 26 | `unsupported_claim_omission_v2` — omission report, claim ledger | `unsupported_claim_omission_v1.yaml` has omission but no claim_ledger | **PARTIAL** | `templates/unsupported_claim_omission_v1.yaml` R0: corrected_resume, omitted_claims, gap_notes — no claim_ledger | YES | `unsupported_claim_omission_v2.yaml` | Replace v1 | `test_final_validators_docx_manifest.py::test_omission_claim_ledger` | **HIGH** |
| 27 | `docx_manifest_v2` — locked section preservation proof | `docx_manifest_v1.yaml` has content_preservation but no locked section proof | **PARTIAL** | `templates/docx_manifest_v1.yaml` R0: content_preservation counts — no locked field verification | YES | `docx_manifest_v2.yaml` with locked proof | Replace v1 | `test_final_validators_docx_manifest.py::test_docx_locked_preservation` | **HIGH** |
| 28 | Locked deterministic copy — InsurTech byte-for-byte | No runtime bypass of L2 model generation for locked sections | **FAIL** | No deterministic copy contract | YES | Runtime deterministic copy contract in `apps_rg/runtime/contracts/locked_section_contracts.py` | L4/DOCX validation | `test_locked_copy_contracts.py::test_insurtech_byte_for_byte` | **CRITICAL** — Resume integrity violation |
| 29 | Locked deterministic copy — EY byte-for-byte | No runtime bypass of L2 model generation for locked sections | **FAIL** | Absent | YES | Runtime deterministic copy contract | L4/DOCX validation | `test_locked_copy_contracts.py::test_ey_byte_for_byte` | **CRITICAL** |
| 30 | Locked deterministic copy — Early Career byte-for-byte | No runtime bypass of L2 model generation for locked sections | **FAIL** | Absent | YES | Runtime deterministic copy contract | L4/DOCX validation | `test_locked_copy_contracts.py::test_early_career_byte_for_byte` | **CRITICAL** |
| 31 | Locked deterministic copy — Education byte-for-byte | No runtime bypass of L2 model generation for locked sections | **FAIL** | Absent | YES | Runtime deterministic copy contract | L4/DOCX validation | `test_locked_copy_contracts.py::test_education_byte_for_byte` | **CRITICAL** |
| 32 | Locked deterministic copy — Certifications byte-for-byte | No runtime bypass of L2 model generation for locked sections | **FAIL** | Absent | YES | Runtime deterministic copy contract | L4/DOCX validation | `test_locked_copy_contracts.py::test_certifications_byte_for_byte` | **CRITICAL** |
| 33 | Company/location/title/dates preserved for all roles | No role header field preservation proof | **FAIL** | Templates don't specify locked field handling | YES | Section templates with locked field contracts | L2 lane | `test_role_headers_preserved.py` | **CRITICAL** |
| 34 | No em dash | `forbidden_ai_phrases.yaml` mentions em dash but no runtime enforcement | **PARTIAL** | `forbidden_ai_phrases.yaml`: "DO NOT PRODUCE: Em dash character" | NO | Update templates with explicit rejection | Add em_dash scanner to L2 or template S0 | `test_no_em_dash.py` | **MEDIUM** |
| 35 | No more than 4 consecutive JD words | No JD word counting in templates | **FAIL** | Absent | YES | Update all generation templates with 4-word constraint | L2 lane or template I0 | `test_jd_word_limit.py` | **HIGH** — JD mimicry risk |
| 36 | JD cannot become proof | `strategic_tailor_v1.yaml` S0 has oath but no runtime verification | **PARTIAL** | `templates/strategic_tailor_v1.yaml` S0: "JD/TARGET CONTEXT IS NOT PROOF" | NO | Strengthen with explicit claim tracing | Add claim tracing to L2 | `test_jd_not_proof.py` | **HIGH** |
| 37 | Briefing cannot support candidate claim | Same as above — oath present, no verification | **PARTIAL** | S0 oath exists | NO | Add briefing claim tracing | L2 verification | `test_briefing_not_proof.py` | **HIGH** |
| 38 | Unsupported JD-only skill excluded from competencies | No explicit exclusion output | **FAIL** | `strategic_tailor_v1.yaml` I0 competencies: "GAP_MARKING_REQUIRED" but no excluded list output | YES | `competency_selector_v2.yaml` | Registry update | `test_competency_selector.py::test_jd_skill_exclusion` | **HIGH** |
| 39 | Duplicate keyword variants collapsed | No variant collapsing logic | **FAIL** | Absent | YES | `competency_selector_v2.yaml` with variant map | L2 lane | `test_competency_selector.py::test_keyword_variant_collapse` | **MEDIUM** |
| 40 | Every competency term maps to source_fact_ids | No source tracking in competencies | **FAIL** | Absent | YES | `competency_selector_v2.yaml` with source tracking | Registry, L2 lane | `test_competency_selector.py::test_source_mapping` | **HIGH** |
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
**Total Tests Required**: 40 test cases grouped into 8 test files (see W8 test grouping)

---

## 8. Prompt Retirement/Replacement Table

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

## 9. Wave Structure

| Wave | Focus | Deliverables | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-------|--------------|---------------|---------------|--------|------------------|
| W0 | Current Prompt Inventory (COMPLETE) | Gap matrix, inventory list, finding report | ~8k | Files readable | ✅ DONE | All 9 templates inventoried, 41 gaps identified |
| W1 | **Plan-Only** — Retirement Strategy Definition | Retirement table, deprecation plan, migration timeline, monolith decommission gate spec | ~5k | None — plan only | **Not Started** | Strategy defined; NO existing template edits |
| W2A | Canonical Prompts — Planning, Headline, Summary | `strategic_tailor_v2.yaml`, `headline_tailor_v1.yaml`, `executive_summary.generate_scratch_v1.yaml` + tests + receipt | ~12k | Clean slate prompt authoring | **🟡 PARTIAL** | 2 templates corrected (v4 schema), 1 pending, STOP 4A export ready |
| W2B | Canonical Prompts — Unify Bullets and Narrative | `unify_bullet_tailor_v1.yaml`, `unify_position_narrative_v1.yaml` + tests + receipt | ~8k | W2A complete | **Not Started** | 2 templates, bullet→fact_check→narrative ordering |
| W2C | Canonical Prompts — IBM Bullets and Narrative | `ibm_bullet_tailor_v1.yaml`, `ibm_position_narrative_v1.yaml` + tests + receipt | ~8k | W2B complete | **Not Started** | 2 templates, conservative rewrite rules |
| W2D | Canonical Prompts — Competencies | `competency_selector_v2.yaml` + tests + receipt | ~6k | W2C complete | **Not Started** | 1 template, 8-category enforcement |
| W3 | Non-Monolithic L2 Routing | L2 lane definitions, ordering enforcement, registry updates + receipt | ~8k | W2D complete | **Not Started** | 12-step lane order enforced |
| W4 | Deterministic Copy Enforcement | Runtime deterministic copy contracts, DOCX manifest validation + receipt | ~6k | W3 complete | **Not Started** | 5 locked sections bypass L2 generation |
| W5 | Claim Ledger and Fact Boundaries | Claim ledger schema enforcement, gap_notes output, JD-as-target verification + receipt | ~8k | W4 complete | **Not Started** | All generation prompts emit claim_ledger |
| W6 | Competency Selector Reset | 8-category taxonomy, keyword collapsing, JD exclusion enforcement + receipt | ~6k | W5 complete | **Not Started** | All competency requirements enforced |
| W7 | Final Validators and DOCX Manifest | `resume_fact_check_v2.yaml`, `unsupported_claim_omission_v2.yaml`, `docx_manifest_v2.yaml` + tests + receipt | ~8k | W6 complete | **Not Started** | 3 v2 validator templates |
| W8 | CI and Regression Proof | 8 grouped test files, monolith decommission gate, coverage gates + final receipt | ~12k | W7 complete | **Not Started** | All 40 test cases pass, ≥80% coverage, monolith CI gate active |

---

## 10. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|---------------|-------------|--------|
| W0 | Current State Inventory | 9 templates, 3 contracts, 5 test files | Large file reads, scattered definitions | ~8k | ✅ DONE |
| W1.P1 | Retirement Strategy Definition | Plan document only | Defining deprecation without editing files | ~2k | Not Started |
| W1.P2 | Migration Timeline | Plan document | Sequencing dependencies | ~1k | Not Started |
| W1.P3 | Monolith Decommission Gate Spec | CI gate design | Spec for blocking monolithic paths | ~2k | Not Started |
| W2A.P1 | strategic_tailor_v2 Contract | `strategic_tailor_v2.yaml` | Planning-only constraint | ~4k | ✅ DONE — v4 schema, fit-to-evidence, temp 0.1-0.2 |
| W2A.P2 | headline_tailor_v1 Contract | `headline_tailor_v1.yaml` | X \| Y \| Z format | ~2k | ✅ DONE — no metrics, role mirroring, temp 0.25-0.45 |
| W2A.P3 | executive_summary.generate_scratch_v1 Contract | `executive_summary.generate_scratch_v1.yaml` | Evidence-first, no word count | ~4k | **Not Started** — pending ChatGPT review |
| W2A.P4 | W2A Tests + Receipt | `test_headline_summary_prompts.py`, receipt | Tests before wiring | ~2k | ✅ DONE — 31 tests pass, W2A receipt issued |
| W2B.P1 | unify_bullet_tailor_v1 Contract | `unify_bullet_tailor_v1.yaml` | 6 bullets, distribution rules | ~4k | Not Started |
| W2B.P2 | unify_position_narrative_v1 Contract | `unify_position_narrative_v1.yaml` | 1 sentence, after fact check | ~2k | Not Started |
| W2B.P3 | W2B Tests + Receipt | `test_unify_ibm_prompts.py`, receipt | Bullet→fact_check→narrative ordering tests | ~2k | Not Started |
| W2C.P1 | ibm_bullet_tailor_v1 Contract | `ibm_bullet_tailor_v1.yaml` | 5 bullets, no HEAVY | ~3k | Not Started |
| W2C.P2 | ibm_position_narrative_v1 Contract | `ibm_position_narrative_v1.yaml` | 1 sentence, term filtering | ~2k | Not Started |
| W2C.P3 | W2C Tests + Receipt | `test_unify_ibm_prompts.py`, receipt | IBM-specific tests | ~3k | Not Started |
| W2D.P1 | competency_selector_v2 Contract | `competency_selector_v2.yaml` | 8 categories, exclusion list | ~4k | Not Started |
| W2D.P2 | W2D Tests + Receipt | `test_competency_selector.py`, receipt | Competency tests | ~2k | Not Started |
| **W2.P4A** | **STOP 4A: Prompt Export & ChatGPT Review** | `artifacts/apps_rg/prompt_reset/prompt_review_packet/` | Export all 12 prompts, critical prompts flagged | ~3k | 🟡 **IN PROGRESS** — PART 1 exported, paused for correction verification |
| **W2.P4B** | **STOP 4B: ChatGPT Review Incorporation** | Prompt corrections per approved feedback | Incorporate only approved corrections | ~2k | **Not Started** — BLOCKED until ChatGPT review |
| W3.P1 | L2 Lane Definitions | `l2_binding.py` (new) | Lane ordering enforcement | ~3k | **Not Started** — BLOCKED until STOP 4B PASS |
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

## 11. Definition of Done

| DoD | Description | Verification |
|-----|-------------|--------------|
| DoD-1 | All 12 canonical prompt templates exist and resolve from registry | `test_prompt_registry_reset.py` passes |
| DoD-2 | `strategic_tailor_v2` emits planning outputs only (no resume prose) | `test_strategic_tailor_v2_no_prose.py` passes |
| DoD-3 | Headline format is X \| Y \| Z with 8-11 words | `test_headline_format_compliance.py` passes |
| DoD-4 | Executive summary has no word count enforcement, uses fit-based length | `test_executive_summary_no_word_count.py` passes |
| DoD-5 | Unify bullets output exactly 6 bullets (2 HEAVY / 3 MODERATE / 1 LIGHT_PROTECTED) | `test_unify_ibm_prompts.py::test_unify_bullet_count`, `test_unify_bullet_distribution` pass |
| DoD-5A | **Unify LIGHT_PROTECTED bullet defaults to Platform Commercialization** unless strategic_tailor_plan proves otherwise | `test_unify_light_protected_default` passes |
| DoD-5B | **Unify protected metrics preserved** ($22M, 20% margin, 6mo→3wk, 8→28 team) | `test_unify_metrics_preserved` passes |
| DoD-6 | IBM bullets output exactly 5 bullets with **0 HEAVY / 3 MODERATE / 2 LIGHT_PROTECTED** | `test_unify_ibm_prompts.py::test_ibm_bullet_count`, `test_ibm_conservative_rewrite` pass |
| DoD-6A | **IBM contains no forbidden Unify terms** (agentic AI, GraphRAG, multi-agent, C0, L2, Exit, UWG) | `test_unify_ibm_prompts.py::test_ibm_no_unify_terms` passes |
| DoD-6B | **IBM narrative isolated from Unify facts** — no Unify runtime terms imported | `test_ibm_payload_isolation` passes |
| DoD-7 | Competencies output exactly 8 categories with excluded_jd_skills | `test_competency_selector.py::test_competency_count`, `test_jd_skill_exclusion` pass |
| DoD-7A | **Competencies anti-repetition check** — no term repeats bullet outcome or copies >5 consecutive words | `test_competency_selector.py::test_no_repetition` passes |
| DoD-7B | **Every competency term maps to source_fact_ids** | `test_competency_selector.py::test_source_mapping` passes |
| DoD-8 | All generation prompts emit claim_ledger, gap_notes, self_check | `test_claim_ledger_present.py` passes for all lanes |
| DoD-9 | Locked sections (InsurTech, EY, Early Career, Education, Certs) are byte-for-byte preserved | `test_locked_copy_contracts.py` passes |
| DoD-9A | **Locked sections never enter model prompt payload as writable text** | `test_locked_sections_not_in_model_payload` passes |
| DoD-9B | **Section source hashes validated** — base_section_hash, locked_copy_hash, claim_ledger_hash present | All 5 hash fields present in output |
| DoD-10 | No em dash in any prompt output | `test_no_em_dash.py` passes |
| DoD-11 | No more than 4 consecutive JD words in any output | `test_jd_word_limit.py` passes |
| DoD-12 | L2 lane ordering enforces: planning → headline → summary → bullets → fact_check → narrative → ... → final validators | `test_l2_lane_ordering.py` passes |
| DoD-13 | `agentic_core` diff is empty (no core changes) | `git diff agentic_core/` returns empty |
| DoD-14 | **No active runtime route points to strategic_tailor_v1 for resume generation** | `test_no_core_leakage.py` passes, monolith CI gate active |
| DoD-14A | **strategic_tailor_v2 planning-only** — output contains NO resume prose | `test_strategic_tailor_v2_planning_only` passes |
| DoD-15 | **All active generation lanes are section-specific** | `test_section_l2_routing.py` passes |
| DoD-16 | **All generated sections emit claim_ledger, gap_notes, change_log, and self_check** | `test_claim_ledger_present.py` passes for all lanes |
| DoD-17 | **Locked sections never enter model prompt payload as writable text** | `test_locked_copy_contracts.py` passes |
| DoD-18 | **DOCX manifest compares locked text against base resume source** | `test_docx_locked_preservation.py` passes |
| DoD-19 | **Final unify_v2 cannot modify locked sections and cannot add net-new claims** | `test_final_validators_docx_manifest.py::test_final_unify_locked_sections` passes |
| DoD-19A | **Final unify_v2 neutered** — allowed operations only (no new claims, metrics, skills) | `test_final_unify_no_add_authority` passes |
| DoD-20 | **Competency selector outputs exactly 8 categories and rejects bullet-outcome restatement** | `test_competency_selector.py` passes |
| DoD-21 | **Unify narrative and IBM narrative run only after their bullet fact checks** | `test_unify_ibm_prompts.py::test_unify_narrative_ordering`, `test_ibm_narrative_ordering` pass |
| DoD-21A | **Narratives exactly 1 sentence, no metric repetition, no new claims** | Narrative structure tests pass |
| DoD-21B | **Narratives "catchy but not claimy"** — no numbers unless in base narrative | `test_narrative_no_new_numbers` passes |
| DoD-22 | All 40 test cases + 10 runtime payload tests pass in grouped files, ≥80% line coverage | `pytest tests/_apps_contract/ -v` passes |
| DoD-23 | **Base resume SSOT enforced** — current DOCX wins all conflicts with old master_resume.json | `test_base_resume_ssot_freeze`, `test_old_master_resume_blocked` pass |
| DoD-24 | **No-patch rule verified** — all canonical prompts created from scratch, no old prompt edits | Wave receipts confirm |
| DoD-25 | **L3 orchestration order verified** — 22-step workflow with dependencies enforced | L3 state machine tests pass |

### Verification vs Deferral Table

| Verification | Deferred |
|--------------|----------|
| W0 inventory complete | W1-W8 implementation (requires wave-by-wave approval) |
| Gap matrix with 41 items | Individual template authoring (deferred to waves) |
| Retirement table defined | Runtime wiring migration (W3 scope) |
| Test list defined | Test implementation (W8 scope) |
| No agentic_core changes in plan | Implementation changes outside plan (blocked until waves approved) |

---

## 12. Top 5 Highest-Risk Prompt Gaps

| Rank | Gap | Risk | Mitigation |
|------|-----|------|------------|
| 1 | **Monolithic `strategic_tailor_v1`** — Generates full resume in one prompt, violating non-monolithic architecture | Resume integrity failures, untraceable claims, locked section mutation | W2: Create `strategic_tailor_v2` planning-only; W3: Implement section lanes |
| 2 | **No section-specific lanes** — Missing headline, bullet, narrative, competency separation | Cross-section contamination, repetition, metric inconsistencies | W2: Create 7 section-specific templates; W3: Wire L2 lanes |
| 3 | **No locked section enforcement** — InsurTech, EY, Early Career, Education, Certs not protected from LLM modification | Resume fraud, experience falsification | W4: Implement deterministic copy with byte-for-byte preservation |
| 4 | **No claim ledger output** — No structured evidence traceability | Unverifiable claims, no fact-checking possible | W5: Add claim_ledger to all generation prompts; W7: Implement v2 validators |
| 5 | **JD can become proof** — Oath present but no runtime verification of claim sources | JD mimicry, unsupported claims presented as experience | W5: Add claim tracing; W7: Strengthen fact check validators |

---

## 13. Files Inspected

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

## 14. Confirmations (Hardened)

| Confirmation | Status |
|--------------|--------|
| **No agentic_core changes** in this plan | ✅ CONFIRMED |
| **No implementation changes** outside plan artifact | ✅ CONFIRMED |
| **Full reset approach** — existing prompts untrusted | ✅ CONFIRMED |
| **Gap matrix with 41 items** | ✅ CONFIRMED |
| **Retirement/replacement table** | ✅ CONFIRMED |
| **Wave list with W2A-W2D subwaves** | ✅ CONFIRMED — 12 waves total |
| **W1 plan-only constraint** | ✅ ADDED — No YAML edits in W1 |
| **No-core-edit rule** | ✅ ADDED — App-local bindings only |
| **Monolith decommission gate** | ✅ ADDED — CI enforcement spec |
| **Deterministic copy bypass** | ✅ UPDATED — No model prompts for locked sections |
| **Test grouping (8 files, 40 cases)** | ✅ ADDED — Grouped by domain |
| **Receipt requirements per wave** | ✅ ADDED — Artifact schema defined |
| **Tightened DoD (22 items)** | ✅ ADDED — 8 new DoD items |
| **Files inspected list** | ✅ CONFIRMED — 26 files |
| **Top 5 highest-risk gaps** | ✅ CONFIRMED |

---

## 15. Next Steps

1. **Review this hardened plan** — Approve wave structure, W1 plan-only constraint, and no-core-edit rule
2. **W1 execution** — Define retirement strategy (NO existing YAML template edits)
3. **Wave-by-wave authorization** — Each wave requires explicit go-ahead and produces receipt artifact
4. **Test-first development** — Tests before runtime wiring for every template
5. **No agentic_core changes** — App-local bindings under `apps_rg/runtime/bindings/` only
6. **Monolith decommission gate** — CI gate active by W8 to block monolithic paths

---

## 16. Wave Receipt Requirements

Each wave (W1-W8) **MUST** produce a receipt artifact at:
```
artifacts/apps_rg/prompt_reset/<wave>_receipt.json
```

### Receipt Schema

| Field | Type | Description |
|-------|------|-------------|
| `wave_id` | string | Wave identifier (e.g., "W2A") |
| `receipt_timestamp` | ISO8601 | UTC timestamp of receipt generation |
| `files_changed` | list[string] | Relative paths of all files created/modified |
| `tests_run` | list[string] | Test files executed |
| `test_result` | PASS \| FAIL | Overall test result |
| `test_details` | object | Per-test pass/fail breakdown |
| `prompts_added` | list[string] | New prompt IDs added to registry |
| `prompts_retired` | list[string] | Prompt IDs marked for retirement |
| `runtime_routes_added` | list[string] | New L2 runtime routes |
| `runtime_routes_changed` | list[string] | Modified L2 runtime routes |
| `agentic_core_diff_empty` | boolean | Confirmation no agentic_core changes |
| `monolithic_path_status` | BLOCKED \| ACTIVE | Whether monolithic paths are blocked |
| `receipt_hash` | string | SHA256 of receipt content |
| `verification_signature` | string | Verification signature |

### W1 Receipt Special Requirements

W1 is **plan-only** — the W1 receipt MUST confirm:
- No existing YAML template files were edited
- No strategic_tailor_v1, tailor_existing_v1, generate_scratch_v1, enhance_current_v1, unify_v1 modifications
- Only plan documents and design specs were created

### Final W8 Receipt

The W8 receipt MUST confirm:
- All 40 test cases pass in 8 grouped test files
- Monolith decommission gate is active in CI
- No active runtime route points to strategic_tailor_v1 for generation
- `agentic_core/` diff is empty across entire reset

---

## 17. Monolith Decommission Gate (CI Enforcement)

### Gate Purpose

After reset completion, **CI MUST FAIL** if any runtime path invokes monolithic full-resume generation.

### Gate Implementation

| Aspect | Requirement |
|--------|-------------|
| **Gate Name** | `MONOLITH-DECOMMISSION` |
| **Gate Location** | `ops_scripts/ci/check_apps_rg_monolith_decommission.py` |
| **Trigger** | Every PR, every merge to main |
| **Severity** | FAIL (blocking) |
| **Bypass** | `MONOLITH_DECOMMISSION_BYPASS=1` (emergency only, logged) |

### Forbidden Patterns (Gate Detection)

The gate MUST detect and block:

| Pattern | Violation |
|---------|-----------|
| `strategic_tailor_v1` invoked for resume generation | Monolithic full-resume generation |
| `tailor_existing_v1` invoked for resume generation | Deprecated monolithic path |
| `generate_scratch_v1` invoked for resume generation | Deprecated monolithic path |
| `enhance_current_v1` invoked for resume generation | Deprecated monolithic path |
| `unify_v1` invoked as primary generation | Monolithic consistency pass |
| Any template with `allowed_stage: E3_EXEC` and `sections: [summary, experience, projects, skills, education]` in output contract | Monolithic full-resume template |

### Allowed Patterns

| Pattern | Permitted Use |
|---------|---------------|
| `strategic_tailor_v2` | Planning-only, NO resume prose |
| `headline_tailor_v1` | Single section (headline) |
| `executive_summary.generate_scratch_v1` | Single section (summary) |
| `unify_bullet_tailor_v1` | Single section (bullets only) |
| `unify_position_narrative_v1` | Single section (narrative only) |
| `resume_fact_check_v2` | Validation only |
| `unsupported_claim_omission_v2` | Validation only |
| `final unify_v2` | Consistency pass only |
| `docx_manifest_v2` | Render manifest only |

### Gate Output

```json
{
  "gate_id": "MONOLITH-DECOMMISSION",
  "result": "PASS|FAIL",
  "monolithic_paths_detected": [],
  "active_section_lanes_verified": [
    "strategic_tailor_v2",
    "headline_tailor_v1",
    "executive_summary.generate_scratch_v1",
    "unify_bullet_tailor_v1",
    "unify_position_narrative_v1",
    "ibm_bullet_tailor_v1",
    "ibm_position_narrative_v1",
    "competency_selector_v2"
  ],
  "verified_at": "2026-05-14T20:00:00Z"
}
```

---

## 18. W8 Test Grouping (8 Files, 40 Test Cases)

The 40 required test cases are grouped into 8 domain files:

| Test File | Test Cases | Coverage |
|-----------|------------|----------|
| `test_prompt_registry_reset.py` | 5 cases | Registry updates, retirement markers, v1→v2 transitions |
| `test_section_l2_routing.py` | 5 cases | Lane ordering, bullet→fact_check→narrative sequence, section isolation |
| `test_headline_summary_prompts.py` | 5 cases | Headline X\|Y\|Z format, word count, constraints; Summary evidence-first, no word count, claim_ledger |
| `test_unify_ibm_prompts.py` | 10 cases | Bullet counts (6/5), distributions, narrative 1-sentence, ordering, IBM term filtering |
| `test_locked_copy_contracts.py` | 5 cases | Byte-for-byte preservation for InsurTech, EY, Early Career, Education, Certs |
| `test_competency_selector.py` | 5 cases | 8 categories, format, JD exclusion, source mapping, anti-repetition |
| `test_final_validators_docx_manifest.py` | 5 cases | Claim ledger validation, omission report, DOCX locked section proof, final unify constraints |
| `test_no_core_leakage.py` | 5 cases | agentic_core diff empty, no shim edits, app-local binding isolation, monolith gate active |

### 15.1 Runtime Payload Tests (Critical Addition)

In addition to template content tests, the following runtime payload tests **MUST** prove section isolation:

| Test Case | Assertion | Failure Mode |
|-----------|-----------|--------------|
| `test_unify_payload_isolation` | Unify bullet prompt does NOT receive IBM facts as writable proof | Cross-contamination |
| `test_ibm_payload_isolation` | IBM bullet prompt does NOT receive Unify facts as writable proof | Cross-contamination |
| `test_competency_payload_scope` | Competency prompt receives finalized bullets ONLY as anti-repetition context | Scope violation |
| `test_locked_sections_not_in_model_payload` | Locked sections NEVER enter model prompt payload as writable text | Integrity violation |
| `test_section_scoped_allowed_fact_ids` | Each section prompt receives ONLY section-scoped allowed_fact_ids | Fact leakage |
| `test_final_unify_no_add_authority` | Final unify receives assembled sections and ledgers, but NO authority to add content | Authority violation |
| `test_docx_manifest_hash_validation` | DOCX manifest fails if locked source hash changes | Preservation failure |
| `test_base_resume_ssot_freeze` | base_resume_ssot_ref frozen at workflow start, carried through all packets | Drift risk |
| `test_old_master_resume_blocked` | Older master_resume.json cannot override current base resume DOCX | SSOT violation |
| `test_strategic_tailor_v2_planning_only` | strategic_tailor_v2 output contains NO resume prose, only planning artifacts | Monolith escape |

**Test Implementation:** These tests inspect actual L2 call payloads at runtime, not just YAML template content.

---

## 19. W1 Plan-Only Constraint Detail

W1 **MUST NOT**:
- Edit `strategic_tailor_v1.yaml`
- Edit `tailor_existing_v1.yaml`
- Edit `generate_scratch_v1.yaml`
- Edit `enhance_current_v1.yaml`
- Edit `unify_v1.yaml`
- Edit `resume_fact_check_v1.yaml`
- Edit `unsupported_claim_omission_v1.yaml`
- Edit `bullet_diversity_repair_v1.yaml`
- Edit `docx_manifest_v1.yaml`

W1 **MAY**:
- Create plan documents
- Create deprecation strategy specs
- Create migration timeline documents
- Create monolith decommission gate design specs
- Create new v2 template files (if approved for W2A-D)

---

## 20. No-Core-Edit Rule Detail

### Forbidden

| Path | Rule |
|------|------|
| `agentic_core/prompt_governance/apps_rg_pa_binding.py` | May inspect, NOT edit |
| `agentic_core/L2_execution/apps_rg_l2_binding.py` | May inspect, NOT edit |
| `agentic_core/` (any file) | Zero edits |

### Required App-Local Creation

If PA/L2 bindings are missing or broken:

| Missing Component | Create At |
|-------------------|-----------|
| PA binding | `apps_rg/runtime/bindings/pa_binding.py` |
| L2 binding | `apps_rg/runtime/bindings/l2_binding.py` |
| L2 lane orchestration | `apps_rg/runtime/bindings/l2_lane_orchestrator.py` |
| Locked section contracts | `apps_rg/runtime/contracts/locked_section_contracts.py` |

---

## 21. Confirmations (Final Executable v4)

| Confirmation | Status |
|--------------|--------|
| **Plan updated to v4 — FINAL EXECUTABLE** | ✅ CONFIRMED |
| **No implementation files changed** | ✅ CONFIRMED — Plan-only updates |
| **No agentic_core changes** | ✅ CONFIRMED — Zero edits to core/shims |
| **DOCX SSOT replaced with JSON SSOT** | ✅ UPDATED — Canonical JSON is runtime SSOT |
| **Canonical JSON paths defined** | ✅ ADDED — `amit_ayer_base_resume_v1.json` + `active_base_resume_pointer.json` |
| **Base resume refresh workflow** | ✅ ADDED — Versioned, approval-bound, separate from JD customization |
| **STOP 0-15 gates added** | ✅ ADDED — 17 mandatory stop points with receipts (0-15 plus 4A, 4B) |
| **STOP 4A added** | ✅ ADDED — Prompt export and ChatGPT review gate (mandatory before runtime wiring) |
| **STOP 4B added** | ✅ ADDED — ChatGPT review incorporation gate (mandatory before W3) |
| **STOP-to-wave mapping added** | ✅ ADDED — Each wave ends at defined STOP |
| **W3 blocked until STOP 4B PASS** | ✅ ADDED — Runtime wiring cannot proceed until prompt review complete |
| **Lane temperature profiles added** | ✅ ADDED — Per-lane temperature ranges |
| **Temperature calibration method** | ✅ ADDED — Sweep low/mid/high, select highest passing |
| **STOP 14 (temperature proof)** | ✅ ADDED — Calibration verification |
| **Section metric suite added** | ✅ ADDED — 15 global metrics, granular tracking |
| **section_metric_receipt.json schema** | ✅ ADDED — Artifact schema defined |
| **STOP 15 (metric receipt proof)** | ✅ ADDED — Metric verification |
| **Updated DoD (25 items)** | ✅ UPDATED — New DoD for JSON SSOT, STOP gates, temperature, metrics |
| **Section source hashes required** | ✅ ADDED — 5 hash fields per section |
| **Explicit L2 count (18 + 2)** | ✅ ADDED — Generation, validator, final, deterministic nodes |
| **L3 orchestration order (22 steps)** | ✅ ADDED — Exact execution order with dependencies |
| **Hardened Unify rules** | ✅ ADDED — 6 bullets, LIGHT_PROTECTED default, metric preservation |
| **Hardened IBM rules** | ✅ ADDED — 5 bullets, 0 HEAVY, forbidden terms list |
| **Hardened narrative rules** | ✅ ADDED — 1 sentence, no metric repetition, no new claims |
| **Hardened competency rules** | ✅ ADDED — 8 categories, overlap check, anti-repetition |
| **Neutered final_unify_v2** | ✅ ADDED — Allowed/forbidden operations defined |
| **Runtime payload tests** | ✅ ADDED — 10 payload isolation tests |
| **No-patch rule** | ✅ ADDED — Create from scratch, old prompts reference-only |
| **Gap matrix with 41 items** | ✅ CONFIRMED |
| **Retirement/replacement table** | ✅ CONFIRMED |
| **Wave list with W2A-W2D subwaves** | ✅ CONFIRMED — 12 waves total |
| **Monolith decommission gate** | ✅ CONFIRMED — CI enforcement spec |
| **Receipt requirements per wave** | ✅ CONFIRMED — Artifact schema defined |
| **Test grouping (8 files, 40 cases + 10 payload tests)** | ✅ CONFIRMED |
| **Files inspected list** | ✅ CONFIRMED — 26 files |
| **Top 5 highest-risk gaps** | ✅ CONFIRMED |

### Remaining Known Risks (Post-Hardening v4)

| Risk | Mitigation | Tracking |
|------|------------|----------|
| Windsurf "helpfully" reusing old prompts | No-patch rule + Monolith kill switch | W1-W8 receipts verify |
| Old master_resume.json contamination | **JSON SSOT rule** + runtime payload tests | `test_old_master_resume_blocked` |
| Section drift from source | Section source hashes + **JSON hash validation** | All 5 hash fields |
| Final unify adding content | Neutered operations list + hash detection | `test_final_unify_no_add_authority` |
| Bullet diversity repair creating drift | Optional only, before fact check, preserves IDs | W2B/W2C phase gates |
| Cross-role term contamination (IBM/Unify) | IBM forbidden terms list + payload isolation tests | `test_ibm_payload_isolation` |
| DOCX parsing during normal customization | **JSON SSOT rule** — DOCX only for refresh workflow | `test_no_docx_parsing_in_customization` |
| Canonical JSON mutation during JD tailoring | **JSON is read-only** during customization | `test_json_immutable_in_customization` |
| Temperature drift | **Calibration receipts** track actual temperature | STOP 14 verification |
| Missing metric tracking | **Section metric receipt** required per lane | STOP 15 verification |
| **Prompt precision issues** | **STOP 4A/4B** — ChatGPT review before runtime wiring | STOP 4A/4B receipts |
| **Windsurf over-interpreting ChatGPT feedback** | **STOP 4B rules** — Only approved corrections, no scope expansion | STOP 4B acceptance criteria |
| **Runtime wiring before prompt review** | **W3 blocked until STOP 4B PASS** | Wave mapping enforcement |

---

### Final Closeout Summary

**1. Updated plan path:**  
`.cursor/plans/apps-rg-prompt-layer-full-reset-plan.md`

**2. Confirmation only plan artifact changed:**  
✅ CONFIRMED — Zero implementation file edits

**3. Confirmation agentic_core unchanged:**  
✅ CONFIRMED — No core/shim modifications

**4. DOCX SSOT replaced with canonical JSON SSOT:**  
✅ CONFIRMED — `apps_rg/resume/base/amit_ayer_base_resume_v1.json` + pointer

**5. Canonical JSON path and pointer path added:**  
✅ CONFIRMED — Section 2.4 updated with paths and refresh workflow

**6. STOP 0-15 added:**  
✅ CONFIRMED — Section 3 with all stop point definitions

**7. STOP-to-wave mapping added:**  
✅ CONFIRMED — Wave mapping table in Section 3

**8. Lane temperature profile table added:**  
✅ CONFIRMED — Section 4 with per-lane ranges

**9. STOP 14 added:**  
✅ CONFIRMED — Temperature calibration proof

**10. Section metric suite added:**  
✅ CONFIRMED — Section 5 with 15 global metrics

**11. section_metric_receipt.json schema added:**  
✅ CONFIRMED — Section 5 with full schema

**12. STOP 15 added:**  
✅ CONFIRMED — Section metric receipt proof

**13. Updated DoD summary:**  
✅ CONFIRMED — 25 DoD items including JSON SSOT, STOP gates, temperature, metrics

**14. STOP 4A added (Prompt Export and ChatGPT Review):**  
✅ CONFIRMED — Section 3 with review packet requirements, 12 prompts for review, critical prompts marked

**15. STOP 4B added (ChatGPT Review Incorporation):**  
✅ CONFIRMED — Section 3 with incorporation rules, receipt schema, acceptance criteria

**16. W3 blocked until STOP 4B PASS:**  
✅ CONFIRMED — Wave mapping updated, W3 cannot start until prompt review complete

**17. Remaining known risks:**  
Documented above with mitigations

**18. Explicit statement:**  
> **Plan is finalized for wave-by-wave implementation, pending Amit approval.**

---

*Plan created per user request: "Do a full reset of the apps_rg resume prompt layer"*  
*Hard stance applied: Current prompts are UNTRUSTED until proven compliant*  
*Finalized v4 per Amit requirements: JSON-SSOT, STOP 0-15, temperature calibration, section metrics, hardened section rules*  
*No code changes made outside this plan artifact*  
*Ready for Amit approval and wave-by-wave implementation*

