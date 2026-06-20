---
plan_id: apps-rg-x2-dead-gates-burndown-c4e8f2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg X2 dead / deprecated gates burndown

Remove or align deprecated X2 gates that still emit **PASS with skip** (or registry ghosts) across the seven generated resume sections, without weakening live product enforcement.

**Inventory source:** prior audit (2026-05-22) + [apps_rg_section_complexity_reduction_audit.json](docs/reports/apps_rg/apps_rg_section_complexity_reduction_audit.json) + [section_authority_convergence_audit.json](docs/reports/apps_rg/section_authority_convergence_audit.json).

**Review mirror:** [apps_rg_x2_dead_gates_deletion_plan.md](docs/reports/apps_rg/apps_rg_x2_dead_gates_deletion_plan.md)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-24
NOTION_STATUS: Completed
NOTION_PAGE_ID: 36827693-f55c-817d-95ec-ec054768d647
NOTION_PLAN_URL: https://www.notion.so/apps-rg-x2-dead-gates-burndown-c4e8f2-36827693f55c817d95ecec054768d647
NOTION_RECONCILED: 2026-05-24
PLAN_COMPLETED: 2026-05-24
PLAN_CREATED: slug=apps-rg-x2-dead-gates-burndown-c4e8f2 path=.cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md status=Completed notion_page=36827693-f55c-817d-95ec-ec054768d647
DISK_SSOT: .cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md

PLAN_COMPLETE: plan=apps-rg-x2-dead-gates-burndown-c4e8f2 note="W1-W4 DONE; registry/SRFS/proof-pool alignment; live exec_summary proof receipt"

---

## Context (SCQA)

- **Situation** — apps_rg has seven generated lanes (headline, executive_summary, competencies, unify_bullets, unify_narrative, ibm_bullets, ibm_narrative). X2 validators, `lane_registry.py`, product-shape SSOT, and audit scripts enumerate overlapping gate IDs. Product evidence authority is `augmented_skills_graph`; SRFS slice gates are disabled on the hot path (`x2_proof_pool_gate_flags` → `srfs_slice=False`).
- **Complication** — Many gates still **emit PASS with `skipped_*` / `MOCKED_runtime_plumbing`**, retired SRFS gate IDs linger in audits/old proofs, and `lane_registry` lists ghosts (e.g. `x2_exec_summary_paragraph_word_bounds` vs live `x2_exec_summary_paragraph_max_words`). This inflates X2 bundles and confuses rigor vs runtime truth.
- **Question** — How do we delete or align deprecated dead gates per section without weakening X2/X3 or mock-vs-live contracts?
- **Answer** — Four-wave burndown: registry/audit alignment (safe), retired SRFS repair emission removal (safe), legacy proof-pool gate ID collapse (conditional), SRFS skip-PASS emission removal only after golden-path proof (conditional).

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.3 | Registry + audit SSOT alignment | ~25K | No runtime validator edits | ✅ DONE | Ghost gate IDs gone from lane_registry / declarative contracts / audit scripts |
| W2 | W2.1–W2.3 | Retired exec-summary SRFS stack | ~35K | Release-disabled repair confirmed | ✅ DONE | No X2 emission of retired SRFS product gates; density/emergency modules removed |
| W3 | W3.1–W3.4 | Legacy `*_within_srfs_slice` collapse | ~45K | Product path only uses active pool | ✅ DONE | Single proof-pool gate ID per section; contract tests green |
| W4 | W4.1–W4.2 | SRFS skip-PASS emission + live proof | ~40K | User accepts SRFS X2 retirement on golden path | ✅ DONE | No SRFS structural rows / no `skipped_no_selected_role_fact_set` in live `x2_gate_outputs.json` (graph path) |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Gate inventory JSON refresh | `ops_scripts/apps_rg/section_complexity_reduction_audit.py`, `docs/reports/apps_rg/*.json` | Stale `gates_permanent_noop_or_skipped` | ~8K | ✅ DONE |
| W1.2 | lane_registry ↔ product_shape reconcile | `tests/unit/apps_rg/section_rigor/lane_registry.py`, `section_product_shape_ssot.py` | `paragraph_word_bounds` ghost; rigor-only C0 duplicates | ~10K | ✅ DONE |
| W1.3 | Declarative contract rename | `prompt_assembly/section_contracts/executive_summary_contract.yaml` | Legacy 2–3 / SRFS bounds text | ~7K | ✅ DONE |
| W2.1 | Stop emitting retired SRFS X2 IDs | `executive_summary_x2.py`, judge packet | Old bundles still show `legacy_2_3` | ~12K | ✅ DONE |
| W2.2 | Delete release-disabled repair modules | `exec_summary_srfs_density_repair.py`, `exec_summary_srfs_emergency_finalizer.py`, `exec_summary_srfs_judge_safe.py` (partial) | 95–160 word band vs max-220 product | ~15K | ✅ DONE |
| W2.3 | Test + contract alignment | `test_exec_summary_runtime_slice.py`, `test_executive_summary_x2_x1d_alignment.py` | Assertions on retired gate IDs | ~8K | ✅ DONE |
| W3.1 | Collapse proof-pool gate ID branch | All `*_x2.py` validators + `proof_pool_source_fact_validation.py` | Dual `within_srfs_slice` / `active_proof_pool` | ~20K | ✅ DONE |
| W3.2 | selected_role_fact_set reporting cleanup | `selected_role_fact_set.py`, `srfs_receipt_aggregator.py` | Legacy `x2_srfs_gate_status` fields | ~10K | ✅ DONE |
| W3.3 | Contract tests | `test_apps_rg_x2_ledger_primary_source_facts.py`, `test_product_evidence_authority_contract.py` | Must stay fail-closed | ~10K | ✅ DONE |
| W3.4 | Re-run section audits | `section_authority_convergence_audit.py` | Proof bundle path | ~5K | ✅ DONE |
| W4.1 | Remove SRFS skip-PASS emission (if approved) | `executive_summary_x2.py` (`x2_srfs_*`, `x2_source_sensitive_phrases_supported` skip path) | Still used when `srfs_integration.artifact_path_resolved` set | ~15K | ✅ DONE |
| W4.2 | Live lane proof receipt | `ops_scripts/apps_rg/run_live_section_authority_proof.py` or canonical CLI | Provider/API availability | ~25K | ✅ DONE |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Registry + audit alignment | ✅ DONE | 58 gates | 6 files |
| W2 | Retired exec-summary SRFS | ✅ DONE | +1 unit | 8 files |
| W3 | Legacy proof-pool gate IDs | ✅ DONE | 56+ | 12 files |
| W4 | SRFS skip-PASS + live proof | ✅ DONE | contract + live x2 bundle | executive_summary_x2.py, tests, receipt |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Gate inventory JSON refresh | ✅ DONE |
| W1.2 | lane_registry ↔ product_shape reconcile | ✅ DONE |
| W1.3 | Declarative contract rename | ✅ DONE |
| W2.1 | Stop emitting retired SRFS X2 IDs | ✅ DONE |
| W2.2 | Delete release-disabled repair modules | ✅ DONE |
| W2.3 | Test + contract alignment | ✅ DONE |
| W3.1 | Collapse proof-pool gate ID branch | ✅ DONE |
| W3.2 | SRFS reporting cleanup | ✅ DONE |
| W3.3 | Contract tests | ✅ DONE |
| W3.4 | Re-run section audits | ✅ DONE |
| W4.1 | Remove SRFS skip-PASS emission | ✅ DONE |
| W4.2 | Live lane proof receipt | ✅ DONE |

---

## Out Of Scope

- Weakening X2/X3 gates to make failing lanes pass
- `agentic_core` spine changes
- Competencies `skipped_not_real_llm` style gates (intentional mock discipline)
- Narrative `MOCKED_runtime_plumbing` skip paths (intentional mock discipline)
- Full competencies lane_runtime + lane_execution collapse (separate simplification plan)

---

## Deletion safety matrix (review SSOT)

### Cross-cutting

| Gate / pattern | Skip behavior | Safe to delete? | Notes |
|----------------|---------------|-----------------|-------|
| `x2_{section}_source_fact_ids_within_srfs_slice` | No on product path | **Conditional (W3)** | Product uses `*_active_proof_pool_source_fact_ids` only |
| `x2_c0_metrics_*` | Not skip — absent if no `c0_metrics.json` | **Not safe** | Live gates via `augment_section_x2_gates` |

### executive_summary

| Gate / pattern | Skip? | Safe? |
|----------------|-------|-------|
| `x2_srfs_claim_business_metrics_substrate` | `skipped_no_selected_role_fact_set` | **Conditional (W4)** |
| `x2_srfs_display_ledger_percent_parity` | same | **Conditional (W4)** |
| `x2_srfs_executive_selected_fact_scope` | same | **Conditional (W4)** |
| `x2_srfs_blocked_or_confirmation_fact_citation_zero` | same | **Conditional (W4)** |
| `x2_srfs_jd_or_briefing_standalone_proof_id_zero` | same | **Conditional (W4)** |
| `x2_source_sensitive_phrases_supported` | `observed: skipped` when no `selected_facts` | **Conditional (W4)** |
| `x2_exec_summary_sentence_count_2_3` | Old proofs only | **Safe (W2)** — not in `run_x2_gates` |
| `x2_exec_summary_srfs_density_word_count` | Not emitted | **Safe (W2)** — repair-only |
| `x2_exec_summary_srfs_sentence_count_4_5` | Not emitted | **Safe (W2)** |
| `x2_exec_summary_paragraph_word_bounds` | Registry ghost | **Safe (W1)** — use `paragraph_max_words` |

### unify_narrative / ibm_narrative

| Gate | Skip? | Safe? |
|------|-------|-------|
| `*_requires_finalized_bullets` | MOCKED / standalone | **Not safe** (mock); standalone path conditional |
| `x2_no_metric_repetition_unless_justified` | no companion | **Conditional** — dependency gate |
| `x2_no_companion_ngram_copy` | no companion text | **Conditional** |
| `x2_no_mock_or_plumbing_language_in_real_l2_output` | offline stub | **Not safe** |

### competencies

| Gate | Skip? | Safe? |
|------|-------|-------|
| Style hygiene (`x2_no_first_person`, etc.) | `skipped_not_real_llm` | **Not safe** |

### headline / unify_bullets / ibm_bullets

No permanent noop catalog entries; rigor “absent” gates are live in validators — fix enumeration in W1/W3, not deletion.

---

## Wave 1 — Registry and audit alignment (safe)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases:**
- **W1.1** — Refresh `gates_permanent_noop_or_skipped` static catalog in complexity audit | ~8K | PHASE_STATUS: DONE
- **W1.2** — Align `lane_registry` critical gates with `section_product_shape_ssot` + runtime emission | ~10K | PHASE_STATUS: DONE
- **W1.3** — Update `executive_summary_contract.yaml` bounds gate id to `paragraph_max_words` | ~7K | PHASE_STATUS: DONE

**Acceptance:**
- No `x2_exec_summary_paragraph_word_bounds` in lane_registry or declarative contract
- `gate_coverage_registry.py` fragments still reference real gate IDs
- `python ops_scripts/apps_rg/section_complexity_reduction_audit.py` exits 0; JSON/MD updated

**Commands:**
```bash
python ops_scripts/apps_rg/section_complexity_reduction_audit.py
python -m pytest tests/unit/apps_rg/section_rigor/ -q --override-ini=addopts= -p no:xdist -p pytest_timeout
```

---

## Wave 2 — Retired executive_summary SRFS stack (safe)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases:**
- **W2.1** — Confirm `run_x2_gates` never emits `x2_exec_summary_srfs_*` or `sentence_count_2_3` | ~12K | PHASE_STATUS: DONE
- **W2.2** — Remove or quarantine `exec_summary_srfs_density_repair.py`, emergency finalizer SRFS-only paths | ~15K | PHASE_STATUS: DONE
- **W2.3** — Update tests that reference retired gate IDs | ~8K | PHASE_STATUS: DONE

**Acceptance:**
- `test_executive_summary_x2_x1d_alignment` and `test_exec_summary_runtime_slice` green
- No import of deleted repair modules from production lane path
- [SIMPLIFICATION_REDESIGN.md](docs/reports/apps_rg/SIMPLIFICATION_REDESIGN.md) cross-link updated

**Commands:**
```bash
python -m pytest tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py tests/_apps_contract/test_exec_summary_runtime_slice.py tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py -q --override-ini=addopts= -p no:xdist -k "not mock_command and not mocked_judges and not three_judge and not judge_provider_status and not provider_request and not temperature_out and not qwen_unavailable and not l6_shadow"
```

---

## Wave 3 — Legacy proof-pool gate ID collapse (conditional)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Authorization**: REQUIRED — touches all seven section validators and proof-pool contract surface.

**Phases:**
- **W3.1** — Remove `within_srfs_slice` branch; always emit `x2_{section}_active_proof_pool_source_fact_ids` when pool gate active | ~20K | PHASE_STATUS: DONE
- **W3.2** — Simplify SRFS receipt fields (`x2_srfs_gate_status` → NOT_APPLICABLE only on product path) | ~10K | PHASE_STATUS: DONE
- **W3.3** — Run ledger-primary + product evidence contract tests | ~10K | PHASE_STATUS: DONE
- **W3.4** — Regenerate convergence + complexity audit artifacts | ~5K | PHASE_STATUS: DONE

**Acceptance:**
- `test_x2_gate_flags_product_path_disables_srfs_slice` still passes
- `test_apps_rg_x2_ledger_primary_source_facts.py` passes (21+ tests)
- No `within_srfs_slice` string in emitted `x2_gate_outputs.json` from mock canonical lane runs

**Commands:**
```bash
python -m pytest tests/_apps_contract/test_apps_rg_x2_ledger_primary_source_facts.py tests/unit/apps_rg/test_product_evidence_authority_contract.py -q --override-ini=addopts= -p no:xdist -p pytest_timeout
python ops_scripts/apps_rg/section_authority_convergence_audit.py
```

---

## Wave 4 — SRFS skip-PASS emission + live proof (conditional)

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Authorization**: REQUIRED — removes X2 rows that still PASS-skip on default qwen path; requires explicit user sign-off that SRFS structural X2 is retired.

**Phases:**
- **W4.1** — Remove emission of `x2_srfs_*` gates and unconditional-skip `x2_source_sensitive_phrases_supported` when SRFS inactive | ~15K | PHASE_STATUS: DONE
- **W4.2** — One qwen live proof per affected lane; receipt under `docs/reports/apps_rg/` | ~25K | PHASE_STATUS: DONE

**Acceptance:**
- Live `executive_summary` proof: no SRFS gates with `skipped_no_selected_role_fact_set` unless SRFS explicitly re-enabled
- Receipt markdown + JSON with gate diff before/after
- X3 disposition unchanged or improved vs baseline (no weakening)

**Commands:**
```bash
python -m apps_rg --section executive_summary --provider qwen_vllm --allow-non-allow-exit-zero
python ops_scripts/apps_rg/run_live_section_authority_proof.py
```

---

## Gap Register

**GAP-1: SRFS integration still wired in executive_summary_lane**
- `srfs_integration` passed to `run_x2_gates` when envelope present
- W4 deletion unsafe if any production targeting still sets `artifact_path_resolved`
- Mitigation: grep + live proof before W4.1

**GAP-2: Old proof bundles show legacy gates**
- `section_authority_convergence_audit` observed `legacy_2_3_gate_observed: true` on snapshot `full_resume_0e41a1c13cfe`
- Mitigation: W2/W4 regenerate proofs; do not treat old artifacts as runtime SSOT

**GAP-3: Mock/companion skip gates must remain**
- unify_narrative / ibm_narrative MOCKED skips are not dead gates
- Mitigation: explicit Out Of Scope + audit catalog comments

---

## Definition of Done

DoD-1: Plan registered in Notion Plans DB and on disk at `.cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md`
- Evidence: Notion row `Exists On Disk=true`; `PLAN_CREATED` marker emitted
- Status: TODO

DoD-2: W1 complete — registry ghosts removed, audits regenerated
- Evidence: `section_complexity_reduction_audit.json` updated; no `paragraph_word_bounds` in lane_registry
- Status: DONE

DoD-3: W2 complete — retired SRFS X2/repair stack removed with tests green
- Evidence: pytest executive_summary slice tests pass; no `x2_exec_summary_srfs_density_word_count` in `run_x2_gates` output
- Status: DONE

DoD-4: W3 complete — single active proof-pool gate ID per section, contract tests pass
- Evidence: `pytest test_apps_rg_x2_ledger_primary_source_facts` → 0 fail
- Status: DONE

DoD-5: W4 complete OR explicitly deferred with `DEFERRED_SCOPE` — live proof shows skip-PASS burndown on golden path
- Evidence: `docs/reports/apps_rg/apps_rg_x2_dead_gates_burndown_receipt.md` with command output
- Status: DONE

### Verification vs deferral

| Item | Verify in plan | Defer only if |
|------|----------------|---------------|
| SRFS skip-PASS removal | W4 | User rejects SRFS retirement |
| Mock skip gates | Out of scope | Never delete |
| C0 gates | Not in scope | N/A — keep live |

---

## Scope Expansion Authorization

Use standard `DISCOVERED_SCOPE` → `AUTHORIZATION_DECISION` → `SCOPE_EXPANSION` markers per template when W3/W4 expand beyond validator seam.

---

## Marker Quick Reference

```
PLAN_CREATED: slug=apps-rg-x2-dead-gates-burndown-c4e8f2 path=.cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md status=Not Started
WAVE_START: plan=apps-rg-x2-dead-gates-burndown-c4e8f2 wave=1
WAVE_COMPLETE: plan=apps-rg-x2-dead-gates-burndown-c4e8f2 wave=1 note="+N tests, N files, scope=registry-audit"
PLAN_COMPLETE: plan=apps-rg-x2-dead-gates-burndown-c4e8f2 note="X2 dead gates aligned; live proof receipt on disk"
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
