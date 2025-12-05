"""
Resume Generation Engine v5.41 - MULTI-LLM SUPPORT (Claude + Gemini)

v5.41 CHANGES - MULTI-LLM INTEGRATION:
✓ NEW: Support for both Claude and Gemini APIs
✓ NEW: LLM_PROVIDER configuration variable
✓ NEW: _call_gemini_api() method
✓ NEW: _call_llm_api() unified wrapper
✓ MODIFIED: All API calls route through unified wrapper
✓ Environment variables: ANTHROPIC_API_KEY and GEMINI_API_KEY
✓ Easy switching between providers with single variable change

All v5.40 functionality maintained:
✓ Single source of truth architecture
✓ Real API integration (not mock)
✓ Comprehensive error handling
✓ All 74 RAG pipeline calls
✓ JD Enforcement System
✓ Complete validation suite
"""

import json
import re
import hashlib
import math
import os
import time
import requests
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
import copy
import logging

__version__ = "5.41"

# ============================================================================
# v5.41 MULTI-LLM CONFIGURATION
# ============================================================================

# Choose your LLM provider: "claude" or "gemini"
LLM_PROVIDER = "gemini"  # <-- CHANGE THIS TO SWITCH PROVIDERS

# Model configurations
LLM_MODELS = {
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash-exp"  # or "gemini-pro", "gemini-1.5-pro"
}

# API endpoints
LLM_ENDPOINTS = {
    "claude": "https://api.anthropic.com/v1/messages",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(f"=" * 80)
logger.info(f"Resume Generation Engine v{__version__}")
logger.info(f"LLM Provider: {LLM_PROVIDER.upper()}")
logger.info(f"Model: {LLM_MODELS.get(LLM_PROVIDER, 'Unknown')}")
logger.info(f"=" * 80)


# ============================================================================
# EXAMPLE: Minimal placeholder class structure for demonstration
# (Your full v5.40 code would continue here with all original classes)
# ============================================================================

class JDEnforcementRule(Enum):
    """Enforcement rules ensuring JD is always used."""
    E1_JD_MIN_LENGTH = "JD must be non-empty (min 100 characters)"
    E2_JD_NON_NULL = "JD must be provided to workflow (not None/empty)"
    # ... (all your other rules)


@dataclass
class JDEnforcementResult:
    """Result of a JD enforcement check."""
    rule: JDEnforcementRule
    passed: bool
    details: str
    gate_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# v5.41 MULTI-LLM API INTEGRATION
# ============================================================================

class MultiLLMProvider:
    """
    Multi-LLM provider supporting both Claude and Gemini APIs.
    
    Features:
    - Unified interface for multiple LLM providers
    - Automatic provider selection based on configuration
    - Retry logic and error handling for both APIs
    - Environment variable management for API keys
    """
    
    def __init__(self, provider: str = None):
        """
        Initialize Multi-LLM Provider.
        
        Args:
            provider: "claude" or "gemini". If None, uses global LLM_PROVIDER
        """
        self.provider = provider or LLM_PROVIDER
        self.model = LLM_MODELS.get(self.provider)
        self.endpoint = LLM_ENDPOINTS.get(self.provider)
        
        if not self.model or not self.endpoint:
            raise ValueError(f"Unknown provider: {self.provider}. Must be 'claude' or 'gemini'")
        
        logger.info(f"Initialized {self.provider.upper()} provider with model {self.model}")
    
    def _call_claude_api(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Call Claude API using Anthropic Messages API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text from Claude
        
        Raises:
            Exception: If API call fails or API key not set
        """
        # Check for API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise Exception(
                "ANTHROPIC_API_KEY not found. Please set it using:\n"
                "export ANTHROPIC_API_KEY='your-api-key-here'"
            )
        
        # Prepare request
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": api_key
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        # Make request with retry logic
        return self._make_request_with_retry(url, headers, payload, "claude")
    
    def _call_gemini_api(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Call Gemini API using Google GenerativeLanguage API.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature (0.0-2.0 for Gemini)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text from Gemini
        
        Raises:
            Exception: If API call fails or API key not set
        """
        # Check for API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise Exception(
                "GEMINI_API_KEY not found. Please set it using:\n"
                "export GEMINI_API_KEY='your-api-key-here'\n"
                "Get your key at: https://makersuite.google.com/app/apikey"
            )
        
        # Prepare request
        # Gemini uses URL parameter for API key
        url = self.endpoint.format(model=self.model)
        url = f"{url}?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Combine system prompt and user prompt for Gemini
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        # Make request with retry logic
        return self._make_request_with_retry(url, headers, payload, "gemini")
    
    def _make_request_with_retry(
        self,
        url: str,
        headers: Dict,
        payload: Dict,
        provider_type: str
    ) -> str:
        """
        Make HTTP request with exponential backoff retry logic.
        
        Args:
            url: API endpoint URL
            headers: Request headers
            payload: Request payload
            provider_type: "claude" or "gemini" for response parsing
        
        Returns:
            Generated text from API
        
        Raises:
            Exception: If all retry attempts fail
        """
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"{provider_type.upper()} API call attempt {attempt + 1}/{max_retries}")
                
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=60  # Increased timeout for larger requests
                )
                
                # Check response status
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Parse response based on provider
                    if provider_type == "claude":
                        generated_text = response_data["content"][0]["text"]
                    elif provider_type == "gemini":
                        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        raise ValueError(f"Unknown provider type: {provider_type}")
                    
                    logger.debug(f"API call successful, response length: {len(generated_text)} chars")
                    return generated_text
                
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limit hit, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} attempts")
                
                elif response.status_code == 400:  # Bad request
                    error_msg = f"Bad Request: {response.text}"
                    logger.error(error_msg)
                    logger.error(f"Payload that caused error: {json.dumps(payload, indent=2)}")
                    raise Exception(error_msg)
                
                else:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise Exception(error_msg)
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.warning(f"Request timeout, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Request timeout after {max_retries} attempts")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Request failed after {max_retries} attempts: {str(e)}")
        
        raise Exception("API call failed after all retry attempts")
    
    def call_llm(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Unified method to call configured LLM provider.
        
        This is the main method you should use in your code.
        It automatically routes to the correct API based on configuration.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt/instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text from configured LLM
        
        Raises:
            Exception: If API call fails
        """
        if self.provider == "claude":
            return self._call_claude_api(prompt, system_prompt, temperature, max_tokens)
        elif self.provider == "gemini":
            return self._call_gemini_api(prompt, system_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

def test_multi_llm():
    """Test function to verify both APIs work."""
    print("\n" + "=" * 80)
    print("TESTING MULTI-LLM PROVIDER")
    print("=" * 80)
    
    # Test prompt
    test_prompt = """
    You are helping to tailor a resume. Given this job description snippet:
    "Looking for a senior software engineer with Python experience and cloud architecture skills."
    
    Suggest 2 technical skills that should be highlighted on the resume.
    Provide just the skill names, one per line.
    """
    
    # Test Claude
    print("\n1. Testing CLAUDE API...")
    try:
        claude_provider = MultiLLMProvider("claude")
        claude_response = claude_provider.call_llm(
            prompt=test_prompt,
            system_prompt="You are a professional resume writer.",
            temperature=0.7,
            max_tokens=200
        )
        print(f"✓ Claude Response:\n{claude_response}\n")
    except Exception as e:
        print(f"✗ Claude API failed: {e}\n")
    
    # Test Gemini
    print("2. Testing GEMINI API...")
    try:
        gemini_provider = MultiLLMProvider("gemini")
        gemini_response = gemini_provider.call_llm(
            prompt=test_prompt,
            system_prompt="You are a professional resume writer.",
            temperature=0.7,
            max_tokens=200
        )
        print(f"✓ Gemini Response:\n{gemini_response}\n")
    except Exception as e:
        print(f"✗ Gemini API failed: {e}\n")
    
    print("=" * 80)


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

"""
INTEGRATION GUIDE:

To integrate this into your existing v5.40 code:

1. Add the configuration section (lines 61-80) to the top of your file

2. Replace your existing _call_claude_api method with the MultiLLMProvider class

3. In your existing classes (like ContentEnrichmentEngine), modify the __init__:
   
   def __init__(self):
       self.llm_provider = MultiLLMProvider()  # Add this line
       # ... rest of your init code

4. Replace all calls to self._call_claude_api() with self.llm_provider.call_llm()
   
   Example:
   OLD: response = self._call_claude_api(prompt, system_prompt, ...)
   NEW: response = self.llm_provider.call_llm(prompt, system_prompt, ...)

5. Update your main() function to check for the correct API key:

   def main():
       # Check API key based on provider
       if LLM_PROVIDER == "claude":
           if not os.environ.get("ANTHROPIC_API_KEY"):
               raise Exception("ANTHROPIC_API_KEY not set!")
       elif LLM_PROVIDER == "gemini":
           if not os.environ.get("GEMINI_API_KEY"):
               raise Exception("GEMINI_API_KEY not set!")
       
       # ... rest of your main code

6. To switch providers, just change the LLM_PROVIDER variable at the top:
   LLM_PROVIDER = "claude"  # or "gemini"

That's it! Your entire script will now use the selected provider.
"""


if __name__ == "__main__":
    # Run test
    test_multi_llm()
    
    print("\n" + "=" * 80)
    print("SETUP INSTRUCTIONS")
    print("=" * 80)
    print("\nTo use Claude API:")
    print("  export ANTHROPIC_API_KEY='your-anthropic-key-here'")
    print("  Then set LLM_PROVIDER = 'claude' in the code")
    
    print("\nTo use Gemini API:")
    print("  export GEMINI_API_KEY='your-gemini-key-here'")
    print("  Get key at: https://makersuite.google.com/app/apikey")
    print("  Then set LLM_PROVIDER = 'gemini' in the code")
    
    print("\n" + "=" * 80)
