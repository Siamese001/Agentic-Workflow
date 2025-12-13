"""Check if npx is accessible in subprocess."""

import subprocess
import sys

def check_npx():
    """Check npx accessibility."""
    
    # Check if npx is in PATH
    try:
        result = subprocess.run(['where', 'npx'], capture_output=True, text=True)
        print(f"npx location: {result.stdout.strip()}")
    except Exception as e:
        print(f"Failed to find npx: {e}")
    
    # Try running npx directly
    try:
        result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
        print(f"npx version: {result.stdout.strip()}")
    except Exception as e:
        print(f"Failed to run npx: {e}")
    
    # Try with full path
    try:
        result = subprocess.run(['C:\\Program Files\\nodejs\\npx.cmd', '--version'], capture_output=True, text=True)
        print(f"npx version (full path): {result.stdout.strip()}")
    except Exception as e:
        print(f"Failed to run npx with full path: {e}")
    
    # Check if the MCP package exists
    try:
        result = subprocess.run(['npm', 'view', '@modelcontextprotocol/server-filesystem', 'name'], capture_output=True, text=True)
        print(f"Package check: {result.stdout.strip()}")
    except Exception as e:
        print(f"Failed to check package: {e}")

if __name__ == "__main__":
    check_npx()
