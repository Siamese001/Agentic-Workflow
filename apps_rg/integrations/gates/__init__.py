"""apps_rg integrations gates — INERT (W0 cleanup).

This package is neutralized per W0 cleanup of quarantine rot.
Runtime gate functionality has been relocated to agentic_core.
"""

# W0 cleanup: Package made inert. No runtime functionality remains here.
__all__: list[str] = []
# """apps_rg Runtime Gates — Domain-specific gate pack.
# 
# Implements resume-generation gates that register into the agentic_core
# RuntimeGateEngine. apps_rg owns domain gate definitions; agentic_core owns
# execution authority and write admission.
# 
# Usage:
#     from agentic_core.runtime_gates import RuntimeGateEngine
#     from apps_rg.integrations.gates.registry import register_apps_rg_gate_pack
#     
#     engine = RuntimeGateEngine()
#     register_apps_rg_gate_pack(engine)
#     
#     # Later in narrative_pass.py:
#     gate_bundle = engine.evaluate(
#         app_id="apps_rg",
#         placement=GatePlacement.POST_ENS,
#         artifact=winner,
#         context=run_context,
#     )
# """
# 
# from apps_rg.integrations.gates.registry import (
#     RESUME_GATE_DEFINITIONS,
#     build_resume_gate_callables,
#     register_apps_rg_gate_pack,
# )
# 
# __all__ = [
#     "RESUME_GATE_DEFINITIONS",
#     "build_resume_gate_callables",
#     "register_apps_rg_gate_pack",
# ]
# 