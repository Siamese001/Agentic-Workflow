#!/usr/bin/env python3
"""
Example usage of RateLimitMixin in agent implementations
"""

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.rate_limit_mixin import RateLimitMixin, RateLimitMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

class HealingAgent(RateLimitMixin, HealerMixin, SovereignBaseAgent):
    """
    Example agent with rate-limited healing capabilities
    """
    
    # Pre-define rate limits in class
    _rate_limits = {
        "heal": {"rate": 10, "per": 60, "burst": 15},  # 10 heals/min, burst 15
        "mcp_call": {"rate": 100, "per": 60, "burst": 150},  # 100 MCP calls/min
        "external_api": {"rate": 1000, "per": 3600, "burst": 1200},  # 1k API calls/hour
    }
    
    def __init__(self):
        super().__init__()
        self.heal_count = 0
    
    async def heal(self, violation):
        """
        Rate-limited heal method using decorator
        """
        self.heal_count += 1
        print(f"Healing violation #{self.heal_count}: {violation.get('type', 'unknown')}")
        
        # Simulate healing work
        await asyncio.sleep(0.1)
        
        return {"success": True, "healed_by": self.__class__.__name__}
    
    async def call_external_api(self, endpoint, data):
        """
        Rate-limited external API call using manual check
        """
        # Manual rate limit check
        await self.check_rate_limit("external_api")
        
        print(f"Calling external API: {endpoint}")
        # Simulate API call
        await asyncio.sleep(0.05)
        
        return {"status": "success", "data": f"Processed {data}"}

class MCPClientAgent(RateLimitMixin, MCPHardenedMixin, SovereignBaseAgent):
    """
    Example MCP client with rate limiting
    """
    
    def __init__(self):
        super().__init__()
        # Dynamic rate limit configuration
        self.configure_rate_limit("mcp_call", rate=50, per=60, burst=75)
        self.configure_rate_limit("file_operation", rate=200, per=60, burst=300)
    
    async def read_file(self, path):
        """Rate-limited file read operation"""
        await self.check_rate_limit("file_operation")
        
        # Use hardened MCP call with rate limiting
        return await self.safe_mcp_call("read_file", {"path": path})
    
    async def write_file(self, path, content):
        """Rate-limited file write operation"""
        await self.check_rate_limit("file_operation", consume=2)  # Write costs 2 tokens
        
        return await self.safe_mcp_call("write_file", {"path": path, "content": content})

async def demonstrate_usage():
    """Demonstrate RateLimitMixin usage"""
    print("=" * 60)
    print("RATE LIMIT MIXIN USAGE EXAMPLES")
    print("=" * 60)
    
    # Example 1: Healing Agent
    print("\n1. Healing Agent Example:")
    print("-" * 30)
    
    healer = HealingAgent()
    
    # Try to heal multiple violations
    violations = [
        {"type": "syntax_error", "file": "test.py"},
        {"type": "import_error", "file": "main.py"},
        {"type": "runtime_error", "file": "utils.py"},
    ]
    
    for i, violation in enumerate(violations):
        try:
            result = await healer.heal(violation)
            print(f"  ✅ Healed {violation['type']}")
        except RateLimitExceeded as e:
            print(f"  ❌ Rate limited: wait {e.wait_time:.2f}s")
            break
    
    # Example 2: MCP Client Agent
    print("\n2. MCP Client Agent Example:")
    print("-" * 30)
    
    mcp_client = MCPClientAgent()
    
    try:
        # Simulate rapid file operations
        for i in range(5):
            result = await mcp_client.read_file(f"file_{i}.py")
            print(f"  ✅ Read file_{i}.py")
    except RateLimitExceeded as e:
        print(f"  ❌ Rate limited after 5 files: wait {e.wait_time:.2f}s")
    
    print("\n" + "=" * 60)
    print("✅ USAGE DEMONSTRATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_usage())
