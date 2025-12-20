"""
Canon Validator Web Dashboard - Interactive Web Interface
Real-time metrics with Flask backend and modern frontend
"""

import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
import time

# Import our metrics system
from canon_dashboard import DashboardMetrics, CanonDashboard

app = Flask(__name__)
CORS(app)

# Global metrics instance
metrics = DashboardMetrics()
dashboard = CanonDashboard(metrics)


@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/session')
def get_session():
    """Get current session information"""
    if not metrics.session:
        return jsonify({"error": "No active session"}), 404
    
    session_data = {
        "session_id": metrics.session.session_id,
        "target_directory": metrics.session.target_directory,
        "start_time": metrics.session.start_time.isoformat(),
        "total_files": metrics.session.total_files,
        "files_processed": metrics.session.files_processed,
        "files_passed": metrics.session.files_passed,
        "files_failed": metrics.session.files_failed,
        "total_violations": metrics.session.total_violations,
        "total_healed": metrics.session.total_healed,
        "current_file": metrics.session.current_file,
        "status": metrics.session.status,
        "progress_pct": metrics.session.progress_pct,
        "elapsed_time": metrics.session.elapsed_time,
        "files_per_minute": metrics.session.files_per_minute,
        "eta_minutes": metrics.session.eta_minutes
    }
    
    return jsonify(session_data)


@app.route('/api/keys')
def get_keys():
    """Get all key metrics"""
    keys_data = []
    
    for key in sorted(metrics.key_metrics.values(), key=lambda k: k.violations_found, reverse=True):
        if key.files_checked == 0 and key.violations_found == 0:
            continue
            
        keys_data.append({
            "key_id": key.key_id,
            "key_name": key.key_name,
            "files_checked": key.files_checked,
            "files_passed": key.files_passed,
            "files_failed": key.files_failed,
            "violations_found": key.violations_found,
            "violations_healed": key.violations_healed,
            "healing_attempts": key.healing_attempts,
            "pass_rate": key.pass_rate,
            "healing_success_rate": key.healing_success_rate,
            "status": key.status
        })
    
    return jsonify(keys_data)


@app.route('/api/keys/<int:key_id>')
def get_key_detail(key_id: int):
    """Get detailed information for a specific key"""
    if key_id not in metrics.key_metrics:
        return jsonify({"error": "Key not found"}), 404
    
    key = metrics.key_metrics[key_id]
    
    # Get violations for this key
    key_violations = [v for v in metrics.violation_timeline if v["key_id"] == key_id]
    key_healings = [h for h in metrics.healing_timeline if h["key_id"] == key_id]
    
    return jsonify({
        "key_id": key.key_id,
        "key_name": key.key_name,
        "files_checked": key.files_checked,
        "files_passed": key.files_passed,
        "files_failed": key.files_failed,
        "violations_found": key.violations_found,
        "violations_healed": key.violations_healed,
        "healing_attempts": key.healing_attempts,
        "pass_rate": key.pass_rate,
        "healing_success_rate": key.healing_success_rate,
        "status": key.status,
        "recent_violations": [
            {
                "file": v["file"],
                "count": v["count"],
                "timestamp": v["timestamp"].isoformat()
            }
            for v in key_violations[-10:]
        ],
        "recent_healings": [
            {
                "file": h["file"],
                "healed": h["healed"],
                "duration": h["duration"],
                "timestamp": h["timestamp"].isoformat()
            }
            for h in key_healings[-10:]
        ]
    })


@app.route('/api/violators')
def get_violators():
    """Get top violating files"""
    limit = int(request.args.get('limit', 20))
    return jsonify(metrics.get_top_violators(limit))


@app.route('/api/summary')
def get_summary():
    """Get overall summary statistics"""
    key_summary = metrics.get_key_summary()
    
    healing_rate = 0.0
    if metrics.session and metrics.session.total_violations > 0:
        healing_rate = (metrics.session.total_healed / metrics.session.total_violations) * 100
    
    return jsonify({
        "key_summary": key_summary,
        "healing_rate": healing_rate,
        "total_violations": metrics.session.total_violations if metrics.session else 0,
        "total_healed": metrics.session.total_healed if metrics.session else 0,
        "violation_timeline_count": len(metrics.violation_timeline),
        "healing_timeline_count": len(metrics.healing_timeline)
    })


@app.route('/api/timeline')
def get_timeline():
    """Get violation and healing timeline"""
    limit = int(request.args.get('limit', 50))
    
    # Combine and sort by timestamp
    combined = []
    
    for v in metrics.violation_timeline[-limit:]:
        combined.append({
            "type": "violation",
            "timestamp": v["timestamp"].isoformat(),
            "file": v["file"],
            "key_id": v["key_id"],
            "count": v["count"]
        })
    
    for h in metrics.healing_timeline[-limit:]:
        combined.append({
            "type": "healing",
            "timestamp": h["timestamp"].isoformat(),
            "file": h["file"],
            "key_id": h["key_id"],
            "healed": h["healed"],
            "duration": h["duration"]
        })
    
    combined.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return jsonify(combined[:limit])


@app.route('/api/export')
def export_report():
    """Export full report as JSON"""
    report_path = f"canon_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    dashboard.export_report(report_path)
    return jsonify({"success": True, "file": report_path})


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask server"""
    print(f"🚀 Canon Dashboard Web Server starting on http://{host}:{port}")
    print(f"📊 Open your browser to view the dashboard")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    # Start with mock data for testing
    metrics.start_session("agentic_core", 238)
    
    # Simulate some activity
    for i in range(10):
        metrics.record_violation(f"agentic_core/file_{i}.py", 40 + (i % 10), i * 2)
        metrics.record_healing(f"agentic_core/file_{i}.py", 40 + (i % 10), i, 1.5 + i * 0.3)
        metrics.update_file_progress(f"agentic_core/file_{i}.py", "passed" if i % 2 == 0 else "failed")
    
    run_server(debug=True)
