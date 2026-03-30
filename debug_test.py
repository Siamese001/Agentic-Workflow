#!/usr/bin/env python3
"""Debug script to trace test database setup"""
import tempfile
from pathlib import Path
import sys
import shutil
import sqlite3

sys.path.insert(0, 'c:/Git/Agentic-Workflow')

# Simulate what the test does
with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    
    # Create a small test database like the factory does
    db_path = tmp_path / 'test_adg.sqlite'
    conn = sqlite3.connect(db_path)
    conn.execute('CREATE TABLE nodes (id INTEGER PRIMARY KEY)')
    conn.execute('CREATE TABLE edges (id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()
    
    # Now simulate adg_dir_with behavior
    adg_dir = tmp_path / 'adg_artifacts'
    adg_dir.mkdir(exist_ok=True)
    dest = adg_dir / db_path.name
    shutil.copy2(db_path, dest)
    
    print(f'Test DB copied to: {dest}')
    print(f'Dest exists: {dest.exists()}')
    files = list(adg_dir.glob('*.sqlite'))
    print(f'Files in adg_dir: {files}')
    
    # Now check what BehavioralCoverageReporter finds
    from scripts.report_behavioral_coverage_ratios import BehavioralCoverageReporter
    reporter = BehavioralCoverageReporter(adg_dir)
    print(f'Reporter db_path: {reporter.db_path}')
    print(f'Reporter db exists: {reporter.db_path.exists() if reporter.db_path else None}')
    
    # Try to run the method (no timeout on Windows)
    try:
        result = reporter._calculate_balance_metrics()
        print(f'Result: {result}')
    except Exception as e:
        import traceback
        print(f'ERROR: {type(e).__name__}: {e}')
        traceback.print_exc()
