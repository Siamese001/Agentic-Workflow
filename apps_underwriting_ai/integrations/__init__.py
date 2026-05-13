"""apps_underwriting_ai integrations.

Active integration adapters consumed by the agentic_core dispatch chain.

REMOVED (plan apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W1):
  - ExecutionAdapter / ExecutionRequest — parallel bypass path, deleted
  - governed_underwriting_run — parallel bypass path, deleted
  - UnderwritingIngressRunner — file-based ingress into parallel path, deleted
  - SpineHandoff — stale envelope for wrong route, deleted
  - underwriting_capability_registry — app-side registry duplication, deleted
"""

from apps_underwriting_ai.integrations.observability_adapter import (
    ObservabilityAdapter,
)

__all__ = [
    "ObservabilityAdapter",
]
