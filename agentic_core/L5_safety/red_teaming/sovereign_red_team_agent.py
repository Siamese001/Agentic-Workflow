#!/usr/bin/env python3
"""
SovereignRedTeamAgent - Eternal Adversarial Tester for L5 Shield
"""

import json
import os
from pathlib import Path
from typing import List, Dict

import random
import redis

class SovereignRedTeamAgent:
    """
    Sovereign red team — tests shield integrity via controlled drift injection.
    """
    def __init__(self, project_root: Path):
        self.root = project_root
        
        # Direct Redis connection for testing
        try:
            self.redis = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
        except Exception as e:
            print(f"Warning: Redis connection failed ({e}), using in-memory cache")
            self.redis = None
            self._attack_log = {}
        
        self.test_dir = project_root / "agentic_core/L5_safety/red_teaming/artifacts"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def _inject_depth_violation(self):
        """Infects the core with a shallow file (Depth 3)."""
        bad_file = self.root / "agentic_core/L5_safety/redteam_probe.py"
        bad_file.write_text("# REDTEAM: Depth Violation Test\npass")
        return bad_file

    def _inject_gravity_violation(self):
        """Creates a file that violates the gravity import law."""
        gravity_probe = self.test_dir / "gravity_probe.py"
        # Importing from a downstream app into the core is a major Gravity breach
        content = "import apps_rg.core.logic\n# REDTEAM: Gravity Violation Test"
        gravity_probe.write_text(content)
        return gravity_probe

    def run_tests(self):
        """Launches a random adversarial probe."""
        probes = [self._inject_depth_violation, self._inject_gravity_violation]
        attack = random.choice(probes)
        target = attack()
        
        print(f"   [REDTEAM] Adversarial probe injected: {target.name}")
        # Log the attack in Redis so the Forensics agent knows it was us
        if self.redis:
            self.redis.set(f"redteam:last_attack:{target.name}", "active", ex=300)
        else:
            self._attack_log[f"redteam:last_attack:{target.name}"] = "active"
        return str(target)

    async def execute(self, ctx):
        """Standard execution hook."""
        # 10% chance to run a stress test on any given validator cycle
        if random.random() < 0.10:
            result = self.run_tests()
            ctx.report("RedTeam", 1, True, f"Injected adversarial probe: {result}")
        else:
            # Clean up old artifacts from previous runs
            self.cleanup()
            ctx.report("RedTeam", 0, True, "Shield test skipped; artifacts purged.")

    def cleanup(self):
        """Purges test files after the Shield has (hopefully) archived them."""
        for f in self.test_dir.glob("*.py"):
            f.unlink()
        
        # Also clean up the redteam probe if it exists
        redteam_probe = self.root / "agentic_core/L5_safety/redteam_probe.py"
        if redteam_probe.exists():
            redteam_probe.unlink()
            
        print("   [OK] RedTeam artifacts cleaned.")
