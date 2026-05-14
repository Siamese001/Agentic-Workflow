"""apps_research dispatch — RETIRED (Bundle C profile migration).

Use instead:
    from apps_research.runtime.profile_builder import build_app_runtime_contract
    AppIngressRunner(profile=build_app_runtime_contract()).run(payload)

This module is kept as a tombstone only. Importing raises ImportError.
"""

raise ImportError(
    "apps_research_dispatch is RETIRED (Bundle C profile migration). "
    "Use: from apps_research.runtime.profile_builder import "
    "build_app_runtime_contract; "
    "AppIngressRunner(profile=build_app_runtime_contract()).run(payload)"
)
