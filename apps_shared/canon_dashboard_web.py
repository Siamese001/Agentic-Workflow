"""
Canon Validator Web Dashboard - Interactive Web Interface
Real-time metrics with Flask backend and modern frontend.
HARDENED: Thread-safe reads, Input sanitization, Robust error handling.
"""
import time


import logging
import os
from datetime import datetime

# Import our metrics system
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Configure Flask logging to not interfere with console output
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL) # Further silence logs to prevent thread flooding

app = Flask(__name__)
CORS(app)

# Global instances (initialized as None to allow validator injection)
try:
    # Attempt to initialize standalone metrics if not injected
    from canon_dashboard import DashboardMetrics, CanonDashboard
    metrics = DashboardMetrics()
    dashboard = CanonDashboard(metrics)
except ImportError:
    metrics = None
    dashboard = None
agents_global = []  # List of live agent instances for visualization

print("[WEB] Dashboard Module Loaded. Waiting for metrics injection...")

# Safety constants
MAX_LIMIT = 1000
DEFAULT_LIMIT = 50

def safe_div(n: float, d: float) -> float:
    """Safe division helper"""
    return (n / d) if d > 0 else 0.0

@app.route('/')
def index():
    """Serve the production dashboard HTML"""
    return render_template('dashboard_pro.html')


@app.route('/api/session')
def get_session():
    """Get current session information (Thread-Safe)"""
    if not metrics:
        return jsonify({"error": "Metrics system not initialized"}), 500

    # Lock to ensure consistent snapshot of session state
    with metrics.lock:
        if not metrics.session:
            return jsonify({"error": "No active session"}), 404
        
        session = metrics.session
        session_data = {
            "session_id": session.session_id,
            "target_directory": session.target_directory,
            "start_time": session.start_time.isoformat(),
            "total_files": session.total_files,
            "files_processed": session.files_processed,
            "files_passed": session.files_passed,
            "files_failed": session.files_failed,
            "total_violations": session.total_violations,
            "total_healed": session.total_healed,
            "current_file": session.current_file,
            "status": session.status,
            "progress_pct": session.progress_pct,
            "elapsed_time": session.elapsed_time,
            "files_per_minute": session.files_per_minute,
            "eta_minutes": session.eta_minutes
        }
    
    return jsonify(session_data)


@app.route('/api/keys')
def get_keys():
    """Get all key metrics (Thread-Safe)"""
    keys_data = []
    
    with metrics.lock:
        # Sort while locked or create snapshot first
        sorted_keys = sorted(
            metrics.key_metrics.values(), 
            key=lambda k: k.violations_found, 
            reverse=True
        )
        
        for key in sorted_keys:
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
    """Get detailed information for a specific key (Thread-Safe)"""
    with metrics.lock:
        if key_id not in metrics.key_metrics:
            return jsonify({"error": "Key not found"}), 404
        
        key = metrics.key_metrics[key_id]
        
        # Create snapshots of deque/list for filtering
        # Note: metrics.violation_timeline is a deque in hardened version
        snapshot_violations = list(metrics.violation_timeline)
        snapshot_healings = list(metrics.healing_timeline)
        
        key_violations = [v for v in snapshot_violations if v["key_id"] == key_id]
        key_healings = [h for h in snapshot_healings if h["key_id"] == key_id]
        
        response_data = {
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
        }
        
    return jsonify(response_data)


@app.route('/api/violators')
def get_violators():
    """Get top violating files (Uses Metrics internal locking)"""
    try:
        limit = min(int(request.args.get('limit', 20)), MAX_LIMIT)
    except ValueError:
        limit = 20
    # get_top_violators is already thread-safe in the hardened DashboardMetrics
    return jsonify(metrics.get_top_violators(limit))


@app.route('/api/healing-log')
def get_healing_log():
    """Get healing activity log (Uses Metrics internal locking)"""
    try:
        limit = min(int(request.args.get('limit', 50)), MAX_LIMIT)
    except ValueError:
        limit = 50
    # get_healing_log is already thread-safe
    return jsonify(metrics.get_healing_log(limit))


@app.route('/api/summary')
def get_summary():
    """Get overall summary statistics (Thread-Safe)"""
    # get_key_summary is thread-safe
    key_summary = metrics.get_key_summary()
    
    with metrics.lock:
        session = metrics.session
        total_violations = session.total_violations if session else 0
        total_healed = session.total_healed if session else 0
        
        healing_rate = safe_div(total_healed, total_violations) * 100
        
        summary_data = {
            "key_summary": key_summary,
            "healing_rate": healing_rate,
            "total_violations": total_violations,
            "total_healed": total_healed,
            "violation_timeline_count": len(metrics.violation_timeline),
            "healing_timeline_count": len(metrics.healing_timeline)
        }
    
    return jsonify(summary_data)


@app.route('/api/timeline')
def get_timeline():
    """Get violation and healing timeline (Thread-Safe Snapshot)"""
    try:
        limit = min(int(request.args.get('limit', 50)), MAX_LIMIT)
    except ValueError:
        limit = DEFAULT_LIMIT
    
    combined = []
    
    with metrics.lock:
        # Create snapshots of the last N items to minimize lock time
        # Deque slicing is not directly supported, so we use list(islice) or just list() if small
        # Since we hardened deque to maxlen=5000, list() is safe and fast enough.
        v_snapshot = list(metrics.violation_timeline)
        h_snapshot = list(metrics.healing_timeline)

    # Process outside the lock
    for v in v_snapshot[-limit:]:
        combined.append({
            "type": "violation",
            "timestamp": v["timestamp"].isoformat(),
            "file": v["file"],
            "key_id": v["key_id"],
            "count": v["count"]
        })
    
    for h in h_snapshot[-limit:]:
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


@app.route('/api/agent_graph')
def get_agent_graph():
    """Get agent architecture graph data for visualization with rich metadata"""
    nodes = []
    edges = []
    
    # Level mapping for agents
    agent_levels = {
        'ArchitectureGovernor': 'L1',
        'SystemArchitect': 'L1',
        'StructuralEngineer': 'L2',
        'HealerAgent': 'L2',
        'HygieneGuardian': 'L3',
        'DependencySentinel': 'L3',
        'SecurityEnforcer': 'L4',
        'MemoryArchitect': 'L5',
        'HallucinationHunter': 'L5',
    }
    
    # Layer color map (production-ready colors)
    level_colors = {
        'L1': '#dc3545',  # Red - Strategic
        'L2': '#fd7e14',  # Orange
        'L3': '#ffc107',  # Yellow
        'L4': '#28a745',  # Green
        'L5': '#007bff',  # Blue - Deep Intelligence
        'L6': '#6c757d',  # Gray - Unknown
        'Core': '#343a40' # Dark Gray - Core Systems
    }
    
    # Fixed core nodes with stable IDs and rich metadata
    core_nodes = {
        'ctx': {
            'id': 'ctx',
            'label': 'ValidationContext',
            'level': 'L4',
            'group': 'core',
            'title': 'Central L4 State\nHolds report, results, signals',
            'description': 'Central state management for all validation operations'
        },
        'engine': {
            'id': 'engine',
            'label': 'SubAtomicEngine\nGemini',
            'level': 'L5',
            'group': 'core',
            'title': 'L5 Neural Link\nAll LLM calls flow here',
            'description': 'Gemini-powered AI engine for code analysis and generation'
        },
        'safety': {
            'id': 'safety',
            'label': 'SafetyGuardrail',
            'level': 'L5',
            'group': 'core',
            'title': 'Deletion Limit: 110 lines\nPrevents runaway edits',
            'description': 'Safety system preventing destructive code changes'
        },
        'fission': {
            'id': 'fission',
            'label': 'FissionManager',
            'level': 'L3',
            'group': 'core',
            'title': 'Atomic Split Logic\nThreshold: 10,000 LOC',
            'description': 'Manages file splitting for large files'
        }
    }
    
    # Add core nodes with enhanced styling
    for node_id, data in core_nodes.items():
        nodes.append({
            'id': node_id,
            'label': data['label'],
            'level': data['level'],
            'group': data['group'],
            'title': data['title'],
            'shape': 'ellipse',
            'color': {
                'background': level_colors['Core'],
                'border': '#17a2b8',
                'highlight': {'background': '#17a2b8', 'border': '#ffffff'}
            },
            'font': {'color': 'white'},
            'status': 'Core',
            'task': 'Always Active'
        })
    
    # Add agents with rich metadata
    for agent in agents_global:
        agent_name = agent.__class__.__name__
        level = agent_levels.get(agent_name, 'L6')
        status = getattr(agent, 'current_status', 'Offline')
        task = getattr(agent, 'current_task', 'No task')
        
        nodes.append({
            'id': agent_name,
            'label': agent_name,
            'level': level,
            'group': 'agent',
            'title': f"Agent: {agent_name}\nLevel: {level}\nStatus: {status}\nTask: {task}",
            'shape': 'box',
            'color': {
                'background': level_colors.get(level, '#6c757d'),
                'border': '#ffffff',
                'highlight': {'background': '#ffffff', 'border': '#ff0000'}
            },
            'font': {'color': 'white'},
            'status': status,
            'task': task
        })
        
        # Universal dependencies (all agents connect to core)
        edges.append({'from': agent_name, 'to': 'ctx', 'dashes': False})
        edges.append({'from': agent_name, 'to': 'engine', 'dashes': False})
        edges.append({'from': agent_name, 'to': 'safety', 'dashes': False})
        
        # Special edge for ArchitectureGovernor (stronger connection to fission)
        if agent_name == 'ArchitectureGovernor':
            edges.append({
                'from': agent_name,
                'to': 'fission',
                'color': {'color': '#dc3545'},
                'width': 3,
                'arrows': 'to'
            })
    
    return jsonify({
        'nodes': nodes,
        'edges': edges
    })


@app.route('/agent_graph')
def agent_graph_page():
    """Serve the agent architecture visualization page"""
    return render_template('agent_graph.html')


@app.route('/api/export')
def export_report():
    """Export full report as JSON"""
    try:
        filename = f"canon_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        # Export logic inside dashboard handles locking
        dashboard.export_report(filename)
        return jsonify({"success": True, "file": filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def run_server(host='0.0.0.0', port=5000, debug=False):
    """
    Run the Flask server with thread-safe configuration.
    HARDENED: External Port Mapping, Re-loader Disabled, Threading Enabled.
    """
    # Use environment port if available (for Docker/Cloud)
    port = int(os.environ.get("DASHBOARD_PORT", port))
    
    print(f"[*] DASHBOARD: Starting background thread on http://{host}:{port}")
    
    try:
        # use_reloader MUST be False when running in a background thread
        app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"[!] DASHBOARD ERROR: Could not start server: {e}")
        if "Address already in use" in str(e):
            print("    -> Tip: Run 'lsof -i :5000' and kill the existing process.")


if __name__ == "__main__":
    import json
    import os
    from pathlib import Path

    # Try to load real session data from validator
    session_file = Path("canon_session.json")
    
    if session_file.exists():
        print(f"Loading real session data from {session_file}...")
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Load session data into metrics
        if session_data.get("session"):
            sess = session_data["session"]
            metrics.start_session(sess.get("target_folder", "agentic_core"), sess.get("total_files", 238))
            metrics.session.start_time = sess.get("start_time")
            metrics.session.elapsed_time = sess.get("elapsed_time", 0)
            metrics.session.files_processed = sess.get("files_processed", 0)
            metrics.session.files_passed = sess.get("files_passed", 0)
            metrics.session.files_failed = sess.get("files_failed", 0)
            metrics.session.total_violations = sess.get("total_violations", 0)
            metrics.session.total_healed = sess.get("total_healed", 0)
        
        # Load key metrics
        if session_data.get("key_metrics"):
            for key_id, key_data in session_data["key_metrics"].items():
                if str(key_id) in metrics.key_metrics:
                    km = metrics.key_metrics[str(key_id)]
                    km.files_checked = key_data.get("files_checked", 0)
                    km.files_passed = key_data.get("files_passed", 0)
                    km.files_failed = key_data.get("files_failed", 0)
                    km.violations_found = key_data.get("violations_found", 0)
                    km.violations_healed = key_data.get("violations_healed", 0)
                    km.status = key_data.get("status", "pending")
        
        print("Real session data loaded successfully!")
    else:
        print(f"No session file found at {session_file}.")
        if metrics:
            print("Using mock data...")
            # Fallback to mock data
            metrics.start_session("agentic_core", 238)
            
            print("Populating mock data...")
            # Simulate some activity
            for i in range(10):
                metrics.record_violation(f"agentic_core/file_{i}.py", 40 + (i % 10), i * 2)
                metrics.record_healing(f"agentic_core/file_{i}.py", 40 + (i % 10), i, 1.5 + i * 0.3)
                metrics.update_file_progress(f"agentic_core/file_{i}.py", "passed" if i % 2 == 0 else "failed")
        else:
            print("No metrics system available - running in minimal mode")
            print("Agent graph visualization will still work!")
    
    run_server(debug=True)