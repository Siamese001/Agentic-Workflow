#!/usr/bin/env python3
"""Test dashboard with mock data"""

import sys
import time
from pathlib import Path

# Add apps_shared to path
sys.path.insert(0, str(Path(__file__).parent / "apps_shared"))

import threading

import canon_dashboard_web as web_module
from canon_dashboard import DashboardMetrics
from canon_dashboard_web import run_server

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
print("📊 Generating test data...\n")

# Start session
metrics.start_session("test_directory", 10)

# Simulate file processing with violations and healing
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
]

for i, (filename, key_id, violation_count) in enumerate(test_files, 1):
    print(f"Processing {filename}...")
    
    # Update current file
    metrics.session.current_file = filename
    
    # Record violations
    metrics.record_violation(filename, key_id, violation_count)
    
    # Record healing with varying durations
    healed_count = max(1, violation_count - 1)
    duration = 1.5 + (violation_count * 0.3)  # More violations = longer healing
    metrics.record_healing(filename, key_id, healed_count, duration)
    
    # Update progress
    metrics.update_file_progress(filename, "passed" if violation_count < 10 else "failed")
    
    time.sleep(0.3)

# Complete session
metrics.session.status = "completed"

print("\n✅ Test data generated!")
print(f"📊 Total violations: {metrics.session.total_violations}")
print(f"🏥 Total healed: {metrics.session.total_healed}")
print(f"📈 Files processed: {metrics.session.files_processed}/{metrics.session.total_files}")
print(f"\n🌐 Open http://localhost:5000 to view dashboard")
print("Press Ctrl+C to exit...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Shutting down...")
