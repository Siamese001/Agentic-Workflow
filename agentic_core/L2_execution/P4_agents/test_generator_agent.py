"""
Test Generator Agent - Automated Scaffolding (Key 47)
Scaffolds unit tests for newly moved or refactored L-layer logic.
"""
import os
from pathlib import Path
from typing import Any, Optional, Protocol, Dict, List
from agentic_core.canon_base_agent import CanonBaseAgent

class TestGeneratorAgent(CanonBaseAgent):
    """
    Validates Canon Key 47: QA & Telemetry.
    Ensures that every high-signal file has a corresponding test coverage path.
    """
    
    def get_validation_keys(self) -> List[int]:
        return [47]

    async def execute(self, file_path: str = None):
        """
        [L5 HARDENING] Scaffolding Loop.
        Detects if a file was moved or refactored and generates missing tests.
        """
        if not file_path:
            return False

        # 1. Detect Relocation or Refactor Events in the Mission Report
        relocation_event = any(
            "RELOCATED" in str(r.get('msg', '')) or "Refactored" in str(r.get('msg', ''))
            for r in self.ctx.report 
            if os.path.basename(file_path) in str(r.get('msg', ''))
        )

        if relocation_event:
            print(f"   [!] {self.name} detected shift in {os.path.basename(file_path)}. Verifying test coverage.")
            return await self._scaffold_unit_test(file_path)

        return False

    async def _scaffold_unit_test(self, source_path: str) -> bool:
        """
        Generates a unit test file in the canonical tests/ unit layer.
        """
        import void_compliance
        source_p = Path(source_path)
        
        # Determine target test path (e.g., tests/unit/agentic_core/L1_cognition/filename_test.py)
        # Using Depth 3 rule for tests
        test_dir = Path("tests/unit") / source_p.parent
        test_file = test_dir / f"{source_p.stem}_test.py"

        if test_file.exists():
            print(f"      [OK] Test coverage already exists at {test_file}")
            return True

        print(f"      [SIGNAL] Scaffolding missing test: {test_file}")
        
        # Read source code to inform test generation
        with open(source_path, 'r', encoding='utf-8') as f:
            source_code = f.read(5000)

        scaffold_prompt = f"""### ROLE: QA_ARCHITECT
### TASK: Generate a Pytest unit test for the following source file.
### SOURCE_PATH: {source_path}
### TARGET_PATH: {test_file}

REQUIREMENTS:
1. Use 'pytest' and 'pytest-asyncio'.
2. Use ABSOLUTE imports from the root (e.g., from agentic_core.L1_cognition.P1_core import ...).
3. Mock all external LLM or Redis calls.
4. Return ONLY the complete Python test code.

SOURCE PREVIEW:
{source_code}
"""
        test_code = await self.resilient_mutation(
            task=scaffold_prompt,
            code="# Placeholder for test code",
            file_path=str(test_file),
            round_num=1
        )

        # Physical Creation
        test_dir.mkdir(parents=True, exist_ok=True)
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        print(f"      [✓] SCAFFOLDED: {test_file}")
        return True