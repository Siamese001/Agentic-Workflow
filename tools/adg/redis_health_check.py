"""Redis Health Check and Auto-start Utility

Ensures Redis server is running and ADG cache is hot for Windsurf workflows.
Provides Windows-specific auto-start capabilities and detailed diagnostics.

Usage:
    python tools/adg/redis_health_check.py [--auto-start]

Exit codes:
    0: Redis is running and ADG cache is HOT
    1: Redis is running but ADG cache is cold/stale
    2: Redis server is down (auto-start attempted if --auto-start)
"""

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "redis_health_check")
_emit_applies_guardrail("p0", "redis_health_check", "p0_governance")
_emit_reads_policy_state("p0", "redis_health_check", "policy_binding")
_emit_snapshots_state("p0", "redis_health_check", "state_snapshot")
emit_replay_key("p0", "redis_health_check")
emit_determinism_digest("p0", "redis_health_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

try:
    import redis
except ImportError:
    print("[Redis Health] ERROR: redis-py not installed. Run: pip install redis")
    sys.exit(2)

logger = logging.getLogger(__name__)

# Import configuration from centralized module
from agentic_core.config.redis_config import (
    get_adg_cache_config,
    get_redis_config,
    get_redis_windows_config,
)


def check_redis_connection(redis_config, adg_config) -> bool:
    """Check if Redis server is responding.

    Args:
        redis_config: Redis connection configuration
        adg_config: ADG cache configuration

    Returns:
        True if Redis is responding, False otherwise

    Raises:
        redis.ConnectionError: If connection fails
        redis.TimeoutError: If connection times out
    """
    r = redis.Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        socket_timeout=redis_config.timeout,
    )
    r.ping()
    return True


def check_adg_cache_health(redis_config, adg_config) -> dict[str, any]:
    """Check ADG cache status in Redis.

    Args:
        redis_config: Redis connection configuration
        adg_config: ADG cache configuration

    Returns:
        Dictionary with 'hot' status, reason, node_count, and timestamp

    Raises:
        redis.ConnectionError: If connection fails
        redis.ResponseError: If Redis command fails
    """
    r = redis.Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        socket_timeout=redis_config.timeout,
    )

    # Get ADG metadata
    meta = r.hgetall("adg:meta")
    if not meta:
        return {"hot": False, "reason": "No ADG metadata found"}

    node_count = int(meta.get(b"node_count", 0))
    timestamp = meta.get(b"timestamp", b"unknown").decode("utf-8")

    # Check node count threshold
    if node_count < adg_config.min_node_count:
        return {
            "hot": False,
            "reason": f"Insufficient nodes: {node_count} < {adg_config.min_node_count}",
            "node_count": node_count,
            "timestamp": timestamp,
        }

    return {
        "hot": True,
        "reason": f"cache HOT: {node_count} nodes, timestamp={timestamp}",
        "node_count": node_count,
        "timestamp": timestamp,
    }


def start_redis_windows() -> bool:
    """Attempt to start Redis on Windows.

    Returns:
        True if Redis was started successfully, False otherwise

    Raises:
        subprocess.TimeoutExpired: If service start times out
        subprocess.CalledProcessError: If service start fails
    """
    windows_config = get_redis_windows_config()

    # Try Windows service first
    print("[Redis Health] Attempting to start Redis service...")
    result = subprocess.run(
        ["sc", "start", "Redis"],
        capture_output=True,
        text=True,
        timeout=windows_config.service_start_timeout,
        check=False,
    )
    if result.returncode == 0:
        print("[Redis Health] ✓ Redis service started")
        time.sleep(windows_config.service_startup_delay)
        return True

    # Try configured Redis installation paths
    for redis_exe in windows_config.installation_paths:
        if Path(redis_exe).exists():
            print(f"[Redis Health] Starting Redis from {redis_exe}...")
            subprocess.Popen([redis_exe], shell=False)
            time.sleep(windows_config.process_startup_delay)
            return True

    print("[Redis Health] Redis executable not found in configured locations")
    return False


def main() -> None:
    """Main health check routine.

    Exit codes:
        0: Redis is running and ADG cache is HOT
        1: Redis is running but ADG cache is cold/stale
        2: Redis server is down
    """
    parser = argparse.ArgumentParser(description="Redis health check for ADG cache")
    parser.add_argument("--auto-start", action="store_true", help="Attempt to auto-start Redis if down")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    redis_config = get_redis_config()
    adg_config = get_adg_cache_config()
    print(f"[Redis Health] Checking {redis_config.host}:{redis_config.port} DB-{redis_config.db}...")

    # Check Redis connection
    try:
        check_redis_connection(redis_config, adg_config)
        print("[Redis Health] ✓ Redis connected")
    except (redis.ConnectionError, redis.TimeoutError) as e:
        print(f"[Redis Health] ✗ Redis server is not responding: {e}")

        if args.auto_start:
            print("[Redis Health] Attempting auto-start...")
            try:
                if start_redis_windows():
                    # Verify connection after start
                    check_redis_connection(redis_config, adg_config)
                    print("[Redis Health] ✓ Redis connection restored")
                else:
                    print("[Redis Health] ✗ Failed to start Redis automatically")
                    sys.exit(2)
            except (redis.ConnectionError, redis.TimeoutError):
                print("[Redis Health] ✗ Redis started but still not responding")
                sys.exit(2)
        else:
            print("[Redis Health] Use --auto-start to attempt automatic start")
            sys.exit(2)

    # Redis is running, check ADG cache
    try:
        r = redis.Redis(
            host=redis_config.host,
            port=redis_config.port,
            db=redis_config.db,
            socket_timeout=redis_config.timeout,
        )
        key_count = r.dbsize()
        print(f"[Redis Health] Found {key_count} keys in DB-{redis_config.db}")
    except redis.RedisError as e:
        print(f"[Redis Health] WARNING: Could not get key count: {e}")
        key_count = 0

    # Check ADG cache health
    try:
        cache_status = check_adg_cache_health(redis_config, adg_config)

        if cache_status["hot"]:
            print(f"[Redis Health] ✓ ADG {cache_status['reason']}")
            drift_score = r.get("adg:drift:score")
            if drift_score:
                print(f"[Redis Health] ✓ Drift score: {drift_score} (run drift_score.py to refresh)")
            sys.exit(0)
        else:
            print(f"[Redis Health] ✗ ADG cache cold: {cache_status['reason']}")
            if args.verbose:
                print("[Redis Health] To refresh ADG cache, run:")
                print("  python tools/adg/adg_redis_ingest.py --force")
            sys.exit(1)
    except redis.RedisError as e:
        print(f"[Redis Health] ERROR: Failed to check ADG cache health: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
