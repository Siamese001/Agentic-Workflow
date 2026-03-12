"""
HOPStageCapability — Pure capability mixin for LIC HOP pipeline stages.

Extracts the shared IO/State plumbing that all 9 HOP agents repeat:
  - Defensive buffer reads with trace logging and validation
  - PHASE_START / DECISION_FINAL trace bookends
  - Required-input validation with clear error messages
  - Standard _process(buffer, registry) template

The business logic remains in each agent's _process() override.
Agents compose this via multiple inheritance alongside LICAgentBase.

    @dataclass
    class HOP5GenerationAgent(HOPStageCapability, LICAgentBase):
        ...

[CREATED 2026-02-08] Cluster 4 extraction per dedup critique §3.
"""
from __future__ import annotations
from typing import Any, ClassVar
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class HOPStageCapability:
    """Pure capability mixin for LIC HOP pipeline stage agents.

    Provides:
        - read_required_inputs(): Defensive buffer reads with trace logging
        - run_stage(): Template method with PHASE_START/DECISION_FINAL bookends
        - write_output(): Standard buffer write with trace logging

    Subclasses MUST:
        - Set HOP_STAGE_NAME (e.g., "hop5_generation")
        - Set REQUIRED_INPUTS (e.g., ["hop1_analysis", "mission_input"])
        - Override _process(buffer, registry) with business logic
    """
    HOP_STAGE_NAME: ClassVar[str] = ''
    REQUIRED_INPUTS: ClassVar[list[str]] = []

    def read_required_inputs(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> dict[str, Any]:
        """Read and validate all required upstream inputs from the buffer.

        Args:
            buffer: The ImmutableStagingBuffer to read from.
            registry: The TraceRegistry for logging.

        Returns:
            Dictionary mapping input key → value for all required inputs.

        Raises:
            RuntimeError: If any required input is missing from the buffer.
        """
        inputs: dict[str, Any] = {}
        agent_name = self.__class__.__name__
        for key in self.REQUIRED_INPUTS:
            value = buffer.read(key)
            if value is None:
                registry.add_trace('DATA_ERROR', {'msg': f'Missing {key}'})
                raise RuntimeError(f'{agent_name} missing required upstream input: {key}')
            inputs[key] = value
        return inputs

    def write_output(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry, output_data: dict[str, Any], *, decision_meta: dict[str, Any] | None=None) -> None:
        """Write stage output to the buffer and log the DECISION_FINAL trace.

        Args:
            buffer: The ImmutableStagingBuffer to write to.
            registry: The TraceRegistry for logging.
            output_data: The output dictionary to write.
            decision_meta: Optional metadata for the DECISION_FINAL trace.
        """
        if not self.HOP_STAGE_NAME:
            raise ValueError(f'{self.__class__.__name__} must set HOP_STAGE_NAME')
        buffer.write_once(self.HOP_STAGE_NAME, output_data)
        registry.add_trace('DECISION_FINAL', decision_meta or {'status': 'COMPLETE'})

    def run_stage(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """Template method: trace bookends + delegate to _process.

        Provides consistent PHASE_START tracing, then delegates to the
        agent's _process() implementation.

        Args:
            buffer: The ImmutableStagingBuffer for the mission.
            registry: The TraceRegistry for the mission.
        """
        registry.add_trace('PHASE_START', {'agent': self.__class__.__name__})
        self._process(buffer, registry)

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """Execute stage-specific business logic. Must be overridden."""
        raise NotImplementedError(f'{self.__class__.__name__} must implement _process()')
