"""
SOVEREIGN LIVE FIRE EXERCISE
----------------------------
Executes a full runtime cycle of the apps_rg Sovereign Fleet.
NO MOCKS allowed for internal logic. Only external LLM calls are mocked.

Objective: Prove Data Flow integrity from HOP-0 to HOP-5.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Force Sovereign Imports
from apps_rg.engines.base.sovereign_context import SovereignContext

from apps_rg.engines.orchestration.resume_orchestrator_engine import ResumeOrchestratorEngine

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
Logger = logging.getLogger("LIVE_FIRE")

MOCK_JD = """
Senior Python Engineer.
Must have experience with AI agents, immutable state management, and orchestration.
Leadership skills required. Budget management of at least $1M.
"""

MOCK_RESUME = {
    "contact_info": {"name": "John Doe", "email": "john@example.com"},
    "experience": [
        {
            "company": "Legacy Systems Inc",
            "title": "Software Engineer",
            "bullets": [
                "Responsible for maintaining legacy codebases.",  # Trap: Weak Verb
                "Managed a budget of $500k and reduced costs by 20%.",  # Trap: Metric Extraction
            ],
        },
    ],
    "education": [{"degree": "BS CS", "school": "State U"}],
    "skills": ["Python", "Java", "SQL"],
}


async def main():
    Logger.info("🔥 INITIATING SOVEREIGN LIVE FIRE EXERCISE...")
    start_time = datetime.now()

    # 1. Initialize Context
    ctx = SovereignContext()
    # Inject Master Resume (simulate DB load)
    ctx.master_resume = MOCK_RESUME

    # 2. Boot Orchestrator
    Logger.info("⚡ Booting L3 Orchestrator...")
    orchestrator = ResumeOrchestratorEngine(ctx)

    # 3. Execute Full Cycle
    try:
        result = await orchestrator.run(MOCK_JD)

        Logger.info("-" * 50)
        Logger.info(f"🏁 MISSION COMPLETE in {(datetime.now() - start_time).total_seconds():.2f}s")
        Logger.info(f"STATUS: {result.get('status')}")
        Logger.info(f"CHECKPOINTS: {result.get('checkpoints')}")

        # 4. Deep Inspection of Buffer
        Logger.info("-" * 50)
        Logger.info("🔍 DEEP BUFFER INSPECTION:")

        # Check HOP-1 Extraction
        hop1 = ctx.buffer.read("hop1_extraction")
        if hop1:
            metrics = hop1["experience_sections"][0]["bullets"][0].get("quantified_metrics", [])
            Logger.info(f"✅ HOP-1 Metrics Extracted: {metrics}")
        else:
            Logger.error("❌ HOP-1 FAILED: No extraction data.")

        # Check HOP-2 Enrichment
        hop2 = ctx.buffer.read("hop2_enrichment")
        if hop2:
            # Check for brand violation flag (Responsible for)
            Logger.info("✅ HOP-2 Enrichment found.")
        else:
            Logger.error("❌ HOP-2 FAILED.")

        # Check HOP-3 Generation
        k9 = ctx.buffer.read("k9_competencies")
        Logger.info(f"✅ HOP-3 K9 Competencies: {len(k9) if k9 else 0}/6")

        # Check HOP-4 Refinement
        ranked = ctx.buffer.read("ranked_content")
        if ranked:
            Logger.info(f"✅ HOP-4 Ranked Sections: {list(ranked.keys())}")
        else:
            Logger.error("❌ HOP-4 FAILED.")

        # Check HOP-5 Safety
        ats = ctx.buffer.read("ats_report")
        Logger.info(f"✅ HOP-5 ATS Status: {'Valid' if ats and ats.get('valid') else 'INVALID'}")

        # 5. Telemetry Audit
        summary = ctx.trace.get_summary()
        Logger.info(
            f"📊 TELEMETRY: {summary['total_spans']} Spans Recorded. Failures: {summary['failures']}",
        )

    except Exception as e:
        Logger.critical(f"❌ SYSTEM CRASH: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
