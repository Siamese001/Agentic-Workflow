# File: rag_RES_v3_8.py
# Version: 3.8.0
# RAG (Retrieval-Augmented Generation) module for Resume Workflow
# Contains classes for web search, circuit breakers, phase execution,
# Librarian persistent memory agent, and job description analysis (HOP-0).
#
# V3_8 INTEGRATION:
# - EnhancedJobDescriptionAnalyzer: Used in HOP-0 (initial state load)
# - LibrarianAgent: Called by workflow for deep RAG with persistent memory
# - RAGMission: Core data structure for thematic analysis
# - WebSearchTool: Performs multi-phase RAG searches
# - CircuitBreaker/PhaseExecutor: Reliability patterns for RAG operations

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
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

# Third-party imports
try:
    import google.generativeai as genai
    from gemini_service import GeminiService
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    GeminiService = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None
    cosine_similarity = None

# ChromaDB for Librarian Agent (NEW - Phase 3)
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    logging.warning("ChromaDB not available - Librarian Agent will be disabled")

# Local module imports
# --- REFACTOR: Import global CONFIG and constants ---
from config_RES_v3_8 import (
    CONFIG, CACHE_DIR,
    DEFAULT_MAX_RETRIES, DEFAULT_HOP_TIMEOUT # <-- IMPORTED CONSTANTS
)
# --- END REFACTOR ---

from models_RES import (
    CircuitState, RAGState, RAGEvidence, RAGCritique,
    PartialRAGResult, RAGTelemetry, CompetitiveIntelligence,
    MasterResumeIndex, RAGMission, ThematicAnalysis, HopStatus,
    RetrievalSource, SkillRequirement, SkillCluster,
    HopExecutionError, CircuitBreakerOpenError, PhaseTimeoutError,
    CompetitiveAnalysisConfig # <-- IMPORTED
)
from utils_RES_v3_8 import TelemetryLogger

# Import prompts module
import prompts_RES_v3_8 as prompts_RES

# Type variable for phase execution
T = TypeVar('T')
logger = logging.getLogger(__name__)

# ==============================================================================
# LIBRARIAN AGENT (NEW - Phase 3)
# ==============================================================================

class LibrarianAgent:
    """
    Persistent memory agent using ChromaDB for cross-job intelligence.
    
    The Librarian maintains a vector database of:
    - Past RAGMission extractions
    - Successful positioning strategies
    - Competitor intelligence patterns
    - Industry-specific insights
    
    This enables:
    - Learning from past successes
    - Consistent high-signal extraction
    - Progressive refinement of RAG quality
    """
    
    def __init__(self, storage_path: str = str(CACHE_DIR / "librarian_db")):
        """
        Initialize Librarian Agent with persistent storage.
        
        Args:
            storage_path: Directory for ChromaDB persistence
        """
        self.storage_path = storage_path
        self.enabled = CHROMADB_AVAILABLE
        self.client = None
        self.collection = None
        
        if not self.enabled:
            logger.warning("Librarian Agent disabled - ChromaDB not available")
            return
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=storage_path,
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
            
            logger.info(f"Librarian Agent initialized with {self.collection.count()} memories at {storage_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Librarian Agent: {e}")
            self.enabled = False
    
    def store_mission_intelligence(
        self,
        rag_mission: RAGMission,
        thematic_analysis: ThematicAnalysis,
        company_name: str,
        job_title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Stores successful RAGMission and analysis for future reference.
        
        Args:
            rag_mission: Extracted RAGMission
            thematic_analysis: Generated ThematicAnalysis
            company_name: Target company
            job_title: Target role title
            metadata: Additional context
        """
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
        """
        Queries for similar past missions to inform current extraction.
        
        Args:
            query: Search query (e.g., job title or theme)
            company_name: Optional company filter
            n_results: Number of results to return
            
        Returns:
            List of similar mission contexts
        """
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
        """
        Gets relevant Librarian context for a specific RAG phase.
        
        Args:
            phase_name: Name of RAG phase (phase1, phase2, etc.)
            rag_mission: Current RAGMission
            company_name: Target company
            
        Returns:
            Formatted context string or None
        """
        if not self.enabled:
            return None
        
        try:
            # Build query based on phase
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
        """Formats RAGMission and analysis into searchable document."""
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


# ==============================================================================
# CIRCUIT BREAKER
# ==============================================================================

class CircuitBreaker:
    """
    Circuit breaker pattern implementation for RAG operations.
    (Extracted from resume_workflow_v16_20.py)
    """
    # --- REFACTOR: Removed config argument ---
    def __init__(self, threshold: int, timeout: int):
        self.failure_count = 0
        self.threshold = threshold
        self.timeout = timeout
        # --- END REFACTOR ---
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    # --- END REFACTOR ---

    def call(self, func, *args, **kwargs):
        """Executes a function call with circuit breaker protection."""
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
            
            # Re-raise the original exception
            raise
        
# ==============================================================================
# PHASE EXECUTOR
# ==============================================================================

class PhaseExecutor:
    """
    Executes individual RAG phases with timeout protection and retries.
    (Extracted from resume_workflow_v16_20.py)
    """
    # --- REFACTOR: Removed config argument ---
    def __init__(self, max_retries: int, timeout: int, backoff_config: Any):
        # --- REFACTOR: Use global config constants ---
        self.phase_max_retries = max_retries
        self.phase_timeout_seconds = timeout
        self.rag_config = backoff_config

    def execute_with_retry(
        self,
        phase_func: Callable[[], T],
        phase_name: str
    ) -> T:
        """Executes a phase function with retry logic."""
        last_exception = None

        for attempt in range(self.phase_max_retries):
            try:
                logger.info(
                    f"{phase_name}: Attempt {attempt+1}/{self.phase_max_retries}"
                )

                # Execute with timeout
                result_tuple = self._execute_with_timeout(
                    phase_func,
                    self.phase_timeout_seconds,
                    phase_name
                )

                if not isinstance(result_tuple, tuple) or len(result_tuple) != 2:
                     logger.error(f"{phase_name}: Phase function did not return expected (result, call_count) tuple. Got: {type(result_tuple)}")
                     raise ValueError(f"{phase_name} did not return a (result, call_count) tuple.")

                result_dict, calls_made = result_tuple

                if self._validate_phase_result(result_dict, phase_name):
                    logger.info(f"{phase_name}: Success on attempt {attempt+1}. Calls: {calls_made}")
                    return result_tuple # Return (result, call_count) tuple
                else:
                    logger.warning(f"{phase_name}: Invalid result structure on attempt {attempt+1}")
                    if attempt < self.phase_max_retries - 1:
                        continue
                    else:
                        raise ValueError(f"{phase_name}: All attempts returned invalid result structure.")

            except PhaseTimeoutError as e:
                last_exception = e
                logger.warning(f"{phase_name}: Timeout on attempt {attempt+1}")
                if attempt == self.phase_max_retries - 1:
                    break
                time.sleep(1.0)  # Default backoff
                continue

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"{phase_name}: Failed on attempt {attempt+1}: "
                    f"{type(e).__name__}: {e}", exc_info=False
                )
                if attempt == self.phase_max_retries - 1:
                    break
                try:
                    backoff = self._calculate_backoff(attempt)
                    logger.info(f"Backing off {backoff:.2f}s before retry...")
                    time.sleep(backoff)
                except AttributeError:
                    logger.warning("Backoff calculation method not found, using default sleep.")
                    time.sleep(2 * (attempt + 1))
                continue

        logger.error(f"{phase_name}: All retries exhausted or loop broken.")
        if last_exception:
            raise last_exception
        raise RuntimeError(f"{phase_name}: Failed after all retries without a specific exception being raised.")

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculates exponential backoff with jitter."""
        # --- BUG 3 FIX: Read from self.rag_config, not self.config ---
        initial = getattr(self.rag_config, 'api_initial_backoff_seconds', 2.0)
        multiplier = getattr(self.rag_config, 'api_backoff_multiplier', 2.0)
        max_backoff = getattr(self.rag_config, 'api_max_backoff_seconds', 64.0)
        jitter = getattr(self.rag_config, 'api_backoff_jitter', 0.1)
        # --- END FIX ---

        base_delay = min(initial * (multiplier ** attempt), max_backoff)
        jitter_range = base_delay * jitter
        random_jitter = random.uniform(-jitter_range, jitter_range)
        return max(0.1, base_delay + random_jitter)
    
    def _execute_with_timeout(
        self, 
        func: Callable[[], T], 
        timeout: int,
        name: str
    ) -> T:
        """Executes a function with a POSIX signal-based timeout."""
        if not hasattr(signal, 'SIGALRM'):
            logger.warning(f"{name}: SIGALRM not available, executing without timeout")
            return func()

        def timeout_handler(signum, frame):
            raise PhaseTimeoutError(f"{name} exceeded {timeout}s timeout")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        try:
            result = func()
            signal.alarm(0)
            return result
        except PhaseTimeoutError:
            raise
        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)

    def _validate_phase_result(self, result: Dict[str, Any], phase_name: str) -> bool:
        """Validates that a phase result has the expected structure."""
        if not isinstance(result, dict):
            logger.warning(f"{phase_name}: Result is not a dictionary")
            return False

        if not result:
            logger.warning(f"{phase_name}: Result is empty")
            return False

        # Phase-specific validation
        if "phase1" in phase_name.lower() or "thematic" in phase_name.lower():
            if 'thematic_analysis' not in result:
                logger.warning(f"{phase_name}: Missing 'thematic_analysis'")
                return False

        return True

# ==============================================================================
# WEB SEARCH TOOL
# ==============================================================================

class WebSearchTool:
    """
    Web search tool using Gemini with Google Search integration.
    (Extracted and enhanced from resume_workflow_v16_20.py)
    """
    # --- REFACTOR: Removed config argument ---
    def __init__(self):
        # --- REFACTOR: Use global CONFIG object ---
        self.config = CONFIG.rag
        self.enabled = GEMINI_AVAILABLE
        # Hardcoded defaults for missing config attributes
        self.temperature = 0.7
        self.max_tokens = 8192
        
        if not GEMINI_AVAILABLE:
            logger.warning("WebSearchTool disabled - Gemini not available")
            return
        
        try:
            self.gemini_service = GeminiService(default_model=self.config.model)
            logger.info(f"WebSearchTool initialized with GeminiService using model: {self.config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize WebSearchTool: {e}")
            self.enabled = False
    # --- END REFACTOR ---

    def search_and_analyze(
        self,
        prompt: str,
        phase_name: str = "unknown"
    ) -> Tuple[Dict[str, Any], int]:
        """
        Execute search and analysis using Gemini with Google Search.
        
        Returns:
            Tuple of (result_dict, api_calls_made)
        """
        if not self.enabled:
            logger.error("WebSearchTool is disabled")
            return {}, 0

        try:
            logger.info(f"{phase_name}: Executing search_and_analyze")
            
            # --- FIX: Call gemini_service with correct signature ---
            parsed_json, api_calls, _ = self.gemini_service.call_api_with_json_response(
                prompt=prompt,
                section_id=phase_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            # --- END FIX ---

            logger.info(f"{phase_name}: Successfully parsed JSON response")
            return parsed_json, api_calls

        except Exception as e:
            logger.error(f"{phase_name}: Search failed: {type(e).__name__}: {e}", exc_info=True)
            raise



class EnhancedJobDescriptionAnalyzer:
    """
    Main orchestrator for HOP-0 RAG operations.
    Integrates Librarian Agent for persistent learning.
    (Enhanced from resume_workflow_v16_20.py)
    """
    
    # --- REFACTOR: Removed config arguments ---
    def __init__(
        self,
        run_path: str,
        run_id: str
    ):
        # --- REFACTOR: Use global CONFIG object ---
        self.app_config = CONFIG
        # --- END REFACTOR ---
        self.run_path = run_path
        self.run_id = run_id
        
        # --- REFACTOR: Initialize components without passing configs ---
        self.web_search = WebSearchTool()
        self.circuit_breaker = CircuitBreaker(
            threshold=CONFIG.rag.circuit_breaker_threshold,
            timeout=CONFIG.rag.circuit_breaker_timeout
        )
        self.phase_executor = PhaseExecutor(
            max_retries=DEFAULT_MAX_RETRIES,
            timeout=DEFAULT_HOP_TIMEOUT,
            backoff_config=CONFIG.rag
        )
        # --- END REFACTOR ---
        
        self.telemetry = TelemetryLogger(log_path=str(CACHE_DIR / "rag_telemetry.jsonl"))
        
        # Initialize Librarian Agent (NEW - Phase 3)
        self.librarian = LibrarianAgent(
            storage_path=os.path.join(self.run_path, "librarian_db")
        )
        
        logger.info("EnhancedJobDescriptionAnalyzer initialized")
    
    def analyze_job_description(
        self,
        job_description: str,
        company_name: str,
        job_title: str, # <-- This argument is now correct
        master_resume_index: MasterResumeIndex,
        comp_config: CompetitiveAnalysisConfig
    ) -> ThematicAnalysis:
        """
        Main entry point for HOP-0: Multi-phase RAG analysis with Librarian integration.
        
        COST-OPTIMIZED: Checks cache for similar missions before running expensive RAG.
        
        Args:
            job_description: Raw job description text
            company_name: Target company name
            job_title: Target job title
            master_resume_index: Indexed master resume content
            comp_config: Competitive analysis configuration
            
        Returns:
            ThematicAnalysis with high-signal extraction
        """
        logger.info("=" * 80)
        logger.info("HOP-0: Starting Enhanced Job Description Analysis")
        logger.info("=" * 80)
        
        start_time = time.time()
        telemetry = RAGTelemetry()
        
        try:
            # Step 1: Extract high-signal RAGMission with Librarian context
            logger.info("Step 1: Extracting RAGMission with Librarian support")
            rag_mission = self._extract_rag_mission_with_librarian(
                job_description, company_name, job_title
            )
            
            # Step 1.5: COST-OPTIMIZED: Check cache for similar missions
            logger.info("Step 1.5: Checking cache for similar missions...")
            cached_analysis = self._check_cache_for_similar_mission(
                rag_mission, company_name, job_title
            )
            
            if cached_analysis:
                logger.info("=" * 80)
                logger.info("✓ CACHE HIT: Using cached ThematicAnalysis (saved ~4-5 RAG calls)")
                logger.info("=" * 80)
                
                telemetry.total_duration_seconds = time.time() - start_time
                telemetry.full_success = True
                telemetry.partial_success = True
                telemetry.success_rate = 1.0
                # --- FIX: (Amnesiac Auditor) Removed redundant log call ---
                
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
            telemetry.full_success = partial_result.full_success
            telemetry.partial_success = partial_result.any_success
            telemetry.success_rate = partial_result.success_rate
            
            # Log the final telemetry for the RAG hop
            self.telemetry.log(telemetry)
            
            logger.info("=" * 80)
            logger.info(f"HOP-0 Complete: Success Rate {partial_result.success_rate:.0%} "
                       f"in {telemetry.total_duration_seconds:.1f}s")
            logger.info("=" * 80)
            
            return thematic_analysis
            
        except Exception as e:
            logger.error(f"HOP-0 failed: {e}", exc_info=True)
            telemetry.total_duration_seconds = time.time() - start_time
            telemetry.errors.append(str(e))
            self.telemetry.log(telemetry)
            raise


    def _check_cache_for_similar_mission(
        self,
        current_mission: RAGMission,
        company_name: str,
        job_title: str,
        similarity_threshold: float = 0.85
    ) -> Optional[ThematicAnalysis]:
        """
        COST-OPTIMIZED: Check Librarian cache for similar missions.
        
        If a high-quality cached ThematicAnalysis is found for a similar role,
        return it directly to skip expensive RAG phases (saves ~4-5 LLM calls).
        
        Args:
            current_mission: The RAGMission just extracted
            company_name: Target company
            job_title: Target job title
            similarity_threshold: Minimum similarity score (0-1) to use cache
            
        Returns:
            Cached ThematicAnalysis if high-quality match found, else None
        """
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
                logger.info("No similar missions found in cache")
                return None
            
            # Check top result for high similarity
            for mission_result in similar_missions:
                distance = mission_result.get('distance', 1.0)
                similarity = 1.0 - distance  # Convert distance to similarity
                
                metadata = mission_result.get('metadata', {})
                cached_company = metadata.get('company_name', '')
                cached_title = metadata.get('job_title', '')
                
                logger.info(
                    f"  Found similar mission: {cached_company} - {cached_title} "
                    f"(similarity: {similarity:.2f})"
                )
                
                # High-quality match criteria:
                # 1. Same company
                # 2. High semantic similarity
                # 3. Similar role title (basic check)
                if (cached_company == company_name and 
                    similarity >= similarity_threshold and
                    self._titles_are_similar(cached_title, job_title)):
                    
                    logger.info(f"  ✓ High-quality cache match found (similarity: {similarity:.2f})")
                    
                    # Extract cached ThematicAnalysis from document
                    cached_analysis = self._extract_thematic_analysis_from_cache(
                        mission_result['content']
                    )
                    
                    if cached_analysis:
                        # Update retrieval metadata to indicate cache hit
                        cached_analysis.retrieval_method = "CACHED_FROM_LIBRARIAN"
                        cached_analysis.signal_quality_score = similarity
                        return cached_analysis
            
            logger.info("No high-quality cache match found")
            return None
            
        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return None
    
    def _titles_are_similar(self, title1: str, title2: str) -> bool:
        """Check if two job titles are similar (basic string matching)."""
        t1_lower = title1.lower()
        t2_lower = title2.lower()
        
        # Same title
        if t1_lower == t2_lower:
            return True
        
        # Key words match (e.g., "Senior Data Scientist" vs "Data Scientist")
        t1_words = set(t1_lower.split())
        t2_words = set(t2_lower.split())
        
        # Remove common words
        common_words = {'senior', 'junior', 'lead', 'principal', 'staff', 'the', 'a', 'an'}
        t1_key = t1_words - common_words
        t2_key = t2_words - common_words
        
        # At least 50% overlap in key words
        if t1_key and t2_key:
            overlap = len(t1_key & t2_key) / min(len(t1_key), len(t2_key))
            return overlap >= 0.5
        
        return False
    
    def _extract_thematic_analysis_from_cache(
        self,
        cached_document: str
    ) -> Optional[ThematicAnalysis]:
        """
        Extract ThematicAnalysis from a cached Librarian document.
        
        The document format is created by _format_mission_document.
        We need to parse it back into a ThematicAnalysis object.
        """
        try:
            # The cached document contains structured information
            # We'll reconstruct a ThematicAnalysis from it
            
            # For simplicity, we'll return a basic ThematicAnalysis
            # In production, you'd want to store/retrieve the full serialized object
            
            # Parse key sections from the document
            lines = cached_document.split('\n')
            
            primary_theme = {}
            secondary_themes = []
            
            for i, line in enumerate(lines):
                if 'Primary Theme:' in line:
                    # Check if theme name is on the same line or next line
                    theme_name_match = re.search(r'Primary Theme:\s*(.*)', line)
                    if theme_name_match and theme_name_match.group(1).strip():
                        theme_name = theme_name_match.group(1).strip()
                    elif i + 1 < len(lines):
                         theme_name = lines[i + 1].strip() # Assume it's on the next line
                    else:
                        theme_name = "N/A"
                    primary_theme = {'name': theme_name, 'keywords': []}

                elif 'Secondary Themes:' in line:
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].startswith('**') and not ':' in lines[j]:
                        secondary_themes.append({'name': lines[j].strip().lstrip('- '), 'keywords': []})
                        j += 1
            
            # Create basic ThematicAnalysis
            analysis = ThematicAnalysis(
                primary_theme=primary_theme,
                secondary_themes=secondary_themes,
                role_classification={'type': 'cached', 'confidence': 0.9},
                positioning_directives={'strategy': 'cached'},
                authenticity_patterns={},
                competitive_intelligence=None,
                signal_quality_score=0.85,
                retrieval_method="CACHED",
                retrieval_sources=[]
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to extract ThematicAnalysis from cache: {e}")
            return None

    def _extract_rag_mission_with_librarian(
        self,
        job_description: str,
        company_name: str,
        job_title: str
    ) -> RAGMission:
        """
        Extracts high-signal RAGMission with Librarian context.
        ENHANCED: Now extracts strategic_priorities, competitors, differentiators, etc.
        """
        logger.info("Extracting RAGMission with Librarian support")
        
        # Get Librarian context from similar missions
        librarian_context = None
        similar_missions = self.librarian.query_similar_missions(
            query=f"{company_name} {job_title}",
            n_results=2
        )
        
        if similar_missions:
            context_parts = ["**Similar Past Missions:**"]
            for mission in similar_missions:
                context_parts.append(f"- {mission['content'][:200]}...")
            librarian_context = "\n".join(context_parts)
        
        # Build enhanced extraction prompt
        prompt = prompts_RES.build_librarian_mission_extraction_prompt(
            job_description=job_description,
            company_name=company_name,
            job_title=job_title
        )
        
        if librarian_context:
            prompt += f"\n\n{librarian_context}"
        
        # Execute extraction
        try:
            result, _ = self.web_search.search_and_analyze( # <-- FIX: Unpack 2
                prompt, "RAGMission_Extraction"
            )
            
            # Parse enhanced RAGMission with new fields
            mission_data = result.get('rag_mission', {})
            
            rag_mission = RAGMission(
                target_company_name=mission_data.get('target_company_name', company_name),
                precise_role_title=mission_data.get('precise_role_title', job_title),
                key_technologies=mission_data.get('key_technologies', []),
                core_responsibilities=mission_data.get('core_responsibilities', []),
                signal_gap_keywords=mission_data.get('signal_gap_keywords', []),
                signal_overlap_keywords=mission_data.get('signal_overlap_keywords', [])
            )
            
            # Add new high-signal fields (Phase 3)
            if 'strategic_priorities' in mission_data:
                rag_mission.strategic_priorities = mission_data['strategic_priorities']
            if 'key_initiatives' in mission_data:
                rag_mission.key_initiatives = mission_data['key_initiatives']
            if 'competitors' in mission_data:
                rag_mission.competitors = mission_data['competitors']
            if 'differentiators' in mission_data:
                rag_mission.differentiators = mission_data['differentiators']
            if 'identified_pain_points' in mission_data:
                rag_mission.identified_pain_points = mission_data['identified_pain_points']
            
            logger.info(f"Extracted RAGMission: {rag_mission.precise_role_title} at {rag_mission.target_company_name}")
            return rag_mission
            
        except Exception as e:
            logger.error(f"Failed to extract RAGMission: {e}")
            # Fallback to basic extraction
            return self._extract_rag_mission_fallback(job_description, company_name, job_title)
    
    def _extract_rag_mission_fallback(
        self,
        job_description: str,
        company_name: str,
        job_title: str
    ) -> RAGMission:
        """Fallback RAGMission extraction using heuristics."""
        logger.warning("Using fallback RAGMission extraction")
        
        # Basic keyword extraction
        jd_lower = job_description.lower()
        
        tech_keywords = []
        for tech in ['ai', 'ml', 'cloud', 'aws', 'azure', 'kubernetes', 'python', 'java', 'react', 'data']:
            if tech in jd_lower:
                tech_keywords.append(tech)
        
        return RAGMission(
            target_company_name=company_name,
            precise_role_title=job_title,
            key_technologies=tech_keywords[:5],
            core_responsibilities=['leadership', 'strategy', 'delivery'],
            signal_gap_keywords=[],
            signal_overlap_keywords=[]
        )
    
    def _execute_four_phase_rag(
        self,
        job_description: str,
        rag_mission: RAGMission,
        master_resume_index: MasterResumeIndex,
        comp_config: CompetitiveAnalysisConfig,
        telemetry: RAGTelemetry
    ) -> PartialRAGResult:
        """
        Executes all 4 RAG phases with Librarian context integration.
        """
        result = PartialRAGResult()
        
        # Phase 1: Thematic Analysis
        phase1_start = time.time()
        try:
            logger.info("Executing Phase 1: Thematic Analysis")
            
            librarian_context = self.librarian.get_context_for_phase(
                "phase1", rag_mission, rag_mission.target_company_name
            )
            
            phase1_prompt = prompts_RES.build_phase1_prompt(
                job_description=job_description,
                mission=rag_mission,
                master_resume_index=master_resume_index,
                company_name=rag_mission.target_company_name,
                librarian_context=librarian_context
            )
            
            phase1_func = partial(
                self.web_search.search_and_analyze,
                phase1_prompt,
                "Phase 1: Thematic Analysis"
            )
            
            phase1_tuple, _ = self.circuit_breaker.call( # Unpack 2
                self.phase_executor.execute_with_retry,
                phase1_func,
                "Phase 1"
            )
            
            phase1_data, phase1_calls = phase1_tuple
            result.phase1_result = phase1_data
            result.phase1_success = True
            
            telemetry.phase1_attempts = 1
            telemetry.phase1_success = True
            telemetry.phase1_duration_seconds = time.time() - phase1_start
            telemetry.total_api_calls += phase1_calls
            
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            result.failure_reasons.append(f"Phase 1: {str(e)}")
            telemetry.phase1_duration_seconds = time.time() - phase1_start
            telemetry.errors.append(f"Phase 1: {str(e)}")
        
        # Phase 2: Authenticity Patterns (with Librarian context)
        phase2_start = time.time()
        try:
            logger.info("Executing Phase 2: Authenticity Patterns")
            
            librarian_context = self.librarian.get_context_for_phase(
                "phase2", rag_mission, rag_mission.target_company_name
            )
            
            industry = self._extract_industry_from_jd(job_description)
            phase2_prompt = prompts_RES.build_phase2_prompt(
                job_description=job_description,
                mission=rag_mission,
                industry=industry,
                librarian_context=librarian_context
            )
            
            phase2_func = partial(
                self.web_search.search_and_analyze,
                phase2_prompt,
                "Phase 2: Authenticity Patterns"
            )
            
            phase2_tuple, _ = self.circuit_breaker.call( # Unpack 2
                self.phase_executor.execute_with_retry,
                phase2_func,
                "Phase 2"
            )
            
            phase2_data, phase2_calls = phase2_tuple
            result.phase2_result = phase2_data
            result.phase2_success = True
            
            telemetry.phase2_attempts = 1
            telemetry.phase2_success = True
            telemetry.phase2_duration_seconds = time.time() - phase2_start
            telemetry.total_api_calls += phase2_calls
            
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            result.failure_reasons.append(f"Phase 2: {str(e)}")
            telemetry.phase2_duration_seconds = time.time() - phase2_start
            telemetry.errors.append(f"Phase 2: {str(e)}")
        
        # Phase 3: Competitive Intelligence (with Librarian context)
        phase3_start = time.time()
        try:
            logger.info("Executing Phase 3: Competitive Intelligence")
            
            librarian_context = self.librarian.get_context_for_phase(
                "phase3", rag_mission, rag_mission.target_company_name
            )
            
            peer_companies = self._identify_peer_companies(
                rag_mission.target_company_name, job_description
            )
            
            industry = self._extract_industry_from_jd(job_description)
            phase3_prompt = prompts_RES.build_phase3_prompt(
                job_description=job_description,
                mission=rag_mission,
                master_resume_index=master_resume_index,
                peer_companies=peer_companies,
                comp_config=comp_config,
                industry=industry,
                librarian_context=librarian_context
            )
            
            phase3_func = partial(
                self.web_search.search_and_analyze,
                phase3_prompt,
                "Phase 3: Competitive Intelligence"
            )
            
            phase3_tuple, _ = self.circuit_breaker.call( # Unpack 2
                self.phase_executor.execute_with_retry,
                phase3_func,
                "Phase 3"
            )
            
            phase3_data, phase3_calls = phase3_tuple
            result.phase3_result = phase3_data
            result.phase3_success = True
            
            telemetry.phase3_attempts = 1
            telemetry.phase3_success = True
            telemetry.phase3_duration_seconds = time.time() - phase3_start
            telemetry.total_api_calls += phase3_calls
            
        except Exception as e:
            logger.error(f"Phase 3 failed: {e}")
            result.failure_reasons.append(f"Phase 3: {str(e)}")
            telemetry.phase3_duration_seconds = time.time() - phase3_start
            telemetry.errors.append(f"Phase 3: {str(e)}")
        
        # Phase 4: Problem-Solution Narratives (with Librarian context)
        phase4_start = time.time()
        try:
            logger.info("Executing Phase 4: Problem-Solution Narratives")
            
            librarian_context = self.librarian.get_context_for_phase(
                "phase4", rag_mission, rag_mission.target_company_name
            )
            
            phase4_prompt = prompts_RES.build_phase4_prompt(
                job_description=job_description,
                mission=rag_mission,
                phase1_result=result.phase1_result,
                phase2_result=result.phase2_result,
                phase3_result=result.phase3_result,
                librarian_context=librarian_context
            )
            
            phase4_func = partial(
                self.web_search.search_and_analyze,
                phase4_prompt,
                "Phase 4: Problem-Solution"
            )
            
            phase4_tuple, _ = self.circuit_breaker.call( # Unpack 2
                self.phase_executor.execute_with_retry,
                phase4_func,
                "Phase 4"
            )
            
            phase4_data, phase4_calls = phase4_tuple
            result.phase4_result = phase4_data
            result.phase4_success = True
            
            telemetry.phase4_attempts = 1
            telemetry.phase4_success = True
            telemetry.phase4_duration_seconds = time.time() - phase4_start
            telemetry.total_api_calls += phase4_calls
            
        except Exception as e:
            logger.error(f"Phase 4 failed: {e}")
            result.failure_reasons.append(f"Phase 4: {str(e)}")
            telemetry.phase4_duration_seconds = time.time() - phase4_start
            telemetry.errors.append(f"Phase 4: {str(e)}")
        
        return result
    
    def _synthesize_thematic_analysis(
        self,
        partial_result: PartialRAGResult,
        rag_mission: RAGMission,
        job_description: str
    ) -> ThematicAnalysis:
        """
        Synthesizes PartialRAGResult into final ThematicAnalysis.
        """
        logger.info("Synthesizing ThematicAnalysis from partial results")
        
        thematic_analysis = ThematicAnalysis()
        
        # Extract from Phase 1
        if partial_result.phase1_success and partial_result.phase1_result:
            phase1_thematic = partial_result.phase1_result.get('thematic_analysis', {})
            thematic_analysis.primary_theme = phase1_thematic.get('primary_theme', {})
            thematic_analysis.secondary_themes = phase1_thematic.get('secondary_themes', [])
            thematic_analysis.role_classification = phase1_thematic.get('role_classification', {})
        
        # Extract from Phase 2
        if partial_result.phase2_success and partial_result.phase2_result:
            thematic_analysis.authenticity_patterns = partial_result.phase2_result.get('authenticity_patterns', {})
            thematic_analysis.positioning_directives = partial_result.phase2_result.get('positioning_directives', {})
        
        # Extract from Phase 3
        if partial_result.phase3_success and partial_result.phase3_result:
            comp_data = partial_result.phase3_result.get('competitive_analysis', {})
            thematic_analysis.competitive_intelligence = CompetitiveIntelligence(
                peer_jds_analyzed_count=comp_data.get('peer_jds_analyzed', 0),
                differentiator_keywords=comp_data.get('differentiator_keywords', []),
                differentiator_keywords_raw=comp_data.get('differentiator_keywords_raw', []),
                differentiator_keywords_weighted=comp_data.get('differentiator_keywords_weighted', [])
            )
        
        # Extract from Phase 4
        if partial_result.phase4_success and partial_result.phase4_result:
            thematic_analysis.problem_solution_narratives = partial_result.phase4_result.get('problem_solution_narratives', {})
        
        # Set metadata
        thematic_analysis.signal_quality_score = partial_result.success_rate
        thematic_analysis.retrieval_method = "Multi-Phase RAG with Librarian"
        
        # Build retrieval sources list
        retrieval_sources = []
        for phase_num in [1, 2, 3, 4]:
            phase_result = getattr(partial_result, f'phase{phase_num}_result')
            phase_success = getattr(partial_result, f'phase{phase_num}_success')
            if phase_success and phase_result:
                retrieval_sources.append(RetrievalSource(
                    id=f"phase{phase_num}",
                    type=f"RAG_Phase_{phase_num}",
                    confidence=1.0 if phase_success else 0.0,
                    status="SUCCESS" if phase_success else "FAILED"
                ))
        thematic_analysis.retrieval_sources = retrieval_sources
        
        logger.info(f"Synthesized ThematicAnalysis with signal quality: {thematic_analysis.signal_quality_score:.2%}")
        return thematic_analysis
    
    def _extract_industry_from_jd(self, job_description: str) -> str:
        """Extracts industry from job description using heuristics."""
        jd_lower = job_description.lower()
        
        industries = {
            'financial services': ['banking', 'finance', 'fintech', 'investment', 'capital markets'],
            'technology': ['software', 'saas', 'cloud', 'ai', 'ml', 'data'],
            'healthcare': ['healthcare', 'medical', 'pharma', 'biotech'],
            'retail': ['retail', 'ecommerce', 'consumer'],
            'consulting': ['consulting', 'advisory', 'professional services']
        }
        
        for industry, keywords in industries.items():
            if any(kw in jd_lower for kw in keywords):
                return industry
        
        return 'technology'
    
    def _identify_peer_companies(
        self,
        target_company: str,
        job_description: str
    ) -> List[str]:
        """Identifies peer companies for competitive analysis."""
        # This is a placeholder - in production, this would use industry databases
        industry_peers = {
            'google': ['microsoft', 'amazon', 'meta', 'apple'],
            'microsoft': ['google', 'amazon', 'salesforce', 'oracle'],
            'amazon': ['google', 'microsoft', 'alibaba', 'walmart'],
            'salesforce': ['microsoft', 'sap', 'oracle', 'servicenow']
        }
        
        company_lower = target_company.lower()
        for company, peers in industry_peers.items():
            if company in company_lower:
                return peers[:3]
        
        # Generic tech peers
        return ['microsoft', 'google', 'amazon']
    
    @staticmethod
    def _dict_to_thematic_analysis(data: Dict[str, Any]) -> ThematicAnalysis:
        """
        Converts a dictionary to ThematicAnalysis dataclass.
        Used by StateSerializer for deserialization.
        """
        thematic = ThematicAnalysis()
        
        # Simple fields
        for field in ['primary_theme', 'secondary_themes', 'role_classification',
                      'positioning_directives', 'authenticity_patterns',
                      'problem_solution_narratives', 'signal_quality_score',
                      'retrieval_method', 'weighting_formula', 'evidence_log']:
            if field in data:
                setattr(thematic, field, data[field])
        
        # Reconstruct CompetitiveIntelligence
        if 'competitive_intelligence' in data and isinstance(data['competitive_intelligence'], dict):
            comp_data = data['competitive_intelligence']
            thematic.competitive_intelligence = CompetitiveIntelligence(
                peer_jds_analyzed_count=comp_data.get('peer_jds_analyzed_count', 0),
                differentiator_keywords=comp_data.get('differentiator_keywords', []),
                differentiator_keywords_raw=comp_data.get('differentiator_keywords_raw', []),
                differentiator_keywords_weighted=comp_data.get('differentiator_keywords_weighted', [])
            )
        
        # Reconstruct RetrievalSource list
        if 'retrieval_sources' in data and isinstance(data['retrieval_sources'], list):
            sources = []
            for src in data['retrieval_sources']:
                if isinstance(src, dict):
                    sources.append(RetrievalSource(
                        id=src.get('id', ''),
                        type=src.get('type', ''),
                        confidence=src.get('confidence', 0.0),
                        status=src.get('status', 'UNKNOWN'),
                        specific_source=src.get('specific_source')
                    ))
            thematic.retrieval_sources = sources
        
        return thematic
