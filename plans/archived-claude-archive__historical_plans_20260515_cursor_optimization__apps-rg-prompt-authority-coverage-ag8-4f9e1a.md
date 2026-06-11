---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-prompt-authority-coverage-ag8-4f9e1a.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-prompt-authority-coverage-ag8-4f9e1a.md'
source_sha256: 04adf812aba63a4ed1871340c9b3fa0251d1eeba034a7daa50c230eb0e9298da
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-prompt-authority-coverage-ag8-4f9e1a
plan_type: audit
dod_exempt: false
---

# apps_rg Prompt Authority Coverage Review and Hardening (AG-8)

Zero-loss prompt authority coverage audit and hardening: discover, classify, map, prove, and gate every apps_rg instructional prompt and prompt-related artifact across the full agentic spine.

---

## Context (SCQA)

- **Situation** — apps_rg is the golden reference implementation. AG-1 proved U0 live reflection. AG-2 proved app_payload consumption through L1/L0/C0/PA. AG-4 created evidence carrier contracts. AG-5 wired Exit X1 evaluator checks. AG-6 proved apps_rg golden path runtime. AG-7 extracted apps_rg as reusable template. The PROMPT_BOUNDARY_CONTRACT.md declares slot authority S0–R0, dual PA topology, and airlocks U0/C0/tool-model/human-reentry. The prompt_registry.yaml catalogues 8 templates. The spine owns 15+ prompt-related files across apps_rg/, agentic_core/prompt_governance/, and config/.
- **Complication** — No single inventory certifies that every prompt surface is discovered, authority-classified, mapped to a contract field, consumed only by allowed spine stages, hashed for replay, and covered by tests and CI gates. The dual PA topology (NEW PA compiler + LEGACY PA bridge + narrative-pipeline PA instrumentation) creates three separate assembly surfaces, any of which could silently accept out-of-authority prompt sources. No CI gate today fails if PA omits slot_lineage_map or component_hash_map entries.
- **Question** — How do we exhaustively inventory, authority-classify, contract-map, stage-fence, hash, and CI-gate every apps_rg prompt surface to guarantee zero prompt authority bypass in the active runtime?
- **Answer** — Execute a six-wave audit (W0 baseline → W1 discovery → W2 classification → W3 stage matrix → W4 contract mapping → W5 hardening → W6 tests → W7 CI gate → W8 artifacts) producing a complete, machine-verifiable inventory that proves the invariant: every instructional prompt is consumed only by its allowed stage, blocked from forbidden stages, hashed for replay, and UNKNOWN never treated as PASS.

---

## Hard Laws (copied verbatim — invariants, not goals)

- Do not create a parallel apps_rg runtime.
- Do not bypass U0, L1, L0, C0, PA, L2, Exit, X1, or X3.
- Do not mutate ChromaDB.
- Do not generate embeddings.
- Do not wire R1B semantic cache.
- Do not change provider behavior unless required for prompt-ref preservation.
- Do not let lower-authority app prompts override system, policy, route, registry, evidence, or schema authority.
- U0 does not reason, route, retrieve, execute, or assemble prompts.
- L1 may interpret intent and emit planning projections, but must not route with authority.
- L0 may route only from governed contract fields, not free-form prompt text.
- C0 retrieves and verifies evidence only. It does not answer or assemble prompts.
- PA composes prompts only from governed contracts and approved prompt slots.
- L2 executes bounded packets only. It must not invent new instructions.
- Exit evaluates sealed results. It must not retrieve or assemble prompts.
- Retrieved text remains data only.
- UNKNOWN is never PASS.
- NOT_APPLICABLE requires reason.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_rg/PROMPT_BOUNDARY_CONTRACT.md` | Canonical slot model, airlock invariants, receipt contract | ✅ Read |
| `apps_rg/prompt_assembly/prompt_registry.yaml` | 8 registered templates with slot/stage declarations | ✅ Read |
| `apps_rg/prompt_assembly/` (17 items) | PA compiler, slot_mapper, contracts, templates | 🔲 W1 |
| `apps_rg/config/` (18 items incl. jd_plan_rules, l0_policy, route_registry, domain_contract/) | Config prompts and policy | 🔲 W1 |
| `apps_rg/contracts/apps_rg_ingress_contract_v1.py` | App payload contract | 🔲 W1 |
| `agentic_core/prompt_governance/apps_rg_pa_binding.py` | PA binding | 🔲 W1 |
| `agentic_core/L1_cognition/apps_rg_l1_binding.py` | L1 binding | 🔲 W1 |
| `agentic_core/L0_routing/apps_rg_l0_binding.py` | L0 routing | 🔲 W1 |
| `agentic_core/runtime/c0/apps_rg_c0_binding.py` | C0 evidence | 🔲 W1 |
| `agentic_core/runtime/exit/apps_rg_exit_binding.py` | Exit binding | 🔲 W1 |
| `apps_rg/engines/` (56 items) | Generation and repair engines | 🔲 W1 |
| `apps_rg/reasoning/` (19 items) | Reasoning prompts | 🔲 W1 |
| `agentic_core/prompt_governance/templates/` (34 items) | Shared PA templates | 🔲 W1 |
| `agentic_core/prompt_governance/security/` (22 items) | Injection defense | 🔲 W1 |
| ADG snapshot `adg_indexed_05102026_1319.sqlite` | Structural dependency verification | ✅ Healthy |
| Existing CI gates: `check_apps_rg_pa_boundary.py`, `check_apps_rg_app_payload_consumption.py`, `check_evidence_contract_carriers.py`, `check_exit_x1_evaluator_wiring.py` | Baseline gate status | 🔲 W0 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W0 | W0.P1 | Baseline gate verification (5 gates + test) | ~2k | 🔲 Not Started |
| W1 | W1.P1–W1.P4 | Full prompt surface discovery → ag8_prompt_authority_inventory.json | ~20k | 🔲 Not Started |
| W2 | W2.P1–W2.P3 | Authority classification + slot mapping → ag8_prompt_authority_classification.json | ~15k | 🔲 Not Started |
| W3 | W3.P1–W3.P2 | Stage consumption matrix → ag8_prompt_stage_consumption_matrix.json | ~10k | 🔲 Not Started |
| W4 | W4.P1–W4.P3 | Contract mapping → ag8_prompt_contract_mapping.json + ag8_prompt_no_bypass_map.json | ~12k | 🔲 Not Started |
| W5 | W5.P1–W5.P3 | Minimal hardening: add missing prompt_id/hash/lineage/slot refs | ~15k | 🔲 Not Started |
| W6 | W6.P1 | Test suite: tests/_apps_contract/test_apps_rg_prompt_authority_coverage.py (24 tests) | ~10k | 🔲 Not Started |
| W7 | W7.P1 | CI gate: ops_scripts/ci/check_apps_rg_prompt_authority_coverage.py | ~8k | 🔲 Not Started |
| W8 | W8.P1 | Final artifacts: report.md + ag8_prompt_acceptance_evidence.json | ~5k | 🔲 Not Started |

**Total: ~97k tokens across 9 waves**

**Status tracking**: Notion Status flips "Not Started" → "In Progress" at **Wave 1 start**.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | Baseline gate run | 5 CI gates + test_ag6 | Gate exits may need --fail-closed flags | ~2k | 🔲 |
| W1.P1 | apps_rg/ prompt surface scan | apps_rg/prompt_assembly/, apps_rg/config/, apps_rg/engines/, apps_rg/reasoning/ | Large surface — 56 engine files | ~6k | 🔲 |
| W1.P2 | agentic_core/ prompt surface scan | prompt_governance/, L1/L0/C0/PA/Exit bindings | Complex cross-layer | ~6k | 🔲 |
| W1.P3 | Config/YAML/JSON/template scan | domain_contract/, templates/, jd_plan_rules, l0_policy, route_registry | YAML prompt fragments hard to detect | ~4k | 🔲 |
| W1.P4 | Inventory JSON emit | artifacts/apps_rg/ag8_prompt_authority_inventory.json | Schema design | ~4k | 🔲 |
| W2.P1 | Authority class assignment | All inventory rows | Authority boundaries can be ambiguous | ~5k | 🔲 |
| W2.P2 | Slot mapping (S0–R0) | All inventory rows | Dual PA topology complicates slot origin | ~5k | 🔲 |
| W2.P3 | Classification JSON emit | artifacts/apps_rg/ag8_prompt_authority_classification.json | — | ~5k | 🔲 |
| W3.P1 | Stage matrix build | U0/L1/L0/C0/PA/L2/Exit/X1/L6 × all prompt_ids | Matrix combinatorics | ~6k | 🔲 |
| W3.P2 | Matrix JSON emit | artifacts/apps_rg/ag8_prompt_stage_consumption_matrix.json | — | ~4k | 🔲 |
| W4.P1 | Contract field mapping | ValidatedRequest → ExitReviewPacket chain | 8 contracts in chain | ~5k | 🔲 |
| W4.P2 | No-bypass map + content_hash proof | PA slot_lineage_map, component_hash_map | Hash continuity requires reading compiled artifact | ~4k | 🔲 |
| W4.P3 | Contract + no-bypass JSON emit | ag8_prompt_contract_mapping.json, ag8_prompt_no_bypass_map.json | — | ~3k | 🔲 |
| W5.P1 | Hardening: prompt_id + hash stubs | Missing prompt_id refs in engines/reasoning | Must not change behavior | ~5k | 🔲 |
| W5.P2 | Hardening: slot_lineage + component_hash | PA binding files | Minimal edit only | ~6k | 🔲 |
| W5.P3 | Hardening: test-only prompt marking | Test fixtures | Flag TEST_ONLY, not delete | ~4k | 🔲 |
| W6.P1 | 24-test suite | tests/_apps_contract/test_apps_rg_prompt_authority_coverage.py | Must cover all 24 invariants | ~10k | 🔲 |
| W7.P1 | CI gate (15 fail conditions) | ops_scripts/ci/check_apps_rg_prompt_authority_coverage.py | AST scan for envelope.payload reads | ~8k | 🔲 |
| W8.P1 | Final report + acceptance evidence | artifacts/apps_rg/ (7 files) | Summary counts required | ~5k | 🔲 |

---

## W0: Baseline Verification

Run before any edits. If any step fails, stop and report.

```
1. python -m pytest tests/_apps_contract/test_ag6_apps_rg_golden_path.py -v
2. python ops_scripts/ci/check_apps_rg_golden_path_runtime.py --fail-closed
3. python ops_scripts/ci/check_apps_rg_app_payload_consumption.py
4. python ops_scripts/ci/check_evidence_contract_carriers.py
5. python ops_scripts/ci/check_exit_x1_evaluator_wiring.py --fail-closed
```

Expected: all pass. Any failure = BLOCKED; do not proceed to W1.

---

## W1: Prompt Surface Discovery

### Search Scope

```
apps_rg/prompt_assembly/          — PA compiler, slot_mapper, templates (8), contracts, rg_pa_compiler
apps_rg/config/                   — l0_policy, jd_plan_rules, route_registry, rg_agent_specs, domain_contract/*
apps_rg/contracts/                — ingress contract v1
apps_rg/engines/                  — 56 engine files (generation, repair, evaluator)
apps_rg/reasoning/                — 19 reasoning files
apps_rg/airlocks/                 — airlock implementations
apps_rg/integrations/             — 40 integration files (hops, llm_client)
apps_rg/validators/               — 7 validator files
agentic_core/L1_cognition/apps_rg_l1_binding.py
agentic_core/L0_routing/apps_rg_l0_binding.py
agentic_core/runtime/c0/apps_rg_c0_binding.py
agentic_core/prompt_governance/apps_rg_pa_binding.py
agentic_core/L2_execution/apps_rg_l2_binding.py (if present)
agentic_core/runtime/exit/apps_rg_exit_binding.py
agentic_core/prompt_governance/templates/  — 34 shared templates
agentic_core/prompt_governance/security/   — 22 injection-defense files
agentic_core/prompt_governance/meta_prompts/ — 18 meta-prompt files
tests/_apps_contract/              — test prompt fixtures
```

### Output Schema

```json
{
  "prompt_id": "string",
  "source_file": "string",
  "source_symbol_or_key": "string",
  "raw_prompt_ref": "string",
  "content_hash": "string | null",
  "prompt_kind": "template | config_rule | role_instruction | generation_directive | evaluator_rubric | repair_hint | schema_instruction | fence | system_invariant | output_schema | test_fixture | meta_prompt",
  "authority_class": "SYSTEM_AUTHORITY | POLICY_AUTHORITY | ROUTE_RULE | DOMAIN_INSTRUCTION | USER_TASK | EVIDENCE_DATA | EXAMPLE_DATA | OUTPUT_SCHEMA | HEAL_HINT | EVALUATOR_RUBRIC | PROVIDER_RENDER_CONTROL | LEARNING_PRIOR | TEST_ONLY",
  "intended_stage": "string",
  "current_consumer_stage": "string",
  "allowed_consumer_stages": ["string"],
  "forbidden_consumer_stages": ["string"],
  "contract_field_target": "string | null",
  "prompt_slot_target": "S0 | D0 | I0 | E0 | C0 | M0 | U0 | H0 | R0 | null",
  "data_boundary_label": "INSTRUCTION | DATA_ONLY | EVIDENCE_DATA | TEST_ONLY",
  "current_status": "MAPPED | PARTIAL | UNMAPPED | FORBIDDEN | DEFERRED_WITH_REASON",
  "deferred_reason": "string | null",
  "evidence_paths": ["string"]
}
```

Output: `artifacts/apps_rg/ag8_prompt_authority_inventory.json`

---

## W2: Classify Every Prompt by Authority and Slot

### Authority Classes

| Class | Definition |
|---|---|
| SYSTEM_AUTHORITY | Immutable invariants (no fabrication, ATS floor, no L4 direct write) |
| POLICY_AUTHORITY | App-level policy rules (HITL policy, route policy, capability policy) |
| ROUTE_RULE | Structured routing fields consumed by L0 (not free-form text) |
| DOMAIN_INSTRUCTION | Per-template operating instructions (I0 slot) |
| USER_TASK | CLI args / wizard input / manual brief content (U0, neutralized) |
| EVIDENCE_DATA | JD, master résumé, company brief — data only (C0) |
| EXAMPLE_DATA | Approved few-shot exemplars (E0) |
| OUTPUT_SCHEMA | Response schema binding (R0) |
| HEAL_HINT | Bounded repair hints for E4_HEAL (H0) |
| EVALUATOR_RUBRIC | Exit/X1 evaluator inputs — NOT generation authority |
| PROVIDER_RENDER_CONTROL | Provider-safe controls (M0) |
| LEARNING_PRIOR | Reasoning priors / planning priors consumed by L1 |
| TEST_ONLY | Test-fixture prompts that must never reach production |

### Slot Mapping Rules

| Slot | Maps from | Never from |
|---|---|---|
| S0 | SYSTEM_AUTHORITY | anything else |
| D0 | fences, anti-injection controls | — |
| I0 | approved DOMAIN_INSTRUCTION | USER_TASK, EVIDENCE_DATA, EVALUATOR_RUBRIC |
| E0 | EXAMPLE_DATA | system authority |
| C0 | EVIDENCE_DATA | — |
| M0 | PROVIDER_RENDER_CONTROL | — |
| U0 | USER_TASK (neutralized) | S0/D0/I0/R0 override |
| H0 | HEAL_HINT (same-authority) | widen route/tool/model/schema/policy |
| R0 | OUTPUT_SCHEMA | user/retrieved/tool/model/human text |

Output: `artifacts/apps_rg/ag8_prompt_authority_classification.json`

---

## W3: Stage Consumption Matrix

### Stages

`U0 | L1 | L0 | C0 | PA | L2 | Exit/X1 | L6`

### Stage Consumption Rules

| Stage | May consume | Must not consume |
|---|---|---|
| U0 | prompt-related fields as DATA only | instructional prompts as authority |
| L1 | planning/domain intent fields → L1PlanContract projections | raw prompt text, route authority |
| L0 | structured L1PlanContract fields only | raw prompt text, free-form instructions |
| C0 | retrieval/evidence requirements | generation instructions |
| PA | governed contracts + approved prompt slots only | raw app prompts, loose dict/string |
| L2 | CompiledPromptArtifact + sealed execution packet | raw app prompts |
| Exit | evaluator rubrics + structured evidence refs | generation instructions as authority |
| L6 | completed-run prompt metadata only | runtime prompt assembly |

Output: `artifacts/apps_rg/ag8_prompt_stage_consumption_matrix.json`

---

## W4: Contract Mapping

### Contract Chain

```
ValidatedRequest.app_payload
  → L1PlanContract fields
    → RouteContract fields
      → FinalEvidenceContract fields
        → CompiledPromptArtifact fields (slot_lineage_map, component_hash_map)
          → SealedL2Artifact refs
            → ExitReviewPacket refs
              → X1CheckoutResult refs
```

### Required Proofs

- No prompt passed as loose dict/string without a contract ref.
- Every prompt has content_hash or component_hash.
- PA component_hash_map includes all used prompt components.
- PA slot_lineage_map traces every prompt slot to source.
- prompt_hash changes when meaningful instructional prompt content changes.
- route_digest does not change from prompt text unless L1/L0 structured fields change.
- L0 does not parse raw instructional prompt text.

Outputs:
- `artifacts/apps_rg/ag8_prompt_contract_mapping.json`
- `artifacts/apps_rg/ag8_prompt_no_bypass_map.json`

---

## W5: Hardening Implementation

**Allowed changes only:**
- Add `prompt_id`/`content_hash`/`component_hash` refs to source files lacking them.
- Add missing `slot_lineage_map` entries.
- Add missing `prompt_contract` refs.
- Add tests.
- Add CI gate.
- Rename ambiguous prompt fields if needed.
- Mark test-only prompts explicitly (`authority_class: TEST_ONLY`).

**Forbidden changes:**
- No prompt rewrite for style.
- No behavior drift without test proof.
- No business logic in U0.
- No L0 free-text prompt parsing.
- No C0 prompt assembly.
- No L2 raw prompt loading.
- No Exit prompt assembly.
- No ChromaDB mutation.
- No embedding generation.

---

## W6: Tests

File: `tests/_apps_contract/test_apps_rg_prompt_authority_coverage.py`

24 required test cases:
1. Every discovered apps_rg prompt has a `prompt_id`.
2. Every prompt has `authority_class`.
3. Every prompt has `allowed_consumer_stages` and `forbidden_consumer_stages`.
4. Every prompt maps to a contract field or prompt slot.
5. U0 does not consume instructional prompts as authority.
6. L1 consumes app_payload-derived prompt requirements into L1PlanContract projections.
7. L0 consumes structured L1PlanContract fields only.
8. L0 does not parse raw prompt text.
9. C0 does not assemble prompts.
10. PA consumes governed contracts only.
11. PA `slot_lineage_map` includes all used prompt components.
12. PA `component_hash_map` includes all used prompt components.
13. Retrieved evidence remains `C0_EVIDENCE_DATA_ONLY`.
14. User task remains U0 neutralized task, not I0 instruction.
15. Output schema maps to R0.
16. Evaluator rubric maps to Exit/X1, not generation authority.
17. L2 does not load raw apps_rg prompts directly.
18. Exit does not assemble prompts.
19. `prompt_hash` changes when I0/D0/R0 meaningful content changes.
20. No legacy `envelope.payload` prompt reads downstream.
21. UNKNOWN never PASS.
22. NOT_APPLICABLE requires reason.
23. No ChromaDB mutation.
24. No embedding generation.

---

## W7: CI Gate

File: `ops_scripts/ci/check_apps_rg_prompt_authority_coverage.py`

Fail conditions (15):
1. Any apps_rg prompt source absent from the inventory.
2. Any prompt lacks `authority_class`.
3. Any prompt lacks `allowed`/`forbidden` consumer stages.
4. Any prompt consumed by a forbidden stage.
5. U0 consumes instructional prompts as authority.
6. L0 parses raw prompt text.
7. C0 assembles prompts.
8. PA omits prompt slot lineage.
9. PA omits prompt component hash.
10. L2 loads raw app prompts instead of sealed PromptEnvelope / CompiledPromptArtifact.
11. Exit assembles generation prompts.
12. Retrieved text can become instruction.
13. User text can become instruction.
14. Evaluator rubric can become generation instruction without approval.
15. No-bypass AST scan finds `envelope.payload` prompt reads downstream of U0.

Bypass: `PROMPT_AUTHORITY_COVERAGE_BYPASS=1`
Fail-closed mode: `PROMPT_AUTHORITY_COVERAGE_FAIL_CLOSED=1`
Report: `artifacts/ci/apps_rg_prompt_authority_coverage.json`

---

## W8: Output Artifacts

| Artifact | Description |
|---|---|
| `artifacts/apps_rg/ag8_prompt_authority_report.md` | Human-readable audit report with all counts |
| `artifacts/apps_rg/ag8_prompt_authority_inventory.json` | Full prompt inventory (one row per prompt surface) |
| `artifacts/apps_rg/ag8_prompt_authority_classification.json` | Authority class + slot mapping per prompt_id |
| `artifacts/apps_rg/ag8_prompt_stage_consumption_matrix.json` | Stage × prompt_id matrix (required/optional/forbidden/not_applicable) |
| `artifacts/apps_rg/ag8_prompt_contract_mapping.json` | Contract chain mapping per prompt_id |
| `artifacts/apps_rg/ag8_prompt_no_bypass_map.json` | AST-verified no-bypass proof for envelope.payload reads |
| `artifacts/apps_rg/ag8_prompt_acceptance_evidence.json` | Acceptance invariant verification record |

---

## Acceptance Invariant

> This plan is complete only when every apps_rg instructional prompt and prompt-related artifact is:
> 1. **Inventoried** — present in ag8_prompt_authority_inventory.json
> 2. **Authority-classified** — has `authority_class` from the 13-value vocabulary
> 3. **Contract-mapped** — mapped to a contract field or canonical prompt slot (S0–R0)
> 4. **Stage-fenced** — consumed only by allowed spine stages, blocked from forbidden stages
> 5. **Hashed for replay** — has `content_hash` or `component_hash`
> 6. **PA-represented** — in `slot_lineage_map`/`component_hash_map` when used
> 7. **Test-proven** — all 24 test cases pass
> 8. **CI-gated** — gate passes with zero violations
> 9. **ChromaDB-clean** — no ChromaDB mutation, no embedding generation

---

## Definition of Done

| DoD ID | Criterion | Verification |
|--------|-----------|--------------|
| DoD-1 | W0 baseline: all 5 gates + test_ag6 pass | Command outputs show exit 0 |
| DoD-2 | ag8_prompt_authority_inventory.json exists with ≥1 row per discovered surface | `python -c "import json; d=json.load(open('artifacts/apps_rg/ag8_prompt_authority_inventory.json')); assert len(d['prompts']) > 0"` |
| DoD-3 | All inventory rows have `authority_class`, `prompt_slot_target`, `allowed_consumer_stages`, `forbidden_consumer_stages` | ag8_prompt_acceptance_evidence.json field `all_fields_populated: true` |
| DoD-4 | 24-test suite passes: `python -m pytest tests/_apps_contract/test_apps_rg_prompt_authority_coverage.py -v` exits 0 | pytest stdout shows 24 PASSED |
| DoD-5 | CI gate passes: `python ops_scripts/ci/check_apps_rg_prompt_authority_coverage.py` exits 0 | Gate output shows `ERRORS: 0` |
| DoD-6 | No ChromaDB mutation, no embedding generation (AST scan + tests 23/24) | Tests 23 and 24 pass |
| DoD-7 | UNKNOWN never PASS (test 21 + CI fail condition) | Test 21 passes |

### Verification-vs-Deferral Table

| Check | Verified in plan | Deferred |
|---|---|---|
| Baseline gates (W0) | ✅ W0.P1 | — |
| Full surface discovery (W1) | ✅ W1.P1-P4 | —  |
| Authority classification (W2) | ✅ W2.P1-P3 | — |
| Stage matrix (W3) | ✅ W3.P1-P2 | — |
| Contract mapping (W4) | ✅ W4.P1-P3 | — |
| Hardening (W5) | ✅ W5.P1-P3 | Behavioral logic changes (forbidden by hard laws) |
| Tests (W6) | ✅ 24 cases | — |
| CI gate (W7) | ✅ 15 fail conditions | — |
| R1B semantic cache wiring | ❌ DEFERRED | Explicitly forbidden by hard laws |
| ChromaDB mutation | ❌ FORBIDDEN | Hard law |
| Parallel runtime | ❌ FORBIDDEN | Hard law |

---

## Non-Goals

- This plan does NOT rewrite apps_rg prompts for style.
- This plan does NOT create a parallel runtime.
- This plan does NOT wire R1B semantic cache.
- This plan does NOT implement new HITL flows.
- This plan does NOT change provider behavior.
- This plan does NOT touch other apps (apps_lic, apps_qna, etc.) — apps_rg only.
