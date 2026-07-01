# Scheduled Run Branching Recommendations

Generated: 2026-07-01

This is a recommendation-only report. It does not change any
`.codex/automations/**/automation.toml` contract.

## Scope

Approved scheduled automation TOMLs are files under `.codex/automations/` with
all of:

- `kind = "cron"`
- `status = "ACTIVE"`
- `rrule = "..."`

`apps-rg-c03-graph-full-override/automation.toml` is excluded. It lacks the
scheduled-run fields above and is an unapproved PR automation artifact, not an
approved scheduled run.

## Default Policy

- Read-only or artifact-producer runs may use the clean primary checkout on
  `main` when the prompt explicitly requires canonical repo-root outputs.
- Edit-capable runs should use one durable same-name worktree and branch:
  `C:\Git\Agentic-Workflow-FRESH-worktrees\<branch>` on `<branch>`.
- Use `codex-<durable-scope>` branch names, never `codex/<scope>`.
- Scheduled Codex runs that rely on the repo edit guard must run with
  `WORKTREE_IDE_OWNER=codex`; otherwise the guard defaults to `claude-...`
  branch ownership.
- Do not create per-run, timestamped, or per-wave branches by default.
- Reuse the same worktree for the same durable automation lane until it is
  merged, proven ancestor-contained in `origin/main`, and explicitly cleaned.

## Recommendations

| Automation | Branch / Worktree Recommendation | Rationale |
|---|---|---|
| `weekly-adg-audit-and-burndown` | No feature branch by default. Run from clean `C:\Git\Agentic-Workflow-FRESH` on `main` / `origin/main`. | It is the canonical ADG handoff producer and writes the downstream receipt/artifacts expected from the primary repo root. Stop on dirty or ambiguous root state. |
| `adg-p0-blocker-burndown` | `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-p0-blocker-burndown` on branch `codex-adg-p0-blocker-burndown`. | P0 is an edit-capable durable severity lane. Prefer one stable lane branch over `codex/adg-p0-blocker-burndown-*`. |
| `adg-p1-ratchet-burndown` | `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-p1-ratchet-burndown` on branch `codex-adg-p1-ratchet-burndown`. | P1 is an edit-capable durable severity lane. Reuse the same branch across ratchet waves. |
| `adg-bcg-p2-next-action` | `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-bcg-p2-next-action` on branch `codex-adg-bcg-p2-next-action`. | P2 should not share publisher scratch space; it has its own evidence chain and publication lifecycle. |
| `adg-p3-promotion-hygiene` | `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-p3-promotion-hygiene` on branch `codex-adg-p3-promotion-hygiene`. | P3 is smaller than P0/P1/P2 but still edit-capable when a promotion candidate qualifies. |
| `on-demand-pr-main-publisher` | No default publication branch. Use the selected source branch, or create a temporary `codex-publish-<scope>` / `codex-recovery-<scope>` branch only after intake proves it is needed. | The publisher is a publication/recovery orchestrator. Its success criteria require exact branch-tip ancestry and final single-main-worktree closeout. |
| `weekly-svp-readme-documentation-refresh` | Audit/plan-only: no branch. Approved docs edits: `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-docs-readme-refresh` on branch `codex-docs-readme-refresh`. | Documentation review can run read-only, but edits should be isolated in one durable docs workstream instead of `codex/docs-readme-refresh-YYYYMMDD`. |

## Non-Scheduled / Excluded

| Automation File | Recommendation |
|---|---|
| `apps-rg-c03-graph-full-override/automation.toml` | Do not include in scheduled-run defaults. Treat as an unapproved PR automation artifact unless explicitly approved and converted into a scheduled contract with `id`, `kind`, `status`, and `rrule`. If it is ever approved, migrate its branch from `codex/apps-rg-c03-graph-full-override` to `codex-apps-rg-c03-graph-full-override`. |

## Validation

Validation run: 2026-07-01 from branch
`codex-scheduled-run-branching-recommendations`.

The smoke test set `WORKTREE_IDE_OWNER=codex`, created checked-out throwaway
worktrees for branches that did not already exist, ran the repo edit guard
against each branch/path pair, verified clean status, then removed the test
worktrees and deleted the temporary branches with `git branch -d`.

| Branch | Result |
|---|---|
| `codex-adg-p1-ratchet-burndown` | PASS: worktree creation, branch name, folder basename, clean status, and edit guard. |
| `codex-adg-bcg-p2-next-action` | PASS: worktree creation, branch name, folder basename, clean status, and edit guard. |
| `codex-adg-p3-promotion-hygiene` | PASS: worktree creation, branch name, folder basename, clean status, and edit guard. |
| `codex-docs-readme-refresh` | PASS: worktree creation, branch name, folder basename, clean status, and edit guard. |
| `codex-publish-test-scope` | PASS: worktree creation, branch name, folder basename, clean status, and edit guard. |
| `codex-recovery-test-scope` | PASS: worktree creation, branch name, folder basename, clean status, and edit guard. |
| `codex-adg-p0-blocker-burndown` | PARTIAL: existing worktree branch/path and edit guard pass, but the current worktree is dirty, so the scheduled run should stop or clean/preserve before editing. |

Post-test cleanup check: temporary test worktrees and branches were removed.
Existing worktrees were left untouched.
