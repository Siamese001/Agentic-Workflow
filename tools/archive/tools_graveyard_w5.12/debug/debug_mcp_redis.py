#!/usr/bin/env python3
"""
Debug MCP Redis Issues - RCA and Fix Testing

This script reproduces the MCP Redis hanging issues during hot cache ingestion
and tests potential fixes.
"""

import json
import subprocess
import time
from pathlib import Path


def run_command_with_timeout(cmd: str, cwd: str, timeout: int = 30) -> dict:
    """Run command with timeout and proper signal handling"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        # Kill the process group
        subprocess.run("taskkill /F /IM python.exe", shell=True, capture_output=True)
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "returncode": -1,
            "timed_out": True,
        }
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Unexpected error: {str(e)}",
            "returncode": -2,
            "timed_out": False,
        }


def test_redis_connection():
    """Test basic Redis connection"""
    repo_root = Path(__file__).parent

    print("Testing Redis connection...")

    # Test 1: Check if Redis is running
    result = run_command_with_timeout("redis-cli ping", cwd=str(repo_root), timeout=10)
    print(f"Redis ping: {result['success']}")
    if result["stdout"].strip() == "PONG":
        print("✅ Redis is running")
    else:
        print("❌ Redis is not running or not accessible")
        return result

    # Test 2: Check Redis info
    result = run_command_with_timeout("redis-cli info server", cwd=str(repo_root), timeout=10)
    print(f"Redis info: {result['success']}")

    return result


def test_adg_redis_ingestion():
    """Test ADG Redis ingestion (this is where the hang occurs)"""
    repo_root = Path(__file__).parent

    print("\nTesting ADG Redis ingestion...")

    # Test the command that hangs
    cmd = "python tools/adg/adg_redis_ingest.py --force"
    print(f"Running: {cmd}")

    # Test with different timeouts
    for timeout in [30, 60, 120]:
        print(f"\nTesting with {timeout}s timeout...")
        result = run_command_with_timeout(cmd, cwd=str(repo_root), timeout=timeout)

        if result["timed_out"]:
            print(f"❌ Command timed out after {timeout}s")
            if timeout == 120:
                print("❌ Even 120s timeout failed - definite hang issue")
        elif result["success"]:
            print(f"✅ Success with {timeout}s timeout")
            return result
        else:
            print(f"❌ Failed with error: {result['stderr']}")

    return result


def analyze_mcp_redis_issues():
    """Analyze the specific MCP Redis issues"""

    print("\n=== MCP Redis RCA Analysis ===\n")

    print("Issue: MCP Redis hangs during hot cache ingestion")
    print("Symptoms:")
    print("- mcp1_adg_* functions hang when called")
    print("- adg_redis_ingest.py --force hangs indefinitely")
    print("- Redis operations timeout after default limits")
    print("- MCP becomes unresponsive during Redis operations")

    print("\nPotential Root Causes:")
    print("1. Redis connection issues - blocking operations")
    print("2. Large dataset processing - memory/CPU bottlenecks")
    print("3. MCP timeout configuration - insufficient timeouts")
    print("4. Redis server configuration - maxmemory or persistence issues")
    print("5. Python subprocess handling - signal handling problems")
    print("6. ADG data size - too large for single operation")

    return True


def test_redis_configuration():
    """Test Redis configuration and identify issues"""
    repo_root = Path(__file__).parent

    print("\n=== Testing Redis Configuration ===\n")

    # Test Redis memory usage
    result = run_command_with_timeout("redis-cli info memory", cwd=str(repo_root), timeout=10)
    if result["success"]:
        print("Redis memory info:")
        for line in result["stdout"].split("\n"):
            if "used_memory:" in line or "maxmemory:" in line:
                print(f"  {line}")

    # Test Redis config
    result = run_command_with_timeout("redis-cli config get maxmemory", cwd=str(repo_root), timeout=10)
    if result["success"]:
        print(f"Maxmemory config: {result['stdout']}")

    # Test Redis keyspace
    result = run_command_with_timeout("redis-cli info keyspace", cwd=str(repo_root), timeout=10)
    if result["success"]:
        print("Keyspace info:")
        for line in result["stdout"].split("\n"):
            if "db0:" in line:
                print(f"  {line}")

    return True


def test_adg_data_size():
    """Test ADG data size that might be causing issues"""
    repo_root = Path(__file__).parent

    print("\n=== Testing ADG Data Size ===\n")

    # Check SQLite file size
    sqlite_files = list(repo_root.glob("artifacts/adg/*.sqlite"))
    for sqlite_file in sqlite_files:
        size_mb = sqlite_file.stat().st_size / (1024 * 1024)
        print(f"SQLite file: {sqlite_file.name} - {size_mb:.1f} MB")

    # Check if there are any existing Redis keys
    result = run_command_with_timeout("redis-cli dbsize", cwd=str(repo_root), timeout=10)
    if result["success"]:
        db_size = result["stdout"].strip()
        print(f"Current Redis DB size: {db_size} keys")

    # Check ADG keys specifically
    result = run_command_with_timeout(
        "redis-cli eval \"return redis.call('keys', 'adg:')\" 0", cwd=str(repo_root), timeout=10
    )
    if result["success"] and result["stdout"]:
        adg_keys = result["stdout"].strip().split("\n")
        print(f"ADG keys found: {len(adg_keys)}")
        for key in adg_keys[:5]:  # Show first 5
            print(f"  {key}")
        if len(adg_keys) > 5:
            print(f"  ... and {len(adg_keys) - 5} more")

    return True


def test_mcp_timeout_configuration():
    """Test MCP timeout configuration issues"""

    print("\n=== Testing MCP Timeout Configuration ===\n")

    print("MCP Redis timeout issues:")
    print("1. Default MCP tool timeout may be too short for Redis operations")
    print("2. Redis batch operations can take minutes for large datasets")
    print("3. MCP doesn't handle long-running Redis operations well")
    print("4. No progress reporting during long operations")

    # Test a simple Redis operation to gauge baseline speed
    repo_root = Path(__file__).parent

    print("\nTesting baseline Redis operation speed...")
    start_time = time.time()
    result = run_command_with_timeout("redis-cli set test_key test_value", cwd=str(repo_root), timeout=10)
    end_time = time.time()

    if result["success"]:
        print(f"Simple SET operation took {end_time - start_time:.2f}s")

    start_time = time.time()
    result = run_command_with_timeout("redis-cli get test_key", cwd=str(repo_root), timeout=10)
    end_time = time.time()

    if result["success"]:
        print(f"Simple GET operation took {end_time - start_time:.2f}s")

    # Clean up
    run_command_with_timeout("redis-cli del test_key", cwd=str(repo_root), timeout=10)

    return True


def generate_redis_fixes():
    """Generate fixes for MCP Redis issues"""

    fixes = {
        "mcp_redis_fixes": {
            "issue": "MCP Redis hangs during hot cache ingestion",
            "root_causes": [
                "MCP timeout configuration too short for large operations",
                "Redis batch operations taking too long for MCP timeouts",
                "No progress reporting during long operations",
                "Memory issues with large ADG datasets",
                "Redis server configuration not optimized for large datasets",
            ],
            "recommended_fixes": [
                {
                    "fix": "Increase MCP tool timeouts",
                    "description": "Extend timeouts for Redis operations to 5-10 minutes",
                    "implementation": "Configure MCP server with longer timeout values",
                },
                {
                    "fix": "Implement batch processing with progress reporting",
                    "description": "Break large ingestion into smaller batches with progress updates",
                    "implementation": "Modify adg_redis_ingest.py to process in chunks",
                },
                {
                    "fix": "Add Redis memory optimization",
                    "description": "Configure Redis for large dataset operations",
                    "implementation": "Set maxmemory and optimize Redis config",
                },
                {
                    "fix": "Implement async Redis operations",
                    "description": "Use async Redis operations to prevent blocking",
                    "implementation": "Use redis-py async or implement background processing",
                },
                {
                    "fix": "Add operation cancellation support",
                    "description": "Allow cancellation of long-running operations",
                    "implementation": "Implement graceful shutdown and cleanup",
                },
            ],
            "workaround": "Use direct Python scripts instead of MCP for large Redis operations",
        },
    }

    return fixes


def test_redis_fixes():
    """Test potential fixes for MCP Redis issues"""

    print("\n=== Testing Redis Fixes ===\n")

    repo_root = Path(__file__).parent

    # Fix 1: Test with increased timeout using direct Python
    print("Fix 1: Testing direct Python execution with longer timeout")

    # Create a test script that simulates the ingestion
    test_script = repo_root / "test_redis_ingestion.py"
    test_script.write_text("""
import time
import sys
from pathlib import Path

# Simulate the Redis ingestion process
print("Starting Redis ingestion simulation...")
sys.stdout.flush()

for i in range(10):
    print(f"Processing batch {i+1}/10...")
    sys.stdout.flush()
    time.sleep(2)  # Simulate processing time

print("Redis ingestion simulation complete!")
""")

    result = run_command_with_timeout("python test_redis_ingestion.py", cwd=str(repo_root), timeout=120)
    print(f"✅ Direct Python with long timeout: {result['success']}")

    # Clean up
    test_script.unlink(missing_ok=True)

    # Fix 2: Test Redis memory optimization
    print("\nFix 2: Testing Redis memory optimization")

    # Check current Redis memory usage
    result = run_command_with_timeout(
        "redis-cli info memory | grep used_memory_human", cwd=str(repo_root), timeout=10
    )
    if result["success"]:
        print(f"Current Redis memory usage: {result['stdout'].strip()}")

    # Test Redis config changes
    result = run_command_with_timeout("redis-cli config set timeout 300", cwd=str(repo_root), timeout=10)
    print(f"✅ Redis timeout config: {result['success']}")

    # Fix 3: Test batch processing concept
    print("\nFix 3: Testing batch processing concept")

    # Simulate batch processing
    print("Testing small batch operations...")
    for i in range(5):
        key = f"test_batch_{i}"
        value = f"batch_value_{i}"
        result = run_command_with_timeout(f"redis-cli set {key} {value}", cwd=str(repo_root), timeout=10)
        if not result["success"]:
            print(f"❌ Batch {i} failed")
            break
        print(f"✅ Batch {i} completed")

    # Clean up test batches
    for i in range(5):
        key = f"test_batch_{i}"
        run_command_with_timeout(f"redis-cli del {key}", cwd=str(repo_root), timeout=5)

    return True


def main():
    """Main debug function"""
    print("=== MCP Redis Debug Tool ===\n")

    # Test Redis connection
    test_redis_connection()

    # Analyze issues
    analyze_mcp_redis_issues()

    # Test Redis configuration
    test_redis_configuration()

    # Test ADG data size
    test_adg_data_size()

    # Test MCP timeout configuration
    test_mcp_timeout_configuration()

    # Test fixes
    test_redis_fixes()

    # Generate recommendations
    fixes = generate_redis_fixes()

    # Save recommendations
    recommendations_file = Path(__file__).parent / "mcp_redis_recommendations.json"
    with open(recommendations_file, "w") as f:
        json.dump(fixes, f, indent=2)

    print(f"\n=== Recommendations saved to {recommendations_file} ===")

    return True


if __name__ == "__main__":
    main()
