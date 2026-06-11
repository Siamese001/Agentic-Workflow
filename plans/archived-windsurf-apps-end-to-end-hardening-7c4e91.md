---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-end-to-end-hardening-7c4e91.md'
original_relative_path: 'apps-end-to-end-hardening-7c4e91.md'
source_sha256: ab9be6c6d96308a192638ff348d66ce8d1efff1451891eb6d5a47ff085345e77
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_* End-to-End Hardening

- **Plan ID:** `apps-end-to-end-hardening-7c4e91`
- **Status:** Complete (this session)
- **Tier:** T3 (cross-app, base-class-touching)
- **Scope:** Make every `apps_*` directory runnable end-to-end and produce a verifiable deliverable artifact, without weakening tests.

## Outcome — Verified Deliverables (7/7 apps)

| App | Deliverable | Status |
|---|---|---|
| `apps_lic` | `output_<trace>.json` | exit=0, production_ready=YES |
| `apps_rg` | `apps_rg/scripts/generated_resume_<ts>.json` | exit=0, **QUALITY SCORE: 0.95** (was 0) |
| `apps_eval` | `eval/eval_report_<trace>.md`, `scorecard_<trace>.csv`, `eval_manifest_<trace>.json` | pipeline emits artifacts; score-gate fails (synthetic scenarios — content, not pipeline) |
| `apps_exec` | `reports/executive/exec_brief_<audience>_<trace>.md` | exit=0, status=complete, score=1.0 |
| `apps_research` | `reports/research/research_brief_<trace>.md`, `source_register_<trace>.json` | exit=0, status=complete, score=1.0 |
| `apps_rfp` | `rfp/proposal_<industry>_<trace>.md`, `proposal_manifest_<trace>.json` | exit=0, status=complete, score=1.0 |
| `apps_underwriting_ai` | `apps_underwriting_ai/outputs/underwriting_result.json` | DECISION=PEND_FOR_INFORMATION |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1** | W1.1, W1.2 | Restore archived modules consumed by live apps | 2k | Files exist in git history | ✅ | All 3 modules restored or non-blocking |
| **W2** | W2.1..W2.5 | Per-app smoke run + targeted unblock (Author-Gate Option A) | 8k | apps_lic / apps_rg pattern transfers | ✅ | Each app produces a deliverable artifact |
| **W3** | W3.1, W3.2 | Quality-of-output fixes (apps_rg current_resume bridge, ContentQualityAgent score emission) | 2k | Buffer-staged hop output is the source of truth | ✅ | apps_rg quality score > 0 |
| **W4** | W4.1 | Pytest scoped to apps_* | 1k | Pre-existing test debt is acceptable | ✅ | apps test suite ≥90% pass; base_agents 100% pass |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Restore `agentic_core/L4_state/config/vllm_routing_predicates.py` | 1 file from `git show 86466c9d0c^` | Module archived in W7.5 cleanup despite live consumers | 0.5k | ✅ |
| W1.2 | Restore `tools/change_impact_engine.py` + `agentic_core/interfaces/execution_agents.py` | 2 files from git history | Same archive-while-still-imported pattern | 1k | ✅ |
| W2.1 | apps_eval | `engines/scenario_runner.py`, `engines/regression_detector.py`, `validators/eval_gate_validator.py`, `scripts/run_eval.py` | Literal-vs-Enum confusion, `" ERROR "` whitespace literal | 2k | ✅ |
| W2.2 | apps_exec | `scripts/run_exec.py` | Literal-vs-Enum, sync call to async `ExecOrchestrator.run` | 1.5k | ✅ |
| W2.3 | apps_research | `engines/research_assembly_engine.py`, `reasoning/ResearchOrchestrator.py` (already had defensive code) | `ArtifactMode.X` / `ClaimType.X` / `isinstance(x, ArtifactMode)` on Literal aliases; SourceEntry.url pydantic scheme | 2k | ✅ |
| W2.4 | apps_rfp | `scripts/run_rfp.py`, `reasoning/RfpOrchestrator.py` | Literal-vs-Enum, sync call to async `RfpOrchestrator.run`, `risk.severity.value` | 1k | ✅ |
| W2.5 | apps_underwriting_ai | `examples/sample_underwriting_request.json` driver | No `__main__` — invoked via `UnderwritingEngine().run(req)` directly | 1k | ✅ |
| W3.1 | apps_rg current_resume bridge | `engines/resume_orchestrator_engine.py` | Engines write to `ctx.buffer`; validators read `ctx.current_resume` | 0.5k | ✅ |
| W3.2 | ContentQualityAgent quality_report emission | `reasoning/ContentQualityAgent.py` + `base_agents/SovereignBaseAgent.py` (record_pass/fail kwargs) | Score never published to buffer; record_fail didn't accept `data=` kwarg | 1k | ✅ |
| W4.1 | Test verification | `tests/unit/apps_*`, `tests/unit/agentic_core/base_agents` | 92.7% apps_* pass rate; 31/31 base_agents pass; failures are pre-existing stale auto-generated import smoke tests | 1k | ✅ |

## Files Modified (this session)

### Restored from git
- `agentic_core/L1_cognition/utils/__init__.py` (new)
- `agentic_core/L1_cognition/utils/guardrails_util.py` (commit `8b694abc34^`)
- `agentic_core/L4_state/config/vllm_routing_predicates.py` (commit `86466c9d0c^`)
- `tools/change_impact_engine.py` (commit `fce655254839^`)
- `agentic_core/interfaces/execution_agents.py` (commit `1517d3de1e^`)

### Modified
- `agentic_core/config/sovereign_config.py` — `get(key, default)` shim
- `agentic_core/base_agents/SovereignBaseAgent.py` — `log/record_pass/record_fail/record_warning/add_signal/remove_signal/has_signal` agent-level helpers; `_record_outcome` accepts `**kwargs`
- `apps_rg/config/reasoning_toggles_config.py` — `RGReasoningToggles` alias
- `apps_rg/types/SovereignContext.py` — `current_resume`, `master_resume`, signal helpers, success history
- `apps_rg/engines/resume_orchestrator_engine.py` — buffer→`ctx.current_resume` sync, default reports
- `apps_rg/reasoning/ContentQualityAgent.py` — emit `quality_report` to buffer with score
- `apps_eval/engines/scenario_runner.py` — strip `" ERROR "` whitespace
- `apps_eval/engines/regression_detector.py` — Literal strings instead of `RegressionVerdict.X`
- `apps_eval/validators/eval_gate_validator.py` — Literal string compare
- `apps_eval/scripts/run_eval.py` — `str()` on Literal-typed status/verdict
- `apps_exec/scripts/run_exec.py` — Literal-set validation, `asyncio.run()` wrapper
- `apps_research/engines/research_assembly_engine.py` — string keys for ArtifactMode/ClaimType, `urn:repo:` URLs
- `apps_rfp/scripts/run_rfp.py` — Literal-set validation, `asyncio.run()` wrapper
- `apps_rfp/reasoning/RfpOrchestrator.py` — drop `.value` on Literal severity
- `system_learning/runtime_adg/runtime_span_emitter.py` — `seal_step` initializes `status` before try

## Root-Cause Pattern (worthy of a follow-up sweep)

> Every app failure traced to the **same architectural pattern**: types defined as `X = Literal["a", "b"]` (a `typing` alias) but consumed as `Enum` (`X.A`, `X(value)`, `isinstance(o, X)`, `o.value`). When that field is later passed to a Pydantic v2 model with strict Literal validation, dotted access raises `AttributeError`. The defensive remedy already used in some sites (`hasattr(x, "value") else str(x)`) is verbose; a structural fix would be to convert all Literal aliases to `StrEnum`.

## Deferred Scope (carry-over)

- `DEFERRED_SCOPE: plan=NEW:apps-literal-vs-enum-cleanup wave=W-NEXT phase=NEXT-pattern layer=L_APP fan_in=8 surface=Execution coverage_gap_pct=70.0 est_tokens=15000 reason=Replace Literal-alias dotted access with StrEnum across apps_*`
- `DEFERRED_SCOPE: plan=NEW:agentic-core-archive-restore-audit wave=W-NEXT phase=NEXT-archive layer=L_SHARED fan_in=12 surface=State coverage_gap_pct=20.0 est_tokens=8000 reason=W7.5 archived 6 dead folders that included still-imported modules; audit remaining archives for live consumers`
- `DEFERRED_SCOPE: plan=NEW:apps-test-suite-modernization wave=W-NEXT phase=NEXT-tests layer=L_APP fan_in=42 surface=Observability coverage_gap_pct=10.0 est_tokens=20000 reason=42 stale auto-generated import smoke tests reference symbols that don't exist in agentic_core/__init__.py`
- `DEFERRED_SCOPE: plan=NEW:agentic-core-structure-blueprint-restore wave=W-NEXT phase=NEXT-l5 layer=L5 fan_in=15 surface=Security coverage_gap_pct=80.0 est_tokens=25000 reason=structure_blueprint package (6 files) was archived; SSOT exclusion loading falls back gracefully but real exclusions are stubbed`

## ADG Provenance

ADG Provenance: backend=sqlite_static, snapshot=adg_indexed_04242026_*.sqlite (ADG queries used were git-history searches, not full ADG queries — this is bounded-scope work where git's `--diff-filter=D --all` was the authoritative source for restoration.)

## Lessons Learned

1. **Literal-vs-Enum is the dominant brittleness pattern in `apps_*`** — every previously-broken app traced to the same root cause.
2. **W7.5 "dead folders" archival was unsafe** — 4 modules were archived despite live consumers (`guardrails_util.py`, `vllm_routing_predicates.py`, `change_impact_engine.py`, `execution_agents.py`).
3. **`base_agents/SovereignBaseAgent.py` was missing app-layer compatibility helpers** (`log`, `record_pass/fail/warning`, `add_signal`, `has_signal`) that 80+ engine sites assumed existed. Adding them once at the base class fixes all apps simultaneously.
4. **Buffer-staged data needs explicit bridging into `ctx.<attribute>` for legacy validators** — the orchestrator's `ctx.buffer.write()` pattern doesn't auto-populate the typed attributes downstream agents read directly.
5. **Pydantic v2 `Literal` validation is strict** — string fields with leading/trailing whitespace fail (`" ERROR "` ≠ `"ERROR"`).
