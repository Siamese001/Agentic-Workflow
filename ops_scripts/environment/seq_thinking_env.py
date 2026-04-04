#!/usr/bin/env python3
"""
Environment setup for sequential thinking prioritization.
Sets system-wide environment variables to influence Windsurf's tool selection.
"""

import os
import sys
from pathlib import Path


def setup_seq_thinking_environment():
    """Setup environment variables for hardened sequential thinking dominance."""

    env_vars = {
        # Sequential thinking HARDENED prioritization
        'SEQUENTIAL_THINKING_ENABLED': 'true',
        'SEQUENTIAL_THINKING_PRIORITY': '0',  # ABSOLUTE highest priority
        'SEQUENTIAL_THINKING_AUTO_TRIGGER': 'true',
        'SEQUENTIAL_THINKING_MIN_COMPLEXITY': 'minimal',  # Trigger on ANY complexity
        'SEQUENTIAL_THINKING_MAX_THOUGHTS': '25',
        'SEQUENTIAL_THINKING_TOKEN_BUDGET': '50000',

        # Windsurf tool preferences - HARDENED
        'WINDSURF_TOOL_PREFERENCE': 'sequential-thinking',
        'WINDSURF_MCP_BOOST_MODE': 'aggressive',
        'WINDSURF_REASONING_MODE': 'sequential-only',  # NO chat fallback

        # Kimi K2.5 HARDENED integration
        'KIMI25_SEQUENTIAL_THINKING': 'enabled',
        'KIMI25_REASONING_BOOST': 'maximum',
        'KIMI25_TOKEN_ALLOCATION': '0.35',  # 35% of context window for reasoning
        'KIMI25_AUTO_ANALYSIS': 'true',
        'KIMI_K2_5_DOMINANCE': 'enabled',

        # MCP integration - HARDENED
        'MCP_SEQUENTIAL_THINKING_BOOST': 'aggressive',
        'MCP_TOOL_ORDERING': 'sequential-dominance',
        'MCP_KIMI25_MODE': 'hardened',

        # CASCADE CHAT SUPPRESSION
        'CASCADE_CHAT_FALLBACK': 'disabled',
        'CASCADE_CHAT_SUPPRESS_ON_PLANNING': 'true',
        'CASCADE_CHAT_MIN_COMPLEXITY': 'high',  # Chat only for trivial tasks

        # Performance tuning - HARDENED
        'SEQUENTIAL_THINKING_CACHE_ENABLED': 'true',
        'SEQUENTIAL_THINKING_ASYNC_MODE': 'false',
        'SEQUENTIAL_THINKING_LOG_LEVEL': 'INFO',
        'SEQUENTIAL_THINKING_AGGRESSIVE_MODE': 'enabled'
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
        'KIMI25_SEQUENTIAL_THINKING',
        'CASCADE_CHAT_FALLBACK',
        'KIMI_K2_5_DOMINANCE'
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

    env_content = """# Sequential Thinking Environment Configuration - HARDENED
# Source this file to enable SEQUENTIAL THINKING DOMINANCE over cascade chat

# Sequential thinking HARDENED settings
export SEQUENTIAL_THINKING_ENABLED=true
export SEQUENTIAL_THINKING_PRIORITY=0
export SEQUENTIAL_THINKING_AUTO_TRIGGER=true
export SEQUENTIAL_THINKING_MIN_COMPLEXITY=minimal
export SEQUENTIAL_THINKING_MAX_THOUGHTS=25
export SEQUENTIAL_THINKING_TOKEN_BUDGET=50000

# Windsurf tool preferences - HARDENED
export WINDSURF_TOOL_PREFERENCE=sequential-thinking
export WINDSURF_MCP_BOOST_MODE=aggressive
export WINDSURF_REASONING_MODE=sequential-only

# Kimi K2.5 HARDENED integration
export KIMI25_SEQUENTIAL_THINKING=enabled
export KIMI25_REASONING_BOOST=maximum
export KIMI25_TOKEN_ALLOCATION=0.35
export KIMI25_AUTO_ANALYSIS=true
export KIMI_K2_5_DOMINANCE=enabled

# MCP integration - HARDENED
export MCP_SEQUENTIAL_THINKING_BOOST=aggressive
export MCP_TOOL_ORDERING=sequential-dominance
export MCP_KIMI25_MODE=hardened

# CASCADE CHAT SUPPRESSION
export CASCADE_CHAT_FALLBACK=disabled
export CASCADE_CHAT_SUPPRESS_ON_PLANNING=true
export CASCADE_CHAT_MIN_COMPLEXITY=high

# Performance tuning - HARDENED
export SEQUENTIAL_THINKING_CACHE_ENABLED=true
export SEQUENTIAL_THINKING_ASYNC_MODE=false
export SEQUENTIAL_THINKING_LOG_LEVEL=INFO
export SEQUENTIAL_THINKING_AGGRESSIVE_MODE=enabled
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
