#!/usr/bin/env python3
"""Simple Playwright test to diagnose issues."""
import sys
import traceback

print("Testing Playwright import...")
try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright imported successfully")
except Exception as e:
    print(f"❌ Failed to import Playwright: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nTesting browser launch...")
try:
    with sync_playwright() as p:
        print("  Launching Chromium...")
        browser = p.chromium.launch(headless=True)
        print("  ✅ Browser launched")
        
        print("  Creating context...")
        context = browser.new_context()
        print("  ✅ Context created")
        
        print("  Creating page...")
        page = context.new_page()
        print("  ✅ Page created")
        
        print("  Navigating to localhost:8765...")
        try:
            page.goto("http://localhost:8765/autonomy_dashboard.html", timeout=10000)
            print("  ✅ Page loaded")
            print(f"  Page title: {page.title()}")
        except Exception as e:
            print(f"  ❌ Failed to load page: {e}")
            traceback.print_exc()
        
        browser.close()
        print("  ✅ Browser closed")
        
except Exception as e:
    print(f"❌ Playwright test failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All Playwright tests passed")
