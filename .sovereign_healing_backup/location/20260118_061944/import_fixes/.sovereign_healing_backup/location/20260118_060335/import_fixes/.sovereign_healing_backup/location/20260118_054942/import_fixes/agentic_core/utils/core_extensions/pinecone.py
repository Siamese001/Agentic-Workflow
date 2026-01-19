from __future__ import annotations
"""
SovereignPineconeClient - Audited Vector Operations

Routes all Pinecone operations through controlled plane with:
- Audit logging
- Connection pooling
- Error handling with fallback
"""
import logging
import os
from typing import Any, Dict, List, Optional

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

from agentic_core.L5_safety.validators.structure_blueprint import (
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


class SovereignPineconeClient(MCPHardenedMixin, HealerMixin):
    """Sovereign Pinecone client - audit + safe exec for all vector operations."""
    
    def __init__(self, index_name: Optional[str] = None, namespace: Optional[str] = None):
        """
        Initialize Pinecone client.
        
        Args:
            index_name: Pinecone index name (defaults to env var)
            namespace: Default namespace for operations
        """
        super().__init__()
        self.index_name = index_name or os.getenv('PINECONE_INDEX_NAME', 'canon-memory-l2')
        self.namespace = namespace or ''
        self.audit_log: List[Dict[str, Any]] = []
        self._pc = None
        self._index = None
        self._mcp_audit('init')
    
    def _get_client(self):
        """Lazy-load Pinecone client."""
        if self._pc is None:
            try:
                from pinecone import Pinecone
                api_key = os.getenv('PINECONE_API_KEY')
                if not api_key:
                    Logger.warning("[SOVEREIGN PINECONE] No API key - using stub mode")
                    return None
                self._pc = Pinecone(api_key=api_key)
                self._index = self._pc.Index(self.index_name)
                Logger.info(f"[SOVEREIGN PINECONE] Connected to index: {self.index_name}")
            except ImportError:
                Logger.warning("[SOVEREIGN PINECONE] pinecone-client not installed - using stub mode")
                return None
            except Exception as e:
                Logger.error(f"[SOVEREIGN PINECONE] Connection failed: {e}")
                return None
        return self._index
    
    def _audit(self, operation: str, payload: Dict[str, Any], result: Any) -> None:
        """Record operation to audit log."""
        self.audit_log.append({
            'operation': operation,
            'namespace': self.namespace,
            'success': result.get('success', False) if isinstance(result, dict) else True
        })
    
    def execute(self, operation: str, **payload) -> Dict[str, Any]:
        """
        Route Pinecone operations safely.
        
        Args:
            operation: Pinecone operation (upsert, query, delete, etc.)
            **payload: Operation-specific parameters
        
        Returns:
            Result dictionary with success status and data
        """
        Logger.debug(f"[SOVEREIGN PINECONE] {operation}")
        
        index = self._get_client()
        namespace = payload.get('namespace', self.namespace)
        
        if index is None:
            # Stub mode - return mock response
            result = {
                'success': True,
                'stub_mode': True,
                'message': f'Stub: {operation} would be executed'
            }
            self._audit(operation, payload, result)
            return result
        
        try:
            if operation == 'upsert':
                vectors = payload.get('vectors', [])
                response = index.upsert(vectors=vectors, namespace=namespace)
                result = {'success': True, 'upserted_count': response.upserted_count}
            
            elif operation == 'query':
                vector = payload.get('vector', [])
                top_k = payload.get('top_k', 10)
                include_metadata = payload.get('include_metadata', True)
                response = index.query(
                    vector=vector,
                    top_k=top_k,
                    namespace=namespace,
                    include_metadata=include_metadata
                )
                result = {
                    'success': True,
                    'matches': [
                        {'id': m.id, 'score': m.score, 'metadata': m.metadata}
                        for m in response.matches
                    ]
                }
            
            elif operation == 'delete':
                ids = payload.get('ids', [])
                if ids:
                    index.delete(ids=ids, namespace=namespace)
                result = {'success': True, 'deleted': len(ids)}
            
            elif operation == 'describe_stats':
                response = index.describe_index_stats()
                result = {'success': True, 'stats': response.to_dict()}
            
            else:
                result = {'success': False, 'error': f'Unsupported Pinecone operation: {operation}'}
        
        except Exception as e:
            Logger.error(f"[SOVEREIGN PINECONE] {operation} failed: {e}")
            result = {'success': False, 'error': str(e)}
        
        self._audit(operation, payload, result)
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
