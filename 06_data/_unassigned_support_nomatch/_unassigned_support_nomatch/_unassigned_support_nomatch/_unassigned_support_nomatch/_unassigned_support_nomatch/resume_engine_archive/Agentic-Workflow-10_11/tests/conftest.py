"""
Root pytest configuration with centralized fixtures and mock factories.

Provides consistent mocking, test data management, and configuration across all test layers.
Implements session-level fixtures for expensive resources and function-level for isolation.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple, Union
from unittest.mock import Mock, MagicMock, AsyncMock
import json
import uuid
from datetime import datetime, timedelta
import threading
import time

# Import shared fixtures
from tests.shared.fixtures.test_data_fixtures import (
    ResumeTestData, JobDescriptionTestData, WorkflowTestData,
    generate_test_resume, generate_test_job
)


# ---------------------------------------------------------------------------
# Session-level fixtures (expensive, shared across tests)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_session_id():
    """Unique identifier for the test session."""
    return f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def mock_llm_factory():
    """Factory for creating consistent LLM mocks across tests."""
    
    class LLMMockFactory:
        def __init__(self):
            self.call_count = 0
            self.responses = {}
            self.lock = threading.Lock()
        
        def create_mock_llm(self, response_data: Optional[Dict[str, Any]] = None):
            """Create a mock LLM with predefined responses."""
            mock_llm = AsyncMock()
            
            default_responses = {
                "analysis": {
                    "requirements": ["Python", "AWS", "5+ years"],
                    "skills_matched": ["Python", "AWS"],
                    "match_score": 0.75,
                    "confidence": 0.85
                },
                "improvements": {
                    "suggestions": ["Add project metrics", "Highlight leadership"],
                    "priority_areas": ["Experience quantification"]
                },
                "safety_check": {
                    "is_safe": True,
                    "risk_level": "low",
                    "concerns": []
                }
            }
            
            responses = response_data or default_responses
            
            async def mock_generate(prompt: str, **kwargs):
                with self.lock:
                    self.call_count += 1
                
                # Determine response type based on prompt content
                if "analysis" in prompt.lower():
                    return responses["analysis"]
                elif "improvement" in prompt.lower():
                    return responses["improvements"]
                elif "safety" in prompt.lower():
                    return responses["safety_check"]
                else:
                    return responses["analysis"]  # Default
            
            mock_llm.generate = mock_generate
            return mock_llm
        
        def get_call_count(self):
            with self.lock:
                return self.call_count
        
        def reset_call_count(self):
            with self.lock:
                self.call_count = 0
    
    return LLMMockFactory()


@pytest.fixture(scope="session")
def mock_external_services():
    """Session-level mock for external services."""
    
    class ExternalServicesMock:
        def __init__(self):
            self.api_responses = {}
            self.request_log = []
            self.lock = threading.Lock()
        
        def create_api_mock(self, service_name: str, responses: Dict[str, Any]):
            """Create a mock API service."""
            mock_api = Mock()
            
            def mock_request(endpoint: str, data: Dict[str, Any]):
                with self.lock:
                    self.request_log.append({
                        "service": service_name,
                        "endpoint": endpoint,
                        "timestamp": datetime.now(),
                        "data": data
                    })
                
                return responses.get(endpoint, {"status": "success", "data": {}})
            
            mock_api.request = mock_request
            self.api_responses[service_name] = responses
            return mock_api
        
        def get_request_log(self):
            with self.lock:
                return self.request_log.copy()
        
        def clear_request_log(self):
            with self.lock:
                self.request_log.clear()
    
    return ExternalServicesMock()


# ---------------------------------------------------------------------------
# Module-level fixtures (shared within test modules)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mock_memory_store():
    """Mock memory store with thread-safe operations."""
    
    class MockMemoryStore:
        def __init__(self):
            self.data = {}
            self.triplets = {}
            self.lock = threading.RLock()
        
        def store_triplets(self, job_id: str, triplets: List[Dict[str, Any]]):
            with self.lock:
                if job_id not in self.triplets:
                    self.triplets[job_id] = []
                self.triplets[job_id].extend(triplets)
        
        def query_triplets(self, job_id: str) -> List[Dict[str, Any]]:
            with self.lock:
                return self.triplets.get(job_id, []).copy()
        
        def store_data(self, key: str, value: Any):
            with self.lock:
                self.data[key] = value
        
        def get_data(self, key: str) -> Any:
            with self.lock:
                return self.data.get(key)
        
        def clear(self):
            with self.lock:
                self.data.clear()
                self.triplets.clear()
    
    store = MockMemoryStore()
    yield store
    store.clear()  # Cleanup after module


@pytest.fixture(scope="module")
def mock_safety_policy():
    """Mock safety policy with configurable rules."""
    
    class MockSafetyPolicy:
        def __init__(self):
            self.validation_rules = {}
            self.blocked_content = set()
            self.lock = threading.Lock()
        
        def add_rule(self, rule_name: str, rule_func: callable):
            """Add a validation rule."""
            with self.lock:
                self.validation_rules[rule_name] = rule_func
        
        def validate_input(self, content: Dict[str, Any]) -> Dict[str, Any]:
            """Validate input against all rules."""
            with self.lock:
                for rule_name, rule_func in self.validation_rules.items():
                    result = rule_func(content)
                    if not result["is_safe"]:
                        return result
                
                return {"is_safe": True, "risk_level": "low", "violations": []}
        
        def block_content(self, content_signature: str):
            """Add content to blocklist."""
            with self.lock:
                self.blocked_content.add(content_signature)
        
        def is_content_blocked(self, content_signature: str) -> bool:
            """Check if content is blocked."""
            with self.lock:
                return content_signature in self.blocked_content
    
    policy = MockSafetyPolicy()
    
    # Add default rules
    def injection_rule(content: Dict[str, Any]) -> Dict[str, Any]:
        text = str(content).lower()
        if "ignore all instructions" in text:
            return {"is_safe": False, "risk_level": "high", "violations": ["injection_attempt"]}
        return {"is_safe": True}
    
    def pii_rule(content: Dict[str, Any]) -> Dict[str, Any]:
        text = str(content)
        if "@" in text and "." in text:  # Simple email detection
            return {"is_safe": False, "risk_level": "medium", "violations": ["pii_detected"]}
        return {"is_safe": True}
    
    policy.add_rule("injection", injection_rule)
    policy.add_rule("pii", pii_rule)
    
    return policy


# ---------------------------------------------------------------------------
# Function-level fixtures (isolated per test)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_workflow_context():
    """Create a mock workflow context for individual tests."""
    return {
        "workflow_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "start_time": datetime.now(),
        "user_id": f"test_user_{uuid.uuid4().hex[:8]}",
        "configuration": {
            "timeout": 300,
            "retry_count": 3,
            "safety_enabled": True
        }
    }


@pytest.fixture
def temporary_test_data():
    """Provide temporary test data that's cleaned up after each test."""
    temp_data = {}
    
    def add_data(key: str, value: Any):
        temp_data[key] = value
    
    def get_data(key: str) -> Any:
        return temp_data.get(key)
    
    yield {"add": add_data, "get": get_data}
    
    # Cleanup is automatic when temp_data goes out of scope


@pytest.fixture
def performance_tracker():
    """Track performance metrics for individual tests."""
    
    class PerformanceTracker:
        def __init__(self):
            self.timings = {}
            self.counters = {}
        
        def start_timer(self, name: str):
            self.timings[name] = {"start": time.time()}
        
        def end_timer(self, name: str):
            if name in self.timings:
                self.timings[name]["end"] = time.time()
                self.timings[name]["duration"] = (
                    self.timings[name]["end"] - self.timings[name]["start"]
                )
        
        def increment_counter(self, name: str, value: int = 1):
            self.counters[name] = self.counters.get(name, 0) + value
        
        def get_timing(self, name: str) -> Optional[float]:
            return self.timings.get(name, {}).get("duration")
        
        def get_counter(self, name: str) -> int:
            return self.counters.get(name, 0)
        
        def get_summary(self) -> Dict[str, Any]:
            return {
                "timings": {k: v.get("duration") for k, v in self.timings.items() if "duration" in v},
                "counters": self.counters.copy()
            }
    
    tracker = PerformanceTracker()
    yield tracker
    # Performance data is available for test analysis


# ---------------------------------------------------------------------------
# Test data generators
# ---------------------------------------------------------------------------

@pytest.fixture
def test_resume_generator():
    """Generate test resumes with configurable properties."""
    
    def create_resume(
        skills: Optional[List[str]] = None,
        experience_years: Optional[int] = None,
        education_level: str = "bachelor",
        custom_data: Optional[Dict[str, Any]] = None
    ) -> ResumeTestData:
        
        default_skills = ["Python", "SQL", "JavaScript"]
        default_experience = [{"title": "Software Engineer", "years": experience_years or 3}]
        
        return ResumeTestData(
            candidate_name="Test Candidate",
            contact_info={"email": "test@example.com", "phone": "+1-555-0000"},
            experience=default_experience,
            education=[{"degree": education_level.title(), "field": "Computer Science"}],
            skills=skills or default_skills,
            certifications=[],
            projects=[],
            metadata=custom_data or {}
        )
    
    return create_resume


@pytest.fixture
def test_job_generator():
    """Generate test job descriptions with configurable properties."""
    
    def create_job(
        difficulty: str = "medium",
        required_skills: Optional[List[str]] = None,
        experience_years: Optional[int] = None,
        remote: bool = True
    ) -> JobDescriptionTestData:
        
        difficulty_configs = {
            "easy": {"min_exp": 0, "req_skills": ["Python"]},
            "medium": {"min_exp": 3, "req_skills": ["Python", "SQL", "AWS"]},
            "hard": {"min_exp": 7, "req_skills": ["Python", "AWS", "Kubernetes", "Leadership"]}
        }
        
        config = difficulty_configs.get(difficulty, difficulty_configs["medium"])
        
        return JobDescriptionTestData(
            job_id=f"test_job_{difficulty}_{uuid.uuid4().hex[:8]}",
            title=f"Test Position ({difficulty})",
            company="Test Company",
            location="Remote" if remote else "Office",
            requirements=[
                f"{config['min_exp']}+ years experience",
                f"Skills: {', '.join(config['req_skills'])}"
            ],
            responsibilities=["Test responsibilities"],
            qualifications={
                "min_experience_years": experience_years or config["min_exp"],
                "required_skills": required_skills or config["req_skills"],
                "remote_work": remote
            },
            description=f"Test job description for {difficulty} position"
        )
    
    return create_job


# ---------------------------------------------------------------------------
# Mock factories for specific components
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_execution_engine():
    """Create a mock execution engine for L2 testing."""
    
    class MockExecutionEngine:
        def __init__(self):
            self.execution_log = []
            self.failure_simulation = {}
        
        def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
            execution_id = str(uuid.uuid4())
            
            self.execution_log.append({
                "execution_id": execution_id,
                "tool": tool_name,
                "parameters": parameters,
                "timestamp": datetime.now()
            })
            
            # Simulate failures if configured
            if tool_name in self.failure_simulation:
                failure_config = self.failure_simulation[tool_name]
                if failure_config.get("always_fail", False):
                    return {
                        "success": False,
                        "error": failure_config["error"],
                        "execution_id": execution_id
                    }
            
            # Default success response
            return {
                "success": True,
                "data": {"result": f"Mocked {tool_name} result"},
                "execution_id": execution_id,
                "tokens_used": 100
            }
        
        def simulate_failure(self, tool_name: str, error: str, always_fail: bool = False):
            """Configure failure simulation for a tool."""
            self.failure_simulation[tool_name] = {
                "error": error,
                "always_fail": always_fail
            }
        
        def get_execution_log(self) -> List[Dict[str, Any]]:
            return self.execution_log.copy()
        
        def clear_log(self):
            self.execution_log.clear()
    
    return MockExecutionEngine()


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator for L3 testing."""
    
    class MockOrchestrator:
        def __init__(self):
            self.execution_plans = []
            self.node_results = {}
        
        def create_execution_plan(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
            plan_id = str(uuid.uuid4())
            plan = {
                "plan_id": plan_id,
                "steps": steps,
                "created_at": datetime.now(),
                "status": "created"
            }
            self.execution_plans.append(plan)
            return plan
        
        def execute_node(self, node_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
            result = {
                "node_id": node_id,
                "success": True,
                "output": {"processed_data": f"Result for {node_id}"},
                "execution_time": 0.1
            }
            self.node_results[node_id] = result
            return result
        
        def get_plan_history(self) -> List[Dict[str, Any]]:
            return self.execution_plans.copy()
        
        def get_node_results(self) -> Dict[str, Any]:
            return self.node_results.copy()
    
    return MockOrchestrator()


# ---------------------------------------------------------------------------
# Test configuration and utilities
# ---------------------------------------------------------------------------

@pytest.fixture
def test_config():
    """Provide test configuration with sensible defaults."""
    return {
        "execution": {
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 0.1
        },
        "safety": {
            "enable_checks": True,
            "strict_mode": False,
            "max_risk_level": "medium"
        },
        "mocking": {
            "realistic_timing": True,
            "simulate_errors": False,
            "deterministic_responses": True
        },
        "assertions": {
            "strict_equality": True,
            "include_performance_checks": False,
            "detailed_error_messages": True
        }
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatically set up test environment for all tests."""
    # Set consistent random seed for reproducible tests
    import random
    random.seed(42)
    
    # Configure logging for tests
    import logging
    logging.getLogger().setLevel(logging.WARNING)
    
    yield
    
    # Cleanup after test
    pass


# ---------------------------------------------------------------------------
# Pytest configuration and markers
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests across components"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end workflow tests"
    )
    config.addinivalue_line(
        "markers", "golden: Golden dataset evaluation tests"
    )
    config.addinivalue_line(
        "markers", "stress: Stress and performance tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )
    config.addinivalue_line(
        "markers", "l1: L1 Planning layer tests"
    )
    config.addinivalue_line(
        "markers", "l2: L2 Execution layer tests"
    )
    config.addinivalue_line(
        "markers", "l3: L3 Orchestration layer tests"
    )
    config.addinivalue_line(
        "markers", "l4: L4 Memory/State layer tests"
    )
    config.addinivalue_line(
        "markers", "l5: L5 Safety/Policy layer tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on file location
        file_path = str(item.fspath)
        
        if "L1_planning" in file_path:
            item.add_marker(pytest.mark.l1)
        elif "L2_execution" in file_path:
            item.add_marker(pytest.mark.l2)
        elif "L3_orchestration" in file_path:
            item.add_marker(pytest.mark.l3)
        elif "L4_memory_state" in file_path:
            item.add_marker(pytest.mark.l4)
        elif "L5_safety_policy" in file_path:
            item.add_marker(pytest.mark.l5)
        elif "e2e" in file_path:
            item.add_marker(pytest.mark.e2e)
        elif "golden" in file_path:
            item.add_marker(pytest.mark.golden)
        elif "stress" in file_path:
            item.add_marker(pytest.mark.stress)
            item.add_marker(pytest.mark.slow)
        
        # Add unit/integration markers based on directory
        if "unit/" in file_path:
            item.add_marker(pytest.mark.unit)
        elif "integration/" in file_path:
            item.add_marker(pytest.mark.integration)
