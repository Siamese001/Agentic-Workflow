"""
Signal Anchoring System - Structural Anchors for High-Temperature RAG.

The signal anchoring system transforms raw RAG content into signed claims with
source attribution and confidence scores, preventing hallucinations while
allowing maximum creativity in narrative construction.
"""


import logging
import re
from enum import Enum
from datetime import datetime
import hashlib


logger = logging.getLogger(__name__)

class ClaimType(str, Enum):
    """Types of claims that can be extracted from content."""
    SKILL = "skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    ACHIEVEMENT = "achievement"
    RESPONSIBILITY = "responsibility"
    METRIC = "metric"
    FACT = "fact"
    PREFERENCE = "preference"

class SourceType(str, Enum):
    """Types of sources for claims."""
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    TRANSCRIPT = "transcript"
    CERTIFICATE = "certificate"
    ASSESSMENT = "assessment"
    REFERENCE = "reference"
    SELF_REPORTED = "self_reported"

@dataclass
class SourceMetadata:
    """Metadata about a claim source."""
    source_type: SourceType
    source_id: str
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[datetime] = None
    reliability_score: float = 0.8  # Base reliability of source
    verification_status: str = "unverified"  # unverified, verified, disputed

@dataclass
class ExtractedClaim:
    """A claim extracted from source content."""
    claim_text: str
    claim_type: ClaimType
    source_metadata: SourceMetadata
    confidence: float
    evidence_snippet: Optional[str] = None
    extraction_method: str = "pattern_match"
    context_window: str = ""  # Text around the claim for context

class ClaimExtractor:
    """
    Extracts structured claims from unstructured source content.

    The extractor uses pattern matching and heuristics to identify
    factual claims and assign confidence scores based on source reliability.
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize claim extractor.

        Args:
            enable_logging: Enable extraction logging
        """
        self.enable_logging = enable_logging
        self._extraction_patterns = self._load_extraction_patterns()
        self._source_weights = {
            SourceType.RESUME: 0.9,
            SourceType.CERTIFICATE: 0.95,
            SourceType.ASSESSMENT: 0.85,
            SourceType.REFERENCE: 0.8,
            SourceType.JOB_DESCRIPTION: 0.95,
            SourceType.TRANSCRIPT: 0.7,
            SourceType.SELF_REPORTED: 0.6
        }

        logger.info("claim_extractor_initialized")

    def extract_claims(
        """Docstring."""
        self,
        content: str,
        source_metadata: SourceMetadata
    ) -> List[ExtractedClaim]:
        """Extract claims from source content.

        Args:
            content: Raw source content
            source_metadata: Metadata about the source

        Returns:
            List of extracted claims
        """
        claims = []

        # Extract claims based on patterns
        for claim_type, patterns in self._extraction_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

                for match in matches:
                    claim_text = self._clean_claim_text(match.group(1))
                    if not claim_text or len(claim_text) < 5:
                        continue

                    # Calculate confidence based on source and pattern
                    base_confidence = self._source_weights.get(
                        source_metadata.source_type, 0.5
                    )
                    pattern_confidence = self._get_pattern_confidence(pattern)
                    confidence = min(base_confidence * pattern_confidence, 1.0)

                    # Extract context window
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context_window = content[start:end].strip()

                    claim = ExtractedClaim(
                        claim_text=claim_text,
                        claim_type=ClaimType(claim_type),
                        source_metadata=source_metadata,
                        confidence=confidence,
                        evidence_snippet=match.group(0),
                        context_window=context_window
                    )
                    claims.append(claim)

        # Deduplicate claims
        claims = self._deduplicate_claims(claims)

        if self.enable_logging:
            logger.info(
                "claims_extracted",
                extra={
                    "source_id": source_metadata.source_id,
                    "source_type": source_metadata.source_type.value,
                    "claim_count": len(claims)
                }
            )

        return claims

    def _load_extraction_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for claim extraction.

        Returns:
            Dictionary of claim type to pattern list
        """
        return {
            "skill": [
                r"(?:skilled in|proficient in|expertise in|experience with)\s+([^.\n]+)",
                r"(?:python|java|javascript|sql|aws|docker|kubernetes)"
                    r"\s+(?:developer|engineer|specialist)",
                r"(\d+)\+?\s*years?\s+(?:of\s+)?experience\s+(?:in|with|as)\s+([^.\n]+)",
                r"(?:certified in|certification:\s*)([^.\n]+)",
                r"(?:fluent in|languages?:)\s+([^.\n]+)",
                r"(?:located|based)\s+(?:in|at)\s+([^.\n]+)"
            ],
            "experience": [
                r"(?:worked at|employed by|position at)\s+([^.\n]+)",
                r"(?:senior|lead|principal|staff)\s+([^.\n]+)",
                r"(?:managed|led|directed|oversaw)\s+([^.\n]+)"
            ],
            "education": [
                r"(?:bachelor's|master's|phd|doctorate|degree)\s+in\s+([^.\n]+)",
                r"(?:graduated from|attended)\s+([^.\n]+)",
                r"(?:gpa|grade point average)[^:]*:\s*([\d.]+)"
            ],
            "achievement": [
                r"(?:achieved|accomplished|delivered|produced)\s+([^.\n]+)",
                r"(?:increased|decreased|reduced|improved)\s+([^.\n]+)",
                r"(?:award|recognition|honors?)\s+(?:for|in)\s+([^.\n]+)"
            ],
            "metric": [
                r"(\d+%|\d+\s*(?:percent|percentage))"
                r"\s+(?:increase|decrease|reduction|improvement)",


                r"(\d+(?:\.\d+)?)\s*(?:million|billion|thousand|k|m|b)"
                r"\s+(?:revenue|sales|users|customers)",


                r"managed\s+(?:a\s+)?team\s+of\s+(\d+)"
            ],
            "fact": [
                r"(?:certified in|certification:\s*)([^.\n]+)",
                r"(?:fluent in|languages?:)\s+([^.\n]+)",
                r"(?:located|based)\s+(?:in|at)\s+([^.\n]+)"
            ]
        }

    def _clean_claim_text(self, text: str) -> str:
        """Clean and normalize claim text.

        Args:
            text: Raw claim text

        Returns:
            Cleaned claim text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove trailing punctuation
        text = text.rstrip('.,;:!?"\'')

        # Normalize quotes
        text = text.replace('"', '').replace("'", "")

        return text

    def _get_pattern_confidence(self, pattern: str) -> float:
        """Get confidence score for a specific pattern.

        Args:
            pattern: Regex pattern

        Returns:
            Confidence multiplier (0-1)
        """
        # More specific patterns have higher confidence
        if "years" in pattern:
            return 0.95
        elif "certified" in pattern or "gpa" in pattern:
            return 0.9
        elif "%" in pattern or "managed" in pattern:
            return 0.85
        elif "skill" in pattern or "experience" in pattern:
            return 0.8
        else:
            return 0.7

    def _deduplicate_claims(self, claims: List[ExtractedClaim]) -> List[ExtractedClaim]:
        """Remove duplicate claims based on text similarity.

        Args:
            claims: List of claims to deduplicate

        Returns:
            Deduplicated claim list
        """
        seen = set()
        deduplicated = []

        for claim in claims:
            # Create a normalized key for comparison
            key = self._normalize_claim_key(claim.claim_text)

            if key not in seen:
                seen.add(key)
                deduplicated.append(claim)
            else:
                # Update existing claim if higher confidence
                for i, existing in enumerate(deduplicated):
                    if self._normalize_claim_key(existing.claim_text) == key:
                        if claim.confidence > existing.confidence:
                            deduplicated[i] = claim
                        break

        return deduplicated

    def _normalize_claim_key(self, text: str) -> str:
        """Create a normalized key for claim comparison.

        Args:
            text: Claim text

        Returns:
            Normalized key
        """
        # Lowercase and remove non-alphanumeric
        normalized = re.sub(r'[^a-z0-9]', '', text.lower())
        return normalized

class SignalAnchor:
    """
    Anchors RAG signals with signed claims to prevent hallucinations.

    The anchor transforms raw documents into structured, attributed claims
    that the LLM can reference without hallucinating facts.
    """

    def __init__(
        self,
        claim_extractor: Optional[ClaimExtractor] = None,
        min_confidence: float = 0.6,
        max_claims_per_source: int = 50
    ):
        """Initialize signal anchor.

        Args:
            claim_extractor: Optional claim extractor
            min_confidence: Minimum confidence threshold for claims
            max_claims_per_source: Maximum claims to extract per source
        """
        self.claim_extractor = claim_extractor or ClaimExtractor()
        self.min_confidence = min_confidence
        self.max_claims_per_source = max_claims_per_source

        logger.info(
            "signal_anchor_initialized",
            extra={
                "min_confidence": min_confidence,
                "max_claims_per_source": max_claims_per_source
            }
        )

    def anchor_rag_content(
        """Docstring."""
        self,
        context: SignalContext,
        rag_content: List[Dict[str, Any]]
    ) -> SignalContext:
        """
        Anchor RAG content with signed claims.

        Args:
            context: Signal context to update
            rag_content: List of RAG content items

        Returns:
            Updated context with anchored claims
        """
        total_claims = 0

        for item in rag_content:
            # Extract source metadata
            source_metadata = self._extract_source_metadata(item)

            # Extract claims from content
            content = item.get("content", item.get("text", ""))
            if not content:
                continue

            extracted_claims = self.claim_extractor.extract_claims(
                content, source_metadata
            )

            # Filter by confidence and limit
            valid_claims = [
                c for c in extracted_claims
                if c.confidence >= self.min_confidence
            ][:self.max_claims_per_source]

            # Convert to signed claims and add to context
            for claim in valid_claims:
                signed_claim = SignedClaim(
                    claim=claim.claim_text,
                    source=f"{source_metadata.source_type.value}:{source_metadata.source_id}",
                    confidence=claim.confidence,
                    evidence=claim.evidence_snippet
                )
                context.add_signed_claim(
                    claim.claim_text,
                    signed_claim.source,
                    claim.confidence,
                    claim.evidence_snippet
                )

            total_claims += len(valid_claims)

        logger.info(
            "rag_content_anchored",
            extra={
                "execution_id": context.hard_state.execution_id,
                "content_items": len(rag_content),
                "claims_added": total_claims
            }
        )

        return context

    def _extract_source_metadata(self, item: Dict[str, Any]) -> SourceMetadata:
        """Extract source metadata from RAG item.

        Args:
            item: RAG content item

        Returns:
            Source metadata
        """
        # Determine source type
        source_type_str = item.get("source_type", "document").lower()
        source_type = SourceType.RESUME  # Default

        if "resume" in source_type_str or "cv" in source_type_str:
            source_type = SourceType.RESUME
        elif "job" in source_type_str and "desc" in source_type_str:
            source_type = SourceType.JOB_DESCRIPTION
        elif "cert" in source_type_str:
            source_type = SourceType.CERTIFICATE
        elif "transcript" in source_type_str:
            source_type = SourceType.TRANSCRIPT
        elif "reference" in source_type_str:
            source_type = SourceType.REFERENCE

        # Create source ID from content hash
        content = item.get("content", item.get("text", ""))
        source_id = hashlib.md5(content.encode()).hexdigest()[:8]

        return SourceMetadata(
            source_type=source_type,
            source_id=source_id,
            title=item.get("title"),
            author=item.get("author"),
            date=item.get("date"),
            reliability_score=item.get("reliability", 0.8)
        )

    def get_claim_summary(self, context: SignalContext) -> Dict[str, Any]:
        """Get a summary of anchored claims.

        Args:
            context: Signal context with claims

        Returns:
            Summary statistics
        """
        if not context.signed_claims:
            return {"total_claims": 0}

        # Group by source type
        source_counts = {}
        confidence_sum = 0

        for claim in context.signed_claims:
            source_type = claim.source.split(":")[0]
            source_counts[source_type] = source_counts.get(source_type, 0) + 1
            confidence_sum += claim.confidence

        return {
            "total_claims": len(context.signed_claims),
            "average_confidence": confidence_sum / len(context.signed_claims),
            "sources": source_counts,
            "high_confidence_claims": len([
                c for c in context.signed_claims if c.confidence >= 0.9
            ]),
            "medium_confidence_claims": len([
                c for c in context.signed_claims
                if 0.7 <= c.confidence < 0.9
            ]),
            "low_confidence_claims": len([
                c for c in context.signed_claims if c.confidence < 0.7
            ])
        }

# Factory functions for common anchoring patterns

def create_resume_anchor() -> SignalAnchor:
    """Create a SignalAnchor optimized for resume content."""
    return SignalAnchor(
        min_confidence=0.7,  # Higher threshold for resume claims
        max_claims_per_source=30
    )

def create_job_description_anchor() -> SignalAnchor:
    """Create a SignalAnchor optimized for job descriptions."""
    return SignalAnchor(
        min_confidence=0.8,  # Very high threshold for job requirements
        max_claims_per_source=20
    )

def anchor_resume_content(
    """Docstring."""
    context: SignalContext,
    resume_text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> SignalContext:
    """
    Convenience function to anchor resume content.

    Args:
        context: Signal context to update
        resume_text: Raw resume text
        metadata: Optional metadata

    Returns:
        Updated context with anchored claims
    """
    anchor = create_resume_anchor()

    rag_content = [{
        "content": resume_text,
        "source_type": "resume",
        "title": metadata.get("title") if metadata else "Resume",
        "reliability": 0.9
    }]

    return anchor.anchor_rag_content(context, rag_content)
