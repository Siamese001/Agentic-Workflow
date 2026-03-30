#!/usr/bin/env python3
"""Debug script to test _verify_l4_path_integrity"""
import tempfile
from pathlib import Path
import sqlite3

# Create a test database
with tempfile.TemporaryDirectory() as tmp:
    db_path = Path(tmp) / 'test.sqlite'
    conn = sqlite3.connect(db_path)
    conn.execute('CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT, entity_type TEXT, layer TEXT, identity_kind TEXT, confidence TEXT, resolved_path TEXT)')
    conn.execute("INSERT INTO nodes VALUES (1, 'ADG::Module::test.py', 'module', 'L4', 'repo_module', 'HIGH', 'agentic_core/L4/test.py')")
    conn.commit()
    conn.close()
    
    # Now test the verifier
    from scripts.verify_l4_normalization import ADGL4NormalizationVerifier
    verifier = ADGL4NormalizationVerifier(Path(tmp))
    result = verifier._verify_l4_path_integrity()
    print(f'Result type: {type(result)}')
    print(f'Result: {result}')
    print(f'Has l4_nodes: {"l4_nodes" in result if isinstance(result, dict) else "N/A - not a dict"}')
