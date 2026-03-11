---
name: script-sprawl-guard
description: Prevents creation of new runner scripts and wrapper executables. Use when invoking any Python module or agent, when deciding how to add an entrypoint, or when tempted to create a new file to run an existing one. Provides canonical invocation policy and an entrypoint decision tree.
enforcement_layer: both
enforcement_timing: before_work
enforcement_type: behavioural_primary_structural_secondary
---

# Script Sprawl Guard Skill

Two artifacts for zero-sprawl invocation discipline:

## Files

- **`canonical_invocation_policy.md`** — Defines allowed invocation patterns (`python file.py` or `python -m module`), prohibited patterns (new runner files), and the rule for adding `__main__` to a canonical file when none exists.

- **`entrypoint_decision_tree.md`** — Four-branch decision flow: (1) `__main__` exists → invoke directly, (2) `-m` is sanctioned → use `-m`, (3) no entrypoint → add to canonical file only, (4) none apply → STOP, no wrappers.

## When to use

- Before invoking any Python file or module: consult `entrypoint_decision_tree.md`.
- When a file has no `__main__`: follow branch 3 — add to the canonical file, never create a new runner.
- When reviewing a diff for new executables: check against `canonical_invocation_policy.md`.
