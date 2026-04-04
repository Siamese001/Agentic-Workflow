"""
Evidence Register Types - Domain contracts for evidence tracking.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class EvidenceEntry(BaseModel):
    """Single evidence entry in the register."""
    entry_id: str = Field(..., description="Unique entry ID")
    claim_category: str = Field(..., description="Category of claim (capacity, collateral, etc.)")
    claim_text: str = Field(..., description="Text of the claim")
    evidence_source: str = Field(..., description="Source of evidence")
    evidence_type: str = Field(..., description="Type of evidence")
    extraction_timestamp: str = Field(..., description="When evidence was extracted")
    confidence: float = Field(0.8, ge=0, le=1)
    supporting_excerpt: Optional[str] = Field(None, description="Excerpt from source")
    contradicting_evidence: List[str] = Field(default_factory=list, description="Any contradicting evidence")


class EvidenceRegister(BaseModel):
    """
    Complete evidence register for audit trail.
    """
    request_id: str = Field(..., description="Reference to request")
    entries: List[EvidenceEntry] = Field(default_factory=list, description="Evidence entries")
    completeness_pct: float = Field(0.0, ge=0, le=1, description="Evidence completeness")
    contradiction_count: int = Field(0, ge=0, description="Number of contradictions found")

    def add_entry(self, entry: EvidenceEntry) -> None:
        """Add an evidence entry to the register."""
        self.entries.append(entry)

    def get_by_category(self, category: str) -> List[EvidenceEntry]:
        """Get entries by claim category."""
        return [e for e in self.entries if e.claim_category == category]

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "UW-2024-001234",
                "entries": [],
                "completeness_pct": 0.85,
                "contradiction_count": 0
            }
        }
