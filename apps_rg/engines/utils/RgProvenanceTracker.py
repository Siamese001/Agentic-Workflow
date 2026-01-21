"""
RG Provenance Tracker - Bullet provenance tracking and strategies.

Ported from: archives/legacy_resume_gen/Job Workflow - JSON/Job_Workflow_v61.27.json
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class ProvenanceType(Enum):
    """Type of provenance source."""

    MASTER_RESUME = "MASTER_RESUME"
    JOB_DESCRIPTION = "JOB_DESCRIPTION"
    RAG_RESULT = "RAG_RESULT"
    GENERATED = "GENERATED"
    HYBRID = "HYBRID"


class BulletCategory(Enum):
    """Category of bullet point."""

    VALUE = "V"  # Value-driven bullet
    TECHNICAL = "T"  # Technical bullet
    SOFT = "S"  # Soft skills bullet
    ACHIEVEMENT = "A"  # Achievement bullet


@dataclass
class ProvenanceSource:
    """Source information for provenance tracking."""

    SourceType: ProvenanceType
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
    pattern: str  # e.g., "4V-3T-0S" = 4 Value, 3 Technical, 0 Soft
    value_count: int = 0
    technical_count: int = 0
    soft_count: int = 0
    achievement_count: int = 0


def parse_provenance_pattern(pattern: str) -> Dict[str, int]:
    """
    Parse a provenance pattern string.

    Args:
        pattern: Pattern like "4V-3T-0S"

    Returns:
        Dictionary with category counts
    """
    result = {"V": 0, "T": 0, "S": 0, "A": 0}

    parts = pattern.split("-")
    for part in parts:
        if len(part) >= 2:
            count = int(part[:-1])
            category = part[-1].upper()
            if category in result:
                result[category] = count

    return result


# Default provenance maps by company
DEFAULT_PROVENANCE_MAPS: Dict[str, str] = {
    "Unify Consulting": "4V-3T-0S",
    "IBM": "4V-2T-0S",
    "default": "10V-0A-0S",
}


class ProvenanceTracker:
    """Tracker for bullet provenance throughout the generation pipeline."""

    def __init__(self) -> None:
        """Initialize the provenance tracker."""
        self._bullets: Dict[str, BulletProvenance] = {}
        self._provenance_maps = DEFAULT_PROVENANCE_MAPS.copy()

    def register_bullet(
        self,
        bullet_text: str,
        category: BulletCategory,
        sources: Optional[List[ProvenanceSource]] = None,
        bullet_id: Optional[str] = None,
    ) -> str:
        """
        Register a bullet point with provenance.

        Args:
            bullet_text: The bullet text
            category: Category of the bullet
            sources: List of provenance sources
            bullet_id: Optional ID (generated if None)

        Returns:
            Bullet ID
        """
        if bullet_id is None:
            bullet_id = self._generate_bullet_id(bullet_text)

        provenance = BulletProvenance(
            bullet_id=bullet_id,
            bullet_text=bullet_text,
            category=category,
            sources=sources or [],
        )

        # Calculate confidence based on sources
        if provenance.sources:
            provenance.confidence_score = sum(
                s.confidence for s in provenance.sources
            ) / len(provenance.sources)

        self._bullets[bullet_id] = provenance
        return bullet_id

    def add_source(
        self,
        bullet_id: str,
        source: ProvenanceSource,
    ) -> bool:
        """Add a source to an existing bullet."""
        if bullet_id not in self._bullets:
            return False

        self._bullets[bullet_id].sources.append(source)

        # Recalculate confidence
        sources = self._bullets[bullet_id].sources
        self._bullets[bullet_id].confidence_score = sum(
            s.confidence for s in sources
        ) / len(sources)

        return True

    def log_transformation(
        self,
        bullet_id: str,
        transformation: str,
    ) -> bool:
        """Log a transformation applied to a bullet."""
        if bullet_id not in self._bullets:
            return False

        self._bullets[bullet_id].transformation_log.append(
            f"{datetime.now().isoformat()}: {transformation}"
        )
        return True

    def get_bullet(self, bullet_id: str) -> Optional[BulletProvenance]:
        """Get provenance for a bullet."""
        return self._bullets.get(bullet_id)

    def get_all_bullets(self) -> List[BulletProvenance]:
        """Get all tracked bullets."""
        return list(self._bullets.values())

    def get_bullets_by_category(
        self, category: BulletCategory
    ) -> List[BulletProvenance]:
        """Get bullets by category."""
        return [b for b in self._bullets.values() if b.category == category]

    def get_provenance_map(self, company: str) -> str:
        """Get provenance map pattern for a company."""
        return self._provenance_maps.get(
            company, self._provenance_maps.get("default", "10V-0A-0S")
        )

    def set_provenance_map(self, company: str, pattern: str) -> None:
        """Set provenance map for a company."""
        self._provenance_maps[company] = pattern

    def validate_provenance_requirements(
        self,
        company: str,
    ) -> Dict[str, object]:
        """
        Validate that bullets meet provenance requirements.

        Args:
            company: Company name to check requirements for

        Returns:
            Validation result dictionary
        """
        pattern = self.get_provenance_map(company)
        requirements = parse_provenance_pattern(pattern)

        # Count bullets by category
        counts = {"V": 0, "T": 0, "S": 0, "A": 0}
        for bullet in self._bullets.values():
            category_key = bullet.category.value
            if category_key in counts:
                counts[category_key] += 1

        # Check requirements
        violations = []
        for category, required in requirements.items():
            actual = counts.get(category, 0)
            if actual < required:
                violations.append(
                    f"Category {category}: need {required}, have {actual}"
                )

        return {
            "is_valid": len(violations) == 0,
            "pattern": pattern,
            "requirements": requirements,
            "actual_counts": counts,
            "violations": violations,
        }

    def get_low_confidence_bullets(
        self, threshold: float = 0.7
    ) -> List[BulletProvenance]:
        """Get bullets with confidence below threshold."""
        return [
            b for b in self._bullets.values() if b.confidence_score < threshold
        ]

    def get_ungrounded_bullets(self) -> List[BulletProvenance]:
        """Get bullets without any provenance sources."""
        return [b for b in self._bullets.values() if not b.sources]

    def export_provenance_report(self) -> Dict[str, object]:
        """Export a complete provenance report."""
        return {
            "total_bullets": len(self._bullets),
            "by_category": {
                cat.value: len(self.get_bullets_by_category(cat))
                for cat in BulletCategory
            },
            "low_confidence_count": len(self.get_low_confidence_bullets()),
            "ungrounded_count": len(self.get_ungrounded_bullets()),
            "bullets": [
                {
                    "id": b.bullet_id,
                    "text": b.bullet_text[:100] + "..." if len(b.bullet_text) > 100 else b.bullet_text,
                    "category": b.category.value,
                    "confidence": b.confidence_score,
                    "source_count": len(b.sources),
                    "transformations": len(b.transformation_log),
                }
                for b in self._bullets.values()
            ],
        }

    def _generate_bullet_id(self, text: str) -> str:
        """Generate a unique ID for a bullet."""
        hash_input = f"{text}_{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


class BulletSelector:
    """Selector for choosing bullets based on JD fit and provenance."""

    def __init__(
        self,
        tracker: ProvenanceTracker,
    ) -> None:
        """Initialize the selector."""
        self.tracker = tracker

    def score_bullet(
        self,
        bullet: BulletProvenance,
        jd_keywords: List[str],
    ) -> float:
        """
        Score a bullet based on JD fit.

        Uses: (JD Keyword Overlap * 0.5) + (Metric Impact * 0.3) + (Uniqueness * 0.2)
        """
        # JD keyword overlap
        bullet_words = set(bullet.bullet_text.lower().split())
        jd_words = set(kw.lower() for kw in jd_keywords)
        overlap = len(bullet_words & jd_words) / max(len(jd_words), 1)
        jd_score = overlap * 0.5

        # Metric impact (check for numbers/percentages)
        import scripts.validation.check_canonical_structure
        metrics = re.findall(r"\d+%|\$\d+|\d+x|\d+\+", bullet.bullet_text)
        metric_score = min(len(metrics) * 0.1, 0.3)

        # Uniqueness (based on confidence and source diversity)
        uniqueness_score = bullet.confidence_score * 0.2

        return jd_score + metric_score + uniqueness_score

    def select_bullets(
        self,
        company: str,
        jd_keywords: List[str],
    ) -> List[BulletProvenance]:
        """
        Select bullets for a company based on requirements and JD fit.

        Args:
            company: Company name
            jd_keywords: Keywords from job description

        Returns:
            Selected bullets in priority order
        """
        pattern = self.tracker.get_provenance_map(company)
        requirements = parse_provenance_pattern(pattern)

        # Score all bullets
        scored_bullets: List[tuple[BulletProvenance, float]] = []
        for bullet in self.tracker.get_all_bullets():
            score = self.score_bullet(bullet, jd_keywords)
            scored_bullets.append((bullet, score))

        # Sort by score
        scored_bullets.sort(key=lambda x: x[1], reverse=True)

        # Select bullets to meet requirements
        selected: List[BulletProvenance] = []
        category_counts = {"V": 0, "T": 0, "S": 0, "A": 0}

        for bullet, score in scored_bullets:
            cat = bullet.category.value
            if category_counts.get(cat, 0) < requirements.get(cat, 0):
                selected.append(bullet)
                category_counts[cat] = category_counts.get(cat, 0) + 1

        return selected


def create_provenance_tracker() -> ProvenanceTracker:
    """Create a provenance tracker instance."""
    return ProvenanceTracker()


def create_bullet_selector(
    tracker: Optional[ProvenanceTracker] = None,
) -> BulletSelector:
    """Create a bullet selector instance."""
    if tracker is None:
        tracker = ProvenanceTracker()
    return BulletSelector(tracker)


def create_provenance_source(
    SourceType: ProvenanceType,
    source_text: str,
    source_id: Optional[str] = None,
    confidence: float = 1.0,
) -> ProvenanceSource:
    """Create a provenance source instance."""
    if source_id is None:
        source_id = hashlib.md5(source_text.encode()).hexdigest()[:8]

    return ProvenanceSource(
        SourceType=SourceType,
        source_id=source_id,
        source_text=source_text,
        confidence=confidence,
        timestamp=datetime.now(),
    )
