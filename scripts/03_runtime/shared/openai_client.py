"""
OpenAI client configuration and utilities for agents.
Provides a centralized way to configure and use OpenAI SDK.
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion
import logging

logger = logging.getLogger(__name__)


class OpenAIClientManager:
    """Manages OpenAI client instances for agents."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI client manager.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            base_url: Custom base URL for OpenAI API. Useful for Azure or proxy.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Initialize clients
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat_completion(
        self,
        messages: list[Dict[str, Any]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletion:
        """
        Create a chat completion.

        Args:
            messages: List of message objects with 'role' and 'content'.
            model: OpenAI model to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters for OpenAI API.

        Returns:
            ChatCompletion object.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def achat_completion(
        self,
        messages: list[Dict[str, Any]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletion:
        """
        Create an async chat completion.

        Args:
            messages: List of message objects with 'role' and 'content'.
            model: OpenAI model to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters for OpenAI API.

        Returns:
            ChatCompletion object.
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def create_embedding(
        self,
        input_text: str,
        model: str = "text-embedding-3-large",
        **kwargs
    ) -> list[float]:
        """
        Create embeddings for text.

        Args:
            input_text: Text to embed.
            model: Embedding model to use.
            **kwargs: Additional parameters.

        Returns:
            List of embedding values.
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=input_text,
                **kwargs
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise

    def list_models(self) -> list[str]:
        """List available OpenAI models."""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []


# Global client manager instance
_client_manager: Optional[OpenAIClientManager] = None


def get_openai_client() -> OpenAIClientManager:
    """Get the global OpenAI client manager instance."""
    global _client_manager
    if _client_manager is None:
        _client_manager = OpenAIClientManager()
    return _client_manager


def configure_openai(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None
) -> OpenAIClientManager:
    """
    Configure OpenAI client with custom settings.

    Args:
        api_key: OpenAI API key.
        base_url: Custom base URL.

    Returns:
        OpenAIClientManager instance.
    """
    global _client_manager
    _client_manager = OpenAIClientManager(api_key=api_key, base_url=base_url)
    return _client_manager


# Example usage patterns
EXAMPLE_PROMPTS = {
    "agent_system": """You are an AI agent designed to assist with specific tasks.
    Follow the user's instructions carefully and provide helpful, accurate responses.""",

    "code_generation": """Generate clean, well-documented code following best practices.
    Include comments and explain your approach when necessary.""",

    "data_analysis": """Analyze the provided data and generate insights.
    Use appropriate statistical methods and visualize results when helpful.""",

    "creative_writing": """Create engaging, original content tailored to the user's requirements.
    Maintain a consistent tone and style throughout.""",
}


def create_agent_prompt(
    task_type: str,
    context: Optional[str] = None,
    instructions: Optional[str] = None
) -> list[Dict[str, Any]]:
    """
    Create a formatted prompt for an agent.

    Args:
        task_type: Type of task (e.g., 'code_generation', 'data_analysis').
        context: Additional context for the task.
        instructions: Specific instructions for the agent.

    Returns:
        Formatted messages list for OpenAI API.
    """
    messages = [{"role": "system", "content": EXAMPLE_PROMPTS.get(task_type, "")}]

    if context:
        messages.append({"role": "system", "content": f"Context: {context}"})

    if instructions:
        messages.append({"role": "user", "content": instructions})

    return messages


# Quick test function
def test_openai_connection():
    """Test OpenAI API connection."""
    try:
        client = get_openai_client()
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Say 'OpenAI connection successful!'"}],
            model="gpt-3.5-turbo",
            max_tokens=50
        )
        logger.info(response.choices[0].message.content)
        return True
    except Exception as e:
        logger.error(f"OpenAI connection failed: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    logger.info("Testing OpenAI configuration...")
    test_openai_connection()
