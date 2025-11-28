# File: rag.py
# RAG (Retrieval-Augmented Generation) module for Resume Workflow
# Contains classes for web search, circuit breakers, phase execution, 
# and job description analysis (HOP-0).

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
from dataclasses import asdict, dataclass, field, is_dataclass # <--- FIX: Added is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

# Third-party imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None
    cosine_similarity = None

# Local module imports
from config_RES import (
    RAGConfig, WebRagConfig, AppConfig
)
# Note: CompetitiveAnalysisConfig is defined in models.py now
from models_RES import (
    CircuitState, RAGState, RAGEvidence, RAGCritique,
    PartialRAGResult, RAGTelemetry, CompetitiveIntelligence,
    MasterResumeIndex, RAGMission, ThematicAnalysis, HopStatus,
    RetrievalSource, SkillRequirement, SkillCluster,
    HopExecutionError, CircuitBreakerOpenError, PhaseTimeoutError,
    CompetitiveAnalysisConfig
)
from utils_RES import TelemetryLogger

# Import prompts module
import prompts_RES

# Type variable for phase execution
T = TypeVar('T')
logger = logging.getLogger(__name__)

# ==============================================================================
# CIRCUIT BREAKER
# ==============================================================================

class CircuitBreaker:
    """
    Circuit breaker pattern implementation for RAG operations.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, config: RAGConfig):
        self.threshold = config.circuit_breaker_threshold
        self.timeout = config.circuit_breaker_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

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
    def __init__(self, config: RAGConfig):
        self.config = config

    def execute_with_retry(
        self,
        phase_func: Callable[[], T],
        phase_name: str
    ) -> T:
        """Executes a phase function with retry logic."""
        last_exception = None

        for attempt in range(self.config.phase_max_retries):
            try:
                logger.info(
                    f"{phase_name}: Attempt {attempt+1}/{self.config.phase_max_retries}"
                )

                # Execute with timeout
                result_tuple = self._execute_with_timeout(
                    phase_func,
                    self.config.phase_timeout_seconds,
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
                    if attempt < self.config.phase_max_retries - 1:
                        continue
                    else:
                        raise ValueError(f"{phase_name}: All attempts returned invalid result structure.")

            except PhaseTimeoutError as e:
                last_exception = e
                logger.warning(f"{phase_name}: Timeout on attempt {attempt+1}")
                if attempt == self.config.phase_max_retries - 1:
                    break
                time.sleep(getattr(self.config, 'api_initial_backoff_seconds', 2.0) / 2)
                continue

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"{phase_name}: Failed on attempt {attempt+1}: "
                    f"{type(e).__name__}: {e}", exc_info=False
                )
                if attempt == self.config.phase_max_retries - 1:
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
        initial = getattr(self.config, 'api_initial_backoff_seconds', 2.0)
        multiplier = getattr(self.config, 'api_backoff_multiplier', 2.0)
        max_backoff = getattr(self.config, 'api_max_backoff_seconds', 64.0)
        jitter = getattr(self.config, 'api_backoff_jitter', 0.1)

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
            logger.debug(f"{name}: No SIGALRM, executing without timeout (likely Windows)")
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
        """Validates the basic structure of a RAG phase result."""
        if not isinstance(result, dict):
            logger.warning(f"{phase_name}: Validation failed. Result is not a dictionary (Type: {type(result)}).")
            return False

        if "search_summary" not in result:
            logger.warning(f"{phase_name}: Validation failed. Missing required key: 'search_summary'.")
            return False

        # Check for phase-specific keys
        if "phase1" in phase_name.lower() or "thematic" in phase_name.lower():
            if "thematic_analysis" not in result:
                 logger.warning(f"{phase_name}: Validation failed. Missing required key: 'thematic_analysis'.")
                 return False
        elif "phase2" in phase_name.lower() or "authenticity" in phase_name.lower():
            if "authenticity_patterns" not in result:
                 logger.warning(f"{phase_name}: Validation failed. Missing required key: 'authenticity_patterns'.")
                 return False
        elif "phase4" in phase_name.lower() or "narrative" in phase_name.lower():
            if "problem_solution_narratives" not in result:
                 logger.warning(f"{phase_name}: Validation failed. Missing required key: 'problem_solution_narratives'.")
                 return False
        elif "phase3" in phase_name.lower() or "competitive" in phase_name.lower():
            if "competitive_analysis" not in result:
                 logger.warning(f"{phase_name}: Validation failed. Missing required key: 'competitive_analysis'.")
                 return False

        return True

# ==============================================================================
# GEMINI WEB SEARCH CLIENT
# ==============================================================================

class GeminiWebSearchClient:
    """
    Client for executing RAG calls via Gemini, including agentic loops.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, config: RAGConfig = RAGConfig()):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package required for web RAG")

        if not os.environ.get("GEMINI_API_KEY"):
            logging.warning("GEMINI_API_KEY environment variable not found. API calls may fail.")

        try:
            # This will use the globally configured API key if set by run_workflow.py
            self.client = genai.GenerativeModel(config.model)
            logging.info(f"GenerativeModel '{config.model}' initialized.")
        except Exception as e:
             logging.error(f"Failed to initialize GenerativeModel '{config.model}': {e}", exc_info=True)
             raise ImportError(f"Failed to initialize Gemini GenerativeModel: {e}") from e

        self.config = config
        self.circuit_breaker = CircuitBreaker(config)
        self.api_calls_made = 0

    def search_and_analyze(
        self,
        prompt: str,
        phase_name: str = "unknown"
    ) -> Tuple[Dict[str, Any], int]:
        """Performs a standard, non-agentic RAG call with retries."""
        last_exception = None
        calls_this_request = 0

        for attempt in range(self.config.api_max_retries):
            try:
                result, calls_made_in_attempt = self.circuit_breaker.call(
                    self._make_api_call,
                    prompt,
                    attempt,
                    phase_name,
                    logger
                )
                calls_this_request += calls_made_in_attempt

                logger.info(f"{phase_name} completed successfully on attempt {attempt+1}")
                return result, calls_this_request

            except CircuitBreakerOpenError as e:
                logger.error(f"{phase_name}: Circuit breaker OPEN - aborting retries")
                raise

            except (HopExecutionError, ValueError, TimeoutError) as e:
                last_exception = e
                error_type = type(e).__name__
                log_msg = f"{phase_name} API attempt {attempt+1}/{self.config.api_max_retries} failed: {error_type}: {e}"

                if isinstance(e, ValueError):
                     problematic_text = str(e)[:200] if str(e) else "N/A"
                     logger.warning(
                         f"{phase_name} API attempt {attempt+1}/{self.config.api_max_retries} failed: {error_type}. "
                         f"Failed to parse JSON. Error snippet: '{problematic_text}...'"
                     )
                elif isinstance(e, TimeoutError):
                     logger.warning(f"{log_msg} (Timeout error)")
                else:
                     logger.warning(f"{log_msg} (HopExecutionError)")

                if attempt < self.config.api_max_retries - 1:
                    backoff = self._calculate_backoff(attempt)
                    logger.info(f"Backing off {backoff:.2f}s before retry...")
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"{phase_name}: All {self.config.api_max_retries} API attempts failed")
                    raise

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"{phase_name} API attempt {attempt+1}/{self.config.api_max_retries} "
                    f"failed with unexpected error: {type(e).__name__}: {e}", exc_info=False
                )
                if attempt < self.config.api_max_retries - 1:
                    backoff = self._calculate_backoff(attempt)
                    logger.info(f"Backing off {backoff:.2f}s before retry...")
                    time.sleep(backoff)
                    continue
                else:
                    logger.error(f"{phase_name}: All {self.config.api_max_retries} API attempts failed")
                    raise

        if last_exception:
            raise last_exception
        raise RuntimeError(f"{phase_name}: Unexpected exit from retry loop")

    def _make_api_call(
        self,
        prompt: str,
        attempt: int,
        phase_name: str,
        logger: logging.Logger
    ) -> Tuple[Dict[str, Any], int]:
        """Internal method to make the actual Gemini API call."""
        start_time = time.time()
        calls_made = 0

        if not self.client:
            raise HopExecutionError(f"{phase_name} cannot make API call: Gemini client not initialized.")

        logger.debug(
            f"{phase_name} API call starting (Attempt {attempt+1}): "
            f"max_tokens={self.config.max_tokens}, temp={self.config.temperature}"
        )

        try:
            self.api_calls_made += 1
            calls_made = 1

            response = self.client.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
            )

            elapsed = time.time() - start_time

            json_text_content = ""
            finish_reason = None
            prompt_feedback = getattr(response, 'prompt_feedback', None)

            if hasattr(response, 'candidates') and response.candidates:
                 candidate_one = response.candidates[0]
                 finish_reason = getattr(candidate_one, 'finish_reason', None)

            logger.debug(
                f"{phase_name} API call completed in {elapsed:.2f}s (Call #{self.api_calls_made}): "
                f"finish_reason={finish_reason}"
            )

            if finish_reason == 2: # MAX_TOKENS
                 logger.error(
                     f"{phase_name} API call stopped: finish_reason=MAX_TOKENS (2), "
                     f"limit={self.config.max_tokens}"
                 )
                 raise HopExecutionError(f"API call stopped due to MAX_TOKENS limit ({self.config.max_tokens}). Response may be incomplete.")
            elif finish_reason is not None and finish_reason != 1: # 1 = STOP
                 block_reason = getattr(prompt_feedback, 'block_reason', None) if prompt_feedback else None
                 logger.error(
                     f"{phase_name} API call stopped: finish_reason={finish_reason}, "
                     f"block_reason={block_reason}"
                 )
                 raise HopExecutionError(f"API call stopped. Finish Reason Code: {finish_reason}. Block Reason: {block_reason}")

            if hasattr(response, 'text') and response.text:
                 json_text_content = response.text
                 logger.debug(f"{phase_name} Extracted text directly from response.text.")
            elif hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                         json_text_content = part.text
                         logger.debug(f"{phase_name} Extracted text from response parts (fallback).")
                         break
                if not json_text_content:
                     logger.warning(f"{phase_name} API response parts did not contain text: {response.parts}")
                     raise ValueError("API response contained parts but no usable text content.")
            else:
                 logger.warning(f"{phase_name} API response structure unexpected or empty: {response}")
                 block_reason = getattr(prompt_feedback, 'block_reason', None) if prompt_feedback else None
                 if block_reason: raise HopExecutionError(f"API call blocked. Block Reason: {block_reason}")
                 raise ValueError("API response did not contain 'parts' or 'text'.")

            parsed_json = self._extract_json(json_text_content)
            return parsed_json, calls_made

        except HopExecutionError as he:
             logger.warning(f"{phase_name} API call failed (Attempt {attempt+1}): {he}")
             raise
        except (TimeoutError, ValueError) as e:
             elapsed = time.time() - start_time
             if isinstance(e, TimeoutError) or "timeout" in str(e).lower():
                  logger.warning(f"{phase_name} API call timed out after {elapsed:.2f}s (Attempt {attempt+1})")
                  raise TimeoutError(f"{phase_name} timed out") from e
             else:
                  logger.warning(f"{phase_name} JSON parsing failed (Attempt {attempt+1}): {e}")
                  raise
        except Exception as e:
            elapsed = time.time() - start_time
            logger.warning(f"{phase_name} API call failed unexpectedly (Attempt {attempt+1}): {type(e).__name__}: {e}", exc_info=False)
            raise

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculates exponential backoff with jitter."""
        base_delay = min(
            self.config.api_initial_backoff_seconds * (
                self.config.api_backoff_multiplier ** attempt
            ),
            self.config.api_max_backoff_seconds
        )
        jitter_range = base_delay * self.config.api_backoff_jitter
        jitter = random.uniform(-jitter_range, jitter_range)
        return max(0.1, base_delay + jitter)

    def _extract_json(self, text_content: str) -> Dict[str, Any]:
        """Extracts a JSON object from a string, handling markdown fences."""
        stripped_content = text_content.strip() if isinstance(text_content, str) else ""
        if not stripped_content or not (stripped_content.startswith('{') or stripped_content.startswith('```json')):
             raise ValueError(
                 f"Response content does not appear to be JSON or a markdown JSON block. "
                 f"Content preview: {str(text_content)[:200]}..."
             )

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text_content, re.DOTALL)
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(1))
                logging.debug("Successfully parsed markdown JSON block.")
                return parsed_json
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse markdown JSON block: {e}. Trying other strategies.")
                pass

        # Find first '{' and last '}'
        brace_level = 0
        start_index = -1
        end_index = -1
        for i, char in enumerate(text_content):
            if char == '{':
                if start_index == -1:
                    start_index = i
                brace_level += 1
            elif char == '}':
                if start_index != -1:
                    brace_level -= 1
                    if brace_level == 0:
                        end_index = i + 1
                        break

        if start_index != -1 and end_index != -1:
            potential_json = text_content[start_index:end_index]
            try:
                parsed_json = json.loads(potential_json)
                logging.debug("Successfully parsed first complete JSON object.")
                return parsed_json
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse first complete JSON object: {e}. Trying other strategies.")
                pass
        else:
             if not json_match:
                 logging.warning("Could not find balanced braces for JSON object and no markdown block found.")

        # Try cleaning and parsing directly
        cleaned = text_content.replace('```json', '').replace('```', '').strip()
        if cleaned.startswith('{'):
            try:
                parsed_json = json.loads(cleaned)
                logging.debug("Successfully parsed cleaned text directly.")
                return parsed_json
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse cleaned text directly: {e}. Trying repair.")
                pass
        else:
             logging.warning("Cleaned text does not start with '{'. Skipping direct parse.")

        # Try repairing
        if cleaned.startswith('{'):
            repaired = self._attempt_json_repair(cleaned)
            if repaired:
                logging.info("Successfully parsed JSON after repair.")
                return repaired
        else:
             logging.warning("Skipping JSON repair as cleaned text does not start with '{'.")

        raise ValueError(
            f"No valid JSON found in Gemini's response after multiple attempts. "
            f"Content preview: {text_content[:200]}..."
        )

    def _attempt_json_repair(self, text: str) -> Optional[Dict[str, Any]]:
        """Tries to fix common JSON errors like trailing commas."""
        repairs = [
            lambda s: re.sub(r',(\s*[}\]])', r'\1', s), # Fix trailing commas
            lambda s: s.replace("'", '"'), # Fix single quotes
            lambda s: ''.join(char for char in s if ord(char) >= 32 or char == '\n'), # Remove control chars
        ]

        for repair_func in repairs:
            try:
                repaired = repair_func(text)
                return json.loads(repaired)
            except (json.JSONDecodeError, Exception):
                continue

        return None

    def agentic_search_and_analyze(
        self,
        prompt: str,
        phase_name: str = "unknown",
        max_iterations: int = 3,
        confidence_threshold: float = 0.7
    ) -> Tuple[Dict[str, Any], int, RAGState]:
        """
        Agentic RAG loop that iteratively refines research through self-critique.
        (Extracted from resume_workflow_v16_20.py)
        """
        logger.info(f"{phase_name}: Starting AGENTIC RAG loop (max_iterations={max_iterations}, threshold={confidence_threshold})")
        
        state = RAGState(
            phase_name=phase_name,
            iteration=0
        )
        
        logger.info(f"{phase_name}: Iteration 1 - Initial search")
        result, calls_made = self.search_and_analyze(prompt, phase_name)
        state.cumulative_result = result
        state.total_api_calls += calls_made
        state.iteration = 1
        
        initial_evidence = RAGEvidence(
            iteration=1,
            action="initial_search",
            query_or_action="Standard phase prompt",
            findings_summary=f"Retrieved {result.get('search_summary', {}).get('searches_performed', 0)} searches",
            sources_count=len(result.get('search_summary', {}).get('sources', [])),
            confidence_contribution=0.5
        )
        state.add_evidence(initial_evidence)
        
        critique = self._critique_rag_results(result, phase_name, state.iteration)
        state.add_critique(critique)
        
        logger.info(
            f"{phase_name}: Iteration 1 critique - confidence={critique.confidence_score:.2f}, "
            f"gaps={len(critique.gaps_identified)}, sufficient={critique.is_sufficient}"
        )
        
        if critique.is_sufficient or critique.confidence_score >= confidence_threshold:
            logger.info(f"{phase_name}: Initial search sufficient. Confidence: {critique.confidence_score:.2f}")
            if 'thematic_analysis' in result and isinstance(result['thematic_analysis'], dict):
                result['thematic_analysis']['evidence_log'] = [asdict(e) for e in state.evidence_log]
            return result, state.total_api_calls, state
        
        for iteration in range(2, max_iterations + 1):
            logger.info(f"{phase_name}: Iteration {iteration} - Refinement")
            state.iteration = iteration
            
            refinement_prompt = self._build_refinement_prompt(
                original_prompt=prompt,
                current_result=result,
                critique=critique,
                phase_name=phase_name
            )
            
            try:
                refined_result, calls_made = self.search_and_analyze(
                    refinement_prompt,
                    f"{phase_name} (Refinement {iteration})"
                )
                state.total_api_calls += calls_made
                
                merged_result = self._merge_rag_results(
                    state.cumulative_result,
                    refined_result,
                    phase_name
                )
                state.cumulative_result = merged_result
                
                refinement_evidence = RAGEvidence(
                    iteration=iteration,
                    action="refinement_query",
                    query_or_action=f"Addressed {len(critique.gaps_identified)} gaps",
                    findings_summary=f"Retrieved {refined_result.get('search_summary', {}).get('searches_performed', 0)} additional searches",
                    sources_count=len(refined_result.get('search_summary', {}).get('sources', [])),
                    confidence_contribution=0.2
                )
                state.add_evidence(refinement_evidence)
                
                critique = self._critique_rag_results(merged_result, phase_name, iteration)
                state.add_critique(critique)
                
                logger.info(
                    f"{phase_name}: Iteration {iteration} critique - confidence={critique.confidence_score:.2f}, "
                    f"gaps={len(critique.gaps_identified)}, sufficient={critique.is_sufficient}"
                )
                
                if critique.is_sufficient or critique.confidence_score >= confidence_threshold:
                    logger.info(
                        f"{phase_name}: Refinement successful after {iteration} iterations. "
                        f"Final confidence: {critique.confidence_score:.2f}"
                    )
                    break
                    
            except Exception as e:
                logger.warning(
                    f"{phase_name}: Refinement iteration {iteration} failed: {e}. "
                    "Using results from previous iteration."
                )
                break
        
        final_result = state.cumulative_result
        if 'thematic_analysis' in final_result and isinstance(final_result['thematic_analysis'], dict):
            final_result['thematic_analysis']['evidence_log'] = [asdict(e) for e in state.evidence_log]
        
        logger.info(
            f"{phase_name}: Agentic RAG complete. Total iterations: {state.iteration}, "
            f"Total API calls: {state.total_api_calls}, Final confidence: {critique.confidence_score:.2f}"
        )
        
        return final_result, state.total_api_calls, state
    
    def _critique_rag_results(
        self,
        result: Dict[str, Any],
        phase_name: str,
        iteration: int
    ) -> RAGCritique:
        """
        Evaluate RAG retrieval quality and identify gaps (heuristic-based).
        """
        search_summary = result.get('search_summary', {})
        searches_performed = search_summary.get('searches_performed', 0)
        sources = search_summary.get('sources', [])
        sources_count = len(sources)
        
        gaps = []
        confidence = 0.5
        
        if searches_performed < 5:
            gaps.append("Insufficient search depth - fewer than 5 searches performed")
            confidence -= 0.2
        elif searches_performed >= 10:
            confidence += 0.1
        
        if sources_count < 3:
            gaps.append("Too few unique sources retrieved")
            confidence -= 0.2
        elif sources_count >= 8:
            confidence += 0.15
        
        # Phase-specific checks
        if "phase1" in phase_name.lower() or "thematic" in phase_name.lower():
            thematic = result.get('thematic_analysis', {})
            if not thematic.get('primary_theme'):
                gaps.append("Missing primary theme identification")
                confidence -= 0.2
            if not thematic.get('secondary_themes'):
                gaps.append("Missing secondary themes")
                confidence -= 0.1
            if len(thematic.get('trending_keywords', [])) < 3:
                gaps.append("Insufficient trending keywords identified")
                confidence -= 0.1
                
        elif "phase2" in phase_name.lower() or "authenticity" in phase_name.lower():
            authenticity = result.get('authenticity_patterns', {})
            if len(authenticity.get('executive_summary_patterns', [])) < 3:
                gaps.append("Insufficient authenticity patterns extracted")
                confidence -= 0.2
                
        elif "phase3" in phase_name.lower() or "competitive" in phase_name.lower():
            competitive = result.get('competitive_analysis', {})
            peer_jds = competitive.get('search_summary', {}).get('peer_jds_analyzed', 0)
            if peer_jds < 5:
                gaps.append("Insufficient peer JDs analyzed for competitive intelligence")
                confidence -= 0.2
        
        if sources:
            unique_domains = len(set(self._extract_domain(url) for url in sources))
            if unique_domains < 3:
                gaps.append("Limited source diversity - same domain repeated")
                confidence -= 0.1
            elif unique_domains >= 5:
                confidence += 0.1
        
        confidence = max(0.0, min(1.0, confidence))
        
        refinement_tasks = []
        if gaps:
            if "search depth" in str(gaps).lower():
                refinement_tasks.append("Perform additional targeted searches on identified themes")
            if "sources" in str(gaps).lower():
                refinement_tasks.append("Search for more diverse sources across different domains")
            if "primary theme" in str(gaps).lower():
                refinement_tasks.append("Focus search on identifying clear primary skill theme")
            if "patterns" in str(gaps).lower():
                refinement_tasks.append("Search for more LinkedIn profiles and extract additional patterns")
            if "peer JDs" in str(gaps).lower():
                refinement_tasks.append("Analyze more competitor job descriptions")
        
        is_sufficient = len(gaps) == 0 and confidence >= 0.7
        
        reasoning = f"Iteration {iteration}: Analyzed {searches_performed} searches across {sources_count} sources. "
        if gaps:
            reasoning += f"Identified {len(gaps)} gaps requiring attention. "
        else:
            reasoning += "No critical gaps identified. "
        reasoning += f"Confidence assessment: {confidence:.2f}"
        
        return RAGCritique(
            confidence_score=confidence,
            gaps_identified=gaps,
            refinement_tasks=refinement_tasks,
            reasoning=reasoning,
            is_sufficient=is_sufficient
        )
    
    def _extract_domain(self, url: str) -> str:
        """Extracts the domain from a URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return url
    
    def _build_refinement_prompt(
        self,
        original_prompt: str,
        current_result: Dict[str, Any],
        critique: RAGCritique,
        phase_name: str
    ) -> str:
        """
        Build targeted refinement prompt based on critique gaps.
        """
        refinement_section = "**REFINEMENT FOCUS:**\n"
        refinement_section += f"Previous search identified {len(critique.gaps_identified)} gaps:\n"
        for gap in critique.gaps_identified:
            refinement_section += f"- {gap}\n"
        refinement_section += "\n**REQUIRED ACTIONS:**\n"
        for task in critique.refinement_tasks:
            refinement_section += f"- {task}\n"
        refinement_section += "\nFocus your additional searches on filling these specific gaps.\n"
        
        refined_prompt = original_prompt + "\n\n" + refinement_section
        
        return refined_prompt
    
    def _merge_rag_results(
        self,
        original: Dict[str, Any],
        refined: Dict[str, Any],
        phase_name: str
    ) -> Dict[str, Any]:
        """
        Merge original and refined RAG results, prioritizing new findings.
        """
        merged = copy.deepcopy(original)
        
        if 'search_summary' in refined:
            orig_summary = merged.get('search_summary', {})
            refined_summary = refined['search_summary']
            
            merged['search_summary']['searches_performed'] = (
                orig_summary.get('searches_performed', 0) +
                refined_summary.get('searches_performed', 0)
            )
            
            orig_sources = set(orig_summary.get('sources', []))
            refined_sources = set(refined_summary.get('sources', []))
            merged['search_summary']['sources'] = list(orig_sources | refined_sources)
            
            # Merge other summary keys
            for key in refined_summary:
                if key not in ['searches_performed', 'sources']:
                    if isinstance(refined_summary[key], int):
                        merged['search_summary'][key] = (
                            orig_summary.get(key, 0) + refined_summary[key]
                        )
                    elif isinstance(refined_summary[key], list):
                        orig_list = orig_summary.get(key, [])
                        if orig_list and isinstance(orig_list[0], str):
                            merged['search_summary'][key] = list(set(orig_list) | set(refined_summary[key]))
                        else:
                            merged['search_summary'][key] = orig_list + refined_summary[key]
        
        # Phase-specific merging
        if "phase1" in phase_name.lower() or "thematic" in phase_name.lower():
            if 'thematic_analysis' in refined:
                orig_thematic = merged.get('thematic_analysis', {})
                refined_thematic = refined['thematic_analysis']
                
                for key in ['trending_keywords', 'required_skills', 'preferred_skills']:
                    if key in refined_thematic:
                        orig_keywords = orig_thematic.get(key, [])
                        merged['thematic_analysis'][key] = list(
                            set(orig_keywords) | set(refined_thematic.get(key, []))
                        )
                
                if 'secondary_themes' in refined_thematic:
                    orig_themes = orig_thematic.get('secondary_themes', [])
                    new_themes = refined_thematic['secondary_themes']
                    existing_names = {t.get('name') for t in orig_themes if isinstance(t, dict)}
                    for theme in new_themes:
                        if isinstance(theme, dict) and theme.get('name') not in existing_names:
                            orig_themes.append(theme)
                    merged['thematic_analysis']['secondary_themes'] = orig_themes
        
        elif "phase2" in phase_name.lower() or "authenticity" in phase_name.lower():
            if 'authenticity_patterns' in refined:
                orig_patterns = merged.get('authenticity_patterns', {})
                refined_patterns = refined['authenticity_patterns']
                
                for key in ['executive_summary_patterns', 'achievement_verb_patterns', 
                           'metric_presentation_patterns', 'competency_phrasing']:
                    if key in refined_patterns:
                        orig_list = orig_patterns.get(key, [])
                        merged['authenticity_patterns'][key] = list(
                            set(orig_list) | set(refined_patterns.get(key, []))
                        )
        
        elif "phase3" in phase_name.lower() or "competitive" in phase_name.lower():
            if 'competitive_analysis' in refined:
                orig_comp = merged.get('competitive_analysis', {})
                refined_comp = refined['competitive_analysis']
                
                if 'differentiator_keywords' in refined_comp:
                    orig_diff = orig_comp.get('differentiator_keywords', [])
                    all_diff = orig_diff + refined_comp.get('differentiator_keywords', [])
                    seen = set()
                    unique_diff = []
                    for item in all_diff:
                        item_key = item.get('keyword') if isinstance(item, dict) else item
                        if item_key not in seen:
                            seen.add(item_key)
                            unique_diff.append(item)
                    merged['competitive_analysis']['differentiator_keywords'] = unique_diff
        
        return merged
    
# ==============================================================================
# JD CACHE MANAGER
# ==============================================================================

class JDCacheManager:
    """
    Manages caching of processed job descriptions.
    (Extracted from resume_workflow_v16_20.py)
    """
    def __init__(self, cache_dir: str, ttl_days: int):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_days * 24 * 3600
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache_key(self, job_description: str) -> str:
        """Generates an MD5 hash for the JD content."""
        return hashlib.md5(job_description.encode('utf-8')).hexdigest()

    def get(self, job_description: str) -> Optional[Dict[str, Any]]:
        """Retrieves a cached result if valid."""
        cache_key = self.get_cache_key(job_description)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        if not os.path.exists(cache_file):
            return None

        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age > self.ttl_seconds:
            os.remove(cache_file)
            return None

        with open(cache_file, 'r') as f:
            return json.load(f)

    def set(self, job_description: str, analysis: Dict[str, Any]):
        """Saves a result to the cache."""
        cache_key = self.get_cache_key(job_description)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        with open(cache_file, 'w') as f:
            json.dump(analysis, f, indent=2)

# ==============================================================================
# WEB SEARCH RAG ORCHESTRATOR
# ==============================================================================

class WebSearchRAG:
    """
    Orchestrates the 4-phase RAG process.
    (Extracted from resume_workflow_v16_20.py and refactored)
    """
    def __init__(self, client: GeminiWebSearchClient, config: RAGConfig = RAGConfig(), master_resume_index: Optional[MasterResumeIndex] = None, web_rag_config: WebRagConfig = None):
        self.client = client
        self.config = config
        self.master_resume_index = master_resume_index
        self.comp_config = CompetitiveAnalysisConfig() # Using default from models.py
        self.executor = PhaseExecutor(config)
        if web_rag_config is None:
            web_rag_config = WebRagConfig()
        self.PEERS_BY_INDUSTRY = web_rag_config.peers_by_industry

    def phase1_thematic_research(self, job_description: str, mission: RAGMission) -> Dict[str, Any]:
        """Executes Phase 1 RAG."""
        def main_phase1():
            # Call the prompt builder from the prompts module
            prompt = prompts_RES.build_phase1_prompt(
                job_description=job_description,
                mission=mission,
                master_resume_index=self.master_resume_index
            )
            
            result_dict, calls_made, rag_state = self.client.agentic_search_and_analyze(
                prompt, 
                "Phase 1: Thematic Research"
            )
            return result_dict, calls_made

        return self.executor.execute_with_retry(
            main_phase1,
            "Phase 1"
        )

    def phase2_authenticity_patterns(
        self,
        job_description: str,
        mission: RAGMission
    ) -> Dict[str, Any]:
        """Executes Phase 2 RAG."""
        def main_phase2():
            # Call the prompt builder from the prompts module
            prompt = prompts_RES.build_phase2_prompt(
                job_description=job_description,
                mission=mission,
                industry=self._infer_industry(job_description)
            )
            
            result_dict, calls_made, rag_state = self.client.agentic_search_and_analyze(
                prompt, 
                "Phase 2: Authenticity Patterns"
            )
            return result_dict, calls_made

        return self.executor.execute_with_retry(
            main_phase2,
            "Phase 2"
        )

    def phase3_competitive_positioning(
        self,
        job_description: str,
        mission: RAGMission
    ) -> Dict[str, Any]:
        """Executes Phase 3 RAG."""
        def main_phase3():
            industry = self._infer_industry(job_description)
            peer_companies = self._infer_peer_companies(mission.target_company_name, job_description)
            
            # Call the prompt builder from the prompts module
            prompt = prompts_RES.build_phase3_prompt(
                job_description=job_description,
                mission=mission,
                master_resume_index=self.master_resume_index,
                peer_companies=peer_companies,
                comp_config=self.comp_config,
                industry=industry
            )
            
            result_dict, calls_made, rag_state = self.client.agentic_search_and_analyze(
                prompt,
                "Phase 3: Competitive Positioning"
            )
            return result_dict, calls_made

        return self.executor.execute_with_retry(
            phase_func=main_phase3,
            phase_name="Phase 3"
        )
  
    def phase4_narrative_mining(self, mission: RAGMission) -> Dict[str, Any]:
        """Executes Phase 4 RAG."""
        def main_phase4():
            # Call the prompt builder from the prompts module
            prompt = prompts_RES.build_phase4_prompt(mission=mission)
            
            result_dict, calls_made, rag_state = self.client.agentic_search_and_analyze(
                prompt, 
                "Phase 4: Narrative Mining"
            )
            return result_dict, calls_made

        return self.executor.execute_with_retry(
            main_phase4,
            "Phase 4"
        )

    # --- Helper methods used by phase prompts ---
    
    def _infer_industry(self, job_description: str) -> str:
        """Infers industry from JD text."""
        jd_lower = job_description.lower()

        if 'fintech' in jd_lower or 'banking' in jd_lower:
            return "Financial Technology"
        elif 'healthcare' in jd_lower or 'medical' in jd_lower:
            return "Healthcare"
        elif 'retail' in jd_lower or 'e-commerce' in jd_lower:
            return "Retail/E-Commerce"
        elif 'saas' in jd_lower or 'software' in jd_lower:
            return "Software/SaaS"
        else:
            return "Technology"

    def _infer_peer_companies(self, company_name: str, job_description: str) -> List[str]:
        """Infers peer companies based on industry."""
        industry = self._infer_industry(job_description)

        peers = self.PEERS_BY_INDUSTRY.get(industry, self.PEERS_BY_INDUSTRY["Technology"])
        return [p for p in peers if p.lower() not in company_name.lower()][:5]


# ==============================================================================
# ENHANCED JOB DESCRIPTION ANALYZER (HOP-0)
# ==============================================================================

class EnhancedJobDescriptionAnalyzer:
    """
    Main class for HOP-0. Runs pre-RAG analysis and orchestrates the 4-phase
    WebSearchRAG execution.
    (Reconciled with resume_workflow_v16_20.py)
    """
    def __init__(
        self,
        master_resume: Dict,
        enable_web_search: bool = True,
        config: Optional[RAGConfig] = None,
        web_rag_config: Optional[WebRagConfig] = None,
        app_config: Optional[AppConfig] = None
    ):
        """
        Initialize the analyzer with flexible configuration options.
        
        Args:
            master_resume: Master resume dictionary
            enable_web_search: Enable web search functionality
            config: RAGConfig instance (deprecated, use app_config)
            web_rag_config: WebRagConfig instance (deprecated, use app_config)
            app_config: Full AppConfig instance (preferred)
        """
        self.master_resume = master_resume
        self.enable_web_search = enable_web_search and GEMINI_AVAILABLE
        
        # Handle backward compatibility for config parameters
        if app_config is not None:
            # New style: use app_config
            self.config = app_config.rag
            self.web_rag_config = app_config.web_rag
            self.app_config = app_config
        else:
            # Old style: use individual configs
            self.config = config if config is not None else RAGConfig()
            self.web_rag_config = web_rag_config if web_rag_config is not None else WebRagConfig()
            # Create minimal app_config for compatibility
            self.app_config = AppConfig(rag=self.config, web_rag=self.web_rag_config)
        
        self.rag_mission: Optional[RAGMission] = None
        self.total_api_calls_hop0 = 0

        logger.info("Building master resume semantic index...")
        self.master_resume_index = self._build_master_resume_semantic_index(master_resume)
        logger.info(f"  ✓ Index built: {len(self.master_resume_index.skill_to_experiences)} skills, "
                   f"{len(self.master_resume_index.achievement_catalog)} achievements")

        if self.config.telemetry_enabled:
            self.telemetry_logger = TelemetryLogger(self.config.telemetry_log_dir)
        else:
            self.telemetry_logger = None

        if self.enable_web_search:
            try:
                self.gemini_client = GeminiWebSearchClient(self.config)
                self.web_rag = WebSearchRAG(
                    self.gemini_client, 
                    self.config, 
                    master_resume_index=self.master_resume_index,
                    web_rag_config=self.web_rag_config
                )
                self.cache_manager = JDCacheManager(
                    self.config.cache_dir,
                    self.config.cache_ttl_days
                )
            except Exception as e:
                logging.getLogger(__name__).warning(f"Web RAG initialization failed: {e}")
                self.gemini_client = None
                self.web_rag = None
                self.cache_manager = None
        else:
            self.gemini_client = None
            self.web_rag = None
            self.cache_manager = None

    def analyze(self, job_description: str) -> Tuple[ThematicAnalysis, int]:
        """
        Main entry point for HOP-0 analysis.
        (FIXED: This logic is restored from resume_workflow_v16_20.py)
        """
        self.total_api_calls_hop0 = 0
        
        try:
            self.rag_mission = self._execute_pre_rag_analysis(job_description)
        except Exception as e:
            logger.error(f"FATAL: Pre-RAG analysis (HOP -0.5) failed: {e}. Halting workflow.", exc_info=True)
            raise HopExecutionError(f"HOP -0.5 Pre-RAG Analysis failed: {e}") from e

        if not self.enable_web_search:
             logger.error("FATAL: Web search is disabled, but no fallback is allowed. Halting workflow.")
             raise HopExecutionError("HOP-0 Configuration Error: Web search disabled, cannot proceed without fallback.")

        if not self.web_rag or not self.gemini_client:
             logger.error("FATAL: Web RAG components failed to initialize. Halting workflow.")
             raise HopExecutionError("HOP-0 Initialization Error: Web RAG components not available.")

        try:
            analysis, calls_made_rag_phases = self._analyze_with_resilient_web_search(job_description)
            self.total_api_calls_hop0 += calls_made_rag_phases
            logger.info(f"HOP-0 Web RAG analysis successful. Total API calls for HOP-0: {self.total_api_calls_hop0}")
            return analysis, self.total_api_calls_hop0
        except Exception as e:
             logger.error(f"FATAL: Web RAG analysis failed at HOP-0: {e}. Halting workflow.", exc_info=True)
             # Attempt to retrieve call count even on failure
             if hasattr(self, 'web_rag') and hasattr(self.web_rag, 'executor') and hasattr(self.web_rag.executor, 'total_api_calls_this_hop'):
                 self.total_api_calls_hop0 += getattr(self.web_rag.executor, 'total_api_calls_this_hop', 0)
             raise HopExecutionError(f"HOP-0 Web RAG analysis failed: {e}") from e

    def _build_master_resume_semantic_index(self, master_resume: Dict) -> MasterResumeIndex:
        """Creates an indexed version of the master resume for RAG."""
        skill_to_experiences: Dict[str, List[Dict]] = defaultdict(list)
        achievement_catalog: List[Dict] = []
        domain_vocabularies: Dict[str, List[str]] = defaultdict(list)
        recency_scores: Dict[str, float] = {}
        
        experiences = master_resume.get("professional_experience", [])
        current_year = datetime.now().year
        
        for exp_idx, exp in enumerate(experiences):
            role = exp.get("role", "")
            company = exp.get("company", "")
            end_date_str = exp.get("dates", {}).get("end", "")
            
            try:
                if end_date_str and end_date_str.lower() != "present":
                    end_year = int(end_date_str.split()[-1]) if end_date_str.split() else current_year
                else:
                    end_year = current_year
                years_ago = current_year - end_year
                recency = max(0.0, 1.0 - (years_ago * 0.15))
            except Exception:
                recency = 0.5
            
            bullets_raw = exp.get("bullet_pool", exp.get("highlights", []))
            bullets = [b for b in bullets_raw if isinstance(b, str)]
            
            for bullet_text in bullets:
                potential_skills = self._extract_skills_from_text(bullet_text)
                
                for skill in potential_skills:
                    skill_lower = skill.lower()
                    skill_to_experiences[skill_lower].append({
                        "role": role,
                        "company": company,
                        "bullet": bullet_text,
                        "recency": recency,
                        "experience_index": exp_idx
                    })
                    
                    if skill_lower not in recency_scores:
                        recency_scores[skill_lower] = recency
                    else:
                        recency_scores[skill_lower] = max(recency_scores[skill_lower], recency)
                
                metrics = self._extract_metrics_from_text(bullet_text)
                for metric_dict in metrics:
                    achievement_catalog.append({
                        **metric_dict,
                        "source_bullet": bullet_text,
                        "role": role,
                        "company": company
                    })
            
            domain = self._infer_domain(role, company, bullets)
            if domain:
                vocab = self._extract_domain_vocabulary(role, company, bullets)
                domain_vocabularies[domain].extend(vocab)
        
        for domain in domain_vocabularies:
            domain_vocabularies[domain] = list(set(domain_vocabularies[domain]))
        
        return MasterResumeIndex(
            skill_to_experiences=dict(skill_to_experiences),
            achievement_catalog=achievement_catalog,
            domain_vocabularies=dict(domain_vocabularies),
            recency_scores=recency_scores,
            skill_vectors=None
        )
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Simple skill extractor (placeholder for NLP)."""
        skill_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', # Capitalized words
            r'\b[A-Z]{2,}\b', # Acronyms
            r'\b\w+(?:-\w+)+\b' # Hyphenated
        ]
        skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, text)
            skills.extend(matches)
        
        stopwords = {"The", "This", "That", "With", "From", "Into", "As", "At"}
        skills = [s for s in skills if s not in stopwords and len(s) > 2]
        return list(set(skills))[:20]
    
    def _extract_metrics_from_text(self, text: str) -> List[Dict]:
        """Simple metric extractor."""
        metrics = []
        money_pattern = r'\$(\d+(?:\.\d+)?)\s*([MBK])'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            metrics.append({
                "metric_type": "revenue/cost",
                "value": f"${match.group(1)}{match.group(2).upper()}",
                "context": text[:100]
            })
        
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%\s*(\w+)'
        for match in re.finditer(percent_pattern, text, re.IGNORECASE):
            metrics.append({
                "metric_type": "percentage",
                "value": f"{match.group(1)}%",
                "dimension": match.group(2),
                "context": text[:100]
            })
        return metrics
    
    def _infer_domain(self, role: str, company: str, bullets: List) -> Optional[str]:
        """Infers domain from experience text."""
        text = f"{role} {company} {' '.join([str(b) for b in bullets])}".lower()
        domain_keywords = {
            "cloud_partnerships": ["aws", "azure", "gcp", "cloud", "partnership", "alliance"],
            "enterprise_sales": ["enterprise", "sales", "account", "quota", "revenue"],
            "ai_ml": ["ai", "ml", "machine learning", "genai", "llm", "model"],
        }
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return None
    
    def _extract_domain_vocabulary(self, role: str, company: str, bullets: List) -> List[str]:
        """Extracts vocabulary related to the inferred domain."""
        text = f"{role} {company} {' '.join([str(b) for b in bullets])}"
        vocab = self._extract_skills_from_text(text)
        return vocab
    
    def _extract_structured_requirements(self, job_description: str) -> Tuple[List[SkillRequirement], List[SkillRequirement]]:
        """Extracts must-have and nice-to-have skills."""
        must_have_skills = []
        nice_to_have_skills = []
        lines = job_description.split('\n')
        current_section_type = "MUST_HAVE"
        
        for line in lines:
            line_lower = line.lower().strip()
            if any(phrase in line_lower for phrase in ["required", "must have", "qualifications", "requirements"]):
                current_section_type = "MUST_HAVE"
                continue
            elif any(phrase in line_lower for phrase in ["preferred", "nice to have", "bonus", "plus", "desired"]):
                current_section_type = "NICE_TO_HAVE"
                continue
            
            if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•') or line.strip().startswith('*')):
                skill_text = line.strip().lstrip('-•*').strip()
                potential_skills = self._extract_skills_from_text(skill_text)
                
                for skill in potential_skills[:2]:
                    skill_req = SkillRequirement(
                        skill=skill,
                        requirement_type=current_section_type,
                        context=skill_text[:200],
                        related_skills=[]
                    )
                    if current_section_type == "MUST_HAVE":
                        must_have_skills.append(skill_req)
                    else:
                        nice_to_have_skills.append(skill_req)
        
        return must_have_skills, nice_to_have_skills
    
    def _cluster_related_skills(self, skills: List[str]) -> List[SkillCluster]:
        """Clusters skills using TF-IDF and cosine similarity."""
        if not SKLEARN_AVAILABLE:
            logging.warning("sklearn not available. Skill clustering disabled.")
            return []
        
        if len(skills) < 2:
            return []
        
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            skill_vectors = vectorizer.fit_transform(skills)
            similarity_matrix = cosine_similarity(skill_vectors)
            
            threshold = 0.3
            clusters: List[SkillCluster] = []
            visited = set()
            
            for i, skill in enumerate(skills):
                if i in visited:
                    continue
                
                similar_indices = [j for j, sim in enumerate(similarity_matrix[i]) 
                                 if sim > threshold and j != i and j not in visited]
                
                if similar_indices:
                    cluster_skills = [skill] + [skills[j] for j in similar_indices]
                    visited.add(i)
                    visited.update(similar_indices)
                    
                    avg_sims = [similarity_matrix[i].mean() for i in [i] + similar_indices]
                    rep_idx = [i] + similar_indices
                    representative = skills[rep_idx[avg_sims.index(max(avg_sims))]]
                    
                    cluster = SkillCluster(
                        cluster_name=f"cluster_{representative}",
                        skills=cluster_skills,
                        representative_skill=representative,
                        confidence=max(avg_sims)
                    )
                    clusters.append(cluster)
            
            return clusters
        
        except Exception as e:
            logging.getLogger(__name__).warning(f"Skill clustering failed: {e}")
            return []
    
    def _infer_implicit_skills(self, explicit_skills: List[str], domain_context: str) -> List[str]:
        """Infers related skills based on explicit skills and domain."""
        implicit_skills = []
        inference_rules = {
            "strategic partnerships": ["relationship management", "executive communication", "negotiation", "GTM strategy"],
            "technology alliances": ["cloud platforms", "AWS", "Azure", "GCP", "ecosystem partnerships"],
            "enterprise sales": ["account management", "quota attainment", "pipeline management", "C-level engagement"],
            "ai/ml": ["model training", "data pipelines", "MLOps", "model deployment"],
        }
        domain_lower = domain_context.lower()
        
        for skill in explicit_skills:
            skill_lower = skill.lower()
            for trigger, inferred in inference_rules.items():
                if trigger in skill_lower or trigger in domain_lower:
                    implicit_skills.extend(inferred)
        
        implicit_skills = list(set(implicit_skills))
        implicit_skills = [s for s in implicit_skills if s.lower() not in [e.lower() for e in explicit_skills]]
        
        return implicit_skills

    def _build_pre_rag_analysis_prompt(self, job_description: str) -> str:
        """Builds the prompt for the pre-RAG analysis (HOP -0.5)."""
        resume_text = json.dumps(self.master_resume.get("professional_experience", []))

        # This prompt is from rag.py, which was correct.
        return f"""You are a hyper-efficient HR intelligence analyst. Your task is to perform a differential analysis between a job description (JD) and a candidate's master resume. Extract key entities and identify the signal gap and overlap.

**JOB DESCRIPTION:**
---
{job_description[:2500]}
---

**CANDIDATE MASTER RESUME (Experience Section):**
---
{resume_text[:2500]}
---

**TASK:**
Analyze both texts and return a single, valid JSON object with the following structure.
1.  **Extract entities from the JD:**
    - `target_company_name`: The name of the hiring company.
    - `precise_role_title`: The exact job title.
    - `key_technologies`: Top 5-7 specific technologies, frameworks, or platforms mentioned (e.g., "Agentic platform", "GenAI engineering", "AWS Bedrock").
    - `core_responsibilities`: Top 3-5 core duties or focus areas (e.g., "post-sales adoption", "customer retention", "strategic partnerships").
2.  **Extract entities from the Resume:**
    - `candidate_skills`: Top 10-15 skills and technologies the candidate emphasizes.
3.  **Perform Differential Analysis:**
    - `signal_gap_keywords`: Keywords from `key_technologies` that are **MISSING** from `candidate_skills`. This is the most important output.
    - `signal_overlap_keywords`: Keywords that appear in **BOTH** `key_technologies` and `candidate_skills`.

**OUTPUT FORMAT (JSON ONLY):**
```json
{{
  "jd_entities": {{
    "target_company_name": "<string>",
    "precise_role_title": "<string>",
    "key_technologies": ["<string>", ...],
    "core_responsibilities": ["<string>", ...]
  }},
  "resume_entities": {{
    "candidate_skills": ["<string>", ...]
  }},
  "differential_analysis": {{
    "signal_gap_keywords": ["<string>", ...],
    "signal_overlap_keywords": ["<string>", ...]
  }}
}}
```"""

    def _execute_pre_rag_analysis(self, job_description: str) -> RAGMission:
        """
        Executes HOP -0.5: Pre-RAG Differential Analysis.
        (Restored from resume_workflow_v16_20.py)
        """
        logger.info("Executing HOP -0.5: Pre-RAG Differential Analysis...")
        
        logger.info("  → Extracting structured requirements...")
        must_have_skills, nice_to_have_skills = self._extract_structured_requirements(job_description)
        logger.info(f"    ✓ Found {len(must_have_skills)} must-have, {len(nice_to_have_skills)} nice-to-have skills")
        
        all_skill_reqs = must_have_skills + nice_to_have_skills
        all_skills = [sr.skill for sr in all_skill_reqs]
        logger.info("  → Clustering related skills...")
        skill_clusters = self._cluster_related_skills(all_skills)
        logger.info(f"    ✓ Identified {len(skill_clusters)} skill clusters")
        
        logger.info("  → Inferring implicit skills from domain context...")
        implicit_skills = self._infer_implicit_skills(all_skills, job_description)
        logger.info(f"    ✓ Inferred {len(implicit_skills)} implicit skills: {implicit_skills[:5]}...")

        prompt = self._build_pre_rag_analysis_prompt(job_description)

        if not self.gemini_client:
             logger.error("FATAL: Gemini client not available for Pre-RAG analysis.")
             raise HopExecutionError("Gemini client not initialized for HOP -0.5.")

        try:
            analysis_json, pre_rag_calls = self.gemini_client.search_and_analyze(prompt, "Pre-RAG Analysis")
            self.total_api_calls_hop0 += pre_rag_calls

        except Exception as e:
             logger.error(f"HOP -0.5 API call failed: {e}", exc_info=True)
             raise HopExecutionError(f"HOP -0.5 failed during API call: {e}") from e

        try:
            jd_entities = analysis_json.get("jd_entities", {})
            differential_analysis = analysis_json.get("differential_analysis", {})
            
            extracted_technologies = jd_entities.get("key_technologies", [])
            
            for cluster in skill_clusters[:3]:
                if cluster.representative_skill not in extracted_technologies:
                    extracted_technologies.append(cluster.representative_skill)
            
            for implicit_skill in implicit_skills[:3]:
                if implicit_skill not in extracted_technologies:
                    extracted_technologies.append(implicit_skill)
            
            logger.info(f"    ✓ Enhanced key_technologies: {len(extracted_technologies)} total")
            
            mission = RAGMission(
                target_company_name=jd_entities.get("target_company_name", "Unknown Company"),
                precise_role_title=jd_entities.get("precise_role_title", "Unknown Role"),
                key_technologies=extracted_technologies,
                core_responsibilities=jd_entities.get("core_responsibilities", []),
                signal_gap_keywords=differential_analysis.get("signal_gap_keywords", []),
                signal_overlap_keywords=differential_analysis.get("signal_overlap_keywords", [])
            )
            
            if not jd_entities or not differential_analysis:
                logger.warning("HOP -0.5: LLM response missing 'jd_entities' or 'differential_analysis'. Used defaults.")
            
            logger.info(f"  ✓ RAG Mission defined. Gap keywords: {mission.signal_gap_keywords}")
            return mission
        except KeyError as ke:
             logger.error(f"HOP -0.5 failed: Missing expected key '{ke}' in API response JSON.")
             logger.debug(f"Received JSON structure sample: {str(analysis_json)[:500]}...")
             raise HopExecutionError(f"HOP -0.5 failed due to missing key '{ke}' in Pre-RAG analysis response.")
        except Exception as e:
             logger.error(f"HOP -0.5 failed during mission creation: {e}", exc_info=True)
             raise HopExecutionError(f"HOP -0.5 failed during mission creation: {e}") from e

    def _analyze_with_resilient_web_search(
        self,
        job_description: str
    ) -> Tuple[ThematicAnalysis, int]:
        """Orchestrates the 4-phase RAG, synthesizing results."""
        telemetry = RAGTelemetry() if self.telemetry_logger else None
        start_time = time.time()
        total_api_calls_this_hop = 0

        if self.cache_manager:
            cached = self.cache_manager.get(job_description)
            if cached:
                logger.info("Using cached web RAG analysis")
                # MODIFICATION: Call static method
                return EnhancedJobDescriptionAnalyzer._dict_to_thematic_analysis(cached), 0

        if not self.web_rag or not self.rag_mission:
             logger.error("FATAL: Web RAG or RAG Mission not available but no fallback exists.")
             raise HopExecutionError("Web RAG initialization failed unexpectedly in resilient search.")

        partial_result = PartialRAGResult()

        # --- Phase 1 ---
        phase1_start = time.time()
        try:
            logger.info("=== Starting Phase 1: Thematic Research ===")
            phase1_results_tuple = self.web_rag.phase1_thematic_research(job_description, self.rag_mission)
            partial_result.phase1_result, calls_p1 = phase1_results_tuple
            total_api_calls_this_hop += calls_p1
            partial_result.phase1_success = True
            if telemetry:
                telemetry.phase1_success = True; telemetry.phase1_attempts = 1
                telemetry.total_search_calls += calls_p1
            logger.info(f"Phase 1: SUCCESS ({calls_p1} calls)")
        except Exception as e:
            logger.warning(f"Phase 1: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 1: {type(e).__name__}")
            if telemetry:
                telemetry.phase1_success = False
                telemetry.errors.append(f"Phase 1: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase1_duration_seconds = time.time() - phase1_start

        # --- Phase 2 ---
        phase2_start = time.time()
        try:
            logger.info("=== Starting Phase 2: Authenticity Patterns ===")
            phase2_results_tuple = self.web_rag.phase2_authenticity_patterns(job_description, self.rag_mission)
            partial_result.phase2_result, calls_p2 = phase2_results_tuple
            total_api_calls_this_hop += calls_p2
            partial_result.phase2_success = True
            if telemetry:
                telemetry.phase2_success = True; telemetry.phase2_attempts = 1
                telemetry.total_search_calls += calls_p2
            logger.info(f"Phase 2: SUCCESS ({calls_p2} calls)")
        except Exception as e:
            logger.warning(f"Phase 2: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 2: {type(e).__name__}")
            if telemetry:
                telemetry.phase2_success = False
                telemetry.errors.append(f"Phase 2: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase2_duration_seconds = time.time() - phase2_start

        # --- Phase 3 ---
        phase3_start = time.time()
        try:
            logger.info("=== Starting Phase 3: Competitive Positioning ===")
            phase3_results_tuple = self.web_rag.phase3_competitive_positioning(job_description, self.rag_mission)
            partial_result.phase3_result, calls_p3 = phase3_results_tuple
            total_api_calls_this_hop += calls_p3
            partial_result.phase3_success = True
            if telemetry:
                telemetry.phase3_success = True; telemetry.phase3_attempts = 1
                telemetry.total_search_calls += calls_p3
            logger.info(f"Phase 3: SUCCESS ({calls_p3} calls)")
        except Exception as e:
            logger.warning(f"Phase 3: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 3: {type(e).__name__}")
            if telemetry:
                telemetry.phase3_success = False
                telemetry.errors.append(f"Phase 3: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase3_duration_seconds = time.time() - phase3_start

        # --- Phase 4 ---
        phase4_start = time.time()
        try:
            logger.info("=== Starting Phase 4: Narrative Mining ===")
            phase4_results_tuple = self.web_rag.phase4_narrative_mining(self.rag_mission)
            partial_result.phase4_result, calls_p4 = phase4_results_tuple
            total_api_calls_this_hop += calls_p4
            partial_result.phase4_success = True
            if telemetry:
                telemetry.phase4_success = True; telemetry.phase4_attempts = 1
                telemetry.total_search_calls += calls_p4
            logger.info(f"Phase 4: SUCCESS ({calls_p4} calls)")
        except Exception as e:
            logger.warning(f"Phase 4: FAILED - {e}", exc_info=False)
            partial_result.failure_reasons.append(f"Phase 4: {type(e).__name__}")
            if telemetry:
                telemetry.phase4_success = False
                telemetry.errors.append(f"Phase 4: {type(e).__name__}: {str(e)[:100]}")
        finally:
             if telemetry: telemetry.phase4_duration_seconds = time.time() - phase4_start

        logger.info(
            f"RAG Phases Complete: "
            f"Success Rate = {partial_result.success_rate:.1%} "
            f"({partial_result.phase1_success}, {partial_result.phase2_success}, "
            f"{partial_result.phase3_success}, {partial_result.phase4_success}) "
            f"Total API Calls (Phases 1-4): {total_api_calls_this_hop}"
        )

        analysis = None

        if partial_result.full_success:
            logger.info("✓ Strategy 1: Full 4-phase RAG successful")

            def _json_roundtrip_convert(data: Any, label: str) -> Dict:
                """Converts complex objects to plain dicts via JSON."""
                try:
                    def default_serializer(o):
                        if hasattr(o, '__dataclass_fields__'):
                            return asdict(o)
                        if isinstance(o, Enum):
                             return o.value
                        try:
                            json.dumps(o) # Test serializability
                            return o
                        except TypeError:
                            return f"__CONVERTED_STR__{str(o)}__"
                    
                    json_str = json.dumps(data, default=default_serializer)
                    plain_data = json.loads(json_str)

                    if isinstance(plain_data, dict):
                        logger.debug(f"Successfully force-converted '{label}' result to plain dict.")
                        return plain_data
                    else:
                        logger.warning(f"JSON roundtrip for '{label}' did not result in a dict (Type: {type(plain_data)}).")
                        return data if isinstance(data, (str, int, float, bool, list, type(None))) else {}
                except Exception as e:
                    logger.error(f"FATAL: Failed to perform JSON roundtrip conversion for '{label}': {e}", exc_info=True)
                    return {"error": "total_conversion_failure", "type": str(type(data))}

            phase1_plain = _json_roundtrip_convert(partial_result.phase1_result, "Phase 1")
            phase2_plain = _json_roundtrip_convert(partial_result.phase2_result, "Phase 2")
            phase3_plain = _json_roundtrip_convert(partial_result.phase3_result, "Phase 3")
            phase4_plain = _json_roundtrip_convert(partial_result.phase4_result, "Phase 4")

            if not all(isinstance(p, dict) for p in [phase1_plain, phase2_plain, phase3_plain, phase4_plain]):
                 logger.error("One or more RAG phase results failed JSON conversion. Cannot synthesize.")
                 raise HopExecutionError("RAG synthesis failed due to data conversion errors after successful phases.")

            analysis = self._synthesize_thematic_analysis(
                phase1_plain,
                phase2_plain,
                phase3_plain,
                phase4_plain,
                job_description
            )
            if telemetry:
                telemetry.full_success = True
                telemetry.success_rate = 1.0

        elif partial_result.any_success:
            logger.error(f"✗ RAG analysis was only partially successful ({partial_result.success_rate:.0%}). Halting workflow.")
            raise HopExecutionError("RAG analysis failed to achieve 100% success across all four phases.")
        else:
            logger.error("✗ All RAG phases failed. Halting workflow.")
            logger.warning(f"Failure reasons: {', '.join(partial_result.failure_reasons)}")
            raise HopExecutionError("All RAG phases failed during execution.")

        # Cache the result if successful
        try:
            if analysis:
                analysis_dict_for_cache = _json_roundtrip_convert(analysis, "Final Analysis")

                if self.cache_manager and isinstance(analysis_dict_for_cache, dict) and "error" not in analysis_dict_for_cache:
                    logger.debug("Attempting to cache the analysis result...")
                    self.cache_manager.set(job_description, analysis_dict_for_cache)
                    logger.debug("Analysis result cached successfully.")
                elif not isinstance(analysis_dict_for_cache, dict) or "error" in analysis_dict_for_cache:
                     logger.warning(f"Skipping cache: Conversion of final analysis to cacheable dict failed.")
            else:
                logger.warning("Skipping cache: Analysis object is None.")

        except Exception as cache_e:
             logger.warning(f"Failed to convert or cache RAG analysis result: {type(cache_e).__name__}: {cache_e}", exc_info=False)

        # Log telemetry
        if telemetry and self.telemetry_logger:
            telemetry.total_duration_seconds = time.time() - start_time
            telemetry.circuit_breaker_triggered = self.gemini_client.circuit_breaker.state == CircuitState.OPEN
            telemetry.failed_api_calls = self.gemini_client.circuit_breaker.failure_count
            telemetry.total_api_calls = total_api_calls_this_hop
            telemetry.total_search_calls = total_api_calls_this_hop
            self.telemetry_logger.log(telemetry)

        logger.info(f"Analysis complete. API calls for RAG phases (1-4): {total_api_calls_this_hop}")
        return analysis, total_api_calls_this_hop

    def _synthesize_thematic_analysis(
        self,
        phase1: Any,
        phase2: Any,
        phase3: Any,
        phase4: Any,
        job_description: str
    ) -> ThematicAnalysis:
        """Combines the 4 phase results into a single ThematicAnalysis object."""
        logger.info("Synthesizing RAG results with weighted analysis...")

        def safe_to_dict(obj: Any) -> Any:
            """Recursively converts objects to dicts."""
            if obj is None: return {}
            if is_dataclass(obj): return asdict(obj)
            if isinstance(obj, dict): return {k: safe_to_dict(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)): return [safe_to_dict(item) for item in obj]
            if isinstance(obj, Enum): return obj.value
            return obj

        logger.debug("Converting phase results to dictionaries (if needed)...")
        phase1_dict = phase1 if isinstance(phase1, dict) else {}
        phase2_dict = phase2 if isinstance(phase2, dict) else {}
        phase3_dict = phase3 if isinstance(phase3, dict) else {}
        phase4_dict = phase4 if isinstance(phase4, dict) else {}
        if not all([phase1_dict, phase2_dict, phase3_dict]):
            logger.warning("One or more essential phase result dictionaries are empty after conversion.")
        logger.debug("Phase conversion check complete.")

        keyword_scores = defaultdict(float)
        weights = getattr(self.config, 'source_weights', {})
        
        # Ensure weights are a dict
        if not isinstance(weights, dict):
            logger.warning(f"source_weights returned {type(weights)} instead of dict. Using defaults.")
            weights = {
                "SOURCE_JD": 1.8, "SOURCE_COMPANY_BLOG": 1.5, "SOURCE_TARGET_EMPLOYEE": 1.4,
                "SOURCE_GARTNER_MQ": 1.2, "SOURCE_PEER_JD": 0.8, "SOURCE_GENERIC_PROFILE": 0.5,
                "LOCAL_NLP": 0.2
            }
        
        # Phase 1: Thematic Analysis
        p1_themes = phase1_dict.get("thematic_analysis", {})
        p1_primary = p1_themes.get("primary_theme", {})
        p1_secondary = p1_themes.get("secondary_themes", [])
        p1_trending = p1_themes.get("trending_keywords", [])

        if isinstance(p1_primary.get("keywords"), list):
            for kw in p1_primary["keywords"]:
                if isinstance(kw, str):
                    keyword_scores[kw] += weights.get("SOURCE_COMPANY_BLOG", 1.5)

        if isinstance(p1_secondary, list):
            for theme in p1_secondary:
                if isinstance(theme, dict) and isinstance(theme.get("keywords"), list):
                    for kw in theme["keywords"]:
                        if isinstance(kw, str):
                            keyword_scores[kw] += weights.get("SOURCE_PEER_JD", 0.8)

        if isinstance(p1_trending, list):
            for kw in p1_trending:
                 if isinstance(kw, str):
                     keyword_scores[kw] += weights.get("SOURCE_PEER_JD", 0.8) * 0.7

        # Phase 2: Authenticity Patterns
        p2_auth = phase2_dict.get("authenticity_patterns", {})
        if not isinstance(p2_auth, dict): p2_auth = {}
        comp_phrasing = p2_auth.get("competency_phrasing", [])
        if isinstance(comp_phrasing, list):
            weight = weights.get("SOURCE_TARGET_EMPLOYEE", 1.4)
            for phrase in comp_phrasing:
                 if isinstance(phrase, str) and ':' in phrase:
                     kw = phrase.split(':', 1)[0].strip()
                     if kw: keyword_scores[kw] += weight

        # Phase 3: Competitive Analysis
        p3_comp = phase3_dict.get("competitive_analysis", {})
        if not isinstance(p3_comp, dict): p3_comp = {}
        p3_diff_kws_data = p3_comp.get("differentiator_keywords", [])
        p3_table_kws_data = p3_comp.get("table_stakes_keywords", [])

        if isinstance(p3_diff_kws_data, list):
            for item in p3_diff_kws_data:
                if isinstance(item, dict) and isinstance(item.get("keyword"), str):
                    kw = item["keyword"]
                    weight = weights.get("SOURCE_GARTNER_MQ", 1.2) * item.get("uniqueness_score", 1.0)
                    keyword_scores[kw] += weight

        if isinstance(p3_table_kws_data, list):
            for item in p3_table_kws_data:
                 if isinstance(item, dict) and isinstance(item.get("keyword"), str):
                     kw = item["keyword"]
                     keyword_scores[kw] += weights.get("SOURCE_PEER_JD", 0.8)

        # Local JD Analysis
        jd_keywords = self.rag_mission.key_technologies if self.rag_mission else []
        if isinstance(jd_keywords, list):
             for kw in jd_keywords:
                  if isinstance(kw, str):
                      keyword_scores[kw] += weights.get("SOURCE_JD", 1.8)

        # Master Resume Index Boost
        if self.master_resume_index:
            logger.info("  ✓ Applying candidate experience weighting from MasterResumeIndex...")
            candidate_boost_applied = 0
            for kw in list(keyword_scores.keys()):
                kw_lower = kw.lower()
                if kw_lower in self.master_resume_index.skill_to_experiences:
                    experiences = self.master_resume_index.skill_to_experiences[kw_lower]
                    recency = self.master_resume_index.recency_scores.get(kw_lower, 0.5)
                    experience_count = len(experiences)
                    count_factor = min(1.5, 1.0 + (experience_count * 0.1))
                    boost_multiplier = 1.3 * (0.5 + recency * 0.5) * count_factor
                    original_score = keyword_scores[kw]
                    keyword_scores[kw] = original_score * boost_multiplier
                    candidate_boost_applied += 1
            logger.info(f"  ✓ Applied candidate experience boost to {candidate_boost_applied} keywords")

        # Synthesize Final Objects
        sorted_keywords = sorted(keyword_scores.items(), key=lambda item: item[1], reverse=True)
        differentiator_keywords_weighted = [{"keyword": kw, "weight": round(score, 3)} for kw, score in sorted_keywords]
        top_differentiators = [kw for kw, score in sorted_keywords[:15]]
        logger.info(f"  ✓ Top 5 weighted keywords: {top_differentiators[:5]}")

        primary_theme = {
            "name": p1_primary.get("name", "Unknown Theme"),
            "confidence": p1_primary.get("confidence", 0.0),
            "keywords": p1_primary.get("keywords", []),
            "market_signal": "STRONG", "source": "WEB_SEARCH"
        }
        secondary_themes = [
            {"name": t.get("name", ""), "relevance": t.get("relevance", 0.0), "keywords": t.get("keywords", []), "source": "WEB_SEARCH"}
            for t in p1_secondary[:5] if isinstance(t, dict)
        ] if isinstance(p1_secondary, list) else []

        role_classification = phase1_dict.get("role_classification", {})
        if not isinstance(role_classification, dict): role_classification = {}
        if self.rag_mission:
             role_classification["precise_role_title"] = self.rag_mission.precise_role_title

        positioning_directives = {
            "apply_industry_first": True,
            "authenticity_positioning_ratio": "0.8:0.2",
            "competitive_edge": phase3_dict.get("positioning_insight", "N/A"),
            "table_stakes_count": len(p3_table_kws_data) if isinstance(p3_table_kws_data, list) else 0,
            "differentiator_count": len(top_differentiators)
        }
        p2_confidence = phase2_dict.get("pattern_confidence", {})
        if not isinstance(p2_confidence, dict): p2_confidence = {}
        authenticity_patterns = {
            "status": "STRONG" if p2_confidence.get("overall", 0.0) > 0.7 else "MODERATE",
            "patterns": p2_auth,
            "confidence": p2_confidence,
            "fallback_applied": False, "fallback_reason": None
        }

        p3_summary = phase3_dict.get("search_summary", {})
        if not isinstance(p3_summary, dict): p3_summary = {}
        competitive_intel = CompetitiveIntelligence(
            peer_jds_analyzed_count=p3_summary.get("peer_jds_analyzed", 0),
            differentiator_keywords=top_differentiators,
            differentiator_keywords_raw=top_differentiators, # Using weighted for both
            differentiator_keywords_weighted=differentiator_keywords_weighted
        )

        p4_success = phase4_dict and phase4_dict.get("problem_solution_narratives") is not None
        signal_quality = (
            p1_primary.get("confidence", 0.0) * 0.35 +
            p2_confidence.get("overall", 0.0) * 0.25 +
            min(1.0, p3_summary.get("peer_jds_analyzed", 0) / 10.0) * 0.25 +
            (0.15 if p4_success else 0.0)
        )

        def get_status(phase_result_dict):
             if phase_result_dict is None: return "FAILED"
             if "thematic_analysis" in phase_result_dict: return "SUCCESS"
             if "authenticity_patterns" in phase_result_dict: return "SUCCESS"
             if "competitive_analysis" in phase_result_dict: return "SUCCESS"
             if "problem_solution_narratives" in phase_result_dict: return "SUCCESS"
             return "SUCCESS" if phase_result_dict else "FAILED"

        retrieval_sources = [
            RetrievalSource(id="PHASE1_THEMATIC", type="Web_RAG", confidence=p1_primary.get("confidence", 0.0), status=get_status(phase1_dict), specific_source="SOURCE_COMPANY_BLOG"),
            RetrievalSource(id="PHASE2_AUTHENTICITY", type="Web_RAG", confidence=p2_confidence.get("overall", 0.0), status=get_status(phase2_dict), specific_source="SOURCE_TARGET_EMPLOYEE"),
            RetrievalSource(id="PHASE3_COMPETITIVE", type="Web_RAG", confidence=min(1.0, p3_summary.get("peer_jds_analyzed", 0) / 10.0), status=get_status(phase3_dict), specific_source="SOURCE_GARTNER_MQ"),
            RetrievalSource(id="PHASE4_NARRATIVE", type="Web_RAG", confidence=1.0 if p4_success else 0.0, status=get_status(phase4_dict), specific_source="SOURCE_NARRATIVE_MINING")
        ]

        problem_solution_narratives = phase4_dict.get("problem_solution_narratives") if p4_success else None

        return ThematicAnalysis(
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            role_classification=role_classification,
            positioning_directives=positioning_directives,
            authenticity_patterns=authenticity_patterns,
            competitive_intelligence=competitive_intel,
            problem_solution_narratives=problem_solution_narratives,
            signal_quality_score=signal_quality,
            retrieval_method="WEB_SEARCH_RAG",
            retrieval_sources=retrieval_sources,
            weighting_formula={"description": "Weighted Synthesis v15.57", "weights": weights}
        )

    # MODIFICATION: Make _dict_to_thematic_analysis a @staticmethod
    # This allows StateSerializer to call it without an instance
    @staticmethod
    def _dict_to_thematic_analysis(data: Dict) -> ThematicAnalysis:
        """Converts a cached dictionary back into a ThematicAnalysis object."""
        comp_intel_data = data.get("competitive_intelligence")
        comp_intel = None

        if isinstance(comp_intel_data, dict):
            try:
                comp_intel = CompetitiveIntelligence(**comp_intel_data)
            except TypeError as e:
                logger.warning(f"Error reconstructing CompetitiveIntelligence from cached data: {e}. Initializing default.")
                comp_intel = CompetitiveIntelligence()
        else:
            comp_intel = CompetitiveIntelligence()

        retrieval_sources = []
        cached_sources = data.get("retrieval_sources", [])
        if isinstance(cached_sources, list):
            for src_data in cached_sources:
                if isinstance(src_data, dict):
                    try:
                        retrieval_sources.append(RetrievalSource(**src_data))
                    except TypeError as e:
                         logger.warning(f"Error reconstructing RetrievalSource from cached data: {e}.")
        
        auth_patterns = data.get("authenticity_patterns", {})
        if not isinstance(auth_patterns, dict):
             auth_patterns = {}

        return ThematicAnalysis(
            primary_theme=data.get("primary_theme", {}),
            secondary_themes=data.get("secondary_themes", []),
            role_classification=data.get("role_classification", {}),
            positioning_directives=data.get("positioning_directives", {}),
            authenticity_patterns=auth_patterns,
            competitive_intelligence=comp_intel,
            signal_quality_score=data.get("signal_quality_score", 0.0),
            retrieval_method=data.get("retrieval_method", "UNKNOWN_CACHE"),
            retrieval_sources=retrieval_sources,
            problem_solution_narratives=data.get("problem_solution_narratives"),
            weighting_formula=data.get("weighting_formula")
        )