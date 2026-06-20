---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\notion-wave-lifecycle-autosync-f4a2b8.md'
original_relative_path: '_archive\\2026-05\\notion-wave-lifecycle-autosync-f4a2b8.md'
source_sha256: 0747e40db06944d8c2a650f7a4764d1911f10fa0d609686d8e8c5a5eaf787cab
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: notion-wave-lifecycle-autosync-f4a2b8
status: Not Started
tier: T3
created: 2026-05-10
target: Eliminate Notion drift on plan/wave/phase status without depending on Cursor Agent discipline
---

# Notion Wave-Lifecycle Auto-Sync

## 1. Problem statement

Drift between the on-disk plan state (`.cursor/plans/*.md`, `wave_execution_state.py` state, phase completion) and the Notion Plans DB is recurring. The user has to remind Cursor Agent every session to update Notion. Constitutional §36 already enforces *plan registration* at wave-1 start, but **wave-by-wave progress, phase completion, and final plan status flip to Completed are not auto-synced**.

## 2. Defense of the recommendation

> **Recommendation**: route all plan/wave/phase Notion writes through `wave_execution_state.py` and a new post-cursor-agent marker hook that calls Notion's REST API directly (bypassing the MCP layer entirely). Switching the Notion MCP transport (stdio → OAuth-hosted variant) is **deferred as a separate decision** because it does not fix the drift root cause.

### 2.1 Why drift happens today (verified RCA)

Five things are already in place, but each has a gap:

| Component | Status | Gap |
|---|---|---|
| `PLAN_CREATED:` marker | Wired (§36) | Hook only **enqueues**, does not call Notion. Cursor Agent must still make the `API-post-page` call. |
| `wave_execution_state.py start` | Wired (§36) | Blocks unregistered plans, but does **not** patch Plans DB Status to `In Progress`. |
| `WAVE_COMPLETE:` / `PHASE_COMPLETE:` markers | Wired (§35 — drains AG queue) | Drains Author-Gate queue only; **does not** patch Notion plan progress. |
| `notion-plan-wave-deferral.md` | Wired | Forbids mid-wave Notion writes — correct, but is a "don't" rule, not a "do" path. |
| `tools/notion/*.py` direct-HTTP scripts | 30 scripts in production | Only invoked manually or by CI; never tied to wave lifecycle markers. |

The drift is therefore a **control-flow gap**: Cursor Agent is the only thing that bridges the existing markers to the existing HTTP scripts. Cursor Agent forgets. The user reminds. Drift returns next session.

### 2.2 Why direct-HTTP from a hook is the right chokepoint

| Alternative | Verdict |
|---|---|
| **A. Switch Notion MCP to OAuth-hosted (`https://mcp.notion.com/mcp`)** | ❌ Does not fix §25. The audit hook (`post_cursor_agent_mcp_serialization_audit.py`) classifies remote by tool-name suffix pattern, not transport. Switching the variant changes the suffix but the rule still fires. Variant C also incurs migration cost: every existing skill, hook, and `tools/notion/*.py` script references the v1 OpenAPI tool names (`API-post-page`, `API-query-data-source`); v2.0 uses different verbs (`notion-search`, `notion-create-page`). |
| **B. New always-on rule reminding Cursor Agent to update Notion** | ❌ Adds tokens, not enforcement. The current rules (§25, §35, §36, deferral, status-taxonomy) already total ~50KB of always-on guidance. The drift proves rules don't replace deterministic execution. |
| **C. Pre-MCP-gate intercepts** | ❌ Confirmed impossible: `pre_mcp_gate.py` cannot see tool arguments (memory `3ba710ed` references `pre_mcp_gate.py:1042-1051`). |
| **D. CI gate posts retroactively** | ⚠️ Useful as a backstop only. Runs at commit time, not session time. CI environment may lack `NOTION_API_KEY`. |
| **E. Marker hook + direct HTTP from hook (this plan)** | ✅ Cursor Agent emits a one-line marker (cannot avoid in normal phrasing). Hook deterministically shells out to Python script. Script calls Notion REST API directly. Cursor Agent is removed from the critical path. **Does not invoke any MCP tool — §25 does not apply.** |
| **F. Extend `wave_execution_state.py` itself to call Notion** | ✅ Complementary to E. The CLI is already the chokepoint for §36 registration check; adding side-effect Notion patches at `start` and `complete` makes Notion writes mandatory at wave boundaries. |

This plan combines **E + F**: a new post-cursor-agent hook captures markers and invokes the CLI; the CLI is extended with a `wave-progress` subcommand and gains Notion side-effects on `start` / `complete`.

### 2.3 Why this does not violate `notion-plan-wave-deferral.md`

The rule says "Cursor Agent MUST NOT call any Notion **MCP** tool" mid-wave. Direct HTTP via `urllib.request` from a Python script invoked by a hook is **not an MCP tool call** — it does not go through the Windsurf MCP transport, does not appear in `<function_calls>` blocks, and is not visible to `post_cursor_agent_mcp_serialization_audit.py`. The deferral rule is preserved verbatim; this plan adds a sanctioned non-MCP path.

### 2.4 Why this does not violate §25 (MCP serialization)

Same reason. The audit classifies remote MCPs by inspecting `<invoke name="mcp\d+_API-...">` patterns in the Cursor Agent response. Hook-spawned Python subprocesses do not emit those tags. The `tools/notion/*.py` scripts already do this in production (e.g. `sync_decision_ledger.py` runs as a CI job and writes 100s of rows; never trips §25).

## 3. Files in scope

In scope (this plan only):

| Path | Action |
|---|---|
| `tools/notion/wave_lifecycle_writer.py` | NEW — pure-HTTP writer: `patch_plan_status()`, `append_wave_progress_note()`, `mark_plan_completed()`. |
| `tools/notion/_wave_lifecycle_helpers.py` | NEW — pure-logic helper: marker→Notion patch spec; importable, no I/O. |
| `tools/plan_lifecycle/wave_execution_state.py` | EXTEND — add `wave-progress --plan <slug> --wave N` subcommand; `start` patches to `In Progress`; `complete` patches to `Completed`. |
| `.cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py` | NEW — parses `WAVE_START:` / `WAVE_COMPLETE:` / `PHASE_COMPLETE:` / `PLAN_COMPLETE:` markers and shells out to the writer. |
| `.cursor/hooks.json` | EXTEND — register the new post-cursor-agent hook (one row, schema-pure per §27). |
| `ops_scripts/ci/check_plan_notion_wave_freshness.py` | NEW — NP4 freshness gate (advisory; fail-closed via env). |
| `ops_scripts/ci/run_contract_gates.py` | EXTEND — register NP4. |
| `tests/unit/tools_notion/test_wave_lifecycle_writer.py` | NEW — patch helper logic, dry-run mode, idempotency. |
| `tests/unit/windsurf_scripts/test_post_cursor_agent_wave_lifecycle_capture.py` | NEW — marker parsing, shell-out args. |
| `.cursor/rules/notion-plan-wave-deferral.md` | UPDATE — add §"Sanctioned non-MCP path" section. |
| `AGENTS.md` Notion section | UPDATE — note auto-sync chain in routing table. |

Out of scope (deferred to follow-up plans):

- Switching to Notion OAuth-hosted MCP (variant C) — separate plan, separate Author-Gate.
- Backfilling 100s of historical plans where Notion drift already exists — handled by `tools/notion/repair_notion_plan_statuses.py` (already exists; one-shot run).
- Notion writeback for Backlog Items mid-plan (already handled by `post_cursor_agent_deferred_scope_capture.py`).

## 4. ADG_GRAPH_LAYER_EVIDENCE

The files in scope live in `.cursor/scripts/`, `tools/windsurf/`, `tools/notion/`, and `ops_scripts/ci/` — **outside the static ADG corpus** (which scans `agentic_core/`, `apps_*/`, `infrastructure/`). No `mv_*` / semantic edge / `v_p*_*` view applies because the affected files are infrastructure tooling, not in-graph code. This matches the precedent set by `ssot-folder-enforcement-*` and `plan-location-*` tooling plans. ADG hotspot ranking is N/A; impact is bounded by the 11 files listed in §3.

**ADG Provenance**: backend=sqlite, snapshot=adg_indexed_<latest>.sqlite (read at plan time; no in-graph nodes affected).

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1, P1.2 | Direct-HTTP writer + pure helper | ~6k | `NOTION_TOKEN` available; Plans DB schema unchanged from memory `2fe76ae0` | Not Started | `wave_lifecycle_writer.py --dry-run` patches a known plan correctly; helper unit tests green |
| W2 | P2.1, P2.2 | Extend `wave_execution_state.py` | ~5k | W1 writer importable; CLI argparse stable | Not Started | `start` calls writer → Plans DB Status flips to `In Progress`; `complete` flips to `Completed`; new `wave-progress` subcommand appends Notes line |
| W3 | P3.1, P3.2 | Marker capture hook + hooks.json | ~5k | W2 CLI subcommands stable; marker grammar fixed in §6 | Not Started | Hook parses 4 marker kinds; shells out to CLI; idempotent on repeated markers |
| W4 | P4.1, P4.2 | NP4 CI freshness gate + tests | ~4k | W1-W3 landed; advisory by default | Not Started | NP4 detects on-disk-vs-Notion skew >24h; advisory unless `NOTION_PLANS_WAVE_FAIL_CLOSED=1` |
| W5 | P5.1, P5.2 | Rule + AGENTS.md updates + DoD smoke | ~3k | W1-W4 landed | Not Started | Smoke run end-to-end: emit fake `WAVE_COMPLETE:` marker, observe Notion patch within 2s |

Total estimate: ~23k tokens.

## 6. Marker grammar (new + extended)

```
WAVE_START: plan=<slug-6hex> wave=<N>             # NEW — emitted on first edit of wave N
WAVE_COMPLETE: plan=<slug-6hex> wave=<N>          # EXTEND existing §35 marker with required wave=
PHASE_COMPLETE: plan=<slug-6hex> phase=<id>       # already in use; add Notion side-effect
PLAN_COMPLETE: plan=<slug-6hex>                   # NEW — emitted by wave_execution_state.py complete
```

Plain-text, own line, parseable by simple regex. Existing `WAVE_COMPLETE:` / `PHASE_COMPLETE:` markers in the §35 enforcement chain remain backward-compatible (the `wave=` / `phase=` field is optional in current parser; new hook treats missing values as no-op).

## 7. Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|----------|-------|-------|-------------|-------------|--------|
| P1.1 | Pure helper module | `_wave_lifecycle_helpers.py`: marker → `NotionPatchSpec` decision logic. No I/O. | Status taxonomy must align with memory `2fe76ae0` (`Not Started` / `In Progress` / `Completed`, NOT `Draft`/`Live`) | ~3k | Not Started |
| P1.2 | HTTP writer | `wave_lifecycle_writer.py`: `patch_plan_status`, `append_wave_progress`, `mark_plan_completed`. Mirror pattern from `apply_plan_derived_status.py`. | Property name `AI Summary ` has trailing space (memory `78c557a4`) | ~3k | Not Started |
| P2.1 | CLI subcommand | New `wave-progress --plan --wave` in `wave_execution_state.py` | Must not break existing `start` / `complete` callers (§36) | ~2k | Not Started |
| P2.2 | Side-effects in start/complete | `start` → `In Progress`; `complete` → `Completed` + AI Summary refresh | Failure modes: no `NOTION_TOKEN`, network down. Must fail-soft (warn, not block wave-state) | ~3k | Not Started |
| P3.1 | Marker capture hook | `post_cursor_agent_wave_lifecycle_capture.py`: parse 4 marker kinds, shell out per marker | Idempotency — same marker twice in one response = single Notion call | ~3k | Not Started |
| P3.2 | hooks.json wiring | One new `post_cursor_agent_response` row, `show_output: false` | Schema purity §27 — only `command` / `working_directory` / `show_output` | ~2k | Not Started |
| P4.1 | NP4 freshness gate | `check_plan_notion_wave_freshness.py`: compare plan file mtime vs Notion `last_edited_time` | Skip when `NOTION_API_KEY` unset (offline CI) | ~2k | Not Started |
| P4.2 | Test coverage | Unit tests for helper, writer, hook, gate | Mock Notion HTTP via `urllib.request` patching | ~2k | Not Started |
| P5.1 | Rule + AGENTS.md | Document sanctioned non-MCP path | Don't loosen `notion-plan-wave-deferral.md` invariant; clarify it | ~2k | Not Started |
| P5.2 | DoD smoke run | End-to-end: emit fake marker, verify Notion patch | Requires live `NOTION_TOKEN` and a test plan slug | ~1k | Not Started |

## 8. Bypass + telemetry

- **Env vars**: `WAVE_LIFECYCLE_NOTION_BYPASS=1` (skip writer side-effects), `WAVE_LIFECYCLE_CAPTURE_BYPASS=1` (skip hook), `NOTION_PLANS_WAVE_FAIL_CLOSED=1` (NP4 strict mode).
- **Log**: `artifacts/cursor/wave_lifecycle_notion.jsonl` — every patch attempt with timestamp, plan, marker, HTTP status.
- **Failure mode**: writer fails-soft on HTTP error (logs + exit 0); hook fails-soft on parse error (logs + exit 0). Wave execution never blocks on Notion.

## 9. Definition of Done

| ID | Criterion | Verification | Deferral allowed? |
|----|-----------|--------------|-------------------|
| DoD-1 | Functional outcome | After `WAVE_COMPLETE:` marker, Notion Plans row Notes contains `W{N} ✅ DONE — <ts>` within 2s | No |
| DoD-2 | Smoke-run | `python tools/plan_lifecycle/wave_execution_state.py start --plan <test-slug>` exits 0 AND patches Plans DB to `In Progress` | No |
| DoD-3 | Test count | ≥15 new unit tests across writer, hook, helper, gate; all green | No |
| DoD-4 | CI gate registered | NP4 appears in `run_contract_gates.py` output as `[advisory]` row | No |
| DoD-5 | Doc + memory | `notion-plan-wave-deferral.md` updated; AGENTS.md routing table notes auto-sync chain | No |
| DoD-6 | Live verification | One real plan wave-completed end-to-end; Notion `last_edited_time` confirms patch | Deferred allowed (advisory) — flag in plan retrospective if not run |

Verification-vs-deferral table: DoD-1 through DoD-5 mandatory; DoD-6 best-effort.

## 10. Risks + mitigations

| Risk | Mitigation |
|---|---|
| Hook parser misfires on prose mention of `WAVE_COMPLETE:` | Same regex discipline as `_plan_registration.py` — require `^WAVE_COMPLETE:` at start of line |
| `NOTION_TOKEN` rotation breaks writer | Already a known failure mode; writer fails-soft; NP4 surfaces stale state at commit time |
| Notion API rate limit (3 req/sec) | Writer uses `THROTTLE_S = 0.35` matching `apply_plan_derived_status.py`; one wave completion = 1 PATCH call (well under limit) |
| Plans DB schema drift (e.g. property rename) | Helper accepts property names as constants imported from `_notion_constants.py`; renames update one place |
| Two parallel Cursor Agent sessions on same plan | Notion PATCH is idempotent on `last_edited_time`; last-writer-wins acceptable for status field |
| `wave_execution_state.py complete` called when AI Summary needs refresh | Deferred — manual `tools/notion/repair_notion_plan_summaries.py` handles batch repair; in-scope auto-refresh would expand wave count |

## 11. Why not switch to OAuth-hosted MCP in this plan (variant C)

Separate Author-Gate decision required:
- Affects all 30 `tools/notion/*.py` scripts (still use v1 tool shape via direct HTTP — would not break, but tool-name audit patterns in §25 must update).
- Affects every skill referencing `API-post-page` etc.
- Requires one-time browser OAuth flow per workstation.
- Migration risk vs benefit unclear without enumerating v2.0 tool surface (would need to launch the OAuth server once and inspect `tools/list`).

**Sequencing**: this plan first (drift fix); variant C migration as a follow-up plan with its own §6 Author-Gate. Doing C alone would NOT fix drift; doing this plan alone DOES fix drift. So this plan is the higher-priority path regardless of C.

## 12. Constitutional cross-references

- §25 (MCP serialization) — preserved; this plan does not invoke any MCP tool.
- §27 (Windsurf config schema purity) — preserved; only `command` / `working_directory` / `show_output`.
- §31 (SSOT folder routing) — followed; `check_*` → `ops_scripts/ci/`, `post_*` → `.cursor/scripts/`, writer → `tools/notion/`, helper → `tools/notion/`.
- §35 (Author-Gate queue drain) — preserved; `WAVE_COMPLETE:` marker still triggers AG drain unchanged.
- §36 (plan-Notion registration) — extended; `start` now also patches Status to `In Progress`.

## 13. Author-Gate decisions required before W1

One. The marker grammar in §6 introduces two new markers (`WAVE_START:`, `PLAN_COMPLETE:`). Decision:
- **Option A**: New explicit markers Cursor Agent must emit (high precision, requires Cursor Agent discipline).
- **Option B**: Hook derives both from existing `WAVE_COMPLETE:` boundaries (zero new markers, slightly less precise — `WAVE_START:` inferred as `WAVE_COMPLETE: wave=N-1` end).
- **Option C** (recommended ⭐): Hybrid — `PLAN_COMPLETE:` is auto-emitted by `wave_execution_state.py complete` (deterministic, no Cursor Agent involvement); `WAVE_START:` inferred from first `WAVE_COMPLETE:` boundary in the session (zero Cursor Agent burden, sufficient precision for status display).

Surfaces via `ask_user_question` before W1 begins.
