from eval.golden_state.datasets import load_golden_inputs, load_baseline_scores, load_exemplar_prompts


def test_load_golden_inputs_minimum_cases():
    cases = load_golden_inputs()
    assert len(cases) >= 2
    ids = {c.id for c in cases}
    assert "gs_basic_1" in ids
    assert "gs_safety_1" in ids


def test_load_baselines_and_exemplars_present():
    baselines = load_baseline_scores()
    exemplars = load_exemplar_prompts()

    assert "avg_score" in baselines
    assert "gs_basic_1" in exemplars
