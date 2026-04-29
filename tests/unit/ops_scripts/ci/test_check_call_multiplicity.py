"""Unit tests for ``ops_scripts/ci/check_call_multiplicity.py``."""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci import check_call_multiplicity as gate  # noqa: E402


@pytest.fixture
def synthetic_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    pkg = tmp_path / "agentic_core"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gate, "LOG_DIR", tmp_path / "log")
    monkeypatch.setattr(gate, "LOG_FILE", tmp_path / "log" / "violations.jsonl")
    monkeypatch.setattr(gate, "BASELINE_DIR", tmp_path / "baselines")
    monkeypatch.setattr(gate, "BASELINE_FILE", tmp_path / "baselines" / "ratchet.json")
    return tmp_path


def _write(repo: Path, rel: str, body: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body), encoding="utf-8")


class TestTopLevelCallExtraction:
    def test_module_level_calls_counted(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/instrumented.py",
            """
            def _emit(layer, name, tag):
                pass

            _emit("p1", "x", "a")
            _emit("p1", "x", "b")
            _emit("p1", "x", "c")
            _emit("p1", "x", "d")
            _emit("p1", "x", "e")
            _emit("p1", "x", "f")
            """,
        )
        outcome = gate.run_gate(synthetic_repo, threshold=5)
        assert len(outcome.hotspots) == 1
        h = outcome.hotspots[0]
        assert h.call_target == "_emit"
        assert h.occurrences == 6

    def test_calls_inside_functions_NOT_counted(self, synthetic_repo: Path) -> None:
        # Calls within function bodies execute per-call, not at module load.
        # The gate must NOT flag these.
        _write(
            synthetic_repo,
            "agentic_core/normal.py",
            """
            def runner():
                _emit("p1", "x", "a")
                _emit("p1", "x", "b")
                _emit("p1", "x", "c")
                _emit("p1", "x", "d")
                _emit("p1", "x", "e")
                _emit("p1", "x", "f")
                _emit("p1", "x", "g")
            """,
        )
        outcome = gate.run_gate(synthetic_repo, threshold=5)
        assert outcome.hotspots == []

    def test_threshold_respected(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/instrumented.py",
            """
            _emit("a")
            _emit("b")
            _emit("c")
            """,
        )
        # threshold=5: 3 occurrences should NOT trigger
        outcome_high = gate.run_gate(synthetic_repo, threshold=5)
        assert outcome_high.hotspots == []
        # threshold=2: 3 occurrences SHOULD trigger
        outcome_low = gate.run_gate(synthetic_repo, threshold=2)
        assert len(outcome_low.hotspots) == 1
        assert outcome_low.hotspots[0].occurrences == 3

    def test_attribute_call_targets_resolved(self, synthetic_repo: Path) -> None:
        # Calls like obj.method() captured as 'obj.method'
        _write(
            synthetic_repo,
            "agentic_core/instrumented.py",
            """
            import logging
            logging.info("a")
            logging.info("b")
            logging.info("c")
            logging.info("d")
            logging.info("e")
            logging.info("f")
            """,
        )
        outcome = gate.run_gate(synthetic_repo, threshold=5)
        assert len(outcome.hotspots) == 1
        assert outcome.hotspots[0].call_target == "logging.info"

    def test_calls_inside_if_main_guard_counted(self, synthetic_repo: Path) -> None:
        # `if __name__ == "__main__":` block runs at module load when invoked
        # directly. Calls inside the guard ARE module-load-equivalent.
        _write(
            synthetic_repo,
            "agentic_core/main_module.py",
            """
            if __name__ == "__main__":
                _emit("a")
                _emit("b")
                _emit("c")
                _emit("d")
                _emit("e")
                _emit("f")
            """,
        )
        outcome = gate.run_gate(synthetic_repo, threshold=5)
        assert len(outcome.hotspots) == 1
        assert outcome.hotspots[0].occurrences == 6


class TestRegressionCase:
    """Reproduce the auto-instrumentation pollution pattern from the
    2026-04-28 RCA (full_agent_discovery, safety_kernel_seam): 80+ identical
    `_emit_*("p1", "<module>", "<tag>")` calls at module load."""

    def test_pollution_pattern_caught(self, synthetic_repo: Path) -> None:
        # Build a module with the actual pollution shape.
        body = "\n".join(f'_emit_routes_through("p1", "fake_module", "tag_{i}")' for i in range(20))
        _write(
            synthetic_repo,
            "agentic_core/polluted.py",
            "def _emit_routes_through(*args): pass\n" + body + "\n",
        )
        outcome = gate.run_gate(synthetic_repo, threshold=5)
        assert len(outcome.hotspots) == 1
        h = outcome.hotspots[0]
        assert h.call_target == "_emit_routes_through"
        assert h.occurrences == 20


class TestBaseline:
    def test_baseline_unset_first_run_passes(self, synthetic_repo: Path) -> None:
        _write(
            synthetic_repo,
            "agentic_core/polluted.py",
            "def _emit(): pass\n" + "\n".join(["_emit()"] * 8) + "\n",
        )
        # Manually exercise main() via run_gate + the baseline-load path
        outcome = gate.run_gate(synthetic_repo, threshold=5)
        baseline = gate._load_baseline()  # noqa: SLF001 — internal access for test
        assert baseline is None
        assert len(outcome.hotspots) == 1


class TestBypass:
    def test_env_bypass_short_circuits(self, synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write(
            synthetic_repo,
            "agentic_core/polluted.py",
            "def _emit(): pass\n" + "\n".join(["_emit()"] * 100) + "\n",
        )
        monkeypatch.setenv("CALL_MULTIPLICITY_BYPASS", "1")
        outcome = gate.run_gate(synthetic_repo)
        assert outcome.bypassed is True
        assert outcome.hotspots == []
