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

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
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
        results = {"passed": 0, "failed": 0, TESTS_DIR: []}
        try:
            assert self is not None
            results["passed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
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


# ============================================================================
# MODIFIED v12.0: S2 SUPERVISOR AGENT
# ============================================================================
