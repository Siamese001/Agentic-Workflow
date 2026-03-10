"""Parse anti-pattern scan results and identify all violations by category."""
import sys

def parse_scan_results(filename):
    """Parse scan results and categorize violations."""
    with open(filename, encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    violations = {
        'silent_swallower': [],
        'magic_configuration': [],
        'path_fragility': [],
        'global_mutation': [],
        'type_erasure': []
    }
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if '[FAIL]' in line and '.py:' in line:
            # Extract file and line number
            fail_info = line
            # Check next line for pattern type
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                for pattern in violations.keys():
                    if f'[{pattern}]' in next_line:
                        violations[pattern].append(fail_info)
                        break
        i += 1
    
    return violations

if __name__ == '__main__':
    violations = parse_scan_results('scan_results.txt')
    
    print("=" * 80)
    print("ANTI-PATTERN VIOLATIONS BY CATEGORY")
    print("=" * 80)
    
    total = 0
    for pattern, items in sorted(violations.items(), key=lambda x: len(x[1])):
        count = len(items)
        total += count
        if count > 0:
            print(f"\n{pattern.upper()}: {count} violations")
            for item in items[:10]:  # Show first 10
                print(f"  {item}")
            if count > 10:
                print(f"  ... and {count - 10} more")
    
    print(f"\n{'=' * 80}")
    print(f"TOTAL VIOLATIONS: {total}")
    print(f"{'=' * 80}")
