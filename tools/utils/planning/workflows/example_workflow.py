"""
Example Integration of Token Estimator into Planning Workflow

This example shows how to integrate the ContextWindowEstimator into a typical
planning workflow that executes multiple phases and waves.
"""

import logging
from pathlib import Path
from typing import Any

from tools.utils.planning.preflight_hook import PlanningPreflightHook, TokenBudgetExceededError
from tools.utils.planning.token_estimator import ContextWindowEstimator, TokenBudget

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenAwarePlanningWorkflow:
    """
    Example planning workflow with integrated token budget management.

    This demonstrates how to wrap planning steps with token budget enforcement
    and maintain visibility into token usage across the entire workflow.
    """

    def __init__(self, budget_file: Path | None = None, custom_budget: TokenBudget | None = None):
        """
        Initialize the token-aware planning workflow.

        Args:
            budget_file: Path to budget history file
            custom_budget: Custom token budget configuration
        """
        self.preflight_hook = PlanningPreflightHook(
            estimator=ContextWindowEstimator(budget=custom_budget),
            budget_file=budget_file,
        )

        # Workflow state
        self.current_phase = None
        self.current_wave = None
        self.step_results = []

    def execute_phase(self, phase_name: str, waves: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Execute a complete phase with multiple waves.

        Args:
            phase_name: Name of the phase
            waves: List of wave configurations

        Returns:
            Phase execution summary with token budget information
        """
        logger.info(f"Starting phase: {phase_name}")
        self.current_phase = phase_name

        phase_results = {
            "phase": phase_name,
            "waves": [],
            "total_tokens": 0,
            "budget_violations": 0,
            "compression_events": 0,
        }

        for wave_config in waves:
            wave_name = wave_config["name"]
            logger.info(f"Executing wave: {wave_name}")

            try:
                wave_result = self.execute_wave(wave_name, wave_config)
                phase_results["waves"].append(wave_result)
                phase_results["total_tokens"] += wave_result["total_tokens"]

                if wave_result["budget_status"] == "red":
                    phase_results["budget_violations"] += 1

                if wave_result["compression_applied"]:
                    phase_results["compression_events"] += 1

            except TokenBudgetExceededError as e:
                logger.error(f"Wave {wave_name} failed due to token budget: {e}")
                phase_results["budget_violations"] += 1
                wave_result = {
                    "wave": wave_name,
                    "status": "failed",
                    "error": str(e),
                    "total_tokens": 0,
                }
                phase_results["waves"].append(wave_result)
                break  # Stop phase on budget failure

        # Log phase summary
        self._log_phase_summary(phase_results)

        return phase_results

    def execute_wave(self, wave_name: str, wave_config: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a single wave with multiple steps.

        Args:
            wave_name: Name of the wave
            wave_config: Wave configuration including steps

        Returns:
            Wave execution summary with token budget information
        """
        self.current_wave = wave_name

        wave_results = {
            "wave": wave_name,
            "steps": [],
            "total_tokens": 0,
            "budget_status": "green",
            "compression_applied": False,
        }

        for step_config in wave_config["steps"]:
            step_name = step_config["name"]
            step_type = step_config["type"]

            logger.info(f"Executing step: {step_name} ({step_type})")

            try:
                step_result = self.execute_step(step_name, step_type, step_config)
                wave_results["steps"].append(step_result)
                wave_results["total_tokens"] += step_result["estimated_tokens"]

                # Update wave budget status
                if step_result["budget_status"] == "red":
                    wave_results["budget_status"] = "red"
                elif step_result["budget_status"] == "yellow" and wave_results["budget_status"] == "green":
                    wave_results["budget_status"] = "yellow"

                if step_result["compression_applied"]:
                    wave_results["compression_applied"] = True

            except TokenBudgetExceededError as e:
                logger.error(f"Step {step_name} failed due to token budget: {e}")
                wave_results["budget_status"] = "red"
                step_result = {
                    "step": step_name,
                    "status": "failed",
                    "error": str(e),
                    "estimated_tokens": 0,
                }
                wave_results["steps"].append(step_result)
                break  # Stop wave on budget failure

        return wave_results

    def execute_step(self, step_name: str, step_type: str, step_config: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a single planning step with token budget enforcement.

        Args:
            step_name: Name of the step
            step_type: Type of step (analysis, implementation, testing, etc.)
            step_config: Step configuration

        Returns:
            Step execution result with token budget information
        """
        # Prepare context for token estimation
        context = self._prepare_step_context(step_name, step_type, step_config)

        # Perform preflight token budget check
        estimate = self.preflight_hook.preflight_check(**context)

        # Record step result
        step_result = {
            "step": step_name,
            "type": step_type,
            "status": "completed",
            "budget_status": estimate.status,
            "estimated_tokens": estimate.total_projected_tokens,
            "compression_applied": len(estimate.compression_applied) > 0,
            "top_contributors": estimate.top_contributors,
            "recommendations": estimate.recommended_reductions,
        }

        # Execute the actual step logic
        if estimate.action == "proceed":
            logger.info(f"Step {step_name} proceeding with {estimate.total_projected_tokens:,} tokens")
            result = self._execute_step_logic(step_type, step_config, estimate)
            step_result.update(result)

        elif estimate.action == "compress":
            logger.info(f"Step {step_name} compressed from original estimate")
            logger.info(f"Compression applied: {estimate.compression_applied}")
            result = self._execute_step_logic(step_type, step_config, estimate)
            step_result.update(result)

        else:  # 'block'
            # This should be caught by the preflight hook, but add safety
            raise TokenBudgetExceededError(
                f"Step {step_name} blocked: {estimate.total_projected_tokens:,} tokens",
            )

        self.step_results.append(step_result)
        return step_result

    def _prepare_step_context(
        self, step_name: str, step_type: str, step_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Prepare context for token estimation based on step type and configuration.

        This is where you would gather the actual content that will be sent to SWE 1.5.
        """
        base_context = {
            "plan_step": f"{self.current_phase}/{self.current_wave}/{step_name}",
            "system_prompt": self._get_system_prompt(step_type),
            "user_prompt": step_config.get("prompt", ""),
            "files": self._get_file_contents(step_config.get("files", [])),
            "diffs": self._get_diff_contents(step_config.get("diffs", [])),
            "logs": self._get_log_contents(step_config.get("logs", [])),
            "retrieved_context": self._get_retrieved_context(step_config.get("context", [])),
            "prior_steps": self._get_prior_step_contents(),
        }

        return base_context

    def _get_system_prompt(self, step_type: str) -> str:
        """Get system prompt based on step type"""
        prompts = {
            "analysis": "You are a code analysis expert. Analyze the provided code and identify issues.",
            "implementation": "You are a senior software engineer. Implement the requested feature.",
            "testing": "You are a QA engineer. Write comprehensive tests for the provided code.",
            "refactoring": "You are a code refactoring specialist. Improve the code structure.",
            "documentation": "You are a technical writer. Create clear documentation.",
        }
        return prompts.get(step_type, "You are a helpful assistant.")

    def _get_file_contents(self, file_paths: list[str]) -> list[dict[str, Any]]:
        """Get file contents for token estimation"""
        files = []
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                files.append(
                    {
                        "path": file_path,
                        "content": content,
                    }
                )
            else:
                # Simulate file content for demonstration
                files.append(
                    {
                        "path": file_path,
                        "content": f"# Simulated content for {file_path}\n"
                        + "def example_function():\n    pass\n" * 100,
                    }
                )
        return files

    def _get_diff_contents(self, diff_paths: list[str]) -> list[dict[str, Any]]:
        """Get diff contents for token estimation"""
        diffs = []
        for diff_path in diff_paths:
            # Simulate diff content
            diff_content = f"""diff --git a/{diff_path} b/{diff_path}
--- a/{diff_path}
+++ b/{diff_path}
@@ -1,3 +1,4 @@
 def existing_function():
     pass
+def new_function():
+    pass"""
            diffs.append(
                {
                    "path": diff_path,
                    "content": diff_content,
                }
            )
        return diffs

    def _get_log_contents(self, log_sources: list[str]) -> list[dict[str, Any]]:
        """Get log contents for token estimation"""
        logs = []
        for source in log_sources:
            # Simulate log content
            log_content = f"""2023-01-01 12:00:00 INFO Starting {source}
2023-01-01 12:00:01 DEBUG Loading configuration
2023-01-01 12:00:02 ERROR Failed to load {source}
Traceback (most recent call last):
  File "main.py", line 10, in <module>
    load_config()
FileNotFoundError: Config file not found
2023-01-01 12:00:03 INFO Process completed"""
            logs.append(
                {
                    "source": source,
                    "content": log_content,
                }
            )
        return logs

    def _get_retrieved_context(self, context_sources: list[str]) -> list[dict[str, Any]]:
        """Get retrieved context for token estimation"""
        context = []
        for i, source in enumerate(context_sources):
            # Simulate retrieved context
            context_content = (
                f"""Retrieved context chunk {i + 1} from {source}:
This is documentation about the codebase structure and best practices.
It contains important information about coding standards and patterns.
{source} provides guidance for implementation decisions.
"""
                * 5
            )  # Make it substantial
            context.append(
                {
                    "source": source,
                    "content": context_content,
                    "chunk_id": f"chunk_{i + 1}",
                }
            )
        return context

    def _get_prior_step_contents(self) -> list[str]:
        """Get contents from prior steps to carry forward"""
        # Return last 3 step results as context
        return [str(result) for result in self.step_results[-3:]]

    def _execute_step_logic(self, step_type: str, step_config: dict[str, Any], estimate) -> dict[str, Any]:
        """
        Execute the actual step logic.

        In a real implementation, this would call SWE 1.5 with the compressed content.
        """
        # Simulate step execution
        execution_time = 0.5  # Simulated execution time

        return {
            "execution_time": execution_time,
            "output_tokens": 5000,  # Simulated output
            "success": True,
            "artifacts": [f"artifact_{step_type}_{hash(str(step_config)) % 1000}.json"],
        }

    def _log_phase_summary(self, phase_results: dict[str, Any]) -> None:
        """Log phase execution summary"""
        logger.info(f"Phase {phase_results['phase']} completed:")
        logger.info(f"  - Total tokens: {phase_results['total_tokens']:,}")
        logger.info(f"  - Budget violations: {phase_results['budget_violations']}")
        logger.info(f"  - Compression events: {phase_results['compression_events']}")

        # Get overall budget summary
        budget_summary = self.preflight_hook.get_budget_summary()
        logger.info("Overall budget summary:")
        logger.info(f"  - Total steps: {budget_summary['total_steps']}")
        logger.info(f"  - Average tokens per step: {budget_summary['average_tokens_per_step']:.0f}")
        logger.info(f"  - Status distribution: {budget_summary['status_distribution']}")

    def get_workflow_summary(self) -> dict[str, Any]:
        """Get complete workflow summary"""
        budget_summary = self.preflight_hook.get_budget_summary()

        return {
            "workflow_summary": {
                "phases_completed": 1,  # Single phase in this example
                "total_steps": len(self.step_results),
                "total_tokens": sum(r["estimated_tokens"] for r in self.step_results),
            },
            "budget_summary": budget_summary,
            "step_results": self.step_results,
        }


# Example usage
def example_workflow():
    """Example of using the TokenAwarePlanningWorkflow"""

    # Initialize workflow with custom budget
    custom_budget = TokenBudget(
        WARNING_THRESHOLD=120000,  # Earlier warning for demo
        SAFE_OPERATING_CAP=150000,  # Lower safe cap for demo
    )

    workflow = TokenAwarePlanningWorkflow(
        budget_file=Path("docs/reports/plans/example_workflow_budget.json"),
        custom_budget=custom_budget,
    )

    # Define phase configuration
    phase_configs = [
        {
            "name": "analysis_wave",
            "steps": [
                {
                    "name": "code_analysis",
                    "type": "analysis",
                    "prompt": "Analyze the existing codebase for the new feature",
                    "files": ["src/main.py", "src/utils.py", "src/config.py"],
                    "context": ["documentation.md", "requirements.txt"],
                },
                {
                    "name": "dependency_analysis",
                    "type": "analysis",
                    "prompt": "Analyze dependencies and potential conflicts",
                    "files": ["requirements.txt", "setup.py"],
                    "logs": ["pip_install.log"],
                },
            ],
        },
        {
            "name": "implementation_wave",
            "steps": [
                {
                    "name": "feature_implementation",
                    "type": "implementation",
                    "prompt": "Implement the new feature following best practices",
                    "files": ["src/main.py", "src/utils.py"],
                    "diffs": ["src/main.py"],
                    "context": ["documentation.md", "api_reference.md"],
                },
                {
                    "name": "unit_tests",
                    "type": "testing",
                    "prompt": "Write comprehensive unit tests",
                    "files": ["tests/test_main.py", "tests/test_utils.py"],
                    "diffs": ["tests/test_main.py"],
                },
            ],
        },
        {
            "name": "documentation_wave",
            "steps": [
                {
                    "name": "update_docs",
                    "type": "documentation",
                    "prompt": "Update documentation for the new feature",
                    "files": ["README.md", "docs/api.md"],
                    "diffs": ["README.md"],
                },
            ],
        },
    ]

    # Execute the phase
    try:
        results = workflow.execute_phase("feature_development", phase_configs)

        # Print workflow summary
        summary = workflow.get_workflow_summary()
        print("\n" + "=" * 50)
        print("WORKFLOW EXECUTION SUMMARY")
        print("=" * 50)
        print(f"Phases completed: {summary['workflow_summary']['phases_completed']}")
        print(f"Total steps: {summary['workflow_summary']['total_steps']}")
        print(f"Total tokens used: {summary['workflow_summary']['total_tokens']:,}")
        print(f"Average tokens per step: {summary['budget_summary']['average_tokens_per_step']:.0f}")
        print(f"Status distribution: {summary['budget_summary']['status_distribution']}")

        return results

    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        logger.error(f"Workflow failed: {e}")
        raise


if __name__ == "__main__":
    # Run the example workflow
    example_workflow()
