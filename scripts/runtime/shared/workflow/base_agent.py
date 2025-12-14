"""Base agent functionality for executive agents."""

import os
import logging
from typing import Dict, Any, Tuple, Optional, Union

try:
    import instructor
    from openai import OpenAI
    from anthropic import Anthropic
    INSTRUCTOR_AVAILABLE = True
except ImportError:
    INSTRUCTOR_AVAILABLE = False
    logging.warning("Instructor not available. Executive agents will use mock responses.")

logger = logging.getLogger(__name__)


class BaseExecutiveAgent:
    """Base class for executive agents with common LLM client functionality."""

    def __init__(self):
        """Initialize base agent with LLM clients."""
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize LLM clients with Instructor if available
        if INSTRUCTOR_AVAILABLE:
            self._initialize_clients()
        else:
            self.openai_client = None
            self.anthropic_client = None
            self.logger.warning("Running in mock mode - install instructor for full functionality")

    def _initialize_clients(self):
        """Initialize LLM clients with Instructor patching."""
        try:
            # Initialize OpenAI client
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = instructor.patch(OpenAI(api_key=openai_key))

            # Initialize Anthropic client
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.anthropic_client = instructor.from_anthropic(Anthropic(api_key=anthropic_key))

            if not self.openai_client and not self.anthropic_client:
                raise ValueError("No API keys found for OpenAI or Anthropic")

        except Exception as e:
            self.logger.error(f"Failed to initialize LLM clients: {e}")
            self.openai_client = None
            self.anthropic_client = None

    def _get_client_and_model(self, config: Dict[str, Any]) -> Tuple[Optional[Union['OpenAI', 'Anthropic']], str]:
        """Get appropriate LLM client and model based on configuration.

        Args:
            config: Node configuration with infrastructure settings

        Returns:
            Tuple of (client, model_name)
        """
        infra = config.get("infrastructure_config", {})
        model = infra.get("primary_model", "gpt-4o")

        if not INSTRUCTOR_AVAILABLE:
            return None, model

        # Route to appropriate client
        if "claude" in model.lower() and self.anthropic_client:
            return self.anthropic_client, model
        elif self.openai_client:
            return self.openai_client, model
        else:
            raise ValueError(f"No client available for model: {model}")
