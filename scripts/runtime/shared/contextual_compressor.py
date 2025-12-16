"""Contextual Compressor - Precision Layer for RAG.

This component extracts only the relevant sentences from retrieved chunks,
reducing noise and improving signal density in the RAG pipeline.
"""
import logging
import re
import time
from typing import List, Optional, Set

from pydantic import BaseModel, Field

from services.configuration import ConfigurationService

LOGGER = logging.getLogger(__name__)


class CompressionResult(BaseModel):
    """Result of contextual compression operation."""
    original_length: int = Field(...,
                                 description='Original text length in characters')
    compressed_length: int = Field(...,
                                   description='Compressed text length in characters')
    compressed_text: str = Field(..., description='Compressed text content')
    compression_ratio: float = Field(..., ge=0.0, le=1.0,
                                     description='Compression ratio (compressed/original)')


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
        self.sentence_pattern = re.compile(
            '(?<!\\w\\.\\w.)(?<![A-Z][a-z]\\.)(?<=\\.|\\?|\\!)\\s', re.MULTILINE)
        self.entity_patterns = {
            'person': '\\b([A-Z][a-z]+ [A-Z][a-z]+)\\b',
            'organization': '\\b([A-Z]{2,})\\b',
            'metric': '\\b(\\d+(?:\\.\\d+)?%|\\d+(?:,\\d{3})*(?:\\.\\d+)?[kmb]?)\\b',
            'date': '\\b(\\d{4}|\\d{1,2}/\\d{1,2}/\\d{2,4})\\b'}
        ConfigurationService().logger.info(
            f'Initialized ContextualCompressor: threshold={similarity_threshold},\n            LLM={use_llm}')

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        sentences = self.sentence_pattern.split(text.strip())
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
        words1 = set((word.lower().strip('.,!?;:"""()[]{}')
                     for word in text1.split()))
        words2 = set((word.lower().strip('.,!?;:"""()[]{}')
                     for word in text2.split()))
        words1.discard('')
        words2.discard('')
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def _extract_entities(self, text: str) -> Set[str]:
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

    def _compress_heuristic(self, chunks: List[str], query: str) -> str:
        """Compress using heuristic Jaccard similarity.

        Args:
            chunks: List of text chunks
            query: Query string for relevance

        Returns:
            Compressed text
        """
        start_time = time.time()
        query_entities = self._extract_entities(query)
        query_words = set((word.lower() for word in query.split()))
        all_sentences = []
        for chunk in chunks:
            all_sentences.extend(self._split_into_sentences(chunk))

        sentence_scores = []
        for i, sentence in enumerate(all_sentences):
            similarity = self._calculate_jaccard_similarity(sentence, query)
            sentence_entities = self._extract_entities(sentence)
            entity_match = bool(query_entities.intersection(sentence_entities))
            sentence_words = set((word.lower() for word in sentence.split()))
            keyword_match = bool(query_words.intersection(sentence_words))

            sentence_scores.append({
                'index': i,
                'sentence': sentence,
                'similarity': similarity,
                'entity_match': entity_match,
                'keyword_match': keyword_match
            })

        selected_sentences = []
        for score in sentence_scores:
            should_include = False
            if score['similarity'] >= self.similarity_threshold:
                should_include = True
            elif score['entity_match']:
                should_include = True
            elif score['keyword_match'] and score['similarity'] >= 0.05:
                should_include = True

            if should_include:
                # Check if the previous sentence was already included to maintain context
                # This is a simplification; a more robust approach might look at sentence proximity
                # or a fixed window of sentences.
                if selected_sentences and selected_sentences[-1]['index'] == score['index'] - 1:
                    selected_sentences.append(score)
                elif not selected_sentences and score['index'] == 0: # Include the first sentence if it meets criteria
                    selected_sentences.append(score)
                elif selected_sentences and score['index'] > selected_sentences[-1]['index'] + 1:
                    # If there's a gap, check if the current sentence is sufficiently relevant
                    # For simplicity, we'll just add it if it meets criteria and wasn't directly adjacent
                    selected_sentences.append(score)
                elif not selected_sentences: # First sentence meeting criteria
                    selected_sentences.append(score)


        selected_sentences.sort(key=lambda x: x['index'])
        compressed_text = ' '.join((s['sentence'] for s in selected_sentences))
        elapsed = time.time() - start_time
        ConfigurationService().logger.debug(
            f'Heuristic compression completed in {elapsed:.3f}s')
        return compressed_text

    async def _compress_llm(self, chunks: List[str], query: str) -> str:
        """Compress using LLM extraction.

        Args:
            chunks: List of text chunks
            query: Query string for relevance

        Returns:
            Compressed text
        """
        full_text = '\n\n'.join(chunks)
        try:
            # Assuming get_client and Provider are defined elsewhere and correctly imported/available
            # from services.llm import get_client, Provider # Example import
            # client = get_client(Provider.ANTHROPIC)
            # For now, let's simulate the LLM call and return a placeholder
            # In a real scenario, you would uncomment and use the actual LLM client.

            # Placeholder for LLM call
            PROMPT = f"Extract verbatim sentences from the text below that answer this question: '{query}'.\nDo not rewrite. Do not summarize. If irrelevant, return empty.\n\nText: \n{full_text}\n\nExtracted sentences: "
            # RESPONSE = await client.messages.create(MODEL='claude-3-5-sonnet-20241022', max_tokens=1000, temperature=0.1, messages=[{'role': 'user', 'content': PROMPT}])
            # return RESPONSE.content[0].text.strip()

            # Simulate a heuristic fallback if LLM is not available or fails
            LOGGER.warning("LLM compression not implemented or failed, falling back to heuristic.")
            return self._compress_heuristic(chunks, query)

        except Exception as e:
ConfigurationService().logger.error(f'LLM compression failed: {e}')
            return self._compress_heuristic(chunks, query)


    async def compress(self, chunks: List[str], query: str, use_llm: Optional[bool] = None) -> CompressionResult:
        """Compress retrieved chunks to extract relevant sentences.

        Args:
            chunks: List of retrieved text chunks
            query: Query string for relevance determination
            use_llm: Override to force LLM mode

        Returns:
            CompressionResult with compressed text and metrics
        """
        original_text = ' '.join(chunks)
        original_length = len(original_text)
        should_use_llm = use_llm if use_llm is not None else self.use_llm

        compressed_text = ""
        if should_use_llm:
            # In a real application, you'd likely need an asyncio event loop manager here
            # if this compress method is called from a non-async context.
            # For demonstration, assuming this is called within an async context or
            # an asyncio.run is handled appropriately elsewhere.
            # import asyncio
            # compressed_text = await asyncio.run(self._compress_llm(chunks, query))
            LOGGER.info("LLM compression requested but not fully implemented in this example. Falling back to heuristic.")
            compressed_text = self._compress_heuristic(chunks, query)
        else:
            compressed_text = self._compress_heuristic(chunks, query)

        compressed_length = len(compressed_text)

        # Ensure compressed_text is not None or empty before proceeding
        if compressed_text is None:
            compressed_text = ""
            compressed_length = 0

        # Check for over-compression and return original if necessary
        if not compressed_text or compressed_length < original_length * 0.1:
            LOGGER.warning(
                'Compression too aggressive, returning original text')
            compressed_text = original_text
            compressed_length = original_length

        compression_ratio = compressed_length / original_length if original_length > 0 else 1.0

        LOGGER.info(
            f'Compression ratio: {compression_ratio: .2f}({original_length} -> {compressed_length} chars)')

        if compression_ratio > 0.95:
            LOGGER.warning(
                'Low compression detected - may need threshold tuning')
        elif compression_ratio < 0.05:
            LOGGER.warning(
                'High compression detected - may be too aggressive')

        return CompressionResult(original_length=original_length, compressed_length=compressed_length, compressed_text=compressed_text, compression_ratio=compression_ratio)


def compress_chunks(chunks: List[str], query: str, similarity_threshold: float = 0.1) -> str:
    """Compress chunks using default settings.

    Args:
        chunks: List of text chunks
        query: Query for relevance
        similarity_threshold: Jaccard similarity threshold

    Returns:
        Compressed text
    """
    COMPRESSOR = ContextualCompressor(
        similarity_threshold=similarity_threshold)
    # In an async context, you would use await COMPRESSOR.compress(...)
    # For this synchronous function, we simulate or call the heuristic directly if LLM is not forced.
    # If LLM is potentially used, this function might need to be async or use asyncio.run.
    # For now, assuming heuristic is sufficient or LLM fallback is handled within compress.
    compression_result = COMPRESSOR.compress(chunks, query) # If compress becomes async, this line needs await
    return compression_result.compressed_text

