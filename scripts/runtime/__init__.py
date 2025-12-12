# -*- coding: utf-8 -*-
"""
08_scripts.runtime_ops — Package initialization

This module provides runtime script execution and coordination for the Agentic-Workflow system.
It includes components for:
- Runtime script orchestration and execution
- Dynamic script loading and unloading
- Runtime context management
- Script dependency resolution
- Execution monitoring and telemetry
- Runtime error handling and recovery

The runtime system ensures that scripts are executed efficiently with proper
resource management and error handling.

Auto-generated to satisfy SSoT structure requirements.
"""

from .synthesis import use_tools, use_tools_invoke

__version__ = "1.0.0"
__author__ = "Agentic-Workflow Team"

__all__: list = [
    "use_tools",
    "use_tools_invoke",
]
