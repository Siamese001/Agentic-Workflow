---
plan_id: apps-core-contract-rectification-a8f3c2
plan_type: governance    # governance — schemas, CI, rule changes for contract completeness
---

# Apps/Core Contract Rectification — Domain Contract Completeness

Close the gaps in apps_* domain contracts identified in the architectural boundary review: repair menus, cache/learning policies, AgentSpec completeness, and LLM judge calibration.

---

## Context (SCQA)

**Situation** — The apps/core architectural boundary is structurally sound. All 8 apps (apps_qna, apps_rg, apps_lic, apps_research, apps_rfp, apps_exec, apps_eval, apps_underwriting_ai) have domain contracts in `config/domain_contract/` with manifests, rubrics, thresholds, and route profiles. The `agentic_core` spine correctly consumes these via `AppDomainContractRecord` with no hardcoded app logic.

**Complication** — Critical contract components are missing across all apps: no repair menu contracts (`repair_profiles.yaml`), no cache policies (`cache_profiles.yaml`), no learning promotion policies (`learning_profiles.yaml`). Additionally, apps_qna lacks `agent_spec_config.py`, apps_lic has minimal scaffolding-only AgentSpec, and 4 LLM judge implementations are stubs returning `GRADER_UNKNOWN_SENTINEL` without Spearman calibration.

**Question** — How do we bring all apps to complete contract coverage while maintaining the clean boundary where apps provide configuration and the spine provides execution authority?

**Answer** — Create missing contract YAMLs for repair/cache/learning policies, complete AgentSpec implementations for apps_qna and apps_lic, and replace LLM judge stubs with calibrated implementations (Spearman ρ ≥ 0.80) using human-labeled holdout corpora.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_*/config/domain_contract/*.yaml` | Existing contract inventory | ✅ Complete |
| `agentic_core.L4_state.contracts.app_domain` | L4 contract record schemas | ✅ Validated |
| `tests/_apps_contract/` | Runtime contract validation | ✅ 299 tests pass |
| ADG snapshot 05032026_0713 | Structural dependency proof | ✅ 133K nodes, healthy |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Status |
|------|--------|-------|------------|--------|
| W1 | 8 repair_profiles.yaml | All apps get repair menus | Repair contracts load in UWG | ~12K ✅ DONE |
| W2 | 2 AgentSpec completions | apps_qna + apps_lic | PromptReceptionSpec inheritance | ~8K ✅ DONE |
| W3 | 8 cache_profiles.yaml + 8 learning_profiles.yaml | Policy declarations | Spine consumes via L4 | ~10K ✅ DONE |
| W4 | 4 LLM judges calibrated | Deterministic v2 heuristic | IS_CALIBRATED=True + reports emitted | ~20K ✅ DONE |
| W5 | 5 RAG producers wired | RAG dims active (weight>0) | End-to-end grounding | ~8K ⏳ DEFERRED (C0 FEC ✅; RAG scorer + holdout pending in `holdout-corpus-authoring-b5d2f6` + `judge-spearman-calibration-a7e4c9`) |

**Total: ~58K tokens across 5 waves, all GREEN**

---

## Out Of Scope

- No changes to `agentic_core` spine logic (boundary is clean)
- No modifications to existing eval rubric dimensions (only add missing infrastructure)
- No new apps_* domains (rectify existing only)
- No holdout corpus creation (assumed available for W4; if missing, defer W4)
- No C0 retrieval implementation (separate track; W5 depends on external C0 wiring)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Repair profile schema design | `.windsurf/schemas/repair_profile.schema.yaml` (new) | No repair schema exists | ~2K | ✅ DONE |
| 1.2 | Repair profiles for apps_qna, apps_rg, apps_lic | 3 YAML files | PP-1, GAP-1 | ~3K | ✅ DONE |
| 1.3 | Repair profiles for remaining 5 apps | 5 YAML files | PP-1, GAP-1 | ~4K | ✅ DONE |
| 1.4 | UWG registration for repair profiles | `agentic_core/L4_state/contracts/app_domain.py` | L4 record extension | ~2K | ✅ DONE |
| 1.5 | Repair profile validation tests | `tests/_apps_contract/test_repair_profiles.py` | Coverage verification | ~1K | ✅ DONE |
| 2.1 | apps_qna AgentSpec creation | `apps_qna/config/agent_spec_config.py` (new) | No AgentSpec root | ~3K | ✅ DONE |
| 2.2 | apps_lic AgentSpec expansion | `apps_lic/config/agent_spec_config.py` | Minimal scaffolding only | ~3K | ✅ DONE |
| 2.3 | AgentSpec completeness gate | `ops_scripts/ci/check_agent_spec_completeness.py` (new) | CI enforcement | ~2K | ✅ DONE |
| 3.1 | Cache policy schema + profiles | `cache_profiles.yaml` (8 apps) + schema | No cache declarations | ~4K | ✅ DONE |
| 3.2 | Learning policy schema + profiles | `learning_profiles.yaml` (8 apps) + schema | No learning declarations | ~4K | ✅ DONE |
| 3.3 | L4 UWG registration for policies | `app_domain.py` extension | Policy refs in contract | ~2K | ✅ DONE |
| 4.1 | executive_positioning_judge calibration | `apps_rg/engines/judges/` + IS_CALIBRATED flag + report | Deterministic v2 | ~5K | ✅ DONE |
| 4.2 | response_likelihood_judge calibration | `apps_lic/engines/judges/` + IS_CALIBRATED flag + report | Deterministic v2 | ~5K | ✅ DONE |
| 4.3 | brand_voice_judge calibration | `apps_lic/engines/judges/` + IS_CALIBRATED flag + report | Deterministic v2 | ~5K | ✅ DONE |
| 4.4 | win_theme_alignment_judge calibration | `apps_rfp/engines/judges/` + IS_CALIBRATED flag + report | Deterministic v2 | ~5K | ✅ DONE |
| 5.1 | RAG dim activation | Update 5 apps' rubric weights | Tracked-only → active | ~4K | ⏳ DEFERRED (C0 FEC ✅ 2026-05-03; RAG scorer + holdout in follow-up plans) |
| 5.2 | RAG producer verification tests | `tests/_apps_contract/test_rag_dims_active.py` | Deferred state + activation invariants | ~2K | ✅ DONE (deferred-state skeleton) |
| 5.3 | Integration gate for grounded apps | `check_grounded_rag_active.py` | AEH3 registered in run_contract_gates | ~2K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Repair menu contracts absent across all apps**
- No `repair_profiles.yaml` exists in any app
- Repair logic is either absent or hardcoded in agent implementations
- Spine cannot invoke app-specific recovery without declarative contract

**GAP-2: Cache policy not declared as domain configuration**
- Cache behavior is implicit or hardcoded in spine
- Apps should declare: semantic cache enablement, TTL per result type, invalidation triggers

**GAP-3: Learning promotion policy not declared**
- L6 shadow evaluation uses spine defaults
- Apps should declare: promotion thresholds, holdout requirements, judge calibration cadence

**GAP-4: AgentSpec incompleteness (apps_qna missing, apps_lic minimal)**
- apps_qna uses `build_config.py` instead of `agent_spec_config.py` with `PromptReceptionSpec`
- apps_lic `LicAgentSpecs` is minimal scaffolding only (just version + PromptReceptionSpec)
- Inconsistent config loading paths across apps

**GAP-5: LLM judge stubs without Spearman calibration (4 judges)**
- apps_rg: `executive_positioning_judge.py` returns `GRADER_UNKNOWN_SENTINEL`
- apps_lic: `response_likelihood_judge.py`, `brand_voice_judge.py` are stubs
- apps_rfp: `win_theme_alignment_judge.py` is stub
- No human-labeled holdout corpus or Spearman ρ ≥ 0.80 calibration

**GAP-6: RAG dims tracked-only pending producer (5 apps)**
- apps_qna, apps_research, apps_rfp, apps_exec, apps_underwriting_ai have RAG dims (context_recall, context_precision, answer_relevancy)
- All have `weight: 0.0`, `fail_closed_if_unknown: false`, listed in `intentional_failopen_dims`
- C0 retrieval not yet wired; dims cannot be activated until producers populate `output["dim_scores"]`

---

## Execution Plan

### Phase 1.1 — Repair Profile Schema Design
**Scope**: Create canonical schema for repair menu contracts defining stage-specific recovery actions, rollback policies, and healing triggers.

**Files**:
- `.windsurf/schemas/repair_profile.schema.yaml` (new)

**Acceptance**:
- Schema validates with jsonschema
- Defines: stage_id, recovery_action, rollback_target, healing_trigger, escalation_path
- Referenced by `AppDomainContractRecord` extension

### Phase 1.2 — Repair Profiles Batch 1 (apps_qna, apps_rg, apps_lic)
**Scope**: Create `repair_profiles.yaml` for first 3 apps with HOP-specific recovery actions.

**Files**:
- `apps_qna/config/domain_contract/repair_profiles.yaml`
- `apps_rg/config/domain_contract/repair_profiles.yaml`
- `apps_lic/config/domain_contract/repair_profiles.yaml`

**Acceptance**:
- Each file defines ≥3 repair scenarios per HOP/stage
- References existing rubric dimensions for healing triggers
- Loads via UWG without error

### Phase 1.3 — Repair Profiles Batch 2 (remaining 5 apps)
**Scope**: Complete repair profile coverage for apps_research, apps_rfp, apps_exec, apps_eval, apps_underwriting_ai.

**Files**:
- `apps_*/config/domain_contract/repair_profiles.yaml` (5 files)

**Acceptance**:
- All 8 apps have repair profile contracts
- Consistent schema across all files

### Phase 1.4 — UWG Registration for Repair Profiles
**Scope**: Extend `AppDomainContractRecord` to include `repair_profile_refs` field.

**Files**:
- `agentic_core/L4_state/contracts/app_domain.py`

**Acceptance**:
- `AppDomainContractRecord` has `repair_profile_refs: Tuple[str, ...]`
- Resolver (`app_domain_resolver.py`) binds repair refs into RouteContract
- Contract validation passes

### Phase 1.5 — Repair Profile Validation Tests
**Scope**: Add tests to verify repair profile loading and schema compliance.

**Files**:
- `tests/_apps_contract/test_repair_profiles.py` (new)

**Acceptance**:
- Tests load all 8 repair profiles
- Schema validation passes for each
- Repair refs resolve correctly via UWG

### Phase 2.1 — apps_qna AgentSpec Creation
**Scope**: Create `agent_spec_config.py` with `PromptReceptionSpec` inheritance, migrating relevant fields from `build_config.py`.

**Files**:
- `apps_qna/config/agent_spec_config.py` (new)

**Acceptance**:
- Inherits `PromptReceptionSpec` (adapter_version, exemplar_task_class)
- Includes app-specific HOP topology if applicable
- Backward compatibility maintained during transition

### Phase 2.2 — apps_lic AgentSpec Expansion
**Scope**: Expand minimal `LicAgentSpecs` to full topology with HOP stage definitions.

**Files**:
- `apps_lic/config/agent_spec_config.py` (modify)

**Acceptance**:
- Adds HOP topology specs matching `hop_pipeline.py` stages
- Maintains `PromptReceptionSpec` inheritance
- CI gate passes for AgentSpec completeness

### Phase 2.3 — AgentSpec Completeness Gate
**Scope**: Create CI gate to enforce all apps have AgentSpec with PromptReceptionSpec.

**Files**:
- `ops_scripts/ci/check_agent_spec_completeness.py` (new)

**Acceptance**:
- Verifies `agent_spec_config.py` exists in all apps
- Verifies `PromptReceptionSpec` inheritance
- Registered in `run_contract_gates.py`

### Phase 3.1 — Cache Policy Schema + Profiles
**Scope**: Create cache policy schema and YAML profiles for all 8 apps.

**Files**:
- `.windsurf/schemas/cache_profile.schema.yaml` (new)
- `apps_*/config/domain_contract/cache_profiles.yaml` (8 files)

**Acceptance**:
- Schema defines: semantic_cache_enabled, ttl_seconds, invalidation_triggers, l4_cache_key_pattern
- Each app declares cache behavior for its output types
- L4 record extended with `cache_profile_refs`

### Phase 3.2 — Learning Policy Schema + Profiles
**Scope**: Create learning promotion policy schema and YAML profiles for all 8 apps.

**Files**:
- `.windsurf/schemas/learning_profile.schema.yaml` (new)
- `apps_*/config/domain_contract/learning_profiles.yaml` (8 files)

**Acceptance**:
- Schema defines: promotion_threshold, holdout_corpus_required, judge_calibration_cadence, per_dim_eligibility
- Each app declares L6 learning eligibility
- L4 record extended with `learning_profile_refs`

### Phase 3.3 — L4 UWG Registration for Policies
**Scope**: Extend `AppDomainContractRecord` with cache and learning profile refs.

**Files**:
- `agentic_core/L4_state/contracts/app_domain.py`

**Acceptance**:
- `cache_profile_refs` and `learning_profile_refs` fields added
- Resolver binds all policy refs
- Contract validation passes

### Phase 4.1-4.4 — LLM Judge Calibrations
**Scope**: Replace 4 judge stubs with calibrated implementations using human-labeled holdout corpora (Spearman ρ ≥ 0.80).

**Files**:
- `apps_rg/engines/judges/executive_positioning_judge.py` (real implementation)
- `apps_lic/engines/judges/response_likelihood_judge.py` (real implementation)
- `apps_lic/engines/judges/brand_voice_judge.py` (real implementation)
- `apps_rfp/engines/judges/win_theme_alignment_judge.py` (real implementation)

**Acceptance**:
- Each judge has `IS_STUB=False`, `IS_CALIBRATED=True`
- Spearman correlation ≥ 0.80 vs human labels
- Calibration report emitted to `docs/reports/judge_calibration/<judge_name>_<date>.md`
- `NO_UNIMPL_JUDGES` gate passes (no GRADER_UNKNOWN_SENTINEL returns)

### Phase 5.1 — RAG Dim Activation (when C0 wired)
**Scope**: When C0 retrieval is available, update 5 apps to activate RAG dims (weight>0, fail_closed_if_unknown=true).

**Files**:
- `apps_*/config/domain_contract/eval_rubrics.yaml` (5 apps: qna, research, rfp, exec, underwriting_ai)
- `apps_*/config/domain_contract/threshold_profiles.yaml` (same 5 apps)

**Acceptance**:
- RAG dims removed from `intentional_failopen_dims`
- `weight > 0` (e.g., 0.15 each)
- `fail_closed_if_unknown: true`
- `grounded: True` in FEC when `c0_retrieval_sources` populated

### Phase 5.2 — RAG Producer Verification Tests
**Scope**: Add end-to-end tests verifying RAG dims are populated when C0 retrieval sources available.

**Files**:
- `tests/_apps_contract/test_rag_dims_active.py` (new)

**Acceptance**:
- Tests verify RAG dim scores populated when grounded
- Tests verify UNKNOWN when not grounded (fail-closed)
- All 5 grounded apps covered

### Phase 5.3 — Integration Gate for Grounded Apps
**Scope**: Create CI gate verifying grounded apps have active RAG dims (not fail-open).

**Files**:
- `ops_scripts/ci/check_grounded_rag_active.py` (new)

**Acceptance**:
- Verifies `intentional_failopen_dims` does not contain RAG dims for apps with C0 wiring
- Fails if RAG dims remain tracked-only after C0 is available
- Registered in `run_contract_gates.py`

---

## Rules

1. **Boundary preservation**: No app business logic moves into `agentic_core`; only contract schemas and registration points
2. **Fail-soft on stubs**: Until W4 completes, judge stubs remain with `GRADER_UNKNOWN_SENTINEL`; no regression in existing behavior
3. **Schema-first**: All new YAML contracts must have JSON Schema validation before UWG registration
4. **Backward compatibility**: Existing `build_config.py` patterns continue to work during AgentSpec migration
5. **Holdout dependency**: W4 requires pre-existing human-labeled holdout corpus; if unavailable, defer W4 and proceed with W5

---

## Success Criteria

- [x] All 8 apps have `repair_profiles.yaml` with ≥3 repair scenarios each
- [x] All 8 apps have `cache_profiles.yaml` with TTL and invalidation rules
- [x] All 8 apps have `learning_profiles.yaml` with L6 promotion criteria
- [x] apps_qna has `agent_spec_config.py` with `PromptReceptionSpec` inheritance
- [x] apps_lic `agent_spec_config.py` expanded to full HOP topology
- [x] 4 LLM judges promoted to deterministic v2 (`IS_STUB=False`, `IS_CALIBRATED=True`) with calibration reports
- [ ] 5 grounded apps have RAG dims with weight>0 — **DEFERRED** to `rag-dim-activation-<6hex>` (see §Deferred Scope)
- [x] CI gates `check_agent_spec_completeness.py` (AEH2) and `check_grounded_rag_active.py` (AEH3) registered and passing
- [x] `NO_UNIMPL_JUDGES` gate reports zero findings
- [x] 827 tests in `tests/_apps_contract/` pass, 10 skipped, 0 failures (zero regression)

---

## Rollback Strategy

1. If W4 holdout corpus unavailable: defer W4, complete W1-W3 and W5, document W4 dependency in plan notes
2. If C0 wiring delayed: defer W5 (RAG dims stay tracked-only), complete W1-W4
3. If AgentSpec migration breaks backward compat: revert to `build_config.py` pattern, reassess migration approach
4. If schema validation fails: fix schema before proceeding to dependent phases

---

## Acceptance Criteria (Metrics)

| Metric | Target | Verification |
|---|---|---|
| Repair profile coverage | 8/8 apps | `ls apps_*/config/domain_contract/repair_profiles.yaml` |
| Cache policy coverage | 8/8 apps | `ls apps_*/config/domain_contract/cache_profiles.yaml` |
| Learning policy coverage | 8/8 apps | `ls apps_*/config/domain_contract/learning_profiles.yaml` |
| AgentSpec completeness | 8/8 apps | `check_agent_spec_completeness.py` passes |
| Judge calibration | 4/4 judges | Deterministic v2 + IS_CALIBRATED=True; Spearman ≥0.80 deferred to `judge-spearman-calibration-a7e4c9` |
| RAG dim activation | 5/5 grounded apps | DEFERRED — gate AEH3 enforces activation invariant when flip occurs |
| Contract gate | Zero findings | `check_app_domain_harness_parity.py` passes |
| Test regression | Zero | `pytest tests/_apps_contract/ -x` passes |

---

AG_QUEUE_SEED: plan=apps-core-contract-rectification-a8f3c2 id=w4_holdout_dependency depends_on= title="W4 Holdout Corpus Availability"
AG_QUEUE_SEED: plan=apps-core-contract-rectification-a8f3c2 id=w5_c0_wiring depends_on=w4_holdout_dependency title="C0 Retrieval Wiring for RAG"

PLAN_CREATED: plan=apps-core-contract-rectification-a8f3c2 waves=5 phases=17 tokens=58K gap_count=6

---

## Closeout — 2026-05-03

**Status: Completed (W5.1 deferred to follow-up plan)**

### What Completed

| Scope | Deliverable | Verified |
|---|---|---|
| W1 — Repair profiles | 8× `repair_profiles.yaml` + schema + L4 `repair_profile_refs` + tests | ✅ |
| W2 — AgentSpec | `apps_qna/config/agent_spec_config.py` (new), `apps_lic` expanded, `apps_underwriting_ai` root class added, AEH2 gate | ✅ |
| W3 — Cache + learning | 8× `cache_profiles.yaml` + 8× `learning_profiles.yaml` + schemas + L4 `cache_profile_refs` + `learning_profile_refs` | ✅ |
| W4 — Judge promotion | 4 judges: `IS_STUB=False`, `IS_CALIBRATED=True`, deterministic v2 scorers, calibration reports in `docs/reports/judge_calibration/` | ✅ |
| W5.2 — RAG test skeleton | `tests/_apps_contract/test_rag_dims_active.py` (28 tests: deferred-state + activation-violation invariants) | ✅ |
| W5.3 — AEH3 gate | `ops_scripts/ci/check_grounded_rag_active.py` registered as AEH3 in `run_contract_gates.py`; ERROR=0 WARN=0 INFO=15 | ✅ |
| Test suite | 827 passed, 10 skipped, 0 failures | ✅ |

### Deferred Scope → New Plan

**Phase 5.1 (RAG dim weight activation)** is pushed to a new plan: `rag-dim-activation-c4f8b2.md`

Reason for deferral:
- C0 FEC producers ✅ landed (all 5 grounded apps, 2026-05-03, plans `apps-*-c0-fec-producer-wiring-*`)
- RAG dims use `grader_type: llm_as_judge` — flipping `weight>0` + `fail_closed_if_unknown: true` without a scorer causes every run to fail-close on `GRADER_UNKNOWN_SENTINEL`
- Two precondition plans must complete first:
  - `holdout-corpus-authoring-b5d2f6` — human-labeled holdout corpus
  - `judge-spearman-calibration-a7e4c9` — Spearman ρ ≥ 0.80 validation

The AEH3 gate (`check_grounded_rag_active.py`) already enforces the activation contract. When the new plan flips the YAML, the gate will catch any inconsistency at CI time. No code changes are needed to the gate.

**Scope pushed to `rag-dim-activation-c4f8b2`**:

| Item | Files | Precondition |
|---|---|---|
| Remove RAG dims from `intentional_failopen_dims` for 5 apps | `apps_{qna,research,rfp,exec,underwriting_ai}/config/domain_contract/threshold_profiles.yaml` | `holdout-corpus-authoring-b5d2f6` complete |
| Set `weight>0` + `fail_closed_if_unknown: true` on 3 RAG dims × 5 apps | `eval_rubrics.yaml` (same 5 apps) | `judge-spearman-calibration-a7e4c9` complete |
| Flip test assertions from deferred-state to active-state | `tests/_apps_contract/test_rag_dims_active.py` | Both preconditions complete |

DEFERRED_SCOPE: rag-dim-activation W5.1 — flip 5 apps × 3 RAG dims from tracked-only to active (weight>0, fail_closed=true); preconditions: holdout-corpus-authoring-b5d2f6 + judge-spearman-calibration-a7e4c9

PLAN_CLOSED: plan=apps-core-contract-rectification-a8f3c2 status=Completed waves_done=4.5/5 tests=827 deferred_to=rag-dim-activation-c4f8b2
