#!/usr/bin/env python3
"""
HTTP Tool
Section 5: Tool Contracts - INFRA tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class HTTPTool:
    """Safe HTTP client"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = self.config.get("timeout", 60)
        self.max_retries = self.config.get("max_retries", 3)
        self.default_headers = self.config.get("default_headers", {"User-Agent": "Agentic-Workflow/1.0"})
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Perform HTTP GET request"""
        try:
            # Simulate HTTP GET response
            response = {
                "status_code": 200,
                "data": {"message": f"GET request to {url} successful"},
                "headers": {**self.default_headers, **(headers or {})},
                "url": url,
                "params": params or {}
            }
            
            logger.info(f"HTTP GET to {url} returned status {response['status_code']}")
            return response
            
        except Exception as e:
            logger.error(f"HTTP GET failed: {e}")
            return {"status_code": 500, "error": str(e), "url": url}
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Perform HTTP POST request"""
        try:
            # Simulate HTTP POST response
            response = {
                "status_code": 201,
                "data": {"message": f"POST request to {url} successful", "received_data": data or json},
                "headers": {**self.default_headers, **(headers or {})},
                "url": url
            }
            
            logger.info(f"HTTP POST to {url} returned status {response['status_code']}")
            return response
            
        except Exception as e:
            logger.error(f"HTTP POST failed: {e}")
            return {"status_code": 500, "error": str(e), "url": url}
    
    def put(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Perform HTTP PUT request"""
        try:
            response = {
                "status_code": 200,
                "data": {"message": f"PUT request to {url} successful", "updated_data": data or json},
                "headers": {**self.default_headers, **(headers or {})},
                "url": url
            }
            
            logger.info(f"HTTP PUT to {url} returned status {response['status_code']}")
            return response
            
        except Exception as e:
            logger.error(f"HTTP PUT failed: {e}")
            return {"status_code": 500, "error": str(e), "url": url}
    
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Perform HTTP DELETE request"""
        try:
            response = {
                "status_code": 204,
                "data": {"message": f"DELETE request to {url} successful"},
                "headers": {**self.default_headers, **(headers or {})},
                "url": url
            }
            
            logger.info(f"HTTP DELETE to {url} returned status {response['status_code']}")
            return response
            
        except Exception as e:
            logger.error(f"HTTP DELETE failed: {e}")
            return {"status_code": 500, "error": str(e), "url": url}
    
    def batch_request(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform multiple HTTP requests"""
        try:
            results = []
            for request in requests:
                method = request.get("method", "GET").lower()
                url = request.get("url", "")
                
                if method == "get":
                    result = self.get(url, request.get("params"), request.get("headers"))
                elif method == "post":
                    result = self.post(url, request.get("data"), request.get("json"), request.get("headers"))
                elif method == "put":
                    result = self.put(url, request.get("data"), request.get("json"), request.get("headers"))
                elif method == "delete":
                    result = self.delete(url, request.get("headers"))
                else:
                    result = {"status_code": 405, "error": f"Method {method} not allowed", "url": url}
                
                results.append(result)
            
            logger.info(f"Batch HTTP requests completed: {len(results)} requests")
            return results
            
        except Exception as e:
            logger.error(f"Batch HTTP requests failed: {e}")
            return [{"status_code": 500, "error": str(e)} for _ in requests]

def create_http_tool(config: Optional[Dict[str, Any]] = None) -> HTTPTool:
    """Factory function to create HTTP tool instance"""
    return HTTPTool(config)

# Re-export components
__all__ = [
    'HTTPTool', 'create_http_tool'
]
