#!/usr/bin/env python3
"""
Environment setup for sequential thinking prioritization.
Sets system-wide environment variables to influence Windsurf's tool selection.
"""

import os
import sys
from pathlib import Path

def setup_seq_thinking_environment():
    """Setup environment variables to favor sequential thinking."""

    env_vars = {
        # Sequential thinking prioritization
        'SEQUENTIAL_THINKING_ENABLED': 'true',
        'SEQUENTIAL_THINKING_PRIORITY': '1',  # Highest priority
        'SEQUENTIAL_THINKING_AUTO_TRIGGER': 'true',
        'SEQUENTIAL_THINKING_MIN_COMPLEXITY': 'low',
        'SEQUENTIAL_THINKING_MAX_THOUGHTS': '15',
        'SEQUENTIAL_THINKING_TOKEN_BUDGET': '30000',

        # Windsurf tool preferences
        'WINDSURF_TOOL_PREFERENCE': 'sequential-thinking',
        'WINDSURF_MCP_BOOST_MODE': 'enabled',
        'WINDSURF_REASONING_MODE': 'sequential-first',

        # Kimi 2.5 integration
        'KIMI25_SEQUENTIAL_THINKING': 'enabled',
        'KIMI25_REASONING_BOOST': 'high',
        'KIMI25_TOKEN_ALLOCATION': '0.20',  # 20% of context window
        'KIMI25_AUTO_ANALYSIS': 'true',

        # MCP integration
        'MCP_SEQUENTIAL_THINKING_BOOST': 'enabled',
        'MCP_TOOL_ORDERING': 'sequential-priority',
        'MCP_KIMI25_MODE': 'optimized',

        # Performance tuning
        'SEQUENTIAL_THINKING_CACHE_ENABLED': 'true',
        'SEQUENTIAL_THINKING_ASYNC_MODE': 'false',
        'SEQUENTIAL_THINKING_LOG_LEVEL': 'INFO'
    }

    print("Setting up sequential thinking environment variables...")

    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  SET {key}={value}")

    # Verify critical variables
    critical_vars = [
        'SEQUENTIAL_THINKING_ENABLED',
        'SEQUENTIAL_THINKING_PRIORITY',
        'WINDSURF_TOOL_PREFERENCE',
        'KIMI25_SEQUENTIAL_THINKING'
    ]

    print("\nVerifying critical environment variables:")
    all_set = True
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            print(f"  OK {var}={value}")
        else:
            print(f"  MISSING {var} not set")
            all_set = False

    if all_set:
        print("\nSUCCESS All critical environment variables set successfully!")
        print("Sequential thinking prioritization is now active.")
    else:
        print("\nFAILED Some critical variables failed to set.")
        sys.exit(1)

def print_env_status():
    """Print current environment status for sequential thinking."""
    print("\nSequential Thinking Environment Status:")
    print("=" * 50)

    key_vars = [
        'SEQUENTIAL_THINKING_ENABLED',
        'SEQUENTIAL_THINKING_PRIORITY',
        'WINDSURF_TOOL_PREFERENCE',
        'KIMI25_SEQUENTIAL_THINKING',
        'MCP_SEQUENTIAL_THINKING_BOOST'
    ]

    for var in key_vars:
        value = os.environ.get(var, 'not set')
        status = "OK" if value != 'not set' else "MISSING"
        print(f"  {status} {var}: {value}")

def create_env_file():
    """Create a .env file for persistent environment setup."""
    env_file = Path(__file__).parent / ".seq_thinking_env"

    env_content = """# Sequential Thinking Environment Configuration
# Source this file to enable sequential thinking prioritization

# Sequential thinking settings
export SEQUENTIAL_THINKING_ENABLED=true
export SEQUENTIAL_THINKING_PRIORITY=1
export SEQUENTIAL_THINKING_AUTO_TRIGGER=true
export SEQUENTIAL_THINKING_MIN_COMPLEXITY=low
export SEQUENTIAL_THINKING_MAX_THOUGHTS=15
export SEQUENTIAL_THINKING_TOKEN_BUDGET=30000

# Windsurf tool preferences
export WINDSURF_TOOL_PREFERENCE=sequential-thinking
export WINDSURF_MCP_BOOST_MODE=enabled
export WINDSURF_REASONING_MODE=sequential-first

# Kimi 2.5 integration
export KIMI25_SEQUENTIAL_THINKING=enabled
export KIMI25_REASONING_BOOST=high
export KIMI25_TOKEN_ALLOCATION=0.20
export KIMI25_AUTO_ANALYSIS=true

# MCP integration
export MCP_SEQUENTIAL_THINKING_BOOST=enabled
export MCP_TOOL_ORDERING=sequential-priority
export MCP_KIMI25_MODE=optimized
"""

    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"\nEnvironment file created: {env_file}")
        print("Source it with: source .seq_thinking_env")
    except Exception as e:
        print(f"Error creating environment file: {e}")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--status':
        print_env_status()
        return

    if len(sys.argv) > 1 and sys.argv[1] == '--create-env':
        create_env_file()
        return

    setup_seq_thinking_environment()
    print_env_status()

if __name__ == "__main__":
    main()
