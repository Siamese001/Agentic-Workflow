import sys
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

sys.path.insert(0, '.')
from agentic_core.L2_execution.engines.rollback_refiner import DefaultDeterministicRollbackRefiner
from agentic_core.L2_execution.types.resource_prediction_types import FailureSignature
from agentic_core.L2_execution.types.rollback_refinement_types import RollbackRefinementRequest, RollbackStrategyId

refiner = DefaultDeterministicRollbackRefiner()
sig = FailureSignature(component="test", failure_type="timeout", fingerprint="12345678")
request = RollbackRefinementRequest(failure_signature=sig, candidates=(), history_bytes=None)

try:
    r = refiner.refine(request=request)
    print(f"empty candidates: returned {r!r}")
except Exception as e:
    print(f"empty candidates: raised {type(e).__name__}: {e}")
