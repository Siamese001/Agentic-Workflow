# L7 boundary open scope

Date: 2026-06-07
Parent plan: `.cursor/plans/l7-auditability-overlap-cleanup-4f8c2d.md`
Follow-up plan: `.cursor/plans/l7-section-shim-legacy-removal-followup-a9c4e2.md`

## Open Scope

| ID | Scope | Resolution |
|---|---|---|
| OS-1 | Stop legacy section shim writes by default | Implemented as an explicit package-finalizer migration mode: compatibility default keeps legacy files; `preferred_only` removes known legacy shim files after preferred mirrors exist. |
| OS-2 | Keep legacy reads during migration | Preserved through `_preferred_or_legacy_ref` and existing downstream legacy readers. |
| OS-3 | Prove package metadata reports migration mode | Covered by focused section evidence package tests. |
| OS-4 | Record closeout receipt and Notion follow-up | Receipt path: `artifacts/certification/apps_rg_l7_open_scope_followup_receipt.json`; Notion row is patched at closeout. |

## Decision

Do not mass-edit every downstream legacy reader in this pass. The safe closure is to make the package finalizer capable of preferred-only output while preserving compatibility-mode defaults for runtime readers that still expect legacy filenames.
