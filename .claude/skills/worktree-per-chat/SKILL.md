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

**App-scope segment.** When the workstream edits files under an `apps_<x>` package
(`apps_rg`/`apps_lic`/`apps01`/...), the branch topic must name that app first:
`<owner>-apps-<x>-<scope>` (e.g. `claude-apps-rg-competencies-finish`). The app token is the
package name with `_`→`-` (matching the all-hyphen topic contract). Core / `agentic_core` /
infrastructure / governance work touches no `apps_<x>` file and needs no app segment — a plain
high-signal topic such as `claude-governance-hooks` stays valid. The per-file edit guard derives the
requirement from the path of the file being edited, so an app segment is mandated exactly when (and
only when) an `apps_<x>` file is touched.

The edit gate blocks Edit/Write to a protected checkout (`main`/`master`). SessionStart only advises;
it does not create branches, create folders, push, or clean up worktrees.

## When to Invoke

| User intent / trigger | Action |
|---|---|
| Session starts with HEAD on `main`/`master` | REUSE the existing named worktree whose workstream matches; create a new sibling (e.g. `<repo-parent>/<repo-name>-worktrees/codex-apps-rg` on `codex-apps-rg`) ONLY on a material scope change |
| Edit/Write refused (exit 2) citing the branch guard | Move the edit into an existing named worktree or create one explicitly |
| "Where should this change go?" | Feature CODE -> named workstream worktree. Plan files (`plans/**`) -> primary checkout, regardless of branch |
| Worktrees or branches piling up | Run `python .claude/hooks/prune_merged_chat_worktrees.py --dry-run`; delete only with explicit `--delete-merged` |

## Hard Routing Rules

| Rule | Why |
|---|---|
| Never edit the primary checkout while it is on `main`/`master` | The PreToolUse edit gate blocks it; isolation is still the point |
| Use durable, scope-bearing workstream names, not timestamped or generated adjective-name branches | Branches remain comprehensible and reusable across sessions |
| Reuse an existing matching worktree; create a new one ONLY on a material scope change | One worktree per durable workstream, not one per chat -- prevents sibling-worktree sprawl |
| Editing an `apps_<x>` file requires an `apps-<x>-<scope>` branch topic (`claude-apps-rg-…`); core/`agentic_core`/infra needs no app segment | The branch self-documents which app a change impacts; the edit guard ties it to the touched path |
| Match the worktree folder basename exactly to the local branch name | Windows folders cannot represent slash branch namespaces as a single basename |
| Plan files are exempt; write them to the primary checkout's `plans/` | A plan in a worktree can miss the shared SSOT |
| Cleanup is explicit | No SessionStart hook should delete branches or folders while a user is starting work |

## Standard Procedure

1. Inspect existing worktrees: `git worktree list`.
2. REUSE the appropriate named worktree if one exists for this workstream -- this is the default. A follow-up chat on the same or overlapping scope continues in the SAME worktree.
3. Create a new one explicitly ONLY when the scope materially changes (a different durable workstream):

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
