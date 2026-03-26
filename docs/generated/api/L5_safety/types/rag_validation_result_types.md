# API Documentation: rag_validation_result_types

**Target Audience**: developers, api_users

# rag_validation_result_types API Documentation

**File**: `rag_validation_result_types.py`
**Classes**: 4
**Functions**: 4

## Classes

- **ValidationResult** (inherits from BaseModel)
- **ThematicAnalysis** (inherits from BaseModel)
- **RagState** (inherits from BaseModel)
- **ImmutableStagingBuffer** (inherits from BaseModel)

## Functions

- **with_data** -> ImmutableStagingBuffer
- **clear** -> ImmutableStagingBuffer
- **validate_severity** -> str
- **validate_confidence_scores** -> list[float]


## Class: ValidationResult

**Description**: Result of a validation rule execution.

**Inherits from**: BaseModel

### Methods

#### validate_severity
**Parameters**: cls, v
**Returns**: str
**Description**: [HARDENED] Ensure severity is valid.



## Class: ThematicAnalysis

**Description**: Analysis of thematic content in text.

**Inherits from**: BaseModel

### Methods

#### validate_confidence_scores
**Parameters**: cls, v
**Returns**: list[float]
**Description**: [HARDENED] Ensure all confidence scores are between 0 and 1.



## Class: RagState

**Description**: State of RAG (Retrieval-Augmented Generation) process.

**Inherits from**: BaseModel



## Class: ImmutableStagingBuffer

**Description**: Immutable buffer for staging data transformations.

**Inherits from**: BaseModel



## Function: with_data

**Parameters**: original_buffer, new_data
**Returns**: ImmutableStagingBuffer
**Description**: Return a new buffer with updated data.



## Function: clear

**Parameters**: original_buffer
**Returns**: ImmutableStagingBuffer
**Description**: Return a new empty buffer.



## Function: validate_severity

**Parameters**: cls, v
**Returns**: str
**Description**: [HARDENED] Ensure severity is valid.



## Function: validate_confidence_scores

**Parameters**: cls, v
**Returns**: list[float]
**Description**: [HARDENED] Ensure all confidence scores are between 0 and 1.



## Usage Examples

### Class Usage

```python
# Using ValidationResult
validationresult = ValidationResult()
validationresult.validate_severity()
```

```python
# Using ThematicAnalysis
thematicanalysis = ThematicAnalysis()
thematicanalysis.validate_confidence_scores()
```

```python
# Using RagState
ragstate = RagState()
```

### Function Usage

```python
# Using with_data
result = with_data(original_buffer, new_data)
```

```python
# Using clear
result = clear(original_buffer)
```

```python
# Using validate_severity
result = validate_severity(cls, v)
```



---
**Generated**: 2026-03-26T09:39:05.542197
**Type**: api_reference
**Quality**: comprehensive
