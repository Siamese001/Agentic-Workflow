# Graph skills hardening — P2-W0 gap inventory

**Plan:** [graph-skills-hardening-f3a8c1](../../.cursor/plans/graph-skills-hardening-f3a8c1.md)  
**Wave:** P2-W0 (inventory/planning only)  
**Machine-readable:** [graph_skills_hardening_gap_inventory.json](graph_skills_hardening_gap_inventory.json)  
**Validator:** `python -m apps_rg.fact_inventory.validate_p2_w0_graph_skills_gap_inventory`

**Part 1 preserved (not modified this wave):**

| Receipt | Status |
|---------|--------|
| [career_track_p1_w4_closeout_receipt.json](career_track_p1_w4_closeout_receipt.json) | C0.3 **BOUND** |
| [career_track_p1_w5_track_balanced_sections_receipt.json](career_track_p1_w5_track_balanced_sections_receipt.json) | `live_competencies_runtime_modified=false` |

**Predecessor PASS pattern:** [executive_summary_graph_only_generation_live_proof.json](executive_summary_graph_only_generation_live_proof.json)

---

## P2-W0 scope (explicit)

- Inventory and gap matrix only
- **No** competencies graph proof pool (P2-W1)
- **No** live competencies runtime behavior changes
- **No** competencies X3_ALLOW claim
- **No** `agentic_core` edits
- `broad_skills_ledger` documented as **current-state gap**, not future product skills authority

---

## Current competencies path (file map)

| Concern | SSOT module / function |
|---------|------------------------|
| Canonical CLI | `python -m apps_rg --section competencies` → `apps_rg/__main__.py` |
| Lane entry | `apps_rg/runtime/sections/competencies_lane.py` |
| Execution | `apps_rg/runtime/sections/competencies_lane_execution.py::run_competencies_lane_execution` |
| Proof pool load | `apps_rg/runtime/proof_pool_lane_integration.py::load_section_proof_for_lane` |
| Proof pool resolve | `apps_rg/runtime/proof_pool_resolver.py::resolve_section_proof_pool` |
| Competencies ledger plan | `proof_pool_resolver.py::_build_competencies_ledger_plan` → `selection_method=broad_skills_ledger_competencies` |
| Prompt compile | `apps_rg/runtime/sections/competencies_pa.py::compile_competencies_prompt` |
| C0 / FEC | `wire_section_fec_bridge_for_lane` + `build_c0_proof_support_blob` (ledger bullets) |
| Post-parse repair | `apps_rg/runtime/sections/competencies_lane_api.py` (structured repairs; **not** graph-only) |
| X2 | `apps_rg/runtime/validators/competencies_x2.py::run_competencies_x2_gates` |
| X1D | `apps_rg/runtime/judges/competencies_x1d.py` (`COMPETENCIES_RUBRIC`) |
| X3 | `apps_rg/runtime/exit/competencies_x3.py` |
| Runtime artifacts | `artifacts/apps_rg/runtime_proofs/competencies/<provider>/<run_id>/` |

**Partial graph touch today:** `competencies_pa.py` may inject `VERIFIED_SKILL_INVENTORY_PROJECTION` when proof metadata marks graph present — but **claim facts** still come from broad-skills ledger slice, not graph-only proof pool.

---

## Executive summary graph-only pattern (reference)

| Layer | Reference |
|-------|-----------|
| Proof pool | `proof_pool_resolver.py::_resolve_executive_summary_graph_only_proof_pool` |
| Track expansion | `apps_rg/fact_inventory/track_weighted_graph_expansion.py` |
| C0.3 | `apps_rg/runtime/c03_graphrag_bound.py` |
| PA guardrails | `executive_summary_pa.py::format_graph_only_quality_guardrails_block` |
| Repair | `exec_summary_graph_only_quality.py` |
| Validator | `validate_exec_summary_graph_only_generation.py` |
| X1D | `executive_summary_judge_packet.py::GRAPH_ONLY_GRADE_ONLY_RUBRIC` |
| Live proof | [executive_summary_graph_only_generation_live_proof.json](executive_summary_graph_only_generation_live_proof.json) |

---

## Gap matrix (summary)

| Capability | Exec (PASS) | Competencies (today) | P2 wave |
|------------|-------------|----------------------|---------|
| Proof pool authority | `augmented_skills_graph` | `broad_skills_ledger_competencies` | P2-W1 |
| C0.3 binding | BOUND | NOT_BOUND | P2-W2 |
| Shared validator | yes | missing | P2-W3 |
| X2 metric/skill locality | repair + gates | ID membership only | P2-W4 |
| PA graph guardrails | full block | partial projection | P2-W5 |
| Graph-only repair | yes | dispatch repairs only | P2-W6 |
| X1D graph rubric | GRADE_ONLY graph | generic advisory | P2-W7 |
| Contract + validator | yes | missing | P2-W8 |
| Live X3_ALLOW proof | documented PASS | not proven | P2-W9 |

Full rows: [graph_skills_hardening_gap_inventory.json](graph_skills_hardening_gap_inventory.json) → `gap_matrix`.

---

## P2-W1 … P2-W9 targets

See JSON `p2_wave_targets` for per-wave: `target_files`, `intended_behavior`, `acceptance_test`, `required_receipt_or_artifact`, `non_claims`.

**Next wave:** P2-W1 — competencies graph-only proof pool in `proof_pool_resolver.py`.

---

## Failure modes to port (from exec-summary root cause)

| Mode | Exec-summary fix | Competencies action |
|------|------------------|---------------------|
| Unsupported % | `allowed_percent_tokens` + repair | P2-W4, P2-W6 |
| Causal merge | separate claim rows | P2-W4, P2-W6 |
| Credential inventory | omit | P2-W6 |
| X2 false PASS on ID only | repair + judges | P2-W4, P2-W6, P2-W7 |

Source: [executive_summary_generation_quality_root_cause.json](executive_summary_generation_quality_root_cause.json)
