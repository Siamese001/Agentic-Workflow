#!/usr/bin/env python3
"""
Resume Generation Script
Loads your actual JD and resume data to generate a customized resume.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))  # guardian: allow-global-mutation

from apps_rg.engines.resume_orchestrator_engine import ResumeOrchestratorEngine
from apps_rg.types.SovereignContext import SovereignContext

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
Logger = logging.getLogger("RESUME_GENERATOR")


def load_data_file(filename: str) -> dict:
    """Load data from JSON file in the same directory."""
    file_path = Path(__file__).parent / filename
    if not file_path.exists():
        Logger.error(f"❌ File not found: {file_path}")
        Logger.info(f"Please create {filename} with your data")
        sys.exit(1)

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


async def main():
    Logger.info("🎯 RESUME GENERATION STARTED...")
    start_time = datetime.now()

    # Load your actual data
    jd_data = load_data_file("job_description.json")
    resume_data = load_data_file("your_resume_updated.json")

    # 1. Initialize Context
    ctx = SovereignContext()
    ctx.master_resume = resume_data

    # 2. Boot Orchestrator
    Logger.info("⚡ Processing your resume against the job description...")
    orchestrator = ResumeOrchestratorEngine(ctx)

    # 3. Generate Customized Resume
    try:
        result = await orchestrator.execute(jd_data["description"])

        Logger.info("-" * 50)
        Logger.info(f"🏁 GENERATION COMPLETE in {(datetime.now() - start_time).total_seconds():.2f}s")
        Logger.info(f"STATUS: {result.get('status')}")
        Logger.info(f"QUALITY SCORE: {result.get('final_quality_score', 0)}")
        Logger.info(f"ATS COMPATIBLE: {result.get('ats_valid', False)}")

        # 4. Save Generated Resume
        Logger.info("-" * 50)
        Logger.info("💾 Saving generated resume...")

        # Get the final ranked content
        final_resume = ctx.buffer.read("ranked_content", {})

        # Save to file
        output_file = f"generated_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = Path(__file__).parent / output_file

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_resume, f, indent=2, ensure_ascii=False)

        Logger.info(f"✅ Resume saved to: {output_file}")

        # Show preview
        if final_resume:
            Logger.info("-" * 50)
            Logger.info("📋 RESUME PREVIEW:")
            for section, content in final_resume.items():
                if isinstance(content, list) and content:
                    Logger.info(f"  {section}: {len(content)} items")
                elif isinstance(content, dict):
                    Logger.info(f"  {section}: {list(content.keys())}")
                else:
                    Logger.info(f"  {section}: {content}")

    except Exception as e:
        Logger.error(f"❌ Generation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
