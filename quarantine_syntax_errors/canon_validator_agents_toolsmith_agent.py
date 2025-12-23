"""
ToolsmithAgent - Dynamic Tool Forger.
Creates diagnostic tools on-the-fly based on detected issues.
"""

import asyncio
import os
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from agentic_core..base import SubAtomicAgent


class ToolsmithAgent(SubAtomicAgent):
    """
    ROLE: Dynamic Tool Forger.
    Creates diagnostic tools on-the-fly based on detected issues.
    L5 Dynamic Agency - self-extends capabilities.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Forging Diagnostic Tools...")
        await asyncio.sleep(0)

        if not self.ctx.intelligence_enabled:
            print("   ⚠️  Intelligence disabled - skipping tool forging")
            return

        # Analyze current issues to determine what tools are needed
        needed_tools = self._analyze_needed_tools()

        if not needed_tools:
            print("   ✅ No diagnostic tools needed")
            return

        print(f"   🔧 Forging {len(needed_tools)} diagnostic tool(s)...")

        for tool_spec in needed_tools:
            await self._forge_tool(tool_spec)

    def _analyze_needed_tools(self) -> list:
        """Analyze current issues to determine what tools are needed."""
        needed = []

        # Check for recurring failures
        failures = [k for k, v in self.ctx.results.items() if not v.get('passed')]

        if len(failures) > 5:
            needed.append({
                'name': 'failure_analyzer',
                'purpose': 'Analyze patterns in recurring failures',
                'keys': failures[:10]
            })

        # Check for flapping files
        if self.ctx.flapping_files:
            needed.append({
                'name': 'flap_detector',
                'purpose': 'Detect and report flapping file patterns',
                'files': list(self.ctx.flapping_files)[:5]
            })

        return needed

    async def _forge_tool(self, tool_spec: dict):
        """Forge a diagnostic tool based on the specification."""
        tool_name = tool_spec['name']
        tool_purpose = tool_spec['purpose']

        print(f"   🔨 Forging: {tool_name}")

        prompt = f"""
Create a Python diagnostic tool for the following purpose:
Purpose: {tool_purpose}
Context: {tool_spec}

Requirements:
1. Single file, <100 lines
2. No external dependencies beyond stdlib
3. Clear output format
4. Include docstring explaining usage
5. Include if __name__ == '__main__' block

Return ONLY the Python code.
"""

        try:
            tool_code = await self.ctx.resilient_mutation(
                self.name, prompt, max_attempts=2
            )

            if tool_code:
                # Save the tool
                tool_dir = "scripts/diagnostic_tools"
                os.makedirs(tool_dir, exist_ok=True)

                timestamp = int(time.time())
                tool_path = os.path.join(tool_dir, f"{tool_name}_{timestamp}.py")

                if self.ctx.write_compliant_file(tool_path, tool_code):
                    print(f"   ✅ Forged: {tool_path}")

                    # Broadcast if streamer available
                    if self.ctx._streamer_initialized:
                        await self.ctx.broadcast(
                            f"Forged diagnostic tool: {tool_path}",
                            agent=self.name,
                            level="TOOL_CREATED"
                        )
                else:
                    print(f"   ❌ Failed to write tool (blocked by governor)")
        except Exception as e:
            print(f"   ❌ Failed to forge {tool_name}: {e}")
