# API Documentation: _ssot_types

**Target Audience**: developers, api_users

# _ssot_types API Documentation

**File**: `_ssot_types.py`
**Classes**: 9
**Functions**: 14

## Classes

- **ConfidenceScore**
- **FailureType** (inherits from <ast.Attribute object at 0x000001CBFAEBF910>)
- **RoutingTier** (inherits from <ast.Attribute object at 0x000001CBFAEBF310>)
- **RoutingInputs**
- **RoutingDecision**
- **ReconciliationViolation**
- **ReconciliationManifest**
- **ASTCodeQualityValidator**
- **HealContext**

## Functions

- **is_high_confidence** -> bool
- **is_medium_confidence** -> bool
- **is_low_confidence** -> bool
- **as_log_line** -> str
- **to_dict** -> dict
- **add_modification** -> None
- **add_failure** -> None
- **finalize** -> dict[str, Any]
- **__init__**
- **_read_and_parse_file** -> tuple[ast.AST | None, str | None]
- **check_file_quality** -> dict
- **enable_llm** -> bool
- **dry_run** -> bool
- **from_args** -> 'HealContext'


## Class: ConfidenceScore

**Description**: [HARDENED] Confidence score for autonomous healing.

### Methods

#### is_high_confidence
**Parameters**: self
**Returns**: bool

#### is_medium_confidence
**Parameters**: self
**Returns**: bool

#### is_low_confidence
**Parameters**: self
**Returns**: bool



## Class: FailureType

**Description**: Classifies the failure being routed.  Drives gate selection.

**Inherits from**: _enum.Enum



## Class: RoutingTier

**Inherits from**: _enum.Enum



## Class: RoutingInputs

**Description**: All inputs to compute_routing_decision.  No embeddings allowed.



## Class: RoutingDecision

**Description**: Immutable routing result with full audit trail.

### Methods

#### as_log_line
**Parameters**: self
**Returns**: str



## Class: ReconciliationViolation

**Description**: Structured violation for enhanced telemetry (Ported from FilesystemSSOTReconciler).

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict



## Class: ReconciliationManifest

**Description**: Telemetry manifest for tracking all reconciliation changes.

### Methods

#### add_modification
**Parameters**: self, modification
**Returns**: None

#### add_failure
**Parameters**: self, failure
**Returns**: None

#### finalize
**Parameters**: self
**Returns**: dict[str, Any]



## Class: ASTCodeQualityValidator

**Description**: AST-based code quality validation with memory guards (Ported from TypeMechanic).

### Methods

#### __init__
**Parameters**: self, project_root

#### _read_and_parse_file
**Parameters**: self, fp
**Returns**: tuple[ast.AST | None, str | None]
**Description**: Reads a file and parses it into an AST with strict size limits.

#### check_file_quality
**Parameters**: self, file_path
**Returns**: dict
**Description**: Check file for code quality issues (missing types, etc).



## Class: HealContext

**Description**: Immutable healing configuration passed uniformly to every phase function.

    Single control surface: --heal drives ALL active-mode flags.

      --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                    enable_meta_learning all True
      --heal OFF => scan/report only, everything passive

    Per hostile audit Section B1: trace_id must appear in every artifact.
    Per hostile audit Section E1: trace_id threads through all artifacts and HealContext.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate modes.
    

### Methods

#### enable_llm
**Parameters**: self
**Returns**: bool
**Description**: LLM arbitration is always active when healing — not a separate flag.

#### dry_run
**Parameters**: self
**Returns**: bool
**Description**: Convenience alias — inverted heal for legacy call sites.

#### from_args
**Parameters**: cls, args
**Returns**: 'HealContext'
**Description**: Construct from parsed CLI args. Single construction point.

        Canonical flag semantics (--heal is the ONLY active-mode switch):
          --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                        enable_meta_learning all True
          --heal OFF => all passive/scan-only

        Deprecated flags (kept for backward-compat, emit warnings):
          --dry-run        => same as omitting --heal
          --manual         => always autonomous now
          --interactive    => auto_approve is always True under --heal
          --apply-proposals => meta-learning always on under --heal
        



## Function: is_high_confidence

**Parameters**: self
**Returns**: bool


## Function: is_medium_confidence

**Parameters**: self
**Returns**: bool


## Function: is_low_confidence

**Parameters**: self
**Returns**: bool


## Function: as_log_line

**Parameters**: self
**Returns**: str


## Function: to_dict

**Parameters**: self
**Returns**: dict


## Function: add_modification

**Parameters**: self, modification
**Returns**: None


## Function: add_failure

**Parameters**: self, failure
**Returns**: None


## Function: finalize

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __init__

**Parameters**: self, project_root


## Function: _read_and_parse_file

**Parameters**: self, fp
**Returns**: tuple[ast.AST | None, str | None]
**Description**: Reads a file and parses it into an AST with strict size limits.



## Function: check_file_quality

**Parameters**: self, file_path
**Returns**: dict
**Description**: Check file for code quality issues (missing types, etc).



## Function: enable_llm

**Parameters**: self
**Returns**: bool
**Description**: LLM arbitration is always active when healing — not a separate flag.



## Function: dry_run

**Parameters**: self
**Returns**: bool
**Description**: Convenience alias — inverted heal for legacy call sites.



## Function: from_args

**Parameters**: cls, args
**Returns**: 'HealContext'
**Description**: Construct from parsed CLI args. Single construction point.

        Canonical flag semantics (--heal is the ONLY active-mode switch):
          --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                        enable_meta_learning all True
          --heal OFF => all passive/scan-only

        Deprecated flags (kept for backward-compat, emit warnings):
          --dry-run        => same as omitting --heal
          --manual         => always autonomous now
          --interactive    => auto_approve is always True under --heal
          --apply-proposals => meta-learning always on under --heal
        



## Usage Examples

### Class Usage

```python
# Using ConfidenceScore
confidencescore = ConfidenceScore()
confidencescore.is_high_confidence()
confidencescore.is_medium_confidence()
```

```python
# Using FailureType
failuretype = FailureType()
```

```python
# Using RoutingTier
routingtier = RoutingTier()
```

### Function Usage

```python
# Using is_high_confidence
result = is_high_confidence()
```

```python
# Using is_medium_confidence
result = is_medium_confidence()
```

```python
# Using is_low_confidence
result = is_low_confidence()
```



---
**Generated**: 2026-03-26T09:39:03.380753
**Type**: api_reference
**Quality**: comprehensive
