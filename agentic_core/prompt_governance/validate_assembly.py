"""Canonical prompt assembly validation entrypoint.

This module provides the expected entrypoint for prompt assembly validation
with the real validation logic located in the validation subpackage.
"""

from .validation.validate_assembly import validate

__all__ = ["validate"]


def main() -> int:
    """Entry point for prompt assembly validation."""
    return validate()


if __name__ == "__main__":
    import sys

    sys.exit(main())
