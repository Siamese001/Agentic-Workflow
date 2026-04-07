#!/usr/bin/env python3
"""
Extreme fallback test for ADG Redis MCP.

Tests scenarios where Redis is completely unavailable and the system
must fall back to direct SQLite access or Python script mode.
"""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_adg_source_context_fallback() -> dict[str, Any]:
    """Test adg_source_context which uses SQLite directly (should work even without Redis)."""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "tools" / "adg"))
        import adg_mcp_server

        # Test with a sample edge ID (should exist in most ADG databases)
        result = adg_mcp_server.adg_source_context("1")

        return {
            "test_passed": result.get("status") == "ok",
            "has_provenance": result.get("provenance") == "sqlite",
            "has_data": "data" in result,
            "result": result,
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e),
        }


def test_redis_completely_down() -> dict[str, Any]:
    """Test behavior when Redis is completely down (not just wrong port)."""
    original_url = os.environ.get('ADG_REDIS_URL', 'redis://localhost:6379/0')

    try:
        # Set Redis to completely invalid host
        os.environ['ADG_REDIS_URL'] = 'redis://nonexistent-host:9999/0'

        # Force reimport
        if 'adg_mcp_server' in sys.modules:
            del sys.modules['adg_mcp_server']

        sys.path.insert(0, str(Path(__file__).parent / "tools" / "adg"))
        import adg_mcp_server

        # Reset connection
        adg_mcp_server._r = None
        adg_mcp_server._meta_cache.clear()

        # Test various functions
        status_result = adg_mcp_server.adg_status()
        cache_result = adg_mcp_server._cache_meta()

        # Test SQLite-based function (should still work)
        sqlite_result = adg_mcp_server.adg_source_context("1")

        return {
            "test_passed": (
                status_result.get("status") == "error" and
                cache_result.get("available") == False and
                sqlite_result.get("status") == "ok"
            ),
            "redis_functions_fail": status_result.get("status") == "error",
            "cache_fails": cache_result.get("available") == False,
            "sqlite_functions_work": sqlite_result.get("status") == "ok",
            "status_result": status_result,
            "cache_result": cache_result,
            "sqlite_result": sqlite_result,
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e),
        }
    finally:
        os.environ['ADG_REDIS_URL'] = original_url


def test_mcp_server_without_redis() -> dict[str, Any]:
    """Test MCP server startup and basic operation without Redis."""
    try:
        # Temporarily disable Redis by setting invalid URL
        env = os.environ.copy()
        env['ADG_REDIS_URL'] = 'redis://invalid-host:9999/0'

        server_path = Path(__file__).parent / "tools" / "adg" / "adg_mcp_server.py"

        # Test server startup with invalid Redis
        process = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=str(Path(__file__).parent),
        )

        try:
            # Send a simple tools/list request
            test_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            }

            stdout, stderr = process.communicate(
                input=json.dumps(test_message) + "\n",
                timeout=10,
            )

            # Check if server responds (even with Redis down)
            server_responded = len(stdout) > 0

            # Try to parse response
            try:
                response = json.loads(stdout.strip())
                has_tools = "result" in response
            except Exception:
                has_tools = False

            return {
                "test_passed": server_responded,
                "server_responded": server_responded,
                "has_tools": has_tools,
                "stdout": stdout[:300],
                "stderr": stderr[:300],
                "returncode": process.returncode,
            }
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "test_passed": False,
                "error": "timeout",
                "server_responded": False,
            }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e),
        }


def test_direct_sqlite_access() -> dict[str, Any]:
    """Test direct SQLite access as ultimate fallback."""
    try:
        adg_dir = Path(__file__).parent / "artifacts" / "adg"

        # Find latest SQLite file
        sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite"))

        if not sqlite_files:
            return {
                "test_passed": False,
                "error": "No ADG SQLite files found",
            }

        latest_sqlite = max(sqlite_files, key=lambda p: p.stat().st_mtime)

        # Test comprehensive SQLite access
        conn = sqlite3.connect(str(latest_sqlite))
        cursor = conn.cursor()

        # Test basic queries
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]

        # Test sample node query
        cursor.execute("SELECT * FROM nodes LIMIT 5")
        sample_nodes = cursor.fetchall()

        # Test sample edge query
        cursor.execute("SELECT * FROM edges LIMIT 5")
        sample_edges = cursor.fetchall()

        # Test layer distribution
        cursor.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer")
        layer_distribution = cursor.fetchall()

        conn.close()

        return {
            "test_passed": True,
            "sqlite_file": str(latest_sqlite),
            "node_count": node_count,
            "edge_count": edge_count,
            "sample_nodes": len(sample_nodes),
            "sample_edges": len(sample_edges),
            "layer_count": len(layer_distribution),
            "file_size_mb": round(latest_sqlite.stat().st_size / (1024*1024), 2),
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e),
        }


def test_ingest_with_redis_down() -> dict[str, Any]:
    """Test ingest script behavior when Redis is down."""
    try:
        ingest_path = Path(__file__).parent / "tools" / "adg" / "adg_redis_ingest.py"

        # Set Redis to invalid host
        env = os.environ.copy()
        env['ADG_REDIS_URL'] = 'redis://invalid-host:9999/0'

        # Test ingest script with Redis down
        result = subprocess.run(
            [sys.executable, str(ingest_path), "--force"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=str(Path(__file__).parent),
        )

        # Should fail gracefully with Redis error
        fails_gracefully = (
            result.returncode != 0 and
            ("redis" in result.stderr.lower() or "connection" in result.stderr.lower())
        )

        return {
            "test_passed": fails_gracefully,
            "fails_gracefully": fails_gracefully,
            "returncode": result.returncode,
            "stdout": result.stdout[:300],
            "stderr": result.stderr[:300],
        }
    except subprocess.TimeoutExpired:
        return {
            "test_passed": False,
            "error": "timeout",
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e),
        }


def test_mcp_error_messages() -> dict[str, Any]:
    """Test that MCP error messages are helpful and guide users."""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "tools" / "adg"))
        import adg_mcp_server

        # Test various error scenarios
        error_scenarios = [
            # Test with Redis down
            lambda: adg_mcp_server.adg_status(),
            # Test invalid node
            lambda: adg_mcp_server.adg_node("invalid_node"),
            # Test invalid edge
            lambda: adg_mcp_server.adg_edge_detail("999999"),
        ]

        helpful_errors = []

        for scenario in error_scenarios:
            try:
                result = scenario()
                # Check if error message is helpful
                if result.get("status") == "error":
                    message = result.get("message", "")
                    is_helpful = any(keyword in message.lower() for keyword in [
                        "run:", "python", "ingest", "redis", "unavailable", "not found",
                    ])
                    helpful_errors.append(is_helpful)
                else:
                    helpful_errors.append(True)  # No error is fine
            except Exception:
                helpful_errors.append(False)  # Exception is not helpful

        all_helpful = all(helpful_errors)

        return {
            "test_passed": all_helpful,
            "all_helpful": all_helpful,
            "helpful_count": sum(helpful_errors),
            "total_scenarios": len(helpful_errors),
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e),
        }


def run_extreme_fallback_test():
    """Run extreme fallback tests."""
    print("=" * 80)
    print("ADG Redis MCP Extreme Fallback Test")
    print("=" * 80)
    print()

    # Test 1: SQLite fallback
    print("1. Testing SQLite direct access fallback...")
    sqlite_test = test_direct_sqlite_access()
    print(f"   SQLite direct access: {sqlite_test.get('test_passed', False)}")
    if sqlite_test.get('node_count'):
        print(f"   Nodes available: {sqlite_test['node_count']}")
    if sqlite_test.get('error'):
        print(f"   Error: {sqlite_test['error']}")
    print()

    # Test 2: Source context (SQLite-based)
    print("2. Testing SQLite-based source context...")
    source_test = test_adg_source_context_fallback()
    print(f"   Source context works: {source_test.get('test_passed', False)}")
    print(f"   Uses SQLite: {source_test.get('has_provenance', False)}")
    if source_test.get('error'):
        print(f"   Error: {source_test['error']}")
    print()

    # Test 3: Redis completely down
    print("3. Testing Redis completely down...")
    redis_down_test = test_redis_completely_down()
    print(f"   Handles Redis down: {redis_down_test.get('test_passed', False)}")
    print(f"   Redis functions fail: {redis_down_test.get('redis_functions_fail', False)}")
    print(f"   SQLite functions work: {redis_down_test.get('sqlite_functions_work', False)}")
    if redis_down_test.get('error'):
        print(f"   Error: {redis_down_test['error']}")
    print()

    # Test 4: MCP server without Redis
    print("4. Testing MCP server without Redis...")
    server_test = test_mcp_server_without_redis()
    print(f"   Server responds: {server_test.get('server_responded', False)}")
    print(f"   Has tools: {server_test.get('has_tools', False)}")
    if server_test.get('error'):
        print(f"   Error: {server_test['error']}")
    print()

    # Test 5: Ingest with Redis down
    print("5. Testing ingest script with Redis down...")
    ingest_test = test_ingest_with_redis_down()
    print(f"   Ingest fails gracefully: {ingest_test.get('fails_gracefully', False)}")
    if ingest_test.get('error'):
        print(f"   Error: {ingest_test['error']}")
    print()

    # Test 6: Error message quality
    print("6. Testing error message quality...")
    error_test = test_mcp_error_messages()
    print(f"   Helpful error messages: {error_test.get('all_helpful', False)}")
    print(f"   Helpful count: {error_test.get('helpful_count', 0)}/{error_test.get('total_scenarios', 0)}")
    if error_test.get('error'):
        print(f"   Error: {error_test['error']}")
    print()

    # Summary
    print("=" * 80)
    print("EXTREME FALLBACK SUMMARY")
    print("=" * 80)

    tests = [
        ("SQLite Direct Access", sqlite_test.get('test_passed', False)),
        ("Source Context Fallback", source_test.get('test_passed', False)),
        ("Redis Completely Down", redis_down_test.get('test_passed', False)),
        ("Server Without Redis", server_test.get('server_responded', False)),
        ("Ingest Fails Gracefully", ingest_test.get('fails_gracefully', False)),
        ("Helpful Error Messages", error_test.get('all_helpful', False)),
    ]

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for test_name, result in tests:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")

    print(f"\nOverall: {passed}/{total} extreme fallback tests passed")

    # Critical fallback assessment
    critical_fallbacks = [
        ("SQLite data available", sqlite_test.get('test_passed', False)),
        ("Redis functions fail gracefully", redis_down_test.get('redis_functions_fail', False)),
        ("SQLite functions work", redis_down_test.get('sqlite_functions_work', False)),
        ("Helpful error messages", error_test.get('all_helpful', False)),
    ]

    critical_passed = sum(1 for _, result in critical_fallbacks if result)
    print(f"Critical fallbacks: {critical_passed}/{len(critical_fallbacks)} working")

    if passed >= 5 and critical_passed >= 3:
        print("\n🎉 ADG Redis MCP has robust extreme fallback behavior!")
    elif passed >= 3:
        print(f"\n⚠️  ADG Redis MCP has partial extreme fallback ({critical_passed}/{len(critical_fallbacks)} critical).")
    else:
        print("\n❌ ADG Redis MCP extreme fallback needs significant improvement.")

    return {
        "total_tests": total,
        "passed_tests": passed,
        "critical_fallbacks_working": critical_passed,
        "total_critical_fallbacks": len(critical_fallbacks),
        "tests": {
            "sqlite_test": sqlite_test,
            "source_test": source_test,
            "redis_down_test": redis_down_test,
            "server_test": server_test,
            "ingest_test": ingest_test,
            "error_test": error_test,
        },
    }


if __name__ == "__main__":
    results = run_extreme_fallback_test()

    # Save results to file
    results_file = Path(__file__).parent / "adg_extreme_fallback_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {results_file}")

    # Exit with appropriate code
    sys.exit(0 if results['passed_tests'] >= 5 else 1)
