#!/usr/bin/env python3
"""
Test the safety layer implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_core.l5_safety.safety_layer import (
    check_outbound_content_safety, 
    check_mutating_action_safety,
    is_content_safe,
    is_action_safe
)

def test_pii_detection():
    """Test PII detection functionality"""
    print("Testing PII detection...")
    
    # Test email detection
    content_with_email = "Contact me at john.doe@example.com for more information"
    result = check_outbound_content_safety(content_with_email)
    assert not result.is_safe, "Should detect email as PII"
    assert len(result.violations) > 0, "Should have violations"
    
    # Test phone detection
    content_with_phone = "Call me at (555) 123-4567 for assistance"
    result = check_outbound_content_safety(content_with_phone)
    assert not result.is_safe, "Should detect phone as PII"
    
    # Test safe content
    safe_content = "This is a safe message without personal information"
    result = check_outbound_content_safety(safe_content)
    assert result.is_safe, "Should be safe"
    
    print("✅ PII detection tests passed")

def test_injection_detection():
    """Test injection detection functionality"""
    print("Testing injection detection...")
    
    # Test SQL injection
    sql_injection = "SELECT * FROM users WHERE id = 1; DROP TABLE users;"
    result = check_outbound_content_safety(sql_injection)
    assert not result.is_safe, "Should detect SQL injection"
    
    # Test command injection
    cmd_injection = "rm -rf /; cat /etc/passwd"
    result = check_outbound_content_safety(cmd_injection)
    assert not result.is_safe, "Should detect command injection"
    
    # Test XSS
    xss = "<script>alert('xss')</script>"
    result = check_outbound_content_safety(xss)
    assert not result.is_safe, "Should detect XSS"
    
    print("✅ Injection detection tests passed")

def test_mutating_action_safety():
    """Test mutating action safety checks"""
    print("Testing mutating action safety...")
    
    # Safe action
    safe_action = {
        "type": "update",
        "target": "user_profile",
        "data": {"name": "John Doe"}
    }
    result = check_mutating_action_safety(safe_action)
    assert result.is_safe, "Safe action should pass"
    
    # Dangerous action
    dangerous_action = {
        "type": "delete",
        "target": "database",
        "command": "DROP DATABASE production;"
    }
    result = check_mutating_action_safety(dangerous_action)
    assert not result.is_safe, "Dangerous action should be blocked"
    
    print("✅ Mutating action safety tests passed")

def test_convenience_functions():
    """Test convenience functions"""
    print("Testing convenience functions...")
    
    # Test is_content_safe
    assert is_content_safe("This is safe content"), "Safe content should return True"
    assert not is_content_safe("email@example.com"), "Unsafe content should return False"
    
    # Test is_action_safe
    safe_action = {"type": "read", "target": "file"}
    assert is_action_safe(safe_action), "Safe action should return True"
    
    print("✅ Convenience function tests passed")

def main():
    """Run all safety tests"""
    print("=== SAFETY LAYER TEST SUITE ===\n")
    
    try:
        test_pii_detection()
        test_injection_detection()
        test_mutating_action_safety()
        test_convenience_functions()
        
        print("\n🎉 ALL SAFETY TESTS PASSED!")
        print("✅ Safety layer is fully functional")
        return True
        
    except Exception as e:
        print(f"\n❌ SAFETY TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)





