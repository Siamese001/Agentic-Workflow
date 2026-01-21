"""Proof-of-Work Injector - Links resume claims to evidence.

This module scans an evidence library and injects clickable links into
resume bullets where the evidence supports the claim, ensuring high
signal with verifiable proof.
"""

import json
import logging
import re
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EvidenceType(str, Enum):
    """Types of evidence items."""
    GITHUB_REPO = "GITHUB_REPO"
    LIVE_DEMO = "LIVE_DEMO"
    PUBLICATION = "PUBLICATION"  # Blog, Paper, Patent
    CASE_STUDY = "CASE_STUDY"
    PORTFOLIO = "PORTFOLIO"
    CERTIFICATION = "CERTIFICATION"
    AWARD = "AWARD"


class EvidenceItem(BaseModel):
    """Individual evidence item."""
    id: str
    url: str
    title: str
    type: EvidenceType
    keywords: list[str] = Field(default_factory=list)
    description: str
    confidence_threshold: float = Field(default=0.3, description="Min similarity for match")
    priority: int = Field(default=1, description="Higher priority = preferred match")


class EvidenceInjector:
    """Injects evidence links into resume bullets."""

    def __init__(self, max_links_per_bullet: int = 1, max_links_per_resume: int = 5):
        """Initialize evidence injector.

        Args:
            max_links_per_bullet: Maximum links to inject per bullet
            max_links_per_resume: Maximum total links per resume
        """
        self.max_links_per_bullet = max_links_per_bullet
        self.max_links_per_resume = max_links_per_resume
        self.evidence_library: list[EvidenceItem] = []
        self._links_used = 0

        logger.info(f"Initialized EvidenceInjector (max {max_links_per_bullet}/bullet, {max_links_per_resume}/resume)")

    def load_library(self, path: str) -> None:
        """Load evidence library from file.

        Args:
            path: Path to JSON/YAML file containing evidence
        """
        file_path = Path(path)

        if not file_path.exists():
            logger.warning(f"Evidence library file not found: {path}")
            return

        try:
            with open(file_path, encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    import yaml
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)

            # Parse evidence items
            self.evidence_library = []
            for item_data in data.get('evidence', []):
                # Convert type string to enum
                if 'type' in item_data and isinstance(item_data['type'], str):
                    item_data['type'] = EvidenceType(item_data['type'])

                evidence = EvidenceItem(**item_data)
                self.evidence_library.append(evidence)

            logger.info(f"Loaded {len(self.evidence_library)} evidence items from {path}")

        except Exception as e:
            logger.error(f"Failed to load evidence library: {e}")
            raise

    def inject(self, bullets: list[str]) -> list[str]:
        """Inject evidence links into resume bullets.

        Args:
            bullets: List of resume bullet points

        Returns:
            Bullets with injected evidence links
        """
        if not self.evidence_library:
            logger.warning("No evidence library loaded")
            return bullets

        injected_bullets = []
        self._links_used = 0

        for bullet in bullets:
            if self._links_used >= self.max_links_per_resume:
                # Reached max links, add remaining bullets as-is
                injected_bullets.append(bullet)
                continue

            injected_bullet = self._inject_into_bullet(bullet)
            injected_bullets.append(injected_bullet)

        logger.info(f"Injected {self._links_used} evidence links into {len(bullets)} bullets")
        return injected_bullets

    def _inject_into_bullet(self, bullet: str) -> str:
        """Inject evidence links into a single bullet.

        Args:
            bullet: Single resume bullet

        Returns:
            Bullet with injected links
        """
        best_matches = self._find_best_matches(bullet)

        if not best_matches:
            return bullet

        # Take top match based on priority and relevance
        best_match = max(best_matches, key=lambda m: (m[1].priority, m[0]))

        # Inject link
        evidence = best_match[1]
        similarity_score = best_match[0]

        # Find the best phrase to link
        link_phrase = self._find_link_phrase(bullet, evidence)

        if link_phrase:
            # Create markdown link
            link_text = f"[{link_phrase}]({evidence.url})"
            injected_bullet = bullet.replace(link_phrase, link_text, 1)

            self._links_used += 1

            logger.debug(f"Injected link for '{evidence.id}' (similarity: {similarity_score:.2f})")
            return injected_bullet

        return bullet

    def _find_best_matches(self, bullet: str) -> list[tuple[float, EvidenceItem]]:
        """Find best matching evidence for a bullet.

        Args:
            bullet: Resume bullet text

        Returns:
            List of (similarity_score, evidence) tuples
        """
        matches = []
        bullet_lower = bullet.lower()

        for evidence in self.evidence_library:
            # Calculate similarity score
            similarity = self._calculate_similarity(bullet_lower, evidence)

            if similarity >= evidence.confidence_threshold:
                matches.append((similarity, evidence))

        # Sort by similarity (descending)
        matches.sort(key=lambda m: m[0], reverse=True)

        return matches[:self.max_links_per_bullet]

    def _calculate_similarity(self, bullet: str, evidence: EvidenceItem) -> float:
        """Calculate similarity between bullet and evidence.

        Args:
            bullet: Lowercase bullet text
            evidence: Evidence item

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Keyword matching score
        keyword_score = 0.0
        if evidence.keywords:
            matches = sum(1 for kw in evidence.keywords if kw.lower() in bullet)
            keyword_score = matches / len(evidence.keywords)

        # Title matching score
        title_score = 0.0
        title_words = evidence.title.lower().split()
        if title_words:
            matches = sum(1 for word in title_words if word in bullet)
            title_score = matches / len(title_words)

        # Description matching score
        desc_score = 0.0
        if evidence.description:
            desc_words = evidence.description.lower().split()
            if desc_words:
                matches = sum(1 for word in desc_words[:20] if word in bullet)  # Check first 20 words
                desc_score = matches / min(len(desc_words), 20)

        # Weighted combination
        total_score = (keyword_score * 0.5) + (title_score * 0.3) + (desc_score * 0.2)

        return min(total_score, 1.0)

    def _find_link_phrase(self, bullet: str, evidence: EvidenceItem) -> str | None:
        """Find the best phrase in bullet to link to evidence.

        Args:
            bullet: Resume bullet text
            evidence: Evidence item

        Returns:
            Phrase to link or None
        """
        # Try to find exact keyword matches first
        for keyword in evidence.keywords:
            if keyword.lower() in bullet.lower():
                # Find the exact case in bullet
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                match = pattern.search(bullet)
                if match:
                    return match.group()

        # Try to find title words
        title_words = evidence.title.split()
        for word in title_words:
            if len(word) > 3 and word.lower() in bullet.lower():  # Skip short words
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                match = pattern.search(bullet)
                if match:
                    return match.group()

        # Try to find technical terms or achievements
        technical_patterns = [
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b',  # CamelCase terms
            r'\b\w+(?:-\w+)+\b',  # Hyphenated terms
            r'\b\w+(?:\s+\w+){1,3}\b'  # 2-4 word phrases
        ]

        for pattern in technical_patterns:
            matches = re.findall(pattern, bullet)
            for match in matches:
                if len(match) > 3 and match.lower() not in ['and', 'the', 'for', 'with', 'from']:
                    return match

        return None

    def add_evidence(self, evidence: EvidenceItem) -> None:
        """Add a single evidence item to the library.

        Args:
            evidence: Evidence item to add
        """
        self.evidence_library.append(evidence)
        logger.debug(f"Added evidence item: {evidence.id}")

    def remove_evidence(self, evidence_id: str) -> bool:
        """Remove evidence item by ID.

        Args:
            evidence_id: ID of evidence to remove

        Returns:
            True if removed
        """
        for i, evidence in enumerate(self.evidence_library):
            if evidence.id == evidence_id:
                del self.evidence_library[i]
                logger.debug(f"Removed evidence item: {evidence_id}")
                return True
        return False

    def get_stats(self) -> dict[str, any]:
        """Get injector statistics.

        Returns:
            Statistics dictionary
        """
        type_counts = {}
        for evidence in self.evidence_library:
            type_counts[evidence.type.value] = type_counts.get(evidence.type.value, 0) + 1

        return {
            "total_evidence": len(self.evidence_library),
            "type_distribution": type_counts,
            "max_links_per_bullet": self.max_links_per_bullet,
            "max_links_per_resume": self.max_links_per_resume,
            "links_injected": self._links_used
        }


# Global injector instance
_evidence_injector: EvidenceInjector | None = None


def get_evidence_injector() -> EvidenceInjector:
    """Get global evidence injector instance.

    Returns:
        EvidenceInjector instance
    """
    global _evidence_injector
    if _evidence_injector is None:
        _evidence_injector = EvidenceInjector()
    return _evidence_injector


# Convenience function
def inject_evidence_links(bullets: list[str], library_path: str | None = None) -> list[str]:
    """Inject evidence links into resume bullets.

    Args:
        bullets: Resume bullet points
        library_path: Path to evidence library file

    Returns:
        Bullets with injected links
    """
    injector = get_evidence_injector()

    if library_path:
        injector.load_library(library_path)

    return injector.inject(bullets)


# Create sample evidence library
def create_sample_library(path: str = "evidence_library.json") -> None:
    """Create a sample evidence library file.

    Args:
        path: Path to create library file
    """
    sample_evidence = [
        {
            "id": "rag_pipeline_2023",
            "url": "https://github.com/example/rag-pipeline",
            "title": "Production RAG Pipeline",
            "type": "GITHUB_REPO",
            "keywords": ["rag", "retrieval", "augmented", "generation", "pipeline", "vector"],
            "description": "A production-ready RAG pipeline with 10M+ documents processed",
            "priority": 3
        },
        {
            "id": "ml_platform_demo",
            "url": "https://demo.example.com/ml-platform",
            "title": "ML Platform Live Demo",
            "type": "LIVE_DEMO",
            "keywords": ["machine learning", "platform", "demo", "interactive", "visualization"],
            "description": "Interactive demo of ML platform with real-time predictions",
            "priority": 2
        },
        {
            "id": "distributed_systems_paper",
            "url": "https://arxiv.org/abs/2023.example",
            "title": "Scaling Distributed Systems",
            "type": "PUBLICATION",
            "keywords": ["distributed", "systems", "scaling", "microservices", "architecture"],
            "description": "Research paper on distributed systems scaling patterns",
            "priority": 1
        },
        {
            "id": "performance_case_study",
            "url": "https://example.com/case-study/performance",
            "title": "10x Performance Improvement",
            "type": "CASE_STUDY",
            "keywords": ["performance", "optimization", "10x", "latency", "throughput"],
            "description": "Case study on achieving 10x performance improvement",
            "priority": 2
        },
        {
            "id": "tech_portfolio",
            "url": "https://portfolio.example.com",
            "title": "Technical Portfolio",
            "type": "PORTFOLIO",
            "keywords": ["portfolio", "projects", "showcase", "work", "achievements"],
            "description": "Comprehensive portfolio of technical projects",
            "priority": 1
        }
    ]

    library_data = {"evidence": sample_evidence}

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(library_data, f, indent=2)

    logger.info(f"Created sample evidence library at {path}")
