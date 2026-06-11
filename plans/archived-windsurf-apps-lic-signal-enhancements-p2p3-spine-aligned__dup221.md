---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-lic-signal-enhancements-p2p3-spine-aligned__dup221.md'
original_relative_path: 'apps-lic-signal-enhancements-p2p3-spine-aligned__dup221.md'
source_sha256: 470f92a8c4ebcbfb5bf27ac2f41f63cea0c13d163e86501b62a4244e0265672b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Signal Enhancements P2/P3 — Spine-Aligned Plan

**Slug**: `apps-lic-signal-enhancements-p2p3-spine-aligned`  
**Status**: Not Started  
**Parent References**: 
- apps-lic-entrypoint-purity-recipe-registry-d4f1a8
- apps-lic-canonical-spine-wireup-e7c2a5
- Old conceptual plan: apps-lic-signal-enhancements-p2p3-f4b8d1 (superseded)

**Created**: 2026-05-05  
**Disposition of Old Plan**: Concepts retained. Implementation wiring superseded by accepted apps_lic spine.

---

## SR_SUMMARY

This plan preserves the P2/P3 signal concepts from the old apps_lic signal plan, but rewires them through the accepted apps_lic spine. P2 improves single-message quality through narrative arc, archetype tone, and competitive landscape context. P3 is split into a follow-up plan or guarded optional wave because multi-touch and resurfacing introduce state, HITL, and L4 read/write concerns. All enhancements must enter through registry-resolved L2 steps, Prompt Assembly, and Exit rubric dimensions. No legacy HOP orchestration, no entrypoint changes, no ad hoc prompts, no direct provider calls, and no direct apps_research calls.

---

## Context: Accepted apps_lic Spine State

- `apps_lic/__main__.py` is a pure shim
- No handmade `l2_callable`
- No callable passing from `apps_lic`
- No legacy fallback
- `run_workflow_lic.py` is quarantined and unreachable
- `agentic_core` runner receives `app_name="apps_lic"`
- `agentic_core` resolves recipes internally
- R4 static path is registry-resolved
- R3R4 managed path is registry-resolved
- `apps_research` bridge executes only as registered L3/L2 managed workflow step
- PromptBOM exists
- `prompt_registry` exists
- Real prompt template bodies exist
- `lic_pa_compiler` emits `CompiledPromptArtifact`
- `compose_draft` consumes `CompiledPromptArtifact`
- Provider gateway requires `CompiledPromptArtifact`
- E5 seals ExitReviewPacket-compatible artifacts
- Exit emits exactly one X3 disposition
- Durable writes only flow Exit V6 → CommitRequest → UWG → L4
- L6 only learns from completed-run exhaust

**Accepted Proof**:
- P0 entrypoint purity accepted
- P1.5 Prompt Assembly plus real prompt bodies accepted
- W2 static R4 recipe accepted
- W3 managed R3R4 workflow accepted
- W4 final acceptance accepted
- Latest proof: 81 passed, 0 failed, 0 skipped

---

## Wave Structure

### P0 — Baseline Preservation and Anti-Regression Guard

**Goal**: Prove the accepted spine remains green before any signal change.

**Scope**:
- `tests/governance/test_apps_lic_entrypoint_purity.py`
- `tests/governance/test_apps_lic_prompt_assembly.py`
- `tests/governance/test_apps_lic_static_recipe.py`
- `tests/governance/test_apps_lic_r3r4_managed_workflow.py`

**Acceptance**:
- 81 passed, 0 failed, 0 skipped remains green
- No changes to `apps_lic/__main__.py`
- No changes to legacy `run_workflow_lic.py` except quarantine docs
- No new direct HOP orchestration
- No new provider SDK calls
- No new ad hoc prompt strings

---

### W1 — P2a Narrative Arc Engine

**Goal**: Add narrative coherence as a spine-aligned L2 E3 context-building step and Exit rubric dimension.

**New Files**:
- `apps_lic/engines/narrative_arc_engine.py`
- `tests/governance/test_apps_lic_signal_p2.py` (seed file)

**Edited Files**:
- `apps_lic/integrations/lic_l2_step_adapters.py`
- `apps_lic/config/apps_lic_static_dag.yaml`
- `apps_lic/config/apps_lic_managed_dag.yaml`
- `apps_lic/prompt_assembly/templates/outreach_draft_v1.yaml`
- `apps_lic/config/exit_rubric.yaml`
- `apps_lic/config/prompt_registry.yaml` (if template hash references need update)

**Placement**:
- E3 Exec before `compile_prompt`
- Produces `NarrativeArc` context
- Prompt Assembly consumes `NarrativeArc` context
- `compose_draft` still consumes `CompiledPromptArtifact`
- Exit evaluates `narrative_coherence`

**Do Not**:
- Edit HOP4DraftAgent directly
- Create ad hoc prompt strings
- Call providers from engine
- Widen authority

---

### W2 — P2b Archetype Tone Calibrator

**Goal**: Add recipient archetype tone calibration as a spine-aligned L2 E3 context-building step.

**New Files**:
- `apps_lic/engines/archetype_tone_calibrator.py`
- `apps_lic/config/archetype_tone_table.yaml`

**Edited Files**:
- `apps_lic/integrations/lic_l2_step_adapters.py`
- `apps_lic/config/apps_lic_static_dag.yaml`
- `apps_lic/config/apps_lic_managed_dag.yaml`
- `apps_lic/prompt_assembly/templates/outreach_draft_v1.yaml`
- `apps_lic/config/exit_rubric.yaml`
- `tests/governance/test_apps_lic_signal_p2.py`

**Placement**:
- E3 Exec before `compile_prompt`
- Consumes `recipient_class`, `recipient_seniority`, `recipient_trigger_vector` if present, company briefing if present
- Produces `ArchetypeToneCalibration` context
- Prompt Assembly consumes tone context
- Exit evaluates `tone_register_fit`

**Do Not**:
- Edit HOP3SenderGroundingAgent directly
- Create direct prompt strings
- Make tone calibration a route decision

---

### W3 — P2c Competitive Landscape Narrative

**Goal**: Add optional company-specific differentiator context when apps_research-backed company briefing exists.

**New Files**:
- `apps_lic/engines/competitive_landscape_engine.py`

**Edited Files**:
- `apps_lic/integrations/lic_l2_step_adapters.py`
- `apps_lic/config/apps_lic_managed_dag.yaml`
- `apps_lic/prompt_assembly/templates/outreach_draft_v1.yaml`
- `apps_lic/config/exit_rubric.yaml`
- `tests/governance/test_apps_lic_signal_p2.py`

**Placement**:
- R3R4 managed path only, after `validate_research_and_build_manifest`
- May also run in R4 only if `PreloadedOutreachContextManifest` already contains company competitive context with source refs
- Produces `CompetitiveLandscapeNarrative` context
- Prompt Assembly consumes it
- `factual_support` requires source refs for any company-specific differentiator claim

**Policy**:
- `confidence < 0.5` means skip, not fabricate
- Missing company briefing means skip, not fabricate
- No `source_ref` means no claim
- `fallback_mode` true must produce no company-specific claim

**Do Not**:
- Call `apps_research` directly
- Create competitive claims from model prior
- Fail a simple recruiter message just because no competitive context exists

---

### W4 — P3 Readiness Design, Not Full Implementation

**Goal**: Do not implement multi-touch, resurfacing, or mutual network mapping yet unless the plan explicitly resolves state, L4, HITL, and scheduling boundaries.

**Reason**: P3 introduces state and workflow complexity:
- Prior touch storage
- Application-status history
- Sequence state
- Mutual contact confidence
- HITL review
- No sending/scheduling boundary
- L4 read/write policy
- L6 outcome learning

**Output**: Create a follow-up design note or child plan section for P3 readiness.

**P3 Concepts Retained** (but deferred):
- `MultiTouchSequencePlanner`
- `StatusAwareResurfacer`
- `MutualNetworkMapper`

**Implementation Deferred Unless** a separate Author-Gate approves:
- State model
- L4 read/write policy
- HITL approval flow
- No-send/no-schedule boundary
- Sequence artifacts
- Replay and Exit rubric policy

**Child Plan Seed**: `apps-lic-signal-enhancements-p3-stateful-followup-readiness`

---

### W5 — Acceptance and Notion Writeback

**Goal**: Run accepted baseline plus P2 tests, update plan status, and register Notion link.

**Acceptance**:
- Baseline 81 tests still green
- All P2 tests green
- No skipped tests
- No spine regressions
- Old plan marked superseded by new plan
- Notion row created or updated

---

## P2A Narrative Arc Engine Spec

**File**: `apps_lic/engines/narrative_arc_engine.py`

### Contracts

```python
@dataclass(frozen=True)
class MessageSection:
    section_id: str
    required_input: str
    forbidden_inputs: list[str]
    transition_marker: str

@dataclass(frozen=True)
class NarrativeArc:
    sections: list[MessageSection]
    arc_coherence_score: float
    arc_breaks: list[str]
    recommended_order: list[str]
    context_ref: str
    source_refs: list[str]
```

### Rules

- Opener should lead with recipient/company/role context when available.
- Opener should not lead with sender biography for executive or hiring-manager outreach.
- Hook must connect to the same problem as proof.
- Proof must map to one sender credibility or repo proof claim.
- Ask must follow logically from proof and ask engine output.
- If evidence is missing, downgrade arc specificity rather than fabricate.
- `arc_coherence_score < 0.6` creates Exit warning or fail depending `recipient_class` policy.
- For recruiter follow-up, narrative arc can be compact and simpler.

### Static R4 Placement

- E3 Exec: `build_narrative_arc_context` before `compile_prompt`

### Managed R3R4 Placement

- After manifest build and before `compile_prompt`

### Prompt Assembly

Update `outreach_draft_v1.yaml` to accept:
- `narrative_arc_context`
- Arc section order
- Transition constraints
- `arc_break` warnings

### Exit

Add dimension:
- `narrative_coherence`
  - Weight: 1.5
  - `fail_closed_when`: `arc_coherence_score < 0.6` AND `recipient_class in [EXECUTIVE, C_LEVEL, CTO, VP_ENG, HIRING_MANAGER]`
  - Contextual/soft for `RECRUITER` and `SENIOR_TA`

### Tests

1. `test_narrative_arc_opener_leads_with_recipient_not_sender_for_exec`
2. `test_narrative_arc_allows_compact_recruiter_arc`
3. `test_narrative_arc_fails_if_proof_disconnected_from_hook`
4. `test_narrative_arc_ask_logically_follows_proof`
5. `test_narrative_arc_context_is_added_before_compile_prompt`
6. `test_narrative_arc_does_not_call_provider_or_retrieve`

---

## P2B Archetype Tone Calibrator Spec

**Files**:
- `apps_lic/engines/archetype_tone_calibrator.py`
- `apps_lic/config/archetype_tone_table.yaml`

### Contracts

```python
@dataclass(frozen=True)
class ArchetypeToneCalibration:
    archetype_id: str
    confidence: float
    detection_signals: list[str]
    vocabulary_boosted: list[str]
    vocabulary_suppressed: list[str]
    sentence_structure_hint: str
    register: str
    context_ref: str
```

### Archetypes

- `TECHNICAL_BUILDER`
- `BUSINESS_EXECUTIVE`
- `RESEARCH_ACADEMIC`
- `TALENT_SCOUT`
- `UNKNOWN`

### Rules

- If confidence is low, use `recipient_class` fallback.
- Do not overfit tone from a single weak trigger.
- Tone calibration affects phrasing constraints, not factual claims.
- Tone calibration must not add new facts.
- Tone calibration must not call provider or retrieval.
- Recruiter/TA tone should prioritize fit-signal and brevity.
- Technical builder tone should avoid empty business jargon.
- Business executive tone should avoid low-level mechanism overload.
- Research academic tone should favor evidence and method.
- Unknown tone defaults to concise professional.

### Prompt Assembly

Update `outreach_draft_v1.yaml` to accept:
- `archetype_tone_calibration`
- `vocabulary_boosted`
- `vocabulary_suppressed`
- `sentence_structure_hint`
- `register`

### Exit

Add dimension:
- `tone_register_fit`
  - Weight: 1.0
  - Soft by default
  - Bound-fail only if `archetype_id` is `TECHNICAL_BUILDER` and message contains configured suppressed phrases above threshold, or if `BUSINESS_EXECUTIVE` message includes excessive low-level implementation detail

### Tests

1. `test_archetype_calibrator_technical_builder_suppresses_business_jargon`
2. `test_archetype_calibrator_business_executive_drops_implementation_detail`
3. `test_archetype_calibrator_unknown_defaults_concise_professional`
4. `test_archetype_tone_context_is_added_before_compile_prompt`
5. `test_archetype_calibrator_does_not_add_factual_claims`
6. `test_archetype_tone_table_validates_required_archetypes`

---

## P2C Competitive Landscape Engine Spec

**File**: `apps_lic/engines/competitive_landscape_engine.py`

### Contracts

```python
@dataclass(frozen=True)
class CompetitiveLandscapeNarrative:
    company_id: str
    differentiator_claim: str
    source_refs: list[str]
    relevance_bridge: str
    confidence: float
    fallback_mode: bool
    context_ref: str
```

### Rules

- Exactly one differentiator sentence maximum in final draft.
- Must be sourced from `apps_research` company briefing or preloaded manifest source refs.
- `confidence < 0.5` means skip.
- Missing company section means skip.
- No `source_refs` means skip.
- `fallback_mode` true means no company-specific differentiator claim.
- Never fabricate competitor facts.
- Never infer competitors from model prior.
- If skipped, output an explicit skipped context receipt so Exit knows no company-specific claim was allowed.

### Placement

- R3R4 managed path after `validate_research_and_build_manifest`.
- R4 static path only if manifest already includes competitive source refs.

### Prompt Assembly

Update `outreach_draft_v1.yaml`:
- Add `competitive_landscape_context` as optional input.
- If absent or `fallback_mode` true, forbid company-specific differentiator claim.
- If present and `source_refs` valid, allow exactly one differentiator sentence.

### Exit

Extend `factual_support`:
- Any company-specific differentiator claim requires `CompetitiveLandscapeNarrative.source_refs`.
- No source refs = fail closed for that claim.

### Tests

1. `test_competitive_landscape_skipped_on_r4_without_source_refs`
2. `test_competitive_landscape_no_fabrication_below_confidence_threshold`
3. `test_competitive_landscape_requires_source_refs_for_company_claim`
4. `test_competitive_landscape_allows_one_sentence_max`
5. `test_competitive_landscape_context_added_after_manifest_validation`
6. `test_competitive_landscape_does_not_call_apps_research_directly`
7. `test_competitive_landscape_fallback_mode_forbids_differentiator_claim`

---

## P3 Readiness / Deferred Implementation

Keep P3 concepts, but **do not implement in this plan** unless Author-Gate explicitly approves a child plan.

### P3a MultiTouchSequencePlanner

Still valid concept, but now requires:
- Sequence artifact schema
- L4 read/write policy
- No scheduling/sending boundary
- HITL approval
- Replay policy
- Exit rubric `sequence_position_fit`
- Durable sequence state or user-provided prior-touch context

### P3b StatusAwareResurfacer

Still valid concept, but now requires:
- Application-status history source
- Prior outreach artifact refs
- New evidence requirement
- User confirmation if rejection/ATS state is inferred
- No auto-send
- L4 policy for status changes

### P3c MutualNetworkMapper

Still valid concept, but now requires:
- `source_ref`-backed mutual signal
- HITL before using any person as intro path
- Privacy policy
- No LinkedIn API assumption
- No invented warm connection

### Child Plan Seed

`apps-lic-signal-enhancements-p3-stateful-followup-readiness`

Do not add P3 implementation files yet unless this child plan is separately approved.

---

## Files In Scope for This Plan

### New
- `apps_lic/engines/narrative_arc_engine.py`
- `apps_lic/engines/archetype_tone_calibrator.py`
- `apps_lic/engines/competitive_landscape_engine.py`
- `apps_lic/config/archetype_tone_table.yaml`
- `tests/governance/test_apps_lic_signal_p2.py`

### Edit
- `apps_lic/integrations/lic_l2_step_adapters.py`
- `apps_lic/config/apps_lic_static_dag.yaml`
- `apps_lic/config/apps_lic_managed_dag.yaml`
- `apps_lic/prompt_assembly/templates/outreach_draft_v1.yaml`
- `apps_lic/config/prompt_registry.yaml` (if template hash registry needs update)
- `apps_lic/config/exit_rubric.yaml`
- Plan/Notion metadata only

### Out of Scope
- `apps_lic/__main__.py`
- `apps_lic/tools/run_workflow_lic.py`
- `apps_lic/integrations/governed_lic_run.py`
- Legacy HOP internals unless adapter boundary cannot call them safely
- Provider SDK calls
- Direct `apps_research` calls
- L4 writes
- Sending/scheduling

---

## Governance Tests

**Create**: `tests/governance/test_apps_lic_signal_p2.py`

### Required Tests

1. `test_signal_p2_baseline_spine_tests_still_green_reference`
2. `test_narrative_arc_opener_leads_with_recipient_not_sender_for_exec`
3. `test_narrative_arc_allows_compact_recruiter_arc`
4. `test_narrative_arc_fails_if_proof_disconnected_from_hook`
5. `test_narrative_arc_ask_logically_follows_proof`
6. `test_narrative_arc_context_is_added_before_compile_prompt`
7. `test_narrative_arc_does_not_call_provider_or_retrieve`
8. `test_archetype_calibrator_technical_builder_suppresses_business_jargon`
9. `test_archetype_calibrator_business_executive_drops_implementation_detail`
10. `test_archetype_calibrator_unknown_defaults_concise_professional`
11. `test_archetype_tone_context_is_added_before_compile_prompt`
12. `test_archetype_calibrator_does_not_add_factual_claims`
13. `test_archetype_tone_table_validates_required_archetypes`
14. `test_competitive_landscape_skipped_on_r4_without_source_refs`
15. `test_competitive_landscape_no_fabrication_below_confidence_threshold`
16. `test_competitive_landscape_requires_source_refs_for_company_claim`
17. `test_competitive_landscape_allows_one_sentence_max`
18. `test_competitive_landscape_context_added_after_manifest_validation`
19. `test_competitive_landscape_does_not_call_apps_research_directly`
20. `test_competitive_landscape_fallback_mode_forbids_differentiator_claim`
21. `test_signal_p2_no_changes_to_apps_lic_main`
22. `test_signal_p2_no_legacy_runner_reachability`
23. `test_signal_p2_no_ad_hoc_prompt_strings`
24. `test_signal_p2_prompt_template_hash_changes_after_template_update`
25. `test_signal_p2_exit_rubric_has_narrative_and_tone_dims`

### Acceptance

- Existing 81 apps_lic governance tests pass
- New 25 P2 tests pass
- Total targeted tests: **106 passed, 0 failed, 0 skipped**
- No changes to `apps_lic/__main__.py`
- No legacy runner reachability
- No skipped tests

---

## Exit Rubric Updates

**Edit**: `apps_lic/config/exit_rubric.yaml`

### Add Dimensions

1. **narrative_coherence**
   - Weight: 1.5
   - `fail_closed_when`: `arc_coherence_score < 0.6` AND `recipient_class in [EXECUTIVE, C_LEVEL, CTO, VP_ENG, HIRING_MANAGER]`
   - Contextual for `RECRUITER` and `SENIOR_TA`
   - Evidence refs: `narrative_arc_context`

2. **tone_register_fit**
   - Weight: 1.0
   - Soft by default
   - Bound-fail only when configured suppressed vocabulary threshold exceeded
   - Evidence refs: `archetype_tone_calibration`

Do not add `sequence_position_fit` in this plan unless P3 child plan is approved.

### Extend factual_support

- Company-specific differentiator claim requires `competitive_landscape_context.source_refs`
- If `competitive_landscape_context.fallback_mode` true, company-specific differentiator claim is forbidden

---

## Prompt Template Update

**Edit**: `apps_lic/prompt_assembly/templates/outreach_draft_v1.yaml`

### Add Optional Inputs

- `narrative_arc_context`
- `archetype_tone_calibration`
- `competitive_landscape_context`

### Add Rules

- Use `narrative_arc_context` to order opener, hook, proof, ask.
- If `arc_breaks` exist, avoid producing final draft unless repair/HITL policy allows.
- Use `archetype_tone_calibration` for register and vocabulary constraints only, not factual claims.
- Use `competitive_landscape_context` only if `fallback_mode` is false and `source_refs` are present.
- If `competitive_landscape_context` is missing or `fallback_mode` true, do not include company-specific differentiator sentence.
- Do not exceed one competitive differentiator sentence.
- Preserve all original forbidden behaviors, `send_mode` restrictions, `claim_permission_map`, `omission_policy`, and origin boundary language.

### Update Template Hash Behavior

- Template changes must change `template_hash` and `prompt_bom_hash` or `prompt_registry_hash` as applicable.

---

## Static DAG Update

**Edit**: `apps_lic/config/apps_lic_static_dag.yaml`

### Insert E3 Context Steps Before compile_prompt

- `build_narrative_arc_context`
- `calibrate_archetype_tone`

Do not add `competitive_landscape_context` to static path unless manifest includes source refs.

### Suggested E3 Order

1. `plan_message`
2. `build_narrative_arc_context`
3. `calibrate_archetype_tone`
4. `maybe_build_competitive_landscape_context_from_manifest` (conditional)
5. `compile_prompt`
6. `compose_draft_using_compiled_prompt_artifact`

---

## Managed DAG Update

**Edit**: `apps_lic/config/apps_lic_managed_dag.yaml`

### After validate_research_and_build_manifest

- `maybe_build_competitive_landscape_context`
- `build_narrative_arc_context`
- `calibrate_archetype_tone`
- `compile_prompt`
- `compose_draft_using_compiled_prompt_artifact`

### Ensure

- Competitive context only after manifest validation
- No R4 compose before manifest valid
- No `apps_research` direct call

---

## ADG / No-Bypass Checks

Plan must require:
- ADG check that `apps_lic/__main__.py` unchanged
- ADG check no new edge from `__main__.py` to signal engines
- ADG check no direct edge from signal engines to provider SDKs
- ADG check no direct edge from `competitive_landscape_engine` to `apps_research`
- ADG check no direct L4 writes from signal engines
- ADG check signal engines only feed step adapters / prompt context / Exit rubric

---

## Notion / Plan Metadata

### Create New Notion Plan Row

```
PLAN_CREATED: slug=apps-lic-signal-enhancements-p2p3-spine-aligned
Status: Not Started
Parent: apps-lic-entrypoint-purity-recipe-registry-d4f1a8
```

### Update Old Notion Plan

- Status: **Superseded**
- Superseded by: `apps-lic-signal-enhancements-p2p3-spine-aligned`
- Reason: Concepts retained, wiring superseded by accepted apps_lic spine.

Do not mark old plan as completed.

---

## Acceptance Criteria

| Criterion | Target |
|-----------|--------|
| New plan created on disk | ✅ |
| Old plan marked Superseded, not Completed | ✅ |
| P2 concepts retained and rewired through accepted spine | ✅ |
| P3 concepts retained but deferred to readiness child plan | ✅ |
| No entrypoint changes | ✅ |
| No legacy orchestration | ✅ |
| No ad hoc prompt strings | ✅ |
| No direct provider SDK calls | ✅ |
| No direct `apps_research` calls outside managed bridge | ✅ |
| Existing 81 apps_lic governance tests remain green | ✅ |
| New 25 P2 tests pass | ✅ |
| Final targeted proof | **106 passed, 0 failed, 0 skipped** |

---

## Non-Goals

- P3 implementation (multi-touch, resurfacing, mutual network) — deferred to child plan
- Changes to `apps_lic/__main__.py`
- Changes to quarantined `run_workflow_lic.py`
- Direct HOP-agent orchestration
- Direct provider SDK calls
- Direct `apps_research` calls outside registered managed workflow bridge
- Direct L4 writes from signal engines
- Sending/scheduling logic
- State management for sequences

---

## References

- Parent plan: `apps-lic-entrypoint-purity-recipe-registry-d4f1a8`
- Spine acceptance: W4 complete, 81 tests green
- Superseded plan: `apps-lic-signal-enhancements-p2p3-f4b8d1`
- Child plan seed: `apps-lic-signal-enhancements-p3-stateful-followup-readiness`
