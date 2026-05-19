---
status: completed
type: live-runtime-wiring
created: 2026-05-10
completed: 2026-05-10
slug: apps-rg-app-payload-consumption-wiring-b3a449
exists_on_disk: true
related:
  - .cursor/plans/apps-rg-u0-reflection-live-wiring-105147.md  # AG-1.d (predecessor)
  - .cursor/plans/apps-rg-u0-reflection-harness-79d032.md      # harness
---

# AG-2 — apps_rg `app_payload` Consumption Wiring

PLAN_CREATED: plan=apps-rg-app-payload-consumption-wiring-b3a449 path=.cursor/plans/apps-rg-app-payload-consumption-wiring-b3a449.md status=in-progress

PLAN_COMPLETE: plan=apps-rg-app-payload-consumption-wiring-b3a449 note="14 files; 33/33 AG-2 tests pass; 42/42 CI checks pass; 52/52 AG-1.d predecessor tests still green; 26 app_payload fields inspected (16 L1, 7 L0, 4 C0, 9 PA consumed); 5 bypasses closed; 4 artifacts emitted; AG-2 invariant met"

## Goal

AG-1.d proved REACHABILITY — a real apps_rg run carries `app_payload` into `ValidatedRequest`. AG-2 proves CONSUMPTION — L1, L0, and PA actually consume the `app_payload` fields required for route selection, grounding, prompt assembly, and downstream execution. C0 and PA must STOP reading the legacy `AppsRgIngressPayload` directly.

## Hard Invariant

> A real apps_rg run cannot enter PA unless:
> - L1 has consumed `app_payload`-derived fields into `L1PlanContract.{task_spec, query_spec, support_expectation, output_expectation, policy_refs}`
> - L0 has consumed those fields into `RouteContract.{cache_eligibility, route_family, execution_form, action_required}`
> - PA has consumed governed contract fields into `CompiledPromptArtifact.{slot_lineage_map, component_hash_map, replay_manifest_ref}` (existing `compilation_hash` is the prompt_hash)
> - No L1/L0/C0/PA code reads `envelope.payload` or accesses `AppsRgIngressPayload` attributes
> - All claims are backed by tests + an evidence path

## W0 — Live Call Chain Bypass Map (Discovery)

```
apps_rg_dispatch(envelope)
  ├── U0  validated_request = u0_validate_apps_rg(envelope)         ◀ AG-1.d wired ✅
  ├── L1  l1_plan = l1_plan_apps_rg(validated_request)               ◀ READS validated_request top-level only — IGNORES app_payload  ❌
  ├── L0  route   = l0_route_apps_rg(l1_plan)                        ◀ READS l1_plan only — depends on L1's app_payload work   ⏸
  ├── C0  fec     = c0_retrieve_apps_rg(route, envelope.payload)     ◀ READS envelope.payload directly  ❌
  ├── PA  pa      = pa_compose_apps_rg(route, l1_plan, fec, envelope.payload)  ◀ READS envelope.payload directly  ❌
  ├── L2  ...
  └── Exit ...
```

### Bypass map

| # | Bypass | File | Symptom | Action (W2/W3/W4) |
|---|---|---|---|---|
| **B1** | L1 ignores `app_payload` entirely | `agentic_core/L1_cognition/apps_rg_l1_binding.py` | hard-coded `task_plan` + `grounding_required=True` regardless of `generation_mode`/`output_requirements`/`quality_thresholds` | W2 — read `app_payload`, populate L1PlanContract projections |
| **B2** | L0 has nothing to consume from L1 | `agentic_core/L0_routing/apps_rg_l0_binding.py` | route variant only on `target_level`; `cache_eligibility` always default | W3 — derive route_family / cache_eligibility / action_required from L1 projections |
| **B3** | C0 reads `envelope.payload` (legacy) | `agentic_core/runtime/c0/apps_rg_c0_binding.py:171` (`payload: AppsRgIngressPayload`) | direct attribute reads of `payload.job_description_text` etc. | W4 — change signature: accept `validated_request`, read `app_payload["jd_payload"]["jd_text"]` etc. |
| **B4** | PA reads `envelope.payload` (legacy) | `agentic_core/prompt_governance/apps_rg_pa_binding.py:172` (`payload: AppsRgIngressPayload`) | direct attribute reads of `payload.target_company` etc. | W4 — change signature: accept `validated_request`, read `app_payload["target"]["company"]` etc. |
| **B5** | dispatch passes `envelope.payload` to C0 + PA | `agentic_core/runtime/entry/apps_rg_dispatch.py:263, 301` | ditto | W4 — pass `validated_request` instead |

## Wave Structure

| Wave | Phases | Focus | Status |
|---|---|---|---|
| **W0** | (this section) | Discovery + bypass map | done |
| **W1** | P1.1–P1.2 | Consumption matrix + projection contract | pending |
| **W2** | P2.1–P2.2 | L1 wiring: read `app_payload`, populate L1PlanContract projections | pending |
| **W3** | P3.1–P3.2 | L0 wiring: read L1 projections, populate RouteContract route_family + cache_eligibility | pending |
| **W4** | P4.1–P4.3 | C0 + PA + dispatch wiring: change signatures to take ValidatedRequest, drop legacy payload reads | pending |
| **W5** | P5.1–P5.3 | Integration tests (10 tests minimum per user spec) | pending |
| **W6** | P6.1 | CI gate — `ops_scripts/ci/check_apps_rg_app_payload_consumption.py` | pending |
| **W7** | P7.1 | Artifacts — matrix.json + bypass-map.json + gap-report.md + acceptance.json | pending |

## Phase Summary

| Phase ID | Title | Files | Status |
|---|---|---|---|
| P1.1 | Authoring consumption matrix | `artifacts/apps_rg/ag2_app_payload_consumption_matrix.json` | pending |
| P1.2 | Add 5 projection fields to L1PlanContract | `agentic_core/runtime/contracts/l1_plan_contract.py` | pending |
| P2.1 | L1 binding reads `app_payload` | `agentic_core/L1_cognition/apps_rg_l1_binding.py` | pending |
| P2.2 | L1 fail-closed on missing `app_payload` keys | same | pending |
| P3.1 | RouteContract: add `route_family` + `execution_form` + `cache_eligibility` + `action_required` | `agentic_core/runtime/contracts/route_contract.py` | pending |
| P3.2 | L0 binding consumes L1 projections, sets route fields | `agentic_core/L0_routing/apps_rg_l0_binding.py` | pending |
| P4.1 | CompiledPromptArtifact: add `slot_lineage_map` + `component_hash_map` + `replay_manifest_ref` | `agentic_core/runtime/contracts/compiled_prompt_artifact.py` | pending |
| P4.2 | C0 + PA signature change: accept ValidatedRequest | `agentic_core/runtime/c0/apps_rg_c0_binding.py`, `agentic_core/prompt_governance/apps_rg_pa_binding.py` | pending |
| P4.3 | Dispatch passes validated_request to C0 + PA | `agentic_core/runtime/entry/apps_rg_dispatch.py` | pending |
| P5.1 | Per-stage consumption tests (L1, L0, PA) | `tests/_apps_contract/test_apps_rg_app_payload_consumption.py` | pending |
| P5.2 | Determinism + failure-mode tests | same | pending |
| P5.3 | Forbidden-pattern AST check | same | pending |
| P6.1 | CI gate script | `ops_scripts/ci/check_apps_rg_app_payload_consumption.py` | pending |
| P7.1 | Emit acceptance artifacts | `artifacts/apps_rg/ag2_*.{json,md}` | pending |

## Definition of Done

| ID | Criterion | Verification |
|---|---|---|
| **DoD-1** | L1PlanContract carries 5 projection fields, populated by L1 binding from `app_payload` | grep + test |
| **DoD-2** | L1 binding does not import or reference `AppsRgIngressPayload`; reads only `validated_request.app_payload` | AST scan + test |
| **DoD-3** | RouteContract carries `route_family` + `cache_eligibility`, populated by L0 from L1 projections | test |
| **DoD-4** | C0 binding signature is `(route, validated_request)`, reads `app_payload["jd_payload"]` etc. | signature inspection + test |
| **DoD-5** | PA binding signature is `(route, l1_plan, fec, validated_request)`, reads `app_payload["target"]` etc. | signature inspection + test |
| **DoD-6** | apps_rg_dispatch passes `validated_request` to C0 + PA, not `envelope.payload` | source scan + test |
| **DoD-7** | CompiledPromptArtifact carries `slot_lineage_map` + `component_hash_map`; PA populates them | test |
| **DoD-8** | RouteContract is deterministic across runs with same `app_payload` | test |
| **DoD-9** | CompiledPromptArtifact `compilation_hash` deterministic across runs with same inputs | test |
| **DoD-10** | No L1/L0/C0/PA code path reads `envelope.payload` or `AppsRgIngressPayload` attributes | AST gate |
| **DoD-11** | New tests: ≥10 covering consumption, determinism, fail-closed, no-bypass | pytest count |
| **DoD-12** | CI gate `check_apps_rg_app_payload_consumption.py` passes | exit 0 |
| **DoD-13** | 4 artifacts emitted under `artifacts/apps_rg/ag2_*` | file existence |
| **DoD-14** | apps_rg_dispatch end-to-end still returns `exit_status=success` | smoke run |

## Files In Scope

| Path | Action |
|---|---|
| `agentic_core/runtime/contracts/l1_plan_contract.py` | add 5 projection fields |
| `agentic_core/runtime/contracts/route_contract.py` | add 4 routing-derivation fields |
| `agentic_core/runtime/contracts/compiled_prompt_artifact.py` | add 3 lineage/hash fields |
| `agentic_core/L1_cognition/apps_rg_l1_binding.py` | read `app_payload`, populate projections |
| `agentic_core/L0_routing/apps_rg_l0_binding.py` | derive route_family + cache_eligibility |
| `agentic_core/runtime/c0/apps_rg_c0_binding.py` | signature change → ValidatedRequest |
| `agentic_core/prompt_governance/apps_rg_pa_binding.py` | signature change → ValidatedRequest + lineage maps |
| `agentic_core/runtime/entry/apps_rg_dispatch.py` | pass validated_request to C0 + PA |
| `tests/_apps_contract/test_apps_rg_app_payload_consumption.py` | new — ≥10 tests |
| `ops_scripts/ci/check_apps_rg_app_payload_consumption.py` | new |
| `artifacts/apps_rg/ag2_app_payload_consumption_matrix.json` | new |
| `artifacts/apps_rg/ag2_no_bypass_map.json` | new |
| `artifacts/apps_rg/ag2_consumption_gap_report.md` | new |
| `artifacts/apps_rg/ag2_acceptance_evidence.json` | new |

## Non-Goals (Hard Laws Restated)

- ❌ Restore parallel apps_rg runtime
- ❌ Bypass agentic_core spine
- ❌ Let L1 route with authority
- ❌ Let L0 infer app semantics from envelope.payload
- ❌ Let PA pull from legacy envelope payload
- ❌ Mutate ChromaDB
- ❌ Generate embeddings
- ❌ Wire provider execution
- ❌ Add new task classes
- ❌ Add new generation modes

## ADG Provenance

backend=adg_sqlite, snapshot=adg_indexed_<latest>.sqlite (read-only inspection — no mutation)
