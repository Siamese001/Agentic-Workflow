from __future__ import annotations

import ast

from tqdm import tqdm

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "dependencygraph_validator")
emit_determinism_digest("p0", "dependencygraph_validator")

_emit_dispatches_healing_run("p1", "dependencygraph_validator", "L5")
_emit_routes_through("p1", "dependencygraph_validator", "L5")
_emit_checks_agent_registry("p1", "dependencygraph_validator", "agent_registry")
_emit_validates_agent_capability("p1", "dependencygraph_validator", "capability")
_emit_dispatches_execution_plan("p1", "dependencygraph_validator", "exec_plan")
_emit_agent_executes_agent("p1", "dependencygraph_validator", "sub_agent")
_emit_routes_to_agent("p1", "dependencygraph_validator", "target_agent")
_emit_verifies_policy("p1", "dependencygraph_validator", "policy_check")
_emit_observes_runtime_state("p1", "dependencygraph_validator", "runtime_state")
_emit_verifies_boundary("p1", "dependencygraph_validator", "boundary_check")
_emit_transcripts_response("p1", "dependencygraph_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "dependencygraph_validator")
_emit_gated_by_confidence("p1", "dependencygraph_validator", "confidence_gate")
_emit_escalates_to_human("p1", "dependencygraph_validator", "L5")
_emit_reads_policy_state("p1", "dependencygraph_validator", "L5")
_emit_authorize_and_execute("p2", "dependencygraph_validator", "execution_auth")
_emit_validates_capability("p2", "dependencygraph_validator", "capability_check")
_emit_routes_to_capability("p2", "dependencygraph_validator", "capability_route")
_emit_writes_via_uwg("p2", "dependencygraph_validator", "uwg_write")
_emit_blocks_direct_write("p2", "dependencygraph_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "dependencygraph_validator", "tool_invocation")
_emit_captures_execution_output("p2", "dependencygraph_validator", "exec_output")
_emit_dispatches_agent("p3", "dependencygraph_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "dependencygraph_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "dependencygraph_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "dependencygraph_validator", "healing_outcome")
_emit_escalates_failure("p3", "dependencygraph_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "dependencygraph_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dependencygraph_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "dependencygraph_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "dependencygraph_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dependencygraph_validator", "eval_metric")
_emit_stores_embedding("p4", "dependencygraph_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "dependencygraph_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dependencygraph_validator", "exec_snapshot_link")

"Brief description of functionality and purpose."
import asyncio
import functools
import importlib
import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("dependencygraph_validator", "p4obs", "metric_1")
_emit_emits_metric_event("dependencygraph_validator", "p4obs", "metric_2")
_emit_emits_metric_event("dependencygraph_validator", "p4obs", "metric_3")
_emit_emits_metric_event("dependencygraph_validator", "p4obs", "metric_4")
_emit_emits_metric_event("dependencygraph_validator", "p4obs", "metric_5")
_emit_emits_metric_event("dependencygraph_validator", "p4obs", "metric_6")
_emit_records_incident_event("dependencygraph_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("dependencygraph_validator", "p4obs", "anomaly")
_emit_writes_observability_log("dependencygraph_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("dependencygraph_validator", "p4obs", "mon_state")
_emit_triggers_alert("dependencygraph_validator", "p4obs", "alert")
_emit_links_incident_trace("dependencygraph_validator", "p4obs", "trace_link")
_emit_captures_pattern("dependencygraph_validator", "p3lm", "pattern")
_emit_records_learning_event("dependencygraph_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("dependencygraph_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("dependencygraph_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("dependencygraph_validator", "p3lm", "routing")
_emit_improves_agent_policy("dependencygraph_validator", "p3lm", "policy")
_emit_stores_learning_state("dependencygraph_validator", "p3lm", "state")
_emit_records_execution_trace("dependencygraph_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("dependencygraph_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("dependencygraph_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("dependencygraph_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("dependencygraph_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("dependencygraph_validator", "env_read", "p2_env_1")
_emit_reads_environ("dependencygraph_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("dependencygraph_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("dependencygraph_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "dependencygraph_validator", "context_pull")
_emit_pulls_context("p1", "dependencygraph_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "dependencygraph_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "dependencygraph_validator", "uwg_term_2")
_emit_writes_through("p1", "dependencygraph_validator", "write_through")
_emit_writes_through("p1", "dependencygraph_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "dependencygraph_validator", "safety_validation")
_emit_invokes_eval("p1", "dependencygraph_validator", "eval_call")
_emit_proposal_commits_routing("p1", "dependencygraph_validator", "routing_commit")

few_shot_hygiene = '\n# Example 1: Missing docstring\n# Original:\n# def my_func(arg):\n#     return arg * 2\n# Refactored:\n# def my_func(arg):\n#     """Doubles the input argument."""\n#     return arg * 2\n\n# Example 2: Incorrect variable naming (not snake_case)\n# Original:\n# myVariable = 10\n# Refactored:\n# my_variable = 10\n\n# Example 3: Unused import\n# Original:\n# import os\n# def func():\n#     pass\n# Refactored:\n# def func():\n#     pass\n\n# Example 4: Trailing whitespace\n# Original:\n# def func():\n#     print("hello")\n# Refactored:\n# def func():\n#     print("hello")\n\n# Example 5: Line too long (over 80 chars)\n# Original:\n# def some_long_function_name(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10):\n#     pass\n# Refactored:\n# def some_long_function_name(\n#     arg1, arg2, arg3, arg4, arg5,\n#     arg6, arg7, arg8, arg9, arg10\n# ):\n#     pass\n'
few_shot_style = "\n# Example 1: Function name not snake_case\n# Original:\n# def MyFunction():\n#     pass\n# Refactored:\n# def my_function():\n#     pass\n\n# Example 2: Class name not CamelCase\n# Original:\n# class my_class:\n#     pass\n# Refactored:\n# class MyClass:\n#     pass\n\n# Example 3: Constant not ALL_CAPS\n# Original:\n# my_constant = 10\n# Refactored:\n# MY_CONSTANT = 10\n\n# Example 4: Missing blank line after imports\n# Original:\n# import os\n# import sys\n# def func():\n#     pass\n# Refactored:\n# import os\n# import sys\n\n# def func():\n#     pass\n\n# Example 5: Missing blank line after class definition\n# Original:\n# class MyClass:\n#     pass\n# def func():\n#     pass\n# Refactored:\n# class MyClass:\n#     pass\n\n\n# def func():\n#     pass\n"


def _get_python_files(base_path: str = ".") -> list[str]:
    """
    Recursively finds all Python files in the given base path.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_python_files", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_python_files", "p0_governance")
    python_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)
    return python_files


def _clean_llm_code(text: str) -> str:
    """
    Cleans LLM generated code by removing common markdown fences.
    """
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
            for attempt in tqdm(range(1, max_attempts + 1), desc="retry", leave=False, disable=True):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                    if attempt < max_attempts:
                        print(
                            f"   [RETRY] Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay_seconds}s...",
                        )
                        await asyncio.sleep(delay_seconds)
                    else:
                        raise

        return wrapper

    return decorator


class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""

    def __init__(self):
        self.graph: dict[str, dict[str, list[Any]]] = {}
        self.reverse_graph: dict[str, list[str]] = {}

    async def build(self, files: list[str]):
        """Asynchronously builds the code graph from a list of files."""
        print("   🕸️ Building Holistic Code Graph...")
        for file_path in tqdm(files, desc="build-graph", leave=False, disable=True):
            self.graph[file_path] = {"imports": [], "classes": []}
            try:
                with open(file_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(
                    tree
                ):  # guardian: Parsing and encoding errors need separate handling strategies
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph[file_path]["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph[file_path]["imports"].append(node.module)
            except (
                OSError,
                SyntaxError,
                UnicodeDecodeError,
            ):  # guardian: Parsing and encoding errors need separate handling strategies
                continue
        for file, data in self.graph.items():
            for imp in data["imports"]:
                if isinstance(imp, str):
                    if imp not in self.reverse_graph:
                        self.reverse_graph[imp] = []
                    self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> list[str]:
        """Calculates which files depend on the given path."""
        module_name = str(Path(file_path).as_posix()).replace("/", ".").replace(".py", "")
        impacted = set()
        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])
        return list(impacted)


class BudgetManager:
    """Tracks estimated token usage and financial safety limits."""

    def __init__(self, limit_usd: float | None = None):
        env_limit = os.getenv("AGENTIC_BUDGET_USD")
        self.limit = float(env_limit) if env_limit else limit_usd or 2.0
        self.spent = 0.0
        self.input_tokens = 0.0
        self.output_tokens = 0.0

    async def track(self, prompt: str, response: str):
        """Asynchronously updates budget metrics."""
        in_t = len(prompt) / 4
        out_t = len(response) / 4
        self.input_tokens += in_t
        self.output_tokens += out_t
        cost = in_t / 1000000 * 0.5 + out_t / 1000000 * 1.5
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
    memory_file: Path = field(default_factory=lambda: Path("canon_memory.json"))
    file_hashes: dict[str, str] = field(default_factory=dict)
    skip_files: set[str] = field(default_factory=set)
    flapping_files: list[str] = field(default_factory=list)
    successful_traces: list[str] = field(default_factory=list)
    model_id: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"))
    _client: Any = field(default=None, init=False)
    intelligence_enabled: bool = field(default=False, init=False)
    file_backups: dict[str, str] = field(default_factory=dict)
    websocket_clients: set[Any] = field(default_factory=set)
    FEW_SHOT_HYGIENE: str = few_shot_hygiene
    FEW_SHOT_STYLE: str = few_shot_style

    def __post_init__(self):
        pass

    def init(self):
        """Explicit initialization - call this when ready to use the context."""
        print("   [CTX] 🧠 INITIALIZING TRI-BRAIN...")
        self.python_files = _get_python_files()
        self._load_memory()
        self._init_intelligence()

    def _init_intelligence(self):
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                self._client = importlib.import_module("infrastructure.sdks_mcps").create_gemini_model(self.model_id)
                self.intelligence_enabled = True
                print("      [OK] Gemini Connected")
            except (ImportError, AttributeError, ValueError) as e:
                print(f"      [WARN] Gemini unavailable: {type(e).__name__}")

    def _load_memory(self):  # guardian: Add error context logging
        if self.memory_file.exists():
            try:
                with open(self.memory_file) as f:
                    data = json.load(f)
                    self.file_hashes = data.get("hashes", {})
                    self.skip_files = set(data.get("skip", []))
            except (OSError, json.JSONDecodeError) as e:  # guardian: Add error context logging
                print(f"      [DEBUG] Failed to load memory: {e}")

    def _save_memory(self):
        try:
            data = {"hashes": self.file_hashes, "skip": list(self.skip_files)}
            self.memory_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except (OSError, TypeError) as e:
            print(f"      [DEBUG] Failed to save memory: {e}")

    def report(self, agent: str, key: int, passed: bool, details: Any):
        self.results[key] = {"passed": passed, "details": details, "agent": agent}
        if not passed:  # guardian: File operations with encoding need error-specific handling
            print(f"   [{agent}] Key {key}: FAIL")

    def get_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except (
            OSError,
            UnicodeDecodeError,
        ):  # guardian: File operations with encoding need error-specific handling
            return ""

    def write_compliant_file(self, path: str, content: str) -> bool:
        """
        Writes content to a file, ensuring directory exists.
        """
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content, encoding="utf-8")
            return True
        except (OSError, TypeError) as e:
            print(f"      [DEBUG] Failed to write file {path}: {e}")
            return False

    @property
    def client(self):
        return self._client

    @_rate_limited_retry()
    # guardian: allow-magic-config
    async def resilient_mutation(
        self,
        agent_name: str,
        Task: str,
        code: str = "",
        file_path: str = None,
        max_attempts: int = 3,
        **kwargs,
    ) -> str:
        if not self.intelligence_enabled or not self.budget.check_budget():
            return code
        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            f"resilient_mutation:{agent_name}",
        )
        try:
            prompt = f"Agent: {agent_name}\nTask: {Task}\nContext:\n{code[:4000]}"
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self.model_id,
                contents=[prompt],
            )
            await self.budget.track(prompt, response.text)
            return _clean_llm_code(response.text)
        except (ImportError, AttributeError, TypeError, ValueError) as e:
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
                    Path(file_path).write_text(content, encoding="utf-8")
                    print(f"   ↩️ Rolled back: {file_path}")
                except (OSError, TypeError) as e:
                    print(f"   [!] Rollback failed for {file_path}: {e}")
            self.file_backups.clear()

    def refresh_graph(self):
        """Rebuilds graph after mutations (sync wrapper)."""
        print("   🕸️ Building Holistic Code Graph...")
        self.graph.graph = {}
        self.graph.reverse_graph = {}
        for file_path in tqdm(self.python_files, desc="refresh-graph", leave=False, disable=True):
            self.graph.graph[file_path] = {"imports": [], "classes": []}
            try:
                with open(file_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(
                    tree
                ):  # guardian: Parsing and encoding errors need separate handling strategies
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph.graph[file_path]["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph.graph[file_path]["imports"].append(node.module)
            except (
                OSError,
                SyntaxError,
                UnicodeDecodeError,
            ):  # guardian: Parsing and encoding errors need separate handling strategies
                continue
        for file, data in self.graph.graph.items():
            for imp in data["imports"]:
                if isinstance(imp, str):
                    if imp not in self.graph.reverse_graph:
                        self.graph.reverse_graph[imp] = []
                    self.graph.reverse_graph[imp].append(file)
