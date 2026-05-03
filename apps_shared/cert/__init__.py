"""apps_shared.cert — shared certification-path utilities for apps_*.

Current surface:
- :func:`maybe_invoke_exit_eval` — W2.P3 opt-in hook invoked by
  per-app cert entrypoints (e.g. ``apps_qna/__main__.py``) to run the
  v6 Exit pipeline against a SINGLE_STEP-sealed artifact. Gated by
  ``invoke_exit_eval: true`` in the route's ``cert_route_registry.yaml``.
"""

from apps_shared.cert.exit_eval_hook import (
    maybe_invoke_exit_eval,
    should_invoke_exit_eval,
)
from apps_shared.cert.rubric_output_mapper import map_l2_receipt_to_dim_scores

__all__ = [
    "maybe_invoke_exit_eval",
    "should_invoke_exit_eval",
    "map_l2_receipt_to_dim_scores",
]
