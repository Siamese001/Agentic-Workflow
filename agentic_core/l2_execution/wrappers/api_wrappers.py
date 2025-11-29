#!/usr/bin/env python3
"""
API Wrappers
Section 5: Tool Contracts - Wrapper classes for external API integrations
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class APIWrapper:
    """Base wrapper class for external API integrations"""
    
    def __init__(self, api_name: str, base_url: str, config: Optional[Dict[str, Any]] = None):
        self.api_name = api_name
        self.base_url = base_url
        self.config = config or {}
        self.headers = self.config.get("headers", {})
        self.timeout = self.config.get("timeout", 30)
    
    def make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make API request to specified endpoint"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            # Simplified implementation - in production would use requests library
            result = {
                "url": url,
                "method": method,
                "data": data,
                "headers": self.headers,
                "status": "success",
                "response": f"Mock response from {self.api_name}"
            }
            
            logger.info(f"API request to {self.api_name} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def set_auth(self, auth_token: str) -> None:
        """Set authentication token"""
        self.headers["Authorization"] = f"Bearer {auth_token}"
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure API wrapper"""
        self.config.update(config)
        self.headers = self.config.get("headers", {})
        self.timeout = self.config.get("timeout", 30)

class OpenAIWrapper(APIWrapper):
    """Wrapper for OpenAI API"""
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        super().__init__("openai", "https://api.openai.com/v1", config)
        self.set_auth(api_key)
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """Make chat completion request"""
        data = {
            "model": model,
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7)
        }
        return self.make_request("chat/completions", "POST", data)

class RESTAPIWrapper(APIWrapper):
    """Generic REST API wrapper"""
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self.make_request(endpoint, "GET", params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request"""
        return self.make_request(endpoint, "POST", data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return self.make_request(endpoint, "PUT", data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return self.make_request(endpoint, "DELETE")

def create_api_wrapper(api_type: str, config: Dict[str, Any]) -> APIWrapper:
    """Factory function to create appropriate API wrapper"""
    if api_type == "openai":
        return OpenAIWrapper(config.get("api_key"), config)
    elif api_type == "rest":
        return RESTAPIWrapper(config.get("name", "rest_api"), config.get("base_url", ""), config)
    else:
        return APIWrapper(api_type, config.get("base_url", ""), config)

# Re-export components
__all__ = [
    'APIWrapper', 'OpenAIWrapper', 'RESTAPIWrapper', 'create_api_wrapper'
]





