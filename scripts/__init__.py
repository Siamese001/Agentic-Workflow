"""

logger = logging.getLogger(__name__)
Agentic-Workflow Root Package
=============================

This is the root package for the Agentic Workflow system, providing a unified
architecture for agentic AI operations with the following taxonomy:

    01_agentic_core/    - Core agent implementations (L1-L5 layers)
    02_schemas/         - Schema definitions and validation
    03_runtime/         - Runtime services and shared utilities
    04_prompt_governance/ - Prompt templates and governance
    05_config/          - Configuration files (YAML/JSON only)
    06_data/            - Data storage, archives, and semantic cache
    07_observability/   - Logging, metrics, and tracing
    08_scripts/         - function scripts and tools
    09_apps/            - Application implementations (LIC, RG)
    10_tests/           - Test suites

Auto-hardened by WINDSURF v7 — Production-ready, type-safe, zero-loss.
"""
import logging


__version__ = "7.0.0"
__author__ = "Agentic Workflow Team"

# Lazy imports to avoid circular dependencies
# Users should import from subpackages directly:
#   from agentic_workflow.runtime.shared import CONFIG, ValidationError
#   from agentic_workflow.agentic_core import PIISanitizerAgent

__all__ = [
    "__version__",
    "__author__",
]
