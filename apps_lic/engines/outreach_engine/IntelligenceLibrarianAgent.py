from __future__ import annotations
from dataclasses import dataclass
# File: intelligence_librarian.py
# Description: Persistent Intelligence Service ("The Librarian") - v13.0
# Runs offline/async to pre-compute deep research and store in vector database
# HARDENED: 2026-01-01 - MCPHardenedMixin applied

__version__ = "13.1"

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# MCP Hardening
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

# PDF parsing
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("WARNING: PyMuPDF not installed. PDF support disabled.")

# Embedding and vector store
import google.generativeai as genai

# Models (updated imports for new locations)
from apps_lic.domain.lic_models import RAGResult
from apps_shared.utils.circuit_breaker import CircuitBreaker
from apps_shared.utils.vector_memory import VectorMemoryStore


@dataclass
class IntelligenceLibrarianAgent(HealerMixin, SubatomicTestingMixin, MCPHardenedMixin):
    """
    v13.1: Offline research agent that pre-computes intelligence (MCP Hardened)
    
    The Librarian runs asynchronously (e.g., nightly via cron) to:
    1. Research target companies and executives
    2. Extract and embed key findings
    3. Store embeddings in persistent vector database (ChromaDB)
    
    This transforms S2 from a runtime-heavy research agent to a
    runtime-light synthesis agent that queries pre-computed memory.
    """
    
    def __init__(
        self,
        search_client: Any = None,
        llm_client: Any = None,
        memory_store: VectorMemoryStore = None
    ):
        """
        Initialize Librarian with API clients and vector store
        
        Args:
            search_client: Google Search API client
            llm_client: Gemini LLM client for analysis
            memory_store: Vector database for persistent storage
        """
        super().__init__()  # MCPHardenedMixin init
        self.search_client = search_client
        self.llm_client = llm_client
        self.memory_store = memory_store
        
        # Configure Gemini embedding API
        self.embedding_model = "models/embedding-001"
        
        print(f"[Librarian] Initialized with vector store: {memory_store.collection_name}")
    
    async def research_company(
        self,
        company_name: str,
        include_strategic_brief: bool = True,
        include_news: bool = True,
        include_blog: bool = True
    ) -> Dict[str, Any]:
        """
        Deep research on a company - runs offline
        
        Args:
            company_name: Company to research
            include_strategic_brief: Search for strategic priorities
            include_news: Search for recent news
            include_blog: Search for company blog/announcements
        
        Returns:
            Dictionary with research findings and metadata
        """
        print(f"\nfrom agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.healer_mixin import HealerMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[Librarian] Starting deep research on: {company_name}")
        
        findings = {
            "company_name": company_name,
            "timestamp": datetime.now().isoformat(),
            "research_duration_seconds": 0,
            "sources": []
        }
        
        start_time = datetime.now()
        
        # 1. Strategic Brief Research (highest priority)
        if include_strategic_brief:
            strategic_results = await self._research_strategic_brief(company_name)
            findings["sources"].extend(strategic_results)
        
        # 2. Recent News Research
        if include_news:
            news_results = await self._research_company_news(company_name)
            findings["sources"].extend(news_results)
        
        # 3. Company Blog/Announcements
        if include_blog:
            blog_results = await self._research_company_blog(company_name)
            findings["sources"].extend(blog_results)
        
        findings["research_duration_seconds"] = (datetime.now() - start_time).total_seconds()
        findings["total_sources"] = len(findings["sources"])
        
        print(f"[Librarian] Research complete: {findings['total_sources']} sources in {findings['research_duration_seconds']:.1f}s")
        
        # 4. Embed and store findings
        await self._embed_and_store(findings)
        
        return findings
    
    async def research_executive(
        self,
        executive_name: str,
        company_name: str,
        include_linkedin: bool = True,
        include_recent_posts: bool = True,
        include_presentations: bool = True
    ) -> Dict[str, Any]:
        """
        Deep research on an executive - runs offline
        
        Args:
            executive_name: Executive to research
            company_name: Their company
            include_linkedin: Search for LinkedIn profile
            include_recent_posts: Search for recent posts/articles
            include_presentations: Search for conference talks/presentations
        
        Returns:
            Dictionary with research findings and metadata
        """
        print(f"\n[Librarian] Starting deep research on: {executive_name} ({company_name})")
        
        findings = {
            "executive_name": executive_name,
            "company_name": company_name,
            "timestamp": datetime.now().isoformat(),
            "research_duration_seconds": 0,
            "sources": []
        }
        
        start_time = datetime.now()
        
        # 1. LinkedIn Profile Research
        if include_linkedin:
            linkedin_results = await self._research_linkedin_profile(executive_name, company_name)
            findings["sources"].extend(linkedin_results)
        
        # 2. Recent Posts/Articles
        if include_recent_posts:
            post_results = await self._research_executive_posts(executive_name, company_name)
            findings["sources"].extend(post_results)
        
        # 3. Conference Presentations
        if include_presentations:
            presentation_results = await self._research_presentations(executive_name, company_name)
            findings["sources"].extend(presentation_results)
        
        findings["research_duration_seconds"] = (datetime.now() - start_time).total_seconds()
        findings["total_sources"] = len(findings["sources"])
        
        print(f"[Librarian] Research complete: {findings['total_sources']} sources in {findings['research_duration_seconds']:.1f}s")
        
        # 4. Embed and store findings
        await self._embed_and_store(findings)
        
        return findings
    
    async def _research_strategic_brief(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Research company strategic priorities (highest signal)
        """
        print(f"[Librarian] Researching strategic brief for {company_name}...")
        
        queries = [
            f"{company_name} strategic priorities 2025",
            f"{company_name} annual roadmap",
            f"{company_name} CEO vision statement",
            f"{company_name} quarterly earnings strategic focus"
        ]
        
        results = []
        
        for query in queries:
            try:
                search_results = self.search_client.search(query, num_results=3)
                
                for item in search_results:
                    # Extract and analyze content
                    content = self._extract_search_result_content(item)
                    
                    # Use LLM to extract strategic priorities
                    priorities = await self._extract_strategic_priorities(content, company_name)
                    
                    if priorities:
                        results.append({
                            "SourceType": "STRATEGIC_BRIEF",
                            "source_url": item.get("link", ""),
                            "title": item.get("title", ""),
                            "content": content,
                            "strategic_priorities": priorities,
                            "extracted_at": datetime.now().isoformat(),
                            "age_days": 0  # Assume recent
                        })
                
                # Rate limit between queries
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"[Librarian] Error searching '{query}': {e}")
        
        print(f"[Librarian] Found {len(results)} strategic brief sources")
        return results
    
    async def _research_company_news(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Research recent company news and announcements
        """
        print(f"[Librarian] Researching news for {company_name}...")
        
        queries = [
            f"{company_name} news last 30 days",
            f"{company_name} latest announcement",
            f"{company_name} recent funding partnership"
        ]
        
        results = []
        
        for query in queries:
            try:
                search_results = self.search_client.search(query, num_results=3)
                
                for item in search_results:
                    content = self._extract_search_result_content(item)
                    
                    results.append({
                        "SourceType": "NEWS_ARTICLE_COMPANY",
                        "source_url": item.get("link", ""),
                        "title": item.get("title", ""),
                        "content": content,
                        "extracted_at": datetime.now().isoformat(),
                        "age_days": self._estimate_age_from_snippet(item.get("snippet", ""))
                    })
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"[Librarian] Error searching '{query}': {e}")
        
        print(f"[Librarian] Found {len(results)} news sources")
        return results
    
    async def _research_company_blog(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Research company blog and announcements
        """
        print(f"[Librarian] Researching blog for {company_name}...")
        
        queries = [
            f"site:{company_name.lower().replace(' ', '')}.com/blog",
            f"{company_name} blog latest posts",
            f"{company_name} company announcements"
        ]
        
        results = []
        
        for query in queries:
            try:
                search_results = self.search_client.search(query, num_results=3)
                
                for item in search_results:
                    content = self._extract_search_result_content(item)
                    
                    results.append({
                        "SourceType": "COMPANY_BLOG_ANNOUNCEMENT",
                        "source_url": item.get("link", ""),
                        "title": item.get("title", ""),
                        "content": content,
                        "extracted_at": datetime.now().isoformat(),
                        "age_days": self._estimate_age_from_snippet(item.get("snippet", ""))
                    })
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"[Librarian] Error searching '{query}': {e}")
        
        print(f"[Librarian] Found {len(results)} blog sources")
        return results
    
    async def _research_linkedin_profile(
        self,
        executive_name: str,
        company_name: str
    ) -> List[Dict[str, Any]]:
        """
        Research executive LinkedIn profile
        """
        print(f"[Librarian] Researching LinkedIn for {executive_name}...")
        
        query = f"{executive_name} {company_name} LinkedIn"
        
        results = []
        
        try:
            search_results = self.search_client.search(query, num_results=2)
            
            for item in search_results:
                if "linkedin.com/in/" in item.get("link", ""):
                    content = self._extract_search_result_content(item)
                    
                    results.append({
                        "SourceType": "RECIPIENT_LINKEDIN_ABOUT",
                        "source_url": item.get("link", ""),
                        "title": item.get("title", ""),
                        "content": content,
                        "executive_name": executive_name,
                        "extracted_at": datetime.now().isoformat(),
                        "age_days": 0
                    })
        
        except Exception as e:
            print(f"[Librarian] Error searching LinkedIn: {e}")
        
        print(f"[Librarian] Found {len(results)} LinkedIn sources")
        return results
    
    async def _research_executive_posts(
        self,
        executive_name: str,
        company_name: str
    ) -> List[Dict[str, Any]]:
        """
        Research executive recent posts and articles
        """
        print(f"[Librarian] Researching posts by {executive_name}...")
        
        queries = [
            f"{executive_name} {company_name} recent post",
            f"{executive_name} article blog post"
        ]
        
        results = []
        
        for query in queries:
            try:
                search_results = self.search_client.search(query, num_results=2)
                
                for item in search_results:
                    content = self._extract_search_result_content(item)
                    
                    results.append({
                        "SourceType": "RECIPIENT_RECENT_POST",
                        "source_url": item.get("link", ""),
                        "title": item.get("title", ""),
                        "content": content,
                        "executive_name": executive_name,
                        "extracted_at": datetime.now().isoformat(),
                        "age_days": self._estimate_age_from_snippet(item.get("snippet", ""))
                    })
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"[Librarian] Error searching posts: {e}")
        
        print(f"[Librarian] Found {len(results)} post sources")
        return results
    
    async def _research_presentations(
        self,
        executive_name: str,
        company_name: str
    ) -> List[Dict[str, Any]]:
        """
        Research executive conference talks and presentations
        """
        print(f"[Librarian] Researching presentations by {executive_name}...")
        
        query = f"{executive_name} {company_name} presentation conference talk"
        
        results = []
        
        try:
            search_results = self.search_client.search(query, num_results=2)
            
            for item in search_results:
                content = self._extract_search_result_content(item)
                
                results.append({
                    "SourceType": "CONFERENCE_TALK",
                    "source_url": item.get("link", ""),
                    "title": item.get("title", ""),
                    "content": content,
                    "executive_name": executive_name,
                    "extracted_at": datetime.now().isoformat(),
                    "age_days": self._estimate_age_from_snippet(item.get("snippet", ""))
                })
            
        except Exception as e:
            print(f"[Librarian] Error searching presentations: {e}")
        
        print(f"[Librarian] Found {len(results)} presentation sources")
        return results
    
    async def _extract_strategic_priorities(
        self,
        content: str,
        company_name: str
    ) -> List[str]:
        """
        Use LLM to extract strategic priorities from content
        """
        prompt = f"""Analyze the following content about {company_name} and extract their strategic priorities.

CONTENT:
{content[:2000]}

Extract 3-5 key strategic priorities, initiatives, or focus areas mentioned.
Output as a JSON array of strings, e.g.: ["Priority 1", "Priority 2", ...]

Output ONLY the JSON array, no explanation."""
        
        try:
            response = self.llm_client.generate(prompt)
            
            # Parse JSON response
            import re
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                priorities = json.loads(json_match.group(0))
                return priorities
            
        except Exception as e:
            print(f"[Librarian] Error extracting priorities: {e}")
        
        return []
    
    def _extract_search_result_content(self, item: Dict[str, Any]) -> str:
        """
        Extract meaningful content from search result
        """
        # Combine title and snippet
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        
        return f"{title}\n\n{snippet}"
    
    def _estimate_age_from_snippet(self, snippet: str) -> int:
        """
        Estimate age in days from snippet text
        Simple heuristic - looks for date indicators
        """
        snippet_lower = snippet.lower()
        
        if any(word in snippet_lower for word in ["today", "hours ago"]):
            return 0
        elif any(word in snippet_lower for word in ["yesterday", "1 day ago"]):
            return 1
        elif any(word in snippet_lower for word in ["this week", "days ago"]):
            return 7
        elif any(word in snippet_lower for word in ["last month", "weeks ago"]):
            return 30
        else:
            return 60  # Default to 60 days if no clear indicator
    
    async def _embed_and_store(self, findings: Dict[str, Any]):
        """
        Embed findings and store in vector database
        """
        print(f"[Librarian] Embedding and storing {len(findings['sources'])} sources...")
        
        for source in findings["sources"]:
            # Create text to embed (title + content + strategic priorities if available)
            text_to_embed = source["title"] + "\n\n" + source["content"]
            
            if "strategic_priorities" in source:
                priorities_text = "\n".join(source["strategic_priorities"])
                text_to_embed += f"\n\nStrategic Priorities:\n{priorities_text}"
            
            # Generate embedding
            try:
                embedding = genai.embed_content(
                    model=self.embedding_model,
                    content=text_to_embed,
                    TaskType="retrieval_document"
                )["embedding"]
                
                # Store in vector database
                metadata = {
                    "SourceType": source["SourceType"],
                    "source_url": source["source_url"],
                    "title": source["title"],
                    "age_days": source["age_days"],
                    "extracted_at": source["extracted_at"]
                }
                
                # Add company/executive name to metadata
                if "company_name" in findings:
                    metadata["company_name"] = findings["company_name"]
                if "executive_name" in findings:
                    metadata["executive_name"] = findings["executive_name"]
                
                self.memory_store.add_document(
                    text=text_to_embed,
                    embedding=embedding,
                    metadata=metadata
                )
                
            except Exception as e:
                print(f"[Librarian] Error embedding source: {e}")
        
        print(f"[Librarian] Storage complete")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


async def run_intelligence_service(target_list_file: str = "research_targets.json") -> Any:
    """
    Main entry point for intelligence service
    
    Reads a list of companies/executives to research and processes them
    Can be run via cron job for nightly updates
    
    Args:
        target_list_file: JSON file with list of targets to research
    """
    print(f"\n{'='*80}")
    print(f"INTELLIGENCE SERVICE v13.0 - The Librarian")
    print(f"{'='*80}\n")
    
    # Load target list
    if not os.path.exists(target_list_file):
        print(f"ERROR: {target_list_file} not found")
        print(f"\nCreate {target_list_file} with format:")
        print("""
{
  "companies": [
    {"name": "Tech Giants Corp"},
    {"name": "AI Innovations Inc"}
  ],
  "executives": [
    {"name": "Sarah Johnson", "company": "Tech Giants Corp"},
    {"name": "John Smith", "company": "AI Innovations Inc"}
  ]
}
""")
        return
    
    with open(target_list_file, 'r') as f:
        targets = json.load(f)
    
    # Initialize components
    circuit_breaker = CircuitBreaker()
    search_client = GoogleSearchClient(circuit_breaker)
    llm_client = GeminiLLMClient(circuit_breaker)
    memory_store = VectorMemoryStore()
    
    librarian = IntelligenceLibrarian(search_client, llm_client, memory_store)
    
    # Research companies
    for company in targets.get("companies", []):
        try:
            await librarian.research_company(company["name"])
        except Exception as e:
            print(f"[ERROR] Failed to research {company['name']}: {e}")
    
    # Research executives
    for exec_info in targets.get("executives", []):
        try:
            await librarian.research_executive(
                exec_info["name"],
                exec_info["company"]
            )
        except Exception as e:
            print(f"[ERROR] Failed to research {exec_info['name']}: {e}")
    
    print(f"\n{'='*80}")
    print(f"Intelligence service complete")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    """
    Run intelligence service from command line
    
    Usage:
        python intelligence_service_LIC.py
    
    Or schedule via cron:
        0 2 * * * /path/to/python /path/to/intelligence_service_LIC.py
    """
    asyncio.run(run_intelligence_service())
