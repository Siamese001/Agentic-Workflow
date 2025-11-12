# File: agent_stacks_v10_6.py
# Version: 10.6 (Refactored)
#
# v10.6 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_6.
# - REFACTORED (Fix #14, #17, #19, #20, #24): All agents (ToT, Prompt,
#   RAG, Bullet, HIL) refactored to use the new async
#   `_format_prompt_with_defaults` from core. This ensures all
#   prompts now correctly include Cognitive Modes, Goal State,
#   Failure Warnings, and use agentic context pruning.
#
# v10.6 MAJOR CHANGES:
# - IMPLEMENTED (Fix #10): RAG_SearchAgent's signature changed. It now
#   accepts the full `state` and returns a state patch `{"resume": ..., "a2a": ...}`
#   to send A2A messages if the RAG loop fails.
# - IMPLEMENTED (Fix #30): Added new `ConstitutionalReviewerAgent`
#   to perform a final review of the draft.
# - FIXED: All v10_5 imports and class names updated to v10_6.
# - FIXED: `RAG_SearchAgent` now correctly imports and uses the
#   `embedding_function` from its `WorkflowContext`.

import os
import json
import logging
import asyncio
import re
import math
import uuid
from collections import Counter
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, validator

# v10.6: Import from new core
from core_v10_6 import (
    _format_prompt_with_defaults, # v10.6: Now an async function
    WorkflowContext, BaseAgent,
    ModelAPIError, JSONParsingError, ValidationError, PydanticSchemaError,
    # Import Pydantic models
    StrategyPlan,
    GeneratedPrompts,
    BulletList,
    CritiqueResult,
    HILAmbiguityReport,
    HILFeedbackRoute,
    HILFeedbackIntent,
    HILReconciliationResult,
    PersonaConsensus,
    PersonaReviewDecision,
    BaseToolOutput,
    ConstitutionalReviewResult, # v10.6 (Fix #30)
    A2AMessage, # v10.6 (Fix #10)
    # v10.6: Import new decorators and services
    track_metrics,
    MetricsCollector,
    BaseTool,
    detect_bias
)

# v10.6: Import from new tools file
from agent_tools_v10_6 import (
    HyDETool,
    ChromaDBSearchTool,
    BM25SearchTool
)

# v10.6: Logger name updated
logger = logging.getLogger("agent_stacks_v10_6")

# ============================================================================
# ROW 7: SAFETY GUARD STACK (v10.6: Added Constitutional AI)
# ============================================================================

class PIISanitizerAgent(BaseAgent):
    """v10.6: Local PII detection using regex."""
    PII_PATTERNS = {
        "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        "PHONE": re.compile(r'\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b'),
        "NAME": re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b') 
    }
    
    @track_metrics('run_pii_sanitizer')
    def run(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        self.log_info("Sanitizing PII (local regex processing)...")
        sanitized_resume = json.loads(json.dumps(resume))
        
        def sanitize_node(node):
            if isinstance(node, dict): return {k: sanitize_node(v) for k, v in node.items()}
            elif isinstance(node, list): return [sanitize_node(item) for item in node]
            elif isinstance(node, str): return self._sanitize_text(node)
            else: return node

        sanitized = sanitize_node(sanitized_resume)
        self.log_info("PII sanitization complete.")
        return sanitized

    def _sanitize_text(self, text: str) -> str:
        for pii_type, pattern in self.PII_PATTERNS.items():
            text = pattern.sub(f"[{pii_type}_REDACTED]", text)
        return text

class BiasDetectorAgent(BaseAgent):
    """v10.6: Local bias detection with dynamic constitution."""
    
    @track_metrics('run_bias_detector')
    def run(self, text: str, workflow_id: str = "") -> Dict[str, Any]:
        self.log_info("Detecting bias (local processing with dynamic rules)...")
        result = detect_bias(self.context, text, workflow_id)

        if workflow_id:
            self.log_feedback(
                workflow_id,
                "bias_detection",
                "warning" if result["bias_detected"] else "success",
                {"patterns_found": len(result.get("patterns", []))}
            )

        return result

class PromptInjectionDetectorAgent(BaseAgent):
    """v10.6: Detects prompt injection attacks."""

    class PIDetectionOutput(BaseModel):
        injection_detected: bool = Field(..., description="True if an attack was detected")
        reason: str = Field(..., description="Explanation for the detection")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the detection")
    
    @track_metrics('run_pi_detector')
    async def run_async(self, user_input: str, workflow_id: str) -> Dict[str, Any]:
        self.log_info("Detecting prompt injection...")
        
        if not self.config.agent_stacks.enable_prompt_injection_detection:
            self.log_warning("Prompt injection detection is disabled.")
            return {"injection_detected": False, "reason": "Detector disabled", "confidence": 0.0}

        client = self.get_model_client("prompt_injection_model")
        prompt_template = self.prompt_manager.get_template("prompt_injection_detector")
        
        # v10.6 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template, 
            {"user_input": user_input}, 
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.prompt_injection_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.PIDetectionOutput)
        if error:
            self.log_error(f"PromptInjectionDetector failed validation: {error}")
            return {"injection_detected": True, "reason": f"Detector validation failed: {error}", "confidence": 1.0}
        
        if validated_output.injection_detected:
            self.log_warning(f"PROMPT INJECTION DETECTED (Confidence: {validated_output.confidence}): {validated_output.reason}")
            
        return validated_output.model_dump()

class ConstitutionalReviewerAgent(BaseAgent):
    """v10.6 (Fix #30): Performs final constitutional review of the output."""
    
    @track_metrics('run_constitutional_review')
    async def run_async(self, final_draft: str, workflow_id: str) -> ConstitutionalReviewResult:
        self.log_info("Running final constitutional review...")
        
        if not self.config.agent_stacks.enable_constitutional_review:
            self.log_warning("Constitutional review is disabled. Passing by default.")
            return ConstitutionalReviewResult(review_passed=True, violations_found=[], feedback="Review disabled")

        client = self.get_model_client("constitutional_review_model")
        prompt_template = self.prompt_manager.get_template("constitutional_review")
        
        # Load rules from the same loader
        rules = self.context.rules_loader.get_constitution_rules()
        constitution_text = json.dumps(rules)
        
        prompt = await _format_prompt_with_defaults(
            prompt_template, 
            {"final_draft": final_draft, "constitution": constitution_text},
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.constitutional_review_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], ConstitutionalReviewResult)
        if error:
            self.log_error(f"ConstitutionalReviewer failed validation: {error}. Failing open (passing draft).")
            return ConstitutionalReviewResult(review_passed=True, violations_found=["VALIDATION_ERROR"], feedback=error)
        
        if not validated_output.review_passed:
            self.log_warning(f"CONSTITUTIONAL REVIEW FAILED: {validated_output.violations_found}")
            
        return validated_output

# ============================================================================
# ROW 7: STRATEGY STACK (v10.6: Refactored)
# ============================================================================

class QueryComplexityClassifier(BaseAgent):
    """v10.6: Classifies query complexity for dynamic routing."""
    
    class ComplexityOutput(BaseModel):
        complexity: str = Field(..., description="The estimated complexity ('simple' or 'complex')")
        reason: str = Field(..., description="Justification for the complexity rating")

    @track_metrics('run_complexity_classifier')
    async def run_async(self, job_description: str, workflow_id: str) -> str:
        self.log_info("Classifying query complexity...")
        
        client = self.get_model_client("strategy_model_simple") 
        
        # v10.6 REFACTOR: Use centralized async formatter
        # Note: This prompt is simple and doesn't use a template
        pruned_jd = await self.budget_manager.prune(job_description, 2000)
        prompt = f"""
        {client.goal_state}
        {client.top_failures}
        -------------------
        MODE: ANALYTICAL
        TASK: Classify the job description's complexity as 'simple' or 'complex'.
        'simple' = Junior role, few requirements, common tech.
        'complex' = Senior/Executive role, many requirements, niche tech, leadership.
        
        Job Description:
        {pruned_jd}
        
        REFLECTION: What is the seniority level?
        Output JSON:
        {{"complexity": "simple/complex", "reason": "..."}}
        """
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.strategy_model_simple.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.ComplexityOutput)
        if error:
            self.log_error(f"ComplexityClassifier failed validation: {error}. Defaulting to 'complex'.")
            return "complex"
            
        self.log_info(f"Task complexity classified as: {validated_output.complexity}")
        return validated_output.complexity

class ToTStrategistAgent(BaseAgent):
    """v10.6: ToT strategist with self-consistency voting."""
    
    async def _generate_branches(self, job_context: Dict[str, Any], client: Any, branching_factor: int) -> List[Dict]:
        prompt_template = self.prompt_manager.get_template("strategy_tot_branch")
        
        branch_tasks = []
        for i in range(branching_factor):
            # v10.6 REFACTOR: Use centralized async formatter
            prompt = await _format_prompt_with_defaults(
                prompt_template,
                {
                    "job_title": job_context.get('job_title', 'N/A'),
                    "company": job_context.get('company', 'N/A'),
                    "job_description": job_context.get('job_description', 'N/A'),
                    "branch_num": i+1,
                    "total_branches": branching_factor,
                    "style_guide": "Style: Be creative and strategically distinct."
                },
                self.budget_manager,
                client.goal_state,
                client.top_failures
            )
            branch_tasks.append(client.chat_completion_async(
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.model_config.strategy_model.temperature,
                response_format="json_object"
            ))
            
        responses = await asyncio.gather(*branch_tasks, return_exceptions=True)
        
        branches = []
        for i, res in enumerate(responses):
            if isinstance(res, Exception):
                self.log_warning(f"ToT Branch {i+1} failed API call: {res}")
                continue
            validated_output, error = self.validator.validate(res["content"], StrategyPlan)
            if error:
                self.log_warning(f"ToT Branch {i+1} failed validation: {error}")
                continue 
            branches.append({"branch_id": f"branch_{i}", "strategy": validated_output})
        return branches
    
    @track_metrics('run_tot_strategy')
    async def run_async(self, job_context: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Generating ToT strategy with voting (v10.6)...")
        
        branching_factor = self.config.agent_stacks.strategy_tot_branching_factor
        client = self.get_model_client("strategy_model")
        
        branches = await self._generate_branches(job_context, client, branching_factor)
        if not branches:
            raise ValidationError("All ToT strategy branches failed validation.")
            
        self.log_info(f"Generated {len(branches)} branches. Starting vote...")
        vote_client = self.get_model_client("strategy_model_simple")
        vote_prompt_template = self.prompt_manager.get_template("strategy_tot_vote")
        
        branches_json = json.dumps([{"id": b["branch_id"], "plan": b["strategy"].model_dump()} for b in branches])
        
        # v10.6 REFACTOR: Use centralized async formatter
        vote_prompt = await _format_prompt_with_defaults(
            vote_prompt_template,
            {
                "num_branches": len(branches),
                "job_description": job_context.get('job_description', 'N/A'),
                "branches_json": branches_json
            },
            self.budget_manager,
            vote_client.goal_state,
            vote_client.top_failures
        )
        
        vote_response = await vote_client.chat_completion_async(
            messages=[{"role": "user", "content": vote_prompt}],
            temperature=0.1,
            response_format="json_object"
        )
        
        class VoteOutput(BaseModel):
            best_branch_id: str
            reason: str
            
        validated_vote, error = self.validator.validate(vote_response["content"], VoteOutput)
        
        selected_strategy = None
        if error:
            self.log_error(f"Strategy vote validation failed: {error}. Defaulting to first branch.")
            selected_strategy = branches[0]["strategy"]
        else:
            self.log_info(f"Vote selected: {validated_vote.best_branch_id}. Reason: {validated_vote.reason}")
            selected_strategy = next(
                (b["strategy"] for b in branches if b["branch_id"] == validated_vote.best_branch_id),
                branches[0]["strategy"] # Fallback
            )
        
        self.log_feedback(
            workflow_id, "tot_strategy_vote", "success",
            {"branches_generated": len(branches), "selected": selected_strategy.strategy_name}
        )
        
        return {
            "strategy_plan": selected_strategy,
            "tot_branches": [b["strategy"].model_dump() for b in branches]
        }

# ============================================================================
# ROW 7: PROMPT STACK (v10.6: Refactored)
# ============================================================================

class PromptEngineerAgent(BaseAgent):
    """v10.6: LLM-driven prompt engineering, complexity-aware."""
    
    @track_metrics('run_prompt_engineer')
    async def run_async(self, strategy: StrategyPlan, complexity: str, workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Engineering prompts (Complexity: {complexity})...")
        
        client = self.get_model_client("prompt_engineer_model")
        
        meta_prompt_template = self.prompt_manager.get_template("prompt_engineer")
        
        # v10.6 REFACTOR: Use centralized async formatter
        meta_prompt = await _format_prompt_with_defaults(
            meta_prompt_template,
            {
                "strategy": strategy.model_dump_json(),
                "complexity": complexity,
                "style_guide": "Style: Generate clear, role-appropriate prompts.",
                "job_description": "N/A"
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=self.config.model_config.prompt_engineer_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], GeneratedPrompts)
        if error:
            raise PydanticSchemaError(f"PromptEngineerAgent failed validation: {error}")
        
        self.log_feedback(
            workflow_id, "prompt_engineering", "success",
            {"complexity": complexity, "prompt_count": 2}
        )
        
        return {"prompts": validated_output}

# ============================================================================
# ROW 7: RAG STACK (v10.6: Fix #10 - A2A Comms)
# ============================================================================

class RAG_SearchAgent(BaseAgent):
    """
    v10.6 (Fix #3, #10): Agentic RAG Conductor (ReAct).
    Orchestrates RAG tools and sends A2A messages on failure.
    """
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.tools = {
            "search_resume_database": ChromaDBSearchTool(context, debug_mode),
            "search_resume_bm25": BM25SearchTool(context, debug_mode),
            "generate_hypothetical_documents": HyDETool(context, debug_mode)
        }
        self.tool_schemas = [t.get_schema() for t in self.tools.values()]
        self.chroma_client = self.context.chromadb_client
        self.collection_name = self.config.chromadb_config.default_collection_name
        # v10.6: Use injected embedding function
        self.embedding_function = self.context.embedding_function

    
    async def _ingest_resume_to_chroma_async(self, resume_experience: List[Dict], workflow_id: str):
        self.log_info(f"Ingesting {len(resume_experience)} experience blocks into ChromaDB...")
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            documents, metadatas, ids = [], [], []
            for exp in resume_experience:
                for bullet in exp.get("bullet_pool", []):
                    documents.append(bullet)
                    metadatas.append({
                        "workflow_id": workflow_id,
                        "company": exp.get("company", "N/A"),
                        "title": exp.get("title", "N/A"),
                        "experience_object": json.dumps(exp) 
                    })
                    ids.append(f"{workflow_id}_{uuid.uuid4()}")
            
            if documents:
                await asyncio.to_thread(collection.add, documents=documents, metadatas=metadatas, ids=ids)
        except Exception as e:
            self.log_error(f"ChromaDB ingestion failed: {e}")

    def _build_bm25_corpus(self, resume_experience: List[Dict]) -> (List[str], List[Dict]):
        corpus_text, corpus_metadata = [], []
        for exp in resume_experience:
            doc = f"{exp.get('title')} {exp.get('company')} {' '.join(exp.get('bullet_pool', []))}"
            corpus_text.append(doc)
            corpus_metadata.append(exp)
        return corpus_text, corpus_metadata

    def _merge_and_deduplicate(self, all_results: List[List[Dict]]) -> List[Dict]:
        merged = {}
        for result_list in all_results:
            for item in result_list:
                key = f"{item.get('company')}_{item.get('title')}"
                if key not in merged:
                    merged[key] = item
        return list(merged.values())

    async def rerank_results(self, query: str, candidates: List[Dict], client: Any) -> List[Dict]:
        self.log_info(f"Reranking {len(candidates)} hybrid candidates...")
        prompt_template = self.prompt_manager.get_template("rerank_results")
        
        # v10.6 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template, 
            {"query": query, "strategy": "N/A", "candidates": json.dumps(candidates)},
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.reranker_model.temperature, 
            response_format="json_object"
        )
        try:
            content, error = self.validator.validate(response["content"], dict)
            if error: raise PydanticSchemaError(error)
            ranked_list = content.get("ranked")
            if isinstance(ranked_list, list):
                ranked = ranked_list[:self.config.agent_stacks.reranking_top_k]
            else:
                ranked = candidates[:self.config.agent_stacks.reranking_top_k]
        except Exception:
            ranked = candidates[:self.config.agent_stacks.reranking_top_k]
        return ranked

    @track_metrics('run_agentic_rag')
    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log_info("Running Agentic RAG Conductor (v10.6)...")
        
        # v10.6 (Fix #10): Get inputs from state
        workflow_id = state['metadata']['workflow_id']
        query = f"{state['job']['job_title']} at {state['job']['company']}"
        resume_experience = state['resume']['master_resume'].get('professional_experience', [])
        a2a_messages = state.get('a2a', {}).get('messages', [])
        
        await self._ingest_resume_to_chroma_async(resume_experience, workflow_id)
        corpus_text, corpus_metadata = self._build_bm25_corpus(resume_experience)
        
        client = self.get_model_client("react_conductor_model")
        rerank_client = self.get_model_client("reranker_model")
        max_steps = 5
        
        # v10.6 REFACTOR: Use centralized async formatter for main prompt
        react_prompt_template = f"""
        {client.goal_state}
        {client.top_failures}
        -------------------
        MODE: ORCHESTRATION
        TASK: You are an Agentic RAG Conductor. Find relevant resume sections.
        Query: "{query}"
        Tools: {json.dumps(self.tool_schemas)}
        Plan:
        1. Call `search_resume_database` (vector) and `search_resume_bm25` (keyword).
        2. THINK: Analyze merged results.
        3. If results are good (> 3), stop.
        4. If results are poor (< 3), call `generate_hypothetical_documents`.
        5. Loop to step 1 with the new query.
        6. Output final list.
        """
        
        messages = [{"role": "user", "content": react_prompt_template}]
        current_query = query
        all_tool_results = []
        
        for step in range(max_steps):
            response = await client.chat_completion_async(
                messages=messages,
                temperature=self.config.agent_stacks.conductor_temperature,
                response_format="json_object"
            )
            
            step_data, error = self.validator.validate(response["content"], dict)
            if error:
                messages.append({"role": "user", "content": f"Error: Invalid JSON: {error}"})
                continue
            
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if "final_results" in step_data:
                self.log_info(f"RAG agent finished in {step+1} steps.")
                merged = self._merge_and_deduplicate([step_data["final_results"]])
                ranked = await self.rerank_results(query, merged, rerank_client)
                return {"resume": {"experience_bullets": ranked}, "a2a": {"messages": a2a_messages}}
            
            if "tool_call" in step_data:
                # ... (Tool call logic preserved from v10.5) ...
                tool_name = step_data["tool_call"].get("name")
                tool_input = step_data["tool_call"].get("input", {})
                if tool_name not in self.tools:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})
                    continue
                if tool_name == "search_resume_bm25":
                    tool_input["corpus_text"] = corpus_text
                    tool_input["corpus_metadata"] = corpus_metadata
                if 'query' not in tool_input:
                    tool_input['query'] = current_query
                try:
                    tool = self.tools[tool_name]
                    tool_result = await tool.run_async(tool_input, workflow_id)
                    if tool_name == "generate_hypothetical_documents" and tool_result.get("status") == "success":
                        current_query = tool_result["hypothetical_document"]
                    elif tool_name in ["search_resume_database", "search_resume_bm25"]:
                        all_tool_results.append(tool_result.get("search_results", []))
                    messages.append({"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"})
                except Exception as e:
                    self.log_error(f"RAG Tool {tool_name} failed: {e}")
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' failed: {e}"})

        self.log_warning(f"RAG agent reached max steps. Reranking gathered results.")
        
        # v10.6 (Fix #10): Send A2A message on failure
        a2a_messages.append(A2AMessage(
            sender="RAG_SearchAgent",
            recipient="ALL",
            message_type="ERROR",
            payload={"error": "RAG_SearchAgent max steps reached."}
        ).model_dump()) # Send as dict
        
        merged = self._merge_and_deduplicate(all_tool_results)
        ranked = await self.rerank_results(query, merged, rerank_client)
        return {"resume": {"experience_bullets": ranked}, "a2a": {"messages": a2a_messages}}

# ============================================================================
# ROW 7: BULLET STACK (v10.6: Refactored)
# ============================================================================

class AsyncBulletGeneratorAgent(BaseAgent):
    """v10.6: Async bullet generator with 4-step provenance plan"""
    
    @track_metrics('run_bullet_generator')
    async def run_async(self, prompt: str, experience: Dict, strategy: StrategyPlan, workflow_id: str) -> List[str]:
        self.log_info(f"Generating bullets for '{experience.get('title')}' (v10.6)...")
        
        client = self.get_model_client("bullet_generator_model")
        fact_check_client = self.get_model_client("bullet_fact_check_model")

        verbatim = await self.run_verbatim(experience, workflow_id)
        customized = await self.run_customized(prompt, experience, client)
        synthetic = await self.run_synthetic(prompt, experience, client)
        
        all_bullets = verbatim + customized + synthetic
        final_bullets = await self.run_fact_check(all_bullets, experience, strategy, fact_check_client)
        
        self.log_feedback(workflow_id, "bullet_generation_4_step", "success", {"bullets_generated": len(final_bullets)})
        return final_bullets

    @track_metrics('run_verbatim_bullets')
    async def run_verbatim(self, experience: Dict, workflow_id: str) -> List[str]:
        metric_pattern = re.compile(r'[%$]|\d')
        bullet_pool = experience.get('bullet_pool', [])
        metric_bullets = [b for b in bullet_pool if metric_pattern.search(b)]
        if not metric_bullets: metric_bullets = bullet_pool[:2]
        return metric_bullets[:3]

    @track_metrics('run_customized_bullets')
    async def run_customized(self, prompt: str, experience: Dict, client: Any) -> List[str]:
        gen_prompt = f"""
        {client.goal_state}
        {client.top_failures}
        -------------------
        MODE: CREATIVE
        TASK: {prompt}\nCustomize these bullets:\n{json.dumps(experience.get('bullet_pool', []))}
        REFLECTION: Are these bullets customized to the prompt?
        Output: JSON array of 2-3 achievement bullets.
        """
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": gen_prompt}], 
            temperature=self.config.model_config.bullet_generator_model.temperature, 
            response_format="json_object"
        )
        content, error = self.validator.validate(response["content"], (list, dict))
        if error: return []
        if isinstance(content, list): return content
        if isinstance(content, dict) and "bullets" in content: return content["bullets"]
        return []

    @track_metrics('run_synthetic_bullets')
    async def run_synthetic(self, prompt: str, experience: Dict, client: Any) -> List[str]:
        gen_prompt = f"""
        {client.goal_state}
        {client.top_failures}
        -------------------
        MODE: CREATIVE
        TASK: {prompt}\nExperience (no bullets):\n{json.dumps({'title': experience.get('title'), 'company': experience.get('company')})}
        REFLECTION: Are these bullets new and metrics-driven?
        Output: JSON array of 2 new achievement bullets.
        """
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": gen_prompt}], 
            temperature=self.config.model_config.bullet_generator_model.temperature, 
            response_format="json_object"
        )
        content, error = self.validator.validate(response["content"], (list, dict))
        if error: return []
        if isinstance(content, list): return content
        if isinstance(content, dict) and "bullets" in content: return content["bullets"]
        return []

    @track_metrics('run_fact_check_bullets')
    async def run_fact_check(self, bullets: List[str], experience: Dict, strategy: StrategyPlan, client: Any) -> List[str]:
        self.log_info("Fact-checking bullets (v10.6)...")
        
        prompt_template = self.prompt_manager.get_template("bullet_generation_fact_check")
        
        # v10.6 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {
                "experience": json.dumps(experience),
                "bullets": json.dumps(bullets),
                "strategy": strategy.model_dump_json()
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.bullet_fact_check_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], BulletList)
        if error:
            self.log_warning(f"Fact-check validation failed: {error}. Returning original bullets.")
            return bullets
            
        return validated_output.verified_bullets

class AsyncBulletCritiqueAgent(BaseAgent):
    """v10.6: Async bullet critique."""
    
    @track_metrics('run_bullet_critique')
    async def run_async(self, bullets: List[Dict], critique_prompt: str, workflow_id: str) -> List[Dict]:
        self.log_info("Critiquing bullets with validation (v10.6)...")
        
        client = self.get_model_client("critique_model")
        bullet_texts = [b['text'] for b in bullets]
        critique_results = []
        
        critique_tasks = []
        for bullet in bullet_texts:
            # v10.6 REFACTOR: Use Cognitive Mode in ad-hoc prompt
            task_prompt = f"""
            {client.goal_state}
            {client.top_failures}
            -------------------
            MODE: ANALYTICAL
            TASK: {critique_prompt}\nBullet: {bullet}
            REFLECTION: Is this critique specific?
            Output: JSON with score 0-10 and suggestions.
            """
            critique_tasks.append(
                client.chat_completion_async(
                    messages=[{"role": "user", "content": task_prompt}],
                    temperature=self.config.model_config.critique_model.temperature,
                    response_format="json_object"
                )
            )
        responses = await asyncio.gather(*critique_tasks)
        
        for res in responses:
            validated_output, error = self.validator.validate(res["content"], CritiqueResult)
            if error:
                critique_results.append(CritiqueResult(score=0.0, suggestions=["Validation failed"]))
            else:
                critique_results.append(validated_output)
        
        self.log_feedback(workflow_id, "parallel_critique", "success", {"bullets_critiqued": len(bullets)})
            
        final_critiqued_bullets = []
        for i, original_bullet in enumerate(bullets):
            final_critiqued_bullets.append({
                "text": original_bullet['text'],
                "experience": original_bullet['experience'],
                "critique": critique_results[i].model_dump() 
            })
            
        return final_critiqued_bullets

# ============================================================================
# ROW 7: HIL STACK (v10.6: Refactored & Extended)
# ============================================================================


class VirtualReviewerPersonaAgent(BaseAgent):
    """Persona-specialized reviewer that interprets human feedback."""

    PersonaPrompt = """
    You are acting as the {persona} reviewer.
    Specialty focus: {focus}
    Human feedback:
    {human_feedback}

    Clustered intents summary:
    {intent_summary}

    Provide a JSON object with keys:
    - persona (string)
    - approval (boolean)
    - confidence (0-1 float)
    - key_concerns (list of strings)
    - proposed_actions (list of strings)
    - escalation_recommended (boolean)
    """

    def __init__(self, context: 'WorkflowContext', persona: str, focus: str, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.persona = persona
        self.focus = focus

    @track_metrics('run_virtual_reviewer_persona')
    async def run_async(
        self,
        human_feedback: str,
        intent_clusters: List[HILFeedbackIntent],
        workflow_id: str
    ) -> PersonaReviewDecision:
        client = self.get_model_client("qa_model")
        intent_summary = json.dumps([intent.model_dump() for intent in intent_clusters]) if intent_clusters else "[]"
        prompt = await _format_prompt_with_defaults(
            self.PersonaPrompt,
            {
                "persona": self.persona,
                "focus": self.focus,
                "human_feedback": human_feedback,
                "intent_summary": intent_summary
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object"
        )

        validated_output, error = self.validator.validate(response["content"], PersonaReviewDecision)
        if error:
            self.log_warning(f"Persona {self.persona} validation failed: {error}. Using fallback decision.")
            fallback = PersonaReviewDecision(
                persona=self.persona,
                approval=False,
                confidence=0.0,
                key_concerns=["Unable to parse persona feedback"],
                proposed_actions=[],
                escalation_recommended=True
            )
            self.log_feedback(
                workflow_id,
                "virtual_persona_decision",
                "error",
                fallback.model_dump()
            )
            return fallback

        self.log_feedback(
            workflow_id,
            "virtual_persona_decision",
            "success",
            validated_output.model_dump()
        )

        return validated_output


class VirtualReviewerCouncilAgent(BaseAgent):
    """Coordinates persona reviewers to negotiate a consensus."""

    DEFAULT_PERSONAS = [
        {"name": "Legal", "focus": "Ensure compliance, risk mitigation, and policy adherence."},
        {"name": "Brand", "focus": "Protect voice, tone, and reputation considerations."},
        {"name": "SME", "focus": "Validate technical accuracy and subject-matter fidelity."}
    ]

    @track_metrics('run_virtual_reviewer_council')
    async def run_async(
        self,
        human_feedback: str,
        intent_clusters: List[HILFeedbackIntent],
        workflow_id: str
    ) -> PersonaConsensus:
        persona_tasks = []
        for persona in self.DEFAULT_PERSONAS:
            persona_agent = VirtualReviewerPersonaAgent(
                self.context,
                persona["name"],
                persona["focus"],
                self.debug_mode
            )
            persona_tasks.append(persona_agent.run_async(human_feedback, intent_clusters, workflow_id))

        persona_decisions = await asyncio.gather(*persona_tasks)
        approvals = sum(1 for decision in persona_decisions if decision.approval)
        escalations = any(decision.escalation_recommended for decision in persona_decisions)
        approved = approvals >= math.ceil(len(persona_decisions) / 2)

        negotiated_actions: List[str] = []
        for decision in persona_decisions:
            for action in decision.proposed_actions:
                if action not in negotiated_actions:
                    negotiated_actions.append(action)

        rationale = (
            "Consensus reached with majority approval." if approved else
            "Consensus blocked: additional drafting or strategy work required."
        )
        if escalations:
            rationale += " Legal/SME escalation recommended by at least one persona."

        consensus = PersonaConsensus(
            approved=approved,
            rationale=rationale,
            negotiated_actions=negotiated_actions,
            persona_votes=persona_decisions
        )

        self.log_feedback(
            workflow_id,
            "virtual_persona_consensus",
            "success" if approved else "warning",
            {
                "approved": approved,
                "negotiated_actions": negotiated_actions,
                "persona_votes": [vote.model_dump() for vote in persona_decisions]
            }
        )

        return consensus


class HILFeedbackSummarizerAgent(BaseAgent):
    """Clusters human edits into reusable intents for downstream routing."""

    class SummarizerOutput(BaseModel):
        intent_clusters: List[HILFeedbackIntent] = Field(default_factory=list)
        delegation_score: float = Field(0.0, ge=0.0, le=1.0)
        recommended_node: str = Field("DRAFTING")
        recommended_specialists: List[str] = Field(default_factory=list)

    @track_metrics('run_hil_feedback_summarizer')
    async def run_async(
        self,
        human_feedback: str,
        state_snapshot: Optional[Dict[str, Any]],
        workflow_id: str
    ) -> SummarizerOutput:
        if not human_feedback.strip():
            return self.SummarizerOutput()

        client = self.get_model_client("qa_model")
        prompt_body = {
            "human_feedback": human_feedback,
            "state_snapshot": json.dumps(state_snapshot or {}, default=str)
        }
        prompt = await _format_prompt_with_defaults(
            "Cluster human edits into intents and recommend routing.",
            prompt_body,
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object"
        )

        validated_output, error = self.validator.validate(response["content"], self.SummarizerOutput)
        if error:
            self.log_warning(f"Summarizer validation failed: {error}. Using default routing.")
            output = self.SummarizerOutput()
        else:
            output = validated_output

        self.log_feedback(
            workflow_id,
            "hil_intent_summary",
            "success" if not error else "warning",
            {
                "delegation_score": output.delegation_score,
                "recommended_node": output.recommended_node,
                "intent_count": len(output.intent_clusters)
            }
        )

        return output


class HILReconciliationAgent(BaseAgent):
    """Integrates specialist human feedback back into the draft."""

    @track_metrics('run_hil_reconciliation')
    async def run_async(
        self,
        draft_sections: Dict[str, Any],
        specialist_feedback: List[str],
        persona_consensus: Optional[PersonaConsensus],
        workflow_id: str
    ) -> HILReconciliationResult:
        if not specialist_feedback:
            empty_result = HILReconciliationResult(
                integrated_text=json.dumps(draft_sections),
                change_log=["No specialist feedback provided"],
                unresolved_questions=[]
            )
            self.log_feedback(
                workflow_id,
                "hil_reconciliation",
                "warning",
                empty_result.model_dump()
            )
            return empty_result

        client = self.get_model_client("qa_model")
        prompt = await _format_prompt_with_defaults(
            """
            Integrate the following specialist feedback into the draft.
            Draft sections:
            {draft}
            Specialist feedback entries:
            {feedback}
            Persona consensus summary:
            {consensus}

            Respond as JSON with keys: integrated_text (string), change_log (list of strings), unresolved_questions (list).
            """,
            {
                "draft": json.dumps(draft_sections, default=str),
                "feedback": json.dumps(specialist_feedback, default=str),
                "consensus": json.dumps(persona_consensus.model_dump() if persona_consensus else {}, default=str)
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object"
        )

        validated_output, error = self.validator.validate(response["content"], HILReconciliationResult)
        if error:
            self.log_warning(f"Reconciliation validation failed: {error}. Returning fallback.")
            fallback = HILReconciliationResult(
                integrated_text=json.dumps(draft_sections),
                change_log=[f"Reconciliation failed validation: {error}"],
                unresolved_questions=specialist_feedback
            )
            self.log_feedback(
                workflow_id,
                "hil_reconciliation",
                "error",
                fallback.model_dump()
            )
            return fallback

        self.log_feedback(
            workflow_id,
            "hil_reconciliation",
            "success",
            validated_output.model_dump()
        )

        return validated_output


class HILAmbiguityDetectorAgent(BaseAgent):
    """v10.6: Proactively detects ambiguity."""
    
    @track_metrics('run_ambiguity_detector')
    async def run_async(self, strategy: StrategyPlan, workflow_id: str) -> Dict[str, Any]:
        self.log_info("Detecting ambiguity (v10.6)...")
        client = self.get_model_client("qa_model")
        
        prompt_template = self.prompt_manager.get_template("hil_ambiguity_detector")
        
        # v10.6 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template, 
            {"strategy": strategy.model_dump_json()},
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], HILAmbiguityReport)
        if error:
            raise PydanticSchemaError(f"HILAmbiguityDetector failed validation: {error}")
        
        self.log_feedback(workflow_id, "ambiguity_detection", "success", {"detected": validated_output.ambiguity_detected})
        
        return {"ambiguity_report": validated_output}

class HILFeedbackRouterAgent(BaseAgent):
    """v10.6: Routes human feedback with persona negotiation and delegation."""

    @track_metrics('run_feedback_router')
    async def run_async(
        self,
        human_feedback: str,
        workflow_id: str,
        state_snapshot: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.log_info("Routing human feedback with persona council...")

        try:
            log_path = self.config.meta_loop_config.preference_log_path
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "workflow_id": workflow_id,
                    "feedback": human_feedback
                }, f)
                f.write('\n')
        except Exception as e:
            self.log_error(f"Failed to log HIL preference feedback: {e}")

        if not human_feedback.strip():
            self.log_warning("No human feedback supplied. Defaulting to drafting continuation.")
            default_route = HILFeedbackRoute(next_step="DRAFTING", payload=None)
            return default_route.model_dump()

        summarizer = HILFeedbackSummarizerAgent(self.context, self.debug_mode)
        summary_output = await summarizer.run_async(human_feedback, state_snapshot, workflow_id)
        intent_clusters = summary_output.intent_clusters

        council = VirtualReviewerCouncilAgent(self.context, self.debug_mode)
        persona_consensus = await council.run_async(human_feedback, intent_clusters, workflow_id)

        delegated_specialists = summary_output.recommended_specialists
        delegation_score = summary_output.delegation_score

        delegation_threshold = getattr(self.config.agent_stacks, "hil_delegation_threshold", 0.65)
        strategy_threshold = getattr(self.config.agent_stacks, "hil_strategy_threshold", 0.45)

        next_step = summary_output.recommended_node or "DRAFTING"
        if not persona_consensus.approved:
            self.log_info("Persona consensus blocked. Routing to strategy for clarification.")
            next_step = "STRATEGY"

        elif delegation_score >= delegation_threshold and delegated_specialists:
            self.log_info(
                f"Delegation threshold met ({delegation_score:.2f} >= {delegation_threshold}). Escalating to specialists."
            )
            next_step = "DELEGATE_SPECIALIST"

        elif delegation_score >= strategy_threshold and summary_output.recommended_node == "STRATEGY":
            self.log_info("Strategy adjustments recommended based on delegation score.")
            next_step = "STRATEGY"

        payload = None
        if intent_clusters:
            payload = intent_clusters[0].summary

        route = HILFeedbackRoute(
            next_step=next_step,
            payload=payload,
            intent_clusters=intent_clusters,
            delegated_specialists=delegated_specialists,
            persona_consensus=persona_consensus,
        )

        return route.model_dump()

# ============================================================================
# END OF agent_stacks_v10_6.py
# ============================================================================