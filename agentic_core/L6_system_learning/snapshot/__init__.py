"""Re-export RuntimeADGSnapshot for harness/report import paths (ADR-088).

Report-generation and spine-proof harness only — not architecture evidence
for product-spine *Agent invocation. See ADR-088 and runtime/LAYER.md.
"""

__layer__ = "L6"
__l6_chapter__ = "06.8"

from agentic_core.L6_system_learning.runtime_adg.snapshot import RuntimeADGSnapshot
__all__ = ["RuntimeADGSnapshot"]
