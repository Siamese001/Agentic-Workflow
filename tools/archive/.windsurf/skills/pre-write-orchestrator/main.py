#!/usr/bin/env python3
"""
Windsurf Skill: Pre-Write Orchestrator
Unified pre-write validation orchestrator with dependency resolution.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for skill orchestration
# guardian: allow-magic-configuration -- Skill configuration and dependency resolution


class SkillResult:
    """Result of a skill validation."""

    def __init__(self, skill_name: str, success: bool, issues: list[str], duration: float):
        self.skill_name = skill_name
        self.success = success
        self.issues = issues
        self.duration = duration


class PreWriteOrchestrator:
    """Orchestrates all pre-write validation skills."""

    def __init__(self):
        self.skills_dir = Path(".windsurf/skills")
        self.skill_registry = self._load_skill_registry()
        self.dependency_graph = self._build_dependency_graph()

    def _load_skill_registry(self) -> dict[str, dict]:
        """Load all available skills and their metadata."""
        registry = {}

        # Core consolidated skills
        consolidated_skills = [
            "artifact-management",
            "boundary-enforcement",
            "graph-analysis",
            "operational-gates",
            "testing-framework",
        ]

        # Standalone skills
        standalone_skills = [
            "dedup-guard",
            "redis-hitl-gate",
            "script-sprawl-guard",
            # Phase 2 critical gap skills
            "powershell-guard",
            "repair-gate-validator",
            "agent-deletion-guard",
            "hitl-decision-validator",
            "guardian-exemption-validator",
        ]

        all_skills = consolidated_skills + standalone_skills

        for skill_name in all_skills:
            skill_path = self.skills_dir / skill_name
            if skill_path.exists():
                registry[skill_name] = {
                    "path": skill_path,
                    "main": skill_path / "main.py",
                    "config": skill_path / "skill.yaml",
                    "category": "consolidated" if skill_name in consolidated_skills else "standalone",
                }

        return registry

    def _build_dependency_graph(self) -> dict[str, list[str]]:
        """Build skill dependency graph."""
        return {
            "pre-write-orchestrator": [],  # Root orchestrator
            "graph-analysis": [],
            "artifact-management": ["graph-analysis"],
            "boundary-enforcement": ["graph-analysis"],
            "testing-framework": ["graph-analysis"],
            "operational-gates": ["artifact-management"],
            "dedup-guard": ["graph-analysis"],
            "powershell-guard": [],
            "repair-gate-validator": ["graph-analysis", "artifact-management"],
            "agent-deletion-guard": [],
            "hitl-decision-validator": [],
            "guardian-exemption-validator": [],
            "redis-hitl-gate": [],
            "script-sprawl-guard": ["graph-analysis"],
        }

    def _get_execution_order(self, skills_to_run: list[str]) -> list[str]:
        """Get topological order for skill execution."""
        visited = set()
        temp_visited = set()
        order = []

        def visit(skill: str):
            if skill in temp_visited:
                raise ValueError(f"Circular dependency detected involving {skill}")
            if skill in visited:
                return

            temp_visited.add(skill)
            for dep in self.dependency_graph.get(skill, []):
                if dep in skills_to_run:
                    visit(dep)
            temp_visited.remove(skill)
            visited.add(skill)
            order.append(skill)

        for skill in skills_to_run:
            if skill not in visited:
                visit(skill)

        return order

    def _run_skill(self, skill_name: str, file_path: str, operation: str, context: str) -> SkillResult:
        """Run a single skill validation."""
        if skill_name not in self.skill_registry:
            return SkillResult(skill_name, False, [f"Skill {skill_name} not found"], 0.0)

        skill_info = self.skill_registry[skill_name]
        main_script = skill_info["main"]

        if not main_script.exists():
            return SkillResult(skill_name, False, [f"Main script not found for {skill_name}"], 0.0)

        start_time = time.time()

        try:
            # Prepare arguments based on skill type
            if skill_name == "powershell-guard":
                cmd = ["python", str(main_script), context or "", file_path]
            elif skill_name == "repair-gate-validator":
                cmd = ["python", str(main_script), file_path, operation]
            elif skill_name == "agent-deletion-guard":
                cmd = ["python", str(main_script), file_path]
            elif skill_name == "hitl-decision-validator":
                cmd = ["python", str(main_script), context or "2", file_path]
            elif skill_name == "guardian-exemption-validator":
                cmd = ["python", str(main_script), context or "", file_path]
            else:
                # Generic skill call
                cmd = ["python", str(main_script), file_path, operation, context or ""]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=Path.cwd())

            duration = time.time() - start_time

            if result.returncode == 0:
                return SkillResult(skill_name, True, [], duration)
            else:
                issues = [result.stderr.strip() or result.stdout.strip() or "Skill failed"]
                return SkillResult(skill_name, False, issues, duration)

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return SkillResult(skill_name, False, ["Skill execution timed out"], duration)
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            duration = time.time() - start_time
            return SkillResult(skill_name, False, [f"Error running skill: {e}"], duration)

    def _determine_relevant_skills(self, file_path: str, operation: str, context: str) -> list[str]:
        """Determine which skills are relevant for this operation."""
        relevant_skills = ["pre-write-orchestrator"]  # Always include orchestrator

        # Always run core validation skills
        relevant_skills.extend(["graph-analysis", "artifact-management", "operational-gates"])

        # Operation-specific skills
        if operation in ["write", "edit"]:
            relevant_skills.extend(
                ["boundary-enforcement", "testing-framework", "dedup-guard", "script-sprawl-guard"],
            )

            # Phase 2 critical gap skills
            if context and "powershell" in context.lower():
                relevant_skills.append("powershell-guard")

            if operation == "edit":
                relevant_skills.append("repair-gate-validator")

            if file_path.endswith("Agent.py"):
                relevant_skills.append("agent-deletion-guard")

            if context and "hitl" in context.lower():
                relevant_skills.append("hitl-decision-validator")

            if context and "guardian" in context.lower():
                relevant_skills.append("guardian-exemption-validator")

        # File-type specific skills
        if file_path.endswith(".py"):
            relevant_skills.extend(["boundary-enforcement", "testing-framework"])

        return list(set(relevant_skills))  # Remove duplicates

    def validate_pre_write(
        self,
        file_path: str,
        operation: str,
        context: str = "",
    ) -> tuple[bool, list[SkillResult]]:
        """Run comprehensive pre-write validation."""
        print(f"🚀 Starting pre-write validation for {operation} on {file_path}")

        # Determine relevant skills
        relevant_skills = self._determine_relevant_skills(file_path, operation, context)
        print(f"📋 Skills to run: {', '.join(relevant_skills)}")

        # Get execution order
        try:
            execution_order = self._get_execution_order(relevant_skills)
            print(f"📊 Execution order: {' → '.join(execution_order)}")
        except ValueError as e:
            return False, [SkillResult("orchestrator", False, [str(e)], 0.0)]

        # Run skills in order
        results = []
        total_start = time.time()

        for skill_name in execution_order:
            if skill_name == "pre-write-orchestrator":
                continue  # Skip self

            print(f"⚡ Running {skill_name}...", end=" ")
            result = self._run_skill(skill_name, file_path, operation, context)
            results.append(result)

            if result.success:
                print(f"✅ ({result.duration:.2f}s)")
            else:
                print(f"❌ ({result.duration:.2f}s)")
                for issue in result.issues:
                    print(f"   - {issue}")

                # Fail fast on critical failures
                if skill_name in ["repair-gate-validator", "agent-deletion-guard"]:
                    break

        total_duration = time.time() - total_start

        # Summary
        successful = sum(1 for r in results if r.success)
        total = len(results)

        print("\n📊 Validation Summary:")
        print(f"   Skills run: {total}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {total - successful}")
        print(f"   Total time: {total_duration:.2f}s")

        all_success = all(r.success for r in results)

        if all_success:
            print("✅ All validations passed - operation allowed")
        else:
            print("❌ Some validations failed - operation blocked")

        return all_success, results

    def generate_status_report(self) -> dict:
        """Generate skill status report."""
        report = {
            "timestamp": time.time(),
            "total_skills": len(self.skill_registry),
            "skill_status": {},
            "dependency_graph": self.dependency_graph,
        }

        for skill_name, skill_info in self.skill_registry.items():
            report["skill_status"][skill_name] = {
                "exists": skill_info["main"].exists(),
                "category": skill_info["category"],
                "dependencies": self.dependency_graph.get(skill_name, []),
            }

        return report


def main():
    """Main entry point for the orchestrator."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path> <operation> [context]")
        print("Operations: write, edit, delete")
        sys.exit(1)

    # Health check
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] Pre-write orchestrator health check")
        sys.exit(0)

    file_path = sys.argv[1]
    operation = sys.argv[2]
    context = sys.argv[3] if len(sys.argv) > 3 else ""

    orchestrator = PreWriteOrchestrator()

    # Special commands
    if operation == "status":
        report = orchestrator.generate_status_report()
        print(json.dumps(report, indent=2))
        sys.exit(0)

    # Health check
    if operation == "--health-check":
        print("[PASS] Pre-write orchestrator health check")
        sys.exit(0)

    # Run validation
    success, results = orchestrator.validate_pre_write(file_path, operation, context)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
