# File: rag.py
# Description: RAG (Retrieval-Augmented Generation) agents and utilities

__version__ = "11.10"
# for the LIC workflow.

import asyncio
import re
from collections import defaultdict
from typing import Dict, List, Any, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models import (
    RAGResult, ResearchContext, ProfileAnalysis, Archetype, RAGCritique, 
    MessageClaim, OutreachMission, SenderGroundingWhitelists, AgentStatus
)
from utils import CircuitBreaker

# ============================================================================
# NEW v11.6: SIGNAL QUALITY SCORER (FEATURE 1.1)
# ============================================================================

class SignalQualityScorer:
    """
    Weights RAG sources by reliability for message generation
    FEATURE 1.1 from SUPREME_SPELL
    """
    
    SOURCE_WEIGHTS = {
        "RECIPIENT_LINKEDIN_ABOUT": 2.0,
        "RECIPIENT_RECENT_POST": 1.8,
        "COMPANY_BLOG_ANNOUNCEMENT": 1.5,
        "COMPANY_LINKEDIN_PAGE": 1.3,
        "NEWS_ARTICLE_COMPANY": 1.2,
        "COMPETITOR_COMPARISON": 0.9,
        "GENERIC_INDUSTRY_TREND": 0.6,
        "SENDER_PROFILE_ONLY": 0.3
    }
    
    MINIMUM_SIGNAL_THRESHOLD = 0.70
    
    def calculate_signal_score(
        self,
        rag_results: List[RAGResult],
        message_content: str
    ) -> Tuple[float, Dict[str, int]]:
        """
        Calculate weighted signal quality score for generated message
        """
        keyword_scores = defaultdict(float)
        source_breakdown = defaultdict(int)
        
        for result in rag_results:
            weight = self.SOURCE_WEIGHTS.get(result.source_type, 0.5)
            for keyword in result.extracted_keywords:
                if keyword.lower() in message_content.lower():
                    keyword_scores[keyword] += weight
                    source_breakdown[result.source_type] += 1
        
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
    Per-claim confidence scoring with rejection gate
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
        Score individual claim based on RAG evidence
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
            claim = self.score_claim(sentence, rag_results)
            claims.append(claim)
        
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
    """
    
    MIN_CONFIDENCE_THRESHOLD = 0.70
    MAX_ITERATIONS = 3
    
    def critique_rag_sufficiency(
        self,
        rag_results: List[RAGResult],
        recipient_archetype: Archetype,
        iteration: int
    ) -> RAGCritique:
        """
        Critique RAG research quality and identify gaps
        """
        gaps = []
        
        # Gap 1: Source diversity
        source_types = set(r.source_type for r in rag_results)
        if "RECIPIENT_LINKEDIN_ABOUT" not in source_types:
            gaps.append("Missing direct recipient profile data")
        if "COMPANY_BLOG_ANNOUNCEMENT" not in source_types:
            gaps.append("Missing recent company announcements")
        
        # Gap 2: Recency for C_LEVEL
        if recipient_archetype == Archetype.C_LEVEL:
            recent_sources = [r for r in rag_results if r.age_days <= 90]
            if len(recent_sources) < 3:
                gaps.append("Insufficient recent sources for C_LEVEL (need 3+ within 90 days)")
        
        # Gap 3: Personalization depth
        recipient_specific = [r for r in rag_results if r.recipient_specific]
        if len(recipient_specific) < 2:
            gaps.append("Insufficient recipient-specific context (need 2+ personalized insights)")
        
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
        Updated v11.6.1: Less conservative calculation for better usability
        """
        num_results = len(rag_results)
        num_source_types = len(set(r.source for r in rag_results))
        base_score = min(0.75, num_results * 0.15)
        diversity_bonus = min(0.30, num_source_types * 0.10)
        gap_penalty = len(gaps) * 0.10
        confidence = base_score + diversity_bonus - gap_penalty
        return max(0.0, min(1.0, confidence))
    
    def _generate_refinement_tasks(self, gaps: List[str]) -> List[str]:
        """Generate refinement search tasks from gaps"""
        tasks = []
        for gap in gaps:
            if "recipient profile" in gap.lower():
                tasks.append("Search for recipient LinkedIn profile and recent posts")
            elif "company announcements" in gap.lower():
                tasks.append("Search for company blog and recent news")
            elif "recent sources" in gap.lower():
                tasks.append("Focus search on content from last 90 days")
            elif "personalized insights" in gap.lower():
                tasks.append("Search for recipient-specific achievements and projects")
        return tasks

# ============================================================================
# NEW v11.10: S2 SPECIALIST AGENTS (Enhancement 1)
# ============================================================================

class RecipientAgent:
    """
    NEW v11.10: Specialist agent for recipient-facing RAG.
    Tools: LinkedIn, GitHub, Conference Talks retrievers (mocked).
    """
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker

    async def get_profile(self, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform RAG on recipient's public footprint."""
        print("     S2.RecipientAgent: Retrieving profile (LinkedIn, GitHub)...")
        await asyncio.sleep(0.1) # Simulate async RAG
        return {
            "rag_results": [
                RAGResult(
                    source="recipient_linkedin",
                    source_type="RECIPIENT_LINKEDIN_ABOUT",
                    text=f"About {mission.recipient_profile.get('name')}: {mission.recipient_profile.get('title')} at {mission.recipient_profile.get('company')}",
                    extracted_keywords=["leadership", "innovation", "technology"],
                    source_weight=2.0,
                    age_days=0,
                    recipient_specific=True
                )
            ]
        }
    
    async def run_refinement_task(self, task: str, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform a targeted refinement RAG task."""
        print(f"     S2.RecipientAgent: Running refinement task: '{task[:50]}...'")
        await asyncio.sleep(0.1)
        return {
            "rag_results": [
                RAGResult(
                    source="recipient_github",
                    source_type="RECIPIENT_GITHUB_REPO",
                    text="Refined search found GitHub repo for recipient.",
                    extracted_keywords=["python", "agentic", "oss"],
                    source_weight=1.8,
                    age_days=10,
                    recipient_specific=True
                )
            ]
        }

class OrganizationAgent:
    """
    NEW v11.10: Specialist agent for organization-facing RAG.
    Tools: Company Blog, News, Industry Reports retrievers (mocked).
    """
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker

    async def get_organization_context(self, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform RAG on organization's public footprint."""
        print("     S2.OrganizationAgent: Retrieving org context (Blog, News)...")
        await asyncio.sleep(0.15) # Simulate async RAG
        return {
            "rag_results": [
                RAGResult(
                    source="company_page",
                    source_type="COMPANY_LINKEDIN_PAGE",
                    text=f"{mission.job_description.get('company')} is a leading technology company",
                    extracted_keywords=["technology", "innovation", "growth"],
                    source_weight=1.3,
                    age_days=30,
                    recipient_specific=False
                )
            ]
        }

    async def run_refinement_task(self, task: str, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform a targeted refinement RAG task."""
        print(f"     S2.OrganizationAgent: Running refinement task: '{task[:50]}...'")
        await asyncio.sleep(0.1)
        
        # Mock finding evidence for a failed S6 metric validation
        if "metric" in task.lower():
             return {
                "rag_results": [
                    RAGResult(
                        source="company_blog_metric_search",
                        source_type="COMPANY_BLOG_ANNOUNCEMENT",
                        text="Our new platform launch resulted in a 40% reduction in processing time.",
                        extracted_keywords=["40%", "reduction", "processing time"],
                        source_weight=1.5,
                        age_days=15,
                        recipient_specific=False
                    )
                ]
            }
        
        return {
            "rag_results": [
                RAGResult(
                    source="company_blog",
                    source_type="COMPANY_BLOG_ANNOUNCEMENT",
                    text="Recent announcement about company growth and new AI platform.",
                    extracted_keywords=["growth", "expansion", "hiring", "AI platform"],
                    source_weight=1.5,
                    age_days=15,
                    recipient_specific=False
                )
            ]
        }

class InternalAgent:
    """
    NEW v11.10: Specialist agent for internal-facing data lookups.
    Tools: Job Tracker (mocked).
    """
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker

    def get_internal_context(self, mission: OutreachMission) -> Dict[str, Any]:
        """Mock: Perform internal data lookups."""
        print("     S2.InternalAgent: Checking job tracker for prior applications...")
        prior_applications = self._search_job_tracker(mission)
        return {
            "prior_applications": prior_applications,
            "rag_results": [] # Internal agent doesn't produce RAG results directly
        }

    def _search_job_tracker(self, mission: OutreachMission) -> List[Dict[str, Any]]:
        """
        NEW v11.6: Search for prior applications to same company (GAP 4.1)
        (Moved to InternalAgent in v11.10)
        """
        # Simulated - would search project knowledge/database
        company = mission.job_description.get("company", "")
        # For now, return empty list (no prior applications)
        return []

class S2_SupervisorAgent:
    """
    NEW v11.10: Replaces ResearchOrchestrator (Enhancement 1).
    Acts as a planner/delegator for a team of specialist agents.
    Runs an internal "Execute-Critique-Replan" loop (Enhancement 2).
    Runs an "Adversarial Self-Verification" step (Enhancement 3).
    Accepts an "S6->S2 Meta-Loop" refinement context (Enhancement 4).
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
        self.signal_scorer = SignalQualityScorer()
        self.rag_reflexion = RAGReflexionSystem()
        
        # NEW v11.10: Instantiate specialist agent team
        self.recipient_agent = RecipientAgent(circuit_breaker)
        self.organization_agent = OrganizationAgent(circuit_breaker)
        self.internal_agent = InternalAgent(circuit_breaker)
    
    async def conduct_research(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis,
        refinement_context: List['models.ValidationResult'] = None # NEW v11.10
    ) -> Tuple[ResearchContext, ProfileAnalysis]:
        """
        NEW v11.10: Agentic planner/delegator workflow.
        """
        self.status = AgentStatus.RUNNING
        
        rag_results = []
        reflexion_iterations = 0
        
        # Initial research plan
        print("     S2.Supervisor: Generating initial research plan...")
        
        # Delegation (Parallel Execution)
        print("     S2.Supervisor: Delegating to specialist agents (parallel)...")
        recipient_report_task = self.recipient_agent.get_profile(mission)
        org_report_task = self.organization_agent.get_organization_context(mission)
        
        internal_report = self.internal_agent.get_internal_context(mission)
        prior_applications = internal_report['prior_applications']
        
        recipient_report, org_report = await asyncio.gather(
            recipient_report_task,
            org_report_task
        )
        
        # Synthesis
        rag_results.extend(recipient_report['rag_results'])
        rag_results.extend(org_report['rag_results'])
        
        # Internal Critique Loop
        while reflexion_iterations < 2: # Max 2 internal refinement loops
            
            critique = self.rag_reflexion.critique_rag_sufficiency(
                rag_results,
                profile_analysis.archetype,
                iteration=reflexion_iterations + 1
            )
            
            if refinement_context and reflexion_iterations == 0:
                print("     S2.Supervisor: Received S6 failure context. Forcing refinement task.")
                failure_rule = refinement_context[0].rule_id
                failure_msg = refinement_context[0].message
                task = f"S6 Validation Failed ({failure_rule}): {failure_msg}. Find new evidence to resolve this."
                critique.is_sufficient = False
                critique.refinement_tasks = [task]

            if critique.is_sufficient:
                print(f"     S2.Supervisor: Internal critique PASSED (Iteration {reflexion_iterations + 1}).")
                break
            
            reflexion_iterations += 1
            task = critique.refinement_tasks[0]
            print(f"     S2.Supervisor: Internal critique FAILED. Refining task: '{task[:50]}...'")
            
            refinement_report = None
            if any(kw in task.lower() for kw in ["recipient", "github", "linkedin"]):
                refinement_report = await self.recipient_agent.run_refinement_task(task, mission)
            else:
                refinement_report = await self.organization_agent.run_refinement_task(task, mission)
            
            rag_results.extend(refinement_report['rag_results'])
        
        sender_grounding = self._extract_sender_grounding(rag_results, mission)
        
        context = ResearchContext(
            recipient_insights=[
                f"Title: {mission.recipient_profile.get('title')}",
                f"Company: {mission.recipient_profile.get('company')}",
                f"Archetype: {profile_analysis.archetype.value}"
            ],
            company_context=[
                f"Company: {mission.job_description.get('company')}",
                f"Job: {mission.job_description.get('title')}"
            ],
            recent_activity=[],
            rag_results=rag_results,
            reflexion_iterations=reflexion_iterations,
            prior_applications=prior_applications,
            mission_context={
                "job_title": mission.job_description.get("title", ""),
                "company": mission.job_description.get("company", ""),
                "sender_teams": mission.sender_profile.get("teams", [])
            },
            sender_context=[],
            sender_grounding=sender_grounding
        )
        
        corrected_profile_analysis = self._critique_archetype_classification(
            profile_analysis,
            context
        )
        
        adversarial_findings = await self._run_adversarial_check(context)
        context.adversarial_findings = adversarial_findings
        if adversarial_findings:
            print(f"     S2.Supervisor: Adversarial check flagged {len(adversarial_findings)} weak claims.")
        
        self.status = AgentStatus.COMPLETED
        
        return context, corrected_profile_analysis
    
    async def _run_adversarial_check(self, context: ResearchContext) -> List[str]:
        """
        NEW v11.10: Mocked "Red Team" adversarial check (Enhancement 3).
        """
        print("     S2.Supervisor: Running Adversarial Self-Verification (Red Team)...")
        await asyncio.sleep(0.05) # Simulate LLM call
        mock_findings = ["Refuted theme: 'direct experience with scaling' (evidence is tangential)"]
        return mock_findings

    def _extract_sender_grounding(
        self,
        rag_results: List[RAGResult],
        mission: OutreachMission
    ) -> SenderGroundingWhitelists:
        """
        NEW v11.9: Extract sender grounding whitelists from RAG (SPEC 1)
        """
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
        """Extract person names from text (simplified - production would use NER)"""
        words = text.split()
        names = []
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    full_name = f"{word} {words[i + 1]}"
                    names.append(full_name)
        return names
    
    def _extract_capitalized_phrases(self, text: str) -> List[str]:
        """Extract capitalized phrases (product/company names)"""
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
        """
        NEW v11.6: Agentic self-correction of archetype classification
        """
        all_text = " ".join([r.text for r in context.rag_results]).lower()
        
        if provisional_analysis.archetype != Archetype.C_LEVEL:
            if any(term in all_text for term in ["strategic vision", "board member", "company direction"]):
                critique = "RAG evidence suggests C_LEVEL status (strategic indicators)"
                provisional_analysis.archetype = Archetype.C_LEVEL
                provisional_analysis.confidence = 0.90
                provisional_analysis.critique_history.append(critique)
        
        if provisional_analysis.archetype != Archetype.RECRUITER:
            if any(term in all_text for term in ["talent acquisition", "hiring manager", "recruitment"]):
                critique = "RAG evidence suggests RECRUITER role (hiring indicators)"
                provisional_analysis.archetype = Archetype.RECRUITER
                provisional_analysis.confidence = 0.88
                provisional_analysis.critique_history.append(critique)
        
        return provisional_analysis