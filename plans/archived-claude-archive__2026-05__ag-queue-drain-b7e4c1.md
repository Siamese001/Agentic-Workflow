---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\ag-queue-drain-b7e4c1.md'
original_relative_path: '_archive\\2026-05\\ag-queue-drain-b7e4c1.md'
source_sha256: c40a67c623fc254b6dbb82bb7b397e535cdc3128c784e54e4c9da3bed64662fd
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: ag-queue-drain-b7e4c1
plan_type: governance
---

# Author-Gate Queue Drain Enforcement

Harden Windsurf to auto-drain pending Author-Gate packets after wave/phase completion so Cascade can no longer silently skip queued decisions.

---

## Context (SCQA)

- **Situation** — Author-Gate enforcement (§6, `author-gate-enforcement.md`) fires when Cascade *recognizes* a decision point. After a wave completes, pending AG items (per §24 deferred-scope or plan drafting) live only in Cascade's working memory and `todo_list`.
- **Complication** — Cascade repeatedly completes a wave and fails to emit the next queued packet; the user must manually prompt "next packet" every time. 2026-05-03 session surfaced 4 queued packets (W2.P4, W4.P3, W4.P2, W2.P3) silently dropped after W6 completion.
- **Question** — How do we make Author-Gate queue drain deterministic rather than behavioral?
- **Answer** — Durable on-disk queue (JSONL) seeded at plan-authoring time; pre-hook surfaces pending head-of-queue; post-hook audits completion responses for missing packet emission; constitutional §35 codifies the invariant.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/rules/author-gate-enforcement.md` | §6 trigger doctrine | ✅ |
| `.windsurf/rules/deferred-scope-capture.md` | §24 marker pattern precedent | ✅ |
| `.windsurf/rules/ssot-folder-enforcement.md` | §31 helper + 2 consumers pattern | ✅ |
| `.windsurf/scripts/post_cascade_author_gate_miss_detector.py` | existing AG audit shape | ✅ |
| `.windsurf/scripts/_ssot_folder_check.py` | helper pattern SSOT | ✅ |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Rule + helper + tests + §35 | State lib + rule + constitutional entry | A | ~12K ✅ |
| Wave 2 | Post-hook audit + hooks.json wire-up | Durable violation log | B | ~8K ✅ |
| Wave 3 | Pre-hook surface injection + AG_QUEUE_SEED marker + pre-commit gate | Proactive prompting | C | ~10K ✅ |
| Wave 4 | CI freshness gate + AGENTS.md + Notion flip | Weekly drift detection | D | ~6K ✅ |

**Total: ~36K tokens across 4 waves, ALL DONE ✅**

---

## Out Of Scope

- Altering existing §6 Author-Gate scoring / dominance rule logic.
- Changing `post_cascade_author_gate_capture.py` (captures decisions after answered) or `post_cascade_author_gate_miss_detector.py` (detects unemitted decisions within a response).
- Retroactively migrating pre-existing plans' queued packets — only future plans use `AG_QUEUE_SEED:` markers; existing queues built on-demand.
- Changes to `apps-eval-harness-parity-f8d4a2.md` or any parallel-session plan.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Queue helper (SSOT pure logic) | `.windsurf/scripts/_author_gate_queue.py` | PP-1 | ~4K | ✅ DONE |
| 1.2 | Rule authored | `.windsurf/rules/author-gate-queue-drain.md` | PP-2 | ~3K | ✅ DONE |
| 1.3 | Constitutional §35 entry | `.windsurf/rules/constitutional.md` | PP-3 | ~2K | ✅ DONE |
| 1.4 | Helper tests | `tests/unit/windsurf_scripts/test_author_gate_queue.py` | GAP-1 | ~3K | ✅ DONE |
| 2.1 | Post-hook audit script | `.windsurf/scripts/post_cascade_ag_queue_drain_audit.py` | PP-4 | ~5K | ✅ DONE |
| 2.2 | hooks.json wire-up | `.windsurf/hooks.json` | PP-5 | ~1K | ✅ DONE |
| 2.3 | Post-hook tests | `tests/unit/windsurf_scripts/test_ag_queue_drain_audit.py` | GAP-1 | ~2K | ✅ DONE |
| 3.1 | Pre-hook surface injection | `.windsurf/scripts/pre_user_prompt_ag_queue_surface.py` + hooks.json | PP-6 | ~4K | ✅ DONE |
| 3.2 | AG_QUEUE_SEED post-hook capture | `.windsurf/scripts/post_cascade_ag_queue_seed_capture.py` + hooks.json | PP-7 | ~3K | ✅ DONE |
| 3.3 | Pre-commit marker-prose gate | `ops_scripts/ci/check_ag_queue_seed_markers.py` + `.pre-commit-config.yaml` T7t | PP-8 | ~3K | ✅ DONE |
| 4.1 | Freshness CI gate | `ops_scripts/ci/check_ag_queue_drain_freshness.py` | PP-9 | ~3K | ✅ DONE |
| 4.2 | AGENTS.md / registry updates | deferred — no new MCP; rule registered via §35 | PP-10 | ~1K | ✅ DONE |
| 4.3 | Notion row flip to Completed | Notion Plans DB | — | ~2K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: No durable queue state**
- Pending AG packets exist only in Cascade's working memory + `todo_list` (session-volatile).
- Session restart loses the queue; Cascade cannot recover pending items.

**GAP-2: No post-wave-completion detection**
- Nothing scans Cascade's response for wave/phase completion markers AND absence of next-packet emission.

**GAP-3: No plan-time seeding**
- Plans describing future AG decisions ("Author-Gate required for W2.P4") use prose, not machine-readable markers.

---

## Pain Points

- **PP-1**: No shared helper for append-only queue reads/writes → duplication risk.
- **PP-2**: No always-on rule codifying the drain invariant.
- **PP-3**: Missing constitutional entry → rule is not tier-1 binding.
- **PP-4**: No post-hook audit → violations go unlogged.
- **PP-5**: Hook not wired → script would never execute.
- **PP-6**: Cascade has no proactive surface of pending head-of-queue at prompt time.
- **PP-7**: AG_QUEUE_SEED markers in plans need auto-capture into queue JSONL.
- **PP-8**: Plan prose ("Author-Gate required for X") without matching marker = silent drop.
- **PP-9**: No weekly drift detection → regression invisible.
- **PP-10**: AGENTS.md Quick Reference / rule index stale without sync.

---

## Execution Plan

### Wave 1 — Helper + Rule + Constitutional Entry + Tests

#### Phase 1.1 — Queue helper (SSOT pure logic)

**Scope**: `.windsurf/scripts/_author_gate_queue.py`

Exports:
```python
def enqueue(plan_slug: str, packet: dict) -> None
def next_packet(plan_slug: str) -> dict | None  # respects depends_on
def mark_answered(plan_slug: str, packet_id: str, chosen_option: str) -> None
def pending_count(plan_slug: str) -> int
def list_plans_with_pending() -> list[str]
```

State file: `.windsurf/state/author_gate_queue/<slug>.jsonl` (append-only).
Row shape: `{"id": str, "title": str, "depends_on": list[str], "status": "pending"|"answered", "recommended_option": str|None, "score": float|None, "gap": float|None, "enqueued_at": iso, "answered_at": iso|None, "chosen": str|None}`.

Pure — no subprocess, no environment reads, no logging. Specific exceptions only.

**Acceptance**: Import succeeds; helper functions work against temp state file; unit tests pass.

#### Phase 1.2 — Rule authored

**Scope**: `.windsurf/rules/author-gate-queue-drain.md`

Frontmatter: `trigger: always_on` (behavioral). Compact, invariant-focused per global rules policy.

**Acceptance**: Rule file validates YAML frontmatter; byte size <4KB.

#### Phase 1.3 — Constitutional §35 entry

**Scope**: Insert §35 clause in `.windsurf/rules/constitutional.md`. Append to §34 Hard Constraints list.

**Acceptance**: Rule count increments to 35; ordering preserved.

#### Phase 1.4 — Helper tests

**Scope**: `tests/unit/windsurf_scripts/test_author_gate_queue.py`

Coverage: enqueue idempotence, next_packet respects depends_on topology, mark_answered removes from head, pending_count accuracy, list_plans_with_pending, corruption recovery (malformed JSONL row skipped).

**Acceptance**: `pytest tests/unit/windsurf_scripts/test_author_gate_queue.py -v` — all green.

### Wave 2 — Post-Hook Audit + Wire-Up

#### Phase 2.1 — Post-hook audit script

**Scope**: `.windsurf/scripts/post_cascade_ag_queue_drain_audit.py`

Logic:
1. Read Cascade response from stdin or env payload.
2. Detect completion markers: `WAVE_COMPLETE:`, `PHASE_COMPLETE:`, `wave_execution_state.py complete`, `✅ DONE` on a wave row.
3. If completion marker present AND `_author_gate_queue.list_plans_with_pending()` non-empty AND response does NOT contain `AUTHOR_GATE_PACKET:` or `HITL_PACKET:` block → log violation to `artifacts/windsurf/ag_queue_drain_violations.jsonl`.
4. Fail-open (exit 0). Bypass: `AG_QUEUE_DRAIN_BYPASS=1`.

**Acceptance**: Script runs on synthetic fixture; violation logged when expected; no log when compliant.

#### Phase 2.2 — hooks.json wire-up

**Scope**: `.windsurf/hooks.json` — add `post_cascade_response` entry for the new script. `show_output: false`.

**Acceptance**: JSON schema pure (§27); no keys beyond `command`/`working_directory`/`show_output`.

#### Phase 2.3 — Post-hook tests

**Scope**: `tests/unit/windsurf_scripts/test_ag_queue_drain_audit.py`

Coverage: completion marker + empty queue = no log; completion marker + pending queue + no packet = violation; completion marker + pending queue + packet present = no log; bypass env suppresses log.

**Acceptance**: all tests green.

### Wave 3 — Pre-Hook Surface + Marker + Pre-Commit Gate

#### Phase 3.1 — Pre-hook surface injection

**Scope**: `.windsurf/scripts/pre_user_prompt_ag_queue_surface.py`

Logic: at prompt start, if `list_plans_with_pending()` returns any plan, print to stdout:
```
AG_QUEUE_PENDING: plan=<slug> next=<packet_id> depends_on=<...> title=<short>
```

Wire into `pre_user_prompt` in hooks.json, `show_output: true` so Cascade sees it.

**Acceptance**: Empty queue → no output; pending queue → exactly one line per plan.

#### Phase 3.2 — AG_QUEUE_SEED post-hook capture

**Scope**: `.windsurf/scripts/post_cascade_ag_queue_seed_capture.py`

Logic: scan response for `AG_QUEUE_SEED: plan=<slug> id=<pkt_id> depends_on=<...> title=<...>` lines; call `_author_gate_queue.enqueue()` for each. Idempotent.

Wire into `post_cascade_response` in hooks.json, `show_output: false`.

**Acceptance**: Synthetic response with 2 markers → 2 queue rows; re-run → no duplicates.

#### Phase 3.3 — Pre-commit marker-prose gate

**Scope**: `ops_scripts/ci/check_ag_queue_seed_markers.py`

Logic: for each staged `.windsurf/plans/*.md`, count prose lines matching `/Author-Gate (required|pending|needed) for/i` and count `AG_QUEUE_SEED:` markers. Prose lines MUST have ≥ matching markers. Bypass: `AG_QUEUE_SEED_BYPASS=1`.

Wire into `.pre-commit-config.yaml` as new hook (T7r or similar).

**Acceptance**: Plan with 3 prose lines + 3 markers → pass. Plan with 3 prose lines + 1 marker → fail with instructions.

### Wave 4 — Freshness Gate + Registry Sync + Notion Flip

#### Phase 4.1 — Freshness CI gate

**Scope**: `ops_scripts/ci/check_ag_queue_drain_freshness.py`

Logic: scan `artifacts/windsurf/ag_queue_drain_violations.jsonl` for last 7 days. Fail (exit 1) if ≥3 violations without matching `reason: "bypass"` entries. Bypass: `AG_QUEUE_DRAIN_FRESHNESS_BYPASS=1`.

**Acceptance**: Synthetic fixtures; both pass and fail paths verified.

#### Phase 4.2 — AGENTS.md / registry updates

**Scope**: `AGENTS.md` rule-count reference (if any); ensure §35 appears in `.windsurf/RULES_INDEX.md#always-on-discipline` if applicable. No Notion MCP registry changes (no new MCP).

**Acceptance**: `python ops_scripts/ci/check_mcp_sync_integrity.py` still green; no orphan references.

#### Phase 4.3 — Notion row flip to Completed

**Scope**: Notion Plans DB — flip this plan's row Status from Active/Draft to Completed. One-per-response per §25.

**Acceptance**: `API-retrieve-a-page` confirms Status=Completed.

---

## Rules

- All NEW Python files land in canonical SSOT folders (§31). Pre-existing files in `.windsurf/scripts/` and `ops_scripts/ci/` remain canonical.
- All subprocess calls use `timeout=` and `shell=False` (§0/§14).
- Specific exceptions only (§15) — no bare `except:` or `except Exception:` without guardian comment.
- Operations >5s display progress bar (§16) — not applicable here (fast scripts).
- Notion writes deferred until plan-end per `notion-plan-wave-deferral.md`.

---

## Success Criteria

- [ ] `_author_gate_queue.py` helper imports cleanly and passes all unit tests.
- [ ] `author-gate-queue-drain.md` rule loads with always_on trigger.
- [ ] Constitutional §35 present and referenced by audit script.
- [ ] Post-hook audit logs violations to `artifacts/windsurf/ag_queue_drain_violations.jsonl`.
- [ ] Pre-hook surface prints `AG_QUEUE_PENDING:` line when queue non-empty.
- [ ] `AG_QUEUE_SEED:` markers captured into queue JSONL by post-hook.
- [ ] Pre-commit gate blocks prose-without-marker plan commits.
- [ ] Freshness gate passes when ≤2 violations/week.
- [ ] All new tests green (helper + post-hook audit + freshness gate).
- [ ] Notion row flipped to Completed after final wave.

---

## Rollback Strategy

If hooks regress:
1. Remove new entries from `.windsurf/hooks.json` (revert to pre-wave-2 commit).
2. Delete `.windsurf/state/author_gate_queue/` directory (state-only, no code).
3. Rule and constitutional §35 can remain (advisory-only absent hook enforcement).
4. Pre-commit gate removable from `.pre-commit-config.yaml` without downstream impact.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Unit tests pass | 100% green | `pytest tests/unit/windsurf_scripts/test_author_gate_queue.py tests/unit/windsurf_scripts/test_ag_queue_drain_audit.py -v` |
| Hook chain fires | No regression | `python .windsurf/scripts/post_cascade_heartbeat.py` still emits |
| Violation log shape | Valid JSONL | Manual fixture trigger; `jq` validates rows |
| Freshness gate | exit 0 on empty log | `python ops_scripts/ci/check_ag_queue_drain_freshness.py` |
| Pre-commit gate | Blocks drift | Synthetic plan with prose-only → git commit fails |
