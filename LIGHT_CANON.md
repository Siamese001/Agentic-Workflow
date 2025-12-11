# LIGHT CANON 2025 — OFFICIAL DEFINITION

## The 7 Brutal Hygiene Rules for All Non-Sovereign Code

The Light Canon applies to **every Python file in the repo** except `data/` and `archives/`.  
These are the minimal, brutal hygiene rules that keep the codebase clean without stopping development.

---

## Coverage Areas

**Light Canon applies to:**

- `tests/` - Test code and utilities
- `scripts/` - One-off tools and automation
- `shared/` - Cross-cutting utilities (caching, vector clients, etc.)
- `runtime/` - Dynamic glue and orchestration
- `apps_shared/` - Shared application code

**Exempt from Light Canon:**

- `data/` - Immutable truth - immune
- `archives/` - Historical data - immune
- Sovereign directories (see list below) - Can have arbitrary depth

---

## The 8 Rules

### 🔥 Rule 1: No TODO/FIXME/XXX/HACK/STUB Comments

**What it blocks:** Development debt markers in production code

**Examples that FAIL:**

```python
# TODO: implement this later
# FIXME: this is broken
# XXX: hack alert
# HACK: quick fix
# STUB: placeholder
```

**Why:** No development debt should be committed. Either implement it or create a proper issue.

### 🔥 Rule 2: No print(), pdb, ipdb, breakpoint()

**What it blocks:** Debug statements in committed code

**Examples that FAIL:**

```python
print("debugging this")
pdb.set_trace()
ipdb.set_trace()
breakpoint()
```

**Why:** Debug code should never reach production. Use proper logging instead.

### 🔥 Rule 3: No Files < 150 bytes

**What it blocks:** Micro-files and stub implementations

**Exceptions:**

- `__init__.py` files can be < 100 bytes (just imports)
- All other Python files must be ≥ 150 bytes

**Why:** Tiny files indicate incomplete implementations or placeholder code.

### 🔥 Rule 4: No Zombie "archive/" Folder

**What it blocks:** The forbidden singular archive folder

**Canon Law:**

- ✅ ALLOWED: `archives/` (plural) - Canon-approved
- ❌ FORBIDDEN: `archive/` (singular) - Zombie

**Why:** Consistent naming prevents confusion and maintains Canon compliance.

### 🔥 Rule 5: No Bare except or except Exception

**What it blocks:** Lazy exception handling

**Examples that FAIL:**

```python
try:
    risky_operation()
except:  # ❌ Bare except
    pass

try:
    risky_operation()
except Exception:  # ❌ Too broad
    pass
```

**What to do instead:**

```python
try:
    risky_operation()
except ValueError:  # ✅ Specific exception
    handle_value_error()
```

**Why:** Proper exception handling is critical for production stability.

### 🔥 Rule 6: No Pass-Only Functions/Classes

**What it blocks:** Empty implementations

**Examples that FAIL:**

```python
def helper_function():
    pass  # ❌ No implementation

class UtilityClass:
    pass  # ❌ No implementation
```

**Exceptions:** Test files with `@pytest.mark.skip` decorators

**Why:** Pass-only definitions indicate incomplete or placeholder code.

### 🔥 Rule 7: No Private Keys/Secrets in Code

**What it blocks:** Accidentally committed credentials

**What it detects:**

- API keys
- Database passwords
- Secret tokens
- Private certificates

**Why:** Security is non-negotiable. Secrets belong in environment variables or secret managers.

### 🔥 Rule 8: No Deep Nesting (Max Depth 3)

**What it blocks:** Deep directory structures in non-sovereign code

**Rule:** All Python files outside sovereign directories must be at depth ≤ 3 from repository root

**Examples that FAIL:**

```
runtime/logic/validation/find_problems/diagnostics/inspect.py  # Depth 6 ❌
scripts/cache/data_access/get_info/utility/format.py           # Depth 5 ❌
shared/security_controls/guardrails/check_rules/policy/apply.py # Depth 5 ❌
```

**Examples that PASS:**

```
runtime/shared/exceptions.py                 # Depth 2 ✅
tests/unit/test_validation.py                # Depth 3 ✅
scripts/deploy/build.sh                      # Depth 2 ✅
```

**Why:** Deep nesting makes code hard to navigate and maintain. Use sovereign directories for complex hierarchies.

---

## Sovereign Directories (Exempt from Depth Limit)

### Original Sovereign (10)

1. `agentic_core/` - Core agentic framework
2. `apps_lic/` - LinkedIn outreach applications
3. `apps_rg/` - Resume generation applications
4. `apps_shared/` - Shared application code
5. `schemas/` - Schema definitions
6. `prompt_governance/` - Prompt governance rules
7. `observability/` - Observability and monitoring
8. `config/` - Configuration files
9. `data/` - Data files and resources
10. `archives/` - Archived legacy code

### Compliance Sovereign (15) - Added December 2025

1. `01_runtime_logic/` - Runtime logic components
2. `02_runtime_cache/` - Runtime cache components
3. `03_scripts_logic/` - Scripts logic components
4. `04_scripts_cache/` - Scripts cache components
5. `05_runtime_security/` - Runtime security controls
6. `06_runtime_runtime/` - Runtime runtime components
7. `07_runtime_pipeline/` - Runtime pipeline components
8. `08_shared_security/` - Shared security controls
9. `09_shared_runtime/` - Shared runtime components
10. `10_shared_pipeline/` - Shared pipeline components
11. `11_shared_logic/` - Shared logic components
12. `12_shared_cache/` - Shared cache components
13. `13_scripts_security/` - Scripts security controls
14. `14_scripts_runtime/` - Scripts runtime components
15. `15_scripts_pipeline/` - Scripts pipeline components

### Audit Script

```python
python -c "
import pathlib
sovereign = {'agentic_core','apps_lic','apps_rg','apps_shared','schemas','prompt_governance','observability','config','data','archives','01_runtime_logic','02_runtime_cache','03_scripts_logic','04_scripts_cache','05_runtime_security','06_runtime_runtime','07_runtime_pipeline','08_shared_security','09_shared_runtime','10_shared_pipeline','11_shared_logic','12_shared_cache','13_scripts_security','14_scripts_runtime','15_scripts_pipeline'}
for f in pathlib.Path('.').rglob('*.py'):
    if any(part in sovereign for part in f.parts): continue
    if len(f.parts) - 1 > 3: print(f'{len(f.parts)-1} {f}')
"
```

---

## Enforcement

### Pre-commit Hooks

All 8 rules run automatically on every commit via pre-commit hooks.

### CI/CD Pipeline

Light Canon rules are enforced in continuous integration.

### Manual Testing

```bash
# Test Light Canon rules manually
pre-commit run --all-files
```

---

## Balance with Full Canon

**Sovereign Code** (`agentic_core/`, `apps_lic/`, `apps_rg/`, `apps_shared/`):

- Full 40/40 Subatomic Canon validation
- Ruthless architectural enforcement
- Zero tolerance for violations

**Non-Sovereign Code** (`tests/`, `scripts/`, `shared/`, `runtime/`):

- Light Canon 7 hygiene rules
- Maintains development velocity
- Prevents worst sins without blocking progress

This balance ensures **production-critical code is perfect** while **utility and test code stays clean and functional**.

---

## Violation Examples

### ❌ Light Canon Violations

```python
# tests/test_example.py
def test_something():
    print("testing")  # Rule 2: Debug statement
    # TODO: add more tests  # Rule 1: TODO comment

# scripts/utility.py
def helper():
    pass  # Rule 6: Pass-only function

try:
    something()
except:  # Rule 5: Bare except
    pass
```

### ✅ Light Canon Compliant

```python
# tests/test_example.py
import logging

def test_something():
    result = calculate_result()
    assert result == expected_value

# scripts/utility.py
def helper():
    """Calculate helper result."""
    return perform_calculation()

try:
    something()
except ValueError as e:
    logging.error(f"Value error occurred: {e}")
```

---

## Why This Matters

The Light Canon ensures:

1. **No Development Debt** - TODO/FIXME never reach production
2. **No Debug Code** - print() and pdb never ship
3. **Complete Implementations** - No stub files or pass-only functions
4. **Proper Error Handling** - Specific exceptions only
5. **Security** - No accidental secrets in code
6. **Consistency** - Proper folder naming
7. **Quality** - Minimum file size prevents placeholder code

## Light Canon + Full 40/40 = ETERNAL REPO

Production code is ruthlessly perfect. Utility code is clean and functional. Development velocity is maintained. Quality is never compromised.

### Canon 2025 - Light Edition
