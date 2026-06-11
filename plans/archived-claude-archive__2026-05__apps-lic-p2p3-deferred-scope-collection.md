---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-lic-p2p3-deferred-scope-collection.md'
original_relative_path: '_archive\\2026-05\\apps-lic-p2p3-deferred-scope-collection.md'
source_sha256: cb21b83d832799fd702d75edc127b787eaee891c045e6fe033456ad1a5223569
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic P2/P3 Deferred Scope Collection Plan

**Plan ID:** apps-lic-p2p3-deferred-scope-collection  
**Parent Plan:** apps-lic-p2p3-deferred-scope-activation (framework-only completion)  
**Status:** Waiting  
**Created:** 2026-05-05  
**Activation Trigger:** Infrastructure prerequisites (L4 state tables, L5 HITL policy, template governance, C0 FEC binding)

---

## 1. Executive Summary

This plan is a **collection container** for all deferred scope from the parent `apps-lic-p2p3-deferred-scope-activation` plan. The parent plan was marked as Completed (framework-only) because all work streams were blocked on external dependencies. This collection plan preserves the deferred scope for activation when infrastructure prerequisites are met.

**Scope Taxonomy:**
- 6 major work streams (24k tokens estimated)
- 3 distinct blocker categories: governance, infrastructure, cross-app integration

---

## 2. Deferred Scope Inventory

### 2.1 P2.1 Prompt Template Updates (~2k tokens)
**Blocker:** Template governance approval  
**Work:** Add P2 context slots to 4 templates (`outreach_draft_v1.yaml`, `outreach_draft_v2.yaml`, `compact_recruiter_arc.yaml`, `exec_positioning.yaml`)

**P2 Contexts to Consume:**
- `NarrativeArc` (from `build_narrative_arc_context`)
- `ArchetypeToneCalibration` (from `calibrate_archetype_tone`)
- `CompetitiveLandscapeContext` (from `build_competitive_landscape_context`)

**Required Slots:**
```yaml
- slot_id: narrative_arc_context
  type: NarrativeArc
  source: build_narrative_arc_context
  required: false  # Graceful degradation

- slot_id: archetype_tone_calibration
  type: ArchetypeToneCalibration
  source: calibrate_archetype_tone
  required: false

- slot_id: competitive_landscape_context
  type: CompetitiveLandscapeContext
  source: build_competitive_landscape_context
  required: false
```

**Exit Criteria:**
- [ ] All 4 templates updated with P2 slot definitions
- [ ] Template hash changes trigger registry updates
- [ ] Graceful fallback when P2 contexts absent

---

### 2.2 P2.2 Exit Rubric Dimension Additions (~3k tokens)
**Blocker:** LLM judge prompt authoring (requires human review)  
**Work:** Add 3 P2-specific evaluation dimensions

| Dimension | Grader Type | Threshold | Description |
|-----------|-------------|-----------|-------------|
| `narrative_coherence` | llm_as_judge | 0.70 | P2a: Arc sections flow logically |
| `tone_register_fit` | llm_as_judge | 0.75 | P2b: Vocabulary matches archetype |
| `differentiator_grounded` | state_check | 1.0 | P2c: Source refs present if claim made |

**Judge Prompts Required:**
- `judge_narrative_coherence_v1`
- `judge_tone_register_fit_v1`

**Exit Criteria:**
- [ ] 3 new dimensions added to `eval_rubrics.yaml`
- [ ] Judge prompts authored for coherence and tone
- [ ] State check schema validates differentiator grounding
- [ ] Threshold profiles updated with new dims

---

### 2.3 Research Bridge Integration (~4k tokens)
**Blocker:** C0 FEC binding across apps  
**Work:** Connect `apps_research` competitive landscape signals to `apps_lic`

**Integration Flow:**
```
apps_research C0 retrieval
  ↓
Company briefing with competitive_landscape section
  ↓
apps_lic manifest includes company_briefing
  ↓
P2c engine extracts competitive signals + source_refs
  ↓
Prompt Assembly receives grounded differentiator
```

**Required Work:**
| Component | Action |
|-----------|--------|
| apps_research | Add competitive landscape to company briefing |
| apps_lic | Enable C0 FEC binding for research sources |
| cert | Add `research_sourced` evidence type |

**Exit Criteria:**
- [ ] apps_research populates competitive signals in briefing
- [ ] Source refs traceable to C0 retrieval
- [ ] P2c confidence boost when research-sourced

---

### 2.4 P3a Multi-Touch Cadence (~6k tokens)
**Blocker:** L4 state tables + Coordination fabric scheduled wake  
**Work:** Multi-touch sequence orchestration with state persistence

**Prerequisites:**
| Prerequisite | Status | ETA |
|--------------|--------|-----|
| L4 `apps_lic_touch_state` table | Not started | TBD |
| Coordination fabric scheduled wake | Not started | TBD |
| Cross-touch identity propagation | Not started | TBD |

**Implementation Waves (when unblocked):**
- W1: State Infrastructure (table creation, UWG integration, migration scripts)
- W2: State Machine (DAG YAML, transition validation, L2 step adapters)
- W3: Cadence Engine (sequence orchestration, timing policy, context carry-forward)

---

### 2.5 P3b Resurfacing Triggers (~4k tokens)
**Blocker:** L5 HITL re-engagement policy  
**Work:** Signal ingestion pipeline with trigger matching

**Prerequisites:**
| Prerequisite | Status | ETA |
|--------------|--------|-----|
| L5 HITL re-engagement policy | Not started | TBD |

**Implementation Waves:**
- W4: Resurfacing Engine (signal ingestion, trigger matcher, context injection)
- W5: HITL Integration (re-engagement policy gates, review workflow, eval harness logging)

---

### 2.6 P3 Infrastructure (~5k tokens)
**Blocker:** Coordination fabric + L4/L5 infrastructure  
**Work:** Supporting infrastructure for P3 features

**Includes:**
- State table schemas
- UWG durable writes for touch state
- State migration scripts
- End-to-end multi-touch test harness
- Resurfacing simulation tests

---

## 3. Activation Prerequisites

This plan transitions from **Waiting** → **In Progress** when ALL of the following are available:

1. **Template governance approves P2 slot additions**
2. **L4 state infrastructure available** (apps_lic_touch_state table)
3. **L5 HITL policy for re-engagement defined**
4. **C0 FEC binding established** (apps_research → apps_lic)

---

## 4. Success Criteria (Deferred Scope Activation)

- [ ] Prompt templates consume all P2 contexts
- [ ] Exit rubric evaluates P2 signal quality
- [ ] Research-sourced competitive signals flow through
- [ ] P3 multi-touch sequences persist and advance
- [ ] Resurfacing triggers fire and route correctly
- [ ] HITL gates review sensitive re-engagements
- [ ] No spine violations (no legacy, no direct provider calls)

---

## 5. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| P2 contexts unused in templates | Medium | Medium | Graceful degradation ensures no harm |
| L4 state tables delayed | High | High | P2 value standalone; P3 non-critical |
| LLM judge calibration fails | Medium | High | Fallback to human evaluation |
| Research bridge permission issues | Medium | Medium | Explicit opt-in for competitive signals |

---

## 6. Related Plans

| Plan | Relationship | Status |
|------|--------------|--------|
| apps-lic-signal-enhancements-p2p3-spine-aligned | Parent | Completed |
| apps-lic-p2p3-deferred-scope-activation | Framework parent | Completed (this session) |
| apps-lic-p3-multi-touch-resurfacing-readiness | Child (Notion: 35727693-f55c-81ff-ab29-df287dc5945a) | Waiting |

---

## 7. Non-Goals

- Real LLM-judge implementations with Spearman ≥ 0.80 calibration
- Production-holdout dataset separation
- PII-redacted production-log mining
- Cross-app YAML consolidation (legacy cleanup)

---

**Plan Status:** `Waiting` — Activation gated on infrastructure prerequisites

**Next Review:** When L4 state table design approved or template governance provides clearance
