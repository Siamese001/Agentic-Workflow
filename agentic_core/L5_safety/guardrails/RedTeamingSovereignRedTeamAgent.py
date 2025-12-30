"""
SovereignRedTeamAgent - Eternal Adversarial Tester for L5 Shield
"""
import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List
import redis

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


class RedTeamingSovereignRedTeamAgent:
    """
    Sovereign red team — tests shield integrity via controlled drift injection.
    """

    def __init__(self, project_root: Path):
        self.root = project_root
        try:
            self.redis = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), decode_responses=True)
            self.redis.ping()
        except Exception as e:
            print(f'Warning: Redis connection failed ({e}), using in-memory cache')
            self.redis = None
            self._attack_log = {}
        self.test_dir = project_root / 'agentic_core/L5_safety/red_teaming/artifacts'
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def _inject_depth_violation(self):
        """Infects the core with a shallow file (Depth 3)."""
        bad_file = self.root / 'agentic_core/L5_safety/redteam_probe.py'
        bad_file.write_text('# REDTEAM: Depth Violation Test\npass')
        return bad_file

    def _inject_gravity_violation(self):
        """Creates a file that violates the gravity import law."""
        gravity_probe = self.test_dir / 'gravity_probe.py'
        content = 'import apps_rg.core.logic\n# REDTEAM: Gravity Violation Test'
        gravity_probe.write_text(content)
        return gravity_probe

    def run_tests(self) -> Any:
        """Launches a random adversarial probe."""
        probes: Any = [self._inject_depth_violation, self._inject_gravity_violation]
        attack: Any = random.choice(probes)
        target: Any = attack()
        print(f'   [REDTEAM] Adversarial probe injected: {target.name}')
        if self.redis:
            self.redis.set(f'redteam:last_attack:{target.name}', 'active', ex=300)
        else:
            self._attack_log[f'redteam:last_attack:{target.name}'] = 'active'
        return str(target)

    async def execute(self, ctx: Any) -> Any:
        """Standard execution hook."""
        if random.random() < 0.1:
            result: Any = self.run_tests()
            ctx.report('RedTeam', 1, True, f'Injected adversarial probe: {result}')
        else:
            self.cleanup()
            ctx.report('RedTeam', 0, True, 'Shield test skipped; artifacts purged.')

    def cleanup(self) -> Any:
        """Purges test files after the Shield has (hopefully) archived them."""
        for f in self.test_dir.glob('*.py'):
            f.unlink()
        redteam_probe: Any = self.root / 'agentic_core/L5_safety/redteam_probe.py'
        if redteam_probe.exists():
            redteam_probe.unlink()
        print('   [OK] RedTeam artifacts cleaned.')
