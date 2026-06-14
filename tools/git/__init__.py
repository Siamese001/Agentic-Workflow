"""Worktree lifecycle tooling (worktree-per-chat companion).

Modules:
  * ``worktree_runtime_links`` — junction/symlink the gitignored runtime-data cache
    dirs from the primary checkout into a fresh worktree (item #2 of the
    worktree-lifecycle streamline). SSOT consumed by the SessionStart hook,
    ``worktree_doctor``, and ``post_setup_worktree``.
  * ``worktree_doctor`` — classify/report every worktree and repair missing runtime
    links (items #2/#4/#6).
  * ``deliver_worktree`` — the standard "deliver" path: rebase on trunk, retest, then
    push/PR (item #5).
"""
