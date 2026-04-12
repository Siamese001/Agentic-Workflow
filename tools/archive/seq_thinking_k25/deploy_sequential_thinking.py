#!/usr/bin/env python3
"""
Deploy Sequential Thinking MCP Configuration for Kimi 2.5

This script applies all sequential thinking forcing strategies:
1. Updates MCP configuration
2. Sets up environment variables
3. Deploys monitoring tools
4. Validates installation
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class SequentialThinkingDeployer:
    """Deployer for sequential thinking MCP configuration."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.backup_dir = repo_root / ".backup" / "sequential_thinking"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Paths to key files
        self.user_mcp_config = Path("C:\\Users\\amita\\.codeium\\windsurf\\mcp_config.json")
        self.workspace_mcp_config = repo_root / ".windsurf" / "mcp_config.json"
        self.enhanced_config = repo_root / ".windsurf" / "mcp_config_enhanced.json"

    def backup_existing_config(self) -> bool:
        """Backup existing MCP configuration."""
        try:
            if self.user_mcp_config.exists():
                backup_path = self.backup_dir / "user_mcp_config_backup.json"
                shutil.copy2(self.user_mcp_config, backup_path)
                print(f"✅ Backed up user MCP config to: {backup_path}")

            if self.workspace_mcp_config.exists():
                backup_path = self.backup_dir / "workspace_mcp_config_backup.json"
                shutil.copy2(self.workspace_mcp_config, backup_path)
                print(f"✅ Backed up workspace MCP config to: {backup_path}")

            return True
        except Exception as e:
            print(f"❌ Failed to backup configuration: {e}")
            return False

    def apply_mcp_configuration(self) -> bool:
        """Apply enhanced MCP configuration."""
        try:
            if not self.enhanced_config.exists():
                print(f"❌ Enhanced MCP config not found: {self.enhanced_config}")
                return False

            # Copy enhanced config to user-global location
            shutil.copy2(self.enhanced_config, self.user_mcp_config)
            print(f"✅ Applied enhanced MCP configuration to: {self.user_mcp_config}")

            # Also update workspace config for documentation
            shutil.copy2(self.enhanced_config, self.workspace_mcp_config)
            print(f"✅ Updated workspace MCP configuration: {self.workspace_mcp_config}")

            return True
        except Exception as e:
            print(f"❌ Failed to apply MCP configuration: {e}")
            return False

    def setup_environment(self) -> bool:
        """Setup environment variables for sequential thinking."""
        try:
            env_script = self.repo_root / "ops_scripts" / "environment" / "seq_thinking_env.py"

            if not env_script.exists():
                print(f"❌ Environment script not found: {env_script}")
                return False

            # Run environment setup and capture output to set in current process
            result = subprocess.run(
                [
                    sys.executable,
                    str(env_script),
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            if result.returncode == 0:
                print("✅ Environment variables configured successfully")
                print(result.stdout)

                # Set environment variables in current process
                env_vars = {
                    "SEQUENTIAL_THINKING_ENABLED": "true",
                    "SEQUENTIAL_THINKING_PRIORITY": "1",
                    "WINDSURF_TOOL_PREFERENCE": "sequential-thinking",
                    "KIMI25_SEQUENTIAL_THINKING": "enabled",
                    "MCP_SEQUENTIAL_THINKING_BOOST": "enabled",
                }

                for key, value in env_vars.items():
                    os.environ[key] = value

                return True
            else:
                print(f"❌ Environment setup failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to setup environment: {e}")
            return False

    def create_directories(self) -> bool:
        """Create necessary directories for monitoring and artifacts."""
        try:
            directories = [
                self.repo_root / "artifacts" / "monitoring",
                self.repo_root / "tools" / "mcp",
                self.repo_root / "tools" / "monitoring",
                self.repo_root / "ops_scripts" / "environment",
                self.repo_root / "apps_shared" / "prompts",
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)

            print("✅ Created necessary directories")
            return True
        except Exception as e:
            print(f"❌ Failed to create directories: {e}")
            return False

    def validate_installation(self) -> dict[str, bool]:
        """Validate sequential thinking installation."""
        results = {}

        # Check MCP configuration
        try:
            with open(self.user_mcp_config) as f:
                config = json.load(f)

            seq_thinking_config = config.get("mcpServers", {}).get("sequential-thinking", {})
            if seq_thinking_config and not seq_thinking_config.get("disabled", True):
                results["mcp_config"] = True
                print("✅ MCP configuration valid")
            else:
                results["mcp_config"] = False
                print("❌ Sequential thinking not properly configured in MCP")
        except Exception as e:
            results["mcp_config"] = False
            print(f"❌ MCP configuration validation failed: {e}")

        # Check environment variables
        env_vars = [
            "SEQUENTIAL_THINKING_ENABLED",
            "SEQUENTIAL_THINKING_PRIORITY",
            "WINDSURF_TOOL_PREFERENCE",
            "KIMI25_SEQUENTIAL_THINKING",
        ]

        all_env_set = True
        for var in env_vars:
            if os.environ.get(var):
                print(f"✅ {var}={os.environ.get(var)}")
            else:
                print(f"❌ {var} not set")
                all_env_set = False

        results["environment"] = all_env_set

        # Check tool files
        tool_files = [
            self.repo_root / "tools" / "mcp" / "sequential_thinking_booster.py",
            self.repo_root / "tools" / "monitoring" / "mcp_usage_tracker.py",
            self.repo_root / "agentic_core" / "planning" / "sequential_thinking_workflow.py",
            self.repo_root / "apps_shared" / "prompts" / "sequential_thinking_templates.py",
        ]

        all_tools_exist = True
        for tool_file in tool_files:
            if tool_file.exists():
                print(f"✅ {tool_file.name}")
            else:
                print(f"❌ {tool_file.name} missing")
                all_tools_exist = False

        results["tools"] = all_tools_exist

        return results

    def run_tests(self) -> bool:
        """Run basic tests to verify installation."""
        try:
            # Test sequential thinking booster
            booster_script = self.repo_root / "tools" / "mcp" / "sequential_thinking_booster.py"

            # Create test data
            test_tools = [
                {"name": "sequential-thinking", "description": "Sequential reasoning tool"},
                {"name": "filesystem", "description": "File system access"},
                {"name": "other-tool", "description": "Other functionality"},
            ]

            test_file = self.repo_root / "test_tools.json"
            with open(test_file, "w") as f:
                json.dump({"tools": test_tools}, f)

            # Run booster
            result = subprocess.run(
                [
                    sys.executable,
                    str(booster_script),
                    str(test_file),
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            # Clean up
            test_file.unlink()

            if result.returncode == 0:
                print("✅ Sequential thinking booster test passed")

                # Check if sequential thinking is boosted
                output_file = self.repo_root / "boosted_tools.json"
                if output_file.exists():
                    with open(output_file) as f:
                        boosted_data = json.load(f)

                    boosted_tools = boosted_data.get("tools", [])
                    if boosted_tools and "sequential" in boosted_tools[0].get("name", "").lower():
                        print("✅ Sequential thinking properly boosted to top priority")
                        output_file.unlink()
                        return True
                    else:
                        print("❌ Sequential thinking not properly boosted")
                        return False
                else:
                    print("❌ Booster output file not found")
                    return False
            else:
                print(f"❌ Booster test failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False

    def generate_deployment_report(self) -> str:
        """Generate deployment report."""
        validation_results = self.validate_installation()

        report = f"""
# Sequential Thinking Deployment Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Deployment Status
- MCP Configuration: {"PASS" if validation_results.get("mcp_config") else "FAIL"}
- Environment Variables: {"PASS" if validation_results.get("environment") else "FAIL"}
- Tool Installation: {"PASS" if validation_results.get("tools") else "FAIL"}

## Configuration Summary
### MCP Configuration
- Sequential thinking prioritized in server order
- Enhanced environment variables configured
- Token budget: 30,000 tokens
- Max thoughts: 15
- Auto-trigger: enabled

### Environment Variables
- SEQUENTIAL_THINKING_ENABLED=true
- SEQUENTIAL_THINKING_PRIORITY=1
- WINDSURF_TOOL_PREFERENCE=sequential-thinking
- KIMI25_SEQUENTIAL_THINKING=enabled

### Tools Deployed
- sequential_thinking_booster.py
- mcp_usage_tracker.py
- sequential_thinking_workflow.py
- sequential_thinking_templates.py

## Next Steps
1. Restart Windsurf to load new MCP configuration
2. Test sequential thinking with complex Kimi 2.5 tasks
3. Monitor usage with: python tools/monitoring/mcp_usage_tracker.py --report
4. Adjust configuration based on usage patterns

## Rollback Instructions
If issues occur, restore from backup:
```bash
cp .backup/sequential_thinking/user_mcp_config_backup.json C:\\Users\\amita\\.codeium\\windsurf\\mcp_config.json
```
"""

        report_file = self.repo_root / "docs" / "reports" / "sequential_thinking_deployment_report.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ Deployment report saved to: {report_file}")
        return report

    def deploy(self) -> bool:
        """Execute full deployment process."""
        print("🚀 Starting Sequential Thinking MCP Deployment")
        print("=" * 60)

        # Step 1: Create directories
        if not self.create_directories():
            return False

        # Step 2: Backup existing configuration
        if not self.backup_existing_config():
            return False

        # Step 3: Apply MCP configuration
        if not self.apply_mcp_configuration():
            return False

        # Step 4: Setup environment
        if not self.setup_environment():
            return False

        # Step 5: Validate installation
        print("\n🔍 Validating installation...")
        validation_results = self.validate_installation()

        # Step 6: Run tests
        print("\n🧪 Running tests...")
        tests_passed = self.run_tests()

        # Step 7: Generate report
        print("\n📋 Generating deployment report...")
        report = self.generate_deployment_report()

        # Summary
        all_passed = all(validation_results.values()) and tests_passed

        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 Sequential Thinking deployment completed successfully!")
            print("\n📝 Next Steps:")
            print("1. Restart Windsurf to load the new configuration")
            print("2. Test with a complex Kimi 2.5 task")
            print("3. Monitor usage with the provided tools")
        else:
            print("❌ Deployment completed with issues")
            print("Please check the validation results above")

        print("\n📄 Full report: docs/reports/sequential_thinking_deployment_report.md")

        return all_passed


def main():
    """Main deployment function."""
    if len(sys.argv) > 1:
        repo_path = Path(sys.argv[1])
    else:
        repo_path = Path.cwd()

    deployer = SequentialThinkingDeployer(repo_path)
    success = deployer.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
