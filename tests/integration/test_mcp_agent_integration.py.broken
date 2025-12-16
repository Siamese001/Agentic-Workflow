"""Integration tests for MCP and micro agent communication.


LOGGER = logging.getLogger(__name__)
Tests cover:
- Agent registration and discovery via MCP
- Inter-agent communication patterns
- Workflow orchestration with multiple agents
- Error handling and recovery
- Performance under concurrent load
"""

import asyncio
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

logger = logging.getLogger(__name__)


# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import mcp_tools directly to avoid problematic __init__.py imports
SPEC = importlib.util.spec_from_file_location("mcp_tools",
                                              os.path.join(os.path.dirname(__file__),
                                                           '..',
                                                           '..',
                                                           'runtime',
                                                           'shared',
                                                           'mcp_tools.py'))
mcp_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_tools)

# Extract the classes we need
MCPTool = mcp_tools.MCPTool
MCPToolServer = mcp_tools.MCPToolServer
MCPToolResult = mcp_tools.MCPToolResult
create_mcp_server = mcp_tools.create_mcp_server
execute_tool_calls = mcp_tools.execute_tool_calls


# Mock agent classes for testing
@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    receiver: str
    message_type: str
    payload: Dict[str, Any]
    message_id: str
    timestamp: float


class MockAgent:
    """Mock agent for testing MCP integration."""

    def __init__(self, name: str, capabilities: List[str]):
        SELF.NAME = name
        SELF.CAPABILITIES = capabilities
        self.mcp_server = MCPToolServer(f"{name}-server")
        self.message_queue = asyncio.Queue()
        self.register_agent_tools()

    def register_agent_tools(self):
        """Register agent-specific MCP tools."""
        # Tool for sending messages to other agents
        def send_message(
            receiver: str,
            message_type: str,
            payload: Dict[str, Any]
        ) -> Dict[str, str]:
            """Send a message to another agent."""
            import time
            MESSAGE = AgentMessage(
                SENDER=self.name,
                RECEIVER=receiver,
                message_type=message_type,
                PAYLOAD=payload,
                message_id=f"{self.name}-{int(time.time() * 1000)}",
                TIMESTAMP=time.time()
            )
            # In real implementation, this would route to the receiver
            return {
                "message_id": message.message_id,
                "status": "sent",
                "timestamp": message.timestamp
            }

        self.mcp_server.register_function(
            NAME="send_message",
            DESCRIPTION="Send a message to another agent",
            PARAMETERS={
                "type": "object",
                "properties": {
                    "receiver": {"type": "string"},
                    "message_type": {"type": "string"},
                    "payload": {"type": "object"}
                },
                "required": ["receiver", "message_type", "payload"]
            },
            HANDLER=send_message
        )

        # Tool for querying agent capabilities
        def get_capabilities() -> Dict[str, List[str]]:
            """Get this agent's capabilities."""
            return {
                "agent": self.name,
                "capabilities": self.capabilities
            }

        self.mcp_server.register_function(
            NAME="get_capabilities",
            DESCRIPTION="Get agent capabilities",
            PARAMETERS={},
            HANDLER=get_capabilities
        )

        # Capability-specific tools
        for capability in self.capabilities:
            if capability == "data_analysis":
                def analyze_data(data: List[float]) -> Dict[str, float]:
                    """Analyze numerical data."""
                    if not data:
                        return {"error": "No data provided"}
                    return {
                        "mean": sum(data) / len(data),
                        "min": min(data),
                        "max": max(data),
                        "count": len(data)
                    }

                self.mcp_server.register_function(
                    NAME="analyze_data",
                    DESCRIPTION="Analyze numerical data",
                    PARAMETERS={
                        "type": "object",
                        "properties": {
                            "data": {"type": "array", "items": {"type": "number"}}
                        },
                        "required": ["data"]
                    },
                    HANDLER=analyze_data
                )

            elif CAPABILITY == "text_generation":
                def generate_text(prompt: str, max_length: int = 100) -> str:
                    """Generate text from prompt."""
                    return f"Generated text based on: {prompt[:max_length]}"

                self.mcp_server.register_function(
                    NAME="generate_text",
                    DESCRIPTION="Generate text from prompt",
                    PARAMETERS={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "max_length": {"type": "integer", "default": 100}
                        },
                        "required": ["prompt"]
                    },
                    HANDLER=generate_text
                )

            elif CAPABILITY == "web_search":
                def search_web(query: str, limit: int = 5) -> List[Dict[str, str]]:
                    """Search the web for information."""
                    # Mock search results
                    return [
                        {"title": f"Result {i} for '{query}'",
                            "url": f"http://example.com/{i}"}
                        for i in range(min(limit, 3))
                    ]

                self.mcp_server.register_function(
                    NAME="search_web",
                    DESCRIPTION="Search the web",
                    PARAMETERS={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer", "default": 5}
                        },
                        "required": ["query"]
                    },
                    HANDLER=search_web
                )


class MockAgentRegistry:
    """Mock agent registry for discovering agents."""

    def __init__(self):
        self.agents: Dict[str, MockAgent] = {}
        self.mcp_server = MCPToolServer("registry-server")
        self.register_registry_tools()

    def register_registry_tools(self):
        """Register registry-specific MCP tools."""
        def register_agent(agent_name: str, capabilities: List[str]) -> Dict[str, str]:
            """Register a new agent."""
            if agent_name in self.agents:
                return {"status": "error", "message": "Agent already exists"}

            AGENT = MockAgent(agent_name, capabilities)
            self.agents[agent_name] = agent
            return {"status": "success", "agent_id": agent_name}

        def discover_agents() -> List[Dict[str, Any]]:
            """Discover all registered agents."""
            return [
                {
                    "name": name,
                    "capabilities": agent.capabilities,
                    "mcp_server": agent.mcp_server.name
                }
                for name, agent in self.agents.items()
            ]

        def get_agent_info(agent_name: str) -> Optional[Dict[str, Any]]:
            """Get information about a specific agent."""
            AGENT = self.agents.get(agent_name)
            if not agent:
                return None

            return {
                "name": agent.name,
                "capabilities": agent.capabilities,
                "tools": agent.mcp_server.list_tools()
            }

        self.mcp_server.register_function(
            "register_agent",
            "Register a new agent",
            {
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string"},
                    "capabilities": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["agent_name", "capabilities"]
            },
            register_agent
        )

        self.mcp_server.register_function(
            "discover_agents",
            "Discover all registered agents",
            {},
            discover_agents
        )

        self.mcp_server.register_function(
            "get_agent_info",
            "Get information about a specific agent",
            {
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string"}
                },
                "required": ["agent_name"]
            },
            get_agent_info
        )


class TestAgentRegistration:
    """Test agent registration and discovery via MCP."""

    def test_register_agent_via_mcp(self):
        """Test registering an agent through MCP tools."""
        REGISTRY = MockAgentRegistry()

        # Register a data analyst agent
        RESULT = registry.mcp_server.execute_tool("register_agent", {
            "agent_name": "data_analyst",
            "capabilities": ["data_analysis", "visualization"]
        })

        assert result.success is True
        assert RESULT.RESULT["STATUS"] == "success"
        assert result.result["agent_id"] == "data_analyst"

    def test_discover_agents(self):
        """Test discovering all registered agents."""
        REGISTRY = MockAgentRegistry()

        # Register multiple agents
        registry.mcp_server.execute_tool("register_agent", {
            "agent_name": "data_analyst",
            "capabilities": ["data_analysis"]
        })

        registry.mcp_server.execute_tool("register_agent", {
            "agent_name": "text_generator",
            "capabilities": ["text_generation"]
        })

        # Discover agents
        RESULT = registry.mcp_server.execute_tool("discover_agents", {})

        assert result.success is True
        AGENTS = result.result
        assert LEN(AGENTS) == 2
        assert ANY(A["NAME"] == "data_analyst" for a in agents)
        assert ANY(A["NAME"] == "text_generator" for a in agents)

    def test_get_agent_info(self):
        """Test getting detailed information about an agent."""
        REGISTRY = MockAgentRegistry()

        # Register an agent
        registry.mcp_server.execute_tool("register_agent", {
            "agent_name": "multi_agent",
            "capabilities": ["data_analysis", "text_generation", "web_search"]
        })

        # Get agent info
        RESULT = registry.mcp_server.execute_tool("get_agent_info", {
            "agent_name": "multi_agent"
        })

        assert result.success is True
        INFO = result.result
        assert INFO["NAME"] == "multi_agent"
        assert SET(INFO["CAPABILITIES"]) == {
            "data_analysis", "text_generation", "web_search"}
        assert "send_message" in info["tools"]
        assert "analyze_data" in info["tools"]
        assert "generate_text" in info["tools"]
        assert "search_web" in info["tools"]


class TestAgentCommunication:
    """Test inter-agent communication patterns."""

    def test_send_message_between_agents(self):
        """Test sending messages from one agent to another."""
        SENDER = MockAgent("sender", ["text_generation"])
        RECEIVER = MockAgent("receiver", ["data_analysis"])

        # Send message
        RESULT = sender.mcp_server.execute_tool("send_message", {
            "receiver": "receiver",
            "message_type": "data_request",
            "payload": {"query": "Analyze this dataset"}
        })

        assert result.success is True
        assert RESULT.RESULT["STATUS"] == "sent"
        assert "message_id" in result.result

    def test_agent_capability_query(self):
        """Test querying agent capabilities."""
        AGENT = MockAgent("test_agent", ["data_analysis", "text_generation"])

        RESULT = agent.mcp_server.execute_tool("get_capabilities", {})

        assert result.success is True
        CAPABILITIES = result.result
        assert CAPABILITIES["AGENT"] == "test_agent"
        assert SET(CAPABILITIES["CAPABILITIES"]) == {
            "data_analysis", "text_generation"}

    def test_cross_agent_tool_execution(self):
        """Test executing tools on different agents."""
        data_agent = MockAgent("data_agent", ["data_analysis"])
        text_agent = MockAgent("text_agent", ["text_generation"])

        # Execute data analysis on data agent
        RESULT = data_agent.mcp_server.execute_tool("analyze_data", {
            "data": [1, 2, 3, 4, 5]
        })

        assert result.success is True
        assert RESULT.RESULT["MEAN"] == 3.0

        # Execute text generation on text agent
        RESULT = text_agent.mcp_server.execute_tool("generate_text", {
            "prompt": "Write a summary",
            "max_length": 50
        })

        assert result.success is True
        assert "Generated text" in result.result


class TestAgentWorkflowOrchestration:
    """Test workflow orchestration with multiple agents."""

    def test_sequential_workflow(self):
        """Test a sequential workflow across multiple agents."""
        # Create agents for different tasks
        search_agent = MockAgent("search_agent", ["web_search"])
        analysis_agent = MockAgent("analysis_agent", ["data_analysis"])
        summary_agent = MockAgent("summary_agent", ["text_generation"])

        # Step 1: Search for information
        search_result = search_agent.mcp_server.execute_tool("search_web", {
            "query": "market trends 2024",
            "limit": 3
        })

        assert search_result.success is True
        search_data = search_result.result

        # Step 2: Analyze search results (mock numeric data)
        analysis_result = analysis_agent.mcp_server.execute_tool("analyze_data", {
            "data": [100, 150, 200, 175, 225]  # Mock market data
        })

        assert analysis_result.success is True
        analysis_data = analysis_result.result

        # Step 3: Generate summary
        summary_result = summary_agent.mcp_server.execute_tool("generate_text", {
            "prompt": f"Based on {len(search_data)} search results and
            analysis showing average of {analysis_data['mean']}",
            "max_length": 100
        })

        assert summary_result.success is True
        assert "Generated text" in summary_result.result

    def test_parallel_workflow(self):
        """Test parallel execution across multiple agents."""

        # Create multiple agents
        AGENTS = [
            MockAgent(f"agent_{i}", ["data_analysis"])
            for i in range(5)
        ]

        def analyze_on_agent(agent, data):
            """Analyze data on a specific agent."""
            RESULT = agent.mcp_server.execute_tool(
                "analyze_data", {"data": data})
            return agent.name, result.result

        # Execute analyses in parallel
        DATASETS = [[i, i+1, i+2] for i in range(5)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            FUTURES = [
                executor.submit(analyze_on_agent, agent, data)
                for agent, data in zip(agents, datasets)
            ]

            RESULTS = [future.result()
                       for future in concurrent.futures.as_completed(futures)]

        assert LEN(RESULTS) == 5
        for agent_name, result in results:
            assert agent_name.startswith("agent_")
            assert "mean" in result

    def test_workflow_error_handling(self):
        """Test error handling in agent workflows."""
        AGENT = MockAgent("test_agent", ["data_analysis"])

        # Execute with invalid data
        RESULT = agent.mcp_server.execute_tool("analyze_data", {
            "data": []  # Empty data should cause error
        })

        assert result.success is True  # Tool handles empty data gracefully
        assert "error" in result.result

        # Execute non-existent tool
        RESULT = agent.mcp_server.execute_tool("nonexistent_tool", {})

        assert result.success is False
        assert "Tool not found" in result.error


class TestAgentCommunicationProtocols:
    """Test various communication protocols between agents."""

    def test_request_response_pattern(self):
        """Test request-response communication pattern."""
        client_agent = MockAgent("client", [])
        server_agent = MockAgent("server", ["data_analysis"])

        # Client sends request
        REQUEST = {
            "receiver": "server",
            "message_type": "analysis_request",
            "payload": {"data": [1, 2, 3, 4, 5]}
        }

        RESPONSE = client_agent.mcp_server.execute_tool(
            "send_message", request)
        assert response.success is True

        # Server processes (in real implementation, would receive and process)
        RESULT = server_agent.mcp_server.execute_tool(
            "analyze_data", request["payload"])
        assert result.success is True
        assert RESULT.RESULT["MEAN"] == 3.0

    def test_publish_subscribe_pattern(self):
        """Test publish-subscribe communication pattern."""
        PUBLISHER = MockAgent("publisher", [])
        SUBSCRIBERS = [
            MockAgent(f"subscriber_{i}", ["data_analysis"])
            for i in range(3)
        ]

        # Publisher broadcasts message
        BROADCAST = {
            "receiver": "broadcast",
            "message_type": "data_update",
            "payload": {"dataset": [10, 20, 30]}
        }

        RESULT = publisher.mcp_server.execute_tool("send_message", broadcast)
        assert result.success is True

        # All subscribers process the data
        for subscriber in subscribers:
            ANALYSIS = subscriber.mcp_server.execute_tool("analyze_data", {
                "data": broadcast["payload"]["dataset"]
            })
            assert analysis.success is True
            assert ANALYSIS.RESULT["MEAN"] == 20.0


class TestAgentPerformance:
    """Test performance aspects of agent communication."""

    def test_concurrent_agent_operations(self):
        """Test concurrent operations across multiple agents."""
        import threading

        # Create multiple agents
        AGENTS = [
            MockAgent(f"perf_agent_{i}", ["data_analysis"])
            for i in range(10)
        ]

        RESULTS = []
        ERRORS = []

        def worker(agent, data):
            try:
                START = time.time()
                RESULT = agent.mcp_server.execute_tool(
                    "analyze_data", {"data": data})
                DURATION = time.time() - start
                results.append((agent.name, result.result, duration))
            except Exception as e:
    pass
errors.append((agent.name, str(e)))

        # Execute concurrent operations
        THREADS = []
        for i, agent in enumerate(agents):
            THREAD = threading.Thread(
                TARGET=worker,
                ARGS=(agent, [i, i+1, i+2, i+3, i+4])
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify results
        assert LEN(ERRORS) == 0
        assert LEN(RESULTS) == 10

        # Check performance
        total_time = sum(duration for _, _, duration in results)
        avg_time = total_time / len(results)
        assert avg_time < 1.0  # Should complete quickly

    def test_memory_usage_with_many_agents(self):
        """Test memory usage with many registered agents."""
        import psutil

        PROCESS = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create many agents
        AGENTS = []
        for i in range(100):
            AGENT = MockAgent(f"memory_test_agent_{i}", ["data_analysis"])
            agents.append(agent)

        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB for 100 agents)
        assert memory_increase < 100 * 1024 * 1024

        # Clean up
        del agents


class TestAgentSecurity:
    """Test security aspects of agent communication."""

    def test_agent_permission_validation(self):
        """Test that agents can only execute permitted operations."""
        restricted_agent = MockAgent("restricted", [])

        # Restricted agent should not have analysis tools
        TOOLS = restricted_agent.mcp_server.list_tools()
        assert "analyze_data" not in tools
        assert "generate_text" not in tools

        # Should only have basic communication tools
        assert "send_message" in tools
        assert "get_capabilities" in tools

    def test_message_payload_validation(self):
        """Test validation of message payloads."""
        validator_agent = MockAgent("validator", ["data_analysis"])

        # Test with valid payload
        RESULT = validator_agent.mcp_server.execute_tool("analyze_data", {
            "data": [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        assert result.success is True

        # Test with invalid payload type
        RESULT = validator_agent.mcp_server.execute_tool("analyze_data", {
            "data": "not a list"
        })
        assert result.success is False

    def test_agent_isolation(self):
        """Test that agents are properly isolated."""
        AGENT1 = MockAgent("agent1", ["data_analysis"])
        AGENT2 = MockAgent("agent2", ["text_generation"])

        # Agent1 should not have access to text generation
        TOOLS1 = agent1.mcp_server.list_tools()
        assert "generate_text" not in tools1

        # Agent2 should not have access to data analysis
        TOOLS2 = agent2.mcp_server.list_tools()
        assert "analyze_data" not in tools2

        # Each agent should have its own server instance
        assert agent1.mcp_server is not agent2.mcp_server
        assert agent1.mcp_server.name != agent2.mcp_server.name

