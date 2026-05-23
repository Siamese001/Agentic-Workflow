# L3 managed workflow — apps_rg scope (W3 documentation)

**REQ-L3-*** orchestration packaging for `MANAGED_WORKFLOW` routes is **core-owned** (`agentic_core/L3_orchestration/`).

## apps_rg responsibilities

- Emit `RouteContract` with `l3_required=True`, `execution_form=MANAGED_WORKFLOW`, and workflow refs from
  [route_profiles.yaml](route_profiles.yaml).
- Populate `allowed_next_stage=frozenset({"L3"})` when managed workflow is selected.
- Do **not** implement a parallel apps_rg L3 engine or DAG executor.

## Test harness

`APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED=1` activates fixture manifest resolution in
[../../runtime/bindings/l0_binding.py](../../runtime/bindings/l0_binding.py) for CI only.

## Product path

Integrated spine: `canonical_dispatch` → core L3 after L0.

Section lanes: modular PA/L2/Exit until W6 Exit unification; L3 is not invoked on section CLI paths today.
