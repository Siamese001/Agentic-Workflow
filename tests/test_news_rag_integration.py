"""
Test Dynamic News RAG Integration with Hardened Outreach Engine
Validates real-time context injection and hyper-personalization
"""
import json
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NewsRAG_Test")


def test_news_rag_pipeline():
    """Test the News RAG pipeline in isolation."""

    logger.info("\n=== Testing News RAG Pipeline ===")

    try:
        from news_rag_pipeline import execute_news_rag

        # Test with mock Redis functions
        mock_redis = {}

        def mock_get(key):
            return mock_redis.get(key)

        def mock_set(key, value):
            mock_redis[key] = value

        # Test 1: Company with news
        result = execute_news_rag(
            company="TechCorp",
            industry="technology",
            redis_get=mock_get,
            redis_set=mock_set,
            logger=logger
        )

        if result.get("status") == "success":
            logger.info("✅ News RAG pipeline executed successfully")
            logger.info(f"   Company: {result.get('company')}")
            logger.info(f"   Industry: {result.get('industry')}")
            logger.info(f"   Insights found: {result.get('insights_count')}")
            logger.info(f"   News available: {result.get('news_available')}")

            # Check if contextual intro was generated
            if result.get("contextual_intro"):
                logger.info(
                    f"   Contextual intro: {result.get('contextual_intro')[:100]}...")

            # Check personalization points
            points = result.get("personalization_points", [])
            if points:
                logger.info(f"   Personalization points: {len(points)}")
                for i, point in enumerate(points[:2], 1):
                    logger.info(f"     {i}. {point}")

            return True
        else:
            logger.error(f"❌ News RAG failed: {result}")
            return False

    except Exception as e:
pass
logger.error(f"❌ News RAG pipeline test failed: {e}")
        return False


def test_news_rag_caching():
    """Test News RAG caching functionality."""

    logger.info("\n=== Testing News RAG Caching ===")

    try:
        from news_rag_pipeline import execute_news_rag

        # Mock Redis with cache tracking
        mock_redis = {}
        cache_hits = 0

        def mock_get(key):
            nonlocal cache_hits
            if key in mock_redis:
                cache_hits += 1
                logger.info(f"🎯 Cache hit for key: {key[:20]}...")
            return mock_redis.get(key)

        def mock_set(key, value):
            mock_redis[key] = value
            logger.info(f"💾 Cached data for key: {key[:20]}...")

        company = "TestCompany"
        industry = "finance"

        # First call - should fetch from API
        logger.info("First call - fetching from API...")
        result1 = execute_news_rag(
            company=company,
            industry=industry,
            redis_get=mock_get,
            redis_set=mock_set,
            logger=logger
        )

        # Second call - should use cache
        logger.info("Second call - using cache...")
        result2 = execute_news_rag(
            company=company,
            industry=industry,
            redis_get=mock_get,
            redis_set=mock_set,
            logger=logger
        )

        # Verify caching worked
        if cache_hits > 0:
            logger.info(f"✅ Caching working: {cache_hits} cache hits")
            return True
        else:
            logger.warning("⚠️ No cache hits detected")
            return False

    except Exception as e:
pass
logger.error(f"❌ News RAG caching test failed: {e}")
        return False


def test_news_rag_outreach_integration():
    """Test News RAG integration with hardened outreach engine."""

    logger.info("\n=== Testing News RAG Outreach Integration ===")

    try:
        from hardened_outreach_engine import execute_hardened_outreach_sequence

        # Mock tools
        tools = {
            'get_current_time': lambda tz: "2025-12-15T14:00:00Z",
            'send_email': lambda **kwargs: f"Email sent to {kwargs.get('recipient', 'unknown')}",
            'add_observations': lambda **kwargs: None,
            'search_records': lambda **kwargs: json.dumps([{"content": "Base template content..."}]),
            'string_get': lambda k: None,
            'string_set': lambda k, v: None,
            'convert_time': lambda s, t, tz: "2025-12-15T10:00:00Z"
        }

        # Mock rate limiting
        from unittest.mock import patch
        with patch('hardened_outreach_engine.execute_temporal_rate_limiting') as mock_rate_limit:
            mock_rate_limit.return_value = {"status": "allowed"}

            # Execute with company info for News RAG
            lead_profile = {
                "company": "InnovateTech",
                "industry": "technology",
                "role": "CTO"
            }

            result = execute_hardened_outreach_sequence(
                lead_timezone="America/New_York",
                lead_profile=lead_profile,
                recipient_email="cto@innovatech.com",
                tools=tools,
                logger=logger
            )

        # Check if News RAG was used
        personalization_source = result.get("personalization_source", "")

        if "NewsRAG" in personalization_source:
            logger.info("✅ News RAG successfully integrated into outreach")
            logger.info(f"   Personalization source: {personalization_source}")
            logger.info(f"   Status: {result.get('status')}")

            # Check cost savings
            cost_savings = result.get("cost_savings", [])
            if any("News RAG" in saving for saving in cost_savings):
                logger.info("✅ News RAG cost saving recorded")

            return True
        else:
            logger.warning(
                f"⚠️ News RAG not used. Source: {personalization_source}")
            logger.info(
                "   This might be due to missing API key or no news found")
            return False

    except Exception as e:
pass
logger.error(f"❌ News RAG outreach integration test failed: {e}")
        return False


def test_news_rag_error_handling():
    """Test News RAG error handling and graceful degradation."""

    logger.info("\n=== Testing News RAG Error Handling ===")

    try:
        from hardened_outreach_engine import execute_hardened_outreach_sequence

        # Mock tools with failing Redis
        tools = {
            'get_current_time': lambda tz: "2025-12-15T14:00:00Z",
            'send_email': lambda **kwargs: f"Email sent to {kwargs.get('recipient', 'unknown')}",
            'add_observations': lambda **kwargs: None,
            'search_records': lambda **kwargs: json.dumps([{"content": "Base template..."}]),
            'string_get': lambda k: None,  # Simulate cache miss
            'string_set': lambda k, v: None,  # Simulate cache failure
            'convert_time': lambda s, t, tz: "2025-12-15T10:00:00Z"
        }

        # Mock rate limiting
        from unittest.mock import patch
        with patch('hardened_outreach_engine.execute_temporal_rate_limiting') as mock_rate_limit:
            mock_rate_limit.return_value = {"status": "allowed"}

            # Execute without BRAVE_API_KEY (simulate missing)
            if os.getenv("BRAVE_SEARCH_API_KEY"):
                del os.environ["BRAVE_SEARCH_API_KEY"]

            result = execute_hardened_outreach_sequence(
                lead_timezone="America/New_York",
                lead_profile={"company": "TestCorp", "industry": "healthcare"},
                recipient_email="test@testcorp.com",
                tools=tools,
                logger=logger
            )

        # System should continue without News RAG
        if result.get("status") in ["SENT_PERSONALIZED", "SENT_TEMPLATE"]:
            logger.info("✅ System gracefully handles News RAG failure")
            logger.info(f"   Fallback status: {result.get('status')}")
            logger.info(
                f"   Personalization source: {result.get('personalization_source')}")
            return True
        else:
            logger.error(
                f"❌ System failed to handle News RAG error: {result.get('status')}")
            return False

    except Exception as e:
pass
logger.error(f"❌ News RAG error handling test failed: {e}")
        return False


def test_news_rag_personalization_quality():
    """Test the quality of News RAG personalization."""

    logger.info("\n=== Testing News RAG Personalization Quality ===")

    try:
        from news_rag_pipeline import execute_news_rag

        # Test with different industries
        test_cases = [
            {"company": "BioPharm", "industry": "healthcare"},
            {"company": "FinTech Solutions", "industry": "finance"},
            {"company": "EcoEnergy", "industry": "energy"},
            {"company": "EduTech", "industry": "education"}
        ]

        quality_scores = []

        for case in test_cases:
            result = execute_news_rag(
                company=case["company"],
                industry=case["industry"],
                redis_get=lambda k: None,
                redis_set=lambda k, v: None,
                logger=logger
            )

            # Score the personalization quality
            score = 0

            # Check for contextual intro
            if result.get("contextual_intro"):
                intro = result["contextual_intro"]
                if case["company"].lower() in intro.lower() or case["industry"].lower() in intro.lower():
                    score += 2
                score += 1  # Has intro

            # Check personalization points
            points = result.get("personalization_points", [])
            if points:
                score += len(points)  # Points for each personalization

                # Bonus for relevant points
                for point in points:
                    if any(word in point.lower() for word in ["congrats", "impressive", "exciting", "smart"]):
                        score += 1

            quality_scores.append(score)
            logger.info(f"   {case['company']}: Score {score}/10")

        # Calculate average quality
        avg_score = sum(quality_scores) / len(quality_scores)

        if avg_score >= 5:
            logger.info(
                f"✅ Good personalization quality: {avg_score:.1f}/10 average")
            return True
        else:
            logger.warning(
                f"⚠️ Low personalization quality: {avg_score:.1f}/10 average")
            return False

    except Exception as e:
pass
logger.error(f"❌ Personalization quality test failed: {e}")
        return False


def main():
    """Run all News RAG integration tests."""
    logger.info("="*60)
    logger.info("DYNAMIC NEWS RAG INTEGRATION TESTS")
    logger.info("="*60)

    results = []

    # Run all tests
    results.append(("News RAG Pipeline", test_news_rag_pipeline()))
    results.append(("News RAG Caching", test_news_rag_caching()))
    results.append(("News RAG Outreach Integration",
                   test_news_rag_outreach_integration()))
    results.append(("News RAG Error Handling", test_news_rag_error_handling()))
    results.append(("News RAG Personalization Quality",
                   test_news_rag_personalization_quality()))

    # Summary
    logger.info("\n" + "="*60)
    logger.info("NEWS RAG INTEGRATION TEST SUMMARY")
    logger.info("="*60)

    passed = sum(1 for _, result in results if result is True)

    for name, result in results:
        if result is True:
            logger.info(f"{name}: ✅ PASS")
        else:
            logger.info(f"{name}: ❌ FAIL")

    logger.info(f"\nTests: {passed}/{len(results)} passed")

    if passed == len(results):
        logger.info("\n🎉 NEWS RAG INTEGRATION COMPLETE!")
        logger.info("   ✅ Real-time news fetching working")
        logger.info("   ✅ Intelligent caching implemented")
        logger.info("   ✅ Hyper-personalization active")
        logger.info("   ✅ Graceful error handling verified")
        logger.info("   ✅ Quality personalization generated")
        logger.info(
            "\n🚀 The outreach engine now has dynamic context awareness!")
        return True
    else:
        logger.error(f"\n💥 {len(results) - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

