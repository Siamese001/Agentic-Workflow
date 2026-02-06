"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""

# LEGACY CODE BELOW - COMMENTED OUT
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

# import asyncio
# import importlib.util
# import inspect
# import json
# import logging
# import os
# from collections.abc import Awaitable, Callable
# from functools import partial, wraps
# from typing import Any

# v10.7: Import from new core
# from core_v10_7 import (
#     AsyncTimeoutError,
#     BaseAgent,
#     BaseTool,
#     CircuitBreaker,
#     CircuitBreakerOpenError,
#     MCPClientStub,
#     PersonaConsensus,
#     PydanticSchemaError,
#     StrategyPlan,
#     WorkflowContext,
#     WorkflowError,
#     WorkflowTimeoutError,
#     exponential_backoff_retry,
#     track_metrics,
#     wrap_mcp,
# )
# from langgraph.errors import GraphRecursionError
# from langgraph.graph import END, StateGraph
# from mcp import get_agent
# from telemetry_v10_7 import log_event

# Make HIL import conditional for environment compatibility
# try:
#     from langgraph.prebuilt import human_in_the_loop

#     HIL_AVAILABLE = True
# except ImportError:
#     HIL_AVAILABLE = False
#     human_in_the_loop = None  # type: ignore
#     logging.getLogger(__name__).warning(
#         "human_in_the_loop not available - HIL features will be disabled"
#     )

# v10.7: Import from new stacks
# from agent_stacks_v10_7 import (
#     AsyncBulletCritiqueAgent,
#     AsyncBulletGeneratorAgent,
#     BiasDetectorAgent,
#     ConstitutionalReviewerAgent,  # v10.7 (Fix #30)
#     HILAmbiguityDetectorAgent,
#     PIISanitizerAgent,
#     PromptEngineerAgent,
#     QueryComplexityClassifier,
# )

# v10.7: Import from new tools file
# from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from agent_tools_v10_7 import (
#         QAAdversarialReviewerTool,
#     QABiasDetectorTool,
#     QAClaimValidatorTool,
#     QAJDSkillsValidatorTool,
#     QAMissedOpportunityTool,
#     QANarrativeThreadTool,
#     QASemanticEntailmentTool,
#     QASignalScoreValidatorTool,
#     QATenureValidatorTool,
#     QAThematicAlignmentTool,
#     QAToneValidatorTool,
#     QAWordCountValidatorTool,
#     UIFireEventTool,
#     UIUpdateElementTool,
# )

# v10.7: Logger name updated
# logger = logging.getLogger("agent_orchestration_v10_7")

# ============================================================================
# MCP STACK ROUTING HELPERS
# ============================================================================


# async def route_to_stack(stack_name: str, context: WorkflowContext, *args, **kwargs):
#     """Resolve an MCP-registered stack and execute it with provided arguments."""

#     agent_cls = get_agent(stack_name)
#     agent = agent_cls(context)

#     runner = getattr(agent, "run_async", None)
#     if callable(runner):
#         result = runner(*args, **kwargs)
#         if asyncio.iscoroutine(result):
#             result = await result
#         return result

#     runner = getattr(agent, "run", None)
#     if callable(runner):
#         result = runner(*args, **kwargs)
#         if asyncio.iscoroutine(result):
#             result = await result
#         return result

#     raise WorkflowError(f"Agent '{stack_name}' does not expose run or run_async methods")


# ============================================================================
# v10.7: RUNTIME DECORATORS (Fix #6)
# ============================================================================


# def get_timeout_decorator(timeout_seconds: float):
#     """v10.7 (Fix #6): Creates a decorator bound to an explicit timeout."""

#     timeout_seconds = float(timeout_seconds)

#     def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
#         @wraps(func)
#         async def wrapper(*args, **kwargs) -> Any:
#             try:
#                 return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
#             except AsyncTimeoutError as e:
#                 logger.error(f"!!! NODE TIMEOUT: {func.__name__} exceeded {timeout_seconds}s !!!")
#                 raise WorkflowTimeoutError(
#                     f"Node {func.__name__} timed out after {timeout_seconds}s"
#                 ) from e

#         return wrapper

#     return decorator


# ============================================================================
# v10.7: DYNAMIC TOOLING (Fix #7)
# ============================================================================


# def load_dynamic_tools(context: WorkflowContext, debug_mode: bool) -> dict[str, BaseTool]:
#     """
#     v10.7 (Fix #7): Scans the generated_tools_path and dynamically
#     loads any valid BaseTool subclasses.
#     """
#     dynamic_tools = {}
#     tools_dir = context.config.meta_loop_config.generated_tools_path
#     if not os.path.exists(tools_dir):
#         logger.info(f"Dynamic tool directory not found, skipping: {tools_dir}")
#         return {}

#     logger.info(f"Loading dynamic tools from: {tools_dir}")
#     mcp_enabled = context.is_mcp_enabled()
#     if mcp_enabled:
#         context.ensure_mcp_clients()
#     for filename in os.listdir(tools_dir):
#         if filename.endswith(".py") and not filename.startswith("_"):
#             try:
#                 file_path = os.path.join(tools_dir, filename)
#                 spec = importlib.util.spec_from_file_location(filename[:-3], file_path)
#                 if spec is None:
#                     raise ImportError(f"Could not create spec for {file_path}")

#                 module = importlib.util.module_from_spec(spec)
#                 spec.loader.exec_module(module)

#                 for name, obj in inspect.getmembers(module):
#                     if inspect.isclass(obj) and issubclass(obj, BaseTool) and obj is not BaseTool:
#                         tool_instance = obj(context, debug_mode)
#                         tool_name = tool_instance.tool_name

#                         if mcp_enabled:
#                             required_clients = getattr(tool_instance, "required_mcp_clients", [])
#                             optional_clients = getattr(tool_instance, "optional_mcp_clients", [])

#                             for attr_name, value in (
#                                 ("required_mcp_clients", required_clients),
#                                 ("optional_mcp_clients", optional_clients),
#                             ):
#                                 if value and not isinstance(value, (list, tuple)):
#                                     raise WorkflowError(
#                                         f"Dynamic tool '{name}' has invalid '{attr_name}' definition."
#                                     )

#                             for client_name in required_clients or []:
#                                 if not isinstance(client_name, str):
#                                     raise WorkflowError(
#                                         f"Dynamic tool '{name}' requires MCP client names as strings."
#                                     )
#                                 context.get_mcp_client(client_name)

#                             for client_name in optional_clients or []:
#                                 if not isinstance(client_name, str):
#                                     raise WorkflowError(
#                                         f"Dynamic tool '{name}' optional MCP clients must be strings."
#                                     )
#                                 context.get_mcp_client(
#                                     client_name,
#                                     default=MCPClientStub(
#                                         client_name, {"source": f"dynamic_tool:{tool_name}"}
#                                     ),
#                                 )
#                         if tool_name in dynamic_tools:
#                             logger.warning(
#                                 f"Duplicate dynamic tool name '{tool_name}'. Overwriting."
#                             )

#                         dynamic_tools[tool_name] = tool_instance
#                         logger.info(f"Successfully loaded dynamic tool: {name} (as '{tool_name}')")

#             except Exception as e:
#                 logger.error(f"Failed to load dynamic tool from {filename}: {e}")

#     return dynamic_tools


# QA CONDUCTOR (v10.7: Fix #7, #8, #17, #19, #20, #24)
# ============================================================================


# class QAConductorAgent(SubatomicTestingMixin, BaseAgent):
#     """v10.7: ReAct QA Conductor with dynamic/UI tooling and cognitive modes."""

#     def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
#         super().__init__(context, debug_mode)
#         static_tools: list[tuple[str, BaseTool]] = [
#             # Standard QA Suite
#             ("validate_claims", QAClaimValidatorTool(context, debug_mode)),
#             ("validate_tone", QAToneValidatorTool(context, debug_mode)),
#             ("validate_thematic_alignment", QAThematicAlignmentTool(context, debug_mode)),
#             ("validate_semantic_entailment", QASemanticEntailmentTool(context, debug_mode)),
#             ("validate_narrative_thread", QANarrativeThreadTool(context, debug_mode)),
#             ("adversarial_review", QAAdversarialReviewerTool(context, debug_mode)),
#             ("validate_jd_skills", QAJDSkillsValidatorTool(context, debug_mode)),
#             ("validate_signal_score", QASignalScoreValidatorTool(context, debug_mode)),
#             ("validate_bias", QABiasDetectorTool(context, debug_mode)),
#             ("validate_tenure", QATenureValidatorTool(context, debug_mode)),
#             ("find_missed_opportunities", QAMissedOpportunityTool(context, debug_mode)),
#             ("validate_word_count", QAWordCountValidatorTool(context, debug_mode)),
#             # v10.7 (Fix #8): Add UI tools
#             ("ui_update_element", UIUpdateElementTool(context, debug_mode)),
#             ("ui_fire_event", UIFireEventTool(context, debug_mode)),
#         ]

#         self.tools: dict[str, BaseTool] = {}
#         for tool_name, tool_instance in static_tools:
#             if tool_name in self.tools:
#                 logger.error(
#                     "Duplicate static QA tool name detected during initialization: %s",
#                     tool_name,
#                 )
#                 raise WorkflowError(f"Duplicate static QA tool detected: {tool_name}")
#             self.tools[tool_name] = tool_instance

#         # v10.7 (Fix #7): Load dynamic tools
#         dynamic_tools = load_dynamic_tools(context, debug_mode)
#         for tool_name in dynamic_tools:
#             if tool_name in self.tools:
#                 logger.warning(
#                     "Dynamic tool '%s' overrides an existing QA tool. Previous instance will be replaced.",
#                     tool_name,
#                 )
#         self.tools.update(dynamic_tools)

#         self.tool_schemas = [t.get_schema() for t in self.tools.values()]

#         self.tool_breakers = {
#             name: CircuitBreaker(
#                 failure_threshold=self.config.batch_config.circuit_breaker_failure_threshold
#             )
#             for name in self.tools
#         }
#         self.style_guide = "Style: Ensure professional, clear, and unbiased language."

#     @track_metrics("run_react_qa_conductor")
#     async def run_async(self, state: dict[str, Any], workflow_id: str) -> dict[str, Any]:
#         self.log_info("Running ReAct QA Conductor (v10.7)...")

#         max_steps = self.config.agent_stacks.conductor_max_steps
#         client = self.get_model_client("react_conductor_model")

#         pruned_draft = await self.budget_manager.prune(json.dumps(state["draft"]["sections"]), 4000)
#         pruned_master_resume = await self.budget_manager.prune(
#             json.dumps(state["resume"]["master_resume"]), 4000
#         )
#         pruned_jd = await self.budget_manager.prune(state["job"]["raw_jd"], 2000)

#         strategy_plan = state["strategy"]["strategy_plan"]
#         if isinstance(strategy_plan, dict):
#             strategy_plan = StrategyPlan.model_validate(strategy_plan)
#         # v10.7 (Fix #17, #19, #20, #24): Inject Goal, Failures, Mode, Reflection
#         react_prompt = f"""
# {client.goal_state}
# {client.top_failures}
# -------------------
# MODE: ORCHESTRATION
# TASK: You are a ReAct QA conductor. Your goal is to validate the draft.
# Draft (Pruned): {pruned_draft}
# Tools: {json.dumps(self.tool_schemas)}
# Plan (v10.7):
# 1.  Run `validate_claims` and `validate_tenure`.
# 2.  Run `validate_jd_skills` and `validate_thematic_alignment`.
# 3.  Run `validate_tone`, `validate_narrative_thread`, and `validate_signal_score`.
# 4.  Run `validate_bias`.
# 5.  Run `validate_word_count` on the summary section (e.g., min: 50, max: 150).
# 6.  Run `find_missed_opportunities`.
# 7.  Run `adversarial_review` as a final check.
# 8.  Compile all feedback into a final QA report.

# REFLECTION: Did I run all critical validation tools?
# Output thoughts/tool calls in JSON:
# {{"thought": "Your reasoning", "tool_call": {{"name": "tool_name", "input": {{"arg": "value"}}}}}}
# When finished, output:
# {{"thought": "QA complete", "final_qa_report": {{"qa_passed": true/false, "issues": [...]}}}}
# """
#         messages = [{"role": "user", "content": react_prompt}]

#         final_report = {}
#         all_tool_results = []

#         tool_context = {
#             "draft_text": pruned_draft,
#             "master_resume": pruned_master_resume,
#             "job_description": pruned_jd,
#             "strategy": strategy_plan.model_dump(),
#             "style_guide": self.style_guide,
#         }

#         for step in range(max_steps):
#             response = await client.chat_completion_async(
#                 messages=messages,
#                 temperature=self.config.agent_stacks.conductor_temperature,
#                 response_format="json_object",
#             )

#             step_data, error = self.validator.validate(response["content"], dict)
#             if error:
#                 logger.warning(f"QA step {step} failed validation: {error}")
#                 messages.append(
#                     {"role": "user", "content": f"Error: Invalid JSON response from LLM. {error}"}
#                 )
#                 continue

#             messages.append({"role": "assistant", "content": json.dumps(step_data)})

#             if "final_qa_report" in step_data:
#                 final_report = step_data["final_qa_report"]
#                 final_report["all_tool_results"] = all_tool_results
#                 self.log_feedback(
#                     workflow_id, "react_conductor_qa", "success", {"steps_executed": step}
#                 )
#                 return final_report

#             if "tool_call" in step_data:
#                 tool_name = step_data["tool_call"].get("name")
#                 tool_input = step_data["tool_call"].get("input", {})

#                 if not tool_name or tool_name not in self.tools:
#                     messages.append(
#                         {"role": "user", "content": f"Error: Tool '{tool_name}' not found."}
#                     )
#                     continue

#                 tool_input.update(tool_context)

#                 try:
#                     breaker = self.tool_breakers[tool_name]
#                     breaker.check()
#                     tool = self.tools[tool_name]
#                     tool_result = await tool.run_async(tool_input, workflow_id)
#                     breaker.record_success()
#                     all_tool_results.append({tool_name: tool_result})
#                     messages.append(
#                         {"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"}
#                     )

#                 except (CircuitBreakerOpenError, PydanticSchemaError, Exception) as e:
#                     self.log_error(f"QA Tool {tool_name} failed: {e}")
#                     if not isinstance(e, CircuitBreakerOpenError):
#                         if tool_name in self.tool_breakers:
#                             self.tool_breakers[tool_name].record_failure()

#                     error_msg = (
#                         f"Error: Tool '{tool_name}' failed. Do not call it again. Reason: {str(e)}"
#                     )
#                     messages.append({"role": "user", "content": error_msg})

#         self.log_feedback(
#             workflow_id, "react_conductor_qa", "failure", {"reason": "Max steps reached"}
#         )
#         return {
#             "error": "Max steps reached",
#             "steps": max_steps,
#             "all_tool_results": all_tool_results,
#             "qa_passed": False,
#         }


# class MetaLearningLoop(BaseAgent):
#     """Placeholder MCP agent for telemetry-aligned meta learning."""

#     async def run_async(self, state: dict[str, Any], workflow_id: str) -> dict[str, Any]:
#         self.log_info("MetaLearningLoop invoked - emitting telemetry only.")
#         log_event("MetaLearningLoop", "executed", {"workflow_id": workflow_id})
#         return {"meta_learning": {"status": "noop"}}


# ============================================================================
# LANGGRAPH NODE & EDGE FUNCTIONS (v10.7: Fix #5, #10, #30)
# ============================================================================

# --- NODE DEFINITIONS (v10.7) ---


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_sanitize_pii(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 0: Sanitize PII"""
#     context = workflow_context
#     context.complexity = state.get("metadata", {}).get("complexity", "unknown")
#     pii_agent = PIISanitizerAgent(context)
#     sanitized = await asyncio.to_thread(pii_agent.run, state["resume"]["master_resume"])

#     bias_agent = BiasDetectorAgent(context)
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     bias_result = await asyncio.to_thread(bias_agent.run, state["job"]["raw_jd"], workflow_id)

#     return {
#         "resume": {"sanitized_resume": sanitized},
#         "safety": {"bias_detected": bias_result["bias_detected"]},
#     }


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_detect_prompt_injection(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 0.5: Detect Prompt Injection"""
#     context = workflow_context
#     if not context.config.agent_stacks.enable_prompt_injection_detection:
#         return {"safety": {"injection_detected": False}}

#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     jd_result = await route_to_stack(
#         "SafetyGuardStack", context, state["job"]["raw_jd"], workflow_id
#     )
#     log_event("SafetyGuardStack", "run", {"workflow_id": workflow_id})

#     return {"safety": {"injection_detected": jd_result.get("injection_detected", False)}}


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_classify_complexity(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 1: Classify Complexity"""
#     context = workflow_context
#     classifier = QueryComplexityClassifier(context)
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     complexity = await classifier.run_async(state["job"]["raw_jd"], workflow_id)
#     context.complexity = complexity
#     return {"metadata": {"complexity": complexity}}


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_tot_strategy(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 2: ToT strategy"""
#     context = workflow_context
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     strategy_result = await route_to_stack(
#         "StrategyStack",
#         context,
#         {
#             "job_title": state["job"]["job_title"],
#             "company": state["job"]["company"],
#             "job_description": state["job"]["raw_jd"],
#         },
#         workflow_id,
#     )
#     log_event("StrategyStack", "completed", {"workflow_id": workflow_id})
#     return {"strategy": strategy_result}


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_detect_ambiguity(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 3: Proactive HIL ambiguity check"""
#     context = workflow_context
#     if not context.config.agent_stacks.enable_hil_stack:
#         return {
#             "hil": {
#                 "ambiguity_report": {
#                     "ambiguity_detected": False,
#                     "confidence": 1.0,
#                     "reason": "HIL disabled",
#                     "question_for_human": "",
#                 }
#             }
#         }

#     detector = HILAmbiguityDetectorAgent(context)
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")

#     strategy_plan = state["strategy"]["strategy_plan"]
#     if isinstance(strategy_plan, dict):
#         strategy_plan = StrategyPlan.model_validate(strategy_plan)

#     ambiguity_result = await detector.run_async(strategy_plan, workflow_id)
#     report = ambiguity_result.get("ambiguity_report")
#     if report.confidence < context.config.agent_stacks.ambiguity_confidence_threshold:
#         report.ambiguity_detected = False

#     return {"hil": {"ambiguity_report": report.model_dump()}}


# v10.7 (Fix #5): Dummy node for parallel fork
# def prepare_parallel_run(state: dict) -> dict:
#     """Node 3.5: Gateway for parallel execution."""
#     logger.info("Forking graph for parallel RAG and Prompt Engineering.")
#     return {}


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_prompt_engineering(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 4: Generate dynamic prompts"""
#     context = workflow_context
#     prompt_agent = PromptEngineerAgent(context)
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     strategy_plan = state["strategy"]["strategy_plan"]
#     if isinstance(strategy_plan, dict):
#         strategy_plan = StrategyPlan.model_validate(strategy_plan)

#     complexity = state.get("metadata", {}).get("complexity", "unknown")
#     prompts_result = await prompt_agent.run_async(strategy_plan, complexity, workflow_id)
#     return {"prompts": {"prompts": prompts_result.get("prompts").model_dump()}}


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_rag_stack(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 5: Agentic RAG (v10.7 Fix #10: A2A enabled)"""
#     context = workflow_context
#     state_patch = await route_to_stack("RAGStack", context, state)
#     log_event(
#         "RAGStack", "completed", {"workflow_id": state.get("metadata", {}).get("workflow_id", "")}
#     )
#     return state_patch


# v10.7 (Fix #5): Dummy node for parallel join
# def join_rag_and_prompt(state: dict) -> dict:
#     """Node 5.5: Gateway for parallel join."""
#     logger.info("Joining graph from parallel RAG and Prompt Engineering.")
#     return {}


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_generate_bullets(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 6: Generate bullets (4-step)"""
#     context = workflow_context
#     bullet_gen = AsyncBulletGeneratorAgent(context)
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     prompt = state["prompts"]["prompts"].get("bullet_generation_prompt", "Generate bullets")
#     strategy = state["strategy"]["strategy_plan"]
#     if isinstance(strategy, dict):
#         strategy = StrategyPlan.model_validate(strategy)

#     all_bullets = []
#     for exp in state["resume"]["experience_bullets"][:3]:
#         bullets = await bullet_gen.run_async(prompt, exp, strategy, workflow_id)
#         all_bullets.extend([{"text": b, "experience": exp} for b in bullets])
#     return {"bullets": {"generated_bullets": all_bullets}}


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_critique_bullets(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 7: Critique bullets"""
#     context = workflow_context
#     critique_agent = AsyncBulletCritiqueAgent(context)
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     critique_prompt = state["prompts"]["prompts"].get("critique_prompt", "Critique bullets")
#     bullets = state["bullets"]["generated_bullets"]
#     critiques = await critique_agent.run_async(bullets, critique_prompt, workflow_id)
#     return {"bullets": {"critiqued_bullets": critiques}}


# @wrap_mcp
# @exponential_backoff_retry()
# async def run_drafting(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 8: Draft assembly with ReAct Conductor"""
#     context = workflow_context
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")

#     good_bullets = [
#         b
#         for b in state["bullets"]["critiqued_bullets"]
#         if b.get("critique", {}).get("score", 0) >= 7
#     ]
#     strategy_plan = state["strategy"]["strategy_plan"]
#     if isinstance(strategy_plan, dict):
#         strategy_plan = StrategyPlan.model_validate(strategy_plan)

#     task_context = {
#         "bullets": good_bullets,
#         "strategy": strategy_plan,
#         "resume": state["resume"]["master_resume"],
#     }
#     draft = await route_to_stack("DraftingStack", context, task_context, workflow_id)
#     log_event("DraftingStack", "completed", {"workflow_id": workflow_id})
#     return {"draft": {"sections": draft.get("final_output", {})}}


# async def run_qa_validation(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 9: Final QA with ReAct Conductor"""
#     context = workflow_context
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")

#     if isinstance(state["strategy"]["strategy_plan"], dict):
#         state["strategy"]["strategy_plan"] = StrategyPlan.model_validate(
#             state["strategy"]["strategy_plan"]
#         )

#     validation = await route_to_stack("QAStack", context, state, workflow_id)
#     log_event("QAStack", "completed", {"workflow_id": workflow_id})
#     return {
#         "qa": {"validation_results": validation, "qa_passed": validation.get("qa_passed", False)},
#         "artifacts": {
#             "artifacts": {"final_resume": state["draft"]["sections"], "qa_report": validation}
#         },
#     }


# async def run_constitutional_review(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 9.5: Constitutional Review (v10.7 Fix #30)"""
#     context = workflow_context
#     agent = ConstitutionalReviewerAgent(context)
#     draft_text = json.dumps(state["artifacts"]["artifacts"]["final_resume"])
#     result = await agent.run_async(draft_text, state["metadata"]["workflow_id"])
#     return {"qa": {"constitutional_review": result.model_dump()}}


# HIL Nodes
# async def run_feedback_router(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 11: HIL Feedback router"""
#     context = workflow_context
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     human_feedback = state.get("hil", {}).get("raw_feedback") or "Default to drafting"
#     route = await route_to_stack("HILStack", context, human_feedback, workflow_id, state)
#     log_event(
#         "HILStack", "completed", {"workflow_id": workflow_id, "next_step": route.get("next_step")}
#     )
#     return {
#         "hil": {
#             "next_step": route.get("next_step"),
#             "payload": route.get("payload"),
#             "intent_clusters": route.get("intent_clusters", []),
#             "delegated_specialists": route.get("delegated_specialists", []),
#             "persona_consensus": route.get("persona_consensus"),
#             "reconciliation": route.get("reconciliation"),
#         }
#     }


# def human_in_the_loop_node(state: dict) -> dict:
#     """Node 10: HIL Pause"""
#     if not HIL_AVAILABLE:
#         logger.warning("HIL not available. Skipping pause.")
#         return {}
#     try:
#         human_in_the_loop(timeout=3600)
#     except GraphRecursionError:
#         logger.info("HIL pause interrupted by user feedback.")
#     except Exception as e:
#         logger.error(f"HIL node failed: {e}")
#     return {}


# async def run_inject_hil_edit(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 12: Inject HIL Edits"""
#     _ = workflow_context
#     logger.info("Injecting human-in-the-loop edits...")
#     payload = state.get("hil", {}).get("payload")
#     if not payload:
#         logger.warning("HIL INJECT_EDIT route chosen, but no payload found.")
#         return {}
#     if "sections" not in state["draft"]:
#         state["draft"]["sections"] = {}
#     reconciliation = state.get("hil", {}).get("reconciliation")
#     if reconciliation and reconciliation.get("integrated_text"):
#         state["draft"]["sections"]["summary"] = reconciliation["integrated_text"]
#     else:
#         state["draft"]["sections"]["summary"] = f"[EDITED BY HUMAN]: {payload}"
#     logger.info("HIL edit injected into draft summary.")
#     return {"draft": state["draft"]}


# async def run_reconcile_specialists(state: dict, workflow_context: WorkflowContext) -> dict:
#     """Node 11.5: Reconcile specialist contributions."""
#     context = workflow_context
#     agent = HILReconciliationAgent(context)
#     workflow_id = state.get("metadata", {}).get("workflow_id", "")
#     specialist_feedback = state.get("hil", {}).get("specialist_feedback", [])
#     persona_consensus_data = state.get("hil", {}).get("persona_consensus")
#     persona_consensus = None
#     if persona_consensus_data:
#         try:
#             persona_consensus = PersonaConsensus.model_validate(persona_consensus_data)
#         except Exception as exc:
#             logger.warning(f"Failed to parse persona consensus for reconciliation: {exc}")

#     draft_sections = state.get("draft", {}).get("sections", {})
#     result = await agent.run_async(
#         draft_sections, specialist_feedback, persona_consensus, workflow_id
#     )
#     return {"hil": {"reconciliation": result.model_dump()}}


# --- CONDITIONAL EDGES (v10.7: Fix #30) ---


# def check_prompt_injection(state: dict) -> str:
#     """Node 0.5 conditional"""
#     if state.get("safety", {}).get("injection_detected", False):
#         logger.error("!!! PROMPT INJECTION DETECTED. Halting workflow. !!!")
#         return "injection_detected"
#     return "injection_safe"


# def check_ambiguity(state: dict) -> str:
#     """Node 3 conditional: Route to HIL or continue"""
#     report = state.get("hil", {}).get("ambiguity_report", {})
#     if report.get("ambiguity_detected", False):
#         return "pause_for_human"
#     return "continue_workflow"


# def check_bullets_passed(state: dict, workflow_context: WorkflowContext) -> str:
#     """Node 7 conditional: Check bullet quality and retries"""
#     critiques = state.get("bullets", {}).get("critiqued_bullets", [])
#     if not critiques:
#         return "global_replanner"
#     avg_score = sum(b.get("critique", {}).get("score", 0) for b in critiques) / len(critiques)
#     if avg_score >= 7.0:
#         return "bullets_passed"
#     retries = state.get("metadata", {}).get("retries", {}).get("bullet_retries", 0)
#     if retries < workflow_context.config.agent_stacks.max_local_retries:
#         if "metadata" not in state:
#             state["metadata"] = {}
#         if "retries" not in state["metadata"]:
#             state["metadata"]["retries"] = {}
#         state["metadata"]["retries"]["bullet_retries"] = retries + 1
#         return "retry_bullets"
#     return "global_replanner"


# def check_qa_passed(state: dict) -> str:
#     """Node 9 conditional: Check QA and retries (v10.7: Rerouted)"""
#     if state.get("qa", {}).get("qa_passed", False):
#         return "qa_passed"  # Route to constitutional review

#     retries = state.get("metadata", {}).get("retries", {}).get("qa_retries", 0)
#     if retries < 1:  # Max 1 QA retry
#         if "metadata" not in state:
#             state["metadata"] = {}
#         if "retries" not in state["metadata"]:
#             state["metadata"]["retries"] = {}
#         state["metadata"]["retries"]["qa_retries"] = retries + 1
#         return "retry_drafting"
#     return "global_replanner"


# def check_constitution(state: dict) -> str:
#     """Node 9.5 conditional: Check constitutional review (v10.7 Fix #30)"""
#     review = state.get("qa", {}).get("constitutional_review", {})
#     if review.get("review_passed", False):
#         return "passed_constitution"
#     else:
#         logger.error("!!! CONSTITUTIONAL REVIEW FAILED. Halting workflow. !!!")
#         logger.error(f"Violations: {review.get('violations_found')}")
#         return "failed_constitution"


# def route_feedback(state: dict) -> str:
#     """Node 11 conditional: Route based on human feedback"""
#     next_step = state.get("hil", {}).get("next_step", "DRAFTING")
#     if next_step == "STRATEGY":
#         return "to_strategy"
#     if next_step == "BULLET_GENERATION":
#         return "to_bullets"
#     if next_step == "INJECT_EDIT":
#         return "to_inject_edit"
#     if next_step == "DELEGATE_SPECIALIST":
#         return "to_delegation"
#     return "to_drafting"


# ============================================================================
# LANGGRAPH WORKFLOW BUILDER (Design-Aligned v10.7: Fix #5, #30)
# ============================================================================


# def get_graph_app(
#     checkpointer: Any,
#     workflow_context: WorkflowContext,
#     enable_hil: bool = True,
#     *,
#     enable_mcp: bool | None = None,
# ):
#     """Build complete LangGraph workflow with v10.7 resilience."""

#     global HIL_AVAILABLE
#     HIL_AVAILABLE = (
#         HIL_AVAILABLE and enable_hil and workflow_context.config.agent_stacks.enable_hil_stack
#     )

#     if enable_mcp is not None:
#         workflow_context.wrap_mcp_nodes = enable_mcp
#         if not enable_mcp:
#             workflow_context.reset_mcp_clients()

#     workflow = StateGraph(dict)

#     timeout_seconds = workflow_context.config.performance_config.workflow_node_timeout_seconds
#     timeout_wrapper = get_timeout_decorator(timeout_seconds)

#     def add_async_node(name: str, func: Callable[..., Awaitable[dict[str, Any]]]):
#         workflow.add_node(name, timeout_wrapper(func))

#     # --- ADD NODES (v10.7: Added new nodes) ---
#     add_async_node(
#         "run_sanitize_pii", partial(run_sanitize_pii, workflow_context=workflow_context)
#     )  # 0
#     add_async_node(
#         "run_detect_prompt_injection",
#         partial(run_detect_prompt_injection, workflow_context=workflow_context),
#     )  # 0.5
#     add_async_node(
#         "run_classify_complexity",
#         partial(run_classify_complexity, workflow_context=workflow_context),
#     )  # 1
#     add_async_node(
#         "run_tot_strategy", partial(run_tot_strategy, workflow_context=workflow_context)
#     )  # 2
#     add_async_node(
#         "run_detect_ambiguity", partial(run_detect_ambiguity, workflow_context=workflow_context)
#     )  # 3
#     workflow.add_node("prepare_parallel_run", prepare_parallel_run)  # 3.5 (Fix #5)
#     add_async_node(
#         "run_prompt_engineering", partial(run_prompt_engineering, workflow_context=workflow_context)
#     )  # 4
#     add_async_node("run_rag_stack", partial(run_rag_stack, workflow_context=workflow_context))  # 5
#     workflow.add_node("join_rag_and_prompt", join_rag_and_prompt)  # 5.5 (Fix #5)
#     add_async_node(
#         "run_generate_bullets", partial(run_generate_bullets, workflow_context=workflow_context)
#     )  # 6
#     add_async_node(
#         "run_critique_bullets", partial(run_critique_bullets, workflow_context=workflow_context)
#     )  # 7
#     add_async_node("run_drafting", partial(run_drafting, workflow_context=workflow_context))  # 8
#     add_async_node(
#         "run_qa_validation", partial(run_qa_validation, workflow_context=workflow_context)
#     )  # 9
#     add_async_node(
#         "run_constitutional_review",
#         partial(run_constitutional_review, workflow_context=workflow_context),
#     )  # 9.5 (Fix #30)
#     workflow.add_node("HIL_PAUSE", human_in_the_loop_node)  # 10
#     add_async_node(
#         "run_feedback_router", partial(run_feedback_router, workflow_context=workflow_context)
#     )  # 11
#     add_async_node(
#         "run_reconcile_specialists",
#         partial(run_reconcile_specialists, workflow_context=workflow_context),
#     )  # 11.5
#     add_async_node(
#         "run_inject_hil_edit", partial(run_inject_hil_edit, workflow_context=workflow_context)
#     )  # 12

#     # --- CONNECT NODES (v10.7: Rerouted for new nodes) ---
#     workflow.set_entry_point("run_sanitize_pii")
#     workflow.add_edge("run_sanitize_pii", "run_detect_prompt_injection")  # 0 -> 0.5

#     workflow.add_conditional_edges(
#         "run_detect_prompt_injection",
#         check_prompt_injection,
#         {"injection_detected": END, "injection_safe": "run_classify_complexity"},
#     )  # 0.5 -> 1 or END

#     workflow.add_edge("run_classify_complexity", "run_tot_strategy")  # 1 -> 2
#     workflow.add_edge("run_tot_strategy", "run_detect_ambiguity")  # 2 -> 3

#     # v10.7 (Fix #5): Reroute for parallel execution
#     workflow.add_conditional_edges(
#         "run_detect_ambiguity",
#         check_ambiguity,
#         {"pause_for_human": "HIL_PAUSE", "continue_workflow": "prepare_parallel_run"},
#     )  # 3 -> 10 or 3.5

#     workflow.add_edge("prepare_parallel_run", "run_prompt_engineering")  # 3.5 -> 4
#     workflow.add_edge("prepare_parallel_run", "run_rag_stack")  # 3.5 -> 5
#     workflow.add_edge("run_prompt_engineering", "join_rag_and_prompt")  # 4 -> 5.5
#     workflow.add_edge("run_rag_stack", "join_rag_and_prompt")  # 5 -> 5.5

#     workflow.add_edge("join_rag_and_prompt", "run_generate_bullets")  # 5.5 -> 6

#     workflow.add_edge("run_generate_bullets", "run_critique_bullets")  # 6 -> 7

#     workflow.add_conditional_edges(
#         "run_critique_bullets",
#         partial(check_bullets_passed, workflow_context=workflow_context),
#         {
#             "bullets_passed": "run_drafting",
#             "retry_bullets": "run_generate_bullets",
#             "global_replanner": END,
#         },
#     )  # 7 -> 8 or 6 or END

#     workflow.add_edge("run_drafting", "run_qa_validation")  # 8 -> 9

#     # v10.7 (Fix #30): Reroute for constitutional review
#     workflow.add_conditional_edges(
#         "run_qa_validation",
#         check_qa_passed,
#         {
#             "qa_passed": "run_constitutional_review",  # 9 -> 9.5
#             "retry_drafting": "run_drafting",  # 9 -> 8
#             "global_replanner": END,
#         },
#     )

#     workflow.add_conditional_edges(
#         "run_constitutional_review",
#         check_constitution,
#         {
#             "passed_constitution": "HIL_PAUSE" if HIL_AVAILABLE else END,  # 9.5 -> 10 or END
#             "failed_constitution": END,  # Fail the job
#         },
#     )

#     workflow.add_edge("HIL_PAUSE", "run_feedback_router")  # 10 -> 11

#     workflow.add_conditional_edges(
#         "run_feedback_router",
#         route_feedback,
#         {
#             "to_strategy": "run_tot_strategy",
#             "to_bullets": "run_generate_bullets",
#             "to_drafting": "run_drafting",
#             "to_inject_edit": "run_inject_hil_edit",
#             "to_delegation": "run_reconcile_specialists",
#         },
#     )

#     workflow.add_edge("run_reconcile_specialists", "run_inject_hil_edit")  # 11.5 -> 12

#     workflow.add_edge("run_inject_hil_edit", "run_qa_validation")  # 12 -> 9 (Re-run QA)

#     return workflow.compile(checkpointer=checkpointer)


# ============================================================================
# END OF agent_orchestration_v10_7.py
# ============================================================================
