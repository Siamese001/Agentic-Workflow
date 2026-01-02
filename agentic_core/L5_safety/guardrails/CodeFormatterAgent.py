from __future__ import annotations
#!/usr/bin/env python3
"""
Code Formatter Agent
Atomic agent: Enforces consistent formatting using Black + Ruff auto-fix.
"""
import subprocess
from pathlib import Path
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


class CodeFormatterAgent(HealerMixin, MCPHardenedMixin):
    """
    Atomic agent: Enforces consistent formatting using Black + Ruff auto-fix.
    """

    def __init__(self, project_root, ctx):
        self.project_root = Path(project_root)
        self.ctx = ctx

    async def execute(self, file_path: str):
        """Format a single file using Black and Ruff."""
        file = Path(file_path)
        if not file.exists():
            return {"healed": False}

        changed = False
        try:
            # Black formatting
            black_result = subprocess.run(
                ["black", "--quiet", str(file)], capture_output=True, text=True
            )
            if black_result.returncode == 0 and "reformatted" in black_result.stderr:
                changed = True

            # Ruff lint auto-fix
            ruff_result = subprocess.run(
                ["ruff", "check", "--fix", "--quiet", str(file)], capture_output=True
            )
            if ruff_result.returncode == 0:
                # Ruff ran successfully, assume it enforced standards
                pass

            if changed:
                return {"healed": True, "action": "formatted"}

        except FileNotFoundError as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report(
                    "CodeFormatterAgent", 0, False, f"Tool Missing: {e.filename}"
                )
        except Exception as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report("CodeFormatterAgent", 0, False, f"Format error: {e}")

        return {"healed": changed}
