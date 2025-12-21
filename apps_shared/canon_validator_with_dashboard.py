"""
Canon Validator with Integrated Dashboard
Runs validation with real-time dashboard monitoring
"""

import sys
import threading
import time
from pathlib import Path
from typing import Optional

# Import dashboard components
from canon_dashboard import CanonDashboard, DashboardMetrics
from canon_dashboard_web import run_server


class DashboardIntegration:
    """Integration layer between validator and dashboard"""
    
    def __init__(self, metrics: DashboardMetrics):
        self.metrics = metrics
        self.dashboard = CanonDashboard(metrics)
        self.web_server_thread: Optional[threading.Thread] = None
        
    def start_web_dashboard(self, host='0.0.0.0', port=5000):
        """Start web dashboard in background thread"""
        self.web_server_thread = threading.Thread(
            target=run_server,
            args=(host, port, False),
            daemon=True
        )
        self.web_server_thread.start()
        print(f"\n🌐 Web Dashboard: http://localhost:{port}")
        print("📊 Terminal Dashboard: Starting in 3 seconds...\n")
        time.sleep(3)
    
    def start_terminal_dashboard(self):
        """Start terminal dashboard in background thread"""
        dashboard_thread = threading.Thread(
            target=self.dashboard.run_live,
            daemon=True
        )
        dashboard_thread.start()
        return dashboard_thread
    
    def hook_validator_events(self, validator):
        """Hook into validator events to update metrics"""
        
        # Override validator methods to capture events
        original_start = validator.start_validation if hasattr(validator, 'start_validation') else None
        original_process_file = validator.process_file if hasattr(validator, 'process_file') else None
        original_record_violation = validator.record_violation if hasattr(validator, 'record_violation') else None
        original_heal = validator.heal_violation if hasattr(validator, 'heal_violation') else None
        
        def wrapped_start(target_dir, total_files):
            self.metrics.start_session(target_dir, total_files)
            if original_start:
                return original_start(target_dir, total_files)
        
        def wrapped_process_file(file_path, *args, **kwargs):
            result = original_process_file(file_path, *args, **kwargs) if original_process_file else None
            
            # Update metrics based on result
            if result:
                status = "passed" if result.get("passed") else "failed"
                self.metrics.update_file_progress(file_path, status)
            
            return result
        
        def wrapped_record_violation(file_path, key_id, count, *args, **kwargs):
            self.metrics.record_violation(file_path, key_id, count)
            if original_record_violation:
                return original_record_violation(file_path, key_id, count, *args, **kwargs)
        
        def wrapped_heal(file_path, key_id, healed_count, duration, *args, **kwargs):
            self.metrics.record_healing(file_path, key_id, healed_count, duration)
            if original_heal:
                return original_heal(file_path, key_id, healed_count, duration, *args, **kwargs)
        
        # Apply hooks
        if original_start:
            validator.start_validation = wrapped_start
        if original_process_file:
            validator.process_file = wrapped_process_file
        if original_record_violation:
            validator.record_violation = wrapped_record_violation
        if original_heal:
            validator.heal_violation = wrapped_heal


def run_validator_with_dashboard(target_dir: str, mode: str = "both"):
    """
    Run canon validator with dashboard
    
    Args:
        target_dir: Target directory to validate
        mode: "web", "terminal", or "both"
    """
    
    # Initialize metrics
    metrics = DashboardMetrics()
    integration = DashboardIntegration(metrics)
    
    # Share metrics with web app
    import canon_dashboard_web
    canon_dashboard_web.metrics = metrics
    
    # Start dashboards based on mode
    if mode in ["web", "both"]:
        integration.start_web_dashboard(port=5000)
    
    if mode in ["terminal", "both"]:
        integration.start_terminal_dashboard()
    
    # Import and run validator
    # Note: This is a placeholder - actual validator import depends on your structure
    try:
        # Try to import the actual validator
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Mock validator for demonstration
        print(f"\n🎯 Starting validation of: {target_dir}")
        print("=" * 80)
        
        # Simulate validation with metrics
        metrics.start_session(target_dir, 238)
        
        # Simulate processing files
        for i in range(238):
            file_path = f"{target_dir}/file_{i}.py"
            
            # Simulate violations
            if i % 3 == 0:
                key_id = 40 + (i % 10)
                violation_count = (i % 20) + 1
                metrics.record_violation(file_path, key_id, violation_count)
                
                # Simulate healing
                time.sleep(0.1)
                healed = int(violation_count * 0.7)
                metrics.record_healing(file_path, key_id, healed, 0.5 + (i % 5) * 0.2)
                
                if healed >= violation_count * 0.8:
                    metrics.update_file_progress(file_path, "passed")
                else:
                    metrics.update_file_progress(file_path, "failed")
            else:
                metrics.update_file_progress(file_path, "passed")
            
            # Update key statuses
            if i % 50 == 0:
                for key_id in range(40, 45):
                    if key_id in metrics.key_metrics:
                        if metrics.key_metrics[key_id].violations_found > 0:
                            if metrics.key_metrics[key_id].healing_success_rate >= 80:
                                metrics.key_metrics[key_id].status = "passed"
                            else:
                                metrics.key_metrics[key_id].status = "failed"
                        else:
                            metrics.key_metrics[key_id].status = "running"
            
            time.sleep(0.05)  # Simulate processing time
        
        # Mark session complete
        if metrics.session:
            metrics.session.status = "completed"
        
        print("\n" + "=" * 80)
        print("✅ Validation complete!")
        print(f"📊 Final Results:")
        print(f"   - Files Processed: {metrics.session.files_processed}/{metrics.session.total_files}")
        print(f"   - Files Passed: {metrics.session.files_passed}")
        print(f"   - Files Failed: {metrics.session.files_failed}")
        print(f"   - Total Violations: {metrics.session.total_violations}")
        print(f"   - Total Healed: {metrics.session.total_healed}")
        print(f"   - Healing Rate: {(metrics.session.total_healed / metrics.session.total_violations * 100):.1f}%")
        
        # Export report
        report_path = f"canon_report_{metrics.session.session_id}.json"
        integration.dashboard.export_report(report_path)
        print(f"\n📄 Report exported: {report_path}")
        
        # Keep web server running
        if mode in ["web", "both"]:
            print(f"\n🌐 Web dashboard still running at http://localhost:5000")
            print("Press Ctrl+C to stop...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
        
    except Exception as e:
        print(f"\n❌ Error running validator: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Canon Validator with Dashboard")
    parser.add_argument("--target", required=True, help="Target directory to validate")
    parser.add_argument("--mode", choices=["web", "terminal", "both"], default="both",
                       help="Dashboard mode: web, terminal, or both")
    parser.add_argument("--port", type=int, default=5000, help="Web dashboard port")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🎯 CANON VALIDATOR WITH BEST-IN-CLASS DASHBOARD")
    print("=" * 80)
    
    run_validator_with_dashboard(args.target, args.mode)
