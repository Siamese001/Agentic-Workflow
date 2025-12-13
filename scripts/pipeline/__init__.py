# -*- coding: utf-8 -*-
"""
08_scripts.pipeline_ops — Package initialization

This module provides pipeline orchestration and data flow management for the Agentic-Workflow system.
It includes components for:
- Pipeline definition and execution
- Data flow coordination between stages
- Pipeline state management and persistence
- Stage-wise error handling and recovery
- Pipeline performance monitoring
- Dynamic pipeline reconfiguration

The pipeline system enables complex data processing workflows to be
executed reliably with proper stage coordination and error handling.

Auto-generated to satisfy SSoT structure requirements.
"""


__version__ = "1.0.0"
__author__ = "Agentic-Workflow Team"

__all__: list = [
    "get_info",
    "get_info_request",
    "use_tools",
]
