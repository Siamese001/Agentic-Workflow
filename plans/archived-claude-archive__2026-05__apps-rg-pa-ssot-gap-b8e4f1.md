---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-pa-ssot-gap-b8e4f1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-pa-ssot-gap-b8e4f1.md'
source_sha256: d8ce7591c4154b6f57f1b5ffe3ad21842e808b254e56c37c82dc329629004baa
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-pa-ssot-gap-b8e4f1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg Prompt Assembly SSOT convergence

Close gaps between **declarative PA SSOT** (BOM, examples YAML, section templates) and **live compile output** (what models see in E0 and sibling slots). Primary failure mode: **dual E0 authority** — especially executive_summary (P0).

**Gap analysis (human review):** [prompt_assembly_ssot_gap_analysis_20260523.md](../docs/reports/apps_rg/prompt_assembly_ssot_gap_analysis_20260523.md)  
**Machine audit:** [prompt_assembly_ssot_gap_audit.json](../artifacts/apps_rg/plans/prompt_assembly_ssot_gap_audit.json)  
**Related (orthogonal):** [apps-rg-proof-pool-c0-ssot-a7f3e2.md](apps-rg-proof-pool-c0-ssot-a7f3e2.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-23
NOTION_STATUS: Completed
NOTION_PLAN_URL: https://www.notion.so/apps-rg-pa-ssot-gap-b8e4f1-36927693f55c81ffa6c5d48b02e86e43
DISK_SSOT: .cursor/plans/apps-rg-pa-ssot-gap-b8e4f1.md

PLAN_CREATED: slug=apps-rg-pa-ssot-gap-b8e4f1 path=.cursor/plans/apps-rg-pa-ssot-gap-b8e4f1.md status=Not Started
PLAN_COMPLETE: slug=apps-rg-pa-ssot-gap-b8e4f1 waves=W0-W5 status=COMPLETED proof=pa_e0_compile_proof_receipt.json

---

## Scope delivered (2026-05-23)

**Problem closed:** Dual E0 authority — declarative examples YAML vs inline template stubs sent different voice to the model (especially executive_summary 3-sentence stubs vs 4–5 sentence gold).

**Solution:** Hydrate E0 at compile from `apps_rg/prompt_assembly/examples/*.yaml` via [`e0_examples.py`](../apps_rg/prompt_assembly/e0_examples.py); W9 `*_pa.py` lanes call `resolve_e0_for_section()`.

| Area | Deliverable |
|------|-------------|
| Runtime | `executive_summary`, `competencies`, `unify_bullets`, `unify_narrative` PA compile paths |
| BOM / registry | `section_example_authority`; W9 lanes require E0 when examples catalog exists |
| Template | Inline exec-summary positives removed; transformation examples merged at compile |
| Tests | `test_pa_e0_examples_ssot.py`, `test_pa_section_contracts_w9.py`; exec-summary PA tests updated |
| CI | `check_prompt_assembly_ssot.py` + `verify_pa_e0_compile_proof.py` in contract gates |
| Docs | [prompt_assembly_ssot_gap_analysis_20260523.md](../docs/reports/apps_rg/prompt_assembly_ssot_gap_analysis_20260523.md), [apps_rg_pa_prompt_contract.md](../docs/guides/apps_rg_pa_prompt_contract.md) |

**Proof (automated):** [pa_e0_compile_proof_receipt.json](../artifacts/apps_rg/plans/pa_e0_compile_proof_receipt.json) — gold 4 sentences in compiled E0; template stub absent.

**Out of scope (unchanged):** C0/FEC proof-pool ([apps-rg-proof-pool-c0-ssot-a7f3e2.md](apps-rg-proof-pool-c0-ssot-a7f3e2.md)), live LLM runtime re-run, `agentic_core` prompt_governance.

---

## Problem statement

BOM declares `executive_summary_example_authority.gold_examples_path`, but `build_executive_summary_assembly_input()` passes `e0_examples=slots.get("E0")` from inline template stubs (2–3 sentences) while examples YAML holds 4–5 sentence gold for the same IDs. Competencies and unify have **orphaned** examples YAML with no compile hydration. Tests prove artifact **existence**, not **equivalence**.

---

## Success criteria (Definition of Done)

- [x] Single E0 SSOT strategy documented in BOM + PA contract doc
- [x] Executive summary compile hydrates E0 from examples YAML (or template E0 removed)
- [x] Contract test fails on inline/YAML body drift for shared example IDs
- [x] `prompt_assembly_ssot_gap_audit.py` returns `p0_count: 0` and no `dual_authority_risk` on ACTIVE lanes with examples files
- [x] Compile-time proof: `verify_pa_e0_compile_proof.py` → [pa_e0_compile_proof_receipt.json](../artifacts/apps_rg/plans/pa_e0_compile_proof_receipt.json)
- [x] BOM/registry E0 requiredness aligned (examples-backed W9 lanes; IBM optional E0 acceptable)

---

## Wave plan

### W0 — Design gate (Author-Gate required)

**Decision:** E0 hydration strategy for all lanes with `examples/*.yaml`.

| Option | Summary | Trade-off |
|--------|---------|-----------|
| A | Hydrate at compile from examples YAML; strip inline positives from templates | One SSOT; may need token budget trim pass |
| B | Delete examples YAML; maintain E0 only in templates | Simpler paths; loses W10.5 multishot catalog |
| C | Build-time codegen: template E0 generated from YAML in CI | No runtime drift; extra build step |

**Deliverable:** `AUTHORIZATION_DECISION` + update BOM `executive_summary_example_authority` into general `section_example_authority` map.

**Status:** DONE (hydrate-from-YAML selected; implemented W1–W4)

---

### W1 — P0 executive_summary E0 wiring

| Task | File(s) |
|------|---------|
| Add `hydrate_e0_from_examples(section_id)` helper | `apps_rg/prompt_assembly/e0_examples.py` (new) |
| Wire `build_executive_summary_assembly_input` | [executive_summary_pa.py](../apps_rg/runtime/sections/executive_summary_pa.py) |
| Remove or stub inline positives in template | [executive_summary.generate_scratch_v1.yaml](../apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml) |
| Contract: shared IDs + sentence-count parity | `tests/_apps_contract/test_pa_e0_examples_ssot.py` (new) |

**Proof:**

```bash
python -m pytest tests/_apps_contract/test_pa_e0_examples_ssot.py tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py -q
python -m apps_rg --section executive_summary  # real proof dir; inspect compiled_prompt.txt E0
```

**Status:** DONE

---

### W2 — P1 competencies + unify hydration

| Task | File(s) |
|------|---------|
| Wire competencies PA | [competencies_pa.py](../apps_rg/runtime/sections/competencies_pa.py) |
| Wire unify bullets/narrative PA | [unify_bullets_pa.py](../apps_rg/runtime/sections/unify_bullets_pa.py), [unify_narrative_pa.py](../apps_rg/runtime/sections/unify_narrative_pa.py) |
| BOM: `section_example_authority` entries for competencies + unify | [prompt_bom.yaml](../apps_rg/prompt_assembly/prompt_bom.yaml) |
| Lane contract tests | extend `test_pa_e0_examples_ssot.py` |

**Status:** DONE

---

### W3 — Registry / BOM alignment + docs

| Task | Notes |
|------|-------|
| Set W9 `required_slots` to include E0 where BOM requires | [prompt_registry.yaml](../apps_rg/prompt_assembly/prompt_registry.yaml) |
| Fix stale paths in PA contract guide | [apps_rg_pa_prompt_contract.md](../docs/guides/apps_rg_pa_prompt_contract.md) |
| Document shell (`strategic_tailor_v1`) vs section template | gap analysis § G5 |

**Status:** DONE

---

### W4 — CI ratchet

| Task | Notes |
|------|-------|
| Wire audit script into contract gates | `ops_scripts/ci/run_contract_gates.py` |
| Fail on `dual_authority_risk: true` for lanes with examples YAML | [prompt_assembly_ssot_gap_audit.py](../ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py) |

**Status:** DONE

---

### W5 — W9 section_prompt_contracts coverage

| Task | File(s) |
|------|---------|
| Contract exists per modular lane | [test_pa_section_contracts_w9.py](../tests/_apps_contract/test_pa_section_contracts_w9.py) |
| Audit gate in CI | [check_prompt_assembly_ssot.py](../ops_scripts/ci/check_prompt_assembly_ssot.py) |
| Compile proof script | [verify_pa_e0_compile_proof.py](../ops_scripts/apps_rg/verify_pa_e0_compile_proof.py) |

**Status:** DONE (E3 `section_contracts/` vs W9 `section_prompt_contracts/` coexistence documented as accepted; W9 dispatch uses `section_prompt_contracts/` only)

---

## Gap reference (from audit — post-close)

| gap_id | Severity | Status |
|--------|----------|--------|
| PA-E0-DRIFT-* | P0/P1 | **CLOSED** (hydrate at compile) |
| PA-BOM-REGISTRY-E0 | P2 | **CLOSED** (examples-backed lanes require E0 in registry) |
| PA-DOCS-STALE-PATH | P3 | **CLOSED** ([apps_rg_pa_prompt_contract.md](../docs/guides/apps_rg_pa_prompt_contract.md) updated) |
| PA-DUAL-CONTRACT-TREES | P2 | **ACCEPTED** (E3 legacy + W9 runtime contracts; documented) |

---

## Out of scope

- `agentic_core` prompt_governance changes (apps_rg-owned PA content)
- C0 / FEC proof-pool convergence (see proof-pool plan)
- X1D judge rubric changes (downstream of prompt fix)

---

## Proof commands (regenerate audit)

```bash
python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py
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
