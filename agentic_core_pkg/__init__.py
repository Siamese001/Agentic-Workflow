"""
Agentic Core L5 Importable Package Interface

This package provides importable access to the L5 agentic architecture
while maintaining the original hyphenated directory structure for
YAML compliance.

Usage:
    from agentic_core_pkg.plan_layer.plan_phase.get_core_info.general.understand_request.build_core_query import BuildCoreQuery
    from agentic_core_pkg.exec_layer.act_phase.use_core_tools.general.use_a_tool import ExecuteCoreExecution
    from agentic_core_pkg.safe_layer.safety_phase.check_core_rules.policy.check_safety import ApplySafetyPolicy
"""

# Version and metadata
__version__ = "1.0.0"
__description__ = "L5 Agentic Architecture Importable Package"
__author__ = "Agentic Core Reconstruction Team"

# Convenience imports for common components
try:
    from .plan_layer.plan_phase.get_core_info.general.understand_request.build_core_query import BuildCoreQuery
    from .orc_layer.plan_phase.get_core_info.general.understand_request.orchestrate_core_planning import OrchestrateCorePlanning
    from .exec_layer.act_phase.use_core_tools.general.use_a_tool import ExecuteCoreExecution
    from .mem_layer.retrieve_phase.get_core_info.general.understand_request.retrieve_core_memory import RetrieveCoreMemory
    from .safe_layer.safety_phase.check_core_rules.policy.check_safety import ApplySafetyPolicy
    
    __all__ = [
        "BuildCoreQuery",
        "OrchestrateCorePlanning", 
        "ExecuteCoreExecution",
        "RetrieveCoreMemory",
        "ApplySafetyPolicy"
    ]
except ImportError as e:
    print(f"Warning: Could not import convenience components: {e}")
    __all__ = []
