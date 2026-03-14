"""
Regression tests for tools/adg/drift_score.py

All tests use synthetic stubs — no live Redis or ADG files required.
Mock ADGRedisClient and Redis via unittest.mock.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from tools.adg.drift_score import (
    WEIGHTS,
    _is_stub_only,
    _load_layer_nodes,
    composite_score,
    compute_blast_mismatch,
    compute_coverage_gap,
    compute_orphan_phantom,
    compute_violation_gap,
    write_to_redis,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_redis(smembers_map: dict = None, scard_map: dict = None, scan_results: list = None):
    """Return a mock Redis client with pre-configured responses."""
    r = MagicMock()

    smembers_map = smembers_map or {}
    scard_map = scard_map or {}

    def smembers(key):
        return smembers_map.get(key, set())

    def scard(key):
        return scard_map.get(key, 0)

    r.smembers.side_effect = smembers
    r.scard.side_effect = scard

    # scan yields (cursor=0, keys) on first call
    if scan_results is not None:
        r.scan.return_value = (0, scan_results)
    else:
        r.scan.return_value = (0, [])

    return r


# ---------------------------------------------------------------------------
# _is_stub_only
# ---------------------------------------------------------------------------


class TestIsStubOnly:
    def test_init_is_stub(self):
        assert _is_stub_only("agentic_core/L0_routing/__init__.py") is True

    def test_shim_is_stub(self):
        assert _is_stub_only("agentic_core/cache/graph_aware_cache_shim.py") is True

    def test_compat_is_stub(self):
        assert _is_stub_only("agentic_core/foo_compat.py") is True

    def test_normal_module_not_stub(self):
        assert _is_stub_only("agentic_core/L0_routing/config/path_constants.py") is False

    def test_apps_module_not_stub(self):
        assert _is_stub_only("apps_rg/engines/resume_orchestrator_engine.py") is False


# ---------------------------------------------------------------------------
# _load_layer_nodes
# ---------------------------------------------------------------------------


class TestLoadLayerNodes:
    def test_returns_module_nodes_for_layer(self):
        r = MagicMock()
        r.smembers.return_value = {"10", "11"}
        r.hgetall.side_effect = lambda key: {
            "adg:node:10": {
                "entity_type": "module",
                "resolved_path": "agentic_core/L0_routing/config/path_constants.py",
                "id": "10",
            },
            "adg:node:11": {
                "entity_type": "symbol",
                "resolved_path": "agentic_core/L0_routing/config/path_constants.py::MyClass",
                "id": "11",
            },
        }.get(key, {})

        result = _load_layer_nodes(r, {"L0"})
        assert "10" in result
        assert "11" not in result  # symbol excluded

    def test_excludes_pycache(self):
        r = MagicMock()
        r.smembers.return_value = {"20"}
        r.hgetall.return_value = {
            "entity_type": "module",
            "resolved_path": "agentic_core/__pycache__/foo.cpython-311.pyc",
            "id": "20",
        }
        result = _load_layer_nodes(r, {"L0"})
        assert result == {}

    def test_excludes_symbol_suffix(self):
        r = MagicMock()
        r.smembers.return_value = {"30"}
        r.hgetall.return_value = {
            "entity_type": "module",
            "resolved_path": "agentic_core/foo.py::Bar",
            "id": "30",
        }
        result = _load_layer_nodes(r, {"L0"})
        assert result == {}

    def test_empty_layer_returns_empty(self):
        r = MagicMock()
        r.smembers.return_value = set()
        result = _load_layer_nodes(r, {"L_UNKNOWN"})
        assert result == {}


# ---------------------------------------------------------------------------
# compute_coverage_gap
# ---------------------------------------------------------------------------


class TestComputeCoverageGap:
    def test_all_covered(self):
        prod = {"1": "agentic_core/L0_routing/config/path_constants.py"}
        test_set = {"99"}
        r = _make_redis(smembers_map={"adg:edge:in:1:covers": {"99"}})
        score, uncovered = compute_coverage_gap(r, prod, test_set)
        assert score == 0.0
        assert uncovered == []

    def test_none_covered(self):
        prod = {
            "1": "agentic_core/L0_routing/config/path_constants.py",
            "2": "agentic_core/L1_cognition/utils/agentic_constants_util.py",
        }
        test_set = {"99"}
        r = _make_redis(smembers_map={})  # no covers edges
        score, uncovered = compute_coverage_gap(r, prod, test_set)
        assert score == 1.0
        assert len(uncovered) == 2

    def test_partial_coverage(self):
        prod = {
            "1": "agentic_core/L0_routing/config/path_constants.py",
            "2": "agentic_core/L1_cognition/utils/agentic_constants_util.py",
            "3": "agentic_core/L2_execution/determinism.py",
        }
        test_set = {"99", "98"}
        r = _make_redis(
            smembers_map={
                "adg:edge:in:1:covers": {"99"},
                "adg:edge:in:2:covers": set(),
                "adg:edge:in:3:covers": set(),
            }
        )
        score, uncovered = compute_coverage_gap(r, prod, test_set)
        assert abs(score - 2 / 3) < 1e-9
        assert len(uncovered) == 2

    def test_stub_only_excluded_from_denominator(self):
        prod = {
            "1": "agentic_core/L0_routing/__init__.py",  # stub — excluded
            "2": "agentic_core/L0_routing/config/path_constants.py",
        }
        test_set = {"99"}
        r = _make_redis(smembers_map={"adg:edge:in:2:covers": {"99"}})
        score, uncovered = compute_coverage_gap(r, prod, test_set)
        assert score == 0.0  # denominator=1, covered=1

    def test_empty_prod_returns_zero(self):
        r = _make_redis()
        score, uncovered = compute_coverage_gap(r, {}, set())
        assert score == 0.0
        assert uncovered == []

    def test_non_test_importer_counts_as_uncovered(self):
        prod = {"1": "agentic_core/L0_routing/config/path_constants.py"}
        test_set = {"99"}
        # importer "50" is not in test_set
        r = _make_redis(smembers_map={"adg:edge:in:1:covers": {"50"}})
        score, uncovered = compute_coverage_gap(r, prod, test_set)
        assert score == 1.0
        assert "agentic_core/L0_routing/config/path_constants.py" in uncovered


# ---------------------------------------------------------------------------
# compute_blast_mismatch
# ---------------------------------------------------------------------------


class TestComputeBlastMismatch:
    def test_all_covered_zero_blast_score(self):
        prod = {"1": "agentic_core/foo.py", "2": "agentic_core/bar.py"}
        covered_set = {"1", "2"}
        r = _make_redis(scard_map={"adg:edge:1:imports": 10, "adg:edge:2:imports": 5})
        score, top = compute_blast_mismatch(r, prod, covered_set, [])
        assert score == 0.0

    def test_none_covered_full_blast_score(self):
        prod = {"1": "agentic_core/foo.py", "2": "agentic_core/bar.py"}
        covered_set = set()
        r = _make_redis(scard_map={"adg:edge:1:imports": 10, "adg:edge:2:imports": 5})
        score, top = compute_blast_mismatch(r, prod, covered_set, [])
        assert score == 1.0

    def test_partial_blast(self):
        prod = {"1": "agentic_core/foo.py", "2": "agentic_core/bar.py"}
        covered_set = {"1"}  # node 1 covered, node 2 not
        r = _make_redis(scard_map={"adg:edge:1:imports": 10, "adg:edge:2:imports": 10})
        score, top = compute_blast_mismatch(r, prod, covered_set, [])
        assert abs(score - 0.5) < 1e-9

    def test_p99_cap_applied(self):
        # 100 nodes with blast=1, 1 node with blast=10000
        prod = {str(i): f"agentic_core/mod{i}.py" for i in range(101)}
        covered_set = set()
        scard_map = {f"adg:edge:{i}:imports": 1 for i in range(100)}
        scard_map["adg:edge:100:imports"] = 10000  # outlier
        r = _make_redis(scard_map=scard_map)
        score, top = compute_blast_mismatch(r, prod, covered_set, [])
        # Score should be 1.0 (all uncovered) but outlier capped
        assert score == 1.0

    def test_top20_sorted_by_fan_out(self):
        prod = {str(i): f"agentic_core/mod{i}.py" for i in range(25)}
        covered_set = set()
        scard_map = {f"adg:edge:{i}:imports": i for i in range(25)}
        r = _make_redis(scard_map=scard_map)
        _, top = compute_blast_mismatch(r, prod, covered_set, [])
        assert len(top) == 20
        fan_outs = [e["fan_out"] for e in top]
        assert fan_outs == sorted(fan_outs, reverse=True)

    def test_empty_prod_returns_zero(self):
        r = _make_redis()
        score, top = compute_blast_mismatch(r, {}, set(), [])
        assert score == 0.0
        assert top == []


# ---------------------------------------------------------------------------
# compute_orphan_phantom
# ---------------------------------------------------------------------------


class TestComputeOrphanPhantom:
    def test_no_dead_imports_zero_score(self):
        test_nodes = {"1": "tests/unit/foo.py", "2": "tests/unit/bar.py"}
        r = _make_redis(scard_map={})  # all zero dead_imports
        score, orphans = compute_orphan_phantom(r, test_nodes, 0)
        assert score == 0.0
        assert orphans == []

    def test_all_orphan_full_score(self):
        test_nodes = {"1": "tests/unit/foo.py", "2": "tests/unit/bar.py"}
        r = _make_redis(
            scard_map={
                "adg:edge:1:dead_imports": 3,
                "adg:edge:2:dead_imports": 1,
            }
        )
        score, orphans = compute_orphan_phantom(r, test_nodes, 0)
        assert score == 1.0
        assert len(orphans) == 2

    def test_partial_orphan(self):
        test_nodes = {str(i): f"tests/unit/mod{i}.py" for i in range(10)}
        scard_map = {f"adg:edge:{i}:dead_imports": 1 for i in range(5)}
        r = _make_redis(scard_map=scard_map)
        score, orphans = compute_orphan_phantom(r, test_nodes, 0)
        assert abs(score - 0.5) < 1e-9

    def test_unresolved_adds_phantom_signal(self):
        test_nodes = {"1": "tests/unit/foo.py"}  # 1 test, no dead_imports
        r = _make_redis(scard_map={})
        # unresolved=2, test_fraction=1.0 → raw=2, capped at 1.0
        score, _ = compute_orphan_phantom(r, test_nodes, 2)
        assert score == 1.0

    def test_score_capped_at_one(self):
        test_nodes = {"1": "tests/unit/foo.py"}
        r = _make_redis(scard_map={"adg:edge:1:dead_imports": 100})
        score, _ = compute_orphan_phantom(r, test_nodes, 9999)
        assert score == 1.0

    def test_empty_test_nodes_returns_zero(self):
        r = _make_redis()
        score, orphans = compute_orphan_phantom(r, {}, 100)
        assert score == 0.0
        assert orphans == []


# ---------------------------------------------------------------------------
# compute_violation_gap
# ---------------------------------------------------------------------------


class TestComputeViolationGap:
    def test_no_violates_edges_zero_score(self):
        r = _make_redis(scan_results=[])
        score, gaps = compute_violation_gap(r, {"99"})
        assert score == 0.0
        assert gaps == []

    def test_violation_source_covered_zero_score(self):
        test_set = {"99"}
        r = _make_redis(
            scan_results=["adg:edge:5:violates"],
            smembers_map={"adg:edge:in:5:covers": {"99"}},
        )
        r.hgetall.return_value = {"resolved_path": "agentic_core/bad.py", "id": "5"}
        score, gaps = compute_violation_gap(r, test_set)
        assert score == 0.0
        assert gaps == []

    def test_violation_source_uncovered_full_score(self):
        test_set = {"99"}
        r = _make_redis(
            scan_results=["adg:edge:5:violates"],
            smembers_map={"adg:edge:in:5:covers": set()},
        )
        r.hgetall.return_value = {"resolved_path": "agentic_core/bad.py", "id": "5"}
        score, gaps = compute_violation_gap(r, test_set)
        assert score == 1.0
        assert "agentic_core/bad.py" in gaps

    def test_fan_in_keys_excluded(self):
        # adg:edge:in:5:violates should be excluded (fan-in key)
        test_set = {"99"}
        r = _make_redis(
            scan_results=["adg:edge:in:5:violates"],  # fan-in — should be filtered
        )
        score, gaps = compute_violation_gap(r, test_set)
        assert score == 0.0


# ---------------------------------------------------------------------------
# composite_score
# ---------------------------------------------------------------------------


class TestCompositeScore:
    def test_weights_sum_to_one(self):
        total = sum(WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_all_zero_is_zero(self):
        assert composite_score(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_all_one_is_one(self):
        assert abs(composite_score(1.0, 1.0, 1.0, 1.0) - 1.0) < 1e-9

    def test_known_values(self):
        # 0.40*0.5 + 0.30*0.5 + 0.20*0.5 + 0.10*0.5 = 0.5
        assert abs(composite_score(0.5, 0.5, 0.5, 0.5) - 0.5) < 1e-9

    def test_coverage_dominant(self):
        # D_coverage=1, rest=0 → score=0.40
        assert abs(composite_score(1.0, 0.0, 0.0, 0.0) - 0.40) < 1e-9

    def test_blast_weight(self):
        assert abs(composite_score(0.0, 1.0, 0.0, 0.0) - 0.30) < 1e-9

    def test_orphan_weight(self):
        assert abs(composite_score(0.0, 0.0, 1.0, 0.0) - 0.20) < 1e-9

    def test_violation_weight(self):
        assert abs(composite_score(0.0, 0.0, 0.0, 1.0) - 0.10) < 1e-9


# ---------------------------------------------------------------------------
# write_to_redis
# ---------------------------------------------------------------------------


class TestWriteToRedis:
    def _make_pipe(self):
        pipe = MagicMock()
        pipe.__enter__ = MagicMock(return_value=pipe)
        pipe.__exit__ = MagicMock(return_value=False)
        return pipe

    def test_all_six_keys_written(self):
        r = MagicMock()
        pipe = self._make_pipe()
        r.pipeline.return_value = pipe
        r.scan_iter.return_value = iter([])  # no existing drift keys

        write_to_redis(
            r,
            scores={"coverage": 0.5, "blast": 0.3, "orphan": 0.1, "violation": 0.0, "composite": 0.35},
            uncovered_paths=["agentic_core/foo.py"],
            orphan_paths=["tests/unit/dead.py"],
            blast_top=[{"path": "agentic_core/bar.py", "fan_out": 100}],
            violation_gaps=["agentic_core/bad.py"],
            prod_total=100,
            test_total=50,
        )

        pipe.execute.assert_called_once()

        # Verify key writes were called
        set_calls = [str(c) for c in pipe.set.call_args_list]
        hmset_calls = [str(c) for c in pipe.hmset.call_args_list]
        rpush_calls = [str(c) for c in pipe.rpush.call_args_list]

        assert any("adg:drift:score" in c for c in set_calls)
        assert any("adg:drift:subscores" in c for c in hmset_calls)
        assert any("adg:drift:uncovered" in c for c in rpush_calls)
        assert any("adg:drift:orphan_tests" in c for c in rpush_calls)
        assert any("adg:drift:blast_top" in c for c in rpush_calls)
        assert any("adg:drift:violation_gaps" in c for c in rpush_calls)

    def test_ttl_set_for_score_key(self):
        r = MagicMock()
        pipe = self._make_pipe()
        r.pipeline.return_value = pipe
        r.scan_iter.return_value = iter([])

        write_to_redis(
            r,
            scores={"coverage": 0.0, "blast": 0.0, "orphan": 0.0, "violation": 0.0, "composite": 0.0},
            uncovered_paths=[],
            orphan_paths=[],
            blast_top=[],
            violation_gaps=[],
            prod_total=0,
            test_total=0,
        )

        expire_calls = [str(c) for c in pipe.expire.call_args_list]
        assert any("adg:drift:score" in c and "3600" in c for c in expire_calls)

    def test_subscore_hash_contains_all_fields(self):
        r = MagicMock()
        pipe = self._make_pipe()
        r.pipeline.return_value = pipe
        r.scan_iter.return_value = iter([])

        write_to_redis(
            r,
            scores={"coverage": 0.4, "blast": 0.3, "orphan": 0.2, "violation": 0.1, "composite": 0.33},
            uncovered_paths=[],
            orphan_paths=[],
            blast_top=[],
            violation_gaps=[],
            prod_total=100,
            test_total=50,
        )

        hmset_calls = pipe.hmset.call_args_list
        assert len(hmset_calls) >= 1
        _, kwargs = hmset_calls[0]
        mapping = hmset_calls[0][0][1]  # second positional arg is the mapping dict
        for field in (
            "coverage",
            "blast",
            "orphan",
            "violation",
            "composite",
            "prod_total",
            "test_total",
            "timestamp",
        ):
            assert field in mapping, f"Missing field: {field}"
