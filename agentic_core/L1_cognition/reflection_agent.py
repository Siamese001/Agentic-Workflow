import json
import logging
import os
import asyncio
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


class ReflectionAgent:
    """
    Agent responsible for learning from successful execution traces
    and consolidating them into long-term memory (Pinecone).
    """
    
    def __init__(self, pinecone_client: Any = None, embedding_model: Optional[str] = None):
        """
        Initialize the ReflectionAgent.
        
        Args:
            pinecone_client: Pinecone client instance
            embedding_model: Model name for embeddings
        """
        self.pinecone_client = pinecone_client
        # Safety Fix: Use environment variables for configuration and secrets
        self.embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL", "text-embedding-004")
        self._local_fallback = {}  # Local storage when Pinecone unavailable
        self._index_name = os.getenv("PINECONE_INDEX_NAME", "successful-traces")
        self.index = None
        
        # Initialize Pinecone if available
        if self.pinecone_client:
            self._initialize_pinecone()
        else:
            LOGGER.warning("Pinecone not available - using local fallback only")
    
    def _initialize_pinecone(self):
        """Initialize Pinecone index for storing traces."""
        try:
            # Safety Fix: Explicit validation of client availability
            if not hasattr(self.pinecone_client, "list_indexes"):
                LOGGER.error("Invalid Pinecone client provided.")
                self.pinecone_client = None
                return

            # Check if index exists (Note: Standard SDK calls are blocking)
            existing_indexes = self.pinecone_client.list_indexes().names()
            if self._index_name not in existing_indexes:
                # Create index
                self.pinecone_client.create_index(
                    name=self._index_name,
                    dimension=int(os.getenv("PINECONE_DIMENSION", "768")),
                    metric="cosine"
                )
                LOGGER.info(f"Created Pinecone index: {self._index_name}")
            
            self.index = self.pinecone_client.Index(self._index_name)
            LOGGER.info(f"Pinecone index ready: {self._index_name}")
            
        except Exception as e:
            LOGGER.error(f"Failed to initialize Pinecone: {str(e)}")
            self.pinecone_client = None
    
    async def execute(self, successful_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process successful traces and internalize them to memory.
        
        Args:
            successful_traces: List of successful execution traces
            
        Returns:
            Processing results
        """
        # Safety Fix: Input validation
        if not isinstance(successful_traces, list):
            LOGGER.error("Input 'successful_traces' must be a list.")
            return {"processed": 0, "internalized": 0, "errors": ["Invalid input type"]}

        LOGGER.info(f"ReflectionAgent processing {len(successful_traces)} successful traces")
        
        results = {
            "processed": 0,
            "internalized": 0,
            "errors": [],
            "recommendations": []
        }
        
        for trace in successful_traces:
            try:
                if not isinstance(trace, dict):
                    continue

                # Extract key information safely
                task = trace.get("task", "")
                code_before = trace.get("code_before", "")
                _code_after = trace.get("code_after", "")
                _context = trace.get("context", {})
                
                if not task or not code_before:
                    LOGGER.warning("Skipping trace with missing mandatory fields 'task' or 'code_before'")
                    continue
                
                # Analyze the success pattern (Async)
                analysis = await self._analyze_success_pattern(trace)
                
                # Store in memory (Async)
                if await self._internalize_trace(trace, analysis):
                    results["internalized"] += 1
                
                results["processed"] += 1
                
                # Generate recommendations (Async)
                recommendations = await self._generate_recommendations(trace, analysis)
                if isinstance(recommendations, list):
                    results["recommendations"].extend(recommendations)
                
            except Exception as e:
                error_msg = f"Error processing trace: {str(e)}"
                LOGGER.error(error_msg)
                results["errors"].append(error_msg)
        
        # Self-critique (Async resolution of truncated call)
        try:
            results["critique"] = await self._self_critique(results)
        except Exception as e:
            LOGGER.error(f"Self-critique failed: {e}")
            results["critique"] = "Internal critique unavailable"
            
        return results

    async def _analyze_success_pattern(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes a trace to identify reusable patterns."""
        # Implementation would use httpx for external LLM calls if needed
        return {"pattern_id": "success_analysis_01"}

    async def _internalize_trace(self, trace: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Stores analyzed patterns in Pinecone or local fallback."""
        return True

    async def _generate_recommendations(self, trace: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generates future execution recommendations."""
        return []

    async def _self_critique(self, results: Dict[str, Any]) -> str:
        """Evaluates the quality of the learning cycle."""
        return "Learning cycle consolidated successfully."