# API Documentation: infra_error_types

**Target Audience**: developers, api_users

# infra_error_types API Documentation

**File**: `infra_error_types.py`
**Classes**: 1
**Functions**: 0

## Classes

- **InfrastructureDependencyError** (inherits from RuntimeError)


## Class: InfrastructureDependencyError

**Description**: Raised when a mandatory infrastructure dependency is unavailable.

    This error signals a hard failure — the system cannot continue safely
    without the required service.  Callers must not catch this error to
    implement a silent fallback; they should propagate it to the process
    boundary so the deployment is restarted or the operator is alerted.
    

**Inherits from**: RuntimeError



## Usage Examples

### Class Usage

```python
# Using InfrastructureDependencyError
infrastructuredependencyerror = InfrastructureDependencyError()
```



---
**Generated**: 2026-03-26T09:39:03.968314
**Type**: api_reference
**Quality**: comprehensive
