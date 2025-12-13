"""Enum types for k25_research_models_types."""


class ResearchHopPhase(str, Enum):
    """TODO: Add docstring."""

    FINANCIAL_STRATEGIC = 'financial_strategic'
    TECHNICAL_PRODUCT = 'technical_product'
    ORGANIZATIONAL_LEADERSHIP = 'organizational_leadership'

    """TODO: Add docstring."""

class ValidationRejectionReason(str, Enum):
    """TODO: Add docstring."""
    UNBOUND_METRICS = 'unbound_metrics'
    FLUFF_LANGUAGE = 'fluff_language'
    ORPHANED_CLAIMS = 'orphaned_claims'
    MISSING_CITATIONS = 'missing_citations'
    INSUFFICIENT_DEPTH = 'insufficient_depth'
