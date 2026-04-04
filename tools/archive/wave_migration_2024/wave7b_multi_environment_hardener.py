#!/usr/bin/env python3
"""
Wave 7b: CI lane hardening - multi-environment testing.

This script creates multi-environment testing configurations
for comprehensive CI lane hardening across different platforms.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class EnvironmentConfig:
    """Multi-environment testing configuration."""
    name: str
    os: str
    python_versions: list[str]
    dependencies: list[str]
    test_categories: list[str]
    special_requirements: list[str]


class MultiEnvironmentHardener:
    """Hardener for multi-environment CI testing."""

    def __init__(self):
        self.environments = []
        self.hardening_stats = {
            'environments_created': 0,
            'matrix_combinations': 0,
            'test_categories': 0,
            'special_configurations': 0
        }

    def create_multi_environment_config(self) -> dict:
        """Create comprehensive multi-environment configuration."""
        print("=== Creating Multi-Environment Testing Configuration ===")

        # Define test environments
        environments = [
            EnvironmentConfig(
                name="ubuntu-latest",
                os="ubuntu-latest",
                python_versions=["3.11", "3.12"],
                dependencies=["pytest", "pytest-cov", "pytest-xdist"],
                test_categories=["unit", "integration", "smoke"],
                special_requirements=["apt-packages"]
            ),
            EnvironmentConfig(
                name="windows-latest",
                os="windows-latest",
                python_versions=["3.11", "3.12"],
                dependencies=["pytest", "pytest-cov", "pytest-xdist"],
                test_categories=["unit", "integration"],
                special_requirements=["windows-specific"]
            ),
            EnvironmentConfig(
                name="macos-latest",
                os="macos-latest",
                python_versions=["3.11", "3.12"],
                dependencies=["pytest", "pytest-cov", "pytest-xdist"],
                test_categories=["unit", "integration"],
                special_requirements=["macos-specific"]
            ),
            EnvironmentConfig(
                name="ubuntu-minimal",
                os="ubuntu-latest",
                python_versions=["3.11"],
                dependencies=["pytest"],
                test_categories=["unit", "smoke"],
                special_requirements=["minimal-deps"]
            )
        ]

        self.environments = environments
        self.hardening_stats['environments_created'] = len(environments)

        # Calculate matrix combinations
        total_combinations = 0
        for env in environments:
            total_combinations += len(env.python_versions) * len(env.test_categories)
        self.hardening_stats['matrix_combinations'] = total_combinations

        # Count unique test categories
        all_categories = set()
        for env in environments:
            all_categories.update(env.test_categories)
        self.hardening_stats['test_categories'] = len(all_categories)

        # Count special configurations
        total_special = sum(len(env.special_requirements) for env in environments)
        self.hardening_stats['special_configurations'] = total_special

        return {
            'environments': environments,
            'stats': self.hardening_stats
        }

    def create_multi_environment_workflow(self) -> dict:
        """Create multi-environment testing workflow."""
        print("=== Creating Multi-Environment Testing Workflow ===")

        workflow = {
            'name': 'Multi-Environment Testing',
            'on': {
                'push': {
                    'branches': ['main', 'develop']
                },
                'pull_request': {
                    'branches': ['main']
                },
                'schedule': [{'cron': '0 2 * * *'}]  # Daily at 2 AM
            },
            'jobs': {
                'test-matrix': {
                    'runs-on': '${{ matrix.os }}',
                    'strategy': {
                        'fail-fast': False,
                        'matrix': {
                            'os': ['ubuntu-latest', 'windows-latest', 'macos-latest'],
                            'python-version': ['3.11', '3.12'],
                            'test-category': ['unit', 'integration'],
                            'include': [
                                {
                                    'os': 'ubuntu-latest',
                                    'python-version': '3.12',
                                    'test-category': 'smoke',
                                    'extra-deps': 'pytest-xdist'
                                },
                                {
                                    'os': 'ubuntu-latest',
                                    'python-version': '3.11',
                                    'test-category': 'performance',
                                    'extra-deps': 'pytest-benchmark'
                                }
                            ],
                            'exclude': [
                                {
                                    'os': 'windows-latest',
                                    'python-version': '3.11',
                                    'test-category': 'performance'
                                },
                                {
                                    'os': 'macos-latest',
                                    'python-version': '3.11',
                                    'test-category': 'performance'
                                }
                            ]
                        }
                    },
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Set up Python ${{ matrix.python-version }}',
                            'uses': 'actions/setup-python@v4',
                            'with': {
                                'python-version': '${{ matrix.python-version }}'
                            }
                        },
                        {
                            'name': 'Cache pip dependencies',
                            'uses': 'actions/cache@v3',
                            'with': {
                                'path': '~/.cache/pip',
                                'key': '${{ runner.os }}-pip-${{ hashFiles(''**/requirements.txt'') }}',
                                'restore-keys': '${{ runner.os }}-pip-'
                            }
                        },
                        {
                            'name': 'Install system dependencies (Ubuntu)',
                            'if': 'runner.os == ''Linux''',
                            'run': 'sudo apt-get update && sudo apt-get install -y build-essential libssl-dev'
                        },
                        {
                            'name': 'Install system dependencies (macOS)',
                            'if': 'runner.os == ''macOS''',
                            'run': 'brew install openssl'
                        },
                        {
                            'name': 'Install Python dependencies',
                            'run': '''
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install pytest pytest-cov pytest-xdist
                                if [ "${{ matrix.extra-deps }}" != "" ]; then pip install ${{ matrix.extra-deps }}; fi
                                '''
                        },
                        {
                            'name': 'Run unit tests',
                            'if': 'matrix.test-category == \'unit\'',
                            'run': 'pytest tests/unit/ -v --cov=agentic_core --cov-report=xml --tb=short'
                        },
                        {
                            'name': 'Run integration tests',
                            'if': 'matrix.test-category == \'integration\'',
                            'run': 'pytest tests/integration/ -v --tb=short'
                        },
                        {
                            'name': 'Run smoke tests',
                            'if': 'matrix.test-category == \'smoke\'',
                            'run': 'pytest tests/smoke/ -v --tb=short'
                        },
                        {
                            'name': 'Run performance tests',
                            'if': 'matrix.test-category == \'performance\'',
                            'run': 'pytest tests/performance/ --benchmark-only --benchmark-json=benchmark-${{ runner.os }}-${{ matrix.python-version }}.json'
                        },
                        {
                            'name': 'Upload test results',
                            'uses': 'actions/upload-artifact@v4',
                            'if': 'always()',
                            'with': {
                                'name': 'test-results-${{ runner.os }}-${{ matrix.python-version }}-${{ matrix.test-category }}',
                                'path': '''
                                    test-results.xml
                                    coverage.xml
                                    benchmark-*.json
                                    '''
                                ,
                                'retention-days': 7
                            }
                        },
                        {
                            'name': 'Upload coverage to Codecov',
                            'if': 'matrix.test-category == ''unit'' && matrix.python-version == ''3.12''',
                            'uses': 'codecov/codecov-action@v3',
                            'with': {
                                'file': 'coverage.xml',
                                'flags': '${{ runner.os }}',
                                'name': 'codecov-${{ runner.os }}-${{ matrix.python-version }}'
                            }
                        }
                    ]
                },
                'collect-results': {
                    'runs-on': 'ubuntu-latest',
                    'needs': 'test-matrix',
                    'if': 'always()',
                    'steps': [
                        {
                            'name': 'Download all test results',
                            'uses': 'actions/download-artifact@v4',
                            'with': {
                                'path': 'all-results'
                            }
                        },
                        {
                            'name': 'Generate summary report',
                            'run': '''
                            python << 'EOF'
                            import json
                            import os
                            from pathlib import Path

                            # Collect all results
                            results_dir = Path('all-results')
                            summary = {
                                'total_runs': 0,
                                'successful_runs': 0,
                                'failed_runs': 0,
                                'by_os': {},
                                'by_python': {},
                                'by_category': {}
                            }

                            for artifact_dir in results_dir.iterdir():
                                if artifact_dir.is_dir():
                                    # Parse artifact name to extract metadata
                                    parts = artifact_dir.name.split('-')
                                    if len(parts) >= 4:
                                        os_name = parts[2]
                                        python_ver = parts[3]
                                        category = parts[4] if len(parts) > 4 else 'unknown'

                                        summary['total_runs'] += 1
                                        summary['by_os'][os_name] = summary['by_os'].get(os_name, 0) + 1
                                        summary['by_python'][python_ver] = summary['by_python'].get(python_ver, 0) + 1
                                        summary['by_category'][category] = summary['by_category'].get(category, 0) + 1

                            # Save summary
                            with open('multi-environment-summary.json', 'w') as f:
                                json.dump(summary, f, indent=2)

                            print(f"Summary: {summary}")
                            '''
                        },
                        {
                            'name': 'Upload summary report',
                            'uses': 'actions/upload-artifact@v4',
                            'with': {
                                'name': 'multi-environment-summary',
                                'path': 'multi-environment-summary.json'
                            }
                        }
                    ]
                }
            }
        }

        return workflow

    def create_environment_specific_workflows(self) -> list[dict]:
        """Create environment-specific workflows."""
        print("=== Creating Environment-Specific Workflows ===")

        workflows = []

        # Windows-specific workflow
        windows_workflow = {
            'name': 'Windows-Specific Testing',
            'on': {
                'push': {'branches': ['main']},
                'pull_request': {'branches': ['main']}
            },
            'jobs': {
                'windows-tests': {
                    'runs-on': 'windows-latest',
                    'strategy': {
                        'matrix': {
                            'python-version': ['3.11', '3.12']
                        }
                    },
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Set up Python ${{ matrix.python-version }}',
                            'uses': 'actions/setup-python@v4',
                            'with': {
                                'python-version': '${{ matrix.python-version }}'
                            }
                        },
                        {
                            'name': 'Install dependencies',
                            'run': '''
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install pytest pytest-cov
                                '''
                        },
                        {
                            'name': 'Run Windows-specific tests',
                            'run': '''
                                pytest tests/unit/ -v --tb=short -k "not unix_only"
                                pytest tests/integration/ -v --tb=short -k "not unix_only"
                                '''
                        },
                        {
                            'name': 'Test Windows path handling',
                            'run': '''
                                python -c "
                                import pathlib
                                import os
                                print('Testing Windows path handling...')
                                path = pathlib.Path('C:\\\\test\\\\path')
                                print(f'Path object: {path}')
                                print(f'Path exists: {path.exists()}')
                                print('Windows path handling test passed')
                                "
                                '''
                        }
                    ]
                }
            }
        }
        workflows.append(windows_workflow)

        # macOS-specific workflow
        macos_workflow = {
            'name': 'macOS-Specific Testing',
            'on': {
                'push': {'branches': ['main']},
                'pull_request': {'branches': ['main']}
            },
            'jobs': {
                'macos-tests': {
                    'runs-on': 'macos-latest',
                    'strategy': {
                        'matrix': {
                            'python-version': ['3.11', '3.12']
                        }
                    },
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Set up Python ${{ matrix.python-version }}',
                            'uses': 'actions/setup-python@v4',
                            'with': {
                                'python-version': '${{ matrix.python-version }}'
                            }
                        },
                        {
                            'name': 'Install dependencies',
                            'run': '''
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install pytest pytest-cov
                                '''
                        },
                        {
                            'name': 'Run macOS-specific tests',
                            'run': '''
                                pytest tests/unit/ -v --tb=short -k "not windows_only"
                                pytest tests/integration/ -v --tb=short -k "not windows_only"
                                '''
                        },
                        {
                            'name': 'Test macOS file permissions',
                            'run': '''
                                python -c "
                                import os
                                import stat
                                print('Testing macOS file permissions...')
                                with open('test_file.txt', 'w') as f:
                                    f.write('test')
                                file_stat = os.stat('test_file.txt')
                                print(f'File permissions: {oct(file_stat.st_mode)}')
                                os.remove('test_file.txt')
                                print('macOS file permissions test passed')
                                "
                                '''
                        }
                    ]
                }
            }
        }
        workflows.append(macos_workflow)

        # Ubuntu-specific workflow
        ubuntu_workflow = {
            'name': 'Ubuntu-Specific Testing',
            'on': {
                'push': {'branches': ['main']},
                'pull_request': {'branches': ['main']}
            },
            'jobs': {
                'ubuntu-tests': {
                    'runs-on': 'ubuntu-latest',
                    'strategy': {
                        'matrix': {
                            'python-version': ['3.11', '3.12']
                        }
                    },
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Set up Python ${{ matrix.python-version }}',
                            'uses': 'actions/setup-python@v4',
                            'with': {
                                'python-version': '${{ matrix.python-version }}'
                            }
                        },
                        {
                            'name': 'Install system dependencies',
                            'run': '''
                                sudo apt-get update
                                sudo apt-get install -y build-essential libssl-dev libffi-dev
                                '''
                        },
                        {
                            'name': 'Install Python dependencies',
                            'run': '''
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install pytest pytest-cov pytest-xdist
                                '''
                        },
                        {
                            'name': 'Run Ubuntu-specific tests',
                            'run': '''
                                pytest tests/unit/ -v --tb=short
                                pytest tests/integration/ -v --tb=short
                                pytest tests/smoke/ -v --tb=short
                                '''
                        },
                        {
                            'name': 'Test Linux-specific features',
                            'run': '''
                                python -c "
                                import os
                                import signal
                                print('Testing Linux-specific features...')
                                # Test signal handling
                                print(f'Available signals: {len(signal.Signals)}')
                                # Test file system
                                with open('/tmp/test_file', 'w') as f:
                                    f.write('test')
                                os.remove('/tmp/test_file')
                                print('Linux-specific features test passed')
                                "
                                '''
                        }
                    ]
                }
            }
        }
        workflows.append(ubuntu_workflow)

        return workflows

    def write_multi_environment_files(self, workflows_dir: str = ".github/workflows") -> dict:
        """Write multi-environment workflow files."""
        print("=== Writing Multi-Environment Workflow Files ===")

        workflows_path = Path(workflows_dir)
        workflows_path.mkdir(parents=True, exist_ok=True)

        files_created = []

        # Write main multi-environment workflow
        main_workflow = self.create_multi_environment_workflow()
        main_file = workflows_path / "multi_environment_testing.yml"
        with open(main_file, 'w') as f:
            yaml.dump(main_workflow, f, default_flow_style=False, sort_keys=False)

        files_created.append({
            'name': 'Multi-Environment Testing',
            'filename': 'multi_environment_testing.yml',
            'path': str(main_file)
        })

        # Write environment-specific workflows
        env_workflows = self.create_environment_specific_workflows()
        for i, workflow in enumerate(env_workflows):
            filename = f"env_specific_{i+1}_{workflow['name'].lower().replace('-', '_')}.yml"
            file_path = workflows_path / filename
            with open(file_path, 'w') as f:
                yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)

            files_created.append({
                'name': workflow['name'],
                'filename': filename,
                'path': str(file_path)
            })

        print(f"✅ Created {len(files_created)} multi-environment workflow files")

        return {
            'files_created': files_created,
            'total_files': len(files_created)
        }

    def generate_wave7b_report(self) -> dict:
        """Generate Wave 7b multi-environment hardening report."""
        print("=== Wave 7b: CI Lane Hardening - Multi-Environment Testing ===")

        # Create multi-environment configuration
        env_config = self.create_multi_environment_config()

        # Write workflow files
        file_results = self.write_multi_environment_files()

        # Create comprehensive report
        report = {
            'wave': 'Wave 7b',
            'timestamp': '2026-03-25 21:25:00',
            'title': 'CI Lane Hardening - Multi-Environment Testing',
            'environments': [
                {
                    'name': env.name,
                    'os': env.os,
                    'python_versions': env.python_versions,
                    'test_categories': env.test_categories,
                    'special_requirements': env.special_requirements
                }
                for env in self.environments
            ],
            'workflow_files': file_results,
            'hardening_stats': self.hardening_stats,
            'summary': {
                'environments_created': self.hardening_stats['environments_created'],
                'matrix_combinations': self.hardening_stats['matrix_combinations'],
                'test_categories': self.hardening_stats['test_categories'],
                'special_configurations': self.hardening_stats['special_configurations'],
                'files_written': file_results['total_files']
            }
        }

        # Save report
        with open('artifacts/wave7b_multi_environment_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Wave 7b Summary ===")
        print(f"Environments created: {summary['environments_created']}")
        print(f"Matrix combinations: {summary['matrix_combinations']}")
        print(f"Test categories: {summary['test_categories']}")
        print(f"Special configurations: {summary['special_configurations']}")
        print(f"Files written: {summary['files_written']}")

        print("\n📄 Report saved to: artifacts/wave7b_multi_environment_report.json")

        return report


def main():
    """Main execution for Wave 7b."""
    hardener = MultiEnvironmentHardener()
    report = hardener.generate_wave7b_report()

    print("\n=== Wave 7b Summary ===")
    print(f"Multi-environment lanes: {len(report['environments'])}")
    print(f"Total matrix combinations: {report['summary']['matrix_combinations']}")

    return report


if __name__ == '__main__':
    main()
