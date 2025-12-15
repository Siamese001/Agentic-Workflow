#!/usr/bin/env python3
"""
Canon Validator Mock Test - Testing the 5-Stage Loop without external APIs

This test verifies the Canon Validator logic works correctly using mock implementations
to avoid API rate limits and quota issues.
"""

import json
import time
import logging
from unittest.mock import Mock, patch
from canon_validator_full import CanonValidator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MockTestRunner")


def create_mock_validator():
    """Create a validator with mocked external dependencies."""
    validator = CanonValidator()
    
    # Mock the LLM client to avoid API calls
    mock_llm_response = {
        "is_valid": True,
        "confidence": 0.9,
        "reason": "Content adheres to architectural principles",
        "applied_rules": ["rule_arch_001"],
        "suggestions": []
    }
    
    validator.llm_client.generate_plan = Mock(return_value=mock_llm_response)
    
    # Mock Redis operations
    validator.redis_index = Mock()
    validator.redis_index.query = Mock(return_value=[])  # Initially no cache hits
    
    # Mock Pinecone operations
    validator.pinecone_index = Mock()
    validator.pinecone_index.query = Mock(return_value={"matches": []})  # Initially no rules
    validator.pinecone_index.upsert = Mock()  # Mock write operations
    
    return validator


def test_five_stage_flow():
    """Test the complete 5-stage flow with mocks."""
    print("\n" + "="*80)
    print("🧪 CANON VALIDATOR MOCK TEST - 5-STAGE FLOW")
    print("="*80)
    
    validator = create_mock_validator()
    
    # Test 1: First validation (should go through all stages)
    print("\n📝 Test 1: First Validation (Cold Start)")
    print("-" * 60)
    
    content = "The cognitive plane must be separate from the data plane."
    result1 = validator.validate(content, "test")
    
    print(f"✓ Valid: {result1['is_valid']}")
    print(f"✓ Confidence: {result1['confidence']}")
    print(f"✓ Latency: {result1['latency_ms']:.2f}ms")
    
    # Verify stages
    assert result1['stages']['embedding']['status'] == 'success'
    assert result1['stages']['l1_cache']['status'] == 'miss'
    assert result1['stages']['l2_retrieval']['status'] == 'no_rules'
    assert result1['stages']['consensus']['status'] == 'success'
    assert result1['stages']['write_back']['status'] == 'success'
    
    print("✅ All 5 stages executed correctly")
    
    # Test 2: Simulate cache hit
    print("\n📝 Test 2: Simulated Cache Hit")
    print("-" * 60)
    
    # Mock a cache hit
    mock_cached = Mock()
    mock_cached.distance = 0.01
    mock_cached.is_valid = "True"
    mock_cached.confidence = "0.9"
    mock_cached.reason = "Cached validation result"
    mock_cached.timestamp = "2025-01-01T00:00:00"
    
    validator.redis_index.query = Mock(return_value=[mock_cached])
    
    result2 = validator.validate(content, "test_cached")
    
    print(f"✓ Valid: {result2['is_valid']}")
    print(f"✓ Source: {result2['source']}")
    print(f"✓ Latency: {result2['latency_ms']:.2f}ms")
    
    # Should be from cache
    assert result2['source'] == 'l1_cache'
    assert result2['stages']['l1_cache']['status'] == 'hit'
    # Note: Still need embedding generation for cache lookup, so latency is higher than pure cache hit
    assert result2['latency_ms'] < 1000  # Should be faster than full validation
    
    print("✅ Cache hit working correctly")
    
    # Test 3: L2 retrieval with rules
    print("\n📝 Test 3: L2 Retrieval with Rules")
    print("-" * 60)
    
    # Reset cache to miss
    validator.redis_index.query = Mock(return_value=[])
    
    # Mock L2 rules
    mock_rule = {
        "id": "rule_001",
        "content": "Cognitive and data planes must be separate",
        "score": 0.85,
        "metadata": {"type": "architecture"}
    }
    
    validator.pinecone_index.query = Mock(return_value={"matches": [mock_rule]})
    
    result3 = validator.validate("Cognitive and data should be separated", "test_l2")
    
    print(f"✓ Valid: {result3['is_valid']}")
    print(f"✓ Rules found: {result3['stages']['l2_retrieval']['rules_found']}")
    print(f"✓ Applied rules: {result3.get('applied_rules', [])}")
    
    assert result3['stages']['l2_retrieval']['status'] == 'success'
    assert result3['stages']['l2_retrieval']['rules_found'] == 1
    
    print("✅ L2 retrieval working correctly")
    
    print("\n" + "="*80)
    print("✅ ALL MOCK TESTS PASSED")
    print("="*80)
    print("\nThe 5-stage validation loop is working correctly:")
    print("1. ✓ Embedding generation")
    print("2. ✓ L1 semantic cache check")
    print("3. ✓ L2 canon retrieval")
    print("4. ✓ Consensus validation")
    print("5. ✓ Meta-learning write-back")


def test_error_handling():
    """Test error handling in the validator."""
    print("\n" + "="*80)
    print("🛡️ ERROR HANDLING TEST")
    print("="*80)
    
    validator = create_mock_validator()
    
    # Test L1 cache error
    print("\n📝 Testing L1 Cache Error Handling")
    validator.redis_index.query = Mock(side_effect=Exception("Redis connection failed"))
    
    result = validator.validate("Test content", "error_test")
    
    # Should continue despite L1 error
    assert result['stages']['l1_cache']['status'] == 'miss'
    assert result['stages']['consensus']['status'] == 'success'
    
    print("✅ Graceful handling of L1 cache error")
    
    # Test L2 error
    print("\n📝 Testing L2 Memory Error Handling")
    validator.pinecone_index.query = Mock(side_effect=Exception("Pinecone connection failed"))
    
    result = validator.validate("Test content", "error_test2")
    
    # Should continue despite L2 error
    assert result['stages']['l2_retrieval']['status'] == 'no_rules'
    assert result['stages']['consensus']['status'] == 'success'
    
    print("✅ Graceful handling of L2 memory error")
    
    print("\n✅ Error handling working correctly")


if __name__ == "__main__":
    print("🚀 Starting Canon Validator Mock Tests")
    print("Testing core logic without external API dependencies...")
    
    test_five_stage_flow()
    test_error_handling()
    
    print("\n✨ All mock tests completed successfully!")
    print("The Canon Validator implementation is working as designed.")
