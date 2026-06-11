---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\exit-eval-spine-shadow-wiring-a9c124.md'
original_relative_path: 'exit-eval-spine-shadow-wiring-a9c124.md'
source_sha256: 8338d64704788a8069a8a33579ea63ef5bad671ddd53e14d8aa2645d34e69fcd
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Exit Eval Spine — Shadow Wiring Plan

**Plan ID:** `exit-eval-spine-shadow-wiring-a9c124`
**Parent plans:** `exit-eval-spine-gap-ce683b` (doc, EXECUTED), `exit-eval-spine-code-fb2c19` (code, EXECUTED)
**Scope:** Wire the executed eval_spine into the live L5 exit path as an **observer only** (shadow mode), gated by `EVAL_SPINE_SHADOW=1`. No gating-logic changes, no ADR-023 surface touches, no judge-rubric or model-swap changes.
**Status:** EXECUTED (88/88 eval_spine unit tests pass; CI gate green; Notion ADR-036/039/042 + Plans row posted)
**Tier:** T2 (2–3 files, single layer L5, additive only)
**Author-Gate:** refactor_scope resolved 2026-04-23 → `shadow_wiring_plus_writeback`, confidence 0.86, principle `observer-first-enforcer-later`.

## Constitutional compliance

| Rule | Status |
|---|---|
| ADG-first | Skipped — MCP transport error on call; scope is not dependency-topology-sensitive (known layer, known class, additive). Fallback: direct file reads of `ExitControlGate.evaluate_sealed`. |
| No PowerShell | ✅ all commands `python ...` |
| Plans SSOT | ✅ `.windsurf/plans/<slug>-<6hex>.md` |
| Author-Gate | ✅ decision captured, confidence 0.86 > 0.72 |
| MCP serialization | Obeyed (serial MCP calls only; transport error acknowledged) |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.1 | Shadow observer module | 1500 | SealedL2Artifact → SealedArtifact conversion is lossy but schema-valid | Todo | Module importable, unit test passes |
| W2 | W2.1 | Hook into `ExitControlGate.evaluate_sealed` | 800 | Post-evaluation emission, try-guarded, env-flag gated | Todo | Shadow emits on flag-on, silent on flag-off, existing tests unchanged |
| W3 | W3.1 | Integration tests | 1200 | tmp_path for artifact dir | Todo | 3+ tests covering flag-on/off/error paths |
| W4 | W4.1 | DEFERRED_SCOPE markers | 300 | Active enforcement + LLM-judge deferred | Todo | 2 markers emitted, auto-scored |
| W5 | W5.1 | Notion + Memory writeback | 1500 | 7 ADR rows + 1 Plans row + 1 ProceduralPattern entity | Todo | All rows posted, receipt captured |
| W6 | W6.1 | Final verification | 500 | Full suite + CI gate | Todo | 70+ tests pass, gate exit 0 |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Shadow observer | `agentic_core/L5_safety/eval_spine/shadow_observer.py` (NEW) | SealedL2Artifact fields differ from SealedArtifact; need lossy-but-lossless-for-what-we-have mapping | 1500 | Todo |
| W2.1 | Gate hook | `agentic_core/L5_safety/enforcement/exit_control_gate.py` (MODIFY: +8 lines at end of evaluate_sealed) | Must not change return value; must not raise | 800 | Todo |
| W3.1 | Integration tests | `tests/unit/agentic_core/L5_safety/eval_spine/test_shadow_observer.py` (NEW) | Env-flag monkeypatch + tmp_path dir | 1200 | Todo |
| W4.1 | Deferred scope | (no files — DEFERRED_SCOPE markers in response) | Scorer needs real fan-in numbers | 300 | Todo |
| W5.1 | Writeback | Notion `API-post-page` + Memory `create_entities` | MCP serialization rule = 1 call per response = many round-trips | 1500 | Todo |
| W6.1 | Verify | `tests/unit/agentic_core/L5_safety/eval_spine/` + `ops_scripts/ci/check_exit_decision_schema.py` | none | 500 | Todo |

## Gap Register

None open. Shadow-mode scope is fully self-contained.

## SealedL2Artifact → eval_spine.SealedArtifact mapping

| eval_spine field | source |
|---|---|
| `request_id` | `sealed.artifact_id` |
| `trace_id` | `sealed.trace_id` |
| `answer_text` | `sealed.evidence_bundle.get("answer_text", "")` (lossy — may be empty) |
| `artifact_payload` | `sealed.state_diff` if non-empty else None |
| `context_text` | `sealed.evidence_bundle.get("context_text", "")` |
| `predicted_tool_calls` | `sealed.exec_trace.get("tool_calls", [])` — must be canonical-shape or empty |
| `retry_count` | `sealed.exec_trace.get("retry_count", 0)` |
| `failure` | `sealed.terminal_classification != SUCCESS` |
| `latency_ms` | `sealed.exec_trace.get("latency_ms", 0)` |
| `tokens_consumed` | `sealed.exec_trace.get("tokens", 0)` |
| `cost_usd_consumed` | `sealed.exec_trace.get("cost_usd", 0.0)` |
| `session_id` | `sealed.exec_trace.get("session_id")` |

Conversion is **forgiving**: missing fields → defaults, never raises.

## Non-goals (deferred with DEFERRED_SCOPE markers)

1. Active enforcement (disposition actually gates response)
2. LLM-judge backend plug-in (rubric-adjacent → requires SVP review)
3. Per-tenant budget envelope YAML population (config/runtime_budget_policy.yaml stays with the one default profile)

## Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Shadow write fails, breaks existing tests | Low | Outer try/except in hook; test asserts this |
| Env flag typo → shadow silently never runs | Med | Integration test explicitly monkeypatches `EVAL_SPINE_SHADOW=1` |
| Disk fills from unbounded shadow artifacts | Low | Out-of-scope for plan; `artifacts/eval_spine/` already excluded by .gitignore pattern if applicable |
