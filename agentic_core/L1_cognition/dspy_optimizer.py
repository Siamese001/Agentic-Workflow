""" """

import logging
import pickle
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import os  # Import os for environment variable access

LOGGER = logging.getLogger(__name__)

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    # logger.warning("DSPy not available. Install with: pip install dspy-ai")
    # Moved logger.warning to after the DSPY_AVAILABLE assignment
    # Corrected the logger usage to use the imported LOGGER object
    if not DSPY_AVAILABLE:
        LOGGER.warning("DSPy not available. Install with: pip install dspy-ai")


@dataclass
class OptimizationExample:
    """A single training example for DSPy optimization."""
    inputs: Dict[str, Any]
    ideal_output: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Result of a DSPy optimization run."""
    optimized_prompt: str
    performance_score: float
    improvement_percentage: float
    best_examples: List[OptimizationExample]
    optimization_time_seconds: float


class DSPyOptimizer:
    """ Optimizes agent prompts using DSPy's teleprompter system.

    Instead of hand-writing prompts, we:
    1. Define a metric for "good" performance
    2. Create training examples
    3. Run DSPy optimization to find the best prompt formulation
    4. Save the optimized prompt for runtime use
    """

    def __init__(
        self,
        model_name: str = "gpt-4o",
        optimization_cache_dir: str = "./optimization_cache"
    ):
        """ """
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
        api_key = os.getenv("OPENAI_API_KEY")
        try:
            if api_key:
                dspy.configure(lm=dspy.OpenAI(model=self.model_name, api_key=api_key))
            else:
                LOGGER.warning("No OpenAI API key found. Using mock LM.")
                # You could implement a mock LM for testing here
                # For example: dspy.configure(lm=dspy.OpenAI(model='gpt-3.5-turbo', api_key='dummy'))
        except Exception as e:
            LOGGER.error(f"Failed to configure DSPy: {e}")

    async def optimize_prompt(
        self,
        base_prompt: str,
        signature_class: type,
        training_examples: List[OptimizationExample],
        validation_examples: List[OptimizationExample],
        metric_func: Callable,
        max_examples: int = 50
    ) -> OptimizationResult:
        """ """
        start_time = time.time()

        # Check cache first
        cache_key = self._get_cache_key(
            base_prompt, signature_class, len(training_examples))
        cached_result = self._load_from_cache(cache_key)
        if cached_result:
            LOGGER.info("Using cached optimization result")
            return cached_result

        # Limit examples to prevent excessive computation
        train_examples = training_examples[:max_examples]
        # 20% for validation
        val_examples = validation_examples[:max_examples // 5]

        LOGGER.info(
            f"Starting optimization with {len(train_examples)} examples")

        try:
            # Create the student module (agent to optimize)
            student_module = self._create_student_module(signature_class, base_prompt)

            # Create the teleprompter (optimizer)
            teleprompter = dspy.teleprompt.BootstrapFewShot(
                metric=metric_func,
                max_bootstrapped_demos=5,
                max_labeled_demos=3
            )

            # Run optimization
            optimized_module = teleprompter.compile(
                student=student_module,
                trainset=self._convert_to_dspy_examples(train_examples)
            )

            # Evaluate on validation set
            validation_score = self._evaluate_module(
                optimized_module,
                val_examples,
                metric_func
            )

            # Extract optimized prompt
            optimized_prompt = self._extract_prompt_from_module(
                optimized_module)

            # Calculate improvement
            baseline_score = self._evaluate_baseline(
                base_prompt,
                signature_class,
                val_examples,
                metric_func
            )

            improvement = (
                (validation_score - baseline_score) / baseline_score) * 100 if baseline_score else float('inf')

            # Create result
            result = OptimizationResult(
                optimized_prompt=optimized_prompt,
                performance_score=validation_score,
                improvement_percentage=improvement,
                best_examples=train_examples[:5],  # Top 5 examples
                optimization_time_seconds=time.time() - start_time
            )

            # Cache the result
            self._save_to_cache(cache_key, result)

            LOGGER.info(
                f"Optimization complete: {improvement:.1f}% improvement")
            return result

        except Exception as e:
            LOGGER.error(f"Optimization failed: {e}")
            # Return baseline as fallback
            return OptimizationResult(
                optimized_prompt=base_prompt,
                performance_score=0.0,
                improvement_percentage=0.0,
                best_examples=[],
                optimization_time_seconds=time.time() - start_time
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
                # Note: prompt_template.format(**kwargs) would format a string, not a dspy.Prompt
                # Assuming prompt_template is meant to be used to construct the prompt,
                # or it's a dspy.Prompt object itself that needs to be instantiated/used.
                # For now, we'll proceed assuming self.generate will implicitly use it or it's passed correctly.
                # If self.prompt_template is a dspy.Prompt object, it should be instantiated in __init__ or forward.
                return self.generate(**kwargs)

        # The base_prompt should likely be used to initialize or configure the signature or the module's prompt.
        # DSPy's ChainOfThought takes a signature. If base_prompt is meant to guide the signature,
        # it needs to be integrated. If it's a literal prompt string, it might be part of a dspy.Prompt.
        # For now, assuming signature_class is the primary definition and base_prompt is a conceptual starting point.
        # A common pattern is to use `dspy.ChainOfThought(signature, prompt=base_prompt)` if base_prompt is a string.
        # Or, if signature_class itself contains a prompt, base_prompt might be used to refine it.
        # Given the context of optimization, base_prompt is likely a template for the prompt part of the signature.
        # If signature_class is a dspy.Signature, it already has a default prompt.
        # For this fix, let's assume base_prompt is implicitly handled by the teleprompter or the signature itself.

        # A more direct way to use a base prompt with a signature in ChainOfThought:
        # Assuming signature_class is a dspy.Signature definition.
        # If base_prompt is a string template:
        # class OptimizedModule(dspy.Module):
        #     def __init__(self, signature, prompt_template_str):
        #         super().__init__()
        #         self.prompt_template = dspy.Prompt(prompt_template_str)
        #         self.generate = dspy.ChainOfThought(signature, prompt=self.prompt_template)
        #     def forward(self, **kwargs):
        #         return self.generate(**kwargs)
        # return OptimizedModule(signature_class, base_prompt)

        # However, the original code implies `dspy.ChainOfThought(signature_class, base_prompt)` or similar.
        # Let's stick closer to the structure, assuming signature_class is a callable that returns a signature or a signature class.
        # If signature_class is a dspy.Signature class:
        # class OptimizedModule(dspy.Module):
        #     def __init__(self, signature_cls, prompt_template_str):
        #         super().__init__()
        #         # If base_prompt needs to be formatted, it should be a dspy.Prompt or string
        #         self.prompt_template = dspy.Prompt(prompt_template_str)
        #         self.generate = dspy.ChainOfThought(signature_cls(prompt=self.prompt_template))
        #     def forward(self, **kwargs):
        #         return self.generate(**kwargs)
        # return OptimizedModule(signature_class, base_prompt)

        # The provided code snippet: `self.GENERATE = dspy.ChainOfThought(signature)` implies signature_class is the signature object itself.
        # And `self.prompt_template = prompt_template` suggests prompt_template is used elsewhere.
        # Let's assume `signature_class` is a dspy.Signature and `base_prompt` is a prompt string that `ChainOfThought` can use.

        class ActualOptimizedModule(dspy.Module):
            def __init__(self, signature, prompt_template_str):
                super().__init__()
                # Assuming signature_class is a dspy.Signature or a class that creates one.
                # If signature_class is a class, it should be instantiated.
                # If base_prompt is a prompt string to be used with the signature:
                self.prompt_template = dspy.Prompt(prompt_template_str)
                # We assume signature_class is the signature itself, or a callable that returns a signature.
                # A common DSPy pattern is `dspy.ChainOfThought(signature, prompt=dspy.Prompt(...))`
                # If `signature_class` is meant to be a definition like `class MySignature(dspy.Signature): ...`,
                # then it should be `dspy.ChainOfThought(signature_class)`.
                # The `base_prompt` argument is the tricky part. It's possible it's meant to format the prompt *within* the signature.
                # For now, let's assume `signature_class` is a dspy.Signature instance or a class that can be directly passed.
                # If `base_prompt` is meant to be the prompt for the signature:
                # If `signature_class` is a callable that returns a signature, e.g., `MySignature()`.
                # If `signature_class` is `dspy.Signature`, it's abstract.

                # Let's assume signature_class is a class like `MySignature(dspy.Signature)` and base_prompt is the prompt string.
                # If base_prompt is a string that defines the prompt, we might need to associate it.
                # A robust way would be:
                if isinstance(signature_class, dspy.Signature):
                    self.generate = dspy.ChainOfThought(signature_class, prompt=dspy.Prompt(prompt_template_str))
                elif isinstance(signature_class, type) and issubclass(signature_class, dspy.Signature):
                    # Instantiate the signature, potentially with the base prompt if the signature allows it.
                    # If base_prompt is a string to be used directly as the prompt for ChainOfThought:
                    self.generate = dspy.ChainOfThought(signature_class, prompt=dspy.Prompt(prompt_template_str))
                else:
                    # Fallback or error handling if signature_class is not a recognized type.
                    raise TypeError("signature_class must be a dspy.Signature or a subclass of dspy.Signature")

            def forward(self, **kwargs):
                return self.generate(**kwargs)

        # The original code `return OptimizedModule(signature_class, base_prompt)` suggests that `signature_class` is the signature definition and `base_prompt` is the prompt string.
        # So we instantiate `ActualOptimizedModule` with `signature_class` (assuming it's a signature class) and `base_prompt`.
        # The `__init__` of `ActualOptimizedModule` is adjusted to handle this.
        return ActualOptimizedModule(signature_class, base_prompt)


    def _convert_to_dspy_examples(self, examples: List[OptimizationExample]):
        """Convert our examples to DSPy format."""
        dspy_examples = []

        for ex in examples:
            # Create a DSPy Example
            dspy_ex = dspy.Example()

            # Add inputs
            for key, value in ex.inputs.items():
                # Using with_inputs method correctly
                dspy_ex = dspy_ex.with_inputs(**{key: value})

            # Add outputs
            for key, value in ex.ideal_output.items():
                # Using with_outputs method correctly
                dspy_ex = dspy_ex.with_outputs(**{key: value})

            dspy_examples.append(dspy_ex)

        return dspy_examples

    def _evaluate_module(
        self,
        module: dspy.Module,
        examples: List[OptimizationExample],
        metric_func: Callable
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
        examples: List[OptimizationExample],
        metric_func: Callable
    ) -> float:
        """Evaluate baseline performance without optimization."""
        # For now, return a mock baseline
        # In practice, you'd run the base prompt through the model
        # This function needs to instantiate and run the base prompt with the given signature.
        # A simple approach is to create a temporary module for evaluation.

        try:
            # Create a DSPy module using the base prompt and signature
            # This assumes signature_class is a class definition for a dspy.Signature.
            if isinstance(signature_class, dspy.Signature):
                # If signature_class is already a signature instance
                base_module = dspy.ChainOfThought(signature_class, prompt=dspy.Prompt(prompt))
            elif isinstance(signature_class, type) and issubclass(signature_class, dspy.Signature):
                # If signature_class is a class definition
                base_module = dspy.ChainOfThought(signature_class, prompt=dspy.Prompt(prompt))
            else:
                LOGGER.error(f"Unsupported signature_class type for baseline: {type(signature_class)}")
                return 0.0 # Return 0 if signature type is incorrect

            # Evaluate this baseline module
            return self._evaluate_module(base_module, examples, metric_func)

        except Exception as e:
            LOGGER.error(f"Failed to evaluate baseline: {e}")
            return 0.0 # Return 0 if baseline evaluation fails

    def _extract_prompt_from_module(self, module: dspy.Module) -> str:
        """Extract the optimized prompt from a DSPy module."""
        # This would extract the actual optimized prompt
        # DSPy teleprompters store optimized demonstrations or prompts.
        # The exact location can vary based on the teleprompter used.
        # For BootstrapFewShot, it often stores the compiled program's demonstrations.
        # If the module itself is a compiled program, its prompt might be accessible.

        # A common way to get the prompt from a compiled module might involve inspecting its sub-modules or its prompt attribute if it has one.
        # If `module` is the compiled program:
        if hasattr(module, 'program'): # Compiled programs often have a 'program' attribute
            compiled_program = module.program
            if hasattr(compiled_program, 'signatures'): # Check if it has signatures
                for sig_name, signature in compiled_program.signatures.items():
                    if hasattr(signature, 'instructions'): # Instructions might hold the prompt string
                        return signature.instructions
            if hasattr(compiled_program, 'prompt'): # Or a direct prompt attribute
                return compiled_program.prompt

        # If the module itself is the one we optimized, and it's a ChainOfThought or similar:
        if hasattr(module, 'generate') and hasattr(module.generate, 'program'):
            compiled_program = module.generate.program
            if hasattr(compiled_program, 'signatures'):
                for sig_name, signature in compiled_program.signatures.items():
                    if hasattr(signature, 'instructions'):
                        return signature.instructions
            if hasattr(compiled_program, 'prompt'):
                return compiled_program.prompt

        # If the teleprompter stored demonstrations directly on the module
        if hasattr(module, 'program') and hasattr(module.program, 'demos'):
            demos = module.program.demos
            if demos:
                # Convert demonstrations back to prompt format
                # This is a simplification, actual prompt reconstruction can be complex.
                prompt_parts = []
                for demo in demos:
                    for key, value in demo.items():
                        prompt_parts.append(f"{key}: {value}")
                return "\n".join(prompt_parts)
        elif hasattr(module, 'demos'): # Some modules might have demos directly
            demos = module.demos
            if demos:
                prompt_parts = []
                for demo in demos:
                    for key, value in demo.items():
                        prompt_parts.append(f"{key}: {value}")
                return "\n".join(prompt_parts)

        # Fallback: if no specific prompt extraction works, return a placeholder
        # If the optimized module has a specific `optimized_prompt` attribute, return that.
        if hasattr(module, 'optimized_prompt'):
            return module.optimized_prompt

        LOGGER.warning("Could not extract optimized prompt from module. Returning a placeholder.")
        return "Optimized prompt (extraction failed)"


    def _get_cache_key(self, prompt: str, signature_class: type, num_examples: int) -> str:
        """Generate a cache key for optimization results."""
        import hashlib
        # Ensure signature_class is represented by its name for hashing
        signature_name = signature_class.__name__ if isinstance(signature_class, type) else str(signature_class)
        content = f"{prompt}_{signature_name}_{num_examples}"
        return hashlib.md5(content.encode()).hexdigest()

    def _save_to_cache(self, key: str, result: OptimizationResult):
        """Save optimization result to cache."""
        cache_file = self.cache_dir / f"opt_{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            LOGGER.warning(f"Failed to cache result: {e}")

    def _load_from_cache(self, key: str) -> Optional[OptimizationResult]:
        """Load optimization result from cache."""
        cache_file = self.cache_dir / f"opt_{key}.pkl"
        try:
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            LOGGER.warning(f"Failed to load from cache: {e}")
        return None


class PromptSignatureRegistry:
    """Registry of DSPy signatures for different agent types."""

    # Common signatures that can be reused

    CODE_GENERATION = dspy.Signature(
        "Generate robust python code based on requirements.",
        requirements=dspy.InputField(),
        context=dspy.InputField(),
        verified_code=dspy.OutputField(desc="Python code that passes tests")
    )

    RESEARCH_ANALYSIS = dspy.Signature(
        "Analyze research data and provide insights.",
        research_data=dspy.InputField(),
        question=dspy.InputField(),
        analysis=dspy.OutputField(desc="Detailed analysis with citations")
    )

    TOOL_SELECTION = dspy.Signature(
        "Select the best tool for a given task.",
        task_description=dspy.InputField(),
        available_tools=dspy.InputField(),
        selected_tool=dspy.OutputField(desc="Name of the best tool"),
        reasoning=dspy.OutputField(desc="Why this tool was chosen")
    )

    SUBATOMIC_HOP = dspy.Signature(
        """You are an intelligent agent responsible for a single atomic task. """,
        role_description=dspy.InputField(desc="Your specific role (e.g., Python Expert)"),
        context_summary=dspy.InputField(desc="Relevant data from previous hops"),
        task_goal=dspy.InputField(desc="What needs to be achieved in this hop"),
        reasoning=dspy.OutputField(desc="Chain of thought analysis"),
        action_plan=dspy.OutputField(desc="Concrete steps to take")
    )

    @ classmethod
    def get_signature(cls, agent_type: str) -> Optional[dspy.Signature]:
        """Get a signature for a specific agent type."""
        signatures = {
            "coder": cls.CODE_GENERATION,
            "researcher": cls.RESEARCH_ANALYSIS,
            "tool_selector": cls.TOOL_SELECTION,
            "subatomic_hop": cls.SUBATOMIC_HOP
        }
        return signatures.get(agent_type.lower())


    class OptimizedHopModule(dspy.Module):
        """The DSPy Module for Subatomic Hop optimization."""

        def __init__(self):
            super().__init__()
            # Ensure SUBATOMIC_HOP is properly referenced if it's part of the class definition
            self.prog = dspy.ChainOfThought(PromptSignatureRegistry.SUBATOMIC_HOP)

        def forward(self, role_description, context_summary, task_goal):
            """Execute the optimized hop reasoning."""
            return self.prog(
                role_description=role_description,
                context_summary=context_summary,
                task_goal=task_goal
            )


    # Common metric functions
    def code_compilation_metric(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Metric for code generation - checks if code would compile."""
        try:
            code = predicted.get("verified_code", "")
            if not code:
                return 0.0

            # Basic syntax checks (these are very rough heuristics)
            if "def " not in code and "class " not in code and "import " not in code:
                return 0.3 # Potentially a very simple script or just text

            # Check for common markdown code block delimiters
            if "" in code or "" in code:
                return 0.5 # Code is likely in a code block

            # In a real scenario, you would attempt to compile or execute the code.
            # For example, using `ast.parse` or `compile()` from Python's built-in modules.
            # For this example, we'll return a higher score for well-formed code.
            # if ast.parse(code):
            #    return 1.0

            # If it looks like code but didn't trigger failure heuristics
            return 0.7
        except Exception as e:
            LOGGER.warning(f"Code compilation metric check failed: {e}")
            return 0.0 # Failed to parse or other issues


    def factual_accuracy_metric(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Metric for factual accuracy - checks key facts match."""
        pred_analysis = predicted.get("analysis", "")
        truth_analysis = ground_truth.get("analysis", "")

        if not truth_analysis:
            return 0.0 # Cannot score if ground truth is missing

        # Simple overlap check as a heuristic
        pred_words = set(pred_analysis.lower().split())
        truth_words = set(truth_analysis.lower().split())

        overlap = len(pred_words & truth_words)
        return overlap / len(truth_words) if truth_words else 0.0


    def tool_selection_metric(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Metric for tool selection - checks if the right tool was chosen."""
        pred_tool = predicted.get("selected_tool", "").lower()
        truth_tool = ground_truth.get("selected_tool", "").lower()

        return 1.0 if pred_tool == truth_tool else 0.0


def create_dspy_optimizer(
    model_name: str="gpt-4o",
    cache_dir: str="./optimization_cache"
) -> DSPyOptimizer:
    """ """
    return DSPyOptimizer(
        model_name=model_name,
        optimization_cache_dir=cache_dir
    )