"""Golden dataset evaluation package.

Complete golden dataset wiring for agentic architecture:
- GoldenDatasetEvaluator: Load and evaluate against immutable golden datasets
- GoldenEvalIntegration: Wire evaluator into Eval Spine (shadow mode)
- GoldenL6Emitter: Emit golden eval metrics to L6 observability
"""

from agentic_core.evaluation.golden.eval_spine_integration import (
    GoldenEvalIntegration,
    attach_golden_eval,
)
from agentic_core.evaluation.golden.golden_evaluator import (
    GoldenDatasetEvaluator,
    GoldenDatasetSummary,
    GoldenEvalResult,
    get_evaluator,
)
from agentic_core.evaluation.golden.l6_emitter import (
    GoldenL6Emitter,
    emit_golden_batch,
    emit_golden_result,
    get_l6_emitter,
)

__all__ = [
    # Core evaluator
    "GoldenDatasetEvaluator",
    "GoldenDatasetSummary",
    "GoldenEvalResult",
    "get_evaluator",
    # Eval Spine integration
    "GoldenEvalIntegration",
    "attach_golden_eval",
    # L6 emission
    "GoldenL6Emitter",
    "emit_golden_batch",
    "emit_golden_result",
    "get_l6_emitter",
]
