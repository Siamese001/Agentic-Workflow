"""
Sovereign DeepWiki Client – Phase 13D (Dec 26, 2025)
Codebase Intelligence via MCP.
L6 Observability integration with DeepWiki MCP for repository knowledge access.
L3 routed, L5 shielded documentation queries.

Allows the agent to 'read' the codebase structure and ask questions about it.
"""
import logging
from typing import Dict, Any, Optional, List
from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config

logger = logging.getLogger("L6.DeepWiki")


class SovereignDeepWikiClient:
    """
    DeepWiki MCP Client for L6 Observability.
    
    Provides access to repository documentation and knowledge base
    through the Sovereign MCP Router with L5 safety shielding.
    
    Allows the agent to 'read' the codebase structure and ask questions about it.
    """
    
    def __init__(self):
        """Initialize the DeepWiki client with sovereign routing."""
        self.router = SovereignMCPRouter(role="observability")
        self.initialized = False
        logger.info("[L6 DEEPWIKI] Client initialized")
    
    async def initialize(self):
        """Async initialization of MCP router."""
        try:
            await self.router.initialize()
            self.initialized = True
            logger.info("[L6 DEEPWIKI] Router initialized successfully")
        except Exception as e:
            logger.error(f"[L6 DEEPWIKI] Initialization failed: {e}")
            raise
    
    async def ask_question(self, question: str, repo: Optional[str] = None) -> str:
        """
        Ask a natural language question about the codebase.
        
        Args:
            question: Natural language question about the codebase
            repo: Optional repository identifier (defaults to config)
            
        Returns:
            Answer string
        """
        if not config.DEEPWIKI_MCP_ENABLED:
            return "DeepWiki MCP Disabled"
        
        if not self.initialized:
            await self.initialize()
        
        repo_target = repo or config.DEEPWIKI_REPO_CONTEXT
        
        logger.info(f"[L6 DEEPWIKI] Asking: {question} (Repo: {repo_target})")
        
        try:
            result = await self.router.manager.call_tool(
                "mcp2_ask_question",
                {
                    "repoName": repo_target,
                    "question": question
                }
            )
            
            # Parse result (DeepWiki usually returns simple text or dict)
            if isinstance(result, dict) and "answer" in result:
                return result["answer"]
            elif isinstance(result, dict) and "response" in result:
                return result["response"]
            
            return str(result)
            
        except Exception as e:
            logger.error(f"[L6 DEEPWIKI] Question failed: {e}")
            return f"Error: {str(e)}"
    
    async def get_structure(self, repo: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve file/folder structure.
        
        Args:
            repo: Optional repository identifier (defaults to config)
            
        Returns:
            Repository structure
        """
        if not config.DEEPWIKI_MCP_ENABLED:
            return {"structure": [], "error": "DeepWiki MCP Disabled"}
        
        if not self.initialized:
            await self.initialize()
        
        repo_target = repo or config.DEEPWIKI_REPO_CONTEXT
        
        try:
            result = await self.router.manager.call_tool(
                "mcp2_read_wiki_structure",
                {
                    "repoName": repo_target
                }
            )
            
            logger.info(f"[L6 DEEPWIKI] Structure retrieved for repo: {repo_target}")
            return result
            
        except Exception as e:
            logger.error(f"[L6 DEEPWIKI] Structure read failed: {e}")
            return {
                "structure": [],
                "error": str(e)
            }
    
    async def read_wiki_structure(self, repo: str) -> Dict[str, Any]:
        """
        Get the structure/topics of a repository's wiki.
        Legacy method - use get_structure() instead.
        
        Args:
            repo: Repository identifier (e.g., "owner/repo")
            
        Returns:
            Wiki structure with topics list
        """
        return await self.get_structure(repo)
    
    async def read_wiki_contents(self, repo: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Read the contents of a repository's wiki.
        
        Args:
            repo: Repository identifier (e.g., "owner/repo")
            topic: Optional specific topic to read
            
        Returns:
            Wiki contents
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            result = await self.router.manager.call_tool(
                "mcp2_read_wiki_contents",
                {
                    "repoName": repo
                }
            )
            
            logger.info(f"[L6 DEEPWIKI] Wiki contents retrieved for repo: {repo}")
            return result
            
        except Exception as e:
            logger.error(f"[L6 DEEPWIKI] Contents read failed for {repo}: {e}")
            return {
                "content": "",
                "error": str(e),
                "status": "failed"
            }
    
    async def search_documentation(
        self, 
        repo: str, 
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search repository documentation for relevant information.
        
        Args:
            repo: Repository identifier
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # First get wiki structure to find relevant topics
            structure = await self.read_wiki_structure(repo)
            topics = structure.get("topics", [])
            
            # Filter topics by query relevance (simple keyword matching)
            query_lower = query.lower()
            relevant_topics = [
                topic for topic in topics 
                if any(word in topic.lower() for word in query_lower.split())
            ][:max_results]
            
            # Get content for relevant topics
            results = []
            for topic in relevant_topics:
                try:
                    answer = await self.ask_question(
                        repo, 
                        f"What does the documentation say about {topic}?"
                    )
                    results.append({
                        "topic": topic,
                        "content": answer.get("response", ""),
                        "relevance": "high"
                    })
                except Exception as e:
                    logger.warning(f"[L6 DEEPWIKI] Failed to get content for topic {topic}: {e}")
            
            logger.info(f"[L6 DEEPWIKI] Search returned {len(results)} results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"[L6 DEEPWIKI] Search failed for {repo}: {e}")
            return []
    
    async def get_canon_guidance(self, key_id: int, violation_desc: str) -> Dict[str, Any]:
        """
        Get canon compliance guidance from internal repository knowledge.
        
        Args:
            key_id: Canon key ID
            violation_desc: Description of the violation
            
        Returns:
            Guidance for resolving the violation
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Query internal canon repository
            question = f"How should Canon Key {key_id} be resolved? Context: {violation_desc}"
            
            result = await self.ask_question(
                "xai/grok-canon",  # Internal canon repository
                question
            )
            
            logger.info(f"[L6 DEEPWIKI] Canon guidance retrieved for Key {key_id}")
            return {
                "key_id": key_id,
                "guidance": result.get("response", ""),
                "source": "internal_canon",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"[L6 DEEPWIKI] Canon guidance failed for Key {key_id}: {e}")
            return {
                "key_id": key_id,
                "guidance": "",
                "error": str(e),
                "status": "failed"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on DeepWiki connection.
        
        Returns:
            Health status
        """
        try:
            # Try a simple query to test connectivity
            result = await self.ask_question(
                "xai/grok-canon",
                "What is the purpose of this repository?"
            )
            
            if result.get("error"):
                return {
                    "status": "unhealthy",
                    "error": result["error"]
                }
            
            return {
                "status": "healthy",
                "response_length": len(result.get("response", "")),
                "initialized": self.initialized
            }
            
        except Exception as e:
            logger.error(f"[L6 DEEPWIKI] Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Singleton instance
_deepwiki_client: Optional[SovereignDeepWikiClient] = None


def get_deepwiki_client() -> SovereignDeepWikiClient:
    """Get or create the global DeepWiki client."""
    global _deepwiki_client
    if _deepwiki_client is None:
        _deepwiki_client = SovereignDeepWikiClient()
    return _deepwiki_client
