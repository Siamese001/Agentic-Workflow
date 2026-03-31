#!/usr/bin/env python3
"""
MCP Redis Wrapper Script

This script provides optimized replacements for problematic MCP Redis operations.
Usage:
    python mcp_redis_wrapper.py status
    python mcp_redis_wrapper.py ingest [--force]
    python mcp_redis_wrapper.py clear
"""

import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_redis_fix import MCPRedisFix

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: mcp_redis_wrapper.py <command> [args]"}))
        sys.exit(1)

    command = sys.argv[1].lower()
    repo_root = Path(__file__).parent
    fix = MCPRedisFix(str(repo_root))

    if command == "status":
        result = fix.test_mcp_redis_functions()
        print(json.dumps(result))

    elif command == "ingest":
        force = "--force" in sys.argv
        result = fix.run_adg_ingestion_optimized(force=force)
        print(json.dumps(result))

    elif command == "clear":
        result = fix.clear_redis_cache()
        print(json.dumps(result))

    elif command == "optimize":
        result = fix.optimize_redis_config()
        print(json.dumps(result))

    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
