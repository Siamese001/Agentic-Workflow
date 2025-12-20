```python
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Fixed: %(message% -> %(message)s
logger = logging.getLogger("ActionNode")


class ActionNode:
    """
    The 'Hands' of the Agent.
    Responsibility: Execute the Cognitive Node's plan safely.
    Security: STRICT WHITELIST of allowed tools.
    """

    # Class-level constants for tool mapping and command blacklisting
    # These improve readability and maintainability.
    TOOL_MAP: Dict[str, str] = {
        "write_file": "write_file",
        "create_file": "write_file",
        "read_file": "read_file",
        "read": "read_file",
        "list_files": "list_files",
        "ls": "list_files",
        "run_command": "run_command",
        "execute": "run_command"
    }

    # WARNING: This blacklist is for demonstration purposes only.
    # A robust production system would require a much more sophisticated
    # sandboxing mechanism (e.g., Docker, gVisor, firejail) for `run_command`.
    BLACKLIST_COMMANDS: List[str] = ["rm -rf", "sudo", "format", "> /dev/sda", "mkfs"]

    def __init__(self, work_dir: str = "./workspace"):
        """
        Initializes the ActionNode with a specified working directory.

        Args:
            work_dir (str): The path to the workspace directory.
        """
        self.work_dir: Path = Path(work_dir).resolve()
        self.allowed_tools: Dict[str, Any] = {
            "write_file": self._tool_write_file,
            "read_file": self._tool_read_file,
            "list_files": self._tool_list_files,
            "run_command": self._tool_run_command  # Use with extreme caution!
        }

        # Ensure workspace exists
        if not self.work_dir.exists():
            logger.info(f"Creating workspace directory: {self.work_dir}")
            self.work_dir.mkdir(parents=True)
        else:
            logger.info(f"Using existing workspace directory: {self.work_dir}")

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a full plan sequence from the Cognitive Node.

        Args:
            plan (Dict[str, Any]): A dictionary representing the plan,
                                   expected to contain 'goal' and 'steps'.

        Returns:
            Dict[str, Any]: A dictionary containing the overall status and results
                            of each executed step.
        """
        logger.info(f"⚙️ Action Node received plan for goal: {plan.get('goal', 'N/A')}")

        results: List[Dict[str, Any]] = []
        # Attempt to get steps from 'steps' key, or nested 'plan.steps'
        steps: List[Dict[str, Any]] = plan.get('steps') or plan.get('plan', {}).get('steps', [])

        if not steps:
            logger.warning("⚠️ Received empty plan. No actions taken.")
            return {"status": "skipped", "results": []}

        for step in steps:
            result = self._execute_single_step(step)
            results.append(result)

            # Stop execution if a critical step fails
            if result.get('status') == 'error':
                logger.error(f"🛑 Execution halted at step {step.get('step', 'N/A')}: {result.get('output')}")
                return {"status": "failed", "results": results}

        logger.info("✅ Plan execution completed successfully.")
        return {"status": "success", "results": results}

    def _execute_single_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses a single step, validates the tool, and executes it.

        Args:
            step (Dict[str, Any]): A dictionary representing a single action step,
                                   expected to contain 'action' and 'params'.

        Returns:
            Dict[str, Any]: A dictionary containing the step number, status, and output.
        """
        action_name: str = step.get('action', '').lower().replace(" ", "_")
        params: Dict[str, Any] = step.get('params', {})
        step_number: Union[int, str] = step.get('step', 'N/A')

        tool_key: Union[str, None] = self.TOOL_MAP.get(action_name)

        if not tool_key or tool_key not in self.allowed_tools:
            # Fixed: Wrapped long string for PEP8 line length
            msg = (
                f"🚫 Tool '{action_name}' (mapped to '{tool_key}') is NOT "
                "whitelisted or recognized."
            )
            logger.warning(msg)
            return {"step": step_number, "status": "blocked", "output": msg}

        logger.info(f"🔨 Executing Tool '{tool_key}' for step {step_number} with params: {params}")

        try:
            # Execute the tool function
            output: str = self.allowed_tools[tool_key](**params)
            return {"step": step_number, "status": "success", "output": output}
        except Exception as e:
            logger.error(f"❌ Tool '{tool_key}' execution failed for step {step_number}: {e}", exc_info=True)
            return {"step": step_number, "status": "error", "output": str(e)}

    # =========================================================================
    # 🔧 SECURE TOOL IMPLEMENTATIONS
    # =========================================================================

    def _safe_path(self, filename: str) -> Path:
        """
        Security: Prevents Directory Traversal (e.g. ../../etc/passwd).
        Ensures that any path accessed is strictly within the designated workspace.

        Args:
            filename (str): The filename or path relative to the workspace.

        Returns:
            Path: The resolved, safe absolute path within the workspace.

        Raises:
            ValueError: If the path attempts to escape the workspace directory.
        """
        target: Path = (self.work_dir / filename).resolve()
        if not str(target).startswith(str(self.work_dir)):
            # Fixed: Wrapped long string for PEP8 line length
            raise ValueError(
                f"SECURITY VIOLATION: Path '{filename}' attempts to escape workspace. "
                f"Resolved path: '{target}' is outside '{self.work_dir}'."
            )
        return target

    def _tool_write_file(self, filename: str, content: str) -> str:
        """
        Writes content to a file within the workspace.

        Args:
            filename (str): The name of the file to write.
            content (str): The content to write into the file.

        Returns:
            str: A success message.
        """
        target: Path = self._safe_path(filename)
        # Ensure parent directories exist
        target.parent.mkdir(parents=True, exist_ok=True)

        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"File '{target.name}' written successfully.")
        return f"File written successfully: {target.name}"

    def _tool_read_file(self, filename: str) -> str:
        """
        Reads content from a file within the workspace.

        Args:
            filename (str): The name of the file to read.

        Returns:
            str: The content of the file, or an error message if the file does not exist.
        """
        target: Path = self._safe_path(filename)
        if not target.exists():
            logger.warning(f"Attempted to read non-existent file: {filename}")
            return f"Error: File '{filename}' does not exist."
        if not target.is_file():
            logger.warning(f"Attempted to read a non-file path: {filename}")
            return f"Error: Path '{filename}' is not a file."

        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"File '{target.name}' read successfully.")
        return content

    def _tool_list_files(self, subdir: str = ".") -> str:
        """
        Lists files and directories within a specified subdirectory of the workspace.

        Args:
            subdir (str): The subdirectory to list files from, relative to the workspace.
                          Defaults to the root of the workspace.

        Returns:
            str: A newline-separated string of file/directory names, or an error message.
        """
        target: Path = self._safe_path(subdir)
        if not target.exists():
            logger.warning(f"Attempted to list non-existent directory: {subdir}")
            return f"Error: Directory '{subdir}' not found."
        if not target.is_dir():
            logger.warning(f"Attempted to list a non-directory path: {subdir}")
            return f"Error: Path '{subdir}' is not a directory."

        files: List[str] = [f.name for f in target.iterdir()]
        output = "\n".join(files) if files else "(empty directory)"
        logger.info(f"Listed files in '{subdir}':\n{output}")
        return output

    def _tool_run_command(self, command: str) -> str:
        """
        Executes a shell command within the workspace.
        WARNING: This tool is highly dangerous. In a production environment,
        it MUST be wrapped in a secure, isolated execution environment (e.g., Docker).

        Args:
            command (str): The shell command string to execute.

        Returns:
            str: The stdout of the command if successful, or an error message.

        Raises:
            ValueError: If the command contains blacklisted patterns.
        """
        # Simple blacklist for demonstration
        if any(b in command for b in self.BLACKLIST_COMMANDS):
            logger.error(f"SECURITY VIOLATION: Command '{command}' contains blacklisted patterns.")
            # Fixed: Wrapped long string for PEP8 line length
            raise ValueError(
                "SECURITY VIOLATION: Command contains blacklisted patterns. "
                "Refusing to execute."
            )

        logger.warning(f"Executing potentially dangerous command: '{command}' in '{self.work_dir}'")
        try:
            # Run inside workspace
            result = subprocess.run(
                command,
                shell=True,  # shell=True is dangerous, prefer list of args if possible
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=10,  # Timeout to prevent hanging commands
                check=False  # Do not raise CalledProcessError for non-zero exit codes
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Command executed successfully. Output: {output or '(no output)'}")
                return output or "(success, no output)"
            else:
                error_output = result.stderr.strip()
                logger.error(f"Command failed with exit code {result.returncode}. Error: {error_output}")
                return f"Command Failed (Exit Code {result.returncode}):\n{error_output}"
        except subprocess.TimeoutExpired:
            logger.error(f"Command '{command}' timed out after 10 seconds.")
            return "Error: Command timed out."
        except Exception as e:
            logger.error(f"An unexpected error occurred during command execution: {e}", exc_info=True)
            return f"Error: An unexpected error occurred: {str(e)}"


if __name__ == "__main__":
    # TEST HARNESS
    test_workspace_dir = "./test_workspace"
    action_node = ActionNode(work_dir=test_workspace_dir)

    # 1. Simulate a plan from Cognitive Node
    mock_plan = {
        "goal": "Demonstrate basic file operations and command execution",
        "steps": [
            {
                "step": 1,
                "action": "write_file",
                "params": {"filename": "test_file.txt", "content": "Hello from ActionNode!"}
            },
            {
                "step": 2,
                "action": "list_files",
                "params": {"subdir": "."}
            },
            {
                "step": 3,
                "action": "read_file",
                "params": {"filename": "test_file.txt"}
            },
            {
                "step": 4,
                "action": "run_command",
                "params": {"command": "echo 'This is a test command.' > command_output.txt"}
            },
            {
                "step": 5,
                "action": "read_file",
                "params": {"filename": "command_output.txt"}
            },
            {
                "step": 6,
                "action": "list_files",
                "params": {"subdir": "."}
            },
            {
                "step": 7,
                "action": "run_command",
                "params": {"command": "ls -l"}
            },
            {
                "step": 8,
                "action": "read_file",
                "params": {"filename": "non_existent_file.txt"} # This should fail
            },
            {
                "step": 9,
                "action": "unknown_tool", # This should be blocked
                "params": {}
            },
            {
                "step": 10,
                "action": "run_command",
                "params": {"command": "rm -rf /"} # This should be blocked by blacklist
            }
        ]
    }

    print("\n--- Executing Mock Plan ---")
    report = action_node.execute_plan(mock_plan)
    print("\n--- Plan Execution Report ---")
    import json
    print(json.dumps(report, indent=2))

    # Clean up test workspace
    print(f"\n--- Cleaning up test workspace: {test_workspace_dir} ---")
    import shutil
    if Path(test_workspace_dir).exists():
        shutil.rmtree(test_workspace_dir)
        print(f"Removed {test_workspace_dir}")
    else:
        print(f"Workspace {test_workspace_dir} already removed or never created.")

```