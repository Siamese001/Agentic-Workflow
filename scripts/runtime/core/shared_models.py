
"""Shared models and enums for the Agentic Workflow runtime.


LOGGER = logging.getLogger(__name__)
This file contains all shared data structures that are used across multiple
modules to avoid circular imports. This file must not import from any
runtime.* modules - only from pydantic, enum, and typing.
"""
