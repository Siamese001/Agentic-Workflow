#!/usr/bin/env python3
"""
Example usage of StateValidationMixin in agent implementations
"""

import asyncio
from agentic_core.utils.core_extensions.state_validation_mixin import StateValidationMixin, StateValidationError

class MockBaseAgent:
    """Mock base agent to avoid circular imports"""
    def __init__(self):
        self.name = "MockAgent"

class HealingAgent(StateValidationMixin, MockBaseAgent):
    """
    Example healing agent with state validation
    """
    
    def __init__(self):
        super().__init__()
        self.status = "healthy"
        self.healing_count = 0
        self.max_heals = 10
        self.violation_history = []
    
    def _is_healthy(self) -> bool:
        """Pre-condition: agent must be healthy to heal"""
        return self.status == "healthy"
    
    def _has_healing_capacity(self) -> bool:
        """Pre-condition: agent must have healing capacity"""
        return self.healing_count < self.max_heals
    
    def _verify_healing_result(self, result) -> bool:
        """Post-condition: healing result must be successful"""
        return isinstance(result, dict) and result.get("success") is True
    
    def _track_violation(self, result) -> bool:
        """Post-condition: violation should be tracked"""
        return len(self.violation_history) > 0
    
    @StateValidationMixin.validate_state(
        pre=_is_healthy,
        post=_verify_healing_result,
        idempotent=True
    )
    async def heal_violation(self, violation):
        """
        Heal a violation with state validation
        - Must be healthy
        - Result must indicate success
        - Idempotent (same violation won't be healed twice)
        """
        self.healing_count += 1
        self.violation_history.append(violation)
        
        # Simulate healing work
        await asyncio.sleep(0.01)
        
        return {
            "success": True,
            "healed_by": self.__class__.__name__,
            "violation": violation,
            "heal_count": self.healing_count
        }
    
    @StateValidationMixin.validate_state(
        pre=_has_healing_capacity,
        post=_track_violation,
        idempotent=False
    )
    async def batch_heal(self, violations):
        """
        Batch heal multiple violations
        - Must have capacity
        - Must track violations
        - Not idempotent (each call processes new violations)
        """
        results = []
        for violation in violations:
            result = await self.heal_violation(violation)
            results.append(result)
        
        return {
            "success": True,
            "processed": len(results),
            "results": results
        }

class DataProcessingAgent(StateValidationMixin, MockBaseAgent):
    """
    Example data processing agent with complex state validation
    """
    
    def __init__(self):
        super().__init__()
        self.status = "ready"
        self.processed_count = 0
        self.max_daily_processes = 100
        self.data_quality_score = 1.0
    
    def _is_ready(self) -> bool:
        """Pre-condition: agent must be ready"""
        return self.status == "ready"
    
    def _has_daily_capacity(self) -> bool:
        """Pre-condition: must not exceed daily limit"""
        return self.processed_count < self.max_daily_processes
    
    def _data_quality_acceptable(self) -> bool:
        """Pre-condition: data quality must be acceptable"""
        return self.data_quality_score >= 0.8
    
    def _verify_processing_result(self, result) -> bool:
        """Post-condition: result must contain required fields"""
        required_fields = ["processed", "quality_score", "timestamp"]
        return isinstance(result, dict) and all(field in result for field in required_fields)
    
    def _quality_maintained(self, result) -> bool:
        """Post-condition: quality should not degrade significantly"""
        return result.get("quality_score", 0) >= 0.7
    
    @StateValidationMixin.validate_state(
        pre=_is_ready,
        post=_verify_processing_result,
        idempotent=True
    )
    async def process_data(self, data):
        """
        Process data with basic validation
        """
        self.processed_count += 1
        
        # Simulate processing
        await asyncio.sleep(0.01)
        quality = self.data_quality_score * 0.95  # Slight quality degradation
        
        return {
            "processed": True,
            "quality_score": quality,
            "timestamp": "2026-01-13T11:00:00Z",
            "data_id": id(data)
        }
    
    @StateValidationMixin.validate_state(
        pre=[_is_ready, _has_daily_capacity, _data_quality_acceptable],
        post=[_verify_processing_result, _quality_maintained],
        idempotent=False
    )
    async def critical_data_processing(self, data):
        """
        Critical processing with multiple pre/post conditions
        """
        self.processed_count += 1
        
        # Simulate critical processing
        await asyncio.sleep(0.02)
        quality = self.data_quality_score * 0.9  # More quality impact
        
        return {
            "processed": True,
            "quality_score": quality,
            "timestamp": "2026-01-13T11:00:00Z",
            "critical": True,
            "data_id": id(data)
        }

class MCPClientAgent(StateValidationMixin, MockBaseAgent):
    """
    Example MCP client with state validation
    """
    
    def __init__(self):
        super().__init__()
        self.mcp_connected = True
        self.call_count = 0
        self.rate_limit_remaining = 100
        self.last_error = None
    
    def _is_connected(self) -> bool:
        """Pre-condition: must be connected to MCP"""
        return self.mcp_connected
    
    def _has_rate_limit(self) -> bool:
        """Pre-condition: must have rate limit remaining"""
        return self.rate_limit_remaining > 0
    
    def _no_recent_errors(self) -> bool:
        """Pre-condition: no recent errors"""
        return self.last_error is None
    
    def _verify_mcp_result(self, result) -> bool:
        """Post-condition: MCP result must be valid"""
        return isinstance(result, dict) and "result" in result
    
    def _update_rate_limit(self, result) -> bool:
        """Post-condition: rate limit should be updated"""
        return self.rate_limit_remaining >= 0
    
    @StateValidationMixin.validate_state(
        pre=[_is_connected, _has_rate_limit],
        post=[_verify_mcp_result, _update_rate_limit],
        idempotent=True
    )
    async def mcp_call(self, tool_name, args):
        """
        Make MCP call with validation
        """
        self.call_count += 1
        self.rate_limit_remaining -= 1
        
        # Simulate MCP call
        await asyncio.sleep(0.01)
        
        return {
            "result": f"Called {tool_name} with {args}",
            "tool": tool_name,
            "args": args,
            "call_id": self.call_count
        }

async def demonstrate_healing_agent():
    """Demonstrate healing agent with state validation"""
    print("\n1. Healing Agent Example:")
    print("-" * 40)
    
    healer = HealingAgent()
    
    # Test successful healing
    violation = {"type": "syntax_error", "file": "test.py"}
    result = await healer.heal_violation(violation)
    print(f"  ✅ Healed violation: {result['success']}")
    
    # Test idempotency (same violation should return cached result)
    result2 = await healer.heal_violation(violation)
    print(f"  ✅ Idempotent result: {result2['heal_count']} (same as before)")
    
    # Test capacity limiting
    healer.healing_count = healer.max_heals
    try:
        await healer.heal_violation({"type": "new_error", "file": "test2.py"})
        print("  ❌ Should have failed capacity check")
    except StateValidationError as e:
        print(f"  ✅ Capacity correctly limited: {str(e)[:50]}...")
    
    # Test unhealthy state
    healer.status = "unhealthy"
    healer.healing_count = 0
    try:
        await healer.heal_violation({"type": "test", "file": "test.py"})
        print("  ❌ Should have failed health check")
    except StateValidationError as e:
        print(f"  ✅ Health check correctly blocked: {str(e)[:50]}...")

async def demonstrate_data_processing():
    """Demonstrate data processing agent"""
    print("\n2. Data Processing Agent Example:")
    print("-" * 40)
    
    processor = DataProcessingAgent()
    
    # Test basic processing
    result = await processor.process_data("sample_data")
    print(f"  ✅ Processed data: quality={result['quality_score']:.2f}")
    
    # Test idempotency
    result2 = await processor.process_data("sample_data")
    print(f"  ✅ Idempotent: same result={result == result2}")
    
    # Test critical processing with multiple conditions
    result3 = await processor.critical_data_processing("critical_data")
    print(f"  ✅ Critical processing: quality={result3['quality_score']:.2f}")
    
    # Test daily capacity limit
    processor.processed_count = processor.max_daily_processes
    try:
        await processor.critical_data_processing("overflow_data")
        print("  ❌ Should have failed capacity check")
    except StateValidationError as e:
        print(f"  ✅ Daily capacity correctly limited: {str(e)[:50]}...")
    
    # Test quality threshold
    processor.processed_count = 0
    processor.data_quality_score = 0.7  # Below threshold
    try:
        await processor.critical_data_processing("low_quality_data")
        print("  ❌ Should have failed quality check")
    except StateValidationError as e:
        print(f"  ✅ Quality threshold correctly enforced: {str(e)[:50]}...")

async def demonstrate_mcp_client():
    """Demonstrate MCP client agent"""
    print("\n3. MCP Client Agent Example:")
    print("-" * 40)
    
    client = MCPClientAgent()
    
    # Test successful MCP call
    result = await client.mcp_call("read_file", {"path": "test.py"})
    print(f"  ✅ MCP call: {result['tool']}")
    
    # Test idempotency
    result2 = await client.mcp_call("read_file", {"path": "test.py"})
    print(f"  ✅ Idempotent: same call_id={result['call_id']}")
    
    # Test rate limiting
    client.rate_limit_remaining = 0
    try:
        await client.mcp_call("write_file", {"path": "test.py", "content": "data"})
        print("  ❌ Should have failed rate limit check")
    except StateValidationError as e:
        print(f"  ✅ Rate limit correctly enforced: {str(e)[:50]}...")
    
    # Test connection requirement
    client.rate_limit_remaining = 10
    client.mcp_connected = False
    try:
        await client.mcp_call("list_dir", {"path": "."})
        print("  ❌ Should have failed connection check")
    except StateValidationError as e:
        print(f"  ✅ Connection requirement correctly enforced: {str(e)[:50]}...")

async def main():
    """Run all demonstrations"""
    print("=" * 60)
    print("STATE VALIDATION MIXIN USAGE DEMONSTRATIONS")
    print("=" * 60)
    
    await demonstrate_healing_agent()
    await demonstrate_data_processing()
    await demonstrate_mcp_client()
    
    print("\n" + "=" * 60)
    print("✅ ALL DEMONSTRATIONS COMPLETE")
    print("=" * 60)
    
    print("\nKey Features Demonstrated:")
    print("• Pre-condition validation (guard clauses)")
    print("• Post-condition verification (invariants)")
    print("• Idempotency guarantees via input hashing")
    print("• Multiple validation conditions")
    print("• Graceful error handling")
    print("• State consistency enforcement")

if __name__ == "__main__":
    asyncio.run(main())
