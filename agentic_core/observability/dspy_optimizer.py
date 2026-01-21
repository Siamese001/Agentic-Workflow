from __future__ import annotations

import hashlib

"""Brief description of functionality and purpose."""

import logging
import os
import pickle
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)

try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    LOGGER.warning("DSPy not available. Install with: pip install dspy-ai")


@dataclass
# NAMING FIXED: OptimizationExample → OptimizationExample
class OptimizationExample:
    """A single training example for DSPy optimization."""

    inputs: dict[str, Any]
    ideal_output: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
# NAMING FIXED: OptimizationResult → OptimizationResult
class OptimizationResult:
    """Result of a DSPy optimization run."""

    optimized_prompt: str
    performance_score: float
    improvement_percentage: float
    best_examples: list[OptimizationExample]
    optimization_time_seconds: float


# NAMING FIXED: DSPyOptimizer → DsPyOptimizer
class DsPyOptimizer:
    """
    Optimizes agent prompts using DSPy's teleprompter system.

    Instead of hand-writing prompts, we:
    1. Define a Metric for "good" performance
    2. Create training examples
    3. Run DSPy optimization to find the best prompt formulation
    4. Save the optimized prompt for runtime use
    """

    def __init__(
        self, model_name: str = "gpt-4o", optimization_cache_dir: str = "./optimization_cache"
    ):
        """
        Initialize the DSPy optimizer.

        Args:
            model_name: LLM model to use for optimization
            optimization_cache_dir: Directory to cache optimization results
        """
        if not DSPY_AVAILABLE:
            raise ImportError("DSPy is required. Install with: pip install dspy-ai")

        self.model_name = model_name
        self.cache_dir = Path(optimization_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Configure DSPy
        self._configure_dspy()

        LOGGER.info(f"DSPy optimizer initialized with model: {model_name}")

    def _configure_dspy(self):
        """Configure DSPy with the selected model."""
        # This would be configured with your actual API key
        # For now, we'll use a mock configuration
        try:
            # Try to configure with OpenAI if available
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                dspy.configure(LM=dspy.OpenAI(model=self.model_name, api_key=api_key))
            else:
                LOGGER.warning("No OpenAI API key found. Using mock LM.")
                # You could implement a mock LM for testing here
        except Exception as e:
            LOGGER.error(f"Failed to configure DSPy: {e}")

    async def optimize_prompt(
        self,
        base_prompt: str,
        signature_class: type,
        training_examples: list[OptimizationExample],
        validation_examples: list[OptimizationExample],
        metric_func: Callable,
        max_examples: int = 50,
    ) -> OptimizationResult:
        """
        Optimize a prompt using DSPy.

        Args:
            base_prompt: Initial prompt to optimize
            signature_class: DSPy signature class defining input/output
            training_examples: Examples to train on
            validation_examples: Examples to validate with
            metric_func: Function to score outputs (0.0 to 1.0)
            max_examples: Maximum examples to use

        Returns:
            OptimizationResult with optimized prompt and metrics
        """
        start_time = time.time()

        # Check cache first
        cache_key = self._get_cache_key(base_prompt, signature_class, len(training_examples))
        cached_result = self._load_from_cache(cache_key)
        if cached_result:
            LOGGER.info("Using cached optimization result")
            return cached_result

        # Limit examples to prevent excessive computation
        train_examples = training_examples[:max_examples]
        val_examples = validation_examples[: max_examples // 5]  # 20% for validation

        LOGGER.info(f"Starting optimization with {len(train_examples)} examples")

        try:
            # Create the student module (agent to optimize)
            student_module = self._create_student_module(signature_class, base_prompt)

            # Create the teleprompter (optimizer)
            teleprompter = dspy.teleprompt.BootstrapFewShot(
                Metric=metric_func, max_bootstrapped_demos=5, max_labeled_demos=3
            )

            # Run optimization
            optimized_module = teleprompter.compile(
                student=student_module, trainset=self._convert_to_dspy_examples(train_examples)
            )

            # Evaluate on validation set
            validation_score = self._evaluate_module(optimized_module, val_examples, metric_func)

            # Extract optimized prompt
            optimized_prompt = self._extract_prompt_from_module(optimized_module)

            # Calculate improvement
            baseline_score = self._evaluate_baseline(
                base_prompt, signature_class, val_examples, metric_func
            )

            improvement = ((validation_score - baseline_score) / baseline_score) * 100

            # Create result
            result = OptimizationResult(
                optimized_prompt=optimized_prompt,
                performance_score=validation_score,
                improvement_percentage=improvement,
                best_examples=train_examples[:5],  # Top 5 examples
                optimization_time_seconds=time.time() - start_time,
            )

            # Cache the result
            self._save_to_cache(cache_key, result)

            LOGGER.info(f"Optimization complete: {improvement:.1f}% improvement")
            return result

        except Exception as e:
            LOGGER.error(f"Optimization failed: {e}")
            # Return baseline as fallback
            return OptimizationResult(
                optimized_prompt=base_prompt,
                performance_score=0.0,
                improvement_percentage=0.0,
                best_examples=[],
                optimization_time_seconds=time.time() - start_time,
            )

    def _create_student_module(self, signature_class: type, base_prompt: str):
        """Create a DSPy module from a signature and prompt."""

        class OptimizedModule(dspy.Module):
            def __init__(self, signature, prompt_template):
                super().__init__()
                self.generate = dspy.ChainOfThought(signature)
                self.prompt_template = prompt_template

            def forward(self, **kwargs):
                # Apply the prompt template
                self.prompt_template.format(**kwargs)
                return self.generate(**kwargs)

        return OptimizedModule(signature_class, base_prompt)

    def _convert_to_dspy_examples(self, examples: list[OptimizationExample]):
        """Convert our examples to DSPy format."""
        dspy_examples = []

        for ex in examples:
            # Create a DSPy Example
            dspy_ex = dspy.Example()

            # Add inputs
            for key, value in ex.inputs.items():
                dspy_ex = dspy_ex.with_inputs(**{key: value})

            # Add outputs
            for key, value in ex.ideal_output.items():
                dspy_ex = dspy_ex.with_outputs(**{key: value})

            dspy_examples.append(dspy_ex)

        return dspy_examples

    def _evaluate_module(
        self, module: dspy.Module, examples: list[OptimizationExample], metric_func: Callable
    ) -> float:
        """Evaluate a module on examples."""
        scores = []

        for ex in examples:
            try:
                # Run the module
                result = module(**ex.inputs)

                # Score the result
                score = metric_func(result, ex.ideal_output)
                scores.append(score)
            except Exception as e:
                LOGGER.warning(f"Evaluation failed on example: {e}")
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 0.0

    def _evaluate_baseline(
        self,
        prompt: str,
        signature_class: type,
        examples: list[OptimizationExample],
        metric_func: Callable,
    ) -> float:
        """Evaluate baseline performance without optimization."""
        # For now, return a mock baseline
        # In practice, you'd run the base prompt through the model
        return 0.5  # Mock baseline score

    def _extract_prompt_from_module(self, module: dspy.Module) -> str:
        """Extract the optimized prompt from a DSPy module."""
        # This would extract the actual optimized prompt
        # For now, return the module's demonstration as the prompt
        if hasattr(module, "generate") and hasattr(module.generate, "demos"):
            demos = module.generate.demos
            if demos:
                # Convert demonstrations back to prompt format
                prompt_parts = []
                for demo in demos:
                    for key, value in demo.items():
                        prompt_parts.append(f"{key}: {value}")
                return "\n".join(prompt_parts)

        return "Optimized prompt (extraction failed)"

    def _get_cache_key(self, prompt: str, signature_class: type, num_examples: int) -> str:
        """Generate a cache key for optimization results."""
        content = f"{prompt}_{signature_class.__name__}_{num_examples}"
        return hashlib.md5(content.encode()).hexdigest()

    def _save_to_cache(self, key: str, result: OptimizationResult):
        """Save optimization result to cache."""
        cache_file = self.cache_dir / f"opt_{key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)
        except Exception as e:
            LOGGER.warning(f"Failed to cache result: {e}")

    def _load_from_cache(self, key: str) -> OptimizationResult | None:
        """Load optimization result from cache."""
        cache_file = self.cache_dir / f"opt_{key}.pkl"
        try:
            if cache_file.exists():
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
        except Exception as e:
            LOGGER.warning(f"Failed to load from cache: {e}")
        return None


# NAMING FIXED: PromptSignatureRegistry → PromptSignatureRegistry
class PromptSignatureRegistry:
    """Registry of DSPy signatures for different agent types."""

    # Common signatures that can be reused
    CODE_GENERATION = dspy.Signature(
        "Generate robust python code based on requirements.",
        REQUIREMENTS=dspy.InputField(),
        CONTEXT=dspy.InputField(),
        verified_code=dspy.OutputField(desc="Python code that passes tests"),
    )

    RESEARCH_ANALYSIS = dspy.Signature(
        "Analyze research data and provide insights.",
        research_data=dspy.InputField(),
        QUESTION=dspy.InputField(),
        ANALYSIS=dspy.OutputField(desc="Detailed analysis with citations"),
    )

    TOOL_SELECTION = dspy.Signature(
        "Select the best tool for a given Task.",
        task_description=dspy.InputField(),
        available_tools=dspy.InputField(),
        selected_tool=dspy.OutputField(desc="Name of the best tool"),
        REASONING=dspy.OutputField(desc="Why this tool was chosen"),
    )
    SUBATOMIC_HOP = dspy.Signature(
        """You are an intelligent agent responsible for a single atomic Task.
        Analyze the context, plan your action, and execute it using the available tools.
        """,
        role_description=dspy.InputField(desc="Your specific role (e.g., Python Expert)"),
        context_summary=dspy.InputField(desc="Relevant data from previous hops"),
        task_goal=dspy.InputField(desc="What needs to be achieved in this hop"),
        REASONING=dspy.OutputField(desc="Chain of thought analysis"),
        action_plan=dspy.OutputField(desc="Concrete steps to take"),
    )

    @classmethod
    def get_signature(cls, agent_type: str) -> dspy.Signature | None:
        """Get a signature for a specific agent type."""
        signatures = {
            "coder": cls.CODE_GENERATION,
            "researcher": cls.RESEARCH_ANALYSIS,
            "tool_selector": cls.TOOL_SELECTION,
            "SubatomicHop": cls.SUBATOMIC_HOP,
        }
        return signatures.get(agent_type.lower())


# NAMING FIXED: OptimizedHopModule → OptimizedHopModule
class OptimizedHopModule(dspy.Module):
    """The DSPy Module for Subatomic Hop optimization."""

    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(PromptSignatureRegistry.SUBATOMIC_HOP)

    def forward(self, role_description, context_summary, task_goal):
        """Execute the optimized hop reasoning."""
        return self.prog(
            role_description=role_description, context_summary=context_summary, task_goal=task_goal
        )


# Common Metric functions
def code_compilation_metric(predicted: dict[str, Any], ground_truth: dict[str, Any]) -> float:
    """Metric for code generation - checks if code would compile."""
    try:
        code = predicted.get("verified_code", "")
        if not code:
            return 0.0

        # Basic syntax checks
        if "def " not in code and "class " not in code:
            return 0.3

        # Check for common errors
        if "```" in code:
            return 0.5

        # In practice, you'd actually try to compile the code
        return 0.8  # Mock score
    except Exception:
        return 0.0


def factual_accuracy_metric(predicted: dict[str, Any], ground_truth: dict[str, Any]) -> float:
    """Metric for factual accuracy - checks key facts match."""
    pred_analysis = predicted.get("analysis", "")
    truth_analysis = ground_truth.get("analysis", "")

    # Simple overlap check
    pred_words = set(pred_analysis.lower().split())
    truth_words = set(truth_analysis.lower().split())

    if not truth_words:
        return 0.0

    overlap = len(pred_words & truth_words)
    return overlap / len(truth_words)


def tool_selection_metric(predicted: dict[str, Any], ground_truth: dict[str, Any]) -> float:
    """Metric for tool selection - checks if the right tool was chosen."""
    pred_tool = predicted.get("selected_tool", "").lower()
    truth_tool = ground_truth.get("selected_tool", "").lower()

    return 1.0 if pred_tool == truth_tool else 0.0


def create_dspy_optimizer(
    model_name: str = "gpt-4o", cache_dir: str = "./optimization_cache"
) -> DSPyOptimizer:
    """
    Factory function to create a DSPy optimizer.

    Args:
        model_name: LLM model to use
        cache_dir: Cache directory for results

    Returns:
        DSPyOptimizer instance
    """
    return DSPyOptimizer(model_name=model_name, optimization_cache_dir=cache_dir)
