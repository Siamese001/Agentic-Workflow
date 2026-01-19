from __future__ import annotations
"""
apps_rg.domain - Resume Generation domain models and configurations.

Contains app-specific domain logic moved from agentic_core for separation of concerns:
- Creative Brief: RG creative brief models and enums
- Validation Gates: Domain validation rules
"""

# Import modules (avoid wildcard imports due to shim files)
from . import rg_creative_brief
from . import rg_creative_brief_enums
from . import rg_creative_brief_models
from . import rg_validation_gates
from . import rg_validation_gates_types
