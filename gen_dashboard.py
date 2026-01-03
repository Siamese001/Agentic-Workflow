#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
AutonomyGuardianAgent(Path(__file__).parent).generate_compliance_report(markdown=True)
print("\n✅ Dashboard regenerated with professional polish!")
