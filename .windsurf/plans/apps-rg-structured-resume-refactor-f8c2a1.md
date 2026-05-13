---
plan_id: apps-rg-structured-resume-refactor-f8c2a1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Refactor apps_rg to Structured Resume with Tiered Customization

Refactor the apps_rg resume generation pipeline to use a structured source resume JSON with separated narrative/bullets and implement tiered customization strategies per role section, plus add inline runtime executive summary output at end of each run.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Not Started
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — Current apps_rg uses flat text resume source (`source_resume_text` string) with no separation between narrative context and achievement bullets. All sections get same generation treatment regardless of role importance (Unify/IBM vs InsurTech/EY vs Early Career).

- **Complication** — Heavy customization roles (Unify, IBM) need full narrative + bullet rewriting with JD alignment. Medium roles (InsurTech, EY) need light reframing. Early career should copy verbatim with zero customization. Current flat structure cannot support differentiated strategies.

- **Design Decisions from 2026-05-13 Session** —
  1. **Narrative copied verbatim** — No LLM customization; U0 supplies briefing, JD, base resume
  2. **Bullets tiered by role** — Unify (current): Top 3 heavy rewrite, 4-5 moderate, 6 light. IBM: Top 2 moderate, 3-5 light. InsurTech/EY: Light reframe. Early career: Preserve verbatim.
  3. **Provider-neutral prompts** — XML-style sections, no Claude-specific wording, Qwen vLLM compatible
  4. **Anti-invention guardrails** — NO new metrics/clients/tools/domains/scope/titles/impacts without source support. INSUFFICIENT_SOURCE_SUPPORT emitted when evidence inadequate.
  5. **Exact source-span extraction** — Verbatim citation required before rewrite, JSON output with source_span, jd_alignment, rewritten_bullet, blocked_items, status

- **Question** — How do we refactor apps_rg to use structured source resume with narrative/bullet separation and implement tiered customization per role, while also adding inline ASCII runtime summary at pipeline completion?

- **Answer** — Implement `source_resume_v2_structured.json` schema, update exit binding ingestion to produce structured format, refactor PA binding with section-specific prompt strategies, and add runtime executive summary inline output.

---

## Wave Overview

**Waves**: 8 total (W1–W8)
**Total Estimate**: ~6,200 tokens
**Current**: W0 (pre-flight)

---

## Consolidated Section Processing Design

| Section | Pipeline | Narrative | Bullets | Count | Treatment Tier | Rationale |
|---------|----------|-----------|---------|-------|----------------|-----------|
| **Headline** | Agentic (U0-L6) | Single X\|Y\|Z line | N/A | 1 line | **Heavy** | High JD visibility, keyword optimization critical |
| **Executive Summary** | Agentic (U0-L6) | 5-sentence paragraph | N/A | 5 sentences | **Heavy** | Flagship positioning, every sentence needs metric/scope/technical term |
| **Unify** | Agentic (U0-L6) | 1 intro sentence | 6 bullets | 6 | **Top 3: Heavy, 4-5: Moderate, 6: Light** | Current role, highest investment, flagship achievements |
| **IBM** | Agentic (U0-L6) | 1 intro sentence | 5 bullets | 5 | **Top 2: Moderate, 3-5: Light** | Supporting relevance, moderate customization |
| **InsurTech** | Agentic (U0-L6) | 1 intro sentence | 3 bullets | 3 | **Moderate** | Background context, selective JD alignment |
| **EY** | Agentic (U0-L6) | 1 intro sentence | 3 bullets | 3 | **Light** | Older experience, minimal customization |
| **Early Career** | Agentic (U0-L6) | 1 intro sentence | 1 bullet | 1 | **Preserve Verbatim** | Historical record, no customization needed |
| **Competencies** | Agentic (U0-L6) | N/A | 12 entries | 12 | **Moderate** | JD-ranked, 2-4 word noun phrases |
| **Education** | **Verbatim Copy** | Exact from source | N/A | All | **None** | No LLM generation, copy exactly |
| **Certifications** | **Verbatim Copy** | Exact from source | N/A | All | **None** | No LLM generation, copy exactly |

### Treatment Tier Definitions

| Tier | Description | Rewrite Depth | JD Keywords |
|------|-------------|---------------|-------------|
| **Heavy** | Full STAR method, specificity expansion, natural length variation | Complete reframing | First 3 words |
| **Moderate** | Preserve core structure/metric, light injection | Selective reframe | 1-2 keywords |
| **Light** | Minimal changes, grammar/format only | Touch-up only | No forced injection |
| **Verbatim** | Copy exactly from source | No rewrite | N/A |

### Anti-Invention Guardrails (All Agentic Sections)

```
NO new metrics not in source materials
NO new client names not in source materials
NO new tools/technologies not in source materials
NO new domains/industries not in source materials
NO expanded scope beyond source support
NO title claims beyond verified source material
NO impact claims without source backing

If support insufficient: emit INSUFFICIENT_SOURCE_SUPPORT
Output format: JSON with source_span, jd_alignment, rewritten_bullet, blocked_items, status
```

**Wave Manifest**:
- **W1** — Structured JSON Schema + Exit Binding Ingestion | ~800 tokens | STATUS: Not Started
- **W2** — PA Binding Section-Specific Prompt Strategies | ~1,200 tokens | STATUS: Not Started
- **W3** — U0 Payload Synthesizer Structured Resume Support | ~600 tokens | STATUS: Not Started
- **W4** — Inline Runtime Executive Summary Output | ~600 tokens | STATUS: Not Started
- **W5** — CI Gates + Tests + Documentation | ~300 tokens | STATUS: Not Started
- **W6** — Exit Gate Payload Extensions (G21/G22 Critical Gaps) | ~800 tokens | STATUS: Not Started
- **W7** — C0 Evidence Trust & Retrieval Safety (G08/G13) | ~600 tokens | STATUS: Not Started
- **W8** — Identity, Budget, and L6 Firewall (G02/G17/G20/G29) | ~400 tokens | STATUS: Not Started

---

## Wave Structure Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Structured JSON schema + exit binding DOCX→JSON ingestion | ~800 | python-docx available | Not Started | `source_resume_v2_structured.json` produced with all fields |
| W2 | W2.1, W2.2, W2.3 | PA binding section-specific prompt strategies (heavy/light/none) | ~1,200 | LLM prompt format stable | Not Started | Per-section prompts match customization tier |
| W3 | W3.1, W3.2 | U0 payload synthesizer reads structured resume | ~600 | JSON schema backward compat | Not Started | U0 emits `resume_payload` with structured flag |
| W4 | W4.1, W4.2 | Inline ASCII runtime summary at pipeline end | ~600 | Terminal supports UTF-8 | Not Started | Summary prints to stdout + saves to run dir |
| W5 | W5.1, W5.2 | CI gates, tests, documentation updates | ~300 | pytest available | Not Started | All tests pass, gates green |
| W6 | W6.1, W6.2, W6.3 | Exit gate payload extensions (G21/G22 critical gaps) | ~800 | X1 gate packet structure stable | Not Started | All G21/G22 gaps upgraded to ACTIVE |
| W7 | W7.1, W7.2 | C0 evidence trust & retrieval safety (G08/G13) | ~600 | Chroma retrieval available | Not Started | Evidence scoping + injection check active |
| W8 | W8.1, W8.2 | Identity, budget, L6 firewall (G02/G17/G20/G29) | ~400 | L6 shadow infra available | Not Started | Identity binding + budget enforcement active |

---

## Phase-Level Summary Table

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Define Structured Resume Schema | `source_resume_structured.json` reference, schema doc | Field naming, nested structure validation | ~400 | Not Started |
| W1.2 | Update Exit Binding Ingestion | `exit_binding.py:_ingest_docx_to_master_resume` | Parsing DOCX into structured sections, bullet detection | ~400 | Not Started |
| W2.1 | Heavy Customization Prompts (Unify/IBM) | `pa_binding.py:_build_section_prompt` | Full narrative+bullet rewrite with JD alignment | ~500 | Not Started |
| W2.2 | Medium Customization Prompts (InsurTech/EY) | `pa_binding.py:_build_section_prompt` | Light reframing, preserve core story | ~400 | Not Started |
| W2.3 | Competency Bullet Generation | `pa_binding.py:_build_competencies_prompt` | Match base resume bullet style (Category: Skills) | ~300 | Not Started |
| W3.1 | U0 Structured Resume Detection | `payload_synthesizer.py`, `u0_binding.py` | Detect structured vs flat, populate `resume_payload` | ~300 | Not Started |
| W3.2 | Backward Compatibility | `payload_synthesizer.py` | Fall back to flat text if structured not available | ~300 | Not Started |
| W4.1 | Runtime Summary Generator | `runtime_executive_summary.py` (existing), `apps_rg_dispatch.py` | ASCII formatting, inline output | ~300 | Not Started |
| W4.2 | Integrate Summary into Dispatch | `apps_rg_dispatch.py` | Call summary at pipeline end, write to stdout + file | ~300 | Not Started |
| W5.1 | Tests for Structured Resume Pipeline | `tests/_apps_contract/test_structured_resume.py` | Schema validation, ingestion correctness | ~150 | Not Started |
| W5.2 | CI Gate + Documentation | `ops_scripts/ci/check_apps_rg_structured_resume.py`, README updates | Gate checks structured resume availability | ~150 | Not Started |
| W6.1 | Exit Payload Extensions: G21 Schema Gates | `exit_binding.py`, `section_scorer.py` | Headline X\|Y\|Z format, competency bullet count, P0 structure | ~300 | Not Started |
| W6.2 | Exit Payload Extensions: G22 Quality Gates | `exit_binding.py`, `apps_rg_exit_evidence_builder.py` | Metric preservation, early career hash compare, claim tracking | ~300 | Not Started |
| W6.3 | Exit Gate Integration Tests | `tests/_apps_contract/test_exit_gate_payloads.py` | Verify G21/G22 gates active with apps_rg fields | ~200 | Not Started |
| W7.1 | C0 Evidence Scoping (G08) | `c0_binding.py`, `airlocks/c0_evidence.py` | Per-section evidence scope profiles, retrieval scoping | ~300 | Not Started |
| W7.2 | Retrieved Content Trust (G13) | `c0_binding.py` | Injection risk detection, content safety scoring | ~300 | Not Started |
| W8.1 | Identity & Isolation (G02/G17) | `u0_binding.py`, `payload_synthesizer.py` | Caller/session/workspace binding, JD/resume isolation | ~200 | Not Started |
| W8.2 | Budget & L6 Firewall (G20/G29) | `l0_binding.py`, `l2_binding.py` | Token/cost/latency caps, L6 shadow learning-only enforcement | ~200 | Not Started |

---

## Wave 1 — Structured JSON Schema + Exit Binding Ingestion

WAVE_ID: W1
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — No shared surface modifications in this wave.

**Phases**:
- **W1.1** — Define Structured Resume Schema v2 | ~400 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W1.2** — Update Exit Binding DOCX→JSON Ingestion | ~400 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO

**Acceptance**:
- `source_resume_v2_structured.json` schema defined with all required fields
- Exit binding `_ingest_docx_to_master_resume` produces structured JSON from DOCX
- `header` (name, headline, contact), `executive_summary`, `experience[]` (company, location, title, date_range, narrative, bullets[]), `education[]`, `certifications[]`, `competencies[]`
- Early career entry has `narrative: null`, bullets[] with single entry
- Unify/IBM entries have full narrative + 5-6 bullets
- InsurTech/EY entries have narrative + 3 bullets
- **Design principle**: Narrative intro sentences are copied verbatim from source (no LLM customization). Only achievement bullets go through agentic spine with tiered treatment.

---

## Wave 2 — PA Binding Section-Specific Prompt Strategies

WAVE_ID: W2
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Provider-Nutral Bullet Rewrite Prompt (Unify tiered: Top 3 Heavy, 4-5 Moderate, 6 Light) | ~500 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W2.2** — Medium/Light Customization Prompts (IBM/InsurTech/EY/Early Career) | ~400 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W2.3** — Competency & Verbatim Section Prompts (Competencies, Education, Certifications) | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO

**Acceptance**:
- PA binding detects section type from `experience[].company`
- **Unify**: 6 bullets through agentic spine — Top 3: HEAVY rewrite (STAR, JD keywords first 3 words), Bullets 4-5: MODERATE reframe, Bullet 6: LIGHT touch/preserve
- **IBM**: 5 bullets through agentic spine — Top 2: MODERATE reframe, Bullets 3-5: LIGHT touch
- **InsurTech/EY**: 3 bullets through agentic spine — All: LIGHT reframe, preserve core story
- **Early career**: 1 bullet — COPY VERBATIM, NO LLM generation
- **Competencies**: 12 entries, JD-ranked, 2-4 word noun phrases
- **Education/Certifications**: COPY VERBATIM, no agentic processing
- **Provider-neutral prompt structure**: XML-style sections (`<task>`, `<source_materials>`, `<instructions>`, `<output_format>`), no Claude/Anthropic-specific wording
- **Anti-invention rules**: Strict enforcement — NO new metrics, clients, tools, domains, scope, titles, or impacts without source support. Emit `INSUFFICIENT_SOURCE_SUPPORT` when evidence inadequate.
- **JSON output**: source_span, jd_alignment, rewritten_bullet, blocked_items, status (SUCCESS|INSUFFICIENT_SOURCE_SUPPORT|PRESERVED_VERBATIM)

---

## Wave 3 — U0 Payload Synthesizer Structured Resume Support

WAVE_ID: W3
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Structured Resume Detection & Loading | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W3.2** — Backward Compatibility with Flat Text | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO

**Acceptance**:
- U0 payload synthesizer detects `.json` extension and structured schema version
- Populates `resume_payload` with `structured: true`, `header`, `executive_summary`, `experience[]`, `education[]`, `certifications[]`, `competencies[]`
- Falls back to flat `source_resume_text` if structured JSON not available or schema version mismatch
- `resume_hash` computed over structured content or text accordingly

---

## Wave 4 — Inline Runtime Executive Summary Output

WAVE_ID: W4
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — ASCII Runtime Summary Formatter | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W4.2** — Integrate into Dispatch Pipeline | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO

**Acceptance**:
- At end of `apps_rg_dispatch.py` section pipeline, generate ASCII summary:
```
╔════════════════════════════════════════════════════════════════╗
║           🤖 APPS_RG RUNTIME EXECUTIVE SUMMARY 🤖              ║
╠════════════════════════════════════════════════════════════════╣
║  Target: Brown & Brown | SVP IT Strategy & Innovation        ║
║  Pipeline: U0→L1→L0→C0→PA→L2→Exit→L6 | Duration: 165s          ║
╠════════════════════════════════════════════════════════════════╣
║  ✅ Headline           [P0]  T1   68 words  score: 0.89        ║
║  ✅ Executive Summary  [P0]  T1  142 words  score: 0.85        ║
║  ✅ Unify Narrative    [P0]  T2  198 words  score: 0.82        ║
║  ✅ IBM Experience     [P0]  T2  312 words  score: 0.88        ║
║  ✅ Competencies       [P1]  T2  156 words  score: 0.91        ║
║  ... (5 more sections)                                         ║
╚════════════════════════════════════════════════════════════════╝
```
- Summary prints to stdout (inline) AND saves to `artifacts/apps_rg/runs/<ts>/99_runtime_executive_summary.md`
- Includes per-section: status, P-level, tier, word count, score

---

## Wave 5 — CI Gates, Tests, Documentation

WAVE_ID: W5
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Tests for Structured Resume Pipeline | ~150 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W5.2** — CI Gate + Documentation | ~150 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO

**Acceptance**:
- Tests validate structured JSON schema, ingestion correctness, PA prompt strategies
- CI gate `check_apps_rg_structured_resume.py` verifies `source_resume_structured.json` exists and is valid
- Documentation updates: `apps_rg/RUNBOOK.md`, `apps_rg/AGENTS.md` with new schema and customization tiers

---

## Wave 6 — Exit Gate Payload Extensions (G21/G22 Critical Gaps)

WAVE_ID: W6
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases**:
- **W6.1** — G21 Schema Gates: Headline X\|Y\|Z Format, Competency Bullet Count, P0 Structure | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W6.2** — G22 Quality Gates: Metric Preservation, Early Career Hash Compare, Claim Tracking | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W6.3** — Exit Gate Integration Tests | ~200 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO

**Acceptance**:
- `AppsRgSectionValidationReceipt` populated in `packet.output["apps_rg_section_validation"]` with headline XYZ format regex check
- `competency_bullet_count` validated in Exit gate (3-5 bullets per competency section)
- `p0_narrative_bullets_required` pre-L2 structure check in PA binding
- `AppsRgMetricPreservationEnvelope` in `packet.evidence_bundle["apps_rg_metrics"]` with quantified claim-to-source binding
- `early_career_hash_compare` verifies P2 sections match source resume SHA256
- All G21/G22 gaps upgraded from GAP → ACTIVE status in canonical gate table

---

## Wave 7 — C0 Evidence Trust & Retrieval Safety (G08/G13)

WAVE_ID: W7
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: G

**Phases**:
- **W7.1** — C0 Evidence Scoping (G08): Per-section evidence scope profiles | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W7.2** — Retrieved Content Trust (G13): Injection risk detection | ~300 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO

**Acceptance**:
- `AppsRgSectionEvidenceScope` populated in `packet.final_evidence_contract["apps_rg_evidence_trust"]`
- Per-section Chroma query hashes, retrieved chunk counts, and scoping metadata
- `injection_risk_score` computed for retrieved content (0.0-1.0 scale)
- `content_safety_verdict` in ["clean", "suspicious_patterns", "instruction_injection"]
- G08 and G13 gaps upgraded from GAP → ACTIVE status

---

## Wave 8 — Identity, Budget, and L6 Firewall (G02/G17/G20/G29)

WAVE_ID: W8
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: H

**Phases**:
- **W8.1** — Identity & Isolation (G02/G17): Caller/session/workspace binding | ~200 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO
- **W8.2** — Budget & L6 Firewall (G20/G29): Token/cost/latency caps | ~200 tokens | PHASE_STATUS: Not Started | PHASE_COMPLETE: NO

**Acceptance**:
- `AppsRgIdentityBinding` in `packet.state_diff["apps_rg_identity"]` with verified caller/tenant/session
- `AppsRgIsolationEnvelope` proves JD/resume/session isolation with fingerprint hashes
- `AppsRgBudgetReceipt` in `packet.exec_trace["apps_rg_budget"]` with per-stage cost tracking
- Token/cost/latency caps enforced at L0 (routing) and L2 (generation)
- `AppsRgLearningFirewallReceipt` in L6 shadow output confirming `learning_only_mode_verified`
- G02, G17, G20, G29 gaps upgraded from GAP/PARTIAL → ACTIVE status

---

## Definition of Done

| DoD | Criterion | Verification | Priority |
|-----|-----------|--------------|----------|
| DoD-1 | `source_resume_v2_structured.json` schema defined and validated | Schema file exists, tests pass | P0 |
| DoD-2 | Exit binding produces structured JSON from DOCX | Run `--ingest-master-resume`, output matches schema | P0 |
| DoD-3 | PA binding implements tiered customization (heavy/medium/light/verbatim) | Unit tests for each tier, prompts verified | P0 |
| DoD-3a | **Provider-neutral prompt compliance** | Tests verify: no Claude/Anthropic wording, no retrieval language, XML structure, anti-invention rules | P0 |
| DoD-4 | U0 payload synthesizer supports structured + flat fallback | Test both paths, verify `resume_payload` | P0 |
| DoD-5 | Inline ASCII runtime summary at pipeline end | Run `apps_rg`, verify stdout output + file | P0 |
| DoD-6 | CI gate passes for structured resume | `check_apps_rg_structured_resume.py` green | P1 |
| DoD-7 | Documentation updated (RUNBOOK.md, AGENTS.md) | Read docs, verify schema + tiers documented | P1 |
| DoD-8 | **W6: All G21/G22 Exit gaps ACTIVE** | `headline_xyz_format`, `competency_bullet_count`, `numeric_claim_tracking` enforced | P0 |
| DoD-9 | **W7: G08/G13 evidence trust ACTIVE** | `section_evidence_scope_profile`, `retrieved_content_data_only` enforced | P1 |
| DoD-10 | **W8: Identity/budget/L6 firewall ACTIVE** | `caller_session_workspace_binding`, `resume_generation_budget`, `future_run_learning_only` enforced | P2 |

**Smoke-Run Verification**:
```bash
# DoD-1: Schema validation
python -c "import json; json.load(open('ops_scripts/apps_rg/source_resume_structured.json')); print('Schema OK')"

# DoD-2: Ingestion
python -m apps_rg --ingest-master-resume

# DoD-5: Full pipeline with inline summary
python -m apps_rg \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy" \
  --target-level "EXECUTIVE" \
  --jd-text "..." \
  --source-resume "ops_scripts/apps_rg/source_resume_structured.json"
# Verify ASCII summary prints at end
```

---

## Gap Register

### Canonical Gate Gaps (from Runtime Gate Analysis)

**GAP-G21-1: Headline X|Y|Z Format Validation** (W6)
- Current: Only extracted at ingest, NOT validated at generation time
- Fix: Add `AppsRgHeadlineValidationReceipt` to ExitReviewPacket.output
- Owner: W6.1

**GAP-G21-2: Competency Bullet Count Cardinality** (W6)
- Current: No validation of competency section bullet counts (3-5 required)
- Fix: Add `narrative_bullets_count` to `AppsRgSectionValidationReceipt`
- Owner: W6.1

**GAP-G21-3: P0 Narrative Bullets Structure** (W6)
- Current: No pre-L2 validation that P0 sections have required structure
- Fix: Pre-L2 structure check in PA binding with `structure_check_passed` field
- Owner: W6.1

**GAP-G22-1: Numeric Claim Tracking** (W6)
- Current: No metric-to-source binding validation
- Fix: `AppsRgMetricPreservationEnvelope` in `evidence_bundle["apps_rg_metrics"]`
- Owner: W6.2

**GAP-G22-2: Early Career Hash Compare** (W6)
- Current: No verbatim integrity hash validation for P2 sections
- Fix: SHA256 hash compare in Exit gate with `early_career_hash_compare` field
- Owner: W6.2

**GAP-G08: Section Evidence Scope Profile** (W7)
- Current: No per-section C0 evidence scoping
- Fix: `AppsRgSectionEvidenceScope` in `final_evidence_contract["apps_rg_evidence_trust"]`
- Owner: W7.1

**GAP-G13: Retrieved Content Data Only** (W7)
- Current: No instruction-injection check on retrieved resume content
- Fix: Add `injection_risk_score` and `content_safety_verdict` to C0 retrieval
- Owner: W7.2

**GAP-G02: Caller/Session/Workspace Binding** (W8)
- Current: Basic request_id only, no full identity/tenant/session binding
- Fix: `AppsRgIdentityBinding` in `state_diff["apps_rg_identity"]`
- Owner: W8.1

**GAP-G17: Candidate/JD/Session Isolation** (W8)
- Current: No explicit cross-context contamination check
- Fix: `AppsRgIsolationEnvelope` with JD/resume fingerprint hashes
- Owner: W8.1

**GAP-G20: Resume Generation Budget** (W8)
- Current: No token/cost/latency caps enforced
- Fix: `AppsRgBudgetReceipt` in `exec_trace["apps_rg_budget"]` with per-stage tracking
- Owner: W8.2

**GAP-G29: Future Run Learning Only** (W8)
- Current: L6 learning firewall not explicitly wired for apps_rg
- Fix: `AppsRgLearningFirewallReceipt` in L6 shadow output
- Owner: W8.2

---

### Implementation Waves for Canonical Gate Gaps

| Gap ID | Canonical Gate | Subcheck Name | Wave | Priority |
|--------|---------------|---------------|------|----------|
| GAP-G21-1 | G21 | `headline_xyz_format` | W6 | P0 (Exit Critical) |
| GAP-G21-2 | G21 | `competency_bullet_count` | W6 | P0 (Exit Critical) |
| GAP-G21-3 | G21 | `p0_narrative_bullets_required` | W6 | P0 (Exit Critical) |
| GAP-G22-1 | G22 | `numeric_claim_tracking` | W6 | P0 (Exit Critical) |
| GAP-G22-2 | G22 | `early_career_hash_compare` | W6 | P1 |
| GAP-G08 | G08 | `section_evidence_scope_profile` | W7 | P1 |
| GAP-G13 | G13 | `retrieved_content_data_only` | W7 | P1 |
| GAP-G02 | G02 | `caller_session_workspace_binding` | W8 | P2 |
| GAP-G17 | G17 | `candidate_jd_session_isolation` | W8 | P2 |
| GAP-G20 | G20 | `resume_generation_budget` | W8 | P2 |
| GAP-G29 | G29 | `future_run_learning_only` | W8 | P2 |

---

### Legacy Gaps (Pre-existing)

**GAP-1: Structured vs Flat Migration Path**
- Need backward compatibility during transition period
- Mitigation: U0 detects schema version, falls back gracefully
- Owner: W3

**GAP-2: DOCX Parsing Edge Cases**
- Early career formatting may not parse cleanly into narrative/bullets
- Mitigation: Manual review after ingestion, fallback to flat text if parsing fails
- Owner: W1

**GAP-3: PA Prompt Token Budget**
- Structured resume adds more content to prompts (separate narrative + bullets)
- Mitigation: Monitor token usage, truncate narrative if needed, prioritize bullets
- Owner: W2

**GAP-4: Human-Scored Benchmarks for Resume Sections**
- **Sections Requiring Benchmarks** (Generated content with JD variance):
  - `executive_summary` — Heavy customization, needs quality scoring
  - `experience[].bullets` (Unify, IBM) — Heavy rewrite, needs relevance + quality scoring
  - `competencies` bullets — Generated from 8 categories, needs skill mapping accuracy
  - `headline` — X|Y|Z format compliance, needs JD alignment scoring

- **Sections NOT Requiring Benchmarks** (Verbatim or light reframe):
  - `header.*` — Copy exact from source (name, phone, email, linkedin, github)
  - `experience[].company`, `location`, `title`, `date_range` — Copy exact
  - `experience[].narrative` (InsurTech, EY) — Light reframe, no benchmark
  - `experience[].bullets` (InsurTech, EY) — Mostly preserved
  - `experience[].bullets` (Early Career) — Copy verbatim
  - `education[]`, `certifications[]` — Copy exact

- **Benchmark Acquisition Strategy**:
  | Section | Method | Sample Size | Frequency |
  |---------|--------|-------------|-----------|
  | Executive Summary | Expert review (SVP Engineering peers) | n=20 resumes | Per plan release |
  | Experience Bullets (Unify/IBM) | Hiring manager blind rating (1-5 scale) | n=15 per role | Quarterly |
  | Competencies | Keyword coverage vs JD analysis | Automated | Every run |
  | Headline | X\|Y\|Z format compliance check | Automated | Every run |
  | End-to-end resume | Recruiter "would interview" rate | n=10 recruiters | Per major schema change |

- **Benchmark Storage**: `artifacts/apps_rg/benchmarks/` — JSON files with `{section, sample_id, human_score, judge_score, jd_hash, timestamp}`

- **Calibration Target**: Spearman ρ ≥ 0.80 between human scores and LLM-as-judge scores before judge can substitute for human review

- **Mitigation**: Defer full benchmark corpus to post-W5; W2-W4 use synthetic JD-aligned test cases for validation

---

## Out Of Scope

- ~~Chroma embedding integration (C0)~~ — NOW IN SCOPE (W7: C0 Evidence Trust)
- Semantic cache R1B writeback — separate plan
- LLM judge implementations — separate plan (stubs in place from apps-eval-harness-deferred-e4a1b7)
- Multi-provider ensemble (beyond Qwen) — separate plan
- Real LLM-judge calibration (Spearman ≥ 0.80) — requires human-labeled holdout corpus
- Holdout vs dev eval-set separation — deferred to eval harness plan
- Production-log mining with PII redaction — deferred to eval harness plan

---

## Requirements Summary (from User Feedback)

1. **PDF/DOCX Auto-Resolution**: `--source-resume` with PDF/DOCX path auto-resolves to canonical JSON (W3.P1, already implemented)
2. **Structured Resume Schema**: Separate `narrative` vs `bullets[]`, immutable fields (company, location, title, date, education, certifications)
3. **Tiered Customization**:
   - **Heavy**: Unify + IBM (narrative + bullets, full rewrite with JD alignment)
   - **Heavy**: Competencies (8 categories → bullets matching base resume style)
   - **Medium**: InsurTech + EY (narrative + bullets, light reframing)
   - **None**: Early career (copy verbatim, `narrative: null`)
4. **Inline Runtime Summary**: ASCII table at end of run showing per-section status, P-level, tier, word count, score
5. **Verbatim Fields**: Header (name, phone, email, linkedin, github), company/location/title/date, education, certifications — never modified
6. **Generated Fields**: Headline (X|Y|Z), executive_summary, narrative (if present), bullets (selected/framed)

---

## Verification vs Deferral

| Item | Verified | Deferred |
|------|----------|----------|
| Structured JSON schema | W1.1 | — |
| Exit binding ingestion | W1.2 | — |
| PA tiered prompts | W2 | — |
| U0 structured support | W3 | — |
| Inline summary | W4 | — |
| CI gates + docs | W5 | — |
| **Exit gate payload extensions (G21/G22)** | **W6** | — |
| **C0 evidence trust (G08/G13)** | **W7** | — |
| **Identity/budget/L6 firewall (G02/G17/G20/G29)** | **W8** | — |
| Full bypass test audit | — | W9 (future) |

---

## References

- Source resume structured JSON: `c:/Git/Agentic-Workflow-FRESH/source_resume_structured.json`
- Exit binding: `apps_rg/runtime/bindings/exit_binding.py:_ingest_docx_to_master_resume`
- PA binding: `apps_rg/runtime/bindings/pa_binding.py`
- U0 payload synthesizer: `apps_rg/runtime/u0/payload_synthesizer.py`
- Runtime summary: `apps_rg/runtime/runtime_executive_summary.py`
