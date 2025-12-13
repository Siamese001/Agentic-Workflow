"""Scripts module for Agentic-Workflow.

This module contains various utility scripts for managing the Agentic-Workflow
project, including data access, validation, synthesis, and pipeline operations.

The scripts are organized into logical sub-modules:
- logic: Core logic operations (data access, synthesis, validation)
- cache: Caching utilities and data access caching
- pipeline: Pipeline orchestration and data flow management
- runtime: Runtime script execution and coordination
- utilities: General utility functions and helpers
- validation: Validation and checking utilities
- merge: Code merging and integration scripts
- setup: Project setup and initialization scripts

Each sub-module follows the same organizational pattern with data_access,
synthesis, and validation components where applicable.
"""

# Version information
__version__ = "1.0.0"
__author__ = "Agentic-Workflow Team"

# Export main components
__all__ = [
    "logic",
    "cache",
    "pipeline",
    "runtime",
    "utilities",
    "validation",
    "merge",
    "setup",
]
