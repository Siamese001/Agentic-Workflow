#!/usr/bin/env python3
"""
P0 gap validation: L1-L6 against ADG SQLite.
"""
import sqlite3, os

adg_dir = r'artifacts\adg'
sqls = sorted([f for f in os.listdir(adg_dir) if f.endswith('.sqlite')], reverse=True)
db = os.path.join(adg_dir, sqls[0])
print(f'SQLite: {db}\n')

conn = sqlite3.connect(db)
c = conn.cursor()

def edge_count(et):
    c.execute('SELECT COUNT(*) FROM edges WHERE relation_type=?', (et,))
    return c.fetchone()[0]

def by_source_file(et, limit=12):
    c.execute('SELECT source_file, COUNT(*) as cnt FROM edges WHERE relation_type=? GROUP BY source_file ORDER BY cnt DESC LIMIT ?', (et, limit))
    return c.fetchall()

def by_layer(et):
    c.execute('''
        SELECT n.layer, COUNT(e.id) as cnt
        FROM nodes n JOIN edges e ON n.id = e.src_id
        WHERE e.relation_type = ?
        GROUP BY n.layer ORDER BY cnt DESC
    ''', (et,))
    return c.fetchall()

def prod_vs_test(et):
    c.execute('''
        SELECT
            SUM(CASE WHEN n.layer = 'L_TEST' THEN 1 ELSE 0 END) as test_cnt,
            SUM(CASE WHEN n.layer != 'L_TEST' THEN 1 ELSE 0 END) as prod_cnt
        FROM nodes n JOIN edges e ON n.id = e.src_id
        WHERE e.relation_type = ?
    ''', (et,))
    r = c.fetchone()
    return r[0] or 0, r[1] or 0

def nodes_in_layer_with_edge(layer, et):
    c.execute('''
        SELECT n.resolved_path, COUNT(e.id) as cnt
        FROM nodes n JOIN edges e ON n.id = e.src_id
        WHERE n.layer = ? AND e.relation_type = ?
        GROUP BY n.id ORDER BY cnt DESC LIMIT 10
    ''', (layer, et))
    return c.fetchall()

# ─── P0/L1: Reasoning trace coverage ──────────────────────────────────────────
print('=' * 70)
print('P0/L1: Reasoning trace coverage')
print('  ChatGPT claim: records_execution_trace=72, calls=20481 (0.35%)')
rct = edge_count('records_execution_trace')
calls = edge_count('calls')
print(f'  ADG actual:    records_execution_trace={rct}, calls={calls} ({rct/calls*100:.2f}% if calls>0)')
rct_test, rct_prod = prod_vs_test('records_execution_trace')
print(f'  Distribution:  test={rct_test}, prod={rct_prod}')
print('  records_execution_trace by source_file:')
for r in by_source_file('records_execution_trace', 10):
    print(f'    {r[1]:3d}  {r[0]}')
print('  Layer breakdown:')
for r in by_layer('records_execution_trace'):
    print(f'    {r[0]:12}  {r[1]}')

# ─── P0/L2: Guardrail enforcement ─────────────────────────────────────────────
print()
print('=' * 70)
print('P0/L2: Guardrail enforcement before execution')
print('  ChatGPT claim: applies_guardrail=612, calls=20481 (~3%)')
ag = edge_count('applies_guardrail')
print(f'  ADG actual:    applies_guardrail={ag}, calls={calls} ({ag/calls*100:.2f}%)')
ag_test, ag_prod = prod_vs_test('applies_guardrail')
print(f'  Distribution:  test={ag_test}, prod={ag_prod}')
print('  applies_guardrail by source_file:')
for r in by_source_file('applies_guardrail', 15):
    print(f'    {r[1]:3d}  {r[0]}')
print('  Layer breakdown:')
for r in by_layer('applies_guardrail'):
    print(f'    {r[0]:12}  {r[1]}')

# Also: fail-closed edges
for et in ['hard_fails_untranscripted', 'reenters_safety', 'validated_by_safety_plane']:
    n = edge_count(et)
    print(f'  {et}: {n}')

# ─── P0/L3: Agent orchestration topology ──────────────────────────────────────
print()
print('=' * 70)
print('P0/L3: Agent orchestration topology visibility')
print('  ChatGPT claim: agent_executes_agent=2')
aea = edge_count('agent_executes_agent')
print(f'  ADG actual:    agent_executes_agent={aea}')
print('  agent_executes_agent by source_file:')
for r in by_source_file('agent_executes_agent'):
    print(f'    {r[1]:3d}  {r[0]}')

# Related orchestration signals
for et in ['orchestrates_healing', 'dispatches_healing_run', 'issues_capability_token',
           'validated_by_registry', 'invokes_getattr_dynamic', 'invokes_dynamic']:
    n = edge_count(et)
    nt, np = prod_vs_test(et)
    print(f'  {et}: {n}  (test={nt}, prod={np})')

# L3 nodes specifically
print('  L3 nodes with agent_executes_agent:')
for r in nodes_in_layer_with_edge('L3', 'agent_executes_agent'):
    print(f'    {r[1]:3d}  {r[0]}')
print('  L3 nodes with invokes_getattr_dynamic (implicit dispatch):')
for r in nodes_in_layer_with_edge('L3', 'invokes_getattr_dynamic'):
    print(f'    {r[1]:3d}  {r[0]}')

# ─── P0/L4: Unified runtime state authority ────────────────────────────────────
print()
print('=' * 70)
print('P0/L4: Unified runtime state authority')
print('  ChatGPT claim: reads_runtime_state=469, snapshots_state=1')
rrs = edge_count('reads_runtime_state')
ss = edge_count('snapshots_state')
obs = edge_count('observes_runtime_state')
print(f'  ADG actual:    reads_runtime_state={rrs}, snapshots_state={ss}, observes_runtime_state={obs}')
rrs_test, rrs_prod = prod_vs_test('reads_runtime_state')
print(f'  reads_runtime_state distribution: test={rrs_test}, prod={rrs_prod}')
print('  reads_runtime_state by source_file (top 10):')
for r in by_source_file('reads_runtime_state', 10):
    print(f'    {r[1]:3d}  {r[0]}')
print('  snapshots_state by source_file:')
for r in by_source_file('snapshots_state'):
    print(f'    {r[1]:3d}  {r[0]}')

# NOTE: reads_runtime_state hits RuntimeError too — check symbol targets
c.execute('''
    SELECT e.symbol, COUNT(*) as cnt
    FROM edges e
    WHERE e.relation_type = 'reads_runtime_state'
    GROUP BY e.symbol ORDER BY cnt DESC LIMIT 15
''')
print('  reads_runtime_state target symbols (to detect false positives):')
for r in c.fetchall():
    print(f'    {r[1]:3d}  {r[0]}')

# L4 layer nodes with runtime state edges
print('  L4 nodes with reads_runtime_state:')
for r in nodes_in_layer_with_edge('L4', 'reads_runtime_state'):
    print(f'    {r[1]:3d}  {r[0]}')

# ─── P0/L5: Policy enforcement coverage ───────────────────────────────────────
print()
print('=' * 70)
print('P0/L5: Policy enforcement coverage')
print('  ChatGPT claim: reads_policy_state=1328, applies_guardrail=612')
rps = edge_count('reads_policy_state')
print(f'  ADG actual:    reads_policy_state={rps}, applies_guardrail={ag}')
print(f'  Enforcement ratio: {ag}/{rps} = {ag/rps*100:.1f}% of policy reads result in guardrail')
rps_test, rps_prod = prod_vs_test('reads_policy_state')
print(f'  reads_policy_state distribution: test={rps_test}, prod={rps_prod}')
print('  reads_policy_state by source_file (top 10):')
for r in by_source_file('reads_policy_state', 10):
    print(f'    {r[1]:3d}  {r[0]}')
print('  Layer breakdown for reads_policy_state:')
for r in by_layer('reads_policy_state'):
    print(f'    {r[0]:12}  {r[1]}')

# L5 nodes specifically
print('  L5 nodes with applies_guardrail:')
for r in nodes_in_layer_with_edge('L5', 'applies_guardrail'):
    print(f'    {r[1]:3d}  {r[0]}')
print('  L5 nodes with reads_policy_state (top 8):')
for r in nodes_in_layer_with_edge('L5', 'reads_policy_state'):
    print(f'    {r[1]:3d}  {r[0]}')

# ─── P0/L6: Cross-layer trace completeness ─────────────────────────────────────
print()
print('=' * 70)
print('P0/L6: Cross-layer trace completeness')
print('  ChatGPT claim: records_execution_trace=72, signs_execution_trace=24')
set_count = edge_count('signs_execution_trace')
print(f'  ADG actual:    records_execution_trace={rct}, signs_execution_trace={set_count}')
set_test, set_prod = prod_vs_test('signs_execution_trace')
print(f'  signs_execution_trace distribution: test={set_test}, prod={set_prod}')
print('  signs_execution_trace by source_file:')
for r in by_source_file('signs_execution_trace'):
    print(f'    {r[1]:3d}  {r[0]}')
print('  Layer breakdown for signs_execution_trace:')
for r in by_layer('signs_execution_trace'):
    print(f'    {r[0]:12}  {r[1]}')
print('  L6 nodes with records_execution_trace:')
for r in nodes_in_layer_with_edge('L6', 'records_execution_trace'):
    print(f'    {r[1]:3d}  {r[0]}')
print('  L6 nodes with signs_execution_trace:')
for r in nodes_in_layer_with_edge('L6', 'signs_execution_trace'):
    print(f'    {r[1]:3d}  {r[0]}')

# Cross-layer coverage: any layer pair that should have trace but doesn't
c.execute('''
    SELECT n.layer, COUNT(DISTINCT n.id) as total,
           SUM(CASE WHEN EXISTS(
               SELECT 1 FROM edges e WHERE e.src_id=n.id AND e.relation_type='records_execution_trace'
           ) THEN 1 ELSE 0 END) as with_trace
    FROM nodes n
    WHERE n.layer NOT LIKE '%UNKNOWN%'
    GROUP BY n.layer ORDER BY n.layer
''')
print('\n  records_execution_trace coverage per layer:')
for r in c.fetchall():
    pct = r[2]/r[1]*100 if r[1] > 0 else 0
    print(f'    {r[0]:12}  {r[2]:4d}/{r[1]:5d} = {pct:5.1f}%')

conn.close()
