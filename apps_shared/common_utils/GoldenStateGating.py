# from archives.legacy_root_folders.eval.golden_state.gating import gate_experiment  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_gate_experiment_allows_without_baseline() -> None:
    assert gate_experiment({"avg_score": 0.5}, {}) is True


def test_gate_experiment_enforces_avg_and_pass_count() -> None:
    baseline = {"avg_score": 0.8, "pass_count": 2}

    better = {"avg_score": 0.9, "pass_count": 2}
    worse_avg = {"avg_score": 0.7, "pass_count": 3}
    worse_pass = {"avg_score": 0.9, "pass_count": 1}

    assert gate_experiment(better, baseline) is True
    assert gate_experiment(worse_avg, baseline) is False
    assert gate_experiment(worse_pass, baseline) is False
