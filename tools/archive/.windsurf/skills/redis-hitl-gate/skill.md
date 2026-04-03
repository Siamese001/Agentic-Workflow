---
description: Enforces Human-in-the-Loop when Redis ADG queries fail - prevents silent fallback to filesystem tools without user authorization
---
# Redis HITL Gate

Enforces Human-in-the-Loop when Redis ADG queries fail. Prevents silent fallback to filesystem tools without user authorization.

## When to Use

- **ALWAYS** use before falling back from Redis to grep/find/SQLite
- When `get_adg_runtime_context()` import fails
- When Redis connection fails
- When Redis query returns no results unexpectedly
- When ADG cache appears stale or missing

## Constitutional Basis

From `.windsurfrules` §0 DEFAULT ANALYSIS MODE:
> "NEVER skip ADG — no query, analysis, refactor, or code change begins without verifying ADG cache"

Redis is the PRIMARY ADG source. Bypassing it without user consent violates graph-first discipline.

## Protocol

### Step 1: Detect Redis Failure

```python
import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    meta = r.hgetall('adg:meta')
    if not meta:
        # STOP - Redis empty or ADG not loaded
        redis_available = False
    else:
        redis_available = True
except Exception as e:
    # STOP - Redis connection failed
    redis_available = False
```

### Step 2: HITL Gate - Present Options

When `redis_available == False`, **IMMEDIATELY** call `ask_user_question`:

```python
# DO NOT proceed without user choice
ask_user_question(
    question="ADG Redis cache is unavailable or empty. How should I proceed?",
    options=[
        {
            "label": "Regenerate ADG and reload Redis",
            "description": "Run generate_full_adg.py then adg_redis_ingest.py to rebuild cache (recommended, ~2-3 min)"
        },
        {
            "label": "Use SQLite fallback",
            "description": "Query adg_indexed_*.sqlite directly (slower, use for complex JOIN queries only)"
        },
        {
            "label": "Use filesystem tools",
            "description": "Fall back to grep/find (VIOLATES graph-first mandate, use only if ADG rebuild fails)"
        },
        {
            "label": "Stop and investigate",
            "description": "Halt execution to diagnose why Redis is unavailable"
        }
    ],
    allowMultiple=False
)
```

### Step 3: Execute User Choice

```python
if user_choice == "Regenerate ADG and reload Redis":
    run_command("python C:\\Git\\Agentic-Workflow\\tools\\generate_full_adg.py")
    run_command("python C:\\Git\\Agentic-Workflow\\tools\\adg\\adg_redis_ingest.py --force")
    # Retry Redis query

elif user_choice == "Use SQLite fallback":
    # Query artifacts/adg/adg_indexed_*.sqlite
    # Document why Redis was unavailable in evidence

elif user_choice == "Use filesystem tools":
    # Log constitutional violation
    # Proceed with grep/find
    # Create RCA documenting bypass

elif user_choice == "Stop and investigate":
    # Halt and report status
```

## Import Failure Variant

When import fails (e.g., `get_adg_runtime_context` not found):

```python
ask_user_question(
    question="ADG import failed: 'get_adg_runtime_context' not found. How should I proceed?",
    options=[
        {
            "label": "Use direct Redis connection",
            "description": "Connect to Redis using redis-py directly (recommended)"
        },
        {
            "label": "Check and fix import path",
            "description": "Investigate agentic_core/cache/__init__.py exports"
        },
        {
            "label": "Use SQLite fallback",
            "description": "Query SQLite directly, skip Redis"
        },
        {
            "label": "Use filesystem tools",
            "description": "Fall back to grep/find (violates mandate)"
        }
    ],
    allowMultiple=False
)
```

## Query Returns No Results Variant

When Redis query succeeds but returns 0 results unexpectedly:

```python
ask_user_question(
    question=f"Redis query for '{search_term}' returned 0 results. This may indicate stale cache or wrong query pattern. How should I proceed?",
    options=[
        {
            "label": "Regenerate ADG cache",
            "description": "Cache may be stale, rebuild and retry"
        },
        {
            "label": "Verify query pattern",
            "description": "Show me the Redis query used so I can verify it's correct"
        },
        {
            "label": "Cross-check with filesystem",
            "description": "Use grep to verify files exist, then investigate Redis schema"
        },
        {
            "label": "Proceed with 0 results",
            "description": "Accept that no matching nodes exist"
        }
    ],
    allowMultiple=False
)
```

## Anti-Patterns (FORBIDDEN)

❌ **Silent fallback:**
```python
# WRONG - bypasses mandate without user consent
try:
    results = query_redis(pattern)
except:
    results = grep_search(pattern)  # VIOLATION
```

❌ **Assuming user wants fastest path:**
```python
# WRONG - assumes user prefers speed over correctness
if not redis_available:
    # "I'll just use grep since it's faster"
    return grep_search(pattern)  # VIOLATION
```

❌ **Logging violation after the fact:**
```python
# WRONG - asks for forgiveness instead of permission
results = grep_search(pattern)
log("Note: Used grep because Redis failed")  # VIOLATION
```

## Correct Pattern (REQUIRED)

✅ **HITL gate before any fallback:**
```python
# CORRECT - user decides fallback strategy
try:
    results = query_redis(pattern)
except RedisError:
    user_choice = ask_user_question(...)  # HITL GATE
    if user_choice == "filesystem":
        results = grep_search(pattern)
        create_rca("Redis bypass authorized by user")
```

## Evidence Requirements

When user authorizes non-Redis fallback, document:

1. **Why Redis failed** (connection error, empty cache, import error)
2. **What user chose** (SQLite, filesystem, stop)
3. **Timestamp** of authorization
4. **Query that would have been used** if Redis worked

Save to: `docs/reports/plans/Redis_Fallback_Authorization_<timestamp>.md`

## Success Criteria

- ✅ User explicitly chooses fallback method
- ✅ No silent bypasses of Redis
- ✅ All fallbacks documented with RCA
- ✅ Redis regeneration offered as first option
- ✅ Constitutional violations only occur with user consent

## Related Skills

- `dependency-graph-analysis` - Graph-first analysis with tier-aware enforcement
- `anti-pattern-hitl-gate` - General HITL enforcement framework

## References

- System memory: "ADG Pre-Ingest Rule — ALL Operating Modes"
- `.windsurfrules` §0: DEFAULT ANALYSIS MODE
- RCA: `docs/reports/plans/RCA_ADG_Redis_Bypass.md`
