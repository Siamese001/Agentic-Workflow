#!/usr/bin/env python3
"""
Dashboard E2E Pipeline Orchestrator

Simplified execution pipeline that:
1. Regenerates autonomy_dashboard.html using generate_dashboard.py
2. Runs unified tests (test_dashboard.py)
3. If tests pass, starts the server (serve_dashboard.py)
4. Opens browser to http://localhost:8080/autonomy_dashboard.html
5. (Optional) Watches for data changes and auto-reloads

Usage:
    python run_dashboard_pipeline.py              # Run full pipeline
    python run_dashboard_pipeline.py --watch      # Run with auto-reload
    python run_dashboard_pipeline.py --skip-tests # Skip tests (dev mode)
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional
import argparse

class DashboardPipeline:
    """Orchestrates the complete dashboard generation and deployment pipeline."""
    
    def __init__(self, project_root: Path, skip_tests: bool = False, watch: bool = False):
        self.project_root = project_root
        self.dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"
        self.skip_tests = skip_tests
        self.watch = watch
        self.server_process: Optional[subprocess.Popen] = None
        
    def print_header(self, title: str):
        """Print a formatted section header."""
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)
    
    def print_step(self, step: str):
        """Print a step indicator."""
        print(f"\n{'─' * 70}")
        print(f"STEP: {step}")
        print(f"{'─' * 70}")
    
    def step_1_regenerate_dashboard(self) -> bool:
        """Step 1: Regenerate dashboard HTML."""
        self.print_step("1. Regenerating Dashboard")
        
        generator_path = self.dashboard_dir / "generate_dashboard.py"
        
        try:
            result = subprocess.run(
                [sys.executable, str(generator_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"❌ Dashboard generation FAILED")
                print(result.stderr)
                return False
            
            print("✅ Dashboard regenerated successfully")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Dashboard generation TIMED OUT (>60s)")
            return False
        except Exception as e:
            print(f"❌ Dashboard generation ERROR: {e}")
            return False
    
    def step_2_run_tests(self) -> bool:
        """Step 2: Run unified test suite."""
        if self.skip_tests:
            print("\n⚠️  SKIPPING TESTS (--skip-tests flag)")
            return True
        
        self.print_step("2. Running Unified Test Suite")
        
        test_path = self.dashboard_dir / "test_dashboard.py"
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"❌ TESTS FAILED - Cannot proceed to deployment")
                print(result.stderr)
                return False
            
            # Check for "ALL TESTS PASSED" in output
            if "ALL TESTS PASSED" in result.stdout:
                print("✅ All tests passed - Dashboard ready for deployment")
                return True
            else:
                print("❌ Tests did not complete successfully")
                return False
            
        except subprocess.TimeoutExpired:
            print("❌ Tests TIMED OUT (>120s)")
            return False
        except Exception as e:
            print(f"❌ Test execution ERROR: {e}")
            return False
    
    def step_3_start_server(self) -> bool:
        """Step 3: Start HTTP server."""
        self.print_step("3. Starting HTTP Server")
        
        server_path = self.dashboard_dir / "serve_dashboard.py"
        
        try:
            # Start server as background process
            self.server_process = subprocess.Popen(
                [sys.executable, str(server_path)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start (check for output)
            print("⏳ Waiting for server to start...")
            time.sleep(2)
            
            # Check if server is still running
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                print(f"❌ Server failed to start")
                print(stdout)
                print(stderr)
                return False
            
            print("✅ Server started on http://localhost:8080")
            print("   Dashboard: http://localhost:8080/autonomy_dashboard.html")
            return True
            
        except Exception as e:
            print(f"❌ Server start ERROR: {e}")
            return False
    
    def step_4_open_browser(self):
        """Step 4: Open browser to dashboard."""
        self.print_step("4. Opening Browser")
        
        url = "http://localhost:8080/autonomy_dashboard.html"
        
        try:
            print(f"🌐 Opening {url}")
            webbrowser.open(url)
            print("✅ Browser opened")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"   Please open manually: {url}")
    
    def step_5_watch_mode(self):
        """Step 5: Watch for changes and auto-reload (optional)."""
        if not self.watch:
            return
        
        self.print_step("5. Watch Mode (Auto-Reload)")
        
        print("👀 Watching for changes to agent_discovery_full.json...")
        print("   Press Ctrl+C to stop")
        
        agent_discovery = self.project_root / "agent_discovery_full.json"
        last_modified = agent_discovery.stat().st_mtime if agent_discovery.exists() else 0
        
        try:
            while True:
                time.sleep(5)  # Check every 5 seconds
                
                if not agent_discovery.exists():
                    continue
                
                current_modified = agent_discovery.stat().st_mtime
                
                if current_modified > last_modified:
                    print("\n🔄 Change detected! Regenerating dashboard...")
                    last_modified = current_modified
                    
                    # Regenerate
                    if self.step_1_regenerate_dashboard():
                        # Run tests
                        if self.skip_tests or self.step_2_run_tests():
                            print("✅ Dashboard updated successfully")
                            print("   Refresh browser to see changes")
                        else:
                            print("❌ Tests failed - dashboard not updated")
                    else:
                        print("❌ Regeneration failed")
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Watch mode stopped")
    
    def cleanup(self):
        """Clean up resources (stop server)."""
        if self.server_process and self.server_process.poll() is None:
            print("\n🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ Server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️  Server forcefully killed")
    
    def run(self) -> bool:
        """Execute the complete pipeline."""
        self.print_header("DASHBOARD E2E PIPELINE")
        
        try:
            # Step 1: Regenerate dashboard
            if not self.step_1_regenerate_dashboard():
                return False
            
            # Step 2: Run tests
            if not self.step_2_run_tests():
                return False
            
            # Step 3: Start server
            if not self.step_3_start_server():
                return False
            
            # Step 4: Open browser
            self.step_4_open_browser()
            
            # Step 5: Watch mode (optional)
            self.step_5_watch_mode()
            
            # If not in watch mode, keep server running
            if not self.watch:
                self.print_header("PIPELINE COMPLETE")
                print("\n✅ Dashboard is live at http://localhost:8080/autonomy_dashboard.html")
                print("   Server is running in background")
                print("   Press Ctrl+C to stop server and exit")
                
                try:
                    # Keep script alive while server runs
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n\n⏹️  Shutting down...")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Pipeline interrupted")
            return False
        finally:
            self.cleanup()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Dashboard E2E Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_dashboard_pipeline.py              # Run full pipeline
  python run_dashboard_pipeline.py --watch      # Run with auto-reload
  python run_dashboard_pipeline.py --skip-tests # Skip tests (dev mode)
        """
    )
    
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip test execution (development mode)'
    )
    
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Watch for changes and auto-reload'
    )
    
    args = parser.parse_args()
    
    # Determine project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent
    
    # Run pipeline
    pipeline = DashboardPipeline(
        project_root=project_root,
        skip_tests=args.skip_tests,
        watch=args.watch
    )
    
    success = pipeline.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
