# PA Prompt Assembly Exec Flowchart — Repo Gap Analysis

**Generated:** 2026-05-23  
**SSOT reference:** [PA_Prompt_Assembly_exec.md](../../reference/03B_PA_Prompt_Assembly/PA_Prompt_Assembly_exec.md)  
**Companion spec:** [PA_Prompt_Assembly.md](../../reference/03B_PA_Prompt_Assembly/PA_Prompt_Assembly.md)  
**Machine audit:** [pa_exec_flowchart_gap_audit.json](../../artifacts/apps_rg/plans/pa_exec_flowchart_gap_audit.json)  
**Execution plan:** [.cursor/plans/pa-exec-flowchart-gap-f2a8c3.md](../../.cursor/plans/pa-exec-flowchart-gap-f2a8c3.md)  
**Notion (Plans DB):** [pa-exec-flowchart-gap-f2a8c3](https://www.notion.so/pa-exec-flowchart-gap-f2a8c3-36927693f55c8138afb7fe72202f206a)  
**Related (narrower, E0 SSOT — closed):** [prompt_assembly_ssot_gap_analysis_20260523.md](prompt_assembly_ssot_gap_analysis_20260523.md)

---

## Executive summary

The repo implements **three parallel PA surfaces** that only partially match the exec flowchart (PA.0 → PA.8 → signed L2 handoff):

| Surface | Location | Exec alignment |
|---------|----------|----------------|
| **A — Core PA pipeline** | `agentic_core/prompt_governance/prompt_assembly/` | PA.0, PA.3 (partial), PA.5, PA.7 stub wired in `run_prompt_assembly_pipeline`; PA.2, PA.4, PA.6, PA.8 **not** in pipeline |
| **B — apps_rg integrated spine** | `apps_rg/runtime/bindings/pa_binding.py` → `pa_compose_apps_rg` | Two-block `CompiledPromptArtifact` (core contract); **no** PA.0–PA.8 pipeline, **no** HMAC/manifest |
| **C — apps_rg section W9 compile** | `apps_rg/prompt_assembly/compiler.py` + `runtime/sections/*_pa.py` | Strongest 8-slot compile path; **local** `CompiledPromptArtifact` type; not unified with core pipeline or spine handoff |

**P0 gaps (blocks “one signed artifact per L2 invocation”):** GAP-PA-INT-1 (integrated path bypasses core PA), GAP-PA-SIGN-1 (no HMAC / `L2HandoffEnvelope` on product paths), GAP-PA-PIPE-1 (PA.2/PA.4/PA.6/PA.8 absent from runtime pipeline).

**P1 gaps:** dual `CompiledPromptArtifact` contracts, section vs integrated divergence, incomplete OTEL child spans, PA.3 airlock not wired on apps_rg lanes.

**Recently closed (orthogonal):** E0 examples YAML hydration ([apps-rg-pa-ssot-gap-b8e4f1](../../.cursor/plans/apps-rg-pa-ssot-gap-b8e4f1.md)) — does **not** close exec-flowchart spine gaps.

---

## Methodology

For each exec substep (PA.0–PA.8) and control spine item:

1. Map intended behavior from [PA_Prompt_Assembly_exec.md](../../reference/03B_PA_Prompt_Assembly/PA_Prompt_Assembly_exec.md).
2. Locate implementation in `agentic_core` and `apps_rg` (bindings, compiler, pipeline, gates, tests).
3. Classify per path: **ALIGNED** | **PARTIAL** | **MISSING** | **DIVERGENT** (intentional).
4. Assign gap IDs `GAP-PA-*` with priority P0–P3.

**Non-claims:** No live integrated-spine end-to-end PA proof run for this document. Assessment is structural (code + contract tests + gate inventory).

---

## Upstream contracts (pre-PA.0)

| Exec requirement | apps_rg | agentic_core | Fit | Gaps |
|------------------|---------|--------------|-----|------|
| L1PlanContract, L0 RouteContract, C0 FEC when grounded | Integrated + section front bridge emit contracts | Contract types + validators | **ALIGNED** | — |
| AgentSpec, response schema, provider lane | Section templates + `rg_output_schema.json` | Package-driven PA binding | **PARTIAL** | **GAP-PA-UP-1:** `pa_compose_apps_rg` does not bind R0/tool schemas as structured provider fields |
| policy_hash / replay_key / blueprint_hash bound | Partial on `pa_compose_apps_rg` (`replay_key`, component hashes) | `run_prompt_assembly_pipeline` reads from execution_metadata | **PARTIAL** | **GAP-PA-UP-2:** No `blueprint_hash` / `route_digest` on apps_rg integrated artifact |
| PA must not retrieve, route, execute, write, approve | Section/compiler path respected | Core pipeline respects boundary | **PARTIAL** | Section lanes still call providers in L2 after local compile (by design); PA layer itself does not execute |

---

## PA.0 — Boundary check

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| `PAAssemblyInput`, `BoundaryCheckReceipt`, `assembly_gap_report` | `pa0_boundary.py` + pipeline PA.0 | **ALIGNED** (core module) | **GAP-PA-INT-1:** `pa_compose_apps_rg` does not call `boundary_check` |
| STOP AS PA GAP on missing refs | Pipeline short-circuits on FAIL | **PARTIAL** | Section compile fails via `PromptAssemblyError`, not canonical gap report shape |
| No retrieval/route/provider/L4 | Enforced in core PA.0 checks | **ALIGNED** | — |

**Canonical (core):** `agentic_core.prompt_governance.prompt_assembly.pa0_boundary.boundary_check`

---

## PA.1 — Load / resolve prompt BOM

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| `PromptBOM`, `component_hash_map` | `pa1_bom_resolver.py`; `apps_rg/prompt_assembly/prompt_bom.yaml` | **PARTIAL** | Pipeline emits `PromptBOMResolved` marker only; does not invoke `pa1_bom_resolver` |
| Stable ref/hash per component | Section compiler `ComponentHashMap` | **PARTIAL** | Integrated path: flat `component_hash_map` without BOM slot refs |
| S0, D0, I0, E0, C0, R0, tools, execution metadata | BOM + registry cover slots | **ALIGNED** (declarative) | **GAP-PA-BOM-1:** IBM/headline lanes optional E0 while BOM globally requires E0 |

---

## PA.2 — Slot composition

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| Canonical order S0→D0→I0→E0→C0→M0→U0→H0; R0 as schema binding | `pa2_slot_composition.py`; `compiler.py` `CANONICAL_SLOT_ORDER` | **PARTIAL** | **GAP-PA-PIPE-1:** `compose_slots` **not** called from `run_prompt_assembly_pipeline` |
| `StructuredPromptSlots`, `slot_authority_map`, `slot_lineage_map` | Section artifact has `slot_lineage_map` / payloads | **PARTIAL** | Integrated: only `slot_lineage_map` on 2 blocks, not full slot model |
| Lower authority cannot override higher | Compiler `OVERRIDE_ATTEMPT_PATTERNS`; G10 gate | **PARTIAL** | No runtime `slot_conflict_map` receipt |

**Note:** apps_rg compiler order includes Y0/R0/H0/M0 positions that differ slightly from exec prose (documented in [apps_rg_pa_prompt_contract.md](../../guides/apps_rg_pa_prompt_contract.md)).

---

## PA.3 — Airlock / security pass

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| U0 neutralization, C0 classifier, H0 re-entry validation | `pa3_u0_airlock.py`, `pa3_c0_classifier.py`, `pa3_h0_healer.py` | **PARTIAL** | Pipeline runs C0 classifier only when `c0_chunks` passed; U0/H0 not in pipeline |
| `AssemblySecurityPassReceipt`, `safe_slot_payload_map` | `AssemblySecurityReceipt` in package-driven binding | **PARTIAL** | **GAP-PA-AIR-1:** W9 section compile does not emit security pass receipt |
| OTEL `pa.airlock` | `apps_qna`/`apps_lic` airlocks emit spans | **PARTIAL** | Not on apps_rg section PA compile path |

---

## PA.4 — Validate slot contract

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| `SlotValidationReceipt`, authority/context contract receipts | `pa4_validation.py` | **MISSING** (runtime) | **GAP-PA-PIPE-1:** Module exists; **not** in pipeline |
| Y0 requires promotion refs | BOM/compiler advisory rules | **PARTIAL** | No promotion-ref gate at compile |
| Tools/schemas as structured bindings | R0 in section artifacts | **PARTIAL** | Integrated path: no native tool/response_schema fields |

---

## PA.5 — Token budget / determinism

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| `TokenBudgetLedger`, deterministic trim order | `pa5_budget.py` + pipeline | **ALIGNED** (core pipeline) | **GAP-PA-INT-1:** apps_rg paths do not call pipeline budget stage |
| `PA_BUDGET_OVERFLOW` | `OverflowStatus` in pa5 | **PARTIAL** | Section compiler `token_estimate` only; no overflow stop code |
| Preserve S0/D0/I0, R0, must-use C0 first | Trim order in exec spec | **PARTIAL** | Not proven on section compile path |

---

## PA.6 — Provider-aware rendering

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| Lanes: Anthropic, OpenAI GPT, OpenAI Reasoning, Gemini | `pa6_provider_rendering.py` | **MISSING** (runtime) | **GAP-PA-PIPE-1:** Not in pipeline |
| `ProviderRenderManifest`, `provider_field_mapping_receipt` | Local artifact field `provider_render_manifest` (apps_rg contract) | **PARTIAL** | Not populated on integrated `pa_compose_apps_rg` |
| C0 never rendered as instruction | Package-driven + compiler fences | **PARTIAL** | Integrated path concatenates evidence into user block semantics only |

---

## PA.7 — Final emit / compiled artifact

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| `compiled_prompt_artifact_id`, BOM/slots/manifest refs | Core `CompiledPromptArtifact` + apps_rg local artifact | **DIVERGENT** | **GAP-PA-ART-1:** Two `CompiledPromptArtifact` types (core W6 vs `apps_rg.prompt_assembly.contracts`) |
| `manifest_hash`, HMAC signature | `orchestrator.sign_manifest`, `pa7_signature.py` | **MISSING** (product) | **GAP-PA-SIGN-1:** Neither integrated nor section path emits HMAC; exec: unsigned cannot be L2-ready |
| `L2HandoffEnvelope` | Not found on apps_rg product paths | **MISSING** | **GAP-PA-SIGN-2** |
| All receipts linked (security, validation, budget, trim) | Doctrine receipts in pipeline only | **PARTIAL** | Section path: compile receipt only |

**Canonical integrated:** `apps_rg.runtime.bindings.pa_binding.pa_compose_apps_rg`  
**Canonical section:** `apps_rg.runtime.bindings.section_prompt_adapter.compile_section_prompt`

---

## PA.8 — Authority red-team

| Exec emit | Implementation | Fit | Gaps |
|-----------|----------------|-----|------|
| `SlotAuthorityProof` | Doc + `tools/prompt_assembly/runtime_evidence.py` references | **MISSING** (runtime) | **GAP-PA-PIPE-1:** No `pa.red_team_scan` in pipeline |
| Adversarial fixtures (C0 promotion, U0 override, trim authority drop) | L5 red-team templates exist elsewhere | **PARTIAL** | Not wired as PA.8 gate before L2 on apps_rg |

---

## Control and proof spine

| Exec requirement | Repo state | Fit | Gaps |
|------------------|------------|-----|------|
| Runtime gates G10, G13, G17, G21, G23 | G10 `g10_prompt_assembly.py` implemented | **PARTIAL** | G13/G17/G21/G23 not mapped per PA stage in apps_rg runtime |
| OTEL `pa.run` children (9 spans) | `span_contracts.py` lists some; pipeline events partial | **PARTIAL** | **GAP-PA-OTEL-1:** Missing `pa.bom_resolve`, `pa.slot_compose`, `pa.slot_validate`, `pa.render`, `pa.red_team_scan` on product paths |
| Prove: no retrieval/route/provider/tool/L4/final answer from PA | Core pipeline + binding tests | **PARTIAL** | Contract tests cover slices; no single spine proof bundle for apps_rg PA |
| Exactly one signed envelope | Exec requirement | **MISSING** | **GAP-PA-SIGN-1** |

---

## Two-path matrix (apps_rg product)

| Capability | Section CLI (`--section`) | Integrated (`python -m apps_rg`) |
|------------|-------------------------|-----------------------------------|
| 8-slot YAML compile | Yes (`compiler.py`) | No |
| Core `CompiledPromptArtifact` (W6) | Via adapter → local type mismatch | Yes (`pa_compose_apps_rg`) |
| `run_prompt_assembly_pipeline` | No | No |
| HMAC / manifest_hash | No | No |
| FEC in prompt | Section C0 capsules | `pa_compose` uses digest only (no FEC blocks in prompt) |
| E0 from examples YAML | Yes (W9 lanes, post b8e4f1) | N/A |

---

## Gap roll-up

| Priority | Count | IDs |
|----------|-------|-----|
| **P0** | 3 | GAP-PA-INT-1, GAP-PA-SIGN-1, GAP-PA-PIPE-1 |
| **P1** | 5 | GAP-PA-ART-1, GAP-PA-SIGN-2, GAP-PA-AIR-1, GAP-PA-OTEL-1, GAP-PA-UP-1 |
| **P2** | 4 | GAP-PA-UP-2, GAP-PA-BOM-1, GAP-PA-DUAL-PATH (section vs integrated), GAP-PA-DOCS-STALE-PATH |
| **P3** | 1 | GAP-PA-DUAL-CONTRACT-TREES (accepted; see SSOT gap doc) |

---

## Explicit non-claims

- No PASS on live integrated spine PA with full PA.0–PA.8 receipts.
- Gap severities are architectural, not CI gate results (except where cited SSOT audit shows `p0_count: 0` for E0-only scope).
- `agentic_core` edits for generic PA spine convergence require separate author-gate / migration receipt per core boundary rules.

---

## Related artifacts

| Artifact | Role |
|----------|------|
| [one_spine_inventory.py](../../apps_rg/runtime/one_spine_inventory.py) | Section vs integrated bypass matrix |
| [apps_rg_v40_spine_gap_analysis_20260523.md](apps_rg_v40_spine_gap_analysis_20260523.md) | Full v40 layer gaps (PA section abbreviated) |
| [check_prompt_assembly_ssot.py](../../ops_scripts/ci/check_prompt_assembly_ssot.py) | E0/registry CI ratchet |
| [orchestrator.py](../../agentic_core/prompt_governance/orchestrator.py) | Core bridge: FEC → pipeline → signed envelope (proof harness) |
