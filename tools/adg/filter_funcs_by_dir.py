#!/usr/bin/env python3
"""Filter unused functions by directory for micro-wave execution."""

import argparse
import json
import sys


def filter_by_directory(input_path: str, output_path: str, dir_pattern: str):
    """Filter unused functions to only include those matching directory pattern."""
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)

    filtered = [
        func for func in data.get('unused_functions', [])
        if dir_pattern in func.get('file', '')
    ]

    output_data = {
        'adg_database': data.get('adg_database'),
        'directory': dir_pattern,
        'unused_functions': filtered
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f'Filtered {len(filtered)} functions matching "{dir_pattern}" to {output_path}')
    return len(filtered)


def main():
    parser = argparse.ArgumentParser(description='Filter unused functions by directory')
    parser.add_argument('--input', required=True, help='Input JSON file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--dir-pattern', required=True, help='Directory pattern to match')

    args = parser.parse_args()

    count = filter_by_directory(args.input, args.output, args.dir_pattern)
    return 0 if count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
