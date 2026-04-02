#!/usr/bin/env python3
"""
MCP GitKraken Wrapper Script

This script provides drop-in replacements for the problematic MCP GitKraken functions.
Usage:
    python mcp_git_wrapper.py add <file1> [file2] ...
    python mcp_git_wrapper.py commit "<message>"
    python mcp_git_wrapper.py status
"""

import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_gitkraken_fix import MCPGitKrakenFix

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: mcp_git_wrapper.py <command> [args]"}))
        sys.exit(1)

    command = sys.argv[1].lower()
    repo_root = Path(__file__).parent
    fix = MCPGitKrakenFix(str(repo_root))

    if command == "add":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: mcp_git_wrapper.py add <file1> [file2] ..."}))
            sys.exit(1)

        files = sys.argv[2:]
        result = fix.smart_add(files)
        print(json.dumps(result))

    elif command == "commit":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: mcp_git_wrapper.py commit \"message\""}))
            sys.exit(1)

        message = sys.argv[2]
        result = fix.smart_commit(message)
        print(json.dumps(result))

    elif command == "commit-safe":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: mcp_git_wrapper.py commit-safe \"message\""}))
            sys.exit(1)

        message = sys.argv[2]
        result = fix.safe_commit_with_fallback(message)
        print(json.dumps(result))

    elif command == "status":
        result = fix.run_git_command("git status")
        print(json.dumps(result))

    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
