# apps_research Spine Alignment Report

Plan: `apps-research-spine-alignment-c0-briefing-2f8a4b`
Status: **W1–W5 COMPLETE**
Generated: 2026-05-04

---

## Summary

This report documents all changes made during the 5-wave spine alignment plan for `apps_research`.
The goal was to bring `apps_research` into full conformance with the canonical spine terminology
(`R3_SIMPLE_GROUNDED_READ`, `C0`, `PA`, `L2 E1–E5`) and to augment the C0 engine with structured
depth profiles, adaptive coverage families, JD context, 7 structured C0 output objects, and a
C0-to-PA gate with `PASS / WEAK_WITH_CAVEATS / FAIL` verdicts.

---

## Wave Summary

| Wave | Phases | Focus | Status |
|------|--------|-------|--------|
| W1 | 1.1–1.3 | Terminology cleanup — retire Hop/DAG language; clarify R3/R5/post-R3 | ✅ DONE |
| W2 | 2.1–2.4 | Domain contract schema additions (9 new YAML files) | ✅ DONE |
| W3 | 3.1–3.3 | Cache profiles, retrieval profiles, prompt profiles updated | ✅ DONE |
| W4 | 4.1–4.7 | C0 engine augmentation: depth profiles, coverage families, JD context, 7 C0 objects, gate | ✅ DONE |
| W5 | 5.1–5.4 | FEC extension, 43-test suite, negative controls YAML, this report | ✅ DONE |

---

## Files Changed

### Wave 1 — Terminology

| File | Change |
|------|--------|
| `apps_research/TECHNICAL_SPEC.md` | Rewrote to use U0/L1/L0/R3/C0/PA/L2 E1-E5 terminology; removed "Hop N" / "inner DAG" |
| `apps_research/README.md` | Updated architecture section; removed "3-stage inner DAG" |
| `apps_research/RUNBOOK.md` | Updated flow description to use spine stage names |
| `apps_research/config/hop_pipeline.py` | Module docstring rewritten; "HOP pipeline topology" → "apps_research inner pipeline" |
| `apps_research/integrations/governed_research_run.py` | `hop_checkpoints` docstring updated |
| `apps_research/engines/company_brief_engine.py` | Removed "V2 retrieval pipeline" hop references |
| `apps_research/integrations/execution_adapter.py` | Receipt names renamed to `L2.E1–E5.research_*` |
| `apps_research/config/route_registry.yaml` | R3/R5/post-R3 description clarified |
| `apps_research/spine_manifest.yaml` | R5 distinct from post-R3 note added; Lincoln depth-exemplar note |

### Wave 2 — Domain Contract Schema

| File | Change |
|------|--------|
| `apps_research/config/domain_contract/research_depth_profiles.yaml` | New — 4 canonical depth profiles |
| `apps_research/config/domain_contract/briefing_coverage_matrix_schema.yaml` | New — coverage matrix schema |
| `apps_research/config/domain_contract/source_portfolio_schema.yaml` | New — source portfolio schema |
| `apps_research/config/domain_contract/claim_evidence_map_schema.yaml` | New — claim evidence map schema |
| `apps_research/config/domain_contract/contradiction_matrix_schema.yaml` | New — contradiction matrix schema |
| `apps_research/config/domain_contract/freshness_policy.yaml` | New — freshness policy schema |
| `apps_research/config/domain_contract/source_mix_policy.yaml` | New — source mix policy schema |
| `apps_research/config/domain_contract/synthesis_guidance_schema.yaml` | New — synthesis guidance schema |
| `apps_research/config/domain_contract/jd_context_schema.yaml` | New — JD context schema |
| `apps_research/config/domain_contract/app_domain_manifest.yaml` | Added W2 schema refs + negative controls |
| `apps_research/config/domain_contract/input_contract.yaml` | Added `jd_ref`, `jd_content_hash`, `jd_context`, `depth_profile` optional inputs |

### Wave 3 — Profile Updates

| File | Change |
|------|--------|
| `apps_research/config/domain_contract/cache_profiles.yaml` | JD-digest cache participation; per-depth TTL variants; R1A/R1B terminal spec |
| `apps_research/config/domain_contract/retrieval_profiles.yaml` | SearXNG + web sources; per-depth retrieval config; JD retrieval families |
| `apps_research/config/domain_contract/prompt_profiles.yaml` | JD/depth/C0 output slots; DATA/JD_CONTEXT/ANALYSIS fence rules |

### Wave 4 — C0 Engine Augmentation

| File | Change |
|------|--------|
| `apps_research/engines/company_brief_engine.py` | `_DEPTH_PROFILES`, `_DEPTH_PARAM_MAP`, `_resolve_depth_profile()`, `_COVERAGE_FAMILY_CATALOG`, `_PROFILE_REQUIRED_FAMILIES`, `_run_research_adaptive()`, `_resolve_jd_context()`, `_jd_context_to_facets()`, `_build_c0_bundle()`, `_evaluate_c0_pa_gate()`, updated `execute()` |
| `apps_research/engines/research_assembly_engine.py` | `execute()` accepts `company_brief_result`; `_resolve_pa_slot_bindings()`; `ResearchAssemblyResult` gains `c0_bundle`, `pa_slot_bindings`, `gate_verdict` |
| `apps_research/integrations/execution_adapter.py` | `submit()` receipt renamed to `L2.E5.research_result_submitted.<run_id>`; added `l2_receipts` dict with `L2.E1–E5` keys |

### Wave 5 — FEC + Tests + Report

| File | Change |
|------|--------|
| `apps_research/cert/fec_producer.py` | `schema_version` → `1.1`; added 15 briefing-grade fields + 8 JD fields; `_safe_int()` helper |
| `apps_research/config/domain_contract/negative_controls.yaml` | Expanded from 2 to 23 controls (12 baseline + 11 JD) |

---

## Files Created

| File | Description |
|------|-------------|
| `apps_research/config/domain_contract/research_depth_profiles.yaml` | W2 — 4 canonical depth profiles |
| `apps_research/config/domain_contract/briefing_coverage_matrix_schema.yaml` | W2 — coverage matrix schema |
| `apps_research/config/domain_contract/source_portfolio_schema.yaml` | W2 — source portfolio schema |
| `apps_research/config/domain_contract/claim_evidence_map_schema.yaml` | W2 — claim evidence map schema |
| `apps_research/config/domain_contract/contradiction_matrix_schema.yaml` | W2 — contradiction matrix schema |
| `apps_research/config/domain_contract/freshness_policy.yaml` | W2 — freshness policy schema |
| `apps_research/config/domain_contract/source_mix_policy.yaml` | W2 — source mix policy schema |
| `apps_research/config/domain_contract/synthesis_guidance_schema.yaml` | W2 — synthesis guidance schema |
| `apps_research/config/domain_contract/jd_context_schema.yaml` | W2 — JD context schema |
| `tests/_apps_contract/test_apps_research_spine_alignment.py` | W5 — 43 tests (20 golden/JD + 23 negative controls) |
| `apps_research/SPINE_ALIGNMENT_REPORT.md` | W5 — this deliverable report |

---

## Test Coverage

| Suite | Count | Scope |
|-------|-------|-------|
| Route registry IDs | 5 | `route_registry.yaml`, `cert_route_registry.yaml`, `spine_manifest.yaml` |
| Depth profiles | 4 | `_DEPTH_PROFILES`, `_resolve_depth_profile()`, source floor |
| Coverage families | 2 | `_PROFILE_REQUIRED_FAMILIES`, DOSSIER = all families |
| C0 bundle + gate | 5 | `_build_c0_bundle()`, `_evaluate_c0_pa_gate()`, PASS/FAIL/WEAK |
| JD context | 2 | `jd_content_hash` computation, `apps_rg_downstream_fields` |
| FEC producer | 4 | `schema_version`, `research_depth_profile`, JD fields, absent-JD Nones |
| L2 receipt names | 2 | ≥5 distinct `L2.E*.research_*` patterns; no `Hop N` in source |
| Negative baseline | 12 | Route contract, source floor, contradiction, freshness, vendor, Lincoln, L3 |
| Negative JD | 11 | content_hash, JD_DECLARED classification, prompt injection, fencing, downstream binding |
| YAML contract | 1 | `negative_controls.yaml` baseline IDs present |
| **Total** | **43** | |

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| `grep -rn "Hop [0-9]\|inner DAG\|HOP pipeline topology" apps_research/` → zero (excluding symbol names) | ✅ |
| `route_registry.yaml routes[0].route_id == "R3_SIMPLE_GROUNDED_READ"` | ✅ |
| `cert_route_registry.yaml routes[0].route_id == "R3_SIMPLE_GROUNDED_READ"` | ✅ |
| `spine_manifest.yaml` contains `R3_SIMPLE_GROUNDED_READ` and `R5_PRE_ROUTE_FALLBACK` | ✅ |
| `_DEPTH_PROFILES["COMPANY_BRIEF_DEEP"].min_sources == 18` | ✅ |
| `_evaluate_c0_pa_gate()` returns PASS / WEAK_WITH_CAVEATS / FAIL | ✅ |
| `c0_bundle` contains all 7 required output objects | ✅ |
| `fec_producer.produce_fec()` schema_version == "1.1" with briefing-grade fields | ✅ |
| `negative_controls.yaml` has 23 entries | ✅ |
| `execution_adapter.submit()` receipt_id uses `L2.E5.research_result_submitted.*` | ✅ |
| `ResearchAssemblyResult` carries `c0_bundle`, `pa_slot_bindings`, `gate_verdict` | ✅ |
| JD content fenced as `JD_CONTEXT` in PA slot bindings | ✅ |

---

## Gap Register (Deferred)

| Gap | Reason deferred |
|-----|----------------|
| GAP-8 full FEC ↔ Exit v6 integration test (live pipeline) | Requires `apps_research --apps-e2e-live`; deferred to E2E wave |
| Real SearXNG retrieval with live COMPANY_BRIEF_DOSSIER depth | Network-bound; offline test suite uses stubs |
| `query_decomposer.py` C0 query fan-out wiring (referenced in W4 plan) | Not in W4 explicit scope; deferred |

---

*No certification claim. This report documents static structural evidence only.*
