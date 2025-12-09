# File: core_v10_2.py
# Version: 10.2 (Design-Aligned Implementation)
#
# v10.2 MAJOR CHANGES:
# - Added chromadb import
# - Updated ConfigV10_1 to ConfigV10_2 and schema check
# - Injected 'chromadb_client' into WorkflowContext
#
# GAP 4 FIX (DI):
# - Removed global 'CONFIG' singleton instance.
# - Refactored WorkflowContext to remove Service Locator anti-pattern.
#   It no longer creates its own dependencies (CacheManager, etc.).
#   Instead, it accepts them via __init__ (true constructor injection).

import os
import json
import logging
import hashlib
import redis
import asyncio
import chromadb # v10.2: Added
from chromadb.utils import embedding_functions # v10.2: Added
from openai import AsyncOpenAI
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger("core_v10_2")

# ============================================================================
# CONFIGURATION
# ============================================================================

class ConfigV10_2:
    """Configuration loader for v10.2"""
    
    def __init__(self, config_path: str = "master_config_v10_2.json"):
        with open(config_path, 'r') as f:
            self._config = json.load(f)
        
        # Validate schema version
        if self._config.get("schema_version") != "master_config_v10.2":
            raise ValueError(f"Config schema mismatch. Expected v10.2, got {self._config.get('schema_version')}")
        
        logger.info("Loaded v10.2 configuration")
    
    def __getattr__(self, name):
        """Dynamic attribute access for nested config"""
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        
        # Convert snake_case section names
        section = self._config.get(name)
        if section is None:
            # Try converting to snake_case for access
            snake_name = name.replace('-', '_')
            section = self._config.get(snake_name)
            if section is None:
                raise AttributeError(f"Config section '{name}' or '{snake_name}' not found")

        # Return ConfigSection wrapper for nested access
        return ConfigSection(section)

class ConfigSection:
    """Wrapper for nested config sections"""
    
    def __init__(self, data: Dict):
        self._data = data
    
    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        
        value = self._data.get(name)
        if value is None:
            # Try converting to snake_case for access
            snake_name = name.replace('-', '_')
            value = self._data.get(snake_name)
            if value is None:
                raise AttributeError(f"Config key '{name}' or '{snake_name}' not found")
        
        # Recursively wrap dicts
        if isinstance(value, dict):
            return ConfigSection(value)
        return value
    
    def get(self, key, default=None):
        """Dict-like get with default"""
        return self._data.get(key, default)
    
    def __contains__(self, key):
        return key in self._data

# ============================================================================
# EXCEPTION HIERARCHY (Preserved from v10.0)
# ============================================================================

class WorkflowError(Exception):
    """Base exception for workflow errors"""
    pass

class ModelAPIError(WorkflowError):
    """LLM API call failed"""
    pass

class JSONParsingError(WorkflowError):
    """Failed to parse JSON from LLM"""
    pass

class ValidationError(WorkflowError):
    """Validation failed"""
    pass

class FileIOError(WorkflowError):
    """File read/write error"""
    pass

class CostCeilingExceededError(WorkflowError):
    """Cost ceiling exceeded"""
    pass

class CircuitBreakerOpenError(WorkflowError):
    """Circuit breaker is open"""
    pass

# ============================================================================
# ROW 7: FEEDBACK LOG READER (Preserved from v10.1)
# ============================================================================

@dataclass
class FeedbackEntry:
    """Single feedback entry from feedback_log.jsonl"""
    timestamp: str
    workflow_id: str
    agent_name: str
    task: str
    feedback_type: str  # "success", "failure", "warning"
    details: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class FeedbackLogReader:
    """Reads and parses feedback_log.jsonl for agent selection"""
    
    def __init__(self, feedback_log_path: str):
        self.feedback_log_path = feedback_log_path
        self.logger = logging.getLogger(f"{__name__}.FeedbackLogReader")
        self._cache: List[FeedbackEntry] = []
        self._last_read_time: Optional[float] = None
        self._cache_ttl = 60.0  # Refresh every 60 seconds
    
    def read_recent_feedback(self, max_entries: int = 100) -> List[FeedbackEntry]:
        """Read recent feedback entries"""
        now = datetime.now().timestamp()
        
        # Check cache freshness
        if self._last_read_time and (now - self._last_read_time) < self._cache_ttl:
            return self._cache[-max_entries:]
        
        # Read from disk
        try:
            if not os.path.exists(self.feedback_log_path):
                self.logger.warning(f"Feedback log not found: {self.feedback_log_path}")
                return []
            
            entries = []
            with open(self.feedback_log_path, 'r') as f:
                lines = f.readlines()[-max_entries:]
                for line in lines:
                    try:
                        data = json.loads(line.strip())
                        entry = FeedbackEntry(
                            timestamp=data.get("timestamp", ""),
                            workflow_id=data.get("workflow_id", ""),
                            agent_name=data.get("agent_name", ""),
                            task=data.get("task", ""),
                            feedback_type=data.get("feedback_type", ""),
                            details=data.get("details", {}),
                            metadata=data.get("metadata", {})
                        )
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            self._cache = entries
            self._last_read_time = now
            self.logger.info(f"Loaded {len(entries)} feedback entries")
            return entries
            
        except Exception as e:
            self.logger.error(f"Failed to read feedback log: {e}")
            return []
    
    def get_agent_success_rate(self, agent_name: str, task_type: str = None) -> float:
        """Calculate success rate for an agent"""
        entries = self.read_recent_feedback()
        
        # Filter by agent and task
        relevant = [
            e for e in entries 
            if e.agent_name == agent_name 
            and (task_type is None or e.task == task_type)
        ]
        
        if not relevant:
            return 0.5  # Default 50% if no data
        
        success_count = sum(1 for e in relevant if e.feedback_type == "success")
        return success_count / len(relevant)
    
    def get_best_agent_for_task(self, task_type: str, candidates: List[str]) -> str:
        """Select best agent based on historical success"""
        best_agent = candidates[0]
        best_rate = 0.0
        
        for agent in candidates:
            rate = self.get_agent_success_rate(agent, task_type)
            if rate > best_rate:
                best_rate = rate
                best_agent = agent
        
        self.logger.info(f"Selected {best_agent} for {task_type} (success rate: {best_rate:.2%})")
        return best_agent
    
    def get_failure_patterns(self, agent_name: str = None) -> List[Dict[str, Any]]:
        """Extract failure patterns for meta-learning"""
        entries = self.read_recent_feedback()
        
        if agent_name:
            entries = [e for e in entries if e.agent_name == agent_name]
        
        failures = [e for e in entries if e.feedback_type == "failure"]
        
        # Group by failure reason
        patterns = {}
        for entry in failures:
            reason = entry.details.get("reason", "unknown")
            if reason not in patterns:
                patterns[reason] = {
                    "reason": reason,
                    "count": 0,
                    "agents": set(),
                    "tasks": set(),
                    "examples": []
                }
            patterns[reason]["count"] += 1
            patterns[reason]["agents"].add(entry.agent_name)
            patterns[reason]["tasks"].add(entry.task)
            patterns[reason]["examples"].append({
                "workflow_id": entry.workflow_id,
                "details": entry.details
            })
        
        # Convert sets to lists for JSON serialization
        result = []
        for pattern in patterns.values():
            pattern["agents"] = list(pattern["agents"])
            pattern["tasks"] = list(pattern["tasks"])
            pattern["examples"] = pattern["examples"][:3]  # Keep max 3 examples
            result.append(pattern)
        
        return sorted(result, key=lambda x: x["count"], reverse=True)

# ============================================================================
# ROW 7: PROPOSED RULES LOADER (Hot-Reloading) (Preserved from v10.1)
# ============================================================================

@dataclass
class ProposedRule:
    """Single proposed rule from proposed_rules.jsonl"""
    timestamp: str
    status: str  # "PROPOSED", "APPROVED", "REJECTED"
    rule_type: str
    description: str
    config_changes: Dict[str, Any]
    pattern_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProposedRulesLoader:
    """Hot-reloads proposed_rules.jsonl for dynamic constitution updates"""
    
    def __init__(self, proposed_rules_path: str):
        self.proposed_rules_path = proposed_rules_path
        self.logger = logging.getLogger(f"{__name__}.ProposedRulesLoader")
        self._cache: List[ProposedRule] = []
        self._last_mtime: Optional[float] = None
    
    def load_rules(self, status_filter: str = "APPROVED") -> List[ProposedRule]:
        """Load rules, hot-reloading if file changed"""
        try:
            if not os.path.exists(self.proposed_rules_path):
                self.logger.warning(f"Proposed rules file not found: {self.proposed_rules_path}")
                return []
            
            # Check if file was modified
            current_mtime = os.path.getmtime(self.proposed_rules_path)
            if self._last_mtime == current_mtime:
                # Return cached rules
                return [r for r in self._cache if r.status == status_filter]
            
            # Hot-reload
            self.logger.info(f"Hot-reloading proposed rules (file modified)")
            rules = []
            with open(self.proposed_rules_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        pattern_data = data.get("pattern", {})
                        rule = ProposedRule(
                            timestamp=data.get("timestamp", ""),
                            status=data.get("status", "PROPOSED"),
                            rule_type=pattern_data.get("type", "unknown"),
                            description=pattern_data.get("description", ""),
                            config_changes=pattern_data.get("config_changes", {}),
                            pattern_id=pattern_data.get("id", ""),
                            metadata=pattern_data.get("metadata", {})
                        )
                        rules.append(rule)
                    except json.JSONDecodeError:
                        continue
            
            self._cache = rules
            self._last_mtime = current_mtime
            
            filtered = [r for r in rules if r.status == status_filter]
            self.logger.info(f"Loaded {len(filtered)} {status_filter} rules")
            return filtered
            
        except Exception as e:
            self.logger.error(f"Failed to load proposed rules: {e}")
            return []
    
    def get_safety_constitution_updates(self) -> List[str]:
        """Get approved safety constitution additions"""
        rules = self.load_rules(status_filter="APPROVED")
        safety_rules = [r for r in rules if r.rule_type in ["safety_constraint", "bias_check", "pii_detection"]]
        
        constitution_updates = []
        for rule in safety_rules:
            update = rule.config_changes.get("constitution_addition")
            if update:
                constitution_updates.append(update)
        
        return constitution_updates
    
    def get_constitution_rules(self) -> List[Dict[str, Any]]:
        """Extract constitution-type rules for bias detection
        
        Returns list of config_changes dicts from rules with type='constitution'
        """
        rules = self.load_rules(status_filter="APPROVED")
        
        constitution_rules = [
            r.config_changes 
            for r in rules 
            if r.rule_type.lower() == "constitution"
        ]
        
        self.logger.info(f"Extracted {len(constitution_rules)} constitution rules")
        return constitution_rules
    
    def get_config_overrides(self) -> Dict[str, Any]:
        """Get approved config overrides"""
        rules = self.load_rules(status_filter="APPROVED")
        
        overrides = {}
        for rule in rules:
            for key, value in rule.config_changes.items():
                if key != "constitution_addition":  # Skip constitution updates
                    overrides[key] = value
        
        return overrides

# ============================================================================
# ROW 5: CACHE MANAGER (Preserved from v10.0)
# ============================================================================

class CacheManager:
    """Redis-based LLM response cache"""
    
    def __init__(self, redis_client: redis.Redis, ttl_seconds: int = 3600):
        self.redis = redis_client
        self.ttl = ttl_seconds
        self.logger = logging.getLogger(f"{__name__}.CacheManager")
        self._hits = 0
        self._misses = 0
    
    def _generate_cache_key(self, provider: str, model: str, prompt: str, temperature: float) -> str:
        """Generate SHA256 cache key"""
        key_str = f"{provider}:{model}:{prompt}:{temperature}"
        return f"llm_cache:{hashlib.sha256(key_str.encode()).hexdigest()}"
    
    def get(self, provider: str, model: str, prompt: str, temperature: float) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        cache_key = self._generate_cache_key(provider, model, prompt, temperature)
        
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                self._hits += 1
                self.logger.debug(f"Cache HIT: {cache_key[:16]}...")
                return json.loads(cached_data)
            else:
                self._misses += 1
                self.logger.debug(f"Cache MISS: {cache_key[:16]}...")
                return None
        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            self._misses += 1
            return None
    
    def set(self, provider: str, model: str, prompt: str, temperature: float, response: Dict[str, Any]):
        """Cache response"""
        cache_key = self._generate_cache_key(provider, model, prompt, temperature)
        
        try:
            self.redis.setex(cache_key, self.ttl, json.dumps(response))
            self.logger.debug(f"Cached response: {cache_key[:16]}...")
        except Exception as e:
            self.logger.error(f"Cache set error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_rate_pct": hit_rate
        }

# ============================================================================
# ROW 4: COST TRACKER (Preserved from v10.1)
# ============================================================================

class CostTracker:
    """Tracks LLM API costs per workflow"""
    
    # Pricing matches models from agentic_design_v10_1.md/master_config_v10_1.json
    PRICING = {
        "anthropic": {
            "claude-4.1-opus": {"input": 0.015, "output": 0.075},
            "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015}
        },
        "google": {
            "gemini-2.5-pro": {"input": 0.002, "output": 0.006},
            "gemini-2.5-flash": {"input": 0.0001, "output": 0.0003},
            "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0}
        },
        "openai": {
            "gpt-5": {"input": 0.05, "output": 0.15},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015}
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CostTracker")
        self._workflow_costs: Dict[str, List[Dict]] = {}
    
    def log_cost(self, workflow_id: str, agent_name: str, model_name: str,
                 input_tokens: int, output_tokens: int):
        """Log cost (wrapper for record_call)"""
        provider = self._get_provider_name(model_name)
        self.record_call(workflow_id, provider, model_name, input_tokens, output_tokens)

    def _get_provider_name(self, model_name: str) -> str:
        """Extract provider name from model"""
        if "claude" in model_name:
            return "anthropic"
        elif "gemini" in model_name:
            return "google"
        elif "gpt-" in model_name:
            return "openai"
        return "unknown"
    
    def record_call(self, workflow_id: str, provider: str, model: str, 
                    input_tokens: int, output_tokens: int):
        """Record a single LLM call"""
        pricing = self.PRICING.get(provider, {}).get(model)
        if not pricing:
            self.logger.warning(f"No pricing for {provider}/{model}")
            return
        
        cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
        
        if workflow_id not in self._workflow_costs:
            self._workflow_costs[workflow_id] = []
        
        self._workflow_costs[workflow_id].append({
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "timestamp": datetime.now().isoformat()
        })
        
        self.logger.debug(f"Recorded ${cost:.4f} for {workflow_id}")
    
    def get_cost_summary(self, workflow_id: str) -> Dict[str, Any]:
        """Get cost summary for workflow"""
        calls = self._workflow_costs.get(workflow_id, [])
        total_cost = sum(c["cost"] for c in calls)
        total_input = sum(c["input_tokens"] for c in calls)
        total_output = sum(c["output_tokens"] for c in calls)
        
        return {
            "workflow_id": workflow_id,
            "total_workflow_cost": total_cost,
            "total_calls": len(calls),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "calls": calls
        }

# ============================================================================
# BASE AGENT CLASS (Preserved from v10.1)
# ============================================================================

class BaseAgent:
    """Base class for all agents with context injection"""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        self.context = context
        self.config = context.config 
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
    
    def log_feedback(self, workflow_id: str, task: str, feedback_type: str, details: Dict[str, Any]):
        """v10.1: Log feedback to feedback_log.jsonl"""
        try:
            feedback_entry = {
                "timestamp": datetime.now().isoformat(),
                "workflow_id": workflow_id,
                "agent_name": self.__class__.__name__,
                "task": task,
                "feedback_type": feedback_type,
                "details": details,
                "metadata": {}
            }
            
            feedback_log_path = self.config.meta_loop_config.feedback_log_path
            os.makedirs(os.path.dirname(feedback_log_path), exist_ok=True)
            
            with open(feedback_log_path, 'a') as f:
                json.dump(feedback_entry, f)
                f.write('\n')
            
            self.log_debug(f"Logged feedback: {feedback_type} for {task}")
        except Exception as e:
            self.log_error(f"Failed to log feedback: {e}")
    
    # Helper to get a configured model client
    def get_model_client(self, model_config_name: str) -> "AsyncBaseModelClient":
        """Helper to get a model client from config"""
        model_config = getattr(self.config.model_config, model_config_name)
        
        client = self.context.get_model_client(
            model_config.provider, 
            model_config.model_name
        )
        
        # Update client with workflow-specific IDs
        client.workflow_id = self.context.workflow_id
        client.agent_name = self.__class__.__name__
        
        return client
        
# ============================================================================
# ROW 6: ASYNC LLM CLIENTS (Preserved from v10.1)
# ============================================================================

class AsyncBaseModelClient:
    """Base class for async LLM clients"""
    
    def __init__(self, model_name: str, cache_manager, cost_tracker, workflow_id: str, agent_name: str):
        self.model_name = model_name
        self.cache_manager = cache_manager
        self.cost_tracker = cost_tracker
        self.workflow_id = workflow_id
        self.agent_name = agent_name
    
    def _get_provider_name(self) -> str:
        """Extract provider name from model"""
        if "claude" in self.model_name:
            return "anthropic"
        elif "gemini" in self.model_name:
            return "google"
        elif "gpt-" in self.model_name:
            return "openai"
        return "unknown"
    
    async def chat_completion_async(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.7,
                                   response_format: Optional[str] = None) -> Dict[str, Any]:
        """Abstract method - implement in subclasses"""
        raise NotImplementedError

class AnthropicAsyncClient(AsyncBaseModelClient):
    """Async Anthropic/Claude API client with caching"""
    
    async def chat_completion_async(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.7,
                                   response_format: Optional[str] = None) -> Dict[str, Any]:
        """Async chat completion with caching"""
        import anthropic
        
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        provider = self._get_provider_name()
        
        cached_response = self.cache_manager.get(provider, self.model_name, prompt, temperature)
        if cached_response:
            return cached_response
        
        try:
            client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            
            response = await client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                temperature=temperature,
                messages=messages
            )
            
            content = response.content[0].text
            
            if response_format == "json_object":
                try:
                    # Find the JSON object
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end]
                        content = json.loads(json_str)
                    else:
                        raise JSONParsingError("No JSON object found in response")
                except json.JSONDecodeError as e:
                    raise JSONParsingError(f"Failed to parse JSON response: {e}")
            
            result = {
                "content": content,
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens
                }
            }
            
            self.cost_tracker.log_cost(
                self.workflow_id, self.agent_name, self.model_name,
                response.usage.input_tokens, response.usage.output_tokens
            )
            
            self.cache_manager.set(provider, self.model_name, prompt, temperature, result)
            
            return result
            
        except Exception as e:
            raise ModelAPIError(f"Anthropic API call failed: {e}")

class GeminiAsyncClient(AsyncBaseModelClient):
    """Async Google Gemini API client with caching"""
    
    async def chat_completion_async(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.7,
                                   response_format: Optional[str] = None) -> Dict[str, Any]:
        """Async chat completion with caching"""
        import google.generativeai as genai
        
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        provider = self._get_provider_name()
        
        cached_response = self.cache_manager.get(provider, self.model_name, prompt, temperature)
        if cached_response:
            return cached_response
        
        try:
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            
            # Note: Gemini's JSON mode is handled differently
            gen_config = {"temperature": temperature}
            if response_format == "json_object":
                gen_config["response_mime_type"] = "application/json"
            
            model = genai.GenerativeModel(self.model_name)
            
            prompt_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            
            response = await asyncio.to_thread(
                model.generate_content,
                prompt_text,
                generation_config=gen_config
            )
            
            content = response.text
            
            if response_format == "json_object":
                try:
                    # Gemini (with mime_type) should return a valid JSON string
                    content = json.loads(content)
                except json.JSONDecodeError as e:
                    raise JSONParsingError(f"Failed to parse JSON response from Gemini: {e}")
            
            result = {
                "content": content,
                "usage": {
                    # Gemini API v1 does not return token counts in response
                    "prompt_tokens": 0, 
                    "completion_tokens": 0
                }
            }
            
            self.cache_manager.set(provider, self.model_name, prompt, temperature, result)
            
            return result
            
        except Exception as e:
            raise ModelAPIError(f"Gemini API call failed: {e}")

class OpenAIAsyncClient(AsyncBaseModelClient):
    """Async OpenAI API client with caching"""
    
    async def chat_completion_async(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.7,
                                   response_format: Optional[str] = None) -> Dict[str, Any]:
        """Async chat completion with caching"""
        
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        provider = self._get_provider_name()
        
        cached_response = self.cache_manager.get(provider, self.model_name, prompt, temperature)
        if cached_response:
            return cached_response
        
        try:
            client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Prepare response format if requested
            completion_kwargs = {
                "model": self.model_name,
                "temperature": temperature,
                "messages": messages
            }
            if response_format == "json_object":
                completion_kwargs["response_format"] = {"type": "json_object"}

            response = await client.chat.completions.create(**completion_kwargs)
            
            content = response.choices[0].message.content
            
            if response_format == "json_object":
                try:
                    # OpenAI returns a string, so we must parse it
                    content = json.loads(content)
                except json.JSONDecodeError as e:
                    raise JSONParsingError(f"Failed to parse JSON response from OpenAI: {e}")
            
            result = {
                "content": content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
            
            self.cost_tracker.log_cost(
                self.workflow_id, self.agent_name, self.model_name,
                response.usage.prompt_tokens, response.usage.completion_tokens
            )
            
            self.cache_manager.set(provider, self.model_name, prompt, temperature, result)
            
            return result
            
        except Exception as e:
            raise ModelAPIError(f"OpenAI API call failed: {e}")

# ============================================================================
# ROW 4: WORKFLOW CONTEXT (Design-Aligned v10.2)
# ============================================================================

class WorkflowContext:
    """
    GAP 4 FIX: Dependency injection container for v10.2.
    This class no longer CREATES dependencies (Service Locator anti-pattern).
    It now RECEIVES them in its constructor (true DI).
    """
    
    def __init__(self, 
                 config: ConfigV10_2, 
                 redis_client: redis.Redis,
                 chromadb_client: chromadb.Client, # v10.2: Added
                 cache_manager: CacheManager,
                 cost_tracker: CostTracker,
                 feedback_reader: FeedbackLogReader,
                 rules_loader: ProposedRulesLoader):
        
        self.config = config
        self.redis_client = redis_client
        self.chromadb_client = chromadb_client # v10.2: Added
        self.workflow_id: str = "" # This will be set by the runner
        
        # GAP 4 FIX: Assign injected dependencies
        self.cache_manager = cache_manager
        self.cost_tracker = cost_tracker
        self.feedback_reader = feedback_reader
        self.rules_loader = rules_loader
        
        # Model client registry
        self._model_clients: Dict[str, Any] = {}
        
        logger.info("WorkflowContext initialized with v10.2 injected dependencies")
    
    def get_model_client(self, provider: str, model_name: str):
        """Get or create model client (no circular dependency - clients in core)"""
        key = f"{provider}:{model_name}"
        
        if key not in self._model_clients:
            base_args = {
                "model_name": model_name,
                "cache_manager": self.cache_manager,
                "cost_tracker": self.cost_tracker,
                "workflow_id": self.workflow_id, # Will be set at runtime
                "agent_name": "" # Will be set by BaseAgent
            }
            
            if provider == "anthropic":
                self._model_clients[key] = AnthropicAsyncClient(**base_args)
            elif provider == "google":
                self._model_clients[key] = GeminiAsyncClient(**base_args)
            elif provider == "openai":
                self._model_clients[key] = OpenAIAsyncClient(**base_args)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        client = self._model_clients[key]
        # Ensure workflow_id is updated for this context
        client.workflow_id = self.workflow_id
        return client

# ============================================================================
# STATE MODELS (Preserved from v10.0, Enhanced for v10.2)
# ============================================================================

@dataclass
class ResumeContext:
    """Resume-related state"""
    master_resume: Dict[str, Any] = field(default_factory=dict)
    sanitized_resume: Dict[str, Any] = field(default_factory=dict)
    experience_bullets: List[Dict] = field(default_factory=list)

@dataclass
class JobContext:
    """Job description state"""
    raw_jd: str = ""
    company: str = ""
    job_title: str = ""
    parsed_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyContext:
    """Strategy state"""
    strategy_plan: Dict[str, Any] = field(default_factory=dict)
    tot_branches: List[Dict] = field(default_factory=list)

@dataclass
class PromptContext:
    """Prompt engineering state"""
    prompts: Dict[str, str] = field(default_factory=dict)

@dataclass
class BulletContext:
    """Bullet generation state"""
    generated_bullets: List[Dict] = field(default_factory=list) # Now {text, experience}
    critiqued_bullets: List[Dict] = field(default_factory=list) # Now {text, score, feedback}

@dataclass
class DraftContext:
    """Drafting state"""
    sections: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QAContext:
    """QA state"""
    validation_results: Dict[str, Any] = field(default_factory=dict)
    qa_passed: bool = False

@dataclass
class ArtifactContext:
    """Artifact storage"""
    artifacts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetadataContext:
    """Workflow metadata"""
    workflow_id: str = ""
    timestamp: str = ""
    cost: float = 0.0
    retries: Dict[str, int] = field(default_factory=lambda: {"bullet_retries": 0, "qa_retries": 0})

@dataclass
class SafetyContext:
    """Safety checks state"""
    pii_detected: bool = False
    bias_detected: bool = False
    safety_notes: List[str] = field(default_factory=list)

@dataclass
class FeedbackContext:
    """v10.2: Feedback-aware state"""
    recent_feedback: List[FeedbackEntry] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    selected_agents: Dict[str, str] = field(default_factory=dict)  # task -> agent_name

@dataclass
class HILContext:
    """v10.2: HIL state"""
    ambiguity_detected: bool = False
    ambiguity_report: Dict[str, Any] = field(default_factory=dict)
    next_step: str = "" # From feedback router

@dataclass
class MainGraphState:
    """Main workflow state (v10.2 Design-Aligned)"""
    resume: ResumeContext = field(default_factory=ResumeContext)
    job: JobContext = field(default_factory=JobContext)
    strategy: StrategyContext = field(default_factory=StrategyContext)
    prompts: PromptContext = field(default_factory=PromptContext)
    bullets: BulletContext = field(default_factory=BulletContext)
    draft: DraftContext = field(default_factory=DraftContext)
    qa: QAContext = field(default_factory=QAContext)
    artifacts: ArtifactContext = field(default_factory=ArtifactContext)
    metadata: MetadataContext = field(default_factory=MetadataContext)
    safety: SafetyContext = field(default_factory=SafetyContext)
    feedback: FeedbackContext = field(default_factory=FeedbackContext)
    hil: HILContext = field(default_factory=HILContext)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for LangGraph"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MainGraphState':
        """Create from dict"""
        state = cls()
        state.resume = ResumeContext(**data.get("resume", {}))
        state.job = JobContext(**data.get("job", {}))
        state.strategy = StrategyContext(**data.get("strategy", {}))
        state.prompts = PromptContext(**data.get("prompts", {}))
        state.bullets = BulletContext(**data.get("bullets", {}))
        state.draft = DraftContext(**data.get("draft", {}))
        state.qa = QAContext(**data.get("qa", {}))
        state.artifacts = ArtifactContext(**data.get("artifacts", {}))
        state.metadata = MetadataContext(**data.get("metadata", {}))
        state.safety = SafetyContext(**data.get("safety", {}))
        state.feedback = FeedbackContext(**data.get("feedback", {}))
        state.hil = HILContext(**data.get("hil", {}))
        return state

@dataclass
class MetaGraphState:
    """Meta-learning graph state"""
    raw_logs: Dict[str, str] = field(default_factory=dict)
    log_summary: Dict[str, Any] = field(default_factory=dict)
    patterns: List[Dict] = field(default_factory=list)
    hypotheses: List[Dict] = field(default_factory=list)
    proposal: Dict[str, Any] = field(default_factory=dict)
    critique: Dict[str, Any] = field(default_factory=dict)
    replan_count: int = 0
    workflow_id: str = ""


# ============================================================================
# SYSTEM PROMPTS FOR META-LEARNING (Preserved from v10.0)
# ============================================================================

META_LOG_READER_SYSTEM_PROMPT = """
You are a log analysis agent. Read the provided feedback and preference logs.
Extract key information about workflow outcomes, user preferences, and system behavior.

Output JSON with:
{
  "total_workflows": int,
  "success_rate": float,
  "common_feedback_themes": [str],
  "preference_patterns": [str]
}
"""

META_PATTERN_FINDER_SYSTEM_PROMPT = """
You are a pattern detection agent. Analyze the log summary and identify recurring issues.

Log data: {log_data}

Output JSON with:
{{
  "patterns": [
    {{
      "id": "unique_id",
      "description": "what is recurring",
      "frequency": "how often",
      "severity": "low|medium|high|critical",
      "affected_components": ["agent_name"]
    }}
  ]
}}
"""

META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT = """
You are a root cause analysis agent. Generate hypotheses for why these patterns occur.

Patterns: {patterns}
Previous critique: {critique}

Output JSON with:
{{
  "hypotheses": [
    {{
      "id": "hyp_id",
      "pattern_id": "related_pattern_id",
      "hypothesis": "why this happens",
      "evidence": ["supporting evidence"],
      "confidence": 0.0-1.0
    }}
  ]
}}
"""

META_PROPOSAL_DRAFTER_SYSTEM_PROMPT = """
You are a change proposal agent. Draft a specific config or prompt change.

Hypothesis: {hypothesis}

Output JSON with:
{{
  "type": "config_change|prompt_modification|agent_replacement",
  "description": "what to change",
  "config_changes": {{"key": "value"}},
  "expected_impact": "what will improve",
  "risk_level": "low|medium|high"
}}
"""

META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT = """
You are a proposal review agent. Critique the proposed change.

Patterns: {patterns}
Proposal: {proposal}

Output JSON with:
{{
  "critique_passed": true|false,
  "reason": "why pass/fail",
  "suggestions": ["improvements"]
}}
"""

# ============================================================================
# END OF core_v10_2.py
# ============================================================================