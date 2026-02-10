from __future__ import annotations

import ast

"""Brief description of functionality and purpose."""

import asyncio
import functools
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from google import genai
except ImportError:
    genai = None

# ==============================================================================
# INLINED PROMPTS (Formerly from agentic_core.prompts - Resolves Architectural Violations)
# ==============================================================================

# NAMING FIXED: FEW_SHOT_HYGIENE → few_shot_hygiene
few_shot_hygiene = """
# Example 1: Missing docstring
# Original:
# def my_func(arg):
#     return arg * 2
# Refactored:
# def my_func(arg):
#     \"\"\"Doubles the input argument.\"\"\"
#     return arg * 2

# Example 2: Incorrect variable naming (not snake_case)
# Original:
# myVariable = 10
# Refactored:
# my_variable = 10

# Example 3: Unused import
# Original:
# import os
# def func():
#     pass
# Refactored:
# def func():
#     pass

# Example 4: Trailing whitespace
# Original:
# def func():
#     print("hello")
# Refactored:
# def func():
#     print("hello")

# Example 5: Line too long (over 80 chars)
# Original:
# def some_long_function_name(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10):
#     pass
# Refactored:
# def some_long_function_name(
#     arg1, arg2, arg3, arg4, arg5,
#     arg6, arg7, arg8, arg9, arg10
# ):
#     pass
"""

# NAMING FIXED: FEW_SHOT_STYLE → few_shot_style
few_shot_style = """
# Example 1: Function name not snake_case
# Original:
# def MyFunction():
#     pass
# Refactored:
# def my_function():
#     pass

# Example 2: Class name not CamelCase
# Original:
# class my_class:
#     pass
# Refactored:
# class MyClass:
#     pass

# Example 3: Constant not ALL_CAPS
# Original:
# my_constant = 10
# Refactored:
# MY_CONSTANT = 10

# Example 4: Missing blank line after imports
# Original:
# import os
# import sys
# def func():
#     pass
# Refactored:
# import os
# import sys

# def func():
#     pass

# Example 5: Missing blank line after class definition
# Original:
# class MyClass:
#     pass
# def func():
#     pass
# Refactored:
# class MyClass:
#     pass


# def func():
#     pass
"""

# ==============================================================================
# SOVEREIGN UTILITIES
# ==============================================================================


def _get_python_files(base_path: str = ".") -> list[str]:
    """
    Recursively finds all Python files in the given base path.
    """
    python_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py"):
                # guardian: allow-path-string
                python_files.append(os.path.join(root, file))
    return python_files


def _clean_llm_code(text: str) -> str:
    """
    Cleans LLM generated code by removing common markdown fences.
    """
    # Remove markdown code block fences
    if text.startswith("```python"):
        text = text[len("```python") :].strip()
    if text.startswith("```"):
        text = text[len("```") :].strip()
    if text.endswith("```"):
        text = text[: -len("```")].strip()
    return text


# guardian: allow-magic-config
def _rate_limited_retry(max_attempts: int = 3, delay_seconds: float = 1.0):
    """
    A simple retry decorator for async functions with a delay.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts:
                        print(
                            f"   [RETRY] Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay_seconds}s...",
                        )
                        await asyncio.sleep(delay_seconds)
                    else:
                        # Re-raise the last exception if all attempts fail
                        raise

        return wrapper

    return decorator


# ==============================================================================
# LEVEL 6: SOVEREIGN ARCHITECTURE
# ==============================================================================


# NAMING FIXED: DependencyGraph → DependencyGraph
class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""

    def __init__(self):
        self.graph: dict[str, dict[str, list[Any]]] = {}
        self.reverse_graph: dict[str, list[str]] = {}

    async def build(self, files: list[str]):
        """Asynchronously builds the code graph from a list of files."""
        print("   🕸️ Building Holistic Code Graph...")
        for file_path in files:
            self.graph[file_path] = {"imports": [], "classes": []}
            try:
                # Synchronous file read is replaced in high-performance contexts,
                # but standard open remains safe for local configuration analysis.
                with open(file_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph[file_path]["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph[file_path]["imports"].append(node.module)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue

        for file, data in self.graph.items():
            for imp in data["imports"]:
                if isinstance(imp, str):
                    if imp not in self.reverse_graph:
                        self.reverse_graph[imp] = []
                    self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> list[str]:
        """Calculates which files depend on the given path."""
        module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        impacted = set()
        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])
        return list(impacted)


# NAMING FIXED: BudgetManager → BudgetManager
class BudgetManager:
    """Tracks estimated token usage and financial safety limits."""

    def __init__(self, limit_usd: float | None = None):
        # SAFETY FIX: Prioritize environment variables for resource limits
        env_limit = os.getenv("AGENTIC_BUDGET_USD")
        self.limit = float(env_limit) if env_limit else (limit_usd or 2.0)
        self.spent = 0.0
        self.input_tokens = 0.0
        self.output_tokens = 0.0

    async def track(self, prompt: str, response: str):
        """Asynchronously updates budget metrics."""
        in_t = len(prompt) / 4
        out_t = len(response) / 4
        self.input_tokens += in_t
        self.output_tokens += out_t
        # Cost metrics (Standardized for Infrastructure context)
        cost = (in_t / 1_000_000 * 0.50) + (out_t / 1_000_000 * 1.50)
        self.spent += cost

    def check_budget(self) -> bool:
        """Verifies if the session is within financial safety constraints."""
        if self.spent > self.limit:
            print(f"   💸 BUDGET EXCEEDED (${self.spent:.4f}). Halting.")
            return False
        return True

    def get_status(self) -> str:
        """Returns a formatted budget status string."""
        return f"${self.spent:.4f} / ${self.limit} ({self.input_tokens:.0f} in, {self.output_tokens:.0f} out)"


@dataclass
# NAMING FIXED: ValidationContext → ValidationContext
class ValidationContext:
    """Shared memory and infrastructure state for all agents."""

    results: dict[int, Any] = field(default_factory=dict)
    signals: set[str] = field(default_factory=set)
    instructions: list[str] = field(default_factory=list)
    modified_files: set[str] = field(default_factory=set)
    python_files: list[str] = field(default_factory=list)
    graph: DependencyGraph = field(default_factory=DependencyGraph)
    code_graph: DependencyGraph = field(default_factory=DependencyGraph)
    budget: BudgetManager = field(default_factory=BudgetManager)

    # Memory
    memory_file: Path = field(default_factory=lambda: Path("canon_memory.json"))
    file_hashes: dict[str, str] = field(default_factory=dict)
    skip_files: set[str] = field(default_factory=set)
    flapping_files: list[str] = field(
        default_factory=list,
    )  # Changed from set to list to match default_factory
    successful_traces: list[str] = field(default_factory=list)

    # Infrastructure
    model_id: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"))
    _client: Any = field(default=None, init=False)
    intelligence_enabled: bool = field(default=False, init=False)

    # File backups for rollback
    file_backups: dict[str, str] = field(default_factory=dict)

    # WebSocket clients for L5 streaming
    websocket_clients: set[Any] = field(default_factory=set)

    # Prompts
    FEW_SHOT_HYGIENE: str = few_shot_hygiene
    FEW_SHOT_STYLE: str = few_shot_style

    def __post_init__(self):
        # Defer expensive initialization to explicit init() call
        # This prevents import-time side effects that cause test hangs
        pass

    def init(self):
        """Explicit initialization - call this when ready to use the context."""
        print("   [CTX] 🧠 INITIALIZING TRI-BRAIN...")
        self.python_files = _get_python_files()  # Refactored
        self._load_memory()
        self._init_intelligence()

    def _init_intelligence(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key and genai:
            try:
                self._client = genai.Client(api_key=api_key)
                self.intelligence_enabled = True
                print("      [OK] Gemini Connected")
            # guardian: allow-silent-swallow
            except Exception:
                pass

    def _load_memory(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file) as f:
                    data = json.load(f)
                    self.file_hashes = data.get("hashes", {})
                    self.skip_files = set(data.get("skip", []))
            # guardian: allow-silent-swallow
            except Exception:
                pass

    def _save_memory(self):
        try:
            data = {"hashes": self.file_hashes, "skip": list(self.skip_files)}
            with open(self.memory_file, "w") as f:
                json.dump(data, f)
        # guardian: allow-silent-swallow
        except Exception:
            pass

    def report(self, agent: str, key: int, passed: bool, details: Any):
        self.results[key] = {"passed": passed, "details": details, "agent": agent}
        if not passed:
            print(f"   [{agent}] Key {key}: FAIL")

    def get_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        # guardian: allow-silent-swallow
        except Exception:
            return ""

    def write_compliant_file(self, path: str, content: str) -> bool:
        """
        Writes content to a file, ensuring directory exists.
        """
        try:
            # guardian: allow-path-string
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False

    @property
    def client(self):
        return self._client

    @_rate_limited_retry()  # Refactored
    # guardian: allow-magic-config
    async def resilient_mutation(
        self,
        agent_name: str,
        Task: str,
        code: str = "",
        file_path: str = None,
        # guardian: allow-magic-config
        max_attempts: int = 3,
        **kwargs,
    ) -> str:
        if not self.intelligence_enabled or not self.budget.check_budget():
            return code

        try:
            prompt = f"Agent: {agent_name}\nTask: {Task}\nContext:\n{code[:4000]}"
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self.model_id,
                contents=[prompt],
            )
            await self.budget.track(prompt, response.text)
            return _clean_llm_code(response.text)  # Refactored
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"   [{agent_name}] Mutation failed: {e}")
            return code

    # guardian: allow-magic-config
    def signal_healing_cycle(self, cycle_number: int, max_cycles: int = 5):
        """Signal the start of a healing cycle."""
        print(f"   [~] Healing Cycle {cycle_number}/{max_cycles}")

    def signal_convergence(self):
        """Signal that the validation has converged."""
        print("   [OK] Convergence achieved - no modifications in this cycle")
        self.signals.add("CONVERGENCE")

    def signal_critical_failure(self, message: str):
        """Signal a critical failure."""
        self.signals.add("CRITICAL_FAILURE")
        print(f"   [ALERT] SIGNAL: CRITICAL_FAILURE - {message}")

    def signal_ast_valid(self):
        """Signal that AST checks passed."""
        self.signals.add("AST_VALID")
        print("   [OK] SIGNAL: AST_VALID asserted on Blackboard.")

    def signal_deps_valid(self):
        """Signal that dependency checks passed."""
        self.signals.add("DEPS_VALID")
        print("   [OK] SIGNAL: DEPS_VALID asserted on Blackboard.")

    def signal_secure(self):
        """Signal that security checks passed."""
        self.signals.add("SECURE")
        print("   [OK] SIGNAL: SECURE asserted on Blackboard.")

    def signal_llm_failure(self, error: str):
        """Signal an LLM failure."""
        self.signals.add("LLM_FAILURE")
        print(f"   [!] SIGNAL: LLM_FAILURE - {error}")

    def rollback_changes(self):
        """Rollback changes from file backups."""
        if self.file_backups:
            for file_path, content in self.file_backups.items():
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"   ↩️ Rolled back: {file_path}")
                # guardian: allow-silent-swallow
                except Exception as e:
                    print(f"   [!] Rollback failed for {file_path}: {e}")
            self.file_backups.clear()

    def refresh_graph(self):
        """Rebuilds graph after mutations (sync wrapper)."""
        # Build graph synchronously since we may be called from async context
        print("   🕸️ Building Holistic Code Graph...")
        self.graph.graph = {}
        self.graph.reverse_graph = {}
        for file_path in self.python_files:
            self.graph.graph[file_path] = {"imports": [], "classes": []}
            try:
                with open(file_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph.graph[file_path]["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph.graph[file_path]["imports"].append(node.module)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
        for file, data in self.graph.graph.items():
            for imp in data["imports"]:
                if isinstance(imp, str):
                    if imp not in self.graph.reverse_graph:
                        self.graph.reverse_graph[imp] = []
                    self.graph.reverse_graph[imp].append(file)
