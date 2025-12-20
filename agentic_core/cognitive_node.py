```python
import ast
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Assuming llm_client is a local module in the same project structure
from llm_client import LLMClient


class CognitiveNode:
    """
    Implements Sequential Thinking for the runtime agent.
    Forces the LLM to 'Show its work' before generating the final code.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("CognitiveNode")
        self.llm = LLMClient()

        # Load configuration
        if config_path is None:
            config_path = Path("config/sequential_thinking.yaml")
        else:
            config_path = Path(config_path)

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(
                f"Config file not found at {config_path}, using defaults"
            )
            self.config = self._get_default_config()
        except yaml.YAMLError as e:
            self.logger.error(
                f"Error parsing config file at {config_path}: {e}, using defaults"
            )
            self.config = self._get_default_config()

        # Apply configuration
        self.max_steps: int = self.config.get('max_steps', 10)
        self.step_timeout: int = self.config.get('step_timeout', 30)
        self.overall_timeout: int = self.config.get('overall_timeout', 300)
        self.circuit_breaker_trips: int = self.config.get(
            'circuit_breaker_trips', 2
        )
        self.slow_step_threshold: int = self.config.get(
            'slow_step_threshold', 30
        )
        self.persist_history: bool = self.config.get('persist_history', True)
        self.max_syntax_attempts: int = self.config.get(
            'max_syntax_attempts', 2
        )

        # [HARDENED 5c] Temperature decay configuration
        self.base_temp: float = self.config.get('base_temperature', 0.7)
        self.min_temp: float = self.config.get('min_temperature', 0.0)

        # Initialize history directory
        self.history_dir: Path = Path(
            self.config.get('history_dir', 'logs/thought_history')
        )
        if self.persist_history:
            self.history_dir.mkdir(parents=True, exist_ok=True)

    def _calculate_dynamic_temperature(self, current_step: int) -> float:
        """
        [HARDENED 5c] Calculates temperature based on progress.
        Decays linearly from base_temp to min_temp as we approach max_steps.

        Args:
            current_step: The current step number in the thinking process.

        Returns:
            The calculated temperature for the LLM.
        """
        if self.max_steps <= 1:
            return self.min_temp

        progress = current_step / (self.max_steps - 1)
        # Linear decay formula
        current_temp = self.base_temp * (1.0 - progress)

        # Clamp to ensure we don't go below absolute zero logic
        return max(self.min_temp, current_temp)

    def _get_system_directive(self, current_step: int) -> str:
        """
        Returns the appropriate psychological stance for the agent
        based on how much 'time' it has left to think.

        Args:
            current_step: The current step number in the thinking process.

        Returns:
            A string directive for the LLM's phase.
        """
        if current_step < (self.max_steps * 0.4):
            return "Phase: EXPLORATION. Generate diverse hypotheses. Be creative."
        elif current_step < (self.max_steps * 0.8):
            return "Phase: CONVERGENCE. Critique hypotheses. Discard weak paths. Focus."
        else:
            return (
                "Phase: EXECUTION. FINAL WARNING. You must conclude immediately. "
                "Do not ask for more information."
            )

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if config file is missing or invalid."""
        return {
            'max_steps': 5,
            'step_timeout': 30,
            'overall_timeout': 300,
            'circuit_breaker_trips': 2,
            'slow_step_threshold': 30,
            'persist_history': True,
            'history_dir': 'logs/thought_history',
            'max_syntax_attempts': 2,
            'base_temperature': 0.7,
            'min_temperature': 0.0,
            'log_thoughts': True,  # Not used in current code, but good to have
            'log_timing': True,  # Not used in current code, but good to have
        }

    def _handle_step_duration_and_circuit_breaker(
        self, step_duration: float, circuit_breaker_count: int, step_num: int
    ) -> int:
        """
        Handles checking step duration against threshold and manages the circuit breaker.

        Args:
            step_duration: The time taken for the current step.
            circuit_breaker_count: The current count of slow steps.
            step_num: The current step number (1-indexed).

        Returns:
            The updated circuit_breaker_count.

        Raises:
            TimeoutError: If the circuit breaker trips due to too many slow steps.
        """
        # If the step was not slow, return early without incrementing or checking the breaker.
        if not (step_duration > self.slow_step_threshold):
            return circuit_breaker_count

        # If we reach here, the step was slow.
        circuit_breaker_count += 1
        self.logger.warning(
            f"⚠️ Step {step_num} took {step_duration:.2f}s "
            f"(threshold: {self.slow_step_threshold}s)"
        )

        # Check if the circuit breaker should trip after incrementing the count.
        if circuit_breaker_count >= self.circuit_breaker_trips:
            self.logger.error("❌ Circuit breaker tripped - too many slow steps")
            raise TimeoutError(
                "Sequential thinking circuit breaker activated due to slow steps"
            )

        return circuit_breaker_count

    def _check_overall_timeout(self, start_time: float) -> None:
        """
        Checks if the overall thinking timeout has been exceeded.

        Args:
            start_time: The timestamp when the overall thinking process started.

        Raises:
            TimeoutError: If the overall timeout has been exceeded.
        """
        if time.time() - start_time > self.overall_timeout:
            self.logger.error(
                f"❌ Overall thinking timeout exceeded ({self.overall_timeout}s)"
            )
            raise TimeoutError(
                "Sequential thinking exceeded maximum allowed duration"
            )

    def _build_thinking_prompt(
        self,
        user_goal: str,
        toolbox_desc: str,
        current_step: int,
        history: List[Dict[str, Any]],
        phase_directive: str,
    ) -> str:
        """
        Builds the system prompt for a thinking step.

        Args:
            user_goal: The main goal provided by the user.
            toolbox_desc: Description of available tools.
            current_step: The current step number (0-indexed).
            history: A list of past thoughts.
            phase_directive: The psychological stance for the current phase.

        Returns:
            The formatted system prompt string.
        """
        history_block = "\n".join(
            [f"Step {h['step']}: {h['thought']}" for h in history]
        )

        return (
            f"You are a Sequential Thinking Engine. {phase_directive}\n\n"
            f"Goal: {user_goal}\n"
            f"Tools: {toolbox_desc}\n"
            f"Current Step: {current_step + 1}/{self.max_steps}\n\n"
            f"PAST THOUGHTS:\n"
            f"{history_block}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Analyze the goal and the past thoughts.\n"
            f"2. Decide if you have enough information and clarity to write the "
            f"final Python code.\n"
            f"3. Output JSON ONLY:\n"
            f"{{\n"
            f'    "thought": "Your analysis of the current situation and next '
            f'step in the sequence.",\n'
            f'    "needs_more_thought": true/false (Set to false ONLY when the '
            f'thought is sufficient to write the final code),\n'
            f"    \"step\": {current_step + 1}\n"
            f"}}\n"
        )

    def _execute_thinking_step(
        self,
        system_prompt: str,
        raw_prompt: str,
        current_step: int,
        circuit_breaker_count: int,
    ) -> Tuple[Dict[str, Any], int, float]:
        """
        Executes a single LLM thinking step, handles timeouts and circuit breaker.

        Args:
            system_prompt: The system-level instructions for the LLM.
            raw_prompt: The user-level prompt for the LLM.
            current_step: The current step number (0-indexed).
            circuit_breaker_count: The current count of slow steps.

        Returns:
            A tuple containing:
                - The LLM's response (parsed JSON).
                - The updated circuit_breaker_count.
                - The duration of the step.

        Raises:
            TimeoutError: If the step times out or the circuit breaker trips.
            RuntimeError: If the LLM call fails for other reasons.
        """
        try:
            step_start = time.time()
            # [HARDENED 5c] Call LLM with dynamic temperature
            # Note: LLMClient doesn't support temperature parameter yet,
            # so this line is a placeholder for future integration.
            # current_temp = self._calculate_dynamic_temperature(current_step)
            response = self.llm.generate_plan(system_prompt, raw_prompt)
            step_duration = time.time() - step_start

            circuit_breaker_count = self._handle_step_duration_and_circuit_breaker(
                step_duration, circuit_breaker_count, current_step + 1
            )
            return response, circuit_breaker_count, step_duration
        except TimeoutError:
            raise  # Re-raise specific TimeoutError
        except Exception as e:
            self.logger.error(f"❌ Cognitive Step Failed: {e}")
            raise RuntimeError(
                f"Cognitive step {current_step + 1} failed: {str(e)}"
            ) from e

    def _process_thinking_step_result(
        self,
        session_id: str,
        user_goal: str,
        current_step: int,
        response: Dict[str, Any],
        step_duration: float,
        history: List[Dict[str, Any]],
    ) -> Tuple[str, bool]:
        """
        Processes the LLM's thought response, updates history, and persists it.

        Args:
            session_id: Unique identifier for the current thinking session.
            user_goal: The main goal provided by the user.
            current_step: The current step number (0-indexed).
            response: The LLM's parsed JSON response.
            step_duration: The time taken for the current step.
            history: The list of past thoughts to update.

        Returns:
            A tuple containing:
                - The extracted thought string.
                - A boolean indicating if more thought is needed.
        """
        thought = response.get("thought", "Analysis failed, proceeding to synthesis.")
        needs_more = response.get("needs_more_thought", True)

        self.logger.info(f"🤔 Step {current_step + 1}: {thought[:120]}...")

        history.append(
            {
                "step": current_step + 1,
                "thought": thought,
                "timestamp": datetime.now().isoformat(),
                "duration": step_duration,
            }
        )

        if self.persist_history:
            self._save_thought_history(session_id, user_goal, history)

        return thought, needs_more

    def _handle_final_synthesis(
        self,
        session_id: str,
        user_goal: str,
        history: List[Dict[str, Any]],
        toolbox_desc: str,
    ) -> str:
        """
        Handles the final code synthesis and persistence.

        Args:
            session_id: Unique identifier for the current thinking session.
            user_goal: The main goal provided by the user.
            history: The complete list of thoughts.
            toolbox_desc: Description of available tools.

        Returns:
            The final generated Python code string.
        """
        self.logger.info("💡 EPIPHANY REACHED. Constructing Final Plan.")
        final_code = self._synthesize_code(user_goal, history, toolbox_desc)

        if self.persist_history:
            self._save_final_result(session_id, final_code)
        return final_code

    def think(self, user_goal: str, toolbox_desc: str) -> str:
        """
        Loops until the agent is satisfied with its plan or max steps are reached.
        Returns the final generated Python code string.

        Args:
            user_goal: The main goal provided by the user.
            toolbox_desc: Description of available tools.

        Returns:
            The final generated Python code string.

        Raises:
            TimeoutError: If overall thinking duration is exceeded or circuit
                          breaker trips.
            RuntimeError: If cognitive steps or code synthesis fail.
        """
        start_time = time.time()
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.logger.info(
            f"🧠 STARTING SEQUENTIAL THINKING LOOP (Max {self.max_steps} Steps, "
            f"{self.step_timeout}s timeout each)..."
        )

        history: List[Dict[str, Any]] = []
        circuit_breaker_count = 0

        # Initial call is always the raw user goal
        raw_prompt = user_goal

        for i in range(self.max_steps):
            self._check_overall_timeout(start_time)

            # [HARDENED 5c] 1. Dynamic Hardening parameters
            current_temp = self._calculate_dynamic_temperature(i)
            phase_directive = self._get_system_directive(i)
            self.logger.debug(
                f"Step {i + 1}/{self.max_steps} | Temp: {current_temp:.2f} | "
                f"{phase_directive}"
            )

            # Dynamic Prompt that evolves based on past thoughts
            system_prompt = self._build_thinking_prompt(
                user_goal, toolbox_desc, i, history, phase_directive
            )

            response, circuit_breaker_count, step_duration = (
                self._execute_thinking_step(
                    system_prompt, raw_prompt, i, circuit_breaker_count
                )
            )

            thought, needs_more = self._process_thinking_step_result(
                session_id, user_goal, i, response, step_duration, history
            )

            if not needs_more:
                return self._handle_final_synthesis(
                    session_id, user_goal, history, toolbox_desc
                )

            # Update the raw prompt for the next loop iteration
            raw_prompt = (
                f"Previous thought: {thought}. Now, what is the next logical step?"
            )

        self.logger.warning(
            f"⚠️ Max thinking steps ({self.max_steps}) reached. "
            "Synthesizing plan with current context."
        )
        return self._handle_final_synthesis(
            session_id, user_goal, history, toolbox_desc
        )

    def _validate_generated_code(self, code: str) -> None:
        """
        Validates the syntax and content of the generated Python code.

        Args:
            code: The Python code string to validate.

        Raises:
            ValueError: If the generated code is empty or only whitespace.
            SyntaxError: If the generated code has invalid Python syntax.
        """
        if not code.strip():
            raise ValueError("Generated code is empty or only whitespace.")
        ast.parse(code)  # This will raise SyntaxError if invalid

    def _build_synthesis_prompt(
        self,
        goal: str,
        thoughts: str,
        toolbox_desc: str,
        attempt: int,
        last_error: Optional[str],
    ) -> str:
        """
        Helper to build the synthesis prompt, reducing nesting.

        Args:
            goal: The main goal provided by the user.
            thoughts: A summary of the agent's thought process.
            toolbox_desc: Description of available tools.
            attempt: The current attempt number for code synthesis.
            last_error: The error message from the previous attempt, if any.

        Returns:
            The formatted synthesis prompt string.
        """
        base_prompt = (
            f"Based on the following Goal and Thought Sequence, write the final, "
            f"complete Python code.\n\n"
            f"GOAL: {goal}\n\n"
            f"CONTEXT (Thought Sequence):\n"
            f"{thoughts}\n\n"
            f"AVAILABLE TOOLS/LIBRARIES:\n"
            f"{toolbox_desc}\n\n"
            f"CRITICAL RULES:\n"
            f"- Write only ONE entry point function (e.g., 'run' or 'main').\n"
            f"- NEVER use triple-quoted f-strings (\"\"\" or ''''). Use string "
            f"concatenation or .format() instead.\n"
            f"- ALL string literals must have matching opening and closing quotes.\n"
            f"- Escape any internal quotes in strings with backslashes (\\\\\").\n"
            f"- Output valid Python code that will compile without syntax errors.\n"
            f"- Output JSON ONLY: {{ \"code\": \"...\" }}\n\n"
            f"EXAMPLE OF CORRECT STRING HANDLING:\n"
            f'message = "Hello, " + name + "!"\n'
            f'query = "SELECT * FROM users WHERE name = \\"" + user_name + "\\""\n\n'
            f"EXAMPLE OF WHAT TO AVOID:\n"
            f'message = "Hello, " + name + "  # Missing closing quote\n'
            f'text = """This is bad"""  # Triple quotes cause issues\n'
        )

        if attempt > 0 and last_error:
            base_prompt += (
                f"\n\nPREVIOUS ATTEMPT FAILED WITH SYNTAX ERROR:\n{last_error}"
                "\n\nPlease fix the syntax error and try again."
            )

        return base_prompt

    def _attempt_code_synthesis_single_pass(
        self,
        goal: str,
        thoughts: str,
        toolbox_desc: str,
        attempt: int,
        last_error: Optional[str],
    ) -> str:
        """
        Performs a single attempt at code synthesis, including LLM call and validation.

        Args:
            goal: The main goal provided by the user.
            thoughts: A summary of the agent's thought process.
            toolbox_desc: Description of available tools.
            attempt: The current attempt number for code synthesis.
            last_error: The error message from the previous attempt, if any.

        Returns:
            The validated Python code string.

        Raises:
            RuntimeError: If the LLM call fails or returns invalid JSON.
            ValueError: If the generated code is empty or only whitespace.
            SyntaxError: If the generated code has invalid Python syntax.
        """
        final_prompt = self._build_synthesis_prompt(
            goal, thoughts, toolbox_desc, attempt, last_error
        )

        try:
            # [HARDENED 5c] Ensure synthesis uses low temp (0.0) for precision
            # Note: LLMClient doesn't support temperature parameter yet,
            # so this line is a placeholder for future integration.
            final_response = self.llm.generate_plan(
                "You are a master coder. Use the context provided to write perfect code.",
                final_prompt,
            )
        except Exception as e:
            self.logger.error(f"❌ LLM code synthesis failed: {e}")
            raise RuntimeError(f"LLM code synthesis failed: {str(e)}") from e

        code = final_response.get("code", "")

        self.logger.debug(f"Raw LLM response: {final_response}")
        self.logger.debug(
            f"Extracted code (first 500 chars): "
            f"{code[:500] if code else 'EMPTY'}"
        )

        self._validate_generated_code(code)
        return code

    def _synthesize_code(
        self, goal: str, history: List[Dict[str, Any]], toolbox_desc: str
    ) -> str:
        """
        Ask the LLM to convert the sequential thought history into Final Python Code.

        Args:
            goal: The main goal provided by the user.
            history: The complete list of thoughts.
            toolbox_desc: Description of available tools.

        Returns:
            The final generated and validated Python code string.

        Raises:
            RuntimeError: If valid code cannot be generated after max attempts.
        """
        self.logger.info("✍️ Synthesizing final code from thought sequence...")
        thoughts = "\n".join(
            [f"Thought {h['step']}: {h['thought']}" for h in history]
        )

        max_attempts = self.max_syntax_attempts
        last_error = None

        for attempt in range(max_attempts):
            try:
                code = self._attempt_code_synthesis_single_pass(
                    goal, thoughts, toolbox_desc, attempt, last_error
                )
                self.logger.info("✅ Code syntax validation passed!")
                return code
            except (SyntaxError, ValueError, RuntimeError) as e:
                last_error = f"Validation/Synthesis error: {str(e)}"
                self.logger.warning(
                    f"⚠️ Code validation/synthesis failed (attempt {attempt + 1}): "
                    f"{last_error}"
                )

        self.logger.error("❌ Max validation attempts reached. Raising exception.")
        raise RuntimeError(
            f"Failed to generate valid code after {max_attempts} attempts. "
            f"Last error: {last_error}"
        )

    def _save_thought_history(
        self, session_id: str, goal: str, history: List[Dict[str, Any]]
    ) -> None:
        """
        Save thought history to disk for debugging.

        Args:
            session_id: Unique identifier for the current thinking session.
            goal: The main goal provided by the user.
            history: The list of thoughts to save.
        """
        try:
            history_file = self.history_dir / f"thoughts_{session_id}.json"
            data_to_save = {
                "session_id": session_id,
                "goal": goal,
                "timestamp": datetime.now().isoformat(),
                "history": history,
            }
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save thought history: {e}")

    def _save_final_result(self, session_id: str, code: str) -> None:
        """
        Save the final generated code.

        Args:
            session_id: Unique identifier for the current thinking session.
            code: The final generated Python code string.
        """
        try:
            result_file = self.history_dir / f"result_{session_id}.py"
            content = (
                f"# Generated on {datetime.now().isoformat()}\n"
                f"# Session ID: {session_id}\n\n"
                f"{code}"
            )
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.logger.warning(f"Failed to save final result: {e}")

```