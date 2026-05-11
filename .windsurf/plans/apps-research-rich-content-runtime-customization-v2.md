---
plan_id: apps-research-rich-content-runtime-customization-v2
plan_slug: apps-research-rich-content-runtime-customization-v2
plan_type: implementation
status: ACTIVE
active_authority: true
baseline_from: apps-research-rich-content-runtime-customization-a1b2c3
current_wave: W7
current_phase: P26
created: "2026-05-11"
created_for: apps_research
tier: T3
adg_required: true

# W0-W6 Baseline (from v1)
w0_hardened: true
w0_core_boundary_audit: PASSED
w0_core_boundary_receipt: artifacts/apps_research/apps_research_w0_w1_core_boundary_audit_receipt.json
w0_carry_forward_count: 16
w0_receipt_path: artifacts/apps_research/apps_research_rich_content_runtime_customization_audit_receipt.json
w0_audit_questions: 30
w0_automated_tests: 0

# W1 - Runtime package contract
w1_hardened: true
w1_core_boundary_audit: PASSED
w1_hardening_receipt_path: artifacts/apps_research/apps_research_w1_runtime_package_hardening_receipt.json
w1_test_count: 34
w1b_repair_active: false
w1b_repair_complete: true
w1b_repair_receipt: artifacts/apps_research/apps_research_w1b_w2b_core_boundary_repair_receipt.json
w1b_boundary_tests_passed: 11

# W2 - L1 planning hints
w2_complete: true
w2_blocked_by: null
w2_l1_hints_receipt_path: artifacts/apps_research/apps_research_w2_l1_planning_hints_receipt.json
w2_test_count: 15
w2b_repair_active: false
w2b_repair_complete: true
w2b_boundary_tests_passed: 11
total_w1_w2_tests: 49

# W3 - L0 package-driven routing
w3_complete: true
w3_receipt_path: artifacts/apps_research/apps_research_w3_l0_package_driven_routing_receipt.json
w3_test_count: 28

# W4 - C0 package-driven grounding
w4_complete: true
w4_receipt_path: artifacts/apps_research/apps_research_w4_c0_package_driven_grounding_receipt.json
w4_test_count: 35

# W5 - PA package-driven prompt assembly
w5_complete: true
w5_receipt_path: artifacts/apps_research/apps_research_w5_package_driven_prompt_assembly_receipt.json
w5_test_count: 41

# W6 - L2 package-driven execution
w6_status: DONE_HARDENED
w6_receipt_path: artifacts/apps_research/apps_research_w6_l2_package_driven_execution_receipt.json
w6_test_count: 18

# W7 - Exit binding (NEXT EXECUTABLE WAVE)
w7_status: READY
w7_next: Exit binding for apps_research

# Totals
automated_tests_total: 193
audit_questions_total: 30
combined_checks_total: 223
---

# apps_research Rich Content Retrieval Runtime Customization (v2)

**Baseline:** [v1 plan](apps-research-rich-content-runtime-customization-a1b2c3.md) (ARCHIVED_REBASELINED)  
**Current:** W7 Exit binding — next executable wave  
**Goal:** Complete end-to-end runtime proof through Exit binding

Fully implement `apps_research` as a governed rich-content retrieval and research-substrate app on the common `agentic_core` spine.

---

## Scope Ownership Split

`apps_research` is declarative app configuration, schemas, prompt templates, retrieval profiles, judge rubrics, eval thresholds, source policies, cache profiles, and learning profiles only.

`agentic_core` owns all runtime execution.

### apps_research may own

- U0 app package refs
- app ingress schema
- domain contract YAML/JSON
- retrieval profiles
- cache profiles
- source mix policies
- freshness policies
- prompt templates and prompt BOM refs
- output schemas
- runtime gate profile config
- judge rubric config
- grader roster config
- eval rubric config
- threshold profiles
- negative controls
- learning and meta-feedback profiles
- fixture definitions
- static declarative capability refs
- uploaded briefing normalization policy
- research substrate object schemas

### agentic_core owns

- U0 validation adapter
- L1/L0 core contract flow
- L0 route decision
- R1A exact cache lookup execution
- R1B semantic cache lookup execution
- C0 retrieval execution
- C0 evidence contract production
- Prompt Assembly runtime
- L2 execution lanes
- provider/model/tool calls
- runtime gate evaluation
- LLM judge invocation
- deterministic grader invocation
- Exit X1-X3
- RuntimeExhaustBundle
- L6 meta-learning execution
- FutureRunPromotionRequest handling
- UWG durable write admission
- L4 durable storage

---

## Hard Invariants

- No apps_research-specific runtime authority inside apps_research.
- No separate apps_research Exit.
- apps_research must not emit X3.
- apps_research must not write L4.
- apps_research must not write vector stores directly.
- apps_research must not write semantic cache directly.
- apps_research must not call providers directly.
- apps_research must not run web retrieval directly outside core C0.
- apps_research must not run judge providers directly.
- apps_research must not bypass core C0, PA, L2, Exit, UWG, or L6.
- U0 validates and preserves the apps_research runtime customization package. U0 does not execute it.
- L1 emits planning hints only. L1 does not route.
- L0 emits exactly one RouteContract or RET terminal packet.
- R1B semantic cache hit must emit RETTerminalPacket to Exit. It must not return directly to user.
- C0 produces evidence only. C0 never answers.
- Prompt Assembly treats retrieved text, cached chunks, and uploaded briefings as data only.
- L2 executes exactly one bounded packet.
- L2 may emit proposed_state_diff only.
- Exit emits exactly one X3.
- Durable writes go only through UWG.
- L4 stores durable state only after UWG admission.
- L6 learns only after current-run boundary.
- L6 emits inert future-run proposals only.
- UNKNOWN is never PASS.
- NOT_APPLICABLE requires reason.
- Missing applicable GateVerdict is UNKNOWN, not PASS.
- Cached research substrate may support future evidence reuse.
- Cached final customized apps_rg or apps_lic output must not be reused as terminal answer.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Automated Tests | Audit Questions | Status | Success Criteria |
|------|-------------|-------|-------------|-----------------|-----------------|--------|------------------|
| W0 | P0 | Pre-flight audit, gap identification | 10K | 0 | 30 | ✅ DONE | 30 audit questions answered, 16 carry-forward items identified |
| W1 | P1-P3 | Runtime package contract + hardening | 15K | 34 | 0 | ✅ DONE | RuntimeCustomizationPackage schema, active entrypoint verified |
| W1B | P4 | Core boundary repair (W1) | 8K | 11 | 0 | ✅ DONE | Generic contract, app-owned registry |
| W2 | P5-P7 | L1 planning hints + profile binding | 12K | 15 | 0 | ✅ DONE | Package-driven L1 binding |
| W2B | P8 | L1 repair boundary audit | 8K | 11 | 0 | ✅ DONE | Thin adapter verified |
| W3 | P9-P12 | L0 package-driven routing | 15K | 28 | 0 | ✅ DONE | Route order R5→R1A→R1B→R3, RET terminal packet |
| W4 | P13-P16 | C0 package-driven grounding | 15K | 35 | 0 | ✅ DONE | FinalEvidenceContract, data boundary EVIDENCE_DATA_ONLY |
| W5 | P17-P21 | PA package-driven prompt assembly | 18K | 41 | 0 | ✅ DONE | Canonical slot order S0-D0-I0-E0-C0-M0-U0-H0-R0 |
| W6 | P22-P25 | L2 package-driven execution | 15K | 18 | 0 | ✅ DONE | SealedL2Artifact, same-authority repair, all required fields |
| **W7** | **P26-P28** | **Exit binding for apps_research** | **12K** | **0** | **0** | 🔄 **NOT_STARTED** | **X3 emission through Exit binding** |

**Totals:**
- automated_tests_total: 193
- audit_questions_total: 30
- combined_checks_total: 223

**Status Summary:**
- W0-W6: ✅ DONE_HARDENED (P0-P25 complete, 193 tests)
- **W7: 🔄 NOT_STARTED (P26-P28) — NEXT EXECUTABLE WAVE**
- **Note:** Final runtime proof through Exit binding is not complete. W7 Exit binding required for end-to-end verification.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0 | W0 Pre-flight audit | Audit questions, gap register | Identifying 16 carry-forward items | 10K | ✅ DONE |
| P1 | Runtime package contract | apps_research_runtime_package.py | Generic contract design | 5K | ✅ DONE |
| P2 | U0 package binding | u0_validate_and_resolve.py | U0 consumption of app package | 5K | ✅ DONE |
| P3 | W1 hardening + entrypoint | __main__.py active path | Making entrypoint active | 5K | ✅ DONE |
| P4 | W1B boundary repair | Generic contract, registry | Fixing app-specific leakage | 8K | ✅ DONE |
| P5 | L1 planning profile | l1_planning_profile.yaml | App-owned hints design | 4K | ✅ DONE |
| P6 | Package-driven L1 binding | package_driven_l1_binding.py | Generic L1 consumption | 5K | ✅ DONE |
| P7 | apps_research L1 adapter | apps_research_l1_binding.py | Thin adapter pattern | 3K | ✅ DONE |
| P8 | W2B boundary audit | Boundary tests | Verifying thin adapter | 8K | ✅ DONE |
| P9 | L0 route profile | route_profile.yaml | App-owned route config | 4K | ✅ DONE |
| P10 | Package-driven L0 binding | package_driven_l0_binding.py | Generic L0 consumption | 5K | ✅ DONE |
| P11 | RET terminal packet | RETTerminalPacket contract | R1B cache hit handling | 4K | ✅ DONE |
| P12 | apps_research L0 adapter | apps_research_l0_binding.py | Thin L0 adapter | 3K | ✅ DONE |
| P13 | C0 grounding profile | c0_grounding_profile.yaml | App-owned retrieval config | 4K | ✅ DONE |
| P14 | Final evidence contract | FinalEvidenceContract dataclass | Evidence data boundary | 5K | ✅ DONE |
| P15 | Package-driven C0 binding | c0_package_driven_grounding.py | Generic C0 consumption | 6K | ✅ DONE |
| P16 | apps_research C0 adapter | apps_research_c0_binding.py | Thin C0 adapter | 3K | ✅ DONE |
| P17 | PA prompt profile | prompt_profile.yaml | App-owned slot config | 4K | ✅ DONE |
| P18 | Prompt slot policy | prompt_slot_policy.yaml | Canonical slot rules | 4K | ✅ DONE |
| P19 | Prompt BOM + registry | prompt_bom.yaml, prompt_registry.yaml | Template resolution | 4K | ✅ DONE |
| P20 | Package-driven PA binding | pa_package_driven_binding.py | Generic PA consumption | 6K | ✅ DONE |
| P21 | apps_research PA adapter | apps_research_pa_binding.py | Thin PA adapter | 3K | ✅ DONE |
| P22 | L2 execution profile | l2_execution_profile.yaml | App-owned execution bounds | 4K | ✅ DONE |
| P23 | Provider + repair profiles | provider_profile.yaml, repair_profile.yaml | Approved lanes, same-authority repair | 5K | ✅ DONE |
| P24 | Package-driven L2 executor | l2_package_driven_executor.py | Generic L2 consumption | 6K | ✅ DONE |
| P25 | apps_research L2 adapter | apps_research_l2_binding.py | Thin L2 adapter refactor | 3K | ✅ DONE |
| **P26** | **Exit profile** | **exit_profile.yaml** | **X3 emission config** | **4K** | 🔄 **NOT_STARTED** |
| **P27** | **Package-driven Exit binding** | **exit_package_driven_binding.py** | **Generic Exit consumption** | **5K** | 🔄 **NOT_STARTED** |
| **P28** | **apps_research Exit adapter** | **apps_research_exit_binding.py** | **Thin Exit adapter** | **3K** | 🔄 **NOT_STARTED** |

**Phase-to-Wave Mapping:**
- P0 = W0 (Pre-flight audit)
- P1-P3 = W1 (Runtime package contract + hardening)
- P4 = W1B (Core boundary repair)
- P5-P7 = W2 (L1 planning hints + profile binding)
- P8 = W2B (L1 repair boundary audit)
- P9-P12 = W3 (L0 package-driven routing)
- P13-P16 = W4 (C0 package-driven grounding)
- P17-P21 = W5 (PA package-driven prompt assembly)
- P22-P25 = W6 (L2 package-driven execution)
- **P26-P28 = W7 (Exit binding — CURRENT EXECUTABLE WAVE)**

---

## Current apps_research Source Facts

From the current uploaded apps_research zip inspection:

- `apps_research/TECHNICAL_SPEC.md` describes canonical route as `R3_SIMPLE_GROUNDED_READ`.
- Current flow is U0 -> L1 -> L0 -> C0 -> PA -> L2 E1-E5 -> FEC Producer -> Exit v6 -> L6.
- R5 pre-route fallback exists for unroutable or ambiguous requests.
- R1A/R1B cache terminals are checked before C0.
- No L3 DAG is in normal apps_research direct scope.
- No durable side effects or CommitRequest are normal apps_research direct scope.
- `apps_research/config/domain_contract/cache_profiles.yaml` currently has semantic cache enabled.
- `apps_research/config/domain_contract/retrieval_profiles.yaml` defines `company_brief` retrieval constraints.
- `apps_research/config/domain_contract/eval_rubrics.yaml` already includes factual grounding, source quality, freshness, completeness, balance, concision, no speculation, coverage depth, citation quality, and tracked RAG metrics.
- `apps_research/config/domain_contract/grader_roster.yaml` already includes deterministic, LLM judge, and hybrid grader refs.
- `apps_research/config/domain_contract/source_mix_policy.yaml` defines source authority tier requirements by depth profile.
- `apps_research/config/domain_contract/freshness_policy.yaml` defines source-type freshness rules by depth profile.
- `apps_research/config/domain_contract/learning_profiles.yaml` exists but needs hardening for cache, retrieval, judge, and downstream-use learning.
- `apps_research/config/domain_contract/route_profiles.yaml` currently includes `managed_workflow_allowed: true`, which conflicts with the normal active route being single-step R3. Reconcile this to reserved or false.

---

## Final Runtime Shape

```text
U0
  -> L1
  -> L0
  -> R5 fallback if unroutable
  -> R1A exact cache check
  -> R1B semantic research substrate cache check
  -> R3_SIMPLE_GROUNDED_READ on cache miss
  -> C0
  -> PA
  -> L2 SINGLE_STEP
  -> Exit
  -> RuntimeExhaustBundle
  -> L6
  -> optional FutureRunPromotionRequest
  -> UWG
  -> L4
```
