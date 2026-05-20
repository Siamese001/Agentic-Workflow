# apps_lic x3 manifest serialization fix — closeout

**Date:** 2026-05-20  
**Root cause:** [x3_unknown_investigation_receipt.md](x3_unknown_investigation_receipt.md)

## Fix

Single SSOT helper `x3_manifest_fields()` in [spine_run_result.py](apps_lic/runtime/dispatch/spine_run_result.py):

1. `final_output["disposition"]` (e.g. `X3D`)
2. else `exit_status`
3. else `"UNKNOWN"`

[canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) writes `x3_disposition`, `exit_status`, `outcome_authorized` to manifest and `SpineRunResult`.

## CLI re-certification

```bash
python -m apps_lic --recipient-class executive --channel email --outreach-mode cold \
  --manual-brief apps_lic/scripts/truist_pascal_brief.json \
  --request-id cli_canonical_cert_x3_fix \
  --artifact-dir artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_x3_fix
```

**Exit code:** 0 | Log: `x3=X3D`

**Manifest:** [spine_run_manifest.json](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_x3_fix/spine_run_manifest.json)
