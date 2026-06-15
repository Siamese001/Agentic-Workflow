# apps_rg Pytest Source-of-Truth Triage

Generated from the full apps_rg keyword run:

```text
python -m pytest -q tests -k apps_rg --tb=short
```

Evidence log:

```text
artifacts/test_runs/apps_rg_full_20260615_142136/stdout.log
agentic_core/L0_routing/logs/guardian_report.json
```

## Run Summary

Pytest selected a very broad cross-repo set:

| Metric | Count |
|---|---:|
| Collected | 55,817 |
| Deselected | 49,169 |
| Selected | 6,648 |
| Passed | 5,824 |
| Failed | 765 |
| Errors | 113 |
| Skipped | 96 |
| XFailed | 9 |
| Warnings | 116 |
| Duration | 14:12 |

Guardian category rollup from the generated report:

| Category | Count |
|---|---:|
| import_safety | 45 |
| ssot_alignment | 8 |
| other | 825 |
| mro_integrity | 0 |
| forensic | 0 |
| subatomic | 0 |

The focused hotspot-gap tests added in this wave all passed in the focused run
and in the broad run. They are not part of the failure inventory.

## Source-of-Truth Rule

Do not ask whether to change the test or the app first. Ask:

```text
Is the failing test protecting an active product contract, or preserving an obsolete implementation expectation?
```

Use this decision:

| Bucket | Meaning | Default action |
|---|---|---|
| LAW | Safety, governance, provenance, X3, L4, PA/C0/Exit authority | Fix app/config |
| CONTRACT | Current product or CLI behavior | Usually fix app/config |
| MIGRATION | Refactor guard for an active migration | Inspect source, then app or test |
| ARCHAEOLOGY | Removed module, old provider, old path, exact helper name | Fix/quarantine test or fixture |
| HARNESS | Collection/import side effect, fixture, live-provider environment | Fix test harness/import pattern |

## First-Pass Failure Queues

### Fix App or Active Config First

These clusters look like active law or product-contract failures unless a more
specific active source proves the test is stale.

| Cluster | Failed tests | Initial bucket | Reason |
|---|---:|---|---|
| `tests/_apps_contract/test_apps_rg_exit_evidence_wiring.py` | 55 | LAW/CONTRACT | Exit evidence, FEC, and proof wiring are authority surfaces. |
| `tests/_apps_contract/test_apps_rg_c0_minimum_safety.py` | 52 | LAW/CONTRACT | C0 grounding and support-status behavior are safety gates. |
| `tests/_apps_contract/test_apps_rg_exit_gate_harness.py` | 30 | LAW/CONTRACT | Exit/X3 gate harness failures are product authorization concerns. |
| `tests/_apps_contract/test_apps_rg_l4_namespace_manifest.py` | 17 | LAW | L4 namespace/write boundaries are governance boundaries. |
| `tests/_apps_contract/test_apps_rg_evidence_trace_map.py` | 12 | LAW/CONTRACT | Evidence traceability protects provenance. |
| `tests/_apps_contract/test_apps_rg_pa_failure_blocks_model_call.py` | 6 | LAW | PA failure must block downstream model calls. |
| `tests/governance/test_apps_rg_spine_refactor.py` | 18 | LAW/MIGRATION | Import and spine-boundary failures may be real app-boundary regressions. |

### Test, Fixture, or Quarantine Candidates

These require an active source check before touching product code. If the only
source is the test itself, do not promote the expectation to product law.

| Cluster | Failed tests | Initial bucket | Reason |
|---|---:|---|---|
| `tests/_apps_contract/test_apps_rg_u0_structured_resume_support.py` | 57 | MIXED | Some assertions are U0 law; others may preserve old import/path expectations. Split before fixing. |
| `tests/_apps_contract/test_apps_rg_domain_config_profiles.py` | 49 | MIXED | Manifest/config assertions may be active contracts or stale fixture-shape checks. |
| `tests/integration/test_per_app_layer_match.py` | 46 | MIGRATION/HARNESS | Layer-match failures need ADG/source check before app changes. |
| `tests/_apps_contract/test_apps_rg_workflow_manifest_profile.py` | 33 | MIXED | Executable-code-in-manifest is active; exact manifest shape may be stale. |
| `tests/_apps_contract/test_apps_rg_l2_output_patches.py` | 13 | MIGRATION | Could protect active L2 output contract or old patch surface. |
| `tests/_apps_contract/test_apps_rg_rb17_guarded_activation_plan.py` | 13 | MIGRATION | Needs active plan/source citation before app changes. |
| `tests/_apps_contract/test_w2_judge_stubs.py` | 4 | ARCHAEOLOGY | Stub/import expectations are likely stale if the provider/judge surface was removed. |

### Harness and Collection Cleanup First

The broad `tests -k apps_rg` command still collects every test module before
deselection. That produced 113 collection/runtime errors across `apps_eval`,
`apps_research`, `apps_shared`, system-learning, runtime-cert, and tool tests.

Initial decision: fix collection hygiene, lazy imports, fixtures, or use a more
bounded apps_rg suite for gating before changing `apps_rg` product code.

Examples:

| Cluster | Initial bucket | Reason |
|---|---|---|
| `tests/apps_eval/*` collection errors | HARNESS / apps_eval boundary | apps_eval should be an exam instrument; it should not require product runtime internals at collection. |
| `tests/apps_research/*` collection errors | HARNESS | Cross-app import/fixture issue triggered by global collection. |
| `tests/unit/system_learning/*` collection errors | HARNESS | Not apps_rg product behavior; broad keyword selection collects these anyway. |
| `tests/unit/tools/runtime_cert/*` collection errors | HARNESS | Tooling fixture/import errors, not apps_rg product functionality. |

## Triage Note Template

Use this before changing code for any individual failing pytest:

```text
Test:
<node id>

Failure:
<one sentence>

What is it protecting?
LAW / CONTRACT / MIGRATION / ARCHAEOLOGY / HARNESS

Active source:
<doc/code/plan line or "none found">

Decision:
APP FIX / CONFIG FIX / TEST FIX / FIXTURE FIX / QUARANTINE

Reason:
<one sentence>
```

## Recommended Next Wave

1. Create a bounded apps_rg gating command that avoids unrelated collection errors.
   Candidate:

   ```text
   python -m pytest -q tests/unit/apps_rg tests/apps_rg tests/e2e/apps_rg tests/runtime/test_apps_rg_e2e_proof.py tests/governance/test_apps_rg_*.py tests/architecture/test_apps_rg_import_boundary_ratchet.py --tb=short
   ```

2. Split the top five clusters into individual triage notes with active-source
   citations before changing either app code or tests.

3. Start with LAW/CONTRACT clusters:
   `exit_evidence_wiring`, `c0_minimum_safety`, `exit_gate_harness`,
   `l4_namespace_manifest`, and `evidence_trace_map`.

4. Separately clean collection errors and stale archaeology tests. Do not mix
   those changes with product fixes.

## Implemented Harness Wave

Implemented in branch `codex/apps-rg-wave2-tests`:

| Change | Bucket | Decision |
|---|---|---|
| Added `tests/apps_eval/conftest.py` | HARNESS / ARCHAEOLOGY | Quarantines retired pre-reset `tests/apps_eval` files that import deleted agent/orchestrator/service surfaces. |
| Added `tests/unit/apps_eval/conftest.py` | HARNESS / ARCHAEOLOGY | Quarantines three unit tests for removed apps_eval HOP, governed-run CLI, and legacy regression-taxonomy surfaces. |
| Added `apps_eval/_telemetry.py` | HARNESS / CONTRACT | Restores a fail-open compatibility shim that delegates emitters to the core lifecycle trace contract without making apps_eval a runtime authority. |

Verification after this wave:

```text
python -m pytest -q tests/apps_eval apps_eval/tests tests/unit/apps_eval --tb=short
119 passed, 3 warnings in 0.83s

python -m pytest -q tests -k apps_rg --collect-only --tb=short
6648/55817 tests collected, 91 errors
```

The broad apps_rg keyword collection improved from 94 errors after the top-level
apps_eval quarantine to 91 errors after the unit apps_eval cleanup and telemetry
shim. The earlier full apps_rg keyword run reported 113 total errors. The
remaining 91 collection errors are outside active apps_eval and should stay in
the HARNESS/MIGRATION queue until each cluster has an active-source check.

## Implemented Runtime ADG Harness Wave

Implemented the next HARNESS/MIGRATION cluster for runtime-cert and runtime ADG
moved import paths:

| Change | Bucket | Decision |
|---|---|---|
| Added `agentic_core/L6_system_learning/app_route_contracts.py` | HARNESS / MIGRATION | Re-export canonical `runtime_adg.app_route_contracts` for runtime-cert tools/tests using the old top-level path. |
| Expanded `agentic_core/L6_system_learning/snapshot/__init__.py` | HARNESS / MIGRATION | Re-export runtime ADG node, edge, factory, and JSON helpers expected by tests. |
| Expanded `agentic_core/L6_system_learning/span_contracts.py` | HARNESS / MIGRATION | Preserve top-level span contract exports, including runtime-cert's read-only internal contract tables. |
| Added `agentic_core/L6_system_learning/manifest_hash.py` | HARNESS / MIGRATION | Re-export runtime ADG manifest hash helpers. |
| Added `agentic_core/L6_system_learning/formal_exception_evidence.py` | HARNESS / MIGRATION | Re-export formal exception evidence helpers. |
| Added `agentic_core/L6_system_learning/runtime_span_emitter.py` | HARNESS / MIGRATION | Re-export runtime ADG tier-1 span emitters. |
| Added `agentic_core/L6_system_learning/store.py` | HARNESS / MIGRATION | Re-export runtime ADG stores and deserializer. |
| Added `agentic_core/L6_system_learning/materializer.py` | HARNESS / MIGRATION | Re-export runtime ADG materializer and privacy helper symbols used by tests. |
| Added `agentic_core/L6_system_learning/auto_persistence.py` | HARNESS / MIGRATION | Re-export runtime ADG auto-persistence adapter. |
| Fixed `runtime_adg/manifest_hash.py` repo-root inference | HARNESS | Resolve app manifests from the checkout root after the package move. |
| Updated `tools/runtime_cert/smoke/live_trace_smoke.py` | HARNESS | Remove eager `from agentic_core` imports from the smoke helper source while preserving lazy helper use. |

Verification after this wave:

```text
python -m pytest -q tests/unit/system_learning/runtime_adg/test_app_route_contracts.py \
  tests/unit/system_learning/runtime_adg/test_span_contracts.py \
  tests/unit/system_learning/runtime_adg/test_tier2_contracts.py \
  tests/unit/system_learning/runtime_adg/test_manifest_hash.py \
  tests/unit/system_learning/runtime_adg/test_formal_exception_evidence.py \
  tests/unit/tools/runtime_cert/test_trace_row_normalizer.py \
  tests/unit/tools/runtime_cert/test_runtime_adg_query_adapter.py \
  tests/unit/tools/runtime_cert/extractors/test_r3_evidence.py \
  tests/unit/tools/runtime_cert/extractors/test_formal_exception_evidence.py \
  tests/unit/tools/runtime_cert/extractors/test_btc_evidence.py \
  tests/unit/tools/runtime_cert/reports/test_attribute_hardening_gap.py \
  tests/unit/tools/runtime_cert/reports/test_phase_c_closeout.py \
  tests/unit/tools/runtime_cert/smoke/test_live_trace_smoke.py --tb=short
339 passed, 3 warnings in 0.92s

python -m pytest -q tests/unit/system_learning/runtime_adg/test_store_guardrail.py \
  tests/unit/system_learning/runtime_adg/test_runtime_span_emitter.py \
  tests/system_learning/runtime_adg/test_materializer_privacy.py \
  tests/unit/tools/runtime_adg/test_backfill_trace_index.py --tb=short
35 passed, 3 warnings in 0.37s

python -m pytest -q tests -k apps_rg --collect-only --tb=short
6648/56319 tests collected, 66 errors
```

The broad apps_rg keyword collection is now down from 91 to 66 errors after this
wave. The remaining errors are still mostly unrelated collection blockers:
apps_research/apps_shared harness issues, broad system_learning engine top-level
imports, retired apps_eval engine imports, missing archived tooling fixtures,
and non-app C0/context test import failures.
