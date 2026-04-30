"""W9 — anti-overfit detector hook on apps_rg orchestrator.

Tests `ResumeOrchestratorEngine._run_anti_overfit_check` directly so we don't
depend on the full orchestrator execution path. Three cases:

  * clean resume + clean JD              -> warning=False, escalate=False
  * resume with fabricated past claims   -> escalate=True
  * resume tailored heavily to JD        -> not escalated (mimicry alone is
                                            below hard-floor; warns only if
                                            aggregate score >= 2.0)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.engines.resume_orchestrator_engine import ResumeOrchestratorEngine  # noqa: E402


# --- helpers ---------------------------------------------------------------


class _StubLogger:
    def warning(self, *args, **kwargs):  # pragma: no cover - logger pass-through
        pass

    def error(self, *args, **kwargs):  # pragma: no cover
        pass

    def info(self, *args, **kwargs):  # pragma: no cover
        pass


@pytest.fixture(name="orchestrator")
def _orchestrator_fixture():
    """Build an orchestrator instance bypassing __init__ side effects."""
    inst = ResumeOrchestratorEngine.__new__(ResumeOrchestratorEngine)
    inst.logger = _StubLogger()
    return inst


# --- cases -----------------------------------------------------------------


def test_clean_resume_passes_anti_overfit(orchestrator):
    """Clean resume + neutral JD: no flags fire."""
    artifact = {
        "headline": "Senior Engineer",
        "summary": "Builds reliable backend systems.",
        "experience": [
            {"company": "Acme", "title": "Engineer", "bullets": ["Shipped service A.", "Cut latency by 30%."]}
        ],
        "skills": ["Python", "PostgreSQL"],
    }
    jd = "Looking for a backend engineer with cloud experience."
    block = orchestrator._run_anti_overfit_check(artifact, jd)

    assert block["escalate"] is False
    assert block["warning"] is False
    assert "fake_history_detected" not in block["flags"]
    assert "forced_warmth_detected" not in block["flags"]


def test_fabricated_history_escalates(orchestrator):
    """First-person past-interaction claim with no memory pointer triggers fake_history."""
    artifact = {
        "headline": "Engineer",
        "summary": "As we discussed last week, I led the migration. We talked about this before, and I delivered as promised.",
        "experience": [
            {"company": "Acme", "title": "Engineer", "bullets": ["Did things."]}
        ],
        "skills": [],
    }
    jd = "Generic engineering role description."
    block = orchestrator._run_anti_overfit_check(artifact, jd)

    # The hard-flag must fire directly (`fake_history_detected`) AND the
    # orchestrator hook MUST escalate when this flag is present.
    assert "fake_history_detected" in block["flags"]
    assert block["escalate"] is True


def test_mimicry_alone_does_not_escalate(orchestrator):
    """Heavy resume-to-JD tailoring should not escalate. The whole point of
    apps_rg is to align resume keywords to the JD; mimicry_max is calibrated
    to 0.85 to allow this. Hard-floor escalation requires a real signal
    like fake_history or forced_warmth, not just keyword overlap."""
    jd = (
        "Senior Vice President of Agentic Transformation. We are looking for "
        "a leader to drive enterprise AI agents, autonomous workflows, and "
        "decision-layer automation across Fortune 1000 clients."
    )
    artifact = {
        "headline": "Senior Vice President of Agentic Transformation",
        "summary": (
            "Leader driving enterprise AI agents, autonomous workflows, and "
            "decision-layer automation across Fortune 1000 clients."
        ),
        "experience": [
            {
                "company": "Acme",
                "title": "Director",
                "bullets": ["Led agentic transformation programs.", "Drove decision-layer automation."],
            }
        ],
        "skills": ["Enterprise AI", "Agentic Workflows", "Fortune 1000 Strategy"],
    }
    block = orchestrator._run_anti_overfit_check(artifact, jd)

    assert block["escalate"] is False
    # mimicry_breach may or may not appear (depends on string overlap), but
    # it must NOT cause an escalation.
    assert "fake_history_detected" not in block["flags"]


def test_block_contract_shape(orchestrator):
    """The returned block carries the expected keys for downstream wiring."""
    artifact = {"headline": "x", "summary": "y", "experience": [], "skills": []}
    block = orchestrator._run_anti_overfit_check(artifact, "z")

    for key in ("score", "flags", "warning", "escalate"):
        assert key in block, f"missing key {key} in overfit block"
    assert isinstance(block["score"], float)
    assert isinstance(block["flags"], list)
    assert isinstance(block["warning"], bool)
    assert isinstance(block["escalate"], bool)
