import json
import sqlite3

db = r"c:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03162026_0908.sqlite"
q = """
WITH calls_by_file AS (
  SELECT source_file, COUNT(*) AS call_edges
  FROM edges
  WHERE relation_type = 'calls'
  GROUP BY source_file
),
dig_by_file AS (
  SELECT DISTINCT source_file
  FROM edges
  WHERE relation_type = 'emits_determinism_digest'
),
replay_by_file AS (
  SELECT DISTINCT source_file
  FROM edges
  WHERE relation_type = 'emits_replay_key'
),
runtime_by_file AS (
  SELECT DISTINCT source_file
  FROM edges
  WHERE relation_type = 'reads_runtime_state'
),
env_by_file AS (
  SELECT DISTINCT source_file
  FROM edges
  WHERE relation_type = 'reads_env'
)
SELECT
  c.source_file,
  c.call_edges,
  CASE WHEN d.source_file IS NULL THEN 1 ELSE 0 END AS missing_digest,
  CASE WHEN r.source_file IS NULL THEN 1 ELSE 0 END AS missing_replay,
  CASE WHEN rs.source_file IS NULL THEN 1 ELSE 0 END AS missing_runtime,
  CASE WHEN ev.source_file IS NULL THEN 1 ELSE 0 END AS missing_env
FROM calls_by_file c
LEFT JOIN dig_by_file d ON d.source_file = c.source_file
LEFT JOIN replay_by_file r ON r.source_file = c.source_file
LEFT JOIN runtime_by_file rs ON rs.source_file = c.source_file
LEFT JOIN env_by_file ev ON ev.source_file = c.source_file
WHERE d.source_file IS NULL
ORDER BY c.call_edges DESC
LIMIT 15;
"""
with sqlite3.connect(db) as con:
    rows = con.execute(q).fetchall()
print(json.dumps(rows, indent=2))
