#!/usr/bin/env python3
"""
Subatomic Canon Validator - L5 Autonomous Healing
Enforces 50 validation keys with AI-powered fixes.

Modular version - broken out from monolithic canon_validator_v2_agentic.py
"""

import argparse
import asyncio
import io
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from agentic_core.canon_orchestrator import IntelligentOrchestrator

load_dotenv()

print("DEBUG: VERSION 3.0 - MODULAR ARCHITECTURE - DECEMBER 19 2025")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canon Validator V3 - Modular Autonomous Healing")
    parser.add_argument("--target", type=str, help="Target directory (e.g., agentic_core, apps_rg)")
    parser.add_argument("--heal", action="store_true", help="Enable LLM-based autonomous healing")
    args = parser.parse_args()

    print("🤖 SUBATOMIC CANON VALIDATOR - LEVEL 5 AUTONOMOUS HEALING")
    if args.target:
        print(f"🎯 Target Scope: {args.target}")
    if args.heal:
        print("🧠 Healing Mode: ENABLED")
    else:
        print("🔍 Healing Mode: DISABLED (Audit Only)")
    print("=" * 60)
    
    orchestrator = IntelligentOrchestrator(target=args.target)
    asyncio.run(orchestrator.run_mission())
