"""Analyze test failures and categorize them for wave-based fixing."""
import subprocess
import sys
import re
from collections import defaultdict

def analyze_test_failures():
    # Run pytest and capture output
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/unit', '--tb=line', '-q', '--continue-on-collection-errors'],
        capture_output=True,
        text=True,
        cwd=r'c:\Git\Agentic-Workflow'
    )
    
    output = result.stdout + result.stderr
    
    # Parse failures
    failed_tests = []
    error_patterns = defaultdict(list)
    
    lines = output.split('\n')
    current_test = None
    
    for line in lines:
        # Look for test failure lines
        match = re.match(r'(FAILED|ERROR)\s+(tests/\S+)', line)
        if match:
            current_test = match.group(2)
            failed_tests.append(current_test)
        
        # Look for error patterns
        if current_test:
            if 'No module named' in line:
                module = re.search(r"No module named '([^']+)'", line)
                if module:
                    error_patterns[f"Missing module: {module.group(1)}"].append(current_test)
            elif 'ImportError' in line:
                error_patterns['ImportError'].append(current_test)
            elif 'AttributeError' in line:
                error_patterns['AttributeError'].append(current_test)
            elif 'NameError' in line:
                error_patterns['NameError'].append(current_test)
    
    # Summary
    print("=" * 80)
    print("TEST FAILURE ANALYSIS")
    print("=" * 80)
    print(f"\nTotal failed tests: {len(failed_tests)}")
    print(f"\nError pattern breakdown:")
    print("-" * 80)
    
    for pattern, tests in sorted(error_patterns.items(), key=lambda x: -len(x[1])):
        print(f"\n{pattern}: {len(tests)} tests")
        for test in tests[:5]:  # Show first 5
            print(f"  - {test}")
        if len(tests) > 5:
            print(f"  ... and {len(tests) - 5} more")
    
    # Wave recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDED WAVES")
    print("=" * 80)
    
    wave_num = 2  # Wave 1 was collection fixes
    for pattern, tests in sorted(error_patterns.items(), key=lambda x: -len(x[1])):
        if len(tests) >= 5:  # Only patterns with 5+ tests
            print(f"\nWave {wave_num}: {pattern} ({len(tests)} tests)")
            wave_num += 1

if __name__ == '__main__':
    analyze_test_failures()
