"""
L3 Orchestration Layer Unit Tests - Agent Coordination

Tests for agent coordination and communication without planning logic.
Focuses on agent roles, message passing, and collaborative execution.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import time
import uuid

# Mark all tests in this module as L3 orchestration unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l3, pytest.mark.orchestration]


class AgentRole(Enum):
    """Agent roles in orchestration."""
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    ANALYZER = "analyzer"
    VALIDATOR = "validator"
    SYNTHESIZER = "synthesizer"


class MessageType(Enum):
    """Types of messages between agents."""
    TASK_ASSIGNMENT = "task_assignment"
    STATUS_UPDATE = "status_update"
    RESULT_REPORT = "result_report"
    ERROR_NOTIFICATION = "error_notification"
    COORDINATION_REQUEST = "coordination_request"


@dataclass(frozen=True)
class MockAgent:
    """Mock agent for coordination testing."""
    agent_id: str
    role: AgentRole
    capabilities: List[str]
    status: str
    current_task: Optional[str]
    message_queue: List[Dict[str, Any]]


@dataclass(frozen=True)
class MockMessage:
    """Mock message for agent communication."""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: float


class TestAgentRolesAndCapabilities:
    """Test agent role definitions and capability matching."""
    
    def test_agent_role_definition(self):
        """Test definition and validation of agent roles."""
        
        role_capabilities = {
            AgentRole.COORDINATOR: ["task_assignment", "workflow_management", "resource_allocation"],
            AgentRole.EXECUTOR: ["tool_execution", "parameter_validation", "error_handling"],
            AgentRole.ANALYZER: ["data_analysis", "pattern_recognition", "metric_calculation"],
            AgentRole.VALIDATOR: ["result_validation", "quality_check", "compliance_verification"],
            AgentRole.SYNTHESIZER: ["content_generation", "result_aggregation", "output_formatting"]
        }
        
        # Create agents for each role
        agents = []
        for role, capabilities in role_capabilities.items():
            agent = MockAgent(
                agent_id=f"{role.value}_agent_{uuid.uuid4().hex[:8]}",
                role=role,
                capabilities=capabilities,
                status="idle",
                current_task=None,
                message_queue=[]
            )
            agents.append(agent)
        
        # Validate role definitions
        assert len(agents) == 5
        
        # Validate each agent has correct role and capabilities
        for agent in agents:
            expected_capabilities = role_capabilities[agent.role]
            assert agent.capabilities == expected_capabilities
            assert agent.agent_id.startswith(agent.role.value)
            assert agent.status == "idle"
            assert agent.current_task is None
        
        # Validate specific role characteristics
        coordinator = next(a for a in agents if a.role == AgentRole.COORDINATOR)
        assert "workflow_management" in coordinator.capabilities
        assert "task_assignment" in coordinator.capabilities
        
        executor = next(a for a in agents if a.role == AgentRole.EXECUTOR)
        assert "tool_execution" in executor.capabilities
        assert "error_handling" in executor.capabilities
    
    def test_capability_matching(self):
        """Test matching tasks to agent capabilities."""
        
        # Define task requirements
        task_requirements = [
            {
                "task_id": "analyze_resume",
                "required_capabilities": ["data_analysis", "pattern_recognition"],
                "preferred_role": AgentRole.ANALYZER
            },
            {
                "task_id": "execute_tool",
                "required_capabilities": ["tool_execution", "parameter_validation"],
                "preferred_role": AgentRole.EXECUTOR
            },
            {
                "task_id": "coordinate_workflow",
                "required_capabilities": ["task_assignment", "workflow_management"],
                "preferred_role": AgentRole.COORDINATOR
            },
            {
                "task_id": "validate_results",
                "required_capabilities": ["result_validation", "quality_check"],
                "preferred_role": AgentRole.VALIDATOR
            }
        ]
        
        # Create agent pool
        agents = [
            MockAgent("agent_1", AgentRole.ANALYZER, ["data_analysis", "pattern_recognition"], "idle", None, []),
            MockAgent("agent_2", AgentRole.EXECUTOR, ["tool_execution", "parameter_validation"], "idle", None, []),
            MockAgent("agent_3", AgentRole.COORDINATOR, ["task_assignment", "workflow_management"], "idle", None, []),
            MockAgent("agent_4", AgentRole.VALIDATOR, ["result_validation", "quality_check"], "idle", None, []),
            MockAgent("agent_5", AgentRole.SYNTHESIZER, ["content_generation", "result_aggregation"], "idle", None, [])
        ]
        
        # Mock capability matcher
        class CapabilityMatcher:
            def __init__(self, agents: List[MockAgent]):
                self.agents = agents
            
            def find_matching_agent(self, task: Dict[str, Any]) -> Optional[MockAgent]:
                """Find agent that can handle the task."""
                required_caps = task["required_capabilities"]
                preferred_role = task["preferred_role"]
                
                # First try to find agent with preferred role
                preferred_agents = [a for a in self.agents if a.role == preferred_role]
                
                for agent in preferred_agents:
                    if self._agent_has_capabilities(agent, required_caps):
                        return agent
                
                # Fallback to any agent with required capabilities
                for agent in self.agents:
                    if self._agent_has_capabilities(agent, required_caps):
                        return agent
                
                return None
            
            def _agent_has_capabilities(self, agent: MockAgent, required_caps: List[str]) -> bool:
                """Check if agent has all required capabilities."""
                return all(cap in agent.capabilities for cap in required_caps)
        
        matcher = CapabilityMatcher(agents)
        matching_results = []
        
        for task in task_requirements:
            matched_agent = matcher.find_matching_agent(task)
            matching_results.append({
                "task_id": task["task_id"],
                "matched_agent_id": matched_agent.agent_id if matched_agent else None,
                "matched_role": matched_agent.role if matched_agent else None,
                "success": matched_agent is not None
            })
        
        # Validate capability matching
        assert all(result["success"] for result in matching_results)
        
        # Validate role preferences were respected
        analyze_result = next(r for r in matching_results if r["task_id"] == "analyze_resume")
        assert analyze_result["matched_role"] == AgentRole.ANALYZER
        
        execute_result = next(r for r in matching_results if r["task_id"] == "execute_tool")
        assert execute_result["matched_role"] == AgentRole.EXECUTOR
    
    def test_agent_load_balancing(self):
        """Test load balancing across agents with same capabilities."""
        
        # Create multiple agents with same capabilities
        executor_agents = [
            MockAgent(f"executor_{i}", AgentRole.EXECUTOR, ["tool_execution"], "idle", None, [])
            for i in range(3)
        ]
        
        # Mock load balancer
        class AgentLoadBalancer:
            def __init__(self, agents: List[MockAgent]):
                self.agents = agents
                self.task_assignments = {}
            
            def assign_task(self, task_id: str, required_capability: str) -> Optional[MockAgent]:
                """Assign task to least loaded agent with required capability."""
                capable_agents = [a for a in self.agents if required_capability in a.capabilities]
                
                if not capable_agents:
                    return None
                
                # Find agent with fewest tasks
                least_loaded_agent = min(
                    capable_agents,
                    key=lambda a: len(self.task_assignments.get(a.agent_id, []))
                )
                
                # Assign task
                if least_loaded_agent.agent_id not in self.task_assignments:
                    self.task_assignments[least_loaded_agent.agent_id] = []
                
                self.task_assignments[least_loaded_agent.agent_id].append(task_id)
                
                return least_loaded_agent
            
            def get_load_distribution(self) -> Dict[str, int]:
                """Get current load distribution across agents."""
                return {
                    agent_id: len(tasks)
                    for agent_id, tasks in self.task_assignments.items()
                }
        
        balancer = AgentLoadBalancer(executor_agents)
        
        # Assign multiple tasks
        task_ids = [f"task_{i}" for i in range(10)]
        assigned_agents = []
        
        for task_id in task_ids:
            agent = balancer.assign_task(task_id, "tool_execution")
            assigned_agents.append(agent)
        
        # Validate load balancing
        assert len(assigned_agents) == 10
        assert all(agent is not None for agent in assigned_agents)
        
        # Check load distribution
        load_distribution = balancer.get_load_distribution()
        loads = list(load_distribution.values())
        
        # Load should be distributed relatively evenly
        max_load = max(loads)
        min_load = min(loads)
        assert max_load - min_load <= 1  # Difference should be at most 1
        
        # All agents should have received some tasks
        assert len(load_distribution) == 3


class TestMessagePassing:
    """Test message passing and communication between agents."""
    
    @pytest.mark.asyncio
    async def test_message_creation_and_routing(self):
        """Test creation and routing of messages between agents."""
        
        class MessageRouter:
            def __init__(self):
                self.message_log = []
                self.delivery_log = []
            
            def create_message(self, sender_id: str, receiver_id: str, 
                             message_type: MessageType, payload: Dict[str, Any]) -> MockMessage:
                """Create a new message."""
                message = MockMessage(
                    message_id=f"msg_{uuid.uuid4().hex[:8]}",
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    message_type=message_type,
                    payload=payload,
                    timestamp=time.time()
                )
                
                self.message_log.append(message)
                return message
            
            async def deliver_message(self, message: MockMessage) -> bool:
                """Deliver message to receiver."""
                # Simulate message delivery
                await asyncio.sleep(0.001)
                
                self.delivery_log.append({
                    "message_id": message.message_id,
                    "sender_id": message.sender_id,
                    "receiver_id": message.receiver_id,
                    "delivered_at": time.time()
                })
                
                return True
            
            def get_messages_for_agent(self, agent_id: str) -> List[MockMessage]:
                """Get all messages for a specific agent."""
                return [msg for msg in self.message_log if msg.receiver_id == agent_id]
        
        # Test message creation and routing
        router = MessageRouter()
        
        # Create agents
        sender_agent = MockAgent("agent_1", AgentRole.COORDINATOR, [], "idle", None, [])
        receiver_agent = MockAgent("agent_2", AgentRole.EXECUTOR, [], "idle", None, [])
        
        # Create different types of messages
        messages = [
            router.create_message(
                sender_agent.agent_id,
                receiver_agent.agent_id,
                MessageType.TASK_ASSIGNMENT,
                {"task_id": "task_1", "parameters": {"param": "value"}}
            ),
            router.create_message(
                sender_agent.agent_id,
                receiver_agent.agent_id,
                MessageType.STATUS_UPDATE,
                {"status": "in_progress", "progress": 0.5}
            ),
            router.create_message(
                receiver_agent.agent_id,  # Receiver responds
                sender_agent.agent_id,
                MessageType.RESULT_REPORT,
                {"task_id": "task_1", "result": "completed"}
            )
        ]
        
        # Deliver messages
        delivery_tasks = [router.deliver_message(msg) for msg in messages]
        delivery_results = await asyncio.gather(*delivery_tasks)
        
        # Validate message creation and delivery
        assert len(messages) == 3
        assert all(result is True for result in delivery_results)
        assert len(router.message_log) == 3
        assert len(router.delivery_log) == 3
        
        # Validate message content
        task_message = messages[0]
        assert task_message.message_type == MessageType.TASK_ASSIGNMENT
        assert task_message.sender_id == sender_agent.agent_id
        assert task_message.receiver_id == receiver_agent.agent_id
        assert "task_id" in task_message.payload
        
        # Validate message routing
        agent_2_messages = router.get_messages_for_agent(receiver_agent.agent_id)
        assert len(agent_2_messages) == 2  # task_assignment and status_update
    
    @pytest.mark.asyncio
    async def test_async_message_handling(self):
        """Test asynchronous message handling by agents."""
        
        class AsyncMessageHandler:
            def __init__(self, agent_id: str):
                self.agent_id = agent_id
                self.message_queue = asyncio.Queue()
                self.processed_messages = []
                self.processing = False
            
            async def receive_message(self, message: MockMessage):
                """Receive and queue message."""
                await self.message_queue.put(message)
            
            async def process_messages(self):
                """Process messages from queue."""
                self.processing = True
                
                while True:
                    try:
                        # Get message with timeout
                        message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
                        
                        # Process message
                        await self._handle_message(message)
                        self.processed_messages.append(message.message_id)
                        
                    except asyncio.TimeoutError:
                        # No more messages
                        break
                
                self.processing = False
            
            async def _handle_message(self, message: MockMessage):
                """Handle individual message."""
                await asyncio.sleep(0.01)  # Simulate processing
                
                # Different handling based on message type
                if message.message_type == MessageType.TASK_ASSIGNMENT:
                    # Handle task assignment
                    pass
                elif message.message_type == MessageType.RESULT_REPORT:
                    # Handle result report
                    pass
        
        # Create message handlers
        coordinator_handler = AsyncMessageHandler("coordinator")
        executor_handler = AsyncMessageHandler("executor")
        
        # Create messages
        messages = [
            MockMessage("msg_1", "coordinator", "executor", MessageType.TASK_ASSIGNMENT, 
                      {"task_id": "task_1"}, time.time()),
            MockMessage("msg_2", "coordinator", "executor", MessageType.STATUS_UPDATE, 
                      {"status": "pending"}, time.time()),
            MockMessage("msg_3", "executor", "coordinator", MessageType.RESULT_REPORT, 
                      {"task_id": "task_1", "result": "done"}, time.time())
        ]
        
        # Route messages to appropriate handlers
        routing_tasks = []
        for message in messages:
            if message.receiver_id == "coordinator":
                routing_tasks.append(coordinator_handler.receive_message(message))
            else:
                routing_tasks.append(executor_handler.receive_message(message))
        
        await asyncio.gather(*routing_tasks)
        
        # Start message processing
        processing_tasks = [
            coordinator_handler.process_messages(),
            executor_handler.process_messages()
        ]
        
        await asyncio.gather(*processing_tasks)
        
        # Validate message processing
        assert len(coordinator_handler.processed_messages) == 1
        assert len(executor_handler.processed_messages) == 2
        assert "msg_3" in coordinator_handler.processed_messages
        assert "msg_1" in executor_handler.processed_messages
        assert "msg_2" in executor_handler.processed_messages
    
    def test_message_priority_and_ordering(self):
        """Test message priority handling and ordering."""
        
        class PriorityMessageRouter:
            def __init__(self):
                self.priority_queues = {
                    "high": [],
                    "medium": [],
                    "low": []
                }
                self.delivery_order = []
            
            def get_message_priority(self, message_type: MessageType) -> str:
                """Get priority for message type."""
                priority_map = {
                    MessageType.ERROR_NOTIFICATION: "high",
                    MessageType.COORDINATION_REQUEST: "high",
                    MessageType.TASK_ASSIGNMENT: "medium",
                    MessageType.STATUS_UPDATE: "medium",
                    MessageType.RESULT_REPORT: "low"
                }
                return priority_map.get(message_type, "low")
            
            def queue_message(self, message: MockMessage):
                """Queue message by priority."""
                priority = self.get_message_priority(message.message_type)
                self.priority_queues[priority].append(message)
            
            def get_next_message(self) -> Optional[MockMessage]:
                """Get next message in priority order."""
                # Check high priority first
                if self.priority_queues["high"]:
                    message = self.priority_queues["high"].pop(0)
                    self.delivery_order.append(message.message_id)
                    return message
                
                # Then medium priority
                if self.priority_queues["medium"]:
                    message = self.priority_queues["medium"].pop(0)
                    self.delivery_order.append(message.message_id)
                    return message
                
                # Finally low priority
                if self.priority_queues["low"]:
                    message = self.priority_queues["low"].pop(0)
                    self.delivery_order.append(message.message_id)
                    return message
                
                return None
        
        router = PriorityMessageRouter()
        
        # Create messages with different priorities
        messages = [
            MockMessage("msg_1", "agent_1", "agent_2", MessageType.RESULT_REPORT, 
                      {"data": "result"}, time.time()),  # Low priority
            MockMessage("msg_2", "agent_1", "agent_2", MessageType.ERROR_NOTIFICATION, 
                      {"error": "critical"}, time.time()),  # High priority
            MockMessage("msg_3", "agent_1", "agent_2", MessageType.TASK_ASSIGNMENT, 
                      {"task": "new_task"}, time.time()),  # Medium priority
            MockMessage("msg_4", "agent_1", "agent_2", MessageType.COORDINATION_REQUEST, 
                      {"request": "urgent"}, time.time()),  # High priority
            MockMessage("msg_5", "agent_1", "agent_2", MessageType.STATUS_UPDATE, 
                      {"status": "progress"}, time.time())  # Medium priority
        ]
        
        # Queue messages in random order
        import random
        random.shuffle(messages)
        
        for message in messages:
            router.queue_message(message)
        
        # Deliver messages in priority order
        delivered_messages = []
        while True:
            message = router.get_next_message()
            if message is None:
                break
            delivered_messages.append(message)
        
        # Validate priority ordering
        assert len(delivered_messages) == 5
        
        # High priority messages should come first
        high_priority_messages = [msg for msg in delivered_messages[:2] 
                                if msg.message_type in [MessageType.ERROR_NOTIFICATION, 
                                                      MessageType.COORDINATION_REQUEST]]
        assert len(high_priority_messages) == 2
        
        # Medium priority messages should come next
        medium_priority_messages = [msg for msg in delivered_messages[2:4] 
                                  if msg.message_type in [MessageType.TASK_ASSIGNMENT, 
                                                        MessageType.STATUS_UPDATE]]
        assert len(medium_priority_messages) == 2
        
        # Low priority should come last
        assert delivered_messages[-1].message_type == MessageType.RESULT_REPORT


class TestCollaborativeExecution:
    """Test collaborative execution patterns across multiple agents."""
    
    @pytest.mark.asyncio
    async def test_coordinator_executor_pattern(self):
        """Test coordinator-executor collaboration pattern."""
        
        class MockCoordinator:
            def __init__(self, agent_id: str):
                self.agent_id = agent_id
                self.task_queue = asyncio.Queue()
                self.executors = {}
                self.completed_tasks = {}
            
            def register_executor(self, executor_agent: MockAgent):
                """Register an executor agent."""
                self.executors[executor_agent.agent_id] = executor_agent
            
            async def assign_task(self, task: Dict[str, Any]) -> str:
                """Assign task to available executor."""
                # Find idle executor
                idle_executors = [eid for eid, agent in self.executors.items() 
                                if agent.status == "idle"]
                
                if not idle_executors:
                    raise Exception("No available executors")
                
                executor_id = idle_executors[0]
                await self.task_queue.put({"task": task, "executor_id": executor_id})
                
                return executor_id
            
            async def coordinate_execution(self):
                """Coordinate task execution."""
                while True:
                    try:
                        assignment = await asyncio.wait_for(self.task_queue.get(), timeout=0.1)
                        task = assignment["task"]
                        executor_id = assignment["executor_id"]
                        
                        # Simulate task assignment
                        await asyncio.sleep(0.01)
                        
                        self.completed_tasks[task["task_id"]] = {
                            "executor_id": executor_id,
                            "status": "assigned"
                        }
                        
                    except asyncio.TimeoutError:
                        break
        
        class MockExecutor:
            def __init__(self, agent: MockAgent):
                self.agent = agent
                self.assigned_tasks = []
            
            async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
                """Execute assigned task."""
                self.agent.status = "busy"
                self.agent.current_task = task["task_id"]
                
                # Simulate task execution
                await asyncio.sleep(0.02)
                
                result = {
                    "task_id": task["task_id"],
                    "executor_id": self.agent.agent_id,
                    "result": f"Completed {task['task_type']}",
                    "execution_time": 0.02
                }
                
                self.agent.status = "idle"
                self.agent.current_task = None
                self.assigned_tasks.append(task["task_id"])
                
                return result
        
        # Create coordinator and executors
        coordinator = MockCoordinator("coordinator_1")
        
        executors = [
            MockExecutor(MockAgent(f"executor_{i}", AgentRole.EXECUTOR, ["tool_execution"], "idle", None, []))
            for i in range(3)
        ]
        
        # Register executors
        for executor in executors:
            coordinator.register_executor(executor.agent)
        
        # Create tasks
        tasks = [
            {"task_id": "task_1", "task_type": "analysis", "parameters": {}},
            {"task_id": "task_2", "task_type": "validation", "parameters": {}},
            {"task_id": "task_3", "task_type": "synthesis", "parameters": {}},
            {"task_id": "task_4", "task_type": "execution", "parameters": {}},
            {"task_id": "task_5", "task_type": "formatting", "parameters": {}}
        ]
        
        # Assign tasks
        assignment_tasks = [coordinator.assign_task(task) for task in tasks]
        assignment_results = await asyncio.gather(*assignment_tasks)
        
        # Start coordination
        coordination_task = asyncio.create_task(coordinator.coordinate_execution())
        await asyncio.sleep(0.05)  # Let coordination process
        coordination_task.cancel()
        
        # Validate task assignment
        assert len(assignment_results) == 5
        assert all(result in ["executor_0", "executor_1", "executor_2"] for result in assignment_results)
        
        # Validate coordinator tracking
        assert len(coordinator.completed_tasks) == 5
        assert all(task["task_id"] in coordinator.completed_tasks for task in tasks)
    
    @pytest.mark.asyncio
    async def test_pipeline_agent_pattern(self):
        """Test pipeline pattern where agents process data sequentially."""
        
        class PipelineAgent:
            def __init__(self, agent_id: str, stage: str, processing_time: float):
                self.agent_id = agent_id
                self.stage = stage
                self.processing_time = processing_time
                self.input_queue = asyncio.Queue()
                self.output_queue = asyncio.Queue()
                self.processed_count = 0
            
            async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
                """Process data through this stage."""
                await asyncio.sleep(self.processing_time)
                
                processed_data = data.copy()
                processed_data["stages_completed"] = data.get("stages_completed", []) + [self.stage]
                processed_data[f"{self.stage}_output"] = f"Processed by {self.agent_id}"
                
                self.processed_count += 1
                return processed_data
            
            async def run_pipeline_stage(self):
                """Run the pipeline stage continuously."""
                while True:
                    try:
                        data = await asyncio.wait_for(self.input_queue.get(), timeout=0.1)
                        processed_data = await self.process_data(data)
                        await self.output_queue.put(processed_data)
                        
                    except asyncio.TimeoutError:
                        break
        
        # Create pipeline stages
        stages = [
            PipelineAgent("stage_1", "extraction", 0.01),
            PipelineAgent("stage_2", "analysis", 0.015),
            PipelineAgent("stage_3", "validation", 0.01),
            PipelineAgent("stage_4", "synthesis", 0.02)
        ]
        
        # Connect pipeline stages
        for i in range(len(stages) - 1):
            stages[i].output_queue = stages[i + 1].input_queue
        
        # Start all stages
        stage_tasks = [stage.run_pipeline_stage() for stage in stages]
        
        # Submit initial data
        initial_data = {"input": "test_data", "stages_completed": []}
        await stages[0].input_queue.put(initial_data)
        
        # Let pipeline process
        await asyncio.sleep(0.1)
        
        # Stop pipeline stages
        for task in stage_tasks:
            task.cancel()
        
        # Validate pipeline processing
        final_output = None
        try:
            final_output = await asyncio.wait_for(stages[-1].output_queue.get(), timeout=0.01)
        except asyncio.TimeoutError:
            pass
        
        assert final_output is not None
        assert final_output["stages_completed"] == ["extraction", "analysis", "validation", "synthesis"]
        assert "extraction_output" in final_output
        assert "synthesis_output" in final_output
        
        # Validate each stage processed data
        for stage in stages:
            assert stage.processed_count == 1
    
    @pytest.mark.asyncio
    async def test_dynamic_agent_formation(self):
        """Test dynamic formation of agent teams for complex tasks."""
        
        class AgentTeamManager:
            def __init__(self):
                self.available_agents = {}
                self.active_teams = {}
                self.team_assignments = {}
            
            def register_agent(self, agent: MockAgent):
                """Register an available agent."""
                self.available_agents[agent.agent_id] = agent
            
            def form_team(self, task_requirements: List[str], team_id: str) -> List[str]:
                """Form a team of agents to handle task requirements."""
                selected_agents = []
                remaining_requirements = task_requirements.copy()
                
                # Greedy team formation
                while remaining_requirements:
                    best_agent = None
                    best_coverage = 0
                    
                    for agent_id, agent in self.available_agents.items():
                        # Skip already assigned agents
                        if agent_id in [a for team in self.active_teams.values() for a in team]:
                            continue
                        
                        # Calculate capability coverage
                        coverage = len(set(agent.capabilities) & set(remaining_requirements))
                        if coverage > best_coverage:
                            best_coverage = coverage
                            best_agent = agent_id
                    
                    if best_agent is None:
                        break  # No more suitable agents
                    
                    selected_agents.append(best_agent)
                    self.active_teams[team_id] = selected_agents
                    
                    # Remove covered requirements
                    agent_caps = self.available_agents[best_agent].capabilities
                    remaining_requirements = [req for req in remaining_requirements if req not in agent_caps]
                
                return selected_agents
            
            def disband_team(self, team_id: str):
                """Disband a team and release agents."""
                if team_id in self.active_teams:
                    del self.active_teams[team_id]
        
        # Create diverse agent pool
        agents = [
            MockAgent("agent_1", AgentRole.ANALYZER, ["data_analysis", "pattern_recognition"], "idle", None, []),
            MockAgent("agent_2", AgentRole.EXECUTOR, ["tool_execution", "parameter_validation"], "idle", None, []),
            MockAgent("agent_3", AgentRole.VALIDATOR, ["result_validation", "quality_check"], "idle", None, []),
            MockAgent("agent_4", AgentRole.SYNTHESIZER, ["content_generation", "result_aggregation"], "idle", None, []),
            MockAgent("agent_5", AgentRole.ANALYZER, ["metric_calculation", "statistical_analysis"], "idle", None, [])
        ]
        
        team_manager = AgentTeamManager()
        
        # Register agents
        for agent in agents:
            team_manager.register_agent(agent)
        
        # Form teams for different tasks
        team_1_requirements = ["data_analysis", "tool_execution", "result_validation"]
        team_2_requirements = ["content_generation", "pattern_recognition", "quality_check"]
        team_3_requirements = ["metric_calculation", "parameter_validation", "result_aggregation"]
        
        team_1 = team_manager.form_team(team_1_requirements, "team_1")
        team_2 = team_manager.form_team(team_2_requirements, "team_2")
        team_3 = team_manager.form_team(team_3_requirements, "team_3")
        
        # Validate team formation
        assert len(team_1) >= 2  # Should cover most requirements
        assert len(team_2) >= 2
        assert len(team_3) >= 2
        
        # Validate no agent is in multiple teams
        all_team_agents = team_1 + team_2 + team_3
        assert len(all_team_agents) == len(set(all_team_agents))
        
        # Validate capability coverage
        def get_team_capabilities(team: List[str]) -> Set[str]:
            caps = set()
            for agent_id in team:
                caps.update(team_manager.available_agents[agent_id].capabilities)
            return caps
        
        team_1_caps = get_team_capabilities(team_1)
        team_2_caps = get_team_capabilities(team_2)
        team_3_caps = get_team_capabilities(team_3)
        
        assert set(team_1_requirements).issubset(team_1_caps)
        assert set(team_2_requirements).issubset(team_2_caps)
        assert set(team_3_requirements).issubset(team_3_caps)
