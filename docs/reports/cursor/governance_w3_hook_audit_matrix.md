# W3 Hook audit matrix

Generated: 2026-05-26T19:27:03.928728+00:00

**Strategy:** dispatcher (`after_agent_governance_dispatch.py`)
**Scripts inventoried:** 30

| Disposition | Count |
|-------------|-------|
| hook_required | 17 |
| ci_required | 0 |
| manual_only | 13 |
| obsolete_candidate | 0 |
| duplicate_candidate | 1 |

## Matrix (summary)

- `.cursor/scripts/post_cursor_agent_adg_audit.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_ag_queue_drain_audit.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_ag_queue_seed_capture.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_ask_user_question_packet_audit.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_author_gate_capture.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_author_gate_miss_detector.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_author_gate_pipeline_audit.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_author_gate_schema_audit.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_author_gate_ui_audit.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_deferred_scope_capture.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_dispatch.py` → **hook_required** (not_in_after_agent_chain)
- `.cursor/scripts/post_cursor_agent_fortknox_integrity_audit.py` → **manual_only** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_long_command_audit.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_mcp_hygiene_audit.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_mcp_orphan_reap.py` → **manual_only** (not_in_after_agent_chain)
- `.cursor/scripts/post_cursor_agent_mcp_preflight_audit.py` → **manual_only** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_next_step_capture.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_next_step_miss_detector.py` → **manual_only** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_notion_plan_identity_audit.py` → **manual_only** (not_in_after_agent_chain)
- `.cursor/scripts/post_cursor_agent_plan_evidence_gate.py` → **manual_only** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_plan_lifecycle_audit.py` → **manual_only** (not_in_after_agent_chain)
- `.cursor/scripts/post_cursor_agent_plan_registration_capture.py` → **manual_only** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_plan_scope_audit.py` → **manual_only** (not_in_after_agent_chain)
- `.cursor/scripts/post_cursor_agent_plan_wave_summary_audit.py` → **manual_only** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_resource_budget_audit.py` → **manual_only** (not_in_after_agent_chain)
- `.cursor/scripts/post_cursor_agent_router_decision_audit.py` → **manual_only** (not_in_after_agent_chain)
- `.cursor/scripts/post_cursor_agent_scope_drift_detector.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_wave_completion_audit.py` → **manual_only** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_wave_lifecycle_capture.py` → **hook_required** (wired_via_governance_dispatch)
- `.cursor/scripts/post_cursor_agent_writeback_audit.py` → **hook_required** (wired_via_governance_dispatch)
