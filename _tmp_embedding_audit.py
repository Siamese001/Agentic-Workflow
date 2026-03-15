import sqlite3

db = r'C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03152026_0344.sqlite'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Find embedding-related nodes
cur.execute("""
    SELECT adg_name, entity_type, layer FROM nodes
    WHERE adg_name LIKE '%embed%' OR adg_name LIKE '%Embed%'
    LIMIT 30
""")
print('--- Embedding nodes ---')
for r in cur.fetchall():
    print(r)

# Find stores_embedding edges
cur.execute("""
    SELECT n1.adg_name, n2.adg_name FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'stores_embedding'
    LIMIT 20
""")
print('\n--- stores_embedding edges ---')
for r in cur.fetchall():
    print(r)

# Find retrieves_via edges
cur.execute("""
    SELECT n1.adg_name, n2.adg_name FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'retrieves_via'
    LIMIT 20
""")
print('\n--- retrieves_via edges ---')
for r in cur.fetchall():
    print(r)

# L0 routing - what does it export
cur.execute("""
    SELECT n1.adg_name, e.symbol FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    WHERE e.relation_type = 'exports'
    AND n1.adg_name LIKE '%L0_routing%'
    AND (e.symbol LIKE '%route%' OR e.symbol LIKE '%Route%' OR e.symbol LIKE '%capacity%')
    AND n1.adg_name NOT LIKE '%test%'
    LIMIT 20
""")
print('\n--- L0 routing exports ---')
for r in cur.fetchall():
    print(r)

# L1 cognition - what are its key functions
cur.execute("""
    SELECT n1.adg_name, e.symbol FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    WHERE e.relation_type = 'exports'
    AND n1.adg_name LIKE '%L1_cognition%'
    AND n1.adg_name NOT LIKE '%test%'
    LIMIT 25
""")
print('\n--- L1 cognition exports ---')
for r in cur.fetchall():
    print(r)

# L3 orchestration - agent dispatch
cur.execute("""
    SELECT n1.adg_name, e.symbol FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    WHERE e.relation_type = 'exports'
    AND n1.adg_name LIKE '%L3_orchestration%'
    AND n1.adg_name NOT LIKE '%test%'
    LIMIT 25
""")
print('\n--- L3 orchestration exports ---')
for r in cur.fetchall():
    print(r)

# system_learning - what layer + what does it export
cur.execute("""
    SELECT n1.adg_name, n1.layer, e.symbol FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    WHERE e.relation_type = 'exports'
    AND n1.adg_name LIKE '%system_learning%'
    AND n1.adg_name NOT LIKE '%test%'
    LIMIT 30
""")
print('\n--- system_learning exports ---')
for r in cur.fetchall():
    print(r)

# L4 state/persistence - semantic cache
cur.execute("""
    SELECT n1.adg_name, e.symbol FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    WHERE e.relation_type = 'exports'
    AND (n1.adg_name LIKE '%L4_state%' OR n1.adg_name LIKE '%L4_persistence%')
    AND (e.symbol LIKE '%cache%' OR e.symbol LIKE '%Cache%' OR e.symbol LIKE '%memory%' OR e.symbol LIKE '%Memory%')
    AND n1.adg_name NOT LIKE '%test%'
    LIMIT 20
""")
print('\n--- L4 state memory/cache exports ---')
for r in cur.fetchall():
    print(r)

# agent_executes_agent - what dispatches to what
cur.execute("""
    SELECT n1.adg_name, n2.adg_name FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'agent_executes_agent'
    AND n1.adg_name NOT LIKE '%test%'
    LIMIT 20
""")
print('\n--- agent_executes_agent edges ---')
for r in cur.fetchall():
    print(r)

conn.close()
