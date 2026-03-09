---
name: scope-guard
description: Prevents scope drift and contamination during phase execution using AST dependency graph analysis (§3.4, §3.7). Use before editing any files to build dependency graph and declare graph-justified scope, after editing to verify no unexpected files appeared, and when out-of-scope files are detected to execute decontamination. Provides scope precheck, decontamination protocol, and phase revision template.
---

# Scope Guard Skill

**PREREQUISITE:** `ast-first-gate` skill MUST be invoked first (§0 DEFAULT ANALYSIS MODE).

Three artifacts for scope discipline with mandatory dependency graph backing:

## Files

- **`scope_precheck.md`** — Run before any edits. **MANDATORY: Build AST dependency graph first (§3.4).** Declare exact file list + N count with graph justification for each file (§3.7), capture pre-change diff baseline, verify post-edit diff matches declaration. STOP if unexpected files appear or files lack graph justification.

- **`decontamination_protocol.md`** — Execute when `git diff --name-only HEAD` contains files outside declared scope. Steps: document unexpected files → reset to baseline → restore only declared files → verify clean scope → STOP.

- **`scope_expansion_revision_template.md`** — Short template for producing a Phase Revision artifact when scope expansion is detected and authorized. Fill in before resuming execution.

## When to use

- Before any file edits: run `scope_precheck.md` (includes mandatory dependency graph build).
- When unexpected files appear in diff: run `decontamination_protocol.md`.
- When scope must legitimately expand: fill `scope_expansion_revision_template.md` first.

## Constitutional Requirements Enforced

- **§3.4:** AST dependency graphs are PRIMARY and REQUIRED analysis primitive
- **§3.5:** Low-signal search (grep/regex) FORBIDDEN as primary analysis method
- **§3.7:** Each changed file MUST be justified by dependency graph
- **§4.4:** Before any code edit, MUST determine graph-backed impact analysis
