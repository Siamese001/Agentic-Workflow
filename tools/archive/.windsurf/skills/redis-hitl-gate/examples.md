# Redis HITL Gate - Examples

## Example 1: Redis Connection Failed

```python
import redis

def find_dashboard_files_with_hitl():
    """Find dashboard files using ADG Redis with HITL fallback."""

    # Step 1: Attempt Redis connection
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        meta = r.hgetall('adg:meta')

        if not meta:
            redis_status = "empty"
        else:
            redis_status = "available"

    except redis.ConnectionError:
        redis_status = "connection_failed"
    except Exception as e:
        redis_status = f"error: {e}"

    # Step 2: HITL Gate if Redis unavailable
    if redis_status != "available":
        from cascade_tools import ask_user_question

        user_choice = ask_user_question(
            question=f"ADG Redis cache status: {redis_status}. How should I proceed with finding dashboard files?",
            options=[
                {
                    "label": "Regenerate ADG and reload Redis",
                    "description": "Run generate_full_adg.py then adg_redis_ingest.py (~2-3 min)"
                },
                {
                    "label": "Use SQLite fallback",
                    "description": "Query adg_indexed_*.sqlite directly"
                },
                {
                    "label": "Use filesystem grep",
                    "description": "Fall back to grep_search (violates graph-first mandate)"
                },
                {
                    "label": "Stop and investigate",
                    "description": "Halt to diagnose Redis issue"
                }
            ],
            allowMultiple=False
        )

        # Step 3: Execute user choice
        if user_choice == "Regenerate ADG and reload Redis":
            print("Regenerating ADG...")
            run_command("python C:\\Git\\Agentic-Workflow\\tools\\generate_full_adg.py")
            run_command("python C:\\Git\\Agentic-Workflow\\tools\\adg\\adg_redis_ingest.py --force")

            # Retry Redis
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            return query_redis_for_dashboard_files(r)

        elif user_choice == "Use SQLite fallback":
            return query_sqlite_for_dashboard_files()

        elif user_choice == "Use filesystem grep":
            create_rca("Redis_Fallback_Filesystem_Authorized")
            return grep_search_for_dashboard_files()

        else:  # Stop and investigate
            raise Exception(f"Redis unavailable: {redis_status}. User chose to investigate.")

    # Step 4: Redis available - proceed normally
    return query_redis_for_dashboard_files(r)


def query_redis_for_dashboard_files(r):
    """Query Redis for nodes with 'dashboard' in path."""
    dashboard_files = []
    cursor = 0

    while True:
        cursor, keys = r.scan(cursor, match='adg:node:*', count=100)
        for key in keys:
            node_data = r.hgetall(key)
            resolved_path = node_data.get('resolved_path', '')
            if 'dashboard' in resolved_path.lower():
                dashboard_files.append({
                    'path': resolved_path,
                    'node_id': node_data.get('id'),
                    'layer': node_data.get('layer'),
                    'entity_type': node_data.get('entity_type')
                })

        if cursor == 0:
            break

    return dashboard_files
```

## Example 2: Import Failed

```python
def get_adg_context_with_hitl():
    """Get ADG context with HITL when import fails."""

    # Step 1: Attempt import
    try:
        from agentic_core.cache import get_adg_runtime_context
        ctx = get_adg_runtime_context()
        return ctx
    except ImportError as e:
        # Step 2: HITL Gate
        from cascade_tools import ask_user_question

        user_choice = ask_user_question(
            question=f"ADG import failed: {e}. How should I proceed?",
            options=[
                {
                    "label": "Use direct Redis connection",
                    "description": "Connect using redis.Redis() directly (recommended)"
                },
                {
                    "label": "Check import path",
                    "description": "Investigate agentic_core/cache/__init__.py exports first"
                },
                {
                    "label": "Use SQLite fallback",
                    "description": "Skip Redis, query SQLite directly"
                }
            ],
            allowMultiple=False
        )

        # Step 3: Execute choice
        if user_choice == "Use direct Redis connection":
            import redis
            return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        elif user_choice == "Check import path":
            # Read and display cache/__init__.py
            with open('agentic_core/cache/__init__.py') as f:
                print(f.read())
            raise Exception("Please verify correct import path and retry")

        else:  # SQLite fallback
            return None  # Signal to use SQLite
```

## Example 3: Query Returns No Results

```python
def find_nodes_with_hitl(search_term):
    """Find nodes with HITL when unexpected empty results."""

    import redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Query Redis
    results = []
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor, match='adg:node:*', count=100)
        for key in keys:
            node_data = r.hgetall(key)
            if search_term.lower() in node_data.get('adg_name', '').lower():
                results.append(node_data)
        if cursor == 0:
            break

    # HITL Gate if no results
    if len(results) == 0:
        from cascade_tools import ask_user_question

        user_choice = ask_user_question(
            question=f"Redis query for '{search_term}' returned 0 results. How should I proceed?",
            options=[
                {
                    "label": "Regenerate ADG cache",
                    "description": "Cache may be stale, rebuild and retry"
                },
                {
                    "label": "Show query pattern",
                    "description": "Display the Redis query used for verification"
                },
                {
                    "label": "Cross-check filesystem",
                    "description": "Use grep to verify files exist"
                },
                {
                    "label": "Accept 0 results",
                    "description": "Proceed assuming no matches exist"
                }
            ],
            allowMultiple=False
        )

        if user_choice == "Regenerate ADG cache":
            run_command("python tools/generate_full_adg.py")
            run_command("python tools/adg/adg_redis_ingest.py --force")
            return find_nodes_with_hitl(search_term)  # Retry

        elif user_choice == "Show query pattern":
            print(f"Query: SCAN match='adg:node:*', filter by '{search_term}' in adg_name")
            print(f"Total keys scanned: {r.dbsize()}")
            raise Exception("Please verify query pattern and retry")

        elif user_choice == "Cross-check filesystem":
            # Use grep to verify
            grep_results = grep_search(search_term)
            print(f"Filesystem found {len(grep_results)} matches")
            print("This suggests Redis cache is stale or query pattern is wrong")
            raise Exception("Redis/filesystem mismatch - investigate")

        else:  # Accept 0 results
            return []

    return results
```

## Example 4: Complete Workflow with Evidence

```python
def adg_query_with_full_hitl_and_evidence(search_pattern):
    """Complete ADG query with HITL and evidence generation."""

    import redis
    import json
    from datetime import datetime

    evidence = {
        "timestamp": datetime.now().isoformat(),
        "search_pattern": search_pattern,
        "redis_status": None,
        "user_choice": None,
        "results_count": 0,
        "fallback_used": False
    }

    # Step 1: Check Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        meta = r.hgetall('adg:meta')

        if meta:
            evidence["redis_status"] = "available"
            evidence["adg_timestamp"] = meta.get('timestamp')
            redis_ok = True
        else:
            evidence["redis_status"] = "empty_cache"
            redis_ok = False

    except Exception as e:
        evidence["redis_status"] = f"error: {str(e)}"
        redis_ok = False

    # Step 2: HITL if needed
    if not redis_ok:
        from cascade_tools import ask_user_question

        user_choice = ask_user_question(
            question=f"Redis status: {evidence['redis_status']}. Choose fallback:",
            options=[
                {"label": "Regenerate ADG", "description": "Rebuild cache"},
                {"label": "SQLite", "description": "Query SQLite"},
                {"label": "Filesystem", "description": "Use grep (violates mandate)"},
                {"label": "Stop", "description": "Investigate issue"}
            ],
            allowMultiple=False
        )

        evidence["user_choice"] = user_choice
        evidence["fallback_used"] = True

        if user_choice == "Regenerate ADG":
            run_command("python tools/generate_full_adg.py")
            run_command("python tools/adg/adg_redis_ingest.py --force")
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            results = query_redis(r, search_pattern)

        elif user_choice == "SQLite":
            results = query_sqlite(search_pattern)

        elif user_choice == "Filesystem":
            results = grep_search(search_pattern)
            create_rca_for_redis_bypass(evidence)

        else:  # Stop
            save_evidence(evidence)
            raise Exception("User chose to stop and investigate Redis issue")
    else:
        # Redis OK - proceed
        results = query_redis(r, search_pattern)

    # Step 3: Save evidence
    evidence["results_count"] = len(results)
    save_evidence(evidence)

    return results


def save_evidence(evidence):
    """Save evidence to file."""
    timestamp = evidence['timestamp'].replace(':', '-')
    filename = f"docs/reports/plans/ADG_Query_Evidence_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(evidence, f, indent=2)
    print(f"Evidence saved: {filename}")
```

## Key Takeaways

1. **Always check Redis first** - Never skip to fallback
2. **Always ask user** - Never assume fallback preference
3. **Always document** - Create evidence/RCA when bypassing Redis
4. **Always offer regeneration** - Make it the first option
5. **Never silent fallback** - User must explicitly authorize
