"""Semantic Enrichment Layer - Pipeline B Step 3 Implementation

Transforms raw text chunks into structured Semantic Knowledge Objects
via LLM-based enrichment. This is the critical gap identified in v9 spec.

Knowledge Object Schema:
- Title: Concise title capturing the essence
- Summary: 2-3 sentence executive summary
- Key Concepts: List of extracted key concepts/terms
- Agentic Patterns: Detected agentic patterns (if any)
- Execution Insight: Code/execution specific insights
- Query Expansion Terms: Alternative phrasings for retrieval
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SemanticKnowledgeObject:
    """Structured knowledge object from enriched chunk.

    This is the 🟠 fact_vec payload that gets stored in Vector DB.
    """

    chunk_id: str
    title: str
    summary: str
    key_concepts: list[str] = field(default_factory=list)
    agentic_patterns: list[str] = field(default_factory=list)
    execution_insight: str = ""
    query_expansion_terms: list[str] = field(default_factory=list)
    source_metadata: dict[str, Any] = field(default_factory=dict)
    enrichment_hash: str = ""  # Content hash for integrity

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "chunk_id": self.chunk_id,
            "title": self.title,
            "summary": self.summary,
            "key_concepts": self.key_concepts,
            "agentic_patterns": self.agentic_patterns,
            "execution_insight": self.execution_insight,
            "query_expansion_terms": self.query_expansion_terms,
            "source_metadata": self.source_metadata,
            "enrichment_hash": self.enrichment_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SemanticKnowledgeObject:
        """Create from dictionary."""
        return cls(
            chunk_id=data.get("chunk_id", ""),
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            key_concepts=data.get("key_concepts", []),
            agentic_patterns=data.get("agentic_patterns", []),
            execution_insight=data.get("execution_insight", ""),
            query_expansion_terms=data.get("query_expansion_terms", []),
            source_metadata=data.get("source_metadata", {}),
            enrichment_hash=data.get("enrichment_hash", ""),
        )

    def to_enriched_text(self) -> str:
        """Generate enriched text representation for embedding.

        This creates the 🟠 fact_vec payload that captures
        concept similarity beyond raw text matching.
        """
        sections = [
            f"Title: {self.title}",
            f"Summary: {self.summary}",
        ]

        if self.key_concepts:
            sections.append(f"Key Concepts: {', '.join(self.key_concepts)}")

        if self.agentic_patterns:
            sections.append(f"Agentic Patterns: {', '.join(self.agentic_patterns)}")

        if self.execution_insight:
            sections.append(f"Execution Insight: {self.execution_insight}")

        if self.query_expansion_terms:
            sections.append(f"Query Terms: {', '.join(self.query_expansion_terms)}")

        return "\n\n".join(sections)


class SemanticEnricher:
    """LLM-based semantic enrichment for chunks.

    Transforms raw text chunks into Knowledge Objects (Pipeline B Step 3).
    """

    def __init__(
        self,
        llm_client: Any | None = None,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
    ):
        """Initialize semantic enricher.

        Args:
            llm_client: Optional pre-configured LLM client
            provider: LLM provider (openai, anthropic, etc.)
            model: Model name for enrichment
        """
        self.llm_client = llm_client
        self.provider = provider
        self.model = model
        self._enrichment_count = 0
        self._cache: dict[str, SemanticKnowledgeObject] = {}

        if llm_client is None:
            self._init_default_client()

    def _init_default_client(self) -> None:
        """Initialize default LLM client based on provider."""
        if self.provider == "openai":
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not configured")
                self.llm_client = OpenAI(api_key=api_key)
            except (ImportError, ValueError):
                Logger.warning("OpenAI not configured, enrichment will use mock")
                self.llm_client = None
        else:
            Logger.warning(f"Provider {self.provider} not yet supported, using mock")
            self.llm_client = None

    def _build_enrichment_prompt(self, raw_text: str, chunk_type: str = "general") -> str:
        """Build LLM prompt for semantic enrichment.

        Args:
            raw_text: Raw chunk content
            chunk_type: Type of chunk (code, doc, trace, etc.)

        Returns:
            Formatted prompt for LLM
        """
        base_prompt = f"""You are a semantic enrichment engine. Transform the following {chunk_type} content into a structured Knowledge Object.

INPUT CONTENT:
{raw_text}

OUTPUT FORMAT (JSON):
{{
    "title": "Concise, descriptive title (5-10 words)",
    "summary": "Executive summary in 2-3 sentences capturing core meaning",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "agentic_patterns": ["pattern1"],
    "execution_insight": "Code/execution specific insight if applicable",
    "query_expansion_terms": ["alternative phrasing 1", "synonym 2"]
}}

INSTRUCTIONS:
- Title: Capture the essence in 5-10 words
- Summary: 2-3 sentences that explain what this content is about
- Key Concepts: Extract 3-7 important concepts, terms, or entities
- Agentic Patterns: Identify any agentic workflow patterns (e.g., "orchestration", "routing", "guardrails", "evaluation")
- Execution Insight: For code - what does it do? For docs - what action does it enable?
- Query Expansion Terms: 2-4 alternative ways someone might search for this content

Respond with ONLY valid JSON."""

        return base_prompt

    def enrich_chunk(
        self,
        chunk_id: str,
        raw_text: str,
        chunk_type: str = "general",
        source_metadata: dict[str, Any] | None = None,
    ) -> SemanticKnowledgeObject:
        """Enrich a single chunk into a Knowledge Object.

        This implements Pipeline B Step 3: Text -> Knowledge Object transformation.

        Args:
            chunk_id: Unique identifier for the chunk
            raw_text: Raw chunk content
            chunk_type: Type of chunk (code, doc, trace)
            source_metadata: Original source metadata

        Returns:
            Enriched SemanticKnowledgeObject
        """
        _trace_id = f"enrich_{chunk_id}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "SemanticEnricher.enrich_chunk")

        # Check cache
        cache_key = hashlib.sha256(f"{chunk_id}:{raw_text}".encode()).hexdigest()
        if cache_key in self._cache:
            Logger.debug(f"Enrichment cache HIT for {chunk_id}")
            return self._cache[cache_key]

        Logger.info(f"Enriching chunk {chunk_id} ({len(raw_text)} chars)")

        if self.llm_client is None:
            # Mock enrichment for testing/development
            knowledge_obj = self._mock_enrich(chunk_id, raw_text, source_metadata)
        else:
            # Real LLM-based enrichment
            knowledge_obj = self._llm_enrich(chunk_id, raw_text, chunk_type, source_metadata)

        # Store in cache
        self._cache[cache_key] = knowledge_obj
        self._enrichment_count += 1

        _emit_stores_embedding(_trace_id, "enrichment", cache_key)

        return knowledge_obj

    def _mock_enrich(
        self,
        chunk_id: str,
        raw_text: str,
        source_metadata: dict[str, Any] | None = None,
    ) -> SemanticKnowledgeObject:
        """Generate mock enrichment for testing.

        Creates deterministic mock output based on content hash.
        """
        content_hash = hashlib.sha256(raw_text.encode()).hexdigest()[:16]

        # Extract some "concepts" from the text (simple heuristic)
        words = raw_text.split()
        key_concepts = list(set([w for w in words if len(w) > 6][:5]))

        return SemanticKnowledgeObject(
            chunk_id=chunk_id,
            title=f"Chunk {chunk_id[:20]}... (Mock Enriched)",
            summary=f"This content discusses {len(raw_text)} characters of material. Key themes include automation and retrieval.",
            key_concepts=key_concepts if key_concepts else ["automation", "retrieval", "knowledge"],
            agentic_patterns=["orchestration"] if "orchestr" in raw_text.lower() else [],
            execution_insight=f"Content hash: {content_hash}",
            query_expansion_terms=["search", "find", "retrieve"],
            source_metadata=source_metadata or {},
            enrichment_hash=content_hash,
        )

    def _llm_enrich(
        self,
        chunk_id: str,
        raw_text: str,
        chunk_type: str,
        source_metadata: dict[str, Any] | None = None,
    ) -> SemanticKnowledgeObject:
        """Perform LLM-based enrichment.

        Args:
            chunk_id: Chunk identifier
            raw_text: Raw content
            chunk_type: Type of content
            source_metadata: Source metadata

        Returns:
            Enriched knowledge object
        """
        prompt = self._build_enrichment_prompt(raw_text, chunk_type)

        try:
            if self.provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a semantic enrichment engine. Output valid JSON only.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
                result = json.loads(response.choices[0].message.content)
            else:
                # Fallback to mock for unsupported providers
                return self._mock_enrich(chunk_id, raw_text, source_metadata)

            # Compute enrichment hash
            content_hash = hashlib.sha256(raw_text.encode()).hexdigest()[:16]

            return SemanticKnowledgeObject(
                chunk_id=chunk_id,
                title=result.get("title", "Untitled"),
                summary=result.get("summary", ""),
                key_concepts=result.get("key_concepts", []),
                agentic_patterns=result.get("agentic_patterns", []),
                execution_insight=result.get("execution_insight", ""),
                query_expansion_terms=result.get("query_expansion_terms", []),
                source_metadata=source_metadata or {},
                enrichment_hash=content_hash,
            )

        except (AttributeError, RuntimeError, TypeError, ValueError) as e:
            Logger.error(f"LLM enrichment failed for {chunk_id}: {e}")
            # Fallback to mock on error
            return self._mock_enrich(chunk_id, raw_text, source_metadata)

    def enrich_batch(
        self,
        chunks: list[dict[str, Any]],
        chunk_type: str = "general",
    ) -> list[SemanticKnowledgeObject]:
        """Enrich multiple chunks in batch.

        Args:
            chunks: List of chunk dicts with 'id', 'text', 'metadata'
            chunk_type: Type of chunks

        Returns:
            List of enriched knowledge objects
        """
        results = []
        for chunk in chunks:
            knowledge_obj = self.enrich_chunk(
                chunk_id=chunk.get("id", "unknown"),
                raw_text=chunk.get("text", ""),
                chunk_type=chunk_type,
                source_metadata=chunk.get("metadata", {}),
            )
            results.append(knowledge_obj)

        Logger.info(f"Batch enrichment complete: {len(results)} chunks processed")
        return results

    def get_stats(self) -> dict[str, Any]:
        """Get enrichment statistics."""
        return {
            "enrichment_count": self._enrichment_count,
            "cache_size": len(self._cache),
            "provider": self.provider,
            "model": self.model,
        }

    def enrich_chunk_adapter(
        self,
        chunk_text: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Adapter method for legacy pipeline compatibility.

        Matches the interface of the rule-based SemanticEnricher in tools/scripts/enrich_embeddings.py.
        Returns a dict with enriched fields for pipeline compatibility.

        Args:
            chunk_text: Raw chunk content
            metadata: Source metadata dict

        Returns:
            Dict with enriched fields (enriched_text, title, summary, key_concepts, etc.)
        """
        chunk_id = (
            metadata.get("chunk_id", metadata.get("id", "unknown"))
            if isinstance(metadata, dict)
            else "unknown"
        )
        knowledge_obj = self.enrich_chunk(
            chunk_id=chunk_id,
            raw_text=chunk_text,
            chunk_type="general",
            source_metadata=metadata if isinstance(metadata, dict) else {},
        )

        return {
            "enriched_text": knowledge_obj.to_enriched_text(),
            "title": knowledge_obj.title,
            "summary": knowledge_obj.summary,
            "key_concepts": knowledge_obj.key_concepts,
            "agentic_patterns": knowledge_obj.agentic_patterns,
            "execution_insight": knowledge_obj.execution_insight,
            "query_expansion": knowledge_obj.query_expansion_terms,
            "enrichment_hash": knowledge_obj.enrichment_hash,
        }


# Global enricher instance for convenience
_global_enricher: SemanticEnricher | None = None


def get_global_enricher() -> SemanticEnricher:
    """Get or create global enricher instance."""
    global _global_enricher
    if _global_enricher is None:
        _global_enricher = SemanticEnricher()
    return _global_enricher


def enrich_chunk(
    chunk_id: str,
    raw_text: str,
    chunk_type: str = "general",
    source_metadata: dict[str, Any] | None = None,
) -> SemanticKnowledgeObject:
    """Convenience function to enrich a single chunk."""
    return get_global_enricher().enrich_chunk(
        chunk_id=chunk_id,
        raw_text=raw_text,
        chunk_type=chunk_type,
        source_metadata=source_metadata,
    )
