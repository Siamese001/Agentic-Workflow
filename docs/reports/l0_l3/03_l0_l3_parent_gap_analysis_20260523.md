# L0 / L3 Parent Contract — Repo Gap Analysis

**Generated:** 2026-05-23  
**SSOT:** [03_L0_Route_Decision_Switching_L3.md](../../reference/03_L0_Route_Decision/03_L0_Route_Decision_Switching_L3.md) (parent invariants §4–§11)  
**Child specs:** `docs/reference/03_L0_Route_Decision/03.1` … `03.9` (per-stage REQ; conversion deferred per parent §12)  
**Remediation plan:** [l0-l3-parent-gap-remediation-a7f3e2](../../.cursor/plans/l0-l3-parent-gap-remediation-a7f3e2.md)  
**Notion (plan):** https://www.notion.so/36927693f55c812e9828ccb5031897fd  
**Related plans:** [l0-routing-v15-only-cutover-c9e2f1](../../.cursor/plans/l0-routing-v15-only-cutover-c9e2f1.md) (v15 vocabulary cutover)

---

## Executive summary

The parent doc defines **12 parent-level invariants** (`REQ-L0-*`, `REQ-L3-*`), a **runtime evidence field set** for `RouteContract` / `L3WorkflowContract` / `L3StepContract`, **nine named release-gate validators**, **OTEL span names**, and **negative controls**. The repo has **substantial L0/L3 machinery** (W6 `RouteContract`, v15 `RouteContractV15`, `ManagedWorkflowRunner`, `contracts_l3_7`, apps_lic `l3_binding`, e2e proof harness) but **no row in §4 is fully PASS at release-gate level**: every parent row is marked `DOC_ONLY`, and the named validators **do not exist** under `ops_scripts/ci/`.

**Headline gaps:**

| Theme | Verdict | Impact |
|-------|---------|--------|
| Contract vocabulary (execution_form, field names) | **DIVERGENT** | Parent §4 vs v15 vs W6 use incompatible `execution_form` enums and digest/HMAC field names |
| W6 spine `RouteContract` evidence fields | **PARTIAL** | Missing `route_digest`, `policy_hash`, `blueprint_hash`, `content_hash`, `lineage`, `terminal`; `signature` not populated on apps_rg path |
| Release-gate validators (§7) | **MISSING** | Zero implementations of `l0_*_validator` / `l3_*_validator` |
| OTEL span contract (§6) | **MISSING** (prod) | Spans exist in e2e proof / unit tests; apps_rg integrated path does not emit `l0.route_decision`, `l3.eligibility_check`, etc. |
| apps_rg L3 binding | **MISSING** | No `apps_rg/runtime/bindings/l3_binding.py`; managed workflow gated by test env flag only |
| L3WorkflowContract (runtime) | **PARTIAL** | Proof harness + doctrine types; not wired on apps_rg product spine |
| Child files 03.1–03.9 | **DOC_ONLY** | Present as reference; per-stage REQ conversion deferred |

Gap IDs: **`GAP-L03-*`** (parent / cross-cutting), **`GAP-AC-L03-*`** (agentic_core), **`GAP-AR-L03-*`** (apps_rg).

**Non-claims:** This analysis is static (code + reference + test inventory). No live integrated-spine run was executed for OTEL span proof on apps_rg.

---

## Methodology

1. Map each §4 parent invariant to implementation surfaces (bindings, contracts, runners, CI).
2. Compare §5 runtime evidence fields to `RouteContract` / `L3StepContract` dataclasses.
3. Search repo for §7 validator names and §6 OTEL span names.
4. Classify: **ALIGNED** | **PARTIAL** | **MISSING** | **DIVERGENT** (intentional doc drift).
5. Assign remediation wave in linked plan.

---

## §4 Parent invariant matrix

| REQ_ID | Fit | Primary implementation | Gaps |
|--------|-----|------------------------|------|
| `REQ-L0-ROUTE-EXACTLY-ONE-001` | **PARTIAL** | [`l0_route_apps_rg`](../../apps_rg/runtime/bindings/l0_binding.py), [`L0Router`](../../agentic_core/L0_routing/route_contract.py), apps_lic L0 tests | One contract per binding call; **no** `l0_one_route_validator`; mid-pipeline double-route not traced in prod OTEL |
| `REQ-L0-DETERMINISTIC-DIGEST-001` | **PARTIAL** | v15 [`deterministic_route_digest`](../../agentic_core/L0_routing/types/route_contract_v15.py); apps_lic [`_route_digest`](../../tests/apps_lic/test_w4_apps_lic_l1_l0.py) helper | W6 [`RouteContract`](../../agentic_core/runtime/contracts/route_contract.py) has **no** `route_digest`; apps_rg L0 does not compute digest |
| `REQ-L0-EXECUTION-FORM-001` | **DIVERGENT** | Parent: `exact_cache`…`hitl`; v15: `TERMINAL_SHORTCIRCUIT`/`SINGLE_STEP`/`MANAGED_WORKFLOW`; W6/apps_rg: `managed_workflow`, `single_step`, profile strings | **GAP-L03-VOCAB-1:** reconcile parent §4 with v15 cutover plan before validators |
| `REQ-L0-NO-RETRIEVE-EXECUTE-001` | **PARTIAL** | apps_rg L0 binding is side-effect-free; [`mutation_prohibition`](../../agentic_core/L0_routing/enforcement/mutation_prohibition.py) | `agentic_core/L0_routing/c0_retrieval/**` couples retrieval under L0 tree; **no** `l0_no_side_effect_validator` / `compiler_anti_cheat_findings.json` gate |
| `REQ-L0-HMAC-SIGNED-001` | **PARTIAL** | v15 HMAC in `route_contract_v15.py`; W6 `signature` field (optional) | apps_rg L0 leaves `signature` empty; parent expects `hmac_sig` — **GAP-L03-FIELD-1** |
| `REQ-L0-CACHE-FALLBACK-001` | **PARTIAL** | Profile `cache_eligibility` in [`l0_binding`](../../apps_rg/runtime/bindings/l0_binding.py); cache receipt fields on W6 contract | Terminal cache path not proven without C0/PA/L2 spans; **no** `l0_cache_terminal_validator` |
| `REQ-L0-GROUNDED-HANDOFF-001` | **PARTIAL** | `allowed_next_stage`, `graph_traverse_policy`, integrated spine | **no** `l0.handoff` span in product path; handoff proof = e2e harness only |
| `REQ-L3-MANAGED-WORKFLOW-ELIGIBLE-001` | **PARTIAL** | [`ManagedWorkflowRunner`](../../agentic_core/L3_orchestration/managed_workflow_runner.py); apps_lic [`l3_binding`](../../apps_lic/runtime/bindings/l3_binding.py) | apps_rg: env `APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED` only; **no** `l3_eligibility_validator` |
| `REQ-L3-DAG-BOUNDED-001` | **PARTIAL** | Runner topo sort + [`static_dag_registry`](../../agentic_core/L3_orchestration/registry/static_dag_registry.py) | `dag_metrics` / `cycle_count` not on runtime W6 emit path; **no** `l3_dag_validator` |
| `REQ-L3-STEP-LEDGER-001` | **PARTIAL** | [`contracts_l3_7`](../../agentic_core/L3_orchestration/doctrine/contracts_l3_7.py) (`L3StateLedger`, `NodeState`) | apps_rg does not emit `l3_step_ledger_<workflow_id>.json`; state enum differs from parent §4 (`pending`…`skipped` vs `NOT_READY`…`SEALED`) |
| `REQ-L3-CONCURRENCY-COMPLETION-001` | **PARTIAL** | `ManagedWorkflowRunner` + [`SectionMergeEngine`](../../agentic_core/L3_orchestration/section_merge_engine.py) | ExitPkg / `l3.completion` span not proven on apps_rg; **no** `l3_completion_validator` |
| `REQ-L3-L2-HANDOFF-001` | **PARTIAL** | apps_lic `L3StepContract` with checkpoint/idempotency fields; [`L3ToL2StepContract`](../../agentic_core/runtime/contracts/l3_to_l2_step_contract.py) | apps_rg **no** L3→L2 binding; resume idempotency NC not gated |
| `REQ-L0-NO-REROUTE-MID-RUN-001` | **PARTIAL** | Policy in apps_lic L3 docstring; L1 forbids route authority keys | **no** `l0_no_reroute_mid_run_validator`; no span-uniqueness enforcement in prod |

**Release gate column:** All parent rows = `DOC_ONLY` → **no production PASS** per parent §10.

---

## §5 Runtime evidence contract vs code

### RouteContract (parent §5)

| Parent field | W6 `RouteContract` | v15 `RouteContractV15` | apps_rg `l0_route_apps_rg` |
|--------------|---------------------|------------------------|------------------------------|
| `route_id` | via `route_id` | yes | yes |
| `request_id` | yes | yes | yes |
| `plan_id` | — | — | — (use `run_id` only) |
| `trace_root` / `trace_id` | `trace_id` | partial | yes |
| `span_id` | `otel_span_refs` tuple only | telemetry struct | not populated |
| `route_digest` | **missing** | `deterministic_route_digest` | **missing** |
| `hmac_sig` | `signature` (optional, often empty) | `signatures` block | **empty** |
| `execution_form` | string (non-enforced enum) | `ExecutionFormV15` enum | profile-driven |
| `policy_hash` / `blueprint_hash` | **missing** | yes | **missing** |
| `registry_digest_set` | **missing** | partial | **missing** |
| `replay_key` | yes | yes | via L1 only |
| `content_hash` / `lineage` | **missing** | partial | **missing** |
| `terminal` | **missing** | via execution form | **missing** |

**GAP-L03-EVID-1:** Unify W6 emit shape with parent §5 or explicitly document W6 as subset pending v15 cutover.

### L3WorkflowContract / L3StepContract

| Surface | Location | Product spine |
|---------|----------|---------------|
| Proof harness | [`tests/e2e/proof/contracts.py`](../../tests/e2e/proof/contracts.py) | F5 fixture only |
| Doctrine | [`contracts_l3_6`](../../agentic_core/L3_orchestration/doctrine/contracts_l3_6.py), [`contracts_l3_7`](../../agentic_core/L3_orchestration/doctrine/contracts_l3_7.py) | apps_lic partial |
| Runtime receipt | [`l3_runtime_orchestration_receipt`](../../agentic_core/runtime/contracts/l3_runtime_orchestration_receipt.py) | apps_lic |
| apps_rg | — | **MISSING** |

---

## §6 OTEL span contract

Required spans (parent): `l0.route_input_preflight`, `l0.route_decision`, `l0.execution_form`, `l0.route_sign`, `l0.cache_terminal` | `l0.handoff`, `l3.eligibility_check`, `l3.dag_validate`, `l3.step_ledger`, `l3.completion`, `l3.l2_handoff`.

| Evidence | Finding |
|----------|---------|
| 10C pilot tests | `NO_SPANS_EMITTED` on REQ-075–080 rows in reconciliation CSV |
| e2e proof | Contract emission without full span tree on apps_rg prod |
| apps_rg L0 binding | No OTEL instrumentation |

**GAP-L03-OTEL-1:** Span contract satisfied only in proof harness / future work — not release-gate proven.

---

## §7 Validator contract

Grep across repo: **validator names appear only in the parent markdown file**, not in `ops_scripts/ci/` or `agentic_core` validators package.

| Validator | Status |
|-----------|--------|
| `l0_one_route_validator` | **MISSING** |
| `l0_route_digest_validator` | **MISSING** |
| `l0_execution_form_validator` | **MISSING** |
| `l0_no_side_effect_validator` | **MISSING** |
| `l0_hmac_validator` | **MISSING** |
| `l0_cache_terminal_validator` | **MISSING** |
| `l0_handoff_validator` | **MISSING** |
| `l0_no_reroute_mid_run_validator` | **MISSING** |
| `l3_eligibility_validator` | **MISSING** |
| `l3_dag_validator` | **MISSING** |
| `l3_step_ledger_validator` | **MISSING** |
| `l3_completion_validator` | **MISSING** |
| `l3_l2_handoff_validator` | **MISSING** |

**Partial coverage:** 10C unit tests (`test_10c_req_075`–`080`, `170`) exercise L0 routing behaviors but do not map 1:1 to parent REQ-IDs or negative controls (`NC-L0-*`, `NC-L3-*`).

---

## §8–§9 Negative controls and replay

| NC_ID | Severity (parent) | Repo coverage |
|-------|-------------------|---------------|
| `NC-L0-DUAL-ROUTE-001` | — | No dedicated NC test named in CI |
| `NC-L0-RETRIEVE-LEAK-001` | critical | Boundary tests partial; no compiler anti-cheat artifact |
| `NC-L3-HIDDEN-EXPANSION-001` | critical | apps_lic tests gate L3 on `execution_form`; apps_rg unguarded without binding |
| `NC-L0-REROUTE-MID-001` | critical | **MISSING** automated NC |
| Replay `byte_identical` | — | e2e fixtures F1–F10; apps_rg prod path **not** replay-certified |

---

## App overlay snapshot

### apps_rg

| Area | Fit | Notes |
|------|-----|-------|
| L0 | **PARTIAL** | [`l0_binding.py`](../../apps_rg/runtime/bindings/l0_binding.py) — profile-driven, gate receipts, no digest/HMAC |
| L3 | **MISSING** | No `l3_binding`; `ManagedWorkflowRunner` test-only; env flag `APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED` |
| Dual path | **DIVERGENT** | Section CLI vs integrated spine (see [apps_rg_v40_spine_gap_analysis_20260523.md](../apps_rg/apps_rg_v40_spine_gap_analysis_20260523.md)) |

### apps_lic (reference implementation)

| Area | Fit | Notes |
|------|-----|-------|
| L0 | **PARTIAL** | Digest tests in `test_w4_apps_lic_l1_l0.py` |
| L3 | **ALIGNED** (binding) | [`l3_orchestrate_apps_lic`](../../apps_lic/runtime/bindings/l3_binding.py) — eligibility, receipt, `L3StepContract` |
| Golden path | **PARTIAL** | AG-8 tests; still missing parent validators |

### agentic_core

| Area | Fit | Notes |
|------|-----|-------|
| v15 types | **ALIGNED** (types only) | Cutover plan not complete |
| W6 contracts | **PARTIAL** | Spine default for apps_* bindings |
| L0/C0 coupling | **DIVERGENT** | Retrieval under `L0_routing/c0_retrieval/` vs parent no-retrieve law |
| Managed workflow | **PARTIAL** | Runner exists; `registered_not_active` in test mode |

---

## Child file map (03.1–03.9)

All nine child reference files exist under `docs/reference/03_L0_Route_Decision/`. Parent §12 states per-stage REQ conversion is **deferred**. Repo implementation depth is **uneven**: 03.7 doctrine code is richest; 03.1–03.5 spread across L0 bindings and v15; 03.8–03.9 partially reflected in `ManagedWorkflowRunner` only.

---

## Recommended remediation order

1. **Vocabulary SSOT** — Resolve parent §4 `execution_form` vs v15 (`l0-routing-v15-only-cutover-c9e2f1`) before writing validators.
2. **W6 evidence uplift** — Add `route_digest`, policy/blueprint hashes, HMAC on apps_rg L0 emit (or bridge from v15).
3. **Validator pack** — Implement §7 validators + wire to `run_contract_gates.py`.
4. **apps_rg L3 binding** — Mirror apps_lic pattern; gate on `execution_form=managed_workflow`.
5. **OTEL + replay proof** — One integrated apps_rg run with span assertions + fixture byte-identical check.

Detail: [l0-l3-parent-gap-remediation-a7f3e2](../../.cursor/plans/l0-l3-parent-gap-remediation-a7f3e2.md).

---

## Acceptance criteria (this document)

- [x] All 12 §4 parent rows assessed with gap IDs
- [x] §5 field-level diff for W6 vs parent
- [x] §7 validators confirmed absent in CI
- [x] apps_rg vs apps_lic vs core called out
- [ ] Live runtime proof (deferred to plan W4)
