# apps_rg ↔ agentic_core v40 Spine Gap Analysis

**Generated:** 2026-05-23  
**SSOT map:** [`agentic_process_mapping_v40.md`](../../reference/_notes/agentic_process_mapping_v40.md)  
**Companion:** [`agentic_process_mapping_v40_v2.md`](../../reference/_notes/agentic_process_mapping_v40_v2.md)  
**Prior review:** [`apps_rg_agentic_core_binding_overlap_review_20260522.md`](apps_rg_agentic_core_binding_overlap_review_20260522.md)  
**Gap inventory plan:** [apps-rg-v40-spine-gap-c4a8f1](../../.cursor/plans/apps-rg-v40-spine-gap-c4a8f1.md)  
**Execution plan (spine-only, no bridges):** [apps-rg-spine-only-unification-d8f4a2](../../.cursor/plans/apps-rg-spine-only-unification-d8f4a2.md)  
**ADR:** [ADR-apps-rg-spine-only-unification.md](../../docs/adr/ADR-apps-rg-spine-only-unification.md)  
**Notion (gap analysis):** https://www.notion.so/36927693f55c8156b234e4362e3b0f53

---

## Executive summary

`apps_rg` binds to `agentic_core` primarily through **frozen contracts** (`ValidatedRequest`, `L1PlanContract`, `RouteContract`, `FinalEvidenceContract`, `CompiledPromptArtifact`, `SealedL2Artifact`) and **generic engines** (hybrid search, provider gateway, L2 executor, L5 cert verify, Exit pipeline on integrated path). App-owned logic lives in [`apps_rg/runtime/bindings/`](../../apps_rg/runtime/bindings/).

**Critical structural gap:** two product-visible runtime paths ([`one_spine_inventory.py`](../../apps_rg/runtime/one_spine_inventory.py)):

| Path | Entry | Spine contracts emitted | Exit / UWG |
|------|-------|-------------------------|------------|
| **A — Section CLI** | `python -m apps_rg --section <lane>` | U0/L1/L0 on front bridge only; lane substitutes for C0/PA/L2/Exit | Lane `x3_disposition.json`; no UWG |
| **B — Integrated R4** | `python -m apps_rg` (no `--section`) | Full chain via `integrated_single_action_spine_run` | `ExitEvalPipeline` → spine X3; UWG on commit |

**W-A binding hardening (2026-05-22) closed:** legacy `agentic_core/**/apps_rg_*_binding.py` shims deleted; L1 `ADVISORY_ONLY` route_hints; `disposition_authority` receipts. **This analysis starts after W-A** and extends to **all v40 layers**.

Gap IDs: **`GAP-AR-*`** = apps_rg-owned; **`GAP-AC-*`** = agentic_core-owned.

---

## Methodology

For each v40 stage/substep:

1. Map intended spine behavior (v40 SSOT).
2. Document **apps_rg** implementation (binding module + section vs integrated path).
3. Document **agentic_core** touchpoints (contracts, engines, leakage).
4. Classify: **ALIGNED** | **PARTIAL** | **MISSING** | **DIVERGENT** (intentional).
5. Assign gap IDs and remediation wave (see plan).

**Non-claims:** No live integrated-spine runtime proof was executed for this document. Section-path behavior is inferred from inventory, bindings, and contract tests.

---

## Cross-cutting: 00A (L5) + 00C (Runtime Gates)

| v40 intent | apps_rg | agentic_core | Fit | Gaps |
|------------|---------|--------------|-----|------|
| L5 certifies evidence; consumed by all layers | `l5_certification_ref` threaded U0→L1→L0→C0→PA→L2→Exit; profiles under `apps_rg/profiles/` | `verify_certification_ref` in contract `__post_init__` | **PARTIAL** | **GAP-AR-00C-1:** Section runs use app X2 validators, not full 00C GateMesh G01–G29. **GAP-AC-00C-1:** C0 binding constructs `GateVerdict` but section path does not prove GateMesh traversal. **GAP-AR-L5-1:** Risk of treating L5 cert as runtime proceed/stop (mitigated by docs; needs contract test on section lanes). |

---

## U0 — Request intake (U0.1–U0.5)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| U0.1 Transport/envelope | Validate channel, shape, size | [`u0_binding.u0_validate_apps_rg`](../../apps_rg/runtime/bindings/u0_binding.py) coerces envelope + required `app_payload` keys | [`ValidatedRequest`](../../agentic_core/runtime/contracts/apps_rg_ingress_payload.py), [`AppsRgIngressPayload`](../../agentic_core/runtime/contracts/apps_rg_ingress_payload.py) | **PARTIAL** | **GAP-AR-U0-1:** No explicit substep modules/receipts per U0.1–U0.5. **GAP-AC-U0-1:** Ingress DTOs live in `agentic_core` while validation is app-owned (reads as core owns apps_rg intake). |
| U0.2 Identity/quota | caller, tenant, session, quota | Stamps `request_id`, `run_id`, `trace_id`, `tenant_id`, `replay_key` | Same fields on `ValidatedRequest` | **ALIGNED** | — |
| U0.3 Schema/idempotency | normalize, digest | `payload_digest`, `task_spec`/`query_spec` synthesis, profile manifest digests | `payload_digest` on contract | **ALIGNED** | — |
| U0.4 Origin trust | origin labels, injection triage | Forbidden authority field checks in U0 path | `AuthorityValidationReceipt` (app-local `_AppsRgU0AuthorityReceipt` + core types) | **PARTIAL** | **GAP-AR-U0-2:** Origin labeling less explicit than v40 prose. |
| U0.5 Handoff | ValidatedRequest / RejectedRequest | Returns `ValidatedRequest` or raises | `ValidatedRequest` | **ALIGNED** | **GAP-AR-U0-3:** Section lanes build envelope inline ([`section_front_spine_bridge`](../../apps_rg/runtime/section_front_spine_bridge.py)) — not full U0 package validation path for all lanes. |

**Canonical symbol:** `apps_rg.runtime.bindings.u0_binding.u0_validate_apps_rg` (shim deleted per W-A).

---

## L1 — Reasoning + plan (L1.1–L1.6)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| L1.1 Intent / ambiguity | goal, ambiguity register | `task_spec`, `query_spec`, `support_expectation`, `output_expectation`, `generation_mode` | Projections on `L1PlanContract` | **PARTIAL** | **GAP-AR-L1-1:** No `ambiguity_register` field. |
| L1.2 Planning priors | L4 read approved refs only | `planning_prior_refs` → `rg_planning_profile.yaml`; digest verify | Ref tuple on contract only | **DIVERGENT** | **GAP-AR-L1-2:** No runtime L4 read (refs only — acceptable if documented). |
| L1.3 Refinement loop | planning-only refinement | **Not implemented** (single pass) | — | **MISSING** | **GAP-AR-L1-3:** By design for deterministic apps_rg; document as N/A for resume_generation. |
| L1.4 Plan + route hints | work units, route hints non-authoritative | `task_plan`, capabilities, work-shape hints, `route_hints` + `authority_class: ADVISORY_ONLY` | `L1PlanContract` + `_validate_route_hints` | **ALIGNED** | W-A closed L1-3 advisory. |
| L1.5 Validation / repair | consistency, bounded repair | Digest mismatch fail-closed; `non_authority_assertion` | `__post_init__` validators, L5 verify | **PARTIAL** | **GAP-AR-L1-4:** No replan/repair loop (fail-closed only). |
| L1.6 L1PlanContract handoff | freeze plan | `l1_plan_apps_rg` → `L1PlanContract` | Contract type | **ALIGNED** | — |

**Canonical symbol:** `apps_rg.runtime.bindings.l1_binding.l1_plan_apps_rg`.

---

## L0 — Route decision (L0.1–L0.6)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| L0.1 Preflight | consume L1PlanContract, bind hashes | [`l0_route_apps_rg`](../../apps_rg/runtime/bindings/l0_binding.py) reads plan + `route_profiles.yaml` | `L1PlanContract`, `RouteContract`, `RouteGateReceipt` | **ALIGNED** | — |
| L0.2 Deterministic selection | fixed order, cheapest safe | Profile-driven selection from YAML | Generic `package_driven_l0_binding` exists separately | **PARTIAL** | **GAP-AR-L0-1:** Unclear which path integrated vs section uses long-term. **GAP-AC-L0-1:** [`apps_rg_prerequisite_gate`](../../agentic_core/L0_routing/gates/apps_rg_prerequisite_gate.py) still in core. |
| L0.3 Cache/fallback/HITL | R1A/R1B/R5 posture | Profile fields + cache preflight in dispatch | Core cache contracts | **PARTIAL** | Whole-run cache vs section skip documented in dispatch. |
| L0.4 Grounded/action shaping | R3/R4 handoff shapes | `grounding_required`, route family in profile | `RouteContract` fields | **ALIGNED** | — |
| L0.5 Managed workflow | execution_form | `APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED` harness | L3 entry in core spine | **PARTIAL** | **GAP-AR-L3-1:** No `apps_rg/runtime/bindings/l3_binding.py`. |
| L0.6 RouteContract | exactly one contract | Emits signed `RouteContract` | Contract + validation | **ALIGNED** | — |

---

## C0 — Context / grounding (C0.0–C0.6)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| C0.0 Preflight | route grants grounding | [`c0_retrieve_apps_rg`](../../apps_rg/runtime/bindings/c0_binding.py) | `FinalEvidenceContract`, `GateVerdict` types | **PARTIAL** | Path A uses [`section_c03_graph_binding`](../../apps_rg/runtime/c03_graphrag_bound.py) — not product C0. |
| C0.1 Retrieval plan | dense/sparse/graph plan | Dense BGE + sparse seam; graph **deferred** | `hybrid_search_engine`, `c0_sparse_exact_seam` | **PARTIAL** | **GAP-AR-C0-1:** `C0_GRAPH_LANE_NA_REF` — no C0.3 graph RAG on spine binding phase 1. **GAP-AR-C0-2:** Section FEC is `fec_shape_only` snapshot. |
| C0.2 Evidence fetch | hydrate spans | Chroma dense when enabled; sparse lane | Core retrieval seams | **PARTIAL** | Live proof blocked when sparse/BM25 unavailable (substitute burndown). |
| C0.3 Graph RAG | bounded expansion | NOT_APPLICABLE (deferred) | Graph engines in core | **MISSING** | **GAP-AR-C0-3:** Misnamed `c03_graphrag_bound` on section path (terminology SSOT exists; behavior gap remains). |
| C0.4 Stratify | MUST_USE / SUPPORTING / … | Support status on FEC items | FEC status enums in core | **ALIGNED** | — |
| C0.5 FinalEvidenceContract | PASS/WEAK/… | Emits `FinalEvidenceContract` on path B | Contract validation | **PARTIAL** | Path A does not emit canonical FEC from spine C0. |
| C0.6 Weak support refinement | one retry | Limited / env-gated | — | **PARTIAL** | **GAP-AR-C0-4:** Weak-support loop not fully parity with v40. |

**Integrated wiring:** [`apps_rg_dispatch.run_ag2_retrieval_and_prompt`](../../agentic_core/runtime/entry/apps_rg_dispatch.py) → app `c0_binding` / `pa_binding` (W-A fixed).

---

## PA — Prompt assembly (PA.0–PA.7)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| PA.0 Boundary | L1/L0/C0 present | `pa_compose_apps_rg` checks route + FEC | `CompiledPromptArtifact`, slot contracts | **PARTIAL** | Section path: `build_section_prompt_artifact` — parallel PA. |
| PA.1 BOM | S0–R0 slots | [`prompt_bom.yaml`](../../apps_rg/prompt_assembly/prompt_bom.yaml) + profile | Core CPA types | **PARTIAL** | **GAP-AR-PA-1:** Section PA does not emit spine `CompiledPromptArtifact` shape uniformly. |
| PA.2–PA.7 Compose/render/sign | canonical order, airlock | `pa_compose_apps_rg` + section helpers | `CompiledPromptArtifact`, `PromptBlock`, `Origin` | **PARTIAL** | **GAP-AR-PA-2:** Provider render path split (`l2_envelope_adapter` vs section compiled JSON). |

---

## L3 — Orchestration (L3.1–L3.4)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| L3.1–L3.4 Managed workflow | DAG, step contracts, merge | **No app L3 binding**; L0 profile selects `MANAGED_WORKFLOW`; W9 E2E in core entry | `integrated_single_action_spine_run`, L3 in core | **PARTIAL** | **GAP-AR-L3-1:** apps_rg does not own L3 step packaging; relies on core orchestrator. Acceptable if documented as generic-only. |

---

## L2 — Execute (E1–E5)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| E1 Prep | frozen execution room | `l2_binding_adapter` / `l2_envelope_adapter` | `FrozenExecutionContext`, L2 v4 types | **PARTIAL** | **GAP-AR-L2-1:** Product section lanes call Qwen/vLLM directly — not always `l2_execute_apps_rg`. |
| E2 Valid | signature, capability | `evaluate_apps_rg_l2_quality_precheck` | Core validation types | **PARTIAL** | — |
| E3 Exec | MODEL/TOOL/ACTION lanes | Section providers + `l2_execute_package_driven` | `ProviderGateway`, `l2_execute_package_driven` | **DIVERGENT** | **GAP-AR-L2-2:** Two L2 owners (documented in boundary doc). **GAP-AR-L2-3:** `l2_envelope_adapter` stack hard to audit. |
| E4 Heal | same-authority repair | App policy + core heal rules | `is_repair_allowed`, healers | **PARTIAL** | — |
| E5 Seal | SealedL2Artifact | Section: `l2_output.json` not always `SealedL2Artifact` | `SealedL2Artifact` contract | **MISSING** | **GAP-AR-L2-4:** Section path missing canonical `SealedL2Artifact` (inventory matrix). |

---

## Exit — Evaluation (5.1–5.7, X1–X3)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| 5.1–5.5 X1/X2/X3 | ExitReviewPacket, one X3 | Path A: X2 → X1D → `aggregate_x3`; Path B: `ExitEvalPipeline` | [`exit_binding`](../../apps_rg/runtime/bindings/exit_binding.py), `ExitEvalPipeline`, `x3_disposition` | **DIVERGENT** | **GAP-AR-EXIT-1:** Two exit paths. **GAP-AR-EXIT-2:** Section does not emit spine `ExitDispositionReceipt` (W-B partial: `disposition_authority`). **GAP-AC-EXIT-1:** [`resume_judges`](../../agentic_core/runtime/judges/resume_judges/) still in core (EV-2). |
| 5.6 HITL | freeze / re-clearance | `hitl_trigger_policy.yaml` (app) | L5 re-clearance in core | **PARTIAL** | — |
| 5.7 Response + exhaust | RuntimeExhaustBundle | Lane-local `runtime_exhaust_bundle.json` | Core exhaust bundle type | **PARTIAL** | **GAP-AR-EXIT-3:** Lane exhaust ≠ spine exhaust schema. |

---

## UWG + L4 — Durable write

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| UWG.1–UWG.7 | commit validation | R1B cache promotion gateway ([`r1b_uwg_promotion`](../../apps_rg/cache/r1b_uwg_promotion.py)); not on section CLI | Generic UWG in core | **PARTIAL** | **GAP-AR-UWG-1:** Section path never invokes UWG (by design). **GAP-AR-L4-1:** L1 does not consume L4 planning priors at runtime. |

---

## L6 — Post-run learning (L6.1–L6.7)

| Substep | v40 | apps_rg bind | agentic_core bind | Fit | Gaps |
|---------|-----|--------------|-------------------|-----|------|
| L6.1–L6.7 | after run boundary | [`build_l6_shadow_package`](../../apps_rg/runtime/shadow/) per section; offline only | [`apps_rg_learning_adapter`](../../agentic_core/runtime/l6/apps_rg_learning_adapter.py) | **DIVERGENT** | **GAP-AR-L6-1:** Section L6 is shadow-only (correct). **GAP-AC-L6-1:** Learning adapter in core — verify no current-run mutation (observer law). |

---

## Gap roll-up (counts)

| Owner | P0 | P1 | P2 | Total |
|-------|----|----|-----|-------|
| **apps_rg (GAP-AR-*)** | 6 | 12 | 8 | 26 |
| **agentic_core (GAP-AC-*)** | 2 | 5 | 4 | 11 |

**P0 (blocks one-spine truth):** GAP-AR-C0-2, GAP-AR-EXIT-1/2, GAP-AR-L2-4, GAP-AR-U0-3, GAP-AR-00C-1, GAP-AC-L0-1  
**P1 (confusion / boundary):** GAP-AC-U0-1, GAP-AR-L0-1, GAP-AR-PA-1, GAP-AC-EXIT-1, GAP-AR-L2-1, …  
**P2 (documentation / N/A):** GAP-AR-L1-3, GAP-AR-L1-2, GAP-AR-L3-1, …

---

## Related artifacts

| Artifact | Role |
|----------|------|
| [one_spine_inventory.py](../../apps_rg/runtime/one_spine_inventory.py) | Two-path contract bypass matrix |
| [section_spine_terminology.py](../../apps_rg/runtime/section_spine_terminology.py) | Honest naming SSOT |
| [apps_rg_binding_hardening_critical_closeout_receipt.md](apps_rg_binding_hardening_critical_closeout_receipt.md) | W-A complete |
| [proof_pool_c0_ssot_gap_audit.json](../../artifacts/apps_rg/plans/proof_pool_c0_ssot_gap_audit.json) | C0 proof-pool gaps |

---

## Explicit non-claims

- No PASS on integrated spine live runtime for all layers.
- Gap severities are architectural assessment, not CI gate results.
- v40 SSOT does not enumerate per-app bindings; this doc is the apps_rg overlay.
