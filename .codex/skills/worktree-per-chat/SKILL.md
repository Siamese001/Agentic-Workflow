---
name: worktree-per-chat
description: Named-workstream git worktree isolation. Use when starting durable editable work, before editing files, or when migrating a legacy branch — keep edits in a registered sibling git worktree whose folder basename exactly equals an agent-owned high-signal branch such as `codex-apps-rg` or `claude-governance-hooks`, never a timestamped per-chat branch, and never the primary checkout on a protected branch.
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

The edit gate blocks Edit/Write to a protected checkout (`main`/`master`). SessionStart and Bash
branch/worktree commands are advisory; they do not create branches, create folders, push, clean up
worktrees, or block branch creation. The hard safety boundary is the file-edit guard.

**Wave reuse rule.** A wave is execution progress inside a durable workstream, not branch identity.
Multiple waves for the same app/plan/scope must continue in the same named worktree branch. Do not
mint `codex-apps-rg-wave4-tests`, `codex-apps-rg-wave5-tests`, etc. Use one durable branch such as
`codex-apps-rg-hotspot-tests` and record wave numbers in the plan, commit message, or receipt.
Create a new worktree only when the app, subsystem, or durable objective changes.

## When to Invoke

| User intent / trigger | Action |
|---|---|
| Session starts with HEAD on `main`/`master` | REUSE the existing named worktree whose workstream matches; create a new sibling (e.g. `<repo-parent>/<repo-name>-worktrees/codex-apps-rg` on `codex-apps-rg`) ONLY on a material scope change |
| Edit/Write refused (exit 2) citing the branch guard | Move the edit into an existing named worktree or create one explicitly |
| "Where should this change go?" | Feature CODE -> named workstream worktree. Plan files (`plans/**`) -> primary checkout, regardless of branch |
| Worktrees or branches piling up | Run `python .codex/hooks/prune_merged_chat_worktrees.py --dry-run`; delete only with explicit `--delete-merged` |

## Hard Routing Rules

| Rule | Why |
|---|---|
| Never edit the primary checkout while it is on `main`/`master` | The PreToolUse edit gate blocks it; isolation is still the point |
| Use durable, scope-bearing workstream names, not timestamped or generated adjective-name branches | Branches remain comprehensible and reusable across sessions |
| Reuse an existing matching worktree; create a new one ONLY on a material scope change | One worktree per durable workstream, not one per chat -- prevents sibling-worktree sprawl |
| Treat later waves in the same plan/workstream as the same scope | Wave numbers are progress metadata; per-wave worktree branches are sprawl |
| Editing an `apps_<x>` file requires an `apps-<x>-<scope>` branch topic (`claude-apps-rg-…`); core/`agentic_core`/infra needs no app segment | The branch self-documents which app a change impacts; the edit guard ties it to the touched path |
| Match the worktree folder basename exactly to the local branch name | Windows folders cannot represent slash branch namespaces as a single basename |
| Plan files are exempt; write them to the primary checkout's `plans/` | A plan in a worktree can miss the shared SSOT |
| Cleanup is explicit and ancestry-gated | No SessionStart hook should delete branches or folders while a user is starting work; deletion waits for exact branch-tip ancestry in `origin/main` |
| Branch creation is advisory at the shell layer | The Bash hook should not force rebaselining or reminting; invalid edit lanes are caught when files are edited |

## Standard Procedure

1. Inspect existing worktrees: `git worktree list`.
2. REUSE the appropriate named worktree if one exists for this workstream -- this is the default. A follow-up chat on the same or overlapping scope continues in the SAME worktree.
3. Create a new one explicitly ONLY when the scope materially changes (a different durable workstream):

   ```bash
   git worktree add ../Agentic-Workflow-FRESH-worktrees/codex-<topic> -b codex-<topic> origin/main
   ```

4. Work and commit inside that worktree.
5. Open a PR or run a deliberate delivery command; do not rely on Stop-hook direct push.
6. For every branch declared done, prove exact ancestry after push:

   ```bash
   git merge-base --is-ancestor <branch> origin/main
   git branch --no-merged origin/main
   ```

   Patch-equivalent `git cherry -v` rows are not enough for cleanup. If work was cherry-picked or
   manually transplanted, record the branch tip in `main` with a deliberate non-squash ancestry merge
   such as `git merge -s ours --no-ff <branch>` before deleting the branch.

7. Clean up delivered local worktrees only after review:

   ```bash
   python .codex/hooks/prune_merged_chat_worktrees.py --dry-run
   python .codex/hooks/prune_merged_chat_worktrees.py --delete-merged
   ```

## Forbidden Patterns

- Bypassing the guard with `BRANCH_PER_CHAT_BYPASS=1` to edit the primary checkout on main, absent explicit user intent.
- Creating new timestamped `chat/*` branches for ordinary work.
- Creating or continuing editable work on `codex/*`, `claude/*`, `work/*`, or `feat/*` slash namespaces without migrating to `codex-*` or `claude-*`.
- Depending on SessionStart to create or delete worktrees.
- Hand-deleting an unmerged, patch-equivalent-only, or dirty worktree.

## References

- Rule: `.codex/rules/git-branch-per-chat.md`
- Hooks: `.codex/hooks/session_start_branch_guard.py`, `before_file_edit_branch_guard.py`, `prune_merged_chat_worktrees.py`
- Config envs: `BRANCH_PER_CHAT_BYPASS`, `BRANCH_PER_CHAT_PROTECTED`, `WORKTREE_IDE_OWNER`
- Sibling skills: `gitkraken`, `scope-containment`; plan placement -> `plan-location.md` rule
