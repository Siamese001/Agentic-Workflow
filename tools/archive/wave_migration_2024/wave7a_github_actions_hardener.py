#!/usr/bin/env python3
"""
Wave 7a: CI lane hardening - GitHub Actions setup.

This script creates comprehensive GitHub Actions workflows
for CI lane hardening and automated test suite validation.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class WorkflowConfig:
    """GitHub Actions workflow configuration."""
    name: str
    description: str
    triggers: list[str]
    jobs: dict[str, dict]
    environment: str | None = None


class GitHubActionsHardener:
    """Hardener for GitHub Actions CI lanes."""

    def __init__(self):
        self.workflows = []
        self.hardening_stats = {
            'workflows_created': 0,
            'jobs_defined': 0,
            'steps_added': 0,
            'environments_configured': 0
        }

    def create_ci_workflows(self) -> dict:
        """Create comprehensive CI workflows."""
        print("=== Creating GitHub Actions CI Workflows ===")

        # Create main CI workflow
        main_ci = self._create_main_ci_workflow()
        self.workflows.append(main_ci)

        # Create validation workflow
        validation_workflow = self._create_validation_workflow()
        self.workflows.append(validation_workflow)

        # Create test suite workflow
        test_suite_workflow = self._create_test_suite_workflow()
        self.workflows.append(test_suite_workflow)

        # Create security workflow
        security_workflow = self._create_security_workflow()
        self.workflows.append(security_workflow)

        # Create performance workflow
        performance_workflow = self._create_performance_workflow()
        self.workflows.append(performance_workflow)

        # Create release workflow
        release_workflow = self._create_release_workflow()
        self.workflows.append(release_workflow)

        return {
            'workflows': self.workflows,
            'stats': self.hardening_stats
        }

    def _create_main_ci_workflow(self) -> WorkflowConfig:
        """Create main CI workflow."""
        workflow = WorkflowConfig(
            name="Main CI Pipeline",
            description="Main continuous integration pipeline with validation",
            triggers=["push", "pull_request"],
            jobs={
                "validate": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.12"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run validation enforcement",
                            "run": "python tools/validation_runner.py"
                        },
                        {
                            "name": "Upload validation report",
                            "uses": "actions/upload-artifact@v4",
                            "if": "always()",
                            "with": {
                                "name": "validation-report",
                                "path": "artifacts/validation_enforcement_report.json"
                            }
                        }
                    ]
                },
                "test": {
                    "runs-on": "ubuntu-latest",
                    "needs": "validate",
                    "strategy": {
                        "matrix": {
                            "python-version": ["3.11", "3.12"]
                        }
                    },
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python ${{ matrix.python-version }}",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "${{ matrix.python-version }}"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run test suite",
                            "run": "pytest tests/ -v --tb=short --junitxml=test-results.xml"
                        },
                        {
                            "name": "Upload test results",
                            "uses": "actions/upload-artifact@v4",
                            "if": "always()",
                            "with": {
                                "name": "test-results-${{ matrix.python-version }}",
                                "path": "test-results.xml"
                            }
                        }
                    ]
                }
            }
        )

        self.hardening_stats['workflows_created'] += 1
        self.hardening_stats['jobs_defined'] += len(workflow.jobs)
        self.hardening_stats['steps_added'] += sum(len(job.get('steps', [])) for job in workflow.jobs.values())

        return workflow

    def _create_validation_workflow(self) -> WorkflowConfig:
        """Create validation-specific workflow."""
        workflow = WorkflowConfig(
            name="Test Suite Validation",
            description="Comprehensive test suite validation and quality checks",
            triggers=["push", "pull_request"],
            jobs={
                "validation-checks": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.12"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run skip pattern validation",
                            "run": "python tools/wave2a_first_party_remover.py --dry-run"
                        },
                        {
                            "name": "Run hollowed test detection",
                            "run": "python tools/wave3a_hollowed_test_restorer.py --scan-only"
                        },
                        {
                            "name": "Run configuration validation",
                            "run": "python tools/wave5a_pytest_config_hardener.py --validate-only"
                        },
                        {
                            "name": "Generate validation summary",
                            "run": "python tools/ci_validation_integration.py"
                        },
                        {
                            "name": "Upload validation artifacts",
                            "uses": "actions/upload-artifact@v4",
                            "if": "always()",
                            "with": {
                                "name": "validation-artifacts",
                                "path": "artifacts/*validation*.json"
                            }
                        }
                    ]
                }
            }
        )

        self.hardening_stats['workflows_created'] += 1
        self.hardening_stats['jobs_defined'] += len(workflow.jobs)
        self.hardening_stats['steps_added'] += sum(len(job.get('steps', [])) for job in workflow.jobs.values())

        return workflow

    def _create_test_suite_workflow(self) -> WorkflowConfig:
        """Create comprehensive test suite workflow."""
        workflow = WorkflowConfig(
            name="Comprehensive Test Suite",
            description="Full test suite execution with coverage and quality metrics",
            triggers=["push", "pull_request", "schedule"],
            jobs={
                "unit-tests": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.12"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt pytest-cov"
                        },
                        {
                            "name": "Run unit tests with coverage",
                            "run": "pytest tests/unit/ -v --cov=agentic_core --cov-report=xml --cov-report=html"
                        },
                        {
                            "name": "Upload coverage to Codecov",
                            "uses": "codecov/codecov-action@v3",
                            "with": {
                                "file": "coverage.xml"
                            }
                        }
                    ]
                },
                "integration-tests": {
                    "runs-on": "ubuntu-latest",
                    "needs": "unit-tests",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.12"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run integration tests",
                            "run": "pytest tests/integration/ -v --tb=short"
                        }
                    ]
                },
                "smoke-tests": {
                    "runs-on": "ubuntu-latest",
                    "needs": "unit-tests",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.12"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run smoke tests",
                            "run": "pytest tests/smoke/ -v --tb=short"
                        }
                    ]
                }
            }
        )

        self.hardening_stats['workflows_created'] += 1
        self.hardening_stats['jobs_defined'] += len(workflow.jobs)
        self.hardening_stats['steps_added'] += sum(len(job.get('steps', [])) for job in workflow.jobs.values())

        return workflow

    def _create_security_workflow(self) -> WorkflowConfig:
        """Create security-focused workflow."""
        workflow = WorkflowConfig(
            name="Security and Quality",
            description="Security scanning and code quality checks",
            triggers=["push", "pull_request", "schedule"],
            jobs={
                "security-scan": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Run Bandit security scan",
                            "run": "pip install bandit && bandit -r agentic_core/ -f json -o bandit-report.json"
                        },
                        {
                            "name": "Run Safety check",
                            "run": "pip install safety && safety check --json --output safety-report.json"
                        },
                        {
                            "name": "Upload security reports",
                            "uses": "actions/upload-artifact@v4",
                            "if": "always()",
                            "with": {
                                "name": "security-reports",
                                "path": "*-report.json"
                            }
                        }
                    ]
                },
                "code-quality": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.12"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt flake8 black isort mypy"
                        },
                        {
                            "name": "Run Flake8",
                            "run": "flake8 agentic_core/ --format=json --output-file=flake8-report.json"
                        },
                        {
                            "name": "Run Black format check",
                            "run": "black --check --diff agentic_core/"
                        },
                        {
                            "name": "Run isort import check",
                            "run": "isort --check-only --diff agentic_core/"
                        },
                        {
                            "name": "Run MyPy type check",
                            "run": "mypy agentic_core/ --json-report mypy-report"
                        },
                        {
                            "name": "Upload quality reports",
                            "uses": "actions/upload-artifact@v4",
                            "if": "always()",
                            "with": {
                                "name": "quality-reports",
                                "path": "*-report.json"
                            }
                        }
                    ]
                }
            }
        )

        self.hardening_stats['workflows_created'] += 1
        self.hardening_stats['jobs_defined'] += len(workflow.jobs)
        self.hardening_stats['steps_added'] += sum(len(job.get('steps', [])) for job in workflow.jobs.values())

        return workflow

    def _create_performance_workflow(self) -> WorkflowConfig:
        """Create performance testing workflow."""
        workflow = WorkflowConfig(
            name="Performance Testing",
            description="Performance benchmarks and load testing",
            triggers=["push", "pull_request", "schedule"],
            jobs={
                "performance-benchmarks": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.12"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt pytest-benchmark"
                        },
                        {
                            "name": "Run performance benchmarks",
                            "run": "pytest tests/performance/ --benchmark-only --benchmark-json=benchmark-report.json"
                        },
                        {
                            "name": "Upload benchmark results",
                            "uses": "actions/upload-artifact@v4",
                            "with": {
                                "name": "benchmark-results",
                                "path": "benchmark-report.json"
                            }
                        }
                    ]
                }
            }
        )

        self.hardening_stats['workflows_created'] += 1
        self.hardening_stats['jobs_defined'] += len(workflow.jobs)
        self.hardening_stats['steps_added'] += sum(len(job.get('steps', [])) for job in workflow.jobs.values())

        return workflow

    def _create_release_workflow(self) -> WorkflowConfig:
        """Create release workflow."""
        workflow = WorkflowConfig(
            name="Release Pipeline",
            description="Automated release and deployment pipeline",
            triggers=["push"],
            environment="production",
            jobs={
                "build-and-test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.12"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run full test suite",
                            "run": "pytest tests/ -v"
                        },
                        {
                            "name": "Build package",
                            "run": "python -m build"
                        }
                    ]
                },
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "needs": "build-and-test",
                    "environment": "production",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Deploy to production",
                            "run": "echo 'Deploy to production environment'"
                        }
                    ]
                }
            }
        )

        self.hardening_stats['workflows_created'] += 1
        self.hardening_stats['jobs_defined'] += len(workflow.jobs)
        self.hardening_stats['steps_added'] += sum(len(job.get('steps', [])) for job in workflow.jobs.values())
        self.hardening_stats['environments_configured'] += 1

        return workflow

    def write_workflow_files(self, workflows_dir: str = ".github/workflows") -> dict:
        """Write workflow files to GitHub Actions directory."""
        print("=== Writing GitHub Actions Workflow Files ===")

        workflows_path = Path(workflows_dir)
        workflows_path.mkdir(parents=True, exist_ok=True)

        files_created = []

        for workflow in self.workflows:
            # Convert workflow to GitHub Actions YAML format
            workflow_yaml = self._workflow_to_yaml(workflow)

            # Generate filename
            filename = f"{workflow.name.lower().replace(' ', '_').replace('-', '_')}.yml"
            file_path = workflows_path / filename

            # Write file
            with open(file_path, 'w') as f:
                f.write(workflow_yaml)

            files_created.append({
                'name': workflow.name,
                'filename': filename,
                'path': str(file_path)
            })

            print(f"✅ Created workflow: {filename}")

        return {
            'files_created': files_created,
            'total_files': len(files_created)
        }

    def _workflow_to_yaml(self, workflow: WorkflowConfig) -> str:
        """Convert workflow configuration to GitHub Actions YAML."""
        yaml_dict = {
            'name': workflow.name,
            'on': {
                trigger: {} for trigger in workflow.triggers
            },
            'jobs': {}
        }

        # Handle special triggers
        if 'schedule' in workflow.triggers:
            yaml_dict['on']['schedule'] = [{'cron': '0 2 * * *'}]  # Daily at 2 AM

        # Convert jobs
        for job_name, job_config in workflow.jobs.items():
            yaml_job = {
                'runs-on': job_config['runs-on']
            }

            if 'needs' in job_config:
                yaml_job['needs'] = job_config['needs']

            if 'strategy' in job_config:
                yaml_job['strategy'] = job_config['strategy']

            if 'environment' in job_config:
                yaml_job['environment'] = job_config['environment']

            # Convert steps
            steps = []
            for step in job_config['steps']:
                yaml_step = {}

                if 'name' in step:
                    yaml_step['name'] = step['name']

                if 'uses' in step:
                    yaml_step['uses'] = step['uses']

                if 'with' in step:
                    yaml_step['with'] = step['with']

                if 'run' in step:
                    yaml_step['run'] = step['run']

                if 'if' in step:
                    yaml_step['if'] = step['if']

                steps.append(yaml_step)

            yaml_job['steps'] = steps
            yaml_dict['jobs'][job_name] = yaml_job

        return yaml.dump(yaml_dict, default_flow_style=False, sort_keys=False)

    def generate_wave7a_report(self) -> dict:
        """Generate Wave 7a CI lane hardening report."""
        print("=== Wave 7a: CI Lane Hardening - GitHub Actions Setup ===")

        # Create CI workflows
        ci_results = self.create_ci_workflows()

        # Write workflow files
        file_results = self.write_workflow_files()

        # Create comprehensive report
        report = {
            'wave': 'Wave 7a',
            'timestamp': '2026-03-25 21:20:00',
            'title': 'CI Lane Hardening - GitHub Actions Setup',
            'ci_workflows': [
                {
                    'name': workflow.name,
                    'description': workflow.description,
                    'triggers': workflow.triggers,
                    'jobs_count': len(workflow.jobs),
                    'steps_count': sum(len(job.get('steps', [])) for job in workflow.jobs.values())
                }
                for workflow in self.workflows
            ],
            'workflow_files': file_results,
            'hardening_stats': self.hardening_stats,
            'summary': {
                'workflows_created': self.hardening_stats['workflows_created'],
                'jobs_defined': self.hardening_stats['jobs_defined'],
                'steps_added': self.hardening_stats['steps_added'],
                'environments_configured': self.hardening_stats['environments_configured'],
                'files_written': file_results['total_files']
            }
        }

        # Save report
        with open('artifacts/wave7a_ci_hardening_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Wave 7a Summary ===")
        print(f"Workflows created: {summary['workflows_created']}")
        print(f"Jobs defined: {summary['jobs_defined']}")
        print(f"Steps added: {summary['steps_added']}")
        print(f"Environments configured: {summary['environments_configured']}")
        print(f"Files written: {summary['files_written']}")

        print("\n📄 Report saved to: artifacts/wave7a_ci_hardening_report.json")

        return report


def main():
    """Main execution for Wave 7a."""
    hardener = GitHubActionsHardener()
    report = hardener.generate_wave7a_report()

    print("\n=== Wave 7a Summary ===")
    print(f"CI lanes hardened: {len(report['ci_workflows'])}")
    print(f"Total workflow steps: {report['summary']['steps_added']}")

    return report


if __name__ == '__main__':
    main()
