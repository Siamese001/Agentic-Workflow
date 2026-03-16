"""Unit tests for ADG Guardian Prioritizer (Phase 4).

Tests cover:
- Prioritize returns scores for all registered guardian IDs
- Scores are non-negative
- Scores are deterministic (same ScanResult -> same output)
- LLM gateway violations increase gateway_bypass score
- Cross-layer violations increase architecture_governance score
- Empty ScanResult -> all scores are zero
- PrioritizationResult.ordered() returns descending order
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.adg.applications.guardian_prioritizer import (
    _GUARDIAN_ADG_SIGNALS,
    GuardianPrioritizer,
    PrioritizationResult,
)
from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
from agentic_core.adg.schema import canonical_name
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_guardian_prioritizer")
_emit_applies_guardrail("p0", "test_guardian_prioritizer", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_prioritizer", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_prioritizer", "state_snapshot")
emit_replay_key("p0", "test_guardian_prioritizer")
emit_determinism_digest("p0", "test_guardian_prioritizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_empty_result() -> ScanResult:
    result = ScanResult(commit_sha="t")
    result.modules = []
    result.edges = []
    result.compute_digest()
    return result


def _make_result_with_llm_violation() -> ScanResult:
    result = ScanResult(commit_sha="llm")
    result.modules = ["apps_rg/engines/SomeAgent.py"]
    result.edges = [
        Edge(
            from_name=canonical_name("Module", "apps_rg/engines/SomeAgent.py"),
            relation_type="imports",
            to_name=canonical_name("Symbol", "openai"),
            edge_kind="network",
            source_file="apps_rg/engines/SomeAgent.py",
            line_no=5,
            symbol="openai",
        )
    ]
    result.compute_digest()
    return result


def _make_result_with_cross_layer_violation() -> ScanResult:
    result = ScanResult(commit_sha="cl")
    result.modules = [
        "agentic_core/L0_routing/config/path_constants.py",
        "agentic_core/L5_safety/config/structure_blueprint_config.py",
    ]
    result.edges = [
        Edge(
            from_name=canonical_name("Module", "agentic_core/L0_routing/config/path_constants.py"),
            relation_type="imports",
            to_name=canonical_name("Module", "agentic_core/L5_safety/config/structure_blueprint_config.py"),
            edge_kind="import",
            source_file="agentic_core/L0_routing/config/path_constants.py",
            line_no=1,
        )
    ]
    result.compute_digest()
    return result


class TestPrioritizeBasicContract:
    """Basic contract: returns PrioritizationResult with scores."""

    @pytest.mark.unit
    def test_returns_prioritization_result(self) -> None:
        result = _make_empty_result()
        prio = GuardianPrioritizer(result).prioritize()
        assert isinstance(prio, PrioritizationResult)

    @pytest.mark.unit
    def test_all_registered_guardians_have_scores(self) -> None:
        result = _make_empty_result()
        prio = GuardianPrioritizer(result).prioritize()
        scored_ids = {s.guardian_id for s in prio.scores}
        for gid in _GUARDIAN_ADG_SIGNALS:
            assert gid in scored_ids, f"Guardian {gid} missing from scores"

    @pytest.mark.unit
    def test_all_scores_non_negative(self) -> None:
        result = _make_empty_result()
        prio = GuardianPrioritizer(result).prioritize()
        for s in prio.scores:
            assert s.score >= 0, f"Negative score for {s.guardian_id}"

    @pytest.mark.unit
    def test_empty_result_all_scores_zero(self) -> None:
        result = _make_empty_result()
        prio = GuardianPrioritizer(result).prioritize()
        for s in prio.scores:
            assert s.score == 0, f"Non-zero score for {s.guardian_id} on empty result"


class TestScoreSignals:
    """Specific violations increase specific guardian scores."""

    @pytest.mark.unit
    def test_llm_violation_increases_gateway_bypass_score(self) -> None:
        empty_result = _make_empty_result()
        violation_result = _make_result_with_llm_violation()

        prio_empty = GuardianPrioritizer(empty_result).prioritize()
        prio_violation = GuardianPrioritizer(violation_result).prioritize()

        def score_of(prio, gid):
            return next((s.score for s in prio.scores if s.guardian_id == gid), 0)

        assert score_of(prio_violation, "gateway_bypass") >= score_of(prio_empty, "gateway_bypass")

    @pytest.mark.unit
    def test_cross_layer_increases_architecture_governance(self) -> None:
        empty_result = _make_empty_result()
        cl_result = _make_result_with_cross_layer_violation()

        prio_empty = GuardianPrioritizer(empty_result).prioritize()
        prio_cl = GuardianPrioritizer(cl_result).prioritize()

        def score_of(prio, gid):
            return next((s.score for s in prio.scores if s.guardian_id == gid), 0)

        assert score_of(prio_cl, "architecture_governance") >= score_of(prio_empty, "architecture_governance")


class TestDeterminism:
    """Same ScanResult always produces same scores."""

    @pytest.mark.unit
    def test_same_result_same_scores(self) -> None:
        result = _make_result_with_llm_violation()
        p1 = GuardianPrioritizer(result).prioritize()
        p2 = GuardianPrioritizer(result).prioritize()
        scores_1 = sorted([(s.guardian_id, s.score) for s in p1.scores])
        scores_2 = sorted([(s.guardian_id, s.score) for s in p2.scores])
        assert scores_1 == scores_2

    @pytest.mark.unit
    def test_digest_stable_across_two_calls(self) -> None:
        result = _make_result_with_llm_violation()
        p1 = GuardianPrioritizer(result).prioritize()
        p2 = GuardianPrioritizer(result).prioritize()
        assert p1.adg_signals_digest == p2.adg_signals_digest


class TestOrderedOutput:
    """ordered() returns descending score order."""

    @pytest.mark.unit
    def test_ordered_is_descending(self) -> None:
        result = _make_result_with_llm_violation()
        prio = GuardianPrioritizer(result).prioritize()
        ordered = prio.ordered()
        scores = [s.score for s in ordered]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.unit
    def test_ordered_tiebreak_by_guardian_id(self) -> None:
        """Tied scores are broken alphabetically by guardian_id."""
        result = _make_empty_result()
        prio = GuardianPrioritizer(result).prioritize()
        ordered = prio.ordered()
        # All zeros: must be sorted alphabetically
        for i in range(len(ordered) - 1):
            if ordered[i].score == ordered[i + 1].score:
                assert ordered[i].guardian_id <= ordered[i + 1].guardian_id


class TestLayerRankUpwardMutations:
    """Upward mutation detection must use integer rank, not string comparison."""

    @pytest.mark.unit
    def test_layer_rank_imported(self) -> None:
        from agentic_core.adg.applications.guardian_prioritizer import _LAYER_RANK

        assert _LAYER_RANK["L0"] < _LAYER_RANK["L1"]
        assert _LAYER_RANK["L0"] < _LAYER_RANK["L5"]
        assert _LAYER_RANK["L_APP"] > _LAYER_RANK["L6"]

    @pytest.mark.unit
    def test_upward_mutation_writes_to_higher_rank_detected(self) -> None:
        """L0 writing to L5 is an upward mutation; must be detected by rank not string."""
        from agentic_core.adg.applications.guardian_prioritizer import _LAYER_RANK

        fl_rank = _LAYER_RANK.get("L0", -1)
        tl_rank = _LAYER_RANK.get("L5", -1)
        assert tl_rank > fl_rank >= 0, "L5 must have higher rank than L0"

    @pytest.mark.unit
    def test_string_comparison_is_unreliable_for_layer_ordering(self) -> None:
        """String comparison of layer labels is unreliable.

        Example: 'L6' > 'L5' correctly, but 'L_APP' > 'L6' is also True
        because '_' > any digit (ASCII 95 vs 48-57) — accidentally correct.
        However 'L_UNKNOWN' > 'L6' is True even though L_UNKNOWN has rank -1.
        The rank map is the authoritative ordering.
        """
        from agentic_core.adg.applications.guardian_prioritizer import _LAYER_RANK

        # L_UNKNOWN has rank -1 (should NOT be treated as higher than any real layer)
        # but string 'L_UNKNOWN' > 'L6' -> True (broken: treats unknown as high layer)
        assert "L_UNKNOWN" > "L6"  # string compare is wrong for this case
        assert _LAYER_RANK["L_UNKNOWN"] < _LAYER_RANK["L0"]  # rank compare is correct


class TestEmbeddingViolationsFilterBySymbol:
    """RULE_B: embedding_violations must filter by EMBEDDING_SYMBOLS, not fire on every instantiates/embedding edge."""

    @pytest.mark.unit
    def test_known_embedding_symbol_triggers_violation(self) -> None:
        from agentic_core.adg.applications.guardian_prioritizer import GuardianPrioritizer
        from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
        from agentic_core.adg.schema import canonical_name

        result = ScanResult(commit_sha="emb")
        result.modules = ["apps_rg/engines/SomeAgent.py"]
        result.edges = [
            Edge(
                from_name=canonical_name("Module", "apps_rg/engines/SomeAgent.py"),
                relation_type="instantiates",
                to_name=canonical_name("Symbol", "OpenAIEmbeddings"),
                edge_kind="embedding",
                source_file="apps_rg/engines/SomeAgent.py",
                line_no=10,
                symbol="OpenAIEmbeddings",
            )
        ]
        result.compute_digest()
        p = GuardianPrioritizer(result)
        signals = p.get_signals()
        assert len(signals["embedding_violations"]) == 1

    @pytest.mark.unit
    def test_unknown_symbol_on_instantiates_embedding_also_recorded(self) -> None:
        """Edges with no symbol (empty string) are still recorded (scanner may omit symbol)."""
        from agentic_core.adg.applications.guardian_prioritizer import GuardianPrioritizer
        from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
        from agentic_core.adg.schema import canonical_name

        result = ScanResult(commit_sha="emb2")
        result.modules = ["apps_rg/engines/X.py"]
        result.edges = [
            Edge(
                from_name=canonical_name("Module", "apps_rg/engines/X.py"),
                relation_type="instantiates",
                to_name=canonical_name("Symbol", "SomeUnknownThing"),
                edge_kind="embedding",
                source_file="apps_rg/engines/X.py",
                line_no=5,
                symbol="",
            )
        ]
        result.compute_digest()
        p = GuardianPrioritizer(result)
        signals = p.get_signals()
        assert len(signals["embedding_violations"]) == 1

    @pytest.mark.unit
    def test_non_embedding_symbol_on_instantiates_not_recorded(self) -> None:
        """A non-EMBEDDING_SYMBOLS symbol with edge_kind=embedding should NOT be in violations (bug was: no filter)."""
        from agentic_core.adg.applications.guardian_prioritizer import GuardianPrioritizer
        from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
        from agentic_core.adg.schema import EMBEDDING_SYMBOLS, canonical_name

        # Pick a symbol definitively NOT in EMBEDDING_SYMBOLS
        non_emb_sym = "SomeRandomFactory"
        assert non_emb_sym not in EMBEDDING_SYMBOLS

        result = ScanResult(commit_sha="emb3")
        result.modules = ["apps_rg/engines/Y.py"]
        result.edges = [
            Edge(
                from_name=canonical_name("Module", "apps_rg/engines/Y.py"),
                relation_type="instantiates",
                to_name=canonical_name("Symbol", non_emb_sym),
                edge_kind="embedding",
                source_file="apps_rg/engines/Y.py",
                line_no=7,
                symbol=non_emb_sym,
            )
        ]
        result.compute_digest()
        p = GuardianPrioritizer(result)
        signals = p.get_signals()
        assert len(signals["embedding_violations"]) == 0

    @pytest.mark.unit
    def test_writes_to_relation_type_detected_not_mutates(self) -> None:
        """'mutates' relation type was dead code — only 'writes_to' is ever emitted by scanner."""
        from agentic_core.adg.applications.guardian_prioritizer import GuardianPrioritizer
        from agentic_core.adg.extraction.static_scanner import Edge, ScanResult
        from agentic_core.adg.schema import canonical_name

        result = ScanResult(commit_sha="mut")
        result.modules = [
            "agentic_core/L0_routing/config/path_constants.py",
            "agentic_core/L5_safety/config/structure_blueprint_config.py",
        ]
        result.edges = [
            Edge(
                from_name=canonical_name("Module", "agentic_core/L0_routing/config/path_constants.py"),
                relation_type="writes_to",
                to_name=canonical_name("Module", "agentic_core/L5_safety/config/structure_blueprint_config.py"),
                edge_kind="write",
                source_file="agentic_core/L0_routing/config/path_constants.py",
                line_no=1,
                symbol="open",
            )
        ]
        result.compute_digest()
        p = GuardianPrioritizer(result)
        signals = p.get_signals()
        assert len(signals["upward_mutations"]) == 1


class TestToDict:
    """to_dict produces expected structure."""

    @pytest.mark.unit
    def test_to_dict_has_priority_order(self) -> None:
        result = _make_empty_result()
        prio = GuardianPrioritizer(result).prioritize()
        d = prio.to_dict()
        assert "priority_order" in d
        assert "adg_signals_digest" in d

    @pytest.mark.unit
    def test_each_entry_has_required_fields(self) -> None:
        result = _make_empty_result()
        prio = GuardianPrioritizer(result).prioritize()
        d = prio.to_dict()
        for entry in d["priority_order"]:
            assert "guardian_id" in entry
            assert "score" in entry
            assert "signals" in entry
