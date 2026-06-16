---
name: worktree-per-chat
description: Procedure for the named-workstream worktree isolation workflow: use registered sibling git worktrees whose folder basename exactly equals an agent-owned high-signal branch such as `codex-apps-rg` or `claude-governance-hooks`, never timestamped per-chat branches, and never edit the primary checkout on a protected branch.
metadata:
  enforcement_layer: deterministic
  enforcement_timing: before_work
  enforcement_type: invariant_check
---

# Named Worktree Isolation

This skill operationalizes `git-branch-per-chat.md`, whose historical name is retained for
compatibility. The current model is one registered sibling worktree per durable workstream, not one
worktree per chat. Worktree folder basenames must exactly equal the local branch name, and editable
agent branches must be `codex-<high-signal-scope>` or `claude-<high-signal-scope>`.
Worktrees still provide the file isolation that makes rebases and merges safe while the primary
checkout carries unrelated work.

The edit gate blocks Edit/Write to a protected checkout (`main`/`master`). SessionStart only advises;
it does not create branches, create folders, push, or clean up worktrees.

## When to Invoke

| User intent / trigger | Action |
|---|---|
| Session starts with HEAD on `main`/`master` | Choose or create a named sibling worktree such as `<repo-parent>/<repo-name>-worktrees/codex-apps-rg` on `codex-apps-rg` |
| Edit/Write refused (exit 2) citing the branch guard | Move the edit into an existing named worktree or create one explicitly |
| "Where should this change go?" | Feature CODE -> named workstream worktree. Plan files (`plans/**`) -> primary checkout, regardless of branch |
| Worktrees or branches piling up | Run `python .claude/hooks/prune_merged_chat_worktrees.py --dry-run`; delete only with explicit `--delete-merged` |

## Hard Routing Rules

| Rule | Why |
|---|---|
| Never edit the primary checkout while it is on `main`/`master` | The PreToolUse edit gate blocks it; isolation is still the point |
| Use durable, scope-bearing workstream names, not timestamped or generated adjective-name branches | Branches remain comprehensible and reusable across sessions |
| Match the worktree folder basename exactly to the local branch name | Windows folders cannot represent slash branch namespaces as a single basename |
| Plan files are exempt; write them to the primary checkout's `plans/` | A plan in a worktree can miss the shared SSOT |
| Cleanup is explicit | No SessionStart hook should delete branches or folders while a user is starting work |

## Standard Procedure

1. Inspect existing worktrees: `git worktree list`.
2. Reuse the appropriate named worktree if one exists.
3. If needed, create one explicitly:

   ```bash
   git worktree add ../Agentic-Workflow-FRESH-worktrees/codex-<topic> -b codex-<topic> origin/main
   ```

4. Work and commit inside that worktree.
5. Open a PR or run a deliberate delivery command; do not rely on Stop-hook direct push.
6. Clean up delivered local worktrees only after review:

   ```bash
   python .claude/hooks/prune_merged_chat_worktrees.py --dry-run
   python .claude/hooks/prune_merged_chat_worktrees.py --delete-merged
   ```

## Forbidden Patterns

- Bypassing the guard with `BRANCH_PER_CHAT_BYPASS=1` to edit the primary checkout on main, absent explicit user intent.
- Creating new timestamped `chat/*` branches for ordinary work.
- Creating or continuing editable work on `codex/*`, `claude/*`, `work/*`, or `feat/*` slash namespaces without migrating to `codex-*` or `claude-*`.
- Depending on SessionStart to create or delete worktrees.
- Hand-deleting an unmerged or dirty worktree.

## References

- Rule: `.claude/rules/git-branch-per-chat.md`
- Hooks: `.claude/hooks/session_start_branch_guard.py`, `before_file_edit_branch_guard.py`, `prune_merged_chat_worktrees.py`
- Config envs: `BRANCH_PER_CHAT_BYPASS`, `BRANCH_PER_CHAT_PROTECTED`, `CHAT_WORKTREE_ROOT`, `WORKTREE_IDE_OWNER`
- Sibling skills: `gitkraken`, `scope-containment`; plan placement -> `plan-location.md` rule
