# On-Demand PR Main Publisher

- run_time: 2026-06-20T07:25:10.4600688-04:00
- published PR #428 from codex/automation and merged commit 469a859167 into GitHub main (a4b1656313848c705db59df5d2725b86d01604a).
- rebased onto origin/main, fixed a stale partnership bundle test call, and re-ran the impacted pytest set successfully (169 passed).
- fast-forwarded local main with git update-ref because the separate C:\Git\Agentic-Workflow-FRESH-gk-publish worktree is dirty and retained.
- no worktrees were removed; two untracked plan drafts remain in the publication worktree.

- run_time: 2026-06-20T00:00:00-04:00
- policy update: prior dirty-worktree retention is superseded. Future successful publication runs must finish with `python scripts/governance/verify_single_main_worktree.py --root C:\Git\Agentic-Workflow-FRESH --expected-path C:\Git\Agentic-Workflow-FRESH --fetch --json` reporting PASS.
- success now requires HEAD == origin/main == GitHub main, exactly one clean main worktree at `C:\Git\Agentic-Workflow-FRESH`, no unstaged diff, no staged diff, and strict `codex_readiness.py --git-publication --require-single-main-worktree` PASS.
