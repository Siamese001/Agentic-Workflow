---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\apps-shared-extension-plan-d4e5f6.md'
original_relative_path: 'apps-shared-extension-plan-d4e5f6.md'
source_sha256: 6a281cd42aa551009923fdc8b20c0601bf55a331f7c49121342784710cb2b297
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Build Plan: `apps_shared` Extension for Four New Apps
**ADG Ingestion Date:** 2026-03-13
**ADG Artifact:** `adg_indexed_03132026_0745.sqlite`
**Companion Plan:** `new-apps-build-plan-4apps-a1b2c3.md`
**Plan Version:** 1.0
**Status:** DRAFT — Awaiting approval

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

`apps_shared` (L_SHARED layer, 651 modules) is the **highest fan-out layer** in the repo. The hottest single symbol is `apps_shared/types/sovereign_severity_types.py` with fan-out 1,146. Four new apps (`apps_coaching`, `apps_intel`, `apps_comply`, `apps_onboard`) will add approximately 200–300 new L_APP modules, all of which need to import from `apps_shared`.

This plan identifies:
1. **Gaps** — capabilities the four new apps need that `apps_shared` does not currently provide
2. **Extensions** — net-new files to add to existing `apps_shared` subdirectories
3. **Refactors** — existing files that need non-breaking additions (no API breaks)
4. **Guardian registry** — new AGS check IDs
5. **Phased delivery** aligned with the four-app build plan phases

---

## ADG Evidence for Each Gap

All gap assertions below are backed by ADG edge analysis from `adg_indexed_03132026_0745.sqlite`.

---

## Gap 1: Multi-Framework Compliance Control Registry

### Problem
`apps_comply` needs structured control definitions for SOC 2, HIPAA, GDPR, ISO 27001, and EU AI Act. No such registry exists in `apps_shared`. The closest relevant file is `apps_shared/utils/input_guardrail_util.py` (18 KB, input validation patterns) but it does not contain framework control catalogs.

### ADG Evidence
- `reads_policy_state: 1,191` edges — the highest ADG plane count for policy reads; currently these all resolve to `agentic_core` L5 policy modules, not to any app-level control catalog
- `applies_guardrail: 68` edges — all originate in `agentic_core/L5_safety`; `apps_comply` would become the first L_APP-layer guardrail emitter, requiring a shared control catalog to be safe

### New Files

#### `apps_shared/config/compliance_framework_config.py`
```python
"""
Compliance framework control catalog for apps_comply and any future compliance consumers.

Provides structured control definitions for SOC2, HIPAA, GDPR, ISO27001, EU_AI_ACT.
Each FrameworkControl is immutable and identifies the control ID, name, domain,
criticality, and whether it requires human review before passing.
"""
```

**Contents:**
- `ComplianceFramework` enum: `SOC2`, `HIPAA`, `GDPR`, `ISO27001`, `EU_AI_ACT`
- `ControlCriticality` enum: `MANDATORY`, `CONDITIONAL`, `INFORMATIONAL`
- `@dataclass(frozen=True) FrameworkControl`: `control_id`, `name`, `domain`, `criticality`, `requires_human_review: bool`
- `COMPLIANCE_CONTROL_CATALOG: dict[ComplianceFramework, tuple[FrameworkControl, ...]]` — populated with canonical control IDs per framework (e.g., SOC2 CC1.1–CC9.9, GDPR Art 5–49, etc.)
- `get_controls(framework: ComplianceFramework) -> tuple[FrameworkControl, ...]`
- `get_critical_controls(framework: ComplianceFramework) -> tuple[FrameworkControl, ...]`

**Exports:** `ComplianceFramework`, `ControlCriticality`, `FrameworkControl`, `COMPLIANCE_CONTROL_CATALOG`, `get_controls`, `get_critical_controls`

**Layer:** L_SHARED
**Consumers:** `apps_comply/engines/control_mapping_engine.py`, `apps_comply/config/framework_definitions_config.py`

---

## Gap 2: Onboarding Phase & Checkpoint Types

### Problem
`apps_onboard` requires typed data structures for phased plans (30/60/), checkpoints with owner+due-date, stakeholder maps, and work-contract stamping. The existing `apps_shared/types/` contains `checkpoint_manager_types.py` (20 KB) and `execution_orchestrator_types.py` but these are infra-level, not domain-level onboarding constructs.

### ADG Evidence
- `stamps_work_contract: 13` edges — current consumers are all in `agentic_core`; `apps_onboard` is the first L_APP consumer; the contract-stamper type must live in L_SHARED
- `apps_shared/types/checkpoint_manager_types.py` exists but defines `CheckpointState`, `CheckpointRecord` for pipeline state — not suitable as onboarding domain types (would create semantic confusion)

### New Files

#### `apps_shared/types/onboarding_domain_types.py`
**Contents:**
- `OnboardingMode` enum: `PEOPLE`, `SYSTEM`
- `PhaseLabel` enum: `DAY_30`, `DAY_60`, `DAY_90`
- `@dataclass(frozen=True) OnboardingMilestone`: `milestone_id`, `description`, `phase: PhaseLabel`, `owner: str`, `due_offset_days: int`
- `@dataclass(frozen=True) StakeholderEntry`: `name`, `role`, `relationship: Literal["sponsor","peer","report","stakeholder"]`, `contact_channel: str`
- `@dataclass(frozen=True) KnowledgeTransferItem`: `item_id`, `topic`, `source_module`, `estimated_hours: float`
- `@dataclass(frozen=True) WorkContractStamp`: `contract_id`, `issued_by`, `issued_at_iso: str`, `phase: PhaseLabel`, `milestones_count: int`

**Exports:** All types above

**Layer:** L_SHARED
**Consumers:** `apps_onboard/types/onboard_types.py`, `apps_onboard/engines/phased_plan_engine.py`

---

## Gap 3: Coaching Domain Types & STAR Answer Schema

### Problem
`apps_coaching` needs structured types for skill gaps, STAR answers, and coaching plans. Existing `apps_shared/types/` has `tone_model_types.py` (23 KB) and `validation_status_types.py` (23 KB) but no domain types for coaching or interview preparation. The `apps_rg` engines (`gap_closure_engine.py`, `competency_item.py`) contain relevant logic but are L_APP layer and cannot be imported by `apps_shared`.

### ADG Evidence
- `apps_shared/utils/tone_voice_util.py` (20 KB, fan-out in ADG) already has a `ToneProfile` concept; coaching tone extension is a safe non-breaking addition
- `apps_shared/types/` currently has 56 files; coaching domain types are a new semantic area with no collision risk
- The `decorated_by: 16,728` ADG plane includes many `@dataclass` decorated agent types — coaching types must follow the same frozen dataclass pattern

### New Files

#### `apps_shared/types/coaching_domain_types.py`
**Contents:**
- `CoachingMode` enum: `FULL`, `INTERVIEW_ONLY`, `NEGOTIATION_ONLY`, `GAP_ANALYSIS_ONLY`
- `SkillGapSeverity` enum: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- `@dataclass(frozen=True) SkillGap`: `skill_name`, `current_level: int`, `required_level: int`, `severity: SkillGapSeverity`, `evidence: str`
- `@dataclass(frozen=True) STARAnswer`: `question_context`, `situation: str`, `task: str`, `action: str`, `result: str`, `competency_tag: str`
- `@dataclass(frozen=True) CoachingSection`: `heading`, `body`, `phase`, `skill_refs: tuple[str, ...]`
- `@dataclass(frozen=True) NegotiationAnchor`: `anchor_type: Literal["market_rate","competing_offer","value_case"]`, `value`, `currency: str`, `confidence: float`

**Exports:** All types above

**Layer:** L_SHARED
**Consumers:** `apps_coaching/types/coaching_types.py`, `apps_coaching/engines/coaching_plan_engine.py`, `apps_coaching/engines/interview_prep_engine.py`

---

## Gap 4: Competitive Intelligence Domain Types

### Problem
`apps_intel` needs structured types for competitor entries, SWOT quadrants, trend signals, and epistemic claim labeling. The existing `apps_research` has its own internal types but these are L_APP-layer. Epistemic labeling (from `apps_research` pattern) needs to be promoted to L_SHARED so `apps_intel` can also use it without cross-app L_APP imports.

### ADG Evidence
- `apps_research` is L_APP — direct import by `apps_intel` would be a layer violation (both L_APP, cross-app coupling, banned by governance)
- `scores_groundedness: 40` ADG edges — currently all within `agentic_core`; `apps_intel`'s groundedness gate needs a shared `GroundednessScore` type
- The `epistemic label` pattern from `apps_research` (not yet in ADG's L_SHARED) is a shared concept needed by both `apps_intel` and potentially `apps_comply`

### New Files

#### `apps_shared/types/intelligence_domain_types.py`
**Contents:**
- `EpistemicType` enum: `DIRECT_EVIDENCE`, `INTERPRETATION`, `ANALYST_INFERENCE`, `ASSUMPTION` (promotes `apps_research`'s inline pattern to SSOT)
- `@dataclass(frozen=True) GroundednessScore`: `score: float`, `source_count: int`, `grounded_claims: int`, `total_claims: int`
- `@dataclass(frozen=True) CompetitorEntry`: `name`, `category: str`, `strengths: tuple[str, ...]`, `weaknesses: tuple[str, ...]`, `market_position: str`
- `SWOTQuadrant` enum: `STRENGTHS`, `WEAKNESSES`, `OPPORTUNITIES`, `THREATS`
- `@dataclass(frozen=True) SWOTItem`: `quadrant: SWOTQuadrant`, `item`, `epistemic_type: EpistemicType`, `confidence: float`
- `@dataclass(frozen=True) TrendSignal`: `signal_id`, `description`, `horizon: Literal["now","12m","36m"]`, `confidence: float`, `epistemic_type: EpistemicType`

**Exports:** All types above

**Layer:** L_SHARED
**Consumers:** `apps_intel/types/intel_types.py`, `apps_intel/engines/competitor_matrix_engine.py`, `apps_intel/engines/trend_radar_engine.py`

---

## Gap 5: Shared Artifact Emitter Utility

### Problem
Each existing app (`apps_exec`, `apps_rfp`, `apps_research`, `apps_eval`) implements its own `_emit_artifacts` method inline in the orchestrator (visible in `apps_exec/reasoning/ExecOrchestrator.py` lines 155–190). Four new apps will duplicate this pattern again. The ADG already shows `writes_to: 4,751` edges — further proliferation increases this debt.

### ADG Evidence
- ADG `dead_imports: 4,466` — part of this debt comes from duplicated utility code that gets partially used
- `writes_to: 4,751` edges span all layers; consolidating artifact emission to a shared util reduces the `writes_to` surface
- No existing `apps_shared/utils/artifact_emitter_util.py` file exists (verified via ADG `adg_name` search)

### New File

#### `apps_shared/utils/artifact_emitter_util.py`
**Contents:**
- `@dataclass ArtifactSpec`: `filename_pattern: str`, `content: str`, `format: Literal["md","json","csv","txt"]`
- `class ArtifactEmitter`:
  - `__init__(self, output_dir: str, dry_run: bool = False)`
  - `emit(self, specs: list[ArtifactSpec], trace_id: str) -> list[str]` — writes files, returns paths; no-ops in dry_run mode
  - `emit_run_summary(self, summary: dict, trace_id: str) -> str` — writes `run_summary_<trace>.json`
  - Internal: `_resolve_path(pattern, trace_id)` — expands `<trace>` token
- **Dry-run contract:** `emit()` returns empty list and logs `[DRY_RUN]` when `dry_run=True`
- **Determinism:** `trace_id` is the only variable component in file names

**Exports:** `ArtifactSpec`, `ArtifactEmitter`

**Layer:** L_SHARED
**Consumers:** All four new apps' `artifact_emitter_engine.py` files, and optionally refactored into `apps_exec`, `apps_rfp`, `apps_research`, `apps_eval` in a separate cleanup phase

---

## Gap 6: Human Escalation Bus

### Problem
`apps_comply`'s `HumanEscalationEngine` needs a typed escalation mechanism. The ADG shows `escalates_to_human: 12` edges, all in `agentic_core`. No `apps_shared` utility exists for L_APP-layer escalation. A new shared escalation bus prevents `apps_comply` from implementing a one-off pattern.

### ADG Evidence
- `escalates_to_human: 12` — all existing consumers in `agentic_core/L5_safety`; `apps_comply` becomes the first L_APP escalation emitter
- `requires_human_review: 2` edges — too few to be a pattern; `apps_comply` will grow this to a meaningful sub-graph
- If escalation logic lives only in `apps_comply`, it cannot be reused by future compliance-adjacent apps

### New File

#### `apps_shared/utils/human_escalation_util.py`
**Contents:**
- `EscalationSeverity` enum: `ADVISORY`, `REQUIRED`, `BLOCKING`
- `@dataclass EscalationFlag`: `flag_id`, `reason`, `severity: EscalationSeverity`, `raised_by: str`, `context: dict`
- `class HumanEscalationBus`:
  - `__init__(self)`
  - `raise_flag(self, flag: EscalationFlag) -> None`
  - `get_flags(self, severity: EscalationSeverity | None = None) -> list[EscalationFlag]`
  - `has_blocking_flags(self) -> bool`
  - `to_dict(self) -> list[dict]` — serializable for `run_summary.json`
- **Contract:** `BLOCKING` flags must cause orchestrator to set `status = FAILED` unless overridden by `force_continue` flag

**Exports:** `EscalationSeverity`, `EscalationFlag`, `HumanEscalationBus`

**Layer:** L_SHARED
**Consumers:** `apps_comply/engines/human_escalation_engine.py`, `apps_comply/reasoning/ComplyOrchestrator.py`

---

## Gap 7: Multi-App Run Registry (Cross-App Provenance)

### Problem
With 10 apps total (6 existing + 4 new), users will run multiple apps in sequence (e.g., resume → coaching → campaign → intel). There is currently no shared registry to track which apps ran in a session and in what order. The `run_summary.json` per-app provenance is sufficient for single-app audit but not for cross-app lifecycle tracing.

### ADG Evidence
- `agent_executes_agent: 2` — the ADG identifies only 2 cross-agent execution edges currently; cross-app orchestration is absent
- `records_execution_trace: 56` edges — all in `agentic_core`; no L_APP layer currently writes execution traces to a shared registry
- Portfolio-level tracing is a new capability gap, not a refactor

### New File

#### `apps_shared/utils/app_run_registry_util.py`
**Contents:**
- `@dataclass AppRunRecord`: `app_name: str`, `trace_id: str`, `status: str`, `started_at_iso: str`, `completed_at_iso: str | None`, `artifact_paths: list[str]`
- `class AppRunRegistry`:
  - `__init__(self, session_id: str)`
  - `record(self, record: AppRunRecord) -> None`
  - `get_session_trace(self) -> list[AppRunRecord]`
  - `to_dict(self) -> dict` — serializable; includes `session_id`, `records`, `total_apps`, `any_failed`
  - `emit_session_summary(self, output_dir: str) -> str` — writes `session_summary_<session_id>.json`
- **Determinism:** `session_id` is SHA-256 of first app trace_id + timestamp; all records are append-only

**Exports:** `AppRunRecord`, `AppRunRegistry`

**Layer:** L_SHARED
**Consumers:** All four new apps' `__main__.py` entrypoints (optional wiring); `apps_eval` for session-level benchmarking

---

## Gap 8: apps_shared `config/app_guardian_registry.py` — New AGS Entries

The existing `APP_GUARDIAN_REGISTRY` covers only `apps_rg` and `apps_lic`. The `App` literal type must be extended and new `AppGuardianSpec` entries added.

### Required Changes to `apps_shared/config/app_guardian_registry.py`

#### 1. Extend `App` literal type

**Current:**
```python
App = Literal["apps_rg", "apps_lic", "apps_shared", "*"]
```

**Extended:**
```python
App = Literal["apps_rg", "apps_lic", "apps_shared", "apps_coaching", "apps_intel", "apps_comply", "apps_onboard", "*"]
```

#### 2. New AGS Entries

| ID | App | Description | Severity |
|---|---|---|---|
| AGS-010 | apps_coaching | Dead import edges in apps_coaching | medium |
| AGS-011 | apps_coaching | PII gate: ControlPlane not wired to NegotiationScriptEngine | high |
| AGS-012 | apps_intel | Dead import edges in apps_intel | medium |
| AGS-013 | apps_intel | Groundedness gate missing or score threshold < 0.70 | high |
| AGS-014 | apps_comply | Dead import edges in apps_comply | medium |
| AGS-015 | apps_comply | PII gate: ControlPlane.evaluate_output not wired | critical |
| AGS-016 | apps_comply | Human escalation bus not wired for CRITICAL gaps | high |
| AGS-017 | apps_onboard | Dead import edges in apps_onboard | medium |
| AGS-018 | apps_onboard | Checkpoint gate not wired: CheckpointGateEngine absent | medium |

---

## Gap 9: `APPS_PORTFOLIO_OVERVIEW.md` Update

The portfolio overview document must be updated to reflect the new apps. This is a documentation change, not a code change, but it is governed by the same constitutional rules (no silent omission of apps from the registry).

### Required Updates to `apps/APPS_PORTFOLIO_OVERVIEW.md`

1. **App Summary section:** Add four new `###` subsections (one per app)
2. **Reviewer Persona Map table:** Add rows for new reviewer personas
3. **Enterprise AI Platform Value Map table:** Add rows for new value dimensions:
   - `apps_coaching` → Career journey orchestration
   - `apps_intel` → Competitive intelligence & market grounding
   - `apps_comply` → Regulatory compliance automation
   - `apps_onboard` → Workforce & system onboarding automation
4. **Directory Structure:** Add four new columns to the structure table
5. **Quick Reference CLI:** Add four new CLI invocation examples

---

## Refactor: Non-Breaking Additions to Existing `apps_shared` Files

These are **additive-only** changes — no existing public API is removed or altered.

### R1: `apps_shared/utils/tone_voice_util.py` — Add `COACHING` tone profile
**Change:** Add `ToneProfile.COACHING` enum value and associated defaults dict entry.
**Risk:** Zero — additive-only enum extension
**Consumer:** `apps_coaching/engines/coaching_plan_engine.py`

### R2: `apps_shared/config/routing_tier_config.py` — Add `COMPLIANCE` routing tier
**Change:** Add `RoutingTier.COMPLIANCE = "compliance_tier"` and a `RouteConfig` entry with `reasoning` tier routing (compliance tasks need high-quality models).
**Risk:** Zero — additive-only dict entry
**Consumer:** `apps_comply/engines/control_mapping_engine.py`

### R3: `apps_shared/types/sovereign_severity_types.py` — Add compliance severity aliases
**Change:** Add `REGULATORY_CRITICAL`, `REGULATORY_HIGH` as aliases mapping to existing `SovereignSeverity` values. **Do not rename or remove existing symbols** — fan-out is 1,146 and any rename would break the entire graph.
**Risk:** Low — aliases only, no rename
**Consumer:** `apps_comply/types/comply_types.py`

### R4: `apps_shared/config/app_guardian_registry.py` — AGS entries (see Gap 8 above)
**Change:** Extend `App` literal, append 9 new `AppGuardianSpec` entries.
**Risk:** Zero — append-only to an immutable tuple

---

## New `apps_shared` Files Summary

| File | Size Estimate | Phase | Consumers |
|---|---|---|---|
| `config/compliance_framework_config.py` | ~150 lines | Phase 1 | apps_comply |
| `types/onboarding_domain_types.py` | ~80 lines | Phase 1 | apps_onboard |
| `types/coaching_domain_types.py` | ~80 lines | Phase 1 | apps_coaching |
| `types/intelligence_domain_types.py` | ~80 lines | Phase 1 | apps_intel |
| `utils/artifact_emitter_util.py` | ~120 lines | Phase 1 | all 4 new apps |
| `utils/human_escalation_util.py` | ~80 lines | Phase 2 | apps_comply |
| `utils/app_run_registry_util.py` | ~100 lines | Phase 3 | all 4 new apps |

**Total new lines:** ~690 lines across 7 new files
**Total modifications:** 4 non-breaking additions to existing files

---

## Delivery Phases (Aligned with Four-App Plan)

### Phase 1 — Domain Types & Framework Config (parallel with four-app Phase 1)

**Deliverables:**
- `apps_shared/config/compliance_framework_config.py`
- `apps_shared/types/onboarding_domain_types.py`
- `apps_shared/types/coaching_domain_types.py`
- `apps_shared/types/intelligence_domain_types.py`
- `apps_shared/utils/artifact_emitter_util.py`

**Acceptance criteria:**
1. All 5 files import cleanly: `python -c "from apps_shared.config.compliance_framework_config import get_controls"`
2. `ruff check apps_shared/` = 0 new violations
3. Existing `apps_shared` imports unaffected (regression: `python -m pytest tests/ -k apps_shared --no-header -q` passes)
4. ADG re-scan: 5 new L_SHARED nodes, 0 new violations

### Phase 2 — Escalation Bus & Guardian Registry (parallel with four-app Phase 3)

**Deliverables:**
- `apps_shared/utils/human_escalation_util.py`
- `apps_shared/config/app_guardian_registry.py` — AGS-010 to AGS-018 entries added

**Acceptance criteria:**
1. `HumanEscalationBus.has_blocking_flags()` returns correct value for blocking and non-blocking flag sets
2. `get_specs_for_app("apps_comply")` returns ≥3 specs
3. `get_specs_for_app("apps_coaching")` returns ≥2 specs (including AGS-001 global)

### Phase 3 — App Run Registry (parallel with four-app Phase 5)

**Deliverables:**
- `apps_shared/utils/app_run_registry_util.py`

**Acceptance criteria:**
1. Registry records 3 sequential app runs correctly
2. `to_dict()` is JSON-serializable (no non-serializable types)
3. `emit_session_summary()` writes file only in non-dry-run mode

### Phase 4 — Refactors (parallel with four-app Phase 5, documentation phase)

**Deliverables:**
- `apps_shared/utils/tone_voice_util.py` — `COACHING` tone profile added
- `apps_shared/config/routing_tier_config.py` — `COMPLIANCE` tier added
- `apps_shared/types/sovereign_severity_types.py` — regulatory aliases added

**Acceptance criteria:**
1. `from apps_shared.utils.tone_voice_util import ToneProfile; ToneProfile.COACHING` — no `AttributeError`
2. `from apps_shared.config.routing_tier_config import RoutingTier; RoutingTier.COMPLIANCE` — no `AttributeError`
3. All existing tests that touch these files pass unchanged (no regressions)

---

## Test Plan for New `apps_shared` Files

All tests live in `tests/apps_shared/` (new subdirectory). Tests must be deterministic — no LLM calls, no network calls.

| Test File | What It Tests |
|---|---|
| `test_compliance_framework_config.py` | `get_controls(GDPR)` returns non-empty tuple; `get_critical_controls(SOC2)` returns only MANDATORY controls |
| `test_onboarding_domain_types.py` | `WorkContractStamp` is frozen (immutable); `StakeholderEntry` relationship field validates |
| `test_coaching_domain_types.py` | `STARAnswer` has all four fields; `SkillGap` severity ordering works |
| `test_intelligence_domain_types.py` | `EpistemicType` enum has 4 members; `GroundednessScore.score` in [0,1] |
| `test_artifact_emitter_util.py` | `emit()` writes files in non-dry-run; returns empty list in dry-run; `run_summary_*.json` is valid JSON |
| `test_human_escalation_util.py` | `raise_flag(BLOCKING)` → `has_blocking_flags()=True`; `raise_flag(ADVISORY)` alone → `has_blocking_flags()=False` |
| `test_app_run_registry_util.py` | Three records recorded correctly; `any_failed` true when one record status=FAILED |

---

## ADG Impact Projection

After all phases complete, the projected ADG snapshot changes are:

| Metric | Current | Projected | Delta |
|---|---|---|---|
| `module_count` | 8,059 | ~8,300 | +241 |
| `L_APP` modules | 1,184 (snapshot) | ~1,500 | +316 |
| `L_SHARED` modules | 365 (snapshot) | ~390 | +25 |
| `layer_violation_count` | 0 | 0 | **0** |
| `dead_imports` edges | 4,466 | ≤4,466 | ≤0 (new apps born clean) |
| `applies_guardrail` edges | 68 | ~80 | +12 (apps_comply) |
| `escalates_to_human` edges | 12 | ~20 | +8 (apps_comply) |
| `stamps_work_contract` edges | 13 | ~18 | +5 (apps_onboard) |
| `scores_groundedness` edges | 40 | ~50 | +10 (apps_intel) |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `sovereign_severity_types.py` fan-out exceeds 1,200 | MEDIUM | LOW | New types added to separate domain-specific files, not to `sovereign_severity_types.py` |
| `artifact_emitter_util.py` non-deterministic file paths | MEDIUM | HIGH | `_resolve_path` must only use `trace_id` as variable; wall clock not used in filename |
| Compliance framework catalog becomes stale | LOW | MEDIUM | `FrameworkControl` objects are frozen; update cycle must be explicit (version tag in config) |
| Cross-app L_APP imports (e.g., `apps_coaching` importing `apps_rg`) | LOW | HIGH | ADG re-scan after Phase 2 catches this; `layer-boundary-guard` skill enforced |
| `human_escalation_util.py` swallowed silently in `ControlPlane` pattern | MEDIUM | HIGH | `has_blocking_flags()` check in orchestrator is a hard gate, not a warning |

---

## Dependency Order (Build Sequence)

```
Phase 1 (apps_shared) ──┐
                         ├──► Phase 1 (all 4 new apps stubs)
                         │
Phase 2 (apps_shared) ──┐
                         ├──► Phase 3 (orchestrators & spine adapters)
                         │
Phase 3 (apps_shared) ──► Phase 5 (documentation + portfolio update)
                         │
Phase 4 (apps_shared refactors) ──► Phase 6 (ADG re-scan)
```

**Critical path:** `compliance_framework_config.py` (Phase 1) → `control_mapping_engine.py` (Phase 2) → `ComplyOrchestrator.py` (Phase 3) → `ComplyGateValidator` (Phase 4). This is the longest chain and should be started first.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

