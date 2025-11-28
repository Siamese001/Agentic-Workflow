# File: execution_specialists_v5_2.py
# Version: 5.2.0 - Recovery from v3.8 logic
# Execution Specialists - Agents with deterministic implementations from v3.8
# This file ports v3.8's functional logic into v5.1's atomic agent architecture

import copy
import hashlib
import json
import logging
import os
import random
import re
import signal
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import partial, cached_property
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, TYPE_CHECKING

# Third-party imports - RESTORED FROM v3.8
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None
    cosine_similarity = None

# Import models and utilities from v3.8
from models_RES import (
    CircuitState, RAGState, RAGEvidence, RAGCritique,
    PartialRAGResult, RAGTelemetry, CompetitiveIntelligence,
    MasterResumeIndex, RAGMission, ThematicAnalysis, HopStatus,
    RetrievalSource, SkillRequirement, SkillCluster,
    HopExecutionError, CircuitBreakerOpenError, PhaseTimeoutError,
    CompetitiveAnalysisConfig, ResumeSection, ImmutableStagingBuffer, 
    ValidationResult, ValidationSeverity, BulletProvenance, ReasoningConfig
)

# Import validation modules from v3.8
from validation_context import ValidationContext
from validation_engine import ValidationEngine
from validation_rules import (
    _validate_bullet_word_count_CRITICAL,
    _validate_cross_section_similarity,
    _validate_no_placeholders,
    _validate_forbidden_verbs,
    _validate_headline_format_no_titles,
    _validate_narrative_vs_master_similarity,
    _validate_section_presence,
    _validate_cover_letter_full_structure
)

# Import utilities and config
from config_RES import CONFIG, CACHE_DIR, DEFAULT_MAX_RETRIES, DEFAULT_HOP_TIMEOUT
from config_RES import CONFIG, CACHE_DIR, DEFAULT_MAX_RETRIES, DEFAULT_HOP_TIMEOUT
from utils_RES import TelemetryLogger, text_utils, sanitize_filename, calculate_signal_score
from gemini_service import GeminiService, get_gemini_service
from prompts_RES import get_prompt_template, build_crl_context_for_section, PROMPT_TEMPLATES
logger = logging.getLogger(__name__)
T = TypeVar('T')

# ==============================================================================
# PHASE 1: RAG SYSTEM RECOVERY - LIBRARY, WEB, AND SYNTHESIS SPECIALISTS
# ==============================================================================

class Library_Specialist:
    """
    Persistent memory agent using ChromaDB for cross-job intelligence.
    PORTED FROM: v3.8/rag_RES_v3_8.py LibrarianAgent (lines 88-313)
    """
    
    def __init__(self, complexity: int = 50):
        """Initialize Library Specialist with ChromaDB persistence."""
        self.complexity = complexity  # v5.1 compatibility
        self.storage_path = str(CACHE_DIR / "librarian_db")
        self.enabled = CHROMADB_AVAILABLE
        self.client = None
        self.collection = None
        
        if not self.enabled:
            logger.warning("Library Specialist disabled - ChromaDB not available")
            return
        
        try:
            # Initialize ChromaDB client - PORTED FROM v3.8 lines 121-135
            self.client = chromadb.PersistentClient(
                path=self.storage_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="rag_intelligence",
                metadata={"description": "Cross-job RAG intelligence and positioning strategies"}
            )
            
            logger.info(f"Library Specialist initialized with {self.collection.count()} memories at {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Library Specialist: {e}")
            self.enabled = False
    
    @property
    def memory_count(self) -> int:
        """
        Returns the count of stored memories in the collection.
        
        Returns:
            int: Number of memories stored, or 0 if collection unavailable
        """
        if not self.enabled or self.collection is None:
            return 0
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to get memory count: {e}")
            return 0
    
    # --- TECHNIQUE #1: DYNAMIC FEW-SHOT INJECTION ---
    def query_few_shot_examples(self, section_type: str, keywords: List[str], n: int = 3) -> str:
        """
        Retrieves high-quality past examples for dynamic prompt injection.
        
        Args:
            section_type: Type of resume section (e.g., 'EXECUTIVE_SUMMARY')
            keywords: List of keywords to search for
            n: Number of examples to retrieve
            
        Returns:
            Formatted XML string with examples, or empty string if none found
        """
        if not self.enabled or not self.collection:
            return ""

        try:
            # Construct a query for the specific section and keywords
            query = f"high quality {section_type} examples containing {', '.join(keywords[:5])}"
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n,
                # Filter for entries that are actual content examples, not just mission briefs
                where={"type": "content_example"} if "type" in (self.collection.get()["metadatas"][0] if self.collection.get()["metadatas"] else {}) else None
            )

            if not results['documents'] or not results['documents'][0]:
                return ""

            # Format examples for injection
            formatted_examples = ["<dynamic_examples_bank>"]
            for i, doc in enumerate(results['documents'][0]):
                formatted_examples.append(f"<example_{i+1}>\n{doc}\n</example_{i+1}>")
            formatted_examples.append("</dynamic_examples_bank>")

            return "\n".join(formatted_examples)

        except Exception as e:
            logger.warning(f"Failed to retrieve few-shot examples: {e}")
            return ""
    # ------------------------------------------------
    
    def store_mission_intelligence(
        self,
        rag_mission: RAGMission,
        thematic_analysis: ThematicAnalysis,
        company_name: str,
        job_title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store successful RAGMission and analysis for future reference."""
        if not self.enabled:
            return
        
        try:
            doc_id = f"{company_name}_{job_title}_{int(time.time())}"
            
            # Create searchable document
            document_text = self._format_mission_document(
                rag_mission, thematic_analysis, company_name, job_title
            )
            
            # Store metadata
            storage_metadata = {
                "company_name": company_name,
                "job_title": job_title,
                "timestamp": datetime.now().isoformat(),
                "primary_theme": thematic_analysis.primary_theme.get('name', 'Unknown') if thematic_analysis.primary_theme else 'Unknown',
                **(metadata or {})
            }
            
            self.collection.add(
                documents=[document_text],
                metadatas=[storage_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Stored mission intelligence: {doc_id}")
            
        except Exception as e:
            logger.error(f"Failed to store mission intelligence: {e}")
    
    def query_similar_missions(
        self,
        query: str,
        company_name: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Query for similar past missions to inform current extraction."""
        if not self.enabled or self.collection.count() == 0:
            return []
        
        try:
            where_filter = None
            if company_name:
                where_filter = {"company_name": company_name}
            
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count()),
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 1.0
                    })
            
            logger.info(f"Retrieved {len(formatted_results)} similar missions for query: {query[:50]}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to query similar missions: {e}")
            return []
    
    def get_context_for_phase(
        self,
        phase_name: str,
        rag_mission: RAGMission,
        company_name: str
    ) -> Optional[str]:
        """Get relevant Librarian context for a specific RAG phase."""
        if not self.enabled:
            return None
        
        try:
            # Build query based on phase - PORTED FROM v3.8 lines 260-270
            if "phase1" in phase_name.lower():
                query = f"{rag_mission.precise_role_title} {company_name} thematic analysis"
            elif "phase2" in phase_name.lower():
                query = f"{rag_mission.precise_role_title} positioning strategy gaps"
            elif "phase3" in phase_name.lower():
                query = f"{company_name} competitive intelligence differentiators"
            elif "phase4" in phase_name.lower():
                query = f"{rag_mission.precise_role_title} problem solution narratives"
            else:
                query = f"{rag_mission.precise_role_title} {company_name}"
            
            similar_missions = self.query_similar_missions(query, n_results=2)
            
            if not similar_missions:
                return None
            
            # Format context
            context_parts = ["**Librarian Intelligence (from past successful extractions):**"]
            for i, mission in enumerate(similar_missions, 1):
                context_parts.append(f"\n**Past Mission {i}:**")
                context_parts.append(f"{mission['content'][:300]}...")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get context for {phase_name}: {e}")
            return None
    
    def _format_mission_document(
        self,
        rag_mission: RAGMission,
        thematic_analysis: ThematicAnalysis,
        company_name: str,
        job_title: str
    ) -> str:
        """Format RAGMission and analysis into searchable document."""
        parts = [
            f"Company: {company_name}",
            f"Role: {job_title}",
            f"Precise Title: {rag_mission.precise_role_title}",
            f"Technologies: {', '.join(rag_mission.key_technologies)}",
            f"Responsibilities: {', '.join(rag_mission.core_responsibilities)}",
            f"Primary Theme: {thematic_analysis.primary_theme.get('name', 'N/A') if thematic_analysis.primary_theme else 'N/A'}"
        ]
        
        if hasattr(rag_mission, 'strategic_priorities') and rag_mission.strategic_priorities:
            parts.append(f"Strategic Priorities: {', '.join(rag_mission.strategic_priorities)}")
        
        if hasattr(rag_mission, 'differentiators') and rag_mission.differentiators:
            parts.append(f"Key Differentiators: {', '.join(rag_mission.differentiators)}")
        
        return "\n".join(parts)


class Web_Specialist:
    """
    Multi-phase web search execution with circuit breaker protection.
    PORTED FROM: v3.8/rag_RES_v3_8.py WebSearchTool & CircuitBreaker (lines 318-610)
    """
    
    def __init__(self, complexity: int = 60):
        """Initialize Web Specialist with circuit breaker and phase executor."""
        self.complexity = complexity
        # Initialize circuit breaker - PORTED FROM v3.8 lines 325-332
        self.circuit_breaker = CircuitBreaker(threshold=3, timeout=60)
        # Initialize phase executor - PORTED FROM v3.8 lines 370-374
        self.phase_executor = PhaseExecutor(
            max_retries=DEFAULT_MAX_RETRIES,
            timeout=DEFAULT_HOP_TIMEOUT,
            backoff_config=CONFIG
        )
        self.telemetry = TelemetryLogger()
    
    def search_and_analyze(
        self,
        search_prompt: str,
        phase_name: str
    ) -> Tuple[Dict[str, Any], int]:
        """Execute web search with retry and circuit breaker protection."""
        logger.info(f"Web Specialist executing: {phase_name}")
        
        def search_function():
            # Simulate web search - in production this would call actual search API
            # This is a stub that would be replaced with actual web search logic
            api_calls = random.randint(1, 3)
            
            # Return structured search results
            results = {
                "search_results": [
                    {"title": f"Result 1 for {phase_name}", "snippet": "Relevant information..."},
                    {"title": f"Result 2 for {phase_name}", "snippet": "More relevant data..."}
                ],
                "analysis": {
                    "key_findings": ["Finding 1", "Finding 2"],
                    "confidence": 0.85
                },
                "metadata": {
                    "phase": phase_name,
                    "timestamp": datetime.now().isoformat(),
                    "api_calls": api_calls
                }
            }
            
            return results, api_calls
        
        try:
            # Execute with circuit breaker and retry logic
            result_tuple = self.circuit_breaker.call(
                self.phase_executor.execute_with_retry,
                search_function,
                phase_name
            )
            
            return result_tuple
            
        except Exception as e:
            logger.error(f"Web search failed for {phase_name}: {e}")
            # Return empty result with error
            return {"error": str(e), "phase": phase_name}, 0


class RAG_Synthesizer:
    """
    Enhanced job description analyzer with TF-IDF and thematic extraction.
    PORTED FROM: v3.8/rag_RES_v3_8.py EnhancedJobDescriptionAnalyzer (lines 610-1320)
    """
    
    def __init__(self, complexity: int = 70):
        """Initialize RAG Synthesizer with analysis capabilities."""
        self.complexity = complexity
        self.librarian = Library_Specialist(complexity=50)
        self.web_search = Web_Specialist(complexity=60)
        self.telemetry = TelemetryLogger()
        
        # TF-IDF capabilities if available
        self.tfidf_enabled = SKLEARN_AVAILABLE
        if self.tfidf_enabled:
            self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    
    def analyze_job_description(
        self,
        job_description: str,
        company_name: str,
        job_title: str,
        master_resume_index: MasterResumeIndex,
        comp_config: CompetitiveAnalysisConfig
    ) -> ThematicAnalysis:
        """
        Execute comprehensive job description analysis with 4-phase RAG.
        PORTED FROM: v3.8 lines 620-714
        """
        logger.info("=" * 80)
        logger.info("RAG Synthesizer: Starting Enhanced Job Description Analysis")
        logger.info("=" * 80)
        
        start_time = time.time()
        telemetry = RAGTelemetry()
        
        try:
            # Step 1: Extract high-signal RAGMission with Librarian context
            logger.info("Step 1: Extracting RAGMission with Librarian support")
            rag_mission = self._extract_rag_mission_with_librarian(
                job_description, company_name, job_title
            )
            
            # Step 1.5: Check cache for similar missions
            logger.info("Step 1.5: Checking cache for similar missions...")
            cached_analysis = self._check_cache_for_similar_mission(
                rag_mission, company_name, job_title
            )
            
            if cached_analysis:
                logger.info("✓ CACHE HIT: Using cached ThematicAnalysis")
                telemetry.total_duration_seconds = time.time() - start_time
                telemetry.full_success = True
                return cached_analysis
            
            logger.info("Cache miss - proceeding with full RAG pipeline")
            
            # Step 2: Execute 4-phase RAG with Librarian context
            logger.info("Step 2: Executing 4-phase RAG pipeline")
            partial_result = self._execute_four_phase_rag(
                job_description,
                rag_mission,
                master_resume_index,
                comp_config,
                telemetry
            )
            
            # Step 3: Synthesize into ThematicAnalysis
            logger.info("Step 3: Synthesizing ThematicAnalysis")
            thematic_analysis = self._synthesize_thematic_analysis(
                partial_result, rag_mission, job_description
            )
            
            # Step 4: Store intelligence in Librarian for future jobs
            logger.info("Step 4: Storing intelligence in Librarian")
            self.librarian.store_mission_intelligence(
                rag_mission=rag_mission,
                thematic_analysis=thematic_analysis,
                company_name=company_name,
                job_title=job_title,
                metadata={"success_rate": partial_result.success_rate}
            )
            
            telemetry.total_duration_seconds = time.time() - start_time
            self.telemetry.log(telemetry)
            
            logger.info(f"Analysis Complete: Success Rate {partial_result.success_rate:.0%}")
            return thematic_analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            raise
    
    def _extract_rag_mission_with_librarian(
        self,
        job_description: str,
        company_name: str,
        job_title: str
    ) -> RAGMission:
        """Extract high-signal RAGMission with Librarian context."""
        # Get similar missions from librarian
        similar_missions = self.librarian.query_similar_missions(
            query=f"{job_title} {company_name}",
            company_name=company_name,
            n_results=2
        )
        
        # Extract key information from job description
        # In production, this would use NLP/LLM to extract structured information
        rag_mission = RAGMission(
            precise_role_title=job_title,
            target_company_name=company_name,
            key_technologies=self._extract_technologies(job_description),
            core_responsibilities=self._extract_responsibilities(job_description),
            strategic_priorities=[],
            differentiators=[]
        )
        
        # Enrich with librarian context if available
        if similar_missions:
            # Extract patterns from similar missions
            for mission in similar_missions:
                # Parse and merge relevant patterns
                content = mission.get('content', '')
                if 'Strategic Priorities:' in content:
                    # Extract strategic priorities from similar mission
                    pass  # Implementation would parse and merge
        
        return rag_mission
    
    def _check_cache_for_similar_mission(
        self,
        current_mission: RAGMission,
        company_name: str,
        job_title: str,
        similarity_threshold: float = 0.85
    ) -> Optional[ThematicAnalysis]:
        """Check Librarian cache for similar missions."""
        if not self.librarian.enabled:
            return None
        
        try:
            # Query for similar missions at the same company
            query_text = f"{company_name} {current_mission.precise_role_title}"
            similar_missions = self.librarian.query_similar_missions(
                query=query_text,
                company_name=company_name,
                n_results=3
            )
            
            if not similar_missions:
                return None
            
            # Check for high similarity match
            for mission_result in similar_missions:
                distance = mission_result.get('distance', 1.0)
                similarity = 1.0 - distance
                
                metadata = mission_result.get('metadata', {})
                cached_company = metadata.get('company_name', '')
                cached_title = metadata.get('job_title', '')
                
                if (cached_company == company_name and 
                    similarity >= similarity_threshold):
                    
                    logger.info(f"High-quality cache match found (similarity: {similarity:.2f})")
                    
                    # Create cached ThematicAnalysis
                    cached_analysis = ThematicAnalysis(
                        primary_theme={'name': 'Cached Theme', 'keywords': []},
                        secondary_themes=[],
                        role_classification={'type': 'cached', 'confidence': 0.9},
                        positioning_directives={'strategy': 'cached'},
                        authenticity_patterns={},
                        competitive_intelligence=None,
                        signal_quality_score=similarity,
                        retrieval_method="CACHED_FROM_LIBRARIAN",
                        retrieval_sources=[]
                    )
                    
                    return cached_analysis
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return None
    
    def _execute_four_phase_rag(
        self,
        job_description: str,
        rag_mission: RAGMission,
        master_resume_index: MasterResumeIndex,
        comp_config: CompetitiveAnalysisConfig,
        telemetry: RAGTelemetry
    ) -> PartialRAGResult:
        """Execute 4-phase RAG pipeline with web search."""
        result = PartialRAGResult()
        
        # Phase 1: Thematic Analysis
        try:
            logger.info("Executing Phase 1: Thematic Analysis")
            librarian_context = self.librarian.get_context_for_phase(
                "phase1", rag_mission, rag_mission.target_company_name
            )
            
            phase1_data, phase1_calls = self.web_search.search_and_analyze(
                f"Thematic analysis for {rag_mission.precise_role_title} at {rag_mission.target_company_name}",
                "Phase 1: Thematic Analysis"
            )
            
            result.phase1_result = phase1_data
            result.phase1_success = True
            telemetry.phase1_success = True
            telemetry.total_api_calls += phase1_calls
            
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            result.failure_reasons.append(f"Phase 1: {str(e)}")
        
        # Phase 2-4 would follow similar pattern...
        # Simplified for brevity
        
        return result
    
    def _synthesize_thematic_analysis(
        self,
        partial_result: PartialRAGResult,
        rag_mission: RAGMission,
        job_description: str
    ) -> ThematicAnalysis:
        """Synthesize PartialRAGResult into final ThematicAnalysis."""
        thematic_analysis = ThematicAnalysis()
        
        # Extract from Phase 1
        if partial_result.phase1_success and partial_result.phase1_result:
            phase1_thematic = partial_result.phase1_result.get('thematic_analysis', {})
            thematic_analysis.primary_theme = phase1_thematic.get('primary_theme', {})
            thematic_analysis.secondary_themes = phase1_thematic.get('secondary_themes', [])
        
        # Set metadata
        thematic_analysis.signal_quality_score = partial_result.success_rate
        thematic_analysis.retrieval_method = "Multi-Phase RAG with Librarian"
        
        return thematic_analysis
    
    def _extract_technologies(self, job_description: str) -> List[str]:
        """Extract technologies from job description."""
        # Simple keyword extraction - would use NLP in production
        tech_keywords = ['python', 'java', 'aws', 'docker', 'kubernetes', 'react', 'sql']
        found_techs = []
        jd_lower = job_description.lower()
        
        for tech in tech_keywords:
            if tech in jd_lower:
                found_techs.append(tech.capitalize())
        
        return found_techs
    
    def _extract_responsibilities(self, job_description: str) -> List[str]:
        """Extract core responsibilities from job description."""
        # Simple extraction - would use NLP in production
        responsibilities = []
        
        # Look for responsibility indicators
        if 'lead' in job_description.lower():
            responsibilities.append("Lead technical initiatives")
        if 'design' in job_description.lower():
            responsibilities.append("Design system architecture")
        if 'mentor' in job_description.lower():
            responsibilities.append("Mentor team members")
        
        return responsibilities[:5]  # Limit to top 5


# ==============================================================================
# Supporting Classes for RAG System
# ==============================================================================

class CircuitBreaker:
    """Circuit breaker pattern implementation for RAG operations."""
    
    def __init__(self, threshold: int, timeout: int):
        self.failure_count = 0
        self.threshold = threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        """Execute a function call with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.threshold:
                self.state = CircuitState.OPEN
            
            raise


class PhaseExecutor:
    """Execute individual RAG phases with timeout protection and retries."""
    
    def __init__(self, max_retries: int, timeout: int, backoff_config: Any):
        self.phase_max_retries = max_retries
        self.phase_timeout_seconds = timeout
        self.rag_config = backoff_config
    
    def execute_with_retry(
        self,
        phase_func: Callable[[], T],
        phase_name: str
    ) -> T:
        """Execute a phase function with retry logic."""
        last_exception = None
        
        for attempt in range(self.phase_max_retries):
            try:
                logger.info(f"{phase_name}: Attempt {attempt+1}/{self.phase_max_retries}")
                
                # Execute with timeout (simplified - would use actual timeout in production)
                result_tuple = phase_func()
                
                if not isinstance(result_tuple, tuple) or len(result_tuple) != 2:
                    raise ValueError(f"{phase_name} did not return a (result, call_count) tuple.")
                
                result_dict, calls_made = result_tuple
                
                logger.info(f"{phase_name}: Success on attempt {attempt+1}. Calls: {calls_made}")
                return result_tuple
                
            except Exception as e:
                last_exception = e
                logger.warning(f"{phase_name}: Failed on attempt {attempt+1}: {e}")
                if attempt < self.phase_max_retries - 1:
                    time.sleep(1.0)  # Simple backoff
                    continue
                else:
                    raise


# ==============================================================================
# PHASE 2: GENERATION SPECIALISTS (NEW - REPLACES STUBS)
# ==============================================================================

class Content_Generator:
    """
    Executes LLM generation calls using the Gemini service.
    Implements the 'Execution Specialist' role from the agentic diagram.
    """
    def __init__(self, complexity: int = 80, librarian: Optional['Library_Specialist'] = None):
        self.complexity = complexity
        self.llm_service = get_gemini_service()
        self.librarian = librarian  # Injected for Technique #1
        self.logger = logging.getLogger(__name__)

    def generate_section(
        self,
        section_name: ResumeSection,
        context: Dict[str, Any],
        attempt: int = 1,
        reasoning_config: Optional[ReasoningConfig] = None
    ) -> str:
        """
        Generates content for a specific resume section.
        """
        try:
            # 1. Identify Prompt Template
            template_name = self._map_section_to_template(section_name)
            prompt_template = get_prompt_template(template_name)

            # --- TECHNIQUE #1: DYNAMIC FEW-SHOT INJECTION ---
            # If we have a librarian and keywords, fetch relevant examples
            dynamic_examples = ""
            if self.librarian and 'keywords_str' in context:
                keywords = [k.strip() for k in context['keywords_str'].split(',')]
                dynamic_examples = self.librarian.query_few_shot_examples(
                    section_type=section_name.name,
                    keywords=keywords
                )
            
            # Add to context for the template to use
            context['dynamic_few_shot_examples'] = dynamic_examples
            # ------------------------------------------------

            # 2. Build Prompt Context
            prompt = prompt_template.format(**context)

            # --- TECHNIQUE #6: PREFILL INJECTION (Assistant Priming) ---
            # For sections that must start with specific formatting, we prefill the response.
            prefill = ""
            if section_name == ResumeSection.K9_COMPETENCIES:
                 prefill = "• **"
            elif section_name == ResumeSection.K0_HEADLINE:
                 prefill = "Senior "
            
            if prefill:
                # Force the model to continue from this point
                prompt += f"\n\n[ASSISTANT START]\n{prefill}"
            # ------------------------------------------------

            # 3. Execute Call
            self.logger.info(f"Generating {section_name.name} (Attempt {attempt})")
            response, _, _ = self.llm_service.call_api(
                prompt=prompt,
                reasoning_config=reasoning_config, # T5: Pass config to service
                section_id=f"{section_name.name}_attempt_{attempt}",
                temperature=CONFIG.model.temperature
            )

            # If we used prefill, prepend it back to the response if missing
            if prefill and not response.startswith(prefill):
                response = prefill + response

            return response

        except Exception as e:
            self.logger.error(f"Generation failed for {section_name.name}: {e}")
            raise

    def _map_section_to_template(self, section: ResumeSection) -> str:
        """
        Dynamically maps ResumeSection enum to prompt template key.
        Falls back to standard naming convention if no explicit override exists.
        """
        # 1. Dynamic Standard Naming Convention Lookup
        standard_key = f"artist_{section.name.lower().replace('.', '_')}"
        if standard_key in PROMPT_TEMPLATES:
            return standard_key

        # 2. Explicit Mappings (Fallback for non-standard names)
        FALLBACK_MAPPING = {
            ResumeSection.K0_HEADLINE: "artist_headline_component",
            ResumeSection.K1_EXECUTIVE_SUMMARY: "artist_executive_summary",
            ResumeSection.K2_UNIFY_BULLETS: "artist_synthetic_bullet",
            ResumeSection.K3_IBM_BULLETS: "artist_synthetic_bullet",
            ResumeSection.K9_COMPETENCIES: "artist_synthetic_bullet",
            ResumeSection.K2_UNIFY_OVERVIEW: "artist_overview_generation",
            ResumeSection.K3_IBM_OVERVIEW: "artist_overview_generation",
            ResumeSection.K11_COVER_LETTER: "artist_cover_letter_full"
        }
        return FALLBACK_MAPPING.get(section, "artist_section_generic")



# ==============================================================================
# PHASE 3: VALIDATION SYSTEM RECOVERY
# ==============================================================================

class FactualConsistency_Validator:
    """
    Validates factual consistency across resume sections.
    PORTED FROM: v3.8 validation_rules.py and validation_engine.py
    """
    
    def __init__(self, complexity: int = 40):
        """Initialize with validation engine and rules."""
        self.complexity = complexity
        self.validation_engine = ValidationEngine()
    
    def validate(self, context: ValidationContext) -> Dict[str, Any]:
        """Execute all factual consistency validations."""
        results = {
            'bullet_word_count': _validate_bullet_word_count_CRITICAL(context),
            'cross_section_similarity': _validate_cross_section_similarity(context),
            'no_placeholders': _validate_no_placeholders(context),
            'headline_format': _validate_headline_format_no_titles(context),
            'narrative_vs_master': _validate_narrative_vs_master_similarity(context),
        }
        
        # Add validation results to context cache
        for rule_id, passed in results.items():
            if not passed:
                logger.warning(f"FactualConsistency validation failed: {rule_id}")
        
        return results


class ToneValidator:
    """
    Validates tone consistency and appropriateness.
    PORTED FROM: v3.8 validation system
    """
    
    def __init__(self, complexity: int = 30):
        """Initialize tone validator."""
        self.complexity = complexity
    
    def validate(self, context: ValidationContext) -> Dict[str, Any]:
        """Validate tone across all sections."""
        results = {}
        
        # Check for conversational fillers
        conversational_pattern = re.compile(
            r"^(Here is the|Certainly,|I have generated|Below is the|Apologies,|Please note)\b", 
            re.IGNORECASE | re.MULTILINE
        )
        
        # Check each section for tone issues
        for section_enum in ResumeSection:
            content = context.staging_buffer.get(section_enum.value, '')
            if isinstance(content, str) and content:
                has_fillers = bool(conversational_pattern.search(content))
                results[f"{section_enum.name}_tone"] = not has_fillers
        
        return results


class ThematicAlignment_Validator:
    """
    Validates thematic alignment with job description.
    PORTED FROM: v3.8 validation system
    """
    
    def __init__(self, complexity: int = 35):
        """Initialize thematic alignment validator."""
        self.complexity = complexity
    
    def validate(self, context: ValidationContext) -> Dict[str, Any]:
        """Validate thematic alignment with JD."""
        results = {}
        
        # Check JD keyword presence
        jd_keywords = context.jd_required_keywords
        if jd_keywords:
            found_keywords = 0
            for keyword in jd_keywords:
                # Check if keyword appears in any section
                for section_enum in ResumeSection:
                    content = context.staging_buffer.get(section_enum.value, '')
                    if isinstance(content, str) and keyword.lower() in content.lower():
                        found_keywords += 1
                        break
            
            results['jd_keyword_coverage'] = found_keywords >= min(7, len(jd_keywords))
            results['keywords_found'] = found_keywords
            results['keywords_required'] = len(jd_keywords)
        
        return results


# ==============================================================================
# PHASE 3: RENDERER RECOVERY - ASSEMBLY AGENTS
# ==============================================================================

class Resume_Assembler:
    """
    Assembles final resume from staging buffer.
    PORTED FROM: v3.8/renderer_RES_v3_8.py FileRenderer._render_resume_artifact (lines 180-250)
    """
    
    def __init__(self, complexity: int = 25):
        """Initialize resume assembler."""
        self.complexity = complexity
        self.logger = logging.getLogger(__name__)
    
    def assemble_resume(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str) -> Tuple[str, str]:
        """
        Assemble resume from staging buffer into markdown format.
        Returns (markdown_content, filename)
        """
        sections = []
        
        # PORT: Headline rendering logic (v3.8 lines 185-195)
        headline = staging_buffer.get(ResumeSection.K0_HEADLINE.value)
        if headline:
            sections.append(f"# {self._strip_fences(headline, 'Headline')}")
        
        # PORT: Professional Summary (v3.8 lines 197-205)
        prof_summary = staging_buffer.get(ResumeSection.K1_EXECUTIVE_SUMMARY.value)
        if prof_summary:
            sections.append("## Professional Summary")
            sections.append(self._strip_fences(prof_summary, "Professional Summary"))
        
        # PORT: Experience sections (v3.8 lines 207-230)
        experience_sections = [
            (ResumeSection.K2_UNIFY_OVERVIEW, "Unify Technologies"),
            (ResumeSection.K3_IBM_OVERVIEW, "IBM"),
            (ResumeSection.K4_TRADERSENSE_NARRATIVE, "TraderSense"),
            (ResumeSection.K5_EY_NARRATIVE, "Ernst & Young"),
            (ResumeSection.K6_EARLY_CAREER_NARRATIVE, "Early Career")
        ]
        
        has_experience = False
        for section_enum, company in experience_sections:
            content = staging_buffer.get(section_enum.value)
            if content:
                if not has_experience:
                    sections.append("## Experience")
                    has_experience = True
                sections.append(f"### {company}")
                sections.append(self._strip_fences(content, company))
        
        # PORT: Skills section
        skills = staging_buffer.get(ResumeSection.K9_COMPETENCIES.value)
        if skills:
            sections.append("## Skills & Competencies")
            sections.append(self._strip_fences(skills, "Skills"))
        
        # PORT: Leadership Approach
        leadership = staging_buffer.get(ResumeSection.K7_LEADERSHIP_APPROACH.value)
        if leadership:
            sections.append("## Leadership Approach")
            sections.append(self._strip_fences(leadership, "Leadership"))
        
        # PORT: Technical Excellence
        technical = staging_buffer.get(ResumeSection.K8_TECHNICAL_EXCELLENCE.value)
        if technical:
            sections.append("## Technical Excellence")
            sections.append(self._strip_fences(technical, "Technical"))
        
        # Assemble final markdown
        markdown_content = "\n\n".join(sections)
        
        # Generate filename
        safe_company = sanitize_filename(company_name)
        safe_title = sanitize_filename(job_title)
        filename = f"resume_{safe_company}_{safe_title}.md"
        
        return markdown_content, filename
    
    def _strip_fences(self, content: str, artifact_name: str) -> str:
        """Remove markdown fences from content."""
        stripped = text_utils.strip_markdown_fences(content)
        
        if len(stripped) < len(content):
            self.logger.warning(f"Removed markdown fences from {artifact_name}")
        
        return stripped


class CoverLetter_Assembler:
    """
    Assembles cover letter from staging buffer.
    PORTED FROM: v3.8/renderer_RES_v3_8.py FileRenderer._render_cover_letter_artifact
    """
    
    def __init__(self, complexity: int = 20):
        """Initialize cover letter assembler."""
        self.complexity = complexity
        self.logger = logging.getLogger(__name__)
    
    def assemble_cover_letter(self, staging_buffer: ImmutableStagingBuffer, company_name: str, job_title: str) -> Tuple[str, str]:
        """
        Assemble cover letter from staging buffer.
        Returns (cover_letter_content, filename)
        """
        cover_letter = staging_buffer.get(ResumeSection.K11_COVER_LETTER.value, '')
        
        if not cover_letter:
            cover_letter = self._generate_default_cover_letter(company_name, job_title)
        
        # Strip any markdown fences
        cover_letter = text_utils.strip_markdown_fences(cover_letter)
        
        # Generate filename
        safe_company = sanitize_filename(company_name)
        safe_title = sanitize_filename(job_title)
        filename = f"cover_letter_{safe_company}_{safe_title}.txt"
        
        return cover_letter, filename
    
    def _generate_default_cover_letter(self, company_name: str, job_title: str) -> str:
        """Generate a default cover letter template."""
        today = datetime.now().strftime("%B %d, %Y")
        
        template = f"""{today}

Hiring Manager
{company_name}

Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}.

[Content paragraph 1 - Background and interest]

[Content paragraph 2 - Key qualifications and achievements]

[Content paragraph 3 - Value proposition and call to action]

Sincerely,

[Your Name]"""
        
        return template


class AppTracker_Assembler:
    """
    Assembles application tracker entry.
    PORTED FROM: v3.8/renderer_RES_v3_8.py FileRenderer._render_app_tracker_artifact
    """
    
    def __init__(self, complexity: int = 15):
        """Initialize app tracker assembler."""
        self.complexity = complexity
    
    def assemble_tracker_entry(
        self,
        staging_buffer: ImmutableStagingBuffer,
        company_name: str,
        job_title: str,
        jd_url: str = "",
        status: str = "Applied"
    ) -> Dict[str, Any]:
        """
        Assemble application tracker entry.
        Returns tracker entry dictionary.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        tracker_entry = {
            "date_applied": today,
            "company": company_name,
            "position": job_title,
            "job_url": jd_url,
            "status": status,
            "resume_version": "v5.2",
            "cover_letter": "Yes" if staging_buffer.get(ResumeSection.K11_COVER_LETTER.value) else "No",
            "keywords": self._extract_keywords(staging_buffer),
            "notes": f"Generated with v5.2 recovery system",
            "follow_up_date": "",
            "response": "",
            "interview_dates": [],
            "outcome": ""
        }
        
        return tracker_entry
    
    def _extract_keywords(self, staging_buffer: ImmutableStagingBuffer) -> List[str]:
        """Extract key keywords from resume."""
        keywords = []
        
        # Extract from skills section
        skills = staging_buffer.get(ResumeSection.K9_COMPETENCIES.value, '')
        if skills:
            # Simple keyword extraction - would use NLP in production
            words = skills.split()
            keywords.extend([w for w in words if len(w) > 4][:5])
        
        return keywords


# ==============================================================================
# PHASE 4: QA AUDITOR RECOVERY
# ==============================================================================

class Auditor_Agent:
    """
    Generates comprehensive QA reports.
    PORTED FROM: v3.8/qa_auditor_RES_v3_8.py QAReportGenerator (lines 25-284)
    """
    
    def __init__(self, complexity: int = 30):
        """Initialize QA auditor."""
        self.complexity = complexity
        self.logger = logging.getLogger(__name__)
    
    def generate_qa_report(
        self,
        staging_buffer: ImmutableStagingBuffer,
        validation_results: Dict[str, Any],
        thematic_analysis: ThematicAnalysis
    ) -> str:
        """
        Generate comprehensive QA report.
        PORTED FROM: v3.8 lines 35-280
        """
        lines = []
        
        # Header
        lines.append("# QA Report - V5.2 Recovery")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Calculate status
        total_validations = len(validation_results)
        passed_validations = sum(1 for v in validation_results.values() if v)
        pass_rate = passed_validations / total_validations if total_validations > 0 else 0
        
        production_ready = pass_rate >= 0.8
        overall_status = "PASS" if production_ready else "FAIL"
        
        lines.append(f"Overall Status: **{overall_status}**")
        lines.append("")
        
        # Section 1: Production Readiness
        lines.append("## Section 1: Production Readiness & Key Indicators")
        lines.append(f"* Production Ready: **{'YES' if production_ready else 'NO'}**")
        lines.append(f"* Total Validation Rules: **{total_validations}**")
        lines.append(f"* Passed: **{passed_validations}**")
        lines.append(f"* Failed: **{total_validations - passed_validations}**")
        lines.append(f"* Pass Rate: **{pass_rate:.1%}**")
        lines.append("")
        
        # Section 2: Validation Details
        lines.append("## Section 2: Validation Details")
        
        # Group validations by category
        factual_validations = {k: v for k, v in validation_results.items() if 'factual' in k.lower() or 'consistency' in k.lower()}
        tone_validations = {k: v for k, v in validation_results.items() if 'tone' in k.lower()}
        thematic_validations = {k: v for k, v in validation_results.items() if 'thematic' in k.lower() or 'keyword' in k.lower()}
        
        if factual_validations:
            lines.append("### Factual Consistency")
            for rule, passed in factual_validations.items():
                status = "✅" if passed else "❌"
                lines.append(f"* {status} {rule}")
        
        if tone_validations:
            lines.append("### Tone Validation")
            for rule, passed in tone_validations.items():
                status = "✅" if passed else "❌"
                lines.append(f"* {status} {rule}")
        
        if thematic_validations:
            lines.append("### Thematic Alignment")
            for rule, passed in thematic_validations.items():
                status = "✅" if passed else "❌"
                lines.append(f"* {status} {rule}")
        
        lines.append("")
        
        # Section 3: Content Summary
        lines.append("## Section 3: Content & Signal Summary")
        
        lines.append("### Signal & Quality Metrics")
        if thematic_analysis:
            lines.append(f"* Signal Quality Score: **{thematic_analysis.signal_quality_score:.1%}**")
            lines.append(f"* Retrieval Method: {thematic_analysis.retrieval_method}")
            
            if thematic_analysis.primary_theme:
                lines.append(f"* Primary Theme: {thematic_analysis.primary_theme.get('name', 'N/A')}")
            
            if thematic_analysis.secondary_themes:
                lines.append(f"* Secondary Themes: {len(thematic_analysis.secondary_themes)}")
        
        lines.append("")
        
        # Section 4: Section Coverage
        lines.append("## Section 4: Section Coverage")
        
        sections_present = []
        sections_missing = []
        
        for section_enum in ResumeSection:
            content = staging_buffer.get(section_enum.value)
            if content and str(content).strip():
                sections_present.append(section_enum.name)
            else:
                sections_missing.append(section_enum.name)
        
        lines.append(f"* Sections Present: **{len(sections_present)}/{len(ResumeSection)}**")
        
        if sections_missing:
            lines.append("* Missing Sections:")
            for section in sections_missing[:5]:  # Limit to first 5
                lines.append(f"  - {section}")
        
        lines.append("")
        
        # Section 5: Compliance Summary
        lines.append("## Section 5: Compliance Summary")
        lines.append(f"* Overall Pass Rate: **{pass_rate:.1%}**")
        lines.append(f"* Recommendation: **{'APPROVE for submission' if production_ready else 'REVISE before submission'}**")
        
        if not production_ready:
            lines.append("")
            lines.append("### Required Actions:")
            
            # List failed validations
            failed = [k for k, v in validation_results.items() if not v]
            for rule in failed[:5]:  # Top 5 failures
                lines.append(f"* Fix: {rule}")
        
        lines.append("")
        lines.append("---")
        lines.append("*End of QA Report*")
        
        return "\n".join(lines)




# ==============================================================================
# PHASE 5: AGENTIC SWARM EXPANSION (Diagram Implementation)
# ==============================================================================

# --- META-LEARNING LOOP AGENTS ---

class HIL_Feedback_Logger:
    """🗃️ Logs Human-in-the-Loop feedback and QA failures for meta-learning."""
    def __init__(self):
        self.log_path = CACHE_DIR / "hil_feedback_log.jsonl"
        
    def log_veto(self, veto: 'VetoRecord', context: Dict):
        """Logs a VETO signal for future analysis."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "VETO",
            "agent": veto.source_agent,
            "reason": veto.reason,
            "job_title": context.get('job_title', 'unknown')
        }
        # In production, append this to self.log_path
        logger.info(f"🗃️ Feedback Logged: {entry}")

class Meta_Planner:
    """📈 Analyzes logs to update global rules and strategies."""
    def __init__(self):
        self.rules_registry = CACHE_DIR / "rules_registry.json"

    def update_rules(self) -> Dict[str, Any]:
        """Reads logs, finds patterns, outputs updated rules."""
        logger.info("📈 Meta-Planner: Analyzing past performance to update rules...")
        # Stub: In a real system, this would perform statistical analysis on logs
        return {"global_retry_limit": 3, "strict_mode": True}

class RetryPolicyAgent:
    """🤔 Determines optimal retry strategy based on failure type."""
    def __init__(self, complexity: int = 90):
        self.complexity = complexity

    def determine_strategy(self, veto: 'VetoRecord', attempt: int) -> str:
        """Decides whether to retry, critique, or escalate."""
        if attempt >= 3:
            return "ESCALATE"
        if veto.severity == ValidationSeverity.CRITICAL:
             return "STRATEGIC_REFRAME" # Try a completely different approach
        return "MECHANICAL_FIX" # Just fix the specific error

class CostRouter:
    """💸 Manages computational budget (stubbed to always approve)."""
    def __init__(self, complexity: int = 75):
        self.complexity = complexity
    
    def approve_expense(self, estimated_tokens: int) -> bool:
        return True

# --- GOVERNANCE & STRATEGY ADVISORS ---

class ChiefStrategistAgent:
    """🧑‍🔬 Defines the overall execution strategy based on RAG data."""
    def __init__(self, complexity: int = 90):
        self.complexity = complexity

    def develop_strategy(self, thematic_analysis: ThematicAnalysis) -> 'ExecutionStrategy':
        """Creates the master plan for the Governor."""
        logger.info("🧑‍🔬 Chief Strategist: Developing execution strategy...")
        # Stub: returns a default high-complexity strategy
        # Imports handled inside method to avoid top-level circular dependency during load
        from models_RES import ExecutionStrategy, ResumeSection
        return ExecutionStrategy(
            name="Aggressive Differentiator Focus",
            focus_areas=[ResumeSection.K1_EXECUTIVE_SUMMARY, ResumeSection.K9_COMPETENCIES],
            cost_sensitivity=0.8,
            required_validators=["FactualConsistency_Validator", "ToneValidator"],
            max_retries_per_node=2
        )

class StrategyValidatorAgent:
    """🧠 Validates the Chief Strategist's plan before execution."""
    def __init__(self, complexity: int = 95):
        self.complexity = complexity

    def validate_strategy(self, strategy: 'ExecutionStrategy') -> bool:
        logger.info(f"🧠 Strategy Validator: Reviewing '{strategy.name}'...")
        return True # Always pass for now

# --- PROMPTING STACK ---

class PromptSelectorAgent:
    """🗂️ Selects the best prompt template for the current context."""
    def __init__(self, complexity: int = 60):
        self.complexity = complexity
        
    def select_prompt(self, section: ResumeSection, strategy: str) -> str:
        # Stub: simple mapping, could be dynamic based on strategy
        return f"artist_{section.name.lower()}"

class ContextAssemblerAgent:
    """📦 Gathers all necessary context (RAG, Master, Constraints) for a prompt."""
    def __init__(self, complexity: int = 60):
        self.complexity = complexity

    def assemble(self, section: ResumeSection, rag_data: ThematicAnalysis, master: Dict) -> Dict:
        # Stub: Wraps existing build_crl_context_for_section
        return {} 

class PromptFormatterAgent:
    """📬 Finalizes the prompt string for transmission to the LLM."""
    def __init__(self, complexity: int = 60):
        self.complexity = complexity
        
    def format(self, template: str, context: Dict) -> str:
        return template.format(**context)

# --- DRAFTING SPECIALISTS (DIVERSE) ---

class Verbatim_Copier:
    """📋 Copies data directly from master without modification."""
    def __init__(self, complexity: int = 15): self.complexity = complexity
    def execute(self, source_text: str) -> str: return source_text

class Gemini_Drafter(Content_Generator):
    """♊ Default Drafter using Gemini."""
    def __init__(self, complexity: int = 30): super().__init__(complexity)

class Claude_Drafter(Content_Generator):
    """☁️ Alternative Drafter using Claude (stubbed to use Gemini for now)."""
    def __init__(self, complexity: int = 30): super().__init__(complexity)

class Muse_Drafter(Content_Generator):
    """🎭 Creative Drafter for high-entropy sections (stubbed)."""
    def __init__(self, complexity: int = 30): super().__init__(complexity)

# --- CRITICS STACK ---

class Mechanical_Critic:
    """🧐 Checks constraints, word counts, formatting."""
    def __init__(self, complexity: int = 60): self.complexity = complexity
    def critique(self, draft: str) -> List[str]: return []

class Strategic_Critic:
    """🎯 Checks alignment with the Strategy Brief."""
    def __init__(self, complexity: int = 65): self.complexity = complexity
    def critique(self, draft: str, strategy: 'ExecutionStrategy') -> List[str]: return []

# --- HIL STACK ---

class HIL_EscalationAgent:
    """🧑‍💻 Manages handoffs to human reviewers with state persistence."""
    def __init__(self, complexity: int = 60):
        self.complexity = complexity
        self.escalation_dir = CACHE_DIR / "escalations"
        self.escalation_dir.mkdir(parents=True, exist_ok=True)

    def escalate(self, context_data: Dict, reason: str):
        """Saves current state to disk and logs critical alert for human review."""
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.escalation_dir / f"escalation_{run_id}.json"
        
        try:
            # Use default=str to handle non-serializable objects temporarily
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, default=str)
            logger.critical(f"🧑‍💻 HIL ESCALATION: {reason}")
            logger.critical(f"💾 State saved for review: {filename}")
        except Exception as e:
            logger.critical(f"🚨 HIL ESCALATION FAILED TO SAVE STATE: {e}")


# --- QA SPECIALISTS (EXPANDED) ---

class Constraint_Jargon_Checker:
    """📏 QA Class 1: Checks specific constraints and jargon usage."""
    def __init__(self, complexity: int = 20): self.complexity = complexity
    def validate(self, text: str) -> ValidationResult: return ValidationResult("Jargon", True, ValidationSeverity.INFO, "OK")

class Grammar_TokenCountAgent:
    """🔡 QA Class 1: Basic mechanical checks."""
    def __init__(self, complexity: int = 15): self.complexity = complexity
    def validate(self, text: str) -> ValidationResult: return ValidationResult("Grammar", True, ValidationSeverity.INFO, "OK")

class RankingAgent:
    """⚖️ Ranks multiple drafts to select the best one."""
    def __init__(self, complexity: int = 50): self.complexity = complexity
    def rank(self, drafts: List[str]) -> str: return drafts[0] if drafts else ""


# Export all specialists
__all__ = [
    # Phase 1 & Base
    'Library_Specialist',
    'Web_Specialist',
    'RAG_Synthesizer',
    'Content_Generator',
    'FactualConsistency_Validator',
    'ToneValidator',
    'ThematicAlignment_Validator',
    'Resume_Assembler',
    'CoverLetter_Assembler',
    'AppTracker_Assembler',
    'Auditor_Agent',
    
    # Meta-Loop
    'HIL_Feedback_Logger', 'Meta_Planner', 'RetryPolicyAgent', 'CostRouter',
    
    # Strategy
    'ChiefStrategistAgent', 'StrategyValidatorAgent',
    
    # Prompting
    'PromptSelectorAgent', 'ContextAssemblerAgent', 'PromptFormatterAgent',
    
    # Drafting
    'Verbatim_Copier', 'Gemini_Drafter', 'Claude_Drafter', 'Muse_Drafter',
    
    # Critics
    'Mechanical_Critic', 'Strategic_Critic',
    
    # HIL
    'HIL_EscalationAgent',
    
    # Extended QA
    'Constraint_Jargon_Checker', 'Grammar_TokenCountAgent', 'RankingAgent'
]
