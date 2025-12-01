"""
L5 Agentic Core - Plan Layer - Get Core Info Phase
Implements L1 Cognitive Planning with full L5 safety compliance
"""

from .get_core_info_coordinator import (
    PhaseStep,
    PhaseStatus,
    PhaseContext,
    PhaseResult,
    GetCoreInfoCoordinator,
    create_get_core_info_coordinator
)

# Import prepare-information utilities
from .utility.prepare_information.prepare_information_coordinator import (
    # Prepare information coordinator
    WorkflowStep,
    WorkflowStatus,
    WorkflowContext,
    WorkflowResult,
    PrepareInformationCoordinator,
    create_prepare_information_coordinator
)

# Version and metadata
__version__ = "1.0.0"
__description__ = "L5 Agentic Core - Get Core Info Phase"
__author__ = "L5 Agentic Core Team"

# Export main classes and factory functions
__all__ = [
    # Phase coordination
    "PhaseStep",
    "PhaseStatus",
    "PhaseContext",
    "PhaseResult",
    "GetCoreInfoCoordinator",
    "create_get_core_info_coordinator",
    
    # Prepare information coordination
    "WorkflowStep",
    "WorkflowStatus",
    "WorkflowContext",
    "WorkflowResult",
    "PrepareInformationCoordinator",
    "create_prepare_information_coordinator"
]
