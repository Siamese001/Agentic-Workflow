from __future__ import annotations
"""
apps_lic.domain - LinkedIn/Outreach domain models and configurations.

Contains app-specific domain logic moved from agentic_core for separation of concerns:
- Archetypes: LIC persona archetypes
- CTA Patterns: Call-to-action templates
- Routing Rules: Message routing logic
- Validator Rules: Domain validation
- Vector Memory: LIC-specific memory configs
"""

# Import modules (avoid wildcard imports due to shim files)
from . import lic_archetypes
from . import lic_archetypes_enums
from . import lic_archetypes_models
from . import lic_cta_patterns
from . import lic_cta_patterns_enums
from . import lic_cta_patterns_models
from . import lic_routing_rules
from . import lic_routing_rules_enums
from . import lic_routing_rules_models
from . import lic_validator_rules
from . import lic_validator_rules_types
from . import lic_vector_memory
from . import lic_vector_memory_types
