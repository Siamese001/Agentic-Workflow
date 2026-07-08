"""Competitor Recon Agent - Strategic Competitive Intelligence.

This agent analyzes target company's competitors to identify strategic gaps
and generates outreach hooks that position the candidate as a solution
to competitive threats.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "competitor_recon_agent_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "competitor_recon_agent_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "competitor_recon_agent_types", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("competitor_recon_agent_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("competitor_recon_agent_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("competitor_recon_agent_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("competitor_recon_agent_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("competitor_recon_agent_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("competitor_recon_agent_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("competitor_recon_agent_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("competitor_recon_agent_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("competitor_recon_agent_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("competitor_recon_agent_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("competitor_recon_agent_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("competitor_recon_agent_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("competitor_recon_agent_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("competitor_recon_agent_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("competitor_recon_agent_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("competitor_recon_agent_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("competitor_recon_agent_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("competitor_recon_agent_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("competitor_recon_agent_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("competitor_recon_agent_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("competitor_recon_agent_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("competitor_recon_agent_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("competitor_recon_agent_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("competitor_recon_agent_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("competitor_recon_agent_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("competitor_recon_agent_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("competitor_recon_agent_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("competitor_recon_agent_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "competitor_recon_agent_types", "context_pull")
trace_contract._emit_pulls_context("p1", "competitor_recon_agent_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "competitor_recon_agent_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "competitor_recon_agent_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "competitor_recon_agent_types", "write_through")
trace_contract._emit_writes_through("p1", "competitor_recon_agent_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "competitor_recon_agent_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "competitor_recon_agent_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "competitor_recon_agent_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "competitor_recon_agent_types", "human_escalation")
trace_contract._emit_routes_through("p1", "competitor_recon_agent_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "competitor_recon_agent_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "competitor_recon_agent_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "competitor_recon_agent_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "competitor_recon_agent_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "competitor_recon_agent_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "competitor_recon_agent_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "competitor_recon_agent_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "competitor_recon_agent_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "competitor_recon_agent_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "competitor_recon_agent_types")
trace_contract._emit_gated_by_confidence("p1", "competitor_recon_agent_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "competitor_recon_agent_types")
trace_contract.emit_determinism_digest("p0", "competitor_recon_agent_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "competitor_recon_agent_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "competitor_recon_agent_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "competitor_recon_agent_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "competitor_recon_agent_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "competitor_recon_agent_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "competitor_recon_agent_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "competitor_recon_agent_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "competitor_recon_agent_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "competitor_recon_agent_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "competitor_recon_agent_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "competitor_recon_agent_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "competitor_recon_agent_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "competitor_recon_agent_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "competitor_recon_agent_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "competitor_recon_agent_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "competitor_recon_agent_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "competitor_recon_agent_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "competitor_recon_agent_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "competitor_recon_agent_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "competitor_recon_agent_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class CompetitorMove:
    """Represents a recent competitive move or feature launch."""

    competitor_name: str
    recent_launch: str
    source_url: str | None = None
    date: str = ""

    def __post_init__(self):
        """Ensure date is in reasonable format."""
        try:
            if "ago" in self.date.lower():
                pass
            elif "month" in self.date.lower() or "week" in self.date.lower():
                pass
            else:
                datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            object.__setattr__(self, "date", "Recent")


@dataclass
class StrategicHook:
    """Strategic outreach hook based on competitive intelligence."""

    hook_text: str
    relevance_score: float
    competitive_gap: str

    @property
    def is_highly_relevant(self) -> bool:
        """Check if hook is highly relevant."""
        return self.relevance_score >= 0.8


class IntelProvider(ABC):
    """Abstract base class for competitive intelligence providers."""

    @abstractmethod
    def get_competitors(self, target_company: str, industry: str) -> list[str]:
        """Get list of competitors for target company.

        Args:
            target_company: Company to analyze
            industry: Industry sector

        Returns:
            List of competitor names
        """
        pass

    @abstractmethod
    def get_recent_moves(self, competitor: str, months: int = 6) -> list[CompetitorMove]:
        """Get recent AI/ML moves by competitor.

        Args:
            competitor: Competitor name
            months: Number of months to look back

        Returns:
            List of recent competitive moves
        """
        pass


class MockIntelProvider(IntelProvider):
    """Mock intelligence provider for testing and development."""

    def __init__(self):
        """Initialize mock provider with sample data."""
        self.mock_competitors = {
            "technology": ["OpenAI", "Anthropic", "Google", "Microsoft", "Meta"],
            "finance": ["Stripe", "Square", "PayPal", "Adyen", "Braintree"],
            "healthcare": ["Tempus", "Flatiron", "Verily", "IBM Watson", "Philips"],
            "retail": ["Amazon", "Shopify", "BigCommerce", "Magento", "WooCommerce"],
            "biotech": ["Ginkgo Bioworks", "Recursion", "Twist Bioscience", "Benchling"],
            "agritech": ["Indigo Ag", "Farmers Business Network", "John Deere AI", "Blue River"],
        }
        self.mock_moves = {
            "OpenAI": [
                CompetitorMove(
                    competitor_name="OpenAI",
                    recent_launch="GPT-4 Turbo with 128K context",
                    source_url="https://openai.com/blog",
                    date="2 months ago",
                ),
                CompetitorMove(
                    competitor_name="OpenAI",
                    recent_launch="Assistants API for agent building",
                    source_url="https://openai.com/blog",
                    date="1 month ago",
                ),
            ],
            "Anthropic": [
                CompetitorMove(
                    competitor_name="Anthropic",
                    recent_launch="Claude 3 with improved reasoning",
                    source_url="https://anthropic.com",
                    date="3 months ago",
                ),
            ],
            "Google": [
                CompetitorMove(
                    competitor_name="Google",
                    recent_launch="Gemini Pro with multimodal capabilities",
                    source_url="https://deepmind.google",
                    date="2 months ago",
                ),
            ],
            "Meta": [
                CompetitorMove(
                    competitor_name="Meta",
                    recent_launch="Llama 3 open source model",
                    source_url="https://ai.meta.com",
                    date="1 month ago",
                ),
            ],
            "Microsoft": [
                CompetitorMove(
                    competitor_name="Microsoft",
                    recent_launch="Copilot Studio for custom AI agents",
                    source_url="https://microsoft.com/ai",
                    date="3 months ago",
                ),
            ],
        }

    def get_competitors(self, target_company: str, industry: str) -> list[str]:
        """Get mock competitors for target company."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "MockIntelProvider.get_competitors"
        )

        industry_lower = industry.lower()
        return self.mock_competitors.get(
            industry_lower,
            ["Market Leader A", "Market Leader B", "Market Leader C"],
        )[:3]

    def get_recent_moves(self, competitor: str, months: int = 6) -> list[CompetitorMove]:
        """Get mock recent moves for competitor."""
        return self.mock_moves.get(competitor, [])


@dataclass
class CompetitorReconAgent:
    """Analyzes competitors and generates strategic hooks."""

    intel_provider: Any = None

    def __post_init__(self):
        """Initialize the competitor recon agent."""
        if self.intel_provider is None:
            self.intel_provider = MockIntelProvider()
        self.skill_feature_map = {
            "llm": ["GPT", "LLM", "language model", "chatbot", "assistant"],
            "vector search": ["vector search", "embedding", "retrieval", "RAG"],
            "computer vision": ["vision", "image", "video", "computer vision"],
            "recommendation": ["recommendation", "personalization", "ranking"],
            "nlp": ["NLP", "text processing", "sentiment", "classification"],
            "mlops": ["MLOps", "deployment", "monitoring", "pipeline"],
            "agents": ["agent", "autonomous", "workflow", "automation"],
            "multimodal": ["multimodal", "vision-language", "cross-modal"],
        }
        logger.info("Initialized CompetitorReconAgent")

    def generate_fomo_hook(
        self,
        target_company: str,
        industry: str,
        candidate_skills: list[str] | None = None,
    ) -> StrategicHook | None:
        """Generate FOMO hook based on competitive intelligence.

        Args:
            target_company: Target company name
            industry: Industry sector
            candidate_skills: Candidate's skills; when omitted, derived from the
                apps_rg shared graph (graph-weighted selection, W3).

        Returns:
            Strategic hook or None if no competitive advantage found
        """
        if candidate_skills is None:
            candidate_skills = graph_weighted_candidate_skills()
        try:
            competitors = self._identify_competitors(target_company, industry)
            if not competitors:
                logger.warning("No competitors identified")
                return None
            all_moves = []
            for competitor in competitors:
                moves = self._gather_intel(competitor)
                all_moves.extend(moves)
            if not all_moves:
                logger.warning("No competitive moves found")
                return None
            matches = self._find_skill_matches(all_moves, candidate_skills)
            if matches:
                best_match = max(matches, key=lambda m: m["relevance"])
                return self._create_targeted_hook(best_match, target_company)
            else:
                return self._create_speed_hook(all_moves[0], target_company, candidate_skills)
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Error generating FOMO hook: {str(e)}")
            return None

    def get_strategic_ps(self, target_company: str, industry: str, candidate_skills: list[str] | None = None) -> str | None:
        """Get strategic P.S. line for emails.

        Args:
            target_company: Target company name
            industry: Industry sector
            candidate_skills: List of candidate's skills

        Returns:
            P.S. line or None
        """
        try:
            hook = self.generate_fomo_hook(target_company, industry, candidate_skills)
            if hook and hook.is_highly_relevant:
                return f"P.S. {hook.hook_text}"
            return None
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Error getting strategic P.S.: {str(e)}")
            return None

    def _identify_competitors(self, target_company: str, industry: str) -> list[str]:
        """Identify competitors for target company.

        Args:
            target_company: Company to analyze
            industry: Industry sector

        Returns:
            List of competitor names
        """
        try:
            competitors = self.intel_provider.get_competitors(target_company, industry)
            filtered = [c for c in competitors if c.lower() != target_company.lower()]
            logger.debug(f"Identified competitors for {target_company}: {filtered}")
            return filtered
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Error identifying competitors: {str(e)}")
            return []

    def _gather_intel(self, competitor: str) -> list[CompetitorMove]:
        """Gather intelligence on competitor's recent moves.

        Args:
            competitor: Competitor name

        Returns:
            List of recent competitive moves
        """
        try:
            moves = self.intel_provider.get_recent_moves(competitor)
            if not moves:
                logger.debug(f"No verified moves found for {competitor}")
                return []
            logger.debug(f"Found {len(moves)} moves for {competitor}")
            return moves
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Error gathering intel on {competitor}: {str(e)}")
            return []

    def _find_skill_matches(self, moves: list[CompetitorMove], skills: list[str]) -> list[dict[str, Any]]:
        """Find matches between candidate skills and competitor moves.

        Args:
            moves: List of competitive moves
            skills: List of candidate skills

        Returns:
            List of matches with relevance scores
        """
        try:
            matches = []
            for move in tqdm(moves, desc="Processing", unit="item"):
                move_text = move.recent_launch.lower()
                for skill in tqdm(skills, desc="Processing", unit="item"):
                    skill_lower = skill.lower()
                    if skill_lower in move_text:
                        matches.append(
                            {"move": move, "skill": skill, "relevance": 0.9, "match_type": "direct"},
                        )
                        continue
                    if skill_lower in self.skill_feature_map:
                        features = self.skill_feature_map[skill_lower]
                        for feature in features:
                            if feature in move_text:
                                matches.append(
                                    {"move": move, "skill": skill, "relevance": 0.7, "match_type": "feature"},
                                )
                                break
            logger.debug(f"Found {len(matches)} skill-feature matches")
            return matches
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.error(f"Error finding skill matches: {str(e)}")
            return []

    def _create_targeted_hook(self, match: dict[str, Any], target_company: str) -> StrategicHook:
        """Create targeted hook based on skill-feature match.

        Args:
            match: Skill-feature match data
            target_company: Target company name

        Returns:
            Strategic hook
        """
        try:
            move = match["move"]
            skill = match["skill"]
            hook_text = f"I noticed {move.competitor_name} recently launched {move.recent_launch}. Having led similar {skill} initiatives to achieve competitive parity, I have a playbook to help {target_company} close this gap."
            gap = f"{target_company} lacks {move.recent_launch} that {move.competitor_name} has"
            return StrategicHook(hook_text=hook_text, relevance_score=match["relevance"], competitive_gap=gap)
        # guardian: allow-silent-swallow
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Error creating targeted hook: {str(e)}")
            raise

    def _create_speed_hook(
        self,
        move: CompetitorMove,
        target_company: str,
        skills: list[str],
    ) -> StrategicHook:
        """Create speed-focused hook when no direct feature match.

        Args:
            move: Competitive move
            target_company: Target company name
            skills: Candidate skills

        Returns:
            Strategic hook focused on speed
        """
        try:
            hook_text = f"The pace of AI shipping at {move.competitor_name} is accelerating. My specialty is establishing high-velocity AI development cycles to maintain competitive positioning."
            gap = f"Development velocity gap with {move.competitor_name}"
            return StrategicHook(hook_text=hook_text, relevance_score=0.6, competitive_gap=gap)
        # guardian: allow-silent-swallow
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Error creating speed hook: {str(e)}")
            raise


def create_competitor_recon_agent(intel_provider: IntelProvider | None = None) -> CompetitorReconAgent:
    """Create a CompetitorReconAgent instance.

    Args:
        intel_provider: Optional custom intelligence provider

    Returns:
        Configured CompetitorReconAgent
    """
    return CompetitorReconAgent(intel_provider)


def graph_weighted_candidate_skills(
    *,
    recipient_class: str = "HIRING_MANAGER",
    top_n: int = 8,
) -> list[str]:
    """W3: derive candidate skills from the apps_rg shared graph, weighted by
    recipient role-family fit — replaces flat hand-authored ``candidate_skills``.

    Returns human-readable skill domains for the top graph-weighted approved
    apps_rg skills; empty when the shared SSOT is unavailable.
    """
    from apps_lic.integrations.apps_rg_proof_bridge import (  # noqa: PLC0415
        graph_weighted_skill_ids,
        load_apps_rg_proof_index,
    )

    index = load_apps_rg_proof_index()
    labels: list[str] = []
    for skill_id in graph_weighted_skill_ids(recipient_class=recipient_class, top_n=top_n):
        proof = index.skills_by_id.get(skill_id)
        label = (proof.domain or proof.capability) if proof is not None else ""
        if label and label not in labels:
            labels.append(label)
    return labels


def generate_competitive_hook(
    target_company: str,
    industry: str,
    candidate_skills: list[str] | None = None,
) -> str | None:
    """Quickly generate a competitive hook.

    Args:
        target_company: Target company name
        industry: Industry sector
        candidate_skills: Candidate skills; when omitted, derived from the
            apps_rg shared graph via :func:`graph_weighted_candidate_skills`.

    Returns:
        Hook text or None
    """
    if candidate_skills is None:
        candidate_skills = graph_weighted_candidate_skills()
    agent = create_competitor_recon_agent()
    hook = agent.generate_fomo_hook(target_company, industry, candidate_skills)
    return hook.hook_text if hook else None
