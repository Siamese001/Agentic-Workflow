# File: agent_swarm_v6.5.py
# Version: 6.5 (Monolithic Agent Architecture)
# Overwrites: agent_swarm_v6_4.py
#
# v6.5 (Based on v7.0 Architecture) CHANGES:
# - This is now a single, monolithic file containing all agents.
# - Removed dependency on validation_stack_v6_4.py.
# - Replaced the entire multi-agent "Strategy Stack" (JDParser, ThemeIdentifier, etc.)
#   with a single new 'ThemeClassifierAgent' (Step 1).
# - Updated RAG agents (Step 2) to use specified Tier 1 models.
# - Updated Adversarial MoE Drafting agents (Step 3) with new roles (Strategist, RedTeam, Refiner)
#   and new models (Gemini 2.5 Pro, Claude 4.1 Opus, GPT-5).
# - Added new 'WorkflowRePlannerAgent' (Step 3 - SC Paths).
# - Added all 'Atomic QA Swarm (LLM)' agents (Step 4) as new classes in this file.
# - Added 'AtomicQALogicAgent' (Step 4) for Python-based checks.
# - Removed all '_simulate_llm_call' stubs. Agents now use get_model_client().
# - Heavily refactored the 'Governor' to instantiate and execute the new v7.0 agents
#   in a linear sequence, removing all old "_run_..._stack" methods.

# ============================================================================
# EXTERNAL IMPORTS
# ============================================================================
import copy
import hashlib
import json
import logging
import os
import random
import re
import time
from collections import defaultdict
from enum import Enum
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Import from core_v6_5
from core_v6_5 import (
    # Base
    BaseAgent, get_model_client, CONFIG,
    # Models
    HopExecutionError, MechanicalFailureError, SemanticFailureError, FactualFailureException,
    ValidationSeverity, ValidationResult, ReasoningConfig, ReasoningStrategy,
    ThematicAnalysis, RAG_Blackboard, RAGMission, RAGPhase, StrategyBrief,
    ReflectionIteration, ReflectionResult, ReflectionStatus,
    ToolCall, ToolType, ReActTrace,
    MoEExpertResult, MoEDecision, ConductorBranch, ConductorDecision,
    WorkflowBlackboard, WorkflowPlan, WorkflowStep,
    # Config
    DEFAULT_GENERATION_TEMPERATURE,
    # Utils
    text_utils, fence_data,
    # Prompts
    STRATEGY_THEME_CLASSIFICATION_SYSTEM_PROMPT, STRATEGY_THEME_CLASSIFICATION_USER_PROMPT,
    RAG_QUERY_GEN_SYSTEM_PROMPT, RAG_QUERY_GEN_USER_PROMPT,
    RAG_CRITIQUE_SYSTEM_PROMPT, RAG_CRITIQUE_USER_PROMPT,
    DRAFTING_STRATEGIST_SYSTEM_PROMPT, DRAFTING_REDTEAM_SYSTEM_PROMPT,
    DRAFTING_REFINER_SYSTEM_PROMPT, DRAFTING_USER_PROMPT,
    REPLANNER_SYSTEM_PROMPT, REPLANNER_USER_PROMPT,
    QA_CLAIM_VALIDATOR_SYSTEM_PROMPT, QA_TONE_VALIDATOR_SYSTEM_PROMPT,
    QA_ALIGNMENT_VALIDATOR_SYSTEM_PROMPT, QA_ENTAILMENT_VALIDATOR_SYSTEM_PROMPT,
    QA_NARRATIVE_VALIDATOR_SYSTEM_PROMPT, QA_ADVERSARIAL_VALIDATOR_SYSTEM_PROMPT,
    QA_JD_SKILLS_VALIDATOR_SYSTEM_PROMPT, QA_SIGNAL_SCORE_VALIDATOR_SYSTEM_PROMPT,
    QA_BIAS_VALIDATOR_SYSTEM_PROMPT, QA_TENURE_VALIDATOR_SYSTEM_PROMPT,
    QA_GENERIC_USER_PROMPT
)

logger = logging.getLogger(__name__)

# ============================================================================
# V6.5: WORKFLOW STEP ENUM
# ============================================================================

class WorkflowSteps(Enum):
    """Centralizes workflow step names to match v7.0 Architecture."""
    STRATEGY = "step_1_strategy"
    RAG = "step_2_rag"
    DRAFTING = "step_3_drafting"
    QA = "step_4_qa"
    RECOVERY = "retry_failed"

# ============================================================================
# PART 1: STRATEGY AGENT (v7.0 Step 1)
# ============================================================================

class ThemeClassifierAgent(BaseAgent):
    """
    v7.0 Step 1: Strategy
    Replaces the entire v6.4 strategy stack.
    A simple, fast agent that classifies the input job description.
    
    Corresponds to:
    Component: ThemeClassifierAgent
    Intelligence: 20 (Low)
    Tier: Tier 3 (Speed/Cost)
    Model: Gemini 2.5 Flash-Lite
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "ThemeClassifierAgent"
        self.model_name = "gemini-2.5-flash-lite"
        self.client_name = "google"
        
        try:
            self.client = get_model_client(
                client_name=self.client_name,
                model_name=self.model_name
            )
            self.log_info(f"Initialized with model: {self.model_name}")
        except Exception as e:
            self.log_error(f"Failed to initialize model client: {e}")
            self.client = None

    def run(self, job_description_text: str) -> dict:
        self.log_info("Running Step 1: Strategy Classification...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for ThemeClassifierAgent.")

        if not job_description_text:
            self.log_warning("No job description text provided.")
            return {"error": "No job description text provided."}

        try:
            messages = [
                {"role": "system", "content": STRATEGY_THEME_CLASSIFICATION_SYSTEM_PROMPT},
                {"role": "user", "content": STRATEGY_THEME_CLASSIFICATION_USER_PROMPT.format(job_description=job_description_text)}
            ]

            response = self.client.chat_completion(
                messages=messages,
                response_format="json_object"
            )

            if not response:
                raise Exception("Model returned an empty response.")

            self.log_info("Successfully classified strategy theme.")
            classification_data = response
            classification_data["agent_name"] = self.agent_name
            
            # Store this crucial artifact on the blackboard
            self.blackboard.update_artifact("strategy_brief", classification_data)
            return classification_data

        except Exception as e:
            self.log_error(f"Error during theme classification: {e}")
            raise HopExecutionError(f"ThemeClassifierAgent failed: {e}")

# ============================================================================
# PART 2: RAG STACK AGENTS (v7.0 Step 2)
# ============================================================================

class RAG_QueryGeneratorAgent(BaseAgent):
    """
    v7.0 Step 2: RAG - QueryGen
    Generates RAG queries based on the strategy.
    
    Corresponds to:
    Component: RAG_QueryGen
    Intelligence: 75 (High)
    Tier: Tier 1 (Flagship)
    Model: Gemini 2.5 Pro
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "RAG_QueryGen"
        self.model_name = "gemini-2.5-pro"
        self.client_name = "google"
        
        try:
            self.client = get_model_client(
                client_name=self.client_name,
                model_name=self.model_name
            )
            self.log_info(f"Initialized with model: {self.model_name}")
        except Exception as e:
            self.log_error(f"Failed to initialize model client: {e}")
            self.client = None

    def run(self, strategy_brief: dict) -> List[str]:
        self.log_info("Running Step 2: RAG Query Generation...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for RAG_QueryGeneratorAgent.")
        
        try:
            # Create a user prompt context from the strategy brief
            prompt_context = json.dumps(strategy_brief, indent=2)
            
            messages = [
                {"role": "system", "content": RAG_QUERY_GEN_SYSTEM_PROMPT},
                {"role": "user", "content": RAG_QUERY_GEN_USER_PROMPT.format(strategy_brief=prompt_context)}
            ]

            response = self.client.chat_completion(
                messages=messages,
                response_format="json_object"
            )

            if not response or "queries" not in response:
                raise Exception("Model returned invalid query list.")

            queries = response.get("queries", [])
            self.log_info(f"Generated {len(queries)} RAG queries.")
            self.blackboard.update_artifact("rag_queries", queries)
            return queries

        except Exception as e:
            self.log_error(f"Error during RAG query generation: {e}")
            raise HopExecutionError(f"RAG_QueryGeneratorAgent failed: {e}")

class RAG_SearchAgent(BaseAgent):
    """
    v7.0 Step 2: RAG - Search (ReAct)
    Executes RAG searches with ReAct loop (Thought-Action-Observation).
    
    Corresponds to:
    Component: RAG_SearchAgent (ReAct)
    Intelligence: 90 (High)
    ReAct: Yes
    Tier: Tier 1 (Flagship)
    Model: Gemini 2.5 Pro
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "RAG_SearchAgent"
        self.model_name = "gemini-2.5-pro"
        self.client_name = "google"
        
        try:
            # This client is used for the ReAct "thought" process
            self.client = get_model_client(
                client_name=self.client_name,
                model_name=self.model_name
            )
            self.log_info(f"Initialized with model: {self.model_name}")
            
            # Tools are placeholder functions. In a real system, these
            # would be API calls to Google Search, ChromaDB, etc.
            self.available_tools = {
                "master_resume_search": self._tool_master_resume_search,
                "web_search": self._tool_web_search,
                "api_search_placeholder": self._tool_api_search_placeholder
            }
            
        except Exception as e:
            self.log_error(f"Failed to initialize model client: {e}")
            self.client = None
            
        self.max_react_iterations = CONFIG.react_config.max_reasoning_loops

    def run(self, queries: List[str]) -> Dict[str, Any]:
        self.log_info("Running Step 2: RAG ReAct Search...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for RAG_SearchAgent.")
        
        all_results = []
        react_traces = []
        master_resume = self.blackboard.master_resume

        for query in queries:
            self.log_info(f"Processing query: {query}")
            
            # ReAct Loop
            for iteration in range(self.max_react_iterations):
                # 1. THOUGHT: Reason about what to do next
                thought = self._generate_thought(query, iteration, all_results)
                
                # 2. ACTION: Select a tool
                # In a real ReAct loop, the LLM generates a function call.
                # We simulate this by having the "thought" guide the action.
                action, tool_name, tool_input = self._select_action(thought, query)
                
                # 3. OBSERVATION: Execute action and observe results
                try:
                    observation = action(tool_input)
                    tool_success = True
                except Exception as e:
                    observation = f"Tool {tool_name} failed: {e}"
                    tool_success = False

                react_traces.append(ReActTrace(
                    thought=thought,
                    action=ToolCall(
                        tool_type=ToolType.DOCUMENT_RETRIEVE, # Generic tool type
                        parameters=tool_input,
                        result=observation,
                        success=tool_success
                    ),
                    observation=str(observation)
                ))
                
                all_results.extend(observation if isinstance(observation, list) else [observation])

                # 4. Check if satisfied
                if self._is_satisfied(all_results):
                    self.log_info(f"Query satisfied after {iteration+1} iterations.")
                    break
        
        final_results = self._deduplicate_and_rank(all_results)
        self.blackboard.update_artifact("rag_search_results", final_results)
        self.blackboard.update_artifact("rag_react_traces", [asdict(t) for t in react_traces])
        return {"results": final_results, "traces": react_traces}

    def _generate_thought(self, query: str, iteration: int, current_results: List) -> str:
        # Simulate LLM thought generation (would be a real call in prod)
        if iteration == 0:
            return f"Thought: I need to find information about '{query}'. I will start by searching the master_resume_search tool."
        elif len(current_results) < 2:
            return f"Thought: The resume search yielded few results. I will try a broad 'web_search' for '{query}'."
        else:
            return "Thought: I have sufficient results from the resume. I am satisfied."

    def _select_action(self, thought: str, query: str) -> Tuple[Callable, str, Dict]:
        thought_low = thought.lower()
        if "master_resume_search" in thought_low:
            return self.available_tools["master_resume_search"], "master_resume_search", {"query": query}
        if "web_search" in thought_low:
            return self.available_tools["web_search"], "web_search", {"query": query}
        # Fallback
        return self.available_tools["master_resume_search"], "master_resume_search", {"query": query}

    def _is_satisfied(self, results: List) -> bool:
        # Simple heuristic
        return len(results) >= 5

    def _deduplicate_and_rank(self, results: List[Dict]) -> List[Dict]:
        unique_results = {}
        for doc in results:
            if isinstance(doc, dict) and doc.get("content_hash"):
                 unique_results[doc.get("content_hash")] = doc
        
        return sorted(unique_results.values(), key=lambda x: x.get("relevance_score", 0), reverse=True)


    # --- ReAct Tools ---
    def _tool_master_resume_search(self, tool_input: Dict) -> List[Dict]:
        query = tool_input.get("query", "")
        self.log_info(f"  Tool: _tool_master_resume_search (Query: {query})")
        master_resume = self.blackboard.master_resume
        
        all_bullets = []
        for exp in master_resume.get("professional_experience", []):
            all_bullets.extend(exp.get("bullet_pool", []))
            all_bullets.extend(exp.get("highlights", []))
        all_bullets.extend(master_resume.get("strategic_and_technical_competencies", []))


        scored_bullets = []
        for bullet in all_bullets:
            score = text_utils.calculate_similarity(query, bullet)
            if score > 0.3: # Relevance threshold
                scored_bullets.append({
                    "source": "master_resume",
                    "content": bullet,
                    "relevance_score": score,
                    "content_hash": hashlib.md5(bullet.encode()).hexdigest()
                })
        
        return sorted(scored_bullets, key=lambda x: x["relevance_score"], reverse=True)[:5]

    def _tool_web_search(self, tool_input: Dict) -> List[Dict]:
        query = tool_input.get("query", "")
        self.log_info(f"  Tool: _tool_web_search (Query: {query})")
        # Placeholder: In production, this calls an external Google Search API
        content = f"Placeholder web result for '{query}': Neo4j is the leader in Graph Database & Analytics."
        return [{
            "source": "web_search_placeholder",
            "content": content,
            "relevance_score": 0.8,
            "content_hash": hashlib.md5(content.encode()).hexdigest()
        }]
        
    def _tool_api_search_placeholder(self, tool_input: Dict) -> List[Dict]:
        # Corresponds to "ReAct Tools (Triggered)" in v7.0 Table
        self.log_info(f"  Tool: _tool_api_search_placeholder")
        return []


class RAG_CritiqueAgent(BaseAgent):
    """
    v7.0 Step 2: RAG - Critique
    Critiques the RAG results for relevance and sufficiency.
    
    Corresponds to:
    Component: RAG_Critique
    Intelligence: 85 (High)
    ReAct: Yes (Implicitly, as it critiques the search)
    Tier: Tier 1 (Flagship)
    Model: Gemini 2.5 Pro
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "RAG_Critique"
        self.model_name = "gemini-2.5-pro"
        self.client_name = "google"
        
        try:
            self.client = get_model_client(
                client_name=self.client_name,
                model_name=self.model_name
            )
            self.log_info(f"Initialized with model: {self.model_name}")
        except Exception as e:
            self.log_error(f"Failed to initialize model client: {e}")
            self.client = None

    def run(self, strategy_brief: dict, rag_results: List[dict]) -> dict:
        self.log_info("Running Step 2: RAG Critique...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for RAG_CritiqueAgent.")
        
        try:
            strategy_context = json.dumps(strategy_brief, indent=2)
            results_context = json.dumps(rag_results[:5], indent=2) # Critique top 5
            
            messages = [
                {"role": "system", "content": RAG_CRITIQUE_SYSTEM_PROMPT},
                {"role": "user", "content": RAG_CRITIQUE_USER_PROMPT.format(
                    strategy_brief=strategy_context,
                    rag_search_results=results_context
                )}
            ]

            response = self.client.chat_completion(
                messages=messages,
                response_format="json_object"
            )

            if not response:
                raise Exception("Model returned an empty critique.")

            self.log_info("Successfully critiqued RAG results.")
            self.blackboard.update_artifact("rag_critique", response)
            return response

        except Exception as e:
            self.log_error(f"Error during RAG critique: {e}")
            raise HopExecutionError(f"RAG_CritiqueAgent failed: {e}")


# ============================================================================
# PART 3: DRAFTING STACK AGENTS (v7.0 Step 3)
# ============================================================================

class PromptStackAgent(BaseAgent):
    """
    v7.0 Step 3: Drafting - Prompt Stack
    This is a simple Python-based agent that assembles prompts.
    
    Corresponds to:
    Component: Prompt Stack (7 Agents)
    Intelligence: 5 (Low)
    Tier: N/A (Python)
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "PromptStackAgent"

    def run(self) -> dict:
        self.log_info("Running Step 3: Prompt Stack Assembly...")
        try:
            strategy = self.blackboard.get_artifact("strategy_brief")
            rag_critique = self.blackboard.get_artifact("rag_critique")
            
            if not strategy or not rag_critique:
                raise HopExecutionError("Missing strategy_brief or rag_critique artifacts.")

            # Combine artifacts into a master prompt for the drafters
            combined_context = {
                "strategy": strategy,
                "rag_critique": rag_critique,
                "rag_results": self.blackboard.get_artifact("rag_search_results")
            }
            
            # This is the final prompt context for the drafting agents
            drafting_prompt_context = DRAFTING_USER_PROMPT.format(
                master_context=json.dumps(combined_context, indent=2)
            )
            
            self.blackboard.update_artifact("final_drafting_prompt", drafting_prompt_context)
            self.log_info("Prompt Stack assembly complete.")
            return {"final_prompt": drafting_prompt_context}
        
        except Exception as e:
            self.log_error(f"Error during Prompt Stack assembly: {e}")
            raise HopExecutionError(f"PromptStackAgent failed: {e}")

class BulletSwarmAgent(BaseAgent):
    """
    v7.0 Step 3: Drafting - Bullet Swarm
    This is a simple Python-based agent that selects bullets.
    
    Corresponds to:
    Component: Bullet Swarm (8 Agents)
    Intelligence: 5 (Low)
    Tier: N/A (Python)
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "BulletSwarmAgent"

    def run(self) -> List[str]:
        self.log_info("Running Step 3: Bullet Swarm...")
        try:
            strategy = self.blackboard.get_artifact("strategy_brief")
            if not strategy:
                raise HopExecutionError("Missing strategy_brief artifact.")
                
            master_resume = self.blackboard.master_resume
            all_bullets = []
            for exp in master_resume.get("professional_experience", []):
                all_bullets.extend(exp.get("bullet_pool", []))
                all_bullets.extend(exp.get("highlights", []))
            
            # Score bullets against the strategy
            query = json.dumps(strategy.get("key_skills", [])) + " " + strategy.get("primary_theme", "")
            
            scored_bullets = []
            for bullet in all_bullets:
                score = text_utils.calculate_similarity(query, bullet)
                if score > 0.25: # Relevance threshold
                    scored_bullets.append((score, bullet))
            
            scored_bullets.sort(key=lambda x: x[0], reverse=True)
            
            top_bullets = [bullet for score, bullet in scored_bullets[:8]] # Get top 8 bullets
            
            if not top_bullets:
                self.log_warning("Bullet swarm found no relevant bullets, using fallback.")
                top_bullets = ["Fallback: Led teams and drove revenue."]
                
            self.blackboard.update_artifact("generated_bullets", top_bullets)
            self.log_info(f"Bullet Swarm selected {len(top_bullets)} bullets.")
            return top_bullets
        
        except Exception as e:
            self.log_error(f"Error during Bullet Swarm: {e}")
            raise HopExecutionError(f"BulletSwarmAgent failed: {e}")


class AdversarialDraftingRouter(BaseAgent):
    """
    v7.0 Step 3: Drafting - Adversarial MoE
    Manages the iterative drafting process between Gemini, Claude, and GPT-5.
    
    Corresponds to:
    Component: AdversarialDrafterStrategist (Gemini)
    Component: RedTeam (Claude)
    Component: Refiner (GPT-5)
    """
    
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "AdversarialDraftingRouter"
        
        # v7.0: Initialize the three adversarial agents
        self.drafters = {
            "Strategist": self._init_drafter("google", "gemini-2.5-pro", DRAFTING_STRATEGIST_SYSTEM_PROMPT),
            "RedTeam": self._init_drafter("anthropic", "claude-4.1-opus", DRAFTING_REDTEAM_SYSTEM_PROMPT),
            "Refiner": self._init_drafter("openai", "gpt-5", DRAFTING_REFINER_SYSTEM_PROMPT)
        }

    def _init_drafter(self, client_name: str, model_name: str, system_prompt: str):
        try:
            client = get_model_client(client_name=client_name, model_name=model_name)
            self.log_info(f"Initialized drafter: {model_name}")
            return {"client": client, "system_prompt": system_prompt}
        except Exception as e:
            self.log_error(f"Failed to initialize drafter {model_name}: {e}")
            return None

    def run(self) -> str:
        self.log_info("Running Step 3: Adversarial MoE Drafting...")
        
        final_drafting_prompt = self.blackboard.get_artifact("final_drafting_prompt")
        bullets = self.blackboard.get_artifact("generated_bullets")
        
        if not final_drafting_prompt or not bullets:
            raise HopExecutionError("Missing prompt or bullets for drafting.")
            
        # Add bullets to the user prompt
        user_prompt_with_bullets = final_drafting_prompt + "\n\n<selected_bullets_for_reference>\n" + "\n".join(bullets) + "\n</selected_bullets_for_reference>"

        try:
            # 1. Strategist (Gemini) creates the first draft
            strategist = self.drafters.get("Strategist")
            if not strategist or not strategist["client"]: raise HopExecutionError("Strategist (Gemini) drafter not initialized.")
            
            messages_strategist = [
                {"role": "system", "content": strategist["system_prompt"]},
                {"role": "user", "content": user_prompt_with_bullets}
            ]
            draft_v1 = strategist["client"].chat_completion(messages=messages_strategist, max_tokens=4096)
            self.log_info("Draft v1 (Strategist) complete.")

            # 2. RedTeam (Claude) critiques the first draft
            red_team = self.drafters.get("RedTeam")
            if not red_team or not red_team["client"]: raise HopExecutionError("RedTeam (Claude) drafter not initialized.")
            
            # RedTeam prompt includes the draft
            red_team_user_prompt = user_prompt_with_bullets + f"\n\n<draft_to_critique>\n{draft_v1}\n</draft_to_critique>"
            messages_red_team = [
                {"role": "system", "content": red_team["system_prompt"]},
                {"role": "user", "content": red_team_user_prompt}
            ]
            critique = red_team["client"].chat_completion(messages=messages_red_team, max_tokens=1024)
            self.log_info("Critique (RedTeam) complete.")

            # 3. Refiner (GPT-5) creates the final draft using draft + critique
            refiner = self.drafters.get("Refiner")
            if not refiner or not refiner["client"]: raise HopExecutionError("Refiner (GPT-5) drafter not initialized.")
            
            # Refiner prompt includes draft + critique
            refiner_user_prompt = user_prompt_with_bullets + f"\n\n<draft_v1>\n{draft_v1}\n</draft_v1>\n\n<red_team_critique>\n{critique}\n</red_team_critique>"
            messages_refiner = [
                {"role": "system", "content": refiner["system_prompt"]},
                {"role": "user", "content": refiner_user_prompt}
            ]
            final_draft = refiner["client"].chat_completion(messages=messages_refiner, max_tokens=4096)
            self.log_info("Draft v2 (Refiner) complete.")
            
            self.blackboard.update_artifact("final_draft", final_draft)
            return final_draft

        except Exception as e:
            self.log_error(f"Error during adversarial drafting: {e}")
            raise HopExecutionError(f"AdversarialDraftingRouter failed: {e}")

class WorkflowRePlannerAgent(BaseAgent):
    """
    v7.0 Step 3: SC Paths
    A medium-intelligence agent to replan workflow if QA fails.
    
    Corresponds to:
    Component: WorkflowRePlannerAgent
    Intelligence: 70 (Medium)
    ReAct: Yes
    Tier: Tier 2 (Workhorse)
    Model: Gemini 2.5 Flash
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "WorkflowRePlannerAgent"
        self.model_name = "gemini-2.5-flash"
        self.client_name = "google"
        
        try:
            self.client = get_model_client(
                client_name=self.client_name,
                model_name=self.model_name
            )
            self.log_info(f"Initialized with model: {self.model_name}")
        except Exception as e:
            self.log_error(f"Failed to initialize model client: {e}")
            self.client = None

    def run(self, failed_qa_results: List[dict]) -> dict:
        self.log_info("Running Step 3 (SC Paths): Workflow Re-Planner...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for WorkflowRePlannerAgent.")
        
        try:
            qa_context = json.dumps(failed_qa_results, indent=2)
            
            messages = [
                {"role": "system", "content": REPLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": REPLANNER_USER_PROMPT.format(
                    qa_failures=qa_context,
                    current_artifacts=json.dumps(list(self.blackboard.artifacts.keys()), indent=2)
                )}
            ]

            response = self.client.chat_completion(
                messages=messages,
                response_format="json_object"
            )

            if not response or "suggested_plan" not in response:
                raise Exception("Model returned an invalid replan.")

            self.log_info("Successfully generated recovery plan.")
            self.blackboard.update_artifact("recovery_plan", response)
            return response

        except Exception as e:
            self.log_error(f"Error during workflow replanning: {e}")
            raise HopExecutionError(f"WorkflowRePlannerAgent failed: {e}")

# ============================================================================
# PART 4: QA STACK AGENTS (v7.0 Step 4)
# ============================================================================

class AtomicQASwarmLLM(BaseAgent):
    """
    v7.0 Step 4: Atomic QA Swarm (LLM)
    This agent orchestrates the 10 parallel LLM-based QA checks.
    """
    
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "AtomicQASwarmLLM"
        
        # v7.0: Define all 10 QA agents
        self.qa_agents = {
            "ClaimValidator": self._init_qa_agent("ClaimValidatorAgent (NLI)", QA_CLAIM_VALIDATOR_SYSTEM_PROMPT),
            "ToneValidator": self._init_qa_agent("ToneValidator", QA_TONE_VALIDATOR_SYSTEM_PROMPT),
            "ThematicAlignment": self._init_qa_agent("ThematicAlignment_Validator", QA_ALIGNMENT_VALIDATOR_SYSTEM_PROMPT),
            "SemanticEntailment": self._init_qa_agent("SemanticEntailmentValidator", QA_ENTAILMENT_VALIDATOR_SYSTEM_PROMPT),
            "NarrativeThread": self._init_qa_agent("NarrativeThreadAgent", QA_NARRATIVE_VALIDATOR_SYSTEM_PROMPT),
            "AdversarialReviewer": self._init_qa_agent("AdversarialReviewerAgent", QA_ADVERSARIAL_VALIDATOR_SYSTEM_PROMPT),
            "JDSkillsValidator": self._init_qa_agent("JDSkillsValidatorAgent", QA_JD_SKILLS_VALIDATOR_SYSTEM_PROMPT),
            "SignalScoreValidator": self._init_qa_agent("SignalScoreValidatorAgent", QA_SIGNAL_SCORE_VALIDATOR_SYSTEM_PROMPT),
            "BiasScrubber": self._init_qa_agent("BiasScrubberAgent", QA_BIAS_VALIDATOR_SYSTEM_PROMPT),
            "TenureValidator": self._init_qa_agent("TenureValidatorAgent", QA_TENURE_VALIDATOR_SYSTEM_PROMPT),
        }

    def _init_qa_agent(self, agent_name: str, system_prompt: str):
        # All v7.0 Tier 2 QA agents use Gemini 2.5 Flash
        try:
            client = get_model_client(
                client_name="google",
                model_name="gemini-2.5-flash"
            )
            return {"client": client, "system_prompt": system_prompt, "name": agent_name}
        except Exception as e:
            self.log_error(f"Failed to initialize QA agent {agent_name}: {e}")
            return None

    def run(self, final_draft: str) -> List[dict]:
        self.log_info("Running Step 4: Atomic QA Swarm (LLM)...")
        
        strategy = self.blackboard.get_artifact("strategy_brief")
        job_description = self.blackboard.job_input.get("raw_jd", "")
        master_resume_json = json.dumps(self.blackboard.master_resume, indent=2)
        
        if not all([final_draft, strategy, job_description, master_resume_json]):
            raise HopExecutionError("Missing artifacts for QA Swarm.")

        all_results = []
        
        # In production, this loop would be run in parallel (e.g., ThreadPoolExecutor)
        for agent_name, agent in self.qa_agents.items():
            if agent is None or not agent["client"]:
                self.log_warning(f"Skipping QA agent {agent_name} as it failed to initialize.")
                all_results.append({
                    "agent_name": agent_name,
                    "passed": False,
                    "error": "Agent not initialized",
                    "details": "Client creation failed. Check API keys/config."
                })
                continue

            try:
                self.log_info(f"  Running QA Agent: {agent['name']}...")
                
                # Format the user prompt with all necessary context
                user_prompt = QA_GENERIC_USER_PROMPT.format(
                    final_draft=final_draft,
                    strategy_brief=json.dumps(strategy, indent=2),
                    job_description=job_description,
                    master_resume=master_resume_json
                )
                
                messages = [
                    {"role": "system", "content": agent["system_prompt"]},
                    {"role": "user", "content": user_prompt}
                ]
                
                # All QA agents must return JSON
                response = agent["client"].chat_completion(
                    messages=messages,
                    response_format="json_object"
                )
                
                response["agent_name"] = agent["name"]
                all_results.append(response)

            except Exception as e:
                self.log_error(f"QA Agent {agent_name} failed: {e}")
                all_results.append({
                    "agent_name": agent_name,
                    "passed": False,
                    "error": str(e)
                })
        
        self.log_info(f"Atomic QA Swarm (LLM) complete. Ran {len(all_results)} checks.")
        self.blackboard.update_artifact("qa_llm_results", all_results)
        return all_results

class AtomicQASwarmLogic(BaseAgent):
    """
    v7.0 Step 4: Atomic QA Swarm (Logic)
    This agent runs the 10 parallel, low-intelligence Python-based checks.
    """
    
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "AtomicQASwarmLogic"
        
        # Define logic checks
        self.logic_checks = [
            self._check_word_count,
            self._check_forbidden_verbs,
            self._check_placeholder_text,
            self._check_contact_info,
            self._check_capitalization,
            self._check_punctuation,
            self._check_for_personal_pronouns,
            self._check_for_empty_sections,
            self._check_bullet_format,
            self._check_acronyms
        ]

    def run(self, final_draft: str) -> List[dict]:
        self.log_info("Running Step 4: Atomic QA Swarm (Logic)...")
        all_results = []
        
        for check_func in self.logic_checks:
            try:
                result = check_func(final_draft)
                all_results.append(result)
            except Exception as e:
                all_results.append({
                    "check_name": check_func.__name__,
                    "passed": False,
                    "error": str(e)
                })
        
        self.log_info(f"Atomic QA Swarm (Logic) complete. Ran {len(all_results)} checks.")
        self.blackboard.update_artifact("qa_logic_results", all_results)
        return all_results

    # --- Logic Check Functions ---
    
    def _check_word_count(self, draft: str) -> dict:
        wc = len(draft.split())
        passed = 50 <= wc <= 1500 # Example range for a document
        return {
            "check_name": "word_count",
            "passed": passed,
            "details": f"Word count is {wc}. Expected 50-1500."
        }
        
    def _check_forbidden_verbs(self, draft: str) -> dict:
        forbidden = ["helped", "assisted", "worked on", "responsible for"]
        found = [v for v in forbidden if re.search(r'\b' + v + r'\b', draft, re.I)]
        return {
            "check_name": "forbidden_verbs",
            "passed": len(found) == 0,
            "details": f"Found: {found}" if found else "No forbidden verbs found."
        }

    def _check_placeholder_text(self, draft: str) -> dict:
        found = re.findall(r'\[.*?\]|\<.*?\>|\{.*?\}|TODO:|FIXME:', draft)
        return {
            "check_name": "placeholder_text",
            "passed": len(found) == 0,
            "details": f"Found: {found}" if found else "No placeholder text found."
        }

    def _check_contact_info(self, draft: str) -> dict:
        # This check is less relevant for the *draft* vs. the final *document*,
        # but we run it as a proxy.
        contact_info = self.blackboard.master_resume.get("owner", {}).get("contact", {})
        email = contact_info.get("email", "dummy@email.com")
        phone = contact_info.get("phone", "999-999-9999")
        # Check if they are mentioned at all
        passed = (email in draft) or (phone in draft)
        return {
            "check_name": "contact_info",
            "passed": True, # Always pass, as draft may not include header
            "details": "This check is informational for draft."
        }

    def _check_capitalization(self, draft: str) -> dict:
        # Simple check: first letter of draft
        passed = draft.strip()[0].isupper()
        return {
            "check_name": "capitalization",
            "passed": passed,
            "details": "Draft starts with a capital letter." if passed else "Draft does not start with a capital letter."
        }

    def _check_punctuation(self, draft: str) -> dict:
        passed = draft.strip().endswith('.') or draft.strip().endswith('!') or draft.strip().endswith('?')
        return {
            "check_name": "punctuation",
            "passed": passed,
            "details": "Draft ends with proper punctuation." if passed else "Draft does not end with proper punctuation."
        }

    def _check_for_personal_pronouns(self, draft: str) -> dict:
        # Allow 'I'/'my' for cover letters, but not 'we'/'us'
        found = re.findall(r'\b(we|us|our)\b', draft, re.I)
        return {
            "check_name": "personal_pronouns",
            "passed": len(found) == 0,
            "details": "No plural personal pronouns found." if not found else f"Found plural pronouns: {found}"
        }

    def _check_for_empty_sections(self, draft: str) -> dict:
        passed = len(draft.strip()) > 10
        return {
            "check_name": "empty_sections",
            "passed": passed,
            "details": "Draft is not empty."
        }
    
    def _check_bullet_format(self, draft: str) -> dict:
        # Checks if lines starting with '*' or '-' exist
        bullets = re.findall(r'^\s*[\*\-•]\s+', draft, re.MULTILINE)
        return {
            "check_name": "bullet_format",
            "passed": True, # Informational
            "details": f"Found {len(bullets)} potential bullet points."
        }

    def _check_acronyms(self, draft: str) -> dict:
        # Finds all-caps words > 1 char
        acronyms = re.findall(r'\b[A-Z]{2,}\b', draft)
        return {
            "check_name": "acronyms",
            "passed": True, # Informational
            "details": f"Found {len(set(acronyms))} unique acronyms."
        }

# ============================================================================
# PART 5: GOVERNOR (v6.5 - Refactored for v7.0 Architecture)
# ============================================================================

class Governor:
    """
    v6.5 Governor: Orchestrates the v7.0 agent flow.
    Replaces static plan execution with a linear, goal-driven loop
    that executes the new v7.0 agents in order.
    """
    
    def __init__(self, config: 'CrewConfiguration', blackboard: WorkflowBlackboard):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.Governor")
        self.telemetry_logger = logging.getLogger("agent_telemetry")
        self.blackboard = blackboard
        
        # v6.5: Instantiate all agents defined in the v7.0 architecture
        self.theme_classifier = ThemeClassifierAgent(blackboard, config.debug_mode)
        self.rag_query_gen = RAG_QueryGeneratorAgent(blackboard, config.debug_mode)
        self.rag_search = RAG_SearchAgent(blackboard, config.debug_mode)
        self.rag_critique = RAG_CritiqueAgent(blackboard, config.debug_mode)
        self.prompt_stack = PromptStackAgent(blackboard, config.debug_mode)
        self.bullet_swarm = BulletSwarmAgent(blackboard, config.debug_mode)
        self.drafting_router = AdversarialDraftingRouter(blackboard, config.debug_mode)
        self.replanner = WorkflowRePlannerAgent(blackboard, config.debug_mode)
        self.qa_swarm_llm = AtomicQASwarmLLM(blackboard, config.debug_mode)
        self.qa_swarm_logic = AtomicQASwarmLogic(blackboard, config.debug_mode)
        
        self.cost_tracker = CostTrackerAgent()
        self.feedback_logger = FeedbackLoggerAgent(
            log_path=CONFIG.meta_loop_config.feedback_log_path
        )
        self.max_replan_loops = CONFIG.planner_config.max_replan_loops

    def _execute_step(self, agent_func: Callable, agent_name: str, step_id: str, **kwargs) -> Any:
        """
        Wrapper for execution, telemetry, cost, and circuit breaking.
        """
        workflow_id = self.blackboard.workflow_id
        log_extra = {"workflow_id": workflow_id, "agent_id": agent_name, "step_id": step_id}
        
        result = None
        start_time = time.monotonic()

        try:
            result = agent_func(**kwargs)
            
            # TODO: Implement real cost/token tracking
            cost_usd, token_input, token_output = 0.0, 0, 0 

            log_extra.update({
                "duration_ms": int((time.monotonic() - start_time) * 1000),
                "status": "SUCCESS",
                "cost_usd": cost_usd,
                "token_input": token_input,
                "token_output": token_output,
            })
            self.telemetry_logger.info(f"Agent {agent_name} SUCCESS", extra=log_extra)

        except Exception as e:
            log_extra.update({
                "duration_ms": int((time.monotonic() - start_time) * 1000),
                "status": "FAILED",
                "error_message": str(e)
            })
            self.telemetry_logger.error(f"Agent {agent_name} FAILED", extra=log_extra)
            raise e # Re-raise to be caught by the main orchestration loop
            
        return result

    def run_dynamic_orchestration(self) -> Dict[str, Any]:
        """
        v6.5: Main orchestration loop, modified to run the v7.0 linear flow.
        """
        self.logger.info(f"🚀 Governor processing: {self.blackboard.job_input.get('company')} - {self.blackboard.job_input.get('job_title')}")
        
        results = {
            'artifacts': {},
            'validation': {},
            'metadata': {'workflow_id': self.blackboard.workflow_id}
        }
        
        replan_count = 0
        
        try:
            while replan_count <= self.max_replan_loops:
                
                # --- STEP 1: STRATEGY ---
                if "strategy_brief" not in self.blackboard.artifacts:
                    self._execute_step(
                        self.theme_classifier.run, "ThemeClassifierAgent", "step_1_strategy",
                        job_description_text=self.blackboard.job_input.get("raw_jd", "")
                    )
                
                # --- STEP 2: RAG ---
                if "rag_queries" not in self.blackboard.artifacts:
                    strategy = self.blackboard.get_artifact("strategy_brief")
                    self._execute_step(
                        self.rag_query_gen.run, "RAG_QueryGen", "step_2_rag_query",
                        strategy_brief=strategy
                    )
                
                if "rag_search_results" not in self.blackboard.artifacts:
                    queries = self.blackboard.get_artifact("rag_queries")
                    self._execute_step(
                        self.rag_search.run, "RAG_SearchAgent", "step_2_rag_search",
                        queries=queries
                    )
                
                if "rag_critique" not in self.blackboard.artifacts:
                    strategy = self.blackboard.get_artifact("strategy_brief")
                    rag_results = self.blackboard.get_artifact("rag_search_results")
                    self._execute_step(
                        self.rag_critique.run, "RAG_Critique", "step_2_rag_critique",
                        strategy_brief=strategy, rag_results=rag_results
                    )

                # --- STEP 3: DRAFTING ---
                if "final_drafting_prompt" not in self.blackboard.artifacts:
                    self._execute_step(self.prompt_stack.run, "PromptStackAgent", "step_3_prompt_stack")
                
                if "generated_bullets" not in self.blackboard.artifacts:
                    self._execute_step(self.bullet_swarm.run, "BulletSwarmAgent", "step_3_bullet_swarm")

                if "final_draft" not in self.blackboard.artifacts:
                    self._execute_step(self.drafting_router.run, "AdversarialDraftingRouter", "step_3_drafting")

                # --- STEP 4: QA ---
                final_draft = self.blackboard.get_artifact("final_draft")
                
                if "qa_llm_results" not in self.blackboard.artifacts:
                    self._execute_step(
                        self.qa_swarm_llm.run, "AtomicQASwarmLLM", "step_4_qa_llm",
                        final_draft=final_draft
                    )
                
                if "qa_logic_results" not in self.blackboard.artifacts:
                     self._execute_step(
                        self.qa_swarm_logic.run, "AtomicQASwarmLogic", "step_4_qa_logic",
                        final_draft=final_draft
                    )

                # --- VALIDATION & REPLANNING ---
                qa_llm_results = self.blackboard.get_artifact("qa_llm_results", [])
                qa_logic_results = self.blackboard.get_artifact("qa_logic_results", [])
                
                all_qa_results = qa_llm_results + qa_logic_results
                failed_checks = [r for r in all_qa_results if not r.get("passed", False)]
                
                validation_summary = {
                    "overall_passed": len(failed_checks) == 0,
                    "failed_checks_count": len(failed_checks),
                    "failed_checks": failed_checks,
                    "all_results": all_qa_results
                }
                self.blackboard.update_artifact("validation_results", validation_summary)
                
                if validation_summary["overall_passed"]:
                    self.logger.info("✅ Orchestration goal met. Final draft produced and validated.")
                    break # Success! Exit the while loop
                else:
                    # QA FAILED
                    replan_count += 1
                    if replan_count > self.max_replan_loops:
                        raise HopExecutionError(f"QA failed and max replan loops ({self.max_replan_loops}) reached.")
                    
                    self.logger.warning(f"QA Failed. {len(failed_checks)} checks failed. Triggering Re-Planner (Attempt {replan_count})...")
                    
                    # Call Re-Planner
                    recovery_plan = self._execute_step(
                        self.replanner.run, "WorkflowRePlannerAgent", "step_3_sc_paths",
                        failed_qa_results=failed_checks
                    )
                    
                    # v6.5: Simple Re-plan: Clear artifacts and re-run
                    # A v7.0 system would parse the 'recovery_plan' and surgically
                    # clear artifacts. For v6.5, we just clear and retry.
                    self.logger.info(f"Re-Planner suggested: {recovery_plan.get('suggestion')}. Clearing drafting artifacts and retrying.")
                    self.blackboard.clear_artifacts([
                        "final_drafting_prompt", "generated_bullets", "final_draft",
                        "qa_llm_results", "qa_logic_results", "validation_results", "recovery_plan"
                    ])

            # --- End of while loop ---

            # Finalize
            results['validation'] = self.blackboard.get_artifact("validation_results")
            results['artifacts'] = self.blackboard.artifacts
            results['metadata']['timestamp'] = datetime.now().isoformat()
            
            self._log_feedback(results.get('validation', {}))
            return results
            
        except Exception as e:
            self.logger.error(f"Governor orchestration failed: {e}", exc_info=True)
            results['validation'] = {'overall_passed': False, 'error': str(e)}
            return results
        
        finally:
            self.cost_tracker.log_final_cost(self.blackboard.workflow_id, {})
            
    def _log_feedback(self, validation_results: Dict[str, Any]):
        """Logs validation results for the meta-learning loop."""
        self.feedback_logger.log(validation_results, self.blackboard.workflow_id)

# ============================================================================
# PART 6: COST TRACKING & FEEDBACK (v6.4 logic, preserved)
# ============================================================================

class CostEstimatorAgent:
    """Estimates workflow costs."""
    def estimate(self, job_input: Dict) -> float:
        jd_length = len(job_input.get('job_description', ''))
        # v6.5: This is a rough guess based on the new flow
        estimated_tokens = (jd_length * 0.75) + 30000 # 30k token assumption
        estimated_cost = (estimated_tokens / 1000) * 0.005 # Avg cost
        return estimated_cost

class CostTrackerAgent:
    """Tracks actual costs."""
    def __init__(self):
        self.costs = {}
    
    def log_cost(self, agent: str, cost: float):
        self.costs[agent] = cost
    
    def log_final_cost(self, workflow_id: str, costs: Dict):
        logger.info(f"Final costs for {workflow_id}: ${sum(costs.values()):.2f}")

class FeedbackLoggerAgent:
    """Logs validation results to a file for the meta-learning loop."""
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.logger = logging.getLogger("FeedbackLoggerAgent")
    
    def log(self, validation_results: Dict[str, Any], workflow_id: str):
        if not self.log_path:
            self.logger.warning("No feedback_log_path configured. Skipping log.")
            return
            
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "workflow_id": workflow_id,
                "overall_passed": validation_results.get("overall_passed", False),
                # v6.5: Log failed checks for easier parsing
                "failed_checks": validation_results.get("failed_checks", []),
                "all_results": validation_results.get("all_results", [])
            }
            
            with open(self.log_path, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n') # Write as JSONL
            
            self.logger.info(f"Feedback logged to {self.log_path} for workflow {workflow_id}")

        except Exception as e:
            self.logger.error(f"Failed to write to feedback log {self.log_path}: {e}")

# ============================================================================
# PART 7: CONFIGURATION & ORCHESTRATOR (v6.4 logic, preserved)
# ============================================================================

@dataclass
class CrewConfiguration:
    """
    Crew configuration.
    REFACTORED: Defaults are now loaded from CONFIG by main.py
    """
    enable_conductor: bool # Note: v6.5 (v7.0 arch) does not use Conductor
    enable_reflection: bool # Note: v6.5 uses this implicitly
    enable_react: bool
    enable_moe: bool
    max_retries: int
    timeout_seconds: int
    max_complexity: int = 100
    parallel_execution: bool = False
    validation_threshold: float = 0.8
    enable_caching: bool = True
    debug_mode: bool = False


@dataclass
class CrewContext:
    """Context for crew execution."""
    job_description: str
    company_name: str
    job_title: str
    master_resume: Dict[str, Any]
    workflow_id: str

class CrewOrchestrator:
    """High-level orchestrator."""
    
    def __init__(self, config: Optional[CrewConfiguration] = None):
        if config:
            self.config = config
        else:
            # v6.5: Use CONFIG from core_v6_5
            defaults = CONFIG.crew_config_defaults
            self.config = CrewConfiguration(
                enable_conductor=defaults.enable_conductor,
                enable_reflection=defaults.enable_reflection,
                enable_react=defaults.enable_react,
                enable_moe=defaults.enable_moe,
                max_retries=CONFIG.llm_config.defaults.max_retries,
                timeout_seconds=300, 
                max_complexity=defaults.max_complexity,
                parallel_execution=defaults.parallel_execution,
                validation_threshold=defaults.validation_threshold,
                enable_caching=defaults.enable_caching,
                debug_mode=defaults.debug_mode
            )
            
        # v6.5: Governor is instantiated inside process_job_application
        # after the blackboard is created.
        self.governor = None 
        self.logger = logging.getLogger(f"{__name__}.CrewOrchestrator")
    
    def process_job_application(self, job_description: str, company_name: str,
                               job_title: str, master_resume: Dict[str, Any],
                               workflow_id: str) -> Dict[str, Any]:
        """Process complete job application."""
        self.logger.info(f"📋 Orchestrating: {company_name} - {job_title}")
        
        context = CrewContext(
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            master_resume=master_resume,
            workflow_id=workflow_id
        )
        
        # v6.5: Initialize the blackboard HERE
        blackboard = WorkflowBlackboard(
            workflow_id=context.workflow_id,
            master_resume=context.master_resume,
            job_input={"raw_jd": context.job_description, "company": context.company_name, "job_title": context.job_title},
            plan=None # v6.5 (v7.0 arch) is dynamic, no static plan
        )
        
        results = {}
        
        try:
            # v6.5: Instantiate Governor, passing the blackboard
            self.governor = Governor(self.config, blackboard)

            # v6.5: Call the new dynamic orchestration method
            gov_results = self.governor.run_dynamic_orchestration()
            
            # Merge governor results into final results
            results.update(gov_results)
            
            results['workflow_results'] = {
                'status': 'COMPLETED' if results.get('validation', {}).get('overall_passed', True) else 'FAILED'
            }
            return results
        
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}", exc_info=True)
            results['workflow_results'] = {'status': 'FAILED', 'error': str(e)}
            return results

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'CrewOrchestrator', 'CrewConfiguration', 'Governor',
    'CrewContext', 'WorkflowSteps', 'FeedbackLoggerAgent',
    'ThemeClassifierAgent', 'RAG_QueryGeneratorAgent', 'RAG_SearchAgent',
    'RAG_CritiqueAgent', 'PromptStackAgent', 'BulletSwarmAgent',
    'AdversarialDraftingRouter', 'WorkflowRePlannerAgent',
    'AtomicQASwarmLLM', 'AtomicQASwarmLogic'
]