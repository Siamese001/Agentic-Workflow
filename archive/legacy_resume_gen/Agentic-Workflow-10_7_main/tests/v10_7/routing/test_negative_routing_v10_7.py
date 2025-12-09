import pytest
from workflow.runner import run_workflow
import re


# ---------------------------------------------------------------------
# Helper: detect stack trace leakage
# ---------------------------------------------------------------------
TRACE_PATTERNS = [
    "Traceback (most recent call last)",
    "File \"",
    "Exception:",
    "ValueError:",
    "TypeError:",
    "KeyError:",
]


def _contains_trace(text: str) -> bool:
    return any(pat in text for pat in TRACE_PATTERNS)


# ---------------------------------------------------------------------
# 1. SafetyGuard must block clearly unsafe inputs
# ---------------------------------------------------------------------
@pytest.mark.routing
@pytest.mark.parametrize("unsafe_payload", [
    None,
    "",
    0,
    123,
    {},
    {"resume": None, "jd": "AI Exec"},
    {"resume": "AI Exec", "jd": None},
])
def test_safetyguard_blocks_unsafe_inputs(unsafe_payload):
    """
    SafetyGuard must run FIRST and block invalid payloads with a
    normalized {status:'blocked', error:{...}} envelope.
    """
    # Normalize input to correct API shape
    if isinstance(unsafe_payload, dict):
        inp = {**unsafe_payload, "compat_mode": "v10_7"}
    else:
        inp = {"compat_mode": "v10_7", "resume": unsafe_payload, "jd": "AI Exec"}

    out = run_workflow(inp)

    # Must not crash
    assert isinstance(out, dict), "Workflow output must be dict"

    # SafetyGuard must be the blocker
    assert out["status"] in {"blocked", "fail"}, (
        f"Unsafe payload should block early. Got status={out['status']}"
    )

    # Safety event must appear
    events = out.get("events", [])
    assert any("safety" in str(e).lower() for e in events), (
        "SafetyGuard event missing despite unsafe input"
    )

    # No downstream steps allowed
    forbidden = ["rag", "draft", "qa", "hil", "bullet"]
    assert not any(f in str(e).lower() for f in forbidden for e in events), (
        "Downstream agents executed despite unsafe input"
    )


# ---------------------------------------------------------------------
# 2. Invalid JD triggers Strategy guardrails and blocks RAG/Bullet/etc.
# ---------------------------------------------------------------------
@pytest.mark.routing
@pytest.mark.parametrize("bad_jd", [None, "", 0, [], {}])
def test_invalid_jd_blocks_strategy_and_downstream(bad_jd):
    out = run_workflow({"compat_mode": "v10_7", "resume": "Test Resume", "jd": bad_jd})

    assert out["status"] in {"blocked", "fail"}

    events = [str(e).lower() for e in out.get("events", [])]

    # Strategy must appear (attempted evaluation)
    assert any("strategy" in e for e in events), "Strategy did not run on invalid JD"

    # But downstream stacks MUST NOT run
    assert not any("rag" in e for e in events)
    assert not any("bullet" in e for e in events)
    assert not any("draft" in e for e in events)
    assert not any("qa" in e for e in events)
    assert not any("hil" in e for e in events)


# ---------------------------------------------------------------------
# 3. Raw Python exceptions must never leak
# ---------------------------------------------------------------------
@pytest.mark.routing
def test_no_stack_trace_leakage_on_bad_inputs():
    out = run_workflow({"compat_mode": "v10_7", "resume": ["bad", "format"], "jd": "AI Exec"})

    # All messages must be normalized
    serialized = str(out)
    assert not _contains_trace(serialized), (
        "Raw stack trace leaked into output. Envelope normalization failed."
    )

    assert out["status"] in {"fail", "blocked"}


# ---------------------------------------------------------------------
# 4. Downstream agents must NOT run after validation failure
# ---------------------------------------------------------------------
@pytest.mark.routing
def test_downstream_agents_never_run_after_safety_fail():
    out = run_workflow({"compat_mode": "v10_7", "resume": None, "jd": "AI Exec"})
    events = [str(e).lower() for e in out.get("events", [])]

    assert any("safety" in e for e in events), "No Safety event on malformed input"

    # Nothing past Strategy should run
    forbidden = ["rag", "bullet", "draft", "qa", "hil"]
    for f in forbidden:
        assert all(f not in e for e in events), (
            f"Forbidden downstream agent '{f}' executed after SafetyGuard failure"
        )


# ---------------------------------------------------------------------
# 5. Retry logic must NOT trigger on malformed input
# ---------------------------------------------------------------------
@pytest.mark.routing
@pytest.mark.parametrize("bad", [None, {}, {"jd": "AI"}, {"resume": "AI"}])
def test_retry_not_triggered_on_malformed_input(bad):
    # Fix shape if possible
    if isinstance(bad, dict):
        inp = {
            "compat_mode": "v10_7",
            "resume": bad.get("resume"),
            "jd": bad.get("jd"),
        }
    else:
        inp = {"compat_mode": "v10_7", "resume": bad, "jd": "AI Exec"}

    out = run_workflow(inp)
    events = [str(e).lower() for e in out.get("events", [])]

    assert not any("retry" in e for e in events), (
        "Retry loop incorrectly triggered on malformed input"
    )


# ---------------------------------------------------------------------
# 6. Invalid downstream data must short-circuit to fail/blocked status
# ---------------------------------------------------------------------
@pytest.mark.routing
def test_downstream_schema_violation_triggers_normalized_error():
    """
    Artificial scenario: 
    Some agents may return malformed downstream data under refactor
    (e.g., Drafting returns a non-dict). The system must normalize
    this to fail, not propagate a Python error.
    """
    out = run_workflow({"compat_mode": "v10_7", "resume": "BAD_DOWNSTREAM_SIM", "jd": "simulate-downstream-error"})

    # Workflow must not crash
    assert isinstance(out, dict), "Workflow crashed — returned no envelope"

    assert out["status"] in {"fail", "blocked"}, (
        f"Downstream schema violation must trigger fail/blocked, not {out['status']}"
    )

    # Must include structured error info
    serialized = str(out)
    assert "error" in serialized.lower() or "issues" in serialized.lower(), (
        "Downstream schema error did not propagate into structured envelope"
    )


# ---------------------------------------------------------------------
# 7. Invalid resume structure — must block early (no RAG)
# ---------------------------------------------------------------------
@pytest.mark.routing
@pytest.mark.parametrize("invalid_resume", [
    ["not", "valid"],
    123,
    0.5,
    {"some": "dict"},
])
def test_invalid_resume_blocks_before_rag(invalid_resume):
    out = run_workflow({"compat_mode": "v10_7", "resume": invalid_resume, "jd": "AI Exec"})
    events = [str(e).lower() for e in out.get("events", [])]

    # Should run Safety + maybe Strategy, but not RAG/Drafting/QA/HIL
    assert any("safety" in e for e in events)
    assert not any("rag" in e for e in events)
    assert not any("draft" in e for e in events)
    assert not any("qa" in e for e in events)
    assert not any("hil" in e for e in events)
