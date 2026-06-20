---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-spine-deferred-followup-d4e7b2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-spine-deferred-followup-d4e7b2.md'
source_sha256: 0f5be32e3dee75e65a155ed220b5696dd657ed9b4a2bf00c12a2fe828cd60bd3
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-spine-deferred-followup-d4e7b2
plan_type: refactor
---

# apps_rg Agentic Spine — Deferred Scope Follow-Up

Implements the 4 deferred waves (W2, W4, W6, W7) from the parent plan that require deeper code changes: R1A/R1B cache strengthening, prompt assembly module, L4/UWG/FEC wiring, and E1-E5 span instrumentation.

---

## Context (SCQA)

- **Situation** — Parent plan `apps_rg_agentic_spine_refactor_plan` completed 2026-05-04 with W1 (docs/terminology), W3 (research boundary), W5 (exit dispositions + sealed packets), and W8 (22 governance tests). apps_rg now has correct terminology, no live research at runtime, canonical X3 dispositions, and sealed violation packets. 22 governance tests green.
- **Complication** — Four implementation waves were deferred because they require deeper code changes with higher risk: (1) R1A exact cache + R1B key strengthening, (2) prompt assembly module with prompt_bom capture, (3) L4/UWG optional cache commit wiring + FEC field enrichment, (4) E1-E5 span instrumentation + E5 sealing with hashes and replay metadata. These gaps mean apps_rg still lacks exact-match cache dedup, auditable prompt provenance, optional cache commit via the canonical UWG path, and structured L2 phase telemetry.
- **Question** — How do we implement the remaining 4 deferred waves to complete apps_rg's canonical spine alignment?
- **Answer** — 4 waves, 10 phases, ~80K tokens. Each wave is independently testable. W1 (cache) and W2 (prompt assembly) are independent; W3 (L4/UWG/FEC) depends on W1 (cache commit needs R1A key); W4 (spans) depends on W2 (prompt_bom) and parent W5 (sealed packets).

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| Parent plan `.windsurf/plans/apps_rg_agentic_spine_refactor_plan.md` | Deferred wave specs, open questions Q1-Q6 | ✅ |
| `apps_rg/cache/r1b_adapter.py` | Current R1B cache implementation, gap analysis for R1A | 🔲 |
| `apps_rg/types/intent_payload.py` | Current cache key fields, gap for 14-field key | 🔲 |
| `apps_rg/reasoning/RgResumeOrchestrator.py` | HOP 3 LLM calls needing prompt_bom wrap | 🔲 |
| `apps_rg/integrations/hops/*.py` | Narrative HOPs needing prompt_bom wrap | 🔲 |
| `apps_rg/cert/fec_producer.py` | Current FEC fields, gap for enrichment | 🔲 |
| `apps_rg/__main__.py` | Main entry point for E1-E5 span wiring, UWG commit | 🔲 |
| `apps_shared/spine_emission/` | governed_run X3 computation, UWG commit path | 🔲 |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|--------|
| W1 | R1A exact cache + R1B 14-field key | `cache/r1b_adapter.py`, `types/intent_payload.py`, `__main__.py` | A: R1A dedup + R1B key validation tests green | ~25K 🟢 |
| W2 | Prompt assembly + prompt_bom capture | NEW `prompt_assembly/pa_local.py`, `reasoning/RgResumeOrchestrator.py`, `integrations/hops/*.py` | B: prompt_bom artifact present in run_dir | ~25K 🟢 |
| W3 | L4/UWG optional cache commit + FEC enrichment | `__main__.py`, `cert/fec_producer.py`, config | C: cache commit gated by Exit X3C, FEC has new fields | ~15K 🟢 |
| W4 | E1-E5 span instrumentation + E5 seal | `__main__.py` | D: OTEL spans named L2.E1–E5, sealed artifact has hashes + replay_key | ~15K 🟢 |

**Total: ~80K tokens across 4 waves, all GREEN**

---

## Out Of Scope

- No changes to `AGENTIC_SPINE.md` (already updated in parent plan W1.P1)
- No changes to `spine_manifest.yaml` (already updated in parent plan W1.P2)
- No changes to research boundary code (already removed in parent plan W3)
- No changes to `company_research_loader.py` (finalized in parent W3.P1)
- No introduction of C0 retrieval, L3 orchestration, or runtime HITL
- No ATS submission, LinkedIn writes, or direct L4 writes
- No changes to HOP logic/behavior — only wrapping for prompt_bom capture
- No changes to other apps (apps_lic, apps_research, apps_exec, etc.)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | R1A exact cache function | `cache/r1b_adapter.py` (or new `r1a_adapter.py`), `__main__.py` | Parent Q5: need to inspect existing R1B check wiring | ~10K | 🔲 TODO |
| 1.2 | R1B cache key strengthening to 14 fields | `types/intent_payload.py`, `utils/intent_builder.py`, `cache/r1b_adapter.py` | Parent Q1: need to audit current `to_cache_key_dict()` fields | ~10K | 🔲 TODO |
| 1.3 | R1A/R1B tests | `tests/governance/test_apps_rg_spine_refactor.py` or new test file | — | ~5K | 🔲 TODO |
| 2.1 | Create `prompt_assembly/pa_local.py` module | NEW `apps_rg/prompt_assembly/pa_local.py` | High: new module, must emit prompt_bom without disrupting domain logic | ~8K | 🔲 TODO |
| 2.2 | Wrap HOP 3 LLM calls with prompt_bom | `reasoning/RgResumeOrchestrator.py` | Parent Q6: need to identify which HOPs call LLM vs deterministic | ~8K | 🔲 TODO |
| 2.3 | Wrap narrative HOPs with prompt_bom | `integrations/hops/*.py` | Parent Q6: same audit | ~5K | 🔲 TODO |
| 2.4 | Prompt assembly tests | test files | — | ~4K | 🔲 TODO |
| 3.1 | Wire optional cache commit via Exit → UWG | `__main__.py`, config | Parent Q2/Q3/Q4: need to audit `apps_shared.spine_emission.governed_run` | ~8K | 🔲 TODO |
| 3.2 | FEC field enrichment | `cert/fec_producer.py` | Low: add fields to existing producer | ~5K | 🔲 TODO |
| 3.3 | L4/UWG/FEC tests | test files | — | ~2K | 🔲 TODO |
| 4.1 | E1-E5 OTEL span instrumentation | `__main__.py` | Medium: wrap existing code in span blocks | ~8K | 🔲 TODO |
| 4.2 | E5 seal: hash computation + replay metadata | `__main__.py` | Medium: add SHA256 of key artifacts | ~5K | 🔲 TODO |
| 4.3 | E1-E5 span + seal tests | test files | — | ~2K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: R1A exact cache key composition unknown**
- Parent plan Q5: need to inspect `_check_r1b_cache()` in `__main__.py` to determine if existing R1B wiring partially supports R1A-style exact matching.
- Impact: determines whether R1A is a new function or a mode flag on the existing adapter.

**GAP-2: R1B cache key field inventory incomplete**
- Parent plan Q1: need to inspect `ResumeGenerationIntent.to_cache_key_dict()` in `types/intent_payload.py` to count which of the 14 required fields are already present.
- Impact: determines the scope of key-strengthening edits.

**GAP-3: Which HOPs call LLM providers**
- Parent plan Q6: narrative HOPs (4A–4H) may include deterministic steps that don't need prompt_bom capture. Need to audit `apps_rg/integrations/hops/*.py` to identify LLM-calling vs deterministic HOPs.
- Impact: determines how many HOP files need wrapping.

**GAP-4: `governed_run` X3 computation internals**
- Parent plan Q2/Q4: need to audit `apps_shared.spine_emission.governed_run` to understand how X3 is computed and whether `EXIT_PARTIAL` exists in shared code (affecting other apps).
- Impact: determines whether cache commit wiring is apps_rg-local or requires shared-code changes.

**GAP-5: `cache_commit_enabled` config wiring**
- Parent plan Q3: need to check if `cert_route_registry.yaml` already has a cache-commit flag or if a new field is needed.
- Impact: determines config-level changes for W3.

---

## Execution Plan

### Wave 1 — R1A Exact Cache + R1B Key Strengthening

#### Phase 1.1 — R1A Exact Cache Function
**Scope**: Add `_check_r1a_cache(args) -> Optional[Path]` to `cache/r1b_adapter.py` (or new `r1a_adapter.py`). R1A computes SHA256 over `(jd_text + master_resume_hash + company_brief_hash + policy_hash + blueprint_hash + schema_hash + cache_schema_version)`. If an exact match exists in the run artifacts directory, return the cached artifact path. Wire the check in `__main__.py` before the R1B semantic check.

**Pre-work**: Resolve GAP-1 by reading `__main__.py` R1B check wiring (lines ~254–300) and `cache/r1b_adapter.py`.

**Acceptance**:
- `_check_r1a_cache` returns `None` on miss, `Path` on hit
- R1A check appears before R1B in `__main__.py` control flow
- `test_apps_rg_route_order_r1a_r1b_r5_r4` passes

#### Phase 1.2 — R1B Cache Key Strengthening
**Scope**: Ensure `ResumeGenerationIntent.to_cache_key_dict()` includes all 14 fields: `candidate_profile_hash`, `master_resume_hash`, `jd_text_hash`, `company_brief_hash`, `target_company`, `role_title_hash`, `seniority_band`, `output_schema_hash`, `prompt_template_hash`, `policy_hash`, `blueprint_hash`, `model_lane_hash`, `freshness_class`, `cache_schema_version`.

**Pre-work**: Resolve GAP-2 by reading `types/intent_payload.py` and `utils/intent_builder.py`.

**Acceptance**:
- `to_cache_key_dict()` returns exactly 14 fields
- `test_apps_rg_r1b_cache_key_includes_jd_master_brief_policy_blueprint_schema` passes

#### Phase 1.3 — R1A/R1B Tests
**Scope**: Add/update governance tests for R1A dedup, R1B 14-field key, route ordering.

### Wave 2 — Prompt Assembly + prompt_bom Capture

#### Phase 2.1 — Create `prompt_assembly/pa_local.py`
**Scope**: New module at `apps_rg/prompt_assembly/pa_local.py` implementing `APP_LOCAL_PA_COMPATIBLE` posture. Exports `capture_prompt_bom(model_name, prompt_template_hash, token_budget, provider_lane) -> PromptBOM` dataclass. The BOM includes: model, template hash, token budget, provider lane, timestamp, replay_key.

**Acceptance**:
- Module importable
- `capture_prompt_bom()` returns a frozen dataclass
- BOM serializes to JSON

#### Phase 2.2 — Wrap HOP 3 LLM Calls
**Scope**: In `reasoning/RgResumeOrchestrator.py`, wrap each LLM invocation to call `capture_prompt_bom()` and write the BOM to `{run_dir}/prompt_bom/{hop_name}.json`.

**Pre-work**: Resolve GAP-3 by auditing which HOPs call LLM providers.

**Acceptance**:
- HOP 3 execution produces `prompt_bom/` directory in run_dir
- `test_apps_rg_prompt_manifest_emitted_for_model_generation` passes

#### Phase 2.3 — Wrap Narrative HOPs
**Scope**: Same prompt_bom wrapping for narrative pass HOPs (4A–4H) that call LLM. Deterministic HOPs are skipped.

**Pre-work**: Resolve GAP-3.

**Acceptance**:
- Narrative HOPs that call LLM produce prompt_bom entries
- No disruption to narrative pass output quality

#### Phase 2.4 — Prompt Assembly Tests
**Scope**: Tests for `pa_local.py` module, BOM serialization, presence in run_dir.

### Wave 3 — L4/UWG Optional Cache Commit + FEC Enrichment

#### Phase 3.1 — Wire Optional Cache Commit via Exit → UWG
**Scope**: After Exit computes X3D (success), if `cache_commit_enabled=true` in config, emit a `CommitRequest` that flows through UWG → L4 for semantic cache storage. This is the ONLY L4 write path — never direct.

**Pre-work**: Resolve GAP-4 and GAP-5.

**Acceptance**:
- Cache commit only fires after successful Exit X3D
- `test_apps_rg_cache_commit_only_via_exit_uwg_if_enabled` passes
- `test_apps_rg_no_direct_l4_write` still passes

#### Phase 3.2 — FEC Field Enrichment
**Scope**: Add fields to `cert/fec_producer.py`: `claim_to_source_map`, `unsupported_claims`, `fabricated_claims`, `brief_freshness_status`, `artifact_hashes`, `run_id`, `replay_key`. Clarify this is a local evidence contract, not C0 FEC.

**Acceptance**:
- FEC producer emits all new fields
- Existing FEC tests still pass
- New field tests pass

#### Phase 3.3 — L4/UWG/FEC Tests
**Scope**: Tests for UWG commit gating, FEC new fields.

### Wave 4 — E1-E5 Span Instrumentation + E5 Seal

#### Phase 4.1 — E1-E5 OTEL Span Instrumentation
**Scope**: Wrap `__main__.py` execution sections in explicit OTEL spans: `L2.E1_prep`, `L2.E2_validate`, `L2.E3_execute`, `L2.E4_heal`, `L2.E5_seal`. Use the existing `gr.span()` context manager.

**Acceptance**:
- OTEL traces show 5 named spans per run
- Span names match `L2.E1`–`L2.E5` pattern

#### Phase 4.2 — E5 Seal: Hash Computation + Replay Metadata
**Scope**: In E5 seal phase, compute SHA256 of `jd_hash`, `resume_hash`, `brief_hash`, `prompt_hash`, `policy_hash`, `blueprint_hash`. Write these plus `replay_key` into the sealed artifact JSON.

**Acceptance**:
- `test_apps_rg_l2_e5_sealed_artifact_contains_required_hashes` passes
- `test_apps_rg_replay_metadata_present` passes
- Sealed artifact JSON contains all 6 hashes + replay_key

#### Phase 4.3 — E1-E5 Span + Seal Tests
**Scope**: Tests for span names, hash presence, replay_key.

---

## Rules

- ❌ No broad refactors — scope limited to the 4 deferred waves
- ❌ No changes to files completed in parent plan (AGENTIC_SPINE.md, spine_manifest.yaml, company_research_loader.py, narrative_pass.py CLI args)
- ❌ No introduction of C0 retrieval, L3 orchestration, or runtime HITL
- ❌ No direct L4 writes — cache commit only through Exit → UWG
- ❌ No disruption to HOP behavior — prompt_bom wrapping is observability, not logic
- ❌ No weakening of existing test assertions
- ✅ Preserve all 22 governance tests from parent plan
- ✅ Resolve parent plan open questions Q1-Q6 during pre-work
- ✅ Each wave independently testable

---

## Success Criteria

- [ ] R1A exact cache dedup functional with SHA256 key
- [ ] R1B cache key includes all 14 required fields
- [ ] Route ordering: R1A → R1B → R5 → R4 in __main__.py
- [ ] `pa_local.py` module exists and emits prompt_bom
- [ ] HOP 3 + narrative HOPs produce prompt_bom artifacts
- [ ] Cache commit fires only after Exit X3D with config flag
- [ ] No direct L4 writes (test green)
- [ ] FEC producer includes all new fields
- [ ] E1-E5 OTEL spans present in traces
- [ ] E5 sealed artifact contains 6 hashes + replay_key
- [ ] All 22 parent tests still green
- [ ] 15+ new tests green

---

## Dependency Graph

```
W1 (R1A/R1B cache) → no deps (parent complete)
W2 (prompt assembly) → no deps (parent complete)
W3 (L4/UWG/FEC) → depends on W1 (R1A key used for cache commit candidate)
W4 (E1-E5 spans) → depends on W2 (prompt_bom in E1/E3), parent W5 (sealed packets in E5)
```

---

## Rollback Strategy

1. Each wave is independently revertable via `git revert` of the wave's commits
2. No shared-code changes — all edits are apps_rg-local
3. Cache commit is config-gated — disable via `cache_commit_enabled: false`
4. Prompt_bom capture is observability-only — removing it does not affect domain behavior

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| R1A exact cache hit | Returns cached path for identical inputs | `test_apps_rg_route_order_r1a_r1b_r5_r4` |
| R1B 14-field key | `to_cache_key_dict()` returns 14 fields | `test_apps_rg_r1b_cache_key_includes_*` |
| Prompt_bom artifact | Present in `run_dir/prompt_bom/` for LLM HOPs | `test_apps_rg_prompt_manifest_emitted_*` |
| Cache commit gating | Only via Exit X3D + config flag | `test_apps_rg_cache_commit_only_via_exit_uwg_*` |
| No direct L4 write | Zero `SemanticCacheManager.store()` outside Exit path | `test_apps_rg_no_direct_l4_write` |
| E5 hashes | 6 SHA256 hashes in sealed artifact | `test_apps_rg_l2_e5_sealed_artifact_*` |
| Replay metadata | `replay_key` in sealed artifact | `test_apps_rg_replay_metadata_present` |
| Parent regression | 22/22 parent tests green | `pytest tests/governance/test_apps_rg_spine_refactor.py` |

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
