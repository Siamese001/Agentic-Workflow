# TESTS DEPTH VIOLATION — 2026-01-18 05:21:40
# tests\core\test_semantic_gatekeeper.py was depth 3, MUST be 2.

"""
Test script for Semantic Gatekeeper and Hybrid Semantic Cache

This script tests:
1. Redis connection and index creation
2. Vector embedding generation
3. Pattern storage and retrieval
4. L5 Safety Protocol enforcement
"""
import sys
import time
from typing import Any
from agentic_core.semantic_gatekeeper import SemanticGatekeeper

def test_redis_connection() -> Any:
    """Test basic Redis connectivity."""
    try:
        gatekeeper: Any = SemanticGatekeeper()
        return gatekeeper
    except Exception as e:
        pass
        pass
        pass
        return None

def test_pattern_storage(gatekeeper: Any) -> Any:
    """Test storing and retrieving patterns."""
    safe_action: Any = 'Format code with autopep8'
    safe_code: Any = "def hello():\n    print('Hello World')"
    entry_id: Any = gatekeeper.record_pattern(action=safe_action, code=safe_code, agent_name='StructuralLinter', pattern_type='format', files_touched=3, success=True)
    dangerous_action: Any = 'Encapsulate all globals across entire codebase'
    dangerous_code: Any = "GLOBAL_VAR = 'dangerous'"
    entry_id: Any = gatekeeper.record_pattern(action=dangerous_action, code=dangerous_code, agent_name='ArchitecturalRefactorAgent', pattern_type='refactor', files_touched=686, success=False)
    return (safe_action, dangerous_action)

def test_safety_gate(gatekeeper: Any, safe_action: Any, dangerous_action: Any) -> Any:
    """Test the safety gating functionality."""
    is_safe: Any = gatekeeper.consult_canon(safe_action)
    is_safe: Any = gatekeeper.consult_canon(dangerous_action)
    new_dangerous: Any = 'Refactor 100+ files in single operation'
    is_safe: Any = gatekeeper.consult_canon(new_dangerous)

def test_vector_search(gatekeeper: Any) -> Any:
    """Test vector similarity search."""
    query: Any = 'Format Python code'
    results: Any = gatekeeper._search_similar_patterns(gatekeeper.embed_action(query), threshold=0.5, max_results=5)

def test_safety_stats(gatekeeper: Any) -> Any:
    """Test safety statistics retrieval."""
    stats: Any = gatekeeper.get_safety_stats()
    if 'error' not in stats:
        pass
    else:
        pass

def main() -> Any:
    """Run all tests."""
    gatekeeper: Any = test_redis_connection()
    if not gatekeeper:
        sys.exit(1)
    safe_action, dangerous_action = test_pattern_storage(gatekeeper)
    time.sleep(1)
    test_safety_gate(gatekeeper, safe_action, dangerous_action)
    test_vector_search(gatekeeper)
    test_safety_stats(gatekeeper)
if __name__ == '__main__':
    main()
