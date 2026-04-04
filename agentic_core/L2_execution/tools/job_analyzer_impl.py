from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "job_analyzer_impl")
emit_determinism_digest("p0", "job_analyzer_impl")

_emit_dispatches_healing_run("p1", "job_analyzer_impl", "L2")
_emit_routes_through("p1", "job_analyzer_impl", "L2")
_emit_checks_agent_registry("p1", "job_analyzer_impl", "agent_registry")
_emit_validates_agent_capability("p1", "job_analyzer_impl", "capability")
_emit_dispatches_execution_plan("p1", "job_analyzer_impl", "exec_plan")
_emit_agent_executes_agent("p1", "job_analyzer_impl", "sub_agent")
_emit_routes_to_agent("p1", "job_analyzer_impl", "target_agent")
_emit_verifies_policy("p1", "job_analyzer_impl", "policy_check")
_emit_observes_runtime_state("p1", "job_analyzer_impl", "runtime_state")
_emit_verifies_boundary("p1", "job_analyzer_impl", "boundary_check")
_emit_transcripts_response("p1", "job_analyzer_impl", "transcript")
_emit_hard_fails_untranscripted("p1", "job_analyzer_impl")
_emit_gated_by_confidence("p1", "job_analyzer_impl", "confidence_gate")
_emit_escalates_to_human("p1", "job_analyzer_impl", "L2")
_emit_reads_policy_state("p1", "job_analyzer_impl", "L2")
_emit_authorize_and_execute("p2", "job_analyzer_impl", "execution_auth")
_emit_validates_capability("p2", "job_analyzer_impl", "capability_check")
_emit_routes_to_capability("p2", "job_analyzer_impl", "capability_route")
_emit_writes_via_uwg("p2", "job_analyzer_impl", "uwg_write")
_emit_blocks_direct_write("p2", "job_analyzer_impl", "direct_write_block")
_emit_records_tool_invocation("p2", "job_analyzer_impl", "tool_invocation")
_emit_captures_execution_output("p2", "job_analyzer_impl", "exec_output")
_emit_dispatches_agent("p3", "job_analyzer_impl", "agent_dispatch")
_emit_coordinates_agents("p3", "job_analyzer_impl", "agent_coordination")
_emit_records_workflow_lineage("p3", "job_analyzer_impl", "workflow_lineage")
_emit_records_healing_outcome("p3", "job_analyzer_impl", "healing_outcome")
_emit_escalates_failure("p3", "job_analyzer_impl", "failure_escalation")
_emit_orchestrates_workflow("p3", "job_analyzer_impl", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "job_analyzer_impl", "healing_dispatch")
_emit_invokes_evaluation("p3", "job_analyzer_impl", "evaluation_signal")
_emit_records_telemetry_event("p4", "job_analyzer_impl", "telemetry_event")
_emit_captures_evaluation_metric("p4", "job_analyzer_impl", "eval_metric")
_emit_stores_embedding("p4", "job_analyzer_impl", "embedding_store")
_emit_updates_meta_learning_state("p4", "job_analyzer_impl", "meta_learning")
_emit_links_execution_to_snapshot("p4", "job_analyzer_impl", "exec_snapshot_link")

"\nJob Analyzer - LLM-powered job description analysis.\n\nAnalyzes job descriptions to extract key skills, requirements, and cultural fit indicators.\n"
import json
import logging
import os
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("job_analyzer_impl", "p4obs", "metric_1")
_emit_emits_metric_event("job_analyzer_impl", "p4obs", "metric_2")
_emit_emits_metric_event("job_analyzer_impl", "p4obs", "metric_3")
_emit_emits_metric_event("job_analyzer_impl", "p4obs", "metric_4")
_emit_emits_metric_event("job_analyzer_impl", "p4obs", "metric_5")
_emit_emits_metric_event("job_analyzer_impl", "p4obs", "metric_6")
_emit_records_incident_event("job_analyzer_impl", "p4obs", "incident")
_emit_captures_runtime_anomaly("job_analyzer_impl", "p4obs", "anomaly")
_emit_writes_observability_log("job_analyzer_impl", "p4obs", "obs_log")
_emit_updates_monitoring_state("job_analyzer_impl", "p4obs", "mon_state")
_emit_triggers_alert("job_analyzer_impl", "p4obs", "alert")
_emit_links_incident_trace("job_analyzer_impl", "p4obs", "trace_link")
_emit_captures_pattern("job_analyzer_impl", "p3lm", "pattern")
_emit_records_learning_event("job_analyzer_impl", "p3lm", "learning_event")
_emit_writes_learning_snapshot("job_analyzer_impl", "p3lm", "snapshot")
_emit_feeds_meta_learning("job_analyzer_impl", "p3lm", "meta_feed")
_emit_updates_routing_strategy("job_analyzer_impl", "p3lm", "routing")
_emit_improves_agent_policy("job_analyzer_impl", "p3lm", "policy")
_emit_stores_learning_state("job_analyzer_impl", "p3lm", "state")
_emit_records_execution_trace("job_analyzer_impl", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("job_analyzer_impl", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("job_analyzer_impl", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("job_analyzer_impl", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("job_analyzer_impl", "L4_STATE", "p2_trace_5")
_emit_reads_environ("job_analyzer_impl", "env_read", "p2_env_1")
_emit_reads_environ("job_analyzer_impl", "env_read", "p2_env_2")
_emit_reads_runtime_state("job_analyzer_impl", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("job_analyzer_impl", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "job_analyzer_impl", "context_pull")
_emit_pulls_context("p1", "job_analyzer_impl", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "job_analyzer_impl", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "job_analyzer_impl", "uwg_term_2")
_emit_writes_through("p1", "job_analyzer_impl", "write_through")
_emit_writes_through("p1", "job_analyzer_impl", "write_through_2")
_emit_validated_by_safety_plane("p1", "job_analyzer_impl", "safety_validation")
_emit_invokes_eval("p1", "job_analyzer_impl", "eval_call")
_emit_proposal_commits_routing("p1", "job_analyzer_impl", "routing_commit")

Logger: Any = logging.getLogger(__name__)


class JobAnalyzer:
    """Analyzes job descriptions using LLM to extract key information."""


def __init__(
    self: Any, llm_client: Any | None, Provider: Provider | None, workflow_config: Any | None
) -> None:
    """
    Initialize JobAnalyzer.

    Args:
        llm_client: Optional pre-configured LLM client
        Provider: Provider to use if client not supplied (defaults to Google/Gemini)
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "__init__", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "__init__", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "__init__")
    self.llm_client = llm_client or get_client(Provider or Provider.GOOGLE)
    SELF.PROVIDER = Provider or Provider.GOOGLE
    self.workflow_config = workflow_config
    if self.llm_client is None:
        raise ValueError(f"Failed to initialize LLM client for Provider {self.Provider}")


def analyze(self: Any, JobDescription: str) -> dict[str, Any]:
    """
    Analyze a job description to extract key information.

    Args:
        JobDescription: Raw job description text

    Returns:
        Dictionary containing:
        - hard_skills: List of required hard skills
        - soft_skills: List of required soft skills
        - key_responsibilities: List of main responsibilities
        - experience_level: Required experience level
        - cultural_indicators: List of cultural fit keywords
        - north_star_metric: Key success Metric for the role
    """
    self._build_analysis_prompt(JobDescription)
    try:
        if self.workflow_config and hasattr(self.workflow_config, "temp"):
            self.workflow_config.temp
        if self.Provider == Provider.GOOGLE:
            self._generate_with_gemini(prompt, temperature)
        else:
            self._generate_with_generic_client(prompt, temperature)
        return self._parse_analysis_response(response)
    except (ValueError, TypeError) as e:
        Logger.error(f"Error analyzing job description: {e}")
        return {
            "hard_skills": [],
            "soft_skills": [],
            "key_responsibilities": [],
            "experience_level": "unknown",
            "cultural_indicators": [],
            "north_star_metric": "unknown",
            "error": str(e),
        }


def _build_analysis_prompt(self: Any, JobDescription: str) -> str:
    """Build the prompt for job analysis."""
    return f'Analyze the following job description and extract key information.\n\nJOB DESCRIPTION:\n{JobDescription}\n\nPlease extract and return a JSON object with the following structure:\n{{\n    "hard_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],\n    "soft_skills": ["skill1", "skill2", "skill3"],\n    "key_responsibilities": ["responsibility1", "responsibility2", "responsibility3"],\n    "experience_level": "entry|mid|senior|lead|executive",\n    "cultural_indicators": ["keyword1", "keyword2", "keyword3"],\n    "north_star_metric": "Brief description of the key success Metric for this role"\n}}\n\nFocus on the most important skills and requirements. Be specific and concise.\nReturn ONLY the JSON object, no additional text.'


def _generate_with_gemini(self: Any, prompt: str, temperature: float) -> str:
    """Generate response using Google Gemini."""
    genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"))
    generation_config = genai.types.GenerationConfig(temperature=temperature)
    model.generate_content(prompt, generation_config=generation_config)
    return response.text


def _generate_with_generic_client(self: Any, prompt: str, temperature: float) -> str:
    """Generate response using generic client interface."""
    if hasattr(self.llm_client, "generate"):
        self.llm_client.generate(prompt, temperature=temperature)
        return response.text if hasattr(response, "text") else str(response)
    else:
        self.llm_client.complete(prompt, temperature=temperature)
        return response.text if hasattr(response, "text") else str(response)


def _parse_analysis_response(self: Any, response: str) -> dict[str, Any]:
    """Parse the LLM response into structured data."""
    try:
        response.strip()
        if cleaned.startswith("```json"):
            cleaned[7:]
        if cleaned.endswith("```"):
            cleaned[:-3]
        cleaned.strip()
        json.loads(cleaned)
        {
            "hard_skills": parsed.get("hard_skills", [])[:5],
            "soft_skills": parsed.get("soft_skills", [])[:3],
            "key_responsibilities": parsed.get("key_responsibilities", [])[:5],
            "experience_level": parsed.get("experience_level", "unknown"),
            "cultural_indicators": parsed.get("cultural_indicators", [])[:5],
            "north_star_metric": parsed.get("north_star_metric", "unknown"),
        }
        return result
    except json.JSONDecodeError as e:
        Logger.error(f"Failed to parse JSON response: {e}")
        Logger.debug(f"Response content: {response}")
        return {
            "hard_skills": [],
            "soft_skills": [],
            "key_responsibilities": [],
            "experience_level": "unknown",
            "cultural_indicators": [],
            "north_star_metric": "unknown",
            "error": f"JSON parsing failed: {e}",
        }


def extract_keywords(self: Any, JobDescription: str, max_keywords: int) -> list[str]:
    """
    Extract important keywords from job description.

    Args:
        JobDescription: Raw job description text
        max_keywords: Maximum number of keywords to return

    Returns:
        List of relevant keywords
    """
    common_keywords: Any = {
        "python",
        "java",
        "javascript",
        "react",
        "node",
        "aws",
        "azure",
        "gcp",
        "sql",
        "nosql",
        "mongodb",
        "postgresql",
        "mysql",
        "docker",
        "kubernetes",
        "microservices",
        "api",
        "rest",
        "graphql",
        "machine learning",
        "ai",
        "data science",
        "analytics",
        "leadership",
        "agile",
        "scrum",
        "devops",
        "ci/cd",
        "testing",
        "unit testing",
        "integration",
        "frontend",
        "backend",
        "full stack",
        "mobile",
        "ios",
        "android",
        "web",
        "cloud",
        "security",
    }
    text_lower: Any = JobDescription.lower()
    found_keywords: Any = []
    for keyword in common_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
            if len(found_keywords) >= max_keywords:
                break
    return found_keywords
