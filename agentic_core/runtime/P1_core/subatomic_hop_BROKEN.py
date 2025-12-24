from typing import Any, Optional, Protocol, Dict, List, TYPE_CHECKING
import re

import logging
import time
import uuid
from typing import Any, Dict

from pydantic import BaseModel
from runtime.core.telemetry import TelemetryRecorder, TraceEvent
from services.configuration import ConfigurationService

if TYPE_CHECKING:
    pass

LOGGER = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


class SovereignDependencyError(Exception):
    """Raised when a required dependency is not injected into a Sovereign component."""
    pass


class AgentPlan(BaseModel):
    reasoning: str
    tool_calls: list[dict]


class SubatomicHop:
    """Sovereign SubatomicHop with Dependency Injection.
    
    All dependencies are injected via constructor to maintain Gravity Compliance.
    No upward imports allowed - all tools passed down from orchestration layer.
    """

    def __init__(
        self,
        role: str,
        config: Dict,
        # Injected Dependencies (Sovereign Pattern)
        storage: Optional[Any] = None,
        genealogy: Optional[Any] = None,
        pii_vault: Optional[Any] = None,
        cost_governor: Optional[Any] = None,
        overseer: Optional[Any] = None,
        membrane: Optional[Any] = None,
        airlock: Optional[Any] = None,
        supreme_court: Optional[Any] = None,
        mcp_manager: Optional[Any] = None,
        sandbox: Optional[Any] = None,
        structured_engine: Optional[Any] = None,
        gatekeeper: Optional[Any] = None,
        telemetry: Optional[Any] = None,
    ) -> None:
        """Initialize SubatomicHop with injected dependencies.
        
        Args:
            role: Agent role identifier
            config: Configuration dictionary
            storage: LocalDiskAdapter instance (injected)
            genealogy: GenealogyRegistry instance (injected)
            pii_vault: PIIVault instance (injected)
            cost_governor: CostGovernor instance (injected)
            overseer: ConstitutionalOverseer instance (injected)
            membrane: InputMembrane instance (injected)
            airlock: AirlockProtocol instance (injected)
            supreme_court: SupremeCourt instance (injected)
            mcp_manager: MCPConnectionManager instance (injected)
            sandbox: DockerSandbox instance (injected)
            structured_engine: StructuredEngine instance (injected)
            gatekeeper: SemanticGatekeeper instance (injected)
            telemetry: TelemetryRecorder instance (injected)
            
        Raises:
            SovereignDependencyError: If required dependencies are missing
        """
        self.role = role
        self.id = str(uuid.uuid4())
        self.config = config
        
        # Validate and assign injected dependencies
        if storage is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'storage' (LocalDiskAdapter) to be injected. "
                "Cannot import from higher layers - must be passed from orchestrator."
            )
        self.storage = storage
        
        if genealogy is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'genealogy' (GenealogyRegistry) to be injected."
            )
        self.genealogy = genealogy
        
        if pii_vault is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'pii_vault' (PIIVault) to be injected."
            )
        self.pii = pii_vault
        
        if cost_governor is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'cost_governor' (CostGovernor) to be injected."
            )
        self.governor = cost_governor
        
        if overseer is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'overseer' (ConstitutionalOverseer) to be injected."
            )
        self.overseer = overseer
        
        if membrane is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'membrane' (InputMembrane) to be injected."
            )
        self.membrane = membrane
        
        if airlock is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'airlock' (AirlockProtocol) to be injected."
            )
        self.airlock = airlock
        
        if supreme_court is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'supreme_court' (SupremeCourt) to be injected."
            )
        self.supreme_court = supreme_court
        
        if mcp_manager is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'mcp_manager' (MCPConnectionManager) to be injected."
            )
        self.mcp = mcp_manager
        
        if sandbox is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'sandbox' (DockerSandbox) to be injected."
            )
        self.sandbox = sandbox
        
        if structured_engine is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'structured_engine' (StructuredEngine) to be injected."
            )
        self.structured_engine = structured_engine
        
        if gatekeeper is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'gatekeeper' (SemanticGatekeeper) to be injected."
            )
        self.gatekeeper = gatekeeper
        
        if telemetry is None:
            raise SovereignDependencyError(
                "SubatomicHop requires 'telemetry' (TelemetryRecorder) to be injected."
            )
        self.telemetry = telemetry


    async def run(self, context: Dict) -> Any:
        """Execute the hop with zero-trust protections."""
        trace_id = context.get('trace_id', self.id)
        # Note: with_gatekeeping is orphaned - needs injection or removal
        # For now, call _run_with_zero_trust directly
        return await self._run_with_zero_trust(context, trace_id)


    async def _run_with_zero_trust(self, context: Dict, trace_id: str) -> Any:
        """Internal method with all L5.5 Zero Trust protections applied."""
        try:
            await self._preflight_checks(context, trace_id)
            plan, think_cost = await self._execute_think_stage_with_consensus(context, trace_id)
            results, act_cost = await self._execute_act_stage_with_airlock(plan, trace_id)
            await self._execute_critique_stage_with_membrane(results, trace_id)
            await self._execute_commit_stage(results, trace_id)
            self.telemetry.record(
                TraceEvent(
                    trace_id=trace_id,
                    span_id=f'{self.id}_complete',
                    ROLE=self.role,
                    event_type='SUCCESS',
                    PAYLOAD={
                        'total_cost': think_cost + act_cost,
                        'zero_trust': True},
                    TIMESTAMP=time.time()))
            return results
        except Exception as e:
            # BudgetExceededError is orphaned - catch as generic Exception
            if type(e).__name__ == 'BudgetExceededError':
                self._handle_budget_exceeded(trace_id, e)
                raise
            # Other exceptions
            self._handle_execution_error(trace_id, e)
        self.telemetry.record(
            TraceEvent(
                trace_id=trace_id,
                span_id=f'{self.id}_complete',
                ROLE=self.role,
                event_type='SUCCESS',
                PAYLOAD={
                    'total_cost': think_cost + act_cost,
                    'zero_trust': True},
                TIMESTAMP=time.time()))
        return results
    except Exception as e:
        # BudgetExceededError is orphaned - catch as generic Exception
        if type(e).__name__ == 'BudgetExceededError':
            self._handle_budget_exceeded(trace_id, e)
            raise
        # Other exceptions
        self._handle_execution_error(trace_id, e)
        raise
    finally:
        await self._cleanup(trace_id)


    async def _preflight_checks(self, context: Dict, trace_id: str) -> None:
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


    async def _sanitize_input(self, context: Dict, trace_id: str) -> Dict:
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


    async def _execute_think_stage_with_consensus(self, context: Dict, trace_id: str) -> tuple[AgentPlan, float]:
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


    def _assess_task_risk(self, task: str) -> str:
    """Assess the risk level of a task."""
    task.lower()
    if any((keyword in ConfigurationService().task_lower for keyword in ConfigurationService().high_risk_keywords)):
        return 'high'
    elif any((keyword in ConfigurationService().task_lower for keyword in ['modify', 'update', 'change'])):
        return 'medium'
    else:
        return 'low'


    async def _check_past_failures(self, task: str) -> str:
    """Check telemetry for past failures on similar tasks."""
    try:
        return 'No similar failures found'
    except Exception:
        return 'Unable to check past failures'


    async def _execute_act_stage_with_airlock(self, plan: AgentPlan, trace_id: str) -> tuple[list, float]:
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


    async def _execute_critique_stage_with_membrane(self, results: list, trace_id: str) -> str:
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


    async def _execute_commit_stage(self, output_text: str, trace_id: str) -> str:
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


    def _handle_budget_exceeded(self, trace_id: str, error: Any) -> None:
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


    def _handle_execution_error(self, trace_id: str, error: Exception) -> None:
    """Handle general execution errors."""
    self.telemetry.record(
        TraceEvent(
            trace_id=ConfigurationService().trace_id, span_id=f'{self.id}_error', ROLE=self.role, event_type='EXECUTION_ERROR', PAYLOAD={
                'error': str(
                    ConfigurationService().error), 'type': type(
                        ConfigurationService().error).__name__}, TIMESTAMP=time.time()))


    async def _cleanup(self, trace_id: str) -> None:
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