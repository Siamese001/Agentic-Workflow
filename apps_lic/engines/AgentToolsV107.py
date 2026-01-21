# File: agent_tools_v10_7.py
# Version: 10.7 (Refactored)
#
# v10.7 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_7.
# - REFACTORED (Fix #14, #17, #19, #20, #24): All tools (Drafting, RAG, QA)
#   refactored to use the new *asynchronous* _format_prompt_with_defaults
#   from core_v10_7. This correctly injects Goal State, Top Failures,
#   Cognitive Modes, Reflection steps, and uses agentic pruning.
#
# v10.7 MAJOR CHANGES:
# - IMPLEMENTED (Fix #8): Added new stubbed tools 'UIUpdateElementTool'
#   and 'UIFireEventTool' for UI control.
# - FIXED: All v10_5 imports and class names updated to v10_7.
# - FIXED (Bug): QABiasDetectorTool now correctly calls the synchronous
#   'bias_agent.run' method from within its async method using
#   'asyncio.to_thread' to prevent blocking the event loop.

import asyncio
import json
import logging
import uuid
from typing import Any

from pydantic import BaseModel, Field

try:
    from rank_bm25 import BM25Okapi

    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    logging.getLogger("agent_tools_v10_7").warning(
        "rank_bm25 not installed. BM25SearchTool will be unavailable. Run 'pip install rank-bm25'"
    )

# v10.7: Import from new core
from core_v10_7 import (
    AddMetricsOutput,
    BaseTool,
    # Import all 15 Pydantic output models
    BaseToolOutput,
    DraftStrategyOutput,
    MCPClientStub,
    PydanticSchemaError,
    QAAdversarialOutput,
    QABiasOutput,
    QAClaimOutput,
    QAJDSkillsOutput,
    QAMissedOpportunitiesOutput,
    QANarrativeThreadOutput,
    QASemanticEntailmentOutput,
    QASignalScoreOutput,
    QATenureOutput,
    QAThematicAlignmentOutput,
    QAToneOutput,
    RedTeamOutput,
    RefineSectionOutput,
    WorkflowContext,
    # v10.7: Import centralized prompt formatter
    _format_prompt_with_defaults,
    detect_bias,
    # v10.7: Import new decorator
    track_metrics,
)

# v10.7: Logger name updated
logger = logging.getLogger("agent_tools_v10_7")


def resolve_mcp_client(
    tool: "BaseTool",
    name: str,
    *,
    optional: bool = False,
    fallback_parameters: dict[str, Any] | None = None,
):
    """Helper that returns an MCP client or a stub fallback."""

    fallback_parameters = fallback_parameters or {}

    try:
        return tool.get_mcp_client(name)
    except KeyError as exc:
        if optional:
            tool.log_warning(f"MCP client '{name}' unavailable: {exc}. Using stub fallback.")
            stub = MCPClientStub(name, fallback_parameters)
            tool.context.get_mcp_client(name, default=stub)
            return stub
        raise


class DraftingLLMTool(BaseTool):
    """Shared async flow for drafting LLM tools."""

    model_client_key: str = ""
    output_model: type[BaseToolOutput] = BaseToolOutput
    log_action: str = ""

    @track_metrics("tool_drafting_llm")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        action = self.log_action or f"Running {self.tool_name}"
        self.log_info(f"Tool: {action} (v10.7)...")

        client = self.get_model_client(self.model_client_key)
        prompt_template = self.prompt_manager.get_template(self.tool_name)

        prompt = await _format_prompt_with_defaults(
            prompt_template, tool_input, self.budget_manager, client.goal_state, client.top_failures
        )

        temperature = self._get_model_temperature()
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")

        return validated_output.model_dump()

    def _get_model_temperature(self) -> float:
        try:
            model_config = getattr(self.config.model_config, self.model_client_key)
        except AttributeError as exc:
            raise AttributeError(
                f"Model config '{self.model_client_key}' not found for {self.__class__.__name__}"
            ) from exc

        temperature = getattr(model_config, "temperature", None)
        if temperature is None:
            raise AttributeError(
                f"Model config '{self.model_client_key}' for {self.__class__.__name__} lacks a 'temperature' value"
            )
        return float(temperature)


class DraftingStrategistTool(DraftingLLMTool):
    """(Gemini 2.5 Pro) Reviews the overall strategy and ensures the draft aligns."""

    tool_name = "review_draft_strategy"
    model_client_key = "drafting_strategist_model"
    output_model = DraftStrategyOutput
    log_action = "Reviewing draft strategy"


class DraftingRedTeamTool(DraftingLLMTool):
    """(Claude 4.1 Opus) Aggressively critiques the draft for weaknesses."""

    tool_name = "red_team_critique"
    model_client_key = "drafting_redteam_model"
    output_model = RedTeamOutput
    log_action = "Red teaming draft"


class DraftingRefinerTool(DraftingLLMTool):
    """(GPT-5) Refines and rewrites specific sections."""

    tool_name = "refine_section"
    model_client_key = "drafting_refiner_model"
    output_model = RefineSectionOutput
    log_action = "Refining section (Debate Pattern)"


class DraftingMetricsTool(DraftingLLMTool):
    """(Gemini 2.5 Flash) Finds opportunities to add metrics to bullets."""

    tool_name = "add_metrics"
    model_client_key = "drafting_metrics_model"
    output_model = AddMetricsOutput
    log_action = "Adding metrics"


class EvidenceClarificationTool(BaseTool):
    """Allows the evidence liaison to raise clarification requests."""

    tool_name = "request_evidence_clarification"

    class ClarificationRequestOutput(BaseToolOutput):
        request_id: str = Field(..., description="Unique id for the clarification request")
        recipient: str = Field(
            ..., description="Who should receive the request (e.g., 'bullet_team', 'rag_team')"
        )
        questions: list[str] = Field(..., description="Questions that need clarification")
        priority: str = Field("normal", description="Request priority level")
        context_summary: str = Field(
            "", description="Short summary of the ambiguity driving the request"
        )

    output_model = ClarificationRequestOutput

    @track_metrics("tool_request_evidence_clarification")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        self.log_info("Tool: Logging clarification request (v10.7 Guild)...")

        recipient = tool_input.get("recipient", "bullet_team")
        questions = [q for q in tool_input.get("questions", []) if isinstance(q, str) and q.strip()]
        if not questions:
            questions = ["Please confirm the data points for this section."]

        request_payload = {
            "status": "queued",
            "request_id": f"clar-{uuid.uuid4()}",
            "recipient": recipient,
            "questions": questions,
            "priority": tool_input.get("priority", "normal"),
            "context_summary": tool_input.get("context_summary", ""),
        }

        validated_output, error = self.validator.validate(request_payload, self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")

        return validated_output.model_dump()


class EvidenceBriefAssemblerTool(BaseTool):
    """Synthesizes structured evidence briefs for the drafting specialists."""

    tool_name = "assemble_evidence_brief"

    class EvidenceBriefOutput(BaseToolOutput):
        section: str = Field(..., description="Name of the section the brief supports")
        brief: str = Field(..., description="Short narrative of the supporting evidence")
        key_points: list[str] = Field(
            default_factory=list, description="Bullet-ready evidence points"
        )
        citations: list[str] = Field(
            default_factory=list, description="Reference identifiers or source hints"
        )
        outstanding_questions: list[str] = Field(
            default_factory=list, description="Clarifications still pending"
        )

    output_model = EvidenceBriefOutput

    @track_metrics("tool_assemble_evidence_brief")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        self.log_info("Tool: Assembling evidence brief (v10.7 Guild)...")

        section_name = tool_input.get("section", "general")
        draft_excerpt = tool_input.get("draft_content", "")
        evidence_points = tool_input.get("evidence_points", [])
        outstanding = [q for q in tool_input.get("open_questions", []) if isinstance(q, str)]

        if isinstance(draft_excerpt, dict):
            draft_excerpt = json.dumps(draft_excerpt)

        if not isinstance(evidence_points, list):
            evidence_points = [str(evidence_points)]

        brief_text = f"Evidence for {section_name}: "
        if evidence_points:
            brief_text += "; ".join(str(pt) for pt in evidence_points[:5])
        elif draft_excerpt:
            brief_text += draft_excerpt[:200]
        else:
            brief_text += "No direct evidence captured."

        result_dict = {
            "section": section_name,
            "brief": brief_text,
            "key_points": [str(pt) for pt in evidence_points[:5]],
            "citations": tool_input.get("citations", []),
            "outstanding_questions": outstanding,
        }

        validated_output, error = self.validator.validate(result_dict, self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")

        return validated_output.model_dump()


# ============================================================================
# ROW 7: RAG STACK TOOLS (v10.7: Refactored)
# ============================================================================


class HyDETool(BaseTool):
    """(HyDE) Generates hypothetical documents for query expansion."""

    tool_name = "generate_hypothetical_documents"

    class HyDEOutput(BaseModel):
        hypothetical_document: str = Field(
            ..., description="A hypothetical document that answers the query."
        )

    @track_metrics("run_hyde_tool")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        self.log_info("Tool: Running HyDE (v10.7)...")
        client = self.get_model_client("hyde_model")

        query = tool_input.get("query", "")
        if not query:
            return {"status": "error", "hypothetical_document": "No query provided."}

        prompt_template = self.prompt_manager.get_template("hyde_generation")

        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template, tool_input, self.budget_manager, client.goal_state, client.top_failures
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.hyde_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(response["content"], self.HyDEOutput)
        if error:
            self.log_warning(f"HyDE validation failed: {error}. Using raw query.")
            return {"status": "error", "hypothetical_document": query}  # Fallback

        return {
            "status": "success",
            "hypothetical_document": validated_output.hypothetical_document,
        }


class ChromaDBSearchTool(BaseTool):
    """v10.7: Searches the resume database using ChromaDB (Vector Search)."""

    tool_name = "search_resume_database"

    def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
        super().__init__(context, debug_mode)
        # v10.7: Use injected embedding function
        self.embedding_function = self.context.embedding_function
        self.collection_name = self.config.chromadb_config.default_collection_name
        self.chroma_client = self.context.chromadb_client

    @track_metrics("run_chroma_tool")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        query = tool_input.get("query", "")
        self.log_info(f"Searching ChromaDB (Vector) for: {query}")

        try:
            collection = self.chroma_client.get_collection(
                name=self.collection_name, embedding_function=self.embedding_function
            )

            results = await asyncio.to_thread(
                collection.query,
                query_texts=[query],
                n_results=5,
                where={"workflow_id": workflow_id},
            )

            search_results = []
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            for doc, meta in zip(documents, metadatas):
                experience_obj_str = meta.get("experience_object")
                if experience_obj_str:
                    search_results.append(json.loads(experience_obj_str))

            self.log_feedback(
                workflow_id, "chroma_search", "success", {"results_found": len(search_results)}
            )
            return {"search_results": search_results}

        except Exception as e:
            self.log_error(f"Failed to run ChromaDB search: {e}")
            return {"search_results": []}


class BM25SearchTool(BaseTool):
    """v10.7: Searches the resume using BM25 (Keyword Search)."""

    tool_name = "search_resume_bm25"

    def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
        super().__init__(context, debug_mode)
        if not BM25_AVAILABLE:
            self.log_error("BM25SearchTool disabled: 'rank_bm25' not installed.")

    @track_metrics("run_bm25_tool")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
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
                search_results = [
                    corpus_metadata[i] for i, score in indexed_scores[:5] if score > 0
                ]
                return search_results

            search_results = await asyncio.to_thread(do_bm25_search)

            self.log_feedback(
                workflow_id, "bm25_search", "success", {"results_found": len(search_results)}
            )
            return {"search_results": search_results}

        except Exception as e:
            self.log_error(f"Failed to run BM25 search: {e}")
            return {"search_results": []}


# ============================================================================
# ROW 7: QA STACK (ReAct Conductor with 11+ REAL Tools)
# ============================================================================


class QABaseValidatorTool(BaseTool):
    """Base class for the 10 T2 validator tools"""

    model_config_name = "qa_validator_model"  # Gemini 2.5 Flash
    output_model: Any = BaseToolOutput

    @track_metrics("tool_qa_validator")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        self.log_info(f"Tool: Running {self.tool_name} (v10.7)...")
        client = self.get_model_client(self.model_config_name)

        prompt_template = self.prompt_manager.get_template(self.tool_name)

        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template, tool_input, self.budget_manager, client.goal_state, client.top_failures
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_validator_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")

        return validated_output.model_dump()


class QAClaimValidatorTool(QABaseValidatorTool):
    """(NLI) Checks if claims in the draft are supported by the master resume."""

    tool_name = "validate_claims"
    output_model = QAClaimOutput


class QAToneValidatorTool(QABaseValidatorTool):
    """Checks if the draft's tone matches the strategy (e.g., 'leadership')."""

    tool_name = "validate_tone"
    output_model = QAToneOutput


class QAThematicAlignmentTool(QABaseValidatorTool):
    """Ensures all sections support the central strategy theme."""

    tool_name = "validate_thematic_alignment"
    output_model = QAThematicAlignmentOutput


class QASemanticEntailmentTool(QABaseValidatorTool):
    """Checks if bullets are semantically entailed by the job description."""

    tool_name = "validate_semantic_entailment"
    output_model = QASemanticEntailmentOutput


class QANarrativeThreadTool(QABaseValidatorTool):
    """Checks for a consistent career story/narrative."""

    tool_name = "validate_narrative_thread"
    output_model = QANarrativeThreadOutput


class QAJDSkillsValidatorTool(QABaseValidatorTool):
    """Ensures keywords/skills from the JD are present in the draft."""

    tool_name = "validate_jd_skills"
    output_model = QAJDSkillsOutput


class QASignalScoreValidatorTool(QABaseValidatorTool):
    """Rates the 'signal' (achievement) vs 'noise' (fluff) of each bullet."""

    tool_name = "validate_signal_score"
    output_model = QASignalScoreOutput


class QATenureValidatorTool(QABaseValidatorTool):
    """Checks for consistency in dates and tenure."""

    tool_name = "validate_tenure"
    output_model = QATenureOutput


class QAMissedOpportunityTool(QABaseValidatorTool):
    """Looks for experience in the master resume that was omitted but is relevant."""

    tool_name = "find_missed_opportunities"
    output_model = QAMissedOpportunitiesOutput


class QAAdversarialReviewerTool(BaseTool):
    """(Claude 4.1 Opus) Acts as a skeptical hiring manager to find flaws."""

    tool_name = "adversarial_review"
    output_model = QAAdversarialOutput

    @track_metrics("tool_qa_adversarial")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        self.log_info("Tool: Running Adversarial Review (v10.7)...")
        client = self.get_model_client("qa_adversarial_model")
        prompt_template = self.prompt_manager.get_template(self.tool_name)

        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template, tool_input, self.budget_manager, client.goal_state, client.top_failures
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_adversarial_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")

        return validated_output.model_dump()


class QABiasDetectorTool(BaseTool):
    """(Local) Runs the local bias detector tool on the final draft."""

    tool_name = "validate_bias"
    output_model = QABiasOutput

    @track_metrics("tool_qa_bias_detector")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        self.log_info("Tool: Running local bias detector (v10.7)...")
        draft_text = json.dumps(tool_input.get("draft_text", ""))

        # v10.7 (FIX): Call the sync function in a thread to avoid blocking
        result_dict = await asyncio.to_thread(detect_bias, self.context, draft_text, workflow_id)

        validated_output, error = self.validator.validate(result_dict, self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")

        return validated_output.model_dump()


class QAWordCountValidatorTool(BaseTool):
    """(Local) Runs deterministic word count check."""

    tool_name = "validate_word_count"

    class WordCountOutput(BaseToolOutput):
        validation_passed: bool
        message: str
        deterministic_count: int

    output_model = WordCountOutput

    @track_metrics("tool_qa_word_count")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        self.log_info("Tool: Running Word Count Validator (v10.7)...")

        text_to_check = tool_input.get("text_to_check", "")
        min_words = tool_input.get("min_words", 50)
        max_words = tool_input.get("max_words", 150)
        llm_reported_count = tool_input.get("llm_reported_count")

        validator = self.context.semantic_validator

        validation_passed, message = validator.check_word_count(
            text=text_to_check,
            min_words=min_words,
            max_words=max_words,
            llm_reported_count=llm_reported_count,
            workflow_id=workflow_id,
        )

        result_dict = {
            "status": "success",
            "validation_passed": validation_passed,
            "message": message,
            "deterministic_count": len(text_to_check.split()),
        }

        validated_output, error = self.validator.validate(result_dict, self.output_model)
        if error:
            raise PydanticSchemaError(
                f"Tool {self.tool_name} failed its own output validation: {error}"
            )

        return validated_output.model_dump()


# ============================================================================
# v10.7 (Fix #8): UI CONTROL TOOLS (STUBS)
# ============================================================================


class UIUpdateElementTool(BaseTool):
    """(Stub) Simulates updating a UI element."""

    tool_name = "ui_update_element"
    output_model = BaseToolOutput

    @track_metrics("tool_ui_update_element")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        element_id = tool_input.get("element_id", "unknown")
        content = tool_input.get("content", "")

        self.log_info(
            f"Tool: UI STUB >> Updating element '{element_id}' with content: '{content[:30]}...'"
        )

        # In a real system, this would dispatch an event.
        # For v10.7, we just log and return success.

        return {"status": "success"}


class UIFireEventTool(BaseTool):
    """(Stub) Simulates firing a UI event."""

    tool_name = "ui_fire_event"
    output_model = BaseToolOutput

    @track_metrics("tool_ui_fire_event")
    async def _run_async_internal(
        self, tool_input: dict[str, Any], workflow_id: str
    ) -> dict[str, Any]:
        event_name = tool_input.get("event_name", "unknown_event")
        payload = tool_input.get("payload", {})

        self.log_info(f"Tool: UI STUB >> Firing event '{event_name}' with payload: {payload}")

        return {"status": "success"}


# ============================================================================
# END OF agent_tools_v10_7.py
# ============================================================================
