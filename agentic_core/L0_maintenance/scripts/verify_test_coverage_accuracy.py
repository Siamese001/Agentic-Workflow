#!/usr/bin/env python3
"""
Verify test coverage accuracy by spot-checking agents.
Sample agents that claim has_tests=True and verify they actually have tests.
"""
import json
import ast
from pathlib import Path

project_root = Path(__file__).parent.parent

# Load discovery data
with open(project_root / "agent_discovery_full.json", 'r', encoding='utf-8') as f:
    agents = json.load(f)

print("\n" + "="*70)
print("TEST COVERAGE ACCURACY VERIFICATION")
print("="*70)

# Sample agents claiming to have tests
agents_with_tests = [a for a in agents if a.get('has_tests', False)]
print(f"\nTotal agents claiming has_tests=True: {len(agents_with_tests)}")

# Sample 10 random agents
import random
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
sample = random.sample(agents_with_tests, min(10, len(agents_with_tests)))

print(f"\nSpot-checking {len(sample)} agents:")
print("="*70)

verified = 0
false_positives = 0

for agent in sample:
    file_path = agent.get('path', '')
    name = agent.get('class_name', 'Unknown')
    
    if not file_path or file_path == 'Unknown':
        print(f"\n❌ {name}: No file path")
        false_positives += 1
        continue
    
    full_path = project_root / file_path
    if not full_path.exists():
        print(f"\n❌ {name}: File not found: {file_path}")
        false_positives += 1
        continue
    
    # Parse the file
    try:
        source = full_path.read_text(encoding='utf-8')
        tree = ast.parse(source)
        
        # Find the class
        class_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == name:
                class_node = node
                break
        
        if not class_node:
            print(f"\n❌ {name}: Class not found in {file_path}")
            false_positives += 1
            continue
        
        # Check for test indicators
        has_run_self_tests = False
        has_test_methods = False
        has_subatomic_mixin = False
        
        # Check methods
        for item in class_node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == '_run_self_tests':
                    has_run_self_tests = True
                if item.name.startswith('test_'):
                    has_test_methods = True
        
        # Check inheritance
        for base in class_node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr
            if base_name in ('SubatomicTestingMixin', 'SubatomicAgent', 'L0DelegationTestingMixin'):
                has_subatomic_mixin = True
        
        # Verify
        has_any_test = has_run_self_tests or has_test_methods or has_subatomic_mixin
        
        if has_any_test:
            indicators = []
            if has_run_self_tests:
                indicators.append("_run_self_tests")
            if has_test_methods:
                indicators.append("test_ methods")
            if has_subatomic_mixin:
                indicators.append("SubatomicTestingMixin")
            
            print(f"\n✅ {name}")
            print(f"   File: {file_path}")
            print(f"   Test indicators: {', '.join(indicators)}")
            verified += 1
        else:
            print(f"\n❌ {name}: Claims has_tests=True but NO test indicators found")
            print(f"   File: {file_path}")
            false_positives += 1
            
    except Exception as e:
        print(f"\n❌ {name}: Error parsing: {e}")
        false_positives += 1

print("\n" + "="*70)
print("VERIFICATION RESULTS")
print("="*70)
print(f"\nSample size: {len(sample)}")
print(f"Verified correct: {verified}")
print(f"False positives: {false_positives}")

if false_positives > 0:
    print(f"\n⚠️  WARNING: {false_positives}/{len(sample)} agents incorrectly marked as having tests")
    print(f"   This suggests test detection may be over-reporting")
    print(f"   Actual coverage may be lower than 87.2%")
else:
    print(f"\n✅ All sampled agents correctly marked as having tests")
    print(f"   87.2% coverage appears accurate")

# Also check agents claiming NO tests
print("\n" + "="*70)
print("SPOT-CHECK: Agents claiming has_tests=False")
print("="*70)

agents_without_tests = [a for a in agents if not a.get('has_tests', False)]
print(f"\nTotal agents claiming has_tests=False: {len(agents_without_tests)}")

sample_no_tests = random.sample(agents_without_tests, min(5, len(agents_without_tests)))

false_negatives = 0

for agent in sample_no_tests:
    file_path = agent.get('path', '')
    name = agent.get('class_name', 'Unknown')
    
    if not file_path or file_path == 'Unknown':
        continue
    
    full_path = project_root / file_path
    if not full_path.exists():
        continue
    
    try:
        source = full_path.read_text(encoding='utf-8')
        tree = ast.parse(source)
        
        class_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == name:
                class_node = node
                break
        
        if not class_node:
            continue
        
        # Check for test indicators
        has_run_self_tests = any(
            item.name == '_run_self_tests' 
            for item in class_node.body 
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        
        if has_run_self_tests:
            print(f"\n⚠️  {name}: Claims NO tests but has _run_self_tests")
            print(f"   File: {file_path}")
            false_negatives += 1
        else:
            print(f"\n✅ {name}: Correctly marked as no tests")
            
    except Exception:
        pass

if false_negatives > 0:
    print(f"\n⚠️  WARNING: {false_negatives} agents incorrectly marked as NOT having tests")
else:
    print(f"\n✅ No false negatives detected")
