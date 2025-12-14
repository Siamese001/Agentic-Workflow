"""
Debug script to check VS Code/Windsurf test discovery configuration.
Run this in the terminal to verify all settings are correct.
import logging

logger = logging.getLogger(__name__)

"""
import os
import sys
import json
import subprocess
from pathlib import Path

def check_vscode_config() -> None:
    """Check VS Code configuration files."""
    logger.info("=== Checking VS Code Configuration ===")

    vscode_dir = Path(".vscode")
    if not vscode_dir.exists():
        logger.info("❌ .vscode directory not found!")
        return False

    # Check settings.json
    settings_file = vscode_dir / "settings.json"
    if settings_file.exists():
        with open(settings_file) as f:
            settings = json.load(f)
        logger.info(f"✅ settings.json found")
        logger.info(f"   - pytest enabled: {settings.get('python.testing.pytestEnabled', False)}")
        logger.info(f"   - pytest args: {settings.get('python.testing.pytestArgs', [])}")
        logger.info(f"   - pytest cwd: {settings.get('python.testing.cwd', 'NOT SET')}")
    else:
        logger.info("❌ settings.json not found!")

    # Check workspace file
    workspace_file = Path("Agentic.code-workspace")
    if workspace_file.exists():
        with open(workspace_file) as f:
            workspace = json.load(f)
        logger.info(f"✅ Workspace file found")
        logger.info(f"   - folders: {workspace.get('folders', [])}")
    else:
        logger.info("❌ Workspace file not found!")

    return True

def check_pytest() -> None:
    """Check pytest installation and discovery."""
    logger.info("\n=== Checking Pytest ===")

    # Check pytest version
    result = subprocess.run([sys.executable, "-m", "pytest", "--version"],
                          capture_output=True, text=True)
    if result.returncode == 0:
        logger.info(f"✅ Pytest installed: {result.stdout.strip()}")
    else:
        logger.info("❌ Pytest not working!")
        return False

    # Check test discovery
    result = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"],
                          capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        for line in lines:
            if 'collected' in line and 'tests' in line:
                logger.info(f"✅ Test discovery working: {line.strip()}")
                break
    else:
        logger.info("❌ Test discovery failed!")
        logger.info(f"Error: {result.stderr}")
        return False

    return True

def check_python_path() -> None:
    """Check Python path and environment."""
    logger.info("\n=== Checking Python Environment ===")
    logger.info(f"✅ Python executable: {sys.executable}")
    logger.info(f"✅ Current directory: {os.getcwd()}")
    logger.info(f"✅ Python path: {sys.path[0]}")

    # Check if we can import key modules
    key_modules = ['pytest', 'asyncio']
    for module in key_modules:
        try:
            __import__(module)
            logger.info(f"✅ Can import {module}")
        except ImportError:
            logger.info(f"❌ Cannot import {module}")

    return True

def main() -> None:
    """Run all checks."""
    logger.info("🔍 VS Code/Windsurf Test Discovery Debug Script")
    logger.info("=" * 50)

    all_good = True
    all_good &= check_vscode_config()
    all_good &= check_pytest()
    all_good &= check_python_path()

    logger.info("\n" + "=" * 50)
    if all_good:
        logger.info("✅ All checks passed! If tests still don't show in VS Code:")
        logger.info("   1. Close Windsurf completely")
        logger.info("   2. Reopen via File → Open Workspace from File")
        logger.info("   3. Open Test Explorer (beaker icon)")
        logger.info("   4. Click refresh button")
        logger.info("   5. Check Output panel for errors")
    else:
        logger.info("❌ Some checks failed. Fix the issues above.")

    logger.info("\n📝 Next steps:")
    logger.info("   - Run: python debug_test_discovery.py")
    logger.info("   - Share the output for further debugging")

if __name__ == "__main__":
    main()
