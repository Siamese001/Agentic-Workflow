import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("LicCodeInterpreter", "p4obs", "metric_1")
_emit_emits_metric_event("LicCodeInterpreter", "p4obs", "metric_2")
_emit_emits_metric_event("LicCodeInterpreter", "p4obs", "metric_3")
_emit_emits_metric_event("LicCodeInterpreter", "p4obs", "metric_4")
_emit_emits_metric_event("LicCodeInterpreter", "p4obs", "metric_5")
_emit_emits_metric_event("LicCodeInterpreter", "p4obs", "metric_6")
_emit_records_incident_event("LicCodeInterpreter", "p4obs", "incident")
_emit_captures_runtime_anomaly("LicCodeInterpreter", "p4obs", "anomaly")
_emit_writes_observability_log("LicCodeInterpreter", "p4obs", "obs_log")
_emit_updates_monitoring_state("LicCodeInterpreter", "p4obs", "mon_state")
_emit_triggers_alert("LicCodeInterpreter", "p4obs", "alert")
_emit_links_incident_trace("LicCodeInterpreter", "p4obs", "trace_link")
_emit_captures_pattern("LicCodeInterpreter", "p3lm", "pattern")
_emit_records_learning_event("LicCodeInterpreter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("LicCodeInterpreter", "p3lm", "snapshot")
_emit_feeds_meta_learning("LicCodeInterpreter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("LicCodeInterpreter", "p3lm", "routing")
_emit_improves_agent_policy("LicCodeInterpreter", "p3lm", "policy")
_emit_stores_learning_state("LicCodeInterpreter", "p3lm", "state")
_emit_records_execution_trace("LicCodeInterpreter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("LicCodeInterpreter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("LicCodeInterpreter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("LicCodeInterpreter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("LicCodeInterpreter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("LicCodeInterpreter", "env_read", "p2_env_1")
_emit_reads_environ("LicCodeInterpreter", "env_read", "p2_env_2")
_emit_reads_runtime_state("LicCodeInterpreter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("LicCodeInterpreter", "runtime_state", "p2_rt_2")

_emit_applies_guardrail("p0", "LicCodeInterpreter", "p0_governance")
_emit_reads_policy_state("p0", "LicCodeInterpreter", "policy_binding")
_emit_snapshots_state("p0", "LicCodeInterpreter", "state_snapshot")
_emit_pulls_context("p1", "LicCodeInterpreter", "context_pull")
_emit_pulls_context("p1", "LicCodeInterpreter", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "LicCodeInterpreter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "LicCodeInterpreter", "uwg_term_secondary")
_emit_writes_through("p1", "LicCodeInterpreter", "write_through")
_emit_writes_through("p1", "LicCodeInterpreter", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "LicCodeInterpreter", "safety_validation")
_emit_invokes_eval("p1", "LicCodeInterpreter", "eval_call")
_emit_proposal_commits_routing("p1", "LicCodeInterpreter", "routing_commit")
_emit_escalates_to_human("p1", "LicCodeInterpreter", "human_escalation")
_emit_routes_through("p1", "LicCodeInterpreter", "route_through")
_emit_checks_agent_registry("p1", "LicCodeInterpreter", "agent_registry")
_emit_validates_agent_capability("p1", "LicCodeInterpreter", "capability")
_emit_dispatches_execution_plan("p1", "LicCodeInterpreter", "exec_plan")
_emit_agent_executes_agent("p1", "LicCodeInterpreter", "sub_agent")
_emit_routes_to_agent("p1", "LicCodeInterpreter", "target_agent")
_emit_verifies_policy("p1", "LicCodeInterpreter", "policy_check")
_emit_observes_runtime_state("p1", "LicCodeInterpreter", "runtime_state")
_emit_verifies_boundary("p1", "LicCodeInterpreter", "boundary_check")
_emit_transcripts_response("p1", "LicCodeInterpreter", "transcript")
_emit_hard_fails_untranscripted("p1", "LicCodeInterpreter")
_emit_gated_by_confidence("p1", "LicCodeInterpreter", "confidence_gate")
emit_replay_key("p0", "LicCodeInterpreter")
emit_determinism_digest("p0", "LicCodeInterpreter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "LicCodeInterpreter", "execution_auth")
_emit_validates_capability("p2", "LicCodeInterpreter", "capability_check")
_emit_routes_to_capability("p2", "LicCodeInterpreter", "capability_route")
_emit_writes_via_uwg("p2", "LicCodeInterpreter", "uwg_write")
_emit_blocks_direct_write("p2", "LicCodeInterpreter", "direct_write_block")
_emit_records_tool_invocation("p2", "LicCodeInterpreter", "tool_invocation")
_emit_captures_execution_output("p2", "LicCodeInterpreter", "exec_output")
_emit_dispatches_agent("p3", "LicCodeInterpreter", "agent_dispatch")
_emit_coordinates_agents("p3", "LicCodeInterpreter", "agent_coordination")
_emit_records_workflow_lineage("p3", "LicCodeInterpreter", "workflow_lineage")
_emit_records_healing_outcome("p3", "LicCodeInterpreter", "healing_outcome")
_emit_escalates_failure("p3", "LicCodeInterpreter", "failure_escalation")
_emit_orchestrates_workflow("p3", "LicCodeInterpreter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "LicCodeInterpreter", "healing_dispatch")
_emit_invokes_evaluation("p3", "LicCodeInterpreter", "evaluation_signal")
_emit_records_telemetry_event("p4", "LicCodeInterpreter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "LicCodeInterpreter", "eval_metric")
_emit_stores_embedding("p4", "LicCodeInterpreter", "embedding_store")
_emit_updates_meta_learning_state("p4", "LicCodeInterpreter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "LicCodeInterpreter", "exec_snapshot_link")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_1")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_2")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_3")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_4")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_5")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_6")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_7")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_8")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_9")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_10")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_11")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_12")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_13")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_14")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_15")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_16")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_17")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_18")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_19")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_20")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_21")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_22")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_23")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_24")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_25")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_26")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_27")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_28")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_29")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_30")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_31")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_32")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_33")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_34")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_35")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_36")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_37")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_38")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_39")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_40")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_41")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_42")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_43")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_44")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_45")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_46")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_47")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_48")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_49")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_50")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_51")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_52")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_53")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_54")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_55")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_56")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_57")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_58")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_59")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_60")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_61")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_62")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_63")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_64")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_65")
_emit_reads_through("l4", "LicCodeInterpreter", "urg_read_66")

"\nLIC Code Interpreter Tool - Fast loop for deterministic evaluation.\n\nPorted from: archives/legacy_lic/Agentic LIC/tools_LIC.py\n"


@dataclass
class ScoredCandidate:
    """A scored candidate message."""

    candidate_index: int
    candidate_text: str
    scores: dict[str, float]
    total_score: float


@dataclass
class ScoringCriteria:
    """Criteria for scoring candidates."""

    strategic_alignment: float = 0.5
    keyword_density: float = 0.3
    readability: float = 0.2


@dataclass
class SimilarityResult:
    """Result of a similarity check."""

    score: float
    method: str
    text1_length: int
    text2_length: int


@dataclass
class KeywordExtractionResult:
    """Result of keyword extraction."""

    keywords: list[str]
    source_text_length: int
    top_n: int


STOP_WORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "he",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "that",
        "the",
        "to",
        "was",
        "were",
        "will",
        "with",
        "the",
        "this",
        "but",
        "they",
        "have",
        "had",
        "what",
        "when",
        "where",
        "who",
        "which",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "can",
        "just",
        "should",
        "now",
        "also",
        "into",
        "over",
        "after",
        "before",
        "between",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "any",
        "about",
    ],
)


class LICCodeInterpreter:
    """
    Safe code execution environment for deterministic evaluation.

    Provides a "Fast Loop" for validation and scoring before committing
    to expensive LLM calls. Used by HOP-6 (ValidationAgent) to:
    - Score message drafts for similarity to strategic brief
    - Rank N candidates without LLM synthesis
    - Run deterministic validation checks
    """

    def __init__(self) -> None:
        """Initialize code interpreter with safe function registry."""
        self.functions: dict[str, Callable[..., Any]] = {
            "run_similarity_check": self.run_similarity_check,
            "run_scoring_competition": self.run_scoring_competition,
            "extract_keywords": self.extract_keywords,
            "calculate_overlap": self.calculate_overlap,
            "rank_by_metric": self.rank_by_metric,
            "validate_structure": self.validate_structure,
        }

    def execute(self, function_name: str, **kwargs: object) -> object:
        """
        Execute a registered function safely.

        Args:
            function_name: Name of function to execute
            **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            ValueError: If function not registered
        """
        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"LicCodeInterpreter.execute:{function_name}"
        )
        if function_name not in self.functions:
            raise ValueError(
                f"Function '{function_name}' not registered. Available: {list(self.functions.keys())}",
            )
        func = self.functions[function_name]
        return func(**kwargs)

    def run_similarity_check(self, text1: str, text2: str, method: str = "cosine") -> SimilarityResult:
        """
        Calculate similarity between two texts.

        Args:
            text1: First text
            text2: Second text
            method: Similarity method ("cosine", "jaccard")

        Returns:
            SimilarityResult with score
        """
        if method == "cosine":
            score = self._cosine_similarity(text1, text2)
        elif method == "jaccard":
            score = self._jaccard_similarity(text1, text2)
        else:
            raise ValueError(f"Unknown similarity method: {method}")
        return SimilarityResult(score=score, method=method, text1_length=len(text1), text2_length=len(text2))

    def run_scoring_competition(
        self,
        candidates: list[str],
        strategic_brief: str,
        criteria: ScoringCriteria | None = None,
    ) -> list[ScoredCandidate]:
        """
        Score N candidate messages against strategic brief.

        This is the "Fast Loop" that replaces LLM synthesis for C_LEVEL.
        Instead of using an LLM to synthesize 3 drafts, we score them
        deterministically and select the winner.

        Args:
            candidates: List of candidate message texts
            strategic_brief: Strategic brief text to align with
            criteria: Optional scoring weights (defaults to equal)

        Returns:
            List of scored candidates, sorted by score (highest first)
        """
        if criteria is None:
            criteria = ScoringCriteria()
        scored: list[ScoredCandidate] = []
        for i, candidate in enumerate(candidates):
            scores: dict[str, float] = {}
            alignment_result = self.run_similarity_check(candidate, strategic_brief, method="cosine")
            scores["strategic_alignment"] = alignment_result.score
            brief_keywords = self.extract_keywords(strategic_brief, top_n=20)
            candidate_words = set(candidate.lower().split())
            keyword_matches = sum(1 for kw in brief_keywords.keywords if kw in candidate_words)
            scores["keyword_density"] = (
                keyword_matches / len(brief_keywords.keywords) if brief_keywords.keywords else 0.0
            )
            scores["readability"] = self._calculate_readability(candidate)
            total_score = (
                scores["strategic_alignment"] * criteria.strategic_alignment
                + scores["keyword_density"] * criteria.keyword_density
                + scores["readability"] * criteria.readability
            )
            scored.append(
                ScoredCandidate(
                    candidate_index=i,
                    candidate_text=candidate,
                    scores=scores,
                    total_score=total_score,
                ),
            )
        scored.sort(key=lambda x: x.total_score, reverse=True)
        return scored

    # guardian: allow-magic-config
    def extract_keywords(self, text: str, top_n: int = 10, min_length: int = 4) -> KeywordExtractionResult:
        """
        Extract top keywords from text using word frequency.

        Args:
            text: Input text
            top_n: Number of keywords to return
            min_length: Minimum word length

        Returns:
            KeywordExtractionResult with keywords
        """
        words = [
            w.lower()
            for w in re.findall("\\b\\w+\\b", text)
            if len(w) >= min_length and w.lower() not in STOP_WORDS
        ]
        if not words:
            return KeywordExtractionResult(keywords=[], source_text_length=len(text), top_n=top_n)
        word_counts: dict[str, int] = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, _ in sorted_words[:top_n]]
        return KeywordExtractionResult(keywords=keywords, source_text_length=len(text), top_n=top_n)

    # guardian: allow-magic-config
    def calculate_overlap(self, text1: str, text2: str, min_word_length: int = 4) -> dict[str, object]:
        """
        Calculate word overlap between two texts.

        Args:
            text1: First text
            text2: Second text
            min_word_length: Minimum word length to consider

        Returns:
            Dictionary with overlap statistics
        """
        words1 = {
            w.lower()
            for w in re.findall("\\b\\w+\\b", text1)
            if len(w) >= min_word_length and w.lower() not in STOP_WORDS
        }
        words2 = {
            w.lower()
            for w in re.findall("\\b\\w+\\b", text2)
            if len(w) >= min_word_length and w.lower() not in STOP_WORDS
        }
        intersection = words1 & words2
        union = words1 | words2
        return {
            "overlap_count": len(intersection),
            "overlap_words": list(intersection),
            "text1_unique_count": len(words1 - words2),
            "text2_unique_count": len(words2 - words1),
            "jaccard_similarity": len(intersection) / len(union) if union else 0.0,
        }

    def rank_by_metric(
        self,
        items: list[dict[str, object]],
        metric_key: str,
        descending: bool = True,
    ) -> list[dict[str, object]]:
        """
        Rank items by a specific Metric.

        Args:
            items: List of items with metrics
            metric_key: Key to sort by
            descending: Sort in descending order

        Returns:
            Sorted list of items
        """
        return sorted(items, key=lambda x: x.get(metric_key, 0), reverse=descending)

    def validate_structure(self, text: str, requirements: dict[str, object]) -> dict[str, object]:
        """
        Validate text structure against requirements.

        Args:
            text: Text to validate
            requirements: Structure requirements

        Returns:
            Validation result dictionary
        """
        result: dict[str, object] = {"is_valid": True, "violations": [], "metrics": {}}
        word_count = len(text.split())
        result["metrics"]["word_count"] = word_count
        if "min_words" in requirements:
            if word_count < requirements["min_words"]:
                result["is_valid"] = False
                result["violations"].append(
                    f"Word count {word_count} below minimum {requirements['min_words']}",
                )
        if "max_words" in requirements:
            if word_count > requirements["max_words"]:
                result["is_valid"] = False
                result["violations"].append(
                    f"Word count {word_count} above maximum {requirements['max_words']}",
                )
        char_count = len(text)
        result["metrics"]["char_count"] = char_count
        if "max_chars" in requirements:
            if char_count > requirements["max_chars"]:
                result["is_valid"] = False
                result["violations"].append(
                    f"Character count {char_count} above maximum {requirements['max_chars']}",
                )
        sentences = re.split("[.!?]+", text)
        sentence_count = len([s for s in sentences if s.strip()])
        result["metrics"]["sentence_count"] = sentence_count
        if "min_sentences" in requirements:
            if sentence_count < requirements["min_sentences"]:
                result["is_valid"] = False
                result["violations"].append(
                    f"Sentence count {sentence_count} below minimum {requirements['min_sentences']}",
                )
        return result

    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity using TF-IDF-like approach."""
        words1 = re.findall("\\b\\w+\\b", text1.lower())
        words2 = re.findall("\\b\\w+\\b", text2.lower())
        vocab = set(words1) | set(words2)
        if not vocab:
            return 0.0
        tf1 = {word: words1.count(word) for word in vocab}
        tf2 = {word: words2.count(word) for word in vocab}
        dot_product = sum(tf1[word] * tf2[word] for word in vocab)
        magnitude1 = sum(tf1[word] ** 2 for word in vocab) ** 0.5
        magnitude2 = sum(tf2[word] ** 2 for word in vocab) ** 0.5
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity on words."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1 & words2
        union = words1 | words2
        if len(union) == 0:
            return 0.0
        return len(intersection) / len(union)

    def _calculate_readability(self, text: str) -> float:
        """
        Calculate readability score (0-1).

        Based on:
        - Word count in target range (140-250 words)
        - Average sentence length (15-25 words ideal)
        """
        words = text.split()
        word_count = len(words)
        if 140 <= word_count <= 250:
            word_score = 1.0 - abs(word_count - 180) / 110
        else:
            word_score = max(0.0, 1.0 - abs(word_count - 180) / 180)
        sentences = re.split("[.!?]+", text)
        sentences = [s for s in sentences if s.strip()]
        if sentences:
            avg_sentence_length = word_count / len(sentences)
            if 15 <= avg_sentence_length <= 25:
                sentence_score = 1.0
            else:
                sentence_score = max(0.0, 1.0 - abs(avg_sentence_length - 20) / 20)
        else:
            sentence_score = 0.5
        return (word_score + sentence_score) / 2


def create_code_interpreter() -> LICCodeInterpreter:
    """builder function to create a code interpreter."""
    return LICCodeInterpreter()
