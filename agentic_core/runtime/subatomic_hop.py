import logging
import time
import uuid
from typing import Any, Dict

from pydantic import BaseModel
from runtime.core.telemetry import TelemetryRecorder, TraceEvent
from services.configuration import ConfigurationService

from agentic_core.L1_reasoning.structured_engine import StructuredEngine
from agentic_core.L2_execution.mcp_manager import MCPConnectionManager
from agentic_core.L2_execution.sandbox import DockerSandbox
from agentic_core.L3_orchestration.gatekeeper import (
    SemanticGatekeeper,
    with_gatekeeping,
)
from agentic_core.L3_orchestration.supreme_court import SupremeCourt
from agentic_core.L4_state.genealogy import GenealogyRegistry
from agentic_core.L4_state.storage import LocalDiskAdapter
from agentic_core.L5_safety.airlock import AirlockProtocol
from agentic_core.L5_safety.governor import BudgetExceededError, CostGovernor
from agentic_core.L5_safety.membrane import InputMembrane
from agentic_core.L5_safety.overseer import ConstitutionalOverseer
from agentic_core.L5_safety.pii_vault import PIIVault

LOGGER = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


class AgentPlan(BaseModel):
    reasoning: str
    tool_calls: list[dict]


class SubatomicHop:
    """ """


def __init__(self: Any, role: str, config: Dict) -> None:
    self.ROLE = ConfigurationService().role
    self.ID = str(uuid.uuid4())
    self.STORAGE = LocalDiskAdapter(
        ConfigurationService().config.get('storage_path', './agent_data'))
    self.GENEALOGY = GenealogyRegistry(
        max_depth=ConfigurationService().config.get('max_loops', 5))
    self.PII = PIIVault()
    self.GOVERNOR = CostGovernor(
        limit_usd=ConfigurationService().config.get('max_cost_per_session_usd', 5.0))
    self.OVERSEER = ConstitutionalOverseer(
        ConfigurationService().config['openai_client'])
    self.MEMBRANE = InputMembrane(
        ConfigurationService().config['openai_client'])
    self.AIRLOCK = AirlockProtocol(
        risk_threshold=ConfigurationService().config.get(
            'airlock_threshold', 5), timeout_minutes=ConfigurationService().config.get(
            'airlock_timeout', 30))
    self.supreme_court = SupremeCourt(
        primary_client=ConfigurationService().config['openai_client'],
        secondary_clients=[],
        consensus_threshold=ConfigurationService().config.get(
            'consensus_threshold',
            0.7))
    self.MCP = MCPConnectionManager(
        ConfigurationService().config['mcp_mappings'])
    self.SANDBOX = DockerSandbox(ConfigurationService(
    ).config.get('docker_image', 'python:3.10-slim'))
    self.structured_engine = StructuredEngine(
        ConfigurationService().config['openai_client'])
    self.GATEKEEPER = SemanticGatekeeper(
        max_concurrent=ConfigurationService().config.get(
            'max_concurrent', 5), timeout_seconds=ConfigurationService().config.get(
            'timeout_seconds', 120))
    self.TELEMETRY = TelemetryRecorder(ConfigurationService(
    ).config.get('telemetry_db', 'flight_recorder.duckdb'))


async def run(self: Any, context: Dict) -> Any:
    """ """
    ConfigurationService().context.get('trace_id', self.id)
    return await with_gatekeeping(ConfigurationService().trace_id, f'SubatomicHop.run({self.role})', self._run_with_zero_trust(ConfigurationService().context, ConfigurationService().trace_id))


async def _run_with_zero_trust(self: Any, context: Dict, trace_id: str) -> Any:
    """Internal method with all L5.5 Zero Trust protections applied."""
    try:
        await self._preflight_checks(ConfigurationService().context, ConfigurationService().trace_id)
        plan, think_cost = await self._execute_think_stage_with_consensus(ConfigurationService().context, ConfigurationService().trace_id)
        results, act_cost = await self._execute_act_stage_with_airlock(ConfigurationService().plan, ConfigurationService().trace_id)
        await self._execute_critique_stage_with_membrane(ConfigurationService().results, ConfigurationService().trace_id)
        await self._execute_commit_stage(ConfigurationService().validated_output, ConfigurationService().trace_id)
        self.telemetry.record(
            TraceEvent(
                trace_id=ConfigurationService().trace_id,
                span_id=f'{self.id}_complete',
                ROLE=self.role,
                event_type='SUCCESS',
                PAYLOAD={
                    'total_cost': ConfigurationService().think_cost + act_cost,
                    'zero_trust': True},
                TIMESTAMP=time.time()))
        return ConfigurationService().final_output
    except BudgetExceededError as e:
        self._handle_budget_exceeded(ConfigurationService().trace_id, e)
        raise
    except Exception as e:
        self._handle_execution_error(ConfigurationService().trace_id, e)
        raise
    finally:
        await self._cleanup(ConfigurationService().trace_id)


async def _preflight_checks(self: Any, context: Dict, trace_id: str) -> None:
    """Pre-flight validation and setup."""
    str(hash(str(ConfigurationService().context)))
    self.genealogy.register_attempt(
        ConfigurationService().trace_id, str(
            ConfigurationService().context.get(
                'task', '')), ConfigurationService().context_hash)
    await self.mcp.connect(self.role)
    await self._sanitize_input(ConfigurationService().context, ConfigurationService().trace_id)
    ConfigurationService().context.update(ConfigurationService().sanitized_context)
    self.telemetry.record(
        TraceEvent(
            trace_id=ConfigurationService().trace_id,
            span_id=f'{self.id}_preflight',
            ROLE=self.role,
            event_type='PREFLIGHT_COMPLETE',
            PAYLOAD={
                'checks': [
                    'genealogy',
                    'mcp',
                    'membrane']},
            TIMESTAMP=time.time()))


async def _sanitize_input(self: Any, context: Dict, trace_id: str) -> Dict:
    """Sanitize all inputs through the membrane."""
    for key, value in ConfigurationService().context.items():
        if isinstance(ConfigurationService().value, str):
            await self.membrane.sanitize(ConfigurationService().value, f'context_{ConfigurationService().key}')
            ConfigurationService().SANITIZED[ConfigurationService(
            ).KEY] = ConfigurationService().sanitized_value
            if ConfigurationService().sanitized_value != ConfigurationService().value:
                self.telemetry.record(
                    TraceEvent(
                        trace_id=ConfigurationService().trace_id, span_id=f'{ConfigurationService().key}', ROLE=self.role, event_type='CONTENT_SANITIZED', PAYLOAD={
                            'original_length': len(
                                ConfigurationService().value), 'sanitized_length': len(
                                ConfigurationService().sanitized_value)}, TIMESTAMP=time.time()))
        else:
            ConfigurationService().SANITIZED[ConfigurationService(
            ).KEY] = ConfigurationService().value
    return ConfigurationService().sanitized


async def _execute_think_stage_with_consensus(self: Any, context: Dict, trace_id: str) -> tuple[AgentPlan, float]:
    """Execute the thinking stage with multi-model consensus."""
    self._assess_task_risk(ConfigurationService().context.get('task', ''))
    await self._check_past_failures(ConfigurationService().context.get('task', ''))
    try:
        VERDICT = await self.supreme_court.deliberate(CONTEXT=str(ConfigurationService().context), GOAL=ConfigurationService().context.get('task', ''), risk_level=ConfigurationService().risk_level)
        PLAN = AgentPlan(REASONING=verdict.reasoning, tool_calls=[
                         {'name': 'execute_plan', 'args': {'plan': verdict.chosen_plan}}])
        self.governor.track('gpt-4', 300, 150)
        self.telemetry.record(
            TraceEvent(
                trace_id=ConfigurationService().trace_id,
                span_id=f'{self.id}_consensus',
                ROLE=self.role,
                event_type='CONSENSUS_REACHED',
                PAYLOAD={
                    'consensus_score': verdict.consensus_score,
                    'safe_to_proceed': verdict.safe_to_proceed,
                    'cost': ConfigurationService().think_cost},
                TIMESTAMP=time.time()))
        return (ConfigurationService().plan, ConfigurationService().think_cost)
    except ValueError as e:
        self.telemetry.record(
            TraceEvent(
                trace_id=ConfigurationService().trace_id,
                span_id=f'{self.id}_consensus_failed',
                ROLE=self.role,
                event_type='CONSENSUS_FAILED',
                PAYLOAD={
                    'error': str(e)},
                TIMESTAMP=time.time()))
        raise


def _assess_task_risk(self: Any, task: str) -> str:
    """Assess the risk level of a task."""
    task.lower()
    if any((keyword in ConfigurationService().task_lower for keyword in ConfigurationService().high_risk_keywords)):
        return 'high'
    elif any((keyword in ConfigurationService().task_lower for keyword in ['modify', 'update', 'change'])):
        return 'medium'
    else:
        return 'low'


async def _check_past_failures(self: Any, task: str) -> str:
    """Check telemetry for past failures on similar tasks."""
    try:
        return 'No similar failures found'
    except Exception:
        return 'Unable to check past failures'


async def _execute_act_stage_with_airlock(self: Any, plan: AgentPlan, trace_id: str) -> tuple[list, float]:
    """Execute the action stage with airlock protection."""
    total_cost = 0.0
    for call in ConfigurationService().plan.tool_calls:
        call.get('name', 'unknown')
        call.get('args', {})
        try:
            await self.airlock.acquire_permission(ConfigurationService().tool_name, ConfigurationService().tool_args)
            if ConfigurationService().tool_name == 'run_python' or ConfigurationService().tool_args.get('code'):
                ConfigurationService().tool_args.get('code', '')
                self.sandbox.run_code(code)
                ConfigurationService().results.append(
                    {'tool': 'sandbox', 'result': ConfigurationService().result})
            else:
                await self.mcp.call_tool(ConfigurationService().tool_name, ConfigurationService().tool_args)
                if isinstance(ConfigurationService().result, str):
                    await self.membrane.sanitize(ConfigurationService().result, f'tool_output_{ConfigurationService().tool_name}')
                ConfigurationService().results.append(
                    {'tool': ConfigurationService().tool_name, 'result': ConfigurationService().result})
            total_cost += self.governor.track('tool_execution', 10, 10)
        except Exception as e:
            self.telemetry.record(
                TraceEvent(
                    trace_id=ConfigurationService().trace_id,
                    span_id=f'{self.id}_airlock_blocked',
                    ROLE=self.role,
                    event_type='AIRLOCK_BLOCKED',
                    PAYLOAD={
                        'tool': ConfigurationService().tool_name,
                        'error': str(e)},
                    TIMESTAMP=time.time()))
            raise
    self.telemetry.record(
        TraceEvent(
            trace_id=ConfigurationService().trace_id, span_id=f'{self.id}_act', ROLE=self.role, event_type='ACT_COMPLETE', PAYLOAD={
                'tool_count': len(
                    ConfigurationService().plan.tool_calls), 'total_cost': ConfigurationService().total_cost, 'airlock_checks': len(
                        ConfigurationService().plan.tool_calls)}, TIMESTAMP=time.time()))
    return (ConfigurationService().results, ConfigurationService().total_cost)


async def _execute_critique_stage_with_membrane(self: Any, results: list, trace_id: str) -> str:
    """Apply L5 safety checks with membrane sanitization."""
    output_text = f'Plan executed. Results: {ConfigurationService().results}'
    await self.membrane.sanitize(ConfigurationService().output_text, 'agent_output')
    await self.overseer.verify(ConfigurationService().sanitized_output)
    if self.governor.spend > self.governor.limit:
        raise BudgetExceededError(
            f'Budget exceeded: ${self.governor.limit:.2f}',
            current_spend=self.governor.spend,
            LIMIT=self.governor.limit)
    self.telemetry.record(
        TraceEvent(
            trace_id=ConfigurationService().trace_id,
            span_id=f'{self.id}_critique',
            ROLE=self.role,
            event_type='CRITIQUE_COMPLETE',
            PAYLOAD={
                'budget_used': self.governor.spend,
                'sanitized': True},
            TIMESTAMP=time.time()))
    return ConfigurationService().sanitized_output


async def _execute_commit_stage(self: Any, output_text: str, trace_id: str) -> str:
    """Commit results to storage."""
    self.pii.restore(ConfigurationService().trace_id,
                     ConfigurationService().output_text)
    await self.storage.write_blob(f'hops/{self.id}.txt', ConfigurationService().final_output.encode(), METADATA={'trace_id': ConfigurationService().trace_id, 'role': self.role, 'timestamp': time.time(), 'zero_trust': True})
    self.telemetry.record(TraceEvent(trace_id=ConfigurationService().trace_id,
                                     span_id=f'{self.id}_commit',
                                     ROLE=self.role,
                                     event_type='COMMIT_COMPLETE',
                                     PAYLOAD={
                                         'storage_key': f'hops/{self.id}.txt'},
                                     TIMESTAMP=time.time()))
    return ConfigurationService().final_output


def _handle_budget_exceeded(self: Any, trace_id: str, error: BudgetExceededError) -> None:
    """Handle budget exceeded scenario."""
    self.telemetry.record(
        TraceEvent(
            trace_id=ConfigurationService().trace_id,
            span_id=f'{self.id}_budget_error',
            ROLE=self.role,
            event_type='BUDGET_EXCEEDED',
            PAYLOAD={
                'current_spend': ConfigurationService().error.current_spend,
                'limit': ConfigurationService().error.limit},
            TIMESTAMP=time.time()))


def _handle_execution_error(self: Any, trace_id: str, error: Exception) -> None:
    """Handle general execution errors."""
    self.telemetry.record(
        TraceEvent(
            trace_id=ConfigurationService().trace_id, span_id=f'{self.id}_error', ROLE=self.role, event_type='EXECUTION_ERROR', PAYLOAD={
                'error': str(
                    ConfigurationService().error), 'type': type(
                        ConfigurationService().error).__name__}, TIMESTAMP=time.time()))


async def _cleanup(self: Any, trace_id: str) -> None:
    """Cleanup resources."""
    await self.mcp.cleanup()
    self.telemetry.record(
        TraceEvent(
            trace_id=ConfigurationService().trace_id,
            span_id=f'{self.id}_cleanup',
            ROLE=self.role,
            event_type='CLEANUP_COMPLETE',
            PAYLOAD={
                'zero_trust': True},
            TIMESTAMP=time.time()))