"""
Grand Unification Tests - 100% pass required for deployment.

Comprehensive system integration tests that verify the Sovereign architecture
functions as a cohesive organism.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports BEFORE any app imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from apps_rg.engines.base.sovereign_context import SovereignContext
from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine

# 🛡️ MANDATORY: 100% Test Pass Rate Required for Deployment


@pytest.mark.asyncio
async def test_full_system_lifecycle_happy_path():
    """
    INTEGRATION TEST 1: The 'Happy Path'.
    Verifies that a valid input flows through all 5 HOPs and produces a ranked artifact.
    """
    ctx = SovereignContext()
    ctx.master_resume = {
        "experience": [{"company": "TestCorp", "bullets": ["Managed $1M budget"]}],
        "education": [],
        "skills": ["Python"],
    }

    orch = ResumeOrchestratorEngine(ctx)
    result = await orch.run("Senior Engineer Job Description")

    # Verification
    assert result["status"] in ["SUCCESS", "WARNING"], "Orchestrator failed to produce valid status"

    # Verify HOP Sequence
    checkpoints = result["checkpoints"]
    expected_hops = ["HOP-1", "HOP-2", "HOP-3-K9", "HOP-4-RANK", "HOP-5-ATS"]
    for hop in expected_hops:
        assert hop in checkpoints, f"Missing critical checkpoint: {hop}"

    # Verify Final Artifact
    final = ctx.buffer.read("ranked_content")
    assert final is not None, "Final ranked content is missing from Buffer"
    assert "experience" in final, "Final content missing experience section"


@pytest.mark.asyncio
async def test_resilience_to_garbage_input():
    """
    INTEGRATION TEST 2: System Resilience.
    Verifies that the system handles malformed data without crashing (Graceful Degradation).
    """
    ctx = SovereignContext()
    ctx.master_resume = {}  # EMPTY RESUME

    orch = ResumeOrchestratorEngine(ctx)

    # Should not raise exception, but return failure/warning status
    try:
        result = await orch.run("Job")
        # Logic: If resume is empty, Clerk might fail, but Orchestrator handles it
        # We expect it to eventually fail or return partial
    except Exception:
        pytest.fail("Orchestrator crashed on empty input instead of handling gracefully")

    # Verify Signal was fired
    # We expect DATA_MISSING or similar
    # (Checking signals set logic requires tracing context updates)
    assert len(ctx.trace.get_summary()["failures"]) > 0 or result["status"] == "WARNING"


@pytest.mark.asyncio
async def test_buffer_cryptography_and_lineage():
    """
    INTEGRATION TEST 3: Data Lineage.
    Verifies that every major write to the buffer is attributed to the correct agent.
    """
    ctx = SovereignContext()
    ctx.master_resume = {"experience": []}

    orch = ResumeOrchestratorEngine(ctx)
    await orch.run("Job")

    history = ctx.buffer.get_history()

    # Verify Specific Attributions
    writers = {tx.key: tx.source_agent for tx in history}

    assert writers.get("hop1_extraction") == "ClerkExtractionEngine"
    assert writers.get("hop2_enrichment") == "DataEnrichmentEngine"
    assert writers.get("ranked_content") == "SectionRankerEngine"


@pytest.mark.asyncio
async def test_telemetry_fidelity_check():
    """
    INTEGRATION TEST 4: Observability.
    Ensures that spans are being recorded for every engine execution.
    """
    ctx = SovereignContext()
    ctx.master_resume = {"experience": []}

    orch = ResumeOrchestratorEngine(ctx)
    await orch.run("Job")

    summary = ctx.trace.get_summary()

    # We expect at least 6 spans (Orch + 5 HOPs)
    assert summary["total_spans"] >= 6, (
        f"Telemetry gap detected. Only found {summary['total_spans']} spans."
    )
    assert summary["completed"] == summary["total_spans"], (
        "Orphaned spans detected (did not close)."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
