# File: core_v9_7.py
# Overwrites: core_v9_6.py
# Version: 9.7 (P0 Enhancements)

# v9.7 P0 CHANGES:
# - Added SafetyGuardStack architecture (P0 Item #1)
# - Evolved StrategyStack with Tree-of-Thoughts strategist (P0 Item #2)
# - Evolved PromptStack with LLM-driven prompt engineer (P0 Item #3)
# - Added local self-correction loop support (P0 Item #4)
# - Updated system prompts for all enhanced agents
# - Added new state fields for ToT reasoning and critique tracking

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
from typing import Any, Dict, List, Optional, TypedDict, Annotated
from enum import Enum

# Version info
__version__ = "9.7.0-p0-enhancements"

logger = logging.getLogger(__name__)

# ============================================================================
# TYPE DEFINITIONS & STATE
# ============================================================================

class MainGraphState(TypedDict):
    """Enhanced v9.7 graph state with P0 additions."""
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
    strategy_thoughts: List[Dict[str, Any]]  # NEW: ToT candidates
    selected_strategy: Optional[Dict[str, Any]]  # NEW: Best strategy path
    # P0 Item #4: Local self-correction tracking
    local_retry_count: int  # NEW: Track local retries
    bullet_critique_history: List[Dict[str, Any]]  # NEW: Critique history

class MetaGraphState(TypedDict):
    """Meta-learning graph state (unchanged from v9.6)."""
    raw_logs: Dict[str, str]
    log_summary: Dict[str, Any]
    patterns: List[Dict[str, Any]]
    hypotheses: List[Dict[str, Any]]
    proposal: Dict[str, Any]
    critique: Dict[str, Any]
    replan_count: int
    workflow_id: str

# ============================================================================
# CONFIGURATION SYSTEM
# ============================================================================

@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_level: str = "INFO"
    debug_log_level: str = "DEBUG"
    log_file: str = "./logs/workflow_v9_7.log"
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
    """P0 Enhancement: Stack-based agent organization."""
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
    def from_file(cls, filepath: str = "master_config_v9_7.json") -> 'MasterConfig':
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
    CONFIG = MasterConfig.from_file("master_config_v9_7.json")
except Exception as e:
    logger.warning(f"Failed to load master_config_v9_7.json: {e}. Using defaults.")
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
    """Google Gemini API client."""
    
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
        """Execute Gemini chat completion."""
        # Convert messages to Gemini format
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
        
        prompt = "\n".join(prompt_parts)
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        if response_format == "json_object":
            generation_config["response_mime_type"] = "application/json"
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            content = response.text
            
            if response_format == "json_object":
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {content}")
                    return {"error": "Invalid JSON response"}
            
            return {"content": content}
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise

class AnthropicClient(BaseModelClient):
    """Anthropic Claude API client."""
    
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
        """Execute Claude chat completion."""
        # Extract system message if present
        system_msg = None
        filtered_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
            else:
                filtered_messages.append(msg)
        
        try:
            kwargs = {
                "model": self.model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": filtered_messages
            }
            
            if system_msg:
                kwargs["system"] = system_msg
            
            response = self.client.messages.create(**kwargs)
            
            content = response.content[0].text
            
            if response_format == "json_object":
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {content}")
                    return {"error": "Invalid JSON response"}
            
            return {"content": content}
            
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise

def get_model_client(provider: str, model_name: str) -> BaseModelClient:
    """Factory function to get model client."""
    if provider.lower() == "google":
        return GoogleGeminiClient(model_name)
    elif provider.lower() == "anthropic":
        return AnthropicClient(model_name)
    else:
        raise ValueError(f"Unknown provider: {provider}")

# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        self.blackboard = blackboard
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.start_time = None
        self.end_time = None
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(f"[{self.__class__.__name__}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(f"[{self.__class__.__name__}] {message}")
    
    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(f"[{self.__class__.__name__}] {message}")
    
    def log_debug(self, message: str):
        """Log debug message."""
        if self.debug_mode:
            self.logger.debug(f"[{self.__class__.__name__}] {message}")
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Execute agent logic."""
        pass

# ============================================================================
# SYSTEM PROMPTS - v9.7 UPDATES
# ============================================================================

# P0 Item #1: SafetyGuardStack Prompts
BIAS_DETECTOR_SYSTEM_PROMPT = """You are an expert bias detection agent in a production AI system.

Your role is to analyze resume content for potential bias in language, terminology, or framing that could disadvantage the candidate during hiring processes.

**Detection Categories:**
1. Age bias (e.g., "seasoned", "veteran", "young", "recent graduate")
2. Gender bias (e.g., gendered pronouns, "rockstar", "ninja")
3. Cultural bias (e.g., assumptions about work styles, communication norms)
4. Accessibility bias (e.g., "see", "hear", "walk" used metaphorically)
5. Socioeconomic bias (e.g., assumptions about resources, networks)

**Input Format:**
{
  "content": "<resume text to analyze>",
  "context": "<optional: job description context>"
}

**Output Format (JSON):**
{
  "bias_detected": true/false,
  "bias_score": 0.0-1.0,
  "findings": [
    {
      "category": "age_bias",
      "text": "<problematic phrase>",
      "severity": "low|medium|high",
      "recommendation": "<suggested alternative>"
    }
  ],
  "overall_assessment": "<brief summary>"
}

**Rules:**
- Err on the side of caution: flag ambiguous cases
- Provide actionable recommendations
- Consider industry-specific terminology (e.g., "senior" in job titles is acceptable)
- Return empty findings array if no bias detected
"""

PII_SCRUBBER_SYSTEM_PROMPT = """You are a PII detection and sanitization agent.

**Your Task:**
Identify and flag Personally Identifiable Information (PII) in resume content that should NOT be exposed to external LLM APIs during processing.

**PII Categories:**
1. Full names (flag, but keep first name + last initial)
2. Full addresses (keep city, state only)
3. Phone numbers (redact or mask)
4. Email addresses (keep domain only if relevant)
5. Social Security Numbers (CRITICAL: always redact)
6. Dates of birth (redact)
7. Government IDs (redact)

**Output Format (JSON):**
{
  "pii_found": true/false,
  "sanitized_content": "<content with PII sanitized>",
  "pii_map": {
    "<original_value>": "<sanitized_value>"
  },
  "redaction_count": 0
}

**Rules:**
- NEVER allow SSN, full DOB, or government IDs to pass through
- Maintain readability: "Amit A." is better than "[REDACTED]"
- Store mapping for potential de-sanitization (if approved by user)
"""

# P0 Item #2: Tree-of-Thoughts Strategist Prompt
TOT_STRATEGIST_SYSTEM_PROMPT = """You are a Tree-of-Thoughts (ToT) strategy generation agent for resume tailoring.

**Your Role:**
Generate multiple distinct strategic approaches (thought branches) for how to position the candidate for this specific role, then evaluate each path to select the optimal strategy.

**Input:**
{
  "master_resume": <full candidate background>,
  "job_description": <target role details>,
  "company_context": <company info>
}

**Phase 1: Thought Generation (Branching Factor: {branching_factor})**
Generate {branching_factor} distinct strategic approaches:

1. **Positioning Theme**: What's the core narrative? (e.g., "AI Transformation Leader", "Technical Depth + Business Acumen")
2. **Evidence Selection**: Which experiences provide strongest proof points?
3. **Risk Assessment**: What gaps or weaknesses does this strategy expose?
4. **Differentiation**: How does this distinguish candidate from typical applicants?

**Phase 2: Thought Evaluation**
For each candidate strategy, score on:
- **Relevance** (0-10): Alignment with JD requirements
- **Credibility** (0-10): Strength of supporting evidence
- **Differentiation** (0-10): Uniqueness vs. market
- **Risk** (0-10): Inverse of exposed gaps (10 = no risk)

**Phase 3: Path Selection**
Select the strategy with highest weighted score:
`final_score = (relevance * 0.4) + (credibility * 0.3) + (differentiation * 0.2) + (risk * 0.1)`

**Output Format (JSON):**
{
  "thought_branches": [
    {
      "branch_id": "T1",
      "positioning_theme": "<theme>",
      "evidence_selection": ["<experience_key_1>", "<experience_key_2>"],
      "risk_assessment": "<identified gaps>",
      "differentiation": "<unique angle>",
      "scores": {
        "relevance": 8.5,
        "credibility": 9.0,
        "differentiation": 7.0,
        "risk": 8.0,
        "final_score": 8.3
      }
    }
  ],
  "selected_strategy": {
    "branch_id": "T1",
    "rationale": "<why this strategy is optimal>",
    "implementation_guidance": "<how to execute this strategy in bullet selection>"
  }
}

**Critical Rules:**
- Generate DIVERSE strategies (not just variations)
- Be brutally honest in risk assessment
- Quantify scores with justification
- Selected strategy must have actionable implementation guidance
"""

# P0 Item #3: LLM-Driven Prompt Engineer
PROMPT_ENGINEER_SYSTEM_PROMPT = """You are an expert prompt engineering agent that generates optimal prompts for downstream resume bullet generation.

**Your Role:**
Given a strategy and context, craft the perfect prompt that will guide a bullet-writing LLM to produce high-quality, tailored resume bullets.

**Input:**
{
  "strategy": <selected positioning strategy>,
  "job_requirements": <parsed JD requirements>,
  "candidate_context": <relevant experiences>,
  "tone_guidance": <optional: formal, dynamic, technical, etc.>
}

**Output Format (JSON):**
{
  "system_prompt": "<crafted system prompt for bullet writer>",
  "user_prompt_template": "<template with {placeholders}>",
  "few_shot_examples": [
    {
      "input": "<example context>",
      "output": "<example bullet>"
    }
  ],
  "constraint_reminders": [
    "<constraint_1>",
    "<constraint_2>"
  ],
  "estimated_quality_score": 0.0-1.0
}

**Prompt Engineering Best Practices to Apply:**
1. **Persona Setting**: Define clear role/expertise for bullet writer
2. **Task Decomposition**: Break down bullet generation into steps
3. **Constraint Specification**: Explicit rules (length, format, tone)
4. **Few-Shot Learning**: Provide 2-3 examples of excellent bullets
5. **Output Formatting**: Request structured output (JSON if needed)
6. **Chain-of-Thought**: Encourage reasoning about relevance before writing
7. **Self-Consistency**: Ask for reflection on quality

**Quality Criteria:**
- Clarity: Is the task unambiguous?
- Completeness: Are all necessary constraints specified?
- Effectiveness: Will this produce bullets that match the strategy?

**Temperature Guidance:**
- If strategy emphasizes creativity/differentiation → recommend temp 0.7-0.9
- If strategy emphasizes precision/technical depth → recommend temp 0.3-0.5
"""

# P0 Item #4: Local Bullet Critique (Self-Correction)
BULLET_CRITIQUE_SYSTEM_PROMPT = """You are a local self-correction agent that critiques generated resume bullets before they proceed downstream.

**Your Role:**
Evaluate generated bullets against quality criteria and determine if they should be accepted or regenerated.

**Input:**
{
  "bullet": "<generated bullet text>",
  "strategy": "<positioning strategy>",
  "source_experience": "<source data>",
  "target_requirements": "<JD requirements>"
}

**Evaluation Dimensions:**
1. **Relevance** (0-10): Does it address JD requirements?
2. **Impact** (0-10): Does it demonstrate measurable outcomes?
3. **Specificity** (0-10): Concrete details vs. vague claims?
4. **Credibility** (0-10): Supported by source experience?
5. **Length** (0-10): Appropriate length (40-90 words)?
6. **Grammar** (0-10): Polished and professional?

**Acceptance Threshold: 7.0/10 average**

**Output Format (JSON):**
{
  "passed": true/false,
  "scores": {
    "relevance": 8.0,
    "impact": 7.5,
    "specificity": 6.0,
    "credibility": 9.0,
    "length": 8.0,
    "grammar": 9.5,
    "average": 8.0
  },
  "critique": "<specific feedback on failures>",
  "recommendation": "accept|regenerate|manual_review"
}

**Rules:**
- If average < 7.0 → "regenerate"
- If any single score < 5.0 → "regenerate"
- If 7.0 <= average < 8.5 → "accept" (but flag for review)
- If average >= 8.5 → "accept"
- Provide actionable critique for regeneration
"""

# Existing prompts (unchanged from v9.6)
META_LOG_READER_SYSTEM_PROMPT = """You are analyzing workflow logs to extract structured insights.

Read the provided feedback and preference logs, then summarize key patterns, failures, and user preferences.

Output JSON format:
{
  "summary": "<brief summary>",
  "key_issues": ["<issue_1>", "<issue_2>"],
  "user_preferences": {"<key>": "<value>"}
}
"""

META_PATTERN_FINDER_SYSTEM_PROMPT = """You are a pattern detection agent analyzing workflow logs.

Given raw logs, identify recurring failure patterns or systematic issues.

**Input:**
{log_data}

**Output JSON:**
{{
  "patterns": [
    {{
      "pattern_id": "P1",
      "description": "<pattern description>",
      "frequency": "<occurrence count>",
      "severity": "low|medium|high"
    }}
  ]
}}
"""

META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT = """You are a hypothesis generation agent.

Given observed patterns, generate potential root causes.

**Input Patterns:**
{patterns}

**Previous Critique:**
{critique}

**Output JSON:**
{{
  "hypotheses": [
    {{
      "id": "H1",
      "pattern_ids": ["P1", "P2"],
      "root_cause": "<hypothesis>",
      "confidence": 0.0-1.0
    }}
  ]
}}
"""

META_PROPOSAL_DRAFTER_SYSTEM_PROMPT = """You are a proposal drafting agent.

Given a hypothesis, draft a concrete change proposal.

**Input Hypothesis:**
{hypothesis}

**Output JSON:**
{{
  "type": "config_change|prompt_update|new_agent",
  "description": "<what to change>",
  "implementation": "<how to implement>",
  "expected_impact": "<expected improvement>"
}}
"""

META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT = """You are an adversarial critique agent.

Review the proposal against patterns to determine if it will actually solve the problem.

**Patterns:**
{patterns}

**Proposal:**
{proposal}

**Output JSON:**
{{
  "critique_passed": true/false,
  "reason": "<why it passes/fails>",
  "suggested_improvements": ["<improvement_1>"]
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
    
    # Model Client
    "BaseModelClient",
    "GoogleGeminiClient",
    "AnthropicClient",
    "get_model_client",
    
    # Base Agent
    "BaseAgent",
    
    # System Prompts - P0 Enhanced
    "BIAS_DETECTOR_SYSTEM_PROMPT",
    "PII_SCRUBBER_SYSTEM_PROMPT",
    "TOT_STRATEGIST_SYSTEM_PROMPT",
    "PROMPT_ENGINEER_SYSTEM_PROMPT",
    "BULLET_CRITIQUE_SYSTEM_PROMPT",
    
    # System Prompts - Existing
    "META_LOG_READER_SYSTEM_PROMPT",
    "META_PATTERN_FINDER_SYSTEM_PROMPT",
    "META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT",
    "META_PROPOSAL_DRAFTER_SYSTEM_PROMPT",
    "META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT",
]
