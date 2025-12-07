"""
03_runtime/compat/utils_RES_v2.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: ef2cf649c7e8bd1e01c1320e03fdaa5d00218dd050161ba9d649ce6ce5a1357b
"""


from __future__ import annotations

import warnings

# Emit deprecation warning on import
warnings.warn(
    "utils_RES_v2 is deprecated. Use 'from agentic_workflow.runtime.shared import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all utils from the canonical location
from ..shared.utils import (
    # Classes
    TextUtils,
    text_utils,
    DuplicateDetector,
    TelemetryLogger,
    WorkflowLogFilter,
    # Functions
    setup_workflow_logging,
    create_directory_if_missing,
    sanitize_filename,
    calculate_signal_score,
    reasoning_config_to_api_params,
    enhance_system_prompt_with_reasoning,
    build_generation_prompt_with_reinforced_constraints,
)

# Re-export config items that were historically accessed via utils
from ..shared.config import (
    CACHE_DIR,
    DATA_DIR,
    PROMPT_ADDENDUM_CONFIG,
)

# Re-export models that were historically accessed via utils
from ..shared.models import (
    ThematicAnalysis,
    ValidationResult,
    ValidationSeverity,
    ReasoningConfig,
)

__all__ = [
    # Classes
    "TextUtils",
    "text_utils",
    "DuplicateDetector",
    "TelemetryLogger",
    "WorkflowLogFilter",
    # Functions
    "setup_workflow_logging",
    "create_directory_if_missing",
    "sanitize_filename",
    "calculate_signal_score",
    "reasoning_config_to_api_params",
    "enhance_system_prompt_with_reasoning",
    "build_generation_prompt_with_reinforced_constraints",
    # Config
    "CACHE_DIR",
    "DATA_DIR",
    "PROMPT_ADDENDUM_CONFIG",
    # Models
    "ThematicAnalysis",
    "ValidationResult",
    "ValidationSeverity",
    "ReasoningConfig",
]
