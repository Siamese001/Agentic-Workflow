"""Triplet extraction executor for knowledge graph construction."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Triplet:
    """Knowledge graph triplet (subject, predicate, object)."""
    subject: str
    predicate: str
    object: str
    confidence: float = 0.8
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ExtractionConfig:
    """Configuration for triplet extraction operations."""
    model_name: str = "default"
    confidence_threshold: float = 0.5
    max_triplets: int = 50
    include_metadata: bool = True
    timeout_seconds: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExtractionResult:
    """Result from triplet extraction operations."""
    text: str = ""
    triplets: List[Triplet] = field(default_factory=list)
    processing_time: float = 0.0
    confidence_score: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class TripletExtractionExecutor:
    """Triplet extraction execution engine for knowledge graph construction."""

    def __init__(self, config: Optional[ExtractionConfig] = None):
        """Initialize with extraction configuration."""
        self.config = config or ExtractionConfig()
        self.model_name = self.config.model_name
        self.confidence_threshold = self.config.confidence_threshold

    def extract_triplets(self, text: str, context: Dict[str, Any] = None) -> ExtractionResult:
        """Extract knowledge graph triplets from text."""
        # Mock implementation - in real system would use NLP model
        mock_triplets = self._generate_mock_triplets(text, context)

        # Filter by confidence threshold
        filtered_triplets = [
            t for t in mock_triplets
            if t.confidence >= self.confidence_threshold
        ]

        # Limit to max triplets
        limited_triplets = filtered_triplets[:self.config.max_triplets]

        return ExtractionResult(
            text=text,
            triplets=limited_triplets,
            processing_time=0.5,
            confidence_score=sum(t.confidence for t in limited_triplets) / len(limited_triplets) if limited_triplets else 0.0,
            metadata={
                "model": self.model_name,
                "original_count": len(mock_triplets),
                "filtered_count": len(filtered_triplets),
                "context": context or {}
            }
        )

    def extract_from_company_profile(self, company_name: str, description: str) -> ExtractionResult:
        """Extract triplets specifically from company profiles."""
        text = f"{company_name}: {description}"
        context = {"extraction_type": "company_profile", "company": company_name}
        return self.extract_triplets(text, context)

    def extract_from_contact_profile(self, contact_name: str, title: str, background: List[str]) -> ExtractionResult:
        """Extract triplets specifically from contact profiles."""
        text = f"{contact_name} - {title}: " + " ".join(background)
        context = {"extraction_type": "contact_profile", "contact": contact_name, "title": title}
        return self.extract_triplets(text, context)

    def refine_triplets(self, initial_result: ExtractionResult, feedback: Dict[str, Any]) -> ExtractionResult:
        """Refine extracted triplets based on feedback."""
        refined_triplets = []

        for triplet in initial_result.triplets:
            # Apply feedback adjustments
            if triplet.subject in feedback.get("remove_subjects", []):
                continue

            confidence_adjustment = feedback.get("confidence_adjustments", {}).get(
                f"{triplet.subject}_{triplet.predicate}_{triplet.object}", 0.0
            )

            refined_triplet = Triplet(
                subject=triplet.subject,
                predicate=triplet.predicate,
                object=triplet.object,
                confidence=max(0.0, min(1.0, triplet.confidence + confidence_adjustment)),
                source=triplet.source,
                metadata={**triplet.metadata, "refined": True}
            )
            refined_triplets.append(refined_triplet)

        return ExtractionResult(
            text=initial_result.text,
            triplets=refined_triplets,
            processing_time=initial_result.processing_time,
            confidence_score=sum(t.confidence for t in refined_triplets) / len(refined_triplets) if refined_triplets else 0.0,
            metadata={**initial_result.metadata, "refined": True, "feedback": feedback}
        )

    def _generate_mock_triplets(self, text: str, context: Dict[str, Any] = None) -> List[Triplet]:
        """Generate mock triplets for testing purposes."""
        # Simple mock extraction based on text content
        mock_triplets = []

        if "company" in text.lower():
            mock_triplets.append(Triplet(
                subject="Company",
                predicate="has_industry",
                object="Technology",
                confidence=0.9,
                source="mock_extraction"
            ))
            mock_triplets.append(Triplet(
                subject="Company",
                predicate="has_size",
                object="1000-5000",
                confidence=0.8,
                source="mock_extraction"
            ))

        if "engineer" in text.lower() or "manager" in text.lower():
            mock_triplets.append(Triplet(
                subject="Contact",
                predicate="has_role",
                object="Engineering",
                confidence=0.85,
                source="mock_extraction"
            ))
            mock_triplets.append(Triplet(
                subject="Contact",
                predicate="has_experience",
                object="10+ years",
                confidence=0.8,
                source="mock_extraction"
            ))

        return mock_triplets

def create_extraction_plan(source_text: str = "", config: Optional[ExtractionConfig] = None) -> Dict[str, Any]:
    """Create an extraction plan with configuration and strategy."""
    config = config or ExtractionConfig()

    return {
        "source_text": source_text,
        "model_name": config.model_name,
        "confidence_threshold": config.confidence_threshold,
        "max_triplets": config.max_triplets,
        "strategy": {
            "extraction_method": "nlp_pipeline",
            "filtering": "confidence_based",
            "post_processing": "refinement_enabled"
        },
        "pipelines": [
            {
                "name": "company_profile_extraction",
                "description": "Extract triplets from company descriptions",
                "config": {"context_type": "company_profile"}
            },
            {
                "name": "contact_profile_extraction",
                "description": "Extract triplets from contact backgrounds",
                "config": {"context_type": "contact_profile"}
            },
            {
                "name": "general_text_extraction",
                "description": "Extract triplets from arbitrary text",
                "config": {"context_type": "general"}
            }
        ],
        "quality_controls": {
            "min_confidence": config.confidence_threshold,
            "max_results": config.max_triplets,
            "validation": "schema_check"
        },
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "config": config.metadata
        }
    }
