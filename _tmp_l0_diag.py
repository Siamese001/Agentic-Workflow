"""Diagnose P1/L0 gate failures."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

print("=== proposal_commits_routing in L0_routing ===")
c.execute(
    "SELECT source_file, symbol, line_no FROM edges "
    "WHERE relation_type='proposal_commits_routing' "
    "AND source_file LIKE '%L0_routing%'"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== proposal_commits_routing non-test (all) ===")
c.execute(
    "SELECT source_file, symbol FROM edges "
    "WHERE relation_type='proposal_commits_routing' "
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%'"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== routing_contract nodes ===")
c.execute("SELECT id, adg_name, layer FROM nodes WHERE adg_name LIKE '%routing_contract%'")
for r in c.fetchall():
    print(" ", r)

print("\n=== imports -> routing_contract (non-test) ===")
c.execute(
    "SELECT e.source_file, n.adg_name "
    "FROM edges e JOIN nodes n ON n.id=e.dst_id "
    "WHERE e.relation_type='imports' "
    "AND n.adg_name LIKE '%routing_contract%' "
    "AND e.source_file NOT LIKE '%test%'"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== routes_path non-test sources ===")
c.execute(
    "SELECT source_file, symbol FROM edges "
    "WHERE relation_type='routes_path' "
    "AND source_file NOT LIKE '%test%' "
    "AND source_file NOT LIKE '%tests%'"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== ADG scanner: what symbols trigger proposal_commits_routing? ===")
print("  ROUTING_COMMIT_SYMBOLS from schema.py:")
print(
    "  RoutingProposal, commit_proposal, ProposalCommitter, commit_routing_update, apply_routing_proposal, etc."
)

print("\n=== routing_contract.py symbols in edges ===")
c.execute("SELECT relation_type, symbol, line_no FROM edges WHERE source_file LIKE '%routing_contract%'")
for r in c.fetchall():
    print(" ", r)

conn.close()
