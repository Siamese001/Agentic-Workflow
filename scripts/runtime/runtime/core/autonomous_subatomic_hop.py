"""
Autonomous Subatomic Hop - Enhanced with Cognitive Autonomy

Integrates episodic memory, reasoning kernel, dynamic tool discovery,
and recursive planning into the SubatomicHop architecture.
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field

# Import base components
from .subatomic_hop import (
    SubatomicHop,
    SubatomicHopConfig,
    MicroStage
)

# Import autonomy components
from agentic_core.L1_cognition.episodic_memory import (
    EpisodicMemory,
    create_episodic_memory
)
from .reasoning_kernel import (
    ReasoningKernel,
    create_reasoning_kernel
)
from agentic_core.L2_execution.tool_registry import (
    ToolRegistry,
    create_tool_registry
)
from apps_rg.L3_orchestration.recursive_agent import (
    RecursivePlannerAgent,
    create_recursive_planner
)

# Import hardening components
from agentic_core.L4_state.storage import create_storage_adapter
from agentic_core.L2_execution.mcp_manager import create_mcp_manager

logger = logging.getLogger(__name__)


@dataclass
class AutonomyConfig:
    """Configuration for autonomy features."""
    enable_episodic_memory: bool = False
    enable_reasoning_kernel: bool = False
    enable_dynamic_tools: bool = False
    enable_recursive_planning: bool = False
    
    # Episodic Memory settings
    memory_similarity_threshold: float = 0.85
    memory_min_rating: float = 0.6
    
    # Reasoning Kernel settings
    reasoning_max_candidates: int = 3
    reasoning_critique_threshold: float = 0.7
    enable_tree_of_thoughts: bool = True
    
    # Tool Registry settings
    tool_max_matches: int = 5
    tool_min_relevance: float = 0.6
    
    # Recursive Planner settings
    planner_max_depth: int = 3
    planner_max_parallel: int = 5


@dataclass
class AutonomousHopConfig(SubatomicHopConfig):
    """Extended configuration for autonomous hops."""
    autonomy: AutonomyConfig = field(default_factory=AutonomyConfig)
    
    # Storage for episodic memory
    storage_type: str = "local"
    storage_path: str = "./agent_memory_store"


class AutonomousSubatomicHop(SubatomicHop):
    """
    Enhanced SubatomicHop with cognitive autonomy capabilities.
    
    Adds:
    - Episodic memory for learning from past experiences
    - Reasoning kernel for System 2 thinking
    - Dynamic tool discovery
    - Recursive planning for complex goals
    """
    
    def __init__(
        self,
        hop_function: Callable,
        config: Optional[AutonomousHopConfig] = None,
        initial_context: Optional[Dict[str, Any]] = None,
        container: Optional[Any] = None
    ):
        """Initialize the autonomous hop."""
        
        # Initialize base class first
        super().__init__(hop_function, config, initial_context, container)
        
        # Autonomy-specific initialization
        self.autonomy_config = config.autonomy if config else AutonomyConfig()
        
        # Initialize autonomy components based on config
        self.episodic_memory: Optional[EpisodicMemory] = None
        self.reasoning_kernel: Optional[ReasoningKernel] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.recursive_planner: Optional[RecursivePlannerAgent] = None
        self.mcp_manager: Optional[Any] = None
        
        # Execution tracking for autonomy
        self.memory_context: Optional[str] = None
        self.reasoning_trace: Optional[Any] = None
        self.selected_tools: List[Any] = []
        
        # Initialize components
        self._initialize_autonomy_components()
    
    def _initialize_autonomy_components(self):
        """Initialize autonomy components based on configuration."""
        
        # Initialize episodic memory
        if self.autonomy_config.enable_episodic_memory:
            self._initialize_episodic_memory()
        
        # Initialize reasoning kernel
        if self.autonomy_config.enable_reasoning_kernel:
            self._initialize_reasoning_kernel()
        
        # Initialize tool registry
        if self.autonomy_config.enable_dynamic_tools:
            self._initialize_tool_registry()
        
        # Initialize recursive planner
        if self.autonomy_config.enable_recursive_planning:
            self._initialize_recursive_planner()
        
        # Initialize MCP manager if needed
        if self.autonomy_config.enable_dynamic_tools:
            self._initialize_mcp_manager()
    
    def _initialize_episodic_memory(self):
        """Initialize episodic memory system."""
        try:
            # Create storage adapter
            storage = create_storage_adapter(
                adapter_type=self.config.storage_type,
                base_path=self.config.storage_path
            )
            
            # Create embedder (reuse from container if available)
            embedder = self._get_embedder()
            
            # Create episodic memory
            self.episodic_memory = create_episodic_memory(
                storage_adapter=storage,
                embedder=embedder,
                similarity_threshold=self.autonomy_config.memory_similarity_threshold
            )
            
            logger.info("Episodic memory initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize episodic memory: {e}")
    
    def _initialize_reasoning_kernel(self):
        """Initialize reasoning kernel for System 2 thinking."""
        try:
            # Get LLM client from container
            llm_client = self._get_llm_client()
            
            # Create reasoning kernel
            self.reasoning_kernel = create_reasoning_kernel(
                llm_client=llm_client,
                max_candidates=self.autonomy_config.reasoning_max_candidates,
                critique_threshold=self.autonomy_config.reasoning_critique_threshold,
                enable_tree_of_thoughts=self.autonomy_config.enable_tree_of_thoughts
            )
            
            logger.info("Reasoning kernel initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize reasoning kernel: {e}")
    
    def _initialize_tool_registry(self):
        """Initialize dynamic tool registry."""
        try:
            # Get embedder
            embedder = self._get_embedder()
            
            # Create tool registry
            self.tool_registry = create_tool_registry(
                embedder=embedder,
                enable_caching=True
            )
            
            # Register built-in tools
            self._register_builtin_tools()
            
            logger.info("Tool registry initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize tool registry: {e}")
    
    def _initialize_recursive_planner(self):
        """Initialize recursive planner for complex goals."""
        try:
            # Get required dependencies
            architect = self._get_workflow_architect()
            orchestrator_factory = self._get_orchestrator_factory()
            
            # Create recursive planner
            self.recursive_planner = create_recursive_planner(
                architect=architect,
                orchestrator_factory=orchestrator_factory,
                max_depth=self.autonomy_config.planner_max_depth,
                max_parallel_subtasks=self.autonomy_config.planner_max_parallel
            )
            
            logger.info("Recursive planner initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize recursive planner: {e}")
    
    def _initialize_mcp_manager(self):
        """Initialize MCP manager for tool discovery."""
        try:
            # Get agent role from context
            role = self.context.get("agent_role", "RESEARCHER")
            
            # Create MCP manager
            self.mcp_manager = create_mcp_manager(role=role)
            
            # Register MCP tools in registry
            if self.tool_registry:
                self._register_mcp_tools()
            
            logger.info("MCP manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP manager: {e}")
    
    async def execute_stage(self, stage: MicroStage, **kwargs) -> Any:
        """
        Execute a stage with autonomy enhancements.
        
        Overrides base method to add autonomy features.
        """
        # Record stage start for telemetry
        if hasattr(self, 'telemetry'):
            self.telemetry.record_event({
                "event_type": f"{stage.name}_START",
                "payload": {"stage": stage.name}
            })
        
        try:
            # Stage-specific autonomy enhancements
            if stage == MicroStage.THINK:
                return await self._execute_think_with_autonomy(**kwargs)
            elif stage == MicroStage.ACT:
                return await self._execute_act_with_dynamic_tools(**kwargs)
            elif stage == MicroStage.CRITIQUE:
                return await self._execute_critique_with_memory(**kwargs)
            else:
                # Use base implementation for other stages
                return await super().execute_stage(stage, **kwargs)
                
        except Exception as e:
            logger.error(f"Stage {stage} failed with autonomy: {e}")
            # Fallback to base implementation
            return await super().execute_stage(stage, **kwargs)
    
    async def _execute_think_with_autonomy(self, **kwargs) -> Any:
        """Execute THINK stage with autonomy enhancements."""
        
        # Recall relevant experience from episodic memory
        if self.episodic_memory:
            task_description = kwargs.get("goal", str(kwargs))
            agent_role = self.context.get("agent_role")
            
            self.memory_context = await self.episodic_memory.recall_relevant_experience(
                current_task=task_description,
                agent_role=agent_role,
                min_rating=self.autonomy_config.memory_min_rating
            )
            
            if self.memory_context:
                logger.debug("Retrieved relevant episodic memory")
        
        # Use reasoning kernel for deliberation
        if self.reasoning_kernel:
            context = {
                **self.context,
                "memory": self.memory_context
            }
            
            goal = kwargs.get("goal", "Complete the task")
            constraints = kwargs.get("constraints", [])
            
            plan, self.reasoning_trace = await self.reasoning_kernel.deliberate(
                context=context,
                goal=goal,
                constraints=constraints,
                memory_context=self.memory_context
            )
            
            logger.info(f"Reasoning completed with confidence: {self.reasoning_trace.confidence:.2f}")
            return plan
        
        # Fallback to base implementation
        return await super().execute_stage(MicroStage.THINK, **kwargs)
    
    async def _execute_act_with_dynamic_tools(self, **kwargs) -> Any:
        """Execute ACT stage with dynamic tool discovery."""
        
        # Discover tools for the task
        if self.tool_registry:
            task_description = kwargs.get("plan", str(kwargs))
            
            tool_matches = await self.tool_registry.find_tools_for_task(
                task_description=task_description,
                max_tools=self.autonomy_config.tool_max_matches,
                min_relevance=self.autonomy_config.tool_min_relevance
            )
            
            if tool_matches:
                logger.info(f"Found {len(tool_matches)} relevant tools")
                
                # Load tools into execution context
                self.selected_tools = []
                for match in tool_matches:
                    tool = match.tool
                    self.selected_tools.append({
                        "name": tool.name,
                        "function": tool.function,
                        "relevance": match.relevance_score
                    })
                
                # Add tools to context
                kwargs["available_tools"] = self.selected_tools
        
        # Use recursive planner for complex tasks
        if self.recursive_planner:
            goal = kwargs.get("goal", "")
            
            # Check if this is a complex task requiring planning
            if self._is_complex_task(goal):
                logger.info("Using recursive planner for complex task")
                
                result = await self.recursive_planner.plan_and_execute(
                    complex_goal=goal,
                    context=self.context,
                    current_depth=0
                )
                
                return result
        
        # Fallback to base implementation
        return await super().execute_stage(MicroStage.ACT, **kwargs)
    
    async def _execute_critique_with_memory(self, **kwargs) -> Any:
        """Execute CRITIQUE stage with memory integration."""
        
        # Execute base critique
        critique_result = await super().execute_stage(MicroStage.CRITIQUE, **kwargs)
        
        # If critique failed and we have episodic memory, check for past failures
        if (self.episodic_memory and 
            hasattr(critique_result, 'score') and 
            critique_result.score < 0.5):
            
            kwargs.get("goal", "")
            
            # Analyze failure patterns
            failure_patterns = await self.episodic_memory.analyze_failure_patterns(
                agent_role=self.context.get("agent_role")
            )
            
            if failure_patterns:
                logger.info(f"Identified failure patterns: {failure_patterns}")
                
                # Add failure insights to critique result
                if hasattr(critique_result, 'feedback'):
                    critique_result.feedback += f"\n\nPAST FAILURE PATTERNS: {failure_patterns}"
        
        return critique_result
    
    async def commit_execution_to_memory(
        self,
        task: str,
        plan: str,
        result: Any,
        success: bool,
        tools_used: Optional[List[str]] = None
    ):
        """Commit the execution to episodic memory."""
        
        if not self.episodic_memory:
            return
        
        # Calculate rating based on success and critique score
        rating = 1.0 if success else 0.0
        
        if hasattr(self, 'last_critique_result') and self.last_critique_result:
            # Adjust rating based on critique
            rating *= getattr(self.last_critique_result, 'score', 1.0)
        
        # Extract failure notes if applicable
        failure_notes = None
        if not success and hasattr(result, 'error'):
            failure_notes = result.error
        
        # Commit to memory
        await self.episodic_memory.commit_episode(
            task=task,
            plan=plan,
            result=str(result),
            tools_used=tools_used or [t["name"] for t in self.selected_tools],
            rating=rating,
            agent_role=self.context.get("agent_role", "UNKNOWN"),
            execution_context=self.context,
            failure_notes=failure_notes
        )
        
        logger.info(f"Committed execution to memory (rating={rating:.2f})")
    
    def _get_embedder(self):
        """Get embedder from container or create default."""
        # This would be implemented based on your embedder setup
        # For now, return a mock embedder
        class MockEmbedder:
            async def embed_query(self, text):
                # Simple mock embedding
                import hashlib
                hash_obj = hashlib.md5(text.encode())
                # Convert to float array
                return [float(int(c, 16)) / 15.0 for c in hash_obj.hexdigest()[:32]]
        
        return MockEmbedder()
    
    def _get_llm_client(self):
        """Get LLM client from container."""
        # This would be implemented based on your LLM setup
        class MockLLMClient:
            async def generate(self, prompt):
                return f"Generated response for: {prompt[:50]}..."
            
            async def evaluate(self, prompt):
                return 0.7  # Mock score
        
        return MockLLMClient()
    
    def _get_workflow_architect(self):
        """Get workflow architect from container."""
        # Mock implementation
        class MockArchitect:
            llm = self._get_llm_client()
        
        return MockArchitect()
    
    def _get_orchestrator_factory(self):
        """Get orchestrator factory from container."""
        # Mock implementation
        class MockOrchestratorFactory:
            def create(self):
                class MockOrchestrator:
                    async def execute_graph(self, graph, initial_inputs):
                        return {"result": "Mock execution"}
                return MockOrchestrator()
            
            def create_hop(self, role):
                class MockHop:
                    async def run(self, **kwargs):
                        return {"output": f"Mock {role} output"}
                return MockHop()
        
        return MockOrchestratorFactory()
    
    def _register_builtin_tools(self):
        """Register built-in tools in the registry."""
        
        def read_file_tool(filepath: str):
            """Read a file from disk."""
            with open(filepath, 'r') as f:
                return f.read()
        
        def write_file_tool(filepath: str, content: str):
            """Write content to a file."""
            with open(filepath, 'w') as f:
                f.write(content)
            return "File written successfully"
        
        def calculate_tool(expression: str):
            """Calculate mathematical expressions."""
            try:
                return eval(expression)
            except:
                return "Invalid expression"
        
        # Register tools
        self.tool_registry.register(
            name="read_file",
            func=read_file_tool,
            description="Read text from a file",
            category="filesystem"
        )
        
        self.tool_registry.register(
            name="write_file",
            func=write_file_tool,
            description="Write text to a file",
            category="filesystem"
        )
        
        self.tool_registry.register(
            name="calculate",
            func=calculate_tool,
            description="Calculate mathematical expressions",
            category="utility"
        )
    
    def _register_mcp_tools(self):
        """Register MCP tools in the registry."""
        if not self.mcp_manager or not self.tool_registry:
            return
        
        # Get available MCP tools
        mcp_tools = self.mcp_manager.get_tools_schema()
        
        for tool in mcp_tools:
            # Create wrapper function for MCP tool
            def create_mcp_wrapper(tool_name):
                async def mcp_wrapper(**kwargs):
                    return await self.mcp_manager.execute_tool(tool_name, kwargs)
                return mcp_wrapper
            
            self.tool_registry.register(
                name=tool["name"],
                func=create_mcp_wrapper(tool["name"]),
                description=tool["description"],
                category="mcp"
            )
    
    def _is_complex_task(self, goal: str) -> bool:
        """Determine if a task is complex enough for recursive planning."""
        # Simple heuristic: check for complexity indicators
        complexity_indicators = [
            "analyze", "design", "implement", "create", "build",
            "multiple", "several", "various", "complex"
        ]
        
        goal_lower = goal.lower()
        return any(indicator in goal_lower for indicator in complexity_indicators)


def create_autonomous_hop(
    hop_function: Callable,
    config: Optional[AutonomousHopConfig] = None,
    initial_context: Optional[Dict[str, Any]] = None,
    container: Optional[Any] = None
) -> AutonomousSubatomicHop:
    """
    Factory function to create an autonomous subatomic hop.
    
    Args:
        hop_function: The function to execute
        config: Autonomous hop configuration
        initial_context: Initial context
        container: Service container
        
    Returns:
        AutonomousSubatomicHop instance
    """
    return AutonomousSubatomicHop(
        hop_function=hop_function,
        config=config,
        initial_context=initial_context,
        container=container
    )
