"""Contextual Compressor - Precision Layer for RAG.

This component extracts only the relevant sentences from retrieved chunks,
reducing noise and improving signal density in the RAG pipeline.
"""

import logging
import re
import time

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CompressionResult(BaseModel):
    """Result of contextual compression operation."""

    original_length: int = Field(..., description="Original text length in characters")
    compressed_length: int = Field(..., description="Compressed text length in characters")
    compressed_text: str = Field(..., description="Compressed text content")
    compression_ratio: float = Field(
        ..., ge=0.0, le=1.0, description="Compression ratio (compressed/original)"
    )


class ContextualCompressor:
    """Compresses retrieved chunks to extract only relevant sentences.

    Uses Jaccard similarity and simple heuristics to filter sentences
    that are relevant to the query while maintaining context.
    """

    def __init__(self, similarity_threshold: float = 0.1, use_llm: bool = False):
        """Initialize the Contextual Compressor.

        Args:
            similarity_threshold: Minimum Jaccard similarity to keep a sentence
            use_llm: Whether to use LLM for extraction (heuristic mode if False)
        """
        self.similarity_threshold = similarity_threshold
        self.use_llm = use_llm

        # Simple sentence tokenizer using regex
        self.sentence_pattern = re.compile(
            r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s", re.MULTILINE
        )

        # Named entity patterns (simple keyword-based)
        self.entity_patterns = {
            "person": r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b",
            "organization": r"\b([A-Z]{2,})\b",
            "metric": r"\b(\d+(?:\.\d+)?%|\d+(?:,\d{3})*(?:\.\d+)?[kmb]?)\b",
            "date": r"\b(\d{4}|\d{1,2}/\d{1,2}/\d{2,4})\b",
        }

        logger.info(
            f"Initialized ContextualCompressor: threshold={similarity_threshold}, llm={use_llm}"
        )

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences using regex.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        sentences = self.sentence_pattern.split(text.strip())
        # Filter out empty strings and strip whitespace
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts.

        Jaccard similarity = |intersection| / |union|

        Args:
            text1: First text
            text2: Second text

        Returns:
            Jaccard similarity score (0-1)
        """
        # Convert to lowercase and split into words
        words1 = set(word.lower().strip('.,!?;:"()[]{}') for word in text1.split())
        words2 = set(word.lower().strip('.,!?;:"()[]{}') for word in text2.split())

        # Remove empty strings
        words1.discard("")
        words2.discard("")

        # Calculate intersection and union
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _extract_entities(self, text: str) -> set[str]:
        """Extract named entities from text using simple patterns.

        Args:
            text: Text to extract entities from

        Returns:
            Set of extracted entities
        """
        entities = set()

        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            entities.update(matches)

        return entities

    def _compress_heuristic(self, chunks: list[str], query: str) -> str:
        """Compress using heuristic Jaccard similarity.

        Args:
            chunks: List of text chunks
            query: Query string for relevance

        Returns:
            Compressed text
        """
        start_time = time.time()

        # Extract entities from query
        query_entities = self._extract_entities(query)
        query_words = set(word.lower() for word in query.split())

        selected_sentences = []
        all_sentences = []

        # Process all chunks
        for chunk in chunks:
            sentences = self._split_into_sentences(chunk)
            all_sentences.extend(sentences)

        # Score each sentence
        sentence_scores = []
        for i, sentence in enumerate(all_sentences):
            # Calculate Jaccard similarity
            similarity = self._calculate_jaccard_similarity(sentence, query)

            # Check for entity matches
            sentence_entities = self._extract_entities(sentence)
            entity_match = bool(query_entities.intersection(sentence_entities))

            # Check for direct keyword matches
            sentence_words = set(word.lower() for word in sentence.split())
            keyword_match = bool(query_words.intersection(sentence_words))

            sentence_scores.append(
                {
                    "index": i,
                    "sentence": sentence,
                    "similarity": similarity,
                    "entity_match": entity_match,
                    "keyword_match": keyword_match,
                }
            )

        # Select sentences based on criteria
        for i, score in enumerate(sentence_scores):
            should_include = False

            # Include if similarity threshold met
            if score["similarity"] >= self.similarity_threshold:
                should_include = True

            # Include if entity match
            elif score["entity_match"]:
                should_include = True

            # Include if keyword match (lower threshold)
            elif score["keyword_match"] and score["similarity"] >= 0.05:
                should_include = True

            # Add buffer sentence (preceding) if included
            if should_include and i > 0:
                prev_index = sentence_scores[i - 1]["index"]
                if prev_index not in [s["index"] for s in selected_sentences]:
                    selected_sentences.append(sentence_scores[i - 1])

            if should_include:
                selected_sentences.append(score)

        # Sort by original order and extract sentences
        selected_sentences.sort(key=lambda x: x["index"])
        compressed_text = " ".join(s["sentence"] for s in selected_sentences)

        # Log performance
        elapsed = time.time() - start_time
        logger.debug(f"Heuristic compression completed in {elapsed:.3f}s")

        return compressed_text

    async def _compress_llm(self, chunks: list[str], query: str) -> str:
        """Compress using LLM extraction.

        Args:
            chunks: List of text chunks
            query: Query string for relevance

        Returns:
            Compressed text
        """
        # Combine all chunks
        full_text = "\n\n".join(chunks)

        # Import LLM client
        try:
            from .multi_provider_clients import Provider, get_client

            client = get_client(Provider.ANTHROPIC)

            prompt = f"""Extract verbatim sentences from the text below that answer this question: '{query}'.
Do not rewrite. Do not summarize. If irrelevant, return empty.

Text:
{full_text}

Extracted sentences:"""

            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"LLM compression failed: {e}")
            # Fallback to heuristic
            return self._compress_heuristic(chunks, query)

    def compress(
        self, chunks: list[str], query: str, use_llm: bool | None = None
    ) -> CompressionResult:
        """Compress retrieved chunks to extract relevant sentences.

        Args:
            chunks: List of retrieved text chunks
            query: Query string for relevance determination
            use_llm: Override to force LLM mode

        Returns:
            CompressionResult with compressed text and metrics
        """
        # Calculate original length
        original_text = " ".join(chunks)
        original_length = len(original_text)

        # Determine compression mode
        should_use_llm = use_llm if use_llm is not None else self.use_llm

        # Perform compression
        if should_use_llm:
            # For LLM mode, we need to run async
            import asyncio

            compressed_text = asyncio.run(self._compress_llm(chunks, query))
        else:
            compressed_text = self._compress_heuristic(chunks, query)

        # Safety net: if compression is too aggressive, return original
        if not compressed_text or len(compressed_text) < original_length * 0.1:
            logger.warning("Compression too aggressive, returning original text")
            compressed_text = original_text

        # Calculate metrics
        compressed_length = len(compressed_text)
        compression_ratio = compressed_length / original_length if original_length > 0 else 1.0

        # Log compression ratio for monitoring
        logger.info(
            f"Compression ratio: {compression_ratio:.2f} "
            f"({original_length} -> {compressed_length} chars)"
        )

        # Alert if ratio is unusual
        if compression_ratio > 0.95:
            logger.warning("Low compression detected - may need threshold tuning")
        elif compression_ratio < 0.05:
            logger.warning("High compression detected - may be too aggressive")

        return CompressionResult(
            original_length=original_length,
            compressed_length=compressed_length,
            compressed_text=compressed_text,
            compression_ratio=compression_ratio,
        )


# Convenience function for direct usage
def compress_chunks(chunks: list[str], query: str, similarity_threshold: float = 0.1) -> str:
    """Compress chunks using default settings.

    Args:
        chunks: List of text chunks
        query: Query for relevance
        similarity_threshold: Jaccard similarity threshold

    Returns:
        Compressed text
    """
    compressor = ContextualCompressor(similarity_threshold=similarity_threshold)
    result = compressor.compress(chunks, query)
    return result.compressed_text
