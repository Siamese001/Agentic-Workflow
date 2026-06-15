# agentic_core Static Architecture Law — stub

> On-demand when editing `agentic_core/` (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged. Core is app-agnostic: no `if app_id ==`, no `apps_*` literals, no app routes/cache/Exit/thresholds in core; core additions need a `CoreAdditionAuthorGateReceipt` + `plan_type: platform_core_change`. Detail: [`boundary-enforcement`](../skills/boundary-enforcement/SKILL.md) skill, `agentic_core/AGENTS.md`. Enforced: `test_agentic_core_static_boundary.py`, `test_no_app_specific_literals_in_core.py`.
