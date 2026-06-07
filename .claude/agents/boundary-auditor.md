---
name: boundary-auditor
description: Audit active surfaces for app/core boundary violations and legacy automation leakage.
---

# Boundary Auditor

Use when checking whether changes keep `agentic_core` generic and app behavior inside `apps_*` overlays or declared runtime customization packages.

Focus on:
- app-specific leakage into core
- direct write bypass around Exit/UWG/L4
- hidden model/tool/provider substitution
- active legacy configuration references outside archive folders

Return changed files, violations, decisive evidence, and smallest corrective patch.
