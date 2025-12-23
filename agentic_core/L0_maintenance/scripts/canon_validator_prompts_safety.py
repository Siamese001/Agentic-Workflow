"""
Safety and concurrency few-shot patterns.
Used by SafetyInspector, ConcurrencyGuardian, SecurityEnforcer.
"""

FEW_SHOT_SAFETY = """
FEW-SHOT SAFETY FIXES (SafetyInspector — Follow exactly):

EXAMPLE 1: Dangerous eval/exec
BAD:
value = eval(user_input)

GOOD:
import ast
try:
    value = ast.literal_eval(user_input)
except (ValueError, SyntaxError):
    raise ValueError("Invalid literal")

EXAMPLE 2: subprocess Without Restrictions
BAD:
subprocess.run(command)
subprocess.Popen(user_command, shell=True)

GOOD:
subprocess.run(["git", "pull"], check=True, cwd="/repo")

EXAMPLE 3: Hardcoded Secrets
BAD:
API_KEY = "sk-1234567890abcdef"

GOOD:
import os
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable required")

Never introduce eval/exec/subprocess/shell=True.
Always require env vars for secrets.
"""

FEW_SHOT_CONCURRENCY = """
FEW-SHOT CONCURRENCY FIXES (ConcurrencyGuardian — Follow exactly):

EXAMPLE 1: Shared Mutable Dict Without Lock
BAD (race condition):
shared_cache = {}
def update_cache(key, value):
    shared_cache[key] = value  # Not thread-safe

GOOD (safe):
from threading import Lock
shared_cache = {}
cache_lock = Lock()

def update_cache(key, value):
    with cache_lock:
        shared_cache[key] = value

EXAMPLE 2: Compound Assignment (+=) on Shared State
BAD:
    total += amount  # Reads, modifies, writes — race!

GOOD:
    with total_lock:
        total += amount

EXAMPLE 3: Async Shared State Without AsyncLock
BAD:
shared_counter = 0
async def increment():
    shared_counter += 1  # Not safe in asyncio

GOOD:
from asyncio import Lock
shared_counter = 0
counter_lock = Lock()

async def increment():
    async with counter_lock:
        shared_counter += 1

Prioritize context managers. Never use time.sleep() for synchronization.
"""
