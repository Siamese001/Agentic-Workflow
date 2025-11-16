from workflow.runner import run_workflow


def test_legacy_resume_view_is_filtered():
    out = run_workflow({"resume": "CompatUser", "jd": "Engineer"})

    assert set(out["resume"].keys()) == {
        "candidate",
        "job_title",
        "summary",
        "highlights",
        "skills",
        "sections",
    }
    assert "state" in out
    assert "master_resume" not in out["resume"]


def test_full_state_available_in_v10_8_mode():
    out = run_workflow(
        {"resume": "CompatUser", "jd": "Engineer", "v10_8_test_mode": True}
    )

    assert "master_resume" in out["resume"]
    assert out["state"]["memory"]["episodic"]["conversation"]
    assert out["state"]["ephemeral"]["events"]
    assert out["resume"]["candidate"] == "CompatUser"
