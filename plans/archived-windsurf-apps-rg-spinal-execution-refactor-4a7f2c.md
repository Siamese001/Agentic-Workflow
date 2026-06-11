---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-spinal-execution-refactor-4a7f2c.md'
original_relative_path: 'apps-rg-spinal-execution-refactor-4a7f2c.md'
source_sha256: 39899ecd974890f9be7338ff350f7ff4c7c49901e8dfb455c0769c1be01f0483
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: apps_rg → agentic_core Spinal Execution Refactor
**Slug:** `apps-rg-spinal-execution-refactor-4a7f2c`
**Status:** ⛔ **ARCHIVED / DO NOT IMPLEMENT** (2026-05-09)
**Superseded by:** `apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md`
**Tier:** T3 — cross-layer, multi-file, architectural
**Created:** 2026-05-28
**Amended:** 2026-05-09 — corrected W5 ownership, added FinalEvidenceContract, execution_form vocabulary, Gemini fail-closed
**Superseded:** 2026-05-09 — see supersession note below

---

## ⛔ SUPERSESSION NOTICE

This plan is **rejected and replaced**. Do not implement.

**Reason for supersession.** The amended W5 still preserves `apps_rg` as a live runtime
participant via four runtime adapters:

- `apps_rg/adapters/l1_resume_planner.py`
- `apps_rg/adapters/rg_route_profile.py`
- `apps_rg/adapters/rg_prompt_refs.py`
- `apps_rg/adapters/rg_l2_resume_executor.py`

Even with the corrected ownership language ("supplies hints/refs only", "called by core L2"),
this architecture preserves runtime gravity inside `apps_rg` and leaves room for a shadow
pipeline. The replacement plan elevates the constraint from "ownership of contract emission"
to **"`apps_rg` is an ingress and declarative domain profile package only — it has no runtime
authority of any kind."**

**Replacement plan:** `@c:\Git\Agentic-Workflow-FRESH\.windsurf\plans\apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md`

**Carried forward** (see new plan §2): contract chain, `execution_form` vocabulary,
`FinalEvidenceContract` / `CompiledPromptArtifact` conditional rules, Gemini fail-closed,
ADG preflight, quarantine targets, wizard preservation, bypass guards, OTEL chain (extended
with L7 audit), L3 deferral rule.

**Dropped** (see new plan §3): all four `apps_rg/adapters/*` runtime adapter files; any
`apps_rg` call to `get_llm_gateway()` or `SovereignLLMGateway`; any "registered domain
adapters" framing.

**Status authority:** This file remains on disk as historical record per zero-loss
discipline. No content below this notice should be implemented. The Notion Plans DB row
for this plan must be patched to `Retired`.

---

> **The remainder of this file is preserved verbatim for historical traceability. Do not act on it.**

---

---

## Objective

Transition `apps_rg` from a self-orchestrating application that owns runtime flow and
calls model providers directly, into a collection of registered domain adapters under
the `agentic_core` spine. After this refactor:

- `apps_rg/__main__.py` calls `agentic_core.runtime.entry.app_ingress_runner.AppIngressRunner`
  (or equivalent spine entry point) — never `RgResumeOrchestrator`.
- ALL LLM/vLLM calls flow exclusively through `agentic_core.L2_execution.enforcement.SovereignLLMGateway`
  via `get_llm_gateway()`.
- The ordered contract chain is enforced (conditional steps in brackets):

  ```
  L1PlanContract
    → RouteContract
      → [FinalEvidenceContract if grounding_required]
        → [CompiledPromptArtifact if model_generation_required]
          → SealedL2Artifact
            → X3Disposition
  ```

- **Authority ownership is non-negotiable:** `apps_rg` supplies domain hints, refs, and
  payloads ONLY. `agentic_core` L0 owns `RouteContract` emission. `agentic_core` Prompt
  Assembly owns `CompiledPromptArtifact` emission. `agentic_core` L2 owns `SealedL2Artifact`
  emission. `apps_rg` adapters never emit core contracts.

---

## Author-Gate Decisions (Locked)

| ID | Decision | Selected Option |
|----|----------|----------------|
| AG-1 | `RgResumeOrchestrator` disposition | **A — Quarantine whole.** Move to `apps_rg/reasoning/_quarantine/` with a tombstone shim; no deletion yet (90-day deprecation). |
| AG-2 | L1 planner location | **B — New `apps_rg/adapters/l1_resume_planner.py`.** Called by `agentic_core` L1; produces resume-specific planning payload. Core L1 validates and freezes the canonical `L1PlanContract`. Adapter is deterministic; no LLM calls. |
| AG-3 | Provider egress | **B-prime — Re-home cascade under SovereignLLMGateway provider layer.** `apps_rg` MUST NOT retain provider egress ownership. `_llm_client.py` Qwen/Anthropic/OpenAI/Gemini cascade logic is ported into registered `ProviderConfig` entries under the gateway's `_providers` dict. `apps_rg` calls `get_llm_gateway().route_generation(request)` only. |
| AG-4 | L3 deferral | **Defer L3 for v1 only when the runtime is a TRUE `SINGLE_STEP` route.** Any multi-hop workflow MUST be expressed as a proper L3 orchestration node — no hidden multi-step logic is permitted inside L2. |
| AG-5 | Test surface | **Both runtime assertions AND pytest bypass guards.** Tests prove the ordered contract chain fires; separate bypass-guard tests prove the spine is not circumventable. |

---

## Hard Constraints

1. `apps_rg` CLI MUST NOT call `RgResumeOrchestrator` or model providers directly.
2. `RgResumeOrchestrator` MUST be quarantined (not deleted; 90-day deprecation path).
3. No Qwen/OpenAI/Anthropic call may occur outside `agentic_core` L2 via `SovereignLLMGateway`. **Gemini is unsupported in v1 and MUST fail closed if selected.** No Gemini direct call may remain anywhere in `apps_rg` after W6.
4. `agentic_core` L1 MUST emit a canonical `L1PlanContract` before L0 runs. `apps_rg` supplies the resume-specific planning payload only.
5. `agentic_core` L0 MUST emit exactly one `RouteContract` before grounding/PA/L2/L3 runs. `apps_rg` supplies route hints/profile only — adapters MUST NOT emit `RouteContract`.
6. When `grounding_required = true` on the route, `agentic_core` MUST emit exactly one `FinalEvidenceContract` before Prompt Assembly runs.
7. When `model_generation_required = true` on the route, `agentic_core` Prompt Assembly MUST produce a signed `CompiledPromptArtifact` before any model generation. `apps_rg` supplies prompt component refs / response schema refs / examples / domain constraints only — adapters MUST NOT emit `CompiledPromptArtifact`.
8. `agentic_core` L2 MUST execute one bounded packet through `SovereignLLMGateway` and return a `SealedL2Artifact`. The `apps_rg` L2 executor adapter is invoked by core L2 with an `ApprovedWorkOrder` and returns the payload core L2 seals.
9. Exit MUST emit exactly one `X3Disposition` before user-visible output.
10. Tests MUST prove the ordered contract chain (including conditional `FinalEvidenceContract` / `CompiledPromptArtifact` steps) and block direct provider/orchestrator bypasses.
11. OTEL spans MUST prove U0 → L1 → L0 → [grounding] → [PA] → L2 → Exit; conditional steps emit named spans only when their predicates fire.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W0 | W0.1–W0.2 | Author-Gate decisions + SR_PLAN draft + plan registration | ~2 k | All AG decisions locked by user | ✅ DONE | Plan on disk; registered in Notion Plans DB |
| W1 | W1.1–W1.3 | Pre-flight ADG green-light + hotspot/fan-in evidence + inventory | ~3 k | ADG MCP healthy | 🔲 | ADG health green; hotspot report authored; fan-in evidence collected for `RgResumeOrchestrator` and `_llm_client.py` |
| W2 | W2.1–W2.2 | Contract inventory and reuse map | ~2 k | W1 complete | 🔲 | All existing contracts identified; reuse map authored; missing contracts listed |
| W3 | W3.1–W3.5 | Author missing contracts only | ~5 k | W2 complete | 🔲 | `L1PlanContract`, `RouteContract`, `FinalEvidenceContract`, `SealedL2Artifact`, `X3Disposition` authored; unit-typed; import-clean |
| W4 | W4.1–W4.2 | Quarantine orchestrator + dead L1 modules | ~3 k | W3 complete | 🔲 | `RgResumeOrchestrator` moved to `_quarantine/`; tombstone shim in place; `jd_planner.py` archived; import-scan passes |
| W5 | W5.1–W5.4 | Author `apps_rg` domain adapters (no core-contract authority) | ~6 k | W4 complete | 🔲 | `l1_resume_planner.py` produces planning payload (core L1 freezes `L1PlanContract`); `rg_route_profile.py` supplies route hints only (core L0 emits `RouteContract`); `rg_prompt_refs.py` supplies refs/schemas/examples (core PA emits `CompiledPromptArtifact`); `rg_l2_resume_executor.py` invoked by core L2 with `ApprovedWorkOrder`, executes one bounded packet through `SovereignLLMGateway`, returns payload for core L2 sealing |
| W6 | W6.1–W6.2 | Re-home provider cascade under `SovereignLLMGateway` | ~4 k | W5 complete | 🔲 | Qwen vLLM / Anthropic / OpenAI providers registered in gateway; **Gemini fails closed at gateway with explicit `UnsupportedProviderError`**; `_llm_client.py` marked deprecated (tombstone comment); `apps_rg` has zero direct provider imports (Gemini included) |
| W7 | W7.1 | Rewrite `apps_rg/__main__.py` → `agentic_core` spine | ~3 k | W6 complete | 🔲 | `__main__.py` uses `AppIngressRunner` dispatch path; no `RgResumeOrchestrator` reference; smoke test passes |
| W8 | W8.1–W8.3 | Runtime assertions + pytest bypass guards | ~5 k | W7 complete | 🔲 | Contract-chain tests pass; bypass-guard tests catch direct provider calls; coverage ≥ 80 % on new adapter files |
| W9 | W9.1–W9.3 | OTEL span-chain proof + Notion evidence writeback + deferred `AG_QUEUE_SEED` | ~3 k | W8 complete | 🔲 | Span trace proves U0→L1→L0→PA→L2→Exit; Notion plan row updated to Completed; deferred AG seeds written |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | AG decision locking + SR_PLAN | 1 plan file | None | ~1 k | ✅ DONE |
| W0.2 | Notion plan registration | Notion Plans DB | Must emit `PLAN_CREATED:` before `start` | ~1 k | ✅ DONE |
| W1.1 | ADG green-light | ADG MCP | ADG snapshot may be stale | ~1 k | 🔲 |
| W1.2 | Hotspot / fan-in report | `RgResumeOrchestrator.py`, `_llm_client.py` | Fan-in may reveal undiscovered callers | ~1 k | 🔲 |
| W1.3 | File inventory | All `apps_rg/` Python files | Broken import in `resume_planning_engine.py` already known | ~1 k | 🔲 |
| W2.1 | Existing contract scan | `agentic_core/runtime/contracts/`, `agentic_core/L2_execution/reasoning/` | `CompiledPromptArtifact` exists; others do not | ~1 k | 🔲 |
| W2.2 | Reuse map + gap list | Plan doc update | Must not overwrite `CompiledPromptArtifact` | ~1 k | 🔲 |
| W3.1 | Author `L1PlanContract` | `agentic_core/runtime/contracts/l1_plan_contract.py` (new) | Frozen dataclass; emitted by core L1 only; no LLM calls | ~1 k | 🔲 |
| W3.2 | Author `RouteContract` | `agentic_core/runtime/contracts/route_contract.py` (new) | **Carries `execution_form: Literal["TERMINAL_SHORTCIRCUIT", "SINGLE_STEP", "MANAGED_WORKFLOW"]`**; also `grounding_required: bool`, `model_generation_required: bool`; emitted by core L0 only | ~1 k | 🔲 |
| W3.3 | Author `FinalEvidenceContract` | `agentic_core/runtime/contracts/final_evidence_contract.py` (new) | Frozen dataclass; emitted by core grounding stage only when `route.grounding_required = true`; binds evidence refs + provenance hashes to `trace_id` | ~1 k | 🔲 |
| W3.4 | Author `SealedL2Artifact` | `agentic_core/runtime/contracts/sealed_l2_artifact.py` (new) | Frozen dataclass; carries `trace_id` binding to `CompiledPromptArtifact.trace_id` (when present); emitted by core L2 only | ~1 k | 🔲 |
| W3.5 | Author `X3Disposition` | `agentic_core/runtime/contracts/x3_disposition.py` (new) | Exactly one per request; drives user-visible output | ~1 k | 🔲 |
| W4.1 | Quarantine `RgResumeOrchestrator` | `apps_rg/reasoning/RgResumeOrchestrator.py` → `apps_rg/reasoning/_quarantine/` | Tombstone shim must preserve public API surface for 90 days | ~2 k | 🔲 |
| W4.2 | Archive dead L1 modules | `apps_rg/L1_cognition/jd_planner.py`, `apps_rg/engines/resume_planning_engine.py` (broken import) | Confirm zero live callers via ADG fan-in before archival | ~1 k | 🔲 |
| W5.1 | `l1_resume_planner.py` adapter | `apps_rg/adapters/l1_resume_planner.py` (new) | Called by core L1; produces resume-specific planning payload (role focus, industry, section weights). **Core L1 validates and freezes the canonical `L1PlanContract`** — adapter does NOT emit it. Deterministic; no LLM calls | ~1.5 k | 🔲 |
| W5.2 | `rg_route_profile.py` adapter | `apps_rg/adapters/rg_route_profile.py` (new) | Supplies route hints / profile only (e.g. `RouteHintSet` / `RouteProfile`: candidate execution_form, grounding need, expected token budget). **Adapter MUST NOT emit `RouteContract`** — core L0 consumes the hints and emits exactly one `RouteContract` | ~1.5 k | 🔲 |
| W5.3 | `rg_prompt_refs.py` adapter | `apps_rg/adapters/rg_prompt_refs.py` (new) | Supplies prompt component refs, response schema refs, few-shot examples, and domain constraints. **Adapter MUST NOT assemble the provider prompt or emit `CompiledPromptArtifact`** — core Prompt Assembly consumes the refs and emits the signed artifact | ~1.5 k | 🔲 |
| W5.4 | `rg_l2_resume_executor.py` adapter | `apps_rg/adapters/rg_l2_resume_executor.py` (new) | Called only by core L2 with an `ApprovedWorkOrder`. Executes one bounded resume-generation packet through `SovereignLLMGateway.route_generation()`. Returns the raw payload for core L2 to seal into `SealedL2Artifact` — adapter does NOT seal | ~1.5 k | 🔲 |
| W6.1 | Port cascade to gateway providers | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | Register `LOCAL_VLLM` (Qwen), `ANTHROPIC`, `OPENAI` provider configs from `_llm_client.py` cascade. **Gemini (`VERTEX_AI`) is registered as a fail-closed stub** that raises `UnsupportedProviderError` — no Google SDK call is wired in v1 | ~2 k | 🔲 |
| W6.2 | Tombstone `_llm_client.py` | `apps_rg/integrations/hops/_llm_client.py` | Must add deprecation header; zero new callers; existing callers redirected | ~2 k | 🔲 |
| W7.1 | Rewrite `__main__.py` | `apps_rg/__main__.py` | Interactive wizard MUST still fire (per `apps-rg-interactive-discipline.md`); must use `AppIngressRunner` dispatch | ~3 k | 🔲 |
| W8.1 | Contract-chain tests | `tests/_apps_contract/test_apps_rg_spinal_chain.py` (new) | Proves `L1PlanContract → RouteContract → [FinalEvidenceContract] → [CompiledPromptArtifact] → SealedL2Artifact → X3Disposition` fires in order; conditional steps fire iff their predicates are true; ownership asserted (only core stages emit core contracts) | ~2 k | 🔲 |
| W8.2 | Bypass-guard tests | `tests/_apps_contract/test_apps_rg_bypass_guards.py` (new) | Asserts `RgResumeOrchestrator` import from `__main__` raises; direct `_llm_client` call raises; **`apps_rg` adapter emitting `RouteContract` / `CompiledPromptArtifact` / `SealedL2Artifact` raises** (ownership guard); Gemini selection raises `UnsupportedProviderError` | ~2 k | 🔲 |
| W8.3 | Coverage gate | All new adapter files | ≥ 80 % line coverage on W5 files | ~1 k | 🔲 |
| W9.1 | OTEL span-chain proof | `tests/_apps_contract/test_apps_rg_otel_spans.py` (new) | Span names: `rg.l1.plan`, `rg.l0.route`, `rg.grounding.evidence` (when `grounding_required`), `rg.pa.compile` (when `model_generation_required`), `rg.l2.execute`, `rg.exit.dispose`. Conditional spans MUST be absent when their predicates are false | ~1.5 k | 🔲 |
| W9.2 | Notion evidence writeback | Notion Plans DB | Post wave-complete state per `notion-plan-wave-deferral.md` | ~1 k | 🔲 |
| W9.3 | `AG_QUEUE_SEED` emission | Plan file | Seeds any deferred Author-Gate decisions surfaced during execution | ~0.5 k | 🔲 |

---

## ADG_HOTSPOT_REPORT

> Pre-flight evidence. To be populated in W1.2 after live ADG fan-in queries.

| Node | Layer | Fan-in | Est. Impact | Archetype | 5-Surface Intersections | Priority |
|------|-------|--------|-------------|-----------|------------------------|----------|
| `RgResumeOrchestrator` | L3 (apps_rg/reasoning) | TBD (W1.2) | TBD | ORCHESTRATOR | Execution, Write, State | P0 — quarantine |
| `_llm_client.make_generator` | L2 egress (apps_rg/integrations) | TBD (W1.2) | TBD | CENTRAL_DEPENDENCY | Execution, Security | P0 — re-home under gateway (Gemini path fails closed) |
| `jd_planner.plan_from_jd` | L1 (apps_rg/L1_cognition) | 0 (orphaned — confirmed) | Low | — | None | Archive |
| `ResumePlanningEngine` | L1 (apps_rg/engines) | TBD (W1.2) | TBD | CENTRAL_DEPENDENCY | Execution | P1 — broken import; archive or fix |

---

## ADG_GRAPH_LAYER_EVIDENCE

> Pre-flight evidence. To be populated in W1 after live ADG queries.

**Required MVs and semantic edges (to be verified in W1):**

1. `mv_hotspot_centrality` — rank `RgResumeOrchestrator` and `_llm_client.py` nodes by degree centrality and fan-in; confirm ORCHESTRATOR / CENTRAL_DEPENDENCY archetypes.
2. `adg_edge_fanin(relation_type="imports", tgt_id=<_llm_client node>)` — enumerate all callers of `make_generator` / `call_judge`; drives W6 re-homing scope.
3. `adg_edge_fanin(relation_type="imports", tgt_id=<RgResumeOrchestrator node>)` — enumerate all callers; drives W4 tombstone shim API surface.
4. `adg_edge_fanout(relation_type="flows_to", src_id=<RgResumeOrchestrator node>)` — confirm downstream L3 qwen-gateway dependency.
5. `v_p0_*` P-view scan — confirm no existing P0 violations in `apps_rg/reasoning/` that would block W4 quarantine.
6. `adg_violations` — confirm current violation count baseline before any W4+ edits land.

---

## Gap Register

| # | Gap | Risk | Mitigation |
|---|-----|------|-----------|
| G-1 | `SealedL2Artifact`, `L1PlanContract`, `RouteContract`, `X3Disposition` do not exist yet | High — contracts are load-bearing for constraint enforcement | W3 authors all four as frozen dataclasses; W8 tests validate |
| G-2 | `ResumePlanningEngine` has a broken import (`resume_section_node` vs `resume_section_node_types`) | Medium — may affect W4 archival completeness | W4.2 confirms no live callers via ADG; archives file |
| G-3 | Interactive wizard must be preserved in `__main__.py` (per `apps-rg-interactive-discipline.md`) | Medium — W7 rewrite must keep wizard TTY path intact | W7.1 wraps dispatch through `AppIngressRunner` while retaining wizard pre-flight |
| G-4 | Qwen vLLM runs under Docker Desktop, not WSL2 systemd; `LOCAL_VLLM` provider config must use `VLLM_BASE_URL=http://localhost:8000/v1` | Low — config value is known | W6.1 reads from env var; no hardcoding |
| G-5 | `_llm_client.py` may have callers outside `apps_rg` (cross-app import) | Medium — ADG fan-in will reveal | W1.2 checks; W6.2 tombstone guards against new callers |

---

## Files in Scope

**New files:**
- `agentic_core/runtime/contracts/l1_plan_contract.py`
- `agentic_core/runtime/contracts/route_contract.py`
- `agentic_core/runtime/contracts/final_evidence_contract.py`
- `agentic_core/runtime/contracts/sealed_l2_artifact.py`
- `agentic_core/runtime/contracts/x3_disposition.py`
- `apps_rg/adapters/__init__.py`
- `apps_rg/adapters/l1_resume_planner.py`
- `apps_rg/adapters/rg_route_profile.py`
- `apps_rg/adapters/rg_prompt_refs.py`
- `apps_rg/adapters/rg_l2_resume_executor.py`
- `apps_rg/reasoning/_quarantine/__init__.py`
- `apps_rg/reasoning/_quarantine/RgResumeOrchestrator.py` (tombstone shim)
- `tests/_apps_contract/test_apps_rg_spinal_chain.py`
- `tests/_apps_contract/test_apps_rg_bypass_guards.py`
- `tests/_apps_contract/test_apps_rg_otel_spans.py`

**Modified files:**
- `apps_rg/__main__.py` — spine dispatch rewrite
- `apps_rg/integrations/hops/_llm_client.py` — tombstone header; no callers from W7+
- `apps_rg/reasoning/RgResumeOrchestrator.py` — moved to `_quarantine/`; shim replaces original
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` — W6 provider registrations
- `apps_rg/L1_cognition/jd_planner.py` — moved to `apps_rg/L1_cognition/_archive/`
- `apps_rg/engines/resume_planning_engine.py` — moved to `_quarantine/` or `_archive/` pending W4.2 ADG check

---

## Deferred Scope

DEFERRED_SCOPE: L3 MANAGED_WORKFLOW orchestration for `apps_rg` resume generation (AG-4 — deferred only when `route.execution_form = SINGLE_STEP`; true multi-hop MANAGED_WORKFLOW pipeline deferred to v2; `TERMINAL_SHORTCIRCUIT` and `SINGLE_STEP` are in scope for v1)
DEFERRED_SCOPE: Gemini (`VERTEX_AI`) provider SDK wiring in `SovereignLLMGateway` (v1 ships a fail-closed `UnsupportedProviderError` stub; full `google-generativeai` SDK wiring deferred post-W9 — no Gemini direct call may remain anywhere in `apps_rg`)
DEFERRED_SCOPE: UWG promotion of `L1PlanContract` / `RouteContract` / `FinalEvidenceContract` to L4 state store (evaluation/promotion gate required; deferred post-W9)
