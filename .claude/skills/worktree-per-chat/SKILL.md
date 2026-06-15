---
name: worktree-per-chat
description: Procedure for the worktree-per-chat isolation workflow: every chat works in its own registered sibling git worktree on a `feat/*` branch cut from main, never editing the primary checkout on a protected branch. Invoke when a session starts on main/master, when an edit is blocked by the branch guard, when reconciling where work should land, or when cleaning up merged chat worktrees.
metadata:
  enforcement_layer: deterministic
  enforcement_timing: before_work
  enforcement_type: invariant_check
---

# Worktree-Per-Chat Isolation

This skill operationalizes `git-branch-per-chat.md`. Each conversation is isolated in its own git
registered sibling worktree + `feat/*` branch so its work is reviewable as a single PR and never collides with the
primary checkout on `main`. The edit gate blocks Edit/Write to the primary checkout while it is on a
protected branch; this skill explains how to satisfy it instead of fighting it.

**Sibling skills:** See the `plan-location.md` rule for plan-file placement (plans always land in the
*primary* checkout's `plans/`, exempt from this guard); `gitkraken` for PR creation, `scope-containment`
for what belongs in the active scope. This skill is specifically about *where the working tree lives*.

## When to Invoke

| User intent / trigger | Action |
|---|---|
| Session starts with HEAD on `main`/`master` | A registered sibling worktree is auto-created at `<repo-parent>/<repo-name>-chat-<stamp>-<hex>` on `feat/chat-<stamp>-<hex>`; `cd` into it and target files there |
| Edit/Write refused (exit 2) citing the branch guard | The file's owning worktree is on a protected branch — move the edit into the chat worktree |
| "Where should this change go?" | Feature CODE → chat worktree. Plan files (`plans/**`) → primary checkout, regardless of branch |
| Merged chat worktrees piling up | Registered sibling worktrees auto-reap at next SessionStart when merged into `origin/main` AND clean; otherwise `git worktree remove <path>` |

## Hard Routing Rules (do not violate)

| Rule | Why |
|---|---|
| Never edit the primary checkout while it is on `main`/`master` | The PreToolUse edit gate blocks it (exit 2); isolation is the whole point |
| Plan files are exempt — always write to the primary checkout's `plans/` | A plan in an ephemeral worktree never reaches the shared SSOT (`plan-location.md`) |
| The `.claude/` governance tree resolves from the primary `$CLAUDE_PROJECT_DIR` | A SessionStart hook cannot relocate the running session's CWD — the per-file branch gate is what enforces landing in the worktree |
| Only reap a chat worktree when merged-into-`origin/main` AND clean | Guarantees zero committed work is ever lost |

## Standard Procedure

1. **Detect state** — at session start, if HEAD is on a protected branch, the guard creates the registered sibling worktree + `feat/chat-<UTC-stamp>-<session-hex>` branch and emits instructions.
2. **Enter the worktree** — `cd` into the printed `<repo-parent>/<repo-name>-chat-*` path; target all feature edits there.
3. **Route plans separately** — write any `plans/<slug>-<6hex>.md` to the *primary* checkout's `plans/`, never the worktree copy.
4. **Work + commit** inside the worktree on its `feat/*` branch (commit/push only when the user asks).
5. **Open a PR** from the worktree branch when ready; merged+clean worktrees auto-reap next session.

## Forbidden Patterns

- ❌ Bypassing the guard with `BRANCH_PER_CHAT_BYPASS=1` to edit the primary checkout on main, absent explicit user intent.
- ❌ Writing a plan file into a feature worktree's `plans/` directory (it will be reaped, plan lost).
- ❌ Hand-deleting an unmerged or dirty chat worktree (the reaper refuses these for a reason).
- ❌ Assuming a SessionStart hook changed your CWD — verify with `pwd`; the hook only creates + instructs.

## References

- Rule: `.claude/rules/git-branch-per-chat.md`
- Hooks: `.claude/hooks/session_start_branch_guard.py`, `before_file_edit_branch_guard.py`, `prune_merged_chat_worktrees.py`
- Config envs: `BRANCH_PER_CHAT_BYPASS`, `BRANCH_PER_CHAT_PROTECTED`, `CHAT_WORKTREE_ROOT`, `WORKTREE_BRANCH_PREFIX`, `WORKTREE_DIR_PREFIX`, `WORKTREE_MERGE_CLEANUP_DRY_RUN`
- Sibling skills: `gitkraken`, `scope-containment` · plan placement → `plan-location.md` rule
- Plan-location exemption: `.claude/rules/plan-location.md`
