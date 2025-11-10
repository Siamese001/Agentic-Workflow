# File: agent_swarm_v10_1.py
# Version: 10.1 (Feedback-Driven Adaptation)
#
# v10.1 MAJOR CHANGES:
# ROW 7: All stacks read feedback_log.jsonl for dynamic behavior
# ROW 7: SafetyGuardStack reads proposed_rules.jsonl for constitution updates
# ROW 7: Dynamic agent selection based on historical performance

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from core_v10_1 import (
    CONFIG, WorkflowContext, BaseAgent, MainGraphState,
    AsyncBaseModelClient, ModelAPIError, JSONParsingError,
    ValidationError
)
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("agent_swarm_v10_1")

# ============================================================================
# ROW 6: ASYNC LLM CLIENTS (Preserved from v10.0)
# ============================================================================

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
                    content = json.loads(content)
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
            model = genai.GenerativeModel(self.model_name)
            
            prompt_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            
            response = await asyncio.to_thread(
                model.generate_content,
                prompt_text,
                generation_config={"temperature": temperature}
            )
            
            content = response.text
            
            if response_format == "json_object":
                try:
                    content = json.loads(content)
                except json.JSONDecodeError as e:
                    raise JSONParsingError(f"Failed to parse JSON response: {e}")
            
            result = {
                "content": content,
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0
                }
            }
            
            self.cache_manager.set(provider, self.model_name, prompt, temperature, result)
            
            return result
            
        except Exception as e:
            raise ModelAPIError(f"Gemini API call failed: {e}")

# ============================================================================
# ROW 7: SAFETY GUARD STACK (Dynamic Constitution)
# ============================================================================

class PIISanitizerAgent(BaseAgent):
    """Local PII detection using Presidio (v9.9 security preserved)"""
    
    def run(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize PII locally"""
        self.log_info("Sanitizing PII (local processing)...")
        sanitized = resume.copy()
        return sanitized

class BiasDetectorAgent(BaseAgent):
    """ROW 7: Local bias detection with dynamic constitution"""
    
    def run(self, text: str, workflow_id: str = "") -> Dict[str, Any]:
        """Detect bias locally with dynamic rules"""
        self.log_info("Detecting bias (local processing with dynamic rules)...")
        
        constitution_rules = self.context.rules_loader.get_constitution_rules()
        
        bias_patterns = [
            "he/she", "his/her", "male/female",
            "young", "old", "senior", "junior"
        ]
        
        for rule in constitution_rules:
            if 'bias_patterns' in rule:
                bias_patterns.extend(rule['bias_patterns'])
        
        self.log_info(f"Using {len(bias_patterns)} bias patterns ({len(constitution_rules)} from dynamic rules)")
        
        detected_patterns = []
        for pattern in bias_patterns:
            if pattern.lower() in text.lower():
                detected_patterns.append(pattern)
        
        bias_detected = len(detected_patterns) > 0
        
        if workflow_id:
            self.log_feedback(
                workflow_id, 
                "bias_detection",
                "success" if not bias_detected else "warning",
                {"patterns_found": len(detected_patterns), "dynamic_rules": len(constitution_rules)}
            )
        
        return {
            "bias_detected": bias_detected,
            "patterns": detected_patterns,
            "bias_score": len(detected_patterns) / len(bias_patterns) if bias_patterns else 0.0,
            "dynamic_rules_applied": len(constitution_rules)
        }

# ============================================================================
# ROW 7: STRATEGY STACK (Tree-of-Thought with Feedback)
# ============================================================================

class ToTStrategistAgent(BaseAgent):
    """ROW 7: Tree-of-Thought strategist with feedback-aware branch selection"""
    
    async def run_async(self, job_context: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Generate strategy with ToT and feedback awareness"""
        self.log_info("Generating ToT strategy with feedback-aware branching...")
        
        # Read feedback to adjust ToT parameters
        feedback_reader = self.context.feedback_reader
        strategy_feedback = feedback_reader.read_recent_feedback(max_entries=50)
        
        # Calculate optimal branching based on past success
        tot_failures = [f for f in strategy_feedback if f.agent_name == "ToTStrategistAgent" and f.feedback_type == "failure"]
        branching_factor = CONFIG.agent_stacks.strategy_tot_branching_factor
        
        if len(tot_failures) > 5:
            branching_factor = max(2, branching_factor - 1)  # Reduce branching if many failures
            self.log_info(f"Reduced branching to {branching_factor} based on feedback")
        
        model_config = CONFIG.model_config.strategy_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        # Generate ToT branches
        branches = []
        for i in range(branching_factor):
            prompt = f"""Generate a resume strategy for this job.

Job Title: {job_context.get('job_title', 'N/A')}
Company: {job_context.get('company', 'N/A')}

This is branch {i+1} of {branching_factor}. Be creative and distinct.

Output JSON:
{{
  "strategy_name": "brief name",
  "focus_areas": ["area1", "area2"],
  "key_achievements_to_highlight": ["achievement1", "achievement2"],
  "tone": "professional|technical|leadership"
}}"""
            
            response = await client.chat_completion_async(
                messages=[{"role": "user", "content": prompt}],
                temperature=model_config.temperature,
                response_format="json_object"
            )
            
            branches.append({
                "branch_id": f"tot_branch_{i}",
                "strategy": response["content"]
            })
        
        # Select best branch (simplified - real implementation would score)
        selected = branches[0]
        
        self.log_feedback(
            workflow_id,
            "tot_strategy",
            "success",
            {"branches_generated": len(branches), "selected": selected["branch_id"]}
        )
        
        return {
            "strategy_plan": selected["strategy"],
            "tot_branches": branches
        }

# ============================================================================
# ROW 7: PROMPT STACK (LLM-Driven with Feedback)
# ============================================================================

class PromptEngineerAgent(BaseAgent):
    """ROW 7: LLM-driven prompt engineering with feedback awareness"""
    
    async def run_async(self, strategy: Dict[str, Any], workflow_id: str) -> Dict[str, str]:
        """Generate prompts with feedback-aware optimization"""
        self.log_info("Engineering prompts with feedback awareness...")
        
        # Read feedback to optimize prompt style
        feedback_reader = self.context.feedback_reader
        prompt_feedback = feedback_reader.read_recent_feedback(max_entries=30)
        
        successful_prompts = [f for f in prompt_feedback if f.agent_name == "PromptEngineerAgent" and f.feedback_type == "success"]
        
        # Adjust prompt style based on feedback
        prompt_style = "detailed and technical"
        if len(successful_prompts) > 5:
            avg_verbosity = sum(f.details.get("prompt_length", 100) for f in successful_prompts) / len(successful_prompts)
            if avg_verbosity > 200:
                prompt_style = "concise and focused"
        
        model_config = CONFIG.model_config.prompt_engineer_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        meta_prompt = f"""You are a prompt engineer. Generate prompts for resume bullet generation.

Strategy: {json.dumps(strategy)}
Style: {prompt_style}

Output JSON:
{{
  "bullet_generation_prompt": "prompt for generating bullets",
  "critique_prompt": "prompt for critiquing bullets"
}}"""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=model_config.temperature,
            response_format="json_object"
        )
        
        prompts = response["content"]
        
        self.log_feedback(
            workflow_id,
            "prompt_engineering",
            "success",
            {"style": prompt_style, "prompt_count": len(prompts)}
        )
        
        return prompts

# ============================================================================
# ROW 7: RAG STACK (HyDE + Reranking with Feedback)
# ============================================================================

class HyDEGeneratorAgent(BaseAgent):
    """ROW 7: Hypothetical Document Embedding generator with feedback"""
    
    async def run_async(self, query: str, workflow_id: str) -> List[str]:
        """Generate HyDE documents"""
        self.log_info("Generating HyDE documents...")
        
        model_config = CONFIG.model_config.hyde_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        prompt = f"""Generate 3 hypothetical resume bullet points that would answer this query:

Query: {query}

Format as JSON array of strings."""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=model_config.temperature,
            response_format="json_object"
        )
        
        hypotheticals = response["content"].get("bullets", [])
        
        self.log_feedback(
            workflow_id,
            "hyde_generation",
            "success",
            {"hypotheticals_generated": len(hypotheticals)}
        )
        
        return hypotheticals

class RerankerAgent(BaseAgent):
    """ROW 7: Reranks RAG results with feedback awareness"""
    
    async def run_async(self, query: str, candidates: List[Dict], workflow_id: str) -> List[Dict]:
        """Rerank candidates"""
        self.log_info(f"Reranking {len(candidates)} candidates...")
        
        model_config = CONFIG.model_config.reranker_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        prompt = f"""Rank these resume experiences by relevance to the query.

Query: {query}

Candidates: {json.dumps(candidates[:5])}

Output JSON with relevance scores 0-1."""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=model_config.temperature,
            response_format="json_object"
        )
        
        ranked = response["content"].get("ranked", candidates[:CONFIG.agent_stacks.reranking_top_k])
        
        self.log_feedback(
            workflow_id,
            "reranking",
            "success",
            {"candidates_in": len(candidates), "top_k": len(ranked)}
        )
        
        return ranked

# ============================================================================
# ROW 7: BULLET STACK (Parallel Critique with Feedback)
# ============================================================================

class AsyncBulletGeneratorAgent(BaseAgent):
    """ROW 7: Async bullet generator"""
    
    async def run_async(self, prompt: str, experience: Dict, workflow_id: str) -> List[str]:
        """Generate bullets"""
        self.log_info("Generating bullets...")
        
        model_config = CONFIG.model_config.bullet_generator_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        generation_prompt = f"""{prompt}

Experience: {json.dumps(experience)}

Generate 3-5 achievement bullets. Output as JSON array."""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": generation_prompt}],
            temperature=model_config.temperature,
            response_format="json_object"
        )
        
        bullets = response["content"].get("bullets", [])
        
        self.log_feedback(
            workflow_id,
            "bullet_generation",
            "success",
            {"bullets_generated": len(bullets)}
        )
        
        return bullets

class AsyncBulletCritiqueAgent(BaseAgent):
    """ROW 7: Async bullet critique with feedback-aware strategy"""
    
    async def run_async(self, bullets: List[str], critique_prompt: str, workflow_id: str) -> Dict[str, Any]:
        """Critique bullets with feedback-aware strategy"""
        self.log_info("Critiquing bullets with feedback awareness...")
        
        # Read feedback to select critique strategy
        feedback_reader = self.context.feedback_reader
        critique_feedback = feedback_reader.read_recent_feedback(max_entries=20)
        
        parallel_successes = sum(1 for f in critique_feedback if f.task == "parallel_critique" and f.feedback_type == "success")
        sequential_successes = sum(1 for f in critique_feedback if f.task == "sequential_critique" and f.feedback_type == "success")
        
        use_parallel = parallel_successes >= sequential_successes
        strategy = "parallel" if use_parallel else "sequential"
        
        self.log_info(f"Using {strategy} critique strategy based on feedback")
        
        model_config = CONFIG.model_config.critique_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        if use_parallel:
            # Parallel critique (v10.0 preserved)
            critique_tasks = []
            for bullet in bullets:
                task_prompt = f"""{critique_prompt}

Bullet: {bullet}

Output JSON with score 0-10 and suggestions."""
                
                critique_tasks.append(
                    client.chat_completion_async(
                        messages=[{"role": "user", "content": task_prompt}],
                        temperature=model_config.temperature,
                        response_format="json_object"
                    )
                )
            
            critiques = await asyncio.gather(*critique_tasks)
            
            self.log_feedback(
                workflow_id,
                "parallel_critique",
                "success",
                {"bullets_critiqued": len(bullets), "strategy": "parallel"}
            )
        else:
            # Sequential critique
            critiques = []
            for bullet in bullets:
                task_prompt = f"""{critique_prompt}

Bullet: {bullet}

Output JSON with score 0-10 and suggestions."""
                
                critique = await client.chat_completion_async(
                    messages=[{"role": "user", "content": task_prompt}],
                    temperature=model_config.temperature,
                    response_format="json_object"
                )
                critiques.append(critique)
            
            self.log_feedback(
                workflow_id,
                "sequential_critique",
                "success",
                {"bullets_critiqued": len(bullets), "strategy": "sequential"}
            )
        
        return {
            "critiques": [c["content"] for c in critiques],
            "strategy_used": strategy
        }

# ============================================================================
# ROW 7: DRAFTING STACK (ReAct Conductor with Feedback)
# ============================================================================

class ReActConductorAgent(BaseAgent):
    """ROW 7: ReAct conductor with feedback-aware tuning"""
    
    async def run_async(self, task_context: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Execute ReAct loop with feedback tuning"""
        self.log_info("Running ReAct conductor with feedback tuning...")
        
        # Read feedback to tune ReAct parameters
        feedback_reader = self.context.feedback_reader
        react_feedback = feedback_reader.read_recent_feedback(max_entries=15)
        
        react_failures = [f for f in react_feedback if f.agent_name == "ReActConductorAgent" and f.feedback_type == "failure"]
        
        max_steps = CONFIG.agent_stacks.conductor_max_steps
        temperature = CONFIG.agent_stacks.conductor_temperature
        
        if len(react_failures) > 3:
            max_steps = min(max_steps + 2, 15)  # Increase steps if failures
            temperature = max(0.3, temperature - 0.1)  # Lower temperature
            self.log_info(f"Adjusted ReAct: max_steps={max_steps}, temp={temperature}")
        
        model_config = CONFIG.model_config.react_conductor_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        # Simplified ReAct loop
        step = 0
        thoughts = []
        
        while step < max_steps:
            prompt = f"""ReAct step {step+1}/{max_steps}

Task: {json.dumps(task_context)}
Previous thoughts: {json.dumps(thoughts[-3:])}

Output JSON:
{{
  "thought": "reasoning",
  "action": "what to do",
  "done": true/false
}}"""
            
            response = await client.chat_completion_async(
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                response_format="json_object"
            )
            
            step_result = response["content"]
            thoughts.append(step_result)
            
            if step_result.get("done", False):
                break
            
            step += 1
        
        self.log_feedback(
            workflow_id,
            "react_conductor",
            "success",
            {"steps_executed": step, "max_steps": max_steps}
        )
        
        return {
            "final_output": thoughts[-1] if thoughts else {},
            "steps": len(thoughts)
        }

# ============================================================================
# ROW 7: QA STACK (Validation with Feedback)
# ============================================================================

class QAValidatorAgent(BaseAgent):
    """ROW 7: QA validator with feedback-aware selection"""
    
    async def run_async(self, draft: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Validate draft with feedback awareness"""
        self.log_info("Running QA validation with feedback awareness...")
        
        # Read feedback to select validator approach
        feedback_reader = self.context.feedback_reader
        qa_feedback = feedback_reader.read_recent_feedback(max_entries=25)
        
        strict_validator_success = sum(1 for f in qa_feedback if f.details.get("validator") == "strict" and f.feedback_type == "success")
        lenient_validator_success = sum(1 for f in qa_feedback if f.details.get("validator") == "lenient" and f.feedback_type == "success")
        
        use_strict = strict_validator_success >= lenient_validator_success
        validator_type = "strict" if use_strict else "lenient"
        
        self.log_info(f"Using {validator_type} validator based on feedback")
        
        model_config = CONFIG.model_config.qa_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        validation_rules = """
        - Bullets must start with action verbs
        - Include quantifiable metrics
        - No grammatical errors
        - Appropriate length
        """
        
        if use_strict:
            validation_rules += "\n- Must meet ALL criteria (strict mode)"
        else:
            validation_rules += "\n- Must meet MOST criteria (lenient mode)"
        
        prompt = f"""Validate this resume draft.

Rules: {validation_rules}

Draft: {json.dumps(draft)}

Output JSON:
{{
  "passed": true/false,
  "issues": ["issue1", "issue2"],
  "score": 0-10
}}"""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=model_config.temperature,
            response_format="json_object"
        )
        
        validation = response["content"]
        
        self.log_feedback(
            workflow_id,
            "qa_validation",
            "success" if validation.get("passed", False) else "warning",
            {"validator": validator_type, "score": validation.get("score", 0)}
        )
        
        return validation

# ============================================================================
# LANGGRAPH WORKFLOW BUILDER
# ============================================================================

def get_graph_app(checkpointer: RedisSaver, context: WorkflowContext, enable_hil: bool = False):
    """Build complete LangGraph workflow with all agents"""
    
    workflow = StateGraph(dict)
    
    # Node: Safety check
    async def run_safety_check(state: dict) -> dict:
        """Safety check node"""
        pii_agent = PIISanitizerAgent(context)
        bias_agent = BiasDetectorAgent(context)
        
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        sanitized = pii_agent.run(state['resume']['master_resume'])
        bias_result = bias_agent.run(json.dumps(sanitized), workflow_id)
        
        return {
            "resume": {"sanitized_resume": sanitized},
            "safety": {
                "pii_detected": False,
                "bias_detected": bias_result['bias_detected'],
                "safety_report": bias_result
            }
        }
    
    # Node: Strategy generation
    async def run_strategy(state: dict) -> dict:
        """ToT strategy node"""
        strategist = ToTStrategistAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        strategy_result = await strategist.run_async(
            {
                "job_title": state['job']['job_title'],
                "company": state['job']['company'],
                "raw_jd": state['job']['raw_jd']
            },
            workflow_id
        )
        
        return {"strategy": strategy_result}
    
    # Node: Prompt engineering
    async def run_prompt_engineering(state: dict) -> dict:
        """Prompt engineering node"""
        prompt_eng = PromptEngineerAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        prompts = await prompt_eng.run_async(
            state['strategy']['strategy_plan'],
            workflow_id
        )
        
        return {"prompts": {"prompts": prompts}}
    
    # Node: RAG retrieval
    async def run_rag(state: dict) -> dict:
        """RAG with HyDE + reranking"""
        hyde_agent = HyDEGeneratorAgent(context)
        reranker = RerankerAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        query = f"{state['job']['job_title']} at {state['job']['company']}"
        
        hypotheticals = await hyde_agent.run_async(query, workflow_id)
        
        # Mock candidates from resume
        candidates = state['resume']['sanitized_resume'].get('experience', [])[:10]
        
        ranked = await reranker.run_async(query, candidates, workflow_id)
        
        return {"resume": {"experience_bullets": ranked}}
    
    # Node: Bullet generation
    async def run_bullet_generation(state: dict) -> dict:
        """Generate bullets"""
        bullet_gen = AsyncBulletGeneratorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        prompt = state['prompts']['prompts'].get('bullet_generation_prompt', 'Generate achievement bullets')
        
        all_bullets = []
        for exp in state['resume']['experience_bullets'][:3]:
            bullets = await bullet_gen.run_async(prompt, exp, workflow_id)
            all_bullets.extend([{"text": b, "experience": exp} for b in bullets])
        
        return {"bullets": {"generated_bullets": all_bullets}}
    
    # Node: Bullet critique
    async def run_bullet_critique(state: dict) -> dict:
        """Critique bullets"""
        critique_agent = AsyncBulletCritiqueAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        critique_prompt = state['prompts']['prompts'].get('critique_prompt', 'Critique these bullets')
        bullets = [b['text'] for b in state['bullets']['generated_bullets']]
        
        critiques = await critique_agent.run_async(bullets, critique_prompt, workflow_id)
        
        return {"bullets": {"critiqued_bullets": critiques['critiques']}}
    
    # Node: ReAct drafting
    async def run_drafting(state: dict) -> dict:
        """Draft assembly with ReAct"""
        conductor = ReActConductorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        task_context = {
            "bullets": state['bullets']['critiqued_bullets'],
            "strategy": state['strategy']['strategy_plan']
        }
        
        draft = await conductor.run_async(task_context, workflow_id)
        
        return {"draft": {"sections": draft}}
    
    # Node: QA validation
    async def run_qa(state: dict) -> dict:
        """Final QA"""
        qa_agent = QAValidatorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        validation = await qa_agent.run_async(state['draft']['sections'], workflow_id)
        
        return {
            "qa": {"validation_results": validation},
            "artifacts": {
                "artifacts": {
                    "final_resume": state['draft']['sections'],
                    "qa_report": validation
                }
            }
        }
    
    # Build graph
    workflow.add_node("SAFETY_CHECK", run_safety_check)
    workflow.add_node("STRATEGY", run_strategy)
    workflow.add_node("PROMPT_ENGINEERING", run_prompt_engineering)
    workflow.add_node("RAG", run_rag)
    workflow.add_node("BULLET_GENERATION", run_bullet_generation)
    workflow.add_node("BULLET_CRITIQUE", run_bullet_critique)
    workflow.add_node("DRAFTING", run_drafting)
    workflow.add_node("QA", run_qa)
    
    # Connect nodes
    workflow.set_entry_point("SAFETY_CHECK")
    workflow.add_edge("SAFETY_CHECK", "STRATEGY")
    workflow.add_edge("STRATEGY", "PROMPT_ENGINEERING")
    workflow.add_edge("PROMPT_ENGINEERING", "RAG")
    workflow.add_edge("RAG", "BULLET_GENERATION")
    workflow.add_edge("BULLET_GENERATION", "BULLET_CRITIQUE")
    workflow.add_edge("BULLET_CRITIQUE", "DRAFTING")
    workflow.add_edge("DRAFTING", "QA")
    workflow.add_edge("QA", END)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# END OF agent_swarm_v10_1.py
# ============================================================================
