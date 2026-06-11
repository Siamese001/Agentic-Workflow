---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-research-rich-content-runtime-customization-a1b2c3.md'
original_relative_path: 'apps-research-rich-content-runtime-customization-a1b2c3.md'
source_sha256: 0c8c9c4e57b0eef56d24af929f7b4f57bbaa000f485cc73b1809c9f8504ab9b9
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-research-rich-content-runtime-customization-v1
plan_slug: apps-research-rich-content-runtime-customization-a1b2c3
plan_type: implementation
status: ARCHIVED_REBASELINED
active_authority: false
superseded_by: apps-research-rich-content-runtime-customization-v2
archived_at: "2026-05-11"
rebase_reason: "W7 Exit binding ready to start — rebaselining for clean execution authority"
created: "2026-05-11"
created_for: apps_research
tier: T3
adg_required: true

# W0 - Pre-flight audit
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

# W7 - Exit binding (READY but not started)
w7_status: READY
w7_next: Exit binding for apps_research

# Totals
automated_tests_total: 193
audit_questions_total: 30
combined_checks_total: 223
---

# apps_research Rich Content Retrieval Runtime Customization

Fully implement `apps_research` as a governed rich-content retrieval and research-substrate app on the common `agentic_core` spine.

This plan is the active sequencing authority for apps_research customizations related to:

- rich content retrieval
- semantic research substrate cache
- direct apps_research runs
- delegated research calls from apps_rg
- delegated research calls from apps_lic
- uploaded briefings supplied inside apps_rg
- uploaded briefings supplied inside apps_lic
- prompts
- runtime gates
- judges
- evals
- L6 meta-learning
- UWG-governed cache and index promotion

Source alignment:
- Mirrors apps_rg ownership split: app owns declarative config, `agentic_core` owns runtime execution. :contentReference[oaicite:0]{index=0}
- Preserves core contract law: no loose objects, signed replayable policy-bound contracts, 00C gates decide current-run proceed or stop, Exit emits one X3, UWG admits writes, L4 stores, L6 learns only after the boundary. :contentReference[oaicite:1]{index=1}
- Preserves 00C runtime gate proof law: every applicable live gate must emit traceable GateVerdict evidence, Exit consumes GateMeshResult, UNKNOWN is never PASS, and owner layers must not bypass gates. :contentReference[oaicite:2]{index=2}

---

## Design Target

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
| W7 | P26-P28 | Exit binding for apps_research | 12K | 0 | 0 | 🔄 NOT_STARTED | X3 emission through Exit binding |

**Totals:**
- automated_tests_total: 193
- audit_questions_total: 30
- combined_checks_total: 223

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
| P26 | Exit profile | exit_profile.yaml | X3 emission config | 4K | 🔄 NOT STARTED |
| P27 | Package-driven Exit binding | exit_package_driven_binding.py | Generic Exit consumption | 5K | 🔄 NOT STARTED |
| P28 | apps_research Exit adapter | apps_research_exit_binding.py | Thin Exit adapter | 3K | 🔄 NOT STARTED |

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
- P26-P28 = W7 (Exit binding - NOT_STARTED, final runtime proof incomplete)

**Status Summary:**
- W0-W6: ✅ DONE (P0-P25 complete)
- W7: 🔄 NOT_STARTED (P26-P28 pending)
- **Note:** Final runtime proof through Exit binding is not complete. W7 Exit binding required for end-to-end verification.

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

apps_research does not normally use L3.

L3 may appear only as an upstream caller context when apps_rg or apps_lic orchestrates a larger managed workflow and delegates a research packet into apps_research. In that case, apps_research still receives its own U0 package and runs its own governed single-step R3 or R1B path.

---

## Route Model

### Final apps_research L0 route order

1. R5_PRE_ROUTE_FALLBACK

   * Use only when request cannot be safely routed.
   * Examples: missing company, ambiguous entity, unsupported task class, blocked source scope, unsafe request.
   * Emits RET fallback or clarify packet to Exit.

2. R1A_EXACT_CACHE

   * Use only for exact valid substrate match.
   * Exact cache is read-only at L0.
   * Hit emits RETTerminalPacket to Exit.
   * L0 never writes cache.

3. R1B_SEMANTIC_CACHE

   * Use for compatible reusable research substrate.
   * Enabled for research substrate, not final customized downstream outputs.
   * Hit emits RETTerminalPacket to Exit.
   * L0 never writes cache.
   * Exit still validates before ALLOW.

4. R3_SIMPLE_GROUNDED_READ

   * Default after cache miss or weak cache.
   * C0 retrieval mandatory.
   * PA mandatory when model or synthesis packet required.
   * L2 executes one bounded research packet.
   * Exit decides final X3.

5. R4_SINGLE_ACTION

   * Not default.
   * Reserved for future bounded action utilities, such as source refresh request or index rebuild proposal.
   * No direct durable write.

6. R3R4_MANAGED_WORKFLOW

   * Not active for apps_research direct path.
   * Reserved only if explicitly introduced through U0 package and core L0 selects managed workflow in future.
   * Must not be silently inferred from `managed_workflow_allowed`.

### Required route fixes

Update apps_research route profiles:

```yaml
managed_workflow_allowed: false
managed_workflow_status: not_active_for_apps_research_direct_route
active_execution_form: SINGLE_STEP
default_route_id: R3_SIMPLE_GROUNDED_READ
semantic_cache_enabled: true
semantic_cache_scope: research_substrate_only
```

Allowed route ids:

```yaml
allowed_route_ids:
  - R5_PRE_ROUTE_FALLBACK
  - R1A_EXACT_CACHE
  - R1B_SEMANTIC_CACHE
  - R3_SIMPLE_GROUNDED_READ
```

---

## Semantic Research Substrate Cache

### Unified namespace

```text
apps_research.semantic_research_substrate.v1
```

### Eligible producers

The namespace accepts normalized research substrate from:

* apps_research direct runs
* apps_research delegated calls from apps_rg
* apps_research delegated calls from apps_lic
* uploaded briefings provided inside apps_rg
* uploaded briefings provided inside apps_lic
* approved future apps that delegate research through apps_research U0

### Eligible record types

Index as reusable research substrate:

* research_chunk
* briefing_section
* final_evidence_contract
* claim_evidence_map
* source_register
* source_portfolio
* company_brief_summary
* freshness_report
* contradiction_report
* citation_anchor_registry
* entity_alias_record
* source_authority_signal
* retrieval_query_plan
* query_decomposition_record
* downstream_substrate_packet

### Prohibited terminal reuse

Do not reuse as final answer:

* final apps_rg resume bullets
* final apps_rg tailored resume sections
* final apps_lic outreach messages
* final apps_lic campaign copy
* any customized user-specific final narrative
* any ungrounded synthesis without source register
* any uploaded briefing text that failed provenance or injection checks

### Required metadata for each cached substrate record

```yaml
record_id: string
record_type: string
substrate_namespace: apps_research.semantic_research_substrate.v1
producer_origin: enum
app_id: apps_research
caller_app_id: string | null
delegation_context: object | null
producer_route_id: string
consumer_route_id: string | null
run_id: string
trace_root: string
request_id: string
company_entity_key: string
company_aliases: list[string]
entity_resolution_receipt_ref: string
topic: string
task_class: company_brief | research_substrate | uploaded_briefing_normalization
downstream_consumer: standalone | apps_rg | apps_lic | unknown
depth_profile: COMPANY_BRIEF_LIGHT | COMPANY_BRIEF_STANDARD | COMPANY_BRIEF_DEEP | COMPANY_BRIEF_DOSSIER
jd_content_hash: string | null
role_context_hash: string | null
source_url: string | null
source_ref: string | null
source_domain: string | null
source_type: string
source_tier: tier_1_authoritative | tier_2_credible | tier_3_signals | tier_4_inferred
source_version: string | null
citation_anchor: string
chunk_digest: string
content_hash: string
embedding_model: string
embedding_model_hash: string
embedding_vector_ref: string
embedding_created_at: string
freshness_timestamp: string
freshness_ttl_seconds: int
freshness_policy_ref: string
source_mix_policy_ref: string
policy_hash: string
blueprint_hash: string
schema_version: string
provenance_status: PASS | WEAK | BLOCKED | UNKNOWN
acl_scope: string
support_status: PASS | WEAK_WITH_CAVEATS | CONFLICTED | EMPTY | BLOCKED | UNKNOWN
contradiction_status: NONE | RESOLVED | UNRESOLVED_BLOCKER
injection_scan_status: PASS | WARN | BLOCK
data_boundary_label: EVIDENCE_DATA_ONLY
runtime_gate_refs: list[string]
receipt_refs: list[string]
audit_manifest_ref: string
```

### R1B semantic cache compatibility requirements

R1B may emit RET only when all required checks pass:

```yaml
entity:
  normalized_company_entity_match: required
  approved_alias_match: allowed
  entity_ambiguity: must_be_none

task:
  task_class: company_brief or research_substrate
  final_output_reuse: prohibited
  downstream_consumer_compatible: required

context:
  depth_profile_compatible: required
  downgrade_allowed: only_if_policy_allows
  jd_hash_compatible_when_present: required
  role_context_compatible_when_present: required
  topic_support_target_compatible: required

evidence:
  support_status: PASS or approved_WEAK_WITH_CAVEATS
  unresolved_contradiction_blocker: prohibited
  citation_anchors_present: required
  source_register_present: required
  provenance_known: required

freshness:
  freshness_within_ttl: required
  freshness_policy_ref_compatible: required
  stale_behavior_respected: required

governance:
  acl_permits_reuse: required
  policy_hash_compatible: required
  schema_version_compatible: required
  tenant_scope_valid: required
  data_boundary_label: EVIDENCE_DATA_ONLY

embedding:
  embedding_model_compatible: required
  similarity_above_threshold: required
  threshold_profile_ref: required
  semantic_compatibility_receipt: required

routing:
  terminal_short_circuit_flag: true
  ret_type: SEMANTIC_CACHE_HIT
  next_stage: Exit
  no_direct_user_return: true
```

---

## W0 Hardening: Carry-Forward Mapping

W0 audit receipt hardened with 16 carry-forward items. Each item maps to a blocking phase with required test and fail-closed consequence.

| CF ID | Item | Current Verdict | Blocking Phase | Required Test | Fail-Closed Consequence |
|-------|------|-----------------|----------------|---------------|----------------------|
| CF-5 | managed_workflow_allowed=true | YES - REQUIRES_FIX | W3 / Phase 3 | test_apps_research_l0_rejects_managed_workflow_direct_route | direct apps_research managed workflow route must fail |
| CF-9 | R1B RET packet implied | IMPLIED | W3 / Phase 3 | test_apps_research_r1b_emits_ret_terminal_packet | R1B cannot be selected |
| CF-10 | semantic compatibility receipt | NOT_VERIFIED | W3 / Phase 3 | test_apps_research_r1b_requires_semantic_compatibility_receipt | R1B cannot be selected |
| CF-12 | uploaded briefing normalizer | NOT_VERIFIED | W5/W13 | test_apps_research_c0_uploaded_briefing_remains_data_only | uploaded briefings cannot enter C0 evidence |
| CF-13/14 | cross-app substrate ingest | NOT_VERIFIED | W13 | test_apps_rg_delegated_research_enters_apps_research_u0, test_apps_lic_delegated_research_enters_apps_research_u0 | apps_rg/apps_lic delegated research disabled |
| CF-15 | PA slot order implied | IMPLIED | W6 | test_apps_research_pa_preserves_authority_order | compiled prompt must not dispatch |
| CF-16 | PA treats cached as C0 data | NOT_VERIFIED | W6 | test_apps_research_cached_chunks_remain_c0_data | cached content may bypass C0 evidence slot |
| CF-19 | GateMeshResult | NOT_VERIFIED | W8/W10 | test_apps_research_exit_requires_gate_mesh_result | Exit cannot emit X3D_ALLOW_FINISH |
| CF-22 | L6 writeback proposer | NOT_VERIFIED | W11 | test_apps_research_l6_writeback_proposer_creates_inert_future_run_promotion | no cache/index promotion may be proposed |
| CF-23 | UWG promotion path | PARTIAL | W12 | test_apps_research_uwg_admits_valid_substrate_promotion | L4 substrate writes blocked |
| CF-24 | L4 accepts UWG-only writes | NOT_VERIFIED | W12 | test_apps_research_l4_accepts_cache_write_only_from_uwg | non-UWG writes may pollute cache |
| CF-25 | judge executability | DECLARATIVE_ONLY | W9 | test_apps_research_claim_support_judge_maps_to_g22 | G22 cannot pass on judge-required dimensions |
| CF-26 | deterministic graders | NOT_VERIFIED | W9 | test_apps_research_required_deterministic_graders_fail_closed_when_missing | required grader dimensions cannot be scored |
| CF-28 | semantic cache false-positive controls | NOT_VERIFIED | W14 | test_apps_research_semantic_cache_false_positive_blocked | false positive cache hits may degrade quality |
| CF-29 | uploaded briefing injection controls | NOT_VERIFIED | W14 | test_apps_research_uploaded_briefing_injection_blocked | malicious briefings may enter evidence stream |
| CF-30 | apps_rg/apps_lic final output cache reuse prevention | NOT_VERIFIED | W14 | test_apps_research_uwg_blocks_final_apps_rg_output_terminal_cache | final apps_rg outputs may be incorrectly reused |

**W0 Status:** DONE with 16 carry-forward items mapped. No NOT_VERIFIED item marked as implemented. No IMPLIED/DECLARATIVE converted to PASS without runtime proof.

---

## Wave Structure

| Wave | Phase IDs | Focus                                      | Est. Tokens | Status      |
| ---- | --------- | ------------------------------------------ | ----------- | ----------- |
| W0   | Phase 0   | Source reconciliation audit (HARDENED)     | ~5K         | DONE |
| W1   | Phase 1   | U0 runtime customization package           | ~8K         | DONE |
| W2   | Phase 2   | L1 apps_research planning hints            | ~6K         | Not Started |
| W3   | Phase 3   | L0 routing and semantic cache route        | ~10K        | Not Started |
| W4   | Phase 4   | Domain config profiles                     | ~8K         | Not Started |
| W5   | Phase 5   | C0 retrieval and substrate normalization   | ~12K        | Not Started |
| W6   | Phase 6   | Prompt Assembly profile consumption        | ~8K         | Not Started |
| W7   | Phase 7   | L2 single-step research execution          | ~10K        | Not Started |
| W8   | Phase 8   | Runtime gates customization                | ~10K        | Not Started |
| W9   | Phase 9   | Judges and evals                           | ~12K        | Not Started |
| W10  | Phase 10  | Exit X1-X3                                 | ~8K         | Not Started |
| W11  | Phase 11  | L6 meta-learning                           | ~10K        | Not Started |
| W12  | Phase 12  | UWG and L4 cache/index writeback           | ~8K         | Not Started |
| W13  | Phase 13  | Cross-app delegation from apps_rg/apps_lic | ~10K        | Not Started |
| W14  | Phase 14  | E2E proof and receipts                     | ~15K        | Not Started |

---

## Phase-Level Summary

| Phase    | Title                       | Scope (files)                                                  | Pain Points                                    | Est. Tokens | Status      |
| -------- | --------------------------- | -------------------------------------------------------------- | ---------------------------------------------- | ----------- | ----------- |
| Phase 0  | Source Reconciliation Audit | zip vs live repo vs agentic_core                       | Route drift, cache semantics, L3 ambiguity     | ~5K         | DONE |
| Phase 1  | U0 Package                  | ingress schema, package refs, U0 adapter               | All customizations must enter through U0       | ~8K         | DONE |
| Phase 2  | L1 Planning                 | intent, entity, depth, consumer hints                  | No route authority leakage                     | ~6K         | Not Started |
| Phase 3  | L0 Routing                  | R5/R1A/R1B/R3 route model                              | R1B must not bypass Exit                       | ~10K        | Not Started |
| Phase 4  | Domain Config               | cache/retrieval/source/freshness/eval profiles         | Declarative only                               | ~8K         | Not Started |
| Phase 5  | C0 Retrieval                | C0 substrate normalization                             | Uploaded briefings as data only                | ~12K        | Not Started |
| Phase 6  | Prompt Assembly             | prompt BOM/profile consumption                         | Evidence cannot become instructions            | ~8K         | Not Started |
| Phase 7  | L2 Execution                | single-step research packet                            | No direct retrieval/write/provider bypass      | ~10K        | Not Started |
| Phase 8  | Runtime Gates               | G01-G29 policy profile                                 | UNKNOWN never PASS                             | ~10K        | Not Started |
| Phase 9  | Judges/Evals                | claim support, citation, coverage, cache compatibility | Judges feed gates/evals, no direct authority   | ~12K        | Not Started |
| Phase 10 | Exit X1-X3                  | RET/SealedL2Artifact handling                          | Exactly one X3                                 | ~8K         | Not Started |
| Phase 11 | L6 Learning                 | cache, source, alias, judge, retrieval learning        | Future-run only                                | ~10K        | Not Started |
| Phase 12 | UWG/L4                      | substrate cache/index promotion                        | UWG-only durable writes                        | ~8K         | Not Started |
| Phase 13 | Cross-App Delegation        | apps_rg/apps_lic delegation and uploads                | Caller context, JD hash, no final-output reuse | ~10K        | Not Started |
| Phase 14 | E2E Proof                   | tests, receipts, negative controls                     | No fake evidence                               | ~15K        | Not Started |

---

## Gap Register

| Gap ID | Description | Phase | P-Band | Owner |
|--------|-------------|-------|--------|-------|
| GAP-01 | Source reconciliation audit complete - receipt written | Phase 0 | P3 | apps_research |
| GAP-02 | U0 runtime package implementation - DONE | Phase 1 | P2 | DONE |
| GAP-03 | L0 semantic cache route integration | Phase 3 | P2 | agentic_core |
| GAP-04 | Cross-app delegation stubs | Phase 13 | P3 | agentic_core |

---

## Definition of Done

| #      | Criterion                                                    | Verification                                             |
| ------ | ------------------------------------------------------------ | -------------------------------------------------------- |
| DoD-1  | Source reconciliation audit written                          | DONE - Audit receipt at artifacts/apps_research/apps_research_rich_content_runtime_customization_audit_receipt.json |
| DoD-2  | U0 runtime customization package complete                    | DONE - 17 tests pass, package digest verified, unknown fields rejected |
| DoD-3  | L1 emits apps_research planning hints only                   | L1 tests prove no route authority                        |
| DoD-4  | L0 emits exactly one deterministic route or RET              | L0 route tests pass                                      |
| DoD-5  | R1B semantic cache is research-substrate-only                | Cache compatibility tests pass                           |
| DoD-6  | R1B never bypasses Exit                                      | RET-to-Exit tests pass                                   |
| DoD-7  | C0 emits source register and claim-evidence map              | C0 evidence contract tests pass                          |
| DoD-8  | Uploaded briefings remain data only                          | Injection and data-boundary tests pass                   |
| DoD-9  | PA preserves canonical authority order                       | PA tests pass                                            |
| DoD-10 | L2 executes one bounded research packet                      | L2 tests pass                                            |
| DoD-11 | Runtime gates customized through profile only                | Gate profile tests pass                                  |
| DoD-12 | Judges feed gates/evals through core                         | Judge integration tests pass                             |
| DoD-13 | Exit emits exactly one X3                                    | Exit tests pass                                          |
| DoD-14 | L6 learning is future-run only                               | L6 tests pass                                            |
| DoD-15 | Durable cache/index writes go only through UWG               | UWG/L4 tests pass                                        |
| DoD-16 | apps_rg/apps_lic delegated calls work                        | Cross-app tests pass                                     |
| DoD-17 | Final apps_rg/apps_lic outputs are not terminal-cache reused | Negative controls pass                                   |
| DoD-18 | Runtime proof bundle complete                                | 99 proof bundle exists and passes no-bypass assertions   |

---

## Verification vs Deferral

| Item                                         | Verify in this plan                 | Defer                       |
| -------------------------------------------- | ----------------------------------- | --------------------------- |
| Real live web retrieval quality              | Stub and fixture-based proof        | Live retrieval benchmark    |
| Real provider LLM inference                  | Stubbed or controlled provider test | Live model eval run         |
| Full source authority calibration corpus     | Partial fixtures                    | Larger benchmark            |
| Longitudinal semantic cache threshold tuning | Contract and L6 proposal path       | Production learning loop    |
| Human calibration of judges                  | Schema and fixture path             | Human review program        |
| Real apps_rg/apps_lic production integration | Delegation stubs and contract proof | End-to-end live product run |

---

## Acceptance Criteria

* apps_research enters U0 with complete `runtime_customization_package`.
* All apps_research customizations are declarative input to U0.
* agentic_core remains sole runtime owner.
* L1 emits apps_research hints without route authority.
* L0 checks R5, R1A, R1B, then R3.
* L0 emits exactly one route or RET packet.
* R1B semantic cache is enabled only for research substrate reuse.
* R1B cache hit emits RETTerminalPacket and goes to Exit.
* C0 emits FinalEvidenceContract, source register, claim-evidence map, freshness report, and contradiction report.
* Uploaded briefings from apps_rg/apps_lic are normalized as evidence data only.
* Prompt Assembly treats cached chunks and briefings as C0 data only.
* L2 executes one bounded research packet.
* Runtime Gates emit apps_research-customized GateVerdicts through shared G01-G29.
* Judges and evals feed G09, G10, G22, G25, and L6 through core judge/eval infrastructure.
* Exit requires GateMeshResult and emits exactly one X3.
* L6 meta-learning is future-run only.
* UWG controls all durable cache/index writes.
* L4 accepts apps_research substrate writes only from UWG.
* apps_rg/apps_lic delegated research calls are supported.
* apps_rg/apps_lic uploaded briefings are supported.
* final apps_rg/apps_lic customized outputs are not terminal-cache reused.
* All targeted tests pass.
* Remaining gaps are explicit, non-blocking, and listed in final receipt.

---

## Scope Boundaries

* Do not broaden beyond apps_research except explicit apps_rg/apps_lic delegation boundaries.
* Do not change agentic_core governance law.
* Do not build a second apps_research runtime.
* Do not add apps_research-owned provider calls.
* Do not add apps_research-owned retrieval execution.
* Do not add apps_research-owned Exit.
* Do not add apps_research-owned durable writes.
* Do not fake gate receipts.
* Do not mark docs-only compliance as implemented.
* Do not treat uploaded briefings as instructions.
* Do not cache customized apps_rg/apps_lic final outputs as reusable terminal answers.
* Do not silently activate L3 managed workflow for apps_research direct route.
* Do not bypass core C0, PA, L2, Exit, L6, UWG, or L4.
