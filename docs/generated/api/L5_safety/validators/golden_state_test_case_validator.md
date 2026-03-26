# API Documentation: golden_state_test_case_validator

**Target Audience**: developers, api_users

# golden_state_test_case_validator API Documentation

**File**: `golden_state_test_case_validator.py`
**Classes**: 5
**Functions**: 2

## Classes

- **GoldenStateTestCase** (inherits from BaseModel)
- **JudgeVerdict** (inherits from BaseModel)
- **EvalResult** (inherits from BaseModel)
- **GoldenCase** (inherits from BaseModel)
- **GoldenOutput** (inherits from BaseModel)

## Functions

- **validate_required_text** -> str
- **validate_non_empty** -> str


## Class: GoldenStateTestCase

**Description**: A single benchmark test case for the system.

**Inherits from**: BaseModel

### Methods

#### validate_required_text
**Parameters**: cls, value
**Returns**: str
**Description**: [HARDENED] Ensure required text fields are not empty.



## Class: JudgeVerdict

**Description**: schema for LM-as-a-Judge evaluation results.

**Inherits from**: BaseModel

### Methods

#### validate_non_empty
**Parameters**: cls, value
**Returns**: str
**Description**: [HARDENED] Ensure rating and explanation are not empty.



## Class: EvalResult

**Description**: Outcome of running a GoldenStateTestCase through the agent loop.

**Inherits from**: BaseModel



## Class: GoldenCase

**Description**: Structured benchmark case for automated evaluation pipelines.

**Inherits from**: BaseModel



## Class: GoldenOutput

**Description**: Benchmark results including safety and metacognitive summaries.

**Inherits from**: BaseModel



## Function: validate_required_text

**Parameters**: cls, value
**Returns**: str
**Description**: [HARDENED] Ensure required text fields are not empty.



## Function: validate_non_empty

**Parameters**: cls, value
**Returns**: str
**Description**: [HARDENED] Ensure rating and explanation are not empty.



## Usage Examples

### Class Usage

```python
# Using GoldenStateTestCase
goldenstatetestcase = GoldenStateTestCase()
goldenstatetestcase.validate_required_text()
```

```python
# Using JudgeVerdict
judgeverdict = JudgeVerdict()
judgeverdict.validate_non_empty()
```

```python
# Using EvalResult
evalresult = EvalResult()
```

### Function Usage

```python
# Using validate_required_text
result = validate_required_text(cls, value)
```

```python
# Using validate_non_empty
result = validate_non_empty(cls, value)
```



---
**Generated**: 2026-03-26T09:39:05.794329
**Type**: api_reference
**Quality**: comprehensive
