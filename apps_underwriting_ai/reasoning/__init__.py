"""apps_underwriting_ai reasoning surface.

UnderwritingHopOrchestrator drives the 5-stage pipeline declaratively via
the shared HopPipelineExecutor. UnderwritingEngine (under engines/) is the
imperative alternative.
"""

from apps_underwriting_ai.reasoning.UnderwritingHopOrchestrator import (
    UnderwritingHopOrchestrator,
)

__all__ = ["UnderwritingHopOrchestrator"]
