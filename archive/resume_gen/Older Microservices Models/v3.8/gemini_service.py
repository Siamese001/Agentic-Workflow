# File: gemini_service.py
# Version: 2.0.2 (Patched) - Production Ready (Config-Managed Constants)
# Unified Gemini API Service - Hardened for Production
# Centralizes all Gemini API call logic for the Resume Generation Engine

import json
import logging
import os
import re
import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Robust import handling for google-generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    import warnings
    warnings.warn(
        "google-generativeai package not installed. "
        "Install with: pip install google-generativeai"
    )
    GEMINI_AVAILABLE = False
    genai = None

from models_RES import HopExecutionError, ReasoningConfig
from utils_RES_v3_8 import text_utils, reasoning_config_to_api_params, enhance_system_prompt_with_reasoning

# --- FIX: Import ALL constants from config_RES_v3_8 ---
from config_RES_v3_8 import (
    DEFAULT_GENERATION_TEMPERATURE, 
    DEFAULT_SYNTHESIS_TEMPERATURE,
    DEFAULT_MAX_RETRIES,  # <-- IMPORTED
    DEFAULT_RETRY_DELAY   # <-- IMPORTED
)
# --- END FIX ---

logger = logging.getLogger(__name__)


# Configuration constants (no magic numbers)
# --- FIX: Removed duplicated constants ---
# DEFAULT_MAX_RETRIES = 3 (REMOVED)
# DEFAULT_RETRY_DELAY = 2.0 (REMOVED)
# --- END FIX ---
DEFAULT_MAX_TOKENS = 8192
SAFETY_THRESHOLD = "BLOCK_NONE"
API_TIMEOUT = 30  # seconds


class APICallStatus(Enum):
    """Status codes for API calls"""
    SUCCESS = "success"
    RATE_LIMITED = "rate_limited"
    SAFETY_BLOCKED = "safety_blocked"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class APICallMetrics:
    """Metrics for API call tracking"""
    call_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_tokens_used: int = 0
    total_latency_ms: float = 0
    safety_blocks: int = 0
    rate_limits: int = 0


class GeminiService:
    """
    Production-ready Gemini API service with comprehensive error handling.
    
    Features:
    - Automatic retry with exponential backoff
    - Rate limiting protection
    - Safety rating handling
    - Response validation and integrity checking
    - Comprehensive metrics tracking
    - Fallback mechanisms for failures
    """
    
    def __init__(self, 
                 default_model: str = "gemini-2.0-flash-exp",
                 max_retries: Optional[int] = None,
                 retry_delay: Optional[float] = None):
        """
        Initialize the Gemini service with production configurations.
        
        Args:
            default_model: Default model to use if not specified in call
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.default_model = default_model
        # --- FIX: (Triplicated Constants) Use imported global constants ---
        self.max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        self.retry_delay = retry_delay if retry_delay is not None else DEFAULT_RETRY_DELAY
        self.metrics = APICallMetrics()
        
        # Validate environment
        self._validate_environment()
        
        logger.info(f"✓ GeminiService initialized with model: {default_model}")
        logger.info(f"  Max retries: {max_retries}, Base retry delay: {retry_delay}s")
    
    def _validate_environment(self) -> None:
        """
        Validate that the environment is properly configured.
        
        Raises:
            RuntimeError: If environment is not properly configured
        """
        if not GEMINI_AVAILABLE:
            raise RuntimeError(
                "google-generativeai package not available. "
                "Install with: pip install google-generativeai"
            )
        
        # Validate API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Try to get from genai config
            try:
                if hasattr(genai, '_config'):
                    api_key = genai._config.api_key
            except:
                pass
            
            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY environment variable not set. "
                    "Set it with: export GEMINI_API_KEY='your-api-key'"
                )
        
        # Configure genai if needed
        if not hasattr(genai, '_config') or not genai._config.api_key:
            genai.configure(api_key=api_key)
    
    def call_api(
        self,
        prompt: str,
        section_id: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        reasoning_config: Optional[ReasoningConfig] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        return_full_response: bool = False,
        validate_response: bool = True
    ) -> Tuple[str, int, Optional[Any]]: # <-- FIX: (Flawed API) Return 3 values
        """
        Execute a production-ready Gemini API call with comprehensive error handling.
        
        Args:
            prompt: The user prompt (required, cannot be empty)
            section_id: Identifier for logging and tracking
            model: Model name override
            system_prompt: Optional system prompt
            reasoning_config: Reasoning configuration
            temperature: Temperature override (0.0-1.0)
            max_tokens: Max output tokens
            return_full_response: Return full API response object
            validate_response: Validate response for mock/placeholder data
            
        Returns:
            Tuple of (generated_text, api_calls_made, full_response)
            
        Raises:
            HopExecutionError: If API call fails after all retries
            ValueError: If input validation fails
        """
        # Input validation
        if not prompt or not prompt.strip():
            raise ValueError(f"{section_id}: Prompt cannot be empty")
        
        if not section_id:
            raise ValueError("section_id is required for tracking")
        
        # Validate no mock data in prompt
        self._validate_no_mock_data(prompt, section_id)
        
        # Configure parameters
        model_name = model or self.default_model
        # --- FIX: Use imported DEFAULT_GENERATION_TEMPERATURE ---
        temp = temperature if temperature is not None else DEFAULT_GENERATION_TEMPERATURE
        max_tok = max_tokens or DEFAULT_MAX_TOKENS
        
        # Validate temperature range
        if not 0.0 <= temp <= 1.0:
            logger.warning(f"{section_id}: Temperature {temp} out of range, using default")
            # --- FIX: Use imported DEFAULT_GENERATION_TEMPERATURE ---
            temp = DEFAULT_GENERATION_TEMPERATURE
        
        # Apply reasoning configuration
        if reasoning_config:
            # --- FIX: Pass section_id to reasoning_config_to_api_params ---
            api_params = reasoning_config_to_api_params(reasoning_config, section_id)
            if system_prompt:
                system_prompt = enhance_system_prompt_with_reasoning(
                    system_prompt, reasoning_config
                )
        else:
            api_params = {}
        
        # Execute with retry logic
        for attempt in range(self.max_retries):
            try:
                response, status = self._execute_api_call(
                    prompt=prompt,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    temperature=temp,
                    max_tokens=max_tok,
                    section_id=section_id,
                    api_params=api_params
                )
                
                if status == APICallStatus.SUCCESS:
                    # Extract and validate text
                    text = self._extract_text(response)
                    
                    if validate_response:
                        self._validate_response_integrity(text, section_id)
                    
                    # Update metrics
                    self.metrics.call_count += 1
                    self.metrics.success_count += 1
                    
                    # Return results
                    full_resp = response if return_full_response else None
                    return text, 1, full_resp
                
                elif status == APICallStatus.RATE_LIMITED:
                    self.metrics.rate_limits += 1
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"{section_id}: Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                elif status == APICallStatus.SAFETY_BLOCKED:
                    self.metrics.safety_blocks += 1
                    raise HopExecutionError(
                        f"{section_id}: Response blocked by safety filters. "
                        f"Please review prompt content."
                    )
                
                else:
                    # Other errors - retry with backoff
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        logger.warning(f"{section_id}: Attempt {attempt + 1} failed, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    
            except Exception as e:
                self.metrics.error_count += 1
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"{section_id}: Exception on attempt {attempt + 1}: {e}")
                    logger.warning(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"{section_id}: All retry attempts exhausted")
                    raise HopExecutionError(
                        f"{section_id}: API call failed after {self.max_retries} attempts: {str(e)}"
                    )
        
        # Should not reach here
        raise HopExecutionError(
            f"{section_id}: API call failed after all retries"
        )
    
    def call_with_self_consistency(
        self,
        prompt: str,
        section_id: str,
        num_runs: int = 3,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        reasoning_config: Optional[ReasoningConfig] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        synthesis_prompt: Optional[str] = None
    ) -> Tuple[str, int, List[str]]:
        """
        Execute multiple API calls for self-consistency with synthesis.
        
        Args:
            prompt: The user prompt
            section_id: Identifier for logging
            num_runs: Number of self-consistency runs
            model: Model name override
            system_prompt: Optional system prompt
            reasoning_config: Reasoning configuration
            temperature: Temperature for generation
            max_tokens: Max output tokens
            synthesis_prompt: Custom prompt for synthesis
            
        Returns:
            Tuple of (synthesized_result, total_api_calls, individual_responses)
        """
        if num_runs < 1:
            raise ValueError(f"{section_id}: num_runs must be at least 1")
        
        if num_runs == 1:
            # Single run - no synthesis needed
            result, calls, _ = self.call_api( # <-- FIX: Unpack 3 values
                prompt=prompt,
                section_id=f"{section_id}_run_1",
                model=model,
                system_prompt=system_prompt,
                reasoning_config=reasoning_config,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return result, calls, [result]
        
        # Multiple runs for self-consistency
        responses = []
        total_calls = 0
        
        for i in range(num_runs):
            try:
                response, calls, _ = self.call_api( # <-- FIX: Unpack 3 values
                    prompt=prompt,
                    section_id=f"{section_id}_run_{i+1}",
                    model=model,
                    system_prompt=system_prompt,
                    reasoning_config=reasoning_config,
                    temperature=temperature or 1.0,  # Higher temp (1.0) for diversity
                    max_tokens=max_tokens
                )
                responses.append(response)
                total_calls += calls
                
            except Exception as e:
                logger.error(f"{section_id}: Self-consistency run {i+1} failed: {e}")
                # Continue with other runs
                continue
        
        if not responses:
            raise HopExecutionError(
                f"{section_id}: All self-consistency runs failed"
            )
        
        # Synthesize results
        if len(responses) == 1:
            return responses[0], total_calls, responses
        
        synthesized = self._synthesize_responses(
            responses=responses,
            section_id=f"{section_id}_synthesis",
            synthesis_prompt=synthesis_prompt,
            model=model
        )
        
        return synthesized, total_calls + 1, responses
    
    def _execute_api_call(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        section_id: str,
        api_params: Dict[str, Any]
    ) -> Tuple[Any, APICallStatus]:
        """
        Execute a single API call with proper configuration.
        
        Returns:
            Tuple of (response_object, status)
        """
        start_time = time.time()
        
        try:
            # Configure model
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "top_p": api_params.get("top_p", 1.0),
                    "top_k": api_params.get("top_k", 40),
                },
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT": SAFETY_THRESHOLD,
                    "HARM_CATEGORY_HATE_SPEECH": SAFETY_THRESHOLD,
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": SAFETY_THRESHOLD,
                    "HARM_CATEGORY_DANGEROUS_CONTENT": SAFETY_THRESHOLD,
                }
            )
            
            # Prepare prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Generate
            response = model.generate_content(full_prompt)
            
            # Check for safety blocking
            if not response.parts:
                return None, APICallStatus.SAFETY_BLOCKED
            
            # Track latency
            latency = (time.time() - start_time) * 1000
            self.metrics.total_latency_ms += latency
            
            return response, APICallStatus.SUCCESS
            
        except Exception as e:
            error_str = str(e).lower()
            
            if "quota" in error_str or "rate" in error_str:
                return None, APICallStatus.RATE_LIMITED
            elif "safety" in error_str or "blocked" in error_str:
                return None, APICallStatus.SAFETY_BLOCKED
            else:
                logger.error(f"{section_id}: API error: {e}")
                return None, APICallStatus.ERROR
    
    def _extract_text(self, response: Any) -> str:
        """
        Extract clean text from API response.
        
        Args:
            response: API response object
            
        Returns:
            Cleaned text string
        """
        if not response or not response.parts:
            return ""
        
        # Extract text from all parts
        text_parts = []
        for part in response.parts:
            if hasattr(part, 'text'):
                text_parts.append(part.text)
        
        text = " ".join(text_parts)
        
        # Clean up text
        # --- FIX: Call text_utils.strip_markdown_fences ---
        text = text_utils.strip_markdown_fences(text)

        # --- FIX: (Conflicting Logic) Removed redundant stripping ---
        return text.strip()
    
    def _synthesize_responses(
        self,
        responses: List[str],
        section_id: str,
        synthesis_prompt: Optional[str],
        model: Optional[str]
    ) -> str:
        """
        Synthesize multiple responses into a single coherent response.
        
        Args:
            responses: List of response texts
            section_id: Identifier for logging
            synthesis_prompt: Custom synthesis prompt
            model: Model to use for synthesis
            
        Returns:
            Synthesized response text
        """
        if not synthesis_prompt:
            synthesis_prompt = f"""You are a response synthesizer.
You have received {len(responses)} different responses to the same prompt.
Your task is to create a single, high-quality response that incorporates the best elements from all responses.

RESPONSES TO SYNTHESIZE:
{chr(10).join([f"Response {i+1}:\n{r}" for i, r in enumerate(responses)])}

Create a synthesized response that:
1. Captures the key points from all responses
2. Resolves any contradictions by choosing the most consistent information
3. Maintains coherence and flow
4. Does not mention that this is a synthesis

SYNTHESIZED RESPONSE:"""
        
        synthesized, _, _ = self.call_api( # <-- FIX: Unpack 3 values
            prompt=synthesis_prompt,
            section_id=section_id,
            model=model,
            # --- FIX: Use imported DEFAULT_SYNTHESIS_TEMPERATURE ---
            temperature=DEFAULT_SYNTHESIS_TEMPERATURE,
            validate_response=True
        )
        
        return synthesized
    
    def _validate_no_mock_data(self, text: str, context: str) -> None:
        """
        Validate that text contains no mock/placeholder data.
        
        Args:
            text: Text to validate
            context: Context for error messages
            
        Raises:
            ValueError: If mock data is detected
        """
        mock_indicators = [
            "[placeholder]", "[PLACEHOLDER]",
            "[your name]", "[YOUR NAME]",
            "[company name]", "[COMPANY NAME]",
            "[TODO]", "[FIXME]",
            "dummy_", "DUMMY_",
            "test_data", "TEST_DATA",
            "mock_response", "MOCK_RESPONSE"
        ]
        
        text_lower = text.lower()
        for indicator in mock_indicators:
            if indicator.lower() in text_lower:
                raise ValueError(
                    f"{context}: Mock/placeholder data detected: '{indicator}'. "
                    f"Production system cannot process test data."
                )
    
    def _validate_response_integrity(self, text: str, context: str) -> None:
        """
        Validate response doesn't contain problematic content.
        
        Args:
            text: Response text to validate
            context: Context for error messages
            
        Raises:
            ValueError: If response fails validation
        """
        # Check for empty response
        if not text or not text.strip():
            raise ValueError(f"{context}: Empty response received")
        
        # Check for mock data
        self._validate_no_mock_data(text, context)
        
        # Check for obvious errors
        error_patterns = [
            "error:", "ERROR:",
            "failed to", "Failed to",
            "could not generate", "Could not generate",
            "I cannot", "I can't"
        ]
        
        for pattern in error_patterns:
            if pattern in text:
                logger.warning(f"{context}: Response contains potential error: '{pattern}'")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics for the service.
        
        Returns:
            Dictionary of metrics
        """
        success_rate = (
            self.metrics.success_count / self.metrics.call_count 
            if self.metrics.call_count > 0 else 0
        )
        
        avg_latency = (
            self.metrics.total_latency_ms / self.metrics.success_count
            if self.metrics.success_count > 0 else 0
        )
        
        return {
            "total_calls": self.metrics.call_count,
            "successful_calls": self.metrics.success_count,
            "failed_calls": self.metrics.error_count,
            "success_rate": f"{success_rate * 100:.1f}%",
            "average_latency_ms": f"{avg_latency:.1f}",
            "safety_blocks": self.metrics.safety_blocks,
            "rate_limits": self.metrics.rate_limits,
            "total_tokens_used": self.metrics.total_tokens_used
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        self.metrics = APICallMetrics()
        logger.info("GeminiService metrics reset")
    
    def call_api_with_json_response(
        self,
        prompt: str,
        # --- FIX: generation_config is not a valid parameter ---
        # Replaced with standard parameters
        section_id: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        # --- END FIX ---
        retry_count: int = 3,
    ) -> Tuple[dict, int, Any]: # <-- FIX: Return tuple
        """
        Calls the Gemini API and ensures the response is valid JSON.
        This is the missing method required by rag_RES_v3_8.py.
        """
        total_calls = 0
        for attempt in range(retry_count):
            try:
                # --- FIX: Use imported default temp ---
                temp = temperature if temperature is not None else DEFAULT_GENERATION_TEMPERATURE
                
                # Make the API call
                raw_response, calls, full_resp = self.call_api( # <-- FIX: Unpack 3 values
                    prompt=prompt,
                    section_id=section_id,
                    temperature=temp,
                    max_tokens=max_tokens,
                    validate_response=False
                )
                total_calls += calls
                # --- END FIX ---
                
                # Basic cleanup to find JSON block
                json_match = re.search(r"```json\n(.*?)\n```", raw_response, re.DOTALL)
                if not json_match:
                    json_match = re.search(r"({.*})", raw_response, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                    # --- FIX: Return tuple ---
                    return json.loads(json_str), total_calls, full_resp
                else:
                    logger.warning(f"No JSON found in response, attempt {attempt + 1}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode failed: {e}. Response: {raw_response}")
            except Exception as e:
                logger.error(f"API call failed: {e}")

        raise ValueError(f"Failed to get valid JSON response after {retry_count} attempts.")


# Singleton instance for global access
_gemini_service_instance = None


def get_gemini_service(
    default_model: str = "gemini-2.0-flash-exp",
    force_new: bool = False
) -> GeminiService:
    """
    Get or create the global GeminiService instance.
    
    Args:
        default_model: Default model to use
        force_new: Force creation of new instance
        
    Returns:
        GeminiService instance
    """
    global _gemini_service_instance
    
    if force_new or _gemini_service_instance is None:
        _gemini_service_instance = GeminiService(default_model=default_model)
    
    return _gemini_service_instance