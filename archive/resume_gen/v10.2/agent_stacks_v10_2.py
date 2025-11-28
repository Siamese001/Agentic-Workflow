# File: agent_stacks_v10_2.py
# Version: 10.2 (Design-Aligned Implementation)
#
# Description:
# v10.2: Replaced TF-IDF GraphSearchTool with ChromaDBSearchTool for
# true semantic search. RAG_SearchAgent now handles ingestion.
#
# Contains the foundational agent stacks (Safety, Strategy, RAG, Bullet, HIL)
# and the simple tools they use. This file has no dependencies on
# other agent_*.py files.

import os
import json
import logging
import asyncio
import re
import math
import uuid # v10.2: Added
import chromadb # v10.2: Added
from chromadb.utils import embedding_functions # v10.2: Added
from collections import Counter
from typing import Dict, Any, List, Optional
from datetime import datetime

# v10.2: Import from new core
from core_v10_2 import (
    WorkflowContext, BaseAgent,
    ModelAPIError, JSONParsingError, ValidationError
)

logger = logging.getLogger("agent_stacks_v10_2")

# ============================================================================
# BASE TOOL INTERFACE
# ============================================================================

class BaseTool(BaseAgent):
    """Base interface for tools used by ReAct Conductors"""
    tool_name: str = "base_tool"
    
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Execute the tool"""
        raise NotImplementedError
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the tool's JSON schema"""
        return {
            "name": self.tool_name,
            "description": self.__doc__ or "No description",
            "parameters": {"type": "object", "properties": {}}
        }

# ============================================================================
# ROW 7: SAFETY GUARD STACK (Dynamic Constitution)
# ============================================================================

class PIISanitizerAgent(BaseAgent):
    """
    GAP 1 FIX: Local PII detection using regex (no longer mock).
    (v9.9 security preserved)
    """
    
    # Simple regex for common PII
    PII_PATTERNS = {
        "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        "PHONE": re.compile(r'\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b'),
        # Simple name finder (Title Case words) - will have false positives
        "NAME": re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b') 
    }
    
    def run(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize PII locally using regex"""
        self.log_info("Sanitizing PII (local regex processing)...")
        
        # Deep copy to avoid modifying original
        sanitized_resume = json.loads(json.dumps(resume))
        
        # Recursively scan and sanitize dictionary
        def sanitize_node(node):
            if isinstance(node, dict):
                return {k: sanitize_node(v) for k, v in node.items()}
            elif isinstance(node, list):
                return [sanitize_node(item) for item in node]
            elif isinstance(node, str):
                return self._sanitize_text(node)
            else:
                return node

        sanitized = sanitize_node(sanitized_resume)
        self.log_info("PII sanitization complete.")
        return sanitized

    def _sanitize_text(self, text: str) -> str:
        """Apply all PII regex patterns to a string"""
        for pii_type, pattern in self.PII_PATTERNS.items():
            text = pattern.sub(f"[{pii_type}_REDACTED]", text)
        return text

class BiasDetectorAgent(BaseAgent):
    """ROW 7: Local bias detection with dynamic constitution"""
    
    def run(self, text: str, workflow_id: str = "") -> Dict[str, Any]:
        """Detect bias locally with dynamic rules"""
        self.log_info("Detecting bias (local processing with dynamic rules)...")
        
        # Reads rules from proposed_rules.jsonl via the loader
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
        
        feedback_reader = self.context.feedback_reader
        strategy_feedback = feedback_reader.read_recent_feedback(max_entries=50)
        
        tot_failures = [f for f in strategy_feedback if f.agent_name == "ToTStrategistAgent" and f.feedback_type == "failure"]
        branching_factor = self.config.agent_stacks.strategy_tot_branching_factor
        
        if len(tot_failures) > 5:
            branching_factor = max(2, branching_factor - 1)
            self.log_info(f"Reduced branching to {branching_factor} based on feedback")
        
        # Design-Aligned: Use strategy_model (Gemini 2.5 Pro)
        client = self.get_model_client("strategy_model")
        
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
                temperature=self.config.model_config.strategy_model.temperature,
                response_format="json_object"
            )
            
            branches.append({
                "branch_id": f"tot_branch_{i}",
                "strategy": response["content"]
            })
        
        # NOTE: Simplified selection for brevity. A real ToT would critique/vote.
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
        
        feedback_reader = self.context.feedback_reader
        prompt_feedback = feedback_reader.read_recent_feedback(max_entries=30)
        
        successful_prompts = [f for f in prompt_feedback if f.agent_name == "PromptEngineerAgent" and f.feedback_type == "success"]
        
        prompt_style = "detailed and technical"
        if len(successful_prompts) > 5:
            avg_verbosity = sum(f.details.get("prompt_length", 100) for f in successful_prompts) / len(successful_prompts)
            if avg_verbosity > 200:
                prompt_style = "concise and focused"
        
        # Design-Aligned: Use prompt_engineer_model (Gemini 2.5 Flash)
        client = self.get_model_client("prompt_engineer_model")
        
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
            temperature=self.config.model_config.prompt_engineer_model.temperature,
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
# ROW 7: RAG STACK (ReAct Search + HyDE + ChromaDB)
# ============================================================================

class HyDETool(BaseTool):
    """Generates hypothetical documents for query expansion"""
    tool_name = "generate_hypothetical_documents"
    
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Generating HyDE documents...")
        query = tool_input.get("query", "")
        
        # Design-Aligned: Use hyde_model (Gemini 2.5 Flash)
        client = self.get_model_client("hyde_model")
        
        prompt = f"Generate 3 hypothetical resume bullet points that would answer this query:\nQuery: {query}\nFormat as JSON array of strings."
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.hyde_model.temperature,
            response_format="json_object"
        )
        
        hypotheticals = response["content"]
        
        self.log_feedback(workflow_id, "hyde_generation", "success", {"hypotheticals_generated": len(hypotheticals)})
        return {"documents": hypotheticals}

# --- v10.2 OVERWRITE: Replaced TF-IDF with ChromaDB ---

class ChromaDBSearchTool(BaseTool):
    """
    v10.2: Searches the resume database using ChromaDB.
    This tool *only queries*. Ingestion is handled by the
    RAG_SearchAgent conductor.
    """
    tool_name = "search_resume_database"

    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        # Use default embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection_name = self.config.chromadb_config.default_collection_name
        self.chroma_client = self.context.chromadb_client
        
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        query = tool_input.get("query", "")
        self.log_info(f"Searching ChromaDB (semantic) for: {query}")

        try:
            collection = self.chroma_client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            
            # Query ChromaDB, filtering by the current workflow_id
            results = await asyncio.to_thread(
                collection.query,
                query_texts=[query],
                n_results=5,
                where={"workflow_id": workflow_id} # Isolate results to this job
            )
            
            # Extract and format results
            search_results = []
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            for doc, meta in zip(documents, metadatas):
                # Reconstruct the original experience object from metadata
                experience_obj = meta.get("experience_object", {})
                if experience_obj:
                    search_results.append(json.loads(experience_obj))

            self.log_feedback(workflow_id, "chroma_search", "success", {"query": query, "results_found": len(search_results)})
            return {"search_results": search_results}
            
        except Exception as e:
            self.log_error(f"Failed to run ChromaDB search: {e}")
            return {"search_results": []}

# --- End of v10.2 OVERWRITE ---

class RAG_SearchAgent(BaseAgent):
    """ReAct-based RAG agent that uses HyDE and Search tools"""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.tools = {
            "generate_hypothetical_documents": HyDETool(context, debug_mode),
            "search_resume_database": ChromaDBSearchTool(context, debug_mode) # v10.2
        }
        # v10.2: Add ChromaDB client
        self.chroma_client = self.context.chromadb_client
        self.collection_name = self.config.chromadb_config.default_collection_name
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
    
    async def _ingest_resume_to_chroma_async(self, resume_experience: List[Dict], workflow_id: str):
        """v10.2: Ingests resume chunks into ChromaDB for this workflow"""
        self.log_info(f"Ingesting {len(resume_experience)} experience blocks into ChromaDB for workflow {workflow_id}")
        
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            
            documents = []
            metadatas = []
            ids = []
            
            for exp in resume_experience:
                # Chunking: Each bullet is a document
                for bullet in exp.get("bullet_pool", []):
                    documents.append(bullet)
                    metadatas.append({
                        "workflow_id": workflow_id,
                        "company": exp.get("company", "N/A"),
                        "title": exp.get("title", "N/A"),
                        # Store the full object for retrieval
                        "experience_object": json.dumps(exp) 
                    })
                    ids.append(f"{workflow_id}_{uuid.uuid4()}")
            
            if not documents:
                self.log_warning("No bullets found to ingest into ChromaDB.")
                return

            # Run blocking 'add' in a separate thread
            await asyncio.to_thread(
                collection.add,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            self.log_info(f"Successfully ingested {len(documents)} bullets into ChromaDB.")
            
        except Exception as e:
            self.log_error(f"ChromaDB ingestion failed: {e}")

    async def run_async(self, query: str, resume_experience: List[Dict], workflow_id: str) -> List[Dict]:
        self.log_info("Running ReAct RAG Search (v10.2 ChromaDB)...")
        
        # v10.2: Ingest data into ChromaDB first
        await self._ingest_resume_to_chroma_async(resume_experience, workflow_id)
        
        # Design-Aligned: Use react_conductor_model (Gemini 2.5 Pro)
        client = self.get_model_client("react_conductor_model")
        
        messages = [{
            "role": "user",
            "content": f"""You are a RAG search agent. Your goal is to find the most relevant experience bullets for the query: "{query}".
You have these tools:
1.  **generate_hypothetical_documents**: Use this *first* to create example bullets.
2.  **search_resume_database**: Use this to search the resume for bullets matching your query or hypotheticals.

Plan:
1.  Think about the query.
2.  Call `generate_hypothetical_documents` with the query.
3.  Analyze the hypothetical documents.
4.  Call `search_resume_database` using keywords from the query and hypotheticals.
5.  Review the search results and output the final list of relevant experiences.

Output your thoughts and tool calls in JSON format:
{{"thought": "Your reasoning", "tool_call": {{"name": "tool_name", "input": {{"arg": "value"}}}}}}
When finished, output:
{{"thought": "Final answer compiled", "final_answer": [...]}}
"""
        }]
        
        final_results = []
        
        for _ in range(5): # Max 5 steps
            response = await client.chat_completion_async(
                messages=messages,
                temperature=self.config.model_config.react_conductor_model.temperature,
                response_format="json_object"
            )
            
            step_data = response["content"]
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if "final_answer" in step_data:
                final_results = step_data["final_answer"]
                break
            
            if "tool_call" in step_data:
                tool_name = step_data["tool_call"]["name"]
                tool_input = step_data["tool_call"]["input"]
                
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    # Note: workflow_id is passed to tool.run_async
                    tool_result = await tool.run_async(tool_input, workflow_id) 
                    messages.append({"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"})
                else:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})

        self.log_feedback(workflow_id, "react_rag_search", "success", {"results_found": len(final_results)})
        
        # Final reranking step
        if final_results:
            return await self.rerank_results(query, final_results, workflow_id)
        return []

    async def rerank_results(self, query: str, candidates: List[Dict], workflow_id: str) -> List[Dict]:
        """Rerank candidates"""
        self.log_info(f"Reranking {len(candidates)} candidates...")
        # Design-Aligned: Use reranker_model (Gemini 2.5 Flash)
        client = self.get_model_client("reranker_model")
        
        prompt = f"Rank these resume experiences by relevance to the query.\nQuery: {query}\nCandidates: {json.dumps(candidates)}\nOutput JSON with relevance scores 0-1."
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.reranker_model.temperature,
            response_format="json_object"
        )
        
        ranked = response["content"].get("ranked", candidates[:self.config.agent_stacks.reranking_top_k])
        
        self.log_feedback(workflow_id, "reranking", "success", {"candidates_in": len(candidates), "top_k": len(ranked)})
        return ranked

# ============================================================================
# ROW 7: BULLET STACK (4-Step Provenance, Design-Aligned)
# ============================================================================

class AsyncBulletGeneratorAgent(BaseAgent):
    """ROW 7: Async bullet generator with 4-step provenance plan"""
    
    async def run_async(self, prompt: str, experience: Dict, workflow_id: str) -> List[str]:
        """Generate bullets using 4-step plan"""
        self.log_info(f"Generating bullets for '{experience.get('title')}' with 4-step plan...")
        
        # 1. Verbatim (GAP 3 FIX: No longer mock, filters for metrics)
        verbatim = await self.run_verbatim(experience, workflow_id)
        
        # 2. Customized
        customized = await self.run_customized(prompt, experience, workflow_id)
        
        # 3. Synthetic
        synthetic = await self.run_synthetic(prompt, experience, workflow_id)
        
        # 4. Fact-Check (Design-Aligned, no longer mock)
        all_bullets = verbatim + customized + synthetic
        final_bullets = await self.run_fact_check(all_bullets, experience, workflow_id)
        
        self.log_feedback(workflow_id, "bullet_generation_4_step", "success", {"bullets_generated": len(final_bullets)})
        return final_bullets

    async def run_verbatim(self, experience: Dict, workflow_id: str) -> List[str]:
        """
        GAP 3 FIX: Step 1: Extract verbatim bullets.
        No longer a simple [:2] mock. Selects bullets that contain metrics.
        """
        metric_pattern = re.compile(r'[%$]|\d')
        bullet_pool = experience.get('bullet_pool', [])
        
        metric_bullets = [
            b for b in bullet_pool 
            if metric_pattern.search(b)
        ]
        
        # Fallback if no metric bullets are found
        if not metric_bullets:
            metric_bullets = bullet_pool[:2]
            
        return metric_bullets[:3] # Take top 3 metric bullets

    async def run_customized(self, prompt: str, experience: Dict, workflow_id: str) -> List[str]:
        """Step 2: Customize existing bullets"""
        # Design-Aligned: Use bullet_generator_model (Gemini 2.5 Pro)
        client = self.get_model_client("bullet_generator_model")
        
        gen_prompt = f"{prompt}\nCustomize these bullets:\n{json.dumps(experience.get('bullet_pool', []))}\nGenerate 2-3 achievement bullets. Output as JSON array of strings."
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": gen_prompt}], 
            temperature=self.config.model_config.bullet_generator_model.temperature, 
            response_format="json_object"
        )
        return response["content"]

    async def run_synthetic(self, prompt: str, experience: Dict, workflow_id: str) -> List[str]:
        """Step 3: Generate new synthetic bullets"""
        # Design-Aligned: Use bullet_generator_model (Gemini 2.5 Pro)
        client = self.get_model_client("bullet_generator_model")
        
        gen_prompt = f"{prompt}\nExperience (no bullets):\n{json.dumps({'title': experience.get('title'), 'company': experience.get('company')})}\nGenerate 2 new achievement bullets. Output as JSON array of strings."
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": gen_prompt}], 
            temperature=self.config.model_config.bullet_generator_model.temperature, 
            response_format="json_object"
        )
        return response["content"]

    async def run_fact_check(self, bullets: List[str], experience: Dict, workflow_id: str) -> List[str]:
        """Step 4: Fact-check synthetic bullets (No longer mock)"""
        self.log_info("Fact-checking bullets...")
        # Design-Aligned: Use bullet_fact_check_model (Gemini 2.5 Flash)
        client = self.get_model_client("bullet_fact_check_model")

        prompt = f"""You are a fact-checker. Review the following bullets against the source experience.
Filter out any bullets that contain plausible-sounding but unverified claims (hallucinations).

Source Experience:
{json.dumps(experience)}

Bullets to Check:
{json.dumps(bullets)}

Output JSON containing *only* the bullets that are factually supported by the source:
{{"verified_bullets": ["bullet1", "bullet2", ...]}}
"""
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.bullet_fact_check_model.temperature,
            response_format="json_object"
        )
        return response["content"].get("verified_bullets", [])

class AsyncBulletCritiqueAgent(BaseAgent):
    """ROW 7: Async bullet critique with feedback-aware strategy"""
    
    async def run_async(self, bullets: List[Dict], critique_prompt: str, workflow_id: str) -> List[Dict]:
        """Critique bullets with feedback-aware strategy"""
        self.log_info("Critiquing bullets with feedback awareness...")
        
        feedback_reader = self.context.feedback_reader
        critique_feedback = feedback_reader.read_recent_feedback(max_entries=20)
        
        parallel_successes = sum(1 for f in critique_feedback if f.task == "parallel_critique" and f.feedback_type == "success")
        sequential_successes = sum(1 for f in critique_feedback if f.task == "sequential_critique" and f.feedback_type == "success")
        
        use_parallel = parallel_successes >= sequential_successes
        strategy = "parallel" if use_parallel else "sequential"
        
        self.log_info(f"Using {strategy} critique strategy based on feedback")
        
        # Design-Aligned: Use critique_model (Gemini 2.5 Flash)
        client = self.get_model_client("critique_model")
        
        bullet_texts = [b['text'] for b in bullets]
        
        critique_results = []
        
        if use_parallel:
            critique_tasks = []
            for bullet in bullet_texts:
                task_prompt = f"{critique_prompt}\nBullet: {bullet}\nOutput JSON with score 0-10 and suggestions."
                critique_tasks.append(
                    client.chat_completion_async(
                        messages=[{"role": "user", "content": task_prompt}],
                        temperature=self.config.model_config.critique_model.temperature,
                        response_format="json_object"
                    )
                )
            critiques = await asyncio.gather(*critique_tasks)
            critique_results = [c["content"] for c in critiques]
            self.log_feedback(workflow_id, "parallel_critique", "success", {"bullets_critiqued": len(bullets), "strategy": "parallel"})
        else:
            for bullet in bullet_texts:
                task_prompt = f"{critique_prompt}\nBullet: {bullet}\nOutput JSON with score 0-10 and suggestions."
                critique = await client.chat_completion_async(
                    messages=[{"role": "user", "content": task_prompt}],
                    temperature=self.config.model_config.critique_model.temperature,
                    response_format="json_object"
                )
                critique_results.append(critique["content"])
            self.log_feedback(workflow_id, "sequential_critique", "success", {"bullets_critiqued": len(bullets), "strategy": "sequential"})
        
        # Combine original bullets with critiques
        final_critiqued_bullets = []
        for i, original_bullet in enumerate(bullets):
            final_critiqued_bullets.append({
                "text": original_bullet['text'],
                "experience": original_bullet['experience'],
                "critique": critique_results[i]
            })
            
        return final_critiqued_bullets

# ============================================================================
# ROW 7: HIL STACK (Ambiguity Detection)
# ============================================================================

class HILAmbiguityDetectorAgent(BaseAgent):
    """Proactively detects ambiguity to trigger HIL"""
    
    async def run_async(self, strategy: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Detect ambiguity in the strategy"""
        self.log_info("Detecting ambiguity...")
        
        # Design-Aligned: Use qa_model (Gemini 2.5 Flash)
        client = self.get_model_client("qa_model")
        
        prompt = f"""Analyze this strategy for ambiguity.
Strategy: {json.dumps(strategy)}

Is the strategy vague, conflicting, or requires human clarification?
Output JSON:
{{
  "ambiguity_detected": true/false,
  "confidence": 0.0-1.0,
  "reason": "Why it is/isn't ambiguous",
  "question_for_human": "If ambiguous, what question needs to be asked?"
}}"""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object"
        )
        
        result = response["content"]
        
        self.log_feedback(workflow_id, "ambiguity_detection", "success", {"detected": result.get("ambiguity_detected", False)})
        return result

class HILFeedbackRouterAgent(BaseAgent):
    """Routes human feedback to the correct next step"""
    
    async def run_async(self, human_feedback: str, workflow_id: str) -> Dict[str, Any]:
        """Routes human feedback"""
        self.log_info(f"Routing human feedback: {human_feedback[:50]}...")
        
        # Log feedback to preference_log.jsonl
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
            self.log_error(f"Failed to log preference: {e}")

        # Design-Aligned: Use qa_model (Gemini 2.5 Flash) for routing
        client = self.get_model_client("qa_model")
        
        prompt = f"""You are a feedback router. Analyze the human's feedback and decide which graph node to jump to.
Human Feedback: "{human_feedback}"

Options are:
- "STRATEGY" (if they want to re-run the strategy)
- "BULLET_GENERATION" (if they want new or different bullets)
- "DRAFTING" (if they want to re-run the drafting process)

Output JSON: {{"next_step": "STRATEGY" | "BULLET_GENERATION" | "DRAFTING"}}
"""
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format="json_object"
        )
            
        return response["content"]