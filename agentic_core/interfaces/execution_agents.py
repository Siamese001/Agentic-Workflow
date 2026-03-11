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



MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Import from L2_execution where execution agents are located

from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import EmbeddingSovereignAgent

from agentic_core.L2_execution.reasoning.RedisSovereignAgent import RedisSovereignAgent



__all__ = [

    "EmbeddingSovereignAgent",

    "RedisSovereignAgent",

]
