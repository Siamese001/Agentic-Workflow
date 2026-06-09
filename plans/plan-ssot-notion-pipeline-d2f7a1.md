---
plan_id: plan-ssot-notion-pipeline-d2f7a1
plan_format: v2
plan_type: governance
status: Not Started
ai_summary: "Plans always land in main-checkout plans SSOT; Notion row created after full write and synced to plan content."
touches_governance_ci: true
dod_exempt: false
supersedes: []
---

# Plan→SSOT→Notion Pipeline — Land in Main SSOT, Register Complete & Synced

One plan: make every plan file land in `C:\Git\Agentic-Workflow-FRESH\plans` (no exceptions), and make the Notion row appear only after the plan is fully written and stay synced to its content.

## Context (SCQA)

- **Situation.** Plans are the always-on SSOT at repo-root `plans/`. Each chat runs in a per-chat git
  worktree (`session_start_branch_guard.py`), and a Notion Plans DB row is meant to mirror every plan (§36).
- **Complication (RCA — two coupled defects, code-confirmed).**
  1. **Plans never reach the main SSOT.** `before_file_edit_branch_guard.py` BLOCKS every Edit/Write to
     the primary checkout while on `main`, with **no `plans/**` exemption**. So a plan written during a
     chat lands in the chat worktree's `plans/`, not `C:\Git\Agentic-Workflow-FRESH\plans`. The worktree is
     ephemeral — `prune_merged_chat_worktrees.py` reaps it after merge, and unmerged chats are abandoned.
     The canonical SSOT folder is chronically incomplete.
  2. **Notion rows are stub pointers created before the plan is complete.** Registration is
     **response-marker-driven**: `post_agent_plan_registration_capture.py` scans the agent *response* for
     `PLAN_CREATED:` and queues **metadata only** (slug/path/status); the row is then created via
     `API-post-page` from that metadata. Nothing reads the finished plan file, the marker fires regardless
     of whether the file is fully written, and `_plan_registration.enqueue_plan` stores **no content
     digest** — so the row never reflects the plan body and drift is undetectable.
- **Question.** How do we guarantee plans live in the main SSOT and Notion rows are complete + synced?
- **Answer.** (W1) Exempt `plans/**` from the worktree guard and resolve plan writes to the primary
  checkout's `plans/`. (W2) Make registration **file-driven**: enqueue only after a complete plan file
  exists in the SSOT (passes `validate_plan_format`), carrying a content digest + extracted AI summary.
  (W3) **Sync the plan body** into the Notion page on registration and re-sync on every plan edit.
  (W4) A **drift gate** asserting every SSOT plan has a Notion row whose content digest matches the file.

## Status Tables

### Wave Progress

> Execution order (required): W1 → W2 → W3 → W4. Each wave depends only on lower-numbered waves.

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Path: plans always write to the main-checkout plans SSOT | ~70k | guard is the only blocker | 🔲 TODO | `plans/**` exempt from worktree guard; canonical-plans-path resolver; rule mandates the main SSOT path; tests prove a plan write to the primary checkout is allowed |
| W2 | W2.1, W2.2 | Sequence: register only after a complete plan file exists in the SSOT | ~80k | depends on W1 | 🔲 TODO | registration is file-driven (not response-marker); enqueue gated on `validate_plan_format` clean + frontmatter present; queue row carries content_digest + ai_summary |
| W3 | W3.1 | Content: sync the plan body into the Notion row + re-sync on edit | ~90k | depends on W2; needs Notion token to live-verify | 🔲 TODO | `plan_driven_closer` upserts page body from the file; row content == file at registration; a later plan edit re-syncs |
| W4 | W4.1 | Drift gate: assert SSOT plan ↔ Notion content in sync | ~60k | depends on W3 | 🔲 TODO | freshness gate flags any SSOT plan whose content_digest != the Notion row; wired into the pre-commit/weekly registration check |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Exempt `plans/**` from `before_file_edit_branch_guard.py` + canonical-path resolver | 🔲 TODO |
| W1.2 | Rule + template: mandate main SSOT absolute path, no exceptions | 🔲 TODO |
| W2.1 | File-driven registration trigger (post-write, complete-file precondition) | 🔲 TODO |
| W2.2 | Queue row carries content_digest + extracted ai_summary | 🔲 TODO |
| W3.1 | `plan_driven_closer` body upsert from file + re-sync on edit | 🔲 TODO |
| W4.1 | Content-drift detection in `check_plan_registration_freshness` / `drift_report` | 🔲 TODO |

## RCA evidence (file:line)
- Guard, no plans exemption: `.claude/hooks/before_file_edit_branch_guard.py:106-127` (blocks primary checkout on protected branch; `plans/**` not exempt).
- Worktree routing: `.claude/hooks/session_start_branch_guard.py` + `git-branch-per-chat.md`; reaper `.claude/hooks/prune_merged_chat_worktrees.py`.
- Marker-driven, metadata-only capture: `post_agent_plan_registration_capture.py:7-16,102-124` (scans response, queues slug/path/status; "register via API-post-page").
- No content in queue row: `_plan_registration.py:175-196` (`enqueue_plan` row = slug/path/declared_status/captured_at/registered — no digest, no body, no ai_summary).
- Legacy path default documented: `post_agent_plan_registration_capture.py:15`; resolver prefers `plans/` (`_plan_registration.py:126-135`) but marker examples still cite `.claude/plans/`.

## Wave 1 — Path: plans always to the main SSOT

WAVE_ID: W1
WAVE_STATUS: TODO

**Phases**:
- **W1.1** — Exempt `plans/**` (parent dir == `plans`, `.md`, not `_archive`) from the worktree edit guard so plan files write to the primary checkout regardless of branch. Add `canonical_plans_dir()` resolving to `$CLAUDE_PROJECT_DIR/plans` (primary checkout) even when CWD is a worktree.
- **W1.2** — `plan-location.md` + template: mandate the absolute main SSOT path (`C:\Git\Agentic-Workflow-FRESH\plans`), no exceptions; note worktree code stays in the worktree but plans are a shared SSOT.

**Acceptance**: a Write to `C:/Git/Agentic-Workflow-FRESH/plans/<slug>.md` is ALLOWED by the guard; non-plan edits to the primary checkout stay BLOCKED.

## Wave 2 — Sequence: register only after the complete file exists in SSOT

WAVE_ID: W2
WAVE_STATUS: TODO

**Phases**:
- **W2.1** — Replace response-marker capture with a file-driven trigger: after a plan file is written to the SSOT, enqueue for registration ONLY if it passes `validate_plan_format` (clean) and has frontmatter. The `PLAN_CREATED:` marker becomes advisory, not the source of truth.
- **W2.2** — Extend `enqueue_plan` to store `content_digest` (sha256 of the file body) + `ai_summary` (extracted from frontmatter) so the row can be created complete and drift detected.

**Acceptance**: registering a stub/partial plan is refused; the queue row carries digest + summary.

## Wave 3 — Content: sync the plan body to the Notion row

WAVE_ID: W3
WAVE_STATUS: TODO

**Phases**:
- **W3.1** — `plan_driven_closer` (the Notion HTTP writer) upserts the plan body (Wave/Phase tables + DoD, or a faithful mirror) into the Notion page on registration, and re-syncs on subsequent plan-file edits (digest changed). Row content == file at registration time.

**Acceptance**: a registered row's content matches the plan file; editing the plan re-syncs the row.

## Wave 4 — Drift gate

WAVE_ID: W4
WAVE_STATUS: TODO

**Phases**:
- **W4.1** — `drift_report` / `check_plan_registration_freshness` flag any SSOT plan whose stored `content_digest` != the live Notion row (content out-of-sync), not just presence. Wire into the existing pre-commit/weekly registration check.

**Acceptance**: a deliberately desynced plan is flagged by the gate.

## Definition of Done
| # | Criterion | Verification |
|---|---|---|
| 1 | A plan write to the primary checkout `plans/` is allowed on `main` | guard unit test: `plans/x.md` on primary → exit 0; `agentic_core/x.py` on primary → exit 2 |
| 2 | `canonical_plans_dir()` resolves to the primary checkout from a worktree | unit test asserts the resolved path is `<primary>/plans` |
| 3 | Registration refuses an incomplete plan; accepts a complete one | unit test: stub plan → not enqueued; v2-complete plan → enqueued with digest+summary |
| 4 | Queue row carries content_digest + ai_summary | unit test on `enqueue_plan` row shape |
| 5 | Drift gate flags a content-desynced plan | unit test on `drift_report` content-mismatch branch |
| 6 | Smoke: governance gates still run | `python ops_scripts/ci/check_plan_registration_freshness.py` exits cleanly; `pytest` for touched validators green |

## Supersedes
| Predecessor slug | Reason |
|---|---|
| _None — net-new plan._ | |
