"""
ADG Retrieval Wiring Accelerator

Validates that all 5 retrieval layers (L1-L5) from Agentic Retrieval Models v18
are wired across agentic_core (L0-L6) and all apps_* packages.

Usage:
    python -m tools.adg.accelerators.retrieval
    python tools/adg/accelerators/retrieval/adg_retrieval_accelerator.py
"""

__version__ = "1.0.0"
__author__ = "Agentic Workflow Team"

from .adg_retrieval_accelerator import (
    RetrievalAccelerator,
    main,
    run_validation,
)

__all__ = [
    "RetrievalAccelerator",
    "run_validation",
    "main",
    "__version__",
]
