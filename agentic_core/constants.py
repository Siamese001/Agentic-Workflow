```python
"""
Constants for the Agentic Core system.

Contains all shared constants used across the agentic framework.
"""


# Complexity thresholds
MAX_COMPLEXITY = 10
MAX_FUNC_LINES = 50
MAX_NESTING_SPACES = 40


# File system constants
ALLOWED_ROOT_FILES = {
    "README.md",
    "requirements.txt",
    "setup.py",
    "pyproject.toml",
    ".gitignore",
    "Dockerfile",
    "docker-compose.yml",
}


# Few-shot prompts for various agents
FEW_SHOT_STRATEGIC = """
You are the StrategicPlanner, an expert in mission planning and coordination.

Your role is to:
1. Generate comprehensive mission plans
2. Coordinate agent execution order
3. Allocate resources efficiently
4. Anticipate potential issues

Mission Plan Structure:
{
    "mission_id": "unique_identifier",
    "cycle_id": 1,
    "priority": "HIGH|MEDIUM|LOW",
    "objective": "Clear mission objective",
    "phases": [...],
    "risk_assessment": {...}
}
"""


FEW_SHOT_SHERLOCK = """
You are Sherlock, the debugging specialist.

Your role is to:
1. Analyze code issues systematically
2. Identify root causes
3. Propose targeted fixes
4. Verify fix effectiveness

Debugging Process:
1. Gather evidence (logs, stack traces)
2. Formulate hypotheses
3. Test hypotheses
4. Implement solution
"""


FEW_SHOT_CONCURRENCY = """
You are the ConcurrencyGuardian, an expert in managing concurrent operations.

Your role is to:
1. Prevent race conditions
2. Manage resource locks
3. Detect deadlocks
4. Ensure thread safety

Lock Usage Pattern:
1. Acquire lock with timeout
2. Execute critical section
3. Always release in finally block
4. Use async/await for I/O operations
"""


# Performance thresholds
MAX_PHASE_TIME = 300  # seconds
MEMORY_THRESHOLD_MB = 100  # MB growth per cycle
PERFORMANCE_DEGRADATION_THRESHOLD = 0.5  # 50% slower than average


# Lock configuration
DEFAULT_LOCK_TIMEOUT = 30  # seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 0.5  # seconds


# History limits
MAX_SNAPSHOTS = 100
BENCHMARK_HISTORY_SIZE = 1000
MAX_ALERTS_PER_TYPE = 50


# Environment variable names
CANON_REMOTE_REPO = "CANON_REMOTE_REPO"
GOOGLE_API_KEY = "GOOGLE_API_KEY"
ENABLE_FUZZ = "ENABLE_FUZZ"
ADDITIONAL_REPO_ROOTS = "ADDITIONAL_REPO_ROOTS"


# Directory constants
MEMORY_DIR = "observability/memory"
ALERTS_DIR = "observability/alerts"
CACHE_DIR = "observability/cache"
```