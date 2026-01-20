#!/usr/bin/env python3
"""
End-to-End Dashboard Verification Script
Automates complete validation including browser cache bypass.
"""
import subprocess
import time
import sys
from pathlib import Path

def main():
    print("=" * 70)
    print("END-TO-END DASHBOARD VERIFICATION")
    print("=" * 70)
    
    # Step 1: Kill existing servers
    print("\n1. Killing existing Python servers...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                      capture_output=True, check=False)
        time.sleep(1)
        print("   ✅ Servers killed")
    except Exception as e:
        print(f"   ⚠️  Could not kill servers: {e}")
    
    # Step 2: Run test suite
    print("\n2. Running test suite...")
    test_path = Path(__file__).parent / "test_dashboard.py"
    result = subprocess.run([sys.executable, str(test_path)], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("   ❌ TESTS FAILED")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("   ✅ All tests passed")
    
    # Step 3: Start server
    print("\n3. Starting HTTP server on port 8080...")
    serve_path = Path(__file__).parent / "serve_dashboard.py"
    server_process = subprocess.Popen(
        [sys.executable, str(serve_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    print(f"   ✅ Server started (PID: {server_process.pid})")
    
    # Step 4: Open browser with cache-busting parameter
    print("\n4. Opening browser with cache-busting...")
    timestamp = int(time.time())
    url = f"http://localhost:8080/autonomy_dashboard.html?v={timestamp}"
    
    try:
        subprocess.run(['start', url], shell=True, check=True)
        print(f"   ✅ Browser opened: {url}")
    except Exception as e:
        print(f"   ❌ Could not open browser: {e}")
    
    # Step 5: Instructions
    print("\n" + "=" * 70)
    print("MANUAL VERIFICATION REQUIRED")
    print("=" * 70)
    print("In the browser that just opened:")
    print("1. Press F12 to open DevTools")
    print("2. Go to Console tab")
    print("3. Press Ctrl+Shift+R to hard refresh (bypass cache)")
    print("4. Verify you see:")
    print("   - [DEBUG] Script execution started")
    print("   - 🚀 loadData() called")
    print("   - 📊 dashboardData: 29 rows")
    print("   - ✅ Tables populated with data")
    print("   - NO red errors in console")
    print("\n5. If tables are empty:")
    print("   - Copy ALL console output")
    print("   - Report the error messages")
    print("=" * 70)
    
    print(f"\nServer running on PID {server_process.pid}")
    print("Press Ctrl+C to stop server")
    
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
