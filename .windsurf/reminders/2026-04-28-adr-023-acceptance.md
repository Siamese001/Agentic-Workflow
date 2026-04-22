---
due_date: 2026-04-28
created_date: 2026-04-22
created_in_session: cascade
priority: medium
topic: adr-acceptance
related_adr: ADR-023
related_plan: runtime-hitl-exit-control-c4e7b3.md
notion_row: 34927693-f55c-8139-9302-f818b3ec8a3b
memory_entity: Project:RuntimeHITL
---

# ADR-023 Formal Acceptance — Due 2026-04-28

## What

Advance ADR-023 (Runtime HITL Exit Control, v30 Step [5] ESCALATE) from **PROPOSED** to **ACCEPTED**.

## Why it's pending (as of 2026-04-22)

- Implementation is **fully shipped** — W1–W7 of `runtime-hitl-exit-control-c4e7b3.md` complete across commits `9444ffff0c` through `e24c660a62` (238 tests pass, zero regressions).
- ADR file line 8 still says `Status: PROPOSED — AWAITING REVIEW` with target decision date **2026-04-28**.
- Reviewers pending: L3 orchestration owner, L5 safety owner, compliance reviewer.
- Sign-off tracker: `docs/architecture/adr/ADR-023-review-request.md`.
- User decision 2026-04-22: **wait for review window** rather than unilaterally accept.

## Exact execution steps on reminder day

1. Confirm with user that reviewers have signed off (or that the deadline has passed without objection).
2. Edit `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md`:
   - Line 8: `**Status:** PROPOSED — AWAITING REVIEW` → `**Status:** ACCEPTED`
   - Add acceptance note above line 8 with date + deciders + rationale (implementation shipped, review window satisfied).
3. Close `docs/architecture/adr/ADR-023-review-request.md` (add a "Closed 2026-04-28" header or move to archived).
4. Commit:
   ```
   git add docs/architecture/adr/ADR-023-*.md
   git commit -m "ADR-023: PROPOSED->ACCEPTED (W1-W7 shipped, review window satisfied 2026-04-28)"
   ```
5. Patch Notion ADR-023 row:
   - Page ID: `34927693-f55c-8139-9302-f818b3ec8a3b`
   - `Status` select → `Accepted`
   - `Decision Date` → `2026-04-28`
   - `Summary` → strip `[REMINDER]` prefix, restore canonical summary
6. Update Memory entity `Project:RuntimeHITL` with observation: `accepted 2026-04-28, ADR-023 formally closed`.
7. Delete this reminder file or move it to `.windsurf/reminders/archived/`.

## How this will surface to Cascade

- Any future session calling `mem_recall_session_start` will see the REMINDER observation on `Project:RuntimeHITL`.
- Any session asking about HITL / ADR-023 will hit this via `search_nodes("RuntimeHITL")` or `search_nodes("ADR-023")`.
- The Notion ADR-023 row has `Decision Date: 2026-04-28` — visible in any dashboard filtered by upcoming dates.
- If the reminder-surfacing hook proposed below is wired, this file will be surfaced automatically at session start on or after 2026-04-28.

## Optional hook enhancement (NOT built yet)

A tiny `.windsurf/scripts/pre_user_prompt_reminder_check.py` could scan `.windsurf/reminders/*.md`
at session start, parse the YAML frontmatter `due_date`, and if `today >= due_date` print to stderr:
```
[REMINDER] 2026-04-28: ADR-023 formal acceptance due — see .windsurf/reminders/2026-04-28-adr-023-acceptance.md
```
~30 lines of Python. Say the word and I'll add it.
