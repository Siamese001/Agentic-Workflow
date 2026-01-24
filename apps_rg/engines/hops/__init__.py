"""
HOP (Hierarchical Orchestration Process) Engines
"""

from apps_rg.engines.hops.hop1_clerk_engine import ClerkExtractionEngine
from apps_rg.engines.hops.hop2_enrichment_engine import DataEnrichmentEngine

# Legacy alias for backward compatibility
EnrichmentEngine = DataEnrichmentEngine

__all__ = ["ClerkExtractionEngine", "DataEnrichmentEngine", "EnrichmentEngine"]
