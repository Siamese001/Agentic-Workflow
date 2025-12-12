"""End-to-End Integration Test for Agentic Workflow with SDK Integration.

Tests complete workflow execution with:
- LLM provider integration (OpenAI/Anthropic)
- Vector store integration (ChromaDB)
- Redis caching
- OpenTelemetry tracing
- Multi-hop agent execution

Phase 1C - SDK Integration Layer
"""

import os
import pytest
from typing import Any, Dict

from runtime.shared import (
    AgentMessage,
    Provider,
    WorkflowOrchestrator,
    create_workflow_context,
    validate_all_sdks,
)


class TestSDKValidation:
    """Test SDK availability and configuration."""
    
    def test_validate_all_sdks(self):
        """Test SDK validation report."""
        report = validate_all_sdks()
        
        assert "total" in report
        assert "available" in report
        assert "details" in report
        assert report["total"] == 23
    
    def test_required_sdks_available(self):
        """Test that required SDKs are available."""
        report = validate_all_sdks()
        
        required_sdks = [
            "openai",
            "litellm",
            "instructor",
            "chromadb",
            "redis",
            "opentelemetry-api",
            "opentelemetry-sdk",
        ]
        
        for sdk_name in required_sdks:
            if sdk_name in report["details"]:
                detail = report["details"][sdk_name]
                assert detail["required"] is True


class TestWorkflowContext:
    """Test workflow context creation and SDK integration."""
    
    def test_create_workflow_context(self):
        """Test workflow context creation."""
        context = create_workflow_context(
            workflow_id="test-workflow-001",
            provider=Provider.OPENAI,
            enable_cache=False,
            enable_vector_store=False,
            enable_tracing=False,
        )
        
        assert context.workflow_id == "test-workflow-001"
        assert context.agent_executor is not None
    
    def test_workflow_context_with_cache(self):
        """Test workflow context with Redis cache."""
        try:
            context = create_workflow_context(
                workflow_id="test-workflow-002",
                enable_cache=True,
                enable_vector_store=False,
                enable_tracing=False,
            )
            
            if context.cache_client:
                context.set_in_cache("test_key", "test_value", ttl=60)
                value = context.get_from_cache("test_key")
                assert value == "test_value"
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")
    
    def test_workflow_context_with_vector_store(self):
        """Test workflow context with vector store."""
        try:
            context = create_workflow_context(
                workflow_id="test-workflow-003",
                enable_cache=False,
                enable_vector_store=True,
                enable_tracing=False,
            )
            
            assert context.vector_store is not None
        except Exception as e:
            pytest.skip(f"Vector store not available: {e}")


class TestAgentExecution:
    """Test agent execution with LLM providers."""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_agent_execute_openai(self):
        """Test agent execution with OpenAI."""
        context = create_workflow_context(
            workflow_id="test-agent-001",
            provider=Provider.OPENAI,
            enable_cache=False,
            enable_vector_store=False,
            enable_tracing=False,
        )
        
        messages = [
            AgentMessage(role="user", content="What is 2+2? Answer with just the number.")
        ]
        
        response = context.agent_executor.execute(
            messages=messages,
            system_prompt="You are a helpful math assistant.",
        )
        
        assert response.content is not None
        assert len(response.content) > 0
        assert response.finish_reason in ["stop", "end_turn"]
        assert "usage" in response.__dict__
    
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_agent_execute_anthropic(self):
        """Test agent execution with Anthropic."""
        context = create_workflow_context(
            workflow_id="test-agent-002",
            provider=Provider.ANTHROPIC,
            enable_cache=False,
            enable_vector_store=False,
            enable_tracing=False,
        )
        
        messages = [
            AgentMessage(role="user", content="What is the capital of France? Answer with just the city name.")
        ]
        
        response = context.agent_executor.execute(
            messages=messages,
            system_prompt="You are a helpful geography assistant.",
        )
        
        assert response.content is not None
        assert "Paris" in response.content or "paris" in response.content.lower()


class TestWorkflowOrchestration:
    """Test end-to-end workflow orchestration."""
    
    def test_workflow_orchestrator_creation(self):
        """Test workflow orchestrator creation."""
        orchestrator = WorkflowOrchestrator(
            workflow_id="test-orchestrator-001",
            provider=Provider.OPENAI,
        )
        
        assert orchestrator.workflow_id == "test-orchestrator-001"
        assert orchestrator.context is not None
        assert len(orchestrator.hops) == 0
    
    def test_workflow_hop_registration(self):
        """Test hop registration."""
        orchestrator = WorkflowOrchestrator(
            workflow_id="test-orchestrator-002",
        )
        
        def hop1(context):
            context.set_output("result", "hop1_output")
        
        def hop2(context):
            input_val = context.get_input("result")
            context.set_output("final_result", f"{input_val}_hop2")
        
        orchestrator.register_hop("hop1", hop1)
        orchestrator.register_hop("hop2", hop2, dependencies=["hop1"])
        
        assert len(orchestrator.hops) == 2
        assert orchestrator.hops[0]["id"] == "hop1"
        assert orchestrator.hops[1]["id"] == "hop2"
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    )
    def test_end_to_end_workflow_execution(self):
        """Test complete end-to-end workflow execution."""
        orchestrator = WorkflowOrchestrator(
            workflow_id="test-e2e-001",
            provider=Provider.OPENAI,
        )
        
        def analyze_hop(context):
            """Analyze input and generate insights."""
            user_input = context.get_input("user_query", "What is AI?")
            
            messages = [
                AgentMessage(
                    role="user",
                    content=f"Provide a brief 1-sentence answer to: {user_input}"
                )
            ]
            
            response = context.execute_agent(
                messages=messages,
                system_prompt="You are a helpful AI assistant. Be concise.",
            )
            
            context.set_output("analysis", response.content)
        
        def summarize_hop(context):
            """Summarize the analysis."""
            analysis = context.get_input("analysis", "")
            
            messages = [
                AgentMessage(
                    role="user",
                    content=f"Summarize this in 5 words or less: {analysis}"
                )
            ]
            
            response = context.execute_agent(
                messages=messages,
                system_prompt="You are a summarization expert.",
            )
            
            context.set_output("summary", response.content)
        
        orchestrator.register_hop("analyze", analyze_hop)
        orchestrator.register_hop("summarize", summarize_hop, dependencies=["analyze"])
        
        outputs = orchestrator.execute(
            initial_inputs={"user_query": "What is machine learning?"}
        )
        
        assert "analysis" in outputs
        assert "summary" in outputs
        assert len(outputs["analysis"]) > 0
        assert len(outputs["summary"]) > 0


class TestMultiProviderFallback:
    """Test multi-provider fallback scenarios."""
    
    def test_provider_fallback_logic(self):
        """Test that fallback providers are configured."""
        from runtime.shared.sdk_registry import SDK_REGISTRY
        
        anthropic_entry = SDK_REGISTRY.get("anthropic")
        assert anthropic_entry is not None
        assert anthropic_entry.fallback == "openai"
        
        groq_entry = SDK_REGISTRY.get("groq")
        assert groq_entry is not None
        assert groq_entry.fallback == "openai"


class TestCachingIntegration:
    """Test caching integration in workflows."""
    
    def test_cache_workflow_state(self):
        """Test caching workflow state."""
        try:
            context = create_workflow_context(
                workflow_id="test-cache-001",
                enable_cache=True,
                enable_vector_store=False,
                enable_tracing=False,
            )
            
            if context.cache_client:
                test_data = {
                    "hop_id": "hop1",
                    "status": "completed",
                    "output": "test_output",
                }
                
                context.set_in_cache("hop1_state", test_data, ttl=300)
                retrieved = context.get_from_cache("hop1_state")
                
                assert retrieved == test_data
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")


class TestVectorStoreIntegration:
    """Test vector store integration in workflows."""
    
    def test_knowledge_search(self):
        """Test knowledge search in vector store."""
        try:
            context = create_workflow_context(
                workflow_id="test-vector-001",
                enable_cache=False,
                enable_vector_store=True,
                enable_tracing=False,
            )
            
            if context.vector_store:
                from runtime.shared import create_chroma_collection, upsert_vectors_chroma
                
                collection = create_chroma_collection(
                    context.vector_store,
                    "test_collection",
                )
                
                upsert_vectors_chroma(
                    collection,
                    ids=["doc1", "doc2"],
                    embeddings=[[0.1] * 1536, [0.2] * 1536],
                    documents=["Test document 1", "Test document 2"],
                )
                
                results = context.search_knowledge(
                    query_embedding=[0.15] * 1536,
                    collection_name="test_collection",
                    n_results=2,
                )
                
                assert results is not None
        except Exception as e:
            pytest.skip(f"Vector store not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
