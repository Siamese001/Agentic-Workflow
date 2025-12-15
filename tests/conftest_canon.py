#!/usr/bin/env python3
"""
Simplified conftest for Canon Validator Engine tests
"""

import pytest
import json
from unittest.mock import Mock
from pathlib import Path


@pytest.fixture
def mock_llm_response():
    """Standard mock LLM response for validation"""
    return {
        "status": "valid",
        "reasoning": "Code complies with all 50 keys",
        "confidence": 0.95,
        "applied_rules": ["rule_001", "rule_002"]
    }


@pytest.fixture
def mock_violation_response():
    """Standard mock LLM response for violations"""
    return {
        "status": "rejected",
        "reasoning": "Violates Key 001: Uses unsafe system calls",
        "confidence": 0.98,
        "violation_type": "security"
    }


@pytest.fixture
def mock_repair_response():
    """Standard mock LLM response for repairs"""
    return {
        "code": "import subprocess\n\ndef safe_execute():\n    subprocess.run(['ls', '-la'])"
    }


@pytest.fixture
def mock_validator_with_all_dependencies():
    """Create a fully mocked validator for testing"""
    import sys
    sys.path.append(str(Path(__file__).parent.parent))

    # Mock the dependencies first
    sys.modules['connection_manager'] = Mock()
    sys.modules['llm_client'] = Mock()
    sys.modules['canon_keys'] = Mock()
    sys.modules['redisvl.extensions.llmcache'] = Mock()
    sys.modules['redisvl.extensions.cache.llm'] = Mock()

    from canon_validator import CanonValidator

    validator = CanonValidator()

    # Mock LLM
    validator.llm = Mock()
    validator.llm.generate_plan = Mock()

    # Mock embedding function
    validator.embed_fn = Mock(return_value=[0.1] * 768)

    # Mock Pinecone
    validator.pinecone = Mock()
    validator.pinecone.query = Mock(return_value={'matches': []})
    validator.pinecone.upsert = Mock()

    # Mock Redis cache
    validator.cache = Mock()
    validator.cache.check = Mock(return_value=None)
    validator.cache.store = Mock()

    # Mock connection manager
    validator.cm = Mock()
    validator.cm.get_pinecone_index = Mock(return_value=validator.pinecone)
    validator.cm.get_embedding = Mock(return_value=[0.1] * 768)

    return validator


@pytest.fixture
def sample_violating_code():
    """Sample code that violates canon rules"""
    return """
import os

def execute_user_input(input_str):
    # Violation: Uses os.system with user input
    os.system(input_str)

    # Violation: Bare except clause
    try:
        result = process(input_str)
    except:
        pass

    return result
"""


@pytest.fixture
def sample_compliant_code():
    """Sample code that complies with canon rules"""
    return """
from typing import Optional, Dict, Any
import subprocess
import logging

logger = logging.getLogger(__name__)

def execute_user_input_safely(input_str: str) -> Optional[str]:
    \"\"\"Execute user input safely using subprocess.\"\"\"
    try:
        result = subprocess.run(
            input_str.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error("Command timed out")
        return None
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return None
"""


@pytest.fixture
def mock_mcp_tools():
    """Mock MCP tools for testing"""
    return {
        'read_text_file': Mock(return_value="sample file content"),
        'get_variable_defs': Mock(return_value=json.dumps([
            {"name": "primary-color", "value": "#FF0000",
                "replacement": "tokens.primary-red"},
            {"name": "secondary-color", "value": "#00FF00",
                "replacement": "tokens.primary-green"}
        ])),
        'search_records': Mock(return_value=json.dumps([{
            "metadata": {"replacement_snippet": "tokens.primary-red"}
        }])),
        'edit_file': Mock(return_value={"status": "success", "changes": 1}),
        'commit': Mock(return_value={"status": "success", "commit": "abc123"}),
        'string_set': Mock(return_value="OK"),
        'string_get': Mock(return_value=None),
        'add_observations': Mock(),
        'issues_get_detail': Mock(return_value=json.dumps({
            "id": "ISSUE_001",
            "file_path": "src/example.js",
            "description": "Security vulnerability"
        }))
    }

