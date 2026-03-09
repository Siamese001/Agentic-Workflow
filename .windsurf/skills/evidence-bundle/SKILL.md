---
name: evidence-bundle
description: Captures raw command outputs into a single phase evidence file using PowerShell Tee-Object. Use when starting a phase, executing commands, or performing post-commit verification. Provides the canonical evidence template, command capture snippets, and post-commit verification block. REQUIRES DEPENDENCY_GRAPH section per §0.
---

# Evidence Bundle Skill

**PREREQUISITE:** `ast-first-gate` skill MUST be invoked first (§0 DEFAULT ANALYSIS MODE).

Provides three artifacts for evidence-first phase execution with mandatory AST dependency graph documentation:

## Files

- **`evidence_template.md`** — Ordered evidence file template with all required sections (phase header, scope declaration, pre-change diff, commands, raw outputs, post-commit block). Use this as the starting structure for every phase evidence file.

- **`command_capture_snippets.ps1`** — Copy-pasteable PowerShell snippets for capturing all phase commands via `Tee-Object -FilePath $E -Append 2>&1`. Includes safe Python invocation patterns and pytest collection + execution commands.

- **`post_commit_verification_block.md`** — Minimal deterministic post-commit verification commands (`git status`, `git show --name-only`, `git show --stat`, `pytest -q`). Run after every commit and capture output into evidence.

## When to use

- At the start of every phase: copy `evidence_template.md` structure.
- For every command executed: use `command_capture_snippets.ps1` patterns.
- After every commit: run `post_commit_verification_block.md` commands.
