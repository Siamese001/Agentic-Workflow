#!/usr/bin/env python3
"""Categorize syntax errors by type and create fix phases."""

import json


def categorize_errors():
    """Load and categorize syntax errors."""
    with open('syntax_error_report.json') as f:
        report = json.load(f)

    # Group errors by type and create phases
    phases = {
        'Phase 1 - Critical Base Agents': [],
        'Phase 2 - Cache Layer': [],
        'Phase 3 - Config Core': [],
        'Phase 4 - Interfaces & Mixins': [],
        'Phase 5 - Remaining Files': []
    }

    for err in report['details']:
        file_path = err['file']
        msg = err['message'].lower()

        # Categorize based on file path and error type
        if 'base_agents' in file_path:
            phases['Phase 1 - Critical Base Agents'].append(err)
        elif 'cache' in file_path:
            phases['Phase 2 - Cache Layer'].append(err)
        elif 'config/core' in file_path:
            phases['Phase 3 - Config Core'].append(err)
        elif 'interfaces' in file_path:
            phases['Phase 4 - Interfaces & Mixins'].append(err)
        else:
            phases['Phase 5 - Remaining Files'].append(err)

    # Print summary
    print('=== PHASED FIX PLAN ===')
    print()
    for phase, errors in phases.items():
        print(f'{phase}: {len(errors)} files')
        for err in errors[:3]:  # Show first 3 examples
            print(f'  - {err["file"]}:{err["line"]} - {err["message"][:60]}...')
        if len(errors) > 3:
            print(f'  ... and {len(errors) - 3} more')
        print()

    # Save phase plan
    with open('syntax_fix_phases.json', 'w') as f:
        json.dump(phases, f, indent=2)

    print('Phase plan saved to: syntax_fix_phases.json')
    return phases

if __name__ == '__main__':
    categorize_errors()
