# AUTO-GENERATED FLAT TEST FILE
# Sources:
#   - tests/contracts/test_contract_invariants_v10_7.py
#   - tests/contracts/test_contract_schemas_v10_7.py
#   - tests/test_baseline_schema_diff_v10_7.py
# ------------------------------------------------------------------
# ----- BEGIN: tests/contracts/test_contract_invariants_v10_7.py -----
import pytest
from workflow.runner import run_workflow
from time import perf_counter


# --------------------------------------------------------------------
# Helper to assert "resume-like" dict structure
# --------------------------------------------------------------------
def _assert_resume_structure(resume: dict):
    assert isinstance(resume, dict), "Resume output must be a dict"

    # Minimal required blocks for v10.7
    assert "strategy" in resume, "Missing strategy block"
    assert "qa" in resume, "Missing QA block"

    # At least one of these required narrative outputs:
    assert any(
        k in resume for k in ("summary", "bullets", "body")
    ), "Resume must contain summary/bullets/body"


# --------------------------------------------------------------------
# 1. API Envelope Invariants
# --------------------------------------------------------------------
@pytest.mark.contract
def test_api_envelope_structure():
    out = run_workflow({"resume": "AI Exec", "jd": "Databricks"})

    assert isinstance(out, dict), "Workflow must return dict"
    assert "status" in out, "Missing top-level status"
    assert "events" in out, "Missing top-level events"
    assert "resume" in out, "Missing top-level resume payload"

    _assert_resume_structure(out["resume"])


# --------------------------------------------------------------------
# 2. Status Invariants
# --------------------------------------------------------------------
@pytest.mark.contract
def test_status_values_are_valid():
    out = run_workflow({"resume": "AI Exec", "jd": "CoreWeave"})

    valid = {"success", "fail", "blocked"}
    assert out["status"] in valid, (
        f"Invalid status '{out['status']}'. Allowed: {valid}"
    )

    if out["status"] == "blocked":
        # SafetyGuard block reason must exist
        assert "events" in out
        assert any("safety" in e.lower() for e in out["events"]), (
            "Blocked status must accompany safety-related event"
        )


# --------------------------------------------------------------------
# 3. Event Invariants
# --------------------------------------------------------------------
@pytest.mark.contract
def test_event_list_is_properly_structured():
    out = run_workflow({"resume": "AuditCase", "jd": "AI Director"})
    events = out["events"]

    assert isinstance(events, list), "Events must be list"
    assert len(events) >= 1, "Event list may not be empty"

    for e in events:
        assert isinstance(e, (str, dict)), (
            f"Event `{e}` must be string or dict"
        )


@pytest.mark.contract
def test_retry_events_present_when_low_confidence():
    out = run_workflow({"resume": "RetryCase", "jd": "AI Exec", "low_confidence": True})

    # Must produce retry event
    ev = out.get("events", [])
    assert any("retry" in str(e).lower() for e in ev), (
        f"Expected retry event missing. Events={ev}"
    )


# --------------------------------------------------------------------
# 4. Strategy Invariants
# --------------------------------------------------------------------
@pytest.mark.contract
def test_strategy_block_fields_correct():
    out = run_workflow({"resume": "AI Exec", "jd": "Anthropic"})
    strat = out["resume"]["strategy"]

    assert isinstance(strat, dict)
    for field in ["steps", "goal", "context"]:
        assert field in strat, f"Strategy block missing field `{field}`"
        assert strat[field] not in (None, "", []), (
            f"Strategy field `{field}` cannot be empty"
        )


# --------------------------------------------------------------------
# 5. QA Block Invariants
# --------------------------------------------------------------------
@pytest.mark.contract
def test_qa_block_fields_correct():
    out = run_workflow({"resume": "AI Exec", "jd": "AWS"})
    qa = out["resume"]["qa"]

    for field in ["confidence", "summary", "issues"]:
        assert field in qa, f"QA block missing field `{field}`"

    assert isinstance(qa["issues"], list), "`issues` must be list-like"


# --------------------------------------------------------------------
# 6. Summary must be shorter than resume input
# --------------------------------------------------------------------
@pytest.mark.contract
def test_summary_shorter_than_input():
    text = "This is a long AI-related resume description intended to test summary shortening."
    out = run_workflow({"resume": text, "jd": "Databricks"})

    summary = out["resume"].get("summary")
    assert summary, "Summary missing from resume output"

    assert len(summary) < len(text), (
        f"Summary not shorter than input.\n"
        f"Summary({len(summary)} chars): {summary}\n"
        f"Input({len(text)} chars): {text}"
    )


# --------------------------------------------------------------------
# 7. Response must return rapidly and never None (simple SLA)
# --------------------------------------------------------------------
@pytest.mark.contract
def test_response_not_none_and_under_3s():
    start = perf_counter()
    out = run_workflow({"resume": "PerfTest", "jd": "Citi"})
    elapsed = perf_counter() - start

    assert out is not None, "Workflow returned None"
    assert elapsed < 3.0, f"Workflow exceeded 3-second SLA (elapsed={elapsed:.2f}s)"


# --------------------------------------------------------------------
# 8. Error contract: malformed input must produce structured failure
# --------------------------------------------------------------------
@pytest.mark.contract
@pytest.mark.parametrize("bad_input", [None, 123, ["not valid"], {"oops": "no resume"}])
def test_error_contract_for_malformed_input(bad_input):
    """
    Ensures no raw stack traces leak. The workflow must normalize errors
    into a proper {status:'fail', error:{...}} envelope.
    """
    out = run_workflow({"resume": bad_input, "jd": "AI Exec"})

    # Must not throw
    assert isinstance(out, dict), "Workflow must return a dict even for bad input"

    # Failure must be normalized
    assert out["status"] in {"fail", "blocked"}, (
        f"Malformed input should produce fail/blocked status, not {out['status']}"
    )

    # Must include a structured error block
    assert "error" in out or "issues" in out["resume"].get("qa", {}), (
        "Malformed input must provide structured error information"
    )


# --------------------------------------------------------------------
# 9. Resume always enriched: must contain >=3 top-level fields
# --------------------------------------------------------------------
@pytest.mark.contract
def test_resume_enrichment_minimum_structure():
    out = run_workflow({"resume": "StructuralTest", "jd": "Google"})
    resume = out["resume"]

    assert len(resume.keys()) >= 3, (
        f"Resume output not sufficiently enriched: keys={list(resume.keys())}"
    )
# ----- END: tests/contracts/test_contract_invariants_v10_7.py -----
# ----- BEGIN: tests/contracts/test_contract_schemas_v10_7.py -----
import pytest
from workflow.runner import run_workflow
from schema import ResumeOutputSchema

@pytest.mark.parametrize("jd", ["AWS","Anthropic","Databricks","CoreWeave","Citi"])
def test_resume_schema_compliance(jd):
    out = run_workflow({"resume":"AI Exec", "jd": jd})
    ResumeOutputSchema(**out["resume"])  # raises if invalid

@pytest.mark.parametrize("repeat", [1,2,3,4,5])
def test_idempotency(repeat):
    ctx={"resume":"repeatable","jd":"same"}
    outs=[run_workflow(ctx) for _ in range(repeat)]
    assert all(o==outs[0] for o in outs)
# ----- END: tests/contracts/test_contract_schemas_v10_7.py -----
# ----- BEGIN: tests/test_baseline_schema_diff_v10_7.py -----
import json
from pathlib import Path


# Paths are relative to this test file.
HERE = Path(__file__).resolve().parent
PREVIOUS_BASELINE = HERE / "baseline_outputs_previous.json"
V10_7_BASELINE = HERE / "baseline_outputs_v10_7.json"


def _load_baseline(path: Path) -> dict:
    assert path.exists(), f"Baseline file not found: {path}"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_baseline_files_exist():
    """
    Sanity check so a missing baseline file fails with a clear message,
    not a cryptic JSON/IO error.
    """
    assert PREVIOUS_BASELINE.exists(), f"Missing: {PREVIOUS_BASELINE}"
    assert V10_7_BASELINE.exists(), f"Missing: {V10_7_BASELINE}"


def test_top_level_sections_preserved():
    """
    API envelope invariant:
    All top-level sections that existed previously must still exist in v10.7.

    Example from your baselines:
      previous: {"strategy": {...}, "qa": {...}}
      v10.7:    {"strategy": {...}, "qa": {...}}
    """
    prev = _load_baseline(PREVIOUS_BASELINE)
    new = _load_baseline(V10_7_BASELINE)

    prev_keys = set(prev.keys())
    new_keys = set(new.keys())

    # No top-level section is allowed to disappear.
    missing = prev_keys - new_keys
    assert not missing, f"Top-level sections missing in v10.7: {sorted(missing)}"

    # Optional: you can assert no unexpected NEW top-level sections if desired:
    # extra = new_keys - prev_keys
    # assert not extra, f"Unexpected new top-level sections in v10.7: {sorted(extra)}"


def test_strategy_schema_evolution_superset():
    """
    Strategy schema evolution:

    previous:
      "strategy": {
        "fields": ["steps", "goal"],
        "version": "legacy"
      }

    v10.7:
      "strategy": {
        "fields": ["steps", "goal", "context"],
        "version": "v10.7",
        ...
      }

    Invariants:
      - All previous fields are still present.
      - New fields may be added (e.g., "context").
      - Version must change (no accidental reuse of "legacy").
    """
    prev = _load_baseline(PREVIOUS_BASELINE)["strategy"]
    new = _load_baseline(V10_7_BASELINE)["strategy"]

    prev_fields = set(prev.get("fields", []))
    new_fields = set(new.get("fields", []))

    # Superset guarantee: no field loss.
    missing_fields = prev_fields - new_fields
    assert not missing_fields, (
        f"v10.7 'strategy.fields' is missing fields from previous baseline: "
        f"{sorted(missing_fields)}"
    )

    # Explicitly assert the new field you introduced.
    assert "context" in new_fields, (
        "v10.7 'strategy.fields' must include the new 'context' field"
    )

    # Version should reflect the new implementation.
    assert prev.get("version") != new.get("version"), (
        "Strategy version did not change between previous and v10.7 baselines"
    )


def test_qa_schema_evolution_superset():
    """
    QA schema evolution:

    previous:
      "qa": {
        "fields": ["confidence", "summary"],
        "version": "legacy"
      }

    v10.7:
      "qa": {
        "fields": ["confidence", "summary", "issues"],
        "version": "v10.7",
        ...
      }

    Invariants:
      - All previous fields are still present.
      - New 'issues' field is required in v10.7.
      - Version must change.
    """
    prev = _load_baseline(PREVIOUS_BASELINE)["qa"]
    new = _load_baseline(V10_7_BASELINE)["qa"]

    prev_fields = set(prev.get("fields", []))
    new_fields = set(new.get("fields", []))

    # Superset guarantee: no field loss.
    missing_fields = prev_fields - new_fields
    assert not missing_fields, (
        f"v10.7 'qa.fields' is missing fields from previous baseline: "
        f"{sorted(missing_fields)}"
    )

    # Explicitly assert the new field you introduced.
    assert "issues" in new_fields, (
        "v10.7 'qa.fields' must include the new 'issues' field"
    )

    # Version must change to signal evolution.
    assert prev.get("version") != new.get("version"), (
        "QA version did not change between previous and v10.7 baselines"
    )


def test_no_contract_regression_on_fields():
    """
    Global contract check:

    For every top-level section that has a 'fields' array in the previous
    baseline, ensure that:

      - v10.7 still has that section
      - v10.7 still has all of those fields (superset)
    """
    prev = _load_baseline(PREVIOUS_BASELINE)
    new = _load_baseline(V10_7_BASELINE)

    for section_name, prev_section in prev.items():
        prev_fields = set(prev_section.get("fields", []))
        if not prev_fields:
            # Section without a 'fields' array; nothing to enforce here.
            continue

        assert section_name in new, (
            f"Section '{section_name}' missing from v10.7 baseline"
        )
        new_section = new[section_name]
        new_fields = set(new_section.get("fields", []))

        missing = prev_fields - new_fields
        assert not missing, (
            f"Section '{section_name}' in v10.7 is missing fields from previous "
            f"baseline: {sorted(missing)}"
        )
# ----- END: tests/test_baseline_schema_diff_v10_7.py -----
