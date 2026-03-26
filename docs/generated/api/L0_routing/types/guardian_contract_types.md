# API Documentation: guardian_contract_types

**Target Audience**: developers, api_users

# guardian_contract_types API Documentation

**File**: `guardian_contract_types.py`
**Classes**: 11
**Functions**: 38

## Classes

- **V15EnforcementError** (inherits from RuntimeError)
- **V15SoftFailAbort** (inherits from Exception)
- **V15HardFailAbort** (inherits from Exception)
- **GuardianStatus** (inherits from str, Enum)
- **CheckStatus** (inherits from str, Enum)
- **ArtifactType** (inherits from str, Enum)
- **ArtifactClass** (inherits from str, Enum)
- **ScanBudgetExceeded**
- **GuardianCheck**
- **GuardianArtifact**
- **GuardianResult**

## Functions

- **is_v15_enforced** -> bool
- **is_v15_hard_fail** -> bool
- **is_v15_soft_fail** -> bool
- **get_artifact_filename** -> str
- **guard_scan_budget** -> ScanBudgetExceeded | None
- **check_schema_compatibility** -> list[str]
- **validate_against_json_schema** -> list[str]
- **normalize_repo_path** -> str
- **validate_no_absolute_paths** -> list[str]
- **_sort_value** -> Any
- **_stable_sort_list** -> list
- **_sort_metrics** -> dict[str, Any]
- **write_guardian_result** -> Path
- **load_guardian_result** -> GuardianResult
- **get_default_signing_enclave** -> Any
- **maybe_sign_result** -> GuardianResult
- **__init__** -> None
- **details** -> str
- **remediation_hints** -> list[str]
- **_validate_type** -> None
- **_validate_enum** -> None
- **_validate_pattern** -> None
- **_validate_not_pattern** -> None
- **_validate_object** -> None
- **_check_depth** -> None
- **_walk** -> None
- **to_dict** -> dict[str, Any]
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]
- **add_check** -> None
- **add_artifact** -> None
- **set_error** -> None
- **sign** -> Any
- **to_dict** -> dict[str, Any]
- **ensure_v15_signed** -> None
- **compute_certification_hash** -> str
- **to_json** -> str
- **validate** -> list[str]


## Class: V15EnforcementError

**Description**: Raised when a V15 invariant is violated in enforced mode.

**Inherits from**: RuntimeError



## Class: V15SoftFailAbort

**Description**: Raised internally when SOFT_FAIL mode detects a contract violation.

    Caught by V15ExecutionGateway.execute() to produce a structured
    GatewayResult with success=False instead of crashing the process.
    

**Inherits from**: Exception



## Class: V15HardFailAbort

**Description**: Raised when HARD_FAIL mode detects a contract violation.

    Single deterministic exception type for all HARD_FAIL aborts.
    Propagates out of V15ExecutionGateway.execute() uncaught —
    callers must handle or let the process terminate.
    

**Inherits from**: Exception



## Class: GuardianStatus

**Description**: Top-level guardian result status.

**Inherits from**: str, Enum



## Class: CheckStatus

**Description**: Per-check status.

**Inherits from**: str, Enum



## Class: ArtifactType

**Description**: Types of artifacts a guardian may emit.

**Inherits from**: str, Enum



## Class: ArtifactClass

**Description**: Classification of guardian artifacts.

**Inherits from**: str, Enum



## Class: ScanBudgetExceeded

**Description**: 
    Sentinel returned by scan functions when a budget cap is breached.

    Carries which cap was exceeded, the limit value, and remediation hints
    so callers can emit a schema-locked FAIL (not ERROR/exception).

    Lives in SSOT types so all scanning guardians share the same pattern.
    

### Methods

#### __init__
**Parameters**: self, cap_name, limit, scanned
**Returns**: None

#### details
**Parameters**: self
**Returns**: str

#### remediation_hints
**Parameters**: self
**Returns**: list[str]



## Class: GuardianCheck

**Description**: Single check within a guardian run.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: GuardianArtifact

**Description**: Artifact emitted by a guardian (path MUST be repo-relative POSIX).

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: GuardianResult

**Description**: 
    Canonical result object emitted by every Guardian.

    Fields:
        guardian_id: Stable string identifier (e.g. "hygiene", "autonomy").
        version: Contract version integer.
        timestamp: Optional ISO-8601 string. If present, must be injected or
                   fixed in tests. Omitted by default for determinism.
        status: One of PASS, FAIL, ERROR.
        summary: 1-2 line human-readable summary.
        checks: Ordered list of individual checks performed.
        artifacts: List of emitted artifacts (paths repo-relative POSIX).
        metrics: Numeric metrics (counts, timings if deterministic).
        remediation_hints: Optional list of short remediation strings.
    

### Methods

#### add_check
**Parameters**: self, check_id, status, details, evidence
**Returns**: None
**Description**: Add a check entry and update top-level status.

#### add_artifact
**Parameters**: self, artifact_type, path, description
**Returns**: None

#### set_error
**Parameters**: self, summary
**Returns**: None
**Description**: Mark the entire result as ERROR (unexpected exception).

#### sign
**Parameters**: self, enclave, key_id, commit_hash
**Returns**: Any
**Description**: Sign this result via a SignatureEnclave; returns SignedGuardianArtifact.

        Fail-closed: raises V15EnforcementError if signing fails.
        

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]

#### ensure_v15_signed
**Parameters**: self
**Returns**: None
**Description**: INV-2: Fail-closed guard — raises if V15 is enforced and result is unsigned.

        Guardian runners MUST call this (or sign()) before emitting results
        when V15_ENFORCEMENT is enabled.
        

#### compute_certification_hash
**Parameters**: self
**Returns**: str
**Description**: Compute SHA256 over canonical JSON (sorted keys, no whitespace).

        The hash excludes the ``certification_hash`` field itself.
        Stores the result in ``self.certification_hash`` and returns it.
        

#### to_json
**Parameters**: self, indent
**Returns**: str

#### validate
**Parameters**: self
**Returns**: list[str]
**Description**: 
        Validate this result against the contract.
        Returns a list of violation messages (empty = valid).
        



## Function: is_v15_enforced

**Returns**: bool
**Description**: Return True when V15 enforcement is active (fail-closed: default ON).

    Unset / absent env var → True (fail-closed production default).
    Explicit opt-out: "0", "false", "no", "off" (case-insensitive) → False.
    Explicit opt-in: "1", "true", "yes", "on", "log", "soft" (case-insensitive) → True.
    Any other value → ValueError (deterministic misconfig rejection).
    Use ``is_v15_hard_fail()`` / ``is_v15_soft_fail()`` for mode selection.
    



## Function: is_v15_hard_fail

**Returns**: bool
**Description**: Return True only when V15_ENFORCEMENT demands hard blocking on violation.

    Hard-fail values: "1", "true", "yes" (case-insensitive).
    "log" and "soft" return False — violations are logged, not blocked.
    



## Function: is_v15_soft_fail

**Returns**: bool
**Description**: Return True when V15_ENFORCEMENT is set to SOFT_FAIL mode.

    SOFT_FAIL mode: violations produce a controlled abort (structured failure
    return via ``V15SoftFailAbort``) without crashing the process.
    Only the literal value "soft" (case-insensitive) activates this mode.
    



## Function: get_artifact_filename

**Parameters**: guardian_id, correlation_id, artifact_class
**Returns**: str
**Description**: 
    Generate the correct artifact filename based on class and correlation.

    Args:
        guardian_id: The guardian_id (required for INDIVIDUAL, ignored for AGGREGATE).
        correlation_id: Optional correlation ID for tracking.
        artifact_class: INDIVIDUAL or AGGREGATE.

    Returns:
        Filename matching the L6 contract pattern.
    



## Function: guard_scan_budget

**Parameters**: file_count, cap_name, limit
**Returns**: ScanBudgetExceeded | None
**Description**: 
    Check whether a running file count exceeds a scan budget cap.

    Returns ScanBudgetExceeded sentinel if cap is breached, None otherwise.
    All scanning guardians MUST use this helper instead of raising RuntimeError.

    Args:
        file_count: Current count of files scanned.
        cap_name: Name of the cap constant (for diagnostics).
        limit: Override limit; defaults to MAX_FILES_PER_SCAN.

    Returns:
        ScanBudgetExceeded if breached, None if within budget.
    



## Function: check_schema_compatibility

**Parameters**: result_dict
**Returns**: list[str]
**Description**: 
    Verify a serialized result dict has exactly the expected top-level keys.
    Returns list of incompatibility messages (empty = compatible).
    



## Function: validate_against_json_schema

**Parameters**: result_dict
**Returns**: list[str]
**Description**: 
    Deep validation of result_dict against CONTRACT_JSON_SCHEMA.
    Returns list of validation errors (empty = valid).

    This is a lightweight validator that does NOT require jsonschema library.
    It validates: required fields, type constraints, enum values, additionalProperties.
    



## Function: normalize_repo_path

**Parameters**: path
**Returns**: str
**Description**: 
    Normalize a path to repo-relative POSIX form.

    Rules (from Constitutional §20):
    - Forward slashes only
    - No ``..``
    - No absolute paths
    - No leading ``/``
    - No ``.`` segments
    



## Function: validate_no_absolute_paths

**Parameters**: data
**Returns**: list[str]
**Description**: 
    Recursively check a dict for absolute path strings.
    Returns list of JSON-path locations where absolute paths were found.
    



## Function: _sort_value

**Parameters**: v
**Returns**: Any
**Description**: Recursively sort dicts by key and lists of dicts by a stable key.



## Function: _stable_sort_list

**Parameters**: items
**Returns**: list
**Description**: Sort a list deterministically. Dicts sorted by 'guardian_id' or first key.



## Function: _sort_metrics

**Parameters**: metrics
**Returns**: dict[str, Any]
**Description**: Return metrics dict with sorted keys and deterministic nested values.



## Function: write_guardian_result

**Parameters**: result, output_dir, filename
**Returns**: Path
**Description**: 
    Write a GuardianResult to a JSON file.

    Args:
        result: The result to write.
        output_dir: Directory to write into (created if needed).
        filename: Output filename.

    Returns:
        Absolute path to the written file.
    



## Function: load_guardian_result

**Parameters**: path
**Returns**: GuardianResult
**Description**: Load a GuardianResult from a JSON file.



## Function: get_default_signing_enclave

**Returns**: Any
**Description**: Return a SignatureEnclave for guardian result signing.

    When V15_TEST_SIGNING=1: returns a DeterministicTestEnclave with a
    fixed HMAC key (deterministic, no network, no wall-clock).
    When enforced but V15_TEST_SIGNING is unset: raises V15EnforcementError
    (no production enclave available yet — fail-closed).
    When not enforced: returns None.
    



## Function: maybe_sign_result

**Parameters**: result
**Returns**: GuardianResult
**Description**: Sign a GuardianResult when V15 enforcement is active.

    When enforced: assigns v15_trace_id (if missing), calls result.sign()
    via get_default_signing_enclave(). Returns the mutated result.
    When not enforced: returns result unchanged (unsigned allowed).

    Args:
        result: The GuardianResult to potentially sign.
        commit_hash: Git commit hash for the signing context.

    Returns:
        The (potentially signed) GuardianResult.
    



## Function: __init__

**Parameters**: self, cap_name, limit, scanned
**Returns**: None


## Function: details

**Parameters**: self
**Returns**: str


## Function: remediation_hints

**Parameters**: self
**Returns**: list[str]


## Function: _validate_type

**Parameters**: value, type_spec, path
**Returns**: None


## Function: _validate_enum

**Parameters**: value, enum_values, path
**Returns**: None


## Function: _validate_pattern

**Parameters**: value, pattern, path
**Returns**: None
**Description**: Validate string against regex pattern.



## Function: _validate_not_pattern

**Parameters**: value, pattern, path
**Returns**: None
**Description**: Validate string does NOT match regex pattern.



## Function: _validate_object

**Parameters**: obj, obj_schema, path
**Returns**: None


## Function: _check_depth

**Parameters**: obj, current_depth, path
**Returns**: None


## Function: _walk

**Parameters**: obj, prefix
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: add_check

**Parameters**: self, check_id, status, details, evidence
**Returns**: None
**Description**: Add a check entry and update top-level status.



## Function: add_artifact

**Parameters**: self, artifact_type, path, description
**Returns**: None


## Function: set_error

**Parameters**: self, summary
**Returns**: None
**Description**: Mark the entire result as ERROR (unexpected exception).



## Function: sign

**Parameters**: self, enclave, key_id, commit_hash
**Returns**: Any
**Description**: Sign this result via a SignatureEnclave; returns SignedGuardianArtifact.

        Fail-closed: raises V15EnforcementError if signing fails.
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: ensure_v15_signed

**Parameters**: self
**Returns**: None
**Description**: INV-2: Fail-closed guard — raises if V15 is enforced and result is unsigned.

        Guardian runners MUST call this (or sign()) before emitting results
        when V15_ENFORCEMENT is enabled.
        



## Function: compute_certification_hash

**Parameters**: self
**Returns**: str
**Description**: Compute SHA256 over canonical JSON (sorted keys, no whitespace).

        The hash excludes the ``certification_hash`` field itself.
        Stores the result in ``self.certification_hash`` and returns it.
        



## Function: to_json

**Parameters**: self, indent
**Returns**: str


## Function: validate

**Parameters**: self
**Returns**: list[str]
**Description**: 
        Validate this result against the contract.
        Returns a list of violation messages (empty = valid).
        



## Usage Examples

### Class Usage

```python
# Using V15EnforcementError
v15enforcementerror = V15EnforcementError()
```

```python
# Using V15SoftFailAbort
v15softfailabort = V15SoftFailAbort()
```

```python
# Using V15HardFailAbort
v15hardfailabort = V15HardFailAbort()
```

### Function Usage

```python
# Using is_v15_enforced
result = is_v15_enforced()
```

```python
# Using is_v15_hard_fail
result = is_v15_hard_fail()
```

```python
# Using is_v15_soft_fail
result = is_v15_soft_fail()
```



---
**Generated**: 2026-03-26T09:39:03.454452
**Type**: api_reference
**Quality**: comprehensive
