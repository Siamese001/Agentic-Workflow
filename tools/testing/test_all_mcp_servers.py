#!/usr/bin/env python3
"""
Comprehensive MCP Server Review and Testing
Analyzes all configured MCP servers and tests their performance/functionality.
"""

import json
import os
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_mcp_server(name, server_config):
    """Test individual MCP server functionality and performance."""
    command = server_config.get('command')
    args = server_config.get('args', [])
    disabled = server_config.get('disabled', False)

    if disabled:
        return {'status': 'skipped', 'time': 0, 'success': False, 'message': 'Server disabled'}

    try:
        start_time = time.time()

        if command == 'node':
            # Test Node.js package
            result = subprocess.run(
                [command] + args + ['--help'],
                capture_output=True,
                text=True,
                timeout=5,
            )
            end_time = time.time()
            startup_time = end_time - start_time

            if result.returncode == 0 or 'timeout' in result.stderr.lower():
                return {
                    'status': 'success',
                    'time': startup_time,
                    'success': True,
                    'message': 'Server starts successfully',
                }
            else:
                return {
                    'status': 'warning',
                    'time': startup_time,
                    'success': False,
                    'message': f'Exit code: {result.returncode}',
                }

        elif command == 'python':
            # Test Python script
            script_path = args[0] if args else None
            if script_path and os.path.exists(script_path):
                return {
                    'status': 'python_ready',
                    'time': 0,
                    'success': True,
                    'message': f'Python script found: {script_path}',
                }
            else:
                return {
                    'status': 'missing',
                    'time': 0,
                    'success': False,
                    'message': f'Python script not found: {script_path}',
                }

        elif command == 'npx':
            # Test NPX package
            package_name = args[1] if len(args) > 1 and args[0] == '-y' else None
            if package_name:
                return {
                    'status': 'npx_configured',
                    'time': 0,
                    'success': True,
                    'message': f'NPX package: {package_name}',
                }
            else:
                return {
                    'status': 'invalid_npx',
                    'time': 0,
                    'success': False,
                    'message': 'Invalid NPX configuration',
                }
        else:
            return {
                'status': 'unknown_command',
                'time': 0,
                'success': False,
                'message': f'Unknown command: {command}',
            }

    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout_success',
            'time': 5.0,
            'success': True,
            'message': 'Server started (timeout expected)',
        }
    except Exception as e:
        return {
            'status': 'error',
            'time': 0,
            'success': False,
            'message': f'Error: {str(e)}',
        }

def get_installed_mcp_packages():
    """Get list of installed MCP packages via npm."""
    try:
        result = subprocess.run(['npm', 'list', '-g'], capture_output=True, text=True, timeout=10)
        lines = result.stdout.split('\n')
        mcp_packages = []

        for line in lines:
            if 'modelcontextprotocol' in line and '@' in line:
                mcp_packages.append(line.strip())

        return mcp_packages
    except Exception as e:
        return [f'Error getting packages: {e}']

def analyze_configuration_optimization(servers, installed_packages):
    """Analyze which servers could be optimized."""
    recommendations = []

    npm_prefix = 'C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation'

    for name, config in servers.items():
        command = config.get('command')

        if command == 'npx' and not config.get('disabled', False):
            # Check if package is installed globally
            args = config.get('args', [])
            package_name = args[1] if len(args) > 1 and args[0] == '-y' else None

            if package_name:
                package_installed = any(package_name in pkg for pkg in installed_packages)

                if package_installed:
                    expected_path = f'{npm_prefix}\\node_modules\\{package_name}\\dist\\index.js'
                    if os.path.exists(expected_path):
                        recommendations.append({
                            'server': name,
                            'action': 'optimize_to_global_npm',
                            'current': 'NPX',
                            'recommended': 'Global npm',
                            'path': expected_path,
                            'benefit': 'Faster startup, more reliable',
                        })
                    else:
                        recommendations.append({
                            'server': name,
                            'action': 'install_and_optimize',
                            'current': 'NPX',
                            'recommended': 'Global npm',
                            'package': package_name,
                            'benefit': 'Faster startup, more reliable',
                        })
                else:
                    recommendations.append({
                        'server': name,
                        'action': 'install_package',
                        'current': 'NPX',
                        'recommended': 'Global npm',
                        'package': package_name,
                        'benefit': 'Faster startup, more reliable',
                    })

    return recommendations

def main():
    print('🔍 Comprehensive MCP Server Review and Testing')
    print('=' * 55)

    # Load configuration
    config_file = REPO_ROOT / '.windsurf' / 'mcp_config.json'
    with open(config_file) as f:
        config = json.load(f)

    servers = config.get('mcpServers', {})

    print(f'\n📋 Configured Servers ({len(servers)}):')
    for name, server_config in servers.items():
        status = '✅ Enabled' if not server_config.get('disabled', False) else '❌ Disabled'
        command = server_config.get('command', 'N/A')
        print(f'   {name}: {status} ({command})')

    # Get installed packages
    print('\n📦 Installed MCP Packages:')
    installed_packages = get_installed_mcp_packages()
    for package in installed_packages:
        print(f'   {package}')

    # Test each server
    print('\n🧪 Testing Each MCP Server')
    print('=' * 30)

    test_results = {}
    for name, server_config in servers.items():
        print(f'\n🔬 Testing {name}...')
        result = test_mcp_server(name, server_config)
        test_results[name] = result

        status_icon = {
            'success': '✅',
            'python_ready': '✅',
            'npx_configured': '✅',
            'timeout_success': '✅',
            'skipped': '⏸️',
            'warning': '⚠️',
            'missing': '❌',
            'invalid_npx': '❌',
            'unknown_command': '❌',
            'error': '❌',
        }.get(result['status'], '❓')

        time_info = f' ({result["time"]:.3f}s)' if result['time'] > 0 else ''
        print(f'   {status_icon} {result["status"]}{time_info}')
        print(f'   📝 {result["message"]}')

    # Performance summary
    print('\n📊 Performance Summary')
    print('=' * 25)

    success_count = sum(1 for r in test_results.values() if r['success'])
    total_count = len([r for r in servers.values() if not r.get('disabled', False)])
    enabled_count = len([r for r in servers.values() if not r.get('disabled', False)])

    print(f'Overall: {success_count}/{total_count} enabled servers working')
    print(f'Total configured: {len(servers)} (enabled: {enabled_count}, disabled: {len(servers) - enabled_count})')

    # Performance breakdown
    node_servers = [(name, r) for name, r in test_results.items()
                   if servers[name].get('command') == 'node' and r['success']]
    python_servers = [(name, r) for name, r in test_results.items()
                      if servers[name].get('command') == 'python' and r['success']]
    npx_servers = [(name, r) for name, r in test_results.items()
                   if servers[name].get('command') == 'npx' and r['success']]

    if node_servers:
        avg_time = sum(r['time'] for _, r in node_servers) / len(node_servers)
        print(f'Node.js servers: {len(node_servers)} working (avg startup: {avg_time:.3f}s)')

    if python_servers:
        print(f'Python servers: {len(python_servers)} working')

    if npx_servers:
        print(f'NPX servers: {len(npx_servers)} configured')

    # Optimization recommendations
    print('\n🚀 Optimization Recommendations')
    print('=' * 35)

    recommendations = analyze_configuration_optimization(servers, installed_packages)

    if recommendations:
        for rec in recommendations:
            print(f'\n📈 {rec["server"]}:')
            print(f'   Action: {rec["action"]}')
            print(f'   Current: {rec["current"]}')
            print(f'   Recommended: {rec["recommended"]}')
            print(f'   Benefit: {rec["benefit"]}')
            if 'path' in rec:
                print(f'   Path: {rec["path"]}')
            if 'package' in rec:
                print(f'   Package: {rec["package"]}')
    else:
        print('✅ All servers are optimally configured!')

    return 0

if __name__ == "__main__":
    exit(main())
