import ast
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from llm_client import LLMClient

logger = logging.getLogger("CognitiveNode")


class CognitiveNode:
    """
    Implements Sequential Thinking for the runtime agent.
    Forces the LLM to 'Show its work' before generating the final code.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.llm = LLMClient()

        # Load configuration
        if config_path is None:
            config_path = Path("config/sequential_thinking.yaml")

        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(
                f"Config file not found at {config_path}, using defaults")
            self.config = self._get_default_config()

        # Apply configuration
        self.max_steps = self.config.get('max_steps', 10)
        self.step_timeout = self.config.get('step_timeout', 30)
        self.overall_timeout = self.config.get('overall_timeout', 300)
        self.circuit_breaker_trips = self.config.get(
            'circuit_breaker_trips', 2)
        self.slow_step_threshold = self.config.get('slow_step_threshold', 30)
        self.persist_history = self.config.get('persist_history', True)
        self.max_syntax_attempts = self.config.get('max_syntax_attempts', 2)

        # [HARDENED 5c] Temperature decay configuration
        self.base_temp = self.config.get('base_temperature', 0.7)
        self.min_temp = self.config.get('min_temperature', 0.0)
        self.logger = logging.getLogger("CognitiveNode")

        # Initialize history directory
        self.history_dir = Path(self.config.get(
            'history_dir', 'logs/thought_history'))
        if self.persist_history:
            self.history_dir.mkdir(parents=True, exist_ok=True)

    def _calculate_dynamic_temperature(self, current_step: int) -> float:
        """
        [HARDENED 5c] Calculates temperature based on progress.
        Decays linearly from base_temp to min_temp as we approach max_steps.
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
        """
        if current_step < (self.max_steps * 0.4):
            return "Phase: EXPLORATION. Generate diverse hypotheses. Be creative."
        elif current_step < (self.max_steps * 0.8):
            return "Phase: CONVERGENCE. Critique hypotheses. Discard weak paths. Focus."
        else:
            return "Phase: EXECUTION. FINAL WARNING. You must conclude immediately. Do not ask for more information."

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if config file is missing."""
        return {
            'max_steps': 5,
            'step_timeout': 30,
            'overall_timeout': 300,
            'circuit_breaker_trips': 2,
            'slow_step_threshold': 30,
            'persist_history': True,
            'history_dir': 'logs/thought_history',
            'max_syntax_attempts': 2,
            'log_thoughts': True,
            'log_timing': True
        }

    def _handle_step_duration_and_circuit_breaker(self, step_duration: float, circuit_breaker_count: int, step_num: int) -> int:
        """
        Handles checking step duration against threshold and manages the circuit breaker.
        Returns the updated circuit_breaker_count.
        Raises TimeoutError if the circuit breaker trips.
        """
        # If the step was not slow, return early without incrementing or checking the breaker.
        if not (step_duration > self.slow_step_threshold):
            return circuit_breaker_count

        # If we reach here, the step was slow.
        circuit_breaker_count += 1
        self.logger.warning(
            f"⚠️ Step {step_num} took {step_duration:.2f}s (threshold: {self.slow_step_threshold}s)")

        # Check if the circuit breaker should trip after incrementing the count.
        if circuit_breaker_count >= self.circuit_breaker_trips:
            self.logger.error(
                "❌ Circuit breaker tripped - too many slow steps")
            raise TimeoutError(
                "Sequential thinking circuit breaker activated")

        return circuit_breaker_count

    def _check_overall_timeout(self, start_time: float) -> None:
        """Checks if the overall thinking timeout has been exceeded."""
        if time.time() - start_time > self.overall_timeout:
            self.logger.error(
                f"❌ Overall thinking timeout exceeded ({self.overall_timeout}s)")
            raise TimeoutError(
                "Sequential thinking exceeded maximum duration")

    def _build_thinking_prompt(self, user_goal: str, toolbox_desc: str, current_step: int, history: List[Dict[str, Any]], phase_directive: str) -> str:
        """Builds the system prompt for a thinking step."""
        history_block = "\n".join(
            [f"Step {h['step']}: {h['thought']}" for h in history])

        return f"""
        You are a Sequential Thinking Engine. {phase_directive}

        Goal: {user_goal}
        Tools: {toolbox_desc}
        Current Step: {current_step+1}/{self.max_steps}

        PAST THOUGHTS:
        {history_block}

        INSTRUCTIONS:
        1. Analyze the goal and the past thoughts.
        2. Decide if you have enough information and clarity to write the final Python code.
        3. Output JSON ONLY:
        {{
            "thought": "Your analysis of the current situation and next step in the sequence.",
            "needs_more_thought": true/false (Set to false ONLY when the thought is sufficient to write the final code),
            "step": {current_step+1}
        }}
        """

    def _execute_thinking_step(self, system_prompt: str, raw_prompt: str, current_step: int, circuit_breaker_count: int) -> Tuple[Dict[str, Any], int, float]:
        """Executes a single LLM thinking step, handles timeouts and circuit breaker."""
        try:
            step_start = time.time()
            # [HARDENED 5c] Call LLM with dynamic temperature
            # Note: LLMClient doesn't support temperature parameter yet
            response = self.llm.generate_plan(system_prompt, raw_prompt)
            step_duration = time.time() - step_start

            circuit_breaker_count = self._handle_step_duration_and_circuit_breaker(
                step_duration, circuit_breaker_count, current_step + 1
            )
            return response, circuit_breaker_count, step_duration
        except TimeoutError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Cognitive Step Failed: {e}")
            raise RuntimeError(f"Cognitive step {current_step+1} failed: {str(e)}")

    def _process_thinking_step_result(self, session_id: str, user_goal: str, current_step: int, response: Dict[str, Any], step_duration: float, history: List[Dict[str, Any]]) -> Tuple[str, bool]:
        """Processes the LLM's thought response, updates history, and persists it."""
        thought = response.get("thought", "Analysis failed, proceeding to synthesis.")
        needs_more = response.get("needs_more_thought", True)

        self.logger.info(f"🤔 Step {current_step+1}: {thought[:120]}...")

        history.append({
            "step": current_step+1,
            "thought": thought,
            "timestamp": datetime.now().isoformat(),
            "duration": step_duration
        })

        if self.persist_history:
            self._save_thought_history(session_id, user_goal, history)

        return thought, needs_more

    def _handle_final_synthesis(self, session_id: str, user_goal: str, history: List[Dict[str, Any]], toolbox_desc: str) -> str:
        """Handles the final code synthesis and persistence."""
        self.logger.info("💡 EPIPHANY REACHED. Constructing Final Plan.")
        final_code = self._synthesize_code(user_goal, history, toolbox_desc)

        if self.persist_history:
            self._save_final_result(session_id, final_code)
        return final_code

    def think(self, user_goal: str, toolbox_desc: str) -> str:
        """
        Loops until the agent is satisfied with its plan.
        Returns the final generated Python code string.
        """
        start_time = time.time()
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.logger.info(
            f"🧠 STARTING SEQUENTIAL THINKING LOOP (Max {self.max_steps} Steps, {self.step_timeout}s timeout each)...")

        history: List[Dict[str, Any]] = []
        circuit_breaker_count = 0

        # Initial call is always the raw user goal
        raw_prompt = user_goal

        for i in range(self.max_steps):
            self._check_overall_timeout(start_time)

            # [HARDENED 5c] 1. Dynamic Hardening parameters
            current_temp = self._calculate_dynamic_temperature(i)
            phase_directive = self._get_system_directive(i)
            self.logger.debug(f"Step {i+1}/{self.max_steps} | Temp: {current_temp:.2f} | {phase_directive}")

            # Dynamic Prompt that evolves based on past thoughts
            system_prompt = self._build_thinking_prompt(user_goal, toolbox_desc, i, history, phase_directive)

            response, circuit_breaker_count, step_duration = self._execute_thinking_step(
                system_prompt, raw_prompt, i, circuit_breaker_count
            )

            thought, needs_more = self._process_thinking_step_result(
                session_id, user_goal, i, response, step_duration, history
            )

            if not needs_more:
                return self._handle_final_synthesis(session_id, user_goal, history, toolbox_desc)

            # Update the raw prompt for the next loop iteration
            raw_prompt = f"Previous thought: {thought}. Now, what is the next logical step?"

        self.logger.warning(
            f"⚠️ Max thinking steps ({self.max_steps}) reached. Synthesizing plan with current context.")
        return self._handle_final_synthesis(session_id, user_goal, history, toolbox_desc)

    def _validate_generated_code(self, code: str) -> None:
        """
        Validates the syntax and content of the generated Python code.
        Raises SyntaxError or ValueError on failure.
        """
        if not code.strip():
            raise ValueError("Generated code is empty or only whitespace.")
        ast.parse(code)  # This will raise SyntaxError if invalid

    def _build_synthesis_prompt(self, goal: str, thoughts: str, toolbox_desc: str, attempt: int, last_error: Optional[str]) -> str:
        """Helper to build the synthesis prompt, reducing nesting."""
        base_prompt = f"""
        Based on the following Goal and Thought Sequence, write the final, complete Python code.

        GOAL: {goal}

        CONTEXT (Thought Sequence):
        {thoughts}

        {toolbox_desc}

        CRITICAL RULES:
        - Write only ONE entry point function (e.g., 'run' or 'main').
        - NEVER use triple-quoted f-strings (\"\"\" or ''''). Use string concatenation or .format() instead.
        - ALL string literals must have matching opening and closing quotes.
        - Escape any internal quotes in strings with backslashes (\\\\").
        - Output valid Python code that will compile without syntax errors.
        - Output JSON ONLY: {{ "code": "..." }}

        EXAMPLE OF CORRECT STRING HANDLING:
        message = "Hello, " + name + "!"
        query = "SELECT * FROM users WHERE name = \\"" + user_name + "\\""

        EXAMPLE OF WHAT TO AVOID:
        message = "Hello, " + name + "  # Missing closing quote
        text = \"\"\"This is bad\"\"\"  # Triple quotes cause issues
        """

        if attempt > 0 and last_error:
            base_prompt += f"\n\nPREVIOUS ATTEMPT FAILED WITH SYNTAX ERROR:\n{last_error}\n\nPlease fix the syntax error and try again."

        return base_prompt

    def _attempt_code_synthesis_single_pass(self, goal: str, thoughts: str, toolbox_desc: str, attempt: int, last_error: Optional[str]) -> str:
        """Performs a single attempt at code synthesis, including LLM call and validation."""
        final_prompt = self._build_synthesis_prompt(goal, thoughts, toolbox_desc, attempt, last_error)

        try:
            final_response = self.llm.generate_plan(
                "You are a master coder. Use the context provided to write perfect code.",
                final_prompt
                # Note: LLMClient doesn't support temperature parameter yet
            )
        except Exception as e:
            self.logger.error(f"❌ LLM code synthesis failed: {e}")
            raise RuntimeError(f"LLM code synthesis failed: {str(e)}")

        code = final_response.get("code", "")

        self.logger.debug(f"Raw LLM response: {final_response}")
        self.logger.debug(f"Extracted code (first 500 chars): {code[:500] if code else 'EMPTY'}")

        self._validate_generated_code(code)
        return code

    def _synthesize_code(self, goal: str, history: List[Dict[str, Any]], toolbox_desc: str) -> str:
        """Ask the LLM to convert the sequential thought history into Final Python Code."""
        self.logger.info("✍️ Synthesizing final code from thought sequence...")
        thoughts = "\n".join(
            [f"Thought {h['step']}: {h['thought']}" for h in history])

        max_attempts = self.max_syntax_attempts
        last_error = None

        # [HARDENED 5c] Ensure synthesis uses low temp (0.0) for precision

        for attempt in range(max_attempts):
            try:
                code = self._attempt_code_synthesis_single_pass(goal, thoughts, toolbox_desc, attempt, last_error)
                self.logger.info("✅ Code syntax validation passed!")
                return code
            except (SyntaxError, ValueError, RuntimeError) as e:
                last_error = f"Validation/Synthesis error: {str(e)}"
                self.logger.warning(
                    f"⚠️ Code validation/synthesis failed (attempt {attempt + 1}): {last_error}")

        self.logger.error("❌ Max validation attempts reached. Raising exception.")
        raise RuntimeError(
            f"Failed to generate valid code after {max_attempts} attempts. Last error: {last_error}")

    def _save_thought_history(self, session_id: str, goal: str, history: List[Dict[str, Any]]) -> None:
        """Save thought history to disk for debugging."""
        try:
            history_file = self.history_dir / f"thoughts_{session_id}.json"
            data_to_save = {
                "session_id": session_id,
                "goal": goal,
                "timestamp": datetime.now().isoformat(),
                "history": history
            }
            with open(history_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save thought history: {e}")

    def _save_final_result(self, session_id: str, code: str) -> None:
        """Save the final generated code."""
        try:
            result_file = self.history_dir / f"result_{session_id}.py"
            content = (
                f"# Generated on {datetime.now().isoformat()}\n"
                f"# Session ID: {session_id}\n\n"
                f"{code}"
            )
            with open(result_file, 'w') as f:
                f.write(content)
        except Exception as e:
            self.logger.warning(f"Failed to save final result: {e}")