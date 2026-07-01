# PR Publisher Dirty-Worktree Recovery Contract

ProceduralPattern:PRPublisherDirtyWorktreeRecovery

- Fixed recurring stop condition where the on-demand PR publisher treated dirty-worktree intake as a hard TOML/PR-flow audit failure before recovery could preserve and route the work.
- Use `python scripts/governance/codex_publication_audit.py --json --branch-limit 100 --require-pr-flow` for intake; dirty current worktree should produce `status=WARN`, `warnings` containing `current_worktree_dirty`, and `recovery_required=["current_worktree_dirty"]`.
- Use `python scripts/governance/codex_readiness.py --git-publication --require-pr-flow --json` for automation-facing readiness; dirty current worktree should be a WARN that says dirty-worktree recovery is required, not a FAIL.
- Use `--require-single-main-worktree` only for strict final closeout; dirty current worktree is a blocker there until the recovery/cleanup loop clears it.
- Guard tests: `tests/unit/scripts/governance/test_codex_publication_audit.py::test_publication_audit_routes_dirty_current_worktree_to_recovery_with_pr_flow` and `tests/unit/scripts/governance/test_codex_readiness.py::test_git_publication_pr_flow_treats_dirty_worktree_as_recovery_warning`.
- Do not "fix" recurrence by weakening PR-flow TOML validation; invalid `publication_mode`, `allow_direct_main_push`, `require_github_ci_green`, or `allow_bypass_merge` remains a hard `pr_flow_contract_violation`.
- discovered: 2026-06-30, validated: 2026-06-30
