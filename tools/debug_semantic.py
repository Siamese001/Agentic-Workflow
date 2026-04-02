# Debug why the fallback isn't working
import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03272026_2022.sqlite')

# Check reads_runtime_state edges
print('=== reads_runtime_state ===')
cursor = conn.execute('SELECT edge_kind, relation_type, semantic_type FROM edges WHERE edge_kind = "reads_runtime_state" LIMIT 5')
samples = cursor.fetchall()
for edge_kind, rel_type, sem_type in samples:
    print(f'  edge_kind: {edge_kind}, relation_type: {rel_type}, semantic_type: {sem_type}')

print('\n=== reads_policy_state ===')
cursor = conn.execute('SELECT edge_kind, relation_type, semantic_type FROM edges WHERE edge_kind = "reads_policy_state" LIMIT 5')
samples = cursor.fetchall()
for edge_kind, rel_type, sem_type in samples:
    print(f'  edge_kind: {edge_kind}, relation_type: {rel_type}, semantic_type: {sem_type}')

print('\n=== layer_membership ===')
cursor = conn.execute('SELECT edge_kind, relation_type, semantic_type FROM edges WHERE edge_kind = "layer_membership" LIMIT 5')
samples = cursor.fetchall()
for edge_kind, rel_type, sem_type in samples:
    print(f'  edge_kind: {edge_kind}, relation_type: {rel_type}, semantic_type: {sem_type}')

# Check if our fallback map should have caught these
print('\n=== Expected behavior ===')
print('reads_runtime_state edges should use relation_type "reads_runtime_state" fallback')
print('reads_policy_state edges should use relation_type "reads_policy_state" fallback')
print('layer_membership edges should use relation_type "belongs_to_layer" fallback')

conn.close()
