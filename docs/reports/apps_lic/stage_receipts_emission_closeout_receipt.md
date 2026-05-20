# apps_lic per-stage receipt emission — closeout

**Date:** 2026-05-20

## Implementation

New module [stage_receipts.py](apps_lic/runtime/dispatch/stage_receipts.py) — shared envelope (`schema_version`, `stage`, `request_id`, `run_id`, `trace_id`, `digest`, `upstream_receipt_refs`, `downstream_receipt_refs`, `payload`).

Wired from [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) only (serialization; no binding/route/HOP changes).

## R4 managed-workflow artifacts per run

| File | Stage |
|------|-------|
| [ingress_raw.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/ingress_raw.json) | INGRESS |
| [u0_receipt.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/u0_receipt.json) | U0 |
| [l1_plan_contract.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/l1_plan_contract.json) | L1 |
| [route_contract.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/route_contract.json) | L0 |
| [c0_final_evidence_contract.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/c0_final_evidence_contract.json) | C0 |
| [fec_summary.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/fec_summary.json) | C0 summary |
| [pa_receipt.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/pa_receipt.json) | PA |
| [l3_workflow_receipt.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/l3_workflow_receipt.json) | L3 |
| [l2_execution_receipt.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/l2_execution_receipt.json) | L2 |
| [exit_disposition_receipt.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/exit_disposition_receipt.json) | EXIT |
| [spine_run_manifest.json](artifacts/apps_lic/spine_convergence/runs/cli_stage_receipts_cert/spine_run_manifest.json) | rollup |

`spine_run_manifest.json` includes `stage_receipt_refs` listing all files above.
