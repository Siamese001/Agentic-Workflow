"""Types and models for rg_provenance_tracker."""
import logging



class ProvenanceType(Enum):
    """Type of provenance source."""

class BulletCategory(Enum):
    """Category of bullet point."""

@dataclass
class ProvenanceSource:
    """Source information for provenance tracking."""
    source_type: ProvenanceType
    source_id: str
    source_text: str
    confidence: float = 1.0
    timestamp: Optional[datetime] = None

@dataclass
class BulletProvenance:
    """Provenance information for a bullet point."""
    bullet_id: str
    bullet_text: str
    category: BulletCategory
    sources: List[ProvenanceSource] = field(default_factory=list)
    transformation_log: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProvenanceMap:
    """Map of provenance requirements by company/section."""
    company: str
    pattern: str
    value_count: int = 0
    technical_count: int = 0
    soft_count: int = 0
    achievement_count: int = 0
