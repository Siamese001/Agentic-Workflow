"""
L5 Autonomous Orchestrator - Phase Execution Logic (Outreach Engine)
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict

from apps_lic.L3_orchestration.l5_orchestrator.types import (
    OutreachCycleState,
    OutreachExecutionPhase,
)

from apps_shared.signal_bus import SignalType

logger = logging.getLogger(__name__)


async def execute_all_phases(
    orchestrator,
    agents: Dict[str, Callable],
    cycle_state: OutreachCycleState,
    recipient_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute all phases in order."""

    results = {}

    for phase in orchestrator.phases:
        # Check phase condition
        if phase.condition and not phase.condition(recipient_context):
            logger.debug(f"Skipping phase {phase.name} - condition not met")
            continue

        logger.info(f"  Executing phase: {phase.name}")

        try:
            if phase.execution_mode == "parallel":
                phase_result = await execute_phase_parallel(
                    orchestrator, phase, agents, cycle_state, recipient_context
                )
            else:
                phase_result = await execute_phase_sequential(
                    orchestrator, phase, agents, cycle_state, recipient_context
                )

            results[phase.name] = phase_result

            # Check for hard gate failure
            if phase.is_hard_gate and not phase_result.get("success", True):
                logger.error(f"Hard gate {phase.name} failed - aborting")
                if orchestrator.signal_bus:
                    await orchestrator.signal_bus.signal_critical_failure(
                        f"Hard gate {phase.name} failed",
                        source="L5Orchestrator"
                    )
                break

        except Exception as e:
            logger.error(f"Phase {phase.name} failed: {e}")
            if orchestrator.signal_bus:
                await orchestrator.signal_bus.emit(
                    SignalType.VALIDATION_FAILURE,
                    f"Phase {phase.name} error: {e}",
                    source="L5Orchestrator",
                    severity="error"
                )
            if phase.is_hard_gate:
                break

    return results


async def execute_phase_sequential(
    orchestrator,
    phase: OutreachExecutionPhase,
    agents: Dict[str, Callable],
    cycle_state: OutreachCycleState,
    recipient_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute phase agents sequentially."""

    results = {"success": True, "agents": {}}

    for agent_name in phase.agents:
        if agent_name not in agents:
            logger.warning(f"Agent {agent_name} not found - skipping")
            continue

        try:
            agent_result = await execute_agent(
                orchestrator, agent_name, agents[agent_name], cycle_state, recipient_context
            )
            results["agents"][agent_name] = agent_result

            if not agent_result.get("success", True):
                results["success"] = False

        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}")
            results["agents"][agent_name] = {"success": False, "error": str(e)}
            results["success"] = False

    return results


async def execute_phase_parallel(
    orchestrator,
    phase: OutreachExecutionPhase,
    agents: Dict[str, Callable],
    cycle_state: OutreachCycleState,
    recipient_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute phase agents in parallel."""

    tasks = []
    agent_names = []

    for agent_name in phase.agents:
        if agent_name not in agents:
            continue
        agent_names.append(agent_name)
        tasks.append(execute_agent(orchestrator, agent_name, agents[agent_name], cycle_state, recipient_context))

    results = {"success": True, "agents": {}}

    if tasks:
        agent_results = await asyncio.gather(*tasks, return_exceptions=True)

        for agent_name, result in zip(agent_names, agent_results):
            if isinstance(result, Exception):
                results["agents"][agent_name] = {"success": False, "error": str(result)}
                results["success"] = False
            else:
                results["agents"][agent_name] = result
                if not result.get("success", True):
                    results["success"] = False

    return results


async def execute_agent(
    orchestrator,
    agent_name: str,
    agent_callable: Callable,
    cycle_state: OutreachCycleState,
    recipient_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute a single agent with tracking."""

    start_time = datetime.utcnow()

    try:
        # Inject few-shot examples if available
        enhanced_context = inject_few_shots(orchestrator, agent_name, recipient_context)

        # Execute agent
        result = await agent_callable(enhanced_context)

        # Track execution
        execution_entry = {
            "agent": agent_name,
            "success": result.get("success", True),
            "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "quality_score": result.get("quality_score"),
            "timestamp": start_time.isoformat(),
        }
        cycle_state.execution_log.append(execution_entry)

        # Track modifications
        if result.get("modified"):
            for item in result.get("modified", []):
                cycle_state.modified_items.add(item)

        # Track quality scores
        if result.get("quality_score"):
            cycle_state.quality_scores[agent_name] = result["quality_score"]

        # Track messages generated
        if result.get("message"):
            orchestrator.outputs["message_generator"] = result["message"]
            cycle_state.messages_generated += 1

        # Track personalization score
        if result.get("personalization_score"):
            cycle_state.personalization_score = result["personalization_score"]

        # Emit signals based on result
        if orchestrator.signal_bus and not result.get("success", True):
            await orchestrator.signal_bus.emit(
                SignalType.VALIDATION_FAILURE,
                f"Agent {agent_name} reported failure",
                source=agent_name
            )

        # Update outputs
        if result.get("output"):
            orchestrator.outputs[agent_name] = result["output"]

        return result

    except Exception as e:
        logger.error(f"Agent {agent_name} execution error: {e}")
        cycle_state.execution_log.append({
            "agent": agent_name,
            "success": False,
            "error": str(e),
            "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            "timestamp": start_time.isoformat(),
        })
        return {"success": False, "error": str(e)}


def inject_few_shots(orchestrator, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Inject relevant few-shot examples into context."""

    try:
        from apps_shared.few_shot_library import FewShotLibrary
    except ImportError:
        return context

    import copy
    enhanced = copy.deepcopy(context)

    # Map agents to relevant few-shot patterns
    agent_patterns = {
        "hook_generator": ["outreach_hooks", "personalized_openers"],
        "value_composer": ["value_propositions", "metric_binding"],
        "cta_generator": ["call_to_action", "urgency_drivers"],
        "tone_validator": ["tone_examples", "archetype_tones"],
        "personalization_engine": ["personalization_patterns"],
    }

    patterns = agent_patterns.get(agent_name, [])
    if patterns:
        few_shots = {}
        for pattern in patterns:
            few_shot = FewShotLibrary.get_all_patterns().get(pattern)
            if few_shot:
                few_shots[pattern] = few_shot

        if few_shots:
            enhanced["few_shot_examples"] = few_shots

    return enhanced
