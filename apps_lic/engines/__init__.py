"""apps_lic/engines/__init__.py — Sovereign Engine Registry.

Only canonical executors are eagerly imported. All other agents remain
importable directly from their modules, e.g.:
    from apps_lic.engines.DeliverabilityAgent import DeliverabilityAgent
    from apps_lic.engines.OutreachSignalRouterAgent import OutreachSignalRouterAgent
"""

try:
    from apps_lic.reasoning.ExecutiveStrategyAgent import (
        ExecutiveStrategyAgent,
        get_exec_interviewer_profile,
        get_exec_shadow_audit,
        get_exec_strategy_roadmap,
    )
    # guardian: allow-silent-swallow - optional dependency
except ImportError:
    ExecutiveStrategyAgent = None  # type: ignore[assignment,misc]
    get_exec_interviewer_profile = None  # type: ignore[assignment]
    get_exec_shadow_audit = None  # type: ignore[assignment]
    get_exec_strategy_roadmap = None  # type: ignore[assignment]

try:
    from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor
except ImportError:
    HOPPipelineExecutor = None  # type: ignore[assignment,misc]

try:
    from apps_lic.reasoning.LICValidationExecutor import LICValidationExecutor
except ImportError:
    LICValidationExecutor = None  # type: ignore[assignment,misc]

try:
    from apps_lic.reasoning.OutreachMessageAgent import OutreachMessageAgent
except ImportError:
    OutreachMessageAgent = None  # type: ignore[assignment,misc]

# Add control_plane export
from apps_lic.engines.control_plane import ControlPlane, PolicyAction

__all__ = [
    "ExecutiveStrategyAgent",
    "get_exec_shadow_audit",
    "get_exec_strategy_roadmap",
    "get_exec_interviewer_profile",
    "HOPPipelineExecutor",
    "LICValidationExecutor",
    "OutreachMessageAgent",
    "ControlPlane",
    "PolicyAction",
]
