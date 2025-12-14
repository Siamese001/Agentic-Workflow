from .utils import MicroStage, HopState, RetryPolicy, MicroCheckpoint, StageTransition, InjectionType, InjectionScope, InjectionPattern, InjectionMatch, InjectionConfig, ValidationResult, ExecutionResult, Config

"""Shared models and enums for the Agentic Workflow runtime.


LOGGER = logging.getLogger(__name__)
This file contains all shared data structures that are used across multiple
modules to avoid circular imports. This file must not import from any
runtime.* modules - only from pydantic, enum, and typing.
"""
from enum import Enum
from pathlib import Path
from services.configuration import ConfigurationService