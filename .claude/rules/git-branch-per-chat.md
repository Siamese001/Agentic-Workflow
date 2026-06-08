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
| Registration | `.claude/settings.json` `hooks.SessionStart` + `hooks.PreToolUse` | — |

Both hooks are **self-contained** (no `lib.claude_hook_common` dependency) and fail
**soft** when git is unavailable / no branch resolves; the edit gate blocks **hard**
only when the file's owning working tree is genuinely on a protected branch.

## Configuration

| Env var | Effect |
|---|---|
| `BRANCH_PER_CHAT_BYPASS=1` / `WORKTREE_PER_CHAT_BYPASS=1` | Disable both hooks (intentional on-primary change). |
| `BRANCH_PER_CHAT_PROTECTED=main,master,release` | Override the protected-branch set (csv). Default: `main,master`. |
| `CHAT_WORKTREE_ROOT=/abs/path` | Override the worktree root. Default: `<repo-parent>/.chat-worktrees`. |

## Naming

- Branch: `chat/<YYYYMMDD-HHMMSS>-<8-hex-of-session-id>` (stamp = session UTC clock).
- Worktree dir: `<repo-parent>/.chat-worktrees/chat-<stamp>-<hex>`.
- Collisions are uniquified with the hook PID.

## Notes

- The worktree + branch are local only; push/PR when ready via the normal `git`/PR flow,
  from inside the worktree.
- This rule governs **chat isolation**, not commit policy. Commit/push only when the user
  asks, per the operating contract.
- Worktrees are siblings of the primary clone and are reclaimed with the container; remove
  stale ones with `git worktree prune` / `git worktree remove <path>`.
