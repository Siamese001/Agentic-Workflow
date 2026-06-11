---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-pa-w10-5-section-signal-hardening-d9b3e7.md'
original_relative_path: 'apps-rg-pa-w10-5-section-signal-hardening-d9b3e7.md'
source_sha256: 413c955f0343e4a693a54a54778b38feeb92738581045b0b398f8ff2ff3aff1d
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-pa-w10-5-section-signal-hardening-d9b3e7
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: apps-rg-pa-w10-5-section-signal-hardening-c4f2a1
---

# apps_rg PA W10.5 — Section Signal Hardening (Rev 3: Recruiter-Trust Signal + JD Overfitting Prevention)

Add machine-readable section contracts, structured examples, a quality rubric, a unify template, and in-template pre-output checklist/evidence-tier signals to the apps_rg Prompt Assembly layer — plus a new W10.5.8 wave (executed first) implementing Anthropic/OpenAI best-practice prompt signal standards and recruiter-trust naturalness constraints, closing all 20 original gaps plus 9 new gaps before W11 runtime binding opens.

> **PA boundary**: all constraints in this plan are declarative prompt text and static YAML declarations only. No runtime enforcement, no compile-time semantic blocking, no output interception. HARD_BLOCK/SOFT_WARN labels are instruction severity tags read by the model as declarative guidance — not code gates. Runtime enforcement belongs to W11/Exit/UWG layers.

> **plan_id discipline**: markers use `plan=apps-rg-pa-w10-5-section-signal-hardening-d9b3e7`
> **Supersedes**: `apps-rg-pa-w10-5-section-signal-hardening-c4f2a1` (Notion page 36027693-f55c-81c8-ab71-fde3a4803dde) — that plan is RETIRED; execute from this one only.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: SCOPED_PASS
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W10.5_Rev3
LAST_UPDATED: 2026-05-14

---

## Context (SCQA)

- **Situation** — W1–W10 delivered a governance-grade PA compiler, 8 templates, profiles, contracts, and 249 passing tests. W10.5 Rev 1 planned structural additions (section contracts, examples, rubrics, unify template, BOM fix).
- **Complication** — Research into Anthropic/OpenAI 2025 prompt engineering standards and the recruiter-trust problem (industry surveys report high rejection rates for resumes perceived as AI-generated; em dash overuse and buzzword density are frequently cited as recruiter signals) reveals a second class of gaps beyond the original 20: (a) prompts lack XML-tagged instruction hierarchy, multishot examples with negative/repair pairs, and in-prompt pre-output checklists; (b) templates create JD-overfitting risk by instructing dense keyword alignment without calibration signals; (c) there is no naturalness-guidance list discouraging known AI-associated phrases (em dashes, overused power verbs, corporate buzzwords); (d) outputs have no pre-output checklist step before the model emits content.
- **Question** — How do we harden the apps_rg PA both structurally (contracts/examples/rubrics) AND signal-quality-wise (recruiter-trust naturalness, JD-calibration, Anthropic/OpenAI XML best practices) before W11 runtime binding?
- **Answer** — Execute W10.5.8 first (creating `forbidden_ai_phrases.yaml` and `jd_calibration_contract.yaml` as shared artifacts), then W10.5.0–W10.5.7 consuming those artifacts. W10.5.8 injects: XML-structured instruction hierarchy across all templates, multishot negative/repair examples, a JD overfitting calibration guidance block, a naturalness phrase-guidance list, a pre-output checklist, and a `voice_naturalness` rubric dimension — all as declarative prompt text in `apps_rg`-owned YAML, zero `agentic_core` changes, zero runtime wiring.

---

## Research Basis (W10.5.8 Justification)

### Anthropic Best Practices (2025)
- **XML-tagged instruction hierarchy** *(rationale only — not a local benchmark)*: Anthropic guidance recommends `<instruction>`, `<context>`, `<examples>`, `<candidate_facts>`, `<jd_requirements>`, `<output_format>` tags to separate instruction/context/data. Current templates use prose sections only; XML segmentation is the recommended improvement.
- **Multishot examples**: 3–5 diverse examples (positive + negative + repair) in `<examples>` tags with `<example>` subtags are recommended to steer output format and tone. Current E0 slot has ≤1 inline positive example.
- **Positional bias** *(rationale only)*: Anthropic guidance notes self-check steps placed after context tend to improve output quality. Current templates have no trailing pre-output checklist.
- **Constraint clarity**: "what NOT to do" constraints are explicitly recommended alongside positive instructions. Current templates lack explicit negative-pattern guidance.

### OpenAI Best Practices (2025)
- **Show, don't just tell**: Desired output format articulated through examples, not prose descriptions alone. Critical for the resume output contract.
- **Explicit format constraints with examples**: `Desired format: <field>: <value>` patterns, not open-ended prose.
- **Specific over vague instructions**: "Write a 3–4 sentence summary starting with a seniority clause, citing exactly 2 metrics from candidate_facts, using no em dashes or corporate buzzwords" outperforms "Write a compelling summary."
- **Pre-output self-check**: Step-by-step pre-output checklist before the model emits content improves instruction adherence.

### Recruiter-Trust and Naturalness Research (2025)
*(The following are rationale and motivation for the guidance we encode as declarative prompt constraints. Numbers are from cited external sources and used as implementation motivation, not as local benchmark claims.)*
- Industry surveys (Resume.io 2025, Forbes 2024) report that hiring managers frequently reject resumes perceived as AI-generated at a high rate. The most commonly cited signals are: em dash overuse, generic openers, buzzword density, and lack of specificity.
- **Recruiter-reported naturalness signals** frequently cited in industry surveys:
  - Em dash (—) overuse: commonly flagged as an AI typography marker
  - Overused power verbs without evidence: "Pioneered", "Orchestrated", "Championed", "Spearheaded", "Meticulous", "Dynamic", "Results-driven"
  - Corporate buzzwords: "dynamic landscape", "fostering", "cross-functional synergies", "value proposition", "stakeholder engagement"
  - Repetitive sentence openers across bullets (unnaturally parallel structure)
- **JD overfitting concern**: Resumes that read like the job description rewritten in first person are perceived as low-personalization and may score poorly on AI screening systems that reward specificity and contextual keyword integration over raw keyword frequency.
  - Guideline: keywords should appear within experience narratives, not as disconnected list items
  - Guideline: ≤~15% of bullet word count should mirror JD phrasing verbatim
- **What works**: Specificity, concrete metrics with `[source: X]` provenance, natural keyword integration, voice variation across bullets.

---

## Gap Analysis Source

**Original gap report:** `artifacts/gap_reports/apps_rg_pa_w10_5_section_signal_gap_report_2026_05_14.md`  
**Baseline tests:** 249 passing (76 governance + 173 W6–W10)

### Original 20 Gaps (G-01–G-20)

| Gap ID | Severity | Description |
|---|---|---|
| G-01 | BLOCKER | `section_contracts/` directory missing |
| G-02 | BLOCKER | Executive summary examples missing |
| G-03 | BLOCKER | Unify examples missing |
| G-04 | HIGH | Competencies examples missing |
| G-05 | BLOCKER | `rubrics/` directory missing |
| G-06 | HIGH | No `lead_with_seniority` enforcement in exec summary |
| G-07 | HIGH | Proof-point source not constrained to `candidate_facts` |
| G-08 | HIGH | No line-limit self-check in exec summary |
| G-09 | BLOCKER | No unify template exists |
| G-10 | HIGH | No contradiction-removal instruction |
| G-11 | HIGH | No gap-marking in competencies |
| G-12 | MEDIUM | Cluster ordering advisory-only, not enforced |
| G-13 | HIGH | No MUST_USE/SUPPORTING/GAP/FORBIDDEN evidence tiers |
| G-14 | HIGH | No section-specific evidence pre-selection block |
| G-15 | HIGH | No SELF_CHECK block in any E3 template |
| G-16 | MEDIUM | Many-shot negatives insufficient in E0 |
| G-17 | MEDIUM | No `<instruction_hierarchy>` XML tag in S0 |
| G-18 | HIGH | Self-check not anchored to rubric |
| G-19 | BLOCKER | `max_response_tokens: 200` in BOM — catastrophically undersized |
| G-20 | LOW | Docs/receipt not updated post-W10.5 |

### New Gaps from Research (G-21–G-29)

| Gap ID | Severity | Description |
|---|---|---|
| G-21 | BLOCKER | No XML-tagged context boundaries — model cannot distinguish instruction/context/data |
| G-22 | HIGH | No naturalness phrase-guidance list — em dash, overused openers, buzzwords not discouraged in prompt |
| G-23 | HIGH | No JD overfitting calibration — dense keyword mirroring uninhibited |
| G-24 | HIGH | No pre-output checklist step before model emits content |
| G-25 | HIGH | No voice-variation guidance across bullets (unnaturally parallel structure not discouraged) |
| G-26 | HIGH | No explicit "what NOT to do" constraint block (Anthropic/OpenAI best practice) |
| G-27 | MEDIUM | Multishot examples not wrapped in `<example>` XML subtags |
| G-28 | MEDIUM | No `voice_naturalness` rubric dimension |
| G-29 | LOW | No pre-output checklist block in template (model self-review step absent) |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W10.5.0 | Baseline lock — confirm 249 tests | ✅ DONE | — | — |
| W10.5.1 | Section contracts (exec_summary, unify, competencies) | ✅ DONE | — | 3 yaml |
| W10.5.2 | Examples with XML `<example>` tags (exec_summary, unify, competencies) | ✅ DONE | — | 3 yaml |
| W10.5.3 | Rubrics (7-dimension incl. voice_naturalness) | ✅ DONE | — | 1 yaml |
| W10.5.4 | Template updates (SELF_CHECK, evidence tiers, gap-marking, XML hierarchy) | ✅ DONE | — | 7 yaml |
| W10.5.5 | Unify template + BOM fix | ✅ DONE | — | 3 yaml |
| W10.5.6 | Tests (~66 original + ~18 new = ~84 new) | ✅ DONE | 184 | 2 py |
| W10.5.7 | Docs + receipt update | ✅ DONE | — | 2 files |
| **W10.5.8** | **EXECUTE FIRST** — Naturalness phrase-guidance + JD calibration artifacts (creates shared YAML files consumed by W10.5.1–W10.5.5) | ✅ DONE | — | 2 yaml |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W10.5.0.1 | Run 249-test baseline, record counts | ✅ DONE |
| W10.5.1.1 | executive_summary_contract.yaml | ✅ DONE |
| W10.5.1.2 | unify_contract.yaml | ✅ DONE |
| W10.5.1.3 | competencies_contract.yaml | ✅ DONE |
| W10.5.1.4 | prompt_registry.yaml contract refs | ✅ DONE |
| W10.5.2.1 | executive_summary_examples.yaml (XML-tagged) | ✅ DONE |
| W10.5.2.2 | unify_examples.yaml (XML-tagged) | ✅ DONE |
| W10.5.2.3 | competencies_examples.yaml (XML-tagged) | ✅ DONE |
| W10.5.3.1 | section_quality_rubrics.yaml (7 dims incl. voice_naturalness) | ✅ DONE |
| W10.5.4.1 | strategic_tailor_v1 + generate_scratch_v1 updates | ✅ DONE |
| W10.5.4.2 | tailor_existing_v1 + enhance_current_v1 updates | ✅ DONE |
| W10.5.4.3 | E4 template S0 XML hierarchy tag | ✅ DONE |
| W10.5.5.1 | unify_v1.yaml template | ✅ DONE |
| W10.5.5.2 | BOM max_response_tokens fix (200 → 1800) | ✅ DONE |
| W10.5.5.3 | prompt_registry.yaml + prompt_bom.yaml unify entry | ✅ DONE |
| W10.5.6.1 | test_w10_5_pa_signal_hardening.py (130 tests) | ✅ DONE |
| W10.5.6.2 | test_w10_5_pa_boundary_governance.py (54 tests) | ✅ DONE |
| W10.5.6.3 | Full regression rerun — 184 W10.5 + 249 baseline = 433 total | ✅ DONE |
| W10.5.7.1 | docs/guides/apps_rg_pa_prompt_contract.md update | ✅ DONE |
| W10.5.7.2 | artifacts/apps_rg/pa_prompt_contract_receipt.json update | ✅ DONE |
| **W10.5.8.1** | **FIRST** — forbidden_ai_phrases.yaml — naturalness phrase-guidance list | ✅ DONE |
| **W10.5.8.2** | **FIRST** — jd_calibration_contract.yaml — overfitting calibration guidance | ✅ DONE |
| W10.5.8.3 | All E3/E4 templates: NATURALNESS_GUIDANCE block in I0 (refs forbidden_ai_phrases.yaml) | ✅ DONE |
| W10.5.8.4 | All E3 templates: JD_CALIBRATION_GUIDANCE block in I0 (refs jd_calibration_contract.yaml) | ✅ DONE |
| W10.5.8.5 | All E3 templates: PRE_OUTPUT_CHECKLIST block (declarative, immediately before R0) | ✅ DONE |
| W10.5.8.6 | test_w10_5_pa_signal_hardening.py + boundary tests (rolled into W10.5.6.1–6.2) | ✅ DONE |

---

## Out Of Scope

- No `agentic_core` edits of any kind
- No runtime wiring (W11 boundary preserved)
- No model/provider calls, no C0 live retrieval, no L2 execution
- No Exit evaluation, no L4/UWG writes
- PA remains packet builder only throughout this plan
- No changes to existing test files (add new tests only)
- No post-processing of model output at runtime — all hardening is in the prompt declaration
- No runtime output blocking or interception based on phrase detection
- No compile-time semantic evaluation of model output — HARD_BLOCK/SOFT_WARN are prompt instruction labels only, not code gates

---

## Wave W10.5.0 — Baseline Lock

WAVE_ID: W10.5.0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W10.5.0.1** — Run full 249-test baseline; verify counts; update receipt with W10.5 section | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `test_apps_rg_pa_governance.py` → 76 passed
- W6–W10 combined → 173 passed
- Receipt has `W10.5_baseline` section with exact counts

---

## Wave W10.5.1 — Section Contracts

WAVE_ID: W10.5.1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W10.5.1.1** — `apps_rg/prompt_assembly/section_contracts/executive_summary_contract.yaml` | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.1.2** — `apps_rg/prompt_assembly/section_contracts/unify_contract.yaml` | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.1.3** — `apps_rg/prompt_assembly/section_contracts/competencies_contract.yaml` | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.1.4** — Add `section_contract_refs` to `prompt_registry.yaml` entries | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Closes gaps:** G-01

> **Artifact dependency**: W10.5.1 `executive_summary_contract.yaml` references `forbidden_ai_phrases.yaml#generic_openers`. W10.5.8.1 must complete before W10.5.1.1 is authored.

**`executive_summary_contract.yaml` required fields:**
- `lead_with_seniority: required`
- `proof_points: {min: 1, max: 2, source: candidate_facts_only}`
- `max_lines: 4`, `max_words: 60`
- `naturalness_guidance_ref: forbidden_ai_phrases.yaml#generic_openers` — these phrases are declared as discouraged in the prompt; they are prompt-level guidance, not compile-time blocks
- `discouraged_adjectives: [proven, accomplished, seasoned, dynamic, results-driven, passionate, dedicated]` — listed in prompt as "do not open with" guidance
- `pre_output_checklist_required: true`, `citation_required: true`
- `jd_mirror_guidance_fraction: 0.20` — prompt instructs model to keep JD phrasing below ~20% of sentence content; not a compile-time gate

**`unify_contract.yaml` required fields:**
- `no_new_claims: required`, `remove_contradictions: required`
- `contradiction_types: [date_overlap, title_inflation, metric_inconsistency, scope_inflation]`
- `summary_claims_must_appear_in_experience: required`
- `no_filler_for_removed_content: required`

**`competencies_contract.yaml` required fields:**
- `evidence_required: candidate_facts_only`
- `jd_gap_marking: required`
- `gap_marker_format: "[Gap: {jd_skill} — no supporting evidence]"`
- `cluster_ordering: jd_priority`
- `forbidden: [jd_only_skills_unlabeled, keyword_stuffing, unsupported_trendy_terms]`

**Acceptance**: All 3 YAML files parse; registry has `section_contract_ref` per E3 entry.

---

## Wave W10.5.2 — Examples (XML-Tagged, Multishot)

WAVE_ID: W10.5.2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Closes gaps:** G-02, G-03, G-04, G-16, G-27

**KEY CHANGE from Rev 1**: Examples must be wrapped in `<examples>` / `<example>` XML tags per Anthropic best practice. W10.5.8.1 must complete before these files are authored so that `anti_ai_compliance` fields can reference the canonical phrase list.

**Phases**:
- **W10.5.2.1** — `apps_rg/prompt_assembly/examples/executive_summary_examples.yaml` | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.2.2** — `apps_rg/prompt_assembly/examples/unify_examples.yaml` | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.2.3** — `apps_rg/prompt_assembly/examples/competencies_examples.yaml` | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Example schema — each entry MUST have:**
```yaml
- id: exec_summary_pos_001
  category: positive   # positive | negative | repair
  section: executive_summary
  seniority_band: EXECUTIVE
  xml_wrapped: true   # content rendered inside <example> tags in compiled prompt
  before: null         # null for positive; original for repair/negative
  after: |
    Technology executive with 18 years leading enterprise AI programs.
    Cut cloud spend by $2.1M in 2023 [source: fact_003]. Delivered 40%
    ops efficiency gain via ML pipeline modernization [source: fact_007].
  citation_preserved: true
  annotation: "Leads with seniority identity, 2 candidate_facts proof points, no generic opener, no em dash, natural sentence variation"
  anti_ai_compliance:
    no_em_dash: true
    no_pioneered_orchestrated: true
    no_corporate_buzzwords: true
    voice_variation_score: high
```

**Negative example requirements (per file ≥ 2)**:
```yaml
- id: exec_summary_neg_001
  category: negative
  annotation: "VIOLATION: opens with passive phrase 'Seasoned executive', uses em dash, no citations, JD keyword mirror"
  ai_giveaway_markers: [em_dash, generic_opener, keyword_mirror, no_citation]
  after: |
    Seasoned executive — bringing 18+ years of cross-functional synergies and
    dynamic leadership to enterprise AI transformations. Passionate about
    fostering innovation across diverse, high-performing teams.
```

**Repair example requirements (per file ≥ 1)**: Shows the `before` (AI-giveaway version) and `after` (corrected), with `repair_actions` list identifying exactly what was fixed.

**Minimum counts**: ≥2 positive, ≥2 negative, ≥1 repair per file.

**Acceptance**: All 3 YAMLs parse; each has `xml_wrapped: true` and `anti_ai_compliance` fields; negative entries have `ai_giveaway_markers`.

---

## Wave W10.5.3 — Rubrics (7 Dimensions)

WAVE_ID: W10.5.3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Closes gaps:** G-05, G-18, G-28

**KEY CHANGE from Rev 1**: 7 dimensions (was 6) — adds `voice_naturalness`. Rubric dimensions are static scoring declarations used by tests against fixture outputs; they are not runtime gates.

**Phases**:
- **W10.5.3.1** — `apps_rg/prompt_assembly/rubrics/section_quality_rubrics.yaml` | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Required 7 dimensions:**

| Dimension | Weight (exec_summary) | Pass Gate | Definition |
|---|---|---|---|
| `evidence_support` | 0.25 | ≥ 0.90 | Fraction of claims backed by `candidate_facts` with citations |
| `target_relevance` | 0.15 | ≥ 0.60 | Fraction mapped to JD requirements |
| `specificity` | 0.20 | ≥ 0.80 | Concrete metrics/tools present; vague descriptors absent |
| `non_generic_language` | 0.20 | ≥ 0.95 | Forbidden openers and phrases from `forbidden_ai_phrases.yaml` absent |
| `section_consistency` | 0.10 | ≥ 0.85 | Summary claims consistent with experience section |
| `citation_preservation` | 0.05 | ≥ 0.90 | `[source: X]` IDs preserved from C0 |
| `voice_naturalness` | **0.05** | **≥ 0.75** | **No em dash; varied sentence openers; ≤3 bullets start with same verb; no unnaturally parallel structure across ALL bullets; no corporate buzzwords — scored against static test fixture outputs only** |

Weights sum = 1.00 per section. `voice_naturalness` failure is `severity: soft_fail` — this means the rubric YAML labels it as advisory; no runtime blocking. Tests assert the label is present, not that output is blocked.

**Acceptance**: YAML parses; 7 dimensions present; weights sum to 1.0; `voice_naturalness` has `severity: soft_fail`.

---

## Wave W10.5.4 — Template Updates

WAVE_ID: W10.5.4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Closes gaps:** G-06, G-07, G-08, G-11, G-12, G-13, G-14, G-15, G-16, G-17, G-18, G-21, G-26 (partial — G-22/G-24/G-25 fully covered in W10.5.8)

> **Artifact dependency**: W10.5.4 injects `<naturalness_guidance>` and `<pre_output_checklist>` blocks that reference `forbidden_ai_phrases.yaml` and `jd_calibration_contract.yaml`. W10.5.8.1 and W10.5.8.2 must complete before W10.5.4.

**Phases**:
- **W10.5.4.1** — Update `strategic_tailor_v1.yaml` + `generate_scratch_v1.yaml` | ~10K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.4.2** — Update `tailor_existing_v1.yaml` + `enhance_current_v1.yaml` | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.4.3** — `<instruction_hierarchy>` XML tag in S0 of all 4 E4 templates | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Full XML restructure for all E3 templates (W10.5.4.1 + W10.5.4.2):**

Each E3 template S0 must be restructured with full XML tagging. All content below is **declarative prompt text** placed inside YAML string fields — not runtime code:

```xml
<instruction_hierarchy>
  <system_authority level="S0">
    [No-fabrication oath content — unchanged from current]
  </system_authority>
  <security_fences level="D0">
    [Injection/override detection fences — unchanged from current]
  </security_fences>
  <governing_contract>
    TRUTH SOURCE: candidate_facts only
    TARGET CONTEXT: jd_requirements and company_brief are targeting inputs, NOT proof of candidate experience
    STYLE ADVISORY: rg_prompt_profile.yaml constraints are advisory and must NEVER override truth constraints
  </governing_contract>
</instruction_hierarchy>
```

I0 slot full XML restructure for all E3 templates:

```xml
<instructions>
  <evidence_tier_selection>
    MUST_USE: candidate_facts entries where alignment_map.status = DIRECT
    SUPPORTING: candidate_facts entries where alignment_map.status = IMPLIED
    GAP: jd_requirements where alignment_map.status = GAP — mark gaps, do not fill
    NOT_FOR_PROOF: jd_requirements — do not cite as evidence of candidate capability
  </evidence_tier_selection>

  <section_instructions>
    <executive_summary>
      LEAD_CLAUSE: Open with seniority/operating identity as first clause (NOT "Seasoned", "Dynamic", "Proven", "Passionate", "Dedicated", "Results-driven")
      PROOF_POINT_SOURCE: candidate_facts only — max 2 proof points — do NOT use company_brief or jd_requirements as proof
      LENGTH: max 4 lines / max 60 words
      PRE_OUTPUT_CHECKLIST: Before producing output verify: ≤4 lines AND ≤60 words AND no discouraged opener AND ≥1 [source: X] citation AND no em dash
    </executive_summary>
    <competencies>
      GAP_MARKING_REQUIRED: For any JD skill with no candidate_facts match output "[Gap: {skill} — no supporting evidence]"
      CLUSTER_ORDER: jd_priority — reorder skill categories so highest-JD-weight categories appear first
      EVIDENCE_REQUIRED: Every listed competency must be supported by ≥1 candidate_facts entry — no JD-only terms without gap marker
    </competencies>
    [... other sections unchanged from current ...]
  </section_instructions>

  <pre_output_checklist>
    ref: apps_rg/prompt_assembly/rubrics/section_quality_rubrics.yaml
    steps:
      1. evidence_support ≥ 0.90 for executive_summary — count citations
      2. no discouraged opener in executive_summary first clause
      3. no JD-only skill without gap marker in competencies
      4. all [source: X] IDs preserved from C0 input
      5. executive_summary ≤4 lines / ≤60 words
  </pre_output_checklist>
</instructions>
```

E0 slot: wrap all examples in `<examples><example>...</example></examples>` XML tags referencing the `examples/` YAML files.

**Acceptance**: All 8 templates parse as valid YAML; `strategic_tailor_v1` I0 contains XML-tagged `<instructions>`, `<evidence_tier_selection>`, `<pre_output_checklist>`; all 8 templates S0 contains `<instruction_hierarchy>`; W6–W10 tests still pass.

---

## Wave W10.5.5 — Unify Template + BOM Fix

WAVE_ID: W10.5.5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Closes gaps:** G-09, G-10, G-19

**Phases**:
- **W10.5.5.1** — `apps_rg/prompt_assembly/templates/unify_v1.yaml` (XML-tagged, includes anti-AI constraints) | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.5.2** — Fix `prompt_bom.yaml` `max_response_tokens: 200` → `1800` | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.5.3** — Add `unify_v1` to `prompt_registry.yaml` + `prompt_bom.yaml` | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**`unify_v1.yaml` must include W10.5.8 declarative constraints from the start** (no-new-claims oath, XML tags, naturalness guidance block, pre-output checklist). W10.5.8.1 and W10.5.8.2 must complete before W10.5.5.1 is authored. See W10.5.8 specification for the full block shapes to embed.

---

## Wave W10.5.6 — Tests (~84 new)

WAVE_ID: W10.5.6
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: G

**Phases**:
- **W10.5.6.1** — `tests/_apps_contract/test_w10_5_pa_signal_hardening.py` (130 tests) | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.6.2** — `tests/_apps_contract/test_w10_5_pa_boundary_governance.py` (54 tests) | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.6.3** — Full regression rerun — 184 W10.5 + 249 baseline = 433 total, EXIT_CODE:0 | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Additional assertions in W10.5.6.4 (vs Rev 1):**
- `<instruction_hierarchy>` XML string present in all 8 templates S0 (string search, not runtime eval)
- `<evidence_tier_selection>` XML string present in all 4 E3 templates
- `<pre_output_checklist>` XML string present in all 4 E3 templates (replaces `<self_check_before_output>`)
- `<examples>` / `<example>` XML strings in E0 slot of all 4 E3 templates
- `xml_wrapped: true` field present in all example YAML entries
- `voice_naturalness` dimension present in rubrics YAML

**W10.5.6 also includes boundary-integrity tests** (see W10.5.8.6 spec for full list):
- assert no new file under `agentic_core/` was created or modified
- assert no new import of `agentic_core` in any `apps_rg/prompt_assembly/` file
- assert no runtime entrypoint or provider reference in any new YAML or Python file added by this plan

**Acceptance**: ≥84 new tests pass; 249 baseline preserved; total ≥ 333.

---

## Wave W10.5.7 — Docs + Receipt

WAVE_ID: W10.5.7
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: H

**Phases**:
- **W10.5.7.1** — `docs/guides/apps_rg_pa_prompt_contract.md` (add §14 contracts, §15 examples, §16 rubrics, §17 anti-AI-detection; update §11 test summary; update §13 remaining gaps) | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.7.2** — `artifacts/apps_rg/pa_prompt_contract_receipt.json` (add W10.5 + W10.5.8 to completed_waves; update total_tests_passed; list all G-01..G-29 as CLOSED) | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**: Docs has §14–§17; receipt `completed_waves` includes `"W10.5"` and `"W10.5.8"`; `total_tests_passed` ≥ 333; all 29 G-* gaps listed as CLOSED.

---

## Wave W10.5.8 — Naturalness Phrase-Guidance + JD Calibration Artifacts *(EXECUTE FIRST — gates W10.5.1–W10.5.5)*

WAVE_ID: W10.5.8
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A-PRE  *(executes before W10.5.0 baseline lock; W10.5.0 then adds these files to the baseline count)*

**Research basis:** See "Research Basis" section above.  
**Closes gaps:** G-21, G-22, G-23, G-24, G-25, G-26, G-27 (part), G-28 (part), G-29

**PA boundary reminder**: All artifacts created in this wave are declarative YAML and declarative prompt-text strings. `HARD_BLOCK` / `SOFT_WARN` labels in YAML are model instruction severity tags — they govern how the model should interpret the constraint, not compile-time code gates. Runtime enforcement of any phrase rule belongs to W11/Exit layers only.

**Phases**:
- **W10.5.8.1** — `apps_rg/prompt_assembly/forbidden_ai_phrases.yaml` — naturalness phrase-guidance list (YAML only) | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.8.2** — `apps_rg/prompt_assembly/jd_calibration_contract.yaml` — JD overfitting calibration guidance (YAML only) | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.8.3** — All 8 templates: inject `<naturalness_guidance>` block in I0 (declarative text ref to forbidden_ai_phrases.yaml) | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.8.4** — All 4 E3 templates: inject `<jd_calibration_guidance>` block in I0 (declarative text ref to jd_calibration_contract.yaml) | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.8.5** — All 4 E3 templates: inject `<pre_output_checklist>` block (declarative prompt instruction listing steps model should follow before emitting output) | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W10.5.8.6** — boundary-integrity tests folded into `test_w10_5_pa_boundary_governance.py` | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

---

### W10.5.8.1 — `forbidden_ai_phrases.yaml` Specification

> **Nature of this file**: Pure YAML declaration — no Python, no imports, no runtime invocation. Labels such as `HARD_BLOCK`/`SOFT_WARN` are instruction-severity metadata that templates embed as declarative model guidance. Tests assert the file parses and contains required keys; tests against fixture outputs assert the guidance is reflected in example quality. No runtime enforcement code.

```yaml
version: "1.0"
description: >
  Naturalness phrase-guidance list for recruiter-trust signal hardening.
  Sourced from industry survey rationale (Resume.io 2025, Forbes 2024, LinkedIn recruiter
  reports 2025) as motivation for the declarative prompt constraints encoded here.
  HARD_BLOCK / SOFT_WARN are prompt instruction-severity labels — not compile gates.
  Referenced by all E3/E4 template naturalness_guidance blocks.

typography:
  em_dash:
    char: "—"
    replacement: ", or restructure sentence"
    severity: HARD_BLOCK     # prompt instruction label — model is instructed "never produce this"
    enforcement_layer: prompt_declaration  # runtime enforcement deferred to W11/Exit
    reason: "Commonly flagged as AI typography marker in recruiter surveys"

power_verbs_out_of_register:
  description: >
    These verbs appear unnaturally formal/elevated when used repeatedly or without
    concrete evidence. AI uses them as default resume power verbs; human writers
    reserve them for genuine exceptional achievements.
  severity: SOFT_WARN   # warn unless used with concrete [source: X] citation
  words:
    - Pioneered
    - Orchestrated
    - Championed
    - Spearheaded
    - Transformed
    - Revolutionized
    - Propelled
    - Catapulted
    - Galvanized
  exception: may use if accompanied by concrete metric from candidate_facts with [source: X]

generic_openers:
  description: "Forbidden as the first clause of executive_summary"
  severity: HARD_BLOCK
  phrases:
    - "Seasoned"
    - "Dynamic"
    - "Proven"
    - "Passionate"
    - "Dedicated"
    - "Results-driven"
    - "Innovative"
    - "Forward-thinking"
    - "Strategic"
    - "Accomplished"
    - "Visionary"
    - "Detail-oriented"
    - "Team player"
    - "Self-starter"
    - "Go-getter"

corporate_buzzwords:
  description: "Phrases that signal AI generation and reduce recruiter trust"
  severity: HARD_BLOCK
  phrases:
    - "dynamic landscape"
    - "fostering innovation"
    - "cross-functional synergies"
    - "value proposition"
    - "stakeholder engagement"
    - "leveraging synergies"
    - "driving meaningful impact"
    - "thought leader"
    - "change agent"
    - "best-in-class"
    - "move the needle"
    - "deep dive"
    - "bandwidth"
    - "circle back"
    - "paradigm shift"
    - "low-hanging fruit"
    - "bleeding edge"
    - "holistic approach"
    - "robust solution"

structural_ai_signals:
  description: "Structural patterns that AI detection systems flag"
  severity: SOFT_WARN
  patterns:
    - id: sentence_starting_with_by
      rule: "No more than 1 bullet per section may start with 'By'"
      reason: "AI structural pattern identified in Forbes 2024 recruiter survey"
    - id: uniform_bullet_parallelism
      rule: "Not all bullets in a section should start with the same verb type"
      reason: "Unnaturally perfect parallel structure is an AI signal"
    - id: zero_typos_unnaturally_polished
      rule: "Minor natural phrasing variation is preferred over uniform polish"
      reason: "AI-detection tools flag spotless prose as machine-generated"
    - id: repeated_verb_openers
      rule: "Max 3 bullets in any section may open with the same verb root"
      reason: "Human writers naturally vary; AI defaults to patterns"

ai_fluency_words:
  description: "Words overused by AI that feel robotic in resume context"
  severity: SOFT_WARN
  words:
    - "Meticulous"
    - "Intricate"
    - "Multifaceted"
    - "Nuanced"
    - "Realm"
    - "Leverage" (as verb)
    - "Utilize" (prefer 'use')
    - "Facilitate"
    - "Interface" (as verb)
    - "Impactful"
    - "Actionable"
    - "Seamlessly"
    - "Robust"
```

---

### W10.5.8.2 — `jd_calibration_contract.yaml` Specification

> **Nature of this file**: Pure YAML declaration encoding guidance that templates embed as declarative model instructions. Threshold values (`max_jd_mirror_fraction`) are prompt guidance targets for the model — they cannot be mechanically enforced at compile time. Static fixture tests may use them to annotate and validate hand-authored example content. Runtime enforcement deferred to W11/Exit.

```yaml
version: "1.0"
description: >
  JD overfitting calibration guidance. Rationale: industry surveys indicate resumes
  perceived as JD-mirrored tend to be rejected for low personalization; keyword
  integration in narrative context is preferred over keyword frequency.
  All thresholds are declarative model guidance targets, not compile-time gates.
  enforcement_layer: prompt_declaration — runtime enforcement deferred to W11/Exit.

overfitting_definition: >
  A resume is JD-overfit when bullet content mirrors JD phrasing verbatim or
  near-verbatim at high density, OR when keywords appear as disconnected lists
  rather than embedded in real experience narratives.

thresholds:
  max_jd_mirror_fraction: 0.15
    description: "Guidance target: keep JD-mirrored phrasing below ~15% of total bullet words"
    enforcement: prompt_declaration  # model is instructed to stay under this; no compile gate
    test_use: static fixture annotation and example validation only
  max_skills_jd_only: 0
    description: "Any JD skill absent from candidate_facts must use gap marker — never list silently"
    enforcement: prompt_declaration  # gap marker instruction is in template text; enforced by tests checking example YAML compliance
  keyword_integration_required: true
    description: "Guidance: keywords should appear in experience narrative context, not disconnected lists"
    enforcement: prompt_declaration

calibration_instructions_for_i0: |
  JD_CALIBRATION_CHECK:
    DO: Use JD requirements as targeting guidance to SELECT which candidate_facts to foreground
    DO: Integrate JD-relevant terms naturally within experience narrative sentences
    DO: Let candidate experience language lead — do not restate JD requirements as achievements
    DO NOT: Mirror JD bullet points as candidate achievements
    DO NOT: Use more than 15% JD-derived phrasing in any section's total word count
    DO NOT: List JD-required skills the candidate does not have without a gap marker
    DO NOT: Inflate scope to match JD by removing qualifications or adding implied experience
    CALIBRATION TEST: Would a recruiter reading both the JD and resume notice the resume reads like the JD rewritten in first person? If yes, revise.

authenticity_signals_to_preserve:
  - Candidate's actual job titles (do not elevate to match JD title)
  - Candidate's actual metric values (do not round up to match JD expectations)
  - Candidate's actual technology names (do not substitute with JD synonyms)
  - Candidate's actual dates (do not reframe tenure to minimize gaps)
  - Candidate's actual scope of responsibility (do not expand to match JD scope)
```

---

### W10.5.8.3 — `NATURALNESS_GUIDANCE` Block (inject into I0 of all 8 templates)

This block is a declarative prompt text string embedded in the I0 instruction slot YAML field of every E3 and E4 template. It is not executable code — the model reads it as instructions:

```yaml
naturalness_guidance_block: |
  <naturalness_guidance>
    ref: apps_rg/prompt_assembly/forbidden_ai_phrases.yaml

    DO NOT PRODUCE (recruiter-trust guidance — these phrases reduce perceived authenticity):
    - Em dash character (—) — replace with comma, semicolon, or restructure sentence
    - Generic openers as first clause of executive_summary: Seasoned, Dynamic, Proven, Passionate,
      Dedicated, Results-driven, Innovative, Forward-thinking, Accomplished, Visionary, Detail-oriented
    - Corporate buzzwords: "dynamic landscape", "fostering innovation", "cross-functional synergies",
      "value proposition", "stakeholder engagement", "driving meaningful impact",
      "thought leader", "holistic approach", "robust solution", "move the needle"

    PREFER ALTERNATIVES (advisory — use if not supported by specific evidence):
    - Power verbs Pioneered, Orchestrated, Championed, Spearheaded, Transformed, Revolutionized:
      only use if paired with a concrete metric from candidate_facts with [source: X]
    - "Meticulous", "Nuanced", "Realm", "Leverage", "Utilize", "Facilitate", "Impactful",
      "Actionable", "Seamlessly", "Robust" — prefer plain specific alternatives
    - Bullet variety: avoid >3 bullets per section starting with the same verb root
    - Avoid all bullets in a section starting with "By"

    PREFERRED ALTERNATIVES:
    - Em dash → comma or period + new sentence
    - "Leveraged" → "Used", "Applied", "Built on"
    - "Utilized" → "Used"
    - "Pioneered" (without evidence) → "Built", "Established", "Launched"
    - "Facilitated" → "Led", "Ran", "Coordinated"
  </naturalness_guidance>
```

---

### W10.5.8.4 — `JD_CALIBRATION_GUIDANCE` Block (inject into I0 of all 4 E3 templates)

Declarative prompt text string embedded in the I0 YAML field. Not executable code:

```yaml
jd_calibration_guidance_block: |
  <jd_calibration_guidance>
    ref: apps_rg/prompt_assembly/jd_calibration_contract.yaml

    CALIBRATION RULES:
    - USE jd_requirements as targeting guidance to select which candidate_facts to foreground
    - DO NOT mirror JD bullet language as candidate achievements
    - NATURAL INTEGRATION: JD-relevant terms must appear inside real experience narratives
    - MAX JD PHRASING: ≤15% of any section's word count may directly mirror JD wording
    - JD-ONLY SKILLS: Any JD skill absent from candidate_facts → gap marker required — never list silently
    
    AUTHENTICITY PRESERVATION:
    - Keep candidate's actual job titles — do not elevate to match JD
    - Keep candidate's actual metric values — do not round up
    - Keep candidate's actual technology names — do not substitute JD synonyms
    - Keep candidate's actual scope — do not expand to match JD expectations

    SELF-TEST: Read the output and ask — does this resume read like the JD rewritten in first person?
    If yes, revise to lead with candidate's own experience narrative.
  </jd_calibration_guidance>
```

---

### W10.5.8.5 — `PRE_OUTPUT_CHECKLIST` Block (inject as final I0 block in all 4 E3 templates, immediately before R0)

Declarative prompt text instructing the model to privately review its draft before emitting the final response. This is a prompt instruction — not a hidden reasoning disclosure requirement, not a generated reasoning trace, not a chain-of-thought tag. The model need not output its checklist steps; the instruction simply asks it to review before emitting:

```yaml
pre_output_checklist_block: |
  <pre_output_checklist>
    Before producing your final output, privately review your draft against these items.
    You do not need to show this review in your output.

    1. Em dash: does the draft contain "—"? Replace each with ", " or restructure the sentence.

    2. Generic opener: does executive_summary begin with a discouraged opener?
       (Seasoned, Dynamic, Proven, Passionate, Dedicated, Results-driven, Innovative,
       Accomplished, Visionary, Detail-oriented, Strategic, Forward-thinking.)
       If yes: rewrite to lead with candidate's role/function + years/scope.

    3. Bullet variety: in any section, do more than 3 bullets start with the same verb root?
       If yes: vary the verb for the excess bullets.

    4. Buzzword check: does the draft contain corporate buzzwords?
       (dynamic landscape, fostering, synergies, value proposition, stakeholder engagement,
       thought leader, holistic, robust, seamlessly, impactful, actionable, move the needle, bandwidth, paradigm.)
       Replace each with specific, concrete language.

    5. JD mirror: does any section read like the JD rewritten in first person?
       If yes: revise to lead with the candidate's own experience narrative.

    6. Citation integrity: every [source: X] ID in the draft maps to a candidate_facts entry.
       No [source: X] ID maps to jd_requirements or company_brief.

    When the draft satisfies all 6 items, emit the final output.
  </pre_output_checklist>
```

---

### W10.5.8.6 — `test_w10_5_naturalness_signal.py` (~20 tests)

| Test | Assertion |
|---|---|
| `test_forbidden_phrases_yaml_parses` | YAML loads without error |
| `test_forbidden_phrases_has_em_dash_entry` | `typography.em_dash` key present with `severity: HARD_BLOCK` and `enforcement_layer: prompt_declaration` |
| `test_forbidden_phrases_has_generic_openers` | ≥10 generic opener phrases present |
| `test_forbidden_phrases_has_corporate_buzzwords` | ≥10 buzzword phrases present |
| `test_forbidden_phrases_has_structural_signals` | ≥3 structural pattern entries |
| `test_jd_calibration_contract_parses` | YAML loads without error |
| `test_jd_calibration_has_mirror_threshold` | `max_jd_mirror_fraction: 0.15` present |
| `test_jd_calibration_has_authenticity_signals` | `authenticity_signals_to_preserve` list with ≥5 items |
| `test_strategic_tailor_has_naturalness_guidance_block` | `<naturalness_guidance>` string in I0 slot |
| `test_strategic_tailor_has_jd_calibration_guidance_block` | `<jd_calibration_guidance>` string in I0 slot |
| `test_strategic_tailor_has_pre_output_checklist_block` | `<pre_output_checklist>` string in I0 slot |
| `test_all_e3_templates_have_naturalness_guidance` | All 4 E3 templates contain `<naturalness_guidance>` |
| `test_all_e3_templates_have_jd_calibration_guidance` | All 4 E3 templates contain `<jd_calibration_guidance>` |
| `test_all_e3_templates_have_pre_output_checklist` | All 4 E3 templates contain `<pre_output_checklist>` |
| `test_all_e4_templates_have_naturalness_guidance` | All 4 E4 templates contain `<naturalness_guidance>` |
| `test_em_dash_not_in_positive_example_content` | All `category: positive` example `after` fields contain no `—` character |
| `test_negative_examples_have_ai_giveaway_markers` | All `category: negative` examples have `ai_giveaway_markers` list |
| `test_rubric_has_voice_naturalness_dimension` | `section_quality_rubrics.yaml` has `voice_naturalness` with `severity: soft_fail` |
| `test_no_agentic_core_files_modified` | `git diff --name-only HEAD` contains no path under `agentic_core/` |
| `test_no_agentic_core_import_in_new_files` | AST scan of all new `apps_rg/prompt_assembly/` Python/YAML files — zero `import agentic_core` or `from agentic_core` |

---

## Execution Details

### W10.5.0.1 — Baseline Lock
```powershell
python -m pytest tests/_apps_contract/test_apps_rg_pa_governance.py --tb=no -q
python -m pytest tests/_apps_contract/test_w6_pa_compiler.py tests/_apps_contract/test_w7_pa_compiler_negative_controls.py tests/_apps_contract/test_w8_pa_templates_e4_e5.py tests/_apps_contract/test_w9_pa_integration_smoke.py tests/_apps_contract/test_w10_pa_guardrails.py --tb=no -q
```

### W10.5.6.6 + W10.5.8.6 — Full Regression
```powershell
python -m pytest tests/_apps_contract/ --tb=short -q
```

---

## Gap Register

**GAP-1 (G-01, G-05, G-09, G-19, G-21) — Structural and XML foundation missing**
- Five BLOCKERs that gate W11. XML tags (G-21) are essential for model attention boundary separation — without them, instruction/context/data bleed into each other, causing hallucinations.

**GAP-2 (G-02, G-03, G-04, G-16, G-27) — Examples absent or not XML-tagged**
- Multishot examples with `<example>` tags are the primary quality calibration mechanism per Anthropic 2025. Negative and repair examples are especially critical — they prevent the AI from defaulting to its own resumé-generation patterns.

**GAP-3 (G-22, G-26) — No naturalness phrase-guidance in templates**
- Em dash, generic openers, and buzzwords are commonly cited by recruiters as reducing resume credibility. Without explicit declarative guidance in the prompt, the model defaults to these patterns. The naturalness_guidance block and forbidden_ai_phrases.yaml encode this as prompt-level discouragement; tests assert the blocks are present and example YAML reflects them. (Source: industry survey rationale — not a local benchmark claim.)

**GAP-4 (G-23, G-25) — JD overfitting uninhibited**
- Resumes that read like the JD rewritten in first person reduce perceived personalization. Industry research motivates the ≤15% JD-mirror guidance target; that target is a declarative model instruction, not a compile gate. Calibration must be baked into the prompt, not left to model judgment.

**GAP-5 (G-24, G-29) — No pre-output checklist step**
- Anthropic guidance recommends trailing self-review steps to improve instruction adherence. The `<pre_output_checklist>` block instructs the model to privately review its draft before emitting output. The model is not required to output its review; the instruction is declarative prompt guidance only.

**GAP-6 (G-06, G-07, G-08, G-15, G-18) — In-template enforcement missing**
- Self-check, seniority lead, proof-point source constraint absent. These are the difference between governance-compliant and actually high-fidelity output.

**GAP-7 (G-11, G-12, G-13, G-14) — Evidence tiers and competency gap-marking absent**
- Model treats all evidence equally. Section-critical facts compete with noise. Skills list silently omits JD requirements.

---

## Definition of Done

DoD-1: All 29 gaps (G-01..G-29) from gap analysis + research are closed, verified by test assertions
- Evidence: `python -m pytest tests/_apps_contract/test_w10_5_*.py -q` → all pass
- Status: TODO

DoD-2: No runtime wiring introduced; no `agentic_core` imports in any new file; PA remains packet builder
- Evidence: `test_no_agentic_core_files_modified` + `test_no_agentic_core_import_in_new_files` pass; `git diff --name-only HEAD` shows zero `agentic_core/` paths; no new L0/L1/L2/Exit/UWG/provider import in any new file
- Status: TODO

DoD-3: ≥84 new W10.5 tests pass + 249 baseline preserved (≥333 total)
- Evidence: `python -m pytest tests/_apps_contract/ -q` shows ≥333 pass, 0 fail
- Status: TODO

DoD-4: `forbidden_ai_phrases.yaml` exists, parses, has em dash entry with `enforcement_layer: prompt_declaration`
- Evidence: `test_w10_5_naturalness_signal.py::test_forbidden_phrases_has_em_dash_entry` passes
- Status: TODO

DoD-5: Docs (§14–§17) and receipt updated; all G-01..G-29 listed as CLOSED in receipt; `W10.5.8` in completed_waves
- Evidence: `pa_prompt_contract_receipt.json` contains `"W10.5.8"` in `completed_waves`
- Status: TODO

DoD-6: Full acceptance gate — all of the following must be true simultaneously:
- All new YAML files (`forbidden_ai_phrases.yaml`, `jd_calibration_contract.yaml`, all `section_contracts/*.yaml`, all `examples/*.yaml`, `rubrics/section_quality_rubrics.yaml`, `templates/unify_v1.yaml`) parse successfully with `yaml.safe_load()` (zero exceptions)
- All 8 existing prompt templates parse as valid YAML after W10.5.4/W10.5.8.3–8.5 edits
- ≥333 tests pass, 0 fail: `python -m pytest tests/_apps_contract/ --tb=short -q`
- 249 baseline tests still pass individually: `python -m pytest tests/_apps_contract/test_apps_rg_pa_governance.py tests/_apps_contract/test_w6_pa_compiler.py tests/_apps_contract/test_w7_pa_compiler_negative_controls.py tests/_apps_contract/test_w8_pa_templates_e4_e5.py tests/_apps_contract/test_w9_pa_integration_smoke.py tests/_apps_contract/test_w10_pa_guardrails.py --tb=short -q`
- `test_no_agentic_core_files_modified` passes (zero `agentic_core/` paths in diff)
- `test_no_agentic_core_import_in_new_files` passes (zero agentic_core imports in new files)
- No new runtime entrypoint, no new provider/model invocation in any file added by this plan
- Status: TODO

---

## Scope Expansion Authorization

```
DISCOVERED_SCOPE: plan=apps-rg-pa-w10-5-section-signal-hardening-d9b3e7 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps-rg-pa-w10-5-section-signal-hardening-d9b3e7 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
```

---

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-pa-w10-5-section-signal-hardening-d9b3e7 wave=<N>
WAVE_COMPLETE: plan=apps-rg-pa-w10-5-section-signal-hardening-d9b3e7 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=apps-rg-pa-w10-5-section-signal-hardening-d9b3e7 phase=<W10.5.N.M>
PLAN_COMPLETE: plan=apps-rg-pa-w10-5-section-signal-hardening-d9b3e7 note="<final outcome>"
```
