import logging

logger = logging.getLogger(__name__)
'Shared models and enums for the Agentic Workflow runtime.\n\n\nLOGGER = logging.getLogger(__name__)\nThis file contains all shared data structures that are used across multiple\nmodules to avoid circular imports. This file must not import from any\nruntime.* modules - only from pydantic, enum, and typing.\n'

