# === CONSOLIDATED FILE ===
# TIMESTAMP: 2025-11-17T16:29:33.154331Z
# TARGET: orchestration_entrypoints.py
# SOURCE FILES:
# - /workspace/Agentic-Workflow/_latest_extract/agent_orchestration_v.py | SHA256: eee97bd04582253972565aaf4008294f4c2540d72c6aaa069b0789b361f302c6
# - /workspace/Agentic-Workflow/_latest_extract/main_v.py | SHA256: 69566bc91fa87e488957667585413079a485a2fdbe1d6aeb88688af79681e0e6
# - /workspace/Agentic-Workflow/_latest_extract/run_batch_v.py | SHA256: 4e9f86f7a8d738c4333c7cb7d95ac7c45062064e45c6dd5e014f1a696c548f38
# - /workspace/Agentic-Workflow/_latest_extract/run_learning_v.py | SHA256: b21911c70db83c40e5700dadc11b4cdf0a9cea4d9d00d52212e6267a5c4080ba
# MERGE RULE: 10_8 overrides 10_7; namespace collisions suffixed with __srcN


# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/agent_orchestration_v.py (sha256=eee97bd04582253972565aaf4008294f4c2540d72c6aaa069b0789b361f302c6) ====
# --- Vendor path bootstrap for Codex offline environment ---
import sys
import os

VENDOR_PATH = os.path.join(os.path.dirname(__file__), "vendor")
if VENDOR_PATH not in sys.path:
    sys.path.insert(0, VENDOR_PATH)

# File: agent_orchestration_v10_7.py
# Version: 10.7 (Refactored - CORRECTED)
#
# v10.7 REFACTOR (CORRECTION):
# - RE-ADDED: Restored the `StrategyPlan.model_validate(...)` calls
#   inside nodes. Removing them was an error and broke the agent
#   contracts, which expect Pydantic objects, not dicts.
#
# v10.7 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_7.
#
# v10.7 MAJOR CHANGES:
# - IMPLEMENTED (Fix #5): Graph now runs run_prompt_engineering and
#   run_rag_stack in parallel using a fork/join pattern.
# - IMPLEMENTED (Fix #7): Added load_dynamic_tools() to dynamically load
#   tools from the generated_tools_v10_7 directory at runtime.
#   Conductors now call this to update their tool lists.
# - IMPLEMENTED (Fix #8): QAConductor now loads UI tools (stubs).
# - IMPLEMENTED (Fix #10): run_rag_stack node refactored to support
#   A2A messaging (accepts full state, returns state patch).
# - IMPLEMENTED (Fix #17, #19, #20, #24): ReActConductor prompts updated
#   to manually inject Goal State, Top Failures, Cognitive Mode,
#   and a Reflection step.
# - IMPLEMENTED (Fix #30): Added 'run_constitutional_review' node and
#   'check_constitution' conditional edge for final safety review.
# - FIXED: All v10_5 imports and class names updated to v10_7.

import json
import logging
import asyncio
import os
import importlib.util
import inspect
from datetime import datetime
from typing import Dict, Any, List, Callable, Awaitable, Tuple, Optional
from functools import wraps, partial

# v10.7: Import from new core
from core_v10_7 import (
    WorkflowContext, BaseAgent, StrategyPlan, PydanticSchemaError,
    CircuitBreakerOpenError,
    CircuitBreaker, WorkflowTimeoutError, AsyncTimeoutError, WorkflowError,
    ConfigV10_7, BaseTool,
    track_metrics,
    _format_prompt_with_defaults,
    ConstitutionalReviewResult, # v10.7 (Fix #30)
    wrap_mcp,
    MCPClientStub,
    ArbitrationReport,
    NodeResult,
    NodeStatus,
)
from mcp import get_agent
from langgraph.graph import StateGraph, END
from langgraph.errors import GraphRecursionError
from telemetry_v10_7 import log_event

# Make HIL import conditional for environment compatibility
try:
    from langgraph.prebuilt import human_in_the_loop
    HIL_AVAILABLE = True
except ImportError:
    HIL_AVAILABLE = False
    human_in_the_loop = None # type: ignore
    logging.getLogger(__name__).warning(
        "human_in_the_loop not available - HIL features will be disabled"
    )

# v10.7: Import from new stacks
from agent_stacks_v10_8 import (
    BulletExecutionStack,
    DraftingExecutionStack,
    HILStackV10_8,
    PromptBuilderStack,
    QAValidationStack,
    SafetyStackV10_8,
    StateAdapterStack,
    StrategyStackV10_8,
    RobustnessStack,
)
from stacks_v10_8 import RAGOrchestratorStack, PromptRendererStack

# v10.7: Import from new tools file
from agent_tools_v10_7 import (
    QAClaimValidatorTool,
    QAToneValidatorTool,
    QAThematicAlignmentTool,
    QASemanticEntailmentTool,
    QANarrativeThreadTool,
    QAAdversarialReviewerTool,
    QAJDSkillsValidatorTool,
    QASignalScoreValidatorTool,
    QABiasDetectorTool,
    QATenureValidatorTool,
    QAMissedOpportunityTool,
    QAWordCountValidatorTool,
    HyDETool,
    ChromaDBSearchTool,
    BM25SearchTool,
    # v10.7 (Fix #8): Import UI tool stubs
    UIUpdateElementTool,
    UIFireEventTool
)

# v10.7: Logger name updated
logger = logging.getLogger("agent_orchestration_v10_7")

NODE_RESULT_KEYS = {"node", "status", "payload"}


def node_success(node: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Build a SUCCESS NodeResult for the given node and payload."""

    return NodeResult(
        node=node,
        status=NodeStatus.SUCCESS,
        payload=dict(payload or {}),
    ).model_dump()


def node_error(
    node: str,
    status: NodeStatus,
    error_kind: str,
    error_message: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build an error NodeResult for the given node."""

    return NodeResult(
        node=node,
        status=status,
        error_kind=error_kind,
        error_message=error_message,
        payload=dict(payload or {}),
    ).model_dump()


def _looks_like_node_result(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    if not NODE_RESULT_KEYS.issubset(value.keys()):
        return False
    status_value = value.get("status")
    if isinstance(status_value, NodeStatus):
        return True
    if isinstance(status_value, str) and status_value in NodeStatus._value2member_map_:
        return True
    return False


def _extract_node_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    if _looks_like_node_result(state):
        payload = state.get("payload") or {}
        if isinstance(payload, dict):
            return payload
        return {}
    return state


def _ensure_node_result(node_name: str, result: Any) -> Dict[str, Any]:
    sanitized = result
    if isinstance(result, dict):
        sanitized = dict(result)
        status_value = sanitized.get("status")
        if isinstance(status_value, str):
            try:
                sanitized["status"] = NodeStatus(status_value)
            except ValueError as exc:
                raise WorkflowError(
                    f"Node '{node_name}' returned unknown status '{status_value}'"
                ) from exc
        for optional_field in ("error_kind", "error_message"):
            if sanitized.get(optional_field) is None:
                sanitized.pop(optional_field, None)
    try:
        return NodeResult.model_validate(sanitized).model_dump()
    except Exception as exc:  # pragma: no cover - defensive
        raise WorkflowError(
            f"Node '{node_name}' did not return a valid NodeResult: {exc}"
        ) from exc


def unwrap_node_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Utility for modules that need to recover the workflow state from a node result."""

    return _extract_node_payload(result)

# ============================================================================
# MCP STACK ROUTING HELPERS
# ============================================================================


async def route_to_stack(stack_name: str, context: WorkflowContext, *args, **kwargs):
    """Resolve an MCP-registered stack and execute it with provided arguments."""

    agent_cls = get_agent(stack_name)
    agent = agent_cls(context)

    runner = getattr(agent, "run_async", None)
    if callable(runner):
        result = runner(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return result

    runner = getattr(agent, "run", None)
    if callable(runner):
        result = runner(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return result

    raise WorkflowError(f"Agent '{stack_name}' does not expose run or run_async methods")


def _attach_arbitration_report(state: dict, stage: str, report: ArbitrationReport) -> None:
    """Attach an arbitration report to the shared state tree."""

    if "arbitration" not in state or not isinstance(state["arbitration"], dict):
        state["arbitration"] = {}
    state["arbitration"][stage] = report.model_dump()


def _read_arbitration_route(state: dict, stage: str) -> Tuple[str, bool]:
    """Return (route, has_report) for the requested arbitration stage."""

    arbitration_section = state.get("arbitration")
    if not isinstance(arbitration_section, dict):
        return "", False

    report_data = arbitration_section.get(stage)
    if report_data is None:
        return "", False

    if isinstance(report_data, ArbitrationReport):
        route = report_data.suggested_route or ""
        if not route and report_data.decision == "ACCEPT":
            route = "ACCEPT"
        return route, True

    if isinstance(report_data, dict):
        route = report_data.get("suggested_route") or ""
        if not route and report_data.get("decision") == "ACCEPT":
            route = "ACCEPT"
        return route, True

    return "", False


def _get_robustness_stack(workflow_context: WorkflowContext) -> RobustnessStack:
    stack = getattr(workflow_context, "_robustness_stack", None)
    if stack is None:
        stack = RobustnessStack(workflow_context)
        setattr(workflow_context, "_robustness_stack", stack)
    return stack


def apply_robustness(stage_name: str):
    """Decorator that routes node execution through the robustness stack."""

    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            workflow_context = kwargs.get("workflow_context")
            if workflow_context is None and len(args) >= 2:
                workflow_context = args[1]
            robustness = _get_robustness_stack(workflow_context)

            async def operation():
                return await func(*args, **kwargs)

            return await robustness.run_with_resilience(stage_name, operation)

        return wrapper

    return decorator


def add_node_with_policies(
    workflow: StateGraph,
    name: str,
    fn: Callable[..., Awaitable[Dict[str, Any]]],
    workflow_context: WorkflowContext,
    *,
    enable_timeout: bool = True,
    enable_robustness: bool = True,
    enable_mcp: bool = True,
) -> None:
    """Apply all orchestration policies in a single, deterministic location."""

    async def base_executor(state: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        payload = _extract_node_payload(state)
        result = fn(payload, *args, workflow_context=workflow_context, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return result

    wrapped: Callable[..., Awaitable[Dict[str, Any]]] = base_executor

    if enable_mcp and getattr(workflow_context, "wrap_mcp_nodes", True):
        wrapped = wrap_mcp(wrapped)

    if enable_robustness:
        wrapped = apply_robustness(stage_name=name)(wrapped)

    if enable_timeout:
        timeout_sec = (
            workflow_context.config.performance_config.workflow_node_timeout_seconds
        )
        wrapped = get_timeout_decorator(timeout_sec)(wrapped)

    async def enforce_contract(state: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        result = wrapped(state, *args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return _ensure_node_result(name, result)

    workflow.add_node(name, enforce_contract)


# ============================================================================
# v10.7: RUNTIME DECORATORS (Fix #6)
# ============================================================================

def get_timeout_decorator(timeout_seconds: float):
    """v10.7 (Fix #6): Creates a decorator bound to an explicit timeout."""

    timeout_seconds = float(timeout_seconds)

    def decorator__src1(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            func_name = getattr(func, "__name__", None)
            if func_name is None and hasattr(func, "func"):
                func_name = getattr(func.func, "__name__", "partial")
            if func_name is None:
                func_name = repr(func)
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except AsyncTimeoutError as e:
                logger.error(
                    f"!!! NODE TIMEOUT: {func_name} exceeded {timeout_seconds}s !!!"
                )
                raise WorkflowTimeoutError(
                    f"Node {func_name} timed out after {timeout_seconds}s"
                ) from e

        return wrapper

    return decorator

# ============================================================================
# v10.7: DYNAMIC TOOLING (Fix #7)
# ============================================================================

def load_dynamic_tools(context: WorkflowContext, debug_mode: bool) -> Dict[str, BaseTool]:
    """
    v10.7 (Fix #7): Scans the generated_tools_path and dynamically
    loads any valid BaseTool subclasses.
    """
    dynamic_tools = {}
    tools_dir = context.config.meta_loop_config.generated_tools_path
    if not os.path.exists(tools_dir):
        logger.info(f"Dynamic tool directory not found, skipping: {tools_dir}")
        return {}

    logger.info(f"Loading dynamic tools from: {tools_dir}")
    mcp_enabled = context.is_mcp_enabled()
    if mcp_enabled:
        context.ensure_mcp_clients()
    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                file_path = os.path.join(tools_dir, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], file_path)
                if spec is None:
                    raise ImportError(f"Could not create spec for {file_path}")
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and \
                       issubclass(obj, BaseTool) and \
                       obj is not BaseTool:
                        
                        tool_instance = obj(context, debug_mode)
                        tool_name = tool_instance.tool_name

                        if mcp_enabled:
                            required_clients = getattr(tool_instance, "required_mcp_clients", [])
                            optional_clients = getattr(tool_instance, "optional_mcp_clients", [])

                            for attr_name, value in (
                                ("required_mcp_clients", required_clients),
                                ("optional_mcp_clients", optional_clients),
                            ):
                                if value and not isinstance(value, (list, tuple)):
                                    raise WorkflowError(
                                        f"Dynamic tool '{name}' has invalid '{attr_name}' definition."
                                    )

                            for client_name in required_clients or []:
                                if not isinstance(client_name, str):
                                    raise WorkflowError(
                                        f"Dynamic tool '{name}' requires MCP client names as strings."
                                    )
                                context.get_mcp_client(client_name)

                            for client_name in optional_clients or []:
                                if not isinstance(client_name, str):
                                    raise WorkflowError(
                                        f"Dynamic tool '{name}' optional MCP clients must be strings."
                                    )
                                context.get_mcp_client(
                                    client_name,
                                    default=MCPClientStub(client_name, {"source": f"dynamic_tool:{tool_name}"}),
                                )
                        if tool_name in dynamic_tools:
                            logger.warning(f"Duplicate dynamic tool name '{tool_name}'. Overwriting.")
                        
                        dynamic_tools[tool_name] = tool_instance
                        logger.info(f"Successfully loaded dynamic tool: {name} (as '{tool_name}')")
            
            except Exception as e:
                logger.error(f"Failed to load dynamic tool from {filename}: {e}")
                
    return dynamic_tools

# QA CONDUCTOR (v10.7: Fix #7, #8, #17, #19, #20, #24)
# ============================================================================

class QAConductorAgent(BaseAgent):
    """v10.7: ReAct QA Conductor with dynamic/UI tooling and cognitive modes."""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        static_tools: List[Tuple[str, BaseTool]] = [
            # Standard QA Suite
            ("validate_claims", QAClaimValidatorTool(context, debug_mode)),
            ("validate_tone", QAToneValidatorTool(context, debug_mode)),
            ("validate_thematic_alignment", QAThematicAlignmentTool(context, debug_mode)),
            ("validate_semantic_entailment", QASemanticEntailmentTool(context, debug_mode)),
            ("validate_narrative_thread", QANarrativeThreadTool(context, debug_mode)),
            ("adversarial_review", QAAdversarialReviewerTool(context, debug_mode)),
            ("validate_jd_skills", QAJDSkillsValidatorTool(context, debug_mode)),
            ("validate_signal_score", QASignalScoreValidatorTool(context, debug_mode)),
            ("validate_bias", QABiasDetectorTool(context, debug_mode)),
            ("validate_tenure", QATenureValidatorTool(context, debug_mode)),
            ("find_missed_opportunities", QAMissedOpportunityTool(context, debug_mode)),
            ("validate_word_count", QAWordCountValidatorTool(context, debug_mode)),
            # v10.7 (Fix #8): Add UI tools
            ("ui_update_element", UIUpdateElementTool(context, debug_mode)),
            ("ui_fire_event", UIFireEventTool(context, debug_mode)),
        ]

        self.tools: Dict[str, BaseTool] = {}
        for tool_name, tool_instance in static_tools:
            if tool_name in self.tools:
                logger.error(
                    "Duplicate static QA tool name detected during initialization: %s",
                    tool_name,
                )
                raise WorkflowError(
                    f"Duplicate static QA tool detected: {tool_name}"
                )
            self.tools[tool_name] = tool_instance

        # v10.7 (Fix #7): Load dynamic tools
        dynamic_tools = load_dynamic_tools(context, debug_mode)
        for tool_name in dynamic_tools:
            if tool_name in self.tools:
                logger.warning(
                    "Dynamic tool '%s' overrides an existing QA tool. Previous instance will be replaced.",
                    tool_name,
                )
        self.tools.update(dynamic_tools)
        
        self.tool_schemas = [t.get_schema() for t in self.tools.values()]
        
        self.tool_breakers = {
            name: CircuitBreaker(
                failure_threshold=self.config.batch_config.circuit_breaker_failure_threshold
            ) for name in self.tools
        }
        self.style_guide = "Style: Ensure professional, clear, and unbiased language."

    @track_metrics('run_react_qa_conductor')
    async def run_async(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        collab = getattr(self.context, "collaboration_engine", None)
        if collab and collab.enabled():
            team = collab.form_team(self.__class__.__name__)
            state.setdefault("a2a_team", team)
        autonomy = getattr(self.context, "autonomy_engine", None)
        if autonomy and autonomy.enabled():
            hints = autonomy.decide(workflow_id)
            self.log_debug(f"Autonomy hints: {hints}")
            state.setdefault("autonomy_hints", {}).update(hints)
        adv = getattr(self.context, "advanced_meta_learner", None)
        if adv and adv.enabled():
            hints = adv.analyze(workflow_id)
            state.setdefault("meta_hints", {}).update(hints)
        result = await self._execute_conductor(state, workflow_id)
        return await self._maybe_self_correct(state, workflow_id, result)

    async def _execute_conductor(
        self,
        state: Dict[str, Any],
        workflow_id: str,
        self_heal_hint: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.log_info("Running ReAct QA Conductor (v10.7)...")

        hint = self_heal_hint or {}
        max_steps = hint.get("max_steps", self.config.agent_stacks.conductor_max_steps)
        client = self.get_model_client("react_conductor_model")

        pruned_draft = await self.budget_manager.prune(
            json.dumps(state['draft']['sections']), 4000
        )
        pruned_master_resume = await self.budget_manager.prune(
            json.dumps(state['resume']['master_resume']), 4000
        )
        pruned_jd = await self.budget_manager.prune(state['job']['raw_jd'], 2000)

        strategy_plan = state['strategy']['strategy_plan']
        if isinstance(strategy_plan, dict):
            strategy_plan = StrategyPlan.model_validate(strategy_plan)

        react_prompt = f"""
{client.goal_state}
{client.top_failures}
-------------------
MODE: ORCHESTRATION
TASK: You are a ReAct QA conductor. Your goal is to validate the draft.
Draft (Pruned): {pruned_draft}
Tools: {json.dumps(self.tool_schemas)}
Plan (v10.7):
1.  Run `validate_claims` and `validate_tenure`.
2.  Run `validate_jd_skills` and `validate_thematic_alignment`.
3.  Run `validate_tone`, `validate_narrative_thread`, and `validate_signal_score`.
4.  Run `validate_bias`.
5.  Run `validate_word_count` on the summary section (e.g., min: 50, max: 150).
6.  Run `find_missed_opportunities`.
7.  Run `adversarial_review` as a final check.
8.  Compile all feedback into a final QA report.

REFLECTION: Did I run all critical validation tools?
Output thoughts/tool calls in JSON:
{{"thought": "Your reasoning", "tool_call": {{"name": "tool_name", "input": {{"arg": "value"}}}}}}
When finished, output:
{{"thought": "QA complete", "final_qa_report": {{"qa_passed": true/false, "issues": [...]}}}}
"""
        if hint.get("extra_instruction"):
            react_prompt += f"\nEXTRA_DIRECTIVE: {hint['extra_instruction']}"

        messages = [{"role": "user", "content": react_prompt}]

        final_report = {}
        all_tool_results = []

        tool_context = {
            "draft_text": pruned_draft,
            "master_resume": pruned_master_resume,
            "job_description": pruned_jd,
            "strategy": strategy_plan.model_dump(),
            "style_guide": self.style_guide
        }

        for step in range(max_steps):
            response = await client.chat_completion_async(
                messages=messages,
                temperature=hint.get(
                    "temperature",
                    self.config.agent_stacks.conductor_temperature,
                ),
                response_format="json_object"
            )

            step_data, error = self.validator.validate(response["content"], dict)
            if error:
                logger.warning(f"QA step {step} failed validation: {error}")
                messages.append({"role": "user", "content": f"Error: Invalid JSON response from LLM. {error}"})
                continue

            messages.append({"role": "assistant", "content": json.dumps(step_data)})

            if "final_qa_report" in step_data:
                final_report = step_data["final_qa_report"]
                final_report["all_tool_results"] = all_tool_results
                self.log_feedback(workflow_id, "react_conductor_qa", "success", {"steps_executed": step})
                return final_report

            if "tool_call" in step_data:
                tool_name = step_data["tool_call"].get("name")
                tool_input = step_data["tool_call"].get("input", {})

                if not tool_name or tool_name not in self.tools:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})
                    continue

                tool_input.update(tool_context)

                try:
                    breaker = self.tool_breakers[tool_name]
                    breaker.check()
                    tool = self.tools[tool_name]
                    tool_result = await tool.run_async(tool_input, workflow_id)
                    breaker.record_success()
                    all_tool_results.append({tool_name: tool_result})
                    messages.append({"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"})

                except (CircuitBreakerOpenError, PydanticSchemaError, Exception) as e:
                    self.log_error(f"QA Tool {tool_name} failed: {e}")
                    if not isinstance(e, CircuitBreakerOpenError):
                        if tool_name in self.tool_breakers:
                            self.tool_breakers[tool_name].record_failure()

                    error_msg = f"Error: Tool '{tool_name}' failed. Do not call it again. Reason: {str(e)}"
                    messages.append({"role": "user", "content": error_msg})

        self.log_feedback(workflow_id, "react_conductor_qa", "failure", {"reason": "Max steps reached"})
        return {"error": "Max steps reached", "steps": max_steps, "all_tool_results": all_tool_results, "qa_passed": False}

    async def _maybe_self_correct(
        self,
        state: Dict[str, Any],
        workflow_id: str,
        base_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        manager = getattr(self, "self_correction_manager", None)
        if not manager:
            return base_result
        if not manager.can_retry(workflow_id, "qa"):
            return base_result

        if base_result.get("qa_passed", False) and not base_result.get("error"):
            return base_result

        issue = "qa_failed" if not base_result.get("qa_passed", False) else "qa_error"
        report = manager.start_retry(
            workflow_id,
            "qa",
            issue=issue,
            action="extend_validation_budget",
        )

        corrected_result = await self._execute_conductor(
            state,
            workflow_id,
            self_heal_hint={
                "max_steps": self.config.agent_stacks.conductor_max_steps + 1,
                "temperature": max(0.0, self.config.agent_stacks.conductor_temperature - 0.1),
                "extra_instruction": "Revisit failed validators and emit a structured QA report.",
            },
        )

        resolved = corrected_result.get("qa_passed", False) and not corrected_result.get("error")
        manager.finalize_retry(report, resolved)
        if resolved:
            corrected_result.setdefault("self_correction", {})["qa"] = report.model_dump()
            return corrected_result
        return base_result


class MetaLearningLoop(BaseAgent):
    """Placeholder MCP agent for telemetry-aligned meta learning."""

    async def run_async(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        collab = getattr(self.context, "collaboration_engine", None)
        if collab and collab.enabled():
            team = collab.form_team(self.__class__.__name__)
            state.setdefault("a2a_team", team)
        self.log_info("MetaLearningLoop invoked - emitting telemetry only.")
        log_event("MetaLearningLoop", "executed", {"workflow_id": workflow_id})
        return {"meta_learning": {"status": "noop"}}

# ============================================================================
# LANGGRAPH NODE & EDGE FUNCTIONS (v10.7: Fix #5, #10, #30)
# ============================================================================

# --- NODE DEFINITIONS (v10.7) ---

async def run_sanitize_pii(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 0: Sanitize PII"""

    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    safety_stack = SafetyStackV10_8(context)

    sanitized = await asyncio.to_thread(
        safety_stack.sanitize_resume,
        state.get('resume', {}).get('master_resume', {}),
    )
    bias_result = await asyncio.to_thread(
        safety_stack.detect_bias,
        state.get('job', {}).get('raw_jd', ''),
        workflow_id,
    )

    patch = {
        "resume": {"sanitized_resume": sanitized},
        "safety": {"bias_detected": bias_result.get('bias_detected', False)},
    }
    adapter = StateAdapterStack(context)
    new_state = adapter.apply_patch(state, patch)

    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile

    return node_success("run_sanitize_pii", new_state)

async def run_detect_prompt_injection(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 0.5: Detect Prompt Injection"""

    context = workflow_context
    safety_stack = SafetyStackV10_8(context)

    if not context.config.agent_stacks.enable_prompt_injection_detection:
        patch = {"safety": {"injection_detected": False}}
    else:
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        detection = await safety_stack.detect_prompt_injection_async(
            state.get('job', {}).get('raw_jd', ''),
            workflow_id,
        )
        log_event("SafetyGuardStack", "run", {"workflow_id": workflow_id})
        patch = {
            "safety": {
                "injection_detected": detection.get('injection_detected', False)
            }
        }

    adapter = StateAdapterStack(context)
    new_state = adapter.apply_patch(state, patch)

    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile

    return node_success("run_detect_prompt_injection", new_state)

async def run_classify_complexity(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 1: Classify Complexity"""

    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    strategy_stack = StrategyStackV10_8(context)
    complexity = await strategy_stack.classify_complexity_async(
        state.get('job', {}).get('raw_jd', ''),
        workflow_id,
    )
    context.complexity = complexity

    adapter = StateAdapterStack(context)
    new_state = adapter.apply_patch(state, {"metadata": {"complexity": complexity}})

    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile

    return node_success("run_classify_complexity", new_state)

async def run_tot_strategy(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 2: ToT strategy"""
    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    strategy_stack = StrategyStackV10_8(context)
    job_context = {
        "job_title": state['job']['job_title'],
        "company": state['job']['company'],
        "job_description": state['job']['raw_jd']
    }
    strategy_result = await strategy_stack.plan_strategy_async(
        job_context,
        workflow_id,
        state,
    )
    log_event("StrategyStack", "completed", {"workflow_id": workflow_id})
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, {"strategy": strategy_result})
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_tot_strategy", state)


async def run_arbitration_after_strategy(state: dict, workflow_context: WorkflowContext) -> dict:
    """Arbitration node after Strategy stack completion."""

    report = await workflow_context.arbitration_engine.run_check("strategy_post_plan", state)
    _attach_arbitration_report(state, "strategy_post_plan", report)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_arbitration_after_strategy", state)

async def run_detect_ambiguity(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 3: Proactive HIL ambiguity check"""
    context = workflow_context
    if not _is_hil_runtime_enabled(workflow_context):
        if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
            profile = workflow_context.tuning_profile
            new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
            workflow_context.tuning_profile = new_profile
        patch = {
            "hil": {
                "ambiguity_report": {
                    "ambiguity_detected": False,
                    "confidence": 1.0,
                    "reason": "HIL disabled",
                    "question_for_human": "",
                }
            }
        }
        adapter = StateAdapterStack(context)
        new_state = adapter.apply_patch(state, patch)
        return node_success("run_detect_ambiguity", new_state)

    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    hil_stack = HILStackV10_8(context)

    strategy_plan = state.get('strategy', {}).get('strategy_plan')
    ambiguity_result = await hil_stack.detect_ambiguity_async(strategy_plan, workflow_id)
    report = ambiguity_result.get("ambiguity_report")
    if report is None:
        report = {"ambiguity_detected": False, "confidence": 0.0}
    confidence_threshold = context.config.agent_stacks.ambiguity_confidence_threshold
    if hasattr(report, "confidence") and report.confidence < confidence_threshold:
        if hasattr(report, "ambiguity_detected"):
            report.ambiguity_detected = False

    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile

    serialized = report.model_dump() if hasattr(report, "model_dump") else report
    patch = {"hil": {"ambiguity_report": serialized}}
    adapter = StateAdapterStack(context)
    new_state = adapter.apply_patch(state, patch)
    return node_success("run_detect_ambiguity", new_state)

# v10.7 (Fix #5): Dummy node for parallel fork
def prepare_parallel_run(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 3.5: Gateway for parallel execution."""
    logger.info("Forking graph for parallel RAG and Prompt Engineering.")
    return node_success("prepare_parallel_run", state)

async def run_prompt_builder(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node: Build structured prompts using the PromptBuilder stack."""

    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    strategy_plan = state['strategy']['strategy_plan']
    if isinstance(strategy_plan, dict):
        strategy_plan = StrategyPlan.model_validate(strategy_plan)

    complexity = state.get('metadata', {}).get('complexity', 'unknown')
    prompt_builder = PromptBuilderStack(context)
    prompts_patch = await prompt_builder.run_async(
        strategy_plan,
        complexity,
        workflow_id,
        state,
    )
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, prompts_patch)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_prompt_builder", state)

async def run_prompt_renderer(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node: Render PromptEnvelope into final prompt with safety context."""

    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    renderer = PromptRendererStack(context)
    prompts_patch = await renderer.run_async(state, workflow_id=workflow_id)
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, prompts_patch)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_prompt_renderer", state)

async def run_prompt_engineering(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 4: Generate dynamic prompts"""
    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    strategy_plan = state['strategy']['strategy_plan']
    if isinstance(strategy_plan, dict):
        strategy_plan = StrategyPlan.model_validate(strategy_plan)

    complexity = state.get('metadata', {}).get('complexity', 'unknown')
    prompt_builder = PromptBuilderStack(context)
    prompts_patch = await prompt_builder.run_async(
        strategy_plan,
        complexity,
        workflow_id,
        state,
    )
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, prompts_patch)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_rag_stack", state)

async def run_rag_stack(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 5: Agentic RAG (v10.7 Fix #10: A2A enabled)"""
    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    orchestrator = RAGOrchestratorStack(context)
    rag_patch = await orchestrator.run_from_state_async(state, workflow_id)
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, rag_patch)
    log_event("RAGStack", "completed", {"workflow_id": workflow_id})
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_generate_bullets", state)

# v10.7 (Fix #5): Dummy node for parallel join
def join_rag_and_prompt(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 5.5: Gateway for parallel join."""
    logger.info("Joining graph from parallel RAG and Prompt Engineering.")
    return node_success("join_rag_and_prompt", state)


async def run_arbitration_after_join(state: dict, workflow_context: WorkflowContext) -> dict:
    """Arbitration node after prompt/RAG join."""

    report = await workflow_context.arbitration_engine.run_check("prompt_rag_join", state)
    _attach_arbitration_report(state, "prompt_rag_join", report)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_arbitration_after_join", state)

async def run_generate_bullets(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 6: Generate bullets (4-step)"""
    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    bullet_stack = BulletExecutionStack(context)
    bullet_patch = await bullet_stack.generate_from_state_async(state, workflow_id)
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, bullet_patch)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_critique_bullets", state)

async def run_critique_bullets(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 7: Critique bullets"""
    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    bullet_stack = BulletExecutionStack(context)
    critique_patch = await bullet_stack.critique_from_state_async(state, workflow_id)
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, critique_patch)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_feedback_router", state)


async def run_arbitration_after_bullets(state: dict, workflow_context: WorkflowContext) -> dict:
    """Arbitration node after bullet critique/selection."""

    report = await workflow_context.arbitration_engine.run_check("bullets_post_selection", state)
    _attach_arbitration_report(state, "bullets_post_selection", report)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_arbitration_after_bullets", state)

async def run_drafting(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 8: Draft assembly with ReAct Conductor"""
    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    drafting_stack = DraftingExecutionStack(context)
    draft_patch = await drafting_stack.run_from_state_async(state, workflow_id)
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, draft_patch)
    log_event("DraftingStack", "completed", {"workflow_id": workflow_id})
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_drafting", state)


async def run_arbitration_after_drafting(state: dict, workflow_context: WorkflowContext) -> dict:
    """Arbitration node after drafting."""

    report = await workflow_context.arbitration_engine.run_check("draft_post_assembly", state)
    _attach_arbitration_report(state, "draft_post_assembly", report)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_arbitration_after_drafting", state)

async def run_qa_validation(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 9: Final QA with ReAct Conductor"""
    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    qa_stack = QAValidationStack(context)
    qa_patch = await qa_stack.run_from_state_async(state, workflow_id)
    log_event("QAStack", "completed", {"workflow_id": workflow_id})
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, qa_patch)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_qa_validation", state)


async def run_arbitration_after_qa(state: dict, workflow_context: WorkflowContext) -> dict:
    """Arbitration node after QA validation."""

    report = await workflow_context.arbitration_engine.run_check("qa_post_validation", state)
    _attach_arbitration_report(state, "qa_post_validation", report)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_arbitration_after_qa", state)

async def run_constitutional_review(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 9.5: Constitutional Review (v10.7 Fix #30)"""
    context = workflow_context
    safety_stack = SafetyStackV10_8(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', context.workflow_id)
    review_patch = await safety_stack.constitutional_review_from_state_async(
        state,
        workflow_id,
    )
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    adapter = StateAdapterStack(context)
    new_state = adapter.apply_patch(state, review_patch)
    return node_success("run_constitutional_review", new_state)

# HIL Nodes
async def run_feedback_router(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 11: HIL Feedback Router"""
    context = workflow_context
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    if not _is_hil_runtime_enabled(workflow_context):
        logger.info("HIL disabled; skipping feedback routing.")
        return state
    hil_stack = HILStackV10_8(context)
    hil_patch = await hil_stack.route_from_state_async(state, workflow_id)
    log_event("HILStack", "completed", {"workflow_id": workflow_id, "next_step": hil_patch.get("hil", {}).get("next_step")})
    adapter = StateAdapterStack(context)
    state = adapter.apply_patch(state, hil_patch)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return state

def human_in_the_loop_node(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 10: HIL Pause"""
    if not _is_hil_runtime_enabled(workflow_context):
        logger.info("HIL disabled or unavailable. Skipping pause.")
        return node_success("HIL_PAUSE", state)
    if not HIL_AVAILABLE:
        logger.warning("human_in_the_loop dependency missing. Skipping pause.")
        return node_success("HIL_PAUSE", state)
    try:
        human_in_the_loop(timeout=3600)
    except GraphRecursionError:
        logger.info("HIL pause interrupted by user feedback.")
    except Exception as e:
        logger.error(f"HIL node failed: {e}")
    return node_success("HIL_PAUSE", state)

async def run_inject_hil_edit(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 12: Inject HIL Edits"""
    context = workflow_context
    logger.info("Injecting human-in-the-loop edits...")
    if not _is_hil_runtime_enabled(workflow_context):
        logger.info("HIL disabled; skipping edit injection.")
        return node_success("run_inject_hil_edit", state)
    hil_stack = HILStackV10_8(context)
    patch = await hil_stack.inject_edit_from_state_async(
        state,
        state.get('metadata', {}).get('workflow_id', ''),
    )
    if not patch:
        logger.warning("HIL INJECT_EDIT route chosen, but no payload found.")
        if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
            profile = workflow_context.tuning_profile
            new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
            workflow_context.tuning_profile = new_profile
        return node_success("run_inject_hil_edit", state)
    adapter = StateAdapterStack(context)
    new_state = adapter.apply_patch(state, patch)
    logger.info("HIL edit injected into draft summary.")

    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    return node_success("run_inject_hil_edit", new_state)


async def run_reconcile_specialists(state: dict, workflow_context: WorkflowContext) -> dict:
    """Node 11.5: Reconcile specialist contributions."""
    context = workflow_context
    if not _is_hil_runtime_enabled(workflow_context):
        logger.info("HIL disabled; skipping specialist reconciliation.")
        return node_success("run_reconcile_specialists", state)
    hil_stack = HILStackV10_8(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    reconciliation_patch = await hil_stack.reconcile_from_state_async(state, workflow_id)
    if workflow_context.policy_auto_tuner and workflow_context.policy_auto_tuner.enabled():
        profile = workflow_context.tuning_profile
        new_profile = workflow_context.policy_auto_tuner.tune_profile(profile)
        workflow_context.tuning_profile = new_profile
    adapter = StateAdapterStack(context)
    new_state = adapter.apply_patch(state, reconciliation_patch)
    return node_success("run_reconcile_specialists", new_state)

# --- CONDITIONAL EDGES (v10.7: Fix #30) ---

def check_prompt_injection(result: dict) -> str:
    """Node 0.5 conditional"""
    state = _extract_node_payload(result)
    if state.get("safety", {}).get("injection_detected", False):
        logger.error(f"!!! PROMPT INJECTION DETECTED. Halting workflow. !!!")
        return "injection_detected"
    return "injection_safe"

def check_ambiguity(result: dict) -> str:
    """Node 3 conditional: Route to HIL or continue"""
    state = _extract_node_payload(result)
    report = state.get("hil", {}).get("ambiguity_report", {})
    if report.get("ambiguity_detected", False):
        return "pause_for_human"
    return "continue_workflow"

def check_bullets_passed(result: dict, workflow_context: WorkflowContext) -> str:
    """Node 7 conditional driven primarily by arbitration decisions."""

    state = _extract_node_payload(result)
    robustness = _get_robustness_stack(workflow_context)
    route, has_report = _read_arbitration_route(state, "bullets_post_selection")

    if route == "GLOBAL_REPLAN":
        return "global_replanner"

    if route == "RETRY_BULLETS":
        if robustness.should_retry("bullets_quality", "arbitration_retry"):
            return "retry_bullets"
        return "global_replanner"

    if route in ("", "ACCEPT") and has_report:
        robustness.reset("bullets_quality")
        return "bullets_passed"

    # Fallback: arbitration report missing, so fall back to legacy heuristics.
    critiques = state.get('bullets', {}).get('critiqued_bullets', [])
    if not critiques:
        return "global_replanner"

    avg_score = sum(b.get('critique', {}).get('score', 0) for b in critiques) / max(len(critiques), 1)
    if avg_score >= 7.0:
        robustness.reset("bullets_quality")
        return "bullets_passed"

    if robustness.should_retry("bullets_quality", "score_below_threshold"):
        return "retry_bullets"

    return "global_replanner"


def check_qa_passed(result: dict, workflow_context: WorkflowContext) -> str:
    """Node 9 conditional prioritizing arbitration + centralized resilience."""

    state = _extract_node_payload(result)
    robustness = _get_robustness_stack(workflow_context)
    route, has_report = _read_arbitration_route(state, "qa_post_validation")

    if route == "GLOBAL_REPLAN":
        return "global_replanner"

    if route in {"RETRY_QA", "RETRY_DRAFTING"}:
        if robustness.should_retry("qa_validation", "arbitration_retry"):
            return "retry_drafting"
        return "global_replanner"

    if route in ("", "ACCEPT") and has_report:
        robustness.reset("qa_validation")
        return "qa_passed"

    # Fallback legacy heuristic when arbitration signal is missing.
    if state.get('qa', {}).get('qa_passed', False):
        robustness.reset("qa_validation")
        return "qa_passed"

    if robustness.should_retry("qa_validation", "qa_failed"):
        return "retry_drafting"

    return "global_replanner"

def check_constitution(result: dict) -> str:
    """Node 9.5 conditional: Check constitutional review (v10.7 Fix #30)"""
    state = _extract_node_payload(result)
    review = state.get('qa', {}).get('constitutional_review', {})
    if review.get("review_passed", False):
        return "passed_constitution"
    else:
        logger.error(f"!!! CONSTITUTIONAL REVIEW FAILED. Halting workflow. !!!")
        logger.error(f"Violations: {review.get('violations_found')}")
        return "failed_constitution"

def route_feedback(result: dict) -> str:
    """Node 11 conditional: Route based on human feedback"""
    state = _extract_node_payload(result)
    next_step = state.get("hil", {}).get("next_step", "DRAFTING")
    if next_step == "STRATEGY": return "to_strategy"
    if next_step == "BULLET_GENERATION": return "to_bullets"
    if next_step == "INJECT_EDIT": return "to_inject_edit"
    if next_step == "DELEGATE_SPECIALIST": return "to_delegation"
    return "to_drafting"


def check_hil_reentry_allowed(result: dict, workflow_context: WorkflowContext) -> str:
    """Conditional guard to stop the graph when HIL loop bounds are exceeded."""
    state = _extract_node_payload(result)

    if not _is_hil_runtime_enabled(workflow_context):
        return "halt"

    if state.get("hil", {}).get("max_reentry_reached"):
        return "halt"

    max_loops = _get_hil_max_reentry_loops(workflow_context)
    retries = _get_current_hil_retries(state)
    if retries <= max_loops:
        return "continue"
    return "halt"


def _append_hil_a2a(state: dict, message_type: str, payload: Dict[str, Any]) -> None:
    channel = state.setdefault("a2a", {})
    messages = channel.setdefault("messages", [])
    messages.append(
        {
            "sender": "HILRouter",
            "recipient": "ALL",
            "message_type": message_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


DEFAULT_MAX_HIL_REENTRY_LOOPS = 1


def _get_hil_max_reentry_loops(workflow_context: WorkflowContext) -> int:
    """Read the configured HIL loop budget, defaulting to a conservative value."""

    hil_config = getattr(getattr(workflow_context, "config", None), "hil_config", None)
    raw_value = getattr(hil_config, "max_reentry_loops", None)
    try:
        loops = int(raw_value)
    except (TypeError, ValueError):
        loops = DEFAULT_MAX_HIL_REENTRY_LOOPS
    return max(1, loops)


def _get_current_hil_retries(state: dict) -> int:
    return int(state.get("metadata", {}).get("retries", {}).get("hil_retries", 0))


def _hil_stack_configured(workflow_context: WorkflowContext) -> bool:
    config = getattr(workflow_context, "config", None)
    if not config:
        return False
    hil_config = getattr(config, "hil_config", None)
    hil_enabled = getattr(hil_config, "enabled", True) if hil_config else True
    agent_stacks = getattr(config, "agent_stacks", None)
    hil_stack_enabled = getattr(agent_stacks, "enable_hil_stack", False) if agent_stacks else False
    return bool(hil_enabled and hil_stack_enabled)


def _is_hil_runtime_enabled(workflow_context: WorkflowContext) -> bool:
    runtime_flag = getattr(workflow_context, "hil_runtime_enabled", None)
    if runtime_flag is not None:
        return bool(runtime_flag)
    return bool(_hil_stack_configured(workflow_context))


def increment_hil_retries(state: dict, workflow_context: WorkflowContext) -> bool:
    """Increment the HIL retry counter and signal whether another loop is permitted."""

    hil_cfg = getattr(getattr(workflow_context, "config", None), "hil_config", None)
    max_loops = getattr(hil_cfg, "max_reentry_loops", DEFAULT_MAX_HIL_REENTRY_LOOPS)
    try:
        max_loops_int = max(1, int(max_loops))
    except (TypeError, ValueError):
        max_loops_int = DEFAULT_MAX_HIL_REENTRY_LOOPS

    retries = state.setdefault("metadata", {}).setdefault("retries", {})
    current = int(retries.get("hil_retries", 0)) + 1
    retries["hil_retries"] = current

    return current <= max_loops_int


async def run_prepare_hil_strategy_reentry(state: dict, workflow_context: WorkflowContext) -> dict:
    """Bounded re-entry prep for the Strategy stack."""
    workflow_id = state.get('metadata', {}).get('workflow_id', workflow_context.workflow_id)
    if not _is_hil_runtime_enabled(workflow_context):
        return node_success("run_prepare_hil_strategy_reentry", state)

    within_limit = increment_hil_retries(state, workflow_context)
    if not within_limit:
        hil_state = state.setdefault("hil", {})
        hil_state["max_reentry_reached"] = True
        log_event(
            "HILStack",
            "max_reentry_reached",
            {
                "workflow_id": workflow_id,
                "route": "strategy",
                "max_reentry_loops": _get_hil_max_reentry_loops(workflow_context),
                "hil_retries": _get_current_hil_retries(state),
            },
        )
        return node_success("run_prepare_hil_strategy_reentry", state)

    _append_hil_a2a(state, "HIL_REENTRY_STRATEGY", {"workflow_id": workflow_id})
    log_event("HILStack", "strategy_reentry", {"workflow_id": workflow_id})
    scm = getattr(workflow_context, "self_correction_manager", None)
    if scm:
        scm.register_signal(
            workflow_id,
            "hil",
            {"route": "strategy"},
        )
    hil_state = state.setdefault("hil", {})
    hil_state["next_step"] = "STRATEGY"
    return node_success("run_prepare_hil_strategy_reentry", state)


async def run_prepare_hil_drafting_reentry(state: dict, workflow_context: WorkflowContext) -> dict:
    """Bounded re-entry prep for the Drafting stack."""
    workflow_id = state.get('metadata', {}).get('workflow_id', workflow_context.workflow_id)
    if not _is_hil_runtime_enabled(workflow_context):
        return node_success("run_prepare_hil_drafting_reentry", state)

    within_limit = increment_hil_retries(state, workflow_context)
    if not within_limit:
        hil_state = state.setdefault("hil", {})
        hil_state["max_reentry_reached"] = True
        log_event(
            "HILStack",
            "max_reentry_reached",
            {
                "workflow_id": workflow_id,
                "route": "drafting",
                "max_reentry_loops": _get_hil_max_reentry_loops(workflow_context),
                "hil_retries": _get_current_hil_retries(state),
            },
        )
        return node_success("run_prepare_hil_drafting_reentry", state)

    _append_hil_a2a(state, "HIL_REENTRY_DRAFTING", {"workflow_id": workflow_id})
    log_event("HILStack", "drafting_reentry", {"workflow_id": workflow_id})
    scm = getattr(workflow_context, "self_correction_manager", None)
    if scm:
        scm.register_signal(
            workflow_id,
            "hil",
            {"route": "drafting"},
        )
    hil_state = state.setdefault("hil", {})
    hil_state["next_step"] = "DRAFTING"
    return node_success("run_prepare_hil_drafting_reentry", state)

# ============================================================================
# LANGGRAPH WORKFLOW BUILDER (Design-Aligned v10.7: Fix #5, #30)
# ============================================================================

def get_graph_app(
    checkpointer: Any,
    workflow_context: WorkflowContext,
    enable_hil: bool = True,
    *,
    enable_mcp: Optional[bool] = None,
):
    """Build complete LangGraph workflow with v10.7 resilience."""

    hil_runtime_enabled = bool(enable_hil and _hil_stack_configured(workflow_context))
    workflow_context.hil_runtime_enabled = hil_runtime_enabled

    if enable_mcp is not None:
        workflow_context.wrap_mcp_nodes = enable_mcp
        if not enable_mcp:
            workflow_context.reset_mcp_clients()

    workflow = StateGraph(dict)

    def register_node(
        name: str,
        func: Callable[..., Awaitable[Dict[str, Any]]],
        *,
        enable_timeout: bool = True,
        enable_robustness: bool = True,
        enable_mcp: bool = True,
    ) -> None:
        add_node_with_policies(
            workflow,
            name,
            func,
            workflow_context,
            enable_timeout=enable_timeout,
            enable_robustness=enable_robustness,
            enable_mcp=enable_mcp,
        )

    # --- ADD NODES (v10.7: Added new nodes) ---
    register_node("run_sanitize_pii", run_sanitize_pii) # 0
    register_node("run_detect_prompt_injection", run_detect_prompt_injection) # 0.5
    register_node("run_classify_complexity", run_classify_complexity) # 1
    register_node("run_tot_strategy", run_tot_strategy) # 2
    register_node("run_arbitration_after_strategy", run_arbitration_after_strategy)
    register_node("run_detect_ambiguity", run_detect_ambiguity) # 3
    # prepare_parallel_run is synchronous fan-out prep; no resilience/MCP wrapping.
    register_node(
        "prepare_parallel_run",
        prepare_parallel_run,
        enable_timeout=False,
        enable_robustness=False,
        enable_mcp=False,
    ) # 3.5 (Fix #5)
    register_node("run_prompt_builder", run_prompt_builder)
    register_node("run_prompt_renderer", run_prompt_renderer)
    register_node("run_prompt_engineering", run_prompt_engineering) # 4
    register_node("run_rag_stack", run_rag_stack) # 5
    # join_rag_and_prompt is a synchronous merge helper and remains unwrapped.
    register_node(
        "join_rag_and_prompt",
        join_rag_and_prompt,
        enable_timeout=False,
        enable_robustness=False,
        enable_mcp=False,
    ) # 5.5 (Fix #5)
    register_node("run_arbitration_after_join", run_arbitration_after_join)
    register_node("run_generate_bullets", run_generate_bullets) # 6
    register_node("run_critique_bullets", run_critique_bullets) # 7
    register_node("run_arbitration_after_bullets", run_arbitration_after_bullets)
    register_node("run_drafting", run_drafting) # 8
    register_node("run_arbitration_after_drafting", run_arbitration_after_drafting)
    register_node("run_qa_validation", run_qa_validation) # 9
    register_node("run_arbitration_after_qa", run_arbitration_after_qa)
    register_node("run_constitutional_review", run_constitutional_review) # 9.5 (Fix #30)
    # HIL pause is a UI-only barrier; keep it synchronous with no extra wrapping.
    register_node(
        "HIL_PAUSE",
        human_in_the_loop_node,
        enable_timeout=False,
        enable_robustness=False,
        enable_mcp=False,
    ) # 10
    register_node("run_feedback_router", run_feedback_router) # 11
    register_node(
        "run_prepare_hil_strategy_reentry",
        run_prepare_hil_strategy_reentry,
        enable_robustness=False,
    )
    register_node(
        "run_prepare_hil_drafting_reentry",
        run_prepare_hil_drafting_reentry,
        enable_robustness=False,
    )
    register_node("run_reconcile_specialists", run_reconcile_specialists) # 11.5
    register_node("run_inject_hil_edit", run_inject_hil_edit) # 12
    
    # --- CONNECT NODES (v10.7: Rerouted for new nodes) ---
    workflow.set_entry_point("run_sanitize_pii")
    workflow.add_edge("run_sanitize_pii", "run_detect_prompt_injection") # 0 -> 0.5
    
    workflow.add_conditional_edges(
        "run_detect_prompt_injection", check_prompt_injection,
        {"injection_detected": END, "injection_safe": "run_classify_complexity"}
    ) # 0.5 -> 1 or END
    
    workflow.add_edge("run_classify_complexity", "run_tot_strategy") # 1 -> 2

    new_prompt_path = bool(getattr(workflow_context, "enable_v10_8_prompts", False))

    if new_prompt_path:
        workflow.add_edge("run_tot_strategy", "run_prompt_builder")
        workflow.add_edge("run_prompt_builder", "run_prompt_renderer")
        workflow.add_edge("run_prompt_renderer", "run_rag_stack")
        workflow.add_edge("run_prompt_renderer", "run_generate_bullets")
        workflow.add_edge("run_prompt_renderer", "run_drafting")
    else:
        workflow.add_edge("run_tot_strategy", "run_arbitration_after_strategy") # 2 -> arbitration
        workflow.add_edge("run_arbitration_after_strategy", "run_detect_ambiguity") # arbitration -> 3

        # v10.7 (Fix #5): Reroute for parallel execution
        workflow.add_conditional_edges(
            "run_detect_ambiguity", check_ambiguity,
            {"pause_for_human": "HIL_PAUSE", "continue_workflow": "prepare_parallel_run"}
        ) # 3 -> 10 or 3.5

        workflow.add_edge("prepare_parallel_run", "run_prompt_engineering") # 3.5 -> 4
        workflow.add_edge("prepare_parallel_run", "run_rag_stack") # 3.5 -> 5
        workflow.add_edge("run_prompt_engineering", "join_rag_and_prompt") # 4 -> 5.5

    workflow.add_edge("run_rag_stack", "join_rag_and_prompt") # 5 -> 5.5
    workflow.add_edge("join_rag_and_prompt", "run_arbitration_after_join") # 5.5 -> arbitration
    workflow.add_edge("run_arbitration_after_join", "run_generate_bullets") # arbitration -> 6
    
    workflow.add_edge("run_generate_bullets", "run_critique_bullets") # 6 -> 7

    workflow.add_conditional_edges(
        "run_critique_bullets", partial(check_bullets_passed, workflow_context=workflow_context),
        {"bullets_passed": "run_arbitration_after_bullets", "retry_bullets": "run_generate_bullets", "global_replanner": END}
    ) # 7 -> arbitration or 6 or END

    workflow.add_edge("run_arbitration_after_bullets", "run_drafting") # arbitration -> 8

    workflow.add_edge("run_drafting", "run_arbitration_after_drafting") # 8 -> arbitration
    workflow.add_edge("run_arbitration_after_drafting", "run_qa_validation") # arbitration -> 9
    
    # v10.7 (Fix #30): Reroute for constitutional review
    workflow.add_edge("run_qa_validation", "run_arbitration_after_qa") # 9 -> arbitration

    workflow.add_conditional_edges(
        "run_arbitration_after_qa", partial(check_qa_passed, workflow_context=workflow_context),
        {
            "qa_passed": "run_constitutional_review", # 9 -> 9.5
            "retry_drafting": "run_drafting", # 9 -> 8
            "global_replanner": END
        }
    )
    
    workflow.add_conditional_edges(
        "run_constitutional_review", check_constitution,
        {
            "passed_constitution": "HIL_PAUSE" if hil_runtime_enabled else END, # 9.5 -> 10 or END
            "failed_constitution": END # Fail the job
        }
    )
    
    workflow.add_edge("HIL_PAUSE", "run_feedback_router") # 10 -> 11
    
    workflow.add_conditional_edges(
        "run_feedback_router", route_feedback,
        {
            "to_strategy": "run_prepare_hil_strategy_reentry",
            "to_bullets": "run_generate_bullets",
            "to_drafting": "run_prepare_hil_drafting_reentry",
            "to_inject_edit": "run_inject_hil_edit",
            "to_delegation": "run_reconcile_specialists"
        }
    )

    workflow.add_conditional_edges(
        "run_prepare_hil_strategy_reentry",
        partial(check_hil_reentry_allowed, workflow_context=workflow_context),
        {"continue": "run_tot_strategy", "halt": END},
    )

    workflow.add_conditional_edges(
        "run_prepare_hil_drafting_reentry",
        partial(check_hil_reentry_allowed, workflow_context=workflow_context),
        {"continue": "run_drafting", "halt": END},
    )
    workflow.add_edge("run_reconcile_specialists", "run_inject_hil_edit") # 11.5 -> 12

    workflow.add_edge("run_inject_hil_edit", "run_qa_validation") # 12 -> 9 (Re-run QA)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# END OF agent_orchestration_v10_7.py
# ============================================================================
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/agent_orchestration_v.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/main_v.py (sha256=69566bc91fa87e488957667585413079a485a2fdbe1d6aeb88688af79681e0e6) ====
# --- Vendor path bootstrap for Codex offline environment ---
import sys
import os

VENDOR_PATH = os.path.join(os.path.dirname(__file__), "vendor")
# Only load vendor stubs when explicitly testing
if os.environ.get("USE_VENDOR_STUBS") == "1":
    if VENDOR_PATH not in sys.path:
        sys.path.insert(0, VENDOR_PATH)


# File: main_v10_7.py
# Version: 10.7 (Refactored)
#
# v10.7 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_7.
# - UPDATED: create_workflow_context call updated to v10_7.
#
# v10.7 MAJOR CHANGES:
# - IMPLEMENTED (Fix #9): run_workflow_async refactored to use
#   `app.astream_events` to listen for `on_chat_model_stream` events.
#   This now prints real-time streaming tokens (thoughts, partial JSON)
#   from the ReAct conductors.
# - IMPLEMENTED (Fix #30): Checks for 'failed_constitution' in the
#   final state to correctly report constitutional failures.
# - FIXED: All v10_5 imports and class names updated to v10_7.
# - FIXED: Changed config file name to master_config_v10_7.json.

import os
import sys
import json
import logging
import asyncio
import argparse
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack

# v10.7: Import from new core
from core_v10_7 import (
    ConfigV10_7, WorkflowContext, MainGraphState,
    FileIOError, CostCeilingExceededError, WorkflowError,
    create_workflow_context, cleanup_workflow_chroma_collection,
    get_checkpointer
)
# v10.7: Import from new orchestration/stacks
from agent_orchestration_v10_7 import get_graph_app, unwrap_node_result

# v10.7: Logger name updated
logger = logging.getLogger("main_v10_7")

def setup_logging(config: ConfigV10_7, debug_mode: bool = False):
    """Configure logging, now accepts a config object."""
    log_dir = os.path.dirname(config.logging_config.log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    level = logging.DEBUG if debug_mode else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logging_config.log_file),
            logging.StreamHandler(sys.stdout) # v10.7: Log to stdout for streaming
        ]
    )
    
    # Configure metrics logger
    metrics_log_path = config.logging_config.metrics_log_path
    metrics_logger = logging.getLogger("core_v10_7.MetricsCollector")
    metrics_logger.setLevel(logging.INFO)
    try:
        metrics_logger.addHandler(logging.FileHandler(metrics_log_path))
    except (IOError, OSError) as e:
        logging.error(f"Failed to add file handler for metrics logger: {e}")
    
    logger.info(f"v10.7 Logging initialized: {config.logging_config.log_file}")
    logger.info(f"v10.7 Metrics logging to: {metrics_log_path}")

def load_job_input(path: str) -> Dict[str, Any]:
    """Load job input JSON"""
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded job input: {path}")
        return data
    except (IOError, OSError) as e:
        raise FileIOError(f"Failed to load {path}: {e}")
    except json.JSONDecodeError as e:
        raise FileIOError(f"Invalid JSON in {path}: {e}")

async def run_workflow_async(
    config: ConfigV10_7,
    job_input_path: str,
    master_resume_path: str,
    debug_mode: bool = False,
    enable_hil: bool = True,
    enable_mcp: Optional[bool] = None,
    compat_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Run workflow asynchronously with v10.7 streaming and validation"""
    
    logger.info(f"===== Starting v10.7 Instructional Injection Workflow =====")
    
    job_input_data = load_job_input(job_input_path)
    master_resume = load_job_input(master_resume_path)
    
    company = job_input_data.get('company_name', 'N/A')
    title = job_input_data.get('job_title', 'N/A')
    
    logger.info(f"Job: {company} - {title}")
    
    # --- v10.7: REFACTOR: COMPOSITION ROOT ---
    context = create_workflow_context(config, db=config.redis_config.db)
    # --- v10.7: REFACTOR END ---

    checkpointer = get_checkpointer(config)
    
    context.enable_v10_8_prompts = compat_mode != "v10_7"

    app = get_graph_app(checkpointer, context, enable_hil=enable_hil, enable_mcp=enable_mcp)
    
    workflow_id = str(uuid.uuid4())
    context.workflow_id = workflow_id
    run_config = {"configurable": {"thread_id": workflow_id}}

    initial_state = MainGraphState()
    initial_state.resume.master_resume = master_resume
    initial_state.job.raw_jd = job_input_data['job_description']
    initial_state.job.company = job_input_data['company_name']
    initial_state.job.job_title = job_input_data['job_title']
    initial_state.metadata.workflow_id = workflow_id

    state_dict = initial_state.to_dict()

    adapter = StateAdapterStack(context, debug_mode)
    episodic_conversation = state_dict.get("memory", {}).get("episodic", {}).get(
        "conversation", []
    )
    conversation_patch = adapter.patch_memory(
        conversation=list(episodic_conversation)
        + [
            {
                "role": "user",
                "type": "job_description",
                "content": job_input_data.get("job_description", ""),
            },
            {
                "role": "user",
                "type": "master_resume",
                "content": master_resume,
            },
        ]
    )
    state_dict = adapter.apply_patch(state_dict, conversation_patch)
    
    logger.info(f"Workflow ID: {workflow_id}")
    
    try:
        final_state_dict = None
        
        # v10.7 (Fix #9): Use astream_events for real-time streaming
        current_node = ""
        print("\n--- Workflow Stream (v10.7) ---", flush=True)
        
        async for event in app.astream_events(state_dict, run_config, version="v1"):
            kind = event["event"]
            
            if kind == "on_graph_start":
                logger.info(f"Graph execution started.")
            
            if kind == "on_node_start":
                current_node = event["data"]["name"]
                logger.info(f"\n--- Executing Node: {current_node} ---")

            # v10.7 (Fix #9): Handle real-time token streaming
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    # Print the streaming token to stdout
                    print(chunk.content, end="", flush=True)
            
            if kind == "on_node_end":
                # Do NOT extract partial state here.
                # Node-end events only indicate completion; they do not carry final graph state.
                pass
                
                if current_node == "HIL_PAUSE":
                    print("\n", flush=True) # Newline after streaming
                    logger.warning("="*80)
                    logger.warning("🛑 WORKFLOW PAUSED: HUMAN INPUT REQUIRED 🛑")
                    logger.warning(f"Please review and provide feedback for: {workflow_id}")
                    logger.warning("="*80)
            
            if kind == "on_graph_end":
                final_output = event["data"]["output"]
                final_state_dict = unwrap_node_result(final_output)
                print("\n--- Workflow Stream Complete ---", flush=True)

        if final_state_dict is None:
            raise WorkflowError("Graph stream finished with no final state.")
        
        # v10.7: Check for rejection
        if "REJECT_JOB" in final_state_dict:
             logger.error(f"Workflow {workflow_id} REJECTED.")
             raise WorkflowError("Workflow rejected, likely due to prompt injection.")
        
        # v10.7 (Fix #30): Check for constitutional failure
        cr = final_state_dict.get("qa", {}).get("constitutional_review")
        if isinstance(cr, dict) and cr.get("review_passed") is False:   
             logger.error(f"Workflow {workflow_id} FAILED CONSTITUTIONAL REVIEW.")
             raise WorkflowError("Workflow rejected due to constitutional failure.")

        final_state = MainGraphState.from_dict(final_state_dict)
        
        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Cache performance: {cache_stats}")
        
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Total workflow cost: ${cost_summary['total_workflow_cost']:.4f}")
        
        logger.info(f"--- Workflow Metrics Summary (v10.7) ---")
        for metric in context.metrics_collector.get_summary():
             logger.info(f"  - {metric['agent_name']}::{metric['task_name']} | {metric['duration_ms']:.2f}ms | Success: {metric['success']}")
        
        # v10.7 REFACTOR: Call centralized cleanup helper
        cleanup_workflow_chroma_collection(context)

        os.makedirs("outputs", exist_ok=True)

        with open("outputs/final_resume.json", "w") as f:
            json.dump(final_state.artifacts.artifacts.get("final_resume", {}), f, indent=2)

        with open("outputs/qa_report.json", "w") as f:
            json.dump(final_state.artifacts.artifacts.get("qa_report", {}), f, indent=2)

        print("\u2713 Saved final resume to outputs/final_resume.json")
        print("\u2713 Saved QA report to outputs/qa_report.json")

        return {
            "status": "SUCCESS",
            "workflow_id": workflow_id,
            "cost": cost_summary['total_workflow_cost'],
            "cache_stats": cache_stats,
            "final_artifacts": final_state.artifacts.artifacts
        }
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        return {
            "status": "FAILED_FATAL",
            "workflow_id": workflow_id,
            "error": str(e)
        }
    
    finally:
        logger.info(f"===== v10.7 Workflow Complete =====")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Resume Generation Engine v10.7")
    parser.add_argument('-j', '--job', required=True, help='Path to job_input.json')
    parser.add_argument('-m', '--master', required=True, help='Path to master_resume.json')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-hil', action='store_true', help='Disable Human-in-the-Loop')
    parser.add_argument('--sim', type=str, help='Run a simulation instead of workflow')

    mcp_group = parser.add_mutually_exclusive_group()
    mcp_group.add_argument('--disable-mcp', action='store_true', help='Disable MCP wrapping even if config enables it')
    mcp_group.add_argument('--enable-mcp', action='store_true', help='Force enable MCP wrapping even if config disables it')
    
    args = parser.parse_args()
    
    # v10.7: Instantiate ConfigV10_7 here, ONCE.
    try:
        config = ConfigV10_7("master_config_v10_7.json")
    except Exception as e:
        print(f"FATAL: Failed to load master_config_v10_7.json: {e}", file=sys.stderr)
        sys.exit(1)
    
    setup_logging(config, debug_mode=args.debug)

    if args.sim:
        from simulations.runner import run_simulation

        payload = load_job_input(args.job)
        payload = dict(payload)
        payload.setdefault("simulation_id", str(uuid.uuid4()))
        result = asyncio.run(run_simulation(args.sim, payload))
        print(json.dumps(result.model_dump(), indent=2))
        return
    
    mcp_toggle: Optional[bool] = None
    if args.disable_mcp:
        mcp_toggle = False
    elif args.enable_mcp:
        mcp_toggle = True

    result = asyncio.run(run_workflow_async(
        config=config,
        job_input_path=args.job,
        master_resume_path=args.master,
        debug_mode=args.debug,
        enable_hil=not args.no_hil,
        enable_mcp=mcp_toggle
    ))
    
    print("\n" + "="*80)
    print(f"WORKFLOW RESULT: {result['status']}")
    print(f"Workflow ID: {result.get('workflow_id')}")
    if result.get('status') == 'SUCCESS':
        print(f"Total Cost: ${result.get('cost', 0.0):.4f}")
        print(f"Cache Stats: {result.get('cache_stats')}")
    else:
        print(f"Error: {result.get('error')}")
    print("="*80)
    
    if result['status'] == 'SUCCESS':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

# ============================================================================
# END OF main_v10_7.py
# ============================================================================
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/main_v.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/run_batch_v.py (sha256=4e9f86f7a8d738c4333c7cb7d95ac7c45062064e45c6dd5e014f1a696c548f38) ====
# --- Vendor path bootstrap for Codex offline environment ---
import sys
import os

VENDOR_PATH = os.path.join(os.path.dirname(__file__), "vendor")
if VENDOR_PATH not in sys.path:
    sys.path.insert(0, VENDOR_PATH)

# File: run_batch_v10_7.py
# Version: 10.7 (Refactored)
#
# v10.7 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_7 (e.g., core_v10_7, ConfigV10_7).
# - UPDATED: create_workflow_context call updated to v10_7.
#
# v10.7 MAJOR CHANGES:
# - IMPLEMENTED (Fix #25): Added backpressure check. The batch
#   will not run if the number of files in BATCH_QUEUE_DIR
#   exceeds config.batch_config.max_batch_queue_size.
# - FIXED: All v10_5 imports and class names updated to v10_7.

import os
import csv
import logging
import shutil
import asyncio
import uuid
import sys
from datetime import datetime
from typing import Any, Dict, List

# v10.7: Import from new main/core
from main_v10_7 import setup_logging, load_job_input
from core_v10_7 import (
    ConfigV10_7,
    ContextBudgetManager,
    CircuitBreaker,
    CircuitBreakerOpenError,
    MainGraphState,
    WorkflowContext,
    WorkflowError,
    cleanup_workflow_chroma_collection,
    create_workflow_context,
    get_checkpointer,
)
# v10.7: Import from new orchestration/stacks
from agent_orchestration_v10_7 import get_graph_app, unwrap_node_result

try:
    # v10.7: Import new meta-learner
    from run_learning_v10_7 import run_meta_learning
    META_LEARNER_AVAILABLE = True
except ImportError:
    META_LEARNER_AVAILABLE = False
    logging.getLogger("batch_runner_v10_7").warning("Meta-learning module (run_learning_v10_7.py) not found.")

logger = logging.getLogger("batch_runner_v10_7")

BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v10_7.csv"

# ============================================================================
# ROW 7: BATCH FEEDBACK AGGREGATOR (Preserved)
# ============================================================================

class BatchFeedbackAggregator:
    """ROW 7: Aggregates feedback across batch jobs"""
    def __init____src3(self):
        self.job_results: List[Dict[str, Any]] = []
    
    def add_job_result(self, result: Dict[str, Any]):
        self.job_results.append(result)
    
    def get_batch_summary(self) -> Dict[str, Any]:
        if not self.job_results:
            return {}

        total_jobs = len(self.job_results)
        successful = sum(
            1 for result in self.job_results if result["status"] == "SUCCESS"
        )
        total_cost = sum(result.get("cost", 0.0) for result in self.job_results)
        avg_cost = total_cost / total_jobs if total_jobs > 0 else 0.0
        success_rate = successful / total_jobs if total_jobs > 0 else 0.0

        return {
            "timestamp": datetime.now().isoformat(),
            "total_jobs": total_jobs,
            "successful": successful,
            "success_rate": success_rate,
            "total_cost": total_cost,
            "avg_cost_per_job": avg_cost,
            "batch_health_score": success_rate * 100,
        }

# ============================================================================
# ROW 6: ASYNC BATCH PROCESSING ENGINE (v10.7)
# ============================================================================

async def process_single_job_async(
    job_file: str,
    master_resume_path: str,
    context: WorkflowContext, # v10.7: This is the JOB-SPECIFIC context
    app, # The compiled graph app
    circuit_breaker: CircuitBreaker,
    batch_aggregator: BatchFeedbackAggregator
) -> Dict[str, Any]:
    """Process a single job asynchronously"""
    
    job_name = os.path.basename(job_file)
    logger.info(f"Processing job: {job_name}")
    
    job_input_data = {}
    workflow_id = str(uuid.uuid4())
    context.workflow_id = workflow_id # Set on job-specific context
    
    try:
        circuit_breaker.check()
        
        job_input_data = load_job_input(job_file)
        master_resume = load_job_input(master_resume_path)
        
        company = job_input_data.get('company_name', 'N/A')
        title = job_input_data.get('job_title', 'N/A')
        
        run_config = {"configurable": {"thread_id": workflow_id}}

        initial_state = MainGraphState()
        initial_state.resume.master_resume = master_resume
        initial_state.job.raw_jd = job_input_data['job_description']
        initial_state.job.company = job_input_data['company_name']
        initial_state.job.job_title = job_input_data['job_title']
        initial_state.metadata.workflow_id = workflow_id
        initial_state.metadata.complexity = "unknown" # Set by graph
        
        state_dict = initial_state.to_dict()
        
        final_state_dict = None
        async for s in app.astream(state_dict, run_config):
            final_state_dict = s[list(s.keys())[0]]

        if final_state_dict is None:
            raise WorkflowError("Workflow returned no final state.")

        final_state_dict = unwrap_node_result(final_state_dict)

        if "REJECT_JOB" in final_state_dict:
             logger.error(f"Workflow {workflow_id} REJECTED.")
             raise WorkflowError("Workflow rejected, likely due to prompt injection or constitutional failure.")

        MainGraphState.from_dict(final_state_dict)
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        total_cost = cost_summary['total_workflow_cost']
        
        complete_path = os.path.join(BATCH_COMPLETE_DIR, job_name)
        shutil.move(job_file, complete_path)
        
        # v10.7 REFACTOR: Call centralized cleanup helper
        cleanup_workflow_chroma_collection(context)

        result = {
            "job_file": job_name, "company_name": company, "job_title": title,
            "status": "SUCCESS", "workflow_id": workflow_id, "cost": total_cost, "error": None
        }
        
        circuit_breaker.record_success()
        batch_aggregator.add_job_result(result)
        logger.info(f"✓ Completed: {company} - {title} (${total_cost:.4f})")
        return result
        
    except (CircuitBreakerOpenError, Exception) as e:
        if not isinstance(e, CircuitBreakerOpenError):
            logger.error(f"✗ Failed job {job_name}: {e}", exc_info=True)
            circuit_breaker.record_failure()
        
        result = {
            "job_file": job_name, "company_name": job_input_data.get('company_name', 'N/A'),
            "job_title": job_input_data.get('job_title', 'N/A'),
            "status": "FAILED_CIRCUIT_BREAKER" if isinstance(e, CircuitBreakerOpenError) else "FAILED_FATAL",
            "workflow_id": workflow_id, "cost": 0.0, "error": str(e)
        }
        batch_aggregator.add_job_result(result)
        return result

async def run_batch_async(config: ConfigV10_7): # v10.7
    """Main async batch processing with semaphore concurrency control"""
    
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
    
    job_files = [
        os.path.join(BATCH_QUEUE_DIR, f) 
        for f in os.listdir(BATCH_QUEUE_DIR) 
        if f.endswith('.json')
    ]
    
    if not job_files:
        logger.info("v10.7 Batch process starting. No jobs found.")
        return
    
    logger.info("===== v10.7 Async Batch Process Starting =====")
    
    # v10.7 (Fix #25): Backpressure Check
    max_queue_size = config.batch_config.max_batch_queue_size
    if len(job_files) > max_queue_size:
        logger.error(f"BACKPRESSURE: Batch queue size ({len(job_files)}) exceeds limit ({max_queue_size}).")
        logger.error("Batch run aborted. Clear queue before retrying.")
        return
        
    logger.info("Found %d jobs in queue (limit: %d)", len(job_files), max_queue_size)
    
    # --- v10.7: REFACTOR: COMPOSITION ROOT ---
    # Create a single, shared context to hold all instantiated services
    shared_context = create_workflow_context(config, db=config.redis_config.db)
    
    # Unpack shared services to be injected into job-specific contexts
    redis_client = shared_context.redis_client
    chromadb_client = shared_context.chromadb_client
    cache_manager = shared_context.cache_manager
    cost_tracker = shared_context.cost_tracker
    feedback_reader = shared_context.feedback_reader
    rules_loader = shared_context.rules_loader
    prompt_manager = shared_context.prompt_manager
    response_validator = shared_context.response_validator
    context_budget_manager = shared_context.context_budget_manager
    metrics_collector = shared_context.metrics_collector
    semantic_validator = shared_context.semantic_validator
    
    checkpointer = get_checkpointer(config)
    # --- v10.7: REFACTOR END ---
    
    batch_aggregator = BatchFeedbackAggregator()
    circuit_breaker = CircuitBreaker(
        failure_threshold=config.batch_config.circuit_breaker_failure_threshold
    )
    
    max_workers = config.batch_config.max_parallel_workers
    semaphore = asyncio.Semaphore(max_workers)
    master_resume_path = config.file_paths.default_master_resume
    
    async def process_with_semaphore(job_file):
        """Process job with semaphore"""
        async with semaphore:
            # v10.7: Create a job-specific context by injecting
            # all the SHARED services created above.
            job_context = WorkflowContext(
                config=config,
                redis_client=redis_client,
                chromadb_client=chromadb_client,
                cache_manager=cache_manager,
                cost_tracker=cost_tracker,
                feedback_reader=feedback_reader,
                rules_loader=rules_loader,
                prompt_manager=prompt_manager,
                response_validator=response_validator,
                context_budget_manager=context_budget_manager,
                metrics_collector=metrics_collector,
                semantic_validator=semantic_validator,
                embedding_function=shared_context.embedding_function
            )
            # v10.7: Manually inject the circular dependency
            job_context.context_budget_manager = ContextBudgetManager(
                config=config,
                model_client_getter=job_context.get_model_client
            )
            
            job_app = get_graph_app(
                checkpointer,
                job_context,
                enable_hil=False,
                enable_mcp=job_context.wrap_mcp_nodes,
            )
            
            return await process_single_job_async(
                job_file,
                master_resume_path,
                job_context, # Pass job-specific context
                job_app,     # Pass job-specific app
                circuit_breaker,
                batch_aggregator
            )
    
    logger.info("Starting parallel processing (%d workers)...", max_workers)
    start_time = datetime.now()
    
    results = await asyncio.gather(*[
        process_with_semaphore(job_file) 
        for job_file in job_files
    ], return_exceptions=True)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info("Processed %d jobs in %.2f seconds", len(results), duration)
    
    # v10.7: Write CSV summary
    batch_summary = batch_aggregator.get_batch_summary()
    if batch_summary:
        summary_path = os.path.join(BATCH_COMPLETE_DIR, SUMMARY_FILE)
        file_exists = os.path.isfile(summary_path)
        try:
            with open(summary_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=batch_summary.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(batch_summary)
            logger.info(f"Wrote batch summary to {summary_path}")
        except IOError as e:
            logger.error(f"Failed to write batch summary: {e}")
    
    logger.info("BATCH PROCESSING COMPLETE (v10.7)")
    logger.info(f"  Total Jobs: {batch_summary.get('total_jobs', 0)}")
    logger.info(f"  Success Rate: {batch_summary.get('success_rate', 0.0):.1%}")
    logger.info(f"  Total Cost: ${batch_summary.get('total_cost', 0.0):.4f}")
    
    # v10.7: Log metrics summary for the *entire* batch
    logger.info("--- Batch Metrics Summary (v10.7) ---")
    for metric in metrics_collector.get_summary():
        logger.info(
            "  - %s::%s | %.2fms | Success: %s",
            metric["agent_name"],
            metric["task_name"],
            metric["duration_ms"],
            metric["success"],
        )
    
    # Optionally trigger meta-learning
    if META_LEARNER_AVAILABLE and config.meta_loop_config.enable_meta_learning:
        logger.info("Triggering meta-learning loop (v10.7)...")
        try:
            # v10.7: Pass the config object to the meta-learner
            await run_meta_learning(config)
        except Exception as e:
            logger.error(f"Meta-learning failed: {e}")
    
    logger.info("v10.7 Batch process complete.")

def run_batch():
    """Synchronous wrapper for async batch processing"""
    # v10.7: Instantiate ConfigV10_7 here, ONCE.
    try:
        config = ConfigV10_7("master_config_v10_7.json")
    except Exception as e:
        print(f"FATAL: Failed to load master_config_v10_7.json: {e}", file=sys.stderr)
        sys.exit(1)
        
    try:
        setup_logging(config, debug_mode=False)
    except Exception as e:
        print(f"Warning: setup_logging failed: {e}")
        logging.basicConfig(level=logging.INFO)
    
    # v10.7: Inject the config object
    asyncio.run(run_batch_async(config))

if __name__ == "__main__":
    run_batch()

# ============================================================================
# END OF run_batch_v10_7.py
# ============================================================================
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/run_batch_v.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/run_learning_v.py (sha256=b21911c70db83c40e5700dadc11b4cdf0a9cea4d9d00d52212e6267a5c4080ba) ====
# --- Vendor path bootstrap for Codex offline environment ---
import sys
import os

VENDOR_PATH = os.path.join(os.path.dirname(__file__), "vendor")
if VENDOR_PATH not in sys.path:
    sys.path.insert(0, VENDOR_PATH)

# File: run_learning_v10_7.py
# Version: 10.7 (Refactored)
#
# v10.7 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_7.
# - UPDATED: create_workflow_context call updated to v10_7.
# - REFACTORED (Fix #14, #17, #19, #20, #24): All async agents
#   (Summarizer, PatternFinder, Hypothesis, etc.) now use the new
#   async `_format_prompt_with_defaults` from core. This injects
#   Cognitive Modes, Goal State, Failure Warnings, and Reflection steps
#   into all meta-learning LLM calls.
#
# v10.7 MAJOR CHANGES:
# - FIXED: All v10_5 imports and class names updated to v10_7.
# - FIXED: State object 'MetaGraphState' (from core) now used.

import json
import logging
import os
import uuid
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Tuple

# v10.7: Import from new core
from core_v10_7 import (
    BaseAgent,
    ConfigV10_7,
    MetaGraphState,
    WorkflowContext,
    WorkflowError,
    create_workflow_context,
    PydanticSchemaError,
    track_metrics,
    _format_prompt_with_defaults, # v10.7: Import async formatter
    get_checkpointer,
    MCPClientStub,
)
from langgraph.graph import StateGraph, END

# v10.7: Logger name updated
logger = logging.getLogger("meta_learner_v10_7")

# ============================================================================
# MODULE HELPERS
# ============================================================================


def _read_log_tail(path: str, limit: int = 50) -> Tuple[str, int]:
    """Return the last ``limit`` lines of ``path`` and a count of entries."""

    if not path or not os.path.exists(path):
        return "", 0

    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except Exception:
        return "", 0

    tail = lines[-limit:]
    if not tail:
        return "", 0

    joined = "\n".join(line.rstrip('\n') for line in tail)
    entry_count = sum(1 for line in tail if line.strip())
    return joined, entry_count


def _count_feedback_entries(config: ConfigV10_7) -> int:
    meta_cfg = getattr(config, "meta_loop_config", None)
    if not meta_cfg:
        return 0
    _, count = _read_log_tail(getattr(meta_cfg, "feedback_log_path", ""))
    return count


def _redis_available(redis_client: Any) -> bool:
    if redis_client is None or isinstance(redis_client, MCPClientStub):
        return False

    ping_fn = getattr(redis_client, "ping", None)
    if not callable(ping_fn):
        return False

    try:  # pragma: no cover - requires Redis
        ping_fn()
        return True
    except Exception:
        return False


# ============================================================================
# ROW 7: HOT-RELOAD RULE MANAGER (Preserved)
# ============================================================================

class HotReloadRuleManager:
    """ROW 7: Manages hot-reload of proposed rules"""
    
    def __init____src4(self, rules_path: str, auto_approve_threshold: float = 0.85):
        self.rules_path = rules_path
        self.auto_approve_threshold = auto_approve_threshold
    
    def write_proposed_rule(self, rule: Dict[str, Any], confidence: float) -> bool:
        try:
            status = "APPROVED" if confidence >= self.auto_approve_threshold else "PROPOSED"
            log_entry = {
                "timestamp": datetime.now().isoformat(), "status": status,
                "confidence": confidence, "pattern": rule,
            }
            os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
            with open(self.rules_path, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
            logger.info(f"Rule written: {rule.get('type', 'unknown')} - Status: {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to write rule: {e}")
            return False

# ============================================================================
# META-LEARNING AGENTS (v10.7: Refactored)
# ============================================================================

class LogReaderAgent(BaseAgent):
    """Reads raw logs from disk"""
    @track_metrics('meta_read_logs')
    def run(self) -> Dict[str, str]:
        self.log_info("Reading feedback and preference logs...")
        logs = {"feedback_log": "", "preference_log": ""}
        feedback_log_path = self.config.meta_loop_config.feedback_log_path
        preference_log_path = self.config.meta_loop_config.preference_log_path

        try:
            feedback_tail, _ = _read_log_tail(feedback_log_path)
            logs["feedback_log"] = feedback_tail
        except Exception:
            pass
        try:
            preference_tail, _ = _read_log_tail(preference_log_path)
            logs["preference_log"] = preference_tail
        except Exception:
            pass
        
        return logs

class AsyncLogSummarizerAgent(BaseAgent):
    """Async LLM-based log summarizer"""
    @track_metrics('meta_summarize_logs')
    async def run_async(self, raw_logs: Dict[str, str], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Summarizing logs with LLM (v10.7)...")
        client = self.get_model_client("qa_model")
        
        prompt_template = self.prompt_manager.get_template("meta_log_reader")
        
        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {
                "feedback_log": raw_logs.get('feedback_log', 'No feedback log'),
                "preference_log": raw_logs.get('preference_log', 'No preference log')
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"LogSummarizer failed validation: {error}")
        
        self.log_feedback(workflow_id, "log_summarization", "success", {})
        return validated_output

class AsyncPatternFinderAgent(BaseAgent):
    """Async pattern detection"""
    @track_metrics('meta_find_patterns')
    async def run_async(self, log_summary: Dict[str, Any], workflow_id: str) -> List[Dict]:
        self.log_info("Finding patterns in logs (v10.7)...")
        client = self.get_model_client("strategy_model")
        
        prompt_template = self.prompt_manager.get_template("meta_pattern_finder")
        
        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"log_data": json.dumps(log_summary)},
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"PatternFinder failed validation: {error}")
            
        patterns = validated_output.get("patterns", [])
        self.log_feedback(workflow_id, "pattern_finding", "success", {"patterns_found": len(patterns)})
        return patterns

class AsyncHypothesisGeneratorAgent(BaseAgent):
    """Async hypothesis generation"""
    @track_metrics('meta_gen_hypotheses')
    async def run_async(self, patterns: List[Dict], previous_critique: Dict[str, Any], workflow_id: str) -> List[Dict]:
        self.log_info("Generating hypotheses (v10.7)...")
        client = self.get_model_client("strategy_model")
        
        prompt_template = self.prompt_manager.get_template("meta_hypothesis_generator")
        
        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {
                "patterns": json.dumps(patterns),
                "critique": json.dumps(previous_critique)
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"HypothesisGenerator failed validation: {error}")
            
        hypotheses = validated_output.get("hypotheses", [])
        self.log_feedback(workflow_id, "hypothesis_generation", "success", {"hypotheses_generated": len(hypotheses)})
        return hypotheses

class AsyncProposalDrafterAgent(BaseAgent):
    """Async proposal drafting"""
    @track_metrics('meta_draft_proposal')
    async def run_async(self, hypothesis: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Drafting proposal for hypothesis (v10.7)...")
        client = self.get_model_client("prompt_engineer_model")
        
        prompt_template = self.prompt_manager.get_template("meta_proposal_drafter")
        
        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"hypothesis": json.dumps(hypothesis)},
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"ProposalDrafter failed validation: {error}")
        
        validated_output["hypothesis_id"] = hypothesis.get("id", "unknown")
        validated_output["confidence"] = hypothesis.get("confidence", 0.5)
        validated_output["hypothesis_type"] = hypothesis.get("type", "rule_change")
        self.log_feedback(workflow_id, "proposal_drafting", "success", {})
        return validated_output

class AsyncProposalCritiqueAgent(BaseAgent):
    """Async proposal critique"""
    @track_metrics('meta_critique_proposal')
    async def run_async(self, proposal: Dict[str, Any], patterns: List[Dict], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Critiquing proposal (v10.7)...")
        client = self.get_model_client("critique_model")
        
        prompt_template = self.prompt_manager.get_template("meta_proposal_critique")
        
        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {
                "patterns": json.dumps(patterns),
                "proposal": json.dumps(proposal)
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"ProposalCritique failed validation: {error}")
            
        self.log_feedback(workflow_id, "proposal_critique", "success" if validated_output.get("critique_passed") else "failure", {})
        return validated_output

class AsyncToolGeneratorAgent(BaseAgent):
    """Async LLM-based tool code generator."""
    @track_metrics('meta_generate_tool')
    async def run_async(self, hypothesis: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Generating new tool code from hypothesis (v10.7)...")
        client = self.get_model_client("meta_tool_generator_model")
        
        prompt_template = self.prompt_manager.get_template("meta_tool_generator")
        
        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"hypothesis": json.dumps(hypothesis)},
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"ToolGenerator failed validation: {error}")
            
        tool_code = validated_output.get("tool_code", "")
        tool_name = validated_output.get("tool_name", f"tool_{uuid.uuid4().hex[:6]}")
        
        self.log_feedback(workflow_id, "tool_generation", "success", {"tool_name": tool_name})
        return {"generated_tool_code": tool_code, "generated_tool_name": tool_name}

class AsyncToolCritiqueAgent(BaseAgent):
    """Async LLM-based tool code critique."""
    @track_metrics('meta_critique_tool')
    async def run_async(self, tool_code: str, workflow_id: str) -> Dict[str, Any]:
        self.log_info("Critiquing generated tool code (v10.7)...")
        client = self.get_model_client("meta_tool_critique_model")
        
        prompt_template = self.prompt_manager.get_template("meta_tool_critique")
        
        # v10.7 REFACTOR: Use centralized async formatter
        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"generated_tool_code": tool_code},
            self.budget_manager,
            client.goal_state,
            client.top_failures
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"ToolCritique failed validation: {error}")
        
        self.log_feedback(workflow_id, "tool_critique", "success" if validated_output.get("critique_passed") else "failure", {})
        return validated_output

class GeneratedToolWriterAgent(BaseAgent):
    """Local agent to write generated tool code to disk."""
    @track_metrics('meta_write_tool')
    def run__src4(self, tool_name: str, tool_code: str, workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Writing generated tool '{tool_name}' to disk...")
        
        try:
            tools_dir = self.config.meta_loop_config.generated_tools_path
            os.makedirs(tools_dir, exist_ok=True)
            
            safe_filename = f"{tool_name.lower().replace(' ', '_')}.py"
            file_path = os.path.join(tools_dir, safe_filename)
            
            with open(file_path, 'w') as f:
                f.write(f"# Generated by Meta-Learning Workflow ID: {workflow_id}\n")
                f.write(f"# Timestamp: {datetime.now().isoformat()}\n\n")
                f.write(tool_code)
                
            self.log_info(f"Successfully wrote new tool to {file_path}")
            return {"status": "success", "file_path": file_path}
        except Exception as e:
            self.log_error(f"Failed to write generated tool: {e}")
            return {"status": "error", "reason": str(e)}

# ============================================================================
# META-LEARNING CONDITIONAL EDGE FUNCTIONS (v10.7: Preserved)
# ============================================================================

def check_proposal_type(state: MetaGraphState) -> str:
    """v10.7: Routes to tool gen or rule gen branch."""
    critique_passed = state.critique.get("critique_passed", False)
    if not critique_passed:
        return "replan"
    
    proposal_type = state.proposal.get("hypothesis_type", "rule_change")
    if proposal_type == "tool_generation":
        logger.info("Proposal critique passed. Routing to TOOL generation.")
        return "generate_tool"
    else:
        logger.info("Proposal critique passed. Routing to RULE generation.")
        return "write_rules"

def check_tool_critique(state: MetaGraphState) -> str:
    """v10.7: Checks if generated tool code passed critique."""
    critique_passed = state.critique.get("critique_passed", False)
    if critique_passed:
        logger.info("Tool critique passed. Routing to write_tool.")
        return "write_tool"
    else:
        logger.info("Tool critique FAILED. Looping back to generate_tool.")
        return "replan"

# ============================================================================
# META-LEARNING GRAPH BUILDER (v10.7: Refactored Nodes)
# ============================================================================

def build_meta_learning_graph(context: WorkflowContext, checkpointer: Any):
    """Build complete async meta-learning graph"""
    
    workflow = StateGraph(MetaGraphState)
    
    # --- Meta-Graph Nodes (v10.7: Refactored) ---
    
    async def read_logs_node(state: MetaGraphState) -> MetaGraphState:
        log_reader = LogReaderAgent(context)
        state.raw_logs = await asyncio.to_thread(log_reader.run)
        return state
    
    async def summarize_logs_node(state: MetaGraphState) -> MetaGraphState:
        summarizer = AsyncLogSummarizerAgent(context)
        state.log_summary = await summarizer.run_async(state.raw_logs, state.workflow_id)
        return state
    
    async def find_patterns_node(state: MetaGraphState) -> MetaGraphState:
        pattern_finder = AsyncPatternFinderAgent(context)
        state.patterns = await pattern_finder.run_async(state.log_summary, state.workflow_id)
        return state
    
    async def generate_hypotheses_node(state: MetaGraphState) -> MetaGraphState:
        hypothesis_gen = AsyncHypothesisGeneratorAgent(context)
        previous_critique = state.critique or {}
        state.hypotheses = await hypothesis_gen.run_async(state.patterns, previous_critique, state.workflow_id)
        return state
    
    async def draft_proposals_node(state: MetaGraphState) -> MetaGraphState:
        drafter = AsyncProposalDrafterAgent(context)
        hypotheses = state.hypotheses or []
        if not hypotheses: 
            state.proposal = {}
            return state
        
        proposal_tasks = [drafter.run_async(hyp, state.workflow_id) for hyp in hypotheses[:3]]
        proposals = await asyncio.gather(*proposal_tasks)
        best_proposal = max(proposals, key=lambda p: p.get("confidence", 0.0))
        state.proposal = best_proposal
        return state
    
    async def critique_proposal_node(state: MetaGraphState) -> MetaGraphState:
        critique_agent = AsyncProposalCritiqueAgent(context)
        state.critique = await critique_agent.run_async(state.proposal, state.patterns, state.workflow_id)
        return state
    
    async def write_rules_node(state: MetaGraphState) -> MetaGraphState:
        rule_manager = HotReloadRuleManager(
            rules_path=context.config.meta_loop_config.proposed_rules_path
        )
        critique = state.critique or {}
        proposal = state.proposal or {}
        
        if critique.get("critique_passed", False):
            confidence = proposal.get("confidence", 0.5)
            await asyncio.to_thread(rule_manager.write_proposed_rule, proposal, confidence)
        else:
            logger.info("✗ Proposal (rule) did not pass critique, not writing rule")
        return state

    async def generate_tool_node(state: MetaGraphState) -> MetaGraphState:
        tool_gen = AsyncToolGeneratorAgent(context)
        tool_gen_output = await tool_gen.run_async(state.proposal, state.workflow_id)
        state.generated_tool_code = tool_gen_output.get("generated_tool_code")
        state.proposal["generated_tool_name"] = tool_gen_output.get("generated_tool_name")
        return state

    async def critique_tool_node(state: MetaGraphState) -> MetaGraphState:
        tool_critique = AsyncToolCritiqueAgent(context)
        critique_output = await tool_critique.run_async(state.generated_tool_code, state.workflow_id)
        state.critique = critique_output
        return state

    async def write_tool_node(state: MetaGraphState) -> MetaGraphState:
        tool_writer = GeneratedToolWriterAgent(context)
        await asyncio.to_thread(
            tool_writer.run,
            tool_name=state.proposal.get("generated_tool_name", "unknown_tool"),
            tool_code=state.generated_tool_code,
            workflow_id=state.workflow_id
        )
        return state

    # --- Conditional Edges ---
    
    def conditional_check_proposal_type(state: MetaGraphState) -> str:
        return check_proposal_type(state)

    def conditional_check_tool_critique(state: MetaGraphState) -> str:
        return check_tool_critique(state)

    def should_replan_hypothesis(state: MetaGraphState) -> str:
        replan_count = state.replan_count + 1
        state.replan_count = replan_count
        max_replans = context.config.meta_loop_config.max_meta_replan_loops
        
        if replan_count < max_replans:
            logger.warning(f"Replanning hypothesis (Attempt {replan_count})...")
            return "replan"
        logger.error("Max hypothesis replans reached. Ending meta-loop.")
        return "end"
    
    # --- Build Graph ---
    workflow.add_node("read_logs", read_logs_node)
    workflow.add_node("summarize_logs", summarize_logs_node)
    workflow.add_node("find_patterns", find_patterns_node)
    workflow.add_node("generate_hypotheses", generate_hypotheses_node)
    workflow.add_node("draft_proposals", draft_proposals_node)
    workflow.add_node("critique_proposal", critique_proposal_node)
    workflow.add_node("write_rules", write_rules_node)
    workflow.add_node("generate_tool", generate_tool_node)
    workflow.add_node("critique_tool", critique_tool_node)
    workflow.add_node("write_tool", write_tool_node)
    
    workflow.set_entry_point("read_logs")
    workflow.add_edge("read_logs", "summarize_logs")
    workflow.add_edge("summarize_logs", "find_patterns")
    workflow.add_edge("find_patterns", "generate_hypotheses")
    workflow.add_edge("generate_hypotheses", "draft_proposals")
    workflow.add_edge("draft_proposals", "critique_proposal")
    
    workflow.add_conditional_edges(
        "critique_proposal",
        conditional_check_proposal_type,
        {
            "replan": "generate_hypotheses",
            "generate_tool": "generate_tool",
            "write_rules": "write_rules"
        }
    )
    
    workflow.add_edge("generate_tool", "critique_tool")
    workflow.add_conditional_edges(
        "critique_tool",
        conditional_check_tool_critique,
        {
            "write_tool": "write_tool",
            "replan": "generate_tool"
        }
    )

    workflow.add_edge("write_rules", END)
    workflow.add_edge("write_tool", END)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# MAIN META-LEARNING RUNNER (v10.7: Refactored)
# ============================================================================

async def run_meta_learning(config: ConfigV10_7):
    """
    v10.7: Runs async meta-learning graph.
    """
    
    logger.info(f"===== Starting v10.7 Meta-Learning =====")

    if not config.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning disabled in config. Exiting.")
        return

    feedback_log_entries = _count_feedback_entries(config)

    try:
        # --- v10.7: REFACTOR: COMPOSITION ROOT ---
        meta_db = config.redis_config.db + 10
        context = create_workflow_context(config, db=meta_db)
        logger.info("Initialized WorkflowContext for meta-learning (v10.7)")

        checkpointer = get_checkpointer(
            config,
            db=meta_db,
            allow_memory_fallback=True
        )
        # --- v10.7: REFACTOR END ---

        app = build_meta_learning_graph(context, checkpointer)

        workflow_id = str(uuid.uuid4())
        run_config = {"configurable": {"thread_id": workflow_id}}

        initial_state = MetaGraphState(workflow_id=workflow_id, replan_count=0)

        redis_available = _redis_available(context.redis_client)
        logger.info(
            "Meta-learning bootstrap | redis_available=%s | feedback_log_entries=%d | patterns_found=%d",
            redis_available,
            feedback_log_entries,
            0,
        )

        logger.info(f"Executing meta-learning graph (ID: {workflow_id})...")

        final_state = None
        async for s in app.astream(initial_state, run_config):
            node_name = list(s.keys())[0]
            logger.info(f"--- Meta-Node: {node_name} ---")
            final_state = s[node_name]
            store = getattr(context, "world_model_store", None)
            if store and store.enabled() and final_state is not None:
                patterns = getattr(final_state, "patterns", None) or []
                store.set_json(
                    "meta_last_snapshot",
                    {
                        "feedback_entries": feedback_log_entries,
                        "patterns_count": len(patterns),
                    },
                )

        if final_state is None:
             raise WorkflowError("Meta-learning graph did not return a final state.")

        patterns_found = len(final_state.patterns)
        critique_passed = final_state.critique.get("critique_passed", False)
        
        logger.info("META-LEARNING RESULTS (v10.7):")
        logger.info(f"  Patterns Found: {patterns_found}")
        logger.info(f"  Critique Passed: {critique_passed}")

        if patterns_found == 0 and feedback_log_entries == 0:
            logger.info("Meta-learning skipped: no data available (harmless).")

        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Meta-learning cost: ${cost_summary['total_workflow_cost']:.4f}")
        logger.info("===== v10.7 Meta-Learning Complete =====")
        
    except Exception as e:
        logger.error(f"Meta-Learning failed: {e}", exc_info=True)
        raise

# v10.7: This file is not a main entry point.
# ============================================================================
# END OF run_learning_v10_7.py
# ============================================================================
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/run_learning_v.py ====
