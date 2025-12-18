"""
L5 Learning Loop & Pinecone Memory Consolidation

Implements the ReflectionAgent that learns from successful traces
and stores them in Pinecone for cross-cycle recall.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


class ReflectionAgent:
    """
    Agent responsible for learning from successful execution traces
    and consolidating them into long-term memory (Pinecone).
    """
    
    def __init__(self, pinecone_client=None, embedding_model="text-embedding-004"):
        """
        Initialize the ReflectionAgent.
        
        Args:
            pinecone_client: Pinecone client instance
            embedding_model: Model name for embeddings
        """
        self.pinecone_client = pinecone_client
        self.embedding_model = embedding_model
        self._local_fallback = {}  # Local storage when Pinecone unavailable
        self._index_name = "successful-traces"
        
        # Initialize Pinecone if available
        if self.pinecone_client:
            self._initialize_pinecone()
        else:
            LOGGER.warning("Pinecone not available - using local fallback only")
    
    def _initialize_pinecone(self):
        """Initialize Pinecone index for storing traces."""
        try:
            # Check if index exists
            if self._index_name not in self.pinecone_client.list_indexes().names():
                # Create index
                self.pinecone_client.create_index(
                    name=self._index_name,
                    dimension=768,  # Dimension for text-embedding-004
                    metric="cosine"
                )
                LOGGER.info(f"Created Pinecone index: {self._index_name}")
            
            self.index = self.pinecone_client.Index(self._index_name)
            LOGGER.info(f"Pinecone index ready: {self._index_name}")
            
        except Exception as e:
            LOGGER.error(f"Failed to initialize Pinecone: {e}")
            self.pinecone_client = None
    
    async def execute(self, successful_traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process successful traces and internalize them to memory.
        
        Args:
            successful_traces: List of successful execution traces
            
        Returns:
            Processing results
        """
        LOGGER.info(f"ReflectionAgent processing {len(successful_traces)} successful traces")
        
        results = {
            "processed": 0,
            "internalized": 0,
            "errors": [],
            "recommendations": []
        }
        
        for trace in successful_traces:
            try:
                # Extract key information from trace
                task = trace.get("task", "")
                code_before = trace.get("code_before", "")
                code_after = trace.get("code_after", "")
                context = trace.get("context", {})
                
                if not task or not code_before:
                    LOGGER.warning("Skipping trace with missing task or code")
                    continue
                
                # Analyze the success pattern
                analysis = await self._analyze_success_pattern(trace)
                
                # Store in memory
                if await self._internalize_trace(trace, analysis):
                    results["internalized"] += 1
                
                results["processed"] += 1
                
                # Generate recommendations
                recommendations = await self._generate_recommendations(trace, analysis)
                results["recommendations"].extend(recommendations)
                
            except Exception as e:
                error_msg = f"Error processing trace: {e}"
                LOGGER.error(error_msg)
                results["errors"].append(error_msg)
        
        # Self-critique
        critique = await self._self_critique(successful_traces, results)
        results["critique"] = critique
        
        LOGGER.info(f"Reflection complete: {results['processed']} processed, {results['internalized']} internalized")
        
        return results
    
    async def _analyze_success_pattern(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a successful trace to identify patterns.
        
        Args:
            trace: Execution trace
            
        Returns:
            Pattern analysis
        """
        analysis = {
            "pattern_type": "unknown",
            "key_changes": [],
            "success_factors": [],
            "confidence": 0.5
        }
        
        # Extract before/after code
        code_before = trace.get("code_before", "")
        code_after = trace.get("code_after", "")
        
        # Identify key changes
        if code_before and code_after:
            # Simple diff analysis
            before_lines = set(code_before.split('\n'))
            after_lines = set(code_after.split('\n'))
            
            added = after_lines - before_lines
            removed = before_lines - after_lines
            
            analysis["key_changes"] = {
                "added": list(added)[:5],  # Limit to top 5
                "removed": list(removed)[:5]
            }
            
            # Identify pattern type
            if any("import" in line for line in added):
                analysis["pattern_type"] = "import_fix"
            elif any("def " in line for line in added):
                analysis["pattern_type"] = "function_addition"
            elif any("class " in line for line in added):
                analysis["pattern_type"] = "class_addition"
            elif any("return" in line for line in added):
                analysis["pattern_type"] = "return_fix"
        
        # Extract success factors
        signals = trace.get("signals", [])
        if "TESTS_PASS" in signals:
            analysis["success_factors"].append("test_compliance")
        if "STYLE_PASS" in signals:
            analysis["success_factors"].append("style_compliance")
        
        # Calculate confidence based on signal strength
        if signals:
            analysis["confidence"] = min(0.9, 0.5 + len(signals) * 0.1)
        
        return analysis
    
    async def _internalize_trace(self, trace: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """
        Store a trace in long-term memory.
        
        Args:
            trace: Execution trace
            analysis: Pattern analysis
            
        Returns:
            True if successfully stored
        """
        # Create embedding content
        task = trace.get("task", "")
        code_before = trace.get("code_before", "")
        context = trace.get("context", {})
        
        # Combine task and code for embedding
        content = f"Task: {task}\n\nCode Before:\n{code_before}\n\nContext: {json.dumps(context, default=str)}"
        
        # Generate embedding
        embedding = await self._generate_embedding(content)
        
        if embedding is None:
            # Fallback to local storage
            trace_id = f"trace_{len(self._local_fallback)}"
            self._local_fallback[trace_id] = {
                "trace": trace,
                "analysis": analysis,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            LOGGER.info(f"Stored trace locally: {trace_id}")
            return True
        
        # Store in Pinecone
        try:
            metadata = {
                "task": task[:1000],  # Limit metadata size
                "pattern_type": analysis["pattern_type"],
                "confidence": str(analysis["confidence"]),
                "timestamp": datetime.utcnow().isoformat(),
                "success_factors": ",".join(analysis["success_factors"])
            }
            
            self.index.upsert(
                vectors=[{
                    "id": f"trace_{datetime.utcnow().timestamp()}",
                    "values": embedding,
                    "metadata": metadata
                }]
            )
            
            LOGGER.info("Trace internalized to Pinecone")
            return True
            
        except Exception as e:
            LOGGER.error(f"Failed to store in Pinecone: {e}")
            # Fallback to local storage
            trace_id = f"trace_{len(self._local_fallback)}"
            self._local_fallback[trace_id] = {
                "trace": trace,
                "analysis": analysis,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            LOGGER.info(f"Stored trace locally after Pinecone failure: {trace_id}")
            return True
    
    async def _generate_embedding(self, content: str) -> Optional[List[float]]:
        """
        Generate embedding for content.
        
        Args:
            content: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.pinecone_client:
            return None
        
        try:
            # Try to use Google Generative AI for embeddings
            import google.generativeai as genai
            
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                LOGGER.warning("GOOGLE_API_KEY not found")
                return None
            
            genai.configure(api_key=api_key)
            
            # Generate embedding using text-embedding-004
            result = genai.embed_content(
                model=f"models/{self.embedding_model}",
                content=content,
                task_type="retrieval_document"
            )
            
            return result["embedding"]
            
        except ImportError:
            LOGGER.warning("google.generativeai not installed")
            return None
        except Exception as e:
            LOGGER.error(f"Failed to generate embedding: {e}")
            return None
    
    async def _generate_recommendations(self, trace: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on successful patterns.
        
        Args:
            trace: Execution trace
            analysis: Pattern analysis
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        pattern_type = analysis["pattern_type"]
        confidence = analysis["confidence"]
        
        if confidence > 0.7:
            if pattern_type == "import_fix":
                recommendations.append("Consider standardizing import organization across modules")
            elif pattern_type == "function_addition":
                recommendations.append("Document new functions for future reference")
            elif pattern_type == "class_addition":
                recommendations.append("Update class documentation and diagrams")
        
        # General recommendations
        if analysis["success_factors"]:
            recommendations.append(f"Maintain focus on: {', '.join(analysis['success_factors'])}")
        
        return recommendations
    
    async def _self_critique(self, traces: List[Dict[str, Any]], results: Dict[str, Any]) -> str:
        """
        Perform self-critique and recommend next actions.
        
        Args:
            traces: Processed traces
            results: Processing results
            
        Returns:
            Critique recommendation
        """
        success_rate = results["internalized"] / max(1, results["processed"])
        
        if success_rate > 0.8:
            return "CONVERGE_AND_COMMIT"
        elif success_rate > 0.5:
            return "CONTINUE_LEARNING"
        else:
            return "ROLLBACK"
    
    async def search_similar_traces(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar past traces.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of similar traces
        """
        if not self.pinecone_client:
            # Search local fallback
            return self._search_local(query, limit)
        
        try:
            # Generate query embedding
            embedding = await self._generate_embedding(query)
            
            if embedding is None:
                return self._search_local(query, limit)
            
            # Search Pinecone
            results = self.index.query(
                vector=embedding,
                top_k=limit,
                include_metadata=True
            )
            
            # Format results
            traces = []
            for match in results["matches"]:
                traces.append({
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match["metadata"]
                })
            
            return traces
            
        except Exception as e:
            LOGGER.error(f"Failed to search Pinecone: {e}")
            return self._search_local(query, limit)
    
    def _search_local(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search local fallback storage.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching traces
        """
        results = []
        query_lower = query.lower()
        
        for trace_id, data in self._local_fallback.items():
            content = data.get("content", "").lower()
            
            # Simple keyword matching
            if any(word in content for word in query_lower.split()):
                results.append({
                    "id": trace_id,
                    "score": 0.8,  # Fixed score for local matches
                    "metadata": {
                        "task": data["trace"].get("task", "")[:1000],
                        "pattern_type": data["analysis"]["pattern_type"],
                        "timestamp": data["timestamp"]
                    }
                })
                
                if len(results) >= limit:
                    break
        
        return results


# Global instance
_reflection_agent: Optional[ReflectionAgent] = None


def get_reflection_agent() -> ReflectionAgent:
    """Get or create the global ReflectionAgent instance."""
    global _reflection_agent
    if _reflection_agent is None:
        _reflection_agent = ReflectionAgent()
    return _reflection_agent


async def initialize_reflection(pinecone_api_key: str = None, environment: str = "us-west1-gcp"):
    """
    Initialize the ReflectionAgent with Pinecone.
    
    Args:
        pinecone_api_key: Pinecone API key
        environment: Pinecone environment
    """
    global _reflection_agent
    
    try:
        import pinecone
        
        # Initialize Pinecone
        pinecone.init(api_key=pinecone_api_key, environment=environment)
        
        _reflection_agent = ReflectionAgent(pinecone_client=pinecone)
        LOGGER.info("ReflectionAgent initialized with Pinecone")
        
    except ImportError:
        LOGGER.warning("pinecone not installed - using local fallback")
        _reflection_agent = ReflectionAgent()
    except Exception as e:
        LOGGER.error(f"Failed to initialize Pinecone: {e}")
        _reflection_agent = ReflectionAgent()


# Convenience functions
async def process_successful_traces(traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process successful traces through the ReflectionAgent."""
    agent = get_reflection_agent()
    return await agent.execute(traces)


async def search_memory(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search memory for similar past traces."""
    agent = get_reflection_agent()
    return await agent.search_similar_traces(query, limit)
