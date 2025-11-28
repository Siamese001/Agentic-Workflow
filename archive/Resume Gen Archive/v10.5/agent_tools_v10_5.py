# File: agent_tools_v10_5.py
# Version: 10.5 (Refactored)
#
# v10.5 REFACTOR CHANGES:
# - MOVED: Added HyDETool, ChromaDBSearchTool, and BM25SearchTool from
#   agent_stacks_v10_5.py to centralize all tools.
# - ADDED: New imports (BM25, chromadb, pydantic) to support
#   the moved RAG tools.
# - ARCHITECTURE FIX: Updated import for BaseTool to pull from
#   core_v10_5.py instead of agent_stacks_v10_5.py. This resolves
#   the circular import dependency.
#
# v10.5 MAJOR CHANGES:
# - IMPLEMENTED (Fix #1): All tools refactored to use _run_async_internal
#   to support BaseTool's new caching wrapper.
# - IMPLEMENTED (Fix #4): DraftingRefinerTool updated to accept 'critique_2'
#   for the Debate Pattern.
# - IMPLEMENTED (Fix #8): @track_metrics decorator added to ALL tools.
# - IMPLEMENTED (Fix #13): Added new local tool 'QAWordCountValidatorTool'
#   which uses the SemanticValidator service.
# - FIXED: All v10_4 imports and class names updated to v10_5.
# - FIXED: All tools now correctly pass a comprehensive set of default
#   keys to prompt_template.format() to prevent KeyErrors.
# - FIXED (TEST): Removed local _format_prompt_with_defaults and now
#   import the centralized version from core_v10_5.py to fix 5 KeyErrors.

import json
import logging
import asyncio # v10.5 REFACTOR: Added
import uuid # v10.5 REFACTOR: Added
from typing import Dict, Any, List

# v10.5 REFACTOR: Added imports for RAG tools
from pydantic import BaseModel, Field
from chromadb.utils import embedding_functions
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    logging.getLogger("agent_tools_v10_5").warning(
        "rank_bm25 not installed. BM25SearchTool will be unavailable. "
        "Run 'pip install rank-bm25'"
    )

# v10.5: Import from new core
from core_v10_5 import (
    WorkflowContext, 
    PydanticSchemaError,
    # Import all 15 Pydantic output models
    BaseToolOutput,
    DraftStrategyOutput,
    RedTeamOutput,
    RefineSectionOutput,
    AddMetricsOutput,
    QAClaimOutput,
    QAToneOutput,
    QAThematicAlignmentOutput,
    QASemanticEntailmentOutput,
    QANarrativeThreadOutput,
    QAJDSkillsOutput,
    QASignalScoreOutput,
    QATenureOutput,
    QAMissedOpportunitiesOutput,
    QAAdversarialOutput,
    QABiasOutput,
    # v10.5: Import new decorator
    track_metrics,
    BaseTool, # v10.5 ARCHITECTURE FIX: Import BaseTool from core
    # v10.5 TEST FIX: Import centralized prompt formatter
    _format_prompt_with_defaults
)
# v10.5: Import from new stacks
from agent_stacks_v10_5 import BiasDetectorAgent # Import from stacks

# v10.5: Logger name updated
logger = logging.getLogger("agent_tools_v10_5")

# ============================================================================
# ROW 7: DRAFTING STACK (ReAct Conductor with REAL Tools)
# ============================================================================

# --- Helper function for formatting prompts ---

# v10.5 TEST FIX: Removed local _format_prompt_with_defaults function.
# Now importing the centralized version from core_v10_5.py.

# --- Drafting Tools (v10.5: Validated, Prompts Centralized, Cached) ---

class DraftingStrategistTool(BaseTool):
    """(Gemini 2.5 Pro) Reviews the overall strategy and ensures the draft aligns."""
    tool_name = "review_draft_strategy"
    output_model = DraftStrategyOutput

    @track_metrics('tool_drafting_strategist') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Reviewing draft strategy (v10.5)...")
        client = self.get_model_client("drafting_strategist_model")
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.5 TEST FIX: Use centralized formatter
        prompt = _format_prompt_with_defaults(prompt_template, tool_input, self.budget_manager)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_strategist_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class DraftingRedTeamTool(BaseTool):
    """(Claude 4.1 Opus) Aggressively critiques the draft for weaknesses."""
    tool_name = "red_team_critique"
    output_model = RedTeamOutput

    @track_metrics('tool_drafting_redteam') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Red teaming draft (v10.5)...")
        client = self.get_model_client("drafting_redteam_model")
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.5 TEST FIX: Use centralized formatter
        prompt = _format_prompt_with_defaults(prompt_template, tool_input, self.budget_manager)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_redteam_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class DraftingRefinerTool(BaseTool):
    """(GPT-5) Refines and rewrites specific sections."""
    tool_name = "refine_section"
    output_model = RefineSectionOutput

    @track_metrics('tool_drafting_refiner') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Refining section (Debate Pattern) (v10.5)...")
        client = self.get_model_client("drafting_refiner_model")
        
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.5 (Fix #4): _format_prompt_with_defaults will now correctly
        # populate 'critique' AND 'critique_2' if they exist in tool_input
        # v10.5 TEST FIX: Use centralized formatter
        prompt = _format_prompt_with_defaults(prompt_template, tool_input, self.budget_manager)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_refiner_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class DraftingMetricsTool(BaseTool):
    """(Gemini 2.5 Flash) Finds opportunities to add metrics to bullets."""
    tool_name = "add_metrics"
    output_model = AddMetricsOutput

    @track_metrics('tool_drafting_metrics') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Adding metrics (v10.5)...")
        client = self.get_model_client("drafting_metrics_model")
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.5 TEST FIX: Use centralized formatter
        prompt = _format_prompt_with_defaults(prompt_template, tool_input, self.budget_manager)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_metrics_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

# ============================================================================
# ROW 7: RAG STACK TOOLS (v10.5: Refactored)
# ============================================================================

# --- v10.5 REFACTOR: Moved HyDETool, ChromaDBSearchTool, BM25SearchTool here ---

class HyDETool(BaseTool):
    """(HyDE) Generates hypothetical documents for query expansion."""
    tool_name = "generate_hypothetical_documents"

    class HyDEOutput(BaseModel):
        hypothetical_document: str = Field(..., description="A hypothetical document that answers the query.")

    @track_metrics('run_hyde_tool') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Running HyDE (v10.5)...")
        client = self.get_model_client("hyde_model")
        
        query = tool_input.get("query", "")
        if not query:
            return {"status": "error", "hypothetical_document": "No query provided."}

        prompt_template = self.prompt_manager.get_template("hyde_generation")
        # v10.5 TEST FIX: Use centralized formatter
        prompt = _format_prompt_with_defaults(prompt_template, tool_input, self.budget_manager)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.hyde_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.HyDEOutput)
        if error:
            self.log_warning(f"HyDE validation failed: {error}. Using raw query.")
            return {"status": "error", "hypothetical_document": query} # Fallback
            
        return {"status": "success", "hypothetical_document": validated_output.hypothetical_document}


class ChromaDBSearchTool(BaseTool):
    """v10.5: Searches the resume database using ChromaDB (Vector Search)."""
    tool_name = "search_resume_database"

    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection_name = self.config.chromadb_config.default_collection_name
        self.chroma_client = self.context.chromadb_client
        
    @track_metrics('run_chroma_tool') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
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
                where={"workflow_id": workflow_id} # Filter by workflow_id
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

class BM25SearchTool(BaseTool):
    """v10.5: Searches the resume using BM25 (Keyword Search)."""
    tool_name = "search_resume_bm25"

    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        if not BM25_AVAILABLE:
            self.log_error("BM25SearchTool disabled: 'rank_bm25' not installed.")
    
    @track_metrics('run_bm25_tool') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
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
            def do_bm25_search():
                tokenized_corpus = [doc.split(" ") for doc in corpus_text]
                bm25 = BM25Okapi(tokenized_corpus)
                tokenized_query = query.split(" ")
                doc_scores = bm25.get_scores(tokenized_query)
                indexed_scores = [(i, score) for i, score in enumerate(doc_scores)]
                indexed_scores.sort(key=lambda x: x[1], reverse=True)
                search_results = [corpus_metadata[i] for i, score in indexed_scores[:5] if score > 0]
                return search_results
            
            search_results = await asyncio.to_thread(do_bm25_search)

            self.log_feedback(workflow_id, "bm25_search", "success", {"results_found": len(search_results)})
            return {"search_results": search_results}
            
        except Exception as e:
            self.log_error(f"Failed to run BM25 search: {e}")
            return {"search_results": []}

# ============================================================================
# ROW 7: QA STACK (ReAct Conductor with 11+ REAL Tools)
# ============================================================================

# --- QA Tools (v10.5: Validated, Prompts Centralized, Cached) ---

class QABaseValidatorTool(BaseTool):
    """Base class for the 10 T2 validator tools"""
    model_config_name = "qa_validator_model" # Gemini 2.5 Flash
    output_model: Any = BaseToolOutput # Subclasses must override this
    
    @track_metrics('tool_qa_base_validator') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Running {self.tool_name} (v10.5)...")
        client = self.get_model_client(self.model_config_name)
        
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        # v10.5 TEST FIX: Use centralized formatter
        prompt = _format_prompt_with_defaults(prompt_template, tool_input, self.budget_manager)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_validator_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class QAClaimValidatorTool(QABaseValidatorTool):
    """(NLI) Checks if claims in the draft are supported by the master resume."""
    tool_name = "validate_claims"
    output_model = QAClaimOutput 
    
    # v10.5: Override track_metrics for specific task name
    @track_metrics('tool_qa_claim_validator')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QAToneValidatorTool(QABaseValidatorTool):
    """Checks if the draft's tone matches the strategy (e.g., 'leadership')."""
    tool_name = "validate_tone"
    output_model = QAToneOutput
    @track_metrics('tool_qa_tone_validator')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QAThematicAlignmentTool(QABaseValidatorTool):
    """Ensures all sections support the central strategy theme."""
    tool_name = "validate_thematic_alignment"
    output_model = QAThematicAlignmentOutput
    @track_metrics('tool_qa_thematic_alignment')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QASemanticEntailmentTool(QABaseValidatorTool):
    """Checks if bullets are semantically entailed by the job description."""
    tool_name = "validate_semantic_entailment"
    output_model = QASemanticEntailmentOutput
    @track_metrics('tool_qa_semantic_entailment')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QANarrativeThreadTool(QABaseValidatorTool):
    """Checks for a consistent career story/narrative."""
    tool_name = "validate_narrative_thread"
    output_model = QANarrativeThreadOutput
    @track_metrics('tool_qa_narrative_thread')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QAJDSkillsValidatorTool(QABaseValidatorTool):
    """Ensures keywords/skills from the JD are present in the draft."""
    tool_name = "validate_jd_skills"
    output_model = QAJDSkillsOutput
    @track_metrics('tool_qa_jd_skills')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QASignalScoreValidatorTool(QABaseValidatorTool):
    """Rates the 'signal' (achievement) vs 'noise' (fluff) of each bullet."""
    tool_name = "validate_signal_score"
    output_model = QASignalScoreOutput
    @track_metrics('tool_qa_signal_score')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QATenureValidatorTool(QABaseValidatorTool):
    """Checks for consistency in dates and tenure."""
    tool_name = "validate_tenure"
    output_model = QATenureOutput
    @track_metrics('tool_qa_tenure')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QAMissedOpportunityTool(QABaseValidatorTool):
    """Looks for experience in the master resume that was omitted but is relevant."""
    tool_name = "find_missed_opportunities"
    output_model = QAMissedOpportunitiesOutput
    @track_metrics('tool_qa_missed_opportunity')
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        return await super()._run_async_internal(tool_input, workflow_id)

class QAAdversarialReviewerTool(BaseTool):
    """(Claude 4.1 Opus) Acts as a skeptical hiring manager to find flaws."""
    tool_name = "adversarial_review"
    output_model = QAAdversarialOutput 

    @track_metrics('tool_qa_adversarial') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Running Adversarial Review (v10.5)...")
        client = self.get_model_client("qa_adversarial_model")
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.5 TEST FIX: Use centralized formatter
        prompt = _format_prompt_with_defaults(prompt_template, tool_input, self.budget_manager)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_adversarial_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class QABiasDetectorTool(BaseTool):
    """(Local) Runs the local bias detector tool on the final draft."""
    tool_name = "validate_bias"
    output_model = QABiasOutput

    @track_metrics('tool_qa_bias_detector') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        # This is a local tool, not an LLM call.
        bias_agent = BiasDetectorAgent(self.context)
        draft_text = json.dumps(tool_input.get("draft_text", ""))
        
        # v10.5 TEST FIX: Use await, as BiasDetectorAgent.run is now async
        # due to the @track_metrics decorator
        result_dict = await bias_agent.run(draft_text, workflow_id)
        
        # We still validate to ensure the contract is met
        validated_output, error = self.validator.validate(result_dict, self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

# v10.5 (Fix #13): New Local Semantic Validator Tool

class QAWordCountValidatorTool(BaseTool):
    """(Local) Runs deterministic word count check."""
    tool_name = "validate_word_count"
    
    class WordCountOutput(BaseToolOutput):
        validation_passed: bool
        message: str
        deterministic_count: int

    output_model = WordCountOutput

    @track_metrics('tool_qa_word_count') # v10.5 (Fix #8)
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Running Word Count Validator (v10.5)...")
        
        # Get inputs from the tool_input dict
        text_to_check = tool_input.get("text_to_check", "")
        min_words = tool_input.get("min_words", 50)
        max_words = tool_input.get("max_words", 150)
        llm_reported_count = tool_input.get("llm_reported_count") # Optional
        
        # Use the injected SemanticValidator service
        validator = self.context.semantic_validator
        
        validation_passed, message = validator.check_word_count(
            text=text_to_check,
            min_words=min_words,
            max_words=max_words,
            llm_reported_count=llm_reported_count,
            workflow_id=workflow_id
        )
        
        # This is a local tool, so we just build the output dict
        result_dict = {
            "status": "success",
            "validation_passed": validation_passed,
            "message": message,
            "deterministic_count": len(text_to_check.split())
        }

        # We still validate our *own* output to ensure contract
        validated_output, error = self.validator.validate(result_dict, self.output_model)
        if error:
            # This should never happen if result_dict is correct
            raise PydanticSchemaError(f"Tool {self.tool_name} failed its own output validation: {error}")
            
        return validated_output.model_dump()