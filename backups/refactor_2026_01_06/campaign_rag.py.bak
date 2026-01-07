from __future__ import annotations
# File: rag_LIC.py
# Description: RAG (Retrieval-Augmented Generation) agents and utilities
# REFACTOR: v12.0 - Strategic Alignment Engine (from tactical posts to strategic briefs)

__version__ = "12.0"

import asyncio
# import scripts.validation.check_canonical_structure  # TODO: Replace with sovereign equivalent
import json
import os
import glob
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
# from scripts.utilities.FormatScriptsContext import TfidfVectorizer  # TODO: Replace with sovereign equivalent
from sklearn.metrics.pairwise import cosine_similarity

# PDF parsing library
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# from archives.legacy_lic.Agentic LIC.utils_LIC import CircuitBreaker  # TODO: Replace with sovereign equivalent

# NEW: Import live API clients
# from archives.legacy_lic.Agentic LIC.retrieval_clients import GoogleSearchClient  # TODO: Replace with sovereign equivalent
# from archives.legacy_lic.Agentic LIC.llm_clients import GeminiLLMClient  # TODO: Replace with sovereign equivalent

from apps_lic.core.data_models import (
    RAGResult, MessageClaim, Archetype, RAGCritique, OutreachMission, 
    ProfileAnalysis, ResearchContext, SenderGroundingWhitelists, MessageScaffold
)

# Stub classes for Missing dependencies (TODO: Replace with sovereign equivalents)
class CircuitBreaker:
    """Stub for CircuitBreaker - TODO: Replace with sovereign equivalent"""
    pass

class GoogleSearchClient:
    """Stub for GoogleSearchClient - TODO: Replace with sovereign equivalent"""
    pass

class GeminiLLMClient:
    """Stub for GeminiLLMClient - TODO: Replace with sovereign equivalent"""
    pass

class BaseAgent(HealerMixin, MCPHardenedMixin):
    """Stub for BaseAgent - TODO: Replace with sovereign equivalent"""
    def __init__(self, context, debug_mode=False) -> None:
        self.context = context
        self.debug_mode = debug_mode
    
    def log_info(self, msg):
        pass

def track_metrics(name):
    """Stub decorator for track_metrics - TODO: Replace with sovereign equivalent"""
    def decorator(func):
        return func
    return decorator

def detect_bias(context, text, workflow_id=""):
    """Stub for detect_bias - TODO: Replace with sovereign equivalent"""
    return {"bias_detected": False, "score": 0.0}

def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results

class SignalQualityScorer:
    """
    Weights RAG sources by reliability for message generation
    FEATURE 1.1 from SUPREME_SPELL
    v12.0: Added STRATEGIC_BRIEF as highest weight source
    """
    
    SOURCE_WEIGHTS = {
        "STRATEGIC_BRIEF": 2.5,              # NEW v12.0: Highest signal
        "RECIPIENT_LINKEDIN_ABOUT": 2.0,
        "RECIPIENT_RECENT_POST": 1.8,
        "COMPANY_BLOG_ANNOUNCEMENT": 1.5,
        "COMPANY_LINKEDIN_PAGE": 1.3,
        "NEWS_ARTICLE_COMPANY": 1.2,
        "COMPETITOR_COMPARISON": 0.9,
        "GENERIC_INDUSTRY_TREND": 0.6,
        "SENDER_PROFILE_ONLY": 0.3,
        "MASTER_RESUME": 2.0,
        "SENDER_KNOWLEDGE_BASE": 1.8,
        # DEPRECATED v12.0: manual_rag_input removed
    }
    
    MINIMUM_SIGNAL_THRESHOLD = 0.70
    
    def calculate_signal_score(
        self,
        rag_results: List[RAGResult],
        MessageContent: str
    ) -> Tuple[float, Dict[str, int]]:
        """
        Calculate weighted signal quality score for generated message
        """
        keyword_scores = defaultdict(float)
        source_breakdown = defaultdict(int)
        
        for result in rag_results:
            weight = self.SOURCE_WEIGHTS.get(result.SourceType, 0.5)
            for keyword in result.extracted_keywords:
                if keyword.lower() in MessageContent.lower():
                    keyword_scores[keyword] += weight
                    source_breakdown[result.SourceType] += 1
        
        if not keyword_scores:
            return 0.0, dict(source_breakdown)
        
        signal_score = sum(keyword_scores.values()) / len(keyword_scores)
        return signal_score, dict(source_breakdown)
    
    def validate_minimum_signal(self, score: float) -> bool:
        return score >= self.MINIMUM_SIGNAL_THRESHOLD

# ============================================================================
# NEW v11.6: CLAIM CONFIDENCE SCORER (FEATURE 1.2)
# ============================================================================

class ClaimConfidenceScorer:
    """
    Per-Claim confidence scoring with rejection gate
    FEATURE 1.2 from SUPREME_SPELL
    """
    
    MIN_PER_CLAIM_CONFIDENCE = 0.70
    MIN_AGGREGATE_CONFIDENCE = 0.75
    
    def score_claim(
        self,
        claim_text: str,
        rag_results: List[RAGResult],
        embedding_similarity_threshold: float = 0.75
    ) -> MessageClaim:
        """
        Score individual Claim based on RAG evidence
        (Simplified version - full implementation would use embeddings)
        """
        supporting = []
        weights = []
        
        # Simple keyword-based support detection
        claim_words = set(claim_text.lower().split())
        
        for result in rag_results:
            result_words = set(result.text.lower().split())
            overlap = len(claim_words & result_words)
            
            if overlap >= 3:  # At least 3 words in common
                supporting.append(result.source)
                weights.append(result.source_weight)
        
        if not supporting:
            confidence = 0.0
        else:
            confidence = min(1.0, (len(supporting) * 0.3) + (sum(weights) / len(weights) * 0.7))
        
        return MessageClaim(
            text=claim_text,
            confidence=confidence,
            supporting_sources=supporting,
            source_weights=weights
        )
    
    def score_message_claims(
        self,
        message: str,
        rag_results: List[RAGResult]
    ) -> Tuple[List[MessageClaim], float]:
        """
        Score all claims in message
        """
        # Split message into sentences (claims)
        sentences = [s.strip() for s in message.split('.') if len(s.strip()) > 10]
        
        claims = []
        for sentence in sentences:
            Claim = self.score_claim(sentence, rag_results)
            claims.append(Claim)
        
        if not claims:
            return [], 0.0
        
        aggregate_confidence = sum(c.confidence for c in claims) / len(claims)
        return claims, aggregate_confidence
    
    def validate_claims(
        self,
        claims: List[MessageClaim],
        aggregate_confidence: float
    ) -> Tuple[bool, str]:
        """
        Validate claims meet minimum thresholds
        """
        low_confidence_claims = [c for c in claims if c.confidence < self.MIN_PER_CLAIM_CONFIDENCE]
        
        if low_confidence_claims:
            return False, f"{len(low_confidence_claims)} claims below 0.70 confidence"
        
        if aggregate_confidence < self.MIN_AGGREGATE_CONFIDENCE:
            return False, f"Aggregate confidence {aggregate_confidence:.2f} < 0.75"
        
        return True, ""

# ============================================================================
# NEW v11.6: RAG REFLEXION SYSTEM (FEATURE 1.4)
# ============================================================================

class RAGReflexionSystem:
    """
    Iterative RAG refinement with critique loop
    FEATURE 1.4 from SUPREME_SPELL
    v12.0: Updated gap detection for strategic brief requirements
    """
    
    MIN_CONFIDENCE_THRESHOLD = 0.70
    MAX_ITERATIONS = 3
    
    def critique_rag_sufficiency(
        self,
        rag_results: List[RAGResult],
        RecipientArchetype: Archetype,
        iteration: int
    ) -> RAGCritique:
        """
        Critique RAG research quality and identify gaps
        v12.0: Now checks for STRATEGIC_BRIEF presence
        """
        gaps = []
        
        # Gap 1: Strategic Brief (NEW v12.0)
        source_types = set(r.SourceType for r in rag_results)
        if "STRATEGIC_BRIEF" not in source_types:
            gaps.append("Missing strategic brief - critical for v12.0 alignment strategy")
        
        # Gap 2: Sender grounding
        if "MASTER_RESUME" not in source_types and "SENDER_KNOWLEDGE_BASE" not in source_types:
            gaps.append("Missing sender grounding data")
        
        # Gap 3: Recency for C_LEVEL
        if RecipientArchetype == Archetype.C_LEVEL:
            recent_sources = [r for r in rag_results if r.age_days <= 90]
            if len(recent_sources) < 2:  # Lowered from 3 since strategic brief is primary
                gaps.append("Insufficient recent sources for C_LEVEL (need 2+ within 90 days)")
        
        # Confidence calculation
        confidence = self._calculate_confidence(rag_results, gaps)
        
        # Refinement tasks
        refinement_tasks = self._generate_refinement_tasks(gaps)
        
        is_sufficient = len(gaps) == 0 and confidence >= self.MIN_CONFIDENCE_THRESHOLD
        
        reasoning = f"Iteration {iteration}: {len(rag_results)} results, {len(source_types)} source types. "
        reasoning += f"Gaps: {len(gaps)}. Confidence: {confidence:.2f}"
        
        return RAGCritique(
            confidence_score=confidence,
            gaps_identified=gaps,
            refinement_tasks=refinement_tasks,
            reasoning=reasoning,
            is_sufficient=is_sufficient
        )
    
    def _calculate_confidence(self, rag_results: List[RAGResult], gaps: List[str]) -> float:
        """
        Calculate confidence score
        v12.0: Bonus for strategic brief presence
        """
        num_results = len(rag_results)
        num_source_types = len(set(r.SourceType for r in rag_results))
        base_score = min(0.75, num_results * 0.15)
        diversity_bonus = min(0.30, num_source_types * 0.10)
        gap_penalty = len(gaps) * 0.10
        
        # v12.0: Bonus for strategic brief
        strategic_brief_bonus = 0.15 if any(r.SourceType == "STRATEGIC_BRIEF" for r in rag_results) else 0.0
        
        confidence = base_score + diversity_bonus + strategic_brief_bonus - gap_penalty
        return max(0.0, min(1.0, confidence))
    
    def _generate_refinement_tasks(self, gaps: List[str]) -> List[str]:
        """Generate refinement search tasks from gaps"""
        tasks = []
        for gap in gaps:
            if "strategic brief" in gap.lower():
                tasks.append("ERROR: Strategic brief Missing - check for target_brief.pdf or *.pdf in root directory")
            elif "sender grounding" in gap.lower():
                tasks.append("Search for sender capabilities and achievements")
            elif "recent sources" in gap.lower():
                tasks.append("Focus search on content from last 90 days")
        return tasks

# ============================================================================
# MODIFIED v12.0: S2 SPECIALIST AGENTS
# ============================================================================

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

class OrganizationAgent:
    """
    v12.0: DEMOTED to secondary fact-checker role.
    Now performs validation searches based on strategic brief entities.
    """
    def __init__(self, circuit_breaker: CircuitBreaker, search_client: GoogleSearchClient) -> None:
        self.circuit_breaker = circuit_breaker
        self.search_client = search_client

    async def validate_initiative(self, initiative_name: str, mission: OutreachMission) -> Dict[str, object]:
        """
        NEW v12.0: Validate a specific initiative from strategic brief.
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

    async def get_organization_context(self, mission: OutreachMission) -> Dict[str, object]:
        """Legacy method - minimal search for basic org validation."""

        company = mission.JobDescription.get('company', '')
        query = f'"{company}" news'
        
        loop = asyncio.get_event_loop()
        search_results = await loop.run_in_executor(
            None, self.search_client.search, query, 2
        )
        
        rag_results = self._process_search_results(search_results, "")
        
        return {"rag_results": rag_results}

    async def run_refinement_task(self, Task: str, mission: OutreachMission) -> Dict[str, object]:
        """Perform targeted refinement RAG."""

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

class InternalAgent:
    """
    v12.0: UPGRADED to primary intelligence-gathering unit.
    NOW LOADS: 
    - master_resume.json (sender grounding)
    - sender_knowledge_base.json (sender grounding)
    - target_brief.pdf OR *.pdf (NEW: strategic brief)
    REMOVED: manual_rag_input.json (deprecated)
    """
    def __init__(self, circuit_breaker: CircuitBreaker) -> None:
        self.circuit_breaker = circuit_breaker

    def get_internal_context(self, mission: OutreachMission) -> Dict[str, object]:
        """
        v12.0: Load sender grounding + strategic brief.
        """

        rag_results = []
        
        # Load master_resume.json (sender grounding)
        rag_results.extend(self._load_resume_as_rag())
        
        # Load sender_knowledge_base.json (sender grounding)
        rag_results.extend(self._load_kb_as_rag())
        
        # NEW v12.0: Load strategic brief PDF
        brief_results, brief_entities = self._load_strategic_brief()
        rag_results.extend(brief_results)
        
        # DEPRECATED v12.0: manual_rag_input.json is NO LONGER loaded
        
        # Check job tracker for prior applications
        prior_applications = self._search_job_tracker(mission)

        if brief_entities:
            pass

        return {
            "prior_applications": prior_applications,
            "rag_results": rag_results,
            "brief_entities": brief_entities  # NEW v12.0: Entities to validate
        }
    
    def _load_strategic_brief(self) -> Tuple[List[RAGResult], List[Dict[str, str]]]:
        """
        NEW v12.0: Load and parse strategic brief PDF.
        Returns: (rag_results, extracted_entities)
        """
        if not PDF_SUPPORT:

            return [], []
        
        # Find PDF file (priority: target_brief.pdf, then any *.pdf)
        pdf_path = None
        if os.path.exists("target_brief.pdf"):
            pdf_path = "target_brief.pdf"
        else:
            pdf_files = glob.glob("*.pdf")
            if pdf_files:
                pdf_path = pdf_files[0]

        if not pdf_path:

            return [], []
        
        try:
            # Parse PDF
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()

            # Split into paragraphs
            paragraphs = [p.strip() for p in full_text.split('\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nfrom agentic_core.utils.core_extensions.healer_mixin import HealerMixin\n\n') if len(p.strip()) > 50]
            
            rag_results = []
            for para in paragraphs[:50]:  # Cap at 50 paragraphs to avoid overload
                keywords = [w.strip('.,!?') for w in para.split() if len(w) > 4]
                keywords = list(set(keywords[:20]))
                
                rag_results.append(RAGResult(
                    source=pdf_path,
                    SourceType="STRATEGIC_BRIEF",
                    text=para,
                    extracted_keywords=keywords,
                    source_weight=2.5,  # Highest weight
                    age_days=0,  # Assume current
                    recipient_specific=True,  # Strategic brief is recipient-specific
                    confidence=1.0
                ))
            
            # Extract entities (simple: look for capitalized names/phrases)
            entities = self._extract_entities_from_text(full_text)
            
            return rag_results, entities
            
        except Exception as e:

            return [], []
    
    def _extract_entities_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extract key entities (people, initiatives) from strategic brief.
        Returns: [{"type": "person", "name": "...", "context": "..."}, ...]
        """
        entities = []
        
        # Simple pattern matching for common entity types
        # Person names: "Name as Title" or "Name, Title"
        person_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)(?:\s+as\s+|\,\s+)([A-Z][^\.]+)'
        for match in re.finditer(person_pattern, text):
            entities.append({
                "type": "person",
                "name": match.group(1),
                "context": match.group(2)[:100]
            })
        
        # Initiative names: quoted phrases or title-cased multi-word phrases
        initiative_pattern = r'"([^"]{10,50})"'
        for match in re.finditer(initiative_pattern, text):
            phrase = match.group(1)
            if any(word[0].isupper() for word in phrase.split()):
                entities.append({
                    "type": "initiative",
                    "name": phrase,
                    "context": ""
                })
        
        # Deduplicate by name
        unique_entities = {}
        for entity in entities:
            unique_entities[entity["name"]] = entity
        
        return list(unique_entities.values())[:10]  # Cap at 10 entities
    
    def _load_resume_as_rag(self) -> List[RAGResult]:
        """Load master_resume.json and convert to RAG results."""
        filepath = "master_resume.json"
        if not os.path.exists(filepath):

            return []
        
        try:
            with open(filepath, 'r') as f:
                resume_data = json.load(f)
        except Exception as e:

            return []
        
        rag_results = []
        
        # Extract bullets from all experience entries
        for exp in resume_data.get('professional_experience', []):
            company = exp.get('company', '')
            for bullet in exp.get('bullet_pool', []):
                keywords = [w.strip('.,!?%') for w in bullet.split() if len(w) > 4]
                keywords = list(set(keywords[:15]))
                
                rag_results.append(RAGResult(
                    source=f"master_resume_{company}",
                    SourceType="MASTER_RESUME",
                    text=bullet,
                    extracted_keywords=keywords,
                    source_weight=2.0,
                    age_days=0,
                    recipient_specific=False,
                    confidence=1.0
                ))
        
        return rag_results
    
    def _load_kb_as_rag(self) -> List[RAGResult]:
        """Load sender_knowledge_base.json and convert to RAG results."""
        filepath = "sender_knowledge_base.json"
        if not os.path.exists(filepath):

            return []
        
        try:
            with open(filepath, 'r') as f:
                kb_data = json.load(f)
        except Exception as e:

            return []
        
        rag_results = []
        
        # Core value propositions
        for vp in kb_data.get('core_value_propositions', []):
            keywords = [w.strip('.,!?') for w in vp.split() if len(w) > 4]
            keywords = list(set(keywords[:15]))
            
            rag_results.append(RAGResult(
                source="sender_knowledge_base",
                SourceType="SENDER_KNOWLEDGE_BASE",
                text=vp,
                extracted_keywords=keywords,
                source_weight=1.8,
                age_days=0,
                recipient_specific=False,
                confidence=1.0
            ))
        
        # Whitelisted products
        for product in kb_data.get('whitelisted_products', []):
            name = product.get('name', '')
            desc = product.get('description', '')
            text = f"{name}: {desc}"
            keywords = [w.strip('.,!?') for w in text.split() if len(w) > 4]
            keywords = list(set(keywords[:15]))
            
            rag_results.append(RAGResult(
                source="sender_knowledge_base",
                SourceType="SENDER_KNOWLEDGE_BASE",
                text=text,
                extracted_keywords=keywords,
                source_weight=1.8,
                age_days=0,
                recipient_specific=False,
                confidence=1.0
            ))
        
        # Case studies
        for case in kb_data.get('whitelisted_case_studies', []):
            client = case.get('client', '')
            outcome = case.get('outcome', '')
            text = f"Client: {client}. {outcome}"
            keywords = [w.strip('.,!?%') for w in text.split() if len(w) > 4]
            keywords = list(set(keywords[:15]))
            
            rag_results.append(RAGResult(
                source="sender_knowledge_base",
                SourceType="SENDER_KNOWLEDGE_BASE",
                text=text,
                extracted_keywords=keywords,
                source_weight=1.8,
                age_days=0,
                recipient_specific=False,
                confidence=1.0
            ))
        
        return rag_results

    def _search_job_tracker(self, mission: OutreachMission) -> List[Dict[str, object]]:
        """Search job tracker for prior applications (placeholder)."""
        # This would integrate with actual job tracking system
        return []

# ============================================================================
# MODIFIED v12.0: S2 SUPERVISOR AGENT
# ============================================================================

class S2_SupervisorAgent:
    """
    v12.0: Updated coordination logic for strategic alignment workflow.
    Now manages entity extraction + validation flow.
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker, search_client: GoogleSearchClient, llm_client: GeminiLLMClient) -> None:
        self.circuit_breaker = circuit_breaker
        self.internal_agent = InternalAgent(circuit_breaker)
        self.recipient_agent = RecipientAgent(circuit_breaker, search_client)
        self.organization_agent = OrganizationAgent(circuit_breaker, search_client)
        self.llm_client = llm_client
        self.signal_scorer = SignalQualityScorer()
        self.claim_scorer = ClaimConfidenceScorer()
        self.rag_reflexion = RAGReflexionSystem()
        self.status = AgentStatus.IDLE
    
    async def orchestrate_research(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis,
        refinement_context: Optional[List] = None
    ) -> Tuple[ResearchContext, ProfileAnalysis]:
        """
        v12.0: Orchestrate strategic alignment research.
        Flow:
        1. InternalAgent loads strategic brief + sender grounding
        2. Extract entities from strategic brief
        3. Validate entities with RecipientAgent/OrganizationAgent
        4. Run reflexion loop if needed
        """
        self.status = AgentStatus.RUNNING

        # Phase 1: Internal grounding (strategic brief + sender data)
        internal_report = self.internal_agent.get_internal_context(mission)
        rag_results = internal_report['rag_results']
        prior_applications = internal_report['prior_applications']
        brief_entities = internal_report.get('brief_entities', [])
        
        # Phase 2: Entity validation
        if brief_entities:

            staleness_warnings = []
            for entity in brief_entities[:5]:  # Validate up to 5 entities
                if entity['type'] == 'person':
                    validation = await self.recipient_agent.validate_entity(
                        entity['name'], entity['context'], mission
                    )
                    rag_results.extend(validation['rag_results'])
                    if validation.get('staleness_warning'):
                        staleness_warnings.append(validation['staleness_warning'])
                elif entity['type'] == 'initiative':
                    validation = await self.organization_agent.validate_initiative(
                        entity['name'], mission
                    )
                    rag_results.extend(validation['rag_results'])
                    if validation.get('staleness_warning'):
                        pass
        
        # Phase 3: Light supplemental RAG (minimal - strategic brief is primary)
        # Only run if no strategic brief found
        if not any(r.SourceType == "STRATEGIC_BRIEF" for r in rag_results):

            recipient_report = await self.recipient_agent.get_profile(mission)
            org_report = await self.organization_agent.get_organization_context(mission)
            rag_results.extend(recipient_report['rag_results'])
            rag_results.extend(org_report['rag_results'])
        
        # Phase 4: Reflexion loop (if triggered by S6 failure or critique)
        reflexion_iterations = 0
        while reflexion_iterations < 2:
            
            critique = self.rag_reflexion.critique_rag_sufficiency(
                rag_results,
                profile_analysis.Archetype,
                iteration=reflexion_iterations + 1
            )
            
            if refinement_context and reflexion_iterations == 0:

                failure_rule = refinement_context[0].rule_id
                failure_msg = refinement_context[0].message
                Task = f"S6 Validation Failed ({failure_rule}): {failure_msg}. Find new evidence to resolve this."
                critique.is_sufficient = False
                critique.refinement_tasks = [Task]

            if critique.is_sufficient:

                break
            
            reflexion_iterations += 1
            Task = critique.refinement_tasks[0]

            refinement_report = None
            if any(kw in Task.lower() for kw in ["recipient", "github", "linkedin"]):
                refinement_report = await self.recipient_agent.run_refinement_task(Task, mission)
            else:
                refinement_report = await self.organization_agent.run_refinement_task(Task, mission)
            
            rag_results.extend(refinement_report['rag_results'])
        
        # Phase 5: Extract sender grounding whitelists
        sender_grounding = self._extract_sender_grounding(rag_results, mission)
        
        # Phase 6: Build ResearchContext
        context = ResearchContext(
            recipient_insights=[
                f"Title: {mission.recipient_profile.get('title')}",
                f"Company: {mission.recipient_profile.get('company')}",
                f"Archetype: {profile_analysis.Archetype.value}"
            ],
            company_context=[
                f"Company: {mission.JobDescription.get('company')}",
                f"Job: {mission.JobDescription.get('title')}"
            ],
            recent_activity=[],
            rag_results=rag_results,
            reflexion_iterations=reflexion_iterations,
            prior_applications=prior_applications,
            mission_context={
                "job_title": mission.JobDescription.get("title", ""),
                "company": mission.JobDescription.get("company", ""),
                "sender_teams": mission.sender_profile.get("teams", [])
            },
            sender_context=[],
            sender_grounding=sender_grounding
        )
        
        # Phase 7: Archetype critique
        # corrected_profile_analysis = self._critique_archetype_classification(
        # TODO: Fix incomplete function call
        corrected_profile_analysis = None  # Placeholder
        # Phase 8: Adversarial check
        adversarial_findings = await self._run_adversarial_check(context)
        context.adversarial_findings = adversarial_findings
        if adversarial_findings:
            pass

        self.status = AgentStatus.COMPLETED
        
        return context, corrected_profile_analysis
    
    async def _run_adversarial_check(self, context: ResearchContext) -> List[str]:
        # ... (rest of the code remains the same)

        rag_summary = "\n".join([
            f"- {r.SourceType}: {r.text[:100]}..." 
            for r in context.rag_results[:10]
        ])
        
        critique_prompt = f"""You are an adversarial reviewer. Review the following research findings and identify any weak or unsupported claims:

{rag_summary}

List any findings that appear:
1. Tangential or loosely connected to the core message
2. Overly generic without specific evidence
3. Could be refuted with minimal scrutiny

Return a numbered list of weaknesses (max 3). Format: "1. [weakness]"
"""
        
        loop = asyncio.get_event_loop()
        try:
            findings_text = await loop.run_in_executor(
                None, self.llm_client.generate, critique_prompt
            )
            
            findings = [
                f.strip() 
                for f in findings_text.split('\n') 
                if f.strip() and len(f.strip()) > 10
            ]
            
            return findings[:3]
            
        except Exception as e:

            return []

    def _extract_sender_grounding(
        self,
        rag_results: List[RAGResult],
        mission: OutreachMission
    ) -> SenderGroundingWhitelists:
        """Extract sender grounding whitelists from RAG."""
        grounding = SenderGroundingWhitelists()
        
        for result in rag_results:
            text_lower = result.text.lower()
            
            if any(marker in text_lower for marker in ["team member", "colleague", "worked with", "collaborator"]):
                names = self._extract_names_from_text(result.text)
                grounding.team_members.extend(names)
                if names:
                    grounding.raw_evidence["team_members"] = grounding.raw_evidence.get("team_members", []) + [result.text[:200]]
            
            if any(marker in text_lower for marker in ["product", "platform", "solution", "service"]):
                products = self._extract_capitalized_phrases(result.text)
                grounding.products.extend(products)
                if products:
                    grounding.raw_evidence["products"] = grounding.raw_evidence.get("products", []) + [result.text[:200]]
            
            if any(marker in text_lower for marker in ["client", "customer", "case study", "project for"]):
                cases = self._extract_capitalized_phrases(result.text)
                grounding.case_studies.extend(cases)
                if cases:
                    grounding.raw_evidence["case_studies"] = grounding.raw_evidence.get("case_studies", []) + [result.text[:200]]
        
        grounding.team_members = list(set(grounding.team_members))
        grounding.products = list(set(grounding.products))
        grounding.case_studies = list(set(grounding.case_studies))
        
        return grounding
    
    def _extract_names_from_text(self, text: str) -> List[str]:
        """Extract person names from text."""
        words = text.split()
        names = []
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    full_name = f"{word} {words[i + 1]}"
                    names.append(full_name)
        return names
    
    def _extract_capitalized_phrases(self, text: str) -> List[str]:
        """Extract capitalized phrases."""
        words = text.split()
        phrases = []
        current_phrase = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                current_phrase.append(word)
            else:
                if len(current_phrase) >= 2:
                    phrases.append(" ".join(current_phrase))
                current_phrase = []
        if len(current_phrase) >= 2:
            phrases.append(" ".join(current_phrase))
        return phrases
    
    def _critique_archetype_classification(
        self,
        provisional_analysis: ProfileAnalysis,
        context: ResearchContext
    ) -> ProfileAnalysis:
        """Agentic self-correction of Archetype classification."""
        all_text = " ".join([r.text for r in context.rag_results]).lower()
        
        if provisional_analysis.Archetype != Archetype.C_LEVEL:
            if any(term in all_text for term in ["strategic vision", "board member", "company direction"]):
                critique = "RAG evidence suggests C_LEVEL status (strategic indicators)"
                provisional_analysis.Archetype = Archetype.C_LEVEL
                provisional_analysis.confidence = 0.90
                provisional_analysis.critique_history.append(critique)
        
        if provisional_analysis.Archetype != Archetype.RECRUITER:
            if any(term in all_text for term in ["talent acquisition", "hiring manager", "recruitment"]):
                critique = "RAG evidence suggests RECRUITER role (hiring indicators)"
                provisional_analysis.Archetype = Archetype.RECRUITER
                provisional_analysis.confidence = 0.88
                provisional_analysis.critique_history.append(critique)
        
        return provisional_analysis