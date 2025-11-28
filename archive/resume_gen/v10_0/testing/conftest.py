# File: conftest.py
# Shared pytest fixtures and configuration for v10.0 test suite

import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "asyncio: marks tests as async tests"
    )


# ============================================================================
# SHARED FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data"""
    temp_dir = tempfile.mkdtemp(prefix="v10_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_config():
    """Sample configuration object"""
    config = MagicMock()
    
    # Logging
    config.logging_config.log_level = "INFO"
    config.logging_config.log_file = "./logs/test.log"
    
    # Redis
    config.redis_config.host = "localhost"
    config.redis_config.port = 6379
    config.redis_config.db = 0
    
    # Caching
    config.caching_config.enable_llm_caching = True
    config.caching_config.cache_ttl_seconds = 3600
    config.caching_config.cache_db = 1
    
    # Performance
    config.performance_config.enable_async_llm = True
    config.performance_config.max_concurrent_llm_calls = 10
    config.performance_config.llm_timeout_seconds = 30
    
    # Cost
    config.cost_config.cost_ceiling_per_workflow = 5.0
    config.cost_config.cost_ceiling_per_agent = 0.5
    config.cost_config.enable_cost_tracking = True
    config.cost_config.cost_warning_threshold = 4.0
    
    # Batch
    config.batch_config.max_parallel_workers = 4
    config.batch_config.enable_circuit_breaker = True
    config.batch_config.circuit_breaker_failure_threshold = 3
    
    # Meta-learning
    config.meta_loop_config.enable_meta_learning = True
    config.meta_loop_config.max_meta_replan_loops = 3
    config.meta_loop_config.feedback_log_path = "./logs/feedback.jsonl"
    config.meta_loop_config.preference_log_path = "./logs/preference.jsonl"
    config.meta_loop_config.proposed_rules_path = "./logs/proposed_rules.jsonl"
    
    # File paths
    config.file_paths.default_job_input = "job_input.json"
    config.file_paths.default_master_resume = "master_resume.json"
    
    return config


@pytest.fixture
def mock_redis_client():
    """Mock Redis client with common operations"""
    redis_mock = MagicMock()
    
    # Storage for mocked data
    redis_mock._data = {}
    
    def mock_get(key):
        return redis_mock._data.get(key)
    
    def mock_set(key, value):
        redis_mock._data[key] = value
        return True
    
    def mock_setex(key, time, value):
        redis_mock._data[key] = value
        return True
    
    def mock_delete(key):
        if key in redis_mock._data:
            del redis_mock._data[key]
        return True
    
    def mock_incr(key):
        current = redis_mock._data.get(key, b'0')
        new_val = int(current) + 1
        redis_mock._data[key] = str(new_val).encode()
        return new_val
    
    redis_mock.get.side_effect = mock_get
    redis_mock.set.side_effect = mock_set
    redis_mock.setex.side_effect = mock_setex
    redis_mock.delete.side_effect = mock_delete
    redis_mock.incr.side_effect = mock_incr
    
    return redis_mock


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic async client"""
    client = AsyncMock()
    
    client.chat_completion_async.return_value = {
        "content": "Mocked response from Claude",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50
        }
    }
    
    return client


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini async client"""
    client = AsyncMock()
    
    client.chat_completion_async.return_value = {
        "content": {"result": "Mocked response from Gemini"},
        "usage": {
            "input_tokens": 80,
            "output_tokens": 40
        }
    }
    
    return client


@pytest.fixture
def sample_job_data():
    """Sample job posting data"""
    return {
        "company_name": "Tech Innovators Inc",
        "job_title": "Senior AI Engineer",
        "location": "San Francisco, CA",
        "job_description": """
We are seeking a Senior AI Engineer to join our team.
You will build cutting-edge machine learning systems at scale.

Requirements:
- 5+ years of ML experience
- Python, TensorFlow, PyTorch
- Experience with LLMs and agentic AI
- Strong communication skills

What we offer:
- Competitive salary ($180k-$250k)
- Remote-friendly
- Equity package
- Health benefits
""",
        "required_skills": [
            "Python",
            "TensorFlow",
            "PyTorch",
            "LangChain",
            "Agentic AI"
        ]
    }


@pytest.fixture
def sample_resume_data():
    """Sample resume data"""
    return {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "555-0123",
        "location": "Seattle, WA",
        "summary": "Experienced AI engineer with 7 years building ML systems",
        "experience": [
            {
                "company": "AI Startup",
                "title": "Senior ML Engineer",
                "duration": "2020-2024",
                "location": "Seattle, WA",
                "bullets": [
                    "Built production ML pipelines processing 10M+ events/day",
                    "Deployed 15+ models to production with 99.9% uptime",
                    "Led team of 5 engineers building recommendation system",
                    "Reduced inference latency by 60% through optimization"
                ]
            },
            {
                "company": "Big Tech Corp",
                "title": "ML Engineer",
                "duration": "2017-2020",
                "location": "San Francisco, CA",
                "bullets": [
                    "Developed NLP models for search ranking",
                    "Improved search relevance by 25%",
                    "Collaborated with 10+ cross-functional teams"
                ]
            }
        ],
        "education": [
            {
                "school": "Stanford University",
                "degree": "MS Computer Science",
                "year": 2017
            },
            {
                "school": "MIT",
                "degree": "BS Computer Science",
                "year": 2015
            }
        ],
        "skills": [
            "Python", "TensorFlow", "PyTorch", "Scikit-learn",
            "LangChain", "Docker", "Kubernetes", "AWS"
        ]
    }


@pytest.fixture
def mock_validation_results():
    """Mock validation results"""
    return {
        "overall_passed": True,
        "checks": [
            {
                "name": "bullet_count",
                "passed": True,
                "details": "5 bullets per experience"
            },
            {
                "name": "quantification",
                "passed": True,
                "details": "All bullets quantified"
            },
            {
                "name": "action_verbs",
                "passed": True,
                "details": "Strong action verbs used"
            }
        ]
    }


@pytest.fixture
def mock_failed_validation_results():
    """Mock failed validation results"""
    return {
        "overall_passed": False,
        "checks": [
            {
                "name": "bullet_count",
                "passed": False,
                "details": "Only 3 bullets, expected 5"
            },
            {
                "name": "quantification",
                "passed": False,
                "details": "Missing quantification in 2 bullets"
            },
            {
                "name": "action_verbs",
                "passed": True,
                "details": "Strong action verbs used"
            }
        ]
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@pytest.fixture
def create_temp_json_file(tmp_path):
    """Factory to create temporary JSON files"""
    def _create_file(data, filename="test.json"):
        file_path = tmp_path / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return str(file_path)
    return _create_file


@pytest.fixture
def create_temp_log_file(tmp_path):
    """Factory to create temporary log files"""
    def _create_file(lines, filename="test.log"):
        file_path = tmp_path / filename
        with open(file_path, 'w') as f:
            for line in lines:
                f.write(line + '\n')
        return str(file_path)
    return _create_file


# ============================================================================
# ASYNC TEST UTILITIES
# ============================================================================

@pytest.fixture
def async_test_timeout():
    """Default timeout for async tests"""
    return 5.0  # 5 seconds


@pytest.fixture
def mock_asyncio_gather():
    """Mock asyncio.gather for testing parallel execution"""
    async def _gather(*tasks):
        results = []
        for task in tasks:
            if callable(task):
                result = await task()
            else:
                result = await task
            results.append(result)
        return results
    return _gather


# ============================================================================
# COST TRACKING UTILITIES
# ============================================================================

@pytest.fixture
def mock_cost_summary():
    """Mock cost summary data"""
    return {
        "total_workflow_cost": 1.25,
        "agent_costs": {
            "StrategyAgent": 0.30,
            "BulletGeneratorAgent": 0.45,
            "CritiqueAgent": 0.25,
            "QAAgent": 0.25
        },
        "warnings": []
    }


@pytest.fixture
def mock_cost_summary_over_ceiling():
    """Mock cost summary exceeding ceiling"""
    return {
        "total_workflow_cost": 6.50,
        "agent_costs": {
            "StrategyAgent": 2.00,
            "BulletGeneratorAgent": 2.50,
            "CritiqueAgent": 1.00,
            "QAAgent": 1.00
        },
        "warnings": ["Cost ceiling exceeded"]
    }


# ============================================================================
# CACHE UTILITIES
# ============================================================================

@pytest.fixture
def mock_cache_stats():
    """Mock cache statistics"""
    return {
        "hits": 25,
        "misses": 15,
        "total_requests": 40,
        "hit_rate_pct": 62.5,
        "total_saved_cost": 0.75
    }


# ============================================================================
# CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_artifacts(tmp_path):
    """Automatically cleanup test artifacts after each test"""
    yield
    # Cleanup any test files created
    if tmp_path.exists():
        try:
            shutil.rmtree(tmp_path)
        except:
            pass


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

@pytest.fixture
def capture_logs(caplog):
    """Fixture to capture and analyze logs"""
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog


# ============================================================================
# MARKERS
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on filename"""
    for item in items:
        # Mark async tests
        if 'async' in item.nodeid.lower():
            item.add_marker(pytest.mark.asyncio)
        
        # Mark integration tests
        if 'integration' in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests
        if 'test_core' in item.nodeid or 'test_agent' in item.nodeid:
            item.add_marker(pytest.mark.unit)
