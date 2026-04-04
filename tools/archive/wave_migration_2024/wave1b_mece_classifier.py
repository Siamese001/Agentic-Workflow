#!/usr/bin/env python3
"""
Wave 1b: MECE classification of skip patterns and test issues.

This script performs MECE (Mutually Exclusive, Collectively Exhaustive)
classification of all skip patterns and test issues identified in Wave 1a.
"""

import json
from collections import defaultdict


class SkipPatternClassifier:
    """MECE classifier for skip patterns and test issues."""

    def __init__(self):
        self.classification_schema = self._define_classification_schema()
        self.classified_patterns = defaultdict(list)

    def _define_classification_schema(self) -> dict:
        """Define MECE classification schema."""
        return {
            'valid_skips': {
                'environmental': {
                    'description': 'Skips due to missing dependencies or environment',
                    'subcategories': {
                        'missing_dependency': 'Required library not available',
                        'platform_specific': 'OS/hardware specific tests',
                        'resource_intensive': 'Tests requiring significant resources',
                        'network_required': 'Tests requiring network access'
                    }
                },
                'intentional_temporary': {
                    'description': 'Intentionally skipped tests with clear reasons',
                    'subcategories': {
                        'feature_not_implemented': 'Feature under development',
                        'bug_in_test': 'Test itself has issues',
                        'known_limitation': 'Known limitation being tracked',
                        'deprecated_functionality': 'Testing deprecated code'
                    }
                },
                'conditional_execution': {
                    'description': 'Tests that run conditionally based on environment',
                    'subcategories': {
                        'version_specific': 'Python version specific',
                        'configuration_dependent': 'Requires specific configuration',
                        'optional_feature': 'Tests optional features'
                    }
                }
            },
            'invalid_skips': {
                'masking_failures': {
                    'description': 'Skips that hide actual test failures',
                    'subcategories': {
                        'broken_test_hidden': 'Broken test hidden behind skip',
                        'implementation_bug': 'Implementation bug masked',
                        'integration_failure': 'Integration failure hidden'
                    }
                },
                'development_convenience': {
                    'description': 'Skips for developer convenience (should be temporary)',
                    'subcategories': {
                        'slow_test': 'Test marked as slow for convenience',
                        'flaky_test': 'Flaky test instead of fixing',
                        'debug_skip': 'Skip left over from debugging',
                        'placeholder_skip': 'Placeholder test never implemented'
                    }
                },
                'anti_patterns': {
                    'description': 'Clear anti-patterns in skip usage',
                    'subcategories': {
                        'silent_failure': 'Skip instead of proper error handling',
                        'conditional_complexity': 'Overly complex skip conditions',
                        'fixture_abuse': 'Using fixtures to skip tests',
                        'commented_out_test': 'Test commented out instead of properly skipped'
                    }
                }
            },
            'questionable_skips': {
                'documentation_issues': {
                    'description': 'Skips with poor or missing documentation',
                    'subcategories': {
                        'no_reason': 'Skip without clear reason',
                        'vague_reason': 'Unclear skip reason',
                        'outdated_reason': 'Skip reason no longer valid'
                    }
                },
                'structural_issues': {
                    'description': 'Skip patterns indicating structural problems',
                    'subcategories': {
                        'repetitive_pattern': 'Same skip pattern repeated',
                        'inconsistent_usage': 'Inconsistent skip usage',
                        'overly_broad': 'Skip condition too broad'
                    }
                }
            }
        }

    def classify_skip_patterns(self, wave1a_data: dict) -> dict:
        """Classify skip patterns from Wave 1a data."""
        print("=== Classifying Skip Patterns ===")

        skip_patterns = wave1a_data.get('skip_patterns', {})
        classified = {
            'total_skips': 0,
            'classification_summary': defaultdict(int),
            'detailed_classification': defaultdict(list),
            'files_by_classification': defaultdict(set),
            'recommendations': []
        }

        # Process each skip pattern type
        for pattern_type, skips in skip_patterns.items():
            if pattern_type == 'total_skips' or pattern_type == 'skip_reasons':
                continue

            if isinstance(skips, list):
                for skip in skips:
                    classification = self._classify_single_skip(skip)

                    # Update counts
                    classified['total_skips'] += 1
                    classified['classification_summary'][classification['category']] += 1
                    classified['classification_summary'][classification['subcategory']] += 1

                    # Store detailed classification
                    classified['detailed_classification'][classification['category']].append({
                        'file': skip['file'],
                        'line': skip.get('line', 0),
                        'pattern_type': pattern_type,
                        'reason': skip.get('reason', ''),
                        'classification': classification,
                        'confidence': classification['confidence']
                    })

                    # Track files
                    classified['files_by_classification'][classification['category']].add(skip['file'])

        # Generate recommendations
        classified['recommendations'] = self._generate_recommendations(classified)

        return dict(classified)

    def _classify_single_skip(self, skip: dict) -> dict:
        """Classify a single skip pattern."""
        file_path = skip['file']
        reason = skip.get('reason', '').lower()
        pattern_type = skip.get('pattern_type', '')
        line_content = skip.get('line_content', '').lower()

        # Classification logic
        classification = {
            'category': 'questionable_skips',
            'subcategory': 'documentation_issues',
            'specific_type': 'no_reason',
            'confidence': 0.5,
            'rationale': []
        }

        # Check for valid skips first
        if self._is_environmental_skip(reason, line_content, file_path):
            classification = self._classify_environmental_skip(reason, line_content, file_path)
        elif self._is_intentional_temporary_skip(reason, line_content):
            classification = self._classify_intentional_temporary_skip(reason, line_content)
        elif self._is_conditional_execution_skip(reason, line_content):
            classification = self._classify_conditional_execution_skip(reason, line_content)

        # Check for invalid skips
        elif self._is_masking_failure_skip(reason, line_content, file_path):
            classification = self._classify_masking_failure_skip(reason, line_content, file_path)
        elif self._is_development_convenience_skip(reason, line_content):
            classification = self._classify_development_convenience_skip(reason, line_content)
        elif self._is_anti_pattern_skip(reason, line_content, pattern_type):
            classification = self._classify_anti_pattern_skip(reason, line_content, pattern_type)

        # Check for questionable skips
        elif self._has_documentation_issues(reason, line_content):
            classification = self._classify_documentation_issues(reason, line_content)
        elif self._has_structural_issues(reason, line_content, file_path):
            classification = self._classify_structural_issues(reason, line_content, file_path)

        return classification

    def _is_environmental_skip(self, reason: str, line_content: str, file_path: str) -> bool:
        """Check if skip is environmental."""
        environmental_keywords = [
            'requires', 'dependency', 'missing', 'platform', 'windows', 'linux', 'mac',
            'resource', 'memory', 'disk', 'network', 'internet', 'connection',
            'docker', 'container', 'vm', 'hardware', 'gpu', 'cpu'
        ]

        return any(keyword in reason or keyword in line_content for keyword in environmental_keywords)

    def _classify_environmental_skip(self, reason: str, line_content: str, file_path: str) -> dict:
        """Classify environmental skip."""
        category = 'valid_skips'
        subcategory = 'environmental'

        if any(keyword in reason or keyword in line_content for keyword in ['requires', 'dependency', 'missing', 'import']):
            specific_type = 'missing_dependency'
        elif any(keyword in reason or keyword in line_content for keyword in ['platform', 'windows', 'linux', 'mac', 'os']):
            specific_type = 'platform_specific'
        elif any(keyword in reason or keyword in line_content for keyword in ['resource', 'memory', 'disk', 'time', 'slow']):
            specific_type = 'resource_intensive'
        elif any(keyword in reason or keyword in line_content for keyword in ['network', 'internet', 'connection']):
            specific_type = 'network_required'
        else:
            specific_type = 'other_environmental'

        return {
            'category': category,
            'subcategory': subcategory,
            'specific_type': specific_type,
            'confidence': 0.8,
            'rationale': [f'Environmental skip detected: {specific_type}']
        }

    def _is_intentional_temporary_skip(self, reason: str, line_content: str) -> bool:
        """Check if skip is intentional temporary."""
        intentional_keywords = [
            'not implemented', 'todo', 'fixme', 'under development', 'wip',
            'work in progress', 'feature', 'implementation', 'bug', 'issue',
            'deprecated', 'legacy', 'temporary', 'soon'
        ]

        return any(keyword in reason or keyword in line_content for keyword in intentional_keywords)

    def _classify_intentional_temporary_skip(self, reason: str, line_content: str) -> dict:
        """Classify intentional temporary skip."""
        category = 'valid_skips'
        subcategory = 'intentional_temporary'

        if any(keyword in reason or keyword in line_content for keyword in ['not implemented', 'todo', 'under development']):
            specific_type = 'feature_not_implemented'
        elif any(keyword in reason or keyword in line_content for keyword in ['bug', 'issue', 'broken']):
            specific_type = 'bug_in_test'
        elif any(keyword in reason or keyword in line_content for keyword in ['known', 'limitation']):
            specific_type = 'known_limitation'
        elif any(keyword in reason or keyword in line_content for keyword in ['deprecated', 'legacy']):
            specific_type = 'deprecated_functionality'
        else:
            specific_type = 'other_intentional'

        return {
            'category': category,
            'subcategory': subcategory,
            'specific_type': specific_type,
            'confidence': 0.7,
            'rationale': [f'Intentional temporary skip: {specific_type}']
        }

    def _is_conditional_execution_skip(self, reason: str, line_content: str) -> bool:
        """Check if skip is conditional execution."""
        conditional_keywords = [
            'version', 'python', 'config', 'option', 'feature', 'optional',
            'condition', 'when', 'if', 'enable', 'disable'
        ]

        return any(keyword in reason or keyword in line_content for keyword in conditional_keywords)

    def _classify_conditional_execution_skip(self, reason: str, line_content: str) -> dict:
        """Classify conditional execution skip."""
        category = 'valid_skips'
        subcategory = 'conditional_execution'

        if any(keyword in reason or keyword in line_content for keyword in ['version', 'python']):
            specific_type = 'version_specific'
        elif any(keyword in reason or keyword in line_content for keyword in ['config', 'configuration']):
            specific_type = 'configuration_dependent'
        elif any(keyword in reason or keyword in line_content for keyword in ['optional', 'feature']):
            specific_type = 'optional_feature'
        else:
            specific_type = 'other_conditional'

        return {
            'category': category,
            'subcategory': subcategory,
            'specific_type': specific_type,
            'confidence': 0.6,
            'rationale': [f'Conditional execution skip: {specific_type}']
        }

    def _is_masking_failure_skip(self, reason: str, line_content: str, file_path: str) -> bool:
        """Check if skip is masking failure."""
        masking_keywords = [
            'broken', 'fails', 'error', 'crash', 'exception', 'issue',
            'problem', 'doesn\'t work', 'not working', 'regression'
        ]

        return any(keyword in reason or keyword in line_content for keyword in masking_keywords)

    def _classify_masking_failure_skip(self, reason: str, line_content: str, file_path: str) -> dict:
        """Classify masking failure skip."""
        category = 'invalid_skips'
        subcategory = 'masking_failures'

        if any(keyword in reason or keyword in line_content for keyword in ['test', 'broken']):
            specific_type = 'broken_test_hidden'
        elif any(keyword in reason or keyword in line_content for keyword in ['implementation', 'code']):
            specific_type = 'implementation_bug'
        elif any(keyword in reason or keyword in line_content for keyword in ['integration', 'system']):
            specific_type = 'integration_failure'
        else:
            specific_type = 'other_masking'

        return {
            'category': category,
            'subcategory': subcategory,
            'specific_type': specific_type,
            'confidence': 0.9,
            'rationale': [f'Masking failure detected: {specific_type}']
        }

    def _is_development_convenience_skip(self, reason: str, line_content: str) -> bool:
        """Check if skip is for development convenience."""
        convenience_keywords = [
            'slow', 'takes too long', 'timeout', 'flaky', 'unstable',
            'debug', 'testing', 'temporary', 'later', 'skip for now'
        ]

        return any(keyword in reason or keyword in line_content for keyword in convenience_keywords)

    def _classify_development_convenience_skip(self, reason: str, line_content: str) -> dict:
        """Classify development convenience skip."""
        category = 'invalid_skips'
        subcategory = 'development_convenience'

        if any(keyword in reason or keyword in line_content for keyword in ['slow', 'time', 'long']):
            specific_type = 'slow_test'
        elif any(keyword in reason or keyword in line_content for keyword in ['flaky', 'unstable']):
            specific_type = 'flaky_test'
        elif any(keyword in reason or keyword in line_content for keyword in ['debug', 'testing']):
            specific_type = 'debug_skip'
        elif any(keyword in reason or keyword in line_content for keyword in ['placeholder', 'todo', 'implement']):
            specific_type = 'placeholder_skip'
        else:
            specific_type = 'other_convenience'

        return {
            'category': category,
            'subcategory': subcategory,
            'specific_type': specific_type,
            'confidence': 0.8,
            'rationale': [f'Development convenience skip: {specific_type}']
        }

    def _is_anti_pattern_skip(self, reason: str, line_content: str, pattern_type: str) -> bool:
        """Check if skip is an anti-pattern."""
        anti_pattern_indicators = [
            'commented_out_test' in pattern_type,
            'fixture' in pattern_type,
            'manual' in pattern_type,
            len(reason) == 0,
            'pass' in line_content and 'skip' in line_content
        ]

        return any(anti_pattern_indicators)

    def _classify_anti_pattern_skip(self, reason: str, line_content: str, pattern_type: str) -> dict:
        """Classify anti-pattern skip."""
        category = 'invalid_skips'
        subcategory = 'anti_patterns'

        if 'commented' in pattern_type or 'commented' in line_content:
            specific_type = 'commented_out_test'
        elif 'fixture' in pattern_type:
            specific_type = 'fixture_abuse'
        elif 'manual' in pattern_type:
            specific_type = 'silent_failure'
        elif len(reason) == 0:
            specific_type = 'silent_failure'
        else:
            specific_type = 'other_anti_pattern'

        return {
            'category': category,
            'subcategory': subcategory,
            'specific_type': specific_type,
            'confidence': 0.9,
            'rationale': [f'Anti-pattern skip detected: {specific_type}']
        }

    def _has_documentation_issues(self, reason: str, line_content: str) -> bool:
        """Check if skip has documentation issues."""
        return len(reason) == 0 or len(reason) < 10 or 'skip' in reason.lower()

    def _classify_documentation_issues(self, reason: str, line_content: str) -> dict:
        """Classify documentation issues."""
        category = 'questionable_skips'
        subcategory = 'documentation_issues'

        if len(reason) == 0:
            specific_type = 'no_reason'
            confidence = 0.9
        elif len(reason) < 10:
            specific_type = 'vague_reason'
            confidence = 0.7
        else:
            specific_type = 'outdated_reason'
            confidence = 0.5

        return {
            'category': category,
            'subcategory': subcategory,
            'specific_type': specific_type,
            'confidence': confidence,
            'rationale': [f'Documentation issue: {specific_type}']
        }

    def _has_structural_issues(self, reason: str, line_content: str, file_path: str) -> bool:
        """Check if skip has structural issues."""
        # This would require more complex analysis of patterns across files
        return False  # Simplified for now

    def _classify_structural_issues(self, reason: str, line_content: str, file_path: str) -> dict:
        """Classify structural issues."""
        return {
            'category': 'questionable_skips',
            'subcategory': 'structural_issues',
            'specific_type': 'other_structural',
            'confidence': 0.3,
            'rationale': ['Structural issue detected']
        }

    def _generate_recommendations(self, classified: dict) -> list[dict]:
        """Generate recommendations based on classification."""
        recommendations = []

        # Count by category
        valid_count = sum(classified['classification_summary'].get(k, 0)
                          for k in classified['classification_summary']
                          if 'valid_skips' in k)
        invalid_count = sum(classified['classification_summary'].get(k, 0)
                            for k in classified['classification_summary']
                            if 'invalid_skips' in k)
        questionable_count = sum(classified['classification_summary'].get(k, 0)
                                for k in classified['classification_summary']
                                if 'questionable_skips' in k)

        total = classified['total_skips']

        # Overall recommendations
        if invalid_count > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'invalid_skips',
                'action': 'Remove or fix invalid skips',
                'count': invalid_count,
                'description': f'{invalid_count} skips are hiding failures or using anti-patterns'
            })

        if questionable_count > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'questionable_skips',
                'action': 'Improve documentation and structure',
                'count': questionable_count,
                'description': f'{questionable_count} skips have poor documentation or structural issues'
            })

        # Specific recommendations
        for category, details in classified['detailed_classification'].items():
            if len(details) > 10:  # If more than 10 skips in a category
                recommendations.append({
                    'priority': 'medium' if category == 'valid_skips' else 'high',
                    'category': category,
                    'action': f'Review {category} patterns',
                    'count': len(details),
                    'description': f'High concentration ({len(details)}) of {category} skips'
                })

        return recommendations


def generate_wave1b_report():
    """Generate Wave 1b MECE classification report."""
    print("=== Wave 1b: MECE Classification of Skip Patterns ===")

    # Load Wave 1a data
    try:
        with open('artifacts/wave1a_inventory_report.json') as f:
            wave1a_data = json.load(f)
    except FileNotFoundError:
        print("❌ Wave 1a report not found. Please run Wave 1a first.")
        return None

    # Classify skip patterns
    classifier = SkipPatternClassifier()
    classification = classifier.classify_skip_patterns(wave1a_data)

    # Create report
    report = {
        'wave': 'Wave 1b',
        'timestamp': '2026-03-25 20:05:00',
        'title': 'MECE Classification of Skip Patterns and Test Issues',
        'classification_schema': classifier.classification_schema,
        'classification_results': classification,
        'summary': {
            'total_skips_classified': classification['total_skips'],
            'valid_skips': sum(classification['classification_summary'].get(k, 0)
                              for k in classification['classification_summary']
                              if 'valid_skips' in k),
            'invalid_skips': sum(classification['classification_summary'].get(k, 0)
                                for k in classification['classification_summary']
                                if 'invalid_skips' in k),
            'questionable_skips': sum(classification['classification_summary'].get(k, 0)
                                    for k in classification['classification_summary']
                                    if 'questionable_skips' in k),
            'recommendations_count': len(classification['recommendations'])
        }
    }

    # Save report
    # Convert sets to lists for JSON serialization
    report_copy = json.loads(json.dumps(report, default=str))
    with open('artifacts/wave1b_classification_report.json', 'w') as f:
        json.dump(report_copy, f, indent=2)

    # Print summary
    summary = report['summary']
    print("\n=== Wave 1b Summary ===")
    print(f"Total skips classified: {summary['total_skips_classified']}")
    print(f"Valid skips: {summary['valid_skips']}")
    print(f"Invalid skips: {summary['invalid_skips']}")
    print(f"Questionable skips: {summary['questionable_skips']}")
    print(f"Recommendations: {summary['recommendations_count']}")

    # Print top recommendations
    print("\n=== Top Recommendations ===")
    for i, rec in enumerate(classification['recommendations'][:3], 1):
        print(f"{i}. [{rec['priority'].upper()}] {rec['action']} ({rec['count']} skips)")
        print(f"   {rec['description']}")

    print("\n📄 Report saved to: artifacts/wave1b_classification_report.json")

    return report


if __name__ == '__main__':
    generate_wave1b_report()
