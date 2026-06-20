# Boundary Audit Triggers — stub

> On-demand when touching the core/apps boundary (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged. Run `/core-boundary-audit` when any `agentic_core/` or `*_binding.py` changes, an app literal appears in core, or a PR touches both trees; leakage BLOCKS until migrated (receipt under `artifacts/governance/boundary_receipts/`). Detail: [`core-boundary-audit`](../skills/core-boundary-audit/SKILL.md) + [`boundary-enforcement`](../skills/boundary-enforcement/SKILL.md) skills. Bypass: `BOUNDARY_AUDIT_BYPASS=1`.
