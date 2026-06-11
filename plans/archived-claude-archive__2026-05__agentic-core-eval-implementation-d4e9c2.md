---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\agentic-core-eval-implementation-d4e9c2.md'
original_relative_path: '_archive\\2026-05\\agentic-core-eval-implementation-d4e9c2.md'
source_sha256: a9cade4eaf3aab19b45780e483c7b264aa215db8247de706f99fe1fffac0de64
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# agentic_core Eval/Control Audit — Operational Implementation

**Slug**: `agentic-core-eval-implementation-d4e9c2`
**Parent reports:**
- `docs/reports/agentic_core_eval_control_audit/2026-05-02.md` (parent audit)
- `docs/reports/agentic_core_eval_control_audit/2026-05-02-per-module-followup.md` (per-module follow-up)
- `docs/reports/agentic_core_eval_control_audit/2026-05-02-gap-closure.md` (gap-closure → `RECOMMENDATION_AUDIT_NEEDS_TARGETED_FIXES`)

**Date opened**: 2026-05-02
**Tier**: T2 (≤7 files, additive only, no cross-layer flow change)
**Status**: Draft

---

## 1 · Why This Plan Exists

The gap-closure audit returned `RECOMMENDATION_AUDIT_NEEDS_TARGETED_FIXES`. The recommendations themselves are correct and boundary-compliant; the operational wiring required to enforce them at runtime is incomplete. This plan implements the actionable items.

## 2 · Items in Scope

| # | Gap ID | Severity | Action | File(s) |
|---|---|---|---|---|
| 1 | F-2 | low | Remove stale `.bak` file | `agentic_core/L5_safety/reasoning/core_kernel/classification_kernel.py.bak` |
| 2 | F-4 | medium | Document llm_judge vs llm_judges split | `agentic_core/evaluation/judges/__init__.py` |
| 3 | F-5 | **critical** | Make Qwen prefer-when-registered default; preserve explicit-override semantics | `agentic_core/evaluation/judges/provider_registry.py::create_default_registry` |
| 4 | F-3 | high | Add 10 missing LLM rubrics for runtime / Exit / G-gate Hybrid+Judge surfaces | `agentic_core/evaluation/judges/rubrics.json` |
| 5 | P-1 | high | Add Qwen vLLM judge backend (OpenAI-compatible) for Exit-eval | `agentic_core/L3_orchestration/exit_eval/judges/qwen_judge.py` (new) + `__init__.py` export |
| 6 | P-2 | high | Add Qwen vLLM backend for eval-spine trace_grader | `agentic_core/L5_safety/eval_spine/judge_backends/qwen_vllm.py` (new) + `__init__.py` export |
| 7 | P-4 | high | Wire env-gated Qwen as default backend pattern (mirrors AnthropicBackend stub shape) — same env var convention across both backends | covered by item 6's `qwen_vllm.py` activating on `VLLM_BASE_URL` |

## 3 · Items NOT in Scope

- Hybrid trigger doc tightening for parent audit rows #61/#63/#66/#104 — `docs/reports/` is `.codeiumignore`-blocked for Cursor Agent native edits; would also force re-issuing the parent audit. Tracked as documentation backlog, not enforceable through this plan.
- ADG fan-in trace for `g22_output_quality.py` upstream scorer (`P-3`) — discovery only, not actionable code change.
- L1 semantic judge abstain → HITL wiring (`P-5`) — separate per-module audit needed first.
- `mixture_of_experts.py` / `ensemble_router.py` naming-vs-logic confirmation (`P-6`) — read-only, no code change.
- `_history_summarizer_llm.py` role classification (`P-8`) — read-only, no code change.
- Two large L5/reasoning files deeper-read (`F-6`) — read-only.
- `config/judges/trace_rubric.yaml` content inspection (`F-1`) — separate read-only pass.

## 4 · Hard Constraints

- **Additive only.** No deletion of existing classes, no signature changes to `JudgeProvider` / `JudgeBackend` / `BaseHttpJudge` / `JudgeProtocol` / `DimScorer`.
- **No layer-gravity violations.** New files at `L3_orchestration/exit_eval/judges/` and `L5_safety/eval_spine/judge_backends/` import only from same-layer / lower-layer packages.
- **No anti-pattern introduction.** Use precise exception types; subprocess timeouts not relevant (no subprocess calls); no PowerShell.
- **Boundary compliance.** All new files honor: L0 RouteContract is deterministic, L3 only orchestrates managed_workflow, L2 bounded packets only, runtime gates emit GateVerdict only, Exit emits one X3 disposition, UWG is sole durable write path, L6 cannot mutate. New files are JUDGE backends — they recommend, never commit, never write L4 state.
- **Existing API preservation.** `provider_registry.py::create_default_registry` keeps existing positional / keyword arguments. Behavior change is gated behind a NEW kwarg `prefer_local: bool = True` — callers that explicitly pass `prefer_local=False` get the old Gemini-defaults-on-API-key behavior.

## 5 · Wave + Phase Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.1 | Repo hygiene (delete .bak, doc clarification) | ~3k | `.bak` is unreferenced; docstring change is comment-only | pending | `.bak` gone; docstring explicit about split |
| W2 | W2.1 | Rubric additions to `rubrics.json` | ~12k | JSON schema supports new entries without code change | pending | 10 new LLM rubrics present; existing rubrics untouched; `_meta.last_updated` bumped |
| W3 | W3.1, W3.2 | Qwen backend authoring (Exit-eval + eval-spine) | ~10k | OpenAI-compatible vLLM API at `VLLM_BASE_URL`; existing `BaseHttpJudge` and `DimScorer` contracts hold | pending | Two new files compile; `__init__.py` exports updated; default registration keys off `VLLM_BASE_URL` |
| W4 | W4.1 | provider_registry.py default-flip behind opt-in flag | ~6k | `JUDGE_PROVIDER` explicit override still wins; new `prefer_local` flag default True flips Gemini→Qwen ordering when both registered | pending | Qwen wins when `VLLM_BASE_URL` set AND `JUDGE_PROVIDER` empty; Gemini still default when only Gemini key present (no Qwen registered); explicit `JUDGE_PROVIDER=gemini` still wins |
| W5 | W5.1 | Verification — all files importable, rubrics.json validates as JSON, registry behavior preserved | ~5k | `python -c "import agentic_core.X"` succeeds for each new module | pending | All new files import cleanly; `json.load(rubrics.json)` succeeds; no syntax errors |

## 6 · Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Hygiene | `core_kernel/classification_kernel.py.bak` (delete), `evaluation/judges/__init__.py` (docstring) | trivial | 3k | pending |
| W2.1 | rubrics.json additions | `rubrics.json` | 10 new rubrics; preserve existing ordering; valid JSON | 12k | pending |
| W3.1 | qwen_judge.py for exit_eval | `L3_orchestration/exit_eval/judges/qwen_judge.py` (new), `__init__.py` (export) | OpenAI-compat shape; vLLM endpoint env resolution | 6k | pending |
| W3.2 | qwen_vllm.py for eval_spine | `L5_safety/eval_spine/judge_backends/qwen_vllm.py` (new), `__init__.py` (export) | Mirror AnthropicBackend env-gated pattern; emit DimensionResult; respect dimension scale from rubric | 4k | pending |
| W4.1 | provider_registry default-flip | `evaluation/judges/provider_registry.py::create_default_registry` | preserve old behavior under opt-out; new kwarg `prefer_local` defaults True | 6k | pending |
| W5.1 | Verification | all touched files | none | 5k | pending |

## 7 · Boundary Compliance Verification

| Invariant | This plan's risk surface | Mitigation |
|---|---|---|
| L0 emits one deterministic RouteContract | None — plan does not touch L0_routing | n/a |
| L3 orchestrates only managed_workflow | New `L3/exit_eval/judges/qwen_judge.py` is a judge backend invoked from within Exit pipeline (already managed_workflow path) | New file imports only from same-layer `_base_http_judge`, `graders/base`, `dimension`, `judges/prompt_templates`. No new orchestration entry point |
| L2 executes bounded packets only | None — plan does not touch L2_execution | n/a |
| Runtime Gates emit GateVerdict only | None — plan does not touch L5_safety/runtime_gates | n/a |
| Exit emits one X3 disposition | New `qwen_judge.py` is a judge backend; X3 disposition still owned by `exit_controller.py` | New file extends `BaseHttpJudge` which returns `JudgeResponse` (not X3 disposition); no override of `exit_controller` |
| UWG sole durable write path | None — plan does not touch L4_state/uwg | n/a |
| L6 cannot mutate or rescue | None — plan does not touch L6_observability | n/a |

## 8 · Anti-Pattern Avoidance

- No `bare except`, no `except Exception` without guardian comment.
- No `subprocess` calls (judge backends use `urllib` per existing `BaseHttpJudge`).
- No PowerShell.
- No new agents, no new orchestrators, no new sovereign wrappers.
- New files are pure functional — they implement an existing protocol (`JudgeProtocol` for exit_eval, `DimScorer` for eval_spine).

## 9 · Verification Steps

1. `python -c "import agentic_core.L3_orchestration.exit_eval.judges"` → no ImportError.
2. `python -c "import agentic_core.L5_safety.eval_spine.judge_backends"` → no ImportError.
3. `python -c "import json; json.load(open('agentic_core/evaluation/judges/rubrics.json'))"` → no JSONDecodeError.
4. `python -c "from agentic_core.evaluation.judges.provider_registry import create_default_registry; r = create_default_registry(); print(r.summary())"` → registry builds without error.
5. Optional: `git status` shows expected file set (1 deletion, 4 modifications, 2 additions).

## 10 · Rollback

Trivial rollback: `git restore agentic_core/evaluation/judges/{__init__.py,provider_registry.py,rubrics.json}` + `rm agentic_core/L3_orchestration/exit_eval/judges/qwen_judge.py agentic_core/L5_safety/eval_spine/judge_backends/qwen_vllm.py` + `git restore agentic_core/L3_orchestration/exit_eval/judges/__init__.py agentic_core/L5_safety/eval_spine/judge_backends/__init__.py`. No state migration, no schema migration, no data loss path.

## 11 · Dependencies

- Plan `qwen-adoption-waves-a7f3c2` (Wave A introduced `qwen_judge_provider.py`); this plan extends that pattern to two more surfaces.
- Existing `BaseHttpJudge` contract at `L3_orchestration/exit_eval/judges/_base_http_judge.py`.
- Existing `DimScorer` / `DimensionResult` contracts at `L5_safety/eval_spine/trace_grader.py`.
- Existing `JudgeProvider` protocol at `evaluation/judges/types.py`.
- vLLM endpoint exposing OpenAI-compatible `/v1/chat/completions` at `VLLM_BASE_URL` env var.

## 12 · Supersedes / Superseded-By

- Supersedes: none
- Superseded-by: none
- Closes (operationally): gap-closure audit items F-2, F-3, F-4, F-5, P-1, P-2, P-4

---

**End of plan.** Ready for execution.
