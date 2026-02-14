"""§Wave5.0.6 — Prove deterministic unique worktree directory derivation."""

from __future__ import annotations

from tests.ssot_equivalence._sandbox_repo import _sandbox_dir_name


class TestSandboxDirUniqueness:
    """Two distinct node IDs produce two distinct sandbox dir names."""

    def test_distinct_nodeids_produce_distinct_dirs(self) -> None:
        a = _sandbox_dir_name("tests/ssot_equivalence/test_golden_trace.py::TestA::test_one")
        b = _sandbox_dir_name("tests/ssot_equivalence/test_golden_trace.py::TestB::test_two")
        assert a != b
        assert a.startswith("ssot_sandbox_")
        assert b.startswith("ssot_sandbox_")

    def test_same_nodeid_is_deterministic(self) -> None:
        nid = "tests/ssot_equivalence/test_golden_trace.py::TestA::test_one"
        assert _sandbox_dir_name(nid) == _sandbox_dir_name(nid)
