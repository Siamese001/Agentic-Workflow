"""TOMBSTONED — Bundle B profile migration retirement.

underwriting_dispatch.py is RETIRED. All pipeline logic has been
migrated to per-stage bindings in apps_underwriting_ai/runtime/bindings/:

    u0_binding.py      → u0_validate_underwriting
    l1_binding.py      → l1_plan_underwriting
    l0_binding.py      → l0_route_underwriting
    c0_binding.py      → c0_run_underwriting  (C0 + 5×L2 + HITL)
    pa_binding.py      → pa_compose_underwriting_profile
    l2_binding.py      → l2_execute_underwriting
    exit_binding.py    → exit_finalize_underwriting

Profile wired in: apps_underwriting_ai/runtime/profile_builder.py
Entrypoint: AppIngressRunner(profile=build_app_runtime_contract()).run(payload)

DO NOT import anything from this module. It raises ImportError.
"""

raise ImportError(
    "underwriting_dispatch is RETIRED (Bundle B profile migration). "
    "Use: from apps_underwriting_ai.runtime.profile_builder import "
    "build_app_runtime_contract; "
    "AppIngressRunner(profile=build_app_runtime_contract()).run(payload)"
)


# All code below this point is dead — the raise above fires at module load.
# Kept as tombstone reference only.
__all__: list[str] = []
