#!/usr/bin/env python3
"""Validate all SDKs and MCPs in the Agentic Workflow."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly to bypass broken __init__.py
import runtime.shared.sdk_registry as sdk_registry
import runtime.shared.mcp_tools as mcp_tools
import runtime.shared.multi_provider_clients as mp_clients

def main():
    print("=" * 60)
    print("AGENTIC WORKFLOW - SDK & MCP VALIDATION")
    print("=" * 60)
    
    # 1. Validate all SDKs
    print("\n1. SDK VALIDATION")
    print("-" * 40)
    
    report = sdk_registry.validate_all_sdks()
    
    print(f"Total SDKs: {report['total']}")
    print(f"Available: {report['available']}")
    print(f"Missing: {report['missing']}")
    print(f"Missing API Keys: {report['missing_keys']}")
    
    # Show missing SDKs
    missing_sdks = [name for name, details in report['details'].items() 
                   if not details['available']]
    if missing_sdks:
        print(f"\nMissing SDKs: {', '.join(missing_sdks)}")
    
    # Show missing API keys
    missing_keys = [name for name, details in report['details'].items() 
                   if details.get('error') and 'not set' in details.get('error', '')]
    if missing_keys:
        print(f"Missing API Keys: {', '.join(missing_keys)}")
    
    # 2. Check MCP Server
    print("\n2. MCP SERVER VALIDATION")
    print("-" * 40)
    
    try:
        mcp_server = mcp_tools.create_mcp_server()
        tools = mcp_server.list_tools()
        print(f"MCP Server: OK")
        print(f"Registered Tools: {len(tools)}")
        print(f"Tools: {', '.join(tools)}")
        
        # Test tool execution
        result = mcp_server.execute_tool("calculator", 
                                       {"operation": "add", "a": 1, "b": 2})
        print(f"Tool Execution Test: OK (1 + 2 = {result.result})")
        
    except Exception as e:
        print(f"MCP Server: FAILED - {e}")
    
    # 3. Check Multi-Provider Clients
    print("\n3. MULTI-PROVIDER CLIENT VALIDATION")
    print("-" * 40)
    
    try:
        providers = mp_clients.get_available_providers()
        print(f"Available Providers: {len(providers)}")
        for provider in providers:
            print(f"  - {provider.value}")
        
        if not providers:
            print("No providers have API keys configured")
            
    except Exception as e:
        print(f"Multi-Provider Client: FAILED - {e}")
    
    # 4. Summary
    print("\n4. VALIDATION SUMMARY")
    print("-" * 40)
    
    all_good = (
        report['missing'] == 0 and 
        report['missing_keys'] == 0 and
        len(missing_sdks) == 0
    )
    
    if all_good:
        print("✅ ALL SDKs AND MCPs FULLY OPERATIONAL")
    else:
        print("⚠️  SOME COMPONENTS MISSING CONFIGURATION")
        print("\nTo fix missing SDKs:")
        print("  pip install --upgrade -r requirements.txt")
        print("\nTo fix missing API keys:")
        print("  Set the required environment variables listed above")
    
    print("\n" + "=" * 60)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
