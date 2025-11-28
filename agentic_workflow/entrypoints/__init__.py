#!/usr/bin/env python3
"""
Entrypoints module for Resume Generator v10_12
Provides various entry points for different integration scenarios
"""

from typing import Dict, Any, Optional
import logging

from agentic_workflow.runtime import generate_resume_v10_12

logger = logging.getLogger(__name__)

# Export main runtime function
__all__ = ["generate_resume_v10_12"]
