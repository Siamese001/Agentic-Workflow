---
status: completed
type: contract-first-harness
created: 2026-05-10
completed: 2026-05-10
slug: apps-rg-u0-reflection-harness-79d032
exists_on_disk: true
---

# apps_rg U0 Payload Reflection Harness

PLAN_CREATED: plan=apps-rg-u0-reflection-harness-79d032 path=.windsurf/plans/apps-rg-u0-reflection-harness-79d032.md status=in-progress

PLAN_COMPLETE: plan=apps-rg-u0-reflection-harness-79d032 note="13 files; 30/30 tests pass; valid fixture: 56 pointers (20 MAPPED, 12 DERIVED, 24 DEFERRED, 0 silently_dropped, 0 unknown_mappings); deterministic digests; all 4 invalid fixtures fail-closed with named exceptions"

## Goal

Ensure every apps_rg ingress JSON field is correctly reflected into U0 and **cannot be silently dropped** during consolidation into agentic_core. The contract-first harness catches any field that validates schema-wise but is not mapped to a downstream consumer.

## Core Rule

> **A field may be deferred. A field may not disappear.**

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| **W1** | P1.1–P1.3 | Contract artifacts (model + schema + field map) | ~8k | in-progress | Pydantic model loads; schema validates against itself; field map covers 100% of model pointers |
| **W2** | P2.1–P2.2 | U0 adapter + ValidatedRequest extension | ~6k | pending | Adapter parses valid fixture; raises on each invalid fixture |
| **W3** | P3.1–P3.3 | Fixtures + tests (reflection + downstream) | ~10k | pending | All tests pass; pytest reports zero collection errors |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **P1.1** | Contracts package | `apps_rg/contracts/__init__.py`, `apps_rg_ingress_contract.v1.py` | Pydantic 2 model with strict, frozen | 3k | in-progress |
| **P1.2** | JSON schema | `apps_rg_ingress_contract.v1.schema.json` | Generated via `model_json_schema()`, persisted, frozen-checked in test | 2k | pending |
| **P1.3** | Field-map SSOT | `apps_rg_ingress_field_map.v1.yaml` | Every JSON Pointer → status (MAPPED/DERIVED/REJECTED/DEFERRED) + reason | 3k | pending |
| **P2.1** | ValidatedRequest extension | `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` | Add `app_payload: Mapping = {}` (additive, default-empty) | 1k | pending |
| **P2.2** | U0 reflection adapter | `agentic_core/runtime/u0/__init__.py`, `apps_rg_u0_adapter.py`, `reflection_receipt.py` | JSON pointer enumeration; field map status lookup; fail-closed receipt | 5k | pending |
| **P3.1** | Test fixtures | 5 fixture JSON files | Valid + 4 invalid permutations | 3k | pending |
| **P3.2** | Reflection tests | `test_apps_rg_u0_payload_reflection.py` | 12 tests | 4k | pending |
| **P3.3** | Downstream consumption tests | `test_apps_rg_downstream_field_consumption.py` | 8 tests | 3k | pending |

## Definition of Done

| ID | Criterion | Verification |
|---|---|---|
| **DoD-1** | Pydantic model loads + JSON schema generates | `python -c "from apps_rg.contracts.apps_rg_ingress_contract_v1 import AppsRgIngressContractV1; AppsRgIngressContractV1.model_json_schema()"` exits 0 |
| **DoD-2** | Field map YAML loads + every model field has a pointer entry | Test `test_field_map_covers_all_model_pointers` passes |
| **DoD-3** | U0 adapter rejects each invalid fixture with the documented exception | All 4 negative tests pass |
| **DoD-4** | U0 adapter accepts valid fixture and emits PASS receipt | `test_valid_payload_produces_validated_request_and_pass_receipt` passes |
| **DoD-5** | Smoke run: `python -m apps_rg.contracts.apps_rg_ingress_contract_v1 --emit-schema > /tmp/schema.json` exits 0 | Module entry point regenerates the schema |
| **DoD-6** | Reflection receipt is deterministic (same input → same digests) | `test_input_payload_digest_is_deterministic` + `test_validated_request_digest_is_deterministic` pass |

## Files In Scope (canonical)

| Path | Action | LOC est |
|---|---|---|
| `apps_rg/contracts/__init__.py` | create | 5 |
| `apps_rg/contracts/apps_rg_ingress_contract_v1.py` | create | ~250 |
| `apps_rg/contracts/apps_rg_ingress_contract.v1.schema.json` | create (generated) | ~200 |
| `apps_rg/contracts/apps_rg_ingress_field_map.v1.yaml` | create | ~150 |
| `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` | edit (add `app_payload`) | +5 |
| `agentic_core/runtime/u0/__init__.py` | create | 5 |
| `agentic_core/runtime/u0/reflection_receipt.py` | create | ~80 |
| `agentic_core/runtime/u0/apps_rg_u0_adapter.py` | create | ~250 |
| `tests/fixtures/apps_rg/valid_ingress_contract.v1.json` | create | ~80 |
| `tests/fixtures/apps_rg/invalid_missing_jd_hash.json` | create | ~70 |
| `tests/fixtures/apps_rg/invalid_unknown_generation_mode.json` | create | ~80 |
| `tests/fixtures/apps_rg/invalid_unmapped_field.json` | create | ~80 |
| `tests/fixtures/apps_rg/invalid_missing_policy_ref.json` | create | ~70 |
| `tests/_apps_contract/test_apps_rg_u0_payload_reflection.py` | create | ~250 |
| `tests/_apps_contract/test_apps_rg_downstream_field_consumption.py` | create | ~200 |

**Note on filename**: Python forbids dots in module names so `apps_rg_ingress_contract.v1.py` is renamed to `apps_rg_ingress_contract_v1.py`. The user's intent (versioned filename) is preserved via the underscore. The schema and field-map YAML retain dotted names since those are non-importable artifacts.

## Non-Goals

- Restore parallel apps_rg runtime
- Execute apps_rg business logic in U0
- Wire all 61 lost capabilities (see `apps-rg-pre-consolidation-functionality-gap.md`)
- Allow a JSON payload that validates but is ignored downstream

## Acceptance

A run passes only if U0 emits:
- ValidatedRequest (with `app_payload` populated)
- `AppsRgU0ReflectionReceipt` with `pass_status=True`
- zero silently dropped fields (`silently_dropped=()`)
- zero unknown mappings (`unknown_mappings=()`)
- deterministic input payload hash (sha256 over canonical JSON)
- deterministic validated request hash (sha256 over canonical JSON)
- explicit `DEFERRED` reasons for fields not yet consumed

## ADG_HOTSPOT_REPORT

This is a NEW-FILE-DOMINATED change (12 of 13 are creates). Hotspot impact:
- 1 edit to `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` — additive only (new optional field)
- New U0 package (`agentic_core/runtime/u0/`) does not yet have callers; downstream wiring deferred to a future plan that flips `apps_rg/__main__.py` to consume the adapter

| Node | Layer | Fan-in | Fan-out | Action |
|---|---|---|---|---|
| `apps_rg_ingress_payload.py` | core/contracts | high (existing consumers) | low | additive edit only |
| `apps_rg_u0_adapter.py` | core/u0 (new) | 0 (until wired) | low | greenfield |
| `apps_rg_ingress_contract_v1.py` | apps_rg/contracts (new) | 0 (until wired) | low | greenfield |

## ADG_GRAPH_LAYER_EVIDENCE

Greenfield contract harness — no graph-layer queries materially constrain the design. The contract introduces a new boundary surface; future plans (W1 multi-provider, W2 safety mesh per AG decisions) will consume it.
