"""Thin wrapper for prompt assembly validation.

This wrapper maintains backward compatibility for documentation workflows
by importing the canonical validator from agentic_core.
"""

# Import the canonical validator from the runtime location
from agentic_core.prompt_governance.validation.validate_assembly import validate

# Re-export for backward compatibility
__all__ = ["validate"]

if __name__ == "__main__":
    import sys

    sys.exit(validate())
