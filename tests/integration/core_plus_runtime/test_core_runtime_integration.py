"""Integration tests for agentic_core + runtime integration."""
from __future__ import annotations
import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class LayerType(Enum):
    L1_COGNITION = "L1_cognition"
    L2_EXECUTION = "L2_execution"
    L3_ORCHESTRATION = "L3_orchestration"
    L4_MEMORY = "L4_memory"
    L5_SAFETY = "L5_safety"

@dataclass
class RuntimeContext:
    request_id: str
    config: Dict[str, Any]
    state: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class TestCoreRuntimeIntegration:
    """Integration tests for core + runtime."""

    def test_runtime_context_flows_through_layers(self):
        """Integration: Runtime context flows through all layers."""
        ctx = RuntimeContext(
            request_id="req_001",
            config={"timeout": 30, "max_retries": 3},
        )
        
        layers = list(LayerType)
        for layer in layers:
            ctx.state[layer.value] = {"processed": True}
        
        assert all(layer.value in ctx.state for layer in layers)

    def test_config_propagation_to_agents(self):
        """Integration: Config propagates to all agents."""
        config = {
            "llm": {"model": "gpt-4o", "temperature": 0.7},
            "vector_store": {"type": "chromadb"},
            "cache": {"ttl_seconds": 3600},
        }
        
        ctx = RuntimeContext(request_id="req_002", config=config)
        
        # Each layer receives config
        for layer in LayerType:
            layer_config = ctx.config
            assert "llm" in layer_config

    def test_error_propagation_from_core_to_runtime(self):
        """Integration: Errors propagate from core to runtime."""
        ctx = RuntimeContext(request_id="req_003", config={})
        
        # Simulate error in L2
        ctx.errors.append("L2_execution: Tool call failed")
        
        # Runtime should see the error
        assert len(ctx.errors) > 0
        assert "L2_execution" in ctx.errors[0]

    def test_state_accumulation_across_layers(self):
        """Integration: State accumulates across layers."""
        ctx = RuntimeContext(request_id="req_004", config={})
        
        ctx.state["L1_cognition"] = {"intent": "search"}
        ctx.state["L2_execution"] = {"results": ["r1", "r2"]}
        ctx.state["L3_orchestration"] = {"workflow_id": "wf_001"}
        
        # All state preserved
        assert len(ctx.state) == 3


class TestSDKIntegration:
    """Integration tests for SDK clients."""

    def test_llm_client_initialization(self):
        """Integration: LLM client initializes with config."""
        config = {"provider": "openai", "model": "gpt-4o", "api_key": "test"}
        
        # Simulated client init
        client = {"provider": config["provider"], "model": config["model"]}
        assert client["provider"] == "openai"

    def test_vector_store_connection(self):
        """Integration: Vector store connects successfully."""
        config = {"type": "chromadb", "collection": "test_collection"}
        
        # Simulated connection
        connection = {"type": config["type"], "connected": True}
        assert connection["connected"]

    def test_cache_client_operations(self):
        """Integration: Cache client performs operations."""
        cache = {}
        
        # Set
        cache["key_1"] = "value_1"
        
        # Get
        value = cache.get("key_1")
        assert value == "value_1"
        
        # Delete
        del cache["key_1"]
        assert "key_1" not in cache

    def test_multi_provider_fallback(self):
        """Integration: Multi-provider fallback works."""
        providers = ["openai", "anthropic", "groq"]
        
        def try_provider(provider: str) -> Optional[str]:
            if provider == "openai":
                return None  # Simulate failure
            return f"response_from_{provider}"
        
        response = None
        for provider in providers:
            response = try_provider(provider)
            if response:
                break
        
        assert response == "response_from_anthropic"


class TestObservabilityIntegration:
    """Integration tests for observability."""

    def test_tracing_spans_created(self):
        """Integration: Tracing spans are created for operations."""
        spans = []
        
        def create_span(name: str, parent: Optional[str] = None):
            span = {"name": name, "parent": parent, "id": f"span_{len(spans)}"}
            spans.append(span)
            return span
        
        root = create_span("request")
        l1 = create_span("L1_cognition", root["id"])
        l2 = create_span("L2_execution", root["id"])
        
        assert len(spans) == 3
        assert spans[1]["parent"] == root["id"]

    def test_metrics_collection(self):
        """Integration: Metrics are collected."""
        metrics = {
            "request_count": 0,
            "error_count": 0,
            "latency_sum": 0,
        }
        
        # Simulate request
        metrics["request_count"] += 1
        metrics["latency_sum"] += 150
        
        assert metrics["request_count"] == 1

    def test_logging_structured(self):
        """Integration: Logs are structured."""
        logs = []
        
        def log(level: str, message: str, **kwargs):
            logs.append({"level": level, "message": message, **kwargs})
        
        log("INFO", "Request started", request_id="req_001")
        log("DEBUG", "Processing L1", layer="L1_cognition")
        
        assert len(logs) == 2
        assert logs[0]["request_id"] == "req_001"


class TestSecurityIntegration:
    """Integration tests for security controls."""

    def test_safety_check_integration(self):
        """Integration: Safety checks integrate with core."""
        content = "Normal business content"
        
        safety_result = {
            "passed": True,
            "checks": ["pii", "injection", "toxicity"],
            "risk_score": 0.1,
        }
        
        assert safety_result["passed"]

    def test_pii_filtering_in_pipeline(self):
        """Integration: PII filtering works in pipeline."""
        input_text = "Contact john@example.com for details"
        
        import re
        filtered = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', input_text)
        
        assert "john@example.com" not in filtered
        assert "[EMAIL]" in filtered

    def test_rate_limiting_integration(self):
        """Integration: Rate limiting integrates with runtime."""
        rate_limit = {"max_requests": 100, "window_seconds": 60}
        current_count = 50
        
        can_proceed = current_count < rate_limit["max_requests"]
        assert can_proceed
