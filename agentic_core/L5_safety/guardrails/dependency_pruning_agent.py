#!/usr/bin/env python3
"""
Dependency Pruning Agent
Batch agent: Detects and removes unused Python dependencies from requirements.txt.
Uses 'deptry' for accurate unused detection via AST analysis.
"""
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List


class DependencyPruningAgent:
    """
    Batch agent: Detects and removes unused Python dependencies from requirements.txt.
    Uses 'deptry' for accurate unused detection.
    """

    def __init__(self, project_root: Path, ctx):
        self.project_root = Path(project_root)
        self.ctx = ctx
        self.dry_run = True  # Safety: Default to non-destructive
        self.requirements_path = self.project_root / "requirements.txt"

    def _find_unused_deptry(self) -> List[str]:
        """Use deptry to find unused dependencies via AST analysis."""
        try:
            # Run deptry in JSON mode for reliable parsing
            result = subprocess.run(
                ["deptry", ".", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("unused", [])
        except FileNotFoundError:
            # deptry not installed
            pass
        except Exception:
            # JSON parsing or other error
            pass
        return []

    def _remove_from_requirements_txt(self, unused: List[str]) -> Dict:
        """Remove unused packages from requirements.txt."""
        if not self.requirements_path.exists():
            return {"removed": 0}

        content = self.requirements_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        new_lines = []
        removed = 0

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("#"):
                new_lines.append(line)
                continue

            # Regex to capture package name before any version specifiers
            match = re.match(r"^([a-zA-Z0-9_-]+)", line_stripped)
            if match and match.group(1).lower() in [u.lower() for u in unused]:
                removed += 1
                if self.dry_run:
                    # Comment out instead of removing (dry run)
                    new_lines.append(f"# [PRUNED UNUSED] {line}")
                else:
                    # Skip writing this line (actually remove)
                    continue
            else:
                new_lines.append(line)

        if removed > 0 and not self.dry_run:
            self.requirements_path.write_text(
                "\n".join(new_lines) + "\n", encoding="utf-8"
            )

        return {"removed": removed, "file": "requirements.txt"}

    async def execute(self) -> Dict:
        """Scan for and optionally remove unused dependencies."""
        print("   [PRUNE] Scanning for unused dependencies...")
        unused = self._find_unused_deptry()

        if not unused:
            print("   [✓] No unused dependencies detected")
            return {"unused_found": 0, "removed": 0}

        print(
            f"   [!] Found {len(unused)} potentially unused packages: {', '.join(unused[:5])}"
        )
        if len(unused) > 5:
            print(f"       ... and {len(unused) - 5} more")

        result = self._remove_from_requirements_txt(unused)

        return {
            "unused_found": len(unused),
            "removed": result["removed"],
            "dry_run": self.dry_run,
        }
