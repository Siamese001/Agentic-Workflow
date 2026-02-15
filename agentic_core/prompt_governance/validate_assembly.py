"""Shim to canonicalize prompt assembly validation entrypoint.

This shim provides the expected path agentic_core/prompt_governance/validate_assembly.py
while delegating to the real validator at docs/reports/assessments/prompt-modules/validation/validate_assembly.py
"""

import importlib.util
import sys
from pathlib import Path


# Import and delegate to the real validator using importlib
def load_real_validator():
    """Load the real validator module using importlib."""
    REAL_VALIDATOR_PATH = (
        Path(__file__).parents[4]
        / "docs"
        / "reports"
        / "assessments"
        / "prompt-modules"
        / "validation"
        / "validate_assembly.py"
    )

    if not REAL_VALIDATOR_PATH.exists():
        return None

    spec = importlib.util.spec_from_file_location("validate_assembly", REAL_VALIDATOR_PATH)
    if spec is None:
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_assembly"] = module
    spec.loader.exec_module(module)
    return module


# Try to load the real validator
real_validator = load_real_validator()

if real_validator and hasattr(real_validator, "validate"):
    validate = real_validator.validate
else:
    # Fallback if the real validator is not available
    def validate():
        print("Real validator not found at expected location")
        return 1


def main():
    """Entry point for prompt assembly validation."""
    return validate()


if __name__ == "__main__":
    sys.exit(main())
