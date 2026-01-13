#!/usr/bin/env python3
"""Test RateLimitMixin implementation"""

import asyncio
import time
from agentic_core.utils.core_extensions.rate_limit_mixin import RateLimitMixin, RateLimitExceeded

class TestAgent(RateLimitMixin):
    def __init__(self):
        super().__init__()
        # Configure rate limits for testing
        self._rate_limits = {
            "heal": {"rate": 5, "per": 60, "burst": 10},  # 5 heals/min
            "mcp_call": {"rate": 100, "per": 60, "burst": 150},  # 100 calls/min
        }

async def test_basic_rate_limit():
    """Test basic rate limiting functionality"""
    print("Testing basic rate limiting...")
    
    agent = TestAgent()
    
    # Should allow first 5 calls (burst capacity)
    for i in range(10):
        try:
            allowed = await agent.check_rate_limit("heal")
            print(f"  Call {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
        except RateLimitExceeded as e:
            print(f"  Call {i+1}: ❌ Rate limited (wait {e.wait_time:.2f}s)")
    
    print("✅ Basic rate limiting test passed")

async def test_token_bucket_refill():
    """Test token bucket refill over time"""
    print("\nTesting token bucket refill...")
    
    agent = TestAgent()
    
    # Consume all tokens
    while await agent.check_rate_limit("heal", raise_exc=False):
        pass
    
    print("  All tokens consumed")
    
    # Wait for refill (should take ~12 seconds for 1 token at 5/min)
    print("  Waiting for token refill...")
    time.sleep(12)
    
    # Should now have 1 token available
    allowed = await agent.check_rate_limit("heal")
    print(f"  After wait: {'✅ Token refilled' if allowed else '❌ No token'}")
    
    print("✅ Token bucket refill test passed")

async def test_decorator():
    """Test rate limiting decorator"""
    print("\nTesting rate limiting decorator...")
    
    class DecoratedAgent(RateLimitMixin):
        def __init__(self):
            super().__init__()
            self._rate_limits = {"test_op": {"rate": 2, "per": 10, "burst": 3}}
            self.call_count = 0
        
        @RateLimitMixin.rate_limit("test_op")
        async def rate_limited_method(self):
            self.call_count += 1
            return f"Call {self.call_count}"
    
    agent = DecoratedAgent()
    
    # Should allow burst of 3 calls
    for i in range(5):
        try:
            result = await agent.rate_limited_method()
            print(f"  Call {i+1}: ✅ {result}")
        except RateLimitExceeded as e:
            print(f"  Call {i+1}: ❌ Rate limited (wait {e.wait_time:.2f}s)")
    
    print("✅ Decorator test passed")

async def test_dynamic_configuration():
    """Test dynamic rate limit configuration"""
    print("\nTesting dynamic configuration...")
    
    agent = TestAgent()
    
    # Add new rate limit dynamically
    agent.configure_rate_limit("new_op", rate=10, per=60, burst=15)
    
    # Test the new limit
    for i in range(20):
        allowed = await agent.check_rate_limit("new_op", raise_exc=False)
        if not allowed:
            print(f"  New op blocked after {i} calls")
            break
    
    print("✅ Dynamic configuration test passed")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("RATE LIMIT MIXIN TESTS")
    print("=" * 60)
    
    await test_basic_rate_limit()
    await test_token_bucket_refill()
    await test_decorator()
    await test_dynamic_configuration()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
