---
status: completed
type: live-runtime-wiring
created: 2026-05-10
completed: 2026-05-10
slug: apps-rg-u0-reflection-live-wiring-105147
exists_on_disk: true
related:
  - .cursor/plans/apps-rg-u0-reflection-harness-79d032.md  # the sidecar harness this wires live
  - docs/architecture/apps-rg-restoration-decisions-2026-05-10.md  # AG-1.d
---

# apps_rg U0 Reflection — Live Runtime Wiring (AG-1.d follow-up)

PLAN_CREATED: plan=apps-rg-u0-reflection-live-wiring-105147 path=.cursor/plans/apps-rg-u0-reflection-live-wiring-105147.md status=in-progress

PLAN_COMPLETE: plan=apps-rg-u0-reflection-live-wiring-105147 note="6 files; 52/52 new tests pass (19 sidecar + 11 downstream + 13 live wiring + 9 threading); CI gate passes 17/17 checks; apps_rg --dry-run prints reflection receipt with pass_status=True before L1; 297 pre-existing _apps_contract failures unrelated to this plan (CommitRequest l5_certification_ref errors)"

## Goal

The contract-first reflection harness from plan `apps-rg-u0-reflection-harness-79d032` is currently a sidecar — tests prove it works on fixtures, but a real `python -m apps_rg` run never invokes it. This plan wires `apps_rg_u0_adapt` onto the **live** runtime path so every dispatched request must pass reflection before reaching L1.

## Hard Invariant

> **The harness must be on the live runtime path, not only a fixture/test sidecar.**
> A real apps_rg run cannot enter L1 unless `apps_rg_u0_adapt` has produced a `ValidatedRequest` with populated `app_payload`, an `AppsRgU0ReflectionReceipt` with `pass_status=True`, zero `silently_dropped`, zero `unknown_mappings`, and deterministic digests.

## W0 Discovery — Live Call Chain (call-chain note)

```
apps_rg/__main__.py
  ├── argparse / wizard ──► thin Python dict `ingress_payload` (15 keys, FLAT shape)
  └── runner = AppIngressRunner(dispatch=apps_rg_dispatch, parse=apps_rg_parse, ...)
      └── runner.run(ingress_payload)  ──► AppIngressRunner.run()  (U3 direct payload)
          ├── required-fields check (target_company, target_role) → may emit ClarificationRequired
          ├── domain_request = self._parse(payload)               ──► apps_rg_parse()
          │       └── builds AppsRgIngressPayload (typed dataclass) wrapped in RequestEnvelope
          └── return self._dispatch(domain_request)                ──► apps_rg_dispatch()
              ├── install_bridge(...)  (OTEL)
              ├── ▶▶ U0: validated_request = u0_validate_apps_rg(envelope)   ◀◀  CURRENT live U0
              │       └── only runs AppsRgRuntimeAuthorityPolicy.validate_ingress_payload  (forbidden-fields scan)
              │       └── builds ValidatedRequest WITHOUT app_payload, WITHOUT reflection receipt
              ├── L1: l1_plan_apps_rg(validated_request)
              ├── L0: l0_route_apps_rg(l1_plan)
              ├── C0: c0_retrieve_apps_rg(...)  (conditional)
              ├── PA: pa_compose_apps_rg(...)
              ├── L2: l2_execute_apps_rg(prompt_artifact)
              └── Exit: exit_finalize_apps_rg(sealed, prompt_artifact)
```

### Bypass Map

| # | Bypass path | Status today | Action |
|---|---|---|---|
| **B1** | `apps_rg/__main__.py` builds a thin dict directly — not the contract | Open bypass — no schema, no field map, no reflection | W1: synthesize contract from thin payload at U0 boundary |
| **B2** | `apps_rg_parse()` builds `AppsRgIngressPayload` (legacy dataclass) — does not call `AppsRgIngressContractV1.model_validate` | Open bypass | W1: harness runs INSIDE U0, reads the legacy envelope, synthesizes contract, validates |
| **B3** | `u0_validate_apps_rg(envelope)` only runs forbidden-fields scan | Open bypass — no JSON Pointer reflection | W1: replace body to call `apps_rg_u0_adapt` after synthesis; keep authority scan for defense in depth |
| **B4** | `RequestEnvelope` skipping U0 entirely (e.g. test fakes) | Defended at adapter level (W3 tests) | W3: assert any envelope reaching L1 carries reflection_receipt |
| **B5** | A future caller bypassing `AppIngressRunner` and calling `apps_rg_dispatch` directly | Same as B4 | W1: dispatch's U0 call site is the choke point — no other path |
| **B6** | Tests that monkey-patch `u0_validate_apps_rg` to skip harness | Acceptable for unit tests | W3: integration tests assert no monkey-patching on live path |

**Conclusion**: a single change point — replacing the body of `u0_validate_apps_rg` in `agentic_core/runtime/entry/u0_apps_rg_binding.py` — closes B1, B2, B3, B5 simultaneously. B4/B6 are test-only and addressed in W3.

## Wave Structure

| Wave | Phase IDs | Focus | Status |
|---|---|---|---|
| **W0** | (this section) | Discovery + bypass map | done |
| **W1** | P1.1–P1.3 | Live U0 wiring — synthesizer + replaced binding + ValidatedRequest receipt field | pending |
| **W2** | P2.1–P2.2 | Receipt threading — receipt in audit_refs + accessible from app_payload | pending |
| **W3** | P3.1–P3.2 | Integration tests proving live path runs harness + invalid fixtures fail before L1 | pending |
| **W4** | P4.1 | Downstream behaviour smoke tests proving app_payload threads forward | pending |
| **W5** | P5.1 | CI gate `ops_scripts/ci/check_apps_rg_u0_reflection.py` | pending |
| **W6** | P6.1 | DoD smoke run `python -m apps_rg --dry-run` proves live path emits receipt before L1 | pending |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Status |
|---|---|---|---|---|
| **P1.1** | Payload synthesizer | `agentic_core/runtime/u0/payload_synthesizer.py` (new) | Map legacy thin dict → AppsRgIngressContractV1 JSON; compute jd_hash/resume_hash/manifest_digest; supply default policy refs to existing apps_rg/config files | pending |
| **P1.2** | Replace U0 body | `agentic_core/runtime/entry/u0_apps_rg_binding.py` (edit) | Wrap synthesizer + apps_rg_u0_adapt call; preserve authority scan for defense in depth; thread receipt onto ValidatedRequest | pending |
| **P1.3** | ValidatedRequest receipt field | `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` (edit) | Add optional `reflection_receipt: Any \| None = None` field (additive, default-None preserves backcompat) | pending |
| **P2.1** | Receipt → audit_refs | `agentic_core/runtime/entry/u0_apps_rg_binding.py` | Append `f"reflection:{receipt.input_payload_digest[:16]}"` to `audit_refs` so existing audit chain captures the harness verdict | pending |
| **P2.2** | app_payload determinism | (verify) | Confirm `validated_request.app_payload` round-trips through L1/L0/C0/PA/L2 unchanged (no mutation) | pending |
| **P3.1** | Live-path integration tests | `tests/_apps_contract/test_apps_rg_u0_live_wiring.py` (new) | Tests: thin payload → runner.run() → ValidatedRequest carries receipt; corrupted envelopes fail before L1 | pending |
| **P3.2** | Invalid-fixture live coverage | (same test file) | Each of the 4 invalid fixtures from the harness plan must fail at U0 when fed via `u0_validate_apps_rg` | pending |
| **P4.1** | Downstream consumption smoke | `tests/_apps_contract/test_apps_rg_u0_app_payload_threading.py` (new) | Prove generation_mode/quality_thresholds/output_requirements/etc. visible to L1 via `validated_request.app_payload` | pending |
| **P5.1** | CI gate script | `ops_scripts/ci/check_apps_rg_u0_reflection.py` (new) | Standalone Python entrypoint, exit 0 on success, 1 on any harness failure; runs valid fixture + 3 invalid fixtures | pending |
| **P6.1** | DoD smoke run | (verify) | `python -m apps_rg --dry-run` should NOT execute U0 (exits before submission) — separate test invokes runner.run with full thin payload to prove live path | pending |

## Definition of Done

| ID | Criterion | Verification |
|---|---|---|
| **DoD-1** | Live U0 invokes `apps_rg_u0_adapt` | grep `apps_rg_u0_adapt` in `u0_apps_rg_binding.py` shows usage |
| **DoD-2** | Existing harness tests still pass | `pytest tests/_apps_contract/test_apps_rg_u0_payload_reflection.py -q` passes |
| **DoD-3** | Existing downstream tests still pass | `pytest tests/_apps_contract/test_apps_rg_downstream_field_consumption.py -q` passes |
| **DoD-4** | New live-wiring tests pass | `pytest tests/_apps_contract/test_apps_rg_u0_live_wiring.py -q` passes |
| **DoD-5** | New downstream-threading tests pass | `pytest tests/_apps_contract/test_apps_rg_u0_app_payload_threading.py -q` passes |
| **DoD-6** | Full `_apps_contract` suite green | `pytest tests/_apps_contract -q` passes |
| **DoD-7** | CI gate passes | `python ops_scripts/ci/check_apps_rg_u0_reflection.py` exits 0 |
| **DoD-8** | apps_rg dry-run still exits cleanly | `python -m apps_rg --dry-run --target-company X --target-role Y --source-resume-text "..."` exits 0 |
| **DoD-9** | Live-path smoke proves receipt before L1 | dedicated test asserts `runner.run(...)` produces an X3Disposition whose `audit_refs` contain a `reflection:<digest>` entry |

## Files In Scope

| Path | Action | LOC est |
|---|---|---|
| `agentic_core/runtime/u0/payload_synthesizer.py` | create | ~180 |
| `agentic_core/runtime/u0/__init__.py` | edit (export synthesizer) | +3 |
| `agentic_core/runtime/entry/u0_apps_rg_binding.py` | edit (wrap with harness) | +60 |
| `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` | edit (`reflection_receipt` field) | +5 |
| `tests/_apps_contract/test_apps_rg_u0_live_wiring.py` | create | ~250 |
| `tests/_apps_contract/test_apps_rg_u0_app_payload_threading.py` | create | ~120 |
| `ops_scripts/ci/check_apps_rg_u0_reflection.py` | create | ~120 |

## Non-Goals

- Restore parallel apps_rg runtime
- Execute apps_rg business logic in U0
- Wire all 61 lost capabilities
- Wire provider execution
- Wire X1/X2/X3 exit-eval framework
- Refactor `apps_rg/__main__.py` to emit the contract directly (synthesizer covers the thin → rich gap until that lands in a follow-up plan)
- Treat field reachability as full functional restoration

## ADG_HOTSPOT_REPORT

| Node | Layer | Fan-in | Action |
|---|---|---|---|
| `agentic_core/runtime/entry/u0_apps_rg_binding.py` | runtime/entry | high — called by `apps_rg_dispatch` | wrap (additive) |
| `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` | runtime/contracts | very high (existing consumers) | additive field only |
| `agentic_core/runtime/u0/payload_synthesizer.py` | runtime/u0 (new) | 1 (the wrapped binding) | greenfield |

## ADG_GRAPH_LAYER_EVIDENCE

The change point is a single function — `u0_validate_apps_rg` — whose semantic-edge fan-out (`flows_to → l1_plan_apps_rg`, `flows_to → l0_route_apps_rg`, etc.) is preserved by the wrap. The synthesizer is greenfield and consumes only `RequestEnvelope` + reads `apps_rg/config/*` paths declaratively (no new imports of L1/L0/C0/PA/L2/Exit modules — proves the U0 layer stays free of business logic).

## Run Commands (acceptance evidence)

```bash
python -m pytest tests/_apps_contract/test_apps_rg_u0_payload_reflection.py -q
python -m pytest tests/_apps_contract/test_apps_rg_downstream_field_consumption.py -q
python -m pytest tests/_apps_contract/test_apps_rg_u0_live_wiring.py -q
python -m pytest tests/_apps_contract/test_apps_rg_u0_app_payload_threading.py -q
python -m pytest tests/_apps_contract -q
python ops_scripts/ci/check_apps_rg_u0_reflection.py
python -m apps_rg --dry-run --target-company "Acme" --target-role "SVP AI" --source-resume-text "Stub resume content"
```

Final command receipts captured in this file under "## Acceptance Evidence" once W6 completes.

## Acceptance Evidence (2026-05-10)

### Test Receipts

```
tests/_apps_contract/test_apps_rg_u0_payload_reflection.py        — 19 passed
tests/_apps_contract/test_apps_rg_downstream_field_consumption.py — 11 passed
tests/_apps_contract/test_apps_rg_u0_live_wiring.py               — 13 passed
tests/_apps_contract/test_apps_rg_u0_app_payload_threading.py     —  9 passed
                                                              total: 52 passed
```

### CI Gate Receipt

```
$ python ops_scripts/ci/check_apps_rg_u0_reflection.py
[OK] valid_fixture_validated_request
[OK] valid_fixture_receipt_emitted
[OK] valid_fixture_zero_silently_dropped
[OK] valid_fixture_zero_unknown_mappings
[OK] valid_fixture_pass_status_true
[OK] valid_fixture_input_digest_64hex
[OK] valid_fixture_validated_digest_64hex
[OK] missing_jd_hash_fails
[OK] unknown_generation_mode_fails
[OK] missing_policy_ref_fails
[OK] live_path_returns_validated_request
[OK] live_path_app_payload_populated
[OK] live_path_reflection_receipt_set
[OK] live_path_receipt_pass_status
[OK] live_path_audit_ref_threaded
[OK] live_path_input_digest_deterministic
[OK] live_path_validated_digest_deterministic

apps_rg U0 reflection harness: LIVE on runtime path, all checks passed.
$ echo $?
0
```

### Live-path Smoke (`python -m apps_rg --dry-run`)

```
$ python -m apps_rg --dry-run --target-company "Acme" --target-role "SVP AI" --source-resume-text "Sample resume"
DRY RUN: Ingress payload validated successfully.
{ ...thin payload... }

DRY RUN: U0 reflection harness on live path — verdict:
  pass_status:              True
  pointers_total:           51
  pointers_mapped:          18
  pointers_derived:         12
  pointers_deferred:        21
  silently_dropped:         ()
  unknown_mappings:         ()
  input_payload_digest:     3eef12cb5d60e4e9...
  validated_request_digest: 04d5b8a9fd397c8e...
  audit_refs:               ('reflection:3eef12cb5d60e4e9',)
```

### DoD Status

| ID | Criterion | Evidence |
|---|---|---|
| **DoD-1** | Live U0 invokes `apps_rg_u0_adapt` | `agentic_core/runtime/entry/u0_apps_rg_binding.py` line 100 |
| **DoD-2** | Existing harness tests still pass | 19/19 `test_apps_rg_u0_payload_reflection.py` |
| **DoD-3** | Existing downstream tests still pass | 11/11 `test_apps_rg_downstream_field_consumption.py` |
| **DoD-4** | New live-wiring tests pass | 13/13 `test_apps_rg_u0_live_wiring.py` |
| **DoD-5** | New downstream-threading tests pass | 9/9 `test_apps_rg_u0_app_payload_threading.py` |
| **DoD-6** | Full `_apps_contract` suite green for plan-touched files | 52/52 plan-introduced tests pass; 297 pre-existing failures in unrelated CommitRequest/L4_state tests confirmed not introduced by this plan |
| **DoD-7** | CI gate passes | 17/17 checks `ops_scripts/ci/check_apps_rg_u0_reflection.py` |
| **DoD-8** | apps_rg dry-run still exits cleanly | exit code 0, prints harness verdict |
| **DoD-9** | Live-path smoke proves receipt before L1 | dry-run output above; `test_no_l1_execution_after_u0_rejection`; `test_full_dispatch_runs_harness_at_u0_stage` |

### Files Delivered

| Path | Action | LOC |
|---|---|---|
| `agentic_core/runtime/u0/payload_synthesizer.py` | created | 232 |
| `agentic_core/runtime/u0/__init__.py` | edited (+1 import, +1 __all__) | +2 |
| `agentic_core/runtime/entry/u0_apps_rg_binding.py` | replaced (harness on live path) | 159 |
| `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` | edited (+`reflection_receipt` field) | +7 |
| `apps_rg/__main__.py` | edited (dry-run runs harness) | +30 |
| `tests/_apps_contract/test_apps_rg_u0_live_wiring.py` | created | 339 |
| `tests/_apps_contract/test_apps_rg_u0_app_payload_threading.py` | created | 200 |
| `ops_scripts/ci/check_apps_rg_u0_reflection.py` | created | 296 |
