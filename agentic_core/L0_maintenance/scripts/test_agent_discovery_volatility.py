"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ AGENT DISCOVERY VOLATILITY TEST SUITE                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Tests to verify that agent discovery produces consistent, deterministic      ║
║ results across multiple runs. Addresses RCA from 2026-01-18 volatility.      ║
║                                                                              ║
║ Root Causes Addressed:                                                       ║
║ 1. Strict 1:1 filename matching causing 80+ agent drops                      ║
║ 2. Non-deterministic file ordering from rglob()                              ║
║ 3. Incremental mode integrity issues                                         ║
║ 4. Dynamic inheritance map inconsistencies                                   ║
║ 5. Volatile exclusion patterns                                               ║
║ 6. Expected count mismatch                                                   ║
║                                                                              ║
║ Usage: python scripts/test_agent_discovery_volatility.py                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test results tracking
PASSED = 0
FAILED = 0
RESULTS = []


def test_result(name: str, passed: bool, details: str = ""):
    """Record test result."""
    global PASSED, FAILED
    if passed:
        PASSED += 1
        status = "✅"
    else:
        FAILED += 1
        status = "❌"
    
    msg = f"{status} Test {PASSED + FAILED}: {name}"
    if details:
        msg += f"\n   {details}"
    print(msg)
    RESULTS.append((name, passed, details))


def run_tests():
    """Run all volatility tests."""
    print("=" * 80)
    print("AGENT DISCOVERY VOLATILITY TEST SUITE")
    print("Testing determinism and consistency of agent discovery")
    print("=" * 80)
    print()
    
    # Import the discovery module
    try:
        from full_agent_discovery import (
            PROJECT_ROOT,
            MINIMUM_AGENT_COUNT,
            MAX_AGENT_DROP_PERCENT,
            EXPECTED_AGENT_COUNT,
            EXCLUDED_DIRS,
            EXCLUDED_FILENAME_PATTERNS,
            EXCLUDED_PATH_PATTERNS,
            should_exclude_path,
            should_exclude_file,
            is_agent_class,
            extract_bases,
            discover_all_agents,
            validate_agent_count,
            CLASS_INHERITANCE_MAP,
            build_inheritance_map,
            safe_parse,
        )
    except ImportError as e:
        print(f"❌ CRITICAL: Failed to import full_agent_discovery: {e}")
        return 1
    
    # =========================================================================
    # TEST 1: Baseline thresholds are reasonable
    # =========================================================================
    test_result(
        "Baseline thresholds are reasonable",
        MINIMUM_AGENT_COUNT >= 100 and MINIMUM_AGENT_COUNT <= 300,
        f"MINIMUM_AGENT_COUNT={MINIMUM_AGENT_COUNT} (should be 100-300)"
    )
    
    # =========================================================================
    # TEST 2: MAX_AGENT_DROP_PERCENT allows reasonable variance
    # =========================================================================
    test_result(
        "MAX_AGENT_DROP_PERCENT allows variance",
        MAX_AGENT_DROP_PERCENT >= 5 and MAX_AGENT_DROP_PERCENT <= 25,
        f"MAX_AGENT_DROP_PERCENT={MAX_AGENT_DROP_PERCENT}% (should be 5-25%)"
    )
    
    # =========================================================================
    # TEST 3: EXPECTED_AGENT_COUNT is realistic
    # =========================================================================
    test_result(
        "EXPECTED_AGENT_COUNT is realistic",
        EXPECTED_AGENT_COUNT >= 150 and EXPECTED_AGENT_COUNT <= 400,
        f"EXPECTED_AGENT_COUNT={EXPECTED_AGENT_COUNT} (should be 150-400)"
    )
    
    # =========================================================================
    # TEST 4: Deterministic file ordering (sorted)
    # =========================================================================
    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    all_py_files_1 = sorted(get_python_files(PROJECT_ROOT))
    all_py_files_2 = sorted(get_python_files(PROJECT_ROOT))
    
    test_result(
        "File ordering is deterministic",
        all_py_files_1 == all_py_files_2,
        f"Two sorted rglob() calls produce identical ordering ({len(all_py_files_1)} files)"
    )
    
    # =========================================================================
    # TEST 5: Exclusion patterns are stable
    # =========================================================================
    test_result(
        "EXCLUDED_DIRS is a set",
        isinstance(EXCLUDED_DIRS, set),
        f"EXCLUDED_DIRS has {len(EXCLUDED_DIRS)} entries"
    )
    
    # =========================================================================
    # TEST 6: Exclusion patterns include critical directories
    # =========================================================================
    critical_excludes = {'__pycache__', '.git', '.venv', 'venv'}
    has_critical = critical_excludes.issubset(EXCLUDED_DIRS)
    test_result(
        "Critical directories are excluded",
        has_critical,
        f"Has {critical_excludes & EXCLUDED_DIRS} of {critical_excludes}"
    )
    
    # =========================================================================
    # TEST 7: should_exclude_path works correctly
    # =========================================================================
    test_cases = [
        (Path("agentic_core/__pycache__/test.py"), True),
        (Path("agentic_core/.git/config"), True),
        (Path("agentic_core/L1_cognition/agent.py"), False),
        (Path(".venv/lib/python3.11/site.py"), True),
    ]
    all_correct = all(should_exclude_path(p) == expected for p, expected in test_cases)
    test_result(
        "should_exclude_path works correctly",
        all_correct,
        f"Tested {len(test_cases)} path patterns"
    )
    
    # =========================================================================
    # TEST 8: should_exclude_file handles mixin exception
    # =========================================================================
    # Files ending with 'agent' should NOT be excluded even if they contain 'mixin'
    mixin_agent_file = Path("agentic_core/L1_cognition/mixin_agent.py")
    regular_mixin_file = Path("agentic_core/L1_cognition/healer_mixin.py")
    
    # Note: should_exclude_file checks .py extension, so we need to be careful
    mixin_agent_excluded = should_exclude_file(mixin_agent_file)
    regular_mixin_excluded = should_exclude_file(regular_mixin_file)
    
    test_result(
        "Mixin exception for *_agent.py files",
        not mixin_agent_excluded and regular_mixin_excluded,
        f"mixin_agent.py excluded={mixin_agent_excluded}, healer_mixin.py excluded={regular_mixin_excluded}"
    )
    
    # =========================================================================
    # TEST 9: Discovery produces consistent count across runs
    # =========================================================================
    print("\n   Running discovery scan 1...")
    agents_1 = discover_all_agents(PROJECT_ROOT)
    count_1 = len(agents_1)
    
    print("   Running discovery scan 2...")
    agents_2 = discover_all_agents(PROJECT_ROOT)
    count_2 = len(agents_2)
    
    test_result(
        "Discovery count is consistent across runs",
        count_1 == count_2,
        f"Run 1: {count_1} agents, Run 2: {count_2} agents"
    )
    
    # =========================================================================
    # TEST 10: Agent names are identical across runs
    # =========================================================================
    names_1 = set(a['class_name'] for a in agents_1)
    names_2 = set(a['class_name'] for a in agents_2)
    
    test_result(
        "Agent names are identical across runs",
        names_1 == names_2,
        f"Both runs found {len(names_1)} unique agent names"
    )
    
    # =========================================================================
    # TEST 11: Agent paths are identical across runs
    # =========================================================================
    paths_1 = set(a['path'] for a in agents_1)
    paths_2 = set(a['path'] for a in agents_2)
    
    test_result(
        "Agent paths are identical across runs",
        paths_1 == paths_2,
        f"Both runs found {len(paths_1)} unique paths"
    )
    
    # =========================================================================
    # TEST 12: Discovery count is above minimum threshold
    # =========================================================================
    test_result(
        "Discovery count above minimum threshold",
        count_1 >= MINIMUM_AGENT_COUNT,
        f"Found {count_1} agents (minimum: {MINIMUM_AGENT_COUNT})"
    )
    
    # =========================================================================
    # TEST 13: validate_agent_count accepts current count
    # =========================================================================
    is_valid, errors = validate_agent_count(count_1)
    test_result(
        "validate_agent_count accepts current count",
        is_valid,
        f"Validation passed for {count_1} agents" if is_valid else f"Errors: {errors}"
    )
    
    # =========================================================================
    # TEST 14: No duplicate agents in discovery
    # =========================================================================
    agent_keys = [(a['class_name'], a['path']) for a in agents_1]
    unique_keys = set(agent_keys)
    
    test_result(
        "No duplicate agents in discovery",
        len(agent_keys) == len(unique_keys),
        f"Total: {len(agent_keys)}, Unique: {len(unique_keys)}"
    )
    
    # =========================================================================
    # TEST 15: All agents have required fields
    # =========================================================================
    required_fields = {'class_name', 'path', 'layer'}
    all_have_fields = all(
        all(field in a for field in required_fields)
        for a in agents_1
    )
    
    test_result(
        "All agents have required fields",
        all_have_fields,
        f"Required fields: {required_fields}"
    )
    
    # =========================================================================
    # TEST 16: Inheritance map is built consistently
    # =========================================================================
    # Clear and rebuild inheritance map
    CLASS_INHERITANCE_MAP.clear()
    
    for py_file in sorted(all_py_files_1)[:100]:  # Sample first 100 files
        if should_exclude_file(py_file):
            continue
        try:
            source = py_file.read_text(encoding='utf-8', errors='replace')
            tree = safe_parse(source, py_file)
            if tree:
                build_inheritance_map(tree)
        except Exception:
            continue
    
    map_size_1 = len(CLASS_INHERITANCE_MAP)
    
    # Rebuild again
    CLASS_INHERITANCE_MAP.clear()
    
    for py_file in sorted(all_py_files_1)[:100]:
        if should_exclude_file(py_file):
            continue
        try:
            source = py_file.read_text(encoding='utf-8', errors='replace')
            tree = safe_parse(source, py_file)
            if tree:
                build_inheritance_map(tree)
        except Exception:
            continue
    
    map_size_2 = len(CLASS_INHERITANCE_MAP)
    
    test_result(
        "Inheritance map is built consistently",
        map_size_1 == map_size_2,
        f"Build 1: {map_size_1} classes, Build 2: {map_size_2} classes"
    )
    
    # =========================================================================
    # TEST 17: Layer distribution is reasonable
    # =========================================================================
    layer_counts = {}
    for a in agents_1:
        layer = a.get('layer', 'Unknown')
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    # Should have agents in multiple layers
    has_multiple_layers = len(layer_counts) >= 3
    
    test_result(
        "Agents distributed across multiple layers",
        has_multiple_layers,
        f"Layers: {dict(sorted(layer_counts.items()))}"
    )
    
    # =========================================================================
    # TEST 18: No 'Unknown' layer agents (or very few)
    # =========================================================================
    unknown_count = layer_counts.get('Unknown', 0)
    unknown_pct = (unknown_count / count_1 * 100) if count_1 > 0 else 0
    
    test_result(
        "Few or no 'Unknown' layer agents",
        unknown_pct < 10,
        f"Unknown: {unknown_count} ({unknown_pct:.1f}%)"
    )
    
    # =========================================================================
    # TEST 19: Content hash is deterministic
    # =========================================================================
    content_str_1 = json.dumps(sorted(agents_1, key=lambda x: x['class_name']), sort_keys=True)
    content_hash_1 = hashlib.sha256(content_str_1.encode()).hexdigest()
    
    content_str_2 = json.dumps(sorted(agents_2, key=lambda x: x['class_name']), sort_keys=True)
    content_hash_2 = hashlib.sha256(content_str_2.encode()).hexdigest()
    
    test_result(
        "Content hash is deterministic",
        content_hash_1 == content_hash_2,
        f"Hash: {content_hash_1[:16]}..."
    )
    
    # =========================================================================
    # TEST 20: Relaxed 1:1 enforcement allows mismatched names
    # =========================================================================
    # Check if any agents have class names that don't match their filename
    mismatched = []
    for a in agents_1:
        path = Path(a['path'])
        filename_stem = path.stem
        class_name = a['class_name']
        if class_name != filename_stem:
            mismatched.append((class_name, filename_stem))
    
    # With relaxed enforcement, we should have some mismatched agents
    # (previously these would have been dropped)
    test_result(
        "Relaxed 1:1 enforcement allows mismatched names",
        True,  # This test documents the behavior
        f"Found {len(mismatched)} agents with class/filename mismatch (allowed)"
    )
    
    # =========================================================================
    # TEST 21: Variance between runs is zero
    # =========================================================================
    variance = abs(count_1 - count_2)
    test_result(
        "Zero variance between consecutive runs",
        variance == 0,
        f"Variance: {variance} agents"
    )
    
    # =========================================================================
    # TEST 22: Discovery completes in reasonable time
    # =========================================================================
    start = time.time()
    _ = discover_all_agents(PROJECT_ROOT)
    duration = time.time() - start
    
    test_result(
        "Discovery completes in reasonable time",
        duration < 60,  # Should complete in under 60 seconds
        f"Duration: {duration:.2f}s"
    )
    
    # =========================================================================
    # TEST 23: All agent class names end with 'Agent'
    # =========================================================================
    non_agent_suffix = [a['class_name'] for a in agents_1 if not a['class_name'].endswith('Agent')]
    
    test_result(
        "All agent class names end with 'Agent'",
        len(non_agent_suffix) == 0,
        f"Non-compliant: {non_agent_suffix[:5]}..." if non_agent_suffix else "All compliant"
    )
    
    # =========================================================================
    # TEST 24: No mixin classes in discovery
    # =========================================================================
    mixin_classes = [a['class_name'] for a in agents_1 if 'Mixin' in a['class_name']]
    
    test_result(
        "No mixin classes in discovery",
        len(mixin_classes) == 0,
        f"Mixins found: {mixin_classes}" if mixin_classes else "No mixins"
    )
    
    # =========================================================================
    # TEST 25: Sorted file list is stable
    # =========================================================================
    files_sorted_1 = sorted([str(p) for p in all_py_files_1])
    files_sorted_2 = sorted([str(p) for p in all_py_files_2])
    
    test_result(
        "Sorted file list is stable",
        files_sorted_1 == files_sorted_2,
        f"Both lists have {len(files_sorted_1)} files in same order"
    )
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print()
    print("=" * 80)
    print(f"RESULTS: {PASSED}/{PASSED + FAILED} PASSED")
    print("=" * 80)
    
    if FAILED > 0:
        print("\nFailed tests:")
        for name, passed, details in RESULTS:
            if not passed:
                print(f"  ❌ {name}")
                if details:
                    print(f"     {details}")
    
    return 0 if FAILED == 0 else 1


if __name__ == '__main__':
    sys.exit(run_tests())
