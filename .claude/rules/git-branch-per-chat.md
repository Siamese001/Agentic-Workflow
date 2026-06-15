# Worktree-Per-Chat — stub

> On-demand (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged (hook-driven). **Invariant:** every chat works in its own git worktree on a `chat/*` branch cut from `origin/main`; never edit the primary checkout while it is on `main`/`master`. Detail: [`worktree-per-chat`](../skills/worktree-per-chat/SKILL.md) skill (lifecycle/delivery/reaping/env). Enforced: `session_start_branch_guard.py`, `before_file_edit_branch_guard.py`, `prune_merged_chat_worktrees.py`, `auto_deliver_on_scope_complete.py`. Bypass: `WORKTREE_PER_CHAT_BYPASS=1`.
