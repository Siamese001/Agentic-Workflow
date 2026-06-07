# Branch-Per-Chat — Never Edit On `main`

> ⛔ Every chat works on its own fresh branch cut from the default branch
> (`main`). Direct edits to `main`/`master` are blocked. This keeps each
> conversation's work isolated and reviewable as a single branch/PR.

## The Invariant

1. At **session start**, if HEAD is on a protected branch (`main`/`master`),
   a new `chat/<UTC-stamp>-<session-hex>` branch is created off the current tip
   and checked out. Uncommitted work is carried onto the new branch.
2. While HEAD is on a protected branch, **any Edit/Write/MultiEdit is refused**
   (exit 2) with a remediation instruction.
3. A chat already on a non-protected branch is left alone — it is already
   isolated from `main`.

## Enforcement Layers

| Layer | Mechanism | File |
|---|---|---|
| Proactive (auto-branch) | `SessionStart` hook | `.claude/hooks/session_start_branch_guard.py` |
| Hard block (edit gate) | `PreToolUse` Edit\|Write\|MultiEdit hook | `.claude/hooks/before_file_edit_branch_guard.py` |
| Registration | `.claude/settings.json` `hooks.SessionStart` + `hooks.PreToolUse` | — |

Both hooks fail **soft** when git is unavailable or the repo has no branch, and
**hard** (block) only on the edit path when HEAD is genuinely on a protected
branch.

## Configuration

| Env var | Effect |
|---|---|
| `BRANCH_PER_CHAT_BYPASS=1` | Disable both hooks (intentional on-`main` change). |
| `BRANCH_PER_CHAT_PROTECTED=main,master,release` | Override the protected-branch set (csv). Default: `main,master`. |

## Branch Naming

`chat/<YYYYMMDD-HHMMSS>-<8-hex-of-session-id>` — stamp derived from the HEAD
commit date, hex from the Claude Code `session_id`. Collisions are uniquified
with the hook PID.

## Notes

- The auto-created branch is local only; push/PR when ready via the normal
  GitKraken/`git` flow.
- This rule governs **chat isolation**, not commit policy. Commit/push only when
  the user asks, per the operating contract.
