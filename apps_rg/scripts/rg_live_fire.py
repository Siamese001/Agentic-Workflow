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

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from apps_rg.engines.resume_orchestrator_engine import ResumeOrchestratorEngine
from apps_rg.types.SovereignContext import SovereignContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
Logger = logging.getLogger("LIVE_FIRE")
MOCK_JD = "\n[Your Job Description Here]\nExample: Senior Software Engineer at TechCorp\nRequirements: Python, AWS, React, 5+ years experience...\n"
MOCK_RESUME = {
    "contact_info": {"name": "Your Name", "email": "your.email@example.com"},
    "experience": [
        {
            "company": "Previous Company",
            "title": "Your Previous Role",
            "bullets": ["Your achievement 1 with metrics", "Your achievement 2 with metrics"],
        }
    ],
    "education": [{"degree": "Your Degree", "school": "Your University"}],
    "skills": ["skill1", "skill2", "skill3"],
}


async def main():
    Logger.info("🔥 INITIATING SOVEREIGN LIVE FIRE EXERCISE...")
    start_time = datetime.now()
    ctx = SovereignContext()
    ctx.master_resume = MOCK_RESUME
    Logger.info("⚡ Booting L3 Orchestrator...")
    orchestrator = ResumeOrchestratorEngine(ctx)
    try:
        result = await orchestrator.execute(MOCK_JD)
        Logger.info("-" * 50)
        Logger.info(f"🏁 MISSION COMPLETE in {(datetime.now() - start_time).total_seconds():.2f}s")
        Logger.info(f"STATUS: {result.get('status')}")
        Logger.info(f"CHECKPOINTS: {result.get('checkpoints')}")
        Logger.info("-" * 50)
        Logger.info("🔍 DEEP BUFFER INSPECTION:")
        hop1 = ctx.buffer.read("hop1_extraction")
        if hop1:
            metrics = hop1["experience_sections"][0]["bullets"][0].get("quantified_metrics", [])
            Logger.info(f"✅ HOP-1 Metrics Extracted: {metrics}")
        else:
            Logger.error("❌ HOP-1 FAILED: No extraction data.")
        hop2 = ctx.buffer.read("hop2_enrichment")
        if hop2:
            Logger.info("✅ HOP-2 Enrichment found.")
        else:
            Logger.error("❌ HOP-2 FAILED.")
        k9 = ctx.buffer.read("k9_competencies")
        Logger.info(f"✅ HOP-3 K9 Competencies: {(len(k9) if k9 else 0)}/6")
        ranked = ctx.buffer.read("ranked_content")
        if ranked:
            Logger.info(f"✅ HOP-4 Ranked Sections: {list(ranked.keys())}")
        else:
            Logger.error("❌ HOP-4 FAILED.")
        ats_report = ctx.buffer.read("ats_report", {"valid": False})
        if ats_report.get("valid"):
            Logger.info("✅ HOP-5 ATS Status: Valid")
        else:
            Logger.error("❌ HOP-5 ATS FAILED")
        summary = ctx.trace.get_summary()
        Logger.info(f"📊 TELEMETRY: {summary['total_spans']} Spans Recorded. Failures: {summary['failures']}")
    except Exception as e:
        raise
        Logger.critical(f"❌ SYSTEM CRASH: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
