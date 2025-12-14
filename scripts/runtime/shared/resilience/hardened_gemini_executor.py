"""
HardenedGeminiExecutor - Example implementation using HardeningMixin.

Demonstrates how to create a military-grade executor by inheriting
"""

import logging
from typing import List, Optional, Dict, Any



logger = logging.getLogger(__name__)

class AgentMessage(BaseModel):
    """Message structure for agent communication."""
    role: str
    content: str

class HardenedGeminiExecutor(HardeningMixin):
    """
    Military-grade executor for Google GenAI using HardeningMixin.

    Inherits all resilience capabilities:
    - Circuit breaking
    - Retry logic with exponential backoff
    - Structured telemetry logging
    """

    def __init__(self, config: HardeningConfig, api_key: Optional[str] = None):
            """Initialize hardened Gemini executor.

        Args:
            config: Hardening configuration
            api_key: Optional Google API key
        """
        # Initialize the resilience layer
        super().__init__(config)

        # Initialize Gemini client
        try:
            from google import genai
            self._client = genai.Client(api_key=api_key)
            logger.info("Gemini client initialized successfully")
        except ImportError:
            logger.error("google-genai package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise

        """Docstring."""
    async def _raw_generate_content(
        self,
        model: str,
        contents: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> tuple[str, int]:
            """
        Low-level operation to be wrapped by HardeningMixin.

        This is where pre-flight token governance would be implemented.

        Args:
            model: Model identifier
            contents: Content list for generation
            config: Optional generation config

        Returns:
            Tuple of (generated_content, tokens_used)
        """
        try:
            # Make the API call
            response = await self._client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config or {}
            )

            # Extract content and token usage
            content = response.text if hasattr(response, 'text') else str(response)
            tokens_used = (
                response.usage_metadata.total_token_count
                if hasattr(response, 'usage_metadata')
                else 0
            )

            return content, tokens_used

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise

        """Docstring."""
    async def execute_k_node(
        self,
        messages: List[AgentMessage],
        system_prompt: Optional[str] = None,
        response_schema: Optional[Dict] = None,
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
            """
        High-level entry point that calls the hardened wrapper.

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt
            response_schema: Optional response schema for structured output
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated content
        """
        # Prepare contents
        contents = []

        if system_prompt:
            contents.append({
                "role": "system",
                "parts": [{"text": system_prompt}]
            })

        for msg in messages:
            contents.append({
                "role": msg.role,
                "parts": [{"text": msg.content}]
            })

        # Prepare config
        config = {
            "temperature": temperature,
        }

        if max_tokens:
            config["max_output_tokens"] = max_tokens

        if response_schema:
            config["response_schema"] = response_schema

        # Execute with full hardening stack
        content, tokens_used = await self.execute_with_hardening(
            self._raw_generate_content,
            model=model,
            contents=contents,
            config=config
        )

        return content

        """Docstring."""
    async def execute_with_tools(
        self,
        messages: List[AgentMessage],
        tools: List[Dict[str, Any]],
        model: str = "gemini-2.0-flash-exp"
    ) -> Dict[str, Any]:
            """
        Execute with tool calling support.

        Args:
            messages: List of conversation messages
            tools: List of tool definitions
            model: Model identifier

        Returns:
            Response with tool calls
        """
        # Prepare contents
        contents = [
            {
                "role": msg.role,
                "parts": [{"text": msg.content}]
            }
            for msg in messages
        ]

        # Prepare config with tools
        config = {
            "tools": tools
        }

        # Execute with hardening
        try:
            response = await self.execute_with_hardening(
                self._raw_generate_content,
                model=model,
                contents=contents,
                config=config
            )

            return {
                "content": response[0],
                "tokens_used": response[1]
            }

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise

    """Docstring."""
def create_hardened_gemini_executor(
    component_name: str = "HardenedGeminiExecutor",
    api_key: Optional[str] = None
) -> HardenedGeminiExecutor:
    """
    Factory function to create a hardened Gemini executor with default config.

    Args:
        component_name: Name for telemetry tracking
        api_key: Optional Google API key

    Returns:
        HardenedGeminiExecutor instance
    """
    config = HardeningConfig(
        component_name=component_name,
        max_retries=5,
        wait_min_ms=1000,
        wait_max_ms=60000,
        circuit_breaker_threshold=5,
        circuit_reset_timeout=60,
        safety_threshold_ratio=0.8,
        enable_telemetry=True
    )

    return HardenedGeminiExecutor(config, api_key=api_key)
