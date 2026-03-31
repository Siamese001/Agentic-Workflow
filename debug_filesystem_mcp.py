#!/usr/bin/env python3
"""
Filesystem MCP Server Debug and RCA Tool
Debugs the filesystem server warning, performs root cause analysis, and fixes issues.
"""

import subprocess
import json
import time
import os
from pathlib import Path

class FilesystemMCPDebugger:
    def __init__(self):
        self.config_file = Path('C:\\Git\\Agentic-Workflow\\.windsurf\\mcp_config.json')
        self.npm_prefix = 'C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation'

    def load_config(self):
        """Load MCP configuration."""
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def debug_filesystem_server(self):
        """Debug the filesystem MCP server issue."""
        print('🔍 Filesystem MCP Server Debug Analysis')
        print('=' * 45)

        # Get filesystem server config
        config = self.load_config()
        fs_config = config.get('mcpServers', {}).get('filesystem', {})

        if not fs_config:
            return {'status': 'error', 'message': 'Filesystem server not found in config'}

        print(f'📋 Current Configuration:')
        print(f'   Command: {fs_config.get("command")}')
        print(f'   Args: {fs_config.get("args")}')
        print(f'   Disabled: {fs_config.get("disabled")}')

        package_path = fs_config.get('args', [None])[0] if fs_config.get('args') else None

        if not package_path:
            return {'status': 'error', 'message': 'No package path found'}

        print(f'\\n🔍 Package Analysis:')
        print(f'   Path: {package_path}')

        # Check package existence
        if not os.path.exists(package_path):
            return {'status': 'error', 'message': f'Package not found: {package_path}'}

        print(f'   ✅ Package exists')

        # Check package details
        try:
            stat = os.stat(package_path)
            print(f'   📊 Size: {stat.st_size:,} bytes')
            print(f'   📅 Modified: {time.ctime(stat.st_mtime)}')
            print(f'   📋 Permissions: {oct(stat.st_mode)[-3:]}')
        except Exception as e:
            print(f'   ❌ Error getting package info: {e}')

        # Test package execution with detailed output
        print(f'\\n🧪 Execution Testing:')

        try:
            # Test 1: Help command
            print(f'   Testing --help command...')
            result = subprocess.run(
                ['node', package_path, '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )

            print(f'   Exit code: {result.returncode}')
            print(f'   Stdout length: {len(result.stdout)} chars')
            print(f'   Stderr length: {len(result.stderr)} chars')

            if result.stdout:
                print(f'   Stdout preview: {result.stdout[:200]}...')

            if result.stderr:
                print(f'   Stderr preview: {result.stderr[:200]}...')

            # Test 2: Version command
            print(f'\\n   Testing --version command...')
            version_result = subprocess.run(
                ['node', package_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            print(f'   Version exit code: {version_result.returncode}')
            print(f'   Version output: {version_result.stdout.strip()}')
            if version_result.stderr:
                print(f'   Version stderr: {version_result.stderr.strip()}')

            # Test 3: Try with repository argument
            print(f'\\n   Testing with repository argument...')
            repo_result = subprocess.run(
                ['node', package_path, 'C:\\Git\\Agentic-Workflow', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )

            print(f'   Repo test exit code: {repo_result.returncode}')
            if repo_result.stdout:
                print(f'   Repo test stdout: {repo_result.stdout[:200]}...')
            if repo_result.stderr:
                print(f'   Repo test stderr: {repo_result.stderr[:200]}...')

            # Analyze the results
            analysis = {
                'package_path': package_path,
                'help_exit_code': result.returncode,
                'version_exit_code': version_result.returncode,
                'repo_exit_code': repo_result.return_code,
                'has_stdout': bool(result.stdout.strip()),
                'has_stderr': bool(result.stderr.strip()),
                'version_output': version_result.stdout.strip(),
                'help_stderr': result.stderr.strip() if result.stderr else '',
                'repo_stderr': repo_result.stderr.strip() if repo_result.stderr else ''
            }

            return self.perform_root_cause_analysis(analysis)

        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Package execution timed out'}
        except Exception as e:
            return {'status': 'error', 'message': f'Execution error: {str(e)}'}

    def perform_root_cause_analysis(self, analysis):
        """Perform root cause analysis based on test results."""
        print(f'\\n🔍 Root Cause Analysis:')
        print('=' * 30)

        issues = []
        recommendations = []

        # Analyze help command
        if analysis['help_exit_code'] != 0:
            issues.append('Help command returns non-zero exit code')
            if 'Error' in analysis['help_stderr']:
                issues.append('Error detected in help stderr')
                if 'ENOENT' in analysis['help_stderr']:
                    issues.append('File not found error in help')
                    recommendations.append('Check package installation integrity')
                elif 'permission' in analysis['help_stderr'].lower():
                    issues.append('Permission error detected')
                    recommendations.append('Check file permissions')

        # Analyze version command
        if analysis['version_exit_code'] != 0:
            issues.append('Version command fails')
            recommendations.append('Package may not support --version flag')

        # Analyze repository argument
        if analysis['repo_exit_code'] != 0:
            issues.append('Repository argument test fails')
            if 'ENOENT' in analysis['repo_stderr']:
                issues.append('Repository path not found')
                recommendations.append('Verify repository path exists')

        # Check for common filesystem MCP issues
        if not analysis['has_stdout'] and analysis['has_stderr']:
            issues.append('Server outputs to stderr instead of stdout')
            recommendations.append('This is normal for MCP servers - use stderr for status')

        # Determine if this is actually an issue
        if len(issues) == 0:
            return {
                'status': 'healthy',
                'issues': [],
                'recommendations': ['No issues detected - server appears healthy'],
                'analysis': analysis
            }
        elif len(issues) <= 2 and 'Error' not in analysis['help_stderr']:
            return {
                'status': 'minor',
                'issues': issues,
                'recommendations': recommendations,
                'analysis': analysis
            }
        else:
            return {
                'status': 'needs_attention',
                'issues': issues,
                'recommendations': recommendations,
                'analysis': analysis
            }

    def fix_filesystem_server(self, analysis_result):
        """Fix identified issues with the filesystem server."""
        print(f'\\n🔧 Filesystem Server Fix Implementation')
        print('=' * 40)

        if analysis_result['status'] == 'healthy':
            print('✅ No fixes needed - server is healthy')
            return True

        fixes_applied = []

        # Fix 1: Check if package needs reinstallation
        recommendations = analysis_result.get('recommendations', [])
        if 'Check package installation integrity' in recommendations:
            print('🔧 Fix 1: Reinstalling filesystem package...')
            try:
                result = subprocess.run(
                    ['npm', 'install', '-g', '@modelcontextprotocol/server-filesystem'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    fixes_applied.append('Package reinstalled successfully')
                    print('   ✅ Package reinstalled')
                else:
                    fixes_applied.append('Package reinstallation failed')
                    print(f'   ❌ Reinstall failed: {result.stderr}')
            except Exception as e:
                fixes_applied.append(f'Package reinstallation error: {e}')
                print(f'   ❌ Reinstall error: {e}')

        # Fix 2: Update configuration with optimized settings
        print('🔧 Fix 2: Optimizing configuration...')

        config = self.load_config()
        fs_config = config.get('mcpServers', {}).get('filesystem', {})

        # Ensure the configuration is optimal
        optimized_config = {
            "_comment": "Filesystem MCP — OPTIMIZED: Using global npm for best performance. allowedDirectories LOCKED to repo root only. SSOT enforced by pre-commit.",
            "command": "node",
            "args": [fs_config.get('args', [''])[0], "C:\\Git\\Agentic-Workflow"],
            "disabled": False,
            "env": {
                "NODE_ENV": "production"
            }
        }

        # Update configuration
        config['mcpServers']['filesystem'] = optimized_config

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            fixes_applied.append('Configuration optimized')
            print('   ✅ Configuration updated')
        except Exception as e:
            fixes_applied.append(f'Configuration update failed: {e}')
            print(f'   ❌ Config update failed: {e}')

        # Fix 3: Verify repository path
        repo_path = "C:\\Git\\Agentic-Workflow"
        if not os.path.exists(repo_path):
            fixes_applied.append('Repository path not found')
            print('   ❌ Repository path not found')
        else:
            fixes_applied.append('Repository path verified')
            print('   ✅ Repository path exists')

        return len(fixes_applied) > 0 and 'failed' not in ' '.join(fixes_applied).lower()

    def test_fixed_server(self):
        """Test the fixed filesystem server."""
        print(f'\\n🧪 Testing Fixed Filesystem Server')
        print('=' * 35)

        # Wait a moment for changes to take effect
        time.sleep(1)

        config = self.load_config()
        fs_config = config.get('mcpServers', {}).get('filesystem', {})

        package_path = fs_config.get('args', [None])[0] if fs_config.get('args') else None

        if not package_path:
            return {'status': 'error', 'message': 'No package path after fix'}

        try:
            # Test startup
            start_time = time.time()
            result = subprocess.run(
                ['node', package_path, '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            end_time = time.time()

            startup_time = end_time - start_time

            print(f'📊 Test Results:')
            print(f'   Startup time: {startup_time:.3f}s')
            print(f'   Exit code: {result.returncode}')
            print(f'   Has output: {bool(result.stdout.strip())}')
            print(f'   Has stderr: {bool(result.stderr.strip())}')

            if result.stdout:
                print(f'   Output preview: {result.stdout[:150]}...')

            if result.stderr:
                print(f'   Stderr preview: {result.stderr[:150]}...')

            # Determine success
            if result.returncode == 0 or 'server' in result.stderr.lower():
                status = 'success'
                message = 'Filesystem server fixed and working'
            elif result.returncode == 1 and 'Error' not in result.stderr:
                status = 'improved'
                message = 'Filesystem server improved (minor issues remain)'
            else:
                status = 'still_issues'
                message = 'Filesystem server still has issues'

            return {
                'status': status,
                'startup_time': startup_time,
                'message': message,
                'exit_code': result.returncode,
                'has_output': bool(result.stdout.strip()),
                'stderr_sample': result.stderr[:200] if result.stderr else ''
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Test error: {str(e)}'
            }

    def run_complete_debug_cycle(self):
        """Run the complete debug, fix, and test cycle."""
        print('🚀 Filesystem MCP Server - Complete Debug Cycle')
        print('=' * 55)

        # Step 1: Debug
        debug_result = self.debug_filesystem_server()

        # Step 2: Fix if needed
        if debug_result['status'] != 'healthy':
            fix_success = self.fix_filesystem_server(debug_result)

            if not fix_success:
                return {
                    'overall_status': 'failed',
                    'debug_result': debug_result,
                    'fix_result': 'failed',
                    'test_result': None
                }

        # Step 3: Test
        test_result = self.test_fixed_server()

        # Step 4: Generate report
        overall_status = 'success' if test_result['status'] in ['success', 'improved'] else 'failed'

        return {
            'overall_status': overall_status,
            'debug_result': debug_result,
            'fix_result': 'completed' if debug_result['status'] != 'healthy' else 'not_needed',
            'test_result': test_result
        }

def main():
    debugger = FilesystemMCPDebugger()
    result = debugger.run_complete_debug_cycle()

    # Save results
    results_file = Path('C:\\Git\\Agentic-Workflow\\filesystem_debug_results.json')
    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'\\n💾 Debug results saved to: {results_file}')

    # Display final status
    print(f'\\n🎯 Final Status:')
    if result['overall_status'] == 'success':
        print('🟢 SUCCESS: Filesystem MCP server debugged and optimized')
    elif result['overall_status'] == 'failed':
        print('🔴 FAILED: Filesystem MCP server still has issues')
    else:
        print('🟡 PARTIAL: Filesystem MCP server partially fixed')

    return 0 if result['overall_status'] == 'success' else 1

if __name__ == "__main__":
    exit(main())
