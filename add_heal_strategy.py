# Add heal() method to StrategyCoordinatorAgent
import re

with open("agentic_core/L3_orchestration/workflow_engines/DomainPlannerAgent.py") as f:
    content = f.read()

# Find the last return metrics in StrategyCoordinatorAgent
pattern = r"(class StrategyCoordinatorAgent.*?)(        return metrics\n)"
replacement = r'\1        return metrics\n\n    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:\n        """\n        Heal violations detected by StrategyCoordinatorAgent.\n        \n        Args:\n            violation: Dictionary containing violation details with keys:\n                - file: Path to the file with the violation\n                - type: Type of violation detected\n                - message: Description of the violation\n                \n        Returns:\n            Dictionary with keys:\n                - status: "success", "partial_success", "failed", or "skipped"\n                - details: Human-readable summary\n                - artifacts: List of modified files\n                - errors: List of error messages\n        """\n        file_path = violation.get("file") or violation.get("file_path")\n        violation_type = violation.get("type", "unknown")\n        \n        # Default implementation - StrategyCoordinatorAgent coordinates strategies\n        try:\n            return {\n                "status": "skipped",\n                "details": f"StrategyCoordinatorAgent heal() not yet implemented for {violation_type}",\n                "artifacts": [],\n                "errors": []\n            }\n        except Exception as e:\n            return {\n                "status": "failed",\n                "details": f"StrategyCoordinatorAgent heal() failed: {str(e)}",\n                "artifacts": [],\n                "errors": [str(e)]\n            }\n'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open("agentic_core/L3_orchestration/workflow_engines/DomainPlannerAgent.py", "w") as f:
    f.write(new_content)

print("Added heal() method to StrategyCoordinatorAgent")
