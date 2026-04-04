#!/usr/bin/env python3
"""
Wave 4c-h: Comprehensive guardian swallow to fixture conversion across all layers.

This script converts guardian swallow patterns to proper pytest fixtures
across all remaining layers (L1-L6).
"""

import json
import re
from pathlib import Path


def convert_guardian_swallow_patterns(file_path: Path) -> dict:
    """Convert guardian swallow patterns to fixtures using regex and simple transformations."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Count patterns before conversion
        original_patterns = len(re.findall(r'# guardian: allow-[a-zA-Z_-]+', content))
        original_exceptions = len(re.findall(r'except\s+\w+.*:\s*pass', content))

        # Common conversions using regex
        conversions = [
            # Convert "except Exception: pass" to pytest.raises
            (r'except\s+(\w+):\s*pass', r'with pytest.raises(\1):'),

            # Convert "except Exception: # guardian: allow-silent-swallow"
            (r'except\s+(\w+):\s*#\s*guardian:\s*allow-silent-swallow.*', r'with pytest.raises(\1):'),

            # Convert "except Exception as e: pass"
            (r'except\s+(\w+)\s+as\s+\w+:\s*pass', r'with pytest.raises(\1):'),

            # Convert "except Exception:" with guardian comment to pytest.raises
            (r'except\s+(\w+):\s*#\s*guardian:.*allow-[a-zA-Z_-]+.*', r'with pytest.raises(\1):'),

            # Convert bare "except:" to pytest.raises(Exception)
            (r'except:\s*pass', r'with pytest.raises(Exception):'),
            (r'except:\s*#\s*guardian:.*allow-[a-zA-Z_-]+.*', r'with pytest.raises(Exception):'),
        ]

        new_content = content
        for pattern, replacement in conversions:
            new_content = re.sub(pattern, replacement, new_content, flags=re.MULTILINE)

        # Add pytest import if needed
        if 'pytest.raises' in new_content and 'import pytest' not in new_content:
            # Add import after existing imports or at the top
            lines = new_content.split('\n')
            insert_pos = 0

            # Skip docstring
            if lines and lines[0].startswith('"""') or lines[0].startswith("'''"):
                # Find end of docstring
                in_docstring = True
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() in ['"""', "'''"]:
                        insert_pos = i + 1
                        in_docstring = False
                        break
                if in_docstring:
                    insert_pos = 0
            else:
                # Skip existing imports
                while (insert_pos < len(lines) and
                       (lines[insert_pos].startswith('import ') or
                        lines[insert_pos].startswith('from ') or
                        lines[insert_pos].strip() == '')):
                    insert_pos += 1

            lines.insert(insert_pos, 'import pytest')
            new_content = '\n'.join(lines)

        # Count patterns after conversion
        new_patterns = len(re.findall(r'# guardian: allow-[a-zA-Z_-]+', new_content))
        new_exceptions = len(re.findall(r'except\s+\w+.*:\s*pass', new_content))

        changes_made = original_content != new_content

        return {
            'file': str(file_path),
            'success': True,
            'changes_made': changes_made,
            'original_patterns': original_patterns,
            'original_exceptions': original_exceptions,
            'new_patterns': new_patterns,
            'new_exceptions': new_exceptions,
            'patterns_converted': original_patterns - new_patterns,
            'exceptions_converted': original_exceptions - new_exceptions,
            'new_content': new_content if changes_made else None
        }

    except Exception as e:
        return {
            'file': str(file_path),
            'success': False,
            'error': str(e)
        }


def convert_layer_files(layer_name: str, files: list[dict]) -> list[dict]:
    """Convert guardian swallow patterns for a specific layer."""
    print(f"\n=== Converting {layer_name} Guardian Swallow Patterns ===")

    files_needing = [f for f in files if f.get('needs_conversion', False)]
    print(f"Found {len(files_needing)} {layer_name} files needing conversion")

    results = []

    for file_info in files_needing:
        file_path = Path(file_info['file'])
        print(f"  Processing: {file_path.name}")

        result = convert_guardian_swallow_patterns(file_path)
        results.append(result)

        if result['success'] and result['changes_made']:
            # Write the converted content
            file_path.write_text(result['new_content'], encoding='utf-8')

            patterns = result['patterns_converted']
            exceptions = result['exceptions_converted']

            print(f"    ✅ Converted - {patterns} patterns, {exceptions} exceptions")
        elif result['success'] and not result['changes_made']:
            print("    ⚪ No changes needed")
        else:
            print(f"    ❌ Failed - {result.get('error', 'Unknown error')}")

    # Summary for this layer
    successful = len([r for r in results if r['success']])
    with_changes = len([r for r in results if r['success'] and r['changes_made']])
    total = len(results)

    print(f"  {layer_name} Summary: {with_changes}/{total} files converted, {successful}/{total} successful")

    return results


def main():
    """Convert guardian swallow patterns across all remaining layers."""
    print("=== Wave 4c-h: Comprehensive Guardian Swallow to Fixture Conversion ===")

    # Load the analysis from Wave 4a
    with open('artifacts/guardian_swallow_analysis.json') as f:
        data = json.load(f)

    all_results = []

    # Process each layer (L1-L6)
    for layer in ['L1_cognition', 'L2_execution', 'L3_orchestration', 'L4_state', 'L5_safety', 'L6_observability']:
        if layer in data['layers'] and data['layers'][layer]:
            layer_results = convert_layer_files(layer, data['layers'][layer])
            all_results.extend(layer_results)

    # Process "other" files (non-layer specific)
    if data['layers']['other']:
        print("\n=== Converting Other Files Guardian Swallow Patterns ===")
        other_files = [f for f in data['layers']['other'] if f.get('needs_conversion', False)]

        # Limit to top 20 "other" files to avoid excessive changes
        top_other = sorted(other_files,
                          key=lambda x: x.get('total_swallows', 0) + x.get('regex_matches', 0),
                          reverse=True)[:20]

        print(f"Processing top 20 of {len(other_files)} other files")

        for file_info in top_other:
            file_path = Path(file_info['file'])
            print(f"  Processing: {file_path.name}")

            result = convert_guardian_swallow_patterns(file_path)
            all_results.append(result)

            if result['success'] and result['changes_made']:
                file_path.write_text(result['new_content'], encoding='utf-8')
                patterns = result['patterns_converted']
                exceptions = result['exceptions_converted']
                print(f"    ✅ Converted - {patterns} patterns, {exceptions} exceptions")

    # Overall summary
    successful = len([r for r in all_results if r['success']])
    with_changes = len([r for r in all_results if r['success'] and r['changes_made']])
    total = len(all_results)

    total_patterns = sum(r.get('patterns_converted', 0) for r in all_results)
    total_exceptions = sum(r.get('exceptions_converted', 0) for r in all_results)

    print("\n=== Wave 4c-h Overall Summary ===")
    print(f"Files processed: {total}")
    print(f"Successfully converted: {successful}")
    print(f"Files with changes: {with_changes}")
    print(f"Total patterns converted: {total_patterns}")
    print(f"Total exceptions converted: {total_exceptions}")

    # Save results
    output = {
        'summary': {
            'total_files': total,
            'successful': successful,
            'with_changes': with_changes,
            'total_patterns_converted': total_patterns,
            'total_exceptions_converted': total_exceptions
        },
        'all_results': all_results
    }

    with open('artifacts/wave4ch_conversion_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\nDetailed results saved to: artifacts/wave4ch_conversion_results.json")


if __name__ == '__main__':
    main()
