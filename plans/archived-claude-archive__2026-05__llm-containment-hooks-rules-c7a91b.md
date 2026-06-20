---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\llm-containment-hooks-rules-c7a91b.md'
original_relative_path: '_archive\\2026-05\\llm-containment-hooks-rules-c7a91b.md'
source_sha256: d37c45657ef90d7c7ec3c3f206536dd4b5b921ccd62b2646132d17b9a0cb9e89
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: llm-containment-hooks-rules-c7a91b
plan_type: governance
# governance → §22 ADG graph-layer-evidence gate SKIPPED (rule/hook/ignore-file change, no code refactor)
---

# LLM Containment — Harness Hardening (Items 1, 2, 4)

Implement three highest-ROI containment controls from web-research review: repo-level ignore file to shrink indexing surface, post-response grep-budget audit to deter shotgun text search, and an always-on `scope-containment` rule codifying the PBI scope-limitation discipline.

---

## Context (SCQA)

- **Situation** — `.cursor/rules/` carries 15+ always_on rules and deterministic hooks cover pre-read/write/run/mcp + 13 post_cascade audits; however the repo has no `.codeiumignore`, no enforcement against unbounded `grep_search`/`code_search` calls, and no explicit scope-limitation rule. Cursor Agent indexes `archives/`, `artifacts/`, `reports/`, `data/` on every session and is free to grep-bomb the whole tree.
- **Complication** — Web research (Cursor, Windsurf docs, Augment Intent, Anthropic skills, MintMCP, Addy Osmani) converges on three control points: (a) shrink what the agent can see, (b) cap how many text-search shots per response, (c) hard-rule scope drift. Without these, the agent reviews the entire codebase on every run and scope creeps silently.
- **Question** — How do we add the highest-ROI containment controls (ignore file + grep audit + scope rule) without breaking existing workflows or hook chain?
- **Answer** — Add `.codeiumignore` (indexing shrink), `post_cursor_agent_grep_budget_audit.py` (advisory post-hook, ≤3 grep_search/code_search per response, logs violations, fail-open), and `.cursor/rules/scope-containment.md` (always_on, codifies "no gold plating / one task in progress / changes outside scope EXPRESSLY PROHIBITED"). Wire the new audit into `post_cursor_agent_response` chain after `post_cursor_agent_adg_audit.py`.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/hooks.json` | wire the new post-hook script | ✅ read |
| `.cursor/scripts/post_cursor_agent_adg_audit.py` | pattern reference for post-response audits | ✅ located |
| `docs.windsurf.com/windsurf/cascade/hooks` schema | entries MUST be `command`+`working_directory`+`show_output` only (§27) | ✅ verified |
| Tavily web research (Cursor, Augment, Anthropic) | best-practice source | ✅ complete |
| PBI agent rules gist (boxabirds) | scope-limitation canonical text | ✅ reviewed |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| W1 | 3 files created + hooks.json edited | `.codeiumignore`, grep audit, scope rule, hooks wiring | A | ~8K 🟢 |
| W2 | Smoke verification + Notion writeback | Plans DB row, backlog row if warranted | B | ~3K 🟢 |

**Total: ~11K tokens across 2 waves, all GREEN**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Create `.codeiumignore` | repo-root `.codeiumignore` | PP-1 unbounded indexing | ~2K | ✅ DONE |
| 1.2 | Author grep-budget post-hook audit | `.cursor/scripts/post_cursor_agent_grep_budget_audit.py` | PP-2 shotgun grep | ~3K | ✅ DONE |
| 1.3 | Author `scope-containment.md` rule | `.cursor/rules/scope-containment.md` | PP-3 silent scope creep | ~2K | ✅ DONE |
| 1.4 | Wire hook into `post_cursor_agent_response` chain | `.cursor/hooks.json` | integration | ~1K | ✅ DONE |
| 2.1 | Smoke-test audit script (run manually on a synthetic response) | — | verify fail-open | ~1K | ✅ DONE |
| 2.2 | Notion writeback: Plans DB row | Notion MCP | durable record | ~2K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: No repo-level `.codeiumignore`**
- Windsurf local indexer preprocesses up to a configurable file cap. Without `.codeiumignore`, large archives/artifacts/data dirs crowd the index budget and dilute relevant retrieval.
- Impact: slower indexing, noisier Fast Context results, larger effective context per session start.

**GAP-2: No grep-budget enforcement**
- `grep_search` and `code_search` are native Cursor Agent tools with NO pre-execution hook (per `global_rules.md` ADG-First section). Only retroactive detection is possible.
- Impact: without an audit, Cursor Agent can issue unlimited text searches — an attention-tax behavior and a proxy for "reviewing entire codebase every run" that the user is trying to contain.

**GAP-3: No explicit scope-containment rule**
- Constitutional §18 says "no hidden scope expansion" but is silent on gold-plating, one-task-in-progress, and the "EXPRESSLY PROHIBITED" framing that the PBI canonical rule set uses.
- Impact: rules are advisory-too-soft on scope drift; Cursor Agent will still volunteer out-of-scope edits.

---

## Execution Plan

### Phase 1.1 — `.codeiumignore`

**Scope**: repo-root ignore file for Windsurf local indexing.

**Excludes**: `archives/`, `.coverage`, `reports/`, `data/`, most of `artifacts/` except the **latest** ADG snapshot (glob keeps current snapshot readable), common junk (`__pycache__`, `.pytest_cache`, `node_modules`, `.venv`, etc.).

**Acceptance**: file exists at `c:\Git\Agentic-Workflow-FRESH\.codeiumignore`; Windsurf re-index respects it (verified next session start via reduced index size).

### Phase 1.2 — `post_cursor_agent_grep_budget_audit.py`

**Scope**: new post-response audit script in `.cursor/scripts/`.

**Behavior**:
- Reads the Cursor Agent response text (same input-mechanism as sibling post-hooks).
- Counts `grep_search` and `code_search` tool invocations in the response.
- Soft-cap: **3 combined per response**. Above cap → append JSONL row to `artifacts/cursor/grep_budget_violations.jsonl` with `{timestamp, response_id, grep_count, code_search_count, total, cap, bypass}`.
- Bypass env var: `GREP_BUDGET_BYPASS=1` — logs row with `bypass=true`, still permitted (advisory).
- Fail-open: any internal error → exit 0 and log to stderr (mirrors `post_cursor_agent_adg_audit.py` pattern).

**Acceptance**: script exits 0 on all inputs; violations file format matches sibling audits.

### Phase 1.3 — `scope-containment.md` rule

**Scope**: new always_on rule at `.cursor/rules/scope-containment.md`.

**Content (summarized)**:
- Scope is what the current plan's `Files In Scope` names + what the user explicitly asked for — nothing more.
- No gold-plating, no "while I'm here" edits, no refactors Cursor Agent "noticed needed doing".
- Improvements outside scope → emit `NEXT_STEP:` marker, DO NOT implement in current response.
- One active task at a time; concurrent scopes require explicit user approval.
- Cross-references constitutional §18 (no hidden scope expansion) and `next-step-capture.md`.
- Keeps rule body lean per Cursor Agent alignment (procedural detail lives in the skill, not the rule).

**Acceptance**: rule file valid, frontmatter `trigger: always_on`, passes `check_windsurf_config_schema.py` if it runs over rules (it doesn't — rules are free-form md).

### Phase 1.4 — hooks.json wiring

**Scope**: insert one entry in `post_cursor_agent_response` chain, positioned after `post_cursor_agent_adg_audit.py` (grep audit is thematically adjacent to ADG-first enforcement).

**Acceptance**: JSON remains schema-valid (`command` + `working_directory` + `show_output` only per constitutional §27); `check_windsurf_config_schema.py` passes.

### Phase 2.1 — smoke test

**Scope**: run the grep-budget audit against `/dev/null`-equivalent input and a synthetic response string containing 5 mock grep calls. Verify:
- Empty input → exit 0, no violations file row.
- 5 grep calls → exit 0, one row in `artifacts/cursor/grep_budget_violations.jsonl`.
- `GREP_BUDGET_BYPASS=1` → exit 0, row logged with `bypass=true`.

### Phase 2.2 — Notion writeback

**Scope**: `API-post-page` into Plans DB (`6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`) with Status=Active, Plan File Path set, Exists On Disk=true.

---

## Rules

- Hooks/MCP-config schema purity (constitutional §27).
- MCP serialization (§25): one MCP call per response.
- SSOT folder routing (§31): scripts into `.cursor/scripts/`, plan into `.cursor/plans/`.
- Plan location (`plan-location.md`): SSOT `.cursor/plans/<slug>-<6hex>.md`.
- No deletion of existing hooks; additive only.

---

## Success Criteria

- [x] `.codeiumignore` exists and excludes `archives/`, `reports/`, `data/`, and most of `artifacts/`
- [x] `post_cursor_agent_grep_budget_audit.py` authored, fail-open, bypass honored
- [x] `scope-containment.md` rule authored, always_on, lean
- [x] `hooks.json` wires the new audit in `post_cursor_agent_response`
- [x] Smoke test passes (empty=rc0, over-cap=rc0 + stderr warning + JSONL row, bypass=rc0 + JSONL row with bypass=true) — verified 2026-05-02
- [x] Notion Plans DB row created (page `35327693-f55c-81c1-8f7f-d51979ceb51c`)

**Status: ✅ COMPLETED 2026-05-02**

---

## Rollback Strategy

1. Remove the new hooks.json entry (single-line JSON delete).
2. Delete `.codeiumignore`, the new audit script, and the new rule.
3. No migrations, no state changes — pure-additive plan, trivial rollback.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| New files written | 3 (`.codeiumignore`, audit, rule) | `git status` |
| hooks.json schema | valid | `python ops_scripts/ci/check_windsurf_config_schema.py` |
| Audit fail-open | exit 0 on all inputs | manual smoke test |
| Notion Plans row | exists, Status=Active | query Plans DB |

---

## Deferred / Next Steps (from web review, NOT in this plan)

These are backlog for future work — do NOT silently expand scope of the current plan to cover them:

- Item 3: `pre_write_code` plan-scope guard (reject writes outside plan's `Files In Scope`) — larger, touches the authoring gate
- Item 5: audit always_on rules, demote 3-4 to `agent_requested`
- Item 6: `post_cursor_agent_scope_drift_detector.py` — files-touched-vs-plan-manifest comparison
- Item 7: `OUT_OF_SCOPE:` section in execution plan template
- Item 8: `pytest`-without-`-k` blocker in `pre_run_gate`

A follow-up `NEXT_STEP:` marker will capture these for the Wave/Phase Convergence backlog.

---

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
