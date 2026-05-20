# apps_lic x3_disposition=UNKNOWN investigation

**Run:** [cli_canonical_cert_20260520](artifacts/apps_lic/spine_convergence/runs/cli_canonical_cert_20260520)  
**Date:** 2026-05-20

## ROOT_CAUSE

**Receipt/manifest serialization defect** in [canonical_dispatch.py](apps_lic/runtime/dispatch/canonical_dispatch.py) lines 379–380 — not an Exit/X1/X2 gate outcome.

Exit produced a valid **ALLOW** disposition (`X3D`); the spine manifest mis-labels it `UNKNOWN` because it reads non-existent attributes on `X3Disposition`.

## Evidence (replay from saved ingress)

| Field | Actual Exit value | Manifest claims |
|-------|-------------------|-----------------|
| `exit_status` | `success` | (not written to manifest) |
| `outcome_authorized` | `True` | (not written to manifest) |
| `final_output["disposition"]` | `X3D` (= V6 ALLOW) | — |
| `gate_verdict_refs` with `:UNKNOWN` | **0** | — |
| `getattr(x3, "disposition")` | `None` | drives manifest |
| Manifest `x3_disposition` | — | `UNKNOWN` (default fallback) |

## UNKNOWN_SOURCE_FIELD_PATHS

1. **Primary (manifest bug):**  
   `apps_lic/runtime/dispatch/canonical_dispatch.py` → `run_canonical_apps_lic_spine` → lines 379–380:
   ```python
   x3_disp = getattr(x3, "disposition", None) or getattr(x3, "final_disposition", "UNKNOWN")
   ```
   `X3Disposition` has neither `disposition` nor `final_disposition` ([x3_disposition.py](agentic_core/runtime/contracts/x3_disposition.py)).

2. **Correct source (not used by manifest):**  
   `X3Disposition.final_output["disposition"]` → `"X3D"`  
   `X3Disposition.exit_status` → `"success"`  
   `X3Disposition.outcome_authorized` → `True`

## Ruled out

| Hypothesis | Verdict |
|------------|---------|
| Missing per-stage receipt JSON on disk | Not cause of UNKNOWN string (Exit ran; gates complete) |
| Missing Exit/X1/X2 material fields | No — 10 gate_verdict_refs, no `:UNKNOWN` suffix |
| Unsupported evidence classification | No — C0 `item_count=4`, FEC hash present |
| Provider output shape | No — L2 `completed`, vLLM 200 OK, draft body in `final_output.text` |
| Local vLLM classification | Live provider; L2 not `stub_fallback` |
| C0/FEC support status | `c0_invoked=true`, fec_summary valid |
| L2 sealed artifact incompleteness | `l2_execution_status=completed`, digest present |
| Audit/replay/trace incompleteness | Not blocking Exit ALLOW |
| X1/X2 aggregation defaults to UNKNOWN | **No** — X2 selected ALLOW (`X3D`) |

## Classification

**Receipt defect** (manifest extraction), not runtime Exit defect, not policy/gate defect, not fixture limitation.

## Smallest zero-loss fix plan (not applied — investigation only)

**Wave 1 (1-line seam, zero architecture change):**  
In `canonical_dispatch.py`, replace manifest extraction with:
```python
x3_str = str(
    (x3.final_output or {}).get("disposition")
    or x3.exit_status
    or "UNKNOWN"
)
```
Optionally add `exit_status` and `outcome_authorized` to `spine_run_manifest.json` for audit parity.

**Wave 2 (optional):** Align `SpineRunResult.x3_disposition` / `to_manifest_dict()` with same source; add contract test asserting manifest `x3_disposition` matches `final_output["disposition"]` after golden CLI run.

No changes to L0 profile, bindings location, HOP, or provider routing required.
