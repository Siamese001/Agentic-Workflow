"""W12 — Cross-App Research Substrate Ingest (C0)

Ingests research substrate from apps_research into C0 context.
Ensures data boundary EVIDENCE_DATA_ONLY is preserved.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from agentic_core.runtime.delegation import (
    SubstrateReturnPacket,
    ReuseEligibility,
)


@dataclass(frozen=True)
class IngestedResearchSubstrate:
    """Research substrate ingested into C0 context."""
    substrate_id: str
    source_delegation_id: str
    source_app_id: str  # apps_research
    
    # Ingested data (evidence only)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    claims: List[Dict[str, Any]] = field(default_factory=list)
    
    # Data boundary
    data_boundary_label: str = "EVIDENCE_DATA_ONLY"
    
    # Provenance
    provenance_chain: List[Dict[str, Any]] = field(default_factory=list)
    freshness_ttl_hours: int = 168
    
    # Evidence digest
    evidence_digest: str = ""
    
    def is_evidence_only(self) -> bool:
        """Verify substrate is evidence data only."""
        return self.data_boundary_label == "EVIDENCE_DATA_ONLY"


class CrossAppResearchSubstrateIngest:
    """Ingests cross-app research substrate into C0.
    
    Core owns ingest logic. Apps provide ingest policy config.
    """
    
    def __init__(self, ingest_policy: Dict[str, Any] = None):
        """Initialize with ingest policy."""
        self._policy = ingest_policy or {}
    
    def ingest_substrate_packet(
        self,
        packet: SubstrateReturnPacket,
        consuming_app_id: str
    ) -> Optional[IngestedResearchSubstrate]:
        """Ingest substrate return packet into C0.
        
        Args:
            packet: Substrate return packet from apps_research
            consuming_app_id: App consuming the substrate (apps_rg/apps_lic)
            
        Returns:
            IngestedResearchSubstrate or None if ingest blocked
        """
        # Verify packet is evidence data only
        if not packet.is_evidence_only():
            raise IngestBlockedError(
                f"Packet {packet.packet_id} is not EVIDENCE_DATA_ONLY. "
                "Cross-app substrate must be evidence data only."
            )
        
        # Verify caller_app_id matches consuming app
        if packet.caller_app_id != consuming_app_id:
            raise IngestBlockedError(
                f"Packet caller_app_id {packet.caller_app_id} does not match "
                f"consuming app {consuming_app_id}"
            )
        
        # Verify reuse eligibility
        if not packet.is_reusable():
            raise IngestBlockedError(
                f"Packet {packet.packet_id} not eligible for reuse: "
                f"{packet.reuse_block_reasons}"
            )
        
        # Create ingested substrate
        ingested = IngestedResearchSubstrate(
            substrate_id=packet.packet_id,
            source_delegation_id=packet.delegation_id,
            source_app_id=packet.target_app_id,
            entities=packet.entity_aliases,
            sources=packet.source_register,
            claims=packet.claim_evidence_map,
            data_boundary_label=packet.data_boundary_label,
            provenance_chain=[packet.substrate_provenance],
            freshness_ttl_hours=packet.freshness_ttl_hours,
            evidence_digest=packet.evidence_digest,
        )
        
        return ingested
    
    def validate_for_consumption(
        self,
        ingested: IngestedResearchSubstrate,
        consuming_app_id: str
    ) -> bool:
        """Validate ingested substrate is suitable for app consumption.
        
        Args:
            ingested: Ingested research substrate
            consuming_app_id: App consuming the substrate
            
        Returns:
            True if valid for consumption
        """
        # Verify data boundary
        if not ingested.is_evidence_only():
            return False
        
        # Verify source
        if ingested.source_app_id != "apps_research":
            return False
        
        # Verify freshness
        if ingested.freshness_ttl_hours <= 0:
            return False
        
        return True


class IngestBlockedError(Exception):
    """Raised when substrate ingest is blocked."""
    pass


# Global ingest instance
default_ingest = CrossAppResearchSubstrateIngest()
