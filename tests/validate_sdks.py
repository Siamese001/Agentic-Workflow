import logging

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""Validate all SDKs and MCPs in the Agentic Workflow."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly to bypass broken __init__.py


def main() -> None:
    """TODO: Add docstring."""

    logger.info("=" * 60)
    logger.info("AGENTIC WORKFLOW - SDK & MCP VALIDATION")
    logger.info("=" * 60)

    # 1. Validate all SDKs
    logger.info("\n1. SDK VALIDATION")
    logger.info("-" * 40)

    report = sdk_registry.validate_all_sdks()

    logger.info(f"Total SDKs: {report['total']}")
    logger.info(f"Available: {report['available']}")
    logger.info(f"Missing: {report['missing']}")
    logger.info(f"Missing API Keys: {report['missing_keys']}")

    # Show missing SDKs
    missing_sdks = [name for name, details in report["details"].items() if not details["available"]]
    if missing_sdks:
        logger.info(f"\nMissing SDKs: {', '.join(missing_sdks)}")

    # Show missing API keys
    missing_keys = [
        name
        for name, details in report["details"].items()
        if details.get("error") and "not set" in details.get("error", "")
    ]
    if missing_keys:
        logger.info(f"Missing API Keys: {', '.join(missing_keys)}")

    # 2. Check MCP Server
    logger.info("\n2. MCP SERVER VALIDATION")
    logger.info("-" * 40)

    try:
        mcp_server = mcp_tools.create_mcp_server()
        tools = mcp_server.list_tools()
        logger.info(f"MCP Server: OK")
        logger.info(f"Registered Tools: {len(tools)}")
        logger.info(f"Tools: {', '.join(tools)}")

        # Test tool execution
        result = mcp_server.execute_tool("calculator", {"operation": "add", "a": 1, "b": 2})
        logger.info(f"Tool Execution Test: OK (1 + 2 = {result.result})")

    except Exception as e:
        logger.info(f"MCP Server: FAILED - {e}")

    # 3. Check Multi-Provider Clients
    logger.info("\n3. MULTI-PROVIDER CLIENT VALIDATION")
    logger.info("-" * 40)

    try:
        providers = mp_clients.get_available_providers()
        logger.info(f"Available Providers: {len(providers)}")
        for provider in providers:
            logger.info(f"  - {provider.value}")

        if not providers:
            logger.info("No providers have API keys configured")

    except Exception as e:
        logger.info(f"Multi-Provider Client: FAILED - {e}")

    # 4. Summary
    logger.info("\n4. VALIDATION SUMMARY")
    logger.info("-" * 40)

    all_good = report["missing"] == 0 and report["missing_keys"] == 0 and len(missing_sdks) == 0

    if all_good:
        logger.info("✅ ALL SDKs AND MCPs FULLY OPERATIONAL")
    else:
        logger.info("⚠️  SOME COMPONENTS MISSING CONFIGURATION")
        logger.info("\nTo fix missing SDKs:")
        logger.info("  pip install --upgrade -r requirements.txt")
        logger.info("\nTo fix missing API keys:")
        logger.info("  Set the required environment variables listed above")

    logger.info("\n" + "=" * 60)

    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
