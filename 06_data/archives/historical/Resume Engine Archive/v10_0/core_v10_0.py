# File: core_v10_0.py
# Version: 10.0 (Modularity, Caching, Async Performance)
#
# v10.0 MAJOR CHANGES:
# ROW 4: Modularity - Decomposed monolithic state, dependency injection
# ROW 5: Caching - Added Redis-based LLM response caching
# ROW 6: Performance - Async LLM clients, parallel operations

import os
import json
import logging
import hashlib
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import redis

# Custom exceptions (preserved from v9.9)
class ModelAPIError(Exception):
    """Raised when LLM API call fails"""
    pass

class JSONParsingError(Exception):
    """Raised when JSON parsing fails"""
    pass

class FileIOError(Exception):
    """Raised when file I/O operations fail"""
    pass

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

class CostCeilingExceededError(Exception):
    """Raised when cost ceiling is exceeded"""
    pass

# ============================================================================
# ROW 4: MODULAR STATE ARCHITECTURE
# ============================================================================

@dataclass
class ResumeContext:
    """Isolated resume state"""
    master_resume: Dict[str, Any] = field(default_factory=dict)
    sanitized_resume: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JobContext:
    """Isolated job input state"""
    raw_jd: str = ""
    company: str = ""
    job_title: str = ""

@dataclass
class WorkflowMetadata:
    """Workflow tracking metadata"""
    workflow_id: str = ""
    replan_count: int = 0
    local_retry_count: int = 0

@dataclass
class ArtifactsState:
    """Generated artifacts"""
    artifacts: Dict[str, Any] = field(default_factory=dict)
    original_draft: str = ""
    human_approved_draft: str = ""

@dataclass
class StrategyState:
    """Strategy planning state"""
    strategy_thoughts: List[Dict] = field(default_factory=list)
    selected_strategy: Optional[Dict] = None

@dataclass
class ConductorState:
    """Conductor reasoning state"""
    conductor_thoughts: List[Dict] = field(default_factory=list)
    conductor_plan: Optional[Dict] = None

@dataclass
class ToolingState:
    """Dynamic tooling state"""
    available_tools: List[Dict] = field(default_factory=list)
    tool_execution_history: List[Dict] = field(default_factory=list)

@dataclass
class HILState:
    """Human-in-the-loop state"""
    ambiguity_detected: bool = False
    hil_feedback_queue: List[Dict] = field(default_factory=list)
    hil_responses: List[Dict] = field(default_factory=list)

@dataclass
class CostState:
    """Cost tracking state"""
    agent_costs: Dict[str, float] = field(default_factory=dict)
    total_workflow_cost: float = 0.0

@dataclass
class QualityState:
    """Quality assurance state"""
    bullet_critique_history: List[Dict] = field(default_factory=list)
    agent_reliability_scores: Dict[str, float] = field(default_factory=dict)

@dataclass
class ProvenanceState:
    """Provenance tracking"""
    provenance_ledger: List[Dict] = field(default_factory=list)
    preference_insight: Optional[Dict] = None

@dataclass
class MainGraphState:
    """Composed state from modular components"""
    resume: ResumeContext = field(default_factory=ResumeContext)
    job: JobContext = field(default_factory=JobContext)
    metadata: WorkflowMetadata = field(default_factory=WorkflowMetadata)
    artifacts: ArtifactsState = field(default_factory=ArtifactsState)
    strategy: StrategyState = field(default_factory=StrategyState)
    conductor: ConductorState = field(default_factory=ConductorState)
    tooling: ToolingState = field(default_factory=ToolingState)
    hil: HILState = field(default_factory=HILState)
    cost: CostState = field(default_factory=CostState)
    quality: QualityState = field(default_factory=QualityState)
    provenance: ProvenanceState = field(default_factory=ProvenanceState)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to flat dict for LangGraph compatibility"""
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    result[f"{key}_{subkey}"] = subvalue
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MainGraphState':
        """Reconstruct from flat dict"""
        state = cls()
        
        # Map flat keys back to nested structure
        for key, value in data.items():
            if '_' in key:
                parent, child = key.split('_', 1)
                if hasattr(state, parent):
                    parent_obj = getattr(state, parent)
                    if hasattr(parent_obj, child):
                        setattr(parent_obj, child, value)
            else:
                if hasattr(state, key):
                    setattr(state, key, value)
        
        return state

class MetaGraphState(TypedDict):
    """Meta-learning state (preserved)"""
    raw_logs: Dict[str, str]
    log_summary: Dict
    patterns: List[Dict]
    hypotheses: List[Dict]
    proposal: Dict
    critique: Dict
    replan_count: int
    workflow_id: str

# ============================================================================
# ROW 5: CACHING LAYER
# ============================================================================

class CacheManager:
    """Redis-based LLM response caching"""
    
    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl
        self.logger = logging.getLogger(f"{__name__}.CacheManager")
        self.hits = 0
        self.misses = 0

    def _generate_cache_key(self, provider: str, model: str, messages: List[Dict], 
                           temperature: float, **kwargs) -> str:
        """Generate deterministic cache key"""
        key_parts = [
            provider,
            model,
            json.dumps(messages, sort_keys=True),
            f"temp_{temperature}",
            json.dumps({k: v for k, v in sorted(kwargs.items())}, sort_keys=True)
        ]
        key_string = "|".join(key_parts)
        return f"llm_cache:{hashlib.sha256(key_string.encode()).hexdigest()}"

    async def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Async cache retrieval"""
        try:
            cached = await asyncio.to_thread(self.redis.get, cache_key)
            if cached:
                self.hits += 1
                self.logger.debug(f"Cache HIT: {cache_key[:16]}...")
                return json.loads(cached)
            else:
                self.misses += 1
                self.logger.debug(f"Cache MISS: {cache_key[:16]}...")
                return None
        except Exception as e:
            self.logger.warning(f"Cache read error: {e}")
            return None

    async def cache_response(self, cache_key: str, response: Dict):
        """Async cache storage"""
        try:
            await asyncio.to_thread(
                self.redis.setex,
                cache_key,
                self.ttl,
                json.dumps(response)
            )
            self.logger.debug(f"Cached response: {cache_key[:16]}...")
        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Cache performance stats"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2)
        }

# ============================================================================
# ROW 4: DEPENDENCY INJECTION CONTAINER
# ============================================================================

class WorkflowContext:
    """Dependency injection container (replaces global singletons)"""
    
    def __init__(self, config: 'Config', redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        
        # Inject dependencies instead of globals
        self.cost_tracker = CostTracker(config.cost_config)
        self.cache_manager = CacheManager(redis_client, ttl=3600)
        self.hil_manager = HILManager()
        self.tool_registry = ToolRegistry()
        self.reliability_tracker = AgentReliabilityTracker(
            config.meta_loop_config.feedback_log_path
        )
        
        self.logger = logging.getLogger(f"{__name__}.WorkflowContext")

    def get_model_client(self, provider: str, model_name: str) -> 'AsyncBaseModelClient':
        """Factory for async model clients with caching"""
        if provider == "anthropic":
            return AsyncAnthropicClient(model_name, self.cache_manager)
        elif provider == "google":
            return AsyncGoogleGeminiClient(model_name, self.cache_manager)
        else:
            raise ValueError(f"Unknown provider: {provider}")

# ============================================================================
# CONFIGURATION (Enhanced)
# ============================================================================

@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0

@dataclass
class CostConfig:
    cost_ceiling_per_workflow: float = 5.0
    cost_ceiling_per_agent: float = 0.5
    enable_cost_tracking: bool = True
    enable_in_flight_tracking: bool = True
    cost_warning_threshold: float = 4.0

@dataclass
class BatchConfig:
    max_parallel_workers: int = 4
    enable_circuit_breaker: bool = True
    circuit_breaker_failure_threshold: int = 3

@dataclass
class MetaLoopConfig:
    enable_meta_learning: bool = True
    max_meta_replan_loops: int = 3
    feedback_log_path: str = "./logs/feedback_log.jsonl"
    preference_log_path: str = "./logs/preference_log.jsonl"
    proposed_rules_path: str = "./logs/proposed_rules.jsonl"

@dataclass
class LoggingConfig:
    log_level: str = "INFO"
    debug_log_level: str = "DEBUG"
    log_file: str = "./logs/workflow_v10_0.log"
    log_format: str = "json"
    correlation_ids: bool = True

@dataclass
class TracingConfig:
    langsmith_enabled: bool = False
    langsmith_api_key: Optional[str] = None

@dataclass
class FilePaths:
    default_job_input: str = "job_input.json"
    default_master_resume: str = "master_resume.json"

@dataclass
class AgentStacksConfig:
    safety_stack_enabled: bool = True
    pii_detection_enabled: bool = True
    use_presidio_for_pii: bool = True
    use_local_bias_detection: bool = True
    bias_detection_threshold: float = 0.7
    strategy_tot_enabled: bool = True
    strategy_tot_branching_factor: int = 3
    strategy_tot_depth: int = 2
    prompt_llm_driven: bool = True
    prompt_temperature: float = 0.7
    enable_local_retries: bool = True
    max_local_retries: int = 2
    enable_react_conductors: bool = True
    conductor_max_steps: int = 10
    conductor_temperature: float = 0.6
    enable_dynamic_tooling: bool = True
    max_tools_per_task: int = 5
    enable_tool_generation: bool = False
    enable_hil_stack: bool = True
    ambiguity_confidence_threshold: float = 0.8
    enable_hyde: bool = True
    enable_reranking: bool = True
    reranking_top_k: int = 5
    enable_dynamic_selection: bool = True
    agent_selection_strategy: str = "reliability"

@dataclass
class CachingConfig:
    """v10.0: Caching configuration"""
    enable_llm_caching: bool = True
    cache_ttl_seconds: int = 3600
    cache_db: int = 1

@dataclass
class PerformanceConfig:
    """v10.0: Performance configuration"""
    enable_async_llm: bool = True
    max_concurrent_llm_calls: int = 10
    llm_timeout_seconds: int = 30

@dataclass
class Config:
    schema_version: str = "master_config_v10.0"
    redis_config: RedisConfig = field(default_factory=RedisConfig)
    cost_config: CostConfig = field(default_factory=CostConfig)
    batch_config: BatchConfig = field(default_factory=BatchConfig)
    meta_loop_config: MetaLoopConfig = field(default_factory=MetaLoopConfig)
    logging_config: LoggingConfig = field(default_factory=LoggingConfig)
    tracing_config: TracingConfig = field(default_factory=TracingConfig)
    file_paths: FilePaths = field(default_factory=FilePaths)
    agent_stacks: AgentStacksConfig = field(default_factory=AgentStacksConfig)
    caching_config: CachingConfig = field(default_factory=CachingConfig)
    performance_config: PerformanceConfig = field(default_factory=PerformanceConfig)
    model_config: Dict[str, Dict] = field(default_factory=dict)

    @classmethod
    def from_json(cls, path: str) -> 'Config':
        """Load from JSON config file"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            config = cls()
            if "redis_config" in data:
                config.redis_config = RedisConfig(**data["redis_config"])
            if "cost_config" in data:
                config.cost_config = CostConfig(**data["cost_config"])
            if "batch_config" in data:
                config.batch_config = BatchConfig(**data["batch_config"])
            if "meta_loop_config" in data:
                config.meta_loop_config = MetaLoopConfig(**data["meta_loop_config"])
            if "logging_config" in data:
                config.logging_config = LoggingConfig(**data["logging_config"])
            if "tracing_config" in data:
                config.tracing_config = TracingConfig(**data["tracing_config"])
            if "file_paths" in data:
                config.file_paths = FilePaths(**data["file_paths"])
            if "agent_stacks" in data:
                config.agent_stacks = AgentStacksConfig(**data["agent_stacks"])
            if "caching_config" in data:
                config.caching_config = CachingConfig(**data["caching_config"])
            if "performance_config" in data:
                config.performance_config = PerformanceConfig(**data["performance_config"])
            if "model_config" in data:
                config.model_config = data["model_config"]
            
            return config
        except FileIOError as e:
            raise FileIOError(f"Failed to load config from {path}: {e}")

# Global config instance
CONFIG = Config.from_json(os.getenv("CONFIG_PATH", "master_config_v10_0.json"))

# ============================================================================
# ROW 6: ASYNC MODEL CLIENTS
# ============================================================================

class AsyncBaseModelClient(ABC):
    """Abstract async model client with caching"""
    
    def __init__(self, model_name: str, cache_manager: CacheManager):
        self.model_name = model_name
        self.cache = cache_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def _call_api(self, messages: List[Dict], **kwargs) -> Dict:
        """Actual API call (to be implemented by subclasses)"""
        pass

    async def chat_completion_async(self, messages: List[Dict], 
                                   use_cache: bool = True,
                                   **kwargs) -> Dict:
        """Async chat completion with caching"""
        provider = self.__class__.__name__.replace("Async", "").replace("Client", "").lower()
        temperature = kwargs.get("temperature", 0.7)
        
        # Generate cache key
        cache_key = self.cache._generate_cache_key(
            provider, self.model_name, messages, temperature, **kwargs
        )
        
        # Try cache first
        if use_cache and CONFIG.caching_config.enable_llm_caching:
            cached = await self.cache.get_cached_response(cache_key)
            if cached:
                return cached
        
        # Call API
        try:
            response = await self.call_api(messages, **kwargs)
            
            # Cache response
            if use_cache and CONFIG.caching_config.enable_llm_caching:
                await self.cache.cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"API call failed: {e}")
            raise ModelAPIError(f"API call failed: {e}")

class AsyncAnthropicClient(AsyncBaseModelClient):
    """Async Anthropic Claude client"""
    
    def __init__(self, model_name: str, cache_manager: CacheManager):
        super().__init__(model_name, cache_manager)
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            raise ImportError("anthropic package not installed")

    async def _call_api(self, messages: List[Dict], **kwargs) -> Dict:
        """Call Anthropic API"""
        try:
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 4096)
            
            response = await self.client.messages.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content_text = response.content[0].text if response.content else ""
            
            return {
                "content": content_text,
                "raw_response": response.model_dump(),
                "model": self.model_name,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            }
        except Exception as e:
            raise ModelAPIError(f"Anthropic API error: {e}")

class AsyncGoogleGeminiClient(AsyncBaseModelClient):
    """Async Google Gemini client"""
    
    def __init__(self, model_name: str, cache_manager: CacheManager):
        super().__init__(model_name, cache_manager)
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel(model_name)
        except ImportError:
            raise ImportError("google-generativeai package not installed")

    async def _call_api(self, messages: List[Dict], **kwargs) -> Dict:
        """Call Gemini API"""
        try:
            temperature = kwargs.get("temperature", 0.7)
            response_format = kwargs.get("response_format", None)
            
            generation_config = {"temperature": temperature}
            if response_format == "json_object":
                generation_config["response_mime_type"] = "application/json"
            
            # Convert messages to Gemini format
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            
            prompt = "\n".join(prompt_parts)
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config
            )
            
            content_text = response.text
            
            # Parse JSON if requested
            if response_format == "json_object":
                try:
                    content_json = json.loads(content_text)
                    return {
                        "content": content_json,
                        "raw_response": content_text,
                        "model": self.model_name
                    }
                except json.JSONDecodeError as e:
                    raise JSONParsingError(f"Failed to parse JSON: {e}")
            
            return {
                "content": content_text,
                "raw_response": content_text,
                "model": self.model_name
            }
            
        except Exception as e:
            raise ModelAPIError(f"Gemini API error: {e}")

# ============================================================================
# COST TRACKING (Refactored with dependency injection)
# ============================================================================

class CostTracker:
    """Cost tracking with dependency injection"""
    
    def __init__(self, config: CostConfig):
        self.config = config
        self.workflow_costs: Dict[str, float] = {}
        self.agent_costs: Dict[str, Dict[str, float]] = {}
        self.logger = logging.getLogger(f"{__name__}.CostTracker")

    def record_cost(self, workflow_id: str, agent_name: str, cost: float):
        """Record cost for agent in workflow"""
        if not self.config.enable_cost_tracking:
            return
        
        if workflow_id not in self.workflow_costs:
            self.workflow_costs[workflow_id] = 0.0
            self.agent_costs[workflow_id] = {}
        
        self.workflow_costs[workflow_id] += cost
        
        if agent_name not in self.agent_costs[workflow_id]:
            self.agent_costs[workflow_id][agent_name] = 0.0
        self.agent_costs[workflow_id][agent_name] += cost
        
        # Check ceilings
        if self.agent_costs[workflow_id][agent_name] > self.config.cost_ceiling_per_agent:
            raise CostCeilingExceededError(
                f"Agent {agent_name} exceeded cost ceiling: "
                f"${self.agent_costs[workflow_id][agent_name]:.4f}"
            )
        
        if self.workflow_costs[workflow_id] > self.config.cost_ceiling_per_workflow:
            raise CostCeilingExceededError(
                f"Workflow exceeded cost ceiling: ${self.workflow_costs[workflow_id]:.4f}"
            )

    def get_cost_summary(self, workflow_id: Optional[str] = None) -> Dict:
        """Get cost summary"""
        if workflow_id:
            return {
                "workflow_id": workflow_id,
                "total_workflow_cost": self.workflow_costs.get(workflow_id, 0.0),
                "agent_costs": self.agent_costs.get(workflow_id, {})
            }
        
        return {
            "total_workflows": len(self.workflow_costs),
            "total_cost": sum(self.workflow_costs.values()),
            "workflows": self.workflow_costs
        }

# ============================================================================
# HIL MANAGER (Refactored)
# ============================================================================

class HILManager:
    """Human-in-the-loop manager"""
    
    def __init__(self):
        self.feedback_queue: List[Dict] = []
        self.responses: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.HILManager")

    def queue_feedback_request(self, request: Dict):
        """Queue feedback request"""
        self.feedback_queue.append(request)
        self.logger.info(f"Queued HIL request: {request.get('type')}")

    def get_pending_requests(self) -> List[Dict]:
        """Get all pending requests"""
        return self.feedback_queue.copy()

    def submit_response(self, request_id: str, response: Any):
        """Submit human response"""
        self.responses[request_id] = response
        self.logger.info(f"Received HIL response for: {request_id}")

# ============================================================================
# TOOL REGISTRY (Refactored)
# ============================================================================

class ToolRegistry:
    """Dynamic tool registry"""
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
        self.logger = logging.getLogger(f"{__name__}.ToolRegistry")

    def register_tool(self, tool_name: str, tool_def: Dict):
        """Register a tool"""
        self.tools[tool_name] = tool_def
        self.logger.info(f"Registered tool: {tool_name}")

    def get_tool(self, tool_name: str) -> Optional[Dict]:
        """Get tool definition"""
        return self.tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """List all tool names"""
        return list(self.tools.keys())

# ============================================================================
# RELIABILITY TRACKER (Refactored)
# ============================================================================

class AgentReliabilityTracker:
    """Track agent reliability from feedback log"""
    
    def __init__(self, feedback_log_path: str):
        self.feedback_log_path = feedback_log_path
        self.logger = logging.getLogger(f"{__name__}.AgentReliabilityTracker")

    def get_reliability_scores(self) -> Dict[str, float]:
        """Calculate reliability scores from feedback log"""
        scores = {}
        
        if not os.path.exists(self.feedback_log_path):
            return scores
        
        try:
            with open(self.feedback_log_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        agent = entry.get("agent_name")
                        success = entry.get("success", False)
                        
                        if agent:
                            if agent not in scores:
                                scores[agent] = {"successes": 0, "total": 0}
                            
                            scores[agent]["total"] += 1
                            if success:
                                scores[agent]["successes"] += 1
                    except json.JSONDecodeError:
                        continue
            
            # Convert to success rate
            return {
                agent: data["successes"] / data["total"] if data["total"] > 0 else 0.5
                for agent, data in scores.items()
            }
            
        except FileIOError as e:
            self.logger.warning(f"Could not read feedback log: {e}")
            return scores

# ============================================================================
# BASE AGENT (Refactored with context injection)
# ============================================================================

class BaseAgent:
    """Base agent with injected context"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        self.context = context
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def log_info(self, message: str):
        self.logger.info(f"[{self.__class__.__name__}] {message}")

    def log_warning(self, message: str):
        self.logger.warning(f"[{self.__class__.__name__}] {message}")

    def log_error(self, message: str):
        self.logger.error(f"[{self.__class__.__name__}] {message}")

    def log_debug(self, message: str):
        if self.debug_mode:
            self.logger.debug(f"[{self.__class__.__name__}] {message}")

    def record_cost(self, workflow_id: str, cost: float):
        """Record cost via injected tracker"""
        self.context.cost_tracker.record_cost(
            workflow_id,
            self.__class__.__name__,
            cost
        )

# ============================================================================
# SYSTEM PROMPTS (Preserved from v9.9)
# ============================================================================

META_LOG_READER_SYSTEM_PROMPT = """You are a log analysis agent. Read feedback_log.jsonl and preference_log.jsonl to extract key data."""

META_PATTERN_FINDER_SYSTEM_PROMPT = """Given raw logs: {log_data}

Identify recurring patterns of failure or preference violations. Return JSON:
{{
  "patterns": [
    {{"id": "P1", "description": "...", "frequency": 5, "severity": "high"}}
  ]
}}"""

META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT = """Given patterns: {patterns}
Previous critique: {critique}

Generate root cause hypotheses. Return JSON:
{{
  "hypotheses": [
    {{"id": "H1", "root_cause": "...", "confidence": 0.8}}
  ]
}}"""

META_PROPOSAL_DRAFTER_SYSTEM_PROMPT = """Given hypothesis: {hypothesis}

Draft a change proposal. Return JSON:
{{
  "type": "config_change|prompt_update|agent_replacement",
  "changes": {{...}},
  "expected_impact": "..."
}}"""

META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT = """Given patterns: {patterns}
Proposal: {proposal}

Critique the proposal. Return JSON:
{{
  "critique_passed": true/false,
  "reason": "...",
  "suggestions": [...]
}}"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_client(provider: str, model_name: str, 
                    cache_manager: Optional[CacheManager] = None) -> AsyncBaseModelClient:
    """Legacy helper for backward compatibility"""
    if cache_manager is None:
        redis_client = redis.Redis(
            host=CONFIG.redis_config.host,
            port=CONFIG.redis_config.port,
            db=CONFIG.caching_config.cache_db
        )
        cache_manager = CacheManager(redis_client)
    
    if provider == "anthropic":
        return AsyncAnthropicClient(model_name, cache_manager)
    elif provider == "google":
        return AsyncGoogleGeminiClient(model_name, cache_manager)
    else:
        raise ValueError(f"Unknown provider: {provider}")

# ============================================================================
# END OF core_v10_0.py
# ============================================================================