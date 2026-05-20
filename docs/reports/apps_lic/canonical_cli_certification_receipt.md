# apps_lic canonical CLI certification

**Date:** 2026-05-20  
**Architecture:** unchanged — `python -m apps_lic` → `run_canonical_apps_lic_spine` only.

## Command

```bash
python -m apps_lic \
  --recipient-class executive \
  --channel email \
  --outreach-mode cold \
  --manual-brief apps_lic/scripts/truist_pascal_brief.json \
  --request-id cli_canonical_cert_20260520 \
  --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520
```

**Exit code:** `0`  
**Wall time:** ~12s  
**Log run_id:** `run_lic_89afed9d1fd7` (transport id; artifact dir is explicit CLI path)

## Provider classification

| Class | Evidence |
|-------|----------|
| **Live local vLLM** | `httpx: HTTP Request: POST http://localhost:8000/v1/chat/completions "HTTP/1.1 200 OK"` |
| Not stub-only | `l2_execution_status=completed` (not `stub_fallback`) |
| Not provider-blocked | CLI returned 0; HOP call succeeded |

## Latest run directory

[cli_canonical_cert_20260520](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520/)

| Artifact | Path |
|----------|------|
| Ingress | [ingress_raw.json](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520/ingress_raw.json) |
| Route | [route_contract.json](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520/route_contract.json) |
| Manifest | [spine_run_manifest.json](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520/spine_run_manifest.json) |
| C0 summary | [fec_summary.json](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520/fec_summary.json) |

## Spine summary (from manifest)

- `producer_component`: `apps_lic.runtime.dispatch.canonical_dispatch`
- `route_family`: `R4_MANAGED_DRAFT`
- `execution_form`: `managed_workflow`
- `l3_participated`: true
- `c0_invoked` / `pa_invoked`: true
- `l2_execution_status`: `completed`
- `terminal_r5`: false
- **`x3_disposition`**: `UNKNOWN`

## Stage receipts on disk

`canonical_dispatch` does **not** write per-stage JSON receipt files under the artifact dir; participation is aggregated in [spine_run_manifest.json](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520/spine_run_manifest.json). C0 evidence hash/count in [fec_summary.json](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520/fec_summary.json).

## Explicit non-claims

- X3 is **not** `ALLOW` / `ALLOW_FINISH` / `COMMIT_REQUEST` — Exit ran and emitted `UNKNOWN` (material gate posture per exit binding).
- No separate L3/L2/PA/Exit sidecar JSON files in artifact dir (by design of current dispatch).
- Not cloud-hosted provider proof — local `localhost:8000` only.
