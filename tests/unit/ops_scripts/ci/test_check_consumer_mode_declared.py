"""Unit tests for the W4 consumer-mode declaration spec + CI gate."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.artifact.consumer_mode import (  # noqa: E402
    ALL_CONSUMER_MODES,
    CONSUMER_MODE_INVENTORY,
    CONSUMER_MODE_PROOF,
    CONSUMER_MODE_RISK,
    DECLARATION_NAME,
    MODE_AUTHORITY_RANK,
    VIEW_TO_REQUIRED_MODE,
    is_mode_compatible_with_view,
    is_valid_mode,
)

# ---------------------------------------------------------------------------
# consumer_mode.py — closed enums + authority law
# ---------------------------------------------------------------------------


class TestConsumerModeEnum:
    def test_three_modes_exactly(self) -> None:
        assert ALL_CONSUMER_MODES == frozenset({"proof", "risk", "inventory"})

    def test_declaration_name_is_canonical(self) -> None:
        assert DECLARATION_NAME == "__adg_consumer_mode__"

    def test_mode_authority_rank_is_total_order(self) -> None:
        assert MODE_AUTHORITY_RANK == {
            CONSUMER_MODE_INVENTORY: 0,
            CONSUMER_MODE_RISK: 1,
            CONSUMER_MODE_PROOF: 2,
        }

    def test_is_valid_mode(self) -> None:
        assert is_valid_mode(CONSUMER_MODE_PROOF)
        assert is_valid_mode(CONSUMER_MODE_RISK)
        assert is_valid_mode(CONSUMER_MODE_INVENTORY)
        assert not is_valid_mode("verdict")
        assert not is_valid_mode("")
        assert not is_valid_mode("PROOF")  # case-sensitive


class TestModeCompatibility:
    """Authority rule:
        proof  may read proof_view, risk_view, inventory_view
        risk   may read risk_view, inventory_view  (NOT proof_view)
        inventory may read inventory_view only
    """

    def test_proof_may_read_every_view(self) -> None:
        for view in ("proof_view", "risk_view", "inventory_view"):
            assert is_mode_compatible_with_view(
                declared_mode=CONSUMER_MODE_PROOF, view_name=view
            ), f"proof should be allowed to read {view}"

    def test_risk_may_not_read_proof_view(self) -> None:
        assert not is_mode_compatible_with_view(
            declared_mode=CONSUMER_MODE_RISK, view_name="proof_view"
        )

    def test_risk_may_read_risk_and_inventory(self) -> None:
        for view in ("risk_view", "inventory_view"):
            assert is_mode_compatible_with_view(
                declared_mode=CONSUMER_MODE_RISK, view_name=view
            )

    def test_inventory_may_read_inventory_only(self) -> None:
        assert is_mode_compatible_with_view(
            declared_mode=CONSUMER_MODE_INVENTORY, view_name="inventory_view"
        )
        assert not is_mode_compatible_with_view(
            declared_mode=CONSUMER_MODE_INVENTORY, view_name="risk_view"
        )
        assert not is_mode_compatible_with_view(
            declared_mode=CONSUMER_MODE_INVENTORY, view_name="proof_view"
        )

    def test_legacy_aliases_resolve_to_correct_minimum_mode(self) -> None:
        # mv_verified_dependencies → proof
        assert (
            VIEW_TO_REQUIRED_MODE["mv_verified_dependencies"] == CONSUMER_MODE_PROOF
        )
        # mv_unresolved_dependencies → risk
        assert (
            VIEW_TO_REQUIRED_MODE["mv_unresolved_dependencies"] == CONSUMER_MODE_RISK
        )
        # mv_governance_dependencies → risk
        assert (
            VIEW_TO_REQUIRED_MODE["mv_governance_dependencies"] == CONSUMER_MODE_RISK
        )

    def test_unknown_view_only_proof_mode_allowed(self) -> None:
        # Conservative rule: unknown views can only be read by proof-mode.
        assert is_mode_compatible_with_view(
            declared_mode=CONSUMER_MODE_PROOF, view_name="some_future_view"
        )
        assert not is_mode_compatible_with_view(
            declared_mode=CONSUMER_MODE_RISK, view_name="some_future_view"
        )
        assert not is_mode_compatible_with_view(
            declared_mode=CONSUMER_MODE_INVENTORY, view_name="some_future_view"
        )

    def test_invalid_mode_returns_false(self) -> None:
        assert not is_mode_compatible_with_view(
            declared_mode="garbage", view_name="proof_view"
        )


# ---------------------------------------------------------------------------
# check_consumer_mode_declared.py — CI gate
# ---------------------------------------------------------------------------


# Late import — the gate module sits under ops_scripts/ci which is not a
# package; load the file directly to avoid the path-not-importable issue.
import importlib.util

GATE_SOURCE = REPO_ROOT / "ops_scripts" / "ci" / "check_consumer_mode_declared.py"
_spec = importlib.util.spec_from_file_location(
    "check_consumer_mode_declared", GATE_SOURCE
)
assert _spec is not None and _spec.loader is not None
GATE = importlib.util.module_from_spec(_spec)
# Python 3.12 + @dataclass needs the module registered in sys.modules before
# exec — otherwise dataclasses._is_type() crashes on cls.__module__ lookup.
sys.modules["check_consumer_mode_declared"] = GATE
_spec.loader.exec_module(GATE)


class TestExtractConstant:
    def test_extracts_string_constant(self) -> None:
        src = '"""docstring"""\n__adg_consumer_mode__ = "proof"\n'
        assert GATE.extract_module_level_constant(src, "__adg_consumer_mode__") == "proof"

    def test_returns_none_when_missing(self) -> None:
        src = '"""no declaration here"""\nx = 1\n'
        assert GATE.extract_module_level_constant(src, "__adg_consumer_mode__") is None

    def test_ignores_non_string_value(self) -> None:
        src = "__adg_consumer_mode__ = 42\n"
        assert GATE.extract_module_level_constant(src, "__adg_consumer_mode__") is None

    def test_ignores_assignment_inside_function(self) -> None:
        # We only care about module-level declarations.
        src = "def f():\n    __adg_consumer_mode__ = 'proof'\n"
        assert GATE.extract_module_level_constant(src, "__adg_consumer_mode__") is None

    def test_handles_syntax_errors(self) -> None:
        src = "this is not python !@#"
        assert GATE.extract_module_level_constant(src, "__adg_consumer_mode__") is None


class TestDetectViewsUsed:
    def test_detects_canonical_views(self) -> None:
        src = "SELECT * FROM proof_view; FROM risk_view; FROM inventory_view"
        views = GATE.detect_views_used(src)
        assert sorted(views) == ["inventory_view", "proof_view", "risk_view"]

    def test_detects_join_clauses(self) -> None:
        src = "SELECT a FROM edges JOIN proof_view p ON ..."
        assert "proof_view" in GATE.detect_views_used(src)

    def test_case_insensitive(self) -> None:
        src = "from PROOF_VIEW"
        assert "proof_view" in GATE.detect_views_used(src)

    def test_no_views_returns_empty(self) -> None:
        src = "x = 1"
        assert GATE.detect_views_used(src) == []


class TestIsAdgConsumer:
    def test_returns_false_for_excluded_writer_files(self) -> None:
        assert not GATE.is_adg_consumer(
            "agentic_core/adg/artifact/edge_authority.py",
            "FROM edges; INSERT INTO edges",
        )

    def test_returns_false_for_files_outside_consumer_dirs(self) -> None:
        assert not GATE.is_adg_consumer(
            "docs/architecture/adr/foo.md",
            "FROM edges",
        )

    def test_returns_true_for_consumer_with_read_signature(self) -> None:
        assert GATE.is_adg_consumer(
            "ops_scripts/ci/check_some_thing.py",
            "FROM edges WHERE authority='verified'",
        )

    def test_returns_false_for_consumer_dir_file_with_no_reads(self) -> None:
        # File is under ops_scripts/ci but has no ADG read signature.
        assert not GATE.is_adg_consumer(
            "ops_scripts/ci/check_unrelated.py",
            "x = 1\nprint('hello')",
        )


class TestScanGate:
    def _write_consumer(
        self, tmp: Path, rel: str, body: str
    ) -> Path:
        # Mimic the consumer-dir layout under ``tmp`` so iter_candidate_files
        # picks up the synthetic files.
        full = tmp / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(body, encoding="utf-8")
        logging.info("C3 write receipt: consumer-mode declaration fixture written")
        return full

    def test_scans_zero_consumers_in_empty_tree(self, tmp_path: Path) -> None:
        report = GATE.scan(tmp_path)
        assert report.consumers_scanned == 0
        assert len(report.violations) == 0

    def test_flags_missing_declaration(self, tmp_path: Path) -> None:
        # Build a fake consumer under ops_scripts/ci/ with an ADG read but
        # no __adg_consumer_mode__ declaration.
        self._write_consumer(
            tmp_path,
            "ops_scripts/ci/check_synth.py",
            '"""no mode here."""\nimport sqlite3\n# FROM edges\n',
        )
        report = GATE.scan(tmp_path)
        assert report.consumers_scanned == 1
        assert report.missing == 1
        assert report.violations[0].kind == "missing"
        assert "synth" in report.violations[0].rel_path

    def test_passes_for_well_declared_consumer(self, tmp_path: Path) -> None:
        self._write_consumer(
            tmp_path,
            "ops_scripts/ci/check_synth.py",
            '"""ok."""\n__adg_consumer_mode__ = "risk"\n# FROM edges WHERE x=1\n',
        )
        report = GATE.scan(tmp_path)
        assert report.consumers_scanned == 1
        assert report.declared == 1
        assert report.missing == 0
        assert report.invalid == 0
        assert report.mode_mismatch == 0
        assert len(report.violations) == 0

    def test_flags_invalid_mode_value(self, tmp_path: Path) -> None:
        self._write_consumer(
            tmp_path,
            "ops_scripts/ci/check_synth.py",
            '"""bad value."""\n__adg_consumer_mode__ = "verdict"\n# FROM edges\n',
        )
        report = GATE.scan(tmp_path)
        assert report.consumers_scanned == 1
        assert report.invalid == 1
        assert report.violations[0].kind == "invalid_value"
        assert report.violations[0].declared_mode == "verdict"

    def test_flags_mode_mismatch(self, tmp_path: Path) -> None:
        # Inventory mode trying to read proof_view → mismatch.
        self._write_consumer(
            tmp_path,
            "ops_scripts/ci/check_synth.py",
            '"""mismatch."""\n__adg_consumer_mode__ = "inventory"\n'
            "# SELECT * FROM proof_view\n",
        )
        report = GATE.scan(tmp_path)
        assert report.consumers_scanned == 1
        assert report.declared == 1
        assert report.mode_mismatch == 1
        assert report.violations[0].kind == "mode_mismatch"
        assert "proof_view" in report.violations[0].message

    def test_proof_mode_can_read_any_view(self, tmp_path: Path) -> None:
        self._write_consumer(
            tmp_path,
            "ops_scripts/ci/check_synth.py",
            '"""proof can read everything."""\n'
            '__adg_consumer_mode__ = "proof"\n'
            "# SELECT * FROM proof_view JOIN risk_view ON ... JOIN inventory_view ON ...\n",
        )
        report = GATE.scan(tmp_path)
        assert report.declared == 1
        assert report.mode_mismatch == 0
        assert len(report.violations) == 0


class TestLiveRepoState:
    """Smoke tests against the live repo — the 5 W4 exemplars must declare."""

    EXEMPLARS_AND_MODES = {
        "ops_scripts/ci/check_edge_authority_well_formed.py": "proof",
        "ops_scripts/ci/check_unresolved_edges_ratchet.py": "risk",
        "ops_scripts/ci/check_dangling_imports.py": "risk",
        "ops_scripts/ci/check_call_multiplicity.py": "inventory",
        "ops_scripts/ci/check_w6_new_orphans_delta.py": "risk",
    }

    def test_each_exemplar_declares_correct_mode(self) -> None:
        for rel, expected_mode in self.EXEMPLARS_AND_MODES.items():
            full = REPO_ROOT / rel
            if not full.exists():
                pytest.skip(f"{rel} not found in this checkout")
            src = full.read_text(encoding="utf-8", errors="replace")
            actual = GATE.extract_module_level_constant(src, "__adg_consumer_mode__")
            assert actual == expected_mode, (
                f"{rel}: expected `__adg_consumer_mode__ = {expected_mode!r}`, "
                f"got {actual!r}"
            )

    def test_live_scan_returns_some_declared_consumers(self) -> None:
        # 3 of the 5 W4 exemplars actively query the ADG SQLite and so qualify
        # as 'consumers' under the gate's strict definition. The other 2
        # (dangling_imports, call_multiplicity) are AST/filesystem walkers —
        # their declarations document intent but they are not classified as
        # SQLite consumers and so do not increment the `declared` counter.
        report = GATE.scan()
        assert report.declared >= 3, (
            f"expected ≥3 declared consumers from W4 exemplars; got {report.declared}"
        )
        # W3 P3.1 (2026-04-30) converged the sweep — all detected consumers
        # MUST now declare. Prior W4-era residue of ~70 unannotated files has
        # been fully annotated across sessions (125 in earlier sessions + the
        # final 2 in P3.1: `tools/adg/integration/common.py` and
        # `tools/adg/integration/calls_ingester.py`). Gate is fail-closed on
        # any regression — if this assertion flips back, a new consumer landed
        # without the declaration and must be annotated before commit.
        assert report.missing == 0, (
            f"expected 0 unannotated consumers post-P3.1; got {report.missing}. "
            f"Run `python ops_scripts/ci/annotate_consumer_mode.py --apply` "
            f"to close the gap."
        )
