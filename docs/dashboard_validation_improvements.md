# Dashboard Data Validation Improvements

## Root Cause Analysis of Past Issues

### Issue 1: Missing Complexity Health Calculation
**Problem**: Dashboard showed "Typed %" instead of "Complexity Health %"
**Root Cause**: `regenerate_dashboard_data.py` wasn't calling `calc_complexity_health()` from SSOT
**Detection Gap**: No validation that all SSOT-defined metrics were included in generated data

### Issue 2: Field Name Mismatches
**Problem**: Validation script used wrong field names (`has_mixin` vs `has_healing`)
**Root Cause**: No single source of truth for field name mappings
**Detection Gap**: No automated check that field names match between source data and SSOT

### Issue 3: Alphabetical vs Canonical Sort Order
**Problem**: Data sorted alphabetically instead of logical layer order (TOTAL, Base, L6→L0, Apps)
**Root Cause**: `sorted(territories.items())` used default alphabetical sort
**Detection Gap**: E2E tests only checked "TOTAL at top", not full canonical order

### Issue 4: Data Type Inconsistencies
**Problem**: Source data structure changed (dict → list) breaking validation
**Root Cause**: No schema validation on source data structure
**Detection Gap**: No type checking or structure validation

---

## Proposed Validation Framework

### 1. **Schema Validation Layer**

#### A. SSOT Compliance Check
Validate that generated dashboard data includes ALL metrics defined in SSOT.

```python
def validate_ssot_compliance(dashboard_data):
    """Ensure all SSOT-defined metrics are present in dashboard data."""
    from scripts.dashboard_ssot_definitions import (
        COLUMN_HEAL_CAP, COLUMN_INVOCATION, COLUMN_TEST, 
        COLUMN_HARDENED, COLUMN_COMPLEXITY_HEALTH, COLUMN_TYPED,
        COLUMN_DOCUMENTED, COLUMN_SCHEMA_STRICTNESS, 
        COLUMN_CANONICAL_INHERITANCE, COLUMN_CODE_QUALITY
    )
    
    required_columns = [
        COLUMN_HEAL_CAP, COLUMN_INVOCATION, COLUMN_TEST,
        COLUMN_HARDENED, COLUMN_COMPLEXITY_HEALTH, COLUMN_TYPED,
        COLUMN_DOCUMENTED, COLUMN_SCHEMA_STRICTNESS,
        COLUMN_CANONICAL_INHERITANCE, COLUMN_CODE_QUALITY
    ]
    
    failures = []
    for row in dashboard_data:
        for col in required_columns:
            if col not in row:
                failures.append(f"{row['Territory']}: missing '{col}'")
    
    return failures
```

**Benefit**: Catches missing metrics immediately after data generation.

---

#### B. Field Name Consistency Check
Validate field names match between source data, SSOT, and dashboard.

```python
def validate_field_name_consistency():
    """Cross-check field names across all data layers."""
    from scripts.dashboard_ssot_definitions import (
        FIELD_HAS_HEALING, FIELD_HAS_INVOCATION, FIELD_HAS_TEST,
        FIELD_TYPED, FIELD_DOCUMENTED, FIELD_SCHEMA_STRICTNESS,
        FIELD_CYCLOMATIC_COMPLEXITY
    )
    
    # Load sample agent from source
    with open('agent_discovery_full.json') as f:
        agents = json.load(f)
        sample = agents[0] if agents else {}
    
    # Check SSOT field names exist in source data
    ssot_fields = [
        FIELD_HAS_HEALING, FIELD_HAS_INVOCATION, FIELD_HAS_TEST,
        FIELD_TYPED, FIELD_DOCUMENTED, FIELD_SCHEMA_STRICTNESS,
        FIELD_CYCLOMATIC_COMPLEXITY
    ]
    
    missing = [f for f in ssot_fields if f not in sample]
    
    if missing:
        return f"❌ SSOT fields missing from source: {missing}"
    return "✅ Field names consistent"
```

**Benefit**: Detects field name drift between source data and SSOT definitions.

---

### 2. **Source-to-Dashboard Data Integrity Checks**

#### A. Calculation Verification
Validate that dashboard metrics match recalculated values from source.

```python
def validate_calculation_integrity(territory_name):
    """Verify dashboard values match SSOT calculations from source."""
    from scripts.dashboard_ssot_definitions import (
        calc_heal_cap_pct, calc_complexity_health, calc_avg_cc
    )
    
    # Load source data
    with open('agent_discovery_full.json') as f:
        agents = json.load(f)
    
    # Filter by territory
    territory_agents = [a for a in agents if a.get('territory') == territory_name]
    
    # Calculate expected values
    expected_heal_cap = calc_heal_cap_pct(territory_agents)
    expected_avg_cc = calc_avg_cc(territory_agents)
    expected_complexity = calc_complexity_health(expected_avg_cc)
    
    # Load dashboard data
    with open('agentic_core/L6_observability/dashboards/data/dashboard_data.js') as f:
        content = f.read().replace('window.dashboardData = ', '').strip().rstrip(';')
        dashboard_data = json.loads(content)
    
    # Find territory row
    row = next((r for r in dashboard_data if r['Territory'] == territory_name), None)
    
    # Compare
    tolerance = 0.1  # Allow 0.1% difference for floating point
    failures = []
    
    if abs(row['Heal Cap %'] - expected_heal_cap) > tolerance:
        failures.append(f"Heal Cap: expected {expected_heal_cap}, got {row['Heal Cap %']}")
    
    if abs(row['Complexity Health %'] - expected_complexity) > tolerance:
        failures.append(f"Complexity Health: expected {expected_complexity}, got {row['Complexity Health %']}")
    
    return failures
```

**Benefit**: Catches calculation errors and ensures dashboard reflects actual source data.

---

#### B. Sample-Based Spot Checks
Randomly validate 5 territories per test run.

```python
def validate_random_sample():
    """Spot-check random territories for data integrity."""
    import random
    
    with open('agentic_core/L6_observability/dashboards/data/dashboard_data.js') as f:
        content = f.read().replace('window.dashboardData = ', '').strip().rstrip(';')
        dashboard_data = json.loads(content)
    
    # Exclude TOTAL
    territories = [r for r in dashboard_data if r['Territory'] != 'TOTAL']
    
    # Sample 5 random territories
    sample = random.sample(territories, min(5, len(territories)))
    
    failures = []
    for row in sample:
        territory_failures = validate_calculation_integrity(row['Territory'])
        if territory_failures:
            failures.extend([f"{row['Territory']}: {f}" for f in territory_failures])
    
    return failures
```

**Benefit**: Provides statistical confidence without testing every territory every time.

---

### 3. **Sort Order Validation**

#### Current Implementation (Good)
```python
expected_order = [
    'TOTAL', 'Base/Base Class', 'L6_Observability/Metrics', ...
]

for i, expected_territory in enumerate(expected_order):
    if table_rows[i] != expected_territory:
        failures.append(f"Position {i}: expected '{expected_territory}', got '{table_rows[i]}'")
```

#### Enhancement: Validate Source Data Order
```python
def validate_source_data_order():
    """Ensure dashboard_data.js has canonical order BEFORE rendering."""
    with open('agentic_core/L6_observability/dashboards/data/dashboard_data.js') as f:
        content = f.read().replace('window.dashboardData = ', '').strip().rstrip(';')
        data = json.loads(content)
    
    expected_order = ['TOTAL', 'Base/Base Class', 'L6_Observability/Metrics', ...]
    
    actual_order = [row['Territory'] for row in data]
    
    if actual_order != expected_order:
        return f"❌ Source data not in canonical order: {actual_order[:5]}..."
    return "✅ Source data in canonical order"
```

**Benefit**: Catches sort order issues at data generation time, not just rendering time.

---

### 4. **Data Type & Range Validation**

#### A. Type Checking
```python
def validate_data_types(dashboard_data):
    """Ensure all fields have correct data types."""
    failures = []
    
    for row in dashboard_data:
        # Territory should be string
        if not isinstance(row.get('Territory'), str):
            failures.append(f"Territory is not string: {row.get('Territory')}")
        
        # Percentages should be float/int
        percentage_fields = [
            'Heal Cap %', 'Invocation %', 'Test %', 'MCP Hardened %',
            'Complexity Health %', 'Typed %', 'Documented %',
            'Schema Strictness %', 'Canonical Inheritance %'
        ]
        
        for field in percentage_fields:
            value = row.get(field)
            if value is not None and not isinstance(value, (int, float)):
                failures.append(f"{row['Territory']}: {field} is not numeric: {value}")
    
    return failures
```

**Benefit**: Catches type errors that could cause rendering failures.

---

#### B. Range Validation (Already Implemented - Good!)
```python
# Current implementation in test_mcp_hardening_all_territories.py
for field in ['Heal Cap %', 'Invocation %', ...]:
    value = row.get(field)
    if value is not None and (value < 0 or value > 100):
        range_failures.append(f"{row['Territory']}: {field}={value} (out of range 0-100)")
```

**Enhancement**: Add expected range warnings
```python
# Warn if values are outside expected ranges (not errors, but suspicious)
EXPECTED_RANGES = {
    'Complexity Health %': (0, 60),  # Typically 0-60%
    'MCP Hardened %': (95, 100),     # Should be near 100%
    'Test %': (60, 100),             # Should be >60%
}

warnings = []
for field, (min_expected, max_expected) in EXPECTED_RANGES.items():
    value = row.get(field)
    if value is not None and (value < min_expected or value > max_expected):
        warnings.append(f"⚠️  {row['Territory']}: {field}={value} (outside expected range {min_expected}-{max_expected})")
```

**Benefit**: Flags suspicious values that are technically valid but unusual.

---

### 5. **Regression Testing**

#### A. Snapshot Testing
```python
def validate_against_baseline():
    """Compare current dashboard data against known-good baseline."""
    import hashlib
    
    # Load current data
    with open('agentic_core/L6_observability/dashboards/data/dashboard_data.js') as f:
        current_content = f.read()
    
    # Calculate hash
    current_hash = hashlib.sha256(current_content.encode()).hexdigest()
    
    # Load baseline hash
    baseline_file = 'tests/dashboard_baseline_hash.txt'
    if os.path.exists(baseline_file):
        with open(baseline_file) as f:
            baseline_hash = f.read().strip()
        
        if current_hash != baseline_hash:
            return "⚠️  Dashboard data changed from baseline (review changes)"
    
    # Update baseline if approved
    with open(baseline_file, 'w') as f:
        f.write(current_hash)
    
    return "✅ Baseline updated"
```

**Benefit**: Detects unintended changes to dashboard data.

---

#### B. Territory Count Validation
```python
def validate_territory_count():
    """Ensure no territories are accidentally dropped."""
    with open('agent_discovery_full.json') as f:
        agents = json.load(f)
    
    source_territories = set(a.get('territory') for a in agents)
    
    with open('agentic_core/L6_observability/dashboards/data/dashboard_data.js') as f:
        content = f.read().replace('window.dashboardData = ', '').strip().rstrip(';')
        dashboard_data = json.loads(content)
    
    dashboard_territories = set(r['Territory'] for r in dashboard_data if r['Territory'] != 'TOTAL')
    
    missing = source_territories - dashboard_territories
    extra = dashboard_territories - source_territories
    
    failures = []
    if missing:
        failures.append(f"Missing territories: {missing}")
    if extra:
        failures.append(f"Extra territories: {extra}")
    
    return failures
```

**Benefit**: Ensures all territories from source are represented in dashboard.

---

### 6. **Proposed Test Structure**

```python
#!/usr/bin/env python3
"""
MANDATORY DASHBOARD DATA VALIDATION
Comprehensive validation of dashboard data integrity.
"""

def test_data_generation():
    """TEST 1: Validate data generation process."""
    print("\n" + "="*70)
    print("TEST 1: Data Generation Validation")
    print("="*70)
    
    failures = []
    
    # 1.1 SSOT Compliance
    ssot_failures = validate_ssot_compliance(dashboard_data)
    if ssot_failures:
        failures.extend(ssot_failures)
    else:
        print("✅ SSOT compliance: All metrics present")
    
    # 1.2 Field Name Consistency
    field_check = validate_field_name_consistency()
    print(field_check)
    
    # 1.3 Data Type Validation
    type_failures = validate_data_types(dashboard_data)
    if type_failures:
        failures.extend(type_failures)
    else:
        print("✅ Data types: All correct")
    
    # 1.4 Range Validation
    range_failures = validate_ranges(dashboard_data)
    if range_failures:
        failures.extend(range_failures)
    else:
        print("✅ Value ranges: All valid")
    
    return len(failures) == 0

def test_data_integrity():
    """TEST 2: Validate source-to-dashboard integrity."""
    print("\n" + "="*70)
    print("TEST 2: Data Integrity Validation")
    print("="*70)
    
    # 2.1 Random Sample Spot Check
    sample_failures = validate_random_sample()
    if sample_failures:
        print(f"❌ Sample validation failed: {len(sample_failures)} issues")
        for f in sample_failures[:5]:
            print(f"   {f}")
    else:
        print("✅ Random sample: All calculations correct")
    
    # 2.2 Territory Count
    count_failures = validate_territory_count()
    if count_failures:
        print(f"❌ Territory count mismatch")
        for f in count_failures:
            print(f"   {f}")
    else:
        print("✅ Territory count: All territories present")
    
    return len(sample_failures) == 0 and len(count_failures) == 0

def test_sort_order():
    """TEST 3: Validate canonical sort order."""
    # (Already implemented - good!)
    pass

def test_mcp_hardening():
    """TEST 4: Validate 100% MCP hardening."""
    # (Already implemented - good!)
    pass

def test_browser_rendering():
    """TEST 5: Validate browser rendering."""
    # (Already implemented - good!)
    pass

if __name__ == "__main__":
    all_passed = True
    all_passed &= test_data_generation()
    all_passed &= test_data_integrity()
    all_passed &= test_sort_order()
    all_passed &= test_mcp_hardening()
    all_passed &= test_browser_rendering()
    
    if all_passed:
        print("\n✅ ALL VALIDATION PASSED - DEPLOYMENT APPROVED")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED - DEPLOYMENT BLOCKED")
        sys.exit(1)
```

---

## Implementation Priority

### Phase 1: Critical Validations (Implement Now)
1. ✅ **SSOT Compliance Check** - Prevents missing metrics
2. ✅ **Field Name Consistency** - Catches field name drift
3. ✅ **Calculation Verification** - Ensures data accuracy
4. ✅ **Sort Order Validation** - Already implemented

### Phase 2: Enhanced Validations (Next Sprint)
5. **Data Type Validation** - Prevents type errors
6. **Territory Count Validation** - Catches dropped territories
7. **Expected Range Warnings** - Flags suspicious values

### Phase 3: Regression Protection (Future)
8. **Snapshot Testing** - Detects unintended changes
9. **Performance Benchmarks** - Ensures data generation speed
10. **Cross-browser Rendering Tests** - Validates in Chrome, Firefox, Safari

---

## Best Practices Going Forward

### 1. **Single Source of Truth (SSOT)**
- All field names defined in `dashboard_ssot_definitions.py`
- All calculations defined in SSOT
- All validation references SSOT constants

### 2. **Fail Fast**
- Validate immediately after data generation
- Don't wait for browser rendering to catch errors
- Block deployment on validation failures

### 3. **Comprehensive Coverage**
- Test data generation (source → dashboard)
- Test data rendering (dashboard → browser)
- Test data integrity (calculations match source)

### 4. **Clear Error Messages**
- Specify which territory failed
- Specify which field is wrong
- Specify expected vs actual values

### 5. **Automated Enforcement**
- Run validation in CI/CD pipeline
- Block merges if validation fails
- Update baseline only after manual review

---

## Summary

The issues encountered were caused by:
1. **Missing validation** between SSOT and generated data
2. **No field name consistency checks** across data layers
3. **Incomplete sort order validation** (only checked TOTAL, not full order)
4. **No calculation verification** against source data

**Proposed solution**: Multi-layer validation framework that checks:
- Schema compliance with SSOT
- Field name consistency
- Calculation integrity
- Data type correctness
- Sort order exactness
- Territory completeness

This framework will catch issues **before deployment** instead of **during debugging**.
