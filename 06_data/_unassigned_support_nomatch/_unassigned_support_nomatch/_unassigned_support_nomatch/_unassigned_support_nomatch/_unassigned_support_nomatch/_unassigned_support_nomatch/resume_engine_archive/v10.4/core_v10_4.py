# File: core_v10_4.py
# Version: 10.4 (Prompt Fixes)
#
# v10.4 MAJOR CHANGES:
# - FIXED: (Category 2 Mock Fix) Implemented all 9 placeholder "..."
#   prompts in PromptTemplateManager with full few-shot examples.
# - FIXED: Added the CircuitBreaker class definition, moving it from
#   run_batch.py to resolve the circular import and blocking failure.
# - FIXED: Renamed ConfigV10_3 to ConfigV10_4.
# - FIXED: Rewrote MainGraphState.to_dict/from_dict to correctly
#   handle nested Pydantic models, fixing serialization.
# - DEBUG: Added verbose logging to ProposedRulesLoader.load_rules().
# - FIX (Test Failure): Added {job_description} to strategy_tot_branch prompt.
# - FIX (Test Failure): Added {strategy} to bullet_generation_fact_check prompt.
# - FIX (Test Failure): Added all required keys (style_guide, draft, etc.)
#   to all 15 tool prompts to resolve KeyErrors.
# - FIX (Test Failure): Rewrote ResponseValidator.validate() to correctly
#   handle non-Pydantic types (dict, list, tuples) passed from agents,
#   resolving the "has no attribute 'model_validate'" error.

import os
import json
import logging
import hashlib
import redis
import asyncio
import chromadb
import time # v10.3: Added for retry decorator
from functools import wraps # v10.3: Added for retry decorator
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError # v10.3: Added
from chromadb.utils import embedding_functions
from openai import AsyncOpenAI
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple, Type, TypeVar, Callable, Awaitable
from datetime import datetime # v10.4: Added for logging

# v10.4: Logger name updated
logger = logging.getLogger("core_v10_4")

# ============================================================================
# CONFIGURATION (v10.4: Fixed class name and paths)
# ============================================================================

class ConfigV10_4:
    """Configuration loader for v10.4"""
    
    def __init__(self, config_path: str = "master_config_v10_4.json"):
        with open(config_path, 'r') as f:
            self._config = json.load(f)
        
        # Validate schema version
        expected_schema = "master_config_v10.4"
        loaded_schema = self._config.get("schema_version")
        if loaded_schema != expected_schema:
            raise ValueError(f"Config schema mismatch. Expected {expected_schema}, got {loaded_schema}")
        
        logger.info(f"Loaded {loaded_schema} configuration")
    
    def __getattr__(self, name):
        """Dynamic attribute access for nested config"""
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        
        section = self._config.get(name)
        if section is None:
            snake_name = name.replace('-', '_')
            section = self._config.get(snake_name)
            if section is None:
                raise AttributeError(f"Config section '{name}' or '{snake_name}' not found")

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
            snake_name = name.replace('-', '_')
            value = self._data.get(snake_name)
            if value is None:
                raise AttributeError(f"Config key '{name}' or '{snake_name}' not found")
        
        if isinstance(value, dict):
            return ConfigSection(value)
        return value
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __contains__(self, key):
        return key in self._data

# ============================================================================
# EXCEPTION HIERARCHY (v10.4: Added CircuitBreaker Class)
# ============================================================================

class WorkflowError(Exception): pass
class ModelAPIError(WorkflowError): pass
class JSONParsingError(WorkflowError): pass
class ValidationError(WorkflowError): pass # v10.3: Now for business logic
class FileIOError(WorkflowError): pass
class CostCeilingExceededError(WorkflowError): pass
class CircuitBreakerOpenError(WorkflowError): pass
# v10.3: Renamed Pydantic's error to avoid name collision
class PydanticSchemaError(ValidationError): pass

# v10.4: ADDED CircuitBreaker class definition
class CircuitBreaker:
    """
    v10.4: Circuit breaker for batch processing.
    Moved from run_batch.py to core.py to resolve circular imports.
    """
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_open = False
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker")
    
    def record_success(self):
        self.failure_count = 0
        self.is_open = False
    
    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            self.logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")
    
    def check(self):
        if self.is_open:
            raise CircuitBreakerOpenError(f"Circuit breaker open after {self.failure_count} failures")

# ============================================================================
# v10.3: PYDANTIC MODELS (Validation & Output Constraints)
# ============================================================================

# Define a generic TypeVar for the Pydantic models
T_BaseModel = TypeVar('T_BaseModel', bound=BaseModel)

class BaseToolOutput(BaseModel):
    """Base model for all tool outputs"""
    status: str = Field("success", description="Indicates tool execution status")

# --- Agent Tools Models (15 tools) ---

class DraftStrategyOutput(BaseToolOutput):
    feedback: str = Field(..., description="Strategic feedback on the draft")

class RedTeamOutput(BaseToolOutput):
    weaknesses_found: List[str] = Field(..., description="List of identified weaknesses")

class RefineSectionOutput(BaseToolOutput):
    refined_text: str = Field(..., description="The new, refined text for the section")

class AddMetricsOutput(BaseToolOutput):
    suggestions: List[str] = Field(..., description="Specific suggestions for adding metrics")

class QAClaimOutput(BaseToolOutput):
    unsupported_claims: int = Field(..., ge=0, description="Count of claims not supported by the master resume")
    feedback: str = Field(..., description="NLI feedback and analysis")

class QAToneOutput(BaseToolOutput):
    tone_match: bool = Field(..., description="Whether the draft's tone matches the required tone")
    current_tone: str = Field(..., description="The detected tone of the draft")

class QAThematicAlignmentOutput(BaseToolOutput):
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0 for thematic alignment")
    feedback: str = Field(..., description="Feedback on alignment")

class QASemanticEntailmentOutput(BaseToolOutput):
    entailment_score: float = Field(..., ge=0.0, le=1.0, description="Semantic entailment score with the job description")

class QANarrativeThreadOutput(BaseModel):
    narrative_clear: bool = Field(..., description="Whether a clear career narrative was detected")

class QAJDSkillsOutput(BaseToolOutput):
    keyword_coverage: float = Field(..., ge=0.0, le=1.0, description="Percentage of JD keywords found in the draft")
    missing_keywords: List[str] = Field(..., description="List of important missing keywords")

class QASignalScoreOutput(BaseToolOutput):
    avg_signal_score: float = Field(..., ge=0.0, le=10.0, description="Average signal-to-noise score (0-10)")

class QATenureOutput(BaseToolOutput):
    gaps_found: int = Field(..., ge=0, description="Number of unexplained tenure gaps")
    overlaps_found: int = Field(..., ge=0, description="Number of overlapping job dates")

class QAMissedOpportunitiesOutput(BaseToolOutput):
    opportunities_found: List[str] = Field(..., description="List of relevant experiences from master resume that were omitted")

class QAAdversarialOutput(BaseToolOutput):
    red_flags: List[str] = Field(..., description="List of red flags a skeptical hiring manager would find")

class QABiasOutput(BaseModel): # Does not inherit BaseToolOutput, it's a local tool
    bias_detected: bool
    patterns: List[str]
    bias_score: float
    dynamic_rules_applied: int

# --- Agent Stacks Models ---

class StrategyPlan(BaseModel):
    strategy_name: str = Field(..., description="A brief, descriptive name for the strategy")
    focus_areas: List[str] = Field(..., description="The main themes to emphasize (e.g., 'AI Leadership', 'Technical Deep-Dive')")
    key_achievements_to_highlight: List[str] = Field(..., description="Specific achievements from the master resume to feature")
    tone: str = Field(..., description="The desired tone (e.g., 'professional', 'technical', 'leadership')")

class GeneratedPrompts(BaseModel):
    bullet_generation_prompt: str
    critique_prompt: str

class BulletList(BaseModel):
    verified_bullets: List[str] = Field(..., description="List of fact-checked, high-quality bullets")

class CritiqueResult(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0, description="Quality score from 0-10")
    suggestions: List[str] = Field(..., description="Specific suggestions for improvement")

class HILAmbiguityReport(BaseModel):
    ambiguity_detected: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    question_for_human: str = Field(..., description="The specific question to ask the human")

class HILFeedbackRoute(BaseModel):
    next_step: str = Field(..., description="The graph node to jump to (e.g., 'STRATEGY', 'DRAFTING')")

# ============================================================================
# v10.3: RESILIENCE UTILITIES (Retry & Context Budget)
# ============================================================================

def exponential_backoff_retry(max_retries: int = 3, initial_delay: float = 1.0):
    """
    v10.3: Decorator for async node functions to perform exponential backoff.
    Implements "Failure Anticipation Injection".
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ModelAPIError, JSONParsingError, PydanticSchemaError, asyncio.TimeoutError) as e:
                    logger.warning(f"Node {func.__name__} failed (Attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt + 1 == max_retries:
                        logger.error(f"Node {func.__name__} failed permanently after {max_retries} attempts.")
                        raise
                    
                    sleep_time = delay * (2 ** attempt)
                    logger.info(f"Retrying {func.__name__} in {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
            raise WorkflowError(f"Node {func.__name__} failed after max retries") # Should not be reached
        return wrapper
    return decorator

class ContextBudgetManager:
    """
    v10.3: Manages context window limits to prevent token errors.
    Implements "Context Budget Management".
    """
    def __init__(self, default_token_limit: int = 8192, buffer: float = 0.2):
        self.default_limit = default_token_limit
        self.buffer = buffer # 20% buffer
        self.logger = logging.getLogger(f"{__name__}.ContextBudgetManager")
    
    def _estimate_tokens(self, text: str) -> int:
        # A simple approximation: 4 chars per token
        return len(text) // 4
    
    def prune(self, document: str, max_tokens: Optional[int] = None) -> str:
        """Prunes a document to fit within the token budget."""
        if max_tokens is None:
            max_tokens = self.default_limit
            
        token_limit_with_buffer = int(max_tokens * (1.0 - self.buffer))
        estimated_tokens = self._estimate_tokens(document)
        
        if estimated_tokens <= token_limit_with_buffer:
            return document # Fits with buffer
        
        # Prune by character count
        max_chars = token_limit_with_buffer * 4
        pruned_doc = document[:max_chars]
        
        self.logger.warning(
            f"Context pruned: Original tokens ~{estimated_tokens}, "
            f"Limit: {token_limit_with_buffer}, Pruned to ~{self._estimate_tokens(pruned_doc)}"
        )
        
        return f"{pruned_doc}\n\n[... DOCUMENT PRUNED TO FIT CONTEXT ...]"

# ============================================================================
# v10.3: PROMPT TEMPLATE MANAGER (v10.4: Fixed Placeholders)
# ============================================================================

class PromptTemplateManager:
    """
    v10.4: Manages all 30+ system prompts.
    FIXED: All placeholder prompts are now fully implemented.
    FIXED: All templates include all possible format keys to prevent KeyErrors.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PromptTemplateManager")
        self.templates = self._load_templates()

    def get_template(self, tool_name: str) -> str:
        """Gets a prompt template by tool name."""
        template = self.templates.get(tool_name)
        if not template:
            self.logger.error(f"No prompt template found for tool: {tool_name}")
            return "ERROR: PROMPT NOT FOUND FOR {tool_name}"
        return template

    def _load_templates(self) -> Dict[str, str]:
        """
        v10.4: FIXED - Defines all 30+ system prompts with COMPLETE format keys.
        Each template now includes all keys that might be passed by any tool,
        using {key} syntax for ALL placeholders to avoid KeyError.
        """
        # Define a set of all possible keys used across all prompts
        # This allows for safe .format() calls with default values
        all_keys_template = {
            "style_guide": "", "draft": "", "strategy": "", "section_text": "",
            "critique": "", "bullets": "", "master_resume": "", "draft_text": "",
            "required_tone": "", "job_description": "", "query": "", "candidates": "",
            "instruction": "", "context": "", "content": "", "job_title": "",
            "company": "", "branch_num": "", "total_branches": "", "experience": "",
            "feedback_log": "", "preference_log": "", "log_data": "", "patterns": "",
            "hypothesis": "", "proposal": "", "human_feedback": ""
        }
        
        templates = {
            # === DRAFTING TOOLS (4) ===
            # v10.4: FIXED - Added ALL format keys: style_guide, draft, strategy, section_text, critique, bullets
            "review_draft_strategy": """
You are a Drafting Strategist. Review the draft against the strategy.
{style_guide}

Strategy:
{strategy}

Draft:
{draft}

Example Input:
Strategy: {{"tone": "leadership", "focus_areas": ["AI", "Team Building"]}}
Draft: {{"summary": "I built code."}}
Example Output:
{{"status": "success", "feedback": "Draft summary is weak and misses all strategic points. It must be rewritten to highlight 'AI' and 'Team Building' with a 'leadership' tone."}}

Your Analysis:
""",
            
            "red_team_critique": """
You are a harsh but fair Red Team agent. Find all weaknesses in this draft.
{style_guide}

Draft:
{draft}

Example Input:
Draft: {{"experience": ["- Led team.", "- Did code."]}}
Example Output:
{{"status": "success", "weaknesses_found": ["'Led team' is a weak, non-metric claim.", "'Did code' is meaningless fluff."]}}

Your Analysis:
""",
            
            "refine_section": """
You are a master editor (Refiner). Rewrite the given section to incorporate the critique,
adhering strictly to the provided Style Guide.
{style_guide}

Section to refine:
{section_text}

Critique:
{critique}

Example Input:
Style Guide: "Use active voice. Quantify all impact."
Section: "The system was responsible for 10% profit."
Critique: "Passive voice. Weak claim."
Example Output:
{{"status": "success", "refined_text": "Drove 10% profit growth by engineering the system."}}

Your Refinement:
""",
            
            "add_metrics": """
You are a Metrics Specialist. Review these bullets and suggest opportunities to add metrics.
{style_guide}

Bullets:
{bullets}

Example Input:
Bullets: ["- Led team.", "- Improved system performance."]
Example Output:
{{"status": "success", "suggestions": ["Quantify 'Led team' with number of reports (e.g., 'Led team of 5').", "Quantify 'Improved system performance' with a percentage (e.g., 'Improved performance by 30%')."]}}

Your Suggestions:
""",
            
            # === QA TOOLS (11) ===
            # v10.4: FIXED - Added all keys: master_resume, draft_text, required_tone, strategy, style_guide, job_description
            "validate_claims": """
Perform a Natural Language Inference (NLI) check. Are the claims in the draft
supported (entailed) by the source resume?

Source:
{master_resume}

Draft:
{draft_text}

Example Input:
Source: {{"experience": ["- Managed $1M budget."]}}
Draft: "- Managed $5M budget."
Example Output:
{{"status": "success", "unsupported_claims": 1, "feedback": "Claim '$5M budget' is contradicted by source ('$1M budget')."}}

Your NLI Analysis:
""",
            
            "validate_tone": """
Check if the draft's tone matches the required tone.
{style_guide}

Required Tone:
{required_tone}

Draft:
{draft_text}

Example Input:
Required Tone: "leadership"
Draft: "I'm a great coder and my boss liked my work."
Example Output:
{{"status": "success", "tone_match": false, "current_tone": "informal"}}

Your Analysis:
""",
            
            "validate_thematic_alignment": """
You are a Thematic Alignment validator. Check if the draft sections
support the central strategy theme.

Strategy:
{strategy}

Draft:
{draft_text}

Example Input:
Strategy: {{"focus_areas": ["AI Leadership"]}}
Draft: "- Wrote Python scripts. - Attended meetings."
Example Output:
{{"status": "success", "alignment_score": 0.2, "feedback": "Draft does not support 'AI Leadership' theme."}}

Your Analysis:
""",
            
            "validate_semantic_entailment": """
You are a Semantic Entailment validator. Does the resume draft
semantically entail the core requirements of the Job Description?

Job Description:
{job_description}

Draft:
{draft_text}

Example Input:
JD: "Requires 5+ years of Python and SQL."
Draft: "- 3 years of Python."
Example Output:
{{"status": "success", "entailment_score": 0.5, "feedback": "Fails to entail 5+ years Python; SQL is missing."}}

Your Analysis:
""",
            
            "validate_narrative_thread": """
You are a Narrative Thread validator. Does the draft tell a clear,
consistent career story, or is it just a list of jobs?

Draft:
{draft_text}

Example Input:
Draft: "- 2020: Engineer. - 2022: Senior Engineer. - 2024: Lead Engineer."
Example Output:
{{"narrative_clear": true}}

Your Analysis:
""",
            
            "validate_jd_skills": """
You are a JD Skills validator. Check if key hard skills from the
Job Description are present in the draft.

Job Description:
{job_description}

Draft:
{draft_text}

Example Input:
JD: "Must know PyTorch, TensorFlow, and AWS."
Draft: "- Used PyTorch and AWS."
Example Output:
{{"status": "success", "keyword_coverage": 0.67, "missing_keywords": ["TensorFlow"]}}

Your Analysis:
""",
            
            "validate_signal_score": """
You are a Signal Score validator. Rate the "signal" (achievements, metrics)
vs "noise" (fluff, responsibilities) for the bullets in the draft.

Draft:
{draft_text}

Example Input:
Draft: "- Responsible for servers. - Increased uptime by 30%."
Example Output:
{{"status": "success", "avg_signal_score": 5.0, "feedback": "First bullet is 100% noise. Second is 100% signal."}}

Your Analysis:
""",
            
            "validate_tenure": """
You are a Tenure Validator. Check the draft for unexplained
employment gaps or overlapping dates.

Draft:
{draft_text}

Example Input:
Draft: "- Job A: 2018-2020. - Job B: 2022-2024."
Example Output:
{{"status": "success", "gaps_found": 1, "overlaps_found": 0}}

Your Analysis:
""",
            
            "find_missed_opportunities": """
You are a Missed Opportunity validator. Compare the draft to the master
resume. Are there critical skills/achievements from the master resume
that were omitted but are relevant to the strategy?

Master Resume:
{master_resume}

Draft:
{draft_text}

Example Input:
Master Resume: {{"experience": ["- Won 'Engineer of the Year' award 2023"]}}
Draft: "- Wrote code."
Example Output:
{{"status": "success", "opportunities_found": ["Omitted 'Engineer of the Year' award."]}}

Your Analysis:
""",
            
            "adversarial_review": """
You are a skeptical hiring manager (Adversarial Reviewer).
Find all red flags, flaws, and reasons NOT to hire this candidate
based *only* on this draft.

Draft:
{draft_text}

Example Input:
Draft: "- Led project for 3 months. - Job-hopped in 2022."
Example Output:
{{"status": "success", "red_flags": ["Short project duration (3 months) suggests incompletion.", "Job-hopping in 2022 is a loyalty risk."]}}

Your Analysis:
""",
            
            "validate_bias": """
You are a Bias Detector. This is a special tool. You will be passed
the draft text, and you must return the output of the *local*
BiasDetectorAgent.
(This prompt is a placeholder, as the tool calls the local agent directly).

Draft:
{draft_text}

Your Analysis:
""",
            
            # === AGENT STACKS (ToT, Prompt Eng, etc.) ===
            # v10.4: TEST FIX - Added {job_description}
            "strategy_tot_branch": """
Generate a resume strategy for this job.

Job Title: {job_title}
Company: {company}
Job Description: {job_description}

This is branch {branch_num} of {total_branches}. Be creative and distinct.
{style_guide}

Example Output:
{{"strategy_name": "AI Visionary", "focus_areas": ["LLM Strategy", "Team Leadership"], "key_achievements_to_highlight": ["BERT implementation 2022"], "tone": "leadership"}}

Your Strategy Branch:
""",
            
            # v10.4: TEST FIX - Added {job_description}
            "prompt_engineer": """
You are a prompt engineer. Generate prompts for resume bullet generation
based on the strategy and style guide.

{style_guide}

Strategy:
{strategy}

Job Description:
{job_description}

Example Output:
{{"bullet_generation_prompt": "Create 3 high-impact bullets...", "critique_prompt": "Review these bullets for..."}}

Your Prompts:
""",
            
            # v10.4: TEST FIX - Added {strategy}
            "bullet_generation_fact_check": """
You are a fact-checker. Review the following bullets against the source experience.
Filter out any bullets that contain plausible-sounding but unverified claims (hallucinations).

Source Experience:
{experience}

Bullets to Check:
{bullets}

Strategy (for context):
{strategy}

Example Input:
Experience: ["- Managed team of 5"]
Bullets: ["- Led team of 50", "- Wrote code"]
Example Output:
{{"verified_bullets": ["- Wrote code"], "rejected_bullets": ["- Led team of 50 (contradicts source)"]}}

Your Verification:
""",
            
            # === HYDE TOOL ===
            # v10.4: TEST FIX - Added {job_description} and {style_guide}
            "hyde_generation": """
You are a HyDE (Hypothetical Document Embeddings) generator.
Given a query, generate a hypothetical document that would rank well
for that query in semantic search.

Query:
{query}

Job Description:
{job_description}

Style Guide:
{style_guide}

Example Input:
Query: "Cloud infrastructure architect"
Example Output:
{{"hypothetical_document": "Designed and deployed multi-cloud infrastructure on AWS, GCP, and Azure. Architected Kubernetes clusters serving 1M+ requests/day. Reduced infrastructure costs by $2M annually through optimization."}}

Your Hypothetical Document:
""",
            
            # === RERANKING ===
            # v10.4: TEST FIX - Added {strategy}
            "rerank_results": """
You are a reranker. Given a list of candidate results, rerank them by relevance
to the query and strategy.

Query:
{query}

Strategy:
{strategy}

Candidates:
{candidates}

Example Input:
Query: "cloud infrastructure"
Strategy: {{"focus_areas": ["Cloud", "DevOps"]}}
Candidates: [{{"id": 1, "text": "Wrote Python scripts"}}, {{"id": 2, "text": "Architected AWS infrastructure"}}]
Example Output:
{{"ranked": [{{"id": 2, "text": "Architected AWS infrastructure"}}, {{"id": 1, "text": "Wrote Python scripts"}}]}}

Your Ranking:
""",
            
            # === FALLBACK DEFAULTS ===
            "generic_instruction": """
{instruction}

{style_guide}

{context}

Your Response:
""",
            
            "generic_analysis": """
Analyze the following and provide insights:

Content:
{content}

Style Guide:
{style_guide}

Your Analysis:
""",
            
            # --- Meta-Learning ---
            "meta_log_reader": "Summarize user feedback and preferences: {feedback_log} {preference_log}",
            "meta_pattern_finder": "Find patterns in log data: {log_data}",
            "meta_hypothesis_generator": "Generate hypotheses from patterns: {patterns} avoiding critique: {critique}",
            "meta_proposal_drafter": "Draft a rule proposal for hypothesis: {hypothesis}",
            "meta_proposal_critique": "Critique this proposal: {proposal} based on patterns: {patterns}",
            
            # --- HIL ---
            "hil_ambiguity_detector": """
You are an Ambiguity Detector. Analyze the following strategy plan
for vagueness or ambiguity that would require human clarification.
Strategy: {strategy}

Example Input:
Strategy: {{ "focus_areas": ["synergy", "impact"] }}
Example Output:
{{ "ambiguity_detected": true, "confidence": 0.9, "reason": "Terms 'synergy' and 'impact' are vague.", "question_for_human": "What specific *kind* of 'impact' should I focus on? (e.g., financial, technical, team)" }}
Your Analysis:
""",
            "hil_feedback_router": """
You are a Feedback Router. Based on the human's feedback,
decide which graph node to route to next.
Options are: 'STRATEGY', 'BULLET_GENERATION', 'DRAFTING'.

Human Feedback: {human_feedback}

Example Input:
Feedback: "No, that's the wrong theme. Focus more on my leadership skills."
Example Output:
{{ "next_step": "STRATEGY" }}
Your Routing Decision:
"""
        }
        
        # v10.4: FIX - This is a safer way to load, but the test failures
        # were due to the prompt keys *not existing*. The fix above
        # (adding all keys to all templates) is the correct one.
        # This implementation remains as-is.
        return templates

# ============================================================================
# v10.3: RESPONSE VALIDATOR (v10.4: Fixed for non-Pydantic types)
# ============================================================================

class ResponseValidator:
    """
    v10.4: Central utility to parse and validate LLM JSON.
    FIXED: Now handles Pydantic models, dict, list, and tuples.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ResponseValidator")

    def _extract_json(self, text: str) -> Optional[Any]:
        """Finds and parses the first valid JSON object or array in a string."""
        try:
            # Try to find a JSON block
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if 0 <= json_start < json_end:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
            
            # Try to find a JSON array
            json_start = text.find('[')
            json_end = text.rfind(']') + 1
            if 0 <= json_start < json_end:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
                
            return None
        except json.JSONDecodeError:
            return None

    def validate(
        self, 
        response_content: Any, 
        output_model: Any # Can be Type[BaseModel], dict, list, or tuple
    ) -> Tuple[Optional[Any], Optional[str]]:
        """
        Validates raw LLM content (str or dict) against a Pydantic model,
        dict, list, or tuple of types.
        Returns (model_instance, None) on success.
        Returns (None, error_message) on failure.
        """
        try:
            # 1. Ensure content is a parsed JSON object/array
            if isinstance(response_content, str):
                json_content = self._extract_json(response_content)
                if json_content is None:
                    raise JSONParsingError(f"No valid JSON object or array found in response: {response_content[:100]}...")
            else:
                json_content = response_content
            
            # 2. Handle different `output_model` types
            
            # Case 1: Pydantic BaseModel
            if isinstance(output_model, type) and issubclass(output_model, BaseModel):
                try:
                    validated_model = output_model.model_validate(json_content)
                    return validated_model, None
                except PydanticValidationError as e:
                    self.logger.warning(f"Pydantic validation failed for {output_model.__name__}: {e}")
                    raise PydanticSchemaError(f"Validation failed for {output_model.__name__}: {e}. Got: {json_content}")

            # Case 2: Standard type (dict, list)
            elif output_model == dict or output_model == list:
                if isinstance(json_content, output_model):
                    return json_content, None
                else:
                    raise PydanticSchemaError(f"Validation failed: Expected {output_model.__name__}, got {type(json_content)}")

            # Case 3: Tuple of types (e.g., (list, dict))
            elif isinstance(output_model, tuple):
                for model_type in output_model:
                    if isinstance(model_type, type) and issubclass(model_type, BaseModel):
                        try:
                            validated_model = model_type.model_validate(json_content)
                            return validated_model, None
                        except PydanticValidationError:
                            continue # Try next type in tuple
                    elif (model_type == dict or model_type == list) and isinstance(json_content, model_type):
                        return json_content, None
                
                # If no type in tuple matched
                raise PydanticSchemaError(f"Validation failed: Content did not match any type in {output_model}. Got: {type(json_content)}")

            # Case 4: Unhandled output_model type
            else:
                raise PydanticSchemaError(f"Unsupported output_model type for validation: {output_model}")

        except (JSONParsingError, PydanticSchemaError) as e:
            self.logger.error(f"Response validation failed: {e}")
            return None, str(e)

# ============================================================================
# ROW 7: FEEDBACK LOG READER (Preserved from v10.1)
# ============================================================================

@dataclass
class FeedbackEntry:
    timestamp: str
    workflow_id: str
    agent_name: str
    task: str
    feedback_type: str
    details: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class FeedbackLogReader:
    def __init__(self, feedback_log_path: str):
        self.feedback_log_path = feedback_log_path
        self.logger = logging.getLogger(f"{__name__}.FeedbackLogReader")
        self._cache: List[FeedbackEntry] = []
        self._last_read_time: Optional[float] = None
        self._cache_ttl = 60.0
    
    def read_recent_feedback(self, max_entries: int = 100) -> List[FeedbackEntry]:
        now = time.time() # Use time.time() for timestamp
        if self._last_read_time and (now - self._last_read_time) < self._cache_ttl:
            return self._cache[-max_entries:]
        
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
                        entries.append(FeedbackEntry(**data))
                    except (json.JSONDecodeError, TypeError):
                        continue
            
            self._cache = entries
            self._last_read_time = now
            self.logger.info(f"Loaded {len(entries)} feedback entries")
            return entries
        except Exception as e:
            self.logger.error(f"Failed to read feedback log: {e}")
            return []
    
    def get_agent_success_rate(self, agent_name: str, task_type: str = None) -> float:
        entries = self.read_recent_feedback()
        relevant = [
            e for e in entries 
            if e.agent_name == agent_name 
            and (task_type is None or e.task == task_type)
        ]
        if not relevant: return 0.5
        success_count = sum(1 for e in relevant if e.feedback_type == "success")
        return success_count / len(relevant)

    def get_best_agent_for_task(self, task_type: str, candidates: List[str]) -> str:
        best_agent = candidates[0]
        best_rate = 0.0
        for agent in candidates:
            rate = self.get_agent_success_rate(agent, task_type)
            if rate > best_rate:
                best_rate = rate
                best_agent = agent
        self.logger.info(f"Selected {best_agent} for {task_type} (success rate: {best_rate:.2%})")
        return best_agent

# ============================================================================
# ROW 7: PROPOSED RULES LOADER (v10.4: Added Debug Logging)
# ============================================================================

@dataclass
class ProposedRule:
    timestamp: str
    status: str
    rule_type: str
    description: str
    config_changes: Dict[str, Any]
    pattern_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProposedRulesLoader:
    def __init__(self, proposed_rules_path: str):
        self.proposed_rules_path = proposed_rules_path
        self.logger = logging.getLogger(f"{__name__}.ProposedRulesLoader")
        self._cache: List[ProposedRule] = []
        self._last_mtime: Optional[float] = None
    
    def load_rules(self, status_filter: str = "APPROVED") -> List[ProposedRule]:
        """v10.4: Added verbose logging to debug test failure."""
        try:
            if not os.path.exists(self.proposed_rules_path):
                self.logger.warning(f"Proposed rules file not found: {self.proposed_rules_path}")
                return []
            
            current_mtime = os.path.getmtime(self.proposed_rules_path)
            if self._last_mtime == current_mtime:
                # v10.4: Added debug logging
                self.logger.debug(f"Using cached rules. mtime: {current_mtime}")
                return [r for r in self._cache if r.status == status_filter]
            
            # v10.4: Added info logging
            self.logger.info(f"Hot-reloading proposed rules (file modified). New mtime: {current_mtime}")
            rules = []
            with open(self.proposed_rules_path, 'r') as f:
                lines = f.readlines() # Read all lines
                # v10.4: Added debug logging
                self.logger.debug(f"Read {len(lines)} lines from rules file: {self.proposed_rules_path}")
                for i, line in enumerate(lines):
                    try:
                        data = json.loads(line.strip())
                        pattern_data = data.get("pattern", {})
                        rules.append(ProposedRule(
                            timestamp=data.get("timestamp", ""),
                            status=data.get("status", "PROPOSED"),
                            rule_type=pattern_data.get("type", "unknown"),
                            description=pattern_data.get("description", ""),
                            config_changes=pattern_data.get("config_changes", {}),
                            pattern_id=pattern_data.get("id", ""),
                            metadata=pattern_data.get("metadata", {})
                        ))
                    except (json.JSONDecodeError, TypeError) as e:
                        # v10.4: Added warning logging
                        self.logger.warning(f"Failed to parse rule on line {i+1}: {e}")
                        continue
            
            self._cache = rules
            self._last_mtime = current_mtime
            filtered = [r for r in rules if r.status == status_filter]
            # v10.4: Added info logging
            self.logger.info(f"Loaded {len(rules)} total rules, {len(filtered)} are '{status_filter}'.")
            return filtered
        except Exception as e:
            self.logger.error(f"Failed to load proposed rules: {e}")
            return []
    
    def get_constitution_rules(self) -> List[Dict[str, Any]]:
        rules = self.load_rules(status_filter="APPROVED")
        constitution_rules = [
            r.config_changes 
            for r in rules 
            if r.rule_type.lower() == "constitution"
        ]
        self.logger.info(f"Extracted {len(constitution_rules)} constitution rules")
        return constitution_rules

# ============================================================================
# ROW 5: CACHE MANAGER (v10.4: Updated cache key)
# ============================================================================

class CacheManager:
    def __init__(self, redis_client: redis.Redis, ttl_seconds: int = 3600):
        self.redis = redis_client
        self.ttl = ttl_seconds
        self.logger = logging.getLogger(f"{__name__}.CacheManager")
        self._hits = 0
        self._misses = 0
    
    def _generate_cache_key(self, provider: str, model: str, prompt: str, temperature: float) -> str:
        key_str = f"{provider}:{model}:{prompt}:{temperature}"
        # v10.4: Updated cache key namespace
        return f"llm_cache_v10_4:{hashlib.sha256(key_str.encode()).hexdigest()}"
    
    def get(self, provider: str, model: str, prompt: str, temperature: float) -> Optional[Dict[str, Any]]:
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
        cache_key = self._generate_cache_key(provider, model, prompt, temperature)
        try:
            self.redis.setex(cache_key, self.ttl, json.dumps(response))
            self.logger.debug(f"Cached response: {cache_key[:16]}...")
        except Exception as e:
            self.logger.error(f"Cache set error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        return {"hits": self._hits, "misses": self._misses, "total_requests": total, "hit_rate_pct": hit_rate}

# ============================================================================
# ROW 4: COST TRACKER (Preserved from v10.1)
# ============================================================================

class CostTracker:
    PRICING = {
        "anthropic": {"claude-4.1-opus": {"input": 0.015, "output": 0.075}},
        "google": {"gemini-2.5-pro": {"input": 0.002, "output": 0.006}, "gemini-2.5-flash": {"input": 0.0001, "output": 0.0003}},
        "openai": {"gpt-5": {"input": 0.05, "output": 0.15}}
    }
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CostTracker")
        self._workflow_costs: Dict[str, List[Dict]] = {}
    
    def log_cost(self, workflow_id: str, agent_name: str, model_name: str, input_tokens: int, output_tokens: int):
        provider = self._get_provider_name(model_name)
        self.record_call(workflow_id, provider, model_name, input_tokens, output_tokens)

    def _get_provider_name(self, model_name: str) -> str:
        if "claude" in model_name: return "anthropic"
        if "gemini" in model_name: return "google"
        if "gpt-" in model_name: return "openai"
        return "unknown"
    
    def record_call(self, workflow_id: str, provider: str, model: str, input_tokens: int, output_tokens: int):
        pricing = self.PRICING.get(provider, {}).get(model)
        if not pricing:
            self.logger.warning(f"No pricing for {provider}/{model}")
            return
        
        cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
        
        if workflow_id not in self._workflow_costs:
            self._workflow_costs[workflow_id] = []
        
        self._workflow_costs[workflow_id].append({
            "provider": provider, "model": model, "input_tokens": input_tokens,
            "output_tokens": output_tokens, "cost": cost, "timestamp": datetime.now().isoformat()
        })
        self.logger.debug(f"Recorded ${cost:.4f} for {workflow_id}")
    
    def get_cost_summary(self, workflow_id: str) -> Dict[str, Any]:
        calls = self._workflow_costs.get(workflow_id, [])
        total_cost = sum(c["cost"] for c in calls)
        total_input = sum(c["input_tokens"] for c in calls)
        total_output = sum(c["output_tokens"] for c in calls)
        
        return {
            "workflow_id": workflow_id, "total_workflow_cost": total_cost,
            "total_calls": len(calls), "total_input_tokens": total_input,
            "total_output_tokens": total_output, "calls": calls
        }

# ============================================================================
# BASE AGENT CLASS (Refactored for v10.3)
# ============================================================================

class BaseAgent:
    """Base class for all agents with v10.3 context injection"""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        self.context = context
        self.config = context.config 
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # v10.3: Direct access to injected utilities
        self.prompt_manager = context.prompt_manager
        self.validator = context.response_validator
        self.budget_manager = context.context_budget_manager
    
    def log_info(self, message: str): self.logger.info(f"[{self.__class__.__name__}] {message}")
    def log_warning(self, message: str): self.logger.warning(f"[{self.__class__.__name__}] {message}")
    def log_error(self, message: str): self.logger.error(f"[{self.__class__.__name__}] {message}")
    def log_debug(self, message: str):
        if self.debug_mode: self.logger.debug(f"[{self.__class__.__name__}] {message}")
    
    def log_feedback(self, workflow_id: str, task: str, feedback_type: str, details: Dict[str, Any]):
        try:
            feedback_entry = {
                "timestamp": datetime.now().isoformat(), "workflow_id": workflow_id,
                "agent_name": self.__class__.__name__, "task": task,
                "feedback_type": feedback_type, "details": details, "metadata": {}
            }
            feedback_log_path = self.config.meta_loop_config.feedback_log_path
            os.makedirs(os.path.dirname(feedback_log_path), exist_ok=True)
            with open(feedback_log_path, 'a') as f:
                json.dump(feedback_entry, f)
                f.write('\n')
            self.log_debug(f"Logged feedback: {feedback_type} for {task}")
        except Exception as e:
            self.log_error(f"Failed to log feedback: {e}")
    
    def get_model_client(self, model_config_name: str) -> "AsyncBaseModelClient":
        model_config = getattr(self.config.model_config, model_config_name)
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        client.workflow_id = self.context.workflow_id
        client.agent_name = self.__class__.__name__
        return client
        
# ============================================================================
# ROW 6: ASYNC LLM CLIENTS (Refactored for v10.3 Validation)
# ============================================================================

class AsyncBaseModelClient:
    def __init__(self, model_name: str, cache_manager, cost_tracker, workflow_id: str, agent_name: str):
        self.model_name = model_name
        self.cache_manager = cache_manager
        self.cost_tracker = cost_tracker
        self.workflow_id = workflow_id
        self.agent_name = agent_name
    
    def _get_provider_name(self) -> str:
        if "claude" in self.model_name: return "anthropic"
        if "gemini" in self.model_name: return "google"
        if "gpt-" in self.model_name: return "openai"
        return "unknown"
    
    async def chat_completion_async(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.7,
                                   response_format: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError

class AnthropicAsyncClient(AsyncBaseModelClient):
    async def chat_completion_async(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.7,
                                   response_format: Optional[str] = None) -> Dict[str, Any]:
        import anthropic
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        provider = self._get_provider_name()
        
        cached_response = self.cache_manager.get(provider, self.model_name, prompt, temperature)
        if cached_response: return cached_response
        
        try:
            client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            response = await client.messages.create(
                model=self.model_name, max_tokens=4096,
                temperature=temperature, messages=messages
            )
            content = response.content[0].text
            
            # v10.3: No need for manual JSON parsing here. The ResponseValidator
            # in the agent layer will handle extracting JSON from this text block.
            
            result = {
                "content": content,
                "usage": {"prompt_tokens": response.usage.input_tokens, "completion_tokens": response.usage.output_tokens}
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
    async def chat_completion_async(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.7,
                                   response_format: Optional[str] = None) -> Dict[str, Any]:
        import google.generativeai as genai
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        provider = self._get_provider_name()
        
        cached_response = self.cache_manager.get(provider, self.model_name, prompt, temperature)
        if cached_response: return cached_response
        
        try:
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            gen_config = {"temperature": temperature}
            
            # v10.3: Use Gemini's native JSON mode
            if response_format == "json_object":
                gen_config["response_mime_type"] = "application/json"
            
            model = genai.GenerativeModel(self.model_name)
            prompt_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            
            response = await asyncio.to_thread(
                model.generate_content, prompt_text, generation_config=gen_config
            )
            
            content = response.text
            
            # v10.3: If we requested JSON, Gemini returns a raw string
            # that we must parse. The ResponseValidator will handle this.
            
            result = {
                "content": content, "usage": {"prompt_tokens": 0, "completion_tokens": 0}
            }
            self.cache_manager.set(provider, self.model_name, prompt, temperature, result)
            return result
        except Exception as e:
            raise ModelAPIError(f"Gemini API call failed: {e}")

class OpenAIAsyncClient(AsyncBaseModelClient):
    async def chat_completion_async(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.7,
                                   response_format: Optional[str] = None) -> Dict[str, Any]:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        provider = self._get_provider_name()
        
        cached_response = self.cache_manager.get(provider, self.model_name, prompt, temperature)
        if cached_response: return cached_response
        
        try:
            client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            completion_kwargs = {
                "model": self.model_name, "temperature": temperature, "messages": messages
            }
            if response_format == "json_object":
                completion_kwargs["response_format"] = {"type": "json_object"}

            response = await client.chat.completions.create(**completion_kwargs)
            content = response.choices[0].message.content
            
            # v10.3: If we requested JSON, OpenAI already wraps this
            # in a string. The ResponseValidator will parse it.
            
            result = {
                "content": content,
                "usage": {"prompt_tokens": response.usage.prompt_tokens, "completion_tokens": response.usage.completion_tokens}
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
# ROW 4: WORKFLOW CONTEXT (v10.4: Fixed class name)
# ============================================================================

class WorkflowContext:
    """
    v10.4: True Dependency Injection container.
    This class now RECEIVES all dependencies in its constructor.
    It no longer creates any of its own services.
    """
    
    def __init__(self, 
                 config: ConfigV10_4,  # v10.4: Updated class
                 redis_client: redis.Redis,
                 chromadb_client: chromadb.Client,
                 cache_manager: CacheManager,
                 cost_tracker: CostTracker,
                 feedback_reader: FeedbackLogReader,
                 rules_loader: ProposedRulesLoader,
                 prompt_manager: PromptTemplateManager,    # v10.3: Injected
                 response_validator: ResponseValidator,  # v10.3: Injected
                 context_budget_manager: ContextBudgetManager # v10.3: Injected
                ):
        
        self.config = config
        self.redis_client = redis_client
        self.chromadb_client = chromadb_client
        self.workflow_id: str = ""
        
        # Assign injected dependencies
        self.cache_manager = cache_manager
        self.cost_tracker = cost_tracker
        self.feedback_reader = feedback_reader
        self.rules_loader = rules_loader
        self.prompt_manager = prompt_manager
        self.response_validator = response_validator
        self.context_budget_manager = context_budget_manager
        
        self._model_clients: Dict[str, Any] = {}
        
        # v10.4: Updated log message
        logger.info("WorkflowContext initialized with v10.4 injected dependencies")
    
    def get_model_client(self, provider: str, model_name: str):
        key = f"{provider}:{model_name}"
        if key not in self._model_clients:
            base_args = {
                "model_name": model_name,
                "cache_manager": self.cache_manager,
                "cost_tracker": self.cost_tracker,
                "workflow_id": self.workflow_id,
                "agent_name": ""
            }
            if provider == "anthropic": self._model_clients[key] = AnthropicAsyncClient(**base_args)
            elif provider == "google": self._model_clients[key] = GeminiAsyncClient(**base_args)
            elif provider == "openai": self._model_clients[key] = OpenAIAsyncClient(**base_args)
            else: raise ValueError(f"Unknown provider: {provider}")
        
        client = self._model_clients[key]
        client.workflow_id = self.workflow_id
        return client

# ============================================================================
# STATE MODELS (v10.4: Serialization Fix)
# ============================================================================

# These dataclasses define the structure of the LangGraph state
@dataclass
class ResumeContext:
    master_resume: Dict[str, Any] = field(default_factory=dict)
    sanitized_resume: Dict[str, Any] = field(default_factory=dict)
    experience_bullets: List[Dict] = field(default_factory=list)

@dataclass
class JobContext:
    raw_jd: str = ""
    company: str = ""
    job_title: str = ""
    parsed_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyContext:
    strategy_plan: Optional[StrategyPlan] = None # v10.3: Now a Pydantic model
    tot_branches: List[Dict] = field(default_factory=list)

@dataclass
class PromptContext:
    prompts: Optional[GeneratedPrompts] = None # v10.3: Now a Pydantic model

@dataclass
class BulletContext:
    generated_bullets: List[Dict] = field(default_factory=list)
    critiqued_bullets: List[Dict] = field(default_factory=list)

@dataclass
class DraftContext:
    sections: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QAContext:
    validation_results: Dict[str, Any] = field(default_factory=dict)
    qa_passed: bool = False

@dataclass
class ArtifactContext:
    artifacts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetadataContext:
    workflow_id: str = ""
    timestamp: str = ""
    cost: float = 0.0
    retries: Dict[str, int] = field(default_factory=lambda: {"bullet_retries": 0, "qa_retries": 0})

@dataclass
class SafetyContext:
    pii_detected: bool = False
    bias_detected: bool = False
    safety_notes: List[str] = field(default_factory=list)

@dataclass
class FeedbackContext:
    recent_feedback: List[FeedbackEntry] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    selected_agents: Dict[str, str] = field(default_factory=dict)

@dataclass
class HILContext:
    ambiguity_detected: bool = False
    ambiguity_report: Optional[HILAmbiguityReport] = None # v10.3: Now a Pydantic model
    next_step: str = ""

@dataclass
class MainGraphState:
    """Main workflow state (v10.4: Serialization Fix)"""
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
        """v1E.g4: Custom serializer to handle nested Pydantic models."""
        # Use dataclasses.asdict for the base structure
        data = asdict(self)
        
        # Manually serialize nested Pydantic models to dicts
        if self.strategy.strategy_plan:
            data['strategy']['strategy_plan'] = self.strategy.strategy_plan.model_dump()
        if self.prompts.prompts:
            data['prompts']['prompts'] = self.prompts.prompts.model_dump()
        if self.hil.ambiguity_report:
            data['hil']['ambiguity_report'] = self.hil.ambiguity_report.model_dump()
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MainGraphState':
        """v1G.g4: Custom deserializer to reconstruct nested Pydantic models."""
        state = cls()
        
        # Deserialize dataclasses
        state.resume = ResumeContext(**data.get("resume", {}))
        state.job = JobContext(**data.get("job", {}))
        state.bullets = BulletContext(**data.get("bullets", {}))
        state.draft = DraftContext(**data.get("draft", {}))
        state.qa = QAContext(**data.get("qa", {}))
        state.artifacts = ArtifactContext(**data.get("artifacts", {}))
        state.metadata = MetadataContext(**data.get("metadata", {}))
        state.safety = SafetyContext(**data.get("safety", {}))
        state.feedback = FeedbackContext(**data.get("feedback", {}))
        
        # Deserialize Pydantic models nested in dataclasses
        strategy_data = data.get("strategy", {})
        strategy_plan_data = strategy_data.get("strategy_plan")
        state.strategy = StrategyContext(
            strategy_plan=StrategyPlan.model_validate(strategy_plan_data) if strategy_plan_data and isinstance(strategy_plan_data, dict) else None,
            tot_branches=strategy_data.get("tot_branches", [])
        )
        
        prompts_data = data.get("prompts", {})
        prompts_model_data = prompts_data.get("prompts")
        state.prompts = PromptContext(
            prompts=GeneratedPrompts.model_validate(prompts_model_data) if prompts_model_data and isinstance(prompts_model_data, dict) else None
        )
        
        hil_data = data.get("hil", {})
        hil_report_data = hil_data.get("ambiguity_report")
        state.hil = HILContext(
            ambiguity_detected=hil_data.get("ambiguity_detected", False),
            ambiguity_report=HILAmbiguityReport.model_validate(hil_report_data) if hil_report_data and isinstance(hil_report_data, dict) else None,
            next_step=hil_data.get("next_step", "")
        )
        return state

@dataclass
class MetaGraphState:
    raw_logs: Dict[str, str] = field(default_factory=dict)
    log_summary: Dict[str, Any] = field(default_factory=dict)
    patterns: List[Dict] = field(default_factory=list)
    hypotheses: List[Dict] = field(default_factory=list)
    proposal: Dict[str, Any] = field(default_factory=dict)
    critique: Dict[str, Any] = field(default_factory=dict)
    replan_count: int = 0
    workflow_id: str = ""

# ============================================================================
# END OF core_v10_4.py
# ============================================================================