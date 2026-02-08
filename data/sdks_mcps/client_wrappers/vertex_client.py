"""Google Vertex AI Client layer - Production Grade with Grounding and Safety
Implements retry logic, grounding optimization, and configurable safety settings.
"""

import os
from dataclasses import dataclass
from typing import object

import backoff
from vertexai import init as vertex_init
from vertexai.generative_models import (
    Content,
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    SafetySetting,
    Tool,
)
from vertexai.preview import grounding as vertex_grounding


@dataclass
class VertexConfig:
    """configuration for Vertex AI client."""

    project_id: str | None = None
    location: str = "us-central1"
    model: str = "gemini-1.5-pro-002"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 60
    enable_grounding: bool = True
    default_safety_threshold: HarmBlockThreshold = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE


class VertexClient:
    """Production-ready Vertex AI client with grounding and safety support."""

    def __init__(self, config: VertexConfig | None = None):
        self.config = config or VertexConfig()

        # Initialize Vertex AI
        vertex_init(
            project=self.config.project_id or os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=self.config.location,
        )

        self.model = GenerativeModel(self.config.model)

        # Track usage for cost monitoring
        self.usage_stats = {
            "total_requests": 0,
            "prompt_tokens": 0,
            "candidates_tokens": 0,
            "total_tokens": 0,
            "grounding_tokens": 0,
            "total_cost": 0.0,
            "errors": 0,
        }

    @backoff.on_exception(
        backoff.expo,
        Exception,  # Vertex AI uses standard exceptions
        max_tries=5,
        factor=1,
        max_value=60,
    )
    def generate_content(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        enable_grounding: bool | None = None,
        safety_settings: dict[HarmCategory, HarmBlockThreshold] | None = None,
        tools: list[Tool] | None = None,
        stream: bool = False,
        **kwargs: dict[str, object],
    ) -> object:
        """Generate content with retry logic and optional grounding.

        Args:
            prompt: Input prompt text
            system_instruction: System instruction for the model
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            enable_grounding: Enable Google Search grounding
            safety_settings: Custom safety settings
            tools: List of tools for function calling
            stream: Whether to stream response
            **kwargs: Additional Vertex AI parameters

        Returns:
            Generation response or stream
        """
        try:
            self.usage_stats["total_requests"] += 1

            # Prepare content
            content = Content(parts=[Part.from_text(prompt)], role="user")

            # Generation config
            generation_config = GenerationConfig(
                temperature=temperature if temperature is not None else self.config.temperature,
                max_output_tokens=max_tokens or self.config.max_tokens,
                **kwargs,
            )

            # Safety settings
            if safety_settings:
                safety_cfg = [
                    SafetySetting(category=cat, threshold=thresh) for cat, thresh in safety_settings.items()
                ]
            else:
                safety_cfg = [
                    SafetySetting(
                        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=self.config.default_safety_threshold,
                    ),
                    SafetySetting(
                        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=self.config.default_safety_threshold,
                    ),
                    SafetySetting(
                        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=self.config.default_safety_threshold,
                    ),
                    SafetySetting(
                        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=self.config.default_safety_threshold,
                    ),
                ]

            # Tools (including grounding)
            tool_list = tools or []
            if enable_grounding if enable_grounding is not None else self.config.enable_grounding:
                grounding_tool = Tool.from_google_search_retrieval(
                    vertex_grounding.GoogleSearchRetrieval(
                        dynamic_retrieval_config=vertex_grounding.DynamicRetrievalConfig(
                            mode="MODE_DYNAMIC",
                            dynamic_threshold=0.7,
                        ),
                    ),
                )
                tool_list.append(grounding_tool)

            # System instruction
            system_inst = None
            if system_instruction:
                system_inst = Content(parts=[Part.from_text(system_instruction)], role="user")

            if stream:
                return self.model.generate_content(
                    content,
                    generation_config=generation_config,
                    safety_settings=safety_cfg,
                    tools=tool_list,
                    system_instruction=system_inst,
                    stream=True,
                )
            else:
                response = self.model.generate_content(
                    content,
                    generation_config=generation_config,
                    safety_settings=safety_cfg,
                    tools=tool_list,
                    system_instruction=system_inst,
                    stream=False,
                )

                self._update_usage_stats(
                    response.usage_metadata if hasattr(response, "usage_metadata") else None,
                )
                return response

        except Exception as e:
            self.usage_stats["errors"] += 1
            raise self._handle_error(e)

    def grounded_response(
        self,
        prompt: str,
        grounding_threshold: float = 0.7,
        include_citations: bool = True,
        **kwargs: dict[str, object],
    ) -> dict[str, object]:
        """Generate response with Google Search grounding and citations.

        Args:
            prompt: Input prompt
            grounding_threshold: Threshold for automatic grounding
            include_citations: Whether to extract and include citations
            **kwargs: Additional generation parameters

        Returns:
            Dictionary with response, grounding metadata, and citations
        """
        # Custom grounding configuration
        grounding_tool = Tool.from_google_search_retrieval(
            vertex_grounding.GoogleSearchRetrieval(
                dynamic_retrieval_config=vertex_grounding.DynamicRetrievalConfig(
                    mode="MODE_DYNAMIC",
                    dynamic_threshold=grounding_threshold,
                ),
            ),
        )

        response = self.generate_content(prompt=prompt, tools=[grounding_tool], **kwargs)

        # Extract grounding information
        grounding_metadata = None
        citations = []

        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                grounding_metadata = {
                    "grounding_score": candidate.grounding_metadata.grounding_score,
                    "grounding_supports": [],
                }

                # Extract grounding supports
                if hasattr(candidate.grounding_metadata, "grounding_supports"):
                    for support in candidate.grounding_metadata.grounding_supports:
                        grounding_support = {
                            "segment": support.grounding_chunk.segment.text
                            if support.grounding_chunk.segment
                            else "",
                            "score": support.grounding_score,
                            "sources": [],
                        }

                        # Extract sources
                        if hasattr(support, "grounding_chunk") and support.grounding_chunk.web:
                            for source in support.grounding_chunk.web:
                                grounding_support["sources"].append(
                                    {
                                        "uri": source.uri,
                                        "title": source.title,
                                        "snippet": source.snippet,
                                    },
                                )

                        grounding_metadata["grounding_supports"].append(grounding_support)

                # Extract citations if requested
                if include_citations:
                    citations = self._extract_citations(grounding_metadata)

        return {
            "content": response.text,
            "model": self.config.model,
            "grounding_enabled": True,
            "grounding_metadata": grounding_metadata,
            "citations": citations,
            "usage": self._extract_usage(response),
        }

    def safe_response(
        self,
        prompt: str,
        safety_threshold: HarmBlockThreshold = HarmBlockThreshold.BLOCK_NONE,
        custom_safety: dict[HarmCategory, HarmBlockThreshold] | None = None,
        **kwargs: dict[str, object],
    ) -> dict[str, object]:
        """Generate response with configurable safety settings.

        Args:
            prompt: Input prompt
            safety_threshold: Default safety threshold
            custom_safety: Category-specific safety settings
            **kwargs: Additional generation parameters

        Returns:
            Dictionary with response and safety metadata
        """
        # Use custom safety settings or default threshold
        safety_settings = custom_safety or {
            HarmCategory.HARM_CATEGORY_HARASSMENT: safety_threshold,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: safety_threshold,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: safety_threshold,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: safety_threshold,
        }

        response = self.generate_content(prompt=prompt, safety_settings=safety_settings, **kwargs)

        # Extract safety ratings
        safety_ratings = []
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "safety_ratings"):
                for rating in candidate.safety_ratings:
                    safety_ratings.append(
                        {
                            "category": rating.category.name,
                            "probability": rating.probability.name if rating.probability else None,
                            "blocked": rating.blocked if hasattr(rating, "blocked") else False,
                        },
                    )

        return {
            "content": response.text,
            "model": self.config.model,
            "safety_ratings": safety_ratings,
            "finish_reason": response.candidates[0].finish_reason.name
            if hasattr(response.candidates[0], "finish_reason")
            else None,
            "usage": self._extract_usage(response),
        }

    def stream_response(
        self,
        prompt: str,
        callback: callable = None,
        **kwargs: dict[str, object],
    ) -> list[str]:
        """Stream response with optional callback.

        Args:
            prompt: Input prompt
            callback: Function to call with each chunk
            **kwargs: Additional generation parameters

        Returns:
            List of accumulated text chunks
        """
        stream = self.generate_content(prompt=prompt, stream=True, **kwargs)
        chunks = []

        for chunk in stream:
            if chunk.text:
                content = chunk.text
                chunks.append(content)

                if callback:
                    callback(content)

        return chunks

    def _extract_citations(self, grounding_metadata: dict[str, object]) -> list[dict[str, object]]:
        """Extract structured citations from grounding metadata."""
        citations = []
        seen_sources = set()

        for support in grounding_metadata.get("grounding_supports", []):
            for source in support.get("sources", []):
                if source["uri"] not in seen_sources:
                    citation = {
                        "uri": source["uri"],
                        "title": source["title"],
                        "snippet": source["snippet"][:200] + "..."
                        if len(source["snippet"]) > 200
                        else source["snippet"],
                        "confidence": support["score"],
                        "referenced_text": support["segment"][:100] + "..."
                        if len(support["segment"]) > 100
                        else support["segment"],
                    }
                    citations.append(citation)
                    seen_sources.add(source["uri"])

        return citations

    def _extract_usage(self, response) -> dict[str, object]:
        """Extract usage metadata from response."""
        if hasattr(response, "usage_metadata"):
            return {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }
        return {}

    def _update_usage_stats(self, usage_metadata):
        """Update usage statistics for monitoring."""
        if usage_metadata:
            self.usage_stats["prompt_tokens"] += usage_metadata.prompt_token_count
            self.usage_stats["candidates_tokens"] += usage_metadata.candidates_token_count
            self.usage_stats["total_tokens"] += usage_metadata.total_token_count

            # Cost calculation (Gemini 1.5 Pro pricing)
            input_cost = (usage_metadata.prompt_token_count * 0.00125) / 1000
            output_cost = (usage_metadata.candidates_token_count * 0.005) / 1000

            self.usage_stats["total_cost"] += input_cost + output_cost

    def _handle_error(self, error: Exception) -> Exception:
        """Enhance error messages with context."""
        error_str = str(error)

        if "quota" in error_str.lower() or "rate limit" in error_str.lower():
            return Exception(f"Rate limit exceeded: {error}")
        elif "permission" in error_str.lower() or "auth" in error_str.lower():
            return Exception(f"Authentication error: {error}")
        elif "timeout" in error_str.lower():
            return Exception(f"Request timeout: {error}")
        else:
            return Exception(f"Vertex AI error: {error}")

    def get_usage_stats(self) -> dict[str, object]:
        """Get current usage statistics."""
        return self.usage_stats.copy()

    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            "total_requests": 0,
            "prompt_tokens": 0,
            "candidates_tokens": 0,
            "total_tokens": 0,
            "grounding_tokens": 0,
            "total_cost": 0.0,
            "errors": 0,
        }


# builder function for easy instantiation
def create_vertex_client(
    project_id: str | None = None,
    location: str = "us-central1",
    model: str = "gemini-1.5-pro-002",
    enable_grounding: bool = True,
    **kwargs: dict[str, object],
) -> VertexClient:
    """Create configured Vertex AI client.

    Args:
        project_id: Google Cloud project ID
        location: Vertex AI region
        model: Default model
        enable_grounding: Enable Google Search grounding
        **kwargs: Additional configuration

    Returns:
        Configured Vertex AI client
    """
    config = VertexConfig(
        project_id=project_id,
        location=location,
        model=model,
        enable_grounding=enable_grounding,
        **kwargs,
    )
    return VertexClient(config)


# Example usage
if __name__ == "__main__":
    # Create client with grounding
    client = create_vertex_client(enable_grounding=True)

    # Simple generation
    try:
        response = client.generate_content("Explain quantum computing in 100 words.")

        # Grounded response
        grounded = client.grounded_response(
            "What are the latest developments in AI large language models?",
            grounding_threshold=0.7,
        )

        # Safe response with custom safety
        safe = client.safe_response(
            "Write a professional email template",
            safety_threshold=HarmBlockThreshold.BLOCK_NONE,
        )

        # Usage stats
        print("Usage Stats:", client.get_usage_stats())

    except Exception as e:
        print(f"An error occurred: {e}")
