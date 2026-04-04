#!/usr/bin/env python3
"""
Wave 5c: Marker and config hardening - core_path semantics.

This script hardens core path semantics in pytest configuration,
focusing on path resolution, test discovery, and execution semantics.
"""

import json
from pathlib import Path


class CorePathSemanticsHardener:
    """Hardener for core path semantics in pytest configuration."""

    def __init__(self):
        self.hardening_stats = {
            'files_processed': 0,
            'files_modified': 0,
            'paths_analyzed': 0,
            'paths_hardened': 0,
            'semantics_added': 0,
            'errors_encountered': 0
        }
        self.modifications = []

    def scan_core_paths(self) -> list[dict]:
        """Scan for core path configuration files."""
        print("=== Scanning Core Path Configuration ===")

        core_files = []
        root_dir = Path('.')

        # Look for pytest.ini files
        for pytest_ini in root_dir.rglob('pytest.ini'):
            core_files.append({
                'file': str(pytest_ini.relative_to(root_dir)),
                'type': 'pytest_ini',
                'path': pytest_ini
            })

        # Look for pyproject.toml files
        for pyproject_toml in root_dir.rglob('pyproject.toml'):
            core_files.append({
                'file': str(pyproject_toml.relative_to(root_dir)),
                'type': 'pyproject_toml',
                'path': pyproject_toml
            })

        # Look for setup.cfg files
        for setup_cfg in root_dir.rglob('setup.cfg'):
            core_files.append({
                'file': str(setup_cfg.relative_to(root_dir)),
                'type': 'setup_cfg',
                'path': setup_cfg
            })

        # Look for conftest.py files (test configuration)
        for conftest in root_dir.rglob('conftest.py'):
            core_files.append({
                'file': str(conftest.relative_to(root_dir)),
                'type': 'conftest_py',
                'path': conftest
            })

        print(f"🔍 Found {len(core_files)} core configuration files")
        return core_files

    def analyze_core_path_semantics(self, core_file: dict) -> dict:
        """Analyze core path semantics."""
        file_path = core_file['path']
        file_type = core_file['type']

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            analysis = {
                'file': core_file['file'],
                'type': file_type,
                'content': content,
                'paths': [],
                'semantics': {},
                'issues': [],
                'recommendations': []
            }

            if file_type in ['pytest_ini', 'pyproject_toml', 'setup_cfg']:
                analysis.update(self._analyze_config_paths(content, file_type))
            elif file_type == 'conftest_py':
                analysis.update(self._analyze_conftest_paths(content))

            return analysis

        except Exception as e:
            print(f"❌ Error analyzing {core_file['file']}: {e}")
            return {'file': core_file['file'], 'type': file_type, 'error': str(e)}

    def _analyze_config_paths(self, content: str, file_type: str) -> dict:
        """Analyze path configuration in config files."""
        analysis = {
            'paths': [],
            'semantics': {},
            'issues': [],
            'recommendations': []
        }

        # Extract path-related configurations
        path_configs = {
            'testpaths': [],
            'python_files': [],
            'python_classes': [],
            'python_functions': [],
            'norecursedirs': []
        }

        if file_type == 'pytest_ini':
            path_configs = self._extract_pytest_ini_paths(content)
        elif file_type == 'pyproject_toml':
            path_configs = self._extract_pyproject_paths(content)
        elif file_type == 'setup_cfg':
            path_configs = self._extract_setup_cfg_paths(content)

        analysis['paths'] = path_configs
        analysis['semantics'] = self._analyze_path_semantics(path_configs)
        analysis['issues'].extend(self._check_path_issues(path_configs))
        analysis['recommendations'].extend(self._generate_path_recommendations(path_configs))

        return analysis

    def _extract_pytest_ini_paths(self, content: str) -> dict:
        """Extract paths from pytest.ini."""
        paths = {
            'testpaths': [],
            'python_files': [],
            'python_classes': [],
            'python_functions': [],
            'norecursedirs': []
        }

        lines = content.split('\n')
        for line in lines:
            line_stripped = line.strip()

            if '=' in line_stripped and not line_stripped.startswith('#'):
                key, value = line_stripped.split('=', 1)
                key = key.strip()
                value = value.strip()

                if key in paths:
                    if key == 'testpaths':
                        paths[key] = [p.strip() for p in value.split() if p.strip()]
                    else:
                        paths[key] = [value]

        return paths

    def _extract_pyproject_paths(self, content: str) -> dict:
        """Extract paths from pyproject.toml."""
        paths = {
            'testpaths': [],
            'python_files': [],
            'python_classes': [],
            'python_functions': [],
            'norecursedirs': []
        }

        try:
            import tomllib
            config = tomllib.loads(content)

            pytest_config = config.get('tool', {}).get('pytest', {}).get('ini_options', {})

            for key in paths:
                if key in pytest_config:
                    value = pytest_config[key]
                    if isinstance(value, list):
                        paths[key] = value
                    else:
                        paths[key] = [str(value)]

        except Exception:
            pass

        return paths

    def _extract_setup_cfg_paths(self, content: str) -> dict:
        """Extract paths from setup.cfg."""
        paths = {
            'testpaths': [],
            'python_files': [],
            'python_classes': [],
            'python_functions': [],
            'norecursedirs': []
        }

        lines = content.split('\n')
        in_pytest_section = False

        for line in lines:
            line_stripped = line.strip()

            if line_stripped == '[pytest]':
                in_pytest_section = True
                continue
            elif line_stripped.startswith('[') and in_pytest_section:
                in_pytest_section = False
                continue

            if not in_pytest_section:
                continue

            if '=' in line_stripped and not line_stripped.startswith('#'):
                key, value = line_stripped.split('=', 1)
                key = key.strip()
                value = value.strip()

                if key in paths:
                    if key == 'testpaths':
                        paths[key] = [p.strip() for p in value.split() if p.strip()]
                    else:
                        paths[key] = [value]

        return paths

    def _analyze_conftest_paths(self, content: str) -> dict:
        """Analyze paths in conftest.py."""
        analysis = {
            'paths': {},
            'semantics': {},
            'issues': [],
            'recommendations': []
        }

        # Look for path-related fixtures and configurations
        path_patterns = [
            'testdir', 'tmp_path', 'monkeypatch', 'pytestconfig',
            'request', 'capsys', 'capfd', 'tmpdir_factory'
        ]

        found_patterns = []
        for pattern in path_patterns:
            if pattern in content:
                found_patterns.append(pattern)

        analysis['paths']['fixtures'] = found_patterns
        analysis['semantics'] = self._analyze_conftest_semantics(found_patterns, content)
        analysis['issues'].extend(self._check_conftest_issues(found_patterns, content))
        analysis['recommendations'].extend(self._generate_conftest_recommendations(found_patterns, content))

        return analysis

    def _analyze_path_semantics(self, path_configs: dict) -> dict:
        """Analyze path semantics."""
        semantics = {
            'test_discovery': {},
            'execution_order': {},
            'filtering': {}
        }

        # Test discovery semantics
        if path_configs.get('testpaths'):
            semantics['test_discovery']['has_testpaths'] = True
            semantics['test_discovery']['testpaths_count'] = len(path_configs['testpaths'])
        else:
            semantics['test_discovery']['has_testpaths'] = False

        # File pattern semantics
        if path_configs.get('python_files'):
            semantics['test_discovery']['file_patterns'] = path_configs['python_files']

        # Class/function semantics
        if path_configs.get('python_classes'):
            semantics['test_discovery']['class_patterns'] = path_configs['python_classes']

        if path_configs.get('python_functions'):
            semantics['test_discovery']['function_patterns'] = path_configs['python_functions']

        # Filtering semantics
        if path_configs.get('norecursedirs'):
            semantics['filtering']['excluded_dirs'] = path_configs['norecursedirs']

        return semantics

    def _analyze_conftest_semantics(self, fixtures: list[str], content: str) -> dict:
        """Analyze conftest.py semantics."""
        semantics = {
            'fixture_count': len(fixtures),
            'has_path_fixtures': bool(fixtures),
            'fixture_types': fixtures
        }

        return semantics

    def _check_path_issues(self, path_configs: dict) -> list[str]:
        """Check for path configuration issues."""
        issues = []

        # Check for missing testpaths
        if not path_configs.get('testpaths'):
            issues.append("Missing testpaths configuration")

        # Check for missing file patterns
        if not path_configs.get('python_files'):
            issues.append("Missing python_files configuration")

        # Check for missing class patterns
        if not path_configs.get('python_classes'):
            issues.append("Missing python_classes configuration")

        # Check for missing function patterns
        if not path_configs.get('python_functions'):
            issues.append("Missing python_functions configuration")

        # Check for invalid testpaths
        for testpath in path_configs.get('testpaths', []):
            if not Path(testpath).exists():
                issues.append(f"Test path does not exist: {testpath}")

        return issues

    def _check_conftest_issues(self, fixtures: list[str], content: str) -> list[str]:
        """Check for conftest.py issues."""
        issues = []

        if not fixtures:
            issues.append("No standard pytest fixtures found")

        return issues

    def _generate_path_recommendations(self, path_configs: dict) -> list[str]:
        """Generate path configuration recommendations."""
        recommendations = []

        # Recommend standard testpaths
        if not path_configs.get('testpaths'):
            recommendations.append("Add testpaths = tests")

        # Recommend standard file patterns
        if not path_configs.get('python_files'):
            recommendations.append("Add python_files = test_*.py *_test.py")

        # Recommend standard class patterns
        if not path_configs.get('python_classes'):
            recommendations.append("Add python_classes = Test* *Tests")

        # Recommend standard function patterns
        if not path_configs.get('python_functions'):
            recommendations.append("Add python_functions = test_*")

        # Recommend exclude patterns
        if not path_configs.get('norecursedirs'):
            recommendations.append("Add norecursedirs = .* build dist CVS _darcs {arch} *.egg")

        return recommendations

    def _generate_conftest_recommendations(self, fixtures: list[str], content: str) -> list[str]:
        """Generate conftest.py recommendations."""
        recommendations = []

        if not fixtures:
            recommendations.append("Add standard pytest fixtures")

        return recommendations

    def harden_core_path_semantics(self, core_files: list[dict]) -> dict:
        """Harden core path semantics."""
        print("=== Hardening Core Path Semantics ===")

        # Analyze each core file
        analyses = []
        for core_file in core_files:
            analysis = self.analyze_core_path_semantics(core_file)
            analyses.append(analysis)

            if 'error' not in analysis:
                self.hardening_stats['files_processed'] += 1

        # Harden configurations
        for analysis in analyses:
            if 'error' not in analysis:
                hardening_result = self._harden_single_core_file(analysis)
                if hardening_result['hardened']:
                    self.hardening_stats['paths_hardened'] += 1
                    self.hardening_stats['semantics_added'] += hardening_result['semantics_added']

        return {
            'stats': self.hardening_stats,
            'analyses': analyses,
            'modifications': self.modifications
        }

    def _harden_single_core_file(self, analysis: dict) -> dict:
        """Harden a single core configuration file."""
        hardening_result = {
            'hardened': False,
            'semantics_added': 0
        }

        file_path = analysis['file']
        file_type = analysis['type']

        try:
            # Read original content
            with open(file_path, encoding='utf-8') as f:
                original_content = f.read()

            # Generate hardened content
            hardened_content = self._generate_hardened_core_content(analysis, original_content)

            # Write back if changed
            if hardened_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(hardened_content)

                hardening_result['hardened'] = True
                hardening_result['semantics_added'] = len(analysis.get('recommendations', []))

                # Record modification
                self.modifications.append({
                    'file': file_path,
                    'type': file_type,
                    'original_issues': analysis.get('issues', []),
                    'recommendations_applied': analysis.get('recommendations', []),
                    'semantics_added': hardening_result['semantics_added']
                })

                print(f"✅ {file_path}: Hardened with {hardening_result['semantics_added']} semantic improvements")
            else:
                print(f"⚪ {file_path}: No semantic hardening needed")

        except Exception as e:
            print(f"❌ Error hardening {file_path}: {e}")
            self.hardening_stats['errors_encountered'] += 1

        return hardening_result

    def _generate_hardened_core_content(self, analysis: dict, original_content: str) -> str:
        """Generate hardened core configuration content."""
        file_type = analysis['type']

        if file_type in ['pytest_ini', 'pyproject_toml', 'setup_cfg']:
            return self._harden_config_content(analysis, original_content, file_type)
        elif file_type == 'conftest_py':
            return self._harden_conftest_content(analysis, original_content)

        return original_content

    def _harden_config_content(self, analysis: dict, content: str, file_type: str) -> str:
        """Harden configuration file content."""
        if file_type == 'pytest_ini':
            return self._generate_optimal_pytest_ini(analysis, content)
        elif file_type == 'pyproject_toml':
            return self._generate_optimal_pyproject_toml(analysis, content)
        elif file_type == 'setup_cfg':
            return self._generate_optimal_setup_cfg(analysis, content)

        return content

    def _generate_optimal_pytest_ini(self, analysis: dict, content: str) -> str:
        """Generate optimal pytest.ini content."""
        lines = [
            "[pytest]",
            "# Core path semantics configuration",
            "minversion = 6.0",
            "",
            "# Test discovery paths",
            "testpaths = tests",
            "",
            "# File and pattern discovery",
            "python_files = test_*.py *_test.py",
            "python_classes = Test* *Tests",
            "python_functions = test_*",
            "",
            "# Path exclusion patterns",
            "norecursedirs = .* build dist CVS _darcs {arch} *.egg __pycache__ .pytest_cache",
            "",
            "# Execution semantics",
            "addopts = --strict-markers --strict-config --tb=short -v",
            "",
            "# Standard markers",
            "markers =",
            "    slow: marks tests as slow (deselect with '-m \"not slow\"')",
            "    integration: marks tests as integration tests",
            "    unit: marks tests as unit tests",
            "    smoke: marks tests as smoke tests",
            "    regression: marks tests as regression tests"
        ]

        return '\n'.join(lines)

    def _generate_optimal_pyproject_toml(self, analysis: dict, content: str) -> str:
        """Generate optimal pyproject.toml pytest section."""
        lines = content.split('\n')
        hardened_lines = []
        pytest_section_added = False

        for line in lines:
            hardened_lines.append(line)

            # Add pytest section after [tool] section
            if line.strip() == '[tool]' and not pytest_section_added:
                hardened_lines.extend([
                    "",
                    "[tool.pytest.ini_options]",
                    "minversion = \"6.0\"",
                    "testpaths = [\"tests\"]",
                    "python_files = [\"test_*.py\", \"*_test.py\"]",
                    "python_classes = [\"Test*\", \"*Tests\"]",
                    "python_functions = [\"test_*\"]",
                    "norecursedirs = [\".*\", \"build\", \"dist\", \"CVS\", \"_darcs\", \"{arch}\", \"*.egg\", \"__pycache__\", \".pytest_cache\"]",
                    "addopts = [\"--strict-markers\", \"--strict-config\", \"--tb=short\", \"-v\"]",
                    "markers = [",
                    "    \"slow: marks tests as slow (deselect with '-m \\\"not slow\\\"')\",",
                    "    \"integration: marks tests as integration tests\",",
                    "    \"unit: marks tests as unit tests\",",
                    "    \"smoke: marks tests as smoke tests\",",
                    "    \"regression: marks tests as regression tests\"",
                    "]"
                ])
                pytest_section_added = True

        return '\n'.join(hardened_lines)

    def _generate_optimal_setup_cfg(self, analysis: dict, content: str) -> str:
        """Generate optimal setup.cfg pytest section."""
        lines = content.split('\n')
        hardened_lines = []
        pytest_section_found = False
        pytest_section_added = False

        for line in lines:
            if line.strip() == '[pytest]':
                pytest_section_found = True

            # Add pytest section if not found
            if not pytest_section_found and not pytest_section_added and line.strip().startswith('['):
                hardened_lines.extend([
                    "[pytest]",
                    "minversion = 6.0",
                    "testpaths = tests",
                    "python_files = test_*.py *_test.py",
                    "python_classes = Test* *Tests",
                    "python_functions = test_*",
                    "norecursedirs = .* build dist CVS _darcs {arch} *.egg __pycache__ .pytest_cache",
                    "addopts = --strict-markers --strict-config --tb=short -v",
                    "markers =",
                    "    slow: marks tests as slow (deselect with '-m \"not slow\"')",
                    "    integration: marks tests as integration tests",
                    "    unit: marks tests as unit tests",
                    "    smoke: marks tests as smoke tests",
                    "    regression: marks tests as regression tests",
                    ""
                ])
                pytest_section_added = True

            hardened_lines.append(line)

        return '\n'.join(hardened_lines)

    def _harden_conftest_content(self, analysis: dict, content: str) -> str:
        """Harden conftest.py content."""
        lines = [
            "# Core pytest configuration",
            "import pytest",
            "",
            "# Standard fixtures for path semantics",
            "@pytest.fixture",
            "def test_data_path():",
            "    \"\"\"Fixture for test data path.\"\"\"",
            "    from pathlib import Path",
            "    return Path(__file__).parent / \"test_data\"",
            "",
            "@pytest.fixture",
            "def temp_project_dir(tmp_path):",
            "    \"\"\"Fixture for temporary project directory.\"\"\"",
            "    return tmp_path / \"project\"",
            "",
            "# Test collection configuration",
            "def pytest_configure(config):",
            "    \"\"\"Configure pytest with custom settings.\"\"\"",
            "    config.addinivalue_line(\"markers\", \"data: marks tests as data-dependent\")",
            "",
            content
        ]

        return '\n'.join(lines)

    def validate_hardening(self) -> dict:
        """Validate that core path semantics hardening was successful."""
        print("=== Validating Core Path Semantics Hardening ===")

        validation = {
            'files_validated': 0,
            'hardening_confirmed': 0,
            'semantics_confirmed': 0,
            'remaining_issues': []
        }

        # Check modified files
        for modification in self.modifications:
            file_path = modification['file']

            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                # Check that standard path configurations are present
                standard_configs = ['testpaths', 'python_files', 'python_classes', 'python_functions']
                configs_found = 0

                for config in standard_configs:
                    if config in content:
                        configs_found += 1

                if configs_found >= 3:  # At least 3 standard configs
                    validation['hardening_confirmed'] += 1
                    validation['semantics_confirmed'] += configs_found
                else:
                    validation['remaining_issues'].append({
                        'file': file_path,
                        'issue': f'Insufficient path configs found: {configs_found}/4'
                    })

                validation['files_validated'] += 1

            except Exception as e:
                validation['remaining_issues'].append({
                    'file': file_path,
                    'issue': f'Validation error: {e}'
                })

        return validation

    def generate_wave5c_report(self) -> dict:
        """Generate Wave 5c hardening report."""
        print("=== Wave 5c: Marker and Config Hardening - Core Path Semantics ===")

        # Scan for core files
        core_files = self.scan_core_paths()

        # Harden core path semantics
        hardening_results = self.harden_core_path_semantics(core_files)

        # Validate hardening
        validation_results = self.validate_hardening()

        # Create report
        report = {
            'wave': 'Wave 5c',
            'timestamp': '2026-03-25 21:05:00',
            'title': 'Marker and Config Hardening - Core Path Semantics',
            'core_files_found': len(core_files),
            'hardening_results': hardening_results,
            'validation_results': validation_results,
            'summary': {
                'core_files_found': len(core_files),
                'files_processed': self.hardening_stats['files_processed'],
                'paths_hardened': self.hardening_stats['paths_hardened'],
                'semantics_added': self.hardening_stats['semantics_added'],
                'hardening_confirmed': validation_results['hardening_confirmed'],
                'success_rate': (validation_results['hardening_confirmed'] / max(self.hardening_stats['paths_hardened'], 1)) * 100
            }
        }

        # Save report
        with open('artifacts/wave5c_hardening_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Wave 5c Summary ===")
        print(f"Core files found: {summary['core_files_found']}")
        print(f"Files processed: {summary['files_processed']}")
        print(f"Paths hardened: {summary['paths_hardened']}")
        print(f"Semantics added: {summary['semantics_added']}")
        print(f"Hardening confirmed: {summary['hardening_confirmed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")

        if validation_results['remaining_issues']:
            print(f"\n⚠️  Remaining issues: {len(validation_results['remaining_issues'])}")
            for issue in validation_results['remaining_issues'][:3]:
                print(f"  - {issue['file']}: {issue['issue']}")

        print("\n📄 Report saved to: artifacts/wave5c_hardening_report.json")

        return report


def main():
    """Main execution for Wave 5c."""
    hardener = CorePathSemanticsHardener()
    report = hardener.generate_wave5c_report()

    return report


if __name__ == '__main__':
    main()
