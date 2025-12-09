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

---

## The 7 Rules

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

---

## Enforcement

### Pre-commit Hooks

All 7 rules run automatically on every commit via pre-commit hooks.

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
