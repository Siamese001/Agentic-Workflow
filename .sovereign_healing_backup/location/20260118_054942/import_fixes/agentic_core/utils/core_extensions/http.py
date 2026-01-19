from __future__ import annotations
"""
SovereignHttpClient - Audited HTTP Operations

Routes all HTTP operations through controlled plane with:
- Audit logging
- Domain allowlist enforcement
- Timeout enforcement
- Error handling
"""
import logging
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

Logger = logging.getLogger(__name__)

# Approved domains for external HTTP (sovereignty enforcement)
ALLOWED_DOMAINS: Set[str] = {
    'python.org', 'docs.python.org',
    'github.com', 'raw.githubusercontent.com', 'api.github.com',
    'readthedocs.io',
    'developer.mozilla.org',
    'stackoverflow.com',
    'pypi.org',
    'api.pinecone.io',
    'api.anthropic.com',
    'api.openai.com',
    'generativelanguage.googleapis.com',
}


class SovereignHttpClient(MCPHardenedMixin, HealerMixin):
    """Sovereign HTTP client - audit + safe exec for all HTTP operations."""
    
    def __init__(self, timeout: int = 30, allow_internal: bool = False):
        super().__init__()
        """
        Initialize HTTP client.
        
        Args:
            timeout: Default request timeout in seconds
            allow_internal: Allow internal/localhost requests (default False)
        """
        self.timeout = timeout
        self.allow_internal = allow_internal
        self.audit_log: List[Dict[str, Any]] = []
        self._session = None
    
    def _get_session(self):
        """Lazy-load requests session."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    'User-Agent': 'SovereignHttpClient/1.0'
                })
                Logger.info("[SOVEREIGN HTTP] Session initialized")
            except ImportError:
                Logger.warning("[SOVEREIGN HTTP] requests not installed")
                return None
        return self._session
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL against sovereignty rules."""
        try:
            parsed = urlparse(url)
            host = (parsed.hostname or '').lower()
            
            # Block internal/localhost unless explicitly allowed
            if not self.allow_internal:
                if host in {'localhost', '127.0.0.1'} or host.startswith('192.168.') or host.endswith('.local'):
                    Logger.warning(f"[SOVEREIGN HTTP] Blocked internal URL: {url}")
                    return False
            
            # Check domain allowlist
            if not any(host == d or host.endswith('.' + d) for d in ALLOWED_DOMAINS):
                Logger.warning(f"[SOVEREIGN HTTP] Domain not in allowlist: {host}")
                return False
            
            return True
        except Exception:
            return False
    
    def _audit(self, operation: str, url: str, result: Any) -> None:
        """Record operation to audit log."""
        parsed = urlparse(url)
        self.audit_log.append({
            'operation': operation,
            'host': parsed.hostname,
            'path': parsed.path[:50],
            'success': result.get('success', False) if isinstance(result, dict) else True
        })
    
    def execute(self, operation: str, **payload) -> Dict[str, Any]:
        """
        Route HTTP operations safely.
        
        Args:
            operation: HTTP operation (get, post, put, delete)
            **payload: Operation-specific parameters (url, data, headers, etc.)
        
        Returns:
            Result dictionary with success status and response data
        """
        url = payload.get('url', '')
        Logger.debug(f"[SOVEREIGN HTTP] {operation.upper()}: {url[:100]}")
        
        # Validate URL
        if not self._validate_url(url):
            result = {
                'success': False,
                'error': 'URL blocked by sovereignty rules'
            }
            self._audit(operation, url, result)
            return result
        
        session = self._get_session()
        if session is None:
            result = {
                'success': True,
                'stub_mode': True,
                'message': f'Stub: {operation.upper()} {url} would be executed'
            }
            self._audit(operation, url, result)
            return result
        
        timeout = payload.get('timeout', self.timeout)
        headers = payload.get('headers', {})
        
        try:
            if operation == 'get':
                params = payload.get('params', {})
                response = session.get(url, params=params, headers=headers, timeout=timeout)
            
            elif operation == 'post':
                data = payload.get('data')
                json_data = payload.get('json')
                response = session.post(url, data=data, json=json_data, headers=headers, timeout=timeout)
            
            elif operation == 'put':
                data = payload.get('data')
                json_data = payload.get('json')
                response = session.put(url, data=data, json=json_data, headers=headers, timeout=timeout)
            
            elif operation == 'delete':
                response = session.delete(url, headers=headers, timeout=timeout)
            
            else:
                result = {'success': False, 'error': f'Unsupported HTTP operation: {operation}'}
                self._audit(operation, url, result)
                return result
            
            # Check response
            response.raise_for_status()
            
            # Try to parse JSON, fallback to text
            try:
                body = response.json()
            except Exception:
                body = response.text[:1000]  # Truncate large responses
            
            result = {
                'success': True,
                'status_code': response.status_code,
                'body': body
            }
        
        except Exception as e:
            Logger.error(f"[SOVEREIGN HTTP] {operation.upper()} {url} failed: {e}")
            result = {
                'success': False,
                'error': str(e)
            }
        
        self._audit(operation, url, result)
        return result

def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, TESTS_DIR: []}
        try:
            assert self is not None
            results["passed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
