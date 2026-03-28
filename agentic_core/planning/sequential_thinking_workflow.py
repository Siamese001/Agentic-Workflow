"""
Sequential Thinking Enhanced Planning Workflow for SWE 1.5

This workflow integrates sequential thinking MCP calls into the planning process
to improve reasoning quality and structured problem decomposition.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from agentic_core.planning.preflight_hook import PlanningPreflightHook, TokenBudgetExceededError
from agentic_core.planning.token_estimator import TokenBudget, ContextWindowEstimator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SequentialThinkingEnhancedWorkflow:
    """
    SWE 1.5 planning workflow with integrated sequential thinking.

    This workflow automatically triggers sequential thinking for complex tasks
    and integrates with the token budget management system.
    """

    def __init__(self,
                 budget_file: Optional[Path] = None,
                 custom_budget: Optional[TokenBudget] = None,
                 seq_thinking_enabled: bool = True):
        """
        Initialize the sequential thinking enhanced workflow.

        Args:
            budget_file: Path to budget history file
            custom_budget: Custom token budget configuration
            seq_thinking_enabled: Enable sequential thinking integration
        """
        self.preflight_hook = PlanningPreflightHook(
            estimator=ContextWindowEstimator(budget=custom_budget),
            budget_file=budget_file
        )

        self.seq_thinking_enabled = seq_thinking_enabled and self._check_seq_thinking_available()

        # Workflow state
        self.current_phase = None
        self.current_wave = None
        self.step_results = []
        self.seq_thinking_usage = 0

        # Sequential thinking configuration
        self.seq_thinking_config = {
            'max_thoughts': int(os.environ.get('SEQUENTIAL_THINKING_MAX_THOUGHTS', '15')),
            'token_budget': int(os.environ.get('SEQUENTIAL_THINKING_TOKEN_BUDGET', '30000')),
            'complexity_threshold': os.environ.get('SEQUENTIAL_THINKING_COMPLEXITY_THRESHOLD', 'medium'),
            'auto_trigger': os.environ.get('SEQUENTIAL_THINKING_AUTO_TRIGGER', 'true').lower() == 'true'
        }

    def _check_seq_thinking_available(self) -> bool:
        """Check if sequential thinking MCP is available."""
        return os.environ.get('SEQUENTIAL_THINKING_ENABLED', 'false').lower() == 'true'

    def force_sequential_thinking(self, step_type: str, step_config: Dict[str, Any]) -> bool:
        """Determine if sequential thinking should be forced for this step."""

        if not self.seq_thinking_enabled:
            return False

        # Force for complex analysis tasks
        complex_types = ['analysis', 'architecture', 'refactoring', 'debugging', 'planning']
        high_complexity = ['high', 'critical']

        # Check step type
        if step_type in complex_types:
            return True

        # Check complexity level
        if step_config.get('complexity', 'medium').lower() in high_complexity:
            return True

        # Check for multi-file operations
        if len(step_config.get('files', [])) > 3:
            return True

        # Check for integration tasks
        if any(keyword in step_type.lower() for keyword in ['integration', 'multiple', 'cross']):
            return True

        # Check auto-trigger configuration
        if self.seq_thinking_config['auto_trigger']:
            # Auto-trigger for medium+ complexity
            if step_config.get('complexity', 'medium') in ['medium', 'high', 'critical']:
                return True

        return False

    def _get_seq_thinking_template(self, step_type: str) -> str:
        """Get appropriate sequential thinking template for step type."""

        templates = {
            'analysis': """
# Sequential Analysis for {step_name}

## Context
{context}

## Task
Analyze the provided code/problem systematically using sequential thinking.

## Sequential Analysis Requirements

### Thought 1: Problem Understanding
- What is the core issue or requirement?
- What are the key constraints and boundaries?
- What information is missing or unclear?

### Thought 2: Current State Assessment
- What exists currently?
- What are the strengths and weaknesses?
- What patterns or anti-patterns do you observe?

### Thought 3: Decomposition
- Break the problem into smaller, manageable components
- Identify dependencies between components
- Prioritize components by importance or risk

### Thought 4: Analysis Strategy
- What analysis approach will be most effective?
- What tools or techniques should be used?
- How will you validate your analysis?

### Thought 5: Risk Assessment
- What could go wrong with this analysis?
- What are the common pitfalls in this type of problem?
- How will you mitigate these risks?

### Thought 6: Recommendations
- What are your key findings?
- What specific actions should be taken?
- What are the next steps and dependencies?

Please analyze this systematically using the sequential thinking approach.
""",
            'implementation': """
# Sequential Implementation Planning for {step_name}

## Context
{context}

## Task
Plan the implementation using sequential thinking for structured reasoning.

## Sequential Planning Requirements

### Thought 1: Requirements Analysis
- What exactly needs to be implemented?
- What are the functional and non-functional requirements?
- What are the acceptance criteria?

### Thought 2: Design Approach
- What architectural pattern should be used?
- How should the code be structured?
- What design principles apply?

### Thought 3: Implementation Strategy
- What is the optimal sequence of implementation?
- What components should be built first?
- How should dependencies be managed?

### Thought 4: Risk Mitigation
- What implementation risks exist?
- How will you handle edge cases?
- What testing strategy is needed?

### Thought 5: Integration Planning
- How will this integrate with existing code?
- What APIs or interfaces are needed?
- How will backward compatibility be maintained?

### Thought 6: Validation & Testing
- How will you verify the implementation?
- What test cases are needed?
- How will you measure success?

Please plan this implementation systematically using sequential thinking.
""",
            'debugging': """
# Sequential Debugging Analysis for {step_name}

## Context
{context}

## Task
Debug the issue systematically using sequential thinking.

## Sequential Debugging Requirements

### Thought 1: Problem Definition
- What exactly is the symptom or error?
- When and where does it occur?
- What are the reproduction steps?

### Thought 2: Information Gathering
- What logs, traces, or error messages are available?
- What recent changes might be related?
- What environmental factors could be relevant?

### Thought 3: Hypothesis Formation
- What are the most likely root causes?
- How can you prioritize hypotheses?
- What evidence supports each hypothesis?

### Thought 4: Systematic Investigation
- How will you test each hypothesis?
- What debugging tools or techniques will you use?
- How will you isolate variables?

### Thought 5: Solution Development
- What is the most likely fix?
- How will you implement it safely?
- How will you test the fix?

### Thought 6: Prevention
- How can similar issues be prevented?
- What monitoring or alerts are needed?
- What documentation should be updated?

Please debug this systematically using sequential thinking.
"""
        }

        return templates.get(step_type, templates['analysis'])

    def _execute_sequential_thinking(self, step_name: str, step_type: str,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sequential thinking for a step."""

        if not self.seq_thinking_enabled:
            return {'success': False, 'reason': 'Sequential thinking not available'}

        logger.info(f"Executing sequential thinking for step: {step_name}")

        # Get template
        template = self._get_seq_thinking_template(step_type)

        # Format context for template
        context_str = json.dumps(context, indent=2)
        prompt = template.format(
            step_name=step_name,
            context=context_str
        )

        # In a real implementation, this would call the sequential thinking MCP
        # For now, we simulate the call
        seq_result = {
            'success': True,
            'thoughts': [
                f"Thought 1: Analyzing {step_name} requirements and context",
                f"Thought 2: Breaking down {step_type} into manageable components",
                f"Thought 3: Identifying dependencies and risks",
                f"Thought 4: Developing systematic approach",
                f"Thought 5: Planning validation strategy",
                f"Thought 6: Defining next steps and success criteria"
            ],
            'recommendations': [
                "Proceed with structured approach",
                "Monitor for complexity indicators",
                "Validate assumptions early"
            ],
            'token_usage': 5000,  # Estimated
            'response_time': 2.5   # Estimated
        }

        self.seq_thinking_usage += 1
        logger.info(f"Sequential thinking completed for {step_name}")

        return seq_result

    def execute_step_with_seq_thinking(self, step_name: str, step_type: str,
                                     step_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute step with forced sequential thinking when appropriate."""

        # Prepare context for token estimation
        context = self._prepare_step_context(step_name, step_type, step_config)

        # Check if we should force sequential thinking
        if self.force_sequential_thinking(step_type, step_config):
            # Inject sequential thinking trigger
            step_config['force_sequential_thinking'] = True
            step_config['seq_thinking_template'] = self._get_seq_thinking_template(step_type)

            logger.info(f"Forcing sequential thinking for step: {step_name}")

            # Execute sequential thinking first
            seq_result = self._execute_sequential_thinking(step_name, step_type, context)

            if seq_result['success']:
                # Add sequential thinking results to context
                context['sequential_thinking'] = seq_result
                logger.info(f"Sequential thinking enhanced context for {step_name}")
            else:
                logger.warning(f"Sequential thinking failed for {step_name}: {seq_result.get('reason', 'Unknown')}")

        # Perform preflight token budget check
        estimate = self.preflight_hook.preflight_check(**context)

        # Record step result
        step_result = {
            'step': step_name,
            'type': step_type,
            'status': 'completed',
            'budget_status': estimate.status,
            'estimated_tokens': estimate.total_projected_tokens,
            'compression_applied': len(estimate.compression_applied) > 0,
            'top_contributors': estimate.top_contributors,
            'recommendations': estimate.recommended_reductions,
            'sequential_thinking_used': step_config.get('force_sequential_thinking', False)
        }

        # Execute the actual step logic
        if estimate.action == 'proceed':
            logger.info(f"Step {step_name} proceeding with {estimate.total_projected_tokens:,} tokens")
            result = self._execute_step_logic(step_type, step_config, estimate)
            step_result.update(result)

        elif estimate.action == 'compress':
            logger.info(f"Step {step_name} compressed from original estimate")
            logger.info(f"Compression applied: {estimate.compression_applied}")
            result = self._execute_step_logic(step_type, step_config, estimate)
            step_result.update(result)

        else:  # 'block'
            # This should be caught by the preflight hook, but add safety
            raise TokenBudgetExceededError(
                f"Step {step_name} blocked: {estimate.total_projected_tokens:,} tokens"
            )

        self.step_results.append(step_result)
        return step_result

    def _prepare_step_context(self, step_name: str, step_type: str, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for token estimation based on step type and configuration."""
        base_context = {
            'plan_step': f"{self.current_phase}/{self.current_wave}/{step_name}",
            'system_prompt': self._get_system_prompt(step_type),
            'user_prompt': step_config.get('prompt', ''),
            'files': self._get_file_contents(step_config.get('files', [])),
            'diffs': self._get_diff_contents(step_config.get('diffs', [])),
            'logs': self._get_log_contents(step_config.get('logs', [])),
            'retrieved_context': self._get_retrieved_context(step_config.get('context', [])),
            'prior_steps': self._get_prior_step_contents(),
            'sequential_thinking_enabled': self.seq_thinking_enabled
        }

        return base_context

    def _get_system_prompt(self, step_type: str) -> str:
        """Get system prompt based on step type with sequential thinking integration."""
        base_prompts = {
            'analysis': "You are a code analysis expert. Analyze the provided code and identify issues.",
            'implementation': "You are a senior software engineer. Implement the requested feature.",
            'testing': "You are a QA engineer. Write comprehensive tests for the provided code.",
            'refactoring': "You are a code refactoring specialist. Improve the code structure.",
            'documentation': "You are a technical writer. Create clear documentation.",
            'debugging': "You are a debugging specialist. Systematically identify and resolve issues.",
            'planning': "You are a system architect. Plan complex implementations systematically."
        }

        base_prompt = base_prompts.get(step_type, "You are a helpful assistant.")

        if self.seq_thinking_enabled:
            base_prompt += "\n\nUse sequential thinking to break down complex problems into manageable steps. Think systematically and validate your reasoning at each step."

        return base_prompt

    def _get_file_contents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Get file contents for token estimation."""
        files = []
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                files.append({
                    'path': file_path,
                    'content': content
                })
            else:
                # Simulate file content for demonstration
                files.append({
                    'path': file_path,
                    'content': f"# Simulated content for {file_path}\n" + "def example_function():\n    pass\n" * 100
                })
        return files

    def _get_diff_contents(self, diff_paths: List[str]) -> List[Dict[str, Any]]:
        """Get diff contents for token estimation."""
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
            diffs.append({
                'path': diff_path,
                'content': diff_content
            })
        return diffs

    def _get_log_contents(self, log_sources: List[str]) -> List[Dict[str, Any]]:
        """Get log contents for token estimation."""
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
            logs.append({
                'source': source,
                'content': log_content
            })
        return logs

    def _get_retrieved_context(self, context_sources: List[str]) -> List[Dict[str, Any]]:
        """Get retrieved context for token estimation."""
        context = []
        for i, source in enumerate(context_sources):
            # Simulate retrieved context
            context_content = f"""Retrieved context chunk {i+1} from {source}:
This is documentation about the codebase structure and best practices.
It contains important information about coding standards and patterns.
{source} provides guidance for implementation decisions.
""" * 5  # Make it substantial
            context.append({
                'source': source,
                'content': context_content,
                'chunk_id': f"chunk_{i+1}"
            })
        return context

    def _get_prior_step_contents(self) -> List[str]:
        """Get contents from prior steps to carry forward."""
        # Return last 3 step results as context
        return [str(result) for result in self.step_results[-3:]]

    def _execute_step_logic(self, step_type: str, step_config: Dict[str, Any], estimate) -> Dict[str, Any]:
        """Execute the actual step logic."""
        # Simulate step execution
        execution_time = 0.5  # Simulated execution time

        return {
            'execution_time': execution_time,
            'output_tokens': 5000,  # Simulated output
            'success': True,
            'artifacts': [f"artifact_{step_type}_{hash(str(step_config)) % 1000}.json"]
        }

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get complete workflow summary including sequential thinking metrics."""
        budget_summary = self.preflight_hook.get_budget_summary()

        return {
            'workflow_summary': {
                'phases_completed': 1,  # Single phase in this example
                'total_steps': len(self.step_results),
                'total_tokens': sum(r['estimated_tokens'] for r in self.step_results),
                'sequential_thinking_usage': self.seq_thinking_usage,
                'sequential_thinking_enabled': self.seq_thinking_enabled
            },
            'budget_summary': budget_summary,
            'step_results': self.step_results,
            'sequential_thinking_config': self.seq_thinking_config
        }


# Example usage
def example_sequential_thinking_workflow():
    """Example of using the SequentialThinkingEnhancedWorkflow"""

    # Initialize workflow with sequential thinking enabled
    custom_budget = TokenBudget(
        WARNING_THRESHOLD=120000,  # Earlier warning for demo
        SAFE_OPERATING_CAP=150000   # Lower safe cap for demo
    )

    workflow = SequentialThinkingEnhancedWorkflow(
        budget_file=Path("docs/reports/plans/seq_thinking_workflow_budget.json"),
        custom_budget=custom_budget,
        seq_thinking_enabled=True
    )

    # Define phase configuration with complex tasks that should trigger sequential thinking
    phase_configs = [
        {
            'name': 'complex_analysis_wave',
            'steps': [
                {
                    'name': 'architecture_analysis',
                    'type': 'analysis',
                    'prompt': 'Analyze the system architecture for scalability issues',
                    'files': ['src/main.py', 'src/utils.py', 'src/config.py', 'src/database.py', 'src/api.py'],
                    'context': ['architecture.md', 'requirements.txt'],
                    'complexity': 'high'
                },
                {
                    'name': 'dependency_analysis',
                    'type': 'analysis',
                    'prompt': 'Analyze dependencies and potential conflicts',
                    'files': ['requirements.txt', 'setup.py', 'pyproject.toml'],
                    'logs': ['pip_install.log'],
                    'complexity': 'medium'
                }
            ]
        },
        {
            'name': 'implementation_wave',
            'steps': [
                {
                    'name': 'feature_implementation',
                    'type': 'implementation',
                    'prompt': 'Implement the new feature following best practices',
                    'files': ['src/main.py', 'src/utils.py'],
                    'diffs': ['src/main.py'],
                    'context': ['documentation.md', 'api_reference.md'],
                    'complexity': 'high'
                },
                {
                    'name': 'debug_session',
                    'type': 'debugging',
                    'prompt': 'Debug the performance issue in the main module',
                    'files': ['src/main.py', 'logs/error.log'],
                    'logs': ['performance.log', 'error.log'],
                    'complexity': 'critical'
                }
            ]
        }
    ]

    # Execute the phase
    try:
        results = workflow.execute_phase('complex_feature_development', phase_configs)

        # Print workflow summary
        summary = workflow.get_workflow_summary()
        print("\n" + "="*60)
        print("SEQUENTIAL THINKING ENHANCED WORKFLOW SUMMARY")
        print("="*60)
        print(f"Phases completed: {summary['workflow_summary']['phases_completed']}")
        print(f"Total steps: {summary['workflow_summary']['total_steps']}")
        print(f"Total tokens used: {summary['workflow_summary']['total_tokens']:,}")
        print(f"Sequential thinking usage: {summary['workflow_summary']['sequential_thinking_usage']}")
        print(f"Sequential thinking enabled: {summary['workflow_summary']['sequential_thinking_enabled']}")
        print(f"Average tokens per step: {summary['budget_summary']['average_tokens_per_step']:.0f}")
        print(f"Status distribution: {summary['budget_summary']['status_distribution']}")

        return results

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise


if __name__ == "__main__":
    # Run the example workflow
    example_sequential_thinking_workflow()
