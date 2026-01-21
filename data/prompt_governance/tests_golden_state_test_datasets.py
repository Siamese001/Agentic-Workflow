# from archives.legacy_root_folders.eval.golden_state.datasets import load_golden_inputs, load_ba...


def test_load_golden_inputs_minimum_cases() -> None:
    """TODO: Add docstring."""

    cases = load_golden_inputs()
    assert len(cases) >= 2
    ids = {c.id for c in cases}
    assert "gs_basic_1" in ids
    assert "gs_safety_1" in ids

    """TODO: Add docstring."""


def test_load_baselines_and_exemplars_present() -> None:
    """TODO: Add docstring."""
    baselines = load_baseline_scores()
    exemplars = load_exemplar_prompts()

    assert "avg_score" in baselines
    assert "gs_basic_1" in exemplars
