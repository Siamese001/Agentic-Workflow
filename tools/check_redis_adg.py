#!/usr/bin/env python3
"""Check Redis ADG status."""

import sys
sys.path.append('C:/Git/Agentic-Workflow/tools/adg')
from adg_redis_query import check_adg_status

status = check_adg_status()
print('=== REDIS ADG STATUS ===')
print('Is Fresh: ' + str(status['is_fresh']))
print('Timestamp: ' + str(status['timestamp']))
print('Node Count: ' + str(status['node_count']))
print('Edge Count: ' + str(status['edge_count']))
print('Ingested At: ' + str(status['ingested_at']))
print('Age (seconds): ' + str(status['age_seconds']))
print('Verdict: ' + str(status['verdict']))
