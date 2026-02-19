---
name: scope-guard
description: Prevents scope drift and contamination during phase execution. Use before editing any files to declare scope and N count, after editing to verify no unexpected files appeared, and when out-of-scope files are detected to execute decontamination. Provides scope precheck, decontamination protocol, and phase revision template.
---

# Scope Guard Skill

Three artifacts for scope discipline:

## Files

- **`scope_precheck.md`** — Run before any edits. Declare exact file list + N count, capture pre-change diff baseline, verify post-edit diff matches declaration. STOP if unexpected files appear.

- **`decontamination_protocol.md`** — Execute when `git diff --name-only HEAD` contains files outside declared scope. Steps: document unexpected files → reset to baseline → restore only declared files → verify clean scope → STOP.

- **`scope_expansion_revision_template.md`** — Short template for producing a Phase Revision artifact when scope expansion is detected and authorized. Fill in before resuming execution.

## When to use

- Before any file edits: run `scope_precheck.md`.
- When unexpected files appear in diff: run `decontamination_protocol.md`.
- When scope must legitimately expand: fill `scope_expansion_revision_template.md` first.
