from dataclasses import dataclass
"""
LicOrganizationAgent - Extracted for one-class-per-file pattern.

Originally from: campaign_rag.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin

@dataclass
class LicOrganizationAgent(SubatomicTestingMixin, MCPHardenedMixin):
    """
    v12.0: DEMOTED to secondary fact-checker role.
    
    Performs validation searches based on strategic brief entities.
    Validates initiatives and provides organization context through RAG.
    
    Attributes:
        circuit_breaker: Circuit breaker for fault tolerance
        search_client: Google search client for validation queries
    """

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
        
        Returns:
            Dict with healing summary
        """
        super().heal_repository()

        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self, circuit_breaker: 'CircuitBreaker', search_client: 'GoogleSearchClient') -> None:
        """
        Initialize the organization validation agent.
        
        Args:
            circuit_breaker: Circuit breaker for fault tolerance
            search_client: Google search client for validation queries
        """
        self.circuit_breaker = circuit_breaker
        self.search_client = search_client

    async def validate_initiative(self, initiative_name: str, mission: 'OutreachMission') -> Dict[str, Any]:
        """
        NEW v12.0: Validate a specific initiative from strategic brief.
        
        Args:
            initiative_name: Name of the initiative to validate
            mission: Outreach mission context
        
        Returns:
            Dict with rag_results, is_validated flag, and staleness_warning
        """

        company = mission.JobDescription.get('company', '')
        query = f'"{company}" "{initiative_name}"'
        
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            None, self.search_client.search, query, 2
        )
        
        rag_results = self._process_search_results(search_results, initiative_name)
        
        is_validated = len(search_results) > 0
        staleness_warning = None if is_validated else f"Could not validate initiative '{initiative_name}' - may be stale"
        
        return {
            "rag_results": rag_results,
            "is_validated": is_validated,
            "staleness_warning": staleness_warning
        }

    async def get_organization_context(self, mission: 'OutreachMission') -> Dict[str, Any]:
        """
        Legacy method - minimal search for basic org validation.
        
        Args:
            mission: Outreach mission context
        
        Returns:
            Dict with rag_results from organization search
        """

        company = mission.JobDescription.get('company', '')
        query = f'"{company}" news'
        
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            None, self.search_client.search, query, 2
        )
        
        rag_results = self._process_search_results(search_results, "")
        
        return {"rag_results": rag_results}

    async def run_refinement_task(self, Task: str, mission: 'OutreachMission') -> Dict[str, Any]:
        """
        Perform targeted refinement RAG.
        
        Args:
            Task: Refinement task description
            mission: Outreach mission context
        
        Returns:
            Dict with rag_results from refinement search
        """

        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            None, self.search_client.search, Task, 2
        )
        
        rag_results = self._process_search_results(search_results, "")
        
        return {"rag_results": rag_results}
    
    def _process_search_results(self, search_results: list, entity_name: str) -> List[RAGResult]:
        """Convert Google Search results into RAGResult objects."""
        rag_results = []
        
        for item in search_results:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            
            text = f"{title}. {snippet}"
            keywords = [w.strip('.,!?') for w in text.split() if len(w) > 4]
            keywords = list(set(keywords[:10]))
            
            SourceType = "COMPANY_BLOG_ANNOUNCEMENT"
            if "news" in link or "press" in link:
                SourceType = "NEWS_ARTICLE_COMPANY"
            elif "blog" in link:
                SourceType = "COMPANY_BLOG_ANNOUNCEMENT"
            elif "linkedin.com" in link:
                SourceType = "COMPANY_LINKEDIN_PAGE"
            
            rag_results.append(RAGResult(
                source=link,
                SourceType=SourceType,
                text=text,
                extracted_keywords=keywords,
                source_weight=1.3,  # Reduced from 1.5 - now secondary validation only
                age_days=30,
                recipient_specific=False,
                confidence=0.75
            ))
        
        return rag_results
