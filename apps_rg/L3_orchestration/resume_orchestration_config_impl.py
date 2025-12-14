"""Implementation for resume_orchestration_config."""
import logging


logger = logging.getLogger(__name__)
# from .resume_orchestration_config_types import *  # Star import removed

def get_word_count_constraint(k_node: str) -> Optional[WordCountConstraint]:
    """Get word count constraint for a K-node.

    Args:
        k_node: K-node identifier (e.g., "K.1_executive_summary")

    Returns:
        WordCountConstraint or None if not defined
    """
    return GLOBAL_WORD_COUNTS.get(k_node)

def get_char_count_constraint(k_node: str) -> Optional[CharCountConstraint]:
    """Get character count constraint for a K-node.

    Args:
        k_node: K-node identifier (e.g., "K.4_headline")

    Returns:
        CharCountConstraint or None if not defined
    """
    return GLOBAL_CHAR_COUNTS.get(k_node)

def get_reasoning_config(k_node: str) -> Optional[ReasoningConfig]:
    """Get reasoning configuration for a K-node.

    Args:
        k_node: K-node identifier (e.g., "K.1", "K.5")

    Returns:
        ReasoningConfig or None if not defined
    """
    return K_NODE_REASONING_CONFIGS.get(k_node)

def get_validation_gates(execution_point: str) -> List[ValidationGate]:
    """Get validation gates for a specific execution point.

    Args:
        execution_point: Execution point identifier

    Returns:
        List of validation gates
    """
    return [gate for gate in VALIDATION_GATES if gate.execution_point == execution_point]
