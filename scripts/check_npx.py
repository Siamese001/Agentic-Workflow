"""Check npx installation and package availability."""

import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def check_npx():
    """Check npx accessibility."""

    # Check if npx is in PATH
    try:
        result = subprocess.run(['where', 'npx'], capture_output=True, text=True)
        logger.info(f"npx location: {result.stdout.strip()}")
    except Exception as e:
        logger.error(f"Failed to find npx: {e}")

    # Try running npx directly
    try:
        result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
        logger.info(f"npx version: {result.stdout.strip()}")
    except Exception as e:
        logger.error(f"Failed to run npx: {e}")

    # Try with full path
    try:
        result = subprocess.run(['C:\\Program Files\\nodejs\\npx.cmd', '--version'], capture_output=True, text=True)
        logger.info(f"npx version (full path): {result.stdout.strip()}")
    except Exception as e:
        logger.error(f"Failed to run npx with full path: {e}")

    # Check if the MCP package exists
    try:
        result = subprocess.run(['npm', 'view', '@modelcontextprotocol/server-filesystem', 'name'], capture_output=True, text=True)
        logger.info(f"Package check: {result.stdout.strip()}")
    except Exception as e:
        logger.error(f"Failed to check package: {e}")

if __name__ == "__main__":
    check_npx()
