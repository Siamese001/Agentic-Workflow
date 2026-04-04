#!/usr/bin/env python3
"""
Wave 5a: Marker and config hardening - pytest.ini.

This script hardens pytest configuration and markers,
focusing on pytest.ini optimization and marker standardization.
"""

import json
from pathlib import Path


class PytestConfigHardener:
    """Hardener for pytest configuration and markers."""

    def __init__(self):
        self.hardening_stats = {
            'files_processed': 0,
            'files_modified': 0,
            'configs_analyzed': 0,
            'configs_hardened': 0,
            'markers_added': 0,
            'errors_encountered': 0
        }
        self.modifications = []

    def scan_pytest_configs(self) -> list[dict]:
        """Scan for pytest configuration files."""
        print("=== Scanning Pytest Configuration Files ===")

        config_files = []
        root_dir = Path('.')

        # Look for pytest.ini files
        for pytest_ini in root_dir.rglob('pytest.ini'):
            config_files.append({
                'file': str(pytest_ini.relative_to(root_dir)),
                'type': 'pytest_ini',
                'path': pytest_ini
            })

        # Look for pyproject.toml with pytest configuration
        for pyproject_toml in root_dir.rglob('pyproject.toml'):
            try:
                with open(pyproject_toml, encoding='utf-8') as f:
                    content = f.read()
                if '[tool.pytest.ini_options]' in content:
                    config_files.append({
                        'file': str(pyproject_toml.relative_to(root_dir)),
                        'type': 'pyproject_toml',
                        'path': pyproject_toml
                    })
            except Exception as e:
                print(f"    Error reading {pyproject_toml}: {e}")

        # Look for setup.cfg with pytest configuration
        for setup_cfg in root_dir.rglob('setup.cfg'):
            try:
                with open(setup_cfg, encoding='utf-8') as f:
                    content = f.read()
                if '[pytest]' in content:
                    config_files.append({
                        'file': str(setup_cfg.relative_to(root_dir)),
                        'type': 'setup_cfg',
                        'path': setup_cfg
                    })
            except Exception as e:
                print(f"    Error reading {setup_cfg}: {e}")

        print(f"🔍 Found {len(config_files)} pytest configuration files")
        return config_files

    def analyze_pytest_config(self, config_file: dict) -> dict:
        """Analyze a pytest configuration file."""
        file_path = config_file['path']
        config_type = config_file['type']

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            analysis = {
                'file': config_file['file'],
                'type': config_type,
                'content': content,
                'markers': [],
                'options': {},
                'issues': [],
                'recommendations': []
            }

            if config_type == 'pytest_ini':
                analysis.update(self._analyze_pytest_ini(content))
            elif config_type == 'pyproject_toml':
                analysis.update(self._analyze_pyproject_toml(content))
            elif config_type == 'setup_cfg':
                analysis.update(self._analyze_setup_cfg(content))

            return analysis

        except Exception as e:
            print(f"❌ Error analyzing {config_file['file']}: {e}")
            return {'file': config_file['file'], 'type': config_type, 'error': str(e)}

    def _analyze_pytest_ini(self, content: str) -> dict:
        """Analyze pytest.ini content."""
        analysis = {
            'markers': [],
            'options': {},
            'issues': [],
            'recommendations': []
        }

        lines = content.split('\n')
        current_section = None

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # Check for markers
            if line_stripped.startswith('markers ='):
                markers_line = line_stripped.replace('markers =', '').strip()
                if markers_line:
                    # Handle multi-line markers
                    if markers_line.endswith('\\'):
                        markers_line = markers_line[:-1].strip()
                        # Continue reading next lines
                        next_line_num = line_num
                        while next_line_num < len(lines):
                            next_line_num += 1
                            next_line = lines[next_line_num - 1].strip()
                            if next_line.endswith('\\'):
                                markers_line += ' ' + next_line[:-1].strip()
                            else:
                                markers_line += ' ' + next_line
                                break

                    # Parse markers
                    markers = [m.strip() for m in markers_line.split() if m.strip()]
                    analysis['markers'].extend(markers)

            # Check for other options
            elif '=' in line_stripped:
                key, value = line_stripped.split('=', 1)
                key = key.strip()
                value = value.strip()
                analysis['options'][key] = value

        # Analyze markers and options
        analysis['issues'].extend(self._check_marker_issues(analysis['markers']))
        analysis['issues'].extend(self._check_option_issues(analysis['options']))
        analysis['recommendations'].extend(self._generate_recommendations(analysis['markers'], analysis['options']))

        return analysis

    def _analyze_pyproject_toml(self, content: str) -> dict:
        """Analyze pyproject.toml pytest configuration."""
        analysis = {
            'markers': [],
            'options': {},
            'issues': [],
            'recommendations': []
        }

        # Look for [tool.pytest.ini_options] section
        try:
            import tomllib
            config = tomllib.loads(content)

            pytest_config = config.get('tool', {}).get('pytest', {}).get('ini_options', {})

            # Extract markers
            markers = pytest_config.get('markers', [])
            if isinstance(markers, list):
                analysis['markers'] = markers
            elif isinstance(markers, str):
                analysis['markers'] = [markers]

            # Extract other options
            for key, value in pytest_config.items():
                if key != 'markers':
                    analysis['options'][key] = str(value)

            # Analyze markers and options
            analysis['issues'].extend(self._check_marker_issues(analysis['markers']))
            analysis['issues'].extend(self._check_option_issues(analysis['options']))
            analysis['recommendations'].extend(self._generate_recommendations(analysis['markers'], analysis['options']))

        except Exception as e:
            analysis['issues'].append(f"TOML parsing error: {e}")

        return analysis

    def _analyze_setup_cfg(self, content: str) -> dict:
        """Analyze setup.cfg pytest configuration."""
        # Similar to pytest.ini analysis but limited to [pytest] section
        analysis = {
            'markers': [],
            'options': {},
            'issues': [],
            'recommendations': []
        }

        lines = content.split('\n')
        in_pytest_section = False

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Check for pytest section
            if line_stripped == '[pytest]':
                in_pytest_section = True
                continue
            elif line_stripped.startswith('[') and in_pytest_section:
                in_pytest_section = False
                continue

            if not in_pytest_section:
                continue

            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # Check for markers
            if line_stripped.startswith('markers ='):
                markers_line = line_stripped.replace('markers =', '').strip()
                if markers_line:
                    markers = [m.strip() for m in markers_line.split() if m.strip()]
                    analysis['markers'].extend(markers)

            # Check for other options
            elif '=' in line_stripped:
                key, value = line_stripped.split('=', 1)
                key = key.strip()
                value = value.strip()
                analysis['options'][key] = value

        # Analyze markers and options
        analysis['issues'].extend(self._check_marker_issues(analysis['markers']))
        analysis['issues'].extend(self._check_option_issues(analysis['options']))
        analysis['recommendations'].extend(self._generate_recommendations(analysis['markers'], analysis['options']))

        return analysis

    def _check_marker_issues(self, markers: list[str]) -> list[str]:
        """Check for marker configuration issues."""
        issues = []

        # Check for standard markers
        standard_markers = {
            'slow': 'slow running tests',
            'integration': 'integration tests',
            'unit': 'unit tests',
            'smoke': 'smoke tests',
            'regression': 'regression tests'
        }

        found_markers = set()
        for marker in markers:
            # Extract marker name (before colon or space)
            marker_name = marker.split(':')[0].split()[0]
            found_markers.add(marker_name)

        # Check for missing standard markers
        missing_standard = set(standard_markers.keys()) - found_markers
        if missing_standard:
            issues.append(f"Missing standard markers: {', '.join(missing_standard)}")

        # Check for marker format issues
        for marker in markers:
            if ':' not in marker and ' ' not in marker:
                issues.append(f"Marker '{marker}' lacks description")

        return issues

    def _check_option_issues(self, options: dict[str, str]) -> list[str]:
        """Check for pytest option issues."""
        issues = []

        # Check for important options
        important_options = [
            'testpaths', 'python_files', 'python_classes', 'python_functions',
            'addopts', 'minversion', 'required_plugins'
        ]

        missing_important = set(important_options) - set(options.keys())
        if missing_important:
            issues.append(f"Missing important options: {', '.join(missing_important)}")

        # Check for testpaths
        if 'testpaths' not in options:
            issues.append("Missing testpaths configuration")

        # Check for addopts
        if 'addopts' not in options:
            issues.append("Missing addopts configuration")

        return issues

    def _generate_recommendations(self, markers: list[str], options: dict[str, str]) -> list[str]:
        """Generate configuration recommendations."""
        recommendations = []

        # Recommend standard markers
        if not any('slow' in m for m in markers):
            recommendations.append("Add 'slow' marker for performance tests")

        if not any('integration' in m for m in markers):
            recommendations.append("Add 'integration' marker for integration tests")

        if not any('unit' in m for m in markers):
            recommendations.append("Add 'unit' marker for unit tests")

        # Recommend important options
        if 'testpaths' not in options:
            recommendations.append("Add testpaths to specify test directories")

        if 'addopts' not in options:
            recommendations.append("Add addopts for default pytest options")

        if 'python_files' not in options:
            recommendations.append("Add python_files to specify test file patterns")

        # Recommend strict mode
        addopts = options.get('addopts', '')
        if '--strict-markers' not in addopts:
            recommendations.append("Add --strict-markers to addopts for marker enforcement")

        if '--strict-config' not in addopts:
            recommendations.append("Add --strict-config to addopts for config enforcement")

        return recommendations

    def harden_pytest_configs(self, config_files: list[dict]) -> dict:
        """Harden pytest configuration files."""
        print("=== Hardening Pytest Configurations ===")

        self.hardening_stats['configs_analyzed'] = len(config_files)

        # Analyze each config file
        analyses = []
        for config_file in config_files:
            analysis = self.analyze_pytest_config(config_file)
            analyses.append(analysis)

            if 'error' not in analysis:
                self.hardening_stats['files_processed'] += 1

        # Harden configurations
        for analysis in analyses:
            if 'error' not in analysis:
                hardening_result = self._harden_single_config(analysis)
                if hardening_result['hardened']:
                    self.hardening_stats['configs_hardened'] += 1
                    self.hardening_stats['markers_added'] += hardening_result['markers_added']

        return {
            'stats': self.hardening_stats,
            'analyses': analyses,
            'modifications': self.modifications
        }

    def _harden_single_config(self, analysis: dict) -> dict:
        """Harden a single pytest configuration."""
        hardening_result = {
            'hardened': False,
            'markers_added': 0,
            'options_added': 0
        }

        file_path = analysis['file']
        config_type = analysis['type']

        try:
            # Read original content
            with open(file_path, encoding='utf-8') as f:
                original_content = f.read()

            # Generate hardened content
            hardened_content = self._generate_hardened_config(analysis, original_content)

            # Write back if changed
            if hardened_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(hardened_content)

                hardening_result['hardened'] = True
                hardening_result['markers_added'] = len(analysis.get('recommendations', []))

                # Record modification
                self.modifications.append({
                    'file': file_path,
                    'type': config_type,
                    'original_issues': analysis.get('issues', []),
                    'recommendations_applied': analysis.get('recommendations', []),
                    'markers_added': hardening_result['markers_added']
                })

                print(f"✅ {file_path}: Hardened with {hardening_result['markers_added']} improvements")
            else:
                print(f"⚪ {file_path}: No hardening needed")

        except Exception as e:
            print(f"❌ Error hardening {file_path}: {e}")
            self.hardening_stats['errors_encountered'] += 1

        return hardening_result

    def _generate_hardened_config(self, analysis: dict, original_content: str) -> str:
        """Generate hardened pytest configuration."""
        config_type = analysis['type']

        if config_type == 'pytest_ini':
            return self._harden_pytest_ini(analysis, original_content)
        elif config_type == 'pyproject_toml':
            return self._harden_pyproject_toml(analysis, original_content)
        elif config_type == 'setup_cfg':
            return self._harden_setup_cfg(analysis, original_content)

        return original_content

    def _harden_pytest_ini(self, analysis: dict, content: str) -> str:
        """Harden pytest.ini configuration."""
        lines = content.split('\n')
        hardened_lines = []

        # Add standard configuration
        hardened_lines.extend([
            "[pytest]",
            "# Standard pytest configuration",
            "minversion = 6.0",
            "testpaths = tests",
            "python_files = test_*.py *_test.py",
            "python_classes = Test* *Tests",
            "python_functions = test_*",
            "",
            "# Default options",
            "addopts = --strict-markers --strict-config --tb=short -v",
            "",
            "# Standard markers",
            "markers =",
            "    slow: marks tests as slow (deselect with '-m \"not slow\"')",
            "    integration: marks tests as integration tests",
            "    unit: marks tests as unit tests",
            "    smoke: marks tests as smoke tests",
            "    regression: marks tests as regression tests"
        ])

        return '\n'.join(hardened_lines)

    def _harden_pyproject_toml(self, analysis: dict, content: str) -> str:
        """Harden pyproject.toml pytest configuration."""
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

    def _harden_setup_cfg(self, analysis: dict, content: str) -> str:
        """Harden setup.cfg pytest configuration."""
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

    def validate_hardening(self) -> dict:
        """Validate that pytest configurations were hardened."""
        print("=== Validating Pytest Configuration Hardening ===")

        validation = {
            'files_validated': 0,
            'hardening_confirmed': 0,
            'markers_confirmed': 0,
            'remaining_issues': []
        }

        # Check modified files
        for modification in self.modifications:
            file_path = modification['file']

            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                # Check that standard markers are present
                standard_markers = ['slow', 'integration', 'unit', 'smoke', 'regression']
                markers_found = 0

                for marker in standard_markers:
                    if marker in content:
                        markers_found += 1

                if markers_found >= 3:  # At least 3 standard markers
                    validation['hardening_confirmed'] += 1
                    validation['markers_confirmed'] += markers_found
                else:
                    validation['remaining_issues'].append({
                        'file': file_path,
                        'issue': f'Insufficient markers found: {markers_found}/5'
                    })

                validation['files_validated'] += 1

            except Exception as e:
                validation['remaining_issues'].append({
                    'file': file_path,
                    'issue': f'Validation error: {e}'
                })

        return validation

    def generate_wave5a_report(self) -> dict:
        """Generate Wave 5a hardening report."""
        print("=== Wave 5a: Marker and Config Hardening - pytest.ini ===")

        # Scan for pytest configs
        config_files = self.scan_pytest_configs()

        # Harden configurations
        hardening_results = self.harden_pytest_configs(config_files)

        # Validate hardening
        validation_results = self.validate_hardening()

        # Create report
        report = {
            'wave': 'Wave 5a',
            'timestamp': '2026-03-25 20:55:00',
            'title': 'Marker and Config Hardening - pytest.ini',
            'config_files_found': len(config_files),
            'hardening_results': hardening_results,
            'validation_results': validation_results,
            'summary': {
                'config_files_found': len(config_files),
                'configs_analyzed': self.hardening_stats['configs_analyzed'],
                'configs_hardened': self.hardening_stats['configs_hardened'],
                'markers_added': self.hardening_stats['markers_added'],
                'hardening_confirmed': validation_results['hardening_confirmed'],
                'success_rate': (validation_results['hardening_confirmed'] / max(self.hardening_stats['configs_hardened'], 1)) * 100
            }
        }

        # Save report
        with open('artifacts/wave5a_hardening_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Wave 5a Summary ===")
        print(f"Config files found: {summary['config_files_found']}")
        print(f"Configs analyzed: {summary['configs_analyzed']}")
        print(f"Configs hardened: {summary['configs_hardened']}")
        print(f"Markers added: {summary['markers_added']}")
        print(f"Hardening confirmed: {summary['hardening_confirmed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")

        if validation_results['remaining_issues']:
            print(f"\n⚠️  Remaining issues: {len(validation_results['remaining_issues'])}")
            for issue in validation_results['remaining_issues'][:3]:
                print(f"  - {issue['file']}: {issue['issue']}")

        print("\n📄 Report saved to: artifacts/wave5a_hardening_report.json")

        return report


def main():
    """Main execution for Wave 5a."""
    hardener = PytestConfigHardener()
    report = hardener.generate_wave5a_report()

    return report


if __name__ == '__main__':
    main()
