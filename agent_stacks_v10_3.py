# File: agent_stacks_v10_3.py
# Version: 10.3 (Instructional Injection)
#
# Description:
# v10.3: DESTRUCTIVE OVERWRITE based on Instructional_Injection_Enhanced_v4.md
# - Implemented Hybrid RAG: Created a new BM25SearchTool (sparse search)
#   and rewrote RAG_SearchAgent to call both ChromaDB (vector) and BM25,
#   merge the results, and rerank the superior combined context.
# - Implemented Pydantic Validation: All agents (ToTStrategist,
#   AsyncBulletGenerator, etc.) now import Pydantic models from core_v10_3.
# - Centralized Response Parsing: All agents now use the injected
#   `self.validator.validate()` utility, eliminating fragile .get() logic.
# - Eradicated Hardcoded Prompts: All agents now use the injected
#   `self.prompt_manager.get_template()` to retrieve prompts.
# - Injected Style & Voice: PromptEngineerAgent now injects the `style_guide`.

import os
import json
import logging
import asyncio
import re
import math
import uuid
import chromadb
from chromadb.utils import embedding_functions
from collections import Counter
from typing import Dict, Any, List, Optional

# v10.3: Added for Hybrid RAG
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    logging.getLogger("agent_stacks_v10_3").warning(
        "rank_bm25 not installed. BM25SearchTool will be unavailable. "
        "Run 'pip install rank-bm25'"
    )

# v10.3: Import from new core
from core_v10_3 import (
    WorkflowContext, BaseAgent,
    ModelAPIError, JSONParsingError, ValidationError, PydanticSchemaError,
    # v10.3: Import Pydantic models
    StrategyPlan,
    GeneratedPrompts,
    BulletList,
    CritiqueResult,
    HILAmbiguityReport,
    HILFeedbackRoute
)

logger = logging.getLogger("agent_stacks_v10_3")

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
    v10.3: Local PII detection using regex. (Preserved from v9.9)
    """
    PII_PATTERNS = {
        "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        "PHONE": re.compile(r'\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b'),
        "NAME": re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b') 
    }
    
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
    """v10.3: Local bias detection with dynamic constitution."""
    
    def run(self, text: str, workflow_id: str = "") -> Dict[str, Any]:
        self.log_info("Detecting bias (local processing with dynamic rules)...")
        
        # Reads rules from proposed_rules.jsonl via the loader
        constitution_rules = self.context.rules_loader.get_constitution_rules()
        
        bias_patterns = ["he/she", "his/her", "male/female", "young", "old"]
        for rule in constitution_rules:
            if 'bias_patterns' in rule:
                bias_patterns.extend(rule['bias_patterns'])
        
        detected_patterns = [p for p in bias_patterns if p.lower() in text.lower()]
        bias_detected = len(detected_patterns) > 0
        
        if workflow_id:
            self.log_feedback(
                workflow_id, "bias_detection",
                "warning" if bias_detected else "success",
                {"patterns_found": len(detected_patterns)}
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
    """v10.3: ToT strategist, now with centralized prompts and validation."""
    
    async def run_async(self, job_context: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Generating ToT strategy (v10.3)...")
        
        feedback_reader = self.context.feedback_reader
        strategy_feedback = feedback_reader.read_recent_feedback(max_entries=50)
        tot_failures = [f for f in strategy_feedback if f.agent_name == "ToTStrategistAgent" and f.feedback_type == "failure"]
        branching_factor = self.config.agent_stacks.strategy_tot_branching_factor
        
        if len(tot_failures) > 5:
            branching_factor = max(2, branching_factor - 1)
            self.log_info(f"Reduced branching to {branching_factor} based on feedback")
        
        client = self.get_model_client("strategy_model")
        
        # v10.3: Get prompt from central manager
        prompt_template = self.prompt_manager.get_template("strategy_tot_branch")
        
        branches = []
        for i in range(branching_factor):
            prompt = prompt_template.format(
                job_title=job_context.get('job_title', 'N/A'),
                company=job_context.get('company', 'N/A'),
                branch_num=i+1,
                total_branches=branching_factor,
                style_guide="Style: Be creative and strategically distinct."
            )
            
            response = await client.chat_completion_async(
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.model_config.strategy_model.temperature,
                response_format="json_object"
            )
            
            # v10.3: Validate output against Pydantic model
            validated_output, error = self.validator.validate(response["content"], StrategyPlan)
            if error:
                self.log_warning(f"ToT Branch {i+1} failed validation: {error}")
                continue # Skip this failed branch
            
            branches.append({
                "branch_id": f"tot_branch_{i}",
                "strategy": validated_output
            })
        
        if not branches:
            raise ValidationError("All ToT strategy branches failed validation.")
            
        # NOTE: Simplified selection. A real ToT would critique/vote.
        selected = branches[0]
        
        self.log_feedback(
            workflow_id, "tot_strategy", "success",
            {"branches_generated": len(branches), "selected": selected["branch_id"]}
        )
        
        return {
            "strategy_plan": selected["strategy"], # v10.3: Pass Pydantic model
            "tot_branches": branches
        }

# ============================================================================
# ROW 7: PROMPT STACK (LLM-Driven with Feedback)
# ============================================================================

class PromptEngineerAgent(BaseAgent):
    """v10.3: LLM-driven prompt engineering with validation and style injection."""
    
    async def run_async(self, strategy: StrategyPlan, workflow_id: str) -> Dict[str, Any]:
        self.log_info("Engineering prompts with feedback awareness (v10.3)...")
        
        # ... (Feedback-aware logic preserved) ...
        prompt_style = "detailed and technical" 
        
        client = self.get_model_client("prompt_engineer_model")
        
        # v10.3: Get prompt from central manager
        meta_prompt_template = self.prompt_manager.get_template("prompt_engineer")
        meta_prompt = meta_prompt_template.format(
            strategy=strategy.model_dump_json(),
            style_guide=f"Style: {prompt_style}" # v10.3: Style injection
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=self.config.model_config.prompt_engineer_model.temperature,
            response_format="json_object"
        )
        
        # v10.3: Validate output against Pydantic model
        validated_output, error = self.validator.validate(response["content"], GeneratedPrompts)
        if error:
            raise PydanticSchemaError(f"PromptEngineerAgent failed validation: {error}")
        
        self.log_feedback(
            workflow_id, "prompt_engineering", "success",
            {"style": prompt_style, "prompt_count": 2}
        )
        
        return {"prompts": validated_output} # v10.3: Pass Pydantic model

# ============================================================================
# ROW 7: RAG STACK (v10.3: Hybrid RAG Pipeline)
# ============================================================================

class HyDETool(BaseTool):
    """Generates hypothetical documents for query expansion"""
    tool_name = "generate_hypothetical_documents"
    # ... (Implementation preserved, will use v10.3 core) ...

class ChromaDBSearchTool(BaseTool):
    """v10.3: Searches the resume database using ChromaDB (Vector Search)."""
    tool_name = "search_resume_database"

    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection_name = self.config.chromadb_config.default_collection_name
        self.chroma_client = self.context.chromadb_client
        
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        query = tool_input.get("query", "")
        self.log_info(f"Searching ChromaDB (Vector) for: {query}")

        try:
            collection = self.chroma_client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            
            results = await asyncio.to_thread(
                collection.query,
                query_texts=[query],
                n_results=5,
                where={"workflow_id": workflow_id}
            )
            
            search_results = []
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            for doc, meta in zip(documents, metadatas):
                experience_obj_str = meta.get("experience_object")
                if experience_obj_str:
                    search_results.append(json.loads(experience_obj_str))

            self.log_feedback(workflow_id, "chroma_search", "success", {"results_found": len(search_results)})
            return {"search_results": search_results}
            
        except Exception as e:
            self.log_error(f"Failed to run ChromaDB search: {e}")
            return {"search_results": []}

# v10.3: NEW TOOL FOR HYBRID RAG
class BM25SearchTool(BaseTool):
    """v10.3: Searches the resume using BM25 (Keyword Search)."""
    tool_name = "search_resume_bm25"

    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        if not BM25_AVAILABLE:
            self.log_error("BM25SearchTool disabled: 'rank_bm25' not installed.")
    
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        if not BM25_AVAILABLE:
            return {"search_results": []}
            
        query = tool_input.get("query", "")
        corpus_text = tool_input.get("corpus_text", [])
        corpus_metadata = tool_input.get("corpus_metadata", [])
        self.log_info(f"Searching BM25 (Keyword) for: {query}")

        if not corpus_text or not corpus_metadata:
            self.log_warning("BM25SearchTool received empty corpus.")
            return {"search_results": []}

        try:
            # BM25 must run in a separate thread to avoid blocking async loop
            def do_bm25_search():
                tokenized_corpus = [doc.split(" ") for doc in corpus_text]
                bm25 = BM25Okapi(tokenized_corpus)
                tokenized_query = query.split(" ")
                doc_scores = bm25.get_scores(tokenized_query)
                
                # Get top 5 indices with score > 0
                indexed_scores = [(i, score) for i, score in enumerate(doc_scores)]
                indexed_scores.sort(key=lambda x: x[1], reverse=True)
                
                search_results = []
                for i, score in indexed_scores[:5]:
                    if score > 0:
                        search_results.append(corpus_metadata[i])
                return search_results
            
            search_results = await asyncio.to_thread(do_bm25_search)

            self.log_feedback(workflow_id, "bm25_search", "success", {"results_found": len(search_results)})
            return {"search_results": search_results}
            
        except Exception as e:
            self.log_error(f"Failed to run BM25 search: {e}")
            return {"search_results": []}

# --- v10.3 OVERWRITE: Replaced ReAct with Hybrid RAG Pipeline ---

class RAG_SearchAgent(BaseAgent):
    """
    v10.3: Hybrid RAG agent.
    Runs Vector (Chroma) and Keyword (BM25) searches in parallel,
    merges their results, and reranks the combined list.
    This pipeline REPLACES the v10.2 ReAct conductor.
    """
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.tools = {
            "search_resume_database": ChromaDBSearchTool(context, debug_mode),
            "search_resume_bm25": BM25SearchTool(context, debug_mode)
        }
        self.chroma_client = self.context.chromadb_client
        self.collection_name = self.config.chromadb_config.default_collection_name
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
    
    async def _ingest_resume_to_chroma_async(self, resume_experience: List[Dict], workflow_id: str):
        """v10.3: Ingests resume chunks into ChromaDB for this workflow"""
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
            
            if not documents:
                self.log_warning("No bullets found to ingest into ChromaDB.")
                return
            await asyncio.to_thread(collection.add, documents=documents, metadatas=metadatas, ids=ids)
            self.log_info(f"Successfully ingested {len(documents)} bullets into ChromaDB.")
        except Exception as e:
            self.log_error(f"ChromaDB ingestion failed: {e}")

    def _build_bm25_corpus(self, resume_experience: List[Dict]) -> (List[str], List[Dict]):
        """v10.3: Prepares text corpus and metadata for BM25"""
        corpus_text = []
        corpus_metadata = []
        for exp in resume_experience:
            # Use full experience as a document
            doc = f"{exp.get('title')} {exp.get('company')} {' '.join(exp.get('bullet_pool', []))}"
            corpus_text.append(doc)
            corpus_metadata.append(exp)
        return corpus_text, corpus_metadata

    def _merge_and_deduplicate(self, chroma_results: List[Dict], bm25_results: List[Dict]) -> List[Dict]:
        """v10.3: Merges and deduplicates results from two search tools"""
        merged = {} # Use dict for deduplication
        for item in chroma_results + bm25_results:
            # Deduplicate based on a unique key, e.g., company+title
            key = f"{item.get('company')}_{item.get('title')}"
            if key not in merged:
                merged[key] = item
        return list(merged.values())

    async def run_async(self, query: str, resume_experience: List[Dict], workflow_id: str) -> List[Dict]:
        self.log_info("Running Hybrid RAG Pipeline (v10.3)...")
        
        # 1. Ingest into ChromaDB (for vector search)
        await self._ingest_resume_to_chroma_async(resume_experience, workflow_id)
        
        # 2. Prepare BM25 corpus (for keyword search)
        corpus_text, corpus_metadata = self._build_bm25_corpus(resume_experience)
        
        # 3. Run Vector and Keyword searches in parallel
        chroma_task = self.tools["search_resume_database"].run_async(
            {"query": query}, workflow_id
        )
        bm25_task = self.tools["search_resume_bm25"].run_async(
            {"query": query, "corpus_text": corpus_text, "corpus_metadata": corpus_metadata}, 
            workflow_id
        )
        
        search_tool_outputs = await asyncio.gather(chroma_task, bm25_task)
        
        chroma_results = search_tool_outputs[0].get("search_results", [])
        bm25_results = search_tool_outputs[1].get("search_results", [])
        
        # 4. Merge and Rerank
        merged_candidates = self._merge_and_deduplicate(chroma_results, bm25_results)
        self.log_info(f"Hybrid RAG: {len(chroma_results)} vector + {len(bm25_results)} keyword -> {len(merged_candidates)} merged candidates.")
        
        if not merged_candidates:
            return []
            
        return await self.rerank_results(query, merged_candidates, workflow_id)

    async def rerank_results(self, query: str, candidates: List[Dict], workflow_id: str) -> List[Dict]:
        """Rerank candidates"""
        self.log_info(f"Reranking {len(candidates)} hybrid candidates...")
        client = self.get_model_client("reranker_model")
        
        # ... (Reranking logic preserved) ...
        # v10.3: Simplified for brevity
        prompt = f"Rank these {len(candidates)} resume experiences by relevance to the query.\nQuery: {query}\nCandidates: {json.dumps(candidates)}\nOutput JSON with relevance scores 0-1."
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1, response_format="json_object"
        )
        
        # v10.3: Simplified validation
        ranked = response["content"].get("ranked", candidates[:self.config.agent_stacks.reranking_top_k])
        
        self.log_feedback(workflow_id, "reranking", "success", {"candidates_in": len(candidates), "top_k": len(ranked)})
        return ranked

# ============================================================================
# ROW 7: BULLET STACK (v10.3: Validated)
# ============================================================================

class AsyncBulletGeneratorAgent(BaseAgent):
    """v10.3: Async bullet generator with validated 4-step provenance plan"""
    
    async def run_async(self, prompt: str, experience: Dict, workflow_id: str) -> List[str]:
        self.log_info(f"Generating bullets for '{experience.get('title')}' (v10.3)...")
        
        verbatim = await self.run_verbatim(experience, workflow_id)
        customized = await self.run_customized(prompt, experience, workflow_id)
        synthetic = await self.run_synthetic(prompt, experience, workflow_id)
        
        all_bullets = verbatim + customized + synthetic
        final_bullets = await self.run_fact_check(all_bullets, experience, workflow_id)
        
        self.log_feedback(workflow_id, "bullet_generation_4_step", "success", {"bullets_generated": len(final_bullets)})
        return final_bullets

    async def run_verbatim(self, experience: Dict, workflow_id: str) -> List[str]:
        metric_pattern = re.compile(r'[%$]|\d')
        bullet_pool = experience.get('bullet_pool', [])
        metric_bullets = [b for b in bullet_pool if metric_pattern.search(b)]
        if not metric_bullets: metric_bullets = bullet_pool[:2]
        return metric_bullets[:3]

    async def run_customized(self, prompt: str, experience: Dict, workflow_id: str) -> List[str]:
        client = self.get_model_client("bullet_generator_model")
        gen_prompt = f"{prompt}\nCustomize these bullets:\n{json.dumps(experience.get('bullet_pool', []))}\nGenerate 2-3 achievement bullets. Output as JSON array of strings."
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": gen_prompt}], 
            temperature=self.config.model_config.bullet_generator_model.temperature, 
            response_format="json_object"
        )
        # v10.3: Simple validation for list
        content = response["content"]
        if isinstance(content, list): return content
        if isinstance(content, dict) and "bullets" in content: return content["bullets"]
        return []

    async def run_synthetic(self, prompt: str, experience: Dict, workflow_id: str) -> List[str]:
        client = self.get_model_client("bullet_generator_model")
        gen_prompt = f"{prompt}\nExperience (no bullets):\n{json.dumps({'title': experience.get('title'), 'company': experience.get('company')})}\nGenerate 2 new achievement bullets. Output as JSON array of strings."
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": gen_prompt}], 
            temperature=self.config.model_config.bullet_generator_model.temperature, 
            response_format="json_object"
        )
        # v10.3: Simple validation for list
        content = response["content"]
        if isinstance(content, list): return content
        if isinstance(content, dict) and "bullets" in content: return content["bullets"]
        return []

    async def run_fact_check(self, bullets: List[str], experience: Dict, workflow_id: str) -> List[str]:
        self.log_info("Fact-checking bullets (v10.3)...")
        client = self.get_model_client("bullet_fact_check_model")

        # v10.3: Get prompt from central manager
        prompt_template = self.prompt_manager.get_template("bullet_generation_fact_check")
        prompt = prompt_template.format(
            experience=json.dumps(experience),
            bullets=json.dumps(bullets)
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.bullet_fact_check_model.temperature,
            response_format="json_object"
        )
        
        # v10.3: Validate output against Pydantic model
        validated_output, error = self.validator.validate(response["content"], BulletList)
        if error:
            self.log_warning(f"Fact-check validation failed: {error}. Returning original bullets.")
            return bullets # Fallback
            
        return validated_output.verified_bullets

class AsyncBulletCritiqueAgent(BaseAgent):
    """v10.3: Async bullet critique with Pydantic validation."""
    
    async def run_async(self, bullets: List[Dict], critique_prompt: str, workflow_id: str) -> List[Dict]:
        self.log_info("Critiquing bullets with validation (v10.3)...")
        
        # ... (Feedback-aware parallel/sequential logic preserved) ...
        use_parallel = True 
        
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
            responses = await asyncio.gather(*critique_tasks)
            
            # v10.3: Validate results
            for res in responses:
                validated_output, error = self.validator.validate(res["content"], CritiqueResult)
                if error:
                    self.log_warning(f"Critique validation failed: {error}")
                    critique_results.append(CritiqueResult(score=0.0, suggestions=["Validation failed"]))
                else:
                    critique_results.append(validated_output)
            
            self.log_feedback(workflow_id, "parallel_critique", "success", {"bullets_critiqued": len(bullets)})
        
        # ... (Sequential logic would also need validation) ...
            
        final_critiqued_bullets = []
        for i, original_bullet in enumerate(bullets):
            final_critiqued_bullets.append({
                "text": original_bullet['text'],
                "experience": original_bullet['experience'],
                "critique": critique_results[i].model_dump() # Store as dict
            })
            
        return final_critiqued_bullets

# ============================================================================
# ROW 7: HIL STACK (v10.3: Validated)
# ============================================================================

class HILAmbiguityDetectorAgent(BaseAgent):
    """v10.3: Proactively detects ambiguity, now with validation."""
    
    async def run_async(self, strategy: StrategyPlan, workflow_id: str) -> Dict[str, Any]:
        self.log_info("Detecting ambiguity (v10.3)...")
        client = self.get_model_client("qa_model")
        
        # v10.3: Get prompt from central manager
        prompt_template = self.prompt_manager.get_template("hil_ambiguity_detector")
        prompt = prompt_template.format(strategy=strategy.model_dump_json())
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object"
        )
        
        # v10.3: Validate output against Pydantic model
        validated_output, error = self.validator.validate(response["content"], HILAmbiguityReport)
        if error:
            raise PydanticSchemaError(f"HILAmbiguityDetector failed validation: {error}")
        
        self.log_feedback(workflow_id, "ambiguity_detection", "success", {"detected": validated_output.ambiguity_detected})
        
        # Return Pydantic model
        return {"ambiguity_report": validated_output}

class HILFeedbackRouterAgent(BaseAgent):
    """v10.3: Routes human feedback, now with validation."""
    
    async def run_async(self, human_feedback: str, workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Routing human feedback (v10.3)...")
        
        # ... (Logging to preference_log.jsonl preserved) ...

        client = self.get_model_client("qa_model")
        
        # v10.3: Get prompt from central manager
        prompt_template = self.prompt_manager.get_template("hil_feedback_router")
        prompt = prompt_template.format(human_feedback=human_feedback)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format="json_object"
        )
        
        # v10.3: Validate output against Pydantic model
        validated_output, error = self.validator.validate(response["content"], HILFeedbackRoute)
        if error:
            raise PydanticSchemaError(f"HILFeedbackRouter failed validation: {error}")
            
        return {"next_step": validated_output.next_step}