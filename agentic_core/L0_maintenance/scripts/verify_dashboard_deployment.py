#!/usr/bin/env python3
"""
Verify Dashboard Deployment with Playwright

This script uses Playwright to:
1. Start the dashboard server
2. Navigate to the Live Runtime tab
3. Verify all Phase 5 sections are visible
4. Take screenshots for verification
5. Check that JavaScript is loading correctly

Usage:
    python scripts/verify_dashboard_deployment.py
"""
import sys
import time
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Verify dashboard deployment using Playwright."""
    print("=" * 70)
    print("DASHBOARD DEPLOYMENT VERIFICATION")
    print("=" * 70)
    
    # Check if Playwright is available
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n❌ Playwright not installed!")
        print("\nInstall with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return 1
    
    # Start dashboard server
    print("\n1. Starting dashboard server on port 8765...")
    dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"
    
    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8765"],
        cwd=str(dashboard_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    print("   ✅ Server started")
    
    try:
        with sync_playwright() as p:
            print("\n2. Launching browser...")
            browser = p.chromium.launch(headless=False)  # Set to False to see the browser
            page = browser.new_page()
            
            # Navigate to dashboard
            print("\n3. Navigating to dashboard...")
            page.goto("http://localhost:8765/autonomy_dashboard.html#runtime")
            page.wait_for_load_state("networkidle")
            
            # Wait for page to fully load
            time.sleep(2)
            
            print("\n4. Checking for Phase 5 sections...")
            
            # Check for section headers
            sections_to_check = [
                ("Meta-Learning Activity", "🧠 Meta-Learning Activity"),
                ("Redis Cache Activity", "💾 Redis Cache Activity"),
                ("Pinecone Vector Operations", "🔍 Pinecone Vector Operations"),
                ("Agent Execution Flow", "⚡ Agent Execution Flow"),
            ]
            
            found_sections = []
            missing_sections = []
            
            for section_id, section_name in sections_to_check:
                # Check if section header is visible
                try:
                    element = page.locator(f"text={section_name}").first
                    if element.is_visible():
                        found_sections.append(section_name)
                        print(f"   ✅ Found: {section_name}")
                    else:
                        missing_sections.append(section_name)
                        print(f"   ❌ Not visible: {section_name}")
                except Exception as e:
                    missing_sections.append(section_name)
                    print(f"   ❌ Not found: {section_name} - {e}")
            
            # Check for container elements
            print("\n5. Checking for container elements...")
            containers = [
                "#meta-stats",
                "#strategy-weights",
                "#experience-stream",
                "#pattern-timeline",
                "#redis-stats",
                "#redis-log",
                "#pinecone-stats",
                "#pinecone-queries",
                "#layer-flow",
                "#execution-summary",
                "#execution-timeline",
            ]
            
            found_containers = []
            missing_containers = []
            
            for container_id in containers:
                try:
                    element = page.locator(container_id).first
                    if element.count() > 0:
                        found_containers.append(container_id)
                        print(f"   ✅ Found: {container_id}")
                    else:
                        missing_containers.append(container_id)
                        print(f"   ❌ Not found: {container_id}")
                except Exception as e:
                    missing_containers.append(container_id)
                    print(f"   ❌ Error checking {container_id}: {e}")
            
            # Check JavaScript console for errors
            print("\n6. Checking browser console...")
            console_messages = []
            
            def handle_console(msg):
                console_messages.append(f"[{msg.type}] {msg.text}")
            
            page.on("console", handle_console)
            
            # Reload to capture console messages
            page.reload()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            errors = [msg for msg in console_messages if 'error' in msg.lower()]
            if errors:
                print(f"   ⚠️  Found {len(errors)} console errors:")
                for error in errors[:5]:  # Show first 5
                    print(f"      {error}")
            else:
                print("   ✅ No console errors")
            
            # Check if JavaScript files loaded
            print("\n7. Checking JavaScript file loading...")
            js_files = [
                "meta-learning-panel.js",
                "redis-monitor.js",
                "pinecone-monitor.js",
                "execution-flow.js",
                "meta-learning-controller.js",
            ]
            
            # Check network requests
            loaded_js = []
            failed_js = []
            
            for js_file in js_files:
                try:
                    # Check if file is accessible
                    response = page.goto(f"http://localhost:8765/js/components/{js_file}")
                    if response.status == 200:
                        loaded_js.append(js_file)
                        print(f"   ✅ Loaded: {js_file}")
                    else:
                        failed_js.append(js_file)
                        print(f"   ❌ Failed ({response.status}): {js_file}")
                except Exception as e:
                    failed_js.append(js_file)
                    print(f"   ❌ Error loading {js_file}: {e}")
            
            # Go back to dashboard
            page.goto("http://localhost:8765/autonomy_dashboard.html#runtime")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Take screenshot
            print("\n8. Taking screenshot...")
            screenshot_path = project_root / "dashboard_verification.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"   ✅ Screenshot saved: {screenshot_path}")
            
            # Summary
            print("\n" + "=" * 70)
            print("VERIFICATION SUMMARY")
            print("=" * 70)
            print(f"Sections found: {len(found_sections)}/4")
            print(f"Containers found: {len(found_containers)}/11")
            print(f"JS files loaded: {len(loaded_js)}/5")
            print(f"Console errors: {len(errors)}")
            
            if missing_sections:
                print(f"\n❌ Missing sections: {missing_sections}")
            if missing_containers:
                print(f"\n❌ Missing containers: {missing_containers}")
            if failed_js:
                print(f"\n❌ Failed JS files: {failed_js}")
            
            if len(found_sections) == 4 and len(found_containers) == 11 and len(loaded_js) == 5:
                print("\n✅ ALL PHASE 5 COMPONENTS DEPLOYED SUCCESSFULLY!")
                result = 0
            else:
                print("\n❌ DEPLOYMENT INCOMPLETE - Some components missing")
                result = 1
            
            browser.close()
            return result
            
    finally:
        # Stop server
        print("\n9. Stopping dashboard server...")
        server_process.terminate()
        server_process.wait()
        print("   ✅ Server stopped")


if __name__ == "__main__":
    sys.exit(main())
