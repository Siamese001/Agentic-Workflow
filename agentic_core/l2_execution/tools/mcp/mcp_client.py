#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Client Implementation
Provides external service integration with schema validation, ACL enforcement, and logging
"""

import json
import logging
import requests
import hashlib
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import os
import re

logger = logging.getLogger(__name__)

class MCPPermission(Enum):
    """MCP access permission levels"""
    DENY = "deny"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

@dataclass
class MCPSchema:
    """MCP tool schema definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required_permissions: List[MCPPermission]
    rate_limit: Optional[int] = None
    timeout: int = 30

@dataclass
class MCPInteraction:
    """MCP interaction log entry"""
    timestamp: str
    user_id: str
    tool_name: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    acl_decision: str
    success: bool
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None

class MCPACLManager:
    """MCP Access Control List Manager"""
    
    def __init__(self):
        self.user_permissions = self._load_user_permissions()
        self.tool_permissions = self._load_tool_permissions()
    
    def _load_user_permissions(self) -> Dict[str, List[MCPPermission]]:
        """Load user permissions from configuration"""
        # In production, this would load from database or config file
        return {
            "admin_user": [MCPPermission.ADMIN, MCPPermission.WRITE, MCPPermission.READ],
            "power_user": [MCPPermission.WRITE, MCPPermission.READ],
            "basic_user": [MCPPermission.READ],
            "guest": []
        }
    
    def _load_tool_permissions(self) -> Dict[str, List[MCPPermission]]:
        """Load tool permission requirements"""
        return {
            "weather_api": [MCPPermission.READ],
            "search_api": [MCPPermission.READ],
            "data_api": [MCPPermission.WRITE, MCPPermission.READ],
            "admin_api": [MCPPermission.ADMIN]
        }
    
    def check_access(self, user_id: str, tool_name: str, required_permissions: List[MCPPermission]) -> bool:
        """Check if user has access to tool"""
        user_perms = self.user_permissions.get(user_id, [])
        
        for perm in required_permissions:
            if perm not in user_perms:
                return False
        
        return True
    
    def get_acl_decision(self, user_id: str, tool_name: str, required_permissions: List[MCPPermission]) -> str:
        """Get detailed ACL decision"""
        if not self.check_access(user_id, tool_name, required_permissions):
            return "DENIED - Insufficient permissions"
        return "ALLOWED - All required permissions present"

class MCPLogger:
    """MCP Interaction Logger"""
    
    def __init__(self, log_file: str = "mcp_interactions.log"):
        self.log_file = log_file
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log_interaction(self, interaction: MCPInteraction):
        """Log MCP interaction"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                log_entry = json.dumps(asdict(interaction), default=str)
                f.write(log_entry + '\n')
            
            # Also log to application logger
            logger.info(f"MCP Interaction: {interaction.tool_name} by {interaction.user_id} - {interaction.acl_decision}")
            
        except Exception as e:
            logger.error(f"Failed to log MCP interaction: {e}")
    
    def get_user_interactions(self, user_id: str, limit: int = 100) -> List[MCPInteraction]:
        """Get interactions for a specific user"""
        interactions = []
        
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            if data.get('user_id') == user_id:
                                interactions.append(MCPInteraction(**data))
                                if len(interactions) >= limit:
                                    break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Failed to read MCP interactions: {e}")
        
        return interactions

class MCPTool:
    """Base MCP Tool implementation"""
    
    def __init__(self, schema: MCPSchema, acl_manager: MCPACLManager, logger: MCPLogger):
        self.schema = schema
        self.acl_manager = acl_manager
        self.logger = logger
        self.name = schema.name
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input against schema"""
        # Simple validation - in production would use jsonschema
        required_fields = self.schema.input_schema.get('required', [])
        for field in required_fields:
            if field not in input_data:
                return False
        
        # Check field types
        properties = self.schema.input_schema.get('properties', {})
        for field, value in input_data.items():
            if field in properties:
                expected_type = properties[field].get('type')
                if expected_type == 'string' and not isinstance(value, str):
                    return False
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    return False
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    return False
        
        return True
    
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate output against schema"""
        # Simple validation
        required_fields = self.schema.output_schema.get('required', [])
        for field in required_fields:
            if field not in output_data:
                return False
        return True
    
    def execute(self, user_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the MCP tool with ACL checks and logging"""
        start_time = datetime.now()
        
        # Check ACL
        acl_decision = self.acl_manager.get_acl_decision(user_id, self.name, self.schema.required_permissions)
        is_allowed = acl_decision.startswith("ALLOWED")
        
        # Create interaction log
        interaction = MCPInteraction(
            timestamp=start_time.isoformat(),
            user_id=user_id,
            tool_name=self.name,
            input_data=input_data,
            output_data=None,
            acl_decision=acl_decision,
            success=False
        )
        
        if not is_allowed:
            interaction.error_message = "Access denied by ACL"
            self.logger.log_interaction(interaction)
            return {"error": "Access denied", "reason": acl_decision}
        
        # Validate input
        if not self.validate_input(input_data):
            interaction.error_message = "Input validation failed"
            self.logger.log_interaction(interaction)
            return {"error": "Invalid input", "schema": self.schema.input_schema}
        
        # Execute the tool
        try:
            result = self._execute_implementation(input_data)
            
            # Validate output
            if not self.validate_output(result):
                interaction.error_message = "Output validation failed"
                self.logger.log_interaction(interaction)
                return {"error": "Invalid output", "result": result}
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            # Update interaction with success
            interaction.output_data = result
            interaction.success = True
            interaction.execution_time_ms = execution_time
            
            self.logger.log_interaction(interaction)
            return result
            
        except Exception as e:
            interaction.error_message = str(e)
            self.logger.log_interaction(interaction)
            return {"error": "Execution failed", "details": str(e)}
    
    def _execute_implementation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_implementation")

class WeatherAPITool(MCPTool):
    """Weather API MCP Tool"""
    
    def __init__(self, acl_manager: MCPACLManager, logger: MCPLogger):
        schema = MCPSchema(
            name="weather_api",
            description="Get weather information for a city",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}
                },
                "required": ["city"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "temperature": {"type": "number"},
                    "description": {"type": "string"},
                    "humidity": {"type": "number"},
                    "timestamp": {"type": "string"}
                },
                "required": ["city", "temperature", "description", "timestamp"]
            },
            required_permissions=[MCPPermission.READ]
        )
        super().__init__(schema, acl_manager, logger)
    
    def _execute_implementation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weather API call"""
        city = input_data["city"]
        units = input_data.get("units", "metric")
        
        # Using OpenWeatherMap API (free tier)
        # In production, API key would be stored securely
        api_key = os.getenv("OPENWEATHER_API_KEY", "demo_key")
        
        if api_key == "demo_key":
            # Return demo data if no API key
            return {
                "city": city,
                "temperature": 22.5 if units == "metric" else 72.5,
                "description": "partly cloudy",
                "humidity": 65,
                "timestamp": datetime.now().isoformat(),
                "units": units,
                "source": "demo_data"
            }
        
        # Make actual API call
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}"
        
        response = requests.get(url, timeout=self.schema.timeout)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "timestamp": datetime.now().isoformat(),
            "units": units,
            "source": "openweathermap_api"
        }

class MCPClient:
    """Main MCP Client"""
    
    def __init__(self):
        self.acl_manager = MCPACLManager()
        self.logger = MCPLogger()
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, MCPTool]:
        """Register available MCP tools"""
        tools = {}
        
        # Register weather API tool
        weather_tool = WeatherAPITool(self.acl_manager, self.logger)
        tools[weather_tool.name] = weather_tool
        
        return tools
    
    def get_tool_schema(self, tool_name: str) -> Optional[MCPSchema]:
        """Get schema for a specific tool"""
        tool = self.tools.get(tool_name)
        return tool.schema if tool else None
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
    
    def call_tool(self, user_id: str, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with full ACL and logging"""
        tool = self.tools.get(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found", "available_tools": self.list_tools()}
        
        return tool.execute(user_id, input_data)
    
    def get_user_interaction_history(self, user_id: str, limit: int = 100) -> List[MCPInteraction]:
        """Get interaction history for a user"""
        return self.logger.get_user_interactions(user_id, limit)

# Global MCP client instance
_mcp_client = None

def get_mcp_client() -> MCPClient:
    """Get the global MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client

# Convenience functions
def call_external_service(user_id: str, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Call external service through MCP"""
    client = get_mcp_client()
    return client.call_tool(user_id, tool_name, input_data)

def get_tool_schemas() -> Dict[str, Dict[str, Any]]:
    """Get all tool schemas"""
    client = get_mcp_client()
    schemas = {}
    for tool_name in client.list_tools():
        schema = client.get_tool_schema(tool_name)
        if schema:
            schemas[tool_name] = asdict(schema)
    return schemas

def check_mcp_access(user_id: str, tool_name: str) -> bool:
    """Check if user has access to MCP tool"""
    client = get_mcp_client()
    schema = client.get_tool_schema(tool_name)
    if not schema:
        return False
    return client.acl_manager.check_access(user_id, tool_name, schema.required_permissions)





