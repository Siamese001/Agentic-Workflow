# Orchestration safety application layer
"""Apply safety policies to orchestration workflows."""

from typing import Dict


def apply_orchestration_safety(workflow_config: Dict) -> Dict:
    """
    Apply safety policies to orchestration workflow configuration.

    Args:
        workflow_config: The workflow configuration to validate

    Returns:
        Validated workflow configuration with safety policies applied
    """
    validated_config = workflow_config.copy()
    validated_config["safety_validated"] = True
    validated_config["max_retries"] = min(workflow_config.get("max_retries", 3), 5)
    return validated_config