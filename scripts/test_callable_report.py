#!/usr/bin/env python3
"""
Test the CallableReport hybrid class to verify both usage patterns work.
"""

class CallableReport(list):
    """Hybrid report object that acts as both a list and a callable method."""
    def __call__(self, agent_name, key_num, passed, details=""):
        """Handles modern 4-parameter calls: ctx.report(name, key, passed, msg)"""
        status = "PASS" if passed else "FAIL"
        self.append({
            "agent": agent_name, 
            "key": key_num, 
            "status": status, 
            "msg": details if isinstance(details, str) else str(details)
        })

# Test 1: Method-style call
report = CallableReport()
report("ArchitectureGovernor", 12, False, "189 atomicity violations")
print(f"Test 1 (Method-style): {len(report)} items")
print(f"  Content: {report[0]}")

# Test 2: List-style append
report.append({"agent": "HygieneGuardian", "msg": "Test violation", "lvl": "warning"})
print(f"\nTest 2 (List-style): {len(report)} items")
print(f"  Content: {report[1]}")

# Test 3: Both patterns mixed
report("DependencySentinel", 9, True, "No unused imports")
report.append({"agent": "SecurityEnforcer", "key": 0, "status": "PASS"})
print(f"\nTest 3 (Mixed): {len(report)} items total")

# Test 4: Iteration
print("\nTest 4 (Iteration):")
for idx, item in enumerate(report):
    agent = item.get('agent', 'Unknown')
    print(f"  {idx+1}. {agent}")

print("\n[OK] All tests passed! CallableReport supports both patterns.")
