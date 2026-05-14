"""apps_research runtime entrypoints — Bundle C profile migration.

apps_research_parse and apps_research_dispatch are RETIRED.
Use profile_builder instead:
    from apps_research.runtime.profile_builder import build_app_runtime_contract
    AppIngressRunner(profile=build_app_runtime_contract()).run(payload)
"""
from __future__ import annotations

__all__: list[str] = []
