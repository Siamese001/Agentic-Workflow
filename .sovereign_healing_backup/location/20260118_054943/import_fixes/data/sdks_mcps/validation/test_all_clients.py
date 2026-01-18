"""Integration Tests for All SDK Clients
Verifies immediate executability and cross-provider compatibility.
"""

#!/usr/bin/env python3
"""Test all SDK client implementations."""

import logging
import os
import sys
from pathlib import Path
from typing import Dict

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from data.sdks_mcps.client_wrappers.anthropic_client import create_anthropic_client
    from agentic_core.L5_safety.guardrails.multi_provider_router_agent import (
        create_multi_provider_router,
    )
    from data.sdks_mcps.client_wrappers.openai_client import create_openai_client
    from data.sdks_mcps.client_wrappers.vertex_client import create_vertex_client
except ImportError as e:
    logger.error(f"Import error: {e}")
    # Define dummy functions if imports fail
    def create_openai_client(): return None
    def create_anthropic_client(): return None
    def create_vertex_client(): return None
    def create_multi_provider_router(): return None

def test_openai_client() -> Dict[str, object]:
    """Test OpenAI client functionality."""
    results = {
        "provider": "OpenAI",
        TESTS_DIR: {},
        "overall": False
    }

    if not os.getenv("OPENAI_API_KEY"):
        results[TESTS_DIR]["initialization"] = {
            "passed": False,
            "error": "OPENAI_API_KEY not set"
        }
        return results

    try:
        # Test client initialization
        client = create_openai_client()
        results[TESTS_DIR]["initialization"] = {"passed": True}

        # Test simple completion
        response = client.chat_completion([
            {"role": "user", "content": "Say 'OpenAI test passed' in 5 words"}
        ], max_tokens=10)

        content = response.choices[0].message.content
        results[TESTS_DIR]["simple_completion"] = {
            "passed": True,
            "response": content,
            "tokens": response.usage.total_tokens
        }

        # Test structured output
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "provider": {"type": "string"}
            },
            "required": ["status"]
        }

        structured = client.structured_completion(
            [{"role": "user", "content": "Return status as 'ok' and provider as 'openai'"}],
            schema
        )

        results[TESTS_DIR]["structured_output"] = {
            "passed": structured["success"],
            "data": structured.get("data"),
            "error": structured.get("error")
        }

        # Test streaming
        chunks = client.stream_completion([
            {"role": "user", "content": "Count from 1 to 3"}
        ])

        results[TESTS_DIR]["streaming"] = {
            "passed": len(chunks) > 0,
            "chunks": len(chunks)
        }

        results["overall"] = all(test["passed"] for test in results[TESTS_DIR].values())

    except Exception as e:
        results[TESTS_DIR]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False

    return results

def test_anthropic_client() -> Dict[str, object]:
    """Test Anthropic client functionality."""
    results = {
        "provider": "Anthropic",
        TESTS_DIR: {},
        "overall": False
    }

    if not os.getenv("ANTHROPIC_API_KEY"):
        results[TESTS_DIR]["initialization"] = {
            "passed": False,
            "error": "ANTHROPIC_API_KEY not set"
        }
        return results

    try:
        # Test client initialization with caching
        client = create_anthropic_client(enable_caching=True)
        results[TESTS_DIR]["initialization"] = {"passed": True}

        # Test simple message
        response = client.message([{
            "role": "user",
            "content": [{"type": "text", "text": "Say 'Anthropic test passed' in 5 words"}]
        }], max_tokens=10)

        content = response.content[0].text if response.content else ""
        results[TESTS_DIR]["simple_message"] = {
            "passed": len(content) > 0,
            "response": content,
            "tokens": response.usage.input_tokens + response.usage.output_tokens
        }

        # Test cached message
        cached_response = client.cached_message(
            [{"role": "user", "content": [{"type": "text", "text": "Return 'cache test'"}]}],
            system=[{"type": "text", "text": "You are a helpful assistant."}],
            cache_system=True
        )

        results[TESTS_DIR]["cached_message"] = {
            "passed": len(cached_response.content) > 0,
            "cache_read_tokens": cached_response.usage.cache_read_input_tokens
        }

        # Test tool use
        tools = [{
            "name": "test_tool",
            "description": "Test tool",
            "input_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}}
            }
        }]

        tool_result = client.tool_use_message(
            [{"role": "user", "content": [{"type": "text", "text": "Use test_tool with message 'hello'"}]}],
            tools
        )

        results[TESTS_DIR]["tool_use"] = {
            "passed": len(tool_result["content"]) > 0 or len(tool_result["tool_calls"]) > 0,
            "tool_calls": len(tool_result["tool_calls"])
        }

        # Test streaming
        chunks = client.stream_message([{
            "role": "user",
            "content": [{"type": "text", "text": "Count from 1 to 3"}]
        }])

        results[TESTS_DIR]["streaming"] = {
            "passed": len(chunks) > 0,
            "chunks": len(chunks)
        }

        results["overall"] = all(test["passed"] for test in results[TESTS_DIR].values())

    except Exception as e:
        results[TESTS_DIR]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False

    return results

def test_vertex_client() -> Dict[str, object]:
    """Test Google Vertex client functionality."""
    results = {
        "provider": "Google Vertex",
        TESTS_DIR: {},
        "overall": False
    }

    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        results[TESTS_DIR]["initialization"] = {
            "passed": False,
            "error": "GOOGLE_CLOUD_PROJECT not set"
        }
        return results

    try:
        # Test client initialization
        client = create_vertex_client(enable_grounding=True)
        results[TESTS_DIR]["initialization"] = {"passed": True}

        # Test simple generation
        response = client.generate_content(
            "Say 'Vertex test passed' in 5 words",
            max_tokens=10
        )

        results[TESTS_DIR]["simple_generation"] = {
            "passed": len(response.text) > 0,
            "response": response.text[:100]
        }

        # Test grounded response
        grounded = client.grounded_response(
            "What is Google Vertex AI?",
            grounding_threshold=0.7
        )

        results[TESTS_DIR]["grounded_response"] = {
            "passed": len(grounded["content"]) > 0,
            "has_grounding": grounded["grounding_metadata"] is not None,
            "grounding_score": grounded["grounding_metadata"]["grounding_score"] if grounded["grounding_metadata"] else None
        }

        # Test safe response
        safe = client.safe_response(
            "Write a professional greeting",
            safety_threshold="BLOCK_NONE"
        )

        results[TESTS_DIR]["safe_response"] = {
            "passed": len(safe["content"]) > 0,
            "safety_ratings": len(safe["safety_ratings"])
        }

        results["overall"] = all(test["passed"] for test in results[TESTS_DIR].values())

    except Exception as e:
        results[TESTS_DIR]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False

    return results

def test_multi_provider_router() -> Dict[str, object]:
    """Test multi-provider router functionality."""
    results = {
        "provider": "Multi-Provider Router",
        TESTS_DIR: {},
        "overall": False
    }

    try:
        # Test router initialization
        router = create_multi_provider_router()
        results[TESTS_DIR]["initialization"] = {"passed": True}

        # Test basic routing
        routing_result = router.chat_completion([
            {"role": "user", "content": "Say 'Router test passed' in 5 words"}
        ], strategy="priority")

        results[TESTS_DIR]["basic_routing"] = {
            "passed": routing_result["success"],
            "provider": routing_result.get("provider"),
            "strategy": routing_result["metadata"]["strategy"]
        }

        # Test failover (simulate by trying all providers)
        failover_result = router.chat_completion([
            {"role": "user", "content": "Simple test message"}
        ], strategy="round_robin")

        results[TESTS_DIR]["failover"] = {
            "passed": failover_result["success"],
            "providers_tried": failover_result["metadata"]["providers_tried"]
        }

        # Test structured output routing
        schema = {
            "type": "object",
            "properties": {"status": {"type": "string"}},
            "required": ["status"]
        }

        structured_result = router.structured_completion(
            [{"role": "user", "content": "Return status as 'ok'"}],
            schema
        )

        results[TESTS_DIR]["structured_routing"] = {
            "passed": structured_result["success"],
            "provider": structured_result.get("provider"),
            "has_data": "structured_data" in structured_result
        }

        # Test router statistics
        stats = router.get_router_stats()
        results[TESTS_DIR]["statistics"] = {
            "passed": "total_requests" in stats,
            "total_requests": stats["total_requests"],
            "success_rate": stats["success_rate"]
        }

        results["overall"] = all(test["passed"] for test in results[TESTS_DIR].values())

    except Exception as e:
        results[TESTS_DIR]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False

    return results

def test_reference_clients() -> Dict[str, object]:
    """Test minimal reference clients."""
    results = {
        "provider": "Reference Clients",
        TESTS_DIR: {},
        "overall": False
    }

    try:
        # Test OpenAI minimal client
        from data.sdks_mcps.reference_clients.minimal_openai import simple_completion

        if os.getenv("OPENAI_API_KEY"):
            openai_result = simple_completion("Say 'minimal test'", "gpt-4o-mini")
            results[TESTS_DIR]["openai_minimal"] = {
                "passed": len(openai_result) > 0,
                "response": openai_result[:50]
            }
        else:
            results[TESTS_DIR]["openai_minimal"] = {
                "passed": False,
                "error": "OPENAI_API_KEY not set"
            }

        # Test Anthropic minimal client
        from data.sdks_mcps.reference_clients.minimal_anthropic import simple_message

        if os.getenv("ANTHROPIC_API_KEY"):
            anthropic_result = simple_message("Say 'minimal test'", "claude-3-5-haiku")
            results[TESTS_DIR]["anthropic_minimal"] = {
                "passed": len(anthropic_result) > 0,
                "response": anthropic_result[:50]
            }
        else:
            results[TESTS_DIR]["anthropic_minimal"] = {
                "passed": False,
                "error": "ANTHROPIC_API_KEY not set"
            }

        # Test Vertex minimal client
        from data.sdks_mcps.reference_clients.minimal_vertex import simple_generation

        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            vertex_result = simple_generation("Say 'minimal test'", "gemini-1.5-flash")
            results[TESTS_DIR]["vertex_minimal"] = {
                "passed": len(vertex_result) > 0,
                "response": vertex_result[:50]
            }
        else:
            results[TESTS_DIR]["vertex_minimal"] = {
                "passed": False,
                "error": "GOOGLE_CLOUD_PROJECT not set"
            }

        results["overall"] = all(
            test.get("passed", False) for test in results[TESTS_DIR].values()
        )

    except Exception as e:
        results[TESTS_DIR]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False

    return results

def main():
    """Run all integration tests."""

    # Check environment

    env_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_CLOUD_PROJECT"]
    for var in env_vars:
        "✅" if os.getenv(var) else "❌"

    # Run tests
    test_results = []

    # Test individual clients
    for test_func in [test_openai_client, test_anthropic_client, test_vertex_client]:
        try:
            result = test_func()
            test_results.append(result)

            "✅" if result["overall"] else "❌"

            for test_name, test_result in result[TESTS_DIR].items():
                if "error" in test_result and not test_result.get("passed", True):
                    logger.error(f"    Failed: {test_name} - {test_result.get('error', 'Unknown error')}")

        except Exception as e:
            logger.error(f"Error processing results: {e}")

    # Test router
    try:
        router_result = test_multi_provider_router()
        test_results.append(router_result)
        "✅" if router_result["overall"] else "❌"

    except Exception as e:
            logger.error(f"Error testing router: {e}")

    # Test reference clients
    try:
        ref_result = test_reference_clients()
        test_results.append(ref_result)
        "✅" if ref_result["overall"] else "❌"

    except Exception as e:
        logger.error(f"Error testing reference clients: {e}")

    # Summary

    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result["overall"])

    if passed_tests == total_tests:
        print(f"✅ All {total_tests} tests passed!")
        return 0
    else:
        print(f"❌ {total_tests - passed_tests} of {total_tests} tests failed")
        return 1

    # Performance summary

    for result in test_results:
        if result["overall"]:
            print(f"  ✅ {result.get('provider', 'Unknown')}")
        else:
            print(f"  ❌ {result.get('provider', 'Unknown')}")

    return 0 if passed_tests == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())