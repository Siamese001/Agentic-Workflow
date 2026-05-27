# C0.1–C0.7 Runtime Hardening Closeout (2026-05-27)

**Plan:** `harden-c01-c07-apps-rg-core-c0-binding` (integrated into `graph-skills-deferred-followup-d7f2a8` W1 REAL_LLM)

## Summary

Closed the runtime proof gap between apps_rg evidence-room C0.1–C0.7 and agentic_core C0.3 graph-skills binding. Brown SVP `executive_summary` REAL_LLM run now emits live graph receipts (`ref:graph:traverse:*`, `canonical_c0_3_graph_claimed: true`).

## Code changes

| Seam | Change |
|------|--------|
| [c0_fec_compose.py](apps_rg/runtime/spine/c0_fec_compose.py) | After evidence room, always invoke `invoke_section_spine_c0_retrieve`; overlay core C0.3 via `apply_spine_c03_overlay_to_bridge_doc` (preserves `producer_stage=section_c0_evidence_room`) |
| [section_c0_retrieve.py](apps_rg/runtime/spine/section_c0_retrieve.py) | New `apply_spine_c03_overlay_to_bridge_doc` — DS-11 spine graph authority without replacing evidence-room producer |
| [section_c0_graph_lane_ensure.py](apps_rg/runtime/spine/section_c0_graph_lane_ensure.py) | Belt-and-suspenders `ensure_section_c0_graph_lane_receipt` |
| [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py) | Calls ensure after `wire_spine_c0_fec_for_section` |
| [audit_c01_c07_graph_skills_apps_rg.py](tools/cursor/audit_c01_c07_graph_skills_apps_rg.py) | Concentration guard (C0.3/C0.4 ≥2 file hits), runtime proof scan, exec_summary emit check |

## Proof

```text
STATUS: PASS
FILES_CHANGED:
- [c0_fec_compose.py](apps_rg/runtime/spine/c0_fec_compose.py)
- [section_c0_retrieve.py](apps_rg/runtime/spine/section_c0_retrieve.py)
- [section_c0_graph_lane_ensure.py](apps_rg/runtime/spine/section_c0_graph_lane_ensure.py)
- [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)
- [audit_c01_c07_graph_skills_apps_rg.py](tools/cursor/audit_c01_c07_graph_skills_apps_rg.py)
- [test_apps_rg_c0_subphase_bindings.py](tests/_apps_contract/test_apps_rg_c0_subphase_bindings.py)
- [test_apps_rg_l0_graph_traverse_policy_active.py](tests/_apps_contract/test_apps_rg_l0_graph_traverse_policy_active.py)
- [test_c0_evidence_room_generated_lanes_e2e.py](tests/_apps_contract/test_c0_evidence_room_generated_lanes_e2e.py)
COMMANDS_RUN:
- pytest tests/_apps_contract/test_apps_rg_c0_subphase_bindings.py tests/_apps_contract/test_apps_rg_l0_graph_traverse_policy_active.py -o addopts= -> 15 passed
- python tools/cursor/audit_c01_c07_graph_skills_apps_rg.py -> status PASS
- CHROMA_PERSIST_DIR=data/cache/chromadb python -m apps_rg --section executive_summary ... -> exit 0, REAL_LLM
TESTS_GATES:
- contract tests -> 15 passed
- audit -> PASS
ARTIFACTS:
- [c0_graph_lane_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_062524/c0_graph_lane_receipt.json)
- [section_spine_c0_retrieve_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_062524/section_spine_c0_retrieve_receipt.json)
- [graph_skills_deferred_followup_w1_real_llm_receipt.json](docs/reports/apps_rg/graph_skills_deferred_followup_w1_real_llm_receipt.json)
- [c01_c07_graph_skills_apps_rg_audit.json](docs/reports/apps_rg/c01_c07_graph_skills_apps_rg_audit.json)
REPORTS_GENERATED:
- [c01_c07_runtime_hardening_closeout_20260527.md](docs/reports/apps_rg/c01_c07_runtime_hardening_closeout_20260527.md)
- [graph_skills_deferred_followup_w1_real_llm_receipt.json](docs/reports/apps_rg/graph_skills_deferred_followup_w1_real_llm_receipt.json)
NOTES:
- Product X3 remains X3_REVIEW_JUDGE_SOFT_FAIL (Anthropic judge) — orthogonal to C0 binding scope per plan risk R2.
- 7-lane LIVE_X3 sweep unchanged (d7f2a8 W2).
```
