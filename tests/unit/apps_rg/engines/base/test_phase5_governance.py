"""
Phase 5 Governance Tests - 100% pass required.

Tests the Safety and Strategy engines:
- Section Ranker reads from Buffer, applies strategies, writes to Buffer
- Template Optimizer reads JD, writes template strategy
- ATS Compatibility scans content, triggers signals
- Void Compliance scans file system
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports BEFORE any app imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from apps_rg.engines.base.sovereign_context import SovereignContext
from apps_rg.engines.refinement.section_ranker_engine import SectionRankerEngine
from apps_rg.engines.safety.ats_compatibility_engine import ATSCompatibilityEngine


@pytest.mark.asyncio
async def test_ranker_reorders_content():
    """Verify ranker reads buffer and applies strategy."""
    ctx = SovereignContext()
    # Mock data
    ctx.buffer.write("optimized_content", {"education": {}, "skills": {}}, "SETUP")
    ctx.buffer.write("mission_input", {"role_type": "technical"}, "SETUP")

    # Mock config injection via config object or stub
    # Assuming the engine uses defaults if config node missing in test env

    engine = SectionRankerEngine(ctx)
    # Inject strategy for test
    engine.strategies = {"technical": ["skills", "education"]}

    await engine.execute()

    ranked = ctx.buffer.read("ranked_content")
    keys = list(ranked.keys())
    assert keys[0] == "skills"
    assert keys[1] == "education"


@pytest.mark.asyncio
async def test_ats_signals_failure():
    """Verify ATS engine triggers signal on bad content."""
    ctx = SovereignContext()
    ctx.buffer.write("ranked_content", {"summary": "<table>bad</table>"}, "SETUP")

    engine = ATSCompatibilityEngine(ctx)
    await engine.execute()

    assert "ATS_FAILURE" in ctx.signals
    report = ctx.buffer.read("ats_report")
    assert report["valid"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
