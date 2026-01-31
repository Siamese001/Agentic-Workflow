"""
HOP (Hierarchical Orchestration Process) Engines
"""

from apps_rg.engines.hops.ClerkExtractionEngine import ClerkExtractionEngine
from apps_rg.engines.hops.DataEnrichmentEngine import DataEnrichmentEngine

# Legacy alias for backward compatibility
EnrichmentEngine = DataEnrichmentEngine

__all__ = ["ClerkExtractionEngine", "DataEnrichmentEngine", "EnrichmentEngine"]
