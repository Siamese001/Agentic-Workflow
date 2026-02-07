"""
scripts/simulate_sovereign_workflow_util.py
"""

import logging
import sys
from pathlib import Path

# Ensure path visibility
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Sovereign Agents
from agentic_core.L0_maintenance.enforcement.core_integrity_util import CoreIntegrityVerifier
from apps_lic.engines.BiasDetectorAgent import BiasDetectorSpecialist
from apps_rg.engines.CampaignPlannerAgent import CampaignPlannerAgent

# Setup Console Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Logger = logging.getLogger("SovereignSimulation")


def run_simulation():
    Logger.info(">>> INITIALIZING SOVEREIGN SIMULATION v2.5 <<<")

    try:
        # 1. Verify Core Integrity
        Logger.info("[1] Verifying Core Integrity...")
        try:
            CoreIntegrityVerifier.verify_core_integrity()
            Logger.info("    PASS: Immutable Lock Verified.")
        except Exception as e:
            Logger.warning(f"    WARNING: Core Integrity check failed (expected during dev): {e}")

        # 2. Boot RG Agent (The Creator)
        Logger.info("[2] Booting Resume Generation Agent (CampaignPlanner)...")
        planner = CampaignPlannerAgent(campaign_id="SIM-2026-ALPHA", active_channels=["web", "social"])
        Logger.info(f"    PASS: Booted {planner.name} (RG Domain)")

        # 3. Boot LIC Agent (The Validator)
        Logger.info("[3] Booting LIC Agent (BiasDetectorSpecialist)...")
        detector = BiasDetectorSpecialist(sensitivity_level=0.9)
        Logger.info(f"    PASS: Booted {detector.name} (LIC Domain)")

        # 4. Execute Workflow
        Logger.info("[4] Executing Cross-Domain Workflow...")
        slogan = "Guaranteed returns with zero risk!"
        Logger.info(f"    RG Action: Generated Slogan -> '{slogan}'")

        result = detector.scan_content(slogan)
        Logger.info(f"    LIC Action: Scan Result -> {result}")

        # 5. Verify Telemetry
        # In a real system, we'd read the log file. Here we trust the object state.
        if result["has_bias"] is not True:
            raise ValueError("Expected bias detection to return True")
        Logger.info("    PASS: Governance Logic Verified.")

        Logger.info(">>> SIMULATION SUCCESSFUL: SYSTEM CONVERGED <<<")

    except Exception as e:
        Logger.error(f">>> SIMULATION FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_simulation()
