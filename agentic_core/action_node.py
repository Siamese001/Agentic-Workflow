import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ActionNode")


class ActionNode:
    """
    The 'Hands' of the Agent.
    Responsibility: Execute the Cognitive Node's plan safely.
    Security: STRICT WHITELIST of allowed tools.
    """

    def __init__(self, work_dir: str = "./workspace"):
        self.work_dir = Path(work_dir).resolve()
        self.allowed_tools = {
            "write_file": self._tool_write_file,
            "read_file": self._tool_read_file,
            "list_files": self._tool_list_files,
            "run_command": self._tool_run_command  # Use with caution!
        }

        # Ensure workspace exists
        if not self.work_dir.exists():
            self.work_dir.mkdir(parents=True)

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a full plan sequence from the Cognitive Node.
        """
        logger.info(f"⚙️ Action Node received plan: {plan.get('goal')}")

        results = []
        steps = plan.get('steps') or plan.get('plan', {}).get('steps', [])

        if not steps:
            logger.warning("⚠️ Received empty plan. No actions taken.")
            return {"status": "skipped", "results": []}

        for step in steps:
            result = self._execute_single_step(step)
            results.append(result)

            # Stop execution if a critical step fails
            if result['status'] == 'error':
                logger.error(f"🛑 Execution halted at step {step.get('step')}")
                return {"status": "failed", "results": results}

        return {"status": "success", "results": results}

    def _execute_single_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses a step, validates the tool, and executes it.
        """
        action_name = step.get('action').lower().replace(" ", "_")
        # Assuming the Cognitive Node formats params correctly
        params = step.get('params', {})

        # MAPPING: Map descriptive action names to tool functions
        # This handles LLM variability (e.g. "Write File" vs "write_file")
        tool_map = {
            "write_file": "write_file",
            "create_file": "write_file",
            "read_file": "read_file",
            "read": "read_file",
            "list_files": "list_files",
            "ls": "list_files",
            "run_command": "run_command",
            "execute": "run_command"
        }

        tool_key = tool_map.get(action_name)

        if not tool_key or tool_key not in self.allowed_tools:
            msg = f"🚫 Tool '{action_name}' is NOT whitelisted."
            logger.warning(msg)
            return {"step": step.get('step'), "status": "blocked", "output": msg}

        logger.info(f"🔨 Executing Tool: {tool_key}")

        try:
            # Execute the tool function
            output = self.allowed_tools[tool_key](**params)
            return {"step": step.get('step'), "status": "success", "output": output}
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            return {"step": step.get('step'), "status": "error", "output": str(e)}

    # =========================================================================
    # 🔧 SECURE TOOL IMPLEMENTATIONS
    # =========================================================================

    def _safe_path(self, filename: str) -> Path:
        """Security: Prevents Directory Traversal (e.g. ../../etc/passwd)"""
        target = (self.work_dir / filename).resolve()
        if not str(target).startswith(str(self.work_dir)):
            raise ValueError(
                f"SECURITY VIOLATION: Path '{filename}' attempts to escape workspace.")
        return target

    def _tool_write_file(self, filename: str, content: str) -> str:
        target = self._safe_path(filename)
        # Ensure parent dirs exist
        target.parent.mkdir(parents=True, exist_ok=True)

        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"File written successfully: {target.name}"

    def _tool_read_file(self, filename: str) -> str:
        target = self._safe_path(filename)
        if not target.exists():
            return f"Error: File {filename} does not exist."

        with open(target, 'r', encoding='utf-8') as f:
            return f.read()

    def _tool_list_files(self, subdir: str = ".") -> str:
        target = self._safe_path(subdir)
        if not target.exists():
            return "Directory not found."

        files = [f.name for f in target.glob("*")]
        return "\n".join(files) if files else "(empty directory)"

    def _tool_run_command(self, command: str) -> str:
        """
        Executes a shell command.
        WARNING: Highly dangerous. In production, wrap this in a Docker container.
        """
        # Simple blacklist for demonstration
        blacklist = ["rm -rf", "sudo", "format", "> /dev/sda"]
        if any(b in command for b in blacklist):
            raise ValueError(
                "SECURITY VIOLATION: Command contains blacklisted patterns.")

        try:
            # Run inside workspace
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip() or "(success, no output)"
            else:
                return f"Command Failed:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out."


if __name__ == "__main__":
    # TEST HARNESS
    action_node = ActionNode(work_dir="./test_workspace")

    # 1. Simulate a plan from Cognitive Node
    mock_plan = {
        "goal": "Create a secure environment",
        "steps": [
            {
                "step": 1,
                "action": "write_file",
                "params": {"filename": "security.txt", "content": "Security Level: Maximum"}
            },
            {
                "step": 2,
                "action": "ls",
                "params": {"subdir": "."}
            },
            {
                "step": 3,
                "action": "read_file",
                "params": {"filename": "security.txt"}
            }
        ]
    }

    report = action_node.execute_plan(mock_plan)