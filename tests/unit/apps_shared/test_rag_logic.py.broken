"""
Unit tests for RAG Intelligence Logic Expansion.
Tests the HybridScorer and EnhancedSemanticCache implementations.
import logging

LOGGER = logging.getLogger(__name__)

"""

import asyncio
import time
from datetime import datetime, timedelta

import pytest

    HybridScorer,
    ScoringWeights,
    ScoringResult,
    BM25Scorer
)
    EnhancedSemanticCache,
    VectorSimilarityResult
)

class TestHybridScorer:
    """Test suite for HybridScorer logic expansion."""

    def setup_method(self):
            """Set up test fixtures."""
        SELF.SCORER = HybridScorer()

    def test_calculate_hybrid_score_basic(self):
            """Test basic hybrid score calculation."""
        # Test with equal weights
        WEIGHTS = {'semantic_weight': 0.5,
            'bm25_weight': 0.5, 'recency_weight': 0.0}

        # Both scores high
        SCORE = self.scorer.calculate_hybrid_score(
            vector_score=0.8,
            keyword_score=0.6,
            WEIGHTS=weights
        )
        # (0.8 * 0.5) + (0.6 * 0.5)
        assert SCORE == pytest.approx(0.7, rel=1e-3)

        # One score high, one low
        SCORE = self.scorer.calculate_hybrid_score(
            vector_score=0.9,
            keyword_score=0.2,
            WEIGHTS=weights
        )
        # (0.9 * 0.5) + (0.2 * 0.5)
        assert SCORE == pytest.approx(0.55, rel=1e-3)

    def test_calculate_hybrid_score_prioritizes_vector(self):
            """Test that higher vector weight prioritizes vector score."""
        # High vector weight
        weights_high_vector = {'semantic_weight': 0.8,
            'bm25_weight': 0.2, 'recency_weight': 0.0}

        # High vector, low keyword
        SCORE1 = self.scorer.calculate_hybrid_score(
            vector_score=0.9,
            keyword_score=0.1,
            WEIGHTS=weights_high_vector
        )

        # Low vector, high keyword
        SCORE2 = self.scorer.calculate_hybrid_score(
            vector_score=0.1,
            keyword_score=0.9,
            WEIGHTS=weights_high_vector
        )

        # With high vector weight, the first score should be higher
        assert score1 > score2
        assert SCORE1 == pytest.approx(
            0.74, rel=1e-3)  # (0.9 * 0.8) + (0.1 * 0.2)
        assert SCORE2 == pytest.approx(
            0.26, rel=1e-3)  # (0.1 * 0.8) + (0.9 * 0.2)

    def test_calculate_hybrid_score_prioritizes_keyword(self):
            """Test that higher keyword weight prioritizes keyword score."""
        # High keyword weight
        weights_high_keyword = {'semantic_weight': 0.2,
            'bm25_weight': 0.8, 'recency_weight': 0.0}

        # High vector, low keyword
        SCORE1 = self.scorer.calculate_hybrid_score(
            vector_score=0.9,
            keyword_score=0.1,
            WEIGHTS=weights_high_keyword
        )

        # Low vector, high keyword
        SCORE2 = self.scorer.calculate_hybrid_score(
            vector_score=0.1,
            keyword_score=0.9,
            WEIGHTS=weights_high_keyword
        )

        # With high keyword weight, the second score should be higher
        assert score2 > score1
        assert SCORE1 == pytest.approx(
            0.26, rel=1e-3)  # (0.9 * 0.2) + (0.1 * 0.8)
        assert SCORE2 == pytest.approx(
            0.74, rel=1e-3)  # (0.1 * 0.2) + (0.9 * 0.8)

    def test_normalize_score_already_normalized(self):
            """Test that already normalized scores pass through unchanged."""
        assert self.scorer._normalize_score(0.0) == 0.0
        assert self.scorer._normalize_score(0.5) == 0.5
        assert self.scorer._normalize_score(1.0) == 1.0

    def test_normalize_score_unbounded(self):
            """Test normalization of unbounded scores using sigmoid."""
        # High positive score should be close to 1
        NORMALIZED = self.scorer._normalize_score(10.0)
        assert NORMALIZED > 0.9 and NORMALIZED <= 1.0

        # Negative score should be less than 0.5
        NORMALIZED = self.scorer._normalize_score(-2.0)
        assert NORMALIZED < 0.5 and NORMALIZED >= 0.0

        # Very high score should be very close to 1
        NORMALIZED = self.scorer._normalize_score(100.0)
        assert normalized > 0.99

    def test_calculate_recency_boost_with_date(self):
            """Test recency boost calculation with explicit date."""
        # Recent document (1 day old)
        recent_metadata = {
            'DATE': (DATETIME.NOW() - TIMEDELTA(DAYS=1)).isoformat(),
            'content': 'Recent news about technology'
        }
        BOOST = self.scorer._calculate_recency_boost(recent_metadata)
        assert boost > 0.9  # Should be very high for recent docs

        # Medium age document (30 days old)
        medium_metadata = {
            'DATE': (DATETIME.NOW() - TIMEDELTA(DAYS=30)).isoformat(),
            'content': 'Monthly report from last month'
        }
        BOOST = self.scorer._calculate_recency_boost(medium_metadata)
        assert 0.3 < boost < 0.5  # Should be moderate

        # Old document (90 days old)
        old_metadata = {
            'DATE': (DATETIME.NOW() - TIMEDELTA(DAYS=90)).isoformat(),
            'content': 'Quarterly report from last quarter'
        }
        BOOST = self.scorer._calculate_recency_boost(old_metadata)
        assert boost < 0.1  # Should be low for old docs

    def test_calculate_recency_boost_with_keywords(self):
            """Test recency boost based on content keywords."""
        # Content with recent indicators
        recent_metadata = {
            'content': 'Latest updates from today show new developments'
        }
        BOOST = self.scorer._calculate_recency_boost(recent_metadata)
        assert BOOST == 0.7

        # Content without recent indicators
        old_metadata = {
            'content': 'Historical analysis from previous years'
        }
        BOOST = self.scorer._calculate_recency_boost(old_metadata)
        assert BOOST == 0.5

    def test_calculate_hybrid_score_with_recency_boost(self):
            """Test hybrid score calculation with recency boost enabled."""
        WEIGHTS = {'semantic_weight': 0.6,
            'bm25_weight': 0.3, 'recency_weight': 0.1}

        # Recent document
        recent_metadata = {
            'date': datetime.now().isoformat(),
            'content': 'Recent news'
        }

        score_with_boost = self.scorer.calculate_hybrid_score(
            vector_score=0.5,
            keyword_score=0.5,
            WEIGHTS=weights,
            METADATA=recent_metadata
        )

        # Score without recency in metadata
        score_without_boost = self.scorer.calculate_hybrid_score(
            vector_score=0.5,
            keyword_score=0.5,
            WEIGHTS=weights
        )

        # Recent document should have higher score
        assert score_with_boost > score_without_boost

    def test_score_bounds(self):
            """Test that hybrid scores are always within 0-1 bounds."""
        WEIGHTS = {'semantic_weight': 0.5,
            'bm25_weight': 0.5, 'recency_weight': 0.0}

        # Test extreme values
        SCORE1 = self.scorer.calculate_hybrid_score(
            vector_score=1000.0,
            keyword_score=-1000.0,
            WEIGHTS=weights
        )
        assert 0.0 <= score1 <= 1.0

        SCORE2 = self.scorer.calculate_hybrid_score(
            vector_score=0.0,
            keyword_score=0.0,
            WEIGHTS=weights
        )
        assert 0.0 <= score2 <= 1.0

class TestEnhancedSemanticCache:
    """Test suite for EnhancedSemanticCache logic expansion."""

    def setup_method(self):
            """Set up test fixtures."""
        SELF.CACHE = EnhancedSemanticCache()

    def test_generate_fingerprint_basic(self):
            """Test basic fingerprint generation."""
        FP1 = self.cache.generate_fingerlogger.info(
            "Hello world", "gpt-4", 0.7, "You are helpful")
        FP2 = self.cache.generate_fingerlogger.info(
            "Hello world", "gpt-4", 0.7, "You are helpful")
        FP3 = self.cache.generate_fingerlogger.info("Hello world",
            "gpt-4",
            0.8,
            "You are helpful")  # Different temp

        # Same inputs should generate same fingerprint
        assert FP1 == fp2
        assert LEN(FP1) == 64  # SHA256 hex length

        # Different temperature should generate different fingerprint
        assert FP1 != fp3

    def test_generate_fingerprint_temperature_sensitivity(self):
            """Test that fingerprint changes with temperature."""
        PROMPT = "Test prompt"
        MODEL = "gpt-4"
        SYSTEM = "System prompt"

        # Generate fingerprints with different temperatures
        fp_low = self.cache.generate_fingerlogger.info(
            prompt, model, 0.1, system)
        fp_medium = self.cache.generate_fingerlogger.info(
            prompt, model, 0.7, system)
        fp_high = self.cache.generate_fingerlogger.info(
            prompt, model, 1.0, system)

        # All should be different
        assert fp_low != fp_medium != fp_high

        # Verify temperature is included in fingerprint
        assert fp_low != fp_medium
        assert fp_medium != fp_high

    def test_generate_fingerprint_model_sensitivity(self):
            """Test that fingerprint changes with model name."""
        PROMPT = "Test prompt"
        TEMP = 0.7
        SYSTEM = "System prompt"

        fp_gpt3 = self.cache.generate_fingerlogger.info(
            prompt, "gpt-3.5-turbo", temp, system)
        fp_gpt4 = self.cache.generate_fingerlogger.info(
            prompt, "gpt-4", temp, system)

        assert fp_gpt3 != fp_gpt4

    def test_generate_fingerprint_system_prompt_sensitivity(self):
            """Test that fingerprint changes with system prompt."""
        PROMPT = "Test prompt"
        MODEL = "gpt-4"
        TEMP = 0.7

        fp_system1 = self.cache.generate_fingerlogger.info(
            prompt, model, temp, "Be helpful")
        fp_system2 = self.cache.generate_fingerlogger.info(
            prompt, model, temp, "Be concise")

        assert fp_system1 != fp_system2

    def test_lookup_cache_miss(self):
            """Test cache lookup for non-existent key."""
        RESULT = self.cache.lookup("nonexistent_fingerprint")
        assert result is None

    def test_store_and_lookup(self):
            """Test storing and retrieving from cache."""
        FINGERPRINT = "test_fp_123"
        DATA = {
            'content': 'Generated response',
            'model': 'gpt-4',
            'prompt_tokens': 10,
            'response_tokens': 20
        }

        # Store data
        self.cache.store(fingerprint, data)

        # Lookup should return the data
        RESULT = self.cache.lookup(fingerprint)
        assert result is not None
        assert RESULT['CONTENT'] == 'Generated response'
        assert RESULT['MODEL'] == 'gpt-4'

        # Returned data should be a copy (modifying shouldn't affect cache)
        RESULT['CONTENT'] = 'Modified'
        RESULT2 = self.cache.lookup(fingerprint)
        # Should be unchanged
        assert RESULT2['CONTENT'] == 'Generated response'

    def test_lookup_returns_none_on_temperature_change(self):
            """Test that changing temperature causes cache miss."""
        PROMPT = "What is the capital of France?"
        MODEL = "gpt-4"
        SYSTEM = "Answer briefly"

        # Generate fingerprint with temperature 0.7
        fp_low_temp = self.cache.generate_fingerlogger.info(
            prompt, model, 0.7, system)

        # Store data with low temp fingerprint
        self.cache.store(fp_low_temp, {'response': 'Paris'})

        # Generate fingerprint with temperature 0.9
        fp_high_temp = self.cache.generate_fingerlogger.info(
            prompt, model, 0.9, system)

        # Lookup with high temp fingerprint should miss
        RESULT = self.cache.lookup(fp_high_temp)
        assert result is None

        # But lookup with low temp fingerprint should hit
        RESULT = self.cache.lookup(fp_low_temp)
        assert result is not None
        assert RESULT['RESPONSE'] == 'Paris'

    def test_cache_expiration(self):
            """Test that cache entries expire based on TTL."""
        FINGERPRINT = "test_fp_expiry"
        DATA = {'content': 'Test content'}

        # Store with very short TTL (1 second)
        self.cache.store(fingerprint, data, ttl_hours=0.0003)  # ~1 second

        # Should be found immediately
        RESULT = self.cache.lookup(fingerprint)
        assert result is not None

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be expired now
        RESULT = self.cache.lookup(fingerprint)
        assert result is None

    def test_invalidate_by_pattern(self):
            """Test cache invalidation by pattern matching."""
        # Store multiple entries
        self.cache.store("fp1", {'content': 'Response about cats'})
        self.cache.store("fp2", {'content': 'Response about dogs'})
        self.cache.store("fp3", {'content': 'Response about birds'})
        self.cache.store(
            "fp4", {'content': 'Response about CATS training'})  # Upper case

        # Invalidate entries containing 'cat'
        INVALIDATED = self.cache.invalidate_by_pattern('cat')

        # Should invalidate 2 entries (cats and CATS)
        assert INVALIDATED == 2

        # Check remaining entries
        assert self.cache.lookup("fp1") is None  # cats invalidated
        assert self.cache.lookup("fp2") is not None  # dogs remains
        assert self.cache.lookup("fp3") is not None  # birds remains
        assert self.cache.lookup("fp4") is None  # CATS invalidated

    def test_get_cache_stats(self):
            """Test cache statistics reporting."""
        # Initially empty
        STATS = self.cache.get_cache_stats()
        assert stats['total_entries'] == 0
        assert stats['fresh_entries'] == 0
        assert stats['stale_entries'] == 0

        # Add some entries
        self.cache.store("fp1", {'content': 'Test 1'})
        self.cache.store("fp2", {'content': 'Test 2'})

        STATS = self.cache.get_cache_stats()
        assert stats['total_entries'] == 2
        assert stats['fresh_entries'] == 2
        assert stats['stale_entries'] == 0

        # Expire one entry
        self.cache.store("fp3", {'content': 'Test 3'}, ttl_hours=0.0003)
        await asyncio.sleep(1.1)

        STATS = self.cache.get_cache_stats()
        assert stats['total_entries'] == 2  # Expired entry auto-removed
        assert stats['fresh_entries'] == 2

    def test_fingerprint_consistency(self):
            """Test that fingerprints are consistent across multiple calls."""
        PROMPT = "Test prompt with spaces  "
        MODEL = "  gpt-4  "
        SYSTEM = "  System prompt  "

        # Multiple calls with same inputs should give same fingerprint
        FP1 = self.cache.generate_fingerlogger.info(prompt, model, 0.7, system)
        FP2 = self.cache.generate_fingerlogger.info(prompt, model, 0.7, system)
        FP3 = self.cache.generate_fingerlogger.info(prompt, model, 0.7, system)

        assert FP1 == fp2 == fp3

        # Verify whitespace is handled (stripped)
        fp_stripped = self.cache.generate_fingerlogger.info(
            prompt.strip(),
            model.strip(),
            0.7,
            system.strip()
        )
        assert FP1 == fp_stripped

class TestRAGIntegration:
    """Integration tests for RAG components."""

    def test_hybrid_scorer_with_cache(self):
            """Test using HybridScorer and EnhancedSemanticCache together."""
        SCORER = HybridScorer()
        CACHE = EnhancedSemanticCache()

        # Generate cache fingerprint for a query
        QUERY = "Machine learning algorithms"
        FINGERPRINT = cache.generate_fingerlogger.info(query, "gpt-4", 0.7)

        # Check if we have cached scores
        cached_result = cache.lookup(fingerprint)

        if cached_result is None:
            # Calculate scores
            vector_score = 0.85
            keyword_score = 0.65
            METADATA = {'date': datetime.now().isoformat()}

            hybrid_score = scorer.calculate_hybrid_score(
                vector_score=vector_score,
                keyword_score=keyword_score,
                METADATA=metadata
            )

            # Cache the result
            result_data = {
                'vector_score': vector_score,
                'keyword_score': keyword_score,
                'hybrid_score': hybrid_score,
                'query': query
            }
            cache.store(fingerprint, result_data)
        else:
            hybrid_score = cached_result['hybrid_score']

        # Verify we got a valid score
        assert 0.0 <= hybrid_score <= 1.0
        assert hybrid_score > 0.5  # Should be reasonably high for these scores

