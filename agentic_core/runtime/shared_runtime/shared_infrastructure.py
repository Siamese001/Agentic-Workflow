"""
Shared Infrastructure
Provides shared infrastructure services and domain configuration.
"""
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class DomainConfig:
    """Domain-specific configuration."""
    engine_type: str
    settings: Dict[str, Any]
    metadata: Dict[str, Any]


class SharedInfrastructure:
    """Shared infrastructure services."""
    
    def __init__(self):
        """Initialize shared infrastructure."""
        self._configs: Dict[str, DomainConfig] = {}
        logger.debug("SharedInfrastructure initialized")
    
    def create_domain_config(self, engine_type: str) -> DomainConfig:
        """Create domain configuration for engine type."""
        config = DomainConfig(
            engine_type=engine_type,
            settings={},
            metadata={}
        )
        self._configs[engine_type] = config
        logger.debug(f"Domain config created for: {engine_type}")
        return config
    
    def get_domain_config(self, engine_type: str) -> Optional[DomainConfig]:
        """Get domain configuration."""
        return self._configs.get(engine_type)


# Singleton instance
_shared_infrastructure: Optional[SharedInfrastructure] = None


def get_shared_infrastructure() -> SharedInfrastructure:
    """Get shared infrastructure singleton."""
    global _shared_infrastructure
    if _shared_infrastructure is None:
        _shared_infrastructure = SharedInfrastructure()
    return _shared_infrastructure


__all__ = [
    "DomainConfig",
    "SharedInfrastructure",
    "get_shared_infrastructure",
]
