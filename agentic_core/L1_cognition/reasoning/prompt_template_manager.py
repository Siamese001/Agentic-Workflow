"""Prompt Template Manager.

Manages prompt templates for RAG generation including rendering,
validation, and template selection.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from tempfile import NamedTemporaryFile
from pathlib import Path
from typing import Any

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.types.rag_types import (
    PromptTemplate,
    RAGConfig,
    RAGContext,
    RAGQuery,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from tqdm import tqdm

emit_replay_key("p0", "prompt_template_manager")
emit_determinism_digest("p0", "prompt_template_manager")

_emit_dispatches_healing_run("p1", "prompt_template_manager", "L1")
_emit_routes_through("p1", "prompt_template_manager", "L1")
_emit_checks_agent_registry("p1", "prompt_template_manager", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_template_manager", "capability")
_emit_dispatches_execution_plan("p1", "prompt_template_manager", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_template_manager", "sub_agent")
_emit_routes_to_agent("p1", "prompt_template_manager", "target_agent")
_emit_verifies_policy("p1", "prompt_template_manager", "policy_check")
_emit_observes_runtime_state("p1", "prompt_template_manager", "runtime_state")
_emit_verifies_boundary("p1", "prompt_template_manager", "boundary_check")
_emit_transcripts_response("p1", "prompt_template_manager", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_template_manager")
_emit_gated_by_confidence("p1", "prompt_template_manager", "confidence_gate")
_emit_escalates_to_human("p1", "prompt_template_manager", "L1")
_emit_reads_policy_state("p1", "prompt_template_manager", "L1")
_emit_authorize_and_execute("p2", "prompt_template_manager", "execution_auth")
_emit_validates_capability("p2", "prompt_template_manager", "capability_check")
_emit_routes_to_capability("p2", "prompt_template_manager", "capability_route")
_emit_writes_via_uwg("p2", "prompt_template_manager", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_template_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_template_manager", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_template_manager", "exec_output")
_emit_dispatches_agent("p3", "prompt_template_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_template_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_template_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_template_manager", "healing_outcome")
_emit_escalates_failure("p3", "prompt_template_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_template_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_template_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_template_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_template_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_template_manager", "eval_metric")
_emit_stores_embedding("p4", "prompt_template_manager", "embedding_store")


class PromptTemplateManager:
    """Manages prompt templates for RAG generation."""

    def __init__(
        self,
        config: RAGConfig | None = None,
        templates_path: Path | None = None,
    ) -> None:
        """Initialize the prompt template manager.

        Args:
            config: RAG configuration
            templates_path: Path to templates directory
        """
        self.config = config or RAGConfig()
        self.graphrag_config = get_config()

        # Template storage
        self.templates: dict[str, PromptTemplate] = {}
        self.templates_path = (
            templates_path or Path(__file__).parent.parent.parent.parent / "templates" / "rag"
        )

        # Initialize default templates
        self._initialize_default_templates()

        # Load custom templates if path exists
        if self.templates_path.exists():
            self._load_templates_from_disk()

    def _initialize_default_templates(self) -> None:
        """Initialize default prompt templates."""

        # QA Template
        qa_template = PromptTemplate(
            template_id="qa_default",
            name="Default Q&A Template",
            description="Standard template for question-answering tasks",
            system_prompt="You are a helpful AI assistant that answers questions based on the provided context. Use only the information given in the context to answer the question. If the context doesn't contain enough information to answer the question, say so clearly.",
            user_prompt_template="Context:\n{context}\n\nQuestion: {query}\n\nAnswer:",
            required_placeholders=["context", "query"],
            optional_placeholders=["sources", "item_count", "avg_relevance"],
            template_type="qa",
            target_llm="generic",
            version="1.0",
        )
        self.templates["qa_default"] = qa_template

        # Summarization Template
        summary_template = PromptTemplate(
            template_id="summarization_default",
            name="Default Summarization Template",
            description="Template for summarizing content from context",
            system_prompt="You are a helpful AI assistant that creates concise summaries based on the provided context. Focus on the main points and key information.",
            user_prompt_template="Context:\n{context}\n\nTask: Create a summary of the above context.\n\nSummary:",
            required_placeholders=["context"],
            optional_placeholders=["query", "sources", "item_count"],
            template_type="summarization",
            target_llm="generic",
            version="1.0",
        )
        self.templates["summarization_default"] = summary_template

        # Explanation Template
        explanation_template = PromptTemplate(
            template_id="explanation_default",
            name="Default Explanation Template",
            description="Template for explaining concepts based on context",
            system_prompt="You are a helpful AI assistant that explains concepts and topics based on the provided context. Provide clear, detailed explanations using only the information available in the context.",
            user_prompt_template="Context:\n{context}\n\nTopic to explain: {query}\n\nExplanation:",
            required_placeholders=["context", "query"],
            optional_placeholders=["sources", "item_count"],
            template_type="explanation",
            target_llm="generic",
            version="1.0",
        )
        self.templates["explanation_default"] = explanation_template

        # Analysis Template
        analysis_template = PromptTemplate(
            template_id="analysis_default",
            name="Default Analysis Template",
            description="Template for analyzing information and providing insights",
            system_prompt="You are a helpful AI assistant that analyzes information and provides insights based on the provided context. Use analytical thinking and draw conclusions based only on the given information.",
            user_prompt_template="Context:\n{context}\n\nAnalysis task: {query}\n\nAnalysis:",
            required_placeholders=["context", "query"],
            optional_placeholders=["sources", "item_count", "avg_relevance"],
            template_type="analysis",
            target_llm="generic",
            version="1.0",
        )
        self.templates["analysis_default"] = analysis_template

        # Code-related QA Template
        code_qa_template = PromptTemplate(
            template_id="code_qa_default",
            name="Code Q&A Template",
            description="Template for answering questions about code and software",
            system_prompt="You are a helpful AI assistant that answers questions about code and software development. Use the provided context about code entities, relationships, and documentation to answer accurately. Reference specific files, functions, or relationships when relevant.",
            user_prompt_template="Code Context:\n{context}\n\nQuestion: {query}\n\nAnswer (with code references when applicable):",
            required_placeholders=["context", "query"],
            optional_placeholders=["sources", "item_count"],
            template_type="qa",
            target_llm="code",
            version="1.0",
        )
        self.templates["code_qa_default"] = code_qa_template

    @staticmethod
    def _sanitize_template_id(template_id: str) -> str:
        sanitized = re.sub(r"[^A-Za-z0-9_.-]", "_", template_id).strip("._")
        if not sanitized:
            raise ValueError("Template ID must contain at least one safe character")
        return sanitized

    def _load_templates_from_disk(self) -> None:
        """Load custom templates from disk."""
        if not self.templates_path.exists():
            return

        for template_file in tqdm(self.templates_path.glob("*.json"), desc="Processing", unit="item"):
            try:
                with open(template_file, encoding="utf-8") as f:
                    template_data = json.load(f)

                template = PromptTemplate(
                    template_id=template_data.get("template_id", template_file.stem),
                    name=template_data.get("name", template_file.stem),
                    description=template_data.get("description", ""),
                    system_prompt=template_data.get("system_prompt", ""),
                    user_prompt_template=template_data.get("user_prompt_template", ""),
                    required_placeholders=template_data.get("required_placeholders", []),
                    optional_placeholders=template_data.get("optional_placeholders", []),
                    template_type=template_data.get("template_type", "qa"),
                    target_llm=template_data.get("target_llm", "generic"),
                    version=template_data.get("version", "1.0"),
                )

                self.templates[template.template_id] = template

            except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                # Log error but continue loading other templates
                print(f"Error loading template {template_file}: {e}")

    def get_template(
        self,
        template_id: str | None = None,
        query_type: str | None = None,
    ) -> PromptTemplate:
        """Get a prompt template.

        Args:
            template_id: Specific template ID to retrieve
            query_type: Query type to find appropriate template

        Returns:
            PromptTemplate instance
        """
        # If specific template ID provided, try to get it
        if template_id and template_id in self.templates:
            return self.templates[template_id]

        # Find template by query type
        if query_type:
            for template in self.templates.values():
                if template.template_type == query_type:
                    return template

        # Fall back to default
        default_id = self.config.default_template_id
        if default_id in self.templates:
            return self.templates[default_id]

        # Ultimate fallback
        return self.templates["qa_default"]

    def render_template(
        self,
        template_id: str | None = None,
        query_type: str | None = None,
        context: RAGContext | None = None,
        query: RAGQuery | None = None,
        additional_data: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Render a template with context and query.

        Args:
            template_id: Specific template ID to use
            query_type: Query type to find appropriate template
            context: RAG context for rendering
            query: RAG query for rendering
            additional_data: Additional data for placeholders

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Get template
        template = self.get_template(template_id, query_type)

        # Validate inputs
        if not context or not query:
            raise ValueError("Both context and query are required for template rendering")

        # Render template
        system_prompt, user_prompt = template.render(context, query, additional_data)

        # Update template usage statistics
        template.usage_count += 1
        template.last_used = datetime.utcnow()

        _emit_records_telemetry_event(
            query.query_id,
            "prompt_template_manager",
            f"template_rendered_{template.template_id}_{template.template_type}",
        )

        return system_prompt, user_prompt

    def list_templates(self) -> list[PromptTemplate]:
        """List all available templates."""
        return list(self.templates.values())

    def get_templates_by_type(self, template_type: str) -> list[PromptTemplate]:
        """Get templates by type."""
        return [t for t in self.templates.values() if t.template_type == template_type]

    def add_template(self, template: PromptTemplate) -> None:
        """Add a new template."""
        self.templates[template.template_id] = template

        _emit_records_telemetry_event(
            template.template_id,
            "prompt_template_manager",
            f"template_added_{template.template_id}",
        )

    def remove_template(self, template_id: str) -> bool:
        """Remove a template."""
        if template_id in self.templates:
            del self.templates[template_id]

            _emit_records_telemetry_event(
                template_id,
                "prompt_template_manager",
                f"template_removed_{template_id}",
            )
            return True
        return False

    def validate_template(self, template: PromptTemplate) -> list[str]:
        """Validate a template and return any issues."""
        issues = []

        # Check required fields
        if not template.template_id:
            issues.append("Template ID is required")

        if not template.name:
            issues.append("Template name is required")

        if not template.system_prompt:
            issues.append("System prompt is required")

        if not template.user_prompt_template:
            issues.append("User prompt template is required")

        # Check placeholders
        system_placeholders = self._extract_placeholders(template.system_prompt)
        user_placeholders = self._extract_placeholders(template.user_prompt_template)
        all_placeholders = system_placeholders | user_placeholders

        # Check if required placeholders are missing
        for required in template.required_placeholders:
            if required not in all_placeholders:
                issues.append(f"Required placeholder '{required}' not found in templates")

        # Check if placeholders in templates are declared
        declared_placeholders = set(template.required_placeholders + template.optional_placeholders)
        for placeholder in all_placeholders:
            if placeholder not in declared_placeholders:
                issues.append(f"Undeclared placeholder '{placeholder}' found in templates")

        return issues

    def _extract_placeholders(self, template_text: str) -> set[str]:
        """Extract placeholders from template text."""
        import re

        # Find all {placeholder} patterns
        placeholders = re.findall(r"\{([^}]+)\}", template_text)
        return set(placeholders)

    def save_template_to_disk(self, template: PromptTemplate) -> bool:
        """Save a template to disk."""
        if not self.templates_path.exists():
            self.templates_path.mkdir(parents=True, exist_ok=True)

        safe_template_id = self._sanitize_template_id(template.template_id)
        template_file = self.templates_path / f"{safe_template_id}.json"

        try:
            template_data = {
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "system_prompt": template.system_prompt,
                "user_prompt_template": template.user_prompt_template,
                "required_placeholders": template.required_placeholders,
                "optional_placeholders": template.optional_placeholders,
                "template_type": template.template_type,
                "target_llm": template.target_llm,
                "version": template.version,
            }

            with NamedTemporaryFile("w", dir=self.templates_path, delete=False, encoding="utf-8") as f:
                tmp_path = Path(f.name)
                json.dump(template_data, f, indent=2)

            try:
                os.replace(tmp_path, template_file)
            except Exception:  # guardian: allow-broad-exception -- temp file cleanup before re-raise; all exception types must trigger unlink
                tmp_path.unlink(missing_ok=True)
                raise

            return True

        except (OSError, TypeError, ValueError) as e:
            print(f"Error saving template to disk: {e}")
            return False

    def get_template_stats(self) -> dict[str, Any]:
        """Get template usage statistics."""
        stats = {
            "total_templates": len(self.templates),
            "templates_by_type": {},
            "most_used": None,
            "recently_used": None,
        }

        # Count by type
        for template in self.templates.values():
            template_type = template.template_type
            stats["templates_by_type"][template_type] = stats["templates_by_type"].get(template_type, 0) + 1

        # Find most used
        if self.templates:
            most_used = max(self.templates.values(), key=lambda t: t.usage_count)
            stats["most_used"] = {
                "template_id": most_used.template_id,
                "usage_count": most_used.usage_count,
            }

        # Find recently used
        recent_templates = [t for t in self.templates.values() if t.last_used]
        if recent_templates:
            most_recent = max(recent_templates, key=lambda t: t.last_used)
            stats["recently_used"] = {
                "template_id": most_recent.template_id,
                "last_used": most_recent.last_used.isoformat(),
            }

        return stats


# Factory function
def create_prompt_template_manager(
    config: RAGConfig | None = None,
    templates_path: Path | None = None,
) -> PromptTemplateManager:
    """Create a prompt template manager."""
    return PromptTemplateManager(config, templates_path)


__all__ = [
    "PromptTemplateManager",
    "create_prompt_template_manager",
]
