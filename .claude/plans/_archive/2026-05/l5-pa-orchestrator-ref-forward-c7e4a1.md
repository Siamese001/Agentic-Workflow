---
plan_id: l5-pa-orchestrator-ref-forward-c7e4a1
plan_type: bugfix
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# L5 PA orchestrator ref forward (governed PA boundary)

Close `L5CertRefViolation stage=PA_entry ref=''` on executive_summary governed core PA signing: runtime `RouteContract` carried `test:valid:w6` but `runtime_route_to_orchestrator_route` dropped it before `assemble_prompt`.

Parent: ADR-100 / apps_rg spine (`governed_pa_compose`).

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-05-24
NOTION_STATUS: Completed
NOTION_PAGE_ID: 36a27693-f55c-81f0-8818-e423baee6798
NOTION_PLAN_URL: https://www.notion.so/l5-pa-orchestrator-ref-forward-c7e4a1-36a27693f55c81f08818e423baee6798
NOTION_RECONCILED: 2026-05-24
PLAN_COMPLETED: 2026-05-24
PLAN_CREATED: slug=l5-pa-orchestrator-ref-forward-c7e4a1 path=.cursor/plans/l5-pa-orchestrator-ref-forward-c7e4a1.md status=Completed notion_page=36a27693-f55c-81f0-8818-e423baee6798

---

## Wave Summary

| Wave | Focus | Status |
|------|-------|--------|
| W1 | Forward `l5_certification_ref` on C0 OrchRoute + apps_rg adapter; contract tests | DONE |

---

## W1 — Done

- `agentic_core/L0_routing/c0_retrieval/route_contract.py`: optional `l5_certification_ref` on orchestrator `RouteContract`
- `apps_rg/runtime/spine/governed_pa_compose.py`: `runtime_route_to_orchestrator_route` passes ref
- `tests/_apps_contract/test_apps_rg_governed_pa_w5.py`: forward + no `L5CertRefViolation` on `pa_compose_apps_rg`

```bash
pytest tests/_apps_contract/test_apps_rg_governed_pa_w5.py -q
```

PLAN_COMPLETE: plan=l5-pa-orchestrator-ref-forward-c7e4a1 note="OrchRoute l5_certification_ref + governed_pa adapter; 6/6 governed PA tests PASS"
