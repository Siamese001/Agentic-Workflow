#!/usr/bin/env python3
"""
REST Interface
Section 18: Deployment Layer - REST API interface for agentic core
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class HTTPMethod(str, Enum):
    """HTTP method enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    max_connections: int = 100

class RESTInterface:
    """REST API interface for agentic core deployment"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.endpoints: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, str] = {}
    
    def register_endpoint(self, path: str, method: HTTPMethod, handler: callable) -> bool:
        """Register REST endpoint"""
        try:
            if path not in self.endpoints:
                self.endpoints[path] = {}
            self.endpoints[path][method.value] = handler
            logger.info(f"Endpoint registered: {method.value} {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to register endpoint: {e}")
            return False
    
    def handle_request(self, path: str, method: HTTPMethod, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle REST request"""
        if path in self.endpoints and method.value in self.endpoints[path]:
            handler = self.endpoints[path][method.value]
            try:
                return handler(data or {})
            except Exception as e:
                return {"error": str(e), "status": "error"}
        else:
            return {"error": "Endpoint not found", "status": "404"}

# Re-export components
__all__ = [
    'RESTInterface', 'DeploymentConfig', 'HTTPMethod'
]





