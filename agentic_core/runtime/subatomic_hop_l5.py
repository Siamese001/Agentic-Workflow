import logging
import time
import uuid
from typing import Any, Dict

from pydantic import BaseModel
from runtime.core.telemetry import TelemetryRecorder, TraceEvent

from agentic_core.L2_execution.mcp_manager import MCPConnectionManager
from agentic_core.L2_execution.sandbox import DockerSandbox
from agentic_core.L4_state.genealogy import GenealogyRegistry
from agentic_core.L4_state.storage import LocalDiskAdapter
from agentic_core.L5_safety.governor import CostGovernor
from agentic_core.L5_safety.overseer import ConstitutionalOverseer
from agentic_core.L5_safety.pii_vault import PIIVault

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)


# Imports from above


class AgentPlan(BaseModel):
    reasoning: str
    tool_calls: list[dict]


class SubatomicHop:
    def __init__(self: Any, role: str, config: Dict) -> None:
        self.role = role
        self.id = str(uuid.uuid4())

        # Hardened Components
        self.storage = LocalDiskAdapter()
        self.genealogy = GenealogyRegistry()
        self.pii = PIIVault()
        self.governor = CostGovernor()
        self.overseer = ConstitutionalOverseer(config['openai_client'])
        self.mcp = MCPConnectionManager(config['mcp_mappings'])
        self.sandbox = DockerSandbox()
        self.telemetry = TelemetryRecorder()

    async def run(self: Any, context: Dict) -> None:
        trace_id = context.get('trace_id', self.id)

        try:
            # 1. PRE-FLIGHT
            await self.mcp.connect(self.role)
            clean_context = self.pii.redact(trace_id, str(context))
            self.genealogy.register_attempt(
                trace_id, "start", str(hash(clean_context)))

            # 2. THINK (L1)
            # (Assuming self.llm is an Instructor client)
            PLAN = await self.llm.chat.completions.create(
                MODEL="gpt-4",
                response_model=AgentPlan,
                MESSAGES=[
                    {"role": "system",
                        "content": f"You are {self.role}. Tools: {self.mcp.tools}"},
                    {"role": "user", "content": clean_context}
                ]
            )
            self.telemetry.record(TraceEvent(trace_id,
                                             self.id,
                                             self.role,
                                             "THINK",
                                             PLAN.model_dump(),
                                             time.time()))

            # 3. ACT (L2)
            RESULTS = []
            for call in PLAN.tool_calls:
                if call['name'] == 'run_python':
                    RES = self.sandbox.run_code(call['args']['code'])
                else:
                    RES = await self.mcp.call_tool(call['name'], call['args'])
                RESULTS.append(RES)

            output_text = f"Plan executed. Results: {RESULTS}"

            # 4. CRITIQUE (L5 Safety)
            await self.overseer.verify(output_text)  # Raises Error if bad

            # 5. COMMIT (L4 State)
            final_output = self.pii.restore(trace_id, output_text)
            await self.storage.write_blob(f"hops/{self.id}.txt", final_output.encode())

            return final_output

        except Exception as e:
            self.telemetry.record(TraceEvent(trace_id,
                                             self.id,
                                             self.role,
                                             "ERROR",
                                             {"error": str(e)},
                                             time.time()))
            raise e
        finally:
            await self.mcp.cleanup()