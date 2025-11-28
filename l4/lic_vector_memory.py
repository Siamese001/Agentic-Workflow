"""LIC Vector Memory - L4 memory/state adapter for vector database operations.

Implements nuclear prompt requirements for deterministic vector memory:
- Provide typed adapter over existing vector DB client for LIC research
- L4 only: memory/state, no planning or orchestration
- Async interface using existing vector client abstractions
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class LICVectorMemory:
    """L4 memory adapter for vector database operations in LIC research.
    
    Provides typed interface over existing vector client abstractions
    for research signal storage and retrieval.
    """
    
    def __init__(self, vector_client: Optional[Any] = None) -> None:
        """Initialize LIC vector memory with vector client."""
        self.vector_client = vector_client
        
        if not self.vector_client:
            logger.warning("No vector client provided to LICVectorMemory - operations will be no-ops")
    
    async def query(self, query_text: str, *, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query vector database for relevant documents.
        
        Args:
            query_text: The query text to search for
            top_k: Maximum number of results to return
            
        Returns:
            List of document results with metadata
        """
        if not self.vector_client:
            logger.debug("No vector client available - returning empty results")
            return []
        
        try:
            # Use existing vector client query interface
            # This assumes the client has a query method with similar signature
            results = await self.vector_client.query(
                query_text=query_text,
                top_k=top_k,
                include_metadata=True,
            )
            
            # Normalize results to expected format
            normalized_results = []
            for result in results:
                normalized_result = {
                    "id": result.get("id", ""),
                    "text": result.get("text", result.get("content", "")),
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", result.get("similarity", 0.0)),
                    "source": result.get("source", "vector_db"),
                }
                normalized_results.append(normalized_result)
            
            logger.debug(f"Vector query returned {len(normalized_results)} results")
            return normalized_results
            
        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            return []
    
    async def upsert_signals(self, signals: List[Dict[str, Any]]) -> None:
        """Upsert research signals to vector database.
        
        Args:
            signals: List of signals to store with embeddings
        """
        if not self.vector_client:
            logger.debug("No vector client available - skipping upsert")
            return
        
        if not signals:
            logger.debug("No signals to upsert")
            return
        
        try:
            # Prepare signals for vector client
            vector_documents = []
            for signal in signals:
                document = {
                    "id": signal.get("id", ""),
                    "text": signal.get("text", signal.get("content", "")),
                    "metadata": {
                        "signal_type": signal.get("signal_type", "unknown"),
                        "source": signal.get("source", "lic_research"),
                        "timestamp": signal.get("timestamp", ""),
                        "company_name": signal.get("company_name", ""),
                        "role_title": signal.get("role_title", ""),
                        **signal.get("metadata", {}),
                    },
                }
                vector_documents.append(document)
            
            # Use existing vector client upsert interface
            await self.vector_client.upsert(documents=vector_documents)
            
            logger.debug(f"Upserted {len(vector_documents)} signals to vector database")
            
        except Exception as e:
            logger.error(f"Vector upsert failed: {e}")
    
    async def delete_signals(self, signal_ids: List[str]) -> None:
        """Delete signals from vector database.
        
        Args:
            signal_ids: List of signal IDs to delete
        """
        if not self.vector_client:
            logger.debug("No vector client available - skipping delete")
            return
        
        if not signal_ids:
            logger.debug("No signal IDs to delete")
            return
        
        try:
            # Use existing vector client delete interface
            await self.vector_client.delete(ids=signal_ids)
            
            logger.debug(f"Deleted {len(signal_ids)} signals from vector database")
            
        except Exception as e:
            logger.error(f"Vector delete failed: {e}")
    
    async def get_signal_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific signal by ID from vector database.
        
        Args:
            signal_id: The ID of the signal to retrieve
            
        Returns:
            Signal data if found, None otherwise
        """
        if not self.vector_client:
            logger.debug("No vector client available - cannot get signal by ID")
            return None
        
        try:
            # Use existing vector client get interface
            result = await self.vector_client.get(id=signal_id)
            
            if result:
                normalized_result = {
                    "id": result.get("id", signal_id),
                    "text": result.get("text", result.get("content", "")),
                    "metadata": result.get("metadata", {}),
                    "score": 1.0,  # Exact match gets perfect score
                    "source": result.get("source", "vector_db"),
                }
                return normalized_result
            
            return None
            
        except Exception as e:
            logger.error(f"Get signal by ID failed: {e}")
            return None
    
    async def list_signals_by_type(self, signal_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List signals of a specific type from vector database.
        
        Args:
            signal_type: The type of signals to list
            limit: Maximum number of signals to return
            
        Returns:
            List of signals of the specified type
        """
        if not self.vector_client:
            logger.debug("No vector client available - returning empty list")
            return []
        
        try:
            # Use existing vector client filter interface
            # This assumes the client supports metadata filtering
            results = await self.vector_client.filter(
                metadata_filter={"signal_type": signal_type},
                limit=limit,
            )
            
            # Normalize results
            normalized_results = []
            for result in results:
                normalized_result = {
                    "id": result.get("id", ""),
                    "text": result.get("text", result.get("content", "")),
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 1.0),
                    "source": result.get("source", "vector_db"),
                }
                normalized_results.append(normalized_result)
            
            logger.debug(f"Listed {len(normalized_results)} signals of type {signal_type}")
            return normalized_results
            
        except Exception as e:
            logger.error(f"List signals by type failed: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the vector memory connection.
        
        Returns:
            Health status information
        """
        health_status = {
            "available": self.vector_client is not None,
            "connected": False,
            "error": None,
        }
        
        if not self.vector_client:
            health_status["error"] = "No vector client configured"
            return health_status
        
        try:
            # Attempt a simple query to check connectivity
            await self.vector_client.query(query_text="health_check", top_k=1)
            health_status["connected"] = True
            
        except Exception as e:
            health_status["connected"] = False
            health_status["error"] = str(e)
            logger.error(f"Vector memory health check failed: {e}")
        
        return health_status
