---
plan_id: pa-exec-flowchart-gap-f2a8c3
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# PA exec flowchart convergence (apps_rg + core pipeline)

Close structural gaps between [PA_Prompt_Assembly_exec.md](../docs/reference/03B_PA_Prompt_Assembly/PA_Prompt_Assembly_exec.md) and runtime PA on **apps_rg** product paths. Unify section compile and integrated spine behind one signed handoff story without weakening gates.

**Gap analysis (human review):** [pa_exec_flowchart_gap_analysis_20260523.md](../docs/reports/apps_rg/pa_exec_flowchart_gap_analysis_20260523.md)  
**Machine audit:** [pa_exec_flowchart_gap_audit.json](../artifacts/apps_rg/plans/pa_exec_flowchart_gap_audit.json)  
**Related (closed E0 SSOT only):** [apps-rg-pa-ssot-gap-b8e4f1.md](apps-rg-pa-ssot-gap-b8e4f1.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-23
NOTION_STATUS: Not Started
NOTION_PLAN_URL: https://www.notion.so/pa-exec-flowchart-gap-f2a8c3-36927693f55c8138afb7fe72202f206a
DISK_SSOT: .cursor/plans/pa-exec-flowchart-gap-f2a8c3.md

PLAN_CREATED: slug=pa-exec-flowchart-gap-f2a8c3 path=.cursor/plans/pa-exec-flowchart-gap-f2a8c3.md status=Not Started notion_page=36927693-f55c-8138-afb7-fe72202f206a

---

## Context (SCQA)

- **Situation** — Core owns a staged PA pipeline (`run_prompt_assembly_pipeline`) and per-stage modules (PA.0–PA.7). apps_rg owns rich 8-slot section compile (`compiler.py`) and a thin integrated `pa_compose_apps_rg`. E0 YAML hydration is closed (b8e4f1).
- **Complication** — Exec flowchart requires PA.0–PA.8, signed `CompiledPromptArtifact`, `L2HandoffEnvelope`, and full OTEL spine. Product paths use neither full pipeline nor HMAC; two `CompiledPromptArtifact` types diverge.
- **Question** — How do we converge apps_rg PA onto the exec flowchart without breaking section lanes or forcing premature `agentic_core` app leakage?
- **Answer** — W0 architecture gate → wire core pipeline stages into apps_rg via orchestrator bridge on integrated path → lift section compile outputs to spine artifact + receipts → add PA.8 + CI proof.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Architecture + Author-Gate (bridge strategy) | 🔲 TODO | — | — |
| W1 | Integrated path: PA.0 boundary + gap reports | 🔲 TODO | — | — |
| W2 | Core pipeline: wire PA.2/PA.4/PA.6 into pipeline | 🔲 TODO | — | — |
| W3 | Section path: spine CPA + security/validation receipts | 🔲 TODO | — | — |
| W4 | PA.7 signing (HMAC, manifest) + L2HandoffEnvelope | 🔲 TODO | — | — |
| W5 | PA.8 red-team + OTEL span completeness + CI ratchet | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Bridge vs unify decision record | 🔲 TODO |
| W1.1 | `pa_compose_apps_rg` → orchestrator or boundary_check | 🔲 TODO |
| W2.1 | Pipeline stage wiring (PA.2, PA.4, PA.6) | 🔲 TODO |
| W3.1 | Unify section `CompiledPromptArtifact` to core W6 or adapter | 🔲 TODO |
| W4.1 | HMAC + handoff envelope on both paths | 🔲 TODO |
| W5.1 | PA.8 fixtures + contract gates | 🔲 TODO |

---

## Gap register (from audit)

| gap_id | Sev | Summary | Target wave |
|--------|-----|---------|-------------|
| GAP-PA-INT-1 | P0 | Integrated PA bypasses core pipeline | W1 |
| GAP-PA-PIPE-1 | P0 | PA.2/PA.4/PA.6/PA.8 not in pipeline | W2, W5 |
| GAP-PA-SIGN-1 | P0 | No HMAC / manifest on product paths | W4 |
| GAP-PA-ART-1 | P1 | Dual CompiledPromptArtifact types | W3 |
| GAP-PA-SIGN-2 | P1 | Missing L2HandoffEnvelope | W4 |
| GAP-PA-AIR-1 | P1 | Section path lacks security pass receipt | W3 |
| GAP-PA-OTEL-1 | P1 | Incomplete pa.* spans | W5 |
| GAP-PA-UP-1 | P1 | R0/tools not provider-native on integrated | W4 |
| GAP-PA-UP-2 | P2 | blueprint_hash / route_digest | W4 |
| GAP-PA-BOM-1 | P2 | BOM vs registry E0 optional mismatch | W3 |
| GAP-PA-DUAL-PATH | P2 | Section vs integrated divergence | W3–W4 |
| GAP-PA-DOCS-STALE-PATH | P3 | Stale profile paths in docs | W3 |
| GAP-PA-DUAL-CONTRACT-TREES | P3 | Accepted (document only) | — |

---

## Out of scope

- Live LLM re-run / judge rubric changes
- C0 proof-pool convergence ([apps-rg-proof-pool-c0-ssot-a7f3e2.md](apps-rg-proof-pool-c0-ssot-a7f3e2.md))
- Broad v40 spine unification beyond PA seam ([apps-rg-v40-spine-gap-c4a8f1.md](apps-rg-v40-spine-gap-c4a8f1.md))

---

## Wave 0 — Architecture gate (Author-Gate required)

**Decision:** How apps_rg invokes exec PA spine.

| Option | Summary | Trade-off |
|--------|---------|-----------|
| A | Integrated + section both call `assemble_prompt` orchestrator after local slot build | Single spine; core touch + migration receipt |
| B | Extend `run_prompt_assembly_pipeline` only on integrated; section stays local compiler + receipt adapter | Smaller blast radius; dual path longer |
| C | Copy PA stages into apps_rg (forbidden pattern) | Faster locally; violates core boundary |

**Deliverable:** `AUTHORIZATION_DECISION` + update gap analysis with chosen bridge.

---

## Wave 1 — Integrated path boundary (P0 GAP-PA-INT-1)

| Task | File(s) |
|------|---------|
| Call `boundary_check` before compose | [pa_binding.py](../apps_rg/runtime/bindings/pa_binding.py) |
| Emit `assembly_gap_report` shape on FAIL | new helper under `apps_rg/runtime/spine/` or reuse core types |
| Contract test: missing FEC → PA gap stop | `tests/_apps_contract/test_pa_exec_boundary_*.py` |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_pa_exec_boundary_integrated.py -q
```

---

## Wave 2 — Core pipeline completeness (P0 GAP-PA-PIPE-1)

| Task | Notes |
|------|-------|
| Wire `compose_slots` (PA.2) into pipeline | [pipeline.py](../agentic_core/prompt_governance/prompt_assembly/pipeline.py) |
| Wire `pa4_validation` (PA.4) | [pa4_validation.py](../agentic_core/prompt_governance/prompt_assembly/pa4_validation.py) |
| Wire `render_for_provider` (PA.6) | [pa6_provider_rendering.py](../agentic_core/prompt_governance/prompt_assembly/pa6_provider_rendering.py) |
| Unit tests per stage | `tests/unit/agentic_core/prompt_governance/` |

**Proof:**

```bash
python -m pytest tests/unit/agentic_core/prompt_governance/test_pa_pipeline_stages.py -q
```

**Note:** `touches_agentic_core: true` — migration receipt + author-gate before merge.

---

## Wave 3 — Section path spine artifacts (P1 GAP-PA-ART-1, GAP-PA-AIR-1)

| Task | File(s) |
|------|---------|
| Adapter: local compile → core W6 CPA or documented bridge | [section_prompt_adapter.py](../apps_rg/runtime/bindings/section_prompt_adapter.py) |
| Emit security pass receipt at compile | [compiler.py](../apps_rg/prompt_assembly/compiler.py) |
| Align BOM/registry E0 for IBM/headline | [prompt_registry.yaml](../apps_rg/prompt_assembly/prompt_registry.yaml) |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_pa_section_contracts_w9.py tests/_apps_contract/test_pa_e0_examples_ssot.py -q
python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py
```

---

## Wave 4 — Sign and handoff (P0 GAP-PA-SIGN-1, P1 GAP-PA-SIGN-2)

| Task | File(s) |
|------|---------|
| HMAC + manifest_hash on product artifacts | [orchestrator.py](../agentic_core/prompt_governance/orchestrator.py), pa_binding |
| `L2HandoffEnvelope` contract + emit | core contracts + apps_rg binding |
| R0 / tool schema provider fields | integrated compose |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_apps_rg_app_payload_consumption.py -q -k pa
```

---

## Wave 5 — PA.8 + OTEL + CI (GAP-PA-PIPE-1, GAP-PA-OTEL-1)

| Task | Notes |
|------|-------|
| Implement `pa.red_team_scan` stage + fixtures | per [PA.8_Authority_RedTeam_Slot_Verification.md](../docs/reference/03B_PA_Prompt_Assembly/PA.8_Authority_RedTeam_Slot_Verification.md) |
| Span emission on apps_rg compile | align with `system_learning/runtime_adg/span_contracts.py` |
| CI gate: pipeline stage coverage | `ops_scripts/ci/run_contract_gates.py` |

**Proof:**

```bash
python ops_scripts/ci/check_prompt_assembly_ssot.py
python -m pytest tests/_apps_contract/test_pa_exec_spine_spans.py -q
```

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | Gap analysis + audit JSON linked from plan | Files exist; Notion Plans row |
| 2 | Integrated path calls PA.0; FAIL emits gap report | pytest boundary test |
| 3 | Core pipeline runs PA.2, PA.4, PA.6, PA.8 | pipeline unit tests |
| 4 | Section path emits security + validation receipts | contract test |
| 5 | Product CPA includes manifest_hash + HMAC | contract test |
| 6 | `python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py` still `p0_count: 0` (E0) | command output |
| 7 | Smoke: `python -m pytest tests/_apps_contract/test_pa_section_contracts_w9.py -q` exits 0 | command |

### Verification vs deferral

| Item | Status |
|------|--------|
| Live integrated spine E2E with provider | **Deferred** — separate runtime proof plan |
| Full GateMesh G13/G17/G21 on section lanes | **Deferred** — wave after PA spine |
| agentic_core generic PA for all apps_* | **In scope W2** with receipt |

---

## Proof commands (regenerate audit)

```bash
python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py
# Manual: refresh pa_exec_flowchart_gap_audit.json after wave closes
```
