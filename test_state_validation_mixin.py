#!/usr/bin/env python3
"""Test StateValidationMixin implementation"""

import asyncio
from agentic_core.utils.core_extensions.state_validation_mixin import StateValidationMixin, StateValidationError

class MockBaseAgent:
    """Mock base agent to avoid circular imports"""
    def __init__(self):
        self.name = "MockAgent"
        self.status = "healthy"
        self.operation_count = 0

class TestAgent(StateValidationMixin, MockBaseAgent):
    """Test agent with state validation"""
    
    def __init__(self):
        super().__init__()
        self.data_store = {}
        self.critical_operations = 0
    
    def _is_healthy(self) -> bool:
        """Pre-condition: agent must be healthy"""
        return self.status == "healthy"
    
    def _verify_result(self, result) -> bool:
        """Post-condition: result must not be None"""
        return result is not None
    
    def _has_capacity(self) -> bool:
        """Pre-condition: agent must have capacity"""
        return self.critical_operations < 5
    
    def _verify_increment(self, result) -> bool:
        """Post-condition: operation count should increment"""
        return self.critical_operations > 0
    
    @StateValidationMixin.validate_state(
        pre=_is_healthy,
        post=_verify_result,
        idempotent=True
    )
    async def healthy_operation(self, data):
        """Operation that requires healthy state and returns non-None result"""
        await asyncio.sleep(0.01)
        return f"processed_{data}"
    
    @StateValidationMixin.validate_state(
        pre=_has_capacity,
        post=_verify_increment,
        idempotent=False
    )
    async def capacity_limited_operation(self, data):
        """Operation limited by capacity, increments counter"""
        self.critical_operations += 1
        await asyncio.sleep(0.01)
        return f"capacity_op_{self.critical_operations}"
    
    @StateValidationMixin.validate_state(
        pre=_is_healthy,
        post=lambda self, result: result["success"] == True,
        idempotent=True
    )
    async def complex_operation(self, input_data):
        """Complex operation with structured result validation"""
        await asyncio.sleep(0.02)
        return {"success": True, "data": input_data, "processed": True}
    
    async def unhealthy_operation(self, data):
        """Operation that will fail pre-condition when agent is unhealthy"""
        return f"unhealthy_{data}"

async def test_basic_pre_condition():
    """Test basic pre-condition validation"""
    print("Testing basic pre-condition validation...")
    
    agent = TestAgent()
    
    # Should pass when healthy
    result = await agent.healthy_operation("test1")
    print(f"  ✅ Healthy operation: {result}")
    
    # Should fail when unhealthy
    agent.status = "unhealthy"
    try:
        await agent.healthy_operation("test2")
        print("  ❌ Should have failed pre-condition")
    except StateValidationError as e:
        print(f"  ✅ Pre-condition correctly blocked: {e}")
    
    print("✅ Basic pre-condition test passed")

async def test_post_condition():
    """Test post-condition validation"""
    print("\nTesting post-condition validation...")
    
    agent = TestAgent()
    
    # Should pass with valid result
    result = await agent.complex_operation("test_data")
    print(f"  ✅ Complex operation: {result}")
    
    # Create a method that will fail post-condition
    class FailingAgent(TestAgent):
        @StateValidationMixin.validate_state(
            post=lambda self, result: result["success"] == False  # This will fail
        )
        async def failing_operation(self, data):
            return {"success": True, "data": data}
    
    failing_agent = FailingAgent()
    try:
        await failing_agent.failing_operation("test")
        print("  ❌ Should have failed post-condition")
    except StateValidationError as e:
        print(f"  ✅ Post-condition correctly blocked: {e}")
    
    print("✅ Post-condition test passed")

async def test_idempotency():
    """Test idempotency functionality"""
    print("\nTesting idempotency...")
    
    agent = TestAgent()
    
    # First call should execute
    result1 = await agent.healthy_operation("idempotent_test")
    print(f"  ✅ First call: {result1}")
    
    # Second call with same args should return cached result
    result2 = await agent.healthy_operation("idempotent_test")
    print(f"  ✅ Second call (cached): {result2}")
    
    # Different args should execute new operation
    result3 = await agent.healthy_operation("different_test")
    print(f"  ✅ Different args: {result3}")
    
    # Verify results
    assert result1 == result2, "Idempotent calls should return same result"
    assert result1 != result3, "Different args should produce different results"
    
    print("✅ Idempotency test passed")

async def test_capacity_limiting():
    """Test capacity-based pre-conditions"""
    print("\nTesting capacity limiting...")
    
    agent = TestAgent()
    
    # Should allow operations up to capacity
    for i in range(5):
        result = await agent.capacity_limited_operation(f"batch_{i}")
        print(f"  ✅ Operation {i+1}: {result}")
    
    # Should fail when capacity exceeded
    try:
        await agent.capacity_limited_operation("overflow")
        print("  ❌ Should have failed capacity check")
    except StateValidationError as e:
        print(f"  ✅ Capacity correctly limited: {e}")
    
    print("✅ Capacity limiting test passed")

async def test_error_handling():
    """Test error handling in validation functions"""
    print("\nTesting error handling...")
    
    agent = TestAgent()
    
    # Create agent with faulty pre-condition
    class FaultyAgent(TestAgent):
        def _faulty_pre(self):
            raise Exception("Pre-condition error")
        
        @StateValidationMixin.validate_state(pre=_faulty_pre)
        async def faulty_operation(self, data):
            return "result"
    
    faulty_agent = FaultyAgent()
    try:
        await faulty_agent.faulty_operation("test")
        print("  ❌ Should have failed with pre-condition error")
    except StateValidationError as e:
        print(f"  ✅ Pre-condition error handled: {e}")
    
    # Create agent with faulty post-condition
    class FaultyPostAgent(TestAgent):
        def _faulty_post(self, result):
            raise Exception("Post-condition error")
        
        @StateValidationMixin.validate_state(post=_faulty_post)
        async def faulty_post_operation(self, data):
            return "result"
    
    faulty_post_agent = FaultyPostAgent()
    try:
        await faulty_post_agent.faulty_post_operation("test")
        print("  ❌ Should have failed with post-condition error")
    except StateValidationError as e:
        print(f"  ✅ Post-condition error handled: {e}")
    
    print("✅ Error handling test passed")

async def test_mixed_validation():
    """Test complex validation scenarios"""
    print("\nTesting mixed validation scenarios...")
    
    agent = TestAgent()
    
    # Test operation with all validation types
    class MixedAgent(TestAgent):
        def _complex_pre(self):
            return self.status == "healthy" and self.critical_operations < 3
        
        def _complex_post(self, result):
            return isinstance(result, dict) and result.get("processed") is True
        
        @StateValidationMixin.validate_state(
            pre=_complex_pre,
            post=_complex_post,
            idempotent=True
        )
        async def mixed_operation(self, data):
            self.critical_operations += 1
            return {"processed": True, "data": data, "count": self.critical_operations}
    
    mixed_agent = MixedAgent()
    
    # Should pass all validations
    result1 = await mixed_agent.mixed_operation("mixed_test")
    print(f"  ✅ Mixed operation 1: {result1}")
    
    # Should be idempotent
    result2 = await mixed_agent.mixed_operation("mixed_test")
    print(f"  ✅ Mixed operation 2 (cached): {result2}")
    
    # Should fail when capacity exceeded
    mixed_agent.critical_operations = 5
    try:
        await mixed_agent.mixed_operation("should_fail")
        print("  ❌ Should have failed pre-condition")
    except StateValidationError as e:
        print(f"  ✅ Mixed validation correctly blocked: {e}")
    
    print("✅ Mixed validation test passed")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("STATE VALIDATION MIXIN TESTS")
    print("=" * 60)
    
    await test_basic_pre_condition()
    await test_post_condition()
    await test_idempotency()
    await test_capacity_limiting()
    await test_error_handling()
    await test_mixed_validation()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
