#!/usr/bin/env python3
"""
Standalone example of RateLimitMixin usage (no circular imports)
"""

import asyncio
from agentic_core.utils.core_extensions.rate_limit_mixin import RateLimitMixin, RateLimitExceeded

class MockBaseAgent:
    """Mock base agent to avoid circular imports"""
    def __init__(self):
        self.name = "MockAgent"

class ExampleAgent(RateLimitMixin, MockBaseAgent):
    """
    Example agent demonstrating RateLimitMixin usage
    """
    
    # Pre-define rate limits
    _rate_limits = {
        "heal": {"rate": 10, "per": 60, "burst": 15},  # 10 heals/min
        "mcp_call": {"rate": 100, "per": 60, "burst": 150},  # 100 MCP calls/min
        "external_api": {"rate": 1000, "per": 3600, "burst": 1200},  # 1k API calls/hour
    }
    
    def __init__(self):
        super().__init__()
        self.heal_count = 0
    
    async def heal(self, violation):
        """
        Rate-limited heal method
        """
        # Check rate limit before healing
        await self.check_rate_limit("heal")
        
        self.heal_count += 1
        print(f"Healing violation #{self.heal_count}: {violation.get('type', 'unknown')}")
        
        # Simulate healing work
        await asyncio.sleep(0.1)
        
        return {"success": True, "healed_by": self.__class__.__name__}
    
    async def call_external_api(self, endpoint, data):
        """
        Rate-limited external API call
        """
        # Manual rate limit check
        await self.check_rate_limit("external_api")
        
        print(f"Calling external API: {endpoint}")
        # Simulate API call
        await asyncio.sleep(0.05)
        
        return {"status": "success", "data": f"Processed {data}"}
    
    @RateLimitMixin.rate_limit("mcp_call")
    async def mcp_operation(self, tool_name, args):
        """
        Rate-limited MCP operation using decorator
        """
        print(f"Performing MCP operation: {tool_name}")
        await asyncio.sleep(0.02)
        return {"result": f"Completed {tool_name}"}

class DynamicRateLimitAgent(RateLimitMixin, MockBaseAgent):
    """
    Example agent with dynamic rate limit configuration
    """
    
    def __init__(self):
        super().__init__()
        
        # Configure rate limits dynamically
        self.configure_rate_limit("file_read", rate=200, per=60, burst=300)
        self.configure_rate_limit("file_write", rate=100, per=60, burst=150)
        self.configure_rate_limit("batch_operation", rate=10, per=60, burst=20)
    
    async def read_file(self, path):
        """Rate-limited file read"""
        await self.check_rate_limit("file_read")
        print(f"Reading file: {path}")
        await asyncio.sleep(0.01)
        return {"content": f"Content of {path}"}
    
    async def write_file(self, path, content):
        """Rate-limited file write (costs 2 tokens)"""
        await self.check_rate_limit("file_write", consume=2)
        print(f"Writing file: {path}")
        await asyncio.sleep(0.02)
        return {"status": "success"}
    
    async def batch_process(self, items):
        """Rate-limited batch processing"""
        await self.check_rate_limit("batch_operation")
        print(f"Processing batch of {len(items)} items")
        await asyncio.sleep(0.1)
        return {"processed": len(items)}

async def demonstrate_basic_usage():
    """Demonstrate basic RateLimitMixin functionality"""
    print("\n1. Basic RateLimitMixin Usage:")
    print("-" * 40)
    
    agent = ExampleAgent()
    
    # Test healing operations
    violations = [
        {"type": "syntax_error", "file": "test.py"},
        {"type": "import_error", "file": "main.py"},
        {"type": "runtime_error", "file": "utils.py"},
    ]
    
    print("Testing healing operations:")
    for i, violation in enumerate(violations):
        try:
            result = await agent.heal(violation)
            print(f"  ✅ Healed {violation['type']}")
        except RateLimitExceeded as e:
            print(f"  ❌ Rate limited: wait {e.wait_time:.2f}s")
            break
    
    # Test MCP operations with decorator
    print("\nTesting MCP operations (decorator):")
    for i in range(5):
        try:
            result = await agent.mcp_operation(f"tool_{i}", {"arg": "value"})
            print(f"  ✅ MCP operation {i+1}")
        except RateLimitExceeded as e:
            print(f"  ❌ Rate limited after {i+1} operations: wait {e.wait_time:.2f}s")
            break

async def demonstrate_dynamic_configuration():
    """Demonstrate dynamic rate limit configuration"""
    print("\n2. Dynamic Rate Limit Configuration:")
    print("-" * 40)
    
    agent = DynamicRateLimitAgent()
    
    # Test file operations
    print("Testing file operations:")
    try:
        for i in range(10):
            await agent.read_file(f"file_{i}.py")
            await agent.write_file(f"output_{i}.py", f"content {i}")
        print("  ✅ 10 file operations completed")
    except RateLimitExceeded as e:
        print(f"  ❌ Rate limited: wait {e.wait_time:.2f}s")
    
    # Test batch operations
    print("\nTesting batch operations:")
    try:
        for i in range(3):
            await agent.batch_process([f"item_{j}" for j in range(10)])
        print("  ✅ 3 batch operations completed")
    except RateLimitExceeded as e:
        print(f"  ❌ Rate limited: wait {e.wait_time:.2f}s")

async def demonstrate_burst_handling():
    """Demonstrate burst capacity handling"""
    print("\n3. Burst Capacity Handling:")
    print("-" * 40)
    
    agent = ExampleAgent()
    
    # Test burst capacity (should allow 15 heals even though rate is 10/min)
    print("Testing burst capacity (15 heals, rate=10/min):")
    successful_heals = 0
    for i in range(20):
        try:
            await agent.heal({"type": f"test_{i}", "file": "test.py"})
            successful_heals += 1
        except RateLimitExceeded as e:
            print(f"  ❌ Rate limited after {successful_heals} heals")
            break
    
    print(f"  ✅ Successful heals: {successful_heals} (burst capacity)")

async def main():
    """Run all demonstrations"""
    print("=" * 60)
    print("RATE LIMIT MIXIN USAGE DEMONSTRATIONS")
    print("=" * 60)
    
    await demonstrate_basic_usage()
    await demonstrate_dynamic_configuration()
    await demonstrate_burst_handling()
    
    print("\n" + "=" * 60)
    print("✅ ALL DEMONSTRATIONS COMPLETE")
    print("=" * 60)
    
    print("\nKey Features Demonstrated:")
    print("• Token bucket algorithm with burst capacity")
    print("• Per-operation rate limits")
    print("• Dynamic configuration")
    print("• Decorator-based enforcement")
    print("• Manual rate limit checks")
    print("• Graceful handling of rate limit exceeded")

if __name__ == "__main__":
    asyncio.run(main())
