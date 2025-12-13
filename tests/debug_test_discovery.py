"""
Debug script to check VS Code/Windsurf test discovery configuration.
Run this in the terminal to verify all settings are correct.
"""
import os
import sys
import json
import subprocess
from pathlib import Path

def check_vscode_config():
    """Check VS Code configuration files."""
    print("=== Checking VS Code Configuration ===")
    
    vscode_dir = Path(".vscode")
    if not vscode_dir.exists():
        print("❌ .vscode directory not found!")
        return False
    
    # Check settings.json
    settings_file = vscode_dir / "settings.json"
    if settings_file.exists():
        with open(settings_file) as f:
            settings = json.load(f)
        print(f"✅ settings.json found")
        print(f"   - pytest enabled: {settings.get('python.testing.pytestEnabled', False)}")
        print(f"   - pytest args: {settings.get('python.testing.pytestArgs', [])}")
        print(f"   - pytest cwd: {settings.get('python.testing.cwd', 'NOT SET')}")
    else:
        print("❌ settings.json not found!")
    
    # Check workspace file
    workspace_file = Path("Agentic.code-workspace")
    if workspace_file.exists():
        with open(workspace_file) as f:
            workspace = json.load(f)
        print(f"✅ Workspace file found")
        print(f"   - folders: {workspace.get('folders', [])}")
    else:
        print("❌ Workspace file not found!")
    
    return True

def check_pytest():
    """Check pytest installation and discovery."""
    print("\n=== Checking Pytest ===")
    
    # Check pytest version
    result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Pytest installed: {result.stdout.strip()}")
    else:
        print("❌ Pytest not working!")
        return False
    
    # Check test discovery
    result = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        for line in lines:
            if 'collected' in line and 'tests' in line:
                print(f"✅ Test discovery working: {line.strip()}")
                break
    else:
        print("❌ Test discovery failed!")
        print(f"Error: {result.stderr}")
        return False
    
    return True

def check_python_path():
    """Check Python path and environment."""
    print("\n=== Checking Python Environment ===")
    print(f"✅ Python executable: {sys.executable}")
    print(f"✅ Current directory: {os.getcwd()}")
    print(f"✅ Python path: {sys.path[0]}")
    
    # Check if we can import key modules
    key_modules = ['pytest', 'asyncio']
    for module in key_modules:
        try:
            __import__(module)
            print(f"✅ Can import {module}")
        except ImportError:
            print(f"❌ Cannot import {module}")
    
    return True

def main():
    """Run all checks."""
    print("🔍 VS Code/Windsurf Test Discovery Debug Script")
    print("=" * 50)
    
    all_good = True
    all_good &= check_vscode_config()
    all_good &= check_pytest()
    all_good &= check_python_path()
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ All checks passed! If tests still don't show in VS Code:")
        print("   1. Close Windsurf completely")
        print("   2. Reopen via File → Open Workspace from File")
        print("   3. Open Test Explorer (beaker icon)")
        print("   4. Click refresh button")
        print("   5. Check Output panel for errors")
    else:
        print("❌ Some checks failed. Fix the issues above.")
    
    print("\n📝 Next steps:")
    print("   - Run: python debug_test_discovery.py")
    print("   - Share the output for further debugging")

if __name__ == "__main__":
    main()
