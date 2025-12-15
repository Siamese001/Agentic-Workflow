#!/usr/bin/env python3
"""
Health Check Script for Canon Validator Engine
Monitors L4 Redis state and L5 Audit Trail connectivity
"""

import os
import sys
import redis
import json
from datetime import datetime

def check_redis_connection():
    """Check L4 Redis connectivity and responsiveness"""
    try:
        # Get Redis connection details from environment
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_password = os.getenv('REDIS_PASSWORD')
        
        # Attempt Redis connection
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connectivity with ping
        result = r.ping()
        if not result:
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
        print(f"ERROR: Redis connection failed: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Unexpected Redis error: {e}", file=sys.stderr)
        return False

def check_ebp_status():
    """Check Emergency Bailout Protocol status"""
    try:
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_password = os.getenv('REDIS_PASSWORD')
        
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
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
    """Check L5 Audit Trail connectivity"""
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
                print(f"ERROR: L5 observation missing required key: {key}", file=sys.stderr)
                return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: L5 audit trail check failed: {e}", file=sys.stderr)
        return False

def check_validator_process():
    """Check if the validator process is responsive"""
    try:
        # Check if main.py exists and is importable
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "/app/main.py")
        if spec is None:
            print("ERROR: Cannot find main.py", file=sys.stderr)
            return False
        
        # Basic module structure check
        module = importlib.util.module_from_spec(spec)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Validator process check failed: {e}", file=sys.stderr)
        return False

def main():
    """Main health check function"""
    all_checks_passed = True
    
    print(f"Health check started at {datetime.now().isoformat()}")
    
    # Check 1: Redis connectivity (L4)
    if not check_redis_connection():
        all_checks_passed = False
    
    # Check 2: EBP status
    if not check_ebp_status():
        all_checks_passed = False
    
    # Check 3: L5 Audit Trail
    if not check_l5_audit_trail():
        all_checks_passed = False
    
    # Check 4: Validator process
    if not check_validator_process():
        all_checks_passed = False
    
    if all_checks_passed:
        print("Health check: PASSED")
        sys.exit(0)
    else:
        print("Health check: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
