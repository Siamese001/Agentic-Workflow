"""
Integration configuration for domain applications.

Provides domain-specific configuration for apps_rg and apps_lic integration
with the feature-flagged agent system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class IntegrationConfig:
    """Configuration for domain integration."""

    domain: str
    domain_prefix: str
    similarity_threshold: float
    ttl_seconds: int
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    required_flags: List[str] = field(default_factory=list)
    optional_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain": self.domain,
            "domain_prefix": self.domain_prefix,
            "similarity_threshold": self.similarity_threshold,
            "ttl_seconds": self.ttl_seconds,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window_seconds": self.rate_limit_window_seconds,
            "required_flags": self.required_flags,
            "optional_flags": self.optional_flags,
        }


# Predefined configurations
RG_CONFIG = IntegrationConfig(
    domain="rg",
    domain_prefix="apps_rg",
    similarity_threshold=0.85,
    ttl_seconds=3600,
    rate_limit_requests=100,
    rate_limit_window_seconds=60,
    required_flags=[
        "ENABLE_VERIFICATION_GATE",
        "ENABLE_AUDIT_TRAIL",
    ],
    optional_flags=[
        "ENABLE_META_LEARNING",
        "ENABLE_HITL_WORKFLOW",
    ],
)

LIC_CONFIG = IntegrationConfig(
    domain="lic",
    domain_prefix="apps_lic",
    similarity_threshold=0.92,  # Stricter for LIC
    ttl_seconds=7200,  # 2 hours
    rate_limit_requests=50,  # More conservative
    rate_limit_window_seconds=60,
    required_flags=[
        "ENABLE_VERIFICATION_GATE",
        "ENABLE_AUDIT_TRAIL",
        "ENABLE_HITL_WORKFLOW",  # Required for LIC compliance
    ],
    optional_flags=[
        "ENABLE_META_LEARNING",
    ],
)


def get_domain_config(domain: str) -> IntegrationConfig:
    """Get configuration for a domain.

    Args:
        domain: Domain name ('rg' or 'lic')

    Returns:
        IntegrationConfig for the domain

    Raises:
        ValueError: If domain is not recognized
    """
    configs = {
        "rg": RG_CONFIG,
        "lic": LIC_CONFIG,
        "apps_rg": RG_CONFIG,
        "apps_lic": LIC_CONFIG,
    }

    if domain not in configs:
        raise ValueError(f"Unknown domain: {domain}. Expected 'rg' or 'lic'")

    return configs[domain]
