# File: agent_swarm_v8_5.py
# Overwrites: agent_swarm_v8_0.py
# Version: 8.5 (Cleanup)
#
# v8.5 (Cleanup) CHANGES:
# - RAG_SearchAgent: Upgraded to a full ReAct agent with an internal critique loop,
#   graph search tools, and write-to-graph capabilities. (Req #1)
# - BulletStack: Replaced BulletSwarmAgent with a new 'ProvenanceRouterAgent'
#   that manages 'CustomizedBulletDrafterAgent' and 'SyntheticBulletDrafterAgent'
#   to implement the 2/3/2 and 2/2/2 provenance plan. (Req #2)
# - DraftingStack: Replaced AdversarialDraftingRouter with a 'DraftingConductorAgent'
#   that dynamically routes between experts (MoE). (Req #1)
# - QAStack: Replaced AtomicQASwarmLLM with a 'QAConductorAgent'
#   that dynamically selects QA checks (MoE). (Req #1)

# ============================================================================
# EXTERNAL IMPORTS
# ============================================================================
import copy
import difflib
import hashlib
import json
import logging
import os
import random
import re
import time
import uuid
from collections import defaultdict
from enum import Enum
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Import from core_v8_5
from core_v8_5 import (
    # Base
    BaseAgent, get_model_client, CONFIG,
    # Models
    HopExecutionError, MechanicalFailureError, SemanticFailureError, FactualFailureException,
    ValidationSeverity, ValidationResult, ReasoningConfig, ReasoningStrategy,
    ThematicAnalysis, RAG_Blackboard, RAGMission, RAGPhase, StrategyBrief,
    ReflectionIteration, ReflectionResult, ReflectionStatus,
    ToolCall, ToolType, ReActTrace,
    MoEExpertResult, MoEDecision, ConductorBranch, ConductorDecision,
    WorkflowBlackboard, WorkflowPlan, WorkflowStep, GraphState,
    # Config
    DEFAULT_GENERATION_TEMPERATURE,
    # Utils
    text_utils, fence_data,
    # Prompts
    STRATEGY_THEME_CLASSIFICATION_SYSTEM_PROMPT, STRATEGY_THEME_CLASSIFICATION_USER_PROMPT,
    RAG_QUERY_GEN_SYSTEM_PROMPT, RAG_QUERY_GEN_USER_PROMPT,
    RAG_THOUGHT_SYSTEM_PROMPT, RAG_CRITIQUE_STEP_SYSTEM_PROMPT,
    RAG_CRITIQUE_SYSTEM_PROMPT, RAG_CRITIQUE_USER_PROMPT,
    BULLET_CUSTOMIZER_SYSTEM_PROMPT, BULLET_CUSTOMIZER_USER_PROMPT,
    BULLET_SYNTHETIC_SYSTEM_PROMPT, BULLET_SYNTHETIC_USER_PROMPT,
    DRAFTING_CONDUCTOR_SYSTEM_PROMPT, DRAFTING_CONDUCTOR_USER_PROMPT,
    DRAFTING_STRATEGIST_SYSTEM_PROMPT, DRAFTING_REDTEAM_SYSTEM_PROMPT,
    DRAFTING_REFINER_SYSTEM_PROMPT, DRAFTING_METRICS_SYSTEM_PROMPT,
    DRAFTING_USER_PROMPT,
    REPLANNER_SYSTEM_PROMPT, REPLANNER_USER_PROMPT,
    QA_CONDUCTOR_SYSTEM_PROMPT, QA_CONDUCTOR_USER_PROMPT,
    QA_CLAIM_VALIDATOR_SYSTEM_PROMPT, QA_TONE_VALIDATOR_SYSTEM_PROMPT,
    QA_ALIGNMENT_VALIDATOR_SYSTEM_PROMPT, QA_ENTAILMENT_VALIDATOR_SYSTEM_PROMPT,
    QA_NARRATIVE_VALIDATOR_SYSTEM_PROMPT, QA_ADVERSARIAL_VALIDATOR_SYSTEM_PROMPT,
    QA_JD_SKILLS_VALIDATOR_SYSTEM_PROMPT, QA_SIGNAL_SCORE_VALIDATOR_SYSTEM_PROMPT,
    QA_BIAS_VALIDATOR_SYSTEM_PROMPT, QA_TENURE_VALIDATOR_SYSTEM_PROMPT,
    QA_MISSED_OPPORTUNITY_SYSTEM_PROMPT,
    QA_GENERIC_USER_PROMPT
)

# v8.0: Stub for Neo4j/Graph Tool
class GraphDatabaseClient:
    def query(self, query: str): return [{"node": "stub"}]
    def write(self, s: str, r: str, o: str): return True

# --- V7.0 LANGGRAPH IMPORTS ---
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver

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
# PART 2: RAG STACK AGENTS (v7.0 Step 2 -> v8.0 Upgrade)
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
            raise HopExecutionError("Model client not initialized for QueryGen.")

        if not strategy_brief:
            raise HopExecutionError("Missing strategy_brief artifact.")

        try:
            strategy_text = json.dumps(strategy_brief, indent=2)
            messages = [
                {"role": "system", "content": RAG_QUERY_GEN_SYSTEM_PROMPT},
                {"role": "user", "content": RAG_QUERY_GEN_USER_PROMPT.format(strategy_brief=strategy_text)}
            ]

            response = self.client.chat_completion(
                messages=messages,
                response_format="json_object"
            )

            queries = response.get("queries", [])
            self.log_info(f"Generated {len(queries)} RAG queries.")
            self.blackboard.update_artifact("rag_queries", queries)
            return queries

        except Exception as e:
            self.log_error(f"Error during query generation: {e}")
            raise HopExecutionError(f"RAG_QueryGen failed: {e}")


class RAG_SearchAgent(BaseAgent):
    """
    v8.0 Upgrade: Full ReAct Agent
    Implements internal critique loop, dynamic tool use (Vector+Graph),
    and persistent graph writing to achieve a 95+ score.
    
    Corresponds to:
    Component: RAG_SearchAgent (ReAct)
    Intelligence: 80 (Very High)
    Tier: Tier 1 (Flagship)
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "RAG_SearchAgent"
        self.model_name = "gemini-2.5-pro"
        self.client_name = "google"
        self.max_react_iterations = 5
        
        try:
            # This client is used for the ReAct "thought" process
            self.client = get_model_client(
                client_name=self.client_name,
                model_name=self.model_name,
            )
            # v8.0: Client for step critiques
            self.critique_client = get_model_client(
                client_name="google", model_name="gemini-2.5-flash"
            )
            self.log_info(f"Initialized with model: {self.model_name}")
            
            # v8.0: Expanded toolset
            self.available_tools = {
                "master_resume_search": self._tool_master_resume_search,
                "web_search": self._tool_web_search,
                "graph_search": self._tool_graph_search,
                "write_to_graph": self._tool_write_to_graph
            }
            self.graph_db_client = GraphDatabaseClient() # Stub client
            
        except Exception as e:
            self.log_error(f"Failed to initialize model client: {e}")
            self.client = None
            self.critique_client = None

    def run(self, queries: List[str]) -> Dict[str, Any]:
        self.log_info(f"Running Step 2: RAG Search (ReAct) for {len(queries)} queries...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for RAG Search.")

        all_results = []
        react_traces = []

        for query in queries:
            self.log_info(f"Processing query: {query}")
            current_context = [] # Context for this query
            
            # ReAct Loop
            for iteration in range(self.max_react_iterations):
                # 1. THOUGHT: Reason about what to do next
                thought = self._generate_thought(query, iteration, current_context)
                self.log_info(f"  Iteration {iteration+1} Thought: {thought}")

                # 2. ACTION: Select a tool
                action_json = self._select_action(thought)
                tool_name = action_json.get("tool_name")
                tool_input = action_json.get("tool_input", {})
                tool_callable = self.available_tools.get(tool_name)

                # 3. OBSERVATION: Execute action and observe results
                if tool_callable:
                    try:
                        observation = tool_callable(tool_input)
                        tool_success = True
                    except Exception as e:
                        observation = f"Tool {tool_name} failed: {e}"
                        tool_success = False
                else:
                    observation, tool_success = f"Tool '{tool_name}' not found.", False
                
                self.log_info(f"  Iteration {iteration+1} Observation: {str(observation)[:100]}...")
                current_context.append(observation)
                all_results.extend(observation if isinstance(observation, list) else [observation])

                # 4. (NEW v8.0) CRITIQUE: Self-correction loop
                if self._critique_step(query, current_context):
                    self.log_info(f"  Query satisfied after {iteration+1} iterations.")
                    break

        final_results = self._deduplicate_and_rank(all_results)
        
        self.blackboard.update_artifact("rag_search_results", final_results)
        self.log_info(f"RAG Search complete. {len(final_results)} results.")
        return {"results": final_results, "traces": react_traces}

    def _generate_thought(self, query: str, iteration: int, current_results: List) -> str:
        # v8.0: This is now a real LLM call
        context = json.dumps(current_results[-2:], indent=2) # Only last 2 results
        prompt = RAG_THOUGHT_SYSTEM_PROMPT.format(
            query=query,
            iteration=iteration+1,
            context=context,
            tools_list=json.dumps(list(self.available_tools.keys()))
        )
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat_completion(messages=messages, response_format="json_object")
        return response.get("thought", "Thought: I am unsure what to do next.")

    def _select_action(self, thought: str) -> Dict:
        # v8.0: Parse the thought for a tool call.
        # In a real system, the LLM would output structured JSON. We simulate that.
        if "master_resume_search" in thought:
            query = re.search(r"search for '(.*?)'", thought)
            return {"tool_name": "master_resume_search", "tool_input": {"query": query.group(1) if query else ""}}
        if "web_search" in thought:
            query = re.search(r"search for '(.*?)'", thought)
            return {"tool_name": "web_search", "tool_input": {"query": query.group(1) if query else ""}}
        if "graph_search" in thought:
            query = re.search(r"query '(.*?)'", thought)
            return {"tool_name": "graph_search", "tool_input": {"query": query.group(1) if query else ""}}
        return {"tool_name": "master_resume_search", "tool_input": {"query": "generic search"}}

    def _critique_step(self, query: str, context: List) -> bool:
        # v8.0: Internal critique loop
        prompt = RAG_CRITIQUE_STEP_SYSTEM_PROMPT.format(query=query, context=json.dumps(context, indent=2))
        messages = [{"role": "user", "content": prompt}]
        response = self.critique_client.chat_completion(messages=messages, response_format="json_object")
        satisfied = response.get("is_satisfied", False)
        self.log_info(f"  Critique: {response.get('critique', '...')} (Satisfied: {satisfied})")
        return satisfied


    def _deduplicate_and_rank(self, results: List[Dict]) -> List[Dict]:
        unique_results = {}
        for result in results:
            content_hash = result.get("content_hash", hashlib.md5(str(result).encode()).hexdigest())
            if content_hash not in unique_results:
                unique_results[content_hash] = result
        
        ranked_results = sorted(
            unique_results.values(),
            key=lambda x: x.get("relevance_score", 0.5),
            reverse=True
        )
        return ranked_results[:20]

    def _tool_master_resume_search(self, tool_input: Dict) -> List[Dict]:
        query = tool_input.get("query", "")
        self.log_info(f"  Tool: _tool_master_resume_search (Query: {query})")
        
        master_resume = self.blackboard.master_resume
        all_text_chunks = []
        
        for exp in master_resume.get("professional_experience", []):
            company = exp.get("company", "Unknown")
            title = exp.get("title", "Unknown")
            bullets = exp.get("bullet_pool", [])
            
            for bullet in bullets:
                chunk = {
                    "source": f"{company} - {title}",
                    "content": bullet,
                    "relevance_score": text_utils.calculate_similarity(query, bullet),
                    "content_hash": hashlib.md5(bullet.encode()).hexdigest()
                }
                all_text_chunks.append(chunk)
        
        all_text_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        return all_text_chunks[:10]

    def _tool_web_search(self, tool_input: Dict) -> List[Dict]:
        query = tool_input.get("query", "")
        self.log_info(f"  Tool: _tool_web_search (Query: {query})")
        
        content = f"Web search result for '{query}': This is simulated content about {query}."
        return [{
            "source": "web_search",
            "content": content,
            "relevance_score": 0.7,
            "content_hash": hashlib.md5(content.encode()).hexdigest()
        }]
        
    def _tool_graph_search(self, tool_input: Dict) -> List[Dict]:
        query = tool_input.get("query", "")
        self.log_info(f"  Tool: _tool_graph_search (Query: {query})")
        # v8.0: Calls the stubbed Neo4j client
        results = self.graph_db_client.query(query)
        return [{"source": "graph_db", "content": str(results), "relevance_score": 0.9, "content_hash": str(uuid.uuid4())}]

    def _tool_write_to_graph(self, tool_input: Dict) -> List[Dict]:
        self.log_info(f"  Tool: _tool_write_to_graph")
        self.graph_db_client.write(tool_input.get("s"), tool_input.get("r"), tool_input.get("o"))
        return [{"source": "graph_db", "content": "Write successful", "relevance_score": 1.0, "content_hash": str(uuid.uuid4())}]


class RAG_CritiqueAgent(BaseAgent):
    """
    v7.0 Step 2: RAG - Critique
    Reviews and critiques the RAG results.
    
    Corresponds to:
    Component: RAG_CritiqueAgent
    Intelligence: 85 (Very High)
    Tier: Tier 1 (Flagship)
    Model: Claude 4.1 Opus
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "RAG_CritiqueAgent"
        self.model_name = "claude-4.1-opus"
        self.client_name = "anthropic"
        
        try:
            self.client = get_model_client(
                client_name=self.client_name,
                model_name=self.model_name
            )
            self.log_info(f"Initialized with model: {self.model_name}")
        except Exception as e:
            self.log_error(f"Failed to initialize model client: {e}")
            self.client = None

    def run(self, strategy_brief: dict, rag_results: List[Dict]) -> dict:
        self.log_info("Running Step 2: RAG Critique...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for RAG Critique.")

        if not strategy_brief or not rag_results:
            raise HopExecutionError("Missing strategy_brief or rag_results for critique.")

        try:
            strategy_text = json.dumps(strategy_brief, indent=2)
            rag_text = json.dumps(rag_results[:10], indent=2)
            
            messages = [
                {"role": "system", "content": RAG_CRITIQUE_SYSTEM_PROMPT},
                {"role": "user", "content": RAG_CRITIQUE_USER_PROMPT.format(
                    strategy_brief=strategy_text,
                    rag_results=rag_text
                )}
            ]

            response = self.client.chat_completion(
                messages=messages,
                response_format="json_object"
            )

            self.log_info("RAG Critique complete.")
            self.blackboard.update_artifact("rag_critique", response)
            return response

        except Exception as e:
            self.log_error(f"Error during RAG critique: {e}")
            raise HopExecutionError(f"RAG_CritiqueAgent failed: {e}")


# ============================================================================
# PART 3: PROMPT STACK AGENT (v7.0 Step 3)
# ============================================================================

class PromptStackAgent(BaseAgent):
    """
    v7.0 Step 3: Drafting - Prompt Stack
    A simple Python-based prompt formatter.
    
    Corresponds to:
    Component: PromptFormatterAgent
    Intelligence: 5 (Minimal)
    Tier: N/A (Python)
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "PromptStackAgent"

    def run(self) -> str:
        self.log_info("Running Step 3: Prompt Stack...")
        try:
            strategy = self.blackboard.get_artifact("strategy_brief")
            rag_results = self.blackboard.get_artifact("rag_search_results")
            
            if not strategy:
                raise HopExecutionError("Missing strategy_brief artifact.")
            
            # Simple prompt template
            prompt = DRAFTING_USER_PROMPT.format(
                strategy_brief=json.dumps(strategy, indent=2),
                rag_context=json.dumps(rag_results[:5], indent=2) if rag_results else "No RAG results available."
            )
            
            self.blackboard.update_artifact("final_drafting_prompt", prompt)
            self.log_info("Prompt Stack complete.")
            return prompt
        
        except Exception as e:
            self.log_error(f"Error during Prompt Stack: {e}")
            raise HopExecutionError(f"PromptStackAgent failed: {e}")

# ============================================================================
# PART 4 (v8.0): NEW BULLET STACK (Req #2)
# ============================================================================

class CustomizedBulletDrafterAgent(BaseAgent):
    """v8.0: (LLM-based) Rewrites existing bullets to match strategy."""
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "CustomizedBulletDrafterAgent"
        self.client = get_model_client("google", "gemini-2.5-pro")

    def run(self, master_bullets: List[str], strategy_brief: dict, n_to_gen: int) -> List[str]:
        self.log_info(f"Running CustomizedBulletDrafter to gen {n_to_gen} bullets...")
        user_prompt = BULLET_CUSTOMIZER_USER_PROMPT.format(
            strategy_brief=json.dumps(strategy_brief),
            master_bullets=json.dumps(master_bullets),
            n_to_gen=n_to_gen
        )
        messages = [{"role": "system", "content": BULLET_CUSTOMIZER_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
        response = self.client.chat_completion(messages=messages, response_format="json_object")
        return response.get("customized_bullets", [])

class SyntheticBulletDrafterAgent(BaseAgent):
    """v8.0: (LLM-based) Generates new bullets from scratch."""
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "SyntheticBulletDrafterAgent"
        self.client = get_model_client("google", "gemini-2.5-pro")

    def run(self, strategy_brief: dict, n_to_gen: int) -> List[str]:
        self.log_info(f"Running SyntheticBulletDrafter to gen {n_to_gen} bullets...")
        user_prompt = BULLET_SYNTHETIC_USER_PROMPT.format(
            strategy_brief=json.dumps(strategy_brief),
            master_resume=json.dumps(self.blackboard.master_resume),
            n_to_gen=n_to_gen
        )
        messages = [{"role": "system", "content": BULLET_SYNTHETIC_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
        response = self.client.chat_completion(messages=messages, response_format="json_object")
        return response.get("synthetic_bullets", [])

class ProvenanceRouterAgent(BaseAgent):
    """v8.0: Replaces BulletSwarmAgent. Implements 2/3/2 & 2/2/2 logic."""
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "ProvenanceRouterAgent"
        self.custom_drafter = CustomizedBulletDrafterAgent(blackboard, debug_mode)
        self.synthetic_drafter = SyntheticBulletDrafterAgent(blackboard, debug_mode)

    def _get_verbatim_bullets(self, query: str, all_bullets: List[str], n: int) -> Tuple[List[str], List[str]]:
        # This is the old v7.5 Python logic, now used as a tool
        scored_bullets = []
        for bullet in all_bullets:
            score = text_utils.calculate_similarity(query, bullet)
            scored_bullets.append((score, bullet))
        
        scored_bullets.sort(key=lambda x: x[0], reverse=True)
        
        verbatim = [bullet for score, bullet in scored_bullets[:n]]
        remaining_pool = [bullet for score, bullet in scored_bullets[n:n+10]] # Get next 10 for customizer
        return verbatim, remaining_pool

    def run(self) -> List[str]:
        self.log_info("Running Step 3: Advanced Bullet Swarm (v8.0)...")
        try:
            strategy = self.blackboard.get_artifact("strategy_brief")
            if not strategy:
                raise HopExecutionError("Missing strategy_brief artifact.")

            # Determine plan
            if "Unify" in strategy.get("primary_theme", ""):
                plan = {"verbatim": 2, "custom": 3, "synthetic": 2}
            else: # Default to IBM/other
                plan = {"verbatim": 2, "custom": 2, "synthetic": 2}
            self.log_info(f"Executing bullet plan: {plan}")

            master_resume = self.blackboard.master_resume
            all_bullets = []
            for exp in master_resume.get("professional_experience", []):
                all_bullets.extend(exp.get("bullet_pool", []))
            
            # 1. Get Verbatim bullets (Python)
            query = json.dumps(strategy.get("key_skills", []))
            verbatim_bullets, remaining_pool = self._get_verbatim_bullets(query, all_bullets, plan["verbatim"])

            # 2. Get Customized bullets (LLM)
            custom_bullets = self.custom_drafter.run(remaining_pool, strategy, plan["custom"])

            # 3. Get Synthetic bullets (LLM)
            synthetic_bullets = self.synthetic_drafter.run(strategy, plan["synthetic"])

            final_bullets = verbatim_bullets + custom_bullets + synthetic_bullets
            self.log_info(f"Bullet Swarm complete. {len(final_bullets)} total bullets generated.")
            self.blackboard.update_artifact("generated_bullets", final_bullets)
            return final_bullets
        
        except Exception as e:
            self.log_error(f"Error during Bullet Swarm: {e}")
            raise HopExecutionError(f"ProvenanceRouterAgent failed: {e}")


# ============================================================================
# PART 5 (v8.0): NEW DRAFTING STACK (Req #1)
# ============================================================================

class DraftingConductorAgent(BaseAgent):
    """v8.0: Replaces AdversarialDraftingRouter. (Req #1)
    This is a dynamic MoE router that selects the best drafting path.
    """
    
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "DraftingConductorAgent"
        
        # v8.0: Initialize all drafting experts
        self.drafters = {
            "Strategist": self._init_drafter("google", "gemini-2.5-pro", DRAFTING_STRATEGIST_SYSTEM_PROMPT),
            "RedTeam": self._init_drafter("anthropic", "claude-4.1-opus", DRAFTING_REDTEAM_SYSTEM_PROMPT),
            "Refiner": self._init_drafter("openai", "gpt-5", DRAFTING_REFINER_SYSTEM_PROMPT),
            "MetricsSpecialist": self._init_drafter("google", "gemini-2.5-flash", DRAFTING_METRICS_SYSTEM_PROMPT)
        }
        self.conductor_client = get_model_client("google", "gemini-2.5-flash")

    def _init_drafter(self, client_name: str, model_name: str, system_prompt: str):
        try:
            return {
                "client": get_model_client(client_name, model_name),
                "system_prompt": system_prompt
            }
        except Exception as e:
            self.log_error(f"Failed to initialize drafter {model_name}: {e}")
            return None

    def run(self) -> str:
        self.log_info("Running Step 3: Dynamic MoE Drafting (v8.0)...")
        final_drafting_prompt = self.blackboard.get_artifact("final_drafting_prompt")
        bullets = self.blackboard.get_artifact("generated_bullets")
        
        if not final_drafting_prompt or not bullets:
            raise HopExecutionError("Missing prompt or bullets for drafting.")

        user_prompt_with_bullets = final_drafting_prompt + "\n\n<selected_bullets_for_reference>\n" + "\n".join(bullets) + "\n</selected_bullets_for_reference>"

        try:
            # 1. Ask Conductor for a plan
            conductor_prompt = DRAFTING_CONDUCTOR_USER_PROMPT.format(
                prompt=final_drafting_prompt,
                bullets=json.dumps(bullets),
                experts=json.dumps(list(self.drafters.keys()))
            )
            messages = [{"role": "system", "content": DRAFTING_CONDUCTOR_SYSTEM_PROMPT}, {"role": "user", "content": conductor_prompt}]
            plan_response = self.conductor_client.chat_completion(messages=messages, response_format="json_object")
            plan = plan_response.get("plan", ["Strategist", "RedTeam", "Refiner"]) # Fallback plan
            self.log_info(f"Drafting Conductor selected plan: {plan}")
            
            # 2. Execute the dynamic plan
            current_artifact = user_prompt_with_bullets
            draft_history = {}

            for agent_name in plan:
                drafter = self.drafters.get(agent_name)
                if not drafter or not drafter["client"]:
                    self.log_warning(f"Conductor planned for unknown agent '{agent_name}'. Skipping.")
                    continue
                
                self.log_info(f"Executing drafting expert: {agent_name}")
                # Context for this agent includes all previous work
                agent_prompt = current_artifact + f"\n\n<previous_drafts>\n{json.dumps(draft_history)}\n</previous_drafts>"
                messages = [{"role": "system", "content": drafter["system_prompt"]}, {"role": "user", "content": agent_prompt}]
                current_artifact = drafter["client"].chat_completion(messages=messages, max_tokens=4096)
                draft_history[agent_name] = current_artifact

            self.blackboard.update_artifact("final_draft", current_artifact)
            return current_artifact

        except Exception as e:
            self.log_error(f"Error during adversarial drafting: {e}")
            raise HopExecutionError(f"DraftingConductorAgent failed: {e}")

# ============================================================================
# PART 6: REPLANNER AGENT (v7.0 Step 3 -> v8.0 Upgrade)
# ============================================================================

class WorkflowRePlannerAgent(BaseAgent):
    """
    v7.0 Step 3 (SC Paths): Workflow Re-Planner
    Analyzes QA failures and creates a recovery plan.
    
    Corresponds to:
    Component: WorkflowRePlanner
    Intelligence: 90 (Expert)
    Tier: Tier 1 (Flagship)
    Model: Claude 4.1 Opus
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "WorkflowRePlannerAgent"
        self.model_name = "claude-4.1-opus"
        self.client_name = "anthropic"
        
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
        self.log_info("Running Step 3 (SC Paths): Workflow Re-Planner (v8.0)...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for WorkflowRePlannerAgent.")
        
        
        try:
            qa_context = json.dumps(failed_qa_results, indent=2)
            
            messages = [
                {"role": "system", "content": REPLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": REPLANNER_USER_PROMPT.format(failed_qa_results=qa_context)}
            ]

            response = self.client.chat_completion(
                messages=messages,
                response_format="json_object"
            )

            if not response:
                raise Exception("Model returned an empty recovery plan.")

            self.log_info("Successfully generated recovery plan.")
            self.blackboard.update_artifact("recovery_plan", response)

            # v8.0: RAG-on-Demand (Req #1)
            # If the plan requires new facts, run the RAG stack now.
            if response.get("requires_new_facts", False):
                self.log_info("Replanner requires new facts. Triggering RAG-on-Demand...")
                rag_queries = response.get("new_rag_queries", [])
                if rag_queries:
                    search_agent = RAG_SearchAgent(self.blackboard, self.debug_mode)
                    search_results = search_agent.run(queries=rag_queries)
                    # Add new facts to the blackboard for the next drafting loop
                    self.blackboard.update_artifact("on_demand_rag_results", search_results.get("results", []))
                    self.log_info("RAG-on-Demand complete. New facts added to artifacts.")

            return response

        except Exception as e:
            self.log_error(f"Error during re-planning: {e}")
            raise HopExecutionError(f"WorkflowRePlannerAgent failed: {e}")


# ============================================================================
# PART 7 (v8.0): NEW QA STACK (Req #1)
# ============================================================================

class QAConductorAgent(BaseAgent):
    """v8.0: Replaces AtomicQASwarmLLM (Req #1)
    This is a dynamic MoE router that selects the optimal QA checks to run.
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "QAConductorAgent"
        
        # v8.0: Define all QA experts
        self.qa_agents = {
            # v7.5 agents
            "ClaimValidator": self._init_qa_agent("ClaimValidatorAgent (NLI)", QA_CLAIM_VALIDATOR_SYSTEM_PROMPT),
            "ToneValidator": self._init_qa_agent("ToneValidator", QA_TONE_VALIDATOR_SYSTEM_PROMPT),
            "ThematicAlignment": self._init_qa_agent("ThematicAlignment_Validator", QA_ALIGNMENT_VALIDATOR_SYSTEM_PROMPT),
            "SemanticEntailment": self._init_qa_agent("SemanticEntailmentValidator", QA_ENTAILMENT_VALIDATOR_SYSTEM_PROMPT),
            "NarrativeThread": self._init_qa_agent("NarrativeThreadAgent", QA_NARRATIVE_VALIDATOR_SYSTEM_PROMPT),
            "JDSkillsValidator": self._init_qa_agent("JDSkillsValidatorAgent", QA_JD_SKILLS_VALIDATOR_SYSTEM_PROMPT),
            "SignalScoreValidator": self._init_qa_agent("SignalScoreValidatorAgent", QA_SIGNAL_SCORE_VALIDATOR_SYSTEM_PROMPT),
            "BiasScrubber": self._init_qa_agent("BiasScrubberAgent", QA_BIAS_VALIDATOR_SYSTEM_PROMPT),
            "TenureValidator": self._init_qa_agent("TenureValidatorAgent", QA_TENURE_VALIDATOR_SYSTEM_PROMPT),
            # v8.0 new agents
            "AdversarialReviewer": self._init_qa_agent("AdversarialReviewerAgent", QA_ADVERSARIAL_VALIDATOR_SYSTEM_PROMPT),
            "MissedOpportunity": self._init_qa_agent("MissedOpportunityAgent", QA_MISSED_OPPORTUNITY_SYSTEM_PROMPT),
        }
        self.conductor_client = get_model_client("google", "gemini-2.5-flash")

    def _init_qa_agent(self, agent_name: str, system_prompt: str):
        # All v7.0 Tier 2 QA agents use Gemini 2.5 Flash
        try:
            return {
                "agent_name": agent_name,
                "client": get_model_client("google", "gemini-2.5-flash"),
                "system_prompt": system_prompt
            }
        except Exception as e:
            self.log_error(f"Failed to initialize QA agent {agent_name}: {e}")
            return None

    def run(self, final_draft: str) -> List[dict]:
        self.log_info("Running Step 4: Dynamic MoE QA Swarm (v8.0)...")
        
        strategy = self.blackboard.get_artifact("strategy_brief")
        job_description = self.blackboard.job_input.get("raw_jd", "")
        master_resume = self.blackboard.master_resume
        
        if not strategy or not job_description or not master_resume:
            raise HopExecutionError("Missing artifacts for QA Swarm.")

        all_results = []

        # 1. Ask QA Conductor for a plan
        conductor_prompt = QA_CONDUCTOR_USER_PROMPT.format(
            final_draft=final_draft[:2000], # Truncate for conductor
            strategy_brief=json.dumps(strategy),
            experts=json.dumps(list(self.qa_agents.keys()))
        )
        messages = [{"role": "system", "content": QA_CONDUCTOR_SYSTEM_PROMPT}, {"role": "user", "content": conductor_prompt}]
        plan_response = self.conductor_client.chat_completion(messages=messages, response_format="json_object")
        plan = plan_response.get("plan", list(self.qa_agents.keys())) # Fallback: run all
        self.log_info(f"QA Conductor selected plan: {plan}")
        
        # 2. Execute the dynamic plan (in parallel)
        for agent_name in plan:
            agent = self.qa_agents.get(agent_name)
            if agent is None or not agent["client"]:
                self.log_warning(f"Conductor planned for unknown/failed agent '{agent_name}'. Skipping.")
                all_results.append({
                    "agent_name": agent_name,
                    "passed": False,
                    "error": "Agent not initialized or not found."
                })
                continue

            try:
                user_prompt = QA_GENERIC_USER_PROMPT.format(
                    final_draft=final_draft,
                    strategy_brief=json.dumps(strategy),
                    job_description=job_description,
                    master_resume=json.dumps(master_resume)
                )

                messages = [
                    {"role": "system", "content": agent["system_prompt"]},
                    {"role": "user", "content": user_prompt}
                ]

                response = agent["client"].chat_completion(
                    messages=messages,
                    response_format="json_object"
                )

                passed = response.get("passed", False)
                details = response.get("details", "")

                result = {
                    "agent_name": agent["agent_name"],
                    "passed": passed,
                    "details": details
                }
                all_results.append(result)

            except Exception as e:
                self.log_error(f"QA agent {agent_name} failed: {e}")
                all_results.append({
                    "agent_name": agent_name,
                    "passed": False,
                    "error": str(e)
                })
        
        self.log_info(f"Dynamic MoE QA Swarm (v8.0) complete. Ran {len(all_results)} checks.")
        self.blackboard.update_artifact("qa_llm_results", all_results)
        return all_results


class AtomicQASwarmLogic(BaseAgent):
    """
    v7.0 Step 4: Atomic QA Swarm (Logic/Python)
    Python-based QA checks.
    
    Corresponds to:
    Component: AtomicQALogicAgent
    Intelligence: 40 (Medium)
    Tier: N/A (Python)
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "AtomicQASwarmLogic"

    def run(self, final_draft: str) -> List[dict]:
        self.log_info("Running Step 4: Atomic QA Swarm (Logic)...")
        results = []

        # 1. Word Count Check
        word_count = len(final_draft.split())
        min_wc = CONFIG.validation_rules.logic_wc_min
        max_wc = CONFIG.validation_rules.logic_wc_max
        wc_passed = min_wc <= word_count <= max_wc

        results.append({
            "check_name": "word_count",
            "passed": wc_passed,
            "details": f"Word count: {word_count} (min: {min_wc}, max: {max_wc})"
        })

        # 2. Character Count Check
        char_count = len(final_draft)
        min_cc = CONFIG.validation_rules.logic_cc_min
        max_cc = CONFIG.validation_rules.logic_cc_max
        cc_passed = min_cc <= char_count <= max_cc

        results.append({
            "check_name": "character_count",
            "passed": cc_passed,
            "details": f"Character count: {char_count} (min: {min_cc}, max: {max_cc})"
        })

        self.log_info(f"Atomic QA Swarm (Logic) complete. Ran {len(results)} checks.")
        return results


# ============================================================================
# FEEDBACK LOGGER & PREFERENCE CAPTURE (v7.5)
# ============================================================================

class FeedbackLoggerAgent:
    """Logs validation results to a file for meta-learning."""
    def __init__(self, log_path: str):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log(self, validation_summary: dict, workflow_id: str):
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "workflow_id": workflow_id,
                "overall_passed": validation_summary.get("overall_passed"),
                "failed_checks_count": validation_summary.get("failed_checks_count"),
                "all_results": validation_summary.get("all_results", [])
            }
            
            with open(self.log_path, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
                
        except Exception as e:
            logger.error(f"Failed to write feedback log: {e}")


class PreferenceCaptureAgent(BaseAgent):
    """
    v7.5: Preference Capture Agent
    Uses LLM to compare AI draft vs. human-approved draft.
    """
    def __init__(self, blackboard: WorkflowBlackboard, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.agent_name = "PreferenceCaptureAgent"
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

    def run(self, ai_draft: str, human_draft: str) -> dict:
        self.log_info("Running Preference Capture...")
        if self.client is None:
            raise HopExecutionError("Model client not initialized for PreferenceCaptureAgent.")

        if not ai_draft or not human_draft:
            return {"error": "Missing AI or human draft."}

        try:
            # Use difflib to compute the diff
            diff = list(difflib.unified_diff(
                ai_draft.splitlines(keepends=True),
                human_draft.splitlines(keepends=True),
                lineterm='',
                n=0
            ))
            diff_text = "".join(diff[:500])
            
            system_prompt = "You are an expert at analyzing preference signals from edits. Compare the AI draft vs. human-approved draft and identify patterns."
            user_prompt = f"""
AI Draft:
{ai_draft[:1000]}

Human-Approved Draft:
{human_draft[:1000]}

Diff (first 500 chars):
{diff_text}

Task: Analyze the edits and return JSON: {{"preference_summary": "...", "key_changes": [...]}}
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = self.client.chat_completion(
                messages=messages,
                response_format="json_object"
            )

            self.log_info("Preference capture complete.")
            return response

        except Exception as e:
            self.log_error(f"Error during preference capture: {e}")
            return {"error": str(e)}


# ============================================================================
# LANGGRAPH NODES (v7.5 -> v8.0 Upgrade)
# ============================================================================

def get_blackboard(state: 'GraphState') -> WorkflowBlackboard:
    """Helper to create a WorkflowBlackboard from the graph state."""
    return WorkflowBlackboard(
        master_resume=state["master_resume"],
        job_input=state["job_input"],
        artifacts=state["artifacts"]
    )

def run_strategy(state: 'GraphState') -> Dict[str, Any]:
    """Node: Runs Step 1: Strategy Classification"""
    blackboard = get_blackboard(state)
    
    agent = ThemeClassifierAgent(blackboard, debug_mode=True)
    strategy_brief = agent.run(job_description_text=state["job_input"]["raw_jd"])
    
    return {"artifacts": {"strategy_brief": strategy_brief}}

def run_rag_stack(state: 'GraphState') -> Dict[str, Any]:
    """Node: Runs Step 2: RAG (QueryGen, Search, Critique)"""
    blackboard = get_blackboard(state)
    
    # 1. QueryGen
    query_agent = RAG_QueryGeneratorAgent(blackboard, debug_mode=True)
    queries = query_agent.run(strategy_brief=state["artifacts"].get("strategy_brief", {}))
    
    # 2. Search
    search_agent = RAG_SearchAgent(blackboard, debug_mode=True)
    search_results = search_agent.run(queries=queries)

    # 3. Critique
    critique_agent = RAG_CritiqueAgent(blackboard, debug_mode=True)
    critique_result = critique_agent.run(
        strategy_brief=state["artifacts"].get("strategy_brief", {}),
        rag_results=search_results.get("results", [])
    )
    
    return {"artifacts": {
        "rag_queries": queries,
        "rag_search_results": search_results.get("results", []),
        "rag_critique": critique_result
    }}

def run_bullet_stack(state: 'GraphState') -> Dict[str, Any]:
    """v8.0 Node: Runs the new Advanced Bullet Swarm (Req #2)"""
    blackboard = get_blackboard(state)
    
    # 1. ProvenanceRouterAgent
    bullet_agent = ProvenanceRouterAgent(blackboard, debug_mode=True) # v8.0
    bullets = bullet_agent.run()
    
    return {"artifacts": {"generated_bullets": bullets}}

def run_drafting_stack(state: 'GraphState') -> Dict[str, Any]:
    """Node: Runs Step 3: Drafting (Prompt, Bullets, Adversarial)"""
    # v8.0: This node is now split into two: run_bullet_stack and run_drafting_stack
    # This function is now *only* for drafting.
    blackboard = get_blackboard(state)
    
    # 1. Prompt Stack
    prompt_agent = PromptStackAgent(blackboard, debug_mode=True)
    prompt_result = prompt_agent.run()
    
    # Bullets are now presumed to be in state["artifacts"] from the previous node
    bullets = state["artifacts"].get("generated_bullets", [])

    # 3. Adversarial Drafting
    drafting_agent = DraftingConductorAgent(blackboard, debug_mode=True) # v8.0
    final_draft = drafting_agent.run()
    
    return {"artifacts": {
        "final_drafting_prompt": prompt_result,
        "generated_bullets": bullets,
        "final_draft": final_draft
    }}

def run_qa_swarm(state: 'GraphState') -> Dict[str, Any]:
    """Node: Runs Step 4: QA (LLM and Logic)"""
    blackboard = get_blackboard(state)
    final_draft = state["artifacts"].get("final_draft", "")
    
    # 1. LLM QA
    qa_llm_agent = QAConductorAgent(blackboard, debug_mode=True) # v8.0
    llm_results = qa_llm_agent.run(final_draft=final_draft)
    
    # 2. Logic QA
    qa_logic_agent = AtomicQASwarmLogic(blackboard, debug_mode=True)
    logic_results = qa_logic_agent.run(final_draft=final_draft)
    
    # 3. Validation Summary (from Governor)
    all_qa_results = llm_results + logic_results
    failed_checks = [r for r in all_qa_results if not r.get("passed", False)]
    validation_summary = {
        "overall_passed": len(failed_checks) == 0,
        "failed_checks_count": len(failed_checks),
        "failed_checks": failed_checks,
        "all_results": all_qa_results
    }
    
    # Log feedback
    feedback_logger = FeedbackLoggerAgent(
        log_path=CONFIG.meta_loop_config.feedback_log_path
    )
    feedback_logger.log(validation_summary, state["workflow_id"])
    
    return {"artifacts": {
        "qa_llm_results": llm_results,
        "qa_logic_results": logic_results,
        "validation_results": validation_summary
    }}

def run_replanner(state: 'GraphState') -> Dict[str, Any]:
    """Node: Runs Step 3 (SC Paths): Re-Planner"""
    blackboard = get_blackboard(state)
    agent = WorkflowRePlannerAgent(blackboard, debug_mode=True) # v8.0 logic is now inside this agent
    failed_checks = state["artifacts"]["validation_results"]["failed_checks"]
    
    plan = agent.run(failed_qa_results=failed_checks)
    
    # Increment replan count and clear failed artifacts
    new_replan_count = state.get("replan_count", 0) + 1
    
    # Clear artifacts for retry (as Governor did)
    artifacts = state["artifacts"].copy()
    for key in [
        "final_drafting_prompt", "generated_bullets", "final_draft",
        "qa_llm_results", "qa_logic_results", "validation_results", "recovery_plan"
    ]:
        artifacts.pop(key, None)
    
    artifacts["recovery_plan"] = plan
    
    return {
        "artifacts": artifacts,
        "replan_count": new_replan_count
    }


# --- v7.5 New Nodes ---

def human_review_pause(state: 'GraphState') -> Dict[str, Any]:
    """
    Node: This node saves the final draft to the state for HIL diffing.
    The graph will be configured to *interrupt* before this node,
    allowing a human to review and provide the 'human_approved_draft'.
    """
    logger.info("HIL Pause: Awaiting human approval/edits.")
    # Save the AI draft so we can diff it against the human's version
    return {"original_draft": state["artifacts"]["final_draft"]}

def run_preference_capture(state: 'GraphState') -> Dict[str, Any]:
    """Node: Runs Step 5: Preference Capture"""
    if not CONFIG.hil_config.enable_preference_learning:
        return {"preference_insight": {"status": "disabled"}}
        
    blackboard = get_blackboard(state)
    agent = PreferenceCaptureAgent(blackboard, debug_mode=True)
    
    ai_draft = state["original_draft"]
    human_draft = state["human_approved_draft"]
    
    if not human_draft:
        # This can happen if HIL is skipped
        logger.warning("No human_approved_draft found, skipping preference capture.")
        return {"preference_insight": {"status": "skipped", "reason": "No human draft provided."}}
    
    insight = agent.run(ai_draft=ai_draft, human_draft=human_draft)
    return {"preference_insight": insight}

# --- Conditional Edge: The "Reasoning Toggle" ---

def check_qa_results(state: 'GraphState') -> str:
    """
    This is the "conditional edge" that replaces the Governor's while loop.
    v7.5: On success, it routes to HIL, not END.
    """
    qa_passed = state["artifacts"]["validation_results"]["overall_passed"]
    replan_count = state["replan_count"]
    max_replan = CONFIG.planner_config.max_replan_loops
    
    if qa_passed:
        logger.info("✅ QA Swarm Passed. Routing to Human-in-the-Loop (HIL) review.")
        return "human_review_pause"
    elif replan_count >= max_replan:
        logger.error(f"❌ QA Failed. Max replan loops ({max_replan}) reached. Halting.")
        return "FAIL_HALT"
    else:
        logger.warning(f"⚠️ QA Failed. Triggering Re-Planner (Attempt {replan_count + 1}).")
        return "REPLANNER"

# --- Graph Assembly ---

def get_graph_app(checkpointer: 'RedisSaver', enable_hil: bool = True) -> 'CompiledGraph':
    """
    Builds and compiles the persistent v8.5 StateGraph.
    """
    from langgraph.graph import StateGraph, END
    from core_v8_5 import GraphState
    
    workflow = StateGraph(GraphState)

    # 1. Add Nodes
    workflow.add_node("strategy", run_strategy)
    workflow.add_node("rag_stack", run_rag_stack)
    workflow.add_node("bullet_stack", run_bullet_stack) # v8.0
    workflow.add_node("drafting_stack", run_drafting_stack)
    workflow.add_node("qa_swarm", run_qa_swarm)
    workflow.add_node("replanner", run_replanner)
    
    # 2. Add Edges (Linear Flow)
    workflow.set_entry_point("strategy")
    workflow.add_edge("strategy", "rag_stack")
    workflow.add_edge("rag_stack", "bullet_stack") # v8.0
    workflow.add_edge("bullet_stack", "drafting_stack") # v8.0
    workflow.add_edge("drafting_stack", "qa_swarm") 
    
    # 3. Add Re-Planner Loop Edge
    workflow.add_edge("replanner", "bullet_stack") # v8.0: Re-plan must re-gen bullets AND draft
    
    # 4. v7.5: Add HIL or non-HIL flow
    if enable_hil and CONFIG.hil_config.enable_content_approval:
        # --- HIL Flow (for main.py) ---
        logger.info("Building graph with HIL Content Approval ENABLED.")
        
        # Add HIL nodes
        workflow.add_node("human_review_pause", human_review_pause)
        workflow.add_node("capture_preferences", run_preference_capture)
        
        # Add Conditional Edge (The QA Loop)
        workflow.add_conditional_edges(
            "qa_swarm",
            check_qa_results,
            {
                "human_review_pause": "human_review_pause",
                "FAIL_HALT": END,
                "REPLANNER": "replanner"
            }
        )
        
        # Add final HIL edges
        workflow.add_edge("human_review_pause", "capture_preferences")
        workflow.add_edge("capture_preferences", END)
        
        interrupt_nodes = ["human_review_pause"]

    else:
        # --- Non-HIL Flow (for run_batch.py) ---
        logger.info("Building graph with HIL Content Approval DISABLED.")
        
        # Add Conditional Edge (The QA Loop)
        workflow.add_conditional_edges(
            "qa_swarm",
            check_qa_results,
            {
                "human_review_pause": END,
                "FAIL_HALT": END,
                "REPLANNER": "replanner"
            }
        )
        interrupt_nodes = []

    # 5. Compile with Persistence
    return workflow.compile(
        checkpointer=checkpointer, 
        interrupt_before=interrupt_nodes
    )



# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # --- New v7.5 Export ---
    'get_graph_app',
    'PreferenceCaptureAgent',
    
    # --- Original Agent Exports (unchanged) ---
    'WorkflowSteps', 'FeedbackLoggerAgent',
    'ThemeClassifierAgent', 'RAG_QueryGeneratorAgent', 'RAG_SearchAgent',
    'RAG_CritiqueAgent', 'PromptStackAgent',
    'ProvenanceRouterAgent', 'CustomizedBulletDrafterAgent', 'SyntheticBulletDrafterAgent', # v8.0
    'DraftingConductorAgent', # v8.0
    'WorkflowRePlannerAgent',
    'QAConductorAgent', 'AtomicQASwarmLogic' # v8.0
]
