#!/usr/bin/env python3
"""
Wave 1d: Categorize all skipped tests with detailed analysis.

This script provides detailed categorization and analysis of all skipped tests
identified in previous waves, preparing for targeted removal in Wave 2.
"""

import json
from collections import defaultdict


class SkipTestCategorizer:
    """Detailed categorizer for skipped tests."""

    def __init__(self):
        self.categorized_tests = defaultdict(list)
        self.actionable_skips = []

    def categorize_all_skipped_tests(self) -> dict:
        """Categorize all skipped tests with detailed analysis."""
        print("=== Wave 1d: Categorizing All Skipped Tests ===")

        # Load previous wave data
        try:
            with open('artifacts/wave1a_inventory_report.json') as f:
                wave1a_data = json.load(f)
            with open('artifacts/wave1b_classification_report.json') as f:
                wave1b_data = json.load(f)
        except FileNotFoundError as e:
            print(f"❌ Missing previous wave data: {e}")
            return None

        categorization = {
            'total_skipped_tests': 0,
            'categories': {
                'invalid_first_party': [],
                'masking_fixtures': [],
                'hidden_failures': [],
                'valid_environmental': [],
                'valid_intentional': [],
                'valid_conditional': [],
                'questionable_documentation': [],
                'questionable_structural': []
            },
            'actionable_removals': [],
            'requires_manual_review': [],
            'wave2_prioritization': {}
        }

        # Process skip patterns from Wave 1b
        classification_results = wave1b_data.get('classification_results', {})
        detailed_classification = classification_results.get('detailed_classification', {})

        # Categorize each skip
        for category, skips in detailed_classification.items():
            for skip_info in skips:
                categorized_skip = self._create_categorized_skip(skip_info, category)

                # Add to appropriate category
                target_category = self._determine_target_category(categorized_skip)
                categorization['categories'][target_category].append(categorized_skip)
                categorization['total_skipped_tests'] += 1

                # Determine actionability
                if self._is_actionable_removal(categorized_skip):
                    categorization['actionable_removals'].append(categorized_skip)
                else:
                    categorization['requires_manual_review'].append(categorized_skip)

        # Create Wave 2 prioritization
        categorization['wave2_prioritization'] = self._create_wave2_prioritization(categorization)

        return categorization

    def _create_categorized_skip(self, skip_info: dict, classification_category: str) -> dict:
        """Create a detailed categorized skip entry."""
        return {
            'file': skip_info['file'],
            'line': skip_info['line'],
            'pattern_type': skip_info['pattern_type'],
            'reason': skip_info['reason'],
            'classification': skip_info['classification'],
            'confidence': skip_info['confidence'],
            'wave1b_category': classification_category,
            'removal_priority': self._calculate_removal_priority(skip_info),
            'estimated_effort': self._estimate_removal_effort(skip_info),
            'risk_level': self._assess_removal_risk(skip_info)
        }

    def _determine_target_category(self, categorized_skip: dict) -> str:
        """Determine the target category for Wave 2 processing."""
        classification = categorized_skip['classification']
        category = classification.get('category', '')
        subcategory = classification.get('subcategory', '')

        # Map Wave 1b categories to Wave 2 categories
        if category == 'invalid_skips':
            if subcategory == 'masking_failures':
                return 'hidden_failures'
            elif subcategory == 'development_convenience':
                return 'invalid_first_party'
            elif subcategory == 'anti_patterns':
                if 'fixture' in categorized_skip.get('pattern_type', ''):
                    return 'masking_fixtures'
                else:
                    return 'invalid_first_party'
        elif category == 'valid_skips':
            if subcategory == 'environmental':
                return 'valid_environmental'
            elif subcategory == 'intentional_temporary':
                return 'valid_intentional'
            elif subcategory == 'conditional_execution':
                return 'valid_conditional'
        elif category == 'questionable_skips':
            if subcategory == 'documentation_issues':
                return 'questionable_documentation'
            elif subcategory == 'structural_issues':
                return 'questionable_structural'

        return 'questionable_documentation'  # default

    def _is_actionable_removal(self, categorized_skip: dict) -> bool:
        """Determine if a skip is actionable for removal."""
        classification = categorized_skip['classification']
        confidence = categorized_skip['confidence']
        risk_level = categorized_skip['risk_level']

        # High confidence invalid skips are actionable
        if (classification.get('category') == 'invalid_skips' and
            confidence > 0.7 and
            risk_level in ['low', 'medium']):
            return True

        # Some questionable skips with high confidence are actionable
        if (classification.get('category') == 'questionable_skips' and
            confidence > 0.8 and
            classification.get('specific_type') == 'no_reason'):
            return True

        return False

    def _calculate_removal_priority(self, skip_info: dict) -> str:
        """Calculate removal priority (high, medium, low)."""
        classification = skip_info['classification']
        confidence = skip_info['confidence']

        # Invalid skips get high priority
        if classification.get('category') == 'invalid_skips':
            if confidence > 0.8:
                return 'high'
            elif confidence > 0.6:
                return 'medium'
            else:
                return 'low'

        # Questionable skips get medium priority
        elif classification.get('category') == 'questionable_skips':
            if confidence > 0.7:
                return 'medium'
            else:
                return 'low'

        # Valid skips get low priority (keep them)
        return 'low'

    def _estimate_removal_effort(self, skip_info: dict) -> str:
        """Estimate effort required to remove skip."""
        pattern_type = skip_info.get('pattern_type', '')
        reason = skip_info.get('reason', '')

        # Simple decorator removals are easy
        if pattern_type in ['pytest_skip', 'pytest_skipif', 'pytest_xfail']:
            return 'low'

        # Manual skips might require more work
        elif pattern_type == 'manual_skips':
            return 'medium'

        # Complex patterns require more effort
        elif pattern_type in ['conditional_skips', 'fixture_skips']:
            return 'high'

        # No reason means investigation needed
        elif len(reason) == 0:
            return 'medium'

        return 'low'

    def _assess_removal_risk(self, skip_info: dict) -> str:
        """Assess risk of removing the skip."""
        classification = skip_info['classification']
        category = classification.get('category', '')
        subcategory = classification.get('subcategory', '')

        # Invalid skips have low risk (they're hiding problems)
        if category == 'invalid_skips':
            return 'low'

        # Valid environmental skips have high risk
        if category == 'valid_skips' and subcategory == 'environmental':
            return 'high'

        # Questionable skips have medium risk
        if category == 'questionable_skips':
            return 'medium'

        return 'medium'

    def _create_wave2_prioritization(self, categorization: dict) -> dict:
        """Create prioritization for Wave 2 processing."""
        actionable = categorization['actionable_removals']

        # Group by priority
        high_priority = [s for s in actionable if s['removal_priority'] == 'high']
        medium_priority = [s for s in actionable if s['removal_priority'] == 'medium']
        low_priority = [s for s in actionable if s['removal_priority'] == 'low']

        # Group by effort
        low_effort = [s for s in actionable if s['estimated_effort'] == 'low']
        medium_effort = [s for s in actionable if s['estimated_effort'] == 'medium']
        high_effort = [s for s in actionable if s['estimated_effort'] == 'high']

        # Create Wave 2 sub-wave assignments
        wave2_assignments = {
            'wave2a_first_party': {
                'description': 'Remove INVALID first-party skip patterns',
                'assigned_skips': [s for s in high_priority if s['wave1b_category'] == 'invalid_skips'],
                'estimated_count': 0,
                'priority': 'high'
            },
            'wave2b_masking_fixtures': {
                'description': 'Remove skips that mask fixture issues',
                'assigned_skips': [s for s in actionable if 'fixture' in s.get('pattern_type', '')],
                'estimated_count': 0,
                'priority': 'high'
            },
            'wave2c_hidden_failures': {
                'description': 'Remove skips that hide actual failures',
                'assigned_skips': [s for s in actionable if s['risk_level'] == 'low'],
                'estimated_count': 0,
                'priority': 'high'
            }
        }

        # Count assigned skips
        for assignment in wave2_assignments.values():
            assignment['estimated_count'] = len(assignment['assigned_skips'])

        return {
            'total_actionable': len(actionable),
            'priority_breakdown': {
                'high_priority': len(high_priority),
                'medium_priority': len(medium_priority),
                'low_priority': len(low_priority)
            },
            'effort_breakdown': {
                'low_effort': len(low_effort),
                'medium_effort': len(medium_effort),
                'high_effort': len(high_effort)
            },
            'wave2_assignments': wave2_assignments,
            'recommended_approach': self._generate_removal_approach(actionable)
        }

    def _generate_removal_approach(self, actionable_skips: list[dict]) -> dict:
        """Generate recommended approach for skip removal."""
        return {
            'strategy': 'gradual_removal',
            'phases': [
                {
                    'phase': 1,
                    'description': 'Remove high-confidence, low-risk invalid skips',
                    'target_count': len([s for s in actionable_skips if s['removal_priority'] == 'high' and s['risk_level'] == 'low']),
                    'estimated_effort': 'low'
                },
                {
                    'phase': 2,
                    'description': 'Remove medium-confidence invalid skips',
                    'target_count': len([s for s in actionable_skips if s['removal_priority'] == 'medium']),
                    'estimated_effort': 'medium'
                },
                {
                    'phase': 3,
                    'description': 'Review and fix questionable skips',
                    'target_count': len([s for s in actionable_skips if s['estimated_effort'] == 'medium']),
                    'estimated_effort': 'high'
                }
            ],
            'success_criteria': [
                'All invalid skips removed',
                'Remaining skips are properly documented',
                'No tests broken by removal process'
            ]
        }

    def generate_wave1d_report(self) -> dict:
        """Generate Wave 1d categorization report."""
        print("=== Wave 1d: Categorize All Skipped Tests ===")

        categorization = self.categorize_all_skipped_tests()

        if not categorization:
            return None

        # Create summary
        summary = {
            'total_skipped_tests': categorization['total_skipped_tests'],
            'actionable_removals': len(categorization['actionable_removals']),
            'manual_review_required': len(categorization['requires_manual_review']),
            'wave2_targets': categorization['wave2_prioritization']['total_actionable']
        }

        categorization['summary'] = summary

        # Save report
        with open('artifacts/wave1d_categorization_report.json', 'w') as f:
            json.dump(categorization, f, indent=2, default=str)

        # Print summary
        print("\n=== Wave 1d Summary ===")
        print(f"Total skipped tests: {summary['total_skipped_tests']}")
        print(f"Actionable for removal: {summary['actionable_removals']}")
        print(f"Require manual review: {summary['manual_review_required']}")
        print(f"Wave 2 targets: {summary['wave2_targets']}")

        # Print Wave 2 assignments
        wave2_assignments = categorization['wave2_prioritization']['wave2_assignments']
        print("\n=== Wave 2 Assignments ===")
        for wave_id, assignment in wave2_assignments.items():
            print(f"{wave_id}: {assignment['estimated_count']} skips")
            print(f"  {assignment['description']}")

        print("\n📄 Report saved to: artifacts/wave1d_categorization_report.json")

        return categorization


def main():
    """Main execution for Wave 1d."""
    categorizer = SkipTestCategorizer()
    report = categorizer.generate_wave1d_report()

    return report


if __name__ == '__main__':
    main()
