# API Documentation: digest_calculator

**Target Audience**: developers, api_users

# digest_calculator API Documentation

**File**: `digest_calculator.py`
**Classes**: 1
**Functions**: 2

## Classes

- **DigestCalculator**

## Functions

- **compute** -> str
- **zero_hash** -> str


## Class: DigestCalculator

**Description**: Compute the canonical determinism digest from its five components.

### Methods

#### compute
**Parameters**: self
**Returns**: str
**Description**: Return SHA-256 hex digest of the canonical determinism surface.

        All five arguments must be 64-character lowercase hex strings (SHA-256).
        

#### zero_hash
**Returns**: str
**Description**: Return a deterministic placeholder SHA-256 (all zeros).



## Function: compute

**Parameters**: self
**Returns**: str
**Description**: Return SHA-256 hex digest of the canonical determinism surface.

        All five arguments must be 64-character lowercase hex strings (SHA-256).
        



## Function: zero_hash

**Returns**: str
**Description**: Return a deterministic placeholder SHA-256 (all zeros).



## Usage Examples

### Class Usage

```python
# Using DigestCalculator
digestcalculator = DigestCalculator()
digestcalculator.compute()
digestcalculator.zero_hash()
```

### Function Usage

```python
# Using compute
result = compute()
```

```python
# Using zero_hash
result = zero_hash()
```



---
**Generated**: 2026-03-26T09:39:03.666277
**Type**: api_reference
**Quality**: comprehensive
