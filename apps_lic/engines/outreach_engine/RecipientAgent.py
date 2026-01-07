"""
RecipientAgent - Extracted for one-class-per-file pattern.

Originally from: campaign_rag.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

class RecipientAgent:
    """
    v12.0: DEMOTED to secondary fact-checker role.
    Now performs validation searches based on strategic brief entities.
    """
    def __init__(self, circuit_breaker: CircuitBreaker, search_client: GoogleSearchClient) -> None:
        self.circuit_breaker = circuit_breaker
        self.search_client = search_client

    async def validate_entity(self, entity_name: str, entity_context: str, mission: OutreachMission) -> Dict[str, object]:
        """
        NEW v12.0: Validate a specific entity (person, initiative) from strategic brief.
        """

        # Build targeted validation query
        company = mission.recipient_profile.get('company', '')
        query = f'"{entity_name}" "{company}" {entity_context}'
        
        # Execute search
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            None, self.search_client.search, query, 2
        )
        
        rag_results = self._process_search_results(search_results, entity_name, recipient_specific=True)
        
        # Validation logic
        is_validated = len(search_results) > 0
        staleness_warning = None if is_validated else f"Could not validate '{entity_name}' - may be stale"
        
        return {
            "rag_results": rag_results,
            "is_validated": is_validated,
            "staleness_warning": staleness_warning
        }
    
    async def get_profile(self, mission: OutreachMission) -> Dict[str, object]:
        """Legacy method - minimal search for basic profile validation."""

        name = mission.recipient_profile.get('name', '')
        company = mission.recipient_profile.get('company', '')
        query = f'"{name}" "{company}" LinkedIn'
        
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            None, self.search_client.search, query, 2
        )
        
        rag_results = self._process_search_results(search_results, name, recipient_specific=True)
        
        return {"rag_results": rag_results}
    
    async def run_refinement_task(self, Task: str, mission: OutreachMission) -> Dict[str, object]:
        """Perform targeted refinement RAG."""

        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            None, self.search_client.search, Task, 2
        )
        
        rag_results = self._process_search_results(search_results, "", recipient_specific=True)
        
        return {"rag_results": rag_results}
    
    def _process_search_results(self, search_results: list, entity_name: str, recipient_specific: bool) -> List[RAGResult]:
        """Convert Google Search results into RAGResult objects."""
        rag_results = []
        
        for item in search_results:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            
            text = f"{title}. {snippet}"
            keywords = [w.strip('.,!?') for w in text.split() if len(w) > 4]
            keywords = list(set(keywords[:10]))
            
            SourceType = "RECIPIENT_LINKEDIN_ABOUT"
            if "github.com" in link:
                SourceType = "RECIPIENT_GITHUB_REPO"
            elif "linkedin.com" in link:
                SourceType = "RECIPIENT_LINKEDIN_ABOUT"
            
            rag_results.append(RAGResult(
                source=link,
                SourceType=SourceType,
                text=text,
                extracted_keywords=keywords,
                source_weight=1.5,  # Reduced from 1.8 - now secondary validation only
                age_days=30,
                recipient_specific=recipient_specific,
                confidence=0.80
            ))
        
        return rag_results
