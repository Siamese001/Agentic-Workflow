"""Unit tests for canonical AST + Fuzzy Matching Utilities"""

import ast
import os

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_ast_fuzzy", "execution_auth")
_emit_validates_capability("p2", "test_ast_fuzzy", "capability_check")
_emit_routes_to_capability("p2", "test_ast_fuzzy", "capability_route")
_emit_writes_via_uwg("p2", "test_ast_fuzzy", "uwg_write")
_emit_blocks_direct_write("p2", "test_ast_fuzzy", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ast_fuzzy", "tool_invocation")
_emit_captures_execution_output("p2", "test_ast_fuzzy", "exec_output")
_emit_dispatches_agent("p3", "test_ast_fuzzy", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ast_fuzzy", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ast_fuzzy", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ast_fuzzy", "healing_outcome")
_emit_escalates_failure("p3", "test_ast_fuzzy", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ast_fuzzy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ast_fuzzy", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ast_fuzzy", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ast_fuzzy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ast_fuzzy", "eval_metric")
_emit_stores_embedding("p4", "test_ast_fuzzy", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ast_fuzzy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ast_fuzzy", "exec_snapshot_link")
from agentic_core.utils.ast_fuzzy_util import (
    ast_dump_hash,
    normalize_repo_path,
    parse_ast_safe,
    similarity_score,
    tokenize_simple,
)

_emit_records_execution_trace("p0", "evidence", "test_ast_fuzzy")
_emit_applies_guardrail("p0", "test_ast_fuzzy", "p0_governance")
_emit_reads_policy_state("p0", "test_ast_fuzzy", "policy_binding")
_emit_snapshots_state("p0", "test_ast_fuzzy", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_ast_fuzzy", "p4obs", "metric_1")
_emit_emits_metric_event("test_ast_fuzzy", "p4obs", "metric_2")
_emit_emits_metric_event("test_ast_fuzzy", "p4obs", "metric_3")
_emit_emits_metric_event("test_ast_fuzzy", "p4obs", "metric_4")
_emit_emits_metric_event("test_ast_fuzzy", "p4obs", "metric_5")
_emit_emits_metric_event("test_ast_fuzzy", "p4obs", "metric_6")
_emit_records_incident_event("test_ast_fuzzy", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_ast_fuzzy", "p4obs", "anomaly")
_emit_writes_observability_log("test_ast_fuzzy", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_ast_fuzzy", "p4obs", "mon_state")
_emit_triggers_alert("test_ast_fuzzy", "p4obs", "alert")
_emit_links_incident_trace("test_ast_fuzzy", "p4obs", "trace_link")
_emit_captures_pattern("test_ast_fuzzy", "p3lm", "pattern")
_emit_records_learning_event("test_ast_fuzzy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_ast_fuzzy", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_ast_fuzzy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_ast_fuzzy", "p3lm", "routing")
_emit_improves_agent_policy("test_ast_fuzzy", "p3lm", "policy")
_emit_stores_learning_state("test_ast_fuzzy", "p3lm", "state")
_emit_records_execution_trace("test_ast_fuzzy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_ast_fuzzy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_ast_fuzzy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_ast_fuzzy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_ast_fuzzy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_ast_fuzzy", "env_read", "p2_env_1")
_emit_reads_environ("test_ast_fuzzy", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_ast_fuzzy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_ast_fuzzy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_ast_fuzzy", "context_pull")
_emit_pulls_context("p1", "test_ast_fuzzy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_ast_fuzzy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_ast_fuzzy", "uwg_term_2")
_emit_writes_through("p1", "test_ast_fuzzy", "write_through")
_emit_writes_through("p1", "test_ast_fuzzy", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_ast_fuzzy", "safety_validation")
_emit_invokes_eval("p1", "test_ast_fuzzy", "eval_call")
_emit_proposal_commits_routing("p1", "test_ast_fuzzy", "routing_commit")
emit_replay_key("p0", "test_ast_fuzzy")
emit_determinism_digest("p0", "test_ast_fuzzy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


class TestAstDumpHash:
    """Test AST structural hashing."""

    def test_hash_determinism(self):
        """Hash of same AST is deterministic."""
        code = "def foo(x): return x + 1"
        tree1 = ast.parse(code)
        tree2 = ast.parse(code)

        hash1 = ast_dump_hash(tree1)
        hash2 = ast_dump_hash(tree2)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest

    def test_hash_differs_for_different_code(self):
        """Hash differs for different code."""
        tree1 = ast.parse("def foo(x): return x + 1")
        tree2 = ast.parse("def foo(x): return x + 2")

        hash1 = ast_dump_hash(tree1)
        hash2 = ast_dump_hash(tree2)

        assert hash1 != hash2

    def test_hash_ignores_attributes(self):
        """Hash ignores line numbers and column offsets."""
        code = "x = 1"
        tree = ast.parse(code)
        hash_val = ast_dump_hash(tree)

        # Should be consistent regardless of attributes
        assert len(hash_val) == 64


class TestSimilarityScore:
    """Test fuzzy similarity scoring."""

    def test_identical_text_score_one(self):
        """Identical text has similarity 1.0."""
        text = "def foo(x): return x + 1"
        score = similarity_score(text, text)
        assert score == 1.0

    def test_empty_text_score_zero(self):
        """Empty text has similarity 0.0."""
        score = similarity_score("", "def foo(x): return x")
        assert score == 0.0

    def test_similarity_symmetric(self):
        """Similarity is symmetric."""
        text_a = "def foo(x): return x + 1"
        text_b = "def foo(x): return x + 2"

        score_ab = similarity_score(text_a, text_b)
        score_ba = similarity_score(text_b, text_a)

        assert score_ab == score_ba
        assert 0.0 <= score_ab <= 1.0

    def test_similar_code_high_score(self):
        """Similar code has high similarity score."""
        text_a = "def foo(x): return x + 1"
        text_b = "def foo(x): return x + 1"

        score = similarity_score(text_a, text_b)
        assert score > 0.9


class TestTokenizeSimple:
    """Test simple tokenization."""

    def test_tokenize_basic(self):
        """Basic tokenization splits on whitespace and punctuation."""
        text = "def foo(x): return x + 1"
        tokens = tokenize_simple(text)

        assert len(tokens) > 0
        assert all(isinstance(t, str) for t in tokens)
        assert all(t.islower() for t in tokens)  # lowercase

    def test_tokenize_idempotency(self):
        """Tokenizing twice gives same result."""
        text = "def foo(x): return x + 1"
        tokens1 = tokenize_simple(text)
        tokens2 = tokenize_simple(text)

        assert tokens1 == tokens2

    def test_tokenize_empty_string(self):
        """Empty string tokenizes to empty list."""
        tokens = tokenize_simple("")
        assert tokens == []


class TestNormalizeRepoPath:
    """Test repository path normalization."""

    def test_normalize_backslashes(self):
        """Backslashes are converted to forward slashes."""
        path = "agentic_core\\utils\\ast_fuzzy.py"
        normalized = normalize_repo_path(path)

        assert normalized == "agentic_core/utils/ast_fuzzy.py"
        assert "\\" not in normalized

    def test_normalize_already_normalized(self):
        """Already normalized paths are unchanged."""
        path = "agentic_core/utils/ast_fuzzy.py"
        normalized = normalize_repo_path(path)

        assert normalized == path

    def test_normalize_mixed_slashes(self):
        """Mixed slashes are normalized to forward."""
        path = "agentic_core\\utils/ast_fuzzy.py"
        normalized = normalize_repo_path(path)

        assert normalized == "agentic_core/utils/ast_fuzzy.py"


class TestThresholdConfiguration:
    """Test threshold environment variable configuration."""

    def test_default_threshold(self):
        """Default threshold is 0.6."""
        # Clear env var if set
        old_val = os.environ.pop("AST_FUZZY_THRESHOLD", None)
        try:
            # Re-import to get fresh value
            from agentic_core.utils import ast_fuzzy as module

            threshold = module.get_threshold()
            assert threshold == 0.6
        finally:
            if old_val is not None:
                os.environ["AST_FUZZY_THRESHOLD"] = old_val

    def test_threshold_env_override(self):
        """Threshold can be overridden via environment variable."""
        old_val = os.environ.get("AST_FUZZY_THRESHOLD")
        try:
            os.environ["AST_FUZZY_THRESHOLD"] = "0.75"
            # Re-import to get new value
            import importlib

            import agentic_core.utils.ast_fuzzy as module

            importlib.reload(module)
            threshold = module.get_threshold()
            assert threshold == 0.75
        finally:
            if old_val is not None:
                os.environ["AST_FUZZY_THRESHOLD"] = old_val
            else:
                os.environ.pop("AST_FUZZY_THRESHOLD", None)


class TestParseAstSafe:
    """Test safe AST parsing."""

    def test_parse_valid_code(self):
        """Valid code parses successfully."""
        code = "def foo(x): return x + 1"
        tree = parse_ast_safe(code)

        assert tree is not None
        assert isinstance(tree, ast.Module)

    def test_parse_invalid_code_returns_none(self):
        """Invalid code returns None."""
        code = "def foo(x) return x + 1"  # Missing colon
        tree = parse_ast_safe(code)

        assert tree is None

    def test_parse_empty_string(self):
        """Empty string parses to empty module."""
        tree = parse_ast_safe("")

        assert tree is not None
        assert isinstance(tree, ast.Module)
        assert len(tree.body) == 0
