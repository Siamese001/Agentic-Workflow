# apps_* PA Spine Hardening — W5 Remaining (5 Apps)

**Slug:** `apps-pa-spine-w5-remaining-7e820f`
**Status:** Not Started
**Tier:** T3
**Parent plan:** `apps-rg-spine-hardening-deferred-wave-2f8b1d` W5 P5.2–P5.6
**Pattern source:** `apps-qna-pa-spine-hardening-498d20` (completed pattern-setter)
**Authored:** 2026-05-09

> Deferred scope from W5 of apps-rg-spine-hardening-deferred-wave-2f8b1d.
> Apply the PA spine hardening pattern (validated on apps_qna) to the 5 remaining
> sibling apps. Each app gets its own child plan slug following the established pattern.
>
> **DO NOT IMPLEMENT** — planning/decomposition only until explicitly activated.

---

## Context: Pattern Established by apps_qna (P5.1)

The `apps-qna-pa-spine-hardening-498d20` plan validated the 4-wave pattern:

| Wave | Deliverable |
|---|---|
| W1 | PA boundary audit — classify each SDK-touching file as SANCTIONED / PASS / CONDITIONAL_V1 / ERROR |
| W2 | Extend `check_apps_rg_pa_boundary.py` — new `_iter_<app>_files()` + `--no-<app>` flag + allowlist/baseline entries |
| W3 | Create `<app>/airlocks/` — `_otel_spans.py` + route-specific gate functions |
| W4 | Contract tests in `tests/_apps_contract/test_<app>_pa_spine.py` — ≥8 tests |

**Key pattern learning:** Look for existing `llm_client.py` shims first. Lazy-import + env-gated + fail-soft SDK callers = CONDITIONAL_V1 (not ERROR). Each app needs route-specific airlocks matching its `spine_manifest.yaml` route types.

---

## Apps to Harden (5 remaining, P5.2–P5.6)

### P5.2 — apps_research

**Priority:** High (grounded C0 RAG app; direct SDK calls likely in research engines)

Pre-scan findings (from W5 parent plan):
- `apps_research/engines/company_brief_engine.py` — known Qwen/vLLM caller
- Check for existing shim at `apps_research/integrations/` (if any)
- Route types: `R3_RESEARCH` (grounded brief synthesis)

Deliverables:
- Child plan slug: `apps-research-pa-spine-hardening-<6hex>.md`
- `apps_research/airlocks/` with research-input gate + C0-evidence gate
- Scanner coverage: `_iter_apps_research_files()` + baseline

---

### P5.3 — apps_underwriting_ai

**Priority:** High (L5 safety gatekeeper surface; underwriting decisions require strict PA)

Pre-scan findings (from W5 parent plan):
- `apps_underwriting_ai/engines/` — decision packet assembler may call LLM
- Already has eval rubric + domain contract (from eval harness plans)
- Route types: check `spine_manifest.yaml`

Deliverables:
- Child plan slug: `apps-underwriting-pa-spine-hardening-<6hex>.md`
- `apps_underwriting_ai/airlocks/` with underwriting-input gate
- Scanner coverage + baseline

---

### P5.4 — apps_lic

**Priority:** Medium (already has `apps_lic/airlocks/hitl_reentry.py` — partial coverage)

Pre-scan findings:
- `hitl_reentry.py` imports from `apps_rg.airlocks` — cross-app dependency; already partially hardened
- Needs own `_otel_spans.py` (currently borrows from apps_rg)
- Route types: messaging/profile planner (check `spine_manifest.yaml`)

Deliverables:
- Child plan slug: `apps-lic-pa-spine-hardening-<6hex>.md`
- Extend `apps_lic/airlocks/` with `_otel_spans.py` + additional route gates
- Break cross-app airlock import dependency (apps_lic should not import from apps_rg.airlocks)
- Scanner coverage + baseline

---

### P5.5 — apps_rfp

**Priority:** Medium (RFP proposal assembly — LLM calls in hop_proposal_assembly_engine.py)

Pre-scan findings:
- `apps_rfp/engines/hop_proposal_assembly_engine.py` — hop-based LLM assembly
- `apps_rfp/integrations/governed_rfp_run.py` — governed execution wrapper
- Route types: check `spine_manifest.yaml`

Deliverables:
- Child plan slug: `apps-rfp-pa-spine-hardening-<6hex>.md`
- `apps_rfp/airlocks/` with proposal-input gate
- Scanner coverage + baseline

---

### P5.6 — apps_exec

**Priority:** Low (executive brief app; check if LLM calls exist at all)

Pre-scan findings:
- `apps_exec/` directory is minimal — may be largely stub/delegating
- Check `config/domain_contract/` for eval rubrics (already has RAG dims from eval harness plan)
- Route types: check `spine_manifest.yaml`

Deliverables:
- Child plan slug: `apps-exec-pa-spine-hardening-<6hex>.md`
- `apps_exec/airlocks/` (if SDK calls found; otherwise document as PASS)
- Scanner coverage (even if no violations)

---

## Wave Structure (this meta-plan)

| Wave | Scope | Status |
|---|---|---|
| W5.2 | apps_research child plan + W1-W4 | Not Started |
| W5.3 | apps_underwriting_ai child plan + W1-W4 | Not Started |
| W5.4 | apps_lic child plan + W1-W4 | Not Started |
| W5.5 | apps_rfp child plan + W1-W4 | Not Started |
| W5.6 | apps_exec child plan + W1-W4 | Not Started |

W5.2–W5.6 may be run in parallel (each app is independent) or sequentially.
apps_lic (W5.4) should be run before apps_rfp/apps_exec since it has existing partial coverage
that establishes the delta scope.

## Activation Gate

Before starting any wave here:
1. `apps-qna-pa-spine-hardening-498d20` must be **Completed** ✅ (already done)
2. User explicitly activates this plan ("start W5.2" or "start apps_research hardening")
3. Run ADG hotspot check for target app before drafting child plan

## Non-Goals (this meta-plan)

- No implementation — planning/decomposition only
- No SovereignLLMGateway wiring (NEXT_STEP-1, tracked separately)
- No PA logic changes in any app
- No C0 FEC producer binding (separate plan)
- No circular import resolutions (W3 of parent plan is permanently deferred)

## Files This Plan Will Touch (when activated)

| App | New Files | Modified Files |
|---|---|---|
| apps_research | `apps_research/airlocks/*.py`, `tests/_apps_contract/test_apps_research_pa_spine.py` | `check_apps_rg_pa_boundary.py` |
| apps_underwriting_ai | `apps_underwriting_ai/airlocks/*.py`, `tests/_apps_contract/test_apps_underwriting_pa_spine.py` | `check_apps_rg_pa_boundary.py` |
| apps_lic | `apps_lic/airlocks/_otel_spans.py`, `tests/_apps_contract/test_apps_lic_pa_spine.py` | `check_apps_rg_pa_boundary.py`, `apps_lic/airlocks/hitl_reentry.py` |
| apps_rfp | `apps_rfp/airlocks/*.py`, `tests/_apps_contract/test_apps_rfp_pa_spine.py` | `check_apps_rg_pa_boundary.py` |
| apps_exec | `apps_exec/airlocks/*.py` (if needed), `tests/_apps_contract/test_apps_exec_pa_spine.py` | `check_apps_rg_pa_boundary.py` |
