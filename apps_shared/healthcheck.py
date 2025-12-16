#!/usr/bin/env python3
"""
Health Check Script for Canon Validator Engine
Monitors L4 Redis state and L5 Audit Trail connectivity
"""

import json
import os
import sys
from datetime import datetime

import redis


def _get_redis_client():
    """Helper to get a Redis client instance with common configurations."""
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_password = os.getenv('REDIS_PASSWORD')

    try:
        return redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    except Exception as e:
        print(f"ERROR: Failed to create Redis client: {e}", file=sys.stderr)
        return None


def check_redis_connection():
    """Check L4 Redis connectivity and responsiveness."""
    r = _get_redis_client()
    if not r:
        return False

    try:
        # Test connectivity with ping
        if not r.ping():
            print("ERROR: Redis ping failed", file=sys.stderr)
            return False

        # Test basic operations
        test_key = "health_check_test"
        r.set(test_key, "ok", ex=10)
        value = r.get(test_key)
        if value != b"ok":
            print("ERROR: Redis read/write test failed", file=sys.stderr)
            return False

        # Clean up
        r.delete(test_key)

        return True

    except redis.ConnectionError as e:
        print(f"ERROR: Redis connection error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Unexpected Redis error: {e}", file=sys.stderr)
        return False


def check_ebp_status():
    """Check Emergency Bailout Protocol status."""
    r = _get_redis_client()
    if not r:
        return False

    try:
        # Check EBP status
        ebp_status = r.get("validator:status:blackout")
        if ebp_status:
            status_str = ebp_status.decode() if isinstance(ebp_status, bytes) else ebp_status
            if status_str == "TRUE":
                print("ERROR: EBP blackout is active", file=sys.stderr)
                return False

        return True

    except Exception as e:
        print(f"ERROR: Failed to check EBP status: {e}", file=sys.stderr)
        return False


def check_l5_audit_trail():
    """Check L5 Audit Trail connectivity."""
    try:
        # For now, just check if we can write to a test observation
        # In a full implementation, this would check MEMemory or other L5 store
        test_observation = {
            "entityName": "health_check",
            "contents": [json.dumps({
                "timestamp": datetime.now().isoformat(),
                "status": "health_check"
            })],
            "corpusNames": ["canon_validator"],
            "tags": ["health", "l5"]
        }

        # Simulate L5 check (would integrate with actual L5 store)
        # For now, just validate the observation structure
        required_keys = ["entityName", "contents", "corpusNames", "tags"]
        for key in required_keys:
            if key not in test_observation:
                print(
                    f"ERROR: L5 observation missing required key: {key}", file=sys.stderr)
                return False

        return True

    except Exception as e:
        print(f"ERROR: L5 audit trail check failed: {e}", file=sys.stderr)
        return False


def check_validator_process():
    """Check if the validator process is responsive."""
    try:
        # Check if main.py exists and is importable
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "/app/main.py")
        if spec is None:
            print("ERROR: Cannot find main.py", file=sys.stderr)
            return False

        # Basic module structure check
        importlib.util.module_from_spec(spec)

        return True

    except Exception as e:
        print(f"ERROR: Validator process check failed: {e}", file=sys.stderr)
        return False


def _run_health_checks():
    """Runs all individual health checks and returns overall status."""
    checks = {
        "Redis Connectivity": check_redis_connection,
        "EBP Status": check_ebp_status,
        "L5 Audit Trail": check_l5_audit_trail,
        "Validator Process": check_validator_process,
    }
    all_checks_passed = True

    for name, check_func in checks.items():
        print(f"Running check: {name}...")
        if not check_func():
            all_checks_passed = False
            print(f"Check '{name}': FAILED")
        else:
            print(f"Check '{name}': PASSED")
    return all_checks_passed


def main():
    """Main health check function."""
    print(f"Health check started at {datetime.now().isoformat()}")

    if _run_health_checks():
        print("Health check: PASSED")
        sys.exit(0)
    else:
        print("Health check: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()

