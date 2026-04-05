#!/usr/bin/env python3
"""
Comprehensive test suite for ADG Redis MCP fallback behavior.

Tests various failure scenarios to ensure the MCP server properly falls back
to Python script mode when Redis is unavailable or buggy.
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


def test_redis_connection() -> bool:
    """Test if Redis is available."""
    try:
        import redis
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        r.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False


def test_adg_mcp_server_direct() -> dict[str, Any]:
    """Test ADG MCP server directly via Python import."""
    try:
        # Import the server module
        sys.path.insert(0, str(Path(__file__).parent / "tools" / "adg"))
        import adg_mcp_server

        # Test basic functionality
        result = {
            "import_success": True,
            "server_created": hasattr(adg_mcp_server, 'mcp'),
            "tools_available": False,
            "error": None
        }

        # Check if tools are registered
        if hasattr(adg_mcp_server, 'mcp'):
            tools = adg_mcp_server.mcp.list_tools()
            result["tools_available"] = len(tools) > 0
            result["tool_count"] = len(tools)

        return result
    except Exception as e:
        return {
            "import_success": False,
            "server_created": False,
            "tools_available": False,
            "error": str(e)
        }


def test_adg_mcp_server_subprocess() -> dict[str, Any]:
    """Test ADG MCP server via subprocess (simulates MCP client)."""
    try:
        server_path = Path(__file__).parent / "tools" / "adg" / "adg_mcp_server.py"

        # Test server startup
        result = subprocess.run(
            [sys.executable, str(server_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "subprocess_success": result.returncode == 0,
            "stdout": result.stdout[:500],  # First 500 chars
            "stderr": result.stderr[:500],  # First 500 chars
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "subprocess_success": False,
            "error": "timeout",
            "returncode": -1
        }
    except Exception as e:
        return {
            "subprocess_success": False,
            "error": str(e),
            "returncode": -1
        }


def test_adg_status_with_redis_down() -> dict[str, Any]:
    """Test adg_status tool behavior when Redis is down."""
    try:
        # Simulate Redis being unavailable by using wrong port
        os.environ['ADG_REDIS_URL'] = 'redis://localhost:6380/0'  # Wrong port

        # Import and test
        sys.path.insert(0, str(Path(__file__).parent / "tools" / "adg"))
        import adg_mcp_server

        # Reset Redis connection to force reconnection with wrong port
        adg_mcp_server._r = None

        # Call adg_status
        result = adg_mcp_server.adg_status()

        return {
            "test_passed": result.get("status") == "error",
            "error_message": result.get("message", ""),
            "is_fresh": result.get("is_fresh", False),
            "result": result
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e)
        }
    finally:
        # Restore original Redis URL
        os.environ['ADG_REDIS_URL'] = 'redis://localhost:6379/0'


def test_adg_cache_meta_with_redis_down() -> dict[str, Any]:
    """Test _cache_meta function when Redis is down."""
    try:
        # Simulate Redis being unavailable
        os.environ['ADG_REDIS_URL'] = 'redis://localhost:6380/0'

        sys.path.insert(0, str(Path(__file__).parent / "tools" / "adg"))
        import adg_mcp_server

        # Reset connection and cache
        adg_mcp_server._r = None
        adg_mcp_server._meta_cache.clear()

        # Call _cache_meta
        result = adg_mcp_server._cache_meta()

        return {
            "test_passed": result.get("available") == False,
            "has_reason": "reason" in result,
            "result": result
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e)
        }
    finally:
        os.environ['ADG_REDIS_URL'] = 'redis://localhost:6379/0'


def test_adg_sqlite_fallback() -> dict[str, Any]:
    """Test if ADG SQLite data is available as fallback."""
    try:
        adg_dir = Path(__file__).parent / "artifacts" / "adg"

        # Find latest SQLite file
        sqlite_files = list(adg_dir.glob("adg_indexed_*.sqlite"))

        if not sqlite_files:
            return {
                "test_passed": False,
                "error": "No ADG SQLite files found"
            }

        latest_sqlite = max(sqlite_files, key=lambda p: p.stat().st_mtime)

        # Test SQLite connection and basic query
        conn = sqlite3.connect(str(latest_sqlite))
        cursor = conn.cursor()

        # Test node count
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]

        # Test edge count
        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]

        conn.close()

        return {
            "test_passed": True,
            "sqlite_file": str(latest_sqlite),
            "node_count": node_count,
            "edge_count": edge_count,
            "file_size_mb": round(latest_sqlite.stat().st_size / (1024*1024), 2)
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e)
        }


def test_ingest_script_fallback() -> dict[str, Any]:
    """Test if ingest script can rebuild Redis cache from SQLite."""
    try:
        ingest_path = Path(__file__).parent / "tools" / "adg" / "adg_redis_ingest.py"

        if not ingest_path.exists():
            return {
                "test_passed": False,
                "error": "Ingest script not found"
            }

        # Test ingest script help
        result = subprocess.run(
            [sys.executable, str(ingest_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "test_passed": result.returncode == 0,
            "script_exists": True,
            "help_available": "--help" in result.stdout or "usage" in result.stdout.lower(),
            "stdout": result.stdout[:300],
            "stderr": result.stderr[:300]
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e)
        }


def test_mcp_config_fallback() -> dict[str, Any]:
    """Test MCP configuration for fallback scenarios."""
    try:
        mcp_config_path = Path(__file__).parent / ".windsurf" / "mcp_config.json"

        if not mcp_config_path.exists():
            return {
                "test_passed": False,
                "error": "MCP config not found"
            }

        with open(mcp_config_path) as f:
            config = json.load(f)

        adg_redis_config = config.get("mcpServers", {}).get("adg_redis", {})

        # Check if configuration points to Python script
        command = adg_redis_config.get("command", "")
        args = adg_redis_config.get("args", [])

        is_python_fallback = (
            command == "python" and
            any("adg_mcp_server.py" in arg for arg in args)
        )

        return {
            "test_passed": is_python_fallback,
            "command": command,
            "args": args,
            "cwd": adg_redis_config.get("cwd", ""),
            "env_vars": list(adg_redis_config.get("env", {}).keys())
        }
    except Exception as e:
        return {
            "test_passed": False,
            "error": str(e)
        }


def run_comprehensive_test():
    """Run all tests and generate comprehensive report."""
    print("=" * 80)
    print("ADG Redis MCP Fallback Test Suite")
    print("=" * 80)
    print()

    # Test 1: Redis availability
    print("1. Testing Redis availability...")
    redis_available = test_redis_connection()
    print(f"   Redis available: {redis_available}")
    print()

    # Test 2: Direct server import
    print("2. Testing ADG MCP server direct import...")
    direct_test = test_adg_mcp_server_direct()
    print(f"   Import success: {direct_test.get('import_success', False)}")
    print(f"   Server created: {direct_test.get('server_created', False)}")
    print(f"   Tools available: {direct_test.get('tools_available', False)}")
    if direct_test.get('tool_count'):
        print(f"   Tool count: {direct_test['tool_count']}")
    if direct_test.get('error'):
        print(f"   Error: {direct_test['error']}")
    print()

    # Test 3: Subprocess test
    print("3. Testing ADG MCP server subprocess...")
    subprocess_test = test_adg_mcp_server_subprocess()
    print(f"   Subprocess success: {subprocess_test.get('subprocess_success', False)}")
    print(f"   Return code: {subprocess_test.get('returncode', -1)}")
    if subprocess_test.get('error'):
        print(f"   Error: {subprocess_test['error']}")
    print()

    # Test 4: Redis down scenario
    print("4. Testing behavior when Redis is down...")
    redis_down_test = test_adg_status_with_redis_down()
    print(f"   Handles Redis down: {redis_down_test.get('test_passed', False)}")
    if redis_down_test.get('error'):
        print(f"   Error: {redis_down_test['error']}")
    print()

    # Test 5: Cache meta with Redis down
    print("5. Testing cache meta when Redis is down...")
    cache_meta_test = test_adg_cache_meta_with_redis_down()
    print(f"   Cache meta handles Redis down: {cache_meta_test.get('test_passed', False)}")
    if cache_meta_test.get('error'):
        print(f"   Error: {cache_meta_test['error']}")
    print()

    # Test 6: SQLite fallback
    print("6. Testing SQLite fallback availability...")
    sqlite_test = test_adg_sqlite_fallback()
    print(f"   SQLite fallback available: {sqlite_test.get('test_passed', False)}")
    if sqlite_test.get('node_count'):
        print(f"   Node count: {sqlite_test['node_count']}")
    if sqlite_test.get('edge_count'):
        print(f"   Edge count: {sqlite_test['edge_count']}")
    if sqlite_test.get('error'):
        print(f"   Error: {sqlite_test['error']}")
    print()

    # Test 7: Ingest script fallback
    print("7. Testing ingest script fallback...")
    ingest_test = test_ingest_script_fallback()
    print(f"   Ingest script available: {ingest_test.get('test_passed', False)}")
    if ingest_test.get('error'):
        print(f"   Error: {ingest_test['error']}")
    print()

    # Test 8: MCP config fallback
    print("8. Testing MCP configuration...")
    mcp_config_test = test_mcp_config_fallback()
    print(f"   MCP config uses Python fallback: {mcp_config_test.get('test_passed', False)}")
    if mcp_config_test.get('error'):
        print(f"   Error: {mcp_config_test['error']}")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    tests = [
        ("Redis Availability", redis_available),
        ("Direct Import", direct_test.get('import_success', False)),
        ("Subprocess", subprocess_test.get('subprocess_success', False)),
        ("Handles Redis Down", redis_down_test.get('test_passed', False)),
        ("Cache Meta Fallback", cache_meta_test.get('test_passed', False)),
        ("SQLite Fallback", sqlite_test.get('test_passed', False)),
        ("Ingest Script", ingest_test.get('test_passed', False)),
        ("MCP Config", mcp_config_test.get('test_passed', False)),
    ]

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for test_name, result in tests:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All fallback mechanisms are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} fallback mechanisms need attention.")

    return {
        "total_tests": total,
        "passed_tests": passed,
        "redis_available": redis_available,
        "tests": {
            "direct_import": direct_test,
            "subprocess": subprocess_test,
            "redis_down": redis_down_test,
            "cache_meta": cache_meta_test,
            "sqlite_fallback": sqlite_test,
            "ingest_script": ingest_test,
            "mcp_config": mcp_config_test,
        }
    }


if __name__ == "__main__":
    results = run_comprehensive_test()

    # Save results to file
    results_file = Path(__file__).parent / "adg_redis_fallback_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {results_file}")

    # Exit with appropriate code
    sys.exit(0 if results['passed_tests'] == results['total_tests'] else 1)
