"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/integrations\gates\__init__.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.integrations\gates\__init__ is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/integrations\gates\__init__.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
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