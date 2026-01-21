"""Agent Executor - LLM-powered agent execution wrapper.

Provides unified agent execution with LLM provider integration,
structured outputs, retry logic, and observability.

Phase 1C - SDK Integration Layer
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .multi_provider_clients import (
    Provider,
    get_client,
    get_instructor_client,
    get_litellm_completion,
)
from .observability_clients import create_span, record_exception, set_span_attribute

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for agent execution."""
    provider: Provider = Provider.OPENAI
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    max_retries: int = 3
    timeout: float = 60.0
    enable_tracing: bool = True


@dataclass
class AgentMessage:
    """Message in agent conversation."""
    role: str
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class AgentResponse:
    """Response from agent execution."""
    content: str
    finish_reason: str
    usage: Dict[str, int] = field(default_factory=dict)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    raw_response: Optional[Any] = None
    interaction_id: Optional[str] = None  # For Google GenAI stateful continuations
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional response metadata


class AgentExecutor:
    """Agent executor with LLM provider integration."""

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize agent executor.

        Args:
            config: Optional agent configuration
        """
        self.config = config or AgentConfig()
        self._client = None

    def _get_client(self) -> Any:
        """Get LLM client (lazy initialization)."""
        if self._client is None:
            self._client = get_client(self.config.provider)
        return self._client

    def execute(
        self,
        messages: List[AgentMessage],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> AgentResponse:
        """Execute agent with messages.

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt
            tools: Optional tool definitions
            **kwargs: Additional provider-specific parameters

        Returns:
            AgentResponse with completion
        """
        span_name = f"agent.execute.{self.config.provider.value}"

        if self.config.enable_tracing:
            with create_span(span_name) as span:
                set_span_attribute("agent.provider", self.config.provider.value)
                set_span_attribute("agent.model", self.config.model or "default")
                set_span_attribute("agent.message_count", len(messages))

                try:
                    return self._execute_internal(messages, system_prompt, tools, **kwargs)
                except Exception as e:
                    record_exception(e)
                    raise
        else:
            return self._execute_internal(messages, system_prompt, tools, **kwargs)

    def _execute_internal(
        self,
        messages: List[AgentMessage],
        system_prompt: Optional[str],
        tools: Optional[List[Dict[str, Any]]],
        **kwargs,
    ) -> AgentResponse:
        """Internal execution logic."""
        # Convert messages to provider format
        formatted_messages = self._format_messages(messages, system_prompt)

        # Get model name
        model = self.config.model or self._get_default_model()

        # Execute based on provider
        if self.config.provider == Provider.OPENAI:
            return self._execute_openai(formatted_messages, model, tools, **kwargs)
        elif self.config.provider == Provider.ANTHROPIC:
            return self._execute_anthropic(formatted_messages, model, tools, **kwargs)
        elif self.config.provider == Provider.GOOGLE:
            return self._execute_google(formatted_messages, model, tools, **kwargs)
        else:
            # Use LiteLLM for other providers
            return self._execute_litellm(formatted_messages, model, tools, **kwargs)

    def _format_messages(
        self,
        messages: List[AgentMessage],
        system_prompt: Optional[str],
    ) -> List[Dict[str, str]]:
        """Format messages for provider."""
        formatted = []

        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})

        for msg in messages:
            formatted_msg = {"role": msg.role, "content": msg.content}

            if msg.name:
                formatted_msg["name"] = msg.name
            if msg.tool_calls:
                formatted_msg["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                formatted_msg["tool_call_id"] = msg.tool_call_id

            formatted.append(formatted_msg)

        return formatted

    def _execute_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        tools: Optional[List[Dict[str, Any]]],
        **kwargs,
    ) -> AgentResponse:
        """Execute using OpenAI client."""
        client = self._get_client()

        params = {
            "model": model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **kwargs,
        }

        if tools:
            params["tools"] = tools

        response = client.chat.completions.create(**params)

        message = response.choices[0].message

        return AgentResponse(
            content=message.content or "",
            finish_reason=response.choices[0].finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            tool_calls=message.tool_calls if hasattr(message, "tool_calls") else None,
            raw_response=response,
        )

    def _execute_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: str,
        tools: Optional[List[Dict[str, Any]]],
        **kwargs,
    ) -> AgentResponse:
        """Execute using Anthropic client."""
        client = self._get_client()

        # Extract system message if present
        system = None
        if messages and messages[0]["role"] == "system":
            system = messages[0]["content"]
            messages = messages[1:]

        params = {
            "model": model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens or 4096,
            **kwargs,
        }

        if system:
            params["system"] = system
        if tools:
            params["tools"] = tools

        response = client.messages.create(**params)

        content = ""
        tool_calls = []

        for block in response.content:
            if hasattr(block, "text"):
                content += block.text
            elif hasattr(block, "tool_use"):
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": block.input,
                    },
                })

        return AgentResponse(
            content=content,
            finish_reason=response.stop_reason,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            tool_calls=tool_calls if tool_calls else None,
            raw_response=response,
        )

    def _execute_google(
        self,
        messages: List[Dict[str, str]],
        model: str,
        tools: Optional[List[Dict[str, Any]]],
        previous_interaction_id: Optional[str] = None,
        **kwargs,
    ) -> AgentResponse:
        """Execute using Google GenAI client with Interactions API."""
        from tenacity import retry, stop_after_attempt, wait_exponential

        client = self._get_client()

        # Check if we have the new v1beta client or legacy
        if hasattr(client, 'interactions'):
            # NEW: Use v1beta Interactions API
            return self._execute_google_interactions(
                client, messages, model, tools, previous_interaction_id, **kwargs
            )
        else:
            # FALLBACK: Use legacy SDK
            return self._execute_google_legacy(client, messages, model, **kwargs)

    def _execute_google_interactions(
        self,
        client,
        messages: List[Dict[str, str]],
        model: str,
        tools: Optional[List[Dict[str, Any]]],
        previous_interaction_id: Optional[str],
        **kwargs,
    ) -> AgentResponse:
        """Execute using Google GenAI v1beta Interactions API with retry."""
        from tenacity import retry, stop_after_attempt, wait_exponential

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
        def _execute_with_retry():
            try:
                # Prepare input for interactions.create
                input_messages = []

                # Convert messages to Interactions API format
                for msg in messages:
                    if msg["role"] == "system":
                        # System prompt becomes first user message with model acknowledgment
                        input_messages.append({"role": "user", "content": msg["content"]})
                        input_messages.append({"role": "model", "content": "Understood. I am ready."})
                    else:
                        input_messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

                # Prepare request parameters
                request_params = {
                    "model": model,
                    "input": input_messages,
                }

                # Add config for structured output if requested
                config = {}
                if "response_mime_type" in kwargs:
                    config["response_mime_type"] = kwargs["response_mime_type"]
                if "response_schema" in kwargs:
                    config["response_schema"] = kwargs["response_schema"]
                if config:
                    request_params["config"] = config

                # Use previous_interaction_id for stateful continuations
                if previous_interaction_id:
                    request_params["previous_interaction_id"] = previous_interaction_id

                # Execute the interaction
                response = client.interactions.create(**request_params)

                # Extract content from response
                content = ""
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        content = candidate.content.parts[0].text if candidate.content.parts else ""

                # Build response
                return AgentResponse(
                    content=content,
                    finish_reason=getattr(response, 'finish_reason', 'stop'),
                    usage={},  # Usage info not available in v1beta yet
                    interaction_id=getattr(response, 'id', None),
                    raw_response=response,
                )

            except Exception as e:
                logger.error(f"Google GenAI Interactions API error: {e}")
                raise

        return _execute_with_retry()

    def _execute_google_legacy(
        self,
        genai_module,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs,
    ) -> AgentResponse:
        """Execute using legacy Google GenerativeAI SDK."""
        # Extract system prompt
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n\n"

        # Create model and generate
        model_client = genai_module.GenerativeModel(model)
        response = model_client.generate_content(prompt)

        return AgentResponse(
            content=str(getattr(response, "text", "") or ""),
            finish_reason=getattr(response, "candidates", [{}])[0].get("finish_reason", "stop"),
            usage={},
            raw_response=response,
        )

    def _execute_litellm(
        self,
        messages: List[Dict[str, str]],
        model: str,
        tools: Optional[List[Dict[str, Any]]],
        **kwargs,
    ) -> AgentResponse:
        """Execute using LiteLLM."""
        params = {
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **kwargs,
        }

        if tools:
            params["tools"] = tools

        response = get_litellm_completion(
            messages=messages,
            model=model,
            **params,
        )

        message = response.choices[0].message

        return AgentResponse(
            content=message.content or "",
            finish_reason=response.choices[0].finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            tool_calls=message.tool_calls if hasattr(message, "tool_calls") else None,
            raw_response=response,
        )

    def _get_default_model(self) -> str:
        """Get default model for provider."""
        from .multi_provider_clients import get_default_model
        return get_default_model(self.config.provider)

    def execute_structured(
        self,
        messages: List[AgentMessage],
        response_model: Any,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Execute agent with structured output using Instructor.

        Args:
            messages: List of conversation messages
            response_model: Pydantic model for response structure
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters

        Returns:
            Structured response matching response_model
        """
        # Special handling for Google GenAI with Interactions API
        if self.config.provider == Provider.GOOGLE:
            return self._execute_google_structured(messages, response_model, system_prompt, **kwargs)

        # Use Instructor for other providers
        instructor_client = get_instructor_client(self.config.provider)

        formatted_messages = self._format_messages(messages, system_prompt)
        model = self.config.model or self._get_default_model()

        response = instructor_client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            response_model=response_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs,
        )

        return response

    def _execute_google_structured(
        self,
        messages: List[AgentMessage],
        response_model: Any,
        system_prompt: Optional[str],
        **kwargs,
    ) -> Any:
        """Execute Google GenAI with structured JSON output using Interactions API."""
        import json
        from pydantic import BaseModel

        client = self._get_client()

        # Check if we have the new v1beta client
        if not hasattr(client, 'interactions'):
            # Fallback to Instructor with legacy SDK
            instructor_client = get_instructor_client(self.config.provider)
            formatted_messages = self._format_messages(messages, system_prompt)
            model = self.config.model or self._get_default_model()

            response = instructor_client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                response_model=response_model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs,
            )
            return response

        # Use v1beta Interactions API with JSON schema
        formatted_messages = self._format_messages(messages, system_prompt)
        model = self.config.model or self._get_default_model()

        # Convert Pydantic model to JSON schema
        if issubclass(response_model, BaseModel):
            schema = response_model.model_json_schema()
        else:
            # Try to get schema from response_model if it has one
            schema = getattr(response_model, 'json_schema', None)
            if not schema:
                raise ValueError("response_model must be a Pydantic BaseModel or have json_schema method")

        # Prepare input for interactions.create
        input_messages = []

        # Convert messages to Interactions API format
        for msg in formatted_messages:
            if msg["role"] == "system":
                # System prompt becomes first user message with model acknowledgment
                input_messages.append({"role": "user", "content": msg["content"]})
                input_messages.append({"role": "model", "content": "Understood. I am ready."})
            else:
                input_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Add JSON schema instruction to last message
        if input_messages:
            last_msg = input_messages[-1]
            if last_msg["role"] == "user":
                last_msg["content"] += "\n\nIMPORTANT: Respond with valid JSON that matches the required schema."

        # Execute the interaction with JSON schema
        response = client.interactions.create(
            model=model,
            input=input_messages,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens,
            }
        )

        # Extract and parse JSON response
        content = ""
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                content = candidate.content.parts[0].text if candidate.content.parts else ""

        # Parse JSON into response model
        try:
            parsed = json.loads(content)
            if issubclass(response_model, BaseModel):
                return response_model(**parsed)
            else:
                return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw content: {content}")
            raise ValueError(f"Invalid JSON response from model: {e}")


def create_agent_executor(
    provider: Provider = Provider.OPENAI,
    model: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs,
) -> AgentExecutor:
    """Factory function to create agent executor.

    Args:
        provider: LLM provider
        model: Optional model name
        temperature: Sampling temperature
        **kwargs: Additional configuration parameters

    Returns:
        AgentExecutor instance
    """
    config = AgentConfig(
        provider=provider,
        model=model,
        temperature=temperature,
        **kwargs,
    )

    return AgentExecutor(config)
