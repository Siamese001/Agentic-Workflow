"""HOP Pipeline Stage Registry — DEPRECATED 2026-05-01.

This registry's stage handlers are one-line stubs (returning
``{"status": "processed"}``); the real domain logic was lost in the
2026-02-08 consolidation and never re-added here. As of plan
.windsurf/plans/apps-hop-substrate-f7751b.md (Wave 2) the canonical
apps_lic pipeline lives in:

- ``apps_lic.config.hop_pipeline.REGISTRY`` — topology
- ``apps_lic/engines/<stage>_engine.py`` — per-stage domain logic
- ``apps_lic.reasoning.LicCampaignOrchestrator`` — thin runner
- ``apps_shared.orchestration.HopPipelineExecutor`` — shared substrate

This module is retained only as a deprecation shim for existing tests
(``tests/unit/apps_lic/reasoning/test_hop_pipeline_executor.py``).
New callers MUST use the canonical path above.
"""

from __future__ import annotations

import warnings
from typing import Any, Callable

warnings.warn(
    "apps_lic.engines.hop_stage_registry is deprecated since 2026-05-01. "
    "Use apps_lic.config.hop_pipeline.REGISTRY + "
    "apps_lic.reasoning.LicCampaignOrchestrator.",
    DeprecationWarning,
    stacklevel=2,
)

_REGISTRY: dict[int, Callable] = {}


def register_stage(stage_id: int):
    """Decorator to register a stage handler."""

    def decorator(func: Callable) -> Callable:
        _REGISTRY[stage_id] = func
        return func

    return decorator


def get_stage_handler(stage_id: int) -> Callable | None:
    """Look up the handler for a given stage_id."""
    return _REGISTRY.get(stage_id)


@register_stage(1)
def _stage_1_profile_analysis(executor: Any, context: dict, **kwargs) -> dict:
    """HOP1: Profile analysis stage."""
    return {"stage": 1, "name": "profile_analysis", "status": "processed", "context": context}


@register_stage(2)
def _stage_2_research(executor: Any, context: dict, **kwargs) -> dict:
    """HOP2: Research stage."""
    return {"stage": 2, "name": "research", "status": "processed", "context": context}


@register_stage(3)
def _stage_3_sender_grounding(executor: Any, context: dict, **kwargs) -> dict:
    """HOP3: Sender grounding stage."""
    return {"stage": 3, "name": "sender_grounding", "status": "processed", "context": context}


@register_stage(4)
def _stage_4_routing(executor: Any, context: dict, **kwargs) -> dict:
    """HOP4: Routing stage."""
    return {"stage": 4, "name": "routing", "status": "processed", "context": context}


@register_stage(5)
def _stage_5_generation(executor: Any, context: dict, **kwargs) -> dict:
    """HOP5: Generation stage."""
    return {"stage": 5, "name": "generation", "status": "processed", "context": context}


@register_stage(6)
def _stage_6_validation(executor: Any, context: dict, **kwargs) -> dict:
    """HOP6: Validation stage."""
    return {"stage": 6, "name": "validation", "status": "processed", "context": context}


@register_stage(7)
def _stage_7_gate_decision(executor: Any, context: dict, **kwargs) -> dict:
    """HOP7: Gate decision stage."""
    return {"stage": 7, "name": "gate_decision", "status": "processed", "context": context}


@register_stage(8)
def _stage_8_qa_report(executor: Any, context: dict, **kwargs) -> dict:
    """HOP8: QA report stage."""
    return {"stage": 8, "name": "qa_report", "status": "processed", "context": context}


@register_stage(9)
def _stage_9_integration(executor: Any, context: dict, **kwargs) -> dict:
    """HOP9: Integration stage."""
    return {"stage": 9, "name": "integration", "status": "processed", "context": context}


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_lic.engines.hop_stage_registry', "module_loaded")
