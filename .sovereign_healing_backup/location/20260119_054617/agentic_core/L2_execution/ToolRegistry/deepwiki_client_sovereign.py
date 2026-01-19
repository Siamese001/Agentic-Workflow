from __future__ import annotations
"""
Sovereign DeepWiki Client – Phase 13E (Dec 26, 2025)
L6 Codebase Intelligence via Official MCP.
L3 Routed | L5 Shielded

Allows the agent to query its own structure and logic.
Enables self-verification and canon audit capabilities.
"""
import logging
import json
from typing import Dict, Any, Optional, List, Union
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.decorators import standard_heal

Logger: Any = logging.getLogger('L6.DeepWiki')

class SovereignDeepWikiClient(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    DeepWiki MCP Client for L6 Observability.
    
    Provides access to repository documentation and knowledge base
    through the Sovereign MCP Router with L5 safety shielding.
    
    Allows the agent to 'read' the codebase structure and ask questions about it.
    """

    def __init__(self):
        """Initialize the DeepWiki client with sovereign routing."""
        super().__init__()
        self.router = SovereignMCPRouter(role='observability')
        self.initialized = False
        self._mcp_audit('init')
        Logger.info('[L6 DEEPWIKI] Client initialized')

    async def initialize(self) -> Any:
        """Async initialization of MCP router."""
        try:
            await self.router.initialize()
            self.initialized = True
            Logger.info('[L6 DEEPWIKI] Router initialized successfully')
        except Exception as e:
            Logger.error(f'[L6 DEEPWIKI] Initialization failed: {e}')
            raise

    async def ask_question(self, question: str, repo: Optional[str]=None) -> str:
        """
        Ask a natural language question about the codebase.
        Example: "Where is the retry logic for Pinecone located?"
        
        Args:
            question: Natural language question about the codebase
            repo: Optional repository identifier (defaults to config)
            
        Returns:
            Answer string
        """
        if not config.DEEPWIKI_MCP_ENABLED:
            return 'DeepWiki MCP Disabled'
        if not self.initialized:
            await self.initialize()
        repo_target: Any = repo or config.DEEPWIKI_REPO_CONTEXT
        Logger.info(f"[L6 DEEPWIKI] Analyzing codebase: '{question}'")
        try:
            result: Any = await self.router.manager.call_tool(tool_name='deepwiki_ask', args={'question': question, 'repo': repo_target})
            if isinstance(result, dict) and 'answer' in result:
                return result['answer']
            elif isinstance(result, dict) and 'response' in result:
                return result['response']
            return str(result)
        except Exception as e:
            Logger.error(f'[L6 DEEPWIKI] Query failed: {e}')
            return f'Error analyzing codebase: {e}'

    async def get_structure(self, repo: Optional[str]=None) -> Dict[str, Any]:
        """
        Retrieve the file/folder structure of the repository.
        Useful for L6 'Canon Verification' (checking for Missing files).
        
        Args:
            repo: Optional repository identifier (defaults to config)
            
        Returns:
            Repository structure as dict
        """
        if not config.DEEPWIKI_MCP_ENABLED:
            return {'structure': [], 'error': 'DeepWiki MCP Disabled'}
        if not self.initialized:
            await self.initialize()
        repo_target: Any = repo or config.DEEPWIKI_REPO_CONTEXT
        try:
            result: Any = await self.router.manager.call_tool(tool_name='deepwiki_structure', args={'repo': repo_target})
            if isinstance(result, str):
                return json.loads(result)
            Logger.info(f'[L6 DEEPWIKI] Structure retrieved for repo: {repo_target}')
            return result
        except Exception as e:
            Logger.error(f'[L6 DEEPWIKI] Structure fetch failed: {e}')
            return {'error': str(e)}

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

    async def read_wiki_contents(self, repo: str, topic: Optional[str]=None) -> Dict[str, Any]:
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
            result: Any = await self.router.manager.call_tool('mcp2_read_wiki_contents', {'repoName': repo})
            Logger.info(f'[L6 DEEPWIKI] Wiki contents retrieved for repo: {repo}')
            return result
        except Exception as e:
            Logger.error(f'[L6 DEEPWIKI] Contents read failed for {repo}: {e}')
            return {'content': '', 'error': str(e), 'status': 'failed'}

    async def search_documentation(self, repo: str, query: str, max_results: int=5) -> List[Dict[str, Any]]:
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
            structure: Any = await self.read_wiki_structure(repo)
            topics: Any = structure.get('topics', [])
            query_lower: Any = query.lower()
            relevant_topics: Any = [topic for topic in topics if any((word in topic.lower() for word in query_lower.split()))][:max_results]
            results: Any = []
            for topic in relevant_topics:
                try:
                    answer: Any = await self.ask_question(repo, f'What does the documentation say about {topic}?')
                    results.append({'topic': topic, 'content': answer.get('response', ''), 'relevance': 'high'})
                except Exception as e:
                    Logger.warning(f'[L6 DEEPWIKI] Failed to get content for topic {topic}: {e}')
            Logger.info(f'[L6 DEEPWIKI] Search returned {len(results)} results for: {query}')
            return results
        except Exception as e:
            Logger.error(f'[L6 DEEPWIKI] Search failed for {repo}: {e}')
            return []

    async def get_canon_guidance(self, key_id: int, violation_desc: str) -> Dict[str, Any]:
        """
        Get canon compliance guidance from internal repository knowledge.
        
        Args:
            key_id: Canon key ID
            violation_desc: Description of the Violation
            
        Returns:
            Guidance for resolving the Violation
        """
        if not self.initialized:
            await self.initialize()
        try:
            question: Any = f'How should Canon Key {key_id} be resolved? Context: {violation_desc}'
            result: Any = await self.ask_question('xai/grok-canon', question)
            Logger.info(f'[L6 DEEPWIKI] Canon guidance retrieved for Key {key_id}')
            return {'key_id': key_id, 'guidance': result.get('response', ''), 'source': 'internal_canon', 'status': 'success'}
        except Exception as e:
            Logger.error(f'[L6 DEEPWIKI] Canon guidance failed for Key {key_id}: {e}')
            return {'key_id': key_id, 'guidance': '', 'error': str(e), 'status': 'failed'}

    async def verify_file_exists(self, filepath: str) -> bool:
        """
        L6 Utility: Check if a file exists in the current context.
        
        Args:
            filepath: Path to the file to verify
            
        Returns:
            True if file exists, False otherwise
        """
        answer: Any = await self.ask_question(f"Does the file '{filepath}' exist in the codebase?")
        answer_lower: Any = answer.lower()
        if any((word in answer_lower for word in ['yes', 'exists', 'found', 'present'])):
            return True
        if any((word in answer_lower for word in ['no', 'not found', 'Missing', 'does not exist', "doesn't exist"])):
            return False
        Logger.warning(f'[L6 DEEPWIKI] Ambiguous file existence response for {filepath}: {answer}')
        return False

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on DeepWiki connection.
        
        Returns:
            Health status
        """
        try:
            result: Any = await self.ask_question('What is the purpose of this repository?')
            if 'error' in result.lower():
                return {'status': 'unhealthy', 'error': result}
            return {'status': 'healthy', 'response_length': len(result), 'initialized': self.initialized}
        except Exception as e:
            Logger.error(f'[L6 DEEPWIKI] Health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}

    @standard_heal
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
_deepwiki_client: Optional[SovereignDeepWikiClient] = None

def get_deepwiki_client() -> SovereignDeepWikiClient:
    """Get or create the global DeepWiki client."""
    global _deepwiki_client
    if _deepwiki_client is None:
        _deepwiki_client = SovereignDeepWikiClient()
    return _deepwiki_client
