"""Corpus Classifier.

Classifies documents by corpus type and routes to appropriate chunking strategies.
Eliminates generic defaults by providing corpus-aware classification.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from agentic_core.knowledge.ingestion.modality_types import ContentType, DocumentModality

log = logging.getLogger(__name__)


class CorpusType(Enum):
    """Type of document corpus."""

    POLICY = "policy"  # Policy/long documents
    INCIDENT_TRACE = "incident_trace"  # Incident logs, traces
    CODE_CONFIG = "code_config"  # Code and configuration
    VISUAL_TABLE = "visual_table"  # Visuals, tables, diagrams
    GENERAL = "general"  # General unstructured text


@dataclass
class ClassificationResult:
    """Result of corpus classification."""

    corpus_type: CorpusType
    confidence: float
    indicators: list[str]
    recommended_strategy: str
    metadata_tags: list[str]


class CorpusClassifier:
    """Classifies documents into corpus types for strategy routing.

    The CorpusClassifier analyzes document content and metadata to determine
    the appropriate corpus type, enabling corpus-aware chunking strategies
    that eliminate generic defaults.
    """

    def __init__(self):
        """Initialize the corpus classifier."""
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup classification patterns."""
        # Policy document indicators
        self.policy_patterns = [
            r"\b(policy|procedure|guideline|standard|compliance|regulation)\b",
            r"\b(section|article|clause|provision)\s+\d+",
            r"\b(approved|effective|version|revision)\s+date",
            r"\b(responsible|owner|stakeholder)\s*:",
        ]

        # Incident/trace indicators
        self.incident_patterns = [
            r"\b(incident|event|alert|error|exception|trace|log)\b",
            r"\b(timestamp|datetime|occurred|detected)\s*:?\s*\d",
            r"\b(severity|priority|impact|status)\s*:?\s*(high|medium|low|critical)",
            r"\b(stack\s*trace|call\s*stack|exception\s*details)",
        ]

        # Code/config indicators
        self.code_patterns = [
            r"```[\w\+\-]*\n",  # Code blocks
            r"\b(function|def|class|method|import|from|const|var|let)\b",
            r"[=:]+\s*[\{\[]",  # JSON/YAML-like structures
            r"\b(config|configuration|settings|properties|yaml|json|xml)\b",
        ]

        # Visual/table indicators
        self.visual_patterns = [
            r"!\[.*?\]\(.*?\)",  # Markdown images
            r"<img\s+",  # HTML images
            r"\|[-:]+\|",  # Markdown tables
            r"\b(chart|graph|diagram|figure|plot|visualization)\b",
        ]

    def classify(
        self,
        content: str,
        file_path: Path | None = None,
        modality: DocumentModality | None = None,
        content_type: ContentType | None = None,
    ) -> ClassificationResult:
        """Classify a document into corpus type.

        Args:
            content: Document content
            file_path: Optional file path
            modality: Optional detected modality
            content_type: Optional content type

        Returns:
            ClassificationResult with corpus type and metadata
        """
        scores: dict[CorpusType, float] = dict.fromkeys(CorpusType, 0.0)
        indicators: dict[CorpusType, list[str]] = {ct: [] for ct in CorpusType}

        content_lower = content.lower()

        # Score each corpus type
        for pattern in self.policy_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                scores[CorpusType.POLICY] += len(matches) * 0.3
                indicators[CorpusType.POLICY].append(f"policy_pattern:{pattern[:20]}")

        for pattern in self.incident_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                scores[CorpusType.INCIDENT_TRACE] += len(matches) * 0.3
                indicators[CorpusType.INCIDENT_TRACE].append(f"incident_pattern:{pattern[:20]}")

        for pattern in self.code_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                scores[CorpusType.CODE_CONFIG] += len(matches) * 0.3
                indicators[CorpusType.CODE_CONFIG].append(f"code_pattern:{pattern[:20]}")

        for pattern in self.visual_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                scores[CorpusType.VISUAL_TABLE] += len(matches) * 0.3
                indicators[CorpusType.VISUAL_TABLE].append(f"visual_pattern:{pattern[:20]}")

        # Consider modality hints
        if modality:
            if modality == DocumentModality.CODE_BASE:
                scores[CorpusType.CODE_CONFIG] += 0.5
                indicators[CorpusType.CODE_CONFIG].append("modality:code")
            elif modality == DocumentModality.VISUAL_HEAVY:
                scores[CorpusType.VISUAL_TABLE] += 0.5
                indicators[CorpusType.VISUAL_TABLE].append("modality:visual")
            elif modality == DocumentModality.TABULAR_DATA:
                scores[CorpusType.VISUAL_TABLE] += 0.5
                indicators[CorpusType.VISUAL_TABLE].append("modality:table")

        # Consider file extension
        if file_path:
            ext = file_path.suffix.lower()
            code_exts = [
                ".py",
                ".js",
                ".ts",
                ".java",
                ".cpp",
                ".c",
                ".h",
                ".cs",
                ".rb",
                ".go",
                ".rs",
                ".swift",
                ".kt",
                ".scala",
            ]
            config_exts = [".yaml", ".yml", ".json", ".xml", ".toml", ".ini", ".conf", ".cfg"]
            doc_exts = [".md", ".rst", ".txt"]

            if ext in code_exts:
                scores[CorpusType.CODE_CONFIG] += 0.4
                indicators[CorpusType.CODE_CONFIG].append(f"extension:{ext}")
            elif ext in config_exts:
                scores[CorpusType.CODE_CONFIG] += 0.4
                indicators[CorpusType.CODE_CONFIG].append(f"extension:{ext}")
            elif ext in doc_exts:
                # Docs could be policy or general
                scores[CorpusType.POLICY] += 0.2
                scores[CorpusType.GENERAL] += 0.2

        # Determine winner
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # If no strong indicators, default to general
        if best_score < 0.1:
            best_type = CorpusType.GENERAL

        # Calculate confidence
        total_score = sum(scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.5

        # Get recommended strategy
        strategy_map = {
            CorpusType.POLICY: "section_aware",
            CorpusType.INCIDENT_TRACE: "semantic_object",
            CorpusType.CODE_CONFIG: "semantic_object",
            CorpusType.VISUAL_TABLE: "fixed_token",
            CorpusType.GENERAL: "overlap_window",
        }

        # Build metadata tags
        tags = [best_type.value] + indicators[best_type][:3]  # Top 3 indicators

        return ClassificationResult(
            corpus_type=best_type,
            confidence=confidence,
            indicators=indicators[best_type],
            recommended_strategy=strategy_map[best_type],
            metadata_tags=tags,
        )

    def batch_classify(
        self,
        documents: list[tuple[str, Path | None]],
    ) -> list[ClassificationResult]:
        """Classify multiple documents.

        Args:
            documents: List of (content, file_path) tuples

        Returns:
            List of ClassificationResult objects
        """
        results = []
        for content, file_path in documents:
            result = self.classify(content, file_path)
            results.append(result)
        return results


# Global instance
_global_classifier: CorpusClassifier | None = None


def get_corpus_classifier() -> CorpusClassifier:
    """Get or create the global corpus classifier."""
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = CorpusClassifier()
    return _global_classifier


def classify_document(
    content: str,
    file_path: Path | None = None,
) -> ClassificationResult:
    """Convenience function to classify a document."""
    return get_corpus_classifier().classify(content, file_path)
