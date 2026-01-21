# File: llm_clients.py
# Description: Centralized LLM client for all generative AI calls

__version__ = "12.0"

import google.generativeai as genai
import os
from utils_LIC import CircuitBreaker, CircuitBreakerOpenError

class GeminiLLMClient:
    """
    Centralized client for all Gemini API calls with circuit breaker protection
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        self.circuit_breaker = circuit_breaker

    def _execute_llm_call(self, prompt: str) -> str:
        """Execute the actual LLM API call"""
        response = self.model.generate_content(prompt)
        return response.text

    def generate(self, prompt: str) -> str:
        """
        Generate content with circuit breaker protection

        Args:
            prompt: The prompt string to send to Gemini

        Returns:
            Generated text response

        Raises:
            Exception: If API call fails
            CircuitBreakerOpenError: If circuit breaker is OPEN
        """
        try:
            return self.circuit_breaker.call(self._execute_llm_call, prompt)
        except Exception as e:
            raise Exception(f"Gemini API call failed: {e}")
