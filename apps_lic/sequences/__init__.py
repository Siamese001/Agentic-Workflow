"""apps_lic.sequences — Multi-Touch Sequence Management

W2: P3 Multi-Touch Sequences

This package provides:
- Sequence definitions (3-touch standard, executive, recruiter)
- Touch-to-touch context propagation
- State machine integration
"""

from apps_lic.sequences.touch_sequence_definitions import (
    SequenceType,
    TouchStrategy,
    TouchDefinition,
    SequenceDefinition,
    STANDARD_3_TOUCH,
    EXECUTIVE_3_TOUCH,
    RECRUITER_COMPACT,
    get_sequence_definition,
    get_touch_definition,
    list_sequence_types,
    calculate_touch_wake_time,
)

from apps_lic.sequences.touch_propagation import (
    TouchContext,
    PropagationResult,
    TouchContextPropagator,
    create_touch_context_from_result,
)

__all__ = [
    # Definitions
    "SequenceType",
    "TouchStrategy",
    "TouchDefinition",
    "SequenceDefinition",
    "STANDARD_3_TOUCH",
    "EXECUTIVE_3_TOUCH",
    "RECRUITER_COMPACT",
    "get_sequence_definition",
    "get_touch_definition",
    "list_sequence_types",
    "calculate_touch_wake_time",
    # Propagation
    "TouchContext",
    "PropagationResult",
    "TouchContextPropagator",
    "create_touch_context_from_result",
]
