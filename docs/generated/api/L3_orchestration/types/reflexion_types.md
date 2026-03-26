# API Documentation: reflexion_types

**Target Audience**: developers, api_users

# reflexion_types API Documentation

**File**: `reflexion_types.py`
**Classes**: 2
**Functions**: 3

## Classes

- **ReflexionCritique**
- **ReflexionMemory**

## Functions

- **add** -> None
- **summary** -> str
- **best_response** -> str | None


## Class: ReflexionCritique

**Description**: Verbal critique produced by the Evaluator LLM call.



## Class: ReflexionMemory

**Description**: Accumulates critique history across iterations for the Revisor.

### Methods

#### add
**Parameters**: self, critique
**Returns**: None

#### summary
**Parameters**: self
**Returns**: str
**Description**: Return a condensed summary of prior critiques for the Revisor prompt.

#### best_response
**Parameters**: self
**Returns**: str | None
**Description**: Return the response with the highest score seen so far.



## Function: add

**Parameters**: self, critique
**Returns**: None


## Function: summary

**Parameters**: self
**Returns**: str
**Description**: Return a condensed summary of prior critiques for the Revisor prompt.



## Function: best_response

**Parameters**: self
**Returns**: str | None
**Description**: Return the response with the highest score seen so far.



## Usage Examples

### Class Usage

```python
# Using ReflexionCritique
reflexioncritique = ReflexionCritique()
```

```python
# Using ReflexionMemory
reflexionmemory = ReflexionMemory()
reflexionmemory.add()
reflexionmemory.summary()
```

### Function Usage

```python
# Using add
result = add(critique)
```

```python
# Using summary
result = summary()
```

```python
# Using best_response
result = best_response()
```



---
**Generated**: 2026-03-26T09:39:04.408926
**Type**: api_reference
**Quality**: comprehensive
