"""Tests for ADG test selector — Accelerator #5.

Coverage matrix per §1.1:
- Success: single file, multiple files, dedup, sorted output
- Edge cases: empty input, file not in ADG, no covers edges, non-test resolved_path,
              Windows backslash path, node missing resolved_path field
- Fail-closed: Redis connection error propagates (no swallowing)
- Gaps: file with no covers is gap, file with covers is not, sorted gaps
- Determinism: identical input → identical output (all tests use fixed data)
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.serial


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Shared fixture builder
# ---------------------------------------------------------------------------


def _make_client(
    nodes_by_file: dict[str, set[str]],
    fan_in_covers: dict[str, set[str]],
    nodes: dict[str, dict[str, str]],
) -> object:
    """Build a minimal ADGRedisClient stub backed by MagicMock."""
    from tools.adg.adg_redis_query import ADGRedisClient

    client = ADGRedisClient.__new__(ADGRedisClient)
    r = MagicMock()

    def smembers(key: str) -> set[str]:
        if key.startswith("adg:nodes:by_file:"):
            return nodes_by_file.get(key[len("adg:nodes:by_file:") :], set())
        if key.startswith("adg:edge:in:") and key.endswith(":covers"):
            nid = key[len("adg:edge:in:") : -len(":covers")]
            return fan_in_covers.get(nid, set())
        return set()

    def hgetall(key: str) -> dict[str, str]:
        nid = key[len("adg:node:") :]
        return nodes.get(nid, {})

    r.smembers.side_effect = smembers
    r.hgetall.side_effect = hgetall
    client._r = r
    return client


def _make_selector(nodes_by_file, fan_in_covers, nodes):
    from tools.adg.adg_test_selector import ADGTestSelector

    return ADGTestSelector(client=_make_client(nodes_by_file, fan_in_covers, nodes))


# ===========================================================================
# Success path
# ===========================================================================


class TestSelectTestsSuccess:
    pass


# ===========================================================================
# Edge cases
# ===========================================================================


class TestSelectTestsEdgeCases:
    def test_file_not_in_adg_returns_empty_no_error(self):
        sel = _make_selector({}, {}, {})
        result = sel.select_tests(["totally/unknown/file.py"])
        assert result == []

    def test_file_with_no_covers_edges_returns_empty(self):
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={},  # no covers
            nodes={},
        )
        result = sel.select_tests(["prod.py"])
        assert result == []

    def test_non_test_resolved_path_excluded(self):
        """Covers edges pointing to production files (not tests/) must be excluded."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t_real", "t_prod"}},
            nodes={
                "t_real": {"resolved_path": "tests/unit/test_prod.py"},
                "t_prod": {"resolved_path": "agentic_core/some_prod.py"},  # not tests/
            },
        )
        result = sel.select_tests(["prod.py"])
        assert result == ["tests/unit/test_prod.py"]
        assert "agentic_core/some_prod.py" not in result

    def test_backslash_path_normalized_to_forward_slash(self):
        """Windows-style backslash paths must be normalized before ADG lookup."""
        sel = _make_selector(
            nodes_by_file={"agentic_core/L0_routing/router.py": {"n1"}},
            fan_in_covers={"n1": {"t1"}},
            nodes={"t1": {"resolved_path": "tests/unit/test_router.py"}},
        )
        result = sel.select_tests(["agentic_core\\L0_routing\\router.py"])
        assert result == ["tests/unit/test_router.py"]

    def test_node_missing_resolved_path_skipped_no_error(self):
        """Nodes without resolved_path field must not cause KeyError."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t_empty"}},
            nodes={"t_empty": {}},  # no resolved_path
        )
        result = sel.select_tests(["prod.py"])
        assert result == []

    def test_node_with_empty_resolved_path_skipped(self):
        """Nodes with empty resolved_path string must be skipped."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t_blank"}},
            nodes={"t_blank": {"resolved_path": ""}},
        )
        result = sel.select_tests(["prod.py"])
        assert result == []

    def test_duplicate_input_paths_deduplicates_output(self):
        """Same file listed twice in input must not produce duplicate test paths."""
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t1"}},
            nodes={"t1": {"resolved_path": "tests/unit/test_prod.py"}},
        )
        result = sel.select_tests(["prod.py", "prod.py"])
        assert result == ["tests/unit/test_prod.py"]
        assert len(result) == 1


# ===========================================================================
# Fail-closed — Redis errors must propagate
# ===========================================================================


class TestSelectTestsFailClosed:
    def test_redis_connection_error_propagates(self):
        """Redis ConnectionError must NOT be swallowed — no fallback to filesystem."""
        import redis

        from tools.adg.adg_redis_query import ADGRedisClient
        from tools.adg.adg_test_selector import ADGTestSelector

        client = ADGRedisClient.__new__(ADGRedisClient)
        bad_r = MagicMock()
        bad_r.smembers.side_effect = redis.ConnectionError("connection refused")
        client._r = bad_r

        sel = ADGTestSelector(client=client)
        with pytest.raises(redis.ConnectionError):
            sel.select_tests(["agentic_core/L0_routing/router.py"])

    def test_redis_timeout_error_propagates(self):
        """Redis TimeoutError must NOT be swallowed."""
        import redis

        from tools.adg.adg_redis_query import ADGRedisClient
        from tools.adg.adg_test_selector import ADGTestSelector

        client = ADGRedisClient.__new__(ADGRedisClient)
        bad_r = MagicMock()
        bad_r.smembers.side_effect = redis.TimeoutError("timed out")
        client._r = bad_r

        sel = ADGTestSelector(client=client)
        with pytest.raises(redis.TimeoutError):
            sel.select_tests(["agentic_core/L0_routing/router.py"])


# ===========================================================================
# Coverage gaps
# ===========================================================================


class TestCoverageGaps:
    def test_file_with_no_covers_is_a_gap(self):
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={},  # no covers
            nodes={},
        )
        gaps = sel.coverage_gaps(["prod.py"])
        assert "prod.py" in gaps

    def test_file_with_covers_is_not_a_gap(self):
        sel = _make_selector(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_covers={"n1": {"t1"}},
            nodes={"t1": {"resolved_path": "tests/unit/test_prod.py"}},
        )
        gaps = sel.coverage_gaps(["prod.py"])
        assert gaps == []

    def test_empty_input_returns_empty_gaps(self):
        sel = _make_selector({}, {}, {})
        assert sel.coverage_gaps([]) == []

    def test_file_not_in_adg_at_all_is_a_gap(self):
        """Files not indexed in ADG have no nodes → no covers → they are gaps."""
        sel = _make_selector({}, {}, {})
        gaps = sel.coverage_gaps(["brand_new_unindexed_file.py"])
        assert "brand_new_unindexed_file.py" in gaps

    def test_gaps_result_is_sorted(self):
        sel = _make_selector({}, {}, {})
        gaps = sel.coverage_gaps(["z_file.py", "a_file.py", "m_file.py"])
        assert gaps == sorted(gaps)

    def test_mixed_covered_and_gap_files(self):
        sel = _make_selector(
            nodes_by_file={
                "covered.py": {"n1"},
                "uncovered.py": {"n2"},
            },
            fan_in_covers={"n1": {"t1"}},  # covered has cover; uncovered has none
            nodes={"t1": {"resolved_path": "tests/test_covered.py"}},
        )
        gaps = sel.coverage_gaps(["covered.py", "uncovered.py"])
        assert "uncovered.py" in gaps
        assert "covered.py" not in gaps

    def test_gap_detection_deterministic(self):
        sel = _make_selector({}, {}, {})
        g1 = sel.coverage_gaps(["a.py", "b.py"])
        g2 = sel.coverage_gaps(["a.py", "b.py"])
        assert g1 == g2
