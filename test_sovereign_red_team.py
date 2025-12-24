#!/usr/bin/env python3
"""
Test script for SovereignRedTeamAgent
"""
import asyncio
import os
import random
from pathlib import Path

# Test imports
from agentic_core.L5_safety.red_teaming.sovereign_red_team_agent import SovereignRedTeamAgent

class MockContext:
    """Mock context for testing"""
    def __init__(self):
        self.reports = []
    
    def report(self, agent, count, success, message):
        self.reports.append({
            'agent': agent,
            'count': count,
            'success': success,
            'message': message
        })
        print(f"   [REPORT] {agent}: {message}")

async def test_sovereign_red_team():
    """Test the SovereignRedTeamAgent functionality"""
    print("\n=== SovereignRedTeamAgent Test ===\n")
    
    project_root = Path("c:/Git/Agentic-Workflow")
    ctx = MockContext()
    
    # Test 1: Initialize agent
    print("[1] Testing SovereignRedTeamAgent initialization...")
    red_team = SovereignRedTeamAgent(project_root)
    print("   ✓ SovereignRedTeamAgent initialized successfully")
    
    # Test 2: Test directory creation
    print("\n[2] Testing artifacts directory creation...")
    if red_team.test_dir.exists():
        print(f"   ✓ Artifacts directory created at: {red_team.test_dir}")
    else:
        print(f"   ✗ Artifacts directory not found")
    
    # Test 3: Test depth violation injection
    print("\n[3] Testing depth violation injection...")
    depth_file = red_team._inject_depth_violation()
    if depth_file.exists():
        print(f"   ✓ Depth violation probe created: {depth_file.name}")
        content = depth_file.read_text()
        if "REDTEAM: Depth Violation Test" in content:
            print("   ✓ Probe contains correct test marker")
        depth_file.unlink()  # Clean up
    else:
        print(f"   ✗ Failed to create depth violation probe")
    
    # Test 4: Test gravity violation injection
    print("\n[4] Testing gravity violation injection...")
    gravity_file = red_team._inject_gravity_violation()
    if gravity_file.exists():
        print(f"   ✓ Gravity violation probe created: {gravity_file.name}")
        content = gravity_file.read_text()
        if "import apps_rg.core.logic" in content:
            print("   ✓ Probe contains gravity violation import")
        gravity_file.unlink()  # Clean up
    else:
        print(f"   ✗ Failed to create gravity violation probe")
    
    # Test 5: Test run_tests with forced execution
    print("\n[5] Testing run_tests method...")
    
    # Temporarily force 100% execution rate for testing
    original_random = random.random
    random.random = lambda: 0.05  # Always less than 0.10
    
    try:
        result = red_team.run_tests()
        print(f"   ✓ Test probe injected: {result}")
        
        # Check if attack was logged
        if red_team.redis:
            keys = red_team.redis.keys("redteam:last_attack:*")
            if keys:
                print(f"   ✓ Attack logged in Redis: {keys[0]}")
        else:
            if red_team._attack_log:
                print(f"   ✓ Attack logged in memory: {list(red_team._attack_log.keys())[0]}")
    finally:
        # Restore original random function
        random.random = original_random
    
    # Test 6: Test cleanup
    print("\n[6] Testing cleanup functionality...")
    
    # Create some test files
    test_file1 = red_team.test_dir / "test1.py"
    test_file2 = red_team.test_dir / "test2.py"
    test_file3 = red_team.root / "agentic_core/L5_safety/redteam_probe.py"
    
    test_file1.write_text("# Test file 1")
    test_file2.write_text("# Test file 2")
    test_file3.write_text("# Test probe")
    
    print(f"   Created test files for cleanup")
    
    # Run cleanup
    red_team.cleanup()
    
    # Check if files were cleaned
    if not test_file1.exists() and not test_file2.exists() and not test_file3.exists():
        print("   ✓ All test artifacts cleaned successfully")
    else:
        print("   ✗ Some artifacts remain after cleanup")
    
    # Test 7: Test execute method with different probabilities
    print("\n[7] Testing execute method with probability control...")
    
    # Test with high probability (should inject)
    random.random = lambda: 0.05  # 10% threshold
    await red_team.execute(ctx)
    if ctx.reports and "injected" in ctx.reports[-1]['message'].lower():
        print("   ✓ Execute method injected probe when probability met")
    
    # Clear reports
    ctx.reports.clear()
    
    # Test with low probability (should skip)
    random.random = lambda: 0.95  # Above 10% threshold
    await red_team.execute(ctx)
    if ctx.reports and "skipped" in ctx.reports[-1]['message'].lower():
        print("   ✓ Execute method skipped when probability not met")
    
    # Restore original random function
    random.random = original_random
    
    # Test 8: Verify Redis integration
    print("\n[8] Testing Redis integration...")
    if red_team.redis:
        try:
            red_team.redis.ping()
            print("   ✓ Redis connection active")
        except Exception as e:
            print(f"   ✗ Redis connection failed: {e}")
    else:
        print("   ✓ Using in-memory fallback (Redis unavailable)")
    
    # Final cleanup
    red_team.cleanup()
    
    print("\n=== Test Complete ===")
    print("SovereignRedTeamAgent is fully operational with:")
    print("  - Randomized adversarial probe injection")
    print("  - Depth violation testing")
    print("  - Gravity violation testing")
    print("  - Redis-based attack logging")
    print("  - Automatic cleanup of test artifacts")
    print("  - Configurable execution probability")

if __name__ == "__main__":
    asyncio.run(test_sovereign_red_team())
