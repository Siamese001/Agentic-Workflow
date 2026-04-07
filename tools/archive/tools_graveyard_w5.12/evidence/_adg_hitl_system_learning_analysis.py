"""ADG analysis: HITL mixin integration with system_learning confidence infrastructure."""

import subprocess
import sys


def run_query(description, query):
    """Execute ADG SQLite query and return results."""
    print(f"\n{'='*80}")
    print(f"QUERY: {description}")
    print(f"{'='*80}")

    cmd = [
        sys.executable,
        "tools/adg/adg_redis_query.py",
        "--sqlite",
        "artifacts/adg/adg_indexed_03132026_1949.sqlite",
        "--query",
        query,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"ERROR: {result.stderr}")

    return result.stdout

# Query 1: Find all modules importing HITLMixin
q1 = """
SELECT DISTINCT src.adg_name, src.layer, src.resolved_path
FROM edges e
JOIN nodes src ON e.src_id = src.id
JOIN nodes dst ON e.dst_id = dst.id
WHERE dst.adg_name LIKE '%HITLMixin%'
AND e.relation_type = 'imports'
ORDER BY src.layer, src.adg_name
"""

# Query 2: Find system_learning confidence/scoring infrastructure
q2 = """
SELECT adg_name, layer, entity_type, resolved_path
FROM nodes
WHERE layer = 'L_SL'
AND entity_type = 'class'
AND (
    adg_name LIKE '%Confidence%'
    OR adg_name LIKE '%Scorer%'
    OR adg_name LIKE '%Score%'
)
ORDER BY adg_name
"""

# Query 3: Find system_learning adapter patterns
q3 = """
SELECT adg_name, layer, entity_type, resolved_path
FROM nodes
WHERE layer = 'L_SL'
AND entity_type = 'class'
AND adg_name LIKE '%Adapter%'
ORDER BY adg_name
"""

# Query 4: Find system_learning proposer patterns
q4 = """
SELECT adg_name, layer, entity_type, resolved_path
FROM nodes
WHERE layer = 'L_SL'
AND entity_type = 'class'
AND adg_name LIKE '%Proposer%'
ORDER BY adg_name
"""

# Query 5: Find existing HITL-to-system_learning connections
q5 = """
SELECT DISTINCT src.adg_name AS hitl_module, dst.adg_name AS sl_module, e.relation_type
FROM edges e
JOIN nodes src ON e.src_id = src.id
JOIN nodes dst ON e.dst_id = dst.id
WHERE (src.resolved_path LIKE '%hitl%' OR src.adg_name LIKE '%HITL%')
AND dst.layer = 'L_SL'
ORDER BY dst.adg_name
"""

# Query 6: Find ApprovalRequest and related types
q6 = """
SELECT adg_name, entity_type, resolved_path
FROM nodes
WHERE adg_name LIKE '%Approval%'
OR adg_name LIKE '%RiskLevel%'
ORDER BY adg_name
"""

# Query 7: Find system_learning outcome/feedback patterns
q7 = """
SELECT adg_name, layer, entity_type, resolved_path
FROM nodes
WHERE layer = 'L_SL'
AND entity_type = 'class'
AND (
    adg_name LIKE '%Outcome%'
    OR adg_name LIKE '%Feedback%'
    OR adg_name LIKE '%Attempt%'
)
ORDER BY adg_name
"""

if __name__ == "__main__":
    print("ADG ANALYSIS: HITL Mixin + System Learning Confidence Integration")
    print("="*80)

    run_query("1. Modules importing HITLMixin", q1)
    run_query("2. System Learning Confidence/Scoring Classes", q2)
    run_query("3. System Learning Adapter Patterns", q3)
    run_query("4. System Learning Proposer Patterns", q4)
    run_query("5. Existing HITL → System Learning Connections", q5)
    run_query("6. HITL Approval/Risk Types", q6)
    run_query("7. System Learning Outcome/Feedback Patterns", q7)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
