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
    test_categories: list[str]


class MultiEnvironmentHardener:
    """Hardener for multi-environment CI testing."""

    def __init__(self):
        self.environments = []
        self.hardening_stats = {
            'environments_created': 0,
            'matrix_combinations': 0,
            'test_categories': 0
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
                test_categories=["unit", "integration", "smoke"]
            ),
            EnvironmentConfig(
                name="windows-latest",
                os="windows-latest",
                python_versions=["3.11", "3.12"],
                test_categories=["unit", "integration"]
            ),
            EnvironmentConfig(
                name="macos-latest",
                os="macos-latest",
                python_versions=["3.11", "3.12"],
                test_categories=["unit", "integration"]
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
                'push': {'branches': ['main', 'develop']},
                'pull_request': {'branches': ['main']}
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
                                    'test-category': 'smoke'
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
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt pytest pytest-cov'
                        },
                        {
                            'name': 'Run unit tests',
                            'if': 'matrix.test-category == \'unit\'',
                            'run': 'pytest tests/unit/ -v --cov=agentic_core --cov-report=xml'
                        },
                        {
                            'name': 'Run integration tests',
                            'if': 'matrix.test-category == \'integration\'',
                            'run': 'pytest tests/integration/ -v'
                        },
                        {
                            'name': 'Run smoke tests',
                            'if': 'matrix.test-category == \'smoke\'',
                            'run': 'pytest tests/smoke/ -v'
                        },
                        {
                            'name': 'Upload test results',
                            'uses': 'actions/upload-artifact@v4',
                            'if': 'always()',
                            'with': {
                                'name': 'test-results-${{ runner.os }}-${{ matrix.python-version }}-${{ matrix.test-category }}',
                                'path': 'test-results.xml,coverage.xml'
                            }
                        }
                    ]
                }
            }
        }

        return workflow

    def generate_wave7b_report(self) -> dict:
        """Generate Wave 7b multi-environment hardening report."""
        print("=== Wave 7b: CI Lane Hardening - Multi-Environment Testing ===")

        # Create multi-environment configuration
        env_config = self.create_multi_environment_config()

        # Write workflow files
        workflow = self.create_multi_environment_workflow()
        workflows_path = Path(".github/workflows")
        workflows_path.mkdir(parents=True, exist_ok=True)

        # Write main multi-environment workflow
        main_file = workflows_path / "multi_environment_testing.yml"
        with open(main_file, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)

        files_created = [{
            'name': 'Multi-Environment Testing',
            'filename': 'multi_environment_testing.yml',
            'path': str(main_file)
        }]

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
                    'test_categories': env.test_categories
                }
                for env in self.environments
            ],
            'workflow_files': files_created,
            'hardening_stats': self.hardening_stats,
            'summary': {
                'environments_created': self.hardening_stats['environments_created'],
                'matrix_combinations': self.hardening_stats['matrix_combinations'],
                'test_categories': self.hardening_stats['test_categories'],
                'files_written': len(files_created)
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
