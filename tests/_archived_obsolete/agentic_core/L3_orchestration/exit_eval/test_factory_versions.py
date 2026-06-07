"""Tests for version-aware rubric loading in exit_eval factory.

Covers the migration of X1D/X1F to v2 rubrics per
docs/archive/windsurf/legacy-tree/plans/runtime-gate-coverage-hardening-7e3f1a.md follow-up.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.factory import (
    _FALLBACK_VERSION,
    _resolve_rubric_version,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
RUBRIC_DIR = REPO_ROOT / "config" / "exit_eval_rubrics"


def test_versions_yaml_exists_and_parses() -> None:
    """The SSOT _versions.yaml must exist and parse."""
    import yaml

    path = RUBRIC_DIR / "_versions.yaml"
    assert path.exists(), f"missing version SSOT: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "versions" in data
    assert isinstance(data["versions"], dict)


def test_x1d_resolves_to_v2_by_default() -> None:
    """X1D defaulted to v2 on 2026-04-25 (G5 hard groundedness veto)."""
    assert _resolve_rubric_version("X1D", RUBRIC_DIR) == "v2"


def test_x1f_resolves_to_v2_by_default() -> None:
    """X1F defaulted to v2 on 2026-04-25 (G7 indirect injection)."""
    assert _resolve_rubric_version("X1F", RUBRIC_DIR) == "v2"


def test_x1a_x1b_remain_v1() -> None:
    """Other gates remain on v1 — only X1D/X1F migrated."""
    assert _resolve_rubric_version("X1A", RUBRIC_DIR) == "v1"
    assert _resolve_rubric_version("X1B", RUBRIC_DIR) == "v1"


def test_unknown_gate_falls_back_to_v1() -> None:
    """A gate not declared in the SSOT falls back to v1."""
    assert _resolve_rubric_version("XZZ", RUBRIC_DIR) == _FALLBACK_VERSION


def test_env_var_overrides_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    """EXIT_EVAL_RUBRIC_VERSION_X1D=v1 wins over the SSOT default."""
    monkeypatch.setenv("EXIT_EVAL_RUBRIC_VERSION_X1D", "v1")
    assert _resolve_rubric_version("X1D", RUBRIC_DIR) == "v1"


def test_missing_versions_yaml_falls_back(tmp_path: Path) -> None:
    """If _versions.yaml is absent, factory falls back to v1."""
    assert _resolve_rubric_version("X1D", tmp_path) == _FALLBACK_VERSION


def test_v2_files_exist() -> None:
    """The v2 rubric files referenced by _versions.yaml must be on disk."""
    assert (RUBRIC_DIR / "x1d_v2.yaml").exists()
    assert (RUBRIC_DIR / "x1f_v2.yaml").exists()


def test_v1_files_retained_for_backcompat() -> None:
    """v1 files retained so explicit-path callers (and rollback) still work."""
    assert (RUBRIC_DIR / "x1d_v1.yaml").exists()
    assert (RUBRIC_DIR / "x1f_v1.yaml").exists()


# ---- Edge cases (hardening pass) ----


def test_malformed_versions_yaml_falls_back(tmp_path: Path) -> None:
    """Garbage YAML in _versions.yaml must not crash; fall back to v1."""
    bad = tmp_path / "_versions.yaml"
    bad.write_text(":not yaml :: nope::", encoding="utf-8")
    assert _resolve_rubric_version("X1D", tmp_path) == _FALLBACK_VERSION


def test_versions_yaml_without_versions_block(tmp_path: Path) -> None:
    """If `versions:` key is missing, fall back to v1."""
    import yaml as _yaml

    (tmp_path / "_versions.yaml").write_text(_yaml.safe_dump({"unrelated": {"X1D": "v9"}}), encoding="utf-8")
    assert _resolve_rubric_version("X1D", tmp_path) == _FALLBACK_VERSION


def test_versions_yaml_non_dict_block(tmp_path: Path) -> None:
    """If `versions:` is a list (not a dict), fall back gracefully."""
    (tmp_path / "_versions.yaml").write_text("versions:\n  - X1D\n  - X1F\n", encoding="utf-8")
    assert _resolve_rubric_version("X1D", tmp_path) == _FALLBACK_VERSION


def test_versions_yaml_non_string_value_falls_back(tmp_path: Path) -> None:
    """If a gate's value is not a string (e.g. int 2), fall back to v1."""
    (tmp_path / "_versions.yaml").write_text("versions:\n  X1D: 2\n", encoding="utf-8")
    assert _resolve_rubric_version("X1D", tmp_path) == _FALLBACK_VERSION


def test_empty_env_var_does_not_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty-string env var must not be treated as a real override."""
    monkeypatch.setenv("EXIT_EVAL_RUBRIC_VERSION_X1D", "   ")
    assert _resolve_rubric_version("X1D", RUBRIC_DIR) == "v2"


def test_lowercase_gate_id_resolves(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lowercase gate id should still resolve (case-insensitive lookup)."""
    monkeypatch.delenv("EXIT_EVAL_RUBRIC_VERSION_X1D", raising=False)
    # _resolve_rubric_version is called with whatever build_pipeline passes.
    # Production callers always pass uppercase; this test guards against a
    # future caller passing lowercase.
    assert _resolve_rubric_version("x1d", RUBRIC_DIR) == "v2"


# ---- Integration smoke: build_pipeline actually loads v2 rubrics ----


def _build(gate_ids: list[str]):
    """Build a pipeline using the canonical FakeJudge + FakeCodeGrader stubs
    from conftest. Works for any combination of X1A/B/C/D/E/F gates because we
    supply overrides for every site-specific dimension the wiring requires."""
    from unittest.mock import MagicMock

    from agentic_core.L3_orchestration.exit_eval.factory import build_pipeline
    from tests.agentic_core.L3_orchestration.exit_eval.conftest import (
        FakeCodeGrader,
        FakeJudge,
    )

    bus = MagicMock()
    bus.emit_decision = MagicMock()
    return build_pipeline(
        gate_ids,
        bus_emitter=bus,
        judge_factory=lambda: FakeJudge(score=0.9),
        grader_overrides={
            "policy_match": FakeCodeGrader(score=1.0),  # X1A site-specific
            "schema_complete": FakeCodeGrader(score=1.0),  # X1B site-specific
            "bias_fairness": FakeCodeGrader(score=1.0),  # X1F site-specific
        },
    )


def test_build_pipeline_loads_x1d_v2_rubric() -> None:
    """End-to-end: build_pipeline(['X1D']) must load X1D@v2 (per SSOT)."""
    bundle = _build(["X1D"])
    assert len(bundle.gates) == 1
    rubric = bundle.gates[0].rubric
    assert rubric.gate == "X1D"
    assert rubric.version == "X1D@v2", f"expected X1D@v2 got {rubric.version}"


def test_build_pipeline_loads_x1f_v2_rubric() -> None:
    """End-to-end: build_pipeline(['X1F']) must load X1F@v2 (per SSOT)."""
    bundle = _build(["X1F"])
    assert len(bundle.gates) == 1
    rubric = bundle.gates[0].rubric
    assert rubric.gate == "X1F"
    assert rubric.version == "X1F@v2", f"expected X1F@v2 got {rubric.version}"


def test_build_pipeline_v1_unchanged() -> None:
    """X1A/X1B remain on v1 — no behavior change for non-promoted gates."""
    bundle = _build(["X1A", "X1B"])
    versions = {g.rubric.gate: g.rubric.version for g in bundle.gates}
    assert versions == {"X1A": "X1A@v1", "X1B": "X1B@v1"}


def test_build_pipeline_env_override_rolls_back_to_v1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Env var EXIT_EVAL_RUBRIC_VERSION_X1D=v1 must roll X1D back to v1
    without touching the SSOT — emergency rollback path."""
    monkeypatch.setenv("EXIT_EVAL_RUBRIC_VERSION_X1D", "v1")
    bundle = _build(["X1D"])
    assert bundle.gates[0].rubric.version == "X1D@v1"


def test_build_pipeline_invalid_version_raises_keyerror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An env override naming a non-existent version must produce a clear
    KeyError naming the missing path — fail-loud, not silent fallback."""
    monkeypatch.setenv("EXIT_EVAL_RUBRIC_VERSION_X1D", "v999")
    with pytest.raises(KeyError) as exc_info:
        _build(["X1D"])
    msg = str(exc_info.value)
    assert "X1D" in msg
    assert "v999" in msg


def test_build_pipeline_v2_loads_new_dims_indirect_injection() -> None:
    """X1F@v2 must expose the indirect_injection_resistance hard sub-gate."""
    bundle = _build(["X1F"])
    rubric = bundle.gates[0].rubric
    hard = {d.name for d in rubric.dimensions if d.is_hard_gate}
    assert "indirect_injection_resistance" in hard


def test_build_pipeline_v2_x1d_groundedness_strengthened() -> None:
    """X1D@v2 must tighten groundedness enforcement (G5 closure).

    NOTE: The exit-eval framework forbids model-graded hard sub-gates
    (gates.py — hard gates must be CODE_BASED). Therefore G5 is closed via
    THREE simultaneous mechanisms, all asserted here:
      1. groundedness weight increased (0.4 -> 0.5)
      2. aggregate_threshold tightened (0.75 -> 0.80)
      3. groundedness added to partial_credit.veto_dimensions in rubrics.yaml
         (asserted by test_groundedness_in_partial_credit_veto_list below)
    """
    bundle = _build(["X1D"])
    rubric = bundle.gates[0].rubric
    by_name = {d.name: d for d in rubric.dimensions}
    assert by_name["groundedness"].weight == 0.5
    assert by_name["groundedness"].threshold == 0.80
    assert rubric.aggregate_threshold == 0.80


def test_groundedness_in_partial_credit_veto_list() -> None:
    """The veto enforcement for groundedness lives in rubrics.yaml partial_credit.

    Test left as a documentation guard — if someone removes groundedness from
    veto_dimensions, this fails.
    """
    import yaml as _yaml

    rubrics_path = REPO_ROOT / "config" / "judges" / "rubrics.yaml"
    data = _yaml.safe_load(rubrics_path.read_text(encoding="utf-8"))
    veto = data.get("partial_credit", {}).get("veto_dimensions", []) or []
    # G7 closure (W1.2)
    assert "sec_indirect_injection_resistance" in veto
    # G11 closure (W1.2)
    assert "cross_context_leakage" in veto


# ---- CI wiring guards ----


def test_versions_yaml_skipped_by_wiring_check() -> None:
    """The CI wiring script must NOT treat _versions.yaml as a rubric file."""
    from ops_scripts.ci.check_exit_eval_wiring import _load_rubrics

    gate_to_path, errors = _load_rubrics()
    assert not errors, f"wiring check should have no rubric-load errors: {errors}"
    # _versions.yaml is not a rubric and must not appear keyed by any gate.
    paths = {str(p) for p in gate_to_path.values()}
    assert not any(p.endswith("_versions.yaml") for p in paths)
