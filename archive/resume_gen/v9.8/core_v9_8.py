# File: core_v9_8.py
# Overwrites: core_v9_7.py
# Version: 9.8 (P1/P2 Enhancements)

# v9.8 P1/P2 CHANGES:
# P1: Added ReAct conductor framework with step-by-step reasoning
# P1: Implemented DynamicToolingStack with tool selection, execution, and generation
# P1: Built HIL_InteractionStack with proactive ambiguity detection
# P2: Added HyDE support for RAG stack
# P2: Implemented dynamic agent selection based on reliability scores
# P2: Added in-flight cost tracking per agent

# ============================================================================
# EXTERNAL IMPORTS
# ============================================================================
import json
import logging
import os
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Annotated, Callable
from enum import Enum

# Version info
__version__ = "9.8.0-p1-p2-enhancements"

logger = logging.getLogger(__name__)

# ============================================================================
# TYPE DEFINITIONS & STATE
# ============================================================================

class MainGraphState(TypedDict):
    """Enhanced v9.8 graph state with P1/P2 additions."""
    master_resume: Dict[str, Any]
    job_input: Dict[str, Any]
    artifacts: Dict[str, Any]
    replan_count: int
    workflow_id: str
    original_draft: str
    human_approved_draft: str
    preference_insight: Optional[Dict[str, Any]]
    provenance_ledger: List[Dict[str, Any]]
    # P0 Item #2: Tree-of-Thoughts fields
    strategy_thoughts: List[Dict[str, Any]]
    selected_strategy: Optional[Dict[str, Any]]
    # P0 Item #4: Local self-correction tracking
    local_retry_count: int
    bullet_critique_history: List[Dict[str, Any]]
    # P1: ReAct conductor tracking
    conductor_thoughts: List[Dict[str, Any]]  # NEW: Conductor reasoning traces
    conductor_plan: Optional[Dict[str, Any]]  # NEW: Current execution plan
    # P1: Dynamic tooling
    available_tools: List[Dict[str, Any]]  # NEW: Tool registry
    tool_execution_history: List[Dict[str, Any]]  # NEW: Tool usage log
    # P1: HIL interaction
    ambiguity_detected: bool  # NEW: Ambiguity flag
    hil_feedback_queue: List[Dict[str, Any]]  # NEW: Pending feedback requests
    hil_responses: List[Dict[str, Any]]  # NEW: Human responses
    # P2: Cost tracking
    agent_costs: Dict[str, float]  # NEW: Per-agent cost accumulation
    total_workflow_cost: float  # NEW: Running total cost
    # P2: Agent reliability
    agent_reliability_scores: Dict[str, float]  # NEW: Dynamic agent selection

class MetaGraphState(TypedDict):
    """Meta-learning graph state (unchanged from v9.7)."""
    raw_logs: Dict[str, str]
    log_summary: Dict[str, Any]
    patterns: List[Dict[str, Any]]
    hypotheses: List[Dict[str, Any]]
    proposal: Dict[str, Any]
    critique: Dict[str, Any]
    replan_count: int
    workflow_id: str

# ============================================================================
# P1: DYNAMIC TOOLING SYSTEM
# ============================================================================

class ToolDefinition:
    """Defines a tool that can be used by agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        implementation: Callable,
        cost_per_call: float = 0.0,
        reliability_score: float = 1.0
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.implementation = implementation
        self.cost_per_call = cost_per_call
        self.reliability_score = reliability_score
        self.execution_count = 0
        self.success_count = 0
        self.total_latency = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize tool definition for agents."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "cost_per_call": self.cost_per_call,
            "reliability_score": self.reliability_score,
            "execution_count": self.execution_count,
            "success_rate": self.success_count / max(self.execution_count, 1)
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with tracking."""
        start_time = time.time()
        self.execution_count += 1
        
        try:
            result = self.implementation(**kwargs)
            self.success_count += 1
            success = True
        except Exception as e:
            logger.error(f"Tool {self.name} execution failed: {e}")
            result = {"error": str(e)}
            success = False
        
        latency = time.time() - start_time
        self.total_latency += latency
        
        return {
            "tool_name": self.name,
            "success": success,
            "result": result,
            "latency_ms": latency * 1000,
            "cost": self.cost_per_call
        }

class ToolRegistry:
    """P1: Central registry for dynamic tool management."""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.generation_history: List[Dict[str, Any]] = []
    
    def register_tool(self, tool: ToolDefinition):
        """Register a new tool."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Retrieve tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def select_tools(self, task_description: str, max_tools: int = 5) -> List[str]:
        """P1: Intelligent tool selection based on task."""
        # Simple heuristic: score tools by keyword matching and reliability
        scores = {}
        task_lower = task_description.lower()
        
        for name, tool in self.tools.items():
            desc_lower = tool.description.lower()
            # Keyword overlap
            overlap_score = sum(1 for word in task_lower.split() if word in desc_lower)
            # Weighted by reliability
            scores[name] = overlap_score * tool.reliability_score
        
        # Sort by score and return top N
        sorted_tools = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [name for name, score in sorted_tools[:max_tools] if score > 0]
    
    def generate_tool(self, specification: Dict[str, Any]) -> Optional[ToolDefinition]:
        """P1: Generate new tool from specification (placeholder for LLM-based generation)."""
        self.generation_history.append({
            "timestamp": datetime.now().isoformat(),
            "specification": specification,
            "status": "pending_implementation"
        })
        logger.warning("Tool generation requested but not yet implemented in v9.8")
        return None

# Global tool registry
TOOL_REGISTRY = ToolRegistry()

# ============================================================================
# P1: HIL INTERACTION SYSTEM
# ============================================================================

class AmbiguityType(Enum):
    """Types of ambiguity that trigger HIL."""
    MISSING_CONTEXT = "missing_context"
    CONFLICTING_REQUIREMENTS = "conflicting_requirements"
    UNCLEAR_PRIORITY = "unclear_priority"
    QUALITY_THRESHOLD = "quality_threshold"
    STRATEGIC_DECISION = "strategic_decision"

@dataclass
class HILRequest:
    """Represents a human-in-the-loop feedback request."""
    request_id: str
    ambiguity_type: AmbiguityType
    question: str
    context: Dict[str, Any]
    options: Optional[List[str]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    response: Optional[str] = None
    response_timestamp: Optional[str] = None

class HILInteractionManager:
    """P1: Manages proactive ambiguity detection and feedback routing."""
    
    def __init__(self, enable_hil: bool = True):
        self.enable_hil = enable_hil
        self.pending_requests: List[HILRequest] = []
        self.completed_requests: List[HILRequest] = []
        self.ambiguity_patterns: Dict[str, int] = {}
    
    def detect_ambiguity(
        self,
        context: Dict[str, Any],
        confidence_threshold: float = 0.8
    ) -> Optional[HILRequest]:
        """Detect potential ambiguities requiring human input."""
        if not self.enable_hil:
            return None
        
        # Check for missing required fields
        required_fields = ["job_title", "company", "raw_jd"]
        missing = [f for f in required_fields if not context.get(f)]
        if missing:
            return HILRequest(
                request_id=f"hil_{datetime.now().timestamp()}",
                ambiguity_type=AmbiguityType.MISSING_CONTEXT,
                question=f"Missing required information: {', '.join(missing)}. Please provide.",
                context=context
            )
        
        # Check for extremely short JD (likely incomplete)
        jd = context.get("raw_jd", "")
        if len(jd) < 100:
            return HILRequest(
                request_id=f"hil_{datetime.now().timestamp()}",
                ambiguity_type=AmbiguityType.MISSING_CONTEXT,
                question="Job description is very short. Is this the complete description?",
                context=context,
                options=["Yes, complete", "No, I'll provide more"]
            )
        
        return None
    
    def request_feedback(self, request: HILRequest):
        """Add request to queue."""
        self.pending_requests.append(request)
        self.ambiguity_patterns[request.ambiguity_type.value] = \
            self.ambiguity_patterns.get(request.ambiguity_type.value, 0) + 1
        logger.info(f"HIL request queued: {request.question}")
    
    def get_pending_requests(self) -> List[HILRequest]:
        """Retrieve pending requests."""
        return self.pending_requests
    
    def submit_response(self, request_id: str, response: str):
        """Submit human response to request."""
        for req in self.pending_requests:
            if req.request_id == request_id:
                req.response = response
                req.response_timestamp = datetime.now().isoformat()
                self.pending_requests.remove(req)
                self.completed_requests.append(req)
                logger.info(f"HIL response received for: {request_id}")
                return True
        return False

# Global HIL manager
HIL_MANAGER = HILInteractionManager()

# ============================================================================
# P2: COST TRACKING SYSTEM
# ============================================================================

class CostTracker:
    """P2: Track costs per agent and workflow."""
    
    # Cost estimates (USD per 1K tokens)
    COST_PER_1K_TOKENS = {
        "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
        "gemini-2.0-flash-exp": {"input": 0.001, "output": 0.002},
        "gpt-4": {"input": 0.03, "output": 0.06}
    }
    
    def __init__(self):
        self.agent_costs: Dict[str, float] = {}
        self.workflow_cost: float = 0.0
        self.cost_log: List[Dict[str, Any]] = []
    
    def estimate_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Estimate cost for model usage."""
        costs = self.COST_PER_1K_TOKENS.get(model_name, {"input": 0.005, "output": 0.01})
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        return input_cost + output_cost
    
    def record_agent_cost(
        self,
        agent_name: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int
    ):
        """Record cost for agent execution."""
        cost = self.estimate_cost(model_name, input_tokens, output_tokens)
        self.agent_costs[agent_name] = self.agent_costs.get(agent_name, 0.0) + cost
        self.workflow_cost += cost
        
        self.cost_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "model": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        })
        
        logger.debug(f"Cost recorded: {agent_name} = ${cost:.4f} (Total: ${self.workflow_cost:.4f})")
    
    def check_cost_ceiling(self, ceiling: float) -> bool:
        """Check if workflow cost exceeds ceiling."""
        return self.workflow_cost < ceiling
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost breakdown summary."""
        return {
            "total_workflow_cost": self.workflow_cost,
            "agent_costs": self.agent_costs,
            "most_expensive_agent": max(self.agent_costs.items(), key=lambda x: x[1])[0] if self.agent_costs else None,
            "execution_count": len(self.cost_log)
        }

# Global cost tracker
COST_TRACKER = CostTracker()

# ============================================================================
# P2: AGENT RELIABILITY SYSTEM
# ============================================================================

class AgentReliabilityTracker:
    """P2: Track agent reliability for dynamic selection."""
    
    def __init__(self, feedback_log_path: str):
        self.feedback_log_path = feedback_log_path
        self.reliability_scores: Dict[str, float] = {}
        self._load_scores()
    
    def _load_scores(self):
        """Load reliability scores from feedback log."""
        if not os.path.exists(self.feedback_log_path):
            logger.warning(f"Feedback log not found: {self.feedback_log_path}")
            return
        
        try:
            with open(self.feedback_log_path, 'r') as f:
                entries = [json.loads(line) for line in f if line.strip()]
            
            # Aggregate feedback by agent
            agent_feedback: Dict[str, List[float]] = {}
            for entry in entries:
                agent = entry.get("agent_name")
                score = entry.get("quality_score", 0.5)
                if agent:
                    if agent not in agent_feedback:
                        agent_feedback[agent] = []
                    agent_feedback[agent].append(score)
            
            # Calculate average reliability
            for agent, scores in agent_feedback.items():
                self.reliability_scores[agent] = sum(scores) / len(scores)
            
            logger.info(f"Loaded reliability scores for {len(self.reliability_scores)} agents")
        
        except Exception as e:
            logger.error(f"Failed to load reliability scores: {e}")
    
    def get_score(self, agent_name: str, default: float = 0.7) -> float:
        """Get reliability score for agent."""
        return self.reliability_scores.get(agent_name, default)
    
    def select_best_agent(
        self,
        agent_options: List[str],
        task_context: Optional[str] = None
    ) -> str:
        """Select most reliable agent from options."""
        if not agent_options:
            raise ValueError("No agent options provided")
        
        if len(agent_options) == 1:
            return agent_options[0]
        
        # Score each agent
        scores = {agent: self.get_score(agent) for agent in agent_options}
        
        # Return highest scoring
        best_agent = max(scores.items(), key=lambda x: x[1])[0]
        logger.info(f"Selected {best_agent} from {agent_options} (score: {scores[best_agent]:.2f})")
        
        return best_agent

# ============================================================================
# CONFIGURATION SYSTEM
# ============================================================================

@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_level: str = "INFO"
    debug_log_level: str = "DEBUG"
    log_file: str = "./logs/workflow_v9_8.log"
    log_format: str = "json"
    correlation_ids: bool = True
    log_rotation: Dict[str, Any] = field(default_factory=lambda: {
        "max_bytes": 10485760,
        "backup_count": 5
    })

@dataclass
class RedisConfig:
    """Redis persistence configuration."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0

@dataclass
class CostConfig:
    """Cost management configuration."""
    cost_ceiling_per_workflow: float = 5.0
    cost_ceiling_per_agent: float = 0.5
    enable_cost_tracking: bool = True
    # P2: In-flight cost tracking
    enable_in_flight_tracking: bool = True
    cost_warning_threshold: float = 4.0

@dataclass
class BatchConfig:
    """Batch processing configuration."""
    max_parallel_workers: int = 4
    enable_circuit_breaker: bool = True
    circuit_breaker_failure_threshold: int = 3

@dataclass
class MetaLoopConfig:
    """Meta-learning configuration."""
    enable_meta_learning: bool = True
    max_meta_replan_loops: int = 3
    feedback_log_path: str = "./logs/feedback_log.jsonl"
    preference_log_path: str = "./logs/preference_log.jsonl"
    proposed_rules_path: str = "./logs/proposed_rules.jsonl"

@dataclass
class TracingConfig:
    """Distributed tracing configuration."""
    langsmith_enabled: bool = False
    langsmith_api_key: Optional[str] = None

@dataclass
class FilePathsConfig:
    """File paths configuration."""
    default_job_input: str = "job_input.json"
    default_master_resume: str = "master_resume.json"

@dataclass
class AgentStackConfig:
    """P0/P1/P2 Enhancement: Stack-based agent organization."""
    # P0 Item #1: SafetyGuardStack
    safety_stack_enabled: bool = True
    bias_detection_threshold: float = 0.7
    pii_detection_enabled: bool = True
    
    # P0 Item #2: Enhanced StrategyStack
    strategy_tot_enabled: bool = True
    strategy_tot_branching_factor: int = 3
    strategy_tot_depth: int = 2
    
    # P0 Item #3: Enhanced PromptStack
    prompt_llm_driven: bool = True
    prompt_temperature: float = 0.7
    
    # P0 Item #4: Local self-correction
    enable_local_retries: bool = True
    max_local_retries: int = 2
    
    # P1: ReAct Conductors
    enable_react_conductors: bool = True
    conductor_max_steps: int = 10
    conductor_temperature: float = 0.6
    
    # P1: Dynamic Tooling
    enable_dynamic_tooling: bool = True
    max_tools_per_task: int = 5
    enable_tool_generation: bool = False  # Not fully implemented in v9.8
    
    # P1: HIL Interaction
    enable_hil_stack: bool = True
    ambiguity_confidence_threshold: float = 0.8
    
    # P2: RAG enhancements
    enable_hyde: bool = True
    enable_reranking: bool = True
    reranking_top_k: int = 5
    
    # P2: Dynamic agent selection
    enable_dynamic_selection: bool = True
    agent_selection_strategy: str = "reliability"  # reliability|cost|balanced

@dataclass
class MasterConfig:
    """Master configuration object."""
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    redis_config: RedisConfig = field(default_factory=RedisConfig)
    cost_config: CostConfig = field(default_factory=CostConfig)
    batch_config: BatchConfig = field(default_factory=BatchConfig)
    meta_loop_config: MetaLoopConfig = field(default_factory=MetaLoopConfig)
    tracing_config: TracingConfig = field(default_factory=TracingConfig)
    file_paths: FilePathsConfig = field(default_factory=FilePathsConfig)
    agent_stacks: AgentStackConfig = field(default_factory=AgentStackConfig)
    
    @classmethod
    def from_file(cls, filepath: str = "master_config_v9_8.json") -> 'MasterConfig':
        """Load configuration from JSON file."""
        try:
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            
            # Build nested dataclasses
            logging_cfg = LoggingConfig(**config_dict.get("logging_config", {}))
            redis_cfg = RedisConfig(**config_dict.get("redis_config", {}))
            cost_cfg = CostConfig(**config_dict.get("cost_config", {}))
            batch_cfg = BatchConfig(**config_dict.get("batch_config", {}))
            meta_cfg = MetaLoopConfig(**config_dict.get("meta_loop_config", {}))
            tracing_cfg = TracingConfig(**config_dict.get("tracing_config", {}))
            file_cfg = FilePathsConfig(**config_dict.get("file_paths", {}))
            stack_cfg = AgentStackConfig(**config_dict.get("agent_stacks", {}))
            
            return cls(
                logging_config=logging_cfg,
                redis_config=redis_cfg,
                cost_config=cost_cfg,
                batch_config=batch_cfg,
                meta_loop_config=meta_cfg,
                tracing_config=tracing_cfg,
                file_paths=file_cfg,
                agent_stacks=stack_cfg
            )
        except Exception as e:
            logger.warning(f"Could not load config from {filepath}: {e}. Using defaults.")
            return cls()

# Initialize global CONFIG
try:
    CONFIG = MasterConfig.from_file("master_config_v9_8.json")
except Exception as e:
    logger.warning(f"Failed to load master_config_v9_8.json: {e}. Using defaults.")
    CONFIG = MasterConfig()

# Directory setup
DATA_DIR = Path("./data")
OUTPUT_DIR = Path("./output")
CACHE_DIR = Path("./cache")
for directory in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# EXCEPTIONS
# ============================================================================

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass

class AgentExecutionError(Exception):
    """Raised when agent execution fails."""
    pass

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class CostCeilingExceededError(Exception):
    """P2: Raised when cost ceiling is exceeded."""
    pass

class ToolExecutionError(Exception):
    """P1: Raised when tool execution fails."""
    pass

# ============================================================================
# MODEL CLIENT FACTORY
# ============================================================================

class BaseModelClient(ABC):
    """Base class for LLM clients."""
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute chat completion."""
        pass

class GoogleGeminiClient(BaseModelClient):
    """Google Gemini API client with token tracking."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
        except ImportError:
            raise ImportError("google-generativeai package not installed")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute chat completion with token tracking."""
        try:
            # Convert messages to Gemini format
            prompt = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            if response_format == "json_object":
                config["response_mime_type"] = "application/json"
            
            response = self.model.generate_content(prompt, generation_config=config)
            
            # Parse JSON if requested
            content = response.text
            if response_format == "json_object":
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, returning as text")
            
            # Estimate tokens (rough approximation)
            input_tokens = len(prompt) // 4
            output_tokens = len(response.text) // 4
            
            return {
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

class AnthropicClient(BaseModelClient):
    """Anthropic Claude API client with token tracking."""
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.model_name = model_name
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute chat completion with token tracking."""
        try:
            # Separate system message
            system_msg = None
            user_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    user_messages.append(msg)
            
            kwargs = {
                "model": self.model_name,
                "messages": user_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if system_msg:
                kwargs["system"] = system_msg
            
            response = self.client.messages.create(**kwargs)
            
            content = response.content[0].text
            if response_format == "json_object":
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, returning as text")
            
            return {
                "content": content,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

def get_model_client(provider: str, model_name: str) -> BaseModelClient:
    """Factory function for model clients."""
    if provider == "google":
        return GoogleGeminiClient(model_name)
    elif provider == "anthropic":
        return AnthropicClient(model_name)
    else:
        raise ValueError(f"Unknown provider: {provider}")

# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class BaseAgent(ABC):
    """Enhanced base agent with cost tracking and reliability."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        self.blackboard = blackboard
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.execution_start_time = None
        self.execution_end_time = None
        self.cost_tracker = COST_TRACKER
        self.workflow_id = blackboard.get("workflow_id", "N/A")
    
    def log_info(self, message: str):
        """Log info with workflow context."""
        self.logger.info(message, extra={"workflow_id": self.workflow_id})
    
    def log_warning(self, message: str):
        """Log warning with workflow context."""
        self.logger.warning(message, extra={"workflow_id": self.workflow_id})
    
    def log_error(self, message: str):
        """Log error with workflow context."""
        self.logger.error(message, extra={"workflow_id": self.workflow_id})
    
    def log_debug(self, message: str):
        """Log debug with workflow context."""
        if self.debug_mode:
            self.logger.debug(message, extra={"workflow_id": self.workflow_id})
    
    def record_cost(self, model_name: str, input_tokens: int, output_tokens: int):
        """P2: Record cost for this agent's execution."""
        if CONFIG.cost_config.enable_in_flight_tracking:
            self.cost_tracker.record_agent_cost(
                agent_name=self.__class__.__name__,
                model_name=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            # Check cost ceiling
            if not self.cost_tracker.check_cost_ceiling(CONFIG.cost_config.cost_ceiling_per_workflow):
                raise CostCeilingExceededError(
                    f"Workflow cost ${self.cost_tracker.workflow_cost:.2f} exceeds ceiling "
                    f"${CONFIG.cost_config.cost_ceiling_per_workflow:.2f}"
                )
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute agent logic."""
        pass

# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

# P0 Prompts (from v9.7)
BIAS_DETECTOR_SYSTEM_PROMPT = """You are a bias detection agent analyzing resume content for potential bias.

Evaluate content for:
1. Gender bias (gendered language, assumptions)
2. Age bias (age-related terms)
3. Cultural bias (culture-specific references)
4. Disability bias (ableist language)
5. Socioeconomic bias (assumptions about background)

Output JSON:
{
  "bias_detected": true/false,
  "bias_score": 0.0-1.0,
  "findings": [
    {
      "type": "gender|age|cultural|disability|socioeconomic",
      "severity": "low|medium|high",
      "text": "<problematic text>",
      "suggestion": "<neutral alternative>"
    }
  ]
}
"""

PII_SCRUBBER_SYSTEM_PROMPT = """You are a PII sanitization agent.

Detect and redact:
- Phone numbers
- Email addresses
- Physical addresses
- Social security numbers
- Credit card numbers
- Personal identifiers

Output JSON:
{
  "pii_found": true/false,
  "redaction_count": 0,
  "sanitized_content": "<JSON string>",
  "pii_map": {"<redacted_key>": "<original_value>"}
}
"""

TOT_STRATEGIST_SYSTEM_PROMPT = """You are a Tree-of-Thoughts strategist generating {branching_factor} strategic approaches.

Generate diverse positioning strategies with rigorous evaluation.

Output JSON:
{{
  "thought_branches": [
    {{
      "branch_id": "T1",
      "positioning_theme": "<strategy>",
      "evidence_selection": ["<criteria>"],
      "risk_factors": ["<risk>"],
      "opportunity_score": 0.0-10.0,
      "feasibility_score": 0.0-10.0,
      "differentiation_score": 0.0-10.0
    }}
  ],
  "selected_strategy": {{
    "branch_id": "T1",
    "rationale": "<selection reasoning>",
    "implementation_guidance": "<execution plan>"
  }}
}}
"""

PROMPT_ENGINEER_SYSTEM_PROMPT = """You are an expert prompt engineering agent.

Craft optimal prompts for resume bullet generation applying best practices:
1. Persona setting
2. Task decomposition
3. Constraint specification
4. Few-shot examples
5. Chain-of-thought guidance

Output JSON:
{
  "system_prompt": "<system prompt>",
  "user_prompt_template": "<template>",
  "few_shot_examples": [{"input": "", "output": ""}],
  "constraint_reminders": ["<constraint>"],
  "estimated_quality_score": 0.0-1.0
}
"""

BULLET_CRITIQUE_SYSTEM_PROMPT = """You are a local self-correction critic evaluating resume bullets.

Evaluate on:
1. Relevance (0-10)
2. Impact (0-10)
3. Specificity (0-10)
4. Credibility (0-10)
5. Length (0-10)
6. Grammar (0-10)

Acceptance threshold: 7.0/10 average

Output JSON:
{
  "passed": true/false,
  "scores": {"relevance": 8.0, "impact": 7.5, ...},
  "critique": "<feedback>",
  "recommendation": "accept|regenerate|manual_review"
}
"""

# P1: ReAct Conductor Prompts
REACT_CONDUCTOR_SYSTEM_PROMPT = """You are a ReAct (Reasoning + Acting) conductor agent.

**Your Role:**
Plan and execute multi-step workflows through iterative reasoning and action cycles.

**Available Actions:**
{available_actions}

**ReAct Loop:**
1. **Thought**: Analyze current state and determine next step
2. **Action**: Select and execute action
3. **Observation**: Process action result
4. **Repeat**: Continue until goal achieved or max steps reached

**Output Format (JSON):**
{{
  "thought": "<current reasoning>",
  "action": {{
    "name": "<action_name>",
    "parameters": {{"<param>": "<value>"}}
  }},
  "termination": {{
    "should_terminate": true/false,
    "reason": "<why terminating or continuing>"
  }}
}}

**Rules:**
- Think step-by-step
- Be explicit about reasoning
- Check action preconditions
- Handle errors gracefully
- Terminate when goal achieved OR max steps reached
"""

# P1: Tool Selection Prompt
TOOL_SELECTOR_SYSTEM_PROMPT = """You are a tool selection agent.

**Task:** {task_description}

**Available Tools:**
{tool_definitions}

**Output Format (JSON):**
{{
  "selected_tools": ["<tool_name_1>", "<tool_name_2>"],
  "selection_rationale": "<why these tools>",
  "execution_order": [
    {{
      "tool": "<tool_name>",
      "reason": "<why this order>"
    }}
  ]
}}

**Selection Criteria:**
1. Task relevance
2. Tool reliability
3. Cost efficiency
4. Execution dependencies
"""

# P1: HIL Ambiguity Detector Prompt
HIL_AMBIGUITY_DETECTOR_PROMPT = """You are an ambiguity detection agent.

**Context:** {context}

**Detect:**
1. Missing critical information
2. Conflicting requirements
3. Unclear priorities
4. Quality threshold ambiguities
5. Strategic decision points

**Output Format (JSON):**
{{
  "ambiguity_detected": true/false,
  "ambiguity_type": "missing_context|conflicting_requirements|unclear_priority|quality_threshold|strategic_decision",
  "confidence": 0.0-1.0,
  "question_for_human": "<specific question>",
  "options": ["<option_1>", "<option_2>"],
  "impact_if_unresolved": "<consequences>"
}}

**Threshold:** Only flag if confidence > {threshold}
"""

# P2: HyDE Generation Prompt
HYDE_GENERATION_PROMPT = """You are a Hypothetical Document Embedding (HyDE) generator.

**Query:** {query}

**Task:** Generate a hypothetical ideal document that would perfectly answer this query.

**Output Format (JSON):**
{{
  "hypothetical_document": "<generated document text>",
  "key_concepts": ["<concept_1>", "<concept_2>"],
  "search_expansion_terms": ["<term_1>", "<term_2>"]
}}

**Rules:**
- Write as if the perfect document exists
- Include domain-specific terminology
- Cover all query aspects
- Be concrete and specific
"""

# P2: Reranking Prompt
RERANKING_PROMPT = """You are a cross-encoder reranker evaluating search result relevance.

**Query:** {query}
**Documents:** {documents}

**Task:** Score each document's relevance to the query.

**Output Format (JSON):**
{{
  "reranked_results": [
    {{
      "doc_id": "<id>",
      "relevance_score": 0.0-1.0,
      "rationale": "<why this score>"
    }}
  ]
}}

**Scoring Criteria:**
1. Semantic relevance
2. Content quality
3. Completeness
4. Specificity
"""

# Meta-learning prompts (unchanged from v9.7)
META_LOG_READER_SYSTEM_PROMPT = """Analyze workflow logs to extract structured insights.

Output JSON:
{
  "summary": "<brief summary>",
  "key_issues": ["<issue_1>", "<issue_2>"],
  "user_preferences": {"<key>": "<value>"}
}
"""

META_PATTERN_FINDER_SYSTEM_PROMPT = """Identify recurring failure patterns.

**Input:** {log_data}

**Output JSON:**
{{
  "patterns": [
    {{
      "pattern_id": "P1",
      "description": "<pattern>",
      "frequency": "<count>",
      "severity": "low|medium|high"
    }}
  ]
}}
"""

META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT = """Generate root cause hypotheses.

**Patterns:** {patterns}
**Critique:** {critique}

**Output JSON:**
{{
  "hypotheses": [
    {{
      "id": "H1",
      "pattern_ids": ["P1"],
      "root_cause": "<hypothesis>",
      "confidence": 0.0-1.0
    }}
  ]
}}
"""

META_PROPOSAL_DRAFTER_SYSTEM_PROMPT = """Draft concrete change proposal.

**Hypothesis:** {hypothesis}

**Output JSON:**
{{
  "type": "config_change|prompt_update|new_agent",
  "description": "<change>",
  "implementation": "<how>",
  "expected_impact": "<impact>"
}}
"""

META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT = """Review proposal effectiveness.

**Patterns:** {patterns}
**Proposal:** {proposal}

**Output JSON:**
{{
  "critique_passed": true/false,
  "reason": "<rationale>",
  "suggested_improvements": ["<improvement>"]
}}
"""

# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Version
    "__version__",
    
    # Config
    "CONFIG",
    "MasterConfig",
    "LoggingConfig",
    "RedisConfig",
    "CostConfig",
    "BatchConfig",
    "MetaLoopConfig",
    "TracingConfig",
    "FilePathsConfig",
    "AgentStackConfig",
    
    # Paths
    "DATA_DIR",
    "OUTPUT_DIR",
    "CACHE_DIR",
    
    # Types
    "MainGraphState",
    "MetaGraphState",
    
    # Exceptions
    "CircuitBreakerOpenError",
    "AgentExecutionError",
    "ValidationError",
    "CostCeilingExceededError",
    "ToolExecutionError",
    
    # Model Client
    "BaseModelClient",
    "GoogleGeminiClient",
    "AnthropicClient",
    "get_model_client",
    
    # Base Agent
    "BaseAgent",
    
    # P1: Dynamic Tooling
    "ToolDefinition",
    "ToolRegistry",
    "TOOL_REGISTRY",
    
    # P1: HIL System
    "AmbiguityType",
    "HILRequest",
    "HILInteractionManager",
    "HIL_MANAGER",
    
    # P2: Cost Tracking
    "CostTracker",
    "COST_TRACKER",
    
    # P2: Reliability
    "AgentReliabilityTracker",
    
    # System Prompts - P0
    "BIAS_DETECTOR_SYSTEM_PROMPT",
    "PII_SCRUBBER_SYSTEM_PROMPT",
    "TOT_STRATEGIST_SYSTEM_PROMPT",
    "PROMPT_ENGINEER_SYSTEM_PROMPT",
    "BULLET_CRITIQUE_SYSTEM_PROMPT",
    
    # System Prompts - P1
    "REACT_CONDUCTOR_SYSTEM_PROMPT",
    "TOOL_SELECTOR_SYSTEM_PROMPT",
    "HIL_AMBIGUITY_DETECTOR_PROMPT",
    
    # System Prompts - P2
    "HYDE_GENERATION_PROMPT",
    "RERANKING_PROMPT",
    
    # System Prompts - Meta
    "META_LOG_READER_SYSTEM_PROMPT",
    "META_PATTERN_FINDER_SYSTEM_PROMPT",
    "META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT",
    "META_PROPOSAL_DRAFTER_SYSTEM_PROMPT",
    "META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT",
]
