# apps_rg reasoning intensity audit (tiered lanes, HTTP singleton)

**Date:** 2026-05-16 (updated trace parity pass)  

## Status accounting (not unconditional global PASS)

| Dimension | Status |
|-----------|--------|
| SCOPED_REASONING_INTENSITY_PROFILE | PASS |
| EXECUTIVE_SUMMARY_DOMINANCE | PASS |
| HTTP_SINGLETON_RECEIPT_HONESTY | PASS |
| CRITICAL_LANES_PROMPT_TRACE_RECEIPT_PARITY (`executive_summary`, `headline`, `competencies`, `unify_narrative`, `unify_bullets`) | PASS |
| FULL_APPS_RG_RUNTIME_TRACE_PARITY (IBM lanes, education, certs, aggregated exit packet merges) | OPEN |
| T1_DISPATCH_BINDING | OPEN (reserved enum tier only — see matrix) |
| T3_SINGLETON_AGGREGATE_BLOCKED_ON_REFLEXION | OPEN (explicit **policy posture** kept — below) |
| FULL_APPS_RG_UNIT_TREE | PARTIAL — pre-existing collection/import failures unrelated to reasoning seam |
| **OVERALL** | **PARTIAL** |

**Scope:** Tiered declarative knobs per `_reasoning_section_lane`, truthful `ReasoningExecutionReceipt`, X1D certification cap for executive summary, **`prompt_selection_trace.json` reasoning snapshot** on critical lanes.

**T3 singleton + reflexion (policy posture):** keep **honest receipts** (`reflexion_loops` POLICY_REQUIRED, **IGNORED** on singleton ⇒ `aggregate_blocked` may attach) until a **narrow branch/sample runner** exists or exits are rewired for explicit SOFTEN-vs-RUNNER. Do **not** paper over unexecuted loops as APPLIED.

**T1 posture:** remove from active singleton-softening logic until a lane binds `ReasoningIntensityTier.T1_SIMPLE_REWRITE`; unknown lanes remain **T2_QUALITY** fallback (documented).

## SSOT files

| Surface | Role |
|--------|------|
| `agentic_core/runtime/config/reasoning_types.py` | Shared reasoning **types/contracts** used by resolver/plan (generic). |
| `agentic_core/runtime/reasoning/reasoning_control_resolver.py` | Resolves gateway receipts; orch rows use **IGNORED** + `proved_reference` JSON (`samples_*`, `loops_*`, requested branch depth). |
| `agentic_core/L3_orchestration/exit_eval/v6/x1_gates.py` | X1D post-pass cap: exec lane demands valid receipt; QUALITY_DENIED → WARN with exec-specific codes. |
| `apps_rg/runtime/reasoning/section_reasoning_intensity.py` | **Declarative tier map**: lane → `SectionReasoningProfile` (temperature, TotT, reflexion, self-consistency targets). ExecSummary > T2/T0 on knobs. |
| `apps_rg/runtime/reasoning/apps_rg_http_reasoning_plan.py` | Adapts gateway requirements: **`T2_QUALITY_SECTION` singleton** softens orch **QUALITY_REQUIRED → OPTIONAL** and **reflexion POLICY_REQUIRED → OPTIONAL**. **T0/T3/exec_lane** unchanged. **T1_SIMPLE_REWRITE** is not bound — not in soften branch. |
| `apps_rg/runtime/providers/section_qwen_slice.py` | Canonical `call_qwen_vllm`: strip orch/scratch/meta from HTTP JSON; clamp temperature from lane profile; attach receipt. |
| `apps_rg/runtime/providers/qwen_vllm_provider.py` | HTTP transport only; wider temperature bounds **clamped here** after profile overwrite. |

## Receipt / transport truths (singleton HTTP)

- **Orchestration** controls (TotT branches/depth, self-consistency N>1, reflexion loops>0) are **not executed** by a single chat completion unless a multi-call runner proves them — resolver marks **`IGNORED`** / `proved_reference` captures requested vs completed (**1 sample / 0 loops** heuristic).
- **Do not mark APPLIED** for orch on singleton gateway unless observability proves execution (not in scope for bare HTTP slice).
- **Scratchpad:** forbidden keys raise before HTTP; sanitized body never forwards `_reasoning_*` meta.

## Gap matrix

| SECTION (lane key) | CURRENT_PROFILE (`SectionReasoningProfile`) | CURRENT_KNOBS | CRITICALITY | TARGET_PROFILE | REQUIRED_CONTROLS | CURRENTLY_PROVED | GAP |
|--------------------|---------------------------------------------|---------------|-------------|----------------|-------------------|------------------|-----|
| education | T0_LOCKED | temp 0.15, tot_b=1, tot_d=1, sc=1, ref=0 | locked fact | T0_LOCKED_FACT | deterministic low temp; no reflexion | temp on wire; orch inactive / ignored | Runner not needed; multi-sample pointless |
| certifications | T0_LOCKED | same as education | locked fact | T0_LOCKED_FACT | same | same | Same |
| headline | T3_CRITICAL (non-exec) | temp 0.39, tot_b 3/2 depth, sc 4, ref 1 | critical narrative | T3_CRITICAL_SECTION | QUALITY orch rows + certification policy | Receipt + `prompt_selection_trace` lane/receipt snapshot + IGNORED orch + transport temp | **Full branch execution / cleared aggregate_blocked on reflexion** — OPEN until runner |
| executive_summary | T3_CRITICAL **exec_lane** | temp **0.42**, tot_b 3/2 depth, **sc 5**, **ref 2** | highest leverage | ≥T3_CRITICAL; **>** T2/T0 | QUALITY_REQUIRED on multi-sample/branches/reflex where policy applies | Receipt on `ProviderResult`; `prompt_selection_trace` lane + receipt | **Full multi-branch execution** deferred — receipt stays honest (IGNORED orch). |
| competencies | T3_CRITICAL | same non-exec T3 knobs | JD match / critical | T3_CRITICAL_SECTION | QUALITY orch + cert policy | Receipt + `prompt_selection_trace` lane/receipt snapshot | Deferred branch runner / reflex POLICY unblock |
| unify_narrative | T3_CRITICAL | non-exec T3 | critical unify | T3_CRITICAL_SECTION | same | Receipt + trace snapshot | Deferred branch runner |
| unify_bullets | T3_CRITICAL | non-exec T3 | critical unify bullets | T3_CRITICAL_SECTION | same | Receipt + trace snapshot | Deferred branch runner |
| ibm_narrative | T2_QUALITY | temp 0.32, tot_b 2/2 depth, sc 3, ref 1 | quality section | T2_QUALITY_SECTION | Relaxed QUALITY orch (OPTIONAL mapping) honest on singleton | Temp + degraded orch acknowledgment | Candidate voting not executed |
| ibm_bullets | T2_QUALITY | same | quality bullets | T2_QUALITY_SECTION | same | same | Candidate voting not executed |
| **T1_SIMPLE_REWRITE (reserved tier)** | **Not mapped** (`_lane_map` has no T1 profiles) | *n/a until bound* | future simple rewrite tier | — | RESERVED | none | Dispatch binding **OPEN**. `apps_rg_http_reasoning_plan` **does not** treat T1 for singleton softening. Unknown lane → `_T2_QUALITY` |

## Regression coverage

- `apps_rg.runtime.reasoning.executive_summary_must_dominate_lesser_sections()`
- Unit file `tests/unit/apps_rg/test_reasoning_intensity_profiles.py`
- X1D: executive lane proof missing / invalid receipt → `REASONING_EXECUTIVE_SUMMARY_*` reason codes (`test_x1_gates.py`)

## Narrow follow-ups (still OUT OF overall PASS)

1. **IBM / locked / certs** traces: optionally merge reasoning fields into `prompt_selection_trace.json` same as critical lanes when those paths expose exit packets.
2. **T3 runner OR policy fork:** instrument multi-call sampler for T3/reflex intents, OR document consumer-side interpretation of `aggregate_blocked` vs quality gates (separate plan).
3. **T1:** add explicit lane keys + presets when rewrite-only sections exist.

## Helper

- `apps_rg/runtime/dispatch/prompt_trace_reasoning.py` — shared `attach_reasoning_to_prompt_trace` for parity across critical dispatches.
