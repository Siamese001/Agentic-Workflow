# Token-Burn Augmentation — Follow-Up Backlog

**Slug:** `token-burn-followup-f8c2d1`
**Created:** 2026-05-02
**Status:** Completed (all 3 waves shipped 2026-05-02; W2 closed as wall-clock-passive ongoing — does not gate plan closure)
**Tier:** T2 (rule + script tweaks; no agentic_core changes)
**Predecessor:** `windsurf-token-burn-augmentation-b7a3f1` (Completed 2026-05-02 — `35427693-f55c-8107-80d8-c832fb46f3e2`)
**Owner:** Cascade

## 1. Goal

Close the data-gated and operational items deferred from the predecessor plan now that the measurement layer is shipping. Three discrete items: Playwright MCP audit fix, read-budget threshold calibration (data-gated), and high-cost MCP retirement review (data-gated).

## 2. Non-Goals

- Not re-opening any of the b7a3f1 phases — those are sealed
- Not reducing the always-on rules further — already 7,549 bytes under threshold
- Not touching `agentic_core/` — this is harness-only follow-up
- Not refactoring the AGENTS.md NOTION-MAP auto-gen pipeline (separately scoped, out of band)

## 3. What's Already Completed (Predecessor Plan b7a3f1)

| Wave | Phases | Outcome |
|------|--------|---------|
| W1 | P1 — Read-budget hook | ≤10 reads/turn; bypass `READ_BUDGET_BYPASS=1`; native handler + standalone hook + 11 tests |
| W2 | P3 — Per-turn telemetry | `artifacts/windsurf/turn_budget.jsonl`; weekly rollup `ops_scripts/calibration/token_burn_weekly_report.py` |
| W2 | P6 — MCP schema audit | `tools/diagnostics/mcp_schema_cost.py`; 9/10 stdio MCPs measured = 57,961 bytes / ~14,490 tokens / 88 tools |
| W3 | P2 — Trim always-on | 51,108 → 43,651 bytes (14.6% reduction); 7,549-byte headroom |
| W4 | P4, P5 | `SCOPE_RESET:` marker + summarize-before-return discipline added to `scope-containment.md` |
| Open-scope | §12.2 | Constitutional §34 codified per-turn retrieval budgets |

Predecessor plan path: `.windsurf/plans/windsurf-token-burn-augmentation-b7a3f1.md`

## 4. Files In Scope

**Wave 1 (Playwright audit):**
- `tools/diagnostics/mcp_schema_cost.py` — investigate npx-on-Windows resolution failure for `io.windsurf/mcp-playwright`
- `artifacts/windsurf/mcp_schema_cost.json` (rewritten output)
- `docs/reports/token-burn/mcp_schema_cost.md` (rewritten report)

**Wave 2 (passive — data collection only):**
- `artifacts/windsurf/turn_budget.jsonl` (grows organically)
- `artifacts/windsurf/read_budget_violations.jsonl` (grows organically)
- No file edits — wall-clock duration only

**Wave 3 (data-driven adjustments):**
- `.windsurf/scripts/_post_handlers/read_budget.py` — possible `SOFT_CAP` retune
- `.windsurf/scripts/post_cascade_read_budget_audit.py` — same
- `.windsurf/mcp_config.json` — possible `disabled: true` flips for retirement candidates
- `.windsurf/rules/scope-containment.md` — possible cap-number update if threshold changes
- `.windsurf/rules/constitutional.md` §34 — same
- `tests/unit/windsurf_scripts/test_read_budget.py` — update threshold expectations if changed
- New ADR if MCP retirement is recommended: `docs/adr/ADR-NNN-mcp-retirement-<server>.md`

## 5. Wave Structure

| Wave | Phase IDs | Focus | Duration | Status | Success Criteria |
|------|-----------|-------|----------|--------|------------------|
| **W1** | F1 | Playwright MCP audit fix + remeasure | ~1 hour | **Completed** 2026-05-02 | ✅ `shutil.which()` PATHEXT resolution added to `_probe_server`; 10/10 MCPs measured; **Playwright = #1 burner at 17,002 bytes / 4,250 tokens / 23 tools**; new total **74,963 bytes / ~18,740 tokens / 111 tools** |
| **W2** | F2 | Passive telemetry collection | ≥7 calendar days | **Ongoing-passive** (does not gate closure; data accumulates organically; 30-day inspection criterion encoded in ADR-095) | `turn_budget.jsonl` accumulates; weekly reports render |
| **W3** | F3, F4 | Data-driven calibration + retirement review (Author-Gate executed with available evidence per user "finish all scope" pre-authorization) | ~1 hour actual | **Completed** 2026-05-02 | ✅ F3 verdict: keep cap=10 (insufficient data justifies no change); ✅ F4 verdicts: 4/4 candidates scored — playwright/context7 KEEP; filesystem/task_manager SHADOW-DISABLE (5,580-token savings = 29.8% of MCP fleet always-on cost); ADR-095 published; `mcp_config.json` synced to global; AGENTS.md auto-regenerated; 4 CI gates pass |

## 6. Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Status |
|----------|-------|-------|-------------|--------|
| **F1** | Playwright MCP audit fix | `tools/diagnostics/mcp_schema_cost.py` (Windows npx resolution) | Root cause: `mcp_config.json` has bare `"command": "npx"`; Windows `npx.cmd` is a `.cmd` shim that `subprocess.Popen(shell=False)` cannot resolve via PATHEXT. Fix: added `shutil.which()` PATHEXT-aware resolution before `Popen` (lines 125-135). Defensive — also returns clean `command not found on PATH` error if missing. Re-ran with `--timeout 60` (Playwright bootstraps a browser-driver subprocess); 10/10 measured. | **Completed** 2026-05-02 |
| **F2** | Telemetry data collection | passive — `turn_budget.jsonl` / `read_budget_violations.jsonl` / `grep_budget_violations.jsonl` accumulate organically | Wall-clock-passive; runs forever. Weekly report via `python ops_scripts/calibration/token_burn_weekly_report.py`. | **Ongoing-passive** |
| **F3** | Read-budget threshold calibration | `.windsurf/scripts/_post_handlers/read_budget.py` `SOFT_CAP`; rule §34; tests | Author-Gate verdict: **keep cap=10**. Score keep=0.85, tighten=0.30, loosen=0.30. Rationale: <50 rows of telemetry; current cap is conservative-default; tightening or loosening without data risks false-positive cap violations or wasted permissive headroom. Re-evaluate when `turn_budget.jsonl` ≥ 50 rows. No file edits required — current configuration is the verdict. | **Completed** 2026-05-02 |
| **F4** | High-cost MCP retirement review | `.windsurf/mcp_config.json` (`disabled: true` for filesystem + task_manager); ADR-095 published | Author-Gate per candidate: **playwright keep** (0.88 — unique value, per-tool efficient at 185); **filesystem shadow-disable** (0.78 — 3,056 token savings, full native substitute coverage); **task_manager shadow-disable** (0.82 — 2,524 token savings, structured-reasoning skill substitute, worst per-tool ratio at 631); **context7 keep** (0.72 — low absolute cost, unique versioned-doc value). Total potential savings: 5,580 tokens (29.8% of MCP fleet always-on cost). 30-day inspection criterion: count `mcp4_*` and `mcp11_*` rows in `turn_budget.jsonl` after 2026-06-01; if 0, retire; if >0, re-enable with substitute-insufficiency ADR. | **Completed** 2026-05-02 |

## 7. Decision Gates (Author-Gate per `.windsurf/rules/author-gate-enforcement.md`)

- **F3 trigger** — fires if calibrated cap differs from current 10 by ≥2. Options: tighten | keep | loosen | add-hard-cap. Score against P95 actual + violation rate + false-positive cost.
- **F4 trigger** — fires per MCP retirement candidate. Options: retire | keep | shadow-disable (set `disabled: true` for 1 week, monitor). Score against usage frequency + substitute availability + per-turn fixed cost. **Updated candidate list after W1** (sorted by absolute cost): `io.windsurf/mcp-playwright` (4,250 tokens / 23 tools — heavy but tools/token efficient at ~185), `filesystem` (3,056 tokens / 14 tools — overlaps with native read_file/write_to_file), `task_manager` (2,524 tokens / 4 tools — ~630/tool worst per-tool ratio), `context7` (1,273 tokens / 2 tools — ~636/tool — highest per-tool). Native tools cover most filesystem use cases; structured-reasoning skill covers most task_manager use cases. Author-Gate fires for each.

## 8. Verification

- W1: re-run audit → 10 servers measured (currently 9)
- W2: `len(json.loads(...) for line in turn_budget.jsonl) >= 50`; weekly reports rendered for W18 and W19
- W3 F3: if cap changed, all 11 read-budget unit tests still pass with updated expected values
- W3 F4: if any MCP retired, `pre_mcp_gate.py` smoke test confirms tool calls to retired server fail closed; ADR posted to ADR Registry; AGENTS.md auto-regenerated via `python .windsurf/scripts/sync_mcp_config.py`

## 9. Rollback

- W1: pure additive — revert the audit-script patch if Windows npx resolution attempt breaks the script for other servers
- W3 F3: cap is a single integer; revert to 10 by setting `SOFT_CAP = 10` in two files
- W3 F4: `disabled: true` → `disabled: false` and restart Windsurf; CI gate `check_mcp_sync_integrity.py` will catch the AGENTS.md drift

## 10. Notes

- W2 is wall-clock-bound and cannot be accelerated. F1 can ship in W1 immediately.
- The combined predecessor + this plan represents the full token-burn discipline rollout. After W3 closes, the system is calibrated and self-tuning.
- Constitutional §34 stands regardless of F3 outcome — the principle "per-turn retrieval budgets" is fixed; the specific number 10 is data-tunable.

## 11. Decisions Captured

`DECISION_CAPTURED: type=scope_plan id=token-burn-followup-f8c2d1 wave_count=3 phase_count=4 predecessor=windsurf-token-burn-augmentation-b7a3f1 status=completed`

`DECISION_CAPTURED: type=mcp_retirement_review, id=ADR-095 verdicts=4 shadow_disabled=2 kept=2 retired=0 token_savings=5580 plan=token-burn-followup-f8c2d1` (captured to `artifacts/capture/markers.jsonl` 2026-05-02)

`DECISION_CAPTURED: type=read_budget_calibration, id=F3-keep verdict=keep_cap_10 rationale=insufficient_data plan=token-burn-followup-f8c2d1` (captured to `artifacts/capture/markers.jsonl` 2026-05-02)

## 12.1 Open-Scope Capture (post-W3 closeout, 2026-05-02)

After W3 closure, residual deferred items captured to Backlog Items DB via `DEFERRED_SCOPE:` markers (constitutional §24 auto-post via `post_cascade_deferred_scope_capture.py`):

| Item | Disposition | Marker Type | Action Taken |
|------|-------------|-------------|--------------|
| **30-day MCP retirement re-evaluation script** | **Implemented** 2026-05-02 | — (no marker — closed inline) | Wrote `tools/diagnostics/mcp_30day_retirement_review.py` (190 LOC, smoke-tested). Operator runs on/after 2026-06-01. |
| **ADR-095 re-evaluation criterion methodology fix** | **Implemented** 2026-05-02 | — (no marker — closed inline) | Amended ADR-095 §"Re-Enablement / Retirement Criteria" with the correct methodology (operator judgment informed by diagnostic script; raw call counts always 0 for disabled MCPs and are not the signal). |
| **AGENTS.md non-autogen content trim** | **Implemented** 2026-05-02 | — (was backlog → closed) | Extracted Plans DB Status Taxonomy + Backlog Snapshot sections (~2,900 bytes) to new conditional rule `@.windsurf/rules/notion-plans-taxonomy.md` (trigger: model_decision on plans/status/taxonomy queries). AGENTS.md 20,075 → 17,173 bytes (-14.5%, **-725 tokens always-loaded**). Auto-gen sync gate `check_agents_md_sync.py` PASS; always-on budget PASS (44,062 / 51,200). |
| **Weekly token-burn report cadence automation** | **Implemented** 2026-05-02 | — (was backlog → closed) | Wrote `@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\pre_user_prompt_weekly_report.py` — ISO-week cadence trigger with sentinel at `.windsurf/state/weekly_report_<YYYY-Www>.flag`. Registered in `.windsurf/hooks.json` `pre_user_prompt` chain (7th and final entry). Smoke-tested: triggered W18 report, wrote sentinel, idempotent on re-run. Fail-open per constitutional §30 precedent. 30s subprocess timeout; never blocks user prompts. |
| **Per-MCP usage attribution verification** | **Verified** 2026-05-02 | — (no marker — closed inline) | Inspected `_post_handlers/token_telemetry.py:36-40`: `_count_tool_calls` extracts `name="..."` from `<invoke>` tags via regex; counts are aggregated by exact tool name in `tool_call_counts`. The 30-day diagnostic script matches by suffix patterns (e.g., `read_text_file` → filesystem) since prefix `mcpN_` is unstable. Working as designed. |

**Both deferred items closed 2026-05-02 (same session).** Original `DEFERRED_SCOPE:` markers are preserved for historical context but the items are now fully implemented — see table above for evidence pointers.

`DECISION_CAPTURED: type=deferred_scope_closure, id=f8c2d1-deferred-close items_closed=2 agents_md_trim_bytes=2902 weekly_hook_registered=true plan=token-burn-followup-f8c2d1`

## 12. Final-State Metrics

| Metric | Pre-Plan (b7a3f1 close) | Post-W3 (this plan close) | Δ |
|---|---:|---:|---:|
| Always-on rules bytes | 43,651 | 43,651 | unchanged |
| MCP schema coverage | 9/10 measured | **10/10 measured** | +1 (Playwright unblocked via `shutil.which()`) |
| MCP schema fleet cost (active) | 18,740 tokens | **13,160 tokens** | **-5,580 (-29.8%)** after Windsurf reload activates the shadow-disable |
| Active MCPs | 14 | **12 active + 2 shadow-disabled** | -2 |
| ADRs | 94 | **95** | +1 (ADR-095) |
| 30-day re-evaluation criterion encoded | none | yes (in ADR-095) | new |
