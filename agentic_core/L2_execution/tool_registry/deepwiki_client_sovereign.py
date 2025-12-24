"""L2 Execution: Sovereign DeepWiki MCP Client
Ultra-hardened access to repository wiki via SSE.
L5 shielded (repo allowlist, token protection) + L4 cached.
"""
import os
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

import httpx
from agentic_core.L5_safety.guardrails.mcp_sovereign import mcp_authority

logger = logging.getLogger(__name__)

# Sovereign boundaries — only trust these repos
SOVEREIGN_REPOS = {"xai/grok-canon", "xai/sovereign-canon", "xai/agentic-core"}
MAX_QUESTION_LENGTH = 2000

class SovereignDeepWikiClient:
    """Ultra-hardened DeepWiki client — repository knowledge sovereignty."""
    
    def __init__(self, base_url: str = "https://mcp.deepwiki.com/sse", private_token: Optional[str] = None, cache=None):
        # L5 URL Validation
        if "deepwiki.com" not in base_url and "devin.ai" not in base_url:
            raise PermissionError("DeepWiki base URL is not recognized as sovereign.")
        
        self.base_url = base_url
        self.private_token = private_token or os.getenv("DEEPWIKI_PRIVATE_KEY")
        
        # Token Shielding: No injection attempts allowed
        if self.private_token and any(c in self.private_token for c in {"'", "\"", ";"}):
            raise ValueError("DeepWiki token fails sovereignty validation.")
            
        self.cache = cache
        self.client = httpx.AsyncClient(timeout=40.0)
        logger.info(f"[L2 DEEPWIKI] Sovereign client armed: {base_url}")

    def _auth_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.private_token:
            headers["Authorization"] = f"Bearer {self.private_token}"
        return headers

    def _validate_repo(self, repo: str):
        if repo not in SOVEREIGN_REPOS:
            raise PermissionError(f"Sovereignty Breach: DeepWiki access to non-sovereign repo '{repo}' blocked.")

    async def read_wiki_structure(self, repo: str) -> Dict[str, Any]:
        """Maps the structure of the repo wiki for targeted lookup."""
        self._validate_repo(repo)
        try:
            resp = await self.client.post(
                urljoin(self.base_url, "/read_wiki_structure"),
                json={"repo": repo},
                headers=self._auth_headers()
            )
            resp.raise_for_status()
            data = resp.json()
            
            # L4 Caching: Store the structural map
            if self.cache:
                await self.cache.cache_file(f"wiki_map_{repo.replace('/', '_')}.json", json.dumps(data, indent=2))
            return data
        except Exception as e:
            mcp_authority.record_breach(f"DeepWiki Structure Failure: {str(e)}")
            return {"error": str(e)}

    async def ask_question(self, repo: str, question: str) -> Dict[str, Any]:
        """Direct Q&A against repo docs — L5 length and term shielded."""
        self._validate_repo(repo)
        if len(question) > MAX_QUESTION_LENGTH or any(bad in question.lower() for bad in ["token", "secret"]):
            raise PermissionError("Sovereignty Breach: Forbidden terms or length in DeepWiki question.")
            
        try:
            resp = await self.client.post(
                urljoin(self.base_url, "/ask_question"),
                json={"repo": repo, "question": question},
                headers=self._auth_headers()
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"[L2 DEEPWIKI] Q&A failed: {e}")
            return {"error": str(e)}

    async def close(self):
        await self.client.aclose()
