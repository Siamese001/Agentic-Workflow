#!/usr/bin/env python3
"""
Test the MCP implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import (
    call_external_service,
    get_tool_schemas,
    check_mcp_access,
    get_mcp_client
)

def test_external_service_calls():
    """Test MCP external service calls"""
    print("Testing external service calls...")
    
    # Test successful weather API call
    result = call_external_service(
        user_id="basic_user",
        tool_name="weather_api",
        input_data={"city": "New York", "units": "metric"}
    )
    
    assert "error" not in result, "Should successfully call weather API"
    assert "city" in result, "Should return city information"
    assert "temperature" in result, "Should return temperature"
    assert "timestamp" in result, "Should return timestamp"
    
    print("✅ External service calls test passed")

def test_schema_definitions():
    """Test MCP tool schema definitions"""
    print("Testing schema definitions...")
    
    schemas = get_tool_schemas()
    
    assert len(schemas) > 0, "Should have tool schemas"
    assert "weather_api" in schemas, "Should have weather_api schema"
    
    weather_schema = schemas["weather_api"]
    assert "input_schema" in weather_schema, "Should have input schema"
    assert "output_schema" in weather_schema, "Should have output schema"
    assert "required_permissions" in weather_schema, "Should have permission requirements"
    
    # Validate input schema structure
    input_schema = weather_schema["input_schema"]
    assert "properties" in input_schema, "Input schema should have properties"
    assert "required" in input_schema, "Input schema should have required fields"
    assert "city" in input_schema["required"], "City should be required"
    
    # Validate output schema structure
    output_schema = weather_schema["output_schema"]
    assert "properties" in output_schema, "Output schema should have properties"
    assert "required" in output_schema, "Output schema should have required fields"
    assert len(output_schema["required"]) > 0, "Should have required output fields"
    
    print("✅ Schema definitions test passed")

def test_acl_enforcement():
    """Test MCP access control enforcement"""
    print("Testing ACL enforcement...")
    
    # Test user with read access
    can_access = check_mcp_access("basic_user", "weather_api")
    assert can_access, "Basic user should have read access to weather API"
    
    # Test user without access
    can_access = check_mcp_access("guest", "weather_api")
    assert not can_access, "Guest should not have access to weather API"
    
    # Test actual ACL enforcement in calls
    result = call_external_service(
        user_id="guest",
        tool_name="weather_api",
        input_data={"city": "London"}
    )
    
    assert "error" in result, "Guest should be denied access"
    assert "Access denied" in result["error"], "Should return access denied error"
    
    # Test successful call with proper permissions
    result = call_external_service(
        user_id="power_user",
        tool_name="weather_api",
        input_data={"city": "Tokyo"}
    )
    
    assert "error" not in result, "Power user should be allowed access"
    assert "city" in result, "Should return weather data"
    
    print("✅ ACL enforcement test passed")

def test_interaction_logging():
    """Test MCP interaction logging"""
    print("Testing interaction logging...")
    
    client = get_mcp_client()
    
    # Make some calls to generate logs
    call_external_service("basic_user", "weather_api", {"city": "Paris"})
    call_external_service("power_user", "weather_api", {"city": "Berlin"})
    call_external_service("guest", "weather_api", {"city": "Madrid"})  # Should be denied
    
    # Check interaction history
    interactions = client.get_user_interaction_history("basic_user", limit=10)
    
    assert len(interactions) > 0, "Should have logged interactions for basic_user"
    
    # Check interaction structure
    interaction = interactions[0]
    assert hasattr(interaction, 'timestamp'), "Should have timestamp"
    assert hasattr(interaction, 'user_id'), "Should have user_id"
    assert hasattr(interaction, 'tool_name'), "Should have tool_name"
    assert hasattr(interaction, 'acl_decision'), "Should have ACL decision"
    assert hasattr(interaction, 'success'), "Should have success flag"
    
    assert interaction.user_id == "basic_user", "Should filter by user"
    assert interaction.tool_name == "weather_api", "Should log tool name"
    
    # Check that denied calls are also logged
    guest_interactions = client.get_user_interaction_history("guest", limit=10)
    assert len(guest_interactions) > 0, "Should log denied access attempts"
    assert not guest_interactions[0].success, "Denied calls should be marked as unsuccessful"
    
    # Verify log file was created
    log_file = "mcp_interactions.log"
    assert os.path.exists(log_file), "Should create log file"
    
    # Check log file content
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert len(log_content) > 0, "Log file should not be empty"
        assert "weather_api" in log_content, "Should contain tool names"
        assert "basic_user" in log_content, "Should contain user IDs"
    
    print("✅ Interaction logging test passed")

def test_input_validation():
    """Test input validation"""
    print("Testing input validation...")
    
    # Test missing required field
    result = call_external_service(
        user_id="basic_user",
        tool_name="weather_api",
        input_data={"units": "metric"}  # Missing city
    )
    
    assert "error" in result, "Should reject input missing required fields"
    assert "Invalid input" in result["error"], "Should return validation error"
    
    # Test invalid field type
    result = call_external_service(
        user_id="basic_user",
        tool_name="weather_api",
        input_data={"city": 123, "units": "metric"}  # City should be string
    )
    
    assert "error" in result, "Should reject invalid field types"
    assert "Invalid input" in result["error"], "Should return validation error"
    
    print("✅ Input validation test passed")

def main():
    """Run all MCP tests"""
    print("=== MCP IMPLEMENTATION TEST SUITE ===\n")
    
    try:
        test_external_service_calls()
        test_schema_definitions()
        test_acl_enforcement()
        test_interaction_logging()
        test_input_validation()
        
        print("\n🎉 ALL MCP TESTS PASSED!")
        print("✅ MCP implementation is fully functional")
        print("✅ All 4 MCP validation keys satisfied:")
        print("   - mcp_used_for_external_calls: ✅")
        print("   - mcp_tools_define_input_output_schemas: ✅")
        print("   - mcp_access_respects_acls: ✅")
        print("   - mcp_interactions_logged: ✅")
        return True
        
    except Exception as e:
        print(f"\n❌ MCP TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
