# Worktree-Per-Chat — Never Edit The Primary Checkout On `main`

> ⛔ Every chat/feature works in its own fresh **git worktree** cut from the
> default branch (`main`). Direct edits to the primary checkout while it is on
> `main`/`master` are blocked. Each conversation's work is isolated in its own
> working directory + branch, reviewable as a single PR.
>
> (Renamed from "branch-per-chat" 2026-06-08 per user directive: isolate each
> chat in a dedicated worktree, not just a branch switch in the primary checkout.)

## The Invariant

1. At **session start**, if HEAD is on a protected branch (`main`/`master`),
   a new worktree is created at `<repo-parent>/.chat-worktrees/chat-<stamp>-<hex>`
   on a fresh `chat/<UTC-stamp>-<session-hex>` branch cut from the current tip.
   The assistant is instructed (via `SessionStart` `additionalContext`) to perform
   all work for the chat **inside that worktree** (`cd` in; target files there).
2. **Edit/Write/MultiEdit is gated per-file by the owning working tree's branch.**
   Edits whose owning worktree is on a non-protected branch (i.e. inside the chat
   worktree) are allowed; edits to the primary checkout while it is on a protected
   branch are refused (exit 2) with remediation pointing at the worktree.
3. A chat already operating on a non-protected branch/worktree is left alone.

> **Known constraint (accepted):** a `SessionStart` hook is a subprocess and
> **cannot relocate the running session's CWD** into the new worktree. It creates
> the worktree and emits instructions; the assistant must `cd` into it. The
> edit-gate's per-file branch resolution is what enforces that work lands in the
> worktree, not the primary checkout. The entire `.claude/` governance tree still
> resolves from the primary `$CLAUDE_PROJECT_DIR`; worktrees contain their own
> copy of the tracked tree.

## Enforcement Layers

| Layer | Mechanism | File |
|---|---|---|
| Proactive (auto-worktree) | `SessionStart` hook | `.claude/hooks/session_start_branch_guard.py` |
| Hard block (per-file edit gate) | `PreToolUse` Edit\|Write\|MultiEdit hook | `.claude/hooks/before_file_edit_branch_guard.py` |
| Lifecycle cleanup (auto-reap merged) | `SessionStart` hook | `.claude/hooks/prune_merged_chat_worktrees.py` |
| Registration | `.claude/settings.json` `hooks.SessionStart` + `hooks.PreToolUse` | — |

Both hooks are **self-contained** (no `lib.claude_hook_common` dependency) and fail
**soft** when git is unavailable / no branch resolves; the edit gate blocks **hard**
only when the file's owning working tree is genuinely on a protected branch.

## Configuration

| Env var | Effect |
|---|---|
| `BRANCH_PER_CHAT_BYPASS=1` / `WORKTREE_PER_CHAT_BYPASS=1` | Disable the guard hooks (intentional on-primary change). Also disables auto-reap. |
| `BRANCH_PER_CHAT_PROTECTED=main,master,release` | Override the protected-branch set (csv). Default: `main,master`. |
| `CHAT_WORKTREE_ROOT=/abs/path` | Override the worktree root. Default: `<repo-parent>/.chat-worktrees`. |
| `WORKTREE_MERGE_CLEANUP_BYPASS=1` | Disable only the auto-reap (keep the create/edit guards on). |
| `WORKTREE_MERGE_CLEANUP_DRY_RUN=1` | Auto-reap reports which worktrees it *would* reap, deletes nothing. |
| `WORKTREE_CLEANUP_MIN_AGE_MINUTES=N` | Grace window — never reap a chat worktree whose HEAD is newer than N minutes. Default `0`. |
| `WORKTREE_CLEANUP_TRUNK_REF=origin/main` | The "merged into" trunk ref the reaper checks against. Default `origin/main`. |

## Naming

- Branch: `chat/<YYYYMMDD-HHMMSS>-<8-hex-of-session-id>` (stamp = session UTC clock).
- Worktree dir: `<repo-parent>/.chat-worktrees/chat-<stamp>-<hex>`.
- Collisions are uniquified with the hook PID.

## Lifecycle cleanup — auto-reap merged chat worktrees

> ⛔ Once a chat worktree's branch is fully **merged into `origin/main`** and its tree is
> **clean**, the worktree has served its purpose and is removed automatically at the next
> `SessionStart` (`git worktree remove` + `git branch -d`). Merged + clean ⇒ **zero committed
> work is ever lost** (everything is already on the trunk).

`prune_merged_chat_worktrees.py` reaps a worktree **only** when ALL hold — a hard safety envelope:

| Guard | A worktree is reaped only if… |
|---|---|
| Scope | it lives under the chat root (`.chat-worktrees/`) **and** its branch matches `chat/*`. Long-lived `feat/*` / `codex/*` / `fix/*` worktrees and the primary checkout are **never** eligible. |
| Self | it is **not** the worktree the current session is running in. |
| Merged | its branch is an **ancestor of `origin/main`** (`git merge-base --is-ancestor`). Unmerged work is never touched. |
| Clean | its working tree is **clean** (`git status --porcelain` empty). Uncommitted work is never touched. |
| Age | its HEAD is older than `WORKTREE_CLEANUP_MIN_AGE_MINUTES` (default `0`) — protects a worktree another live chat just created. |

It is **best-effort and fail-soft**: a fetch failure, a worktree-remove failure, or a non-git
environment never blocks session start (always exits 0). Run it on demand in dry-run with
`WORKTREE_MERGE_CLEANUP_DRY_RUN=1 python .claude/hooks/prune_merged_chat_worktrees.py`.

## Notes

- The worktree + branch are local only; push/PR when ready via the normal `git`/PR flow,
  from inside the worktree.
- This rule governs **chat isolation**, not commit policy. Commit/push only when the user
  asks, per the operating contract.
- Worktrees are siblings of the primary clone. Merged+clean chat worktrees are reaped
  automatically (above); reap others manually with `git worktree remove <path>` /
  `git worktree prune`.
