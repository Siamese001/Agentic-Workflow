# apps_lic Runtime Proof Bundle — Closeout Receipt

**Date:** 2026-05-20  
**Scope:** Canonical per-run `runtime_proof_bundle.json` for 99-style no-bypass verification.

## Summary

Each canonical `apps_lic` spine run now emits [runtime_proof_bundle.json](artifacts/apps_lic/spine_convergence/runs/cli_runtime_proof_bundle_cert/runtime_proof_bundle.json) in the run artifact directory. The bundle validates stage receipts, chain coherence, canonical producer, shadow-surface absence, app-owned bindings, R4/R5 policy, and durable-write invariants. Fail-closed: dispatch raises if bundle status is not `PASS`.

## Implementation

| Component | Path |
|-----------|------|
| Proof gate | [runtime_proof_bundle.py](apps_lic/runtime/dispatch/runtime_proof_bundle.py) |
| Wiring | [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) |
| Tests | [test_runtime_proof_bundle.py](tests/apps_lic/test_runtime_proof_bundle.py) |

## Chat waves (2026-05-20)

| Wave | Status | Evidence |
|------|--------|----------|
| W1 Runtime proof bundle module | COMPLETED | [runtime_proof_bundle.py](apps_lic/runtime/dispatch/runtime_proof_bundle.py) |
| W2 Canonical dispatch wiring | COMPLETED | [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) |
| W3 Tests + CI | COMPLETED | pytest 12 + AG-8 109 + golden 18/18 |
| W4 Closeout + CLI | COMPLETED | [runtime_proof_bundle_waves_manifest.json](docs/reports/apps_lic/runtime_proof_bundle_waves_manifest.json) |

Plan: [apps-lic-runtime-proof-bundle-c9e2f1.md](.cursor/plans/apps-lic-runtime-proof-bundle-c9e2f1.md)

## Proof commands

```text
python -m apps_lic --manual-brief "..." --recipient-class executive --channel email --outreach-mode cold --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_runtime_proof_bundle_cert
→ exit 0, runtime_proof_bundle.json status=PASS

pytest tests/apps_lic/test_runtime_proof_bundle.py tests/apps_lic/test_canonical_dispatch_smoke.py tests/apps_lic/test_canonical_dispatch_manifest_x3.py -q
→ 12 passed

pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -q
→ 109 passed

python ops_scripts/ci/check_apps_lic_golden_path_runtime.py --fail-closed
→ ALL CHECKS PASSED (18 runtime probes)
```
