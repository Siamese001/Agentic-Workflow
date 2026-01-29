"""
Phase 3 Data Flow Tests - 100% pass required.

Tests the Sovereign Data Flow pattern:
- HOP1 reads from Buffer, writes to Buffer
- HOP2 reads HOP1 output from Buffer, writes to Buffer
- Orchestrator manages the flow without passing data directly
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports BEFORE any app imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from apps_rg.engines.base.sovereign_context import SovereignContext
from apps_rg.engines.hops.hop1_clerk_engine import ClerkExtractionEngine
from apps_rg.engines.hops.hop2_enrichment_engine import DataEnrichmentEngine
from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine


@pytest.mark.asyncio
async def test_hop1_reads_from_buffer():
    """Verify HOP1 fails if buffer is empty, succeeds if populated."""
    ctx = SovereignContext()
    # Don't write mission_input yet

    clerk = ClerkExtractionEngine(ctx)
    with pytest.raises(ValueError, match="Buffer missing mission_input"):
        await clerk.execute()

    # Now write input
    mock_resume = {"experience": []}
    ctx.buffer.write("mission_input", {"master_resume": mock_resume}, "TEST_SETUP")

    result = await clerk.execute()
    assert "experience_sections" in result

    # Verify Write
    saved = ctx.buffer.read("hop1_extraction")
    assert saved is not None


@pytest.mark.asyncio
async def test_hop2_chaining():
    """Verify HOP2 reads HOP1's output from buffer."""
    ctx = SovereignContext()

    # Simulate HOP1 output existing
    hop1_out = {"experience_sections": [{"bullets": [{"bullet_text": "Managed stuff"}]}]}
    ctx.buffer.write("hop1_extraction", hop1_out, "HOP1_MOCK")

    enricher = DataEnrichmentEngine(ctx)
    result = await enricher.execute()

    assert "enrichment_metadata" in result
    assert ctx.buffer.read("hop2_enrichment") is not None


@pytest.mark.asyncio
async def test_orchestrator_end_to_end_flow():
    """Verify the General drives the data flow correctly."""
    ctx = SovereignContext()
    # Inject master resume into context wrapper as expected by Orchestrator init
    ctx.master_resume = {"experience": [{"company": "A", "bullets": ["Did A"]}]}

    orch = ResumeOrchestratorEngine(ctx)
    result = await orch.execute("Job Description")

    assert result["status"] == "success"
    assert "HOP-1" in result["checkpoints"]
    assert "HOP-2" in result["checkpoints"]

    # Verify Trace
    summary = ctx.trace.get_summary()
    assert summary["completed"] >= 2  # HOP1 + HOP2 (Orchestrator span might be open still)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
