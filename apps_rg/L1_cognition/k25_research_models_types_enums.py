"""Enum types for k25_research_models_types."""

from enum import Enum

class ResearchHopPhase(str, Enum):
    FINANCIAL_STRATEGIC = 'financial_strategic'
    TECHNICAL_PRODUCT = 'technical_product'
    ORGANIZATIONAL_LEADERSHIP = 'organizational_leadership'

class ValidationRejectionReason(str, Enum):
    UNBOUND_METRICS = 'unbound_metrics'
    FLUFF_LANGUAGE = 'fluff_language'
    ORPHANED_CLAIMS = 'orphaned_claims'
    MISSING_CITATIONS = 'missing_citations'
    INSUFFICIENT_DEPTH = 'insufficient_depth'

