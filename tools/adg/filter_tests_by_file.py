#!/usr/bin/env python3
"""Filter unused tests by file for micro-wave execution."""

import argparse
import json
import sys


def filter_by_file(input_path: str, output_path: str, file_pattern: str):
    """Filter unused tests to only include those matching file pattern."""
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)

    filtered = [
        test for test in data.get('unused_tests', [])
        if file_pattern in test.get('file', '')
    ]

    output_data = {
        'adg_database': data.get('adg_database'),
        'directory': data.get('directory'),
        'unused_tests': filtered,
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f'Filtered {len(filtered)} tests matching "{file_pattern}" to {output_path}')
    return len(filtered)


def main():
    parser = argparse.ArgumentParser(description='Filter unused tests by file pattern')
    parser.add_argument('--input', required=True, help='Input JSON file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--file-pattern', required=True, help='File pattern to match')

    args = parser.parse_args()

    count = filter_by_file(args.input, args.output, args.file_pattern)
    return 0 if count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
