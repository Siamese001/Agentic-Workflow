"""

agentic_core/interfaces/execution_agents.py



Sovereign Execution Agent interfaces for L1_cognition consumption.



Re-exports execution agents and related components so L1_cognition can

access execution services without directly importing from L2_execution.



AUTHORITY CONSTRAINTS:

- Execution agents provide execution authority through controlled interfaces

- All execution operations are recorded for audit and replay

- No direct execution without proper authorization



USAGE (L1_cognition):

    from agentic_core.interfaces.execution_agents import (

        EmbeddingSovereignAgent,

        RedisSovereignAgent,

    )

"""
from __future__ import annotations
from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import EmbeddingSovereignAgent
from agentic_core.L2_execution.reasoning.RedisSovereignAgent import RedisSovereignAgent
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
__all__ = ['EmbeddingSovereignAgent', 'RedisSovereignAgent']
