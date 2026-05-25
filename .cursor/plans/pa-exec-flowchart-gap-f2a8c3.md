---
plan_id: pa-exec-flowchart-gap-f2a8c3
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "dec_19e55e81295a26123"
dod_exempt: false
---

# apps_rg governed spine convergence (U0 → L6 + PA)

Converge **apps_rg** onto spine REQ parents: apps_* **owns domain config and prompt content**; **agentic_core** **ingests the domain packet at U0** and runs **one governed pipeline** per layer (no section vs integrated bypass).

**Full spine gap analysis:** [apps_rg_spine_req_gap_analysis_20260523.md](../docs/reports/apps_rg/apps_rg_spine_req_gap_analysis_20260523.md)  
**Machine audit:** [apps_rg_spine_req_gap_audit.json](../artifacts/apps_rg/plans/apps_rg_spine_req_gap_audit.json)  
**PA drill-down:** [pa_exec_flowchart_gap_analysis_20260523.md](../docs/reports/apps_rg/pa_exec_flowchart_gap_analysis_20260523.md)  
**v40 overlay:** [apps_rg_v40_spine_gap_analysis_20260523.md](../docs/reports/apps_rg/apps_rg_v40_spine_gap_analysis_20260523.md)  
**Closed (E0 only):** [apps-rg-pa-ssot-gap-b8e4f1.md](apps-rg-pa-ssot-gap-b8e4f1.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: done
LAST_COMPLETED_WAVE: W8-followup
LAST_UPDATED: 2026-05-23
NOTION_STATUS: Completed
NOTION_PLAN_URL: https://www.notion.so/pa-exec-flowchart-gap-f2a8c3-36927693f55c8138afb7fe72202f206a
DISK_SSOT: .cursor/plans/pa-exec-flowchart-gap-f2a8c3.md

PLAN_CREATED: slug=pa-exec-flowchart-gap-f2a8c3 path=.cursor/plans/pa-exec-flowchart-gap-f2a8c3.md status=Not Started notion_page=36927693-f55c-8138-afb7-fe72202f206a
SCOPE_EXPANSION: 2026-05-23 expanded from PA-only to full U0-L6 + governed PA per user architecture target

---

## Context (SCQA)

- **Situation** — REQ parents exist for U0–L6 (`01`–`06`, `03A`, `03B`). apps_rg has bindings that emit core contracts. E0 YAML hydration is closed. Other apps (e.g. apps_research) ingest `RuntimeCustomizationPackage` at U0.
- **Complication** — Product has **two paths** (section CLI vs integrated). U0 inlines profile refs instead of core package binding. PA/L2/Exit on section paths bypass core engines, receipts, HMAC, and spine X3.
- **Question** — How do we bind apps_rg domain logic to agentic_core generic pipelines without app leakage in core?
- **Answer** — W0 Author-Gate → W1 U0 package → W2 unify entry (one path) → W3–W7 layer bridges → W8 CI/OTEL proof.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Architecture + Author-Gate | ✅ DONE | — | plan + gap doc |
| W1 | U0: core package ingest + RejectedRequest | ✅ DONE | test_apps_rg_u0_package_ingest | package yaml + u0_binding |
| W2 | One product path (section → spine front) | ✅ DONE | test_one_spine_inventory + front_bridge | section_front_spine_bridge |
| W3 | L1/L0 receipts + route HMAC | ✅ DONE | test_apps_rg_l1_l0_w3_evidence | l1_plan_evidence, l0_route_evidence, contracts |
| W4 | C0 spine FEC on all lanes | ✅ DONE | test_apps_rg_spine_c0_w4 | section_c0_retrieve + C0_graph_lane_deferral |
| W5 | PA: core pipeline + domain slot build | ✅ DONE | test_apps_rg_governed_pa_w5 | governed_pa_compose, pa_binding, orchestrator fix |
| W6 | L2 seal + Exit one X3 | ✅ DONE | test_apps_rg_governed_l2_exit_w6 + test_one_spine_exit_receipt_w6 | governed_l2_exit_compose, exit_binding, section_x3_finalize |
| W7 | L6 exhaust + shadow ingest | ✅ DONE | test_apps_rg_governed_l6_shadow_w7 + test_one_spine_runtime_exhaust_w7 | governed_l6_shadow_compose, l6_handoff_packet gate |
| W8 | OTEL spans + REQ CI ratchet | ✅ DONE | test_apps_rg_spine_convergence_w8 | span_contracts checklist, apps_rg_spine_req_gap_audit, check_apps_rg_spine_convergence_w8 |
| W8-followup | Deferred scope + one-pipeline E2E | ✅ DONE | test_apps_rg_deferred_scope_followup + test_apps_rg_one_pipeline_e2e | section core PA sign, l2_handoff, spine_span_emit; harness E2E 20/20 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Bridge architecture record (U0 pkg + PA orchestrator) | ✅ DONE |
| W1.1 | `runtime_customization_package.yaml` + registry | ✅ DONE |
| W1.2 | `u0_validate_apps_rg` → `u0_runtime_package_binding` | ✅ DONE |
| W2.1 | Section lanes through U0→L1→L0 front bridge | ✅ DONE |
| W5.1 | `assemble_prompt` after apps_rg slot compile | ✅ DONE (integrated); section BOM receipt stub |
| W6.1 | `SealedL2Artifact` + `ExitEvalPipeline` on section | ✅ DONE |

---

## Gap register (spine REQ audit)

| gap_id | Sev | Layer | Target wave |
|--------|-----|-------|-------------|
| GAP-SPINE-U0-PKG | P0 | U0 | W1 |
| GAP-SPINE-DUAL-PATH | P0 | ALL | W2 |
| GAP-SPINE-C0-SECTION | P0 | C0 | W4 |
| GAP-SPINE-PA-CORE | P0 | PA | W5 |
| GAP-SPINE-SIGN | P0 | L0/PA/L2 | W3, W5, W6 |
| GAP-SPINE-EXIT-ONE | P0 | Exit | W6 |
| GAP-SPINE-L2-SECTION | P0 | L2 | W6 |
| GAP-SPINE-OTEL | P1 | ALL | W8 |
| GAP-SPINE-REJECT | P1 | U0 | W1 |
| GAP-SPINE-L0-HMAC | P1 | L0 | W3 |
| GAP-SPINE-L6-EXHAUST | P2 | L6 | W7 |

---

## Out of scope

- Live LLM provider re-certification across all lanes
- Full C0.3 graph RAG (track as deferred; honest NA ref)
- `agentic_core` app-specific prompt strings
- Notion backlog auto-write during waves

---

## Wave 0 — Architecture gate (Author-Gate required)

**Decisions:**

| # | Decision | Options |
|---|----------|---------|
| D1 | U0 domain packet | A: core `u0_runtime_package_binding` + apps_rg package YAML (recommended) · B: keep inline manifest |
| D2 | PA bridge | A: apps_rg builds slot inputs → `assemble_prompt` orchestrator · B: fork core pipeline into apps_rg (reject) |
| D3 | Section path | A: mandatory `section_front_spine_bridge` before proof pool · B: parallel path forever (reject) |

**Deliverable:** `AUTHORIZATION_DECISION` + update [apps_rg_spine_req_gap_analysis_20260523.md](../docs/reports/apps_rg/apps_rg_spine_req_gap_analysis_20260523.md)

```text
AUTHORIZATION_DECISION: plan=pa-exec-flowchart-gap-f2a8c3 decision=ACCEPTED authorized_by=author_gate decisive_reason="spine_full_convergence — core U0 RuntimeCustomizationPackage ingest, mandatory section_front_spine_bridge, PA via assemble_prompt; apps_rg owns domain templates/BOM only"
DECISION_CAPTURED: type=architecture_choice, repo_area=apps_rg, selected=spine_full_convergence, outcome=executed, confidence=0.88, decision_id=dec_19e55e81295a26123
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=0 note="Author-Gate spine_full_convergence; touches agentic_core authorized"
```

| Decision | Selected |
|----------|----------|
| D1 U0 domain packet | A — `u0_runtime_package_binding` + apps_rg package YAML |
| D2 PA bridge | A — slot compile in apps_rg → `assemble_prompt` orchestrator |
| D3 Section path | A — mandatory `section_front_spine_bridge` (no parallel bypass) |

**Rejected for this plan:** `u0_package_only` (deferral), `keep_dual_paths` (conflicts with target architecture).

---

## Wave 1 — U0 core package ingest (REQ-U0-*)

| Task | Reference | File(s) |
|------|-----------|---------|
| Add `runtime_customization_package.yaml` listing all domain_contract refs | REQ-U0-VALIDATED-HANDOFF-001 | `apps_rg/config/domain_contract/` |
| Add `runtime_package_registry.yaml` | apps_qna pattern | `apps_rg/config/domain_contract/` |
| Delegate validation to core package binding | REQ-U0-SCHEMA-NORMALIZE-001 | [u0_binding.py](../apps_rg/runtime/bindings/u0_binding.py), [u0_runtime_package_binding.py](../agentic_core/runtime/entry/u0_runtime_package_binding.py) |
| Emit `RejectedRequest` + reason codes (not bare ValueError) | REQ-U0-REJECTION-TERMINAL-001 | new helper in apps_rg or core |
| Stamp `session_id`, `trace_root`, `caller_scope_baseline` | REQ-U0-IDENTITY-STAMP-001 | ValidatedRequest fields |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_apps_rg_u0_package_ingest.py -q
```

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=1 note="RuntimePackageRegistry ingest; RejectedRequestNotice; identity stamps; 9/9 package_ingest tests PASS"
```

---

## Wave 2 — One product path (GAP-SPINE-DUAL-PATH)

| Task | Notes |
|------|-------|
| Route all `--section` lanes through [section_front_spine_bridge](../apps_rg/runtime/section_front_spine_bridge.py) | U0→L1→L0 before C0/PA |
| Update [one_spine_inventory.py](../apps_rg/runtime/one_spine_inventory.py) matrix | honest bypass flags |
| Contract: no lane runs without ValidatedRequest from U0 package path | |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_one_spine_inventory.py tests/unit/apps_rg/test_one_spine_fec_bridge_w4.py -q
```

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=2 note="section_front_spine_bridge mandatory; RequestEnvelope U0 package path; inventory two_paths_found=false; 45/45 proof tests PASS"
```

---

## Wave 3 — L1 / L0 (REQ-L1-*, REQ-L0-*)

| Task | File(s) |
|------|---------|
| Optional `ambiguity_register` when detected | [l1_binding.py](../apps_rg/runtime/bindings/l1_binding.py) |
| `validation_receipt_id` on plan path | l1_binding |
| Route `hmac_sig` + `route_digest` proof | [l0_binding.py](../apps_rg/runtime/bindings/l0_binding.py) |
| Document L3 as core-only for managed_workflow | [L3_managed_workflow_scope.md](../apps_rg/config/domain_contract/L3_managed_workflow_scope.md) |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_apps_rg_l1_l0_w3_evidence.py tests/_apps_contract/test_l0_gate_verdicts.py tests/_apps_contract/test_apps_rg_l1_profile_wiring.py -q
```

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=3 note="L1 validation_receipt_id + ambiguity_register; L0 route_digest + hmac_sig via stamp_route_evidence; L3 scope doc; 21/21 proof tests PASS"
```

---

## Wave 4 — C0 spine (REQ-L6 / C0.0–C0.5)

| Task | Notes |
|------|-------|
| Section lanes call `c0_retrieve_apps_rg` not proof-pool shim | [c0_binding.py](../apps_rg/runtime/bindings/c0_binding.py) |
| STOP AS EVIDENCE GAP when grounding required and FEC weak | C0 exec flowchart |
| Graph lane: keep `C0_GRAPH_LANE_NA_REF` documented | [C0_graph_lane_deferral.md](../apps_rg/config/domain_contract/C0_graph_lane_deferral.md) |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_apps_rg_spine_c0_w4.py tests/unit/apps_rg/test_one_spine_fec_bridge_w4.py tests/unit/apps_rg/test_c0_evidence_room.py -q
```

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=4 note="section_c0_retrieve invokes c0_retrieve_apps_rg; STOP AS EVIDENCE GAP on weak FEC; graph NA doc; 38/38 proof tests PASS"
```

---

## Wave 5 — Governed PA (REQ-PA-*, [PA_Prompt_Assembly_exec.md](../docs/reference/03B_PA_Prompt_Assembly/PA_Prompt_Assembly_exec.md))

| Task | Notes |
|------|-------|
| Section: `compiler.py` produces slot payloads / BOM inputs only | apps_rg domain |
| Integrated + section: call [assemble_prompt](../agentic_core/prompt_governance/orchestrator.py) | core PA.0–PA.8 |
| Wire PA.2/PA.4/PA.6/PA.8 in core pipeline first | [pipeline.py](../agentic_core/prompt_governance/prompt_assembly/pipeline.py) |
| HMAC + `L2HandoffEnvelope` | W5 + W6 boundary |

**Proof:**

```bash
python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py
python -m pytest tests/_apps_contract/test_pa_section_contracts_w9.py tests/_apps_contract/test_pa_e0_examples_ssot.py tests/_apps_contract/test_apps_rg_governed_pa_w5.py -q
```

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=5 note="pa_compose_apps_rg -> governed_pa_compose_integrated -> assemble_prompt; section slot BOM + stamp_section_governed_pa_receipt; orchestrator pipeline kwarg fix; 5/5 W5 + 12/12 PA proof tests PASS"
```

---

## Wave 6 — L2 + Exit (REQ-L2-*, REQ-EXIT-*)

| Task | Notes |
|------|-------|
| Section L2 → `SealedL2Artifact` via core executor | [section_l2_spine_receipt.py](../apps_rg/runtime/section_l2_spine_receipt.py) + [section_l2_lane_integration.py](../apps_rg/runtime/section_l2_lane_integration.py) |
| Section Exit → `ExitEvalPipeline` / spine X3 vocabulary | [section_x3_finalize.py](../apps_rg/runtime/spine/section_x3_finalize.py) + [exit_artifacts.py](../apps_rg/runtime/spine/exit_artifacts.py) |
| Integrated L2/Exit | [governed_l2_exit_compose.py](../apps_rg/runtime/spine/governed_l2_exit_compose.py) → `l2_execute_apps_rg` + `exit_finalize_apps_rg` |
| Exactly one X3 per run | `exit_disposition_receipt.json` authority; section `x3_disposition.json` mirror-only |
| `RuntimeExhaustBundle` sealed for L6 | `build_exhaust_bundle_from_exit` on integrated path (W7 section exhaust receipt separate) |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_apps_rg_governed_l2_exit_w6.py tests/unit/apps_rg/test_one_spine_exit_receipt_w6.py tests/_apps_contract/test_apps_rg_disposition_authority_receipts.py -q
```

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=6 note="governed_l2_exit_compose integrated L2+ExitEvalPipeline+RuntimeExhaustBundle; section sealed L2 + exit_disposition_receipt authority; 23/23 proof tests PASS"
```

---

## Wave 7 — L6 (REQ-L6-*)

| Task | Notes |
|------|-------|
| Shadow ingest only sealed spine exhaust | [section_runtime_exhaust_spine_receipt.py](../apps_rg/runtime/section_runtime_exhaust_spine_receipt.py) + [governed_l6_shadow_compose.py](../apps_rg/runtime/spine/governed_l6_shadow_compose.py) |
| `build_l6_shadow_handoff_dict` gated on exhaust + handoff receipts | [l6_handoff_packet.py](../apps_rg/runtime/shadow/l6_handoff_packet.py) |
| No promotion without eval + gauntlet | [L6_eval_before_learn_scope.md](../apps_rg/config/domain_contract/L6_eval_before_learn_scope.md) |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_apps_rg_governed_l6_shadow_w7.py tests/unit/apps_rg/test_one_spine_runtime_exhaust_w7.py -q
```

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=7 note="runtime_exhaust_bundle + l6_shadow_handoff before build_l6_shadow_package; governed L6 envelope blocks promotion; integrated exhaust ingest validates created_after_exit; 18/18 proof tests PASS"
```

---

## Wave 8 — OTEL + CI ratchet ✅

| Task | Notes |
|------|-------|
| Span emission checklist vs REQ parents | `APPS_RG_SPINE_SPAN_CHECKLIST` in [span_contracts.py](../system_learning/runtime_adg/span_contracts.py) |
| Contract gate: dual-path regression | [check_apps_rg_spine_convergence_w8.py](../ops_scripts/ci/check_apps_rg_spine_convergence_w8.py) + APPS-RG-SINGLE-SPINE |
| Refresh [apps_rg_spine_req_gap_audit.json](../artifacts/apps_rg/plans/apps_rg_spine_req_gap_audit.json) | `p0_count=0`, `convergence_status=PASS` |

**Proof:**

```bash
python ops_scripts/ci/check_apps_rg_spine_convergence_w8.py
python -m pytest tests/_apps_contract/test_apps_rg_spine_convergence_w8.py -q
```

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=8 note="APPS_RG_SPINE_SPAN_CHECKLIST + apps_rg_spine_req_gap_audit regenerator + APPS-RG-SPINE-CONVERGENCE gate; removed build_section_fec_bridge alias (single-spine scan); 19/19 W5-W8 contract tests PASS"
PLAN_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 note="W0–W8 + follow-up: one governed pipeline U0→L6; p0_count=0; test_apps_rg_one_pipeline_e2e 20/20; CI single-spine + spine-convergence PASS"
```

---

## Wave 8-followup — Deferred scope closure + one-pipeline E2E ✅

| Deliverable | Path |
|-------------|------|
| Section core PA signing | [governed_pa_compose.py](../apps_rg/runtime/spine/governed_pa_compose.py) |
| L2 handoff receipt | [l2_handoff_receipt.py](../apps_rg/runtime/spine/l2_handoff_receipt.py) |
| Span emit fallback | [spine_span_emit.py](../apps_rg/runtime/spine/spine_span_emit.py) |
| One-pipeline E2E | [test_apps_rg_one_pipeline_e2e.py](../tests/_apps_contract/test_apps_rg_one_pipeline_e2e.py) |
| Closeout receipt | [pa_exec_flowchart_gap_closeout_receipt.md](../docs/reports/apps_rg/pa_exec_flowchart_gap_closeout_receipt.md) |

```text
WAVE_COMPLETE: plan=pa-exec-flowchart-gap-f2a8c3 wave=8-followup note="section_slot_bom_core_signed + l2_handoff_receipt + spine_span_emit; test_apps_rg_one_pipeline_e2e + certification_w8 + no_two_path_w9 = 20 passed"
```

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | Spine REQ gap analysis + audit JSON on disk | files exist |
| 2 | U0 ingests `RuntimeCustomizationPackage` via core binding | pytest U0 package |
| 3 | Section + integrated share U0→L0 front bridge | inventory + contract tests |
| 4 | C0 product path emits spine FEC or evidence gap stop | c0 contract tests |
| 5 | PA uses core `assemble_prompt` / pipeline; apps_rg owns slots only | PA contract tests |
| 6 | Section emits `SealedL2Artifact` + one spine X3 | test_apps_rg_governed_l2_exit_w6 + test_one_spine_exit_receipt_w6 |
| 7 | `python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py` → `p0_count: 0` | command output |
| 8 | Smoke: `python -m pytest tests/_apps_contract/test_pa_section_contracts_w9.py -q` exits 0 | command |

### Verification vs deferral

| Item | Status |
|------|--------|
| C0.3 graph RAG | **Deferred** — NA ref + plan note |
| L1 refinement loop | **N/A** — deterministic apps_rg |
| Full X1A..X1J on section | **Deferred** — phase after Exit unification |
| Live integrated E2E all lanes | **Deferred** — separate runtime proof plan |

---

## Proof commands

```bash
python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py
# Regenerate spine audit after wave closes (manual update to apps_rg_spine_req_gap_audit.json)
```
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
