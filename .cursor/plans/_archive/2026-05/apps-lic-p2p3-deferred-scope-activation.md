# apps_lic P2/P3 Deferred Scope Activation Plan

**Plan ID:** apps-lic-p2p3-deferred-scope-activation  
**Parent Plan:** apps-lic-signal-enhancements-p2p3-spine-aligned (COMPLETED)  
**Status:** Waiting  
**Created:** 2026-05-05  
**Trigger:** L4 state tables + L5 HITL policy availability

---

## 1. Executive Summary

This plan captures **all deferred scope** from the parent P2/P3 signal enhancement plan. The parent plan successfully delivered P2a/b/c signal engines (narrative arc, archetype tone, competitive landscape) through the accepted apps_lic spine. This plan documents the remaining work required for full P2 integration completion and P3 activation.

**Deferred Scope Taxonomy:**
- P2 Integration Completion (pending prompt/exit updates)
- P3 Multi-Touch & Resurfacing (pending infrastructure)
- Research Bridge Integration (pending C0 FEC binding)

---

## 2. P2 Integration Completion (Deferred from W5)

### 2.1 Prompt Template Updates

**Current State:** P2 engines produce context (`NarrativeArc`, `ArchetypeToneCalibration`, `CompetitiveLandscapeContext`) but prompt templates do not yet consume these contexts.

**Required Work:**

| Template | Update Required | Consumes P2 Context |
|----------|-----------------|---------------------|
| `outreach_draft_v1.yaml` | Add P2 slots | All three |
| `outreach_draft_v2.yaml` | Add P2 slots | All three |
| `compact_recruiter_arc.yaml` | Add narrative arc | P2a only |
| `exec_positioning.yaml` | Add tone + competitive | P2b + P2c |

**Template Slot Additions:**
```yaml
# New slots for Prompt Assembly BOM
slots:
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
- [ ] Graceful fallback when P2 contexts absent (backward compatibility)

**Effort:** ~2k tokens  
**Blocked by:** Template version freeze (requires template governance approval)

### 2.2 Exit Rubric Dimension Additions

**Current State:** Exit rubric evaluates core dimensions but lacks P2-specific signal quality evaluation.

**Required Dimensions:**

| Dimension | Grader Type | Threshold | Description |
|-----------|-------------|-----------|-------------|
| `narrative_coherence` | llm_as_judge | 0.70 | P2a: Arc sections flow logically |
| `tone_register_fit` | llm_as_judge | 0.75 | P2b: Vocabulary matches archetype |
| `differentiator_grounded` | state_check | 1.0 | P2c: Source refs present if claim made |

**Rubric Schema Updates:**
```yaml
# additions to eval_rubrics.yaml
dimensions:
  narrative_coherence:
    grader_type: llm_as_judge
    min_required_score: 0.70
    weight: 0.15
    llm_judge_prompt_ref: judge_narrative_coherence_v1
    
  tone_register_fit:
    grader_type: llm_as_judge
    min_required_score: 0.75
    weight: 0.10
    llm_judge_prompt_ref: judge_tone_register_fit_v1
    
  differentiator_grounded:
    grader_type: state_check
    min_required_score: 1.0
    weight: 0.10
    state_path: competitive_landscape_context.source_refs
    required_when: competitive_landscape_context.differentiator_claim != ""
```

**Exit Criteria:**
- [ ] 3 new dimensions added to eval_rubrics.yaml
- [ ] Judge prompts authored for coherence and tone
- [ ] State check schema validates differentiator grounding
- [ ] Threshold profiles updated with new dims

**Effort:** ~3k tokens  
**Blocked by:** LLM judge prompt authoring (requires human review)

---

## 3. P3 Multi-Touch & Resurfacing (Deferred from W4)

See child plan: `apps-lic-p3-multi-touch-resurfacing-readiness` (Notion: 35727693-f55c-81ff-ab29-df287dc5945a)

### 3.1 Prerequisites Status

| Prerequisite | Status | ETA | Unblocks |
|--------------|--------|-----|----------|
| L4 `apps_lic_touch_state` table | Not started | TBD | P3a state persistence |
| L5 HITL re-engagement policy | Not started | TBD | P3b sensitive triggers |
| Coordination fabric scheduled wake | Not started | TBD | P3a timing |
| Cross-touch identity propagation | Not started | TBD | P3 recipient tracking |

### 3.2 Implementation Waves (When Unblocked)

**W1: State Infrastructure**
- Create `apps_lic_touch_state` table per schema in child plan
- UWG integration for touch state durable writes
- State migration scripts

**W2: State Machine**
- State DAG YAML implementation
- State transition validation gates
- State-aware L2 step adapters

**W3: Cadence Engine**
- Multi-touch sequence orchestration
- Touch timing policy (exec vs recruiter tracks)
- Context carry-forward across touches

**W4: Resurfacing Engine**
- Signal ingestion pipeline
- Trigger matcher implementation
- Resurfacing context injection

**W5: HITL Integration**
- L5 re-engagement policy gates
- HITL review workflow integration
- Decision logging to eval harness

**W6: Acceptance**
- End-to-end multi-touch tests
- Resurfacing simulation tests
- HITL path verification

**Total Effort (when unblocked):** ~15k tokens  
**Dependencies:** L4, L5, Coordination fabric

---

## 4. Research Bridge Integration (Deferred)

### 4.1 C0 FEC Binding for Competitive Landscape

**Current State:** P2c engine uses `company_briefing` from manifest but apps_research does not yet populate competitive landscape signals.

**Required Work:**

| Component | Action | Status |
|-----------|--------|--------|
| apps_research | Add competitive landscape to company briefing | Not started |
| apps_lic | Enable C0 FEC binding for research sources | Not started |
| cert | Add `research_sourced` evidence type | Not started |

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

**Exit Criteria:**
- [ ] apps_research populates competitive signals in briefing
- [ ] Source refs traceable to C0 retrieval
- [ ] P2c confidence boost when research-sourced

**Effort:** ~4k tokens  
**Blocked by:** C0 FEC binding across apps (apps_qna pattern established, needs replication)

---

## 5. Deferred Scope Summary

| Scope Item | Status | Blocker | Est. Effort |
|------------|--------|---------|-------------|
| P2: Prompt template P2 slots | Deferred | Template governance | 2k |
| P2: Exit rubric P2 dimensions | Deferred | LLM judge authoring | 3k |
| P2: Research bridge integration | Deferred | C0 FEC binding | 4k |
| P3a: Multi-touch cadence | Deferred | L4 state tables | 6k |
| P3b: Resurfacing triggers | Deferred | L5 HITL policy | 4k |
| P3: Infrastructure | Deferred | Coordination fabric | 5k |

**Total Deferred Effort:** ~24k tokens  
**Critical Path:** L4 state tables → L5 HITL policy → Coordination fabric

---

## 6. Activation Triggers

This plan transitions from **Waiting** → **Live** when:

1. **L4 state infrastructure available** AND
2. **L5 HITL policy for re-engagement defined** AND
3. **Template governance approves P2 slot additions**

**Activation Sequence:**
1. Author prompt template updates (W1)
2. Author exit rubric dimensions (W2)
3. Implement research bridge (W3)
4. Begin P3 infrastructure (W4+)

---

## 7. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| P2 contexts unused in templates | Medium | Medium | Graceful degradation ensures no harm |
| L4 state tables delayed | High | High | P2 value standalone; P3 non-critical |
| LLM judge calibration fails | Medium | High | Fallback to human evaluation |
| Research bridge permission issues | Medium | Medium | Explicit opt-in for competitive signals |

---

## 8. Success Criteria (Deferred Scope Activation)

- [ ] Prompt templates consume all P2 contexts
- [ ] Exit rubric evaluates P2 signal quality
- [ ] Research-sourced competitive signals flow through
- [ ] P3 multi-touch sequences persist and advance
- [ ] Resurfacing triggers fire and route correctly
- [ ] HITL gates review sensitive re-engagements
- [ ] No spine violations (no legacy, no direct provider calls)

---

**Plan Status:** `Waiting` — Activation gated on infrastructure prerequisites

**Next Review:** When L4 state table design approved
