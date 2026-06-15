"""Worktree lifecycle tooling for named sibling worktrees.

Modules:
  * ``worktree_runtime_links`` — junction/symlink the gitignored runtime-data cache
    dirs from the primary checkout into a fresh worktree. SSOT consumed by
    ``worktree_doctor`` and ``post_setup_worktree``.
  * ``worktree_doctor`` — classify/report every worktree and repair missing runtime
    links.
  * ``deliver_worktree`` — the standard "deliver" path: rebase on trunk, retest, then
    push/PR (item #5).
"""
