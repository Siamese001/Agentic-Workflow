---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\exit-eval-spine-deferred-closeout-d5e8b3.md'
original_relative_path: 'exit-eval-spine-deferred-closeout-d5e8b3.md'
source_sha256: 97c74ae16d876bc65220e032906666501417e591f30a48719944c565a611b8ef
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Exit Eval Spine — Deferred Scope Closeout

**Plan ID:** `exit-eval-spine-deferred-closeout-d5e8b3`
**Parent plans:** `-gap-ce683b` (EXECUTED), `-code-fb2c19` (EXECUTED), `-shadow-wiring-a9c124` (EXECUTED)
**Scope:** Close out the 4 deferred items from the shadow-wiring plan.
**Status:** EXECUTED (128/128 eval_spine tests pass; CI gate green; 7 Notion ADR rows + 2 Plans rows + 1 Memory entity persisted)
**Tier:** T2 (≤5 files per wave, single layer per wave, additive)
**Author-Gate:** User directive 2026-04-23 — "create plan add to notion and implement and mark complete in notion". Explicitly overrides parent `-ce683b` §6 non-touch constraint on active enforcement + judge-backend seam.

## Deferred items being closed

| # | Item | Status at start | Approach |
|---|---|---|---|
| 1 | ADR-037 / 038 / 040 / 041 markdown files | Authored on disk (verified 2026-04-23); not in Notion | Post 4 rows to Notion ADR Registry |
| 2 | LLM-judge backend plugin scaffold | Not present | New `eval_spine/judge_backends/` with `JudgeBackend` callable type + `NullBackend` + `AnthropicBackend` env-gated stub |
| 3 | Active §5 enforcement | Not present | New env flag `EVAL_SPINE_ENFORCE=1` makes `ExitControlGate.evaluate_sealed` honor eval_spine `ExitDecision.disposition` |
| 4 | Memory MCP writeback (`ProceduralPattern:EvalSpineShadowWiring`) | MCP dead at 22:58 UTC | Retry server; fall back to direct SQLite write on `artifacts/memory/knowledge_graph.sqlite` |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| Q1 | Q1.1 | Plan file + Notion Plans row | 600 | Todo | Plans row exists with Plan File Path |
| Q2 | Q2.1 | Post 4 ADR rows to Notion (037, 038-budget, 040, 041) | 1200 | Todo | 4 ADR Registry rows created |
| Q3 | Q3.1 | LLM-judge backend plugin package | 1500 | Todo | Module importable + NullBackend tested + AnthropicBackend stub tested |
| Q4 | Q4.1 | Active §5 enforcement hook | 1000 | Todo | `EVAL_SPINE_ENFORCE=1` maps eval_spine disposition→ExitDisposition, covered by tests |
| Q5 | Q5.1 | Memory MCP writeback | 400 | Todo | Entity persisted (MCP or SQLite fallback) |
| Q6 | Q6.1 | Full test run + CI gate | 400 | Todo | 90+ eval_spine tests pass, no neighbor regression |
| Q7 | Q7.1 | Flip Notion rows to Complete | 500 | Todo | Plans row status=Complete, 7 ADR rows status=Accepted |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Est. Tokens | Status |
|---|---|---|---|---|
| Q1.1 | Plan file + Plans row | `.windsurf/plans/exit-eval-spine-deferred-closeout-d5e8b3.md`, Notion Plans DB | 600 | Todo |
| Q2.1 | ADR backfill to Notion | ADR Registry DB (4 rows) | 1200 | Todo |
| Q3.1 | Judge backend plugin | `agentic_core/L5_safety/eval_spine/judge_backends/{__init__,base,null,anthropic_stub}.py` (NEW), `tests/.../test_judge_backends.py` (NEW) | 1500 | Todo |
| Q4.1 | Active enforcement | `agentic_core/L5_safety/eval_spine/enforcement_bridge.py` (NEW), `agentic_core/L5_safety/enforcement/exit_control_gate.py` (MODIFY +15 lines after shadow hook), tests added | 1000 | Todo |
| Q5.1 | Memory writeback | Memory MCP OR direct SQLite fallback | 400 | Todo |
| Q6.1 | Verify | pytest + CI gate | 400 | Todo |
| Q7.1 | Complete Notion | 8 Notion patch calls | 500 | Todo |

## Key Architectural Decisions

### Judge backend plugin (Q3)
- **Interface**: `JudgeBackend = Callable[[GraderInput, DimSpec], DimensionResult]` — already the `DimScorer` shape from `trace_grader.py`
- **NullBackend**: returns `score="Unknown"` for every dim — existing default behavior, now explicit
- **AnthropicBackend stub**: checks `ANTHROPIC_API_KEY`; if absent → behaves as Null; if present → raises `NotImplementedError("real scoring not wired in this plan; track via DEFERRED_SCOPE")`
- **No rubric weights touched**. The seam is structural only, respecting parent §6 with user-authorized overlay.

### Active §5 enforcement (Q4)
- Adds `EVAL_SPINE_ENFORCE=1` env flag (distinct from `EVAL_SPINE_SHADOW=1` which stays shadow-only)
- When set: `ExitControlGate.evaluate_sealed` builds the legacy `CurrentRunEvaluationResult`, then runs `evaluate_exit(artifact, envelope, policy)`, and **if eval_spine returns a stricter disposition**, the legacy result's disposition is upgraded (never downgraded)
- Upgrade precedence: `policy_halt > escalate_hitl > deny_reroute > allow_finish`
- **Safety bias**: enforcement never loosens; always fail-closed towards escalation
- Default off (flag unset) preserves zero behavior change

### Memory writeback (Q5)
- Primary: retry `mcp5_memory_health`; if healthy, `create_entities`
- Fallback: write directly to `artifacts/memory/knowledge_graph.sqlite` via stdlib `sqlite3` using the same entity/observation shape

## Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Active enforcement changes production disposition unexpectedly | Low (gated by flag, default off) | Upgrade-only precedence, unit tests pin every transition |
| Judge backend stub accidentally makes an Anthropic API call | Very Low | `NotImplementedError` path deliberately raises rather than calling; test verifies |
| Memory SQLite schema drift | Low | Match existing `knowledge_graph.sqlite` schema; idempotent INSERT OR IGNORE |
| Notion status-flip fails partially | Low | Run as 8 independent patches; log which succeeded |

## Success Criteria (plan-level)

- All 4 deferred items closed (code + writeback)
- `pytest tests/unit/agentic_core/L5_safety/eval_spine/` green
- CI gate `check_exit_decision_schema.py` exit 0
- 1 Plans row + 7 ADR Registry rows marked Complete/Accepted in Notion
- No change to ExitControlGate default behavior (both new flags off by default)
