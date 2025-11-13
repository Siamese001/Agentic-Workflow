"""Service-layer helpers for the v10.7 runtime."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Tuple

from chromadb.utils import embedding_functions
from pydantic import BaseModel, ValidationError as PydanticValidationError

from telemetry_v10_7 import log_event

from .config import ConfigV10_7
from .constants import legacy_model_alias
from .exceptions import JSONParsingError, PydanticSchemaError
from .models import GeneratedPrompts, StrategyPlan

if TYPE_CHECKING:  # pragma: no cover - typing helpers
    from .clients import AsyncBaseModelClient
    from redis import Redis as RedisType
    from chromadb import Client as ChromaClientType
else:  # pragma: no cover - fallback aliases for runtime
    AsyncBaseModelClient = Any
    RedisType = Any
    ChromaClientType = Any

logger = logging.getLogger("core_v10_7")


class ContextBudgetManager:
    """
    v10.7 (Fix #14): Manages context window limits using agentic pruning.
    """
    def __init__(self, 
                 config: ConfigV10_7,
                 model_client_getter: Callable[..., 'AsyncBaseModelClient']
                ):
        self.default_limit = config.performance_config.default_token_limit
        self.buffer = 0.2 # 20% buffer
        self.logger = logging.getLogger(f"{__name__}.ContextBudgetManager")
        self.config = config
        self.get_model_client = model_client_getter
    
    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4
    
    async def _prune_agentic(self, document: str, max_tokens: int) -> str:
        """v10.7 (Fix #14): Uses an LLM to prune text."""
        self.logger.warning(f"Context > {max_tokens} tokens. Pruning agentically...")
        try:
            summarizer_config = self.config.model_config.summarizer_model
            client = self.get_model_client(
                summarizer_config.provider,
                legacy_model_alias(summarizer_config.model_name)
            )
            # v10.7 NOTE: We cannot use PromptTemplateManager here as it
            # creates a circular dependency. We define the prompt inline.
            prompt = f"""
            MODE: ANALYTICAL
            TASK: You are a context pruner. Summarize the following document
            into its essential points. The output *must* be less than {max_tokens * 3} characters.
            DOCUMENT:
            {document}

            SUMMARY:
            """

            response = await client.chat_completion_async(
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.model_config.summarizer_model.temperature
            )
            pruned_doc = response.get("content")

            if not isinstance(pruned_doc, str) or not pruned_doc.strip():
                raise TypeError("Summarizer returned empty or non-string content")

            pruned_tokens = self._estimate_tokens(pruned_doc)

            # Final fallback truncation if the summarizer still overshoots the budget
            if pruned_tokens > max_tokens:
                self.logger.warning(
                    "Agentic pruning output still above budget (%s > %s tokens). Applying truncation fallback.",
                    pruned_tokens,
                    max_tokens,
                )
                return self._prune_truncate(pruned_doc, max_tokens, label="AGENTIC_TRUNCATION")

            return f"{pruned_doc}\n\n[... DOCUMENT PRUNED (AGENTIC) ...]"

        except Exception as e:
            self.logger.error("Agentic pruning failed: %s. Falling back to truncation.", e, exc_info=True)
            return self._prune_truncate(document, max_tokens, label="AGENTIC_FAILURE")

    def _prune_truncate(self, document: str, max_tokens: int, *, label: str = "TRUNCATION") -> str:
        """v10.7: Simple truncation fallback."""
        max_chars = max_tokens * 4
        pruned_doc = document[:max_chars]
        self.logger.warning(f"Context truncated to {max_tokens} tokens.")
        return f"{pruned_doc}\n\n[... DOCUMENT PRUNED ({label}) ...]"
    
    async def prune(self, document: str, max_tokens: Optional[int] = None) -> str:
        if max_tokens is None:
            max_tokens = self.default_limit

        if document is None:
            document = ""
        elif not isinstance(document, str):
            document = str(document)

        token_limit_with_buffer = int(max_tokens * (1.0 - self.buffer))
        estimated_tokens = self._estimate_tokens(document)
        
        if estimated_tokens <= token_limit_with_buffer:
            return document 
        
        # v10.7 (Fix #14): Use agentic pruning
        return await self._prune_agentic(document, token_limit_with_buffer)


class MetricsCollector:
    """v10.7: In-memory collector for agent/tool observability."""
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.metrics: List[Dict[str, Any]] = []
        self.log_path = "./logs/metrics_v10_7.jsonl"
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            self.logger.info(f"Metrics logging to {self.log_path}")
        except OSError as e:
            self.logger.error(f"Could not create log directory for metrics: {e}")

    def record(self, agent_name: str, task_name: str, duration_ms: float, success: bool, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        metric = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "task_name": task_name,
            "duration_ms": duration_ms,
            "success": success,
            "error": error,
            "metadata": metadata or {}
        }
        self.metrics.append(metric)
        try:
            with open(self.log_path, 'a') as f:
                json.dump(metric, f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write metric to log: {e}")

    def get_summary(self) -> List[Dict[str, Any]]:
        return self.metrics

    def get_average_latency(self, agent_name: str, task_name: str) -> Optional[float]:
        """v10.7 (Fix #15): Gets average latency for a specific task."""
        latencies = [
            m['duration_ms'] for m in self.metrics
            if m['agent_name'] == agent_name and m['task_name'] == task_name and m['success']
        ]
        if not latencies:
            return None
        return sum(latencies) / len(latencies)


def track_metrics(task_name: str):
    """
    v10.7: Decorator for agent/tool/model run methods.

    Updated to support BOTH:
      - Agents: self.context.metrics_collector
      - Model clients: self.metrics
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(self: Any, *args, **kwargs) -> Any:
                collector = None

                # Prefer agent-style: self.context.metrics_collector
                if hasattr(self, "context") and getattr(self.context, "metrics_collector", None):
                    collector = self.context.metrics_collector
                # Fallback: client-style: self.metrics
                elif hasattr(self, "metrics"):
                    collector = self.metrics

                if collector is None:
                    logger.warning(
                        f"@track_metrics on {func.__name__} could not find a MetricsCollector "
                        f"(looked for self.context.metrics_collector or self.metrics)"
                    )
                    return await func(self, *args, **kwargs)

                agent_name = self.__class__.__name__
                start_time = time.perf_counter()

                try:
                    result = await func(self, *args, **kwargs)
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    collector.record(
                        agent_name,
                        task_name,
                        duration_ms,
                        success=True,
                        error=None,
                        metadata=dict(kwargs),
                    )
                    return result
                except Exception as e:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    collector.record(
                        agent_name,
                        task_name,
                        duration_ms,
                        success=False,
                        error=str(e),
                        metadata=dict(kwargs),
                    )
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(self: Any, *args, **kwargs) -> Any:
                collector = None

                if hasattr(self, "context") and getattr(self.context, "metrics_collector", None):
                    collector = self.context.metrics_collector
                elif hasattr(self, "metrics"):
                    collector = self.metrics

                if collector is None:
                    logger.warning(
                        f"@track_metrics on {func.__name__} could not find a MetricsCollector "
                        f"(looked for self.context.metrics_collector or self.metrics)"
                    )
                    return func(self, *args, **kwargs)

                agent_name = self.__class__.__name__
                start_time = time.perf_counter()

                try:
                    result = func(self, *args, **kwargs)
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    collector.record(
                        agent_name,
                        task_name,
                        duration_ms,
                        success=True,
                        error=None,
                        metadata=dict(kwargs),
                    )
                    return result
                except Exception as e:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    collector.record(
                        agent_name,
                        task_name,
                        duration_ms,
                        success=False,
                        error=str(e),
                        metadata=dict(kwargs),
                    )
                    raise
            return sync_wrapper
    return decorator


class SemanticValidator:
    """v10.7: Local, deterministic validation service."""
    def __init__(self, metrics_collector: MetricsCollector):
        self.logger = logging.getLogger(f"{__name__}.SemanticValidator")
        self.metrics = metrics_collector

    def check_word_count(self, text: str, min_words: int, max_words: int, llm_reported_count: Optional[int] = None, workflow_id: str = "") -> Tuple[bool, str]:
        deterministic_count = len(text.split())
        
        if llm_reported_count is not None:
            discrepancy = abs(deterministic_count - llm_reported_count)
            if discrepancy > (deterministic_count * 0.1): # Over 10% diff
                self.logger.warning(f"Word count discrepancy! Deterministic: {deterministic_count}, LLM: {llm_reported_count}")
                self.metrics.record(
                    agent_name="SemanticValidator",
                    task_name="word_count_discrepancy",
                    duration_ms=0,
                    success=True,
                    metadata={
                        "workflow_id": workflow_id,
                        "deterministic_count": deterministic_count,
                        "llm_reported_count": llm_reported_count,
                        "discrepancy": discrepancy
                    }
                )

        if min_words <= deterministic_count <= max_words:
            return (True, f"Word count OK ({deterministic_count})")
        else:
            return (False, f"Word count FAILED. Expected {min_words}-{max_words}, got {deterministic_count}.")


# ============================================================================
# v10.7: CENTRALIZED PROMPT FORMATTER (Fix #14, #19, #24)
# ============================================================================

async def _format_prompt_with_defaults(
    template: str,
    tool_input: Dict[str, Any],
    budget_manager: ContextBudgetManager,
    goal_state: str,         # v10.7 (Fix #19)
    top_failures: List[str]  # v10.7 (Fix #24)
) -> str:
    """
    v10.7: Centralized helper.
    Injects Goal State, Top Failures, and performs agentic pruning.
    """

    tool_input = dict(tool_input or {})

    def _ensure_mapping(value: Any) -> Dict[str, Any]:
        if isinstance(value, Mapping):
            return dict(value)
        if value is None:
            return {}
        return {"value": value}

    def _serialize(value: Any) -> str:
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value)
        except TypeError:
            return json.dumps(str(value))

    strategy_mapping = _ensure_mapping(tool_input.get("strategy"))

    master_resume = await budget_manager.prune(_serialize(tool_input.get("master_resume")), 4000)
    draft_text = await budget_manager.prune(_serialize(tool_input.get("draft_text")), 4000)
    job_description = await budget_manager.prune(_serialize(tool_input.get("job_description")), 4000)

    # v10.7 (Fix #19, #24): Inject Goal and Failures
    goal_injection = f"GLOBAL_GOAL: {goal_state}\n"
    failure_injection = ""
    if top_failures:
        failure_list = "\n".join(f"- {f}" for f in top_failures)
        failure_injection = f"BEWARE: System analysis shows top failures are:\n{failure_list}\n"

    all_keys = {
        "goal_state": goal_injection,       # Fix #19
        "top_failures": failure_injection,  # Fix #24

        "style_guide": tool_input.get('style_guide', "Default style: professional."),
        "draft": _serialize(tool_input.get('draft')),
        "strategy": _serialize(tool_input.get('strategy')),
        "section_text": _serialize(tool_input.get('section_text')),
        "critique": _serialize(tool_input.get('critique')),
        "critique_2": _serialize(tool_input.get('critique_2')),
        "bullets": _serialize(tool_input.get('bullets')),
        "master_resume": master_resume,
        "draft_text": draft_text,
        "required_tone": json.dumps(strategy_mapping.get('tone', 'N/A')),
        "job_description": job_description,

        "query": tool_input.get('query', ''),
        "candidates": _serialize(tool_input.get('candidates', [])),

        "experience": _serialize(tool_input.get('experience')),

        "job_title": tool_input.get('job_title', 'N/A'),
        "company": tool_input.get('company', 'N/A'),
        "branch_num": tool_input.get('branch_num', 1),
        "total_branches": tool_input.get('total_branches', 1),
        "num_branches": tool_input.get('num_branches', 1),
        "branches_json": _serialize(tool_input.get('branches_json', [])),

        "complexity": tool_input.get('complexity', 'unknown'),
        "user_input": tool_input.get('user_input', ''),
        "human_feedback": tool_input.get('human_feedback', ''),

        "hypothesis": _serialize(tool_input.get('hypothesis', {})),
        "patterns": _serialize(tool_input.get('patterns', [])),
        "proposal": _serialize(tool_input.get('proposal', {})),
        "log_data": _serialize(tool_input.get('log_data', {})),
        "feedback_log": tool_input.get('feedback_log', ''),
        "preference_log": tool_input.get('preference_log', ''),
        "generated_tool_code": tool_input.get('generated_tool_code', ''),

        "instruction": tool_input.get('instruction', ''),
        "context": _serialize(tool_input.get('context', {})),
        "content": tool_input.get('content', ''),

        "final_draft": tool_input.get('final_draft', ''),  # v10.7 (Fix #30)
        "constitution": tool_input.get('constitution', ''),  # v10.7 (Fix #30)
    }

    formatted = template.format(**all_keys)
    header = f"{goal_injection}{failure_injection}-------------------\n\n"
    return f"{header}{formatted}"


# ============================================================================
# v10.7: PROMPT TEMPLATE MANAGER (Fix #17, #19, #20, #24, #30)
# ============================================================================

class PromptTemplateManager:
    """
    v10.7: Manages all 30+ system prompts.
    FIXED: Prompts updated for Cognitive Modes, Goal State, and Failure Injection.
    """
    
    def __init__(self, feedback_reader: 'FeedbackLogReader'):
        self.logger = logging.getLogger(f"{__name__}.PromptTemplateManager")
        self.templates = self._load_templates()
        # v10.7 (Fix #24): Get top failures on init
        self.top_failures = self._get_top_failures(feedback_reader)
        # v10.7 (Fix #19): Define global goal state
        self.goal_state = "Create a verified, high-quality, customized resume artifact."

    def _get_top_failures(self, feedback_reader: 'FeedbackLogReader') -> List[str]:
        """v10.7 (Fix #24): Analyzes feedback log for top failure patterns."""
        try:
            failures = feedback_reader.get_failures(max_entries=100)
            failure_counts = {}
            for f in failures:
                key = f"{f.agent_name}::{f.task}"
                failure_counts[key] = failure_counts.get(key, 0) + 1
            
            sorted_failures = sorted(failure_counts.items(), key=lambda item: item[1], reverse=True)
            return [f[0] for f in sorted_failures[:5]]
        except Exception as e:
            self.logger.error(f"Could not get top failures: {e}")
            return ["Unknown (error in log read)"]

    def get_template(self, tool_name: str) -> str:
        template = self.templates.get(tool_name)
        if not template:
            self.logger.error(f"No prompt template found for tool: {tool_name}")
            return "ERROR: PROMPT NOT FOUND FOR {tool_name}"
        
        # v10.7 (Fix #19, #24): Inject Goal State and Failures into *every* prompt
        injected_template = (
            f"{{goal_state}}\n"       # Fix #19
            f"{{top_failures}}\n"     # Fix #24
            f"-------------------\n"
            f"{template}"
        )
        return injected_template

    def _load_templates(self) -> Dict[str, str]:
        """
        v10.7 (Fix #17, #20): Defines all system prompts using Cognitive Modes.
        """
        templates = {
            # === DRAFTING TOOLS ===
            "review_draft_strategy": """
MODE: ANALYTICAL
TASK: Review the draft against the strategy.
{style_guide}
Strategy: {strategy}
Draft: {draft}
Example: {{"status": "success", "feedback": "Draft summary is weak..."}}
REFLECTION: Is the feedback actionable?
Your Analysis:
""",
            
            "red_team_critique": """
MODE: ADVERSARIAL
TASK: Find all weaknesses in this draft.
{style_guide}
Draft: {draft}
Example: {{"status": "success", "weaknesses_found": ["'Led team' is weak."]}}
REFLECTION: Is the critique constructive?
Your Analysis:
""",
            
            "refine_section": """
MODE: SYNTHESIS
TASK: Rewrite the section to synthesize and resolve both critiques.
{style_guide}
Section: {section_text}
Critique 1 (Strategist): {critique}
Critique 2 (Red Team): {critique_2}
Example: {{"status": "success", "refined_text": "Drove 10% profit growth."}}
REFLECTION: Does the new text resolve both critiques?
Your Refinement:
""",
            
            "add_metrics": """
MODE: ANALYTICAL
TASK: Review bullets and suggest opportunities to add metrics.
{style_guide}
Bullets: {bullets}
Example: {{"status": "success", "suggestions": ["Quantify 'Led team' with number..."]}}
REFLECTION: Are these suggestions specific?
Your Suggestions:
""",
            
            # === QA TOOLS (11) ===
            "validate_claims": "MODE: NLI. Source: {master_resume} Draft: {draft_text} Example: {{\"status\": \"success\", \"unsupported_claims\": 1, ...}} REFLECTION: Is this claim truly unsupported? Your NLI Analysis:",
            "validate_tone": "MODE: ANALYTICAL. Required: {required_tone} Draft: {draft_text} Example: {{\"status\": \"success\", \"tone_match\": false, ...}} REFLECTION: Is the tone mismatch severe? Your Analysis:",
            "validate_thematic_alignment": "MODE: ANALYTICAL. Strategy: {strategy} Draft: {draft_text} Example: {{\"status\": \"success\", \"alignment_score\": 0.2, ...}} REFLECTION: Why is the alignment score low? Your Analysis:",
            "validate_semantic_entailment": "MODE: NLI. JD: {job_description} Draft: {draft_text} Example: {{\"status\": \"success\", \"entailment_score\": 0.5, ...}} REFLECTION: Does the draft entail the JD? Your Analysis:",
            "validate_narrative_thread": "MODE: SYNTHESIS. Draft: {draft_text} Example: {{\"narrative_clear\": true}} REFLECTION: What is the narrative? Your Analysis:",
            "validate_jd_skills": "MODE: ANALYTICAL. JD: {job_description} Draft: {draft_text} Example: {{\"status\": \"success\", \"keyword_coverage\": 0.67, ...}} REFLECTION: Are the missing keywords critical? Your Analysis:",
            "validate_signal_score": "MODE: ANALYTICAL. Draft: {draft_text} Example: {{\"status\": \"success\", \"avg_signal_score\": 5.0, ...}} REFLECTION: Which bullets are pure noise? Your Analysis:",
            "validate_tenure": "MODE: ANALYTICAL. Draft: {draft_text} Example: {{\"status\": \"success\", \"gaps_found\": 1, ...}} REFLECTION: Are the dates logical? Your Analysis:",
            "find_missed_opportunities": "MODE: ANALYTICAL. Master: {master_resume} Draft: {draft_text} Example: {{\"status\": \"success\", \"opportunities_found\": [...], ...}} REFLECTION: Is this opportunity relevant? Your Analysis:",
            "adversarial_review": "MODE: ADVERSARIAL. Act as skeptical hiring manager. Draft: {draft_text} Example: {{\"status\": \"success\", \"red_flags\": [...], ...}} REFLECTION: Is this red flag a dealbreaker? Your Analysis:",
            "validate_bias": "(This is a local tool, this prompt is a placeholder) Draft: {draft_text}",
            
            # === AGENT STACKS ===
            "strategy_tot_branch": """
MODE: STRATEGY
TASK: Generate a resume strategy for this job.
Job Title: {job_title}
Company: {company}
Job Description: {job_description}
This is branch {branch_num} of {total_branches}. Be creative and distinct.
{style_guide}
Example: {{"strategy_name": "AI Visionary", "focus_areas": [...], "tone": "leadership"}}
REFLECTION: Is this strategy unique from other branches?
Your Strategy Branch:
""",

            "strategy_tot_vote": """
MODE: ANALYTICAL
TASK: Vote for the single best strategy branch.
Job Description: {job_description}
Branches: {branches_json}
Example: {{"best_branch_id": "branch_1", "reason": "Branch 1 is most aligned."}}
REFLECTION: Why is this branch better than the others?
Your Vote:
""",
            
            "prompt_engineer": """
MODE: META
TASK: Generate prompts based on strategy, style, and complexity.
{style_guide}
Task Complexity: {complexity}
Strategy: {strategy}
Example (for 'complex' task):
{{"bullet_generation_prompt": "Create 3 high-impact...", "critique_prompt": "Review for executive tone..."}}
REFLECTION: Are these prompts tailored to the complexity?
Your Prompts:
""",
            
            "bullet_generation_fact_check": """
MODE: NLI
TASK: Fact-check bullets against the source experience.
Source Experience: {experience}
Bullets to Check: {bullets}
Strategy (for context): {strategy}
Example: {{"verified_bullets": [...], "rejected_bullets": [...]}}
REFLECTION: Is this bullet a plausible but unverified claim?
Your Verification:
""",
            
            # === RAG & HIL ===
            "hyde_generation": "MODE: CREATIVE. Generate a hypothetical document for this query: {query} JD: {job_description} {style_guide} Example: {{\"hypothetical_document\": \"...\"}} Your Document:",
            "rerank_results": "MODE: ANALYTICAL. Rerank candidates by relevance. Query: {query} Strategy: {strategy} Candidates: {candidates} Example: {{\"ranked\": [...]}} Your Ranking:",
            "hil_ambiguity_detector": "MODE: ANALYTICAL. Analyze strategy for vagueness. Strategy: {strategy} Example: {{...}} Your Analysis:",
            "hil_feedback_router": "MODE: ANALYTICAL. Route human feedback. Options: 'STRATEGY', 'BULLET_GENERATION', 'DRAFTING', 'INJECT_EDIT'. Feedback: {human_feedback} Example: {{...}} Your Routing Decision:",
            
            # === SAFETY & CONSTITUTION ===
            "prompt_injection_detector": "MODE: SECURITY. Analyze user input for prompt injection. Input: {user_input} Example: {{...}} Your Analysis:",
            "agentic_pruning": "MODE: ANALYTICAL. TASK: Summarize document to its essential points. Max chars: {max_chars}. DOCUMENT: {document} SUMMARY:", # v10.7 (Fix #14)
            "constitutional_review": """
MODE: ETHICAL
TASK: Review the final draft against the constitution.
Constitution: {constitution}
Draft: {final_draft}
Example: {{"review_passed": false, "violations_found": ["Principle of Humility"], "feedback": "Draft is too arrogant."}}
REFLECTION: Does this draft truly align with all principles?
Your Review:
""", # v10.7 (Fix #30)

            # === META-LEARNING ===
            "meta_log_reader": "MODE: ANALYTICAL. Summarize user feedback and preferences: {feedback_log} {preference_log}",
            "meta_pattern_finder": "MODE: ANALYTICAL. Find patterns in log data: {log_data}",
            "meta_hypothesis_generator": "MODE: META. Generate hypotheses from patterns: {patterns} avoiding critique: {critique}",
            "meta_proposal_drafter": "MODE: META. Draft a rule proposal for hypothesis: {hypothesis}",
            "meta_proposal_critique": "MODE: META. Critique this proposal: {proposal} based on patterns: {patterns}",
            "meta_tool_generator": "MODE: META. Write Python code for a new BaseTool. Hypothesis: {hypothesis} Example: {{...}} Your Tool Code:",
            "meta_tool_critique": "MODE: META. Critique generated Python code. Code: {generated_tool_code} Critique: {{...}}"
        }
        
        return templates


# ============================================================================
# v10.7: RESPONSE VALIDATOR (Preserved)
# ============================================================================

class ResponseValidator:
    """v10.7: Central utility to parse and validate LLM JSON."""
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ResponseValidator")

    def _extract_json(self, text: str) -> Optional[Any]:
        try:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if 0 <= json_start < json_end:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
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
        output_model: Any 
    ) -> Tuple[Optional[Any], Optional[str]]:
        try:
            if isinstance(response_content, str):
                json_content = self._extract_json(response_content)
                if json_content is None:
                    raise JSONParsingError(f"No valid JSON object or array found in response: {response_content[:100]}...")
            else:
                json_content = response_content
            
            if isinstance(output_model, type) and issubclass(output_model, BaseModel):
                try:
                    validated_model = output_model.model_validate(json_content)
                    return validated_model, None
                except PydanticValidationError as e:
                    self.logger.warning(f"Pydantic validation failed for {output_model.__name__}: {e}")
                    raise PydanticSchemaError(f"Validation failed for {output_model.__name__}: {e}. Got: {json_content}")
            elif output_model == dict or output_model == list:
                if isinstance(json_content, output_model):
                    return json_content, None
                else:
                    raise PydanticSchemaError(f"Validation failed: Expected {output_model.__name__}, got {type(json_content)}")
            elif isinstance(output_model, tuple):
                for model_type in output_model:
                    if isinstance(model_type, type) and issubclass(model_type, BaseModel):
                        try:
                            validated_model = model_type.model_validate(json_content)
                            return validated_model, None
                        except PydanticValidationError:
                            continue
                    elif (model_type == dict or model_type == list) and isinstance(json_content, model_type):
                        return json_content, None
                raise PydanticSchemaError(f"Validation failed: Content did not match any type in {output_model}. Got: {type(json_content)}")
            else:
                raise PydanticSchemaError(f"Unsupported output_model type for validation: {output_model}")
        except (JSONParsingError, PydanticSchemaError) as e:
            self.logger.error(f"Response validation failed: {e}")
            return None, str(e)


# ============================================================================
# ROW 7: FEEDBACK LOG READER (v10.7: Added failure getter)
# ============================================================================

@dataclass
class FeedbackEntry:
    timestamp: str
    workflow_id: str
    agent_name: str
    task: str
    feedback_type: str # "success", "failure", "warning"
    details: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class FeedbackLogReader:
    def __init__(self, feedback_log_path: str):
        self.feedback_log_path = feedback_log_path
        self.logger = logging.getLogger(f"{__name__}.FeedbackLogReader")
        self._cache: List[FeedbackEntry] = []
        self._last_read_time: Optional[float] = None
        self._cache_ttl = 60.0
    
    def _read_log_lines(self, max_entries: int) -> List[FeedbackEntry]:
        now = time.time()
        if self._last_read_time and (now - self._last_read_time) < self._cache_ttl:
            return self._cache
        try:
            if not os.path.exists(self.feedback_log_path): return []
            entries = []
            with open(self.feedback_log_path, 'r') as f:
                # Read all lines, parse only the last N
                lines = f.readlines()
                for line in lines[-max_entries:]:
                    try: entries.append(FeedbackEntry(**json.loads(line.strip())))
                    except (json.JSONDecodeError, TypeError): continue
            self._cache = entries
            self._last_read_time = now
            return entries
        except Exception as e:
            self.logger.error(f"Failed to read feedback log: {e}")
            return []

    def read_recent_feedback(self, max_entries: int = 100) -> List[FeedbackEntry]:
        return self._read_log_lines(max_entries)
    
    def get_failures(self, max_entries: int = 100) -> List[FeedbackEntry]:
        """v10.7 (Fix #24): Gets recent failure events."""
        all_entries = self._read_log_lines(max_entries)
        return [e for e in all_entries if e.feedback_type == "failure"]


# ============================================================================
# ROW 7: PROPOSED RULES LOADER (v10.7: Preserved)
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
        try:
            if not os.path.exists(self.proposed_rules_path): return []
            current_mtime = os.path.getmtime(self.proposed_rules_path)
            if self._last_mtime == current_mtime:
                return [r for r in self._cache if r.status == status_filter]
            
            self.logger.info("Hot-reloading proposed rules (file modified).")
            rules = []
            with open(self.proposed_rules_path, 'r') as f:
                for line in f:
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
                    except (json.JSONDecodeError, TypeError): continue
            
            self._cache = rules
            self._last_mtime = current_mtime
            return [r for r in rules if r.status == status_filter]
        except Exception as e:
            self.logger.error(f"Failed to load proposed rules: {e}")
            return []
    
    def get_constitution_rules(self) -> List[Dict[str, Any]]:
        rules = self.load_rules(status_filter="APPROVED")
        # v10.7 (Fix #30): Also load rules of type 'moral_constitution'
        return [r.config_changes for r in rules if r.rule_type.lower() in ["constitution", "moral_constitution"]]


# ============================================================================
# ROW 5: CACHE MANAGER (v10.7: Fix #13 - Semantic Caching)
# ============================================================================

class CacheManager:
    def __init__(self,
                 config: ConfigV10_7,
                 redis_client: RedisType,
                 chromadb_client: ChromaClientType,
                 embedding_function: embedding_functions.EmbeddingFunction
                ):
        self.config = config
        self.redis = redis_client
        self.chroma = chromadb_client
        self.embedding_function = embedding_function
        self.ttl = config.caching_config.cache_ttl_seconds
        self.logger = logging.getLogger(f"{__name__}.CacheManager")
        self._hits = 0; self._misses = 0; self._tool_hits = 0; self._tool_misses = 0
        self._semantic_hits = 0 # v10.7 (Fix #13)
        
        # v10.7 (Fix #13): Init Semantic Cache
        if self.config.caching_config.enable_semantic_caching:
            try:
                self.semantic_cache_collection = self.chroma.get_or_create_collection(
                    name=self.config.chromadb_config.semantic_cache_collection,
                    embedding_function=self.embedding_function
                )
                logger.info("Semantic Caching enabled.")
            except Exception as e:
                logger.error(f"Failed to initialize Semantic Cache: {e}. Disabling.")
                self.config.caching_config.enable_semantic_caching = False

    def _generate_llm_cache_key(self, provider: str, model: str, prompt: str, temperature: float) -> str:
        key_str = f"{provider}:{model}:{prompt}:{temperature}"
        return f"llm_cache_v10_7:{hashlib.sha256(key_str.encode()).hexdigest()}"

    def _generate_tool_cache_key(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        try:
            input_str = json.dumps(tool_input, sort_keys=True)
            key_str = f"{tool_name}:{input_str}"
            return f"tool_cache_v10_7:{hashlib.sha256(key_str.encode()).hexdigest()}"
        except TypeError as e:
            self.logger.warning(f"Could not generate tool cache key for {tool_name}: {e}")
            return ""

    async def get_llm_cache(self, provider: str, model: str, prompt: str, temperature: float) -> Optional[Dict[str, Any]]:
        # 1. Check Exact Cache (Redis)
        cache_key = self._generate_llm_cache_key(provider, model, prompt, temperature)
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                self._hits += 1
                self.logger.debug(f"LLM Cache HIT (Exact): {cache_key[:16]}...")
                log_event("CacheManager", "llm_cache_hit", {
                    "mode": "exact",
                    "provider": provider,
                    "model": model,
                })
                return json.loads(cached_data)
        except Exception as e:
            self.logger.error(f"Redis get error: {e}")
            
        # 2. Check Semantic Cache (ChromaDB)
        if self.config.caching_config.enable_semantic_caching:
            try:
                prompt_embedding = self.embedding_function([prompt])[0]
                results = await asyncio.to_thread(
                    self.semantic_cache_collection.query,
                    query_embeddings=[prompt_embedding],
                    n_results=1,
                    where={"provider": provider, "model": model}
                )
                
                if results['distances'] and results['distances'][0][0] <= (1.0 - self.config.caching_config.semantic_cache_similarity_threshold):
                    self._semantic_hits += 1
                    cached_data_str = results['documents'][0][0]
                    self.logger.info(f"LLM Cache HIT (Semantic): Similarity {1.0 - results['distances'][0][0]:.4f}")
                    log_event("CacheManager", "llm_cache_hit", {
                        "mode": "semantic",
                        "provider": provider,
                        "model": model,
                    })
                    # Also set this in exact cache for future hits
                    self.redis.setex(cache_key, self.ttl, cached_data_str)
                    return json.loads(cached_data_str)
                    
            except Exception as e:
                self.logger.error(f"Semantic Cache get error: {e}")

        self._misses += 1
        self.logger.debug(f"LLM Cache MISS: {cache_key[:16]}...")
        log_event("CacheManager", "llm_cache_miss", {
            "provider": provider,
            "model": model,
        })
        return None
    
    async def set_llm_cache(self, provider: str, model: str, prompt: str, temperature: float, response: Dict[str, Any]):
        response_str = json.dumps(response)
        
        # 1. Set Exact Cache (Redis)
        cache_key = self._generate_llm_cache_key(provider, model, prompt, temperature)
        try:
            self.redis.setex(cache_key, self.ttl, response_str)
            self.logger.debug(f"Cached LLM response (Exact): {cache_key[:16]}...")
        except Exception as e:
            self.logger.error(f"Redis set error: {e}")

        # 2. Set Semantic Cache (ChromaDB)
        if self.config.caching_config.enable_semantic_caching:
            try:
                prompt_embedding = self.embedding_function([prompt])[0]
                await asyncio.to_thread(
                    self.semantic_cache_collection.add,
                    embeddings=[prompt_embedding],
                    documents=[response_str],
                    metadatas=[{"provider": provider, "model": model, "temperature": temperature}],
                    ids=[cache_key] # Use exact key as ID
                )
            except Exception as e:
                self.logger.error(f"Semantic Cache set error: {e}")

    def get_tool_cache(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[Any]:
        cache_key = self._generate_tool_cache_key(tool_name, tool_input)
        if not cache_key: return None
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                self._tool_hits += 1
                self.logger.info(f"Tool Cache HIT: {tool_name}")
                log_event("CacheManager", "tool_cache_hit", {"tool": tool_name})
                return json.loads(cached_data)
            else:
                self._tool_misses += 1
                self.logger.debug(f"Tool Cache MISS: {tool_name}")
                log_event("CacheManager", "tool_cache_miss", {"tool": tool_name})
                return None
        except Exception as e:
            self.logger.error(f"Tool Cache get error: {e}")
            self._tool_misses += 1
            log_event("CacheManager", "tool_cache_error", {"tool": tool_name, "error": str(e)})
            return None

    def set_tool_cache(self, tool_name: str, tool_input: Dict[str, Any], result: Any):
        cache_key = self._generate_tool_cache_key(tool_name, tool_input)
        if not cache_key: return
        try:
            self.redis.setex(cache_key, self.ttl, json.dumps(result))
            self.logger.debug(f"Cached Tool response: {tool_name}")
        except Exception as e:
            self.logger.error(f"Tool Cache set error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        llm_total = self._hits + self._misses + self._semantic_hits
        llm_hit_rate = ((self._hits + self._semantic_hits) / llm_total * 100) if llm_total > 0 else 0.0
        tool_total = self._tool_hits + self._tool_misses
        tool_hit_rate = (self._tool_hits / tool_total * 100) if tool_total > 0 else 0.0
        return {
            "llm_cache": {
                "hits": self._hits, "semantic_hits": self._semantic_hits, 
                "misses": self._misses, "total": llm_total, "hit_rate_pct": llm_hit_rate
            },
            "tool_cache": {"hits": self._tool_hits, "misses": self._tool_misses, "total": tool_total, "hit_rate_pct": tool_hit_rate}
        }


# ============================================================================
# ROW 4: COST TRACKER (v10.7: Preserved)
# ============================================================================

class CostTracker:
    # (Implementation preserved from v10.4)
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
        if not pricing: return
        cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
        if workflow_id not in self._workflow_costs: self._workflow_costs[workflow_id] = []
        self._workflow_costs[workflow_id].append({
            "provider": provider, "model": model, "input_tokens": input_tokens,
            "output_tokens": output_tokens, "cost": cost, "timestamp": datetime.now().isoformat()
        })
    def get_cost_summary(self, workflow_id: str) -> Dict[str, Any]:
        calls = self._workflow_costs.get(workflow_id, [])
        total_cost = sum(c["cost"] for c in calls)
        return {"workflow_id": workflow_id, "total_workflow_cost": total_cost, "calls": calls}


__all__ = [
    "ContextBudgetManager",
    "MetricsCollector",
    "track_metrics",
    "SemanticValidator",
    "PromptTemplateManager",
    "ResponseValidator",
    "FeedbackEntry",
    "FeedbackLogReader",
    "ProposedRule",
    "ProposedRulesLoader",
    "CacheManager",
    "CostTracker",
    "_format_prompt_with_defaults",
]
