#!/usr/bin/env python3
"""Test dashboard with continuous live data generation"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add apps_shared to path
sys.path.insert(0, str(Path(__file__).parent / "apps_shared"))

from canon_dashboard import DashboardMetrics, CanonDashboard
from canon_dashboard_web import app, run_server
import canon_dashboard_web as web_module
import threading

# Initialize dashboard
metrics = DashboardMetrics()
web_module.metrics = metrics

# Start web server
web_thread = threading.Thread(
    target=run_server,
    args=('0.0.0.0', 5000, False),
    daemon=True
)
web_thread.start()

print("🌐 Dashboard running at http://localhost:5000")
print("⏳ Waiting 3 seconds for server to be ready...")
time.sleep(3)

print("📊 Starting session and generating live data...\n")

# Start session
metrics.start_session("agentic_core", 50)

# Simulate continuous file processing
test_files = [
    ("action_node.py", 40, 5),
    ("canon_agents_core.py", 41, 12),
    ("cognitive_node.py", 42, 3),
    ("consensus_engine.py", 40, 2),
    ("agent_logic_connectivity.py", 41, 8),
    ("canon_orchestrator.py", 40, 6),
    ("subatomic_engine.py", 41, 15),
    ("validation_context.py", 42, 4),
    ("memory_manager.py", 40, 7),
    ("blackboard.py", 41, 20),
    ("safety_guardrail.py", 40, 3),
    ("void_compliance.py", 41, 9),
    ("fission_manager.py", 42, 5),
    ("healing_engine.py", 40, 11),
    ("pattern_matcher.py", 41, 6),
]

print("🔄 Processing files continuously...")
print("=" * 60)

for i, (filename, key_id, violation_count) in enumerate(test_files, 1):
    print(f"[{i}/50] Processing {filename}...")
    
    # Update current file
    metrics.session.current_file = f"agentic_core/{filename}"
    
    # Record violations
    metrics.record_violation(f"agentic_core/{filename}", key_id, violation_count)
    print(f"  ❌ Found {violation_count} violations (Key {key_id})")
    
    # Simulate healing time
    time.sleep(0.5)
    
    # Record healing with varying durations
    healed_count = max(1, violation_count - 1)
    duration = 1.5 + (violation_count * 0.3)
    metrics.record_healing(f"agentic_core/{filename}", key_id, healed_count, duration)
    print(f"  ✅ Healed {healed_count}/{violation_count} violations in {duration:.1f}s")
    
    # Update progress
    status = "passed" if violation_count < 10 else "failed"
    metrics.update_file_progress(f"agentic_core/{filename}", status)
    print(f"  📊 Status: {status.upper()}")
    print()
    
    # Pause between files to simulate real processing
    time.sleep(1)

# Continue with remaining files (simulated)
print("🔄 Continuing with remaining files...")
for i in range(16, 51):
    filename = f"file_{i}.py"
    key_id = 40 + (i % 10)
    violation_count = (i % 15) + 1
    
    print(f"[{i}/50] Processing {filename}...")
    metrics.session.current_file = f"agentic_core/{filename}"
    
    metrics.record_violation(f"agentic_core/{filename}", key_id, violation_count)
    time.sleep(0.3)
    
    healed_count = max(1, violation_count - 1)
    duration = 1.0 + (violation_count * 0.2)
    metrics.record_healing(f"agentic_core/{filename}", key_id, healed_count, duration)
    
    status = "passed" if violation_count < 10 else "failed"
    metrics.update_file_progress(f"agentic_core/{filename}", status)
    
    time.sleep(0.5)

# Complete session
metrics.session.status = "completed"

print("\n" + "=" * 60)
print("✅ Validation complete!")
print(f"📊 Total violations: {metrics.session.total_violations}")
print(f"🏥 Total healed: {metrics.session.total_healed}")
print(f"📈 Files processed: {metrics.session.files_processed}/{metrics.session.total_files}")
print(f"✨ Success rate: {(metrics.session.total_healed / metrics.session.total_violations * 100):.1f}%")
print(f"\n🌐 Dashboard: http://localhost:5000")
print("Press Ctrl+C to exit...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Shutting down...")
