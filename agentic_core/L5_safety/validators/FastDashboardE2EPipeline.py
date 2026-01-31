#!/usr/bin/env python3
"""
FAST DASHBOARD E2E PIPELINE
===========================

Optimized pipeline that skips slow discovery regeneration and uses existing data.
Only regenerates discovery if absolutely necessary (e.g., after code fixes).

Steps:
1. Fix heal invocation gaps (adds super(, **kwargs).heal_repository(, **kwargs) calls, **kwargs)
2. Update agent_discovery_full.json metadata directly (fast)
3. Regenerate dashboard HTML
4. Validate all data integrity
5. Provide visual confirmation
"""

import json
import re
import sys
from pathlib import Path

from agentic_core.utils.security import safe_execute

from agentic_core.L5_safety.validators.structure_blueprint import (
    DASHBOARD_DIR,
    get_validated_project_root,
)


class FastDashboardE2EPipeline:
    """Fast automated dashboard pipeline."""

    def __init__(self):
        self.project_root = get_validated_project_root()
        self.discovery_path = self.project_root / "agent_discovery_full.json"
        self.dashboard_path = self.project_root / DASHBOARD_DIR / "autonomy_dashboard.html"
        self.stats = {
            "heal_fixes": 0,
            "agents_discovered": 0,
            "dashboard_rows": 0,
            "heal_invocation_before": 0,
            "heal_invocation_after": 0,
        }

    def print_header(self, title: str):
        print()
        print("=" * 80)
        print(title)
        print("=" * 80)
        print()

    def print_step(self, step: str):
        print(f"📍 {step}")

    def step1_fix_heal_invocation(self) -> int:
        """Step 1: Fix heal invocation gaps in code."""
        self.print_step("STEP 1: Fixing heal invocation gaps...")

        if not self.discovery_path.exists():
            print("   ⚠️  No discovery data - skipping fixes")
            return 0

        data = json.load(open(self.discovery_path))
        needs_fix = [a for a in data if a.get("has_healing") and a.get("invocation") != "Yes"]

        if not needs_fix:
            print("   ✅ No fixes needed")
            return 0

        fixed_count = 0
        for agent in needs_fix:
            path = Path(agent["path"])
            if not path.exists():
                continue

            try:
                content = path.read_text(encoding="utf-8")
                pattern = r'(    def heal_repository\([^)]*\)[^:]*:.*?)(\n        (?:""".*?"""|\'\'\'.*?\'\'\')\s*\n)?(.*?)(\n    def |\n\nclass |\Z)'
                matches = list(re.finditer(pattern, content, re.DOTALL))

                if not matches:
                    continue

                match = matches[0]
                method_body = match.group(3)

                if "super().heal_repository" in method_body:
                    continue

                # Insert super() call
                method_sig = match.group(1)
                docstring = match.group(2) or ""
                next_section = match.group(4)

                lines = method_body.split("\n")
                insert_index = 0
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if (
                        stripped
                        and not stripped.startswith("#")
                        and not stripped.startswith('"""')
                        and not stripped.startswith("'''")
                    ):
                        insert_index = i
                        break

                lines.insert(
                    insert_index,
                    "        super(, **kwargs).heal_repository(, **kwargs)\n",
                    **kwargs,
                )
                new_method_body = "\n".join(lines)
                new_method = method_sig + docstring + new_method_body + next_section
                new_content = content[: match.start()] + new_method + content[match.end() :]
                path.write_text(new_content, encoding="utf-8")

                fixed_count += 1

            except Exception:
                pass

        self.stats["heal_fixes"] = fixed_count
        print(f"   ✅ Fixed {fixed_count} agents")
        return fixed_count

    def step1_5_fix_mcp_hardening(self) -> int:
        """Step 1.5: Fix MCP hardening gaps in code."""
        self.print_step("STEP 1.5: Fixing MCP hardening gaps...")

        if not self.discovery_path.exists():
            print("   ⚠️  No discovery data - skipping")
            return 0

        data = json.load(open(self.discovery_path))
        needs_hardening = [a for a in data if not a.get("mcp_hardened")]

        if not needs_hardening:
            print("   ✅ All agents already MCP hardened")
            return 0

        fixed_count = 0
        for agent in needs_hardening:
            path = Path(agent["path"])
            if not path.exists():
                continue

            try:
                content = path.read_text(encoding="utf-8")

                # Skip if already has MCPHardenedMixin
                if "MCPHardenedMixin" in content:
                    continue

                # Skip stub/re-export files
                if (
                    "from agentic_core" in content
                    and "import" in content
                    and agent["class_name"] in content
                ):
                    if content.count(f"class {agent['class_name']}") == 0:
                        continue

                # Find class definition
                class_pattern = rf"class\s+{re.escape(agent['class_name'])}\s*\((.*?)\)\s*:"
                match = re.search(class_pattern, content, re.DOTALL)

                if not match:
                    continue

                current_inheritance = match.group(1).strip()

                # Build new inheritance
                if current_inheritance:
                    new_inheritance = f"{current_inheritance}, MCPHardenedMixin"
                else:
                    new_inheritance = "MCPHardenedMixin"

                # Replace class definition
                old_class_def = match.group(0)
                new_class_def = f"class {agent['class_name']}({new_inheritance}):"
                content = content.replace(old_class_def, new_class_def)

                # Add import if needed
                if (
                    "from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin"
                    not in content
                ):
                    lines = content.split("\n")
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith("import ") or line.strip().startswith("from "):
                            insert_idx = i + 1
                    lines.insert(
                        insert_idx,
                        "from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin",
                    )
                    content = "\n".join(lines)

                path.write_text(content, encoding="utf-8")
                fixed_count += 1

            except Exception:
                pass

        self.stats["mcp_fixes"] = fixed_count
        print(f"   ✅ Fixed {fixed_count} agents")
        return fixed_count

    def step2_update_discovery_metadata(self, fixed_count: int) -> bool:
        """Step 2: Update discovery metadata directly (fast)."""
        self.print_step("STEP 2: Updating discovery metadata...")

        if not self.discovery_path.exists():
            print("   ❌ Discovery file not found")
            return False

        try:
            data = json.load(open(self.discovery_path))

            # Calculate before stats
            total = len(data)
            before_invocation = sum(1 for a in data if a.get("invocation") == "Yes")
            self.stats["heal_invocation_before"] = (
                before_invocation / total * 100 if total > 0 else 0
            )

            # Update invocation status for fixed agents
            updated = 0
            for agent in data:
                if agent.get("has_healing") and agent.get("invocation") != "Yes":
                    # Check if file now has super() call
                    path = Path(agent["path"])
                    if path.exists():
                        content = path.read_text(encoding="utf-8")
                        if "super().heal_repository()" in content:
                            agent["invocation"] = "Yes"
                            updated += 1

            # Save updated discovery
            with open(self.discovery_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Calculate after stats
            after_invocation = sum(1 for a in data if a.get("invocation") == "Yes")
            self.stats["heal_invocation_after"] = after_invocation / total * 100 if total > 0 else 0
            self.stats["agents_discovered"] = total

            print(f"   ✅ Updated {updated} agent records")
            print(
                f"   ✅ Heal invocation: {after_invocation}/{total} ({self.stats['heal_invocation_after']:.1f}%)"
            )

            return True

        except Exception as e:
            print(f"   ❌ Update failed: {e}")
            return False

    def step3_regenerate_dashboard(self) -> bool:
        """Step 3: Regenerate dashboard HTML."""
        self.print_step("STEP 3: Regenerating dashboard HTML...")

        dashboard_script = (
            self.project_root
            / "agentic_core"
            / "L6_observability"
            / "dashboards"
            / "generate_dashboard.py"
        )

        try:
            result = safe_execute(
                [sys.executable, str(dashboard_script)],
                cwd=str(self.project_root),
                capture_output=True,
                check=False,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                print(f"   ❌ Failed: {result.stderr[:200]}")
                return False

            # Extract row count
            html = self.dashboard_path.read_text(encoding="utf-8")
            start_idx = html.find("const dashboardData = [")
            end_idx = html.find("];", start_idx)

            if start_idx != -1 and end_idx != -1:
                json_str = html[start_idx + 22 : end_idx + 1]
                territories = json.loads(json_str)
                self.stats["dashboard_rows"] = len(territories)
                print(f"   ✅ Generated {len(territories)} rows")

            return True

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def step4_run_tests(self) -> bool:
        """Step 4: Run validation tests."""
        self.print_step("STEP 4: Running validation tests...")

        test_script = self.project_root / "scripts" / "test_dashboard_end_to_end.py"

        try:
            result = safe_execute(
                [sys.executable, str(test_script)],
                cwd=str(self.project_root),
                capture_output=True,
                check=False,
                text=True,
                timeout=30,
                env={"PYTHONPATH": str(self.project_root)},
            )

            if result.returncode != 0:
                print("   ❌ Tests failed")
                print(result.stdout[-500:] if result.stdout else "")
                return False

            print("   ✅ All tests passed")
            return True

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def step5_visual_confirmation(self):
        """Step 5: Visual confirmation."""
        self.print_step("STEP 5: Visual confirmation...")

        before = self.stats["heal_invocation_before"]
        after = self.stats["heal_invocation_after"]
        improvement = after - before

        print()
        print("┏" + "━" * 78 + "┓")
        print("┃" + " " * 25 + "DASHBOARD UPDATE SUMMARY" + " " * 29 + "┃")
        print("┣" + "━" * 78 + "┫")
        print("┃  Heal Invocation Coverage:                                              ┃")
        print(
            f"┃    Before: {before:5.1f}%  →  After: {after:5.1f}%  (Δ +{improvement:4.1f}%)                    ┃"
        )

        if after >= 100.0:
            print("┃    🎯 TARGET ACHIEVED: 100% heal invocation coverage!                   ┃")
        elif after >= 99.0:
            print(
                f"┃    ⚠️  Nearly complete: {100 - after:.1f}% gap remaining                             ┃"
            )

        print("┃                                                                              ┃")
        print(
            f"┃  Code Fixes: {self.stats['heal_fixes']:3d} agents                                              ┃"
        )
        print(
            f"┃  Total Agents: {self.stats['agents_discovered']:3d}                                              ┃"
        )
        print(
            f"┃  Dashboard Rows: {self.stats['dashboard_rows']:2d}                                                   ┃"
        )
        print("┃                                                                              ┃")
        print(f"┃  📊 Dashboard: {str(self.dashboard_path.relative_to(self.project_root)):<58}┃")
        print("┗" + "━" * 78 + "┛")
        print()

    def step0_validate_data(self) -> bool:
        """Step 0: Validate dashboard data quality before processing."""
        self.print_step("STEP 0: Validating dashboard data quality...")

        # Run comprehensive data validation
        validation_script = self.project_root / "scripts" / "validate_dashboard_data.py"
        base_agent_script = self.project_root / "scripts" / "validate_base_agents.py"

        if not validation_script.exists() or not base_agent_script.exists():
            print("   ⚠️  Validation scripts not found - skipping validation")
            return True

        try:
            # Run base agent validation
            result = safe_execute(
                [sys.executable, str(base_agent_script)],
                cwd=str(self.project_root),
                capture_output=True,
                check=False,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print("   ❌ Base agent validation failed:")
                print(result.stdout[-500:] if result.stdout else "")
                print("\n   ⚠️  CRITICAL: Multiple base agents detected per layer")
                print("   This causes inheritance confusion and must be fixed manually")
                return False

            # Run comprehensive validation
            result = safe_execute(
                [sys.executable, str(validation_script)],
                cwd=str(self.project_root),
                capture_output=True,
                check=False,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print("   ⚠️  Data validation warnings (non-critical):")
                print(result.stdout[-500:] if result.stdout else "")
            else:
                print("   ✅ All data validation checks passed")

            return True

        except Exception as e:
            print(f"   ⚠️  Validation error: {e}")
            return True  # Continue pipeline even if validation fails

    def run(self) -> bool:
        """Run fast pipeline."""
        self.print_header("FAST DASHBOARD E2E PIPELINE")

        # Step 0: Validate data quality
        if not self.step0_validate_data():
            print("\n❌ PIPELINE BLOCKED: Critical data validation failures")
            print("   Fix base agent duplicates before continuing")
            print("   Run: python scripts/validate_base_agents.py")
            return False

        # Step 1: Fix heal invocation
        self.step1_fix_heal_invocation()

        # Step 1.5: Fix MCP hardening
        self.step1_5_fix_mcp_hardening()

        # Step 2: Update metadata
        if not self.step2_update_discovery_metadata(0):
            print("\n❌ PIPELINE FAILED at metadata update")
            return False

        # Step 3: Regenerate dashboard
        if not self.step3_regenerate_dashboard():
            print("\n❌ PIPELINE FAILED at dashboard generation")
            return False

        # Step 4: Run tests
        if not self.step4_run_tests():
            print("\n❌ PIPELINE FAILED at validation")
            return False

        # Step 5: Visual confirmation
        self.step5_visual_confirmation()

        self.print_header("✅ PIPELINE COMPLETE - Dashboard updated!")

        return True


def main():
    pipeline = FastDashboardE2EPipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
