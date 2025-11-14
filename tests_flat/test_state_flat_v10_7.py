# AUTO-GENERATED FLAT TEST FILE
# Sources:
#   - tests/state/test_state_evolution_v10_7.py
# ------------------------------------------------------------------
# ----- BEGIN: tests/state/test_state_evolution_v10_7.py -----
import pytest
from workflow.runner import run_workflow
import copy


# ----------------------------------------------------------------------
# Helper: remove volatile fields (timestamps, uuids, cost tokens)
# ----------------------------------------------------------------------
VOLATILE_KEYS = {"timestamp", "uuid", "usage", "cost", "trace_id"}


def _sanitize_state(state: dict):
    """
    Removes volatile fields that are allowed to differ run-run.
    Ensures stable comparison for deterministic state evolution tests.
    """
    if not isinstance(state, dict):
        return state

    clean = {}
    for k, v in state.items():
        if k in VOLATILE_KEYS:
            continue
        if isinstance(v, dict):
            clean[k] = _sanitize_state(v)
        else:
            clean[k] = v
    return clean


# ----------------------------------------------------------------------
# 1. State must monotonically grow (no loss of upstream keys)
# ----------------------------------------------------------------------
@pytest.mark.state
def test_state_grows_monotonically_through_pipeline():
    out = run_workflow({"resume": "StateGrowUser", "jd": "AI Exec"})
    resume = out["resume"]

    # Required blocks
    required_blocks = ["strategy", "rag", "drafting", "qa"]

    for blk in required_blocks:
        assert blk in resume, f"Missing required state block '{blk}'"

    # Strategy context must persist through entire pipeline
    assert resume["strategy"].get("context"), "Strategy context lost downstream"

    # RAG must add document/score
    assert resume["rag"].get("document"), "RAG did not populate document"

    # Drafting must add bullets or summary
    assert (
        resume.get("summary") or resume.get("bullets")
    ), "Drafting stage did not add summary or bullets"

    # QA must add issues/confidence
    assert "qa" in resume
    assert "issues" in resume["qa"], "QA issues missing"
    assert "confidence" in resume["qa"]


# ----------------------------------------------------------------------
# 2. No downstream stack may delete or overwrite upstream keys
# ----------------------------------------------------------------------
@pytest.mark.state
def test_no_upstream_state_loss():
    out = run_workflow({"resume": "UpstreamLossTest", "jd": "AWS"})
    resume = out["resume"]

    expected_upstream_keys = {"strategy", "rag"}

    missing = [k for k in expected_upstream_keys if k not in resume]
    assert not missing, f"Upstream blocks lost: {missing}"

    # Ensure strategy context preserved
    assert resume["strategy"].get("context"), (
        "Strategy context was lost or overwritten downstream"
    )


# ----------------------------------------------------------------------
# 3. Deterministic state: two runs must produce same cleaned structure
# ----------------------------------------------------------------------
@pytest.mark.state
def test_state_determinism_clean_structure():
    ctx = {"resume": "DeterminismUser", "jd": "Citi"}

    out1 = _sanitize_state(run_workflow(copy.deepcopy(ctx)))
    out2 = _sanitize_state(run_workflow(copy.deepcopy(ctx)))

    assert out1 == out2, (
        "State output mismatch across identical runs "
        "(determinism broken). "
        f"out1={out1}\nout2={out2}"
    )


# ----------------------------------------------------------------------
# 4. No cross-run state contamination / cache leakage
# ----------------------------------------------------------------------
@pytest.mark.state
def test_no_cross_run_state_leakage():
    out1 = run_workflow({"resume": "LeakUserA", "jd": "Exec"})
    out2 = run_workflow({"resume": "LeakUserB", "jd": "Exec"})

    clean1 = _sanitize_state(out1["resume"])
    clean2 = _sanitize_state(out2["resume"])

    # They should differ because resume text differs,
    # but no contamination should cause identical or oddly correlated outputs.
    assert clean1 != clean2, "Cross-run contamination detected (state leak)"


# ----------------------------------------------------------------------
# 5. State evolution must add AT LEAST N required keys vs empty initialization
# ----------------------------------------------------------------------
@pytest.mark.state
def test_state_adds_minimum_required_keys():
    out = run_workflow({"resume": "MinKeysTest", "jd": "Director"})
    resume = out["resume"]

    # enforce minimal required state topology
    required = [
        "strategy",
        "rag",
        "drafting",
        "qa",
        "events",
    ]

    for k in required:
        assert k in resume or k in out, (
            f"State missing required block '{k}'"
        )


# ----------------------------------------------------------------------
# 6. State consistency between events and resume blocks
# ----------------------------------------------------------------------
@pytest.mark.state
def test_event_sequence_matches_state_sequence():
    out = run_workflow({"resume": "SeqTest", "jd": "AWS"})
    resume = out["resume"]
    events = [str(e).lower() for e in out.get("events", [])]

    state_blocks_order = [
        ("strategy", "strategy"),
        ("rag", "rag"),
        ("bullet", "bullet"),
        ("draft", "draft"),
        ("qa", "qa"),
    ]

    for block, event_prefix in state_blocks_order:
        if block in resume:
            assert any(event_prefix in e for e in events), (
                f"State contains '{block}' but no corresponding '{event_prefix}' event recorded"
            )


# ----------------------------------------------------------------------
# 7. Regression tripwire: total number of resume keys must never shrink
# ----------------------------------------------------------------------
@pytest.mark.state
def test_total_resume_key_count_does_not_shrink():
    """
    Acts as a tripwire for structural regressions.
    For v10.7, resume typically contains 5–7 keys.
    This test enforces that the count does NOT shrink across refactors.
    """
    out = run_workflow({"resume": "CountTest", "jd": "Exec"})
    resume = out["resume"]

    assert len(resume.keys()) >= 5, (
        f"Resume structure shrunk unexpectedly: keys={list(resume.keys())}"
    )


# ----------------------------------------------------------------------
# 8. State blocks must be dict-like and preserve types across runs
# ----------------------------------------------------------------------
@pytest.mark.state
def test_state_block_type_stability():
    out = run_workflow({"resume": "TypeStableUser", "jd": "AI Exec"})
    resume = out["resume"]

    for blk in ["strategy", "rag", "drafting", "qa"]:
        val = resume.get(blk)
        assert isinstance(val, dict), (
            f"Block '{blk}' must be dict, got {type(val)}"
        )


# ----------------------------------------------------------------------
# 9. Summary/bullets must survive QA validation (no destructive overwrites)
# ----------------------------------------------------------------------
@pytest.mark.state
def test_drafting_content_survives_qa():
    out = run_workflow({"resume": "SurvivalTest", "jd": "CoreWeave"})
    resume = out["resume"]

    # QA must not erase summary content completely
    assert any(
        resume.get(k) for k in ("summary", "bullets")
    ), "Drafting content erased after QA stage"
# ----- END: tests/state/test_state_evolution_v10_7.py -----
