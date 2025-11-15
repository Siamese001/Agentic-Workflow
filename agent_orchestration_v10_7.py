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
from stacks_v10_8 import RAGOrchestratorStack

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

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
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
    if not context.config.agent_stacks.enable_hil_stack:
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
    if not HIL_AVAILABLE:
        logger.warning("HIL not available. Skipping pause.")
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
    """Node 7 conditional: Check bullet quality and retries"""
    state = _extract_node_payload(result)

    critiques = state.get('bullets', {}).get('critiqued_bullets', [])
    if not critiques:
        return "global_replanner"

    avg_score = sum(b.get('critique', {}).get('score', 0) for b in critiques) / len(critiques)
    robustness = _get_robustness_stack(workflow_context)
    if avg_score >= 7.0:
        robustness.reset("bullets_quality")
        return "bullets_passed"

    if robustness.should_retry("bullets_quality", "score_below_threshold"):
        return "retry_bullets"
    return "global_replanner"


def check_qa_passed(result: dict, workflow_context: WorkflowContext) -> str:
    """Node 9 conditional: Check QA and retries (v10.7: Rerouted)"""
    state = _extract_node_payload(result)

    robustness = _get_robustness_stack(workflow_context)
    if state.get('qa', {}).get('qa_passed', False):
        robustness.reset("qa_validation")
        return "qa_passed"  # Route to constitutional review

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


def increment_hil_retries(state: dict, max_loops: int) -> bool:
    """Increment the HIL retry counter and signal whether another loop is permitted."""

    retries = state.setdefault("metadata", {}).setdefault("retries", {})
    current = int(retries.get("hil_retries", 0)) + 1
    retries["hil_retries"] = current
    return current <= max_loops


def _enforce_hil_loop_budget(
    state: dict,
    workflow_context: WorkflowContext,
    *,
    workflow_id: str,
    route: str,
) -> bool:
    """Ensure HIL re-entry loops remain within the configured bound."""

    max_loops = _get_hil_max_reentry_loops(workflow_context)
    if increment_hil_retries(state, max_loops):
        return True

    hil_state = state.setdefault("hil", {})
    hil_state["max_reentry_reached"] = True
    log_event(
        "HILStack",
        "max_reentry_reached",
        {
            "workflow_id": workflow_id,
            "route": route,
            "max_reentry_loops": max_loops,
            "hil_retries": _get_current_hil_retries(state),
        },
    )
    return False


async def run_prepare_hil_strategy_reentry(state: dict, workflow_context: WorkflowContext) -> dict:
    workflow_id = state.get('metadata', {}).get('workflow_id', workflow_context.workflow_id)
    if not _enforce_hil_loop_budget(
        state,
        workflow_context,
        workflow_id=workflow_id,
        route="strategy",
    ):
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
    workflow_id = state.get('metadata', {}).get('workflow_id', workflow_context.workflow_id)
    if not _enforce_hil_loop_budget(
        state,
        workflow_context,
        workflow_id=workflow_id,
        route="drafting",
    ):
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

    global HIL_AVAILABLE
    HIL_AVAILABLE = HIL_AVAILABLE and enable_hil and workflow_context.config.agent_stacks.enable_hil_stack

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
            "passed_constitution": "HIL_PAUSE" if HIL_AVAILABLE else END, # 9.5 -> 10 or END
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