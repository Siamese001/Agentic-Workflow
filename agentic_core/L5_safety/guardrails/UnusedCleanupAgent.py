#!/usr/bin/env python3
"""
Unused Cleanup Agent
Atomic agent: Removes unused imports and variables using autoflake.
"""
import subprocess
from pathlib import Path


class UnusedCleanupAgent:
    """
    Atomic agent: Removes unused imports and variables using autoflake.
    """

    def __init__(self, project_root, ctx):
        self.project_root = Path(project_root)
        self.ctx = ctx

    async def execute(self, file_path: str):
        """Remove unused imports and variables from a single file."""
        file = Path(file_path)
        if not file.exists():
            return {"healed": False}

        try:
            # Autoflake removes unused imports/variables in place
            result = subprocess.run(
                [
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    str(file),
                ],
                capture_output=True,
                text=True,
            )

            # Check if file changed (autoflake returns 0 on success)
            if result.returncode == 0:
                # Assume success if return code is 0
                # To confirm 'healed', we rely on git diff or hash check in main loop
                return {"healed": True, "action": "unused_removed"}

        except FileNotFoundError:
            if hasattr(self.ctx, "report"):
                self.ctx.report("UnusedCleanupAgent", 0, False, "autoflake not installed")
        except Exception as e:
            if hasattr(self.ctx, "report"):
                self.ctx.report("UnusedCleanupAgent", 0, False, str(e))

        return {"healed": False}
