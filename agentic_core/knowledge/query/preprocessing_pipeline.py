"""Query Preprocessor.

Cleans and normalizes raw queries, generates normalized_query output,
and handles multiple query formats.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class QueryFormat(Enum):
    """Format of the incoming query."""
    RAW_TEXT = "raw_text"
    STRUCTURED = "structured"
    CONVERSATION = "conversation"
    COMMAND = "command"


@dataclass
class QueryPacket:
    """Normalized query packet for routing and retrieval.

    The QueryPacket provides a split structure for distinct routing
    vs. retrieval duties with query provenance tracking.
    """
    # Original query
    raw_query: str
    original_format: QueryFormat = QueryFormat.RAW_TEXT

    # Normalized for routing (intent/domain assessment)
    normalized_query: str = ""
    routing_signal: dict[str, Any] | None = None

    # Normalized for retrieval (vector search)
    retrieval_query: str = ""
    query_vector: list[float] | None = None

    # Context propagation
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Provenance
    source_session: str | None = None
    timestamp: float = field(default_factory=lambda: time.time())

    def __post_init__(self):
        if not self.normalized_query:
            self.normalized_query = self.raw_query
        if not self.retrieval_query:
            self.retrieval_query = self.raw_query


class QueryPreprocessor:
    """Preprocesses queries with cleaning and normalization.

    The QueryPreprocessor handles multiple query formats and produces
    normalized outputs suitable for routing and retrieval operations.
    """

    def __init__(self):
        """Initialize the query preprocessor."""
        self._setup_patterns()
        log.info("QueryPreprocessor initialized")

    def _setup_patterns(self):
        """Setup cleaning patterns."""
        # Whitespace normalization
        self.whitespace_pattern = re.compile(r'\s+')

        # Special character cleaning (preserve essential punctuation)
        self.special_chars_pattern = re.compile(r'[^\w\s\-\.\?\!\,\;\:]')

        # Multiple punctuation
        self.multi_punct_pattern = re.compile(r'[\.\?\!\,\;\:]+')

    def preprocess(
        self,
        query: str | dict[str, Any],
        source_format: QueryFormat = QueryFormat.RAW_TEXT,
        session_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> QueryPacket:
        """Preprocess a query into normalized packet.

        Args:
            query: Raw query string or structured dict
            source_format: Format of the incoming query
            session_id: Optional session identifier
            context: Optional context dictionary

        Returns:
            QueryPacket with normalized routing and retrieval queries
        """
        trace_id = f"preprocess_{hash(str(query)) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "QueryPreprocessor.preprocess",
        )

        # Extract raw text from various formats
        raw_text = self._extract_raw_text(query, source_format)

        # Clean and normalize
        normalized = self._clean_query(raw_text)

        # Create routing-optimized version (focused on intent)
        routing_query = self._optimize_for_routing(normalized)

        # Create retrieval-optimized version (preserve semantic content)
        retrieval_query = self._optimize_for_retrieval(normalized)

        # Build packet
        packet = QueryPacket(
            raw_query=raw_text,
            original_format=source_format,
            normalized_query=normalized,
            retrieval_query=retrieval_query,
            source_session=session_id,
            context=context or {},
            metadata={
                "original_length": len(raw_text),
                "normalized_length": len(normalized),
                "cleaning_applied": normalized != raw_text,
            },
        )

        _emit_records_telemetry_event(
            trace_id,
            "QueryPreprocessor",
            f"processed_{source_format.value}",
        )

        log.debug(f"Preprocessed query: {len(raw_text)} -> {len(normalized)} chars")
        return packet

    def preprocess_batch(
        self,
        queries: list[str | dict[str, Any]],
        source_format: QueryFormat = QueryFormat.RAW_TEXT,
    ) -> list[QueryPacket]:
        """Preprocess multiple queries.

        Args:
            queries: List of raw queries
            source_format: Format of incoming queries

        Returns:
            List of QueryPacket objects
        """
        return [
            self.preprocess(q, source_format)
            for q in queries
        ]

    def _extract_raw_text(
        self,
        query: str | dict[str, Any],
        format: QueryFormat,
    ) -> str:
        """Extract raw text from various query formats."""
        if isinstance(query, str):
            return query

        if format == QueryFormat.CONVERSATION:
            # Extract from conversation format
            messages = query.get("messages", [])
            if messages:
                # Get last user message
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        return msg.get("content", "")
            return query.get("text", "")

        if format == QueryFormat.STRUCTURED:
            # Extract from structured format
            return query.get("query", query.get("text", query.get("content", "")))

        if format == QueryFormat.COMMAND:
            # Extract command arguments
            args = query.get("args", [])
            return " ".join(str(a) for a in args) if args else query.get("command", "")

        # Default: try common keys
        for key in ["query", "text", "content", "question", "input"]:
            if key in query:
                return str(query[key])

        return str(query)

    def _clean_query(self, query: str) -> str:
        """Clean and normalize query text."""
        # Strip leading/trailing whitespace
        cleaned = query.strip()

        # Normalize whitespace
        cleaned = self.whitespace_pattern.sub(' ', cleaned)

        # Remove excessive special characters (but preserve meaning)
        cleaned = self.special_chars_pattern.sub('', cleaned)

        # Normalize multiple punctuation
        cleaned = self.multi_punct_pattern.sub(lambda m: m.group(0)[0], cleaned)

        return cleaned.strip()

    def _optimize_for_routing(self, query: str) -> str:
        """Optimize query for routing (intent/domain focus)."""
        # For routing, we want to focus on key terms
        # Remove stop words (basic implementation)
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'and', 'but', 'or', 'yet', 'so',
            'if', 'because', 'although', 'though', 'while', 'where',
            'when', 'that', 'which', 'who', 'whom', 'whose', 'what',
            'this', 'these', 'those', 'i', 'me', 'my', 'myself', 'we',
            'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'am',
        }

        words = query.lower().split()
        keywords = [w for w in words if w not in stop_words]

        return ' '.join(keywords) if keywords else query

    def _optimize_for_retrieval(self, query: str) -> str:
        """Optimize query for retrieval (semantic content preservation)."""
        # For retrieval, preserve more of the original meaning
        # Just basic cleaning without aggressive stop word removal
        return query


# Global instance
_global_preprocessor: QueryPreprocessor | None = None


def get_query_preprocessor() -> QueryPreprocessor:
    """Get or create the global query preprocessor."""
    global _global_preprocessor
    if _global_preprocessor is None:
        _global_preprocessor = QueryPreprocessor()
    return _global_preprocessor
