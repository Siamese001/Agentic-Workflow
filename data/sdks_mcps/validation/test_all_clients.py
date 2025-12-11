"""Integration Tests for All SDK Clients
Verifies immediate executability and cross-provider compatibility.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, object, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from data.sdks_mcps.client_wrappers.openai_client import create_openai_client
    from data.sdks_mcps.client_wrappers.anthropic_client import create_anthropic_client
    from data.sdks_mcps.client_wrappers.vertex_client import create_vertex_client
    from data.sdks_mcps.client_wrappers.multi_provider_router import create_multi_provider_router
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the data/sdks_mcps/ directory")


def test_openai_client() -> Dict[str, object]:
    """Test OpenAI client functionality."""
    results = {
        "provider": "OpenAI",
        "tests": {},
        "overall": False
    }
    
    if not os.getenv("OPENAI_API_KEY"):
        results["tests"]["initialization"] = {
            "passed": False,
            "error": "OPENAI_API_KEY not set"
        }
        return results
    
    try:
        # Test client initialization
        client = create_openai_client()
        results["tests"]["initialization"] = {"passed": True}
        
        # Test simple completion
        response = client.chat_completion([
            {"role": "user", "content": "Say 'OpenAI test passed' in 5 words"}
        ], max_tokens=10)
        
        content = response.choices[0].message.content
        results["tests"]["simple_completion"] = {
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
        
        results["tests"]["structured_output"] = {
            "passed": structured["success"],
            "data": structured.get("data"),
            "error": structured.get("error")
        }
        
        # Test streaming
        chunks = client.stream_completion([
            {"role": "user", "content": "Count from 1 to 3"}
        ])
        
        results["tests"]["streaming"] = {
            "passed": len(chunks) > 0,
            "chunks": len(chunks)
        }
        
        results["overall"] = all(test["passed"] for test in results["tests"].values())
        
    except Exception as e:
        results["tests"]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False
    
    return results


def test_anthropic_client() -> Dict[str, object]:
    """Test Anthropic client functionality."""
    results = {
        "provider": "Anthropic",
        "tests": {},
        "overall": False
    }
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        results["tests"]["initialization"] = {
            "passed": False,
            "error": "ANTHROPIC_API_KEY not set"
        }
        return results
    
    try:
        # Test client initialization with caching
        client = create_anthropic_client(enable_caching=True)
        results["tests"]["initialization"] = {"passed": True}
        
        # Test simple message
        response = client.message([{
            "role": "user",
            "content": [{"type": "text", "text": "Say 'Anthropic test passed' in 5 words"}]
        }], max_tokens=10)
        
        content = response.content[0].text if response.content else ""
        results["tests"]["simple_message"] = {
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
        
        results["tests"]["cached_message"] = {
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
        
        results["tests"]["tool_use"] = {
            "passed": len(tool_result["content"]) > 0 or len(tool_result["tool_calls"]) > 0,
            "tool_calls": len(tool_result["tool_calls"])
        }
        
        # Test streaming
        chunks = client.stream_message([{
            "role": "user", 
            "content": [{"type": "text", "text": "Count from 1 to 3"}]
        }])
        
        results["tests"]["streaming"] = {
            "passed": len(chunks) > 0,
            "chunks": len(chunks)
        }
        
        results["overall"] = all(test["passed"] for test in results["tests"].values())
        
    except Exception as e:
        results["tests"]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False
    
    return results


def test_vertex_client() -> Dict[str, object]:
    """Test Google Vertex client functionality."""
    results = {
        "provider": "Google Vertex",
        "tests": {},
        "overall": False
    }
    
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        results["tests"]["initialization"] = {
            "passed": False,
            "error": "GOOGLE_CLOUD_PROJECT not set"
        }
        return results
    
    try:
        # Test client initialization
        client = create_vertex_client(enable_grounding=True)
        results["tests"]["initialization"] = {"passed": True}
        
        # Test simple generation
        response = client.generate_content(
            "Say 'Vertex test passed' in 5 words",
            max_tokens=10
        )
        
        results["tests"]["simple_generation"] = {
            "passed": len(response.text) > 0,
            "response": response.text[:100]
        }
        
        # Test grounded response
        grounded = client.grounded_response(
            "What is Google Vertex AI?",
            grounding_threshold=0.7
        )
        
        results["tests"]["grounded_response"] = {
            "passed": len(grounded["content"]) > 0,
            "has_grounding": grounded["grounding_metadata"] is not None,
            "grounding_score": grounded["grounding_metadata"]["grounding_score"] if grounded["grounding_metadata"] else None
        }
        
        # Test safe response
        safe = client.safe_response(
            "Write a professional greeting",
            safety_threshold="BLOCK_NONE"
        )
        
        results["tests"]["safe_response"] = {
            "passed": len(safe["content"]) > 0,
            "safety_ratings": len(safe["safety_ratings"])
        }
        
        results["overall"] = all(test["passed"] for test in results["tests"].values())
        
    except Exception as e:
        results["tests"]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False
    
    return results


def test_multi_provider_router() -> Dict[str, object]:
    """Test multi-provider router functionality."""
    results = {
        "provider": "Multi-Provider Router",
        "tests": {},
        "overall": False
    }
    
    try:
        # Test router initialization
        router = create_multi_provider_router()
        results["tests"]["initialization"] = {"passed": True}
        
        # Test basic routing
        routing_result = router.chat_completion([
            {"role": "user", "content": "Say 'Router test passed' in 5 words"}
        ], strategy="priority")
        
        results["tests"]["basic_routing"] = {
            "passed": routing_result["success"],
            "provider": routing_result.get("provider"),
            "strategy": routing_result["metadata"]["strategy"]
        }
        
        # Test failover (simulate by trying all providers)
        failover_result = router.chat_completion([
            {"role": "user", "content": "Simple test message"}
        ], strategy="round_robin")
        
        results["tests"]["failover"] = {
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
        
        results["tests"]["structured_routing"] = {
            "passed": structured_result["success"],
            "provider": structured_result.get("provider"),
            "has_data": "structured_data" in structured_result
        }
        
        # Test router statistics
        stats = router.get_router_stats()
        results["tests"]["statistics"] = {
            "passed": "total_requests" in stats,
            "total_requests": stats["total_requests"],
            "success_rate": stats["success_rate"]
        }
        
        results["overall"] = all(test["passed"] for test in results["tests"].values())
        
    except Exception as e:
        results["tests"]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False
    
    return results


def test_reference_clients() -> Dict[str, object]:
    """Test minimal reference clients."""
    results = {
        "provider": "Reference Clients",
        "tests": {},
        "overall": False
    }
    
    try:
        # Test OpenAI minimal client
        from data.sdks_mcps.reference_clients.minimal_openai import simple_completion
        
        if os.getenv("OPENAI_API_KEY"):
            openai_result = simple_completion("Say 'minimal test'", "gpt-4o-mini")
            results["tests"]["openai_minimal"] = {
                "passed": len(openai_result) > 0,
                "response": openai_result[:50]
            }
        else:
            results["tests"]["openai_minimal"] = {
                "passed": False,
                "error": "OPENAI_API_KEY not set"
            }
        
        # Test Anthropic minimal client
        from data.sdks_mcps.reference_clients.minimal_anthropic import simple_message
        
        if os.getenv("ANTHROPIC_API_KEY"):
            anthropic_result = simple_message("Say 'minimal test'", "claude-3-5-haiku")
            results["tests"]["anthropic_minimal"] = {
                "passed": len(anthropic_result) > 0,
                "response": anthropic_result[:50]
            }
        else:
            results["tests"]["anthropic_minimal"] = {
                "passed": False,
                "error": "ANTHROPIC_API_KEY not set"
            }
        
        # Test Vertex minimal client
        from data.sdks_mcps.reference_clients.minimal_vertex import simple_generation
        
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            vertex_result = simple_generation("Say 'minimal test'", "gemini-1.5-flash")
            results["tests"]["vertex_minimal"] = {
                "passed": len(vertex_result) > 0,
                "response": vertex_result[:50]
            }
        else:
            results["tests"]["vertex_minimal"] = {
                "passed": False,
                "error": "GOOGLE_CLOUD_PROJECT not set"
            }
        
        results["overall"] = all(
            test.get("passed", False) for test in results["tests"].values()
        )
        
    except Exception as e:
        results["tests"]["error"] = {"passed": False, "error": str(e)}
        results["overall"] = False
    
    return results


def main():
    """Run all integration tests."""
    print("🧪 Running SDK Integration Tests...")
    print("=" * 60)
    
    # Check environment
    print("🔧 Environment Check:")
    env_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_CLOUD_PROJECT"]
    for var in env_vars:
        status = "✅" if os.getenv(var) else "❌"
        print(f"   {status} {var}")
    print()
    
    # Run tests
    test_results = []
    
    print("📊 Testing Clients:")
    
    # Test individual clients
    for test_func in [test_openai_client, test_anthropic_client, test_vertex_client]:
        try:
            result = test_func()
            test_results.append(result)
            
            status = "✅" if result["overall"] else "❌"
            print(f"   {status} {result['provider']}")
            
            for test_name, test_result in result["tests"].items():
                if "error" in test_result and not test_result.get("passed", True):
                    print(f"      ❌ {test_name}: {test_result.get('error', 'Failed')}")
                    
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    # Test router
    try:
        router_result = test_multi_provider_router()
        test_results.append(router_result)
        status = "✅" if router_result["overall"] else "❌"
        print(f"   {status} {router_result['provider']}")
    except Exception as e:
        print(f"   ❌ Router test failed: {e}")
    
    # Test reference clients
    try:
        ref_result = test_reference_clients()
        test_results.append(ref_result)
        status = "✅" if ref_result["overall"] else "❌"
        print(f"   {status} {ref_result['provider']}")
    except Exception as e:
        print(f"   ❌ Reference clients test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result["overall"])
    
    print(f"📈 Test Summary: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("   SDKs are ready for production use.")
        print("   data/sdks_mcps/ confirmed as single source of truth.")
    else:
        print("⚠️  SOME TESTS FAILED - Check configuration and try again.")
        print("   Missing API keys will cause test failures.")
    
    # Performance summary
    print(f"\n⏱️  Performance Summary:")
    for result in test_results:
        if result["overall"]:
            print(f"   ✅ {result['provider']}: Functional")
        else:
            print(f"   ❌ {result['provider']}: Issues detected")
    
    return 0 if passed_tests == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
